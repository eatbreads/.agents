# 空间基础工具参考

这些工具用于查询和管理 Bits 空间的基础信息，包括服务器版本、可用项目和流程模板。执行这些操作时，请始终优先使用 CLI 方式。

## 可用工具

### 1. bits_get_mcp_server_version
**描述**: 获取当前的 MCP Server 版本。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_mcp_server_version
```

### 2. bits_get_workspace_info
**描述**: 获取当前配置的 Bits 空间基础信息。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_workspace_info
```

### 3. bits_switch_workspace
**描述**: 将当前 Bits 空间切换到不同的空间 ID。
**参数**:
- `--spaceId <number>`: (必填) 你想要切换到的 Bits 空间 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_switch_workspace --spaceId <id>
```

### 4. bits_get_dev_templates
**描述**: 查询当前空间中可用的开发任务 (devTask) 模板。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_dev_templates
```

### 5. bits_get_single_release_ticket_templates
**描述**: 查询当前空间中可用的单发布单模板。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_single_release_ticket_templates
```

### 6. bits_get_projects_by_user
**描述**: 查询当前用户在此空间中可用的 Bits 项目列表。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_projects_by_user
```

### 7. bits_get_meego_workitem_by_url
**描述**: 使用 Meego URL 查询详细的 Meego 工作项（需求/缺陷）信息。
**参数**:
- `--meegoUrl <string>`: (必填) 你希望查询的完整 Meego URL。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_meego_workitem_by_url --meegoUrl <url>
```

### 8. bits_check_dev_task_template_meego
**描述**: 检查开发任务模板是否必须关联 Meego，返回 true 或 false。
**参数**:
- `--devTaskTemplateId <number>`: (必填) 开发任务模板 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_check_dev_task_template_meego --devTaskTemplateId <id>
```

### 9. bits_get_dev_template_detail
**描述**: 获取当前开发任务模板的详细信息。
**参数**:
- `--devTaskTemplateId <number>`: (必填) 开发任务模板 ID。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_dev_template_detail --devTaskTemplateId <id>
```

### 10. bits_get_opened_dev_task_list
**描述**: 获取当前用户所有进行中的开发任务列表。
**用法**:
```bash
npx -y @mcp_hub/bits-devops bits_get_opened_dev_task_list
```

