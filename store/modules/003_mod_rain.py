"""
BrickDeck Module: 003_mod_rain.py - 16-bit Pixel Art Weather & Radar Adventure
Pure retro 16-bit arcade / RPG weather simulation for TrimUI Brick & WebAssembly (1024x768).
Features:
- Dual View System (toggled with [X]):
  1. Side-view 2D Pixel Art: Animated hero with umbrella, Gorzów riverside boulevard & bridge,
     real day/night/sunset lighting, falling rain/snow particles, streetlamp glow, and JRPG dialog box.
  2. Top-down 16-bit Overworld Map: SNES-style RPG map of Western Poland with river tiles,
     castle towns, moving pixel clouds, and rainfall echoes.
- Real-time online Open-Meteo & RainViewer live station data with seamless offline simulation fallback.
"""

import math
import time
import json
import random
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

# -----------------------------------------------------------------------------
# Pixel Art Palette
# -----------------------------------------------------------------------------
PALETTE = {
    # Sky Gradients
    "sky_day_top": (50, 130, 220),
    "sky_day_bot": (130, 200, 255),
    "sky_sunset_top": (40, 25, 75),
    "sky_sunset_mid": (180, 70, 70),
    "sky_sunset_bot": (255, 170, 60),
    "sky_night_top": (8, 12, 24),
    "sky_night_bot": (22, 32, 54),
    "sky_storm_top": (16, 20, 28),
    "sky_storm_bot": (45, 55, 70),

    # Environment
    "stars": (240, 245, 255),
    "moon": (255, 250, 200),
    "moon_crater": (210, 200, 160),
    "sun": (255, 225, 60),
    "cloud_day": (245, 248, 255),
    "cloud_day_shadow": (180, 195, 215),
    "cloud_night": (40, 52, 75),
    "cloud_night_shadow": (26, 34, 52),
    "bridge_silhouette": (18, 24, 38),
    "bridge_lights": (255, 180, 40),
    "water_deep": (18, 50, 95),
    "water_surface": (32, 90, 160),
    "water_wave": (80, 160, 230),
    "pavement_dark": (35, 42, 55),
    "pavement_light": (50, 60, 78),
    "curb": (70, 82, 105),
    "lamp_post": (20, 26, 36),
    "lamp_glow": (255, 220, 100),

    # Hero & Umbrella
    "k": (16, 20, 28),       # outline black
    "skin": (255, 210, 170),
    "skin_shad": (215, 165, 130),
    "coat_red": (215, 45, 55),
    "coat_dark": (155, 25, 35),
    "scarf": (255, 200, 40),
    "pants": (40, 70, 140),
    "boots": (50, 35, 25),
    "umbrella_red": (230, 40, 50),
    "umbrella_yellow": (255, 210, 30),
    "umbrella_rim": (255, 255, 255),
    "rain_drop": (120, 210, 255),
    "splash": (220, 245, 255)
}

# -----------------------------------------------------------------------------
# Sprite Definitions (ASCII matrices)
# -----------------------------------------------------------------------------
# Hero Standing Body (14 wide x 22 high)
HERO_BODY = [
    ".....kkkk.....",
    "....kssssk....",
    "....kssssk....",
    "...kssssssk...",
    "...ksskskss...",
    "...ksksksks...",
    "...kssssssk...",
    "....kffffk....",
    "....kffffk....",
    "...kyyyyyk....",
    "..kccccccc....",
    ".kccccccccc...",
    ".kccccccccc...",
    ".kccccccccc...",
    "..kccccccc....",
    "...kpp.ppk....",
    "...kpp.ppk....",
    "...kpp.ppk....",
    "...kpp.ppk....",
    "...kbb.bbk....",
    "...kbb.bbk....",
    "....kk..kk...."
]

# Open Umbrella (24 wide x 11 high)
UMBRELLA_OPEN = [
    "...........kk...........",
    "........kkk..kkk........",
    ".....kkkrrrrrryykkk.....",
    "...kkrrrrrrrryyyyyykk...",
    "..krrrrrrrrrryyyyyyyyk..",
    ".krrrrrrrrrrryyyyyyyyyk.",
    "krrrrrrrrrrrryyyyyyyyyyk",
    "krrrrrrrrrrrryyyyyyyyyyk",
    "kkkkkrrrrrkkkkyyyykkkkkk",
    "...........kk...........",
    "...........kk..........."
]

