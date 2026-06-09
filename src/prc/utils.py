import asyncio
from typing import Any, Coroutine

def execute_async[T](coro: Coroutine[Any, Any, T]) -> T:
    """Execute an asynchronous coroutine in a synchronous context.
    If called from an existing event loop, it will raise a `RuntimeError`."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    raise RuntimeError((
        "execute_async() cannot be called from a running event loop; "
        "use 'await' instead."
    ))