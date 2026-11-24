#!/usr/bin/env python3
"""
BrickFlipper - Flipper Zero Remote Display & Controller for TrimUI Brick
Renders Flipper Zero's 128x64 LCD to TrimUI Brick's 1024x768 display with 8x integer scaling.
Supports Direct Framebuffer (/dev/fb0), Pygame (PC test), and Terminal (ANSI half-block).
"""

import os
import sys
import time
import mmap
import fcntl
import struct
import select
import termios
import tty
import argparse
import threading
from typing import Optional

from flipper_proto import (
    FlipperClient,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_BACK,
    TYPE_PRESS, TYPE_RELEASE, TYPE_SHORT
)

# Color definitions (32-bit BGRA for typical Linux FB)
# Flipper Colors:
# Backlight Amber/Orange: #FF8A00 -> (B: 0x00, G: 0x8A, R: 0xFF, A: 0xFF)
COLOR_AMBER_BGRA = b"\x00\x8a\xff\xff"
# Dark LCD Pixels: #1E140A -> (B: 0x0A, G: 0x14, R: 0x1E, A: 0xFF)
COLOR_DARK_BGRA = b"\x0a\x14\x1e\xff"
# Header / Footer background: #181A1F
COLOR_HEADER_BGRA = b"\x1f\x1a\x18\xff"
# Accent line: #FF8A00
COLOR_ACCENT_BGRA = b"\x00\x8a\xff\xff"
# Text / light gray: #C0C0C0
COLOR_TEXT_BGRA = b"\xc0\xc0\xc0\xff"

# Pre-computed 8-pixel horizontal segments (32 bytes each)
ORANGE_SEGMENT_8PX = COLOR_AMBER_BGRA * 8
DARK_SEGMENT_8PX = COLOR_DARK_BGRA * 8


class FramebufferRenderer:
    """Fast direct /dev/fb0 renderer with 8x integer scaling for TrimUI Brick."""

    def __init__(self, fb_device: str = "/dev/fb0"):
        self.fb_device = fb_device
        self.width = 1024
        self.height = 768
        self.bpp = 32
        self.bytes_per_pixel = 4
        self.line_stride = self.width * self.bytes_per_pixel  # 4096 bytes
        self.fb_size = self.line_stride * self.height         # 3,145,728 bytes
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
            self.draw_ui_shell("Szukam Flippera na USB/BT...")
            return True
        except Exception as e:
            print(f"[FB] Cannot open {self.fb_device}: {e}")
            return False

    def close(self):
        if self.fb_mmap:
            try:
                # Clear screen to black on exit
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

    def draw_ui_shell(self, status_text: str = "POLACZONO (USB)"):
        """Draw top banner (y=0..127) and bottom banner (y=640..767)."""
        if not self.fb_mmap:
            return

        header_row = COLOR_HEADER_BGRA * self.width
        accent_row = COLOR_ACCENT_BGRA * self.width

        # Top banner (y=0..127)
        for y in range(0, 126):
            offset = y * self.line_stride
            self.fb_mmap[offset:offset + self.line_stride] = header_row
        # Accent separator at y=126, 127
        for y in range(126, 128):
            offset = y * self.line_stride
            self.fb_mmap[offset:offset + self.line_stride] = accent_row

        # Bottom banner (y=640..767)
        # Accent separator at y=640, 641
        for y in range(640, 642):
            offset = y * self.line_stride
            self.fb_mmap[offset:offset + self.line_stride] = accent_row
        for y in range(642, 768):
            offset = y * self.line_stride
            self.fb_mmap[offset:offset + self.line_stride] = header_row

    def render_flipper_frame(self, raw_1024_bytes: bytes):
        """
        Unpack 1024 bytes SSD1306 buffer and scale 8x into framebuffer.
        Flipper screen (128x64) -> (1024x512) centered between y=128 and y=639.
        """
        if not self.fb_mmap or len(raw_1024_bytes) < 1024:
            return

        base_y_offset = 128
        # Loop over all 64 Flipper rows
        for fy in range(64):
            page = fy >> 3
            bit = fy & 7
            page_offset = page * 128

            # Build one 1024-pixel horizontal row (4096 bytes)
            row_segments = []
            for fx in range(128):
                pixel = (raw_1024_bytes[page_offset + fx] >> bit) & 1
                row_segments.append(DARK_SEGMENT_8PX if pixel else ORANGE_SEGMENT_8PX)
            row_bytes = b"".join(row_segments)

            # Copy this 1024-pixel row 8 times (8 vertical pixels per Flipper pixel)
            target_y = base_y_offset + (fy * 8)
            for dy in range(8):
                byte_offset = (target_y + dy) * self.line_stride
                self.fb_mmap[byte_offset:byte_offset + self.line_stride] = row_bytes


