import asyncio
import prc
from prc import cmd

def get_env_vars() -> tuple[str, int]:
    import os
    
    global_key = os.getenv("GLOBAL_KEY")
    app_id = os.getenv("APP_ID")
    
    return global_key or "", int(app_id or 0)

async def main(global_key: str, app_id: int):
    app = prc.v2.AsyncClient(global_key=global_key, app_id=app_id)
    
    # Emulate a server key (replace with some mechanism)
    key1 = "abc-123"
    
    try:
        await app.send_command(cmd.m("Hello to server 1!"), server_key=key1)
    except prc.exceptions.UnauthorizedError:
        # This exception will be raised if the application has not been allowed to send commands
        # to this server key by the user. 
        # The user must authenticate the application using the link created by `app.generate_auth_link()`.
        print(
            "Unauthorized: Please authenticate this application using this link and try again:",
            app.generate_auth_link(key1)
        )

if __name__ == "__main__":
    global_key, app_id = get_env_vars()
    asyncio.run(main(global_key, app_id))