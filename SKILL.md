---
name: inkos-like-novel-os
description: Novel-production operating system for long-form fiction, web novels, serials, fanfiction, and side stories. Use when designing or running a structured writing pipeline with persistent world state, chapter summaries, hooks, character matrices, continuity audits, rewrite/revise loops, style guides, or per-book rules. Best for requests like building an InkOS-like skill, creating a long-novel workflow, keeping multi-chapter story consistency, generating/auditing/revising chapters, or maintaining story files across many chapters.
---

# inkos-like-novel-os

Build and run long-form fiction as a stateful pipeline, not a one-shot prompt.

Treat this skill as a **novel OS skeleton**: it provides project structure, workflow, audit criteria, and helper scripts for an OpenClaw-based writing system that is conceptually close to InkOS.

## Core operating model

Use this loop:

1. **Load truth files**
2. **Plan the next chapter**
3. **Draft with constraints**
4. **Audit for continuity / style / pacing / leaks**
5. **Revise with spot fixes first**
6. **Update story state**
7. **Queue unresolved issues for human review**

Prefer stable files over fragile memory. If information matters in later chapters, write it into a truth file.

## Project layout

When starting a new project, copy the template from `assets/project-template/`.

Expected files:

- `story_bible.md` — world rules, premise, factions, locations, power system
- `book_rules.md` — per-book rules, prohibitions, protagonist locks, tone limits
- `outline.md` — macro arc, chapter targets, payoff plan
- `current_state.md` — authoritative latest world state
- `chapter_summaries.md` — per-chapter summaries and state deltas
- `pending_hooks.md` — open promises, foreshadowing, unresolved conflicts
- `character_matrix.md` — who met whom, trust/conflict, information boundaries
- `emotional_arcs.md` — tracked emotional movement by key character
- `subplot_board.md` — A/B/C line progress and stagnation notes
- `continuity_issues.md` — known inconsistencies or manual review backlog
- `style_guide.md` — qualitative style guide
- `style_profile.json` — optional quantitative style stats
- `chapters/` — chapter markdown files
- `reviews/` — audit and revision reports

`current_state.md` is the most important operational file. Keep it compact, current, and explicit.

## Workflow

### 1) Initialize a project

Run:

```bash
bash scripts/init_novel_project.sh /path/to/project "Book Title"
```

This copies the template and creates the standard directory layout.

### 2) Before writing a chapter

Read at least:

- `story_bible.md`
- `book_rules.md`
- `outline.md`
- `current_state.md`
- latest section of `chapter_summaries.md`
- `pending_hooks.md`
- `character_matrix.md`

If the request is for a side story, prequel, sequel, or alternate timeline, also establish:

- parent canon constraints
- divergence point
- what characters do **not** know yet
- which original hooks must remain untouched

### 3) Planning rules

Before drafting, explicitly decide:

- chapter purpose
- POV
- conflict driver
- payoff or partial payoff
- hooks to advance, delay, or close
- state changes that must occur
- constraints that must not be violated

Write a short chapter plan into the response or a scratch file if useful.

### 4) Drafting rules

Draft from observed reality, not abstract explanation.

Prefer:

- concrete action
- sensory evidence
- state changes that can be tracked later
- character knowledge limited to what they have seen, inferred, or been told

Avoid:

- breaking protagonist personality lock
- introducing untracked items/powers/injuries
- resolving major hooks accidentally
- report-speak in narrative prose
- broad whole-crowd reactions unless earned
- full-chapter rewrites when only a few lines are broken

### 5) Audit pass

After drafting, audit against `references/audit-dimensions.md`.

Minimum audit set:

- continuity / timeline
- character consistency
- information boundary leaks
- world-rule violations
- unresolved logic gaps
- pacing / subplot movement
- repetitive diction / fatigue terms
- outline drift

Write reports into `reviews/` when operating on files.

### 6) Revision policy

Prefer this order:

