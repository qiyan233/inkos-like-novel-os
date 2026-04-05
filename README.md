# inkos-like-novel-os

[![CI](https://img.shields.io/github/actions/workflow/status/qiyan233/inkos-like-novel-os/ci.yml?branch=main&label=CI)](https://github.com/qiyan233/inkos-like-novel-os/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Version](https://img.shields.io/badge/version-v0.5.0-blue)](CHANGELOG.md)

当前版本：**0.5.0**

完整变更记录见 [CHANGELOG.md](CHANGELOG.md)。

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



## 快速导航



### 一句话定位



一个面向 **OpenClaw** 的长篇小说工作流 skill skeleton：用 truth files、审计脚本和状态更新工具，把小说写作运行成可持续维护的流程。



### 适合谁



- 想搭建 **类似 InkOS** 的 OpenClaw 小说工作流

- 想把长篇 / 连载 / 网文 / 同人写作做成**可协作、可追踪、可回归验证**的仓库

- 想让 AI 写多章时，尽量基于 `current_state.md`、`chapter_summaries.md`、`pending_hooks.md` 等文件稳定推进

- 想在起草之外，补上 audit、revision、snapshot/diff 这些“工程化”环节



### 快速开始入口 / Quick Entry







1. **先读定位 / Start with positioning**：[`SKILL.md`](SKILL.md)



2. **看仓库能力与使用方式 / Usage overview**：本 README 的[快速开始](#快速开始)



3. **优先使用统一 CLI / Prefer the unified CLI**：







```bash



python3 scripts/inkos_cli.py init /path/to/project "书名"



```







4. **跑一遍基础回归 / Run a baseline check**：







```bash



python3 scripts/inkos_cli.py smoke-test



```







5. **如果你是第一次上手 / First time here**：可先看 [`docs/getting-started.md`](docs/getting-started.md)

6. **想直接看一个完整例子 / Example-first**：打开 [`examples/demo-novel/README.md`](examples/demo-novel/README.md)

7. **想看 CLI 与底层脚本的关系 / CLI vs scripts**：打开 [`docs/cli.md`](docs/cli.md)




### 仓库结构导览



- `SKILL.md`：技能主说明，定义工作流与操作模型

- `scripts/`：初始化、审计、状态更新、快照 diff、打包、smoke test 等脚本

- `references/`：审计规则、文件结构、workflow playbooks、worked examples

- `assets/project-template/`：新小说项目模板

- `docs/`：补充上手说明与协作文档
- `examples/demo-novel/`：最小但完整的示例小说项目，可直接对照 context / audit / extract-state / state-update



## 最新更新


### v0.5.0

- 新增 `write-next` 工作流入口：把下一章写作准备整理成结构化 packet，而不是只给一段大块 context
- 新增 `revise` 工作流入口：把 `knowledge-check + audit + revision-plan + spot-fixes` 串成单次修订闭环
- 新增 `build_write_next_packet.py` / `run_revision_cycle.py`
- `write-next` 现在可输出 `chapter_file_hint`、`plan_template` 并支持 `--write-report`
- `revise` 现在会附带 hook pressure / stale hook 摘要，并支持 `--write-report`
- smoke test 现在覆盖 `write-next / revise`
- CLI 从“统一脚本入口”进一步升级为更完整的工作流入口

如果只想看本次发布说明，可直接看 [CHANGELOG.md](CHANGELOG.md)。

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
- `update_story_state.py` — 追加章节状态变更（章节摘要、伏笔、关系、情绪变化等），同步 `current_state.md` 的最新接受章节信息，并可输出稳定 JSON 更新报告
- `build_write_next_packet.py` — 基于 truth files、outline、hooks 和 current state 构建下一章结构化工作包
- `audit_chapter.py` — 对章节做启发式但结构化的规则审计，输出稳定 JSON 或 Markdown 报告
- `build_next_chapter_context.py` — 从 truth files 自动拼装“下一章写作上下文”，并支持稳定 JSON 输出
- `run_revision_cycle.py` — 统一输出 knowledge-check、audit、revision plan 与 spot-fix 建议
- `inkos_cli.py` — 轻量 CLI 封装，统一 init/context/audit/knowledge-check/extract-state/hook-report/state-update/revision-plan/spot-fixes/snapshot/diff/package/smoke-test 入口
- `smoke_test.py` — 跨平台快速回归测试整个 init → context → audit → update → revision-plan → spot-fixes → snapshot/diff / package 链路
- `package_skill.py` — 跨平台稳定打包 `.skill` 文件，并在存在 `VERSION` 时自动输出带版本号的 `.skill` 副本
- `smoke_test.sh` — 兼容保留的 shell 回归入口
- `package_skill.sh` — 兼容保留的 shell 打包入口
- `build_revision_plan.py` — 基于 audit report 产出结构化修订计划，区分局部修补与场景级重写
- `suggest_spot_fixes.py` — 为低风险局部问题生成 spot-fix 建议
- `snapshot_story_state.py` — 对 truth files 建立版本化快照
- `diff_story_state.py` — 对比 snapshot 与当前 / 其他 snapshot 的状态差异

### 4. `assets/project-template/`
小说项目模板，包含：

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

## 安装与使用



### 方式一：安装 `.skill` 发布包



从 Releases 下载 `.skill` 文件，用你的 OpenClaw / skill 安装流程导入。



### 方式二：直接使用仓库目录 / Use the repo directly



克隆仓库后，推荐把 `scripts/inkos_cli.py` 当作**统一主入口 / unified entrypoint**，其下再调用各个底层脚本：



- `SKILL.md`

- `references/`

- `scripts/`

- `assets/project-template/`



如需快速确认 CLI 可用：



```bash

python3 scripts/inkos_cli.py --help

```



## 快速开始 / CLI Quickstart



> 推荐入口 / Recommended entrypoint：`python3 scripts/inkos_cli.py ...`

>

> 底层脚本仍然保留，但更适合作为高级用法 / advanced usage。



### 1. init — 初始化项目 / Initialize a project



```bash

python3 scripts/inkos_cli.py init /path/to/project "书名"

```



初始化后会自动准备：



- truth files 模板

- `chapters/`

- `reviews/`



### 2. context — 生成下一章上下文 / Build next-chapter context



```bash

python3 scripts/inkos_cli.py context \

  --project /path/to/project

```



### 2.5. write-next — 生成下一章工作包 / Build write-next packet

```bash

python3 scripts/inkos_cli.py write-next \

  --project /path/to/project \

  --json

```

### 3. audit — 审计章节 / Audit a chapter



```bash

python3 scripts/inkos_cli.py audit \

  --project /path/to/project \

  --chapter-file /path/to/project/chapters/ch12.md

```



输出 JSON：



```bash

python3 scripts/inkos_cli.py audit \

  --project /path/to/project \

  --chapter-file /path/to/project/chapters/ch12.md \

  --json

```



### 4. extract-state — 提取候选状态更新 / Extract candidate state updates



```bash

python3 scripts/inkos_cli.py extract-state \

  --project /path/to/project \

  --chapter-file /path/to/project/chapters/ch12.md \

  --json

```



### 5. state-update — 写回状态 / Update truth files



```bash

python3 scripts/inkos_cli.py state-update \

  --project /path/to/project \

  --chapter 12 \

  --title "沉默的代价" \

  --summary "主角第一次确认玉佩被人调包" \

  --state-change "林烬确认玉佩是伪造的" \

  --hook-open "是谁替换了玉佩" \

  --relationship "林烬 -> 徐安：信任下降" \

  --emotion "林烬：怀疑上升"

```



### 6. smoke-test — 跑基础回归 / Run smoke tests



```bash

python3 scripts/inkos_cli.py smoke-test

```



### 7. revise — 跑修订闭环 / Run revision cycle

```bash

python3 scripts/inkos_cli.py revise \

  --project /path/to/project \

  --chapter-file /path/to/project/chapters/ch12.md \

  --json

```

### 底层脚本 / Advanced usage



如果你需要更细粒度地单独调用脚本、调试某一段链路、或在外部工具里直接复用某个脚本，也仍然可以继续使用：



- `bash scripts/init_novel_project.sh ...`

- `python3 scripts/build_next_chapter_context.py ...`

- `python3 scripts/build_write_next_packet.py ...`

- `python3 scripts/audit_chapter.py ...`

- `python3 scripts/extract_state.py ...`

- `python3 scripts/update_story_state.py ...`

- `python3 scripts/run_revision_cycle.py ...`

- `python3 scripts/smoke_test.py`

- `python3 scripts/package_skill.py ...`



跨平台场景下，优先使用 `scripts/inkos_cli.py` 与 Python 版辅助脚本。更详细的 CLI 说明见 [`docs/cli.md`](docs/cli.md)。



## 最小工作流示例


假设用户说：

> 帮我继续写第 12 章，重点是主角开始怀疑徐安，但不要直接撕破脸。

推荐流程：



1. 先生成下一章工作包



```bash

python3 scripts/inkos_cli.py write-next --project /path/to/project --json

```



2. 用 `write-next` 里的 chapter function / scene beats 去起草章节

3. 起草完成后跑修订闭环



```bash

python3 scripts/inkos_cli.py revise \

  --project /path/to/project \

  --chapter-file /path/to/project/chapters/ch12.md \

  --json

```



4. 根据 `revise` 结果先修 blocking / major 问题

5. 用 extract-state 生成候选状态更新

6. 接受后更新状态



```bash

python3 scripts/inkos_cli.py state-update ...

```



如果你更习惯直接调底层脚本，也可以切回 `scripts/*.py`；但文档与示例现在默认以 CLI 作为主路径。


## JSON 与 CLI

当前脚本已经开始提供更稳定的 JSON 契约，适合后续接自动修订脚本、状态快照或外部工具。

可参考：

- `references/json-schemas.md`
- `references/audit-rules.md`
- `references/revision-workflow.md`

### 统一 CLI 示例 / Unified CLI examples



```bash

python3 scripts/inkos_cli.py init /path/to/project "书名"

python3 scripts/inkos_cli.py context --project /path/to/project --json

python3 scripts/inkos_cli.py write-next --project /path/to/project --json

python3 scripts/inkos_cli.py audit --project /path/to/project --chapter-file /path/to/project/chapters/ch12.md --json

python3 scripts/inkos_cli.py knowledge-check --project /path/to/project --chapter-file /path/to/project/chapters/ch12.md --json

python3 scripts/inkos_cli.py extract-state --project /path/to/project --chapter-file /path/to/project/chapters/ch12.md --json

python3 scripts/inkos_cli.py hook-report --project /path/to/project --stale-after 5 --json

python3 scripts/inkos_cli.py state-update --project /path/to/project --chapter 12 --title "沉默的代价" --summary "..." --json

python3 scripts/inkos_cli.py revision-plan --project /path/to/project --chapter-file /path/to/project/chapters/ch12.md --json

python3 scripts/inkos_cli.py spot-fixes --project /path/to/project --chapter-file /path/to/project/chapters/ch12.md --json

python3 scripts/inkos_cli.py revise --project /path/to/project --chapter-file /path/to/project/chapters/ch12.md --json

python3 scripts/inkos_cli.py snapshot --project /path/to/project --chapter 12 --label accepted --json

python3 scripts/inkos_cli.py diff --project /path/to/project --from latest --to current --json

python3 scripts/inkos_cli.py smoke-test

```



CLI 现在是文档中的默认入口；底层脚本主要用于高级调试、脚本集成和逐个能力验证。



## 修订与状态版本化

现在这套骨架已经不只是“写完后跑个 audit”，而是开始形成更完整的 revision OS：

- `audit_chapter.py`：发现问题
- `build_revision_plan.py`：决定修订策略与优先级
- `suggest_spot_fixes.py`：给出低风险局部修改建议
- `snapshot_story_state.py`：在关键节点保存 truth files 快照
- `diff_story_state.py`：比较 snapshot 与当前状态的变化

适合的最小闭环：

1. 写完章节
2. 跑 audit
3. 产出 revision plan
4. 处理 spot-fix / scene rewrite
5. 接受章节后更新 truth files
6. 建立 snapshot，必要时再 diff 回查

## 验证与打包

### 跑 smoke test

```bash
python3 scripts/smoke_test.py
```

它会自动验证：

- 项目初始化
- 下一章上下文构建
- 章节审计
- 状态更新
- 修订计划与 spot-fix 建议
- 状态快照与差异对比
- `write-report` 落盘一致性、snapshot 唯一性、无快照时的错误提示回归验证
- 边界参数与错误路径输入的回归验证

### 打包 `.skill`

```bash
python3 scripts/package_skill.py
```

输出会写到默认 `dist/` 目录。

如果要显式指定输出目录和版本后缀：

```bash
python3 scripts/package_skill.py /path/to/dist v0.1.3
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

> **从 InkOS 风格 skill 骨架升级到更可运行的 workflow 层**

已经包含：

- 项目结构
- 状态文件设计
- 审计参考
- 工作流说明
- 初始化 / 更新脚本
- 上下文组装脚本
- write-next 工作包入口
- 启发式但结构化的章节审计脚本
- revise 修订闭环入口
- 稳定 JSON schema 输出
- 轻量 CLI
- smoke test
- 稳定打包脚本

还没包含：

- 真正的 LLM 写作执行器
- 守护进程 / 通知 / 多 agent 调度
- 更强的规则引擎和自动修订系统

## Roadmap

### 已完成

- [x] 基础 skill 骨架
- [x] 项目模板与 truth files
- [x] 下一章上下文组装
- [x] 启发式章节审计
- [x] 状态更新脚本
- [x] revision plan / spot-fix 辅助
- [x] knowledge boundary 检查
- [x] hook lifecycle 报告
- [x] draft-to-state 候选提取
- [x] story-state snapshot / diff
- [x] 稳定 JSON 契约（v1）
- [x] 轻量 CLI 封装
- [x] write-next 工作流入口
- [x] revise 工作流入口
- [x] `.skill` 打包与版本化产物
- [x] smoke test 回归

### 下一步

- [ ] 更强的规则引擎与更细粒度审计
- [ ] 场景级 rewrite / patch 辅助
- [ ] knowledge-check 与 truth files 的更深联动
- [ ] 更多 worked examples / 示例项目
- [ ] 更完整的 LLM 写作执行器接入

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
