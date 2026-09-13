from typing import Any, Callable

from ..v2.client import AsyncClient, Client
from .models import Context
from .router import Router

type _EventHandler[T: (Client, AsyncClient)] = Callable[[Context[T]], Any]
type _EventDecorator[T: (Client, AsyncClient)] = Callable[[_EventHandler[T]], _EventHandler[T]]

class _On[T: (Client, AsyncClient)]:
    def __init__(self, router: Router) -> None:
        self.router = router
        
    def command(self, command: str, *commands: str) -> _EventDecorator[T]:
        """Register a function to be called when a specific command is run in-game."""
        def wrapper(func: _EventHandler[T]) -> _EventHandler[T]:
            self.router._add_command(func, command)
            for cmd in commands:
                self.router._add_command(func, cmd)
            return func
        return wrapper
    
    def any_custom_command(self) -> _EventDecorator[T]:
        """Register a function to be called when any custom command is run in-game."""
        def wrapper(func: _EventHandler[T]) -> _EventHandler[T]:
            self.router._add_command(func, None)
            return func
        return wrapper
    
    def custom_event(self, event_name: str, *event_names: str) -> _EventDecorator[T]:
        """Register a function to be called when a custom event with the specified name is received."""
        def wrapper(func: _EventHandler[T]) -> _EventHandler[T]:
            self.router._add_function(func, event_name)
            for name in event_names:
                self.router._add_function(func, name)
            return func
        return wrapper
    
    def emergency_start(self) -> _EventDecorator[T]:
        """Register a function to be called when an emergency call is made in-game."""
        def wrapper(func: _EventHandler[T]) -> _EventHandler[T]:
            self.router._add_function(func, "EmergencyCallStarted")
            return func
        return wrapper
    
    def probe(self) -> _EventDecorator[T]:
        """Register a function to be called when a webhook ping is received from the PRC API.
        
        These are occasionally sent by the API to test the validity of the webhook URL and its signature verification.
        """
        def wrapper(func: _EventHandler[T]) -> _EventHandler[T]:
            self.router._add_function(func, "WebhookProbe")
            return func
        return wrapper
    
    def any_event(self) -> _EventDecorator[T]:
        """Register a function to be called when any non-command event is received."""
        def wrapper(func: _EventHandler[T]) -> _EventHandler[T]:
            self.router._add_function(func, None)
            return func
        return wrapper
