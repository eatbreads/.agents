# FSX Report Required Reads

## Inputs that are actually useful

Read these local files first:

- `fsx-pipelines-summary.md`
  Use to confirm candidate pipeline names and Bits URLs.
- `fsx-pipelines-doc.json`
  Use to cross-check the original source wording when the summary markdown is ambiguous.
- `.agents/secret`
  Use only as the default local Bits service-account secret source when `BITS_SA_SECRET` is absent.

## Skills and references that are actually useful

Read these existing skill files before operating:

- `.agents/skills/bits-openapi-real-access/SKILL.md`
  Use for the auth flow, required headers, and 401 vs 403 interpretation.
- `.agents/skills/bits-openapi-real-access/references/bits-openapi-real-access.md`
  Use for the standard request shape and env var naming.
- `.agents/skills/lark-base/references/lark-base-base-create.md`
  Use when a fresh Base must be created.
- `.agents/skills/lark-base/references/lark-base-table-list.md`
  Use before deciding whether to reuse, create, or delete tables.
- `.agents/skills/lark-base/references/lark-base-table-delete.md`
  Use when removing the default `数据表`.
- `.agents/skills/lark-base/references/lark-base-field-list.md`
  Use before creating fields.
- `.agents/skills/lark-base/references/lark-base-field-create.md`
  Use for field creation rules and payload shape.
- `.agents/skills/lark-base/references/lark-base-record-list.md`
  Use for record reads and pagination.
- `.agents/skills/lark-base/references/lark-base-record-delete.md`
  Use when clearing stale rows.
- `.agents/skills/lark-base/references/lark-base-record-upsert.md`
  Use for final row writes.
- `.agents/skills/lark-im/references/lark-im-messages-send.md`
  Use before sending the group message, especially for user vs bot fallback.

## Files that were low-signal or only historical

- `artifacts/base_summary_fields.json`
  Historical schema from an earlier draft. Do not treat it as the final Base schema.
- `artifacts/base_detail_fields.json`
  Historical schema from an earlier draft. Do not treat it as the final Base schema.
- `doc`
  Large Bits OpenAPI route dump. Useful only if endpoint naming is uncertain; not the first file to read for this workflow.
