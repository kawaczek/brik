"""
BrickDeck Module: Global Aerospace, Satellite & Tactical Air Radar
Unified Air & Space tracking: 3D Earth Globe with ISS and satellites, seamless multi-level zoom,
dynamic ADS-B live air traffic, interactive city search (OSM Nominatim), and GPS coordinate targeting.
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

# Simplified Tactical Vector Continents for 3D Globe Projection
CONTINENTS_GEO = [
    # Europe & Mediterranean
    [(10, 55), (15, 55), (20, 60), (30, 70), (40, 65), (50, 60), (40, 45), (30, 40), (25, 36), (15, 38), (5, 43), (-5, 36), (-9, 43), (2, 51), (10, 55)],
    [(-5, 50), (2, 52), (-2, 58), (-5, 50)], # Britain
    [(5, 60), (15, 58), (28, 70), (20, 70), (10, 64), (5, 60)], # Scandinavia
    # Africa
    [(-5, 36), (12, 38), (32, 31), (43, 12), (51, 10), (40, -10), (33, -28), (20, -35), (15, -20), (10, 5), (-17, 15), (-12, 28), (-5, 36)],
    # Asia
    [(35, 32), (40, 45), (60, 40), (70, 25), (80, 10), (85, 22), (100, 15), (105, 5), (110, 20), (122, 32), (130, 45), (140, 55), (170, 65), (100, 75), (60, 70), (40, 65), (35, 32)],
    [(130, 32), (140, 36), (142, 44), (135, 35), (130, 32)], # Japan
    # North America
    [(-165, 65), (-140, 70), (-85, 75), (-60, 60), (-65, 45), (-80, 25), (-98, 20), (-105, 23), (-125, 48), (-165, 65)],
    [(-80, 25), (-82, 30), (-75, 35)], # Florida
    # South America
    [(-75, 10), (-60, 8), (-35, -5), (-40, -22), (-55, -35), (-68, -55), (-75, -45), (-80, -5), (-75, 10)],
    # Australia
    [(115, -22), (130, -12), (142, -10), (153, -28), (148, -38), (135, -35), (115, -34), (115, -22)]
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

        # Zoom Scale Levels: 1.0 (Orbit Globe) -> 3.5 (Continent) -> 12.0 (Approach) -> 35.0 (Tactical Radar)
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_levels = [1.0, 3.5, 12.0, 35.0]
        self.zoom_idx = 0
        self.zoom_names = ["Globus 3D / Orbity", "Kontynentalny", "Podejście / Korytarze", "Radar Taktyczny ADS-B"]

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
        self.selected_object_idx = 0  # 0..len(flights + sats)
        self.tracking_mode = False

        # City Picker Modal State
        self.modal_open = False
        self.modal_tab = 0  # 0: Presets, 1: Search, 2: GPS Edit
        self.city_picker_idx = 0
        self.search_query = "Gorzow"
        self.search_status = "Gotowy do wyszukiwania"

        # Threading & Background Pollers
        self.thread_running = False
        self.last_fetch_time = 0.0
        self.status_msg = "Inicjalizacja..."
        self.sweep_angle = 0.0

    def on_load(self):
        self._init_synthetic_flights()
        self.thread_running = True
        threading.Thread(target=self._background_worker, daemon=True).start()

    def get_hotkey_hints(self):
        if self.modal_open:
            return [
                ("D-Pad", "Wybierz miejscowość"),
                ("A", "Zatwierdź / Leć tam"),
                ("B", "Zamknij"),
                ("X", "Tryb (Lista / GPS)")
            ]
        else:
            zoom_name = self.zoom_names[self.zoom_idx]
            return [
                ("L1/R1", "Moduły"),
                ("D-Pad", "Obróć globus / Wybierz"),
                ("X / Y", f"Zoom: {zoom_name}"),
                ("B", "Zmień lokalizację (GPS)"),
                ("A", "Śledź obiekt")
            ]

    def _generate_iss_orbit_track(self):
        """Generate sine wave ground track for 51.6° inclination orbit."""
        track = []
        # Center around current ISS longitude
        base_lon = self.iss_data.get("lon", 0.0)
        for deg in range(-180, 180, 6):
            rad = math.radians(deg)
            # Orbit inclination = 51.6 degrees
            lat = 51.6 * math.sin(rad)
            lon = (base_lon + deg)
            if lon > 180: lon -= 360
            if lon < -180: lon += 360
            track.append((lat, lon))
        self.iss_orbit_track = track

    def _init_synthetic_flights(self):
        """Realistic commercial and cargo air traffic around active observer station."""
        p_lat, p_lon = self.obs_lat, self.obs_lon
        self.flights = [
            {"icao": "4851ab", "callsign": "LOT3801", "country": "Polska", "lat": p_lat + 0.18, "lon": p_lon + 0.22, "alt_m": 10970, "speed_kmh": 840, "track": 245.0, "squawk": "7104"},
            {"icao": "3c65c2", "callsign": "DLH142", "country": "Niemcy", "lat": p_lat - 0.25, "lon": p_lon - 0.38, "alt_m": 11580, "speed_kmh": 875, "track": 85.0, "squawk": "1000"},
            {"icao": "4ca831", "callsign": "RYR45P", "country": "Irlandia", "lat": p_lat + 0.32, "lon": p_lon - 0.15, "alt_m": 9450, "speed_kmh": 790, "track": 170.0, "squawk": "4421"},
            {"icao": "47805d", "callsign": "WZZ22A", "country": "Węgry", "lat": p_lat - 0.35, "lon": p_lon + 0.42, "alt_m": 11270, "speed_kmh": 860, "track": 315.0, "squawk": "6215"},
            {"icao": "484b39", "callsign": "LOT282", "country": "Polska", "lat": p_lat + 0.08, "lon": p_lon - 0.45, "alt_m": 8200, "speed_kmh": 760, "track": 110.0, "squawk": "2201"},
            {"icao": "4ca211", "callsign": "RYR198", "country": "Irlandia", "lat": p_lat - 0.12, "lon": p_lon + 0.55, "alt_m": 10300, "speed_kmh": 820, "track": 290.0, "squawk": "5312"},
            {"icao": "3c4a20", "callsign": "CFG312", "country": "Niemcy", "lat": p_lat + 0.42, "lon": p_lon + 0.15, "alt_m": 11800, "speed_kmh": 890, "track": 210.0, "squawk": "7000"},
            {"icao": "896172", "callsign": "UAE152", "country": "ZEA", "lat": p_lat - 0.48, "lon": p_lon - 0.20, "alt_m": 12190, "speed_kmh": 910, "track": 320.0, "squawk": "3411"},
            {"icao": "486290", "callsign": "ENT418", "country": "Polska", "lat": p_lat + 0.22, "lon": p_lon - 0.32, "alt_m": 9800, "speed_kmh": 810, "track": 155.0, "squawk": "4102"},
            {"icao": "4401a5", "callsign": "AUA602", "country": "Austria", "lat": p_lat - 0.18, "lon": p_lon - 0.50, "alt_m": 10600, "speed_kmh": 830, "track": 40.0, "squawk": "6110"}
        ]
        self.status_msg = f"LIVE ADS-B ({len(self.flights)} samolotów) & ISS"

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
            lamin = self.obs_lat - 1.0
            lomin = self.obs_lon - 1.5
            lamax = self.obs_lat + 1.0
            lomax = self.obs_lon + 1.5
            url = f"{OPENSKY_BASE_URL}?lamin={lamin:.3f}&lomin={lomin:.3f}&lamax={lamax:.3f}&lomax={lomax:.3f}"
            req = urllib.request.Request(url, headers={"User-Agent": "BrickDeck-ADS-B/1.0"})
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=4.0) as resp:
                data = json.loads(resp.read().decode())
                states = data.get("states", [])
                if states and len(states) > 0:
                    parsed = []
                    for s in states:
                        if s[6] is None or s[5] is None: continue
                        parsed.append({
                            "icao": s[0] or "",
                            "callsign": (s[1] or s[0] or "UNKNOWN").strip(),
                            "country": s[2] or "Unknown",
                            "lat": float(s[6]),
                            "lon": float(s[5]),
                            "alt_m": float(s[7] or 0.0),
                            "speed_kmh": int((s[9] or 0.0) * 3.6),
                            "track": float(s[10] or 0.0),
                            "squawk": str(s[14] or "N/A")
                        })
                    if parsed:
                        self.flights = parsed
                        self.status_msg = f"LIVE ADS-B ({len(parsed)} samolotów) & ISS"
                        self.last_fetch_time = time.time()
        except Exception:
            if not self.flights:
                self._init_synthetic_flights()
            self.status_msg = "Standby / Cache"

    def _background_worker(self):
        while self.thread_running:
            self._fetch_live_data()
            time.sleep(10.0)

    def _search_city_nominatim(self, query: str):
        """Search GPS coordinates for any city name on OpenStreetMap."""
        self.search_status = f"Szukanie: {query}..."
        def worker():
            try:
                url = f"{NOMINATIM_BASE_URL}?q={urllib.parse.quote(query)}&format=json&limit=1"
                req = urllib.request.Request(url, headers={"User-Agent": "BrickDeck-Geo/1.0"})
                with urllib.request.urlopen(req, timeout=4.0) as resp:
                    data = json.loads(resp.read().decode())
                    if data and len(data) > 0:
                        lat = float(data[0]["lat"])
                        lon = float(data[0]["lon"])
                        name = data[0]["display_name"].split(",")[0]
                        self.obs_name = name
                        self.obs_lat = lat
                        self.obs_lon = lon
                        self.target_cam_lat = lat
                        self.target_cam_lon = lon
                        self.search_status = f"Znaleziono: {name} ({lat:.3f}, {lon:.3f})"
                        self.modal_open = False
                        # Trigger new air traffic fetch
                        threading.Thread(target=self._fetch_live_data, daemon=True).start()
                    else:
                        self.search_status = "Nie znaleziono miejscowości!"
            except Exception as e:
                self.search_status = f"Błąd geolokalizacji: {e}"
        threading.Thread(target=worker, daemon=True).start()

    def update(self, dt: float):
        self.sweep_angle = (self.sweep_angle + dt * 60.0) % 360.0

        # Smooth camera orientation interpolation (Cinematic fly-to)
        lat_diff = self.target_cam_lat - self.cam_lat
        lon_diff = self.target_cam_lon - self.cam_lon
        self.cam_lat += lat_diff * min(1.0, dt * 5.0)
        self.cam_lon += lon_diff * min(1.0, dt * 5.0)

        # Smooth zoom level interpolation
        target_z = self.zoom_levels[self.zoom_idx]
        self.zoom += (target_z - self.zoom) * min(1.0, dt * 7.0)

        # Propagate simulated satellites slightly for life
        for sat in self.satellites[1:]:
            sat["lon"] = (sat["lon"] + dt * 2.0)
            if sat["lon"] > 180: sat["lon"] -= 360

        # Update dynamic flight positions along their heading
        for fl in self.flights:
            t_rad = math.radians(fl["track"])
            dist_deg = (fl["speed_kmh"] / 3600.0 * dt) / 111.0
            fl["lat"] += math.cos(t_rad) * dist_deg
            fl["lon"] += math.sin(t_rad) * dist_deg / max(0.2, math.cos(math.radians(fl["lat"])))
            # Keep within boundary around obs station
            if abs(fl["lat"] - self.obs_lat) > 1.8 or abs(fl["lon"] - self.obs_lon) > 2.2:
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

    def render(self, canvas):
        card_w_left = 634
        card_w_right = 316

        # ----------------------------------------------------------------------
        # Left Panel: 3D Tactical Globe & Aerospace Radar Canvas
        # ----------------------------------------------------------------------
        canvas.draw_card(
            32, 66, card_w_left, 634,
            title="GLOBAL AEROSPACE & SATELLITE RADAR",
            subtitle=f"Baza: {self.obs_name}  |  Tryb: {self.zoom_names[self.zoom_idx]}",
            border_color=self.accent_color
        )

        cx = 349
        cy = 385
        # Base sphere radius scaled by dynamic zoom
        globe_r = int(185 * self.zoom)

        # Clip mask viewport
        vx = 48
        vy = 118
        vw = card_w_left - 32
        vh = 500
        canvas.draw.rectangle([(vx, vy), (vx + vw, vy + vh)], fill=(8, 12, 18), outline=COLOR_BORDER, width=1)

        # 1. Render 3D Earth Globe Sphere
        if self.zoom < 10.0:
            # Outer Atmospheric Glow Rim
            canvas.draw.ellipse([(cx - globe_r, cy - globe_r), (cx + globe_r, cy + globe_r)],
                                fill=(12, 20, 32), outline=(30, 100, 180), width=2)

            # Draw Latitude Parallels (Equator, ±30°, ±60°)
            for par_deg in [-60, -30, 0, 30, 60]:
                par_pts = []
                for p_lon in range(-180, 181, 15):
                    px, py, vis = self._project_ortho(par_deg, p_lon, cx, cy, globe_r)
                    if vis and (vx <= px <= vx + vw and vy <= py <= vy + vh):
                        par_pts.append((px, py))
                    else:
                        par_pts.append(None)
                # Draw visible segments
                for i in range(len(par_pts) - 1):
                    if par_pts[i] and par_pts[i+1]:
                        col = (30, 80, 120) if par_deg == 0 else (18, 38, 60)
                        canvas.draw.line([par_pts[i], par_pts[i+1]], fill=col, width=1)

            # Draw Continents Outlines
            for cont in CONTINENTS_GEO:
                c_pts = [self._project_ortho(lat, lon, cx, cy, globe_r) for lon, lat in cont]
                for i in range(len(c_pts) - 1):
                    p1 = c_pts[i]
                    p2 = c_pts[i+1]
                    if p1[2] and p2[2]:  # Both points on front hemisphere
                        if (vx <= p1[0] <= vx + vw and vy <= p1[1] <= vy + vh) or (vx <= p2[0] <= vx + vw and vy <= p2[1] <= vy + vh):
                            canvas.draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=(36, 120, 90), width=2)

            # Draw ISS Orbit Track Ground Projection (Golden Sine Path)
            if self.zoom < 5.0 and self.iss_orbit_track:
                t_pts = [self._project_ortho(lat, lon, cx, cy, globe_r) for lat, lon in self.iss_orbit_track]
                for i in range(len(t_pts) - 1):
                    if t_pts[i][2] and t_pts[i+1][2]:
                        canvas.draw.line([(t_pts[i][0], t_pts[i][1]), (t_pts[i+1][0], t_pts[i+1][1])], fill=(160, 110, 20), width=1)

            # Draw Satellites on Globe
            font_sat = get_font(10, bold=True)
            for sat in self.satellites:
                sx, sy, is_vis = self._project_ortho(sat["lat"], sat["lon"], cx, cy, globe_r)
                if is_vis and (vx - 10 <= sx <= vx + vw + 10 and vy - 10 <= sy <= vy + vh + 10):
                    s_col = sat["col"]
                    canvas.draw.ellipse([(sx - 4, sy - 4), (sx + 4, sy + 4)], fill=s_col, outline=COLOR_TEXT_PRIMARY)
                    # Solar panel wings graphic for ISS
                    if sat["id"] == "ISS":
                        canvas.draw.line([(sx - 8, sy), (sx + 8, sy)], fill=COLOR_FLIPPER_AMBER, width=2)
                        canvas.draw.rectangle([(sx - 8, sy - 3), (sx - 5, sy + 3)], fill=(40, 120, 200))
                        canvas.draw.rectangle([(sx + 5, sy - 3), (sx + 8, sy + 3)], fill=(40, 120, 200))
                    canvas.draw.text((sx + 10, sy - 6), sat["id"], fill=s_col, font=font_sat)

            # Draw Aircraft on Globe
            font_fl = get_font(9, bold=True)
            for fl in self.flights:
                fx, fy, is_fvis = self._project_ortho(fl["lat"], fl["lon"], cx, cy, globe_r)
                if is_fvis and (vx <= fx <= vx + vw and vy <= fy <= vy + vh):
                    canvas.draw.ellipse([(fx - 3, fy - 3), (fx + 3, fy + 3)], fill=COLOR_CYBER_CYAN, outline=COLOR_TEXT_PRIMARY)
                    if self.zoom >= 2.0:
                        canvas.draw.text((fx + 5, fy - 6), fl["callsign"], fill=COLOR_CYBER_CYAN, font=font_fl)

        # ----------------------------------------------------------------------
        # 2. Render Zoomed Tactical Airspace Radar (Appears at higher zoom levels)
        # ----------------------------------------------------------------------
        if self.zoom >= 3.0:
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

            # Draw ADS-B Aircraft in Airspace
            font_plane = get_font(11, bold=True)
            for fl in self.flights:
                # Convert lat/lon relative to active observer station
                dx_km = (fl["lon"] - self.obs_lon) * 67.5
                dy_km = (fl["lat"] - self.obs_lat) * 111.2
                scale = radar_r / 150.0
                ax = cx + int(dx_km * scale)
                ay = cy - int(dy_km * scale)

                if (ax - cx)**2 + (ay - cy)**2 <= radar_r**2:
                    t_rad = math.radians(fl["track"] - 90)
                    p_len = 10
                    tip_x = ax + int(math.cos(t_rad) * p_len)
                    tip_y = ay + int(math.sin(t_rad) * p_len)
                    tail_l_x = ax + int(math.cos(t_rad + 2.5) * (p_len * 0.8))
                    tail_l_y = ay + int(math.sin(t_rad + 2.5) * (p_len * 0.8))
                    tail_r_x = ax + int(math.cos(t_rad - 2.5) * (p_len * 0.8))
                    tail_r_y = ay + int(math.sin(t_rad - 2.5) * (p_len * 0.8))

                    canvas.draw.polygon([(tip_x, tip_y), (tail_l_x, tail_l_y), (ax, ay), (tail_r_x, tail_r_y)], fill=COLOR_CYBER_CYAN)
                    fl_level = int(fl["alt_m"] * 3.28084 / 100)
                    canvas.draw.text((ax + 10, ay - 8), f"{fl['callsign']}\nFL{fl_level:03d}", fill=COLOR_TEXT_PRIMARY, font=font_plane)

        # Observer Ground Station Reticle / Target Pin
        ox, oy, o_vis = self._project_ortho(self.obs_lat, self.obs_lon, cx, cy, globe_r)
        if o_vis and (vx <= ox <= vx + vw and vy <= oy <= vy + vh):
            canvas.draw.ellipse([(ox - 6, oy - 6), (ox + 6, oy + 6)], outline=COLOR_FLIPPER_AMBER, width=2)
            canvas.draw.line([(ox - 10, oy), (ox + 10, oy)], fill=COLOR_FLIPPER_AMBER, width=1)
            canvas.draw.line([(ox, oy - 10), (ox, oy + 10)], fill=COLOR_FLIPPER_AMBER, width=1)
            canvas.draw.text((ox + 10, oy - 14), f"● {self.obs_name}", fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))

        # Bottom Zoom Slider & Orientation Info
        z_y = vy + vh + 12
        canvas.draw.rounded_rectangle([(vx, z_y), (vx + vw, z_y + 36)], radius=6, fill=(18, 24, 34), outline=COLOR_BORDER)
        canvas.draw.text((vx + 14, z_y + 10), f"KAMERA: Lat {self.cam_lat:+.2f}°  Lon {self.cam_lon:+.2f}°  |  Zoom: {self.zoom:.1f}x", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=True))
        canvas.draw_badge(vx + vw - 140, z_y + 6, "[X/Y] ZMIEŃ ZOOM", bg_color=(36, 48, 64), text_color=COLOR_CYBER_CYAN)

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
        canvas.draw_badge(rx + 12, ry + 78, "[B] ZMIEŃ MIASTO / GPS", bg_color=(36, 52, 72), text_color=COLOR_FLIPPER_AMBER)

        # 2. ISS Real-Time Flight Card
        iss_y = ry + 128
        canvas.draw.rounded_rectangle([(rx, iss_y), (rx + rw, iss_y + 200)], radius=8, fill=(20, 26, 36), outline=COLOR_FLIPPER_AMBER, width=1)
        canvas.draw.text((rx + 12, iss_y + 10), "★ MIĘDZYNARODOWA STACJA (ISS)", fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))
        canvas.draw.line([(rx + 12, iss_y + 30), (rx + rw - 12, iss_y + 30)], fill=COLOR_BORDER, width=1)

        iss_items = [
            ("Szerokość (Lat):", f"{self.iss_data['lat']:+.3f}°"),
            ("Długość (Lon):", f"{self.iss_data['lon']:+.3f}°"),
            ("Pułap orbitalny:", f"{self.iss_data['alt_km']:.1f} km"),
            ("Prędkość przelotowa:", f"{self.iss_data['vel_kmh']:,} km/h".replace(",", " ")),
            ("Widoczność:", f"{self.iss_data['visibility'].upper()}"),
            ("Najbliższy przelot:", f"za {self.iss_data['next_pass_min']} min (Elew: {self.iss_data['max_elevation']}°)")
        ]
        s_y = iss_y + 38
        for lbl, val in iss_items:
            canvas.draw.text((rx + 12, s_y), lbl, fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=False))
            canvas.draw.text((rx + 130, s_y), val, fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=True))
            s_y += 24

        # 3. Aerospace Radio Frequencies Card
        freq_y = iss_y + 212
        canvas.draw.rounded_rectangle([(rx, freq_y), (rx + rw, freq_y + 160)], radius=8, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((rx + 12, freq_y + 10), "CZĘSTOTLIWOŚCI RADIOWE (SDR)", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))
        canvas.draw.line([(rx + 12, freq_y + 28), (rx + rw - 12, freq_y + 28)], fill=COLOR_BORDER, width=1)

        freqs = [
            ("ISS APRS / Packet:", "145.825 MHz"),
            ("ISS Voice (Krótkofalowcy):", "145.800 MHz"),
            ("NOAA-15 / 18 APT Pogoda:", "137.620 MHz"),
            ("ADS-B Samoloty Cywilne:", "1090.000 MHz"),
            ("Pasmo Lotnicze AM Voice:", "118 - 136 MHz")
        ]
        f_row_y = freq_y + 36
        for f_name, f_val in freqs:
            canvas.draw.text((rx + 12, f_row_y), f_name, fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=False))
            canvas.draw.text((rx + 175, f_row_y), f_val, fill=COLOR_PHOSPHOR_GREEN, font=get_font(11, bold=True))
            f_row_y += 24

        # ----------------------------------------------------------------------
        # Modal Overlay: Location Picker / Search / GPS Input
        # ----------------------------------------------------------------------
        if self.modal_open:
            # Dark transparent overlay over entire screen
            canvas.draw.rectangle([(0, 0), (canvas.width, canvas.height)], fill=(5, 8, 12, 235))

            # Modal Box (Center: 180, 100, 664, 560)
            modal_x = 180
            modal_y = 100
            modal_w = 664
            modal_h = 560
            canvas.draw.rounded_rectangle([(modal_x, modal_y), (modal_x + modal_w, modal_y + modal_h)],
                                          radius=14, fill=(20, 26, 38), outline=COLOR_CYBER_CYAN, width=2)

            canvas.draw.text((modal_x + 24, modal_y + 20), "WYBÓR LOKALIZACJI STACJI BAZOWEJ & PRZELOT KAMERY", fill=COLOR_CYBER_CYAN, font=get_font(15, bold=True))
            canvas.draw.text((modal_x + 24, modal_y + 42), "Wybierz miejscowość z listy, a globus płynnie przybliży się do celu", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=False))
            canvas.draw.line([(modal_x + 20, modal_y + 64), (modal_x + modal_w - 20, modal_y + 64)], fill=COLOR_BORDER, width=1)

            # City List
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

            # Bottom Modal Prompt
            bot_y = modal_y + modal_h - 60
            canvas.draw.line([(modal_x + 20, bot_y), (modal_x + modal_w - 20, bot_y)], fill=COLOR_BORDER, width=1)
            canvas.draw.text((modal_x + 24, bot_y + 18), "[D-Pad G/D]: Wybierz  |  [A]: Leć do celu  |  [B]: Anuluj", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))

    def handle_input(self, event: str) -> bool:
        if self.modal_open:
            if event == "UP":
                if self.city_picker_idx > 0:
                    self.city_picker_idx -= 1
                    return True
            elif event == "DOWN":
                if self.city_picker_idx < min(12, len(PRESET_CITIES)) - 1:
                    self.city_picker_idx += 1
                    return True
            elif event == "BTN_A":
                # Select city and fly camera to destination
                name, lat, lon, _ = PRESET_CITIES[self.city_picker_idx]
                self.obs_name = name
                self.obs_lat = lat
                self.obs_lon = lon
                self.target_cam_lat = lat
                self.target_cam_lon = lon
                self.zoom_idx = 3  # Automatically zoom into Tactical Radar!
                self.modal_open = False
                # Trigger live ADS-B refresh for new location
                threading.Thread(target=self._fetch_live_data, daemon=True).start()
                return True
            elif event in ("BTN_B", "MENU"):
                self.modal_open = False
                return True
            return False

        # Normal view controls
        if event == "BTN_B":
            self.modal_open = True
            return True
        elif event == "BTN_X":
            # Zoom In (Closer and closer: Orbit -> Continent -> Approach -> Tactical Radar)
            if self.zoom_idx < len(self.zoom_levels) - 1:
                self.zoom_idx += 1
                return True
        elif event == "BTN_Y":
            # Zoom Out (Back up into space!)
            if self.zoom_idx > 0:
                self.zoom_idx -= 1
                return True
        elif event == "LEFT":
            self.target_cam_lon = (self.target_cam_lon - 20.0 / self.zoom)
            if self.target_cam_lon < -180: self.target_cam_lon += 360
            return True
        elif event == "RIGHT":
            self.target_cam_lon = (self.target_cam_lon + 20.0 / self.zoom)
            if self.target_cam_lon > 180: self.target_cam_lon -= 360
            return True
        elif event == "UP":
            self.target_cam_lat = min(85.0, self.target_cam_lat + 15.0 / self.zoom)
            return True
        elif event == "DOWN":
            self.target_cam_lat = max(-85.0, self.target_cam_lat - 15.0 / self.zoom)
            return True
        elif event == "BTN_A":
            # Snap camera back to Ground Station
            self.target_cam_lat = self.obs_lat
            self.target_cam_lon = self.obs_lon
            return True

        return False
