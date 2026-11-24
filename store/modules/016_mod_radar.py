"""
BrickDeck Module: Tactical Bluetooth BLE Radar
Scans for nearby Bluetooth / BLE devices and visualizes them on a 360° sweeping radar.
"""

import math
import time
import subprocess
from typing import List, Dict

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_PANEL_BG, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_FLIPPER_AMBER, COLOR_NEON_PINK
)


class RadarModule(BaseModule):
    name = "Tactical BLE Radar"
    short_name = "BLE Radar"
    icon = "📡"
    accent_color = COLOR_CYBER_CYAN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.sweep_angle = 0.0
        self.selected_device_idx = 0
        self.devices: List[Dict] = []
        self._init_mock_devices()

    def _init_mock_devices(self):
        """Default ambient BLE targets."""
        self.devices = [
            {"name": "Flipper Zero [White]", "mac": "80:E1:26:A1:3B:42", "rssi": -48, "angle": 45, "dist": 0.35, "type": "flipper"},
            {"name": "Pwngotchi-BT", "mac": "B8:27:EB:12:34:56", "rssi": -55, "angle": 130, "dist": 0.45, "type": "pi"},
            {"name": "Nordic_BLE_Beacon", "mac": "C4:4F:33:8A:90:12", "rssi": -72, "angle": 210, "dist": 0.70, "type": "beacon"},
            {"name": "Mi Smart Band 7", "mac": "D2:11:44:88:99:AA", "rssi": -64, "angle": 290, "dist": 0.58, "type": "wearable"},
            {"name": "Unknown BLE Tag", "mac": "FA:CE:B0:0C:13:37", "rssi": -85, "angle": 340, "dist": 0.88, "type": "unknown"},
        ]

    def get_hotkey_hints(self):
        return [
            ("L1/R1", "Moduly"),
            ("D-Pad", "Wybierz cel"),
            ("A", "Pinguj cel"),
            ("X", "Skanuj otoczenie")
        ]

    def update(self, dt: float):
        # Rotate radar sweep beam at ~90 degrees per second
        self.sweep_angle = (self.sweep_angle + dt * 100) % 360

    def render(self, canvas):
        # Main card panel
        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title="TACTICAL BLUETOOTH RADAR",
            subtitle=f"Aktywne cele w zasiegu: {len(self.devices)}  |  Kat wiazki: {int(self.sweep_angle)}°",
            border_color=self.accent_color
        )

        # Draw Radar on left side: Center = (290, 390), Radius = 230
        radar_cx = 290
        radar_cy = 390
        radar_r = 230

        # Prepare blips for canvas widget
        blips = []
        for dev in self.devices:
            blips.append({
                "angle": dev["angle"],
                "dist": dev["dist"],
                "label": dev["name"],
                "rssi": dev["rssi"]
            })

        canvas.draw_radar(cx=radar_cx, cy=radar_cy, radius=radar_r,
                          sweep_angle=self.sweep_angle, blips=blips)

        # Highlight selected device with pulsing crosshair ring on radar
        if 0 <= self.selected_device_idx < len(self.devices):
            sel_dev = self.devices[self.selected_device_idx]
            s_rad = math.radians(sel_dev["angle"])
            s_dist = sel_dev["dist"] * radar_r
            bx = radar_cx + int(s_dist * math.cos(s_rad))
            by = radar_cy + int(s_dist * math.sin(s_rad))
            canvas.draw.ellipse([(bx - 14, by - 14), (bx + 14, by + 14)],
                                outline=COLOR_CYBER_CYAN, width=2)

        # Draw Device List Panel on right side (x=570, y=120, w=400, h=550)
        list_x = 570
        list_y = 120
        list_w = 400
        canvas.draw.rounded_rectangle(
            [(list_x, list_y), (list_x + list_w, list_y + 550)],
            radius=10, fill=(20, 24, 32), outline=COLOR_BORDER, width=1
        )
        canvas.draw.text((list_x + 16, list_y + 14), "WYKRYTE URZADZENIA BLE",
                         fill=COLOR_CYBER_CYAN, font=canvas.draw.getfont())
        canvas.draw.line([(list_x + 12, list_y + 40), (list_x + list_w - 12, list_y + 40)],
                         fill=COLOR_BORDER, width=1)

        item_y = list_y + 52
        for idx, dev in enumerate(self.devices):
            is_selected = (idx == self.selected_device_idx)
            item_h = 74

            # Highlight selected item
            if is_selected:
                canvas.draw.rounded_rectangle(
                    [(list_x + 10, item_y), (list_x + list_w - 10, item_y + item_h)],
                    radius=8, fill=(32, 44, 60), outline=COLOR_CYBER_CYAN, width=2
                )
            else:
                canvas.draw.rounded_rectangle(
                    [(list_x + 10, item_y), (list_x + list_w - 10, item_y + item_h)],
                    radius=8, fill=(24, 28, 38)
                )

            # Device Icon & Name
            icon = "🐬" if "Flipper" in dev["name"] else ("👻" if "Pwngotchi" in dev["name"] else "📡")
            canvas.draw.text((list_x + 20, item_y + 10), f"{icon} {dev['name']}",
                             fill=COLOR_TEXT_PRIMARY, font=canvas.draw.getfont())
            canvas.draw.text((list_x + 20, item_y + 32), f"MAC: {dev['mac']}",
                             fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())

            # RSSI Signal Gauge
            rssi = dev["rssi"]
            signal_pct = max(0, min(100, (rssi + 100) * 2))
            canvas.draw.text((list_x + 20, item_y + 50), f"Sygnal: {rssi} dBm",
                             fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
            canvas.draw_gauge(x=list_x + 240, y=item_y + 52, w=130, h=12,
                              value=signal_pct, max_val=100, color=COLOR_CYBER_CYAN)

            item_y += item_h + 12

    def handle_input(self, event: str) -> bool:
        if event == "UP":
            self.selected_device_idx = (self.selected_device_idx - 1) % len(self.devices)
            return True
        elif event == "DOWN":
            self.selected_device_idx = (self.selected_device_idx + 1) % len(self.devices)
            return True
        elif event == "BTN_X":
            # Rescan trigger
            self._init_mock_devices()
            return True
        return False
