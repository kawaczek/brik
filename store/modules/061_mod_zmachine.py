#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core.module_base import BaseModule
from core.canvas import Canvas, get_font

class ZMachineModule(BaseModule):
    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.game_title = "ZORK I: THE GREAT UNDERGROUND EMPIRE"
        self.score = 10
        self.moves = 24
        self.location = "West of House"
        self.story_text = (
            "You are standing in an open field west of a white house, with a boarded front door.\\n\\n"
            "There is a small mailbox here.\\n\\n"
            "> OPEN MAILBOX\\n"
            "Opening the small mailbox reveals a leaflet.\\n\\n"
            "> READ LEAFLET\\n"
            "'WELCOME TO ZORK! ZORK is a game of adventure, danger, and low cunning. In it you will explore some of the most amazing territory ever seen by mortals.'"
        )
        self.command_choices = ["OPEN MAILBOX", "READ LEAFLET", "GO NORTH", "GO EAST", "TAKE ALL", "INVENTORY"]
        self.selected_cmd = 0

    def update(self, dt: float): pass

    def render(self, canvas: Canvas):
        draw = canvas.draw
        w, h = 1024, 768
        canvas.clear((8, 12, 18, 255))

        draw.rectangle([0, 0, w, 50], fill=(14, 20, 30, 255), outline=(0, 240, 255, 100), width=1)
        draw.text((20, 14), f"🕹️ 061 // Z-MACHINE INTERACTIVE FICTION // {self.game_title}", fill=(0, 240, 255), font=get_font(18, bold=True))
        canvas.draw_badge(w - 220, 12, f"SCORE: {self.score}", bg_color=(20, 50, 30), text_color=(0, 255, 136))
        canvas.draw_badge(w - 95, 12, f"MOVES: {self.moves}", bg_color=(30, 45, 65))

        # Location status bar
        draw.rectangle([20, 60, 1004, 95], fill=(18, 26, 40))
        draw.text((36, 68), f"LOKACJA: {self.location.upper()}", fill=(255, 200, 0), font=get_font(16, bold=True))

        # Main Story Terminal Window
        canvas.draw_card(20, 105, 984, 450, title="KONSOLA FABULARNA INTERACTIVE FICTION", subtitle="Silnik Z-Machine v3/v5 kompatybilny z Infocom i Inform 7")
        sy = 160
        for para in self.story_text.split("\n\n"):
            draw.text((45, sy), para, fill=(230, 240, 255), font=get_font(16))
            sy += 45

        # D-Pad Wheel Action Selector
        canvas.draw_card(20, 565, 984, 150, title="WYBÓR ROZKAZU D-PADEM (KOŁOWE MENU KOMEND)", subtitle="Wybierz polecenie bez konieczności wpisywania na klawiaturze")
        for i, cmd in enumerate(self.command_choices):
            cx = 40 + i * 158
            is_sel = (i == self.selected_cmd)
            draw.rectangle([cx, 615, cx + 148, 675], fill=(24, 40, 65) if is_sel else (14, 20, 30), outline=(0, 255, 180) if is_sel else (35, 50, 70), width=2 if is_sel else 1)
            draw.text((cx + 12, 638), cmd, fill=(0, 255, 180) if is_sel else (150, 175, 205), font=get_font(13, bold=is_sel))

        draw.rectangle([0, 724, w, 768], fill=(12, 16, 26, 255))
        draw.text((20, 738), "D-Pad Lewo/Prawo: Wybierz Komendę | [A]: Wykonaj Polecenie | [B]: Cofnij Ruch | [Y]: Zapisz Stan Gry", fill=(120, 150, 185), font=get_font(13))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_LEFT", "LEFT"):
            self.selected_cmd = (self.selected_cmd - 1) % len(self.command_choices); return True
        elif event in ("KEY_RIGHT", "RIGHT"):
            self.selected_cmd = (self.selected_cmd + 1) % len(self.command_choices); return True
        return False
