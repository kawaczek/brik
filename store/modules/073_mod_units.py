#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class UnitsConverterModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.input_val = 100.0
        self.category = "CIŚNIENIE (PRESSURE)"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🧮 073 // ENGINEERING UNITS CONVERTER // {self.category}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "PRECYZJA 64-BIT", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 85, 12, "SI / IMP", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big Value Card
        canvas.draw_card(20, 65, 450, 440, title="WARTOŚĆ WEJŚCIOWA (BAZOWA)", subtitle="100.00 PSI (Funty na cal kwadratowy)")
        draw.text((60, 160), "100.00", fill=(0, 255, 180), font=get_font(72, bold=True))
        draw.text((310, 200), "PSI", fill=(255, 200, 0), font=get_font(28, bold=True))
        draw.text((60, 280), "Odpowiednik ciśnienia opon samochodowych:", fill=(160, 185, 215), font=get_font(14))
        draw.text((60, 310), "Ok. 6.89 bara (Typowe ciśnienie w kolarzówkach)", fill=(0, 255, 136), font=get_font(15, bold=True))

        # Converted Grid Card
        canvas.draw_card(490, 65, 514, 440, title="PRZELICZENIE NA JEDNOSTKI UKŁADU SI I SPECJALNE", subtitle="Wszystkie odpowiedniki ciśnienia jednocześnie")
        conv = [
            ("BAR (bar):", "6.8947 bar", (0, 240, 255)),
            ("KILOPASKAL (kPa):", "689.475 kPa", (0, 240, 255)),
            ("MEGAPASKAL (MPa):", "0.6895 MPa", (0, 240, 255)),
            ("ATMOSFERA FIZYCZNA (atm):", "6.8046 atm", (240, 245, 255)),
            ("MILIMETRY SŁUPA RTĘCI (mmHg):", "5171.49 mmHg", (240, 245, 255)),
            ("KILOGRAM-SIŁA / CM² (at):", "7.0307 kgf/cm²", (240, 245, 255)),
        ]
        for i, (u_name, u_val, col) in enumerate(conv):
            cy = 135 + i * 58
            draw.text((510, cy), u_name, fill=(140, 170, 200), font=get_font(13))
            draw.text((510, cy + 20), u_val, fill=col, font=get_font(18, bold=True))

        # Bottom Categories
        canvas.draw_card(20, 520, 984, 190, title="KATEGORIE JEDNOSTEK INŻYNIERYJNYCH", subtitle="Wybierz kategorię konwersji D-Padem")
        cats = ["Ciśnienie", "Moment obrotowy (Nm/ft-lb)", "Moc (W/KM/HP)", "Energia (J/kWh/cal)", "Prędkość (km/h / kt / mph)", "Temperatura (°C/°F/K)"]
        for i, c_name in enumerate(cats):
            cx = 40 + (i % 3) * 320
            cy = 575 + (i // 3) * 55
            is_sel = (i == 0)
            draw.rectangle([cx, cy, cx + 300, cy + 45], fill=(24, 40, 65) if is_sel else (14, 20, 32), outline=(0, 240, 255) if is_sel else (35, 50, 70))
            draw.text((cx + 15, cy + 12), c_name, fill=(0, 255, 180) if is_sel else (180, 200, 230), font=get_font(13, bold=is_sel))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmień Kategorię / Wartość | [A]: Edytuj Liczbę | [X]: Odwróć Kierunek Konwersji", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
