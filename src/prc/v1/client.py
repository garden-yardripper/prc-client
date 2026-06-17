from httpx import Response
from ..utils import _read_env_var
from ..command import CommandLike
from .fetch import _GetDataAsync, _GetDataSync
from .send_command import _SendCommand

class AsyncClient(_GetDataAsync, _SendCommand):
    async def send_command(self, command: CommandLike) -> Response:
        return await self._send_command_async(command)
    
    @classmethod
    def from_env(cls, env_key: str | None = None, **kwargs) -> "AsyncClient":
        """Create a new `AsyncClient` instance from environment variables.
        
        To configure rate limit handling, set the "PRC_WAIT_FOR_RATE_LIMIT" environment variable
        to "true" or "false" (defaults to "false").

        Arguments
        ---------
        env_key: `str` | `None` (optional)
            The environment variable key to use for the server key. Defaults to "PRC_SERVER_KEY".
        **kwargs
            Additional keyword arguments to pass to the `AsyncClient` constructor.
            
        Returns
        -------
        `AsyncClient`
            The constructed `AsyncClient` instance.
        """
        server_key = _read_env_var(env_key or "PRC_SERVER_KEY")
        wait_for_rate_limit = _read_env_var("PRC_WAIT_FOR_RATE_LIMIT", "false").lower() == "true"
        
        return cls(server_key=server_key, wait_for_rate_limit=wait_for_rate_limit, **kwargs)

class Client(_GetDataSync, _SendCommand):
    def send_command(self, command: CommandLike) -> Response:
        return self._send_command_sync(command)
    
    @classmethod
    def from_env(cls, env_key: str | None = None, **kwargs) -> "Client":
        """Create a new `Client` instance from environment variables.
        
        To configure rate limit handling, set the "PRC_WAIT_FOR_RATE_LIMIT" environment variable
        to "true" or "false" (defaults to "false").

        Arguments
        ---------
        env_key: `str` | `None` (optional)
            The environment variable key to use for the server key. Defaults to "PRC_SERVER_KEY".
        **kwargs
            Additional keyword arguments to pass to the `Client` constructor.
            
        Returns
        -------
        `Client`
            The constructed `Client` instance.
        """
        server_key = _read_env_var(env_key or "PRC_SERVER_KEY")
        wait_for_rate_limit = _read_env_var("PRC_WAIT_FOR_RATE_LIMIT", "false").lower() == "true"
        
        return cls(server_key=server_key, wait_for_rate_limit=wait_for_rate_limit, **kwargs)