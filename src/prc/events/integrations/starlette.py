from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..router import Router
    from starlette.requests import Request
    from starlette.background import BackgroundTask

class _StarletteIntegration:
    def __init__(self, router: "Router") -> None:
        self.router = router
    
    async def handle_starlette_request(
        self, request: "Request"
    ) -> tuple[Literal[200, 400], "BackgroundTask | None"]:
        try:
            from starlette.background import BackgroundTask
        except ImportError:
            raise RuntimeError("Starlette integration for PRC events requires the `starlette` library.")
        
        raw_body = await request.body()
        headers = dict(request.headers)
        
        status, task = await self.router.prepare_request(raw_body, headers)
        if status == 200 and task:
            background_task = BackgroundTask(task)
        else:
            background_task = None
        
        return status, background_task
