import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class ConfigBridgeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ConfigBridge")
        self.setMinimumSize(800, 500)

        label = QLabel("ConfigBridge - Phase 1: Network Session Manager")
        label.setStyleSheet("font-size: 20px; padding: 20px;")
        self.setCentralWidget(label)


def main():
    app = QApplication(sys.argv)
    window = ConfigBridgeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()