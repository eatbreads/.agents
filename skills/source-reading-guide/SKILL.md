---
name: source-reading-guide
description: Analyze source code as a step-by-step source reading navigation map instead of a high-level summary. Use when Codex needs to help users read large codebases, follow execution flow into real functions, produce function-level sequence diagrams, avoid skipping bridge or dispatch layers, map analysis back to IDE-friendly reading order, or explain confirmed vs unconfirmed call chains during code reading.
---

# Source Reading Guide

## Overview

把源码分析结果整理成“能顺着点进 IDE 继续读”的导航结果，而不是抽象架构汇报。
重点是帮助用户按真实执行流跟读代码，不在中间分发、包装、调度、回调这些层里迷路。

## Core Goal

默认把输出做成“源码阅读导航图”。
优先回答这几件事：

- 这段代码在整个系统里处于哪一层
- 建议从哪个函数开始读
- 应该按什么顺序继续点进去
- 哪些函数虽然简单，但属于阅读路标，不能随便跳过

## Working Rules

### 1. 先建立阅读定位

在任何图之前，先用一小段话说明：

- 这段代码或模块在系统里的位置
- 这次阅读建议从哪里开始
- 推荐按什么顺序跟进去
- 哪些函数是“路径路标”

语气要像在带人读源码，明确说“先看哪个，再看哪个”。
不要一上来就只给抽象架构图。

### 2. 输出三层执行流

必须同时输出下面三层，而不是只给一个高层图。

#### 第 1 层：高层总览顺序图

目标：

- 先让用户知道总体链路
- 只保留主要阶段

要求：

- 包含入口、核心分发、后端处理、返回路径
- 可以适度简洁，但不能只剩模块名
- 每条调用旁边都写简短中文解释

#### 第 2 层：源码阅读型详细顺序图

这是最重要的一层，默认投入最多篇幅。

目标：

- 让用户可以对照源码一步步往下读
- 尽量少跳函数
- 保留中间桥接、转发、封装、分发、调度函数

要求：

- 必须按真实阅读顺序展开
- 不要因为函数逻辑简单就省略
- 对下面这些函数默认不要跳过：
  - 入口函数
  - `dispatch` / `handle` / `process` / `route`
  - `enqueue` / `submit` / `schedule`
  - `callback` / `completion`
  - `prepare` / `init` / `open` / `create context`
  - `wrapper` / `adapter` / `bridge`
- 每一步调用都写中文解释，格式尽量接近：
  - `Foo -> Bar: doRead() 【把用户请求转成内部读任务】`

如果确实跳过了一些中间函数，必须单独说明：

- 省略了哪些函数
- 为什么可以省略
- 跳过后为什么不影响阅读主线

#### 第 3 层：重点节点下钻顺序图

目标：

- 对详细图里最容易迷路的 1 到 3 个节点继续往下拆
- 帮用户看清内部子调用链

要求：

- 优先选复杂节点、调度节点、状态切换节点、异步回调节点
- 展开它内部的子调用链
- 标清哪些函数真正做事，哪些只是转发

### 3. 顺序图必须使用 PlainUML 风格

所有顺序图都遵守这些规则：

- 图里必须写函数名，不能只写模块名
- 每条调用旁边都写中文短注释
- 如果函数名很泛，比如 `process`、`handle`、`run`，注释里必须写清它实际处理什么
- 如果链路里有返回值、错误、重试、异步回调，要在图里体现
- 对很长的链路，可以用 `note` 提醒“建议在这里停下来先读源码”

### 4. 还要给静态结构图

除顺序图外，再输出一个类图或模块图。

要求：

- 标出主要类、模块、组件
- 类里尽量写较多关键函数，不要只列 2 到 3 个
- 优先展示阅读主线相关的函数
- 标出依赖、组合、调用方向
- 用注释标明：
  - 哪些类更偏入口层
  - 哪些类更偏调度层
  - 哪些类更偏后端执行层
  - 哪些类更偏恢复或状态管理层

