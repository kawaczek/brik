"""
BrickDeck Module: Tactical Inspection Camera & Borescope Monitor (CamScope)
Portable video monitor for USB-C OTG endoscopes, inspection cameras, webcams, and Wi-Fi IP streams.
Features optical zoom, night vision / false color thermal filters, edge detection, measurement graticules, and snapshots.
"""

import os
import io
import time
import math
import glob
import threading
import urllib.request
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageEnhance

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN, COLOR_STATUS_ERR
)
from core.canvas import get_font
from core.i18n import t

# Screenshot / Snapshot Save Directory
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "captures")
SD_CAPTURES_DIR = "/mnt/SDCARD/Photos"

FILTER_NAMES = [
    ("Normalny (RGB)", "Naturalny obraz z sensora"),
    ("Noktowizor (Green)", "Zielony luminofor + kontrast do ciemnych szczelin"),
    ("Termowizja (False Color)", "Intensywność podczerwieni / ciepła (Pseudo-IR)"),
    ("Monochromatyczny (B&W)", "Czysty kontrast bez dystrakcji kolorystycznych"),
    ("Detekcja Krawędzi (Edges)", "Wykrywanie pęknięć, zarysowań i ścieżek PCB")
]

GRATICULE_NAMES = ["Brak (Czysty podgląd)", "Celownik Precyzyjny", "Siatka Milimetrowa", "Okręgi Koncentryczne"]
ZOOM_LEVELS = [1.0, 1.5, 2.0, 4.0]


