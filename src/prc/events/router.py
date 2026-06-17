import logging
import asyncio
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
from ..base_client import ClientType
from .decorators import _On
from .models import EventBatch

if TYPE_CHECKING:
    from fastapi import Request as FastRequest, BackgroundTasks as FastBackgroundTasks
    from quart import Quart
    from starlette.requests import Request as StarletteRequest
    from starlette.background import BackgroundTask as StarletteBackgroundTask

ANY_COMMAND = object()
ANY_EVENT = object()

logger = logging.getLogger(__name__)

class Router:
    def __init__(self, client: ClientType, *, sync_handlers_to_thread: bool = True) -> None:
        """Initialize a new `Router` instance to handle event routing and request verification.
        
        Use the `router.on` decorators to register event handlers.
        
        Routers allow you to register both sync and async handlers,
        and the library will take care of running them in the appropriate context.
        
        All handlers must take in a context parameter which contains information about the event
        and helper methods for replying to the event, like so:
        
        ```python
        @router.on.command("mycommand")
        async def handle_my_command(ctx: Context[prc.v2.AsyncClient]):
            # handle ;mycommand, and use ctx to reply or get info about the event
            # you can optionally specify the client type in the context for better type hints
        ```
        
        Context objects will have an injected `client` attribute
        which is the client instance associated with this router.
        
        Please note that you are responsible for creating an endpoint for the game to use 
        with a (preferrably) ASGI API framework of choosing 
            ([FastAPI](https://fastapi.tiangolo.com/),
            [Starlette](https://www.starlette.dev/),
            [Quart](https://quart.palletsprojects.com/en/latest/),
        etc.).
        This is to ensure compatability with any service that works best for your application's needs.
        
        Arguments
        ----------
        client: `ClientType`
            The client instance to associate with this router.
            This client will be accessible in event contexts.
        sync_handlers_to_thread: `bool` (optional)
            Whether to run synchronous handlers in a separate thread.
            Setting to `False` will cause synchronous handlers to block the event loop.
            Defaults to `True`.
        """
        
        # prevent circular import
        from .integrations import _FastApiIntegration, _QuartIntegration, _StarletteIntegration
        
        self.client = client
        self.sync_handlers_to_thread = sync_handlers_to_thread
        self._handlers: dict[str | object, list[Callable]] = {}
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
        event_type: Literal["EmergencyCallStarted", "WebhookProbe"] | str | None
    ):
        if event_type:
            logger.debug("Registering handler '%s' for event type '%s'.", func.__name__, event_type)
            self._handlers.setdefault(event_type, []).append(func)
        else:
            logger.debug("Registering handler '%s' for any event type.", func.__name__)
            self._handlers.setdefault(ANY_EVENT, []).append(func)
        
    def _add_command(self, func: Callable, name: str | None):
        if name:
            logger.debug("Registering handler '%s' for command '%s'.", func.__name__, name)
            self._commands.setdefault(name, []).append(func)
        else:
            logger.debug("Registering handler '%s' for any command.", func.__name__)
            self._commands.setdefault(ANY_COMMAND, []).append(func)
    
    def _decode_verified_body(self, raw_body: bytes) -> EventBatch:
        logger.debug("Decoding verified request body and injecting client.")
        batch = EventBatch.model_validate_json(raw_body)
        for event in batch.events:
            event._client = self.client
            event._b64_server = batch.server
        return batch
    
    def _verify_signature(self, raw_body: bytes, sighex: str, timestamp: str) -> bool:
        if not isinstance(self._public_key, Ed25519PublicKey):
            logger.error("Invalid public key type. Expected Ed25519PublicKey, got %s.", type(self._public_key))
            return False
        
        message = timestamp.encode() + raw_body
        sighex_bytes = binascii.unhexlify(sighex)
        
        try:
            logger.info("Request signature is VALID.")
            self._public_key.verify(sighex_bytes, message)
            return True
        except InvalidSignature:
            logger.info("Request signature is INVALID.")
            return False 
            
    def _verify_prc_request(self, raw_body: bytes, headers: dict):
        logger.debug("Verifying incoming PRC request signature.")
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        sighex = normalized_headers.get("x-signature-ed25519")
        timestamp = normalized_headers.get("x-signature-timestamp")
        
        if not sighex or not timestamp:
            logger.info("Missing signature headers in the request.")
            raise MissingSignatureError
        
        valid = self._verify_signature(raw_body, sighex, timestamp)
        if not valid:
            logger.info("Invalid signature for incoming request.")
            raise InvalidSignatureError   
    
    async def _dispatch_async(self, batch: EventBatch):
        logger.info("Dispatching event batch with %d events.", len(batch.events))
        for e in batch.events:
            event_type = e.event_type
            
            command_funcs = []
            if e.event_type == "CustomCommand":
                # collect command handlers
                command_funcs = list(chain(
                    self._commands.get(e.command.command, []),
                    self._commands.get(ANY_COMMAND, [])
                ))
            
            # collect other event handlers
            handler_funcs = []
            if event_type in self._handlers:
                handler_funcs = list(chain(
                    self._handlers.get(event_type, []),
                    self._handlers.get(ANY_EVENT, [])
                ))
            
            funcs = command_funcs + handler_funcs
            if not funcs:
                continue
            
            logger.info("Dispatching event of type '%s' to %d handlers.", event_type, len(funcs))
            coros = [
                maybe_coro(func, e, sync_to_thread=self.sync_handlers_to_thread)
                for func in funcs
            ]
            results = await asyncio.gather(*coros, return_exceptions=True)
            
            excs = [res for res in results if isinstance(res, Exception)]
            if excs:
                logger.error("One or more handlers raised exceptions during dispatch.")
                raise ExceptionGroup("One or more command/event handlers raised exceptions.", excs)
                    
    async def prepare_request(self, raw_body: bytes, headers: dict) -> tuple[Literal[200, 400], Callable | None]:
        """Verify an incoming request and prepare for dispatching if the signature is valid.
        
        This method will verify the request signature return the appropriate HTTP status code
        and dispatch job if the signature is valid.
        
        It is recommended to use the provided integration methods for FastAPI, Quart, or Starlette
        instead of calling this method directly, as they will handle the background task scheduling for you.
        
        Arguments
        ---------
        raw_body: `bytes`
            The raw body of the incoming request. **IMPORTANT:** This must be the raw body as bytes
            exactly as received by the API. Ensure that your framework doesn't attempt to parse or decode the body
            before passing it to this method.
        headers: `dict`
            The **full** headers of the incoming request.
        
        Returns
        -------
        `tuple[Literal[200, 400], Callable | None]`
            A tuple containing the appropriate HTTP status code and the dispatch job if the signature is valid,
            or `None` if the signature is invalid.
        """
        logger.info("Preparing incoming request for dispatch.")
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
        """Handle an incoming FastAPI request containing a PRC event batch.
        
        This method will automatically handle signature verification and event dispatching,
        adding dispatching to background tasks, and immediately returning the appropriate HTTP status code.
        
        Arguments
        ---------
        request: `fastapi.Request`
            The incoming FastAPI request object.
        background_tasks: `fastapi.BackgroundTasks`
            The FastAPI `BackgroundTasks` instance to use for scheduling event handler execution.
        
        Returns
        -------
        `Literal[200, 400]`
            The appropriate HTTP status code to return to the PRC server (200 for success, 400 for invalid signature).
        """
        logger.debug("Handling incoming FastAPI request for event batch.")
        return await self._fastapi.handle_fastapi_request(request, background_tasks)
    
    async def handle_quart_request(self, app: "Quart") -> Literal[200, 400]:
        """Handle an incoming Quart request containing a PRC event batch.
        
        This method will automatically handle signature verification and event dispatching,
        adding dispatching to background tasks, and immediately returning the appropriate HTTP status code.
        
        Arguments
        ---------
        app: `quart.Quart`
            The Quart app instance to use for scheduling event handler execution.
        
        Returns
        -------
        `Literal[200, 400]`
            The appropriate HTTP status code to return to the PRC server (200 for success, 400 for invalid signature).
        """
        logger.debug("Handling incoming Quart request for event batch.")
        return await self._quart.handle_quart_request(app)
    
    async def handle_starlette_request(
        self, request: "StarletteRequest"
    ) -> tuple[Literal[200, 400], "StarletteBackgroundTask | None"]:
        """Handle an incoming Starlette request containing a PRC event batch.
        
        This method will automatically handle signature verification and event dispatching,
        creating the BackgroundTask instance and returning the appropriate HTTP status code.
        
        Arguments
        ---------
        request: `starlette.requests.Request`
            The incoming Starlette request object.
        
        Returns
        -------
        `tuple[Literal[200, 400], starlette.background.BackgroundTask | None]`
            A tuple containing the appropriate HTTP status code to return to the PRC server
            (200 for success, 400 for invalid signature)
            and the Starlette `BackgroundTask` instance to add to the `Response` for dispatching
            if the signature is valid, or `None` if the signature is invalid.
        """
        logger.debug("Handling incoming Starlette request for event batch.")
        return await self._starlette.handle_starlette_request(request)