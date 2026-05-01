---
name: source-reading-guide
description: Analyze source code as a step-by-step source reading navigation map instead of a high-level summary. Use when Codex needs to help users read large codebases, follow execution flow into real functions, produce function-level sequence diagrams, avoid skipping bridge or dispatch layers, and map analysis back to IDE-friendly reading order.
---

# Source Reading Guide

## Overview

把源码分析结果整理成“能顺着点进 IDE 继续读”的导航结果，而不是抽象架构汇报。
重点是帮助用户按真实执行流跟读代码，不在中间分发、包装、调度、回调这些层里迷路。

## Core Goal

默认把输出做成“源码阅读导航图”，并满足以下目标：

- 先给目录结构总览，明确每个目录的职责
- 提供多条“源码阅读型详细顺序图”（覆盖主要执行分支）
- 顺序图里的函数名、类名必须与源码真实一致
- 调用链尽量不断层，保证可以对着图一步步点进代码
- 提供一个更完整、更大的静态类图/模块图，并标注关键交互
- 强制把结果写入本地 `.md` 文件，而不是只在对话里输出

## Working Rules

### 1. 目录结构总览必须放在最前面

输出开头必须先给目录结构总览，格式类似：

- `目录A`：一句话职责说明。
- `目录B`：一句话职责说明。
- `目录B/子目录`：一句话职责说明。

要求：

- 覆盖当前阅读范围内的重要目录（入口、核心执行、调度、后端、协议、工具）
- 描述以“职责”而不是“文件名罗列”为主
- 顺序应支持用户自顶向下建立整体心智模型

### 2. 只输出“源码阅读型详细顺序图”，并且要有多条

不要输出“高层总览顺序图”。

必须输出多条详细顺序图，至少覆盖：

- 初始化/启动流程
- 主请求处理流程
- 至少 1 条分支流程（如控制命令、异步回调、重试、恢复、监控命令、worker loop 等）

如果代码本身存在更多核心分支，应继续补充，而不是只给 1 条主链。

### 3. 每条顺序图都要“可跟读”

顺序图必须满足：

- 使用真实函数名、真实类名（与代码一致）
- 每一步调用都有中文解释，解释其在当前链路中的作用
- 保留关键桥接函数：
  - 入口函数
  - `dispatch` / `handle` / `process` / `route`
  - `enqueue` / `submit` / `schedule`
  - `callback` / `completion`
  - `prepare` / `init` / `open` / `create context`
  - `wrapper` / `adapter` / `bridge`
- 不能用“模块A调用模块B”替代真实函数级调用
- 代码流转不能跳太大；允许少量折叠，但不能让主路径断层

### 4. 不要“省略函数说明”章节

不再输出“省略函数说明”或“其他请求示例”章节。

要求是：

- 直接把关键分支展开成完整顺序图
- 通过多图覆盖复杂度，而不是通过“省略说明”减少信息

### 5. 顺序图使用 PlainUML 风格

所有顺序图遵守：

- 图里必须写函数名/类名
- 每条调用后面加中文注释
- 有返回值、错误分支、重试、异步回调时要显式画出
- 对易迷路节点可用 `note` 标注“建议停下读源码”的位置

### 6. 提供更完整的静态结构图（增强版）

除顺序图外，必须输出一个更完整的类图/模块图：

- 关键类/模块尽量完整，不要只列少数方法
- 类中优先列阅读主线相关函数
- 标出依赖、调用方向、组合关系
- 除结构连线外，增加关键交互标注（例如：`Srv -> Net: StartNetThread()【启动网络线程并注册RPC服务】`）
- 标注层次：入口层、调度层、执行层、状态/恢复层

### 7. 分层关键函数表仍需保留

函数表至少分层覆盖：

- 入口函数
- 路由/分发函数
- 调度/队列函数
- 核心执行函数
- 状态更新/副作用函数
- 错误处理/恢复函数

表格字段保持：

