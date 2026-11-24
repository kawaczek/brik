"""
BrickDeck Module: Hardware Pinouts & Pocket Reference
Interactive offline pinout diagram and electrical cheat-sheet for Raspberry Pi, ESP32, Flipper Zero, USB-C, DB9, and Arduino.
"""

from typing import List, Dict, Tuple, Optional

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)
from core.canvas import get_font

# Pin Color Coding
COL_5V = (235, 60, 60)         # Red
COL_3V3 = (240, 140, 20)       # Orange
COL_GND = (40, 48, 56)         # Deep Gray
COL_I2C = (0, 180, 255)        # Blue
COL_SPI = (180, 80, 240)       # Purple
COL_UART = (50, 220, 100)      # Green
COL_GPIO = (220, 200, 40)      # Yellow
COL_OTHER = (100, 110, 125)    # Gray
COL_FLIPPER_AMBER = COLOR_FLIPPER_AMBER
COL_CYBER_CYAN = COLOR_CYBER_CYAN


BOARDS_DATA = [
    {
        "name": "Raspberry Pi 40-Pin Header",
        "short": "RPi 40-Pin",
        "desc": "Standard 2x20 header dla RPi 3B+, 4B, 5, Zero / Zero 2W. Logika 3.3V (LVTTL).",
        "power_warning": "UWAGA: Piny GPIO tolerują TYLKO 3.3V! Podanie 5V bez konwertera spali układ BCM SoC.",
        "pins": [
            {"pin": 1, "name": "3V3 Power", "type": "POWER", "col": COL_3V3, "note": "Zasilanie 3.3V (max ~50mA)"},
            {"pin": 2, "name": "5V Power", "type": "POWER", "col": COL_5V, "note": "Szyna 5V bezpośrednio z USB-C"},
            {"pin": 3, "name": "GPIO 2 (SDA)", "type": "I2C", "col": COL_I2C, "note": "I2C1 Data (wbudowany pull-up 1.8k do 3.3V)"},
            {"pin": 4, "name": "5V Power", "type": "POWER", "col": COL_5V, "note": "Szyna 5V (do 2-3A w zależności od zasilacza)"},
            {"pin": 5, "name": "GPIO 3 (SCL)", "type": "I2C", "col": COL_I2C, "note": "I2C1 Clock (wbudowany pull-up 1.8k do 3.3V)"},
            {"pin": 6, "name": "Ground", "type": "GND", "col": COL_GND, "note": "Masa układu (0V)"},
            {"pin": 7, "name": "GPIO 4 (GPCLK0)", "type": "GPIO", "col": COL_GPIO, "note": "Ogólny pin GPIO / 1-Wire (DS18B20)"},
            {"pin": 8, "name": "GPIO 14 (TXD)", "type": "UART", "col": COL_UART, "note": "UART0 Transmit (Primary Serial)"},
            {"pin": 9, "name": "Ground", "type": "GND", "col": COL_GND, "note": "Masa układu (0V)"},
            {"pin": 10, "name": "GPIO 15 (RXD)", "type": "UART", "col": COL_UART, "note": "UART0 Receive (Primary Serial)"},
            {"pin": 11, "name": "GPIO 17", "type": "GPIO", "col": COL_GPIO, "note": "Standardowy pin wejścia/wyjścia"},
            {"pin": 12, "name": "GPIO 18 (PWM0)", "type": "PWM", "col": COL_GPIO, "note": "Sprzętowy PWM kanał 0 / Audio DAC"},
            {"pin": 13, "name": "GPIO 27", "type": "GPIO", "col": COL_GPIO, "note": "Standardowy pin wejścia/wyjścia"},
            {"pin": 14, "name": "Ground", "type": "GND", "col": COL_GND, "note": "Masa układu (0V)"},
            {"pin": 15, "name": "GPIO 22", "type": "GPIO", "col": COL_GPIO, "note": "Standardowy pin wejścia/wyjścia"},
            {"pin": 16, "name": "GPIO 23", "type": "GPIO", "col": COL_GPIO, "note": "Standardowy pin wejścia/wyjścia"},
            {"pin": 17, "name": "3V3 Power", "type": "POWER", "col": COL_3V3, "note": "Zasilanie 3.3V"},
            {"pin": 18, "name": "GPIO 24", "type": "GPIO", "col": COL_GPIO, "note": "Standardowy pin wejścia/wyjścia"},
            {"pin": 19, "name": "GPIO 10 (MOSI)", "type": "SPI", "col": COL_SPI, "note": "SPI0 Master Out Slave In"},
            {"pin": 20, "name": "Ground", "type": "GND", "col": COL_GND, "note": "Masa układu (0V)"},
            {"pin": 21, "name": "GPIO 9 (MISO)", "type": "SPI", "col": COL_SPI, "note": "SPI0 Master In Slave Out"},
            {"pin": 22, "name": "GPIO 25", "type": "GPIO", "col": COL_GPIO, "note": "Standardowy pin wejścia/wyjścia"},
            {"pin": 23, "name": "GPIO 11 (SCLK)", "type": "SPI", "col": COL_SPI, "note": "SPI0 Serial Clock"},
            {"pin": 24, "name": "GPIO 8 (CE0)", "type": "SPI", "col": COL_SPI, "note": "SPI0 Chip Enable 0 (CS0)"},
            {"pin": 25, "name": "Ground", "type": "GND", "col": COL_GND, "note": "Masa układu (0V)"},
            {"pin": 26, "name": "GPIO 7 (CE1)", "type": "SPI", "col": COL_SPI, "note": "SPI0 Chip Enable 1 (CS1)"},
            {"pin": 27, "name": "ID_SD", "type": "I2C", "col": COL_I2C, "note": "I2C ID EEPROM dla nakładek HAT"},
            {"pin": 28, "name": "ID_SC", "type": "I2C", "col": COL_I2C, "note": "I2C ID EEPROM Clock"},
            {"pin": 29, "name": "GPIO 5", "type": "GPIO", "col": COL_GPIO, "note": "Standardowy pin wejścia/wyjścia"},
            {"pin": 30, "name": "Ground", "type": "GND", "col": COL_GND, "note": "Masa układu (0V)"},
            {"pin": 31, "name": "GPIO 6", "type": "GPIO", "col": COL_GPIO, "note": "Standardowy pin wejścia/wyjścia"},
            {"pin": 32, "name": "GPIO 12 (PWM0)", "type": "PWM", "col": COL_GPIO, "note": "Sprzętowy PWM kanał 0"},
            {"pin": 33, "name": "GPIO 13 (PWM1)", "type": "PWM", "col": COL_GPIO, "note": "Sprzętowy PWM kanał 1"},
            {"pin": 34, "name": "Ground", "type": "GND", "col": COL_GND, "note": "Masa układu (0V)"},
            {"pin": 35, "name": "GPIO 19 (PWM1)", "type": "PWM", "col": COL_GPIO, "note": "Sprzętowy PWM kanał 1 / PCM FS"},
            {"pin": 36, "name": "GPIO 16", "type": "GPIO", "col": COL_GPIO, "note": "Standardowy pin wejścia/wyjścia"},
            {"pin": 37, "name": "GPIO 26", "type": "GPIO", "col": COL_GPIO, "note": "Standardowy pin wejścia/wyjścia"},
            {"pin": 38, "name": "GPIO 20", "type": "GPIO", "col": COL_GPIO, "note": "PCM Digital Audio Data In"},
            {"pin": 39, "name": "Ground", "type": "GND", "col": COL_GND, "note": "Masa układu (0V)"},
            {"pin": 40, "name": "GPIO 21", "type": "GPIO", "col": COL_GPIO, "note": "PCM Digital Audio Data Out"}
        ]
    },
    {
        "name": "ESP32 DevKit 30-Pin (WROOM)",
        "short": "ESP32 30-Pin",
        "desc": "Popularny moduł deweloperski ESP32. Dwurdzeniowy Xtensa LX6, Wi-Fi 2.4GHz + BLE.",
        "power_warning": "UWAGA: ADC2 nie działa podczas aktywnego Wi-Fi! Uważaj na piny strappingu (GPIO 0, 2, 12, 15).",
        "pins": [
            {"pin": 1, "name": "EN / RST", "type": "OTHER", "col": COL_OTHER, "note": "Reset układu (Active LOW, pull-up 10k)"},
            {"pin": 2, "name": "VP / GPIO 36", "type": "ADC", "col": COL_GPIO, "note": "ADC1_CH0 (Tylko wejście, brak pull-up)"},
            {"pin": 3, "name": "VN / GPIO 39", "type": "ADC", "col": COL_GPIO, "note": "ADC1_CH3 (Tylko wejście, brak pull-up)"},
            {"pin": 4, "name": "GPIO 34", "type": "ADC", "col": COL_GPIO, "note": "ADC1_CH6 (Tylko wejście cyfrowe/analog)"},
            {"pin": 5, "name": "GPIO 35", "type": "ADC", "col": COL_GPIO, "note": "ADC1_CH7 (Tylko wejście cyfrowe/analog)"},
            {"pin": 6, "name": "GPIO 32", "type": "ADC", "col": COL_GPIO, "note": "ADC1_CH4 / Touch 9 / Kryształ 32kHz"},
            {"pin": 7, "name": "GPIO 33", "type": "ADC", "col": COL_GPIO, "note": "ADC1_CH5 / Touch 8"},
            {"pin": 8, "name": "GPIO 25", "type": "DAC", "col": COL_GPIO, "note": "DAC 1 (Prawdziwy 8-bit analog out) / ADC2_8"},
            {"pin": 9, "name": "GPIO 26", "type": "DAC", "col": COL_GPIO, "note": "DAC 2 / ADC2_9"},
            {"pin": 10, "name": "GPIO 27", "type": "GPIO", "col": COL_GPIO, "note": "Touch 7 / ADC2_7 / PWM"},
            {"pin": 11, "name": "GPIO 14", "type": "SPI", "col": COL_SPI, "note": "HSPI_CLK / Touch 6 / Strapping"},
            {"pin": 12, "name": "GPIO 12", "type": "SPI", "col": COL_SPI, "note": "HSPI_MISO / MTDI (Strapping pin!)"},
            {"pin": 13, "name": "GND", "type": "GND", "col": COL_GND, "note": "Masa (0V)"},
            {"pin": 14, "name": "VIN / 5V", "type": "POWER", "col": COL_5V, "note": "Wejście zasilania 5V przez stabilizator LDO"},
            {"pin": 15, "name": "GPIO 23", "type": "SPI", "col": COL_SPI, "note": "VSPI_MOSI"},
            {"pin": 16, "name": "GPIO 22", "type": "I2C", "col": COL_I2C, "note": "I2C_SCL (domyślny zegar sprzętowy)"},
            {"pin": 17, "name": "TX0 / GPIO 1", "type": "UART", "col": COL_UART, "note": "UART0 Transmit (programowanie USB)"},
            {"pin": 18, "name": "RX0 / GPIO 3", "type": "UART", "col": COL_UART, "note": "UART0 Receive (programowanie USB)"},
            {"pin": 19, "name": "GPIO 21", "type": "I2C", "col": COL_I2C, "note": "I2C_SDA (domyślne dane sprzętowe)"},
            {"pin": 20, "name": "GPIO 19", "type": "SPI", "col": COL_SPI, "note": "VSPI_MISO"},
            {"pin": 21, "name": "GPIO 18", "type": "SPI", "col": COL_SPI, "note": "VSPI_CLK"},
            {"pin": 22, "name": "GPIO 5", "type": "SPI", "col": COL_SPI, "note": "VSPI_CS0 (Strapping: boot log)"},
            {"pin": 23, "name": "GPIO 17", "type": "UART", "col": COL_UART, "note": "UART2_TXD"},
            {"pin": 24, "name": "GPIO 16", "type": "UART", "col": COL_UART, "note": "UART2_RXD"},
            {"pin": 25, "name": "GPIO 4", "type": "GPIO", "col": COL_GPIO, "note": "Touch 0 / ADC2_0"},
            {"pin": 26, "name": "GPIO 0", "type": "OTHER", "col": COL_OTHER, "note": "BOOT Pin (Musi być HIGH przy starcie!)"},
            {"pin": 27, "name": "GPIO 2", "type": "OTHER", "col": COL_OTHER, "note": "Wbudowana niebieska LED (Strapping pin)"},
            {"pin": 28, "name": "GPIO 15", "type": "SPI", "col": COL_SPI, "note": "HSPI_CS0 (Strapping pin)"},
            {"pin": 29, "name": "GND", "type": "GND", "col": COL_GND, "note": "Masa (0V)"},
            {"pin": 30, "name": "3V3 Power", "type": "POWER", "col": COL_3V3, "note": "Wyjście regulowane 3.3V"}
        ]
    },
    {
        "name": "Flipper Zero 18-Pin GPIO",
        "short": "Flipper GPIO",
        "desc": "Złącze rozszerzeń Flipper Zero na górnej ściance. 3.3V logiczne, ochrona ESD.",
        "power_warning": "UWAGA: Pin 9 to 3.3V (do 1.5A), Pin 1 to 5V (włączany w menu Power). Wejścia NIE są 5V tolerancyjne!",
        "pins": [
            {"pin": 1, "name": "5V Power Out", "type": "POWER", "col": COL_5V, "note": "Zasilanie 5V (włączane programowo w menu Flipper)"},
            {"pin": 2, "name": "PA7 / USART1_TX", "type": "UART", "col": COL_UART, "note": "UART Transmit / GPIO / IR Out"},
            {"pin": 3, "name": "PA6 / USART1_RX", "type": "UART", "col": COL_UART, "note": "UART Receive / GPIO / IR In"},
            {"pin": 4, "name": "PA4 / SPI1_CS", "type": "SPI", "col": COL_SPI, "note": "SPI Chip Select / DAC"},
            {"pin": 5, "name": "PB3 / SPI1_CLK", "type": "SPI", "col": COL_SPI, "note": "SPI Clock"},
            {"pin": 6, "name": "PB4 / SPI1_MISO", "type": "SPI", "col": COL_SPI, "note": "SPI Master In Slave Out"},
            {"pin": 7, "name": "PB5 / SPI1_MOSI", "type": "SPI", "col": COL_SPI, "note": "SPI Master Out Slave In"},
            {"pin": 8, "name": "GND", "type": "GND", "col": COL_GND, "note": "Masa układowa (0V)"},
            {"pin": 9, "name": "3V3 Power Out", "type": "POWER", "col": COL_3V3, "note": "Zasilanie 3.3V (zasilane z baterii Flippera)"},
            {"pin": 10, "name": "SWCLK", "type": "OTHER", "col": COL_OTHER, "note": "SWD Debug Clock dla STM32WB55"},
            {"pin": 11, "name": "GND", "type": "GND", "col": COL_GND, "note": "Masa układowa (0V)"},
            {"pin": 12, "name": "SWDIO", "type": "OTHER", "col": COL_OTHER, "note": "SWD Debug Data I/O"},
            {"pin": 13, "name": "PC0 / GPIO", "type": "GPIO", "col": COL_GPIO, "note": "Ogólny pin GPIO / ADC"},
            {"pin": 14, "name": "PC1 / GPIO", "type": "GPIO", "col": COL_GPIO, "note": "Ogólny pin GPIO / ADC"},
            {"pin": 15, "name": "PC3 / I2C1_SCL", "type": "I2C", "col": COL_I2C, "note": "I2C Zegar (Wymaga zewnętrznych pull-upów)"},
            {"pin": 16, "name": "PC4 / I2C1_SDA", "type": "I2C", "col": COL_I2C, "note": "I2C Dane (Wymaga zewnętrznych pull-upów)"},
            {"pin": 17, "name": "1-Wire / iButton", "type": "OTHER", "col": COL_FLIPPER_AMBER, "note": "Odczyt/Emulacja pastylek Dallas DS1990"},
            {"pin": 18, "name": "GND", "type": "GND", "col": COL_GND, "note": "Masa układowa (0V)"}
        ]
    },
    {
        "name": "USB-C 24-Pin Reversible Pinout",
        "short": "USB Type-C",
        "desc": "Pełne złącze symetryczne USB Type-C. Standard Power Delivery do 100W/240W, DisplayPort Alt Mode.",
        "power_warning": "Dla roli Sink (odbiornik 5V) piny CC1 i CC2 MUSZĄ mieć rezystory 5.1 kOhm do masy GND!",
        "pins": [
            {"pin": 1, "name": "A1 / B12: GND", "type": "GND", "col": COL_GND, "note": "Masa powrotna zasilania"},
            {"pin": 2, "name": "A2 / B11: SSTXp1", "type": "SPI", "col": COL_SPI, "note": "SuperSpeed TX Differential Positive"},
            {"pin": 3, "name": "A3 / B10: SSTXn1", "type": "SPI", "col": COL_SPI, "note": "SuperSpeed TX Differential Negative"},
            {"pin": 4, "name": "A4 / B9: VBUS", "type": "POWER", "col": COL_5V, "note": "Szyna zasilania 5V / 9V / 15V / 20V PD"},
            {"pin": 5, "name": "A5: CC1 (Config)", "type": "OTHER", "col": COL_CYBER_CYAN, "note": "Kanał konfiguracyjny (5.1k pull-down = Sink 5V)"},
            {"pin": 6, "name": "A6 / B7: D+ (USB 2.0)", "type": "UART", "col": COL_UART, "note": "Szyna danych High Speed USB 2.0 (480 Mbps)"},
            {"pin": 7, "name": "A7 / B6: D- (USB 2.0)", "type": "UART", "col": COL_UART, "note": "Szyna danych High Speed USB 2.0 (480 Mbps)"},
            {"pin": 8, "name": "A8: SBU1 (Sideband)", "type": "OTHER", "col": COL_OTHER, "note": "Sideband Use 1 (Auxiliary kanał DisplayPort Alt)"},
            {"pin": 9, "name": "A9 / B4: VBUS", "type": "POWER", "col": COL_5V, "note": "Szyna zasilania VBUS"},
            {"pin": 10, "name": "A10 / B3: SSRXn2", "type": "SPI", "col": COL_SPI, "note": "SuperSpeed RX Differential Negative"},
            {"pin": 11, "name": "A11 / B2: SSRXp2", "type": "SPI", "col": COL_SPI, "note": "SuperSpeed RX Differential Positive"},
            {"pin": 12, "name": "A12 / B1: GND", "type": "GND", "col": COL_GND, "note": "Masa powrotna zasilania"},
            {"pin": 13, "name": "B5: CC2 (Config)", "type": "OTHER", "col": COL_CYBER_CYAN, "note": "Drugi kanał konfiguracyjny CC"}
        ]
    },
    {
        "name": "DB9 RS-232 / TTL Serial",
        "short": "DB9 Serial",
        "desc": "Standard 9-pinowego złącza szeregowego D-Sub DE-9. Stosowany w konsolach przemysłowych i retro PC.",
        "power_warning": "UWAGA: Prawdziwy standard RS-232 używa napięć od -12V do +12V! Wymaga konwertera MAX3232 dla mikrokontrolerów.",
        "pins": [
            {"pin": 1, "name": "Pin 1: DCD", "type": "OTHER", "col": COL_OTHER, "note": "Data Carrier Detect (Wykrycie nośnej)"},
            {"pin": 2, "name": "Pin 2: RxD", "type": "UART", "col": COL_UART, "note": "Receive Data (Odbiór danych do komputera)"},
            {"pin": 3, "name": "Pin 3: TxD", "type": "UART", "col": COL_UART, "note": "Transmit Data (Nadawanie danych z komputera)"},
            {"pin": 4, "name": "Pin 4: DTR", "type": "OTHER", "col": COL_OTHER, "note": "Data Terminal Ready (Terminal gotowy do pracy)"},
            {"pin": 5, "name": "Pin 5: GND", "type": "GND", "col": COL_GND, "note": "Signal Ground (Wspólna masa sygnałowa)"},
            {"pin": 6, "name": "Pin 6: DSR", "type": "OTHER", "col": COL_OTHER, "note": "Data Set Ready (Modem / Urządzenie gotowe)"},
            {"pin": 7, "name": "Pin 7: RTS", "type": "UART", "col": COL_UART, "note": "Request To Send (Żądanie nadawania sprzętowego)"},
            {"pin": 8, "name": "Pin 8: CTS", "type": "UART", "col": COL_UART, "note": "Clear To Send (Zezwolenie na nadawanie sprzętowe)"},
            {"pin": 9, "name": "Pin 9: RI", "type": "OTHER", "col": COL_OTHER, "note": "Ring Indicator (Sygnał dzwonienia modemu)"}
        ]
    }
]


