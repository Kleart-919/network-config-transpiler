"""
SSH Connection

This module handles interactive SSH sessions using Paramiko.
"""

import socket
import time

import paramiko

from configbridge.connections.base_connection import BaseConnection


class SSHConnection(BaseConnection):
    """
    Interactive SSH connection.

    Paramiko authenticates first, then opens an interactive shell.
    After login, the user can type directly into the terminal.
    """

    def __init__(
        self,
        host: str,
        cli_mode: str,
        username: str,
        password: str,
        port: int = 22,
    ):
        super().__init__(
            host=host,
            cli_mode=cli_mode,
            username=username,
            password=password,
        )
        self.port = port
        self.client = None
        self.channel = None

    def connect(self) -> str:
        """
        Connect to the SSH device and open an interactive shell.
        """

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                look_for_keys=False,
                allow_agent=False,
                timeout=10,
                auth_timeout=10,
                banner_timeout=10,
            )

            self.channel = self.client.invoke_shell()
            self.channel.settimeout(0.0)
            self.connected = True

            time.sleep(0.5)
            initial_output = self.read()

            # Disable paging for Cisco-style CLI sessions.
            # This prevents --More-- prompts from interrupting long command output.
            if self.cli_mode == "Cisco IOS":
                self.write("terminal length 0\n")
                time.sleep(0.5)
                initial_output += self.read()

            return initial_output or f"SSH interactive shell opened to {self.host}"

        except paramiko.AuthenticationException:
            return "ERROR: SSH authentication failed. Check username/password."
        except (paramiko.SSHException, socket.error, TimeoutError) as error:
            return f"ERROR: SSH connection failed: {error}"

    def disconnect(self) -> str:
        self.connected = False

        if self.channel is not None:
            self.channel.close()
            self.channel = None

        if self.client is not None:
            self.client.close()
            self.client = None

        return "SSH connection closed."

    def write(self, data: str) -> None:
        if not self.connected or self.channel is None:
            return

        self.channel.send(data)

    def read(self) -> str:
        if not self.connected or self.channel is None:
            return ""

        output = ""

        while self.channel.recv_ready():
            data = self.channel.recv(4096)
            output += data.decode(errors="ignore")

        return output
    
    def execute_command(self, command: str) -> str:
    
        if not self.connected or self.client is None:
            return ""

        try:
            stdin, stdout, stderr = self.client.exec_command(command)

            output = stdout.read().decode(errors="ignore")
            errors = stderr.read().decode(errors="ignore")

            return output + errors

        except Exception as error:
            return f"ERROR: {error}"