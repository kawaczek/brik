#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class WireframeRaceModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.speed_kmh = 248
        self.score = 8420
        self.time_left = 42.5
        self.car_x = 512

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 4, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(20, 8, 32, 255), outline=(255, 0, 180, 100), width=1)
        draw.text((20, 14), "🏎️ 084 // SYNTHWAVE VECTOR HIGHWAY 3D // OUTRUN RETRO RACE", fill=(255, 0, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"{self.speed_kmh} KM/H", bg_color=(60, 10, 40), text_color=(255, 0, 180))
        canvas.draw_badge(w - 80, 12, f"{self.time_left:.1f}S", bg_color=(20, 50, 40), text_color=(0, 255, 136))

        # Main 3D Vector Highway Perspective
        canvas.draw_card(20, 65, 984, 640, title="NEONOWA TRASA WEKTOROWA (PSEUDO-3D)", subtitle="Wymijaj cyber-samochody D-Padem, zbieraj punkty kontrolne")
        horizon_y = 320
        # Draw perspective road lines
        draw.line([(512, horizon_y), (40, 680)], fill=(0, 240, 255), width=3)
        draw.line([(512, horizon_y), (984, 680)], fill=(0, 240, 255), width=3)
        draw.line([(512, horizon_y), (512, 680)], fill=(255, 220, 0), width=2) # Center line

        # Big Retro Neon Sun on horizon
        draw.ellipse([(512 - 70, horizon_y - 70), (512 + 70, horizon_y + 70)], fill=(255, 60, 120))
        for gy in range(horizon_y - 50, horizon_y + 50, 14):
            draw.line([(512 - 68, gy), (512 + 68, gy)], fill=(10, 4, 20), width=3)

        # Player Car (Wireframe Vector Style)
        cx = self.car_x
        draw.rectangle([cx - 50, 580, cx + 50, 640], fill=(255, 0, 128), outline=(0, 255, 255), width=2)
        draw.rectangle([cx - 35, 595, cx + 35, 620], fill=(10, 20, 40))
        # Tail lights
        draw.rectangle([cx - 45, 625, cx - 25, 635], fill=(255, 0, 0))
        draw.rectangle([cx + 25, 625, cx + 45, 635], fill=(255, 0, 0))

        draw.rectangle([0, 724, w, 768], fill=(16, 8, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Sterowanie Autem | [A]: Przyspieszenie (Nitro) | [B]: Hamulec", fill=(255, 150, 220), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
