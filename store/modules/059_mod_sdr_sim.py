#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class SdrSimModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.freq_mhz = 145.500
        self.mode = "FM"
        self.rssi = -68
        self.bandwidth_khz = 12.5

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((6, 10, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 255, 200, 100), width=1)
        draw.text((20, 14), f"🌊 059 // SDR WATERFALL & SPECTRUM SIMULATOR // {self.freq_mhz:.3f} MHZ {self.mode}", fill=(0, 255, 200), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, "RTL-SDR / HACKRF", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 75, 12, "LIVE", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # FFT Spectrum Plot
        canvas.draw_card(20, 65, 984, 260, title="WIDMO CZĘSTOTLIWOŚCI FFT (FAST FOURIER TRANSFORM)", subtitle="Moc sygnału w pasmie 2 MHz wokół częstotliwości środkowej")
        draw.rectangle([40, 120, 980, 290], fill=(10, 16, 26), outline=(0, 180, 220))
        # Mock FFT peaks
        peaks = [(-85), (-82), (-80), (-45), (-42), (-78), (-81), (-65), (-80)]
        for i in range(len(peaks) - 1):
            x1 = 60 + i * 110
            x2 = 60 + (i + 1) * 110
            y1 = 280 - int((peaks[i] + 90) * 3)
            y2 = 280 - int((peaks[i + 1] + 90) * 3)
            draw.line([(x1, y1), (x2, y2)], fill=(0, 255, 180), width=2)
        # Tuning carrier marker
        draw.line([(512, 120), (512, 290)], fill=(255, 0, 80), width=2)
        draw.text((520, 130), f"NOŚNA: {self.freq_mhz:.3f} MHz", fill=(255, 80, 80), font=get_font(13, bold=True))

        # Waterfall (Wodospad) Area
        canvas.draw_card(20, 340, 984, 370, title="WODOSPAD RADIOELEKTRONICZNY (WATERFALL HISTORY)", subtitle="Historia transmisji w dziedzinie czasu i częstotliwości")
        draw.rectangle([40, 390, 980, 680], fill=(8, 12, 24), outline=(0, 200, 255))
        # Simulated waterfall lines
        for y in range(400, 670, 18):
            draw.rectangle([480, y, 540, y + 14], fill=(255, 180, 0))
            draw.rectangle([700, y, 740, y + 14], fill=(0, 160, 255))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Strojenie ±12.5 kHz | Góra/Dół: ±1 MHz | [A]: Zmień Modulację (AM/FM/SSB/CW)", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool: return False
