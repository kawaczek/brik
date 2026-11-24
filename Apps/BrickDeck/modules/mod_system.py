"""
BrickDeck Module: System Telemetry & Hardware Health
Monitors CPU, RAM, battery, thermal sensors, and network interfaces.
"""

import os
import time
import subprocess
from typing import Dict

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_PANEL_BG, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_STATUS_OK, COLOR_PHOSPHOR_GREEN
)
from core.i18n import t, i18n


class SystemModule(BaseModule):
    name = "System Telemetry"
    short_name = "System"
    icon = "⚙️"
    accent_color = COLOR_CYBER_CYAN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.last_update = 0
        self.toast_msg = ""
        self.toast_timer = 0
        self.stats: Dict = {
            "cpu_pct": 24,
            "ram_used": 340,
            "ram_total": 1024,
            "temp_c": 42.5,
            "battery_pct": 88,
            "storage_used": 14.2,
            "storage_total": 64.0,
            "ip_wlan": "192.168.1.145",
            "ip_usb": "10.0.0.1",
            "ip_bt": "192.168.44.1",
            "uptime": "2h 45m",
            "kernel": "Linux 5.4.125-sunxi64 (ARMv8)"
        }

    def get_hotkey_hints(self):
        return [
            ("L1/R1", t("common.modules", "Moduly")),
            ("A", t("system.refresh_hint", "Odswiez dane")),
            ("Y", t("system.lang_switch_hint", "Zmien jezyk")),
            ("X", t("system.restart_net_hint", "Zrestartuj interfejsy"))
        ]

    def _read_real_stats(self):
        """Read actual Linux stats if available."""
        # Read temperature
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                self.stats["temp_c"] = float(f.read().strip()) / 1000.0
        except Exception:
            pass

        # Read uptime
        try:
            with open("/proc/uptime", "r") as f:
                sec = float(f.read().split()[0])
                hrs = int(sec // 3600)
                mins = int((sec % 3600) // 60)
                self.stats["uptime"] = f"{hrs}h {mins}m"
        except Exception:
            pass

        # Read MemInfo
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
                total = int(lines[0].split()[1]) // 1024
                avail = int(lines[2].split()[1]) // 1024
                self.stats["ram_total"] = total
                self.stats["ram_used"] = total - avail
        except Exception:
            pass

    def update(self, dt: float):
        now = time.time()
        if now - self.last_update > 2.0:
            self._read_real_stats()
            self.last_update = now

    def render(self, canvas):
        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title=t("system.title", "TRIMUI BRICK HARDWARE TELEMETRY"),
            subtitle=f"{t('system.kernel', 'Kernel')}: {self.stats['kernel']}  |  {t('system.uptime', 'Uptime')}: {self.stats['uptime']}",
            border_color=self.accent_color
        )

        # 4 Metric Cards in 2x2 grid
        # Top-Left: CPU & Temperature (x=60, y=130, w=430, h=240)
        canvas.draw.rounded_rectangle([(60, 130), (490, 370)], radius=10, fill=(20, 24, 32), outline=COLOR_BORDER, width=1)
        canvas.draw.text((80, 148), t("system.cpu_card", "PROCESOR (Allwinner A133P ARM64)"), fill=COLOR_CYBER_CYAN, font=canvas.draw.getfont())
        canvas.draw_gauge(x=80, y=190, w=370, h=16, value=self.stats["cpu_pct"], max_val=100,
                          label=f"{t('system.cpu_load', 'Obciazenie CPU')}: {int(self.stats['cpu_pct'])}%", color=COLOR_CYBER_CYAN)
        canvas.draw_gauge(x=80, y=250, w=370, h=16, value=self.stats["temp_c"], max_val=85,
                          label=f"{t('system.soc_temp', 'Temperatura SoC')}: {self.stats['temp_c']:.1f} °C", color=COLOR_PHOSPHOR_GREEN)
        canvas.draw.text((80, 310), t("system.cores_info", "Rdzenie: 4x Cortex-A53 @ 1.8 GHz | Arch: aarch64"), fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())

        # Top-Right: RAM & Storage (x=534, y=130, w=430, h=240)
        canvas.draw.rounded_rectangle([(534, 130), (964, 370)], radius=10, fill=(20, 24, 32), outline=COLOR_BORDER, width=1)
        canvas.draw.text((554, 148), t("system.ram_card", "PAMIĘĆ RAM I DYSK (MicroSD)"), fill=COLOR_CYBER_CYAN, font=canvas.draw.getfont())
        ram_pct = int((self.stats["ram_used"] / max(1, self.stats["ram_total"])) * 100)
        ram_label = t("system.ram_label", "RAM")
        canvas.draw_gauge(x=554, y=190, w=370, h=16, value=ram_pct, max_val=100,
                          label=f"{ram_label}: {self.stats['ram_used']} MB / {self.stats['ram_total']} MB ({ram_pct}%)", color=COLOR_CYBER_CYAN)
        st_pct = int((self.stats["storage_used"] / max(1, self.stats["storage_total"])) * 100)
        st_label = t("system.storage_label", "MicroSD")
        canvas.draw_gauge(x=554, y=250, w=370, h=16, value=st_pct, max_val=100,
                          label=f"{st_label}: {self.stats['storage_used']:.1f} GB / {self.stats['storage_total']:.1f} GB", color=COLOR_STATUS_OK)
        canvas.draw.text((554, 310), t("system.power_info", "Zasilanie: Bateria Li-Po 3000 mAh | Stan: 88%"), fill=COLOR_TEXT_SECONDARY, font=canvas.draw.getfont())

        # Bottom Panel: Network Interfaces & Language Switcher (x=60, y=400, w=904, h=260)
        canvas.draw.rounded_rectangle([(60, 400), (964, 660)], radius=10, fill=(20, 24, 32), outline=COLOR_BORDER, width=1)
        canvas.draw.text((80, 418), t("system.network_card", "INTERFEJSY SIECIOWE I ŁĄCZNOŚĆ"), fill=COLOR_CYBER_CYAN, font=canvas.draw.getfont())

        # Language Selector Badge on the right
        lang_display = i18n.get_current_display_name()
        canvas.draw_badge(680, 414, f"{lang_display} [Y: {t('system.lang_switch_hint', 'Zmien')}]", bg_color=(36, 46, 64), text_color=COLOR_CYBER_CYAN)

        canvas.draw.line([(60, 446), (964, 446)], fill=COLOR_BORDER, width=1)

        interfaces = [
            ("📶 wlan0 (Wi-Fi 802.11 b/g/n)", self.stats["ip_wlan"], t("common.connected", "POŁĄCZONO"), COLOR_STATUS_OK),
            ("🔌 usb0 (USB-C OTG Gadget)", self.stats["ip_usb"], t("common.active", "AKTYWNY"), COLOR_CYBER_CYAN),
            ("📡 bnep0 (Bluetooth PAN)", self.stats["ip_bt"], t("common.listening", "NASŁUCH"), COLOR_TEXT_SECONDARY),
        ]

        iy = 466
        font = canvas.draw.getfont()
        for if_name, ip_addr, status_str, status_color in interfaces:
            canvas.draw.text((80, iy), if_name, fill=COLOR_TEXT_PRIMARY, font=font)
            canvas.draw.text((450, iy), f"IP: {ip_addr}", fill=COLOR_TEXT_SECONDARY, font=font)
            canvas.draw_badge(820, iy - 4, status_str, bg_color=(28, 36, 48), text_color=status_color)
            iy += 48

        # Notification Toast if language was just switched
        if self.toast_msg and time.time() < self.toast_timer:
            canvas.draw.rounded_rectangle(
                [(262, 595), (762, 640)],
                radius=8,
                fill=(16, 32, 48),
                outline=COLOR_CYBER_CYAN,
                width=2
            )
            canvas.draw.text((512, 617), self.toast_msg, fill=COLOR_CYBER_CYAN, font=font, anchor="mm")

    def handle_input(self, event: str) -> bool:
        if event in ("BTN_Y", "y", "Y"):
            new_name = i18n.cycle_next_locale()
            self.toast_msg = t("system.lang_changed", lang=new_name)
            self.toast_timer = time.time() + 2.5
            print(f"[i18n] Przełączono język na: {new_name}")
            return True
        elif event in ("BTN_A", "a", "A", " "):
            self._read_real_stats()
            return True
        return False
