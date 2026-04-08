# FSX Report Pitfalls

## Bits pitfalls

### 1. Raw secret is not the Bits auth header

Wrong path:

- send the service-account secret directly as `x-jwt-token`

Correct path:

1. exchange the secret at `https://cloud.bytedance.net/auth/api/v1/jwt`
2. read `X-Jwt-Token`
3. use that value as `x-jwt-token`

### 2. Latest runs are under `pipeline_runs`, not `data.items`

The real Bits response used in this workflow returned:

- top-level `count`
- top-level `pipeline_runs`

Do not assume the run list is under `data.items`.

### 3. Failed steps are under `latest.jobs`

The real run object used here exposed:

- `run_status`
- `pipeline_run_url`
- `jobs`

Each job row used:

- `job_name`
- `job_run_id`
- `job_status`

Do not waste time searching for nested `job_runs` unless the live response actually contains that structure.

### 4. Status mapping matters

Useful mappings confirmed in this task:

- run status `3` -> `运行中`
- run status `8` -> `已结束`
- run status `9` -> `成功`
- job status `4` -> `阻塞`
- job status `6` -> `失败`

Do not infer root cause from these statuses. Only use them for report labeling.

## Feishu Base pitfalls

### 5. Default `数据表` must be removed

Fresh Bases create a default table automatically.

The final deliverable for this workflow must contain only:

- `汇总信息`
- `失败步骤明细`

Always delete `数据表` before closing the task.

### 6. `+field-create` can be rate-limited

Real error seen:

- `800004135`
- `OpenAPIAddField limited`

Use serial field creation with retry and backoff.
Do not blast field creation in parallel.

### 7. `number` field payload should stay minimal

Real issue seen:

- `precision` was rejected by the current API shape in one create flow

Safe path:

- use `{\"name\":\"失败步骤数\",\"type\":\"number\"}`
- keep style tuning optional unless you have proof the endpoint accepts it

### 8. Background retry processes can corrupt the final Base

This task produced duplicate rows because old retry loops were still running in the background while new cleanup and write passes started.

Before a final write pass:

1. confirm no stale `lark-cli base +record-upsert` or `+record-delete` processes remain
2. clear both target tables
3. run exactly one write pass
4. verify the final counts

## Feishu IM pitfalls

### 9. User send scope may be missing

Real issue seen:

- missing `im:message.send_as_user`

Fallback path:

1. try `--as user`
2. if scope is missing, send with `--as bot`
3. mention that fallback explicitly in the final response
