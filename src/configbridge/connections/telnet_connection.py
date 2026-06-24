"""
Telnet Connection

Basic interactive Telnet support using sockets.

Python 3.13 removed telnetlib, so this implementation uses a raw socket.
This is enough for basic testing, but Telnet support can be improved later.
"""

import socket

from configbridge.connections.base_connection import BaseConnection


class TelnetConnection(BaseConnection):
    """
    Basic Telnet connection.

    Telnet is insecure because traffic is not encrypted.
    It is included only for legacy device support.
    """

    def __init__(
        self,
        host: str,
        cli_mode: str,
        username: str = "",
        password: str = "",
        port: int = 23,
    ):
        super().__init__(
            host=host,
            cli_mode=cli_mode,
            username=username,
            password=password,
        )
        self.port = port
        self.client = None

    def connect(self) -> str:
        """
        Open a basic Telnet socket connection.
        """

        try:
            self.client = socket.create_connection(
                (self.host, self.port),
                timeout=10,
            )
            self.client.setblocking(False)
            self.connected = True

            return f"Telnet session opened to {self.host}\n"

        except (socket.error, TimeoutError) as error:
            return f"ERROR: Telnet connection failed: {error}"

    def disconnect(self) -> str:
        """
        Close the Telnet socket.
        """

        self.connected = False

        if self.client is not None:
            self.client.close()
            self.client = None

        return "Telnet connection closed."

    def write(self, data: str) -> None:
        """
        Send raw terminal input to the Telnet session.
        """

        if not self.connected or self.client is None:
            return

        self.client.sendall(data.encode("utf-8", errors="ignore"))

    def read(self) -> str:
        """
        Read currently available Telnet output.
        """

        if not self.connected or self.client is None:
            return ""

        try:
            data = self.client.recv(4096)

            if not data:
                self.connected = False
                return "\nERROR: Telnet session closed by remote host.\n"

            return data.decode("utf-8", errors="ignore")

        except BlockingIOError:
            return ""

        except socket.error as error:
            self.connected = False
            return f"\nERROR: Telnet read failed: {error}\n"