### 5. 关键函数表必须分层整理

不要只列少量函数，至少按下面几类整理：

- 入口函数
- 路由/分发函数
- 调度/队列函数
- 核心执行函数
- 状态更新/副作用函数
- 错误处理/恢复函数

表格必须包含以下字段：

| 函数名 | 所属类/模块 | 在阅读路径中的位置 | 主要行为 | 为什么这一步不能跳过 | 输入 | 输出 | 副作用 | 阻塞/异步 | 下一步应该看什么 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

其中这两列必须认真写：

- `为什么这一步不能跳过`
- `下一步应该看什么`

表格的目的不是罗列 API，而是让用户能顺着一路读下去。

### 6. 术语解释要贴着当前链路写

如果出现项目术语或系统术语，用下面格式解释：

- 注：xxx 是什么：一句人话解释
- 注：xxx 在这里的作用：它在当前调用链里负责什么

不要只给百科式定义，必须解释它在当前链路里干嘛。

### 7. 最后给可落地的阅读建议

收尾时必须给出源码阅读建议，至少包括：

- 推荐阅读顺序（函数级）
- 第一遍重点看什么
- 第二遍补哪些边角逻辑
- 哪些函数第一次可以只扫一眼
- 哪些函数必须停下来精读

## Output Structure

默认按下面结构输出，除非用户明确要求别的格式：

```markdown
## 阅读定位

## 已确认链路

## 待确认链路

## 第 1 层：高层总览顺序图

## 第 2 层：源码阅读型详细顺序图

## 省略函数说明

## 第 3 层：重点节点下钻顺序图

## 静态结构图

## 分层关键函数表

## 术语解释

## 源码阅读建议
```

如果当前链路已经足够确定，可以弱化“待确认链路”；如果信息不足，就必须保留“已确认链路”和“待确认链路”的区分。

## PlainUML Template

顺序图和结构图尽量使用下面这种 PlainUML 风格，注释保持中文：

```text
@startuml
actor Caller
participant Entry
participant Dispatcher
participant Worker

Caller -> Entry: read() 【进入入口函数】
Entry -> Dispatcher: dispatchRead() 【把请求交给分发层】
Dispatcher -> Worker: submitTask() 【提交到底层执行单元】
Worker --> Dispatcher: result 【返回处理结果】
Dispatcher --> Entry: status 【汇总执行状态】
Entry --> Caller: response 【返回给上层调用者】

note right of Dispatcher
建议在这里停下来先读源码，
先确认它如何选择后续分支。
end note
@enduml
```

### 静态结构图模板

```text
@startuml
class EntryLayer {
  +open()
  +read()
  +handleRequest()
}

class DispatchLayer {
  +dispatch()
  +route()
  +schedule()
}

class BackendLayer {
  +execute()
  +complete()
  +updateState()
}

EntryLayer --> DispatchLayer
DispatchLayer --> BackendLayer

note top of EntryLayer : 入口层
note top of DispatchLayer : 调度层
note top of BackendLayer : 后端执行层
@enduml
```

## Confirmed vs Unconfirmed

如果无法确认完整调用链：

- 不要编造缺失函数
- 明确写“这里是推测，需要继续点进源码确认”
- 把“已确认链路”和“待确认链路”分开
- 在图外补一句“下一步该点哪几个函数来确认”

## Style Rules

- 目标是帮人读源码，不是做 PPT 汇报
- 不要只讲抽象架构
- 不要把图画得过短
- 宁可适当长一点，也不要让调用链断层
- 所有说明都贴近“打开 IDE 一步步跟代码”的场景
- 语气自然，像有经验的工程师在带读源码

## Hard Bans

避免下面这些常见问题：

- 只给模块级架构，不给函数级入口
- 顺序图里跳过关键桥接函数
- 用“某模块调用某模块”替代真实函数名
- 对泛函数名不给上下文解释
- 把推测写成已确认事实
- 只给结论，不告诉用户下一步点哪里
