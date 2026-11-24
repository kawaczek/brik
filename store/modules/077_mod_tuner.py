#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TunerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.note = "A4"
        self.target_hz = 440.0
        self.detected_hz = 440.2
        self.cents_diff = +0.8
        self.instrument = "GITARA STANDARD (E A D G B E)"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), f"🎸 077 // INSTRUMENT TUNER & PITCH GENERATOR // {self.instrument}", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "STROIK CHROMATYCZNY", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 90, 12, "IN TUNE", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big Tuning Arc / Strobe Card
        canvas.draw_card(20, 65, 620, 440, title="WSKAŹNIK DOSTROJENIA (CENTS DIFF)", subtitle="Dokładność ±0.1 centa // Algorytm autokorelacji YIN")
        draw.text((240, 140), self.note, fill=(0, 255, 136), font=get_font(96, bold=True))
        draw.text((230, 250), f"{self.detected_hz:.1f} Hz", fill=(255, 220, 0), font=get_font(28, bold=True))
        draw.text((205, 290), f"Różnica: {self.cents_diff:+.1f} centów (IDEALNIE)", fill=(0, 255, 180), font=get_font(16, bold=True))

        # Tuning Needle
        draw.rectangle([60, 350, 580, 380], fill=(16, 26, 40), outline=(0, 200, 255))
        center_x = 320
        needle_x = center_x + int(self.cents_diff * 4)
        draw.line([(center_x, 340), (center_x, 390)], fill=(120, 150, 180), width=2)
        draw.line([(needle_x, 345), (needle_x, 385)], fill=(0, 255, 136), width=4)
        draw.text((center_x - 12, 395), "0", fill=(0, 255, 136), font=get_font(14, bold=True))
        draw.text((80, 395), "-50 CENTS", fill=(100, 130, 160), font=get_font(12))
        draw.text((500, 395), "+50 CENTS", fill=(100, 130, 160), font=get_font(12))

        # Guitar Strings Card
        canvas.draw_card(660, 65, 344, 440, title="STRUNY GITAROWE", subtitle="Wybór struny docelowej")
        strings = [
            ("E2 (Najgrubsza)", "82.4 Hz"),
            ("A2", "110.0 Hz"),
            ("D3", "146.8 Hz"),
            ("G3", "196.0 Hz"),
            ("B3", "246.9 Hz"),
            ("E4 (Wiolinowa)", "329.6 Hz"),
        ]
        for i, (s_name, s_hz) in enumerate(strings):
            sy = 125 + i * 55
            draw.rectangle([675, sy, 985, sy + 48], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((690, sy + 14), s_name, fill=(240, 245, 255), font=get_font(14, bold=True))
            draw.text((890, sy + 14), s_hz, fill=(0, 255, 180), font=get_font(14))

        # Bottom Tone Generator Card
        canvas.draw_card(20, 520, 984, 190, title="GENERATOR WZORCOWEGO TONU ODNIESIENIA (PITCH GENERATOR)", subtitle="Czysty sinus A4 = 440 Hz (lub 432 Hz) na głośnikach stereo")
        draw.text((45, 580), "STAN GENERATORA: [AKTYWNY] // TON A4 = 440.0 HZ", fill=(0, 255, 180), font=get_font(16, bold=True))
        draw.text((45, 615), "Naciśnij [A] aby włączyć/wyłączyć ton referencyjny. Klawisz [X] przełącza strój na 432 Hz.", fill=(160, 185, 215), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmień Strunę / Nutę | [A]: Odtwórz Dźwięk Wzorcowy | [X]: Kalibracja A4 (440/432 Hz)", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
