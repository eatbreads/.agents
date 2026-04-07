---
name: bits-openapi-real-access
description: "Recover and enable real Bits OpenAPI access when an agent has already built a mock or local workflow but is blocked on real environment authentication, headers, username choice, or service-account permissions. Use when Codex needs to obtain a cloud JWT from a Bits service account secret, determine the correct `username` header, validate `domain: pipelines_open;v1`, distinguish 401 vs 403 failures, or unblock real calls such as GetPipeline, GetPipelineRun, GetJobRun, RunPipeline, and NotePipelineRunForOpenapi."
---

# Bits OpenAPI Real Access

## Overview

Use this skill when the implementation is basically ready but real Bits access is failing.

The skill exists to solve the common blocker pattern:

- the agent already built the skeleton
- mock mode works
- real calls fail because `x-jwt-token`, `username`, `domain`, or permissions are wrong

## Workflow

### 1. Confirm this is the right problem

Use this skill when the agent is blocked on one of these symptoms:

- `401` from Bits OpenAPI
- `403` from Bits OpenAPI
- unclear whether a short secret is a service account secret or a personal token
- unclear whether `username` should be a real user or the service account name
- mock mode works but real environment is not connected

Do not use this skill for general Bits business logic or pipeline design.

### 2. Treat auth as a two-step flow

Never call Bits OpenAPI directly with the service account secret.

Always do:

1. exchange the service account secret for a cloud JWT
2. call Bits OpenAPI with that JWT

JWT exchange:

```bash
curl -i -H "Authorization: Bearer ${BITS_SA_SECRET}" \
  https://cloud.bytedance.net/auth/api/v1/jwt
```

Read the response header:

- `X-Jwt-Token`

That value becomes:

- `x-jwt-token`

### 3. Prefer a real human `username`

When calling Bits OpenAPI for pipeline scenarios, prefer:

- `username: <email_prefix>`

Do not default to the service account name as `username` unless the integration explicitly requires it.

If you know the real user, use that user's email prefix, such as:

- `sunjunhao.39`

Do not use:

- `sunjunhao.39@bytedance.com`

unless you have evidence that the endpoint requires a full email address.

### 4. Always include the backend domain header

For backend/server calls, include:

```http
domain: pipelines_open;v1
```

Recommended standard header set:

```http
x-jwt-token: <cloud_jwt>
username: <email_prefix>
domain: pipelines_open;v1
Content-Type: application/json
```

### 5. Verify with the smallest reliable endpoint first

Do not start with complicated write operations.

Use this order:

1. `GetPipeline`
2. `GetPipelineRun`
3. `GetJobRun`
4. `RunPipeline`
5. `NotePipelineRunForOpenapi`

Minimal validation example:

```bash
curl 'https://bits.bytedance.net/api/v1/pipelines/open/656265707522' \
  -H "x-jwt-token: ${CLOUD_JWT}" \
  -H 'username: sunjunhao.39' \
  -H 'domain: pipelines_open;v1'
```

If this returns `200`, the real path is basically alive.

### 6. Interpret failures correctly

#### `401`

Treat as authentication or header construction failure.

Common causes:

- no real cloud JWT was exchanged
- wrong `x-jwt-token`
- JWT expired
- missing or malformed auth headers

#### `403`

Treat as permission failure, not auth failure.

Common causes:

- service account lacks `pipelines_open:v1` permission
- service account lacks target space resource permission
- the API itself requires separate application approval

### 7. Do not hide real blockers behind mock success

If real auth fails, say so explicitly.

Do not report the system as “done” just because:

- mock mode passed
- local JSON artifacts were generated
- the control flow ran without real API access

The correct behavior is:

- report real blocker
- name the exact missing input or permission
- keep the implementation state separate from environment readiness

## What to ask for

If the agent needs real access, ask for:

- `BITS_SA_SECRET`
- real `pipeline_id`
- optional `run_id`
- optional `job_run_id`
- optional Feishu `chat_id`

If the user already provided a short secret and it is unclear what it is, test whether it is a service account secret by trying the cloud JWT exchange first.

## Real access checklist

Before attempting a real run, confirm:

- service account secret is available
- cloud JWT exchange succeeds
- `username` is a real email prefix
- `domain: pipelines_open;v1` is present
- `GetPipeline` succeeds

Only then proceed to:

- `GetPipelineRun`
- `GetJobRun`
- `RunPipeline`
- `NotePipelineRunForOpenapi`

## References

Read [references/bits-openapi-real-access.md](references/bits-openapi-real-access.md) when you need:

- ready-to-send prompts for another agent
- standard env var names
- 401 vs 403 troubleshooting examples
- a compact operator checklist
