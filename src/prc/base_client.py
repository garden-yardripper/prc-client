from typing import cast
import httpx

from prc.v2.models import Endpoint
from prc.exceptions import ApiError, RateLimited, DeserializationError
from prc import utils

type HTTPXClient = httpx.Client | httpx.AsyncClient

class _AsyncContext:
    server_key: str
    connection: HTTPXClient | None

    async def __aenter__(self) -> httpx.AsyncClient:
        self.connection = httpx.AsyncClient(
            base_url="https://api.erlc.gg/",
            headers={"server-key": self.server_key}
        )
        return self.connection
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.connection and not self.connection.is_closed:
            # use cast here because the context manager ensures AsyncClient
            await cast(httpx.AsyncClient, self.connection).aclose()
        self.connection = None
        self.closed = True

class _SyncContext:
    server_key: str
    connection: HTTPXClient | None

    def __enter__(self) -> httpx.Client:
        self.connection = httpx.Client(
            base_url="https://api.erlc.gg/",
            headers={"server-key": self.server_key}
        )
        return self.connection
    
    def __exit__(self, exc_type, exc, tb):
        if self.connection and not self.connection.is_closed:
            # use cast here because the context manager ensures Client
            cast(httpx.Client, self.connection).close()
        self.connection = None
        self.closed = True

class _BaseApiClient(_SyncContext, _AsyncContext):
    def __init__(self, server_key: str, *, connection: HTTPXClient | None = None) -> None:
        self.server_key = server_key
        self.connection: HTTPXClient | None = connection
        self.closed = False
        
    async def send_async_request(self, endpoint: Endpoint, **kwargs) -> httpx.Response:
        if self.connection is None and self.closed:
            raise RuntimeError("Unable to make request as this connection is closed.")
        if self.connection is None:
            self.connection = httpx.AsyncClient(
                base_url="https://api.erlc.gg/",
                headers={"server-key": self.server_key}
            )
        
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
    
    def send_sync_request(self, endpoint: Endpoint, **kwargs) -> httpx.Response:
        return utils.execute_async(self.send_async_request(endpoint, **kwargs))