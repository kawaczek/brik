#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class BallisticsModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.caliber = ".308 WINCHESTER (7.62x51mm)"
        self.v0_ms = 820.0
        self.bullet_weight_g = 10.9 # 168 gr
        self.bc_g1 = 0.462
        self.zero_distance_m = 100.0

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 30, 255), outline=(255, 140, 0, 100), width=1)
        draw.text((20, 14), f"🎯 066 // BALLISTICS LAB & TRAJECTORY SIMULATOR // {self.caliber}", fill=(255, 140, 0), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"ZERO: {self.zero_distance_m:.0f} M", bg_color=(40, 30, 15))
        canvas.draw_badge(w - 85, 12, "BC 0.462", bg_color=(20, 45, 65))

        # Ballistic Table Card
        canvas.draw_card(20, 65, 984, 440, title="TABELA BALISTYCZNA OPADU POCISKU (BULLET DROP)", subtitle="Poprawki celownika w MIL / MOA oraz energia kinetyczna w dżulach (J)")
        headers = ["DYSTANS (M)", "CZAS LOTU (S)", "PRĘDKOŚĆ (M/S)", "OPAD (CM)", "POPRAWKA MIL", "POPRAWKA MOA", "ENERGIA (J)"]
        for c, h_text in enumerate(headers):
            draw.text((45 + c * 136, 125), h_text, fill=(255, 170, 0), font=get_font(12, bold=True))

        rows = [
            ("50 m", "0.06 s", "792 m/s", "+1.2 cm", "-0.2 MIL", "-0.8 MOA", "3420 J"),
            ("100 m", "0.13 s", "764 m/s", " 0.0 cm", " 0.0 MIL", " 0.0 MOA", "3180 J"),
            ("200 m", "0.27 s", "711 m/s", "-11.8 cm", "+0.6 MIL", "+2.0 MOA", "2750 J"),
            ("300 m", "0.42 s", "659 m/s", "-42.4 cm", "+1.4 MIL", "+4.9 MOA", "2370 J"),
            ("500 m", "0.76 s", "561 m/s", "-172.5 cm", "+3.5 MIL", "+11.9 MOA", "1710 J"),
            ("800 m", "1.39 s", "428 m/s", "-612.0 cm", "+7.7 MIL", "+26.3 MOA", "1000 J"),
        ]
        for r, row in enumerate(rows):
            ry = 165 + r * 50
            draw.rectangle([35, ry - 6, 990, ry + 36], fill=(16, 22, 34) if r % 2 == 0 else (12, 16, 26))
            for c, val in enumerate(row):
                col = (0, 255, 180) if "MIL" in headers[c] else (240, 245, 255)
                draw.text((45 + c * 136, ry + 6), val, fill=col, font=get_font(14, bold=(c==0 or "MIL" in headers[c])))

        # Bottom Wind Deflection Card
        canvas.draw_card(20, 520, 984, 190, title="ZNOSZENIE PRZEZ WIATR BOCZNY (CROSSWIND DEFLECTION)", subtitle="Wiatr 4 m/s (pod kątem 90°)")
        draw.text((45, 580), "Znoszenie na 300 m: 18.4 cm (0.6 MIL) | Znoszenie na 500 m: 58.2 cm (1.2 MIL)", fill=(0, 255, 180), font=get_font(16, bold=True))
        draw.text((45, 615), "Przejście w zakres transoniczny: dystans 890 m (prędkość spada do 340 m/s)", fill=(255, 180, 0), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Dystanse | [A]: Zmień Kaliber (.223 / .308 / 6.5 CM) | [Y]: Wiatr", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
