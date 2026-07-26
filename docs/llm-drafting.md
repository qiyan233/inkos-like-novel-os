# LLM 起草与自动修订 / LLM Drafting & Auto Revision

从 1.1.0 起，`draft` 与 `auto-revise` 两个命令把 write-next 工作包和修订闭环接到真实的 LLM 上。默认面向 **Nous Hermes** 系列模型，协议是 OpenAI 兼容 chat completions——任何兼容端点（Ollama、LM Studio、vLLM、Nous Portal）都可用。

## 接入方式

### 本地 Ollama（默认）

模板配置开箱即用，无需 API key：

```json
{
  "llm": {
    "provider": "ollama",
    "base_url": "http://localhost:11434/v1",
    "model": "hermes4"
  }
}
```

准备工作：

```bash
ollama pull hermes4
ollama serve
```

然后：

```bash
python scripts/novelops_cli.py draft --project /path/to/project --chapter 3 --json
```

### Nous Portal 云端

改 `novelops.config.json` 的 `llm` 节：

```json
{
  "llm": {
    "provider": "nous",
    "base_url": "https://inference-api.nousresearch.com/v1",
    "model": "Hermes-4-405B",
    "api_key_env": "NOVELOPS_LLM_API_KEY"
  }
}
```

API key 通过环境变量传入（优先于配置文件里的 `api_key` 明文字段，后者不推荐入库）：

```bash
export NOVELOPS_LLM_API_KEY=你的key
```

## Hermes 相关默认值

- 采样：`temperature=0.6`、`top_p=0.95`（Hermes 4 官方推荐值，可在配置或 CLI flag 覆盖）
- `<think>` 推理块：Hermes 4 是混合推理模型，响应可能带 `<think>...</think>`；`strip_think: true`（默认）会在落盘前剥离。若剥离后发现未闭合的 `<think>`，说明响应大概率被 `max_tokens` 截断，命令会报错提示调大 `llm.max_tokens`
- 单章契约：draft 的提示词首尾双压"只输出第 N 章正文"；若模型仍输出多个章节标题，草稿会被**拒绝**而不是静默截断

## 离线通道（不联网）

两条路径，主要供调试与回归测试：

```bash
# 只组装并输出完整请求 payload，不调用任何网络
python scripts/novelops_cli.py draft --project P --chapter 3 --dry-run --json

# 用文件内容充当模型响应，走完整校验与落盘链路
python scripts/novelops_cli.py draft --project P --chapter 3 --mock-response mock.txt --json
```

mock 文件支持三种形态：JSON 数组（多段响应，auto-revise 多 target 时按序取用）、OpenAI 响应对象（取 `choices[0].message.content`）、纯文本（整个文件当响应）。环境变量 `NOVELOPS_LLM_MOCK` 与 `--mock-response` 等效（flag 优先）。

## auto-revise 的安全设计

```bash
# 缺省：重写但只输出整章 unified diff，不写盘
python scripts/novelops_cli.py auto-revise --project P --chapter-file P/chapters/ch03.md --json

# 确认 diff 后再写回：先自动 snapshot + 章节原文备份
python scripts/novelops_cli.py auto-revise --project P --chapter-file P/chapters/ch03.md --apply --json
```

`--apply` 写回前会：
1. 调 snapshot 备份全部 truth files（`.novelops-state/snapshots/<id>/`）
2. 把章节原文备份到 `.novelops-state/backups/<id>/`（章节不在快照追踪清单里）

回滚 = 把备份文件复制回 `chapters/`。

只有 local-dimension（可局部修补）的问题会被重写；全篇性问题（段落节奏、对话密度）与定位不到段落的问题会记入 `skipped_findings`，交人工处理。

## 常见报错排查

| 报错关键词 | 原因与处理 |
| --- | --- |
| `cannot connect to` | 端点未启动。本地跑 `ollama serve`，或检查 `llm.base_url` |
| `timed out after` | 模型太慢或章节太长。调大 `llm.timeout_seconds` |
| `LLM HTTP 401/403` | key 无效。检查环境变量 `NOVELOPS_LLM_API_KEY` 或 `llm.api_key` |
| `unclosed <think> block` | 响应被截断。调大 `llm.max_tokens` |
| `contains N chapter headings` | 模型越章。重试，或调小 `max_tokens`、检查提示词约束 |
| `Draft target already exists` | 目标章节已存在。确认后加 `--force` |

代理环境提示：`urllib` 会读取 `HTTP_PROXY`/`HTTPS_PROXY` 环境变量。若本机代理拦截了 localhost 请求，设置 `NO_PROXY=localhost,127.0.0.1`。

## smoke test 与 CI

`python scripts/smoke_test.py` 覆盖了 draft / auto-revise 的 dry-run 与 mock 全链路，**全程离线**——真实网络调用永不进 smoke test 与 CI。
