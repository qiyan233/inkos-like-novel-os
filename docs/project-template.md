# 项目模板说明

`assets/project-template/` 提供的是一个最小可用的长篇小说项目骨架，不是豪华模板，也不是固定写法。

## 初始化

```bash
bash scripts/init_novel_project.sh /path/to/project "书名"
```

初始化后你会得到：

- `story_bible.md`
- `book_rules.md`
- `outline.md`
- `current_state.md`
- `chapter_summaries.md`
- `pending_hooks.md`
- `character_matrix.md`
- `character_knowledge.md`
- `emotional_arcs.md`
- `subplot_board.md`
- `continuity_issues.md`
- `style_guide.md`
- `style_profile.json`
- `chapters/`
- `reviews/`

## 最重要的几个文件

### `current_state.md`

这是下一章写作前最该读的文件。

建议只保留“此刻真正有效的信息”：

- 时间位置
- 关键人物状态
- 关系变化
- 当前冲突
- 角色认知边界
- 下一章压力点

### `chapter_summaries.md`

记录每章发生了什么，不是复制正文。

重点写：

- 章节功能
- 状态变化
- 新增事实
- hook 是打开、推进还是回收

### `pending_hooks.md`

不要只写“有伏笔”。要写清：

- 伏笔是什么
- 当前状态是 open / advanced / paid off / deferred
- 最后更新时间或首次出现章节

### `character_knowledge.md`

如果你的故事有悬疑、信息差、严格 POV，这个文件非常有用。

它能帮助：

- `knowledge_check.py` 判断是否提前泄露
- 起草下一章时避免角色突然知道不该知道的事

## 推荐最小维护节奏

每接受一章，至少做三件事：

1. 更新 `chapter_summaries.md`
2. 更新 `pending_hooks.md`
3. 更新 `current_state.md`

如果这一章显著改变了关系或情绪，再补：

- `character_matrix.md`
- `emotional_arcs.md`

## 结合 demo 看更直观

如果你觉得模板说明太抽象，直接看：

- [快速上手](getting-started.md)
- [用户路径](user-paths.md)
- [demo-novel 示例](../examples/demo-novel/README.md)
