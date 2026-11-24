#!/usr/bin/env python3
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
        return False\n