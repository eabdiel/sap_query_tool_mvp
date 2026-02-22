from __future__ import annotations
import os
from typing import List

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox, QLabel, QSplitter, QTextEdit
)
from PySide6.QtCore import Qt

from storage.io import load_json, save_json, DEFAULT_PROFILES_PATH
from models.profile import ConnectionProfile
from ui.profile_dialog import ProfileDialog
from ui.widgets.sql_editor import SQLEditor
from ui.widgets.results_grid import ResultsGrid
from runners.rfc_runner import RfcQueryRunner, RFCBackendError
from runners.hana_runner import HanaQueryRunner, HanaBackendError

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAP Query Tool (MVP)")
        self.resize(1200, 720)

        self.profiles_path = DEFAULT_PROFILES_PATH
        self.profiles: List[ConnectionProfile] = []
        self._load_profiles()

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        # Top toolbar row
        top = QHBoxLayout()
        layout.addLayout(top)

        top.addWidget(QLabel("Profile"))
        self.cb_profile = QComboBox()
        for p in self.profiles:
            self.cb_profile.addItem(p.name)
        top.addWidget(self.cb_profile)

        self.btn_edit_profile = QPushButton("Edit profile")
        top.addWidget(self.btn_edit_profile)

        top.addWidget(QLabel("Runner"))
        self.cb_runner = QComboBox()
        self.cb_runner.addItems(["RFC (SAP)", "HANA (DB)"])
        top.addWidget(self.cb_runner)

        top.addWidget(QLabel("RFC mode"))
        self.cb_rfc_mode = QComboBox()
        self.cb_rfc_mode.addItems([RfcQueryRunner.MODE_RFC_READ_TABLE, RfcQueryRunner.MODE_Z_SRE_QUERY_EXEC])
        top.addWidget(self.cb_rfc_mode)

        self.btn_run = QPushButton("Run")
        top.addWidget(self.btn_run)

        top.addStretch(1)

        # Splitter: editor and results
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter, 1)

        self.editor = SQLEditor()
        splitter.addWidget(self.editor)

        bottom = QWidget()
        bl = QVBoxLayout(bottom)
        splitter.addWidget(bottom)

        self.grid = ResultsGrid()
        bl.addWidget(self.grid, 3)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Messages / warnings will appear here...")
        bl.addWidget(self.log, 1)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        # Wiring
        self.btn_edit_profile.clicked.connect(self.edit_profile)
        self.btn_run.clicked.connect(self.run_query)
        self.cb_runner.currentIndexChanged.connect(self._sync_controls)
        self._sync_controls()

        # Default query
        if not self.editor.toPlainText().strip():
            self.editor.setPlainText("SELECT * FROM ZAGT_CONSTANTS WHERE MANDT = '100' LIMIT 100")

    def _sync_controls(self):
        is_rfc = (self.cb_runner.currentText().startswith("RFC"))
        self.cb_rfc_mode.setEnabled(is_rfc)

    def _load_profiles(self):
        data = load_json(self.profiles_path) or {}
        self.profiles = [ConnectionProfile.from_dict(p) for p in (data.get("profiles") or [])]
        if not self.profiles:
            from models.profile import RFCProfile, HANAProfile
            self.profiles = [ConnectionProfile("Default", RFCProfile(), HANAProfile())]

    def _save_profiles(self):
        save_json(self.profiles_path, {"profiles": [p.to_dict() for p in self.profiles]})

    def current_profile(self) -> ConnectionProfile:
        idx = self.cb_profile.currentIndex()
        idx = max(0, idx)
        idx = min(idx, len(self.profiles) - 1)
        return self.profiles[idx]

    def edit_profile(self):
        p = self.current_profile()
        dlg = ProfileDialog(p, self)
        if dlg.exec():
            new_p = dlg.get_profile()
            idx = self.cb_profile.currentIndex()
            self.profiles[idx] = new_p
            self.cb_profile.setItemText(idx, new_p.name)
            self._save_profiles()
            self._append_log(f"Saved profile: {new_p.name}")

    def _append_log(self, msg: str):
        self.log.append(msg)

    def run_query(self):
        sql = self.editor.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "No SQL", "Please enter a SELECT statement.")
            return

        profile = self.current_profile()
        runner_choice = self.cb_runner.currentText()

        try:
            if runner_choice.startswith("RFC"):
                mode = self.cb_rfc_mode.currentText()
                runner = RfcQueryRunner(profile=profile, mode=mode, max_rows=2000)

                # Complex WHERE warning only for RFC_READ_TABLE
                if mode == RfcQueryRunner.MODE_RFC_READ_TABLE:
                    is_complex, reason = runner.precheck_for_ui(sql)
                    if is_complex:
                        QMessageBox.warning(
                            self,
                            "Complex WHERE detected",
                            "Your WHERE clause looks complex for RFC_READ_TABLE (which is limited).\n\n"
                            f"Detected: {reason}\n\n"
                            "Suggestion: switch RFC mode to Z_SRE_QUERY_EXEC for complex filters."
                        )
                        self._append_log(f"Warning (RFC_READ_TABLE): complex WHERE detected -> {reason}")

                result = runner.run(sql)

            else:
                runner = HanaQueryRunner(profile=profile, default_schema=profile.hana.schema)
                result = runner.run(sql)

            self.grid.set_result(result.columns, result.rows)
            self._append_log(f"{result.message} | rows={result.rowcount} | runtime_ms={result.runtime_ms}")

        except Exception as e:
            QMessageBox.critical(self, "Query error", str(e))
            self._append_log(f"ERROR: {e}")
