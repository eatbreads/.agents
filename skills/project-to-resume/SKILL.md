---
name: project-to-resume
description: Transform a software project, repository, design note, or architecture summary into resume-ready bullets and interview-ready project storytelling. Use when Codex needs to help a user present project experience for resumes, job applications, mock interviews, self-introductions, or achievement summaries, especially for backend, systems, storage, infrastructure, performance, or agent/runtime projects.
---

# Project to Resume

## Goal
Convert raw project material into hiring-signal outputs that are concise, technically credible, and easy to speak aloud.

## Inputs
- Require project material: repository, architecture document, notes, or a user summary.
- Accept optional targeting hints: role, seniority, domain, company style, language, and desired emphasis.
- Prefer concrete evidence such as scale, latency, throughput, cost reduction, reliability improvement, or team ownership when available.

If the input is incomplete, infer structure and impact cautiously, but do not invent metrics, benchmarks, or ownership claims.

## Working Rules
- Reframe from "built X" to "solved Y with Z".
- Emphasize architecture depth, performance work, reliability choices, and technical tradeoffs.
- Prefer bullets in `action + technical method + result` form.
- Quantify only when numbers are explicitly provided or strongly grounded in supplied evidence.
- If metrics are missing, use qualitative impact such as `reduced latency`, `improved throughput`, or `simplified recovery path` instead of fake numbers.
- Avoid generic praise such as `optimized performance a lot` or `improved the system significantly`.

## Workflow

### 1. Extract the Project Thesis
- Identify the problem the project solves.
- Identify the technical bet that makes the project interesting.
- Identify why the implementation is non-trivial.

### 2. Find Resume Signals
Prioritize:
- Architecture and system decomposition
- Core algorithms or execution model
- Performance and scalability work
- Reliability, correctness, and operability
- Tradeoffs and why the chosen design was justified

### 3. Convert Into Resume Language
- Compress low-signal implementation details.
- Keep the hardest technical decisions.
- Surface user impact, engineering impact, or business relevance.
- Favor strong verbs such as `designed`, `implemented`, `optimized`, `re-architected`, `hardened`, `built`, `reduced`, or `improved`.

### 4. Convert Into Spoken Interview Language
- Make the 1-minute version high-level and easy to follow.
- Make the 3-minute version explain architecture, key mechanism, and tradeoff.
- Preserve technical precision; do not turn the project into a product pitch.

## Output Contract
Return exactly these sections in this order:

```markdown
【一、项目一句话总结】
【二、简历 Bullet（3-5 条）】
【三、面试 1 分钟讲解】
【四、面试 3 分钟深挖版本】
【五、技术亮点（面试加分点）】
```

## Output Requirements
- Write bullets that are dense enough to paste into a resume with minimal edits.
- Keep each bullet focused on one technical contribution.
- Make the one-sentence summary readable by a hiring manager and still credible to an engineer.
- Make the spoken sections sound like natural interview answers, not written prose.
- Make the technical highlights explicitly answer `why this project is impressive`.

## Style Control
- If the user asks for systems, storage, backend, infra, high-performance, or agent/runtime emphasis, bias toward architecture, concurrency, IO model, memory/state handling, performance tuning, and tradeoffs.
- If the user asks for junior-friendly output, simplify wording without removing the key mechanism.
- If the user asks for senior or staff-level output, increase emphasis on system boundaries, design rationale, and operational consequences.
