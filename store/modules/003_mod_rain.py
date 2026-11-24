"""
BrickDeck Module: 003_mod_rain.py - 16-bit Pixel Art Weather Adventure (Gorzów Bulwary)
Cozy 16-bit arcade / JRPG weather simulation for TrimUI Brick & WebAssembly (1024x768).
Features:
- D-Pad Walking Engine:
  - In RPG Overworld Map [X]: Freely walk around Western Poland in 4 directions!
    Discover towns (Gorzów, Szczecin, Poznań, Zielona Góra, Kostrzyn, Berlin).
    Walk under the drifting radar rain cloud to trigger an umbrella and rainfall!
    See animated windmills spin with real wind and boats drift on the Warta river!
  - In 2D Street View: Walk left and right along the Gorzów boulevard!
- Real-time Open-Meteo & IMGW Gorzów station data with offline simulation fallback.
"""

import math
import time
import json
import random
import datetime
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw

from core.module_base import BaseModule
from core.canvas import get_font

# -----------------------------------------------------------------------------
# Color Palette
# -----------------------------------------------------------------------------
C_NIGHT_SKY_TOP = (8, 12, 26)
C_NIGHT_SKY_MID = (18, 28, 54)
C_NIGHT_SKY_BOT = (32, 46, 78)

C_DAY_SKY_TOP = (45, 120, 215)
C_DAY_SKY_BOT = (140, 205, 255)

C_STARS = (245, 250, 255)
C_MOON = (255, 245, 190)

C_SILHOUETTE_FAR = (14, 20, 34)
C_BRIDGE_BRICK = (32, 42, 62)
C_BRIDGE_LIGHT = (255, 185, 45)
C_TRAIN_LIGHT = (255, 215, 80)

C_WATER_DARK = (14, 38, 72)
C_WATER_MID = (24, 62, 115)
C_WATER_RIPPLE = (50, 120, 195)
C_WATER_REFLECT = (255, 200, 70)

C_COBBLE_DARK = (28, 34, 46)
C_COBBLE_MID = (42, 50, 68)
C_CURB = (85, 98, 125)
C_RAILING = (16, 22, 32)

C_LAMP_IRON = (18, 24, 34)
C_LAMP_GOLD = (255, 220, 90)

C_HERO_SKIN = (255, 212, 175)
C_HERO_HAIR = (55, 38, 28)
C_HERO_BEANIE = (220, 48, 56)
C_HERO_COAT = (36, 68, 125)
C_HERO_COAT_LIGHT = (52, 92, 165)
C_HERO_SCARF = (255, 195, 35)
C_HERO_PANTS = (28, 38, 56)
C_HERO_BOOTS = (72, 48, 32)

C_MUG = (245, 245, 250)
C_MUG_COFFEE = (90, 50, 30)

C_UMB_RED = (225, 42, 52)
C_UMB_YELLOW = (255, 205, 35)
C_UMB_STAFF = (22, 28, 38)

C_RAIN = (130, 210, 255)
C_SPLASH = (225, 245, 255)

# -----------------------------------------------------------------------------
# Sprites
# -----------------------------------------------------------------------------
SPRITE_LAMP = [
    "....kkkk....",
    "...kyyyyk...",
    "..kyyyyyyk..",
    ".kwwwwwwwwk.",
    ".kwwwwwwwwk.",
    ".kwwwwwwwwk.",
    ".kwwwwwwwwk.",
    "..kyyyyyyk..",
    "...kyyyyk...",
    "....kkkk....",
    ".....kk.....",
    "....kkkk....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    ".....kk.....",
    "....kkkk....",
    "...kssssk...",
    "..kssssssk..",
    ".kssssssssk.",
    "kssssssssssk",
    "kkkkkkkkkkkk"
]

SPRITE_UMB_FOLDED = [
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
    "kryk",
    "kryk",
    "kryk",
    "kryk",
    ".kk.",
    ".kk.",
    ".kk.",
    ".kk.",
    "k..k",
    "k..k",
    ".kk.",
    "....",
    "....",
    "....",
    "....",
    "...."
]

SPRITE_UMB_OPEN = [
    ".............kk.............",
    "..........kkk..kkk..........",
    ".......kkkrrrrrryykkk.......",
    ".....kkrrrrrrrryyyyyykk.....",
    "...kkrrrrrrrrrryyyyyyyykk...",
    "..krrrrrrrrrrrryyyyyyyyyyk..",
    ".krrrrrrrrrrrrryyyyyyyyyyyk.",
    ".krrrrrrrrrrrrryyyyyyyyyyyk.",
    "krrrrrrrrrrrrrryyyyyyyyyyyyk",
    "krrrrrrrrrrrrrryyyyyyyyyyyyk",
    "kkkkkrrrrrkkkkkkyyyyykkkkkkk",
    ".............kk.............",
    ".............kk.............",
    ".............kk............."
]

PORTRAIT_HERO_COZY = [
    "....kkkkkkkkkkk.....",
    "...krrrrrrrrrrrk....",
    "..krrrrrrrrrrrrrk...",
    "..krrrrrrrrrrrrrk...",
    ".krrrrrrrrrrrrrrrk..",
    ".khhhhhhhhhhhhhhhk..",
    ".khffffffffffffhhk..",
    ".khf.kf.ffff.kf.hk..",
    ".khf.kf.ffff.kf.hk..",
    ".khffffffffffffffk..",
    ".khffffffffffffffk..",
    "..kffffffffffffk....",
    "..kffffkkkkkfffk....",
    "...kfffffffffffk....",
    "...kyyyyyyyyyyyk....",
    "..kyyyyyyyyyyyyyk...",
    ".kyyykcccccccckyyyk.",
    ".kccckcccccccckccck.",
    ".kccckcccccccckccck.",
    "..kkkkkkkkkkkkkkkk.."
]

