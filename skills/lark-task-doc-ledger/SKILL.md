---
name: lark-task-doc-ledger
description: "Maintain a specified Lark doc as a simple numbered task list instead of a loose note. Use when Codex needs to read a user-provided Feishu/Lark cloud document that stores tasks, normalize it into a flat list where each task keeps fixed fields such as owner, source, priority, description, notes, and related docs, append new tasks from the current conversation context, or write Feishu document links back into the matching task."
---

# Lark Task Doc Ledger

先阅读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md) 和 [`../lark-doc/SKILL.md`](../lark-doc/SKILL.md)。
这个 skill 通过 `lark-cli docs +fetch` 和 `lark-cli docs +create` / `lark-cli docs +update` 维护飞书云文档里的任务清单。

## Overview

把飞书云文档里的任务清单维护成“简单、稳定、可继续追加”的单层编号结构。
默认不拆子任务，不做复杂台账，只保留固定字段，方便持续回写。

## Canonical Structure

每条任务都按下面格式维护：

```markdown
### 0. 任务标题
- 负责人：张三
- 来源：某同学 / 某部门 / 暂无
- 优先级：高 / 中 / 低 / 暂无
- 任务描述：...
- 备注：...
- 相关文档：...
```

固定字段为：

- `负责人`
- `来源`
- `优先级`
- `任务描述`
- `备注`
- `相关文档`

如果原文缺字段，就自动补齐。
默认补值：

- `来源`：`暂无`
- `优先级`：`暂无`
- `备注`：`暂无`
- `相关文档`：`暂无`

## Working Rules

### 1. 用户给了文档链接就直接读取

如果用户已经提供飞书云文档 URL 或 token，直接读取该文档，不先搜索其他文档。

### 2. 保留原任务表达方式

用户如果更喜欢：

- `0. 任务标题`
- `- 负责人`
- `- 来源`
- `- 任务描述`

这种简单格式，就保持这种风格，不要升级成更复杂的层级结构。

### 3. 规范化只做最小必要整理

规范化时只做这些事：

- 统一编号任务格式
- 补齐固定字段
- 把零散说明收进 `备注`
- 把文档链接收进 `相关文档`

不要额外引入：

- 子任务
- 状态机
- 大任务 / 小任务分层
- 复杂表格结构

### 4. 当前聊天上下文可以生成新任务

如果当前对话里已经形成了明确工作项，比如：

- 新建了一个 skill
- 产出了一份日报
- 完成了一份方案
- 整理出一个待跟进事项

可以作为一条新的编号任务追加到文档里。

### 5. 文档链接优先写进相关任务

如果聊天里产出了新的飞书文档链接，优先把它写到最匹配任务的 `相关文档` 字段里。
如果没有合适任务，再新增一条任务记录这件事。

### 6. 默认做简单覆盖式回写

对于纯文本任务清单，默认流程是：

1. `docs +fetch`
2. 在本地整理出新的 Markdown
3. 已有文档用 `docs +update --mode overwrite`
4. 用户要求“新生成一份”时用 `docs +create`

## Matching Rules

把当前聊天内容挂到现有任务时，优先看：

- 任务标题关键词
- 任务描述主题
- 负责人
- 相关文档类型

如果无法唯一匹配：

- 新增一条任务
- 不要硬塞到不确定的旧任务里

## Example Request

下面这些请求应该触发本 skill：

- “读取这个飞书文档，把任务清单补齐备注和相关文档”
- “按简单编号格式重新整理这份任务文档”
- “根据当前聊天内容新增一条任务”
- “把这份日报链接挂到对应任务的相关文档里”
- “帮我重新生成一份新的飞书任务文档”

示例文档：

- `https://bytedance.larkoffice.com/docx/WtwFdmTONoZnHPxVD9zcoJugnRe`

## Quality Bar

回写前自查：

- 是否保持了简单单层格式
- 是否每条任务都补齐了固定字段
- 是否没有偷偷引入子任务结构
- 是否新增任务足够明确
- 是否把链接放到了正确任务的 `相关文档`

## Style

- 用中文维护文档
- 简洁优先
- 固定字段名不要漂移
- 不要过度包装格式
