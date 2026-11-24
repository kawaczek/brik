"""
BrickDeck Module: Cyberdeck Hacker & Network Calculator
Handheld tools for network engineers and hardware hackers: IPv4 CIDR Subnet Calculator, Radix Base Converter, and Resistor Color Decoder.
"""

import base64
from typing import List, Dict, Tuple, Optional

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)
from core.canvas import get_font

RESISTOR_COLORS = [
    ("Czarny", (20, 20, 20), 0, 1),
    ("Brązowy", (139, 69, 19), 1, 10),
    ("Czerwony", (220, 40, 40), 2, 100),
    ("Pomarańczowy", (255, 140, 0), 3, 1000),
    ("Żółty", (240, 220, 40), 4, 10000),
    ("Zielony", (40, 200, 60), 5, 100000),
    ("Niebieski", (30, 140, 255), 6, 1000000),
    ("Fioletowy", (160, 60, 220), 7, 10000000),
    ("Szary", (128, 128, 128), 8, 100000000),
    ("Biały", (240, 240, 240), 9, 1000000000),
]

TOLERANCE_COLORS = [
    ("Brązowy (±1%)", (139, 69, 19), "±1%"),
    ("Czerwony (±2%)", (220, 40, 40), "±2%"),
    ("Złoty (±5%)", (212, 175, 55), "±5%"),
    ("Srebrny (±10%)", (192, 192, 192), "±10%"),
]


