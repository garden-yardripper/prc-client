# prc-client
`prc-client` is a flexible, feature-rich API client for the ER:LC private server API. This client provides a simple and intuitive interface for interacting with ER:LC private servers with detailed data models, typing, comprehensive error handling, and a high-performance architecture.

This library aims to provide all the functionality you need without overwhelming developers with unnecessary features or complexity. `prc-client` stays lightweight, allowing for full control over your development process - whether you're building a simple automation script to fully-featured complex application integrating with the PRC API.

# Key Features
- 100% coverage of all V1 and V2 API endpoints
- Full support for the event webhook API
- Full support for **public applications**
- Support for both synchronous and asynchronous applications
- Automatic rate limit handling
- Intuitive developer interface allows for rapid prototyping and high development experience
- High performance - built on top of [HTTPX](https://github.com/encode/httpx) for HTTP requests and [Pydantic](https://github.com/samuelcolvin/pydantic) for data validation
- Detailed docstring documentation and examples
- Comprehensive error handling and logging

# Installation
Install `prc-client` using pip:

```bash
pip install prc-client
```

Optionally install additional dependencies:

```bash
pip install prc-client[events,fastapi]
```

# Quick Start
Import the `prc` module and create a client instance.

```python
import prc

client = prc.v2.Client()
```
<details>
<summary>Or asynchronously...</summary>

```python
import prc

client = prc.v2.AsyncClient()
```
</details>  

Get a server with configurable parameters, or get a `BundledServer` with all available API data.

```python
import prc

client = prc.v2.Client()

# Contains only the specified data
server = client.get_server(players=True, vehicles=True)
# Contains all available data
bundled_server = client.get_bundled_server()
```

<details>
<summary>Or asynchronously...</summary>

```python
import prc

async def main():
    client = prc.v2.AsyncClient()

    # Contains only the specified data
    server = await client.get_server(players=True, vehicles=True)
    # Contains all available data
    bundled_server = await client.get_bundled_server()
```
</details> 

Send a command to the server using the `send_command` method and `cmd` factory to build commands.

```python
import prc
from prc import cmd

client = prc.v2.Client()

# Contains only the specified data
server = client.get_server(players=True, vehicles=True)
# Contains all available data
bundled_server = client.get_bundled_server()

# Send a PM to all players
client.send_command(cmd.pm(server.players, "Welcome to the server!"))
```

<details>
<summary>Or asynchronously...</summary>

```python
import prc
from prc import cmd

async def main():
    client = prc.v2.AsyncClient()

    # Contains only the specified data
    server = await client.get_server(players=True, vehicles=True)
    # Contains all available data
    bundled_server = await client.get_bundled_server()

    # Send a PM to all players
    await client.send_command(cmd.pm(server.players, "Welcome to the server!"))
```
</details> 

Let's set up a router with a simple command handler to receive requests from PRC.

```python
import prc
from prc import cmd
from prc.events import Router, Context

client = prc.v2.Client()
# Create a router
router = Router(client)

# Define a command handler to run when the command ;myid / ;id / ;whoami is sent
@router.on.command("myid", "id", "whoami")
def handle_myid_command(ctx: Context):
    ctx.reply(f"Your ID is: {ctx.user.id}")

# This command handler runs when any command is received
@router.on.any_command()
def handle_any_command(ctx: Context):
    print(f"User {ctx.user.id} sent command '{ctx.command.command}' with arguments {ctx.command.arguments}")

# Contains only the specified data
server = client.get_server(players=True, vehicles=True)
# Contains all available data
bundled_server = client.get_bundled_server()

# Send a PM to all players
client.send_command(cmd.pm(server.players, "Welcome to the server!"))
```

<details>
<summary>Or asynchronously...</summary>

```python
import prc
from prc import cmd
from prc.events import Router, Context

client = prc.v2.AsyncClient()
# Create a router
router = Router(client)

# Define a command handler to run when the command ;myid / ;id / ;whoami is sent
@router.on.command("myid", "id", "whoami")
async def handle_myid_command(ctx: Context):
    await ctx.areply(f"Your ID is: {ctx.user.id}")

# This command handler runs when any command is received
@router.on.any_command()
def handle_any_command(ctx: Context):
    print(f"User {ctx.user.id} sent command '{ctx.command.command}' with arguments {ctx.command.arguments}")

async def main():
    # Contains only the specified data
    server = await client.get_server(players=True, vehicles=True)
    # Contains all available data
    bundled_server = await client.get_bundled_server()

    # Send a PM to all players
    await client.send_command(cmd.pm(server.players, "Welcome to the server!"))
```

</details>

<details>
<summary>FastAPI application code</summary>

See the [FastAPI documentation](https://fastapi.tiangolo.com/) for more information on how to use FastAPI.

```python
from fastapi import FastAPI, Request, Response, BackgroundTasks

app = FastAPI()

@app.post("/your/endpoint")
async def prc_webhook(request: Request, background_tasks: BackgroundTasks):
    status = await router.handle_fastapi_request(request, background_tasks)
    return Response(status_code=status)
```
</details>

Check out the [examples](./examples) for more information on specific use cases.

# Public Application Guide
`prc-client` fully supports PRC's new public application system. With the new ERLC API safety changes, this is essential for medium-sized apps to be able to send commands to users' servers without needing to be manually IP whitelisted.

The authentication flow is described in more detail on PRC's [documentation](https://apidocs.erlc.gg/creating-authorization-links), however the basic steps are as follows:

1. Ask the user for their server key
2. Generate an auth URL from the server key and application ID
3. User accepts the request from the link
4. Use the user's server key along with your application's global key to authenticate command requests

`prc-client` hides the internal details for you, but it is important to understand how it works.

Public applications are created with the regular `Client`/`AsyncClient` clients. Let's create one:

```python
import prc
from prc import cmd

# Create an application via https://api.erlc.gg/developers/applications
# and set your global key and app ID here
# Note: You cannot supply server_key and global_key/app_id together
app = prc.v2.Client(
    global_key="...",
    app_id=123
)

# Simulated server key input from a user; replace with an actual mechanism
server_key = input("What is your server key?")
link = app.generate_auth_link(server_key)
print("Please authenticate this app via this link:", link)

# Once the user authenticates, this command will work
# without needing manual IP whitelisting:
app.send_command(cmd.m("This works!"), server_key=server_key)
```