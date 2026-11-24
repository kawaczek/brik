#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class UnicodeInspectorModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.code_point = 0x2588
        self.char_name = "FULL BLOCK"
        self.category = "Block Elements (U+2580..U+259F)"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🔤 069 // UNICODE & UTF-8 CHARACTER INSPECTOR // U+{self.code_point:04X}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "UNICODE 15.1", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 80, 12, "3 BAJTY", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big Char Preview Box
        canvas.draw_card(20, 65, 400, 440, title="PODGLĄD GLYPHU (RENDER)", subtitle=f"Punkt kodowy U+{self.code_point:04X}")
        draw.rectangle([60, 130, 380, 370], fill=(16, 26, 42), outline=(0, 240, 255), width=2)
        draw.text((150, 180), "█", fill=(0, 255, 180), font=get_font(120, bold=True))
        draw.text((120, 420), f"ZNAK: '█' (KOD 0x{self.code_point:04X})", fill=(255, 200, 0), font=get_font(16, bold=True))

        # Encoding Details Card
        canvas.draw_card(440, 65, 564, 440, title="KODOWANIA CYFROWE I ENTYCJE", subtitle=self.char_name)
        details = [
            ("NAZWA OFICJALNA:", self.char_name),
            ("KATEGORIA UNICODE:", self.category),
            ("SEKWENCJA BAJTÓW UTF-8:", "0xE2 0x96 0x88 (Binarne: 11100010 10010110 10001000)"),
            ("KODOWANIE UTF-16:", "0x2588"),
            ("KODOWANIE UTF-32:", "0x00002588"),
            ("ENCJA HTML:", "&block;  lub  &#9608;"),
            ("ESCAPE C / PYTHON:", "\\u2588"),
        ]
        for i, (k, v) in enumerate(details):
            py = 125 + i * 46
            draw.text((460, py), k, fill=(140, 170, 200), font=get_font(12, bold=True))
            draw.text((460, py + 18), v, fill=(0, 255, 180) if "UTF" in k else (240, 245, 255), font=get_font(14))

        # Bottom Glyph Table Preview
        canvas.draw_card(20, 520, 984, 190, title="RAMKI PSEUDOGRAFICZNE CP437 & SYMBOLE TECHNICZNE", subtitle="Elementy interfejsów TUI / Cyberdeck")
        sample_chars = ["─", "│", "┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼", "▀", "▄", "█", "▌", "▐", "░", "▒", "▓", "■", "▲", "▼", "◄", "►"]
        for i, ch in enumerate(sample_chars):
            cx = 45 + i * 39
            draw.rectangle([cx, 580, cx + 32, 650], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((cx + 8, 600), ch, fill=(0, 255, 180), font=get_font(20, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Następny Znak | Góra/Dół: ±16 Znaków | [A]: Wprowadź Hex | [Y]: Kopiuj Kod", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "LEFT"):
            self.code_point = max(0, self.code_point - 1); return True
        elif event in ("KEY_RIGHT", "RIGHT"):
            self.code_point = min(0x10FFFF, self.code_point + 1); return True
        return False
