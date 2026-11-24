#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TachometerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.target_rpm = 1200
        self.freq_hz = 20.0
        self.duty_cycle = 10
        self.running = False

    def update(self, dt: float):
        self.freq_hz = self.target_rpm / 60.0

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 12, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🌀 054 // STROBOSKOPOWY OBROTOMIERZ OPTYCZNY RPM", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "BEZDOTYKOWY POMIAR", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "60 HZ", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main RPM Gauge Card
        canvas.draw_card(20, 65, 600, 450, title="CZĘSTOTLIWOŚĆ BŁYSKÓW STROBOSKOPU", subtitle="Skieruj ekran IPS na wirujące śmigło/wentylator")
        draw.text((130, 140), f"{self.target_rpm}", fill=(0, 255, 180), font=get_font(96, bold=True))
        draw.text((430, 205), "RPM", fill=(0, 200, 255), font=get_font(32, bold=True))
        draw.text((135, 275), f"Częstotliwość migania: {self.freq_hz:.2f} Hz", fill=(255, 220, 0), font=get_font(22, bold=True))
        draw.text((135, 315), f"Wypełnienie impulsu (Duty): {self.duty_cycle}% (Ostre krawędzie)", fill=(140, 170, 200), font=get_font(16))
        draw.text((70, 390), "Zasada: Gdy obracający się element wydaje się stać w miejscu,", fill=(180, 200, 230), font=get_font(14))
        draw.text((70, 415), "częstotliwość błysków równa się rzeczywistym obrotom RPM.", fill=(0, 255, 180), font=get_font(14, bold=True))

        # Preset Speeds & Quick Jumps
        canvas.draw_card(640, 65, 364, 450, title="SZYBKIE NASTAWY WARSZTATOWE", subtitle="Standardowe prędkości silników")
        presets = [
            ("Wentylator PC 120mm", "1200 RPM", "20.0 Hz"),
            ("Wentylator Wysokoobrotowy", "2400 RPM", "40.0 Hz"),
            ("Silnik Krokowy NEMA 17", "600 RPM", "10.0 Hz"),
            ("Wrzeciono CNC Dremel", "3600 RPM", "60.0 Hz"),
        ]
        for i, (p_name, p_rpm, p_hz) in enumerate(presets):
            cy = 135 + i * 75
            draw.rectangle([660, cy, 980, cy + 65], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((675, cy + 12), p_name, fill=(220, 235, 255), font=get_font(13, bold=True))
            draw.text((675, cy + 34), p_rpm, fill=(0, 255, 180), font=get_font(16, bold=True))
            draw.text((880, cy + 34), p_hz, fill=(255, 200, 0), font=get_font(14))

        # Bottom Instructions
        canvas.draw_card(20, 530, 984, 180, title="INSTRUKCJA BEZPIECZEŃSTWA", subtitle="Ostrzeżenie przed epilepsją fotogenną")
        draw.text((40, 595), "⚠️ UWAGA: Moduł generuje impulsy świetlne o wysokiej częstotliwości.", fill=(255, 80, 80), font=get_font(15, bold=True))
        draw.text((40, 625), "Nie używać w obecności osób wrażliwych na migające światło. Trzymaj ekran 10 cm od badanego obiektu.", fill=(160, 180, 210), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Dokładna regulacja ±10 RPM | Góra/Dół: ±100 RPM | [A]: Włącz/Wyłącz Stroboskop", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "LEFT"):
            self.target_rpm = max(60, self.target_rpm - 10); return True
        elif event in ("KEY_RIGHT", "RIGHT"):
            self.target_rpm = min(7200, self.target_rpm + 10); return True
        elif event in ("KEY_UP", "UP"):
            self.target_rpm = min(7200, self.target_rpm + 100); return True
        elif event in ("KEY_DOWN", "DOWN"):
            self.target_rpm = max(60, self.target_rpm - 100); return True
        return False
