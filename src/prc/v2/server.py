from ..base_client import _BaseApiClient
from .models import Endpoint, Server, BundledServer

def _format_bool_params(mapping: dict[str, bool]) -> dict[str, str]:
    return {k: "true" if v else "false" for k, v in mapping.items()}

ALL_DATA_PARAMS = _format_bool_params({
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
        
        response = await self._send_async_request(
            endpoint=Endpoint.v2_server,
            params=params
        )
        
        return Server.model_validate(response.json())
    
    async def _get_bundled_server_async(self) -> BundledServer:
        response = await self._send_async_request(
            endpoint=Endpoint.v2_server,
            params=ALL_DATA_PARAMS
        )
        
        return BundledServer.model_validate(response.json())
    
    def _get_server_sync(
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
        
        response = self._send_sync_request(
            endpoint=Endpoint.v2_server,
            params=params
        )
        
        return Server.model_validate(response.json())
        
    def _get_bundled_server_sync(self) -> BundledServer:
        response = self._send_sync_request(
            endpoint=Endpoint.v2_server,
            params=ALL_DATA_PARAMS
        )
        
        return BundledServer.model_validate(response.json())