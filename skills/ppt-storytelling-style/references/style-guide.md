# Style Guide

Use this reference when building decks in the user's latest preferred presentation style.

## 1. Overall Personality

The deck should feel like:

- a live internal talk
- a methodology share with narrative control
- a serious engineering argument with concrete operating detail
- a deck with intentional visual hierarchy, not a well-formatted document

It should not feel like:

- a copied report
- a wiki dump
- a consulting slide wall
- a generic "AI overview" with no lived perspective
- a deck where every page uses the same structure
- a deck with large boxes containing too little text

## 2. Core Preferences

### Pain first

Prefer:

- show recognizable friction first
- let the audience nod first
- only then define the concept

Avoid:

- opening with abstract taxonomy
- opening with a definition page when a pain page would do better

### Progressive questioning

The user likes decks that unfold as a sequence of answered questions.

Strong sequence:

1. 大家现在到底遇到了什么
2. 我们第一反应为什么会这样
3. 为什么这套反应开始失效
4. 底层到底变了什么
5. 所以新的工作框架是什么
6. 我们接下来具体怎么做

### Paradigm-shift feeling

When the topic is about AI engineering practice, system design, or workflow change, show explicit phase transitions.

Good devices:

- year labels
- phase labels
- `从 A 到 B，再到 C`
- `曾经重要，但现在开始不够`

### Explicit takeaway sentence

Most slides should have a visible takeaway bar such as:

- `结论：问题不再只是“怎么问”，而是“怎么让 AI 在长任务里持续做对”。`

This is a major part of the user's preferred deck rhythm.

### Bigger focal statements

If a page has one main judgment, make it visibly large.

Good pattern:

- sparse text -> larger font
- fewer blocks -> bolder statement
- less explanation -> more visual emphasis

Avoid:

- leaving a large box mostly empty
- letting the key sentence look like a footnote

### Operational artifact bias

When teaching a team methodology, show the actual artifact instead of describing it abstractly.

Preferred artifact types:

- spec template
- experience-card template
- AGENTS.md snippet
- annotated directory tree
- small prompt or command example

### Prompt compression bias

Prompt sections should be shorter than they were before.

What to preserve:

- Prompt had value
- Prompt worked for single-turn quality
- Prompt has clear boundaries

What to avoid:

- over-explaining Prompt theory
- letting Prompt consume too much deck time
- making Prompt feel like the main topic when Harness is the main topic

## 3. Preferred Slide Types

### A. Shared-experience opener

Purpose:

- create immediate resonance

Typical titles:

- `大家应该都经历过这个过程`
- `这些翻车你们一定见过`

### B. Instinct-vs-reality slide

Purpose:

- show the audience's default reaction
- prepare the need for a new frame

Typical title:

- `我们第一反应通常是什么`

### C. Paradigm-shift slide

Purpose:

- explain why the dominant engineering frame changed over time

Typical title:

- `但这其实是范式变化，不是技巧问题`

Preferred visual form:

- large left-side statement
- right-side timeline or compact phase structure
- not necessarily the default title + three cards layout

### D. Mechanism slide

Purpose:

- answer "why" at a deeper level

Examples:

- why prompt worked
- why external structure mattered
- why some prompts now degrade
- why harness adds value beyond context

Rules:

- may be denser than ordinary slides
- still needs one clear takeaway
- still needs one concrete example or counterexample
- if the page is only making one mechanism point, prefer one large statement box over multiple weak cards

### E. Failure-pattern slide

Purpose:

- name recurring failure modes so the room can recognize them instantly

Good examples:

- 任务漂移
- Context anxiety
- 虚假完成
- 自评偏乐观

### F. Four-layer walkthrough slide group

Purpose:

- explain a system or workflow through operational layers

Preferred sequence:

1. 输入层
2. 执行层
3. 沉淀层
4. 演化层

Each page should show:

- what the human says or does
- what the agent does
- what skill/spec/doc gets used
- what output artifact is produced

### G. Template page

Purpose:

- make the method immediately reusable

