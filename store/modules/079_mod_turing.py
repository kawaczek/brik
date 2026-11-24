#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TuringMachineModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.program_name = "INKREMENTACJA LICZBY BINARNEJ (+1)"
        self.head_pos = 9
        self.state = "q1"
        self.step_count = 14
        self.tape = ["0", "0", "1", "1", "0", "1", "0", "1", "1", "1", "0", "0", "0", "0", "0", "0", "0", "0"]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), f"🧠 079 // TURING MACHINE SIMULATOR // {self.program_name}", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"STAN: {self.state}", bg_color=(20, 50, 40))
        canvas.draw_badge(w - 90, 12, f"KROK: {self.step_count}", bg_color=(35, 45, 65))

        # Main Infinite Tape Box
        canvas.draw_card(20, 65, 984, 280, title="PRZESUWNA TAŚMA WIRTUALNA & GŁOWICA (R/W HEAD)", subtitle="Model matematyczny uniwersalnego komputera Alana Turinga (1936)")
        # Tape Cells
        cell_w = 48
        for i, val in enumerate(self.tape):
            cx = 40 + i * cell_w
            is_head = (i == self.head_pos)
            bg = (0, 80, 140) if is_head else (16, 26, 40)
            border = (0, 255, 180) if is_head else (40, 60, 85)
            draw.rectangle([cx, 160, cx + cell_w - 4, 230], fill=bg, outline=border, width=2 if is_head else 1)
            draw.text((cx + 14, 175), val, fill=(255, 255, 255), font=get_font(32, bold=True))
            if is_head:
                # Arrow pointing to active cell
                draw.polygon([(cx + 22, 145), (cx + 10, 125), (cx + 34, 125)], fill=(255, 200, 0))
                draw.text((cx - 8, 105), f"GŁOWICA [{self.state}]", fill=(255, 200, 0), font=get_font(12, bold=True))

        # State Transition Table Card
        canvas.draw_card(20, 360, 984, 345, title="TABLICA PRZEJŚĆ AUTOMATU (TRANSITION RULES)", subtitle="Reguły: (Stan bieżący, Znak) -> (Nowy stan, Zapis, Ruch L/R)")
        rules = [
            ("(q0, 0) -> (q0, 0, R)", "Przewijaj w prawo do końca liczby"),
            ("(q0, 1) -> (q0, 1, R)", "Przewijaj w prawo do końca liczby"),
            ("(q0, B) -> (q1, B, L)", "Koniec liczby znaleziony, cofnij o 1"),
            ("(q1, 0) -> (q_halt, 1, N)", "Zamień 0 na 1 i zatrzymaj maszynę"),
            ("(q1, 1) -> (q1, 0, L)", "Przeniesienie: zamień 1 na 0 i idź w lewo"),
        ]
        for i, (rule, desc) in enumerate(rules):
            ry = 425 + i * 52
            draw.rectangle([40, ry, 980, ry + 44], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((60, ry + 12), rule, fill=(0, 255, 180), font=get_font(15, bold=True))
            draw.text((450, ry + 12), f"// {desc}", fill=(160, 185, 215), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przesuń Taśmę | [A]: Wykonaj Jeden Krok | [X]: Autoodtwarzanie (Run) | [B]: Reset Taśmy", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
