from pydantic import BaseModel
from ...v2.command import Command, CommandLike, normalize_command
from ...exceptions import CommandPolicyViolation

class CommandPreview(BaseModel):
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
    command: Command
    allowed: bool
    reason: str | None

class CommandPolicy:
    def __init__(self, whitelist: set[str], blacklist: set[str], *, max_length: int = 120) -> None:
        self.whitelist = {normalize_command(cmd) for cmd in whitelist}
        self.blacklist = {normalize_command(cmd) for cmd in blacklist}
        self.max_length = max_length
    
    def preview_command(self, command: CommandLike, *, raise_for_status: bool = False) -> CommandPreview:
        if isinstance(command, str):
            command = Command(text=command)
        
        if command.command in self.blacklist:
            preview = CommandPreview(command=command, allowed=False, reason="Command blacklisted")
        elif command.command not in self.whitelist:
            preview = CommandPreview(command=command, allowed=False, reason="Command not whitelisted")
        elif len(command.text) > self.max_length:
            preview = CommandPreview(command=command, allowed=False, reason="Command too long")
        else:
            preview = CommandPreview(command=command, allowed=True, reason=None)
        
        if raise_for_status and not preview.allowed:
            raise CommandPolicyViolation.from_preview(preview)
        return preview