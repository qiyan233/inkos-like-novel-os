# inkos-like-novel-os

中文 | [English](#english)

一个面向 **OpenClaw** 的小说生产技能骨架，把长篇 / 连载 / 网文 / 同人写作当成**有状态的工作流系统**来运行，而不是一次性提示词。

这个项目的目标不是直接“替你写神作”，而是提供一个接近 **InkOS** 思路的基础设施：

- 让小说写作变成可持续维护的流程
- 用 truth files 管理世界观、人物状态、伏笔、情绪弧线
- 支持“起草 → 审计 → 局部修订 → 更新状态”的闭环
- 支持番外、前传、后传、if 线等依赖正典约束的写作场景

## 适用场景

适合这些需求：

- 想做一个类似 InkOS 的小说写作 skill
- 想让 AI 连续写多章时尽量少崩设定
- 想维护角色关系、伏笔板、章节摘要、当前状态
- 想给长篇小说建立“世界状态 + 审计 + 修订”的基础框架
- 想做 side story / fanfic / sequel / prequel 的约束式写作

## 当前包含

### 1. `SKILL.md`
核心技能说明，定义小说生产操作系统的工作方式：

- 写前读取哪些状态文件
- 写作时如何受规则约束
- 写后如何做审计与修订
- 何时更新 truth files
- 如何处理番外 / 前传 / 平行线

### 2. `references/`
参考文档：

- `audit-dimensions.md` — 审计维度
- `file-schemas.md` — 各类状态文件结构
- `workflow-playbooks.md` — 常见工作流剧本
- `canon-side-story.md` — 正典 / 衍生线处理原则
- `style-learning.md` — 文风学习方法

### 3. `scripts/`
辅助脚本：

- `init_novel_project.sh` — 初始化一个小说项目骨架
- `update_story_state.py` — 追加章节摘要、伏笔、关系、情绪变化等状态更新

### 4. `assets/project-template/`
小说项目模板，包含：

- `story_bible.md`
- `book_rules.md`
- `outline.md`
- `current_state.md`
- `chapter_summaries.md`
- `pending_hooks.md`
- `character_matrix.md`
- `emotional_arcs.md`
- `subplot_board.md`
- `continuity_issues.md`
- `style_guide.md`
- `style_profile.json`

## 工作流思路

推荐按下面的方式运行：

1. 读取 truth files
2. 规划下一章目标
3. 按约束起草章节
4. 审计连续性 / OOC / 信息边界 / 节奏 / 文风问题
5. 优先做 spot-fix，而不是整章推倒重写
6. 接受后更新状态文件

核心理念：

> 长篇小说最怕的不是“写不出来”，而是“写着写着全乱了”。

所以这个 skill 的重点不是单次生成质量，而是：

- 连续可维护
- 状态可追踪
- 规则可检查
- 修订有依据

## 快速开始

### 初始化项目

```bash
bash scripts/init_novel_project.sh /path/to/project "书名"
```

### 追加章节状态

```bash
python3 scripts/update_story_state.py \
  --project /path/to/project \
  --chapter 12 \
  --title "沉默的代价" \
  --summary "主角第一次确认玉佩被人调包" \
  --state-change "林烬确认玉佩是伪造的" \
  --hook-open "是谁替换了玉佩" \
  --relationship "林烬 -> 徐安：信任下降" \
  --emotion "林烬：怀疑上升"
```

## 当前定位

当前版本是：

> **接近 InkOS 的 skill 骨架 / 基础设施层**

已经包含：

- 项目结构
- 状态文件设计
- 审计参考
- 工作流说明
- 初始化 / 更新脚本

还没包含：

- 完整 CLI（如 `write next / audit / revise`）
- 自动章节审计脚本
- 自动上下文拼装器
- 守护进程 / 通知 / 多 agent 调度

## 发布说明

仓库已提供 `.skill` 发布包，可用于分发和安装。

---

## English

An OpenClaw skill skeleton for running long-form fiction as a stateful pipeline.

## Included

- `SKILL.md` with workflow and operating model
- `references/` for audit dimensions, file schemas, canon handling, playbooks, and style learning
- `scripts/` for project initialization and structured story-state updates
- `assets/project-template/` for bootstrapping a new novel project

## Goal

Provide an InkOS-like foundation for:

- serial fiction workflows
- world-state persistence
- continuity audits
- chapter revision loops
- side-story / canon-aware writing
