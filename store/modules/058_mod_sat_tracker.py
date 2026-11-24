#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class SatTrackerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.satellite = "HOTBIRD 13G (13.0°E)"
        self.azimuth = 184.2
        self.elevation = 31.8
        self.skew = -2.1
        self.qth = "Gorzów Wlkp. (52.73°N, 15.24°E)"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"📡 058 // SATTRACK 3D // NAMIAR ANTENY // {self.satellite}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 240, 12, "ORBITA GEO 35786 KM", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 80, 12, "KU-BAND", bg_color=(40, 30, 60), text_color=(0, 240, 255))

        # Main Angles Card
        canvas.draw_card(20, 65, 540, 440, title="KĄTY NASTAWIENIA CZASZY ANTENOWEJ", subtitle=f"Pozycja odbiorcy: {self.qth}")
        draw.text((50, 140), f"AZYMUT (POZIOM):  {self.azimuth:.1f}°", fill=(0, 255, 180), font=get_font(26, bold=True))
        draw.text((50, 210), f"ELEWACJA (PION):  {self.elevation:.1f}°", fill=(0, 240, 255), font=get_font(26, bold=True))
        draw.text((50, 280), f"SKRĘCENIE LNB (SKEW):  {self.skew:.1f}°", fill=(255, 200, 0), font=get_font(26, bold=True))
        draw.text((50, 360), "Kompas magnetyczny: Skieruj antenę niemal dokładnie na południe.", fill=(160, 185, 215), font=get_font(14))
        draw.text((50, 390), "Brak przeszkód terenowych powyżej kąta 32° nad horyzontem.", fill=(0, 255, 136), font=get_font(14, bold=True))

        # Visual Dish & Skew Diagram
        canvas.draw_card(580, 65, 424, 440, title="WIZUALIZACJA NACHYLENIA CZASZY", subtitle="Kątomierz z czujnika pochylenia")
        cx, cy = 790, 260
        draw.ellipse([(cx - 110, cy - 110), (cx + 110, cy + 110)], outline=(0, 200, 255), width=2)
        draw.line([(cx - 120, cy), (cx + 120, cy)], fill=(40, 60, 85))
        draw.line([(cx, cy - 120), (cx, cy + 120)], fill=(40, 60, 85))
        draw.line([(cx - 70, cy + 50), (cx + 70, cy - 50)], fill=(0, 255, 180), width=4)
        draw.text((cx - 50, cy + 130), "CZASZA 80 CM // OFFSET", fill=(150, 180, 210), font=get_font(13))

        # Bottom List of Satellites
        canvas.draw_card(20, 520, 984, 190, title="POZYCJE SATELITARNE W ZASIĘGU", subtitle="Wybierz satelitę do ustawienia namiaru")
        sats = ["HotBird 13°E", "Astra 19.2°E", "Eutelsat 16°E", "Astra 28.2°E", "Thor 0.8°W", "Hispasat 30°W"]
        for i, s in enumerate(sats):
            sx = 40 + i * 158
            draw.rectangle([sx, 580, sx + 145, 660], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((sx + 10, 610), s, fill=(240, 245, 255), font=get_font(13, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Satelitę | [A]: Kalibruj Kompas Konsoli | [X]: Zmień Współrzędne GPS", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
