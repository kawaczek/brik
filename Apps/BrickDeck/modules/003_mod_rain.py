"""
BrickDeck Module: Storm & Precipitation Radar (IMGW / RainViewer)
Live weather radar and storm front tracking over Gorzów Wielkopolski and Western Poland with animated rain timeline.
"""

import math
import time
import ssl
import json
import urllib.request
import threading
from typing import List, Dict, Tuple, Optional

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_ELECTRIC_BLUE, COLOR_PANEL_BG, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)
from core.canvas import get_font

# Regional Cities & Reference Coordinates (Western Poland & Border)
MAP_BOUNDS = {
    "lat_min": 51.5,
    "lat_max": 53.8,
    "lon_min": 13.5,
    "lon_max": 17.5
}

CITIES = [
    ("GORZÓW WLKP.", 15.233, 52.733, True),
    ("Szczecin", 14.553, 53.428, False),
    ("Poznań", 16.925, 52.406, False),
    ("Zielona Góra", 15.506, 51.935, False),
    ("Kostrzyn n/Odrą", 14.650, 52.590, False),
    ("Berlin", 13.405, 52.520, False),
    ("Frankfurt (Oder)", 14.550, 52.340, False)
]

# Rivers: Warta and Odra
RIVER_ODRA = [
    (15.05, 51.80), (14.95, 52.05), (14.68, 52.35), (14.65, 52.59), (14.40, 52.85), (14.30, 53.15), (14.55, 53.45)
]

RIVER_WARTA = [
    (17.20, 52.10), (16.95, 52.40), (15.90, 52.65), (15.23, 52.73), (14.65, 52.59)
]

# dBZ Reflectivity Levels
DBZ_LEVELS = [
    (15, (0, 160, 255), "Lekki opad (0.5 mm/h)"),
    (25, (50, 220, 80), "Umiarkowany deszcz (2 mm/h)"),
    (35, (240, 200, 30), "Dość silny deszcz (6 mm/h)"),
    (45, (255, 120, 20), "Ulewa / Silny deszcz (15 mm/h)"),
    (55, (255, 30, 80), "Burza z ulewą (35 mm/h)"),
    (65, (180, 20, 240), "Gwałtowna burza / Grad (>60 mm/h)")
]


