#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class MandelbrotModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.center_r = -0.743643887037158704752191506114774
        self.center_i = 0.131825904205311970493132056385139
        self.zoom = 120.0
        self.mode = "MANDELBROT" # or JULIA
        self.max_iter = 40
        self.preview_w = 480
        self.preview_h = 360

    def get_hotkey_hints(self):
        return [
            {"key": "D-Pad", "desc": "Przesuwanie płaszczyzny"},
            {"key": "A", "desc": "Zoom +"},
            {"key": "B", "desc": "Zoom -"},
            {"key": "X", "desc": "Tryb Julia / Mandel"}
        ]

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        draw = canvas.draw
        canvas.draw_card(20, 66, w - 40, h - 90, title=f"🌀 FRACTAL LAB // {self.mode} EXPLORER",
                         subtitle=f"Współrzędne: Re {self.center_r:.6f}, Im {self.center_i:.6f} | Przybliżenie: {self.zoom:.1f}x",
                         border_color=(190, 80, 255))

        # Viewport Frame
        vx, vy = 50, 120
        vw, vh = 600, 480
        draw.rounded_rectangle([vx, vy, vx + vw, vy + vh], radius=8, fill=(10, 8, 16), outline=(180, 80, 255), width=2)

        # Draw fast pseudo-fractal representation
        step = 6
        for py in range(0, vh, step):
            ci = (py - vh / 2) / (self.zoom * 2.0) + self.center_i
            for px in range(0, vw, step):
                cr = (px - vw / 2) / (self.zoom * 2.0) + self.center_r
                zr, zi = 0.0, 0.0
                it = 0
                while zr * zr + zi * zi <= 4.0 and it < self.max_iter:
                    zr, zi = zr * zr - zi * zi + cr, 2.0 * zr * zi + ci
                    it += 1

                if it == self.max_iter:
                    col = (0, 0, 0)
                else:
                    hue = (it * 12) % 360
                    # Quick neon palette
                    col = (int((it / self.max_iter) * 200), int((it * 6) % 255), 255)
                draw.rectangle([vx + px, vy + py, vx + px + step, vy + py + step], fill=col)

        # Crosshairs
        draw.line([(vx + vw // 2 - 15, vy + vh // 2), (vx + vw // 2 + 15, vy + vh // 2)], fill=(255, 255, 255, 180), width=1)
        draw.line([(vx + vw // 2, vy + vh // 2 - 15), (vx + vw // 2, vy + vh // 2 + 15)], fill=(255, 255, 255, 180), width=1)

        # Right Telemetry Panel
        rx = vx + vw + 30
        draw.text((rx, 130), "TELEMETRIA MATEMATYCZNA:", fill=(0, 255, 200), font=get_font(18, bold=True))
        
        info = [
            ("Równanie:", "Z_{n+1} = Z_n^2 + C"),
            ("Iteracje max:", f"{self.max_iter} iter"),
            ("Rozdzielczość:", f"{vw} x {vh} px"),
            ("Promień ucieczki:", "|Z| > 2.0"),
            ("Wymiar Hausdorffa:", "D = 2.0 (granica)")
        ]
        ty = 170
        for label, val in info:
            draw.text((rx, ty), label, fill=(150, 170, 200), font=get_font(14))
            draw.text((rx, ty + 20), val, fill=(240, 250, 255), font=get_font(15, bold=True))
            ty += 50

        # Coordinates display box
        draw.rounded_rectangle([rx, 450, rx + 280, 580], radius=8, fill=(18, 22, 34), outline=(40, 60, 90))
        draw.text((rx + 15, 465), "PŁASZCZYZNA ZESPOLONA:", fill=(255, 210, 0), font=get_font(12, bold=True))
        draw.text((rx + 15, 495), f"Re: {self.center_r:.10f}", fill=(220, 230, 245), font=get_font(13))
        draw.text((rx + 15, 525), f"Im: {self.center_i:.10f}", fill=(220, 230, 245), font=get_font(13))
        draw.text((rx + 15, 555), f"Mag: {self.zoom:.1f}x", fill=(0, 255, 160), font=get_font(13, bold=True))

    def handle_input(self, event: str) -> bool:
        delta = 40.0 / self.zoom
        if event == "KEY_LEFT":
            self.center_r -= delta
            return True
        elif event == "KEY_RIGHT":
            self.center_r += delta
            return True
        elif event == "KEY_UP":
            self.center_i -= delta
            return True
        elif event == "KEY_DOWN":
            self.center_i += delta
            return True
        elif event == "KEY_A":
            self.zoom *= 1.5
            return True
        elif event == "KEY_B":
            self.zoom = max(10.0, self.zoom / 1.5)
            return True
        elif event == "KEY_X":
            self.mode = "JULIA C=-0.7+0.27i" if self.mode == "MANDELBROT" else "MANDELBROT"
            return True
        return False
