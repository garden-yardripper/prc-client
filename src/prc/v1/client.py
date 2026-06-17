from httpx import Response
from ..command import CommandLike
from .fetch import _GetDataAsync, _GetDataSync
from .send_command import _SendCommand

class AsyncClient(_GetDataAsync, _SendCommand):
    async def send_command(self, command: CommandLike) -> Response:
        return await self._send_command_async(command)

class Client(_GetDataSync, _SendCommand):
    def send_command(self, command: CommandLike) -> Response:
        return self._send_command_sync(command)