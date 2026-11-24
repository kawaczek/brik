#!/usr/bin/env python3
"""
Brickgotchi - Pwngotchi Live Display & Companion for TrimUI Brick
Connects over Bluetooth (or USB/Wi-Fi), fetches the live Pwngotchi /ui stream,
and renders it on TrimUI Brick's 1024x768 display with themes and integer scaling.
Supports Direct Framebuffer (/dev/fb0) and Terminal (ANSI half-blocks).
"""

import os
import sys
import time
import json
import mmap
import select
import struct
import io
import urllib.request
import urllib.error
import argparse
import threading
from typing import Optional, Tuple

try:
    from PIL import Image, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Color Theme Definitions (BGRA 32-bit for Framebuffer, and RGB strings for Terminal)
THEMES = {
    "classic": {
        "name": "Klasyczny E-Paper (Biel/Czern)",
        "bg_bgra": b"\xf0\xf0\xf0\xff",      # Paper off-white #F0F0F0
        "fg_bgra": b"\x14\x14\x14\xff",      # Black ink #141414
        "header_bgra": b"\x20\x20\x20\xff",  # Dark graphite
        "accent_bgra": b"\x00\xcc\xff\xff",  # Cyan line
        "text_fgra": b"\xff\xff\xff\xff",
        "term_bg": "240;240;240",
        "term_fg": "20;20;20"
    },
    "cyberpunk": {
        "name": "Cyberpunk Neon (Ciemny/Cyjan)",
        "bg_bgra": b"\x0a\x0a\x0e\xff",      # Deep dark blue #0E0A0A
        "fg_bgra": b"\xff\xd8\x00\xff",      # Bright Cyan ink #00D8FF
        "header_bgra": b"\x12\x12\x1c\xff",
        "accent_bgra": b"\xff\x00\x88\xff",  # Neon pink line
        "text_fgra": b"\xff\xd8\x00\xff",
        "term_bg": "10;10;14",
        "term_fg": "0;216;255"
    },
    "amber": {
        "name": "Retro Bursztyn (Bursztyn/Ciemny)",
        "bg_bgra": b"\x0a\x14\x1e\xff",      # Dark #1E140A
        "fg_bgra": b"\x00\x8a\xff\xff",      # Flipper Orange #FF8A00
        "header_bgra": b"\x18\x12\x08\xff",
        "accent_bgra": b"\x00\x8a\xff\xff",
        "text_fgra": b"\x00\x8a\xff\xff",
        "term_bg": "30;20;10",
        "term_fg": "255;138;0"
    },
    "matrix": {
        "name": "Hacker Matrix (Zielen/Czern)",
        "bg_bgra": b"\x00\x08\x00\xff",      # Dark green-black
        "fg_bgra": b"\x20\xff\x20\xff",      # Bright phosphor green
        "header_bgra": b"\x00\x14\x00\xff",
        "accent_bgra": b"\x30\xff\x30\xff",
        "text_fgra": b"\x30\xff\x30\xff",
        "term_bg": "0;8;0",
        "term_fg": "32;255;32"
    }
}

THEME_KEYS = list(THEMES.keys())


class PwngotchiClient:
    """Fetches live /ui frames and API data from Pwngotchi over HTTP."""

    def __init__(self, target_ip: str = "192.168.44.44", port: int = 8080, fallback_ips=None):
        self.target_ip = target_ip
        self.port = port
        self.fallback_ips = fallback_ips or ["10.0.0.2", "pwngotchi.local", "127.0.0.1"]
        self.active_ip = target_ip
        self.connected = False
        self.last_fetch_time = 0

    def get_ui_url(self) -> str:
        return f"http://{self.active_ip}:{self.port}/ui"

    def fetch_frame(self, timeout_sec: float = 1.5) -> Optional[bytes]:
        """Fetch raw PNG image data from /ui."""
        urls_to_try = [f"http://{self.active_ip}:{self.port}/ui"]
        # Add fallbacks if not yet connected
        if not self.connected:
            for fb in self.fallback_ips:
                if fb != self.active_ip:
                    urls_to_try.append(f"http://{fb}:{self.port}/ui")

        for url in urls_to_try:
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Brickgotchi/1.0 (TrimUI Brick Linux)"}
                )
                with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                    if response.status == 200:
                        data = response.read()
                        if len(data) > 100 and data[:8] == b"\x89PNG\r\n\x1a\n":
                            # Extract host IP from URL
                            host = url.split("://")[1].split(":")[0]
                            self.active_ip = host
                            self.connected = True
                            self.last_fetch_time = time.time()
                            return data
            except Exception:
                continue

        self.connected = False
        return None


