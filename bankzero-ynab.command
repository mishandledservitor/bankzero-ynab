#!/usr/bin/env bash
# Launcher for Bank Zero -> YNAB converter
# Double-click to run, or drag a CSV onto this file
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ $# -gt 0 ]; then
    python3 "$SCRIPT_DIR/bankzero_to_ynab.py" "$1"
else
    python3 "$SCRIPT_DIR/bankzero_to_ynab.py"
fi

osascript -e 'tell application "Terminal" to close front window' &
exit 0
