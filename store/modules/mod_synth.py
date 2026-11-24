#!/usr/bin/env python3
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
