import sys

from PySide6.QtWidgets import QApplication

from configbridge.gui.virtual_cli_widget import VirtualCLIWidget


class DummySession:

    def write(self, text):
        print("SEND:", text)


app = QApplication(sys.argv)

widget = VirtualCLIWidget(DummySession())

widget.show()

app.exec()