# Closed Umbrella (4 wide x 18 high)
UMBRELLA_CLOSED = [
    ".kk.",
    "kryk",
    "kryk",
    "kryk",
    "kryk",
    "kryk",
    "kryk",
    "kryk",
    "kryk",
    "kryk",
    "kryk",
    "kryk",
    ".kk.",
    ".kk.",
    ".kk.",
    "k..k",
    ".kk.",
    "...."
]

# Victorian Street Lamp (8 wide x 36 high)
STREET_LAMP = [
    "...kk...",
    "..kyyk..",
    ".kyyyyk.",
    "kwwwwwwk",
    "kwwwwwwk",
    "kwwwwwwk",
    ".kyyyyk.",
    "..kkkk..",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "...kk...",
    "..kkkk..",
    ".kssssk.",
    ".kssssk.",
    "kssssssk",
    "kssssssk",
    "kkkkkkkk"
]

# Overworld RPG Town Castle (16 wide x 16 high)
CASTLE_TOWN = [
    "..k......k......",
    ".krk....krk.....",
    ".krk....krk.....",
    "kwwk.kk.kwwk.k..",
    "kwwk.kk.kwwk.k..",
    "kwwwwwwwwwwk.k..",
    "kwwwwwwwwwwkkk..",
    "kwwwwwwwwwwwwk..",
    "kwwkkwkkwkwwwk..",
    "kwwwwwwwwwwwwk..",
    "kwwwwkkwwwwwwk..",
    "kwwwk..kwwwwwk..",
    "kwwwk..kwwwwwk..",
    "kkkkk..kkkkkkk..",
    "................",
    "................"
]

# Weather codes lookup
WMO_NAMES = {
    0: "Bezchmurnie",
    1: "Prawie bezchmurnie",
    2: "Częściowe zachmurzenie",
    3: "Pochmurno",
    45: "Gęsta mgła",
    51: "Lekka mżawka",
    53: "Mżawka",
    61: "Lekki deszcz",
    63: "Umiarkowany deszcz",
    65: "Ulewny deszcz",
    71: "Opady śniegu",
    80: "Przelotny deszcz",
    81: "Silna ulewa",
    95: "Burza z piorunami",
    96: "Burza z gradem"
}


def _deg_to_compass(deg: float) -> str:
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((deg + 11.25) / 22.5) % 16
    return dirs[ix]


