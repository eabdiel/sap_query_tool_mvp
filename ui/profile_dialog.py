from __future__ import annotations
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox, QGroupBox, QMessageBox
)
from models.profile import ConnectionProfile, RFCProfile, HANAProfile

class ProfileDialog(QDialog):
    def __init__(self, profile: ConnectionProfile, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Connection Profile")
        self.profile = profile

        layout = QVBoxLayout(self)

        # Name
        row = QHBoxLayout()
        row.addWidget(QLabel("Profile name"))
        self.ed_name = QLineEdit(profile.name)
        row.addWidget(self.ed_name)
        layout.addLayout(row)

        # RFC group
        g_rfc = QGroupBox("RFC (SSO via sap_connector.py)")
        lr = QVBoxLayout(g_rfc)

        def add_line(label, value):
            r = QHBoxLayout()
            r.addWidget(QLabel(label))
            e = QLineEdit(value)
            r.addWidget(e)
            lr.addLayout(r)
            return e

        self.ed_system = add_line("System (e.g. SMP/SMD)", profile.rfc.system)
        self.ed_client = add_line("Client", profile.rfc.client)
        self.ed_sysnr  = add_line("Sysnr", profile.rfc.sysnr)
        self.ed_ashost = add_line("AS Host (optional)", profile.rfc.ashost)
        self.ed_lang   = add_line("Lang", profile.rfc.lang)

        layout.addWidget(g_rfc)

        # HANA group (scaffold)
        g_hana = QGroupBox("HANA (hdbcli) — optional")
        lh = QVBoxLayout(g_hana)
        self.cb_hana_enabled = QCheckBox("Enable HANA for this profile")
        self.cb_hana_enabled.setChecked(profile.hana.enabled)
        lh.addWidget(self.cb_hana_enabled)

        self.ed_hana_host = add_line("HANA host", profile.hana.host)
        self.sp_hana_port = QSpinBox()
        self.sp_hana_port.setRange(1, 65535)
        self.sp_hana_port.setValue(int(profile.hana.port))
        rr = QHBoxLayout()
        rr.addWidget(QLabel("HANA port"))
        rr.addWidget(self.sp_hana_port)
        lh.addLayout(rr)

        self.ed_hana_user = add_line("HANA user", profile.hana.user)
        self.ed_hana_pass = QLineEdit(profile.hana.password)
        self.ed_hana_pass.setEchoMode(QLineEdit.Password)
        rr2 = QHBoxLayout()
        rr2.addWidget(QLabel("HANA password"))
        rr2.addWidget(self.ed_hana_pass)
        lh.addLayout(rr2)

        self.ed_hana_schema = add_line("Default schema", profile.hana.schema)

        layout.addWidget(g_hana)

        # Buttons
        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")
        btns.addStretch(1)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def get_profile(self) -> ConnectionProfile:
        r = RFCProfile(
            system=self.ed_system.text().strip() or "SMP",
            client=self.ed_client.text().strip() or "100",
            sysnr=self.ed_sysnr.text().strip() or "00",
            ashost=self.ed_ashost.text().strip(),
            lang=self.ed_lang.text().strip() or "EN",
        )
        h = HANAProfile(
            enabled=self.cb_hana_enabled.isChecked(),
            host=self.ed_hana_host.text().strip(),
            port=int(self.sp_hana_port.value()),
            user=self.ed_hana_user.text().strip(),
            password=self.ed_hana_pass.text(),
            schema=self.ed_hana_schema.text().strip(),
        )
        return ConnectionProfile(name=self.ed_name.text().strip() or "Unnamed", rfc=r, hana=h)
