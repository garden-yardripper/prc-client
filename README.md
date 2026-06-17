# prc-client
`prc-client` is a flexible, feature-rich API client for the ER:LC private server API. This client provides a simple and intuitive interface for interacting with ER:LC private servers with detailed data models, typing, comprehensive error handling, and a high-performance architecture.

# Key Features
- 100% coverage of all V1 and V2 API endpoints
- Full support for the event webhook API
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