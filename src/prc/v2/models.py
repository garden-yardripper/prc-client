import datetime
from enum import Enum
from typing import Annotated, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_pascal
from ..exceptions import DataNotRequestedError

class Endpoint(Enum):
    v2_server = "/v2/server"
    v2_command = "/v2/server/command"
    
    fall_blank_map = "/maps/fall_blank.png"
    fall_postals_map = "/maps/fall_postals.png"
    winter_blank_map = "/maps/snow_blank.png"
    winter_postals_map = "/maps/snow_postals.png"

def _validate_datetime(v):
    if isinstance(v, int):
        return datetime.datetime.fromtimestamp(v)
    return v

class UsernameUser(BaseModel):
    """Represents a user returned by the API with only a username.
    
    Attributes
    ----------
    name: `str`
        The user's username.
    """
    name: str
    
    model_config = ConfigDict(frozen=True)
    
    def __str__(self):
        return self.name

class IdUser(BaseModel):
    """Represents a user returned by the API with only an ID.
    
    Attributes
    ----------
    id: `int`
        The user's ID.
    """
    id: int
    
    model_config = ConfigDict(frozen=True)
    
    def __int__(self):
        return self.id
    
    def __str__(self):
        return str(self.id)

class FullUser(BaseModel):
    """Represents a user returned by the API with a username and ID.
    
    Attributes
    ----------
    name: `str`
        The user's username.
    id: `int`
        The user's ID.
    """
    name: str
    id: int
    
    model_config = ConfigDict(frozen=True)
    
    @classmethod
    def from_delimited(cls, delimited: str):
        name, id = delimited.split(":", maxsplit=1)
        return cls(name=name, id=int(id))
    
    @classmethod
    def validate_full_user(cls, v):
        if isinstance(v, str):
            return cls.from_delimited(v)
        return v
    
    def __str__(self):
        return f"{self.name}:{self.id}"
    
    def __int__(self):
        return int(self.id)

class MinimalLocation(BaseModel):
    """Represents a location with minimal information."""
    x: Annotated[float, Field(alias="LocationX")]
    z: Annotated[float, Field(alias="LocationZ")]
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @property
    def position(self) -> tuple[float, float]:
        """Returns the (x, z) position as a tuple."""
        return self.x, self.z

class Location(MinimalLocation):
    postal_code: int
    street_name: str
    building_number: int
    
# possibly add command model

class Vehicle(BaseModel):
    name: str
    owner: UsernameUser
    plate: str
    texture: str
    color_hex: str
    color_name: str
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)

    @field_validator("owner", mode="before")
    def owner_to_username_user(cls, v):
        if isinstance(v, str):
            return UsernameUser(name=v)
        return v
    
class EmergencyCall(BaseModel):
    team: str
    caller: IdUser
    players: list[IdUser]
    position: MinimalLocation
    started_at: datetime.datetime
    call_number: int
    description: str
    position_descriptor: str
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @field_validator("caller", "players", mode="before")
    def caller_to_id_user(cls, v):
        if isinstance(v, int):
            return IdUser(id=v)
        elif isinstance(v, list):
            return [IdUser(id=id) for id in v]
        return v
    
    @field_validator("position", mode="before")
    def position_to_minimal_location(cls, v):
        if isinstance(v, list) and len(v) == 2:
            return MinimalLocation(x=v[0], z=v[1])
        return v
    
    @field_validator("started_at", mode="before")
    def timestamp_to_datetime(cls, v):
        return _validate_datetime(v)
    
class Log(BaseModel):
    timestamp: datetime.datetime
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @field_validator("timestamp", mode="before")
    def timestamp_to_datetime(cls, v):
        return _validate_datetime(v)
    
    @field_validator(
        "user", "killed", "killer", "caller", "moderator",
        check_fields=False,
        mode="before"
    )
    def user_to_full_user(cls, v):
        if isinstance(v, str) and v == "Remote Server":
            return FullUser(name=v, id=0)
        return FullUser.validate_full_user(v)

class JoinLog(Log):
    user: Annotated[FullUser, Field(alias="Player")]
    join: bool

class KillLog(Log):
    killed: FullUser
    killer: FullUser
    
class CommandLog(Log):
    user: Annotated[FullUser, Field(alias="Player")]
    command: str
    
class ModCall(Log):
    caller: FullUser
    moderator: FullUser
    
class Queue(BaseModel):
    players: list[IdUser]
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @property
    def length(self) -> int:
        return len(self.players)
    
    @field_validator("players", mode="before")
    def caller_to_id_user(cls, v):
        if isinstance(v, list):
            return [IdUser(id=id) for id in v]
        return v
    
class Staff(BaseModel):
    admins: list[FullUser]
    mods: list[FullUser]
    helpers: list[FullUser]
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @field_validator("admins", "mods", "helpers", mode="before")
    def validate_full_user(cls, v):
        if isinstance(v, dict):
            return [FullUser(name=name, id=int(id)) for id, name in v.items()]
        return v
    
