"""
Command Executor

Executes operational discovery commands through the active SessionManager.

Unlike the interactive terminal, this component is intended for automated
workflows such as discovery, validation and future deployment checks.
"""

import time


class CommandExecutor:

    def __init__(self, session_manager):
        self.session_manager = session_manager

    def execute(self, command: str) -> str:
        """
        Execute a command through the active session.
        """

        return self.session_manager.execute_command(command)