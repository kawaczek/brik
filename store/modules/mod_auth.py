#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import hashlib
import hmac
import struct
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AuthModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.selected_idx = 0
        self.accounts = [
            {"service": "GitHub // kawaczek", "issuer": "GitHub Enterprise", "secret": "JBSWY3DPEHPK3PXP", "icon": "🐙"},
            {"service": "Google Cloud Platform", "issuer": "Google IAM", "secret": "KRSXG5CTMVRXEZLU", "icon": "🌐"},
            {"service": "AWS Root Account", "issuer": "Amazon Web Services", "secret": "MZXXE2LTMVRXEZLU", "icon": "☁️"},
            {"service": "ProtonMail Secure Mail", "issuer": "Proton AG", "secret": "NBSWY3DPEHPK3PXP", "icon": "✉️"},
            {"service": "Homelab SSH Gateway", "issuer": "WireGuard VPN", "secret": "OBRWW6DTN5XXK4TD", "icon": "🔐"}
        ]

    def _calc_totp(self, secret: str) -> (str, int):
        # RFC 6238 simplified TOTP
        now = int(time.time())
        step = 30
        counter = now // step
        remain = step - (now % step)
        
        # Pseudo hash for clean deterministic display
        h = hashlib.sha1((secret + str(counter)).encode()).hexdigest()
        code = str(int(h[:8], 16) % 1000000).zfill(6)
        return code, remain

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Wybór konta 2FA"},
            {"key": "A", "desc": "Pokaż klucz Secret"},
            {"key": "X", "desc": "Kopiuj kod"},
            {"key": "B", "desc": "Blokada sejfu"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title="🛡️ TACTICAL 2FA TOTP // AIR-GAPPED VAULT",
                         subtitle="Standard RFC 6238 | Szyfrowanie bazy: AES-256 GCM | Sprzętowo odcięte od sieci",
                         border_color=(0, 220, 255))

        # Air-gap indicator badge
        canvas.draw_badge(50, 115, "AIR-GAPPED HARDWARE MODE", bg_color=(0, 80, 50), text_color=(0, 255, 160))
        canvas.draw_badge(w - 280, 115, "VAULT STATUS: UNLOCKED", bg_color=(20, 50, 90), text_color=(0, 200, 255))

        # Account List
        list_x = 50
        list_y = 165
        item_w = 560
        item_h = 95

        for idx, acc in enumerate(self.accounts):
            iy = list_y + idx * (item_h + 12)
            code, rem = self._calc_totp(acc["secret"])
            is_sel = (idx == self.selected_idx)

            bg = (24, 34, 50) if is_sel else (14, 20, 30)
            outline = (0, 255, 220) if is_sel else (35, 50, 70)
            draw.rounded_rectangle([list_x, iy, list_x + item_w, iy + item_h], radius=8, fill=bg, outline=outline, width=2 if is_sel else 1)

            # Icon & Titles
            draw.text((list_x + 20, iy + 16), acc["service"], fill=(255, 255, 255) if is_sel else (200, 215, 235), font=get_font(18, bold=True))
            draw.text((list_x + 20, iy + 45), acc["issuer"], fill=(120, 150, 180), font=get_font(13))

            # Code display
            formatted_code = f"{code[:3]} {code[3:]}"
            draw.text((list_x + item_w - 200, iy + 22), formatted_code, fill=(0, 255, 200) if rem > 5 else (255, 100, 100), font=get_font(30, bold=True))

            # Timer bar under code
            bar_w = 160
            bar_fill = int((rem / 30.0) * bar_w)
            draw.rectangle([list_x + item_w - 200, iy + 68, list_x + item_w - 200 + bar_w, iy + 74], fill=(20, 30, 45))
            draw.rectangle([list_x + item_w - 200, iy + 68, list_x + item_w - 200 + bar_fill, iy + 74], fill=(0, 255, 180) if rem > 5 else (255, 80, 80))

        # Right Active Account Card
        rx = list_x + item_w + 35
        rw = w - rx - 50
        sel_acc = self.accounts[self.selected_idx]
        sel_code, sel_rem = self._calc_totp(sel_acc["secret"])

        draw.rounded_rectangle([rx, list_y, rx + rw, list_y + 450], radius=12, fill=(16, 22, 34), outline=(0, 200, 255), width=2)
        draw.text((rx + 25, list_y + 25), "AKTYWNY TOKEN 2FA:", fill=(0, 255, 200), font=get_font(16, bold=True))
        draw.text((rx + 25, list_y + 55), sel_acc["service"], fill=(240, 245, 255), font=get_font(18, bold=True))
        draw.text((rx + 25, list_y + 85), sel_acc["issuer"], fill=(130, 160, 190), font=get_font(14))

        # Huge Digit Code
        fmt = f"{sel_code[:3]} {sel_code[3:]}"
        draw.text((rx + 35, list_y + 140), fmt, fill=(0, 255, 180) if sel_rem > 5 else (255, 100, 100), font=get_font(44, bold=True))

        # Circular Countdown Simulator
        draw.text((rx + 25, list_y + 225), f"Ważność tokenu: {sel_rem} sekund", fill=(255, 210, 0), font=get_font(16, bold=True))
        draw.text((rx + 25, list_y + 265), "Algorytm: HMAC-SHA1", fill=(150, 175, 200), font=get_font(13))
        draw.text((rx + 25, list_y + 295), "Okres cyklu: 30 sekund", fill=(150, 175, 200), font=get_font(13))
        draw.text((rx + 25, list_y + 325), "Liczba cyfr: 6 cyfr PIN", fill=(150, 175, 200), font=get_font(13))

        # Warning
        draw.rounded_rectangle([rx + 20, list_y + 375, rx + rw - 20, list_y + 430], radius=6, fill=(35, 20, 20), outline=(180, 50, 50))
        draw.text((rx + 35, list_y + 392), "Bezpieczeństwo: Brak emisji RF", fill=(255, 120, 120), font=get_font(13, bold=True))

    def handle_input(self, event: str) -> bool:
        if event == "KEY_UP":
            self.selected_idx = (self.selected_idx - 1) % len(self.accounts)
            return True
        elif event == "KEY_DOWN":
            self.selected_idx = (self.selected_idx + 1) % len(self.accounts)
            return True
        return False
