import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

@pytest.fixture
def v2_payload():
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

@pytest.fixture 
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

@pytest.fixture
def players_payload():
    return [
        {
            "Player": "PlayerName:123",
            "Permission": "Server Administrator",
            "Callsign": "A-123",
            "Team": "Police"
        }
    ]

@pytest.fixture
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

@pytest.fixture
def join_logs_payload():
    return [
        {
            "Join": True,
            "Timestamp": 1704614400,
            "Player": "PlayerName:123"
        }
    ]

@pytest.fixture
def queue_payload():
    return [123]

@pytest.fixture
def kill_logs_payload():
    return [
        {
            "Killed": "PlayerName:123",
            "Killer": "PlayerName:456",
            "Timestamp": 1704614400
        }
    ]

@pytest.fixture
def command_logs_payload():
    return [
        {
            "Player": "PlayerName:123",
            "Command": ":h",
            "Timestamp": 1704614400
        }
    ]

@pytest.fixture
def mod_calls_payload():
    return [
        {
            "Caller": "PlayerName:123",
            "Moderator": "PlayerName:456",
            "Timestamp": 1704614400
        }
    ]

@pytest.fixture
def bans_payload():
    return {
        "123": "PlayerName",
        "456": "OtherPlayerName"
    }
    
@pytest.fixture
def vehicles_payload():
    return [
        {
            "Name": "2019 Falcon Interceptor Utility",
            "Owner": "flat_bird",
            "Texture": "Standard"
        }
    ]