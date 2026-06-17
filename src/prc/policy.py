import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from .exceptions import CommandPolicyViolation

if TYPE_CHECKING:
    from .command import Command, CommandLike
    
logger = logging.getLogger(__name__)

@dataclass
class CommandPreview:
    """Represents the result of a command preview.
    
    Attributes
    ----------
    command: `Command`
        The preview's Command object.
    allowed: `bool`
        Whether the command violates the command policy.
    reason: `str` | `None`
        The reason the command is not allowed.
    """
    command: "Command"
    allowed: bool
    reason: str | None

class CommandPolicy:
    def __init__(self, *,
        whitelist: set[str] | None = None,
        blacklist: set[str] | None = None,
        max_length: int | None = None
    ) -> None:
        """Initialize a new CommandPolicy.

        Parameters
        ----------
        whitelist: `set[str]` | `None` (optional)
            A set of allowed commands.
        blacklist: `set[str]` | `None` (optional)
            A set of forbidden commands. Takes priority over whitelist.
        max_length: `int` (optional)
            The maximum length of a command. Defaults to 120.
        """
        # prevent circular import
        from .command import normalize_command
        
        whitelist = whitelist or set()
        blacklist = blacklist or set()
        self.whitelist = {normalize_command(cmd) for cmd in whitelist}
        self.blacklist = {normalize_command(cmd) for cmd in blacklist}
        self.max_length = max_length
    
    def preview_command(self, command: "CommandLike", *, raise_for_status: bool = False) -> CommandPreview:
        """Previews a command against this policy, returning a `CommandPreview` object
        or raising a `CommandPolicyViolation` if the command is not allowed and `raise_for_status` is `True`.
        
        This importantly does **NOT** send a request to the API.

        Parameters
        ----------
        command: `CommandLike`
            The command to preview.
        raise_for_status: `bool` (optional)
            Whether to raise a `CommandPolicyViolation` if the command is not allowed. Defaults to `False`.

        Returns
        -------
        `CommandPreview`
            The preview of the command.
        """
        if isinstance(command, str):
            # prevent circular import
            from .command import Command
            command = Command(text=command)
        
        if command.command in self.blacklist:
            logger.warning("Command '%s' is blacklisted.", command.text)
            preview = CommandPreview(command, allowed=False, reason="Command blacklisted")
        elif command.command not in self.whitelist:
            logger.warning("Command '%s' is not whitelisted.", command.text)
            preview = CommandPreview(command, allowed=False, reason="Command not whitelisted")
        elif self.max_length and len(command.text) > self.max_length:
            logger.warning("Command '%s' exceeds maximum length.", command.text)
            preview = CommandPreview(command, allowed=False, reason="Command too long")
        else:
            preview = CommandPreview(command, allowed=True, reason=None)
        
        if raise_for_status and not preview.allowed:
            raise CommandPolicyViolation.from_preview(preview)
        return preview