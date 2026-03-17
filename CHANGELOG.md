# Changelog

这个文件记录 GitHub 上已发布版本的主要变化。

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