| 函数名 | 所属类/模块 | 在阅读路径中的位置 | 主要行为 | 为什么这一步不能跳过 | 输入 | 输出 | 副作用 | 阻塞/异步 | 下一步应该看什么 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### 8. 术语解释与阅读建议保持贴链路

- 术语解释必须结合当前调用链，不写百科式定义
- 阅读建议必须给出“按函数可点击”的实际阅读顺序

### 9. 强制写入 Markdown 文件

每次使用本 skill 完成分析后，必须把完整结果写入本地 `.md` 文件。

强制要求：

- 不能只在对话里输出，必须落盘
- 默认输出路径优先：`docs/source-reading-guide-<scope>.md`
- 若 `docs/` 不存在，则写到仓库根目录：`source-reading-guide-<scope>.md`
- `<scope>` 使用被分析目录名或模块名（例如 `src`、`fusedaemon`）
- 回答中必须明确告知写入文件的绝对路径

## Output Structure

默认按下面结构输出（除非用户明确要求其他格式）：

```markdown
## 目录结构总览

## 源码阅读型详细顺序图 - 启动流程

## 源码阅读型详细顺序图 - 主请求流程

## 源码阅读型详细顺序图 - 分支流程 A

## 源码阅读型详细顺序图 - 分支流程 B（如果有）

## 静态结构图（增强）

## 分层关键函数表

## 术语解释

## 源码阅读建议
```

注意：

- 不要输出 `阅读定位`
- 不要输出 `已确认链路`
- 不要输出 `待确认链路`
- 不要输出 `第 1 层：高层总览顺序图`
- 不要输出 `省略函数说明`
- 不要输出“其他请求示例”占位段落

## PlainUML Template

### 详细顺序图模板

```text
@startuml
actor Caller
participant Entry
participant Dispatcher
participant Worker
participant Callback

Caller -> Entry: start() 【进入真实入口函数】
Entry -> Dispatcher: dispatchRequest() 【进入分发桥接层】
Dispatcher -> Worker: submitTask() 【提交到执行单元】
Worker -> Callback: onComplete() 【触发回调/收口】
Callback --> Dispatcher: result/status 【回传执行结果】
Dispatcher --> Entry: response/status 【汇总状态并返回】
Entry --> Caller: done 【返回调用方】

note right of Dispatcher
建议在这里停下来先读源码：
先确认分支选择条件，再继续往下点。
end note
@enduml
```

### 增强静态结构图模板

```text
@startuml
class EntryLayer {
  +main()
  +init()
  +handleRequest()
}

class DispatchLayer {
  +dispatch()
  +route()
  +enqueue()
  +schedule()
}

class WorkerLayer {
  +process()
  +execute()
  +complete()
}

class StateLayer {
  +updateState()
  +recover()
  +onError()
}

EntryLayer --> DispatchLayer
DispatchLayer --> WorkerLayer
WorkerLayer --> StateLayer

note top of EntryLayer : 入口层
note top of DispatchLayer : 调度层
note top of WorkerLayer : 执行层
note top of StateLayer : 状态/恢复层

note bottom
关键交互示例：
Srv -> Net: StartNetThread()【启动网络线程并注册RPC服务】
Dispatcher -> Worker: submitTask()【提交执行任务】
@end note
@enduml
```

## Style Rules

- 目标是帮人读源码，不是做 PPT 汇报
- 优先函数级调用链，不停留在模块名层面
- 顺序图宁可长一点，也不要断主线
- 输出要让用户可以“照图点代码”
- 语气自然，像有经验工程师带读源码

## Hard Bans

避免下面问题：

- 只给模块级架构，不给函数级入口
- 顺序图跳过关键桥接/分发/回调函数
- 函数名或类名与源码不一致
- 用“某模块调用某模块”替代真实函数调用
- 把推测写成已确认事实
- 给结论但不告诉用户下一步点哪个函数
- 只在对话输出而不写入 `.md` 文件
