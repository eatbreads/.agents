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

## CLI / Integration pitfalls

### 10. `lark-cli` 未安装或 PATH 找不到

- 症状：`lark-cli: command not found`。
- 成因：云/容器环境未预装 CLI，或 PATH 未包含用户安装目录。
- 修复：使用用户前缀安装并调用显式路径。
  - 安装：`npm install --prefix "$HOME/.local" -g @larksuite/cli`
  - 调用：`$HOME/.local/bin/lark-cli ...` 或将 `~/.local/bin` 加入 PATH。

### 11. 全局安装权限不足（EACCES）

- 症状：`npm install -g` 报 `EACCES: permission denied`。
- 修复：改用用户目录安装：`npm install --prefix "$HOME/.local" -g @larksuite/cli`。

### 12. 首次使用需初始化与登录

- 症状：`lark-cli auth status` 显示 `not configured` 或无 user 身份。
- 修复：
  - 初始化配置：`lark-cli config init --new`（根据输出链接完成设备授权）。
  - 获取用户身份：`lark-cli auth login --recommend`，完成浏览器授权后再执行后续操作。

### 13. Base 用 bot 创建后用户无法访问

- 症状：用户打开 Base 链接提示无权限。
- 原因：Base 由 `bot` 创建，未为个人用户授予访问。
- 处理：
  - 首选使用 `user` 身份为目标用户授予权限/加入成员；
  - 或保留 `bot` 身份，拿到用户 `open_id` 后进行增权。

### 14. 同步脚本需支持 `--as bot`

- 症状：同步时报 `need_user_authorization`，而 `bot` 对该 Base 有权限。
- 处理：为 `scripts/sync_fsx_lark_base.py` 增加 `--as [user|bot]`，在用户未授权时使用 `--as bot` 完成表结构与数据写入。

### 15. 以 bot 发群消息需先将应用加入群

- 症状：`im +messages-send --as bot` 失败提示未在群内或权限不足。
- 处理：确认应用已在目标群；若缺少用户发送 scope，按“先 user，失败再 bot”顺序回退。
