#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import random
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class PinballModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.ball_x = 480.0
        self.ball_y = 350.0
        self.vx = 2.4
        self.vy = 4.2
        self.left_flipper_up = False
        self.right_flipper_up = False
        self.score = 284500
        self.multiplier = 3
        self.bumpers = [
            {"x": 420, "y": 240, "r": 35, "color": (255, 0, 128)},
            {"x": 580, "y": 240, "r": 35, "color": (0, 240, 255)},
            {"x": 500, "y": 340, "r": 30, "color": (255, 210, 0)}
        ]

    def get_hotkey_hints(self):
        return [
            {"key": "L1", "desc": "Lewy flipper"},
            {"key": "R1", "desc": "Prawy flipper"},
            {"key": "A", "desc": "Naciąg wyrzutni"},
            {"key": "X", "desc": "Nowa bila"}
        ]

    def update(self, dt: float):
        self.vy += 0.15 # gravity
        self.ball_x += self.vx
        self.ball_y += self.vy

        # Walls
        if self.ball_x <= 280:
            self.ball_x = 280
            self.vx = abs(self.vx) * 0.95
        elif self.ball_x >= 740:
            self.ball_x = 740
            self.vx = -abs(self.vx) * 0.95
        if self.ball_y <= 120:
            self.ball_y = 120
            self.vy = abs(self.vy) * 0.95
        elif self.ball_y >= 680:
            # Drain
            self.ball_x = 720
            self.ball_y = 580
            self.vx = -1.5
            self.vy = -8.0

        # Bumpers collision
        for b in self.bumpers:
            dist = math.hypot(self.ball_x - b["x"], self.ball_y - b["y"])
            if dist < b["r"] + 8:
                angle = math.atan2(self.ball_y - b["y"], self.ball_x - b["x"])
                self.vx = math.cos(angle) * 7.5
                self.vy = math.sin(angle) * 7.5
                self.score += 1000 * self.multiplier

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🕹️ NEON CYBER PINBALL // MATRIX TABLE",
                         subtitle=f"Punkty: {self.score:,} | Mnożnik: x{self.multiplier} | Stan: W GRZE",
                         border_color=(255, 0, 180))

        # Pinball Cabinet Area (Center)
        cx1, cx2 = 260, 760
        draw.rounded_rectangle([cx1, 105, cx2, 680], radius=16, fill=(10, 14, 22), outline=(255, 0, 140), width=3)

        # Neon Ramps & Guides
        draw.line([(cx1 + 40, 180), (cx1 + 40, 520)], fill=(0, 200, 255), width=2)
        draw.line([(cx2 - 40, 180), (cx2 - 40, 520)], fill=(0, 200, 255), width=2)
        draw.arc([cx1 + 40, 110, cx2 - 40, 250], start=180, end=0, fill=(0, 255, 180), width=3)

        # Bumpers
        for b in self.bumpers:
            draw.ellipse([b["x"] - b["r"], b["y"] - b["r"], b["x"] + b["r"], b["y"] + b["r"]], fill=(20, 25, 40), outline=b["color"], width=3)
            draw.ellipse([b["x"] - 12, b["y"] - 12, b["x"] + 12, b["y"] + 12], fill=b["color"])

        # Flippers
        # Left flipper
        lf_angle = -25 if self.left_flipper_up else 20
        rad_l = math.radians(lf_angle)
        draw.line([(390, 620), (390 + int(math.cos(rad_l) * 80), 620 + int(math.sin(rad_l) * 80))], fill=(255, 210, 0), width=8)

        # Right flipper
        rf_angle = 205 if self.right_flipper_up else 160
        rad_r = math.radians(rf_angle)
        draw.line([(630, 620), (630 + int(math.cos(rad_r) * 80), 620 + int(math.sin(rad_r) * 80))], fill=(255, 210, 0), width=8)

        # Ball
        bx, by = int(self.ball_x), int(self.ball_y)
        draw.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(240, 245, 255), outline=(0, 240, 255), width=2)

        # Left / Right Side HUD Panels
        draw.rounded_rectangle([45, 120, 235, 340], radius=8, fill=(16, 22, 34), outline=(40, 65, 95))
        draw.text((60, 135), "BONUSY STOŁU:", fill=(0, 255, 200), font=get_font(14, bold=True))
        draw.text((60, 175), "• MULTIBALL: 80%", fill=(220, 230, 245), font=get_font(13))
        draw.text((60, 210), "• JACKPOT: 500K", fill=(255, 210, 0), font=get_font(13, bold=True))
        draw.text((60, 245), "• TILT: SAFE", fill=(0, 255, 120), font=get_font(13))
        draw.text((60, 280), "• RAMP COMBO: x4", fill=(190, 80, 255), font=get_font(13))

        draw.rounded_rectangle([785, 120, 975, 340], radius=8, fill=(16, 22, 34), outline=(40, 65, 95))
        draw.text((800, 135), "STEROWANIE FIZYKĄ:", fill=(0, 255, 200), font=get_font(14, bold=True))
        draw.text((800, 175), "L1: Lewy Flipper", fill=(220, 230, 245), font=get_font(13))
        draw.text((800, 210), "R1: Prawy Flipper", fill=(220, 230, 245), font=get_font(13))
        draw.text((800, 245), "A: Wyrzutnia tłokowa", fill=(255, 210, 0), font=get_font(13))
        draw.text((800, 280), "X: Nowa bila", fill=(0, 200, 255), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_L1":
            self.left_flipper_up = not self.left_flipper_up
            return True
        elif event == "KEY_R1":
            self.right_flipper_up = not self.right_flipper_up
            return True
        elif event == "KEY_A":
            self.ball_x = 720
            self.ball_y = 560
            self.vx = -1.5
            self.vy = -11.0
            return True
        elif event == "KEY_X":
            self.ball_x = 500
            self.ball_y = 200
            self.vx = 2.0
            self.vy = 1.0
            return True
        return False
