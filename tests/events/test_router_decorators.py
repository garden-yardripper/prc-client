import json
import pytest

from prc.events.models import CustomCommand, EventBatch, Context
from prc.events.router import Router
from prc.v2.client import AsyncClient
from prc.v2.models import EmergencyCall

def emergency_call():
    return {
        "events": [{
            "data": {
                "players": [],
                "caller": 913430532,
                "description": "hekp me",
                "callNumber": 136,
                "team": "Fire",
                "position": [
                    2358.7,
                    1180.1
                ],
                "positionDescriptor": "rta",
                "startedAt": 1775442933
            },
            "timestamp": 1775442933,
            "event": "EmergencyCallStarted",
            "origin": "server"
        }],
        "server": "gbzaDhOJQTPrFVIjmNuyTYqzyqupLolnWfJmPznx"
    }
    
def webhook_probe():
    return {
        "server": "global",
        "events": [{
            "event": "WebhookProbe",
            "timestamp": 1775444267,
            "origin": "global",
            "data": {}
        }]
    }
    
def custom_command():
    return {
        "events": [{
            "data": {
                "command": "logging",
                "argument": "This is a custom command."
            },
            "timestamp": 1775518795,
            "event": "CustomCommand",
            "origin": "913430532"
        }],
        "server": "gbzaDhOJQTPrFVIjmNuyTYqzyqupLolnWfJmPznx"
    }
    
def all_events():
    return {
        "events": [
            {
                "data": {
                    "players": [],
                    "caller": 913430532,
                    "description": "hekp me",
                    "callNumber": 136,
                    "team": "Fire",
                    "position": [
                        2358.7,
                        1180.1
                    ],
                    "positionDescriptor": "rta",
                    "startedAt": 1775442933
                },
                "timestamp": 1775442933,
                "event": "EmergencyCallStarted",
                "origin": "server"
            },
            {
                "event": "WebhookProbe",
                "timestamp": 1775444267,
                "origin": "global",
                "data": {}
            },
            {
                "data": {
                    "command": "logging",
                    "argument": "This is a custom command."
                },
                "timestamp": 1775518795,
                "event": "CustomCommand",
                "origin": "913430532"
            }
        ],
        "server": "gbzaDhOJQTPrFVIjmNuyTYqzyqupLolnWfJmPznx"
    }

def test_event_validation():
    router = Router(AsyncClient("server-key"))
    emergency = router._decode_verified_body(json.dumps(emergency_call()).encode())
    probe = router._decode_verified_body(json.dumps(webhook_probe()).encode())
    command = router._decode_verified_body(json.dumps(custom_command()).encode())
    
    assert isinstance(emergency, EventBatch)
    assert isinstance(probe, EventBatch)
    assert isinstance(command, EventBatch)
    
    assert isinstance(emergency.events[0], Context)
    assert isinstance(probe.events[0], Context)
    assert isinstance(command.events[0], Context)
    
    assert isinstance(emergency.events[0].emergency_call, EmergencyCall)
    assert isinstance(command.events[0].command, CustomCommand)
    
    with pytest.raises(ValueError):
        emergency.events[0].command
    
    with pytest.raises(ValueError):
        command.events[0].emergency_call
        
async def test_router_event_dispatch():
    router = Router(AsyncClient("server-key"), sync_handlers_to_thread=False)
    # ensure each decorated function is called exactly once
    emergency_start_called = 0
    logging_command_called = 0
    any_cmd_called = 0
    any_event_called = 0
    
    @router.on.emergency_start()
    def emergency_start(e: Context):
        nonlocal emergency_start_called
        assert isinstance(e, Context)
        assert e.event_type == "EmergencyCallStarted"
        emergency_start_called += 1
    
    @router.on.command("logging")
    async def logging_command(e: Context):
        nonlocal logging_command_called
        assert isinstance(e, Context)
        assert e.event_type == "CustomCommand"
        logging_command_called += 1
    
    @router.on.any_custom_command()
    def any_cmd(e: Context):
        nonlocal any_cmd_called
        assert e.event_type == "CustomCommand"
        any_cmd_called += 1
        
    @router.on.any_event()
    async def any_event(e: Context):
        nonlocal any_event_called
        any_event_called += 1

    emergency = EventBatch.model_validate(all_events())
    await router._dispatch_async(emergency)
    
    assert emergency_start_called == 1
    assert logging_command_called == 1
    assert any_cmd_called == 1
    assert any_event_called == 1