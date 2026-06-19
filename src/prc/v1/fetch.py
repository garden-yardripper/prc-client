from itertools import chain
import logging
from ..base_client import _BaseApiClient, _Endpoint
from .models import (
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
        response = await self._send_async_request(endpoint=_Endpoint.v1_server)
        return Server.model_validate(response.json())
    
    async def get_players(self) -> list[Player]:
        logger.info("Fetching players data.")
        response = await self._send_async_request(endpoint=_Endpoint.v1_players)
        players = [Player.model_validate(player) for player in response.json()]
        if self.registry:
            for player in players:
                self.registry._add_user(player.user)
        return players
    
    async def get_staff(self) -> Staff:
        logger.info("Fetching staff data.")
        response = await self._send_async_request(endpoint=_Endpoint.v1_staff)
        staff = Staff.model_validate(response.json())
        if self.registry:
            for user in chain(staff.admins, staff.mods):
                self.registry._add_user(user)
        return staff
    
    async def get_join_logs(self) -> list[JoinLog]:
        logger.info("Fetching join logs data.")
        response = await self._send_async_request(endpoint=_Endpoint.v1_join_logs)
        logs = [JoinLog.model_validate(log) for log in response.json()]
        if self.registry:
            for log in logs:
                self.registry._add_user(log.user)
        return logs
    
    async def get_queue(self) -> Queue:
        logger.info("Fetching queue data.")
        response = await self._send_async_request(endpoint=_Endpoint.v1_queue)
        return Queue.model_validate(response.json())
    
    async def get_kill_logs(self) -> list[KillLog]:
        logger.info("Fetching kill logs data.")
        response = await self._send_async_request(endpoint=_Endpoint.v1_kill_logs)
        logs = [KillLog.model_validate(log) for log in response.json()]
        if self.registry:
            for log in logs:
                self.registry._add_user(log.killer)
                self.registry._add_user(log.killed)
        return logs
    
    async def get_command_logs(self) -> list[CommandLog]:
        logger.info("Fetching command logs data.")
        response = await self._send_async_request(endpoint=_Endpoint.v1_command_logs)
        logs = [CommandLog.model_validate(log) for log in response.json()]
        if self.registry:
            for log in logs:
                self.registry._add_user(log.user)
        return logs
    
    async def get_mod_calls(self) -> list[ModCall]:
        logger.info("Fetching mod calls data.")
        response = await self._send_async_request(endpoint=_Endpoint.v1_mod_calls)
        logs = [ModCall.model_validate(log) for log in response.json()]
        if self.registry:
            for log in logs:
                self.registry._add_user(log.caller)
                self.registry._add_user(log.moderator)
        return logs
    
    async def get_bans(self) -> Bans:
        logger.info("Fetching bans data.")
        response = await self._send_async_request(endpoint=_Endpoint.v1_bans)
        bans = Bans.model_validate(response.json())
        if self.registry:
            for user in bans.users:
                self.registry._add_user(user)
        return bans
    
    async def get_vehicles(self) -> list[Vehicle]:
        logger.info("Fetching vehicles data.")
        response = await self._send_async_request(endpoint=_Endpoint.v1_vehicles)
        return [Vehicle.model_validate(vehicle) for vehicle in response.json()]
    
class _GetDataSync(_BaseApiClient):
    def get_server(self) -> Server:
        logger.info("Fetching server data.")
        response = self._send_sync_request(endpoint=_Endpoint.v1_server)
        return Server.model_validate(response.json())
    
    def get_players(self) -> list[Player]:
        logger.info("Fetching players data.")
        response = self._send_sync_request(endpoint=_Endpoint.v1_players)
        players = [Player.model_validate(player) for player in response.json()]
        if self.registry:
            for player in players:
                self.registry._add_user(player.user)
        return players
    
    def get_staff(self) -> Staff:
        logger.info("Fetching staff data.")
        response = self._send_sync_request(endpoint=_Endpoint.v1_staff)
        staff = Staff.model_validate(response.json())
        if self.registry:
            for user in chain(staff.admins, staff.mods):
                self.registry._add_user(user)
        return staff
    
    def get_join_logs(self) -> list[JoinLog]:
        logger.info("Fetching join logs data.")
        response = self._send_sync_request(endpoint=_Endpoint.v1_join_logs)
        logs = [JoinLog.model_validate(log) for log in response.json()]
        if self.registry:
            for log in logs:
                self.registry._add_user(log.user)
        return logs
    
    def get_queue(self) -> Queue:
        logger.info("Fetching queue data.")
        response = self._send_sync_request(endpoint=_Endpoint.v1_queue)
        return Queue.model_validate({"Players": response.json()})
    
    def get_kill_logs(self) -> list[KillLog]:
        logger.info("Fetching kill logs data.")
        response = self._send_sync_request(endpoint=_Endpoint.v1_kill_logs)
        logs = [KillLog.model_validate(log) for log in response.json()]
        if self.registry:
            for log in logs:
                self.registry._add_user(log.killer)
                self.registry._add_user(log.killed)
        return logs
    
    def get_command_logs(self) -> list[CommandLog]:
        logger.info("Fetching command logs data.")
        response = self._send_sync_request(endpoint=_Endpoint.v1_command_logs)
        logs = [CommandLog.model_validate(log) for log in response.json()]
        if self.registry:
            for log in logs:
                self.registry._add_user(log.user)
        return logs
    
    def get_mod_calls(self) -> list[ModCall]:
        logger.info("Fetching mod calls data.")
        response = self._send_sync_request(endpoint=_Endpoint.v1_mod_calls)
        logs = [ModCall.model_validate(log) for log in response.json()]
        if self.registry:
            for log in logs:
                self.registry._add_user(log.caller)
                self.registry._add_user(log.moderator)
        return logs
    
    def get_bans(self) -> Bans:
        logger.info("Fetching bans data.")
        response = self._send_sync_request(endpoint=_Endpoint.v1_bans)
        bans = Bans.model_validate({"Users": response.json()})
        if self.registry:
            for user in bans.users:
                self.registry._add_user(user)
        return bans

    def get_vehicles(self) -> list[Vehicle]:
        logger.info("Fetching vehicles data.")
        response = self._send_sync_request(endpoint=_Endpoint.v1_vehicles)
        return [Vehicle.model_validate(vehicle) for vehicle in response.json()]