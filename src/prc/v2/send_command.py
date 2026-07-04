import logging
from typing import TYPE_CHECKING
from httpx import Response
from ..base_client import _BaseApiClient, _Endpoint

if TYPE_CHECKING:
    from ..command import CommandLike
    
logger = logging.getLogger(__name__)

class _SendCommand(_BaseApiClient):
    async def _send_command_async(self, command: "CommandLike", *, server_key: str | None = None) -> Response:
        from ..command import normalize_command
        cmd = command if isinstance(command, str) else command.text
        
        logger.info("Sending command: %s", cmd)
        if server_key is not None:
            return await self._send_async_request(
                endpoint=_Endpoint.v2_command,
                json={"command": normalize_command(cmd)},
                headers={"server-key": server_key, "Authorization": self.global_key}
            )
        else:
            return await self._send_async_request(
                endpoint=_Endpoint.v2_command,
                json={"command": normalize_command(cmd)}
            )
        
    def _send_command_sync(self, command: "CommandLike", *, server_key: str | None = None) -> Response:
        from ..command import normalize_command
        cmd = command if isinstance(command, str) else command.text

        logger.info("Sending command: %s", cmd)
        if server_key is not None:
            return self._send_sync_request(
                endpoint=_Endpoint.v2_command,
                json={"command": normalize_command(cmd)},
                headers={"server-key": server_key, "Authorization": self.global_key}
            )
        else:
            return self._send_sync_request(
                endpoint=_Endpoint.v2_command,
                json={"command": normalize_command(cmd)}
            )