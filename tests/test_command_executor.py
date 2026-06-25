from configbridge.discovery.command_executor import CommandExecutor
from configbridge.connections.session_manager import SessionManager


manager = SessionManager()

print(
    "CommandExecutor created successfully."
)

executor = CommandExecutor(manager)

print("Ready.")