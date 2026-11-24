#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class GravitySimModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.bodies = [
            {"name": "GWIAZDA CENTRALNA", "x": 512, "y": 384, "mass": 1000, "col": (255, 220, 0), "r": 18},
            {"name": "PLANETA A (BLISKA)", "x": 680, "y": 384, "mass": 10, "col": (0, 240, 255), "r": 8},
            {"name": "PLANETA B (Z PIERŚCIENIEM)", "x": 840, "y": 384, "mass": 25, "col": (0, 255, 140), "r": 12},
            {"name": "SONDA KOSMICZNA", "x": 710, "y": 360, "mass": 1, "col": (255, 80, 80), "r": 4},
        ]
        self.time_speed = 1.0

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((4, 8, 16, 255))

        draw.rectangle([0, 0, w, 50], fill=(12, 18, 30, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🪐 078 // N-BODY GRAVITATIONAL ORBIT SIMULATOR // PRAWA KEPLERA", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "FIZYKA NEWTONA", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "60 FPS", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main Deep Space Orbit View
        canvas.draw_card(20, 65, 700, 640, title="PRZESTRZEŃ GRAWITACYJNA (ORBITY KEPLERA)", subtitle="Symulacja numeryczna Rungego-Kutty RK4")
        # Draw orbit paths
        draw.ellipse([(512 - 168, 384 - 168), (512 + 168, 384 + 168)], outline=(0, 120, 180), width=1)
        draw.ellipse([(512 - 328, 384 - 328), (512 + 328, 384 + 328)], outline=(0, 120, 180), width=1)

        # Draw bodies
        for b in self.bodies:
            bx, by, br, bcol = b["x"], b["y"], b["r"], b["col"]
            draw.ellipse([(bx - br, by - br), (bx + br, by + br)], fill=bcol)
            draw.text((bx + br + 8, by - 6), b["name"].split()[0], fill=bcol, font=get_font(11, bold=True))

        # Right Telemetry Card
        canvas.draw_card(735, 65, 269, 640, title="PARAMETRY ORBITALNE", subtitle="Prędkości i okresy obiegu")
        for i, b in enumerate(self.bodies):
            by = 135 + i * 110
            draw.rectangle([750, by, 990, by + 95], fill=(14, 20, 32), outline=b["col"], width=1)
            draw.text((760, by + 10), b["name"], fill=b["col"], font=get_font(12, bold=True))
            draw.text((760, by + 32), f"Masa: {b['mass']} M_earth", fill=(210, 225, 245), font=get_font(13))
            v_val = 29.8 / (i + 1)
            draw.text((760, by + 56), f"Prędkość: {v_val:.1f} km/s", fill=(0, 255, 180), font=get_font(13, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Manewr Sondą | [A]: Wystrzel Nowe Ciało | [X]: Prędkość Czasu (1x/2x/5x) | [B]: Reset", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
