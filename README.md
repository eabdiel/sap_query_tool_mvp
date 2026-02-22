# SAP Query Tool (Python zTOAD-style) — MVP

Desktop query tool with a zTOAD-like UI and pluggable execution backends.

## What this MVP includes

- PySide6 desktop UI: query editor + results grid + run log
- Connection Profiles (saved locally): RFC and/or HANA parameters
- Two RFC run modes:
  1. **RFC_READ_TABLE** (MVP mode)
  2. **Z_SRE_QUERY_EXEC** (custom ABAP FM mode — scaffolded)
- SQL parsing + validation for RFC mode using `sqlglot`
- **Complex WHERE alert** when using RFC_READ_TABLE (joins/subqueries/ORs/LIKE/IN/etc.)

> Note: HANA runner is included as a scaffold and can be enabled once your credentials/SSO approach is decided.

## Install

Create a venv, then:

```bash
pip install -r requirements.txt
```

If you want RFC and/or HANA backends:

```bash
pip install pyrfc
pip install hdbcli
```

## Run

```bash
python app.py
```

## Governance / Safety

- RFC mode only accepts **SELECT** statements.
- RFC_READ_TABLE mode is restricted to **single table** queries and simple WHERE clauses.
- For anything more complex, switch to **Z_SRE_QUERY_EXEC** (recommended) or HANA mode.

## ABAP FM spec

See: `docs/abap/Z_SRE_QUERY_EXEC_SPEC.md`
