import prc
import asyncio

async def main():
    async with prc.v2.AsyncClient(server_key="...") as client:
        server = await client.get_bundled_server()
        for player in server.players:
            print(f"{player.user.username} is on the {player.team} team!")
    
if __name__ == "__main__":
    asyncio.run(main())