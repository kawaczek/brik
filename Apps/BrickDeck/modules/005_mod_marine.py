"""
BrickDeck Module: Global Marine Traffic & AIS Nautical Radar (mod_marine.py)
Tactical Maritime AIS Radar and Vessel Fleet Telemetry.
Features:
- 360° PPI Nautical Radar display with rotating beam sweep and range rings (2 to 50 NM)
- Shoreline vector coastline contours for major global straits and ports
- Color-coded vessel tracking: Cargo, Tankers, Ferries, Tugs, Fishing, Military/Coast Guard
- Directional vessel chevrons with 10-minute velocity predictor vectors
- Detailed Vessel Telemetry: MMSI, IMO, Callsign, Draught, Dimensions, Destination, ETA
- Switchable AIS Fleet List and Beaufort Sea State Scale
- 100% standalone, zero-dongle: realistic kinematic simulation and open AIS feed support.
"""

import math
import time
import random
from typing import List, Dict, Tuple, Optional, Any

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_ELECTRIC_BLUE, COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN, COLOR_STATUS_ERR
)
from core.canvas import get_font
from core.i18n import t

# Vessel Type Colors
VESSEL_COLORS = {
    "Cargo": (50, 220, 100),       # Green
    "Tanker": (255, 80, 80),       # Red
    "Passenger": (0, 210, 255),    # Cyan
    "Tug": (255, 190, 0),          # Amber
    "Fishing": (220, 100, 255),    # Violet/Pink
    "Coast Guard": (100, 160, 255),# Blue
    "Sailing": (240, 240, 255)     # White
}

# Major Global Sea Ports and Waterways
MARITIME_ZONES = [
    {
        "id": "swinoujscie",
        "name": "Zatoka Pomorska / Świnoujście & Szczecin",
        "name_en": "Pomeranian Bay / Swinoujscie & Szczecin",
        "country": "Polska 🇵🇱",
        "center": (53.95, 14.28),
        "desc": "Terminal LNG, tor wodny do Szczecina, promy Ystad/Trelleborg",
        "coastline": [
            (-25, -15), (-10, -8), (0, -4), (5, -6), (15, -12), (25, -18)
        ]
    },
    {
        "id": "gdansk",
        "name": "Zatoka Gdańska / Gdańsk & Gdynia",
        "name_en": "Gulf of Gdansk / Gdansk & Gdynia",
        "country": "Polska 🇵🇱",
        "center": (54.42, 18.72),
        "desc": "Hub DCT Baltic Hub, Naftoport, Półwysep Helski",
        "coastline": [
            (-20, -20), (-15, -5), (-5, 15), (5, 22), (18, 18), (25, 0)
        ]
    },
    {
        "id": "dover",
        "name": "Cieśnina Dover / Kanał La Manche",
        "name_en": "Strait of Dover / English Channel",
        "country": "UK 🇬🇧 / FR 🇫🇷",
        "center": (51.10, 1.48),
        "desc": "Najruchliwszy szlak morski świata (>500 statków/dobę)",
        "coastline": [
            (-25, 12), (-10, 15), (10, 22), (25, 25),   # UK coast
            (-25, -18), (-5, -12), (15, -6), (25, -2)   # FR coast
        ]
    },
    {
        "id": "gibraltar",
        "name": "Cieśnina Gibraltarska (Gibraltar Strait)",
        "name_en": "Strait of Gibraltar",
        "country": "ES 🇪🇸 / MA 🇲🇦",
        "center": (35.96, -5.52),
        "desc": "Wrota Atlantyk - Morze Śródziemne",
        "coastline": [
            (-25, 10), (0, 12), (15, 8), (25, 14),      # Europe
            (-25, -12), (-5, -10), (10, -14), (25, -10) # Africa
        ]
    },
    {
        "id": "rotterdam",
        "name": "Port Rotterdam / Europort",
        "name_en": "Port of Rotterdam / Europort",
        "country": "Holandia 🇳🇱",
        "center": (51.96, 4.08),
        "desc": "Największy port morski Europy, megakontenerowce",
        "coastline": [
            (-25, -10), (-5, -4), (10, -2), (25, 4)
        ]
    },
    {
        "id": "fehmarn",
        "name": "Cieśnina Fehmarn & Kanał Kiloński",
        "name_en": "Fehmarn Belt & Kiel Canal",
        "country": "Niemcy 🇩🇪 / Dania 🇩🇰",
        "center": (54.52, 11.25),
        "desc": "Kluczowa arteria łącząca Morze Północne z Bałtykiem",
        "coastline": [
            (-25, 8), (-10, 10), (5, 12), (20, 8),
            (-25, -12), (-5, -10), (15, -14), (25, -12)
        ]
    },
    {
        "id": "bosphorus",
        "name": "Cieśnina Bosfor / Stambuł",
        "name_en": "Bosphorus Strait / Istanbul",
        "country": "Turcja 🇹🇷",
        "center": (41.12, 29.08),
        "desc": "Tranzyt Morze Czarne - Morze Marmara",
        "coastline": [
            (-12, -25), (-8, 0), (-10, 25),
            (8, -25), (10, 0), (12, 25)
        ]
    },
    {
        "id": "singapore",
        "name": "Cieśnina Malakka & Port Singapur",
        "name_en": "Malacca Strait & Singapore",
        "country": "Singapur 🇸🇬",
        "center": (1.24, 103.82),
        "desc": "Serce światowego handlu kontenerowego Azja-Europa",
        "coastline": [
            (-25, 5), (-10, 8), (10, 10), (25, 6),
            (-25, -12), (-5, -14), (15, -10), (25, -8)
        ]
    }
]

