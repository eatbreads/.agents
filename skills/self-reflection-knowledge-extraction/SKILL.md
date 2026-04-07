---
name: self-reflection-knowledge-extraction
description: "Extract reusable engineering knowledge after a task succeeds. Use when Codex finishes a coding, debugging, CI, pipeline, agent workflow, or root-cause-analysis task and needs to turn the successful process into reusable knowledge instead of a plain summary. Support three output modes: direct output in chat, emit a registerable skill draft, or write a standalone knowledge card to a specified location. If the user does not specify an output mode, default to direct output."
---

# Self Reflection And Knowledge Extraction

Turn one successful task into reusable knowledge that makes future tasks faster and more reliable.

## Operating Rule

Do not write a narrative summary of the whole process.
Extract only knowledge that can be reused next time.

Prioritize:
- decision patterns
- recognition signals
- narrowing strategies
- standard debug flow
- anti-patterns
- compact knowledge cards

Ignore:
- repetitive chronology
- code restatement
- low-signal trial-and-error
- long diffs unless they prove the cause

## Inputs To Collect

Gather these if available from the current task context:
- task goal
- final successful result
- key failed attempts
- important logs or error messages
- important code changes or operational steps
- root cause, if confirmed
- constraints that shaped the solution

If some inputs are missing, continue with the available evidence and mark uncertain parts explicitly.

## Output Mode Selection

Choose one output mode before writing:

### Mode 1: `direct`

Use when the user asks to "直接输出", "直接给我复盘", "先产出内容", or gives no destination.
Output the full reflection directly in chat.

### Mode 2: `register-skill`

Use when the user asks to register this as a skill, save as a reusable Codex skill, or place it under a skills directory.
Output:
- suggested skill name
- `SKILL.md` content
- optional recommended folder path

Do not assume filesystem write unless explicitly asked.

### Mode 3: `knowledge-card`

Use when the user asks to沉淀经验卡, save to a knowledge base, or provides a target path.
Output:
- one final experience card
- suggested filename
- target location if provided

If the user does not specify a mode, default to `direct`.

## Direct Output Format

Use this exact structure for `direct` mode.

### 1. 任务概述

```text
【任务类型】：
【目标】：
【结果】：
```

Write this section briefly in 3 lines.

### 2. 成功路径

Keep only the path that actually worked.

```text
Step1：
Step2：
Step3：
...
```

For each step, explain why it was effective.
Delete dead ends unless they are needed to understand the eventual success path.

### 3. 关键决策点

Extract the judgments that most reduced search space.

```text
- 决策1：为什么选择这个方向？
- 决策2：为什么放弃之前方案？
- 决策3：如何定位问题范围？
```

Answer the practical question:
"If this happened again, how would we get to the right answer faster?"

### 4. 问题模式抽象

Generalize from the specific case.

```text
【问题模式】：
【识别信号】：
【本质原因】：
【通用解法】：
```

Write this as a reusable pattern, not a one-off story.

### 5. 可复用排查流程

Standardize the workflow.

```text
1. 先看 xxx
2. 再检查 xxx
3. 如果是 xxx，就执行 xxx
4. 否则走分支 xxx
```

Keep it operational and branch-aware.

### 6. 反模式

Capture wasted motion.

```text
本次低效/错误的尝试：

- 错误1：xxx（为什么错）
- 错误2：xxx（为什么浪费时间）

避免方式：
- 下次直接跳过这些路径
```

Only include anti-patterns that are broadly useful.

### 7. 经验卡

This is the final reusable artifact.

```text
【标题】：
【适用场景】：
【核心结论】：
【快速排查步骤】：
【关键指标/信号】：
【推荐操作】：
```

This section should be self-contained and reusable without the rest of the reflection.

## Registerable Skill Output Format

If mode is `register-skill`, output these sections:

### A. 建议技能名

Use lowercase letters, digits, and hyphens only.

### B. `SKILL.md`

Emit a complete `SKILL.md` draft.

### C. 建议放置位置

Use the user-provided path if given.
Otherwise recommend:
`${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>/SKILL.md`

### D. 可选扩展

Recommend optional bundled resources only if truly useful, for example:
- `references/knowledge-card-template.md`
- `scripts/save_experience_card.sh`

Do not invent extra files unless they clearly improve repeated use.

## Knowledge Card Output Format

If mode is `knowledge-card`, output only:

```text
建议文件名：
目标位置：

【标题】：
【适用场景】：
【核心结论】：
【快速排查步骤】：
【关键指标/信号】：
【推荐操作】：
```

Keep it short enough to store and retrieve efficiently.

## Compression Rules

When the source task is long or noisy:
- collapse repeated failed attempts into one anti-pattern
- keep at most 3 to 5 key decisions
- keep at most 4 to 6 troubleshooting steps
- keep the experience card under 12 lines

## Quality Bar

A good result should let a future agent:
- recognize a similar problem faster
- skip obviously bad paths
- choose a likely-good debugging order
- reuse the final knowledge card without rereading the full case

If the draft still reads like a story, rewrite it into a decision aid.
