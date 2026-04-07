---
name: project-to-question-tree
description: Transform a software project, repository, design document, or project summary into layered interview question trees with connected follow-up chains. Use when Codex needs to act like a strict interviewer and generate progressive backend, systems, storage, infrastructure, performance, or agent/runtime questions that test concept, mechanism, design rationale, implementation depth, tradeoffs, optimization choices, and fundamental OS/network/storage understanding.
---

# Project to Question Tree

## Goal
Turn a project into a reusable interview pressure-test that separates surface familiarity from real understanding.

## Inputs
- Require project material: repository, design document, architecture summary, or user-provided explanation.
- Accept optional hints: target role, desired strictness, domain bias, language, and number of themes.
- Accept optional focus areas such as storage engine, networking, scheduling, reliability, concurrency, or agent runtime.

If the project material is broad, choose the highest-signal technical themes instead of covering everything shallowly.

## Core Question Model
Build each chain with progressive depth:
- Q1: concept or high-level purpose
- Q2: mechanism or execution path
- Q3: design reason or tradeoff
- Q4: implementation detail or failure mode
- Q5: comparison, optimization, or extension
- Q6: deep-water follow-up when the topic clearly supports it

Keep the chain continuous. Each later question should naturally pressure-test the previous answer.

## Workflow

### 1. Extract Evaluation Axes
Prioritize:
- Architecture design
- Core technical mechanisms
- Performance and scalability
- Reliability and correctness
- OS, networking, storage, or runtime fundamentals
- Tradeoffs and rejected alternatives

### 2. Merge Related Topics
- Combine overlapping questions into one stronger theme.
- Avoid producing scattered trivia.
- Prefer 4-8 strong themes over many weak ones.

### 3. Build Follow-Up Chains
- Start with an easy entry point.
- Move toward mechanism, then tradeoff, then implementation pressure.
- End with optimization, comparison, or failure-mode discussion.

### 4. Match the User's Interview Style
- If the user asks for strict or high-pressure output, make questions pointed and probing.
- If the user asks for systems or storage emphasis, bias toward execution model, concurrency, IO path, data layout, memory ownership, recovery, and tradeoffs.
- If the user asks for mock interview practice, prefer questions that a human interviewer can ask aloud without extra context.

## Working Rules
- Ground questions in the project instead of asking generic textbook prompts only.
- Use fundamentals to deepen the project discussion, not to derail it.
- Prefer question chains that distinguish `used the technology` from `understands why it works`.
- Do not answer the questions unless the user explicitly asks for answer keys.

## Output Contract
Return exactly these sections in this order:

```markdown
【一、项目核心考察点总结】
【二、问题树（多个主题）】
```

For each theme, use this exact pattern:

```markdown
=== 主题：xxx ===

Q1：
Q2：
Q3：
Q4：
Q5：
```

Add `Q6：` only when the theme clearly supports a deeper extension.

## Output Requirements
- Make questions concise and oral-interview friendly.
- Make the order feel like a real interrogation path, not a random list.
- Keep each theme internally coherent.
- Let the full set cover architecture, core mechanism, performance,底层原理, and tradeoff.
