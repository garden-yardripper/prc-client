from httpx import Response
from pydantic import BaseModel
from ..v2.models import Endpoint
from ..base_client import _BaseApiClient

def normalize_command(command: str):
    return command if command.startswith(":") else f":{command}"

class Command(BaseModel):
    command: str
    
    @property
    def payload(self) -> dict[str, str]:
        """Returns the payload to send this command to the API."""
        return {"command": self.command}

class _CmdFactory:
    def __getattr__(self, name: str):
        def call(*args):
            joined_args = ' '.join(args)
            full = f"{name} {joined_args}".strip()
            return Command(command=normalize_command(full))
        return call

cmd = _CmdFactory()

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