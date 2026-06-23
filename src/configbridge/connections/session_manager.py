"""
Session Manager

This module provides a vendor-independent interface for creating and managing
network sessions.

The GUI should not directly interact with SSH, Telnet, Serial, Netmiko, or
Scrapli. The GUI should call SessionManager, and SessionManager should decide
how the connection is handled.
"""


class SessionManager:
    """
    Main connection abstraction for ConfigBridge.

    This is currently a simulated session manager. Real SSH/Telnet logic will be
    added later.
    """

    def __init__(self):
        # These values store the current session state.
        self.connected = False
        self.host = None
        self.vendor = None
        self.protocol = None

    def connect(self, host: str, vendor: str, protocol: str) -> str:
        """
        Simulate a connection to a network device.

        Later, this method will create a real SSH/Telnet session.
        """

        self.host = host
        self.vendor = vendor
        self.protocol = protocol
        self.connected = True

        return f"Connected (simulated) to {host} using {protocol} [{vendor}]"

    def disconnect(self) -> str:
        """
        Simulate disconnecting from the current session.
        """

        self.connected = False
        self.host = None
        self.vendor = None
        self.protocol = None

        return "Disconnected (simulated)"

    def send_command(self, command: str) -> str:
        """
        Simulate sending a command to a connected device.
        """

        if not self.connected:
            return "ERROR: No active session."

        return f"Simulated device output for: {command}"