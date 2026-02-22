from __future__ import annotations
import json
import time
from typing import Any, List

from models.profile import ConnectionProfile
from models.query_result import QueryResult
from sql.validate import parse_select, detect_complex_where, SQLValidationError
from sql.translate_to_rfc import to_rfc_read_table

class RFCBackendError(RuntimeError):
    pass

def _import_pyrfc():
    try:
        from pyrfc import Connection  # type: ignore
        return Connection
    except Exception as e:
        raise RFCBackendError(
            "pyrfc is not installed or SAP NWRFC SDK is not configured. "
            "Install pyrfc and ensure SAP NWRFC SDK is available."
        ) from e

class RfcQueryRunner:
    """Supports both RFC_READ_TABLE (MVP) and Z_SRE_QUERY_EXEC (custom FM)."""

    MODE_RFC_READ_TABLE = "RFC_READ_TABLE"
    MODE_Z_SRE_QUERY_EXEC = "Z_SRE_QUERY_EXEC"

    def __init__(self, profile: ConnectionProfile, mode: str, max_rows: int = 2000):
        self.profile = profile
        self.mode = mode
        self.max_rows = max_rows

    def _connect(self):
        # Uses the user's existing sap_connector.py helper
        from sap_connector import connect_sso  # local file in repo
        r = self.profile.rfc
        # Your connect_sso signature supports system/client and infers SNC partner;
        # host/sysnr may be optional depending on your implementation.
        return connect_sso(system=r.system, client=r.client, sysnr=r.sysnr, host=r.ashost)

    def precheck_for_ui(self, sql_text: str):
        """Return (is_complex, reason) for WHERE complexity in RFC_READ_TABLE mode."""
        parsed = parse_select(sql_text)
        return detect_complex_where(parsed.where_sql)

    def run(self, sql_text: str) -> QueryResult:
        t0 = time.time()
        parsed = parse_select(sql_text)

        if self.mode == self.MODE_RFC_READ_TABLE:
            is_complex, reason = detect_complex_where(parsed.where_sql)
            # UI will warn; still allow execution, but note limitations.
            payload = to_rfc_read_table(parsed, max_rows=self.max_rows)
            conn = self._connect()
            try:
                raw = conn.call("RFC_READ_TABLE", **payload)
            except Exception as e:
                raise RFCBackendError(f"RFC_READ_TABLE failed: {e}") from e

            # Parse result (DATA rows are delimited strings)
            data = raw.get("DATA", []) or []
            fields = raw.get("FIELDS", []) or []
            cols = [f.get("FIELDNAME", "") for f in fields] if fields else (["WA"] if data else [])
            rows: List[List[Any]] = []
            delim = payload["DELIMITER"]
            for d in data:
                wa = d.get("WA", "")
                if cols == ["WA"]:
                    rows.append([wa])
                else:
                    rows.append(wa.split(delim))

            ms = int((time.time() - t0) * 1000)
            msg = "OK"
            if is_complex:
                msg = f"OK (Warning: complex WHERE detected for RFC_READ_TABLE: {reason})"
            return QueryResult(columns=cols, rows=rows, message=msg, runtime_ms=ms, rowcount=len(rows))

        if self.mode == self.MODE_Z_SRE_QUERY_EXEC:
            # Scaffold: You will implement Z_SRE_QUERY_EXEC to accept SQL_TEXT or structured parts.
            # Here we assume it accepts IV_QUERY_TEXT and returns EV_JSON (stringified JSON table)
            conn = self._connect()
            try:
                raw = conn.call("Z_SRE_QUERY_EXEC", IV_QUERY_TEXT=sql_text, IV_MAX_ROWS=self.max_rows)
            except Exception as e:
                raise RFCBackendError(f"Z_SRE_QUERY_EXEC failed (FM missing or error): {e}") from e

            # Flexible decoding: try JSON first, fall back to ET_DATA strings
            cols: List[str] = []
            rows: List[List[Any]] = []
            if "EV_JSON" in raw and raw["EV_JSON"]:
                try:
                    obj = json.loads(raw["EV_JSON"])
                    cols = obj.get("columns", [])
                    rows = obj.get("rows", [])
                except Exception:
                    cols = ["EV_JSON"]
                    rows = [[raw["EV_JSON"]]]
            else:
                cols = [c.get("NAME","") for c in (raw.get("ET_FIELDS") or [])] or []
                data = raw.get("ET_DATA") or []
                for r in data:
                    if isinstance(r, dict):
                        rows.append(list(r.values()))
                    else:
                        rows.append([r])

            ms = int((time.time() - t0) * 1000)
            return QueryResult(columns=cols, rows=rows, message="OK", runtime_ms=ms, rowcount=len(rows))

        raise SQLValidationError(f"Unknown RFC mode: {self.mode}")
