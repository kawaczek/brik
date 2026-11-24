#!/usr/bin/env python3
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
