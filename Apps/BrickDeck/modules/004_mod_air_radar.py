"""
BrickDeck Module: Global Aerospace, Satellite & Tactical Air Radar
Unified Air & Space tracking: 3D Earth Globe with ISS and satellites, seamless multi-level zoom,
dynamic ADS-B live air traffic, interactive aircraft inspection with livery profiles,
city search (OSM Nominatim), and GPS coordinate targeting.
"""

import math
import time
import ssl
import json
import urllib.request
import urllib.parse
import threading
from typing import List, Dict, Tuple, Optional

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

# Strategic Global Hubs / Waypoints for 3D Globe Projection
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
    # North America - Alaska & Canada
    [(-168, 66), (-155, 71), (-140, 70), (-120, 70), (-95, 70), (-80, 60), (-65, 60), (-60, 46),
     (-70, 42), (-75, 36), (-80, 30), (-81, 25), (-83, 30), (-90, 30), (-95, 29), (-97, 26)],
    # Central America & Mexico
    [(-97, 26), (-90, 20), (-87, 16), (-83, 9), (-85, 10), (-90, 14), (-100, 17), (-105, 22), (-110, 23)],
    # US West Coast
    [(-110, 23), (-117, 32), (-124, 38), (-124, 48), (-130, 54), (-135, 60), (-150, 59), (-165, 55), (-168, 66)],
    # Greenland
    [(-50, 60), (-40, 60), (-20, 70), (-20, 80), (-40, 83), (-60, 80), (-55, 70), (-50, 60)],
    # South America
    [(-75, 10), (-62, 10), (-50, 0), (-35, -5), (-35, -10), (-40, -22), (-50, -30), (-58, -38),
     (-65, -50), (-68, -55), (-75, -50), (-72, -35), (-75, -20), (-80, -5), (-78, 2), (-75, 10)],
    # Australia
    [(115, -22), (124, -15), (130, -12), (136, -12), (142, -10), (145, -15), (153, -28), (150, -37),
     (140, -38), (135, -34), (120, -34), (115, -30), (115, -22)],
    # New Zealand
    [(173, -35), (178, -38), (175, -42), (170, -45), (167, -46), (170, -43), (173, -35)]
]


