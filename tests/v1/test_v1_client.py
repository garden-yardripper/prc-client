import respx
from prc.users import IdUser
from prc.v1 import Client, AsyncClient
from prc.v1.models import (
    Server, Player, Staff, JoinLog,
    Queue, KillLog, CommandLog,
    ModCall, Bans, Vehicle
)

def server_payload():
    return {
        "Name": "API Test",
        "OwnerId": 123,
        "CoOwnerIds": [
            123
        ],
        "CurrentPlayers": 123,
        "MaxPlayers": 123,
        "JoinKey": "APIServer",
        "AccVerifiedReq": "Email",
        "TeamBalance": True
    }
    
def players_payload():
    return [
        {
            "Player": "PlayerName:123",
            "Permission": "Server Administrator",
            "Callsign": "A-123",
            "Team": "Police"
        }
    ]

def staff_payload():
    return {
        "CoOwners": [
            123
        ],
        "Admins": {
            "54249787": "Black_Hallow",
            "77573259": "sli_ckk"
        },
        "Mods": {
            "2": "JohnDoe",
            "3": "JaneDoe"
        }
    }
    
def join_logs_payload():
    return [
        {
            "Join": True,
            "Timestamp": 1704614400,
            "Player": "PlayerName:123"
        }
    ]
    
def queue_payload():
    return [123]

def kill_logs_payload():
    return [
        {
            "Killed": "PlayerName:123",
            "Killer": "PlayerName:456",
            "Timestamp": 1704614400
        }
    ]
    
def command_logs_payload():
    return [
        {
            "Player": "PlayerName:123",
            "Command": ":h",
            "Timestamp": 1704614400
        }
    ]
    
def mod_calls_payload():
    return [
        {
            "Caller": "PlayerName:123",
            "Moderator": "PlayerName:456",
            "Timestamp": 1704614400
        }
    ]
    
def bans_payload():
    return {
        "123": "PlayerName",
        "456": "OtherPlayerName"
    }
    
def vehicles_payload():
    return [
        {
            "Name": "2019 Falcon Interceptor Utility",
            "Owner": "flat_bird",
            "Texture": "Standard"
        }
    ]

@respx.mock
def test_get_server_sync(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=server_payload()
    )
    
    client = Client("server-key")
    server = client.get_server()
    
    assert route.called
    assert isinstance(server, Server)
    assert route.calls[0].request.headers["server-key"] == "server-key"
    
    assert client.get_remaining == 10
    assert client.get_expiration == 9999999
    
    assert server.name == "API Test"
    assert server.co_owners[0].id == 123
    
@respx.mock
async def test_get_server_async(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=server_payload()
    )
    
    client = AsyncClient("server-key")
    server = await client.get_server()
    
    assert route.called
    assert isinstance(server, Server)
    assert route.calls[0].request.headers["server-key"] == "server-key"
    
    assert client.get_remaining == 10
    assert client.get_expiration == 9999999
    
    assert server.name == "API Test"
    assert server.co_owners[0].id == 123

@respx.mock
def test_get_players_sync(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/players").respond(200,
        headers={"x-ratelimit-remaining":"9", "x-ratelimit-reset":"9999998"},
        json=players_payload()
    )

    client = Client("server-key")
    players_resp = client.get_players()

    assert route.called
    assert client.get_remaining == 9
    assert client.get_expiration == 9999998
    
    assert isinstance(players_resp, list)
    assert isinstance(players_resp[0], Player)
    
    assert players_resp[0].user.name.startswith("PlayerName")

@respx.mock
def test_get_staff_sync(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/staff").respond(200,
        headers={"x-ratelimit-remaining":"8", "x-ratelimit-reset":"9999997"},
        json=staff_payload()
    )

    client = Client("server-key")
    staff_resp = client.get_staff()

    assert route.called
    assert client.get_remaining == 8
    assert client.get_expiration == 9999997
    
    assert isinstance(staff_resp, Staff)
    assert staff_resp.admins

@respx.mock
def test_get_join_logs_sync(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/joinlogs").respond(200,
        headers={"x-ratelimit-remaining":"7", "x-ratelimit-reset":"9999996"},
        json=join_logs_payload()
    )

    client = Client("server-key")
    joins = client.get_join_logs()

    assert route.called
    assert client.get_remaining == 7
    assert client.get_expiration == 9999996
    
    assert isinstance(joins, list)
    assert isinstance(joins[0], JoinLog)
    assert joins[0].join is True


@respx.mock
def test_get_queue_sync(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/queue").respond(200,
        headers={"x-ratelimit-remaining":"6", "x-ratelimit-reset":"9999995"},
        json=queue_payload()
    )

    client = Client("server-key")
    q = client.get_queue()

    assert route.called
    assert client.get_remaining == 6
    assert client.get_expiration == 9999995
    
    assert isinstance(q, Queue)
    assert isinstance(q.players, list)
    assert isinstance(q.players[0], IdUser)

@respx.mock
def test_get_kill_logs_sync(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/killlogs").respond(200,
        headers={"x-ratelimit-remaining":"5", "x-ratelimit-reset":"9999994"},
        json=kill_logs_payload()
    )

    client = Client("server-key")
    kills = client.get_kill_logs()

    assert route.called
    assert client.get_remaining == 5
    assert client.get_expiration == 9999994
    
    assert isinstance(kills, list)
    assert isinstance(kills[0], KillLog)

@respx.mock
def test_get_command_logs_sync(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/commandlogs").respond(200,
        headers={"x-ratelimit-remaining":"4", "x-ratelimit-reset":"9999993"},
        json=command_logs_payload()
    )

    client = Client("server-key")
    cmds = client.get_command_logs()

    assert route.called
    assert client.get_remaining == 4
    assert client.get_expiration == 9999993

    assert isinstance(cmds, list)
    assert isinstance(cmds[0], CommandLog)

@respx.mock
def test_get_mod_calls_sync(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/modcalls").respond(200,
        headers={"x-ratelimit-remaining":"3", "x-ratelimit-reset":"9999992"},
        json=mod_calls_payload()
    )

    client = Client("server-key")
    calls = client.get_mod_calls()

    assert route.called
    assert client.get_remaining == 3
    assert client.get_expiration == 9999992
    
    assert isinstance(calls, list)
    assert isinstance(calls[0], ModCall)


@respx.mock
def test_get_bans_sync(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/bans").respond(200,
        headers={"x-ratelimit-remaining":"2", "x-ratelimit-reset":"9999991"},
        json=bans_payload()
    )

    client = Client("server-key")
    bans_resp = client.get_bans()

    assert route.called
    assert client.get_remaining == 2
    assert client.get_expiration == 9999991
    
    assert isinstance(bans_resp, Bans)
    assert bans_resp.users[0].name == "PlayerName"

@respx.mock
def test_get_vehicles_sync(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/vehicles").respond(200,
        headers={"x-ratelimit-remaining":"1", "x-ratelimit-reset":"9999990"},
        json=vehicles_payload()
    )

    client = Client("server-key")
    vehicles_resp = client.get_vehicles()

    assert route.called
    assert client.get_remaining == 1
    assert client.get_expiration == 9999990
    
    assert isinstance(vehicles_resp, list)
    assert isinstance(vehicles_resp[0], Vehicle)