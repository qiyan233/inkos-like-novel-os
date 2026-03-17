#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <project-dir> <book-title>"
  exit 1
fi

PROJECT_DIR="$1"
BOOK_TITLE="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_DIR="$SKILL_DIR/assets/project-template"

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
