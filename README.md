# inkos-like-novel-os

[![CI](https://img.shields.io/github/actions/workflow/status/qiyan233/inkos-like-novel-os/ci.yml?branch=main&label=CI)](https://github.com/qiyan233/inkos-like-novel-os/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Version](https://img.shields.io/badge/version-v0.5.1-blue)](CHANGELOG.md)

当前版本：**0.5.1**

一个面向 **OpenClaw** 的长篇小说工作流 skill。  
它的重点不是“单次写一章”，而是把长篇 / 连载 / 网文 / 同人写作跑成一个**长期可维护的流程**。

灵感参考原项目 **InkOS**：<https://github.com/Narcooo/inkos>

> 本项目是受 InkOS 启发的 skill skeleton，不是原项目官方移植版。

中文 | [English](#english)

---

## 这是什么

你可以把它理解成一个“小说 workflow skill”：

- 用 truth files 维护世界观和当前状态
- 用 `write-next` 准备下一章
- 用 `revise` 做修订闭环
- 用 `extract-state` / `state-update` 维护长期状态

也就是说，它不是只负责“写”，而是负责把**多章写作**这件事组织起来。

---

## 适合谁

适合这些情况：

- 你想做一个类似 InkOS 的小说写作 skill
- 你想让 AI 连续写很多章时尽量别崩设定
- 你想长期维护章节摘要、角色状态、伏笔和当前局势
- 你希望写作之外还有审计、修订、状态更新、快照这些环节

如果你只是想临时生成一篇短文，这个仓库会偏重。  
如果你想跑**长期、多章、可回溯**的小说流程，它就是为这个场景准备的。

---

## 现在这个版本多了什么

`0.5.1` 这个版本继续把它往“可运行 workflow skill”方向推进。

这次比较关键的提升是：

- 有了 `write-next`，能把“下一章怎么写”整理成结构化工作包
- 有了 `revise`，能把修订环节串成一个入口
- 文档和输出契约开始围绕 workflow，而不只是围绕单个脚本

换句话说，它从一个 skill skeleton，往“更可运行的 workflow 层”迈了一步。

---

## 核心使用方式

如果只记一条主线，可以理解成：

```text
init -> write-next -> draft -> revise -> extract-state -> state-update
```

这里不展开写很多指令细节，因为这个仓库本身是 skill。  
真正给智能体看的使用方式，应该优先看：

- [`SKILL.md`](SKILL.md)

如果你是人在看仓库、想快速理解这个 skill 怎么用，建议看：

- [`examples/demo-novel/README.md`](examples/demo-novel/README.md)
- [`docs/cli.md`](docs/cli.md)

---

## 第一次看这个仓库，建议这样读

### 先看定位

- [`SKILL.md`](SKILL.md)

这是这个仓库最核心的文件。  
README 负责介绍项目，`SKILL.md` 才更接近“这个 skill 真正怎么工作”。

### 再看一个完整例子

- [`examples/demo-novel/`](examples/demo-novel/)

如果你想最快看懂 `write-next / revise / state-update` 是怎么串起来的，先看 demo，比先读很多实现细节更直观。

### 最后按需看文档

- [`docs/cli.md`](docs/cli.md)
- [`docs/getting-started.md`](docs/getting-started.md)
- [`docs/project-template.md`](docs/project-template.md)

---

## 仓库里主要有什么

这里只说用途，不展开实现：

- `SKILL.md`：skill 主说明
- `scripts/`：入口和辅助脚本
- `assets/project-template/`：小说项目模板
- `examples/`：示例项目
- `docs/`：使用说明
- `references/`：规则、结构和契约参考

如果你是普通使用者，最常接触的通常是：

- `SKILL.md`
- `examples/demo-novel/`
- `docs/cli.md`

---

## 当前定位

这个仓库现在更像一个**面向长篇小说的 workflow skill**，而不是单纯的 prompt 集合。

它已经能覆盖的事情：

- 下一章准备
- 修订闭环
- 状态提取
- truth files 更新
- 基础回归和打包

还没做到的事情也很明确：

- 真正的 LLM 写作执行器
- 更强的规则引擎
- 更深入的自动修订
- 更多完整示例项目

---

## 更多内容

- [CHANGELOG.md](CHANGELOG.md)
- [docs/cli.md](docs/cli.md)
- [docs/getting-started.md](docs/getting-started.md)
- [docs/project-template.md](docs/project-template.md)
- [references/json-schemas.md](references/json-schemas.md)
- [references/workflow-playbooks.md](references/workflow-playbooks.md)

---

## English

An OpenClaw-oriented long-form fiction workflow skill.

This project is not mainly about generating a single chapter.  
It is about running multi-chapter fiction as a maintainable workflow.

Core idea:

```text
init -> write-next -> draft -> revise -> extract-state -> state-update
```

If you are new here, start with:

1. [SKILL.md](SKILL.md)
2. [examples/demo-novel/README.md](examples/demo-novel/README.md)
3. [docs/cli.md](docs/cli.md)

For humans, this README is intentionally lightweight.  
The real operating behavior of the skill lives in `SKILL.md`.
