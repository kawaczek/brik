#!/bin/sh
# ==============================================================================
# BrickDeck Launcher for TrimUI Brick
# ==============================================================================

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR" || exit 1

LOG_FILE="$APP_DIR/brickdeck.log"
echo "=== Starting BrickDeck OS $(date) ===" > "$LOG_FILE"

export LD_LIBRARY_PATH="$APP_DIR/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$APP_DIR:$PYTHONPATH"

# Find suitable Python 3
PYTHON=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif [ -f "/mnt/SDCARD/System/bin/python3" ]; then
    PYTHON="/mnt/SDCARD/System/bin/python3"
elif [ -f "/usr/bin/python3" ]; then
    PYTHON="/usr/bin/python3"
fi

if [ -z "$PYTHON" ]; then
    echo "ERROR: python3 interpreter not found!" >> "$LOG_FILE"
    exit 1
fi

echo "Using Python: $PYTHON" >> "$LOG_FILE"
$PYTHON "$APP_DIR/brickdeck.py" --mode fb >> "$LOG_FILE" 2>&1

EXIT_CODE=$?
echo "=== BrickDeck stopped with code $EXIT_CODE at $(date) ===" >> "$LOG_FILE"
exit $EXIT_CODE
