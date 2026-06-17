from ..base_client import _BaseApiClient
from .models import (
    Endpoint,
    JoinLog,
    Player,
    Server,
    Staff,
    Queue,
    KillLog,
    CommandLog,
    ModCall,
    Bans,
    Vehicle
)

class _GetDataAsync(_BaseApiClient):
    async def get_server(self) -> Server:
        response = await self._send_async_request(endpoint=Endpoint.server)
        return Server.model_validate(response.json())
    
    async def get_players(self) -> list[Player]:
        response = await self._send_async_request(endpoint=Endpoint.players)
        return [Player.model_validate(player) for player in response.json()]
    
    async def get_staff(self) -> Staff:
        response = await self._send_async_request(endpoint=Endpoint.staff)
        return Staff.model_validate(response.json())
    
    async def get_join_logs(self) -> list[JoinLog]:
        response = await self._send_async_request(endpoint=Endpoint.join_logs)
        return [JoinLog.model_validate(log) for log in response.json()]
    
    async def get_queue(self) -> Queue:
        response = await self._send_async_request(endpoint=Endpoint.queue)
        return Queue.model_validate(response.json())
    
    async def get_kill_logs(self) -> list[KillLog]:
        response = await self._send_async_request(endpoint=Endpoint.kill_logs)
        return [KillLog.model_validate(log) for log in response.json()]
    
    async def get_command_logs(self) -> list[CommandLog]:
        response = await self._send_async_request(endpoint=Endpoint.command_logs)
        return [CommandLog.model_validate(log) for log in response.json()]
    
    async def get_mod_calls(self) -> list[ModCall]:
        response = await self._send_async_request(endpoint=Endpoint.mod_calls)
        return [ModCall.model_validate(log) for log in response.json()]
    
    async def get_bans(self) -> Bans:
        response = await self._send_async_request(endpoint=Endpoint.bans)
        return Bans.model_validate(response.json())

    async def get_vehicles(self) -> list[Vehicle]:
        response = await self._send_async_request(endpoint=Endpoint.vehicles)
        return [Vehicle.model_validate(vehicle) for vehicle in response.json()]
    
class _GetDataSync(_BaseApiClient):
    def get_server(self) -> Server:
        response = self._send_sync_request(endpoint=Endpoint.server)
        return Server.model_validate(response.json())
    
    def get_players(self) -> list[Player]:
        response = self._send_sync_request(endpoint=Endpoint.players)
        return [Player.model_validate(player) for player in response.json()]
    
    def get_staff(self) -> Staff:
        response = self._send_sync_request(endpoint=Endpoint.staff)
        return Staff.model_validate(response.json())
    
    def get_join_logs(self) -> list[JoinLog]:
        response = self._send_sync_request(endpoint=Endpoint.join_logs)
        return [JoinLog.model_validate(log) for log in response.json()]
    
    def get_queue(self) -> Queue:
        response = self._send_sync_request(endpoint=Endpoint.queue)
        return Queue.model_validate(response.json())
    
    def get_kill_logs(self) -> list[KillLog]:
        response = self._send_sync_request(endpoint=Endpoint.kill_logs)
        return [KillLog.model_validate(log) for log in response.json()]
    
    def get_command_logs(self) -> list[CommandLog]:
        response = self._send_sync_request(endpoint=Endpoint.command_logs)
        return [CommandLog.model_validate(log) for log in response.json()]
    
    def get_mod_calls(self) -> list[ModCall]:
        response = self._send_sync_request(endpoint=Endpoint.mod_calls)
        return [ModCall.model_validate(log) for log in response.json()]
    
    def get_bans(self) -> Bans:
        response = self._send_sync_request(endpoint=Endpoint.bans)
        return Bans.model_validate(response.json())

    def get_vehicles(self) -> list[Vehicle]:
        response = self._send_sync_request(endpoint=Endpoint.vehicles)
        return [Vehicle.model_validate(vehicle) for vehicle in response.json()]