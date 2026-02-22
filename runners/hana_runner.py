from __future__ import annotations
import time
from typing import Any, List

from models.profile import ConnectionProfile
from models.query_result import QueryResult

class HanaBackendError(RuntimeError):
    pass

class HanaQueryRunner:
    def __init__(self, profile: ConnectionProfile, default_schema: str = ""):
        self.profile = profile
        self.default_schema = default_schema

    def run(self, sql_text: str) -> QueryResult:
        # Scaffold. Requires hdbcli.
        try:
            from hdbcli import dbapi  # type: ignore
        except Exception as e:
            raise HanaBackendError("hdbcli is not installed. Install hdbcli to use HANA mode.") from e

        h = self.profile.hana
        if not h.enabled:
            raise HanaBackendError("HANA is not enabled for this profile.")

        t0 = time.time()
        conn = dbapi.connect(host=h.host, port=h.port, user=h.user, password=h.password)
        cur = conn.cursor()
        try:
            cur.execute(sql_text)
            rows = cur.fetchall()
            cols = [d[0] for d in (cur.description or [])]
        finally:
            cur.close()
            conn.close()

        ms = int((time.time() - t0) * 1000)
        return QueryResult(columns=cols, rows=[list(r) for r in rows], message="OK", runtime_ms=ms, rowcount=len(rows))
