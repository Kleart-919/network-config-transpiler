"""
Base Connection

This module defines the common interface that all connection types should follow.
"""


class BaseConnection:
    """
    Base class for network connection types.
    """

    def __init__(self, host: str, cli_mode: str):
        self.host = host
        self.cli_mode = cli_mode
        self.connected = False

    def connect(self) -> str:
        raise NotImplementedError("Connection classes must implement connect().")

    def disconnect(self) -> str:
        raise NotImplementedError("Connection classes must implement disconnect().")

    def send_command(self, command: str) -> str:
        raise NotImplementedError("Connection classes must implement send_command().")