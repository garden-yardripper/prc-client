import asyncio
from typing import Any, Coroutine

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

def run_coroutine[T](coroutine: Coroutine[Any, Any, T]) -> T | asyncio.Task[T]:
    """Execute a coroutine by scheduling the coroutine as a task if an event loop is already running, or
    creating a new event loop and executing the coroutine until completion.
    
    This is useful when you need to execute a coroutine from contexts where
    the event loop state is uncertain (for example, in async and/or sync code paths).
    
    Arguments
    ---------
    coroutine: `Coroutine`
        The coroutine object to execute.
    
    Returns
    -------
    `asyncio.Task` | `Any`
        The `asyncio.Task` object if a running loop exists (task is scheduled but
        not awaited here), otherwise the coroutine's result when executed via
        `asyncio.run`.
    """
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return asyncio.create_task(coroutine)
    else:
        return asyncio.run(coroutine)