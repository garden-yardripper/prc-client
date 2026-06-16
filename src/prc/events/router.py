import base64
import binascii
from itertools import chain
from typing import Callable, Literal, TYPE_CHECKING

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except ImportError:
    raise RuntimeError((
        "PRC event webhook support requires the `cryptography` library. "
        "Install the dependency with `pip install prc-client[events]`."
    ))

from ..exceptions import InvalidSignatureError, MissingSignatureError
from ..utils import maybe_coro
from ..v2.client import ClientType
from .decorators import _On
from .models import EventBatch

if TYPE_CHECKING:
    from fastapi import Request as FastRequest, BackgroundTasks as FastBackgroundTasks
    from quart import Quart
    from starlette.requests import Request as StarletteRequest
    from starlette.background import BackgroundTask as StarletteBackgroundTask

ANY_COMMAND = object()

class Router:
    def __init__(self, client: ClientType, *, sync_handlers_to_thread: bool = True) -> None:
        """Initialize a new `Router` instance.
        
        Use the `router.on` decorators to register event handlers.
        
        Arguments
        ----------
        sync_handlers_to_thread: `bool` (optional)
            Whether to run synchronous handlers in a separate thread.
            Setting to `False` will cause synchronous handlers to block the event loop.
            Defaults to `True`.
        """
        # prevent circular import
        from .integrations import _FastApiIntegration, _QuartIntegration, _StarletteIntegration
        
        self.client = client
        self.sync_handlers_to_thread = sync_handlers_to_thread
        self._handlers: dict[str, list[Callable]] = {}
        self._commands: dict[str | object, list[Callable]] = {}
        
        _raw_public_key = "MCowBQYDK2VwAyEAjSICb9pp0kHizGQtdG8ySWsDChfGqi+gyFCttigBNOA="
        _public_key_bytes = base64.b64decode(_raw_public_key)
        self._public_key = serialization.load_der_public_key(_public_key_bytes)
        
        self.on = _On(self)
        
        self._fastapi = _FastApiIntegration(self)
        self._quart = _QuartIntegration(self)
        self._starlette = _StarletteIntegration(self)
    
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
    
    def _decode_verified_body(self, raw_body: bytes) -> EventBatch:
        batch = EventBatch.model_validate_json(raw_body)
        for event in batch.events:
            event.client = self.client
            event.b64_server = batch.server
        return batch
    
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
            
    def _verify_prc_request(self, raw_body: bytes, headers: dict):
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        sighex = normalized_headers.get("x-signature-ed25519")
        timestamp = normalized_headers.get("x-signature-timestamp")
        
        if not sighex or not timestamp:
            raise MissingSignatureError
        
        valid = self._verify_signature(raw_body, sighex, timestamp)
        if not valid:
            raise InvalidSignatureError   
    
    async def _dispatch_async(self, batch: EventBatch):
        for e in batch.events:
            event_type = e.event_type
            if event_type == "CustomCommand":
                # run command handlers
                command_name = e.command.command
                for func in chain(
                    self._commands.get(command_name, []),
                    self._commands.get(ANY_COMMAND, [])
                ):
                    await maybe_coro(func, e, sync_to_thread=self.sync_handlers_to_thread)
        
            # run other event handlers
            if event_type in self._handlers:
                for func in self._handlers[event_type]:
                    await maybe_coro(func, e, sync_to_thread=self.sync_handlers_to_thread)
                    
    async def prepare_request(self, raw_body: bytes, headers: dict) -> tuple[Literal[200, 400], Callable | None]:
        try:
            self._verify_prc_request(raw_body, headers)
            status = 200
        except (MissingSignatureError, InvalidSignatureError):
            status = 400
        
        if status == 400:
            return 400, None
        
        batch = self._decode_verified_body(raw_body)
        async def dispatch():
            await self._dispatch_async(batch)
            
        return 200, dispatch
    
    async def handle_fastapi_request(self,
        request: "FastRequest",
        background_tasks: "FastBackgroundTasks"
    ) -> Literal[200, 400]:
        return await self._fastapi.handle_fastapi_request(request, background_tasks)
    
    async def handle_quart_request(self, app: "Quart") -> Literal[200, 400]:
        return await self._quart.handle_quart_request(app)
    
    async def handle_starlette_request(
        self, request: "StarletteRequest"
    ) -> tuple[Literal[200, 400], "StarletteBackgroundTask | None"]:
        return await self._starlette.handle_starlette_request(request)