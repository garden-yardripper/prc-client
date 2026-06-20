from typing import TYPE_CHECKING
from httpx import Response

from ..utils import _read_env_var
from ..users import FullUser, IdUser, UsernameUser
from .models import Player, Server, BundledServer
from .server import _GetServer
from .send_command import _SendCommand

if TYPE_CHECKING:
    from ..command import AnyUserType, CommandLike

def _get_player_in_server_from_user(
    server: Server | BundledServer,
    user: "AnyUserType",
    partial_match: bool
) -> Player:
    if isinstance(user, Player):
        return user
    
    id_search = None
    name_search = None
    
    if isinstance(user, (FullUser, IdUser)):
        id_search = user.id
    elif isinstance(user, UsernameUser):
        name_search = user.name
    else:
        if isinstance(user, int):
            id_search = user
        elif isinstance(user, str):
            name_search = user
        else:
            name_search = str(user)
        
    for player in server.players:
        if partial_match:
            if (id_search is not None and player.user.id == id_search) or (
                name_search is not None and player.user.name.lower().startswith(name_search.lower())
            ):
                return player
        else:
            if (id_search is not None and player.user.id == id_search) or (
                name_search is not None and player.user.name == name_search
            ):
                return player
            
    raise ValueError("User not found in server")

class AsyncClient(_GetServer, _SendCommand):
    """Asynchronous client for the ER:LC private server API."""
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
        """Get a `Server` object with only the specified data.
        Use parameters to control which data is included."""
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
        """Get a `BundledServer` object with all server data available."""
        return await self._get_bundled_server_async()
    
    async def send_command(self, command: "CommandLike") -> Response:
        """Send a command to the server.

        Parameters
        ----------
        command: `CommandLike`
            The command to send to the server.
        
        Returns
        -------
        `Response`
            The raw HTTPX response from the server.
        """
        if self.policy:
            self.policy.preview_command(command, raise_for_status=True)
        return await self._send_command_async(command)
    
    async def get_player_from_user(
        self,
        user: "AnyUserType",
        server: Server | BundledServer | None = None,
        *,
        partial_match: bool = False
    ) -> Player:
        """Utility function to get an in-game `Player` from a `User` type.
        
        This is useful to access player data when you only have a `User` object.

        Parameters
        ----------
        user: `AnyUserType`
            The user to get the player from.
        server: `Server` | `None` (optional)
            An optional server to search for the player in.
            If you already have a `Server` object, you can pass it here to save an additional API call.
        partial_match: `bool` (optional)
            Whether to allow partial matches on usernames (player name starts with username). Defaults to `False`.
        
        Raises
        ------
        `ValueError`
            If the user is not in-game.

        Returns
        -------
        `Player`
            The player object for the given user.
        """
        if isinstance(user, Player):
            return user
        
        server = server or await self.get_server(players=True)
        return _get_player_in_server_from_user(server, user, partial_match)

    @classmethod
    def from_env(cls, env_key: str | None = None, **kwargs) -> "AsyncClient":
        """Create a new `AsyncClient` instance from environment variables.
        
        To configure rate limit handling, set the "PRC_WAIT_FOR_RATE_LIMIT" environment variable
        to "true" or "false" (defaults to "false").

        Arguments
        ---------
        env_key: `str` | `None` (optional)
            The environment variable key to use for the server key. Defaults to "PRC_SERVER_KEY".
        **kwargs
            Additional keyword arguments to pass to the `AsyncClient` constructor.
            
        Returns
        -------
        `AsyncClient`
            The constructed `AsyncClient` instance.
        """
        server_key = _read_env_var(env_key or "PRC_SERVER_KEY")
        wait_for_rate_limit = _read_env_var("PRC_WAIT_FOR_RATE_LIMIT", "false").lower() == "true"
        
        return cls(server_key=server_key, wait_for_rate_limit=wait_for_rate_limit, **kwargs)

class Client(_GetServer, _SendCommand):
    """Synchronous client for the ER:LC private server API."""
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
        """Get a lean `Server` object with only the specified data.
        Use parameters to control which data is included in the response."""
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
        """Get a `BundledServer` object with all server data available."""
        return self._get_bundled_server_sync()
    
    def send_command(self, command: "CommandLike") -> Response:
        """Send a command to the server.

        Parameters
        ----------
        command: `CommandLike`
            The command to send to the server.
        
        Returns
        -------
        `Response`
            The raw HTTPX response from the server.
        """
        if self.policy:
            self.policy.preview_command(command, raise_for_status=True)
        return self._send_command_sync(command)
    
    def get_player_from_user(
        self,
        user: "AnyUserType",
        server: Server | BundledServer | None = None,
        *,
        partial_match: bool = False
    ) -> Player:
        """Utility function to get an in-game `Player` from a `User` type.
        
        This is useful to access player data when you only have a `User` object.

        Parameters
        ----------
        user: `AnyUserType`
            The user to get the player from.
        server: `Server` | `None` (optional)
            An optional server to search for the player in.
            If you already have a `Server` object, you can pass it here to save an additional API call.
        partial_match: `bool` (optional)
            Whether to allow partial matches on usernames (player name starts with username). Defaults to `False`.
        
        Raises
        ------
        `ValueError`
            If the user is not in-game.

        Returns
        -------
        `Player`
            The player object for the given user.
        """
        if isinstance(user, Player):
            return user
        
        server = server or self.get_server(players=True)
        return _get_player_in_server_from_user(server, user, partial_match)
    
    @classmethod
    def from_env(cls, env_key: str | None = None, **kwargs) -> "Client":
        """Create a new `Client` instance from environment variables.
        
        To configure rate limit handling, set the "PRC_WAIT_FOR_RATE_LIMIT" environment variable
        to "true" or "false" (defaults to "false").

        Arguments
        ---------
        env_key: `str` | `None` (optional)
            The environment variable key to use for the server key. Defaults to "PRC_SERVER_KEY".
        **kwargs
            Additional keyword arguments to pass to the `Client` constructor.
            
        Returns
        -------
        `Client`
            The constructed `Client` instance.
        """
        server_key = _read_env_var(env_key or "PRC_SERVER_KEY")
        wait_for_rate_limit = _read_env_var("PRC_WAIT_FOR_RATE_LIMIT", "false").lower() == "true"
        
        return cls(server_key=server_key, wait_for_rate_limit=wait_for_rate_limit, **kwargs)