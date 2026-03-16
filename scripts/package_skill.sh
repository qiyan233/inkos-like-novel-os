#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_NAME="inkos-like-novel-os"
OUTDIR="${1:-$(cd "$ROOT/../.." && pwd)/dist}"
VERSION_SUFFIX="${2:-}"
TMPDIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

mkdir -p "$OUTDIR"
STAGE="$TMPDIR/$SKILL_NAME"
mkdir -p "$STAGE"
cp -R "$ROOT/." "$STAGE/"
find "$STAGE" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "$STAGE" -type f \( -name '*.pyc' -o -name '.DS_Store' \) -delete
rm -rf "$STAGE/.git"

BASENAME="$SKILL_NAME"
if [[ -n "$VERSION_SUFFIX" ]]; then
  BASENAME="$SKILL_NAME-$VERSION_SUFFIX"
fi
OUTFILE="$OUTDIR/$BASENAME.skill"
rm -f "$OUTFILE"
(
  cd "$TMPDIR"
  zip -qr "$OUTFILE" "$SKILL_NAME" -x '*/.git/*' '*/__pycache__/*' '*/node_modules/*'
)
echo "$OUTFILE"
