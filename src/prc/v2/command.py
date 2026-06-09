from httpx import Response
from ..v2.models import Endpoint
from ..base_client import _BaseApiClient

def normalize_command(command: str):
    return command if command.startswith(":") else f":{command}"

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