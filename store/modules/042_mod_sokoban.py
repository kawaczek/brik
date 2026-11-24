#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class SokobanModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.moves = 28
        self.pushes = 14
        self.level = 1
        self.player_x = 3
        self.player_y = 3
        # 0: empty, 1: wall, 2: box, 3: target, 4: box on target
        self.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 2, 0, 1, 0, 3, 0, 1],
            [1, 0, 0, 0, 0, 0, 3, 0, 1],
            [1, 1, 0, 2, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.grid_rows = len(self.grid)
        self.grid_cols = len(self.grid[0])

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Ruch technika"},
            {"key": "B", "desc": "Cofnij ruch (Undo)"},
            {"key": "X", "desc": "Reset poziomu"},
            {"key": "A", "desc": "Następny poziom"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="📦 SOKOBAN // CYBERDECK WAREHOUSE",
                         subtitle=f"Poziom: {self.level} // Serwerownia Gamma | Ruchy: {self.moves} | Pchnięcia: {self.pushes}",
                         border_color=(0, 255, 140))

        # Warehouse Board
        ox, oy = 180, 130
        tile_sz = 68

        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                tx = ox + c * tile_sz
                ty = oy + r * tile_sz
                cell = self.grid[r][c]

                # Floor grid
                draw.rectangle([tx, ty, tx + tile_sz, ty + tile_sz], fill=(12, 16, 24), outline=(25, 35, 50))

                if cell == 1: # Server rack wall
                    draw.rounded_rectangle([tx + 2, ty + 2, tx + tile_sz - 2, ty + tile_sz - 2], radius=6, fill=(24, 34, 48), outline=(0, 200, 255), width=2)
                    draw.line([(tx + 12, ty + 20), (tx + tile_sz - 12, ty + 20)], fill=(0, 255, 200), width=2)
                    draw.line([(tx + 12, ty + 40), (tx + tile_sz - 12, ty + 40)], fill=(0, 255, 200), width=2)
                elif cell == 3: # Power socket Target
                    draw.ellipse([tx + 18, ty + 18, tx + tile_sz - 18, ty + tile_sz - 18], fill=(10, 40, 25), outline=(0, 255, 120), width=2)
                    draw.text((tx + 26, ty + 22), "⚡", fill=(0, 255, 140), font=get_font(18))
                elif cell == 2: # Power Core Box
                    draw.rounded_rectangle([tx + 8, ty + 8, tx + tile_sz - 8, ty + tile_sz - 8], radius=8, fill=(80, 50, 10), outline=(255, 170, 0), width=2)
                    draw.text((tx + 22, ty + 20), "CORE", fill=(255, 220, 0), font=get_font(12, bold=True))
                elif cell == 4: # Box on Target (Done)
                    draw.rounded_rectangle([tx + 8, ty + 8, tx + tile_sz - 8, ty + tile_sz - 8], radius=8, fill=(10, 80, 40), outline=(0, 255, 140), width=3)
                    draw.text((tx + 24, ty + 20), "OK!", fill=(255, 255, 255), font=get_font(13, bold=True))

        # Player
        px = ox + self.player_x * tile_sz
        py = oy + self.player_y * tile_sz
        draw.ellipse([px + 12, py + 12, px + tile_sz - 12, py + tile_sz - 12], fill=(0, 200, 255), outline=(255, 255, 255), width=2)
        draw.text((px + 24, py + 20), "🤖", fill=(255, 255, 255), font=get_font(18))

        # Right Telemetry
        rx = ox + self.grid_cols * tile_sz + 40
        draw.rounded_rectangle([rx, 130, w - 50, 600], radius=10, fill=(16, 22, 34), outline=(40, 65, 95))
        draw.text((rx + 20, 150), "STATUS OPERACJI:", fill=(0, 255, 200), font=get_font(16, bold=True))
        draw.text((rx + 20, 190), f"Cele: 2 / 2 rdzenie", fill=(220, 230, 245), font=get_font(14))
        draw.text((rx + 20, 225), f"Licznik ruchów: {self.moves}", fill=(220, 230, 245), font=get_font(14))
        draw.text((rx + 20, 260), f"Pchnięcia: {self.pushes}", fill=(255, 210, 0), font=get_font(14, bold=True))
        draw.text((rx + 20, 295), f"Czas sesji: 02:41", fill=(140, 170, 200), font=get_font(14))

        canvas.draw_badge(rx + 20, 360, "CEL: PRZESUŃ RDZENIE DO ⚡", bg_color=(20, 50, 40), text_color=(0, 255, 140))

    def handle_input(self, event: str) -> bool:
        dx, dy = 0, 0
        if event == "KEY_LEFT": dx = -1
        elif event == "KEY_RIGHT": dx = 1
        elif event == "KEY_UP": dy = -1
        elif event == "KEY_DOWN": dy = 1
        if dx != 0 or dy != 0:
            nx = self.player_x + dx
            ny = self.player_y + dy
            if 0 <= ny < self.grid_rows and 0 <= nx < self.grid_cols and self.grid[ny][nx] != 1:
                self.player_x = nx
                self.player_y = ny
                self.moves += 1
                return True
        return False
