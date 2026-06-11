from collections.abc import Iterable
from typing import TYPE_CHECKING
from httpx import Response
from pydantic import BaseModel
from ..v2.models import Endpoint, Player, FullUser, UsernameUser, IdUser
from ..base_client import _BaseApiClient

def normalize_command(command: str) -> str:
    return command if command.startswith(":") else f":{command}"

class Command(BaseModel):
    text: str
    
    @property
    def payload(self) -> dict[str, str]:
        """Returns the payload to send this command to the API."""
        return {"command": self.text}

# define user types
type AnyUserType = Player | FullUser | UsernameUser | IdUser | str | int
type UsernameUserType = Player | FullUser | UsernameUser | str
type IdUserType = Player | FullUser | IdUser | int

type CommandLike = Command | str

class _CmdFactory:
    if TYPE_CHECKING:
        # define in-game command methods 
        def h(self, message: str) -> Command: ...
        def hint(self, message: str) -> Command: ...
        def m(self, message: str) -> Command: ...
        def message(self, message: str) -> Command: ...
        def pm(self, player: UsernameUserType | list[UsernameUserType], message: str) -> Command: ...
        def privatemessage(self, player: UsernameUserType | list[UsernameUserType], message: str) -> Command: ...
        def kick(self, player: AnyUserType | list[AnyUserType], reason: str = "") -> Command: ...
        def ban(self, player: AnyUserType | list[AnyUserType], reason: str = "") -> Command: ...
        def unban(self, player: AnyUserType | list[AnyUserType]) -> Command: ...
        def wanted(self, player: UsernameUserType | list[UsernameUserType]) -> Command: ...
        def unwanted(self, player: UsernameUserType | list[UsernameUserType]) -> Command: ...
        def jail(self, player: UsernameUserType | list[UsernameUserType]) -> Command: ...
        def unjail(self, player: UsernameUserType | list[UsernameUserType]) -> Command: ...
        def kill(self, player: UsernameUserType | list[UsernameUserType]) -> Command: ...
        def heal(self, player: UsernameUserType | list[UsernameUserType]) -> Command: ...
        def refresh(self, player: UsernameUserType | list[UsernameUserType]) -> Command: ...
        def respawn(self, player: UsernameUserType | list[UsernameUserType]) -> Command: ...
        def tp(self, player1: UsernameUserType, player2: UsernameUserType) -> Command: ...
        def teleport(self, player1: UsernameUserType, player2: UsernameUserType) -> Command: ...
        def admin(self, player: AnyUserType) -> Command: ...
        def unadmin(self, player: AnyUserType) -> Command: ...
        def mod(self, player: AnyUserType) -> Command: ...
        def unmod(self, player: AnyUserType) -> Command: ...
        def helper(self, player: AnyUserType) -> Command: ...
        def unhelper(self, player: AnyUserType) -> Command: ...
        def log(self, message: str) -> Command: ...
        def weather(self, weather: str) -> Command: ...
        def time(self, time: float) -> Command: ...
        def shutdown(self) -> Command: ...
    
    # handle argument parsing and custom command creation
    def __getattr__(self, name: str):
        def call(*args):
            # parse player/user objects into username/ID representations
            parsed: list[str] = []
            for arg in args:
                for item in arg if isinstance(arg, Iterable) else [arg]:
                    if isinstance(item, Player):
                        parsed.append(item.user.name)
                    elif isinstance(item, (UsernameUser, FullUser)):
                        parsed.append(item.name)
                    elif isinstance(item, IdUser):
                        parsed.append(str(item.id))
                    else:
                        parsed.append(str(item))
            
            # join the parsed arguments
            joined_args = ' '.join(parsed)
            full = f"{name} {joined_args}".strip()
            return Command(text=normalize_command(full))
        return call

cmd: _CmdFactory = _CmdFactory()
"""Factory for creating in-game commands.

Used to build commands, such as `cmd.hint("Hello, World!")` or `cmd.kick(["player1", "player2"], "reason")`.

In-game commands have type hints/method stubs, but any command can be created the same way
and user arguments will be parsed automatically."""

class _SendCommand(_BaseApiClient):
    async def _send_command_async(self, command: str) -> Response:
        return await self._send_async_request(
            endpoint=Endpoint.v2_command,
            json={"command": normalize_command(command)}
        )
        
    def _send_command_sync(self, command: str) -> Response:
        return self._send_sync_request(
            endpoint=Endpoint.v2_command,
            json={"command": normalize_command(command)}
        )
        
__all__ = ["cmd"]