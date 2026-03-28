# Changelog

## v0.4.1 — 2026-03-28

### Added

- 新增最小 `docs/` 上手文档结构：`getting-started`、`installation`、`user-paths`、`project-template`、`faq`
- 新增 `examples/demo-novel/` 示例项目，包含 truth files 与两章演示内容，方便快速理解 `context / audit / extract-state / state-update` 的协作方式
- README 顶部新增 CI / License / Version 徽章，并补充 docs / example 导航入口
- 新增开源协作基础文件：`LICENSE`、`CONTRIBUTING.md`、`CODE_OF_CONDUCT.md`、`SECURITY.md`
- 新增 GitHub 协作模板与最小 CI 工作流

### Fixed

- 修复 `scripts/smoke_test.sh` 在 Windows / Git Bash 风格环境中的 Python 入口兼容问题
- 修复 smoke test 对中文 JSON 输出的脆弱匹配方式，改为更稳的 UTF-8 / Python 断言路径

### Notes

- 这是一个小版本维护发布，重点是提升开源协作体验、首次上手路径和环境兼容性
- 当前 `snapshot_story_state.py` 仍存在 `datetime.utcnow()` 的 deprecation warning，但不影响使用与本次发布

这个文件记录 GitHub 上已发布版本的主要变化。

## v0.4.0 — 2026-03-18

### Added

- 新增 `knowledge_check.py`，用于检测人物认知边界、POV 泄露、以及“角色提前知道真相”类问题
- 新增 `hook_report.py`，用于统计 hook 生命周期状态并标记 stale hooks
- 新增 `extract_state.py`，用于从章节正文中提取候选状态更新，默认只输出候选、不直接写盘
- `inkos_cli.py` 新增 `knowledge-check`、`hook-report`、`extract-state` 子命令
- 模板新增 `character_knowledge.md`，并补强 `pending_hooks.md` / `chapter_summaries.md` 结构

### Changed

- `build_next_chapter_context.py` 现在支持自动加载 `character_knowledge.md`
- `SKILL.md` 工作流升级为“knowledge-check → audit → extract-state → state-update”闭环
- `references/file-schemas.md`、`references/json-schemas.md`、`references/workflow-playbooks.md` 同步扩展新能力说明
- `smoke_test.sh` 新增对 knowledge-check / hook-report / extract-state 的回归覆盖

### Assets

- `inkos-like-novel-os-v0.4.0.skill`

## v0.3.4 — 2026-03-17

### Fixed

- 修复 `init_novel_project.sh` 在书名包含 `&`、`/`、反斜杠等字符时的占位符替换问题
- 修复 `build_next_chapter_context.py` 的边界行为：
  - 极小 `--max-chars-per-file` 下截断结果可能超长
  - `--recent-chapters 0` 之前会错误返回全部章节
  - 负数参数现在会明确报错
  - 中英文章节标题提取更一致
- 修复 `update_story_state.py` 的 `updated_files`，现在只返回实际写入的文件
- 修复 `audit_chapter.py` 在 chapter 文件缺失时的误导性“空章节”结果
- 修复 `build_next_chapter_context.py`、`update_story_state.py`、`snapshot_story_state.py`、`diff_story_state.py` 在 project 路径不存在或未初始化时的误导性成功返回

### Quality

- `inkos_cli.py` 同步增加 context 参数校验，避免 CLI 与底层脚本行为不一致
- `package_skill.sh` 支持从 `VERSION` 自动生成带版本号的 `.skill` 副本
- 补充 smoke test 回归覆盖：特殊书名转义、极小 `max-chars`、`recent-chapters=0`、负数参数、缺失 project / chapter、snapshot/diff 回归

### Assets

- `inkos-like-novel-os-v0.3.4.skill`

## Earlier GitHub releases

- [v0.3.1](https://github.com/qiyan233/inkos-like-novel-os/releases/tag/v0.3.1)
- [v0.3.0](https://github.com/qiyan233/inkos-like-novel-os/releases/tag/v0.3.0)
- [v0.2.0](https://github.com/qiyan233/inkos-like-novel-os/releases/tag/v0.2.0)
- [v0.1.3](https://github.com/qiyan233/inkos-like-novel-os/releases/tag/v0.1.3)
- [v0.1.2](https://github.com/qiyan233/inkos-like-novel-os/releases/tag/v0.1.2)
- [v0.1.1](https://github.com/qiyan233/inkos-like-novel-os/releases/tag/v0.1.1)
- [v0.1.0](https://github.com/qiyan233/inkos-like-novel-os/releases/tag/v0.1.0)
