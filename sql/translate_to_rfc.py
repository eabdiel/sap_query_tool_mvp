from __future__ import annotations
from typing import List, Dict
from .validate import ParsedSelect

def to_rfc_read_table(parsed: ParsedSelect, max_rows: int = 2000, delimiter: str = "|") -> Dict:
    # RFC_READ_TABLE expects OPTIONS lines up to 72 chars typically (varies by system),
    # and it's not a full SQL engine. This MVP assumes the WHERE is already simple.
    options: List[Dict[str, str]] = []
    if parsed.where_sql:
        # naive split into <= 72 chunks to avoid immediate dump
        s = parsed.where_sql.strip()
        while s:
            options.append({"TEXT": s[:72]})
            s = s[72:].lstrip()
    fields = [{"FIELDNAME": c} for c in parsed.columns if c != "*"]
    return {
        "QUERY_TABLE": parsed.table,
        "DELIMITER": delimiter,
        "ROWCOUNT": max_rows,
        "OPTIONS": options,
        "FIELDS": fields,
    }
