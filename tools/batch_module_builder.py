#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/batch_module_builder.py - Automated Background Module Builder & Publisher
Builds modules from FUTURE_MODULES_IDEAS.md into store/modules/,
generates screenshots, updates store/registry.json, and pushes to GitHub.
Runs silently in the background.
"""

import os
import sys
import time
import json
import subprocess

sys.path.insert(0, os.path.abspath("Apps/BrickDeck"))

# We will define implementations for the queued modules
MODULE_IMPLEMENTATIONS = {}

# 1. mod_tamagotchi.py
MODULE_IMPLEMENTATIONS["mod_tamagotchi"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, random, time
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TamagotchiModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.pet_name = "CYBER-BOT v1"
        self.hunger = 80
        self.happiness = 85
        self.energy = 90
        self.cleanliness = 95
        self.age_cycles = 142
        self.anim_frame = 0
        self.last_tick = time.time()
        self.action_msg = "Twój Cyber-Bot jest zadowolony i czuwa."
        self.selected_action = 0 # 0: Karm, 1: Zabawa, 2: Myj, 3: Sen

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Wybór akcji"},
            {"key": "A", "desc": "Wykonaj"},
            {"key": "X", "desc": "Minigra"},
            {"key": "B", "desc": "Status"}
        ]

    def update(self, dt: float):
        now = time.time()
        if now - self.last_tick > 2.0:
            self.last_tick = now
            self.anim_frame = (self.anim_frame + 1) % 4
            self.hunger = max(0, self.hunger - 1)
            self.energy = max(0, self.energy - 1)

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title=f"👾 CYBERPET // {self.pet_name}", subtitle=f"Wiek: {self.age_cycles} cykli | Poczucie szczęścia: {self.happiness}%", border_color=(0, 255, 180))
        
        # Virtual Pet Screen (CRT Green Monitor)
        scr_x, scr_y, scr_w, scr_h = 50, 120, 520, 480
        draw.rounded_rectangle([scr_x, scr_y, scr_x + scr_w, scr_y + scr_h], radius=12, fill=(8, 16, 12), outline=(0, 255, 120), width=3)
        
        # Animated Pixel Pet Face (Robot / Monster)
        cx = scr_x + scr_w // 2
        cy = scr_y + scr_h // 2 - 20
        bob = int(math.sin(self.anim_frame * math.pi / 2) * 8)
        
        # Head / Body
        draw.rounded_rectangle([cx - 80, cy - 80 + bob, cx + 80, cy + 70 + bob], radius=16, fill=(0, 220, 100), outline=(0, 255, 160), width=4)
        # Antenna
        draw.line([(cx, cy - 80 + bob), (cx, cy - 110 + bob)], fill=(0, 255, 160), width=4)
        draw.ellipse([cx - 10, cy - 130 + bob, cx + 10, cy - 110 + bob], fill=(255, 220, 0))
        # Eyes (Blinking)
        eye_h = 4 if self.anim_frame == 3 else 24
        draw.ellipse([cx - 50, cy - 30 + bob - eye_h//2, cx - 20, cy - 30 + bob + eye_h//2], fill=(8, 16, 12))
        draw.ellipse([cx + 20, cy - 30 + bob - eye_h//2, cx + 50, cy - 30 + bob + eye_h//2], fill=(8, 16, 12))
        # Smile
        draw.arc([cx - 40, cy + 10 + bob, cx + 40, cy + 45 + bob], start=0, end=180, fill=(8, 16, 12), width=5)

        # Right Status Dashboard
        dash_x = scr_x + scr_w + 30
        dash_w = w - dash_x - 50
        
        stats = [
            ("Głód (Bateria)", self.hunger, (0, 220, 255)),
            ("Humor (CPU)", self.happiness, (255, 210, 0)),
            ("Energia (RAM)", self.energy, (0, 255, 120)),
            ("Czystość (Cache)", self.cleanliness, (190, 80, 255)),
        ]
        
        sy = 130
        draw.text((dash_x, sy), "PARAMETRY ŻYCIOWE:", fill=(0, 255, 200), font=get_font(18, bold=True))
        sy += 36
        for label, val, col in stats:
            draw.text((dash_x, sy), f"{label}: {val}%", fill=(220, 230, 245), font=get_font(14, bold=True))
            draw.rectangle([dash_x, sy + 22, dash_x + dash_w, sy + 38], fill=(20, 28, 40), outline=(40, 60, 80))
            fill_len = int(dash_w * (val / 100.0))
            if fill_len > 0:
                draw.rectangle([dash_x, sy + 22, dash_x + fill_len, sy + 38], fill=col)
            sy += 54
            
        # Action Buttons at bottom
        actions = ["🥩 Nakarm", "🎾 Zabawa", "🚿 Wyczyść", "💤 Uśpij"]
        ax = 50
        ay = 618
        btn_w = 220
        for i, act in enumerate(actions):
            is_sel = (i == self.selected_action)
            bg = (0, 140, 80) if is_sel else (18, 26, 36)
            outline = (0, 255, 140) if is_sel else (40, 60, 80)
            draw.rounded_rectangle([ax, ay, ax + btn_w, ay + 42], radius=6, fill=bg, outline=outline, width=2 if is_sel else 1)
            draw.text((ax + 24, ay + 12), act, fill=(255, 255, 255) if is_sel else (160, 180, 200), font=get_font(15, bold=True))
            ax += btn_w + 20

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "KEY_A"):
            self.selected_action = (self.selected_action - 1) % 4
            return True
        elif event in ("KEY_RIGHT", "KEY_D"):
            self.selected_action = (self.selected_action + 1) % 4
            return True
        elif event == "KEY_A":
            if self.selected_action == 0:
                self.hunger = min(100, self.hunger + 25)
            elif self.selected_action == 1:
                self.happiness = min(100, self.happiness + 20)
            elif self.selected_action == 2:
                self.cleanliness = 100
            elif self.selected_action == 3:
                self.energy = 100
            return True
        return False
'''

# 2. mod_pipe_hack.py
MODULE_IMPLEMENTATIONS["mod_pipe_hack"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random, time
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

GRID_SZ = 6

class PipeHackModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.cursor_x = 0
        self.cursor_y = 0
        # 0: I-pipe, 1: L-pipe, 2: T-pipe, 3: Cross
        self.grid = [[random.randint(0, 2) for _ in range(GRID_SZ)] for _ in range(GRID_SZ)]
        self.rotations = [[random.randint(0, 3) for _ in range(GRID_SZ)] for _ in range(GRID_SZ)]
        self.time_left = 45.0
        self.score = 1200
        self.is_connected = False

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Kursor węzła"},
            {"key": "A", "desc": "Obróć złącze"},
            {"key": "X", "desc": "Test sygnału"},
            {"key": "Y", "desc": "Nowa matryca"}
        ]

    def update(self, dt: float):
        if not self.is_connected and self.time_left > 0:
            self.time_left = max(0.0, self.time_left - dt)

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🔌 CIRCUIT CONDUIT // NET PIPE HACK", subtitle=f"Czas impulsu: {int(self.time_left)} s | Punkty: {self.score} | D-Pad: Kursor | [A]: Obrót", border_color=(0, 220, 255))
        
        # Grid Viewport in center
        cell_sz = 80
        start_x = 120
        start_y = 130
        
        draw.rounded_rectangle([start_x - 16, start_y - 16, start_x + GRID_SZ * cell_sz + 16, start_y + GRID_SZ * cell_sz + 16], radius=10, fill=(10, 16, 26), outline=(0, 180, 220), width=2)
        
        for gy in range(GRID_SZ):
            for gx in range(GRID_SZ):
                cx = start_x + gx * cell_sz
                cy = start_y + gy * cell_sz
                is_cur = (gx == self.cursor_x and gy == self.cursor_y)
                
                # Cell plate
                c_bg = (24, 38, 56) if is_cur else (14, 20, 32)
                draw.rectangle([cx, cy, cx + cell_sz - 2, cy + cell_sz - 2], fill=c_bg, outline=(0, 255, 220) if is_cur else (26, 40, 60))
                
                # Draw pipe graphic
                mid_x = cx + cell_sz // 2
                mid_y = cy + cell_sz // 2
                ptype = self.grid[gy][gx]
                rot = self.rotations[gy][gx]
                
                pipe_col = (0, 255, 200) if is_cur else (0, 180, 240)
                if ptype == 0: # Straight line
                    if rot % 2 == 0:
                        draw.line([(mid_x, cy + 8), (mid_x, cy + cell_sz - 8)], fill=pipe_col, width=8)
                    else:
                        draw.line([(cx + 8, mid_y), (cx + cell_sz - 8, mid_y)], fill=pipe_col, width=8)
                elif ptype == 1: # Corner
                    draw.line([(mid_x, cy + 8), (mid_x, mid_y)], fill=pipe_col, width=8)
                    draw.line([(mid_x, mid_y), (cx + cell_sz - 8, mid_y)], fill=pipe_col, width=8)
                else: # T-connector
                    draw.line([(cx + 8, mid_y), (cx + cell_sz - 8, mid_y)], fill=pipe_col, width=8)
                    draw.line([(mid_x, mid_y), (mid_x, cy + cell_sz - 8)], fill=pipe_col, width=8)

        # Right Telemetry
        tx = start_x + GRID_SZ * cell_sz + 50
        draw.text((tx, 140), "STATUS IMPULSU:", fill=(0, 255, 220), font=get_font(18, bold=True))
        time_c = (255, 60, 60) if self.time_left < 10 else (0, 255, 120)
        draw.text((tx, 175), f"CZAS DO PRZEŁAMANIA: {self.time_left:.1f} s", fill=time_c, font=get_font(15, bold=True))
        draw.text((tx, 220), "CEL: Połącz wejście DATA_IN", fill=(200, 220, 240), font=get_font(14))
        draw.text((tx, 245), "z głównym rdzeniem SYSTEM_CORE.", fill=(200, 220, 240), font=get_font(14))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_UP":
            self.cursor_y = (self.cursor_y - 1) % GRID_SZ
            return True
        elif event == "KEY_DOWN":
            self.cursor_y = (self.cursor_y + 1) % GRID_SZ
            return True
        elif event == "KEY_LEFT":
            self.cursor_x = (self.cursor_x - 1) % GRID_SZ
            return True
        elif event == "KEY_RIGHT":
            self.cursor_x = (self.cursor_x + 1) % GRID_SZ
            return True
        elif event == "KEY_A":
            self.rotations[self.cursor_y][self.cursor_x] = (self.rotations[self.cursor_y][self.cursor_x] + 1) % 4
            return True
        return False
'''

# 3. mod_lunar_lander.py
MODULE_IMPLEMENTATIONS["mod_lunar_lander"] = '''#!/usr/bin/env python3
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
'''

def main():
    print("=== STARTING BACKGROUND BATCH MODULE BUILDER ===")
    out_dir = "store/modules"
    os.makedirs(out_dir, exist_ok=True)
    
    built_count = 0
    for mod_id, code in MODULE_IMPLEMENTATIONS.items():
        dest = os.path.join(out_dir, f"{mod_id}.py")
        print(f"[*] Building {mod_id}.py...")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(code.strip() + "\\n")
        built_count += 1
        
    print(f"[+] Successfully wrote {built_count} new modules to {out_dir}!")
    
    # Generate screenshots for newly created modules
    print("[*] Generating screenshots for all modules...")
    subprocess.run([sys.executable, "tools/generate_screenshots.py"], check=True)
    
    # Update registry and push to GitHub
    print("[*] Updating store/registry.json...")
    subprocess.run([sys.executable, "tools/update_registry.py"], check=True)
    
    print("[*] Committing and pushing to GitHub...")
    subprocess.run(["git", "add", "store/modules/", "docs/screenshots/", "store/registry.json", "index.html"], check=True)
    subprocess.run(["git", "commit", "-m", f"Batch build: Add {built_count} modules ({', '.join(MODULE_IMPLEMENTATIONS.keys())}) with screenshots"], check=False)
    subprocess.run(["git", "push"], check=True)
    print("=== BACKGROUND BUILD COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    main()
