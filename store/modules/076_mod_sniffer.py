#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class SnifferModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.packets_total = 1420
        self.kbps = 48.5
        self.dns_queries = [
            ("api.github.com", "A (IPv4)", "140.82.121.4", "OK"),
            ("pool.ntp.org", "UDP 123", "Czas sieciowy NTP", "OK"),
            ("google.com", "A (IPv4)", "142.250.203.206", "OK"),
            ("homeassistant.local", "mDNS 5353", "192.168.1.100", "LOKALNE"),
            ("telemetry.vendor.com", "HTTPS 443", "ZABLOKOWANO (PI-HOLE)", "BLOK"),
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "📡 076 // WI-FI PACKET SNIFFER & DNS QUERY INSPECTOR // INTERFEJS: WL0", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 240, 12, f"{self.packets_total} PAKIETÓW", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 90, 12, f"{self.kbps} KB/S", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Protocol Breakdown Card
        canvas.draw_card(20, 65, 984, 200, title="ROZKŁAD PROTOKOŁÓW SIECIOWYCH (PROMISCUOUS / LOCAL)", subtitle="Analiza nagłówków Ethernet / IP w czasie rzeczywistym")
        proto = [("TCP / TLS", 68, (0, 240, 255)), ("UDP", 22, (0, 255, 180)), ("DNS", 6, (255, 200, 0)), ("ICMP / ARP", 4, (255, 100, 100))]
        bx = 45
        for name, pct, col in proto:
            pw = int(914 * (pct / 100.0))
            draw.rectangle([bx, 125, bx + pw, 165], fill=col)
            draw.text((bx + 10, 175), f"{name}: {pct}%", fill=col, font=get_font(14, bold=True))
            bx += pw

        # DNS Query Table Card
        canvas.draw_card(20, 280, 984, 425, title="REJESTR ZAPYTAŃ DOMENOWYCH DNS & MDNS (PORT 53 / 5353)", subtitle="Ostatnio odpytywane serwery i adresy docelowe")
        for i, (domain, qtype, dest, status) in enumerate(self.dns_queries):
            dy = 345 + i * 68
            draw.rectangle([40, dy, 980, dy + 58], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((60, dy + 18), domain, fill=(240, 245, 255), font=get_font(15, bold=True))
            draw.text((420, dy + 20), qtype, fill=(140, 170, 200), font=get_font(13))
            draw.text((620, dy + 20), dest, fill=(0, 240, 255), font=get_font(14))
            stat_col = (255, 70, 70) if "BLOK" in status else (0, 255, 136)
            draw.text((860, dy + 18), status, fill=stat_col, font=get_font(14, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Listę Pakietów | [A]: Filtruj wg IP / Portu | [B]: Wyczyść Bufor | [Y]: Zapisz PCAP", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
