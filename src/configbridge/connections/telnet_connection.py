"""
Telnet Connection

This module will handle Telnet-based network sessions.

For now, this is simulated. Real Telnet logic will be added later.
"""

from configbridge.connections.base_connection import BaseConnection


class TelnetConnection(BaseConnection):
    def connect(self) -> str:
        self.connected = True
        return f"Telnet connection established (simulated) to {self.host} using CLI mode [{self.cli_mode}]"

    def disconnect(self) -> str:
        self.connected = False
        return "Telnet connection closed (simulated)"

    def send_command(self, command: str) -> str:
        if not self.connected:
            return "ERROR: No active Telnet session."

        return f"Simulated Telnet output for: {command}"