import threading
import time
import asyncio
from typing import Literal, Self, cast
import httpx
from dataclasses import dataclass

from .policy import CommandPolicy
from .v2.models import Endpoint as V2Endpoint
from .v1.models import Endpoint as V1Endpoint
from .exceptions import ApiError, RateLimited, DeserializationError

type HTTPXClient = httpx.Client | httpx.AsyncClient
type EndpointType = V1Endpoint | V2Endpoint

def create_async_client(server_key: str, **kwargs) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url="https://api.erlc.gg/",
        headers={"server-key": server_key},
        **kwargs
    )
    
def create_sync_client(server_key: str, **kwargs) -> httpx.Client:
    return httpx.Client(
        base_url="https://api.erlc.gg/",
        headers={"server-key": server_key},
        **kwargs
    )

@dataclass
class RateLimitConfig:
    wait_for_rate_limit: bool = True
    retry_on_rate_limit: bool = True
    
    max_retries: int = 5

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
        rate_limit_config: RateLimitConfig = RateLimitConfig(),
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
        
        from .v2.client import AsyncClient # prevent circular import
        self.server_key: str = server_key
        self.policy = policy
        self.rate_limit_config = rate_limit_config
        self.connection: HTTPXClient | None = connection
        self.closed: bool = False
        self.is_async: bool = issubclass(type(self), AsyncClient)
        
        # rate limit tracking attributes, updated on each request based on response headers
        self.post_expiration: int = int(time.time())
        self.get_remaining: int = 0
        self.get_expiration: int = int(time.time())
        
        if self.is_async:
            self.lock = asyncio.Lock()
        else:
            self.lock = threading.Lock()
    
    def _raise_for_status(self, resp: httpx.Response):
        body = resp.json()
        if resp.status_code == 429:
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
                raise ApiError.from_dict(body)
            except DeserializationError:
                raise ApiError(code=resp.status_code, message="API call failed (status not 200).")
            
    def _update_ratelimit(self, resp: httpx.Response):
        headers = resp.headers
        
        limit_remaining = headers.get("x-ratelimit-remaining")
        limit_expiration = headers.get("x-ratelimit-reset")
        
        if resp.request.method == "GET":
            self.get_remaining = int(limit_remaining) or self.get_remaining
            self.get_expiration = int(limit_expiration) or self.get_expiration
        else:
            self.post_expiration = int(limit_expiration) or self.post_expiration
            
    def _get_method(self, endpoint: EndpointType) -> Literal["GET", "POST"]:
        if isinstance(endpoint, V2Endpoint):
            return "GET" if endpoint == V2Endpoint.v2_server else "POST"
        else:
            return "POST" if endpoint == V1Endpoint.command else "GET"
        
    async def _send_async_request(self, endpoint: EndpointType, **kwargs) -> httpx.Response:
        if self.connection is None and self.closed:
            raise RuntimeError("Unable to make request as this connection is closed.")
        if self.connection is None:
            self.connection = create_async_client(self.server_key)
        if not isinstance(self.connection, httpx.AsyncClient):
            raise RuntimeError("Cannot send async request; connection is not an async client.")
        
        method = self._get_method(endpoint)
        if self.rate_limit_config.wait_for_rate_limit:
            async with cast(asyncio.Lock, self.lock):
                if method == "GET":
                    wait_for = self._get_wait_time()
                else:
                    wait_for = self._post_wait_time()
                    
                if wait_for > 0:
                    await asyncio.sleep(wait_for)
                                            
                resp = await self.connection.request(method, endpoint.value, **kwargs)
                self._update_ratelimit(resp)
                self._raise_for_status(resp)
                
                return resp
            
        resp = await self.connection.request(method, endpoint.value, **kwargs)
        self._update_ratelimit(resp)
        self._raise_for_status(resp)
            
        return resp
    
    def _send_sync_request(self, endpoint: EndpointType, **kwargs) -> httpx.Response:
        if self.connection is None and self.closed:
            raise RuntimeError("Unable to make request as this connection is closed.")
        if self.connection is None:
            self.connection = create_sync_client(self.server_key)
        if not isinstance(self.connection, httpx.Client):
            raise RuntimeError("Cannot send sync request; connection is not a sync client.")
        
        method = self._get_method(endpoint)
        if self.rate_limit_config.wait_for_rate_limit:
            with cast(threading.Lock, self.lock):
                if method == "GET":
                    wait_for = self._get_wait_time()
                else:
                    wait_for = self._post_wait_time()
                    
                if wait_for > 0:
                    time.sleep(wait_for)
                    
                resp = self.connection.request(method, endpoint.value, **kwargs)
                self._update_ratelimit(resp)
                self._raise_for_status(resp)

                return resp
            
        resp = self.connection.request(method, endpoint.value, **kwargs)
        self._update_ratelimit(resp)
        self._raise_for_status(resp)
        
        return resp
    
    def _get_wait_time(self) -> float:
        if self.get_remaining > 0:
            return 0.0
        return max(self.get_expiration - time.time() + 1, 0)
    
    def _post_wait_time(self) -> float:
        return max(self.post_expiration - time.time() + 1, 0)
    
    async def aclose(self):
        if not isinstance(self.connection, httpx.AsyncClient):
            raise RuntimeError("Connection is not an async client; close with .close().")
        if self.connection and not self.connection.is_closed:
            await self.connection.aclose()
        
        self.connection = None
        self.closed = True
        
    def close(self):
        if not isinstance(self.connection, httpx.Client):
            raise RuntimeError("Connection is not an sync client; close with .aclose().")
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        
        self.connection = None
        self.closed = True