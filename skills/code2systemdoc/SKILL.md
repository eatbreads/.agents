---
name: code2systemdoc
description: Transform source code (single file, module, or repository) into a narratable system model and interview-ready architecture document. Use when Codex needs to read unfamiliar code, explain end-to-end execution flow, output PlantUML sequence diagrams, extract module and function responsibilities, summarize key mechanisms (loop/state/IO/dataflow), prepare design-review notes, or generate interview-style explanations.
---

# Code2SystemDoc

## Goal
Convert code into a system model that can be explained clearly to engineers or interviewers. Prioritize architecture reasoning over feature summary.

## Inputs
- Required: code scope (`file`, `module`, or `repository root`)
- Optional: focus modules, runtime scenario, output language, depth (`quick`/`standard`/`deep`)

If scope is ambiguous, infer a reasonable default from the request and state the assumption explicitly.

## Workflow

### 1) Structure Scan
- Locate entrypoints (`main`, CLI command handlers, API routers, workers, schedulers)
- Identify orchestration modules vs execution modules
- Build a high-signal caller-to-callee map for critical paths

### 2) Main Flow Reconstruction
- Reconstruct one canonical chain:
  `User/Event -> Entry -> Orchestration -> Core Execution -> IO -> Response`
- Add at most two alternate branches only when they materially change behavior (retry/error/async)

### 3) Module Responsibility Extraction
For each core module, state:
- Responsibility: what problem it solves
- Boundary: what it does not solve
- Position: where it sits in the main chain
- Dependencies: upstream/downstream interactions

### 4) Mechanism Extraction
Analyze and summarize:
- Control loop (retry/termination/backoff)
- State model (session/context/cache/memory ownership and lifecycle)
- IO model (tool, network, file, DB side effects)
- Dataflow (`input -> transform -> output`)
- Reliability hooks (timeout, fallback, idempotency, error propagation)

### 5) Function-Level Explanation
Pick 3-8 highest-leverage functions and explain:
- Inputs
- Outputs
- Core behavior and side effects
- Preconditions/invariants
- Failure path
- Why this function is central

### 6) UML Generation (Mandatory)
Output one PlantUML sequence diagram that represents the canonical main flow.
- Include only major participants
- Keep arrows aligned with actual call semantics
- Use `loop` / `alt` blocks for retry/error branches when needed

### 7) Design Rationale (WHY)
Explain:
- Why a simpler approach is insufficient
- Which concrete problems this design solves
- Main tradeoffs introduced by the current design

### 8) Interview Expression Layer (Mandatory)
Produce:
- One-sentence system thesis
- Three-layer architecture narrative (max 3 layers)
- 30-second spoken answer
- 2-minute spoken answer
- 3 likely follow-up questions with concise answers

## Evidence and Accuracy Rules
- Distinguish `Observed` vs `Inferred` claims.
- Attach code anchors (`path:line`) for key technical claims.
- Do not invent modules or interactions not grounded in code.
- If full coverage is impossible, declare analyzed scope and blind spots.

## Output Contract
Return exactly these sections in this order:

```markdown
# 一、系统流程（UML）
# 二、核心链路
# 三、模块职责
# 四、函数说明
# 五、关键机制
# 六、设计思想
# 七、面试表达
```

Use concise bullets. Avoid long narrative paragraphs.

## Optional Advanced Modes
Load [references/advanced-modes.md](references/advanced-modes.md) only when the user explicitly requests one of these:
- Code -> UML + Class Diagram
- Code -> Interview Q&A Set
- Code -> Debug Entrypoint Map
- Architecture Comparison (for example, OpenClaw vs LangGraph vs AutoGPT)
