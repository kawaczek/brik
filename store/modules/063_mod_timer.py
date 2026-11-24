#!/usr/bin/env python3
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
