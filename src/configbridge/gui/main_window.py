from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from configbridge.connections.session_manager import SessionManager
from configbridge.discovery.discovery_manager import DiscoveryManager
from configbridge.discovery.discovery_profile import DiscoveryProfile
from configbridge.gui.terminal_widget import TerminalWidget
from configbridge.gui.virtual_cli_widget import VirtualCLIWidget
from configbridge.parsers.juniper_discovery_parser import JuniperDiscoveryParser
from configbridge.plugins.vendor_manifest import VendorManifest


class DiscoveryWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, discovery_manager, vendor, hostname):
        super().__init__()
        self.discovery_manager = discovery_manager
        self.vendor = vendor
        self.hostname = hostname

    def run(self):
        try:
            inventory = self.discovery_manager.discover(
                vendor=self.vendor,
                hostname=self.hostname,
            )
            self.finished.emit(inventory)
        except Exception as error:
            self.failed.emit(str(error))


class ConfigBridgeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.session_manager = SessionManager()
        self.discovery_manager = DiscoveryManager(self.session_manager)
        self.log_file_path = None
        self.discovery_thread = None
        self.discovery_worker = None

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
        self.discover_button.setEnabled(False)

        self.status_label = QLabel("Status: Disconnected")

        self.terminal = TerminalWidget(
            self.session_manager,
            log_callback=self.write_session_log,
        )

        self.virtual_cli = VirtualCLIWidget(
            self.session_manager,
            log_callback=self.write_session_log,
        )

        self.terminal_tabs = QTabWidget()
        self.terminal_tabs.addTab(self.terminal, "Native Terminal")
        self.terminal_tabs.addTab(self.virtual_cli, "Virtual CLI")

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
        main_layout.addWidget(self.terminal_tabs)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_from_session)
        self.read_timer.start(100)

    def start_session_log(self, host: str, protocol: str, cli_mode: str):
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

        self.start_session_log(host, protocol, cli_mode)

        self.status_label.setText(
            f"Status: Connecting | {protocol} | {cli_mode} | {host}"
        )

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
            self.discover_button.setEnabled(False)
            self.write_session_log(f"\n[ConfigBridge] Connection failed: {message}\n")
            return

        self.status_label.setText(
            f"Status: Connected | {protocol} | {cli_mode} | {host}"
        )

        self.discover_button.setEnabled(True)

        self.virtual_cli.write_output(
            f"[ConfigBridge] Connected to {host} using {protocol}.\n"
        )

        self.write_session_log("\n[ConfigBridge] Connection successful.\n")

    def handle_disconnect_clicked(self):
        message = self.session_manager.disconnect()

        self.status_label.setText("Status: Disconnected")
        self.discover_button.setEnabled(False)

        self.terminal.write_output(f"\n[ConfigBridge] {message}\n")
        self.write_session_log(f"\n[ConfigBridge] {message}\n")
        self.write_session_log(f"Ended: {datetime.now()}\n")

    def read_from_session(self):
        output = self.session_manager.read()

        if not output:
            return

        active_widget = self.terminal_tabs.currentWidget()

        if hasattr(active_widget, "write_output"):
            active_widget.write_output(output)

    def handle_discover_clicked(self):
        if not self.session_manager.is_connected():
            self.terminal.write_output(
                "\n[ConfigBridge] ERROR: Connect to a device before discovery.\n"
            )
            return

        self.discover_button.setEnabled(False)
        self.status_label.setText("Status: Discovering device...")

        profile = DiscoveryProfile(
            vendor_name="Juniper Junos",
            commands={
                "interfaces": "show interfaces terse | no-more",
            },
        )

        manifest = VendorManifest(
            name="Juniper Junos",
            discovery_profile=profile,
            discovery_parser=JuniperDiscoveryParser(),
            configuration_parser=None,
            configuration_generator=None,
        )

        self.discovery_thread = QThread()
        self.discovery_worker = DiscoveryWorker(
            self.discovery_manager,
            manifest,
            self.host_input.text().strip(),
        )

        self.discovery_worker.moveToThread(self.discovery_thread)

        self.discovery_thread.started.connect(self.discovery_worker.run)
        self.discovery_worker.finished.connect(self.handle_discovery_finished)
        self.discovery_worker.failed.connect(self.handle_discovery_failed)

        self.discovery_worker.finished.connect(self.discovery_thread.quit)
        self.discovery_worker.failed.connect(self.discovery_thread.quit)

        self.discovery_thread.finished.connect(self.discovery_thread.deleteLater)

        self.discovery_thread.start()

    def handle_discovery_finished(self, inventory):
        self.virtual_cli.runtime.set_inventory(inventory)
        self.virtual_cli.connected_vendor = inventory.vendor

        self.virtual_cli.write_output(
            f"\n[ConfigBridge] Discovery loaded {len(inventory.interfaces)} interfaces.\n"
        )

        self.status_label.setText(
            f"Status: Discovery complete | {len(inventory.interfaces)} interfaces"
        )

        self.discover_button.setEnabled(True)

    def handle_discovery_failed(self, error):
        self.terminal.write_output(
            f"\n[ConfigBridge] Discovery failed: {error}\n"
        )

        self.status_label.setText("Status: Discovery failed")
        self.discover_button.setEnabled(True)