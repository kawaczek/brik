#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class OpticsCalcModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.aperture_mm = 200.0  # 8" Dobson
        self.focal_len_mm = 1200.0
        self.eyepiece_mm = 10.0

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🔭 064 // KALKULATOR OPTYKI TELESKOPOWEJ & ASTROFOTOGRAFII", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, '8" NEWTON DOBSON', bg_color=(20, 45, 65))
        canvas.draw_badge(w - 90, 12, "F/6.0", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Parameters Card
        canvas.draw_card(20, 65, 480, 440, title="PARAMETRY TELESKOPU & OKULARU", subtitle="Apertura i ogniskowa toru optycznego")
        mag = self.focal_len_mm / self.eyepiece_mm
        exit_pupil = self.aperture_mm / mag
        dawes_limit = 116.0 / self.aperture_mm
        draw.text((45, 130), f"Apertura (Średnica zwierciadła): {self.aperture_mm:.0f} mm", fill=(240, 245, 255), font=get_font(16))
        draw.text((45, 165), f"Ogniskowa teleskopu: {self.focal_len_mm:.0f} mm", fill=(240, 245, 255), font=get_font(16))
        draw.text((45, 200), f"Ogniskowa okularu: {self.eyepiece_mm:.0f} mm", fill=(255, 200, 0), font=get_font(16, bold=True))

        draw.rectangle([45, 250, 455, 410], fill=(14, 22, 34), outline=(0, 255, 180), width=2)
        draw.text((65, 275), f"POWIĘKSZENIE OPTYCZNE: {mag:.0f}x", fill=(0, 255, 180), font=get_font(22, bold=True))
        draw.text((65, 315), f"Źrenica wyjściowa: {exit_pupil:.2f} mm (Oko ludzkie: 5-7 mm)", fill=(0, 240, 255), font=get_font(15))
        draw.text((65, 355), f"Rozdzielczość (Kryterium Dawesa): {dawes_limit:.2f} arcsec", fill=(255, 220, 0), font=get_font(16, bold=True))

        # Astrophotography Rule 500 / NPF Card
        canvas.draw_card(520, 65, 484, 440, title="CZAS NAŚWIETLANIA (REGUŁA 500 & NPF)", subtitle="Maksymalny czas bez widocznego poruszenia gwiazd")
        t_500 = 500.0 / self.focal_len_mm
        draw.text((545, 130), f"Maksymalny czas naświetlania: {t_500:.2f} sek.", fill=(0, 255, 136), font=get_font(24, bold=True))
        draw.text((545, 175), "Zasięg gwiazdowy (Limiting Mag): 14.2 mag", fill=(220, 235, 255), font=get_font(16))
        draw.text((545, 215), "Pole widzenia (True FOV z okularem 52°): 0.43° (Księżyc mieści się w całości)", fill=(160, 185, 215), font=get_font(14))

        # Bottom Filters Guide
        canvas.draw_card(20, 520, 984, 190, title="REKOMENDOWANE FILTRY MGŁAWICOWE (O-III / UHC / H-ALPHA)", subtitle="Kontrast przy zanieczyszczeniu światłem (Bortle Scale 5)")
        draw.text((45, 580), "Zalecany filtr wąskopasmowy: Baader O-III (501 nm) dla mgławic planetarnych.", fill=(0, 255, 200), font=get_font(15, bold=True))
        draw.text((45, 615), "Filtr polaryzacyjny: Niezbędny do obserwacji powierzchni Księżyca w kwadrze.", fill=(160, 180, 210), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Góra/Dół: Zmiana Okularu | Lewo/Prawo: Zmiana Apertury | [A]: Wybierz Sensor Kamery", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
