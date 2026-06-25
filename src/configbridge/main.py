import sys

from PySide6.QtWidgets import QApplication

from configbridge.gui.main_window import ConfigBridgeWindow


def main():
    app = QApplication(sys.argv)

    window = ConfigBridgeWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()