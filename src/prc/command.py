import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar
from httpx import Response

from .users import FullUser, UsernameUser, IdUser
from .v2.models import Player as V2Player
from .v1.models import Player as V1Player
from .users import AnyUserType, UsernameUserType

if TYPE_CHECKING:
    from .v2.client import AsyncClient as V2AsyncClient, Client as V2Client
    
logger = logging.getLogger(__name__)

def normalize_command(command: str) -> str:
    """Normalize a command by ensuring it starts with a colon."""
    return command if command.startswith(":") else f":{command}"

@dataclass
class Command:
    """Represents an in-game command.
    
    You should import and use the `cmd` instance to dynamically create `Command` objects
    instead of instantiating this class directly:
    
    ```python
    from prc import cmd
    
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
    
    def __post_init__(self) -> None:
        self.text = normalize_command(self.text)
    
    async def asend(self, client: "V2AsyncClient") -> Response:
        """Sends this command to the API using the provided asynchronous client."""
        logger.info("Sending async command: '%s'", self.text)
        return await client.send_command(self)
    
    def send(self, client: "V2Client") -> Response:
        """Sends this command to the API using the provided synchronous client."""
        logger.info("Sending sync command: '%s'", self.text)
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
                        if isinstance(item, (V2Player, V1Player)):
                            items.append(item.user.name)
                        elif isinstance(item, (UsernameUser, FullUser)):
                            items.append(item.name)
                        elif isinstance(item, IdUser):
                            items.append(str(item.id))
                        else:
                            items.append(str(item))
                    parsed.append(','.join(items))
                else:
                    item = arg
                    if isinstance(item, (V2Player, V1Player)):
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
            logger.debug("Created command: '%s'", full)
            
            return Command(text=full)
        return call

cmd: _CmdFactory = _CmdFactory()
"""Factory for creating in-game commands.

Used to build commands, such as `cmd.hint("Hello, World!")` or `cmd.kick(["player1", "player2"], "reason")`.

In-game commands have type hints/method stubs, but any command can be created the same way
and user arguments will be parsed automatically."""