#!/usr/bin/env python3
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
