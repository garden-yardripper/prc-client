import prc
from prc.command import cmd
from prc.policy import CommandPolicy

# Only allow hint and message commands
# Blacklist set takes priority over whitelist
policy = CommandPolicy(whitelist={"h", "hint", "m", "message"}, blacklist={"kick"})

with prc.v2.Client(server_key="...", policy=policy) as client:
    hint_preview = policy.preview_command(cmd.h("Hello World!"))
    wanted_preview = policy.preview_command(cmd.wanted("Alice"))
    
    if hint_preview.allowed:
        client.send_command(hint_preview.command)
    
    if wanted_preview.allowed:
        # This will not run
        client.send_command(wanted_preview.command)
    else:
        print("Command disallowed! Reason:", wanted_preview.reason)