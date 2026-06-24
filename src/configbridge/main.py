import sys

from PySide6.QtCore import Qt
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
    A simple terminal-like widget.

    This is not a full terminal emulator yet.
    It allows the user to type commands directly into the terminal area.
    """

    def __init__(self, session_manager: SessionManager):
        super().__init__()

        self.session_manager = session_manager
        self.prompt = "> "
        self.current_input_start = 0

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

        self.setPlainText(self.prompt)
        self.moveCursor(QTextCursor.End)
        self.current_input_start = len(self.toPlainText())

    def keyPressEvent(self, event):
        """
        Handle Enter so typed text is sent as a command.
        """

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            command = self._get_current_command().strip()
            self.appendPlainText("")

            if command:
                response = self.session_manager.send_command(command)
                self.appendPlainText(response)

            self.appendPlainText(self.prompt)
            self.moveCursor(QTextCursor.End)
            self.current_input_start = len(self.toPlainText())
            return

        super().keyPressEvent(event)

    def write_line(self, text: str):
        """
        Write a line to the terminal.
        """

        self.appendPlainText(text)
        self.appendPlainText(self.prompt)
        self.moveCursor(QTextCursor.End)
        self.current_input_start = len(self.toPlainText())

    def _get_current_command(self) -> str:
        """
        Return only the text typed after the current prompt.
        """

        text = self.toPlainText()
        return text[self.current_input_start:]


class ConfigBridgeWindow(QMainWindow):
    """
    Main ConfigBridge application window.

    Phase 1 focuses on the Network Session Manager interface.
    """

    def __init__(self):
        super().__init__()

        self.session_manager = SessionManager()

        self.setWindowTitle("ConfigBridge")
        self.setMinimumSize(900, 600)

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

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.handle_connect_clicked)

        self.terminal = TerminalWidget(self.session_manager)

        main_layout = QVBoxLayout()

        connection_layout = QHBoxLayout()
        connection_layout.addWidget(QLabel("CLI Mode:"))
        connection_layout.addWidget(self.cli_mode_dropdown)
        connection_layout.addWidget(QLabel("Protocol:"))
        connection_layout.addWidget(self.protocol_dropdown)
        connection_layout.addWidget(QLabel("Host/IP:"))
        connection_layout.addWidget(self.host_input)
        connection_layout.addWidget(self.connect_button)

        main_layout.addLayout(connection_layout)
        main_layout.addWidget(self.terminal)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def handle_connect_clicked(self):
        """
        Handle the Connect button click.

        This currently connects to the simulated SessionManager.
        """

        cli_mode = self.cli_mode_dropdown.currentText()
        protocol = self.protocol_dropdown.currentText()
        host = self.host_input.text().strip()

        if not host:
            self.terminal.write_line("ERROR: Please enter a host/IP address.")
            return

        message = self.session_manager.connect(
            host=host,
            cli_mode=cli_mode,
            protocol=protocol,
        )

        self.terminal.write_line(message)


def main():
    app = QApplication(sys.argv)
    window = ConfigBridgeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()