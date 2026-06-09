from ..base_client import _BaseApiClient
from .models import Endpoint, Server, BundledServer
from .. import utils

def _format_bool_params(mapping: dict[str, bool]) -> dict[str, str]:
    return {k: "true" if v else "false" for k, v in mapping.items()}

class _GetServer(_BaseApiClient):
    async def _get_server_async(
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
        params = _format_bool_params({
            "Players": players,
            "Staff": staff,
            "JoinLogs": join_logs,
            "Queue": queue,
            "KillLogs": kill_logs,
            "CommandLogs": command_logs,
            "ModCalls": mod_calls,
            "EmergencyCalls": emergency_calls,
            "Vehicles": vehicles
        })
        
        response = await self.send_async_request(
            endpoint=Endpoint.v2_server,
            params=params
        )
        
        return Server.model_validate(response.json())
    
    async def _get_bundled_server_async(self) -> BundledServer:
        params = _format_bool_params({
            "Players": True,
            "Staff": True,
            "JoinLogs": True,
            "Queue": True,
            "KillLogs": True,
            "CommandLogs": True,
            "ModCalls": True,
            "EmergencyCalls": True,
            "Vehicles": True,
        })
        
        response = await self.send_async_request(
            endpoint=Endpoint.v2_server,
            params=params
        )
        
        return BundledServer.model_validate(response.json())
    
    def _get_server_sync(self, **kwargs) -> Server:
        return utils.execute_async(self._get_server_async(**kwargs))
        
    def _get_bundled_server_sync(self) -> BundledServer:
        return utils.execute_async(self._get_bundled_server_async())

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