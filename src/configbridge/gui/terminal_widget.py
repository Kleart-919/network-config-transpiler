from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit

from configbridge.connections.session_manager import SessionManager

class TerminalWidget(QPlainTextEdit):
    """
    Simple terminal-style widget.

    The switch echoes typed characters back, so this widget does not display
    typed characters locally. It only displays what comes back from the session.
    """

    def __init__(self, session_manager: SessionManager, log_callback=None):
        super().__init__()
        self.session_manager = session_manager
        self.log_callback = log_callback

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
        Send keystrokes to the active session.
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
        Display output received from the switch and write it to the session log.
        """

        if not text:
            return

        if self.log_callback:
            self.log_callback(text)

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