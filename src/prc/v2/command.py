from collections.abc import Sequence
from typing import TYPE_CHECKING, ClassVar
from httpx import Response
from pydantic import BaseModel, field_validator
from ..v2.models import (
    Endpoint as V2Endpoint,
    Player as V2Player,
    FullUser as V2FullUser,
    UsernameUser as V2UsernameUser,
    IdUser as V2IdUser
)
from ..base_client import _BaseApiClient

if TYPE_CHECKING:
    from .client import AsyncClient, Client

def normalize_command(command: str) -> str:
    """Normalize a command by ensuring it starts with a colon."""
    return command if command.startswith(":") else f":{command}"

class Command(BaseModel):
    """Represents an in-game command.
    
    This model is not meant to be instantiated directly;
    instead, import and use the `cmd` instance to dynamically create `Command` objects:
    
    ```python
    from prc.v2 import cmd
    
    cmd.pm("Alice", "Hello World!") # Command(text=":pm Alice Hello World!")
    ```
    
    Attributes
    ----------
    text: `str`
        The command's normalized text.
    """
    text: str
    
    dangerous_cmds: ClassVar[set[str]] = {
        ":kick", ":ban", ":wanted", ":unwanted",
        ":jail", ":unjail", ":kill", ":heal",
        ":refresh", ":respawn"
    }
    
    @field_validator("text", mode="after")
    def normalize_text(cls, v):
        return normalize_command(v)
    
    async def asend(self, client: "AsyncClient"):
        """Sends this command to the API using the provided asynchronous client."""
        return await client.send_command(self)
    
    def send(self, client: "Client") -> Response:
        """Sends this command to the API using the provided synchronous client."""
        return client.send_command(self)
    
    @property
    def payload(self) -> dict[str, str]:
        """Returns the payload to send this command to the API."""
        return {"command": self.text}

    @property
    def command(self) -> str:
        """Returns the command with leading colon (`:h`, `:kick`, etc.)"""
        return self.text.split()[0]
    
    @property
    def dangerous(self) -> bool:
        """Returns True if the command is dangerous (e.g. `:kick all`, `:ban all`), else False."""
        return any(
            self.text.startswith((f"{cmd} all", f"{cmd} others"))
            for cmd in type(self).dangerous_cmds
        )

# define user types
type AnyUserType = V2Player | V2FullUser | V2UsernameUser | V2IdUser | str | int
type UsernameUserType = V2Player | V2FullUser | V2UsernameUser | str
type IdUserType = V2Player | V2FullUser | V2IdUser | int

type CommandLike = Command | str

class _CmdFactory:
    if TYPE_CHECKING:
        # define in-game command methods 
        def h(self, message: str) -> Command: ...
        def hint(self, message: str) -> Command: ...
        def m(self, message: str) -> Command: ...
        def message(self, message: str) -> Command: ...
        def pm(self, player: UsernameUserType | Sequence[UsernameUserType], message: str) -> Command: ...
        def privatemessage(self, player: UsernameUserType | Sequence[UsernameUserType], message: str) -> Command: ...
        def kick(self, player: AnyUserType | Sequence[AnyUserType], reason: str = "") -> Command: ...
        def ban(self, player: AnyUserType | Sequence[AnyUserType], reason: str = "") -> Command: ...
        def unban(self, player: AnyUserType | Sequence[AnyUserType]) -> Command: ...
        def wanted(self, player: UsernameUserType | Sequence[UsernameUserType]) -> Command: ...
        def unwanted(self, player: UsernameUserType | Sequence[UsernameUserType]) -> Command: ...
        def jail(self, player: UsernameUserType | Sequence[UsernameUserType]) -> Command: ...
        def unjail(self, player: UsernameUserType | Sequence[UsernameUserType]) -> Command: ...
        def kill(self, player: UsernameUserType | Sequence[UsernameUserType]) -> Command: ...
        def heal(self, player: UsernameUserType | Sequence[UsernameUserType]) -> Command: ...
        def refresh(self, player: UsernameUserType | Sequence[UsernameUserType]) -> Command: ...
        def respawn(self, player: UsernameUserType | Sequence[UsernameUserType]) -> Command: ...
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
        def call(*args, **kwargs) -> Command:
            # parse player/user objects into username/ID representations
            parsed: list[str] = []
            collected_args = list(args) + list(kwargs.values())
            
            for arg in collected_args:
                # treat non-string sequences as a grouped player list
                if isinstance(arg, Sequence) and not isinstance(arg, (str, bytes)):
                    items: list[str] = []
                    for item in arg:
                        if isinstance(item, V2Player):
                            items.append(item.user.name)
                        elif isinstance(item, (V2UsernameUser, V2FullUser)):
                            items.append(item.name)
                        elif isinstance(item, V2IdUser):
                            items.append(str(item.id))
                        else:
                            items.append(str(item))
                    parsed.append(','.join(items))
                else:
                    item = arg
                    if isinstance(item, V2Player):
                        parsed.append(item.user.name)
                    elif isinstance(item, (V2UsernameUser, V2FullUser)):
                        parsed.append(item.name)
                    elif isinstance(item, V2IdUser):
                        parsed.append(str(item.id))
                    else:
                        parsed.append(str(item))
            
            # join the parsed arguments
            joined_args = ' '.join(parsed)
            full = f"{name} {joined_args}".strip()
            return Command(text=full)
        return call

cmd: _CmdFactory = _CmdFactory()
"""Factory for creating in-game commands.

Used to build commands, such as `cmd.hint("Hello, World!")` or `cmd.kick(["player1", "player2"], "reason")`.

In-game commands have type hints/method stubs, but any command can be created the same way
and user arguments will be parsed automatically."""

class _SendCommand(_BaseApiClient):
    async def _send_command_async(self, command: str) -> Response:
        return await self._send_async_request(
            endpoint=V2Endpoint.v2_command,
            json={"command": normalize_command(command)}
        )
        
    def _send_command_sync(self, command: str) -> Response:
        return self._send_sync_request(
            endpoint=V2Endpoint.v2_command,
            json={"command": normalize_command(command)}
        )