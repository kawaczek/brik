#!/usr/bin/env python3
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