class TerminalRenderer:
    """Terminal renderer using 24-bit ANSI colors and Unicode half-blocks (▀)."""

    def __init__(self):
        self.amber_rgb = "255;138;0"
        self.dark_rgb = "30;20;10"

    def clear(self):
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    def render_frame(self, raw_1024_bytes: bytes):
        if len(raw_1024_bytes) < 1024:
            return

        lines = []
        lines.append(f"\033[1;38;2;{self.amber_rgb}m=== FLIPPER ZERO REMOTE (BRICKFLIPPER) ===\033[0m")
        lines.append("Sterowanie: W/A/S/D - Krzyzak | Spacja - OK | B - Back | Q - Wyjscie\n")

        # 64 rows packed into 32 text rows using half blocks (2 vertical pixels per char)
        for text_row in range(32):
            y_top = text_row * 2
            y_bot = y_top + 1

            page_top = y_top >> 3
            bit_top = y_top & 7
            off_top = page_top * 128

            page_bot = y_bot >> 3
            bit_bot = y_bot & 7
            off_bot = page_bot * 128

            row_chars = []
            for fx in range(128):
                px_top = (raw_1024_bytes[off_top + fx] >> bit_top) & 1
                px_bot = (raw_1024_bytes[off_bot + fx] >> bit_bot) & 1

                # 1 = Dark LCD pixel, 0 = Amber backlight
                color_fg = self.dark_rgb if px_top else self.amber_rgb
                color_bg = self.dark_rgb if px_bot else self.amber_rgb
                row_chars.append(f"\033[38;2;{color_fg};48;2;{color_bg}m▀")

            row_chars.append("\033[0m")
            lines.append("".join(row_chars))

        # Reset cursor to top-left to avoid terminal scrolling / flickering
        sys.stdout.write("\033[H" + "\n".join(lines) + "\n")
        sys.stdout.flush()


class InputManager:
    """Manages gamepad / evdev inputs on TrimUI and keyboard inputs on PC."""

    def __init__(self, flipper_client: FlipperClient):
        self.client = flipper_client
        self.running = True
        self.thread: Optional[threading.Thread] = None

    def start_evdev_listener(self):
        """Spawn listener thread for Linux /dev/input/event* devices."""
        self.thread = threading.Thread(target=self._evdev_loop, daemon=True)
        self.thread.start()

    def _evdev_loop(self):
        import glob
        ev_paths = glob.glob("/dev/input/event*")
        fds = []
        for path in ev_paths:
            try:
                fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                fds.append(fd)
            except Exception:
                pass

        if not fds:
            return

        # Key mappings (Linux input keycodes)
        # 103: KEY_UP, 108: KEY_DOWN, 105: KEY_LEFT, 106: KEY_RIGHT
        # 304/28/57: BTN_A/ENTER/SPACE -> OK
        # 305/1/14: BTN_B/ESC/BACKSPACE -> BACK
        key_map = {
            103: KEY_UP,
            108: KEY_DOWN,
            105: KEY_LEFT,
            106: KEY_RIGHT,
            28: KEY_OK,
            57: KEY_OK,
            304: KEY_OK,
            1: KEY_BACK,
            14: KEY_BACK,
            305: KEY_BACK,
        }

        # struct input_event format: time (16 bytes), uint16 type, uint16 code, int32 value
        fmt = "llHHi"
        event_size = struct.calcsize(fmt)

        while self.running:
            r, _, _ = select.select(fds, [], [], 0.05)
            for fd in r:
                try:
                    data = os.read(fd, event_size * 8)
                    for i in range(0, len(data), event_size):
                        chunk = data[i:i + event_size]
                        if len(chunk) < event_size:
                            continue
                        _, _, ev_type, ev_code, ev_value = struct.unpack(fmt, chunk)
                        if ev_type == 1:  # EV_KEY
                            if ev_code in key_map:
                                f_key = key_map[ev_code]
                                press_type = TYPE_PRESS if ev_value == 1 else (TYPE_RELEASE if ev_value == 0 else TYPE_SHORT)
                                self.client.send_input_event(f_key, press_type)
                            elif ev_code in (314, 315, 316):  # Select / Start / Menu -> Exit
                                if ev_value == 1:
                                    self.running = False
                except Exception:
                    pass

        for fd in fds:
            try:
                os.close(fd)
            except Exception:
                pass


