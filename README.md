# SAP Query Tool (Python zTOAD-style) — MVP

Python/PySide6 SAP query tool prototype with SQL validation and RFC_READ_TABLE support; custom RFC and HANA backends remain scaffolded.

A project of **[ProgreTech LLC](https://progretech.com)**, owned and maintained by **Ed Rodriguez**. Third-party components and contributions retain their respective ownership and notices.

[Project website](https://progretech.com) · [Report an issue](https://github.com/eabdiel/sap_query_tool_mvp/issues) · [Contribute](CONTRIBUTING.md)

Desktop query tool with a zTOAD-like UI and pluggable execution backends.

## What this MVP includes

- PySide6 desktop UI: query editor + results grid + run log
- Connection Profiles (saved locally): RFC and/or HANA parameters
- Two RFC run modes:
  1. **RFC_READ_TABLE** (MVP mode)
  2. **Z_SRE_QUERY_EXEC** (custom ABAP FM mode — scaffolded)
- SQL parsing + validation for RFC mode using `sqlglot`
- **Complex WHERE alert** when using RFC_READ_TABLE (joins/subqueries/ORs/LIKE/IN/etc.)

> Note: HANA runner is included as a scaffold which will be enabled on subsequent versions once the credentials/SSO approach is developed.

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

## Collaboration

Documentation corrections, small reproducible examples, and setup improvements are useful ways to help. Read [CONTRIBUTING.md](CONTRIBUTING.md) for issue reports, proposed changes, and attribution requirements.

## License and reuse

No complete root license was found in this repository. Public availability alone does not grant a general right to reuse or redistribute the code. The maintainer needs to clarify the intended license before code contributions or redistribution.

## More from ProgreTech



Discover the wider portfolio at [progretech.com](https://progretech.com). These links identify related products; they do not imply a bundled integration or shared license.
