from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple

import sqlglot
from sqlglot import exp

@dataclass
class ParsedSelect:
    table: str
    columns: List[str]          # ["*"] allowed
    where_sql: str
    limit: Optional[int]

class SQLValidationError(ValueError):
    pass

COMPLEX_WHERE_TOKENS = {
    " OR ", " LIKE ", " IN ", " EXISTS ", " BETWEEN ", " UNION ", " JOIN ",
    " SELECT ", " FROM ", " CASE ", " WHEN ", " COALESCE ", " IS NULL ", " IS NOT NULL ",
}

def parse_select(sql_text: str) -> ParsedSelect:
    try:
        parsed = sqlglot.parse_one(sql_text, read="ansi")
    except Exception as e:
        raise SQLValidationError(f"SQL parse error: {e}")

    if not isinstance(parsed, exp.Select):
        # Allow with/CTE that results in select? For MVP, reject.
        raise SQLValidationError("Only SELECT statements are allowed in RFC mode.")

    # Reject joins/subqueries in RFC_READ_TABLE mode at a higher layer; but parse anyway.
    from_ = parsed.args.get("from")
    if not from_ or not from_.expressions:
        raise SQLValidationError("SELECT must include a FROM clause.")
    # Only first table is considered for MVP
    table_exp = from_.expressions[0]
    table = table_exp.name if hasattr(table_exp, "name") else table_exp.sql()
    if not table:
        raise SQLValidationError("Unable to determine table name from FROM clause.")

    # Columns
    select_exprs = parsed.expressions or []
    cols: List[str] = []
    for e in select_exprs:
        if isinstance(e, exp.Star):
            cols.append("*")
        elif isinstance(e, exp.Column):
            cols.append(e.name)
        else:
            # MVP: only allow simple column refs
            cols.append(e.sql())
    if not cols:
        cols = ["*"]

    where_exp = parsed.args.get("where")
    where_sql = where_exp.sql(dialect="ansi") if where_exp else ""
    # Normalize: remove leading "WHERE "
    if where_sql.upper().startswith("WHERE "):
        where_sql = where_sql[6:].strip()

    limit_exp = parsed.args.get("limit")
    limit = None
    if limit_exp and limit_exp.expression:
        try:
            limit = int(limit_exp.expression.name)
        except Exception:
            limit = None

    return ParsedSelect(table=table, columns=cols, where_sql=where_sql, limit=limit)

def detect_complex_where(where_sql: str) -> Tuple[bool, str]:
    if not where_sql:
        return (False, "")

    up = f" {where_sql.strip().upper()} "
    reasons = []

    # Heuristics: OR/LIKE/IN/etc.
    for tok in sorted(COMPLEX_WHERE_TOKENS):
        if tok in up:
            reasons.append(tok.strip())
    # Too long for typical RFC_READ_TABLE OPTIONS
    if len(where_sql) > 72:
        reasons.append("WHERE length > 72 chars (likely needs splitting)")

    if reasons:
        return (True, ", ".join(reasons))
    return (False, "")
