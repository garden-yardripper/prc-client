import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_pascal

from .users import FullUser


class Log(BaseModel):
    timestamp: datetime.datetime
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @field_validator("timestamp", mode="before")
    def timestamp_to_datetime(cls, v):
        if isinstance(v, int):
            return datetime.datetime.fromtimestamp(v)
        return v
    
    @field_validator(
        "user", "killed", "killer", "caller", "moderator",
        check_fields=False,
        mode="before"
    )
    def user_to_full_user(cls, v):
        if isinstance(v, str) and v == "Remote Server":
            return FullUser(name=v, id=0)
        return FullUser.from_delimited(v)

class JoinLog(Log):
    """Represents join/leave log.
    
    Attributes
    ----------
    timestamp: `datetime.datetime`
        The time the event occurred.
    user: `FullUser`
        The user who joined.
    join: `bool`
        Whether the user joined or left.
    """
    user: Annotated[FullUser, Field(alias="Player")]
    join: bool

class KillLog(Log):
    """Represents a kill log.
    
    Attributes
    ----------
    timestamp: `datetime.datetime`
        The time the event occurred.
    killed: `FullUser`
        The user who was killed.
    killer: `FullUser`
        The user who killed the other user.
    """
    killed: FullUser
    killer: FullUser
    
class CommandLog(Log):
    """Represents a command log.
    
    Attributes
    ----------
    timestamp: `datetime.datetime`
        The time the event occurred.
    user: `FullUser`
        The user who executed the command.
    command: `str`
        The command that was executed.
    """
    user: Annotated[FullUser, Field(alias="Player")]
    command: str
    
class ModCall(Log):
    """Represents a moderator call.
    
    Attributes
    ----------
    timestamp: `datetime.datetime`
        The time the event occurred.
    caller: `FullUser`
        The user who made the call.
    moderator: `FullUser`
        The moderator who responded to the call.
    """
    caller: FullUser
    moderator: FullUser