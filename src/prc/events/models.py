from dataclasses import dataclass
import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

from prc.v2.models import EmergencyCall

@dataclass
class CustomCommand:
    """Represents a custom `;` in-game command.
    
    Attributes
    ----------
    command: `str`
        The main command that was executed by the user.
    argument: `str`
        The command's arguments (the rest of the line after the command).
    """
    command: str
    argument: str

class Event(BaseModel):
    """Represents an in-game event.
    
    Use the `emergency_call` and `command` properties to obtain specific data on the event.
    Ensure to check the `event_type` before doing so to prevent accessing invalid data.
    
    Attributes
    ----------
    timestamp: `int`
        The event's timestamp as a unix timestamp.
    origin: `str`
        The origin of the event. In the case of custom commands, this will be the command user's ID as a string.
    event_type: `Literal["EmergencyCallStarted", "WebhookProbe", "CustomCommand"]`
        The event's type.
    """
    zzz_data: Annotated[dict, Field(alias="data")]
    timestamp: datetime.datetime
    event_type: Annotated[
        Literal["EmergencyCallStarted", "WebhookProbe", "CustomCommand"],
        Field(alias="event")
    ]
    origin: str
    
    @field_validator("timestamp", mode="before")
    def timestamp_to_datetime(cls, v):
        if isinstance(v, int):
            return datetime.datetime.fromtimestamp(v)
        return v
    
    @property
    def emergency_call(self) -> EmergencyCall:
        if self.event_type != "EmergencyCallStarted":
            raise ValueError("This event is not an emergency call.")
        return EmergencyCall.model_validate(self.zzz_data)
    
    @property
    def command(self) -> CustomCommand:
        if self.event_type != "CustomCommand":
            raise ValueError("This event is not a custom command.")
        
        try:
            cmd = self.zzz_data["command"]
            argument = self.zzz_data["argument"]
        except KeyError:
            raise ValueError("Malformed command data (missing command or argument).")
        
        return CustomCommand(cmd, argument)

class EventBatch(BaseModel):
    """Represents a batch of events sent by the webhook.
    
    Attributes
    ----------
    events: `list[Event]`
        The list of events in the batch.
    server: `str`
        The server to which the events belong (Base64 string).
    """
    events: list[Event]
    server: str