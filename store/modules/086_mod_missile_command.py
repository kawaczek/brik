#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class MissileCommandModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.score = 4850
        self.cities_left = 4
        self.missiles_ammo = 18
        self.target_x = 512
        self.target_y = 350

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 10, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(255, 80, 80, 100), width=1)
        draw.text((20, 14), "🚀 086 // CYBER DEFENSE MISSILE INTERCEPTOR // ARCADE DEFENSE", fill=(255, 80, 80), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"PUNKTY: {self.score}", bg_color=(50, 15, 20))
        canvas.draw_badge(w - 85, 12, f"RAKIETY: {self.missiles_ammo}", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main Combat Theater Card
        canvas.draw_card(20, 65, 984, 640, title="TEATR DZIAŁAŃ OBRONY PRZECIWRAKIETOWEJ", subtitle="Celuj D-Padem, wystrzeliwuj wybuchy kasetowe klawiszem [A]")
        
        # Enemy incoming ballistic streaks
        draw.line([(150, 120), (320, 600)], fill=(255, 60, 60), width=2)
        draw.line([(550, 120), (480, 600)], fill=(255, 60, 60), width=2)
        draw.line([(850, 120), (750, 600)], fill=(255, 60, 60), width=2)

        # Flak explosion
        draw.ellipse([(self.target_x - 40, self.target_y - 40), (self.target_x + 40, self.target_y + 40)], outline=(0, 255, 200), width=3)
        draw.text((self.target_x - 30, self.target_y - 10), "WYBUCH FLAK", fill=(0, 255, 200), font=get_font(12, bold=True))

        # Ground and 6 Cities to protect
        draw.rectangle([40, 620, 980, 660], fill=(20, 40, 30))
        for c in range(6):
            cx = 120 + c * 140
            draw.rectangle([cx, 595, cx + 50, 620], fill=(0, 200, 255))
            draw.text((cx + 10, 600), "MIASTO", fill=(10, 20, 30), font=get_font(10, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Ruch Celownikiem | [A]: Ognia Bateria Środkowa | [L1/R1]: Bateria Lewa / Prawa", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
