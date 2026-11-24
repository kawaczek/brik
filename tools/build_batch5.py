#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/build_batch5.py - Builds modules 068 to 076 into store/modules/
"""

import os

MODULES = {}

# 068: mod_astroclock.py - Praski Zegar Astronomiczny – Orloj
MODULES["mod_astroclock"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AstroClockModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.sun_zodiac = "STRZELEC (SAGITTARIUS ♐)"
        self.moon_phase = "PIERWSZA KWADRA (52%)"
        self.sidereal_time = "21:14:08 LST"
        self.babylonian_hour = "GODZINA 7. SŁONECZNA"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 24, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(255, 200, 0, 100), width=1)
        draw.text((20, 14), "🏛️ 068 // PRASKI ZEGAR ASTRONOMICZNY // ORLOJ (1410)", fill=(255, 210, 0), font=get_font(18, bold=True))
        canvas.draw_badge(w - 240, 12, "CZAS GWIEZDNY (LST)", bg_color=(35, 30, 20))
        canvas.draw_badge(w - 75, 12, "ZODIAK", bg_color=(40, 30, 60), text_color=(0, 240, 255))

        # Big Astrolabe Dial
        canvas.draw_card(20, 65, 540, 440, title="CYFERBLAT ASTRONOMICZNY (ASTROLABIUM)", subtitle="Rzut stereograficzny sfery niebieskiej")
        cx, cy = 290, 280
        draw.ellipse([(cx - 150, cy - 150), (cx + 150, cy + 150)], outline=(255, 200, 0), width=3)
        draw.ellipse([(cx - 90, cy - 90), (cx + 90, cy + 90)], outline=(0, 200, 255), width=2)
        draw.line([(cx - 160, cy), (cx + 160, cy)], fill=(40, 60, 85))
        draw.line([(cx, cy - 160), (cx, cy + 160)], fill=(40, 60, 85))
        # Sun & Moon Pointers
        draw.line([(cx, cy), (cx + 80, cy - 90)], fill=(255, 220, 0), width=3) # Sun
        draw.ellipse([(cx + 74, cy - 96), (cx + 86, cy - 84)], fill=(255, 220, 0))
        draw.line([(cx, cy), (cx - 100, cy + 50)], fill=(200, 225, 255), width=2) # Moon
        draw.ellipse([(cx - 106, cy + 44), (cx - 94, cy + 56)], fill=(200, 225, 255))

        # Astronomy Telemetry Card
        canvas.draw_card(580, 65, 424, 440, title="PARAMETRY ASTRONOMICZNE", subtitle="Wskazania słońca, księżyca i zodiaku")
        draw.text((605, 130), "POŁOŻENIE SŁOŃCA W ZODIAKU:", fill=(140, 170, 200), font=get_font(13))
        draw.text((605, 155), self.sun_zodiac, fill=(255, 210, 0), font=get_font(18, bold=True))
        draw.text((605, 210), "FAZA KSIĘŻYCA:", fill=(140, 170, 200), font=get_font(13))
        draw.text((605, 235), self.moon_phase, fill=(220, 240, 255), font=get_font(18, bold=True))
        draw.text((605, 290), "CZAS GWIEZDNY (SIDEREAL):", fill=(140, 170, 200), font=get_font(13))
        draw.text((605, 315), self.sidereal_time, fill=(0, 240, 255), font=get_font(22, bold=True))
        draw.text((605, 370), "GODZINA BABILOŃSKA:", fill=(140, 170, 200), font=get_font(13))
        draw.text((605, 395), self.babylonian_hour, fill=(0, 255, 180), font=get_font(18, bold=True))

        # Bottom Calendar
        canvas.draw_card(20, 520, 984, 190, title="TARCZA KALENDARZOWA MÁNESA & ŚWIĘTA ASTRONOMICZNE", subtitle="Cykl pór roku i zmierzch astronomiczny")
        draw.text((45, 580), "Zmierzch cywilny: 16:15 | Zmierzch nautyczny: 17:02 | Zmierzch astronomiczny: 17:48", fill=(0, 255, 180), font=get_font(16, bold=True))
        draw.text((45, 620), "Przesilenie zimowe (Winter Solstice): 21 grudnia // Najkrótszy dzień w roku (07h 42m)", fill=(255, 200, 0), font=get_font(15))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Czas (Godzina/Dzień) | [A]: Animuj Koło Zodiaku | [X]: Zmień Współrzędne", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 069: mod_unicode.py - Inspektor Znaków Unicode & ASCII UTF-8
MODULES["mod_unicode"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class UnicodeInspectorModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.code_point = 0x2588
        self.char_name = "FULL BLOCK"
        self.category = "Block Elements (U+2580..U+259F)"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🔤 069 // UNICODE & UTF-8 CHARACTER INSPECTOR // U+{self.code_point:04X}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "UNICODE 15.1", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 80, 12, "3 BAJTY", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big Char Preview Box
        canvas.draw_card(20, 65, 400, 440, title="PODGLĄD GLYPHU (RENDER)", subtitle=f"Punkt kodowy U+{self.code_point:04X}")
        draw.rectangle([60, 130, 380, 370], fill=(16, 26, 42), outline=(0, 240, 255), width=2)
        draw.text((150, 180), "█", fill=(0, 255, 180), font=get_font(120, bold=True))
        draw.text((120, 420), f"ZNAK: '█' (KOD 0x{self.code_point:04X})", fill=(255, 200, 0), font=get_font(16, bold=True))

        # Encoding Details Card
        canvas.draw_card(440, 65, 564, 440, title="KODOWANIA CYFROWE I ENTYCJE", subtitle=self.char_name)
        details = [
            ("NAZWA OFICJALNA:", self.char_name),
            ("KATEGORIA UNICODE:", self.category),
            ("SEKWENCJA BAJTÓW UTF-8:", "0xE2 0x96 0x88 (Binarne: 11100010 10010110 10001000)"),
            ("KODOWANIE UTF-16:", "0x2588"),
            ("KODOWANIE UTF-32:", "0x00002588"),
            ("ENCJA HTML:", "&block;  lub  &#9608;"),
            ("ESCAPE C / PYTHON:", "\\\\u2588"),
        ]
        for i, (k, v) in enumerate(details):
            py = 125 + i * 46
            draw.text((460, py), k, fill=(140, 170, 200), font=get_font(12, bold=True))
            draw.text((460, py + 18), v, fill=(0, 255, 180) if "UTF" in k else (240, 245, 255), font=get_font(14))

        # Bottom Glyph Table Preview
        canvas.draw_card(20, 520, 984, 190, title="RAMKI PSEUDOGRAFICZNE CP437 & SYMBOLE TECHNICZNE", subtitle="Elementy interfejsów TUI / Cyberdeck")
        sample_chars = ["─", "│", "┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼", "▀", "▄", "█", "▌", "▐", "░", "▒", "▓", "■", "▲", "▼", "◄", "►"]
        for i, ch in enumerate(sample_chars):
            cx = 45 + i * 39
            draw.rectangle([cx, 580, cx + 32, 650], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((cx + 8, 600), ch, fill=(0, 255, 180), font=get_font(20, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Następny Znak | Góra/Dół: ±16 Znaków | [A]: Wprowadź Hex | [Y]: Kopiuj Kod", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "LEFT"):
            self.code_point = max(0, self.code_point - 1); return True
        elif event in ("KEY_RIGHT", "RIGHT"):
            self.code_point = min(0x10FFFF, self.code_point + 1); return True
        return False
'''

# 070: mod_battery_bench.py - Tester Żywotności Baterii & Profiler
MODULES["mod_battery_bench"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class BatteryBenchModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.voltage_mv = 3920
        self.capacity_mah = 2840 # out of 3000
        self.health = 94.6
        self.discharge_ma = 480
        self.eta_hours = 5.9
        self.temp_c = 34.2
        self.samples = [4180, 4120, 4060, 4010, 3960, 3920]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 136, 100), width=1)
        draw.text((20, 14), "🔋 070 // BATTERY BENCHMARK & HARDWARE DISCHARGE PROFILER", fill=(0, 255, 136), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "OGNIWO LI-PO 3000 MAH", bg_color=(20, 45, 30))
        canvas.draw_badge(w - 85, 12, f"{self.health:.1f}%", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Battery Health Card
        canvas.draw_card(20, 65, 480, 440, title="KONDYCJA AKUMULATORA (SOH)", subtitle="Pomiar napięcia i szacowana degradacja chemiczna")
        draw.text((50, 135), f"{self.health:.1f}%", fill=(0, 255, 136), font=get_font(74, bold=True))
        draw.text((50, 240), f"Pojemność rzeczywista: {self.capacity_mah} / 3000 mAh", fill=(240, 245, 255), font=get_font(16, bold=True))
        draw.text((50, 280), f"Napięcie ogniwa: {self.voltage_mv} mV (3.92 V)", fill=(0, 200, 255), font=get_font(16))
        draw.text((50, 315), f"Pobór prądu: {self.discharge_ma} mA (Moc: 1.88 W)", fill=(255, 180, 0), font=get_font(16))
        draw.text((50, 350), f"Temperatura baterii: {self.temp_c}°C (W normie)", fill=(0, 255, 180), font=get_font(16))
        draw.text((50, 400), f"Szacowany czas pracy: {self.eta_hours:.1f} godzin", fill=(0, 255, 136), font=get_font(20, bold=True))

        # Discharge Curve Chart
        canvas.draw_card(520, 65, 484, 440, title="KRZYWA ROZŁADOWANIA (DISCHARGE mV)", subtitle="Rejestracja napięcia w funkcji czasu (Krok 30 min)")
        draw.rectangle([545, 125, 975, 470], fill=(14, 20, 30), outline=(0, 180, 220))
        for i in range(len(self.samples) - 1):
            x1 = 570 + i * 75
            x2 = 570 + (i + 1) * 75
            y1 = 440 - int((self.samples[i] - 3400) * 0.4)
            y2 = 440 - int((self.samples[i + 1] - 3400) * 0.4)
            draw.line([(x1, y1), (x2, y2)], fill=(0, 255, 180), width=3)
            draw.ellipse([(x1 - 4, y1 - 4), (x1 + 4, y1 + 4)], fill=(255, 200, 0))
        draw.text((560, 135), "4.20V (100%)", fill=(120, 150, 180), font=get_font(12))
        draw.text((560, 445), "3.40V (KRYTYCZNE)", fill=(255, 80, 80), font=get_font(12))

        # Bottom Stress Test Modes
        canvas.draw_card(20, 520, 984, 190, title="PROFILE OBCIĄŻENIOWE KONSOLI (STRESS BENCHMARK)", subtitle="Testowanie poboru energii w różnych stanach pracy")
        draw.text((45, 580), "• IDLE (Ekran 30%, CPU 400 MHz): 180 mA (~16h)  |  • RETRO GAMING (CPU 1.2 GHz): 450 mA (~6.5h)", fill=(220, 235, 255), font=get_font(15))
        draw.text((45, 620), "• MAX STRESS (4 rdzenie 1.8 GHz, Wi-Fi, Ekran 100%): 820 mA (~3.6h)", fill=(255, 170, 0), font=get_font(15, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Profil Testowy | [A]: Uruchom Test Rozładowania | [Y]: Eksport Wykresu do CSV", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 071: mod_binaural.py - Generator Dźwięków Binaural Beats & Szumów
MODULES["mod_binaural"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class BinauralModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.preset = "GŁĘBOKIE SKUPIENIE (ALPHA 10 HZ)"
        self.base_freq = 210.0 # Left ear Hz
        self.beat_freq = 10.0  # Right ear = 220 Hz
        self.noise_type = "SZUM RÓŻOWY (PINK NOISE)"
        self.playing = True

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🎧 071 // BINAURAL BEATS NEURO-SYNTH // DUDNIENIA RÓŻNICOWE", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "SŁUCHAWKI STEREO", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 90, 12, "ALPHA 10 HZ", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big Frequency Visualizer Card
        canvas.draw_card(20, 65, 600, 440, title="PARAMETRY TONÓW BINAURALNYCH", subtitle="Wymagane podłączenie słuchawek stereo przez gniazdo jack 3.5mm")
        draw.text((50, 135), self.preset, fill=(0, 255, 180), font=get_font(22, bold=True))
        draw.text((50, 190), f"Lewy kanał:  {self.base_freq:.1f} Hz (Fala nośna)", fill=(0, 200, 255), font=get_font(18))
        draw.text((50, 230), f"Prawy kanał: {self.base_freq + self.beat_freq:.1f} Hz (Fala nośna + dudnienie)", fill=(0, 200, 255), font=get_font(18))
        draw.rectangle([50, 280, 560, 370], fill=(14, 22, 34), outline=(0, 255, 180), width=2)
        draw.text((70, 300), f"Częstotliwość fali mózgowej: {self.beat_freq:.1f} Hz (Fale Alpha)", fill=(255, 200, 0), font=get_font(20, bold=True))
        draw.text((70, 335), "Stan umysłu: Relaksacja, kreatywność, szybkie przyswajanie wiedzy.", fill=(180, 205, 235), font=get_font(14))

        # Noise Generator Card
        canvas.draw_card(640, 65, 364, 440, title="GENERATOR TŁA DŹWIĘKOWEGO", subtitle="Maskowanie hałasów zewnętrznych")
        noises = [
            ("Szum Różowy (Pink)", "1/f spadek mocy", True),
            ("Szum Brązowy (Brown)", "Głęboki bas / wodospad", False),
            ("Szum Biały (White)", "Pełne spektrum pasma", False),
            ("Dźwięk Deszczu", "Akustyczny relaks", False),
        ]
        for i, (n_name, n_desc, is_act) in enumerate(noises):
            ny = 135 + i * 75
            draw.rectangle([660, ny, 980, ny + 65], fill=(16, 26, 42) if is_act else (12, 16, 26), outline=(0, 255, 180) if is_act else (40, 60, 85))
            draw.text((675, ny + 12), n_name, fill=(0, 255, 180) if is_act else (200, 220, 245), font=get_font(14, bold=True))
            draw.text((675, ny + 35), n_desc, fill=(120, 150, 180), font=get_font(12))

        # Bottom Presets
        canvas.draw_card(20, 520, 984, 190, title="ZAKRESY CZĘSTOTLIWOŚCI BIOELEKTRYCZNYCH MÓZGU (EEG)", subtitle="Wybierz pożądany stan neurobiologiczny")
        draw.text((45, 580), "• DELTA (0.5-4 Hz): Głęboki sen  |  • THETA (4-8 Hz): Medytacja i pamięć  |  • ALPHA (8-13 Hz): Skupienie", fill=(220, 235, 255), font=get_font(15))
        draw.text((45, 615), "• BETA (13-30 Hz): Czujność i analiza  |  • GAMMA (30-50 Hz): Szczytowa percepcja poznawcza", fill=(255, 200, 0), font=get_font(15, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmiana Zakresu Fal | [A]: Start / Stop Dźwięku | [Y]: Typ Szumu Tła", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 072: mod_brain.py - Trening Pamięci i Refleksu Cyber-Simon
MODULES["mod_brain"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class CyberBrainModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.score = 7
        self.high_score = 14
        self.reaction_time_ms = 214
        self.state = "TWÓJ RUCH // ODTWÓRZ SEKWENCJĘ PRZYCISKÓW"
        self.sequence = ["A", "X", "B", "Y", "A", "A", "B"]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 12, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), "🧠 072 // CYBER-SIMON BRAIN TRAINER & REACTION TEST", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"SERIA: {self.score}", bg_color=(20, 50, 40))
        canvas.draw_badge(w - 80, 12, f"{self.reaction_time_ms} MS", bg_color=(40, 30, 15), text_color=(255, 200, 0))

        # 4 Big Buttons in Diamond Layout (ABXY)
        canvas.draw_card(20, 65, 540, 440, title="POLE REAKCJI PRZYCISKÓW ABXY", subtitle="Zapamiętaj sekwencję błysków i dźwięków")
        draw.text((100, 130), self.state, fill=(0, 255, 180), font=get_font(14, bold=True))

        # Diamond buttons
        bx, by = 280, 280
        # X (North)
        draw.ellipse([(bx - 40, by - 120), (bx + 40, by - 40)], fill=(0, 140, 255), outline=(0, 240, 255), width=3)
        draw.text((bx - 10, by - 92), "X", fill=(255, 255, 255), font=get_font(26, bold=True))
        # Y (West)
        draw.ellipse([(bx - 120, by - 40), (bx - 40, by + 40)], fill=(0, 180, 100), outline=(0, 255, 140), width=3)
        draw.text((bx - 90, by - 12), "Y", fill=(255, 255, 255), font=get_font(26, bold=True))
        # A (East)
        draw.ellipse([(bx + 40, by - 40), (bx + 120, by + 40)], fill=(200, 0, 80), outline=(255, 0, 120), width=3)
        draw.text((bx + 70, by - 12), "A", fill=(255, 255, 255), font=get_font(26, bold=True))
        # B (South)
        draw.ellipse([(bx - 40, by + 40), (bx + 40, by + 120)], fill=(220, 160, 0), outline=(255, 220, 0), width=3)
        draw.text((bx - 10, by + 68), "B", fill=(255, 255, 255), font=get_font(26, bold=True))

        # Stats Card
        canvas.draw_card(580, 65, 424, 440, title="WYNIKI I REKORDY TRENINGU", subtitle="Pomiary neuro-kognitywne")
        draw.text((610, 140), f"AKTUALNA RUNDA: {self.score}", fill=(0, 255, 180), font=get_font(24, bold=True))
        draw.text((610, 190), f"REKORD SESJI:   {self.high_score}", fill=(255, 200, 0), font=get_font(24, bold=True))
        draw.text((610, 250), f"CZAS REAKCJI:   {self.reaction_time_ms} ms", fill=(0, 240, 255), font=get_font(22, bold=True))
        draw.text((610, 310), "Ocena refleksu: BARDZO SZYBKI (TOP 5%)", fill=(0, 255, 136), font=get_font(15, bold=True))
        draw.text((610, 345), "Średnia dla populacji: 260 - 300 ms.", fill=(160, 180, 210), font=get_font(14))

        # Bottom Instructions
        canvas.draw_card(20, 520, 984, 190, title="ZASADY TRENINGU MÓZGU", subtitle="Trening pamięci roboczej i refleksu ruchowego")
        draw.text((45, 580), "Konsola generuje rosnący ciąg sygnałów świetlnych i dźwiękowych. Każdy błąd resetuje rundę.", fill=(220, 235, 255), font=get_font(15))
        draw.text((45, 615), "Naciśnij [A], [B], [X] lub [Y] zgodnie z kolejnością pokazywaną przez system.", fill=(0, 255, 180), font=get_font(15, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "Klawisze ABXY: Wprowadź Kolor | [START]: Rozpocznij Nową Grę | [SELECT]: Tryb Tylko Refleks", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 073: mod_units.py - Wielki Przelicznik Jednostek Inżynieryjnych
MODULES["mod_units"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class UnitsConverterModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.input_val = 100.0
        self.category = "CIŚNIENIE (PRESSURE)"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🧮 073 // ENGINEERING UNITS CONVERTER // {self.category}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "PRECYZJA 64-BIT", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 85, 12, "SI / IMP", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big Value Card
        canvas.draw_card(20, 65, 450, 440, title="WARTOŚĆ WEJŚCIOWA (BAZOWA)", subtitle="100.00 PSI (Funty na cal kwadratowy)")
        draw.text((60, 160), "100.00", fill=(0, 255, 180), font=get_font(72, bold=True))
        draw.text((310, 200), "PSI", fill=(255, 200, 0), font=get_font(28, bold=True))
        draw.text((60, 280), "Odpowiednik ciśnienia opon samochodowych:", fill=(160, 185, 215), font=get_font(14))
        draw.text((60, 310), "Ok. 6.89 bara (Typowe ciśnienie w kolarzówkach)", fill=(0, 255, 136), font=get_font(15, bold=True))

        # Converted Grid Card
        canvas.draw_card(490, 65, 514, 440, title="PRZELICZENIE NA JEDNOSTKI UKŁADU SI I SPECJALNE", subtitle="Wszystkie odpowiedniki ciśnienia jednocześnie")
        conv = [
            ("BAR (bar):", "6.8947 bar", (0, 240, 255)),
            ("KILOPASKAL (kPa):", "689.475 kPa", (0, 240, 255)),
            ("MEGAPASKAL (MPa):", "0.6895 MPa", (0, 240, 255)),
            ("ATMOSFERA FIZYCZNA (atm):", "6.8046 atm", (240, 245, 255)),
            ("MILIMETRY SŁUPA RTĘCI (mmHg):", "5171.49 mmHg", (240, 245, 255)),
            ("KILOGRAM-SIŁA / CM² (at):", "7.0307 kgf/cm²", (240, 245, 255)),
        ]
        for i, (u_name, u_val, col) in enumerate(conv):
            cy = 135 + i * 58
            draw.text((510, cy), u_name, fill=(140, 170, 200), font=get_font(13))
            draw.text((510, cy + 20), u_val, fill=col, font=get_font(18, bold=True))

        # Bottom Categories
        canvas.draw_card(20, 520, 984, 190, title="KATEGORIE JEDNOSTEK INŻYNIERYJNYCH", subtitle="Wybierz kategorię konwersji D-Padem")
        cats = ["Ciśnienie", "Moment obrotowy (Nm/ft-lb)", "Moc (W/KM/HP)", "Energia (J/kWh/cal)", "Prędkość (km/h / kt / mph)", "Temperatura (°C/°F/K)"]
        for i, c_name in enumerate(cats):
            cx = 40 + (i % 3) * 320
            cy = 575 + (i // 3) * 55
            is_sel = (i == 0)
            draw.rectangle([cx, cy, cx + 300, cy + 45], fill=(24, 40, 65) if is_sel else (14, 20, 32), outline=(0, 240, 255) if is_sel else (35, 50, 70))
            draw.text((cx + 15, cy + 12), c_name, fill=(0, 255, 180) if is_sel else (180, 200, 230), font=get_font(13, bold=is_sel))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmień Kategorię / Wartość | [A]: Edytuj Liczbę | [X]: Odwróć Kierunek Konwersji", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 074: mod_hasher.py - Multi-Hasher & Generator Haszy w Locie
MODULES["mod_hasher"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class MultiHasherModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.input_text = "BrickDeckOS_CyberDeck_2026"
        self.hashes = [
            ("MD5 (128-bit):", "e4d909c290d0fb1ca068ffaddf22cbd0"),
            ("SHA-1 (160-bit):", "2aae6c35c94fcfb415dbe95f408b9ce91ee846ed"),
            ("SHA-256 (256-bit):", "a8f5f167f44f4964e6c998dee827110c...9a7e"),
            ("CRC32 (Suma Kontrolna):", "0x89D2F4A1"),
            ("BASE64 (Zakodowane):", "QnJpY2tEZWNrT1NfQ3liZXJEZWNrXzIwMjY="),
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), "🔐 074 // MULTI-HASHER & CRYPTOGRAPHIC CHECKSUM GENERATOR", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "HASZOWANIE W LOCIE", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 80, 12, "OPENSSL", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Input Text Box Card
        canvas.draw_card(20, 65, 984, 150, title="TEKST WEJŚCIOWY DO SKRÓTU", subtitle="Wpisz dowolne słowo lub hasło")
        draw.rectangle([45, 120, 980, 185], fill=(16, 24, 38), outline=(0, 240, 255), width=2)
        draw.text((65, 138), f"> {self.input_text}", fill=(255, 220, 0), font=get_font(22, bold=True))

        # Hashes Table Card
        canvas.draw_card(20, 235, 984, 475, title="WYGENEROWANE SUMY KONTROLNE I SKRÓTY KRYPTOGRAFICZNE", subtitle="Wszystkie algorytmy liczone równolegle w pamięci RAM")
        for i, (algo, val) in enumerate(self.hashes):
            hy = 300 + i * 78
            draw.rectangle([40, hy, 980, hy + 66], fill=(14, 20, 30), outline=(0, 200, 255))
            draw.text((55, hy + 10), algo, fill=(0, 240, 255), font=get_font(13, bold=True))
            draw.text((55, hy + 32), val, fill=(0, 255, 180), font=get_font(17, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Zmień Tekst Wejściowy | [A]: Haszuj Plik z Karty SD | [Y]: Kopiuj Hasz do Schowka", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 075: mod_pixel.py - Pixel Art Studio & Sprite Painter
MODULES["mod_pixel"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class PixelArtModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.grid_sz = 16
        self.cursor_x = 8
        self.cursor_y = 8
        self.palette = [
            (0, 0, 0), (255, 255, 255), (0, 240, 255), (0, 255, 136),
            (255, 200, 0), (255, 60, 60), (180, 80, 255), (100, 120, 150)
        ]
        self.selected_color = 2
        self.pixels = [[0 for _ in range(16)] for _ in range(16)]
        # Draw mock heart/icon
        for x, y in [(5,5), (6,4), (7,4), (8,5), (9,4), (10,4), (11,5), (6,6), (7,7), (8,8), (9,7), (10,6)]:
            self.pixels[y][x] = 5

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🎨 075 // PIXEL ART STUDIO & SPRITE PAINTER (16x16)", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "SIATKA 16x16 PIKSELI", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "8 BARW", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main 16x16 Canvas Area
        canvas.draw_card(20, 65, 600, 640, title="OBSZAR RYSOWANIA SPRITE'A", subtitle="Ruch kursorem D-Padem, malowanie klawiszem [A]")
        cx, cy, sz = 80, 140, 30
        for y in range(16):
            for x in range(16):
                col = self.palette[self.pixels[y][x]]
                draw.rectangle([cx + x * sz, cy + y * sz, cx + (x + 1) * sz - 1, cy + (y + 1) * sz - 1], fill=col)
        # Cursor marker
        draw.rectangle([cx + self.cursor_x * sz, cy + self.cursor_y * sz, cx + (self.cursor_x + 1) * sz, cy + (self.cursor_y + 1) * sz], outline=(255, 255, 0), width=3)

        # Right Palette & Tools Card
        canvas.draw_card(640, 65, 364, 640, title="PALETA BARW I EKSPORT", subtitle="Wybór koloru pędzla pod [X]")
        draw.text((665, 130), "AKTYWNA PALETA CYBERPUNK:", fill=(140, 170, 200), font=get_font(13))
        for i, col in enumerate(self.palette):
            px = 665 + (i % 4) * 75
            py = 160 + (i // 4) * 75
            is_sel = (i == self.selected_color)
            draw.rectangle([px, py, px + 60, py + 60], fill=col, outline=(255, 255, 0) if is_sel else (40, 60, 85), width=3 if is_sel else 1)

        draw.text((665, 340), "FORMATY ZAPISU NA KARTĘ SD:", fill=(140, 170, 200), font=get_font(13))
        draw.text((665, 370), "• Plik obrazu PNG (16x16 lub skalowany)", fill=(240, 245, 255), font=get_font(14))
        draw.text((665, 400), "• Tablica bajtów w C (const uint16_t sprite[])", fill=(240, 245, 255), font=get_font(14))
        draw.text((665, 430), "• Tablica pikseli w Pythonie (.py)", fill=(240, 245, 255), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Ruch Pędzlem | [A]: Postaw Piksel | [B]: Gumka | [X]: Zmień Kolor | [Y]: Eksport PNG", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "LEFT"):
            self.cursor_x = max(0, self.cursor_x - 1); return True
        elif event in ("KEY_RIGHT", "RIGHT"):
            self.cursor_x = min(15, self.cursor_x + 1); return True
        elif event in ("KEY_UP", "UP"):
            self.cursor_y = max(0, self.cursor_y - 1); return True
        elif event in ("KEY_DOWN", "DOWN"):
            self.cursor_y = min(15, self.cursor_y + 1); return True
        elif event in ("KEY_A", "a"):
            self.pixels[self.cursor_y][self.cursor_x] = self.selected_color; return True
        return False
'''

# 076: mod_sniffer.py - Wi-Fi Packet Sniffer & DNS Inspector
MODULES["mod_sniffer"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class SnifferModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.packets_total = 1420
        self.kbps = 48.5
        self.dns_queries = [
            ("api.github.com", "A (IPv4)", "140.82.121.4", "OK"),
            ("pool.ntp.org", "UDP 123", "Czas sieciowy NTP", "OK"),
            ("google.com", "A (IPv4)", "142.250.203.206", "OK"),
            ("homeassistant.local", "mDNS 5353", "192.168.1.100", "LOKALNE"),
            ("telemetry.vendor.com", "HTTPS 443", "ZABLOKOWANO (PI-HOLE)", "BLOK"),
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "📡 076 // WI-FI PACKET SNIFFER & DNS QUERY INSPECTOR // INTERFEJS: WL0", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 240, 12, f"{self.packets_total} PAKIETÓW", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 90, 12, f"{self.kbps} KB/S", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Protocol Breakdown Card
        canvas.draw_card(20, 65, 984, 200, title="ROZKŁAD PROTOKOŁÓW SIECIOWYCH (PROMISCUOUS / LOCAL)", subtitle="Analiza nagłówków Ethernet / IP w czasie rzeczywistym")
        proto = [("TCP / TLS", 68, (0, 240, 255)), ("UDP", 22, (0, 255, 180)), ("DNS", 6, (255, 200, 0)), ("ICMP / ARP", 4, (255, 100, 100))]
        bx = 45
        for name, pct, col in proto:
            pw = int(914 * (pct / 100.0))
            draw.rectangle([bx, 125, bx + pw, 165], fill=col)
            draw.text((bx + 10, 175), f"{name}: {pct}%", fill=col, font=get_font(14, bold=True))
            bx += pw

        # DNS Query Table Card
        canvas.draw_card(20, 280, 984, 425, title="REJESTR ZAPYTAŃ DOMENOWYCH DNS & MDNS (PORT 53 / 5353)", subtitle="Ostatnio odpytywane serwery i adresy docelowe")
        for i, (domain, qtype, dest, status) in enumerate(self.dns_queries):
            dy = 345 + i * 68
            draw.rectangle([40, dy, 980, dy + 58], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((60, dy + 18), domain, fill=(240, 245, 255), font=get_font(15, bold=True))
            draw.text((420, dy + 20), qtype, fill=(140, 170, 200), font=get_font(13))
            draw.text((620, dy + 20), dest, fill=(0, 240, 255), font=get_font(14))
            stat_col = (255, 70, 70) if "BLOK" in status else (0, 255, 136)
            draw.text((860, dy + 18), status, fill=stat_col, font=get_font(14, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Listę Pakietów | [A]: Filtruj wg IP / Portu | [B]: Wyczyść Bufor | [Y]: Zapisz PCAP", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "store", "modules")
os.makedirs(output_dir, exist_ok=True)

for name, code in MODULES.items():
    path = os.path.join(output_dir, f"{name}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[+] Zapisano: {name}.py")

print(f"Batch 5 completed! Generated {len(MODULES)} modules.")
