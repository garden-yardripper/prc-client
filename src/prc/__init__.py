"""`prc-client`: A flexible, feature-rich Python API client for the ER:LC private server API."""

from . import v1, v2, utils, exceptions
from .users import FullUser, UsernameUser, IdUser
from .command import cmd
from .policy import CommandPolicy

__all__ = [
    "v1", "v2", "utils", "exceptions",
    "FullUser", "UsernameUser", "IdUser",
    "cmd", "CommandPolicy"
]

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())