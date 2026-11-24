"""
BrickDeck Module: Storm & Precipitation Radar (IMGW / RainViewer / Open-Meteo)
Live weather radar and storm front tracking over Gorzów Wielkopolski and Western Poland.
Supports real-time online data fetching (live Gorzów weather station & POLRAD/RainViewer timeline)
with automatic fallback to deterministic offline regional simulation for TrimUI Brick and WASM.
Includes multi-level map zoom (1.0x-4.0x), map panning, font scaling (12pt-22pt), and fullscreen radar mode.
"""

import math
import time
import json
import datetime
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_ELECTRIC_BLUE, COLOR_PANEL_BG, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)
from core.canvas import get_font

# Regional Coordinates Bounds (Western Poland & Border)
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
    ("Kostrzyn n/O.", 14.650, 52.590, False),
    ("Berlin", 13.405, 52.520, False),
    ("Frankfurt (O)", 14.550, 52.340, False)
]

RIVER_ODRA = [
    (15.05, 51.80), (14.95, 52.05), (14.68, 52.35), (14.65, 52.59),
    (14.40, 52.85), (14.30, 53.15), (14.55, 53.45)
]

RIVER_WARTA = [
    (17.20, 52.10), (16.95, 52.40), (15.90, 52.65), (15.23, 52.73), (14.65, 52.59)
]

BORDER_PL_DE = [
    (14.65, 52.59), (14.68, 52.35), (14.95, 52.05)
]

DBZ_LEVELS = [
    (15, (0, 160, 255), "Lekki opad (0.5 mm/h)"),
    (25, (50, 220, 80), "Umiarkowany deszcz (2 mm/h)"),
    (35, (240, 200, 30), "Dość silny deszcz (6 mm/h)"),
    (45, (255, 120, 20), "Ulewa / Silny deszcz (15 mm/h)"),
    (55, (255, 30, 80), "Burza z ulewą (35 mm/h)"),
    (65, (180, 20, 240), "Gwałtowna burza / Grad (>60 mm/h)")
]

WMO_WEATHER_CODES = {
    0: "Bezchmurnie (Czyste niebo)",
    1: "Prawie bezchmurnie",
    2: "Częściowe zachmurzenie",
    3: "Pochmurno",
    45: "Mgła",
    48: "Osadzająca się szadź",
    51: "Lekka mżawka",
    53: "Umiarkowana mżawka",
    55: "Gęsta mżawka",
    56: "Marznąca mżawka",
    57: "Gęsta marznąca mżawka",
    61: "Lekki deszcz",
    63: "Umiarkowany deszcz",
    65: "Silny deszcz / Ulewa",
    66: "Lekki marznący deszcz",
    67: "Silny marznący deszcz",
    71: "Niewielkie opady śniegu",
    73: "Umiarkowane opady śniegu",
    75: "Intensywne opady śniegu",
    77: "Ziarna śniegu",
    80: "Przelotny lekki deszcz",
    81: "Przelotny deszcz",
    82: "Gwałtowna ulewa",
    85: "Przelotne opady śniegu",
    86: "Intensywne opady śniegu",
    95: "Burza z piorunami",
    96: "Burza z drobnym gradem",
    99: "Gwałtowna burza z gradem"
}


def _deg_to_cardinal(deg: float) -> str:
    dirs = ["N (Północ)", "NNE", "NE", "ENE", "E (Wschód)", "ESE", "SE", "SSE",
            "S (Południe)", "SSW", "SW", "WSW", "W (Zachód)", "WNW", "NW", "NNW"]
    ix = int((deg + 11.25) / 22.5) % 16
    return dirs[ix]


def _fetch_url_json(url: str, timeout: int = 5) -> Optional[dict]:
    # 1. Try Browser JS Bridge (WASM mode)
    try:
        import js
        if hasattr(js, "brickFetchSync"):
            raw = js.brickFetchSync(url)
            if raw:
                return json.loads(str(raw))
    except Exception:
        pass

    # 2. Try Pyodide open_url
    try:
        from pyodide.http import open_url
        content = open_url(url).read()
        if content:
            return json.loads(content)
    except Exception:
        pass

    # 3. Standard CPython (TrimUI Brick Linux)
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "BrickDeck/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        pass

    return None


