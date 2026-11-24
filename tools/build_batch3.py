#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/build_batch3.py - Builds modules 046 to 056 into store/modules/
"""

import os
import sys

MODULES = {}

# 046: mod_ai.py - Pocket AI Terminal & Ollama Gateway
MODULES["mod_ai"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AiTerminalModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.models = ["llama3:8b-q4", "mistral:7b", "gemma:2b", "phi-3:mini"]
        self.selected_model = 0
        self.status = "CONNECTED // LOCAL OLLAMA"
        self.latency_ms = 42
        self.chat_history = [
            ("USER", "Zoptymalizuj pętlę renderowania na ekranie 1024x768 ARM64:"),
            ("AI", "Użyj podwójnego buforowania (Double Buffering) w pamięci DMA oraz unikaj ponownego alokowania tablic RGBA w każdej klatce 60 FPS."),
            ("USER", "Jaki jest pobór mocy procesora Allwinner A133P w trybie uśpienia?"),
            ("AI", "W trybie deep-sleep przy wyłączonym podświetleniu ekranu pobór prądu spada do ok. 15-20 mA, co daje ponad 120 godzin czuwania.")
        ]
        self.prompt_text = "Prompt: > Analiza telemetrii sieciowej..."
        self.cursor_blink = 0

    def update(self, dt: float):
        self.cursor_blink = (self.cursor_blink + 1) % 60

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        # Header
        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🤖 046 // POCKET AI TERMINAL & OLLAMA GATEWAY", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 290, 12, f"MODEL: {self.models[self.selected_model]}", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 110, 12, f"{self.latency_ms} ms", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Left Panel: Status & Model selector
        canvas.draw_card(20, 65, 300, 640, title="PARAMETRY AI & HOST", subtitle="Ollama / vLLM / Gemini Gateway")
        draw.text((36, 130), f"Status: {self.status}", fill=(0, 255, 136), font=get_font(14, bold=True))
        draw.text((36, 160), "Host: http://192.168.1.150:11434", fill=(160, 180, 210), font=get_font(13))
        draw.text((36, 190), "Temp: 0.7 | Top-P: 0.9 | Ctx: 4096", fill=(160, 180, 210), font=get_font(13))
        draw.text((36, 225), "DOSTĘPNE MODELE:", fill=(255, 170, 0), font=get_font(14, bold=True))
        for i, m in enumerate(self.models):
            bg = (30, 50, 75) if i == self.selected_model else (16, 24, 36)
            col = (0, 240, 255) if i == self.selected_model else (140, 160, 190)
            draw.rectangle([36, 255 + i * 40, 300, 285 + i * 40], fill=bg, outline=(0, 200, 255) if i == self.selected_model else (40, 60, 85))
            draw.text((46, 262 + i * 40), f"{i+1}. {m}", fill=col, font=get_font(13, bold=(i == self.selected_model)))

        # Chat Terminal Area
        canvas.draw_card(335, 65, 669, 560, title="KONSOLA DIALOGOWA CYBER-AI", subtitle="Strumieniowanie odpowiedzi w czasie rzeczywistym")
        cy = 130
        for sender, msg in self.chat_history:
            is_user = (sender == "USER")
            tag_col = (255, 170, 0) if is_user else (0, 240, 255)
            draw.text((355, cy), f"[{sender}]:", fill=tag_col, font=get_font(13, bold=True))
            # Wrap message
            words = msg.split()
            line = ""
            for word in words:
                if len(line) + len(word) > 65:
                    draw.text((355, cy + 20), line, fill=(230, 240, 255) if not is_user else (200, 220, 240), font=get_font(14))
                    cy += 22
                    line = word + " "
                else:
                    line += word + " "
            if line:
                draw.text((355, cy + 20), line, fill=(230, 240, 255) if not is_user else (200, 220, 240), font=get_font(14))
                cy += 24
            cy += 16

        # Prompt input bar
        draw.rectangle([335, 640, 1004, 700], fill=(14, 20, 32, 255), outline=(0, 240, 255), width=2)
        cursor = "_" if self.cursor_blink < 30 else ""
        draw.text((350, 655), f"{self.prompt_text}{cursor}", fill=(0, 255, 180), font=get_font(15, bold=True))

        # Footer
        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Góra/Dół: Zmiana Modelu | [A]: Wyślij Zapytanie | [B]: Wyczyść Czat | [X]: Zmień Host", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_UP", "UP"):
            self.selected_model = (self.selected_model - 1) % len(self.models)
            return True
        elif event in ("KEY_DOWN", "DOWN"):
            self.selected_model = (self.selected_model + 1) % len(self.models)
            return True
        return False
'''

# 047: mod_morse_trainer.py - Morse Code Audio Trainer & Koch Method
MODULES["mod_morse_trainer"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class MorseTrainerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.wpm = 20
        self.freq_hz = 700
        self.current_char = "K"
        self.morse_code = "-.-"
        self.koch_lesson = 5
        self.score = 92
        self.history = ["K  -.-  OK", "M  --   OK", "R  .-.  OK", "S  ...  OK", "U  ..-  BŁĄD"]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(255, 170, 0, 100), width=1)
        draw.text((20, 14), "📻 047 // MORSE CODE AUDIO TRAINER (METODA KOCHA)", fill=(255, 170, 0), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"TEMPO: {self.wpm} WPM", bg_color=(40, 30, 10), text_color=(255, 200, 0))
        canvas.draw_badge(w - 90, 12, f"{self.score}%", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big Training Display
        canvas.draw_card(20, 65, 600, 450, title="BIEŻĄCY ZNAK TELEGRAFICZNY", subtitle="Metoda Kocha // Słuchaj tonu i wciśnij klawisz")
        draw.text((230, 160), self.current_char, fill=(0, 240, 255), font=get_font(90, bold=True))
        draw.text((215, 280), f"KOD:  {self.morse_code}", fill=(255, 220, 0), font=get_font(36, bold=True))
        draw.text((160, 360), f"Dźwięk: {self.freq_hz} Hz // Ton sinusoidalny", fill=(140, 170, 205), font=get_font(15))
        draw.rectangle([60, 410, 560, 435], fill=(20, 30, 45), outline=(0, 200, 255))
        draw.rectangle([60, 410, 60 + int(500 * (self.score / 100.0)), 435], fill=(0, 255, 136))
        draw.text((75, 415), f"Skuteczność lekcji {self.koch_lesson}: {self.score}% (Wymagane >90% do awansu)", fill=(10, 20, 30), font=get_font(12, bold=True))

        # Right History Card
        canvas.draw_card(640, 65, 364, 450, title="HISTORIA ODBIORU", subtitle="Ostatnie zdekodowane symbole")
        for i, h_item in enumerate(self.history):
            col = (0, 255, 136) if "OK" in h_item else (255, 80, 80)
            draw.text((660, 130 + i * 45), f"#{i+1}: {h_item}", fill=col, font=get_font(18, bold=True))

        # Bottom Audio Keyer Mode
        canvas.draw_card(20, 530, 984, 180, title="TRYB KLUCZA SZTORCOWEGO & PROSTOTY (MANUAL CW)", subtitle="Naciśnij [A] aby nadać sygnał na głośnikach konsoli")
        draw.text((40, 595), "STAN KLUCZA: [ZWOLNIONY] // OCZEKIWANIE NA IMPULS", fill=(0, 255, 200), font=get_font(16, bold=True))
        draw.text((40, 630), "Alfabet: A (.-) B (-...) C (-.-.) D (-..) E (.) F (..-.) G (--.) H (....) I (..) J (.---) K (-.-)", fill=(140, 160, 190), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Tempo WPM | [A]: Odtwórz Znak / Kluczuj | [Y]: Kolejna Lekcja Kocha", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "LEFT"):
            self.wpm = max(5, self.wpm - 1); return True
        elif event in ("KEY_RIGHT", "RIGHT"):
            self.wpm = min(40, self.wpm + 1); return True
        return False
'''

# 048: mod_air_quality.py - Global Air Quality & Smog Radar AQI
MODULES["mod_air_quality"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AirQualityModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.city = "Gorzów Wielkopolski"
        self.aqi = 28
        self.status = "DOBRA (GOOD)"
        self.pm25 = 7.4
        self.pm10 = 14.2
        self.o3 = 45.1
        self.no2 = 12.8
        self.so2 = 3.1
        self.history = [35, 32, 28, 25, 22, 24, 28, 30, 28]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 16, 24, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 22, 34, 255), outline=(0, 255, 136, 100), width=1)
        draw.text((20, 14), f"🌱 048 // GLOBAL AIR QUALITY & SMOG RADAR // {self.city.upper()}", fill=(0, 255, 136), font=get_font(18, bold=True))
        canvas.draw_badge(w - 200, 12, "GIOŚ / OPENAQ", bg_color=(20, 45, 35))
        canvas.draw_badge(w - 75, 12, "LIVE", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main Index Card
        canvas.draw_card(20, 65, 400, 440, title="INDEKS JAKOŚCI POWIETRZA (AQI)", subtitle="Europejski Indeks Czystości Powietrza")
        draw.text((120, 140), str(self.aqi), fill=(0, 255, 136), font=get_font(84, bold=True))
        draw.text((90, 250), self.status, fill=(0, 255, 180), font=get_font(22, bold=True))
        draw.text((45, 310), "Zanieczyszczenie pyłowe w normie.", fill=(160, 185, 215), font=get_font(15))
        draw.text((45, 340), "Zalecana aktywność na świeżym powietrzu.", fill=(160, 185, 215), font=get_font(15))
        draw.rectangle([45, 410, 375, 430], fill=(20, 30, 45))
        draw.rectangle([45, 410, 45 + int(330 * (self.aqi / 100.0)), 430], fill=(0, 255, 136))

        # Pollutant Detailed Grid
        canvas.draw_card(440, 65, 564, 440, title="STĘŻENIA PYŁÓW I GAZÓW (µg/m³)", subtitle="Czujniki laserowe i stacje referencyjne")
        params = [
            ("PYŁ ZAWIESZONY PM2.5", f"{self.pm25} µg/m³", "Norma: 25 µg/m³ (29%)", (0, 255, 136)),
            ("PYŁ ZAWIESZONY PM10", f"{self.pm10} µg/m³", "Norma: 50 µg/m³ (28%)", (0, 255, 136)),
            ("OZON TROPOSFERYCZNY O3", f"{self.o3} µg/m³", "Norma: 120 µg/m³ (37%)", (0, 200, 255)),
            ("DWUTLENEK AZOTU NO2", f"{self.no2} µg/m³", "Norma: 200 µg/m³ (6%)", (0, 255, 136)),
            ("DWUTLENEK SIARKI SO2", f"{self.so2} µg/m³", "Norma: 125 µg/m³ (2%)", (0, 255, 136)),
        ]
        for i, (title, val, norm, col) in enumerate(params):
            py = 125 + i * 65
            draw.text((460, py), title, fill=(150, 175, 205), font=get_font(13))
            draw.text((460, py + 18), val, fill=col, font=get_font(20, bold=True))
            draw.text((700, py + 20), norm, fill=(130, 150, 180), font=get_font(12))

        # Bottom 24h Trend Chart
        canvas.draw_card(20, 520, 984, 190, title="HISTOGRAM 24-GODZINNY JAKOŚCI POWIETRZA", subtitle="Trend dobowy PM2.5 / PM10")
        bw = 90
        for i, v in enumerate(self.history):
            bx = 60 + i * 102
            bh = int(v * 2.2)
            draw.rectangle([bx, 670 - bh, bx + bw, 670], fill=(0, 200, 140))
            draw.text((bx + 15, 675), f"-{len(self.history)-1-i}h", fill=(120, 140, 170), font=get_font(12))
            draw.text((bx + 18, 645 - bh), str(v), fill=(220, 240, 255), font=get_font(12, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Góra/Dół: Zmień Miasto | [A]: Wymuś Odświeżenie Stacji | [X]: Zmień Jednostki (US/EU)", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 049: mod_worldclock.py - World Clock & Solar Terminator
MODULES["mod_worldclock"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class WorldClockModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.cities = [
            ("WARSZAWA (CET)", "17:25", "UTC+1", True),
            ("LONDYN (GMT)", "16:25", "UTC+0", True),
            ("NOWY JORK (EST)", "11:25", "UTC-5", True),
            ("SAN FRANCISCO (PST)", "08:25", "UTC-8", True),
            ("TOKIO (JST)", "01:25", "UTC+9", False),
            ("SYDNEY (AEST)", "03:25", "UTC+11", False),
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🌐 049 // WORLD CLOCK & SOLAR TERMINATOR (KRZYWA SŁONECZNA)", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 180, 12, "TERMINATOR: ON", bg_color=(20, 40, 60))

        # World Map with Day/Night simulation
        canvas.draw_card(20, 65, 984, 380, title="GLOBALNA MAPA DZIENNA / NOCNA", subtitle="Krzywa Solar Terminator wyliczana z bieżącej deklinacji Słońca")
        mx, my, mw, mh = 40, 115, 944, 310
        draw.rectangle([mx, my, mx + mw, my + mh], fill=(12, 25, 45), outline=(0, 180, 240))
        # Draw continents outline mock & solar night curve
        for x in range(0, mw, 8):
            rad = (x / mw) * 2 * math.pi
            night_y = my + mh / 2 + math.sin(rad) * 90
            draw.rectangle([mx + x, int(night_y), mx + x + 8, my + mh], fill=(6, 12, 22))
        draw.text((mx + 20, my + 20), "DZIEŃ [SŁOŃCE]", fill=(255, 220, 0), font=get_font(13, bold=True))
        draw.text((mx + mw - 140, my + mh - 30), "NOC [CIEŃ ZIEMI]", fill=(100, 130, 170), font=get_font(13))

        # City Clocks Grid
        canvas.draw_card(20, 460, 984, 250, title="STREFY CZASOWE I SESJE GIEŁDOWE", subtitle="Czas lokalny na świecie")
        for i, (name, clock, utc, is_day) in enumerate(self.cities):
            col = i % 3
            row = i // 3
            cx = 40 + col * 320
            cy = 515 + row * 95
            draw.rectangle([cx, cy, cx + 300, cy + 80], fill=(18, 26, 40), outline=(0, 200, 255) if is_day else (40, 60, 85))
            draw.text((cx + 14, cy + 12), name, fill=(220, 235, 255), font=get_font(13, bold=True))
            draw.text((cx + 14, cy + 34), clock, fill=(255, 220, 0) if is_day else (140, 170, 210), font=get_font(26, bold=True))
            draw.text((cx + 180, cy + 42), utc, fill=(100, 130, 160), font=get_font(13))
            icon = "☀️ DZIEŃ" if is_day else "🌙 NOC"
            draw.text((cx + 225, cy + 14), icon, fill=(255, 170, 0) if is_day else (100, 140, 200), font=get_font(11, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Strefy | [A]: Dodaj Miasto | [X]: Format 12h/24h", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 050: mod_ticker.py - Crypto & Currency Ticker BTC/ETH/SOL/NBP
MODULES["mod_ticker"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TickerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.crypto = [
            ("BITCOIN (BTC)", "$96,420", "+3.4%", True),
            ("ETHEREUM (ETH)", "$3,480", "+1.8%", True),
            ("SOLANA (SOL)", "$215", "-0.7%", False),
        ]
        self.fx = [
            ("USD / PLN (NBP)", "4.08 PLN", "+0.1%"),
            ("EUR / PLN (NBP)", "4.31 PLN", "-0.2%"),
            ("CHF / PLN (NBP)", "4.59 PLN", "+0.4%"),
        ]
        self.candles = [100, 105, 103, 110, 118, 115, 122, 120, 128, 135, 132, 140]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(255, 170, 0, 100), width=1)
        draw.text((20, 14), "📈 050 // CRYPTO & FIAT CURRENCY TICKER // LIVE DATA", fill=(255, 170, 0), font=get_font(18, bold=True))
        canvas.draw_badge(w - 240, 12, "FEAR & GREED: 84 (GREED)", bg_color=(20, 50, 30), text_color=(0, 255, 136))
        canvas.draw_badge(w - 70, 12, "NBP", bg_color=(30, 45, 65))

        # Big Candlestick / Area Chart
        canvas.draw_card(20, 65, 620, 440, title="WYKRES ŚWIECOWY BTC/USD (24H)", subtitle="Średnia krocząca EMA 20/50 + Wolumen obrotu")
        # Draw chart grid
        for gy in range(130, 460, 60):
            draw.line([(40, gy), (620, gy)], fill=(20, 30, 45))
        # Draw candlesticks
        for i, val in enumerate(self.candles):
            cx = 60 + i * 46
            top = 450 - int(val * 2.2)
            draw.line([(cx + 12, top - 15), (cx + 12, top + 45)], fill=(0, 255, 136), width=2)
            draw.rectangle([cx, top, cx + 24, top + 30], fill=(0, 200, 120))
        draw.text((45, 130), "ATH: $99,800", fill=(100, 140, 180), font=get_font(12))
        draw.text((45, 455), "MIN 24H: $92,100", fill=(100, 140, 180), font=get_font(12))

        # Right Side: Crypto Assets
        canvas.draw_card(660, 65, 344, 440, title="RYNEK KRYPTOWALUT", subtitle="Aktualne wyceny spot")
        for i, (name, price, chg, up) in enumerate(self.crypto):
            cy = 125 + i * 90
            draw.rectangle([675, cy, 985, cy + 75], fill=(16, 24, 38), outline=(0, 255, 136) if up else (255, 70, 70))
            draw.text((690, cy + 12), name, fill=(220, 235, 255), font=get_font(13, bold=True))
            draw.text((690, cy + 36), price, fill=(255, 255, 255), font=get_font(22, bold=True))
            draw.text((910, cy + 40), chg, fill=(0, 255, 136) if up else (255, 80, 80), font=get_font(14, bold=True))

        # Bottom: NBP Currencies
        canvas.draw_card(20, 520, 984, 190, title="KURSY ŚREDNIE WALUT NBP (TABELA A)", subtitle="Oficjalne kursy Narodowego Banku Polskiego")
        for i, (pair, rate, chg) in enumerate(self.fx):
            fx_x = 40 + i * 320
            draw.rectangle([fx_x, 570, fx_x + 300, 680], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((fx_x + 16, 585), pair, fill=(160, 185, 215), font=get_font(13))
            draw.text((fx_x + 16, 615), rate, fill=(0, 240, 255), font=get_font(24, bold=True))
            draw.text((fx_x + 220, 622), chg, fill=(0, 255, 136) if "+" in chg else (255, 80, 80), font=get_font(14, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Aktywa | [A]: Wybierz Parę | [X]: Interwał (1h/24h/7d)", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 051: mod_tracks.py - GPX Track Inspector & Outdoor Workout
MODULES["mod_tracks"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TracksModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.track_name = "Trasa_Warta_Gorzow_Santok.gpx"
        self.distance_km = 16.4
        self.elevation_gain = 245
        self.duration = "01:42:15"
        self.avg_speed = "9.6 km/h"

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 15, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), f"🗺️ 051 // GPX TRACK INSPECTOR // {self.track_name}", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 180, 12, "KARTA SD // GPX", bg_color=(20, 50, 40))

        # Vector Map Area
        canvas.draw_card(20, 65, 640, 440, title="WEKTOROWA TRASA GPS (ŚCIEŻKA)", subtitle="Współrzędne WGS84 z pliku GPX")
        draw.rectangle([40, 120, 640, 480], fill=(14, 22, 32), outline=(0, 180, 200))
        # Draw mock GPS track
        points = [(60, 400), (140, 370), (220, 310), (320, 260), (410, 240), (490, 200), (580, 160)]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=(0, 255, 180), width=4)
        draw.ellipse([(points[0][0]-6, points[0][1]-6), (points[0][0]+6, points[0][1]+6)], fill=(0, 255, 0))
        draw.text((points[0][0]+12, points[0][1]-10), "START", fill=(0, 255, 0), font=get_font(12, bold=True))
        draw.ellipse([(points[-1][0]-6, points[-1][1]-6), (points[-1][0]+6, points[-1][1]+6)], fill=(255, 0, 80))
        draw.text((points[-1][0]+12, points[-1][1]-10), "META", fill=(255, 80, 80), font=get_font(12, bold=True))

        # Stats Card
        canvas.draw_card(680, 65, 324, 440, title="STATYSTYKI TRENINGU", subtitle="Telemetria z czujników GPS")
        stats = [
            ("DYSTANS:", f"{self.distance_km} km"),
            ("PRZEWYŻSZENIE:", f"+{self.elevation_gain} m"),
            ("CZAS SESJI:", self.duration),
            ("ŚREDNIA PRĘDKOŚĆ:", self.avg_speed),
            ("SPALONE KALORIE:", "680 kcal"),
        ]
        for i, (label, val) in enumerate(stats):
            draw.text((700, 130 + i * 65), label, fill=(140, 170, 200), font=get_font(13))
            draw.text((700, 150 + i * 65), val, fill=(0, 255, 180), font=get_font(24, bold=True))

        # Bottom Elevation Profile
        canvas.draw_card(20, 520, 984, 190, title="PROFIL WYSOKOŚCIOWY TERENU (ELEVATION PROFILE)", subtitle="Wysokość n.p.m. w funkcji dystansu")
        draw.rectangle([40, 570, 984, 680], fill=(14, 20, 30))
        alt_points = [20, 25, 45, 60, 85, 110, 95, 130, 145, 120, 90, 75, 40]
        for i in range(len(alt_points) - 1):
            x1 = 50 + i * 75
            x2 = 50 + (i + 1) * 75
            y1 = 670 - alt_points[i]
            y2 = 670 - alt_points[i + 1]
            draw.line([(x1, y1), (x2, y2)], fill=(255, 200, 0), width=3)
        draw.text((50, 580), "Max: 145 m n.p.m. | Min: 18 m n.p.m.", fill=(255, 200, 0), font=get_font(13, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Przewijaj Trasę | [A]: Otwórz Inny Plik GPX | [Y]: Zoom Mapy", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 052: mod_chip8.py - CHIP-8 Retro Virtual Machine & Game Lab
MODULES["mod_chip8"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class Chip8Module(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.rom_name = "PONG.CH8"
        self.pc = 0x0200
        self.i_reg = 0x0250
        self.delay_timer = 60
        self.sound_timer = 0
        self.fps = 60
        self.screen_grid = [[1 if (x+y)%7==0 else 0 for x in range(64)] for y in range(32)]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((6, 10, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🕹️ 052 // CHIP-8 RETRO VIRTUAL MACHINE // ROM: {self.rom_name}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 200, 12, "CPU: 500 HZ", bg_color=(20, 40, 60))
        canvas.draw_badge(w - 80, 12, "60 FPS", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Big 64x32 Monochrome Screen
        canvas.draw_card(20, 65, 680, 460, title="EKRAN WIRTUALNY 64x32 PIKSELE", subtitle="Bezpośredni bufor graficzny CHIP-8")
        sx, sy, sz = 40, 120, 9.8
        draw.rectangle([sx, sy, sx + 64 * sz, sy + 32 * sz], fill=(4, 8, 14), outline=(0, 240, 255), width=2)
        for y in range(32):
            for x in range(64):
                if self.screen_grid[y][x]:
                    draw.rectangle([sx + x * sz, sy + y * sz, sx + (x + 1) * sz - 1, sy + (y + 1) * sz - 1], fill=(0, 255, 180))

        # CPU Registers & Disassembly
        canvas.draw_card(720, 65, 284, 460, title="REJESTRY & STAN CPU", subtitle="Architektura CHIP-8 (1977)")
        draw.text((740, 125), f"PC:  0x{self.pc:04X}", fill=(0, 255, 136), font=get_font(14, bold=True))
        draw.text((740, 150), f"I:   0x{self.i_reg:04X}", fill=(0, 255, 136), font=get_font(14, bold=True))
        draw.text((740, 175), f"DT:  {self.delay_timer}", fill=(255, 200, 0), font=get_font(14))
        draw.text((740, 200), f"ST:  {self.sound_timer}", fill=(255, 200, 0), font=get_font(14))
        draw.text((740, 235), "REJESTRY V0 - VF:", fill=(140, 170, 210), font=get_font(13))
        for r in range(8):
            draw.text((740, 260 + r * 22), f"V{r:X}: 0x00    V{r+8:X}: 0x00", fill=(180, 200, 230), font=get_font(12))

        # Bottom Game Selector & Controls
        canvas.draw_card(20, 540, 984, 170, title="STEROWANIE GRĄ & WYBÓR ROMU", subtitle="Mapowanie klawiatury heksadecymalnej 4x4 na D-Pad i ABXY")
        draw.text((40, 600), "D-Pad Góra/Dół: Paletka Gracza 1 | Klawisz A: Serwuj Piłkę | Klawisz B: Reset Gry", fill=(0, 255, 180), font=get_font(15, bold=True))
        draw.text((40, 635), "Dostępne ROMy na karcie SD: PONG.CH8, TETRIS.CH8, INVADERS.CH8, BLINKY.CH8, BRIX.CH8", fill=(140, 170, 200), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Ruch w grze | [A]: Akcja | [Y]: Wybierz Inny ROM CHIP-8", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 053: mod_rss.py - Pocket RSS & Tech News Reader
MODULES["mod_rss"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class RssReaderModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.selected_idx = 0
        self.articles = [
            ("Niebezpiecznik", "Luka 0-day w jądrze Linuksa ARM64 – zalecana natychmiastowa aktualizacja", "10 min temu"),
            ("Sekurak", "Analiza ataku na magistralę CAN w nowoczesnych samochodach elektrycznych", "42 min temu"),
            ("Hacker News", "Show HN: CPython 3.12 compiled to WebAssembly runs 60 FPS games", "1 godz. temu"),
            ("Zaufana Trzecia Strona", "Ostrzeżenie przed nową kampanią phishingową podszywającą się pod mObywatela", "2 godz. temu"),
            ("Ars Technica", "NASA James Webb Space Telescope discovers oldest known black hole", "3 godz. temu"),
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(255, 140, 0, 100), width=1)
        draw.text((20, 14), "📰 053 // POCKET RSS & TECH NEWS READER (OFFLINE CACHE)", fill=(255, 140, 0), font=get_font(18, bold=True))
        canvas.draw_badge(w - 200, 12, "TRYB: OFFLINE", bg_color=(20, 45, 60))
        canvas.draw_badge(w - 75, 12, "5 RSS", bg_color=(40, 25, 10), text_color=(255, 170, 0))

        # Left list
        canvas.draw_card(20, 65, 450, 640, title="NAGŁÓWKI WIADOMOŚCI", subtitle="Wybierz artykuł D-Padem")
        for i, (source, title, time_ago) in enumerate(self.articles):
            is_sel = (i == self.selected_idx)
            bg = (24, 38, 58) if is_sel else (14, 20, 30)
            draw.rectangle([35, 125 + i * 110, 455, 225 + i * 110], fill=bg, outline=(255, 140, 0) if is_sel else (35, 50, 70), width=2 if is_sel else 1)
            draw.text((45, 135 + i * 110), f"[{source.upper()}] • {time_ago}", fill=(255, 170, 0) if is_sel else (120, 150, 180), font=get_font(12, bold=True))
            # Text line wrap
            words = title.split()
            l1, l2 = "", ""
            for w_item in words:
                if len(l1) + len(w_item) < 32: l1 += w_item + " "
                else: l2 += w_item + " "
            draw.text((45, 155 + i * 110), l1, fill=(240, 245, 255), font=get_font(14, bold=is_sel))
            if l2: draw.text((45, 175 + i * 110), l2, fill=(240, 245, 255), font=get_font(14, bold=is_sel))

        # Right Reader Preview
        canvas.draw_card(485, 65, 519, 640, title="TREŚĆ ARTYKUŁU // CZYTNIK", subtitle="Formatowanie tekstu bez reklam i trackerów")
        src, tit, tm = self.articles[self.selected_idx]
        draw.text((505, 130), src.upper(), fill=(255, 170, 0), font=get_font(14, bold=True))
        draw.text((505, 155), tit, fill=(0, 240, 255), font=get_font(18, bold=True))
        draw.line([(505, 195), (980, 195)], fill=(30, 45, 65), width=2)
        sample_body = (
            "Eksperci do spraw cyberbezpieczeństwa opublikowali szczegółowy raport dotyczący nowo odkrytej "
            "podatności. Atakujący może uzyskać podwyższenie uprawnień do poziomu roota, omijając "
            "standardowe mechanizmy izolacji pamięci. Zaleca się zastosowanie najnowszych łatek w systemach "
            "oraz weryfikację logów audytowych. Zespół projektowy potwierdził wydanie poprawki w repozytorium."
        )
        words = sample_body.split()
        cur_line = ""
        by = 215
        for word in words:
            if len(cur_line) + len(word) > 42:
                draw.text((505, by), cur_line, fill=(210, 225, 245), font=get_font(16))
                by += 28
                cur_line = word + " "
            else:
                cur_line += word + " "
        if cur_line:
            draw.text((505, by), cur_line, fill=(210, 225, 245), font=get_font(16))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Góra/Dół: Następny/Poprzedni Artykuł | [A]: Tryb Pełnoekranowy | [Y]: Synchronizuj Wi-Fi", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_UP", "UP"):
            self.selected_idx = (self.selected_idx - 1) % len(self.articles); return True
        elif event in ("KEY_DOWN", "DOWN"):
            self.selected_idx = (self.selected_idx + 1) % len(self.articles); return True
        return False
'''

# 054: mod_tachometer.py - Stroboskopowy Obrotomierz Optyczny RPM
MODULES["mod_tachometer"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class TachometerModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.target_rpm = 1200
        self.freq_hz = 20.0
        self.duty_cycle = 10
        self.running = False

    def update(self, dt: float):
        self.freq_hz = self.target_rpm / 60.0

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 12, 20, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🌀 054 // STROBOSKOPOWY OBROTOMIERZ OPTYCZNY RPM", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "BEZDOTYKOWY POMIAR", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "60 HZ", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Main RPM Gauge Card
        canvas.draw_card(20, 65, 600, 450, title="CZĘSTOTLIWOŚĆ BŁYSKÓW STROBOSKOPU", subtitle="Skieruj ekran IPS na wirujące śmigło/wentylator")
        draw.text((130, 140), f"{self.target_rpm}", fill=(0, 255, 180), font=get_font(96, bold=True))
        draw.text((430, 205), "RPM", fill=(0, 200, 255), font=get_font(32, bold=True))
        draw.text((135, 275), f"Częstotliwość migania: {self.freq_hz:.2f} Hz", fill=(255, 220, 0), font=get_font(22, bold=True))
        draw.text((135, 315), f"Wypełnienie impulsu (Duty): {self.duty_cycle}% (Ostre krawędzie)", fill=(140, 170, 200), font=get_font(16))
        draw.text((70, 390), "Zasada: Gdy obracający się element wydaje się stać w miejscu,", fill=(180, 200, 230), font=get_font(14))
        draw.text((70, 415), "częstotliwość błysków równa się rzeczywistym obrotom RPM.", fill=(0, 255, 180), font=get_font(14, bold=True))

        # Preset Speeds & Quick Jumps
        canvas.draw_card(640, 65, 364, 450, title="SZYBKIE NASTAWY WARSZTATOWE", subtitle="Standardowe prędkości silników")
        presets = [
            ("Wentylator PC 120mm", "1200 RPM", "20.0 Hz"),
            ("Wentylator Wysokoobrotowy", "2400 RPM", "40.0 Hz"),
            ("Silnik Krokowy NEMA 17", "600 RPM", "10.0 Hz"),
            ("Wrzeciono CNC Dremel", "3600 RPM", "60.0 Hz"),
        ]
        for i, (p_name, p_rpm, p_hz) in enumerate(presets):
            cy = 135 + i * 75
            draw.rectangle([660, cy, 980, cy + 65], fill=(16, 24, 38), outline=(0, 200, 255))
            draw.text((675, cy + 12), p_name, fill=(220, 235, 255), font=get_font(13, bold=True))
            draw.text((675, cy + 34), p_rpm, fill=(0, 255, 180), font=get_font(16, bold=True))
            draw.text((880, cy + 34), p_hz, fill=(255, 200, 0), font=get_font(14))

        # Bottom Instructions
        canvas.draw_card(20, 530, 984, 180, title="INSTRUKCJA BEZPIECZEŃSTWA", subtitle="Ostrzeżenie przed epilepsją fotogenną")
        draw.text((40, 595), "⚠️ UWAGA: Moduł generuje impulsy świetlne o wysokiej częstotliwości.", fill=(255, 80, 80), font=get_font(15, bold=True))
        draw.text((40, 625), "Nie używać w obecności osób wrażliwych na migające światło. Trzymaj ekran 10 cm od badanego obiektu.", fill=(160, 180, 210), font=get_font(14))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Dokładna regulacja ±10 RPM | Góra/Dół: ±100 RPM | [A]: Włącz/Wyłącz Stroboskop", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "LEFT"):
            self.target_rpm = max(60, self.target_rpm - 10); return True
        elif event in ("KEY_RIGHT", "RIGHT"):
            self.target_rpm = min(7200, self.target_rpm + 10); return True
        elif event in ("KEY_UP", "UP"):
            self.target_rpm = min(7200, self.target_rpm + 100); return True
        elif event in ("KEY_DOWN", "DOWN"):
            self.target_rpm = max(60, self.target_rpm - 100); return True
        return False
'''

# 055: mod_stego.py - Steganografia Obrazowa LSB
MODULES["mod_stego"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class StegoModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.filename = "secret_carrier_photo.png"
        self.status = "UKRYTA WIADOMOŚĆ WYKRYTA (LSB EMBEDDED)"
        self.extracted_text = "KLUCZ_EWAKUACJI_BRAVO_2026_SEKTOR_9 // KOD_AUTORYZACJI: #77F2-99B1"
        self.bits_per_channel = 1
        self.payload_size = 64

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🖼️ 055 // STEGANOGRAFIA OBRAZOWA LSB (LEAST SIGNIFICANT BIT) // {self.filename}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 200, 12, "LSB 1-BIT RGB", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "64 B", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Carrier Image Simulation Box
        canvas.draw_card(20, 65, 450, 440, title="NOŚNIK GRAFICZNY (CARRIER)", subtitle="Wizualny podgląd pliku PNG z karty SD")
        draw.rectangle([40, 120, 450, 480], fill=(18, 28, 44), outline=(0, 180, 220))
        # Visual mock noise
        for y in range(130, 470, 15):
            for x in range(50, 440, 15):
                draw.rectangle([x, y, x + 8, y + 8], fill=(25, 45, 75))
        draw.text((120, 280), "[OBRAZ NOŚNIKA 1024x768]", fill=(120, 160, 210), font=get_font(15, bold=True))
        draw.text((95, 310), "Różnica wizualna dla oka: 0.00% (Niewidoczna)", fill=(0, 255, 136), font=get_font(12))

        # Extracted Payload Card
        canvas.draw_card(490, 65, 514, 440, title="WYODRĘBNIONE DANE TEKSTOWE", subtitle="Zdekodowane bajty z najmłodszych bitów kanałów R, G, B")
        draw.rectangle([510, 130, 980, 270], fill=(14, 20, 30), outline=(0, 255, 180), width=2)
        draw.text((525, 150), "ZDEKODOWANY TEKST:", fill=(255, 170, 0), font=get_font(13, bold=True))
        draw.text((525, 185), self.extracted_text[:40], fill=(0, 255, 200), font=get_font(15, bold=True))
        draw.text((525, 215), self.extracted_text[40:], fill=(0, 255, 200), font=get_font(15, bold=True))

        draw.text((510, 300), "STATYSTYKI NOŚNIKA LSB:", fill=(140, 170, 205), font=get_font(14, bold=True))
        draw.text((510, 330), f"Pojemność nośnika: 294 912 bajtów (288 KB)", fill=(160, 185, 215), font=get_font(14))
        draw.text((510, 360), f"Wykorzystano bitów: {self.payload_size * 8} / 2 359 296 (0.02%)", fill=(160, 185, 215), font=get_font(14))
        draw.text((510, 390), "Entropia Shannona: 7.9984 bit/bajt (Optymalna)", fill=(0, 255, 136), font=get_font(14))

        # Bottom Stego Inspector Mode
        canvas.draw_card(20, 520, 984, 190, title="ANALIZATOR ENTROPII I WYKRYWACZ STEGO (CHI-SQUARE)", subtitle="Test statystyczny Chi-Kwadrat na obecność ukrytej steganografii")
        draw.text((40, 580), "Współczynnik anomalii bitowej: 0.984 -> Prawdopodobieństwo steganografii: 99.2%", fill=(255, 200, 0), font=get_font(15, bold=True))
        draw.rectangle([40, 620, 960, 650], fill=(20, 30, 45))
        draw.rectangle([40, 620, 40 + int(920 * 0.992), 650], fill=(255, 170, 0))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Obraz PNG | [A]: Ekstrakcja Wiadomości LSB | [Y]: Ukryj Nowy Tekst", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

# 056: mod_shamir.py - Dzielenie Sekretu Shamira (k, n)
MODULES["mod_shamir"] = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class ShamirSecretModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.k_threshold = 3
        self.n_shares = 5
        self.secret_seed = "abandon ability able about above absent absorb abstract absurd abuse"
        self.shares = [
            ("CZĘŚĆ #1", "01-8A3F-99B1-44E2-C7A1", True),
            ("CZĘŚĆ #2", "02-11C0-77A4-99D3-FF82", True),
            ("CZĘŚĆ #3", "03-44E8-22B9-11C4-AA90", True),
            ("CZĘŚĆ #4", "04-99A1-55C2-77F8-BB12", False),
            ("CZĘŚĆ #5", "05-22B4-88D1-33E9-CC45", False),
        ]

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 24, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 180, 100), width=1)
        draw.text((20, 14), f"🧩 056 // DZIELENIE SEKRETU SHAMIRA (K={self.k_threshold}, N={self.n_shares}) CRYPTO-VAULT", fill=(0, 255, 180), font=get_font(18, bold=True))
        canvas.draw_badge(w - 240, 12, "PRÓG K=3 Z N=5", bg_color=(20, 50, 40))
        canvas.draw_badge(w - 85, 12, "GF(256)", bg_color=(40, 30, 60), text_color=(0, 240, 255))

        # Reconstructed Secret Card
        canvas.draw_card(20, 65, 984, 200, title="ODZYSKANY SEKRET / FRAZA SEED PORTFELA", subtitle="Sekret odtwarzany przy pomocy wielomianu Lagrange'a nad ciałem Galois GF(256)")
        draw.rectangle([40, 120, 980, 230], fill=(14, 22, 34), outline=(0, 255, 136), width=2)
        draw.text((60, 140), "ODTWISTOŚĆ: SUKCES (DOSTARCZONO 3 Z 5 CZĘŚCI)", fill=(0, 255, 136), font=get_font(14, bold=True))
        draw.text((60, 175), self.secret_seed, fill=(255, 230, 120), font=get_font(18, bold=True))

        # Shares Grid
        canvas.draw_card(20, 280, 984, 430, title="WYGENEROWANE KLUCZE SKŁADOWE (SHARES)", subtitle="Rozdaj klucze zaufanym osobom lub ukryj w różnych lokalizacjach")
        for i, (name, val, active) in enumerate(self.shares):
            sy = 340 + i * 68
            border = (0, 255, 180) if active else (40, 60, 85)
            draw.rectangle([40, sy, 980, sy + 58], fill=(16, 24, 38) if active else (12, 16, 26), outline=border, width=2 if active else 1)
            draw.text((60, sy + 18), name, fill=(0, 240, 255) if active else (120, 140, 170), font=get_font(15, bold=True))
            draw.text((220, sy + 18), val, fill=(240, 245, 255) if active else (90, 110, 140), font=get_font(16, bold=True))
            tag = "✅ DOSTARCZONA DO ODTWORZENIA" if active else "❌ BRAK (NIEWYMAGANA PRZY K=3)"
            draw.text((620, sy + 20), tag, fill=(0, 255, 136) if active else (100, 120, 150), font=get_font(12, bold=True))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad: Wybierz Część | [A]: Wprowadź Klucz | [Y]: Wygeneruj Nowy Podział (K, N)", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
'''

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "store", "modules")
os.makedirs(output_dir, exist_ok=True)

for name, code in MODULES.items():
    path = os.path.join(output_dir, f"{name}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[+] Zapisano: {name}.py")

print(f"Batch 3 completed! Generated {len(MODULES)} modules.")
