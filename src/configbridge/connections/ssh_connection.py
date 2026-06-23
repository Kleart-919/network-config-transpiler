"""
SSH Connection

This module will handle SSH-based network sessions.

For now, this is simulated. Real SSH logic will be added later using Netmiko or
Scrapli.
"""

from configbridge.connections.base_connection import BaseConnection


class SSHConnection(BaseConnection):
    def connect(self) -> str:
        self.connected = True
        return f"SSH connection established (simulated) to {self.host} using CLI mode [{self.cli_mode}]"

    def disconnect(self) -> str:
        self.connected = False
        return "SSH connection closed (simulated)"

    def send_command(self, command: str) -> str:
        if not self.connected:
            return "ERROR: No active SSH session."

        return f"Simulated SSH output for: {command}"