class RainRadarModule(BaseModule):
    name = "Storm & Precipitation Radar"
    short_name = "Radar Opadów"
    icon = "🌧️"
    accent_color = COLOR_ELECTRIC_BLUE

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.total_frames = 8
        self.frame_idx = 7  # 0..7 (Last frame is NOW)
        self.frame_labels = ["-70m", "-60m", "-50m", "-40m", "-30m", "-20m", "-10m", "TERAZ"]
        self.is_animating = True
        self.anim_timer = 0.0
        self.frame_duration = 0.9

        # Zoom & Pan State
        self.zoom_level = 1.0  # 1.0x to 4.0x
        self.pan_x = 0
        self.pan_y = 0

        # Font scale: 0 = Standard (12pt), 1 = Powiększona (16pt), 2 = Duża (20pt)
        self.font_scale_idx = 1
        self.font_scale_labels = ["Standard (12pt)", "Powiększona (16pt)", "Maksymalna (20pt)"]

        # View mode: False = Split panel, True = Fullscreen Radar
        self.fullscreen_radar = False

        # Live telemetry status
        self.is_live = False
        self.live_status_msg = "Ładowanie danych stacji..."
        self.last_update_time_str = "--:--"
        self.temp_str = "1.2 °C"
        self.apparent_temp_str = "-1.9 °C"
        self.humidity_str = "85%"
        self.weather_condition_str = "Pochmurno"
        self.precipitation_str = "0.0 mm/h"
        self.wind_str = "6 km/h z W (Zachód)"
        self.storm_risk_str = "Niskie (0% wyładowań)"
        self.auto_refresh_timer = 0.0

        # Radar Clusters (Simulated or adjusted from real rain rate)
        self.clusters = [
            {"base_lon": 13.9, "base_lat": 52.6, "radius_lon": 0.45, "radius_lat": 0.35, "dbz": 38},
            {"base_lon": 14.3, "base_lat": 53.1, "radius_lon": 0.60, "radius_lat": 0.40, "dbz": 48},
            {"base_lon": 16.2, "base_lat": 51.9, "radius_lon": 0.40, "radius_lat": 0.30, "dbz": 24},
        ]

        # Initial live data fetch
        self._refresh_live_data()

    def _refresh_live_data(self):
        """Fetch live Gorzów weather and RainViewer POLRAD radar frame timeline."""
        # 1. Open-Meteo Gorzów Live Weather Station
        url_om = (
            "https://api.open-meteo.com/v1/forecast?"
            "latitude=52.73&longitude=15.23&"
            "current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m&"
            "timezone=Europe%2FWarsaw"
        )
        data_om = _fetch_url_json(url_om, timeout=4)
        if data_om and "current" in data_om:
            cur = data_om["current"]
            self.temp_str = f"{cur.get('temperature_2m', 0.0):.1f} °C"
            self.apparent_temp_str = f"{cur.get('apparent_temperature', 0.0):.1f} °C"
            self.humidity_str = f"{cur.get('relative_humidity_2m', 0)}%"
            precip = cur.get("precipitation", 0.0)
            self.precipitation_str = f"{precip:.1f} mm/h"

            w_code = cur.get("weather_code", 0)
            self.weather_condition_str = WMO_WEATHER_CODES.get(w_code, "Zmienne")

            w_spd = cur.get("wind_speed_10m", 0.0)
            w_dir = cur.get("wind_direction_10m", 270.0)
            self.wind_str = f"{w_spd:.1f} km/h z {_deg_to_cardinal(w_dir)}"

            if w_code in (95, 96, 99):
                self.storm_risk_str = "WYSOKIE (Burza z wyładowaniami!)"
            elif precip > 2.0:
                self.storm_risk_str = "Średnie (Opad umiarkowany)"
            else:
                self.storm_risk_str = "Niskie (Brak aktywnych burz)"

            raw_time = cur.get("time", "")
            if "T" in raw_time:
                self.last_update_time_str = raw_time.split("T")[1]
            else:
                self.last_update_time_str = time.strftime("%H:%M")

            self.is_live = True
            self.live_status_msg = f"LIVE: Stacja Gorzów ({self.last_update_time_str})"

            # If real precipitation is falling, amplify radar cloud over the area
            if precip > 0.0:
                calc_dbz = min(60, int(20 + precip * 8))
                self.clusters[0]["base_lon"] = 15.2
                self.clusters[0]["base_lat"] = 52.7
                self.clusters[0]["dbz"] = calc_dbz

        # 2. RainViewer / POLRAD Live Timestamps
        url_rv = "https://api.rainviewer.com/public/weather-maps.json"
        data_rv = _fetch_url_json(url_rv, timeout=4)
        if data_rv and "radar" in data_rv and "past" in data_rv["radar"]:
            past = data_rv["radar"]["past"]
            if len(past) >= 8:
                new_labels = []
                for p in past[-8:]:
                    ts = p.get("time", 0)
                    try:
                        # Convert UTC to Warsaw (+1h or +2h)
                        dt = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=1)))
                        new_labels.append(dt.strftime("%H:%M"))
                    except Exception:
                        pass
                if len(new_labels) == 8:
                    new_labels[-1] += " (TERAZ)"
                    self.frame_labels = new_labels

    def _f(self, base_size: int, bold: bool = False):
        multipliers = [1.0, 1.35, 1.7]
        m = multipliers[self.font_scale_idx]
        return get_font(max(10, int(base_size * m)), bold=bold)

    def get_hotkey_hints(self):
        play_txt = "Pauza" if self.is_animating else "Graj"
        mode_txt = "Podział" if self.fullscreen_radar else "Pełny Radar"
        font_txt = ["12pt", "16pt", "20pt"][self.font_scale_idx]
        return [
            ("L1/R1", f"Zoom {self.zoom_level:.1f}x"),
            ("D-Pad", "Przesuń" if self.zoom_level > 1.0 else f"Klatka: {self.frame_labels[self.frame_idx]}"),
            ("A", play_txt),
            ("B", "Reset Zoom"),
            ("X", f"Ekran: {mode_txt}"),
            ("Y", f"Czcionka: {font_txt}")
        ]

    def update(self, dt: float):
        # Frame animation
        if self.is_animating:
            self.anim_timer += dt
            if self.anim_timer >= self.frame_duration:
                self.anim_timer = 0.0
                self.frame_idx = (self.frame_idx + 1) % self.total_frames

        # Auto-refresh live weather data every 5 minutes (300 sec)
        self.auto_refresh_timer += dt
        if self.auto_refresh_timer >= 300.0:
            self.auto_refresh_timer = 0.0
            self._refresh_live_data()

    def _geo_to_map(self, lon: float, lat: float, mw: int, mh: int) -> Tuple[int, int]:
        center_lon = 15.5
        center_lat = 52.65
        lon_span = MAP_BOUNDS["lon_max"] - MAP_BOUNDS["lon_min"]
        lat_span = MAP_BOUNDS["lat_max"] - MAP_BOUNDS["lat_min"]

        d_x = (lon - center_lon) / lon_span
        d_y = (center_lat - lat) / lat_span

        cx = mw // 2 + self.pan_x
        cy = mh // 2 + self.pan_y

        px = cx + int(d_x * mw * self.zoom_level)
        py = cy + int(d_y * mh * self.zoom_level)
        return px, py

    def render(self, canvas):
        if self.fullscreen_radar:
            card_x = 32
            card_y = 66
            card_w = 960
            card_h = 634
            mw = card_w - 32
            mh = 500
        else:
            card_x = 32
            card_y = 66
            card_w = 630
            card_h = 634
            mw = card_w - 32
            mh = 500

        # Subtitle with live status
        live_tag = f"🟢 {self.live_status_msg}" if self.is_live else "⚪ TRYB OFFLINE (Model regionalny)"
        sub = f"Klatka: {self.frame_labels[self.frame_idx]}  |  {live_tag}  |  Zoom: {self.zoom_level:.1f}x"
        canvas.draw_card(
            card_x, card_y, card_w, card_h,
            title="RADAR BURZ I OPADÓW (POLRAD / RAINVIEWER)",
            subtitle=sub,
            border_color=self.accent_color
        )

        mx = card_x + 16
        my = card_y + 52

        # Draw Map to clipped Image layer to prevent overspill
        map_img = Image.new("RGBA", (mw, mh), (12, 16, 24, 255))
        mdraw = ImageDraw.Draw(map_img)

        # Coordinate Grid
        grid_step = max(30, int(60 * self.zoom_level))
        start_x = (mw // 2 + self.pan_x) % grid_step
        start_y = (mh // 2 + self.pan_y) % grid_step
        for gx in range(start_x, mw, grid_step):
            mdraw.line([(gx, 0), (gx, mh)], fill=(20, 28, 42, 255), width=1)
        for gy in range(start_y, mh, grid_step):
            mdraw.line([(0, gy), (mw, gy)], fill=(20, 28, 42, 255), width=1)

        # Draw Border PL-DE
        b_pts = [self._geo_to_map(lon, lat, mw, mh) for lon, lat in BORDER_PL_DE]
        for i in range(len(b_pts) - 1):
            mdraw.line([b_pts[i], b_pts[i + 1]], fill=(100, 90, 130, 255), width=2)

        # Draw Odra River
        odra_pts = [self._geo_to_map(lon, lat, mw, mh) for lon, lat in RIVER_ODRA]
        for i in range(len(odra_pts) - 1):
            mdraw.line([odra_pts[i], odra_pts[i + 1]], fill=(16, 80, 130, 255), width=max(3, int(4 * self.zoom_level)))
            mdraw.line([odra_pts[i], odra_pts[i + 1]], fill=(30, 144, 255, 255), width=max(1, int(2 * self.zoom_level)))

        # Draw Warta River
        warta_pts = [self._geo_to_map(lon, lat, mw, mh) for lon, lat in RIVER_WARTA]
        for i in range(len(warta_pts) - 1):
            mdraw.line([warta_pts[i], warta_pts[i + 1]], fill=(16, 80, 130, 255), width=max(3, int(4 * self.zoom_level)))
            mdraw.line([warta_pts[i], warta_pts[i + 1]], fill=(30, 144, 255, 255), width=max(1, int(2 * self.zoom_level)))

        # Rain Clouds / Radar Clusters (Wind movement from West-Northwest)
        cloud_offset_lon = (self.frame_idx - 7) * 0.08
        cloud_offset_lat = (self.frame_idx - 7) * -0.02

        for cl in self.clusters:
            c_lon = cl["base_lon"] + cloud_offset_lon
            c_lat = cl["base_lat"] + cloud_offset_lat
            c_px, c_py = self._geo_to_map(c_lon, c_lat, mw, mh)

            dbz = cl["dbz"]
            for ring_step, color, _ in DBZ_LEVELS:
                if ring_step <= dbz:
                    factor = 1.0 - (ring_step / 70.0)
                    rx = int(cl["radius_lon"] * (mw / 4.0) * factor * self.zoom_level)
                    ry = int(cl["radius_lat"] * (mh / 2.3) * factor * self.zoom_level)
                    if rx > 4 and ry > 4:
                        mdraw.ellipse([(c_px - rx, c_py - ry), (c_px + rx, c_py + ry)], outline=color + (255,), width=2)
                        if ring_step >= dbz - 10:
                            mdraw.ellipse([(c_px - rx + 2, c_py - ry + 2), (c_px + rx - 2, c_py + ry - 2)], fill=color + (140,))

        # Cities & Towns
        city_font = self._f(11, bold=True)
        for c_name, c_lon, c_lat, is_target in CITIES:
            cx, cy = self._geo_to_map(c_lon, c_lat, mw, mh)
            if -50 <= cx <= mw + 50 and -20 <= cy <= mh + 20:
                dot_col = (255, 170, 0, 255) if is_target else (140, 160, 190, 255)
                r = 6 if is_target else 4
                mdraw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=dot_col)
                if is_target:
                    tr = max(10, int(12 * min(2.0, self.zoom_level)))
                    mdraw.ellipse([(cx - tr, cy - tr), (cx + tr, cy + tr)], outline=(255, 170, 0, 255), width=2)
                # Label
                text_col = (255, 255, 255, 255) if is_target else (170, 190, 215, 255)
                mdraw.text((cx + 10, cy - 8), c_name, fill=text_col, font=city_font)

        # On-Map HUD Badge (Zoom, Pan, Frame)
        hud_txt = f"🔍 ZOOM {self.zoom_level:.1f}x [L1/R1]  |  [B] Reset  |  [Y] Czcionka  |  [X] {'Podział' if self.fullscreen_radar else 'Pełny Ekran'}"
        mdraw.rounded_rectangle([(10, 10), (mw - 10, 36)], radius=6, fill=(10, 14, 22, 220), outline=(0, 240, 255, 180), width=1)
        mdraw.text((18, 14), hud_txt, fill=(0, 240, 255, 255), font=self._f(11, bold=True))

        # Paste map layer onto canvas
        canvas.image.paste(map_img, (mx, my), map_img)

        # Map Viewport Border
        canvas.draw.rectangle([(mx, my), (mx + mw, my + mh)], outline=COLOR_BORDER, width=2)

        # Bottom Timeline Bar under map
        t_y = my + mh + 12
        step_w = mw // self.total_frames
        for f_i in range(self.total_frames):
            is_cur = (f_i == self.frame_idx)
            is_now = (f_i == self.total_frames - 1)
            tx = mx + f_i * step_w
            pill_col = COLOR_ELECTRIC_BLUE if is_cur else ((28, 42, 58) if is_now else (18, 22, 30))
            out_col = COLOR_CYBER_CYAN if is_cur else COLOR_BORDER

            canvas.draw.rounded_rectangle([(tx + 2, t_y), (tx + step_w - 4, t_y + 36)], radius=6, fill=pill_col, outline=out_col)
            lbl = self.frame_labels[f_i]
            canvas.draw.text((tx + 6, t_y + 8), lbl, fill=COLOR_TEXT_PRIMARY if is_cur else COLOR_TEXT_SECONDARY, font=self._f(11, bold=is_cur))

        # ----------------------------------------------------------------------
        # If Fullscreen: Mini Floating Gorzów Telemetry
        # ----------------------------------------------------------------------
        if self.fullscreen_radar:
            fx = mx + mw - 350
            fy = my + 46
            canvas.draw.rounded_rectangle([(fx, fy), (fx + 340, fy + 175)], radius=8, fill=(14, 20, 30), outline=COLOR_CYBER_CYAN, width=2)
            canvas.draw.text((fx + 14, fy + 10), "GORZÓW WLKP. (LIVE STACJA)", fill=COLOR_CYBER_CYAN, font=self._f(13, bold=True))
            canvas.draw.line([(fx + 14, fy + 32), (fx + 326, fy + 32)], fill=COLOR_BORDER, width=1)
            canvas.draw.text((fx + 14, fy + 40), f"Stan: {self.weather_condition_str}", fill=COLOR_TEXT_PRIMARY, font=self._f(12, bold=True))
            canvas.draw.text((fx + 14, fy + 68), f"Temp: {self.temp_str} (odcz. {self.apparent_temp_str})", fill=COLOR_TEXT_SECONDARY, font=self._f(11))
            canvas.draw.text((fx + 14, fy + 94), f"Opad: {self.precipitation_str}  |  Wilg: {self.humidity_str}", fill=COLOR_TEXT_PRIMARY, font=self._f(11))
            canvas.draw.text((fx + 14, fy + 120), f"Wiatr: {self.wind_str}", fill=COLOR_PHOSPHOR_GREEN, font=self._f(11))
            canvas.draw.text((fx + 14, fy + 146), f"Zagrożenie: {self.storm_risk_str}", fill=COLOR_FLIPPER_AMBER, font=self._f(11, bold=True))
            return

        # ----------------------------------------------------------------------
        # Right Panel: Gorzów Live Telemetry & dBZ Legend (x=672, y=66, w=320, h=634)
        # ----------------------------------------------------------------------
        card_w_right = 320
        canvas.draw_card(
            672, 66, card_w_right, 634,
            title="STACJA POGODOWA GORZÓW",
            subtitle=f"Dane na żywo: {self.last_update_time_str}",
            border_color=COLOR_BORDER
        )

        rx = 688
        ry = 118
        rw = card_w_right - 32

        # Gorzów Live Alert Box
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + 195)], radius=8, fill=(22, 28, 38), outline=COLOR_CYBER_CYAN, width=1)
        canvas.draw.text((rx + 14, ry + 10), "TELEMETRIA METEO (LIVE)", fill=COLOR_CYBER_CYAN, font=self._f(13, bold=True))
        canvas.draw.line([(rx + 14, ry + 32), (rx + rw - 14, ry + 32)], fill=COLOR_BORDER, width=1)

        summary_rows = [
            ("Stan bieżący:", self.weather_condition_str),
            ("Temperatura:", f"{self.temp_str} (odcz. {self.apparent_temp_str})"),
            ("Intensywność opadów:", f"{self.precipitation_str}"),
            ("Wiatr przyziemny:", self.wind_str),
            ("Wilgotność względna:", f"{self.humidity_str}"),
            ("Zagrożenie burzowe:", self.storm_risk_str)
        ]
        s_y = ry + 38
        for lbl, val in summary_rows:
            canvas.draw.text((rx + 12, s_y), lbl, fill=COLOR_TEXT_SECONDARY, font=self._f(10, bold=False))
            canvas.draw.text((rx + 12, s_y + 14), val, fill=COLOR_TEXT_PRIMARY, font=self._f(11, bold=True))
            s_y += 26

        # Radar Reflectivity dBZ Legend
        leg_box_y = ry + 208
        canvas.draw.rounded_rectangle([(rx, leg_box_y), (rx + rw, leg_box_y + 288)], radius=8, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((rx + 14, leg_box_y + 10), "SKALA ODBICIOWOŚCI dBZ", fill=COLOR_CYBER_CYAN, font=self._f(12, bold=True))
        canvas.draw.line([(rx + 14, leg_box_y + 30), (rx + rw - 14, leg_box_y + 30)], fill=COLOR_BORDER, width=1)

        leg_y = leg_box_y + 38
        for dbz_val, col, desc in DBZ_LEVELS:
            canvas.draw.rectangle([(rx + 14, leg_y), (rx + 44, leg_y + 22)], fill=col, outline=COLOR_BORDER)
            canvas.draw.text((rx + 16, leg_y + 3), f"{dbz_val}", fill=(0, 0, 0) if dbz_val in (25, 35) else (255, 255, 255), font=self._f(11, bold=True))
            canvas.draw.text((rx + 54, leg_y + 3), desc, fill=COLOR_TEXT_PRIMARY, font=self._f(10, bold=False))
            leg_y += 32

    def handle_input(self, event: str) -> bool:
        ev = str(event).upper()
        if ev.startswith("KEY_"):
            ev = ev[4:]
        elif ev.startswith("BTN_"):
            ev = ev[4:]

        if ev in ("L1", "BUMPER_LEFT", "ZOOM_OUT", "Q", "MINUS"):
            self.zoom_level = max(1.0, round(self.zoom_level - 0.5, 1))
            if self.zoom_level == 1.0:
                self.pan_x = 0
                self.pan_y = 0
            return True
        elif ev in ("R1", "BUMPER_RIGHT", "ZOOM_IN", "E", "PLUS"):
            self.zoom_level = min(4.0, round(self.zoom_level + 0.5, 1))
            return True
        elif ev in ("Y", "BTN_Y", "I"):
            self.font_scale_idx = (self.font_scale_idx + 1) % len(self.font_scale_labels)
            return True
        elif ev in ("X", "BTN_X", "U"):
            self.fullscreen_radar = not self.fullscreen_radar
            return True
        elif ev in ("SELECT", "REFRESH", "R"):
            self._refresh_live_data()
            return True
        elif ev in ("B", "BTN_B", "K", "ESCAPE"):
            self.zoom_level = 1.0
            self.pan_x = 0
            self.pan_y = 0
            return True
        elif ev in ("A", "BTN_A", "J", "SPACE", "RETURN"):
            self.is_animating = not self.is_animating
            return True
        elif ev in ("LEFT", "A_KEY", "DPAD_LEFT"):
            if self.zoom_level > 1.0:
                self.pan_x += 50
            else:
                self.frame_idx = (self.frame_idx - 1) % self.total_frames
                self.is_animating = False
            return True
        elif ev in ("RIGHT", "D_KEY", "DPAD_RIGHT"):
            if self.zoom_level > 1.0:
                self.pan_x -= 50
            else:
                self.frame_idx = (self.frame_idx + 1) % self.total_frames
                self.is_animating = False
            return True
        elif ev in ("UP", "W_KEY", "DPAD_UP"):
            if self.zoom_level > 1.0:
                self.pan_y += 50
            return True
        elif ev in ("DOWN", "S_KEY", "DPAD_DOWN"):
            if self.zoom_level > 1.0:
                self.pan_y -= 50
            return True
        return False
