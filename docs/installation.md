# 安装与环境

如果你只想先跑起来，按下面做就够了。

## 方式一：直接使用仓库

```bash
git clone https://github.com/qiyan233/inkos-like-novel-os.git
cd inkos-like-novel-os
bash scripts/smoke_test.sh
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

## 首次验证

建议第一次 clone 后先做两步：

```bash
python3 -m py_compile scripts/*.py
bash scripts/smoke_test.sh
```

如果你正在评估真实使用方式，继续看：

- [快速上手](getting-started.md)
- [用户路径](user-paths.md)
- [示例项目模板说明](project-template.md)
