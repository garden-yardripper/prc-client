import asyncio
import base64
import binascii
from itertools import chain
from typing import Callable, Literal

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from ..utils import maybe_coro
from .decorators import _On
from .models import EventBatch

ANY_COMMAND = object()

class Router:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}
        self._commands: dict[str | object, list[Callable]] = {}
        
        _raw_public_key = "MCowBQYDK2VwAyEAjSICb9pp0kHizGQtdG8ySWsDChfGqi+gyFCttigBNOA="
        _public_key_bytes = base64.b64decode(_raw_public_key)
        self._public_key = serialization.load_der_public_key(_public_key_bytes)
        
        self.on = _On(self)
    
    def _verify_signature(self, raw_body: bytes, sighex: str, timestamp: str) -> bool:
        if not isinstance(self._public_key, Ed25519PublicKey):
            return False
        
        message = timestamp.encode() + raw_body
        sighex_bytes = binascii.unhexlify(sighex)
        
        try:
            self._public_key.verify(sighex_bytes, message)
            return True
        except InvalidSignature:
            return False    
    
    def _add_function(self,
        func: Callable,
        event_type: Literal["EmergencyCallStarted", "WebhookProbe"] | str
    ):
        self._handlers.setdefault(event_type, []).append(func)
        
    def _add_command(self, func: Callable, name: str | None):
        if name:
            self._commands.setdefault(name, []).append(func)
        else:
            self._commands.setdefault(ANY_COMMAND, []).append(func)
    
    async def _dispatch_async(self, events: list[EventBatch]):
        for batch in events:
            for e in batch.events:
                event_type = e.event_type
                if event_type == "CustomCommand":
                    # run command handlers
                    command_name = e.command.command
                    for func in chain(self._commands.get(command_name, []), self._commands.get(ANY_COMMAND, [])):
                        await maybe_coro(func, e)
            
                # run other event handlers
                if event_type in self._handlers:
                    for func in self._handlers[event_type]:
                        await maybe_coro(func, e)

    def _dispatch(self, events):
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

        asyncio.run(self._dispatch_async(events))