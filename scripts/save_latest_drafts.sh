#!/bin/bash
# Pull the newest cloud-generated digest and save its drafts into X.
#
# Meant to be run by launchd (see install_local_schedule.sh), but safe to
# run by hand. Skips a digest it has already saved, so waking the Mac
# several times a day won't duplicate drafts.

set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR" || exit 1

STATE_DIR="$REPO_DIR/work"
mkdir -p "$STATE_DIR"
SAVED_LOG="$STATE_DIR/.saved-digests"
touch "$SAVED_LOG"

PYTHON="$REPO_DIR/.venv/bin/python3"
[ -x "$PYTHON" ] || PYTHON="$(command -v python3)"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') saving latest drafts ==="

git pull --quiet --ff-only || {
  echo "git pull failed; using whatever is already checked out." >&2
}

# Newest digests/<date>/drafts.json by directory name (dates sort lexically).
LATEST="$(ls -d digests/*/ 2>/dev/null | sort | tail -1)"
if [ -z "$LATEST" ]; then
  echo "No digests found yet. Nothing to do."
  exit 0
fi

DATE="$(basename "$LATEST")"
DRAFTS="$LATEST/drafts.json"

if [ ! -f "$DRAFTS" ]; then
  echo "No drafts.json in $LATEST. Nothing to do."
  exit 0
fi

if grep -qxF "$DATE" "$SAVED_LOG"; then
  echo "Digest $DATE already saved. Nothing to do."
  exit 0
fi

echo "Saving drafts from $DRAFTS"
if "$PYTHON" scripts/save_x_drafts.py --input "$DRAFTS" --no-wait; then
  echo "$DATE" >> "$SAVED_LOG"
  echo "Saved $DATE."
else
  echo "Saving $DATE failed; leaving it unmarked so the next run retries." >&2
  exit 1
fi
