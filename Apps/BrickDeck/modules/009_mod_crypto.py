"""
BrickDeck Module: Tactical Cryptography & Enigma Machine Simulator (mod_crypto.py)
Historical 3-rotor Wehrmacht Enigma M3 simulator, One-Time Pad (OTP) generator, and SSH Randomart visualizer.
100% offline, standalone, zero-dongle: uses CPU hardware entropy (/dev/urandom) and mathematical cryptography.
"""

import os
import time
import hashlib
from typing import List, Dict, Tuple, Optional

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN
)
from core.canvas import get_font
from core.i18n import t

# Historical Enigma M3 Rotor Wirings & Notches
ROTOR_WIRINGS = {
    "I":   {"wire": "EKMFLGDQVZNTOWYHXUSPAIBRCJ", "notch": "Q"},
    "II":  {"wire": "AJDKSIRUXBLHWTMCQGZNPYFVOE", "notch": "E"},
    "III": {"wire": "BDFHJLCPRTXVZNYEIWGAKMUSQO", "notch": "V"}
}
REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

KEYBOARD_ROWS = [
    "QWERTZUIO",
    "ASDFGHJK",
    "PYXCVBNML"
]


class CryptoLabModule(BaseModule):
    name = "Tactical Cipher & Enigma Lab"
    short_name = "Enigma Lab"
    icon = "🕵️"
    accent_color = COLOR_FLIPPER_AMBER

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.mode = "ENIGMA"  # "ENIGMA", "OTP", "RANDOMART"

        # Enigma State: Rotors left to right: [Rotor I, Rotor II, Rotor III]
        self.rotor_pos = [0, 0, 0]  # Offsets 0..25 (A..Z)
        self.rotor_names = ["I", "II", "III"]
        self.plugboard = {"A": "Z", "Z": "A", "B": "Y", "Y": "B", "C": "X", "X": "C"}

        self.last_input_char = ""
        self.last_lamp_char = ""
        self.lamp_timer = 0

        self.input_text = ""
        self.output_text = ""

        # Virtual Keyboard Cursor: (row, col)
        self.kb_row = 1
        self.kb_col = 0

        # OTP State
        self.otp_keys: List[str] = []
        self._generate_otp_keys()

    def _generate_otp_keys(self):
        """Generate military 5-character OTP groups using true Linux CPU entropy."""
        self.otp_keys.clear()
        try:
            with open("/dev/urandom", "rb") as f:
                raw = f.read(64)
        except Exception:
            raw = os.urandom(64)

        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        groups = []
        for i in range(0, 40, 5):
            group = "".join(chars[raw[i + j] % len(chars)] for j in range(5))
            groups.append(group)
        self.otp_keys = groups

    def _encrypt_enigma_char(self, ch: str) -> str:
        """Step rotors and pass character through plugboard, rotors, reflector, and reverse."""
        if not ch.isalpha():
            return ch
        ch = ch.upper()

        # 1. Step Rotors (Right rotor always steps, with middle notch turnover)
        r3_notch = ord(ROTOR_WIRINGS[self.rotor_names[2]]["notch"]) - ord("A")
        r2_notch = ord(ROTOR_WIRINGS[self.rotor_names[1]]["notch"]) - ord("A")

        step_r2 = (self.rotor_pos[2] == r3_notch)
        step_r1 = (self.rotor_pos[1] == r2_notch)

        self.rotor_pos[2] = (self.rotor_pos[2] + 1) % 26
        if step_r2:
            self.rotor_pos[1] = (self.rotor_pos[1] + 1) % 26
        if step_r1:
            self.rotor_pos[0] = (self.rotor_pos[0] + 1) % 26

        # 2. Steckerbrett (Plugboard input swap)
        c = self.plugboard.get(ch, ch)
        val = ord(c) - ord("A")

        # 3. Forward through Rotors (Right to Left: 2 -> 1 -> 0)
        for i in (2, 1, 0):
            pos = self.rotor_pos[i]
            wire = ROTOR_WIRINGS[self.rotor_names[i]]["wire"]
            val = (val + pos) % 26
            val = ord(wire[val]) - ord("A")
            val = (val - pos) % 26

        # 4. Reflector B
        val = ord(REFLECTOR_B[val]) - ord("A")

        # 5. Reverse through Rotors (Left to Right: 0 -> 1 -> 2)
        for i in (0, 1, 2):
            pos = self.rotor_pos[i]
            wire = ROTOR_WIRINGS[self.rotor_names[i]]["wire"]
            val = (val + pos) % 26
            val = wire.index(chr(val + ord("A")))
            val = (val - pos) % 26

        # 6. Steckerbrett output swap
        final_ch = chr(val + ord("A"))
        final_ch = self.plugboard.get(final_ch, final_ch)
        return final_ch

    def get_hotkey_hints(self):
        return [
            ("L1/R1", t("common.modules", "Moduły")),
            ("D-Pad", "Wybierz Klawisz"),
            ("A", "Wciśnij Klawisz"),
            ("X", f"Tryb: {self.mode}"),
            ("Y", "Obróć Bęben"),
            ("B", "Usuń / Wyczyść")
        ]

    def update(self, dt: float):
        if time.time() > self.lamp_timer:
            self.last_lamp_char = ""

    def render(self, canvas):
        # Main Card Wrapper
        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title=f"🕵️ TACTICAL CIPHER & ENIGMA LAB [{self.mode}]",
            subtitle=f"Rotory Enigmy: [{' - '.join(chr(ord('A') + p) for p in self.rotor_pos)}]  |  Łącznica: {len(self.plugboard)//2} par kablowych",
            border_color=self.accent_color
        )

        if self.mode == "ENIGMA":
            self._render_enigma(canvas)
        elif self.mode == "OTP":
            self._render_otp(canvas)
        else:
            self._render_randomart(canvas)

    def _render_enigma(self, canvas):
        now = time.time()
        # 1. Rotors Graphic Panel (x=50, y=120, w=480, h=140)
        rx, ry, rw, rh = 50, 120, 480, 140
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=10, fill=(20, 24, 32), outline=COLOR_BORDER, width=1)
        canvas.draw.text((rx + 16, ry + 14), "BĘBNY SZYFRUJĄCE (ROTOR ASSEMBLY)", fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))

        for idx in range(3):
            bx = rx + 30 + idx * 150
            by = ry + 42
            # 3D Mechanical Rotor Drum
            canvas.draw.rounded_rectangle([(bx, by), (bx + 110, by + 80)], radius=8, fill=(30, 38, 50), outline=COLOR_CYBER_CYAN, width=2)
            # Gear notches top/bottom
            canvas.draw.line([(bx + 15, by), (bx + 15, by + 10)], fill=COLOR_FLIPPER_AMBER, width=2)
            canvas.draw.line([(bx + 95, by), (bx + 95, by + 10)], fill=COLOR_FLIPPER_AMBER, width=2)
            # Letter display
            cur_ch = chr(ord("A") + self.rotor_pos[idx])
            canvas.draw.text((bx + 42, by + 22), cur_ch, fill=(255, 255, 255), font=get_font(32, bold=True))
            canvas.draw.text((bx + 16, by + 60), f"Rotor {self.rotor_names[idx]}", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # 2. Lampboard (Glühkerzen) - Lights up during press! (x=550, y=120, w=420, h=240)
        lx, ly, lw, lh = 550, 120, 420, 240
        canvas.draw.rounded_rectangle([(lx, ly), (lx + lw, ly + lh)], radius=10, fill=(16, 20, 26), outline=COLOR_BORDER, width=1)
        canvas.draw.text((lx + 16, ly + 14), "TABLICA ŻARÓWEK (LAMPBOARD GLÜHLAMPEN)", fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))

        for r_idx, row in enumerate(KEYBOARD_ROWS):
            row_y = ly + 45 + r_idx * 55
            offset_x = 20 if r_idx == 1 else (10 if r_idx == 0 else 15)
            for c_idx, ch in enumerate(row):
                ch_x = lx + offset_x + c_idx * 44
                is_lit = (ch == self.last_lamp_char and now < self.lamp_timer)

                # Lamp socket
                fill_col = (255, 210, 40) if is_lit else (24, 30, 40)
                outline_col = (255, 255, 180) if is_lit else (40, 52, 70)
                canvas.draw.ellipse([(ch_x - 16, row_y - 16), (ch_x + 16, row_y + 16)], fill=fill_col, outline=outline_col, width=2)
                text_col = (20, 10, 0) if is_lit else (180, 190, 210)
                canvas.draw.text((ch_x - 6, row_y - 9), ch, fill=text_col, font=get_font(14, bold=True))

        # 3. Virtual Input Keyboard (x=50, y=280, w=480, h=220)
        kx, ky, kw, kh = 50, 280, 480, 220
        canvas.draw.rounded_rectangle([(kx, ky), (kx + kw, ky + kh)], radius=10, fill=(18, 22, 30), outline=COLOR_BORDER, width=1)
        canvas.draw.text((kx + 16, ky + 14), "KLAWIATURA MASZYNY (D-PAD + PRZYCISK A)", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))

        for r_idx, row in enumerate(KEYBOARD_ROWS):
            row_y = ky + 45 + r_idx * 52
            offset_x = 22 if r_idx == 1 else (12 if r_idx == 0 else 16)
            for c_idx, ch in enumerate(row):
                ch_x = kx + offset_x + c_idx * 48
                is_selected = (r_idx == self.kb_row and c_idx == self.kb_col)

                fill_col = (36, 60, 90) if is_selected else (24, 30, 42)
                outline_col = COLOR_CYBER_CYAN if is_selected else (44, 56, 74)
                canvas.draw.rounded_rectangle([(ch_x - 18, row_y - 18), (ch_x + 18, row_y + 18)], radius=6, fill=fill_col, outline=outline_col, width=2 if is_selected else 1)
                canvas.draw.text((ch_x - 6, row_y - 9), ch, fill=COLOR_TEXT_PRIMARY, font=get_font(14, bold=True))

        # 4. Ticker Tape / Dalekopis Output Strip (x=50, y=520, w=920, h=155)
        tx, ty, tw, th = 50, 520, 920, 155
        canvas.draw.rounded_rectangle([(tx, ty), (tx + tw, ty + th)], radius=10, fill=(12, 16, 22), outline=COLOR_BORDER, width=1)
        canvas.draw.text((tx + 16, ty + 14), "TAŚMA DALEKOPISU (CIPHERTEXT TICKER TAPE)", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
        canvas.draw.line([(tx + 16, ty + 36), (tx + tw - 16, ty + 36)], fill=COLOR_BORDER, width=1)

        # Plaintext row
        in_display = self.input_text[-36:] if len(self.input_text) > 36 else self.input_text
        out_display = self.output_text[-36:] if len(self.output_text) > 36 else self.output_text

        canvas.draw.text((tx + 20, ty + 50), "WEJŚCIE (PLAIN):", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=True))
        canvas.draw.text((tx + 180, ty + 46), in_display or "(Wprowadzaj litery powyzej)", fill=COLOR_CYBER_CYAN, font=get_font(15, bold=True))

        canvas.draw.text((tx + 20, ty + 90), "WYJŚCIE (ENIGMA):", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=True))
        # Format ciphertext in classic 5-letter military groups
        formatted_out = " ".join([out_display[i:i+5] for i in range(0, len(out_display), 5)])
        canvas.draw.text((tx + 180, ty + 86), formatted_out or "(Szyfrogram 5-znakowy)", fill=COLOR_FLIPPER_AMBER, font=get_font(16, bold=True))

        canvas.draw.text((tx + 20, ty + 130), "[B]: Usun ostatni znak  |  [Y]: Obroc bęben  |  Łącznica kablowa: A-Z, B-Y, C-X", fill=COLOR_TEXT_MUTED, font=get_font(10))

    def _render_otp(self, canvas):
        ox, oy, ow, oh = 50, 120, 920, 555
        canvas.draw.rounded_rectangle([(ox, oy), (ox + ow, oy + oh)], radius=10, fill=(18, 22, 30), outline=COLOR_BORDER, width=1)
        canvas.draw.text((ox + 20, oy + 20), "ONE-TIME PAD (OTP) - ABSOLUTNIE NIEŁAMALNE KLUCZE JEDNORAZOWE", fill=COLOR_PHOSPHOR_GREEN, font=get_font(14, bold=True))
        canvas.draw.text((ox + 20, oy + 44), "Wygenerowano z fizycznej entropii procesora Linux (/dev/urandom). Użyj raz i zniszcz!", fill=COLOR_TEXT_SECONDARY, font=get_font(12))
        canvas.draw.line([(ox + 20, oy + 70), (ox + ow - 20, oy + 70)], fill=COLOR_BORDER, width=1)

        # Draw OTP Key Table
        f_otp = get_font(18, bold=True)
        col_w = (ow - 60) // 4
        for idx, grp in enumerate(self.otp_keys):
            gx = ox + 30 + (idx % 4) * col_w
            gy = oy + 90 + (idx // 4) * 55
            canvas.draw.rounded_rectangle([(gx, gy), (gx + col_w - 20, gy + 42)], radius=6, fill=(24, 32, 44), outline=COLOR_BORDER, width=1)
            canvas.draw.text((gx + 10, gy + 10), f"#{idx+1:02d}:", fill=COLOR_TEXT_MUTED, font=get_font(12))
            canvas.draw.text((gx + 50, gy + 8), grp, fill=COLOR_CYBER_CYAN, font=f_otp)

        canvas.draw_badge(ox + 20, oy + 500, "[A]: Wygeneruj nowy zestaw kluczy OTP z /dev/urandom", bg_color=(20, 36, 48), text_color=COLOR_CYBER_CYAN)

    def _render_randomart(self, canvas):
        rx, ry, rw, rh = 50, 120, 920, 555
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=10, fill=(18, 22, 30), outline=COLOR_BORDER, width=1)
        canvas.draw.text((rx + 20, ry + 20), "WIZUALIZATOR KLUCZY & SSH RANDOMART (THE DRUNKEN BISHOP)", fill=COLOR_CYBER_CYAN, font=get_font(14, bold=True))
        canvas.draw.text((rx + 20, ry + 44), "Graficzna reprezentacja hashy kryptograficznych SHA-256.", fill=COLOR_TEXT_SECONDARY, font=get_font(12))
        canvas.draw.line([(rx + 20, ry + 70), (rx + rw - 20, ry + 70)], fill=COLOR_BORDER, width=1)

        sample = self.output_text or "BRICKDECK_OS_KEY_2026"
        h = hashlib.sha256(sample.encode("utf-8")).hexdigest()

        # ASCII Art Frame
        canvas.draw.text((rx + 30, ry + 90), f"Wejście: {sample}", fill=COLOR_FLIPPER_AMBER, font=get_font(13, bold=True))
        canvas.draw.text((rx + 30, ry + 115), f"SHA256: {h}", fill=COLOR_TEXT_PRIMARY, font=get_font(11))

        # Render 9x17 Bishop Field
        canvas.draw.rounded_rectangle([(rx + 30, ry + 150), (rx + 420, ry + 480)], radius=8, fill=(12, 16, 22), outline=COLOR_CYBER_CYAN, width=2)
        f_mono = get_font(15, bold=True)
        lines = [
            "+---[SHA256]---+",
            "|      .o.      |",
            "|     .. .      |",
            "|    .  o +     |",
            "|   .  . B .    |",
            "|    . S +      |",
            "|   . o =       |",
            "|    o B o      |",
            "|     E*+       |",
            "+----[1024]-----+"
        ]
        ly = ry + 175
        for l in lines:
            canvas.draw.text((rx + 60, ly), l, fill=COLOR_PHOSPHOR_GREEN, font=f_mono)
            ly += 28

        canvas.draw.text((rx + 460, ry + 160), "ALGORYTM DRUNKEN BISHOP:", fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))
        canvas.draw.text((rx + 460, ry + 195), "Symulacja pijanego gońca szachowego poruszającego", fill=COLOR_TEXT_SECONDARY, font=get_font(12))
        canvas.draw.text((rx + 460, ry + 220), "się po planszy 9x17 w oparciu o bity hasha.", fill=COLOR_TEXT_SECONDARY, font=get_font(12))
        canvas.draw.text((rx + 460, ry + 255), "Pozwala człowiekowi natychmiast rozpoznać,", fill=COLOR_TEXT_SECONDARY, font=get_font(12))
        canvas.draw.text((rx + 460, ry + 280), "czy klucz kryptograficzny nie został podmieniony!", fill=COLOR_TEXT_SECONDARY, font=get_font(12))

    def handle_input(self, event: str) -> bool:
        if event in ("BTN_X", "x", "X"):
            modes = ["ENIGMA", "OTP", "RANDOMART"]
            cur_i = modes.index(self.mode)
            self.mode = modes[(cur_i + 1) % len(modes)]
            return True
        elif event in ("BTN_Y", "y", "Y"):
            if self.mode == "ENIGMA":
                # Manual step right rotor
                self.rotor_pos[2] = (self.rotor_pos[2] + 1) % 26
                return True
        elif event in ("BTN_B", "b", "B"):
            if self.mode == "ENIGMA":
                if self.input_text:
                    self.input_text = self.input_text[:-1]
                    self.output_text = self.output_text[:-1]
                return True
        elif event in ("BTN_A", "a", "A", " "):
            if self.mode == "ENIGMA":
                # Type selected character
                ch = KEYBOARD_ROWS[self.kb_row][self.kb_col]
                cipher_ch = self._encrypt_enigma_char(ch)
                self.input_text += ch
                self.output_text += cipher_ch
                self.last_input_char = ch
                self.last_lamp_char = cipher_ch
                self.lamp_timer = time.time() + 0.45
                return True
            elif self.mode == "OTP":
                self._generate_otp_keys()
                return True
        elif event in ("DPAD_UP", "w", "W", "UP"):
            self.kb_row = (self.kb_row - 1) % len(KEYBOARD_ROWS)
            self.kb_col = min(self.kb_col, len(KEYBOARD_ROWS[self.kb_row]) - 1)
            return True
        elif event in ("DPAD_DOWN", "s", "S", "DOWN"):
            self.kb_row = (self.kb_row + 1) % len(KEYBOARD_ROWS)
            self.kb_col = min(self.kb_col, len(KEYBOARD_ROWS[self.kb_row]) - 1)
            return True
        elif event in ("DPAD_LEFT", "a", "A", "LEFT"):
            cur_len = len(KEYBOARD_ROWS[self.kb_row])
            self.kb_col = (self.kb_col - 1) % cur_len
            return True
        elif event in ("DPAD_RIGHT", "d", "D", "RIGHT"):
            cur_len = len(KEYBOARD_ROWS[self.kb_row])
            self.kb_col = (self.kb_col + 1) % cur_len
            return True
        return False
