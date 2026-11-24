#!/bin/sh
# ==============================================================================
# Brickgotchi Launcher for TrimUI Brick
# ==============================================================================

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR" || exit 1

LOG_FILE="$APP_DIR/brickgotchi.log"
echo "=== Starting Brickgotchi $(date) ===" > "$LOG_FILE"

export LD_LIBRARY_PATH="$APP_DIR/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$APP_DIR:$PYTHONPATH"

# Run Bluetooth setup in background if configured
if [ -f "$APP_DIR/bt_setup.sh" ]; then
    sh "$APP_DIR/bt_setup.sh" >> "$LOG_FILE" 2>&1 &
fi

# Find python interpreter
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

# Run in Framebuffer mode
$PYTHON "$APP_DIR/brickgotchi.py" --mode fb >> "$LOG_FILE" 2>&1

EXIT_CODE=$?
echo "=== Brickgotchi stopped with code $EXIT_CODE at $(date) ===" >> "$LOG_FILE"
exit $EXIT_CODE
