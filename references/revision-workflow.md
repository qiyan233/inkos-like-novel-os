# Revision Workflow

这一层工作流解决的不是“怎么生成一章”，而是“写完之后如何稳地修”。

## 推荐顺序

1. 跑审计：`audit_chapter.py`
2. 产出修订计划：`build_revision_plan.py`
3. 生成低风险 spot-fix 建议：`suggest_spot_fixes.py`
4. 若章节接受，更新 truth files
5. 在关键节点做状态快照：`snapshot_story_state.py`
6. 如有争议，比较快照差异：`diff_story_state.py`

## 角色分工

### 审计器
负责发现问题，不负责改正文。

### 修订计划器
负责决定：
- 是 spot-fix 还是 scene-level rewrite
- 哪些问题必须先修
- 哪些问题需要人类确认

### Spot-fix 建议器
只做低风险、局部性的改动建议，不碰高风险剧情判断。

### 状态快照器
负责在章节接受或重大调整前后留下 truth files 的可回溯版本。

## 核心原则

- 先定修订策略，再动正文
- 优先修 high-severity 问题
- 优先局部修，不轻易整章推倒
- 每次接受关键章节后都值得做 snapshot
