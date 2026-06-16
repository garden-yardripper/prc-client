from typing import Literal
from ..router import Router

try:
    from fastapi import Request, BackgroundTasks
except ImportError:
    raise RuntimeError((
        "FastAPI integration for PRC events requires the `fastapi` library. "
        "Install the dependency with `pip install prc-client[fastapi]`."
    ))

class _FastApiIntegration:
    def __init__(self, router: Router) -> None:
        self.router = router
    
    async def handle_fastapi_request(self, request: Request, background_tasks: BackgroundTasks) -> Literal[200, 400]:
        raw_body = await request.body()
        headers = dict(request.headers)

        status, task = await self.router.prepare_request(raw_body, headers)
        if status == 200 and task:
            background_tasks.add_task(task)

        return status