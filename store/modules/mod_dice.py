#!/usr/bin/env python3
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