Typical examples:

- Spec 模板
- 经验卡模板
- ai-harness/ 目录树
- AGENTS.md 工作规则

Rules:

- allow denser content than normal
- use code/text blocks
- annotate with plain Chinese where needed

### H. Large-statement page

Purpose:

- make one judgment impossible to miss

Good uses:

- cover / opener
- paradigm shift page
- prompt boundary page
- transition into Harness

Rules:

- use much larger text than ordinary pages
- let the statement occupy real area
- do not surround it with decorative filler just to balance the page

### I. Practice / workflow slide

Purpose:

- prove the framework already works outside theory

Typical pattern:

- what the work used to look like
- what the agent does now
- why this changes leverage

### J. Mixed-rhythm slide

Purpose:

- break repetition after too many card pages

Good patterns:

- top band + three lower cards
- top summary box + two lower boxes
- left statement + right system diagram
- upper-wide box + lower staggered cards

### K. Ending slide

Purpose:

- turn personal practice into team method

Preferred closing move:

- 个人案例
- workflow 显式化
- 团队能力

## 4. Title Voice

Prefer titles that sound speakable and mildly provocative:

- `为什么到了 2026，Context 也开始不够`
- `没有 Harness vs 有 Harness，差别到底在哪`
- `如果不写 runtime，只靠文档，Harness 还能不能落地`
- `除了 coding，其他工作也一样可以被 AI 提效`

Avoid weak generic titles:

- `背景介绍`
- `方案概述`
- `经验分享`
- `总结`

## 5. Bullet Style

- Keep bullets short.
- Bullets should sound like spoken assertions.
- Avoid long academic bullets.
- If a point needs explanation, either give it a mini example box or make it a separate slide.
- If a page can be reduced to one strong sentence, do that instead of keeping several mediocre bullets.

## 6. Layout Rhythm

Avoid making nearly every page:

- title
- takeaway
- three side-by-side cards

The user now explicitly prefers more variation.

In a substantial deck, deliberately include:

- 2-4 large-statement pages
- 2-3 mixed-rhythm pages
- some vertical progression layouts
- some artifact-heavy pages

## 7. Example Boxes

Use small example boxes aggressively when they carry real explanatory value.

Good uses:

- a concrete prompt
- a spec skeleton
- an experience-card skeleton
- a directory tree with annotations
- a human/agent interaction snippet
- a before-vs-now workflow

These boxes should support the argument, not decorate the page.

Special rule for boxes named:

- `一句话判断`
- `一句话理解`
- `一句话抓手`

Make them more prominent than ordinary example boxes.

## 8. Language Handling

When technical English is necessary:

- keep the field names if they matter operationally
- add plain Chinese explanation next to them or on the same slide

Examples:

- `pattern：问题模式`
- `symptom：外在现象`
- `root_cause：根本原因`

The user strongly prefers not to leave the room behind with unexplained English schema terms.

## 9. Space Management

Do not leave large unused space inside major text areas if the page is supposed to make a strong point.

Preferred fixes:

- enlarge the sentence
- enlarge the box
- reduce competing elements
- switch to a statement-page layout

## 10. Scope Transition Rules

If the deck moves from coding productivity to broader work productivity:

- announce that scope change explicitly in the title
- make it feel like a deliberate expansion, not a sudden topic jump

Preferred move:

- `除了 coding，其他工作也一样可以被 AI 提效`

## 11. Anti-Patterns

Avoid:

- too many generic category slides in a row
- giant evidence dumps with no takeaway
- pure abstraction after several concrete examples
- untranslated English-heavy schema pages
- ending with taxonomy after the audience has already bought into practice
- non-coding practice pages with weak transition titles
- overly sparse statement boxes
- repeating the same left-middle-right card grid too many times
- spending too long explaining Prompt when Harness is the real subject

## 12. Default Ending Formula

When unsure, close the deck with this logic:

1. these were real personal practices
2. they are not random tricks
3. they can be written down and standardized
4. standardized workflows become reusable skills
5. reusable skills become team capability
