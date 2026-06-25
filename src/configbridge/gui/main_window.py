from datetime import datetime
from pathlib import Path
from configbridge.discovery.discovery_manager import DiscoveryManager
from configbridge.discovery.discovery_profile import DiscoveryProfile
from configbridge.parsers.juniper_discovery_parser import JuniperDiscoveryParser
from configbridge.plugins.vendor_manifest import VendorManifest

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from configbridge.connections.session_manager import SessionManager
from configbridge.gui.terminal_widget import TerminalWidget

class ConfigBridgeWindow(QMainWindow):
    """
    Main ConfigBridge application window.
    """

    def __init__(self):
        super().__init__()

        self.session_manager = SessionManager()
        self.discovery_manager = DiscoveryManager(self.session_manager)
        self.log_file_path = None

        self.setWindowTitle("ConfigBridge")
        self.setMinimumSize(1000, 600)

        self.cli_mode_dropdown = QComboBox()
        self.cli_mode_dropdown.addItems(
            [
                "Cisco IOS",
                "Juniper Junos",
                "Cisco Nexus NX-OS",
                "Aruba",
                "HP",
                "Arista EOS",
            ]
        )

        self.protocol_dropdown = QComboBox()
        self.protocol_dropdown.addItems(["SSH", "Telnet"])

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Device IP address or hostname")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.handle_connect_clicked)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.handle_disconnect_clicked)

        self.discover_button = QPushButton("Discover Device")
        self.discover_button.clicked.connect(self.handle_discover_clicked)

        self.status_label = QLabel("Status: Disconnected")

        self.terminal = TerminalWidget(
            self.session_manager,
            log_callback=self.write_session_log,
        )

        main_layout = QVBoxLayout()

        connection_layout = QHBoxLayout()
        connection_layout.addWidget(QLabel("CLI Mode:"))
        connection_layout.addWidget(self.cli_mode_dropdown)
        connection_layout.addWidget(QLabel("Protocol:"))
        connection_layout.addWidget(self.protocol_dropdown)
        connection_layout.addWidget(QLabel("Host/IP:"))
        connection_layout.addWidget(self.host_input)
        connection_layout.addWidget(QLabel("Username:"))
        connection_layout.addWidget(self.username_input)
        connection_layout.addWidget(QLabel("Password:"))
        connection_layout.addWidget(self.password_input)
        connection_layout.addWidget(self.connect_button)
        connection_layout.addWidget(self.disconnect_button)
        connection_layout.addWidget(self.discover_button)

        main_layout.addLayout(connection_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.terminal)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_from_session)
        self.read_timer.start(100)

    def start_session_log(self, host: str, protocol: str, cli_mode: str):
        """
        Create a new log file for the current session.
        """

        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_host = host.replace(".", "_").replace("/", "_").replace("\\", "_")

        self.log_file_path = logs_dir / f"session_{safe_host}_{timestamp}.log"

        self.write_session_log("=" * 70 + "\n")
        self.write_session_log("ConfigBridge Session Log\n")
        self.write_session_log(f"Started: {datetime.now()}\n")
        self.write_session_log(f"Host: {host}\n")
        self.write_session_log(f"Protocol: {protocol}\n")
        self.write_session_log(f"CLI Mode: {cli_mode}\n")
        self.write_session_log("=" * 70 + "\n\n")

    def write_session_log(self, text: str):
        """
        Append text to the current session log file.
        """

        if self.log_file_path is None:
            return

        with open(self.log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(text)

    def handle_connect_clicked(self):
        cli_mode = self.cli_mode_dropdown.currentText()
        protocol = self.protocol_dropdown.currentText()
        host = self.host_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not host:
            self.terminal.write_output("ERROR: Please enter a host/IP address.\n")
            return

        if protocol == "SSH" and (not username or not password):
            self.terminal.write_output(
                "ERROR: SSH requires username and password for this implementation.\n"
            )
            return

        self.start_session_log(
            host=host,
            protocol=protocol,
            cli_mode=cli_mode,
        )

        self.status_label.setText(f"Status: Connecting | {protocol} | {cli_mode} | {host}")

        self.terminal.write_output(
            f"\n[ConfigBridge] Connecting to {host} using {protocol} "
            f"with CLI mode {cli_mode}...\n"
        )

        message = self.session_manager.connect(
            host=host,
            cli_mode=cli_mode,
            protocol=protocol,
            username=username,
            password=password,
        )

        if message:
            self.terminal.write_output(message + "\n")

        if message.startswith("ERROR"):
            self.status_label.setText("Status: Disconnected")
            self.write_session_log(f"\n[ConfigBridge] Connection failed: {message}\n")
        else:
            self.status_label.setText(
                f"Status: Connected | {protocol} | {cli_mode} | {host}"
            )
            self.write_session_log("\n[ConfigBridge] Connection successful.\n")

    def handle_disconnect_clicked(self):
        message = self.session_manager.disconnect()

        self.status_label.setText("Status: Disconnected")

        self.terminal.write_output(f"\n[ConfigBridge] {message}\n")
        self.write_session_log(f"\n[ConfigBridge] {message}\n")
        self.write_session_log(f"Ended: {datetime.now()}\n")

    def read_from_session(self):
        output = self.session_manager.read()

        if output:
            self.terminal.write_output(output)

    def handle_discover_clicked(self):

        profile = DiscoveryProfile(
            vendor_name="Juniper Junos",
            commands={
                "interfaces": "show interfaces terse",
            },
        )

        manifest = VendorManifest(
            name="Juniper Junos",
            discovery_profile=profile,
            discovery_parser=JuniperDiscoveryParser(),
            configuration_parser=None,
            configuration_generator=None,
        )

        inventory = self.discovery_manager.discover(
            vendor=manifest,
            hostname=self.host_input.text().strip(),
        )

        self.terminal.write_output("\n===== DEVICE INVENTORY =====\n")
        self.terminal.write_output(str(inventory.to_dict()))
        self.terminal.write_output("\n============================\n")