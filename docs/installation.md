# 安装与环境 / Installation

如果你只想先跑起来，按下面做就够了。

> 推荐入口 / Recommended entrypoint：`python scripts/inkos_cli.py ...`

## 方式一：直接使用仓库 / Use the repo directly

```bash
git clone https://github.com/qiyan233/inkos-like-novel-os.git
cd inkos-like-novel-os
python scripts/inkos_cli.py --help
python scripts/inkos_cli.py smoke-test
```

适合你想：

- 先理解这个 skill skeleton 的结构
- 直接改 `SKILL.md`、`scripts/`、`assets/project-template/`
- 把它当作自己的 OpenClaw 小说工作流底座

## 方式二：下载 `.skill` 发布包

如果你主要是面向 OpenClaw 安装使用，可从 Releases 获取 `.skill` 包。

仓库内也可自行打包：

```bash
bash scripts/package_skill.sh
```

## 最小运行要求

- Bash
- Python 3
- 一个可编辑 Markdown / JSON 的本地环境

本仓库当前不依赖复杂第三方 Python 包，默认使用标准库脚本。

## 首次验证 / First verification

建议第一次 clone 后先做两步：

```bash
python -m py_compile scripts/*.py
python scripts/inkos_cli.py smoke-test
```

如果你更习惯直接调底层脚本，也可以继续使用：

```bash
bash scripts/smoke_test.sh
```

如果你正在评估真实使用方式，继续看：

- [快速上手](getting-started.md)
- [用户路径](user-paths.md)
- [CLI 入口](cli.md)
- [示例项目模板说明](project-template.md)