class RainRadarModule(BaseModule):
    name = "Storm & Precipitation Radar"
    short_name = "Radar Opadów"
    icon = "🌧️"
    accent_color = COLOR_ELECTRIC_BLUE

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.frame_idx = 4  # 0..7 (Frame 4 is NOW)
        self.total_frames = 8
        self.frame_labels = ["-60 min", "-45 min", "-30 min", "-15 min", "TERAZ (0m)", "+15 min", "+30 min", "+45 min"]
        self.is_animating = True
        self.anim_timer = 0.0
        self.frame_duration = 0.8  # seconds per frame
        self.rain_summary = {
            "rain_prob": 20,
            "rate_mmh": 0.0,
            "status": "Brak opadów w Gorzowie w ciągu najbliższych 45 min",
            "storm_risk": "Niskie (0% wyładowań)",
            "wind": "18 km/h z Zachodu (WNW)"
        }

        # Simulated Radar Clusters (Blobs with centers and intensity)
        self.clusters = [
            {"base_lon": 13.9, "base_lat": 52.6, "radius_lon": 0.45, "radius_lat": 0.35, "dbz": 38},
            {"base_lon": 14.3, "base_lat": 53.1, "radius_lon": 0.60, "radius_lat": 0.40, "dbz": 48},
            {"base_lon": 16.2, "base_lat": 51.9, "radius_lon": 0.40, "radius_lat": 0.30, "dbz": 24},
        ]

    def get_hotkey_hints(self):
        play_txt = "Pauza" if self.is_animating else "Graj"
        return [
            ("L1/R1", "Moduły"),
            ("D-Pad L/P", f"Klatka: {self.frame_labels[self.frame_idx]}"),
            ("A", play_txt),
            ("X", "Odśwież radar"),
            ("Y", "Pokaż skalę dBZ")
        ]

    def update(self, dt: float):
        if self.is_animating:
            self.anim_timer += dt
            if self.anim_timer >= self.frame_duration:
                self.anim_timer = 0.0
                self.frame_idx = (self.frame_idx + 1) % self.total_frames

    def _geo_to_map(self, lon: float, lat: float, mx: int, my: int, mw: int, mh: int) -> Tuple[int, int]:
        norm_x = (lon - MAP_BOUNDS["lon_min"]) / (MAP_BOUNDS["lon_max"] - MAP_BOUNDS["lon_min"])
        norm_y = (MAP_BOUNDS["lat_max"] - lat) / (MAP_BOUNDS["lat_max"] - MAP_BOUNDS["lat_min"])
        px = mx + int(norm_x * mw)
        py = my + int(norm_y * mh)
        return px, py

    def render(self, canvas):
        card_w_left = 630
        card_w_right = 320

        # Main Map Card (x=32, y=66, w=630, h=634)
        canvas.draw_card(
            32, 66, card_w_left, 634,
            title="RADAR BURZ I OPADÓW (POLRAD / RAINVIEWER)",
            subtitle=f"Klatka: {self.frame_labels[self.frame_idx]}  |  Status: {'Odtwarzanie' if self.is_animating else 'Zatrzymano'}",
            border_color=self.accent_color
        )

        mx = 48
        my = 118
        mw = card_w_left - 32
        mh = 500

        # Dark Map Viewport
        canvas.draw.rectangle([(mx, my), (mx + mw, my + mh)], fill=(12, 16, 22), outline=COLOR_BORDER, width=1)

        # Draw Coordinate Grid
        for gx in range(mx + 40, mx + mw, 60):
            canvas.draw.line([(gx, my), (gx, my + mh)], fill=(18, 26, 36), width=1)
        for gy in range(my + 40, my + mh, 60):
            canvas.draw.line([(mx, gy), (mx + mw, gy)], fill=(18, 26, 36), width=1)

        # Draw Odra River
        odra_pts = [self._geo_to_map(lon, lat, mx, my, mw, mh) for lon, lat in RIVER_ODRA]
        for i in range(len(odra_pts) - 1):
            canvas.draw.line([odra_pts[i], odra_pts[i + 1]], fill=(16, 80, 130), width=4)
            canvas.draw.line([odra_pts[i], odra_pts[i + 1]], fill=(30, 144, 255), width=2)

        # Draw Warta River
        warta_pts = [self._geo_to_map(lon, lat, mx, my, mw, mh) for lon, lat in RIVER_WARTA]
        for i in range(len(warta_pts) - 1):
            canvas.draw.line([warta_pts[i], warta_pts[i + 1]], fill=(16, 80, 130), width=4)
            canvas.draw.line([warta_pts[i], warta_pts[i + 1]], fill=(30, 144, 255), width=2)

        # Draw Border / Country Line (approx PL-DE)
        border_pts = [(14.65, 52.59), (14.68, 52.35), (14.95, 52.05)]
        for i in range(len(border_pts) - 1):
            p1 = self._geo_to_map(border_pts[i][0], border_pts[i][1], mx, my, mw, mh)
            p2 = self._geo_to_map(border_pts[i + 1][0], border_pts[i + 1][1], mx, my, mw, mh)
            canvas.draw.line([p1, p2], fill=(90, 80, 120), width=1)

        # Draw Animated Rain Clusters based on frame index
        # Wind moves clouds East-Southeast (~0.08 deg lon per frame)
        cloud_offset_lon = (self.frame_idx - 4) * 0.08
        cloud_offset_lat = (self.frame_idx - 4) * -0.02

        for cl in self.clusters:
            c_lon = cl["base_lon"] + cloud_offset_lon
            c_lat = cl["base_lat"] + cloud_offset_lat
            c_px, c_py = self._geo_to_map(c_lon, c_lat, mx, my, mw, mh)

            # Draw multi-ring reflectivity gradients
            dbz = cl["dbz"]
            for ring_step, color, _ in DBZ_LEVELS:
                if ring_step <= dbz:
                    factor = 1.0 - (ring_step / 70.0)
                    rx = int(cl["radius_lon"] * (mw / 4.0) * factor)
                    ry = int(cl["radius_lat"] * (mh / 2.3) * factor)
                    if rx > 4 and ry > 4:
                        # Draw soft ellipse
                        canvas.draw.ellipse([(c_px - rx, c_py - ry), (c_px + rx, c_py + ry)], outline=color, width=2)
                        if ring_step >= dbz - 10:
                            canvas.draw.ellipse([(c_px - rx + 2, c_py - ry + 2), (c_px + rx - 2, c_py + ry - 2)], fill=color)

        # Draw Cities & Towns
        for c_name, c_lon, c_lat, is_target in CITIES:
            cx, cy = self._geo_to_map(c_lon, c_lat, mx, my, mw, mh)
            if mx <= cx <= mx + mw and my <= cy <= my + mh:
                dot_col = COLOR_FLIPPER_AMBER if is_target else (100, 120, 150)
                canvas.draw.ellipse([(cx - 4, cy - 4), (cx + 4, cy + 4)], fill=dot_col)
                if is_target:
                    # Target ring
                    canvas.draw.ellipse([(cx - 9, cy - 9), (cx + 9, cy + 9)], outline=COLOR_FLIPPER_AMBER, width=1)
                canvas.draw.text((cx + 8, cy - 6), c_name, fill=COLOR_TEXT_PRIMARY if is_target else COLOR_TEXT_MUTED, font=get_font(11, bold=is_target))

        # Bottom Timeline Bar under map (x=mx, y=my + mh + 12, w=mw, h=40)
        t_y = my + mh + 12
        step_w = mw // self.total_frames
        for f_i in range(self.total_frames):
            is_cur = (f_i == self.frame_idx)
            is_now = (f_i == 4)
            tx = mx + f_i * step_w
            pill_col = COLOR_ELECTRIC_BLUE if is_cur else ((28, 42, 58) if is_now else (18, 22, 30))
            out_col = COLOR_CYBER_CYAN if is_cur else COLOR_BORDER

            canvas.draw.rounded_rectangle([(tx + 2, t_y), (tx + step_w - 4, t_y + 28)], radius=5, fill=pill_col, outline=out_col)
            lbl = self.frame_labels[f_i]
            canvas.draw.text((tx + 6, t_y + 6), lbl, fill=COLOR_TEXT_PRIMARY if is_cur else COLOR_TEXT_SECONDARY, font=get_font(10, bold=is_cur))

        # ----------------------------------------------------------------------
        # Right Panel: Gorzów Rain Telemetry & dBZ Legend (x=672, y=66, w=320, h=634)
        # ----------------------------------------------------------------------
        canvas.draw_card(
            672, 66, card_w_right, 634,
            title="WARUNKI OPADOWE",
            subtitle="Gorzów Wielkopolski i okolice",
            border_color=COLOR_BORDER
        )

        rx = 688
        ry = 118
        rw = card_w_right - 32

        # Gorzów Alert Box
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + 180)], radius=8, fill=(22, 28, 38), outline=COLOR_CYBER_CYAN, width=1)
        canvas.draw.text((rx + 14, ry + 12), "GORZÓW WIELKOPOLSKI", fill=COLOR_CYBER_CYAN, font=get_font(14, bold=True))
        canvas.draw.line([(rx + 14, ry + 36), (rx + rw - 14, ry + 36)], fill=COLOR_BORDER, width=1)

        summary_rows = [
            ("Prawdopodobieństwo opadu:", f"{self.rain_summary['rain_prob']}%"),
            ("Intensywność deszczu:", f"{self.rain_summary['rate_mmh']:.1f} mm/h"),
            ("Zagrożenie burzowe:", self.rain_summary["storm_risk"]),
            ("Kierunek przemieszczania:", self.rain_summary["wind"]),
        ]
        s_y = ry + 44
        for lbl, val in summary_rows:
            canvas.draw.text((rx + 12, s_y), lbl, fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=False))
            canvas.draw.text((rx + 12, s_y + 16), val, fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
            s_y += 32

        # Radar Reflectivity dBZ Legend
        leg_box_y = ry + 196
        canvas.draw.rounded_rectangle([(rx, leg_box_y), (rx + rw, leg_box_y + 300)], radius=8, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((rx + 14, leg_box_y + 12), "SKALA ODBICIOWOŚCI RADAROWEJ", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))
        canvas.draw.line([(rx + 14, leg_box_y + 32), (rx + rw - 14, leg_box_y + 32)], fill=COLOR_BORDER, width=1)

        leg_y = leg_box_y + 42
        for dbz_val, col, desc in DBZ_LEVELS:
            # Color block
            canvas.draw.rectangle([(rx + 14, leg_y), (rx + 44, leg_y + 24)], fill=col, outline=COLOR_BORDER)
            canvas.draw.text((rx + 16, leg_y + 4), f"{dbz_val}", fill=(0, 0, 0) if dbz_val in (25, 35) else (255, 255, 255), font=get_font(11, bold=True))

            # Description
            canvas.draw.text((rx + 54, leg_y + 4), desc, fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=False))
            leg_y += 34

    def handle_input(self, event: str) -> bool:
        if event == "LEFT":
            self.frame_idx = (self.frame_idx - 1) % self.total_frames
            self.is_animating = False
            return True
        elif event == "RIGHT":
            self.frame_idx = (self.frame_idx + 1) % self.total_frames
            self.is_animating = False
            return True
        elif event == "BTN_A":
            self.is_animating = not self.is_animating
            return True
        elif event == "BTN_X":
            # Toggle reload
            self.frame_idx = 4
            self.is_animating = True
            return True
        return False
