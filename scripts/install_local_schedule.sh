#!/bin/bash
# Install a launchd agent that saves each morning's drafts into X.
#
#   bash scripts/install_local_schedule.sh          # install
#   bash scripts/install_local_schedule.sh --remove # uninstall
#
# Runs at 08:05 local time. If the Mac is asleep or shut down then,
# launchd runs the job once at the next wake, so a closed laptop only
# delays the drafts rather than skipping the day.
#
# This is a LaunchAgent, not a LaunchDaemon: it runs as you, inside your
# GUI login session, which is what gives it access to the browser profile
# holding your X session.

set -euo pipefail

LABEL="com.descidecoded.xdrafts"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$HOME/Library/Logs"

if [ "${1:-}" = "--remove" ]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Removed $LABEL."
  exit 0
fi

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This installs a macOS launchd agent and only runs on macOS." >&2
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

cat > "$PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$REPO_DIR/scripts/save_latest_drafts.sh</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$REPO_DIR</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>5</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>$LOG_DIR/$LABEL.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/$LABEL.err.log</string>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
PLIST_EOF

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "Installed $LABEL -- runs daily at 08:05, or at next wake if asleep."
echo
echo "  Logs:       $LOG_DIR/$LABEL.log"
echo "  Errors:     $LOG_DIR/$LABEL.err.log"
echo "  Run now:    launchctl kickstart -k gui/$(id -u)/$LABEL"
echo "  Uninstall:  bash scripts/install_local_schedule.sh --remove"
echo
echo "Before relying on it, run the saver once by hand so the browser"
echo "profile has a signed-in X session:"
echo "  python3 scripts/save_x_drafts.py --input digests/<date>/drafts.json"
