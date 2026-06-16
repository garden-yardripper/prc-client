from typing import Literal
from ..router import Router

try:
    from quart import Quart, request
except ImportError:
    raise RuntimeError((
        "Quart integration for PRC events requires the `quart` library. "
        "Install the dependency with `pip install prc-client[quart]`."
    ))

class _QuartIntegration:
    def __init__(self, router: Router) -> None:
        self.router = router
    
    async def handle_quart_request(self, app: Quart) -> Literal[200, 400]:
        raw_body = await request.get_data(as_text=False)
        raw_body = raw_body.encode() if isinstance(raw_body, str) else raw_body
        headers = dict(request.headers)
        
        status, task = await self.router.prepare_request(raw_body, headers)
        if status == 200 and task:
            app.add_background_task(task)
        
        return status