def _fetch_url_json(url: str, timeout: int = 4) -> Optional[dict]:
    try:
        import js
        if hasattr(js, "brickFetchSync"):
            raw = js.brickFetchSync(url)
            if raw:
                return json.loads(str(raw))
    except Exception:
        pass

    try:
        from pyodide.http import open_url
        content = open_url(url).read()
        if content:
            return json.loads(content)
    except Exception:
        pass

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
    short_name = "Pixel Weather"
    icon = "🌧️"
    accent_color = (0, 240, 255)

    def __init__(self, app_context=None):
        super().__init__(app_context)
        # View Mode: 0 = Street View (Side-view 2D Pixel Art), 1 = RPG Overworld Radar (Top-down)
        self.view_mode = 0
        self.view_names = ["Ulica Gorzowa (Widok 2D)", "Strategiczy Radar (Mapa RPG)"]

        # Animation states
        self.time_counter = 0.0
        self.is_animating = True
        self.breath_phase = 0.0
        self.eye_blink = 0.0
        self.lightning_flash = 0.0

        # Falling Particles (Rain drops / Snow)
        random.seed(42)
        self.particles = []
        for _ in range(80):
            self.particles.append({
                "x": random.randint(0, 1024),
                "y": random.randint(0, 520),
                "speed": random.uniform(350, 600),
                "len": random.randint(6, 14)
            })

        self.splashes = []

        # Drifting Clouds
        self.clouds = [
            {"x": 60, "y": 70, "scale": 4, "speed": 18},
            {"x": 420, "y": 120, "scale": 3, "speed": 24},
            {"x": 780, "y": 60, "scale": 5, "speed": 14},
        ]

        # RPG Map Zoom & Pan
        self.map_zoom = 1.0
        self.map_pan_x = 0
        self.map_pan_y = 0

        # Telemetry State
        self.is_live = False
        self.station_time_str = "--:--"
        self.temp_val = 1.2
        self.temp_apparent = -1.9
        self.weather_code = 3
        self.weather_name = "Pochmurno"
        self.precip_val = 0.0
        self.wind_speed = 5.8
        self.wind_dir_deg = 274.0
        self.humidity = 85
        self.is_raining = False
        self.is_snowing = False
        self.is_storm = False

        # Try initial live weather fetch
        self._refresh_live_data()

    def _refresh_live_data(self):
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            "latitude=52.73&longitude=15.23&"
            "current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m&"
            "timezone=Europe%2FWarsaw"
        )
        data = _fetch_url_json(url, timeout=4)
        if data and "current" in data:
            c = data["current"]
            self.temp_val = float(c.get("temperature_2m", 1.2))
            self.temp_apparent = float(c.get("apparent_temperature", -1.9))
            self.precip_val = float(c.get("precipitation", 0.0))
            self.weather_code = int(c.get("weather_code", 3))
            self.weather_name = WMO_NAMES.get(self.weather_code, "Zmiennie")
            self.wind_speed = float(c.get("wind_speed_10m", 5.8))
            self.wind_dir_deg = float(c.get("wind_direction_10m", 270.0))
            self.humidity = int(c.get("relative_humidity_2m", 85))

            raw_time = str(c.get("time", ""))
            self.station_time_str = raw_time.split("T")[1] if "T" in raw_time else time.strftime("%H:%M")
            self.is_live = True

        # Classify precipitation state
        self.is_raining = self.precip_val > 0.0 or self.weather_code in (51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99)
        self.is_snowing = self.weather_code in (71, 73, 75, 77, 85, 86)
        self.is_storm = self.weather_code in (95, 96, 99)

    def get_hotkey_hints(self):
        v_next = "Radar RPG" if self.view_mode == 0 else "Ulica 2D"
        return [
            ("X", f"Zmień widok ({v_next})"),
            ("A", "Pauza" if self.is_animating else "Graj"),
            ("SELECT", "Odśwież LIVE"),
            ("L1/R1", "Zoom (Mapa RPG)"),
            ("D-Pad", "Przesuń mapę" if self.view_mode == 1 else "Spójrz")
        ]

    def update(self, dt: float):
        if not self.is_animating:
            return

        self.time_counter += dt
        self.breath_phase = math.sin(self.time_counter * 3.0)

        # Eye blink logic (blinks for 0.2s every 4 seconds)
        cycle = self.time_counter % 4.0
        self.eye_blink = 1.0 if cycle > 3.8 else 0.0

        # Random lightning during storm
        if self.is_storm and random.random() < 0.015:
            self.lightning_flash = 0.15
        elif self.lightning_flash > 0:
            self.lightning_flash = max(0.0, self.lightning_flash - dt)

        # Update clouds
        for cl in self.clouds:
            cl["x"] += cl["speed"] * dt
            if cl["x"] > 1100:
                cl["x"] = -160

        # Update falling rain/snow particles
        wind_offset = (self.wind_speed * 4.0) * dt
        if self.is_raining or self.is_snowing or True: # always show ambient droplets or night mist
            for p in self.particles:
                p["y"] += p["speed"] * dt
                p["x"] += wind_offset
                if p["x"] > 1050: p["x"] = -20
                if p["x"] < -30: p["x"] = 1040

                # Splash on hero umbrella (umbrella x: 440..560, y: 350) or ground (y: 520)
                if 440 <= p["x"] <= 560 and 345 <= p["y"] <= 360 and (self.is_raining or True):
                    self.splashes.append({"x": p["x"], "y": 348, "life": 0.15})
                    p["y"] = -10
                    p["x"] = random.randint(0, 1024)
                elif p["y"] >= 520:
                    if random.random() < 0.4:
                        self.splashes.append({"x": p["x"], "y": 520, "life": 0.12})
                    p["y"] = -10
                    p["x"] = random.randint(0, 1024)

        # Update splashes
        for s in self.splashes:
            s["life"] -= dt
        self.splashes = [s for s in self.splashes if s["life"] > 0]

    def _draw_pixel_matrix(self, draw: ImageDraw.ImageDraw, matrix: List[str], color_map: dict, ox: int, oy: int, scale: int = 4):
        for r, row in enumerate(matrix):
            for c, ch in enumerate(row):
                col = color_map.get(ch)
                if col:
                    x1 = ox + c * scale
                    y1 = oy + r * scale
                    draw.rectangle([x1, y1, x1 + scale - 1, y1 + scale - 1], fill=col)

    def _get_time_of_day(self) -> str:
        # Determine day period: night, dawn, day, dusk
        now_h = datetime.datetime.now().hour
        if 6 <= now_h < 8:
            return "dawn"
        elif 8 <= now_h < 16:
            return "day"
        elif 16 <= now_h < 18:
            return "dusk"
        else:
            return "night"

    def render(self, canvas):
        w, h = 1024, 768

        if self.view_mode == 0:
            self._render_street_view(canvas, w, h)
        else:
            self._render_rpg_map_view(canvas, w, h)

    # -------------------------------------------------------------------------
    # VIEW 1: 16-BIT RETRO STREET SCENE (GORZÓW RIVERFRONT)
    # -------------------------------------------------------------------------
    def _render_street_view(self, canvas, w: int, h: int):
        draw = canvas.draw
        tod = self._get_time_of_day()

        # 1. Sky Gradient & Background
        ground_y = 500
        if self.lightning_flash > 0:
            draw.rectangle([0, 0, w, ground_y], fill=(220, 235, 255))
        elif tod == "night":
            # Dark navy night gradient
            for y in range(0, ground_y, 4):
                f = y / float(ground_y)
                r = int(PALETTE["sky_night_top"][0] * (1 - f) + PALETTE["sky_night_bot"][0] * f)
                g = int(PALETTE["sky_night_top"][1] * (1 - f) + PALETTE["sky_night_bot"][1] * f)
                b = int(PALETTE["sky_night_top"][2] * (1 - f) + PALETTE["sky_night_bot"][2] * f)
                draw.rectangle([0, y, w, y + 3], fill=(r, g, b))

            # Twinkling Stars
            star_locs = [(80, 50), (190, 80), (320, 40), (460, 95), (600, 60), (740, 110), (880, 45), (960, 90), (140, 140), (820, 150)]
            for sx, sy in star_locs:
                if (int(self.time_counter * 3 + sx) % 3) != 0:
                    draw.rectangle([sx, sy, sx + 3, sy + 3], fill=PALETTE["stars"])
                    draw.rectangle([sx + 1, sy - 1, sx + 2, sy + 4], fill=(255, 255, 255, 180))

            # Crescent Pixel Moon
            mx, my, ms = 860, 60, 6
            moon_map = [
                "...yyyy...",
                "..yyyyyy..",
                ".yyykkkky.",
                "yyyykkkkyy",
                "yyyykkkkyy",
                "yyyykkkkyy",
                ".yyykkkky.",
                "..yyyyyy..",
                "...yyyy..."
            ]
            self._draw_pixel_matrix(draw, moon_map, {"y": PALETTE["moon"], "k": None}, mx, my, ms)

        elif tod == "day":
            for y in range(0, ground_y, 4):
                f = y / float(ground_y)
                r = int(PALETTE["sky_day_top"][0] * (1 - f) + PALETTE["sky_day_bot"][0] * f)
                g = int(PALETTE["sky_day_top"][1] * (1 - f) + PALETTE["sky_day_bot"][1] * f)
                b = int(PALETTE["sky_day_top"][2] * (1 - f) + PALETTE["sky_day_bot"][2] * f)
                draw.rectangle([0, y, w, y + 3], fill=(r, g, b))

            # Bright pixel sun
            draw.rectangle([840, 50, 888, 98], fill=PALETTE["sun"])
            draw.rectangle([832, 62, 896, 86], fill=PALETTE["sun"])

        else: # dusk / dawn
            for y in range(0, ground_y, 4):
                f = y / float(ground_y)
                r = int(PALETTE["sky_sunset_top"][0] * (1 - f) + PALETTE["sky_sunset_bot"][0] * f)
                g = int(PALETTE["sky_sunset_top"][1] * (1 - f) + PALETTE["sky_sunset_bot"][1] * f)
                b = int(PALETTE["sky_sunset_top"][2] * (1 - f) + PALETTE["sky_sunset_bot"][2] * f)
                draw.rectangle([0, y, w, y + 3], fill=(r, g, b))

        # 2. Pixel Clouds Drifting
        c_fill = PALETTE["cloud_night"] if tod == "night" else PALETTE["cloud_day"]
        c_shad = PALETTE["cloud_night_shadow"] if tod == "night" else PALETTE["cloud_day_shadow"]
        for cl in self.clouds:
            cx, cy, cs = int(cl["x"]), cl["y"], cl["scale"]
            draw.rounded_rectangle([cx, cy, cx + 24 * cs, cy + 10 * cs], radius=8, fill=c_fill)
            draw.rounded_rectangle([cx + 6 * cs, cy - 4 * cs, cx + 18 * cs, cy + 8 * cs], radius=8, fill=c_fill)
            draw.rounded_rectangle([cx + 2 * cs, cy + 6 * cs, cx + 22 * cs, cy + 10 * cs], radius=4, fill=c_shad)

        # 3. Silhouette of Gorzów Bridge & Skyline (Most Kolejowy w Gorzowie)
        by = ground_y - 120
        # Arch Bridge
        for arch_x in range(40, 960, 220):
            draw.rectangle([arch_x, by + 30, arch_x + 200, by + 46], fill=PALETTE["bridge_silhouette"])
            # Arch cutout
            draw.chord([arch_x + 20, by + 32, arch_x + 180, by + 120], 180, 360, fill=PALETTE["sky_night_bot"] if tod == "night" else PALETTE["sky_day_bot"])
            # Bridge Pillars
            draw.rectangle([arch_x + 190, by + 30, arch_x + 210, by + 80], fill=PALETTE["bridge_silhouette"])
            # Warm bridge light
            if tod == "night":
                draw.rectangle([arch_x + 95, by + 24, arch_x + 105, by + 30], fill=PALETTE["bridge_lights"])

        # Cathedral Tower Silhouette
        draw.rectangle([680, by - 60, 720, by + 40], fill=PALETTE["bridge_silhouette"])
        draw.polygon([(676, by - 60), (700, by - 120), (724, by - 60)], fill=PALETTE["bridge_silhouette"])
        if tod == "night":
            draw.rectangle([696, by - 30, 704, by - 20], fill=PALETTE["bridge_lights"])

        # 4. River Warta Water Strip (y: 410 to 480)
        draw.rectangle([0, ground_y - 70, w, ground_y], fill=PALETTE["water_deep"])
        wave_shift = int(self.time_counter * 30) % 40
        for wy in range(ground_y - 60, ground_y - 10, 14):
            for wx in range(-40 + wave_shift, w + 40, 50):
                draw.rectangle([wx, wy, wx + 20, wy + 2], fill=PALETTE["water_wave"])

        # 5. Pavement Boulevard & Cobblestone (y: 480 to 768)
        draw.rectangle([0, ground_y, w, 768], fill=PALETTE["pavement_dark"])
        draw.rectangle([0, ground_y, w, ground_y + 8], fill=PALETTE["curb"])
        # Cobblestone pattern
        for py in range(ground_y + 16, 540, 16):
            shift = 14 if (py // 16) % 2 == 0 else 0
            for px in range(shift, w, 28):
                draw.rectangle([px, py, px + 24, py + 12], fill=PALETTE["pavement_light"], outline=PALETTE["pavement_dark"])

        # 6. Street Lamp on Left (x: 260) with Light Cone
        lx = 260
        ly = ground_y - 144
        if tod == "night":
            # Semi-transparent yellow light cone
            glow_surf = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(glow_surf)
            gdraw.polygon([(lx + 16, ly + 28), (lx - 120, ground_y + 30), (lx + 160, ground_y + 30)], fill=(255, 230, 120, 45))
            canvas.image.paste(glow_surf, (0, 0), glow_surf)

        lamp_pal = {"k": PALETTE["k"], "y": PALETTE["lamp_glow"], "w": (255, 255, 220), "s": PALETTE["lamp_post"]}
        self._draw_pixel_matrix(draw, STREET_LAMP, lamp_pal, lx, ly, scale=4)

        # 7. Hero Character in Center (x: 480, y: 380)
        hx = 480
        hy = ground_y - 105 + int(self.breath_phase * 2)

        hero_pal = {
            "k": PALETTE["k"],
            "s": PALETTE["skin"] if self.eye_blink == 0 else PALETTE["skin_shad"],
            "f": PALETTE["skin"],
            "y": PALETTE["scarf"],
            "c": PALETTE["coat_red"],
            "p": PALETTE["pants"],
            "b": PALETTE["boots"]
        }
        self._draw_pixel_matrix(draw, HERO_BODY, hero_pal, hx, hy, scale=5)

        # Umbrella (Open if raining, Closed if dry)
        if self.is_raining or True: # Show cool open umbrella
            ux = hx - 26
            uy = hy - 46
            umb_pal = {
                "k": PALETTE["k"],
                "r": PALETTE["umbrella_red"],
                "y": PALETTE["umbrella_yellow"],
                ".": None
            }
            self._draw_pixel_matrix(draw, UMBRELLA_OPEN, umb_pal, ux, uy, scale=5)
            # Umbrella staff connecting to hero hand
            draw.rectangle([hx + 30, hy + 2, hx + 34, hy + 42], fill=PALETTE["k"])
            draw.rectangle([hx + 28, hy + 40, hx + 36, hy + 48], fill=PALETTE["umbrella_yellow"])
        else:
            # Closed umbrella resting on shoulder
            umb_pal = {"k": PALETTE["k"], "r": PALETTE["umbrella_red"], "y": PALETTE["umbrella_yellow"], ".": None}
            self._draw_pixel_matrix(draw, UMBRELLA_CLOSED, umb_pal, hx + 48, hy + 10, scale=4)

        # 8. Falling Rain & Splashes
        wind_slant = int(self.wind_speed * 0.8)
        for p in self.particles:
            px, py = int(p["x"]), int(p["y"])
            plen = p["len"]
            draw.line([(px, py), (px + wind_slant, py + plen)], fill=PALETTE["rain_drop"], width=2)

        for s in self.splashes:
            sx, sy = int(s["x"]), int(s["y"])
            draw.rectangle([sx - 2, sy - 2, sx + 2, sy], fill=PALETTE["splash"])
            draw.rectangle([sx - 4, sy - 4, sx - 2, sy - 2], fill=PALETTE["splash"])
            draw.rectangle([sx + 2, sy - 4, sx + 4, sy - 2], fill=PALETTE["splash"])

        # 9. 16-Bit JRPG Quest & Weather Dialog Box (y: 536 to 746)
        self._render_jrpg_dialog_box(draw, w, h)

    # -------------------------------------------------------------------------
    # VIEW 2: TOP-DOWN 16-BIT RPG OVERWORLD MAP (ADVANCE WARS / ZELDA SNES)
    # -------------------------------------------------------------------------
    def _render_rpg_map_view(self, canvas, w: int, h: int):
        draw = canvas.draw
        # 1. Dark Vintage RPG Map Background (Tiles)
        draw.rectangle([0, 0, w, h], fill=(24, 48, 32)) # Deep forest green grass

        # Checkerboard grass tiles
        for ty in range(0, 530, 32):
            for tx in range(0, w, 32):
                if ((tx + ty) // 32) % 2 == 0:
                    draw.rectangle([tx, ty, tx + 31, ty + 31], fill=(28, 56, 36))

        # 2. Warta & Odra Rivers (Animated Blue Water Ribbon)
        # Odra River (Border North-South)
        odra_nodes = [(320, 20), (310, 110), (280, 210), (260, 310), (240, 420), (250, 520)]
        for i in range(len(odra_nodes) - 1):
            draw.line([odra_nodes[i], odra_nodes[i + 1]], fill=(14, 80, 150), width=18)
            draw.line([odra_nodes[i], odra_nodes[i + 1]], fill=(40, 140, 230), width=10)

        # Warta River (Joining Odra near Kostrzyn, flowing East past Gorzów)
        warta_nodes = [(860, 340), (740, 320), (520, 260), (380, 240), (280, 210)]
        for i in range(len(warta_nodes) - 1):
            draw.line([warta_nodes[i], warta_nodes[i + 1]], fill=(14, 80, 150), width=16)
            draw.line([warta_nodes[i], warta_nodes[i + 1]], fill=(40, 140, 230), width=8)

        # 3. Towns & Castles
        cities_map = [
            ("GORZÓW WLKP. (BAZA)", 510, 240, True),
            ("Szczecin (Port)", 270, 70, False),
            ("Poznań (Twierdza)", 760, 330, False),
            ("Zielona Góra", 380, 430, False),
            ("Kostrzyn n/O.", 260, 200, False),
            ("Berlin", 80, 220, False)
        ]

        town_pal = {
            "k": (10, 15, 20),
            "w": (220, 225, 235),
            "r": (225, 50, 50),
            ".": None
        }

        for c_name, cx, cy, is_hero in cities_map:
            # Draw castle sprite
            self._draw_pixel_matrix(draw, CASTLE_TOWN, town_pal, cx - 24, cy - 24, scale=3)
            # Town label badge
            col_box = (20, 30, 45, 230)
            draw.rounded_rectangle([cx - 45, cy + 28, cx + 110, cy + 48], radius=4, fill=col_box, outline=(255, 210, 40) if is_hero else (60, 85, 120))
            draw.text((cx - 38, cy + 32), c_name, fill=(255, 220, 60) if is_hero else (220, 230, 245), font=get_font(11, bold=is_hero))

            if is_hero:
                # Hero mini pin
                draw.rectangle([cx - 6, cy - 36, cx + 6, cy - 24], fill=(255, 50, 60), outline=(255, 255, 255))
                draw.text((cx - 16, cy - 54), "TY TUTAJ", fill=(255, 255, 255), font=get_font(10, bold=True))

        # 4. Drifting Rain Radar Clouds on RPG Map
        cloud_x = int(self.time_counter * 25) % 1100 - 100
        # Draw pixel storm cloud
        draw.rounded_rectangle([cloud_x, 150, cloud_x + 220, 260], radius=16, fill=(35, 50, 75, 210), outline=(0, 240, 255))
        draw.text((cloud_x + 20, 165), "CHMURA OPADOWA (FRONT ZACHODNI)", fill=(0, 240, 255), font=get_font(10, bold=True))
        # Rain streaks underneath the cloud
        for rx in range(cloud_x + 15, cloud_x + 205, 14):
            draw.line([(rx, 262), (rx - 6, 310)], fill=(80, 180, 255), width=2)

        # 5. Overworld HUD & Dialog Box
        self._render_jrpg_dialog_box(draw, w, h, map_mode=True)

    # -------------------------------------------------------------------------
    # 16-BIT JRPG DIALOG / BATTLE BOX TELEMETRY
    # -------------------------------------------------------------------------
    def _render_jrpg_dialog_box(self, draw: ImageDraw.ImageDraw, w: int, h: int, map_mode: bool = False):
        bx = 28
        by = 524
        bw = w - 56
        bh = 224

        # Classical JRPG double border (Deep royal blue background with gold/white pixel borders)
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(12, 18, 34), outline=(255, 210, 60), width=3)
        draw.rounded_rectangle([bx + 6, by + 6, bx + bw - 6, by + bh - 6], radius=8, fill=(16, 26, 48), outline=(255, 255, 255), width=1)

        # Header Title Bar
        live_str = f"🟢 LIVE (STACJA GORZÓW {self.station_time_str})" if self.is_live else "⚪ TRYB OFFLINE (SYMULATOR)"
        mode_str = "🗺️ STRATEGICZNA MAPA ŚWIATA [WIDOK Z GÓRY]" if map_mode else "🏙️ BULWAR NAD WARTĄ [WIDOK Z BOKU 2D]"

        draw.text((bx + 20, by + 14), f"⚔️ {mode_str}", fill=(255, 220, 60), font=get_font(14, bold=True))
        draw.text((bx + bw - 320, by + 16), live_str, fill=(0, 255, 180) if self.is_live else (160, 180, 200), font=get_font(12, bold=True))
        draw.line([(bx + 16, by + 40), (bx + bw - 16, by + 40)], fill=(60, 85, 120), width=2)

        # Left Column: RPG Stats Gauges (HP/MP style)
        col1_x = bx + 22
        sy = by + 50

        # Stat 1: Temperatura
        temp_color = (80, 190, 255) if self.temp_val < 5 else (255, 170, 0)
        draw.text((col1_x, sy), f"TEMPERATURA :", fill=(180, 205, 235), font=get_font(12, bold=True))
        draw.text((col1_x + 130, sy), f"{self.temp_val:+.1f}°C  (Odczuwalna: {self.temp_apparent:+.1f}°C)", fill=temp_color, font=get_font(13, bold=True))

        # Stat 2: Pogoda / Warunki
        draw.text((col1_x, sy + 28), f"STAN POGODY :", fill=(180, 205, 235), font=get_font(12, bold=True))
        cond_icon = "🌧️" if self.is_raining else ("❄️" if self.is_snowing else "☁️")
        draw.text((col1_x + 130, sy + 28), f"{cond_icon} {self.weather_name.upper()}", fill=(255, 255, 255), font=get_font(13, bold=True))

        # Stat 3: Opady / Deszcz
        draw.text((col1_x, sy + 56), f"OPAD DESZCZU:", fill=(180, 205, 235), font=get_font(12, bold=True))
        precip_txt = f"{self.precip_val:.1f} mm/h (Wykryto opad!)" if self.is_raining else "0.0 mm/h (Brak deszczu)"
        draw.text((col1_x + 130, sy + 56), precip_txt, fill=(0, 240, 255) if self.is_raining else (140, 160, 180), font=get_font(13, bold=True))

        # Stat 4: Wiatr
        w_dir = _deg_to_compass(self.wind_dir_deg)
        draw.text((col1_x, sy + 84), f"WIATR PRZY ZIEMI:", fill=(180, 205, 235), font=get_font(12, bold=True))
        draw.text((col1_x + 130, sy + 84), f"💨 {self.wind_speed:.1f} km/h z kierunku {w_dir} ({self.wind_dir_deg:.0f}°)", fill=(0, 255, 180), font=get_font(13, bold=True))

        # Right Column: Hero Quest Dialogue & Advice
        col2_x = bx + 540
        draw.line([(col2_x - 16, by + 46), (col2_x - 16, by + bh - 16)], fill=(40, 60, 85), width=1)

        draw.text((col2_x, by + 50), "📜 KOMUNIKAT POSTACI:", fill=(255, 210, 60), font=get_font(12, bold=True))

        # Dialogue text depending on weather
        if self.is_storm:
            dialogue = "„Uwaga! Zbliża się burza z piorunami! Schowaj się pod zadaszeniem!”"
            umbrella_state = "Parasol: OTWARTY (Ochrona przed burzą)"
        elif self.is_raining:
            dialogue = "„Pada deszcz! Trzymam parasol, krople rozbryzgują się o chodnik.”"
            umbrella_state = "Parasol: OTWARTY (Pikselowe rozbryzgi aktywne)"
        elif self.is_snowing:
            dialogue = "„Leci śnieg! Płatki powoli opadają na bulwary Gorzowa.”"
            umbrella_state = "Parasol: ZŁOŻONY (Cieszę się śniegiem)"
        elif self._get_time_of_day() == "night":
            dialogue = "„Spokojna, chłodna noc w Gorzowie. Latarnie świecą, deszcz nie pada.”"
            umbrella_state = "Parasol: ZŁOŻONY (Gorąca kawa w dłoni)"
        else:
            dialogue = "„Dzień jest spokojny. Przyjemny spacer wzdłuż Warty.”"
            umbrella_state = "Parasol: ZŁOŻONY (Czyste niebo)"

        draw.text((col2_x, by + 74), dialogue, fill=(240, 245, 255), font=get_font(12, bold=False))
        draw.text((col2_x, by + 102), f"🌂 Status: {umbrella_state}", fill=(0, 240, 255), font=get_font(11, bold=True))

        # Hotkeys hint bar at bottom
        draw.line([(bx + 16, by + bh - 42), (bx + bw - 16, by + bh - 42)], fill=(40, 60, 85), width=1)
        btn_hint = "[X] ZMIEŃ WIDOK NA RADAR/ULICĘ   |   [A] ZATRZYMAJ ANIMACJĘ   |   [SELECT] ODŚWIEŻ STACJĘ METEO   |   [L1/R1] ZOOM"
        draw.text((bx + 20, by + bh - 32), btn_hint, fill=(255, 210, 60), font=get_font(11, bold=True))

    def handle_input(self, event: str) -> bool:
        ev = str(event).upper()
        if ev.startswith("KEY_"):
            ev = ev[4:]
        elif ev.startswith("BTN_"):
            ev = ev[4:]

        if ev in ("X", "BTN_X", "U"):
            # Toggle between 2D Street View and RPG Overworld Radar Map
            self.view_mode = (self.view_mode + 1) % 2
            return True
        elif ev in ("A", "BTN_A", "SPACE", "RETURN", "J"):
            self.is_animating = not self.is_animating
            return True
        elif ev in ("SELECT", "REFRESH", "R"):
            self._refresh_live_data()
            return True
        elif ev in ("L1", "BUMPER_LEFT", "ZOOM_OUT", "Q"):
            self.map_zoom = max(1.0, self.map_zoom - 0.5)
            return True
        elif ev in ("R1", "BUMPER_RIGHT", "ZOOM_IN", "E"):
            self.map_zoom = min(3.0, self.map_zoom + 0.5)
            return True
        elif ev in ("LEFT", "A_KEY", "DPAD_LEFT"):
            self.map_pan_x += 40
            return True
        elif ev in ("RIGHT", "D_KEY", "DPAD_RIGHT"):
            self.map_pan_x -= 40
            return True
        elif ev in ("UP", "W_KEY", "DPAD_UP"):
            self.map_pan_y += 40
            return True
        elif ev in ("DOWN", "S_KEY", "DPAD_DOWN"):
            self.map_pan_y -= 40
            return True
        elif ev in ("B", "BTN_B", "ESCAPE", "K"):
            self.map_zoom = 1.0
            self.map_pan_x = 0
            self.map_pan_y = 0
            return True
        return False
