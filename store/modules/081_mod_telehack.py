#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TelehackBbsModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.terminal_lines = [
            "CONNECT 1200 / ARPANET GATEWAY IMP #4 (MIT-AI)",
            "Last login: Fri Oct 29 1982 from SRI-NIC",
            "Type 'help' for command summary.",
            "",
            "> wardial 213-555-0100",
            "Scanning prefix (213) 555-0100 ... DIALING...",
            "Carrier detected at 213-555-0142! [WOPR MAINFRAME]",
            "",
            "LOGON: Joshua",
            "GREETINGS PROFESSOR FALKEN.",
            "SHALL WE PLAY A GAME?",
            "> 1. GLOBAL THERMONUCLEAR WAR",
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((4, 10, 6, 255)) # Green phosphor CRT

        draw.rectangle([0, 0, w, 50], fill=(8, 16, 10, 255), outline=(0, 255, 136, 100), width=1)
        draw.text((20, 14), "📠 081 // 80S ARPANET BBS & WARDIALER // VT100 PHOSPHOR CRT", fill=(0, 255, 136), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "MODEM: 1200 BAUD", bg_color=(10, 40, 20), text_color=(0, 255, 136))
        canvas.draw_badge(w - 80, 12, "WARGAMES", bg_color=(20, 45, 25))

        # Big Retro Green CRT Screen
        canvas.draw_card(20, 65, 984, 640, title="TERMINAL TEKSTOWY TELEHACK / WOPR", subtitle="Autentyczna symulacja sieci z lat 80. z filmami ASCII i botem ELIZA")
        ty = 130
        for line in self.terminal_lines:
            col = (255, 220, 0) if "SHALL WE" in line or "GLOBAL" in line else (0, 255, 136)
            draw.text((45, ty), line, fill=col, font=get_font(17, bold=(">" in line or "CARRIER" in line)))
            ty += 34
        # Blinking CRT block cursor
        draw.rectangle([45, ty + 5, 60, ty + 25], fill=(0, 255, 136))

        draw.rectangle([0, 724, w, 768], fill=(8, 16, 10, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Terminal | [A]: Wyślij Komendę | [X]: Uruchom Wardialer | [Y]: Rozmowa z ELIZA", fill=(0, 200, 110), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
