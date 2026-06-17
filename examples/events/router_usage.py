from fastapi import FastAPI, Request, Response, BackgroundTasks

import prc
from prc import cmd
from prc.events import Router, Context

client = prc.v2.AsyncClient(server_key="nJbYdaPQCZhhCSCVRjFO-gbzaDhOJQTPrFVIjmNuyTYqzyqupLolnWfJmPznx")

# No need to send sync handlers to a thread in this example
# because our sync handlers don't do any blocking operations,
# which will give better performance.
router = Router(client, sync_handlers_to_thread=False)

# You can assign multiple commands to the same handler
# by passing them as additional arguments to the decorator
@router.on.command("myid", "id", "whoami")
async def handle_myid_command(ctx: Context):
    # This handler will send the command user a PM when they run the command ';myid' in-game
    await ctx.areply(f"Your user ID is {ctx.user.id}.")
    
@router.on.emergency_start()
async def handle_emergency_start(ctx: Context[prc.v2.AsyncClient]):
    # This handler will check if the caller of an emergency call is on the Police or Sheriff team,
    # and if so, will PM them and then wanted off the team
    player = await ctx.client.get_player_from_user(ctx.emergency_call.caller)
    
    if player.team in ("Police", "Sheriff"):
        await ctx.client.send_command(cmd.pm(player,
            "You cannot make emergency calls while on this team! You will be wanted off the team shortly."
        ))
        await ctx.client.send_command(cmd.wanted(player))

@router.on.any_event()
def handle_any_event(ctx: Context):
    # This handler will be called for any non-command event
    print(f"Received event of type {ctx.event_type}.")

@router.on.any_custom_command()
def log_command_usage(ctx: Context):
    # This handler will log the usage of any custom command to the console
    # Replace with a proper logging statement in a production application
    print(f"User {ctx.user.id} executed command '{ctx.command.command}' with argument '{ctx.command.argument}'.")
    
# Basic FastAPI application to receive requests from PRC
app = FastAPI()

@app.post("/prc/webhook")
async def prc_webhook(request: Request, background_tasks: BackgroundTasks):
    # Handle the incoming request using the handle_fastapi_request method,
    # which will handle all dispatching and background task scheduling for us
    # and immediately return the appropriate HTTP status code.
    status = await router.handle_fastapi_request(request, background_tasks)
    return Response(status_code=status)