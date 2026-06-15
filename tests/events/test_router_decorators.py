import pytest

from prc.events.models import CustomCommand, EventBatch, Event
from prc.events.router import Router
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

def test_event_validation():
    emergency = EventBatch.model_validate(emergency_call())
    probe = EventBatch.model_validate(webhook_probe())
    command = EventBatch.model_validate(custom_command())
    
    assert isinstance(emergency, EventBatch)
    assert isinstance(probe, EventBatch)
    assert isinstance(command, EventBatch)
    
    assert isinstance(emergency.events[0], Event)
    assert isinstance(probe.events[0], Event)
    assert isinstance(command.events[0], Event)
    
    assert isinstance(emergency.events[0].emergency_call, EmergencyCall)
    assert isinstance(command.events[0].command, CustomCommand)
    
    with pytest.raises(ValueError):
        emergency.events[0].command
    
    with pytest.raises(ValueError):
        command.events[0].emergency_call
        
async def test_router_command_handlers():
    router = Router()
    
    @router.on.emergency_start()
    def emergency_start(e: Event):
        assert isinstance(e, Event)
        assert e.event_type == "EmergencyCallStarted"
    
    @router.on.command("logging")
    async def logging_command(e: Event):
        assert isinstance(e, Event)
        assert e.event_type == "CustomCommand"
    
    @router.on.any_custom_command()
    def any_cmd(e: Event):
        assert e.event_type == "CustomCommand"
    
    emergency = EventBatch.model_validate(emergency_call())
    command = EventBatch.model_validate(custom_command())
    
    await router.dispatch_async([emergency, command])