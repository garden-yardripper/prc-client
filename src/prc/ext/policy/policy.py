from prc.v2.command import normalize_command

class CommandPolicy:
    def __init__(self, allowed: set[str], *, max_length: int = 120) -> None:
        self.allowed = {normalize_command(cmd) for cmd in allowed}
        self.max_length = max_length
    
    