from configbridge.connections.session_manager import SessionManager

HOST = input("Host: ")
USERNAME = input("Username: ")
PASSWORD = input("Password: ")

manager = SessionManager()

print(
    manager.connect(
        host=HOST,
        cli_mode="Juniper Junos",
        protocol="SSH",
        username=USERNAME,
        password=PASSWORD,
    )
)

print("\n===== EXEC OUTPUT =====\n")

print(manager.execute_command("show interfaces terse"))

print("\n=======================\n")

manager.disconnect()