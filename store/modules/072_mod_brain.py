#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class CyberBrainModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.score = 7
        self.high_score = 14
        self.reaction_time_ms = 214
        self.state = "TWÓJ RUCH // ODTWÓRZ SEKWENCJĘ PRZYCISKÓW"
        self.sequence = ["A", "X", "B", "Y", "A", "A", "B"]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 12, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), "🧠 072 // CYBER-SIMON BRAIN TRAINER & REACTION TEST", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"SERIA: {self.score}", bg_color=(20, 50, 40))
        canvas.draw_badge(w - 80, 12, f"{self.reaction_time_ms} MS", bg_color=(40, 30, 15), text_color=(255, 200, 0))

        # 4 Big Buttons in Diamond Layout (ABXY)
        canvas.draw_card(20, 65, 540, 440, title="POLE REAKCJI PRZYCISKÓW ABXY", subtitle="Zapamiętaj sekwencję błysków i dźwięków")
        draw.text((100, 130), self.state, fill=(0, 255, 180), font=get_font(14, bold=True))

        # Diamond buttons
        bx, by = 280, 280
        # X (North)
        draw.ellipse([(bx - 40, by - 120), (bx + 40, by - 40)], fill=(0, 140, 255), outline=(0, 240, 255), width=3)
        draw.text((bx - 10, by - 92), "X", fill=(255, 255, 255), font=get_font(26, bold=True))
        # Y (West)
        draw.ellipse([(bx - 120, by - 40), (bx - 40, by + 40)], fill=(0, 180, 100), outline=(0, 255, 140), width=3)
        draw.text((bx - 90, by - 12), "Y", fill=(255, 255, 255), font=get_font(26, bold=True))
        # A (East)
        draw.ellipse([(bx + 40, by - 40), (bx + 120, by + 40)], fill=(200, 0, 80), outline=(255, 0, 120), width=3)
        draw.text((bx + 70, by - 12), "A", fill=(255, 255, 255), font=get_font(26, bold=True))
        # B (South)
        draw.ellipse([(bx - 40, by + 40), (bx + 40, by + 120)], fill=(220, 160, 0), outline=(255, 220, 0), width=3)
        draw.text((bx - 10, by + 68), "B", fill=(255, 255, 255), font=get_font(26, bold=True))

        # Stats Card
        canvas.draw_card(580, 65, 424, 440, title="WYNIKI I REKORDY TRENINGU", subtitle="Pomiary neuro-kognitywne")
        draw.text((610, 140), f"AKTUALNA RUNDA: {self.score}", fill=(0, 255, 180), font=get_font(24, bold=True))
        draw.text((610, 190), f"REKORD SESJI:   {self.high_score}", fill=(255, 200, 0), font=get_font(24, bold=True))
        draw.text((610, 250), f"CZAS REAKCJI:   {self.reaction_time_ms} ms", fill=(0, 240, 255), font=get_font(22, bold=True))
        draw.text((610, 310), "Ocena refleksu: BARDZO SZYBKI (TOP 5%)", fill=(0, 255, 136), font=get_font(15, bold=True))
        draw.text((610, 345), "Średnia dla populacji: 260 - 300 ms.", fill=(160, 180, 210), font=get_font(14))

        # Bottom Instructions
        canvas.draw_card(20, 520, 984, 190, title="ZASADY TRENINGU MÓZGU", subtitle="Trening pamięci roboczej i refleksu ruchowego")
        draw.text((45, 580), "Konsola generuje rosnący ciąg sygnałów świetlnych i dźwiękowych. Każdy błąd resetuje rundę.", fill=(220, 235, 255), font=get_font(15))
        draw.text((45, 615), "Naciśnij [A], [B], [X] lub [Y] zgodnie z kolejnością pokazywaną przez system.", fill=(0, 255, 180), font=get_font(15, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "Klawisze ABXY: Wprowadź Kolor | [START]: Rozpocznij Nową Grę | [SELECT]: Tryb Tylko Refleks", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
