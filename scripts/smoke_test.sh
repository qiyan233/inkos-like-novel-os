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

printf '\n===== init title escaping regression =====\n'
SPECIAL_PROJECT="$TMPDIR/special-title-novel"
SPECIAL_TITLE='A&B/测试'
bash "$ROOT/scripts/init_novel_project.sh" "$SPECIAL_PROJECT" "$SPECIAL_TITLE" >/dev/null
for f in README-project.md story_bible.md book_rules.md outline.md current_state.md; do
  grep -q "$SPECIAL_TITLE" "$SPECIAL_PROJECT/$f"
  if grep -q '{{BOOK_TITLE}}' "$SPECIAL_PROJECT/$f"; then
    echo "placeholder not replaced in $f" >&2
    exit 1
  fi
done
printf 'init title escaping ok\n'

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

printf '\n===== context max-chars regression =====\n'
LONG_SUMMARIES="$PROJECT/chapter_summaries.md"
: > "$LONG_SUMMARIES"
for i in $(seq 1 40); do
  printf '没有章节标题的长文本段落 %03d %080d\n' "$i" "$i" >> "$LONG_SUMMARIES"
done
CTX_JSON="$($PYTHON_BIN "$ROOT/scripts/build_next_chapter_context.py" --project "$PROJECT" --max-chars-per-file 500 --json)"
CTX_LEN=$(printf '%s' "$CTX_JSON" | "$PYTHON_BIN" -c 'import json,sys; data=json.load(sys.stdin); print(len(data["sections"].get("chapter_summaries.md","")))')
if [ "$CTX_LEN" -gt 500 ]; then
  echo "chapter_summaries exceeded max chars: $CTX_LEN" >&2
  exit 1
fi
CTX_TINY="$($PYTHON_BIN "$ROOT/scripts/build_next_chapter_context.py" --project "$PROJECT" --max-chars-per-file 5 --json)"
printf '%s' "$CTX_TINY" | "$PYTHON_BIN" -c 'import json,sys; data=json.load(sys.stdin); assert len(data["sections"]["chapter_summaries.md"]) <= 5; print("tiny max chars ok")' >/dev/null
printf 'context max-chars ok\n'

cat > "$PROJECT/chapter_summaries.md" <<'SUMMARIES'
## Chapter 1 - First
- Summary: one

## 第2章 - Second
- Summary: two

## 第3章 - Third
- Summary: three
SUMMARIES

printf '\n===== chapter heading compatibility regression =====\n'
CTX_JSON_CN="$($PYTHON_BIN "$ROOT/scripts/build_next_chapter_context.py" --project "$PROJECT" --recent-chapters 2 --json)"
printf '%s' "$CTX_JSON_CN" | grep -q '第2章 - Second'
printf '%s' "$CTX_JSON_CN" | grep -q '第3章 - Third'
if printf '%s' "$CTX_JSON_CN" | grep -q 'Chapter 1 - First'; then
  echo 'recent chapter extraction did not respect recent-chapters with Chinese headings' >&2
  exit 1
fi
CTX_ZERO="$($PYTHON_BIN "$ROOT/scripts/build_next_chapter_context.py" --project "$PROJECT" --recent-chapters 0 --json)"
printf '%s' "$CTX_ZERO" | "$PYTHON_BIN" -c 'import json,sys; data=json.load(sys.stdin); assert data["sections"].get("chapter_summaries.md", "") == ""'
set +e
"$PYTHON_BIN" "$ROOT/scripts/build_next_chapter_context.py" --project "$PROJECT" --recent-chapters -1 >/dev/null 2>"$TMPDIR/recent.err"
RECENT_CODE=$?
set -e
if [ "$RECENT_CODE" -eq 0 ]; then
  echo 'expected negative recent-chapters to fail' >&2
  exit 1
fi
grep -q -- '--recent-chapters must be >= 0' "$TMPDIR/recent.err"
printf 'chapter heading compatibility ok\n'

printf '\n===== audit_chapter =====\n'
"$PYTHON_BIN" "$ROOT/scripts/audit_chapter.py" --project "$PROJECT" --chapter-file "$PROJECT/chapters/ch01.md" --json >/dev/null
printf 'chapter audit ok\n'

printf '\n===== update_story_state =====\n'
STATE_JSON="$($PYTHON_BIN "$ROOT/scripts/update_story_state.py" \
  --project "$PROJECT" \
  --chapter 1 \
  --title "第一章" \
  --summary "林烬察觉玉佩疑似被调包，并开始怀疑有人提前动过手脚。" \
  --state-change "林烬确认手中的玉佩手感异常，怀疑其并非原物。" \
  --hook-open "是谁在林烬之前碰过玉佩" \
  --relationship "林烬 -> 徐安：出现试探与怀疑" \
  --emotion "林烬：警觉上升" \
  --json)"
printf '%s' "$STATE_JSON" | "$PYTHON_BIN" -c 'import json,sys; data=json.load(sys.stdin); paths=data["updated_files"]; assert any(p.endswith("chapter_summaries.md") for p in paths); assert any(p.endswith("pending_hooks.md") for p in paths); assert any(p.endswith("character_matrix.md") for p in paths); assert any(p.endswith("emotional_arcs.md") for p in paths)'
STATE_JSON_MIN="$($PYTHON_BIN "$ROOT/scripts/update_story_state.py" \
  --project "$PROJECT" \
  --chapter 2 \
  --title "第二章" \
  --summary "仅摘要更新" \
  --json)"
