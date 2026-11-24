"""
BrickDeck Display Driver
Blits Canvas frames to Framebuffer (/dev/fb0), Terminal (ANSI 24-bit), or Pygame.
"""

import os
import sys
import mmap
from typing import Optional
from PIL import Image

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class DisplayDriver:
    """Renders 1024x768 Canvas frames to hardware or virtual outputs."""

    def __init__(self, mode: str = "auto", fb_device: str = "/dev/fb0"):
        self.mode = mode
        self.fb_device = fb_device
        self.width = 1024
        self.height = 768
        self.fb_fd = None
        self.fb_mmap = None
        self.pyg_screen = None

    def initialize(self) -> str:
        """Resolve mode and initialize driver. Returns active mode."""
        if self.mode == "auto":
            if os.path.exists(self.fb_device) and os.access(self.fb_device, os.W_OK):
                self.mode = "fb"
            elif HAS_PYGAME and (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
                self.mode = "pygame"
            else:
                self.mode = "term"

        if self.mode == "fb":
            try:
                self.fb_fd = os.open(self.fb_device, os.O_RDWR)
                size = self.width * self.height * 4
                self.fb_mmap = mmap.mmap(
                    self.fb_fd, size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE
                )
                print(f"[Display] Initialized direct framebuffer: {self.fb_device}")
            except Exception as e:
                print(f"[Display] Framebuffer failed ({e}), falling back to terminal.")
                self.mode = "term"

        if self.mode == "pygame" and HAS_PYGAME:
            try:
                pygame.init()
                self.pyg_screen = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption("BrickDeck OS (TrimUI Brick Simulator)")
                print("[Display] Initialized Pygame desktop window (1024x768)")
            except Exception as e:
                print(f"[Display] Pygame init failed ({e}), falling back to terminal.")
                self.mode = "term"

        if self.mode == "term":
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            print("[Display] Initialized Terminal ANSI 24-bit TrueColor renderer.")

        return self.mode

    def render(self, canvas):
        """Present a frame from canvas."""
        if self.mode == "fb" and self.fb_mmap:
            bgra_bytes = canvas.to_bgra_bytes()
            self.fb_mmap.seek(0)
            self.fb_mmap.write(bgra_bytes)

        elif self.mode == "pygame" and self.pyg_screen:
            # Convert PIL image to Pygame surface
            raw_str = canvas.image.tobytes("raw", "RGBA")
            pyg_img = pygame.image.fromstring(raw_str, (self.width, self.height), "RGBA")
            self.pyg_screen.blit(pyg_img, (0, 0))
            pygame.display.flip()

        elif self.mode == "term":
            # Downscale 1024x768 to 128 cols x 36 text rows (72 vertical pixels)
            tw, th = 128, 70
            small = canvas.image.resize((tw, th), Image.BILINEAR)
            rgb_small = small.convert("RGB")
            raw = rgb_small.tobytes()

            lines = []
            stride = tw * 3
            for text_row in range(th // 2):
                y_top = text_row * 2
                y_bot = y_top + 1
                row_chars = []
                for x in range(tw):
                    idx_top = (y_top * stride) + (x * 3)
                    idx_bot = (y_bot * stride) + (x * 3)
                    rt, gt, bt = raw[idx_top], raw[idx_top + 1], raw[idx_top + 2]
                    rb, gb, bb = raw[idx_bot], raw[idx_bot + 1], raw[idx_bot + 2]
                    row_chars.append(f"\033[38;2;{rt};{gt};{bt};48;2;{rb};{gb};{bb}m▀")
                row_chars.append("\033[0m")
                lines.append("".join(row_chars))

            sys.stdout.write("\033[H" + "\n".join(lines) + "\n")
            sys.stdout.flush()

    def close(self):
        """Cleanup resources."""
        if self.fb_mmap:
            try:
                self.fb_mmap.seek(0)
                self.fb_mmap.write(b"\x00" * (self.width * self.height * 4))
                self.fb_mmap.close()
            except Exception:
                pass
        if self.fb_fd is not None:
            try:
                os.close(self.fb_fd)
            except Exception:
                pass
        if HAS_PYGAME and self.pyg_screen:
            try:
                pygame.quit()
            except Exception:
                pass
        if self.mode == "term":
            sys.stdout.write("\033[0m\n")
            sys.stdout.flush()
