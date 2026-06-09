from ..base_client import _BaseApiClient
from .models import Endpoint, Server, BundledServer

class AsyncClient(_BaseApiClient):
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
        params = {
            "Players": str(players).lower(),
            "Staff": str(staff).lower(),
            "JoinLogs": str(join_logs).lower(),
            "Queue": str(queue).lower(),
            "KillLogs": str(kill_logs).lower(),
            "CommandLogs": str(command_logs).lower(),
            "ModCalls": str(mod_calls).lower(),
            "EmergencyCalls": str(emergency_calls).lower(),
            "Vehicles": str(vehicles).lower()
        }
        
        response = await self.send_async_request(
            endpoint=Endpoint.v2_server,
            params=params
        )
        
        return Server.model_validate(response.json())
    
    async def get_bundled_server(self) -> BundledServer:
        params = {
            "Players": "true",
            "Staff": "true",
            "JoinLogs": "true",
            "Queue": "true",
            "KillLogs": "true",
            "CommandLogs": "true",
            "ModCalls": "true",
            "EmergencyCalls": "true",
            "Vehicles": "true",
        }
        
        response = await self.send_async_request(
            endpoint=Endpoint.v2_server,
            params=params
        )
        
        return BundledServer.model_validate(response.json())

class Client(_BaseApiClient):
    pass