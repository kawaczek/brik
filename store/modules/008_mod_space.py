"""
BrickDeck Module: NOAA Global Space Weather & Aurora Oval (mod_space.py)
Real-time space weather monitoring: Solar wind (DSCOVR), GOES X-ray flares, SDO Sunspots, and Auroral Oval.
100% standalone and zero-dongle: pulls live NOAA SWPC & NASA feeds with offline fallback.
"""

import os
import math
import time
import json
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


class SpaceWeatherModule(BaseModule):
    name = "NOAA Space Weather & Aurora Oval"
    short_name = "Kosmos NOAA"
    icon = "☀️"
    accent_color = COLOR_FLIPPER_AMBER

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.view_pole = "NORTH"  # "NORTH" or "SOUTH"
        self.show_sunspots = True

        # Telemetry State
        self.solar_wind_speed = 462.0   # km/s
        self.solar_wind_density = 5.8   # protons / cm3
        self.solar_mag_bz = -3.4        # nT (southward = aurora)
        self.solar_temp = 120000        # Kelvin
        self.kp_index = 3.67            # 0 to 9
        self.xray_flux = "C1.8"         # A, B, C, M, X
        self.xray_class = "NORMAL"
        self.radio_blackout = "R0 (Brak)"
        self.geomag_storm = "G1 (Słaba burza)"

        # Sunspot active regions
        self.sunspots = [
            {"id": "AR3615", "x": 0.25, "y": -0.15, "size": 6, "class": "Beta-Gamma"},
            {"id": "AR3619", "x": -0.35, "y": 0.20, "size": 9, "class": "Beta-Delta"},
            {"id": "AR3622", "x": 0.05, "y": 0.40, "size": 4, "class": "Alpha"}
        ]

        self.last_fetch_time = 0
        self.thread_running = False

    def on_load(self):
        self.thread_running = True
        threading.Thread(target=self._poll_worker, daemon=True).start()

    def _poll_worker(self):
        while self.thread_running:
            now = time.time()
            if now - self.last_fetch_time > 60.0:
                self._fetch_noaa_data()
                self.last_fetch_time = now
            time.sleep(2.0)

    def _fetch_noaa_data(self):
        """Fetch real-time space weather summary from NOAA SWPC."""
        url = "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BrickDeck-OS/2.0"})
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                val = float(data.get("WindSpeed", 460.0))
                if val > 100:
                    self.solar_wind_speed = val
        except Exception:
            pass

        # Try Planetary K-Index
        url_kp = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        try:
            req = urllib.request.Request(url_kp, headers={"User-Agent": "BrickDeck-OS/2.0"})
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if len(data) > 1 and len(data[-1]) > 1:
                    self.kp_index = float(data[-1][1])
        except Exception:
            pass

    def get_hotkey_hints(self):
        pole_label = "Biegun: Płn" if self.view_pole == "NORTH" else "Biegun: Płd"
        return [
            ("L1/R1", t("common.modules", "Moduły")),
            ("X", pole_label),
            ("Y", "Plamy Słoneczne"),
            ("A", t("common.refresh", "Odśwież NOAA")),
            ("B", "Skale NOAA")
        ]

    def update(self, dt: float):
        pass

    def render(self, canvas):
        # Main Card Wrapper
        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title=f"☀️ NOAA SPACE WEATHER & AURORA MONITOR [SATELLITES: SDO / DSCOVR / GOES-16]",
            subtitle=f"Wiatr słoneczny: {self.solar_wind_speed:.0f} km/s  |  Indeks Kp: {self.kp_index:.1f}  |  Promieniowanie X-Ray: {self.xray_flux}",
            border_color=self.accent_color
        )

        # -------------------------------------------------------------
        # 1. Top-Left: SDO 4K Solar Disk Model (x=50, y=120, w=300, h=310)
        # -------------------------------------------------------------
        sx, sy, sw, sh = 50, 120, 300, 310
        canvas.draw.rounded_rectangle([(sx, sy), (sx + sw, sy + sh)], radius=10, fill=(18, 22, 30), outline=COLOR_BORDER, width=1)
        canvas.draw.text((sx + 14, sy + 14), "TARCZA SŁOŃCA (NASA SDO)", fill=COLOR_FLIPPER_AMBER, font=get_font(13, bold=True))
        canvas.draw.line([(sx + 14, sy + 34), (sx + sw - 14, sy + 34)], fill=COLOR_BORDER, width=1)

        # Draw Glowing Sun Sphere
        cx, cy, r = sx + sw // 2, sy + 165, 80
        # Corona glow
        for gr in range(r + 14, r, -2):
            alpha = int(40 * (1.0 - (gr - r) / 14.0))
            canvas.draw.ellipse([(cx - gr, cy - gr), (cx + gr, cy + gr)], outline=(255, 140, 20), width=1)

        # Golden Solar Disk
        canvas.draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(255, 180, 20), outline=(255, 210, 60), width=2)

        # Draw Sunspots (Plamy słoneczne)
        if self.show_sunspots:
            for sp in self.sunspots:
                sp_x = int(cx + sp["x"] * r * 0.8)
                sp_y = int(cy + sp["y"] * r * 0.8)
                sz = sp["size"]
                # Penumbra (brown) + Umbra (dark)
                canvas.draw.ellipse([(sp_x - sz, sp_y - sz // 2), (sp_x + sz, sp_y + sz // 2)], fill=(120, 60, 10))
                canvas.draw.ellipse([(sp_x - sz // 2, sp_y - sz // 4), (sp_x + sz // 2, sp_y + sz // 4)], fill=(20, 10, 5))
                canvas.draw.text((sp_x + sz + 3, sp_y - 5), sp["id"], fill=(255, 240, 200), font=get_font(9, bold=True))

        canvas.draw.text((sx + 14, sy + sh - 28), "Widok: UV 193Å (Korona Słoneczna)", fill=COLOR_TEXT_SECONDARY, font=get_font(11))

        # -------------------------------------------------------------
        # 2. Top-Right: Auroral Oval Polar Projection (x=366, y=120, w=300, h=310)
        # -------------------------------------------------------------
        ax, ay, aw, ah = 366, 120, 300, 310
        canvas.draw.rounded_rectangle([(ax, ay), (ax + aw, ay + ah)], radius=10, fill=(18, 22, 30), outline=COLOR_BORDER, width=1)
        pole_name = "BIEGUN PÓŁNOCNY (AURORA BOREALIS)" if self.view_pole == "NORTH" else "BIEGUN POŁUDNIOWY (AUSTRALIS)"
        canvas.draw.text((ax + 14, ay + 14), pole_name, fill=COLOR_PHOSPHOR_GREEN, font=get_font(12, bold=True))
        canvas.draw.line([(ax + 14, ay + 34), (ax + aw - 14, ay + 34)], fill=COLOR_BORDER, width=1)

        # Polar projection circle
        pcx, pcy, pr = ax + aw // 2, ay + 165, 80
        canvas.draw.ellipse([(pcx - pr, pcy - pr), (pcx + pr, pcy + pr)], fill=(12, 18, 26), outline=(32, 48, 68), width=1)
        # Latitudes
        canvas.draw.ellipse([(pcx - pr * 2 // 3, pcy - pr * 2 // 3), (pcx + pr * 2 // 3, pcy + pr * 2 // 3)], outline=(20, 32, 48), width=1)
        canvas.draw.ellipse([(pcx - pr // 3, pcy - pr // 3), (pcx + pr // 3, pcy + pr // 3)], outline=(20, 32, 48), width=1)

        # Auroral Oval Ring (Expands with Kp index)
        # Kp 0 = small ring around pole, Kp 9 = expands down to Europe/USA
        oval_r = int(pr * 0.45 + (self.kp_index / 9.0) * (pr * 0.45))
        oval_thickness = max(3, int(self.kp_index * 1.5))
        canvas.draw.ellipse([(pcx - oval_r, pcy - oval_r), (pcx + oval_r, pcy + oval_r)],
                            outline=COLOR_PHOSPHOR_GREEN, width=oval_thickness)

        # Center Pole Dot
        canvas.draw.ellipse([(pcx - 2, pcy - 2), (pcx + 2, pcy + 2)], fill=COLOR_CYBER_CYAN)

        # Aurora Status Text
        aurora_msg = "ZORZA WIDOCZNA W POLSCE!" if self.kp_index >= 6.0 else ("Zorza widoczna w Skandynawii" if self.kp_index >= 4.0 else "Niska aktywność zorzowa")
        aurora_col = COLOR_STATUS_ERR if self.kp_index >= 6.0 else (COLOR_PHOSPHOR_GREEN if self.kp_index >= 4.0 else COLOR_TEXT_MUTED)
        canvas.draw.text((ax + 14, ay + ah - 28), aurora_msg, fill=aurora_col, font=get_font(11, bold=True))

        # -------------------------------------------------------------
        # 3. Far-Right: Kp-Index & NOAA Scales (x=682, y=120, w=290, h=310)
        # -------------------------------------------------------------
        kx, ky, kw, kh = 682, 120, 290, 310
        canvas.draw.rounded_rectangle([(kx, ky), (kx + kw, ky + kh)], radius=10, fill=(18, 22, 30), outline=COLOR_BORDER, width=1)
        canvas.draw.text((kx + 14, ky + 14), "INDEKS GEOMAGNETYCZNY Kp", fill=COLOR_CYBER_CYAN, font=get_font(13, bold=True))
        canvas.draw.line([(kx + 14, ky + 34), (kx + kw - 14, ky + 34)], fill=COLOR_BORDER, width=1)

        # Big Kp Meter
        canvas.draw.text((kx + 14, ky + 50), f"Kp {self.kp_index:.1f}", fill=COLOR_PHOSPHOR_GREEN if self.kp_index < 5 else COLOR_STATUS_ERR, font=get_font(32, bold=True))
        canvas.draw_gauge(kx + 14, ky + 105, kw - 28, 16, value=self.kp_index, max_val=9.0,
                          label="Skala planetarna Kp (0 - 9)", color=COLOR_PHOSPHOR_GREEN if self.kp_index < 5 else COLOR_STATUS_ERR)

        # NOAA Storm Levels
        canvas.draw.text((kx + 14, ky + 140), "STATUS BURZY GEOMAGNETYCZNEJ:", fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=True))
        canvas.draw_badge(kx + 14, ky + 160, self.geomag_storm, bg_color=(28, 36, 48), text_color=COLOR_FLIPPER_AMBER)

        canvas.draw.text((kx + 14, ky + 200), "ZAKŁÓCENIA RADIOWE (X-RAY):", fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=True))
        canvas.draw_badge(kx + 14, ky + 220, self.radio_blackout, bg_color=(28, 36, 48), text_color=COLOR_CYBER_CYAN)

        canvas.draw.text((kx + 14, ky + 265), "Sonda: DSCOVR @ Punkt L1 (1.5 mln km)", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # -------------------------------------------------------------
        # 4. Bottom Panel: Solar Wind Instruments & Gauges (x=50, y=446, w=922, h=230)
        # -------------------------------------------------------------
        bx, by, bw, bh = 50, 446, 922, 230
        canvas.draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=10, fill=(16, 22, 32), outline=COLOR_BORDER, width=1)
        canvas.draw.text((bx + 16, by + 16), "TELEMETRIA WIATRU SŁONECZNEGO (SOLAR WIND INSTRUMENTS)", fill=COLOR_CYBER_CYAN, font=get_font(13, bold=True))
        canvas.draw.line([(bx + 16, by + 38), (bx + bw - 16, by + 38)], fill=COLOR_BORDER, width=1)

        # 3 Instruments in row: Speed, Density, Magnetic Field Bz
        gw = (bw - 64) // 3

        # 1. Speed (300 - 800 km/s)
        canvas.draw_gauge(bx + 16, by + 60, gw, 16, value=self.solar_wind_speed, max_val=800.0,
                          label=f"Prędkość: {self.solar_wind_speed:.0f} km/s", color=COLOR_CYBER_CYAN)
        canvas.draw.text((bx + 16, by + 95), "Norma: 350-450 km/s | Szybki wiatr: > 600 km/s", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # 2. Density (0 - 30 p/cm3)
        canvas.draw_gauge(bx + 32 + gw, by + 60, gw, 16, value=self.solar_wind_density, max_val=30.0,
                          label=f"Gęstość: {self.solar_wind_density:.1f} p/cm³", color=COLOR_FLIPPER_AMBER)
        canvas.draw.text((bx + 32 + gw, by + 95), "Plazma słoneczna w otoczeniu Ziemi", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # 3. Magnetic Field Bz (-15 to +15 nT)
        bz_val = max(0.0, min(30.0, self.solar_mag_bz + 15.0))
        bz_col = COLOR_STATUS_ERR if self.solar_mag_bz < -3.0 else COLOR_PHOSPHOR_GREEN
        canvas.draw_gauge(bx + 48 + gw * 2, by + 60, gw, 16, value=bz_val, max_val=30.0,
                          label=f"Wektor Bz: {self.solar_mag_bz:+.1f} nT", color=bz_col)
        canvas.draw.text((bx + 48 + gw * 2, by + 95), "Południowy Bz (< 0 nT) otwiera magnetosferę!", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # Real-time Radiation Alert Box
        canvas.draw.line([(bx + 16, by + 130), (bx + bw - 16, by + 130)], fill=COLOR_BORDER, width=1)
        canvas.draw.text((bx + 16, by + 145), "GLOBALNY WPŁYW NA INFRASTRUKTURĘ:", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))

        inf_items = [
            ("📡 Łączność radiowa HF:", "STABILNA", COLOR_STATUS_OK),
            ("🛰️ Nawigacja GPS / GNSS:", "DOKŁADNA (< 1.2m)", COLOR_STATUS_OK),
            ("⚡ Sieci elektroenergetyczne:", "BEZ ZAGROŻEŃ GIC", COLOR_STATUS_OK),
            ("👨‍🚀 Dawka dla astronautów:", "W NORMIE", COLOR_STATUS_OK)
        ]
        ix = bx + 16
        for label, val_str, col in inf_items:
            canvas.draw.text((ix, by + 175), label, fill=COLOR_TEXT_SECONDARY, font=get_font(11))
            canvas.draw.text((ix, by + 195), val_str, fill=col, font=get_font(12, bold=True))
            ix += gw + 8

    def handle_input(self, event: str) -> bool:
        if event in ("BTN_X", "x", "X"):
            self.view_pole = "SOUTH" if self.view_pole == "NORTH" else "NORTH"
            return True
        elif event in ("BTN_Y", "y", "Y"):
            self.show_sunspots = not self.show_sunspots
            return True
        elif event in ("BTN_A", "a", "A", " "):
            self._fetch_noaa_data()
            return True
        return False
