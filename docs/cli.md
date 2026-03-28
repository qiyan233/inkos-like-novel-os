# CLI 入口 / CLI Entrypoint

`python3 scripts/inkos_cli.py ...` 是这个仓库当前推荐的**统一主入口 / unified entrypoint**。

它不会改变底层脚本的职责，而是把常见工作流命令集中到一个地方，方便你在 README、docs、demo 和日常使用里走同一条路径。

## 什么时候优先用 CLI / When to prefer CLI

优先用 CLI：

- 你是第一次上手这个仓库
- 你想跑完整工作流，而不是记住很多脚本名
- 你希望 README / docs / demo 用一致命令
- 你想把 `init -> context -> audit -> extract-state -> state-update -> smoke-test` 作为主线

## 什么时候直接调底层脚本 / When to call scripts directly

直接调底层脚本更合适：

- 你在调试某个单独脚本
- 你在 shell / CI / 外部工具里只复用一个能力
- 你需要更明确地区分 Bash 脚本和 Python 脚本

## 常用命令 / Common commands

### 初始化项目 / Initialize

```bash
python3 scripts/inkos_cli.py init /path/to/project "书名"
```

### 生成上下文 / Build context

```bash
python3 scripts/inkos_cli.py context --project /path/to/project
```

### 审计章节 / Audit chapter

```bash
python3 scripts/inkos_cli.py audit \
  --project /path/to/project \
  --chapter-file /path/to/project/chapters/ch01.md
```

### 提取候选状态 / Extract candidate state

```bash
python3 scripts/inkos_cli.py extract-state \
  --project /path/to/project \
  --chapter-file /path/to/project/chapters/ch01.md \
  --json
```

### 更新 truth files / Update truth files

```bash
python3 scripts/inkos_cli.py state-update \
  --project /path/to/project \
  --chapter 1 \
  --title "第一章" \
  --summary "..."
```

### 跑回归 / Run smoke tests

```bash
python3 scripts/inkos_cli.py smoke-test
```

## 补充说明 / Notes

- 这次调整**不要求**把 CLI 做成 pip 包。
- 当前目标只是把 CLI 提升为更正式、可被自然引用的入口。
- 底层脚本仍然是实际能力实现层，CLI 只是轻量封装。
