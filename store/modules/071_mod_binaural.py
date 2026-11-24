#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class BinauralModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.preset = "GŁĘBOKIE SKUPIENIE (ALPHA 10 HZ)"
        self.base_freq = 210.0 # Left ear Hz
        self.beat_freq = 10.0  # Right ear = 220 Hz
        self.noise_type = "SZUM RÓŻOWY (PINK NOISE)"
        self.playing = True

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🎧 071 // BINAURAL BEATS NEURO-SYNTH // DUDNIENIA RÓŻNICOWE", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "SŁUCHAWKI STEREO", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 90, 12, "ALPHA 10 HZ", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big Frequency Visualizer Card
        canvas.draw_card(20, 65, 600, 440, title="PARAMETRY TONÓW BINAURALNYCH", subtitle="Wymagane podłączenie słuchawek stereo przez gniazdo jack 3.5mm")
        draw.text((50, 135), self.preset, fill=(0, 255, 180), font=get_font(22, bold=True))
        draw.text((50, 190), f"Lewy kanał:  {self.base_freq:.1f} Hz (Fala nośna)", fill=(0, 200, 255), font=get_font(18))
        draw.text((50, 230), f"Prawy kanał: {self.base_freq + self.beat_freq:.1f} Hz (Fala nośna + dudnienie)", fill=(0, 200, 255), font=get_font(18))
        draw.rectangle([50, 280, 560, 370], fill=(14, 22, 34), outline=(0, 255, 180), width=2)
        draw.text((70, 300), f"Częstotliwość fali mózgowej: {self.beat_freq:.1f} Hz (Fale Alpha)", fill=(255, 200, 0), font=get_font(20, bold=True))
        draw.text((70, 335), "Stan umysłu: Relaksacja, kreatywność, szybkie przyswajanie wiedzy.", fill=(180, 205, 235), font=get_font(14))

        # Noise Generator Card
        canvas.draw_card(640, 65, 364, 440, title="GENERATOR TŁA DŹWIĘKOWEGO", subtitle="Maskowanie hałasów zewnętrznych")
        noises = [
            ("Szum Różowy (Pink)", "1/f spadek mocy", True),
            ("Szum Brązowy (Brown)", "Głęboki bas / wodospad", False),
            ("Szum Biały (White)", "Pełne spektrum pasma", False),
            ("Dźwięk Deszczu", "Akustyczny relaks", False),
        ]
        for i, (n_name, n_desc, is_act) in enumerate(noises):
            ny = 135 + i * 75
            draw.rectangle([660, ny, 980, ny + 65], fill=(16, 26, 42) if is_act else (12, 16, 26), outline=(0, 255, 180) if is_act else (40, 60, 85))
            draw.text((675, ny + 12), n_name, fill=(0, 255, 180) if is_act else (200, 220, 245), font=get_font(14, bold=True))
            draw.text((675, ny + 35), n_desc, fill=(120, 150, 180), font=get_font(12))

        # Bottom Presets
        canvas.draw_card(20, 520, 984, 190, title="ZAKRESY CZĘSTOTLIWOŚCI BIOELEKTRYCZNYCH MÓZGU (EEG)", subtitle="Wybierz pożądany stan neurobiologiczny")
        draw.text((45, 580), "• DELTA (0.5-4 Hz): Głęboki sen  |  • THETA (4-8 Hz): Medytacja i pamięć  |  • ALPHA (8-13 Hz): Skupienie", fill=(220, 235, 255), font=get_font(15))
        draw.text((45, 615), "• BETA (13-30 Hz): Czujność i analiza  |  • GAMMA (30-50 Hz): Szczytowa percepcja poznawcza", fill=(255, 200, 0), font=get_font(15, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmiana Zakresu Fal | [A]: Start / Stop Dźwięku | [Y]: Typ Szumu Tła", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
