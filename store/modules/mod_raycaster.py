#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_raycaster.py - 3D Cyber-Maze Raycasting Engine
Pure-Python real-time pseudo-3D engine (Wolfenstein 3D style) for TrimUI Brick (1024x768).
Zero external dependencies (uses standard math & PIL).
"""

import math
import time
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont

from core.module_base import BaseModule
from core.canvas import Canvas, get_font

MAP_W = 16
MAP_H = 16

# 0: Empty, 1: Cyan Wall, 2: Amber Wall, 3: Purple Wall, 4: Terminal Wall, 9: Exit Gate
MAZE_MAP = [
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 2, 2, 0, 0, 1, 0, 3, 3, 3, 3, 0, 2, 0, 1,
    1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 2, 0, 1,
    1, 0, 2, 0, 1, 1, 1, 0, 0, 0, 0, 3, 0, 0, 0, 1,
    1, 0, 0, 0, 1, 0, 1, 0, 2, 2, 0, 0, 0, 4, 0, 1,
    1, 0, 0, 0, 1, 0, 1, 0, 0, 2, 0, 0, 0, 4, 0, 1,
    1, 1, 0, 1, 1, 0, 1, 1, 0, 2, 2, 2, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 3, 0, 1,
    1, 0, 3, 3, 3, 0, 0, 1, 1, 0, 0, 0, 0, 3, 0, 1,
    1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 3, 0, 1,
    1, 0, 3, 0, 2, 2, 2, 0, 0, 0, 1, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 2, 0, 0, 0, 4, 0, 1, 0, 2, 2, 0, 1,
    1, 0, 2, 0, 2, 0, 1, 1, 4, 0, 0, 0, 2, 9, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
]

WALL_COLORS = {
    1: {"base": (0, 180, 210), "dark": (0, 90, 120)},    # Cyan Neon
    2: {"base": (230, 150, 20), "dark": (140, 80, 10)},   # Amber Cyber
    3: {"base": (180, 50, 220), "dark": (100, 25, 130)},  # Magenta Matrix
    4: {"base": (40, 220, 100), "dark": (20, 120, 50)},   # Green Terminal
    9: {"base": (255, 230, 50), "dark": (160, 140, 20)},  # Golden Gate
}

NUM_RAYS = 128  # 128 columns for high FPS (1024 / 128 = 8px slice)
FOV = math.radians(66.0)
HALF_FOV = FOV / 2.0


class RaycasterModule(BaseModule):
    """3D Raycasting Maze Crawler Module."""

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.px = 2.5
        self.py = 2.5
        self.angle = 0.0
        self.move_speed = 3.2
        self.rot_speed = 2.8

        # Collectible cyber-disks (x, y, collected)
        self.disks = [
            {"x": 4.5, "y": 3.5, "taken": False},
            {"x": 9.5, "y": 2.5, "taken": False},
            {"x": 5.5, "y": 12.5, "taken": False},
            {"x": 13.5, "y": 8.5, "taken": False},
            {"x": 13.5, "y": 13.5, "taken": False},
        ]
        self.score = 0
        self.show_minimap = True
        self.fps = 60.0
        self.last_time = time.time()

        # Input keys held
        self.keys_held = {
            "UP": False, "DOWN": False, "LEFT": False, "RIGHT": False,
            "SPRINT": False
        }

    def get_hotkey_hints(self) -> List[Dict[str, str]]:
        return [
            {"key": "D-Pad", "desc": "Krok / Obrót"},
            {"key": "A", "desc": "Weź dysk"},
            {"key": "X", "desc": "Minimapa"},
            {"key": "B", "desc": "Sprint"},
        ]

    def update(self, dt: float):
        now = time.time()
        self.fps = 0.9 * self.fps + 0.1 * (1.0 / max(0.001, dt))
        self.last_time = now

        spd = self.move_speed * (1.8 if self.keys_held["SPRINT"] else 1.0) * dt
        rot = self.rot_speed * dt

        if self.keys_held["LEFT"]:
            self.angle -= rot
        if self.keys_held["RIGHT"]:
            self.angle += rot

        # Normalize angle
        self.angle = self.angle % (2.0 * math.pi)

        dx = math.cos(self.angle) * spd
        dy = math.sin(self.angle) * spd

        new_x = self.px
        new_y = self.py

        if self.keys_held["UP"]:
            new_x += dx
            new_y += dy
        if self.keys_held["DOWN"]:
            new_x -= dx
            new_y -= dy

        # Collision check with wall radius 0.25
        grid_x = int(new_x)
        grid_y = int(new_y)
        if 0 <= grid_x < MAP_W and 0 <= grid_y < MAP_H:
            if MAZE_MAP[grid_y * MAP_W + int(self.px)] == 0:
                self.py = new_y
            if MAZE_MAP[int(self.py) * MAP_W + grid_x] == 0:
                self.px = new_x

        # Collect disks if close
        for d in self.disks:
            if not d["taken"]:
                dist = math.hypot(self.px - d["x"], self.py - d["y"])
                if dist < 0.6:
                    d["taken"] = True
                    self.score += 500

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768

        # 1. Sky & Floor gradient
        # Ceiling: deep cyber navy
        draw.rectangle([0, 0, w, h // 2], fill=(8, 12, 22))
        # Floor: dark grid
        draw.rectangle([0, h // 2, w, h], fill=(14, 18, 28))

        # Horizontal grid line accents on floor
        for y_line in range(h // 2 + 10, h, 28):
            shade = min(45, 10 + (y_line - h // 2) // 7)
            draw.line([(0, y_line), (w, y_line)], fill=(shade, shade + 8, shade + 18), width=1)

        # 2. DDA Raycasting
        slice_w = w / NUM_RAYS
        half_h = h / 2.0
        dist_proj_plane = (w / 2.0) / math.tan(HALF_FOV)

        ray_angle = self.angle - HALF_FOV
        angle_step = FOV / NUM_RAYS

        for r in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            # Map coordinates
            map_x = int(self.px)
            map_y = int(self.py)

            # Length of ray from one x or y-side to next
            delta_dist_x = abs(1.0 / cos_a) if cos_a != 0 else 1e30
            delta_dist_y = abs(1.0 / sin_a) if sin_a != 0 else 1e30

            step_x = 1 if cos_a >= 0 else -1
            side_dist_x = (map_x + 1.0 - self.px) * delta_dist_x if cos_a >= 0 else (self.px - map_x) * delta_dist_x

            step_y = 1 if sin_a >= 0 else -1
            side_dist_y = (map_y + 1.0 - self.py) * delta_dist_y if sin_a >= 0 else (self.py - map_y) * delta_dist_y

            hit = 0
            side = 0  # 0 for X, 1 for Y
            wall_type = 1

            while hit == 0:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1

                if 0 <= map_x < MAP_W and 0 <= map_y < MAP_H:
                    tile = MAZE_MAP[map_y * MAP_W + map_x]
                    if tile > 0:
                        hit = 1
                        wall_type = tile
                else:
                    hit = 1
                    wall_type = 1

            # Calculate perpendicular distance to fix fish-eye lens effect
            if side == 0:
                perp_dist = (map_x - self.px + (1 - step_x) / 2.0) / cos_a if cos_a != 0 else 0.001
            else:
                perp_dist = (map_y - self.py + (1 - step_y) / 2.0) / sin_a if sin_a != 0 else 0.001

            # Fix cos distortion
            corrected_dist = max(0.05, perp_dist * math.cos(ray_angle - self.angle))
            line_height = min(h * 2.0, (dist_proj_plane / corrected_dist))

            line_top = int(half_h - line_height / 2.0)
            line_bot = int(half_h + line_height / 2.0)

            # Shading by distance and orientation
            colors = WALL_COLORS.get(wall_type, WALL_COLORS[1])
            base_col = colors["base"] if side == 0 else colors["dark"]
            fog = max(0.15, min(1.0, 1.0 - (corrected_dist / 14.0)))
            shaded = (
                int(base_col[0] * fog),
                int(base_col[1] * fog),
                int(base_col[2] * fog)
            )

            x_start = int(r * slice_w)
            x_end = int((r + 1) * slice_w)
            draw.rectangle([x_start, line_top, x_end, line_bot], fill=shaded)

            # Neon edge highlight at wall top/bottom
            if line_height > 10:
                edge_col = (int(shaded[0] * 1.3), int(shaded[1] * 1.3), int(shaded[2] * 1.3))
                draw.line([(x_start, line_top), (x_end, line_top)], fill=edge_col, width=1)

            ray_angle += angle_step

        # 3. HUD Overlays (Crosshair & Compass)
        ch_x, ch_y = w // 2, h // 2
        draw.line([(ch_x - 10, ch_y), (ch_x + 10, ch_y)], fill=(0, 255, 200, 128), width=1)
        draw.line([(ch_x, ch_y - 10), (ch_x, ch_y + 10)], fill=(0, 255, 200, 128), width=1)

        # 4. Top Telemetry Bar
        draw.rectangle([0, 0, w, 44], fill=(10, 14, 22, 220), outline=(0, 180, 220), width=1)
        draw.text((16, 12), "3D CYBER-MAZE v1.0", fill=(0, 255, 200), font=get_font(16, bold=True))
        draw.text((280, 12), f"SCORE: {self.score:06d}", fill=(255, 210, 0), font=get_font(16, bold=True))
        taken_count = sum(1 for d in self.disks if d['taken'])
        draw.text((480, 12), f"DISKS: {taken_count}/{len(self.disks)}", fill=(0, 200, 255), font=get_font(16))
        draw.text((680, 12), f"POS: [{self.px:.1f}, {self.py:.1f}]", fill=(180, 190, 210), font=get_font(16))
        canvas.draw_badge(w - 110, 10, f"{int(self.fps)} FPS", bg_color=(0, 120, 90), text_color=(255, 255, 255))

        # 5. Minimap Radar (Top-Right or Full)
        if self.show_minimap:
            mm_size = 176
            mm_x = w - mm_size - 16
            mm_y = 56
            cell_size = mm_size / MAP_W

            # Minimap background plate
            draw.rectangle([mm_x - 4, mm_y - 4, mm_x + mm_size + 4, mm_y + mm_size + 4],
                           fill=(6, 10, 16, 230), outline=(0, 200, 255), width=2)

            for my in range(MAP_H):
                for mx in range(MAP_W):
                    tile = MAZE_MAP[my * MAP_W + mx]
                    if tile > 0:
                        tc = WALL_COLORS.get(tile, WALL_COLORS[1])["base"]
                        draw.rectangle([
                            mm_x + mx * cell_size,
                            mm_y + my * cell_size,
                            mm_x + (mx + 1) * cell_size - 1,
                            mm_y + (my + 1) * cell_size - 1
                        ], fill=tc)

            # Draw collectible disks on minimap
            for d in self.disks:
                if not d["taken"]:
                    dx_p = mm_x + d["x"] * cell_size
                    dy_p = mm_y + d["y"] * cell_size
                    draw.ellipse([dx_p - 2, dy_p - 2, dx_p + 2, dy_p + 2], fill=(255, 230, 0))

            # Draw Player Marker & FOV Cone
            p_scr_x = mm_x + self.px * cell_size
            p_scr_y = mm_y + self.py * cell_size
            draw.ellipse([p_scr_x - 3, p_scr_y - 3, p_scr_x + 3, p_scr_y + 3], fill=(255, 60, 60))

            # FOV lines
            fov_len = 16
            x1 = p_scr_x + math.cos(self.angle - HALF_FOV) * fov_len
            y1 = p_scr_y + math.sin(self.angle - HALF_FOV) * fov_len
            x2 = p_scr_x + math.cos(self.angle + HALF_FOV) * fov_len
            y2 = p_scr_y + math.sin(self.angle + HALF_FOV) * fov_len
            draw.line([(p_scr_x, p_scr_y), (x1, y1)], fill=(0, 255, 200), width=1)
            draw.line([(p_scr_x, p_scr_y), (x2, y2)], fill=(0, 255, 200), width=1)

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_UP", "KEY_W"):
            self.keys_held["UP"] = not self.keys_held["UP"]
            return True
        elif event in ("KEY_DOWN", "KEY_S"):
            self.keys_held["DOWN"] = not self.keys_held["DOWN"]
            return True
        elif event in ("KEY_LEFT", "KEY_A"):
            self.keys_held["LEFT"] = not self.keys_held["LEFT"]
            return True
        elif event in ("KEY_RIGHT", "KEY_D"):
            self.keys_held["RIGHT"] = not self.keys_held["RIGHT"]
            return True
        elif event == "KEY_B":
            self.keys_held["SPRINT"] = not self.keys_held["SPRINT"]
            return True
        elif event == "KEY_X":
            self.show_minimap = not self.show_minimap
            return True
        return False
