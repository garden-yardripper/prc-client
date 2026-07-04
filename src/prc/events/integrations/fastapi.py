from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..router import Router
    from fastapi import Request, BackgroundTasks

class _FastApiIntegration:
    def __init__(self, router: "Router") -> None:
        self.router = router
    
    async def handle_fastapi_request(self,
        request: "Request", background_tasks: "BackgroundTasks"
    ) -> Literal[200, 400]:
        raw_body = await request.body()
        headers = dict(request.headers)

        status, task = await self.router.prepare_request(raw_body, headers)
        if status == 200 and task:
            background_tasks.add_task(task)

        return status