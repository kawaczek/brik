#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class EeLabModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.r1 = 10000.0 # 10k
        self.r2 = 4700.0  # 4.7k
        self.c1 = 1e-7    # 100nF
        self.vin = 5.0    # 5V

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Zmiana R1 / R2 / C1"},
            {"key": "L1/R1", "desc": "Napięcie Vin +/-"},
            {"key": "X", "desc": "Tryb NE555 / Dzielnik"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="⚡ ELECTRONICS LAB // CIRCUIT & NE555 DESIGNER",
                         subtitle="Kalkulator NE555 Astable | Dzielniki napięcia | Typoszereg E24 | Filtry RC",
                         border_color=(255, 210, 0))

        # NE555 calculations
        # f = 1.44 / ((R1 + 2*R2) * C)
        freq = 1.44 / ((self.r1 + 2.0 * self.r2) * self.c1)
        duty = ((self.r1 + self.r2) / (self.r1 + 2.0 * self.r2)) * 100.0
        # Voltage divider: Vout = Vin * (R2 / (R1 + R2))
        vout = self.vin * (self.r2 / (self.r1 + self.r2))

        # Panel 1: NE555 Generator (Left)
        p1_x, p1_y, p1_w, p1_h = 45, 120, 450, 480
        draw.rounded_rectangle([p1_x, p1_y, p1_x + p1_w, p1_y + p1_h], radius=10, fill=(16, 22, 32), outline=(255, 200, 0), width=2)
        draw.text((p1_x + 20, p1_y + 20), "GENERATOR ASTABILNY NE555:", fill=(255, 220, 0), font=get_font(16, bold=True))

        lines_ne555 = [
            ("Rezystor R1:", f"{self.r1/1000:.1f} kΩ"),
            ("Rezystor R2:", f"{self.r2/1000:.1f} kΩ"),
            ("Kondensator C:", f"{self.c1*1e9:.0f} nF"),
            ("Częstotliwość f:", f"{freq:.1f} Hz"),
            ("Wypełnienie (Duty):", f"{duty:.1f} %"),
            ("Czas stanu wysokiego Th:", f"{(0.693*(self.r1+self.r2)*self.c1)*1000:.2f} ms"),
            ("Czas stanu niskiego Tl:", f"{(0.693*self.r2*self.c1)*1000:.2f} ms")
        ]
        ly = p1_y + 60
        for l, v in lines_ne555:
            draw.text((p1_x + 20, ly), l, fill=(140, 165, 195), font=get_font(13))
            draw.text((p1_x + 240, ly), v, fill=(240, 250, 255), font=get_font(14, bold=True))
            ly += 34

        # Waveform visual
        draw.rectangle([p1_x + 20, p1_y + 340, p1_x + p1_w - 20, p1_y + 440], fill=(8, 12, 18), outline=(40, 60, 85))
        draw.text((p1_x + 30, p1_y + 350), f"WYKRES PROSTOKĄTA (Duty {duty:.0f}%):", fill=(0, 255, 200), font=get_font(11))
        pts = [(p1_x + 40, p1_y + 420), (p1_x + 40, p1_y + 380), (p1_x + 120, p1_y + 380), (p1_x + 120, p1_y + 420),
               (p1_x + 200, p1_y + 420), (p1_x + 200, p1_y + 380), (p1_x + 280, p1_y + 380), (p1_x + 280, p1_y + 420)]
        draw.line(pts, fill=(0, 255, 140), width=2)

        # Panel 2: Voltage Divider & Filters (Right)
        p2_x = p1_x + p1_w + 30
        p2_w = w - p2_x - 45
        draw.rounded_rectangle([p2_x, p1_y, p2_x + p2_w, p1_y + p1_h], radius=10, fill=(16, 22, 32), outline=(0, 200, 255), width=2)
        draw.text((p2_x + 20, p1_y + 20), "DZIELNIK NAPIĘCIA I FILTRY:", fill=(0, 220, 255), font=get_font(16, bold=True))

        # Filter Cutoff: fc = 1 / (2*pi*R*C)
        fc = 1.0 / (2.0 * math.pi * self.r1 * self.c1)

        lines_div = [
            ("Napięcie Vin:", f"{self.vin:.1f} V"),
            ("Napięcie wyjściowe Vout:", f"{vout:.2f} V"),
            ("Prąd dzielnika I:", f"{(self.vin/(self.r1+self.r2))*1000:.2f} mA"),
            ("Moc strat na R1:", f"{((self.vin - vout)**2 / self.r1)*1000:.2f} mW"),
            ("Filtr dolnoprzepustowy RC fc:", f"{fc:.1f} Hz"),
            ("Szerokość ścieżki PCB (1A):", "0.38 mm (15 mil)"),
            ("Typoszereg:", "E24 (5% tolerancji)")
        ]
        ly = p1_y + 60
        for l, v in lines_div:
            draw.text((p2_x + 20, ly), l, fill=(140, 165, 195), font=get_font(13))
            draw.text((p2_x + 240, ly), v, fill=(255, 220, 0) if "Vout" in l else (240, 250, 255), font=get_font(14, bold=True))
            ly += 34

        canvas.draw_badge(p2_x + 20, p1_y + 420, "NORMY: IPC-2152 // TYPOSZEREG E12/E24", bg_color=(20, 50, 80), text_color=(0, 220, 255))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_LEFT":
            self.r1 = max(100.0, self.r1 - 1000.0)
            return True
        elif event == "KEY_RIGHT":
            self.r1 = min(100000.0, self.r1 + 1000.0)
            return True
        elif event == "KEY_UP":
            self.r2 = min(100000.0, self.r2 + 500.0)
            return True
        elif event == "KEY_DOWN":
            self.r2 = max(100.0, self.r2 - 500.0)
            return True
        elif event == "KEY_L1":
            self.vin = max(1.0, self.vin - 0.5)
            return True
        elif event == "KEY_R1":
            self.vin = min(24.0, self.vin + 0.5)
            return True
        return False
