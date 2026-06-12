#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 <project-dir> <book-title> [--force]"
  exit 1
fi

PROJECT_DIR="$1"
BOOK_TITLE="$2"
FORCE="${3:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_DIR="$SKILL_DIR/assets/project-template"

if [[ -n "$FORCE" && "$FORCE" != "--force" ]]; then
  echo "Unknown option: $FORCE" >&2
  echo "Usage: $0 <project-dir> <book-title> [--force]" >&2
  exit 1
fi

if [[ -e "$PROJECT_DIR" && ! -d "$PROJECT_DIR" ]]; then
  echo "Init target exists but is not a directory: $PROJECT_DIR" >&2
  exit 1
fi

if [[ -d "$PROJECT_DIR" && "$FORCE" != "--force" ]]; then
  if [[ -n "$(find "$PROJECT_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
    echo "Refusing to initialize non-empty directory: $PROJECT_DIR. Use --force to overwrite template files." >&2
    exit 1
  fi
fi

mkdir -p "$PROJECT_DIR"
cp -r "$TEMPLATE_DIR"/. "$PROJECT_DIR"/
mkdir -p "$PROJECT_DIR/chapters" "$PROJECT_DIR/reviews"

ESCAPED_TITLE="${BOOK_TITLE//\\/\\\\}"
ESCAPED_TITLE="${ESCAPED_TITLE//&/\\&}"
ESCAPED_TITLE="${ESCAPED_TITLE//\//\\/}"

sed -i "s/{{BOOK_TITLE}}/${ESCAPED_TITLE}/g" "$PROJECT_DIR"/README-project.md
sed -i "s/{{BOOK_TITLE}}/${ESCAPED_TITLE}/g" "$PROJECT_DIR"/story_bible.md
sed -i "s/{{BOOK_TITLE}}/${ESCAPED_TITLE}/g" "$PROJECT_DIR"/book_rules.md
sed -i "s/{{BOOK_TITLE}}/${ESCAPED_TITLE}/g" "$PROJECT_DIR"/outline.md
sed -i "s/{{BOOK_TITLE}}/${ESCAPED_TITLE}/g" "$PROJECT_DIR"/current_state.md

echo "Initialized novel project at: $PROJECT_DIR"
echo "Title: $BOOK_TITLE"
