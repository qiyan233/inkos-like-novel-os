# File Schemas

Use these schemas as templates, not rigid law. Keep files easy to skim.

## story_bible.md
Contains durable world information.

Suggested sections:
- premise
- themes
- world rules
- factions
- locations
- power / tech system
- historical events
- taboo constraints

## book_rules.md
Contains book-specific instructions.

Suggested sections:
- protagonist lock
- behavioral constraints
- prohibitions
- tone goals
- pacing rules
- genre-specific taboos
- naming constraints
- spoiler / canon boundaries

## outline.md
Contains macro plan.

Suggested sections:
- act structure
- target chapter ranges
- major reversals
- key payoffs
- unresolved mysteries

## current_state.md
Contains the latest authoritative state.

Suggested sections:
- current timeline position
- active POV set
- major character status
- relationships
- open conflicts
- active resources / items
- known truths vs false beliefs
- immediate next pressure

## chapter_summaries.md
Store one section per chapter:

```md
## Chapter 12 - The Price of Silence
- POV:
- Summary:
- Key events:
- State changes:
- Hooks opened:
- Hooks advanced:
- Hooks closed:
- New facts:
- Character knowledge changes:
```

## pending_hooks.md
Track reader promises.

Recommended statuses:
- OPEN
- ADVANCED
- PAID OFF
- DEFERRED
- BROKEN

Suggested record format:

```md
- [OPEN] Who replaced the token? (opened: ch12, owner: mystery line A)
- [ADVANCED] Lin Jin now suspects an inside actor. (updated: ch15, owner: mystery line A)
- [PAID OFF] Han Lan replaced the token. (closed: ch20, owner: mystery line A)
```

## character_matrix.md
Track encounters, trust, conflict, secrets, and asymmetry.

Suggested row format:

```md
- Lin Jin <-> Xu An
  - relationship: allies under strain
  - latest change: trust decreased after token incident
  - secrets: Xu An hides contact with the magistrate
  - info asymmetry: Lin Jin does not know the contact exists
```

## character_knowledge.md
Optional but recommended when the story depends heavily on hidden truths, mysteries, or spoiler boundaries.

Suggested format:

```md
## Lin Jin
- knows:
- suspects:
- does not know:
- wrong beliefs:
```

## emotional_arcs.md
Track durable emotional movement, not every mood swing.

Suggested format:

```md
## Lin Jin
- baseline: controlled, suspicious
- current phase: anger hardening into restraint
- trigger events:
- likely next break point:
```

## subplot_board.md
Track line progress.

Suggested format:

```md
- Line A: family revenge
  - status: advancing
  - last progress: ch12
  - risk: overshadowing political line
```

## continuity_issues.md
Use for known problems not yet repaired.

Suggested fields:
- issue
- first seen
- severity
- affected files
- repair plan
- status
