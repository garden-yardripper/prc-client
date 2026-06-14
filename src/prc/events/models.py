from dataclasses import dataclass
import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

from prc.v2.models import EmergencyCall

@dataclass
class CustomCommand:
    command: str
    argument: str

class Event(BaseModel):
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
    events: list[Event]
    server: str