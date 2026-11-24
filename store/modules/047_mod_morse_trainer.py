#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class MorseTrainerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.wpm = 20
        self.freq_hz = 700
        self.current_char = "K"
        self.morse_code = "-.-"
        self.koch_lesson = 5
        self.score = 92
        self.history = ["K  -.-  OK", "M  --   OK", "R  .-.  OK", "S  ...  OK", "U  ..-  BŁĄD"]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(255, 170, 0, 100), width=1)
        draw.text((20, 14), "📻 047 // MORSE CODE AUDIO TRAINER (METODA KOCHA)", fill=(255, 170, 0), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"TEMPO: {self.wpm} WPM", bg_color=(40, 30, 10), text_color=(255, 200, 0))
        canvas.draw_badge(w - 90, 12, f"{self.score}%", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big Training Display
        canvas.draw_card(20, 65, 600, 450, title="BIEŻĄCY ZNAK TELEGRAFICZNY", subtitle="Metoda Kocha // Słuchaj tonu i wciśnij klawisz")
        draw.text((230, 160), self.current_char, fill=(0, 240, 255), font=get_font(90, bold=True))
        draw.text((215, 280), f"KOD:  {self.morse_code}", fill=(255, 220, 0), font=get_font(36, bold=True))
        draw.text((160, 360), f"Dźwięk: {self.freq_hz} Hz // Ton sinusoidalny", fill=(140, 170, 205), font=get_font(15))
        draw.rectangle([60, 410, 560, 435], fill=(20, 30, 45), outline=(0, 200, 255))
        draw.rectangle([60, 410, 60 + int(500 * (self.score / 100.0)), 435], fill=(0, 255, 136))
        draw.text((75, 415), f"Skuteczność lekcji {self.koch_lesson}: {self.score}% (Wymagane >90% do awansu)", fill=(10, 20, 30), font=get_font(12, bold=True))

        # Right History Card
        canvas.draw_card(640, 65, 364, 450, title="HISTORIA ODBIORU", subtitle="Ostatnie zdekodowane symbole")
        for i, h_item in enumerate(self.history):
            col = (0, 255, 136) if "OK" in h_item else (255, 80, 80)
            draw.text((660, 130 + i * 45), f"#{i+1}: {h_item}", fill=col, font=get_font(18, bold=True))

        # Bottom Audio Keyer Mode
        canvas.draw_card(20, 530, 984, 180, title="TRYB KLUCZA SZTORCOWEGO & PROSTOTY (MANUAL CW)", subtitle="Naciśnij [A] aby nadać sygnał na głośnikach konsoli")
        draw.text((40, 595), "STAN KLUCZA: [ZWOLNIONY] // OCZEKIWANIE NA IMPULS", fill=(0, 255, 200), font=get_font(16, bold=True))
        draw.text((40, 630), "Alfabet: A (.-) B (-...) C (-.-.) D (-..) E (.) F (..-.) G (--.) H (....) I (..) J (.---) K (-.-)", fill=(140, 160, 190), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Tempo WPM | [A]: Odtwórz Znak / Kluczuj | [Y]: Kolejna Lekcja Kocha", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "LEFT"):
            self.wpm = max(5, self.wpm - 1); return True
        elif event in ("KEY_RIGHT", "RIGHT"):
            self.wpm = min(40, self.wpm + 1); return True
        return False
