import datetime
from typing import Annotated, Literal
from pydantic import AliasChoices, AliasGenerator, BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_pascal, to_camel
from ..exceptions import DataNotRequestedError
from ..users import FullUser, UsernameUser, IdUser
from ..logs import JoinLog, KillLog, CommandLog, ModCall

class MinimalLocation(BaseModel):
    """Represents a location with minimal information.
    
    Attributes
    ----------
    x: `float`
        The location's X coordinate.
    z: `float`
        The location's Z coordinate.
    """
    x: Annotated[float, Field(alias="LocationX")]
    z: Annotated[float, Field(alias="LocationZ")]
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @property
    def position(self) -> tuple[float, float]:
        """Returns the (x, z) position as a tuple."""
        return self.x, self.z

class Location(MinimalLocation):
    """Represents a location with full information.
    
    Attributes
    ----------
    x: `float`
        The location's X coordinate.
    z: `float`
        The location's Z coordinate.
    postal_code: `int`
        The location's postal code.
    street_name: `str`
        The location's street name.
    building_number: `int`
        The location's building number.
    """
    postal_code: int
    street_name: str
    building_number: int

class Vehicle(BaseModel):
    """Represents an in-game vehicle.
    
    Attributes
    ----------
    name: `str`
        The vehicle's name.
    owner: `UsernameUser`
        The vehicle's owner.
    plate: `str`
        The vehicle's license plate.
    texture: `str`
        The vehicle's texture.
    color_hex: `str`
        The vehicle's color in hexadecimal format.
    color_name: `str`
        The vehicle's color name.
    """
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
    """Represents an in-game emergency call.
    
    Attributes
    ----------
    team: `str`
        The team that received the call.
    caller: `IdUser`
        The user who made the call.
    players: `list[IdUser]`
        The users involved in the call.
    position: `MinimalLocation`
        The location of the call.
    started_at: `datetime.datetime`
        The time the call was started.
    call_number: `int`
        The number of the call.
    description: `str`
        The call's description.
    position_descriptor: `str`
        The call's description of the location.
    """
    team: str
    caller: IdUser
    players: list[IdUser]
    position: MinimalLocation
    started_at: datetime.datetime
    call_number: int
    description: str
    position_descriptor: str
    
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=lambda f_name: AliasChoices(
                to_pascal(f_name), to_camel(f_name)
            )
        ),
        populate_by_name=True,
        frozen=True
    )
    
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
            return MinimalLocation(LocationX=v[0], LocationZ=v[1])
        return v
    
    @field_validator("started_at", mode="before")
    def timestamp_to_datetime(cls, v):
        if isinstance(v, int):
            return datetime.datetime.fromtimestamp(v)
        return v
    
