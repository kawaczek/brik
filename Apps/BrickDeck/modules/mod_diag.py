"""
BrickDeck Module: Hardware Diagnostic & Gamepad Lab
Interactive testbench for TrimUI Brick: Gamepad button tester, Dead Pixel screen analyzer, stereo audio test, and evdev event monitor.
"""

import time
import math
from typing import List, Dict, Tuple, Optional

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN, COLOR_STATUS_ERR
)
from core.canvas import get_font


class DiagModule(BaseModule):
    name = "Hardware Diagnostic Lab"
    short_name = "Diag Lab"
    icon = "🛠️"
    accent_color = COLOR_CYBER_CYAN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.sub_mode = 0  # 0: Gamepad & Input, 1: Screen & Dead Pixels, 2: Audio & Speakers
        self.sub_mode_names = ["Tester Gamepada & Input", "Tester Ekranu (Martwe Piksele)", "Test Dźwięku Stereo"]

        # Gamepad Button States & Counters
        self.btn_states: Dict[str, bool] = {
            "UP": False, "DOWN": False, "LEFT": False, "RIGHT": False,
            "BTN_A": False, "BTN_B": False, "BTN_X": False, "BTN_Y": False,
            "BTN_L1": False, "BTN_R1": False, "MENU": False
        }
        self.btn_press_counts: Dict[str, int] = {k: 0 for k in self.btn_states}
        self.last_press_time: Dict[str, float] = {k: 0.0 for k in self.btn_states}
        self.recent_events: List[str] = []

        # Screen Test Pattern Index (for sub_mode == 1)
        self.screen_pattern_idx = 0
        self.patterns = [
            ("Czysta Czerń (#000000) - Szukanie jasnych/świecących pikseli", (0, 0, 0)),
            ("Czysta Biel (#FFFFFF) - Szukanie ciemnych/martwych pikseli", (255, 255, 255)),
            ("Czysta Czerwień (RGB Red)", (255, 0, 0)),
            ("Czysta Zieleń (RGB Green)", (0, 255, 0)),
            ("Czysty Błękit (RGB Blue)", (0, 0, 255)),
            ("Szarość 50% - Równomierność podświetlenia IPS", (128, 128, 128)),
            ("Siatka ostrości 1024x768 (Grid Pattern)", "grid"),
            ("Paski gradientu 16-stopniowego (Color Ramp)", "gradient")
        ]

        # Audio Test State
        self.audio_active_channel = "IDLE"  # "LEFT", "RIGHT", "BOTH", "IDLE"
        self.audio_timer = 0.0

    def get_hotkey_hints(self):
        if self.sub_mode == 0:
            return [
                ("L1/R1", "Moduły"),
                ("D-Pad / ABXY", "Testuj przyciski"),
                ("X", "Zmień tryb testu"),
                ("Y", "Resetuj liczniki")
            ]
        elif self.sub_mode == 1:
            return [
                ("L1/R1", "Moduły"),
                ("A / D-Pad P", "Następna plansza"),
                ("B / D-Pad L", "Poprzednia plansza"),
                ("X", "Zmień tryb testu")
            ]
        else:
            return [
                ("L1/R1", "Moduły"),
                ("A", "Test Lewy"),
                ("B", "Test Prawy"),
                ("X", "Zmień tryb testu"),
                ("Y", "Test Oba Kanały")
            ]

    def update(self, dt: float):
        # Decay active visual button highlights after 0.15s
        now = time.time()
        for k, last_t in self.last_press_time.items():
            if now - last_t > 0.15:
                self.btn_states[k] = False

        if self.audio_active_channel != "IDLE":
            self.audio_timer -= dt
            if self.audio_timer <= 0:
                self.audio_active_channel = "IDLE"

    def _render_gamepad_tester(self, canvas):
        # Main Card (x=32, y=66, w=590, h=634)
        canvas.draw_card(
            32, 66, 590, 634,
            title="WIZUALNY TESTER GAMEPADA TRIMUI BRICK",
            subtitle="Wciśnij dowolny przycisk na konsoli, aby sprawdzić reakcję",
            border_color=self.accent_color
        )

        cx = 327
        cy = 380

        # Draw Console Handheld Silhouette (TrimUI Brick 4:3 Chassis)
        body_w = 440
        body_h = 490
        bx = cx - body_w // 2
        by = cy - body_h // 2 + 20

        # Outer chassis body
        canvas.draw.rounded_rectangle(
            [(bx, by), (bx + body_w, by + body_h)],
            radius=24, fill=(24, 30, 42), outline=COLOR_BORDER, width=2
        )

        # Screen Bezel & Mini Preview (Top section of chassis)
        scr_w = 340
        scr_h = 240
        sx = cx - scr_w // 2
        sy = by + 24
        canvas.draw.rounded_rectangle(
            [(sx, sy), (sx + scr_w, sy + scr_h)],
            radius=10, fill=(10, 14, 20), outline=(40, 52, 70), width=2
        )
        canvas.draw.text((sx + 95, sy + 105), "1024×768 IPS 4:3", fill=(50, 70, 95), font=get_font(18, bold=True))
        canvas.draw.text((sx + 100, sy + 130), "OKNO AKTYWNE", fill=COLOR_PHOSPHOR_GREEN, font=get_font(12, bold=True))

        # Bumpers L1 & R1 on top shoulders
        l1_col = COLOR_CYBER_CYAN if self.btn_states["BTN_L1"] else (36, 48, 64)
        r1_col = COLOR_CYBER_CYAN if self.btn_states["BTN_R1"] else (36, 48, 64)
        canvas.draw.rounded_rectangle([(bx + 20, by - 12), (bx + 110, by + 4)], radius=6, fill=l1_col, outline=COLOR_BORDER)
        canvas.draw.text((bx + 52, by - 8), "L1", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))

        canvas.draw.rounded_rectangle([(bx + body_w - 110, by - 12), (bx + body_w - 20, by + 4)], radius=6, fill=r1_col, outline=COLOR_BORDER)
        canvas.draw.text((bx + body_w - 74, by - 8), "R1", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))

        # D-Pad Cross (Left side)
        dpad_cx = bx + 95
        dpad_cy = by + 370
        arm_w = 30
        arm_l = 84

        # Cross background
        canvas.draw.rectangle([(dpad_cx - arm_w // 2, dpad_cy - arm_l // 2), (dpad_cx + arm_w // 2, dpad_cy + arm_l // 2)], fill=(32, 40, 54))
        canvas.draw.rectangle([(dpad_cx - arm_l // 2, dpad_cy - arm_w // 2), (dpad_cx + arm_l // 2, dpad_cy + arm_w // 2)], fill=(32, 40, 54))
        canvas.draw.ellipse([(dpad_cx - 12, dpad_cy - 12), (dpad_cx + 12, dpad_cy + 12)], fill=(20, 26, 36))

        # D-Pad Arms
        up_col = COLOR_CYBER_CYAN if self.btn_states["UP"] else (44, 56, 76)
        down_col = COLOR_CYBER_CYAN if self.btn_states["DOWN"] else (44, 56, 76)
        left_col = COLOR_CYBER_CYAN if self.btn_states["LEFT"] else (44, 56, 76)
        right_col = COLOR_CYBER_CYAN if self.btn_states["RIGHT"] else (44, 56, 76)

        canvas.draw.rounded_rectangle([(dpad_cx - 13, dpad_cy - 40), (dpad_cx + 13, dpad_cy - 14)], radius=4, fill=up_col)
        canvas.draw.rounded_rectangle([(dpad_cx - 13, dpad_cy + 14), (dpad_cx + 13, dpad_cy + 40)], radius=4, fill=down_col)
        canvas.draw.rounded_rectangle([(dpad_cx - 40, dpad_cy - 13), (dpad_cx - 14, dpad_cy + 13)], radius=4, fill=left_col)
        canvas.draw.rounded_rectangle([(dpad_cx + 14, dpad_cy - 13), (dpad_cx + 40, dpad_cy + 13)], radius=4, fill=right_col)

        canvas.draw.text((dpad_cx - 5, dpad_cy - 36), "▲", fill=COLOR_TEXT_PRIMARY, font=get_font(10, bold=True))
        canvas.draw.text((dpad_cx - 5, dpad_cy + 22), "▼", fill=COLOR_TEXT_PRIMARY, font=get_font(10, bold=True))
        canvas.draw.text((dpad_cx - 32, dpad_cy - 6), "◀", fill=COLOR_TEXT_PRIMARY, font=get_font(10, bold=True))
        canvas.draw.text((dpad_cx + 24, dpad_cy - 6), "▶", fill=COLOR_TEXT_PRIMARY, font=get_font(10, bold=True))

        # ABXY Diamond (Right side)
        abxy_cx = bx + body_w - 95
        abxy_cy = by + 370
        btn_r = 16

        btn_y_col = COLOR_FLIPPER_AMBER if self.btn_states["BTN_X"] else (44, 56, 76)  # North / X
        btn_a_col = COLOR_PHOSPHOR_GREEN if self.btn_states["BTN_B"] else (44, 56, 76) # East / A
        btn_b_col = COLOR_NEON_PINK if self.btn_states["BTN_A"] else (44, 56, 76)      # South / B
        btn_x_col = COLOR_CYBER_CYAN if self.btn_states["BTN_Y"] else (44, 56, 76)     # West / Y

        # North (X)
        canvas.draw.ellipse([(abxy_cx - btn_r, abxy_cy - 36 - btn_r), (abxy_cx + btn_r, abxy_cy - 36 + btn_r)], fill=btn_y_col, outline=COLOR_BORDER)
        canvas.draw.text((abxy_cx - 5, abxy_cy - 43), "X", fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))

        # East (A)
        canvas.draw.ellipse([(abxy_cx + 36 - btn_r, abxy_cy - btn_r), (abxy_cx + 36 + btn_r, abxy_cy + btn_r)], fill=btn_a_col, outline=COLOR_BORDER)
        canvas.draw.text((abxy_cx + 31, abxy_cy - 7), "A", fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))

        # South (B)
        canvas.draw.ellipse([(abxy_cx - btn_r, abxy_cy + 36 - btn_r), (abxy_cx + btn_r, abxy_cy + 36 + btn_r)], fill=btn_b_col, outline=COLOR_BORDER)
        canvas.draw.text((abxy_cx - 5, abxy_cy + 29), "B", fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))

        # West (Y)
        canvas.draw.ellipse([(abxy_cx - 36 - btn_r, abxy_cy - btn_r), (abxy_cx - 36 + btn_r, abxy_cy + btn_r)], fill=btn_x_col, outline=COLOR_BORDER)
        canvas.draw.text((abxy_cx - 41, abxy_cy - 7), "Y", fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))

        # Center Menu Button
        menu_col = COLOR_FLIPPER_AMBER if self.btn_states["MENU"] else (36, 44, 58)
        canvas.draw.rounded_rectangle([(cx - 30, by + 440), (cx + 30, by + 464)], radius=6, fill=menu_col, outline=COLOR_BORDER)
        canvas.draw.text((cx - 18, by + 446), "MENU", fill=COLOR_TEXT_PRIMARY, font=get_font(10, bold=True))

        # ----------------------------------------------------------------------
        # Right Panel: Telemetry & Press Counter Table (x=632, y=66, w=360, h=634)
        # ----------------------------------------------------------------------
        canvas.draw_card(
            632, 66, 360, 634,
            title="LICZNIK KLIKNIĘĆ & EVDEV",
            subtitle="Rejestr zdarzeń sprzętowych",
            border_color=COLOR_BORDER
        )

        rx = 648
        ry = 118
        rw = 328

        # Table Header
        canvas.draw.rectangle([(rx, ry), (rx + rw, ry + 26)], fill=(28, 36, 48))
        canvas.draw.text((rx + 10, ry + 5), "PRZYCISK", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=True))
        canvas.draw.text((rx + 140, ry + 5), "STAN", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=True))
        canvas.draw.text((rx + 230, ry + 5), "LICZNIK", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=True))

        btn_labels = [
            ("UP", "D-Pad Góra"),
            ("DOWN", "D-Pad Dół"),
            ("LEFT", "D-Pad Lewo"),
            ("RIGHT", "D-Pad Prawo"),
            ("BTN_A", "Przycisk A"),
            ("BTN_B", "Przycisk B"),
            ("BTN_X", "Przycisk X"),
            ("BTN_Y", "Przycisk Y"),
            ("BTN_L1", "Bumper L1"),
            ("BTN_R1", "Bumper R1"),
            ("MENU", "Przycisk Menu")
        ]

        row_y = ry + 32
        for key, name in btn_labels:
            is_down = self.btn_states[key]
            count = self.btn_press_counts[key]

            bg_row = (36, 50, 70) if is_down else (20, 24, 32)
            canvas.draw.rounded_rectangle([(rx, row_y), (rx + rw, row_y + 24)], radius=4, fill=bg_row)

            canvas.draw.text((rx + 10, row_y + 4), name, fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=False))

            stat_txt = "WCISK!" if is_down else "OK"
            stat_col = COLOR_CYBER_CYAN if is_down else COLOR_TEXT_MUTED
            canvas.draw.text((rx + 140, row_y + 4), stat_txt, fill=stat_col, font=get_font(11, bold=True))

            canvas.draw.text((rx + 240, row_y + 4), str(count), fill=COLOR_PHOSPHOR_GREEN, font=get_font(12, bold=True))

            row_y += 28

        # Recent Event Stream Box
        log_box_y = row_y + 10
        canvas.draw.rounded_rectangle([(rx, log_box_y), (rx + rw, log_box_y + 140)], radius=8, fill=(16, 20, 26), outline=COLOR_BORDER)
        canvas.draw.text((rx + 10, log_box_y + 8), "STRUMIEŃ ZDARZEŃ LINUX EVDEV:", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))

        e_y = log_box_y + 28
        for ev_str in self.recent_events[-5:]:
            canvas.draw.text((rx + 10, e_y), ev_str, fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=False))
            e_y += 20

    def _render_screen_tester(self, canvas):
        pattern_name, p_val = self.patterns[self.screen_pattern_idx]

        # Inner viewport area for test
        vx = 32
        vy = 66
        vw = 960
        vh = 634

        if p_val == "grid":
            canvas.draw.rectangle([(vx, vy), (vx + vw, vy + vh)], fill=(0, 0, 0))
            # 32px alignment grid
            for gx in range(vx, vx + vw, 32):
                canvas.draw.line([(gx, vy), (gx, vy + vh)], fill=(40, 50, 70), width=1)
            for gy in range(vy, vy + vh, 32):
                canvas.draw.line([(vx, gy), (vx + vw, gy)], fill=(40, 50, 70), width=1)
            # Center crosshair
            canvas.draw.line([(vx + vw // 2, vy), (vx + vw // 2, vy + vh)], fill=COLOR_CYBER_CYAN, width=2)
            canvas.draw.line([(vx, vy + vh // 2), (vx + vw, vy + vh // 2)], fill=COLOR_CYBER_CYAN, width=2)
        elif p_val == "gradient":
            canvas.draw.rectangle([(vx, vy), (vx + vw, vy + vh)], fill=(0, 0, 0))
            step_w = vw // 16
            for step_i in range(16):
                val = int((step_i / 15.0) * 255)
                canvas.draw.rectangle([(vx + step_i * step_w, vy), (vx + (step_i + 1) * step_w, vy + vh)], fill=(val, val, val))
        else:
            canvas.draw.rectangle([(vx, vy), (vx + vw, vy + vh)], fill=p_val)

        # Overlay information pill
        canvas.draw.rounded_rectangle([(vx + 20, vy + 20), (vx + 700, vy + 70)], radius=8, fill=(16, 20, 28, 220), outline=COLOR_CYBER_CYAN, width=2)
        canvas.draw.text((vx + 34, vy + 28), f"PLANSZA {self.screen_pattern_idx + 1}/{len(self.patterns)}: {pattern_name}", fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))
        canvas.draw.text((vx + 34, vy + 48), "Naciśnij [A] lub [D-Pad P], aby zmienić kolor  |  [X], aby wrócić do testera gamepada", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=False))

    def _render_audio_tester(self, canvas):
        canvas.draw_card(
            32, 66, 960, 634,
            title="TEST GŁOŚNIKÓW STEREO TRIMUI BRICK",
            subtitle="Sprawdzenie balansu kanałów L / R i przetwornika audio",
            border_color=COLOR_PHOSPHOR_GREEN
        )

        cx = 512
        cy = 380

        # Left Speaker Box
        l_active = (self.audio_active_channel in ("LEFT", "BOTH"))
        l_col = COLOR_PHOSPHOR_GREEN if l_active else COLOR_BORDER
        l_bg = (24, 46, 36) if l_active else (20, 24, 32)
        canvas.draw.rounded_rectangle([(cx - 380, cy - 140), (cx - 60, cy + 140)], radius=16, fill=l_bg, outline=l_col, width=3 if l_active else 1)
        canvas.draw.text((cx - 260, cy - 100), "KANAŁ LEWY (L)", fill=COLOR_TEXT_PRIMARY, font=get_font(18, bold=True))
        canvas.draw.text((cx - 250, cy - 60), "🔊 SPEAKER L", fill=COLOR_CYBER_CYAN, font=get_font(14, bold=True))

        # Pulse circles if active
        if l_active:
            for ring_r in [40, 70, 100]:
                canvas.draw.ellipse([(cx - 220 - ring_r, cy + 40 - ring_r), (cx - 220 + ring_r, cy + 40 + ring_r)], outline=COLOR_PHOSPHOR_GREEN, width=2)
        canvas.draw.ellipse([(cx - 250, cy + 10), (cx - 190, cy + 70)], fill=(40, 56, 70), outline=COLOR_CYBER_CYAN)

        canvas.draw_badge(cx - 280, cy + 90, "[A] TESTUJ LEWY", bg_color=(36, 48, 64), text_color=COLOR_CYBER_CYAN)

        # Right Speaker Box
        r_active = (self.audio_active_channel in ("RIGHT", "BOTH"))
        r_col = COLOR_PHOSPHOR_GREEN if r_active else COLOR_BORDER
        r_bg = (24, 46, 36) if r_active else (20, 24, 32)
        canvas.draw.rounded_rectangle([(cx + 60, cy - 140), (cx + 380, cy + 140)], radius=16, fill=r_bg, outline=r_col, width=3 if r_active else 1)
        canvas.draw.text((cx + 170, cy - 100), "KANAŁ PRAWY (R)", fill=COLOR_TEXT_PRIMARY, font=get_font(18, bold=True))
        canvas.draw.text((cx + 180, cy - 60), "🔊 SPEAKER R", fill=COLOR_CYBER_CYAN, font=get_font(14, bold=True))

        if r_active:
            for ring_r in [40, 70, 100]:
                canvas.draw.ellipse([(cx + 220 - ring_r, cy + 40 - ring_r), (cx + 220 + ring_r, cy + 40 + ring_r)], outline=COLOR_PHOSPHOR_GREEN, width=2)
        canvas.draw.ellipse([(cx + 190, cy + 10), (cx + 250, cy + 70)], fill=(40, 56, 70), outline=COLOR_CYBER_CYAN)

        canvas.draw_badge(cx + 150, cy + 90, "[B] TESTUJ PRAWY", bg_color=(36, 48, 64), text_color=COLOR_CYBER_CYAN)

        # Status text below
        stat_txt = f"Aktywny sygnał: {self.audio_active_channel}" if self.audio_active_channel != "IDLE" else "Oczekiwanie na sygnał testowy..."
        canvas.draw.text((cx - 120, cy + 180), stat_txt, fill=COLOR_TEXT_SECONDARY, font=get_font(14, bold=True))

    def render(self, canvas):
        if self.sub_mode == 0:
            self._render_gamepad_tester(canvas)
        elif self.sub_mode == 1:
            self._render_screen_tester(canvas)
        else:
            self._render_audio_tester(canvas)

    def handle_input(self, event: str) -> bool:
        # Record button state & increment counter
        if event in self.btn_states:
            self.btn_states[event] = True
            self.btn_press_counts[event] += 1
            self.last_press_time[event] = time.time()
            ts = time.strftime("%H:%M:%S")
            self.recent_events.append(f"[{ts}] EV_KEY {event} -> PRESS")
            if len(self.recent_events) > 8:
                self.recent_events.pop(0)

        # Switch sub-mode on BTN_X
        if event == "BTN_X":
            self.sub_mode = (self.sub_mode + 1) % len(self.sub_mode_names)
            return True

        if self.sub_mode == 0:
            if event == "BTN_Y":
                for k in self.btn_press_counts:
                    self.btn_press_counts[k] = 0
                self.recent_events.clear()
                return True
        elif self.sub_mode == 1:
            if event in ("BTN_A", "RIGHT"):
                self.screen_pattern_idx = (self.screen_pattern_idx + 1) % len(self.patterns)
                return True
            elif event in ("BTN_B", "LEFT"):
                self.screen_pattern_idx = (self.screen_pattern_idx - 1) % len(self.patterns)
                return True
        elif self.sub_mode == 2:
            if event == "BTN_A":
                self.audio_active_channel = "LEFT"
                self.audio_timer = 1.0
                return True
            elif event == "BTN_B":
                self.audio_active_channel = "RIGHT"
                self.audio_timer = 1.0
                return True
            elif event == "BTN_Y":
                self.audio_active_channel = "BOTH"
                self.audio_timer = 1.0
                return True

        return False
