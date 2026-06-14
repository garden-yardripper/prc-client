from prc.command import normalize_command, Command, cmd
from prc import FullUser, IdUser

def test_normalize_command():
    assert normalize_command("h") == ":h"
    assert normalize_command(":h") == ":h"
    
def test_command_payload_and_dangerous():
    c = Command(text="kick all")
    assert c.text == ":kick all"
    assert c.payload == {"command": ":kick all"}
    assert c.dangerous is True
    
def test_cmd_factory():
    # recognized command
    c = cmd.pm(FullUser("Alice", 123), "Hello")
    assert isinstance(c, Command)
    assert c.text == ":pm Alice Hello"
    assert c.dangerous is False
    
    # unrecognized command
    c = cmd.something("Hello", IdUser(456))
    assert isinstance(c, Command)
    assert c.text == ":something Hello 456"