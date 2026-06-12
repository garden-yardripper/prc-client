from httpx import Response
from .models import Server, BundledServer
from .server import _GetServer
from .command import _SendCommand, CommandLike

type ClientType = AsyncClient | Client

class AsyncClient(_GetServer, _SendCommand):
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
        vehicles: bool = False,
        immediate: bool = False
    ) -> Server:
        return await self._get_server_async(
            players=players,
            staff=staff,
            join_logs=join_logs,
            queue=queue,
            kill_logs=kill_logs,
            command_logs=command_logs,
            mod_calls=mod_calls,
            emergency_calls=emergency_calls,
            vehicles=vehicles,
            immediate=immediate
        )
    
    async def get_bundled_server(self, *, immediate: bool = False) -> BundledServer:
        return await self._get_bundled_server_async(immediate=immediate)
    
    async def send_command(self, command: CommandLike, *, immediate: bool = False) -> Response:
        cmd = command if isinstance(command, str) else command.text
        return await self._send_command_async(cmd, immediate=immediate)

class Client(_GetServer, _SendCommand):
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
        vehicles: bool = False,
        immediate: bool = False
    ) -> Server:
        return self._get_server_sync(
            players=players,
            staff=staff,
            join_logs=join_logs,
            queue=queue,
            kill_logs=kill_logs,
            command_logs=command_logs,
            mod_calls=mod_calls,
            emergency_calls=emergency_calls,
            vehicles=vehicles,
            immediate=immediate
        )
    
    def get_bundled_server(self, *, immediate: bool = False) -> BundledServer:
        return self._get_bundled_server_sync(immediate=immediate)
    
    def send_command(self, command: CommandLike, *, immediate: bool = False) -> Response:
        cmd = command if isinstance(command, str) else command.text
        return self._send_command_sync(cmd, immediate=immediate)