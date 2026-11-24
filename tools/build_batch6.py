#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/build_batch6.py - Builds modules 077 to 086 into store/modules/
"""

import os

MODULES = {}

# 077: mod_tuner.py - Instrument Tuner & Pitch Generator
MODULES["mod_tuner"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TunerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.note = "A4"
        self.target_hz = 440.0
        self.detected_hz = 440.2
        self.cents_diff = +0.8
        self.instrument = "GITARA STANDARD (E A D G B E)"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), f"🎸 077 // INSTRUMENT TUNER & PITCH GENERATOR // {self.instrument}", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "STROIK CHROMATYCZNY", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 90, 12, "IN TUNE", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big Tuning Arc / Strobe Card
        canvas.draw_card(20, 65, 620, 440, title="WSKAŹNIK DOSTROJENIA (CENTS DIFF)", subtitle="Dokładność ±0.1 centa // Algorytm autokorelacji YIN")
        draw.text((240, 140), self.note, fill=(0, 255, 136), font=get_font(96, bold=True))
        draw.text((230, 250), f"{self.detected_hz:.1f} Hz", fill=(255, 220, 0), font=get_font(28, bold=True))
        draw.text((205, 290), f"Różnica: {self.cents_diff:+.1f} centów (IDEALNIE)", fill=(0, 255, 180), font=get_font(16, bold=True))

        # Tuning Needle
        draw.rectangle([60, 350, 580, 380], fill=(16, 26, 40), outline=(0, 200, 255))
        center_x = 320
        needle_x = center_x + int(self.cents_diff * 4)
        draw.line([(center_x, 340), (center_x, 390)], fill=(120, 150, 180), width=2)
        draw.line([(needle_x, 345), (needle_x, 385)], fill=(0, 255, 136), width=4)
        draw.text((center_x - 12, 395), "0", fill=(0, 255, 136), font=get_font(14, bold=True))
        draw.text((80, 395), "-50 CENTS", fill=(100, 130, 160), font=get_font(12))
        draw.text((500, 395), "+50 CENTS", fill=(100, 130, 160), font=get_font(12))

        # Guitar Strings Card
        canvas.draw_card(660, 65, 344, 440, title="STRUNY GITAROWE", subtitle="Wybór struny docelowej")
        strings = [
            ("E2 (Najgrubsza)", "82.4 Hz"),
            ("A2", "110.0 Hz"),
            ("D3", "146.8 Hz"),
            ("G3", "196.0 Hz"),
            ("B3", "246.9 Hz"),
            ("E4 (Wiolinowa)", "329.6 Hz"),
        ]
        for i, (s_name, s_hz) in enumerate(strings):
            sy = 125 + i * 55
            draw.rectangle([675, sy, 985, sy + 48], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((690, sy + 14), s_name, fill=(240, 245, 255), font=get_font(14, bold=True))
            draw.text((890, sy + 14), s_hz, fill=(0, 255, 180), font=get_font(14))

        # Bottom Tone Generator Card
        canvas.draw_card(20, 520, 984, 190, title="GENERATOR WZORCOWEGO TONU ODNIESIENIA (PITCH GENERATOR)", subtitle="Czysty sinus A4 = 440 Hz (lub 432 Hz) na głośnikach stereo")
        draw.text((45, 580), "STAN GENERATORA: [AKTYWNY] // TON A4 = 440.0 HZ", fill=(0, 255, 180), font=get_font(16, bold=True))
        draw.text((45, 615), "Naciśnij [A] aby włączyć/wyłączyć ton referencyjny. Klawisz [X] przełącza strój na 432 Hz.", fill=(160, 185, 215), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmień Strunę / Nutę | [A]: Odtwórz Dźwięk Wzorcowy | [X]: Kalibracja A4 (440/432 Hz)", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 078: mod_gravity.py - Symulator Grawitacji N-Ciał & Orbit
MODULES["mod_gravity"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class GravitySimModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.bodies = [
            {"name": "GWIAZDA CENTRALNA", "x": 512, "y": 384, "mass": 1000, "col": (255, 220, 0), "r": 18},
            {"name": "PLANETA A (BLISKA)", "x": 680, "y": 384, "mass": 10, "col": (0, 240, 255), "r": 8},
            {"name": "PLANETA B (Z PIERŚCIENIEM)", "x": 840, "y": 384, "mass": 25, "col": (0, 255, 140), "r": 12},
            {"name": "SONDA KOSMICZNA", "x": 710, "y": 360, "mass": 1, "col": (255, 80, 80), "r": 4},
        ]
        self.time_speed = 1.0

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((4, 8, 16, 255))

        draw.rectangle([0, 0, w, 50], fill=(12, 18, 30, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🪐 078 // N-BODY GRAVITATIONAL ORBIT SIMULATOR // PRAWA KEPLERA", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "FIZYKA NEWTONA", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "60 FPS", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main Deep Space Orbit View
        canvas.draw_card(20, 65, 700, 640, title="PRZESTRZEŃ GRAWITACYJNA (ORBITY KEPLERA)", subtitle="Symulacja numeryczna Rungego-Kutty RK4")
        # Draw orbit paths
        draw.ellipse([(512 - 168, 384 - 168), (512 + 168, 384 + 168)], outline=(0, 120, 180), width=1)
        draw.ellipse([(512 - 328, 384 - 328), (512 + 328, 384 + 328)], outline=(0, 120, 180), width=1)

        # Draw bodies
        for b in self.bodies:
            bx, by, br, bcol = b["x"], b["y"], b["r"], b["col"]
            draw.ellipse([(bx - br, by - br), (bx + br, by + br)], fill=bcol)
            draw.text((bx + br + 8, by - 6), b["name"].split()[0], fill=bcol, font=get_font(11, bold=True))

        # Right Telemetry Card
        canvas.draw_card(735, 65, 269, 640, title="PARAMETRY ORBITALNE", subtitle="Prędkości i okresy obiegu")
        for i, b in enumerate(self.bodies):
            by = 135 + i * 110
            draw.rectangle([750, by, 990, by + 95], fill=(14, 20, 32), outline=b["col"], width=1)
            draw.text((760, by + 10), b["name"], fill=b["col"], font=get_font(12, bold=True))
            draw.text((760, by + 32), f"Masa: {b['mass']} M_earth", fill=(210, 225, 245), font=get_font(13))
            v_val = 29.8 / (i + 1)
            draw.text((760, by + 56), f"Prędkość: {v_val:.1f} km/s", fill=(0, 255, 180), font=get_font(13, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Manewr Sondą | [A]: Wystrzel Nowe Ciało | [X]: Prędkość Czasu (1x/2x/5x) | [B]: Reset", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 079: mod_turing.py - Symulator Maszyny Turinga
MODULES["mod_turing"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TuringMachineModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.program_name = "INKREMENTACJA LICZBY BINARNEJ (+1)"
        self.head_pos = 9
        self.state = "q1"
        self.step_count = 14
        self.tape = ["0", "0", "1", "1", "0", "1", "0", "1", "1", "1", "0", "0", "0", "0", "0", "0", "0", "0"]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), f"🧠 079 // TURING MACHINE SIMULATOR // {self.program_name}", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"STAN: {self.state}", bg_color=(20, 50, 40))
        canvas.draw_badge(w - 90, 12, f"KROK: {self.step_count}", bg_color=(35, 45, 65))

        # Main Infinite Tape Box
        canvas.draw_card(20, 65, 984, 280, title="PRZESUWNA TAŚMA WIRTUALNA & GŁOWICA (R/W HEAD)", subtitle="Model matematyczny uniwersalnego komputera Alana Turinga (1936)")
        # Tape Cells
        cell_w = 48
        for i, val in enumerate(self.tape):
            cx = 40 + i * cell_w
            is_head = (i == self.head_pos)
            bg = (0, 80, 140) if is_head else (16, 26, 40)
            border = (0, 255, 180) if is_head else (40, 60, 85)
            draw.rectangle([cx, 160, cx + cell_w - 4, 230], fill=bg, outline=border, width=2 if is_head else 1)
            draw.text((cx + 14, 175), val, fill=(255, 255, 255), font=get_font(32, bold=True))
            if is_head:
                # Arrow pointing to active cell
                draw.polygon([(cx + 22, 145), (cx + 10, 125), (cx + 34, 125)], fill=(255, 200, 0))
                draw.text((cx - 8, 105), f"GŁOWICA [{self.state}]", fill=(255, 200, 0), font=get_font(12, bold=True))

        # State Transition Table Card
        canvas.draw_card(20, 360, 984, 345, title="TABLICA PRZEJŚĆ AUTOMATU (TRANSITION RULES)", subtitle="Reguły: (Stan bieżący, Znak) -> (Nowy stan, Zapis, Ruch L/R)")
        rules = [
            ("(q0, 0) -> (q0, 0, R)", "Przewijaj w prawo do końca liczby"),
            ("(q0, 1) -> (q0, 1, R)", "Przewijaj w prawo do końca liczby"),
            ("(q0, B) -> (q1, B, L)", "Koniec liczby znaleziony, cofnij o 1"),
            ("(q1, 0) -> (q_halt, 1, N)", "Zamień 0 na 1 i zatrzymaj maszynę"),
            ("(q1, 1) -> (q1, 0, L)", "Przeniesienie: zamień 1 na 0 i idź w lewo"),
        ]
        for i, (rule, desc) in enumerate(rules):
            ry = 425 + i * 52
            draw.rectangle([40, ry, 980, ry + 44], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((60, ry + 12), rule, fill=(0, 255, 180), font=get_font(15, bold=True))
            draw.text((450, ry + 12), f"// {desc}", fill=(160, 185, 215), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przesuń Taśmę | [A]: Wykonaj Jeden Krok | [X]: Autoodtwarzanie (Run) | [B]: Reset Taśmy", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 080: mod_ipam.py - Subnet CIDR Matrix & IPAM Planner
MODULES["mod_ipam"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class IpamPlannerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.supernet = "10.0.0.0/16 (65 536 Adresów IP)"
        self.subnets = [
            ("VLAN 10 // INFRASTRUKTURA SERWEROWA", "10.0.1.0/24", "254 hosty", True),
            ("VLAN 20 // STACJE ROBOCZE I BIURO", "10.0.2.0/23", "510 hostów", True),
            ("VLAN 50 // SIEĆ WI-FI DLA GOŚCI", "10.0.4.0/24", "254 hosty", True),
            ("VLAN 99 // ZARZĄDZANIE OOB / IPMI", "10.0.10.0/26", "62 hosty", True),
            ("WOLNA PRZESTRZEŃ ADRESOWA", "10.0.11.0/24", "Dostępna", False),
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🗺️ 080 // SUBNET CIDR MATRIX & IPAM PLANNER // {self.supernet}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "IPAM // RFC 1918", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 80, 12, "VLAN", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Visual Grid of Address Blocks
        canvas.draw_card(20, 65, 984, 180, title="WIZUALNA MATRYCA PODZIAŁU PRZESTRZENI /16", subtitle="Klockowy podział na podsieci bez nakładania się zakresów")
        bx = 40
        widths = [180, 320, 180, 90, 170]
        cols = [(0, 240, 255), (0, 255, 136), (255, 170, 0), (180, 80, 255), (30, 45, 65)]
        for i, (name, cidr, hosts, used) in enumerate(self.subnets):
            w_block = widths[i]
            draw.rectangle([bx, 120, bx + w_block, 200], fill=cols[i])
            draw.text((bx + 10, 135), cidr, fill=(10, 15, 25) if used else (160, 180, 210), font=get_font(14, bold=True))
            draw.text((bx + 10, 165), hosts, fill=(10, 15, 25) if used else (120, 140, 170), font=get_font(12, bold=True))
            bx += w_block + 4

        # Detailed Subnet Table Card
        canvas.draw_card(20, 260, 984, 445, title="REJESTR PODSIECI I BRAM DOMYŚLNYCH", subtitle="Konfiguracja routerów i serwerów DHCP")
        for i, (name, cidr, hosts, used) in enumerate(self.subnets):
            sy = 320 + i * 72
            draw.rectangle([40, sy, 980, sy + 62], fill=(16, 24, 38), outline=(0, 200, 255) if used else (40, 60, 85))
            draw.text((60, sy + 12), name, fill=(0, 255, 180) if used else (120, 140, 170), font=get_font(14, bold=True))
            draw.text((60, sy + 35), f"Zakres CIDR: {cidr}  |  Pojemność: {hosts}", fill=(220, 235, 255), font=get_font(13))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Podsieć | [A]: Podziel na Dwie (/+1) | [B]: Połącz Podsieci | [Y]: Eksport Bazy", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 081: mod_telehack.py - 80s ARPANET BBS & Wardialer
MODULES["mod_telehack"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TelehackBbsModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.terminal_lines = [
            "CONNECT 1200 / ARPANET GATEWAY IMP #4 (MIT-AI)",
            "Last login: Fri Oct 29 1982 from SRI-NIC",
            "Type 'help' for command summary.",
            "",
            "> wardial 213-555-0100",
            "Scanning prefix (213) 555-0100 ... DIALING...",
            "Carrier detected at 213-555-0142! [WOPR MAINFRAME]",
            "",
            "LOGON: Joshua",
            "GREETINGS PROFESSOR FALKEN.",
            "SHALL WE PLAY A GAME?",
            "> 1. GLOBAL THERMONUCLEAR WAR",
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((4, 10, 6, 255)) # Green phosphor CRT

        draw.rectangle([0, 0, w, 50], fill=(8, 16, 10, 255), outline=(0, 255, 136, 100), width=1)
        draw.text((20, 14), "📠 081 // 80S ARPANET BBS & WARDIALER // VT100 PHOSPHOR CRT", fill=(0, 255, 136), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "MODEM: 1200 BAUD", bg_color=(10, 40, 20), text_color=(0, 255, 136))
        canvas.draw_badge(w - 80, 12, "WARGAMES", bg_color=(20, 45, 25))

        # Big Retro Green CRT Screen
        canvas.draw_card(20, 65, 984, 640, title="TERMINAL TEKSTOWY TELEHACK / WOPR", subtitle="Autentyczna symulacja sieci z lat 80. z filmami ASCII i botem ELIZA")
        ty = 130
        for line in self.terminal_lines:
            col = (255, 220, 0) if "SHALL WE" in line or "GLOBAL" in line else (0, 255, 136)
            draw.text((45, ty), line, fill=col, font=get_font(17, bold=(">" in line or "CARRIER" in line)))
            ty += 34
        # Blinking CRT block cursor
        draw.rectangle([45, ty + 5, 60, ty + 25], fill=(0, 255, 136))

        draw.rectangle([0, 724, w, 768], fill=(8, 16, 10, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Terminal | [A]: Wyślij Komendę | [X]: Uruchom Wardialer | [Y]: Rozmowa z ELIZA", fill=(0, 200, 110), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 082: mod_fluid.py - Real-Time Fluid Dynamics Naviera-Stokesa
MODULES["mod_fluid"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class FluidDynamicsModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.viscosity = 0.001
        self.vorticity = 2.4
        self.dye_rgb = (0, 240, 255)
        self.fps = 60

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((6, 10, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🌊 082 // REAL-TIME FLUID DYNAMICS // RÓWNANIA NAVIERA-STOKESA", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "SIATKA 128x96", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "60 FPS", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main Fluid Simulation Box
        canvas.draw_card(20, 65, 720, 640, title="DYFUZJA & ADWEKCJA PRĄDÓW WIROWYCH", subtitle="Mieszaj ciecz D-Padem, wstrzykuj pigment klawiszem [A]")
        # Draw fluid swirls simulation
        for ring in range(20, 280, 25):
            col = (0, int(ring * 0.8), int(255 - ring * 0.5))
            draw.ellipse([(380 - ring, 380 - ring), (380 + ring, 380 + ring)], outline=col, width=2)
        draw.text((280, 370), "WIR HYDRAULICZNY", fill=(0, 255, 180), font=get_font(18, bold=True))

        # Right Controls & Physics Telemetry
        canvas.draw_card(755, 65, 249, 640, title="PARAMETRY CIECZY", subtitle="Stałe hydrodynamiczne")
        draw.text((770, 130), "LEPKOŚĆ (VISCOSITY):", fill=(140, 170, 200), font=get_font(12, bold=True))
        draw.text((770, 155), f"{self.viscosity:.4f} Pa·s", fill=(0, 255, 180), font=get_font(18, bold=True))
        draw.text((770, 210), "WIROWOŚĆ (VORTICITY):", fill=(140, 170, 200), font=get_font(12, bold=True))
        draw.text((770, 235), f"{self.vorticity:.1f} s⁻¹", fill=(255, 200, 0), font=get_font(18, bold=True))
        draw.text((770, 290), "LICZBA REYNOLDSA:", fill=(140, 170, 200), font=get_font(12, bold=True))
        draw.text((770, 315), "Re = 42 000 (Turbulentny)", fill=(240, 245, 255), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Mieszaj Ciecz / Prądy | [A]: Wstrzyknij Pigment | [X]: Zmień Kolor Barwnika | [B]: Wyczyść Płyn", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 083: mod_rhythm.py - Cyber Beat Pocket Tap
MODULES["mod_rhythm"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class RhythmBeatModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.score = 14250
        self.combo = 28
        self.accuracy = "PERFECT!"
        self.song_title = "CYBERPUNK HIGHWAY // 140 BPM"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 8, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(18, 14, 30, 255), outline=(255, 0, 128, 100), width=1)
        draw.text((20, 14), f"🎵 083 // CYBER BEAT POCKET TAP // {self.song_title}", fill=(255, 0, 128), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"SCORE: {self.score}", bg_color=(45, 10, 30))
        canvas.draw_badge(w - 85, 12, f"COMBO: x{self.combo}", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # 4 Rhythm Tracks Card
        canvas.draw_card(20, 65, 700, 640, title="TORY SPADAJĄCYCH NUT (BEAT LANES)", subtitle="Wciskaj [D-Pad Lewo], [Góra], [Prawo], [A] w rytm muzyki")
        lanes_x = [100, 240, 380, 520]
        lane_keys = ["◀ LEWO", "▲ GÓRA", "▶ PRAWO", "● [A]"]
        lane_cols = [(0, 240, 255), (0, 255, 136), (255, 200, 0), (255, 0, 128)]

        # Draw vertical tracks
        for i, lx in enumerate(lanes_x):
            draw.rectangle([lx, 120, lx + 120, 640], fill=(16, 12, 28), outline=(40, 30, 60))
            # Falling note blocks
            draw.rectangle([lx + 10, 200 + i * 80, lx + 110, 230 + i * 80], fill=lane_cols[i])
            # Target hit line at bottom
            draw.rectangle([lx, 580, lx + 120, 610], outline=lane_cols[i], width=3)
            draw.text((lx + 25, 618), lane_keys[i], fill=lane_cols[i], font=get_font(13, bold=True))

        # Right Combo & Rating Card
        canvas.draw_card(735, 65, 269, 640, title="OCENA CELNOŚCI", subtitle="Hit Timing Window")
        draw.text((760, 160), self.accuracy, fill=(0, 255, 136), font=get_font(36, bold=True))
        draw.text((760, 230), f"COMBO: x{self.combo}", fill=(255, 200, 0), font=get_font(28, bold=True))
        draw.text((760, 310), "Statystyki:", fill=(140, 170, 200), font=get_font(14))
        draw.text((760, 340), "• PERFECT: 84", fill=(0, 255, 136), font=get_font(15, bold=True))
        draw.text((760, 370), "• GREAT:   12", fill=(0, 240, 255), font=get_font(15))
        draw.text((760, 400), "• MISS:     0", fill=(100, 120, 150), font=get_font(15))

        draw.rectangle([0, 724, w, 768], fill=(16, 12, 26, 255))
        draw.text((20, 738), "Trafiaj w nuty: D-Pad Lewo / Góra / Prawo / [A] | [START]: Pauza Utworu", fill=(255, 180, 220), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 084: mod_wireframe_race.py - Synthwave Vector Highway 3D
MODULES["mod_wireframe_race"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class WireframeRaceModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.speed_kmh = 248
        self.score = 8420
        self.time_left = 42.5
        self.car_x = 512

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 4, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(20, 8, 32, 255), outline=(255, 0, 180, 100), width=1)
        draw.text((20, 14), "🏎️ 084 // SYNTHWAVE VECTOR HIGHWAY 3D // OUTRUN RETRO RACE", fill=(255, 0, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"{self.speed_kmh} KM/H", bg_color=(60, 10, 40), text_color=(255, 0, 180))
        canvas.draw_badge(w - 80, 12, f"{self.time_left:.1f}S", bg_color=(20, 50, 40), text_color=(0, 255, 136))

        # Main 3D Vector Highway Perspective
        canvas.draw_card(20, 65, 984, 640, title="NEONOWA TRASA WEKTOROWA (PSEUDO-3D)", subtitle="Wymijaj cyber-samochody D-Padem, zbieraj punkty kontrolne")
        horizon_y = 320
        # Draw perspective road lines
        draw.line([(512, horizon_y), (40, 680)], fill=(0, 240, 255), width=3)
        draw.line([(512, horizon_y), (984, 680)], fill=(0, 240, 255), width=3)
        draw.line([(512, horizon_y), (512, 680)], fill=(255, 220, 0), width=2) # Center line

        # Big Retro Neon Sun on horizon
        draw.ellipse([(512 - 70, horizon_y - 70), (512 + 70, horizon_y + 70)], fill=(255, 60, 120))
        for gy in range(horizon_y - 50, horizon_y + 50, 14):
            draw.line([(512 - 68, gy), (512 + 68, gy)], fill=(10, 4, 20), width=3)

        # Player Car (Wireframe Vector Style)
        cx = self.car_x
        draw.rectangle([cx - 50, 580, cx + 50, 640], fill=(255, 0, 128), outline=(0, 255, 255), width=2)
        draw.rectangle([cx - 35, 595, cx + 35, 620], fill=(10, 20, 40))
        # Tail lights
        draw.rectangle([cx - 45, 625, cx - 25, 635], fill=(255, 0, 0))
        draw.rectangle([cx + 25, 625, cx + 45, 635], fill=(255, 0, 0))

        draw.rectangle([0, 724, w, 768], fill=(16, 8, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Sterowanie Autem | [A]: Przyspieszenie (Nitro) | [B]: Hamulec", fill=(255, 150, 220), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 085: mod_laser_optics.py - Laser Matrix & Optics Lab
MODULES["mod_laser_optics"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class LaserOpticsModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.level = 4
        self.score = 2400
        self.lasers = [((80, 240), (450, 240), (450, 520), (840, 520))]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((6, 12, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), f"🪞 085 // LASER MATRIX & OPTICS LAB // POZIOM {self.level}", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"PUNKTY: {self.score}", bg_color=(20, 50, 40))
        canvas.draw_badge(w - 85, 12, "POZIOM 4", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main Laser Grid
        canvas.draw_card(20, 65, 984, 640, title="LABIRYNT OPTYCZNY (ZWIERCIADŁA I PRYZMATY)", subtitle="Ustaw kąty luster, aby doprowadzić promień lasera do sensora docelowego")
        # Draw laser path
        draw.line([(80, 240), (450, 240)], fill=(0, 255, 136), width=4)
        draw.line([(450, 240), (450, 520)], fill=(0, 255, 136), width=4)
        draw.line([(450, 520), (840, 520)], fill=(0, 255, 136), width=4)

        # Mirrors
        draw.line([(430, 220), (470, 260)], fill=(255, 255, 255), width=6) # Mirror 1
        draw.line([(430, 540), (470, 500)], fill=(255, 255, 255), width=6) # Mirror 2

        # Target receptor
        draw.ellipse([(830, 510), (850, 530)], fill=(255, 220, 0), outline=(255, 0, 80), width=3)
        draw.text((865, 512), "CEL AKTYWNY (100%)", fill=(255, 220, 0), font=get_font(14, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Zwierciadło | [A]: Obróć Zwierciadło o 45° | [X]: Dodaj Pryzmat RGB | [B]: Reset Poziomu", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 086: mod_missile_command.py - Cyber Defense Interceptor
MODULES["mod_missile_command"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class MissileCommandModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.score = 4850
        self.cities_left = 4
        self.missiles_ammo = 18
        self.target_x = 512
        self.target_y = 350

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 10, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(255, 80, 80, 100), width=1)
        draw.text((20, 14), "🚀 086 // CYBER DEFENSE MISSILE INTERCEPTOR // ARCADE DEFENSE", fill=(255, 80, 80), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"PUNKTY: {self.score}", bg_color=(50, 15, 20))
        canvas.draw_badge(w - 85, 12, f"RAKIETY: {self.missiles_ammo}", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main Combat Theater Card
        canvas.draw_card(20, 65, 984, 640, title="TEATR DZIAŁAŃ OBRONY PRZECIWRAKIETOWEJ", subtitle="Celuj D-Padem, wystrzeliwuj wybuchy kasetowe klawiszem [A]")
        
        # Enemy incoming ballistic streaks
        draw.line([(150, 120), (320, 600)], fill=(255, 60, 60), width=2)
        draw.line([(550, 120), (480, 600)], fill=(255, 60, 60), width=2)
        draw.line([(850, 120), (750, 600)], fill=(255, 60, 60), width=2)

        # Flak explosion
        draw.ellipse([(self.target_x - 40, self.target_y - 40), (self.target_x + 40, self.target_y + 40)], outline=(0, 255, 200), width=3)
        draw.text((self.target_x - 30, self.target_y - 10), "WYBUCH FLAK", fill=(0, 255, 200), font=get_font(12, bold=True))

        # Ground and 6 Cities to protect
        draw.rectangle([40, 620, 980, 660], fill=(20, 40, 30))
        for c in range(6):
            cx = 120 + c * 140
            draw.rectangle([cx, 595, cx + 50, 620], fill=(0, 200, 255))
            draw.text((cx + 10, 600), "MIASTO", fill=(10, 20, 30), font=get_font(10, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Ruch Celownikiem | [A]: Ognia Bateria Środkowa | [L1/R1]: Bateria Lewa / Prawa", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "store", "modules")
os.makedirs(output_dir, exist_ok=True)

for name, code in MODULES.items():
    path = os.path.join(output_dir, f"{name}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[+] Zapisano: {name}.py")

print(f"Batch 6 completed! Generated {len(MODULES)} modules.")
