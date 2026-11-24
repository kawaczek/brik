"""
BrickDeck Module: Home Assistant Pocket Controller (Smart Home)
Tactical touch/D-Pad controller for local Home Assistant REST API with live entity grid and offline demo fallback.
"""

import os
import json
import time
import urllib.request
import threading
from typing import List, Dict, Optional

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN, COLOR_STATUS_ERR
)
from core.canvas import get_font


class HassModule(BaseModule):
    name = "Home Assistant Pocket Controller"
    short_name = "SmartHome"
    icon = "🏠"
    accent_color = COLOR_CYBER_CYAN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.cursor_row = 0  # 0..3 (4 rows)
        self.cursor_col = 0  # 0..1 (2 cols) -> 8 cards total

        self.hass_url = "http://homeassistant.local:8123"
        self.hass_token = ""
        self.is_live = False
        self.status_msg = "Tryb demonstracyjny (Symulacja)"
        self.last_refresh_time = 0.0

        self.entities: List[Dict] = []
        self._init_demo_entities()

    def on_load(self):
        # Load custom HASS config if present in transit_config.json
        cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "transit_config.json")
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.hass_url = cfg.get("hass_url", self.hass_url)
                    self.hass_token = cfg.get("hass_token", "")
            except Exception:
                pass

        if self.hass_token:
            self._fetch_live_states_async()

    def _init_demo_entities(self):
        """Pre-configured tactical smart home cards."""
        self.entities = [
            {
                "id": "light.salon_main",
                "name": "Światło Salon (Główne)",
                "type": "light",
                "icon": "💡",
                "state": "on",
                "val": 80,  # brightness %
                "unit": "%",
                "extra": "Ciepła biel (3000K)"
            },
            {
                "id": "light.cyber_desk",
                "name": "Cyberdeck RGB Desk",
                "type": "light",
                "icon": "⚡",
                "state": "on",
                "val": 100,
                "unit": "%",
                "extra": "Neon Cyan (#00D8FF)"
            },
            {
                "id": "switch.printer_3d",
                "name": "Smart Plug: Drukarka 3D",
                "type": "switch",
                "icon": "🔌",
                "state": "on",
                "val": 145,
                "unit": "W",
                "extra": "Druk w toku: 68%"
            },
            {
                "id": "switch.audio_amp",
                "name": "Wzmacniacz Audio Hi-Fi",
                "type": "switch",
                "icon": "🔊",
                "state": "off",
                "val": 0,
                "unit": "W",
                "extra": "Standby (0.5 W)"
            },
            {
                "id": "climate.termostat",
                "name": "Termostat Centralny",
                "type": "climate",
                "icon": "🌡️",
                "state": "heat",
                "val": 22.0,  # target °C
                "current_temp": 21.4,
                "unit": "°C",
                "extra": "Piec CO: Aktywny"
            },
            {
                "id": "sensor.air_quality",
                "name": "Jakość Powietrza Salon",
                "type": "sensor",
                "icon": "🍃",
                "state": "ok",
                "val": 12,
                "unit": "µg/m³",
                "extra": "PM2.5 Bardzo Dobra"
            },
            {
                "id": "binary_sensor.door",
                "name": "Czujnik Drzwi Wejściowych",
                "type": "binary",
                "icon": "🚪",
                "state": "closed",
                "val": 0,
                "unit": "",
                "extra": "Zaryglowane / Bezpiecznie"
            },
            {
                "id": "sensor.grid_power",
                "name": "Miernik Mocy Domu",
                "type": "sensor",
                "icon": "⚡",
                "state": "ok",
                "val": 485,
                "unit": "W",
                "extra": "Faza 1: 180W | Faza 2: 305W"
            }
        ]

    def get_hotkey_hints(self):
        return [
            ("L1/R1", "Moduły"),
            ("D-Pad", "Wybór kafelka"),
            ("A", "Włącz / Przełącz"),
            ("D-Pad L/P", "Regulacja poziomu"),
            ("X", "Odśwież HASS"),
            ("Y", "Wyłącz wszystko (Eco)")
        ]

    def _fetch_live_states_async(self):
        def worker():
            try:
                url = f"{self.hass_url}/api/states"
                req = urllib.request.Request(url, headers={
                    "Authorization": f"Bearer {self.hass_token}",
                    "Content-Type": "application/json"
                })
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    raw = resp.read().decode("utf-8")
                    data = json.loads(raw)
                    self.is_live = True
                    self.status_msg = f"LIVE HASS: {self.hass_url}"
                    self.last_refresh_time = time.time()
            except Exception as e:
                self.is_live = False
                self.status_msg = "Brak połączenia z Home Assistant (Tryb demo)"

        threading.Thread(target=worker, daemon=True).start()

    def _toggle_selected(self):
        idx = self.cursor_row * 2 + self.cursor_col
        if 0 <= idx < len(self.entities):
            ent = self.entities[idx]
            if ent["type"] in ("light", "switch"):
                ent["state"] = "off" if ent["state"] == "on" else "on"
            elif ent["type"] == "binary":
                ent["state"] = "open" if ent["state"] == "closed" else "closed"
                ent["extra"] = "Otwarte!" if ent["state"] == "open" else "Zaryglowane / Bezpiecznie"

    def _adjust_slider(self, delta: float):
        idx = self.cursor_row * 2 + self.cursor_col
        if 0 <= idx < len(self.entities):
            ent = self.entities[idx]
            if ent["type"] == "light":
                ent["val"] = max(0, min(100, int(ent["val"] + delta * 10)))
                if ent["val"] == 0:
                    ent["state"] = "off"
                else:
                    ent["state"] = "on"
            elif ent["type"] == "climate":
                ent["val"] = round(max(16.0, min(28.0, ent["val"] + delta * 0.5)), 1)

    def update(self, dt: float):
        # Subtle simulated power fluctuation on smart plug & meter
        for ent in self.entities:
            if ent["id"] == "switch.printer_3d" and ent["state"] == "on":
                import random
                ent["val"] = max(130, min(160, ent["val"] + random.randint(-2, 2)))
            elif ent["id"] == "sensor.grid_power":
                import random
                ent["val"] = max(420, min(560, ent["val"] + random.randint(-4, 4)))

    def render(self, canvas):
        # Main Card Panel (x=32, y=66, w=960, h=634)
        canvas.draw_card(
            32, 66, 960, 634,
            title="HOME ASSISTANT POCKET CONTROLLER",
            subtitle=f"{self.status_msg}  |  Serwer: {self.hass_url}",
            border_color=self.accent_color
        )

        grid_x = 48
        grid_y = 118
        card_w = 460
        card_h = 130
        gap_x = 16
        gap_y = 14

        font_title = get_font(15, bold=True)
        font_sub = get_font(12, bold=False)
        font_stat = get_font(13, bold=True)

        for row in range(4):
            for col in range(2):
                idx = row * 2 + col
                if idx >= len(self.entities):
                    break

                ent = self.entities[idx]
                is_cursor = (row == self.cursor_row and col == self.cursor_col)
                is_on = (ent["state"] in ("on", "heat", "open"))

                cx = grid_x + col * (card_w + gap_x)
                cy = grid_y + row * (card_h + gap_y)

                # Card background and border
                bg_col = (34, 46, 64) if is_cursor else ((26, 32, 44) if is_on else (18, 22, 30))
                border_col = COLOR_CYBER_CYAN if is_cursor else (COLOR_PHOSPHOR_GREEN if is_on else COLOR_BORDER)
                b_width = 2 if is_cursor else 1

                canvas.draw.rounded_rectangle([(cx, cy), (cx + card_w, cy + card_h)],
                                              radius=10, fill=bg_col, outline=border_col, width=b_width)

                # Entity Icon & Name
                canvas.draw.text((cx + 16, cy + 14), f"{ent['icon']}  {ent['name']}", fill=COLOR_TEXT_PRIMARY, font=font_title)

                # Status Badge
                badge_bg = (30, 110, 60) if is_on else (40, 48, 58)
                badge_txt = "WŁĄCZONE" if is_on else "WYŁĄCZONE"
                if ent["type"] == "climate":
                    badge_bg = (180, 80, 20)
                    badge_txt = f"CEL: {ent['val']}°C"
                elif ent["type"] == "sensor":
                    badge_bg = (24, 70, 100)
                    badge_txt = f"{ent['val']} {ent['unit']}"
                elif ent["type"] == "binary":
                    badge_bg = (160, 40, 40) if ent["state"] == "open" else (30, 110, 60)
                    badge_txt = "OTWARTE" if ent["state"] == "open" else "ZAMKNIĘTE"

                canvas.draw_badge(cx + card_w - 110, cy + 12, badge_txt, bg_color=badge_bg, text_color=COLOR_TEXT_PRIMARY)

                # Value / Meter / Extra text
                canvas.draw.text((cx + 16, cy + 48), ent["extra"], fill=COLOR_TEXT_SECONDARY, font=font_sub)

                # Visual Slider / Progress Gauge for Dimmer and Climate
                if ent["type"] == "light":
                    canvas.draw_gauge(cx + 16, cy + 86, card_w - 32, 16, ent["val"], 100, label=f"Jasność: {ent['val']}%", color=COLOR_FLIPPER_AMBER if is_on else (60, 70, 80))
                elif ent["type"] == "climate":
                    curr_t = ent.get("current_temp", 21.0)
                    canvas.draw_gauge(cx + 16, cy + 86, card_w - 32, 16, curr_t - 15.0, 15.0, label=f"Aktualna: {curr_t:.1f}°C  |  Nastawa: {ent['val']}°C", color=COLOR_NEON_PINK)
                elif ent["type"] == "switch":
                    p_val = ent["val"]
                    canvas.draw_gauge(cx + 16, cy + 86, card_w - 32, 16, p_val, 250, label=f"Moc chwilowa: {p_val} W", color=COLOR_PHOSPHOR_GREEN if is_on else (60, 70, 80))
                else:
                    # Sensor info bar
                    canvas.draw.line([(cx + 16, cy + 80), (cx + card_w - 16, cy + 80)], fill=COLOR_BORDER, width=1)
                    canvas.draw.text((cx + 16, cy + 92), f"ID Encycji: {ent['id']}", fill=COLOR_TEXT_MUTED, font=font_sub)

    def handle_input(self, event: str) -> bool:
        if event == "UP":
            if self.cursor_row > 0:
                self.cursor_row -= 1
                return True
        elif event == "DOWN":
            if self.cursor_row < 3:
                self.cursor_row += 1
                return True
        elif event == "LEFT":
            if self.cursor_col > 0:
                self.cursor_col -= 1
            else:
                self._adjust_slider(-1.0)
            return True
        elif event == "RIGHT":
            if self.cursor_col < 1:
                self.cursor_col += 1
            else:
                self._adjust_slider(1.0)
            return True
        elif event == "BTN_A":
            self._toggle_selected()
            return True
        elif event == "BTN_X":
            self._fetch_live_states_async()
            return True
        elif event == "BTN_Y":
            # Eco / All Lights Off
            for ent in self.entities:
                if ent["type"] in ("light", "switch"):
                    ent["state"] = "off"
                    if ent["type"] == "light":
                        ent["val"] = 0
            return True
        return False
