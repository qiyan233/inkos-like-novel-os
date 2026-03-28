# demo-novel

这是一个**最小但完整**的示例项目，用来展示这个仓库的核心闭环：

`context -> draft -> audit -> extract-state -> state-update`

> 推荐入口 / Recommended entrypoint：`python3 scripts/inkos_cli.py ...`

故事设定是一个两章规模的古风悬疑开局：主角林烬发现徐家旧玉佩疑似被调包，但还不能直接确认幕后人。

## 你可以先读什么

建议顺序：

1. `current_state.md`
2. `chapter_summaries.md`
3. `pending_hooks.md`
4. `chapters/ch01.md`
5. `chapters/ch02.md`

这样能最快看懂：truth files 如何约束正文，正文又如何反过来更新 truth files。

## 这个 demo 重点演示什么 / What this demo shows

### 1. context

生成下一章上下文：

```bash
python3 scripts/inkos_cli.py context --project examples/demo-novel
```

脚本会读取如下一批 truth files：

- `story_bible.md`
- `book_rules.md`
- `outline.md`
- `current_state.md`
- `chapter_summaries.md`
- `pending_hooks.md`
- `character_matrix.md`
- `character_knowledge.md`

你会看到：下一章不是凭空写，而是基于“当前状态 + 已开伏笔 + 人物认知边界”来写。

### 2. audit

对现有章节跑审计：

```bash
python3 scripts/inkos_cli.py audit --project examples/demo-novel --chapter-file examples/demo-novel/chapters/ch02.md --json
```

这个结果不等于文学评价，而是帮助你检查：

- 连续性是否稳定
- 是否有知识边界泄露
- 是否把悬念过早讲破

### 3. extract-state

从章节正文中提取候选状态更新：

```bash
python3 scripts/inkos_cli.py extract-state --project examples/demo-novel --chapter-file examples/demo-novel/chapters/ch02.md --json
```

这里的输出是**候选项**，例如：

- 可作为摘要的句子
- 角色新认知
- hook 的打开 / 推进
- 关系与情绪变化

### 4. state-update

确认候选项后，再写回 truth files：

```bash
python3 scripts/inkos_cli.py state-update \
  --project examples/demo-novel \
  --chapter 2 \
  --title "第二章 雨夜试探" \
  --summary "林烬借试探确认徐安隐瞒了玉佩转手顺序，但仍不能确定幕后人。" \
  --state-change "林烬确认徐安知道更多内情。" \
  --hook-advance "徐安为什么隐瞒玉佩最早经手人的名字" \
  --relationship "林烬 -> 徐安：表面合作维持，但实质信任继续下降" \
  --emotion "林烬：怀疑转为克制的逼问" \
  --json
```

执行后会更新：

- `chapter_summaries.md`
- `pending_hooks.md`
- `character_matrix.md`
- `emotional_arcs.md`

### 5. 底层脚本 / Advanced usage

如果你在调试某个单独能力，也仍然可以直接运行：

- `python3 scripts/build_next_chapter_context.py --project examples/demo-novel`
- `python3 scripts/audit_chapter.py --project examples/demo-novel --chapter-file examples/demo-novel/chapters/ch02.md --json`
- `python3 scripts/extract_state.py --project examples/demo-novel --chapter-file examples/demo-novel/chapters/ch02.md --json`
- `python3 scripts/update_story_state.py ...`

## 为什么这里只放两章

因为这个 demo 的目标不是展示“长”，而是展示“工作流怎么落地”。

两章已经足够说明：

- 第 1 章如何建立异常与悬念
- 第 2 章如何推进怀疑，但不直接揭示真相
- truth files 如何成为下一章的稳定输入

如果你要从零做自己的书，建议再看：

- [docs/getting-started.md](../../docs/getting-started.md)
- [docs/cli.md](../../docs/cli.md)
- [docs/project-template.md](../../docs/project-template.md)
- [docs/user-paths.md](../../docs/user-paths.md)
