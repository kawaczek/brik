#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class MechanicModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.search_code = "P0420"
        self.obd_description = "Wydajność układu katalizatora poniżej wartości progowej (Bank 1)"
        self.causes = [
            "Uszkodzony lub zużyty reaktor katalityczny (katalizator)",
            "Nieszczelność układu wydechowego przed sondą lambda",
            "Niesprawna tylna sonda lambda (za katalizatorem)",
            "Niewłaściwa mieszanka paliwowo-powietrzna (wypadanie zapłonów)",
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🔧 067 // ASYSTENT MECHANIKA & BAZA KODÓW BŁĘDÓW OBD-II", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "OBD-II / EOBD", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "DTC", bg_color=(40, 25, 10), text_color=(255, 170, 0))

        # Big DTC Lookup Card
        canvas.draw_card(20, 65, 984, 240, title="ROZSZYFROWANY KOD BŁĘDU DIAGNOSTYCZNEGO (DTC)", subtitle="Standard SAE J2012 / ISO 15031-6")
        draw.rectangle([45, 125, 230, 215], fill=(24, 38, 58), outline=(255, 170, 0), width=2)
        draw.text((65, 145), self.search_code, fill=(255, 200, 0), font=get_font(44, bold=True))
        draw.text((255, 135), "OPIS USTERKI:", fill=(140, 170, 200), font=get_font(13))
        draw.text((255, 160), self.obd_description, fill=(240, 245, 255), font=get_font(18, bold=True))
        draw.text((255, 210), "Status kontrolki Check Engine: ŚWIECI CIĄGLE (MIL ON)", fill=(255, 80, 80), font=get_font(15, bold=True))

        # Typical Causes Card
        canvas.draw_card(20, 320, 560, 390, title="NAJCZĘSTSZE PRZYCZYNY USTERKI", subtitle="Procedura diagnostyczna krok po kroku")
        for i, c in enumerate(self.causes):
            cy = 385 + i * 70
            draw.rectangle([35, cy, 565, cy + 58], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((45, cy + 18), f"{i+1}. {c}", fill=(220, 235, 255), font=get_font(13, bold=True))

        # Tire & Torque Calculator
        canvas.draw_card(600, 320, 404, 390, title="KALKULATOR OPON & MOMENTU ŚRUB", subtitle="Zamienniki rozmiarów i Nm")
        draw.text((620, 385), "Momenty dokręcania kół:", fill=(255, 200, 0), font=get_font(14, bold=True))
        draw.text((620, 415), "• Śruby M12: 100 - 120 Nm", fill=(210, 225, 245), font=get_font(14))
        draw.text((620, 445), "• Śruby M14: 120 - 150 Nm", fill=(210, 225, 245), font=get_font(14))
        draw.text((620, 495), "Kalkulator opon (205/55 R16):", fill=(0, 255, 180), font=get_font(14, bold=True))
        draw.text((620, 525), "Średnica koła: 631.9 mm", fill=(210, 225, 245), font=get_font(14))
        draw.text((620, 555), "Zamiennik 17 cali: 225/45 R17 (Różnica -0.4%)", fill=(0, 255, 136), font=get_font(13, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wprowadź Inny Kod OBD | [A]: Szukaj w Bazie | [Y]: Kalkulator Opon i Felg", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
