from prc.v2.models import Location, Player, EmergencyCall
import math

def get_distance_between_locations(
    location1: Location | Player | EmergencyCall,
    location2: Location | Player | EmergencyCall
) -> float:
    if isinstance(location1, Player):
        position1 = location1.location.position
    elif isinstance(location1, EmergencyCall):
        position1 = location1.position.position
    else:
        position1 = location1.position
        
    if isinstance(location2, Player):
        position2 = location2.location.position
    elif isinstance(location2, EmergencyCall):
        position2 = location2.position.position
    else:
        position2 = location2.position
    
    return math.dist(position1, position2)