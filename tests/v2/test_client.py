import json

import httpx
import pytest
import datetime
import respx
from prc.exceptions import ApiError, RateLimited
from prc.v2.client import AsyncClient, Client
from prc.v2.models import BundledServer

@pytest.fixture
def payload():
    # Slightly modified version of PRC API docs' example response
    return {
        "Name": "API Test",
        "OwnerId": 123,
        "CoOwnerIds": [123],
        "CurrentPlayers": 123,
        "MaxPlayers": 123,
        "JoinKey": "APIServer",
        "AccVerifiedReq": "Disabled",
        "TeamBalance": True,
        
        "Players": [{
            "Team": "Sheriff",
            "Player": "PlayerName:123",
            "Callsign": "5D-550",
            "Location": {
                "LocationX": 1084.965,
                "LocationZ": 2302.28,
                "PostalCode": "218",
                "StreetName": "Park Street",
                "BuildingNumber": "2083"
            },
            "Permission": "Server Administrator",
            "WantedStars": 0
        }],
        
        "Staff": {
            "Admins": {
                "54249787": "Black_Hallow",
                "77573259": "sli_ckk"
            },
            "Mods": {
                "2": "JohnDoe",
                "3": "JaneDoe"
            },
            "Helpers": {
                "168691872": "Flat_bird"
            }
        },
        
        "JoinLogs": [{
            "Join": True,
            "Timestamp": 1704614400,
            "Player": "PlayerName:123"
        }],
        
        "Queue": [123],
        
        "KillLogs": [{
            "Killed": "PlayerName:123",
            "Timestamp": 1704614400,
            "Killer": "PlayerName:123"
        }],
        
        "CommandLogs": [{
            "Player": "PlayerName:123",
            "Timestamp": 1704614400,
            "Command": ":h"
        }],
        
        "ModCalls": [{
            "Caller": "PlayerName:123",
            "Moderator": "PlayerName:123",
            "Timestamp": 1704614400
        }],
        
        "EmergencyCalls": [{
            "Team": "Police",
            "Caller": 168691872,
            "Players": [],
            "Position": [
                -654.6,
                666.5
            ],
            "StartedAt": 1774216563,
            "CallNumber": 400,
            "Description": "stg",
            "PositionDescriptor": "sdfsdfsdf"
        }],
        
        "Vehicles": [{
            "Name": "Redline Fire Engine",
            "Owner": "Shawnyg",
            "Plate": "ABC-123",
            "Texture": "Livery Name",
            "ColorHex": "#ff4444",
            "ColorName": "Super Red"
        }]
    }

@respx.mock
def test_get_bundled_server_sync(payload: dict, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v2/server").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=payload
    )
    
    client = Client("server-key")
    server = client.get_bundled_server()
    
    assert route.called
    assert isinstance(server, BundledServer)
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
async def test_get_bundled_server_async(payload: dict, respx_mock: respx.MockRouter):
    route = respx_mock.get("https://api.erlc.gg/v2/server").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=payload
    )
    
    client = AsyncClient("server-key")
    server = await client.get_bundled_server()
    
    assert route.called
    assert isinstance(server, BundledServer)
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
    client = Client("server-key")
    
    ratelimit_body = {"code": 429, "message": "rate limited", "retry_after": 1}
    ratelimit_resp = httpx.Response(429, content=json.dumps(ratelimit_body).encode("utf-8"))
    with pytest.raises(RateLimited):
        client._raise_for_status(ratelimit_resp)
        
    error_body = {"code": 500, "message": "random error"}
    error_resp = httpx.Response(429, content=json.dumps(error_body).encode("utf-8"))
    with pytest.raises(ApiError):
        client._raise_for_status(error_resp)