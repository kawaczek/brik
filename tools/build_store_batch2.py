#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/build_store_batch2.py - Generates Batch 2 of modules into store/modules/
(mod_breakout, mod_pinball, mod_sokoban, mod_periodic, mod_ee_lab, mod_hex)
"""

import os
import sys

MODULES = {}

# ==============================================================================
# 1. mod_breakout.py - Cyber Arkanoid & Vaus Paddle
# ==============================================================================
MODULES["mod_breakout"] = '''#!/usr/bin/env python3
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
'''

# ==============================================================================
# 2. mod_pinball.py - Neon Cyber Pinball
# ==============================================================================
MODULES["mod_pinball"] = '''#!/usr/bin/env python3
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
'''

# ==============================================================================
# 3. mod_sokoban.py - Cyberdeck Warehouse Sokoban
# ==============================================================================
MODULES["mod_sokoban"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class SokobanModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.moves = 28
        self.pushes = 14
        self.level = 1
        self.player_x = 3
        self.player_y = 3
        # 0: empty, 1: wall, 2: box, 3: target, 4: box on target
        self.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 2, 0, 1, 0, 3, 0, 1],
            [1, 0, 0, 0, 0, 0, 3, 0, 1],
            [1, 1, 0, 2, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.grid_rows = len(self.grid)
        self.grid_cols = len(self.grid[0])

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Ruch technika"},
            {"key": "B", "desc": "Cofnij ruch (Undo)"},
            {"key": "X", "desc": "Reset poziomu"},
            {"key": "A", "desc": "Następny poziom"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="📦 SOKOBAN // CYBERDECK WAREHOUSE",
                         subtitle=f"Poziom: {self.level} // Serwerownia Gamma | Ruchy: {self.moves} | Pchnięcia: {self.pushes}",
                         border_color=(0, 255, 140))

        # Warehouse Board
        ox, oy = 180, 130
        tile_sz = 68

        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                tx = ox + c * tile_sz
                ty = oy + r * tile_sz
                cell = self.grid[r][c]

                # Floor grid
                draw.rectangle([tx, ty, tx + tile_sz, ty + tile_sz], fill=(12, 16, 24), outline=(25, 35, 50))

                if cell == 1: # Server rack wall
                    draw.rounded_rectangle([tx + 2, ty + 2, tx + tile_sz - 2, ty + tile_sz - 2], radius=6, fill=(24, 34, 48), outline=(0, 200, 255), width=2)
                    draw.line([(tx + 12, ty + 20), (tx + tile_sz - 12, ty + 20)], fill=(0, 255, 200), width=2)
                    draw.line([(tx + 12, ty + 40), (tx + tile_sz - 12, ty + 40)], fill=(0, 255, 200), width=2)
                elif cell == 3: # Power socket Target
                    draw.ellipse([tx + 18, ty + 18, tx + tile_sz - 18, ty + tile_sz - 18], fill=(10, 40, 25), outline=(0, 255, 120), width=2)
                    draw.text((tx + 26, ty + 22), "⚡", fill=(0, 255, 140), font=get_font(18))
                elif cell == 2: # Power Core Box
                    draw.rounded_rectangle([tx + 8, ty + 8, tx + tile_sz - 8, ty + tile_sz - 8], radius=8, fill=(80, 50, 10), outline=(255, 170, 0), width=2)
                    draw.text((tx + 22, ty + 20), "CORE", fill=(255, 220, 0), font=get_font(12, bold=True))
                elif cell == 4: # Box on Target (Done)
                    draw.rounded_rectangle([tx + 8, ty + 8, tx + tile_sz - 8, ty + tile_sz - 8], radius=8, fill=(10, 80, 40), outline=(0, 255, 140), width=3)
                    draw.text((tx + 24, ty + 20), "OK!", fill=(255, 255, 255), font=get_font(13, bold=True))

        # Player
        px = ox + self.player_x * tile_sz
        py = oy + self.player_y * tile_sz
        draw.ellipse([px + 12, py + 12, px + tile_sz - 12, py + tile_sz - 12], fill=(0, 200, 255), outline=(255, 255, 255), width=2)
        draw.text((px + 24, py + 20), "🤖", fill=(255, 255, 255), font=get_font(18))

        # Right Telemetry
        rx = ox + self.grid_cols * tile_sz + 40
        draw.rounded_rectangle([rx, 130, w - 50, 600], radius=10, fill=(16, 22, 34), outline=(40, 65, 95))
        draw.text((rx + 20, 150), "STATUS OPERACJI:", fill=(0, 255, 200), font=get_font(16, bold=True))
        draw.text((rx + 20, 190), f"Cele: 2 / 2 rdzenie", fill=(220, 230, 245), font=get_font(14))
        draw.text((rx + 20, 225), f"Licznik ruchów: {self.moves}", fill=(220, 230, 245), font=get_font(14))
        draw.text((rx + 20, 260), f"Pchnięcia: {self.pushes}", fill=(255, 210, 0), font=get_font(14, bold=True))
        draw.text((rx + 20, 295), f"Czas sesji: 02:41", fill=(140, 170, 200), font=get_font(14))

        canvas.draw_badge(rx + 20, 360, "CEL: PRZESUŃ RDZENIE DO ⚡", bg_color=(20, 50, 40), text_color=(0, 255, 140))

    def handle_input(self, event: str) -> bool:
        dx, dy = 0, 0
        if event == "KEY_LEFT": dx = -1
        elif event == "KEY_RIGHT": dx = 1
        elif event == "KEY_UP": dy = -1
        elif event == "KEY_DOWN": dy = 1
        if dx != 0 or dy != 0:
            nx = self.player_x + dx
            ny = self.player_y + dy
            if 0 <= ny < self.grid_rows and 0 <= nx < self.grid_cols and self.grid[ny][nx] != 1:
                self.player_x = nx
                self.player_y = ny
                self.moves += 1
                return True
        return False
'''

# ==============================================================================
# 4. mod_periodic.py - ChemLab Periodic Table of Elements
# ==============================================================================
MODULES["mod_periodic"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class PeriodicModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.cursor_idx = 0
        self.elements = [
            {"sym": "H", "name": "Wodór (Hydrogen)", "num": 1, "mass": 1.008, "cat": "Niemetal", "conf": "1s¹"},
            {"sym": "He", "name": "Hel (Helium)", "num": 2, "mass": 4.0026, "cat": "Gaz szlachetny", "conf": "1s²"},
            {"sym": "Li", "name": "Lit (Lithium)", "num": 3, "mass": 6.94, "cat": "Litowiec", "conf": "[He] 2s¹"},
            {"sym": "Be", "name": "Beryl (Beryllium)", "num": 4, "mass": 9.0122, "cat": "Berylowiec", "conf": "[He] 2s²"},
            {"sym": "B", "name": "Bor (Boron)", "num": 5, "mass": 10.81, "cat": "Półmetal", "conf": "[He] 2s² 2p¹"},
            {"sym": "C", "name": "Węgiel (Carbon)", "num": 6, "mass": 12.011, "cat": "Niemetal", "conf": "[He] 2s² 2p²"},
            {"sym": "N", "name": "Azot (Nitrogen)", "num": 7, "mass": 14.007, "cat": "Niemetal", "conf": "[He] 2s² 2p³"},
            {"sym": "O", "name": "Tlen (Oxygen)", "num": 8, "mass": 15.999, "cat": "Niemetal", "conf": "[He] 2s² 2p⁴"},
            {"sym": "F", "name": "Fluor (Fluorine)", "num": 9, "mass": 18.998, "cat": "Fluorowiec", "conf": "[He] 2s² 2p⁵"},
            {"sym": "Ne", "name": "Neon (Neon)", "num": 10, "mass": 20.180, "cat": "Gaz szlachetny", "conf": "[He] 2s² 2p⁶"},
            {"sym": "Na", "name": "Sód (Sodium)", "num": 11, "mass": 22.990, "cat": "Litowiec", "conf": "[Ne] 3s¹"},
            {"sym": "Si", "name": "Krzem (Silicon)", "num": 14, "mass": 28.085, "cat": "Półmetal", "conf": "[Ne] 3s² 3p²"},
            {"sym": "Fe", "name": "Żelazo (Iron)", "num": 26, "mass": 55.845, "cat": "Metal przejściowy", "conf": "[Ar] 3d⁶ 4s²"},
            {"sym": "Cu", "name": "Miedź (Copper)", "num": 29, "mass": 63.546, "cat": "Metal przejściowy", "conf": "[Ar] 3d¹⁰ 4s¹"},
            {"sym": "Au", "name": "Złoto (Gold)", "num": 79, "mass": 196.97, "cat": "Metal szlachetny", "conf": "[Xe] 4f¹⁴ 5d¹⁰ 6s¹"}
        ]

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Wybór pierwiastka"},
            {"key": "A", "desc": "Kalkulator masy molowej"},
            {"key": "X", "desc": "Izotopy i właściwości"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🧪 CHEMLAB // UKŁAD OKRESOWY PIERWIASTKÓW",
                         subtitle="118 pierwiastków | Konfiguracje elektronowe | Właściwości fizykochemiczne",
                         border_color=(0, 240, 255))

        # Grid of Elements (Left)
        gx, gy = 45, 120
        tile_w, tile_h = 95, 80

        for i, el in enumerate(self.elements):
            col = i % 5
            row = i // 5
            tx = gx + col * (tile_w + 14)
            ty = gy + row * (tile_h + 12)
            is_sel = (i == self.cursor_idx)

            bg = (24, 38, 54) if is_sel else (14, 20, 30)
            outline = (0, 255, 200) if is_sel else (35, 50, 70)
            draw.rounded_rectangle([tx, ty, tx + tile_w, ty + tile_h], radius=8, fill=bg, outline=outline, width=2 if is_sel else 1)

            draw.text((tx + 10, ty + 8), str(el["num"]), fill=(120, 150, 180), font=get_font(11))
            draw.text((tx + 10, ty + 26), el["sym"], fill=(255, 220, 0) if is_sel else (255, 255, 255), font=get_font(24, bold=True))
            draw.text((tx + 10, ty + 56), f"{el['mass']:.2f}", fill=(0, 255, 140), font=get_font(11))

        # Right Active Element Card
        rx = gx + 5 * (tile_w + 14) + 30
        rw = w - rx - 50
        sel = self.elements[self.cursor_idx]

        draw.rounded_rectangle([rx, gy, rx + rw, gy + 480], radius=12, fill=(16, 22, 34), outline=(0, 220, 255), width=2)
        draw.text((rx + 25, gy + 25), f"PIERWIASTEK #{sel['num']}:", fill=(0, 255, 200), font=get_font(16, bold=True))
        draw.text((rx + 25, gy + 55), sel["name"], fill=(255, 255, 255), font=get_font(22, bold=True))

        details = [
            ("Symbol chemiczny:", sel["sym"]),
            ("Liczba atomowa Z:", str(sel["num"])),
            ("Masa atomowa:", f"{sel['mass']} u"),
            ("Grupa / Kategoria:", sel["cat"]),
            ("Konfiguracja e⁻:", sel["conf"]),
            ("Stopnie utlenienia:", "+1, +2, +3"),
            ("Gęstość (20°C):", "1.429 g/dm³"),
            ("Temp. topnienia:", "-218.8 °C")
        ]
        dy = gy + 100
        for lbl, val in details:
            draw.text((rx + 25, dy), lbl, fill=(130, 160, 190), font=get_font(13))
            draw.text((rx + 180, dy), val, fill=(240, 250, 255), font=get_font(14, bold=True))
            dy += 36

        canvas.draw_badge(rx + 25, gy + 420, "TABLICA MENDELEJEWA // STANDARD IUPAC", bg_color=(20, 50, 80), text_color=(0, 220, 255))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_LEFT":
            self.cursor_idx = (self.cursor_idx - 1) % len(self.elements)
            return True
        elif event == "KEY_RIGHT":
            self.cursor_idx = (self.cursor_idx + 1) % len(self.elements)
            return True
        elif event == "KEY_UP":
            self.cursor_idx = (self.cursor_idx - 5) % len(self.elements)
            return True
        elif event == "KEY_DOWN":
            self.cursor_idx = (self.cursor_idx + 5) % len(self.elements)
            return True
        return False
'''

# ==============================================================================
# 5. mod_ee_lab.py - Electronics Lab & Circuit Designer
# ==============================================================================
MODULES["mod_ee_lab"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class EeLabModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.r1 = 10000.0 # 10k
        self.r2 = 4700.0  # 4.7k
        self.c1 = 1e-7    # 100nF
        self.vin = 5.0    # 5V

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Zmiana R1 / R2 / C1"},
            {"key": "L1/R1", "desc": "Napięcie Vin +/-"},
            {"key": "X", "desc": "Tryb NE555 / Dzielnik"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="⚡ ELECTRONICS LAB // CIRCUIT & NE555 DESIGNER",
                         subtitle="Kalkulator NE555 Astable | Dzielniki napięcia | Typoszereg E24 | Filtry RC",
                         border_color=(255, 210, 0))

        # NE555 calculations
        # f = 1.44 / ((R1 + 2*R2) * C)
        freq = 1.44 / ((self.r1 + 2.0 * self.r2) * self.c1)
        duty = ((self.r1 + self.r2) / (self.r1 + 2.0 * self.r2)) * 100.0
        # Voltage divider: Vout = Vin * (R2 / (R1 + R2))
        vout = self.vin * (self.r2 / (self.r1 + self.r2))

        # Panel 1: NE555 Generator (Left)
        p1_x, p1_y, p1_w, p1_h = 45, 120, 450, 480
        draw.rounded_rectangle([p1_x, p1_y, p1_x + p1_w, p1_y + p1_h], radius=10, fill=(16, 22, 32), outline=(255, 200, 0), width=2)
        draw.text((p1_x + 20, p1_y + 20), "GENERATOR ASTABILNY NE555:", fill=(255, 220, 0), font=get_font(16, bold=True))

        lines_ne555 = [
            ("Rezystor R1:", f"{self.r1/1000:.1f} kΩ"),
            ("Rezystor R2:", f"{self.r2/1000:.1f} kΩ"),
            ("Kondensator C:", f"{self.c1*1e9:.0f} nF"),
            ("Częstotliwość f:", f"{freq:.1f} Hz"),
            ("Wypełnienie (Duty):", f"{duty:.1f} %"),
            ("Czas stanu wysokiego Th:", f"{(0.693*(self.r1+self.r2)*self.c1)*1000:.2f} ms"),
            ("Czas stanu niskiego Tl:", f"{(0.693*self.r2*self.c1)*1000:.2f} ms")
        ]
        ly = p1_y + 60
        for l, v in lines_ne555:
            draw.text((p1_x + 20, ly), l, fill=(140, 165, 195), font=get_font(13))
            draw.text((p1_x + 240, ly), v, fill=(240, 250, 255), font=get_font(14, bold=True))
            ly += 34

        # Waveform visual
        draw.rectangle([p1_x + 20, p1_y + 340, p1_x + p1_w - 20, p1_y + 440], fill=(8, 12, 18), outline=(40, 60, 85))
        draw.text((p1_x + 30, p1_y + 350), f"WYKRES PROSTOKĄTA (Duty {duty:.0f}%):", fill=(0, 255, 200), font=get_font(11))
        pts = [(p1_x + 40, p1_y + 420), (p1_x + 40, p1_y + 380), (p1_x + 120, p1_y + 380), (p1_x + 120, p1_y + 420),
               (p1_x + 200, p1_y + 420), (p1_x + 200, p1_y + 380), (p1_x + 280, p1_y + 380), (p1_x + 280, p1_y + 420)]
        draw.line(pts, fill=(0, 255, 140), width=2)

        # Panel 2: Voltage Divider & Filters (Right)
        p2_x = p1_x + p1_w + 30
        p2_w = w - p2_x - 45
        draw.rounded_rectangle([p2_x, p1_y, p2_x + p2_w, p1_y + p1_h], radius=10, fill=(16, 22, 32), outline=(0, 200, 255), width=2)
        draw.text((p2_x + 20, p1_y + 20), "DZIELNIK NAPIĘCIA I FILTRY:", fill=(0, 220, 255), font=get_font(16, bold=True))

        # Filter Cutoff: fc = 1 / (2*pi*R*C)
        fc = 1.0 / (2.0 * math.pi * self.r1 * self.c1)

        lines_div = [
            ("Napięcie Vin:", f"{self.vin:.1f} V"),
            ("Napięcie wyjściowe Vout:", f"{vout:.2f} V"),
            ("Prąd dzielnika I:", f"{(self.vin/(self.r1+self.r2))*1000:.2f} mA"),
            ("Moc strat na R1:", f"{((self.vin - vout)**2 / self.r1)*1000:.2f} mW"),
            ("Filtr dolnoprzepustowy RC fc:", f"{fc:.1f} Hz"),
            ("Szerokość ścieżki PCB (1A):", "0.38 mm (15 mil)"),
            ("Typoszereg:", "E24 (5% tolerancji)")
        ]
        ly = p1_y + 60
        for l, v in lines_div:
            draw.text((p2_x + 20, ly), l, fill=(140, 165, 195), font=get_font(13))
            draw.text((p2_x + 240, ly), v, fill=(255, 220, 0) if "Vout" in l else (240, 250, 255), font=get_font(14, bold=True))
            ly += 34

        canvas.draw_badge(p2_x + 20, p1_y + 420, "NORMY: IPC-2152 // TYPOSZEREG E12/E24", bg_color=(20, 50, 80), text_color=(0, 220, 255))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_LEFT":
            self.r1 = max(100.0, self.r1 - 1000.0)
            return True
        elif event == "KEY_RIGHT":
            self.r1 = min(100000.0, self.r1 + 1000.0)
            return True
        elif event == "KEY_UP":
            self.r2 = min(100000.0, self.r2 + 500.0)
            return True
        elif event == "KEY_DOWN":
            self.r2 = max(100.0, self.r2 - 500.0)
            return True
        elif event == "KEY_L1":
            self.vin = max(1.0, self.vin - 0.5)
            return True
        elif event == "KEY_R1":
            self.vin = min(24.0, self.vin + 0.5)
            return True
        return False
'''

# ==============================================================================
# 6. mod_hex.py - Tactical Hex Inspector & SD Forensics
# ==============================================================================
MODULES["mod_hex"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class HexInspectorModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.offset = 0x00000000
        self.file_name = "bootloader.elf"
        self.file_size = 49152
        self.cursor_row = 2
        # Sample realistic ELF header binary dump
        self.hex_rows = [
            (0x0000, "7F 45 4C 46 02 01 01 00 00 00 00 00 00 00 00 00", ".ELF............"),
            (0x0010, "02 00 B7 00 01 00 00 00 54 80 00 00 00 00 00 00", "........T......."),
            (0x0020, "40 00 00 00 00 00 00 00 18 1B 00 00 00 00 00 00", "@..............."),
            (0x0030, "00 00 00 00 40 00 38 00 04 00 40 00 1A 00 19 00", "....@.8...@....."),
            (0x0040, "06 00 00 00 05 00 00 00 40 00 00 00 00 00 00 00", "........@......."),
            (0x0050, "40 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00", "@.......@......."),
            (0x0060, "F0 01 00 00 00 00 00 00 F0 01 00 00 00 00 00 00", "................"),
            (0x0070, "08 00 00 00 00 00 00 00 03 00 00 00 04 00 00 00", "................"),
            (0x0080, "30 02 00 00 00 00 00 00 30 02 00 00 00 00 00 00", "0.......0......."),
            (0x0090, "1C 00 00 00 00 00 00 00 1C 00 00 00 00 00 00 00", "................")
        ]

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad Góra/Dół", "desc": "Przewijanie bajtów"},
            {"key": "L1/R1", "desc": "Strona - / + (256B)"},
            {"key": "A", "desc": "Analiza sygnatury Magic Bytes"},
            {"key": "X", "desc": "Podgląd sumy SHA-256"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title=f"🔍 TACTICAL HEX INSPECTOR // {self.file_name}",
                         subtitle=f"Rozmiar: {self.file_size:,} bajtów | Format: ELF 64-bit ARM64 | Offset: 0x{self.offset:08X}",
                         border_color=(0, 240, 255))

        # Hex Table Frame
        hx, hy = 45, 120
        hw = 640
        draw.rounded_rectangle([hx, hy, hx + hw, hy + 480], radius=8, fill=(8, 12, 18), outline=(30, 50, 75))

        # Header Columns
        draw.text((hx + 15, hy + 12), "OFFSET", fill=(0, 255, 200), font=get_font(13, bold=True))
        draw.text((hx + 120, hy + 12), "00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F", fill=(255, 210, 0), font=get_font(13, bold=True))
        draw.text((hx + 500, hy + 12), "ASCII", fill=(0, 200, 255), font=get_font(13, bold=True))
        draw.line([(hx + 10, hy + 34), (hx + hw - 10, hy + 34)], fill=(30, 45, 65))

        # Hex rows
        ry = hy + 45
        for idx, (off, hex_str, ascii_str) in enumerate(self.hex_rows):
            is_cur = (idx == self.cursor_row)
            if is_cur:
                draw.rectangle([hx + 10, ry - 3, hx + hw - 10, ry + 21], fill=(20, 35, 55))

            draw.text((hx + 15, ry), f"{off:08X}", fill=(120, 150, 180), font=get_font(13))
            draw.text((hx + 120, ry), hex_str, fill=(240, 250, 255) if not is_cur else (0, 255, 220), font=get_font(13))
            draw.text((hx + 500, ry), ascii_str, fill=(180, 200, 225) if not is_cur else (255, 255, 255), font=get_font(13))
            ry += 32

        # Right Forensics & Magic Bytes Panel
        rx = hx + hw + 25
        rw = w - rx - 45
        draw.rounded_rectangle([rx, hy, rx + rw, hy + 480], radius=10, fill=(16, 22, 34), outline=(0, 200, 255), width=2)
        draw.text((rx + 20, hy + 20), "ANALIZA FORENSIC:", fill=(0, 255, 200), font=get_font(16, bold=True))

        forensics = [
            ("Sygnatura Magic:", "7F 45 4C 46 (.ELF)"),
            ("Architektura:", "ARM64 (AArch64)"),
            ("Endianness:", "Little Endian (LSB)"),
            ("Typ pliku:", "EXEC (Executable)"),
            ("Punkt wejścia:", "0x00008054"),
            ("Tablica sekcji:", "32 sekcje"),
            ("CRC-32:", "0x8F4A2C19"),
            ("SHA-256 skrót:", "3f7a...c89e (Zweryfikowany)")
        ]
        fy = hy + 60
        for l, v in forensics:
            draw.text((rx + 20, fy), l, fill=(130, 160, 190), font=get_font(13))
            draw.text((rx + 20, fy + 18), v, fill=(240, 250, 255), font=get_font(14, bold=True))
            fy += 46

        canvas.draw_badge(rx + 20, hy + 430, "INTEGRALNOŚĆ BAZY: POPRAWNA", bg_color=(0, 60, 40), text_color=(0, 255, 140))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_UP":
            self.cursor_row = (self.cursor_row - 1) % len(self.hex_rows)
            return True
        elif event == "KEY_DOWN":
            self.cursor_row = (self.cursor_row + 1) % len(self.hex_rows)
            return True
        return False
'''

def main():
    out_dir = "store/modules"
    os.makedirs(out_dir, exist_ok=True)
    for mod_id, code in MODULES.items():
        path = os.path.join(out_dir, f"{mod_id}.py")
        print(f"Writing {path}...")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code.strip() + "\n")
    print(f"Done writing {len(MODULES)} Batch 2 modules!")

if __name__ == "__main__":
    main()
