# inkos-like-novel-os

> 面向 OpenClaw 的长篇小说工作流技能骨架。

中文 | [English](#english)

一个面向 **OpenClaw** 的小说生产技能骨架，把长篇 / 连载 / 网文 / 同人写作当成 **有状态的工作流系统** 来运行，而不是一次性提示词。

这个项目的目标不是直接“替你写神作”，而是提供一个接近 **InkOS** 思路的基础设施：

- 让小说写作变成可持续维护的流程
- 用 truth files 管理世界观、人物状态、伏笔、情绪弧线
- 支持“起草 → 审计 → 局部修订 → 更新状态”的闭环
- 支持番外、前传、后传、if 线等依赖正典约束的写作场景

灵感参考原项目 **InkOS**：<https://github.com/Narcooo/inkos>

> 说明：本项目是面向 OpenClaw 的 skill skeleton，受 InkOS 启发，但不是原项目的官方移植版本。

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

- `init_novel_project.sh` — 初始化一个小说项目骨架，并创建标准工作目录
- `update_story_state.py` — 追加章节摘要、伏笔、关系、情绪变化等状态更新
- `audit_chapter.py` — 对章节做启发式审计，输出 Markdown 或 JSON 报告
- `build_next_chapter_context.py` — 从 truth files 自动拼装“下一章写作上下文”
- `smoke_test.sh` — 快速回归测试整个 init → context → audit → update 链路
- `package_skill.sh` — 稳定打包 `.skill` 文件，确保顶层目录始终为 `inkos-like-novel-os/`

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

## 安装与使用

### 方式一：安装 `.skill` 发布包

从 Releases 下载 `.skill` 文件，用你的 OpenClaw / skill 安装流程导入。

### 方式二：直接使用仓库目录

克隆仓库后，直接使用其中的：

- `SKILL.md`
- `references/`
- `scripts/`
- `assets/project-template/`

## 快速开始

### 初始化一个小说项目

```bash
bash scripts/init_novel_project.sh /path/to/project "书名"
```

初始化后会自动准备：

- truth files 模板
- `chapters/`
- `reviews/`

### 生成下一章上下文

```bash
python3 scripts/build_next_chapter_context.py \
  --project /path/to/project
```

### 审计章节

```bash
python3 scripts/audit_chapter.py \
  --project /path/to/project \
  --chapter-file /path/to/project/chapters/ch12.md
```

输出 JSON：

```bash
python3 scripts/audit_chapter.py \
  --project /path/to/project \
  --chapter-file /path/to/project/chapters/ch12.md \
  --json
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

## 最小工作流示例

假设用户说：

> 帮我继续写第 12 章，重点是主角开始怀疑徐安，但不要直接撕破脸。

推荐流程：

1. 先生成上下文

```bash
python3 scripts/build_next_chapter_context.py --project /path/to/project
```

2. 用生成的上下文去起草章节
3. 起草完成后跑审计

```bash
python3 scripts/audit_chapter.py \
  --project /path/to/project \
  --chapter-file /path/to/project/chapters/ch12.md
```

4. 根据审计结果做 spot-fix
5. 接受后更新状态

```bash
python3 scripts/update_story_state.py ...
```

## 验证与打包

### 跑 smoke test

```bash
bash scripts/smoke_test.sh
```

它会自动验证：

- 项目初始化
- 下一章上下文构建
- 章节审计
- 状态更新

### 打包 `.skill`

```bash
bash scripts/package_skill.sh
```

输出会写到默认 `dist/` 目录。

如果要显式指定输出目录和版本后缀：

```bash
bash scripts/package_skill.sh /path/to/dist v0.1.3
```

## 从 0 到第 3 章：一个最小 walkthrough

假设你想跑一个古风悬疑长篇，核心是“玉佩被调包”。

### Step 1：初始化项目

```bash
bash scripts/init_novel_project.sh /path/to/project "玉佩疑云"
```

初始化后先不要急着写正文，先补最关键的 truth files：

- `story_bible.md`：世界、势力、玉佩相关规则
- `book_rules.md`：主角锁、禁忌、悬疑释放规则
- `outline.md`：前 3 章要推进什么
- `current_state.md`：谁知道什么、谁怀疑谁

### Step 2：准备第 1 章

先明确 chapter function，例如：

- 主角第一次察觉玉佩不对
- 徐安在场但态度暧昧
- 留下“谁先碰过玉佩”的悬念
- 不能直接揭示幕后人

然后生成下一章上下文：

```bash
python3 scripts/build_next_chapter_context.py --project /path/to/project
```

### Step 3：写完第 1 章后审计

```bash
python3 scripts/audit_chapter.py \
  --project /path/to/project \
  --chapter-file /path/to/project/chapters/ch01.md
```

重点看：

- 主角有没有 OOC
- 是否提前泄露真相
- 是否有太重的解释腔 / 报告感
- 钩子有没有被意外说破

### Step 4：接受后更新状态

```bash
python3 scripts/update_story_state.py \
  --project /path/to/project \
  --chapter 1 \
  --title "第一章" \
  --summary "林烬察觉玉佩手感异常。" \
  --state-change "林烬确认玉佩并非记忆中的原物。" \
  --hook-open "是谁在林烬之前碰过玉佩" \
  --relationship "林烬 -> 徐安：试探增加，信任下降" \
  --emotion "林烬：警觉上升"
```

### Step 5：推进到第 2～3 章

推荐节奏：

- **第 1 章**：察觉异常，建立悬念
- **第 2 章**：试探徐安，怀疑开始发酵
- **第 3 章**：怀疑方向第一次偏转，悬念加深

原则是：

- 每章都推进至少一个 hook
- 每章都要产生明确 state change
- 真相不要直线揭露，而是逐步校正怀疑对象

更完整的落地范例，可读：`references/worked-examples.md`。

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

## 当前定位

当前版本是：

> **接近 InkOS 的 skill 骨架 / 基础设施层**

已经包含：

- 项目结构
- 状态文件设计
- 审计参考
- 工作流说明
- 初始化 / 更新脚本
- 上下文组装脚本
- 启发式章节审计脚本
- smoke test
- 稳定打包脚本

还没包含：

- 完整 CLI（如 `write next / audit / revise`）
- 真正的 LLM 写作执行器
- 守护进程 / 通知 / 多 agent 调度
- 更强的规则引擎和自动修订系统

## Roadmap

- [x] 基础 skill 骨架
- [x] 项目模板
- [x] 状态更新脚本
- [x] 下一章上下文组装器
- [x] 启发式章节审计脚本
- [x] `.skill` 发布包
- [x] smoke test
- [x] 稳定打包脚本
- [ ] 更强的规则审计
- [ ] 更稳定的 JSON schema 输出
- [ ] 轻量 CLI 封装
- [ ] 自动修订辅助脚本
- [ ] 版本化项目状态管理

## 发布说明

仓库已提供 `.skill` 发布包，可用于分发和安装。

---

## English

An OpenClaw skill skeleton for running long-form fiction as a stateful pipeline.

Inspired by the original InkOS project: <https://github.com/Narcooo/inkos>.
This repository is an OpenClaw-oriented skill skeleton, not an official port of the original project.

## Included

- `SKILL.md` with workflow and operating model
- `references/` for audit dimensions, file schemas, canon handling, playbooks, and style learning
- `scripts/` for project initialization, story-state updates, chapter auditing, next-context building, smoke testing, and packaging
- `assets/project-template/` for bootstrapping a new novel project

## Goal

Provide an InkOS-like foundation for:

- serial fiction workflows
- world-state persistence
- continuity audits
- chapter revision loops
- side-story / canon-aware writing
