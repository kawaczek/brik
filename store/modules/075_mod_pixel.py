#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class PixelArtModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.grid_sz = 16
        self.cursor_x = 8
        self.cursor_y = 8
        self.palette = [
            (0, 0, 0), (255, 255, 255), (0, 240, 255), (0, 255, 136),
            (255, 200, 0), (255, 60, 60), (180, 80, 255), (100, 120, 150)
        ]
        self.selected_color = 2
        self.pixels = [[0 for _ in range(16)] for _ in range(16)]
        # Draw mock heart/icon
        for x, y in [(5,5), (6,4), (7,4), (8,5), (9,4), (10,4), (11,5), (6,6), (7,7), (8,8), (9,7), (10,6)]:
            self.pixels[y][x] = 5

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🎨 075 // PIXEL ART STUDIO & SPRITE PAINTER (16x16)", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "SIATKA 16x16 PIKSELI", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "8 BARW", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main 16x16 Canvas Area
        canvas.draw_card(20, 65, 600, 640, title="OBSZAR RYSOWANIA SPRITE'A", subtitle="Ruch kursorem D-Padem, malowanie klawiszem [A]")
        cx, cy, sz = 80, 140, 30
        for y in range(16):
            for x in range(16):
                col = self.palette[self.pixels[y][x]]
                draw.rectangle([cx + x * sz, cy + y * sz, cx + (x + 1) * sz - 1, cy + (y + 1) * sz - 1], fill=col)
        # Cursor marker
        draw.rectangle([cx + self.cursor_x * sz, cy + self.cursor_y * sz, cx + (self.cursor_x + 1) * sz, cy + (self.cursor_y + 1) * sz], outline=(255, 255, 0), width=3)

        # Right Palette & Tools Card
        canvas.draw_card(640, 65, 364, 640, title="PALETA BARW I EKSPORT", subtitle="Wybór koloru pędzla pod [X]")
        draw.text((665, 130), "AKTYWNA PALETA CYBERPUNK:", fill=(140, 170, 200), font=get_font(13))
        for i, col in enumerate(self.palette):
            px = 665 + (i % 4) * 75
            py = 160 + (i // 4) * 75
            is_sel = (i == self.selected_color)
            draw.rectangle([px, py, px + 60, py + 60], fill=col, outline=(255, 255, 0) if is_sel else (40, 60, 85), width=3 if is_sel else 1)

        draw.text((665, 340), "FORMATY ZAPISU NA KARTĘ SD:", fill=(140, 170, 200), font=get_font(13))
        draw.text((665, 370), "• Plik obrazu PNG (16x16 lub skalowany)", fill=(240, 245, 255), font=get_font(14))
        draw.text((665, 400), "• Tablica bajtów w C (const uint16_t sprite[])", fill=(240, 245, 255), font=get_font(14))
        draw.text((665, 430), "• Tablica pikseli w Pythonie (.py)", fill=(240, 245, 255), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Ruch Pędzlem | [A]: Postaw Piksel | [B]: Gumka | [X]: Zmień Kolor | [Y]: Eksport PNG", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "LEFT"):
            self.cursor_x = max(0, self.cursor_x - 1); return True
        elif event in ("KEY_RIGHT", "RIGHT"):
            self.cursor_x = min(15, self.cursor_x + 1); return True
        elif event in ("KEY_UP", "UP"):
            self.cursor_y = max(0, self.cursor_y - 1); return True
        elif event in ("KEY_DOWN", "DOWN"):
            self.cursor_y = min(15, self.cursor_y + 1); return True
        elif event in ("KEY_A", "a"):
            self.pixels[self.cursor_y][self.cursor_x] = self.selected_color; return True
        return False
