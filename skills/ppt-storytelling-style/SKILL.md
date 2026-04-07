---
name: ppt-storytelling-style
description: "Create or revise Chinese PPT decks in the user's latest preferred storytelling style: pain-first openings, progressive questioning, explicit year-by-year paradigm shifts, compressed Prompt sections, concrete mechanism explanations, four-layer system walkthroughs, layout variety, larger judgment-callout text, denser but controlled pages, and endings that turn personal practice into team capability. Use when Codex needs to make or revise PPT/PowerPoint/Slides for internal sharing, AI efficiency advocacy, engineering methodology talks, harness/spec/skill/context topics, experience sharing, proposal decks, or any presentation that should feel like a live talk with strong narrative control rather than a static document."
---

# PPT Storytelling Style

## Overview

Use this skill to shape the storyline before building slides. The target is not "cover everything"; it is "easy to listen to, easy to retell, and convincing in a live room".

The current preferred style has moved beyond generic pain-first storytelling. It now strongly favors:

- clear paradigm evolution over time
- concrete, reusable templates on key methodology pages
- detailed but speakable mechanism explanations
- system walkthroughs split by layers
- personal practice expanded into general workflow method
- less empty whitespace and more intentional information fill
- larger key statements on sparse pages
- multiple page rhythms instead of repeating the same three-column card layout
- compressed Prompt sections that quickly hand off to Context and Harness

When the user wants the actual `.pptx`, combine this skill with:

- `/Users/bytedance/.codex/skills/ppt-maker/SKILL.md`
- `/Users/bytedance/.codex/skills/slides/SKILL.md`

Read `references/style-guide.md` before outlining the deck.

## Workflow

### 1. Open from shared friction, not abstract definition

Start from something the listener has already felt.

Prefer openings like:

- `大家应该都经历过这个过程`
- `我们第一反应通常是什么`
- `这些翻车你们一定见过`

The audience should first feel:

- this is my real work
- this speaker has lived the same failure
- the conclusion is being earned step by step

### 2. Advance the deck by progressive questioning

Make the story move as a chain of answered questions:

1. what are we seeing now
2. why did the old response make sense
3. why is it becoming insufficient
4. what changed underneath
5. what is the new frame
6. how do we actually operate now

Do not jump directly from pain to framework. The transition is part of the persuasion.

### 3. Prefer explicit paradigm-shift storytelling

For methodology, AI workflow, and engineering-practice decks, show phase changes explicitly.

Typical pattern:

- `2023-2024：Prompt 工程`
- `2025：Context 工程`
- `2026：Harness 工程`

For each stage, answer both:

- what it solved at the time
- why it started to stop being enough

This deck style especially values "曾经重要，但现在开始不够" as a narrative device.

### 4. Treat slides as spoken beats, not document sections

Most slides should include:

- a speakable title
- one explicit takeaway sentence
- only the minimum support needed

If a slide reads like a wiki section or framework chapter, rewrite it until it sounds like something the speaker would actually say out loud.

Also ask:

- is this page too empty for its current amount of text
- should this page become a big-statement page instead of a normal card page
- does this deck already have too many pages with the same left-middle-right structure

### 5. Make mechanism pages denser, but still concrete

Theory is welcome when it answers a question the audience now genuinely cares about.

Preferred structure:

- pain
- question
- mechanism
- implication

When explaining why something worked or stopped working, always include at least one concrete example, micro-example, or counterexample.

Examples that fit this style:

- why prompt engineering worked
- why `You are an expert` started to degrade
- why context becomes insufficient in long tasks
- why harness creates team-level reuse

Important update:

- Prompt sections should usually be short, high-yield, and transitional
- Explain only enough to establish shared understanding
- Do not let Prompt theory take too much oxygen away from Harness
- Default goal: "Prompt 有用，但不够" rather than "把 Prompt 讲得更深"

### 6. Use four-layer walkthroughs for system/process explanation

When a concept is operational and can be decomposed, prefer splitting it into separate slides by layer instead of one big summary slide.

Strong default pattern:

1. `输入层`
2. `执行层`
3. `沉淀层`
4. `演化层`

Each layer slide should show:

- what the person does
- what the agent does
- which skill/spec/doc is involved
- what artifact is produced

This is especially important for harness/spec/knowledge topics.

