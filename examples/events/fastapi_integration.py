from fastapi import FastAPI, BackgroundTasks, Request, Response

import prc
from prc.events import Router, Context

client = prc.v2.AsyncClient(server_key="...")
router = Router(client)

@router.on.command("say")
async def handle_say_command(ctx: Context[prc.v2.AsyncClient]):
    player = await ctx.client.get_player_from_user(ctx.user.id)
    await ctx.areply(f"Hello, {player.user.name}! You said: {ctx.command.argument}")

# Basic FastAPI application to receive requests from PRC
app = FastAPI()

@app.post("/prc/webhook")
async def prc_webhook(request: Request, background_tasks: BackgroundTasks):
    # Handle the incoming request using the handle_fastapi_request method,
    # which will handle all dispatching and background task scheduling for us
    # and immediately return the appropriate HTTP status code.
    status = await router.handle_fastapi_request(request, background_tasks)
    return Response(status_code=status)