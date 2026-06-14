from dataclasses import dataclass

@dataclass(frozen=True)
class UsernameUser:
    """Represents a user returned by the API with only a username.
    
    Attributes
    ----------
    name: `str`
        The user's username.
    """
    name: str
    
    def __str__(self):
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
    
    def __int__(self):
        return self.id
    
    def __str__(self):
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
    
    def __str__(self):
        return f"{self.name}:{self.id}"
    
    def __int__(self):
        return int(self.id)