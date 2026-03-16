# JSON Schemas

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

## 稳定性原则

- 先新增字段，再考虑移除字段
- `schema_version` 升级时，尽量保留旧字段语义
- CLI 与后续自动修订脚本应优先依赖这些 JSON 输出，而不是解析 Markdown 文本


## 4. `inkos.revision-plan.v1`

来源：`scripts/build_revision_plan.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`
- `based_on`
- `overall_strategy`
- `summary`
- `minimal_fix_plan[]`
- `actions[]`

### `actions[]`
每条 action 包含：
- `action_id`
- `priority`
- `rule_id`
- `dimension`
- `target_scope`
- `needs_human_review`
- `goal`
- `recommended_strategy`
- `repair_targets[]`

## 5. `inkos.spot-fix-suggestions.v1`

来源：`scripts/suggest_spot_fixes.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `chapter`
- `based_on`
- `summary`
- `suggestions[]`

### `suggestions[]`
每条 suggestion 包含：
- `suggestion_id`
- `rule_id`
- `severity`
- `dimension`
- `snippet`
- `suggested_action`
- `repair_targets[]`
- `confidence`

## 6. `inkos.state-snapshot.v1`

来源：`scripts/snapshot_story_state.py --json`

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

## 7. `inkos.state-diff.v1`

来源：`scripts/diff_story_state.py --json`

核心字段：
- `schema_version`
- `tool`
- `generated_at`
- `project`
- `from`
- `to`
- `summary`
- `file_diffs[]`

### `file_diffs[]`
每条 diff 包含：
- `path`
- `status`
- `added_lines`
- `removed_lines`
- `diff_excerpt[]`
