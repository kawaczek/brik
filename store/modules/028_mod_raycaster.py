#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_raycaster.py - 3D Cyber-Maze Raycasting Engine with Accessibility & Settings
Pure-Python real-time pseudo-3D engine (Wolfenstein 3D style) for TrimUI Brick (1024x768).
Includes UI font scaling, minimap zoom (1x-3x), full-screen tactical radar, and in-game settings menu.
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

NUM_RAYS = 128
FOV = math.radians(66.0)
HALF_FOV = FOV / 2.0


class RaycasterModule(BaseModule):
    """3D Raycasting Maze Crawler Module with Accessibility Settings."""

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.px = 2.5
        self.py = 2.5
        self.angle = 0.0
        self.move_speed = 3.2
        self.rot_speed = 2.8

        # Collectible cyber-disks
        self.disks = [
            {"x": 4.5, "y": 3.5, "taken": False},
            {"x": 9.5, "y": 2.5, "taken": False},
            {"x": 5.5, "y": 12.5, "taken": False},
            {"x": 13.5, "y": 8.5, "taken": False},
            {"x": 13.5, "y": 13.5, "taken": False},
        ]
        self.score = 0
        self.fps = 60.0
        self.last_time = time.time()

        # --- USER ACCESSIBILITY & DISPLAY SETTINGS ---
        # 0: Standard (16px), 1: Duży / Czytelny (24px), 2: Bardzo Duży (32px)
        self.font_scale_idx = 1  # Default to Large for 3.2" IPS!
        self.font_scales = [
            {"name": "Standard (16pt)", "size": 16, "bar_h": 46},
            {"name": "Duży 3.2\" IPS (24pt)", "size": 24, "bar_h": 64},
            {"name": "Maksymalny (32pt)", "size": 32, "bar_h": 76}
        ]

        # 0: Mała (180px), 1: Średnia (260px), 2: Duża (340px), 3: Pełny Ekran (620px), 4: Wyłączona
        self.minimap_mode_idx = 1
        self.minimap_modes = [
            {"name": "Kompaktowa (180px)", "size": 180, "fullscreen": False},
            {"name": "Duża (280px)", "size": 280, "fullscreen": False},
            {"name": "Pełnoekranowy Radar 2D", "size": 600, "fullscreen": True},
            {"name": "Ukryta (Brak)", "size": 0, "fullscreen": False}
        ]

        # Zoom level inside the minimap
        self.minimap_zoom_levels = [1.0, 1.5, 2.0, 3.0]
        self.minimap_zoom_idx = 1 # 1.5x zoom

        # Settings overlay state
        self.show_settings = False
        self.settings_cursor = 0
        self.settings_items = [
            "Wielkość czcionki HUD",
            "Tryb i rozmiar minimapy",
            "Przybliżenie radaru (Zoom)",
            "Prędkość obrotu kamery"
        ]

        # Input keys held
        self.keys_held = {
            "UP": False, "DOWN": False, "LEFT": False, "RIGHT": False,
            "SPRINT": False
        }

    def get_hotkey_hints(self) -> List[Dict[str, str]]:
        return [
            {"key": "D-Pad", "desc": "Ruch / Obrót"},
            {"key": "A", "desc": "Weź dysk"},
            {"key": "X", "desc": "Tryb mapy"},
            {"key": "Y", "desc": "⚙️ Ustawienia & Tekst"},
            {"key": "L1/R1", "desc": "Zoom mapy"}
        ]

    def update(self, dt: float):
        now = time.time()
        self.fps = 0.9 * self.fps + 0.1 * (1.0 / max(0.001, dt))
        self.last_time = now

        if self.show_settings:
            return  # Paused during settings

        spd = self.move_speed * (1.8 if self.keys_held["SPRINT"] else 1.0) * dt
        rot = self.rot_speed * dt

        if self.keys_held["LEFT"]:
            self.angle -= rot
        if self.keys_held["RIGHT"]:
            self.angle += rot

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

        grid_x = int(new_x)
        grid_y = int(new_y)
        if 0 <= grid_x < MAP_W and 0 <= grid_y < MAP_H:
            if MAZE_MAP[grid_y * MAP_W + int(self.px)] == 0:
                self.py = new_y
            if MAZE_MAP[int(self.py) * MAP_W + grid_x] == 0:
                self.px = new_x

        for d in self.disks:
            if not d["taken"]:
                dist = math.hypot(self.px - d["x"], self.py - d["y"])
                if dist < 0.6:
                    d["taken"] = True
                    self.score += 500

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768

        # Check if full-screen tactical radar mode is active
        cur_map_cfg = self.minimap_modes[self.minimap_mode_idx]
        is_fullscreen_radar = cur_map_cfg["fullscreen"]

        if not is_fullscreen_radar:
            # 1. 3D Raycasting Viewport
            draw.rectangle([0, 0, w, h // 2], fill=(8, 12, 22))
            draw.rectangle([0, h // 2, w, h], fill=(14, 18, 28))

            for y_line in range(h // 2 + 10, h, 28):
                shade = min(45, 10 + (y_line - h // 2) // 7)
                draw.line([(0, y_line), (w, y_line)], fill=(shade, shade + 8, shade + 18), width=1)

            slice_w = w / NUM_RAYS
            half_h = h / 2.0
            dist_proj_plane = (w / 2.0) / math.tan(HALF_FOV)

            ray_angle = self.angle - HALF_FOV
            angle_step = FOV / NUM_RAYS

            for r in range(NUM_RAYS):
                sin_a = math.sin(ray_angle)
                cos_a = math.cos(ray_angle)

                map_x = int(self.px)
                map_y = int(self.py)

                delta_dist_x = abs(1.0 / cos_a) if cos_a != 0 else 1e30
                delta_dist_y = abs(1.0 / sin_a) if sin_a != 0 else 1e30

                step_x = 1 if cos_a >= 0 else -1
                side_dist_x = (map_x + 1.0 - self.px) * delta_dist_x if cos_a >= 0 else (self.px - map_x) * delta_dist_x

                step_y = 1 if sin_a >= 0 else -1
                side_dist_y = (map_y + 1.0 - self.py) * delta_dist_y if sin_a >= 0 else (self.py - map_y) * delta_dist_y

                hit = 0
                side = 0
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

                if side == 0:
                    perp_dist = (map_x - self.px + (1 - step_x) / 2.0) / cos_a if cos_a != 0 else 0.001
                else:
                    perp_dist = (map_y - self.py + (1 - step_y) / 2.0) / sin_a if sin_a != 0 else 0.001

                corrected_dist = max(0.05, perp_dist * math.cos(ray_angle - self.angle))
                line_height = min(h * 2.0, (dist_proj_plane / corrected_dist))

                line_top = int(half_h - line_height / 2.0)
                line_bot = int(half_h + line_height / 2.0)

                colors = WALL_COLORS.get(wall_type, WALL_COLORS[1])
                base_col = colors["base"] if side == 0 else colors["dark"]
                fog = max(0.15, min(1.0, 1.0 - (corrected_dist / 14.0)))
                shaded = (int(base_col[0] * fog), int(base_col[1] * fog), int(base_col[2] * fog))

                x_start = int(r * slice_w)
                x_end = int((r + 1) * slice_w)
                draw.rectangle([x_start, line_top, x_end, line_bot], fill=shaded)

                if line_height > 10:
                    edge_col = (int(shaded[0] * 1.3), int(shaded[1] * 1.3), int(shaded[2] * 1.3))
                    draw.line([(x_start, line_top), (x_end, line_top)], fill=edge_col, width=1)

                ray_angle += angle_step

            # Center Crosshair
            ch_x, ch_y = w // 2, h // 2
            draw.line([(ch_x - 12, ch_y), (ch_x + 12, ch_y)], fill=(0, 255, 200, 160), width=2)
            draw.line([(ch_x, ch_y - 12), (ch_x, ch_y + 12)], fill=(0, 255, 200, 160), width=2)
        else:
            # Full Tactical Radar Screen
            draw.rectangle([0, 0, w, h], fill=(6, 10, 16))
            draw.text((w // 2 - 180, 20), "TA戦 TACTICAL RADAR FULLSCREEN", fill=(0, 255, 200), font=get_font(20, bold=True))

        # 2. Minimap Rendering
        if cur_map_cfg["size"] > 0:
            mm_size = cur_map_cfg["size"]
            zoom = self.minimap_zoom_levels[self.minimap_zoom_idx]

            if is_fullscreen_radar:
                mm_x = (w - mm_size) // 2
                mm_y = (h - mm_size) // 2 + 20
            else:
                mm_x = w - mm_size - 18
                mm_y = self.font_scales[self.font_scale_idx]["bar_h"] + 14

            draw.rounded_rectangle([mm_x - 4, mm_y - 4, mm_x + mm_size + 4, mm_y + mm_size + 4],
                                   radius=8, fill=(8, 14, 22, 235), outline=(0, 220, 255), width=2)

            cell_size = (mm_size / MAP_W) * zoom
            # Centering offset based on player position and zoom
            if zoom > 1.0:
                off_x = mm_x + mm_size / 2.0 - self.px * cell_size
                off_y = mm_y + mm_size / 2.0 - self.py * cell_size
            else:
                off_x = mm_x
                off_y = mm_y

            for my in range(MAP_H):
                for mx in range(MAP_W):
                    tile = MAZE_MAP[my * MAP_W + mx]
                    if tile > 0:
                        tc = WALL_COLORS.get(tile, WALL_COLORS[1])["base"]
                        tx1 = int(off_x + mx * cell_size)
                        ty1 = int(off_y + my * cell_size)
                        tx2 = int(off_x + (mx + 1) * cell_size)
                        ty2 = int(off_y + (my + 1) * cell_size)
                        # Clip inside minimap box
                        if tx2 >= mm_x and tx1 <= mm_x + mm_size and ty2 >= mm_y and ty1 <= mm_y + mm_size:
                            draw.rectangle([
                                max(mm_x, tx1), max(mm_y, ty1),
                                min(mm_x + mm_size, tx2 - 1), min(mm_y + mm_size, ty2 - 1)
                            ], fill=tc)

            # Draw collectible disks on minimap
            for d in self.disks:
                if not d["taken"]:
                    dx_p = off_x + d["x"] * cell_size
                    dy_p = off_y + d["y"] * cell_size
                    if mm_x <= dx_p <= mm_x + mm_size and mm_y <= dy_p <= mm_y + mm_size:
                        draw.ellipse([dx_p - 4, dy_p - 4, dx_p + 4, dy_p + 4], fill=(255, 230, 0), outline=(0, 0, 0))

            # Draw Player marker
            p_scr_x = off_x + self.px * cell_size
            p_scr_y = off_y + self.py * cell_size
            if mm_x <= p_scr_x <= mm_x + mm_size and mm_y <= p_scr_y <= mm_y + mm_size:
                draw.ellipse([p_scr_x - 5, p_scr_y - 5, p_scr_x + 5, p_scr_y + 5], fill=(255, 60, 80), outline=(255, 255, 255))
                fov_len = 22
                x1 = p_scr_x + math.cos(self.angle - HALF_FOV) * fov_len
                y1 = p_scr_y + math.sin(self.angle - HALF_FOV) * fov_len
                x2 = p_scr_x + math.cos(self.angle + HALF_FOV) * fov_len
                y2 = p_scr_y + math.sin(self.angle + HALF_FOV) * fov_len
                draw.line([(p_scr_x, p_scr_y), (x1, y1)], fill=(0, 255, 200), width=2)
                draw.line([(p_scr_x, p_scr_y), (x2, y2)], fill=(0, 255, 200), width=2)

            # Minimap Zoom Badge
            draw.text((mm_x + 8, mm_y + mm_size - 22), f"ZOOM {zoom:.1f}x [L1/R1]", fill=(0, 255, 200), font=get_font(12, bold=True))

        # 3. Dynamic Scalable High-Contrast Top Telemetry Bar
        f_cfg = self.font_scales[self.font_scale_idx]
        bar_h = f_cfg["bar_h"]
        f_size = f_cfg["size"]
        font_main = get_font(f_size, bold=True)
        font_sub = get_font(max(12, f_size - 4))

        draw.rectangle([0, 0, w, bar_h], fill=(10, 16, 26, 240), outline=(0, 200, 255), width=2)

        taken_count = sum(1 for d in self.disks if d['taken'])
        ty = (bar_h - f_size) // 2

        if self.font_scale_idx >= 1:
            # Big High-Legibility Mode for 3.2" Screen!
            draw.text((16, ty), f"🏆 {self.score:05d}", fill=(255, 220, 0), font=font_main)
            draw.text((220, ty), f"💾 DYSKI: {taken_count}/{len(self.disks)}", fill=(0, 255, 200), font=font_main)
            draw.text((510, ty), f"POZ: [{self.px:.1f}, {self.py:.1f}]", fill=(220, 230, 245), font=font_sub)
            canvas.draw_badge(w - 180, ty - 2, f"FPS: {int(self.fps)}", bg_color=(0, 120, 80), text_color=(255, 255, 255))
        else:
            # Compact Standard Mode
            draw.text((16, ty), "🕹️ 3D CYBER-MAZE", fill=(0, 255, 200), font=font_main)
            draw.text((260, ty), f"SCORE: {self.score:06d}", fill=(255, 220, 0), font=font_main)
            draw.text((460, ty), f"DISKS: {taken_count}/{len(self.disks)}", fill=(0, 200, 255), font=font_main)
            draw.text((650, ty), f"POS: [{self.px:.1f}, {self.py:.1f}]", fill=(180, 190, 210), font=font_sub)
            canvas.draw_badge(w - 110, ty - 2, f"{int(self.fps)} FPS", bg_color=(0, 120, 80), text_color=(255, 255, 255))

        # Bottom Hint Bar
        draw.text((20, h - 35), "[Y]: ⚙️ Ustawienia & Skala | [X]: Tryb Mapy | [L1/R1]: Zoom | [A]: Dysk",
                  fill=(255, 210, 0), font=get_font(14, bold=True))

        # 4. In-Game Settings Overlay (when Y is pressed)
        if self.show_settings:
            self._render_settings_modal(canvas, w, h)

    def _render_settings_modal(self, canvas: Canvas, w: int, h: int):
        draw = canvas.draw
        # Dim background
        draw.rectangle([0, 0, w, h], fill=(0, 0, 0, 180))

        # Settings Card (Center)
        sw, sh = 680, 440
        sx = (w - sw) // 2
        sy = (h - sh) // 2
        draw.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=14, fill=(14, 20, 32, 250), outline=(255, 200, 0), width=3)

        draw.text((sx + 30, sy + 25), "⚙️ USTAWIENIA EKRANU & CZYTELNOŚCI (3.2\" IPS)", fill=(255, 220, 0), font=get_font(20, bold=True))
        draw.line([(sx + 20, sy + 65), (sx + sw - 20, sy + 65)], fill=(50, 70, 95))

        cur_font = self.font_scales[self.font_scale_idx]["name"]
        cur_map = self.minimap_modes[self.minimap_mode_idx]["name"]
        cur_zoom = f"{self.minimap_zoom_levels[self.minimap_zoom_idx]:.1f}x (Centrowany na graczu)"
        cur_speed = f"{self.rot_speed:.1f} rad/s"

        items = [
            ("Wielkość czcionki HUD:", cur_font),
            ("Rozmiar i tryb minimapy:", cur_map),
            ("Przybliżenie radaru (Zoom):", cur_zoom),
            ("Czułość obrotu kamery:", cur_speed)
        ]

        iy = sy + 90
        for idx, (label, val) in enumerate(items):
            is_cur = (idx == self.settings_cursor)
            if is_cur:
                draw.rounded_rectangle([sx + 25, iy - 6, sx + sw - 25, iy + 42], radius=6, fill=(28, 42, 65), outline=(0, 240, 255), width=2)

            col = (255, 255, 255) if is_cur else (170, 190, 215)
            draw.text((sx + 40, iy + 4), label, fill=col, font=get_font(16, bold=is_cur))
            draw.text((sx + 320, iy + 4), f"◀  {val}  ▶", fill=(0, 255, 200) if is_cur else (255, 220, 0), font=get_font(16, bold=True))
            iy += 58

        # Footer advice for TrimUI Brick
        draw.rounded_rectangle([sx + 25, sy + sh - 110, sx + sw - 25, sy + sh - 30], radius=8, fill=(10, 15, 24), outline=(30, 45, 65))
        draw.text((sx + 40, sy + sh - 98), "💡 WSKAZÓWKA: Ekran TrimUI Brick (3.2\") ma wysoką gęstość pikseli.", fill=(255, 210, 0), font=get_font(13, bold=True))
        draw.text((sx + 40, sy + sh - 75), "Zalecamy tryb 'Duży 3.2\" IPS (24pt)' dla maksymalnej czytelności w biegu.", fill=(180, 200, 225), font=get_font(13))
        draw.text((sx + 40, sy + sh - 52), "D-Pad: Wybór opcji i zmiana | [Y] lub [B]: Zamknij menu", fill=(0, 255, 140), font=get_font(13, bold=True))

    def handle_input(self, event: str) -> bool:
        # Settings Toggle & Dismiss
        if event in ("KEY_Y", "BTN_Y", "y", "Y"):
            self.show_settings = not self.show_settings
            return True
        elif (event in ("KEY_B", "BTN_B", "b", "B")) and self.show_settings:
            self.show_settings = False
            return True

        if self.show_settings:
            if event in ("KEY_UP", "UP", "w", "W"):
                self.settings_cursor = (self.settings_cursor - 1) % len(self.settings_items)
                return True
            elif event in ("KEY_DOWN", "DOWN", "s", "S"):
                self.settings_cursor = (self.settings_cursor + 1) % len(self.settings_items)
                return True
            elif event in ("KEY_LEFT", "LEFT", "KEY_RIGHT", "RIGHT", "a", "d", "A", "D"):
                delta = 1 if event in ("KEY_RIGHT", "RIGHT", "d", "D") else -1
                if self.settings_cursor == 0: # Font scale
                    self.font_scale_idx = (self.font_scale_idx + delta) % len(self.font_scales)
                elif self.settings_cursor == 1: # Minimap mode
                    self.minimap_mode_idx = (self.minimap_mode_idx + delta) % len(self.minimap_modes)
                elif self.settings_cursor == 2: # Zoom
                    self.minimap_zoom_idx = (self.minimap_zoom_idx + delta) % len(self.minimap_zoom_levels)
                elif self.settings_cursor == 3: # Rot speed
                    self.rot_speed = max(1.5, min(5.0, self.rot_speed + delta * 0.4))
                return True
            return False

        # Gameplay Direct Movement & Actions
        if event in ("KEY_UP", "UP", "KEY_W", "w", "W"):
            spd = 0.30 * (1.8 if self.keys_held["SPRINT"] else 1.0)
            dx = math.cos(self.angle) * spd
            dy = math.sin(self.angle) * spd
            buf_x = 0.22 if dx > 0 else -0.22
            buf_y = 0.22 if dy > 0 else -0.22
            if 0 <= int(self.py) < MAP_H and 0 <= int(self.px + dx + buf_x) < MAP_W:
                if MAZE_MAP[int(self.py) * MAP_W + int(self.px + dx + buf_x)] == 0:
                    self.px += dx
            if 0 <= int(self.py + dy + buf_y) < MAP_H and 0 <= int(self.px) < MAP_W:
                if MAZE_MAP[int(self.py + dy + buf_y) * MAP_W + int(self.px)] == 0:
                    self.py += dy
            return True
        elif event in ("KEY_DOWN", "DOWN", "KEY_S", "s", "S"):
            spd = 0.30 * (1.8 if self.keys_held["SPRINT"] else 1.0)
            dx = math.cos(self.angle) * spd
            dy = math.sin(self.angle) * spd
            buf_x = -0.22 if dx > 0 else 0.22
            buf_y = -0.22 if dy > 0 else 0.22
            if 0 <= int(self.py) < MAP_H and 0 <= int(self.px - dx + buf_x) < MAP_W:
                if MAZE_MAP[int(self.py) * MAP_W + int(self.px - dx + buf_x)] == 0:
                    self.px -= dx
            if 0 <= int(self.py - dy + buf_y) < MAP_H and 0 <= int(self.px) < MAP_W:
                if MAZE_MAP[int(self.py - dy + buf_y) * MAP_W + int(self.px)] == 0:
                    self.py -= dy
            return True
        elif event in ("KEY_LEFT", "LEFT", "KEY_A", "a", "A"):
            self.angle = (self.angle - 0.16) % (2.0 * math.pi)
            return True
        elif event in ("KEY_RIGHT", "RIGHT", "KEY_D", "d", "D"):
            self.angle = (self.angle + 0.16) % (2.0 * math.pi)
            return True
        elif event in ("KEY_B", "BTN_B", "b", "B"):
            self.keys_held["SPRINT"] = not self.keys_held["SPRINT"]
            return True
        elif event in ("KEY_X", "BTN_X", "x", "X"):
            # Cycle through map modes directly: Compact -> Large -> Fullscreen -> Off
            self.minimap_mode_idx = (self.minimap_mode_idx + 1) % len(self.minimap_modes)
            return True
        elif event in ("KEY_L1", "BTN_L1", "l1", "q", "Q"):
            # Zoom out
            self.minimap_zoom_idx = max(0, self.minimap_zoom_idx - 1)
            return True
        elif event in ("KEY_R1", "BTN_R1", "r1", "e", "E"):
            # Zoom in
            self.minimap_zoom_idx = min(len(self.minimap_zoom_levels) - 1, self.minimap_zoom_idx + 1)
            return True
        return False
