"""
BrickDeck Module: Cyber Radio & Audio Spectrum Visualizer
Streams cyberdeck & hacker radio stations with animated 32-band spectrum, oscilloscope, and reel-to-reel deck.
"""

import math
import time
import random
import shutil
import subprocess
from typing import List, Dict, Optional

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)
from core.canvas import get_font

STATIONS = [
    {
        "name": "SomaFM: DEF CON Radio",
        "tag": "Music for Hackers",
        "genre": "Dark Ambient / Cyber Synth",
        "url": "http://ice1.somafm.com/defcon-128-mp3",
        "bitrate": "128 kbps MP3",
        "icon": "⚡"
    },
    {
        "name": "SomaFM: Secret Agent",
        "tag": "Spy Lounge & Espionage",
        "genre": "Downtempo / James Bond Style",
        "url": "http://ice1.somafm.com/secretagent-128-mp3",
        "bitrate": "128 kbps MP3",
        "icon": "🕵️"
    },
    {
        "name": "SomaFM: Groove Salad",
        "tag": "Downtempo Ambient",
        "genre": "Ambient / Chillout Beats",
        "url": "http://ice1.somafm.com/groovesalad-128-mp3",
        "bitrate": "128 kbps MP3",
        "icon": "🥗"
    },
    {
        "name": "Kohina: 8-Bit Chiptunes",
        "tag": "Vintage Microcomputers",
        "genre": "C64 / Amiga / Arcade SID Tunes",
        "url": "http://stream.kohina.com:8000/stream.ogg",
        "bitrate": "160 kbps Vorbis",
        "icon": "👾"
    },
    {
        "name": "SceneSat: Demoscene",
        "tag": "Demoscene Tracker & Synth",
        "genre": "MOD / XM / S3M / IT Music",
        "url": "https://stream.scenesat.com:8000/scenesat",
        "bitrate": "192 kbps MP3",
        "icon": "💽"
    },
    {
        "name": "Radio Gorzów 95.6 FM",
        "tag": "Stacja Regionalna",
        "genre": "Wiadomości / Publicystyka / Muzyka",
        "url": "http://stream.zachod.pl:8000/rg",
        "bitrate": "128 kbps MP3",
        "icon": "📻"
    },
    {
        "name": "Polskie Radio Trójka",
        "tag": "Program Trzeci Polskiego Radia",
        "genre": "Rock / Jazz / Audycje",
        "url": "http://stream3.polskieradio.pl:8904/",
        "bitrate": "128 kbps MP3",
        "icon": "🎙️"
    }
]


