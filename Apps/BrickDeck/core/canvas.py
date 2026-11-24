"""
BrickDeck Canvas - Rich 2D Vector & Component Drawing Engine
Designed specifically for 1024x768 display on TrimUI Brick.
"""

import os
import math
import time
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont

from .theme import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HEADER_HEIGHT, FOOTER_HEIGHT,
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_ALT, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN, COLOR_STATUS_ERR
)
from .i18n import t

_FONT_CACHE: Dict[Tuple[int, bool], ImageFont.ImageFont] = {}


def get_font(size: int = 14, bold: bool = False) -> ImageFont.ImageFont:
    """Load or return cached TTF font with automatic fallback."""
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    font_candidates = [
        os.path.join(repo_root, "assets/fonts/default-bold.ttf") if bold else os.path.join(repo_root, "assets/fonts/default.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/mnt/SDCARD/System/fonts/default.ttf",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
    ]

    font = None
    for path in font_candidates:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                break
            except Exception:
                pass

    if font is None:
        font = ImageFont.load_default()

    _FONT_CACHE[key] = font
    return font


class Canvas:
    """Main double-buffered 2D drawing canvas."""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (width, height), COLOR_BG_DARK)
        self.draw = ImageDraw.Draw(self.image)
        self.anim_time = time.time()

    def clear(self, bg_color=COLOR_BG_DARK):
        """Clear canvas to background color."""
        self.draw.rectangle([(0, 0), (self.width, self.height)], fill=bg_color)

    # --------------------------------------------------------------------------
    # Framework Chrome (Header & Footer)
    # --------------------------------------------------------------------------

    def draw_header(self, active_idx: int, modules: list, sys_info: dict):
        """Draw top navigation header with tabs and status icons."""
        # Header background
        self.draw.rectangle([(0, 0), (self.width, HEADER_HEIGHT)], fill=(18, 22, 30, 255))
        # Accent glowing bottom line
        self.draw.line([(0, HEADER_HEIGHT - 2), (self.width, HEADER_HEIGHT - 2)], fill=COLOR_BORDER, width=1)
        self.draw.line([(0, HEADER_HEIGHT - 1), (self.width, HEADER_HEIGHT - 1)], fill=(0, 216, 255, 120), width=1)

        # Brand Logo on left
        font_brand = get_font(15, bold=True)
        self.draw.text((16, 16), "⚡ BRICKDECK", fill=COLOR_CYBER_CYAN, font=font_brand)

        # Space constraints for tab carousel
        tab_start_x = 195
        telemetry_w = 210
        tab_end_x = self.width - telemetry_w - 45  # ~769 px
        max_tab_space = tab_end_x - tab_start_x

        # Calculate widths and localized labels for all tabs
        tab_widths = []
        tab_labels = []
        for mod in modules:
            mod_id = getattr(mod, "id", None) or mod.__class__.__module__.split(".")[-1]
            short_lbl = t(f"modules.{mod_id}", getattr(mod, "short_name", "Mod"))
            lbl = f"{mod.icon} {short_lbl}"
            tab_labels.append(lbl)
            w = max(68, len(lbl) * 8 + 18)
            tab_widths.append(w)

        total_needed = sum(tab_widths) + (len(modules) - 1) * 6

        # Determine visible slice of tabs
        if total_needed <= max_tab_space:
            start_i = 0
            end_i = len(modules)
        else:
            # Sliding window centered around active_idx
            start_i = active_idx
            cur_w = tab_widths[active_idx]
            end_i = active_idx + 1

            expanded = True
            while expanded:
                expanded = False
                if start_i > 0:
                    cand_w = cur_w + 6 + tab_widths[start_i - 1]
                    if cand_w <= max_tab_space:
                        start_i -= 1
                        cur_w = cand_w
                        expanded = True
                if end_i < len(modules):
                    cand_w = cur_w + 6 + tab_widths[end_i]
                    if cand_w <= max_tab_space:
                        end_i += 1
                        cur_w = cand_w
                        expanded = True

        # Draw L1 bumper badge
        l1_x = 148
        self.draw_badge(l1_x, 14, "L1", bg_color=(36, 44, 58), text_color=COLOR_CYBER_CYAN)
        if start_i > 0:
            self.draw.text((l1_x + 36, 16), "‹", fill=COLOR_CYBER_CYAN, font=get_font(15, bold=True))

        # Render visible tabs
        cur_x = tab_start_x
        font_tab = get_font(12, bold=False)
        font_tab_active = get_font(12, bold=True)

        for i in range(start_i, end_i):
            mod = modules[i]
            is_active = (i == active_idx)
            label = tab_labels[i]
            tab_w = tab_widths[i]

            if is_active:
                self.draw.rounded_rectangle(
                    [(cur_x, 8), (cur_x + tab_w, HEADER_HEIGHT - 8)],
                    radius=8,
                    fill=(32, 42, 58, 255),
                    outline=mod.accent_color,
                    width=2
                )
                self.draw.text((cur_x + 8, 16), label, fill=COLOR_TEXT_PRIMARY, font=font_tab_active)
            else:
                self.draw.text((cur_x + 8, 16), label, fill=COLOR_TEXT_SECONDARY, font=font_tab)

            cur_x += tab_w + 6

        # Draw R1 bumper badge and right indicator
        r1_x = tab_end_x + 8
        if end_i < len(modules):
            self.draw.text((cur_x + 2, 16), "›", fill=COLOR_CYBER_CYAN, font=get_font(15, bold=True))
        self.draw_badge(r1_x, 14, "R1", bg_color=(36, 44, 58), text_color=COLOR_CYBER_CYAN)

        # Right-side telemetry: Battery %, Time, Status
        clock_str = time.strftime("%H:%M")
        bat_str = f"🔋 {sys_info.get('battery', 85)}%"
        wifi_str = "📶" if sys_info.get('wifi', True) else "🚫"

        font_stat = get_font(13, bold=True)
        self.draw.text((self.width - 200, 16), f"{wifi_str}  {bat_str}  🕒 {clock_str}",
                       fill=COLOR_TEXT_PRIMARY, font=font_stat)

    def draw_footer(self, hints: List[Tuple[str, str]]):
        """Draw bottom bar with dynamic gamepad control badges."""
        y_top = SCREEN_HEIGHT - FOOTER_HEIGHT
        # Footer background
        self.draw.rectangle([(0, y_top), (self.width, SCREEN_HEIGHT)], fill=(18, 22, 30, 255))
        self.draw.line([(0, y_top), (self.width, y_top)], fill=COLOR_BORDER, width=1)

        x = 20
        font_btn = get_font(11, bold=True)
        font_desc = get_font(13, bold=False)

        for btn_badge, desc in hints:
            # Localize description if translation exists
            desc_trans = t(f"common.{desc.lower()}", t(desc, desc))
            # Badge pill
            badge_w = len(btn_badge) * 8 + 14
            self.draw.rounded_rectangle(
                [(x, y_top + 10), (x + badge_w, y_top + 34)],
                radius=6,
                fill=(40, 48, 64),
                outline=COLOR_CYBER_CYAN,
                width=1
            )
            self.draw.text((x + 7, y_top + 14), btn_badge, fill=COLOR_CYBER_CYAN, font=font_btn)
            x += badge_w + 8

            # Description
            self.draw.text((x, y_top + 14), str(desc_trans), fill=COLOR_TEXT_PRIMARY, font=font_desc)
            x += len(str(desc_trans)) * 8 + 24

        # Menu / Exit hint on far right
        exit_str = f"[MENU]: {t('common.exit', 'Wyjscie')}"
        self.draw.text((self.width - 160, y_top + 14), exit_str, fill=COLOR_TEXT_MUTED, font=font_btn)

    # --------------------------------------------------------------------------
    # Standard UI Components
    # --------------------------------------------------------------------------

    def draw_card(self, x: int, y: int, w: int, h: int, title: str = "", subtitle: str = "",
                  border_color=COLOR_BORDER, fill_color=COLOR_PANEL_BG, radius: int = 10):
        """Draw a tactical rounded panel/card with optional header."""
        self.draw.rounded_rectangle(
            [(x, y), (x + w, y + h)],
            radius=radius,
            fill=fill_color,
            outline=border_color,
            width=2
        )
        if title:
            font_title = get_font(15, bold=True)
            self.draw.text((x + 16, y + 14), title, fill=COLOR_TEXT_PRIMARY, font=font_title)
            if subtitle:
                font_sub = get_font(12, bold=False)
                self.draw.text((x + 16 + len(title) * 9 + 12, y + 16), subtitle, fill=COLOR_TEXT_SECONDARY, font=font_sub)
            self.draw.line([(x + 12, y + 42), (x + w - 12, y + 42)], fill=COLOR_BORDER, width=1)

    def draw_badge(self, x: int, y: int, text: str, bg_color=(40, 50, 70), text_color=COLOR_TEXT_PRIMARY):
        """Draw small rounded badge pill."""
        font = get_font(11, bold=True)
        bw = len(text) * 8 + 12
        bh = 22
        self.draw.rounded_rectangle([(x, y), (x + bw, y + bh)], radius=5, fill=bg_color)
        self.draw.text((x + 6, y + 4), text, fill=text_color, font=font)

    def draw_gauge(self, x: int, y: int, w: int, h: int, value: float, max_val: float,
                   label: str = "", color=COLOR_CYBER_CYAN):
        """Draw a progress / meter bar."""
        ratio = max(0.0, min(1.0, value / max(max_val, 0.001)))
        # Background slot
        self.draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=h // 2, fill=(28, 34, 46))
        # Filled part
        fill_w = int(w * ratio)
        if fill_w > h:
            self.draw.rounded_rectangle([(x, y), (x + fill_w, y + h)], radius=h // 2, fill=color)

        if label:
            font = get_font(12, bold=False)
            self.draw.text((x, y - 18), label, fill=COLOR_TEXT_SECONDARY, font=font)
            val_text = f"{int(value)} / {int(max_val)}"
            self.draw.text((x + w - len(val_text) * 8, y - 18), val_text, fill=COLOR_TEXT_PRIMARY, font=font)

    # --------------------------------------------------------------------------
    # Specialized Tactical Widgets
    # --------------------------------------------------------------------------

    def draw_radar(self, cx: int, cy: int, radius: int, sweep_angle: float, blips: list):
        """
        Draw animated tactical radar.
        blips: list of dicts: {'angle': float, 'dist': float (0..1), 'label': str, 'rssi': int}
        """
        # Outer border ring
        self.draw.ellipse([(cx - radius, cy - radius), (cx + radius, cy + radius)],
                          outline=(0, 216, 255, 180), width=2)
        # Inner range rings (25%, 50%, 75%)
        for ring_pct in [0.25, 0.50, 0.75]:
            r_inner = int(radius * ring_pct)
            self.draw.ellipse([(cx - r_inner, cy - r_inner), (cx + r_inner, cy + r_inner)],
                              outline=(32, 64, 88, 255), width=1)

        # Crosshairs
        self.draw.line([(cx - radius, cy), (cx + radius, cy)], fill=(32, 64, 88, 255), width=1)
        self.draw.line([(cx, cy - radius), (cx, cy + radius)], fill=(32, 64, 88, 255), width=1)

        # Radar Sweep Beam
        rad = math.radians(sweep_angle)
        sx = cx + int(radius * math.cos(rad))
        sy = cy + int(radius * math.sin(rad))
        self.draw.line([(cx, cy), (sx, sy)], fill=COLOR_CYBER_CYAN, width=3)

        # Blips (targets)
        font_blip = get_font(11, bold=True)
        for b in blips:
            b_rad = math.radians(b['angle'])
            b_dist = max(0.1, min(0.95, b['dist'])) * radius
            bx = cx + int(b_dist * math.cos(b_rad))
            by = cy + int(b_dist * math.sin(b_rad))

            # Pulse dot
            color = COLOR_FLIPPER_AMBER if "Flipper" in b.get('label', '') else COLOR_NEON_PINK
            self.draw.ellipse([(bx - 5, by - 5), (bx + 5, by + 5)], fill=color)
            self.draw.ellipse([(bx - 8, by - 8), (bx + 8, by + 8)], outline=color, width=1)

            # Label
            label = b.get('label', 'Device')
            self.draw.text((bx + 10, by - 6), label, fill=COLOR_TEXT_PRIMARY, font=font_blip)

    def draw_bar_chart(self, x: int, y: int, w: int, h: int, labels: list, values: list,
                       max_val: float, active_idx: int = -1, bar_color=COLOR_CYBER_CYAN):
        """Draw bar chart (e.g. Wi-Fi channel spectrum 1..14)."""
        num_bars = len(values)
        if num_bars == 0:
            return

        bar_width = max(10, (w - (num_bars * 8)) // num_bars)
        font = get_font(11, bold=False)

        # Zero baseline
        self.draw.line([(x, y + h), (x + w, y + h)], fill=COLOR_BORDER, width=1)

        cur_x = x
        for i, val in enumerate(values):
            ratio = max(0.0, min(1.0, val / max(max_val, 1.0)))
            bar_h = int(h * ratio)
            bar_y = y + h - bar_h

            color = COLOR_FLIPPER_AMBER if i == active_idx else bar_color
            if bar_h > 0:
                self.draw.rounded_rectangle(
                    [(cur_x, bar_y), (cur_x + bar_width, y + h)],
                    radius=4,
                    fill=color
                )

            # Label under bar
            if i < len(labels):
                lbl = str(labels[i])
                self.draw.text((cur_x + 4, y + h + 6), lbl, fill=COLOR_TEXT_SECONDARY, font=font)

            cur_x += bar_width + 8

    def draw_spectrum(self, x: int, y: int, w: int, h: int, values: list, peaks: list = None,
                      bar_color=COLOR_CYBER_CYAN, peak_color=COLOR_FLIPPER_AMBER):
        """Draw dynamic 32-band audio equalizer spectrum."""
        num_bars = len(values)
        if num_bars == 0:
            return
        gap = 3
        bar_width = max(3, (w - (num_bars * gap)) // num_bars)
        # Background slot box
        self.draw.rectangle([(x, y), (x + w, y + h)], fill=(16, 20, 28))
        self.draw.line([(x, y + h), (x + w, y + h)], fill=COLOR_BORDER, width=1)

        cur_x = x + 4
        for i, val in enumerate(values):
            norm = max(0.0, min(1.0, val))
            bh = int(h * norm)
            by = y + h - bh
            b_col = COLOR_NEON_PINK if norm > 0.85 else (COLOR_FLIPPER_AMBER if norm > 0.6 else bar_color)
            if bh > 0:
                self.draw.rectangle([(cur_x, by), (cur_x + bar_width, y + h)], fill=b_col)
            if peaks and i < len(peaks):
                p_norm = max(0.0, min(1.0, peaks[i]))
                py = y + h - int(h * p_norm)
                self.draw.line([(cur_x, py), (cur_x + bar_width, py)], fill=peak_color, width=2)
            cur_x += bar_width + gap

    def draw_oscilloscope(self, x: int, y: int, w: int, h: int, points: list, color=COLOR_PHOSPHOR_GREEN):
        """Draw retro phosphor green oscilloscope beam."""
        self.draw.rectangle([(x, y), (x + w, y + h)], fill=(10, 16, 12), outline=(20, 48, 28), width=1)
        mid_y = y + h // 2
        self.draw.line([(x, mid_y), (x + w, mid_y)], fill=(18, 40, 24), width=1)
        if len(points) < 2:
            return
        step = w / max(1, len(points) - 1)
        for i in range(len(points) - 1):
            x1 = int(x + i * step)
            y1 = int(mid_y + points[i] * (h // 2 - 6))
            x2 = int(x + (i + 1) * step)
            y2 = int(mid_y + points[i + 1] * (h // 2 - 6))
            self.draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

    def draw_vu_meter(self, x: int, y: int, w: int, h: int, left_db: float, right_db: float):
        """Draw stereo analog/cyber VU meter (-40dB to +6dB)."""
        ch_h = (h - 8) // 2
        for ch_idx, (val, label) in enumerate([(left_db, "L"), (right_db, "R")]):
            cy = y + ch_idx * (ch_h + 8)
            self.draw.text((x, cy + 2), label, fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
            slot_x = x + 20
            slot_w = w - 24
            self.draw.rectangle([(slot_x, cy), (slot_x + slot_w, cy + ch_h)], fill=(20, 24, 32), outline=COLOR_BORDER)
            norm = max(0.0, min(1.0, (val + 40.0) / 46.0))
            fill_w = int(slot_w * norm)
            split_green = int(slot_w * 0.82)
            if fill_w > 0:
                g_part = min(fill_w, split_green)
                self.draw.rectangle([(slot_x, cy), (slot_x + g_part, cy + ch_h)], fill=COLOR_CYBER_CYAN)
                if fill_w > split_green:
                    self.draw.rectangle([(slot_x + split_green, cy), (slot_x + fill_w, cy + ch_h)], fill=COLOR_NEON_PINK)
            self.draw.line([(slot_x + split_green, cy - 2), (slot_x + split_green, cy + ch_h + 2)], fill=COLOR_TEXT_PRIMARY, width=1)

    # --------------------------------------------------------------------------
    # Output Conversion
    # --------------------------------------------------------------------------

    def to_bgra_bytes(self) -> bytes:
        """Convert RGBA image to 32-bit BGRA bytes for direct /dev/fb0 mmap."""
        r, g, b, a = self.image.split()
        bgra_img = Image.merge("RGBA", (b, g, r, a))
        return bgra_img.tobytes()
