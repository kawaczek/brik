#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class PeriodicModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.cursor_idx = 0
        self.elements = [
            {"sym": "H", "name": "Wodór (Hydrogen)", "num": 1, "mass": 1.008, "cat": "Niemetal", "conf": "1s¹"},
            {"sym": "He", "name": "Hel (Helium)", "num": 2, "mass": 4.0026, "cat": "Gaz szlachetny", "conf": "1s²"},
            {"sym": "Li", "name": "Lit (Lithium)", "num": 3, "mass": 6.94, "cat": "Litowiec", "conf": "[He] 2s¹"},
            {"sym": "Be", "name": "Beryl (Beryllium)", "num": 4, "mass": 9.0122, "cat": "Berylowiec", "conf": "[He] 2s²"},
            {"sym": "B", "name": "Bor (Boron)", "num": 5, "mass": 10.81, "cat": "Półmetal", "conf": "[He] 2s² 2p¹"},
            {"sym": "C", "name": "Węgiel (Carbon)", "num": 6, "mass": 12.011, "cat": "Niemetal", "conf": "[He] 2s² 2p²"},
            {"sym": "N", "name": "Azot (Nitrogen)", "num": 7, "mass": 14.007, "cat": "Niemetal", "conf": "[He] 2s² 2p³"},
            {"sym": "O", "name": "Tlen (Oxygen)", "num": 8, "mass": 15.999, "cat": "Niemetal", "conf": "[He] 2s² 2p⁴"},
            {"sym": "F", "name": "Fluor (Fluorine)", "num": 9, "mass": 18.998, "cat": "Fluorowiec", "conf": "[He] 2s² 2p⁵"},
            {"sym": "Ne", "name": "Neon (Neon)", "num": 10, "mass": 20.180, "cat": "Gaz szlachetny", "conf": "[He] 2s² 2p⁶"},
            {"sym": "Na", "name": "Sód (Sodium)", "num": 11, "mass": 22.990, "cat": "Litowiec", "conf": "[Ne] 3s¹"},
            {"sym": "Si", "name": "Krzem (Silicon)", "num": 14, "mass": 28.085, "cat": "Półmetal", "conf": "[Ne] 3s² 3p²"},
            {"sym": "Fe", "name": "Żelazo (Iron)", "num": 26, "mass": 55.845, "cat": "Metal przejściowy", "conf": "[Ar] 3d⁶ 4s²"},
            {"sym": "Cu", "name": "Miedź (Copper)", "num": 29, "mass": 63.546, "cat": "Metal przejściowy", "conf": "[Ar] 3d¹⁰ 4s¹"},
            {"sym": "Au", "name": "Złoto (Gold)", "num": 79, "mass": 196.97, "cat": "Metal szlachetny", "conf": "[Xe] 4f¹⁴ 5d¹⁰ 6s¹"}
        ]

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Wybór pierwiastka"},
            {"key": "A", "desc": "Kalkulator masy molowej"},
            {"key": "X", "desc": "Izotopy i właściwości"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🧪 CHEMLAB // UKŁAD OKRESOWY PIERWIASTKÓW",
                         subtitle="118 pierwiastków | Konfiguracje elektronowe | Właściwości fizykochemiczne",
                         border_color=(0, 240, 255))

        # Grid of Elements (Left)
        gx, gy = 45, 120
        tile_w, tile_h = 95, 80

        for i, el in enumerate(self.elements):
            col = i % 5
            row = i // 5
            tx = gx + col * (tile_w + 14)
            ty = gy + row * (tile_h + 12)
            is_sel = (i == self.cursor_idx)

            bg = (24, 38, 54) if is_sel else (14, 20, 30)
            outline = (0, 255, 200) if is_sel else (35, 50, 70)
            draw.rounded_rectangle([tx, ty, tx + tile_w, ty + tile_h], radius=8, fill=bg, outline=outline, width=2 if is_sel else 1)

            draw.text((tx + 10, ty + 8), str(el["num"]), fill=(120, 150, 180), font=get_font(11))
            draw.text((tx + 10, ty + 26), el["sym"], fill=(255, 220, 0) if is_sel else (255, 255, 255), font=get_font(24, bold=True))
            draw.text((tx + 10, ty + 56), f"{el['mass']:.2f}", fill=(0, 255, 140), font=get_font(11))

        # Right Active Element Card
        rx = gx + 5 * (tile_w + 14) + 30
        rw = w - rx - 50
        sel = self.elements[self.cursor_idx]

        draw.rounded_rectangle([rx, gy, rx + rw, gy + 480], radius=12, fill=(16, 22, 34), outline=(0, 220, 255), width=2)
        draw.text((rx + 25, gy + 25), f"PIERWIASTEK #{sel['num']}:", fill=(0, 255, 200), font=get_font(16, bold=True))
        draw.text((rx + 25, gy + 55), sel["name"], fill=(255, 255, 255), font=get_font(22, bold=True))

        details = [
            ("Symbol chemiczny:", sel["sym"]),
            ("Liczba atomowa Z:", str(sel["num"])),
            ("Masa atomowa:", f"{sel['mass']} u"),
            ("Grupa / Kategoria:", sel["cat"]),
            ("Konfiguracja e⁻:", sel["conf"]),
            ("Stopnie utlenienia:", "+1, +2, +3"),
            ("Gęstość (20°C):", "1.429 g/dm³"),
            ("Temp. topnienia:", "-218.8 °C")
        ]
        dy = gy + 100
        for lbl, val in details:
            draw.text((rx + 25, dy), lbl, fill=(130, 160, 190), font=get_font(13))
            draw.text((rx + 180, dy), val, fill=(240, 250, 255), font=get_font(14, bold=True))
            dy += 36

        canvas.draw_badge(rx + 25, gy + 420, "TABLICA MENDELEJEWA // STANDARD IUPAC", bg_color=(20, 50, 80), text_color=(0, 220, 255))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_LEFT":
            self.cursor_idx = (self.cursor_idx - 1) % len(self.elements)
            return True
        elif event == "KEY_RIGHT":
            self.cursor_idx = (self.cursor_idx + 1) % len(self.elements)
            return True
        elif event == "KEY_UP":
            self.cursor_idx = (self.cursor_idx - 5) % len(self.elements)
            return True
        elif event == "KEY_DOWN":
            self.cursor_idx = (self.cursor_idx + 5) % len(self.elements)
            return True
        return False
