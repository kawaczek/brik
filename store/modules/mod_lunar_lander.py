#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, random, time
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class LunarLanderModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.ship_x = 512.0
        self.ship_y = 120.0
        self.vx = 0.5
        self.vy = 0.0
        self.fuel = 500.0
        self.angle = 0.0 # degrees
        self.thrusting = False
        self.pad_x = 460
        self.pad_w = 110
        self.state = "FLY" # FLY, LANDED, CRASHED
        self._init_terrain()

    def get_hotkey_hints(self):
        return [
            {"key": "A", "desc": "Ciąg główny"},
            {"key": "D-Pad", "desc": "Obrót RCS"},
            {"key": "Y", "desc": "Nowe lądowanie"}
        ]

    def _init_terrain(self):
        self.terrain = [620] * 1024
        for x in range(1024):
            self.terrain[x] = 580 + int(math.sin(x * 0.012) * 50 + math.cos(x * 0.025) * 30)
        # Flatten target pad
        for x in range(self.pad_x, self.pad_x + self.pad_w):
            self.terrain[x] = 610

    def update(self, dt: float):
        if self.state == "FLY":
            # Gravity
            self.vy += 1.6 * dt
            # Thrust
            if self.thrusting and self.fuel > 0:
                rad = math.radians(self.angle - 90)
                self.vx += math.cos(rad) * 4.2 * dt
                self.vy += math.sin(rad) * 4.2 * dt
                self.fuel = max(0.0, self.fuel - 18.0 * dt)
            
            self.ship_x += self.vx * 40.0 * dt
            self.ship_y += self.vy * 40.0 * dt
            
            # Ground check
            ix = int(max(0, min(1023, self.ship_x)))
            ground_y = self.terrain[ix]
            if self.ship_y >= ground_y - 12:
                # Landed or crashed
                speed = math.hypot(self.vx, self.vy)
                if self.pad_x <= ix <= self.pad_x + self.pad_w and speed < 1.8 and abs(self.angle) < 15:
                    self.state = "LANDED"
                else:
                    self.state = "CRASHED"

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🚀 APOLLO CYBER LANDER // MOONBASE ALPHA", subtitle=f"Prędkość: {math.hypot(self.vx, self.vy):.1f} m/s | Paliwo: {int(self.fuel)} kg | Kąt: {self.angle:.0f}°", border_color=(255, 210, 0))
        
        # Draw Space & Stars
        draw.rectangle([30, 110, w - 30, h - 40], fill=(6, 10, 18))
        
        # Terrain
        pts = [(30, h - 40)]
        for x in range(30, w - 30, 2):
            pts.append((x, self.terrain[x]))
        pts.append((w - 30, h - 40))
        draw.polygon(pts, fill=(24, 32, 44), outline=(0, 200, 255))
        
        # Landing Pad highlight
        draw.line([(self.pad_x, 610), (self.pad_x + self.pad_w, 610)], fill=(0, 255, 120), width=4)
        
        # Draw Lander Ship
        sx, sy = int(self.ship_x), int(self.ship_y)
        draw.rounded_rectangle([sx - 12, sy - 12, sx + 12, sy + 8], radius=3, fill=(240, 245, 255), outline=(0, 220, 255))
        draw.line([(sx - 14, sy + 8), (sx - 20, sy + 18)], fill=(180, 190, 210), width=2)
        draw.line([(sx + 14, sy + 8), (sx + 20, sy + 18)], fill=(180, 190, 210), width=2)
        
        # Thrust flame
        if self.thrusting and self.fuel > 0 and self.state == "FLY":
            draw.polygon([(sx - 6, sy + 9), (sx + 6, sy + 9), (sx, sy + 24)], fill=(255, 140, 0))
            
        # Flight state badge
        if self.state == "LANDED":
            canvas.draw_badge(w // 2 - 100, 300, "UDANE LĄDOWANIE! 100 PKT", bg_color=(0, 140, 60), text_color=(255, 255, 255))
        elif self.state == "CRASHED":
            canvas.draw_badge(w // 2 - 100, 300, "KATASTROFA MODUŁU!", bg_color=(160, 20, 20), text_color=(255, 255, 255))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_A":
            self.thrusting = True
            return True
        elif event == "KEY_LEFT":
            self.angle = max(-60.0, self.angle - 5.0)
            return True
        elif event == "KEY_RIGHT":
            self.angle = min(60.0, self.angle + 5.0)
            return True
        elif event == "KEY_Y":
            self.ship_x = 512.0
            self.ship_y = 120.0
            self.vx = 0.5
            self.vy = 0.0
            self.fuel = 500.0
            self.state = "FLY"
            self._init_terrain()
            return True
        return False
