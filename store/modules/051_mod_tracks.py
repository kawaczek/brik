#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TracksModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.track_name = "Trasa_Warta_Gorzow_Santok.gpx"
        self.distance_km = 16.4
        self.elevation_gain = 245
        self.duration = "01:42:15"
        self.avg_speed = "9.6 km/h"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 15, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), f"🗺️ 051 // GPX TRACK INSPECTOR // {self.track_name}", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 180, 12, "KARTA SD // GPX", bg_color=(20, 50, 40))

        # Vector Map Area
        canvas.draw_card(20, 65, 640, 440, title="WEKTOROWA TRASA GPS (ŚCIEŻKA)", subtitle="Współrzędne WGS84 z pliku GPX")
        draw.rectangle([40, 120, 640, 480], fill=(14, 22, 32), outline=(0, 180, 200))
        # Draw mock GPS track
        points = [(60, 400), (140, 370), (220, 310), (320, 260), (410, 240), (490, 200), (580, 160)]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=(0, 255, 180), width=4)
        draw.ellipse([(points[0][0]-6, points[0][1]-6), (points[0][0]+6, points[0][1]+6)], fill=(0, 255, 0))
        draw.text((points[0][0]+12, points[0][1]-10), "START", fill=(0, 255, 0), font=get_font(12, bold=True))
        draw.ellipse([(points[-1][0]-6, points[-1][1]-6), (points[-1][0]+6, points[-1][1]+6)], fill=(255, 0, 80))
        draw.text((points[-1][0]+12, points[-1][1]-10), "META", fill=(255, 80, 80), font=get_font(12, bold=True))

        # Stats Card
        canvas.draw_card(680, 65, 324, 440, title="STATYSTYKI TRENINGU", subtitle="Telemetria z czujników GPS")
        stats = [
            ("DYSTANS:", f"{self.distance_km} km"),
            ("PRZEWYŻSZENIE:", f"+{self.elevation_gain} m"),
            ("CZAS SESJI:", self.duration),
            ("ŚREDNIA PRĘDKOŚĆ:", self.avg_speed),
            ("SPALONE KALORIE:", "680 kcal"),
        ]
        for i, (label, val) in enumerate(stats):
            draw.text((700, 130 + i * 65), label, fill=(140, 170, 200), font=get_font(13))
            draw.text((700, 150 + i * 65), val, fill=(0, 255, 180), font=get_font(24, bold=True))

        # Bottom Elevation Profile
        canvas.draw_card(20, 520, 984, 190, title="PROFIL WYSOKOŚCIOWY TERENU (ELEVATION PROFILE)", subtitle="Wysokość n.p.m. w funkcji dystansu")
        draw.rectangle([40, 570, 984, 680], fill=(14, 20, 30))
        alt_points = [20, 25, 45, 60, 85, 110, 95, 130, 145, 120, 90, 75, 40]
        for i in range(len(alt_points) - 1):
            x1 = 50 + i * 75
            x2 = 50 + (i + 1) * 75
            y1 = 670 - alt_points[i]
            y2 = 670 - alt_points[i + 1]
            draw.line([(x1, y1), (x2, y2)], fill=(255, 200, 0), width=3)
        draw.text((50, 580), "Max: 145 m n.p.m. | Min: 18 m n.p.m.", fill=(255, 200, 0), font=get_font(13, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Trasę | [A]: Otwórz Inny Plik GPX | [Y]: Zoom Mapy", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
