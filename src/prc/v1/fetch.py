import logging
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

logger = logging.getLogger(__name__)

class _GetDataAsync(_BaseApiClient):
    async def get_server(self) -> Server:
        logger.info("Fetching server data.")
        response = await self._send_async_request(endpoint=Endpoint.server)
        return Server.model_validate(response.json())
    
    async def get_players(self) -> list[Player]:
        logger.info("Fetching players data.")
        response = await self._send_async_request(endpoint=Endpoint.players)
        return [Player.model_validate(player) for player in response.json()]
    
    async def get_staff(self) -> Staff:
        logger.info("Fetching staff data.")
        response = await self._send_async_request(endpoint=Endpoint.staff)
        return Staff.model_validate(response.json())
    
    async def get_join_logs(self) -> list[JoinLog]:
        logger.info("Fetching join logs data.")
        response = await self._send_async_request(endpoint=Endpoint.join_logs)
        return [JoinLog.model_validate(log) for log in response.json()]
    
    async def get_queue(self) -> Queue:
        logger.info("Fetching queue data.")
        response = await self._send_async_request(endpoint=Endpoint.queue)
        return Queue.model_validate(response.json())
    
    async def get_kill_logs(self) -> list[KillLog]:
        logger.info("Fetching kill logs data.")
        response = await self._send_async_request(endpoint=Endpoint.kill_logs)
        return [KillLog.model_validate(log) for log in response.json()]
    
    async def get_command_logs(self) -> list[CommandLog]:
        logger.info("Fetching command logs data.")
        response = await self._send_async_request(endpoint=Endpoint.command_logs)
        return [CommandLog.model_validate(log) for log in response.json()]
    
    async def get_mod_calls(self) -> list[ModCall]:
        logger.info("Fetching mod calls data.")
        response = await self._send_async_request(endpoint=Endpoint.mod_calls)
        return [ModCall.model_validate(log) for log in response.json()]
    
    async def get_bans(self) -> Bans:
        logger.info("Fetching bans data.")
        response = await self._send_async_request(endpoint=Endpoint.bans)
        return Bans.model_validate(response.json())

    async def get_vehicles(self) -> list[Vehicle]:
        logger.info("Fetching vehicles data.")
        response = await self._send_async_request(endpoint=Endpoint.vehicles)
        return [Vehicle.model_validate(vehicle) for vehicle in response.json()]
    
class _GetDataSync(_BaseApiClient):
    def get_server(self) -> Server:
        logger.info("Fetching server data.")
        response = self._send_sync_request(endpoint=Endpoint.server)
        return Server.model_validate(response.json())
    
    def get_players(self) -> list[Player]:
        logger.info("Fetching players data.")
        response = self._send_sync_request(endpoint=Endpoint.players)
        return [Player.model_validate(player) for player in response.json()]
    
    def get_staff(self) -> Staff:
        logger.info("Fetching staff data.")
        response = self._send_sync_request(endpoint=Endpoint.staff)
        return Staff.model_validate(response.json())
    
    def get_join_logs(self) -> list[JoinLog]:
        logger.info("Fetching join logs data.")
        response = self._send_sync_request(endpoint=Endpoint.join_logs)
        return [JoinLog.model_validate(log) for log in response.json()]
    
    def get_queue(self) -> Queue:
        logger.info("Fetching queue data.")
        response = self._send_sync_request(endpoint=Endpoint.queue)
        return Queue.model_validate({"Players": response.json()})
    
    def get_kill_logs(self) -> list[KillLog]:
        logger.info("Fetching kill logs data.")
        response = self._send_sync_request(endpoint=Endpoint.kill_logs)
        return [KillLog.model_validate(log) for log in response.json()]
    
    def get_command_logs(self) -> list[CommandLog]:
        logger.info("Fetching command logs data.")
        response = self._send_sync_request(endpoint=Endpoint.command_logs)
        return [CommandLog.model_validate(log) for log in response.json()]
    
    def get_mod_calls(self) -> list[ModCall]:
        logger.info("Fetching mod calls data.")
        response = self._send_sync_request(endpoint=Endpoint.mod_calls)
        return [ModCall.model_validate(log) for log in response.json()]
    
    def get_bans(self) -> Bans:
        logger.info("Fetching bans data.")
        response = self._send_sync_request(endpoint=Endpoint.bans)
        return Bans.model_validate({"Users": response.json()})

    def get_vehicles(self) -> list[Vehicle]:
        logger.info("Fetching vehicles data.")
        response = self._send_sync_request(endpoint=Endpoint.vehicles)
        return [Vehicle.model_validate(vehicle) for vehicle in response.json()]