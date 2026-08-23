# prc-client
`prc-client` is a flexible, feature-rich API client for the ER:LC private server API. This client provides a simple and intuitive interface for interacting with ER:LC private servers with detailed data models, typing, comprehensive error handling, and a high-performance architecture.

This library aims to provide all the functionality you need without overwhelming developers with unnecessary features or complexity. `prc-client` stays lightweight, allowing for full control over your development process - whether you're building a simple automation script to fully-featured complex application integrating with the PRC API.

# Key Features
- 100% coverage of all V1 and V2 API endpoints
- Full support for the event webhook API
- Full support for [public applications](README.md#public-application-guide)
- Support for both synchronous and asynchronous applications
- Automatic rate limit handling
- Intuitive developer interface allows for rapid prototyping and high development experience
- High performance - built on top of [HTTPX](https://github.com/encode/httpx) for HTTP requests and [Pydantic](https://github.com/samuelcolvin/pydantic) for data validation
- Detailed docstring documentation and examples
- Easy to debug with comprehensive error handling and logging

# Installation
Install `prc-client` using pip:

```bash
pip install prc-client
```

Optionally install additional dependencies:

```bash
pip install prc-client[events]
```

# Quick Start
Import the `prc` module and create a client instance.

```python
import prc

client = prc.v2.Client(server_key="...")
```
<details>
<summary>Or asynchronously...</summary>

```python
import prc
import asyncio

async def main():
    client = prc.v2.AsyncClient(server_key="...")

asyncio.run(main())
```
</details>  

Get a server with configurable parameters, or get a `BundledServer` with all available API data.

```python
import prc

client = prc.v2.Client(server_key="...")

# Contains only the specified data
server = client.get_server(players=True, vehicles=True)
# Contains all available data
bundled_server = client.get_bundled_server()
```

<details>
<summary>Or asynchronously...</summary>

```python
import prc
import asyncio

async def main():
    client = prc.v2.AsyncClient(server_key="...")

    # Contains only the specified data
    server = await client.get_server(players=True, vehicles=True)
    # Contains all available data
    bundled_server = await client.get_bundled_server()

asyncio.run(main())
```
</details> 

Send a command to the server using the `send_command` method and `cmd` factory to build commands.

```python
import prc
from prc import cmd

client = prc.v2.Client(server_key="...")

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
import asyncio
from prc import cmd

async def main():
    client = prc.v2.AsyncClient(server_key="...")

    # Contains only the specified data
    server = await client.get_server(players=True, vehicles=True)
    # Contains all available data
    bundled_server = await client.get_bundled_server()

    # Send a PM to all players
    await client.send_command(cmd.pm(server.players, "Welcome to the server!"))

asyncio.run(main())
```
</details> 

Let's set up a router with a simple command handler to receive requests from PRC.

Note that routers require an ASGI web framework using libraries such as FastAPI or Starlette in order to receive and process requests from PRC. Refer to the [Web server guide](README.md#web-server-guide) section for help.

```python
import prc
from prc import cmd
from prc.events import Router, Context

client = prc.v2.Client(server_key="...")
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
import asyncio
from prc import cmd
from prc.events import Router, Context

client = prc.v2.AsyncClient(server_key="...")
# Create a router
router = Router(client)

# Define a command handler to run when the command ;myid / ;id / ;whoami is sent
@router.on.command("myid", "id", "whoami")
async def handle_myid_command(ctx: Context):
    await ctx.areply(f"Your ID is: {ctx.user.id}")

# This command handler runs when any command is received
@router.on.any_command()
async def handle_any_command(ctx: Context):
    print(f"User {ctx.user.id} sent command '{ctx.command.command}' with arguments {ctx.command.arguments}")

async def main():
    # Contains only the specified data
    server = await client.get_server(players=True, vehicles=True)
    # Contains all available data
    bundled_server = await client.get_bundled_server()

    # Send a PM to all players
    await client.send_command(cmd.pm(server.players, "Welcome to the server!"))

asyncio.run(main())
```

</details>

# Web Server Guide
In order to properly integrate with PRC's event webhook and receive requests from PRC, you will need to run a web server with an ASGI framework of your choosing. `prc-client` comes with built-in integrations for FastAPI, Starlette, and Quart, but you can use any framework with the lower-level `prepare_request` method.

Using the `Router` class methods allows the library to automatically validate incoming requests for you and ensure that the request comes from PRC and was not tampered with.

`prc-client` makes the required framework code extremely minimal. Take a look:

```python
import prc
from prc.events import Router
from fastapi import FastAPI, Request, Response, BackgroundTasks

client = prc.v2.Client(server_key="...")
router = Router(client)

@router.on.command("myid")
async def handle_myid_command(ctx: Context):
    await ctx.areply(f"Your ID is: {ctx.user.id}")

app = FastAPI()

@app.post("/your/endpoint")
async def prc_webhook(request: Request, background_tasks: BackgroundTasks):
    status = await router.handle_fastapi_request(request, background_tasks)
    return Response(status_code=status)
```

Code breakdown:
- Creates a client and an event router
- Registers the command `;myid`
- Creates a FastAPI application and creates a POST endpoint
- Uses the built in `handle_fastapi_request` method to validate the request and dispatches to registered functions. 
  - The method requires the `Request` and `BackgroundTasks` objects.
  - It will add the dispatch job as a background task and immediately return the HTTP status code that should be returned to the server. This allows long-running or rate-limit-bound functions to run in the background while immediately responding to the server so requests do not time out.

See the [FastAPI documentation](https://fastapi.tiangolo.com/) for more information on how to use FastAPI, or check out the [examples](./examples) for more information on specific use cases.

# Public Application Guide
`prc-client` fully supports PRC's new public application system. With the new ERLC API safety changes, this is essential for medium-sized apps to be able to send commands to users' servers without needing to be manually IP whitelisted.

The authentication flow is described in more detail on PRC's [documentation](https://apidocs.erlc.gg/creating-authorization-links), however the basic steps are as follows:

1. Ask the user for their server key
2. Generate an auth URL from the server key and application ID
3. User accepts the request from the link
4. Use the user's server key along with your application's global key to authenticate command requests

`prc-client` hides the internal details for you, but it is important to understand how it works.

Public applications are required to supply the `server_key` parameter for every call to `send_command`. This is a requirement by the API in order to authenticate and specify the server to send the command to.

Public applications are created with the regular `Client`/`AsyncClient` V2 clients. Let's create one:

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
# without needing manual IP whitelisting.
app.send_command(cmd.m("This works!"), server_key=server_key)
```
