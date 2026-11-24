"""
BrickDeck Module: Pwngotchi Live Display & Companion
Connects to Pwngotchi over Bluetooth/Wi-Fi/USB and renders live UI with themes.
"""

import io
import time
import urllib.request
from typing import Optional
from PIL import Image

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_PANEL_BG, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY
)

THEMES = [
    ("classic", "E-Paper B&W", (245, 245, 245), (20, 20, 20)),
    ("cyberpunk", "Neon Cyber", (14, 18, 24), (0, 216, 255)),
    ("amber", "Retro Amber", (24, 16, 10), (255, 138, 0)),
    ("matrix", "Matrix Green", (8, 16, 8), (57, 211, 83)),
]


class PwngotchiModule(BaseModule):
    name = "Pwngotchi Companion"
    short_name = "Pwngotchi"
    icon = "👻"
    accent_color = COLOR_CYBER_CYAN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.target_ips = ["192.168.44.44", "10.0.0.2", "pwngotchi.local", "127.0.0.1"]
        self.port = 8080
        self.active_ip = "192.168.44.44"
        self.connected = False
        self.theme_idx = 1  # Default to Cyberpunk Neon
        self.last_fetch_time = 0
        self.refresh_interval = 1.0
        self.current_png_bytes: Optional[bytes] = None

    def get_hotkey_hints(self):
        return [
            ("L1/R1", "Moduly"),
            ("X", "Zmien Motyw"),
            ("Y", "Zmien IP"),
            ("A", "Odswiez teraz")
        ]

    def _fetch_frame(self):
        urls = [f"http://{self.active_ip}:{self.port}/ui"]
        for ip in self.target_ips:
            if ip != self.active_ip:
                urls.append(f"http://{ip}:{self.port}/ui")

        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "BrickDeck/1.0"})
                with urllib.request.urlopen(req, timeout=0.8) as resp:
                    if resp.status == 200:
                        data = resp.read()
                        if len(data) > 100 and data[:8] == b"\x89PNG\r\n\x1a\n":
                            host = url.split("://")[1].split(":")[0]
                            self.active_ip = host
                            self.connected = True
                            self.current_png_bytes = data
                            return
            except Exception:
                continue
        self.connected = False

    def update(self, dt: float):
        now = time.time()
        if now - self.last_fetch_time >= self.refresh_interval:
            self._fetch_frame()
            self.last_fetch_time = now

    def render(self, canvas):
        theme_key, theme_name, bg_col, fg_col = THEMES[self.theme_idx]

        status = f"IP: {self.active_ip}  |  Motyw: {theme_name}" if self.connected else "Oczekiwanie na polaczenie z Pwngotchi..."
        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title="PWNGOTCHI LIVE DASHBOARD",
            subtitle=status,
            border_color=self.accent_color
        )

        if self.current_png_bytes:
            try:
                img = Image.open(io.BytesIO(self.current_png_bytes)).convert("L")
                orig_w, orig_h = img.size

                # Target viewport in card: width 800, height 400
                scale = min(800 / orig_w, 420 / orig_h)
                nw = int(orig_w * scale)
                nh = int(orig_h * scale)

                resized = img.resize((nw, nh), Image.NEAREST)
                raw_bytes = resized.tobytes()

                # Build colored image
                themed_img = Image.new("RGBA", (nw, nh), bg_col + (255,))
                t_draw = themed_img.load()

                for y in range(nh):
                    for x in range(nw):
                        val = raw_bytes[y * nw + x]
                        # Invert: dark ink on light background
                        if val < 128:
                            t_draw[x, y] = fg_col + (255,)
                        else:
                            t_draw[x, y] = bg_col + (255,)

                # Center on card
                cx = 32 + (960 - nw) // 2
                cy = 130 + (440 - nh) // 2

                # Frame around e-paper
                canvas.draw.rounded_rectangle(
                    [(cx - 10, cy - 10), (cx + nw + 10, cy + nh + 10)],
                    radius=12,
                    fill=(20, 24, 32),
                    outline=fg_col,
                    width=2
                )

                canvas.image.paste(themed_img, (cx, cy))
            except Exception:
                pass
        else:
            cx = 32 + 960 // 2
            cy = 66 + 634 // 2
            canvas.draw.text((cx - 160, cy - 40), "(◕‿‿◕) PWNGOTCHI",
                             fill=COLOR_CYBER_CYAN, font=canvas.draw.getfont())
            canvas.draw.text((cx - 240, cy),
                             "Polacz przez Bluetooth PAN (192.168.44.44) lub USB (10.0.0.2).",
                             fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
            canvas.draw_badge(cx - 80, cy + 40, "[A] Skanuj IP",
                              bg_color=(36, 44, 60), text_color=COLOR_CYBER_CYAN)

    def handle_input(self, event: str) -> bool:
        if event == "BTN_X":
            self.theme_idx = (self.theme_idx + 1) % len(THEMES)
            return True
        elif event == "BTN_Y":
            # Cycle target IP
            cur_idx = self.target_ips.index(self.active_ip) if self.active_ip in self.target_ips else 0
            self.active_ip = self.target_ips[(cur_idx + 1) % len(self.target_ips)]
            self._fetch_frame()
            return True
        elif event == "BTN_A":
            self._fetch_frame()
            return True
        return False
