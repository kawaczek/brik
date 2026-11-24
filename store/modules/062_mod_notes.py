#!/usr/bin/env python3
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
