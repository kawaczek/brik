#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class LaserOpticsModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.level = 4
        self.score = 2400
        self.lasers = [((80, 240), (450, 240), (450, 520), (840, 520))]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((6, 12, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), f"🪞 085 // LASER MATRIX & OPTICS LAB // POZIOM {self.level}", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"PUNKTY: {self.score}", bg_color=(20, 50, 40))
        canvas.draw_badge(w - 85, 12, "POZIOM 4", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main Laser Grid
        canvas.draw_card(20, 65, 984, 640, title="LABIRYNT OPTYCZNY (ZWIERCIADŁA I PRYZMATY)", subtitle="Ustaw kąty luster, aby doprowadzić promień lasera do sensora docelowego")
        # Draw laser path
        draw.line([(80, 240), (450, 240)], fill=(0, 255, 136), width=4)
        draw.line([(450, 240), (450, 520)], fill=(0, 255, 136), width=4)
        draw.line([(450, 520), (840, 520)], fill=(0, 255, 136), width=4)

        # Mirrors
        draw.line([(430, 220), (470, 260)], fill=(255, 255, 255), width=6) # Mirror 1
        draw.line([(430, 540), (470, 500)], fill=(255, 255, 255), width=6) # Mirror 2

        # Target receptor
        draw.ellipse([(830, 510), (850, 530)], fill=(255, 220, 0), outline=(255, 0, 80), width=3)
        draw.text((865, 512), "CEL AKTYWNY (100%)", fill=(255, 220, 0), font=get_font(14, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Zwierciadło | [A]: Obróć Zwierciadło o 45° | [X]: Dodaj Pryzmat RGB | [B]: Reset Poziomu", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
