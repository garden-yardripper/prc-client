import logging
from httpx import Response
from .models import Endpoint
from ..base_client import _BaseApiClient
from ..command import CommandLike, normalize_command

logger = logging.getLogger(__name__)

class _SendCommand(_BaseApiClient):
    async def _send_command_async(self, command: CommandLike) -> Response:
        cmd = command if isinstance(command, str) else command.text
        logger.info("Sending command: '%s'", cmd)
        
        return await self._send_async_request(
            endpoint=Endpoint.command,
            json={"command": normalize_command(cmd)}
        )
        
    def _send_command_sync(self, command: CommandLike) -> Response:
        cmd = command if isinstance(command, str) else command.text 
        logger.info("Sending command: '%s'", cmd)
        
        return self._send_sync_request(
            endpoint=Endpoint.command,
            json={"command": normalize_command(cmd)}
        )