class PinoutsModule(BaseModule):
    name = "Hardware Pinouts Cheat-Sheet"
    short_name = "Pinouty"
    icon = "🔌"
    accent_color = COLOR_PHOSPHOR_GREEN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.selected_board_idx = 0
        self.selected_pin_idx = 0
        self.filter_category = 0  # 0: Wszystkie, 1: I2C, 2: SPI, 3: UART, 4: POWER/GND, 5: GPIO/PWM
        self.categories = ["Wszystkie", "I2C", "SPI", "UART", "POWER", "GPIO"]

    def get_hotkey_hints(self):
        cat_name = self.categories[self.filter_category]
        return [
            ("L1/R1", "Moduły"),
            ("D-Pad L/P", "Zmiana płytki"),
            ("D-Pad G/D", "Wybór pinu"),
            ("A", f"Filtr: {cat_name}"),
            ("X", "Reset wyboru")
        ]

    def render(self, canvas):
        curr_board = BOARDS_DATA[self.selected_board_idx]
        pins = curr_board["pins"]

        if self.selected_pin_idx >= len(pins):
            self.selected_pin_idx = 0

        # Main Layout: Board diagram on Left (x=32, y=66, w=480, h=634)
        canvas.draw_card(
            32, 66, 480, 634,
            title="SCHEMAT WIZUALNY PINOUTU",
            subtitle=f"Płytka: {curr_board['short']}  ({self.selected_board_idx + 1}/{len(BOARDS_DATA)})",
            border_color=self.accent_color
        )

        bx = 48
        by = 118
        bw = 448

        # Board Switcher Pills at top
        tab_x = bx
        for i, b in enumerate(BOARDS_DATA):
            is_cur = (i == self.selected_board_idx)
            lbl = b["short"]
            tw = len(lbl) * 8 + 14
            pill_col = (36, 48, 64) if is_cur else (20, 24, 32)
            out_col = COLOR_PHOSPHOR_GREEN if is_cur else COLOR_BORDER
            canvas.draw.rounded_rectangle([(tab_x, by), (tab_x + tw, by + 24)], radius=4, fill=pill_col, outline=out_col)
            canvas.draw.text((tab_x + 6, by + 5), lbl, fill=COLOR_TEXT_PRIMARY if is_cur else COLOR_TEXT_MUTED, font=get_font(10, bold=is_cur))
            tab_x += tw + 6

        # Pin List / Header Representation
        list_y = by + 36
        pin_h = 24
        visible_pins = min(18, len(pins))

        font_pin_num = get_font(11, bold=True)
        font_pin_name = get_font(12, bold=False)

        # Draw physical header slot
        canvas.draw.rounded_rectangle([(bx, list_y), (bx + bw, list_y + 440)], radius=8, fill=(16, 20, 26), outline=COLOR_BORDER)

        start_p = max(0, min(self.selected_pin_idx - 8, len(pins) - visible_pins))

        cur_py = list_y + 10
        for p_i in range(start_p, min(len(pins), start_p + visible_pins)):
            pin_data = pins[p_i]
            is_active_pin = (p_i == self.selected_pin_idx)
            p_col = pin_data["col"]

            # Filter highlight check
            is_highlighted = True
            if self.filter_category > 0:
                target_cat = self.categories[self.filter_category]
                if target_cat == "POWER":
                    is_highlighted = pin_data["type"] in ("POWER", "GND")
                else:
                    is_highlighted = (pin_data["type"] == target_cat)

            row_bg = (32, 46, 62) if is_active_pin else ((22, 28, 36) if p_i % 2 == 0 else (18, 22, 30))
            if not is_highlighted:
                row_bg = (14, 18, 24)

            canvas.draw.rounded_rectangle([(bx + 8, cur_py), (bx + bw - 8, cur_py + pin_h)],
                                          radius=4, fill=row_bg, outline=COLOR_CYBER_CYAN if is_active_pin else (40, 48, 58), width=2 if is_active_pin else 1)

            # Colored Pin Dot
            dot_color = p_col if is_highlighted else (60, 68, 78)
            canvas.draw.ellipse([(bx + 18, cur_py + 5), (bx + 32, cur_py + 19)], fill=dot_color, outline=(240, 240, 240) if is_active_pin else None)

            # Pin #
            pnum_str = f"#{pin_data['pin']:<2}"
            canvas.draw.text((bx + 40, cur_py + 4), pnum_str, fill=COLOR_TEXT_PRIMARY if is_highlighted else COLOR_TEXT_MUTED, font=font_pin_num)

            # Pin Name
            pname_col = COLOR_TEXT_PRIMARY if is_highlighted else COLOR_TEXT_MUTED
            if is_active_pin:
                pname_col = COLOR_CYBER_CYAN
            canvas.draw.text((bx + 76, cur_py + 4), pin_data["name"][:26], fill=pname_col, font=font_pin_name)

            # Type badge on right
            t_col = p_col if is_highlighted else (40, 48, 56)
            canvas.draw_badge(bx + bw - 78, cur_py + 2, pin_data["type"], bg_color=t_col, text_color=COLOR_TEXT_PRIMARY)

            cur_py += pin_h + 1

        # Scrollbar / Pos hint
        canvas.draw.text((bx + 12, list_y + 450), f"Pozycja: {self.selected_pin_idx + 1} z {len(pins)} pinów  (D-Pad G/D przewija)", fill=COLOR_TEXT_MUTED, font=get_font(11, bold=False))

        # ----------------------------------------------------------------------
        # Right Panel: Selected Pin Deep Dive & Board Electrical Notes (x=526, y=66, w=466, h=634)
        # ----------------------------------------------------------------------
        canvas.draw_card(
            526, 66, 466, 634,
            title="SPECYFIKACJA PINU & ELEKTRYKA",
            subtitle=curr_board["name"],
            border_color=COLOR_BORDER
        )

        rx = 542
        ry = 118
        rw = 434

        sel_pin = pins[self.selected_pin_idx]

        # Pin Highlight Box
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + 160)], radius=10, fill=(20, 26, 36), outline=sel_pin["col"], width=2)

        # Pin Number & Name Big
        canvas.draw.text((rx + 16, ry + 14), f"PIN #{sel_pin['pin']} : {sel_pin['name']}", fill=COLOR_TEXT_PRIMARY, font=get_font(18, bold=True))
        canvas.draw_badge(rx + 16, ry + 44, f"TYP: {sel_pin['type']}", bg_color=sel_pin["col"], text_color=COLOR_TEXT_PRIMARY)

        canvas.draw.line([(rx + 16, ry + 78), (rx + rw - 16, ry + 78)], fill=COLOR_BORDER, width=1)

        # Pin detailed notes
        canvas.draw.text((rx + 16, ry + 90), "FUNKCJA I OPIS:", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=True))
        canvas.draw.text((rx + 16, ry + 110), sel_pin["note"], fill=COLOR_CYBER_CYAN, font=get_font(13, bold=False))

        # Electrical Warning Box
        warn_y = ry + 174
        canvas.draw.rounded_rectangle([(rx, warn_y), (rx + rw, warn_y + 90)], radius=8, fill=(36, 24, 18), outline=COLOR_FLIPPER_AMBER, width=1)
        canvas.draw.text((rx + 14, warn_y + 10), "⚠️ ZASADY BEZPIECZEŃSTWA ELEKTRYCZNEGO", fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))
        canvas.draw.text((rx + 14, warn_y + 32), curr_board["power_warning"][:130], fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=False))
        if len(curr_board["power_warning"]) > 130:
            canvas.draw.text((rx + 14, warn_y + 50), curr_board["power_warning"][130:], fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=False))

        # Color Legend Box
        leg_y = warn_y + 104
        canvas.draw.rounded_rectangle([(rx, leg_y), (rx + rw, leg_y + 240)], radius=8, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((rx + 14, leg_y + 12), "LEGENDA KOLORÓW MAGISTRALI I STANDARDÓW", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))
        canvas.draw.line([(rx + 14, leg_y + 32), (rx + rw - 14, leg_y + 32)], fill=COLOR_BORDER, width=1)

        legend_items = [
            (COL_5V, "Zasilanie 5.0V (VBUS / Raw Power)"),
            (COL_3V3, "Zasilanie 3.3V (Regulated Logic Power)"),
            (COL_GND, "Masa układowa (Ground 0V)"),
            (COL_I2C, "I2C (SDA dane, SCL zegar, pull-up)"),
            (COL_SPI, "SPI (MOSI, MISO, SCLK, Chip Select)"),
            (COL_UART, "UART Serial (TX nadawanie, RX odbiór)"),
            (COL_GPIO, "GPIO / PWM / ADC przetwornik analogowy")
        ]

        leg_row_y = leg_y + 44
        for l_col, l_desc in legend_items:
            canvas.draw.ellipse([(rx + 16, leg_row_y + 2), (rx + 28, leg_row_y + 14)], fill=l_col)
            canvas.draw.text((rx + 36, leg_row_y), l_desc, fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=False))
            leg_row_y += 26

    def handle_input(self, event: str) -> bool:
        curr_board = BOARDS_DATA[self.selected_board_idx]
        pins = curr_board["pins"]

        if event == "UP":
            if self.selected_pin_idx > 0:
                self.selected_pin_idx -= 1
                return True
        elif event == "DOWN":
            if self.selected_pin_idx < len(pins) - 1:
                self.selected_pin_idx += 1
                return True
        elif event == "LEFT":
            self.selected_board_idx = (self.selected_board_idx - 1) % len(BOARDS_DATA)
            self.selected_pin_idx = 0
            return True
        elif event == "RIGHT":
            self.selected_board_idx = (self.selected_board_idx + 1) % len(BOARDS_DATA)
            self.selected_pin_idx = 0
            return True
        elif event == "BTN_A":
            # Cycle filter category
            self.filter_category = (self.filter_category + 1) % len(self.categories)
            return True
        elif event == "BTN_X":
            self.filter_category = 0
            self.selected_pin_idx = 0
            return True
        return False
