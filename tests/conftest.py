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