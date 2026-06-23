"""
Session Manager

This module controls the active network session.

The GUI communicates with SessionManager only. SessionManager then chooses the
correct connection class, such as SSHConnection or TelnetConnection.
"""

from configbridge.connections.ssh_connection import SSHConnection
from configbridge.connections.telnet_connection import TelnetConnection


class SessionManager:
    """
    Coordinates network sessions for the application.
    """

    def __init__(self):
        self.connection = None

    def connect(self, host: str, cli_mode: str, protocol: str) -> str:
        """
        Create a connection object based on the selected protocol.
        """

        if protocol == "SSH":
            self.connection = SSHConnection(host=host, cli_mode=cli_mode)
        elif protocol == "Telnet":
            self.connection = TelnetConnection(host=host, cli_mode=cli_mode)
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

    def send_command(self, command: str) -> str:
        """
        Send a command through the active connection.
        """

        if self.connection is None:
            return "ERROR: No active session."

        return self.connection.send_command(command)