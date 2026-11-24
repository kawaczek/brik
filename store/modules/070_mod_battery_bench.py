#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class BatteryBenchModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.voltage_mv = 3920
        self.capacity_mah = 2840 # out of 3000
        self.health = 94.6
        self.discharge_ma = 480
        self.eta_hours = 5.9
        self.temp_c = 34.2
        self.samples = [4180, 4120, 4060, 4010, 3960, 3920]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 136, 100), width=1)
        draw.text((20, 14), "🔋 070 // BATTERY BENCHMARK & HARDWARE DISCHARGE PROFILER", fill=(0, 255, 136), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "OGNIWO LI-PO 3000 MAH", bg_color=(20, 45, 30))
        canvas.draw_badge(w - 85, 12, f"{self.health:.1f}%", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Battery Health Card
        canvas.draw_card(20, 65, 480, 440, title="KONDYCJA AKUMULATORA (SOH)", subtitle="Pomiar napięcia i szacowana degradacja chemiczna")
        draw.text((50, 135), f"{self.health:.1f}%", fill=(0, 255, 136), font=get_font(74, bold=True))
        draw.text((50, 240), f"Pojemność rzeczywista: {self.capacity_mah} / 3000 mAh", fill=(240, 245, 255), font=get_font(16, bold=True))
        draw.text((50, 280), f"Napięcie ogniwa: {self.voltage_mv} mV (3.92 V)", fill=(0, 200, 255), font=get_font(16))
        draw.text((50, 315), f"Pobór prądu: {self.discharge_ma} mA (Moc: 1.88 W)", fill=(255, 180, 0), font=get_font(16))
        draw.text((50, 350), f"Temperatura baterii: {self.temp_c}°C (W normie)", fill=(0, 255, 180), font=get_font(16))
        draw.text((50, 400), f"Szacowany czas pracy: {self.eta_hours:.1f} godzin", fill=(0, 255, 136), font=get_font(20, bold=True))

        # Discharge Curve Chart
        canvas.draw_card(520, 65, 484, 440, title="KRZYWA ROZŁADOWANIA (DISCHARGE mV)", subtitle="Rejestracja napięcia w funkcji czasu (Krok 30 min)")
        draw.rectangle([545, 125, 975, 470], fill=(14, 20, 30), outline=(0, 180, 220))
        for i in range(len(self.samples) - 1):
            x1 = 570 + i * 75
            x2 = 570 + (i + 1) * 75
            y1 = 440 - int((self.samples[i] - 3400) * 0.4)
            y2 = 440 - int((self.samples[i + 1] - 3400) * 0.4)
            draw.line([(x1, y1), (x2, y2)], fill=(0, 255, 180), width=3)
            draw.ellipse([(x1 - 4, y1 - 4), (x1 + 4, y1 + 4)], fill=(255, 200, 0))
        draw.text((560, 135), "4.20V (100%)", fill=(120, 150, 180), font=get_font(12))
        draw.text((560, 445), "3.40V (KRYTYCZNE)", fill=(255, 80, 80), font=get_font(12))

        # Bottom Stress Test Modes
        canvas.draw_card(20, 520, 984, 190, title="PROFILE OBCIĄŻENIOWE KONSOLI (STRESS BENCHMARK)", subtitle="Testowanie poboru energii w różnych stanach pracy")
        draw.text((45, 580), "• IDLE (Ekran 30%, CPU 400 MHz): 180 mA (~16h)  |  • RETRO GAMING (CPU 1.2 GHz): 450 mA (~6.5h)", fill=(220, 235, 255), font=get_font(15))
        draw.text((45, 620), "• MAX STRESS (4 rdzenie 1.8 GHz, Wi-Fi, Ekran 100%): 820 mA (~3.6h)", fill=(255, 170, 0), font=get_font(15, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Profil Testowy | [A]: Uruchom Test Rozładowania | [Y]: Eksport Wykresu do CSV", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
