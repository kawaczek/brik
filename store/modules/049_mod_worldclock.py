#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class WorldClockModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.cities = [
            ("WARSZAWA (CET)", "17:25", "UTC+1", True),
            ("LONDYN (GMT)", "16:25", "UTC+0", True),
            ("NOWY JORK (EST)", "11:25", "UTC-5", True),
            ("SAN FRANCISCO (PST)", "08:25", "UTC-8", True),
            ("TOKIO (JST)", "01:25", "UTC+9", False),
            ("SYDNEY (AEST)", "03:25", "UTC+11", False),
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🌐 049 // WORLD CLOCK & SOLAR TERMINATOR (KRZYWA SŁONECZNA)", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 180, 12, "TERMINATOR: ON", bg_color=(20, 40, 60))

        # World Map with Day/Night simulation
        canvas.draw_card(20, 65, 984, 380, title="GLOBALNA MAPA DZIENNA / NOCNA", subtitle="Krzywa Solar Terminator wyliczana z bieżącej deklinacji Słońca")
        mx, my, mw, mh = 40, 115, 944, 310
        draw.rectangle([mx, my, mx + mw, my + mh], fill=(12, 25, 45), outline=(0, 180, 240))
        # Draw continents outline mock & solar night curve
        for x in range(0, mw, 8):
            rad = (x / mw) * 2 * math.pi
            night_y = my + mh / 2 + math.sin(rad) * 90
            draw.rectangle([mx + x, int(night_y), mx + x + 8, my + mh], fill=(6, 12, 22))
        draw.text((mx + 20, my + 20), "DZIEŃ [SŁOŃCE]", fill=(255, 220, 0), font=get_font(13, bold=True))
        draw.text((mx + mw - 140, my + mh - 30), "NOC [CIEŃ ZIEMI]", fill=(100, 130, 170), font=get_font(13))

        # City Clocks Grid
        canvas.draw_card(20, 460, 984, 250, title="STREFY CZASOWE I SESJE GIEŁDOWE", subtitle="Czas lokalny na świecie")
        for i, (name, clock, utc, is_day) in enumerate(self.cities):
            col = i % 3
            row = i // 3
            cx = 40 + col * 320
            cy = 515 + row * 95
            draw.rectangle([cx, cy, cx + 300, cy + 80], fill=(18, 26, 40), outline=(0, 200, 255) if is_day else (40, 60, 85))
            draw.text((cx + 14, cy + 12), name, fill=(220, 235, 255), font=get_font(13, bold=True))
            draw.text((cx + 14, cy + 34), clock, fill=(255, 220, 0) if is_day else (140, 170, 210), font=get_font(26, bold=True))
            draw.text((cx + 180, cy + 42), utc, fill=(100, 130, 160), font=get_font(13))
            icon = "☀️ DZIEŃ" if is_day else "🌙 NOC"
            draw.text((cx + 225, cy + 14), icon, fill=(255, 170, 0) if is_day else (100, 140, 200), font=get_font(11, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Strefy | [A]: Dodaj Miasto | [X]: Format 12h/24h", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
