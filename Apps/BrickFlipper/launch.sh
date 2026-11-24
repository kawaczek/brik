#!/bin/sh
# ==============================================================================
# BrickFlipper Launcher for TrimUI Brick
# ==============================================================================

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR" || exit 1

LOG_FILE="$APP_DIR/brickflipper.log"
echo "=== Starting BrickFlipper $(date) ===" > "$LOG_FILE"

# Setup library paths in case bundled dependencies exist
export LD_LIBRARY_PATH="$APP_DIR/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$APP_DIR:$PYTHONPATH"

# Find suitable Python 3 binary
PYTHON=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif [ -f "/mnt/SDCARD/System/bin/python3" ]; then
    PYTHON="/mnt/SDCARD/System/bin/python3"
elif [ -f "/usr/bin/python3" ]; then
    PYTHON="/usr/bin/python3"
elif [ -f "$APP_DIR/python/bin/python3" ]; then
    PYTHON="$APP_DIR/python/bin/python3"
fi

if [ -z "$PYTHON" ]; then
    echo "ERROR: python3 interpreter not found!" >> "$LOG_FILE"
    echo "Please ensure Python 3 is installed or available in firmware." >> "$LOG_FILE"
    exit 1
fi

echo "Using Python: $PYTHON" >> "$LOG_FILE"
echo "Checking for Flipper Zero on USB..." >> "$LOG_FILE"

# Run BrickFlipper in Framebuffer mode
$PYTHON "$APP_DIR/brickflipper.py" --mode fb >> "$LOG_FILE" 2>&1

EXIT_CODE=$?
echo "=== BrickFlipper exited with code $EXIT_CODE at $(date) ===" >> "$LOG_FILE"
exit $EXIT_CODE
