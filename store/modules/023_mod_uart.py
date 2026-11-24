"""
BrickDeck Module: Hardware UART / Serial Terminal
Connects to microcontrollers (ESP32, Arduino, Pi UART) via USB-C OTG adapters.
"""

import glob
import time
from typing import List, Optional
import serial

from core.module_base import BaseModule
from core.theme import (
    COLOR_WARNING_YELLOW, COLOR_PANEL_BG, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_STATUS_OK
)

BAUD_RATES = [9600, 19200, 38400, 57600, 115200, 230400]


class UartModule(BaseModule):
    name = "UART Serial Monitor"
    short_name = "UART"
    icon = "🔌"
    accent_color = COLOR_WARNING_YELLOW

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.baud_idx = 4  # Default to 115200
        self.port = "/dev/ttyUSB0"
        self.connected = False
        self.ser: Optional[serial.Serial] = None
        self.log_lines: List[str] = [
            "[BrickDeck UART] Gotowy do pracy. Podlacz przejsciowke USB-UART.",
            "[INFO] Obslugiwane uklady: FTDI, CH340, CP2102, PL2303.",
            "[HINT] Strzalki Lewo/Prawo: Zmiana Baudrate | [A]: Otworz Port.",
        ]
        self._init_mock_stream()

    def _init_mock_stream(self):
        """Add sample boot logs for visual inspection when no physical device is attached."""
        self.log_lines.extend([
            "[0.000] ESP-ROM: esp32s3-20210327",
            "[0.004] Build: Mar 27 2021",
            "[0.008] rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)",
            "[0.012] SPIWP:0xee",
            "[0.016] mode:DIO, clock div:1",
            "[0.020] load:0x3fce3808,len:0x1730",
            "[0.035] entry 0x403c98a0",
            "[0.112] I (28) boot: ESP-IDF v5.1-dev-2234-g9e28f3 2nd stage bootloader",
            "[0.118] I (32) boot: chip revision: v0.1",
            "[0.124] I (36) boot.esp32s3: Boot loaded at 0x40378000",
            "[0.130] I (41) cpu_start: Pro cpu up.",
            "[0.240] I (150) main_app: Initializing Wi-Fi stack & BLE stack...",
            "[0.480] I (390) main_app: Hardware ready. Entering main loop.",
        ])

    def get_hotkey_hints(self):
        return [
            ("L1/R1", "Moduly"),
            ("Lewo/Prawo", "Baudrate"),
            ("A", "Polacz / Rozlacz" if not self.connected else "Rozlacz"),
            ("X", "Wyczysc ekran")
        ]

    def _scan_ports(self) -> List[str]:
        return sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))

    def update(self, dt: float):
        if self.connected and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    raw = self.ser.read(self.ser.in_waiting).decode("utf-8", errors="replace")
                    for line in raw.split("\n"):
                        if line:
                            self.log_lines.append(line.strip("\r"))
                            if len(self.log_lines) > 200:
                                self.log_lines.pop(0)
            except Exception:
                pass

    def render(self, canvas):
        baud = BAUD_RATES[self.baud_idx]
        status = f"Port: {self.port}  |  Baudrate: {baud} 8-N-1"
        if self.connected:
            status += "  |  STAN: POLACZONO"

        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title="KIESZONKOWY TERMINAL SZEREGOWY (UART)",
            subtitle=status,
            border_color=self.accent_color
        )

        # Control Bar (Baud rate pills)
        canvas.draw.text((60, 118), "PREDKOSC (BAUDRATE):", fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
        bx = 240
        for idx, b_val in enumerate(BAUD_RATES):
            is_active = (idx == self.baud_idx)
            pill_w = 78
            if is_active:
                canvas.draw.rounded_rectangle(
                    [(bx, 114), (bx + pill_w, 138)],
                    radius=6, fill=(54, 46, 20), outline=COLOR_WARNING_YELLOW, width=2
                )
                canvas.draw.text((bx + 10, 119), str(b_val), fill=COLOR_WARNING_YELLOW, font=canvas.draw.getfont())
            else:
                canvas.draw.rounded_rectangle(
                    [(bx, 114), (bx + pill_w, 138)],
                    radius=6, fill=(24, 28, 36)
                )
                canvas.draw.text((bx + 10, 119), str(b_val), fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
            bx += pill_w + 10

        # Console Box (x=60, y=156, w=904, h=524)
        con_x = 60
        con_y = 156
        con_w = 904
        con_h = 524
        canvas.draw.rounded_rectangle(
            [(con_x, con_y), (con_x + con_w, con_y + con_h)],
            radius=8, fill=(10, 14, 18), outline=COLOR_BORDER, width=1
        )

        # Draw terminal lines (last 23 lines)
        visible_lines = self.log_lines[-22:]
        line_y = con_y + 14
        font = canvas.draw.getfont()
        for l in visible_lines:
            col = COLOR_WARNING_YELLOW if l.startswith("[") else COLOR_TEXT_PRIMARY
            canvas.draw.text((con_x + 16, line_y), l, fill=col, font=font)
            line_y += 22

    def handle_input(self, event: str) -> bool:
        if event == "LEFT":
            self.baud_idx = (self.baud_idx - 1) % len(BAUD_RATES)
            return True
        elif event == "RIGHT":
            self.baud_idx = (self.baud_idx + 1) % len(BAUD_RATES)
            return True
        elif event == "BTN_X":
            self.log_lines = ["[INFO] Ekran wyczyszczony."]
            return True
        elif event == "BTN_A":
            ports = self._scan_ports()
            if ports:
                self.port = ports[0]
                self.connected = not self.connected
                self.log_lines.append(f"[INFO] Przelaczono polaczenie {self.port}: {'Polaczono' if self.connected else 'Rozlaczono'}")
            else:
                self.log_lines.append("[!] Nie znaleziono aktywnego portu /dev/ttyUSB* ani /dev/ttyACM*")
            return True
        return False