class Player(BaseModel):
    team: str
    user: Annotated[FullUser, Field(alias="Player")]
    callsign: Annotated[str | None, Field(default=None)]
    location: Location
    permission: Literal["Normal", "Server Administrator", "Server Owner", "Server Moderator"]
    wanted_stars: int
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @field_validator("user", mode="before")
    def user_to_full_user(cls, v):
        return FullUser.validate_full_user(v)
    
    @field_validator("location", mode="before")
    def validate_location(cls, v):
        if isinstance(v, dict):
            return Location.model_validate(v)
        return v
    
    def __str__(self):
        return str(self.user)

class _ServerBase(BaseModel):
    name: str
    owner: Annotated[IdUser, Field(alias="OwnerId")]
    co_owners: Annotated[list[IdUser], Field(alias="CoOwnerIds")]
    current_players: int
    max_players: int
    join_key: str
    verification_required: Annotated[Literal["Disabled", "Email", "Phone/ID"], Field(alias="AccVerifiedReq")]
    team_balance: bool
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @field_validator("owner", "co_owners", mode="before")
    def owner_to_id_user(cls, v):
        if isinstance(v, int):
            return IdUser(id=v)
        elif isinstance(v, list):
            return [IdUser(id=id) for id in v]
        return v

class Server(_ServerBase):
    zzz_players: Annotated[list[dict] | None, Field(default=None, alias="Players")]
    zzz_staff: Annotated[dict | None, Field(default=None, alias="Staff")]
    zzz_join_logs: Annotated[list[dict] | None, Field(default=None, alias="JoinLogs")]
    zzz_queue: Annotated[list[int] | None, Field(default=None, alias="Queue")]
    zzz_kill_logs: Annotated[list[dict] | None, Field(default=None, alias="KillLogs")]
    zzz_command_logs: Annotated[list[dict] | None, Field(default=None, alias="CommandLogs")]
    zzz_mod_calls: Annotated[list[dict] | None, Field(default=None, alias="ModCalls")]
    zzz_emergency_calls: Annotated[list[dict] | None, Field(default=None, alias="EmergencyCalls")]
    zzz_vehicles: Annotated[list[dict] | None, Field(default=None, alias="Vehicles")]
    
    @property
    def players(self) -> list[Player]:
        if not self.zzz_players:
            raise DataNotRequestedError("Player data not requested.")
        return [Player.model_validate(player_dict) for player_dict in self.zzz_players]
    
    @property
    def staff(self) -> Staff:
        if not self.zzz_staff:
            raise DataNotRequestedError("Staff data not requested.")
        return Staff.model_validate(self.zzz_staff)
    
    @property
    def join_logs(self) -> list[JoinLog]:
        if not self.zzz_join_logs:
            raise DataNotRequestedError("Join log data not requested.")
        return [JoinLog.model_validate(log_dict) for log_dict in self.zzz_join_logs]
    
    @property
    def queue(self) -> Queue:
        if not self.zzz_queue:
            raise DataNotRequestedError("Queue data not requested.")
        return Queue.model_validate(self.zzz_queue)
    
    @property
    def kill_logs(self) -> list[KillLog]:
        if not self.zzz_kill_logs:
            raise DataNotRequestedError("Kill log data not requested.")
        return [KillLog.model_validate(log_dict) for log_dict in self.zzz_kill_logs]
    
    @property
    def command_logs(self) -> list[CommandLog]:
        if not self.zzz_command_logs:
            raise DataNotRequestedError("Command log data not requested.")
        return [CommandLog.model_validate(log_dict) for log_dict in self.zzz_command_logs]
    
    @property
    def mod_calls(self) -> list[ModCall]:
        if not self.zzz_mod_calls:
            raise DataNotRequestedError("Mod call data not requested.")
        return [ModCall.model_validate(mod_call_dict) for mod_call_dict in self.zzz_mod_calls]
    
    @property
    def emergency_calls(self) -> list[EmergencyCall]:
        if not self.zzz_emergency_calls:
            raise DataNotRequestedError("Emergency call data not requested.")
        return [EmergencyCall.model_validate(emergency_call_dict) for emergency_call_dict in self.zzz_emergency_calls]
    
    @property
    def vehicles(self) -> list[Vehicle]:
        if not self.zzz_vehicles:
            raise DataNotRequestedError("Vehicle data not requested.")
        return [Vehicle.model_validate(vehicle_dict) for vehicle_dict in self.zzz_vehicles]

class BundledServer(_ServerBase):
    players: list[Player]
    staff: Staff
    join_logs: list[JoinLog]
    queue: Queue
    kill_logs: list[KillLog]
    command_logs: list[CommandLog]
    mod_calls: list[ModCall]
    emergency_calls: list[EmergencyCall]
    vehicles: list[Vehicle]
    
    @field_validator("queue", mode="before")
    def queue_list_to_queue(cls, v):
        if isinstance(v, list):
            return Queue(players=v)
        return v