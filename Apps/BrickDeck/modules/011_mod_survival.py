"""
BrickDeck Module: Tactical Survival & Off-Grid Platform (mod_survival.py)
Extensible, data-driven survival field manual and interactive off-grid utility suite.
Features:
- Dynamic discovery of JSON and Markdown (.md) guides from data/survival/
- Interactive offline survival calculators (WHO ORS, Battery Runtime, Solar Compass, Water Reserves)
- Tactical Knots ASCII atlas
- Optical SOS / Beacon / Lantern emergency flasher
- 100% standalone and offline, zero-dongle.
"""

import os
import math
import time
from typing import List, Dict, Tuple, Optional, Any

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN, COLOR_STATUS_ERR
)
from core.canvas import get_font
from core.i18n import t
from core.survival_engine import SurvivalEngine


class SurvivalModule(BaseModule):
    name = "Tactical Survival & Off-Grid Platform"
    short_name = "Survival"
    icon = "🏕️"
    accent_color = COLOR_PHOSPHOR_GREEN

    def __init__(self, app_context=None):
        super().__init__(app_context)

        # Initialize survival data engine
        self.engine = SurvivalEngine()

        # Navigation state
        self.cat_idx = 0
        self.article_idx = 0
        self.scroll_y = 0
        self.reading_mode = False

        # Status notification message (e.g. after database reload)
        self.status_msg = ""
        self.status_msg_timer = 0.0

        # Emergency Flasher State
        self.flasher_active = False
        self.flasher_mode = 0  # 0: SOS Morse, 1: Beacon (100ms/2s), 2: High White Lantern
        self.flasher_step = 0
        self.last_flash_time = 0.0

        # Interactive Tools State
        self.tool_idx = 0
        self.tools_list = [
            {"id": "ors", "name": "Kalkulator WHO ORS (Elektrolity)", "icon": "🧪"},
            {"id": "battery", "name": "Magazyn Energii & Czas Pracy", "icon": "🔋"},
            {"id": "compass", "name": "Kompas Słoneczny & Zegarkowy", "icon": "🧭"},
            {"id": "water", "name": "Planer Zapasów Wody Pitnej", "icon": "💧"},
            {"id": "knots", "name": "Atlas Węzłów Ratowniczych", "icon": "🪢"}
        ]

        # Tool 1: ORS state
        self.ors_volumes = [0.5, 1.0, 1.5, 2.0, 5.0]
        self.ors_vol_idx = 1  # 1.0 L default
        self.ors_patients = [
            ("Dorosły (>30 kg)", 1.0, 1000),
            ("Dziecko (10-30 kg)", 0.6, 500),
            ("Niemowlę (<10 kg)", 0.3, 250)
        ]
        self.ors_patient_idx = 0

        # Tool 2: Battery Runtime state
        self.batteries = [
            ("Akumulator Samochodowy 12V 50Ah", 600.0, "Ołowiowy 12V"),
            ("Akumulator AGM Alarm 12V 7Ah", 84.0, "AGM 12V"),
            ("Powerbank USB 20000mAh 3.7V", 74.0, "Li-Poly 3.7V"),
            ("Ogniwo Li-Ion 18650 3000mAh", 11.1, "Li-Ion 3.7V"),
            ("4x AA NiMH Eneloop 2000mAh", 9.6, "NiMH 4.8V")
        ]
        self.batt_idx = 0
        self.loads = [
            ("Konsola TrimUI Brick (Ekran 40%)", 2.0),
            ("Smartfon (Szybkie ładowanie 5V)", 5.0),
            ("Radio PMR446 (Nasłuch / Nadawanie)", 1.2),
            ("Latarka Czołowa LED (High)", 1.5),
            ("Latarka Czołowa LED (Low / Eco)", 0.2)
        ]
        self.load_idx = 0

        # Tool 3: Sun Compass state
        self.compass_hour = 14  # 14:00 default
        self.compass_is_dst = True  # Czas letni UTC+2
        self.compass_hemisphere_north = True  # Półkula Północna

        # Tool 4: Water Reserves state
        self.water_persons = 2
        self.water_days = 7
        self.water_modes = [
            ("Umiarkowane warunki (2.5 L/os/dzień)", 2.5),
            ("Upał / Ciężki wysiłek (4.5 L/os/dzień)", 4.5),
            ("Ścisłe racjonowanie (1.5 L/os/dzień)", 1.5)
        ]
        self.water_mode_idx = 0

        # Tool 5: Tactical Knots state
        self.knot_idx = 0
        self.knots_data = [
            {
                "name": "WĘZEŁ RATOWNICZY / TATRZAŃSKI (BOWLINE)",
                "alias": "Król Węzłów – Pętla nie zaciskająca się",
                "strength": "70% wytrzymałości liny",
                "use": "Asekuracja człowieka, wyciąganie poszkodowanego, ucho cumownicze, pętla ratunkowa.",
                "ascii": [
                    "       ___             ",
                    "      /   \\   (WĄŻ)   ",
                    "  ---(  O  )----->     ",
                    "      \\___/            ",
                    "     JEZIORKO & DRZEWO "
                ],
                "steps": [
                    "1. Zrób małą pętelkę na linie głównej (to jest 'jeziorko').",
                    "2. Koniec roboczy liny ('wąż') wychodzi od dołu z jeziorka.",
                    "3. Wąż okrąża od tyłu linę główną ('drzewo').",
                    "4. Wąż nurkuje z powrotem w to samo jeziorko.",
                    "5. Zaciągnij pętlę – węzeł NIGDY nie zaciśnie się pod ciężarem!"
                ]
            },
            {
                "name": "WYBLINKA (CLOVE HITCH)",
                "alias": "Mocowanie do drzewa, rury, żerdzi",
                "strength": "60% wytrzymałości liny",
                "use": "Budowa szałasów, pionierka obozowa, tratwy, rozpoczęcie oplotów krzyżowych.",
                "ascii": [
                    "     //=====//         ",
                    "    //  X   //         ",
                    "   //======//  (SŁUP)  ",
                    "  PODWÓJNY OPLOT       "
                ],
                "steps": [
                    "1. Owiń linę wokół pnia drzewa lub rury.",
                    "2. Skrzyżuj linę tworząc literę 'X' na powierzchni pnia.",
                    "3. Zrób kolejny obrót i przełóż koniec roboczy pod ostatnim oplotem.",
                    "4. Zaciągnij oba końce. Trzyma pewnie pod stałym naciągiem."
                ]
            },
            {
                "name": "WĘZEŁ PRUSIKA / ZACISKOWY (TAUT-LINE HITCH)",
                "alias": "Samozaciskowy regulator odciągów",
                "strength": "75% wytrzymałości liny",
                "use": "Regulacja naciągu plandeki, tropiku namiotu, hamaka bez rozwiązywania.",
                "ascii": [
                    "  ====(@@@)==========> ",
                    "    OPLOTY ZACISKOWE   ",
                    "  PRZESUWNY W JEDNĄ    ",
                    "  STRONĘ POD NACISKIEM "
                ],
                "steps": [
                    "1. Owiń koniec liny wokół odciągu lub drzewa.",
                    "2. Zrób dwa pełne oploty roboczym końcem WEWNĄTRZ pętli.",
                    "3. Wyprowadź koniec i zrób jeden oplot na zewnątrz pętli.",
                    "4. Przesuwaj węzeł dłonią, by napiąć linkę – pod obciążeniem blokuje się sam!"
                ]
            },
            {
                "name": "WĘZEŁ SZOTOWY (SHEET BEND)",
                "alias": "Łączenie dwóch lin o RÓŻNEJ grubości",
                "strength": "65% wytrzymałości liny",
                "use": "Bezpieczne łączenie cienkiego sznurka z grubą liną, łączenie lin z tkaniną.",
                "ascii": [
                    "  GRUBY:  ====)        ",
                    "  CIENKI: ----(==#==>  ",
                    "  NIE ROZŁĄCZA SIĘ!    "
                ],
                "steps": [
                    "1. Zegnij grubszą linę w zwykłą pętlę (bight).",
                    "2. Przełóż cieńszą linę od dołu przez tę pętlę.",
                    "3. Owiń cieńszą linę wokół OBU ramion grubej pętli.",
                    "4. Przełóż koniec cieńszej liny pod nią samą (nie przez pętlę).",
                    "5. Zaciągnij – nie ślizga się nawet przy dużej różnicy średnic!"
                ]
            },
            {
                "name": "WĘZEŁ PŁASKI (SQUARE / REEF KNOT)",
                "alias": "Wiązanie bandaży i jednakowych lin",
                "strength": "50% wytrzymałości liny",
                "use": "Pierwsza pomoc, wiązanie chust trójkątnych, pakunków (NIE używać do asekuracji!).",
                "ascii": [
                    "  ---\\---/---          ",
                    "      \\ /              ",
                    "  ---/---\\---          ",
                    "  PRAWA NA LEWĄ, LEWA  ",
                    "  NA PRAWĄ             "
                ],
                "steps": [
                    "1. Chwyć dwa końce tej samej liny lub bandaża.",
                    "2. Załóż prawy koniec na lewy i przewlecz (półwęzeł).",
                    "3. Następnie załóż lewy koniec na prawy i przewlecz.",
                    "4. Oba końce leżą równolegle do liny macierzystej. Płaski pod opatrunkiem."
                ]
            }
        ]

    def get_hotkey_hints(self):
        cats = self.engine.get_categories()
        cur_cat = cats[self.cat_idx]["id"] if self.cat_idx < len(cats) else "water"

        if self.flasher_active:
            mode_names = ["SOS Morse", "Stroboskop Beacon", "Latarka Biała"]
            return [
                ("X", "Flasher: WYŁĄCZ"),
                ("Y", f"Tryb: {mode_names[self.flasher_mode]}"),
                ("B", "Powrót")
            ]

        if cur_cat == "tools":
            return [
                ("L1/R1", "Kategoria"),
                ("D-Pad G/D", "Wybierz Narzędzie"),
                ("D-Pad L/P", "Zmień Wartość"),
                ("X", "Opcja / Tryb"),
                ("Y", "Odśwież Bazę"),
                ("A", "Akcja")
            ]

        if self.reading_mode:
            return [
                ("D-Pad G/D", "Przewiń Artykuł"),
                ("D-Pad L/P", "Szybki Skok"),
                ("B", "Lista Artykułów"),
                ("X", "Flasher SOS"),
                ("Y", "Odśwież Bazę")
            ]

        return [
            ("L1/R1", "Kategoria"),
            ("D-Pad G/D", "Wybierz Poradnik"),
            ("A", "Czytaj Pełny Tekst"),
            ("X", "Flasher SOS"),
            ("Y", "Skanuj Pliki (.md/.json)")
        ]

    def update(self, dt: float):
        now = time.time()

        # Handle SOS / Beacon flasher pulsing
        if self.flasher_active:
            if self.flasher_mode == 0:
                # Morse SOS sequence: 3 short, 3 long, 3 short, pause
                # 18 steps total, interval ~0.3s
                if now - self.last_flash_time > 0.30:
                    self.flasher_step = (self.flasher_step + 1) % 18
                    self.last_flash_time = now
            elif self.flasher_mode == 1:
                # Beacon: 100ms flash every 2.0s
                # Step 0 = flash, Steps 1..19 = dark
                if now - self.last_flash_time > 0.10:
                    self.flasher_step = (self.flasher_step + 1) % 20
                    self.last_flash_time = now

        # Clear temporary status banner after 3 seconds
        if self.status_msg and (now - self.status_msg_timer > 3.0):
            self.status_msg = ""

    def render(self, canvas):
        now = time.time()

        # -------------------------------------------------------------
        # EMERGENCY FLASHER OVERLAY
        # -------------------------------------------------------------
        if self.flasher_active:
            is_lit = False
            if self.flasher_mode == 0:
                # Morse SOS lit frames:
                # S: 0, 2, 4 (short)
                # O: 6,7, 9,10, 12,13 (long)
                # S: 15, 17, 19
                is_lit = (self.flasher_step in (0, 2, 4, 6, 7, 9, 10, 12, 13, 15, 17))
            elif self.flasher_mode == 1:
                is_lit = (self.flasher_step == 0)
            elif self.flasher_mode == 2:
                is_lit = True  # Steady 100% white lantern

            bg = (255, 255, 255) if is_lit else (12, 14, 18)
            fg = (0, 0, 0) if is_lit else (255, 255, 255)

            canvas.draw.rectangle([(0, 52), (1024, 716)], fill=bg)

            mode_titles = [
                "🆘 AWARYJNY NADAJNIK SOS MORSE'A 🆘",
                "🚨 LATARKA POZYCYJNA (BEACON STROBE) 🚨",
                "💡 LATARKA RATUNKOWA 100% BIAŁY EKRAN 💡"
            ]
            mode_sub = [
                "Pulsuje międzynarodowym kodem SOS:  •••  ———  •••",
                "Błysk co 2 sekundy – maksymalna oszczędność baterii w terenie",
                "Równomierne białe światło oświetlające wnętrze namiotu lub pokoju"
            ]

            canvas.draw.text((512, 330), mode_titles[self.flasher_mode], fill=fg, font=get_font(26, bold=True), anchor="mm")
            canvas.draw.text((512, 380), mode_sub[self.flasher_mode], fill=fg, font=get_font(15, bold=False), anchor="mm")
            canvas.draw.text((512, 450), "[X]: Wyłącz  |  [Y]: Przełącz Tryb  |  [B]: Powrót", fill=fg, font=get_font(13, bold=True), anchor="mm")
            return

        # -------------------------------------------------------------
        # TOP CATEGORY CAROUSEL TABS (y=58, h=44)
        # -------------------------------------------------------------
        categories = self.engine.get_categories()
        if not categories:
            return

        self.cat_idx = max(0, min(len(categories) - 1, self.cat_idx))
        active_cat = categories[self.cat_idx]

        cat_y = 60
        cat_h = 38
        cx = 30

        for i, cat in enumerate(categories):
            is_active = (i == self.cat_idx)
            lbl = f"{cat['icon']} {cat['name'].split('&')[0].strip()}"
            font_tab = get_font(12, bold=is_active)
            tw = len(lbl) * 8 + 16

            tab_col = tuple(cat.get("color", [0, 210, 255]))
            fill_c = (28, 38, 48) if is_active else (18, 22, 28)
            border_c = tab_col if is_active else (38, 46, 58)

            canvas.draw.rounded_rectangle([(cx, cat_y), (cx + tw, cat_y + cat_h)], radius=6, fill=fill_c, outline=border_c, width=2 if is_active else 1)
            canvas.draw.text((cx + 8, cat_y + 11), lbl, fill=COLOR_TEXT_PRIMARY if is_active else COLOR_TEXT_MUTED, font=font_tab)

            cx += tw + 6
            if cx > 980:
                break

        # Status notification banner (if recently reloaded or scanned)
        if self.status_msg:
            canvas.draw_badge(760, 64, self.status_msg, bg_color=(20, 60, 35), text_color=COLOR_PHOSPHOR_GREEN)

        # -------------------------------------------------------------
        # MAIN BODY (y=108, h=598)
        # -------------------------------------------------------------
        cat_id = active_cat["id"]

        if cat_id == "tools":
            self._render_tools_view(canvas)
        else:
            self._render_guides_view(canvas, active_cat)

    # -----------------------------------------------------------------
    # RENDER VIEW: SURVIVAL GUIDES & ARTICLES
    # -----------------------------------------------------------------
    def _render_guides_view(self, canvas, active_cat: Dict[str, Any]):
        guides = self.engine.get_guides_for_category(active_cat["id"])
        cat_col = tuple(active_cat.get("color", [0, 230, 118]))

        # Main Card Frame
        canvas.draw_card(
            x=25, y=106, w=974, h=600,
            title=f"{active_cat['icon']} {active_cat['name'].upper()} [BAZA WIEDZY]",
            subtitle=f"{active_cat['badge']}  |  {len(guides)} dostępnych poradników  |  Działa w 100% offline",
            border_color=cat_col
        )

        # -------------------------------------------------------------
        # Left Column: Articles Index (x=40, y=156, w=330, h=534)
        # -------------------------------------------------------------
        lx, ly, lw, lh = 40, 156, 330, 534
        canvas.draw.rounded_rectangle([(lx, ly), (lx + lw, ly + lh)], radius=8, fill=(16, 20, 26), outline=COLOR_BORDER, width=1)
        canvas.draw.text((lx + 14, ly + 12), f"ROZDZIAŁY ({len(guides)})", fill=COLOR_PHOSPHOR_GREEN, font=get_font(12, bold=True))
        canvas.draw.line([(lx + 14, ly + 32), (lx + lw - 14, ly + 32)], fill=COLOR_BORDER, width=1)

        if not guides:
            canvas.draw.text((lx + 20, ly + 50), "Brak poradników w tej kategorii.", fill=COLOR_TEXT_MUTED, font=get_font(12))
            canvas.draw.text((lx + 20, ly + 80), "Wrzuć plik .md lub .json do:", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
            canvas.draw.text((lx + 20, ly + 105), "data/survival/custom/", fill=COLOR_CYBER_CYAN, font=get_font(11))
            canvas.draw.text((lx + 20, ly + 130), "i naciśnij [Y] aby odświeżyć!", fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))
            return

        self.article_idx = max(0, min(len(guides) - 1, self.article_idx))
        active_guide = guides[self.article_idx]

        item_y = ly + 42
        for idx, g in enumerate(guides):
            is_sel = (idx == self.article_idx)
            is_custom = g.get("is_custom", False)

            fill_c = (26, 38, 34) if is_sel else (20, 24, 32)
            outline_c = cat_col if is_sel else (34, 42, 54)
            canvas.draw.rounded_rectangle([(lx + 8, item_y), (lx + lw - 8, item_y + 64)], radius=6, fill=fill_c, outline=outline_c, width=2 if is_sel else 1)

            # Title
            t_col = COLOR_TEXT_PRIMARY if is_sel else COLOR_TEXT_SECONDARY
            title_text = g["title"]
            if len(title_text) > 34:
                title_text = title_text[:32] + "..."
            canvas.draw.text((lx + 16, item_y + 8), title_text, fill=t_col, font=get_font(11, bold=is_sel))

            # Badges
            b_text = g.get("badge", "PORADNIK")
            canvas.draw.text((lx + 16, item_y + 36), b_text, fill=COLOR_CYBER_CYAN if is_sel else COLOR_TEXT_MUTED, font=get_font(9, bold=True))

            if is_custom:
                canvas.draw_badge(lx + lw - 100, item_y + 34, "CUSTOM MD", bg_color=(45, 30, 60), text_color=COLOR_NEON_PINK)

            item_y += 72
            if item_y > ly + lh - 70:
                break

        # Bottom hint on left column
        canvas.draw.text((lx + 14, ly + lh - 24), "[D-Pad G/D]: Wybór  |  [A]: Czytaj", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # -------------------------------------------------------------
        # Right Column: Article Reader (x=385, y=156, w=598, h=534)
        # -------------------------------------------------------------
        rx, ry, rw, rh = 385, 156, 598, 534
        reader_fill = (14, 18, 24) if not self.reading_mode else (12, 16, 22)
        reader_border = cat_col if self.reading_mode else COLOR_BORDER
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=8, fill=reader_fill, outline=reader_border, width=2 if self.reading_mode else 1)

        # Reader Title Bar
        canvas.draw.text((rx + 18, ry + 12), active_guide["title"][:48], fill=COLOR_FLIPPER_AMBER, font=get_font(13, bold=True))
        canvas.draw_badge(rx + rw - 150, ry + 10, active_guide.get("badge", "SURVIVAL"), bg_color=(20, 36, 28), text_color=COLOR_PHOSPHOR_GREEN)
        canvas.draw.line([(rx + 16, ry + 36), (rx + rw - 16, ry + 36)], fill=COLOR_BORDER, width=1)

        # Content Rendering
        parsed_lines = active_guide.get("parsed_lines", [])
        total_lines = len(parsed_lines)
        visible_count = 19

        max_scroll = max(0, total_lines - visible_count)
        self.scroll_y = max(0, min(max_scroll, self.scroll_y))
        visible_slice = parsed_lines[self.scroll_y:self.scroll_y + visible_count]

        line_y = ry + 46
        f_norm = get_font(11, bold=False)
        f_bold = get_font(11, bold=True)
        f_head = get_font(12, bold=True)

        for text_line, style in visible_slice:
            if style == "empty":
                line_y += 8
                continue

            if style == "header":
                canvas.draw.text((rx + 18, line_y), text_line, fill=COLOR_FLIPPER_AMBER, font=f_head)
                canvas.draw.line([(rx + 18, line_y + 18), (rx + rw - 30, line_y + 18)], fill=(70, 50, 20), width=1)
                line_y += 24
            elif style == "subheader":
                canvas.draw.text((rx + 18, line_y), text_line, fill=COLOR_CYBER_CYAN, font=f_bold)
                line_y += 20
            elif style == "warn":
                canvas.draw.rounded_rectangle([(rx + 14, line_y - 2), (rx + rw - 24, line_y + 18)], radius=4, fill=(45, 18, 20))
                canvas.draw.text((rx + 20, line_y), text_line, fill=(255, 100, 100), font=f_bold)
                line_y += 22
            elif style == "tip":
                canvas.draw.rounded_rectangle([(rx + 14, line_y - 2), (rx + rw - 24, line_y + 18)], radius=4, fill=(18, 35, 30))
                canvas.draw.text((rx + 20, line_y), text_line, fill=COLOR_PHOSPHOR_GREEN, font=f_norm)
                line_y += 22
            elif style == "step":
                canvas.draw.text((rx + 24, line_y), text_line, fill=COLOR_TEXT_PRIMARY, font=f_norm)
                line_y += 20
            elif style == "bullet":
                canvas.draw.text((rx + 24, line_y), text_line, fill=COLOR_TEXT_SECONDARY, font=f_norm)
                line_y += 20
            else:
                canvas.draw.text((rx + 18, line_y), text_line, fill=COLOR_TEXT_SECONDARY, font=f_norm)
                line_y += 20

        # Scrollbar on right edge
        if total_lines > visible_count:
            scroll_pct = self.scroll_y / float(max_scroll)
            bar_track_h = rh - 80
            bar_thumb_h = max(24, int(bar_track_h * (visible_count / float(total_lines))))
            thumb_y = int(ry + 46 + scroll_pct * (bar_track_h - bar_thumb_h))
            canvas.draw.rounded_rectangle([(rx + rw - 10, thumb_y), (rx + rw - 5, thumb_y + bar_thumb_h)], radius=3, fill=COLOR_CYBER_CYAN)

        # Bottom status hint
        if self.reading_mode:
            canvas.draw.text((rx + 18, ry + rh - 22), "TRYB CZYTANIA: [D-Pad G/D] przewija  |  [B] wyjście do listy", fill=COLOR_PHOSPHOR_GREEN, font=get_font(10, bold=True))
        else:
            canvas.draw.text((rx + 18, ry + rh - 22), f"Plik: {os.path.basename(active_guide.get('file_path', ''))}  |  [A]: Aktywuj pełny czytnik", fill=COLOR_TEXT_MUTED, font=get_font(10))

    # -----------------------------------------------------------------
    # RENDER VIEW: INTERACTIVE SURVIVAL TOOLS
    # -----------------------------------------------------------------
    def _render_tools_view(self, canvas):
        canvas.draw_card(
            x=25, y=106, w=974, h=600,
            title="🧮 INTERAKTYWNY PRZYBORNIK I KALKULATORY PRZETRWANIA",
            subtitle="Kalkulatory offline, symulator kompasu słonecznego, atlas węzłów, zarządzanie energią",
            border_color=(187, 134, 252)
        )

        # Left Column: Tools List (x=40, y=156, w=300, h=534)
        lx, ly, lw, lh = 40, 156, 300, 534
        canvas.draw.rounded_rectangle([(lx, ly), (lx + lw, ly + lh)], radius=8, fill=(16, 20, 26), outline=COLOR_BORDER, width=1)
        canvas.draw.text((lx + 14, ly + 12), "NARZĘDZIA PRZETRWANIA", fill=(187, 134, 252), font=get_font(12, bold=True))
        canvas.draw.line([(lx + 14, ly + 32), (lx + lw - 14, ly + 32)], fill=COLOR_BORDER, width=1)

        tool_y = ly + 46
        for idx, t_info in enumerate(self.tools_list):
            is_sel = (idx == self.tool_idx)
            fill_c = (34, 28, 48) if is_sel else (20, 24, 32)
            outline_c = (187, 134, 252) if is_sel else (34, 42, 54)

            canvas.draw.rounded_rectangle([(lx + 8, tool_y), (lx + lw - 8, tool_y + 54)], radius=6, fill=fill_c, outline=outline_c, width=2 if is_sel else 1)
            canvas.draw.text((lx + 16, tool_y + 16), f"{t_info['icon']}  {t_info['name']}", fill=COLOR_TEXT_PRIMARY if is_sel else COLOR_TEXT_SECONDARY, font=get_font(11, bold=is_sel))

            tool_y += 62

        canvas.draw.text((lx + 14, ly + lh - 24), "[D-Pad G/D]: Wybór narzędzia", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # Right Column: Tool Interface (x=355, y=156, w=628, h=534)
        rx, ry, rw, rh = 355, 156, 628, 534
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=8, fill=(14, 18, 24), outline=COLOR_BORDER, width=1)

        # Dispatch selected tool
        cur_tool_id = self.tools_list[self.tool_idx]["id"]
        if cur_tool_id == "ors":
            self._render_tool_ors(canvas, rx, ry, rw, rh)
        elif cur_tool_id == "battery":
            self._render_tool_battery(canvas, rx, ry, rw, rh)
        elif cur_tool_id == "compass":
            self._render_tool_compass(canvas, rx, ry, rw, rh)
        elif cur_tool_id == "water":
            self._render_tool_water(canvas, rx, ry, rw, rh)
        elif cur_tool_id == "knots":
            self._render_tool_knots(canvas, rx, ry, rw, rh)

    # -----------------------------------------------------------------
    # TOOL 1: WHO ORS REHYDRATION CALCULATOR
    # -----------------------------------------------------------------
    def _render_tool_ors(self, canvas, x, y, w, h):
        canvas.draw.text((x + 20, y + 16), "🧪 KALKULATOR DOMOWYCH ELEKTROLITÓW (WHO ORS)", fill=COLOR_FLIPPER_AMBER, font=get_font(14, bold=True))
        canvas.draw_badge(x + w - 160, y + 12, "FORMUŁA 245 mOsm/L", bg_color=(20, 45, 30), text_color=COLOR_PHOSPHOR_GREEN)
        canvas.draw.line([(x + 20, y + 42), (x + w - 20, y + 42)], fill=COLOR_BORDER, width=1)

        cur_vol = self.ors_volumes[self.ors_vol_idx]
        pat_name, pat_mult, pat_dose = self.ors_patients[self.ors_patient_idx]

        sugar_spoons = cur_vol * 6.0
        salt_spoons = cur_vol * 0.5
        potassium_juice = int(cur_vol * 100)  # ml soku

        # Parameter Adjusters
        canvas.draw.rounded_rectangle([(x + 20, y + 55), (x + w - 20, y + 120)], radius=6, fill=(20, 26, 36), outline=(40, 52, 70))
        canvas.draw.text((x + 35, y + 68), f"Objętość wody: {cur_vol:.1f} Litra", fill=COLOR_CYBER_CYAN, font=get_font(13, bold=True))
        canvas.draw.text((x + 35, y + 92), "[D-Pad L/P]: Zmień objętość (0.5L / 1L / 1.5L / 2L / 5L)", fill=COLOR_TEXT_MUTED, font=get_font(11))

        canvas.draw.text((x + 340, y + 68), f"Pacjent: {pat_name}", fill=COLOR_PHOSPHOR_GREEN, font=get_font(13, bold=True))
        canvas.draw.text((x + 340, y + 92), "[X / A]: Przełącz grupę wiekową", fill=COLOR_TEXT_MUTED, font=get_font(11))

        # Big Recipe Cards
        card_w = (w - 60) // 3
        # Sugar
        canvas.draw.rounded_rectangle([(x + 20, y + 135), (x + 20 + card_w, y + 235)], radius=6, fill=(22, 32, 28), outline=COLOR_PHOSPHOR_GREEN)
        canvas.draw.text((x + 35, y + 148), "CUKIER / GLUKOZA", fill=COLOR_PHOSPHOR_GREEN, font=get_font(11, bold=True))
        canvas.draw.text((x + 35, y + 175), f"{sugar_spoons:.1f}", fill=COLOR_TEXT_PRIMARY, font=get_font(26, bold=True))
        canvas.draw.text((x + 35, y + 210), "płaskich łyżeczek (lub miodu)", fill=COLOR_TEXT_SECONDARY, font=get_font(10))

        # Salt
        canvas.draw.rounded_rectangle([(x + 30 + card_w, y + 135), (x + 30 + 2 * card_w, y + 235)], radius=6, fill=(28, 28, 38), outline=COLOR_CYBER_CYAN)
        canvas.draw.text((x + 45 + card_w, y + 148), "SÓL KUCHENNA (NaCl)", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))
        canvas.draw.text((x + 45 + card_w, y + 175), f"{salt_spoons:.2f}", fill=COLOR_TEXT_PRIMARY, font=get_font(26, bold=True))
        canvas.draw.text((x + 45 + card_w, y + 210), "płaskiej łyżeczki", fill=COLOR_TEXT_SECONDARY, font=get_font(10))

        # Potassium
        canvas.draw.rounded_rectangle([(x + 40 + 2 * card_w, y + 135), (x + 40 + 3 * card_w, y + 235)], radius=6, fill=(35, 28, 24), outline=COLOR_FLIPPER_AMBER)
        canvas.draw.text((x + 55 + 2 * card_w, y + 148), "SOK Z CYTRYNY / POTAS", fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))
        canvas.draw.text((x + 55 + 2 * card_w, y + 175), f"{potassium_juice} ml", fill=COLOR_TEXT_PRIMARY, font=get_font(26, bold=True))
        canvas.draw.text((x + 55 + 2 * card_w, y + 210), "lub szczypta soku owocowego", fill=COLOR_TEXT_SECONDARY, font=get_font(10))

        # Medical Advice & Dosage
        canvas.draw.rounded_rectangle([(x + 20, y + 250), (x + w - 20, y + 430)], radius=6, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((x + 35, y + 265), "PROTOKÓŁ PODAWANIA ELEKTROLITÓW:", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))

        canvas.draw.text((x + 35, y + 295), f"• Dawka uderzeniowa (pierwsze 4 godziny): ok. {pat_dose} ml roztworu.", fill=COLOR_PHOSPHOR_GREEN, font=get_font(11))
        canvas.draw.text((x + 35, y + 320), "• Sposób: Pij powoli małymi łykami co 5-10 minut (wypicie duszkiem wywoła wymioty!).", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw.text((x + 35, y + 345), "• Po każdym luźnym stolcu: podaj dodatkowo 100-200 ml roztworu.", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw.text((x + 35, y + 370), "• Uwaga: Cukier jest niezbędny! Bez glukozy jelita nie wchłoną sodu ani wody.", fill=COLOR_STATUS_WARN, font=get_font(11, bold=True))
        canvas.draw.text((x + 35, y + 395), "• Nigdy nie przekraczaj zalecanej dawki soli – nadmiar soli niszczy nerki w odwodnieniu.", fill=(255, 120, 120), font=get_font(11))

        # Bottom Tip
        canvas.draw.text((x + 20, y + h - 25), "💡 Tip: Przegotuj wodę przed wymieszaniem składników. Roztwór zużyj w 24 godziny.", fill=COLOR_TEXT_MUTED, font=get_font(10))

    # -----------------------------------------------------------------
    # TOOL 2: BATTERY RUNTIME CALCULATOR
    # -----------------------------------------------------------------
    def _render_tool_battery(self, canvas, x, y, w, h):
        canvas.draw.text((x + 20, y + 16), "🔋 KALKULATOR POJEMNOŚCI I CZASU PRACY BATERII", fill=COLOR_FLIPPER_AMBER, font=get_font(14, bold=True))
        canvas.draw_badge(x + w - 160, y + 12, "DC-DC STEP-DOWN 85%", bg_color=(30, 40, 20), text_color=COLOR_PHOSPHOR_GREEN)
        canvas.draw.line([(x + 20, y + 42), (x + w - 20, y + 42)], fill=COLOR_BORDER, width=1)

        batt_name, batt_wh, batt_chem = self.batteries[self.batt_idx]
        load_name, load_watts = self.loads[self.load_idx]

        # Calculation (with 85% converter efficiency)
        eff = 0.85
        usable_wh = batt_wh * eff
        runtime_hours = usable_wh / max(load_watts, 0.01)
        runtime_days = runtime_hours / 24.0
        brick_charges = usable_wh / 11.0  # 11 Wh battery

        # Selectors
        canvas.draw.rounded_rectangle([(x + 20, y + 55), (x + w - 20, y + 140)], radius=6, fill=(20, 26, 36), outline=(40, 52, 70))
        canvas.draw.text((x + 35, y + 68), f"ŹRÓDŁO: {batt_name} ({batt_wh:.1f} Wh)", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))
        canvas.draw.text((x + 35, y + 88), "[D-Pad L/P]: Zmień magazyn energii", fill=COLOR_TEXT_MUTED, font=get_font(10))

        canvas.draw.text((x + 35, y + 108), f"ODBIORNIK: {load_name} ({load_watts:.1f} W)", fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))
        canvas.draw.text((x + 35, y + 124), "[X / A]: Przełącz urządzenie odbiorcze", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # Big Result Displays
        canvas.draw.rounded_rectangle([(x + 20, y + 155), (x + (w // 2) - 10, y + 265)], radius=6, fill=(20, 36, 28), outline=COLOR_PHOSPHOR_GREEN)
        canvas.draw.text((x + 35, y + 170), "SZACOWANY CZAS PRACY CIĄGŁEJ", fill=COLOR_PHOSPHOR_GREEN, font=get_font(11, bold=True))
        canvas.draw.text((x + 35, y + 200), f"{runtime_hours:.1f} Godzin", fill=COLOR_TEXT_PRIMARY, font=get_font(24, bold=True))
        canvas.draw.text((x + 35, y + 238), f"czyli ok. {runtime_days:.1f} Dni nieprzerwanej pracy!", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))

        canvas.draw.rounded_rectangle([(x + (w // 2) + 10, y + 155), (x + w - 20, y + 265)], radius=6, fill=(28, 28, 42), outline=COLOR_CYBER_CYAN)
        canvas.draw.text((x + (w // 2) + 25, y + 170), "ŁADOWANIA KONSOLI TRIMUI BRICK", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))
        canvas.draw.text((x + (w // 2) + 25, y + 200), f"{brick_charges:.1f} x", fill=COLOR_TEXT_PRIMARY, font=get_font(24, bold=True))
        canvas.draw.text((x + (w // 2) + 25, y + 238), f"Pełnych ładowań od 0% do 100%", fill=COLOR_TEXT_SECONDARY, font=get_font(11))

        # Technical Details
        canvas.draw.rounded_rectangle([(x + 20, y + 280), (x + w - 20, y + 430)], radius=6, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((x + 35, y + 295), "BILANS ENERGETYCZNY & ZASADY EKSPLOATACJI:", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
        canvas.draw.text((x + 35, y + 325), f"• Pojemność nominalna: {batt_wh:.1f} Wh | Użyteczna po stratach przetwornicy: {usable_wh:.1f} Wh", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw.text((x + 35, y + 350), "• Pobór prądu TrimUI Brick zależy w 70% od podświetlenia ekranu (ustawienie 25% wydłuża czas 2x).", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw.text((x + 35, y + 375), "• Ochrona akumulatora 12V: Nie rozładowuj poniżej 10.5V (ryzyko trwałego uszkodzenia cel).", fill=COLOR_STATUS_WARN, font=get_font(11))
        canvas.draw.text((x + 35, y + 400), "• W temperaturze poniżej 0°C pojemność baterii litowych i kwasowych spada o 30-40%.", fill=(255, 120, 120), font=get_font(11))

    # -----------------------------------------------------------------
    # TOOL 3: SUN & WATCH COMPASS SIMULATOR
    # -----------------------------------------------------------------
    def _render_tool_compass(self, canvas, x, y, w, h):
        canvas.draw.text((x + 20, y + 16), "🧭 KOMPAS SŁONECZNY Z TARCZĄ ZEGARKA", fill=COLOR_FLIPPER_AMBER, font=get_font(14, bold=True))
        dst_str = "CZAS LETNI (UTC+2)" if self.compass_is_dst else "CZAS ZIMOWY (UTC+1)"
        canvas.draw_badge(x + w - 180, y + 12, dst_str, bg_color=(25, 35, 45), text_color=COLOR_CYBER_CYAN)
        canvas.draw.line([(x + 20, y + 42), (x + w - 20, y + 42)], fill=COLOR_BORDER, width=1)

        # Controls banner
        canvas.draw.rounded_rectangle([(x + 20, y + 55), (x + w - 20, y + 115)], radius=6, fill=(20, 26, 36), outline=(40, 52, 70))
        canvas.draw.text((x + 35, y + 68), f"Aktualna godzina: {self.compass_hour:02d}:00", fill=COLOR_PHOSPHOR_GREEN, font=get_font(13, bold=True))
        canvas.draw.text((x + 35, y + 90), "[D-Pad L/P]: Zmień godzinę  |  [X]: Przełącz Czas Letni/Zimowy", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # Draw Visual Analog Clock Compass on left of panel
        clock_cx, clock_cy, clock_r = x + 160, y + 270, 110
        canvas.draw.ellipse([(clock_cx - clock_r, clock_cy - clock_r), (clock_cx + clock_r, clock_cy + clock_r)], outline=COLOR_CYBER_CYAN, width=2, fill=(16, 22, 30))

        # Clock dial marks
        for hr in (12, 3, 6, 9):
            ang = math.radians((hr % 12) * 30 - 90)
            mx = clock_cx + int((clock_r - 16) * math.cos(ang))
            my = clock_cy + int((clock_r - 16) * math.sin(ang))
            canvas.draw.text((mx, my), str(hr), fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=True), anchor="mm")

        # Sun angle: corresponds to hour hand
        hour_val = self.compass_hour % 12
        hour_angle_deg = (hour_val * 30) - 90
        hour_rad = math.radians(hour_angle_deg)

        # Hour Hand (directed at Sun)
        hx = clock_cx + int((clock_r - 28) * math.cos(hour_rad))
        hy = clock_cy + int((clock_r - 28) * math.sin(hour_rad))
        canvas.draw.line([(clock_cx, clock_cy), (hx, hy)], fill=COLOR_FLIPPER_AMBER, width=4)
        canvas.draw.text((hx + 10, hy - 10), "☀️ SŁOŃCE", fill=COLOR_FLIPPER_AMBER, font=get_font(10, bold=True))

        # Bisector angle calculation (South direction)
        # In Northern Hemisphere: bisector between Hour hand and 12:00 (or 1:00 for DST)
        base_ref_hr = 1 if self.compass_is_dst else 12
        base_angle_deg = (base_ref_hr % 12) * 30 - 90

        # Bisector angle
        diff = (hour_angle_deg - base_angle_deg) % 360
        south_angle_deg = base_angle_deg + (diff / 2.0)
        north_angle_deg = (south_angle_deg + 180) % 360

        s_rad = math.radians(south_angle_deg)
        n_rad = math.radians(north_angle_deg)

        # Draw South Line (S)
        sx = clock_cx + int((clock_r - 10) * math.cos(s_rad))
        sy = clock_cy + int((clock_r - 10) * math.sin(s_rad))
        canvas.draw.line([(clock_cx, clock_cy), (sx, sy)], fill=(255, 80, 80), width=3)
        canvas.draw.text((sx, sy), "S", fill=(255, 80, 80), font=get_font(14, bold=True), anchor="mm")

        # Draw North Line (N)
        nx = clock_cx + int((clock_r - 10) * math.cos(n_rad))
        ny = clock_cy + int((clock_r - 10) * math.sin(n_rad))
        canvas.draw.line([(clock_cx, clock_cy), (nx, ny)], fill=COLOR_CYBER_CYAN, width=3)
        canvas.draw.text((nx, ny), "N", fill=COLOR_CYBER_CYAN, font=get_font(14, bold=True), anchor="mm")

        # Center dot
        canvas.draw.ellipse([(clock_cx - 4, clock_cy - 4), (clock_cx + clock_r // 20, clock_cy + clock_r // 20)], fill=(255, 255, 255))

        # Explanatory Steps on right side of clock
        tx = x + 310
        canvas.draw.text((tx, y + 130), "JAK WYZNACZYĆ PÓŁNOC W TERENIE:", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
        canvas.draw.text((tx, y + 160), "1. Trzymaj zegarek poziomo przed sobą.", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw.text((tx, y + 185), "2. Skieruj WSKAZÓWKĘ GODZINOWĄ w stronę Słońca.", fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))
        if self.compass_is_dst:
            canvas.draw.text((tx, y + 210), "3. Czas letni: Znajdź kąt między wskazówką a godziną 1:00.", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        else:
            canvas.draw.text((tx, y + 210), "3. Czas zimowy: Znajdź kąt między wskazówką a godziną 12:00.", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw.text((tx, y + 235), "4. DWUSIECZNA tego kąta wskazuje dokładnie POŁUDNIE (S)!", fill=(255, 100, 100), font=get_font(11, bold=True))
        canvas.draw.text((tx, y + 260), "5. Przeciwny kierunek tej linii to PÓŁNOC (N).", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))

        canvas.draw.rounded_rectangle([(tx, y + 295), (x + w - 20, y + 415)], radius=6, fill=(20, 26, 36), outline=COLOR_BORDER)
        canvas.draw.text((tx + 15, y + 310), "METODA PATYKA I CIENIA (BEZ ZEGARKA):", fill=COLOR_PHOSPHOR_GREEN, font=get_font(11, bold=True))
        canvas.draw.text((tx + 15, y + 335), "• Wbij pionowy patyk w ziemię i zaznacz czubek cienia kamieniem (A).", fill=COLOR_TEXT_SECONDARY, font=get_font(10))
        canvas.draw.text((tx + 15, y + 360), "• Odczekaj 15-20 minut i zaznacz nowy czubek cienia drugim kamieniem (B).", fill=COLOR_TEXT_SECONDARY, font=get_font(10))
        canvas.draw.text((tx + 15, y + 385), "• Linia od punktu A do punktu B wyznacza idealny kierunek WSCHÓD-ZACHÓD!", fill=COLOR_TEXT_PRIMARY, font=get_font(10, bold=True))

    # -----------------------------------------------------------------
    # TOOL 4: WATER RESERVES PLANNER
    # -----------------------------------------------------------------
    def _render_tool_water(self, canvas, x, y, w, h):
        canvas.draw.text((x + 20, y + 16), "💧 PLANER I RACJONOWANIE ZAPASÓW WODY PITNEJ", fill=COLOR_FLIPPER_AMBER, font=get_font(14, bold=True))
        canvas.draw_badge(x + w - 160, y + 12, "MINIMUM: 2.0L / OSOBĘ", bg_color=(20, 35, 45), text_color=COLOR_CYBER_CYAN)
        canvas.draw.line([(x + 20, y + 42), (x + w - 20, y + 42)], fill=COLOR_BORDER, width=1)

        mode_name, per_day = self.water_modes[self.water_mode_idx]
        total_liters = self.water_persons * self.water_days * per_day
        drinking_liters = total_liters * 0.65
        hygiene_liters = total_liters * 0.35
        bottles_5l = math.ceil(total_liters / 5.0)

        # Controls
        canvas.draw.rounded_rectangle([(x + 20, y + 55), (x + w - 20, y + 130)], radius=6, fill=(20, 26, 36), outline=(40, 52, 70))
        canvas.draw.text((x + 35, y + 68), f"Liczba osób: {self.water_persons}  |  Dni kryzysu: {self.water_days} dni", fill=COLOR_CYBER_CYAN, font=get_font(13, bold=True))
        canvas.draw.text((x + 35, y + 88), "[D-Pad L/P]: Zmień osoby  |  [X]: Zmień dni (1-30)", fill=COLOR_TEXT_MUTED, font=get_font(10))

        canvas.draw.text((x + 35, y + 106), f"Warunki: {mode_name}", fill=COLOR_PHOSPHOR_GREEN, font=get_font(11, bold=True))
        canvas.draw.text((x + 350, y + 106), "[Y / A]: Przełącz tryb zużycia", fill=COLOR_TEXT_MUTED, font=get_font(10))

        # Result Cards
        card_w = (w - 60) // 2
        canvas.draw.rounded_rectangle([(x + 20, y + 145), (x + 20 + card_w, y + 265)], radius=6, fill=(18, 36, 42), outline=COLOR_CYBER_CYAN)
        canvas.draw.text((x + 35, y + 160), "WYMAGANY ZAPAS CAŁKOWITY", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))
        canvas.draw.text((x + 35, y + 195), f"{total_liters:.1f} L", fill=COLOR_TEXT_PRIMARY, font=get_font(28, bold=True))
        canvas.draw.text((x + 35, y + 238), f"Masa wody: {total_liters:.0f} kg  |  Butle 5L: {bottles_5l} szt.", fill=COLOR_TEXT_SECONDARY, font=get_font(11))

        canvas.draw.rounded_rectangle([(x + 30 + card_w, y + 145), (x + w - 20, y + 265)], radius=6, fill=(22, 34, 28), outline=COLOR_PHOSPHOR_GREEN)
        canvas.draw.text((x + 45 + card_w, y + 160), "STRUKTURA RACJONOWANIA", fill=COLOR_PHOSPHOR_GREEN, font=get_font(11, bold=True))
        canvas.draw.text((x + 45 + card_w, y + 190), f"Picie bezpośrednie: {drinking_liters:.1f} L", fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))
        canvas.draw.text((x + 45 + card_w, y + 215), f"Gotowanie i higiena: {hygiene_liters:.1f} L", fill=COLOR_TEXT_SECONDARY, font=get_font(12))
        canvas.draw.text((x + 45 + card_w, y + 238), f"Dzienna porcja na osobę: {per_day:.1f} L/dobę", fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))

        # Strategy box
        canvas.draw.rounded_rectangle([(x + 20, y + 280), (x + w - 20, y + 430)], radius=6, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((x + 35, y + 295), "ZASADY PRZETRWANIA Z OGRANICZONĄ WODĄ:", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
        canvas.draw.text((x + 35, y + 325), "• Nie jedz słonych, suchych ani mocno białkowych posiłków (trawienie białka zużywa 3x więcej wody).", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw.text((x + 35, y + 350), "• Oddychaj przez nos, nie przez usta – zmniejsza utratę wilgoci z płuc o 40%.", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw.text((x + 35, y + 375), "• Ogranicz aktywność w ciągu dnia – pracuj fizycznie wyłącznie o świcie i po zmierzchu.", fill=COLOR_TEXT_SECONDARY, font=get_font(11))
        canvas.draw.text((x + 35, y + 400), "• Pamiętaj: Człowiek w upale bez wody traci przytomność już po 48-72 godzinach!", fill=COLOR_STATUS_ERR, font=get_font(11, bold=True))

    # -----------------------------------------------------------------
    # TOOL 5: TACTICAL KNOTS ATLAS
    # -----------------------------------------------------------------
    def _render_tool_knots(self, canvas, x, y, w, h):
        canvas.draw.text((x + 20, y + 16), "🪢 ATLAS WĘZŁÓW RATOWNICZYCH I PIONIERSKICH", fill=COLOR_FLIPPER_AMBER, font=get_font(14, bold=True))
        canvas.draw_badge(x + w - 160, y + 12, "PIONIERKA & LINY", bg_color=(35, 30, 20), text_color=COLOR_FLIPPER_AMBER)
        canvas.draw.line([(x + 20, y + 42), (x + w - 20, y + 42)], fill=COLOR_BORDER, width=1)

        self.knot_idx = max(0, min(len(self.knots_data) - 1, self.knot_idx))
        k = self.knots_data[self.knot_idx]

        # Knot Header & Navigation
        canvas.draw.rounded_rectangle([(x + 20, y + 55), (x + w - 20, y + 120)], radius=6, fill=(20, 26, 36), outline=(40, 52, 70))
        canvas.draw.text((x + 35, y + 68), f"Węzeł ({self.knot_idx + 1}/5): {k['name']}", fill=COLOR_PHOSPHOR_GREEN, font=get_font(13, bold=True))
        canvas.draw.text((x + 35, y + 92), f"{k['alias']}  |  [D-Pad L/P]: Następny węzeł", fill=COLOR_TEXT_MUTED, font=get_font(11))

        # Knot Details Card
        canvas.draw.rounded_rectangle([(x + 20, y + 130), (x + w - 20, y + 200)], radius=6, fill=(22, 28, 38), outline=COLOR_BORDER)
        canvas.draw.text((x + 35, y + 145), f"Wytrzymałość węzła: {k['strength']}", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))
        canvas.draw.text((x + 35, y + 170), f"Zastosowanie: {k['use']}", fill=COLOR_TEXT_SECONDARY, font=get_font(11))

        # ASCII Schematic Panel (Left)
        canvas.draw.rounded_rectangle([(x + 20, y + 215), (x + 260, y + 425)], radius=6, fill=(12, 16, 22), outline=COLOR_BORDER)
        canvas.draw.text((x + 35, y + 228), "SCHEMAT WIZUALNY:", fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))

        ascii_y = y + 260
        for line in k["ascii"]:
            canvas.draw.text((x + 35, ascii_y), line, fill=COLOR_PHOSPHOR_GREEN, font=get_font(11, bold=True))
            ascii_y += 24

        # Step by Step Instructions (Right)
        canvas.draw.rounded_rectangle([(x + 275, y + 215), (x + w - 20, y + 425)], radius=6, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((x + 295, y + 228), "INSTRUKCJA WIĄZANIA KROK PO KROKU:", fill=COLOR_TEXT_PRIMARY, font=get_font(11, bold=True))

        step_y = y + 260
        for s in k["steps"]:
            canvas.draw.text((x + 295, step_y), s, fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=False))
            step_y += 30

    # -----------------------------------------------------------------
    # INPUT HANDLING
    # -----------------------------------------------------------------
    def handle_input(self, event: str) -> bool:
        categories = self.engine.get_categories()
        cur_cat = categories[self.cat_idx]["id"] if self.cat_idx < len(categories) else "water"

        # Hotkey [X]: Emergency SOS Flasher
        if event in ("BTN_X", "x", "X"):
            if self.flasher_active:
                self.flasher_active = False
            else:
                self.flasher_active = True
                self.flasher_step = 0
            return True

        # When flasher is active:
        if self.flasher_active:
            if event in ("BTN_Y", "y", "Y"):
                self.flasher_mode = (self.flasher_mode + 1) % 3
                self.flasher_step = 0
                return True
            elif event in ("BTN_B", "b", "B"):
                self.flasher_active = False
                return True
            return False

        # Hotkey [Y]: Refresh Database / Scan custom files
        if event in ("BTN_Y", "y", "Y"):
            self.engine.load_all()
            self.status_msg = f"Baza odświeżona! ({len(self.engine.all_guides)} poradników)"
            self.status_msg_timer = time.time()
            return True

        # Category Carousel: L1 / R1
        if event in ("BTN_L1", "l1", "L1"):
            self.cat_idx = (self.cat_idx - 1) % len(categories)
            self.article_idx = 0
            self.scroll_y = 0
            self.reading_mode = False
            return True
        elif event in ("BTN_R1", "r1", "R1"):
            self.cat_idx = (self.cat_idx + 1) % len(categories)
            self.article_idx = 0
            self.scroll_y = 0
            self.reading_mode = False
            return True

        # -------------------------------------------------------------
        # Category: TOOLS
        # -------------------------------------------------------------
        if cur_cat == "tools":
            cur_tool_id = self.tools_list[self.tool_idx]["id"]

            if event in ("DPAD_UP", "w", "W", "UP"):
                self.tool_idx = (self.tool_idx - 1) % len(self.tools_list)
                return True
            elif event in ("DPAD_DOWN", "s", "S", "DOWN"):
                self.tool_idx = (self.tool_idx + 1) % len(self.tools_list)
                return True

            # Tool specific controls
            if cur_tool_id == "ors":
                if event in ("DPAD_LEFT", "a", "A", "LEFT"):
                    self.ors_vol_idx = (self.ors_vol_idx - 1) % len(self.ors_volumes)
                    return True
                elif event in ("DPAD_RIGHT", "d", "D", "RIGHT"):
                    self.ors_vol_idx = (self.ors_vol_idx + 1) % len(self.ors_volumes)
                    return True
                elif event in ("BTN_A", "BTN_X"):
                    self.ors_patient_idx = (self.ors_patient_idx + 1) % len(self.ors_patients)
                    return True

            elif cur_tool_id == "battery":
                if event in ("DPAD_LEFT", "a", "A", "LEFT"):
                    self.batt_idx = (self.batt_idx - 1) % len(self.batteries)
                    return True
                elif event in ("DPAD_RIGHT", "d", "D", "RIGHT"):
                    self.batt_idx = (self.batt_idx + 1) % len(self.batteries)
                    return True
                elif event in ("BTN_A", "BTN_X"):
                    self.load_idx = (self.load_idx + 1) % len(self.loads)
                    return True

            elif cur_tool_id == "compass":
                if event in ("DPAD_LEFT", "a", "A", "LEFT"):
                    self.compass_hour = 24 if self.compass_hour <= 1 else self.compass_hour - 1
                    return True
                elif event in ("DPAD_RIGHT", "d", "D", "RIGHT"):
                    self.compass_hour = 1 if self.compass_hour >= 24 else self.compass_hour + 1
                    return True
                elif event in ("BTN_A", "BTN_X"):
                    self.compass_is_dst = not self.compass_is_dst
                    return True

            elif cur_tool_id == "water":
                if event in ("DPAD_LEFT", "a", "A", "LEFT"):
                    self.water_persons = max(1, self.water_persons - 1)
                    return True
                elif event in ("DPAD_RIGHT", "d", "D", "RIGHT"):
                    self.water_persons = min(10, self.water_persons + 1)
                    return True
                elif event in ("BTN_A", "BTN_X"):
                    days = [1, 3, 5, 7, 14, 30]
                    cur_d_idx = days.index(self.water_days) if self.water_days in days else 3
                    self.water_days = days[(cur_d_idx + 1) % len(days)]
                    return True
                elif event in ("BTN_Y", "y", "Y"):
                    self.water_mode_idx = (self.water_mode_idx + 1) % len(self.water_modes)
                    return True

            elif cur_tool_id == "knots":
                if event in ("DPAD_LEFT", "a", "A", "LEFT"):
                    self.knot_idx = (self.knot_idx - 1) % len(self.knots_data)
                    return True
                elif event in ("DPAD_RIGHT", "d", "D", "RIGHT"):
                    self.knot_idx = (self.knot_idx + 1) % len(self.knots_data)
                    return True

            return False

        # -------------------------------------------------------------
        # Category: ARTICLES & GUIDES
        # -------------------------------------------------------------
        guides = self.engine.get_guides_for_category(cur_cat)
        if not guides:
            return False

        if self.reading_mode:
            # When in reading mode, D-Pad Up/Down scrolls text
            if event in ("DPAD_UP", "w", "W", "UP"):
                self.scroll_y = max(0, self.scroll_y - 2)
                return True
            elif event in ("DPAD_DOWN", "s", "S", "DOWN"):
                self.scroll_y = self.scroll_y + 2
                return True
            elif event in ("DPAD_LEFT", "a", "A", "LEFT"):
                self.scroll_y = max(0, self.scroll_y - 6)
                return True
            elif event in ("DPAD_RIGHT", "d", "D", "RIGHT"):
                self.scroll_y = self.scroll_y + 6
                return True
            elif event in ("BTN_B", "b", "B"):
                self.reading_mode = False
                return True
            return False

        # Normal list navigation mode
        if event in ("DPAD_UP", "w", "W", "UP"):
            self.article_idx = (self.article_idx - 1) % len(guides)
            self.scroll_y = 0
            return True
        elif event in ("DPAD_DOWN", "s", "S", "DOWN"):
            self.article_idx = (self.article_idx + 1) % len(guides)
            self.scroll_y = 0
            return True
        elif event in ("BTN_A", "a", "A"):
            self.reading_mode = True
            return True
        elif event in ("DPAD_LEFT", "a", "LEFT"):
            self.scroll_y = max(0, self.scroll_y - 4)
            return True
        elif event in ("DPAD_RIGHT", "d", "RIGHT"):
            self.scroll_y = self.scroll_y + 4
            return True

        return False
