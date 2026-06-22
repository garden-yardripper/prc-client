import json

import httpx
import pytest
import datetime
import respx
import prc

@respx.mock
def test_get_bundled_server_sync(v2_payload: dict, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v2/server").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=v2_payload
    )
    
    client = prc.v2.Client("server-key")
    server = client.get_bundled_server()
    
    assert route.called
    assert isinstance(server, prc.v2.BundledServer)
    assert route.calls[0].request.headers["server-key"] == "server-key"
    
    assert client._get_remaining == 10
    assert client._get_expiration == 9999999
    
    assert server.name == "API Test"
    assert server.co_owners[0].id == 123
    
    assert len(server.players) == 1
    assert server.players[0].user.name == "PlayerName"
    assert server.players[0].location.street_name == "Park Street"
    
    assert str(server.staff.admins[0]) == "Black_Hallow:54249787"
    
    assert isinstance(server.join_logs[0].timestamp, datetime.datetime)
    
    assert server.queue.length == 1
    
@respx.mock
async def test_get_bundled_server_async(v2_payload: dict, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v2/server").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=v2_payload
    )
    
    client = prc.v2.AsyncClient("server-key")
    server = await client.get_bundled_server()
    
    assert route.called
    assert isinstance(server, prc.v2.BundledServer)
    assert route.calls[0].request.headers["server-key"] == "server-key"
    
    assert client._get_remaining == 10
    assert client._get_expiration == 9999999
    
    assert server.name == "API Test"
    assert server.co_owners[0].id == 123
    
    assert len(server.players) == 1
    assert server.players[0].user.name == "PlayerName"
    assert server.players[0].location.street_name == "Park Street"
    
    assert str(server.staff.admins[0]) == "Black_Hallow:54249787"
    
    assert isinstance(server.join_logs[0].timestamp, datetime.datetime)
    
    assert server.queue.length == 1

def test_raise_for_status():
    client = prc.v2.Client("server-key")
    
    ratelimit_body = {"code": 429, "message": "rate limited", "retry_after": 1}
    ratelimit_resp = httpx.Response(429, content=json.dumps(ratelimit_body).encode("utf-8"))
    with pytest.raises(prc.exceptions.RateLimited):
        client._raise_for_status(ratelimit_resp)
        
    error_body = {"code": 500, "message": "random error"}
    error_resp = httpx.Response(500, content=json.dumps(error_body).encode("utf-8"))
    with pytest.raises(prc.exceptions.ApiError):
        client._raise_for_status(error_resp)