import logging
from collections.abc import Collection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .policy import CommandPreview
    from .command import Command

logger = logging.getLogger(__name__)

class PRCError(Exception):
    """Base class for all PRC API errors."""

class WebhookError(PRCError):
    """Base class for all event webhook errors."""
    
class MissingSignatureError(WebhookError):
    """Required data for signature verification is missing."""
    
class InvalidSignatureError(WebhookError):
    """The request's signature is invalid."""

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
    codes: Collection[int] | int | range | None = None
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

    @classmethod
    def _matches_code(cls, code: int) -> bool:
        """Returns True if this class is configured to handle the provided error code, else False."""
        if isinstance(cls.codes, Collection):
            if any(code == c for c in cls.codes):
                return True
        elif isinstance(cls.codes, range):
            if code in cls.codes:
                return True
        elif isinstance(cls.codes, int):
            if code == cls.codes:
                return True
        
        return False

    @classmethod
    def _dispatch_class(cls, code: int) -> type["ApiError"]:
        """Finds the most specific ApiError subclass that matches an error code."""
        for child in cls.__subclasses__():
            # iterate over this class's children
            best = child._dispatch_class(code)
            if best is not child:
                # there is a more specific subclass under this child, propagate it up
                return best

            # no more specific subclass matched, check if this child matches
            if child._matches_code(code):
                print(f"Found matching subclass {child.__name__} for code {code}.")
                return child

        # no more specific match was found, return this class
        return cls
    
    @classmethod
    def from_dict(cls, data: dict):
        whitelist = ("code", "message", "retry_after")
        clean = {k: v for k, v in data.items() if k in whitelist}
        
        error_cls = cls._dispatch_class(clean["code"]) if "code" in clean else cls
        
        if "code" not in clean or "message" not in clean or (
            error_cls is RateLimited and "retry_after" not in clean
        ):
            logger.error("Data for ApiError is missing one or more necessary fields.")
            raise DeserializationError("Data for ApiError is missing one or more necessary fields.")

        logger.debug("Validated ApiError data.")
        print(f"Dispatching to {error_cls.__name__} for code {clean['code']}.")
        return error_cls(**clean)
    
class SystemError(ApiError):
    """A subclass of `ApiError` that stores PRC system error classes."""
    codes = range(0, 2000)
    
class AuthenticationError(ApiError):
    """A subclass of `ApiError` that stores PRC authentication error classes."""
    codes = range(2000, 3000)
    
class RequestError(ApiError):
    """A subclass of `ApiError` that stores PRC request error classes."""
    codes = range(3000, 4000)
    
class AccessError(ApiError):
    """A subclass of `ApiError` that stores PRC access error classes, including `RateLimited`."""
    codes = range(4000, 5000)

class SpecialError(ApiError):
    """A subclass of `ApiError` that stores PRC special error classes."""
    codes = range(9000, 10000)

class UnknownError(SystemError):
    """A `SystemError` that is raised when an unknown error occurs."""
    codes = 0
    
class RobloxCommunicationError(SystemError):
    """A `SystemError` that is raised when the PRC API is unable to communicate with Roblox or your private server."""
    codes = 1001

class InternalSystemError(SystemError):
    """A `SystemError` that is raised when the PRC API encounters an internal error."""
    codes = 1002
    
class ServerKeyNotProvided(AuthenticationError):
    """An `AuthenticationError` that is raised when a required server key is not provided."""
    codes = 2000

class ServerKeyFormatError(AuthenticationError):
    """An `AuthenticationError` that is raised when a server key is provided but is formatted incorrectly."""
    codes = 2001

class ServerKeyInvalidError(AuthenticationError):
    """An `AuthenticationError` that is raised when a server key is provided but is invalid or expired."""
    codes = 2002

class GlobalKeyInvalidError(AuthenticationError):
    """An `AuthenticationError` that is raised when a global key is provided but is invalid."""
    codes = 2003

class ServerKeyBannedError(AuthenticationError):
    """An `AuthenticationError` that is raised when the provided server key is banned from accessing the API."""
    codes = 2004
    
class InvalidCommandError(RequestError):
    """A `RequestError` that is raised when a provided command is invalid or malformed."""
    codes = 3001
    
class ServerOfflineError(RequestError):
    """A `RequestError` that is raised when the server is offline or has zero players when sending a command."""
    codes = 3002
    
class UnauthorizedError(AccessError):
    """An `AccessError` that is raised when the provided server key does not have permission
    to send a command to the server."""
    codes = 4000

class RateLimited(AccessError):
    """An `AccessError` that is raised when an API rate limit is reached."""
    codes = 4001

    def __init__(self, code: int, message: str, retry_after: float):
        self.retry_after = retry_after
        super().__init__(code, message)
        
class CommandRestrictedError(AccessError):
    """An `AccessError` that is raised when a command is restricted by the API."""
    codes = 4002
    
class MessageProhibitedError(AccessError):
    """An `AccessError` that is raised when a command's message is prohibited by the API."""
    codes = 4003

class ResourceRestrictedError(SpecialError):
    """A `SpecialError` that is raised when the resource you are attempting to access is restricted."""
    codes = 9998

class ModuleOutdatedError(SpecialError):
    """A `SpecialError` that is raised when the module running on the in-game server is outdated.
    
    To resolve this error, restart your server via :shutdown or kicking all players and retrying."""
    codes = 9999
