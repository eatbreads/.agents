---
name: doc-to-ai-solution
description: "Turn a set of meeting notes, technical docs, design notes, postmortems, AI practice summaries, or mixed document collections into a concrete analysis output: one-line insight, problem breakdown, root cause, actionable requirements, AI solution design, pipeline/workflow changes, priorities, and risks. Use when the user provides multiple documents or document titles and wants a synthesized engineering judgment instead of a summary, especially for stability, quality, efficiency, workflow, review, test, observability, or AI-engineering topics. When the source material lives in Feishu/Lark docs, first use the lark-doc skill to search and fetch the documents before analyzing them."
---

# Doc To AI Solution

## Overview

Use this skill to transform a pile of documents into a decision-ready engineering output.
Do not stop at summarization. Extract the real problems, name the deeper cause, turn them into buildable tasks, and design an AI solution that can plug into an existing engineering system.

## Workflow

### 1. Gather the source material first

If the user gives document URLs, tokens, or Feishu document titles, treat document retrieval as part of the job.

For Feishu/Lark documents:
- Read [`../lark-doc/SKILL.md`](../lark-doc/SKILL.md) first.
- Before searching, read [`../lark-doc/references/lark-doc-search.md`](../lark-doc/references/lark-doc-search.md).
- Before fetching, read [`../lark-doc/references/lark-doc-fetch.md`](../lark-doc/references/lark-doc-fetch.md).
- Use `lark-cli docs +search` to locate documents by title when the user gives names instead of links.
- Use `lark-cli docs +fetch` to read the matched documents.

Document matching rules:
- Prefer exact title matches.
- If there are multiple plausible matches, use the strongest title match plus summary context.
- If the match is still ambiguous, say so briefly and avoid pretending certainty.

### 2. Build an evidence table before writing

For each document, extract only the parts that matter for synthesis:
- what problem is being described
- what current process or system exists
- what pain repeatedly shows up
- what constraints are real
- what concrete actions or TODOs are already mentioned
- what signals suggest the deeper cause

Then merge overlapping signals across documents.

Do not analyze each document in isolation. The point is to identify repeated patterns, contradictions, and missing links across the full set.

### 3. Decide the real topic

Do not assume the topic is always pipeline optimization.

Infer the actual focus from the documents:
- stability
- testing quality
- review quality
- workflow efficiency
- observability
- failure analysis
- AI engineering practices
- documentation and knowledge flow
- cross-team execution

If the documents span several areas, pick the dominant problem and explain the other areas as supporting factors.

### 4. Convert symptoms into engineering structure

Move in this order:
1. symptoms and friction
2. repeated patterns
3. deeper cause
4. buildable requirements
5. AI system design
6. workflow or pipeline change

Do not jump straight from "the docs mention AI" to "build an AI platform".
Anchor every conclusion in evidence from the source material.

### 5. Write requirements that can become tasks immediately

Every requirement must be task-shaped.

Each requirement must include:
- `Input`
- `Output`
- `Acceptance`

Good requirement example:
- Input: MR diff, rule set, existing comments
- Output: structured review findings with rule IDs and confidence
- Acceptance: runs on every MR, deduplicates repeated comments, exposes false-positive rate

Bad requirement example:
- "Use AI to improve review quality"

### 6. Design AI as part of the existing system

All AI proposals must connect to real engineering surfaces:
- MR pipeline
- CI / nightly pipeline
- logs
- metrics
- docs
- ticket systems
- test frameworks
- repo conventions

Do not propose demo-style features.
Do not write vague ideas like "an AI assistant helps engineers".

Spell out:
- architecture layers
- modules
- integration points
- what data each module consumes
- what artifact each module emits

### 7. Use the fixed output structure

Unless the user explicitly requests a different format, output exactly these sections:

1. `一句话总结`
2. `问题拆解`
3. `本质原因`
4. `可落地需求`
5. `AI解决方案设计`
6. `流水线改造`
7. `优先级建议`
8. `风险与限制`

If the topic is not literally a pipeline problem, keep section 6 but broaden it to workflow/system execution changes. You may still label it `流水线改造（Before/After）` and interpret "pipeline" as the current execution flow.

## Writing Rules

- Use plain language a strong engineer would use with teammates.
- Start with a sharp insight, not a soft summary.
- Be specific. Name the broken loop, missing abstraction, or execution gap.
- Do not dump jargon when a simple explanation is clearer.
- Do not write "可以考虑", "可能可以", "进一步优化", or similar weak filler.
- If a fact is missing, say what is missing and what that limits. Do not invent.
- If one document is thin and another is rich, weight the richer evidence more heavily.

## Output Constraints

### 1. 一句话总结

Make it decisive. It should identify the real bottleneck, not restate the topic.

### 2. 问题拆解

Explain the pain in human terms:
- where people are spending effort
- what stays manual
- what repeats
- what cannot scale

### 3. 本质原因

Go one level deeper than the observed problem.
Typical examples:
- data exists but is not machine-usable
- rules exist but are not executable by default
- workflows exist but have no closed-loop feedback
- quality checks exist but are not structured enough for automation

### 4. 可落地需求

Use a numbered list.
For each item include:
- `Input:`
- `Output:`
- `Acceptance:`

Requirements must be implementation-ready.

### 5. AI解决方案设计

Include:
- overall architecture
- module list
- module responsibility
- integration point into the current system

### 6. 流水线改造

Always use `Before` and `After`.
Show what changes in the real engineering flow, not just in the analysis layer.

### 7. 优先级建议

Use `P0 / P1 / P2`.
Prioritize based on engineering leverage, not presentation polish.

### 8. 风险与限制

Be honest about:
- missing structure in source docs
- hidden dependencies on permissions, owners, or data quality
- where AI is strong
- where AI still cannot replace human judgment

## Fast Pattern

When the documents are about engineering effectiveness, this pattern is often useful:
- documents are rich in experience but weak in structure
- recurring problems are visible to humans but not queryable by machines
- the real task is converting human-facing process into machine-facing semantics

When that pattern appears, say it directly and turn it into:
- structured event model
- rule engine
- workflow orchestration
- feedback and evaluation loop

## Minimum Deliverable

If the document set is incomplete, still produce the full 8-section output.
In that case:
- keep conclusions conservative
- make requirements concrete
- push uncertainty into `风险与限制`