class FramebufferRenderer:
    """Direct /dev/fb0 renderer for TrimUI Brick (1024x768)."""

    def __init__(self, fb_device: str = "/dev/fb0"):
        self.fb_device = fb_device
        self.width = 1024
        self.height = 768
        self.line_stride = self.width * 4
        self.fb_size = self.line_stride * self.height
        self.fd = None
        self.fb_mmap = None

    def open(self) -> bool:
        try:
            self.fd = os.open(self.fb_device, os.O_RDWR)
            self.fb_mmap = mmap.mmap(
                self.fd,
                self.fb_size,
                mmap.MAP_SHARED,
                mmap.PROT_READ | mmap.PROT_WRITE
            )
            return True
        except Exception as e:
            print(f"[FB] Blad otwarcia {self.fb_device}: {e}")
            return False

    def close(self):
        if self.fb_mmap:
            try:
                self.fb_mmap.seek(0)
                self.fb_mmap.write(b"\x00" * self.fb_size)
                self.fb_mmap.close()
            except Exception:
                pass
        if self.fd is not None:
            try:
                os.close(self.fd)
            except Exception:
                pass

    def draw_chrome(self, theme_key: str, status_str: str):
        """Draw top banner (y=0..64) and bottom banner (y=704..767)."""
        if not self.fb_mmap:
            return

        th = THEMES[theme_key]
        header_row = th["header_bgra"] * self.width
        accent_row = th["accent_bgra"] * self.width

        # Top banner (y=0..62)
        for y in range(0, 62):
            off = y * self.line_stride
            self.fb_mmap[off:off + self.line_stride] = header_row
        # Accent line at y=62, 63
        for y in range(62, 64):
            off = y * self.line_stride
            self.fb_mmap[off:off + self.line_stride] = accent_row

        # Bottom banner (y=704..767)
        for y in range(704, 706):
            off = y * self.line_stride
            self.fb_mmap[off:off + self.line_stride] = accent_row
        for y in range(706, 768):
            off = y * self.line_stride
            self.fb_mmap[off:off + self.line_stride] = header_row

    def render_png_frame(self, png_bytes: bytes, theme_key: str):
        """Scale and render PNG image to center of framebuffer (y=64..703)."""
        if not self.fb_mmap or not HAS_PIL:
            return

        th = THEMES[theme_key]
        try:
            img = Image.open(io.BytesIO(png_bytes)).convert("L")  # Grayscale
        except Exception:
            return

        orig_w, orig_h = img.size
        # Target viewport: width 1024, height 640 (from y=64 to y=704)
        target_max_w = 1024
        target_max_h = 640

        scale = min(target_max_w / orig_w, target_max_h / orig_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)

        # Scale with clean nearest-neighbor (pixel art crispness)
        resized = img.resize((new_w, new_h), Image.NEAREST)

        # Convert grayscale to themed BGRA
        bg_bgra = th["bg_bgra"]
        fg_bgra = th["fg_bgra"]

        # Center in (1024, 640)
        start_x = (1024 - new_w) // 2
        start_y = 64 + (640 - new_h) // 2

        img_bytes = resized.tobytes()

        # Fill background of canvas area
        canvas_bg_row = bg_bgra * self.width
        for y in range(64, start_y):
            off = y * self.line_stride
            self.fb_mmap[off:off + self.line_stride] = canvas_bg_row
        for y in range(start_y + new_h, 704):
            off = y * self.line_stride
            self.fb_mmap[off:off + self.line_stride] = canvas_bg_row

        # Render rows
        left_pad = bg_bgra * start_x
        right_pad = bg_bgra * (1024 - start_x - new_w)

        for ry in range(new_h):
            row_raw = img_bytes[ry * new_w:(ry + 1) * new_w]
            # Invert or map: Pwngotchi e-ink white is background, black is ink
            # pixel > 128 means background, pixel <= 128 means foreground ink
            row_pixels = []
            for px in row_raw:
                row_pixels.append(bg_bgra if px > 128 else fg_bgra)

            full_row = left_pad + b"".join(row_pixels) + right_pad
            off = (start_y + ry) * self.line_stride
            self.fb_mmap[off:off + self.line_stride] = full_row


