# JSON Schemas

## CLI-first note / CLI 优先说明

这些 JSON 契约既可由底层脚本直接输出，也可通过 `python3 scripts/inkos_cli.py ... --json` 统一获取。对普通使用者，推荐优先走 CLI。

这些不是 JSON Schema draft 文件，而是当前脚本输出的稳定 JSON 契约说明。

## 1. `inkos.audit-report.v1`

来源：`scripts/audit_chapter.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`
- `overall`
- `summary`
- `source_files`
- `chapter_metrics`
- `findings[]`
- `minimal_fix_plan[]`

### `findings[]`
每条 finding 包含：
- `rule_id`
- `severity`
- `dimension`
- `message`
- `evidence[]`
- `repair_targets[]`

## 2. `inkos.next-context.v1`

来源：`scripts/build_next_chapter_context.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `config`
- `files_loaded[]`
- `summary`
- `section_meta`
- `sections`
- `context`

## 3. `inkos.state-update.v1`

来源：`scripts/update_story_state.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`
- `title`
- `summary`
- `operations`
- `updated_files[]`
- `report_path`（仅 `--write-report` 时出现）

## 4. `inkos.knowledge-check.v1`

来源：`scripts/knowledge_check.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`
- `chapter_file`
- `ok`
- `summary`
- `source_files[]`
- `violations[]`

### `violations[]`
每条 violation 包含：
- `severity`
- `type`
- `character`
- `fact`
- `evidence`
- `reason`
- `suggested_fix`

## 5. `inkos.hook-report.v1`

来源：`scripts/hook_report.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `config`
- `summary`
- `hooks[]`
- `stale_hooks[]`

## 6. `inkos.extract-state.v1`

来源：`scripts/extract_state.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`
- `chapter_file`
- `title_guess`
- `summary`
- `state_changes[]`
- `hook_open[]`
- `hook_advance[]`
- `hook_close[]`
- `relationships[]`
- `emotions[]`
- `write_mode`

## 7. `inkos.write-next.v1`

来源：`scripts/build_write_next_packet.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`
- `chapter_file_hint`
- `files_loaded[]`
- `chapter_function`
- `required_inputs`
- `suggested_scene_beats[]`
- `plan_template`
- `context_packet`
- `next_actions[]`
- `report_path`（仅 `--write-report` 时出现）

### `chapter_function`
- `primary_goal`
- `pressure[]`
- `planned_payoff_or_partial_payoff`

### `required_inputs`
- `suggested_pov`
- `active_hooks[]`
- `open_conflicts[]`
- `constraints[]`
- `state_targets[]`

## 8. `inkos.revision-cycle.v1`

来源：`scripts/run_revision_cycle.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`
- `status`
- `summary`
- `recommended_sequence[]`
- `hook_pressure`
- `knowledge_check`
- `audit`
- `revision_plan`
- `spot_fixes`
- `report_path`（仅 `--write-report` 时出现）

### `summary`
- `knowledge_check_run`
- `blocking_item_count`
- `audit_overall`
- `spot_fix_count`
- `human_review_needed`
- `stale_hook_count`

## 稳定性原则

- 先新增字段，再考虑移除字段
- `schema_version` 升级时，尽量保留旧字段语义
- CLI 与后续自动修订脚本应优先依赖这些 JSON 输出，而不是解析 Markdown 文本
