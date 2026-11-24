#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_artillery.py - Cyber Artillery (Scorched Earth / Tank Wars 2D)
Pure-Python physics artillery duel on destructible procedural terrain for TrimUI Brick (1024x768).
Zero external dependencies.
"""

import math
import random
import time
from typing import Dict, Any, List
from PIL import Image, ImageDraw

from core.module_base import BaseModule
from core.canvas import Canvas, get_font

SCREEN_W = 1024
SCREEN_H = 768


class ArtilleryModule(BaseModule):
    """2D Physics Tank Duel with Destructible Terrain."""

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.terrain_heights = [450] * SCREEN_W
        self.p1_x = 120
        self.p2_x = SCREEN_W - 140
        self.p1_angle = 45.0
        self.p2_angle = 135.0
        self.p1_power = 65.0
        self.p2_power = 60.0
        self.wind = 0.0  # -15 to +15

        self.weapons = [
            {"name": "Standard Cannon", "radius": 24, "dmg": 35},
            {"name": "Cyber MIRV (x3)", "radius": 18, "dmg": 25},
            {"name": "Mini-Nuke Warhead", "radius": 55, "dmg": 80},
            {"name": "Dirt Maker", "radius": -30, "dmg": 0},
        ]
        self.cur_weapon_idx = 0

        self.p1_hp = 100
        self.p2_hp = 100
        self.turn = 1  # 1: Player, 2: AI Bot
        self.state = "AIM"  # AIM, FLYING, EXPLODING, GAMEOVER

        # Projectile physics
        self.proj_x = 0.0
        self.proj_y = 0.0
        self.proj_vx = 0.0
        self.proj_vy = 0.0
        self.proj_trail: List[tuple] = []
        self.explosion_timer = 0.0
        self.explosion_x = 0
        self.explosion_y = 0
        self.explosion_rad = 0

        self.status_banner = "Twoja tura! Ustaw kąt i siłę, naciśnij [A]."
        self._generate_terrain()

    def get_hotkey_hints(self) -> List[Dict[str, str]]:
        return [
            {"key": "D-Pad Góra/Dół", "desc": "Kąt lufy"},
            {"key": "D-Pad Lewo/Prawo", "desc": "Siła ognia"},
            {"key": "L1/R1", "desc": "Wybór broni"},
            {"key": "A", "desc": "Ognia!"},
            {"key": "Y", "desc": "Nowa mapa"},
        ]

    def _generate_terrain(self):
        """Generates a smooth rolling hills terrain with craters."""
        base_h = 500
        freq1 = random.uniform(0.003, 0.008)
        freq2 = random.uniform(0.012, 0.022)
        offset = random.uniform(0, 1000)

        for x in range(SCREEN_W):
            h = base_h + math.sin((x + offset) * freq1) * 120 + math.cos((x + offset) * freq2) * 50
            self.terrain_heights[x] = max(260, min(650, int(h)))

        # Flatten player spawn spots
        p1_h = self.terrain_heights[self.p1_x]
        for x in range(self.p1_x - 20, self.p1_x + 20):
            self.terrain_heights[x] = p1_h

        p2_h = self.terrain_heights[self.p2_x]
        for x in range(self.p2_x - 20, self.p2_x + 20):
            self.terrain_heights[x] = p2_h

        self.wind = round(random.uniform(-12.0, 12.0), 1)

    def _fire(self):
        """Launches projectile."""
        if self.state != "AIM":
            return
        self.state = "FLYING"
        self.proj_trail = []

        is_p1 = (self.turn == 1)
        tank_x = self.p1_x if is_p1 else self.p2_x
        tank_y = self.terrain_heights[tank_x] - 12
        angle = self.p1_angle if is_p1 else self.p2_angle
        power = self.p1_power if is_p1 else self.p2_power

        rad = math.radians(angle)
        barrel_len = 22
        self.proj_x = tank_x + math.cos(rad) * barrel_len
        self.proj_y = tank_y - math.sin(rad) * barrel_len
        self.proj_vx = math.cos(rad) * (power * 0.28)
        self.proj_vy = -math.sin(rad) * (power * 0.28)

    def _apply_explosion(self, cx: int, cy: int, radius: int):
        """Destructs or builds terrain and applies tank damage."""
        if radius > 0:
            # Crater destruction
            for x in range(max(0, cx - radius), min(SCREEN_W, cx + radius)):
                dx = x - cx
                dy = int(math.sqrt(max(0, radius * radius - dx * dx)))
                crater_bottom = cy + dy
                if crater_bottom > self.terrain_heights[x]:
                    self.terrain_heights[x] = min(SCREEN_H - 10, max(self.terrain_heights[x], crater_bottom))
        else:
            # Dirt bomb (adds terrain)
            r = abs(radius)
            for x in range(max(0, cx - r), min(SCREEN_W, cx + r)):
                dx = x - cx
                dy = int(math.sqrt(max(0, r * r - dx * dx)))
                self.terrain_heights[x] = max(180, self.terrain_heights[x] - dy)

        # Tank damage
        d1 = math.hypot(cx - self.p1_x, cy - (self.terrain_heights[self.p1_x] - 8))
        d2 = math.hypot(cx - self.p2_x, cy - (self.terrain_heights[self.p2_x] - 8))

        w = self.weapons[self.cur_weapon_idx]
        dmg_max = w["dmg"]

        if d1 < abs(radius) + 12:
            self.p1_hp = max(0, self.p1_hp - int(dmg_max * (1.0 - d1 / (abs(radius) + 14))))
        if d2 < abs(radius) + 12:
            self.p2_hp = max(0, self.p2_hp - int(dmg_max * (1.0 - d2 / (abs(radius) + 14))))

        if self.p1_hp <= 0 or self.p2_hp <= 0:
            self.state = "GAMEOVER"
            self.status_banner = "KONIEC GRY! " + ("GRACZ 1 WYGRYWA!" if self.p2_hp <= 0 else "BOT AI WYGRYWA!")
        else:
            # Switch turn
            self.turn = 2 if self.turn == 1 else 1
            self.status_banner = "Tura bota AI..." if self.turn == 2 else "Twoja tura! Wyceluj i strzelaj."
            self.wind = round(self.wind + random.uniform(-4.0, 4.0), 1)

            # Trigger AI logic if bot's turn
            if self.turn == 2:
                self._ai_turn()

    def _ai_turn(self):
        """Simple AI tank logic calculating trajectory with wind offset."""
        dx = self.p1_x - self.p2_x
        # Base angle ~135 degrees
        self.p2_angle = round(random.uniform(128.0, 148.0), 1)
        # Power with estimated range and wind correction
        dist = abs(dx)
        base_p = math.sqrt(dist * 9.8) * 2.1
        self.p2_power = max(20.0, min(100.0, round(base_p - self.wind * 1.5 + random.uniform(-6, 6), 1)))

    def update(self, dt: float):
        if self.state == "FLYING":
            # Gravity & wind
            self.proj_vy += 9.8 * 0.45 * dt
            self.proj_vx += self.wind * 0.08 * dt
            self.proj_x += self.proj_vx * 60.0 * dt
            self.proj_y += self.proj_vy * 60.0 * dt

            self.proj_trail.append((int(self.proj_x), int(self.proj_y)))
            if len(self.proj_trail) > 40:
                self.proj_trail.pop(0)

            # Check collision with ground or screen bounds
            ix = int(self.proj_x)
            iy = int(self.proj_y)
            if ix < 0 or ix >= SCREEN_W or iy >= SCREEN_H or (0 <= ix < SCREEN_W and iy >= self.terrain_heights[ix]):
                self.state = "EXPLODING"
                self.explosion_x = max(0, min(SCREEN_W - 1, ix))
                self.explosion_y = max(0, min(SCREEN_H - 1, iy))
                self.explosion_rad = self.weapons[self.cur_weapon_idx]["radius"]
                self.explosion_timer = 0.6
                self._apply_explosion(self.explosion_x, self.explosion_y, self.explosion_rad)

        elif self.state == "EXPLODING":
            self.explosion_timer -= dt
            if self.explosion_timer <= 0:
                if self.state != "GAMEOVER":
                    self.state = "AIM"
                    if self.turn == 2:
                        self._fire()

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = SCREEN_W, SCREEN_H

        # Sky background with stars
        draw.rectangle([0, 0, w, h], fill=(8, 12, 22))

        # Terrain polygon
        poly = [(0, h)]
        for x in range(w):
            poly.append((x, self.terrain_heights[x]))
        poly.append((w, h))
        draw.polygon(poly, fill=(20, 32, 45), outline=(0, 200, 255))

        # Terrain neon crust highlight
        for x in range(0, w - 1, 3):
            draw.line([(x, self.terrain_heights[x]), (x + 3, self.terrain_heights[x + 3])], fill=(0, 255, 180), width=2)

        # Tanks
        # Tank 1 (Player - Cyan)
        t1_y = self.terrain_heights[self.p1_x]
        draw.rectangle([self.p1_x - 14, t1_y - 10, self.p1_x + 14, t1_y], fill=(0, 180, 230), outline=(0, 255, 255))
        draw.ellipse([self.p1_x - 7, t1_y - 16, self.p1_x + 7, t1_y - 6], fill=(0, 220, 255))
        # Barrel 1
        b1_rad = math.radians(self.p1_angle)
        draw.line([(self.p1_x, t1_y - 11),
                   (self.p1_x + math.cos(b1_rad) * 18, t1_y - 11 - math.sin(b1_rad) * 18)],
                  fill=(0, 255, 255), width=3)

        # Tank 2 (Bot - Amber / Red)
        t2_y = self.terrain_heights[self.p2_x]
        draw.rectangle([self.p2_x - 14, t2_y - 10, self.p2_x + 14, t2_y], fill=(220, 80, 40), outline=(255, 140, 0))
        draw.ellipse([self.p2_x - 7, t2_y - 16, self.p2_x + 7, t2_y - 6], fill=(255, 120, 30))
        # Barrel 2
        b2_rad = math.radians(self.p2_angle)
        draw.line([(self.p2_x, t2_y - 11),
                   (self.p2_x + math.cos(b2_rad) * 18, t2_y - 11 - math.sin(b2_rad) * 18)],
                  fill=(255, 160, 0), width=3)

        # Projectile Trail & Bullet
        if self.state in ("FLYING", "EXPLODING"):
            for pt in self.proj_trail:
                draw.point(pt, fill=(255, 220, 80))
            if self.state == "FLYING":
                draw.ellipse([self.proj_x - 3, self.proj_y - 3, self.proj_x + 3, self.proj_y + 3], fill=(255, 255, 255))

        # Explosion blast
        if self.state == "EXPLODING":
            rad = int(abs(self.explosion_rad) * (1.0 + (0.6 - self.explosion_timer) * 1.5))
            draw.ellipse([self.explosion_x - rad, self.explosion_y - rad,
                          self.explosion_x + rad, self.explosion_y + rad],
                         outline=(255, 180, 0), width=3)
            draw.ellipse([self.explosion_x - rad // 2, self.explosion_y - rad // 2,
                          self.explosion_x + rad // 2, self.explosion_y + rad // 2],
                         fill=(255, 255, 200))

        # Top HUD Bar
        draw.rectangle([0, 0, w, 52], fill=(12, 16, 26, 230), outline=(0, 180, 220), width=1)
        draw.text((18, 14), "CYBER ARTILLERY 2D", fill=(0, 255, 220), font=get_font(18, bold=True))

        # HP Bars
        draw.text((240, 16), f"P1 (GRACZ): {self.p1_hp}%", fill=(0, 220, 255), font=get_font(15, bold=True))
        draw.text((420, 16), f"P2 (BOT): {self.p2_hp}%", fill=(255, 120, 60), font=get_font(15, bold=True))

        # Wind indicator
        wind_dir = ">> PRAWO >>" if self.wind > 0 else ("<< LEWO <<" if self.wind < 0 else "CISZA")
        draw.text((620, 16), f"WIATR: {abs(self.wind):.1f} {wind_dir}", fill=(255, 220, 0), font=get_font(14))

        # Weapon badge
        canvas.draw_badge(w - 200, 12, self.weapons[self.cur_weapon_idx]["name"], bg_color=(0, 90, 140), text_color=(255, 255, 255))

        # Aiming values at bottom
        draw.rectangle([20, h - 54, w - 20, h - 14], fill=(10, 14, 22, 220), outline=(0, 120, 160), width=1)
        draw.text((36, h - 42), f"KĄT: {self.p1_angle:.1f}°", fill=(0, 255, 220), font=get_font(16, bold=True))
        draw.text((200, h - 42), f"MOC: {self.p1_power:.1f}%", fill=(255, 210, 0), font=get_font(16, bold=True))
        draw.text((380, h - 40), self.status_banner, fill=(220, 230, 245), font=get_font(14))

    def handle_input(self, event: str) -> bool:
        if self.state == "GAMEOVER":
            if event in ("KEY_A", "KEY_Y"):
                self.p1_hp = 100
                self.p2_hp = 100
                self.state = "AIM"
                self._generate_terrain()
            return True

        if self.turn == 1 and self.state == "AIM":
            if event == "KEY_UP":
                self.p1_angle = min(90.0, self.p1_angle + 2.0)
                return True
            elif event == "KEY_DOWN":
                self.p1_angle = max(0.0, self.p1_angle - 2.0)
                return True
            elif event == "KEY_RIGHT":
                self.p1_power = min(100.0, self.p1_power + 3.0)
                return True
            elif event == "KEY_LEFT":
                self.p1_power = max(10.0, self.p1_power - 3.0)
                return True
            elif event == "KEY_R1":
                self.cur_weapon_idx = (self.cur_weapon_idx + 1) % len(self.weapons)
                return True
            elif event == "KEY_L1":
                self.cur_weapon_idx = (self.cur_weapon_idx - 1) % len(self.weapons)
                return True
            elif event == "KEY_A":
                self._fire()
                return True
            elif event == "KEY_Y":
                self._generate_terrain()
                return True
        return False
