from .models import Server, BundledServer
from .server import _GetServer

class AsyncClient(_GetServer):
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
        return await self._get_bundled_server_async()

class Client(_GetServer):
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
        return self._get_bundled_server_sync()