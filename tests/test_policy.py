import pytest
from prc.command import Command
from prc.exceptions import CommandPolicyViolation
from prc.policy import CommandPolicy
from prc.v2.client import AsyncClient, Client
from prc.v2 import cmd

def test_policy_params():
    policy = CommandPolicy(
        whitelist={"h", ":pm", "kick"},
        blacklist={"ban", "m", ":kick"},
        max_length=30
    )
    
    hint = policy.preview_command("h Hello!")
    assert hint.allowed
    assert isinstance(hint.command, Command)
    assert hint.command.text == ":h Hello!"
    
    kick = policy.preview_command(":kick player reason")
    assert not kick.allowed
    assert kick.reason == "Command blacklisted"
    
    random = policy.preview_command(":random command")
    assert not random.allowed
    assert random.reason == "Command not whitelisted"
    
    long = policy.preview_command(":pm long command above 30 characters")
    assert not long.allowed
    assert long.reason == "Command too long"
    
    with pytest.raises(CommandPolicyViolation):
        policy.preview_command(":m banned", raise_for_status=True)
        
def test_policy_client_raises():
    policy = CommandPolicy(blacklist={"m"})
    client = Client("server-key", policy=policy)
    
    with pytest.raises(CommandPolicyViolation):
        client.send_command(cmd.m("message"))
        
async def test_policy_async_client_raises():
    policy = CommandPolicy(blacklist={"m"})
    client = AsyncClient("server-key", policy=policy)
    
    with pytest.raises(CommandPolicyViolation):
        await client.send_command(cmd.m("message"))