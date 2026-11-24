#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AstroClockModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.sun_zodiac = "STRZELEC (SAGITTARIUS ♐)"
        self.moon_phase = "PIERWSZA KWADRA (52%)"
        self.sidereal_time = "21:14:08 LST"
        self.babylonian_hour = "GODZINA 7. SŁONECZNA"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 24, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(255, 200, 0, 100), width=1)
        draw.text((20, 14), "🏛️ 068 // PRASKI ZEGAR ASTRONOMICZNY // ORLOJ (1410)", fill=(255, 210, 0), font=get_font(18, bold=True))
        canvas.draw_badge(w - 240, 12, "CZAS GWIEZDNY (LST)", bg_color=(35, 30, 20))
        canvas.draw_badge(w - 75, 12, "ZODIAK", bg_color=(40, 30, 60), text_color=(0, 240, 255))

        # Big Astrolabe Dial
        canvas.draw_card(20, 65, 540, 440, title="CYFERBLAT ASTRONOMICZNY (ASTROLABIUM)", subtitle="Rzut stereograficzny sfery niebieskiej")
        cx, cy = 290, 280
        draw.ellipse([(cx - 150, cy - 150), (cx + 150, cy + 150)], outline=(255, 200, 0), width=3)
        draw.ellipse([(cx - 90, cy - 90), (cx + 90, cy + 90)], outline=(0, 200, 255), width=2)
        draw.line([(cx - 160, cy), (cx + 160, cy)], fill=(40, 60, 85))
        draw.line([(cx, cy - 160), (cx, cy + 160)], fill=(40, 60, 85))
        # Sun & Moon Pointers
        draw.line([(cx, cy), (cx + 80, cy - 90)], fill=(255, 220, 0), width=3) # Sun
        draw.ellipse([(cx + 74, cy - 96), (cx + 86, cy - 84)], fill=(255, 220, 0))
        draw.line([(cx, cy), (cx - 100, cy + 50)], fill=(200, 225, 255), width=2) # Moon
        draw.ellipse([(cx - 106, cy + 44), (cx - 94, cy + 56)], fill=(200, 225, 255))

        # Astronomy Telemetry Card
        canvas.draw_card(580, 65, 424, 440, title="PARAMETRY ASTRONOMICZNE", subtitle="Wskazania słońca, księżyca i zodiaku")
        draw.text((605, 130), "POŁOŻENIE SŁOŃCA W ZODIAKU:", fill=(140, 170, 200), font=get_font(13))
        draw.text((605, 155), self.sun_zodiac, fill=(255, 210, 0), font=get_font(18, bold=True))
        draw.text((605, 210), "FAZA KSIĘŻYCA:", fill=(140, 170, 200), font=get_font(13))
        draw.text((605, 235), self.moon_phase, fill=(220, 240, 255), font=get_font(18, bold=True))
        draw.text((605, 290), "CZAS GWIEZDNY (SIDEREAL):", fill=(140, 170, 200), font=get_font(13))
        draw.text((605, 315), self.sidereal_time, fill=(0, 240, 255), font=get_font(22, bold=True))
        draw.text((605, 370), "GODZINA BABILOŃSKA:", fill=(140, 170, 200), font=get_font(13))
        draw.text((605, 395), self.babylonian_hour, fill=(0, 255, 180), font=get_font(18, bold=True))

        # Bottom Calendar
        canvas.draw_card(20, 520, 984, 190, title="TARCZA KALENDARZOWA MÁNESA & ŚWIĘTA ASTRONOMICZNE", subtitle="Cykl pór roku i zmierzch astronomiczny")
        draw.text((45, 580), "Zmierzch cywilny: 16:15 | Zmierzch nautyczny: 17:02 | Zmierzch astronomiczny: 17:48", fill=(0, 255, 180), font=get_font(16, bold=True))
        draw.text((45, 620), "Przesilenie zimowe (Winter Solstice): 21 grudnia // Najkrótszy dzień w roku (07h 42m)", fill=(255, 200, 0), font=get_font(15))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Czas (Godzina/Dzień) | [A]: Animuj Koło Zodiaku | [X]: Zmień Współrzędne", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
