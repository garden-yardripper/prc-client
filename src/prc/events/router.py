from typing import Callable, Literal
from itertools import chain
import asyncio

from .decorators import _On
from .models import EventBatch
from ..utils import maybe_coro

ANY_COMMAND = object()

class Router:
    def __init__(self) -> None:
        self.handlers: dict[str, list[Callable]] = {}
        self.commands: dict[str | object, list[Callable]] = {}
        
        self.on = _On(self)
        
    def add_function(self,
        func: Callable,
        event_type: Literal["EmergencyCallStarted", "WebhookProbe"] | str
    ):
        self.handlers.setdefault(event_type, []).append(func)
        
    def add_command(self, func: Callable, name: str | None):
        if name:
            self.commands.setdefault(name, []).append(func)
        else:
            self.commands.setdefault(ANY_COMMAND, []).append(func)
    
    async def dispatch_async(self, events: list[EventBatch]):
        for batch in events:
            for e in batch.events:
                event_type = e.event_type
                if event_type == "CustomCommand":
                    # run command handlers
                    command_name = e.command.command
                    for func in chain(self.commands.get(command_name, []), self.commands.get(ANY_COMMAND, [])):
                        await maybe_coro(func, e)
            
                # run other event handlers
                if event_type in self.handlers:
                    for func in self.handlers[event_type]:
                        await maybe_coro(func, e)

    def dispatch(self, events):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            # disallow calling dispatch from an async context,
            # force users to use dispatch_async to avoid accidentally blocking the event loop
            raise RuntimeError(
                "dispatch() cannot be called from an async context. "
                "Use await dispatch_async()."
            )

        asyncio.run(self.dispatch_async(events))