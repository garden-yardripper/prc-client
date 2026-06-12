import time
import asyncio
from typing import Self, cast
import httpx

from .v2.models import Endpoint
from .exceptions import ApiError, RateLimited, DeserializationError

type HTTPXClient = httpx.Client | httpx.AsyncClient

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
        handle_rate_limit: bool = True,
        connection: HTTPXClient | None = None
    ) -> None:
        from .v2.client import AsyncClient # prevent circular import
        self.server_key: str = server_key
        self.handle_rate_limit = handle_rate_limit
        self.connection: HTTPXClient | None = connection
        self.closed: bool = False
        self.is_async: bool = issubclass(type(self), AsyncClient)
        
        # rate limit tracking attributes, updated on each request based on response headers
        self.post_expiration: int = int(time.time())
        self.get_remaining: int = 0
        self.get_expiration: int = int(time.time())
    
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
        
    async def _send_async_request(self, endpoint: Endpoint, **kwargs) -> httpx.Response:
        if self.connection is None and self.closed:
            raise RuntimeError("Unable to make request as this connection is closed.")
        if self.connection is None:
            self.connection = create_async_client(self.server_key)
        if not isinstance(self.connection, httpx.AsyncClient):
            raise RuntimeError("Cannot send async request; connection is not an async client.")
        
        method = "GET" if endpoint == Endpoint.v2_server else "POST"
        if self.handle_rate_limit:
            if method == "GET":
                if self.get_on_cooldown:
                    await self.await_for_get_cooldown()
            else:
                if self.post_on_cooldown:
                    await self.await_for_post_cooldown()
        
        resp = await self.connection.request(method, endpoint.value, **kwargs)
        self._raise_for_status(resp)
        self._update_ratelimit(resp)
            
        return resp
    
    def _send_sync_request(self, endpoint: Endpoint, **kwargs) -> httpx.Response:
        if self.connection is None and self.closed:
            raise RuntimeError("Unable to make request as this connection is closed.")
        if self.connection is None:
            self.connection = create_sync_client(self.server_key)
        if not isinstance(self.connection, httpx.Client):
            raise RuntimeError("Cannot send sync request; connection is not a sync client.")
        
        method = "GET" if endpoint == Endpoint.v2_server else "POST"
        if self.handle_rate_limit:
            if method == "GET":
                if self.get_on_cooldown:
                    self.wait_for_get_cooldown()
            else:
                if self.post_on_cooldown:
                    self.wait_for_post_cooldown()
        
        resp = self.connection.request(method, endpoint.value, **kwargs)
        self._raise_for_status(resp)
        self._update_ratelimit(resp)
        
        return resp
    
    @property
    def get_on_cooldown(self) -> bool:
        return self.get_remaining <= 0 and self.get_expiration > time.time()
    
    @property
    def post_on_cooldown(self) -> bool:
        return self.post_expiration > time.time()
    
    def wait_for_get_cooldown(self):
        if self.is_async:
            raise RuntimeError("Client is not synchronous - use 'await_for_get_cooldown' instead.")
        if self.get_remaining <= 0:
            # add 1 second for redundancy
            time.sleep(max(self.get_expiration - time.time() + 1, 0))
        
    async def await_for_get_cooldown(self):
        if not self.is_async:
            raise RuntimeError("Client is not async - use 'wait_for_get_cooldown' instead.")
        if self.get_remaining <= 0:
            await asyncio.sleep(max(self.get_expiration - time.time() + 1, 0))
            
    def wait_for_post_cooldown(self):
        if self.is_async:
            raise RuntimeError("Client is not synchronous - use 'await_for_get_cooldown' instead.")
        time.sleep(max(self.post_expiration - time.time() + 1, 0))
        
    async def await_for_post_cooldown(self):
        if not self.is_async:
            raise RuntimeError("Client is not async - use 'wait_for_get_cooldown' instead.")
        await asyncio.sleep(max(self.post_expiration - time.time() + 1, 0))
    
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