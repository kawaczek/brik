#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class PunchcardModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.code_text = "HELLO BRICKDECK 2026 // RETRO-COMPUTING IBM 029"
        self.card_type = "IBM 80-COLUMN EBCDIC"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((12, 14, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(18, 22, 32, 255), outline=(220, 180, 100, 100), width=1)
        draw.text((20, 14), "💾 060 // WIRTUALNE KARTY PERFOROWANE & DŹWIĘK KASETOWY", fill=(255, 200, 100), font=get_font(18, bold=True))
        canvas.draw_badge(w - 240, 12, "KARTA IBM 5081", bg_color=(45, 35, 20))
        canvas.draw_badge(w - 75, 12, "80 KOL", bg_color=(35, 45, 60))

        # Main IBM 80-column Punchcard
        canvas.draw_card(20, 65, 984, 420, title="PERFOROWANA KARTA TEKTUROWA IBM 80 KOLUMN", subtitle="Kodowanie EBCDIC // Dziurkowanie pod programy FORTRAN / COBOL")
        cx, cy, cw, ch = 40, 120, 944, 340
        draw.rectangle([cx, cy, cx + cw, cy + ch], fill=(235, 220, 185), outline=(180, 160, 120), width=2)
        # Top text printed by card punch
        draw.text((cx + 30, cy + 20), self.code_text, fill=(40, 40, 40), font=get_font(16, bold=True))
        # Punch holes simulation
        for col in range(len(self.code_text)):
            hx = cx + 35 + col * 18
            draw.rectangle([hx, cy + 70, hx + 8, cy + 86], fill=(20, 20, 20)) # Zone punch
            draw.rectangle([hx, cy + 140, hx + 8, cy + 156], fill=(20, 20, 20)) # Digit punch
        draw.text((cx + cw - 180, cy + ch - 35), "IBM 5081 FORTRAN", fill=(100, 90, 70), font=get_font(12, bold=True))

        # Cassette Tape Audio Synthesizer Mode
        canvas.draw_card(20, 500, 984, 210, title="SYNTEZATOR DŹWIĘKU MODEMU KASETOWEGO (ZX SPECTRUM / C64)", subtitle="Generowanie pisku i modulacji FSK na głośnikach stereo")
        draw.text((45, 560), "STAN TAŚMY: [GOTOWA DO ODTWORZENIA] // MODULACJA KANSAS CITY STANDARD (300 BD)", fill=(0, 255, 180), font=get_font(15, bold=True))
        draw.text((45, 595), "Ton prowadzący (Pilot Tone): 1200 Hz | Bit '0': 1 cykl 1200 Hz | Bit '1': 2 cykle 2400 Hz", fill=(160, 185, 215), font=get_font(14))
        draw.text((45, 630), "Naciśnij [A] aby wygenerować autentyczny pisk ładowania gry retro na głośnikach.", fill=(255, 200, 0), font=get_font(14, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmień Tekst Karty | [A]: Odtwórz Dźwięk Taśmy Kasetowej | [X]: Eksport do Karty SD", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
