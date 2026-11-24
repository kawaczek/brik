#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class E6bFlightComputerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.tas = 120.0     # True Airspeed kt
        self.course = 045.0  # Course deg
        self.wind_dir = 320.0
        self.wind_spd = 25.0
        self.fuel_flow = 8.5 # GPH
        self.density_alt = 4500 # ft

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 14, 24, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "✈️ 057 // E6B FLIGHT COMPUTER // CYFROWY SUWAK PILOTA", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "TRÓJKĄT WIATRU", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 90, 12, "VFR / IFR", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Wind Triangle Card
        canvas.draw_card(20, 65, 500, 440, title="WIND TRIANGLE & GROUND SPEED", subtitle="Kalkulator znoszenia i prędkości podróżnej")
        draw.text((45, 130), f"Prędkość rzeczywista (TAS): {self.tas:.0f} kt", fill=(240, 245, 255), font=get_font(16))
        draw.text((45, 165), f"Kurs magnetyczny: {self.course:.0f}°", fill=(240, 245, 255), font=get_font(16))
        draw.text((45, 200), f"Wiatr: {self.wind_dir:.0f}° / {self.wind_spd:.0f} kt", fill=(255, 170, 0), font=get_font(16, bold=True))
        
        # Wind calculations
        wca = -11.4 # Wind correction angle
        gs = 108.5  # Ground speed
        draw.rectangle([45, 250, 475, 410], fill=(14, 22, 34), outline=(0, 255, 180), width=2)
        draw.text((65, 275), f"KĄT ZNOSZENIA (WCA): {wca:+.1f}°", fill=(0, 255, 180), font=get_font(18, bold=True))
        draw.text((65, 315), f"NAMIAR MAGNETYCZNY (HDG): {self.course + wca:.1f}°", fill=(255, 220, 0), font=get_font(18, bold=True))
        draw.text((65, 355), f"PRĘDKOŚĆ WZGLĘDEM ZIEMI (GS): {gs:.1f} kt", fill=(0, 240, 255), font=get_font(20, bold=True))

        # Fuel & Distance Card
        canvas.draw_card(540, 65, 464, 440, title="PALIWO, CZAS I ZASIĘG", subtitle="Zużycie paliwa AvGas / Jet-A1")
        draw.text((565, 130), f"Zużycie (Fuel Flow): {self.fuel_flow} GPH (galon/h)", fill=(240, 245, 255), font=get_font(16))
        draw.text((565, 170), "Dystans do celu: 180 NM", fill=(240, 245, 255), font=get_font(16))
        draw.text((565, 210), "Czas lotu (ETE): 01h 39m", fill=(0, 255, 136), font=get_font(20, bold=True))
        draw.text((565, 250), "Wymagane paliwo: 14.1 galonów", fill=(255, 200, 0), font=get_font(18, bold=True))
        draw.text((565, 290), "Rezerwa paliwa VFR 45 min: +6.4 galona", fill=(160, 180, 210), font=get_font(14))

        # Bottom Altitude Card
        canvas.draw_card(20, 520, 984, 190, title="WYSOKOŚĆ GĘSTOŚCIOWA & PUNKT BEZPOWROTU (PET / PNR)", subtitle="Density Altitude & Critical Point")
        draw.text((45, 580), f"Wysokość gęstościowa (Density Altitude): {self.density_alt} ft (Rozbieg wydłużony o 28%)", fill=(255, 180, 0), font=get_font(16, bold=True))
        draw.text((45, 620), "Punkt bezpiecznego powrotu (Point of Safe Return): 94 NM od lotniska odlotu", fill=(0, 255, 180), font=get_font(15))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Góra/Dół: Zmiana Prędkości TAS | Lewo/Prawo: Kurs | [A]: Edycja Wiatru", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
