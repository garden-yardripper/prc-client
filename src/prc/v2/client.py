from httpx import Response
from .models import Server, BundledServer
from .server import _GetServer
from .command import _SendCommand, CommandLike

type ClientType = AsyncClient | Client

class AsyncClient(_GetServer, _SendCommand):
    """Asynchronous client for the ER:LC private server API."""
    async def get_server(
        self, *,
        players: bool = False,
        staff: bool = False,
        join_logs: bool = False,
        queue: bool = False,
        kill_logs: bool = False,
        command_logs: bool = False,
        mod_calls: bool = False,
        emergency_calls: bool = False,
        vehicles: bool = False
    ) -> Server:
        """Get a `Server` object with only the specified data.
        Use parameters to control which data is included."""
        return await self._get_server_async(
            players=players,
            staff=staff,
            join_logs=join_logs,
            queue=queue,
            kill_logs=kill_logs,
            command_logs=command_logs,
            mod_calls=mod_calls,
            emergency_calls=emergency_calls,
            vehicles=vehicles
        )
    
    async def get_bundled_server(self) -> BundledServer:
        """Get a `BundledServer` object with all server data available."""
        return await self._get_bundled_server_async()
    
    async def send_command(self, command: CommandLike) -> Response:
        """Send a command to the server.

        Parameters
        ----------
        command: `CommandLike`
            The command to send to the server.
        
        Returns
        -------
        `Response`
            The raw HTTPX response from the server.
        """
        cmd = command if isinstance(command, str) else command.text
        return await self._send_command_async(cmd)

class Client(_GetServer, _SendCommand):
    """Synchronous client for the ER:LC private server API."""
    def get_server(
        self, *,
        players: bool = False,
        staff: bool = False,
        join_logs: bool = False,
        queue: bool = False,
        kill_logs: bool = False,
        command_logs: bool = False,
        mod_calls: bool = False,
        emergency_calls: bool = False,
        vehicles: bool = False
    ) -> Server:
        """Get a lean `Server` object with only the specified data.
        Use parameters to control which data is included in the response."""
        return self._get_server_sync(
            players=players,
            staff=staff,
            join_logs=join_logs,
            queue=queue,
            kill_logs=kill_logs,
            command_logs=command_logs,
            mod_calls=mod_calls,
            emergency_calls=emergency_calls,
            vehicles=vehicles
        )
    
    def get_bundled_server(self) -> BundledServer:
        """Get a `BundledServer` object with all server data available."""
        return self._get_bundled_server_sync()
    
    def send_command(self, command: CommandLike) -> Response:
        """Send a command to the server.

        Parameters
        ----------
        command: `CommandLike`
            The command to send to the server.
        
        Returns
        -------
        `Response`
            The raw HTTPX response from the server.
        """
        cmd = command if isinstance(command, str) else command.text
        return self._send_command_sync(cmd)