class Queue(BaseModel):
    """Represents a queue of players.
    
    Attributes
    ----------
    players: `list[IdUser]`
        The players in the queue.
    """
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
    """Represents the server's staff members.

    Attributes
    ----------
    admins: `list[FullUser]`
        The server administrators.
    mods: `list[FullUser]`
        The server moderators.
    helpers: `list[FullUser]`
        The server helpers.
    """
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
    """Represents an in-game player.

    Attributes
    ----------
    team: `str`
        The team the player is on.
    user: `FullUser`
        The player's `User` object.
    callsign: `str | None`
        The player's callsign if on a non-civilian team.
    location: `Location`
        The player's current location.
    permission: `Literal["Normal", "Server Administrator", "Server Owner", "Server Moderator"]`
        The player's permission level.
    wanted_stars: `int`
        The number of wanted stars the player has.
    """
    team: str
    user: Annotated[FullUser, Field(alias="Player")]
    callsign: Annotated[str | None, Field(default=None)]
    location: Location
    permission: Literal["Normal", "Server Administrator", "Server Owner", "Server Moderator"]
    wanted_stars: float
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @field_validator("user", mode="before")
    def user_to_full_user(cls, v):
        return FullUser.from_delimited(v)
    
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
    """Represents a customized server.
    
    Properties will raise a `DataNotRequestedError`
    if the corresponding data has not been requested in the initial request.
    
    Attributes
    ----------
    name: `str`
        The name of the server.
    owner: `IdUser`
        The owner of the server.
    co_owners: `list[IdUser]`
        The co-owners of the server.
    current_players: `int`
        The number of players currently on the server.
    max_players: `int`
        The maximum number of players that can be on the server.
    join_key: `str`
        The server's join code.
    verification_required: `Literal["Disabled", "Email", "Phone/ID"]`
        The type of verification required to join the server.
    team_balance: `bool`
        Whether or not the server enforces team balance.
    
    players: `list[Player]`
        The players currently on the server.
    staff: `Staff`
        The staff members of the server.
    join_logs: `list[JoinLog]`
        The server's recent join/leave logs.
    queue: `Queue`
        The queue of players waiting to join the server.
    kill_logs: `list[KillLog]`
        The server's recent kill logs.
    command_logs: `list[CommandLog]`
        The server's recent command logs.
    mod_calls: `list[ModCall]`
        The server's recent moderation calls.
    emergency_calls: `list[EmergencyCall]`
        The server's recent emergency calls.
    vehicles: `list[Vehicle]`
        The spawned vehicles on the server.
    """
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
        if self.zzz_players is None:
            raise DataNotRequestedError("Player data not requested.")
        return [Player.model_validate(player_dict) for player_dict in self.zzz_players]
    
    @property
    def staff(self) -> Staff:
        if self.zzz_staff is None:
            raise DataNotRequestedError("Staff data not requested.")
        return Staff.model_validate(self.zzz_staff)
    
    @property
    def join_logs(self) -> list[JoinLog]:
        if self.zzz_join_logs is None:
            raise DataNotRequestedError("Join log data not requested.")
        return [JoinLog.model_validate(log_dict) for log_dict in self.zzz_join_logs]
    
    @property
    def queue(self) -> Queue:
        if self.zzz_queue is None:
            raise DataNotRequestedError("Queue data not requested.")
        return Queue.model_validate(self.zzz_queue)
    
    @property
    def kill_logs(self) -> list[KillLog]:
        if self.zzz_kill_logs is None:
            raise DataNotRequestedError("Kill log data not requested.")
        return [KillLog.model_validate(log_dict) for log_dict in self.zzz_kill_logs]
    
    @property
    def command_logs(self) -> list[CommandLog]:
        if self.zzz_command_logs is None:
            raise DataNotRequestedError("Command log data not requested.")
        return [CommandLog.model_validate(log_dict) for log_dict in self.zzz_command_logs]
    
    @property
    def mod_calls(self) -> list[ModCall]:
        if self.zzz_mod_calls is None:
            raise DataNotRequestedError("Mod call data not requested.")
        return [ModCall.model_validate(mod_call_dict) for mod_call_dict in self.zzz_mod_calls]
    
    @property
    def emergency_calls(self) -> list[EmergencyCall]:
        if self.zzz_emergency_calls is None:
            raise DataNotRequestedError("Emergency call data not requested.")
        return [EmergencyCall.model_validate(emergency_call_dict) for emergency_call_dict in self.zzz_emergency_calls]
    
    @property
    def vehicles(self) -> list[Vehicle]:
        if self.zzz_vehicles is None:
            raise DataNotRequestedError("Vehicle data not requested.")
        return [Vehicle.model_validate(vehicle_dict) for vehicle_dict in self.zzz_vehicles]

class BundledServer(_ServerBase):
    """Represents a server with all available data bundled.
    
    Attributes
    ----------
    name: `str`
        The name of the server.
    owner: `IdUser`
        The owner of the server.
    co_owners: `list[IdUser]`
        The co-owners of the server.
    current_players: `int`
        The number of players currently on the server.
    max_players: `int`
        The maximum number of players that can be on the server.
    join_key: `str`
        The server's join code.
    verification_required: `Literal["Disabled", "Email", "Phone/ID"]`
        The type of verification required to join the server.
    team_balance: `bool`
        Whether or not the server enforces team balance.

    players: `list[Player]`
        The players currently on the server.
    staff: `Staff`
        The staff members of the server.
    join_logs: `list[JoinLog]`
        The server's recent join/leave logs.
    queue: `Queue`
        The queue of players waiting to join the server.
    kill_logs: `list[KillLog]`
        The server's recent kill logs.
    command_logs: `list[CommandLog]`
        The server's recent command logs.
    mod_calls: `list[ModCall]`
        The server's recent moderation calls.
    emergency_calls: `list[EmergencyCall]`
        The server's recent emergency calls.
    vehicles: `list[Vehicle]`
        The spawned vehicles on the server.
    """
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