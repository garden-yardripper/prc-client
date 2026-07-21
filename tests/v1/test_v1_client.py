import respx
from prc import JoinLog, KillLog, CommandLog, ModCall, IdUser
from prc.v1 import (
    Client, AsyncClient,
    Server, Player, Staff,
    Queue, Bans, Vehicle
)

@respx.mock
def test_get_server_sync(server_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=server_payload
    )
    
    client = Client("server-key", use_registry=False, wait_for_rate_limit=False)
    server = client.get_server()
    
    assert route.called
    assert isinstance(server, Server)
    assert route.calls[0].request.headers["server-key"] == "server-key"
    
    assert client._get_remaining == 10
    assert client._get_expiration == 9999999
    
    assert server.name == "API Test"
    assert server.co_owners[0].id == 123
    
@respx.mock
async def test_get_server_async(server_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=server_payload
    )
    
    client = AsyncClient("server-key", use_registry=False, wait_for_rate_limit=False)
    server = await client.get_server()
    
    assert route.called
    assert isinstance(server, Server)
    assert route.calls[0].request.headers["server-key"] == "server-key"
    
    assert client._get_remaining == 10
    assert client._get_expiration == 9999999
    
    assert server.name == "API Test"
    assert server.co_owners[0].id == 123

@respx.mock
def test_get_players_sync(players_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/players").respond(200,
        headers={"x-ratelimit-remaining":"9", "x-ratelimit-reset":"9999998"},
        json=players_payload
    )

    client = Client("server-key", use_registry=False, wait_for_rate_limit=False)
    players_resp = client.get_players()

    assert route.called
    assert client._get_remaining == 9
    assert client._get_expiration == 9999998
    
    assert isinstance(players_resp, list)
    assert isinstance(players_resp[0], Player)
    
    assert players_resp[0].user.name.startswith("PlayerName")

@respx.mock
def test_get_staff_sync(staff_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/staff").respond(200,
        headers={"x-ratelimit-remaining":"8", "x-ratelimit-reset":"9999997"},
        json=staff_payload
    )

    client = Client("server-key", use_registry=False, wait_for_rate_limit=False)
    staff_resp = client.get_staff()

    assert route.called
    assert client._get_remaining == 8
    assert client._get_expiration == 9999997
    
    assert isinstance(staff_resp, Staff)
    assert staff_resp.admins

@respx.mock
def test_get_join_logs_sync(join_logs_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/joinlogs").respond(200,
        headers={"x-ratelimit-remaining":"7", "x-ratelimit-reset":"9999996"},
        json=join_logs_payload
    )

    client = Client("server-key", use_registry=False, wait_for_rate_limit=False)
    joins = client.get_join_logs()

    assert route.called
    assert client._get_remaining == 7
    assert client._get_expiration == 9999996
    
    assert isinstance(joins, list)
    assert isinstance(joins[0], JoinLog)
    assert joins[0].join is True


@respx.mock
def test_get_queue_sync(queue_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/queue").respond(200,
        headers={"x-ratelimit-remaining":"6", "x-ratelimit-reset":"9999995"},
        json=queue_payload
    )

    client = Client("server-key", use_registry=False, wait_for_rate_limit=False)
    q = client.get_queue()

    assert route.called
    assert client._get_remaining == 6
    assert client._get_expiration == 9999995
    
    assert isinstance(q, Queue)
    assert isinstance(q.players, list)
    assert isinstance(q.players[0], IdUser)

@respx.mock
def test_get_kill_logs_sync(kill_logs_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/killlogs").respond(200,
        headers={"x-ratelimit-remaining":"5", "x-ratelimit-reset":"9999994"},
        json=kill_logs_payload
    )

    client = Client("server-key", use_registry=False, wait_for_rate_limit=False)
    kills = client.get_kill_logs()

    assert route.called
    assert client._get_remaining == 5
    assert client._get_expiration == 9999994
    
    assert isinstance(kills, list)
    assert isinstance(kills[0], KillLog)

@respx.mock
def test_get_command_logs_sync(command_logs_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/commandlogs").respond(200,
        headers={"x-ratelimit-remaining":"4", "x-ratelimit-reset":"9999993"},
        json=command_logs_payload
    )

    client = Client("server-key", use_registry=False, wait_for_rate_limit=False)
    cmds = client.get_command_logs()

    assert route.called
    assert client._get_remaining == 4
    assert client._get_expiration == 9999993

    assert isinstance(cmds, list)
    assert isinstance(cmds[0], CommandLog)

@respx.mock
def test_get_mod_calls_sync(mod_calls_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/modcalls").respond(200,
        headers={"x-ratelimit-remaining":"3", "x-ratelimit-reset":"9999992"},
        json=mod_calls_payload
    )

    client = Client("server-key", use_registry=False, wait_for_rate_limit=False)
    calls = client.get_mod_calls()

    assert route.called
    assert client._get_remaining == 3
    assert client._get_expiration == 9999992
    
    assert isinstance(calls, list)
    assert isinstance(calls[0], ModCall)


@respx.mock
def test_get_bans_sync(bans_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/bans").respond(200,
        headers={"x-ratelimit-remaining":"2", "x-ratelimit-reset":"9999991"},
        json=bans_payload
    )

    client = Client("server-key", use_registry=False, wait_for_rate_limit=False)
    bans_resp = client.get_bans()

    assert route.called
    assert client._get_remaining == 2
    assert client._get_expiration == 9999991
    
    assert isinstance(bans_resp, Bans)
    assert bans_resp.users[0].name == "PlayerName"

@respx.mock
def test_get_vehicles_sync(vehicles_payload, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v1/server/vehicles").respond(200,
        headers={"x-ratelimit-remaining":"1", "x-ratelimit-reset":"9999990"},
        json=vehicles_payload
    )

    client = Client("server-key", use_registry=False, wait_for_rate_limit=False)
    vehicles_resp = client.get_vehicles()

    assert route.called
    assert client._get_remaining == 1
    assert client._get_expiration == 9999990
    
    assert isinstance(vehicles_resp, list)
    assert isinstance(vehicles_resp[0], Vehicle)