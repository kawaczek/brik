#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import random
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class BreakoutModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.paddle_x = 450.0
        self.paddle_w = 120.0
        self.paddle_h = 16.0
        self.ball_x = 512.0
        self.ball_y = 600.0
        self.ball_vx = 3.5
        self.ball_vy = -4.5
        self.score = 3450
        self.lives = 3
        self.combo = 4
        self.rows = 6
        self.cols = 10
        self.bricks = []
        self._init_bricks()

    def _init_bricks(self):
        self.bricks.clear()
        colors = [(255, 60, 100), (255, 140, 0), (255, 220, 0), (0, 255, 180), (0, 200, 255), (180, 80, 255)]
        for r in range(self.rows):
            for c in range(self.cols):
                self.bricks.append({
                    "x": 60 + c * 91, "y": 130 + r * 30,
                    "w": 82, "h": 22,
                    "color": colors[r % len(colors)],
                    "alive": True, "hp": 1 if r > 1 else 2
                })

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad ◄►", "desc": "Ruch paletką VAUS"},
            {"key": "A", "desc": "Wystrzał kulki"},
            {"key": "X", "desc": "Reset poziomu"}
        ]

    def update(self, dt: float):
        # Ball movement
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        # Wall collisions
        if self.ball_x <= 40:
            self.ball_x = 40
            self.ball_vx = abs(self.ball_vx)
        elif self.ball_x >= 984:
            self.ball_x = 984
            self.ball_vx = -abs(self.ball_vx)
        if self.ball_y <= 115:
            self.ball_y = 115
            self.ball_vy = abs(self.ball_vy)
        elif self.ball_y >= 700:
            # Ball lost
            self.ball_x = 512
            self.ball_y = 550
            self.ball_vy = -4.5

        # Paddle collision
        py = 640
        if py <= self.ball_y <= py + self.paddle_h and self.paddle_x <= self.ball_x <= self.paddle_x + self.paddle_w:
            self.ball_vy = -abs(self.ball_vy)
            offset = (self.ball_x - (self.paddle_x + self.paddle_w / 2)) / (self.paddle_w / 2)
            self.ball_vx = offset * 5.5

        # Brick collisions
        for b in self.bricks:
            if b["alive"] and b["x"] <= self.ball_x <= b["x"] + b["w"] and b["y"] <= self.ball_y <= b["y"] + b["h"]:
                b["alive"] = False
                self.ball_vy = -self.ball_vy
                self.score += 150
                break

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🧱 CYBER ARKANOID // VAUS PADDLE & LASER",
                         subtitle=f"Wynik: {self.score:05d} | Życia: {'❤️ ' * self.lives} | Combo: x{self.combo}",
                         border_color=(0, 240, 255))

        # Playfield boundary
        draw.rectangle([35, 110, w - 35, 680], fill=(8, 12, 18), outline=(30, 50, 75), width=2)

        # Bricks
        for b in self.bricks:
            if b["alive"]:
                draw.rounded_rectangle([b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]], radius=4, fill=b["color"], outline=(255, 255, 255), width=1)
                # Neon highlight line
                draw.line([(b["x"] + 4, b["y"] + 3), (b["x"] + b["w"] - 4, b["y"] + 3)], fill=(255, 255, 255, 180), width=1)

        # Paddle (Vaus)
        px = int(self.paddle_x)
        draw.rounded_rectangle([px, 640, px + int(self.paddle_w), 640 + int(self.paddle_h)], radius=6, fill=(0, 240, 255), outline=(255, 255, 255), width=2)
        # Thrusters on paddle
        draw.rectangle([px + 10, 656, px + 25, 660], fill=(255, 100, 0))
        draw.rectangle([px + int(self.paddle_w) - 25, 656, px + int(self.paddle_w) - 10, 660], fill=(255, 100, 0))

        # Ball
        bx, by = int(self.ball_x), int(self.ball_y)
        draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(255, 255, 255), outline=(0, 240, 255))

        # Status HUD
        canvas.draw_badge(50, 120, "POWER-UP: MULTIBALL READY", bg_color=(0, 60, 40), text_color=(0, 255, 140))
        canvas.draw_badge(w - 240, 120, "VAUS CORE: ONLINE", bg_color=(20, 40, 80), text_color=(0, 200, 255))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_LEFT":
            self.paddle_x = max(40, self.paddle_x - 30)
            return True
        elif event == "KEY_RIGHT":
            self.paddle_x = min(1024 - 40 - self.paddle_w, self.paddle_x + 30)
            return True
        elif event == "KEY_X":
            self._init_bricks()
            self.score = 0
            return True
        return False
