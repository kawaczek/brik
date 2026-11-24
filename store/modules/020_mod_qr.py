"""
BrickDeck Module: Barcode & QR Code Generator (mod_qr.py)
Generates high-contrast 2D QR Codes and 1D Barcodes (Code 128, EAN-13) directly on the TrimUI Brick screen.
Features:
- Instant on-screen scanning with any smartphone camera or handheld barcode reader
- Presets: Wi-Fi Access Point Auto-Connect, URLs, Bitcoin/ETH crypto wallets, vCards, SOS coordinates
- 1D Linear Barcodes: Code 128 (ASCII text/serials), EAN-13 (retail products)
- Toggle High-Contrast Scanner Mode (solid white background for rapid optical camera detection)
- Error correction toggle (Level L / Level M)
- 100% standalone and pure-Python: zero-pip dependencies.
"""

from typing import List, Dict, Any, Optional

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)
from core.canvas import get_font
from core.i18n import t
from core.qr_engine import generate_qr_matrix, generate_code128, generate_ean13

PRESETS = [
    {
        "id": "wifi",
        "title": "Wi-Fi Hotspot Auto-Connect",
        "badge": "WI-FI QR",
        "type": "qr",
        "content": "WIFI:S:BrickDeck-AP;T:WPA;P:cyberdeck2026;;",
        "desc": "Zeskanuj telefonem, aby połączyć się z Wi-Fi konsoli bez wpisywania hasła!"
    },
    {
        "id": "github",
        "title": "Projekt GitHub Repository",
        "badge": "URL LINK",
        "type": "qr",
        "content": "https://github.com/user/brick",
        "desc": "Bezpośredni link do kodu źródłowego systemu BrickDeck OS."
    },
    {
        "id": "vcard",
        "title": "Cyfrowa Wizytówka (vCard)",
        "badge": "KONTAKT",
        "type": "qr",
        "content": "BEGIN:VCARD\nVERSION:3.0\nFN:BrickDeck Operator\nORG:Cyberdeck Labs\nTEL:+48123456789\nEMAIL:operator@brickdeck.local\nEND:VCARD",
        "desc": "Automatycznie dodaje kontakt i numer telefonu do książki adresowej telefonu."
    },
    {
        "id": "btc",
        "title": "Portfel Bitcoin (BTC SegWit)",
        "badge": "CRYPTO WALLET",
        "type": "qr",
        "content": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.005",
        "desc": "Adres odbiorczy portfela krypto gotowy do przelewu z aplikacji mobilnej."
    },
    {
        "id": "sos",
        "title": "Meldunek Ratunkowy GPS SOS",
        "badge": "GEO & SOS",
        "type": "qr",
        "content": "geo:52.7333,15.2333?q=52.7333,15.2333(SOS_BASE)",
        "desc": "Otwiera koordynaty bazy ratunkowej w Google Maps lub Apple Maps."
    },
    {
        "id": "serial128",
        "title": "Numer Seryjny Urządzenia (Code 128)",
        "badge": "CODE 128",
        "type": "code128",
        "content": "SN-TRIMUI-BRICK-2026-A133P",
        "desc": "Logistyczny kod paskowy czytany przez skanery magazynowe i laserowe."
    },
    {
        "id": "inventory128",
        "title": "Identyfikator Magazynowy (Code 128)",
        "badge": "CODE 128",
        "type": "code128",
        "content": "CYBERDECK-LAB-UNIT-01",
        "desc": "Format alfanumeryczny ASCII dla inwentaryzacji sprzętu."
    },
    {
        "id": "ean13_pl",
        "title": "Polski Kod Towarowy EAN-13 (590)",
        "badge": "EAN-13",
        "type": "ean13",
        "content": "590123456789",
        "desc": "Klasyczny 13-cyfrowy kod kreskowy z automatyczną cyfrą kontrolną."
    }
]


