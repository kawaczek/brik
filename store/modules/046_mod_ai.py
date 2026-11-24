#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class AiTerminalModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.models = ["llama3:8b-q4", "mistral:7b", "gemma:2b", "phi-3:mini"]
        self.selected_model = 0
        self.status = "CONNECTED // LOCAL OLLAMA"
        self.latency_ms = 42
        self.chat_history = [
            ("USER", "Zoptymalizuj pętlę renderowania na ekranie 1024x768 ARM64:"),
            ("AI", "Użyj podwójnego buforowania (Double Buffering) w pamięci DMA oraz unikaj ponownego alokowania tablic RGBA w każdej klatce 60 FPS."),
            ("USER", "Jaki jest pobór mocy procesora Allwinner A133P w trybie uśpienia?"),
            ("AI", "W trybie deep-sleep przy wyłączonym podświetleniu ekranu pobór prądu spada do ok. 15-20 mA, co daje ponad 120 godzin czuwania.")
        ]
        self.prompt_text = "Prompt: > Analiza telemetrii sieciowej..."
        self.cursor_blink = 0

    def update(self, dt: float):
        self.cursor_blink = (self.cursor_blink + 1) % 60

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((10, 14, 22, 255))

        # Header
        draw.rectangle([0, 0, w, 50], fill=(14, 20, 32, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), "🤖 046 // POCKET AI TERMINAL & OLLAMA GATEWAY", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 290, 12, f"MODEL: {self.models[self.selected_model]}", bg_color=(20, 45, 65))
        canvas.draw_badge(w - 110, 12, f"{self.latency_ms} ms", bg_color=(15, 60, 40), text_color=(0, 255, 136))

        # Left Panel: Status & Model selector
        canvas.draw_card(20, 65, 300, 640, title="PARAMETRY AI & HOST", subtitle="Ollama / vLLM / Gemini Gateway")
        draw.text((36, 130), f"Status: {self.status}", fill=(0, 255, 136), font=get_font(14, bold=True))
        draw.text((36, 160), "Host: http://192.168.1.150:11434", fill=(160, 180, 210), font=get_font(13))
        draw.text((36, 190), "Temp: 0.7 | Top-P: 0.9 | Ctx: 4096", fill=(160, 180, 210), font=get_font(13))
        draw.text((36, 225), "DOSTĘPNE MODELE:", fill=(255, 170, 0), font=get_font(14, bold=True))
        for i, m in enumerate(self.models):
            bg = (30, 50, 75) if i == self.selected_model else (16, 24, 36)
            col = (0, 240, 255) if i == self.selected_model else (140, 160, 190)
            draw.rectangle([36, 255 + i * 40, 300, 285 + i * 40], fill=bg, outline=(0, 200, 255) if i == self.selected_model else (40, 60, 85))
            draw.text((46, 262 + i * 40), f"{i+1}. {m}", fill=col, font=get_font(13, bold=(i == self.selected_model)))

        # Chat Terminal Area
        canvas.draw_card(335, 65, 669, 560, title="KONSOLA DIALOGOWA CYBER-AI", subtitle="Strumieniowanie odpowiedzi w czasie rzeczywistym")
        cy = 130
        for sender, msg in self.chat_history:
            is_user = (sender == "USER")
            tag_col = (255, 170, 0) if is_user else (0, 240, 255)
            draw.text((355, cy), f"[{sender}]:", fill=tag_col, font=get_font(13, bold=True))
            # Wrap message
            words = msg.split()
            line = ""
            for word in words:
                if len(line) + len(word) > 65:
                    draw.text((355, cy + 20), line, fill=(230, 240, 255) if not is_user else (200, 220, 240), font=get_font(14))
                    cy += 22
                    line = word + " "
                else:
                    line += word + " "
            if line:
                draw.text((355, cy + 20), line, fill=(230, 240, 255) if not is_user else (200, 220, 240), font=get_font(14))
                cy += 24
            cy += 16

        # Prompt input bar
        draw.rectangle([335, 640, 1004, 700], fill=(14, 20, 32, 255), outline=(0, 240, 255), width=2)
        cursor = "_" if self.cursor_blink < 30 else ""
        draw.text((350, 655), f"{self.prompt_text}{cursor}", fill=(0, 255, 180), font=get_font(15, bold=True))

        # Footer
        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Góra/Dół: Zmiana Modelu | [A]: Wyślij Zapytanie | [B]: Wyczyść Czat | [X]: Zmień Host", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_UP", "UP"):
            self.selected_model = (self.selected_model - 1) % len(self.models)
            return True
        elif event in ("KEY_DOWN", "DOWN"):
            self.selected_model = (self.selected_model + 1) % len(self.models)
            return True
        return False
