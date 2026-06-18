from .v2.models import Server, BundledServer
from .users import FullUser, IdUser, StrictUserType, UsernameUser
from .exceptions import DataNotRequestedError
from itertools import chain

class UserRegistry:
    def __init__(self):
        self._by_id: dict[int, FullUser] = {}
        self._by_username: dict[str, FullUser] = {}
    
    def _add_user(self, user: FullUser):
        self._by_id[user.id] = user
        self._by_username[user.name] = user
    
    def _extract_user_data_from_server(self, server: Server | BundledServer):
        try:
            for player in server.players:
                self._add_user(player.user)
        except DataNotRequestedError:
            pass
        
        try:
            for user in chain(server.staff.admins, server.staff.mods, server.staff.helpers):
                self._add_user(user)
        except DataNotRequestedError:
            pass
        
        try:
            for log in server.join_logs:
                self._add_user(log.user)
        except DataNotRequestedError:
            pass
        
        try:
            for log in server.kill_logs:
                self._add_user(log.killer)
                self._add_user(log.killed)
        except DataNotRequestedError:
            pass
        
        try:
            for log in server.command_logs:
                self._add_user(log.user)
        except DataNotRequestedError:
            pass
        
        try:
            for log in server.mod_calls:
               self._add_user(log.caller)
               self._add_user(log.moderator)
        except DataNotRequestedError:
            pass
        
    def resolve(self, user: StrictUserType) -> FullUser | None:
        """Resolves a user reference to a `FullUser` object,
        or returns `None` if the user is not found in the registry.
        
        Arguments
        ---------
        user: `StrictUserType`
            A user reference to search for in the registry.
            
        Returns
        -------
        `FullUser` | `None`
            The resolved `FullUser` object, or `None` if not found.
        """
        
        if isinstance(user, FullUser):
            return user
        
        id_search = None
        name_search = None
        if isinstance(user, UsernameUser):
            name_search = user.name
        elif isinstance(user, IdUser):
            id_search = user.id
        elif isinstance(user, str):
            name_search = user
        else:
            id_search = user
            
        if id_search:
            return self._by_id.get(id_search)
        if name_search:
            return self._by_username.get(name_search)
        
        return None