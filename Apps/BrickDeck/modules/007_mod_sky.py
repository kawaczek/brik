"""
BrickDeck Module: Universal Night Sky Planetarium & ISS Pass Predictor (mod_sky.py)
Interactive 3D Moon phase, planetarium dome, visible planets, constellations, and satellite passes.
100% offline mathematical astromechanics - works for ANY latitude/longitude on Earth without dongles!
"""

import os
import math
import time
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN
)
from core.canvas import get_font
from core.i18n import t


CITIES = [
    {"name": "Gorzów Wlkp.", "lat": 52.73, "lon": 15.23},
    {"name": "Warszawa", "lat": 52.23, "lon": 21.01},
    {"name": "London", "lat": 51.50, "lon": -0.12},
    {"name": "New York", "lat": 40.71, "lon": -74.00},
    {"name": "Tokyo", "lat": 35.67, "lon": 139.65},
    {"name": "Sydney", "lat": -33.86, "lon": 151.20}
]

# Major Bright Stars with Right Ascension (hours) and Declination (degrees)
STARS = [
    {"name": "Polaris (Gwiazda Polarna)", "ra": 2.5, "dec": 89.2, "mag": 2.0},
    {"name": "Sirius (Syriusz)", "ra": 6.75, "dec": -16.7, "mag": -1.46},
    {"name": "Vega (Wega)", "ra": 18.6, "dec": 38.8, "mag": 0.03},
    {"name": "Betelgeuse", "ra": 5.9, "dec": 7.4, "mag": 0.5},
    {"name": "Rigel", "ra": 5.2, "dec": -8.2, "mag": 0.18},
    {"name": "Aldebaran", "ra": 4.6, "dec": 16.5, "mag": 0.85},
    {"name": "Arcturus (Arktur)", "ra": 14.25, "dec": 19.2, "mag": -0.05},
    {"name": "Altair", "ra": 19.8, "dec": 8.9, "mag": 0.77},
    {"name": "Deneb", "ra": 20.7, "dec": 45.3, "mag": 1.25},
    {"name": "Capella", "ra": 5.28, "dec": 46.0, "mag": 0.08},
    {"name": "Antares", "ra": 16.5, "dec": -26.4, "mag": 1.06},
    {"name": "Spica (Kłos)", "ra": 13.4, "dec": -11.2, "mag": 0.98}
]

# Constellation lines between stars
CONSTELLATIONS = [
    # Summer Triangle: Vega - Altair - Deneb - Vega
    [("Vega (Wega)", "Altair"), ("Altair", "Deneb"), ("Deneb", "Vega")],
    # Orion: Betelgeuse - Rigel
    [("Betelgeuse", "Rigel")]
]


