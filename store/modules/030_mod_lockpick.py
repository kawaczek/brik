#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_lockpick.py - Safe Cracker & Lockpicking Mini-Game
Audio-tactile safe cracking simulator for TrimUI Brick (1024x768).
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


class LockpickModule(BaseModule):
    """Safe Combination Dial & Pin Tumbler Cracking Game."""

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.dial_value = 0  # 0 to 99
        self.combo_length = 3
        self.target_combo = [
            random.randint(5, 30),
            random.randint(40, 65),
            random.randint(75, 95)
        ]
        self.current_pin = 0  # which pin we are cracking (0, 1, 2)
        self.cracked_pins = [False, False, False]
        self.time_left = 60.0
        self.is_unlocked = False
        self.is_alarm = False
        self.click_feedback = 0.0  # visual & auditory tension meter
        self.status_msg = "Kręć tarczą D-Padem. Wyczuj kliknięcie zapadki!"

    def get_hotkey_hints(self) -> List[Dict[str, str]]:
        return [
            {"key": "D-Pad Lewo/Prawo", "desc": "Obrót tarczy"},
            {"key": "A", "desc": "Sprawdź zapadkę"},
            {"key": "B", "desc": "Reset kombinacji"},
            {"key": "Y", "desc": "Nowy sejf"},
        ]

    def update(self, dt: float):
        if not self.is_unlocked and not self.is_alarm:
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.is_alarm = True
                self.status_msg = "ALARM! CZAS MINĄŁ! Sejf zablokowany."

        # Decay click feedback
        if self.click_feedback > 0:
            self.click_feedback = max(0.0, self.click_feedback - dt * 2.5)

        # Calculate proximity to target pin
        if self.current_pin < self.combo_length:
            target = self.target_combo[self.current_pin]
            diff = abs(self.dial_value - target)
            if diff <= 3:
                self.click_feedback = max(self.click_feedback, 1.0 - (diff / 4.0))

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = SCREEN_W, SCREEN_H

        # Metallic safe door background
        draw.rectangle([0, 0, w, h], fill=(12, 16, 24))
        # Heavy steel rivets
        for rx in (40, w - 40):
            for ry in range(40, h, 80):
                draw.ellipse([rx - 6, ry - 6, rx + 6, ry + 6], fill=(45, 55, 75), outline=(90, 110, 140))

        # Safe Wheel Dial in center
        cx, cy = w // 2 - 80, h // 2
        r_outer = 180

        # Outer steel ring
        draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
                     fill=(22, 28, 38), outline=(0, 200, 255), width=3)
        # Inner dial plate
        r_inner = 145
        draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner],
                     fill=(14, 18, 26), outline=(60, 80, 110), width=2)

        # Draw tick marks (0 to 99)
        for val in range(0, 100, 2):
            angle_deg = (val / 100.0) * 360.0 - 90.0
            rad = math.radians(angle_deg)
            is_major = (val % 10 == 0)
            len_tick = 14 if is_major else 7
            x1 = cx + math.cos(rad) * (r_inner - 2)
            y1 = cy + math.sin(rad) * (r_inner - 2)
            x2 = cx + math.cos(rad) * (r_inner - 2 - len_tick)
            y2 = cy + math.sin(rad) * (r_inner - 2 - len_tick)

            t_color = (0, 255, 220) if is_major else (70, 90, 115)
            draw.line([(x1, y1), (x2, y2)], fill=t_color, width=2 if is_major else 1)

        # Dial Indicator needle at top (0 position)
        needle_angle = (self.dial_value / 100.0) * 360.0 - 90.0
        n_rad = math.radians(needle_angle)
        draw.line([(cx, cy), (cx + math.cos(n_rad) * (r_inner - 18), cy + math.sin(n_rad) * (r_inner - 18))],
                  fill=(255, 60, 60), width=4)
        draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(30, 40, 55), outline=(0, 220, 255), width=2)

        # Digital indicator in center
        draw.text((cx - 18, cy - 12), f"{self.dial_value:02d}", fill=(255, 255, 255), font=get_font(20, bold=True))

        # Top Needle marker (Fixed reading mark)
        draw.polygon([(cx - 8, cy - r_outer - 4), (cx + 8, cy - r_outer - 4), (cx, cy - r_outer + 8)], fill=(255, 220, 0))

        # Right Panel: Tumbler Pins & Tension Meter
        panel_x = w - 380
        draw.rounded_rectangle([panel_x, 70, panel_x + 340, 690], radius=8, fill=(16, 22, 32), outline=(0, 180, 220), width=2)

        draw.text((panel_x + 20, 90), "SEJF ELEKTRONICZNY", fill=(0, 255, 220), font=get_font(18, bold=True))
        time_col = (255, 60, 60) if self.time_left < 15 else (255, 210, 0)
        draw.text((panel_x + 20, 125), f"POZOSTAŁY CZAS: {int(self.time_left)} s", fill=time_col, font=get_font(15, bold=True))

        # Tension / Click Gauge
        draw.text((panel_x + 20, 175), "WSKAŹNIK NAPRĘŻENIA:", fill=(140, 160, 180), font=get_font(13))
        gauge_w = 300
        draw.rectangle([panel_x + 20, 200, panel_x + 20 + gauge_w, 224], fill=(20, 28, 40), outline=(50, 70, 95))
        click_fill_w = int(gauge_w * self.click_feedback)
        if click_fill_w > 0:
            c_col = (0, 255, 120) if self.click_feedback > 0.8 else ((255, 200, 0) if self.click_feedback > 0.4 else (0, 150, 220))
            draw.rectangle([panel_x + 20, 200, panel_x + 20 + click_fill_w, 224], fill=c_col)

        # 3 Tumblers representation
        draw.text((panel_x + 20, 250), "ZAPADKI MECHANIZMU:", fill=(0, 200, 255), font=get_font(14, bold=True))
        for pin_i in range(3):
            pin_y = 285 + pin_i * 68
            is_done = self.cracked_pins[pin_i]
            is_active = (pin_i == self.current_pin and not self.is_unlocked)

            p_border = (0, 255, 120) if is_done else ((0, 200, 255) if is_active else (40, 55, 75))
            p_fill = (10, 45, 25) if is_done else ((20, 32, 48) if is_active else (14, 18, 26))

            draw.rectangle([panel_x + 20, pin_y, panel_x + 320, pin_y + 54], fill=p_fill, outline=p_border, width=2)
            draw.text((panel_x + 36, pin_y + 16), f"Zapadka #{pin_i + 1}", fill=(255, 255, 255), font=get_font(15, bold=True))

            status_str = f"ZŁAMANA ({self.target_combo[pin_i]:02d})" if is_done else ("AKTYWNA" if is_active else "ZABLOKOWANA")
            s_col = (0, 255, 120) if is_done else ((255, 210, 0) if is_active else (100, 120, 140))
            draw.text((panel_x + 180, pin_y + 18), status_str, fill=s_col, font=get_font(13))

        # Status Banner at bottom
        banner_bg = (0, 100, 50) if self.is_unlocked else ((120, 20, 20) if self.is_alarm else (16, 24, 36))
        draw.rectangle([40, h - 60, w - 40, h - 16], fill=banner_bg, outline=(0, 180, 220), width=1)
        draw.text((60, h - 44), self.status_msg, fill=(255, 255, 255), font=get_font(15, bold=True))

    def handle_input(self, event: str) -> bool:
        if self.is_unlocked or self.is_alarm:
            if event in ("KEY_A", "KEY_Y"):
                # Reset game
                self.dial_value = 0
                self.current_pin = 0
                self.cracked_pins = [False, False, False]
                self.target_combo = [random.randint(5, 30), random.randint(40, 65), random.randint(75, 95)]
                self.time_left = 60.0
                self.is_unlocked = False
                self.is_alarm = False
                self.status_msg = "Nowy sejf wygenerowany. Zaczynamy!"
            return True

        if event == "KEY_RIGHT":
            self.dial_value = (self.dial_value + 1) % 100
            return True
        elif event == "KEY_LEFT":
            self.dial_value = (self.dial_value - 1) % 100
            return True
        elif event == "KEY_A":
            # Test current pin
            if self.current_pin < self.combo_length:
                target = self.target_combo[self.current_pin]
                if self.dial_value == target:
                    self.cracked_pins[self.current_pin] = True
                    self.current_pin += 1
                    if self.current_pin >= self.combo_length:
                        self.is_unlocked = True
                        self.status_msg = "KLIK! SEJF OTWARTO POMYŚLNIE!"
                    else:
                        self.status_msg = f"KLIK! Zapadka #{self.current_pin} zaliczona! Szukaj kolejnej."
                else:
                    self.status_msg = "Zapadka nie drgnęła. Szukaj dalej!"
            return True
        elif event == "KEY_B":
            self.dial_value = 0
            self.current_pin = 0
            self.cracked_pins = [False, False, False]
            self.status_msg = "Zresetowano kombinację."
            return True
        return False
