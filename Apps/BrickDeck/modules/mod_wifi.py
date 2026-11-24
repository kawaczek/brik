"""
BrickDeck Module: Wi-Fi 2.4 GHz Spectrum Analyzer
Visualizes 2.4 GHz channel congestion (Channels 1..14) and nearby Access Points.
"""

from typing import List, Dict
from core.module_base import BaseModule
from core.theme import (
    COLOR_PHOSPHOR_GREEN, COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY
)


class WifiModule(BaseModule):
    name = "Wi-Fi Spectrum Analyzer"
    short_name = "Wi-Fi"
    icon = "📶"
    accent_color = COLOR_PHOSPHOR_GREEN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.selected_ap_idx = 0
        self.channels = list(range(1, 15))
        # Initial simulated channel traffic levels (channels 1..14)
        self.channel_loads = [65, 12, 5, 8, 10, 85, 20, 15, 10, 5, 75, 18, 5, 0]
        self.access_points = [
            {"ssid": "CyberHome_5G_Ext", "bssid": "34:8A:12:90:BB:11", "ch": 6, "rssi": -42, "sec": "WPA3-SAE"},
            {"ssid": "Netgear_IoT_Guest", "bssid": "9C:3D:CF:14:22:98", "ch": 1, "rssi": -58, "sec": "WPA2-PSK"},
            {"ssid": "Livebox-Lab-2.4G", "bssid": "00:1F:33:DE:44:A1", "ch": 11, "rssi": -65, "sec": "WPA2-PSK"},
            {"ssid": "Pwngotchi-AdHoc", "bssid": "B8:27:EB:AA:BB:CC", "ch": 6, "rssi": -49, "sec": "OPEN"},
            {"ssid": "Office_Cisco_Mesh", "bssid": "70:DB:98:31:AA:FF", "ch": 1, "rssi": -78, "sec": "WPA2-ENT"},
        ]

    def get_hotkey_hints(self):
        return [
            ("L1/R1", "Moduly"),
            ("D-Pad", "Wybierz AP"),
            ("X", "Reskanuj pasmo"),
            ("A", "Szczegoly kanalu")
        ]

    def render(self, canvas):
        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title="WI-FI 2.4 GHz SPECTRUM & CHANNELS",
            subtitle=f"Wykryte sieci: {len(self.access_points)}  |  Zakres pasma: 2412 MHz - 2484 MHz",
            border_color=self.accent_color
        )

        # 1. Top Panel: Spectrum Bar Chart (x=60, y=130, w=900, h=180)
        canvas.draw.text((60, 115), "ZAJĘTOŚĆ KANAŁÓW (1 - 14):",
                         fill=COLOR_PHOSPHOR_GREEN, font=canvas.draw.getfont())

        # Determine which channel is highlighted based on selected AP
        active_ch_idx = -1
        if 0 <= self.selected_ap_idx < len(self.access_points):
            active_ch_idx = self.access_points[self.selected_ap_idx]["ch"] - 1

        canvas.draw_bar_chart(
            x=60, y=140, w=904, h=160,
            labels=[f"Ch{c}" for c in self.channels],
            values=self.channel_loads,
            max_val=100.0,
            active_idx=active_ch_idx,
            bar_color=COLOR_PHOSPHOR_GREEN
        )

        # 2. Bottom Panel: Access Points List Table (x=60, y=350, w=904, h=330)
        table_y = 350
        canvas.draw.rounded_rectangle(
            [(60, table_y), (964, table_y + 330)],
            radius=8, fill=(18, 22, 30), outline=COLOR_BORDER, width=1
        )
        canvas.draw.text((80, table_y + 12), "SSID / NAZWA SIECI", fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
        canvas.draw.text((400, table_y + 12), "BSSID (MAC)", fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
        canvas.draw.text((620, table_y + 12), "KANAŁ", fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
        canvas.draw.text((710, table_y + 12), "SZYFROWANIE", fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
        canvas.draw.text((840, table_y + 12), "SYGNAŁ", fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
        canvas.draw.line([(60, table_y + 36), (964, table_y + 36)], fill=COLOR_BORDER, width=1)

        row_y = table_y + 44
        for idx, ap in enumerate(self.access_points):
            is_sel = (idx == self.selected_ap_idx)
            row_h = 48

            if is_sel:
                canvas.draw.rounded_rectangle(
                    [(66, row_y), (958, row_y + row_h)],
                    radius=6, fill=(30, 42, 54), outline=COLOR_PHOSPHOR_GREEN, width=2
                )
            else:
                canvas.draw.rounded_rectangle(
                    [(66, row_y), (958, row_y + row_h)],
                    radius=6, fill=(22, 26, 36)
                )

            # Columns
            col_text = COLOR_TEXT_PRIMARY if not is_sel else COLOR_PHOSPHOR_GREEN
            canvas.draw.text((80, row_y + 14), ap["ssid"], fill=col_text, font=canvas.draw.getfont())
            canvas.draw.text((400, row_y + 14), ap["bssid"], fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())
            canvas.draw.text((630, row_y + 14), f"Ch {ap['ch']}", fill=COLOR_FLIPPER_AMBER, font=canvas.draw.getfont())
            canvas.draw.text((710, row_y + 14), ap["sec"], fill=COLOR_TEXT_PRIMARY, font=canvas.draw.getfont())

            rssi = ap["rssi"]
            sig_pct = max(0, min(100, (rssi + 100) * 2))
            canvas.draw_gauge(x=840, y=row_y + 18, w=100, h=12,
                              value=sig_pct, max_val=100, color=COLOR_PHOSPHOR_GREEN)

            row_y += row_h + 8

    def handle_input(self, event: str) -> bool:
        if event == "UP":
            self.selected_ap_idx = (self.selected_ap_idx - 1) % len(self.access_points)
            return True
        elif event == "DOWN":
            self.selected_ap_idx = (self.selected_ap_idx + 1) % len(self.access_points)
            return True
        elif event == "BTN_X":
            # Simulate slight RSSI noise / variation
            for i in range(len(self.channel_loads)):
                self.channel_loads[i] = max(5, min(95, self.channel_loads[i] + (i % 7 - 3)))
            return True
        return False
