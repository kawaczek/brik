#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_store.py - BrickDeck CyberStore (GitHub App Store & Package Manager)
Allows browsing, installing, updating, and removing modules directly via Wi-Fi from GitHub.
Zero external pip dependencies.
"""

import os
import json
import time
import urllib.request
import urllib.error
import threading
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw

from core.module_base import BaseModule
from core.canvas import Canvas, get_font
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)

DEFAULT_REGISTRY_URL = "https://raw.githubusercontent.com/kawaczek/brik/main/store/registry.json"
CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "store_cache.json")
MODULES_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "modules.json")
MODULES_DIR = os.path.abspath(os.path.dirname(__file__))

CORE_PROTECTED_MODULES = {"mod_clock", "mod_system", "mod_diag", "mod_store"}


class StoreModule(BaseModule):
    """Online Package Manager & GitHub App Store for BrickDeck OS."""

    def __init__(self, app_context=None):
        super().__init__(app_context)

        self.registry_url = DEFAULT_REGISTRY_URL
        self.categories = ["Wszystkie", "Gry & 3D", "Cyber & Hacking", "Narzędzia & Net", "Nauka & Kosmos", "Multimedia & Audio"]
        self.active_cat_idx = 0

        self.modules_list: List[Dict[str, Any]] = []
        self.filtered_modules: List[Dict[str, Any]] = []
        self.selected_idx = 0

        # State & Feedback
        self.status_msg = "Gotowy (Wi-Fi)"
        self.status_color = (0, 255, 180)
        self.is_loading = False
        self.is_installing = False
        self.last_sync_time = 0.0

        # Installed cache set
        self.installed_ids = set()
        self._refresh_installed_set()

        # Load initial cache / background fetch
        self._load_cached_registry()
        self.fetch_registry_async()

    def get_hotkey_hints(self) -> List[Dict[str, str]]:
        return [
            {"key": "D-Pad", "desc": "Wybór modułu"},
            {"key": "L1/R1", "desc": "Kategoria"},
            {"key": "A", "desc": "Zainstaluj / Update"},
            {"key": "X", "desc": "Odinstaluj"},
            {"key": "Y", "desc": "Odśwież z GitHub"},
        ]

    def _refresh_installed_set(self):
        """Scans filesystem and modules.json for installed modules."""
        self.installed_ids = set()
        try:
            if os.path.exists(MODULES_DIR):
                for f in os.listdir(MODULES_DIR):
                    if f.startswith("mod_") and f.endswith(".py"):
                        mod_id = f[:-3]
                        self.installed_ids.add(mod_id)
        except Exception:
            pass

    def _load_cached_registry(self):
        """Loads repository cache from disk if available."""
        if os.path.exists(CACHE_PATH):
            try:
                with open(CACHE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.modules_list = data.get("modules", [])
                    if "categories" in data:
                        self.categories = data["categories"]
                    self._apply_filter()
                    self.status_msg = "Załadowano z pamięci podręcznej"
                    return
            except Exception:
                pass

        # Fallback local registry if cache doesn't exist yet
        fallback_store_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "store", "registry.json")
        if os.path.exists(fallback_store_file):
            try:
                with open(fallback_store_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.modules_list = data.get("modules", [])
                    self._apply_filter()
                    self.status_msg = "Załadowano lokalny katalog"
            except Exception:
                pass

    def fetch_registry_async(self):
        """Fetches the latest registry JSON from GitHub in a background thread."""
        if self.is_loading:
            return
        self.is_loading = True
        self.status_msg = "Łączenie z GitHub..."
        self.status_color = (255, 200, 0)

        def _worker():
            try:
                req = urllib.request.Request(
                    self.registry_url,
                    headers={"User-Agent": "BrickDeckOS-Store/1.0"}
                )
                with urllib.request.urlopen(req, timeout=6.0) as resp:
                    raw_data = resp.read().decode("utf-8")
                    data = json.loads(raw_data)
                    self.modules_list = data.get("modules", [])
                    if "categories" in data:
                        self.categories = data["categories"]

                    # Save to cache
                    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
                    with open(CACHE_PATH, "w", encoding="utf-8") as f:
                        f.write(raw_data)

                    self.status_msg = f"Zsynchronizowano z GitHub ({len(self.modules_list)} modułów)"
                    self.status_color = (0, 255, 120)
                    self.last_sync_time = time.time()
            except Exception as e:
                self.status_msg = f"Brak sieci / Błąd GitHub: {str(e)[:24]}"
                self.status_color = (255, 80, 80)
            finally:
                self.is_loading = False
                self._refresh_installed_set()
                self._apply_filter()

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_filter(self):
        """Filters modules by selected category."""
        active_cat = self.categories[self.active_cat_idx]
        if active_cat == "Wszystkie":
            self.filtered_modules = list(self.modules_list)
        else:
            self.filtered_modules = [m for m in self.modules_list if m.get("category") == active_cat]

        if self.selected_idx >= len(self.filtered_modules):
            self.selected_idx = max(0, len(self.filtered_modules) - 1)

    def install_module_async(self, mod_info: Dict[str, Any]):
        """Downloads and registers a module from GitHub in a background thread."""
        if self.is_installing:
            return
        mod_id = mod_info.get("id")
        dl_url = mod_info.get("download_url")
        if not mod_id or not dl_url:
            self.status_msg = "Błąd: Brak URL modułu"
            self.status_color = (255, 50, 50)
            return

        self.is_installing = True
        self.status_msg = f"Pobieranie {mod_id}.py..."
        self.status_color = (255, 210, 0)

        def _worker():
            try:
                dest_file = os.path.join(MODULES_DIR, f"{mod_id}.py")
                req = urllib.request.Request(
                    dl_url,
                    headers={"User-Agent": "BrickDeckOS-Store/1.0"}
                )
                with urllib.request.urlopen(req, timeout=12.0) as resp:
                    content = resp.read()

                # Basic validation: check if valid python file
                if b"class " not in content and b"import " not in content:
                    raise ValueError("Pobrany plik nie jest modułem Pythona")

                with open(dest_file, "wb") as f:
                    f.write(content)

                # Register in modules.json
                self._register_in_modules_json(mod_id, mod_info.get("name", mod_id))

                self._refresh_installed_set()
                self.status_msg = f"Sukces! Zainstalowano {mod_id}"
                self.status_color = (0, 255, 120)
            except Exception as e:
                self.status_msg = f"Błąd instalacji: {str(e)[:30]}"
                self.status_color = (255, 80, 80)
            finally:
                self.is_installing = False

        threading.Thread(target=_worker, daemon=True).start()

    def _register_in_modules_json(self, mod_id: str, name: str):
        """Safely inserts new module into modules.json."""
        try:
            if not os.path.exists(MODULES_JSON_PATH):
                return
            with open(MODULES_JSON_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            mods = cfg.get("modules", [])
            # Check if exists
            for m in mods:
                if m.get("id") == mod_id:
                    m["enabled"] = True
                    with open(MODULES_JSON_PATH, "w", encoding="utf-8") as f:
                        json.dump(cfg, f, indent=4, ensure_ascii=False)
                    return

            # Add to end of list
            mods.append({
                "id": mod_id,
                "enabled": True,
                "name": name
            })
            cfg["modules"] = mods
            with open(MODULES_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def uninstall_module(self, mod_info: Dict[str, Any]):
        """Uninstalls a non-protected module."""
        mod_id = mod_info.get("id")
        if mod_id in CORE_PROTECTED_MODULES:
            self.status_msg = f"Moduł bazowy {mod_id} jest chroniony!"
            self.status_color = (255, 140, 0)
            return

        target_file = os.path.join(MODULES_DIR, f"{mod_id}.py")
        try:
            if os.path.exists(target_file):
                os.remove(target_file)

            # Disable or remove in modules.json
            if os.path.exists(MODULES_JSON_PATH):
                with open(MODULES_JSON_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                mods = [m for m in cfg.get("modules", []) if m.get("id") != mod_id]
                cfg["modules"] = mods
                with open(MODULES_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=4, ensure_ascii=False)

            self._refresh_installed_set()
            self.status_msg = f"Odinstalowano {mod_id}"
            self.status_color = (255, 180, 0)
        except Exception as e:
            self.status_msg = f"Błąd usuwania: {e}"
            self.status_color = (255, 50, 50)

    def update(self, dt: float):
        pass

    def render(self, canvas: Canvas):
        w, h = 1024, 768

        # 1. Main Card Wrapper
        active_cat = self.categories[self.active_cat_idx]
        canvas.draw_card(
            x=20, y=66, w=984, h=638,
            title=f"🛍️ BRICKSTORE // KATALOG GITHUB: {active_cat.upper()}",
            subtitle=f"{self.status_msg}  |  Moduły: {len(self.filtered_modules)}  |  L1/R1: Kategoria  |  [A] Instaluj  |  [X] Usuń",
            border_color=COLOR_CYBER_CYAN
        )

        draw = canvas.draw

        # 2. Category Tab Pills
        cat_y = 114
        cat_x = 36
        for i, cat in enumerate(self.categories):
            is_active = (i == self.active_cat_idx)
            text_w = len(cat) * 9 + 20
            bg = (0, 110, 150) if is_active else (20, 26, 38)
            fg = (255, 255, 255) if is_active else COLOR_TEXT_SECONDARY
            border = COLOR_CYBER_CYAN if is_active else COLOR_BORDER

            draw.rounded_rectangle([(cat_x, cat_y), (cat_x + text_w, cat_y + 28)], radius=4, fill=bg, outline=border, width=1)
            draw.text((cat_x + 10, cat_y + 5), cat, fill=fg, font=get_font(13, bold=is_active))
            cat_x += text_w + 8

        # Split: Left List (w: 520), Right Details (w: 400)
        list_x = 36
        list_w = 520
        list_y_start = 154
        item_h = 68
        visible_count = 7

        scroll_offset = 0
        if self.selected_idx >= visible_count:
            scroll_offset = self.selected_idx - visible_count + 1

        # 3. Modules List
        if not self.filtered_modules:
            draw.text((list_x + 20, list_y_start + 40), "Brak modułów w wybranej kategorii", fill=COLOR_TEXT_MUTED, font=get_font(16))
        else:
            for slot in range(visible_count):
                idx = scroll_offset + slot
                if idx >= len(self.filtered_modules):
                    break
                mod = self.filtered_modules[idx]
                mod_id = mod.get("id", "")
                is_selected = (idx == self.selected_idx)
                is_installed = (mod_id in self.installed_ids)

                y_pos = list_y_start + slot * (item_h + 6)

                # Card background
                card_bg = (26, 40, 60) if is_selected else (14, 20, 30)
                card_border = COLOR_CYBER_CYAN if is_selected else COLOR_BORDER
                draw.rounded_rectangle([list_x, y_pos, list_x + list_w, y_pos + item_h], radius=6, fill=card_bg, outline=card_border, width=2 if is_selected else 1)

                # Selection indicator bar
                if is_selected:
                    draw.rounded_rectangle([list_x, y_pos, list_x + 6, y_pos + item_h], radius=2, fill=COLOR_CYBER_CYAN)

                # Name & Version
                name_str = mod.get("name", mod_id)
                draw.text((list_x + 16, y_pos + 6), name_str, fill=COLOR_TEXT_PRIMARY if is_selected else (210, 225, 240), font=get_font(15, bold=True))

                # Category & Size
                meta_str = f"{mod.get('category', 'Moduł')} • {mod.get('size_kb', 0)} KB • v{mod.get('version', '1.0')}"
                draw.text((list_x + 16, y_pos + 27), meta_str, fill=COLOR_CYBER_CYAN, font=get_font(12))

                # Short description
                desc_short = mod.get("description", "")
                if len(desc_short) > 48:
                    desc_short = desc_short[:46] + "..."
                draw.text((list_x + 16, y_pos + 46), desc_short, fill=COLOR_TEXT_MUTED, font=get_font(12))

                # Status badge
                if is_installed:
                    canvas.draw_badge(list_x + list_w - 140, y_pos + 10, "ZAINSTALOWANY", bg_color=(0, 95, 55), text_color=(120, 255, 180))
                else:
                    canvas.draw_badge(list_x + list_w - 105, y_pos + 10, "DOSTĘPNY", bg_color=(0, 60, 110), text_color=(0, 220, 255))

        # 4. Right Details Panel
        det_x = list_x + list_w + 18
        det_w = 984 - det_x + 20
        det_y = list_y_start
        det_h = 530

        draw.rounded_rectangle([det_x, det_y, det_x + det_w, det_y + det_h], radius=6, fill=(12, 17, 26), outline=COLOR_BORDER, width=1)

        if self.filtered_modules and 0 <= self.selected_idx < len(self.filtered_modules):
            cur = self.filtered_modules[self.selected_idx]
            cur_id = cur.get("id", "")
            is_cur_installed = (cur_id in self.installed_ids)

            # Details Header
            draw.text((det_x + 18, det_y + 14), cur.get("name", cur_id), fill=COLOR_CYBER_CYAN, font=get_font(18, bold=True))
            draw.text((det_x + 18, det_y + 38), f"Plik: {cur_id}.py", fill=COLOR_TEXT_MUTED, font=get_font(13))

            draw.line([(det_x + 18, det_y + 60), (det_x + det_w - 18, det_y + 60)], fill=COLOR_BORDER, width=1)

            # Metadata Table
            meta_y = det_y + 70
            fields = [
                ("Autor", cur.get("author", "kawaczek")),
                ("Wersja", cur.get("version", "1.0.0")),
                ("Rozmiar", f"{cur.get('size_kb', 0)} KB"),
                ("Kategoria", cur.get("category", "Ogólne")),
                ("Wymagania", "Brak (Zero Dongle)" if not cur.get("dongle_required", False) else "Dongle USB"),
                ("Status", "Zainstalowany lokalnie" if is_cur_installed else "Dostępny w GitHub"),
            ]
            for label, val in fields:
                draw.text((det_x + 18, meta_y), f"{label}:", fill=COLOR_TEXT_SECONDARY, font=get_font(13))
                draw.text((det_x + 130, meta_y), str(val), fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))
                meta_y += 22

            draw.line([(det_x + 18, meta_y + 6), (det_x + det_w - 18, meta_y + 6)], fill=COLOR_BORDER, width=1)

            # Description
            desc_y = meta_y + 16
            draw.text((det_x + 18, desc_y), "OPIS MODUŁU:", fill=COLOR_CYBER_CYAN, font=get_font(13, bold=True))
            desc_text = cur.get("description", "Brak opisu.")

            words = desc_text.split(" ")
            line_buf = ""
            dy = desc_y + 22
            for word in words:
                if len(line_buf) + len(word) + 1 > 34:
                    draw.text((det_x + 18, dy), line_buf, fill=COLOR_TEXT_PRIMARY, font=get_font(13))
                    dy += 18
                    line_buf = word
                else:
                    line_buf = f"{line_buf} {word}".strip()
            if line_buf:
                draw.text((det_x + 18, dy), line_buf, fill=COLOR_TEXT_PRIMARY, font=get_font(13))
                dy += 22

            # Controls
            ctrls = cur.get("controls", "")
            if ctrls:
                draw.text((det_x + 18, dy + 8), "STEROWANIE:", fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))
                draw.text((det_x + 18, dy + 28), ctrls, fill=COLOR_TEXT_SECONDARY, font=get_font(12))

            # Action Buttons at Bottom
            btn_y = det_y + det_h - 60
            if is_cur_installed:
                # Update / Reinstall & Uninstall options
                btn_half = (det_w - 46) // 2
                draw.rounded_rectangle([det_x + 18, btn_y, det_x + 18 + btn_half, btn_y + 42], radius=6, fill=(0, 90, 130), outline=COLOR_CYBER_CYAN, width=1)
                draw.text((det_x + 28, btn_y + 12), "[A] Przeinstaluj", fill=(255, 255, 255), font=get_font(14, bold=True))

                draw.rounded_rectangle([det_x + 28 + btn_half, btn_y, det_x + det_w - 18, btn_y + 42], radius=6, fill=(110, 25, 25), outline=COLOR_NEON_PINK, width=1)
                draw.text((det_x + 38 + btn_half, btn_y + 12), "[X] Odinstaluj", fill=(255, 255, 255), font=get_font(14, bold=True))
            else:
                draw.rounded_rectangle([det_x + 18, btn_y, det_x + det_w - 18, btn_y + 42], radius=6, fill=(0, 120, 60), outline=COLOR_PHOSPHOR_GREEN, width=2)
                draw.text((det_x + 40, btn_y + 12), "⚡ [A] ZAINSTALUJ Z GITHUBA", fill=(255, 255, 255), font=get_font(15, bold=True))

    def handle_input(self, event: str) -> bool:
        if event in ("KEY_UP", "KEY_W"):
            if self.filtered_modules:
                self.selected_idx = (self.selected_idx - 1) % len(self.filtered_modules)
            return True
        elif event in ("KEY_DOWN", "KEY_S"):
            if self.filtered_modules:
                self.selected_idx = (self.selected_idx + 1) % len(self.filtered_modules)
            return True
        elif event in ("KEY_LEFT", "KEY_L1"):
            self.active_cat_idx = (self.active_cat_idx - 1) % len(self.categories)
            self._apply_filter()
            return True
        elif event in ("KEY_RIGHT", "KEY_R1"):
            self.active_cat_idx = (self.active_cat_idx + 1) % len(self.categories)
            self._apply_filter()
            return True
        elif event == "KEY_A":
            if self.filtered_modules and 0 <= self.selected_idx < len(self.filtered_modules):
                target = self.filtered_modules[self.selected_idx]
                self.install_module_async(target)
            return True
        elif event == "KEY_X":
            if self.filtered_modules and 0 <= self.selected_idx < len(self.filtered_modules):
                target = self.filtered_modules[self.selected_idx]
                self.uninstall_module(target)
            return True
        elif event == "KEY_Y":
            self.fetch_registry_async()
            return True
        return False
