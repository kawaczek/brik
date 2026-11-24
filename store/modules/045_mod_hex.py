#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class HexInspectorModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.offset = 0x00000000
        self.file_name = "bootloader.elf"
        self.file_size = 49152
        self.cursor_row = 2
        # Sample realistic ELF header binary dump
        self.hex_rows = [
            (0x0000, "7F 45 4C 46 02 01 01 00 00 00 00 00 00 00 00 00", ".ELF............"),
            (0x0010, "02 00 B7 00 01 00 00 00 54 80 00 00 00 00 00 00", "........T......."),
            (0x0020, "40 00 00 00 00 00 00 00 18 1B 00 00 00 00 00 00", "@..............."),
            (0x0030, "00 00 00 00 40 00 38 00 04 00 40 00 1A 00 19 00", "....@.8...@....."),
            (0x0040, "06 00 00 00 05 00 00 00 40 00 00 00 00 00 00 00", "........@......."),
            (0x0050, "40 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00", "@.......@......."),
            (0x0060, "F0 01 00 00 00 00 00 00 F0 01 00 00 00 00 00 00", "................"),
            (0x0070, "08 00 00 00 00 00 00 00 03 00 00 00 04 00 00 00", "................"),
            (0x0080, "30 02 00 00 00 00 00 00 30 02 00 00 00 00 00 00", "0.......0......."),
            (0x0090, "1C 00 00 00 00 00 00 00 1C 00 00 00 00 00 00 00", "................")
        ]

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad Góra/Dół", "desc": "Przewijanie bajtów"},
            {"key": "L1/R1", "desc": "Strona - / + (256B)"},
            {"key": "A", "desc": "Analiza sygnatury Magic Bytes"},
            {"key": "X", "desc": "Podgląd sumy SHA-256"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title=f"🔍 TACTICAL HEX INSPECTOR // {self.file_name}",
                         subtitle=f"Rozmiar: {self.file_size:,} bajtów | Format: ELF 64-bit ARM64 | Offset: 0x{self.offset:08X}",
                         border_color=(0, 240, 255))

        # Hex Table Frame
        hx, hy = 45, 120
        hw = 640
        draw.rounded_rectangle([hx, hy, hx + hw, hy + 480], radius=8, fill=(8, 12, 18), outline=(30, 50, 75))

        # Header Columns
        draw.text((hx + 15, hy + 12), "OFFSET", fill=(0, 255, 200), font=get_font(13, bold=True))
        draw.text((hx + 120, hy + 12), "00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F", fill=(255, 210, 0), font=get_font(13, bold=True))
        draw.text((hx + 500, hy + 12), "ASCII", fill=(0, 200, 255), font=get_font(13, bold=True))
        draw.line([(hx + 10, hy + 34), (hx + hw - 10, hy + 34)], fill=(30, 45, 65))

        # Hex rows
        ry = hy + 45
        for idx, (off, hex_str, ascii_str) in enumerate(self.hex_rows):
            is_cur = (idx == self.cursor_row)
            if is_cur:
                draw.rectangle([hx + 10, ry - 3, hx + hw - 10, ry + 21], fill=(20, 35, 55))

            draw.text((hx + 15, ry), f"{off:08X}", fill=(120, 150, 180), font=get_font(13))
            draw.text((hx + 120, ry), hex_str, fill=(240, 250, 255) if not is_cur else (0, 255, 220), font=get_font(13))
            draw.text((hx + 500, ry), ascii_str, fill=(180, 200, 225) if not is_cur else (255, 255, 255), font=get_font(13))
            ry += 32

        # Right Forensics & Magic Bytes Panel
        rx = hx + hw + 25
        rw = w - rx - 45
        draw.rounded_rectangle([rx, hy, rx + rw, hy + 480], radius=10, fill=(16, 22, 34), outline=(0, 200, 255), width=2)
        draw.text((rx + 20, hy + 20), "ANALIZA FORENSIC:", fill=(0, 255, 200), font=get_font(16, bold=True))

        forensics = [
            ("Sygnatura Magic:", "7F 45 4C 46 (.ELF)"),
            ("Architektura:", "ARM64 (AArch64)"),
            ("Endianness:", "Little Endian (LSB)"),
            ("Typ pliku:", "EXEC (Executable)"),
            ("Punkt wejścia:", "0x00008054"),
            ("Tablica sekcji:", "32 sekcje"),
            ("CRC-32:", "0x8F4A2C19"),
            ("SHA-256 skrót:", "3f7a...c89e (Zweryfikowany)")
        ]
        fy = hy + 60
        for l, v in forensics:
            draw.text((rx + 20, fy), l, fill=(130, 160, 190), font=get_font(13))
            draw.text((rx + 20, fy + 18), v, fill=(240, 250, 255), font=get_font(14, bold=True))
            fy += 46

        canvas.draw_badge(rx + 20, hy + 430, "INTEGRALNOŚĆ BAZY: POPRAWNA", bg_color=(0, 60, 40), text_color=(0, 255, 140))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_UP":
            self.cursor_row = (self.cursor_row - 1) % len(self.hex_rows)
            return True
        elif event == "KEY_DOWN":
            self.cursor_row = (self.cursor_row + 1) % len(self.hex_rows)
            return True
        return False
