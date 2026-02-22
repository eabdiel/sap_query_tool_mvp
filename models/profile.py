from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class RFCProfile:
    system: str = "SMP"   # e.g. SMP/SMD
    client: str = "100"
    sysnr: str = "00"
    ashost: str = ""      # optional if your sap_connector infers it
    lang: str = "EN"

@dataclass
class HANAProfile:
    enabled: bool = False
    host: str = ""
    port: int = 30015
    user: str = ""
    password: str = ""
    schema: str = ""

@dataclass
class ConnectionProfile:
    name: str
    rfc: RFCProfile
    hana: HANAProfile

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ConnectionProfile":
        r = d.get("rfc", {}) or {}
        h = d.get("hana", {}) or {}
        return ConnectionProfile(
            name=d.get("name", "Unnamed"),
            rfc=RFCProfile(**{k: r.get(k, getattr(RFCProfile(), k)) for k in RFCProfile().__dict__.keys()}),
            hana=HANAProfile(**{k: h.get(k, getattr(HANAProfile(), k)) for k in HANAProfile().__dict__.keys()}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "rfc": self.rfc.__dict__,
            "hana": self.hana.__dict__,
        }
