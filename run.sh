#!/bin/bash
set -euo pipefail

SIGNAL_DIR="/Users/malcolmsheehan/Documents/Claude/signal"
PYTHON="$SIGNAL_DIR/.venv/bin/python"
LOG="$SIGNAL_DIR/logs/signal.log"

cd "$SIGNAL_DIR"
echo "--- $(date '+%Y-%m-%d %H:%M:%S') ---" >> "$LOG"
"$PYTHON" main.py >> "$LOG" 2>&1
