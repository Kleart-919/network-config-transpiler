"""
Base Connection

This module defines the common interface that all connection types should follow.
"""


class BaseConnection:
    """
    Base class for network connection types.
    """

    def __init__(self, host: str, cli_mode: str, username: str = "", password: str = ""):
        self.host = host
        self.cli_mode = cli_mode
        self.username = username
        self.password = password
        self.connected = False

    def connect(self) -> str:
        raise NotImplementedError("Connection classes must implement connect().")

    def disconnect(self) -> str:
        raise NotImplementedError("Connection classes must implement disconnect().")

    def write(self, data: str) -> None:
        raise NotImplementedError("Connection classes must implement write().")

    def read(self) -> str:
        raise NotImplementedError("Connection classes must implement read().")
    def execute_command(self, command: str) -> str:
        raise NotImplementedError