def run_terminal_mode(client: FlipperClient):
    """Run in terminal mode with non-blocking keyboard input."""
    renderer = TerminalRenderer()
    renderer.clear()

    # Setup non-blocking stdin
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        # Request stream start
        client.start_screen_stream()

        while True:
            # Check keyboard
            r, _, _ = select.select([sys.stdin], [], [], 0.01)
            if r:
                ch = sys.stdin.read(1)
                if ch in ("q", "\x03"):  # q or Ctrl-C
                    break
                elif ch in ("w", "W"):
                    client.send_short_click(KEY_UP)
                elif ch in ("s", "S"):
                    client.send_short_click(KEY_DOWN)
                elif ch in ("a", "A"):
                    client.send_short_click(KEY_LEFT)
                elif ch in ("d", "D"):
                    client.send_short_click(KEY_RIGHT)
                elif ch in (" ", "\r", "\n"):
                    client.send_short_click(KEY_OK)
                elif ch in ("b", "\x7f", "\x1b"):
                    client.send_short_click(KEY_BACK)

            frame = client.read_screen_frame(timeout_sec=0.03)
            if frame:
                renderer.render_frame(frame)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\033[0m\nZamknieto sesje Flipper Zero.")


def run_framebuffer_mode(client: FlipperClient):
    """Run native on TrimUI Brick using direct /dev/fb0 and evdev inputs."""
    fb = FramebufferRenderer("/dev/fb0")
    if not fb.open():
        print("[BrickFlipper] Nie mozna otworzyc /dev/fb0, przelaczam na tryb terminala.")
        run_terminal_mode(client)
        return

    inp = InputManager(client)
    inp.start_evdev_listener()

    try:
        fb.draw_ui_shell("POLACZONO (USB)")
        client.start_screen_stream()

        while inp.running:
            frame = client.read_screen_frame(timeout_sec=0.05)
            if frame:
                fb.render_flipper_frame(frame)
    except KeyboardInterrupt:
        pass
    finally:
        inp.running = False
        fb.close()


def main():
    parser = argparse.ArgumentParser(description="BrickFlipper - Flipper Zero on TrimUI Brick")
    parser.add_argument("--mode", choices=["auto", "fb", "term"], default="auto",
                        help="Tryb wyswietlania (auto, fb - framebuffer, term - terminal)")
    parser.add_argument("--port", type=str, default=None,
                        help="Port szeregowy Flippera (np. /dev/ttyACM0 lub /tmp/flipper_vserial)")
    args = parser.parse_args()

    print("==========================================")
    print("   BRICKFLIPPER dla TrimUI Brick & PC     ")
    print("==========================================")

    client = FlipperClient(port=args.port)
    if not client.connect():
        print("[!] Nie udalo sie polaczyc z Flipperem Zero.")
        print("[!] Podlacz Flippera przez USB lub uruchom symulator: python3 tools/simulate_flipper.py")
        sys.exit(1)

    # Determine mode
    mode = args.mode
    if mode == "auto":
        if os.path.exists("/dev/fb0") and os.access("/dev/fb0", os.W_OK):
            mode = "fb"
        else:
            mode = "term"

    print(f"[*] Uruchamianie w trybie: {mode.upper()}")
    try:
        if mode == "fb":
            run_framebuffer_mode(client)
        else:
            run_terminal_mode(client)
    finally:
        client.close()


if __name__ == "__main__":
    main()
