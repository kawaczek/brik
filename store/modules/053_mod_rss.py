#!/usr/bin/env python3
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
