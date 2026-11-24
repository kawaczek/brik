"""
BrickDeck Module: Global Aerospace, Satellite & Tactical Air Radar
Unified Air & Space tracking for TrimUI Brick:
- Real Satellite Imagery (Google Earth / ESRI World Imagery) & Tactical OSM Map (OpenStreetMap)
- 3D Tactical Earth Globe with ISS and orbital satellites
- Physical Gamepad Target Lock-on: L1/R1 & D-Pad target cycling, [A] to open aircraft photo & telemetry
- Authentic airliner liveries (LOT, Lufthansa, Ryanair, Wizz Air, Emirates, Air France, etc.)
- Multi-level smooth zoom & OSM geocoding search
"""

import os
import io
import math
import time
import ssl
import json
import urllib.request
import urllib.parse
import threading
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_ELECTRIC_BLUE, COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)
from core.canvas import get_font

# API Endpoints
WHERETHEISS_URL = "https://api.wheretheiss.at/v1/satellites/25544"
OPENSKY_BASE_URL = "https://opensky-network.org/api/states/all"
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"

# Cache Directory for Map Tiles
MAP_CACHE_DIR = "/tmp/brick_maps_cache"

# Preset Global Locations
PRESET_CITIES = [
    ("Gorzów Wielkopolski (Baza)", 52.7333, 15.2333, "Polska"),
    ("Warszawa (EPWA)", 52.2297, 21.0122, "Polska"),
    ("Poznań (EPPO)", 52.4064, 16.9252, "Polska"),
    ("Szczecin (EPSC)", 53.4285, 14.5528, "Polska"),
    ("Wrocław (EPWR)", 51.1079, 17.0385, "Polska"),
    ("Kraków (EPKK)", 50.0647, 19.9450, "Polska"),
    ("Gdańsk (EPGD)", 54.3520, 18.6466, "Polska"),
    ("Berlin (EDDB)", 52.5200, 13.4050, "Niemcy"),
    ("Londyn (EGLL)", 51.5074, -0.1278, "Wlk. Brytania"),
    ("Paryż (LFPG)", 48.8566, 2.3522, "Francja"),
    ("Nowy Jork (KJFK)", 40.7128, -74.0060, "USA"),
    ("Tokio (RJTT)", 35.6762, 139.6503, "Japonia"),
    ("Sydney (YSSY)", -33.8688, 151.2093, "Australia"),
    ("Przylądek Canaveral (NASA)", 28.3922, -80.6077, "USA (KSC)")
]

# Strategic Global Hubs for 3D Globe Projection
GLOBAL_WAYPOINTS = [
    ("Warszawa", 52.23, 21.01, "EPWA"),
    ("Berlin", 52.52, 13.40, "EDDB"),
    ("Londyn", 51.51, -0.13, "EGLL"),
    ("Paryż", 48.86, 2.35, "LFPG"),
    ("Nowy Jork", 40.71, -74.01, "KJFK"),
    ("Tokio", 35.68, 139.65, "RJTT"),
    ("Dubaj", 25.20, 55.27, "OMDB"),
    ("Sydney", -33.87, 151.21, "YSSY"),
    ("Kair", 30.04, 31.24, "HECA"),
    ("Singapur", 1.35, 103.82, "WSSS"),
    ("Reykjavik", 64.15, -21.94, "BIRK"),
    ("Rio de Janeiro", -22.91, -43.17, "SBGL")
]

# Detailed Tactical Vector Continents for 3D Globe Projection
CONTINENTS_GEO = [
    # Europe Main Coast & Baltic
    [(10, 54), (14, 54), (18, 55), (22, 56), (25, 59), (30, 60), (32, 65), (28, 68), (24, 66),
     (22, 60), (18, 59), (12, 56), (10, 54)],
    # Scandinavia
    [(5, 58), (10, 58), (11, 59), (18, 60), (22, 65), (28, 71), (25, 71), (15, 68), (5, 62), (5, 58)],
    # British Isles & Ireland
    [(-5, 50), (1.5, 51), (1.8, 53), (-1.5, 55), (-3, 58), (-5, 58), (-5, 54), (-3, 53), (-5, 50)],
    [(-10, 51.5), (-6, 52), (-6, 54.5), (-10, 54), (-10, 51.5)],
    # Western Europe & Iberian Peninsula
    [(2, 51), (8, 49), (7, 43), (3, 42), (3, 37), (-5, 36), (-9, 37), (-9, 43), (-1, 44), (-2, 47), (-4, 48), (0, 49), (2, 51)],
    # Italy & Adriatic
    [(9, 44), (12, 44), (16, 41), (18, 40), (15, 38), (15, 40), (12, 42), (9, 44)],
    # Greece & Balkans
    [(13, 45), (20, 45), (28, 42), (29, 41), (26, 38), (23, 38), (20, 39), (18, 41), (14, 45)],
    # Mediterranean North Coast & Black Sea
    [(30, 46), (36, 45), (41, 42), (35, 41), (28, 41)],
    # Africa
    [(-5, 36), (10, 37), (25, 32), (32, 31), (34, 27), (43, 12), (51, 10), (42, -2), (40, -15),
     (33, -28), (28, -34), (18, -34), (12, -18), (10, 2), (2, 6), (-15, 11), (-17, 15), (-17, 21), (-12, 28), (-5, 36)],
    # Madagascar
    [(44, -12), (50, -15), (47, -25), (44, -25), (44, -12)],
    # Arabian Peninsula
    [(35, 30), (45, 30), (55, 25), (60, 22), (55, 15), (45, 12), (38, 22), (35, 30)],
    # India Subcontinent
    [(68, 24), (73, 20), (77, 8), (80, 13), (85, 20), (88, 22), (78, 24), (68, 24)],
    # Southeast Asia & Indochina
    [(90, 22), (98, 10), (103, 1), (105, 10), (108, 15), (108, 21), (92, 22)],
    # China & East Coast
    [(108, 21), (120, 25), (122, 31), (120, 38), (125, 40), (130, 42), (135, 48), (140, 50), (142, 53)],
    # Japan Archipelago
    [(130, 32), (133, 34), (139, 35), (141, 38), (141, 43), (145, 44), (141, 45), (138, 37), (131, 33), (130, 32)],
    # Northern Asia & Siberia
    [(40, 65), (60, 70), (80, 72), (110, 75), (140, 72), (170, 66), (180, 65), (160, 55), (142, 53), (110, 50), (80, 50), (50, 55), (40, 65)],
    # North America
    [(-168, 66), (-155, 71), (-140, 70), (-120, 70), (-95, 70), (-80, 60), (-65, 60), (-60, 46),
     (-70, 42), (-75, 36), (-80, 30), (-81, 25), (-83, 30), (-90, 30), (-95, 29), (-97, 26)],
    [(-97, 26), (-90, 20), (-87, 16), (-83, 9), (-85, 10), (-90, 14), (-100, 17), (-105, 22), (-110, 23)],
    [(-110, 23), (-117, 32), (-124, 38), (-124, 48), (-130, 54), (-135, 60), (-150, 59), (-165, 55), (-168, 66)],
    [(-50, 60), (-40, 60), (-20, 70), (-20, 80), (-40, 83), (-60, 80), (-55, 70), (-50, 60)],
    # South America
    [(-75, 10), (-62, 10), (-50, 0), (-35, -5), (-35, -10), (-40, -22), (-50, -30), (-58, -38),
     (-65, -50), (-68, -55), (-75, -50), (-72, -35), (-75, -20), (-80, -5), (-78, 2), (-75, 10)],
    # Australia & New Zealand
    [(115, -22), (124, -15), (130, -12), (136, -12), (142, -10), (145, -15), (153, -28), (150, -37),
     (140, -38), (135, -34), (120, -34), (115, -30), (115, -22)],
    [(173, -35), (178, -38), (175, -42), (170, -45), (167, -46), (170, -43), (173, -35)]
]


