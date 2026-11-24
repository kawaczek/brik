#!/bin/sh
# ==============================================================================
# Bluetooth PAN Connection Helper for Pwngotchi on TrimUI Brick
# ==============================================================================

SETTINGS_FILE="$(dirname "$0")/settings.json"
PWNGOTCHI_MAC=""

if [ -n "$1" ]; then
    PWNGOTCHI_MAC="$1"
elif [ -f "$SETTINGS_FILE" ]; then
    PWNGOTCHI_MAC=$(grep -o '"bt_mac": *"[^"]*"' "$SETTINGS_FILE" | cut -d'"' -f4)
fi

echo "=== Pwngotchi Bluetooth Setup ==="
if [ -z "$PWNGOTCHI_MAC" ]; then
    echo "UWAGA: Nie podano adresu MAC Pwngotchi!"
    echo "Uzycie: ./bt_setup.sh XX:XX:XX:XX:XX:XX"
    echo "Mozesz tez wpisac adres MAC w pliku settings.json."
    echo ""
    echo "Skanowanie w poszukiwaniu urzadzen Bluetooth..."
    if command -v bluetoothctl >/dev/null 2>&1; then
        bluetoothctl scan on &
        SCAN_PID=$!
        sleep 5
        kill $SCAN_PID 2>/dev/null
        bluetoothctl devices
    fi
    exit 1
fi

echo "Laczenie z Pwngotchi: $PWNGOTCHI_MAC przez Bluetooth PAN..."

# Ensure Bluetooth interface is UP
rfkill unblock bluetooth 2>/dev/null
hciconfig hci0 up 2>/dev/null

# Try pairing / trusting via bluetoothctl
if command -v bluetoothctl >/dev/null 2>&1; then
    echo "Parowanie z $PWNGOTCHI_MAC..."
    bluetoothctl trust "$PWNGOTCHI_MAC" 2>/dev/null
    bluetoothctl pair "$PWNGOTCHI_MAC" 2>/dev/null
    bluetoothctl connect "$PWNGOTCHI_MAC" 2>/dev/null
fi

# Try establishing BNEP (Bluetooth Network Encapsulation Protocol)
if command -v bt-pan >/dev/null 2>&1; then
    bt-pan client "$PWNGOTCHI_MAC" &
elif command -v pand >/dev/null 2>&1; then
    pand --connect "$PWNGOTCHI_MAC" --service PANU --autorange &
fi

sleep 2

# Check if bnep0 interface appeared
if ifconfig bnep0 >/dev/null 2>&1; then
    echo "[OK] Interfejs bnep0 powstal!"
    echo "Konfiguracja adresu IP dla bnep0..."
    ifconfig bnep0 192.168.44.1 netmask 255.255.255.0 up 2>/dev/null
    echo "Gotowe! Pwngotchi powinno byc osiagalne pod http://192.168.44.44:8080"
else
    echo "[!] Interfejs bnep0 nie powstal automatycznie."
    echo "Upewnij sie, ze w config.toml Pwngotchi masz wlaczony plugin bt-tether!"
fi