### 7. Show the actual template when teaching a team method

If the deck says the team should use a `Spec`, `Experience Card`, `AGENTS.md`, or directory convention, show the template directly.

Preferred examples:

- `Spec` skeleton with `task / context / goal / constraints / verification`
- `经验卡` skeleton with `pattern / symptom / root_cause / fix / prevention / confidence`
- annotated repository tree
- `AGENTS.md` excerpt with rules and file-reading order

Do not merely describe the template. Put a usable version on the slide.

When a page has only one central idea, prefer a large highlighted statement box over several small cards.

### 8. Translate jargon into Chinese operational language

If a methodology page includes English fields or system terms, explain them in plain Chinese on the same slide or immediately adjacent slide.

Examples:

- `pattern` -> `问题模式`
- `symptom` -> `外在现象`
- `root_cause` -> `根本原因`

The goal is fast audience comprehension, not terminological purity.

### 9. Transition clearly when moving beyond coding

When the deck expands from engineering to broader office workflows, make the transition explicit in the title.

Prefer titles like:

- `除了 coding，其他工作也一样可以被 AI 提效`

Do not make the audience infer that scope shift on their own.

### 10. Land with concrete practice and upward abstraction

The ending should move like this:

1. real personal cases
2. extracted workflow principle
3. explicit team method or capability

Preferred closing logic:

- this PPT itself is a case
- these workflows are not random tricks
- they can be made explicit
- explicit workflows become skills
- skills become team capability

Do not end by repeating the taxonomy after several concrete cases.

### 11. Vary layout rhythm on purpose

Do not let the whole deck become:

- title
- takeaway bar
- three cards
- repeat

Actively vary the visual rhythm across the deck.

Good alternates:

- big-statement page with one large left or center text block
- left statement + right timeline
- top summary band + three lower blocks
- vertical top-middle-bottom progression
- one wide artifact box + one or two supporting callouts

At least a few pages in a substantial deck should visibly break the default card rhythm.

### 12. Fill pages more intentionally

The user dislikes pages where a text box is mostly empty.

When a page contains little text:

- increase font size
- make the core judgment more prominent
- let the key box occupy more area

When a page contains more text:

- still avoid clutter, but do not leave unnecessary dead space
- make the page feel intentionally filled rather than sparse by accident

Dense is acceptable if hierarchy is strong and the page still has one obvious focal point.

### 13. Make one-line judgments look important

Boxes titled like:

- `一句话判断`
- `一句话理解`
- `一句话抓手`

should not look like tiny helper notes.

They should usually have:

- larger text
- stronger weight
- clearer visual emphasis
- less empty padding relative to content

## Writing Rules

- Write in Chinese unless the user asks otherwise.
- Use short spoken assertions rather than academic exposition in slide bodies.
- Use visible one-line `结论：...` takeaways often.
- Make titles feel like claims, questions, or live transitions.
- Let examples do argumentative work; do not add examples as decoration.
- If a page teaches a process, show artifacts, templates, or commands.
- If a page includes English schema fields, add plain Chinese explanation nearby.
- Prefer "先让人感到痛，再给解释，再给方法，再给模板".
- For Prompt sections, prefer "快速建立共识 -> 快速指出边界 -> 快速让位给 Context / Harness".
- If one sentence carries the whole page, make that sentence large and central instead of surrounding it with weak filler.

## Visual Intent

- Keep the deck clean, modern, and high-signal.
- Favor stable alignment and restrained color contrast over flashy decoration.
- Prefer "serious internal strategy / methodology deck" over conference-keynote theatrics.
- Use dense pages only when they are template pages or mechanism pages with real explanatory value.
- Small example boxes are strongly encouraged.
- Annotated trees, template blocks, and micro-example boxes fit this style well.
- Avoid excessive empty space inside major boxes.
- Let sparse pages become bold pages, not empty pages.
- Strong pages should alternate between cards, wide bands, statement blocks, and mixed layouts.

## Deliverable Bias

When the user asks for a full deck, bias toward producing:

- `deck-brief.md`
- `deck-outline.md`
- editable source
- final `.pptx`

When the user asks to revise style, reflect the latest proven deck structure back into the outline before editing slides.

## References

- Read `references/style-guide.md` for the detailed slide patterns, title voice, template-page guidance, and anti-patterns.