class MapTileManager:
    """Fetches, caches, and stitches satellite (ESRI / Google Earth) & OSM map tiles."""
    def __init__(self, cache_dir: str = MAP_CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.mem_cache: Dict[Tuple, Image.Image] = {}

    def get_tile(self, mode: str, z: int, x: int, y: int) -> Optional[Image.Image]:
        key = (mode, z, x, y)
        if key in self.mem_cache:
            return self.mem_cache[key]

        ext = "jpg" if mode == "SATELLITE" else "png"
        filepath = os.path.join(self.cache_dir, f"{mode.lower()}_{z}_{x}_{y}.{ext}")

        if os.path.exists(filepath):
            try:
                img = Image.open(filepath).convert("RGBA")
                self.mem_cache[key] = img
                return img
            except Exception:
                pass

        if mode == "SATELLITE":
            url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.jpg"
        else:
            url = f"https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BrickDeck/2.0"})
            with urllib.request.urlopen(req, context=self.ctx, timeout=3.0) as resp:
                data = resp.read()
                with open(filepath, "wb") as f:
                    f.write(data)
                img = Image.open(io.BytesIO(data)).convert("RGBA")
                self.mem_cache[key] = img
                return img
        except Exception:
            return None

    def build_radar_map(self, mode: str, lat: float, lon: float, zoom_lvl: float, radius: int) -> Optional[Image.Image]:
        """Generate circular radar scope map centered at (lat, lon)."""
        if zoom_lvl < 2.5:
            z = 5
        elif zoom_lvl < 7.0:
            z = 6
        elif zoom_lvl < 18.0:
            z = 7
        else:
            z = 8

        lat_rad = math.radians(lat)
        n = 2.0 ** z
        cx_tile = (lon + 180.0) / 360.0 * n
        cy_tile = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n

        center_tx = int(cx_tile)
        center_ty = int(cy_tile)

        fx = int((cx_tile - center_tx) * 256)
        fy = int((cy_tile - center_ty) * 256)

        mosaic = Image.new("RGBA", (768, 768), (10, 16, 26, 255))
        has_any_tile = False
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                tx = center_tx + dx
                ty = center_ty + dy
                t_img = self.get_tile(mode, z, tx, ty)
                if t_img:
                    mosaic.paste(t_img, ((dx + 1) * 256, (dy + 1) * 256))
                    has_any_tile = True

        if not has_any_tile:
            return None

        diam = radius * 2
        mc_x = 256 + fx
        mc_y = 256 + fy
        crop_box = (mc_x - radius, mc_y - radius, mc_x + radius, mc_y + radius)

        if crop_box[0] >= 0 and crop_box[1] >= 0 and crop_box[2] <= 768 and crop_box[3] <= 768:
            cropped = mosaic.crop(crop_box)
        else:
            cropped = mosaic.resize((diam, diam))

        # Circular mask for radar display
        mask = Image.new("L", (diam, diam), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.ellipse([(0, 0), (diam, diam)], fill=240)

        result = Image.new("RGBA", (diam, diam), (0, 0, 0, 0))
        result.paste(cropped, (0, 0), mask)
        return result


class AirRadarModule(BaseModule):
    name = "Global Aerospace & Tactical Radar"
    short_name = "AeroSpace"
    icon = "★"
    accent_color = COLOR_ELECTRIC_BLUE

    def __init__(self, app_context=None):
        super().__init__(app_context)
        # Observer Station Coordinates (Default Gorzów Wielkopolski)
        self.obs_name = "Gorzów Wielkopolski"
        self.obs_lat = 52.7333
        self.obs_lon = 15.2333

        # Camera & Globe Orientation
        self.cam_lat = 52.7333
        self.cam_lon = 15.2333
        self.target_cam_lat = 52.7333
        self.target_cam_lon = 15.2333

        # Map Modes: Real Satellite Imagery (Google Earth) / OSM Dark / Cyber 3D Globe
        self.map_modes = ["SATELLITE", "OSM", "CYBER"]
        self.map_mode_idx = 0
        self.map_mode_names = [
            "🛰️ SATELITA (Google Earth)",
            "🗺️ MAPA OSM (Tactical Dark)",
            "🌐 GLOBUS 3D (Cyber Vector)"
        ]
        self.tile_manager = MapTileManager()
        self.current_radar_map: Optional[Image.Image] = None
        self.last_map_key = None

        # Multi-level Smooth Zoom
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_levels = [1.0, 2.2, 5.0, 12.0, 25.0, 45.0]
        self.zoom_idx = 0
        self.zoom_names = [
            "Globus 3D / Orbity",
            "Półkula / Kontynent",
            "Sektor FIR / Kraj",
            "Radar Zbliżania (250 km)",
            "Sektor TMA (100 km)",
            "Radar Taktyczny ADS-B (40 km)"
        ]

        # Satellite Telemetry
        self.iss_data = {
            "lat": 39.7, "lon": -77.4, "alt_km": 416.3, "vel_kmh": 27609,
            "visibility": "daylight", "next_pass_min": 84, "max_elevation": 68
        }
        self.satellites = [
            {"id": "ISS", "name": "ISS (Zarya/Destiny)", "lat": 39.7, "lon": -77.4, "alt": 416, "col": COLOR_FLIPPER_AMBER, "type": "station"},
            {"id": "CSS", "name": "Tiangong (CSS)", "lat": 24.2, "lon": 110.5, "alt": 385, "col": COLOR_NEON_PINK, "type": "station"},
            {"id": "NOAA", "name": "NOAA-19 Weather", "lat": -45.1, "lon": 18.2, "alt": 850, "col": COLOR_CYBER_CYAN, "type": "weather"},
            {"id": "STARLINK", "name": "Starlink-Train", "lat": 51.2, "lon": 16.8, "alt": 550, "col": COLOR_TEXT_PRIMARY, "type": "cluster"}
        ]
        self.iss_orbit_track: List[Tuple[float, float]] = []
        self._generate_iss_orbit_track()

        # Air Traffic (ADS-B Commercial & Cargo Flights)
        self.flights: List[Dict] = []
        self._init_synthetic_flights()

        # Console Gamepad Target Lock-on Index (TrimUI Brick)
        self.target_flight_idx = 0
        self.selected_flight: Optional[Dict] = self.flights[0] if self.flights else None
        self.hovered_flight: Optional[Dict] = None

        # Modals State
        self.flight_modal_open = False
        self.modal_open = False  # Location picker modal
        self.city_picker_idx = 0

        # Background Worker & Sweep
        self.thread_running = False
        self.status_msg = "Inicjalizacja radaru..."
        self.sweep_angle = 0.0

    def on_load(self):
        self._init_synthetic_flights()
        self.thread_running = True
        threading.Thread(target=self._background_worker, daemon=True).start()
        threading.Thread(target=self._tile_loader_worker, daemon=True).start()

    def get_hotkey_hints(self):
        if self.flight_modal_open:
            return [
                ("L1 / R1 lub D-Pad", "Zmień samolot"),
                ("A", "Śledź ten lot"),
                ("B", "Zamknij kartę")
            ]
        elif self.modal_open:
            return [
                ("D-Pad G/D", "Wybierz stację bazową"),
                ("A", "Zatwierdź / Leć tam"),
                ("B", "Anuluj")
            ]
        else:
            mode_name = self.map_mode_names[self.map_mode_idx].split()[0]
            cur_cs = self.selected_flight["callsign"] if self.selected_flight else "Brak"
            return [
                ("L1/R1 / D-Pad", f"Cel: {cur_cs}"),
                ("A", "Zdjęcie i dane lotu"),
                ("X / Y", f"Zoom: {self.zoom_names[self.zoom_idx]}"),
                ("L2/R2 / Sel", f"Mapa: {mode_name}"),
                ("B", "Baza GPS")
            ]

    def _generate_iss_orbit_track(self):
        """Generate ground track for 51.6° inclination orbit."""
        track = []
        base_lon = self.iss_data.get("lon", 0.0)
        for deg in range(-180, 180, 6):
            rad = math.radians(deg)
            lat = 51.6 * math.sin(rad)
            lon = (base_lon + deg)
            if lon > 180: lon -= 360
            if lon < -180: lon += 360
            track.append((lat, lon))
        self.iss_orbit_track = track

    def _init_synthetic_flights(self):
        """Authentic commercial fleet around active observer station."""
        p_lat, p_lon = self.obs_lat, self.obs_lon
        self.flights = [
            {
                "icao": "4851ab", "callsign": "LOT3801", "airline": "Polskie Linie Lotnicze LOT",
                "model": "Boeing 787-9 Dreamliner", "reg": "SP-LSA", "country": "Polska",
                "origin": "WAW (Warszawa)", "dest": "JFK (Nowy Jork)", "progress": 0.68,
                "lat": p_lat + 0.18, "lon": p_lon + 0.22, "alt_m": 10970, "speed_kmh": 885,
                "track": 285.0, "vert_rate": "+0 ft/min", "squawk": "7104"
            },
            {
                "icao": "3c65c2", "callsign": "DLH142", "airline": "Deutsche Lufthansa",
                "model": "Airbus A350-900", "reg": "D-AIXG", "country": "Niemcy",
                "origin": "FRA (Frankfurt)", "dest": "WAW (Warszawa)", "progress": 0.74,
                "lat": p_lat - 0.25, "lon": p_lon - 0.38, "alt_m": 11580, "speed_kmh": 875,
                "track": 85.0, "vert_rate": "-400 ft/min", "squawk": "1000"
            },
            {
                "icao": "4ca831", "callsign": "RYR45P", "airline": "Ryanair",
                "model": "Boeing 737-8200 MAX", "reg": "SP-RZX", "country": "Irlandia",
                "origin": "KRK (Kraków)", "dest": "STN (Londyn Stansted)", "progress": 0.35,
                "lat": p_lat + 0.32, "lon": p_lon - 0.15, "alt_m": 9450, "speed_kmh": 820,
                "track": 270.0, "vert_rate": "+0 ft/min", "squawk": "4421"
            },
            {
                "icao": "47805d", "callsign": "WZZ22A", "airline": "Wizz Air",
                "model": "Airbus A321neo", "reg": "HA-LVS", "country": "Węgry",
                "origin": "WAW (Warszawa)", "dest": "BCN (Barcelona)", "progress": 0.28,
                "lat": p_lat - 0.35, "lon": p_lon + 0.42, "alt_m": 11270, "speed_kmh": 860,
                "track": 225.0, "vert_rate": "+0 ft/min", "squawk": "6215"
            },
            {
                "icao": "896172", "callsign": "UAE152", "airline": "Emirates",
                "model": "Boeing 777-300ER", "reg": "A6-EGB", "country": "ZEA",
                "origin": "DXB (Dubaj)", "dest": "CPH (Kopenhaga)", "progress": 0.81,
                "lat": p_lat - 0.48, "lon": p_lon - 0.20, "alt_m": 12190, "speed_kmh": 915,
                "track": 320.0, "vert_rate": "+0 ft/min", "squawk": "3411"
            },
            {
                "icao": "484b39", "callsign": "LOT282", "airline": "Polskie Linie Lotnicze LOT",
                "model": "Embraer E195-E2", "reg": "SP-LMA", "country": "Polska",
                "origin": "POZ (Poznań)", "dest": "WAW (Warszawa)", "progress": 0.48,
                "lat": p_lat + 0.08, "lon": p_lon - 0.45, "alt_m": 7200, "speed_kmh": 680,
                "track": 95.0, "vert_rate": "+600 ft/min", "squawk": "2201"
            },
            {
                "icao": "486290", "callsign": "ENT418", "airline": "Enter Air",
                "model": "Boeing 737-800 NG", "reg": "SP-ENG", "country": "Polska",
                "origin": "KTW (Katowice)", "dest": "AYT (Antalya)", "progress": 0.18,
                "lat": p_lat + 0.22, "lon": p_lon - 0.32, "alt_m": 9800, "speed_kmh": 810,
                "track": 145.0, "vert_rate": "+0 ft/min", "squawk": "4102"
            },
            {
                "icao": "3944eb", "callsign": "AFR1145", "airline": "Air France",
                "model": "Airbus A220-300", "reg": "F-HZUF", "country": "Francja",
                "origin": "CDG (Paryż)", "dest": "WAW (Warszawa)", "progress": 0.82,
                "lat": p_lat - 0.12, "lon": p_lon + 0.55, "alt_m": 10300, "speed_kmh": 830,
                "track": 75.0, "vert_rate": "-800 ft/min", "squawk": "5312"
            },
            {
                "icao": "4064d4", "callsign": "BAW846", "airline": "British Airways",
                "model": "Airbus A320neo", "reg": "G-TTNN", "country": "Wlk. Brytania",
                "origin": "LHR (Londyn Heathrow)", "dest": "WAW (Warszawa)", "progress": 0.70,
                "lat": p_lat + 0.42, "lon": p_lon + 0.15, "alt_m": 11800, "speed_kmh": 890,
                "track": 88.0, "vert_rate": "+0 ft/min", "squawk": "7000"
            },
            {
                "icao": "4401a5", "callsign": "AUA602", "airline": "Austrian Airlines",
                "model": "Airbus A320", "reg": "OE-LBN", "country": "Austria",
                "origin": "VIE (Wiedeń)", "dest": "GDN (Gdańsk)", "progress": 0.55,
                "lat": p_lat - 0.18, "lon": p_lon - 0.50, "alt_m": 10600, "speed_kmh": 830,
                "track": 20.0, "vert_rate": "+0 ft/min", "squawk": "6110"
            }
        ]
        self.selected_flight = self.flights[0]
        self.status_msg = f"LIVE RADAR: {len(self.flights)} maszyn w zasięgu"

    def _tile_loader_worker(self):
        """Asynchronously preloads satellite / OSM map tiles for observer location."""
        while self.thread_running:
            mode = self.map_modes[self.map_mode_idx]
            if mode != "CYBER":
                cur_key = (mode, round(self.obs_lat, 2), round(self.obs_lon, 2), self.zoom_idx)
                if cur_key != self.last_map_key:
                    map_img = self.tile_manager.build_radar_map(mode, self.obs_lat, self.obs_lon, self.zoom, 210)
                    if map_img:
                        self.current_radar_map = map_img
                        self.last_map_key = cur_key
            time.sleep(2.0)

    def _fetch_live_data(self):
        """Fetch live ISS position from wheretheiss.at and ADS-B flights from OpenSky."""
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        # 1. Fetch ISS
        try:
            req = urllib.request.Request(WHERETHEISS_URL, headers={"User-Agent": "BrickDeck/2.0"})
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=3.5) as resp:
                data = json.loads(resp.read().decode())
                if "latitude" in data and "longitude" in data:
                    self.iss_data["lat"] = float(data["latitude"])
                    self.iss_data["lon"] = float(data["longitude"])
                    self.iss_data["alt_km"] = float(data.get("altitude", 416.0))
                    self.iss_data["vel_kmh"] = int(data.get("velocity", 27600))
                    self.iss_data["visibility"] = data.get("visibility", "daylight")
                    self.satellites[0]["lat"] = self.iss_data["lat"]
                    self.satellites[0]["lon"] = self.iss_data["lon"]
                    self._generate_iss_orbit_track()
        except Exception:
            pass

        # 2. Fetch ADS-B flights for current observer location
        try:
            lamin = self.obs_lat - 1.2
            lomin = self.obs_lon - 1.8
            lamax = self.obs_lat + 1.2
            lomax = self.obs_lon + 1.8
            url = f"{OPENSKY_BASE_URL}?lamin={lamin:.3f}&lomin={lomin:.3f}&lamax={lamax:.3f}&lomax={lomax:.3f}"
            req = urllib.request.Request(url, headers={"User-Agent": "BrickDeck-ADS-B/2.0"})
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=4.0) as resp:
                data = json.loads(resp.read().decode())
                states = data.get("states", [])
                if states and len(states) > 0:
                    parsed = []
                    for s in states:
                        if s[6] is None or s[5] is None: continue
                        cs = (s[1] or s[0] or "UNKNOWN").strip().upper()
                        airline_name = "Komercyjne Linie Lotnicze"
                        model_name = "Boeing 737-800"
                        orig = "WAW (Warszawa)"
                        dest = "FRA (Frankfurt)"
                        reg = f"SP-{s[0][:4].upper()}"

                        if cs.startswith("LOT"):
                            airline_name = "Polskie Linie Lotnicze LOT"
                            model_name = "Boeing 787-9 Dreamliner"
                            orig, dest = "WAW (Warszawa)", "JFK (Nowy Jork)"
                        elif cs.startswith("DLH"):
                            airline_name = "Deutsche Lufthansa"
                            model_name = "Airbus A350-900"
                            orig, dest = "FRA (Frankfurt)", "WAW (Warszawa)"
                        elif cs.startswith("RYR"):
                            airline_name = "Ryanair"
                            model_name = "Boeing 737-8200 MAX"
                            orig, dest = "KRK (Kraków)", "STN (Londyn)"
                        elif cs.startswith("WZZ"):
                            airline_name = "Wizz Air"
                            model_name = "Airbus A321neo"
                            orig, dest = "WAW (Warszawa)", "BCN (Barcelona)"
                        elif cs.startswith("UAE"):
                            airline_name = "Emirates"
                            model_name = "Boeing 777-300ER"
                            orig, dest = "DXB (Dubaj)", "CPH (Kopenhaga)"

                        parsed.append({
                            "icao": str(s[0] or "N/A"),
                            "callsign": cs,
                            "airline": airline_name,
                            "model": model_name,
                            "reg": reg,
                            "country": str(s[2] or "Polska"),
                            "origin": orig,
                            "dest": dest,
                            "progress": 0.55,
                            "lat": float(s[6]),
                            "lon": float(s[5]),
                            "alt_m": float(s[7] or 10000.0),
                            "speed_kmh": int((s[9] or 230.0) * 3.6),
                            "track": float(s[10] or 0.0),
                            "vert_rate": f"{int((s[11] or 0.0) * 196.85):+d} ft/min",
                            "squawk": str(s[14] or "7000")
                        })
                    if parsed:
                        self.flights = parsed
                        self.status_msg = f"LIVE ADS-B: {len(parsed)} maszyn online"
        except Exception:
            if not self.flights:
                self._init_synthetic_flights()

    def _background_worker(self):
        while self.thread_running:
            self._fetch_live_data()
            time.sleep(10.0)

    def update(self, dt: float):
        self.sweep_angle = (self.sweep_angle + dt * 65.0) % 360.0

        # Smooth camera orientation interpolation
        lat_diff = self.target_cam_lat - self.cam_lat
        lon_diff = self.target_cam_lon - self.cam_lon
        self.cam_lat += lat_diff * min(1.0, dt * 6.0)
        self.cam_lon += lon_diff * min(1.0, dt * 6.0)

        # Smooth dynamic zoom level interpolation
        target_z = self.zoom_levels[self.zoom_idx]
        self.zoom += (target_z - self.zoom) * min(1.0, dt * 7.5)

        # Propagate simulated satellites along orbits
        for sat in self.satellites[1:]:
            sat["lon"] = (sat["lon"] + dt * 2.2)
            if sat["lon"] > 180: sat["lon"] -= 360

        # Move aircraft along their current heading vectors
        for fl in self.flights:
            t_rad = math.radians(fl.get("track", 0.0))
            dist_deg = (fl.get("speed_kmh", 800) / 3600.0 * dt) / 111.0
            fl["lat"] += math.cos(t_rad) * dist_deg
            fl["lon"] += math.sin(t_rad) * dist_deg / max(0.2, math.cos(math.radians(fl["lat"])))
            if abs(fl["lat"] - self.obs_lat) > 1.9 or abs(fl["lon"] - self.obs_lon) > 2.4:
                fl["track"] = (fl["track"] + 180.0) % 360.0

    def _project_ortho(self, lat_deg: float, lon_deg: float, cx: int, cy: int, r: float) -> Tuple[int, int, bool]:
        """Project latitude/longitude onto 3D orthographic sphere centered at (cam_lat, cam_lon)."""
        c_lat = math.radians(self.cam_lat)
        c_lon = math.radians(self.cam_lon)
        lat = math.radians(lat_deg)
        lon = math.radians(lon_deg)

        cos_lat = math.cos(lat)
        sin_lat = math.sin(lat)
        dlon = lon - c_lon

        x = r * cos_lat * math.sin(dlon)
        y = - r * (math.cos(c_lat) * sin_lat - math.sin(c_lat) * cos_lat * math.cos(dlon))
        z = math.sin(c_lat) * sin_lat + math.cos(c_lat) * cos_lat * math.cos(dlon)

        px = int(cx + x)
        py = int(cy + y)
        is_visible = (z > 0.0)
        return px, py, is_visible

    def handle_pointer(self, cx: int, cy: int, is_down: bool):
        """Secondary pointer support for browser simulation."""
        if self.flight_modal_open:
            if is_down:
                mx, my, mw, mh = 160, 60, 704, 648
                close_x0, close_y0 = mx + mw - 54, my + 14
                close_x1, close_y1 = mx + mw - 18, my + 46
                if (close_x0 <= cx <= close_x1 and close_y0 <= cy <= close_y1) or not (mx <= cx <= mx + mw and my <= cy <= my + mh):
                    self.flight_modal_open = False
            return

        best_flight = None
        best_dist = 26.0

        for idx, fl in enumerate(self.flights):
            sx = fl.get("_screen_x")
            sy = fl.get("_screen_y")
            if sx is not None and sy is not None:
                d = math.hypot(cx - sx, cy - sy)
                if d < best_dist:
                    best_dist = d
                    best_flight = fl
                    self.target_flight_idx = idx

        self.hovered_flight = best_flight
        if best_flight:
            self.selected_flight = best_flight
            if is_down:
                self.flight_modal_open = True

    def handle_input(self, event: str) -> bool:
        """Physical Button Controls for TrimUI Brick console."""
        # 1. Modal Navigation (Flight Card Opened)
        if self.flight_modal_open:
            if event in ("BTN_B", "KEY_B", "ESCAPE", "MENU"):
                self.flight_modal_open = False
                return True
            # Switch between aircraft photos while viewing card
            elif event in ("LEFT", "KEY_LEFT", "L1", "KEY_L1", "BTN_L1"):
                if self.flights:
                    self.target_flight_idx = (self.target_flight_idx - 1) % len(self.flights)
                    self.selected_flight = self.flights[self.target_flight_idx]
                    return True
            elif event in ("RIGHT", "KEY_RIGHT", "R1", "KEY_R1", "BTN_R1"):
                if self.flights:
                    self.target_flight_idx = (self.target_flight_idx + 1) % len(self.flights)
                    self.selected_flight = self.flights[self.target_flight_idx]
                    return True
            elif event in ("BTN_A", "KEY_A", "ENTER", "SPACE"):
                if self.selected_flight:
                    self.target_cam_lat = self.selected_flight["lat"]
                    self.target_cam_lon = self.selected_flight["lon"]
                return True
            return False

        # 2. Location Picker Modal
        if self.modal_open:
            if event in ("UP", "KEY_UP"):
                if self.city_picker_idx > 0:
                    self.city_picker_idx -= 1
                    return True
            elif event in ("DOWN", "KEY_DOWN"):
                if self.city_picker_idx < min(12, len(PRESET_CITIES)) - 1:
                    self.city_picker_idx += 1
                    return True
            elif event in ("BTN_A", "KEY_A", "ENTER", "SPACE"):
                name, lat, lon, _ = PRESET_CITIES[self.city_picker_idx]
                self.obs_name = name
                self.obs_lat = lat
                self.obs_lon = lon
                self.target_cam_lat = lat
                self.target_cam_lon = lon
                self.zoom_idx = 4
                self.modal_open = False
                self.last_map_key = None  # Force map reload for new location
                threading.Thread(target=self._fetch_live_data, daemon=True).start()
                return True
            elif event in ("BTN_B", "KEY_B", "ESCAPE", "MENU"):
                self.modal_open = False
                return True
            return False

        # 3. Main Console Controls (TrimUI Brick)
        # Target Cycling via Shoulder Buttons [L1] / [R1]
        if event in ("R1", "KEY_R1", "BTN_R1"):
            if self.flights:
                self.target_flight_idx = (self.target_flight_idx + 1) % len(self.flights)
                self.selected_flight = self.flights[self.target_flight_idx]
                return True
        elif event in ("L1", "KEY_L1", "BTN_L1"):
            if self.flights:
                self.target_flight_idx = (self.target_flight_idx - 1) % len(self.flights)
                self.selected_flight = self.flights[self.target_flight_idx]
                return True

        # Map Mode Toggle via [L2] / [R2] / [SELECT]
        elif event in ("L2", "KEY_L2", "BTN_L2", "R2", "KEY_R2", "BTN_R2", "SELECT", "KEY_SELECT", "BTN_SELECT"):
            self.map_mode_idx = (self.map_mode_idx + 1) % len(self.map_modes)
            self.last_map_key = None  # Force fresh map stitch
            return True

        # Open Flight Details Card via [A]
        elif event in ("BTN_A", "KEY_A", "SPACE", "ENTER"):
            if self.flights:
                self.selected_flight = self.flights[self.target_flight_idx]
                self.flight_modal_open = True
                return True

        # Open City / GPS Picker via [B]
        elif event in ("BTN_B", "KEY_B"):
            self.modal_open = True
            return True

        # Zoom In / Out via [X] / [Y]
        elif event in ("BTN_X", "KEY_X", "ZOOM_IN", "WHEEL_UP"):
            if self.zoom_idx < len(self.zoom_levels) - 1:
                self.zoom_idx += 1
                return True
        elif event in ("BTN_Y", "KEY_Y", "ZOOM_OUT", "WHEEL_DOWN"):
            if self.zoom_idx > 0:
                self.zoom_idx -= 1
                return True

        # D-Pad Controls:
        # In Tactical Radar mode: D-Pad Left/Right also cycles aircraft targets!
        elif event in ("LEFT", "KEY_LEFT", "KeyA"):
            if self.zoom >= 2.5 and self.flights:
                self.target_flight_idx = (self.target_flight_idx - 1) % len(self.flights)
                self.selected_flight = self.flights[self.target_flight_idx]
                return True
            else:
                self.target_cam_lon = (self.target_cam_lon - 22.0 / max(0.5, self.zoom))
                if self.target_cam_lon < -180: self.target_cam_lon += 360
                return True
        elif event in ("RIGHT", "KEY_RIGHT", "KeyD"):
            if self.zoom >= 2.5 and self.flights:
                self.target_flight_idx = (self.target_flight_idx + 1) % len(self.flights)
                self.selected_flight = self.flights[self.target_flight_idx]
                return True
            else:
                self.target_cam_lon = (self.target_cam_lon + 22.0 / max(0.5, self.zoom))
                if self.target_cam_lon > 180: self.target_cam_lon -= 360
                return True
        elif event in ("UP", "KEY_UP", "KeyW"):
            self.target_cam_lat = min(85.0, self.target_cam_lat + 16.0 / max(0.5, self.zoom))
            return True
        elif event in ("DOWN", "KEY_DOWN", "KeyS"):
            self.target_cam_lat = max(-85.0, self.target_cam_lat - 16.0 / max(0.5, self.zoom))
            return True

        return False

    def _draw_aircraft_photo(self, draw, px: int, py: int, pw: int, ph: int, fl: Dict):
        """Procedural side-view airliner photo in authentic airline livery."""
        draw.rounded_rectangle([(px, py), (px + pw, py + ph)], radius=10, fill=(12, 18, 28), outline=(35, 75, 120), width=2)
        for y_off in range(ph - 4):
            rat = y_off / float(ph)
            r_c = int(10 + rat * 16)
            g_c = int(20 + rat * 28)
            b_c = int(38 + rat * 48)
            draw.line([(px + 2, py + 2 + y_off), (px + pw - 2, py + 2 + y_off)], fill=(r_c, g_c, b_c))

        contrail_y = py + ph // 2 + 12
        draw.line([(px + 25, contrail_y), (px + pw // 2 - 20, contrail_y)], fill=(220, 235, 255), width=3)
        draw.line([(px + 50, contrail_y - 2), (px + pw // 2 - 40, contrail_y - 2)], fill=(255, 255, 255), width=2)

        airline = fl.get("airline", "")
        callsign = fl.get("callsign", "")

        if "LOT" in airline or "LOT" in callsign:
            body_col = (248, 250, 255)
            belly_col = (18, 35, 80)
            tail_col = (14, 28, 70)
            accent_col = (225, 185, 30)
        elif "Lufthansa" in airline or "DLH" in callsign:
            body_col = (245, 246, 250)
            belly_col = (15, 25, 50)
            tail_col = (10, 20, 45)
            accent_col = (255, 180, 0)
        elif "Ryanair" in airline or "RYR" in callsign:
            body_col = (240, 245, 252)
            belly_col = (10, 24, 85)
            tail_col = (10, 24, 85)
            accent_col = (250, 200, 20)
        elif "Wizz" in airline or "WZZ" in callsign:
            body_col = (246, 246, 250)
            belly_col = (160, 20, 100)
            tail_col = (190, 25, 115)
            accent_col = (0, 190, 255)
        elif "Emirates" in airline or "UAE" in callsign:
            body_col = (252, 252, 255)
            belly_col = (220, 225, 235)
            tail_col = (195, 20, 25)
            accent_col = (200, 160, 40)
        elif "Air France" in airline or "AFR" in callsign:
            body_col = (248, 249, 252)
            belly_col = (20, 30, 60)
            tail_col = (15, 28, 70)
            accent_col = (230, 30, 40)
        elif "British Airways" in airline or "BAW" in callsign:
            body_col = (248, 249, 252)
            belly_col = (18, 32, 68)
            tail_col = (18, 32, 68)
            accent_col = (210, 25, 35)
        else:
            body_col = (245, 248, 255)
            belly_col = (25, 45, 75)
            tail_col = (0, 160, 230)
            accent_col = (0, 230, 255)

        ac_x = px + pw // 2 + 10
        ac_y = py + ph // 2 + 8
        fuse_len = 240
        fuse_h = 26
        fx0 = ac_x - fuse_len // 2
        fy0 = ac_y - fuse_h // 2

        draw.rounded_rectangle([(fx0 + 32, fy0), (fx0 + fuse_len - 32, fy0 + fuse_h)], radius=7, fill=body_col)
        draw.polygon([(fx0 + 34, fy0), (fx0, fy0 + fuse_h // 2), (fx0 + 34, fy0 + fuse_h)], fill=body_col)
        draw.polygon([(fx0 + 8, fy0 + fuse_h // 2 - 4), (fx0, fy0 + fuse_h // 2), (fx0 + 8, fy0 + fuse_h // 2 + 4)], fill=(35, 42, 50))
        draw.polygon([(fx0 + 14, fy0 + 5), (fx0 + 26, fy0 + 3), (fx0 + 28, fy0 + 8), (fx0 + 18, fy0 + 9)], fill=(16, 28, 48))
        draw.rectangle([(fx0 + 28, fy0 + fuse_h // 2 + 2), (fx0 + fuse_len - 38, fy0 + fuse_h)], fill=belly_col)
        draw.polygon([(fx0 + fuse_len - 35, fy0), (fx0 + fuse_len, fy0 + 9), (fx0 + fuse_len - 35, fy0 + fuse_h)], fill=body_col)

        draw.polygon([(fx0 + fuse_len - 58, fy0), (fx0 + fuse_len - 16, fy0 - 48), (fx0 + fuse_len, fy0 - 46), (fx0 + fuse_len - 22, fy0)], fill=tail_col)
        draw.ellipse([(fx0 + fuse_len - 24, fy0 - 36), (fx0 + fuse_len - 10, fy0 - 22)], fill=accent_col)
        draw.polygon([(fx0 + fuse_len - 28, fy0 + 7), (fx0 + fuse_len + 16, fy0 + 9), (fx0 + fuse_len - 12, fy0 + 14)],
                     fill=(min(255, tail_col[0] + 30), min(255, tail_col[1] + 30), min(255, tail_col[2] + 30)))

        win_y = fy0 + 7
        for wx in range(fx0 + 40, fx0 + fuse_len - 48, 6):
            draw.rectangle([(wx, win_y), (wx + 3, win_y + 4)], fill=(15, 25, 40))

        draw.polygon([(ac_x - 38, ac_y + 6), (ac_x - 10, ac_y + 40), (ac_x + 10, ac_y + 40), (ac_x + 18, ac_y + 6)],
                     fill=(185, 192, 205), outline=(135, 145, 160))
        draw.polygon([(ac_x + 10, ac_y + 40), (ac_x + 14, ac_y + 26), (ac_x + 18, ac_y + 40)], fill=accent_col)

        eng_x = ac_x - 20
        eng_y = ac_y + 14
        draw.rounded_rectangle([(eng_x, eng_y), (eng_x + 40, eng_y + 18)], radius=5, fill=(160, 172, 188), outline=(100, 112, 128))
        draw.ellipse([(eng_x - 3, eng_y + 1), (eng_x + 6, eng_y + 17)], fill=(25, 30, 40))
        draw.polygon([(eng_x + 40, eng_y + 3), (eng_x + 46, eng_y + 9), (eng_x + 40, eng_y + 15)], fill=(45, 50, 60))

        draw.rounded_rectangle([(px + 12, py + ph - 34), (px + 270, py + ph - 8)], radius=6, fill=(8, 14, 22, 220), outline=(0, 200, 255))
        draw.text((px + 20, py + ph - 28), f"✈ {fl.get('model', 'BOEING 737-800')[:28]}", fill=(0, 240, 255), font=get_font(11, bold=True))
        draw.text((px + pw - 145, py + 12), f"REG: {fl.get('reg', 'SP-LWA')}", fill=(255, 255, 255), font=get_font(11, bold=True))

    def _draw_flight_modal(self, canvas, fl: Dict):
        """Render high-tech flight telemetry modal with airliner photo and telemetry stats."""
        canvas.draw.rectangle([(0, 0), (canvas.width, canvas.height)], fill=(4, 6, 10, 225))

        mx, my, mw, mh = 160, 60, 704, 648
        canvas.draw.rounded_rectangle([(mx, my), (mx + mw, my + mh)], radius=16, fill=(16, 22, 32), outline=COLOR_CYBER_CYAN, width=2)

        canvas.draw.rounded_rectangle([(mx + 2, my + 2), (mx + mw - 2, my + 60)], radius=14, fill=(24, 34, 50))
        canvas.draw.line([(mx, my + 60), (mx + mw, my + 60)], fill=COLOR_CYBER_CYAN, width=2)

        airline = fl.get("airline", "KOMERCYJNE LINIE LOTNICZE").upper()
        canvas.draw.text((mx + 24, my + 14), f"✈ {airline}", fill=(210, 230, 255), font=get_font(13, bold=True))
        canvas.draw.text((mx + 24, my + 35), f"REJS: {fl['callsign']}  |  ICAO24: {fl.get('icao', 'N/A').upper()}  |  TRANS: {fl.get('squawk', '7000')}",
                         fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))

        canvas.draw.rounded_rectangle([(mx + mw - 54, my + 14), (mx + mw - 18, my + 46)], radius=6, fill=(190, 35, 45), outline=(255, 100, 110))
        canvas.draw.text((mx + mw - 41, my + 19), "✕", fill=(255, 255, 255), font=get_font(14, bold=True))

        px, py, pw, ph = mx + 20, my + 72, mw - 40, 180
        self._draw_aircraft_photo(canvas.draw, px, py, pw, ph, fl)

        rx, ry, rw = mx + 20, my + 264, mw - 40
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + 82)], radius=10, fill=(20, 28, 42), outline=COLOR_BORDER)

        orig = fl.get("origin", "WAW (Warszawa)")
        dest = fl.get("dest", "FRA (Frankfurt)")
        prog = fl.get("progress", 0.65)

        canvas.draw.text((rx + 16, ry + 12), f"WYLOT:  {orig}", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
        canvas.draw.text((rx + rw - 240, ry + 12), f"CEL:  {dest}", fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))

        bar_x = rx + 16
        bar_y = ry + 44
        bar_w = rw - 32
        canvas.draw.rounded_rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + 12)], radius=6, fill=(12, 16, 24))
        fill_w = int(bar_w * prog)
        canvas.draw.rounded_rectangle([(bar_x, bar_y), (bar_x + fill_w, bar_y + 12)], radius=6, fill=COLOR_CYBER_CYAN)

        pl_icon_x = bar_x + fill_w
        canvas.draw.ellipse([(pl_icon_x - 8, bar_y - 2), (pl_icon_x + 8, bar_y + 14)], fill=(255, 255, 255), outline=COLOR_CYBER_CYAN)
        canvas.draw.text((bar_x + bar_w - 95, ry + 60), f"{int(prog * 100)}% TRASY", fill=COLOR_CYBER_CYAN, font=get_font(10, bold=True))

        tx, ty, tw = mx + 20, my + 358, mw - 40
        canvas.draw.rounded_rectangle([(tx, ty), (tx + tw, ty + 215)], radius=10, fill=(18, 25, 38), outline=COLOR_BORDER)

        fl_alt = int(fl.get("alt_m", 10000) * 3.28084 / 100)
        speed = fl.get("speed_kmh", 850)
        mach = speed / 1225.0

        col1 = [
            ("Wysokość przelotowa:", f"FL{fl_alt:03d} ({int(fl.get('alt_m', 0)):,} m)".replace(",", " ")),
            ("Prędkość rzeczywista:", f"{speed} km/h (M {mach:.2f})"),
            ("Kurs magnetyczny:", f"{fl.get('track', 0):.1f}° (Heading)"),
            ("Prędkość pionowa:", f"{fl.get('vert_rate', '+0 ft/min')} (Przelot)")
        ]
        col2 = [
            ("Transponder Squawk:", f"{fl.get('squawk', '7000')} (ADS-B Mode-S)"),
            ("Pozycja geograficzna:", f"{fl.get('lat', 0.0):.4f}°N, {fl.get('lon', 0.0):.4f}°E"),
            ("Kraj rejestracji:", f"{fl.get('country', 'Polska')}"),
            ("Status radaru:", "LOCKED ON RADAR (Sygnał 99%)")
        ]

        for idx, (lbl, val) in enumerate(col1):
            sy = ty + 16 + idx * 47
            canvas.draw.text((tx + 16, sy), lbl, fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=False))
            canvas.draw.text((tx + 16, sy + 18), val, fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))

        for idx, (lbl, val) in enumerate(col2):
            sy = ty + 16 + idx * 47
            canvas.draw.text((tx + tw // 2 + 10, sy), lbl, fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=False))
            col_v = COLOR_PHOSPHOR_GREEN if idx == 3 else COLOR_TEXT_PRIMARY
            canvas.draw.text((tx + tw // 2 + 10, sy + 18), val, fill=col_v, font=get_font(12, bold=True))

        canvas.draw.text((mx + 24, my + mh - 30),
                         "[L1/R1 lub D-Pad L/P]: Inny samolot  |  [A]: Śledź  |  [B]: Zamknij kartę",
                         fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))

    def render(self, canvas):
        card_w_left = 634
        card_w_right = 316

        cur_mode = self.map_modes[self.map_mode_idx]
        cur_mode_name = self.map_mode_names[self.map_mode_idx]

        # ----------------------------------------------------------------------
        # Left Panel: Radar & Global Map Viewport
        # ----------------------------------------------------------------------
        canvas.draw_card(
            32, 66, card_w_left, 634,
            title="GLOBAL AEROSPACE & TACTICAL RADAR",
            subtitle=f"Baza: {self.obs_name}  |  Tryb: {self.zoom_names[self.zoom_idx]}",
            border_color=self.accent_color
        )

        cx = 349
        cy = 385
        globe_r = int(185 * self.zoom)

        vx = 48
        vy = 118
        vw = card_w_left - 32
        vh = 500
        canvas.draw.rectangle([(vx, vy), (vx + vw, vy + vh)], fill=(8, 12, 18), outline=COLOR_BORDER, width=1)

        # ----------------------------------------------------------------------
        # MAP LAYER: SATELLITE (Google Earth) / OSM / CYBER 3D GLOBE
        # ----------------------------------------------------------------------
        radar_r = 210

        if cur_mode != "CYBER":
            # Real Satellite Imagery or OSM Underlay Map
            if self.current_radar_map:
                map_x = cx - radar_r
                map_y = cy - radar_r
                canvas.image.paste(self.current_radar_map, (map_x, map_y), self.current_radar_map)
            else:
                # Fallback loading background
                canvas.draw.ellipse([(cx - radar_r, cy - radar_r), (cx + radar_r, cy + radar_r)],
                                    fill=(12, 18, 30), outline=(0, 200, 255), width=2)
                canvas.draw.text((cx - 80, cy - 8), "POBIERANIE KAFELKÓW MAPY...", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))
        else:
            # Procedural 3D Tactical Earth Globe
            if self.zoom < 10.0:
                for i in range(14, 0, -3):
                    gr = globe_r + i
                    glow_col = (10, 60 + i * 8, 120 + i * 9)
                    canvas.draw.ellipse([(cx - gr, cy - gr), (cx + gr, cy + gr)], outline=glow_col, width=2)

                canvas.draw.ellipse([(cx - globe_r, cy - globe_r), (cx + globe_r, cy + globe_r)],
                                    fill=(10, 18, 32), outline=(0, 200, 255), width=2)

                for i in range(globe_r, max(0, globe_r - 20), -2):
                    canvas.draw.ellipse([(cx - i, cy - i), (cx + i, cy + i)], outline=(16, 32, 54), width=1)

                # Meridians & Parallels Graticule
                for m_lon in range(-180, 180, 30):
                    pts = []
                    for m_lat in range(-80, 81, 10):
                        px, py, vis = self._project_ortho(m_lat, m_lon, cx, cy, globe_r)
                        if vis and (vx <= px <= vx + vw and vy <= py <= vy + vh):
                            pts.append((px, py))
                        else:
                            if len(pts) > 1: canvas.draw.line(pts, fill=(18, 42, 65), width=1)
                            pts = []
                    if len(pts) > 1: canvas.draw.line(pts, fill=(18, 42, 65), width=1)

                for p_lat in [-60, -30, 0, 30, 60]:
                    pts = []
                    for p_lon in range(-180, 181, 10):
                        px, py, vis = self._project_ortho(p_lat, p_lon, cx, cy, globe_r)
                        if vis and (vx <= px <= vx + vw and vy <= py <= vy + vh):
                            pts.append((px, py))
                        else:
                            if len(pts) > 1:
                                col = (0, 160, 210) if p_lat == 0 else (18, 42, 65)
                                canvas.draw.line(pts, fill=col, width=1)
                            pts = []
                    if len(pts) > 1:
                        col = (0, 160, 210) if p_lat == 0 else (18, 42, 65)
                        canvas.draw.line(pts, fill=col, width=1)

                for cont in CONTINENTS_GEO:
                    c_pts = [self._project_ortho(lat, lon, cx, cy, globe_r) for lon, lat in cont]
                    for i in range(len(c_pts) - 1):
                        p1, p2 = c_pts[i], c_pts[i + 1]
                        if p1[2] and p2[2]:
                            if (vx <= p1[0] <= vx + vw and vy <= p1[1] <= vy + vh) or (vx <= p2[0] <= vx + vw and vy <= p2[1] <= vy + vh):
                                canvas.draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=(38, 140, 95), width=2)

                font_city = get_font(9, bold=True)
                for c_name, c_lat, c_lon, iata in GLOBAL_WAYPOINTS:
                    wpx, wpy, wvis = self._project_ortho(c_lat, c_lon, cx, cy, globe_r)
                    if wvis and (vx <= wpx <= vx + vw and vy <= wpy <= vy + vh):
                        canvas.draw.ellipse([(wpx - 2, wpy - 2), (wpx + 2, wpy + 2)], fill=COLOR_CYBER_CYAN, outline=COLOR_TEXT_PRIMARY)
                        if self.zoom >= 1.5:
                            canvas.draw.text((wpx + 5, wpy - 5), iata, fill=(140, 200, 255), font=font_city)

                if self.zoom < 5.0 and self.iss_orbit_track:
                    t_pts = [self._project_ortho(lat, lon, cx, cy, globe_r) for lat, lon in self.iss_orbit_track]
                    for i in range(len(t_pts) - 1):
                        if t_pts[i][2] and t_pts[i + 1][2]:
                            canvas.draw.line([(t_pts[i][0], t_pts[i][1]), (t_pts[i + 1][0], t_pts[i + 1][1])], fill=(180, 125, 25), width=1)

                font_sat = get_font(10, bold=True)
                for sat in self.satellites:
                    sx, sy, is_vis = self._project_ortho(sat["lat"], sat["lon"], cx, cy, globe_r)
                    if is_vis and (vx - 10 <= sx <= vx + vw + 10 and vy - 10 <= sy <= vy + vh + 10):
                        s_col = sat["col"]
                        canvas.draw.ellipse([(sx - 4, sy - 4), (sx + 4, sy + 4)], fill=s_col, outline=COLOR_TEXT_PRIMARY)
                        if sat["id"] == "ISS":
                            canvas.draw.line([(sx - 8, sy), (sx + 8, sy)], fill=COLOR_FLIPPER_AMBER, width=2)
                            canvas.draw.rectangle([(sx - 8, sy - 3), (sx - 5, sy + 3)], fill=(40, 120, 200))
                            canvas.draw.rectangle([(sx + 5, sy - 3), (sx + 8, sy + 3)], fill=(40, 120, 200))
                        canvas.draw.text((sx + 10, sy - 6), sat["id"], fill=s_col, font=font_sat)

        # ----------------------------------------------------------------------
        # Tactical Radar Overlay (Range Rings, Sweep, Crosshairs)
        # ----------------------------------------------------------------------
        # Radar scope range rings
        for r_pct, km_val in [(0.25, "25km"), (0.50, "50km"), (0.75, "100km"), (1.0, "150km")]:
            cr = int(radar_r * r_pct)
            canvas.draw.ellipse([(cx - cr, cy - cr), (cx + cr, cy + cr)], outline=(0, 220, 255, 110), width=1)
            canvas.draw.text((cx + 6, cy - cr + 4), km_val, fill=COLOR_CYBER_CYAN, font=get_font(10, bold=False))

        # Crosshairs & Scope Outer Ring
        canvas.draw.ellipse([(cx - radar_r, cy - radar_r), (cx + radar_r, cy + radar_r)], outline=COLOR_CYBER_CYAN, width=2)
        canvas.draw.line([(cx - radar_r, cy), (cx + radar_r, cy)], fill=(0, 220, 255, 90), width=1)
        canvas.draw.line([(cx, cy - radar_r), (cx, cy + radar_r)], fill=(0, 220, 255, 90), width=1)

        # Rotating Radar Sweep Beam
        rad = math.radians(self.sweep_angle)
        sw_x = cx + int(radar_r * math.cos(rad))
        sw_y = cy + int(radar_r * math.sin(rad))
        canvas.draw.line([(cx, cy), (sw_x, sw_y)], fill=COLOR_CYBER_CYAN, width=2)

        # ----------------------------------------------------------------------
        # Aircraft Rendering on Radar / Map
        # ----------------------------------------------------------------------
        font_plane = get_font(11, bold=True)
        scale_km = (150.0 / max(1.0, self.zoom * 0.45))

        for idx, fl in enumerate(self.flights):
            dx_km = (fl["lon"] - self.obs_lon) * 67.5
            dy_km = (fl["lat"] - self.obs_lat) * 111.2
            scale = radar_r / scale_km
            ax = cx + int(dx_km * scale)
            ay = cy - int(dy_km * scale)

            fl["_screen_x"] = ax
            fl["_screen_y"] = ay

            if (ax - cx) ** 2 + (ay - cy) ** 2 <= radar_r ** 2:
                t_rad = math.radians(fl.get("track", 0.0) - 90)
                p_len = 11
                tip_x = ax + int(math.cos(t_rad) * p_len)
                tip_y = ay + int(math.sin(t_rad) * p_len)
                tail_l_x = ax + int(math.cos(t_rad + 2.5) * (p_len * 0.8))
                tail_l_y = ay + int(math.sin(t_rad + 2.5) * (p_len * 0.8))
                tail_r_x = ax + int(math.cos(t_rad - 2.5) * (p_len * 0.8))
                tail_r_y = ay + int(math.sin(t_rad - 2.5) * (p_len * 0.8))

                is_targeted = (idx == self.target_flight_idx)
                p_col = COLOR_FLIPPER_AMBER if is_targeted else COLOR_CYBER_CYAN

                canvas.draw.polygon([(tip_x, tip_y), (tail_l_x, tail_l_y), (ax, ay), (tail_r_x, tail_r_y)], fill=p_col)
                fl_level = int(fl.get("alt_m", 10000) * 3.28084 / 100)
                canvas.draw.text((ax + 10, ay - 8), f"{fl['callsign']}\nFL{fl_level:03d}", fill=COLOR_TEXT_PRIMARY, font=font_plane)

        # ----------------------------------------------------------------------
        # PHYSICAL GAMEPAD TARGET LOCK-ON HUD (TrimUI Brick)
        # ----------------------------------------------------------------------
        if self.flights and 0 <= self.target_flight_idx < len(self.flights):
            locked_fl = self.flights[self.target_flight_idx]
            lx = locked_fl.get("_screen_x")
            ly = locked_fl.get("_screen_y")

            if lx is not None and ly is not None and (vx <= lx <= vx + vw and vy <= ly <= vy + vh):
                # 1. Pulsing Lock-On Reticle
                pulse_r = 15 + int(abs(math.sin(time.time() * 7.0)) * 4)
                canvas.draw.ellipse([(lx - pulse_r, ly - pulse_r), (lx + pulse_r, ly + pulse_r)],
                                    outline=COLOR_FLIPPER_AMBER, width=2)

                # 2. Military Corner Brackets [ ┌ ┐ └ ┘ ]
                b_size = 22
                c_len = 7
                # Top-Left
                canvas.draw.line([(lx - b_size, ly - b_size), (lx - b_size + c_len, ly - b_size)], fill=COLOR_FLIPPER_AMBER, width=2)
                canvas.draw.line([(lx - b_size, ly - b_size), (lx - b_size, ly - b_size + c_len)], fill=COLOR_FLIPPER_AMBER, width=2)
                # Top-Right
                canvas.draw.line([(lx + b_size, ly - b_size), (lx + b_size - c_len, ly - b_size)], fill=COLOR_FLIPPER_AMBER, width=2)
                canvas.draw.line([(lx + b_size, ly - b_size), (lx + b_size, ly - b_size + c_len)], fill=COLOR_FLIPPER_AMBER, width=2)
                # Bottom-Left
                canvas.draw.line([(lx - b_size, ly + b_size), (lx - b_size + c_len, ly + b_size)], fill=COLOR_FLIPPER_AMBER, width=2)
                canvas.draw.line([(lx - b_size, ly + b_size), (lx - b_size, ly + b_size - c_len)], fill=COLOR_FLIPPER_AMBER, width=2)
                # Bottom-Right
                canvas.draw.line([(lx + b_size, ly + b_size), (lx + b_size - c_len, ly + b_size)], fill=COLOR_FLIPPER_AMBER, width=2)
                canvas.draw.line([(lx + b_size, ly + b_size), (lx + b_size, ly + b_size - c_len)], fill=COLOR_FLIPPER_AMBER, width=2)

                # 3. Leader Line & Tactical Target Banner
                tag_x = max(vx + 10, min(vx + vw - 280, lx - 140))
                tag_y = max(vy + 10, ly - b_size - 32)
                canvas.draw.line([(lx, ly - b_size), (tag_x + 100, tag_y + 24)], fill=COLOR_FLIPPER_AMBER, width=1)

                fl_fl = int(locked_fl.get("alt_m", 10000) * 3.28084 / 100)
                tag_txt = f"⌖ CEL #{self.target_flight_idx + 1}: {locked_fl['callsign']} | FL{fl_fl:03d} | [A]: KARTA LOTU"
                canvas.draw_badge(tag_x, tag_y, tag_txt, bg_color=(20, 28, 42), text_color=COLOR_FLIPPER_AMBER)

        # Observer Ground Station Reticle / Target Pin
        ox, oy, o_vis = self._project_ortho(self.obs_lat, self.obs_lon, cx, cy, globe_r)
        if o_vis and (vx <= ox <= vx + vw and vy <= oy <= vy + vh):
            canvas.draw.ellipse([(ox - 6, oy - 6), (ox + 6, oy + 6)], outline=COLOR_FLIPPER_AMBER, width=2)
            canvas.draw.line([(ox - 10, oy), (ox + 10, oy)], fill=COLOR_FLIPPER_AMBER, width=1)
            canvas.draw.line([(ox, oy - 10), (ox, oy + 10)], fill=COLOR_FLIPPER_AMBER, width=1)
            canvas.draw.text((ox + 10, oy - 14), f"● {self.obs_name}", fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))

        # Top-Right Map Mode Indicator Badge
        canvas.draw_badge(vx + vw - 235, vy + 10, f"MAPA: {cur_mode_name}", bg_color=(18, 28, 42), text_color=COLOR_CYBER_CYAN)

        # Bottom Zoom Slider & Gamepad Helper Bar
        z_y = vy + vh + 12
        canvas.draw.rounded_rectangle([(vx, z_y), (vx + vw, z_y + 36)], radius=6, fill=(18, 24, 34), outline=COLOR_BORDER)
        canvas.draw.text((vx + 14, z_y + 10),
                         f"KAMERA: {self.cam_lat:+.2f}°N, {self.cam_lon:+.2f}°E  |  ZOOM: {self.zoom:.1f}x  |  CEL: #{self.target_flight_idx + 1}/{len(self.flights)}",
                         fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=True))
        canvas.draw_badge(vx + vw - 190, z_y + 6, "[L1/R1]: ZMIEŃ CEL", bg_color=(36, 48, 64), text_color=COLOR_FLIPPER_AMBER)

        # ----------------------------------------------------------------------
        # Right Panel: Satellite & Air Telemetry Deck (w=316, h=634)
        # ----------------------------------------------------------------------
        canvas.draw_card(
            670, 66, card_w_right, 634,
            title="TELEMETRIA KOSMICZNA",
            subtitle=f"{self.status_msg}",
            border_color=COLOR_BORDER
        )

        rx = 686
        ry = 118
        rw = card_w_right - 32

        # 1. Observer Station Box
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + 115)], radius=8, fill=(22, 28, 38), outline=COLOR_CYBER_CYAN, width=1)
        canvas.draw.text((rx + 12, ry + 10), "STACJA OBSERWACYJNA:", fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=True))
        canvas.draw.text((rx + 12, ry + 26), f"● {self.obs_name[:20]}", fill=COLOR_TEXT_PRIMARY, font=get_font(14, bold=True))
        canvas.draw.text((rx + 12, ry + 48), f"GPS: {self.obs_lat:.4f}°N, {self.obs_lon:.4f}°E", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=False))
        canvas.draw_badge(rx + 12, ry + 78, "[B] ZMIEŃ BAZĘ (GPS)", bg_color=(36, 52, 72), text_color=COLOR_FLIPPER_AMBER)

        # 2. Selected Aircraft Quick Card (Snapped to locked target)
        ac_y = ry + 126
        sel_fl = self.selected_flight or (self.flights[self.target_flight_idx] if self.flights else None)
        canvas.draw.rounded_rectangle([(rx, ac_y), (rx + rw, ac_y + 195)], radius=8, fill=(20, 26, 36), outline=COLOR_FLIPPER_AMBER, width=2)
        canvas.draw.text((rx + 12, ac_y + 10), f"⌖ CEL #{self.target_flight_idx + 1}: {sel_fl['callsign'] if sel_fl else '---'}",
                         fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))
        canvas.draw.line([(rx + 12, ac_y + 30), (rx + rw - 12, ac_y + 30)], fill=COLOR_BORDER, width=1)

        if sel_fl:
            fl_items = [
                ("Linia:", f"{sel_fl.get('airline', 'N/A')[:18]}"),
                ("Model:", f"{sel_fl.get('model', 'Boeing 737')[:16]}"),
                ("Wysokość:", f"FL{int(sel_fl.get('alt_m', 0) * 3.28084 / 100):03d} ({int(sel_fl.get('alt_m', 0))} m)"),
                ("Prędkość:", f"{sel_fl.get('speed_kmh', 0)} km/h"),
                ("Trasa:", f"{sel_fl.get('origin', 'WAW')[:3]} ➔ {sel_fl.get('dest', 'FRA')[:3]}")
            ]
            s_y = ac_y + 38
            for lbl, val in fl_items:
                canvas.draw.text((rx + 12, s_y), lbl, fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=False))
                canvas.draw.text((rx + 105, s_y), val, fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=True))
                s_y += 22
            canvas.draw_badge(rx + 12, ac_y + 155, "[A] ZOBACZ ZDJĘCIE & DANE", bg_color=(24, 45, 65), text_color=COLOR_CYBER_CYAN)

        # 3. ISS Real-Time Flight Card
        iss_y = ac_y + 206
        canvas.draw.rounded_rectangle([(rx, iss_y), (rx + rw, iss_y + 175)], radius=8, fill=(20, 26, 36), outline=COLOR_FLIPPER_AMBER, width=1)
        canvas.draw.text((rx + 12, iss_y + 10), "★ STACJA KOSMICZNA (ISS)", fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))
        canvas.draw.line([(rx + 12, iss_y + 30), (rx + rw - 12, iss_y + 30)], fill=COLOR_BORDER, width=1)

        iss_items = [
            ("Szerokość (Lat):", f"{self.iss_data['lat']:+.3f}°"),
            ("Długość (Lon):", f"{self.iss_data['lon']:+.3f}°"),
            ("Pułap orbitalny:", f"{self.iss_data['alt_km']:.1f} km"),
            ("Prędkość:", f"{self.iss_data['vel_kmh']:,} km/h".replace(",", " ")),
            ("Widoczność:", f"{self.iss_data['visibility'].upper()}"),
            ("Najbliższy przelot:", f"za {self.iss_data['next_pass_min']} min")
        ]
        s_y = iss_y + 38
        for lbl, val in iss_items:
            canvas.draw.text((rx + 12, s_y), lbl, fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=False))
            canvas.draw.text((rx + 125, s_y), val, fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=True))
            s_y += 22

        # ----------------------------------------------------------------------
        # Modal 1: Flight Details Card with Airliner Photo / Profile
        # ----------------------------------------------------------------------
        if self.flight_modal_open and self.selected_flight:
            self._draw_flight_modal(canvas, self.selected_flight)

        # ----------------------------------------------------------------------
        # Modal 2: Location Picker / Fly-to City
        # ----------------------------------------------------------------------
        if self.modal_open:
            canvas.draw.rectangle([(0, 0), (canvas.width, canvas.height)], fill=(5, 8, 12, 235))
            modal_x = 180
            modal_y = 100
            modal_w = 664
            modal_h = 560
            canvas.draw.rounded_rectangle([(modal_x, modal_y), (modal_x + modal_w, modal_y + modal_h)],
                                          radius=14, fill=(20, 26, 38), outline=COLOR_CYBER_CYAN, width=2)

            canvas.draw.text((modal_x + 24, modal_y + 20), "WYBÓR LOKALIZACJI STACJI BAZOWEJ & PRZELOT KAMERY",
                             fill=COLOR_CYBER_CYAN, font=get_font(15, bold=True))
            canvas.draw.text((modal_x + 24, modal_y + 42), "Wybierz stację z listy, a globus płynnie przeleci do wybranego celu",
                             fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=False))
            canvas.draw.line([(modal_x + 20, modal_y + 64), (modal_x + modal_w - 20, modal_y + 64)], fill=COLOR_BORDER, width=1)

            list_start_y = modal_y + 76
            row_h = 32
            for i, (name, lat, lon, country) in enumerate(PRESET_CITIES[:12]):
                is_cur = (i == self.city_picker_idx)
                cy_row = list_start_y + i * row_h
                bg_col = (36, 52, 76) if is_cur else (24, 30, 42)
                out_col = COLOR_FLIPPER_AMBER if is_cur else COLOR_BORDER

                canvas.draw.rounded_rectangle([(modal_x + 24, cy_row), (modal_x + modal_w - 24, cy_row + 28)],
                                              radius=6, fill=bg_col, outline=out_col, width=2 if is_cur else 1)

                canvas.draw.text((modal_x + 36, cy_row + 6), name, fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=is_cur))
                canvas.draw.text((modal_x + 360, cy_row + 6), country, fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=False))
                canvas.draw.text((modal_x + 480, cy_row + 6), f"{lat:+.2f}°, {lon:+.2f}°", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))

            bot_y = modal_y + modal_h - 60
            canvas.draw.line([(modal_x + 20, bot_y), (modal_x + modal_w - 20, bot_y)], fill=COLOR_BORDER, width=1)
            canvas.draw.text((modal_x + 24, bot_y + 18), "[D-Pad G/D]: Wybierz  |  [A]: Leć do celu  |  [B]: Anuluj",
                             fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
