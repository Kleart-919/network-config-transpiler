import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor
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


class TerminalWidget(QPlainTextEdit):
    """
    Simple terminal-style widget.

    The switch echoes typed characters back to us, so this widget does NOT
    display typed characters locally. It only displays what comes back from
    the SSH session.

    It also interprets basic terminal control characters such as backspace.
    """

    def __init__(self, session_manager: SessionManager):
        super().__init__()
        self.session_manager = session_manager

        self.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #111111;
                color: #eeeeee;
                font-family: Consolas, monospace;
                font-size: 13px;
            }
            """
        )

        self.setPlaceholderText("Terminal session output will appear here...")

    def keyPressEvent(self, event):
        """
        Send keystrokes to the switch.

        Do not print typed characters locally. Cisco echoes them back.
        """

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.session_manager.write("\n")
            return

        if event.key() == Qt.Key_Backspace:
            self.session_manager.write("\x7f")
            return

        text = event.text()

        if text:
            self.session_manager.write(text)
            return

        super().keyPressEvent(event)

    def write_output(self, text: str):
        """
        Display output received from the switch.

        This handles simple terminal behaviour:
        - backspace deletes the previous visible character
        - bell is ignored
        - carriage return is ignored
        """

        if not text:
            return

        self.moveCursor(QTextCursor.End)
        cursor = self.textCursor()

        for char in text:
            if char == "\x07":
                continue

            if char == "\r":
                continue

            if char == "\x08":
                cursor.deletePreviousChar()
                continue

            cursor.insertText(char)

        self.setTextCursor(cursor)
        self.moveCursor(QTextCursor.End)


class ConfigBridgeWindow(QMainWindow):
    """
    Main ConfigBridge application window.
    """

    def __init__(self):
        super().__init__()

        self.session_manager = SessionManager()

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

        self.terminal = TerminalWidget(self.session_manager)

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

        main_layout.addLayout(connection_layout)
        main_layout.addWidget(self.terminal)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_from_session)
        self.read_timer.start(100)

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

    def handle_disconnect_clicked(self):
        message = self.session_manager.disconnect()
        self.terminal.write_output(f"\n[ConfigBridge] {message}\n")

    def read_from_session(self):
        output = self.session_manager.read()

        if output:
            self.terminal.write_output(output)


def main():
    app = QApplication(sys.argv)
    window = ConfigBridgeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()