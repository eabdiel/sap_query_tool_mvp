import sys
from ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
