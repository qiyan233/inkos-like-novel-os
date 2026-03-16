#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TMPDIR="$(mktemp -d)"
PROJECT="$TMPDIR/demo-novel"
cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

bash "$ROOT/scripts/init_novel_project.sh" "$PROJECT" "测试长篇"
mkdir -p "$PROJECT/chapters" "$PROJECT/reviews"

cat > "$PROJECT/chapters/ch01.md" <<'CHAPTER'
# Chapter 1

林烬推开旧库房的门时，先闻到一股潮木味，像是很多年前被封住的雨水。

桌上的玉佩安静地躺在布包里，颜色、纹路、缺口都和记忆里一样，可他摸上去时，指腹却迟疑了一瞬。

太新了。

不是表面的光，而是一种不该存在的完整感。真正跟了徐家十几年的东西，不会在边角处毫无磨痕。

“你在看什么？”徐安站在门边，语气平静。

林烬把玉佩收回掌心，没有立刻抬头：“我在想，谁有机会先碰到它。”

徐安没有接话。库房外风声掠过窗纸，像有人在暗处轻轻笑了一下。
CHAPTER

printf '\n===== build_next_chapter_context =====\n'
"$PYTHON_BIN" "$ROOT/scripts/build_next_chapter_context.py" --project "$PROJECT" >/dev/null
printf 'context build ok\n'

printf '\n===== audit_chapter =====\n'
"$PYTHON_BIN" "$ROOT/scripts/audit_chapter.py" --project "$PROJECT" --chapter-file "$PROJECT/chapters/ch01.md" --json >/dev/null
printf 'chapter audit ok\n'

printf '\n===== update_story_state =====\n'
"$PYTHON_BIN" "$ROOT/scripts/update_story_state.py" \
  --project "$PROJECT" \
  --chapter 1 \
  --title "第一章" \
  --summary "林烬察觉玉佩疑似被调包，并开始怀疑有人提前动过手脚。" \
  --state-change "林烬确认手中的玉佩手感异常，怀疑其并非原物。" \
  --hook-open "是谁在林烬之前碰过玉佩" \
  --relationship "林烬 -> 徐安：出现试探与怀疑" \
  --emotion "林烬：警觉上升" \
  --json >/dev/null
printf 'story state update ok\n'

printf '\n===== revision_plan / spot_fixes =====\n'
"$PYTHON_BIN" "$ROOT/scripts/build_revision_plan.py" --project "$PROJECT" --chapter-file "$PROJECT/chapters/ch01.md" --json >/dev/null
"$PYTHON_BIN" "$ROOT/scripts/suggest_spot_fixes.py" --project "$PROJECT" --chapter-file "$PROJECT/chapters/ch01.md" --json >/dev/null
printf 'revision helpers ok\n'

printf '\n===== snapshot / diff =====\n'
SNAP1=$("$PYTHON_BIN" "$ROOT/scripts/snapshot_story_state.py" --project "$PROJECT" --chapter 1 --label before-edit)
echo "补一条临时状态" >> "$PROJECT/current_state.md"
"$PYTHON_BIN" "$ROOT/scripts/diff_story_state.py" --project "$PROJECT" --from "$SNAP1" --to current --json >/dev/null
printf 'state snapshot diff ok\n'

echo
echo 'Smoke test passed.'
