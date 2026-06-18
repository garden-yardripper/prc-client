import prc
from prc import cmd
from prc.events import Router, Context

client = prc.v2.Client(server_key="...")
router = Router(client, sync_handlers_to_thread=True)

# When retrieving servers, any full users in the data are automatically stored in a user registry
# which allows you to access a full user in the future if you only have a username or ID.
# This is useful when running certain commands (like :pm) that only require a username.
server = client.get_bundled_server()

@router.on.command("hello")
def hello_command(ctx: Context):
    # ctx.user only returns an IdUser. In the context reply methods,
    # it will check if the IdUser is found in the registry from a previous request
    # and fall back to calling the API to get the user's info.
    ctx.reply("Hello, world!")

# You can also check the registry manually using the client.cache attribute:
user = client.registry.resolve("username")
if user:
    client.send_command(cmd.pm(user, "I found you!"))