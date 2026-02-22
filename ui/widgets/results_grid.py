from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from typing import List, Any

class ResultsGrid(QTableWidget):
    def set_result(self, columns: List[str], rows: List[List[Any]]):
        self.clear()
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns or [])
        self.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                item = QTableWidgetItem("" if val is None else str(val))
                self.setItem(r_idx, c_idx, item)
        self.resizeColumnsToContents()
