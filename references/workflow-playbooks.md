# Workflow Playbooks

## Playbook 1: Write next chapter

1. Read `story_bible.md`, `book_rules.md`, `outline.md`, `current_state.md`
2. Read the latest 3-5 chapter summaries
3. Review `pending_hooks.md`, `character_matrix.md`, `subplot_board.md`
4. State the chapter function in 1-3 bullets
5. Draft the chapter
6. Run `knowledge-check` if the chapter depends on hidden truths or limited POV
7. Audit using core dimensions
8. Spot-fix the highest-severity issues
9. Run `extract-state` to prepare candidate truth-file updates
10. Update truth files
11. Report: what changed, what remains open, what needs human review

## Playbook 2: Audit existing chapter

1. Read chapter text
2. Read only the minimum supporting truth files
3. Run audit dimensions by severity
4. Distinguish hard breakage from stylistic preference
5. Propose minimal patch plan before suggesting rewrite

## Playbook 3: Build from existing novel / canon

1. Read source material or curated canon notes
2. Separate objective canon from interpretation
3. Create `story_bible.md` and `current_state.md`
4. Record timeline anchors and hard constraints
5. If writing derivative work, define divergence point and spoiler boundary

## Playbook 4: Human-in-the-loop revision

Use when the user wants control over risky changes.

1. List critical/major issues
2. Show 2-3 repair options
3. Explain downstream truth-file updates needed
4. Wait for direction before changing high-impact events

## Playbook 5: Style-learning mode

1. Read sample text
2. Extract qualitative style cues into `style_guide.md`
3. Optionally record quantitative stats in `style_profile.json`
4. Apply style as a soft constraint, not a prison
5. During audit, flag mimicry that damages clarity or continuity

## Playbook 6: Draft-to-state extraction

1. Finish draft and save chapter file
2. Run `knowledge-check` for POV / spoiler leakage
3. Run `audit` and patch critical / major findings first
4. Run `extract-state --json`
5. Review summary / hooks / relationship / emotion candidates
6. Feed approved items into `update_story_state.py`
7. If many hooks remain open, run `hook-report` to review backlog pressure
