"""
BrickDeck Module: Desk Clock, Screensaver, Weather & MZK Gorzow Live Transit
Pulls REAL live GPS-tracked departures from MZK Gorzow Wielkopolski API:
https://komunikacja.um.gorzow.pl/vm/main?command=fs&action=departures&stop={id}
Also features Open-Meteo live weather for Gorzow and 3 animated background styles.
"""

import os
import ssl
import time
import json
import random
import threading
import urllib.request
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont

from core.module_base import BaseModule
from core.canvas import get_font
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN, COLOR_NEON_PINK
)
from core.i18n import t

ANIMATION_STYLES = ["starfield", "matrix", "synthwave"]

WEATHER_CODES = {
    0: ("Slonecznie", "☀️"),
    1: ("Przewaznie slonecznie", "🌤️"),
    2: ("Czesciowe zachmurzenie", "⛅"),
    3: ("Pochmurno", "☁️"),
    45: ("Mgla", "🌫️"),
    48: ("Szron / Mgla", "🌫️"),
    51: ("Lekka mzawka", "🌦️"),
    53: ("Mzawka", "🌧️"),
    55: ("Gesta mzawka", "🌧️"),
    61: ("Lekki deszcz", "🌧️"),
    63: ("Umiarkowany deszcz", "🌧️"),
    65: ("Ulewny deszcz", "🌧️"),
    71: ("Lekki snieg", "🌨️"),
    73: ("Snieg", "❄️"),
    75: ("Sniezyca", "❄️"),
    80: ("Przelotny deszcz", "🌦️"),
    81: ("Ulewa", "🌧️"),
    82: ("Gwaltowna ulewa", "⛈️"),
    95: ("Burza", "⛈️"),
}


