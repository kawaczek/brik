#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AirQualityModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.city = "Gorzów Wielkopolski"
        self.aqi = 28
        self.status = "DOBRA (GOOD)"
        self.pm25 = 7.4
        self.pm10 = 14.2
        self.o3 = 45.1
        self.no2 = 12.8
        self.so2 = 3.1
        self.history = [35, 32, 28, 25, 22, 24, 28, 30, 28]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 16, 24, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 22, 34, 255), outline=(0, 255, 136, 100), width=1)
        draw.text((20, 14), f"🌱 048 // GLOBAL AIR QUALITY & SMOG RADAR // {self.city.upper()}", fill=(0, 255, 136), font=get_font(18, bold=True))
        canvas.draw_badge(w - 200, 12, "GIOŚ / OPENAQ", bg_color=(20, 45, 35))
        canvas.draw_badge(w - 75, 12, "LIVE", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main Index Card
        canvas.draw_card(20, 65, 400, 440, title="INDEKS JAKOŚCI POWIETRZA (AQI)", subtitle="Europejski Indeks Czystości Powietrza")
        draw.text((120, 140), str(self.aqi), fill=(0, 255, 136), font=get_font(84, bold=True))
        draw.text((90, 250), self.status, fill=(0, 255, 180), font=get_font(22, bold=True))
        draw.text((45, 310), "Zanieczyszczenie pyłowe w normie.", fill=(160, 185, 215), font=get_font(15))
        draw.text((45, 340), "Zalecana aktywność na świeżym powietrzu.", fill=(160, 185, 215), font=get_font(15))
        draw.rectangle([45, 410, 375, 430], fill=(20, 30, 45))
        draw.rectangle([45, 410, 45 + int(330 * (self.aqi / 100.0)), 430], fill=(0, 255, 136))

        # Pollutant Detailed Grid
        canvas.draw_card(440, 65, 564, 440, title="STĘŻENIA PYŁÓW I GAZÓW (µg/m³)", subtitle="Czujniki laserowe i stacje referencyjne")
        params = [
            ("PYŁ ZAWIESZONY PM2.5", f"{self.pm25} µg/m³", "Norma: 25 µg/m³ (29%)", (0, 255, 136)),
            ("PYŁ ZAWIESZONY PM10", f"{self.pm10} µg/m³", "Norma: 50 µg/m³ (28%)", (0, 255, 136)),
            ("OZON TROPOSFERYCZNY O3", f"{self.o3} µg/m³", "Norma: 120 µg/m³ (37%)", (0, 200, 255)),
            ("DWUTLENEK AZOTU NO2", f"{self.no2} µg/m³", "Norma: 200 µg/m³ (6%)", (0, 255, 136)),
            ("DWUTLENEK SIARKI SO2", f"{self.so2} µg/m³", "Norma: 125 µg/m³ (2%)", (0, 255, 136)),
        ]
        for i, (title, val, norm, col) in enumerate(params):
            py = 125 + i * 65
            draw.text((460, py), title, fill=(150, 175, 205), font=get_font(13))
            draw.text((460, py + 18), val, fill=col, font=get_font(20, bold=True))
            draw.text((700, py + 20), norm, fill=(130, 150, 180), font=get_font(12))

        # Bottom 24h Trend Chart
        canvas.draw_card(20, 520, 984, 190, title="HISTOGRAM 24-GODZINNY JAKOŚCI POWIETRZA", subtitle="Trend dobowy PM2.5 / PM10")
        bw = 90
        for i, v in enumerate(self.history):
            bx = 60 + i * 102
            bh = int(v * 2.2)
            draw.rectangle([bx, 670 - bh, bx + bw, 670], fill=(0, 200, 140))
            draw.text((bx + 15, 675), f"-{len(self.history)-1-i}h", fill=(120, 140, 170), font=get_font(12))
            draw.text((bx + 18, 645 - bh), str(v), fill=(220, 240, 255), font=get_font(12, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Góra/Dół: Zmień Miasto | [A]: Wymuś Odświeżenie Stacji | [X]: Zmień Jednostki (US/EU)", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
