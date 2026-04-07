---
name: ppt-maker
description: Plan, write, and build editable PowerPoint decks from a topic, outline, Markdown notes, meeting notes, research docs, or an existing presentation. Use when Codex needs to create or revise PPT/PowerPoint/Slides content, turn raw material into a slide storyline, generate slide-by-slide outlines, prepare speaker notes, or produce an editable `.pptx` deck for business reviews, project updates, technical sharing, training, sales, or interview presentations.
---

# PPT Maker

## Overview

Turn rough material into a clear presentation, then produce editable slide artifacts. Prefer a two-stage workflow:

1. Shape the narrative and slide structure.
2. Build the final editable deck as `.pptx`.

When the task includes actual PowerPoint generation, use the installed `slides` skill at `/Users/bytedance/.codex/skills/slides` as the rendering and validation layer.

## Workflow

### 1. Build the brief

Extract or infer:

- audience
- presentation goal
- single key takeaway
- desired tone
- target length or slide count
- source material available

If the user does not provide all of these, make reasonable assumptions and state them briefly in the output.

### 2. Choose the deck shape

Default to one of these structures:

- status update: context -> progress -> evidence -> risks -> next steps
- proposal: problem -> why now -> options -> recommendation -> plan
- technical sharing: background -> architecture -> mechanism -> tradeoffs -> demo/results
- training: objective -> concepts -> examples -> practice -> summary
- sales or pitch: audience pain -> solution -> proof -> offer -> call to action

Load `references/deck-patterns.md` when you need more detailed slide patterns.

### 3. Write the slide-by-slide outline

For each slide, define:

- slide title
- one-sentence takeaway
- 3-5 supporting bullets or visual instructions
- optional speaker note

Keep each slide focused on one message. Merge or split slides instead of overloading them.

### 4. Decide the deliverable depth

Choose the lightest output that satisfies the request:

- outline only: deliver Markdown with slide titles and bullets
- content package: deliver brief + outline + speaker notes
- full deck: deliver Markdown planning files plus editable `.pptx`

If the user asks for a PPT, default to the full deck.

### 5. Build the deck

When generating the actual presentation:

- use the `slides` skill for `.pptx` authoring
- keep the source editable and deliver both `.pptx` and authoring source
- default to 16:9 unless the reference material clearly uses another ratio
- preserve text as text and simple charts as editable chart objects whenever practical

## Content Rules

- Lead with the conclusion when the audience is business-facing.
- For technical decks, explain why something matters before diving into mechanism.
- Prefer short assertions over paragraph blocks.
- Put numbers, comparisons, and examples on slides that make claims.
- Limit each slide to one core message.
- When the source material is dense, summarize aggressively and move detail into speaker notes.

## Visual Rules

- Prefer simple layouts with stable alignment and generous whitespace.
- Use charts, diagrams, tables, or comparison blocks when they clarify faster than bullets.
- Avoid decorative elements that do not support the message.
- Keep terminology, capitalization, and color usage consistent across slides.

## Output Package

When building a full deck, produce these artifacts when practical:

- `deck-brief.md`: audience, goal, takeaway, assumptions
- `deck-outline.md`: slide-by-slide structure
- `speaker-notes.md`: optional presenter notes
- editable slide source used to generate the deck
- final `.pptx`

If render validation is needed, also keep rendered preview images until the deck is accepted.

## References

- Load `references/deck-patterns.md` for reusable presentation structures and per-slide guidance.
- Load `/Users/bytedance/.codex/skills/slides/SKILL.md` only when you need to author or validate the actual `.pptx`.
