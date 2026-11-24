"""
BrickDeck Module: Gorzów Wielkopolski Live Transit Map & Fleet Radar
Renders a real-time vector map of Gorzów with Warta river, tram lines, and live GPS vehicles.
"""

import math
import time
import ssl
import json
import urllib.request
import threading
from typing import List, Dict, Optional, Tuple

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)
from core.canvas import get_font

API_VEHICLES_URL = "https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=v"

# Geographic reference boundaries for Gorzów Wielkopolski
GORZOW_LAT_MIN = 52.700
GORZOW_LAT_MAX = 52.775
GORZOW_LON_MIN = 52.700  # Will use correct lon below
GORZOW_LON_MIN = 15.150
GORZOW_LON_MAX = 15.305

# River Warta geographic coordinates (East to West)
WARTA_COORDS = [
    (15.310, 52.715),
    (15.285, 52.722),
    (15.260, 52.727),
    (15.237, 52.729),  # Center / Most Staromiejski
    (15.215, 52.731),
    (15.185, 52.734),
    (15.150, 52.737)
]

# Major Tram line vector paths
TRAM_CORRIDOR_1 = [
    (15.295, 52.760),  # Silwana
    (15.275, 52.750),  # Walczaka
    (15.255, 52.742),  # Biskupa Pluty
    (15.238, 52.733),  # Katedra / Sikorskiego
    (15.210, 52.734),  # Brama Koszary
    (15.180, 52.737),  # Kostrzyńska
    (15.160, 52.738)   # Wieprzyce
]

TRAM_CORRIDOR_2 = [
    (15.230, 52.765),  # Piaski
    (15.233, 52.750),  # Chrobrego Północ
    (15.238, 52.733),  # Katedra
    (15.210, 52.734),  # Wieprzyce junction
    (15.160, 52.738)
]

LANDMARKS = [
    ("Centrum / Katedra", 15.238, 52.733),
    ("Silwana (Pętla)", 15.295, 52.760),
    ("Wieprzyce (Pętla)", 15.160, 52.738),
    ("Piaski (Pętla)", 15.230, 52.765),
    ("Górczyn", 15.265, 52.752),
    ("Zamoście", 15.238, 52.720),
    ("Dworzec Główny", 15.228, 52.728)
]


