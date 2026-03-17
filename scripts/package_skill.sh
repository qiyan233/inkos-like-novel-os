#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_NAME="inkos-like-novel-os"
OUTDIR="${1:-$(cd "$ROOT/../.." && pwd)/dist}"
VERSION_SUFFIX="${2:-}"
VERSION_FILE="$ROOT/VERSION"
TMPDIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

normalize_tag() {
  local tag="$1"
  tag="${tag//$'\r'/}"
  tag="${tag//$'\n'/}"
  if [[ -n "$tag" && "$tag" != v* ]]; then
    tag="v$tag"
  fi
  printf '%s' "$tag"
}

if [[ -z "$VERSION_SUFFIX" && -f "$VERSION_FILE" ]]; then
  VERSION_SUFFIX="$(cat "$VERSION_FILE")"
fi
VERSION_SUFFIX="$(normalize_tag "$VERSION_SUFFIX")"

mkdir -p "$OUTDIR"
STAGE="$TMPDIR/$SKILL_NAME"
mkdir -p "$STAGE"
cp -R "$ROOT/." "$STAGE/"
find "$STAGE" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "$STAGE" -type f \( -name '*.pyc' -o -name '.DS_Store' \) -delete
rm -rf "$STAGE/.git"

OUTFILE="$OUTDIR/$SKILL_NAME.skill"
rm -f "$OUTFILE"
(
  cd "$TMPDIR"
  zip -qr "$OUTFILE" "$SKILL_NAME" -x '*/.git/*' '*/__pycache__/*' '*/node_modules/*'
)
echo "$OUTFILE"

if [[ -n "$VERSION_SUFFIX" ]]; then
  VERSIONED_OUTFILE="$OUTDIR/$SKILL_NAME-$VERSION_SUFFIX.skill"
  rm -f "$VERSIONED_OUTFILE"
  cp "$OUTFILE" "$VERSIONED_OUTFILE"
  echo "$VERSIONED_OUTFILE"
fi
