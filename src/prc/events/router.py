from typing import Callable, Literal

ANY_COMMAND = object()

class Router:
    def __init__(self) -> None:
        self.handlers: dict[str, list[Callable]] = {}
        self.commands: dict[str | object, list[Callable]]
        
    def add_function(self,
        func: Callable,
        event_type: Literal["EmergencyCallStarted", "WebhookProbe"] | str
    ):
        self.handlers.setdefault(event_type, []).append(func)
        
    def add_command(self, func: Callable, name: str | None):
        if name:
            self.commands.setdefault(name, []).append(func)
        self.commands.setdefault(ANY_COMMAND, []).append(func)