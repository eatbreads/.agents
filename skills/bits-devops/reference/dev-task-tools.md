# 开发任务工具参考

这些工具允许你在 Bits 平台上管理开发任务 (devTask)，包括创建、查询、推进阶段和关闭任务。执行这些操作时，请始终优先使用 CLI 方式。

## 可用工具

### 1. bits_create_dev_task
**描述**: 根据用户提供的参数创建一个新的 Bits 开发任务。如果需要，请务必在创建前根据流程规则检查是否需要关联 Meego。
**参数**:
- `--teamFlowId <number>`: (必填) 开发任务模板 (teamFlow) 的 ID。
- `--projectNames <string...>`: (必填) 一个或多个项目名称。对于多个值，用空格分隔它们（例如 `projA projB`）。
- `--branch <string>`: (必填) 新开发任务的基础分支（例如 `master`）。
- `--title <string>`: (可选) 开发任务的自定义标题。
- `--meegoUrl <string>`: (可选) 要关联的 Meego 需求 URL。
- `--devTaskTemplateId <string>`: (可选) 开发任务模板 ID。
- `--laneId <string>`: (可选) 自定义泳道名称。
- `--releaseTicketId <number>`: (可选) 如果提供，开发任务将在创建后自动绑定到指定的发布单。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_create_dev_task --teamFlowId <id> --projectNames projA projB --branch <branch>
```

### 2. bits_close_dev_task
**描述**: 关闭现有的开发任务。
**参数**:
- `--devtaskId <number>`: (必填) 要关闭的开发任务的数字 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_close_dev_task --devtaskId <id>
```

### 3. bits_get_dev_task_basic_info
**描述**: 获取特定开发任务的基本信息和状态详情。
**参数**:
- `--devtaskId <number>`: (必填) 开发任务的数字 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_dev_task_basic_info --devtaskId <id>
```

### 4. bits_get_dev_task_stages
**描述**: 查询开发任务流水线的当前阶段、变量和代码评审状态。
**参数**:
- `--devtaskId <number>`: (必填) 开发任务的数字 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_dev_task_stages --devtaskId <id>
```

### 5. bits_pass_dev_task_stage
**描述**: 推进开发任务的特定阶段。
**参数**:
- `--devtaskId <number>`: (必填) 开发任务的数字 ID。
- `--action <string>`: (必填) 用于推进阶段的操作名称（通常从 `bits_get_dev_task_stages` 获取）。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_pass_dev_task_stage --devtaskId <id> --action <action>
```

### 6. bits_get_dev_task_changes
**描述**: 获取开发任务的代码变更信息。
**参数**:
- `--devtaskId <number>`: (必填) 开发任务的数字 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_dev_task_changes --devtaskId <id>
```

### 7. bits_get_dev_task_lane_info
**描述**: 获取开发任务的泳道环境信息。
**参数**:
- `--devtaskId <number>`: (必填) 开发任务的数字 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_dev_task_lane_info --devtaskId <id>
```

### 8. bits_get_dev_task_code_review_info
**描述**: 获取开发任务的代码评审 (CodeReview) 信息。
**参数**:
- `--devtaskId <number>`: (必填) 开发任务的数字 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_dev_task_code_review_info --devtaskId <id>
```

### 9. bits_get_dev_task_project_info
**描述**: 获取开发任务的项目信息。
**参数**:
- `--devtaskId <number>`: (必填) 开发任务的数字 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_dev_task_project_info --devtaskId <id>
```

### 10. bits_get_dev_task_vars_info
**描述**: 获取开发任务的变量信息。
**参数**:
- `--devtaskId <number>`: (必填) 开发任务的数字 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_dev_task_vars_info --devtaskId <id>
```

### 11. bits_get_train_mode_devtasks
**描述**: 获取当前用户的火车研发流程类型的开发任务列表。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_train_mode_devtasks
```

