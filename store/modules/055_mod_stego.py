#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class StegoModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.filename = "secret_carrier_photo.png"
        self.status = "UKRYTA WIADOMOŚĆ WYKRYTA (LSB EMBEDDED)"
        self.extracted_text = "KLUCZ_EWAKUACJI_BRAVO_2026_SEKTOR_9 // KOD_AUTORYZACJI: #77F2-99B1"
        self.bits_per_channel = 1
        self.payload_size = 64

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🖼️ 055 // STEGANOGRAFIA OBRAZOWA LSB (LEAST SIGNIFICANT BIT) // {self.filename}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 200, 12, "LSB 1-BIT RGB", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "64 B", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Carrier Image Simulation Box
        canvas.draw_card(20, 65, 450, 440, title="NOŚNIK GRAFICZNY (CARRIER)", subtitle="Wizualny podgląd pliku PNG z karty SD")
        draw.rectangle([40, 120, 450, 480], fill=(18, 28, 44), outline=(0, 180, 220))
        # Visual mock noise
        for y in range(130, 470, 15):
            for x in range(50, 440, 15):
                draw.rectangle([x, y, x + 8, y + 8], fill=(25, 45, 75))
        draw.text((120, 280), "[OBRAZ NOŚNIKA 1024x768]", fill=(120, 160, 210), font=get_font(15, bold=True))
        draw.text((95, 310), "Różnica wizualna dla oka: 0.00% (Niewidoczna)", fill=(0, 255, 136), font=get_font(12))

        # Extracted Payload Card
        canvas.draw_card(490, 65, 514, 440, title="WYODRĘBNIONE DANE TEKSTOWE", subtitle="Zdekodowane bajty z najmłodszych bitów kanałów R, G, B")
        draw.rectangle([510, 130, 980, 270], fill=(14, 20, 30), outline=(0, 255, 180), width=2)
        draw.text((525, 150), "ZDEKODOWANY TEKST:", fill=(255, 170, 0), font=get_font(13, bold=True))
        draw.text((525, 185), self.extracted_text[:40], fill=(0, 255, 200), font=get_font(15, bold=True))
        draw.text((525, 215), self.extracted_text[40:], fill=(0, 255, 200), font=get_font(15, bold=True))

        draw.text((510, 300), "STATYSTYKI NOŚNIKA LSB:", fill=(140, 170, 205), font=get_font(14, bold=True))
        draw.text((510, 330), f"Pojemność nośnika: 294 912 bajtów (288 KB)", fill=(160, 185, 215), font=get_font(14))
        draw.text((510, 360), f"Wykorzystano bitów: {self.payload_size * 8} / 2 359 296 (0.02%)", fill=(160, 185, 215), font=get_font(14))
        draw.text((510, 390), "Entropia Shannona: 7.9984 bit/bajt (Optymalna)", fill=(0, 255, 136), font=get_font(14))

        # Bottom Stego Inspector Mode
        canvas.draw_card(20, 520, 984, 190, title="ANALIZATOR ENTROPII I WYKRYWACZ STEGO (CHI-SQUARE)", subtitle="Test statystyczny Chi-Kwadrat na obecność ukrytej steganografii")
        draw.text((40, 580), "Współczynnik anomalii bitowej: 0.984 -> Prawdopodobieństwo steganografii: 99.2%", fill=(255, 200, 0), font=get_font(15, bold=True))
        draw.rectangle([40, 620, 960, 650], fill=(20, 30, 45))
        draw.rectangle([40, 620, 40 + int(920 * 0.992), 650], fill=(255, 170, 0))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Obraz PNG | [A]: Ekstrakcja Wiadomości LSB | [Y]: Ukryj Nowy Tekst", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
