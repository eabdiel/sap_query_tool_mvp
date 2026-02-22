from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont

class SQLEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        f = QFont("Consolas")
        f.setPointSize(10)
        self.setFont(f)
        self.setPlaceholderText('Example:\nSELECT * FROM ZAGT_CONSTANTS WHERE MANDT = \'100\' LIMIT 100')
