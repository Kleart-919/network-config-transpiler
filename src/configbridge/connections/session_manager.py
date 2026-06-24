"""
Session Manager

This module controls the active network session.
"""

from configbridge.connections.ssh_connection import SSHConnection
from configbridge.connections.telnet_connection import TelnetConnection


class SessionManager:
    """
    Coordinates network sessions for the application.
    """

    def __init__(self):
        self.connection = None

    def connect(
        self,
        host: str,
        cli_mode: str,
        protocol: str,
        username: str = "",
        password: str = "",
    ) -> str:
        """
        Create a connection object based on the selected protocol.
        """

        if protocol == "SSH":
            self.connection = SSHConnection(
                host=host,
                cli_mode=cli_mode,
                username=username,
                password=password,
            )
        elif protocol == "Telnet":
            self.connection = TelnetConnection(
                host=host,
                cli_mode=cli_mode,
                username=username,
                password=password,
            )
        else:
            return f"ERROR: Unsupported protocol selected: {protocol}"

        return self.connection.connect()

    def disconnect(self) -> str:
        """
        Disconnect the current active connection.
        """

        if self.connection is None:
            return "ERROR: No active session."

        message = self.connection.disconnect()
        self.connection = None
        return message

    def write(self, data: str) -> None:
        """
        Send raw terminal input to the active connection.
        """

        if self.connection is None:
            return

        self.connection.write(data)

    def read(self) -> str:
        """
        Read currently available output from the active connection.
        """

        if self.connection is None:
            return ""

        return self.connection.read()