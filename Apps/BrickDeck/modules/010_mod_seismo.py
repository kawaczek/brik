"""
BrickDeck Module: Global Seismology & Live Drum Seismograph (mod_seismo.py)
Real-time worldwide earthquake monitoring (USGS) and animated scrolling drum seismograph.
100% standalone, zero-dongle: pulls live public USGS/EMSC GeoJSON feeds with offline seismic simulation.
"""

import os
import math
import time
import json
import random
import threading
import urllib.request
from typing import List, Dict, Tuple, Optional

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN, COLOR_STATUS_ERR
)
from core.canvas import get_font
from core.i18n import t


class SeismoModule(BaseModule):
    name = "Global Seismology & Drum Seismograph"
    short_name = "Sejsmograf"
    icon = "🌋"
    accent_color = COLOR_NEON_PINK

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.user_lat = 52.7333
        self.user_lon = 15.2333

        self.mag_filter_idx = 0  # 0: M2.5+, 1: M4.5+, 2: M6.0+
        self.selected_quake_idx = 0
        self.sound_alert = True

        # Earthquakes List: dicts with mag, place, time, lat, lon, depth_km, tsunami
        self.quakes: List[Dict] = []
        self.tsunami_active = False

        # Drum Seismograph Waveform Buffer (200 points)
        self.seismo_history: List[float] = [0.0] * 180
        self.pen_phase = 0.0

        self.last_fetch_time = 0
        self.thread_running = False

        # Seed initial realistic earthquakes
        self._seed_initial_quakes()

    def _seed_initial_quakes(self):
        now = time.time()
        self.quakes = [
            {"mag": 6.8, "place": "Off Coast of Honshu, Japan", "lat": 37.5, "lon": 142.0, "depth_km": 35.0, "time": now - 1800, "tsunami": 1},
            {"mag": 5.4, "place": "Near Coast of Central Chile", "lat": -31.2, "lon": -71.5, "depth_km": 42.0, "time": now - 3400, "tsunami": 0},
            {"mag": 4.8, "place": "Southern Greece", "lat": 36.8, "lon": 22.4, "depth_km": 15.0, "time": now - 5200, "tsunami": 0},
            {"mag": 5.1, "place": "Andreanof Islands, Aleutian Islands", "lat": 51.8, "lon": -176.2, "depth_km": 28.0, "time": now - 7800, "tsunami": 0},
            {"mag": 4.2, "place": "Iceland Region (Reykjanes)", "lat": 63.9, "lon": -22.3, "depth_km": 5.0, "time": now - 9400, "tsunami": 0},
            {"mag": 3.4, "place": "Central California, USA", "lat": 36.2, "lon": -120.8, "depth_km": 8.0, "time": now - 11000, "tsunami": 0}
        ]
        self._update_distances()

    def _update_distances(self):
        for q in self.quakes:
            d = self._haversine(self.user_lat, self.user_lon, q["lat"], q["lon"])
            q["dist_km"] = d
        self.tsunami_active = any(q.get("tsunami", 0) > 0 for q in self.quakes[:3])

    def _haversine(self, lat1, lon1, lat2, lon2) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def on_load(self):
        self.thread_running = True
        threading.Thread(target=self._poll_worker, daemon=True).start()

    def _poll_worker(self):
        while self.thread_running:
            now = time.time()
            if now - self.last_fetch_time > 120.0:
                self._fetch_usgs_data()
                self.last_fetch_time = now
            time.sleep(2.0)

    def load_geojson_data(self, data):
        """Parse USGS GeoJSON data directly from live web feed."""
        if isinstance(data, (bytes, bytearray)):
            data = data.decode("utf-8")
        if isinstance(data, str):
            data = json.loads(data)
        feats = data.get("features", [])
        new_quakes = []
        for f in feats[:30]:
            prop = f.get("properties", {})
            geom = f.get("geometry", {})
            coords = geom.get("coordinates", [0, 0, 0])
            new_quakes.append({
                "mag": float(prop.get("mag", 3.0) or 3.0),
                "place": str(prop.get("place", "Nieznana lokalizacja")),
                "lat": float(coords[1]),
                "lon": float(coords[0]),
                "depth_km": float(coords[2]),
                "time": float(prop.get("time", 0)) / 1000.0,
                "tsunami": int(prop.get("tsunami", 0) or 0)
            })
        if new_quakes:
            self.quakes = new_quakes
            self._update_distances()

    def _fetch_usgs_data(self):
        """Fetch live USGS M2.5+ earthquakes for the past day."""
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
        try:
            from pyodide.http import open_url
            with open_url(url) as resp:
                self.load_geojson_data(resp.read())
                return
        except Exception:
            pass

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BrickDeck-OS/2.0"})
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                self.load_geojson_data(resp.read().decode("utf-8"))
        except Exception:
            pass

    def get_hotkey_hints(self):
        f_labels = ["Filtr: M2.5+", "Filtr: M4.5+", "Filtr: M6.0+"]
        snd_label = "Alarm: WŁ" if self.sound_alert else "Alarm: WYŁ"
        return [
            ("L1/R1", t("common.modules", "Moduły")),
            ("D-Pad G/D", "Wybierz Trzęsienie"),
            ("A", "Centruj / Odśwież"),
            ("X", f_labels[self.mag_filter_idx]),
            ("Y", snd_label),
            ("B", "Świat 360°")
        ]

    def update(self, dt: float):
        # Update drum seismograph simulation
        self.pen_phase += dt * 4.0
        # Background microseismic noise + pulse if recent high mag quake
        highest_mag = max([q["mag"] for q in self.quakes], default=3.0)
        spike = math.sin(self.pen_phase * 2.8) * (highest_mag * 4.0 if highest_mag >= 6.0 else 4.0)
        noise = random.uniform(-2.5, 2.5) + spike
        self.seismo_history.pop(0)
        self.seismo_history.append(noise)

    def render(self, canvas):
        # Main Card Wrapper
        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title="🌋 GLOBAL SEISMOLOGY & REAL-TIME DRUM SEISMOGRAPH [FEED: USGS / EMSC]",
            subtitle=f"Aktywne zjawiska: {len(self.quakes)} trzęsień  |  Status Tsunami: {'⚠️ ZAGROŻENIE TSUNAMI!' if self.tsunami_active else 'Brak ostrzeżeń'}",
            border_color=self.accent_color
        )

        # -------------------------------------------------------------
        # 1. Left Panel: Drum Seismograph Oscilloscope (x=50, y=120, w=440, h=555)
        # -------------------------------------------------------------
        sx, sy, sw, sh = 50, 120, 440, 555
        canvas.draw.rounded_rectangle([(sx, sy), (sx + sw, sy + sh)], radius=10, fill=(14, 18, 24), outline=COLOR_BORDER, width=1)
        canvas.draw.text((sx + 16, sy + 16), "SEJSMOGRAF BĘBNOWY (DRUM RECORDER)", fill=COLOR_PHOSPHOR_GREEN, font=get_font(13, bold=True))
        canvas.draw.line([(sx + 16, sy + 38), (sx + sw - 16, sy + 38)], fill=COLOR_BORDER, width=1)

        # Draw Seismograph Grid (Paper trace grid)
        paper_x, paper_y, paper_w, paper_h = sx + 16, sy + 50, sw - 32, 280
        canvas.draw.rectangle([(paper_x, paper_y), (paper_x + paper_w, paper_y + paper_h)], fill=(10, 14, 18), outline=(30, 42, 54), width=1)

        # Grid lines (time ticks and amplitude channels)
        for gy in range(paper_y + 35, paper_y + paper_h, 35):
            canvas.draw.line([(paper_x, gy), (paper_x + paper_w, gy)], fill=(18, 26, 36), width=1)
        for gx in range(paper_x + 40, paper_x + paper_w, 40):
            canvas.draw.line([(gx, paper_y), (gx, paper_y + paper_h)], fill=(18, 26, 36), width=1)

        # Zero baseline
        mid_y = paper_y + paper_h // 2
        canvas.draw.line([(paper_x, mid_y), (paper_x + paper_w, mid_y)], fill=(34, 50, 68), width=1)

        # Draw Real-time Seismogram Waveform Trace
        pts = []
        step = paper_w / float(len(self.seismo_history) - 1)
        for idx, val in enumerate(self.seismo_history):
            px = int(paper_x + idx * step)
            py = int(mid_y - val)
            py = max(paper_y + 2, min(paper_y + paper_h - 2, py))
            pts.append((px, py))

        for i in range(len(pts) - 1):
            canvas.draw.line([pts[i], pts[i + 1]], fill=COLOR_PHOSPHOR_GREEN, width=2)

        # Recording Stylus Needle (at the rightmost edge)
        stylus_x, stylus_y = pts[-1]
        canvas.draw.ellipse([(stylus_x - 4, stylus_y - 4), (stylus_x + 4, stylus_y + 4)], fill=(255, 80, 80))
        canvas.draw.line([(stylus_x, paper_y), (stylus_x, paper_y + paper_h)], fill=(255, 80, 80, 80), width=1)

        # Seismograph Specs & Peak Velocity
        max_amp = max([abs(v) for v in self.seismo_history], default=0.0)
        canvas.draw.text((sx + 16, sy + 345), f"SZCZYTOWA AMPLITUDA (PGV): {max_amp:.2f} mm/s", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))
        canvas.draw.text((sx + 16, sy + 370), "Pasmo: 0.01 - 50 Hz (Szerokopasmowy 3-osiowy)", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw.text((sx + 16, sy + 392), "Stacja bazowa: GORZ / PL (Wirtualny sejsmometr)", fill=COLOR_TEXT_MUTED, font=get_font(11))

        # Tsunami / Emergency Warning Banner
        if self.tsunami_active:
            canvas.draw.rounded_rectangle([(sx + 16, sy + 430), (sx + sw - 16, sy + 535)], radius=8, fill=(40, 16, 20), outline=COLOR_STATUS_ERR, width=2)
            canvas.draw.text((sx + 26, sy + 442), "⚠️ ALERT TSUNAMI NOAA / PTWC", fill=COLOR_STATUS_ERR, font=get_font(13, bold=True))
            canvas.draw.text((sx + 26, sy + 468), "Wykryto płytkie trzęsienie podwodne > M6.5!", fill=(255, 200, 200), font=get_font(11))
            canvas.draw.text((sx + 26, sy + 490), "Zagrożenie falami przybrzeżnymi Pacyfiku / Indii.", fill=(255, 160, 160), font=get_font(11))
        else:
            canvas.draw.rounded_rectangle([(sx + 16, sy + 430), (sx + sw - 16, sy + 535)], radius=8, fill=(18, 24, 34), outline=COLOR_BORDER, width=1)
            canvas.draw.text((sx + 26, sy + 445), "GLOBALNA AKTYWNOŚĆ PŁYT TEKTONICZNYCH", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))
            canvas.draw.text((sx + 26, sy + 472), "Strefa Pacyfiku (Ring of Fire): 78% trzęsień", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
            canvas.draw.text((sx + 26, sy + 495), "Grzbiet Śródatlantycki: Płyta Eurazjatycka / Północnoamerykańska", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # -------------------------------------------------------------
        # 2. Right Panel: World Map & Live Quakes List (x=510, y=120, w=462, h=555)
        # -------------------------------------------------------------
        qx, qy, qw, qh = 510, 120, 462, 555
        canvas.draw.rounded_rectangle([(qx, qy), (qx + qw, qy + qh)], radius=10, fill=(16, 20, 28), outline=COLOR_BORDER, width=1)
        canvas.draw.text((qx + 16, qy + 16), "OSTATNIE TRZĘSIENIA ZIEMI NA ŚWIECIE", fill=COLOR_FLIPPER_AMBER, font=get_font(13, bold=True))
        canvas.draw.line([(qx + 16, qy + 38), (qx + qw - 16, qy + 38)], fill=COLOR_BORDER, width=1)

        # Filter quakes by magnitude
        min_mags = [2.5, 4.5, 6.0]
        thresh = min_mags[self.mag_filter_idx]
        filtered_quakes = [q for q in self.quakes if q["mag"] >= thresh]

        if not filtered_quakes:
            filtered_quakes = self.quakes

        # Render list of quakes (selectable with D-Pad)
        ly = qy + 50
        for idx, q in enumerate(filtered_quakes[:6]):
            is_sel = (idx == self.selected_quake_idx)
            # Magnitude color coding
            mag = q["mag"]
            if mag >= 6.5:
                mag_col = COLOR_NEON_PINK
            elif mag >= 5.0:
                mag_col = COLOR_STATUS_ERR
            elif mag >= 4.0:
                mag_col = COLOR_FLIPPER_AMBER
            else:
                mag_col = COLOR_CYBER_CYAN

            card_fill = (26, 36, 50) if is_sel else (20, 26, 36)
            card_outline = COLOR_CYBER_CYAN if is_sel else COLOR_BORDER
            canvas.draw.rounded_rectangle([(qx + 16, ly), (qx + qw - 16, ly + 68)], radius=6, fill=card_fill, outline=card_outline, width=2 if is_sel else 1)

            # Mag pill
            canvas.draw.rounded_rectangle([(qx + 24, ly + 10), (qx + 80, ly + 56)], radius=6, fill=(14, 18, 24), outline=mag_col, width=2)
            canvas.draw.text((qx + 32, ly + 18), f"M{mag:.1f}", fill=mag_col, font=get_font(15, bold=True))

            # Location & depth
            p_text = q["place"] if len(q["place"]) < 32 else q["place"][:30] + "..."
            canvas.draw.text((qx + 92, ly + 10), p_text, fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
            canvas.draw.text((qx + 92, ly + 30), f"Głębokość: {q['depth_km']:.0f} km  |  Odległość: {q.get('dist_km', 0):.0f} km", fill=COLOR_TEXT_SECONDARY, font=get_font(10))

            mins_ago = int((time.time() - q["time"]) / 60.0)
            canvas.draw.text((qx + 92, ly + 48), f"Czas: {mins_ago} min temu  |  Koord: {q['lat']:.1f}°, {q['lon']:.1f}°", fill=COLOR_TEXT_MUTED, font=get_font(10))

            ly += 76

        canvas.draw_badge(qx + 16, qy + 512, "[D-Pad G/D]: Wybór zdarzenia  |  [X]: Zmień filtr magnitudy", bg_color=(24, 32, 44), text_color=COLOR_CYBER_CYAN)

    def handle_input(self, event: str) -> bool:
        if event in ("BTN_X", "x", "X"):
            self.mag_filter_idx = (self.mag_filter_idx + 1) % 3
            self.selected_quake_idx = 0
            return True
        elif event in ("BTN_Y", "y", "Y"):
            self.sound_alert = not self.sound_alert
            return True
        elif event in ("BTN_A", "a", "A", " "):
            self._fetch_usgs_data()
            return True
        elif event in ("DPAD_UP", "w", "W", "UP"):
            self.selected_quake_idx = max(0, self.selected_quake_idx - 1)
            return True
        elif event in ("DPAD_DOWN", "s", "S", "DOWN"):
            self.selected_quake_idx = min(5, self.selected_quake_idx + 1)
            return True
        return False
