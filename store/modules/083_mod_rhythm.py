#!/usr/bin/env python3
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
