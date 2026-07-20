import prc
from prc import cmd

# You can use the `cmd` factory to build commands to send to the server.
# This has many advantages over manually constructing commands with strings (although you still can).

# For example, the factory has built-in type checking and required parameters for recognized in-game commands 
# and automatic user object conversion, while still allowing you to create custom commands with the factory.
# This prevents tons of common mistakes, saves you time, and makes your code more readable.

# Let's look at an example:

with prc.v2.Client(server_key="...") as client:
    # Let's say we want to send a private message to a user named "Alice".
    # We can use the `cmd.pm` factory method to create the command and parse the user object for us.
    
    user = prc.FullUser("Alice", 123)
    command = cmd.pm(user, "Hello World!")
    
    # This will create a Command object.
    print(command.text)  # Output: ":pm Alice Hello World!"
    
    # Now we can send this command to the server using the client.
    client.send_command(command)
    
    # You can even pass in multiple users for supported commands, and the factory will handle formatting correctly:
    client.send_command(cmd.kick(("Alice", "Bob", "Charlie"), reason="Breaking the rules!")) 
    
    # You can also create entirely custom commands:
    custom_command = cmd.hello("You can pass in", "any parameters here!")
    print(custom_command.text)  # Output: ":hello You can pass in any parameters here!"