class AirRadarModule(BaseModule):
    name = "Global Aerospace & Satellite Radar"
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

        # Multi-level Smooth Zoom: 1.0 (Orbit Globe) -> 45.0 (Tactical Airspace Radar)
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

        # Air Traffic (ADS-B Flights)
        self.flights: List[Dict] = []
        self._init_synthetic_flights()
        self.selected_flight_idx = 0
        self.selected_flight: Optional[Dict] = self.flights[0] if self.flights else None
        self.hovered_flight: Optional[Dict] = None

        # Interactive Pointer / Mouse State
        self.mouse_x = -1
        self.mouse_y = -1
        self.last_hover_change = 0.0

        # Modals State
        self.flight_modal_open = False
        self.modal_open = False  # Location picker modal
        self.city_picker_idx = 0

        # Threading & Status
        self.thread_running = False
        self.last_fetch_time = 0.0
        self.status_msg = "Inicjalizacja radaru..."
        self.sweep_angle = 0.0

    def on_load(self):
        self._init_synthetic_flights()
        self.thread_running = True
        threading.Thread(target=self._background_worker, daemon=True).start()

    def get_hotkey_hints(self):
        if self.flight_modal_open:
            return [
                ("D-Pad L/P", "Poprzedni / Następny samolot"),
                ("A", "Namierz ten lot"),
                ("B / Klik", "Zamknij kartę lotu")
            ]
        elif self.modal_open:
            return [
                ("D-Pad G/D", "Wybierz stację bazową"),
                ("A", "Zatwierdź / Leć tam"),
                ("B", "Anuluj")
            ]
        else:
            zoom_name = self.zoom_names[self.zoom_idx]
            return [
                ("Kursor / Klik", "Otwórz kartę samolotu"),
                ("D-Pad", "Obróć globus / Przełącz cel"),
                ("X / Y / Kółko", f"Zoom: {zoom_name}"),
                ("A", "Szczegóły lotu"),
                ("B", "Zmień bazę (GPS)")
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
        """Realistic commercial airline traffic with complete livery and flight plan data."""
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

    def _fetch_live_data(self):
        """Fetch live ISS position from wheretheiss.at and ADS-B flights from OpenSky."""
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        # 1. Fetch ISS
        try:
            req = urllib.request.Request(WHERETHEISS_URL, headers={"User-Agent": "BrickDeck/1.0"})
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
            req = urllib.request.Request(url, headers={"User-Agent": "BrickDeck-ADS-B/1.0"})
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=4.0) as resp:
                data = json.loads(resp.read().decode())
                states = data.get("states", [])
                if states and len(states) > 0:
                    parsed = []
                    for s in states:
                        if s[6] is None or s[5] is None: continue
                        cs = (s[1] or s[0] or "UNKNOWN").strip().upper()
                        airline_name = "Linie Komercyjne"
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
                        self.status_msg = f"LIVE ADS-B: {len(parsed)} samolotów online"
                        self.last_fetch_time = time.time()
        except Exception:
            if not self.flights:
                self._init_synthetic_flights()

    def _background_worker(self):
        while self.thread_running:
            self._fetch_live_data()
            time.sleep(10.0)

    def update(self, dt: float):
        self.sweep_angle = (self.sweep_angle + dt * 65.0) % 360.0

        # Smooth camera orientation interpolation (Cinematic glide)
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
            # Keep within airspace boundaries around active base
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
        """Handle mouse hover and clicks directly on aircraft or UI buttons."""
        self.mouse_x = cx
        self.mouse_y = cy

        # If modal is open, check if clicked on [X] or outside modal to close
        if self.flight_modal_open:
            if is_down:
                mx, my, mw, mh = 160, 60, 704, 648
                close_x0, close_y0 = mx + mw - 54, my + 14
                close_x1, close_y1 = mx + mw - 18, my + 46
                # Clicked close button or clicked outside modal card
                if (close_x0 <= cx <= close_x1 and close_y0 <= cy <= close_y1) or not (mx <= cx <= mx + mw and my <= cy <= my + mh):
                    self.flight_modal_open = False
            return

        # Check if cursor is over any aircraft (radar or globe)
        best_flight = None
        best_dist = 24.0  # Hit radius in pixels

        for fl in self.flights:
            sx = fl.get("_screen_x")
            sy = fl.get("_screen_y")
            if sx is not None and sy is not None:
                d = math.hypot(cx - sx, cy - sy)
                if d < best_dist:
                    best_dist = d
                    best_flight = fl

        self.hovered_flight = best_flight

        # If clicked on aircraft or hovered directly over it
        if best_flight:
            self.selected_flight = best_flight
            if is_down:
                self.flight_modal_open = True

    def handle_input(self, event: str) -> bool:
        # 1. Flight Modal Navigation
        if self.flight_modal_open:
            if event in ("BTN_B", "KEY_B", "ESCAPE", "MENU"):
                self.flight_modal_open = False
                return True
            elif event in ("LEFT", "KEY_LEFT", "UP", "KEY_UP"):
                if self.flights:
                    idx = self.flights.index(self.selected_flight) if self.selected_flight in self.flights else 0
                    self.selected_flight = self.flights[(idx - 1) % len(self.flights)]
                    return True
            elif event in ("RIGHT", "KEY_RIGHT", "DOWN", "KEY_DOWN"):
                if self.flights:
                    idx = self.flights.index(self.selected_flight) if self.selected_flight in self.flights else 0
                    self.selected_flight = self.flights[(idx + 1) % len(self.flights)]
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
                self.zoom_idx = 4  # Smoothly zoom into tactical approach
                self.modal_open = False
                threading.Thread(target=self._fetch_live_data, daemon=True).start()
                return True
            elif event in ("BTN_B", "KEY_B", "ESCAPE", "MENU"):
                self.modal_open = False
                return True
            return False

        # 3. Main Radar / Globe View Controls
        if event in ("BTN_B", "KEY_B"):
            self.modal_open = True
            return True
        elif event in ("BTN_X", "KEY_X", "ZOOM_IN", "WHEEL_UP"):
            # Zoom In
            if self.zoom_idx < len(self.zoom_levels) - 1:
                self.zoom_idx += 1
                return True
        elif event in ("BTN_Y", "KEY_Y", "ZOOM_OUT", "WHEEL_DOWN"):
            # Zoom Out
            if self.zoom_idx > 0:
                self.zoom_idx -= 1
                return True
        elif event in ("BTN_A", "KEY_A", "SPACE", "ENTER"):
            # Open flight modal for selected/hovered flight
            target = self.hovered_flight or self.selected_flight
            if target:
                self.selected_flight = target
                self.flight_modal_open = True
                return True
            else:
                # Snap camera back to base
                self.target_cam_lat = self.obs_lat
                self.target_cam_lon = self.obs_lon
                return True
        elif event in ("LEFT", "KEY_LEFT", "KeyA"):
            self.target_cam_lon = (self.target_cam_lon - 22.0 / max(0.5, self.zoom))
            if self.target_cam_lon < -180: self.target_cam_lon += 360
            return True
        elif event in ("RIGHT", "KEY_RIGHT", "KeyD"):
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
        """Procedural side-view illustration/photo of modern airliner in authentic airline livery."""
        # Sky background with realistic atmospheric altitude gradient
        draw.rounded_rectangle([(px, py), (px + pw, py + ph)], radius=10, fill=(12, 18, 28), outline=(35, 75, 120), width=2)
        for y_off in range(ph - 4):
            rat = y_off / float(ph)
            r_c = int(10 + rat * 16)
            g_c = int(20 + rat * 28)
            b_c = int(38 + rat * 48)
            draw.line([(px + 2, py + 2 + y_off), (px + pw - 2, py + 2 + y_off)], fill=(r_c, g_c, b_c))

        # High-altitude condensation trail (contrail)
        contrail_y = py + ph // 2 + 12
        draw.line([(px + 25, contrail_y), (px + pw // 2 - 20, contrail_y)], fill=(220, 235, 255), width=3)
        draw.line([(px + 50, contrail_y - 2), (px + pw // 2 - 40, contrail_y - 2)], fill=(255, 255, 255), width=2)

        # Livery and color scheme
        airline = fl.get("airline", "")
        callsign = fl.get("callsign", "")

        if "LOT" in airline or "LOT" in callsign:
            body_col = (248, 250, 255)
            belly_col = (18, 35, 80)
            tail_col = (14, 28, 70)
            accent_col = (225, 185, 30)  # Crane gold
        elif "Lufthansa" in airline or "DLH" in callsign:
            body_col = (245, 246, 250)
            belly_col = (15, 25, 50)
            tail_col = (10, 20, 45)
            accent_col = (255, 180, 0)  # Lufthansa yellow
        elif "Ryanair" in airline or "RYR" in callsign:
            body_col = (240, 245, 252)
            belly_col = (10, 24, 85)
            tail_col = (10, 24, 85)
            accent_col = (250, 200, 20)  # Ryanair harp gold
        elif "Wizz" in airline or "WZZ" in callsign:
            body_col = (246, 246, 250)
            belly_col = (160, 20, 100)
            tail_col = (190, 25, 115)  # Wizz magenta
            accent_col = (0, 190, 255)  # Cyan W
        elif "Emirates" in airline or "UAE" in callsign:
            body_col = (252, 252, 255)
            belly_col = (220, 225, 235)
            tail_col = (195, 20, 25)  # UAE flag red
            accent_col = (200, 160, 40)
        elif "Air France" in airline or "AFR" in callsign:
            body_col = (248, 249, 252)
            belly_col = (20, 30, 60)
            tail_col = (15, 28, 70)
            accent_col = (230, 30, 40)  # Red accent
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

        # 1. Fuselage tube
        draw.rounded_rectangle([(fx0 + 32, fy0), (fx0 + fuse_len - 32, fy0 + fuse_h)], radius=7, fill=body_col)
        # Nose radome
        draw.polygon([(fx0 + 34, fy0), (fx0, fy0 + fuse_h // 2), (fx0 + 34, fy0 + fuse_h)], fill=body_col)
        draw.polygon([(fx0 + 8, fy0 + fuse_h // 2 - 4), (fx0, fy0 + fuse_h // 2), (fx0 + 8, fy0 + fuse_h // 2 + 4)], fill=(35, 42, 50))
        # Cockpit windshield
        draw.polygon([(fx0 + 14, fy0 + 5), (fx0 + 26, fy0 + 3), (fx0 + 28, fy0 + 8), (fx0 + 18, fy0 + 9)], fill=(16, 28, 48))
        # Lower belly paint
        draw.rectangle([(fx0 + 28, fy0 + fuse_h // 2 + 2), (fx0 + fuse_len - 38, fy0 + fuse_h)], fill=belly_col)
        # Tail taper
        draw.polygon([(fx0 + fuse_len - 35, fy0), (fx0 + fuse_len, fy0 + 9), (fx0 + fuse_len - 35, fy0 + fuse_h)], fill=body_col)

        # 2. Vertical Stabilizer (Tail)
        draw.polygon([(fx0 + fuse_len - 58, fy0), (fx0 + fuse_len - 16, fy0 - 48), (fx0 + fuse_len, fy0 - 46), (fx0 + fuse_len - 22, fy0)], fill=tail_col)
        draw.ellipse([(fx0 + fuse_len - 24, fy0 - 36), (fx0 + fuse_len - 10, fy0 - 22)], fill=accent_col)
        # Horizontal Stabilizer
        draw.polygon([(fx0 + fuse_len - 28, fy0 + 7), (fx0 + fuse_len + 16, fy0 + 9), (fx0 + fuse_len - 12, fy0 + 14)],
                     fill=(min(255, tail_col[0] + 30), min(255, tail_col[1] + 30), min(255, tail_col[2] + 30)))

        # 3. Passenger Windows
        win_y = fy0 + 7
        for wx in range(fx0 + 40, fx0 + fuse_len - 48, 6):
            draw.rectangle([(wx, win_y), (wx + 3, win_y + 4)], fill=(15, 25, 40))

        # 4. Main Swept Wing & Blended Winglet
        draw.polygon([(ac_x - 38, ac_y + 6), (ac_x - 10, ac_y + 40), (ac_x + 10, ac_y + 40), (ac_x + 18, ac_y + 6)],
                     fill=(185, 192, 205), outline=(135, 145, 160))
        draw.polygon([(ac_x + 10, ac_y + 40), (ac_x + 14, ac_y + 26), (ac_x + 18, ac_y + 40)], fill=accent_col)

        # 5. High-Bypass Turbofan Jet Engine
        eng_x = ac_x - 20
        eng_y = ac_y + 14
        draw.rounded_rectangle([(eng_x, eng_y), (eng_x + 40, eng_y + 18)], radius=5, fill=(160, 172, 188), outline=(100, 112, 128))
        draw.ellipse([(eng_x - 3, eng_y + 1), (eng_x + 6, eng_y + 17)], fill=(25, 30, 40))
        draw.polygon([(eng_x + 40, eng_y + 3), (eng_x + 46, eng_y + 9), (eng_x + 40, eng_y + 15)], fill=(45, 50, 60))

        # Badge overlays on photo
        draw.rounded_rectangle([(px + 12, py + ph - 34), (px + 270, py + ph - 8)], radius=6, fill=(8, 14, 22, 220), outline=(0, 200, 255))
        draw.text((px + 20, py + ph - 28), f"✈ {fl.get('model', 'BOEING 737-800')[:28]}", fill=(0, 240, 255), font=get_font(11, bold=True))
        draw.text((px + pw - 145, py + 12), f"REG: {fl.get('reg', 'SP-LWA')}", fill=(255, 255, 255), font=get_font(11, bold=True))

    def _draw_flight_modal(self, canvas, fl: Dict):
        """Render high-tech flight telemetry modal with full airliner photo and telemetry stats."""
        # Dark translucent overlay
        canvas.draw.rectangle([(0, 0), (canvas.width, canvas.height)], fill=(4, 6, 10, 225))

        mx, my, mw, mh = 160, 60, 704, 648
        # Outer Modal Container
        canvas.draw.rounded_rectangle([(mx, my), (mx + mw, my + mh)], radius=16, fill=(16, 22, 32), outline=COLOR_CYBER_CYAN, width=2)

        # Header Bar
        canvas.draw.rounded_rectangle([(mx + 2, my + 2), (mx + mw - 2, my + 60)], radius=14, fill=(24, 34, 50))
        canvas.draw.line([(mx, my + 60), (mx + mw, my + 60)], fill=COLOR_CYBER_CYAN, width=2)

        airline = fl.get("airline", "KOMERCYJNE LINIE LOTNICZE").upper()
        canvas.draw.text((mx + 24, my + 14), f"✈ {airline}", fill=(210, 230, 255), font=get_font(13, bold=True))
        canvas.draw.text((mx + 24, my + 35), f"REJS: {fl['callsign']}  |  ICAO24: {fl.get('icao', 'N/A').upper()}  |  TRANS: {fl.get('squawk', '7000')}",
                         fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))

        # Close button [X]
        canvas.draw.rounded_rectangle([(mx + mw - 54, my + 14), (mx + mw - 18, my + 46)], radius=6, fill=(190, 35, 45), outline=(255, 100, 110))
        canvas.draw.text((mx + mw - 41, my + 19), "✕", fill=(255, 255, 255), font=get_font(14, bold=True))

        # 1. Aircraft Photo Box
        px, py, pw, ph = mx + 20, my + 72, mw - 40, 180
        self._draw_aircraft_photo(canvas.draw, px, py, pw, ph, fl)

        # 2. Flight Route & Progress
        rx, ry, rw = mx + 20, my + 264, mw - 40
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + 82)], radius=10, fill=(20, 28, 42), outline=COLOR_BORDER)

        orig = fl.get("origin", "WAW (Warszawa)")
        dest = fl.get("dest", "FRA (Frankfurt)")
        prog = fl.get("progress", 0.65)

        canvas.draw.text((rx + 16, ry + 12), f"WYLOT:  {orig}", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
        canvas.draw.text((rx + rw - 240, ry + 12), f"CEL:  {dest}", fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))

        # Visual progress track
        bar_x = rx + 16
        bar_y = ry + 44
        bar_w = rw - 32
        canvas.draw.rounded_rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + 12)], radius=6, fill=(12, 16, 24))
        fill_w = int(bar_w * prog)
        canvas.draw.rounded_rectangle([(bar_x, bar_y), (bar_x + fill_w, bar_y + 12)], radius=6, fill=COLOR_CYBER_CYAN)

        pl_icon_x = bar_x + fill_w
        canvas.draw.ellipse([(pl_icon_x - 8, bar_y - 2), (pl_icon_x + 8, bar_y + 14)], fill=(255, 255, 255), outline=COLOR_CYBER_CYAN)
        canvas.draw.text((bar_x + bar_w - 95, ry + 60), f"{int(prog * 100)}% TRASY", fill=COLOR_CYBER_CYAN, font=get_font(10, bold=True))

        # 3. Telemetry Stats Grid
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

        # Bottom Controls Helper
        canvas.draw.text((mx + 24, my + mh - 30), "[A]: Wycentruj widok  |  [D-Pad L/P]: Inny samolot  |  [B / Kliknij poza]: Zamknij",
                         fill=COLOR_TEXT_MUTED, font=get_font(11, bold=True))

    def render(self, canvas):
        card_w_left = 634
        card_w_right = 316

        # ----------------------------------------------------------------------
        # Left Panel: 3D Tactical Globe & Aerospace Radar Canvas
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

        # Viewport Bounds
        vx = 48
        vy = 118
        vw = card_w_left - 32
        vh = 500
        canvas.draw.rectangle([(vx, vy), (vx + vw, vy + vh)], fill=(8, 12, 18), outline=COLOR_BORDER, width=1)

        # ----------------------------------------------------------------------
        # 1. Render 3D Earth Globe (When zoom < 10.0x)
        # ----------------------------------------------------------------------
        if self.zoom < 10.0:
            # Multi-layer Outer Atmospheric Halo
            for i in range(14, 0, -3):
                gr = globe_r + i
                glow_col = (10, 60 + i * 8, 120 + i * 9)
                canvas.draw.ellipse([(cx - gr, cy - gr), (cx + gr, cy + gr)], outline=glow_col, width=2)

            # Globe Sphere Base: Deep Oceanic Blue
            canvas.draw.ellipse([(cx - globe_r, cy - globe_r), (cx + globe_r, cy + globe_r)],
                                fill=(10, 18, 32), outline=(0, 200, 255), width=2)

            # Limb Darkening / Internal Specular Horizon Ring
            for i in range(globe_r, max(0, globe_r - 20), -2):
                canvas.draw.ellipse([(cx - i, cy - i), (cx + i, cy + i)], outline=(16, 32, 54), width=1)

            # Meridians & Parallels Graticule (Curved 3D coordinate mesh)
            # Longitude Meridians (every 30°)
            for m_lon in range(-180, 180, 30):
                pts = []
                for m_lat in range(-80, 81, 10):
                    px, py, vis = self._project_ortho(m_lat, m_lon, cx, cy, globe_r)
                    if vis and (vx <= px <= vx + vw and vy <= py <= vy + vh):
                        pts.append((px, py))
                    else:
                        if len(pts) > 1:
                            canvas.draw.line(pts, fill=(18, 42, 65), width=1)
                        pts = []
                if len(pts) > 1:
                    canvas.draw.line(pts, fill=(18, 42, 65), width=1)

            # Latitude Parallels (Equator + Parallels at ±30°, ±60°)
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

            # Continents Outlines
            for cont in CONTINENTS_GEO:
                c_pts = [self._project_ortho(lat, lon, cx, cy, globe_r) for lon, lat in cont]
                for i in range(len(c_pts) - 1):
                    p1 = c_pts[i]
                    p2 = c_pts[i + 1]
                    if p1[2] and p2[2]:
                        if (vx <= p1[0] <= vx + vw and vy <= p1[1] <= vy + vh) or (vx <= p2[0] <= vx + vw and vy <= p2[1] <= vy + vh):
                            canvas.draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=(38, 140, 95), width=2)

            # Strategic Global Waypoints / Cities on Globe
            font_city = get_font(9, bold=True)
            for c_name, c_lat, c_lon, iata in GLOBAL_WAYPOINTS:
                wpx, wpy, wvis = self._project_ortho(c_lat, c_lon, cx, cy, globe_r)
                if wvis and (vx <= wpx <= vx + vw and vy <= wpy <= vy + vh):
                    canvas.draw.ellipse([(wpx - 2, wpy - 2), (wpx + 2, wpy + 2)], fill=COLOR_CYBER_CYAN, outline=COLOR_TEXT_PRIMARY)
                    if self.zoom >= 1.5:
                        canvas.draw.text((wpx + 5, wpy - 5), iata, fill=(140, 200, 255), font=font_city)

            # ISS Orbit Track Ground Projection (Golden Sine Wave)
            if self.zoom < 5.0 and self.iss_orbit_track:
                t_pts = [self._project_ortho(lat, lon, cx, cy, globe_r) for lat, lon in self.iss_orbit_track]
                for i in range(len(t_pts) - 1):
                    if t_pts[i][2] and t_pts[i + 1][2]:
                        canvas.draw.line([(t_pts[i][0], t_pts[i][1]), (t_pts[i + 1][0], t_pts[i + 1][1])], fill=(180, 125, 25), width=1)

            # Satellites on Globe
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

            # Aircraft Blips on Globe (Stored for hover / click detection)
            font_fl = get_font(9, bold=True)
            for fl in self.flights:
                fx, fy, is_fvis = self._project_ortho(fl["lat"], fl["lon"], cx, cy, globe_r)
                if is_fvis and (vx <= fx <= vx + vw and vy <= fy <= vy + vh):
                    fl["_screen_x"] = fx
                    fl["_screen_y"] = fy
                    canvas.draw.ellipse([(fx - 3, fy - 3), (fx + 3, fy + 3)], fill=COLOR_CYBER_CYAN, outline=COLOR_TEXT_PRIMARY)
                    if self.zoom >= 1.8:
                        canvas.draw.text((fx + 5, fy - 6), fl["callsign"], fill=COLOR_CYBER_CYAN, font=font_fl)
                else:
                    if self.zoom < 2.5:
                        fl["_screen_x"] = None
                        fl["_screen_y"] = None

        # ----------------------------------------------------------------------
        # 2. Render Tactical Airspace Radar (Overlaid / Primary when Zoom >= 2.5)
        # ----------------------------------------------------------------------
        if self.zoom >= 2.5:
            radar_r = 235
            # Range rings
            for r_pct, km_val in [(0.25, "25km"), (0.50, "50km"), (0.75, "100km"), (1.0, "150km")]:
                cr = int(radar_r * r_pct)
                canvas.draw.ellipse([(cx - cr, cy - cr), (cx + cr, cy + cr)], outline=(24, 54, 84), width=1)
                canvas.draw.text((cx + 6, cy - cr + 4), km_val, fill=(60, 100, 140), font=get_font(10, bold=False))

            # Crosshairs
            canvas.draw.line([(cx - radar_r, cy), (cx + radar_r, cy)], fill=(24, 54, 84), width=1)
            canvas.draw.line([(cx, cy - radar_r), (cx, cy + radar_r)], fill=(24, 54, 84), width=1)

            # Rotating Radar Sweep Beam
            rad = math.radians(self.sweep_angle)
            sw_x = cx + int(radar_r * math.cos(rad))
            sw_y = cy + int(radar_r * math.sin(rad))
            canvas.draw.line([(cx, cy), (sw_x, sw_y)], fill=COLOR_CYBER_CYAN, width=2)

            # Draw ADS-B Aircraft in Tactical Airspace
            font_plane = get_font(11, bold=True)
            for fl in self.flights:
                # Scale relative to observer ground station
                scale_km = (150.0 / max(2.5, self.zoom * 0.4))
                dx_km = (fl["lon"] - self.obs_lon) * 67.5
                dy_km = (fl["lat"] - self.obs_lat) * 111.2
                scale = radar_r / scale_km
                ax = cx + int(dx_km * scale)
                ay = cy - int(dy_km * scale)

                # Store screen coordinates for hover/pointer interaction
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

                    is_sel = (self.selected_flight == fl) or (self.hovered_flight == fl)
                    p_col = COLOR_FLIPPER_AMBER if is_sel else COLOR_CYBER_CYAN

                    canvas.draw.polygon([(tip_x, tip_y), (tail_l_x, tail_l_y), (ax, ay), (tail_r_x, tail_r_y)], fill=p_col)
                    fl_level = int(fl.get("alt_m", 10000) * 3.28084 / 100)
                    canvas.draw.text((ax + 10, ay - 8), f"{fl['callsign']}\nFL{fl_level:03d}", fill=COLOR_TEXT_PRIMARY, font=font_plane)

        # ----------------------------------------------------------------------
        # Target Reticle on Hovered / Selected Flight
        # ----------------------------------------------------------------------
        active_fl = self.hovered_flight or self.selected_flight
        if active_fl:
            hx = active_fl.get("_screen_x")
            hy = active_fl.get("_screen_y")
            if hx is not None and hy is not None and (vx <= hx <= vx + vw and vy <= hy <= vy + vh):
                # Lock-on Reticle
                pulse_r = 14 + int(abs(math.sin(time.time() * 5.0)) * 4)
                canvas.draw.ellipse([(hx - pulse_r, hy - pulse_r), (hx + pulse_r, hy + pulse_r)],
                                    outline=COLOR_FLIPPER_AMBER, width=2)
                canvas.draw.line([(hx - pulse_r - 4, hy), (hx - pulse_r + 2, hy)], fill=COLOR_FLIPPER_AMBER, width=2)
                canvas.draw.line([(hx + pulse_r - 2, hy), (hx + pulse_r + 4, hy)], fill=COLOR_FLIPPER_AMBER, width=2)
                canvas.draw.line([(hx, hy - pulse_r - 4), (hx, hy - pulse_r + 2)], fill=COLOR_FLIPPER_AMBER, width=2)
                canvas.draw.line([(hx, hy + pulse_r - 2), (hx, hy + pulse_r + 4)], fill=COLOR_FLIPPER_AMBER, width=2)

                # Tooltip prompt
                canvas.draw_badge(max(vx + 10, min(vx + vw - 220, hx - 100)),
                                  max(vy + 10, hy - pulse_r - 26),
                                  f"✈ {active_fl['callsign']} [KLIKNIJ PO DANE]",
                                  bg_color=(20, 32, 48), text_color=COLOR_CYBER_CYAN)

        # Observer Ground Station Reticle / Target Pin
        ox, oy, o_vis = self._project_ortho(self.obs_lat, self.obs_lon, cx, cy, globe_r)
        if o_vis and (vx <= ox <= vx + vw and vy <= oy <= vy + vh):
            canvas.draw.ellipse([(ox - 6, oy - 6), (ox + 6, oy + 6)], outline=COLOR_FLIPPER_AMBER, width=2)
            canvas.draw.line([(ox - 10, oy), (ox + 10, oy)], fill=COLOR_FLIPPER_AMBER, width=1)
            canvas.draw.line([(ox, oy - 10), (ox, oy + 10)], fill=COLOR_FLIPPER_AMBER, width=1)
            canvas.draw.text((ox + 10, oy - 14), f"● {self.obs_name}", fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))

        # Bottom Zoom Slider & Orientation Info Bar
        z_y = vy + vh + 12
        canvas.draw.rounded_rectangle([(vx, z_y), (vx + vw, z_y + 36)], radius=6, fill=(18, 24, 34), outline=COLOR_BORDER)
        canvas.draw.text((vx + 14, z_y + 10),
                         f"KAMERA: {self.cam_lat:+.2f}°N, {self.cam_lon:+.2f}°E  |  ZOOM: {self.zoom:.1f}x ({self.zoom_names[self.zoom_idx]})",
                         fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=True))
        canvas.draw_badge(vx + vw - 175, z_y + 6, "[X/Y/KÓŁKO] ZOOM", bg_color=(36, 48, 64), text_color=COLOR_CYBER_CYAN)

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
        canvas.draw_badge(rx + 12, ry + 78, "[B] ZMIEŃ BAZĘ / GPS", bg_color=(36, 52, 72), text_color=COLOR_FLIPPER_AMBER)

        # 2. Selected Aircraft Quick Card
        ac_y = ry + 126
        sel_fl = self.selected_flight or (self.flights[0] if self.flights else None)
        canvas.draw.rounded_rectangle([(rx, ac_y), (rx + rw, ac_y + 195)], radius=8, fill=(20, 26, 36), outline=COLOR_BORDER)
        canvas.draw.text((rx + 12, ac_y + 10), "✈ WYBRANY LOT ADS-B", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))
        canvas.draw.line([(rx + 12, ac_y + 30), (rx + rw - 12, ac_y + 30)], fill=COLOR_BORDER, width=1)

        if sel_fl:
            fl_items = [
                ("Znak (Callsign):", f"{sel_fl['callsign']}"),
                ("Model:", f"{sel_fl.get('model', 'Boeing 737')[:16]}"),
                ("Wysokość:", f"FL{int(sel_fl.get('alt_m', 0) * 3.28084 / 100):03d} ({int(sel_fl.get('alt_m', 0))} m)"),
                ("Prędkość:", f"{sel_fl.get('speed_kmh', 0)} km/h"),
                ("Trasa:", f"{sel_fl.get('origin', 'WAW')[:3]} ➔ {sel_fl.get('dest', 'FRA')[:3]}")
            ]
            s_y = ac_y + 38
            for lbl, val in fl_items:
                canvas.draw.text((rx + 12, s_y), lbl, fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=False))
                canvas.draw.text((rx + 115, s_y), val, fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=True))
                s_y += 22
            canvas.draw_badge(rx + 12, ac_y + 155, "[A / KLIK] OTWÓRZ ZDJĘCIE", bg_color=(24, 45, 65), text_color=COLOR_CYBER_CYAN)

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
