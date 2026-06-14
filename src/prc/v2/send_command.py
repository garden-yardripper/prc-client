from httpx import Response
from .models import Endpoint
from ..base_client import _BaseApiClient
from ..command import normalize_command

class _SendCommand(_BaseApiClient):
    async def _send_command_async(self, command: str) -> Response:
        return await self._send_async_request(
            endpoint=Endpoint.v2_command,
            json={"command": normalize_command(command)}
        )
        
    def _send_command_sync(self, command: str) -> Response:
        return self._send_sync_request(
            endpoint=Endpoint.v2_command,
            json={"command": normalize_command(command)}
        )