class CalcNetModule(BaseModule):
    name = "Cyberdeck Hacker & Net Utils"
    short_name = "Calc & Net"
    icon = "🧮"
    accent_color = COLOR_PHOSPHOR_GREEN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.tool_idx = 0  # 0: CIDR Subnet, 1: Radix Converter, 2: Resistor Colors
        self.tool_names = ["Kalkulator Podsieci CIDR", "Konwerter Baz (Radix)", "Dekoder Rezystorów"]

        # Tool 0: CIDR State
        self.ip_octets = [192, 168, 1, 42]
        self.prefix_len = 24
        self.cidr_cursor = 3  # 0..3: octet, 4: prefix

        # Tool 1: Radix State
        self.radix_value = 1337
        self.radix_step = 1

        # Tool 2: Resistor State
        self.band1_idx = 4  # Żółty = 4
        self.band2_idx = 7  # Fioletowy = 7
        self.band_mult_idx = 2  # Czerwony = 100 -> 4.7 kΩ
        self.band_tol_idx = 2  # Złoty = ±5%
        self.resistor_cursor = 0  # 0..3: band

    def get_hotkey_hints(self):
        if self.tool_idx == 0:
            return [
                ("L1/R1", "Moduły"),
                ("D-Pad L/P", "Wybór oktetu"),
                ("D-Pad G/D", "Wartość +/-"),
                ("X", "Zmień narzędzie"),
                ("Y", "Reset do /24")
            ]
        elif self.tool_idx == 1:
            return [
                ("L1/R1", "Moduły"),
                ("D-Pad G/D", f"Wartość +/- ({self.radix_step})"),
                ("D-Pad L/P", "Mnożnik kroku"),
                ("X", "Zmień narzędzie"),
                ("Y", "Wartość = 0")
            ]
        else:
            return [
                ("L1/R1", "Moduły"),
                ("D-Pad L/P", "Wybór paska"),
                ("D-Pad G/D", "Zmień kolor"),
                ("X", "Zmień narzędzie"),
                ("Y", "Typowe 10k")
            ]

    def _calc_cidr(self) -> Dict:
        """Compute full IPv4 subnet details."""
        ip_int = (self.ip_octets[0] << 24) | (self.ip_octets[1] << 16) | (self.ip_octets[2] << 8) | self.ip_octets[3]
        mask_int = (0xFFFFFFFF << (32 - self.prefix_len)) & 0xFFFFFFFF if self.prefix_len > 0 else 0
        wild_int = (~mask_int) & 0xFFFFFFFF

        net_int = ip_int & mask_int
        bcast_int = net_int | wild_int

        first_host_int = net_int + 1 if self.prefix_len < 31 else net_int
        last_host_int = bcast_int - 1 if self.prefix_len < 31 else bcast_int

        total_hosts = 2 ** (32 - self.prefix_len)
        usable_hosts = max(0, total_hosts - 2) if self.prefix_len < 31 else (1 if self.prefix_len == 32 else 2)

        def int_to_ip(v):
            return f"{(v >> 24) & 0xFF}.{(v >> 16) & 0xFF}.{(v >> 8) & 0xFF}.{v & 0xFF}"

        # RFC1918 check
        o1, o2 = self.ip_octets[0], self.ip_octets[1]
        is_private = (o1 == 10) or (o1 == 172 and 16 <= o2 <= 31) or (o1 == 192 and o2 == 168)
        scope = "Prywatny (RFC 1918)" if is_private else ("Pętla zwrotna (Loopback)" if o1 == 127 else "Publiczny Internet")

        return {
            "netmask": int_to_ip(mask_int),
            "wildcard": int_to_ip(wild_int),
            "network": int_to_ip(net_int),
            "broadcast": int_to_ip(bcast_int),
            "first_host": int_to_ip(first_host_int),
            "last_host": int_to_ip(last_host_int),
            "total_hosts": total_hosts,
            "usable_hosts": usable_hosts,
            "scope": scope,
            "mask_bin": f"{mask_int:032b}",
            "ip_bin": f"{ip_int:032b}"
        }

    def _render_cidr_tool(self, canvas):
        canvas.draw_card(
            32, 66, 960, 634,
            title="KALKULATOR PODSIECI IPV4 & CIDR",
            subtitle=f"Narzędzie: {self.tool_names[self.tool_idx]}  (Klawisz [X] zmienia narzędzie)",
            border_color=self.accent_color
        )

        cx = 56
        cy = 118

        # Interactive Input Display Pill
        canvas.draw.text((cx, cy), "WPROWADŹ ADRES IP ORAZ PREFIX CIDR:", fill=COLOR_TEXT_SECONDARY, font=get_font(12, bold=True))

        inp_y = cy + 24
        oct_x = cx
        for i in range(4):
            is_cur = (self.cidr_cursor == i)
            bg_pill = (36, 50, 72) if is_cur else (20, 26, 36)
            out_pill = COLOR_CYBER_CYAN if is_cur else COLOR_BORDER

            canvas.draw.rounded_rectangle([(oct_x, inp_y), (oct_x + 70, inp_y + 44)], radius=6, fill=bg_pill, outline=out_pill, width=2 if is_cur else 1)
            oct_val_str = str(self.ip_octets[i])
            canvas.draw.text((oct_x + 20, inp_y + 10), oct_val_str, fill=COLOR_TEXT_PRIMARY, font=get_font(18, bold=True))

            if i < 3:
                canvas.draw.text((oct_x + 78, inp_y + 12), ".", fill=COLOR_TEXT_MUTED, font=get_font(20, bold=True))
            oct_x += 96

        # Slash and Prefix
        canvas.draw.text((oct_x, inp_y + 10), "/", fill=COLOR_CYBER_CYAN, font=get_font(22, bold=True))
        oct_x += 20

        is_cur_pfx = (self.cidr_cursor == 4)
        bg_pfx = (36, 50, 72) if is_cur_pfx else (20, 26, 36)
        out_pfx = COLOR_CYBER_CYAN if is_cur_pfx else COLOR_BORDER
        canvas.draw.rounded_rectangle([(oct_x, inp_y), (oct_x + 64, inp_y + 44)], radius=6, fill=bg_pfx, outline=out_pfx, width=2 if is_cur_pfx else 1)
        canvas.draw.text((oct_x + 16, inp_y + 10), str(self.prefix_len), fill=COLOR_FLIPPER_AMBER, font=get_font(18, bold=True))

        canvas.draw.text((oct_x + 80, inp_y + 14), "(D-Pad Lewo/Prawo wybiera, Góra/Dół zmienia)", fill=COLOR_TEXT_MUTED, font=get_font(11, bold=False))

        # Calculation Details Grid
        cidr = self._calc_cidr()
        res_y = inp_y + 60

        # Left Column Card (x=cx, y=res_y, w=430, h=360)
        canvas.draw.rounded_rectangle([(cx, res_y), (cx + 430, res_y + 360)], radius=8, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((cx + 16, res_y + 12), "PARAMETRY SIECI I MASKI", fill=COLOR_CYBER_CYAN, font=get_font(13, bold=True))
        canvas.draw.line([(cx + 16, res_y + 34), (cx + 414, res_y + 34)], fill=COLOR_BORDER, width=1)

        left_items = [
            ("Maska podsieci (Netmask):", cidr["netmask"]),
            ("Maska odwrotna (Wildcard):", cidr["wildcard"]),
            ("Adres sieci (Network ID):", cidr["network"]),
            ("Adres rozgłoszeniowy (Broadcast):", cidr["broadcast"]),
            ("Zasięg hostów (Pula użyteczna):", f"{cidr['first_host']}  —"),
            ("", cidr["last_host"]),
            ("Klasa / Przeznaczenie:", cidr["scope"]),
        ]
        row_y = res_y + 46
        for lbl, val in left_items:
            canvas.draw.text((cx + 16, row_y), lbl, fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=False))
            canvas.draw.text((cx + 210, row_y), val, fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
            row_y += 38

        # Right Column Card (x=cx + 450, y=res_y, w=430, h=360)
        rcx = cx + 450
        canvas.draw.rounded_rectangle([(rcx, res_y), (rcx + 430, res_y + 360)], radius=8, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((rcx + 16, res_y + 12), "POJEMNOŚĆ I REPREZENTACJA BITOWA", fill=COLOR_CYBER_CYAN, font=get_font(13, bold=True))
        canvas.draw.line([(rcx + 16, res_y + 34), (rcx + 414, res_y + 34)], fill=COLOR_BORDER, width=1)

        right_items = [
            ("Łączna liczba adresów IP:", f"{cidr['total_hosts']:,} adresów".replace(",", " ")),
            ("Liczba użytecznych hostów:", f"{cidr['usable_hosts']:,} maszyn".replace(",", " ")),
            ("Długość prefiksu CIDR:", f"/{self.prefix_len} bitów"),
            ("Bity części hosta:", f"{32 - self.prefix_len} bitów")
        ]
        row_y = res_y + 46
        for lbl, val in right_items:
            canvas.draw.text((rcx + 16, row_y), lbl, fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=False))
            canvas.draw.text((rcx + 210, row_y), val, fill=COLOR_PHOSPHOR_GREEN, font=get_font(12, bold=True))
            row_y += 38

        # Binary strings representation
        bin_y = row_y + 10
        canvas.draw.text((rcx + 16, bin_y), "Maska (Binarnie):", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=False))
        # Format binary with spaces every 8 bits
        m_bin = cidr["mask_bin"]
        m_fmt = f"{m_bin[:8]} {m_bin[8:16]} {m_bin[16:24]} {m_bin[24:]}"
        canvas.draw.text((rcx + 16, bin_y + 20), m_fmt, fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))

        bin_y += 50
        canvas.draw.text((rcx + 16, bin_y), "Adres IP (Binarnie):", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=False))
        i_bin = cidr["ip_bin"]
        i_fmt = f"{i_bin[:8]} {i_bin[8:16]} {i_bin[16:24]} {i_bin[24:]}"
        canvas.draw.text((rcx + 16, bin_y + 20), i_fmt, fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))

    def _render_radix_tool(self, canvas):
        canvas.draw_card(
            32, 66, 960, 634,
            title="KONWERTER BAZ LICZBOWYCH & DANYCH (RADIX)",
            subtitle=f"Wartość źródłowa: {self.radix_value}  |  Krok: {self.radix_step}",
            border_color=COLOR_CYBER_CYAN
        )

        cx = 56
        cy = 128

        val = self.radix_value

        # Formatted conversions
        dec_str = f"{val}"
        hex_str = f"0x{val:04X}"
        bin_str = f"0b{val:016b}"
        oct_str = f"0o{val:06o}"

        # ASCII representation (if printable)
        ascii_char = chr(val % 256) if 32 <= (val % 256) <= 126 else "."
        b64_str = base64.b64encode(str(val).encode()).decode()

        conversions = [
            ("DZIESIĘTNY (DECIMAL, BASE 10)", dec_str, COLOR_CYBER_CYAN),
            ("SZESNASTKOWY (HEXADECIMAL, BASE 16)", hex_str, COLOR_FLIPPER_AMBER),
            ("DWÓJKOWY (BINARY, BASE 2)", f"{bin_str[:6]} {bin_str[6:10]} {bin_str[10:14]} {bin_str[14:]}", COLOR_PHOSPHOR_GREEN),
            ("ÓSEMKOWY (OCTAL, BASE 8)", oct_str, (180, 140, 255)),
            ("ZNAK ASCII (BYTE % 256)", f"'{ascii_char}' (Kod ASCII: {val % 256})", COLOR_TEXT_PRIMARY),
            ("KODOWANIE BASE64", b64_str, COLOR_NEON_PINK),
            ("PRZESUNIĘCIE W LEWO (<< 1)", f"{val << 1} (0x{(val << 1):X})", COLOR_TEXT_SECONDARY),
            ("PRZESUNIĘCIE W PRAWO (>> 1)", f"{val >> 1} (0x{(val >> 1):X})", COLOR_TEXT_SECONDARY),
        ]

        row_y = cy
        for title, value, col in conversions:
            canvas.draw.rounded_rectangle([(cx, row_y), (cx + 890, row_y + 50)], radius=6, fill=(20, 26, 36), outline=COLOR_BORDER)
            canvas.draw.text((cx + 16, row_y + 8), title, fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=True))
            canvas.draw.text((cx + 16, row_y + 24), value, fill=col, font=get_font(16, bold=True))
            row_y += 58

    def _render_resistor_tool(self, canvas):
        canvas.draw_card(
            32, 66, 960, 634,
            title="DEKODER PASKÓW REZYSTORA (4-BAND)",
            subtitle="Obliczanie rezystancji i tolerancji na podstawie barwnych kodów",
            border_color=COLOR_FLIPPER_AMBER
        )

        cx = 512
        cy = 240

        # Selected colors
        col1_name, col1_rgb, d1, _ = RESISTOR_COLORS[self.band1_idx]
        col2_name, col2_rgb, d2, _ = RESISTOR_COLORS[self.band2_idx]
        col3_name, col3_rgb, _, mult = RESISTOR_COLORS[self.band_mult_idx]
        tol_name, tol_rgb, tol_str = TOLERANCE_COLORS[self.band_tol_idx]

        # Resistance math
        res_ohms = (d1 * 10 + d2) * mult
        if res_ohms >= 1_000_000:
            res_str = f"{res_ohms / 1_000_000:.2f} MΩ"
        elif res_ohms >= 1_000:
            res_str = f"{res_ohms / 1_000:.1f} kΩ"
        else:
            res_str = f"{res_ohms} Ω"

        # Draw Physical Resistor Graphic (Center cx, cy)
        # Leads
        canvas.draw.line([(cx - 300, cy), (cx + 300, cy)], fill=(180, 190, 200), width=6)

        # Ceramic body (Beige / Cyan body)
        r_w = 340
        r_h = 100
        canvas.draw.rounded_rectangle([(cx - r_w // 2, cy - r_h // 2), (cx + r_w // 2, cy + r_h // 2)], radius=20, fill=(210, 185, 140), outline=(140, 120, 90), width=2)

        # 4 Color Bands
        bands_spec = [
            (cx - 100, col1_rgb, 0),
            (cx - 40, col2_rgb, 1),
            (cx + 20, col3_rgb, 2),
            (cx + 100, tol_rgb, 3)
        ]

        for bx, b_col, b_idx in bands_spec:
            is_active = (self.resistor_cursor == b_idx)
            bw = 24
            canvas.draw.rectangle([(bx - bw // 2, cy - r_h // 2), (bx + bw // 2, cy + r_h // 2)], fill=b_col)
            if is_active:
                # Active selection arrow
                canvas.draw.text((bx - 6, cy + r_h // 2 + 10), "▲", fill=COLOR_CYBER_CYAN, font=get_font(16, bold=True))

        # Big Result Pill (x=cx - 200, y=cy + 90, w=400, h=70)
        canvas.draw.rounded_rectangle([(cx - 200, cy + 90), (cx + 200, cy + 160)], radius=10, fill=(18, 24, 34), outline=COLOR_FLIPPER_AMBER, width=2)
        res_full_str = f"{res_str}  {tol_str}"
        canvas.draw.text((cx - len(res_full_str) * 7, cy + 105), res_full_str, fill=COLOR_TEXT_PRIMARY, font=get_font(24, bold=True))

        # Band Labels Table (y=cy + 180)
        t_y = cy + 180
        canvas.draw.text((cx - 340, t_y), f"Pasek 1 (Cyfra 1): {col1_name} ({d1})", fill=COLOR_TEXT_SECONDARY, font=get_font(12, bold=False))
        canvas.draw.text((cx - 340, t_y + 24), f"Pasek 2 (Cyfra 2): {col2_name} ({d2})", fill=COLOR_TEXT_SECONDARY, font=get_font(12, bold=False))
        canvas.draw.text((cx + 60, t_y), f"Pasek 3 (Mnożnik): {col3_name} (×{mult})", fill=COLOR_TEXT_SECONDARY, font=get_font(12, bold=False))
        canvas.draw.text((cx + 60, t_y + 24), f"Pasek 4 (Tolerancja): {tol_name}", fill=COLOR_TEXT_SECONDARY, font=get_font(12, bold=False))

    def render(self, canvas):
        if self.tool_idx == 0:
            self._render_cidr_tool(canvas)
        elif self.tool_idx == 1:
            self._render_radix_tool(canvas)
        else:
            self._render_resistor_tool(canvas)

    def handle_input(self, event: str) -> bool:
        if event == "BTN_X":
            self.tool_idx = (self.tool_idx + 1) % len(self.tool_names)
            return True

        if self.tool_idx == 0:
            # CIDR Subnet Calculator
            if event == "LEFT":
                self.cidr_cursor = (self.cidr_cursor - 1) % 5
                return True
            elif event == "RIGHT":
                self.cidr_cursor = (self.cidr_cursor + 1) % 5
                return True
            elif event == "UP":
                if self.cidr_cursor < 4:
                    self.ip_octets[self.cidr_cursor] = (self.ip_octets[self.cidr_cursor] + 1) % 256
                else:
                    self.prefix_len = min(32, self.prefix_len + 1)
                return True
            elif event == "DOWN":
                if self.cidr_cursor < 4:
                    self.ip_octets[self.cidr_cursor] = (self.ip_octets[self.cidr_cursor] - 1) % 256
                else:
                    self.prefix_len = max(1, self.prefix_len - 1)
                return True
            elif event == "BTN_Y":
                self.ip_octets = [192, 168, 1, 1]
                self.prefix_len = 24
                return True

        elif self.tool_idx == 1:
            # Radix Converter
            if event == "UP":
                self.radix_value = min(0xFFFFFFFF, self.radix_value + self.radix_step)
                return True
            elif event == "DOWN":
                self.radix_value = max(0, self.radix_value - self.radix_step)
                return True
            elif event == "RIGHT":
                self.radix_step = min(1000, self.radix_step * 10)
                return True
            elif event == "LEFT":
                self.radix_step = max(1, self.radix_step // 10)
                return True
            elif event == "BTN_Y":
                self.radix_value = 0
                return True

        elif self.tool_idx == 2:
            # Resistor Color Decoder
            if event == "LEFT":
                self.resistor_cursor = (self.resistor_cursor - 1) % 4
                return True
            elif event == "RIGHT":
                self.resistor_cursor = (self.resistor_cursor + 1) % 4
                return True
            elif event == "UP":
                if self.resistor_cursor == 0:
                    self.band1_idx = (self.band1_idx + 1) % len(RESISTOR_COLORS)
                elif self.resistor_cursor == 1:
                    self.band2_idx = (self.band2_idx + 1) % len(RESISTOR_COLORS)
                elif self.resistor_cursor == 2:
                    self.band_mult_idx = (self.band_mult_idx + 1) % len(RESISTOR_COLORS)
                else:
                    self.band_tol_idx = (self.band_tol_idx + 1) % len(TOLERANCE_COLORS)
                return True
            elif event == "DOWN":
                if self.resistor_cursor == 0:
                    self.band1_idx = (self.band1_idx - 1) % len(RESISTOR_COLORS)
                elif self.resistor_cursor == 1:
                    self.band2_idx = (self.band2_idx - 1) % len(RESISTOR_COLORS)
                elif self.resistor_cursor == 2:
                    self.band_mult_idx = (self.band_mult_idx - 1) % len(RESISTOR_COLORS)
                else:
                    self.band_tol_idx = (self.band_tol_idx - 1) % len(TOLERANCE_COLORS)
                return True
            elif event == "BTN_Y":
                # Standard 10k resistor
                self.band1_idx = 1  # 1
                self.band2_idx = 0  # 0
                self.band_mult_idx = 3  # 1000 -> 10k
                self.band_tol_idx = 2  # 5%
                return True

        return False
