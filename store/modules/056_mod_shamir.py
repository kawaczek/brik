#!/usr/bin/env python3
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
