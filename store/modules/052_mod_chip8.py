#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class Chip8Module(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.rom_name = "PONG.CH8"
        self.pc = 0x0200
        self.i_reg = 0x0250
        self.delay_timer = 60
        self.sound_timer = 0
        self.fps = 60
        self.screen_grid = [[1 if (x+y)%7==0 else 0 for x in range(64)] for y in range(32)]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((6, 10, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🕹️ 052 // CHIP-8 RETRO VIRTUAL MACHINE // ROM: {self.rom_name}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 200, 12, "CPU: 500 HZ", bg_color=(20, 40, 60))
        canvas.draw_badge(w - 80, 12, "60 FPS", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big 64x32 Monochrome Screen
        canvas.draw_card(20, 65, 680, 460, title="EKRAN WIRTUALNY 64x32 PIKSELE", subtitle="Bezpośredni bufor graficzny CHIP-8")
        sx, sy, sz = 40, 120, 9.8
        draw.rectangle([sx, sy, sx + 64 * sz, sy + 32 * sz], fill=(4, 8, 14), outline=(0, 240, 255), width=2)
        for y in range(32):
            for x in range(64):
                if self.screen_grid[y][x]:
                    draw.rectangle([sx + x * sz, sy + y * sz, sx + (x + 1) * sz - 1, sy + (y + 1) * sz - 1], fill=(0, 255, 180))

        # CPU Registers & Disassembly
        canvas.draw_card(720, 65, 284, 460, title="REJESTRY & STAN CPU", subtitle="Architektura CHIP-8 (1977)")
        draw.text((740, 125), f"PC:  0x{self.pc:04X}", fill=(0, 255, 136), font=get_font(14, bold=True))
        draw.text((740, 150), f"I:   0x{self.i_reg:04X}", fill=(0, 255, 136), font=get_font(14, bold=True))
        draw.text((740, 175), f"DT:  {self.delay_timer}", fill=(255, 200, 0), font=get_font(14))
        draw.text((740, 200), f"ST:  {self.sound_timer}", fill=(255, 200, 0), font=get_font(14))
        draw.text((740, 235), "REJESTRY V0 - VF:", fill=(140, 170, 210), font=get_font(13))
        for r in range(8):
            draw.text((740, 260 + r * 22), f"V{r:X}: 0x00    V{r+8:X}: 0x00", fill=(180, 200, 230), font=get_font(12))

        # Bottom Game Selector & Controls
        canvas.draw_card(20, 540, 984, 170, title="STEROWANIE GRĄ & WYBÓR ROMU", subtitle="Mapowanie klawiatury heksadecymalnej 4x4 na D-Pad i ABXY")
        draw.text((40, 600), "D-Pad Góra/Dół: Paletka Gracza 1 | Klawisz A: Serwuj Piłkę | Klawisz B: Reset Gry", fill=(0, 255, 180), font=get_font(15, bold=True))
        draw.text((40, 635), "Dostępne ROMy na karcie SD: PONG.CH8, TETRIS.CH8, INVADERS.CH8, BLINKY.CH8, BRIX.CH8", fill=(140, 170, 200), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Ruch w grze | [A]: Akcja | [Y]: Wybierz Inny ROM CHIP-8", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