# Preset templates for realistic simulated AIS fleet per port
VESSEL_TEMPLATES = [
    # Polish Pomeranian Bay / Swinoujscie
    [
        {"name": "BALTICA (POLFERRIES)", "mmsi": "261014230", "call": "SPO342", "flag": "🇵🇱 PL", "type": "Passenger", "speed": 17.2, "course": 350, "dist": 3.8, "bearing": 15, "dim": "180x28m", "draught": 6.2, "dest": "YSTAD", "eta": "14:30"},
        {"name": "LNG LECH KACZYNSKI", "mmsi": "261099110", "call": "SPLK1", "flag": "🇵🇱 PL", "type": "Tanker", "speed": 0.0, "course": 140, "dist": 1.2, "bearing": 210, "dim": "299x46m", "draught": 11.8, "dest": "SWINOUJSCIE LNG", "eta": "MOORED"},
        {"name": "MAERSK HAMBURG", "mmsi": "219018440", "call": "OYKH2", "flag": "🇩🇰 DK", "type": "Cargo", "speed": 14.5, "course": 65, "dist": 8.4, "bearing": 55, "dim": "366x48m", "draught": 13.5, "dest": "GDANSK DCT", "eta": "19:00"},
        {"name": "STRAZAK-28 (SAR)", "mmsi": "261000450", "call": "SPG28", "flag": "🇵🇱 PL", "type": "Coast Guard", "speed": 12.0, "course": 210, "dist": 2.1, "bearing": 170, "dim": "32x8m", "draught": 3.1, "dest": "PATROL BASEN", "eta": "UNDERWAY"},
        {"name": "KUTER SWI-44", "mmsi": "261044120", "call": "SPK44", "flag": "🇵🇱 PL", "type": "Fishing", "speed": 7.4, "course": 310, "dist": 5.6, "bearing": 305, "dim": "24x6m", "draught": 2.8, "dest": "FISHING ZONE B", "eta": "16:00"},
        {"name": "FAIRPLAY VII (TUG)", "mmsi": "211234990", "call": "DLIH", "flag": "🇩🇪 DE", "type": "Tug", "speed": 4.5, "course": 135, "dist": 1.8, "bearing": 190, "dim": "26x9m", "draught": 4.5, "dest": "HARBOUR TUG", "eta": "READY"},
        {"name": "DAR MLODZIEZY", "mmsi": "261141000", "call": "SQLZ", "flag": "🇵🇱 PL", "type": "Sailing", "speed": 9.1, "course": 45, "dist": 11.2, "bearing": 340, "dim": "108x14m", "draught": 6.6, "dest": "GDYNIA", "eta": "JUTRO 10:00"}
    ],
    # Gdansk Bay
    [
        {"name": "MSC GULSUN", "mmsi": "353136000", "call": "3FLO8", "flag": "🇵🇦 PA", "type": "Cargo", "speed": 15.8, "course": 120, "dist": 6.2, "bearing": 45, "dim": "399x61m", "draught": 16.0, "dest": "GDANSK BALTIC HUB", "eta": "12:15"},
        {"name": "ORLEN BALTIC EXPLORER", "mmsi": "261005220", "call": "SPBE", "flag": "🇵🇱 PL", "type": "Tanker", "speed": 0.0, "course": 0, "dist": 4.1, "bearing": 110, "dim": "245x42m", "draught": 14.2, "dest": "NAFTOPORT T1", "eta": "DISCHARGING"},
        {"name": "STENA SPIRIT", "mmsi": "265431000", "call": "SLSX", "flag": "🇸🇪 SE", "type": "Passenger", "speed": 18.5, "course": 355, "dist": 2.8, "bearing": 15, "dim": "175x30m", "draught": 6.3, "dest": "KARLSKRONA", "eta": "19:30"},
        {"name": "KAPITAN POINCA (SAR)", "mmsi": "261002340", "call": "SPO2", "flag": "🇵🇱 PL", "type": "Coast Guard", "speed": 11.0, "course": 90, "dist": 3.5, "bearing": 85, "dim": "53x12m", "draught": 4.8, "dest": "DYŻUR ZATOKA", "eta": "READY"},
        {"name": "KUTER GDY-18", "mmsi": "261018990", "call": "SPY18", "flag": "🇵🇱 PL", "type": "Fishing", "speed": 6.2, "course": 215, "dist": 7.5, "bearing": 290, "dim": "19x5m", "draught": 2.4, "dest": "PUCKA BAY", "eta": "15:45"},
        {"name": "WUJAX (TUG)", "mmsi": "261008770", "call": "SPWJ", "flag": "🇵🇱 PL", "type": "Tug", "speed": 5.1, "course": 180, "dist": 1.9, "bearing": 195, "dim": "30x10m", "draught": 5.0, "dest": "PORT GDYNIA", "eta": "ASSIST"}
    ]
]


