# Audit Dimensions

Use this file to review drafted fiction systematically. Not every project needs every dimension; choose a subset when speed matters.

## Severity model

- **critical** — breaks core logic, continuity, setting, or protagonist lock
- **major** — harms readability, payoff, pacing, or trust in the story
- **minor** — local weakness, repetition, awkwardness
- **note** — optional improvement or observation

## Core dimensions

### 1. Character consistency (OOC)
Check whether named characters behave, speak, and decide in ways consistent with their established traits, capabilities, fear, pride, intelligence, and recent emotional state.

Questions:
- Did a character become passive/merciful/cowardly without setup?
- Did dialogue suddenly shift register?
- Did the protagonist forget their long-running behavioral lock?

### 2. Timeline continuity
Check whether the order, duration, travel time, cooldowns, injuries, and recovery windows make sense.

Questions:
- Did events happen too fast?
- Did time of day change accidentally?
- Did prior chapter constraints get ignored?

### 3. World-rule consistency
Check magic system, technology, politics, geography, institutions, ranks, economics, taboo rules, and cause/effect.

Questions:
- Did the chapter violate a hard world rule?
- Did a location or institution suddenly behave differently without explanation?

### 4. Information boundary leaks
Check what each character is allowed to know.

Questions:
- Did a character refer to information learned only by others?
- Did narration implicitly spoil beyond POV knowledge?
- Did a side story leak future-canon information?

### 5. Resource / inventory / injury tracking
Check money, items, weapons, clues, injuries, stamina, cultivation resources, social capital, and obligations.

Questions:
- Did a lost item reappear?
- Did a serious injury vanish?
- Did power output ignore established cost?

### 6. Hook management
Check promises made to the reader.

Questions:
- Was a hook accidentally dropped?
- Was a payoff rushed or unearned?
- Were too many hooks opened without progress?

### 7. Plot logic
Check motives, decisions, scene causality, and consequence flow.

Questions:
- Are actions causally connected?
- Is anyone holding the idiot ball?
- Did conflict resolve through convenience rather than setup?

### 8. Pacing and chapter function
Check whether the chapter has a clear job and enough movement.

Questions:
- Does the chapter advance plot, relationship, mystery, or emotional arc?
- Is it stalling?
- Does it over-explain instead of dramatize?

### 9. Emotional arc consistency
Check emotional carryover from recent chapters.

Questions:
- Did fear/anger/grief vanish between scenes?
- Did emotional escalation or release feel earned?

### 10. Dialogue authenticity
Check whether characters sound distinct and context-appropriate.

Questions:
- Is the dialogue too expositional?
- Do different characters sound identical?
- Are lines too neat or too AI-clean?

## Style and anti-formula dimensions

### 11. Repetition / fatigue words
Check repeated phrases, metaphors, sentence patterns, and emotional labels.

### 12. Report-speak / abstract explanation
Flag prose that sounds like analysis, summary, motivational speaking, or writing advice instead of lived narrative.

### 13. Over-generic crowd response
Flag clichés like whole-room shock, universal silence, everyone gasping, etc., unless specifically earned.

### 14. Telling instead of dramatizing
Flag lines that summarize where one concrete action would work better.

### 15. Paragraph monotony
Check equal-length paragraphs, repeated transition patterns, and list-like rhythm.

### 16. AI-ish transition density
Check overuse of words like suddenly, instantly, as if, at that moment, could not help but, unexpectedly.

## Structure dimensions

### 17. Outline drift
Check whether the chapter still serves the intended arc.

### 18. Subplot stagnation
Check whether side threads are frozen for too long.

### 19. Promise/payoff mismatch
Check whether reader expectation is managed well.

### 20. Scene entry / exit discipline
Check whether scenes start too early, end too late, or drift without beat change.

## Canon / derivative-work dimensions

### 21. Parent-canon conflict
For prequels, sequels, side stories, or fanfiction, check whether this chapter contradicts parent canon.

### 22. Future-info leakage
Check whether characters know revelations that should only appear later in the canon timeline.

### 23. Hook isolation
Check whether derivative work improperly resolves hooks that belong to the parent work.

## Suggested audit output format

```md
# Chapter Audit

## Summary verdict
- overall: pass / revise / block
- main risks: ...

## Findings
### critical
- [dimension] Description

### major
- [dimension] Description

### minor
- [dimension] Description

### note
- [dimension] Description

## Minimal fix plan
- Fix X in paragraph 3
- Remove leaked knowledge in dialogue 2
- Update current_state after acceptance
```
