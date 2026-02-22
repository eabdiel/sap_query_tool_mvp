# Z_SRE_QUERY_EXEC — ABAP Function Module Spec (Draft)

## Goal
Provide a governed, auditable, role-safe query endpoint for the desktop tool.

This FM is the recommended upgrade path from **RFC_READ_TABLE** because it can:
- enforce authorization checks
- enforce allowlists of objects/fields
- support richer filter logic / joins (if allowed)
- return typed metadata
- centrally log usage (SLG1 or Z table)

## Interface (proposed)

### Import
- `IV_QUERY_TEXT` TYPE `STRING`
  - SQL text from client (only SELECT allowed)
- `IV_MAX_ROWS` TYPE `I` DEFAULT 2000
- `IV_OFFSET` TYPE `I` DEFAULT 0   *(optional for paging)*
- `IV_CLIENT` TYPE `MANDT` OPTIONAL *(if you want to force client check)*

### Export
- `EV_JSON` TYPE `STRING`
  - JSON object:
    ```json
    {
      "columns": ["FIELD1","FIELD2"],
      "rows": [["v1","v2"], ["v3","v4"]],
      "rowcount": 2,
      "runtime_ms": 31,
      "messages": ["..."]
    }
    ```
- `EV_ROWCOUNT` TYPE `I`
- `EV_RUNTIME_MS` TYPE `I`

### Tables (optional if not using JSON)
- `ET_FIELDS` TYPE `ZSRE_T_FIELD_META`
- `ET_DATA`   TYPE `ZSRE_T_ROW_DATA`
- `ET_MESSAGES` TYPE `BAPIRET2_T`

## Validation Rules
- Reject anything not `SELECT`
- Reject `INSERT/UPDATE/DELETE/MERGE/DDL`
- Enforce allowlist:
  - allowed tables/views list in `ZSRE_QUERY_ALLOW`
  - optional allowed field lists per object
- Enforce hard max rows (e.g. 10,000 absolute max)
- Enforce runtime/timeouts (best-effort; use DB hints cautiously)
- Optional: allow JOINS only for CDS SQL views, not raw transparent tables

## Authorization
- Check standard authorizations depending on target:
  - For tables: S_TABU_DIS or CDS-based auth if view
  - For CDS: DCL / analytic privileges as applicable
- Always log the executed query, user, timestamp, system/client, rowcount.

## Implementation Outline
1. Normalize input SQL (trim, single spaces)
2. Parse minimal features:
   - FROM object(s)
   - SELECT list
   - WHERE
   - LIMIT/OFFSET
3. Enforce allowlist and feature policy
4. Execute using Open SQL or ADBC
   - If using ADBC, keep it SELECT-only and protect against injection by rejecting unsafe tokens
5. Build JSON response:
   - columns + rows as strings (MVP)
   - or typed fields if desired
6. Write application log (SLG1) and/or Z audit table

## Notes
- Consider returning results in pages (offset/limit) to avoid huge RFC payloads.
- Consider hashing query text for log keys if you don't want full query stored.
