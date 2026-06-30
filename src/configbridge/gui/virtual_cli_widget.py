from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QLineEdit,
)

from PySide6.QtGui import QTextCursor
from configbridge.runtime.runtime_engine import RuntimeEngine


class VirtualCLIWidget(QWidget):
    """
    Vendor-neutral CLI.

    The user types commands in their preferred CLI.
    ConfigBridge translates them before sending them.
    """

    def __init__(self, session_manager, log_callback=None):
        super().__init__()

        self.session_manager = session_manager
        self.log_callback = log_callback

        self.runtime = RuntimeEngine()

        self.cli_mode = "Cisco IOS"
        self.connected_vendor = "Juniper Junos"

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)

        self.input = QLineEdit()

        self.input.returnPressed.connect(
            self.execute_command
        )

        layout = QVBoxLayout()

        layout.addWidget(self.output)
        layout.addWidget(self.input)

        self.setLayout(layout)

    def execute_command(self):

        command = self.input.text().strip()

        if not command:
            return

        translated = self.runtime.translate(command)

        self.write_output(
            f"> {command}\n"
        )

        self.session_manager.write(
            translated + "\n"
        )

        self.input.clear()

    def write_output(self, text):

        if not text:
            return

        text = self.runtime.virtualize_output(text)

        if self.log_callback:
            self.log_callback(text)

        cursor = self.output.textCursor()

        cursor.movePosition(QTextCursor.End)

        cursor.insertText(text)

        self.output.setTextCursor(cursor)

        self.output.ensureCursorVisible()