class TerminalRenderer:
    """Terminal renderer using 24-bit ANSI colors and half-blocks (▀)."""

    def __init__(self):
        pass

    def render_frame(self, png_bytes: bytes, theme_key: str, active_ip: str):
        if not HAS_PIL:
            print("[Terminal] Pillow (PIL) wymagany do renderowania w terminalu.")
            return

        th = THEMES[theme_key]
        try:
            img = Image.open(io.BytesIO(png_bytes)).convert("L")
        except Exception:
            return

        # Target terminal width: 120 cols x 30 lines (60 vertical pixels)
        term_w = 120
        term_h = 58
        resized = img.resize((term_w, term_h), Image.NEAREST)
        raw = resized.tobytes()

        lines = []
        lines.append(f"\033[1;36m=== PWNGOTCHI LIVE ({active_ip}) | Motyw: {th['name']} ===\033[0m")
        lines.append("[C]: Zmiana Koloru | [R]: Odswiez | [Q]: Wyjscie\n")

        bg_rgb = th["term_bg"]
        fg_rgb = th["term_fg"]

        for text_row in range(term_h // 2):
            y_top = text_row * 2
            y_bot = y_top + 1

            row_top = raw[y_top * term_w:(y_top + 1) * term_w]
            row_bot = raw[y_bot * term_w:(y_bot + 1) * term_w]

            row_chars = []
            for x in range(term_w):
                px_top = row_top[x] <= 128  # True if ink
                px_bot = row_bot[x] <= 128

                color_top = fg_rgb if px_top else bg_rgb
                color_bot = fg_rgb if px_bot else bg_rgb
                row_chars.append(f"\033[38;2;{color_top};48;2;{color_bot}m▀")

            row_chars.append("\033[0m")
            lines.append("".join(row_chars))

        sys.stdout.write("\033[H" + "\n".join(lines) + "\n")
        sys.stdout.flush()


def load_settings() -> dict:
    default_settings = {
        "target_ip": "192.168.44.44",
        "port": 8080,
        "fallback_ips": ["10.0.0.2", "pwngotchi.local", "127.0.0.1"],
        "theme": "classic",
        "refresh_interval": 1.0
    }
    path = os.path.join(os.path.dirname(__file__), "settings.json")
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                default_settings.update(data)
        except Exception:
            pass
    return default_settings


def main():
    parser = argparse.ArgumentParser(description="Brickgotchi - Pwngotchi on TrimUI Brick")
    parser.add_argument("--mode", choices=["auto", "fb", "term"], default="auto")
    parser.add_argument("--ip", type=str, default=None, help="Adres IP Pwngotchi (domyslnie z settings.json)")
    parser.add_argument("--theme", choices=THEME_KEYS, default=None)
    args = parser.parse_args()

    settings = load_settings()
    target_ip = args.ip or settings.get("target_ip", "192.168.44.44")
    port = settings.get("port", 8080)
    current_theme = args.theme or settings.get("theme", "classic")
    refresh_sec = settings.get("refresh_interval", 1.0)

    mode = args.mode
    if mode == "auto":
        if os.path.exists("/dev/fb0") and os.access("/dev/fb0", os.W_OK):
            mode = "fb"
        else:
            mode = "term"

    print("==========================================")
    print("      BRICKGOTCHI dla TrimUI Brick        ")
    print("==========================================")
    print(f"[*] Cel: http://{target_ip}:{port}/ui")
    print(f"[*] Tryb wyswietlania: {mode.upper()}")
    print(f"[*] Motyw: {current_theme}")

    client = PwngotchiClient(target_ip=target_ip, port=port, fallback_ips=settings.get("fallback_ips"))

    if mode == "fb":
        fb = FramebufferRenderer("/dev/fb0")
        if not fb.open():
            print("[!] Nie mozna otworzyc /dev/fb0, przelaczam na tryb terminala.")
            mode = "term"
        else:
            fb.draw_chrome(current_theme, f"Szukanie Pwngotchi ({target_ip})...")

    running = True

    try:
        if mode == "term":
            term = TerminalRenderer()
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()

        while running:
            # Check keyboard if terminal
            if mode == "term":
                r, _, _ = select.select([sys.stdin], [], [], 0.02)
                if r:
                    ch = sys.stdin.read(1)
                    if ch in ("q", "Q", "\x03"):
                        break
                    elif ch in ("c", "C"):
                        # Cycle theme
                        cur_idx = THEME_KEYS.index(current_theme)
                        current_theme = THEME_KEYS[(cur_idx + 1) % len(THEME_KEYS)]
                    elif ch in ("r", "R"):
                        refresh_sec = 0.5 if refresh_sec == 2.0 else (refresh_sec * 2.0)

            png_data = client.fetch_frame(timeout_sec=refresh_sec)
            if png_data:
                if mode == "fb":
                    fb.render_png_frame(png_data, current_theme)
                else:
                    term.render_frame(png_data, current_theme, client.active_ip)
            else:
                if mode == "fb":
                    fb.draw_chrome(current_theme, "Oczekiwanie na polaczenie z Pwngotchi...")
                time.sleep(0.5)

            time.sleep(refresh_sec)

    except KeyboardInterrupt:
        pass
    finally:
        if mode == "fb":
            fb.close()
        print("\n[Brickgotchi] Zakonczono dzialanie.")


if __name__ == "__main__":
    main()
