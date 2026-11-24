#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import random
import time
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AsteroidsModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.ship_x = 512.0
        self.ship_y = 384.0
        self.ship_angle = -90.0 # facing up
        self.vx = 0.0
        self.vy = 0.0
        self.bullets = [] # [(x, y, vx, vy, ttl)]
        self.asteroids = [] # [(x, y, vx, vy, radius, points)]
        self.score = 1420
        self.lives = 3
        self.level = 3
        self._spawn_asteroids()

    def _spawn_asteroids(self):
        self.asteroids.clear()
        for _ in range(6):
            x = random.choice([random.randint(50, 300), random.randint(700, 950)])
            y = random.choice([random.randint(120, 250), random.randint(500, 700)])
            r = random.randint(35, 55)
            pts = []
            num_v = 10
            for i in range(num_v):
                a = (i / num_v) * 2 * math.pi
                dist = r * (0.75 + random.random() * 0.5)
                pts.append((math.cos(a) * dist, math.sin(a) * dist))
            self.asteroids.append({
                "x": x, "y": y,
                "vx": random.uniform(-1.5, 1.5), "vy": random.uniform(-1.5, 1.5),
                "r": r, "pts": pts
            })

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Obrót / Ciąg"},
            {"key": "A", "desc": "Laser"},
            {"key": "B", "desc": "Hiperprzestrzeń"},
            {"key": "X", "desc": "Reset gry"}
        ]

    def update(self, dt: float):
        # Update asteroids
        for ast in self.asteroids:
            ast["x"] = (ast["x"] + ast["vx"]) % 960 + 32
            ast["y"] = (ast["y"] + ast["vy"]) % 600 + 100

        # Update bullets
        new_b = []
        for b in self.bullets:
            bx, by, bvx, bvy, ttl = b
            bx += bvx
            by += bvy
            ttl -= 1
            if ttl > 0 and 30 < bx < 994 and 100 < by < 730:
                new_b.append((bx, by, bvx, bvy, ttl))
        self.bullets = new_b

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="☄️ VECTOR SPACE COMBAT // ASTEROIDS 360°",
                         subtitle=f"Wynik: {self.score:05d} | Życia: {'▲ ' * self.lives} | Fala: {self.level}",
                         border_color=(0, 255, 200))

        # Vector Radar Playfield
        play_rect = [32, 106, w - 32, h - 34]
        draw.rectangle(play_rect, fill=(6, 10, 16), outline=(0, 120, 100), width=2)

        # Starfield
        random.seed(42)
        for _ in range(60):
            sx = random.randint(36, w - 36)
            sy = random.randint(110, h - 38)
            draw.point((sx, sy), fill=(100, 140, 180))

        # Render Asteroids (Vector Wireframe)
        for ast in self.asteroids:
            pts = [(ast["x"] + px, ast["y"] + py) for px, py in ast["pts"]]
            if len(pts) > 2:
                draw.polygon(pts, fill=(12, 24, 30), outline=(0, 255, 180), width=2)

        # Render Bullets (Laser bolts)
        for b in self.bullets:
            draw.ellipse([b[0]-3, b[1]-3, b[0]+3, b[1]+3], fill=(255, 255, 0), outline=(255, 100, 0))

        # Render Player Ship
        rad = math.radians(self.ship_angle)
        nose = (self.ship_x + math.cos(rad) * 22, self.ship_y + math.sin(rad) * 22)
        left = (self.ship_x + math.cos(rad + 2.5) * 16, self.ship_y + math.sin(rad + 2.5) * 16)
        right = (self.ship_x + math.cos(rad - 2.5) * 16, self.ship_y + math.sin(rad - 2.5) * 16)
        back = (self.ship_x - math.cos(rad) * 6, self.ship_y - math.sin(rad) * 6)

        draw.polygon([nose, left, back, right], fill=(0, 40, 60), outline=(0, 255, 255), width=2)
        # Thruster plume
        draw.polygon([left, (self.ship_x - math.cos(rad)*18, self.ship_y - math.sin(rad)*18), right], fill=(255, 140, 0))

        # HUD Info Badge
        canvas.draw_badge(50, 120, "HYPER-RADAR ACTIVE", bg_color=(0, 80, 50), text_color=(0, 255, 160))
        canvas.draw_badge(w - 240, 120, f"DEFENSE LVL {self.level}", bg_color=(20, 40, 80), text_color=(0, 200, 255))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_LEFT":
            self.ship_angle -= 15.0
            return True
        elif event == "KEY_RIGHT":
            self.ship_angle += 15.0
            return True
        elif event == "KEY_UP":
            rad = math.radians(self.ship_angle)
            self.vx += math.cos(rad) * 1.5
            self.vy += math.sin(rad) * 1.5
            return True
        elif event == "KEY_A":
            rad = math.radians(self.ship_angle)
            bx = self.ship_x + math.cos(rad) * 25
            by = self.ship_y + math.sin(rad) * 25
            self.bullets.append((bx, by, math.cos(rad) * 8, math.sin(rad) * 8, 40))
            return True
        elif event == "KEY_X":
            self.score = 0
            self.lives = 3
            self.ship_x, self.ship_y = 512, 384
            self._spawn_asteroids()
            return True
        return False
