"""
BrickDeck Module: Flipper Zero Controller & Display
Communicates via USB Serial or Bluetooth with Flipper Zero over Protobuf RPC.
"""

import os
import sys
import time
import glob
import serial
from typing import Optional

from core.module_base import BaseModule
from core.theme import (
    COLOR_FLIPPER_AMBER, COLOR_PANEL_BG, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_STATUS_OK, COLOR_STATUS_ERR
)
from PIL import Image

# Import Flipper RPC helper from existing Apps/BrickFlipper
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "BrickFlipper")))
try:
    from flipper_proto import (
        FlipperClient, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_BACK,
        TYPE_PRESS, TYPE_RELEASE, TYPE_SHORT
    )
except ImportError:
    FlipperClient = None


class FlipperModule(BaseModule):
    name = "Flipper Zero"
    short_name = "Flipper"
    icon = "🐬"
    accent_color = COLOR_FLIPPER_AMBER

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.client: Optional[FlipperClient] = None
        self.connected = False
        self.last_frame: Optional[bytes] = None
        self.status_msg = "Rozlaczono"
        self.reconnect_cooldown = 0

    def on_load(self):
        if FlipperClient:
            self.client = FlipperClient(timeout=0.2)

    def on_activate(self):
        super().on_activate()
        if self.client and not self.connected:
            self._try_connect()

    def on_deactivate(self):
        super().on_deactivate()

    def _try_connect(self):
        if not self.client:
            return
        self.status_msg = "Laczenie z Flipperem..."
        if self.client.connect():
            self.connected = True
            self.status_msg = "Polaczono (USB / RPC)"
            self.client.start_screen_stream()
        else:
            self.connected = False
            self.status_msg = "Nie wykryto Flippera (/dev/ttyACM*)"

    def get_hotkey_hints(self):
        if self.connected:
            return [
                ("L1/R1", "Moduly"),
                ("D-Pad", "Krzyzak F0"),
                ("A", "OK"),
                ("B", "Wroc"),
                ("X", "Rozlacz")
            ]
        else:
            return [
                ("L1/R1", "Moduly"),
                ("A", "Polacz ponownie"),
                ("B", "Menu")
            ]

    def update(self, dt: float):
        if self.connected and self.client:
            frame = self.client.read_screen_frame(timeout_sec=0.02)
            if frame:
                self.last_frame = frame

    def render(self, canvas):
        # Draw main panel card
        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title="FLIPPER ZERO COMPANION",
            subtitle=self.status_msg,
            border_color=COLOR_FLIPPER_AMBER
        )

        if self.connected and self.last_frame and len(self.last_frame) >= 1024:
            # Render Flipper 128x64 display with 6x integer scaling (768 x 384 px)
            scale = 6
            disp_w = 128 * scale  # 768 px
            disp_h = 64 * scale   # 384 px
            disp_x = 32 + (960 - disp_w) // 2
            disp_y = 130

            # Outer amber LCD border
            canvas.draw.rounded_rectangle(
                [(disp_x - 12, disp_y - 12), (disp_x + disp_w + 12, disp_y + disp_h + 12)],
                radius=14,
                fill=(24, 18, 12),
                outline=COLOR_FLIPPER_AMBER,
                width=3
            )

            # Build 128x64 image
            flipper_img = Image.new("RGBA", (128, 64), (255, 138, 0, 255))
            f_draw = flipper_img.load()

            for fy in range(64):
                page = fy >> 3
                bit = fy & 7
                page_off = page * 128
                for fx in range(128):
                    pixel = (self.last_frame[page_off + fx] >> bit) & 1
                    if pixel:
                        f_draw[fx, fy] = (30, 20, 10, 255)  # Dark LCD ink
                    else:
                        f_draw[fx, fy] = (255, 138, 0, 255) # Amber backlight

            # Scale up with nearest neighbor for pixel-perfect sharpness
            scaled_disp = flipper_img.resize((disp_w, disp_h), Image.NEAREST)
            canvas.image.paste(scaled_disp, (disp_x, disp_y))

            # Helper status under LCD
            font = canvas.draw.getfont()
            canvas.draw.text((disp_x, disp_y + disp_h + 30),
                             "Sterowanie z konsolki: [Krzyzak]: Nawigacja | [A]: OK | [B]: Wstecz",
                             fill=COLOR_TEXT_SECONDARY, font=font)
        else:
            # Disconnected View
            cx = 32 + 960 // 2
            cy = 66 + 634 // 2
            canvas.draw.text((cx - 180, cy - 60), "FLIPPER ZERO ROZLACZONY",
                             fill=COLOR_FLIPPER_AMBER, font=canvas.draw.getfont())
            canvas.draw.text((cx - 240, cy - 20),
                             "Podlacz Flippera kablem USB-C do konsoli lub uruchom symulator.",
                             fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
            canvas.draw_badge(cx - 80, cy + 30, "[A] Skanuj i Polacz",
                              bg_color=(48, 56, 72), text_color=COLOR_FLIPPER_AMBER)

    def handle_input(self, event: str) -> bool:
        if not self.connected:
            if event == "BTN_A":
                self._try_connect()
                return True
            return False

        if not self.client:
            return False

        # Map events directly to Flipper keys
        key_map = {
            "UP": KEY_UP,
            "DOWN": KEY_DOWN,
            "LEFT": KEY_LEFT,
            "RIGHT": KEY_RIGHT,
            "BTN_A": KEY_OK,
            "BTN_B": KEY_BACK,
        }

        if event in key_map:
            self.client.send_short_click(key_map[event])
            return True
        elif event == "BTN_X":
            if self.client:
                self.client.close()
            self.connected = False
            self.status_msg = "Rozlaczono przez uzytkownika"
            return True

        return False
