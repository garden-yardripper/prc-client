from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .router import Router

class _On:
    def __init__(self, router: "Router") -> None:
        self.router = router
        
    def command(self, command: str):
        """Register a function to be called when a specific command is run in-game."""
        def wrapper(func):
            self.router.add_command(func, command)
            return func
        return wrapper
    
    def any_custom_command(self):
        """Register a function to be called when any custom command is run in-game."""
        def wrapper(func):
            self.router.add_command(func, None)
            return func
        return wrapper
    
    def custom_event(self, event_name: str):
        """Register a function to be called when a custom event with the specified name is received."""
        def wrapper(func):
            self.router.add_function(func, event_name)
            return func
        return wrapper
    
    def emergency_start(self):
        """Register a function to be called when an emergency call is made in-game."""
        def wrapper(func):
            self.router.add_function(func, "EmergencyCallStarted")
            return func
        return wrapper
    
    def probe(self):
        """Register a function to be called when a webhook ping is received from the PRC API.
        
        These are occasionally sent by the API to test the validity of the webhook URL and its signature verification.
        """
        def wrapper(func):
            self.router.add_function(func, "WebhookProbe")
            return func
        return wrapper