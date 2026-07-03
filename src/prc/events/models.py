from dataclasses import dataclass
import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator

from ..users import IdUser
from ..v2.models import EmergencyCall
from ..v2.client import Client, AsyncClient
from ..command import cmd

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

class Context[T: (Client, AsyncClient)](BaseModel):
    """Represents the context of an in-game event.
    
    Use the `emergency_call` and `command` properties to obtain specific context data.
    Ensure to check the `event_type` before doing so to prevent accessing invalid data.
    
    Attributes
    ----------
    timestamp: `datetime.datetime`
        The event's timestamp as a datetime.
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
    
    # private attributes that will be added immediately after initialization
    _client: Annotated[T, PrivateAttr()]
    _b64_server: Annotated[str, PrivateAttr()]
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def reply(self, message: str) -> None:
        """Reply to this event with a message. Only valid for custom command events.
        
        Handler function must match the client type (`async def` for `AsyncClient`, `def` for `Client`)
        to use this method."""
        
        if self.event_type != "CustomCommand":
            raise ValueError("Can only reply to custom command events.")
        if not isinstance(self.client, Client):
            raise TypeError("Client type does not support sending messages.")
        
        user_id = int(self.origin)
        if self.client.registry is not None:
            player = self.client.registry.resolve(user_id) or self.client.get_player_from_user(user_id)
        else:
            player = self.client.get_player_from_user(user_id)
        self.client.send_command(cmd.pm(player, message))
    
    async def areply(self, message: str) -> None:
        """Reply to this event with a message. Only valid for custom command events.
        
        Handler function must match the client type (`async def` for `AsyncClient`, `def` for `Client`)
        to use this method."""
        
        if self.event_type != "CustomCommand":
            raise ValueError("Can only reply to custom command events.")
        if not isinstance(self.client, AsyncClient):
            raise TypeError("Client type does not support sending messages.")
        
        user_id = int(self.origin)
        if self.client.registry is not None:
            player = self.client.registry.resolve(user_id) or await self.client.get_player_from_user(user_id)
        else:
            player = await self.client.get_player_from_user(user_id)
        await self.client.send_command(cmd.pm(player, message))
    
    @field_validator("timestamp", mode="before")
    def timestamp_to_datetime(cls, v):
        if isinstance(v, int):
            return datetime.datetime.fromtimestamp(v)
        return v
    
    @property
    def client(self) -> T:
        """`ClientType`: The client instance associated with this event's router."""
        return self._client
    
    @property
    def server_id(self) -> str:
        """`str`: The Base64 server ID associated with this event."""
        return self._b64_server
    
    @property
    def emergency_call(self) -> EmergencyCall:
        """`EmergencyCall`: The emergency call data associated with this event."""
        if self.event_type != "EmergencyCallStarted":
            raise ValueError("This event is not an emergency call.")
        return EmergencyCall.model_validate(self.zzz_data)
    
    @property
    def command(self) -> CustomCommand:
        """`CustomCommand`: The custom command data associated with this event."""
        if self.event_type != "CustomCommand":
            raise ValueError("This event is not a custom command.")
        
        try:
            cmd = self.zzz_data["command"]
            argument = self.zzz_data["argument"]
        except KeyError:
            raise ValueError("Malformed command data (missing command or argument).")
        
        return CustomCommand(cmd, argument)
    
    @property
    def user(self) -> IdUser:
        """`IdUser`: The user who executed the custom command. Only available for custom command events."""
        if self.event_type != "CustomCommand":
            raise ValueError("This event is not a custom command.")
        return IdUser(id=int(self.origin))

class EventBatch(BaseModel):
    """Internal class representing a batch of events sent by the webhook.
    
    Attributes
    ----------
    contexts: `list[Context]`
        The list of event contexts in the batch.
    server: `str`
        The server ID to which the events belong (Base64 string).
    """
    events: list[Context]
    server: str