SPRITE_CASTLE = [
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

WMO_DESCRIPTIONS = {
    0: "Bezchmurnie (Czyste niebo)",
    1: "Prawie bezchmurnie",
    2: "Częściowe zachmurzenie",
    3: "Pochmurno (Spokojny wieczór)",
    45: "Mgła nad Wartą",
    51: "Lekka mżawka",
    53: "Mżawka",
    61: "Lekki deszcz",
    63: "Umiarkowany deszcz",
    65: "Silna ulewa",
    71: "Prószy lekki śnieg",
    73: "Opady śniegu",
    80: "Przelotny deszcz",
    95: "Burza z wyładowaniami!"
}


def _compass_name(deg: float) -> str:
    dirs = ["Północy (N)", "NNE", "północnego-wschodu (NE)", "ENE",
            "Wschodu (E)", "ESE", "południowego-wschodu (SE)", "SSE",
            "Południa (S)", "SSW", "południowego-zachodu (SW)", "WSW",
            "Zachodu (W)", "WNW", "północnego-zachodu (NW)", "NNW"]
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
        # 0 = Riverside Boulevard (Side 2D), 1 = Tactical RPG Map (Top-down)
        self.view_mode = 0

        # Animation state
        self.is_animating = True
        self.time_counter = 0.0
        self.breath_y = 0
        self.blink_closed = False
        self.steam_particles = []
        self.rain_particles = []
        self.splashes = []

        # RPG Walk Engine States
        self.hero_map_x = 500.0
        self.hero_map_y = 230.0
        self.hero_map_dir = "down" # "up", "down", "left", "right"
        self.hero_step_anim = 0
        self.hero_street_x = 450.0
        self.footstep_dust = []

        # Weather Station Data
        self.is_live = False
        self.station_time_str = "--:--"
        self.temp = 1.2
        self.apparent_temp = -1.9
        self.humidity = 85
        self.weather_code = 3
        self.weather_desc = "Pochmurno"
        self.precip_mmh = 0.0
        self.wind_speed = 5.8
        self.wind_dir = 274.0

        # Physical state
        self.is_raining = False
        self.is_snowing = False
        self.is_storm = False

        # Pre-seed gentle steam & raindrops
        random.seed(1337)
        for _ in range(60):
            self.rain_particles.append({
                "x": random.randint(0, 1024),
                "y": random.randint(0, 520),
                "speed": random.uniform(380, 580),
                "len": random.randint(6, 12)
            })

        for _ in range(8):
            self.steam_particles.append({
                "x": random.uniform(494, 502),
                "y": random.uniform(400, 420),
                "vy": random.uniform(-18, -32),
                "life": random.uniform(0.1, 1.2),
                "max_life": 1.2
            })

        # Fetch initial live data
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
            self.temp = float(c.get("temperature_2m", 1.2))
            self.apparent_temp = float(c.get("apparent_temperature", -1.9))
            self.precip_mmh = float(c.get("precipitation", 0.0))
            self.weather_code = int(c.get("weather_code", 3))
            self.weather_desc = WMO_DESCRIPTIONS.get(self.weather_code, "Zmienne")
            self.wind_speed = float(c.get("wind_speed_10m", 5.8))
            self.wind_dir = float(c.get("wind_direction_10m", 274.0))
            self.humidity = int(c.get("relative_humidity_2m", 85))

            raw_time = str(c.get("time", ""))
            self.station_time_str = raw_time.split("T")[1] if "T" in raw_time else time.strftime("%H:%M")
            self.is_live = True

        # STRICT REAL-TIME LOGIC: It only rains if precipitation is actually detected!
        self.is_raining = (self.precip_mmh > 0.0) or (self.weather_code in (51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99))
        self.is_snowing = (self.weather_code in (71, 73, 75, 77, 85, 86))
        self.is_storm = (self.weather_code in (95, 96, 99))

    def get_hotkey_hints(self):
        v_next = "Mapa RPG" if self.view_mode == 0 else "Ulica 2D"
        return [
            ("D-Pad", "Chodź postacią!"),
            ("X", f"Zmień widok ({v_next})"),
            ("A", "Pauza" if self.is_animating else "Graj"),
            ("SELECT", "Odśwież stację LIVE")
        ]

    def update(self, dt: float):
        if not self.is_animating:
            return

        self.time_counter += dt
        self.breath_y = int(math.sin(self.time_counter * 3.0) * 1.5)

        # Eye blink cycle (0.15s blink every 4s)
        cycle = self.time_counter % 4.0
        self.blink_closed = (cycle > 3.85)

        # Update footstep dust particles
        for dust in self.footstep_dust:
            dust["life"] -= dt
        self.footstep_dust = [d for d in self.footstep_dust if d["life"] > 0]

        # Update warm coffee steam (when dry)
        if not self.is_raining:
            for st in self.steam_particles:
                st["y"] += st["vy"] * dt
                st["x"] += math.sin(self.time_counter * 2.0 + st["y"] * 0.1) * 6.0 * dt
                st["life"] -= dt
                if st["life"] <= 0:
                    st["x"] = random.uniform(self.hero_street_x + 46, self.hero_street_x + 54)
                    st["y"] = 418
                    st["life"] = st["max_life"]

        # Update rain particles ONLY when actually raining
        if self.is_raining:
            wind_dx = (self.wind_speed * 4.0) * dt
            for p in self.rain_particles:
                p["y"] += p["speed"] * dt
                p["x"] += wind_dx
                if p["x"] > 1030: p["x"] = -10
                if p["x"] < -20: p["x"] = 1040

                # Check splash on hero open umbrella (around hero_street_x) or ground
                if (self.hero_street_x - 10) <= p["x"] <= (self.hero_street_x + 90) and 345 <= p["y"] <= 358:
                    self.splashes.append({"x": p["x"], "y": 348, "life": 0.12})
                    p["y"] = -10
                    p["x"] = random.randint(0, 1024)
                elif p["y"] >= 508:
                    if random.random() < 0.3:
                        self.splashes.append({"x": p["x"], "y": 508, "life": 0.10})
                    p["y"] = -10
                    p["x"] = random.randint(0, 1024)

            for s in self.splashes:
                s["life"] -= dt
            self.splashes = [s for s in self.splashes if s["life"] > 0]

    def _draw_matrix(self, draw: ImageDraw.ImageDraw, matrix: List[str], colors: dict, ox: int, oy: int, scale: int = 4):
        for r, row in enumerate(matrix):
            for c, ch in enumerate(row):
                col = colors.get(ch)
                if col:
                    x1 = ox + c * scale
                    y1 = oy + r * scale
                    draw.rectangle([x1, y1, x1 + scale - 1, y1 + scale - 1], fill=col)

    def render(self, canvas):
        w, h = 1024, 768
        if self.view_mode == 0:
            self._render_cozy_street(canvas, w, h)
        else:
            self._render_rpg_overworld(canvas, w, h)

    # -------------------------------------------------------------------------
    # SCENE 1: COZY 16-BIT RIVERSIDE BOULEVARD (BULWARY GORZÓW)
    # -------------------------------------------------------------------------
    def _render_cozy_street(self, canvas, w: int, h: int):
        draw = canvas.draw
        ground_y = 508

        # 1. Atmospheric Dithered Sky
        now_h = datetime.datetime.now().hour
        is_night = (now_h >= 17 or now_h < 7)

        if is_night:
            for y in range(0, ground_y, 4):
                f = y / float(ground_y)
                r = int(C_NIGHT_SKY_TOP[0] * (1 - f) + C_NIGHT_SKY_BOT[0] * f)
                g = int(C_NIGHT_SKY_TOP[1] * (1 - f) + C_NIGHT_SKY_BOT[1] * f)
                b = int(C_NIGHT_SKY_TOP[2] * (1 - f) + C_NIGHT_SKY_BOT[2] * f)
                draw.rectangle([0, y, w, y + 3], fill=(r, g, b))

            # Stars
            stars = [(60, 40), (140, 75), (230, 30), (340, 90), (450, 45), (570, 70), (680, 35), (780, 85), (890, 50), (970, 80)]
            for sx, sy in stars:
                if (int(self.time_counter * 3.5 + sx) % 3) != 0:
                    draw.rectangle([sx, sy, sx + 2, sy + 2], fill=C_STARS)

            # Moon
            mx, my = 850, 55
            draw.ellipse([mx - 20, my - 20, mx + 68, my + 68], fill=(40, 60, 100, 40))
            moon_ascii = [
                "...yyyyyy...", "..yyyyyyyy..", ".yyykkkkyyy.", "yyyykkkkyyyy",
                "yyyykkkkyyyy", "yyyykkkkyyyy", ".yyykkkkyyy.", "..yyyyyyyy..", "...yyyyyy..."
            ]
            self._draw_matrix(draw, moon_ascii, {"y": C_MOON, "k": None}, mx, my, scale=5)
        else:
            for y in range(0, ground_y, 4):
                f = y / float(ground_y)
                r = int(C_DAY_SKY_TOP[0] * (1 - f) + C_DAY_SKY_BOT[0] * f)
                g = int(C_DAY_SKY_TOP[1] * (1 - f) + C_DAY_SKY_BOT[1] * f)
                b = int(C_DAY_SKY_TOP[2] * (1 - f) + C_DAY_SKY_BOT[2] * f)
                draw.rectangle([0, y, w, y + 3], fill=(r, g, b))
            draw.rectangle([840, 50, 888, 98], fill=(255, 225, 60))

        # 2. Skyline & Cathedral
        skyline_y = ground_y - 140
        draw.rectangle([660, skyline_y - 65, 700, skyline_y + 20], fill=C_SILHOUETTE_FAR)
        draw.polygon([(656, skyline_y - 65), (680, skyline_y - 130), (704, skyline_y - 65)], fill=C_SILHOUETTE_FAR)
        if is_night:
            draw.rectangle([675, skyline_y - 35, 685, skyline_y - 25], fill=(255, 210, 70))

        # 3. Arched Railway Bridge & Animated Passing Train
        by = ground_y - 95
        for ax in range(20, 980, 200):
            draw.rectangle([ax, by + 10, ax + 185, by + 26], fill=C_BRIDGE_BRICK)
            draw.chord([ax + 18, by + 12, ax + 167, by + 90], 180, 360, fill=C_NIGHT_SKY_BOT if is_night else C_DAY_SKY_BOT)
            draw.rectangle([ax + 172, by + 10, ax + 192, by + 60], fill=C_BRIDGE_BRICK)
            if is_night:
                train_x = int(self.time_counter * 60 + ax) % 240
                if train_x < 180:
                    draw.rectangle([ax + train_x, by + 2, ax + train_x + 16, by + 8], fill=C_TRAIN_LIGHT)

        # 4. River Warta
        wy1 = ground_y - 50
        draw.rectangle([0, wy1, w, ground_y], fill=C_WATER_DARK)
        water_shift = int(self.time_counter * 28) % 44
        for wy in range(wy1 + 4, ground_y - 4, 10):
            for wx in range(-44 + water_shift, w + 44, 44):
                draw.rectangle([wx, wy, wx + 18, wy + 2], fill=C_WATER_RIPPLE)

        # 5. Pavement & Railing
        draw.rectangle([0, ground_y, w, 768], fill=C_COBBLE_DARK)
        draw.rectangle([0, ground_y - 4, w, ground_y + 4], fill=C_CURB)
        for rx in range(0, w, 24):
            draw.rectangle([rx, ground_y - 20, rx + 4, ground_y - 4], fill=C_RAILING)
        draw.rectangle([0, ground_y - 22, w, ground_y - 18], fill=C_RAILING)

        for py in range(ground_y + 10, 540, 16):
            sh = 16 if (py // 16) % 2 == 0 else 0
            for px in range(sh, w, 32):
                draw.rectangle([px, py, px + 26, py + 12], fill=C_COBBLE_MID, outline=C_COBBLE_DARK)

        # 6. Lamp
        lx = 240
        ly = ground_y - 192
        if is_night:
            glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(glow_layer)
            gdraw.polygon([(lx + 24, ly + 36), (lx - 160, ground_y + 40), (lx + 220, ground_y + 40)], fill=(255, 225, 110, 50))
            canvas.image.paste(glow_layer, (0, 0), glow_layer)
        lamp_pal = {"k": C_LAMP_IRON, "y": C_LAMP_GOLD, "w": (255, 255, 230), "s": C_LAMP_IRON}
        self._draw_matrix(draw, SPRITE_LAMP, lamp_pal, lx, ly, scale=4)

        # 7. Hero Walking along the Boulevard (x = hero_street_x)
        hx = int(self.hero_street_x)
        hy = ground_y - 130 + self.breath_y

        # Footstep dust
        for dust in self.footstep_dust:
            draw.rectangle([int(dust["x"]), int(dust["y"]), int(dust["x"]) + 4, int(dust["y"]) + 3], fill=(120, 140, 165))

        # Hero Body
        draw.rectangle([hx + 20, hy + 4, hx + 56, hy + 24], fill=C_HERO_BEANIE)
        draw.rectangle([hx + 16, hy + 20, hx + 60, hy + 28], fill=C_HERO_BEANIE)
        draw.rectangle([hx + 34, hy - 2, hx + 42, hy + 6], fill=(255, 255, 255))

        draw.rectangle([hx + 20, hy + 28, hx + 56, hy + 48], fill=C_HERO_SKIN)
        if self.blink_closed:
            draw.line([(hx + 28, hy + 38), (hx + 34, hy + 38)], fill=(40, 25, 20), width=2)
            draw.line([(hx + 42, hy + 38), (hx + 48, hy + 38)], fill=(40, 25, 20), width=2)
        else:
            draw.rectangle([hx + 28, hy + 36, hx + 32, hy + 40], fill=(20, 25, 35))
            draw.rectangle([hx + 42, hy + 36, hx + 46, hy + 40], fill=(20, 25, 35))

        draw.rectangle([hx + 16, hy + 48, hx + 60, hy + 60], fill=C_HERO_SCARF)
        draw.rectangle([hx + 14, hy + 60, hx + 62, hy + 104], fill=C_HERO_COAT)
        draw.rectangle([hx + 24, hy + 64, hx + 52, hy + 102], fill=C_HERO_COAT_LIGHT)

        # Legs step offset when walking
        step_off = 4 if (self.hero_step_anim % 2 == 1) else 0
        draw.rectangle([hx + 20 - step_off, hy + 104, hx + 34 - step_off, hy + 128], fill=C_HERO_PANTS)
        draw.rectangle([hx + 42 + step_off, hy + 104, hx + 56 + step_off, hy + 128], fill=C_HERO_PANTS)
        draw.rectangle([hx + 16 - step_off, hy + 126, hx + 34 - step_off, hy + 134], fill=C_HERO_BOOTS)
        draw.rectangle([hx + 42 + step_off, hy + 126, hx + 60 + step_off, hy + 134], fill=C_HERO_BOOTS)

        # Props: Coffee or Umbrella
        if not self.is_raining:
            umb_fold_pal = {"k": C_UMB_STAFF, "r": C_UMB_RED, "y": C_UMB_YELLOW, ".": None}
            self._draw_matrix(draw, SPRITE_UMB_FOLDED, umb_fold_pal, lx + 36, ground_y - 92, scale=3)

            draw.rectangle([hx + 28, hy + 76, hx + 48, hy + 92], fill=C_MUG)
            draw.rectangle([hx + 30, hy + 78, hx + 46, hy + 82], fill=C_MUG_COFFEE)
            for st in self.steam_particles:
                draw.rectangle([int(st["x"]), int(st["y"]), int(st["x"]) + 3, int(st["y"]) + 3], fill=(225, 235, 255))
        else:
            ux = hx - 22
            uy = hy - 48
            umb_open_pal = {"k": C_UMB_STAFF, "r": C_UMB_RED, "y": C_UMB_YELLOW, ".": None}
            self._draw_matrix(draw, SPRITE_UMB_OPEN, umb_open_pal, ux, uy, scale=4)
            draw.rectangle([hx + 34, hy + 8, hx + 38, hy + 76], fill=C_UMB_STAFF)

            wind_slant = int(self.wind_speed * 0.7)
            for p in self.rain_particles:
                draw.line([(p["x"], p["y"]), (p["x"] + wind_slant, p["y"] + p["len"])], fill=C_RAIN, width=2)
            for s in self.splashes:
                draw.rectangle([s["x"] - 2, s["y"] - 2, s["x"] + 2, s["y"]], fill=C_SPLASH)

        self._render_top_hud(draw, w)
        self._render_jrpg_dialogue(draw, w, h)

    # -------------------------------------------------------------------------
    # SCENE 2: TOP-DOWN 16-BIT RPG OVERWORLD RADAR (ADVANCE WARS / ZELDA SNES)
    # -------------------------------------------------------------------------
    def _render_rpg_overworld(self, canvas, w: int, h: int):
        draw = canvas.draw

        # 1. Forest & Grass Tiles
        draw.rectangle([0, 0, w, h], fill=(22, 46, 30))
        for ty in range(0, 530, 32):
            for tx in range(0, w, 32):
                if ((tx + ty) // 32) % 2 == 0:
                    draw.rectangle([tx, ty, tx + 31, ty + 31], fill=(26, 54, 34))

        # 2. Animated Windmill on the hills (near Zielona Góra, x: 420, y: 460)
        wx, wy = 420, 450
        draw.rectangle([wx - 6, wy, wx + 6, wy + 26], fill=(160, 140, 110), outline=(30, 20, 15))
        blade_angle = self.time_counter * (self.wind_speed * 0.8 + 1.5)
        for i in range(4):
            ang = blade_angle + i * (math.pi / 2)
            bx2 = wx + math.cos(ang) * 22
            by2 = wy + math.sin(ang) * 22
            draw.line([(wx, wy), (bx2, by2)], fill=(245, 245, 255), width=2)

        # 3. Animated Drifting River Barge / Boat on River Warta
        boat_t = (self.time_counter * 14) % 600
        boat_x = 800 - boat_t
        boat_y = 310 - int(math.sin(boat_t * 0.02) * 15)
        draw.polygon([(boat_x - 12, boat_y + 4), (boat_x + 12, boat_y + 4), (boat_x + 8, boat_y + 10), (boat_x - 8, boat_y + 10)], fill=(120, 70, 40))
        draw.rectangle([boat_x - 3, boat_y - 2, boat_x + 3, boat_y + 4], fill=(240, 240, 250)) # cabin

        # 4. Rivers (Warta and Odra as animated blue ribbons)
        odra = [(310, 20), (300, 110), (270, 210), (250, 310), (230, 420), (240, 520)]
        for i in range(len(odra) - 1):
            draw.line([odra[i], odra[i + 1]], fill=(14, 75, 145), width=18)
            draw.line([odra[i], odra[i + 1]], fill=(38, 135, 225), width=10)

        warta = [(860, 340), (740, 320), (510, 250), (370, 230), (270, 210)]
        for i in range(len(warta) - 1):
            draw.line([warta[i], warta[i + 1]], fill=(14, 75, 145), width=16)
            draw.line([warta[i], warta[i + 1]], fill=(38, 135, 225), width=8)

        # 5. Castle Towns
        towns = [
            ("Gorzów Wlkp. [Baza]", 500, 230, True),
            ("Szczecin (Port)", 260, 65, False),
            ("Poznań (Twierdza)", 750, 320, False),
            ("Zielona Góra", 360, 420, False),
            ("Kostrzyn n/O.", 250, 195, False),
            ("Berlin", 70, 210, False)
        ]
        town_pal = {"k": (10, 15, 20), "w": (225, 230, 240), "r": (225, 45, 45), ".": None}
        for name, cx, cy, is_home in towns:
            self._draw_matrix(draw, SPRITE_CASTLE, town_pal, cx - 24, cy - 24, scale=3)
            # Animated waving flag atop castles!
            flag_w = int(math.sin(self.time_counter * 5.0 + cx) * 3)
            draw.line([(cx - 15, cy - 24), (cx - 15, cy - 32)], fill=(255, 255, 255), width=1)
            draw.polygon([(cx - 15, cy - 32), (cx - 7 + flag_w, cy - 29), (cx - 15, cy - 26)], fill=(255, 40, 40))

            draw.rounded_rectangle([cx - 42, cy + 28, cx + 90, cy + 46], radius=4, fill=(16, 24, 40), outline=(255, 210, 50) if is_home else (60, 85, 120))
            draw.text((cx - 36, cy + 31), name, fill=(255, 220, 60) if is_home else (210, 225, 240), font=get_font(10, bold=is_home))

        # 6. Moving Radar Cloud
        cloud_x = int(self.time_counter * 25) % 1100 - 100
        draw.rounded_rectangle([cloud_x, 140, cloud_x + 240, 250], radius=16, fill=(35, 50, 75, 210), outline=(0, 240, 255))
        draw.text((cloud_x + 18, 155), "RADAR OPADÓW: FRONT CHMUR", fill=(0, 240, 255), font=get_font(10, bold=True))

        # Check if Hero is under the radar cloud
        under_cloud = (cloud_x - 20 <= self.hero_map_x <= cloud_x + 240) and (130 <= self.hero_map_y <= 270)
        if under_cloud or self.is_raining:
            for rx in range(cloud_x + 15, cloud_x + 225, 14):
                draw.line([(rx, 252), (rx - 6, 298)], fill=(80, 180, 255), width=2)

        # 7. Footstep dust puffs on map
        for dust in self.footstep_dust:
            draw.rectangle([int(dust["x"]), int(dust["y"]), int(dust["x"]) + 3, int(dust["y"]) + 3], fill=(80, 140, 80))

        # 8. MINIATURE HERO CHARACTER ON RPG MAP (WALKABLE WITH D-PAD!)
        mx = int(self.hero_map_x)
        my = int(self.hero_map_y)

        # 4-Directional 16-bit RPG Hero Sprite (Scale: 3x -> 24x36 px)
        # Beanie
        draw.rectangle([mx - 10, my - 26, mx + 10, my - 16], fill=C_HERO_BEANIE)
        draw.rectangle([mx - 4, my - 29, mx + 4, my - 26], fill=(255, 255, 255)) # pompom

        # Face & Eyes depending on direction
        draw.rectangle([mx - 9, my - 16, mx + 9, my - 7], fill=C_HERO_SKIN)
        if self.hero_map_dir == "down":
            draw.rectangle([mx - 6, my - 13, mx - 3, my - 10], fill=(20, 25, 35))
            draw.rectangle([mx + 3, my - 13, mx + 6, my - 10], fill=(20, 25, 35))
        elif self.hero_map_dir == "left":
            draw.rectangle([mx - 8, my - 13, mx - 5, my - 10], fill=(20, 25, 35))
        elif self.hero_map_dir == "right":
            draw.rectangle([mx + 5, my - 13, mx + 8, my - 10], fill=(20, 25, 35))
        # if "up": back of head, no eyes

        # Scarf
        draw.rectangle([mx - 10, my - 7, mx + 10, my - 3], fill=C_HERO_SCARF)
        # Coat Body
        draw.rectangle([mx - 11, my - 3, mx + 11, my + 10], fill=C_HERO_COAT)

        # Walking Legs Cycle
        leg_shift = 3 if (self.hero_step_anim % 2 == 1) else 0
        if self.hero_map_dir in ("down", "up"):
            draw.rectangle([mx - 8, my + 10, mx - 2, my + 16 + leg_shift], fill=C_HERO_PANTS)
            draw.rectangle([mx + 2, my + 10, mx + 8, my + 16 - leg_shift], fill=C_HERO_PANTS)
            draw.rectangle([mx - 9, my + 14 + leg_shift, mx - 1, my + 19 + leg_shift], fill=C_HERO_BOOTS)
            draw.rectangle([mx + 1, my + 14 - leg_shift, mx + 9, my + 19 - leg_shift], fill=C_HERO_BOOTS)
        else: # left or right
            draw.rectangle([mx - 4 - leg_shift, my + 10, mx + 4 - leg_shift, my + 16], fill=C_HERO_PANTS)
            draw.rectangle([mx - 5 - leg_shift, my + 14, mx + 5 - leg_shift, my + 19], fill=C_HERO_BOOTS)

        # Miniature Umbrella if under rain cloud!
        if under_cloud or self.is_raining:
            draw.chord([mx - 18, my - 44, mx + 18, my - 22], 180, 360, fill=C_UMB_RED, outline=C_UMB_YELLOW)
            draw.line([(mx, my - 26), (mx, my - 6)], fill=(255, 255, 255), width=2)
            # Falling rain droplets on hero
            for i in range(4):
                draw.line([(mx - 10 + i * 7, my - 18), (mx - 10 + i * 7, my - 12)], fill=C_RAIN, width=1)

        # "TY" Marker
        draw.polygon([(mx - 5, my - 34), (mx + 5, my - 34), (mx, my - 28)], fill=(255, 215, 60))

        # Top HUD & Bottom Dialogue
        self._render_top_hud(draw, w)
        self._render_jrpg_dialogue(draw, w, h, under_cloud=under_cloud)

    # -------------------------------------------------------------------------
    # TOP FLOATING ARCADE RIBBON (Minimalist Glass Banner)
    # -------------------------------------------------------------------------
    def _render_top_hud(self, draw: ImageDraw.ImageDraw, w: int):
        rx = 24
        ry = 16
        rw = w - 48
        rh = 46

        draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=8, fill=(12, 18, 30), outline=(0, 240, 255), width=2)

        f_hud = get_font(12, bold=True)
        draw.text((rx + 16, ry + 14), "● GORZÓW WIELKOPOLSKI", fill=(255, 215, 60), font=f_hud)

        temp_col = (80, 195, 255) if self.temp < 5 else (255, 170, 0)
        draw.text((rx + 240, ry + 14), f"TEMP: {self.temp:+.1f}°C (odcz. {self.apparent_temp:+.1f}°C)", fill=temp_col, font=f_hud)

        draw.text((rx + 480, ry + 14), f"AURA: {self.weather_desc.upper()}", fill=(245, 250, 255), font=f_hud)

        rain_txt = f"OPAD: {self.precip_mmh:.1f} mm/h (Pada deszcz!)" if self.is_raining else "OPAD: 0.0 mm/h (SUCHO)"
        draw.text((rx + 700, ry + 14), rain_txt, fill=(0, 240, 255) if self.is_raining else (160, 180, 205), font=f_hud)

        live_str = f"● LIVE ({self.station_time_str})" if self.is_live else "○ OFFLINE"
        draw.text((rx + rw - 130, ry + 14), live_str, fill=(0, 255, 180) if self.is_live else (150, 160, 175), font=f_hud)

    # -------------------------------------------------------------------------
    # BOTTOM JRPG DIALOGUE BOX WITH AVATAR PORTRAIT & LOCATION DETECTOR
    # -------------------------------------------------------------------------
    def _render_jrpg_dialogue(self, draw: ImageDraw.ImageDraw, w: int, h: int, under_cloud: bool = False):
        bx = 24
        by = 540
        bw = w - 48
        bh = 206

        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=10, fill=(12, 18, 34), outline=(255, 210, 50), width=3)
        draw.rounded_rectangle([bx + 4, by + 4, bx + bw - 4, by + bh - 4], radius=8, fill=(16, 24, 46), outline=(255, 255, 255), width=1)

        # Avatar Box on Left
        av_x = bx + 18
        av_y = by + 16
        draw.rounded_rectangle([av_x, av_y, av_x + 90, av_y + 90], radius=6, fill=(22, 34, 60), outline=(255, 210, 50), width=2)

        av_pal = {
            "k": (16, 20, 28),
            "r": C_HERO_BEANIE,
            "h": C_HERO_HAIR,
            "f": C_HERO_SKIN,
            "y": C_HERO_SCARF,
            "c": C_HERO_COAT,
            ".": None
        }
        self._draw_matrix(draw, PORTRAIT_HERO_COZY, av_pal, av_x + 5, av_y + 5, scale=4)

        draw.rectangle([av_x, av_y + 96, av_x + 90, av_y + 116], fill=(255, 210, 50))
        draw.text((av_x + 12, av_y + 98), "BOHATER", fill=(10, 15, 25), font=get_font(11, bold=True))

        # Dialogue Column
        cx = av_x + 108

        # In RPG Mode: Location & Exploration Engine!
        if self.view_mode == 1:
            # Detect nearest town
            town_distances = [
                ("Gorzów Wlkp.", math.hypot(self.hero_map_x - 500, self.hero_map_y - 230), "Stacja meteo działa, spokojny wieczór nad Wartą."),
                ("Szczecin", math.hypot(self.hero_map_x - 260, self.hero_map_y - 65), "Czujesz morską bryzę znad Zalewu Szczecińskiego! Statki w porcie."),
                ("Poznań", math.hypot(self.hero_map_x - 750, self.hero_map_y - 320), "Główna twierdza. Radar dopplerowski POLRAD kręci się na wieży."),
                ("Zielona Góra", math.hypot(self.hero_map_x - 360, self.hero_map_y - 420), "Wzgórza i winnice Ziemi Lubuskiej. Ciepły mikroklimat."),
                ("Kostrzyn n/O.", math.hypot(self.hero_map_x - 250, self.hero_map_y - 195), "Ujście Warty do Odry. Granica zachodnia."),
                ("Berlin", math.hypot(self.hero_map_x - 70, self.hero_map_y - 210), "Zachodni kraniec mapy radarowej. Masy powietrza idą na wschód.")
            ]
            nearest_town, dist, town_lore = min(town_distances, key=lambda t: t[1])

            if under_cloud:
                msg1 = "„Wszedłem w zasięg chmury radarowej! Z góry pada deszcz, otwieram parasolkę!”"
                msg2 = "Radar wykrywa opad w tym sektorze. Klawisze D-Pad pozwalają wyjść poza chmurę."
                prop_status = "Stan: PARASOLKA OTWARTA POD CHMURĄ RADAROWĄ"
            elif dist < 65:
                msg1 = f"„Wkraczam do rejonu: {nearest_town}! {town_lore}”"
                msg2 = f"Koordynaty GPS: ({int(self.hero_map_x)}, {int(self.hero_map_y)}). Wiatr {self.wind_speed:.1f} km/h z {_compass_name(self.wind_dir)}."
                prop_status = f"Lokacja: W POBLIŻU {nearest_town.upper()}"
            else:
                msg1 = "„Przemierzam szlaki Ziemi Lubuskiej wzdłuż rzek. Wiatraki kręcą się na wzgórzach.”"
                msg2 = f"D-Pad pozwala swobodnie chodzić po mapie! Klawisz [X] powraca na bulwar Gorzowa."
                prop_status = f"Eksploracja: TRASA POLNA ({int(self.hero_map_x)}, {int(self.hero_map_y)})"

        else: # Street View
            if self.is_storm:
                msg1 = "„Oho! Grzmi na horyzoncie! Dobrze, że mam parasol – burza nadciąga!”"
                msg2 = f"Uwaga na wyładowania. Wiatr {self.wind_speed:.1f} km/h z {_compass_name(self.wind_dir)}."
                prop_status = "Stan: PARASOL OTWARTY (Ochrona przed burzą)"
            elif self.is_raining:
                msg1 = f"„Pada deszcz ({self.precip_mmh:.1f} mm/h). Trzymam parasol, krople rozbryzgują się o bruk.”"
                msg2 = f"Wilgotność powietrza wynosi {self.humidity}%. Wiatr wieje z {_compass_name(self.wind_dir)}."
                prop_status = "Stan: PARASOL OTWARTY (Pikselowe krople aktywne)"
            elif self.is_snowing:
                msg1 = "„Prószy śnieg nad bulwarami! Czas na spacer w zimowej scenerii.”"
                msg2 = f"Temperatura {self.temp:+.1f}°C. Płatki śniegu osiadają na mostach Gorzowa."
                prop_status = "Stan: ZIMOWY PŁASZCZ (Parasol schowany)"
            else: # DRY (Like right now!)
                msg1 = "„Na dworze jest sucho, ani kropli deszczu! Wziąłem kubek gorącej kawy.”"
                msg2 = f"Spokojna, chłodna noc ({self.temp:+.1f}°C). Wiatr słaby ({self.wind_speed:.1f} km/h). D-Pad pozwala spacerować w lewo i prawo!"
                prop_status = "Stan: GORĄCA KAWA W DŁONI (Parasol złożony przy latarni)"

        f_diag = get_font(13, bold=False)
        f_sub = get_font(12, bold=False)
        f_bold = get_font(12, bold=True)

        draw.text((cx, by + 18), msg1, fill=(255, 255, 255), font=f_diag)
        draw.text((cx, by + 46), msg2, fill=(195, 215, 245), font=f_sub)
        draw.text((cx, by + 76), f"► {prop_status}", fill=(0, 240, 255), font=f_bold)

        # Telemetry pills bar
        draw.line([(cx, by + 104), (bx + bw - 18, by + 104)], fill=(45, 65, 95), width=1)
        pills = [
            f"WILGOTNOŚĆ: {self.humidity}%",
            f"WIATR: {self.wind_speed:.1f} km/h",
            f"OPAD: {self.precip_mmh:.1f} mm",
            f"STACJA: GORZÓW ({self.station_time_str})"
        ]
        px = cx
        for pill in pills:
            draw.text((px, by + 114), pill, fill=(255, 210, 60), font=get_font(11, bold=True))
            px += 185

        # Controls Hint Footer
        draw.line([(bx + 14, by + bh - 38), (bx + bw - 14, by + bh - 38)], fill=(45, 65, 95), width=1)
        hint_txt = "► [D-PAD] CHODŹ POSTACIĄ!   |   [X] PRZEŁĄCZ: ULICA 2D ◄► MAPA RPG   |   [SELECT] ODŚWIEŻ STACJĘ"
        draw.text((bx + 20, by + bh - 28), hint_txt, fill=(0, 255, 180), font=get_font(11, bold=True))

    def handle_input(self, event: str) -> bool:
        ev = str(event).upper()
        if ev.startswith("KEY_"): ev = ev[4:]
        if ev.startswith("BTN_"): ev = ev[4:]

        move_speed = 18

        # D-PAD WALKING ENGINE
        if ev in ("UP", "W_KEY", "DPAD_UP"):
            if self.view_mode == 1:
                self.hero_map_y = max(35, self.hero_map_y - move_speed)
                self.hero_map_dir = "up"
                self.hero_step_anim = (self.hero_step_anim + 1) % 4
                self.footstep_dust.append({"x": self.hero_map_x, "y": self.hero_map_y + 14, "life": 0.4})
            return True
        elif ev in ("DOWN", "S_KEY", "DPAD_DOWN"):
            if self.view_mode == 1:
                self.hero_map_y = min(500, self.hero_map_y + move_speed)
                self.hero_map_dir = "down"
                self.hero_step_anim = (self.hero_step_anim + 1) % 4
                self.footstep_dust.append({"x": self.hero_map_x, "y": self.hero_map_y + 14, "life": 0.4})
            return True
        elif ev in ("LEFT", "A_KEY", "DPAD_LEFT"):
            if self.view_mode == 1:
                self.hero_map_x = max(30, self.hero_map_x - move_speed)
                self.hero_map_dir = "left"
                self.hero_step_anim = (self.hero_step_anim + 1) % 4
                self.footstep_dust.append({"x": self.hero_map_x + 6, "y": self.hero_map_y + 14, "life": 0.4})
            else:
                self.hero_street_x = max(60, self.hero_street_x - 16)
                self.hero_step_anim = (self.hero_step_anim + 1) % 4
                self.footstep_dust.append({"x": self.hero_street_x + 50, "y": 508, "life": 0.3})
            return True
        elif ev in ("RIGHT", "D_KEY", "DPAD_RIGHT"):
            if self.view_mode == 1:
                self.hero_map_x = min(980, self.hero_map_x + move_speed)
                self.hero_map_dir = "right"
                self.hero_step_anim = (self.hero_step_anim + 1) % 4
                self.footstep_dust.append({"x": self.hero_map_x - 6, "y": self.hero_map_y + 14, "life": 0.4})
            else:
                self.hero_street_x = min(920, self.hero_street_x + 16)
                self.hero_step_anim = (self.hero_step_anim + 1) % 4
                self.footstep_dust.append({"x": self.hero_street_x + 20, "y": 508, "life": 0.3})
            return True

        elif ev in ("X", "BTN_X", "U"):
            self.view_mode = (self.view_mode + 1) % 2
            return True
        elif ev in ("A", "BTN_A", "SPACE", "RETURN", "J"):
            self.is_animating = not self.is_animating
            return True
        elif ev in ("SELECT", "REFRESH", "R"):
            self._refresh_live_data()
            return True
        return False