class CameraModule(BaseModule):
    name = "Tactical Inspection Cam (Borescope)"
    short_name = "CamScope"
    icon = "📹"
    accent_color = COLOR_FLIPPER_AMBER

    def __init__(self, app_context=None):
        super().__init__(app_context)
        # Capture States
        self.source_mode = 0  # 0: Auto (USB OTG /dev/video* -> Simulator fallback), 1: Wi-Fi IP Cam (MJPEG), 2: Simulator
        self.source_names = ["USB-C OTG Kamera", "Wi-Fi IP Cam (MJPEG)", "Symulacja Inspekcyjna"]
        self.device_node: Optional[str] = None
        self.ip_cam_url = "http://192.168.1.100:8080/video"

        # Vision Adjustments
        self.filter_idx = 0
        self.graticule_idx = 1  # Default Crosshair
        self.zoom_idx = 0
        self.brightness_bias = 0.0  # -0.5 to +0.5
        self.pan_x = 0
        self.pan_y = 0

        # Snapshot notification
        self.snapshot_toast = ""
        self.snapshot_toast_time = 0.0
        self.snapshot_count = 0

        # Video Threading
        self.thread_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.current_frame: Optional[Image.Image] = None
        self.fps = 30
        self.frame_counter = 0
        self.last_fps_time = time.time()
        self.is_hardware_connected = False

        # Prepare captures directory
        try:
            os.makedirs(CAPTURES_DIR, exist_ok=True)
        except Exception:
            pass

    def on_load(self):
        self.thread_running = True
        self.worker_thread = threading.Thread(target=self._capture_worker, daemon=True)
        self.worker_thread.start()

    def get_hotkey_hints(self):
        filter_name = FILTER_NAMES[self.filter_idx][0].split()[0]
        zoom_val = f"{ZOOM_LEVELS[self.zoom_idx]:.1f}x"
        return [
            ("L1/R1", t("common.modules", "Moduly")),
            ("A", t("camera.capture_hint", "Zrob zdjecie")),
            ("X", f"{t('camera.filter_label', 'Filtr')}: {filter_name}"),
            ("Y", t("camera.graticule", "Siatka")),
            ("D-Pad L/P", f"{t('common.zoom', 'Zoom')}: {zoom_val}"),
            ("B", t("common.back", "Wroc"))
        ]

    def _check_hardware_device(self) -> Optional[str]:
        """Detect USB video nodes (/dev/video0, /dev/video1...)."""
        nodes = sorted(glob.glob("/dev/video*"))
        return nodes[0] if nodes else None

    def _generate_synthetic_pcb_frame(self, t: float) -> Image.Image:
        """High-resolution realistic macro inspection view of PCB electronics."""
        base_w, base_h = 640, 480
        img = Image.new("RGB", (base_w, base_h), (18, 48, 28))  # Classic Green Solder Mask
        draw = ImageDraw.Draw(img)

        # Copper Traces (Gold / Yellow tracks)
        for i in range(12):
            y_pos = 40 + i * 36
            draw.line([(0, y_pos), (180, y_pos), (240, y_pos + 20), (base_w, y_pos + 20)], fill=(180, 150, 40), width=3)
            # Via holes
            draw.ellipse([(177, y_pos - 3), (183, y_pos + 3)], fill=(220, 190, 80), outline=(100, 80, 20))
            draw.ellipse([(237, y_pos + 17), (243, y_pos + 23)], fill=(220, 190, 80), outline=(100, 80, 20))

        # Big Main Microcontroller QFP Chip (Center: 320, 240)
        cx, cy = 320, 240
        chip_w, chip_h = 160, 160
        draw.rectangle([(cx - chip_w // 2, cy - chip_h // 2), (cx + chip_w // 2, cy + chip_h // 2)], fill=(22, 22, 24), outline=(40, 40, 45), width=2)
        # Orientation notch
        draw.ellipse([(cx - chip_w // 2 + 8, cy - chip_h // 2 + 8), (cx - chip_w // 2 + 20, cy - chip_h // 2 + 20)], fill=(12, 12, 14))

        # Chip Laser Marking text
        font_ic = get_font(12, bold=True)
        draw.text((cx - 60, cy - 20), "ALLWINNER A133P", fill=(160, 160, 170), font=font_ic)
        draw.text((cx - 50, cy + 2), "ARM64 CORTEX-A53", fill=(120, 120, 130), font=get_font(10, bold=False))
        draw.text((cx - 40, cy + 20), "T62611-2026A", fill=(90, 90, 100), font=get_font(9, bold=False))

        # QFP Pins (Solder leads on all 4 sides)
        pin_col = (200, 205, 215)
        for p in range(16):
            offset = -70 + p * 9
            # Top & Bottom pins
            draw.rectangle([(cx + offset, cy - chip_h // 2 - 12), (cx + offset + 4, cy - chip_h // 2)], fill=pin_col)
            draw.rectangle([(cx + offset, cy + chip_h // 2), (cx + offset + 4, cy + chip_h // 2 + 12)], fill=pin_col)
            # Left & Right pins
            draw.rectangle([(cx - chip_w // 2 - 12, cy + offset), (cx - chip_w // 2, cy + offset + 4)], fill=pin_col)
            draw.rectangle([(cx + chip_w // 2, cy + offset), (cx + chip_w // 2 + 12, cy + offset + 4)], fill=pin_col)

        # SMD Capacitors & Resistors (0805 components)
        smd_list = [
            (100, 80, "C104", (160, 120, 70)),
            (100, 140, "R470", (30, 30, 30)),
            (100, 200, "C22", (160, 120, 70)),
            (520, 80, "L1", (40, 70, 90)),
            (520, 140, "R10k", (30, 30, 30)),
            (520, 360, "ESD1", (20, 20, 20)),
            (220, 380, "C10", (160, 120, 70)),
            (320, 390, "OSC_24M", (180, 180, 190))
        ]
        for sx, sy, lbl, bcol in smd_list:
            draw.rectangle([(sx - 14, sy - 8), (sx + 14, sy + 8)], fill=bcol, outline=(50, 50, 50))
            # Silver solder terminations
            draw.rectangle([(sx - 14, sy - 8), (sx - 9, sy + 8)], fill=(210, 215, 225))
            draw.rectangle([(sx + 9, sy - 8), (sx + 14, sy + 8)], fill=(210, 215, 225))
            draw.text((sx - 12, sy + 10), lbl, fill=(180, 200, 180), font=get_font(9, bold=False))

        # Simulated LED Ring-Light Glare Reflection (Moving subtly with time)
        glare_cx = int(cx + math.sin(t * 0.8) * 80)
        glare_cy = int(cy + math.cos(t * 0.8) * 60)
        draw.ellipse([(glare_cx - 50, glare_cy - 50), (glare_cx + 50, glare_cy + 50)],
                     outline=(255, 255, 255, 60), width=3)

        return img

    def _capture_worker(self):
        """Continuously pulls frames from hardware USB device or generates synthetic feed."""
        t_start = time.time()
        while self.thread_running:
            now = time.time()
            elapsed = now - t_start

            # Check if USB video device appeared
            dev = self._check_hardware_device()
            self.device_node = dev
            self.is_hardware_connected = (dev is not None)

            raw_frame = None

            # 1. Try Hardware USB Read if present and in Auto mode
            if self.is_hardware_connected and self.source_mode == 0:
                try:
                    # Non-blocking probe read
                    with open(dev, "rb") as f:
                        chunk = f.read(131072)
                        # Check for JPEG Start of Image marker
                        soi = chunk.find(b"\xff\xd8\xff")
                        if soi != -1:
                            eoi = chunk.find(b"\xff\xd9", soi)
                            if eoi != -1:
                                raw_frame = Image.open(io.BytesIO(chunk[soi:eoi+2]))
                except Exception:
                    raw_frame = None

            # 2. Try Wi-Fi IP Camera if selected
            elif self.source_mode == 1:
                try:
                    req = urllib.request.Request(self.ip_cam_url, headers={"User-Agent": "BrickDeck/1.0"})
                    with urllib.request.urlopen(req, timeout=1.5) as resp:
                        data = resp.read()
                        raw_frame = Image.open(io.BytesIO(data))
                except Exception:
                    raw_frame = None

            # 3. Fallback to Inspection Simulator
            if raw_frame is None:
                raw_frame = self._generate_synthetic_pcb_frame(elapsed)

            self.current_frame = raw_frame
            self.frame_counter += 1

            # Compute actual FPS
            if now - self.last_fps_time >= 1.0:
                self.fps = self.frame_counter
                self.frame_counter = 0
                self.last_fps_time = now

            time.sleep(0.033)  # ~30 FPS throttle

    def update(self, dt: float):
        if self.snapshot_toast and (time.time() - self.snapshot_toast_time > 2.5):
            self.snapshot_toast = ""

    def _apply_vision_filters(self, img: Image.Image) -> Image.Image:
        """Apply active visual enhancements (Night vision, thermal, edge detection, brightness)."""
        # 1. Digital Brightness / Exposure Bias
        if abs(self.brightness_bias) > 0.05:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(max(0.2, 1.0 + self.brightness_bias))

        # 2. Optical Filters
        if self.filter_idx == 0:
            return img
        elif self.filter_idx == 1:
            # Green Phosphor Night Vision
            gray = ImageOps.grayscale(img)
            return ImageOps.colorize(gray, black=(0, 20, 4), white=(40, 255, 60))
        elif self.filter_idx == 2:
            # Pseudo-Thermal False Color
            gray = ImageOps.grayscale(img)
            return ImageOps.colorize(gray, black=(20, 0, 80), mid=(240, 60, 20), white=(255, 255, 120))
        elif self.filter_idx == 3:
            # High-Contrast Monochrome
            gray = ImageOps.grayscale(img)
            enhancer = ImageEnhance.Contrast(gray)
            return enhancer.enhance(1.6).convert("RGB")
        elif self.filter_idx == 4:
            # Sobel / Laplac Edge Detection
            gray = ImageOps.grayscale(img)
            edges = gray.filter(ImageFilter.FIND_EDGES)
            enhancer = ImageEnhance.Contrast(edges)
            high_edges = enhancer.enhance(2.0)
            return ImageOps.colorize(high_edges, black=(10, 14, 20), white=(0, 220, 255))
        return img

    def _draw_measurement_overlay(self, draw: ImageDraw.ImageDraw, vx: int, vy: int, vw: int, vh: int):
        """Draw tactical measurement reticles, millimeter grids, and scales."""
        cx = vx + vw // 2
        cy = vy + vh // 2

        if self.graticule_idx == 1:
            # Crosshair Reticle with Millimeter Hash Marks
            # Horizontal crosshair
            draw.line([(vx + 40, cy), (vx + vw - 40, cy)], fill=(0, 216, 255, 180), width=1)
            # Vertical crosshair
            draw.line([(cx, vy + 30), (cx, vy + vh - 30)], fill=(0, 216, 255, 180), width=1)
            # Center Target Box
            draw.rectangle([(cx - 16, cy - 16), (cx + 16, cy + 16)], outline=COLOR_FLIPPER_AMBER, width=2)
            draw.ellipse([(cx - 2, cy - 2), (cx + 2, cy + 2)], fill=COLOR_FLIPPER_AMBER)

            # 10px tick marks along crosshairs
            for tick in range(-180, 181, 20):
                if tick != 0:
                    draw.line([(cx + tick, cy - 4), (cx + tick, cy + 4)], fill=COLOR_CYBER_CYAN, width=1)
                    draw.line([(cx - 4, cy + tick), (cx + 4, cy + tick)], fill=COLOR_CYBER_CYAN, width=1)

            draw.text((cx + 22, cy + 8), "XY: (0, 0)", fill=COLOR_CYBER_CYAN, font=get_font(10, bold=True))

        elif self.graticule_idx == 2:
            # Millimeter Engineering Grid (40px square grid)
            grid_col = (0, 216, 255, 70)
            for gx in range(vx, vx + vw, 40):
                draw.line([(gx, vy), (gx, vy + vh)], fill=grid_col, width=1)
            for gy in range(vy, vy + vh, 40):
                draw.line([(vx, gy), (vx + vw, gy)], fill=grid_col, width=1)
            # Baseline axes
            draw.line([(cx, vy), (cx, vy + vh)], fill=(255, 138, 0, 140), width=1)
            draw.line([(vx, cy), (vx + vw, cy)], fill=(255, 138, 0, 140), width=1)
            draw.text((vx + 12, vy + 10), "PODZIAŁKA SIATKI: 1.0 mm / DIV", fill=COLOR_CYBER_CYAN, font=get_font(10, bold=True))

        elif self.graticule_idx == 3:
            # Concentric Radar/Inspection Circles
            for r in [40, 80, 130, 190]:
                draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(0, 216, 255, 120), width=1)
                draw.text((cx + r - 20, cy - 14), f"r={r//2}mm", fill=(0, 216, 255, 180), font=get_font(9, bold=False))
            draw.line([(cx - 200, cy), (cx + 200, cy)], fill=(0, 216, 255, 120), width=1)
            draw.line([(cx, cy - 200), (cx, cy + 200)], fill=(0, 216, 255, 120), width=1)

    def _save_snapshot(self):
        """Save high-resolution snapshot to SD card or captures dir."""
        if not self.current_frame:
            return
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = f"CAP_{ts}.png"
        filepath = os.path.join(CAPTURES_DIR, filename)

        try:
            # Apply current optical filter and save original resolution
            filtered = self._apply_vision_filters(self.current_frame.copy())
            filtered.save(filepath, format="PNG")
            self.snapshot_count += 1
            self.snapshot_toast = f"📸 ZAPISANO ZDJĘCIE: {filename}"
            self.snapshot_toast_time = time.time()
        except Exception as e:
            self.snapshot_toast = f"Błąd zapisu: {e}"
            self.snapshot_toast_time = time.time()

    def render(self, canvas):
        card_w_left = 680
        card_w_right = 270

        # Viewport dimensions on screen
        vx = 44
        vy = 118
        vw = 656
        vh = 560

        # ----------------------------------------------------------------------
        # Left Panel: Main Video Viewport & Borescope Feed
        # ----------------------------------------------------------------------
        canvas.draw_card(
            32, 66, card_w_left, 634,
            title="TACTICAL INSPECTION CAMERA & CAM MONITOR",
            subtitle=f"Źródło: {self.source_names[self.source_mode]}  |  Status: LIVE ({self.fps} FPS)",
            border_color=self.accent_color
        )

        # Draw Video Frame
        if self.current_frame:
            # 1. Apply Digital Zoom (Crop into center)
            zoom = ZOOM_LEVELS[self.zoom_idx]
            frame_img = self.current_frame

            if zoom > 1.0:
                fw, fh = frame_img.size
                cw = int(fw / zoom)
                ch = int(fh / zoom)
                cx = fw // 2 + self.pan_x
                cy = fh // 2 + self.pan_y
                box = (max(0, cx - cw // 2), max(0, cy - ch // 2),
                       min(fw, cx + cw // 2), min(fh, cy + ch // 2))
                frame_img = frame_img.crop(box)

            # 2. Apply Vision Filters (Night vision, thermal, edges)
            processed_img = self._apply_vision_filters(frame_img)

            # 3. Scale to 656x560 Viewport
            scaled_feed = processed_img.resize((vw, vh), Image.BILINEAR)
            canvas.image.paste(scaled_feed, (vx, vy))

        # Outer Viewport Bezel
        canvas.draw.rectangle([(vx, vy), (vx + vw, vy + vh)], outline=COLOR_BORDER_LIGHT, width=2)

        # Draw Tactical HUD Overlays directly over camera feed
        canvas.draw_badge(vx + 14, vy + 12, f"● CAM1: LIVE ({self.fps} FPS)", bg_color=(20, 100, 50, 220), text_color=COLOR_TEXT_PRIMARY)
        canvas.draw_badge(vx + 180, vy + 12, f"ZOOM: {ZOOM_LEVELS[self.zoom_idx]:.1f}x", bg_color=(36, 48, 64, 220), text_color=COLOR_CYBER_CYAN)

        exp_str = f"EKSP: {self.brightness_bias:+.0%}" if abs(self.brightness_bias) > 0.05 else "EKSP: AUTO"
        canvas.draw_badge(vx + vw - 140, vy + 12, exp_str, bg_color=(36, 48, 64, 220), text_color=COLOR_FLIPPER_AMBER)

        # Draw Measurement Graticule / Crosshair
        if self.graticule_idx > 0:
            self._draw_measurement_overlay(canvas.draw, vx, vy, vw, vh)

        # Snapshot Toast Alert Banner (Centered bottom of camera feed)
        if self.snapshot_toast:
            tw = len(self.snapshot_toast) * 8 + 32
            tx = vx + (vw - tw) // 2
            ty = vy + vh - 48
            canvas.draw.rounded_rectangle([(tx, ty), (tx + tw, ty + 36)], radius=8, fill=(20, 30, 42, 240), outline=COLOR_STATUS_OK, width=2)
            canvas.draw.text((tx + 16, ty + 10), self.snapshot_toast, fill=COLOR_STATUS_OK, font=get_font(12, bold=True))

        # ----------------------------------------------------------------------
        # Right Panel: Optical Enhancements, Graticules, and Snapshot Controls
        # ----------------------------------------------------------------------
        canvas.draw_card(
            722, 66, card_w_right, 634,
            title="KONTROLA OBIEKTYWU",
            subtitle="Filtry & Narzędzia",
            border_color=COLOR_BORDER
        )

        rx = 738
        ry = 118
        rw = card_w_right - 32

        # 1. Video Source Card
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + 105)], radius=8, fill=(22, 28, 38), outline=COLOR_CYBER_CYAN, width=1)
        canvas.draw.text((rx + 12, ry + 10), "AKTYWNE WEJŚCIE WIDEO:", fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=True))
        canvas.draw.text((rx + 12, ry + 26), f"📷 {self.source_names[self.source_mode]}", fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))

        hw_txt = f"Węzeł: {self.device_node}" if self.is_hardware_connected else "Brak USB (Symulacja)"
        hw_col = COLOR_STATUS_OK if self.is_hardware_connected else COLOR_FLIPPER_AMBER
        canvas.draw.text((rx + 12, ry + 48), hw_txt, fill=hw_col, font=get_font(11, bold=False))
        canvas.draw_badge(rx + 12, ry + 72, "[B] ZMIEŃ ŹRÓDŁO", bg_color=(36, 48, 64), text_color=COLOR_CYBER_CYAN)

        # 2. Optical Filters Card
        fil_y = ry + 116
        canvas.draw.rounded_rectangle([(rx, fil_y), (rx + rw, fil_y + 160)], radius=8, fill=(20, 24, 34), outline=COLOR_FLIPPER_AMBER, width=1)
        canvas.draw.text((rx + 12, fil_y + 10), "FILTR OPTYCZNY (KLAWISZ X):", fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))

        cur_fil_name, cur_fil_desc = FILTER_NAMES[self.filter_idx]
        canvas.draw.text((rx + 12, fil_y + 30), cur_fil_name, fill=COLOR_TEXT_PRIMARY, font=get_font(14, bold=True))
        canvas.draw.text((rx + 12, fil_y + 52), cur_fil_desc, fill=COLOR_TEXT_SECONDARY, font=get_font(10, bold=False))

        # Filter List Indicators
        f_row_y = fil_y + 74
        for f_i, (f_n, _) in enumerate(FILTER_NAMES):
            is_active = (f_i == self.filter_idx)
            dot_col = COLOR_FLIPPER_AMBER if is_active else (60, 70, 80)
            canvas.draw.ellipse([(rx + 14, f_row_y + 3), (rx + 22, f_row_y + 11)], fill=dot_col)
            canvas.draw.text((rx + 28, f_row_y), f_n.split()[0], fill=COLOR_TEXT_PRIMARY if is_active else COLOR_TEXT_MUTED, font=get_font(11, bold=is_active))
            f_row_y += 16

        # 3. Measurement Graticule Card
        grat_y = fil_y + 170
        canvas.draw.rounded_rectangle([(rx, grat_y), (rx + rw, grat_y + 100)], radius=8, fill=(18, 22, 30), outline=COLOR_BORDER)
        canvas.draw.text((rx + 12, grat_y + 10), "SIATKA POMIAROWA (KLAWISZ Y):", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))
        canvas.draw.text((rx + 12, grat_y + 30), GRATICULE_NAMES[self.graticule_idx], fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))
        canvas.draw.text((rx + 12, grat_y + 52), "Pomiar szczelin, ścieżek i ubytków", fill=COLOR_TEXT_MUTED, font=get_font(10, bold=False))

        # 4. Snapshots & Gallery Card
        snap_y = grat_y + 110
        canvas.draw.rounded_rectangle([(rx, snap_y), (rx + rw, snap_y + 120)], radius=8, fill=(20, 26, 36), outline=COLOR_STATUS_OK, width=1)
        canvas.draw.text((rx + 12, snap_y + 10), "ZRZUTY EKRANU & FOTO:", fill=COLOR_STATUS_OK, font=get_font(11, bold=True))
        canvas.draw.text((rx + 12, snap_y + 28), f"Zapisano w sesji: {self.snapshot_count} zdjęć", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
        canvas.draw.text((rx + 12, snap_y + 48), f"Folder: .../captures/", fill=COLOR_TEXT_MUTED, font=get_font(10, bold=False))
        canvas.draw_badge(rx + 12, snap_y + 74, "[A] ZRÓB ZDJĘCIE (SNAP)", bg_color=(30, 80, 50), text_color=COLOR_TEXT_PRIMARY)

    def handle_input(self, event: str) -> bool:
        if event == "BTN_A":
            # Take photo / snapshot
            self._save_snapshot()
            return True
        elif event == "BTN_X":
            # Cycle optical filter
            self.filter_idx = (self.filter_idx + 1) % len(FILTER_NAMES)
            return True
        elif event == "BTN_Y":
            # Cycle measurement graticule overlay
            self.graticule_idx = (self.graticule_idx + 1) % len(GRATICULE_NAMES)
            return True
        elif event == "RIGHT":
            # Zoom In
            self.zoom_idx = min(len(ZOOM_LEVELS) - 1, self.zoom_idx + 1)
            return True
        elif event == "LEFT":
            # Zoom Out
            self.zoom_idx = max(0, self.zoom_idx - 1)
            if self.zoom_idx == 0:
                self.pan_x = 0
                self.pan_y = 0
            return True
        elif event == "UP":
            # Exposure / Brightness Boost
            self.brightness_bias = min(0.6, self.brightness_bias + 0.1)
            return True
        elif event == "DOWN":
            # Exposure / Brightness Decrease
            self.brightness_bias = max(-0.5, self.brightness_bias - 0.1)
            return True
        elif event == "BTN_B":
            # Cycle video source (USB OTG -> Wi-Fi IP Cam -> Simulator)
            self.source_mode = (self.source_mode + 1) % len(self.source_names)
            return True
        return False
