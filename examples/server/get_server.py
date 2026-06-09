import prc

def main():
    with prc.v2.Client(server_key="...") as client:
        server = client.get_bundled_server()
        for player in server.players:
            print(f"{player.user.username} is on the {player.team} team!")
    
if __name__ == "__main__":
    main()