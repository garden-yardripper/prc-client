import respx
import prc
from prc import FullUser, UsernameUser
from prc.v2 import BundledServer, Server
from prc.v1 import Player as V1Player

def server_staff():
    return {
        "Name": "API Test",
        "OwnerId": 123,
        "CoOwnerIds": [123],
        "CurrentPlayers": 123,
        "MaxPlayers": 123,
        "JoinKey": "APIServer",
        "AccVerifiedReq": "Disabled",
        "TeamBalance": True,
        
        "Staff": {
            "Admins": {},
            "Mods": {},
            "Helpers": {
                "168691872": "Flat_bird"
            }
        }
    }

@respx.mock
def test_user_registry_on_bundle(v2_payload: dict, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v2/server").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=v2_payload
    )
    
    client = prc.v2.Client("server-key")
    server = client.get_bundled_server()
    
    assert route.called
    assert isinstance(server, BundledServer)
    
    # resolved from server.staff.admins
    user_resolved = client.registry.resolve(UsernameUser("Black_Hallow"))
    assert isinstance(user_resolved, FullUser)
    assert user_resolved.name == "Black_Hallow"
    assert user_resolved.id == 54249787
    
    id_resolved = client.registry.resolve(123)
    assert isinstance(id_resolved, FullUser)
    assert id_resolved.name == "PlayerName"
    assert id_resolved.id == 123

    # found in vehicles but without ID
    assert client.registry.resolve("Shawnyg") is None
    
@respx.mock
def test_user_registry_on_server(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v2/server").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=server_staff()
    )
    
    client = prc.v2.Client("server-key")
    server = client.get_server(staff=True)
    
    assert route.called
    assert isinstance(server, Server)
    
    user_resolved = client.registry.resolve(UsernameUser("Flat_bird"))
    assert isinstance(user_resolved, FullUser)
    assert user_resolved.name == "Flat_bird"
    assert user_resolved.id == 168691872
    
    # PlayerName is not found in server staff, so it should not be resolved
    id_resolved = client.registry.resolve(123)
    assert id_resolved is None
    
@respx.mock
def test_user_registry_on_v1(players_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/players").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=players_payload
    )
    
    client = prc.v1.Client("server-key")
    players = client.get_players()
    
    assert route.called
    assert isinstance(players, list)
    assert isinstance(players[0], V1Player)
    
    user_resolved = client.registry.resolve("PlayerName")
    assert isinstance(user_resolved, FullUser)
    assert user_resolved.name == "PlayerName"
    assert user_resolved.id == 123
    
    # not found in players, so it should not be resolved
    id_resolved = client.registry.resolve(456)
    assert id_resolved is None