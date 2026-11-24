#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class IpamPlannerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.supernet = "10.0.0.0/16 (65 536 Adresów IP)"
        self.subnets = [
            ("VLAN 10 // INFRASTRUKTURA SERWEROWA", "10.0.1.0/24", "254 hosty", True),
            ("VLAN 20 // STACJE ROBOCZE I BIURO", "10.0.2.0/23", "510 hostów", True),
            ("VLAN 50 // SIEĆ WI-FI DLA GOŚCI", "10.0.4.0/24", "254 hosty", True),
            ("VLAN 99 // ZARZĄDZANIE OOB / IPMI", "10.0.10.0/26", "62 hosty", True),
            ("WOLNA PRZESTRZEŃ ADRESOWA", "10.0.11.0/24", "Dostępna", False),
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🗺️ 080 // SUBNET CIDR MATRIX & IPAM PLANNER // {self.supernet}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "IPAM // RFC 1918", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 80, 12, "VLAN", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Visual Grid of Address Blocks
        canvas.draw_card(20, 65, 984, 180, title="WIZUALNA MATRYCA PODZIAŁU PRZESTRZENI /16", subtitle="Klockowy podział na podsieci bez nakładania się zakresów")
        bx = 40
        widths = [180, 320, 180, 90, 170]
        cols = [(0, 240, 255), (0, 255, 136), (255, 170, 0), (180, 80, 255), (30, 45, 65)]
        for i, (name, cidr, hosts, used) in enumerate(self.subnets):
            w_block = widths[i]
            draw.rectangle([bx, 120, bx + w_block, 200], fill=cols[i])
            draw.text((bx + 10, 135), cidr, fill=(10, 15, 25) if used else (160, 180, 210), font=get_font(14, bold=True))
            draw.text((bx + 10, 165), hosts, fill=(10, 15, 25) if used else (120, 140, 170), font=get_font(12, bold=True))
            bx += w_block + 4

        # Detailed Subnet Table Card
        canvas.draw_card(20, 260, 984, 445, title="REJESTR PODSIECI I BRAM DOMYŚLNYCH", subtitle="Konfiguracja routerów i serwerów DHCP")
        for i, (name, cidr, hosts, used) in enumerate(self.subnets):
            sy = 320 + i * 72
            draw.rectangle([40, sy, 980, sy + 62], fill=(16, 24, 38), outline=(0, 200, 255) if used else (40, 60, 85))
            draw.text((60, sy + 12), name, fill=(0, 255, 180) if used else (120, 140, 170), font=get_font(14, bold=True))
            draw.text((60, sy + 35), f"Zakres CIDR: {cidr}  |  Pojemność: {hosts}", fill=(220, 235, 255), font=get_font(13))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Podsieć | [A]: Podziel na Dwie (/+1) | [B]: Połącz Podsieci | [Y]: Eksport Bazy", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