printf '%s' "$STATE_JSON_MIN" | "$PYTHON_BIN" -c 'import json,sys; data=json.load(sys.stdin); assert len(data["updated_files"]) == 1, data["updated_files"]; assert data["updated_files"][0].endswith("chapter_summaries.md")'
printf 'story state update ok\n'

printf '\n===== revision_plan / spot_fixes =====\n'
"$PYTHON_BIN" "$ROOT/scripts/build_revision_plan.py" --project "$PROJECT" --chapter-file "$PROJECT/chapters/ch01.md" --json >/dev/null
"$PYTHON_BIN" "$ROOT/scripts/suggest_spot_fixes.py" --project "$PROJECT" --chapter-file "$PROJECT/chapters/ch01.md" --json >/dev/null
printf 'revision helpers ok\n'

printf '\n===== snapshot / diff =====\n'
SNAP1=$("$PYTHON_BIN" "$ROOT/scripts/snapshot_story_state.py" --project "$PROJECT" --chapter 1 --label before-edit)
SNAP2=$("$PYTHON_BIN" "$ROOT/scripts/snapshot_story_state.py" --project "$PROJECT" --chapter 1 --label before-edit)
if [ "$SNAP1" = "$SNAP2" ]; then
  echo 'snapshot collision detected'
  exit 1
fi
echo "补一条临时状态" >> "$PROJECT/current_state.md"
"$PYTHON_BIN" "$ROOT/scripts/diff_story_state.py" --project "$PROJECT" --from "$SNAP1" --to current --json >/dev/null
printf 'state snapshot diff ok\n'

printf '\n===== write-report regression =====\n'
"$PYTHON_BIN" "$ROOT/scripts/audit_chapter.py" --project "$PROJECT" --chapter-file "$PROJECT/chapters/ch01.md" --write-report --json > "$TMPDIR/audit.json"
"$PYTHON_BIN" "$ROOT/scripts/update_story_state.py" --project "$PROJECT" --chapter 1 --title "第一章" --summary "回归测试" --write-report --json > "$TMPDIR/state.json"
"$PYTHON_BIN" "$ROOT/scripts/build_revision_plan.py" --project "$PROJECT" --chapter-file "$PROJECT/chapters/ch01.md" --write-report --json > "$TMPDIR/revision.json"
"$PYTHON_BIN" "$ROOT/scripts/suggest_spot_fixes.py" --project "$PROJECT" --chapter-file "$PROJECT/chapters/ch01.md" --write-report --json > "$TMPDIR/fixes.json"
TMPDIR_FOR_PY="$TMPDIR" "$PYTHON_BIN" - <<'PY'
import json
import os
from pathlib import Path

tmpdir = Path(os.environ['TMPDIR_FOR_PY'])
for name in ['audit', 'state', 'revision', 'fixes']:
    stdout = json.load(open(str(tmpdir / (name + '.json')), 'r', encoding='utf-8'))
    report_path = stdout.get('report_path')
    assert report_path, name
    report = json.load(open(report_path, 'r', encoding='utf-8'))
    assert report.get('report_path') == report_path, (name, report)
print('write-report regression ok')
PY

printf '\n===== latest-without-snapshot regression =====\n'
EMPTY="$TMPDIR/empty-project"
mkdir -p "$EMPTY"
cp "$PROJECT/README-project.md" "$EMPTY/README-project.md"
set +e
"$PYTHON_BIN" "$ROOT/scripts/diff_story_state.py" --project "$EMPTY" --from latest --to current >/dev/null 2>"$TMPDIR/latest.err"
CODE=$?
set -e
if [ "$CODE" -eq 0 ]; then
  echo 'expected latest-without-snapshot to fail'
  exit 1
fi
grep -q 'No snapshots found under' "$TMPDIR/latest.err"
printf 'latest-without-snapshot regression ok\n'

printf '\n===== missing-project validation regression =====\n'
MISSING="$TMPDIR/does-not-exist"
for cmd in \
  "build_next_chapter_context.py --project $MISSING" \
  "update_story_state.py --project $MISSING --chapter 1 --title x --summary y" \
  "snapshot_story_state.py --project $MISSING" \
  "diff_story_state.py --project $MISSING --from current --to current"
do
  set +e
  "$PYTHON_BIN" "$ROOT/scripts/${cmd%% *}" ${cmd#* } >/dev/null 2>"$TMPDIR/missing.err"
  CODE=$?
  set -e
  if [ "$CODE" -eq 0 ]; then
    echo "expected missing project validation to fail: $cmd" >&2
    exit 1
  fi
  grep -Eq 'Project (does not exist|is not a directory)' "$TMPDIR/missing.err"
done
set +e
"$PYTHON_BIN" "$ROOT/scripts/audit_chapter.py" --project "$PROJECT" --chapter-file "$TMPDIR/no-such-chapter.md" >/dev/null 2>"$TMPDIR/missing-chapter.err"
CODE=$?
set -e
if [ "$CODE" -eq 0 ]; then
  echo 'expected missing chapter validation to fail' >&2
  exit 1
fi
grep -q 'Chapter file does not exist' "$TMPDIR/missing-chapter.err"
printf 'missing-project validation ok\n'

echo
echo 'Smoke test passed.'
