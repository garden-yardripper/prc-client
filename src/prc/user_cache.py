from .v2.models import Server, BundledServer
from .users import FullUser
from .exceptions import DataNotRequestedError
from itertools import chain

class _UserCache:
    def __init__(self):
        self._by_id: dict[int, FullUser] = {}
        self._by_username: dict[str, FullUser] = {}
        
    def _extract_user_data_from_server(self, server: Server | BundledServer):
        try:
            for player in server.players:
                self._by_id[player.user.id] = player.user
                self._by_username[player.user.name] = player.user
        except DataNotRequestedError:
            pass
        
        try:
            for user in chain(server.staff.admins, server.staff.mods, server.staff.helpers):
                self._by_id[user.id] = user
                self._by_username[user.name] = user
        except DataNotRequestedError:
            pass
        
        try:
            for log in server.join_logs:
                self._by_id[log.user.id] = log.user
                self._by_username[log.user.name] = log.user
        except DataNotRequestedError:
            pass
        
        try:
            for log in server.kill_logs:
                self._by_id[log.killer.id] = log.killer
                self._by_username[log.killer.name] = log.killer
                
                self._by_id[log.killed.id] = log.killed
                self._by_username[log.killed.name] = log.killed
        except DataNotRequestedError:
            pass
        
        try:
            for log in server.command_logs:
                self._by_id[log.user.id] = log.user
                self._by_username[log.user.name] = log.user
        except DataNotRequestedError:
            pass
        
        try:
            for log in server.mod_calls:
               self._by_id[log.caller.id] = log.caller
               self._by_username[log.caller.name] = log.caller
               
               self._by_id[log.moderator.id] = log.moderator
               self._by_username[log.moderator.name] = log.moderator
        except DataNotRequestedError:
            pass