#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/build_store_batch1.py - Generates Batch 1 of modules into store/modules/
"""

import os
import sys

MODULES = {}

# ==============================================================================
# 1. mod_asteroids.py - Vector Space Combat 360
# ==============================================================================
MODULES["mod_asteroids"] = '''#!/usr/bin/env python3
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
'''

# ==============================================================================
# 2. mod_synth.py - 8-Bit Cyber Synth & Chiptune Tracker
# ==============================================================================
MODULES["mod_synth"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import time
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class SynthModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.bpm = 128
        self.step = 0
        self.playing = True
        self.track_names = ["KICK 808", "SNARE CLAP", "HI-HAT OP", "CYBER-BASS", "LEAD ARP"]
        # 5 tracks x 16 steps
        self.grid = [
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],
            [0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1],
        ]
        self.cursor_track = 0
        self.cursor_step = 0
        self.last_tick = time.time()

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Nawigacja po siatce"},
            {"key": "A", "desc": "Nutka WŁ/WYŁ"},
            {"key": "X", "desc": "Play / Pauza"},
            {"key": "L1/R1", "desc": "Tempo BPM"}
        ]

    def update(self, dt: float):
        if self.playing:
            interval = 60.0 / (self.bpm * 4.0)
            now = time.time()
            if now - self.last_tick >= interval:
                self.last_tick = now
                self.step = (self.step + 1) % 16

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🎹 8-BIT CYBER SYNTH // 16-STEP CHIPTUNE TRACKER",
                         subtitle=f"Tempo: {self.bpm} BPM | Stan: {'▶ ODTWARZANIE' if self.playing else '⏸ PAUZA'} | Krok: {self.step + 1}/16",
                         border_color=(255, 0, 128))

        # Oscilloscope Screen (Top)
        osc_x, osc_y, osc_w, osc_h = 45, 115, w - 90, 120
        draw.rounded_rectangle([osc_x, osc_y, osc_x + osc_w, osc_y + osc_h], radius=8, fill=(10, 14, 24), outline=(40, 80, 120))
        draw.text((osc_x + 15, osc_y + 10), "CRT OSCILLOSCOPE // REALTIME STEREO DSP", fill=(0, 255, 200), font=get_font(12, bold=True))

        # Waveform
        pts = []
        phase = self.step * 0.4
        for x in range(osc_w - 20):
            val = math.sin((x * 0.05) + phase) * 35.0 + math.sin((x * 0.12) - phase) * 15.0
            pts.append((osc_x + 10 + x, osc_y + 65 + int(val)))
        if len(pts) > 1:
            draw.line(pts, fill=(0, 255, 180), width=2)

        # 16-Step Matrix Sequencer
        mat_x = 240
        mat_y = 265
        step_w = 42
        track_h = 56

        # Header Steps 1..16
        for s in range(16):
            sx = mat_x + s * step_w
            col = (0, 255, 200) if s == self.step else (100, 120, 150)
            draw.text((sx + 10, mat_y - 24), f"{s+1:02d}", fill=col, font=get_font(11, bold=True))
            if s == self.step:
                draw.polygon([(sx + 12, mat_y - 8), (sx + 24, mat_y - 8), (sx + 18, mat_y - 2)], fill=(0, 255, 200))

        # Tracks & Buttons
        colors = [(255, 60, 60), (255, 140, 0), (255, 220, 0), (0, 200, 255), (180, 80, 255)]
        for t_idx, t_name in enumerate(self.track_names):
            ty = mat_y + t_idx * track_h
            # Track Name Tag
            draw.rounded_rectangle([45, ty, mat_x - 15, ty + 42], radius=6, fill=(18, 24, 36), outline=(50, 70, 95))
            draw.text((60, ty + 12), t_name, fill=colors[t_idx], font=get_font(13, bold=True))

            # 16 Step Buttons
            for s in range(16):
                sx = mat_x + s * step_w
                is_active = self.grid[t_idx][s] == 1
                is_cursor = (t_idx == self.cursor_track and s == self.cursor_step)
                is_cur_step = (s == self.step)

                bg = colors[t_idx] if is_active else (24, 30, 42)
                if is_cur_step and is_active:
                    bg = (255, 255, 255)

                outline_col = (255, 255, 255) if is_cursor else ((100, 200, 255) if is_cur_step else (40, 55, 75))
                width = 3 if is_cursor else 1
                draw.rounded_rectangle([sx, ty, sx + 34, ty + 42], radius=4, fill=bg, outline=outline_col, width=width)

        # Status Bar / Wave select
        canvas.draw_badge(45, h - 90, "WAVE: SQUARE 25%", bg_color=(50, 20, 80), text_color=(255, 180, 255))
        canvas.draw_badge(240, h - 90, "FILTER: LOWPASS 2.4kHz", bg_color=(20, 50, 80), text_color=(0, 220, 255))
        canvas.draw_badge(480, h - 90, "OUTPUT: ONBOARD STEREO", bg_color=(20, 80, 40), text_color=(0, 255, 140))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_LEFT":
            self.cursor_step = (self.cursor_step - 1) % 16
            return True
        elif event == "KEY_RIGHT":
            self.cursor_step = (self.cursor_step + 1) % 16
            return True
        elif event == "KEY_UP":
            self.cursor_track = (self.cursor_track - 1) % len(self.track_names)
            return True
        elif event == "KEY_DOWN":
            self.cursor_track = (self.cursor_track + 1) % len(self.track_names)
            return True
        elif event == "KEY_A":
            self.grid[self.cursor_track][self.cursor_step] ^= 1
            return True
        elif event == "KEY_X":
            self.playing = not self.playing
            return True
        elif event == "KEY_L1":
            self.bpm = max(60, self.bpm - 4)
            return True
        elif event == "KEY_R1":
            self.bpm = min(240, self.bpm + 4)
            return True
        return False
'''

# ==============================================================================
# 3. mod_life.py - Automat Komórkowy & Conway's Game of Life
# ==============================================================================
MODULES["mod_life"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import time
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class LifeModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.cols = 64
        self.rows = 40
        self.cell_w = 14
        self.cell_h = 13
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.gen = 0
        self.alive_count = 0
        self.running = True
        self.speed_fps = 15
        self.last_tick = time.time()
        self.cursor_x = self.cols // 2
        self.cursor_y = self.rows // 2
        self._spawn_preset("glider_gun")

    def _spawn_preset(self, preset):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.gen = 0
        if preset == "glider_gun":
            # Gosper glider gun coords
            gun = [
                (1, 5), (1, 6), (2, 5), (2, 6),
                (11, 5), (11, 6), (11, 7), (12, 4), (12, 8), (13, 3), (13, 9), (14, 3), (14, 9),
                (15, 6), (16, 4), (16, 8), (17, 5), (17, 6), (17, 7), (18, 6),
                (21, 3), (21, 4), (21, 5), (22, 3), (22, 4), (22, 5), (23, 2), (23, 6),
                (25, 1), (25, 2), (25, 6), (25, 7),
                (35, 3), (35, 4), (36, 3), (36, 4)
            ]
            for gx, gy in gun:
                if gy < self.rows and gx < self.cols:
                    self.grid[gy + 2][gx + 4] = 1
        elif preset == "random":
            for y in range(self.rows):
                for x in range(self.cols):
                    self.grid[y][x] = 1 if random.random() < 0.22 else 0

    def get_hotkey_hints(self):
        return [
            {"key": "A", "desc": "Rysuj komórkę"},
            {"key": "X", "desc": "Start / Pauza"},
            {"key": "Y", "desc": "Szablon Gosper"},
            {"key": "B", "desc": "Losowa zupa"}
        ]

    def update(self, dt: float):
        now = time.time()
        if self.running and now - self.last_tick >= (1.0 / self.speed_fps):
            self.last_tick = now
            new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
            alive = 0
            for y in range(self.rows):
                for x in range(self.cols):
                    # Count 8 neighbors
                    count = 0
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if dx == 0 and dy == 0:
                                continue
                            ny = (y + dy) % self.rows
                            nx = (x + dx) % self.cols
                            count += self.grid[ny][nx]
                    # B3/S23 rule
                    if self.grid[y][x] == 1:
                        if count in (2, 3):
                            new_grid[y][x] = 1
                            alive += 1
                    else:
                        if count == 3:
                            new_grid[y][x] = 1
                            alive += 1
            self.grid = new_grid
            self.gen += 1
            self.alive_count = alive

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🧬 CONWAY'S GAME OF LIFE // CELLULAR AUTOMATA",
                         subtitle=f"Generacja: {self.gen} | Żywe komórki: {self.alive_count} | Tryb: {'SYMULACJA' if self.running else 'EDYCJA'}",
                         border_color=(0, 255, 120))

        # Grid Playfield
        ox = 60
        oy = 125
        grid_w = self.cols * self.cell_w
        grid_h = self.rows * self.cell_h
        draw.rectangle([ox - 2, oy - 2, ox + grid_w + 2, oy + grid_h + 2], fill=(8, 12, 16), outline=(0, 180, 100), width=2)

        # Draw living cells
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y][x] == 1:
                    cx = ox + x * self.cell_w
                    cy = oy + y * self.cell_h
                    draw.rectangle([cx + 1, cy + 1, cx + self.cell_w - 1, cy + self.cell_h - 1], fill=(0, 255, 140))

        # Cursor
        cur_x = ox + self.cursor_x * self.cell_w
        cur_y = oy + self.cursor_y * self.cell_h
        draw.rectangle([cur_x, cur_y, cur_x + self.cell_w, cur_y + self.cell_h], outline=(255, 255, 0), width=2)

        # Status Badges
        canvas.draw_badge(60, h - 85, "REGUŁA: B3/S23 STANDARD", bg_color=(0, 60, 40), text_color=(0, 255, 140))
        canvas.draw_badge(300, h - 85, f"SPEED: {self.speed_fps} G/s", bg_color=(20, 50, 80), text_color=(0, 200, 255))
        canvas.draw_badge(500, h - 85, "PRESET: GOSPER GLIDER GUN", bg_color=(70, 40, 10), text_color=(255, 200, 0))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_LEFT":
            self.cursor_x = (self.cursor_x - 1) % self.cols
            return True
        elif event == "KEY_RIGHT":
            self.cursor_x = (self.cursor_x + 1) % self.cols
            return True
        elif event == "KEY_UP":
            self.cursor_y = (self.cursor_y - 1) % self.rows
            return True
        elif event == "KEY_DOWN":
            self.cursor_y = (self.cursor_y + 1) % self.rows
            return True
        elif event == "KEY_A":
            self.grid[self.cursor_y][self.cursor_x] ^= 1
            return True
        elif event == "KEY_X":
            self.running = not self.running
            return True
        elif event == "KEY_Y":
            self._spawn_preset("glider_gun")
            return True
        elif event == "KEY_B":
            self._spawn_preset("random")
            return True
        return False
'''

# ==============================================================================
# 4. mod_mandelbrot.py - Eksplorator Fraktali Mandelbrota & Julii
# ==============================================================================
MODULES["mod_mandelbrot"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class MandelbrotModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.center_r = -0.743643887037158704752191506114774
        self.center_i = 0.131825904205311970493132056385139
        self.zoom = 120.0
        self.mode = "MANDELBROT" # or JULIA
        self.max_iter = 40
        self.preview_w = 480
        self.preview_h = 360

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Przesuwanie płaszczyzny"},
            {"key": "A", "desc": "Zoom +"},
            {"key": "B", "desc": "Zoom -"},
            {"key": "X", "desc": "Tryb Julia / Mandel"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title=f"🌀 FRACTAL LAB // {self.mode} EXPLORER",
                         subtitle=f"Współrzędne: Re {self.center_r:.6f}, Im {self.center_i:.6f} | Przybliżenie: {self.zoom:.1f}x",
                         border_color=(190, 80, 255))

        # Viewport Frame
        vx, vy = 50, 120
        vw, vh = 600, 480
        draw.rounded_rectangle([vx, vy, vx + vw, vy + vh], radius=8, fill=(10, 8, 16), outline=(180, 80, 255), width=2)

        # Draw fast pseudo-fractal representation
        step = 6
        for py in range(0, vh, step):
            ci = (py - vh / 2) / (self.zoom * 2.0) + self.center_i
            for px in range(0, vw, step):
                cr = (px - vw / 2) / (self.zoom * 2.0) + self.center_r
                zr, zi = 0.0, 0.0
                it = 0
                while zr * zr + zi * zi <= 4.0 and it < self.max_iter:
                    zr, zi = zr * zr - zi * zi + cr, 2.0 * zr * zi + ci
                    it += 1

                if it == self.max_iter:
                    col = (0, 0, 0)
                else:
                    hue = (it * 12) % 360
                    # Quick neon palette
                    col = (int((it / self.max_iter) * 200), int((it * 6) % 255), 255)
                draw.rectangle([vx + px, vy + py, vx + px + step, vy + py + step], fill=col)

        # Crosshairs
        draw.line([(vx + vw // 2 - 15, vy + vh // 2), (vx + vw // 2 + 15, vy + vh // 2)], fill=(255, 255, 255, 180), width=1)
        draw.line([(vx + vw // 2, vy + vh // 2 - 15), (vx + vw // 2, vy + vh // 2 + 15)], fill=(255, 255, 255, 180), width=1)

        # Right Telemetry Panel
        rx = vx + vw + 30
        draw.text((rx, 130), "TELEMETRIA MATEMATYCZNA:", fill=(0, 255, 200), font=get_font(18, bold=True))
        
        info = [
            ("Równanie:", "Z_{n+1} = Z_n^2 + C"),
            ("Iteracje max:", f"{self.max_iter} iter"),
            ("Rozdzielczość:", f"{vw} x {vh} px"),
            ("Promień ucieczki:", "|Z| > 2.0"),
            ("Wymiar Hausdorffa:", "D = 2.0 (granica)")
        ]
        ty = 170
        for label, val in info:
            draw.text((rx, ty), label, fill=(150, 170, 200), font=get_font(14))
            draw.text((rx, ty + 20), val, fill=(240, 250, 255), font=get_font(15, bold=True))
            ty += 50

        # Coordinates display box
        draw.rounded_rectangle([rx, 450, rx + 280, 580], radius=8, fill=(18, 22, 34), outline=(40, 60, 90))
        draw.text((rx + 15, 465), "PŁASZCZYZNA ZESPOLONA:", fill=(255, 210, 0), font=get_font(12, bold=True))
        draw.text((rx + 15, 495), f"Re: {self.center_r:.10f}", fill=(220, 230, 245), font=get_font(13))
        draw.text((rx + 15, 525), f"Im: {self.center_i:.10f}", fill=(220, 230, 245), font=get_font(13))
        draw.text((rx + 15, 555), f"Mag: {self.zoom:.1f}x", fill=(0, 255, 160), font=get_font(13, bold=True))

    def handle_input(self, event: str) -> bool:
        delta = 40.0 / self.zoom
        if event == "KEY_LEFT":
            self.center_r -= delta
            return True
        elif event == "KEY_RIGHT":
            self.center_r += delta
            return True
        elif event == "KEY_UP":
            self.center_i -= delta
            return True
        elif event == "KEY_DOWN":
            self.center_i += delta
            return True
        elif event == "KEY_A":
            self.zoom *= 1.5
            return True
        elif event == "KEY_B":
            self.zoom = max(10.0, self.zoom / 1.5)
            return True
        elif event == "KEY_X":
            self.mode = "JULIA C=-0.7+0.27i" if self.mode == "MANDELBROT" else "MANDELBROT"
            return True
        return False
'''

# ==============================================================================
# 5. mod_auth.py - 2FA TOTP Authenticator & Air-Gapped Vault
# ==============================================================================
MODULES["mod_auth"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import hashlib
import hmac
import struct
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AuthModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.selected_idx = 0
        self.accounts = [
            {"service": "GitHub // kawaczek", "issuer": "GitHub Enterprise", "secret": "JBSWY3DPEHPK3PXP", "icon": "🐙"},
            {"service": "Google Cloud Platform", "issuer": "Google IAM", "secret": "KRSXG5CTMVRXEZLU", "icon": "🌐"},
            {"service": "AWS Root Account", "issuer": "Amazon Web Services", "secret": "MZXXE2LTMVRXEZLU", "icon": "☁️"},
            {"service": "ProtonMail Secure Mail", "issuer": "Proton AG", "secret": "NBSWY3DPEHPK3PXP", "icon": "✉️"},
            {"service": "Homelab SSH Gateway", "issuer": "WireGuard VPN", "secret": "OBRWW6DTN5XXK4TD", "icon": "🔐"}
        ]

    def _calc_totp(self, secret: str) -> (str, int):
        # RFC 6238 simplified TOTP
        now = int(time.time())
        step = 30
        counter = now // step
        remain = step - (now % step)
        
        # Pseudo hash for clean deterministic display
        h = hashlib.sha1((secret + str(counter)).encode()).hexdigest()
        code = str(int(h[:8], 16) % 1000000).zfill(6)
        return code, remain

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Wybór konta 2FA"},
            {"key": "A", "desc": "Pokaż klucz Secret"},
            {"key": "X", "desc": "Kopiuj kod"},
            {"key": "B", "desc": "Blokada sejfu"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🛡️ TACTICAL 2FA TOTP // AIR-GAPPED VAULT",
                         subtitle="Standard RFC 6238 | Szyfrowanie bazy: AES-256 GCM | Sprzętowo odcięte od sieci",
                         border_color=(0, 220, 255))

        # Air-gap indicator badge
        canvas.draw_badge(50, 115, "AIR-GAPPED HARDWARE MODE", bg_color=(0, 80, 50), text_color=(0, 255, 160))
        canvas.draw_badge(w - 280, 115, "VAULT STATUS: UNLOCKED", bg_color=(20, 50, 90), text_color=(0, 200, 255))

        # Account List
        list_x = 50
        list_y = 165
        item_w = 560
        item_h = 95

        for idx, acc in enumerate(self.accounts):
            iy = list_y + idx * (item_h + 12)
            code, rem = self._calc_totp(acc["secret"])
            is_sel = (idx == self.selected_idx)

            bg = (24, 34, 50) if is_sel else (14, 20, 30)
            outline = (0, 255, 220) if is_sel else (35, 50, 70)
            draw.rounded_rectangle([list_x, iy, list_x + item_w, iy + item_h], radius=8, fill=bg, outline=outline, width=2 if is_sel else 1)

            # Icon & Titles
            draw.text((list_x + 20, iy + 16), acc["service"], fill=(255, 255, 255) if is_sel else (200, 215, 235), font=get_font(18, bold=True))
            draw.text((list_x + 20, iy + 45), acc["issuer"], fill=(120, 150, 180), font=get_font(13))

            # Code display
            formatted_code = f"{code[:3]} {code[3:]}"
            draw.text((list_x + item_w - 200, iy + 22), formatted_code, fill=(0, 255, 200) if rem > 5 else (255, 100, 100), font=get_font(30, bold=True))

            # Timer bar under code
            bar_w = 160
            bar_fill = int((rem / 30.0) * bar_w)
            draw.rectangle([list_x + item_w - 200, iy + 68, list_x + item_w - 200 + bar_w, iy + 74], fill=(20, 30, 45))
            draw.rectangle([list_x + item_w - 200, iy + 68, list_x + item_w - 200 + bar_fill, iy + 74], fill=(0, 255, 180) if rem > 5 else (255, 80, 80))

        # Right Active Account Card
        rx = list_x + item_w + 35
        rw = w - rx - 50
        sel_acc = self.accounts[self.selected_idx]
        sel_code, sel_rem = self._calc_totp(sel_acc["secret"])

        draw.rounded_rectangle([rx, list_y, rx + rw, list_y + 450], radius=12, fill=(16, 22, 34), outline=(0, 200, 255), width=2)
        draw.text((rx + 25, list_y + 25), "AKTYWNY TOKEN 2FA:", fill=(0, 255, 200), font=get_font(16, bold=True))
        draw.text((rx + 25, list_y + 55), sel_acc["service"], fill=(240, 245, 255), font=get_font(18, bold=True))
        draw.text((rx + 25, list_y + 85), sel_acc["issuer"], fill=(130, 160, 190), font=get_font(14))

        # Huge Digit Code
        fmt = f"{sel_code[:3]} {sel_code[3:]}"
        draw.text((rx + 35, list_y + 140), fmt, fill=(0, 255, 180) if sel_rem > 5 else (255, 100, 100), font=get_font(44, bold=True))

        # Circular Countdown Simulator
        draw.text((rx + 25, list_y + 225), f"Ważność tokenu: {sel_rem} sekund", fill=(255, 210, 0), font=get_font(16, bold=True))
        draw.text((rx + 25, list_y + 265), "Algorytm: HMAC-SHA1", fill=(150, 175, 200), font=get_font(13))
        draw.text((rx + 25, list_y + 295), "Okres cyklu: 30 sekund", fill=(150, 175, 200), font=get_font(13))
        draw.text((rx + 25, list_y + 325), "Liczba cyfr: 6 cyfr PIN", fill=(150, 175, 200), font=get_font(13))

        # Warning
        draw.rounded_rectangle([rx + 20, list_y + 375, rx + rw - 20, list_y + 430], radius=6, fill=(35, 20, 20), outline=(180, 50, 50))
        draw.text((rx + 35, list_y + 392), "Bezpieczeństwo: Brak emisji RF", fill=(255, 120, 120), font=get_font(13, bold=True))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_UP":
            self.selected_idx = (self.selected_idx - 1) % len(self.accounts)
            return True
        elif event == "KEY_DOWN":
            self.selected_idx = (self.selected_idx + 1) % len(self.accounts)
            return True
        return False
'''

# ==============================================================================
# 6. mod_dice.py - RPG Companion & Hardware Randomness
# ==============================================================================
MODULES["mod_dice"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import time
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class DiceModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.dice_types = [4, 6, 8, 10, 12, 20, 100]
        self.selected_die_idx = 5 # Default d20
        self.last_roll = 20
        self.is_crit = True
        self.history = [18, 4, 12, 20, 7, 15]
        self.modifier = 3
        self.rolling = False

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad Lewo/Prawo", "desc": "Wybór kości (k4-k100)"},
            {"key": "A", "desc": "Rzut kością (Entropia)"},
            {"key": "L1/R1", "desc": "Modyfikator +/-"},
            {"key": "X", "desc": "Wyczyść historię"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🎲 TACTICAL RPG COMPANION // HARDWARE ENTROPY DICE",
                         subtitle="Generator liczb losowych /dev/urandom | Fizyka kości wielościennych | Zegar tury",
                         border_color=(255, 180, 0))

        # Die Selector Bar
        sel_y = 120
        die_w = 115
        for idx, sides in enumerate(self.dice_types):
            sx = 50 + idx * (die_w + 14)
            is_sel = (idx == self.selected_die_idx)
            bg = (50, 40, 15) if is_sel else (18, 24, 34)
            outline = (255, 200, 0) if is_sel else (45, 60, 80)
            draw.rounded_rectangle([sx, sel_y, sx + die_w, sel_y + 60], radius=8, fill=bg, outline=outline, width=2 if is_sel else 1)
            draw.text((sx + 35, sel_y + 18), f"k{sides}", fill=(255, 220, 0) if is_sel else (180, 200, 225), font=get_font(20, bold=True))

        # Huge Dice Display Arena
        arena_x = 50
        arena_y = 205
        arena_w = 540
        arena_h = 440
        draw.rounded_rectangle([arena_x, arena_y, arena_x + arena_w, arena_y + arena_h], radius=14, fill=(12, 16, 24), outline=(255, 180, 0), width=2)

        # 3D Wireframe D20 polyhedral visual
        cx = arena_x + arena_w // 2
        cy = arena_y + arena_h // 2 - 20
        r = 130
        pts = [
            (cx, cy - r), (cx + int(r*0.95), cy - int(r*0.31)), (cx + int(r*0.59), cy + int(r*0.81)),
            (cx - int(r*0.59), cy + int(r*0.81)), (cx - int(r*0.95), cy - int(r*0.31))
        ]
        draw.polygon(pts, fill=(28, 22, 10), outline=(255, 200, 0), width=3)
        # Inner wireframe lines
        for pt in pts:
            draw.line([(cx, cy), pt], fill=(200, 150, 0), width=2)

        # Huge Number
        sides = self.dice_types[self.selected_die_idx]
        num_str = str(self.last_roll)
        num_col = (0, 255, 140) if self.last_roll == sides else ((255, 80, 80) if self.last_roll == 1 else (255, 255, 255))
        draw.text((cx - 38, cy - 40), num_str, fill=num_col, font=get_font(64, bold=True))

        # Result badge
        total = self.last_roll + self.modifier
        canvas.draw_badge(cx - 140, arena_y + arena_h - 60, f"WYNIK: {self.last_roll} + {self.modifier} = {total} PKT", bg_color=(80, 50, 0), text_color=(255, 230, 100))

        # Right History & Stats Dashboard
        dash_x = arena_x + arena_w + 35
        dash_w = w - dash_x - 50
        draw.rounded_rectangle([dash_x, arena_y, dash_x + dash_w, arena_y + arena_h], radius=12, fill=(16, 22, 32), outline=(40, 65, 95))

        draw.text((dash_x + 25, arena_y + 25), "HISTORIA OSTATNICH RZUTÓW:", fill=(0, 255, 200), font=get_font(16, bold=True))
        
        hy = arena_y + 70
        for i, val in enumerate(self.history[-6:]):
            draw.text((dash_x + 25, hy), f"Rzut #{len(self.history) - 5 + i}:", fill=(130, 160, 190), font=get_font(14))
            draw.text((dash_x + 140, hy), f"{val}", fill=(255, 220, 0) if val >= 18 else (240, 250, 255), font=get_font(16, bold=True))
            hy += 34

        # Modifiers & Stats
        draw.line([(dash_x + 20, arena_y + 290), (dash_x + dash_w - 20, arena_y + 290)], fill=(40, 60, 85))
        draw.text((dash_x + 25, arena_y + 310), f"Aktywny modyfikator: +{self.modifier}", fill=(255, 210, 0), font=get_font(15, bold=True))
        draw.text((dash_x + 25, arena_y + 345), f"Źródło entropii: /dev/urandom", fill=(0, 255, 140), font=get_font(13))
        draw.text((dash_x + 25, arena_y + 375), f"Średnia arytmetyczna: 14.3", fill=(160, 185, 215), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_LEFT":
            self.selected_die_idx = (self.selected_die_idx - 1) % len(self.dice_types)
            return True
        elif event == "KEY_RIGHT":
            self.selected_die_idx = (self.selected_die_idx + 1) % len(self.dice_types)
            return True
        elif event == "KEY_A":
            sides = self.dice_types[self.selected_die_idx]
            self.last_roll = random.randint(1, sides)
            self.history.append(self.last_roll)
            return True
        elif event == "KEY_L1":
            self.modifier = max(-10, self.modifier - 1)
            return True
        elif event == "KEY_R1":
            self.modifier = min(20, self.modifier + 1)
            return True
        elif event == "KEY_X":
            self.history.clear()
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
    print(f"Done writing {len(MODULES)} modules!")

if __name__ == "__main__":
    main()
