# 发布单与集成工具参考

这些工具用于处理 Bits 发布单 (singleReleaseTicket) 和集成火车操作，包括创建、阶段推进以及任务的绑定/解绑（上车/下车）。执行这些操作时，请始终优先使用 CLI 方式。

## 可用工具

### 1. bits_create_single_release_ticket
**描述**: 根据可用模板和所需项目创建一个单发布单。在继续之前，请询问用户是否需要关联 Meego 需求。
**参数**:
- `--singleReleaseTicketWorkflowId <number>`: (必填) 单发布单工作流模板的 ID。
- `--projectNames <string...>`: (必填) 目标项目名称。对于多个项目，用空格分隔。
- `--branch <string>`: (必填) 目标分支名称（例如 `master`）。
- `--title <string>`: (可选) 发布单的自定义标题。
- `--meegoUrl <string>`: (可选) Meego 需求 URL。
- `--laneId <string>`: (可选) 自定义泳道名称。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_create_single_release_ticket --singleReleaseTicketWorkflowId <id> --projectNames <name> --branch <branch>
```

### 2. bits_close_release_ticket
**描述**: 关闭现有的发布单。
**参数**:
- `--release_ticket_id <number>`: (必填) 发布单 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_close_release_ticket --release_ticket_id <id>
```

### 3. bits_bind_dev_task_to_train
**描述**: 将指定的开发任务绑定到火车发布单（上车）。
**参数**:
- `--dev_basic_id <number>`: (必填) 开发任务的数字 ID。
- `--integration_id <number>`: (必填) 火车发布单/集成的 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_bind_dev_task_to_train --dev_basic_id <id> --integration_id <id>
```

### 4. bits_unbind_dev_task_to_train
**描述**: 解除开发任务与发布单的绑定（下车）。
**参数**:
- `--dev_basic_id <number>`: (必填) 开发任务的数字 ID。
- `--integration_id <number>`: (必填) 火车发布单/集成的 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_unbind_dev_task_to_train --dev_basic_id <id> --integration_id <id>
```

### 5. bits_get_integration_train_release_tickets
**描述**: 查询当前可用且正在进行的用于集成目的的火车发布单。这应该在绑定开发任务之前使用。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_integration_train_release_tickets
```

### 6. bits_pass_release_ticket_stage
**描述**: 推进发布单流水线中的特定阶段。
**参数**:
- `--releaseTicketId <number>`: (必填) 发布单的 ID。
- `--stageId <number>`: (必填) 要推进的具体阶段 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_pass_release_ticket_stage --releaseTicketId <id> --stageId <id>
```

### 7. bits_get_integration_trains_by_devtask
**描述**: 根据开发任务 ID 获取其可用的集成火车列表。
**参数**:
- `--devTaskId <number>`: (必填) 开发任务 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_integration_trains_by_devtask --devTaskId <id>
```

### 8. bits_get_release_ticket_basic_info
**描述**: 获取发布单的基本信息。
**参数**:
- `--releaseTicketId <number>`: (必填) 发布单 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_release_ticket_basic_info --releaseTicketId <id>
```

### 9. bits_get_release_ticket_projects
**描述**: 获取发布单的项目信息。
**参数**:
- `--releaseTicketId <number>`: (必填) 发布单 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_release_ticket_projects --releaseTicketId <id>
```

### 10. bits_get_release_ticket_stages
**描述**: 获取发布单的阶段 (stages) 信息。
**参数**:
- `--releaseTicketId <number>`: (必填) 发布单 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_release_ticket_stages --releaseTicketId <id>
```

### 11. bits_get_release_ticket_vars
**描述**: 获取发布单的变量信息。
**参数**:
- `--releaseTicketId <number>`: (必填) 发布单 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_release_ticket_vars --releaseTicketId <id>
```