1. **spot-fix** — patch only bad sentences/paragraphs
2. **polish** — improve local expression without changing story events
3. **rewrite scene** — only if scene logic is broken
4. **rewrite chapter** — last resort

Do not silently change:

- names
- outcomes of key events
- resource counts / power levels
- relationship states
- what characters know

If any of the above changes, also update truth files.

### 7) State update

After a chapter is accepted, update:

- `chapter_summaries.md`
- `current_state.md`
- `pending_hooks.md`
- `character_matrix.md`
- `emotional_arcs.md`
- `subplot_board.md`

Use `scripts/update_story_state.py` to append a structured summary block:

```bash
python3 scripts/update_story_state.py \
  --project /path/to/project \
  --chapter 12 \
  --title "The Price of Silence" \
  --summary "..." \
  --state-change "Lin Jin now knows the token is fake" \
  --hook-open "Who replaced the token?" \
  --relationship "Lin Jin -> Xu An: trust decreased" \
  --emotion "Lin Jin: suspicion hardens into anger"
```

Then manually refine the truth files if the chapter caused complex changes.

## Modes to support

### Full pipeline mode

Use when the user says things like:

- write the next chapter
- continue the novel
- run the full story pipeline
- draft and audit this chapter

Sequence:

1. load context
2. plan
3. draft
4. audit
5. spot-fix
6. update state

### Audit-only mode

Use when the user already has chapter text and wants:

- continuity check
- OOC check
- pacing review
- world-rule validation
- AI-ish writing detection

Read `references/audit-dimensions.md`, produce findings grouped by severity, then propose minimal edits.

### State-maintenance mode

Use when the user says:

- remember this chapter
- update the story bible
- update hooks / character relations / arcs
- summarize what changed

Focus on truth-file accuracy, not prose generation.

### Side-story / fanfic / sequel mode

Use when the project depends on another canon. Read `references/canon-side-story.md` and establish:

- parent canon facts
- allowed divergence
- forbidden spoilers
- hook isolation

## File discipline

When working over many chapters:

- prefer additive updates over destructive rewrites
- never delete hook history without a reason
- mark hooks as `OPEN`, `PAID OFF`, `BROKEN`, or `DEFERRED`
- mark uncertain facts as `UNCONFIRMED`
- separate **world facts** from **character beliefs**

Good pattern:

```md
## Facts
- The seal broke in chapter 17.

## Character beliefs
- Lin Jin believes Xu An caused it.
- Xu An does not know the true source.
```

## Use bundled scripts where helpful:

- `scripts/init_novel_project.sh` — scaffold a new novel project with standard working directories
- `scripts/update_story_state.py` — append structured state deltas after a chapter
- `scripts/build_next_chapter_context.py` — assemble a compact truth-file context for the next chapter
- `scripts/audit_chapter.py` — run a heuristic chapter audit with Markdown or JSON output
- `scripts/smoke_test.sh` — quick regression test for the init/context/audit/update loop
- `scripts/package_skill.sh` — create a clean `.skill` package with a stable top-level directory name

## Use bundled references

Read these only when needed:

- `references/audit-dimensions.md` — audit taxonomy and severity model
- `references/file-schemas.md` — what each truth file should contain
- `references/workflow-playbooks.md` — step-by-step operating playbooks
- `references/worked-examples.md` — concrete end-to-end examples from project setup to chapter progression
- `references/canon-side-story.md` — how to handle prequels / sequels / alternate lines
- `references/style-learning.md` — how to learn and apply style without overfitting

## Output expectations

When responding in chat, prefer concise operational structure:

- **Plan**
- **Draft / Findings / Proposed fixes**
- **State updates needed**
- **Open questions**

When producing audits, use severity:

- `critical` — breaks logic / continuity / core characterization
- `major` — noticeably weakens chapter or damages setup/payoff
- `minor` — style, clarity, repetition, local pacing
- `note` — optional enhancement

## Design goal

This skill is not a magic novel writer. It is a discipline layer that makes long-form AI writing more stable, inspectable, and maintainable.