class MarineModule(BaseModule):
    name = "Global Marine Traffic & AIS Nautical Radar"
    short_name = "Marine"
    icon = "🚢"
    accent_color = (0, 190, 255)

    def __init__(self, app_context=None):
        super().__init__(app_context)

        # Active port / zone
        self.zone_idx = 0
        # Radar display range in Nautical Miles (NM)
        self.range_levels = [2, 5, 10, 25, 50]
        self.range_idx = 2  # 10 NM default
        # Radar rotating sweep angle (0 to 360 deg)
        self.sweep_angle = 0.0
        self.sweep_speed = 70.0  # deg/sec

        # Target selection
        self.selected_vessel_idx = 0
        # View mode: 0 = Vessel Inspector, 1 = AIS Fleet List Table
        self.view_mode = 0

        # Vessels container (hydrated per zone)
        self.vessels: List[Dict[str, Any]] = []
        self._load_zone_vessels(0)

        # Sea State / Beaufort scale simulation
        self.beaufort_scale = 3  # 3°B: Łagodny wiatr, fale 0.6-1.0m
        self.wind_dir_deg = 230
        self.wind_speed_kn = 11.5

        # Last kinematic update timestamp
        self.last_kinematic_time = time.time()

    def _load_zone_vessels(self, zone_idx: int):
        self.zone_idx = zone_idx
        # Pick template or generate dynamic fleet
        tpl_idx = zone_idx if zone_idx < len(VESSEL_TEMPLATES) else 0
        base_list = VESSEL_TEMPLATES[tpl_idx]

        self.vessels = []
        zone = MARITIME_ZONES[self.zone_idx]

        for i, b in enumerate(base_list):
            v = dict(b)
            # Add dynamic xy coordinates relative to radar center (in NM)
            rad = math.radians(v["bearing"])
            dist = v["dist"]
            v["x_nm"] = dist * math.sin(rad)
            v["y_nm"] = -dist * math.cos(rad)
            self.vessels.append(v)

        # If zone has few vessels, generate generic international cargo/tankers
        if len(self.vessels) < 6:
            types = ["Cargo", "Tanker", "Tug", "Passenger", "Fishing"]
            names = ["EVER GIVEN", "CMA CGM ANTOINE", "NORDIC STAR", "BALTIC TRADER", "SEASPAN LION"]
            flags = ["🇵🇦 PA", "🇱🇷 LR", "🇲🇹 MT", "🇩🇪 DE", "🇸🇬 SG"]

            for k in range(len(self.vessels), 7):
                v_type = types[k % len(types)]
                dist = random.uniform(2.0, 9.0)
                brg = random.uniform(0, 360)
                spd = random.uniform(6.0, 19.5) if v_type != "Tug" else 4.2
                rad = math.radians(brg)
                crs = random.randint(0, 359)
                self.vessels.append({
                    "name": names[k % len(names)],
                    "mmsi": f"219{random.randint(100000, 999999)}",
                    "call": f"OZ{random.randint(1000, 9999)}",
                    "flag": flags[k % len(flags)],
                    "type": v_type,
                    "speed": round(spd, 1),
                    "course": crs,
                    "dist": round(dist, 1),
                    "bearing": int(brg),
                    "dim": "280x40m",
                    "draught": 12.0,
                    "dest": zone["name"].split("/")[0].strip()[:14],
                    "eta": f"{random.randint(12, 23)}:{random.randint(10, 59)}",
                    "x_nm": dist * math.sin(rad),
                    "y_nm": -dist * math.cos(rad)
                })

        self.selected_vessel_idx = 0

    def get_hotkey_hints(self):
        v_mode_lbl = "Lista Floty" if self.view_mode == 0 else "Karta Statku"
        cur_rng = self.range_levels[self.range_idx]
        return [
            ("L1/R1", "Zmień Port/Akwen"),
            ("D-Pad G/D", "Wybierz Statek"),
            ("D-Pad L/P", f"Zoom: {cur_rng}NM"),
            ("X", v_mode_lbl),
            ("Y", "Odśwież AIS"),
            ("A", "Karta / Śledź")
        ]

    def update(self, dt: float):
        # Update radar rotating sweep
        self.sweep_angle = (self.sweep_angle + self.sweep_speed * dt) % 360.0

        # Kinematic movement of vessels (time-stepped simulation)
        now = time.time()
        elapsed = now - self.last_kinematic_time
        if elapsed > 1.0:
            for v in self.vessels:
                if v["speed"] > 0.1:
                    # Speed in knots -> nautical miles per second (1 kn = 1 NM / 3600 s)
                    dist_traveled_nm = (v["speed"] / 3600.0) * elapsed * 10.0  # Time acceleration x10
                    crs_rad = math.radians(v["course"])
                    v["x_nm"] += dist_traveled_nm * math.sin(crs_rad)
                    v["y_nm"] -= dist_traveled_nm * math.cos(crs_rad)

                    # Update distance and bearing from center
                    new_dist = math.sqrt(v["x_nm"]**2 + v["y_nm"]**2)
                    new_brg = (math.degrees(math.atan2(v["x_nm"], -v["y_nm"])) + 360) % 360
                    v["dist"] = round(new_dist, 1)
                    v["bearing"] = int(new_brg)

            self.last_kinematic_time = now

    def render(self, canvas):
        now = time.time()
        zone = MARITIME_ZONES[self.zone_idx]
        cur_range_nm = self.range_levels[self.range_idx]

        # -------------------------------------------------------------
        # Main Tactical Frame
        # -------------------------------------------------------------
        canvas.draw_card(
            x=25, y=66, w=974, h=638,
            title=f"🚢 GLOBAL MARINE AIS RADAR: {zone['name'].upper()}",
            subtitle=f"{zone['country']}  |  Zasięg: {cur_range_nm} NM  |  Wykryto {len(self.vessels)} jednostek AIS  |  Stan morza: {self.beaufort_scale}°B",
            border_color=self.accent_color
        )

        # -------------------------------------------------------------
        # Left Panel: Tactical PPI Radar Scope (x=40, y=116, w=570, h=570)
        # -------------------------------------------------------------
        rx, ry, rw, rh = 40, 116, 570, 570
        cx, cy = rx + rw // 2, ry + rh // 2
        radar_r = 250  # radius of radar circle in pixels

        # Radar Scope Background (Dark Maritime Ocean)
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=10, fill=(8, 14, 22), outline=COLOR_BORDER, width=1)
        canvas.draw.ellipse([(cx - radar_r, cy - radar_r), (cx + radar_r, cy + radar_r)], fill=(10, 18, 28), outline=(25, 45, 65), width=2)

        # Concentric Nautical Distance Range Rings
        # Rings at 25%, 50%, 75%, 100% of radius
        for step in (0.25, 0.50, 0.75, 1.0):
            step_r = int(radar_r * step)
            step_nm = cur_range_nm * step
            canvas.draw.ellipse([(cx - step_r, cy - step_r), (cx + step_r, cy + step_r)], outline=(22, 38, 55), width=1)
            # Label along North radius
            canvas.draw.text((cx + 6, cy - step_r + 3), f"{step_nm:.1f} NM", fill=(0, 120, 160), font=get_font(9))

        # Radial Azimuth Lines (every 30 degrees)
        for deg in range(0, 360, 30):
            rad = math.radians(deg - 90)
            lx = cx + int(radar_r * math.cos(rad))
            ly = cy + int(radar_r * math.sin(rad))
            canvas.draw.line([(cx, cy), (lx, ly)], fill=(18, 30, 44), width=1)
            # Cardinal markers
            if deg in (0, 90, 180, 270):
                card_lbl = {0: "000° N", 90: "090° E", 180: "180° S", 270: "270° W"}[deg]
                tx = cx + int((radar_r + 14) * math.cos(rad))
                ty = cy + int((radar_r + 14) * math.sin(rad))
                canvas.draw.text((tx, ty), card_lbl, fill=COLOR_CYBER_CYAN, font=get_font(9, bold=True), anchor="mm")

        # Coastline Approximation Vectors
        coast_pts = zone.get("coastline", [])
        if len(coast_pts) >= 2:
            pixel_pts = []
            for c_nm_x, c_nm_y in coast_pts:
                px = cx + int((c_nm_x / float(cur_range_nm)) * radar_r)
                py = cy + int((c_nm_y / float(cur_range_nm)) * radar_r)
                pixel_pts.append((px, py))
            for i in range(len(pixel_pts) - 1):
                canvas.draw.line([pixel_pts[i], pixel_pts[i + 1]], fill=(35, 70, 60), width=2)
            canvas.draw.text((pixel_pts[0][0] + 5, pixel_pts[0][1]), "LINIA BRZEGOWA", fill=(45, 95, 80), font=get_font(8, bold=True))

        # Rotating Radar Beam Sweep with trailing glow
        sw_rad = math.radians(self.sweep_angle - 90)
        bx = cx + int(radar_r * math.cos(sw_rad))
        by = cy + int(radar_r * math.sin(sw_rad))
        # Main beam line
        canvas.draw.line([(cx, cy), (bx, by)], fill=(0, 220, 255), width=2)

        # Center Own Ship / Radar Base
        canvas.draw.ellipse([(cx - 4, cy - 4), (cx + 4, cy + 4)], fill=COLOR_FLIPPER_AMBER)
        canvas.draw.text((cx, cy + 12), "STACJA BAZOWA AIS", fill=COLOR_FLIPPER_AMBER, font=get_font(8, bold=True), anchor="mm")

        # -------------------------------------------------------------
        # Draw Ships / AIS Vessel Blips
        # -------------------------------------------------------------
        for idx, v in enumerate(self.vessels):
            # Scale NM coordinates to radar pixel radius
            vx = cx + int((v["x_nm"] / float(cur_range_nm)) * radar_r)
            vy = cy + int((v["y_nm"] / float(cur_range_nm)) * radar_r)

            # Check if vessel is within radar scope
            v_dist_px = math.sqrt((vx - cx)**2 + (vy - cy)**2)
            if v_dist_px > radar_r:
                continue

            v_col = VESSEL_COLORS.get(v["type"], (0, 210, 255))
            is_sel = (idx == self.selected_vessel_idx)

            # Draw Directional Vessel Chevron (▲ oriented to course)
            crs_rad = math.radians(v["course"] - 90)
            ch_len = 8 if not is_sel else 11
            ch_w = 5 if not is_sel else 7

            tip_x = vx + int(ch_len * math.cos(crs_rad))
            tip_y = vy + int(ch_len * math.sin(crs_rad))
            left_rad = crs_rad + math.radians(140)
            right_rad = crs_rad - math.radians(140)
            p1 = (vx + int(ch_w * math.cos(left_rad)), vy + int(ch_w * math.sin(left_rad)))
            p2 = (vx + int(ch_w * math.cos(right_rad)), vy + int(ch_w * math.sin(right_rad)))

            canvas.draw.polygon([(tip_x, tip_y), p1, (vx, vy), p2], fill=v_col, outline=(255, 255, 255) if is_sel else None)

            # Velocity Predictor Vector (Course over ground for next 10 minutes)
            if v["speed"] > 1.0:
                vec_len = max(6, int((v["speed"] / float(cur_range_nm)) * 25))
                vec_x = vx + int(vec_len * math.cos(crs_rad))
                vec_y = vy + int(vec_len * math.sin(crs_rad))
                canvas.draw.line([(vx, vy), (vec_x, vec_y)], fill=v_col, width=1)

            # Label on scope
            canvas.draw.text((vx + 10, vy - 6), v["name"].split()[0][:10], fill=COLOR_TEXT_PRIMARY if is_sel else (120, 160, 190), font=get_font(8, bold=is_sel))

            # Selected Target Reticle [ ]
            if is_sel:
                box_sz = 14
                canvas.draw.line([(vx - box_sz, vy - box_sz), (vx - box_sz + 5, vy - box_sz)], fill=COLOR_CYBER_CYAN, width=2)
                canvas.draw.line([(vx - box_sz, vy - box_sz), (vx - box_sz, vy - box_sz + 5)], fill=COLOR_CYBER_CYAN, width=2)
                canvas.draw.line([(vx + box_sz, vy - box_sz), (vx + box_sz - 5, vy - box_sz)], fill=COLOR_CYBER_CYAN, width=2)
                canvas.draw.line([(vx + box_sz, vy - box_sz), (vx + box_sz, vy - box_sz + 5)], fill=COLOR_CYBER_CYAN, width=2)
                canvas.draw.line([(vx - box_sz, vy + box_sz), (vx - box_sz + 5, vy + box_sz)], fill=COLOR_CYBER_CYAN, width=2)
                canvas.draw.line([(vx - box_sz, vy + box_sz), (vx - box_sz, vy + box_sz - 5)], fill=COLOR_CYBER_CYAN, width=2)
                canvas.draw.line([(vx + box_sz, vy + box_sz), (vx + box_sz - 5, vy + box_sz)], fill=COLOR_CYBER_CYAN, width=2)
                canvas.draw.line([(vx + box_sz, vy + box_sz), (vx + box_sz, vy + box_sz - 5)], fill=COLOR_CYBER_CYAN, width=2)

        # Radar Range Legend Bottom-Left
        canvas.draw.text((rx + 16, ry + rh - 25), f"Zasięg radaru: {cur_range_nm} NM  |  PPI 360°", fill=COLOR_CYBER_CYAN, font=get_font(10, bold=True))

        # -------------------------------------------------------------
        # Right Panel: AIS Vessel Inspector or Fleet Table (x=625, y=116, w=358, h=570)
        # -------------------------------------------------------------
        ix, iy, iw, ih = 625, 116, 358, 570
        canvas.draw.rounded_rectangle([(ix, iy), (ix + iw, iy + ih)], radius=10, fill=(14, 18, 26), outline=COLOR_BORDER, width=1)

        # Tab Navigation Header
        tab1_sel = (self.view_mode == 0)
        canvas.draw.rounded_rectangle([(ix + 12, iy + 10), (ix + 170, iy + 36)], radius=5,
                                      fill=(25, 38, 50) if tab1_sel else (18, 22, 30),
                                      outline=COLOR_CYBER_CYAN if tab1_sel else COLOR_BORDER, width=1)
        canvas.draw.text((ix + 26, iy + 16), "KARTA STATKU", fill=COLOR_TEXT_PRIMARY if tab1_sel else COLOR_TEXT_MUTED, font=get_font(11, bold=tab1_sel))

        canvas.draw.rounded_rectangle([(ix + 180, iy + 10), (ix + iw - 12, iy + 36)], radius=5,
                                      fill=(25, 38, 50) if not tab1_sel else (18, 22, 30),
                                      outline=COLOR_CYBER_CYAN if not tab1_sel else COLOR_BORDER, width=1)
        canvas.draw.text((ix + 200, iy + 16), f"LISTA FLOTY ({len(self.vessels)})", fill=COLOR_TEXT_PRIMARY if not tab1_sel else COLOR_TEXT_MUTED, font=get_font(11, bold=not tab1_sel))

        canvas.draw.line([(ix + 12, iy + 44), (ix + iw - 12, iy + 44)], fill=COLOR_BORDER, width=1)

        # Render active tab
        if self.view_mode == 0:
            self._render_vessel_card(canvas, ix, iy + 48, iw, ih - 48)
        else:
            self._render_fleet_table(canvas, ix, iy + 48, iw, ih - 48)

    # -----------------------------------------------------------------
    # RIGHT VIEW: DETAILED VESSEL INSPECTOR CARD
    # -----------------------------------------------------------------
    def _render_vessel_card(self, canvas, x, y, w, h):
        if not self.vessels:
            return

        self.selected_vessel_idx = max(0, min(len(self.vessels) - 1, self.selected_vessel_idx))
        v = self.vessels[self.selected_vessel_idx]
        v_col = VESSEL_COLORS.get(v["type"], (0, 210, 255))

        # Ship Name & Flag Banner
        canvas.draw.text((x + 16, y + 10), v["name"], fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))
        canvas.draw.text((x + 16, y + 32), f"Bandera: {v['flag']}  |  Znak: {v['call']}", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw_badge(x + w - 120, y + 8, v["type"].upper(), bg_color=(20, 35, 45), text_color=v_col)

        canvas.draw.line([(x + 16, y + 54), (x + w - 16, y + 54)], fill=COLOR_BORDER, width=1)

        # Kinematic Gauges Card: Speed & Course
        canvas.draw.rounded_rectangle([(x + 14, y + 64), (x + w - 14, y + 148)], radius=6, fill=(18, 24, 34), outline=(32, 44, 60))

        # Speed
        speed_kmh = v["speed"] * 1.852
        canvas.draw.text((x + 26, y + 74), "PRĘDKOŚĆ (SOG)", fill=COLOR_CYBER_CYAN, font=get_font(10, bold=True))
        canvas.draw.text((x + 26, y + 94), f"{v['speed']:.1f} kn", fill=COLOR_TEXT_PRIMARY, font=get_font(20, bold=True))
        canvas.draw.text((x + 26, y + 124), f"{speed_kmh:.1f} km/h", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # Course / Heading
        canvas.draw.text((x + 180, y + 74), "KURS RZECZYWISTY (COG)", fill=COLOR_FLIPPER_AMBER, font=get_font(10, bold=True))
        canvas.draw.text((x + 180, y + 94), f"{v['course']:03d}°", fill=COLOR_TEXT_PRIMARY, font=get_font(20, bold=True))

        cardinal = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        card_idx = int((v["course"] + 11.25) / 22.5) % 16
        canvas.draw.text((x + 180, y + 124), f"Kierunek: {cardinal[card_idx]}", fill=COLOR_FLIPPER_AMBER, font=get_font(10, bold=True))

        # Radar Tactical Range & Bearing
        canvas.draw.rounded_rectangle([(x + 14, y + 158), (x + w - 14, y + 218)], radius=6, fill=(18, 24, 34), outline=(32, 44, 60))
        canvas.draw.text((x + 26, y + 168), "POŁOŻENIE WZGLĘDEM BAZY", fill=COLOR_PHOSPHOR_GREEN, font=get_font(10, bold=True))
        dist_km = v["dist"] * 1.852
        canvas.draw.text((x + 26, y + 188), f"Odległość: {v['dist']:.1f} NM ({dist_km:.1f} km)  |  Namiar: {v['bearing']:03d}°", fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=True))

        # Vessel Physical Dimensions & AIS Specs
        canvas.draw.rounded_rectangle([(x + 14, y + 228), (x + w - 14, y + 338)], radius=6, fill=(18, 24, 34), outline=(32, 44, 60))
        canvas.draw.text((x + 26, y + 238), "DANE TECHNICZNE JEDNOSTKI:", fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=True))
        canvas.draw.text((x + 26, y + 262), f"• Wymiary (Dł x Szer): {v.get('dim', '150x22m')}", fill=COLOR_TEXT_SECONDARY, font=get_font(10))
        canvas.draw.text((x + 26, y + 284), f"• Zanurzenie (Draught): {v.get('draught', 7.5):.1f} m", fill=COLOR_TEXT_SECONDARY, font=get_font(10))
        canvas.draw.text((x + 26, y + 306), f"• Numer MMSI: {v['mmsi']}", fill=COLOR_CYBER_CYAN, font=get_font(10, bold=True))

        # Voyage Route & Destination
        canvas.draw.rounded_rectangle([(x + 14, y + 348), (x + w - 14, y + 428)], radius=6, fill=(20, 28, 38), outline=COLOR_BORDER)
        canvas.draw.text((x + 26, y + 358), "TRASA I PORT DOCELOWY:", fill=COLOR_FLIPPER_AMBER, font=get_font(10, bold=True))
        canvas.draw.text((x + 26, y + 380), f"Cel: {v.get('dest', 'BRAK DANYCH')}", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
        canvas.draw.text((x + 26, y + 404), f"Szacowany czas (ETA): {v.get('eta', '12:00')}", fill=COLOR_PHOSPHOR_GREEN, font=get_font(11))

        # Nautical Tip / Weather at bottom
        canvas.draw.line([(x + 14, y + 440), (x + w - 14, y + 440)], fill=COLOR_BORDER, width=1)
        canvas.draw.text((x + 16, y + 452), "METEOROLOGIA MORSKA:", fill=COLOR_CYBER_CYAN, font=get_font(10, bold=True))
        canvas.draw.text((x + 16, y + 472), f"Wiatr: {self.wind_speed_kn} kn SW ({self.wind_dir_deg}°)  |  Stan morza: 3°B", fill=COLOR_TEXT_SECONDARY, font=get_font(10))
        canvas.draw.text((x + 16, y + 494), "[D-Pad G/D]: Przełącz statek  |  [X]: Tabela floty", fill=COLOR_TEXT_MUTED, font=get_font(9))

    # -----------------------------------------------------------------
    # RIGHT VIEW: AIS FLEET LIST TABLE
    # -----------------------------------------------------------------
    def _render_fleet_table(self, canvas, x, y, w, h):
        canvas.draw.text((x + 16, y + 10), "JEDNOSTKA", fill=COLOR_TEXT_MUTED, font=get_font(10, bold=True))
        canvas.draw.text((x + 160, y + 10), "TYP", fill=COLOR_TEXT_MUTED, font=get_font(10, bold=True))
        canvas.draw.text((x + 245, y + 10), "WĘZŁY", fill=COLOR_TEXT_MUTED, font=get_font(10, bold=True))
        canvas.draw.text((x + 300, y + 10), "DYST.", fill=COLOR_TEXT_MUTED, font=get_font(10, bold=True))
        canvas.draw.line([(x + 14, y + 26), (x + w - 14, y + 26)], fill=COLOR_BORDER, width=1)

        row_y = y + 36
        for idx, v in enumerate(self.vessels):
            is_sel = (idx == self.selected_vessel_idx)
            v_col = VESSEL_COLORS.get(v["type"], (0, 210, 255))

            if is_sel:
                canvas.draw.rounded_rectangle([(x + 10, row_y - 2), (x + w - 10, row_y + 24)], radius=4, fill=(28, 42, 56), outline=COLOR_CYBER_CYAN, width=1)

            # Ship name
            sname = v["name"]
            if len(sname) > 16:
                sname = sname[:14] + ".."
            canvas.draw.text((x + 16, row_y + 3), sname, fill=COLOR_TEXT_PRIMARY if is_sel else COLOR_TEXT_SECONDARY, font=get_font(10, bold=is_sel))

            # Type badge
            canvas.draw.text((x + 160, row_y + 3), v["type"][:7], fill=v_col, font=get_font(9, bold=True))

            # Speed
            canvas.draw.text((x + 245, row_y + 3), f"{v['speed']:.1f}", fill=COLOR_TEXT_PRIMARY, font=get_font(10))

            # Distance
            canvas.draw.text((x + 300, row_y + 3), f"{v['dist']:.1f}M", fill=COLOR_FLIPPER_AMBER if is_sel else COLOR_TEXT_MUTED, font=get_font(10))

            row_y += 30
            if row_y > y + h - 40:
                break

        canvas.draw.line([(x + 14, y + h - 30), (x + w - 14, y + h - 30)], fill=COLOR_BORDER, width=1)
        canvas.draw.text((x + 16, y + h - 16), "[D-Pad G/D]: Wybór  |  [A / X]: Szczegóły", fill=COLOR_TEXT_MUTED, font=get_font(9))

    # -----------------------------------------------------------------
    # INPUT HANDLING
    # -----------------------------------------------------------------
    def handle_input(self, event: str) -> bool:
        # Switch Sea Zone / Port: L1 / R1
        if event in ("BTN_L1", "l1", "L1"):
            new_idx = (self.zone_idx - 1) % len(MARITIME_ZONES)
            self._load_zone_vessels(new_idx)
            return True
        elif event in ("BTN_R1", "r1", "R1"):
            new_idx = (self.zone_idx + 1) % len(MARITIME_ZONES)
            self._load_zone_vessels(new_idx)
            return True

        # Vessel Selection: D-Pad Up / Down
        elif event in ("DPAD_UP", "w", "W", "UP"):
            if self.vessels:
                self.selected_vessel_idx = (self.selected_vessel_idx - 1) % len(self.vessels)
            return True
        elif event in ("DPAD_DOWN", "s", "S", "DOWN"):
            if self.vessels:
                self.selected_vessel_idx = (self.selected_vessel_idx + 1) % len(self.vessels)
            return True

        # Range Zoom: D-Pad Left / Right
        elif event in ("DPAD_LEFT", "a", "LEFT"):
            self.range_idx = max(0, self.range_idx - 1)
            return True
        elif event in ("DPAD_RIGHT", "d", "RIGHT"):
            self.range_idx = min(len(self.range_levels) - 1, self.range_idx + 1)
            return True

        # Toggle Right Panel View: X
        elif event in ("BTN_X", "x", "X"):
            self.view_mode = 1 if self.view_mode == 0 else 0
            return True

        # Action / Center on Vessel: A
        elif event in ("BTN_A", "a", "A"):
            if self.view_mode == 1:
                self.view_mode = 0  # Switch to detailed card
            return True

        # Refresh AIS Feed: Y
        elif event in ("BTN_Y", "y", "Y"):
            self._load_zone_vessels(self.zone_idx)
            return True

        return False
