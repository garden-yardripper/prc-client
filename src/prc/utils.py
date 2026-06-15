import asyncio
import inspect
from typing import Awaitable, Callable

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

async def maybe_coro[T](
    func: Callable[..., T] | Awaitable[T] | Callable[..., Awaitable[T]],
    *args,
    sync_to_thread: bool = True,
    **kwargs,
) -> T:
    """A utility to call `func` with the given arguments and await the result if needed,
    await `func` itself if it is a coroutine, or run the function in a separate thread if it is not a coroutine.
    
    This is useful for calling functions that may or may not be coroutines.
    
    Arguments
    ---------
    func: `Callable` | `Awaitable`
        The function to call.
    *args
        Positional arguments to pass to `func`.
    **kwargs
        Keyword arguments passed to `func`.
        
    Returns
    -------
    `Any`
        The result of `func`, awaited if it is awaitable.
    """
    if inspect.isawaitable(func):
        return await func
    
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    
    if callable(func):
        if sync_to_thread:
            result = await asyncio.to_thread(func, *args, **kwargs)
        else:
            result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result
    
    raise TypeError("maybe_coro expects a callable or an awaitable")