from typing import Literal, Self, cast, TYPE_CHECKING
import logging
import threading
import time
import asyncio
import httpx

from .policy import CommandPolicy
from .registry import UserRegistry
from .v2.models import Endpoint as V2Endpoint
from .v1.models import Endpoint as V1Endpoint
from .exceptions import ApiError, RateLimited, DeserializationError

if TYPE_CHECKING:
    from .v2.client import AsyncClient as V2AsyncClient, Client as V2Client
    from .v1.client import AsyncClient as V1AsyncClient, Client as V1Client

logger = logging.getLogger(__name__)

type ClientType = "V2AsyncClient | V2Client | V1AsyncClient | V1Client"
type HTTPXClient = httpx.Client | httpx.AsyncClient
type EndpointType = V1Endpoint | V2Endpoint

def create_async_client(server_key: str, **kwargs) -> httpx.AsyncClient:
    logger.debug("Creating new async HTTPX client.")
    return httpx.AsyncClient(
        base_url="https://api.erlc.gg/",
        headers={"server-key": server_key},
        **kwargs
    )
    
def create_sync_client(server_key: str, **kwargs) -> httpx.Client:
    logger.debug("Creating new sync HTTPX client.")
    return httpx.Client(
        base_url="https://api.erlc.gg/",
        headers={"server-key": server_key},
        **kwargs
    )

class _AsyncContext:
    server_key: str
    connection: HTTPXClient | None

    async def __aenter__(self) -> Self:
        self.connection = create_async_client(self.server_key)
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.connection and not self.connection.is_closed:
            # use cast here because the context manager ensures AsyncClient
            await cast(httpx.AsyncClient, self.connection).aclose()
        self.connection = None
        self.closed = True

class _SyncContext:
    server_key: str
    connection: HTTPXClient | None

    def __enter__(self) -> Self:
        self.connection = create_sync_client(self.server_key)
        return self
    
    def __exit__(self, exc_type, exc, tb):
        if self.connection and not self.connection.is_closed:
            # use cast here because the context manager ensures Client
            cast(httpx.Client, self.connection).close()
        self.connection = None
        self.closed = True

