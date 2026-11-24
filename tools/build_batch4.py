#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/build_batch4.py - Builds modules 057 to 067 into store/modules/
"""

import os

MODULES = {}

# 057: mod_e6b.py - Komputer Nawigacyjny Pilota E6B
MODULES["mod_e6b"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class E6bFlightComputerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.tas = 120.0     # True Airspeed kt
        self.course = 045.0  # Course deg
        self.wind_dir = 320.0
        self.wind_spd = 25.0
        self.fuel_flow = 8.5 # GPH
        self.density_alt = 4500 # ft

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 14, 24, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "✈️ 057 // E6B FLIGHT COMPUTER // CYFROWY SUWAK PILOTA", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "TRÓJKĄT WIATRU", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 90, 12, "VFR / IFR", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Wind Triangle Card
        canvas.draw_card(20, 65, 500, 440, title="WIND TRIANGLE & GROUND SPEED", subtitle="Kalkulator znoszenia i prędkości podróżnej")
        draw.text((45, 130), f"Prędkość rzeczywista (TAS): {self.tas:.0f} kt", fill=(240, 245, 255), font=get_font(16))
        draw.text((45, 165), f"Kurs magnetyczny: {self.course:.0f}°", fill=(240, 245, 255), font=get_font(16))
        draw.text((45, 200), f"Wiatr: {self.wind_dir:.0f}° / {self.wind_spd:.0f} kt", fill=(255, 170, 0), font=get_font(16, bold=True))
        
        # Wind calculations
        wca = -11.4 # Wind correction angle
        gs = 108.5  # Ground speed
        draw.rectangle([45, 250, 475, 410], fill=(14, 22, 34), outline=(0, 255, 180), width=2)
        draw.text((65, 275), f"KĄT ZNOSZENIA (WCA): {wca:+.1f}°", fill=(0, 255, 180), font=get_font(18, bold=True))
        draw.text((65, 315), f"NAMIAR MAGNETYCZNY (HDG): {self.course + wca:.1f}°", fill=(255, 220, 0), font=get_font(18, bold=True))
        draw.text((65, 355), f"PRĘDKOŚĆ WZGLĘDEM ZIEMI (GS): {gs:.1f} kt", fill=(0, 240, 255), font=get_font(20, bold=True))

        # Fuel & Distance Card
        canvas.draw_card(540, 65, 464, 440, title="PALIWO, CZAS I ZASIĘG", subtitle="Zużycie paliwa AvGas / Jet-A1")
        draw.text((565, 130), f"Zużycie (Fuel Flow): {self.fuel_flow} GPH (galon/h)", fill=(240, 245, 255), font=get_font(16))
        draw.text((565, 170), "Dystans do celu: 180 NM", fill=(240, 245, 255), font=get_font(16))
        draw.text((565, 210), "Czas lotu (ETE): 01h 39m", fill=(0, 255, 136), font=get_font(20, bold=True))
        draw.text((565, 250), "Wymagane paliwo: 14.1 galonów", fill=(255, 200, 0), font=get_font(18, bold=True))
        draw.text((565, 290), "Rezerwa paliwa VFR 45 min: +6.4 galona", fill=(160, 180, 210), font=get_font(14))

        # Bottom Altitude Card
        canvas.draw_card(20, 520, 984, 190, title="WYSOKOŚĆ GĘSTOŚCIOWA & PUNKT BEZPOWROTU (PET / PNR)", subtitle="Density Altitude & Critical Point")
        draw.text((45, 580), f"Wysokość gęstościowa (Density Altitude): {self.density_alt} ft (Rozbieg wydłużony o 28%)", fill=(255, 180, 0), font=get_font(16, bold=True))
        draw.text((45, 620), "Punkt bezpiecznego powrotu (Point of Safe Return): 94 NM od lotniska odlotu", fill=(0, 255, 180), font=get_font(15))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Góra/Dół: Zmiana Prędkości TAS | Lewo/Prawo: Kurs | [A]: Edycja Wiatru", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 058: mod_sat_tracker.py - SatTrack 3D – Namiar Anten Satelitarnych
MODULES["mod_sat_tracker"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class SatTrackerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.satellite = "HOTBIRD 13G (13.0°E)"
        self.azimuth = 184.2
        self.elevation = 31.8
        self.skew = -2.1
        self.qth = "Gorzów Wlkp. (52.73°N, 15.24°E)"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"📡 058 // SATTRACK 3D // NAMIAR ANTENY // {self.satellite}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 240, 12, "ORBITA GEO 35786 KM", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 80, 12, "KU-BAND", bg_color=(40, 30, 60), text_color=(0, 240, 255))

        # Main Angles Card
        canvas.draw_card(20, 65, 540, 440, title="KĄTY NASTAWIENIA CZASZY ANTENOWEJ", subtitle=f"Pozycja odbiorcy: {self.qth}")
        draw.text((50, 140), f"AZYMUT (POZIOM):  {self.azimuth:.1f}°", fill=(0, 255, 180), font=get_font(26, bold=True))
        draw.text((50, 210), f"ELEWACJA (PION):  {self.elevation:.1f}°", fill=(0, 240, 255), font=get_font(26, bold=True))
        draw.text((50, 280), f"SKRĘCENIE LNB (SKEW):  {self.skew:.1f}°", fill=(255, 200, 0), font=get_font(26, bold=True))
        draw.text((50, 360), "Kompas magnetyczny: Skieruj antenę niemal dokładnie na południe.", fill=(160, 185, 215), font=get_font(14))
        draw.text((50, 390), "Brak przeszkód terenowych powyżej kąta 32° nad horyzontem.", fill=(0, 255, 136), font=get_font(14, bold=True))

        # Visual Dish & Skew Diagram
        canvas.draw_card(580, 65, 424, 440, title="WIZUALIZACJA NACHYLENIA CZASZY", subtitle="Kątomierz z czujnika pochylenia")
        cx, cy = 790, 260
        draw.ellipse([(cx - 110, cy - 110), (cx + 110, cy + 110)], outline=(0, 200, 255), width=2)
        draw.line([(cx - 120, cy), (cx + 120, cy)], fill=(40, 60, 85))
        draw.line([(cx, cy - 120), (cx, cy + 120)], fill=(40, 60, 85))
        draw.line([(cx - 70, cy + 50), (cx + 70, cy - 50)], fill=(0, 255, 180), width=4)
        draw.text((cx - 50, cy + 130), "CZASZA 80 CM // OFFSET", fill=(150, 180, 210), font=get_font(13))

        # Bottom List of Satellites
        canvas.draw_card(20, 520, 984, 190, title="POZYCJE SATELITARNE W ZASIĘGU", subtitle="Wybierz satelitę do ustawienia namiaru")
        sats = ["HotBird 13°E", "Astra 19.2°E", "Eutelsat 16°E", "Astra 28.2°E", "Thor 0.8°W", "Hispasat 30°W"]
        for i, s in enumerate(sats):
            sx = 40 + i * 158
            draw.rectangle([sx, 580, sx + 145, 660], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((sx + 10, 610), s, fill=(240, 245, 255), font=get_font(13, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Satelitę | [A]: Kalibruj Kompas Konsoli | [X]: Zmień Współrzędne GPS", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 059: mod_sdr_sim.py - Symulator Wodospadu SDR & Odbiornika Radiowego
MODULES["mod_sdr_sim"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class SdrSimModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.freq_mhz = 145.500
        self.mode = "FM"
        self.rssi = -68
        self.bandwidth_khz = 12.5

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((6, 10, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 200, 100), width=1)
        draw.text((20, 14), f"🌊 059 // SDR WATERFALL & SPECTRUM SIMULATOR // {self.freq_mhz:.3f} MHZ {self.mode}", fill=(0, 255, 200), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "RTL-SDR / HACKRF", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "LIVE", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # FFT Spectrum Plot
        canvas.draw_card(20, 65, 984, 260, title="WIDMO CZĘSTOTLIWOŚCI FFT (FAST FOURIER TRANSFORM)", subtitle="Moc sygnału w pasmie 2 MHz wokół częstotliwości środkowej")
        draw.rectangle([40, 120, 980, 290], fill=(10, 16, 26), outline=(0, 180, 220))
        # Mock FFT peaks
        peaks = [(-85), (-82), (-80), (-45), (-42), (-78), (-81), (-65), (-80)]
        for i in range(len(peaks) - 1):
            x1 = 60 + i * 110
            x2 = 60 + (i + 1) * 110
            y1 = 280 - int((peaks[i] + 90) * 3)
            y2 = 280 - int((peaks[i + 1] + 90) * 3)
            draw.line([(x1, y1), (x2, y2)], fill=(0, 255, 180), width=2)
        # Tuning carrier marker
        draw.line([(512, 120), (512, 290)], fill=(255, 0, 80), width=2)
        draw.text((520, 130), f"NOŚNA: {self.freq_mhz:.3f} MHz", fill=(255, 80, 80), font=get_font(13, bold=True))

        # Waterfall (Wodospad) Area
        canvas.draw_card(20, 340, 984, 370, title="WODOSPAD RADIOELEKTRONICZNY (WATERFALL HISTORY)", subtitle="Historia transmisji w dziedzinie czasu i częstotliwości")
        draw.rectangle([40, 390, 980, 680], fill=(8, 12, 24), outline=(0, 200, 255))
        # Simulated waterfall lines
        for y in range(400, 670, 18):
            draw.rectangle([480, y, 540, y + 14], fill=(255, 180, 0))
            draw.rectangle([700, y, 740, y + 14], fill=(0, 160, 255))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Strojenie ±12.5 kHz | Góra/Dół: ±1 MHz | [A]: Zmień Modulację (AM/FM/SSB/CW)", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 060: mod_punchcard.py - Wirtualne Karty Perforowane i Dźwięk Kasetowy
MODULES["mod_punchcard"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class PunchcardModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.code_text = "HELLO BRICKDECK 2026 // RETRO-COMPUTING IBM 029"
        self.card_type = "IBM 80-COLUMN EBCDIC"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((12, 14, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(18, 22, 32, 255), outline=(220, 180, 100, 100), width=1)
        draw.text((20, 14), "💾 060 // WIRTUALNE KARTY PERFOROWANE & DŹWIĘK KASETOWY", fill=(255, 200, 100), font=get_font(18, bold=True))
        canvas.draw_badge(w - 240, 12, "KARTA IBM 5081", bg_color=(45, 35, 20))
        canvas.draw_badge(w - 75, 12, "80 KOL", bg_color=(35, 45, 60))

        # Main IBM 80-column Punchcard
        canvas.draw_card(20, 65, 984, 420, title="PERFOROWANA KARTA TEKTUROWA IBM 80 KOLUMN", subtitle="Kodowanie EBCDIC // Dziurkowanie pod programy FORTRAN / COBOL")
        cx, cy, cw, ch = 40, 120, 944, 340
        draw.rectangle([cx, cy, cx + cw, cy + ch], fill=(235, 220, 185), outline=(180, 160, 120), width=2)
        # Top text printed by card punch
        draw.text((cx + 30, cy + 20), self.code_text, fill=(40, 40, 40), font=get_font(16, bold=True))
        # Punch holes simulation
        for col in range(len(self.code_text)):
            hx = cx + 35 + col * 18
            draw.rectangle([hx, cy + 70, hx + 8, cy + 86], fill=(20, 20, 20)) # Zone punch
            draw.rectangle([hx, cy + 140, hx + 8, cy + 156], fill=(20, 20, 20)) # Digit punch
        draw.text((cx + cw - 180, cy + ch - 35), "IBM 5081 FORTRAN", fill=(100, 90, 70), font=get_font(12, bold=True))

        # Cassette Tape Audio Synthesizer Mode
        canvas.draw_card(20, 500, 984, 210, title="SYNTEZATOR DŹWIĘKU MODEMU KASETOWEGO (ZX SPECTRUM / C64)", subtitle="Generowanie pisku i modulacji FSK na głośnikach stereo")
        draw.text((45, 560), "STAN TAŚMY: [GOTOWA DO ODTWORZENIA] // MODULACJA KANSAS CITY STANDARD (300 BD)", fill=(0, 255, 180), font=get_font(15, bold=True))
        draw.text((45, 595), "Ton prowadzący (Pilot Tone): 1200 Hz | Bit '0': 1 cykl 1200 Hz | Bit '1': 2 cykle 2400 Hz", fill=(160, 185, 215), font=get_font(14))
        draw.text((45, 630), "Naciśnij [A] aby wygenerować autentyczny pisk ładowania gry retro na głośnikach.", fill=(255, 200, 0), font=get_font(14, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmień Tekst Karty | [A]: Odtwórz Dźwięk Taśmy Kasetowej | [X]: Eksport do Karty SD", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 061: mod_zmachine.py - Silnik Przygodówek Tekstowych Z-Machine / Zork
MODULES["mod_zmachine"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class ZMachineModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.game_title = "ZORK I: THE GREAT UNDERGROUND EMPIRE"
        self.score = 10
        self.moves = 24
        self.location = "West of House"
        self.story_text = (
            "You are standing in an open field west of a white house, with a boarded front door.\n\n"
            "There is a small mailbox here.\n\n"
            "> OPEN MAILBOX\n"
            "Opening the small mailbox reveals a leaflet.\n\n"
            "> READ LEAFLET\n"
            "\"WELCOME TO ZORK! ZORK is a game of adventure, danger, and low cunning. In it you will explore some of the most amazing territory ever seen by mortals.\""
        )
        self.command_choices = ["OPEN MAILBOX", "READ LEAFLET", "GO NORTH", "GO EAST", "TAKE ALL", "INVENTORY"]
        self.selected_cmd = 0

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 30, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🕹️ 061 // Z-MACHINE INTERACTIVE FICTION // {self.game_title}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"SCORE: {self.score}", bg_color=(20, 50, 30), text_color=(0, 255, 136))
        canvas.draw_badge(w - 95, 12, f"MOVES: {self.moves}", bg_color=(30, 45, 65))

        # Location status bar
        draw.rectangle([20, 60, 1004, 95], fill=(18, 26, 40))
        draw.text((36, 68), f"LOKACJA: {self.location.upper()}", fill=(255, 200, 0), font=get_font(16, bold=True))

        # Main Story Terminal Window
        canvas.draw_card(20, 105, 984, 450, title="KONSOLA FABULARNA INTERACTIVE FICTION", subtitle="Silnik Z-Machine v3/v5 kompatybilny z Infocom i Inform 7")
        sy = 160
        for para in self.story_text.split("\\n\\n"):
            draw.text((45, sy), para, fill=(230, 240, 255), font=get_font(16))
            sy += 45

        # D-Pad Wheel Action Selector
        canvas.draw_card(20, 565, 984, 150, title="WYBÓR ROZKAZU D-PADEM (KOŁOWE MENU KOMEND)", subtitle="Wybierz polecenie bez konieczności wpisywania na klawiaturze")
        for i, cmd in enumerate(self.command_choices):
            cx = 40 + i * 158
            is_sel = (i == self.selected_cmd)
            draw.rectangle([cx, 615, cx + 148, 675], fill=(24, 40, 65) if is_sel else (14, 20, 30), outline=(0, 255, 180) if is_sel else (35, 50, 70), width=2 if is_sel else 1)
            draw.text((cx + 12, 638), cmd, fill=(0, 255, 180) if is_sel else (150, 175, 205), font=get_font(13, bold=is_sel))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Wybierz Komendę | [A]: Wykonaj Polecenie | [B]: Cofnij Ruch | [Y]: Zapisz Stan Gry", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "LEFT"):
            self.selected_cmd = (self.selected_cmd - 1) % len(self.command_choices); return True
        elif event in ("KEY_RIGHT", "RIGHT"):
            self.selected_cmd = (self.selected_cmd + 1) % len(self.command_choices); return True
        return False
'''

# 062: mod_notes.py - Cyberdeck Kanban & Task Tracker
MODULES["mod_notes"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class NotesKanbanModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.todo = ["Wymiana baterii 3000mAh", "Kalibracja kompasu I2C", "Skompilować jądro 6.6"]
        self.in_progress = ["Optymalizacja Raycaster 3D", "Wdrożenie 41 modułów"]
        self.done = ["Obsługa Pyodide WASM", "Instalator OTA z GitHuba", "Skalowanie czcionek 24pt"]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "📋 062 // CYBERDECK KANBAN & TASK TRACKER // POMODORO 25:00", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "ZADANIA: 8 AKTYWNYCH", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 80, 12, "PLIKI .TXT", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # 3 Kanban Columns: To-Do | In-Progress | Done
        cols = [
            ("DO ZROBIENIA (TO DO)", self.todo, (255, 100, 100), 20),
            ("W TOKU (IN PROGRESS)", self.in_progress, (255, 200, 0), 355),
            ("UKOŃCZONE (DONE)", self.done, (0, 255, 136), 690),
        ]

        for title, tasks, col_accent, x in cols:
            canvas.draw_card(x, 65, 314, 640, title=title, subtitle=f"{len(tasks)} zadań w kolumnie")
            for i, task in enumerate(tasks):
                ty = 135 + i * 85
                draw.rectangle([x + 15, ty, x + 299, ty + 70], fill=(16, 24, 38), outline=col_accent, width=1)
                draw.text((x + 28, ty + 12), f"#{i+1}:", fill=col_accent, font=get_font(13, bold=True))
                draw.text((x + 28, ty + 32), task, fill=(230, 240, 255), font=get_font(14, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przejdź między Zadaniami | [A]: Przesuń w Prawo -> | [B]: Usuń Zadanie | [Y]: Nowe Zadanie", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 063: mod_timer.py - Multi-Timer Laboratoryjny & Metronom
MODULES["mod_timer"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class MultiTimerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.timers = [
            ("TIMER 1 // TRAWIENIE PCB", "14:32.4", True),
            ("TIMER 2 // STYGNIĘCIE ŻYWICY", "45:00.0", False),
            ("TIMER 3 // INTERWAŁ POMIARU", "02:15.8", True),
            ("TIMER 4 // KROK STROBOSKOPU", "00:30.0", False),
        ]
        self.metronome_bpm = 120

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "⏱️ 063 // MULTI-TIMER LABORATORYJNY & METRONOM AKUSTYCZNY", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "4 STOPERY PRECYZYJNE", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, f"{self.metronome_bpm} BPM", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # 4 Stopwatch Quadrants
        for i, (name, val, running) in enumerate(self.timers):
            col = i % 2
            row = i // 2
            qx = 20 + col * 500
            qy = 65 + row * 240
            canvas.draw_card(qx, qy, 484, 225, title=name, subtitle="Stoper z dokładnością do 0.1s")
            draw.text((qx + 70, qy + 90), val, fill=(0, 255, 180) if running else (160, 180, 210), font=get_font(52, bold=True))
            status_text = "🟢 DZIAŁA // POMIAR W TOKU" if running else "⏸️ ZATRZYMANY"
            draw.text((qx + 75, qy + 170), status_text, fill=(0, 255, 136) if running else (255, 170, 0), font=get_font(14, bold=True))

        # Bottom Metronome Bar
        canvas.draw_card(20, 560, 984, 150, title="METRONOM AKUSTYCZNY (TYKANIE NA GŁOŚNIKACH STEREO)", subtitle="Dźwiękowe odmierzanie tempa z akcentem na pierwszą miarę")
        draw.text((45, 615), f"TEMPO: {self.metronome_bpm} BPM // METRUM 4/4 // TON 1000 HZ", fill=(255, 200, 0), font=get_font(20, bold=True))
        draw.text((45, 655), "D-Pad Lewo/Prawo: Zmiana Tempa ±1 BPM | [A]: Start/Pauza Metronomu", fill=(140, 170, 200), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybór Stopera | [A]: Start / Stop | [B]: Reset do Zera | [Y]: Ustaw Czas Odliczania", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 064: mod_optics.py - Kalkulator Optyki Teleskopowej & Astrofotografii
MODULES["mod_optics"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class OpticsCalcModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.aperture_mm = 200.0  # 8" Dobson
        self.focal_len_mm = 1200.0
        self.eyepiece_mm = 10.0

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🔭 064 // KALKULATOR OPTYKI TELESKOPOWEJ & ASTROFOTOGRAFII", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "8\" NEWTON DOBSON", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 90, 12, "F/6.0", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Parameters Card
        canvas.draw_card(20, 65, 480, 440, title="PARAMETRY TELESKOPU & OKULARU", subtitle="Apertura i ogniskowa toru optycznego")
        mag = self.focal_len_mm / self.eyepiece_mm
        exit_pupil = self.aperture_mm / mag
        dawes_limit = 116.0 / self.aperture_mm
        draw.text((45, 130), f"Apertura (Średnica zwierciadła): {self.aperture_mm:.0f} mm", fill=(240, 245, 255), font=get_font(16))
        draw.text((45, 165), f"Ogniskowa teleskopu: {self.focal_len_mm:.0f} mm", fill=(240, 245, 255), font=get_font(16))
        draw.text((45, 200), f"Ogniskowa okularu: {self.eyepiece_mm:.0f} mm", fill=(255, 200, 0), font=get_font(16, bold=True))

        draw.rectangle([45, 250, 455, 410], fill=(14, 22, 34), outline=(0, 255, 180), width=2)
        draw.text((65, 275), f"POWIĘKSZENIE OPTYCZNE: {mag:.0f}x", fill=(0, 255, 180), font=get_font(22, bold=True))
        draw.text((65, 315), f"Źrenica wyjściowa: {exit_pupil:.2f} mm (Oko ludzkie: 5-7 mm)", fill=(0, 240, 255), font=get_font(15))
        draw.text((65, 355), f"Rozdzielczość (Kryterium Dawesa): {dawes_limit:.2f}\"", fill=(255, 220, 0), font=get_font(16, bold=True))

        # Astrophotography Rule 500 / NPF Card
        canvas.draw_card(520, 65, 484, 440, title="CZAS NAŚWIETLANIA (REGUŁA 500 & NPF)", subtitle="Maksymalny czas bez widocznego poruszenia gwiazd")
        t_500 = 500.0 / self.focal_len_mm
        draw.text((545, 130), f"Maksymalny czas naświetlania: {t_500:.2f} sek.", fill=(0, 255, 136), font=get_font(24, bold=True))
        draw.text((545, 175), "Zasięg gwiazdowy (Limiting Mag): 14.2 mag", fill=(220, 235, 255), font=get_font(16))
        draw.text((545, 215), "Pole widzenia (True FOV z okularem 52°): 0.43° (Księżyc mieści się w całości)", fill=(160, 185, 215), font=get_font(14))

        # Bottom Filters Guide
        canvas.draw_card(20, 520, 984, 190, title="REKOMENDOWANE FILTRY MGŁAWICOWE (O-III / UHC / H-ALPHA)", subtitle="Kontrast przy zanieczyszczeniu światłem (Bortle Scale 5)")
        draw.text((45, 580), "Zalecany filtr wąskopasmowy: Baader O-III (501 nm) dla mgławic planetarnych.", fill=(0, 255, 200), font=get_font(15, bold=True))
        draw.text((45, 615), "Filtr polaryzacyjny: Niezbędny do obserwacji powierzchni Księżyca w kwadrze.", fill=(160, 180, 210), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Góra/Dół: Zmiana Okularu | Lewo/Prawo: Zmiana Apertury | [A]: Wybierz Sensor Kamery", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 065: mod_acoustics.py - Kalkulator Akustyki & Rezonansów Pokoju
MODULES["mod_acoustics"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AcousticsModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.length = 5.0 # m
        self.width = 4.0  # m
        self.height = 2.6 # m
        self.speed_of_sound = 343.0 # m/s (20C)

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "📐 065 // KALKULATOR AKUSTYKI POKOJU & MODY OSIOWE (ROOM MODES)", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "WYNIK RT60: 0.42S", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "343 M/S", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Room Dimensions Card
        canvas.draw_card(20, 65, 480, 440, title="WYMIARY POMIESZCZENIA", subtitle="Kubatura i proporcje wg kryterium Bonello")
        draw.text((45, 130), f"Długość (L):  {self.length:.2f} m", fill=(240, 245, 255), font=get_font(18))
        draw.text((45, 170), f"Szerokość (W): {self.width:.2f} m", fill=(240, 245, 255), font=get_font(18))
        draw.text((45, 210), f"Wysokość (H):  {self.height:.2f} m", fill=(240, 245, 255), font=get_font(18))
        vol = self.length * self.width * self.height
        draw.text((45, 260), f"Kubatura pokoju: {vol:.1f} m³", fill=(255, 200, 0), font=get_font(16, bold=True))

        # Axial Modes Card
        canvas.draw_card(520, 65, 484, 440, title="NAJNIEŻSZE MODY OSIOWE (FALE STOJĄCE)", subtitle="Częstotliwości podbicia i wygaszania basu")
        fl = self.speed_of_sound / (2 * self.length)
        fw = self.speed_of_sound / (2 * self.width)
        fh = self.speed_of_sound / (2 * self.height)
        draw.text((545, 130), f"Mod wzdłużny (1,0,0): {fl:.1f} Hz (Podbicie basu)", fill=(0, 255, 180), font=get_font(18, bold=True))
        draw.text((545, 175), f"Mod poprzeczny (0,1,0): {fw:.1f} Hz", fill=(0, 240, 255), font=get_font(18, bold=True))
        draw.text((545, 220), f"Mod pionowy (0,0,1): {fh:.1f} Hz", fill=(255, 170, 0), font=get_font(18, bold=True))
        draw.text((545, 280), "Zalecane pułapki basowe w rogach pomieszczenia.", fill=(160, 185, 215), font=get_font(15))
        draw.text((545, 310), "Punkt podziału Schrödera: 180 Hz", fill=(160, 185, 215), font=get_font(15))

        # Bottom Delay Calculator
        canvas.draw_card(20, 520, 984, 190, title="OPÓŹNIENIE KOLUMN (SPEAKER DELAY MS) WG ODLEGŁOŚCI", subtitle="Wyrównanie fazowe kolumn i subwoofera")
        draw.text((45, 580), "Różnica odległości 1 metra = 2.91 ms opóźnienia sygnału.", fill=(0, 255, 180), font=get_font(16, bold=True))
        draw.text((45, 615), "Prędkość dźwięku wyliczana automatycznie wg temperatury otoczenia: c = 331.3 + 0.606 * T(°C)", fill=(140, 170, 200), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmiana Wymiarów Pokoju | [A]: Temperatura Otoczenia | [X]: Pokaż Wykres RT60", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 066: mod_ballistics.py - Symulator Balistyczny & Trajektorii Rzutu
MODULES["mod_ballistics"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class BallisticsModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.caliber = ".308 WINCHESTER (7.62x51mm)"
        self.v0_ms = 820.0
        self.bullet_weight_g = 10.9 # 168 gr
        self.bc_g1 = 0.462
        self.zero_distance_m = 100.0

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 30, 255), outline=(255, 140, 0, 100), width=1)
        draw.text((20, 14), f"🎯 066 // BALLISTICS LAB & TRAJECTORY SIMULATOR // {self.caliber}", fill=(255, 140, 0), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"ZERO: {self.zero_distance_m:.0f} M", bg_color=(40, 30, 15))
        canvas.draw_badge(w - 85, 12, "BC 0.462", bg_color=(20, 45, 65))

        # Ballistic Table Card
        canvas.draw_card(20, 65, 984, 440, title="TABELA BALISTYCZNA OPADU POCISKU (BULLET DROP)", subtitle="Poprawki celownika w MIL / MOA oraz energia kinetyczna w dżulach (J)")
        headers = ["DYSTANS (M)", "CZAS LOTU (S)", "PRĘDKOŚĆ (M/S)", "OPAD (CM)", "POPRAWKA MIL", "POPRAWKA MOA", "ENERGIA (J)"]
        for c, h_text in enumerate(headers):
            draw.text((45 + c * 136, 125), h_text, fill=(255, 170, 0), font=get_font(12, bold=True))

        rows = [
            ("50 m", "0.06 s", "792 m/s", "+1.2 cm", "-0.2 MIL", "-0.8 MOA", "3420 J"),
            ("100 m", "0.13 s", "764 m/s", " 0.0 cm", " 0.0 MIL", " 0.0 MOA", "3180 J"),
            ("200 m", "0.27 s", "711 m/s", "-11.8 cm", "+0.6 MIL", "+2.0 MOA", "2750 J"),
            ("300 m", "0.42 s", "659 m/s", "-42.4 cm", "+1.4 MIL", "+4.9 MOA", "2370 J"),
            ("500 m", "0.76 s", "561 m/s", "-172.5 cm", "+3.5 MIL", "+11.9 MOA", "1710 J"),
            ("800 m", "1.39 s", "428 m/s", "-612.0 cm", "+7.7 MIL", "+26.3 MOA", "1000 J"),
        ]
        for r, row in enumerate(rows):
            ry = 165 + r * 50
            draw.rectangle([35, ry - 6, 990, ry + 36], fill=(16, 22, 34) if r % 2 == 0 else (12, 16, 26))
            for c, val in enumerate(row):
                col = (0, 255, 180) if "MIL" in headers[c] else (240, 245, 255)
                draw.text((45 + c * 136, ry + 6), val, fill=col, font=get_font(14, bold=(c==0 or "MIL" in headers[c])))

        # Bottom Wind Deflection Card
        canvas.draw_card(20, 520, 984, 190, title="ZNOSZENIE PRZEZ WIATR BOCZNY (CROSSWIND DEFLECTION)", subtitle="Wiatr 4 m/s (pod kątem 90°)")
        draw.text((45, 580), "Znoszenie na 300 m: 18.4 cm (0.6 MIL) | Znoszenie na 500 m: 58.2 cm (1.2 MIL)", fill=(0, 255, 180), font=get_font(16, bold=True))
        draw.text((45, 615), "Przejście w zakres transoniczny: dystans 890 m (prędkość spada do 340 m/s)", fill=(255, 180, 0), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Dystanse | [A]: Zmień Kaliber (.223 / .308 / 6.5 CM) | [Y]: Wiatr", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 067: mod_mechanic.py - Asystent Mechanika & Baza Kodów OBD-II
MODULES["mod_mechanic"] = '''#!/usr/bin/env python3
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
        draw.text((620, 555), "Zamiennik 17\": 225/45 R17 (Różnica -0.4%)", fill=(0, 255, 136), font=get_font(13, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wprowadź Inny Kod OBD | [A]: Szukaj w Bazie | [Y]: Kalkulator Opon i Felg", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "store", "modules")
os.makedirs(output_dir, exist_ok=True)

for name, code in MODULES.items():
    path = os.path.join(output_dir, f"{name}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[+] Zapisano: {name}.py")

print(f"Batch 4 completed! Generated {len(MODULES)} modules.")