class RadioModule(BaseModule):
    name = "Cyber Radio & Spectrum"
    short_name = "Radio"
    icon = "📻"
    accent_color = COLOR_NEON_PINK

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.selected_station_idx = 0
        self.active_station_idx = -1
        self.is_playing = False
        self.is_muted = False
        self.volume = 80  # 0 to 100%
        self.visualizer_mode = 0  # 0: EQ Spectrum, 1: Oscilloscope, 2: Stereo VU Meter
        self.mode_names = ["Spectrum EQ (32-Band)", "Oscyloskop CRT", "Stereo VU-Meter"]

        # Audio Subprocess
        self.audio_proc: Optional[subprocess.Popen] = None
        self.player_bin: Optional[str] = None

        # Animation states
        self.reel_angle = 0.0
        self.elapsed_play_time = 0.0
        self.spectrum_bands = [0.1] * 32
        self.peak_bands = [0.1] * 32
        self.osc_phase = 0.0

    def on_load(self):
        # Detect available audio player CLI binary
        for cand in ["mpg123", "ffplay", "cvlc", "mplayer"]:
            if shutil.which(cand):
                self.player_bin = cand
                break

    def on_deactivate(self):
        # We allow audio to keep playing in background if desired, or stop when app closes
        pass

    def get_hotkey_hints(self):
        status_txt = "Pauza" if self.is_playing else "Graj"
        return [
            ("L1/R1", "Moduły"),
            ("D-Pad G/D", "Wybór stacji"),
            ("A", status_txt),
            ("D-Pad L/P", f"Głośność: {self.volume}%"),
            ("X", "Tryb wizualizacji"),
            ("Y", "Wycisz (Mute)")
        ]

    def _start_playback(self, station_idx: int):
        self._stop_playback()
        self.active_station_idx = station_idx
        station = STATIONS[station_idx]
        url = station["url"]
        self.is_playing = True
        self.elapsed_play_time = 0.0

        if not self.player_bin:
            return  # Run in simulated visualizer mode

        try:
            if self.player_bin == "mpg123":
                cmd = ["mpg123", "-q", "-f", str(int(self.volume * 327.67)), url]
            elif self.player_bin == "ffplay":
                cmd = ["ffplay", "-nodisp", "-autoexit", "-volume", str(self.volume), url]
            else:
                cmd = [self.player_bin, url]
            self.audio_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            self.audio_proc = None

    def _stop_playback(self):
        self.is_playing = False
        if self.audio_proc:
            try:
                self.audio_proc.terminate()
                self.audio_proc.wait(timeout=0.5)
            except Exception:
                pass
            self.audio_proc = None

    def update(self, dt: float):
        if self.is_playing:
            self.elapsed_play_time += dt
            # Spin tape reels
            self.reel_angle = (self.reel_angle + dt * 180.0) % 360.0
            self.osc_phase = (self.osc_phase + dt * 12.0) % (2 * math.pi)

            # Generate dynamic audio spectrum bands
            for i in range(len(self.spectrum_bands)):
                target = random.uniform(0.15, 0.95) * (0.0 if self.is_muted else (self.volume / 100.0))
                # Add bass emphasis to lower bands
                if i < 8:
                    target = min(1.0, target * 1.3)
                self.spectrum_bands[i] += (target - self.spectrum_bands[i]) * 0.4
                # Decay peak hold needles slowly
                if self.spectrum_bands[i] > self.peak_bands[i]:
                    self.peak_bands[i] = self.spectrum_bands[i]
                else:
                    self.peak_bands[i] = max(0.0, self.peak_bands[i] - dt * 0.5)
        else:
            # Decay to zero when stopped
            for i in range(len(self.spectrum_bands)):
                self.spectrum_bands[i] = max(0.02, self.spectrum_bands[i] - dt * 1.5)
                self.peak_bands[i] = max(0.02, self.peak_bands[i] - dt * 0.8)

    def _draw_tape_reel(self, draw, cx: int, cy: int, radius: int, angle: float):
        """Draw animated tape deck reel with spinning spokes."""
        # Outer reel rim
        draw.ellipse([(cx - radius, cy - radius), (cx + radius, cy + radius)], fill=(28, 34, 46), outline=COLOR_BORDER, width=2)
        # Inner hub
        hub_r = int(radius * 0.35)
        draw.ellipse([(cx - hub_r, cy - hub_r), (cx + hub_r, cy + hub_r)], fill=(16, 20, 28), outline=COLOR_CYBER_CYAN, width=1)
        # Center spindle
        draw.ellipse([(cx - 4, cy - 4), (cx + 4, cy + 4)], fill=COLOR_TEXT_PRIMARY)

        # 3 Spokes
        for i in range(3):
            spoke_ang = math.radians(angle + i * 120)
            sx = cx + int(math.cos(spoke_ang) * (radius - 6))
            sy = cy + int(math.sin(spoke_ang) * (radius - 6))
            draw.line([(cx, cy), (sx, sy)], fill=COLOR_BORDER, width=2)
            # Spoke circular cutout
            mx = cx + int(math.cos(spoke_ang) * (radius * 0.65))
            my = cy + int(math.sin(spoke_ang) * (radius * 0.65))
            draw.ellipse([(mx - 6, my - 6), (mx + 6, my + 6)], fill=(14, 18, 24), outline=COLOR_CYBER_CYAN, width=1)

    def render(self, canvas):
        # Left Panel: Stations list (x=32, y=66, w=450, h=634)
        canvas.draw_card(
            32, 66, 450, 634,
            title="CYBERDECK RADIO TUNER",
            subtitle=f"Dostępne stacje: {len(STATIONS)}  |  Silnik audio: {self.player_bin or 'Sim'}",
            border_color=self.accent_color
        )

        font_name = get_font(13, bold=True)
        font_genre = get_font(11, bold=False)
        font_tag = get_font(11, bold=True)

        list_y = 118
        for i, st in enumerate(STATIONS):
            is_cursor = (i == self.selected_station_idx)
            is_active_st = (i == self.active_station_idx and self.is_playing)

            # Card background
            bg_col = (36, 48, 68) if is_cursor else ((22, 34, 30) if is_active_st else (20, 24, 32))
            border_col = self.accent_color if is_cursor else (COLOR_PHOSPHOR_GREEN if is_active_st else COLOR_BORDER)

            canvas.draw.rounded_rectangle([(46, list_y), (46 + 422, list_y + 68)],
                                          radius=8, fill=bg_col, outline=border_col, width=2 if is_cursor else 1)

            # Station Icon & Name
            canvas.draw.text((60, list_y + 10), f"{st['icon']}  {st['name']}", fill=COLOR_TEXT_PRIMARY, font=font_name)

            # Active Playing Badge
            if is_active_st:
                canvas.draw_badge(46 + 320, list_y + 10, "LIVE ON AIR", bg_color=(20, 100, 50), text_color=COLOR_TEXT_PRIMARY)
            elif is_cursor:
                canvas.draw_badge(46 + 348, list_y + 10, "WYBIERZ", bg_color=(40, 50, 70), text_color=COLOR_CYBER_CYAN)

            # Genre & Subtitle
            canvas.draw.text((60, list_y + 32), st["genre"], fill=COLOR_TEXT_SECONDARY, font=font_genre)
            canvas.draw.text((60, list_y + 48), f"Tag: {st['tag']}  •  {st['bitrate']}", fill=COLOR_TEXT_MUTED, font=font_genre)

            list_y += 76

        # ----------------------------------------------------------------------
        # Right Panel: Tape Deck & Visualizer Studio (x=496, y=66, w=496, h=634)
        # ----------------------------------------------------------------------
        canvas.draw_card(
            496, 66, 496, 634,
            title="AUDIO VISUALIZER & DECK",
            subtitle=f"Tryb: {self.mode_names[self.visualizer_mode]}",
            border_color=COLOR_BORDER
        )

        rx = 512
        ry = 118
        rw = 464

        # 1. Retro Reel-to-Reel Tape Deck Chassis (x=rx, y=ry, w=rw, h=160)
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + 160)], radius=10, fill=(16, 20, 28), outline=COLOR_BORDER, width=1)

        # Tape Heads and guides in middle
        canvas.draw.rectangle([(rx + rw // 2 - 30, ry + 70), (rx + rw // 2 + 30, ry + 120)], fill=(28, 34, 46), outline=COLOR_BORDER)
        canvas.draw.line([(rx + 90, ry + 95), (rx + rw - 90, ry + 95)], fill=(120, 70, 30), width=4)  # Magnetic tape ribbon

        # Left Reel
        self._draw_tape_reel(canvas.draw, rx + 90, ry + 80, radius=56, angle=self.reel_angle)
        # Right Reel
        self._draw_tape_reel(canvas.draw, rx + rw - 90, ry + 80, radius=56, angle=self.reel_angle * 1.05)

        # Tape Counter & Play status in center
        min_play = int(self.elapsed_play_time) // 60
        sec_play = int(self.elapsed_play_time) % 60
        timer_str = f"{min_play:02d}:{sec_play:02d}"
        canvas.draw.rounded_rectangle([(rx + rw // 2 - 42, ry + 18), (rx + rw // 2 + 42, ry + 46)], radius=4, fill=(10, 14, 20), outline=COLOR_CYBER_CYAN)
        canvas.draw.text((rx + rw // 2 - 26, ry + 22), timer_str, fill=COLOR_CYBER_CYAN, font=get_font(16, bold=True))

        status_lbl = "● PLAYING" if self.is_playing else "■ STOPPED"
        status_col = COLOR_PHOSPHOR_GREEN if self.is_playing else COLOR_TEXT_MUTED
        canvas.draw.text((rx + rw // 2 - 34, ry + 50), status_lbl, fill=status_col, font=get_font(11, bold=True))

        # 2. Main Visualizer Screen (x=rx, y=ry + 172, w=rw, h=210)
        vis_y = ry + 172
        vis_h = 210

        if self.visualizer_mode == 0:
            # 32-Band Equalizer Spectrum
            canvas.draw_spectrum(rx, vis_y, rw, vis_h, self.spectrum_bands, self.peak_bands,
                                bar_color=COLOR_CYBER_CYAN, peak_color=COLOR_FLIPPER_AMBER)
        elif self.visualizer_mode == 1:
            # Retro Green CRT Oscilloscope Beam
            wave_pts = []
            for pt_i in range(80):
                wave = math.sin(self.osc_phase + pt_i * 0.18) * 0.6 + math.sin(self.osc_phase * 2.3 + pt_i * 0.35) * 0.25
                if not self.is_playing:
                    wave *= 0.05
                wave_pts.append(wave)
            canvas.draw_oscilloscope(rx, vis_y, rw, vis_h, wave_pts, color=COLOR_PHOSPHOR_GREEN)
        else:
            # Stereo Analog/Cyber VU-Meters
            avg_l = sum(self.spectrum_bands[:16]) / 16.0
            avg_r = sum(self.spectrum_bands[16:]) / 16.0
            db_l = -40.0 + (avg_l * 44.0)
            db_r = -40.0 + (avg_r * 44.0)
            canvas.draw_vu_meter(rx, vis_y + 35, rw, vis_h - 70, db_l, db_r)

        # 3. Track Info Card (x=rx, y=vis_y + vis_h + 12, w=rw, h=100)
        card_y = vis_y + vis_h + 12
        canvas.draw.rounded_rectangle([(rx, card_y), (rx + rw, card_y + 94)], radius=8, fill=(20, 24, 32), outline=COLOR_BORDER)

        act_st = STATIONS[self.active_station_idx] if 0 <= self.active_station_idx < len(STATIONS) else STATIONS[self.selected_station_idx]

        canvas.draw.text((rx + 14, card_y + 10), "AKTYWNY STRUMIEŃ:", fill=COLOR_TEXT_SECONDARY, font=get_font(11, bold=False))
        canvas.draw.text((rx + 14, card_y + 26), act_st["name"], fill=COLOR_CYBER_CYAN, font=get_font(14, bold=True))
        canvas.draw.text((rx + 14, card_y + 46), f"Gatunek: {act_st['genre']}", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=False))
        canvas.draw.text((rx + 14, card_y + 64), f"Kodek / Bitrate: {act_st['bitrate']}  |  Buffer: OK (100%)", fill=COLOR_TEXT_MUTED, font=get_font(11, bold=False))

        # 4. Master Volume Bar
        vol_y = card_y + 106
        canvas.draw_gauge(rx, vol_y, rw, 14, self.volume, 100, label=f"GŁOŚNOŚĆ AUDIO ({self.volume}%)", color=COLOR_FLIPPER_AMBER)

    def handle_input(self, event: str) -> bool:
        if event == "UP":
            if self.selected_station_idx > 0:
                self.selected_station_idx -= 1
                return True
        elif event == "DOWN":
            if self.selected_station_idx < len(STATIONS) - 1:
                self.selected_station_idx += 1
                return True
        elif event == "BTN_A":
            # Toggle play selected station
            if self.is_playing and self.active_station_idx == self.selected_station_idx:
                self._stop_playback()
            else:
                self._start_playback(self.selected_station_idx)
            return True
        elif event == "LEFT":
            self.volume = max(0, self.volume - 5)
            return True
        elif event == "RIGHT":
            self.volume = min(100, self.volume + 5)
            return True
        elif event == "BTN_X":
            # Cycle visualizer mode
            self.visualizer_mode = (self.visualizer_mode + 1) % len(self.mode_names)
            return True
        elif event == "BTN_Y":
            # Mute toggle
            self.is_muted = not self.is_muted
            return True
        return False