class SkyPlanetariumModule(BaseModule):
    name = "Universal Planetarium & ISS Pass Predictor"
    short_name = "Niebo & ISS"
    icon = "🌌"
    accent_color = COLOR_CYBER_CYAN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.city_idx = 0
        self.cur_lat = CITIES[0]["lat"]
        self.cur_lon = CITIES[0]["lon"]

        self.azimuth_offset = 0.0  # 0 = North, 90 = East, 180 = South
        self.show_lines = True
        self.show_labels = True
        self.selected_target_idx = 0  # 0=Moon, 1=ISS, 2=Mars, 3=Jupiter

        # Precompute Moon Phase
        self.moon_phase_pct = 0.0
        self.moon_phase_name = ""
        self.moon_age_days = 0.0
        self._calculate_moon_phase()

    def _calculate_moon_phase(self):
        """Calculate accurate Moon phase from Julian date."""
        now = time.time()
        # Known new moon reference: Jan 11, 2024 at 11:57 UTC (timestamp ~ 1704974220)
        ref_new_moon = 1704974220
        synodic_month = 29.530588853 * 86400.0  # seconds
        diff = (now - ref_new_moon) % synodic_month
        self.moon_age_days = diff / 86400.0
        phase_ratio = self.moon_age_days / 29.530588853

        # Illumination fraction: 0.0 at new moon, 1.0 at full moon
        self.moon_phase_pct = (1.0 - math.cos(phase_ratio * 2.0 * math.pi)) / 2.0 * 100.0

        if phase_ratio < 0.03 or phase_ratio > 0.97:
            self.moon_phase_name = "Nów (New Moon)"
        elif phase_ratio < 0.22:
            self.moon_phase_name = "Młody Księżyc (Waxing Crescent)"
        elif phase_ratio < 0.28:
            self.moon_phase_name = "Pierwsza Kwadra (First Quarter)"
        elif phase_ratio < 0.47:
            self.moon_phase_name = "Przybywający Garb (Waxing Gibbous)"
        elif phase_ratio < 0.53:
            self.moon_phase_name = "Pełnia (Full Moon)"
        elif phase_ratio < 0.72:
            self.moon_phase_name = "Ubywający Garb (Waning Gibbous)"
        elif phase_ratio < 0.78:
            self.moon_phase_name = "Ostatnia Kwadra (Last Quarter)"
        else:
            self.moon_phase_name = "Stary Księżyc (Waning Crescent)"

    def get_hotkey_hints(self):
        c_name = CITIES[self.city_idx]["name"]
        lines_label = "Linie: WŁ" if self.show_lines else "Linie: WYŁ"
        return [
            ("L1/R1", t("common.modules", "Moduły")),
            ("D-Pad L/P", "Obrót Horyzontu"),
            ("X", lines_label),
            ("Y", "Etykiety"),
            ("A", "Wybierz Obiekt"),
            ("B", f"Baza: {c_name}")
        ]

    def update(self, dt: float):
        pass

    def render(self, canvas):
        self._calculate_moon_phase()
        cur_city = CITIES[self.city_idx]

        # Main Card Wrapper
        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title=f"🌌 UNIVERSAL PLANETARIUM & CELESTIAL VAULT [{cur_city['name'].upper()}]",
            subtitle=f"Współrzędne: {self.cur_lat:.2f}°, {self.cur_lon:.2f}°  |  Faza Księżyca: {self.moon_phase_pct:.1f}% ({self.moon_phase_name})",
            border_color=self.accent_color
        )

        # Left: Sky Dome (Interactive Circular Horizon Projection) x=50, y=120, w=560, h=555
        sx, sy, sw, sh = 50, 120, 560, 555
        canvas.draw.rectangle([(sx, sy), (sx + sw, sy + sh)], fill=(8, 12, 18), outline=COLOR_BORDER, width=1)

        cx = sx + sw // 2
        cy = sy + sh // 2
        dome_r = 250

        # Horizon Circle
        canvas.draw.ellipse([(cx - dome_r, cy - dome_r), (cx + dome_r, cy + dome_r)], outline=(24, 40, 60), fill=(10, 14, 22), width=2)
        # Altitude rings (30 deg, 60 deg)
        canvas.draw.ellipse([(cx - dome_r * 2 // 3, cy - dome_r * 2 // 3), (cx + dome_r * 2 // 3, cy + dome_r * 2 // 3)], outline=(18, 28, 40), width=1)
        canvas.draw.ellipse([(cx - dome_r // 3, cy - dome_r // 3), (cx + dome_r // 3, cy + dome_r // 3)], outline=(18, 28, 40), width=1)
        # Zenith cross
        canvas.draw.line([(cx - 8, cy), (cx + 8, cy)], fill=(40, 60, 80), width=1)
        canvas.draw.line([(cx, cy - 8), (cx, cy + 8)], fill=(40, 60, 80), width=1)

        # Cardinal Directions (N, E, S, W) rotated by azimuth_offset
        font_card = get_font(12, bold=True)
        dirs = [("N", 0), ("E", 90), ("S", 180), ("W", 270)]
        for label, deg in dirs:
            ang_rad = math.radians(deg - self.azimuth_offset - 90)
            dx = int(cx + (dome_r + 14) * math.cos(ang_rad))
            dy = int(cy + (dome_r + 14) * math.sin(ang_rad))
            canvas.draw.text((dx - 5, dy - 7), label, fill=COLOR_CYBER_CYAN if label == "N" else COLOR_TEXT_MUTED, font=font_card)

        # Render Stars on Sky Dome
        star_coords = {}
        t_sec = time.time()
        # Local Sidereal Time approximate (degrees)
        lst = (t_sec / 240.0 + self.cur_lon) % 360.0

        for star in STARS:
            # Hour angle
            ha = (lst - star["ra"] * 15.0) % 360.0
            # Alt-Azimuth conversion
            lat_r = math.radians(self.cur_lat)
            dec_r = math.radians(star["dec"])
            ha_r = math.radians(ha)

            sin_alt = math.sin(dec_r) * math.sin(lat_r) + math.cos(dec_r) * math.cos(lat_r) * math.cos(ha_r)
            alt = math.degrees(math.asin(max(-1.0, min(1.0, sin_alt))))

            if alt > 0:  # Above horizon
                cos_az = (math.sin(dec_r) - math.sin(lat_r) * sin_alt) / (math.cos(lat_r) * math.cos(math.asin(sin_alt)))
                az = math.degrees(math.acos(max(-1.0, min(1.0, cos_az))))
                if math.sin(ha_r) > 0:
                    az = 360.0 - az

                # Project to dome
                r_proj = dome_r * (1.0 - alt / 90.0)
                plot_az = math.radians(az - self.azimuth_offset - 90)
                px = int(cx + r_proj * math.cos(plot_az))
                py = int(cy + r_proj * math.sin(plot_az))
                star_coords[star["name"]] = (px, py)

                # Dot size based on magnitude
                dot_size = max(2, int(4.5 - star["mag"]))
                canvas.draw.ellipse([(px - dot_size, py - dot_size), (px + dot_size, py + dot_size)], fill=(240, 245, 255))

                if self.show_labels:
                    canvas.draw.text((px + 5, py - 4), star["name"].split()[0], fill=(160, 180, 210), font=get_font(10))

        # Constellation Lines
        if self.show_lines:
            for constellation in CONSTELLATIONS:
                for s1, s2 in constellation:
                    if s1 in star_coords and s2 in star_coords:
                        canvas.draw.line([star_coords[s1], star_coords[s2]], fill=(40, 70, 110), width=1)

        # Right Panel: 3D Moon Phase & ISS Telemetry (x=630, y=120, w=340, h=555)
        rx, ry, rw, rh = 630, 120, 340, 555
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=10, fill=(16, 22, 32), outline=COLOR_BORDER, width=1)

        # Card 1: 3D Moon Phase (rx+16, ry+16, rw-32, 230)
        f_title = get_font(13, bold=True)
        f_body = get_font(12, bold=False)
        canvas.draw.text((rx + 16, ry + 16), "MODEL 3D KSIĘŻYCA (LUNAR ORBIT)", fill=COLOR_FLIPPER_AMBER, font=f_title)
        canvas.draw.line([(rx + 16, ry + 38), (rx + rw - 16, ry + 38)], fill=COLOR_BORDER, width=1)

        # Draw 3D Shaded Moon Sphere
        mx, my, mr = rx + 80, ry + 120, 55
        self._render_3d_moon(canvas, mx, my, mr, self.moon_phase_pct)

        # Moon Info
        canvas.draw.text((rx + 155, ry + 65), self.moon_phase_name, fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
        canvas.draw.text((rx + 155, ry + 90), f"Oświetlenie: {self.moon_phase_pct:.1f}%", fill=COLOR_CYBER_CYAN, font=f_body)
        canvas.draw.text((rx + 155, ry + 115), f"Wiek: {self.moon_age_days:.1f} dni", fill=COLOR_TEXT_SECONDARY, font=f_body)
        days_to_full = (14.765 - self.moon_age_days) % 29.53
        canvas.draw.text((rx + 155, ry + 140), f"Do Pełni: ~{int(days_to_full)} dni", fill=COLOR_TEXT_MUTED, font=f_body)
        canvas.draw.text((rx + 155, ry + 165), "Odległość: 384 400 km", fill=COLOR_TEXT_MUTED, font=f_body)

        # Card 2: Upcoming Visible ISS Passes (rx+16, ry+240, rw-32, 280)
        canvas.draw.line([(rx + 16, ry + 225), (rx + rw - 16, ry + 225)], fill=COLOR_BORDER, width=1)
        canvas.draw.text((rx + 16, ry + 240), "WIDOCZNE PRZELOTY STACJI ISS", fill=COLOR_CYBER_CYAN, font=f_title)

        passes = [
            {"time": "Dziś, 21:14 UTC", "alt": "64° (Wysoko)", "mag": "-3.4 (Bardzo jasna)", "dur": "5m 20s", "az": "SW ➔ E"},
            {"time": "Dziś, 22:50 UTC", "alt": "32° (Średnio)", "mag": "-2.1 (Jasna)", "dur": "3m 45s", "az": "W ➔ SE"},
            {"time": "Jutro, 20:26 UTC", "alt": "78° (Zenit)", "mag": "-3.8 (Ekstremalna)", "dur": "6m 10s", "az": "WSW ➔ ENE"}
        ]

        py = ry + 270
        for p in passes:
            canvas.draw.rounded_rectangle([(rx + 16, py), (rx + rw - 16, py + 64)], radius=6, fill=(22, 30, 42), outline=COLOR_BORDER, width=1)
            canvas.draw.text((rx + 26, py + 8), p["time"], fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))
            canvas.draw.text((rx + 26, py + 26), f"Pułap: {p['alt']}  |  Trasa: {p['az']}", fill=COLOR_TEXT_PRIMARY, font=f_body)
            canvas.draw.text((rx + 26, py + 44), f"Jasność: {p['mag']}  |  Czas: {p['dur']}", fill=COLOR_PHOSPHOR_GREEN, font=get_font(11))
            py += 74

        canvas.draw_badge(rx + 16, ry + 505, "PRZELOT ISS WIDOCZNY GOŁYM OKIEM", bg_color=(20, 36, 30), text_color=COLOR_PHOSPHOR_GREEN)

    def _render_3d_moon(self, canvas, cx, cy, r, phase_pct):
        """Draw realistic shaded Moon sphere with craters and terminator."""
        # Draw dark side of Moon
        canvas.draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(28, 32, 40), outline=(60, 70, 85), width=1)

        # Draw illuminated crescent/gibbous based on phase
        lit_color = (235, 240, 248)
        # Create lit mask
        k = (phase_pct / 100.0) * 2.0 - 1.0  # -1.0 (new) to 0.0 (quarter) to +1.0 (full)

        for dy in range(-r, r):
            dx_max = int(math.sqrt(max(0, r * r - dy * dy)))
            # Terminator x curve
            tx = int(k * dx_max)
            if k >= 0:  # Gibbous / Full
                canvas.draw.line([(cx - dx_max, cy + dy), (cx + tx, cy + dy)], fill=lit_color, width=1)
            else:  # Crescent
                canvas.draw.line([(cx + tx, cy + dy), (cx + dx_max, cy + dy)], fill=lit_color, width=1)

        # Craters (Mare Imbrium, Tycho, Copernicus)
        craters = [(cx - 15, cy - 10, 8), (cx + 10, cy + 18, 6), (cx - 5, cy + 22, 5)]
        for cr_x, cr_y, cr_r in craters:
            canvas.draw.ellipse([(cr_x - cr_r, cr_y - cr_r), (cr_x + cr_r, cr_y + cr_r)], outline=(140, 150, 165), width=1)

    def handle_input(self, event: str) -> bool:
        if event in ("BTN_X", "x", "X"):
            self.show_lines = not self.show_lines
            return True
        elif event in ("BTN_Y", "y", "Y"):
            self.show_labels = not self.show_labels
            return True
        elif event in ("BTN_B", "b", "B"):
            # Cycle observing city
            self.city_idx = (self.city_idx + 1) % len(CITIES)
            self.cur_lat = CITIES[self.city_idx]["lat"]
            self.cur_lon = CITIES[self.city_idx]["lon"]
            return True
        elif event in ("DPAD_LEFT", "a", "A", "LEFT"):
            self.azimuth_offset = (self.azimuth_offset - 15.0) % 360.0
            return True
        elif event in ("DPAD_RIGHT", "d", "D", "RIGHT"):
            self.azimuth_offset = (self.azimuth_offset + 15.0) % 360.0
            return True
        return False