class _BaseApiClient(_SyncContext, _AsyncContext):
    def __init__(self,
        server_key: str,
        *,
        policy: CommandPolicy | None = None,
        wait_for_rate_limit: bool = True,
        connection: HTTPXClient | None = None
    ) -> None:
        """
        Parameters
        ----------
        server_key: `str`
            The private server API key.
        policy: `CommandPolicy` | `None` (optional)
            The optional command policy to use to validate commands. Raises `CommandPolicyViolation` on violations.
        rate_limit_config: `RateLimitConfig` (optional)
            The rate limit configuration for this client. Defaults to safe values.
        connection: `HTTPXClient` | `None` (optional)
            An existing HTTPX client to use. If not provided, a new one will be created.
        """
        # prevent circular import
        from .v2.client import AsyncClient as V2AsyncClient
        from .v1.client import AsyncClient as V1AsyncClient
        
        self.server_key: str = server_key
        self.policy = policy
        self.wait_for_rate_limit = wait_for_rate_limit
        self.connection: HTTPXClient | None = connection
        self.closed: bool = False
        self.is_async: bool = issubclass(type(self), (V2AsyncClient, V1AsyncClient))
        
        self.registry = UserRegistry()
        
        # rate limit tracking attributes, updated on each request based on response headers
        self._post_expiration: int = int(time.time())
        self._get_remaining: int = 0
        self._get_expiration: int = int(time.time())
        
        if self.is_async:
            self.lock = asyncio.Lock()
        else:
            self.lock = threading.Lock()
    
    def _raise_for_status(self, resp: httpx.Response):
        body = resp.json()
        if resp.status_code == 429:
            logger.error("Currently being rate-limited by PRC.", extra={"body": body})
            try:
                raise RateLimited.from_dict(body)
            except DeserializationError:
                raise RateLimited(
                    code=429,
                    message="API call failed (rate limited by PRC - unknown refresh_after).",
                    retry_after=0.0
                )
                
        if resp.status_code != 200:
            try:
                logger.error("API call failed with non-200 status code.", extra={"body": body})
                raise ApiError.from_dict(body)
            except DeserializationError:
                logger.error(
                    "API call failed with non-200 status code %s.",
                    resp.status_code,
                    extra={"code": resp.status_code}
                )
                raise ApiError(code=resp.status_code, message="API call failed (status not 200).")
            
    def _update_ratelimit(self, resp: httpx.Response):
        headers = resp.headers
        
        limit_remaining = headers.get("x-ratelimit-remaining")
        limit_expiration = headers.get("x-ratelimit-reset")
        
        if resp.request.method == "GET":
            self._get_remaining = int(limit_remaining) or self._get_remaining
            self._get_expiration = int(limit_expiration) or self._get_expiration
        else:
            self._post_expiration = int(limit_expiration) or self._post_expiration
        
        logger.debug("Updated rate limit info.", extra={
            "get_remaining": self._get_remaining,
            "get_expiration": self._get_expiration,
            "post_expiration": self._post_expiration
        })
            
    def _get_method(self, endpoint: EndpointType) -> Literal["GET", "POST"]:
        if isinstance(endpoint, V2Endpoint):
            return "GET" if endpoint == V2Endpoint.v2_server else "POST"
        else:
            return "POST" if endpoint == V1Endpoint.command else "GET"
        
    async def _send_async_request(self, endpoint: EndpointType, **kwargs) -> httpx.Response:
        if self.connection is None and self.closed:
            logger.error("Attempted to send async request with closed connection.")
            raise RuntimeError("Unable to make request as this connection is closed.")
        if self.connection is None:
            logger.debug("No existing connection found; creating new async client for request.")
            self.connection = create_async_client(self.server_key)
        if not isinstance(self.connection, httpx.AsyncClient):
            logger.error("Async request attempted with non-async client.")
            raise RuntimeError("Cannot send async request; connection is not an async client.")
        
        method = self._get_method(endpoint)
        if self.wait_for_rate_limit:
            async with cast(asyncio.Lock, self.lock):
                if method == "GET":
                    wait_for = self._get_wait_time()
                else:
                    wait_for = self._post_wait_time()
                    
                if wait_for > 0:
                    logger.debug("Waiting for %s seconds due to rate limit before sending async request.", wait_for)
                    await asyncio.sleep(wait_for)
                    logger.debug("Rate limit waiting finished.")
                
                logger.debug("Sending async request to endpoint %s.", endpoint.value)
                resp = await self.connection.request(method, endpoint.value, **kwargs)
                self._update_ratelimit(resp)
                self._raise_for_status(resp)
                
                return resp
        
        logger.debug("Sending async request to endpoint %s.", endpoint.value)
        resp = await self.connection.request(method, endpoint.value, **kwargs)
        self._update_ratelimit(resp)
        self._raise_for_status(resp)
            
        return resp
    
    def _send_sync_request(self, endpoint: EndpointType, **kwargs) -> httpx.Response:
        if self.connection is None and self.closed:
            logger.error("Attempted to send sync request with closed connection.")
            raise RuntimeError("Unable to make request as this connection is closed.")
        if self.connection is None:
            logger.debug("No existing connection found; creating new sync client for request.")
            self.connection = create_sync_client(self.server_key)
        if not isinstance(self.connection, httpx.Client):
            logger.error("Sync request attempted with non-sync client.")
            raise RuntimeError("Cannot send sync request; connection is not a sync client.")
        
        method = self._get_method(endpoint)
        if self.wait_for_rate_limit:
            with cast(threading.Lock, self.lock):
                if method == "GET":
                    wait_for = self._get_wait_time()
                else:
                    wait_for = self._post_wait_time()
                    
                if wait_for > 0:
                    logger.debug("Waiting for %s seconds due to rate limit before sending sync request.", wait_for)
                    time.sleep(wait_for)
                    logger.debug("Rate limit waiting finished.")
                
                logger.debug("Sending sync request to endpoint %s.", endpoint.value)
                resp = self.connection.request(method, endpoint.value, **kwargs)
                self._update_ratelimit(resp)
                self._raise_for_status(resp)

                return resp
        
        logger.debug("Sending sync request to endpoint %s.", endpoint.value)
        resp = self.connection.request(method, endpoint.value, **kwargs)
        self._update_ratelimit(resp)
        self._raise_for_status(resp)
        
        return resp
    
    def _get_wait_time(self) -> float:
        if self._get_remaining > 0:
            return 0.0
        return max(self._get_expiration - time.time() + 1, 0)
    
    def _post_wait_time(self) -> float:
        return max(self._post_expiration - time.time() + 1, 0)
    
    async def aclose(self):
        if not isinstance(self.connection, httpx.AsyncClient):
            logger.error("Attempted to close async connection with non-async client.")
            raise RuntimeError("Connection is not an async client; close with .close().")
        if self.connection and not self.connection.is_closed:
            await self.connection.aclose()
        
        self.connection = None
        self.closed = True
        logger.info("Async connection closed.")
        
    def close(self):
        if not isinstance(self.connection, httpx.Client):
            logger.error("Attempted to close sync connection with non-sync client.")
            raise RuntimeError("Connection is not an sync client; close with .aclose().")
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        
        self.connection = None
        self.closed = True
        logger.info("Sync connection closed.")