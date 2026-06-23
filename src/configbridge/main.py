import sys

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from configbridge.connections.session_manager import SessionManager


class ConfigBridgeWindow(QMainWindow):
    """
    Main ConfigBridge application window.

    Phase 1 focuses on the Network Session Manager interface.
    """

    def __init__(self):
        super().__init__()

        # Create one session manager instance for the lifetime of the window.
        self.session_manager = SessionManager()

        self.setWindowTitle("ConfigBridge")
        self.setMinimumSize(900, 600)

        self.vendor_dropdown = QComboBox()
        self.vendor_dropdown.addItems(
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

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.handle_connect_clicked)

        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("Session output will appear here...")

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command...")

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_send_clicked)

        main_layout = QVBoxLayout()

        connection_layout = QHBoxLayout()
        connection_layout.addWidget(QLabel("Vendor:"))
        connection_layout.addWidget(self.vendor_dropdown)
        connection_layout.addWidget(QLabel("Protocol:"))
        connection_layout.addWidget(self.protocol_dropdown)
        connection_layout.addWidget(QLabel("Host/IP:"))
        connection_layout.addWidget(self.host_input)
        connection_layout.addWidget(self.connect_button)

        command_layout = QHBoxLayout()
        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.send_button)

        main_layout.addLayout(connection_layout)
        main_layout.addWidget(QLabel("Session Output"))
        main_layout.addWidget(self.output_area)
        main_layout.addLayout(command_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def handle_connect_clicked(self):
        """
        Handle the Connect button click.

        This currently calls the simulated SessionManager connection method.
        Real SSH/Telnet connection logic will be added later.
        """

        vendor = self.vendor_dropdown.currentText()
        protocol = self.protocol_dropdown.currentText()
        host = self.host_input.text().strip()

        if not host:
            self.output_area.appendPlainText("Please enter a host/IP address.")
            return

        message = self.session_manager.connect(
            host=host,
            vendor=vendor,
            protocol=protocol,
        )

        self.output_area.appendPlainText(message)

    def handle_send_clicked(self):
        """
        Handle the Send button click.

        This currently sends the command to the simulated SessionManager.
        """

        command = self.command_input.text().strip()

        if not command:
            return

        self.output_area.appendPlainText(f"> {command}")

        response = self.session_manager.send_command(command)
        self.output_area.appendPlainText(response)

        self.command_input.clear()


def main():
    app = QApplication(sys.argv)
    window = ConfigBridgeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()