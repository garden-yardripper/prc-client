from typing import Self, cast
import httpx

from .v2.models import Endpoint
from .exceptions import ApiError, RateLimited, DeserializationError
from . import utils

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
    def __init__(self, server_key: str, *, connection: HTTPXClient | None = None) -> None:
        from .v2.client import AsyncClient # prevent circular import
        self.server_key = server_key
        self.connection: HTTPXClient | None = connection
        self.closed = False
        self.is_async = issubclass(type(self), AsyncClient)
        
    async def _send_async_request(self, endpoint: Endpoint, **kwargs) -> httpx.Response:
        if self.connection is None and self.closed:
            raise RuntimeError("Unable to make request as this connection is closed.")
        if self.connection is None:
            # create the appropriate client based on the subclass type (async/sync)
            if self.is_async:
                self.connection = create_async_client(self.server_key)
            else:
                self.connection = create_sync_client(self.server_key)
        
        method = "GET" if endpoint == Endpoint.v2_server else "POST"
        
        if isinstance(self.connection, httpx.AsyncClient):
            resp = await self.connection.request(method, endpoint.value, **kwargs)
        else:
            resp = self.connection.request(method, endpoint.value, **kwargs)
        
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
            
        return resp
    
    def _send_sync_request(self, endpoint: Endpoint, **kwargs) -> httpx.Response:
        return utils.execute_async(self._send_async_request(endpoint, **kwargs))
    
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