class QRModule(BaseModule):
    name = "Barcode & QR Code Generator"
    short_name = "QR / Kody"
    icon = "📱"
    accent_color = (0, 210, 255)

    def __init__(self, app_context=None):
        super().__init__(app_context)

        self.preset_idx = 0
        # High-contrast scanner mode: True = solid white plate for 100% camera scanning
        self.high_contrast = True
        # Error correction: 'M' (15%) or 'L' (7%)
        self.ec_level = 'M'
        # Cached render data
        self.cached_qr: Optional[List[List[int]]] = None
        self.cached_barcode: Optional[List[int]] = None
        self.cached_qr_version = 1
        self.cached_ean_full = ""
        self.last_preset_rendered = -1

        self._regenerate_code()

    def _regenerate_code(self):
        p = PRESETS[self.preset_idx]
        p_type = p["type"]
        text = p["content"]

        if p_type == "qr":
            self.cached_qr, self.cached_qr_version = generate_qr_matrix(text, self.ec_level)
            self.cached_barcode = None
        elif p_type == "code128":
            self.cached_barcode = generate_code128(text)
            self.cached_qr = None
        elif p_type == "ean13":
            self.cached_barcode, self.cached_ean_full = generate_ean13(text)
            self.cached_qr = None

        self.last_preset_rendered = self.preset_idx

    def get_hotkey_hints(self):
        cur_p = PRESETS[self.preset_idx]
        contrast_lbl = "Kolor: Cyber" if self.high_contrast else "Kolor: Biały"
        return [
            ("L1/R1", "Typ Kodu"),
            ("D-Pad G/D", "Wybierz Szablon"),
            ("X", contrast_lbl),
            ("Y", f"Korekcja: {self.ec_level}"),
            ("A", "Pełny Podgląd")
        ]

    def update(self, dt: float):
        if self.last_preset_rendered != self.preset_idx:
            self._regenerate_code()

    def render(self, canvas):
        p = PRESETS[self.preset_idx]

        # Main Card Wrapper
        canvas.draw_card(
            x=25, y=66, w=974, h=638,
            title=f"📱 BARCODE & QR CODE GENERATOR: {p['title'].upper()}",
            subtitle=f"{p['badge']}  |  Format: {p['type'].upper()}  |  Gotowy do zeskanowania aparatem smartfona",
            border_color=self.accent_color
        )

        # -------------------------------------------------------------
        # Left Panel: Optical Code Display Plate (x=40, y=116, w=500, h=570)
        # -------------------------------------------------------------
        lx, ly, lw, lh = 40, 116, 500, 570
        canvas.draw.rounded_rectangle([(lx, ly), (lx + lw, ly + lh)], radius=10, fill=(14, 18, 24), outline=COLOR_BORDER, width=1)

        # Draw Code Plate (Solid white in high_contrast mode for perfect optical camera scanning)
        plate_w, plate_h = 440, 440
        px = lx + (lw - plate_w) // 2
        py = ly + 25

        plate_bg = (255, 255, 255) if self.high_contrast else (20, 26, 36)
        plate_border = (200, 200, 200) if self.high_contrast else COLOR_CYBER_CYAN
        canvas.draw.rounded_rectangle([(px, py), (px + plate_w, py + plate_h)], radius=12, fill=plate_bg, outline=plate_border, width=2)

        # 1. Render 2D QR Code
        if p["type"] == "qr" and self.cached_qr:
            matrix = self.cached_qr
            grid_size = len(matrix)
            # Module pixel scale: fit inside 380x380 px with quiet zone
            cell_size = max(4, min(14, 380 // grid_size))
            qr_total_px = grid_size * cell_size
            offset_x = px + (plate_w - qr_total_px) // 2
            offset_y = py + (plate_h - qr_total_px) // 2

            bar_color = (0, 0, 0) if self.high_contrast else COLOR_CYBER_CYAN
            for r in range(grid_size):
                for c in range(grid_size):
                    if matrix[r][c] == 1:
                        mx1 = offset_x + c * cell_size
                        my1 = offset_y + r * cell_size
                        mx2 = mx1 + cell_size
                        my2 = my1 + cell_size
                        canvas.draw.rectangle([(mx1, my1), (mx2, my2)], fill=bar_color)

        # 2. Render 1D Barcode (Code 128 / EAN-13)
        elif self.cached_barcode:
            bits = self.cached_barcode
            bit_count = len(bits)
            bar_w = max(2, min(4, 380 // bit_count))
            total_bar_px = bit_count * bar_w
            bar_start_x = px + (plate_w - total_bar_px) // 2
            bar_start_y = py + 70
            bar_h = 240

            bar_color = (0, 0, 0) if self.high_contrast else COLOR_PHOSPHOR_GREEN

            for i, bit in enumerate(bits):
                if bit == 1:
                    bx1 = bar_start_x + i * bar_w
                    bx2 = bx1 + bar_w
                    canvas.draw.rectangle([(bx1, bar_start_y), (bx2, bar_start_y + bar_h)], fill=bar_color)

            # Human-readable text under barcode
            text_str = self.cached_ean_full if p["type"] == "ean13" else p["content"]
            txt_color = (0, 0, 0) if self.high_contrast else COLOR_TEXT_PRIMARY
            canvas.draw.text((px + plate_w // 2, bar_start_y + bar_h + 30), text_str, fill=txt_color, font=get_font(16, bold=True), anchor="mm")

        # Bottom Tip on Left Panel
        mode_text = "TRYB SKANERA: 100% Czysta Biel (Zoptymalizowany dla aparatu)" if self.high_contrast else "TRYB CYBERDECK: Ciemne tło"
        canvas.draw.text((lx + lw // 2, ly + lh - 65), mode_text, fill=COLOR_PHOSPHOR_GREEN if self.high_contrast else COLOR_CYBER_CYAN, font=get_font(11, bold=True), anchor="mm")
        canvas.draw.text((lx + lw // 2, ly + lh - 35), "[X]: Przełącz kontrast tła  |  [Y]: Korekcja błędów", fill=COLOR_TEXT_MUTED, font=get_font(10), anchor="mm")

        # -------------------------------------------------------------
        # Right Panel: Preset Selector & Content Inspector (x=560, y=116, w=424, h=570)
        # -------------------------------------------------------------
        rx, ry, rw, rh = 560, 116, 424, 570
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=10, fill=(16, 20, 28), outline=COLOR_BORDER, width=1)

        # Header
        canvas.draw.text((rx + 16, ry + 14), "BIBLIOTEKA SZABLONÓW KODÓW", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))
        canvas.draw.line([(rx + 14, ry + 36), (rx + rw - 14, ry + 36)], fill=COLOR_BORDER, width=1)

        # Presets List
        item_y = ry + 46
        for idx, preset in enumerate(PRESETS):
            is_sel = (idx == self.preset_idx)
            fill_c = (26, 40, 52) if is_sel else (20, 24, 34)
            outline_c = COLOR_CYBER_CYAN if is_sel else (34, 42, 56)

            canvas.draw.rounded_rectangle([(rx + 10, item_y), (rx + rw - 10, item_y + 44)], radius=6, fill=fill_c, outline=outline_c, width=2 if is_sel else 1)

            # Title
            t_col = COLOR_TEXT_PRIMARY if is_sel else COLOR_TEXT_SECONDARY
            canvas.draw.text((rx + 18, item_y + 7), preset["title"], fill=t_col, font=get_font(11, bold=is_sel))
            canvas.draw.text((rx + 18, item_y + 26), preset["badge"], fill=COLOR_FLIPPER_AMBER if is_sel else COLOR_TEXT_MUTED, font=get_font(9, bold=True))

            item_y += 50
            if item_y > ry + 320:
                break

        # Content Inspector Card (Bottom Right)
        canvas.draw.line([(rx + 14, ry + 350), (rx + rw - 14, ry + 350)], fill=COLOR_BORDER, width=1)
        canvas.draw.text((rx + 16, ry + 360), "ZAKODOWANA ZAWARTOŚĆ:", fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))

        content_box_y = ry + 382
        canvas.draw.rounded_rectangle([(rx + 12, content_box_y), (rx + rw - 12, content_box_y + 90)], radius=6, fill=(12, 16, 22), outline=COLOR_BORDER)

        # Multi-line preview
        lines = p["content"].split("\n")
        prev_y = content_box_y + 10
        for l in lines[:4]:
            canvas.draw.text((rx + 20, prev_y), l[:42], fill=COLOR_TEXT_PRIMARY, font=get_font(10, bold=False))
            prev_y += 18

        # Description
        canvas.draw.text((rx + 16, content_box_y + 105), p["desc"], fill=COLOR_TEXT_SECONDARY, font=get_font(10))

        # Specs Badge at bottom
        if p["type"] == "qr":
            spec_info = f"Format: QR Wersja {self.cached_qr_version} ({len(self.cached_qr)}x{len(self.cached_qr)} mod)  |  Korekcja: {self.ec_level}"
        else:
            spec_info = f"Format: {p['type'].upper()}  |  Długość: {len(self.cached_barcode)} modułów"
        canvas.draw.text((rx + 16, ry + rh - 20), spec_info, fill=COLOR_TEXT_MUTED, font=get_font(9))

    # -----------------------------------------------------------------
    # INPUT HANDLING
    # -----------------------------------------------------------------
    def handle_input(self, event: str) -> bool:
        # Switch Preset: D-Pad Up / Down
        if event in ("DPAD_UP", "w", "W", "UP"):
            self.preset_idx = (self.preset_idx - 1) % len(PRESETS)
            self._regenerate_code()
            return True
        elif event in ("DPAD_DOWN", "s", "S", "DOWN"):
            self.preset_idx = (self.preset_idx + 1) % len(PRESETS)
            self._regenerate_code()
            return True

        # Switch Symbology / Category: L1 / R1
        elif event in ("BTN_L1", "l1", "L1"):
            # Jump to previous format type
            cur_type = PRESETS[self.preset_idx]["type"]
            for offset in range(1, len(PRESETS)):
                prev_i = (self.preset_idx - offset) % len(PRESETS)
                if PRESETS[prev_i]["type"] != cur_type:
                    self.preset_idx = prev_i
                    self._regenerate_code()
                    break
            return True
        elif event in ("BTN_R1", "r1", "R1"):
            # Jump to next format type
            cur_type = PRESETS[self.preset_idx]["type"]
            for offset in range(1, len(PRESETS)):
                next_i = (self.preset_idx + offset) % len(PRESETS)
                if PRESETS[next_i]["type"] != cur_type:
                    self.preset_idx = next_i
                    self._regenerate_code()
                    break
            return True

        # Toggle Scanner High-Contrast Mode: X
        elif event in ("BTN_X", "x", "X"):
            self.high_contrast = not self.high_contrast
            return True

        # Toggle Error Correction: Y
        elif event in ("BTN_Y", "y", "Y"):
            self.ec_level = 'L' if self.ec_level == 'M' else 'M'
            self._regenerate_code()
            return True

        return False
