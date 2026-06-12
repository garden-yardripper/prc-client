import prc
from prc.v2.command import cmd

with prc.v2.Client(server_key="...") as client:
    server = client.get_server(players=True)
    
    # Get players whose names start with 'all' or 'others'
    players_to_kick = [
        player for player in server.players
        if player.user.name.lower().startswith(("all", "others"))
    ]
    
    # Kick the players from the server
    client.send_command(cmd.kick(players_to_kick, "Username starts with 'all' or 'others'."))
    
    # Alternatively:
    # cmd.kick(players_to_kick, "Username starts with 'all' or 'others'.").send(client)