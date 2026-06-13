from .v2.models import Location, MinimalLocation, Player, EmergencyCall
import math

type PositionLike = Location | MinimalLocation | Player | EmergencyCall | tuple[int | float, int | float]

def get_distance_between_locations(
    location1: PositionLike,
    location2: PositionLike
) -> float:
    """Get the Euclidean distance between two locations as a float.
    
    Parameters
    ----------
    location1: `PositionLike`
        The first location.
    location2: `PositionLike`
        The second location.
    """
    if isinstance(location1, Player):
        position1 = location1.location.position
    elif isinstance(location1, EmergencyCall):
        position1 = location1.position.position
    elif isinstance(location1, tuple):
        position1 = location1
    else:
        position1 = location1.position
        
    if isinstance(location2, Player):
        position2 = location2.location.position
    elif isinstance(location2, EmergencyCall):
        position2 = location2.position.position
    elif isinstance(location2, tuple):
        position2 = location2
    else:
        position2 = location2.position
    
    return math.dist(position1, position2)