class ClockModule(BaseModule):
    name = "Desk Clock & MZK"
    short_name = "Clock & MZK"
    icon = "🕒"
    accent_color = COLOR_CYBER_CYAN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.config_path = os.path.join(os.path.dirname(__file__), "..", "transit_config.json")
        self.config = self._load_config()

        self.anim_idx = ANIMATION_STYLES.index(self.config.get("animation_style", "starfield"))
        self.active_stop_idx = self.config.get("active_stop_idx", 0)

        # Weather state
        self.weather_temp: float = 2.0
        self.weather_code: int = 2
        self.weather_wind: float = 12.0
        self.weather_status_str = "Czesciowe zachmurzenie"
        self.last_weather_fetch = 0

        # Live Transit (MZK Gorzow) State
        self.live_departures: List[Dict] = []
        self.last_transit_fetch = 0
        self.transit_status_str = "Laczenie z MZK Gorzow..."

        # Live Smog / Air Quality Sensors (Gorzow)
        self.smog_info = "Bardzo dobry"
        self.smog_pm25 = 8.5
        self.smog_pm10 = 11.0

        # Background Animation Data
        self._init_starfield()
        self._init_matrix()

    def _load_config(self) -> dict:
        default_cfg = {
            "city": "Gorzow Wielkopolski",
            "coordinates": {"lat": 52.7333, "lon": 15.2333},
            "active_stop_idx": 0,
            "animation_style": "starfield",
            "stops": [
                {"name": "Katedra", "id": "000000000095", "code": "8"},
                {"name": "AWF", "id": "000000000005", "code": "12"},
                {"name": "Jagielly", "id": "000000000076", "code": "161"},
                {"name": "Dworzec Glowny", "id": "000000001264", "code": "118"},
                {"name": "Rondo Santockie", "id": "000000000023", "code": "421"},
                {"name": "Wieprzyce PKP", "id": "000000000127", "code": "545"}
            ]
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_cfg.update(data)
            except Exception:
                pass
        return default_cfg

    def _init_starfield(self):
        """150 stars with 3D projection coordinates (x, y, z)."""
        self.stars = []
        for _ in range(150):
            self.stars.append([
                random.uniform(-500, 500),
                random.uniform(-350, 350),
                random.uniform(10, 800),
                random.uniform(8, 22)  # Speed
            ])

    def _init_matrix(self):
        """Matrix rain columns."""
        self.matrix_cols = 64
        self.matrix_drops = [random.randint(-40, 0) for _ in range(self.matrix_cols)]

    def on_activate(self):
        super().on_activate()
        # Fetch weather and MZK live departures in background thread
        t_weather = threading.Thread(target=self._fetch_weather_async, daemon=True)
        t_weather.start()
        t_transit = threading.Thread(target=self._fetch_mzk_live_async, daemon=True)
        t_transit.start()

    def _get_ssl_ctx(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def _fetch_weather_async(self):
        coords = self.config.get("coordinates", {"lat": 52.7333, "lon": 15.2333})
        lat, lon = coords.get("lat", 52.7333), coords.get("lon", 15.2333)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BrickDeck/1.0"})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cur = data.get("current_weather", {})
                self.weather_temp = float(cur.get("temperature", 2.0))
                self.weather_code = int(cur.get("weathercode", 0))
                self.weather_wind = float(cur.get("windspeed", 10.0))
                self.weather_status_str = WEATHER_CODES.get(self.weather_code, ("Czyste niebo", "☀️"))[0]
                self.last_weather_fetch = time.time()
        except Exception:
            pass

    def _fetch_mzk_live_async(self):
        """Fetch real-time departures from MZK Gorzow Wielkopolski official API."""
        stops = self.config.get("stops", [])
        if not stops:
            return
        cur_stop = stops[self.active_stop_idx % len(stops)]
        stop_id = cur_stop.get("id", "000000000095")

        url = f"https://komunikacja.um.gorzow.pl/vm/main?command=fs&action=departures&stop={stop_id}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (TrimUI Brick)"})
            with urllib.request.urlopen(req, context=self._get_ssl_ctx(), timeout=4.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, list):
                    parsed = []
                    for item in data:
                        parsed.append({
                            "line": str(item.get("line", "")),
                            "dest": item.get("destination", "Centrum"),
                            "time": item.get("time", "---"),
                            "info": item.get("depInfo") or ""
                        })
                    self.live_departures = parsed
                    self.transit_status_str = f"GPS LIVE: {len(parsed)} odjazdow"
                    self.last_transit_fetch = time.time()
        except Exception as e:
            self.transit_status_str = f"Tryb Offline ({cur_stop.get('name')})"

        # Also fetch live smog sensor data from Gorzow
        try:
            url_aq = "https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=aqsd"
            req_aq = urllib.request.Request(url_aq, headers={"User-Agent": "Mozilla/5.0 (TrimUI Brick)"})
            with urllib.request.urlopen(req_aq, context=self._get_ssl_ctx(), timeout=3.0) as r_aq:
                aq_data = json.loads(r_aq.read().decode("utf-8"))
                if aq_data and isinstance(aq_data, list):
                    first = aq_data[0]
                    self.smog_info = first.get("info", "Bardzo dobry")
                    self.smog_pm25 = float(first.get("pm2_5", 8.0))
                    self.smog_pm10 = float(first.get("pm10", 10.0))
        except Exception:
            pass

    def get_hotkey_hints(self):
        return [
            ("L1/R1", t("common.modules", "Moduly")),
            ("X", t("clock.stop_hint", "Zmien Przystanek MZK")),
            ("Y", t("clock.anim_hint", "Styl Animacji")),
            ("A", t("clock.refresh_hint", "Odswiez Teraz"))
        ]

    def update(self, dt: float):
        # 1. Update background animation
        anim = ANIMATION_STYLES[self.anim_idx]
        if anim == "starfield":
            for s in self.stars:
                s[2] -= s[3]
                if s[2] <= 5:
                    s[0] = random.uniform(-500, 500)
                    s[1] = random.uniform(-350, 350)
                    s[2] = 800
        elif anim == "matrix":
            for i in range(self.matrix_cols):
                self.matrix_drops[i] += 1
                if self.matrix_drops[i] > 40:
                    self.matrix_drops[i] = random.randint(-15, 0)

        # 2. Weather refresh check (every 15 min)
        now = time.time()
        if now - self.last_weather_fetch > 900:
            threading.Thread(target=self._fetch_weather_async, daemon=True).start()
            self.last_weather_fetch = now

        # 3. MZK Live departures refresh check (every 15 seconds)
        if now - self.last_transit_fetch > 15:
            threading.Thread(target=self._fetch_mzk_live_async, daemon=True).start()
            self.last_transit_fetch = now

    def _render_background_animation(self, canvas):
        """Render chosen animated background effect."""
        anim = ANIMATION_STYLES[self.anim_idx]
        draw = canvas.draw

        if anim == "starfield":
            cx, cy = 512, 384
            for s in self.stars:
                k = 320.0 / max(s[2], 1.0)
                px = int(cx + s[0] * k)
                py = int(cy + s[1] * k)
                if 0 <= px < 1024 and 52 <= py < 716:
                    brightness = int(max(40, min(255, (1.0 - s[2] / 800.0) * 255)))
                    size = 2 if s[2] < 350 else 1
                    draw.rectangle([(px, py), (px + size, py + size)], fill=(brightness, brightness, brightness))

        elif anim == "matrix":
            chars = "0123456789ABCDEFｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈ"
            font_m = get_font(12, bold=False)
            for col in range(self.matrix_cols):
                x = col * 16
                head_y = self.matrix_drops[col] * 16
                for trail in range(12):
                    y = head_y - (trail * 16)
                    if 52 <= y < 716:
                        ch = chars[(col + trail + int(time.time())) % len(chars)]
                        if trail == 0:
                            draw.text((x, y), ch, fill=(240, 255, 240), font=font_m)
                        else:
                            alpha = int(max(20, (1.0 - trail / 12.0) * 180))
                            draw.text((x, y), ch, fill=(0, alpha, 40), font=font_m)

        elif anim == "synthwave":
            hy = 520
            draw.line([(0, hy), (1024, hy)], fill=COLOR_NEON_PINK, width=2)
            cx = 512
            for x in range(0, 1025, 64):
                draw.line([(x, 716), (cx + (x - cx) // 4, hy)], fill=(60, 20, 80), width=1)
            t_offset = int((time.time() * 40) % 30)
            for y_line in range(hy + 10, 716, 25):
                draw.line([(0, y_line + t_offset), (1024, y_line + t_offset)], fill=(80, 20, 100), width=1)

    def render(self, canvas):
        # 1. Background animation
        self._render_background_animation(canvas)

        draw = canvas.draw

        # 2. Top-Left Card: GIANT CLOCK & DATE (x=36, y=68, w=530, h=250)
        canvas.draw.rounded_rectangle(
            [(36, 68), (566, 318)],
            radius=12, fill=(18, 22, 30, 235), outline=COLOR_CYBER_CYAN, width=2
        )

        cur_time_str = time.strftime("%H:%M:%S")
        days = t("clock.days")
        if not isinstance(days, list) or len(days) < 7:
            days = ["Poniedzialek", "Wtorek", "Sroda", "Czwartek", "Piatek", "Sobota", "Niedziela"]
        months = t("clock.months")
        if not isinstance(months, list) or len(months) < 12:
            months = ["Stycznia", "Lutego", "Marca", "Kwietnia", "Maja", "Czerwca",
                      "Lipca", "Sierpnia", "Wrzesnia", "Pazdziernika", "Listopada", "Grudnia"]
        now_dt = time.localtime()
        day_str = days[now_dt.tm_wday]
        date_str = f"{day_str}, {now_dt.tm_mday} {months[now_dt.tm_mon - 1]} {now_dt.tm_year}"

        # Big Digital Clock Font (54pt)
        font_clock = get_font(54, bold=True)
        font_date = get_font(15, bold=False)
        draw.text((60, 95), cur_time_str, fill=COLOR_CYBER_CYAN, font=font_clock)
        draw.text((64, 185), date_str, fill=COLOR_TEXT_PRIMARY, font=font_date)

        # Mode hint under clock
        anim_name = ANIMATION_STYLES[self.anim_idx].upper()
        canvas.draw_badge(64, 250, f"Animacja: {anim_name} [Y]", bg_color=(28, 36, 48), text_color=COLOR_CYBER_CYAN)

        # 3. Top-Right Card: WEATHER WIDGET (x=584, y=68, w=404, h=250)
        canvas.draw.rounded_rectangle(
            [(584, 68), (988, 318)],
            radius=12, fill=(18, 22, 30, 235), outline=COLOR_FLIPPER_AMBER, width=2
        )

        font_w_title = get_font(14, bold=True)
        draw.text((604, 86), t("clock.weather_title", "POGODA: GORZÓW WIELKOPOLSKI"),
                  fill=COLOR_FLIPPER_AMBER, font=font_w_title)
        draw.line([(584, 114), (988, 114)], fill=COLOR_BORDER, width=1)

        # Large Temperature
        font_temp = get_font(40, bold=True)
        icon_str = WEATHER_CODES.get(self.weather_code, ("", "⛅"))[1]
        temp_str = f"{self.weather_temp:+.1f} °C"
        draw.text((604, 130), f"{icon_str} {temp_str}", fill=COLOR_TEXT_PRIMARY, font=font_temp)

        # Weather Details
        font_det = get_font(13, bold=False)
        cond_lbl = t("clock.conditions", "Conditions")
        wind_lbl = t("clock.wind", "Wind")
        smog_lbl = t("clock.smog", "Air Quality")
        draw.text((604, 196), f"{cond_lbl}: {self.weather_status_str}", fill=COLOR_TEXT_PRIMARY, font=font_det)
        draw.text((604, 222), f"{wind_lbl}: {self.weather_wind:.1f} km/h | Station: Open-Meteo",
                  fill=COLOR_TEXT_SECONDARY, font=font_det)
        draw.text((604, 248), f"{smog_lbl} (Gorzow): {self.smog_info} (PM2.5: {self.smog_pm25:.1f})",
                  fill=COLOR_PHOSPHOR_GREEN, font=font_det)
        draw.text((604, 274), f"Refresh [A: {t('clock.refresh_hint', 'Refresh')}]", fill=COLOR_TEXT_MUTED, font=font_det)

        # 4. Bottom Half: REAL MZK GORZOW TRANSIT DISPLAY (x=36, y=334, w=952, h=360)
        canvas.draw.rounded_rectangle(
            [(36, 334), (988, 694)],
            radius=12, fill=(14, 18, 24, 240), outline=COLOR_FLIPPER_AMBER, width=2
        )

        stops = self.config.get("stops", [])
        cur_stop = stops[self.active_stop_idx % len(stops)] if stops else {"name": "Katedra"}
        stop_name = cur_stop.get("name", "Katedra")
        alt_code = cur_stop.get("code", "")

        # Pulsing Red/Amber Live Indicator dot
        pulse = (int(time.time() * 2) % 2 == 0)
        dot_color = (255, 42, 109) if pulse else (80, 20, 40)
        draw.ellipse([(60, 356), (72, 368)], fill=dot_color)

        font_sip_title = get_font(16, bold=True)
        title_full = f"MZK GORZÓW WLKP. NA ŻYWO: [{stop_name.upper()} ({alt_code})]"
        draw.text((82, 352), title_full, fill=COLOR_FLIPPER_AMBER, font=font_sip_title)

        canvas.draw_badge(850, 350, "Zmien [X]", bg_color=(36, 44, 58), text_color=COLOR_FLIPPER_AMBER)
        draw.line([(36, 384), (988, 384)], fill=COLOR_BORDER, width=1)

        # Table Column Headers
        font_th = get_font(12, bold=True)
        draw.text((60, 396), "LINIA", fill=COLOR_TEXT_SECONDARY, font=font_th)
        draw.text((180, 396), "KIERUNEK / PĘTLA DOCELOWA", fill=COLOR_TEXT_SECONDARY, font=font_th)
        draw.text((850, 396), "ODJAZD", fill=COLOR_TEXT_SECONDARY, font=font_th)
        draw.line([(36, 418), (988, 418)], fill=COLOR_BORDER, width=1)

        # Render departures
        font_line = get_font(18, bold=True)
        font_dest = get_font(16, bold=False)
        font_min = get_font(17, bold=True)

        row_y = 430
        display_deps = self.live_departures[:5] if self.live_departures else []

        if not display_deps:
            draw.text((60, 450), "Pobieranie rozkladu jazdy MZK Gorzow z GPS pojazdow...",
                      fill=COLOR_TEXT_SECONDARY, font=font_dest)
        else:
            for dep in display_deps:
                line_str = dep.get("line", "")
                dest_str = dep.get("dest", "")
                time_str = dep.get("time", "")

                # Line Badge
                canvas.draw.rounded_rectangle(
                    [(60, row_y), (140, row_y + 36)],
                    radius=6, fill=(48, 36, 12), outline=COLOR_FLIPPER_AMBER, width=2
                )
                draw.text((75, row_y + 6), line_str, fill=COLOR_FLIPPER_AMBER, font=font_line)

                # Destination
                draw.text((180, row_y + 8), dest_str, fill=COLOR_TEXT_PRIMARY, font=font_dest)

                # Time formatting
                is_arriving = (">>>" in time_str or time_str in ("0 min", "1 min", "2 min"))
                if is_arriving:
                    blink_bg = (255, 42, 109) if pulse else (80, 20, 40)
                    canvas.draw_badge(820, row_y + 4, ">>> ZA CHWILĘ <<<", bg_color=blink_bg, text_color=(255, 255, 255))
                else:
                    draw.text((850, row_y + 8), time_str, fill=COLOR_FLIPPER_AMBER, font=font_min)

                draw.line([(60, row_y + 44), (960, row_y + 44)], fill=(28, 32, 42), width=1)
                row_y += 52

    def handle_input(self, event: str) -> bool:
        if event == "BTN_X":
            # Cycle through Gorzow stops
            stops = self.config.get("stops", [])
            if stops:
                self.active_stop_idx = (self.active_stop_idx + 1) % len(stops)
                self.config["active_stop_idx"] = self.active_stop_idx
                self.live_departures = []
                threading.Thread(target=self._fetch_mzk_live_async, daemon=True).start()
            return True
        elif event == "BTN_Y":
            # Cycle animation styles
            self.anim_idx = (self.anim_idx + 1) % len(ANIMATION_STYLES)
            self.config["animation_style"] = ANIMATION_STYLES[self.anim_idx]
            return True
        elif event == "BTN_A":
            # Refresh both weather and transit immediately
            threading.Thread(target=self._fetch_weather_async, daemon=True).start()
            threading.Thread(target=self._fetch_mzk_live_async, daemon=True).start()
            return True
        return False
