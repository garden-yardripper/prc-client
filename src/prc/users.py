from typing import TYPE_CHECKING
from dataclasses import dataclass
if TYPE_CHECKING:
    from .v2.models import Player as V2Player
    from .v1.models import Player as V1Player

type AnyUserType = "V2Player | V1Player | FullUser | UsernameUser | IdUser | str | int"
type UsernameUserType = "V2Player | V1Player | FullUser | UsernameUser | str"
type IdUserType = "V2Player | V1Player | FullUser | IdUser | int"
type StrictUserType = FullUser | UsernameUser | IdUser | str | int

@dataclass(frozen=True)
class UsernameUser:
    """Represents a user returned by the API with only a username.
    
    Attributes
    ----------
    name: `str`
        The user's username.
    """
    name: str
    
    def __str__(self) -> str:
        return self.name

@dataclass(frozen=True)
class IdUser:
    """Represents a user returned by the API with only an ID.
    
    Attributes
    ----------
    id: `int`
        The user's ID.
    """
    id: int
    
    def __int__(self) -> int:
        return self.id
    
    def __str__(self) -> str:
        return str(self.id)

@dataclass(frozen=True)
class FullUser:
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
    
    @classmethod
    def from_delimited(cls, delimited: str):
        name, id = delimited.split(":", maxsplit=1)
        return cls(name=name, id=int(id))
    
    def __str__(self) -> str:
        return f"{self.name}:{self.id}"
    
    def __int__(self) -> int:
        return self.id