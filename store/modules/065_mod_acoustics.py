#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AcousticsModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.length = 5.0 # m
        self.width = 4.0  # m
        self.height = 2.6 # m
        self.speed_of_sound = 343.0 # m/s (20C)

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "📐 065 // KALKULATOR AKUSTYKI POKOJU & MODY OSIOWE (ROOM MODES)", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "WYNIK RT60: 0.42S", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "343 M/S", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Room Dimensions Card
        canvas.draw_card(20, 65, 480, 440, title="WYMIARY POMIESZCZENIA", subtitle="Kubatura i proporcje wg kryterium Bonello")
        draw.text((45, 130), f"Długość (L):  {self.length:.2f} m", fill=(240, 245, 255), font=get_font(18))
        draw.text((45, 170), f"Szerokość (W): {self.width:.2f} m", fill=(240, 245, 255), font=get_font(18))
        draw.text((45, 210), f"Wysokość (H):  {self.height:.2f} m", fill=(240, 245, 255), font=get_font(18))
        vol = self.length * self.width * self.height
        draw.text((45, 260), f"Kubatura pokoju: {vol:.1f} m³", fill=(255, 200, 0), font=get_font(16, bold=True))

        # Axial Modes Card
        canvas.draw_card(520, 65, 484, 440, title="NAJNIEŻSZE MODY OSIOWE (FALE STOJĄCE)", subtitle="Częstotliwości podbicia i wygaszania basu")
        fl = self.speed_of_sound / (2 * self.length)
        fw = self.speed_of_sound / (2 * self.width)
        fh = self.speed_of_sound / (2 * self.height)
        draw.text((545, 130), f"Mod wzdłużny (1,0,0): {fl:.1f} Hz (Podbicie basu)", fill=(0, 255, 180), font=get_font(18, bold=True))
        draw.text((545, 175), f"Mod poprzeczny (0,1,0): {fw:.1f} Hz", fill=(0, 240, 255), font=get_font(18, bold=True))
        draw.text((545, 220), f"Mod pionowy (0,0,1): {fh:.1f} Hz", fill=(255, 170, 0), font=get_font(18, bold=True))
        draw.text((545, 280), "Zalecane pułapki basowe w rogach pomieszczenia.", fill=(160, 185, 215), font=get_font(15))
        draw.text((545, 310), "Punkt podziału Schrödera: 180 Hz", fill=(160, 185, 215), font=get_font(15))

        # Bottom Delay Calculator
        canvas.draw_card(20, 520, 984, 190, title="OPÓŹNIENIE KOLUMN (SPEAKER DELAY MS) WG ODLEGŁOŚCI", subtitle="Wyrównanie fazowe kolumn i subwoofera")
        draw.text((45, 580), "Różnica odległości 1 metra = 2.91 ms opóźnienia sygnału.", fill=(0, 255, 180), font=get_font(16, bold=True))
        draw.text((45, 615), "Prędkość dźwięku wyliczana automatycznie wg temperatury otoczenia: c = 331.3 + 0.606 * T(°C)", fill=(140, 170, 200), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmiana Wymiarów Pokoju | [A]: Temperatura Otoczenia | [X]: Pokaż Wykres RT60", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
