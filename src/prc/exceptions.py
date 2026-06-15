import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .policy import CommandPreview
    from .command import Command

logger = logging.getLogger(__name__)

class PRCError(Exception):
    """Base class for all PRC API errors."""

class DeserializationError(PRCError):
    """Raised when PRC API JSON data was unable to be deserialized into a Python object."""

class DataNotRequestedError(PRCError):
    """Raised when attempting to access data that was not requested from the API."""

class CommandPolicyViolation(PRCError):
    """Represents a raised violation of the command policy.
    
    Attributes
    ----------
    command: `Command`
        The preview's Command object.
    reason: `str` | `None`
        The reason the command is not allowed.
    """
    def __init__(self, command: "Command", reason: str | None = None) -> None:
        self.command: "Command" = command
        self.reason: str | None = reason
        super().__init__(f"CommandPolicyViolation: {self.reason}")
        
    @classmethod
    def from_preview(cls, preview: "CommandPreview"):
        # Use the provided preview's Command directly to avoid circular imports.
        return cls(preview.command, preview.reason)
        

class ApiError(PRCError):
    """Raised when the PRC API returned an error."""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")
    
    @classmethod
    def from_dict(cls, data: dict):
        whitelist = ("code", "message", "retry_after")
        clean = {k: v for k, v in data.items() if k in whitelist}
        
        if "code" not in clean or "message" not in clean or (
            cls is RateLimited and "retry_after" not in clean
        ):
            logger.error("Data for ApiError is missing one or more necessary fields.")
            raise DeserializationError("Data for ApiError is missing one or more necessary fields.")

        logger.debug("Validated ApiError data.")
        return cls(**clean)

class RateLimited(ApiError):
    """A subclass of `ApiError` that is raised when an API rate limit is reached."""
    def __init__(self, code: int, message: str, retry_after: float):
        self.retry_after = retry_after
        super().__init__(code, message)