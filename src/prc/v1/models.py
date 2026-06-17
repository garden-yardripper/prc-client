import datetime
from enum import StrEnum
from typing import Annotated, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_pascal
from ..users import FullUser, UsernameUser, IdUser

class Endpoint(StrEnum):
    server = "/v1/server"
    players = "/v1/server/players"
    staff = "/v1/server/staff"
    join_logs = "/v1/server/joinlogs"
    queue = "/v1/server/queue"
    kill_logs = "/v1/server/killlogs"
    command_logs = "/v1/server/commandlogs"
    mod_calls = "/v1/server/modcalls"
    bans = "/v1/server/bans"
    vehicles = "/v1/server/vehicles"
    command = "/v1/server/command"

class Vehicle(BaseModel):
    """Represents an in-game vehicle.
    
    Attributes
    ----------
    name: `str`
        The vehicle's name.
    owner: `UsernameUser`
        The vehicle's owner.
    texture: `str`
        The vehicle's texture.
    """
    name: str
    owner: UsernameUser
    texture: str
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)

    @field_validator("owner", mode="before")
    def owner_to_username_user(cls, v):
        if isinstance(v, str):
            return UsernameUser(name=v)
        return v
    
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
    co_owners: `list[IdUser]`
        The server co-owners.
    """
    admins: list[FullUser]
    mods: list[FullUser]
    co_owners: list[IdUser]
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @field_validator("admins", "mods", mode="before")
    def validate_full_user(cls, v):
        if isinstance(v, dict):
            return [FullUser(name=name, id=int(id)) for id, name in v.items()]
        return v
    
    @field_validator("co_owners", mode="before")
    def co_owners_to_id_users(cls, v):
        if isinstance(v, list):
            return [IdUser(id=id) for id in v]
        return v
    
class Bans(BaseModel):
    """Represents the server's bans.

    Attributes
    ----------
    users: `list[FullUser]`
        The banned users.
    """
    users: list[FullUser]
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @field_validator("users", mode="before")
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
    permission: `Literal["Normal", "Server Administrator", "Server Owner", "Server Moderator"]`
        The player's permission level.
    """
    team: str
    user: Annotated[FullUser, Field(alias="Player")]
    callsign: Annotated[str | None, Field(default=None)]
    permission: Literal["Normal", "Server Administrator", "Server Owner", "Server Moderator"]
    
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True, frozen=True)
    
    @field_validator("user", mode="before")
    def user_to_full_user(cls, v):
        return FullUser.from_delimited(v)
    
    def __str__(self):
        return str(self.user)

class Server(BaseModel):
    """Represents an ER:LC private server.
    
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
        The server's join key.
    verification_required: `Literal["Disabled", "Email", "Phone/ID"]`
        The server's account verification requirement.
    team_balance: `bool`
        Whether team balance is enabled on the server.
    """
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