class MzkMapModule(BaseModule):
    name = "Gorzów Live Transit Map"
    short_name = "MZK Mapa"
    icon = "🗺️"
    accent_color = COLOR_FLIPPER_AMBER

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.vehicles: List[Dict] = []
        self.selected_idx = 0
        self.filter_mode = 0  # 0: Wszystkie, 1: Tramwaje, 2: Autobusy
        self.filter_labels = ["Wszystkie", "Tramwaje", "Autobusy"]
        self.last_fetch_time = 0.0
        self.fetch_status = "Inicjalizacja..."
        self.pulse_phase = 0.0

        # Map Viewport Transform
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        # Background polling thread
        self.thread_running = False
        self.worker_thread: Optional[threading.Thread] = None

    def on_load(self):
        self._init_synthetic_fallback()
        self.thread_running = True
        self.worker_thread = threading.Thread(target=self._poll_worker, daemon=True)
        self.worker_thread.start()

    def on_deactivate(self):
        pass

    def get_hotkey_hints(self):
        filter_name = self.filter_labels[self.filter_mode]
        return [
            ("L1/R1", "Moduły"),
            ("D-Pad", "Wybór wozu / Przesuń"),
            ("A", "Wycentruj na wozie"),
            ("B", f"Filtr: {filter_name}"),
            ("X/Y", "Zoom +/-")
        ]

    def _init_synthetic_fallback(self):
        """Provide realistic Gorzów fleet if offline."""
        self.vehicles = [
            {"id": "301", "lineLabel": "1", "type": "Tramwaj", "lat": 52.745, "lon": 15.260, "bearing": 225.0, "depid": 1001},
            {"id": "302", "lineLabel": "2", "type": "Tramwaj", "lat": 52.755, "lon": 15.232, "bearing": 180.0, "depid": 1002},
            {"id": "303", "lineLabel": "3", "type": "Tramwaj", "lat": 52.736, "lon": 15.220, "bearing": 90.0, "depid": 1003},
            {"id": "650", "lineLabel": "101", "type": "Autobus", "lat": 52.730, "lon": 15.236, "bearing": 45.0, "depid": 2001},
            {"id": "682", "lineLabel": "124", "type": "Autobus", "lat": 52.762, "lon": 15.265, "bearing": 310.0, "depid": 2002},
            {"id": "654", "lineLabel": "104", "type": "Autobus", "lat": 52.738, "lon": 15.205, "bearing": 120.0, "depid": 2003},
            {"id": "662", "lineLabel": "126", "type": "Autobus", "lat": 52.743, "lon": 15.212, "bearing": 270.0, "depid": 2004},
        ]
        self.fetch_status = "Tryb offline (Symulacja)"

    def _poll_worker(self):
        """Polls Gorzów MZK Trapeze API every 5 seconds."""
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        while self.thread_running:
            try:
                req = urllib.request.Request(API_VEHICLES_URL, headers={"User-Agent": "BrickDeck-MZK/1.0"})
                with urllib.request.urlopen(req, context=ssl_ctx, timeout=4.5) as resp:
                    raw = resp.read().decode("utf-8")
                    data = json.loads(raw)
                    if isinstance(data, list) and len(data) > 0:
                        self.vehicles = data
                        self.last_fetch_time = time.time()
                        self.fetch_status = f"LIVE GPS ({len(data)} wozów)"
            except Exception as e:
                # Keep existing data on transient network drop
                if not self.vehicles:
                    self._init_synthetic_fallback()
                self.fetch_status = "Błąd sieci / Cache"

            time.sleep(5.0)

    def update(self, dt: float):
        self.pulse_phase = (self.pulse_phase + dt * 4.0) % (2 * math.pi)

    def _get_filtered_vehicles(self) -> List[Dict]:
        if self.filter_mode == 1:
            return [v for v in self.vehicles if v.get("type") == "Tramwaj"]
        elif self.filter_mode == 2:
            return [v for v in self.vehicles if v.get("type") == "Autobus"]
        return self.vehicles

    def _geo_to_map_px(self, lon: float, lat: float, map_x: int, map_y: int, map_w: int, map_h: int) -> Tuple[int, int]:
        """Convert GPS lat/lon to map screen pixel coordinates."""
        norm_x = (lon - GORZOW_LON_MIN) / (GORZOW_LON_MAX - GORZOW_LON_MIN)
        norm_y = (GORZOW_LAT_MAX - lat) / (GORZOW_LAT_MAX - GORZOW_LAT_MIN)

        cx = map_x + map_w // 2
        cy = map_y + map_h // 2

        px = map_x + int(norm_x * map_w)
        py = map_y + int(norm_y * map_h)

        # Apply zoom and pan around map center
        zx = int(cx + (px - cx + self.pan_x) * self.zoom)
        zy = int(cy + (py - cy + self.pan_y) * self.zoom)
        return zx, zy

    def render(self, canvas):
        # 1. Main Container Cards
        map_card_x = 32
        map_card_y = 66
        map_card_w = 644
        map_card_h = 634

        info_card_x = 690
        info_card_y = 66
        info_card_w = 302
        info_card_h = 634

        filtered_vehs = self._get_filtered_vehicles()
        if self.selected_idx >= len(filtered_vehs):
            self.selected_idx = max(0, len(filtered_vehs) - 1)

        trams_cnt = sum(1 for v in self.vehicles if v.get("type") == "Tramwaj")
        buses_cnt = sum(1 for v in self.vehicles if v.get("type") == "Autobus")

        # Map Card
        canvas.draw_card(
            map_card_x, map_card_y, map_card_w, map_card_h,
            title="GORZÓW TACTICAL FLEET RADAR",
            subtitle=f"{self.fetch_status}  |  Zoom: {self.zoom:.1f}x",
            border_color=self.accent_color
        )

        # Inner Map Canvas
        mx = map_card_x + 12
        my = map_card_y + 48
        mw = map_card_w - 24
        mh = map_card_h - 60

        canvas.draw.rectangle([(mx, my), (mx + mw, my + mh)], fill=(12, 16, 22), outline=COLOR_BORDER, width=1)

        # Draw Grid Coordinates
        for gx in range(mx + 40, mx + mw, 60):
            canvas.draw.line([(gx, my), (gx, my + mh)], fill=(18, 26, 36), width=1)
        for gy in range(my + 40, my + mh, 60):
            canvas.draw.line([(mx, gy), (mx + mw, gy)], fill=(18, 26, 36), width=1)

        # Draw River Warta (Tactical Glowing Curve)
        warta_pts = [self._geo_to_map_px(lon, lat, mx, my, mw, mh) for lon, lat in WARTA_COORDS]
        for i in range(len(warta_pts) - 1):
            p1 = warta_pts[i]
            p2 = warta_pts[i + 1]
            canvas.draw.line([p1, p2], fill=(16, 80, 130), width=6)
            canvas.draw.line([p1, p2], fill=(30, 144, 255), width=2)

        # River label
        if len(warta_pts) > 3:
            rx, ry = warta_pts[3]
            canvas.draw.text((rx - 30, ry + 8), "Rzeka Warta", fill=(30, 144, 255), font=get_font(10, bold=True))

        # Draw Tram Tracks (Yellow/Amber dashed or solid)
        for corridor, c_col in [(TRAM_CORRIDOR_1, (200, 140, 20)), (TRAM_CORRIDOR_2, (180, 120, 20))]:
            t_pts = [self._geo_to_map_px(lon, lat, mx, my, mw, mh) for lon, lat in corridor]
            for i in range(len(t_pts) - 1):
                canvas.draw.line([t_pts[i], t_pts[i + 1]], fill=c_col, width=2)

        # Draw Landmarks
        font_land = get_font(10, bold=False)
        for name, lon, lat in LANDMARKS:
            lx, ly = self._geo_to_map_px(lon, lat, mx, my, mw, mh)
            if mx <= lx <= mx + mw and my <= ly <= my + mh:
                canvas.draw.ellipse([(lx - 3, ly - 3), (lx + 3, ly + 3)], fill=(100, 120, 150))
                canvas.draw.text((lx + 6, ly - 5), name, fill=COLOR_TEXT_SECONDARY, font=font_land)

        # Draw Active Vehicles
        font_veh = get_font(11, bold=True)
        sel_veh = filtered_vehs[self.selected_idx] if filtered_vehs else None

        for idx, veh in enumerate(filtered_vehs):
            v_lat = veh.get("lat", 0.0)
            v_lon = veh.get("lon", 0.0)
            v_type = veh.get("type", "Autobus")
            v_line = str(veh.get("lineLabel", "?"))
            bearing = float(veh.get("bearing", 0.0))

            vx, vy = self._geo_to_map_px(v_lon, v_lat, mx, my, mw, mh)

            # Skip if out of viewport bounds
            if not (mx - 20 <= vx <= mx + mw + 20 and my - 20 <= vy <= my + mh + 20):
                continue

            is_selected = (sel_veh and veh.get("id") == sel_veh.get("id"))
            is_tram = (v_type == "Tramwaj")

            marker_col = COLOR_FLIPPER_AMBER if is_tram else COLOR_CYBER_CYAN
            radius = 12 if is_selected else 9

            # Selected pulse animation
            if is_selected:
                pulse_r = radius + int(math.sin(self.pulse_phase) * 4) + 4
                canvas.draw.ellipse([(vx - pulse_r, vy - pulse_r), (vx + pulse_r, vy + pulse_r)],
                                    outline=COLOR_NEON_PINK, width=2)

            # Vehicle dot
            canvas.draw.ellipse([(vx - radius, vy - radius), (vx + radius, vy + radius)],
                                fill=marker_col, outline=COLOR_TEXT_PRIMARY, width=1)

            # Bearing Arrow
            if bearing > 0:
                brad = math.radians(bearing - 90)
                ax = vx + int(math.cos(brad) * (radius + 6))
                ay = vy + int(math.sin(brad) * (radius + 6))
                canvas.draw.line([(vx, vy), (ax, ay)], fill=COLOR_TEXT_PRIMARY, width=2)

            # Line label inside/beside marker
            canvas.draw.text((vx - len(v_line) * 3 - 1, vy - 6), v_line, fill=(10, 14, 20), font=font_veh)

        # Draw Compass Rose (N)
        canvas.draw.rectangle([(mx + mw - 46, my + 10), (mx + mw - 10, my + 46)], fill=(20, 26, 36), outline=COLOR_BORDER)
        canvas.draw.text((mx + mw - 34, my + 18), "⬆ N", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))

        # ----------------------------------------------------------------------
        # Right Panel: Fleet Stats & Selected Vehicle Inspector
        # ----------------------------------------------------------------------
        canvas.draw_card(
            info_card_x, info_card_y, info_card_w, info_card_h,
            title="TELEMETRIA FLOTY",
            subtitle=f"Tramwaje: {trams_cnt}  |  Autobusy: {buses_cnt}",
            border_color=COLOR_BORDER
        )

        ix = info_card_x + 16
        iy = info_card_y + 54

        # Selected Vehicle Card Box
        canvas.draw.rounded_rectangle([(ix, iy), (ix + info_card_w - 32, iy + 220)],
                                      radius=8, fill=(22, 28, 38), outline=COLOR_CYBER_CYAN, width=1)

        font_label = get_font(12, bold=False)
        font_val = get_font(13, bold=True)
        font_big = get_font(18, bold=True)

        if sel_veh:
            v_type = sel_veh.get("type", "Autobus")
            v_line = sel_veh.get("lineLabel", "?")
            v_id = sel_veh.get("id", "?")
            v_lat = sel_veh.get("lat", 0.0)
            v_lon = sel_veh.get("lon", 0.0)
            v_bearing = sel_veh.get("bearing", 0.0)
            v_depid = sel_veh.get("depid", "N/A")

            # Icon & Line
            icon = "🚋" if v_type == "Tramwaj" else "🚌"
            canvas.draw.text((ix + 12, iy + 12), f"{icon} LINIA {v_line}", fill=COLOR_FLIPPER_AMBER if v_type == "Tramwaj" else COLOR_CYBER_CYAN, font=font_big)
            canvas.draw.text((ix + 180, iy + 16), f"Wóz #{v_id}", fill=COLOR_TEXT_PRIMARY, font=font_val)

            canvas.draw.line([(ix + 12, iy + 44), (ix + info_card_w - 44, iy + 44)], fill=COLOR_BORDER, width=1)

            # Details table
            items = [
                ("Typ pojazdu:", v_type),
                ("Szerokość (Lat):", f"{v_lat:.5f}°"),
                ("Długość (Lon):", f"{v_lon:.5f}°"),
                ("Kurs (Bearing):", f"{v_bearing:.1f}°"),
                ("ID Kursu:", str(v_depid)),
                ("Status GPS:", "Aktywny w trasie")
            ]
            row_y = iy + 52
            for lbl, val in items:
                canvas.draw.text((ix + 12, row_y), lbl, fill=COLOR_TEXT_SECONDARY, font=font_label)
                canvas.draw.text((ix + 140, row_y), val, fill=COLOR_TEXT_PRIMARY, font=font_val)
                row_y += 24
        else:
            canvas.draw.text((ix + 16, iy + 40), "Brak pojazdów do wyświetlenia", fill=COLOR_TEXT_MUTED, font=font_label)

        # Vehicle List Header
        list_y = iy + 236
        canvas.draw.text((ix, list_y), f"POJAZDY W RUCHU ({len(filtered_vehs)})", fill=COLOR_CYBER_CYAN, font=get_font(13, bold=True))
        canvas.draw.line([(ix, list_y + 22), (ix + info_card_w - 32, list_y + 22)], fill=COLOR_BORDER, width=1)

        # Scrollable Vehicles List
        row_y = list_y + 30
        visible_rows = 9
        start_row = max(0, min(self.selected_idx - 3, len(filtered_vehs) - visible_rows))

        for idx in range(start_row, min(len(filtered_vehs), start_row + visible_rows)):
            veh = filtered_vehs[idx]
            is_active = (idx == self.selected_idx)
            v_type = veh.get("type", "Autobus")
            v_line = veh.get("lineLabel", "?")
            v_id = veh.get("id", "?")

            bg_col = (36, 46, 62) if is_active else (20, 24, 32)
            outline_col = COLOR_CYBER_CYAN if is_active else COLOR_BORDER

            canvas.draw.rounded_rectangle([(ix, row_y), (ix + info_card_w - 32, row_y + 26)],
                                          radius=5, fill=bg_col, outline=outline_col, width=1)

            t_mark = "🚋" if v_type == "Tramwaj" else "🚌"
            canvas.draw.text((ix + 8, row_y + 5), f"{t_mark} {v_line}", fill=COLOR_FLIPPER_AMBER if v_type == "Tramwaj" else COLOR_CYBER_CYAN, font=font_val)
            canvas.draw.text((ix + 90, row_y + 5), f"Wóz #{v_id}", fill=COLOR_TEXT_PRIMARY, font=font_label)

            row_y += 32

    def handle_input(self, event: str) -> bool:
        filtered_vehs = self._get_filtered_vehicles()
        if event == "UP":
            if self.selected_idx > 0:
                self.selected_idx -= 1
                return True
        elif event == "DOWN":
            if self.selected_idx < len(filtered_vehs) - 1:
                self.selected_idx += 1
                return True
        elif event == "LEFT":
            self.pan_x += 40.0
            return True
        elif event == "RIGHT":
            self.pan_x -= 40.0
            return True
        elif event == "BTN_A":
            # Center on selected vehicle
            if 0 <= self.selected_idx < len(filtered_vehs):
                sel = filtered_vehs[self.selected_idx]
                v_lat = sel.get("lat", 52.733)
                v_lon = sel.get("lon", 15.233)
                # Reset pan so this point is centered
                self.pan_x = 0.0
                self.pan_y = 0.0
            return True
        elif event == "BTN_B":
            # Cycle filter
            self.filter_mode = (self.filter_mode + 1) % len(self.filter_labels)
            self.selected_idx = 0
            return True
        elif event == "BTN_X":
            # Zoom In
            self.zoom = min(3.0, self.zoom + 0.25)
            return True
        elif event == "BTN_Y":
            # Zoom Out
            self.zoom = max(0.6, self.zoom - 0.25)
            return True
        return False
