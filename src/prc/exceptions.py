import logging

logger = logging.getLogger(__name__)

class DeserializationError(Exception):
    """Raised when PRC API JSON data was unable to be deserialized into a Python object."""

class ApiError(Exception):
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