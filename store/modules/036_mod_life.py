#!/usr/bin/env python3
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
