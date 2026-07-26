# JSON Schemas

## CLI-first note / CLI 优先说明

这些 JSON 契约既可由底层脚本直接输出，也可通过 `python scripts/novelops_cli.py ... --json` 统一获取。对普通使用者，推荐优先走 CLI。

这些不是 JSON Schema draft 文件，而是当前脚本输出的稳定 JSON 契约说明。

## 1. `novelops.audit-report.v1`

来源：`scripts/audit_chapter.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`（因历史原因为章节文件路径字符串，语义保持不变）
- `chapter_file`（与 `chapter` 同值的章节文件路径，用于与 knowledge-check 的字段约定对齐）
- `overall`
- `summary`
- `source_files`
- `chapter_metrics`
- `findings[]`
- `minimal_fix_plan[]`
- `report_path`（仅 `--write-report` 时出现）

### `findings[]`
每条 finding 包含：
- `rule_id`
- `severity`
- `dimension`
- `message`
- `evidence[]`
- `repair_targets[]`

## 2. `novelops.next-context.v1`

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

## 3. `novelops.state-update.v1`

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

## 4. `novelops.knowledge-check.v1`

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

## 5. `novelops.hook-report.v1`

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

## 6. `novelops.extract-state.v1`

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

## 7. `novelops.write-next.v1`

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
- `single_chapter_contract[]`
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

## 8. `novelops.revision-cycle.v1`

来源：`scripts/run_revision_cycle.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`（章节文件路径字符串）
- `chapter_file`（与 `chapter` 同值）
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

## 9. `novelops.longdoc-reverse.v1`

来源：`scripts/reverse_long_document.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `source`
- `workspace`
- `summary`
- `outputs`

### `summary`
- `total_chapters`
- `chunk_file_count`
- `analysis_file_count`

### `outputs`
- `index`
- `chunks_dir`
- `chunk_analysis_dir`
- `summary_json`
- `summary_md`

## 10. `novelops.revision-plan.v1`

来源：`scripts/build_revision_plan.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`（沿用 audit 报告中的章节文件路径）
- `chapter_file`（优先取 audit 报告的 `chapter_file`，缺失时回退 `chapter`）
- `based_on`
- `overall_strategy`
- `summary`
- `source_files[]`
- `minimal_fix_plan[]`
- `actions[]`
- `report_path`（仅 `--write-report` 时出现）

### `based_on`
- `schema_version`
- `overall`

### `overall_strategy`
- `mode`（`block-and-patch` / `targeted-scene-rewrite` / `targeted-rewrite` / `spot-fix-pass` / `light-pass-or-accept`）
- `reason`

### `summary`
- `action_count`
- `human_review_needed`
- `counts`

### `actions[]`
每条 action 包含：
- `action_id`（`REV-001` 起）
- `priority`
- `rule_id`
- `dimension`
- `target_scope`
- `needs_human_review`
- `goal`
- `recommended_strategy`
- `repair_targets[]`
- `evidence[]`

## 11. `novelops.spot-fix-suggestions.v1`

来源：`scripts/suggest_spot_fixes.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`（沿用 audit 报告中的章节文件路径）
- `chapter_file`（优先取 audit 报告的 `chapter_file`，缺失时回退 `chapter`）
- `based_on`
- `summary`
- `suggestions[]`
- `report_path`（仅 `--write-report` 时出现）

### `summary`
- `suggestion_count`
- `local_dimensions[]`

### `suggestions[]`
每条 suggestion 包含：
- `suggestion_id`（`FIX-001` 起）
- `rule_id`
- `severity`
- `dimension`
- `snippet`
- `suggested_action`
- `repair_targets[]`
- `confidence`

## 12. `novelops.state-snapshot.v1`

来源：`scripts/snapshot_story_state.py --json`

快照写入 `<project>/.novelops-state/snapshots/<snapshot_id>/`，并在 `<project>/.novelops-state/index.jsonl` 追加一行索引。

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `snapshot_id`
- `snapshot_dir`
- `label`
- `chapter`
- `notes`
- `files_copied[]`
- `files_missing[]`

### `files_copied[]`
每条包含：
- `path`
- `bytes`
- `sha1`

## 13. `novelops.state-diff.v1`

来源：`scripts/diff_story_state.py --json`

`latest` 与裸快照 ID 的解析会优先查 `.novelops-state/snapshots/`，查不到时回退兼容旧的 `.inkos-state/snapshots/`。

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `from`
- `to`
- `summary`
- `file_diffs[]`

### `from` / `to`
- `kind`（`current` / `snapshot`）
- `id`
- `path`

### `summary`
- `changed_files`
- `added_lines`
- `removed_lines`

### `file_diffs[]`
每条包含：
- `path`
- `status`（`added` / `removed` / `changed`）
- `added_lines`
- `removed_lines`
- `diff_excerpt[]`（unified diff 片段，最多 80 行）

## 稳定性原则

- 先新增字段，再考虑移除字段
- `schema_version` 升级时，尽量保留旧字段语义
- CLI 与后续自动修订脚本应优先依赖这些 JSON 输出，而不是解析 Markdown 文本

