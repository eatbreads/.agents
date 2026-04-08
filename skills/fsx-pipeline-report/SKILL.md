---
name: fsx-pipeline-report
description: Generate FSX watched-pipeline operations reports from Bits and publish them to Feishu. Use when Codex needs to fetch the latest runs for a fixed set of FSX duty-owned pipelines, extract summary plus failed-step details, create or update a Feishu Base, produce a Markdown report, or send a concise report message to a Feishu group. This skill is especially for requests like “完成需看护流水线运营报表”, “抓取 FSX 值班流水线失败步骤”, or “同步 Bits 流水线报表到飞书多维表格/群聊”.
---

# FSX Pipeline Report

## Overview

Use this skill to turn Bits pipeline status into an operations report that people can read directly in Feishu.

Keep the output split into two layers:

- summary for management scan
- failed-step detail for operator follow-up

Do not expand into root-cause analysis unless the user explicitly asks for it.

## Workflow

### 1. Lock the scope first

Only report the watched pipelines that belong to FSX duty coverage.

Do not automatically include:

- EFS self-maintained pipelines
- QA fault-injection pipelines marked as no-watch
- unrelated upstream or downstream pipelines

Read [references/fsx-report-reference.md](references/fsx-report-reference.md) for the current watched pipeline list, recommended report fields, and the group-chat target used in this workspace.
Read [references/required-reads.md](references/required-reads.md) for the exact files that were truly useful in this workflow.

### 2. Load the local secret correctly

Prefer this order for the Bits service-account secret:

1. environment variable `BITS_SA_SECRET`
2. local file `.agents/secret`

Treat `.agents/secret` as local-only machine state. Do not commit it and do not echo the raw secret back to the user unless they explicitly ask.

If neither source exists, ask the user for the service-account secret.

### 3. Authenticate to Bits the right way

Never call Bits OpenAPI with the raw secret directly.

Always:

1. exchange the service-account secret for a cloud JWT via `https://cloud.bytedance.net/auth/api/v1/jwt`
2. call Bits with headers:
   - `x-jwt-token: <cloud_jwt>`
   - `username: sunjunhao.39`
   - `domain: pipelines_open;v1`

Treat `401` as auth/header trouble.
Treat `403` as permission trouble.

If auth works but the run payload shape looks different from memory, read [references/pitfalls.md](references/pitfalls.md) before guessing field paths.

### 4. Pull only the data needed for reporting

For each watched pipeline:

- fetch pipeline metadata
- fetch the latest run, unless the user explicitly asks for a wider date range
- extract run status
- extract job list and keep failed or blocked steps
- keep the operator-facing question narrow: which day, which pipeline, which step, what status

Avoid spending time on logs or failure-cause analysis unless the user asks for diagnosis.

### 5. Build the report in two sections

Use two outputs with the same information architecture:

- `汇总信息`
- `失败步骤明细`

Do not keep an extra default table such as `数据表` in the final Base.

Recommended local artifacts:

- raw Bits response JSON
- summary JSON
- detail JSON
- Markdown report

Do not write artifacts into this git workspace. Use `/tmp/fsx-pipeline-report` as the default output directory.

If you need deterministic data generation, run:

```bash
python3 scripts/fetch_fsx_pipeline_report.py \
  --repo-root /path/to/workspace \
  --output-dir /tmp/fsx-pipeline-report
```

This script writes:

- `fsx_pipeline_runs_raw.json`
- `fsx_pipeline_report_summary.json`
- `fsx_pipeline_report_details.json`
- `fsx_pipeline_report.md`

### 6. Write to Feishu Base

Prefer Feishu Base over Sheets for this report.

Create or update two tables:

- `汇总信息`
- `失败步骤明细`

Before writing records:

1. inspect table and field structure
2. create missing fields
3. upsert summary records
4. upsert detail records

If the Base already exists, update it instead of creating duplicate tables unless the user asked for a fresh one.

If you want a repeatable Feishu sync path, run:

```bash
python3 scripts/sync_fsx_lark_base.py \
  --base-token <base_token> \
  --artifact-dir /tmp/fsx-pipeline-report
```

This script:

- ensures `汇总信息` and `失败步骤明细` exist
- creates missing fields with retry
- deletes default `数据表`
- clears old rows
- writes one clean summary pass and one clean detail pass

### 7. Send the group summary

Send a concise summary message to the target group after the Base is ready.

Preferred order:

1. try `lark-cli im +messages-send --as user`
2. if the user identity lacks `im:message.send_as_user`, fall back to `--as bot`

The message should include:

- report title and date
- Base link
- how many watched pipelines were included
- which pipelines currently need attention
- total failed/blocked detail count
- a short note that this round does not analyze root cause

Do not add filler text such as “Markdown 版本已同步生成，便于后续沉淀或转文档”.

### 8. Close out clearly

In the final response, include:

- Base link
- local Markdown path
- whether the group message was sent as user or bot
- any remaining limitation such as missing message scope or incomplete pipeline coverage

## Guardrails

- Do not silently widen the watched-pipeline list.
- Do not include the raw secret in generated artifacts.
- Do not present mock data as if it came from real Bits.
- Do not claim root-cause conclusions from step names alone.
- Do not forget that `.agents/secret` is the default local secret location in this workspace.
- Do not leave `数据表` in the final Base delivered to the user.
- Do not store any generated artifacts under this git workspace; prefer `/tmp/fsx-pipeline-report`.

## References

- Read [references/fsx-report-reference.md](references/fsx-report-reference.md) for watched pipelines, target chat, and the current field set.
- Read [references/required-reads.md](references/required-reads.md) for the exact high-signal files.
- Read [references/pitfalls.md](references/pitfalls.md) for the real issues hit in this task.
- Read [references/final-base-summary-fields.json](references/final-base-summary-fields.json) and [references/final-base-detail-fields.json](references/final-base-detail-fields.json) when rebuilding the Base schema.
- Read [references/example-report.md](references/example-report.md) when you need the expected markdown shape.
