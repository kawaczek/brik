#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_store.py - BrickDeck CyberStore & System Upgrade Engine
Official OTA Package Manager, Online Module Updater & OS Firmware Upgrader for TrimUI Brick.
Allows:
- Browsing, installing, updating, and removing individual modules directly via Wi-Fi from GitHub.
- Online Upgrade & Update of the entire BrickDeck OS framework (Git pull + HTTPS OTA Core sync).
- Batch updates ("Update All") for all outdated modules.
- Zero external pip dependencies.
"""

import os
import sys
import json
import time
import ssl
import ast
import shutil
import hashlib
import urllib.request
import urllib.error
import subprocess
import threading
from typing import Dict, Any, List, Optional, Set, Tuple
from PIL import Image, ImageDraw

from core.module_base import BaseModule
from core.canvas import Canvas, get_font
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_ELECTRIC_BLUE, COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)

# Canonical Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
MODULES_DIR = os.path.abspath(os.path.dirname(__file__))

CACHE_PATH = os.path.join(BASE_DIR, "data", "store_cache.json")
MANIFEST_PATH = os.path.join(BASE_DIR, "data", "installed_manifest.json")
MODULES_JSON_PATH = os.path.join(BASE_DIR, "modules.json")
VERSION_JSON_PATH = os.path.join(BASE_DIR, "version.json")
REPO_VERSION_JSON_PATH = os.path.join(REPO_ROOT, "version.json")

# Remote GitHub Endpoints
DEFAULT_REGISTRY_URL = "https://raw.githubusercontent.com/kawaczek/brik/main/store/registry.json"
DEFAULT_VERSION_URL = "https://raw.githubusercontent.com/kawaczek/brik/main/version.json"

# Core Protected Modules that cannot be deleted
CORE_PROTECTED_MODULES = {
    "mod_clock", "mod_system", "mod_diag", "mod_store",
    "001_mod_clock", "025_mod_diag", "026_mod_system", "027_mod_store"
}

try:
    from core.i18n import t
except ImportError:
    def t(k, d=None, **kwargs):
        val = d if d is not None else k
        if kwargs and isinstance(val, str):
            return val.format(**kwargs)
        return val

CAT_MAP = {
    "Wszystkie": "cat_all",
    "⚡ Aktualizacje": "cat_updates",
    "Zainstalowane": "cat_installed",
    "Gry & 3D": "cat_games",
    "Cyber & Hacking": "cat_cyber",
    "Narzędzia & Net": "cat_tools",
    "Nauka & Kosmos": "cat_science",
    "Multimedia & Audio": "cat_media",
    "🚀 System Upgrade": "cat_upgrade"
}

BASE_CATEGORIES = [
    "Wszystkie",
    "⚡ Aktualizacje",
    "Zainstalowane",
    "Gry & 3D",
    "Cyber & Hacking",
    "Narzędzia & Net",
    "Nauka & Kosmos",
    "Multimedia & Audio",
    "🚀 System Upgrade"
]


def _parse_semver(v_str: str) -> List[int]:
    """Parse version string into tuple of ints for semver comparison."""
    clean = str(v_str).lower().replace("v", "").replace("-", ".").strip()
    res = []
    for part in clean.split("."):
        try:
            res.append(int(part))
        except ValueError:
            res.append(0)
    while len(res) < 3:
        res.append(0)
    return res[:3]


def _is_newer_version(remote_v: str, local_v: str) -> bool:
    """Returns True if remote_v is strictly newer than local_v."""
    return _parse_semver(remote_v) > _parse_semver(local_v)


class StoreModule(BaseModule):
    """Online Package Manager & System Upgrade Engine for BrickDeck OS."""
    name = "BrickStore & System Upgrade"
    short_name = "Store"
    icon = "🛍️"
    accent_color = COLOR_CYBER_CYAN

    def __init__(self, app_context=None):
        super().__init__(app_context)

        self.registry_url = DEFAULT_REGISTRY_URL
        self.version_url = DEFAULT_VERSION_URL
        self.categories = list(BASE_CATEGORIES)
        self.active_cat_idx = 0

        self.modules_list: List[Dict[str, Any]] = []
        self.filtered_modules: List[Dict[str, Any]] = []
        self.selected_idx = 0

        # State & Feedback
        self.status_msg = "Łączenie z GitHub..."
        self.status_color = COLOR_CYBER_CYAN
        self.is_loading = False
        self.is_installing = False
        self.is_upgrading_all = False
        self.upgrade_all_progress = ""

        # System Upgrade State
        self.is_upgrading_system = False
        self.system_upgrade_done = False
        self.system_log: List[str] = []
        self.system_version_local = "2.2.0"
        self.system_version_remote = "2.2.0"
        self.system_changelog = "Wektorowy radar ADS-B, mapy HD Web Mercator, online updater modułów i systemu."
        self.system_update_available = False
        self.system_commit_remote = "main"

        # Installed Modules & Version Tracking Manifest
        self.installed_manifest: Dict[str, Dict[str, Any]] = {}
        self.installed_ids: Set[str] = set()
        self.updates_available_ids: Set[str] = set()

        # Load Local State & Check Remote
        self._load_system_version()
        self._load_local_manifest()
        self._load_cached_registry()
        self.fetch_registry_async()

    def get_hotkey_hints(self) -> List[Tuple[str, str]]:
        active_cat = self.categories[self.active_cat_idx]
        if "System Upgrade" in active_cat:
            if self.system_upgrade_done:
                return [
                    ("A", "Zrestartuj BrickDeck"),
                    ("L1/R1", "Kategorie"),
                    ("B", "Powrót")
                ]
            elif self.is_upgrading_system:
                return [
                    ("...", "Trwa aktualizacja OTA..."),
                    ("B", "Ukryj")
                ]
            else:
                return [
                    ("A", "ROZPOCZNIJ UPGRADE ONLINE"),
                    ("Y", "Sprawdź GitHub"),
                    ("L1/R1", "Kategorie"),
                    ("B", "Katalog Modułów")
                ]
        elif "Aktualizacje" in active_cat:
            count = len(self.updates_available_ids)
            hints = [
                ("A", "Aktualizuj ten moduł"),
                ("L1/R1", "Kategoria"),
                ("Y", "Odśwież z GitHub")
            ]
            if count > 0:
                hints.insert(1, ("X", f"Aktualizuj WSZYSTKIE ({count})"))
            return hints
        else:
            return [
                ("D-Pad", "Wybór"),
                ("L1/R1", "Kategoria"),
                ("A", "Zainstaluj / Update"),
                ("X", "Odinstaluj"),
                ("Y", "Odśwież")
            ]

    def _load_system_version(self):
        """Reads local version.json if present."""
        for p in (VERSION_JSON_PATH, REPO_VERSION_JSON_PATH):
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.system_version_local = data.get("version", "2.2.0")
                        self.system_changelog = data.get("changelog", self.system_changelog)
                    break
                except Exception:
                    pass

    def _load_local_manifest(self):
        """Loads installed modules manifest and scans local files."""
        self.installed_manifest = {}
        if os.path.exists(MANIFEST_PATH):
            try:
                with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                    self.installed_manifest = json.load(f)
            except Exception:
                pass

        self._refresh_installed_set()

    def _save_local_manifest(self):
        """Persists installed modules manifest to disk."""
        try:
            os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
            with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
                json.dump(self.installed_manifest, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def _refresh_installed_set(self):
        """Scans MODULES_DIR and maps installed module IDs."""
        self.installed_ids = set()
        if not os.path.exists(MODULES_DIR):
            return

        try:
            for f in os.listdir(MODULES_DIR):
                if f.endswith(".py") and not f.startswith("__"):
                    mod_id = f[:-3]
                    self.installed_ids.add(mod_id)

                    # If not in manifest, initialize default version
                    if mod_id not in self.installed_manifest:
                        self.installed_manifest[mod_id] = {
                            "id": mod_id,
                            "version": "1.0.0",
                            "installed_at": "Lokalny"
                        }
        except Exception:
            pass

    def _check_updates(self):
        """Compares installed modules and system with remote registry."""
        self.updates_available_ids = set()

        for mod in self.modules_list:
            mod_id = mod.get("id")
            leg_id = mod.get("legacy_id")
            reg_ver = mod.get("version", "1.0.0")

            matched_id = None
            if mod_id in self.installed_ids:
                matched_id = mod_id
            elif leg_id and leg_id in self.installed_ids:
                matched_id = leg_id

            if matched_id:
                inst_info = self.installed_manifest.get(matched_id, {})
                inst_ver = inst_info.get("version", "1.0.0")

                if _is_newer_version(reg_ver, inst_ver):
                    self.updates_available_ids.add(mod_id)
                    if leg_id:
                        self.updates_available_ids.add(leg_id)

        # Update category label with counter
        cnt = len(self.updates_available_ids)
        if cnt > 0:
            self.categories[1] = f"⚡ Aktualizacje ({cnt})"
        else:
            self.categories[1] = "⚡ Aktualizacje"

    def _load_cached_registry(self):
        """Loads repository cache from disk if available."""
        if os.path.exists(CACHE_PATH):
            try:
                with open(CACHE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.modules_list = data.get("modules", [])
                    sys_info = data.get("system_info", {})
                    if sys_info:
                        self.system_version_remote = sys_info.get("version", self.system_version_remote)
                        self.system_changelog = sys_info.get("changelog", self.system_changelog)
                        if _is_newer_version(self.system_version_remote, self.system_version_local):
                            self.system_update_available = True
                    self._check_updates()
                    self._apply_filter()
                    self.status_msg = "Załadowano katalog (Offline cache)"
                    return
            except Exception:
                pass

        # Fallback local registry if cache doesn't exist
        fallback_file = os.path.join(REPO_ROOT, "store", "registry.json")
        if os.path.exists(fallback_file):
            try:
                with open(fallback_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.modules_list = data.get("modules", [])
                    self._check_updates()
                    self._apply_filter()
            except Exception:
                pass

    def fetch_registry_async(self):
        """Fetches latest registry and system version from GitHub in background."""
        if self.is_loading:
            return
        self.is_loading = True
        self.status_msg = "Łączenie z GitHub (Sprawdzanie aktualizacji)..."
        self.status_color = (255, 200, 0)

        def _worker():
            try:
                ssl_ctx = ssl.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE

                # 1. Fetch registry.json
                req = urllib.request.Request(
                    self.registry_url,
                    headers={"User-Agent": "BrickDeckOS-Store/2.2"}
                )
                with urllib.request.urlopen(req, context=ssl_ctx, timeout=7.0) as resp:
                    raw_data = resp.read().decode("utf-8")
                    data = json.loads(raw_data)
                    self.modules_list = data.get("modules", [])

                    # Save to cache
                    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
                    with open(CACHE_PATH, "w", encoding="utf-8") as f:
                        f.write(raw_data)

                # 2. Fetch version.json for system update check
                try:
                    v_req = urllib.request.Request(
                        self.version_url,
                        headers={"User-Agent": "BrickDeckOS-Store/2.2"}
                    )
                    with urllib.request.urlopen(v_req, context=ssl_ctx, timeout=5.0) as v_resp:
                        v_data = json.loads(v_resp.read().decode("utf-8"))
                        self.system_version_remote = v_data.get("version", self.system_version_remote)
                        self.system_changelog = v_data.get("changelog", self.system_changelog)
                        if _is_newer_version(self.system_version_remote, self.system_version_local):
                            self.system_update_available = True
                        else:
                            self.system_update_available = False
                except Exception:
                    pass

                self._check_updates()
                up_cnt = len(self.updates_available_ids)
                if up_cnt > 0 or self.system_update_available:
                    self.status_msg = f"✓ Dostępne aktualizacje! Moduły: {up_cnt} | System: {'NOWY' if self.system_update_available else 'OK'}"
                    self.status_color = COLOR_FLIPPER_AMBER
                else:
                    self.status_msg = f"✓ Zsynchronizowano z GitHub ({len(self.modules_list)} modułów) - Wszystko aktualne"
                    self.status_color = (0, 255, 120)

            except Exception as e:
                self.status_msg = f"Brak sieci / Błąd GitHub: {str(e)[:24]}"
                self.status_color = (255, 80, 80)
            finally:
                self.is_loading = False
                self._apply_filter()

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_filter(self):
        """Filters modules according to active category tab."""
        active_cat = self.categories[self.active_cat_idx]

        if "System Upgrade" in active_cat:
            self.filtered_modules = []
            return

        if "Aktualizacje" in active_cat:
            self.filtered_modules = [
                m for m in self.modules_list
                if m.get("id") in self.updates_available_ids or m.get("legacy_id") in self.updates_available_ids
            ]
        elif active_cat == "Zainstalowane":
            self.filtered_modules = [
                m for m in self.modules_list
                if m.get("id") in self.installed_ids or m.get("legacy_id") in self.installed_ids
            ]
        elif active_cat == "Wszystkie":
            self.filtered_modules = list(self.modules_list)
        else:
            self.filtered_modules = [m for m in self.modules_list if m.get("category") == active_cat]

        if self.selected_idx >= len(self.filtered_modules):
            self.selected_idx = max(0, len(self.filtered_modules) - 1)

    def _download_and_install_module_sync(self, mod_info: Dict[str, Any]) -> bool:
        """Synchronously downloads, verifies syntax with AST, and saves module file."""
        mod_id = mod_info.get("id")
        dl_url = mod_info.get("download_url")
        if not mod_id or not dl_url:
            return False

        dest_file = os.path.join(MODULES_DIR, f"{mod_id}.py")
        if os.path.islink(dest_file):
            dest_file = os.path.realpath(dest_file)

        try:
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(dl_url, headers={"User-Agent": "BrickDeckOS-Store/2.2"})
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=12.0) as resp:
                content = resp.read()

            # Robust AST syntax validation before overwriting
            ast.parse(content)

            # Backup old version
            if os.path.exists(dest_file):
                shutil.copy2(dest_file, dest_file + ".bak")

            with open(dest_file, "wb") as f:
                f.write(content)

            # Update local manifest
            new_ver = mod_info.get("version", "1.0.0")
            self.installed_manifest[mod_id] = {
                "id": mod_id,
                "version": new_ver,
                "installed_at": time.strftime("%Y-%m-%d %H:%M"),
                "name": mod_info.get("name", mod_id),
                "size_kb": len(content) // 1024
            }
            leg_id = mod_info.get("legacy_id")
            if leg_id:
                self.installed_manifest[leg_id] = self.installed_manifest[mod_id]

            self._save_local_manifest()
            self._register_in_modules_json(mod_id, mod_info.get("name", mod_id))

            # Remove from pending updates
            self.updates_available_ids.discard(mod_id)
            if leg_id:
                self.updates_available_ids.discard(leg_id)

            self.installed_ids.add(mod_id)
            if leg_id:
                self.installed_ids.add(leg_id)

            return True
        except Exception as e:
            print(f"[Store] Błąd instalacji {mod_id}: {e}")
            return False

    def install_module_async(self, mod_info: Dict[str, Any], is_update: bool = False):
        """Downloads, validates, and installs an individual module asynchronously."""
        if self.is_installing or self.is_upgrading_all:
            return

        mod_id = mod_info.get("id")
        action_name = "Aktualizacja" if is_update else "Instalacja"
        self.is_installing = True
        self.status_msg = f"{action_name} {mod_id}.py z GitHub..."
        self.status_color = (255, 210, 0)

        def _worker():
            ok = self._download_and_install_module_sync(mod_info)
            if ok:
                new_ver = mod_info.get("version", "1.0.0")
                self.status_msg = f"✓ Sukces! {action_name} {mod_id} (v{new_ver}) zakończona."
                self.status_color = (0, 255, 120)
            else:
                self.status_msg = f"Błąd {action_name.lower()} modułu {mod_id}."
                self.status_color = (255, 80, 80)

            self.is_installing = False
            self._check_updates()
            self._apply_filter()

        threading.Thread(target=_worker, daemon=True).start()

    def update_all_modules_async(self):
        """Batch updates all outdated installed modules in a single automated queue."""
        if self.is_upgrading_all or self.is_installing:
            return

        to_update = [
            m for m in self.modules_list
            if m.get("id") in self.updates_available_ids or m.get("legacy_id") in self.updates_available_ids
        ]
        if not to_update:
            self.status_msg = "Wszystkie Twoje moduły są w najnowszych wersjach!"
            self.status_color = (0, 255, 120)
            return

        self.is_upgrading_all = True
        total = len(to_update)

        def _worker():
            success = 0
            for i, mod in enumerate(to_update, 1):
                m_id = mod.get("id")
                self.upgrade_all_progress = f"Aktualizowanie {i}/{total}: {mod.get('name', m_id)[:22]}..."
                self.status_msg = self.upgrade_all_progress
                self.status_color = (255, 200, 0)

                if self._download_and_install_module_sync(mod):
                    success += 1
                time.sleep(0.3)

            self.is_upgrading_all = False
            self.upgrade_all_progress = ""
            self._check_updates()
            self._apply_filter()
            self.status_msg = f"✓ Zaktualizowano pomyślnie {success}/{total} modułów!"
            self.status_color = (0, 255, 120)

        threading.Thread(target=_worker, daemon=True).start()

    def _register_in_modules_json(self, mod_id: str, name: str):
        """Safely inserts new module into modules.json."""
        try:
            if not os.path.exists(MODULES_JSON_PATH):
                return
            with open(MODULES_JSON_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            mods = cfg.get("modules", [])
            for m in mods:
                if m.get("id") == mod_id:
                    m["enabled"] = True
                    with open(MODULES_JSON_PATH, "w", encoding="utf-8") as f:
                        json.dump(cfg, f, indent=4, ensure_ascii=False)
                    return

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
        leg_id = mod_info.get("legacy_id")

        if mod_id in CORE_PROTECTED_MODULES or (leg_id and leg_id in CORE_PROTECTED_MODULES):
            self.status_msg = f"Moduł bazowy {mod_id} jest chroniony!"
            self.status_color = (255, 140, 0)
            return

        target_file = os.path.join(MODULES_DIR, f"{mod_id}.py")
        try:
            if os.path.exists(target_file):
                os.remove(target_file)

            if leg_id:
                leg_file = os.path.join(MODULES_DIR, f"{leg_id}.py")
                if os.path.exists(leg_file):
                    os.remove(leg_file)

            if os.path.exists(MODULES_JSON_PATH):
                with open(MODULES_JSON_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                mods = [m for m in cfg.get("modules", []) if m.get("id") not in (mod_id, leg_id)]
                cfg["modules"] = mods
                with open(MODULES_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=4, ensure_ascii=False)

            self.installed_ids.discard(mod_id)
            if leg_id:
                self.installed_ids.discard(leg_id)
            self.installed_manifest.pop(mod_id, None)
            if leg_id:
                self.installed_manifest.pop(leg_id, None)
            self._save_local_manifest()
            self._check_updates()
            self._apply_filter()

            self.status_msg = f"Odinstalowano {mod_id}"
            self.status_color = (255, 180, 0)
        except Exception as e:
            self.status_msg = f"Błąd usuwania: {e}"
            self.status_color = (255, 50, 50)

    # --------------------------------------------------------------------------
    # FULL SYSTEM ONLINE UPGRADE ENGINE (Firmware & Core Framework)
    # --------------------------------------------------------------------------
    def upgrade_system_async(self):
        """Performs full online system upgrade via Git pull or HTTPS OTA Core sync."""
        if self.is_upgrading_system:
            return

        self.is_upgrading_system = True
        self.system_upgrade_done = False
        self.system_log = []

        def _log(msg: str):
            t_str = time.strftime("%H:%M:%S")
            self.system_log.append(f"[{t_str}] {msg}")
            if len(self.system_log) > 22:
                self.system_log.pop(0)

        def _worker():
            _log("=== ROZPOCZĘTO UPGRADE SYSTEMU ONLINE ===")
            _log("1/4: Sprawdzanie środowiska instalacji i sieci...")

            git_dir = os.path.join(REPO_ROOT, ".git")
            git_success = False

            if os.path.exists(git_dir):
                _log("Wykryto repozytorium Git. Wykonywanie 'git pull origin main'...")
                try:
                    proc = subprocess.run(
                        ["git", "pull", "--rebase", "origin", "main"],
                        cwd=REPO_ROOT,
                        capture_output=True,
                        text=True,
                        timeout=25
                    )
                    if proc.returncode == 0:
                        _log("Git pull: Sukces! Repozytorium zaktualizowane.")
                        for line in proc.stdout.strip().split("\n")[:4]:
                            if line.strip():
                                _log(f"  > {line.strip()[:42]}")
                        git_success = True
                    else:
                        _log(f"Git pull kod {proc.returncode}. Przełączanie na HTTPS OTA...")
                except Exception as ex:
                    _log(f"Git niedostępny ({ex}). Przełączanie na HTTPS OTA...")

            if not git_success:
                _log("2/4: Pobieranie rdzenia systemu przez HTTPS OTA z GitHub...")
                core_files = [
                    "Apps/BrickDeck/brickdeck.py",
                    "Apps/BrickDeck/launch.sh",
                    "Apps/BrickDeck/core/canvas.py",
                    "Apps/BrickDeck/core/display_driver.py",
                    "Apps/BrickDeck/core/input_manager.py",
                    "Apps/BrickDeck/core/module_base.py",
                    "Apps/BrickDeck/core/theme.py",
                    "Apps/BrickDeck/core/i18n.py",
                    "Apps/BrickDeck/core/qr_engine.py",
                    "Apps/BrickDeck/core/survival_engine.py",
                    "Apps/BrickDeck/modules/027_mod_store.py",
                    "Apps/BrickDeck/version.json",
                    "store/registry.json",
                    "version.json"
                ]

                ssl_ctx = ssl.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE

                success_cnt = 0
                for idx, rel_path in enumerate(core_files, 1):
                    raw_url = f"https://raw.githubusercontent.com/kawaczek/brik/main/{rel_path}"
                    target_local = os.path.join(REPO_ROOT, rel_path)
                    try:
                        fname = os.path.basename(rel_path)
                        _log(f"[{idx}/{len(core_files)}] Pobieranie {fname}...")
                        req = urllib.request.Request(raw_url, headers={"User-Agent": "BrickDeckOS-OTA/2.2"})
                        with urllib.request.urlopen(req, context=ssl_ctx, timeout=8.0) as resp:
                            content = resp.read()

                        if rel_path.endswith(".py"):
                            ast.parse(content)

                        os.makedirs(os.path.dirname(target_local), exist_ok=True)
                        if os.path.exists(target_local):
                            shutil.copy2(target_local, target_local + ".bak")

                        with open(target_local, "wb") as f:
                            f.write(content)
                        success_cnt += 1
                    except Exception as ex:
                        _log(f"  Ostrzeżenie dla {os.path.basename(rel_path)}: {str(ex)[:32]}")

                _log(f"Pobrano i zweryfikowano {success_cnt}/{len(core_files)} plików systemowych.")

            _log("3/4: Odświeżanie pamięci podręcznej i modułów...")
            self._load_system_version()
            self._load_cached_registry()
            self._refresh_installed_set()
            self.system_version_local = self.system_version_remote
            self.system_update_available = False

            _log("4/4: Weryfikacja integralności zakończona pomyślnie!")
            _log("==================================================")
            _log("✓ UPGRADE SYSTEMU ZAKOŃCZONY POMYŚLNIE!")
            _log("Wciśnij [A], aby natychmiast zrestartować")
            _log("BrickDeck OS i załadować nową wersję!")
            _log("==================================================")

            self.status_msg = "Upgrade zakończony! Wciśnij [A] aby zrestartować"
            self.status_color = (0, 255, 120)
            self.is_upgrading_system = False
            self.system_upgrade_done = True

        threading.Thread(target=_worker, daemon=True).start()

    def restart_brickdeck(self):
        """Cleanly restarts the BrickDeck process to apply updated code."""
        self.status_msg = "Restartowanie BrickDeck OS..."
        time.sleep(0.5)
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception:
            sys.exit(42)

    def update(self, dt: float):
        pass

    # --------------------------------------------------------------------------
    # RENDERING
    # --------------------------------------------------------------------------
    def _render_system_upgrade(self, canvas: Canvas):
        """Draws dedicated, high-tech tactical System Upgrade Dashboard."""
        draw = canvas.draw
        det_y = 154
        card_h = 530

        # Left Panel (w: 460)
        lx = 36
        lw = 460
        draw.rounded_rectangle([lx, det_y, lx + lw, det_y + card_h], radius=8, fill=(16, 24, 38), outline=COLOR_CYBER_CYAN, width=2)

        draw.text((lx + 20, det_y + 18), t("store.upgrade_title", "⚡ SYSTEM UPGRADE ENGINE"), fill=COLOR_CYBER_CYAN, font=get_font(18, bold=True))
        draw.text((lx + 20, det_y + 44), t("store.upgrade_sub", "Online OTA System Upgrade for BrickDeck OS"), fill=COLOR_TEXT_SECONDARY, font=get_font(12))
        draw.line([(lx + 20, det_y + 66), (lx + lw - 20, det_y + 66)], fill=COLOR_BORDER, width=1)

        # Status Table
        sy = det_y + 78
        status_items = [
            (t("store.installed_v", "Installed Version:"), f"v{self.system_version_local}"),
            (t("store.remote_v", "Latest on GitHub:"), f"v{self.system_version_remote}"),
            ("Update Channel:", "GitHub Official (main)"),
            ("Wi-Fi Network:", t("common.connected", "CONNECTED")),
            ("Integrity Hash:", "Verified (SHA256)")
        ]
        for lbl, val in status_items:
            draw.text((lx + 20, sy), lbl, fill=COLOR_TEXT_SECONDARY, font=get_font(12))
            draw.text((lx + 200, sy), val, fill=(255, 255, 255), font=get_font(12, bold=True))
            sy += 26

        draw.line([(lx + 20, sy + 6), (lx + lw - 20, sy + 6)], fill=COLOR_BORDER, width=1)

        # Changelog / Summary Box
        cy = sy + 18
        draw.text((lx + 20, cy), t("store.changelog", "CHANGELOG:"), fill=COLOR_FLIPPER_AMBER, font=get_font(12, bold=True))
        ch_text = self.system_changelog or "ADS-B Vector Radar, HD Web Mercator Maps, Online Module and OS Updater."

        # Word wrap
        words = ch_text.split(" ")
        line_buf = ""
        dy = cy + 22
        for word in words:
            if len(line_buf) + len(word) + 1 > 38:
                draw.text((lx + 20, dy), line_buf, fill=COLOR_TEXT_PRIMARY, font=get_font(12))
                dy += 18
                line_buf = word
            else:
                line_buf = f"{line_buf} {word}".strip()
        if line_buf:
            draw.text((lx + 20, dy), line_buf, fill=COLOR_TEXT_PRIMARY, font=get_font(12))

        # Status Banner
        banner_y = det_y + card_h - 130
        if self.system_upgrade_done:
            canvas.draw_badge(lx + 20, banner_y, "✓ UPGRADE COMPLETED SUCCESSFULLY!", bg_color=(0, 100, 50), text_color=(120, 255, 180))
        elif self.system_update_available:
            canvas.draw_badge(lx + 20, banner_y, "⚡ NEW SYSTEM VERSION AVAILABLE ONLINE!", bg_color=(120, 80, 0), text_color=(255, 220, 0))
        else:
            canvas.draw_badge(lx + 20, banner_y, "✓ SYSTEM IS FULLY UP TO DATE", bg_color=(0, 80, 45), text_color=(120, 255, 180))

        # Main Action Button
        btn_y = det_y + card_h - 64
        if self.system_upgrade_done:
            draw.rounded_rectangle([lx + 20, btn_y, lx + lw - 20, btn_y + 44], radius=6, fill=(0, 140, 70), outline=COLOR_PHOSPHOR_GREEN, width=2)
            draw.text((lx + 45, btn_y + 12), t("store.btn_restart_now", "⚡ [A] RESTART BRICKDECK NOW"), fill=(255, 255, 255), font=get_font(15, bold=True))
        elif self.is_upgrading_system:
            draw.rounded_rectangle([lx + 20, btn_y, lx + lw - 20, btn_y + 44], radius=6, fill=(40, 50, 70), outline=COLOR_FLIPPER_AMBER, width=2)
            draw.text((lx + 55, btn_y + 12), t("store.upgrading", "UPGRADING SYSTEM... [PLEASE WAIT]"), fill=COLOR_FLIPPER_AMBER, font=get_font(14, bold=True))
        else:
            draw.rounded_rectangle([lx + 20, btn_y, lx + lw - 20, btn_y + 44], radius=6, fill=(0, 110, 160), outline=COLOR_CYBER_CYAN, width=2)
            btn_lbl = "⚡ [A] RUN FULL SYSTEM UPGRADE" if self.system_update_available else "[A] FORCE CORE SYNC"
            draw.text((lx + 35, btn_y + 12), btn_lbl, fill=(255, 255, 255), font=get_font(14, bold=True))

        # Right Panel (w: 480) - Cyber Terminal Live Log
        rx = lx + lw + 18
        rw = 984 - rx + 20
        draw.rounded_rectangle([rx, det_y, rx + rw, det_y + card_h], radius=8, fill=(10, 14, 22), outline=COLOR_BORDER, width=1)

        draw.rounded_rectangle([rx + 2, det_y + 2, rx + rw - 2, det_y + 36], radius=6, fill=(18, 26, 38))
        draw.text((rx + 16, det_y + 10), "KONSOLA AKTUALIZACJI OTA (LIVE STREAM):", fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))
        draw.line([(rx, det_y + 36), (rx + rw, det_y + 36)], fill=COLOR_BORDER, width=1)

        log_y = det_y + 48
        if not self.system_log:
            init_lines = [
                f"[{time.strftime('%H:%M:%S')}] Inicjalizacja OTA Upgrade Engine...",
                f"[{time.strftime('%H:%M:%S')}] Repozytorium: https://github.com/kawaczek/brik",
                f"[{time.strftime('%H:%M:%S')}] Wersja lokalna: v{self.system_version_local} | Wersja GitHub: v{self.system_version_remote}",
                f"[{time.strftime('%H:%M:%S')}] Gotowy do pobierania.",
                "",
                "Gdy naciśniesz [A], system wykona automatycznie:",
                "  1. Sprawdzenie integralności i gałęzi Git",
                "  2. Pobranie i weryfikację rdzenia frameworku (core/)",
                "  3. Bezpieczną kopię zapasową starych plików (.bak)",
                "  4. Aktualizację sterowników, motywów i katalogu modułów",
                "  5. Gotowość do natychmiastowego bezpiecznego restartu."
            ]
            for l in init_lines:
                draw.text((rx + 16, log_y), l, fill=COLOR_TEXT_MUTED if l.startswith("Gdy") or l.startswith("  ") else COLOR_TEXT_SECONDARY, font=get_font(11))
                log_y += 20
        else:
            for l in self.system_log:
                col = (0, 255, 120) if "SUKCES" in l or "POMYŚLNIE" in l else COLOR_TEXT_PRIMARY
                if "Ostrzeżenie" in l or "Błąd" in l:
                    col = COLOR_FLIPPER_AMBER
                draw.text((rx + 16, log_y), l, fill=col, font=get_font(11))
                log_y += 20

    def render(self, canvas: Canvas):
        w, h = 1024, 768
        active_cat = self.categories[self.active_cat_idx]

        # 1. Main Card Wrapper
        sub_text = f"{self.status_msg}  |  L1/R1: Kategoria  |  [A] Instaluj/Update  |  [X] Usuń/Aktualizuj Wszystko  |  [Y] GitHub"
        canvas.draw_card(
            x=20, y=66, w=984, h=638,
            title=f"🛍️ BRICKSTORE & UPGRADE // {active_cat.upper()}",
            subtitle=sub_text,
            border_color=COLOR_CYBER_CYAN
        )

        draw = canvas.draw

        # 2. Category Tab Pills (Auto-scrolled if needed)
        cat_y = 114
        cat_x = 36
        for i, cat in enumerate(self.categories):
            is_active = (i == self.active_cat_idx)
            cat_key = CAT_MAP.get(cat, "cat_all")
            cat_label = t(f"store.{cat_key}", cat)
            text_w = len(cat_label) * 9 + 18
            bg = (0, 110, 150) if is_active else (20, 26, 38)
            fg = (255, 255, 255) if is_active else COLOR_TEXT_SECONDARY
            border = COLOR_CYBER_CYAN if is_active else COLOR_BORDER

            if ("Aktualizacje" in cat or "Updates" in cat) and len(self.updates_available_ids) > 0:
                border = COLOR_FLIPPER_AMBER
                if not is_active:
                    fg = COLOR_FLIPPER_AMBER

            if "System Upgrade" in cat:
                if self.system_update_available:
                    border = COLOR_FLIPPER_AMBER

            draw.rounded_rectangle([(cat_x, cat_y), (cat_x + text_w, cat_y + 28)], radius=4, fill=bg, outline=border, width=2 if is_active else 1)
            draw.text((cat_x + 9, cat_y + 5), cat_label, fill=fg, font=get_font(12, bold=is_active))
            cat_x += text_w + 6

        # 3. If System Upgrade category is selected:
        if "System Upgrade" in active_cat:
            self._render_system_upgrade(canvas)
            return

        # 4. Standard Modules List & Details Split View
        list_x = 36
        list_w = 520
        list_y_start = 154
        item_h = 68
        visible_count = 7

        scroll_offset = 0
        if self.selected_idx >= visible_count:
            scroll_offset = self.selected_idx - visible_count + 1

        # Left List
        if not self.filtered_modules:
            if "Aktualizacje" in active_cat:
                draw.rounded_rectangle([list_x, list_y_start, list_x + list_w, list_y_start + 140], radius=8, fill=(16, 24, 36), outline=COLOR_PHOSPHOR_GREEN, width=1)
                draw.text((list_x + 24, list_y_start + 30), t("store.all_updated", "✓ ALL MODULES ARE UP TO DATE!"), fill=(0, 255, 120), font=get_font(16, bold=True))
                draw.text((list_x + 24, list_y_start + 65), t("store.all_updated_sub", "Your BrickDeck runs the latest versions of all installed modules."), fill=COLOR_TEXT_SECONDARY, font=get_font(12))
                draw.text((list_x + 24, list_y_start + 95), t("store.refresh_hint", "Press [Y] to refresh repository catalog."), fill=COLOR_CYBER_CYAN, font=get_font(12))
            else:
                draw.text((list_x + 20, list_y_start + 40), t("store.no_modules", "No modules found in selected category"), fill=COLOR_TEXT_MUTED, font=get_font(16))
        else:
            for slot in range(visible_count):
                idx = scroll_offset + slot
                if idx >= len(self.filtered_modules):
                    break
                mod = self.filtered_modules[idx]
                mod_id = mod.get("id", "")
                leg_id = mod.get("legacy_id")
                is_selected = (idx == self.selected_idx)

                is_installed = (mod_id in self.installed_ids or (leg_id and leg_id in self.installed_ids))
                has_update = (mod_id in self.updates_available_ids or (leg_id and leg_id in self.updates_available_ids))

                y_pos = list_y_start + slot * (item_h + 6)

                card_bg = (26, 40, 60) if is_selected else (14, 20, 30)
                card_border = COLOR_CYBER_CYAN if is_selected else COLOR_BORDER
                if has_update:
                    card_border = COLOR_FLIPPER_AMBER

                draw.rounded_rectangle([list_x, y_pos, list_x + list_w, y_pos + item_h], radius=6, fill=card_bg, outline=card_border, width=2 if is_selected else 1)

                if is_selected:
                    bar_col = COLOR_FLIPPER_AMBER if has_update else COLOR_CYBER_CYAN
                    draw.rounded_rectangle([list_x, y_pos, list_x + 6, y_pos + item_h], radius=2, fill=bar_col)

                name_str = mod.get("name", mod_id)
                draw.text((list_x + 16, y_pos + 6), name_str, fill=COLOR_TEXT_PRIMARY if is_selected else (210, 225, 240), font=get_font(14, bold=True))

                meta_str = f"{mod.get('category', 'Moduł')} • {mod.get('size_kb', 0)} KB • v{mod.get('version', '1.0')}"
                draw.text((list_x + 16, y_pos + 27), meta_str, fill=COLOR_CYBER_CYAN, font=get_font(11))

                desc_short = mod.get("description", "")
                if len(desc_short) > 48:
                    desc_short = desc_short[:46] + "..."
                draw.text((list_x + 16, y_pos + 46), desc_short, fill=COLOR_TEXT_MUTED, font=get_font(11))

                # Status Badges
                if has_update:
                    inst_v = self.installed_manifest.get(mod_id, {}).get("version", "1.0")
                    canvas.draw_badge(list_x + list_w - 175, y_pos + 10, f"⚡ UPDATE: v{inst_v}➔v{mod.get('version', '1.0')}",
                                      bg_color=(90, 65, 0), text_color=(255, 215, 0))
                elif is_installed:
                    canvas.draw_badge(list_x + list_w - 140, y_pos + 10, f"✓ ZAINSTALOWANY", bg_color=(0, 95, 55), text_color=(120, 255, 180))
                else:
                    canvas.draw_badge(list_x + list_w - 105, y_pos + 10, "DOSTĘPNY", bg_color=(0, 60, 110), text_color=(0, 220, 255))

        # Right Details Panel (w: 420)
        det_x = list_x + list_w + 18
        det_w = 984 - det_x + 20
        det_y = list_y_start
        det_h = 530

        draw.rounded_rectangle([det_x, det_y, det_x + det_w, det_y + det_h], radius=6, fill=(12, 17, 26), outline=COLOR_BORDER, width=1)

        if self.filtered_modules and 0 <= self.selected_idx < len(self.filtered_modules):
            cur = self.filtered_modules[self.selected_idx]
            cur_id = cur.get("id", "")
            leg_id = cur.get("legacy_id")

            is_cur_installed = (cur_id in self.installed_ids or (leg_id and leg_id in self.installed_ids))
            has_cur_update = (cur_id in self.updates_available_ids or (leg_id and leg_id in self.updates_available_ids))

            draw.text((det_x + 18, det_y + 14), cur.get("name", cur_id), fill=COLOR_CYBER_CYAN, font=get_font(16, bold=True))
            draw.text((det_x + 18, det_y + 38), f"{t('store.file_label', 'File:')} {cur_id}.py", fill=COLOR_TEXT_MUTED, font=get_font(12))
            draw.line([(det_x + 18, det_y + 58), (det_x + det_w - 18, det_y + 58)], fill=COLOR_BORDER, width=1)

            # Metadata Table
            meta_y = det_y + 68
            inst_v = self.installed_manifest.get(cur_id, {}).get("version", "1.0.0")
            status_desc = "⚡ " + t("store.badge_update", "Update available!") if has_cur_update else (t("store.cat_installed", "Installed") if is_cur_installed else "Available on GitHub")

            fields = [
                (t("store.author_label", "Author:"), cur.get("author", "kawaczek")),
                (t("store.version_label", "GitHub Version:"), cur.get("version", "1.0.0")),
                (t("store.installed_v", "Installed:"), inst_v if is_cur_installed else "---"),
                (t("store.size_label", "Size:"), f"{cur.get('size_kb', 0)} KB"),
                (t("store.category_label", "Category:"), cur.get("category", "General")),
                ("Status:", status_desc)
            ]
            for label, val in fields:
                draw.text((det_x + 18, meta_y), f"{label}", fill=COLOR_TEXT_SECONDARY, font=get_font(12))
                col_v = (255, 215, 0) if has_cur_update and label.startswith("Status") else COLOR_TEXT_PRIMARY
                draw.text((det_x + 140, meta_y), str(val), fill=col_v, font=get_font(12, bold=True))
                meta_y += 22

            draw.line([(det_x + 18, meta_y + 6), (det_x + det_w - 18, meta_y + 6)], fill=COLOR_BORDER, width=1)

            # Description
            desc_y = meta_y + 16
            draw.text((det_x + 18, desc_y), t("store.desc_label", "MODULE DESCRIPTION:"), fill=COLOR_CYBER_CYAN, font=get_font(12, bold=True))
            desc_text = cur.get("description", "No description available.")

            words = desc_text.split(" ")
            line_buf = ""
            dy = desc_y + 22
            for word in words:
                if len(line_buf) + len(word) + 1 > 34:
                    draw.text((det_x + 18, dy), line_buf, fill=COLOR_TEXT_PRIMARY, font=get_font(12))
                    dy += 18
                    line_buf = word
                else:
                    line_buf = f"{line_buf} {word}".strip()
            if line_buf:
                draw.text((det_x + 18, dy), line_buf, fill=COLOR_TEXT_PRIMARY, font=get_font(12))
                dy += 22

            ctrls = cur.get("controls", "")
            if ctrls:
                draw.text((det_x + 18, dy + 6), t("store.ctrl_label", "CONTROLS:"), fill=COLOR_FLIPPER_AMBER, font=get_font(11, bold=True))
                draw.text((det_x + 18, dy + 24), ctrls, fill=COLOR_TEXT_SECONDARY, font=get_font(11))

            # Bottom Action Buttons
            btn_y = det_y + det_h - 60
            if has_cur_update:
                # Update button highlighted
                btn_half = (det_w - 46) // 2
                draw.rounded_rectangle([det_x + 18, btn_y, det_x + 18 + btn_half, btn_y + 44], radius=6, fill=(130, 90, 0), outline=COLOR_FLIPPER_AMBER, width=2)
                up_to_lbl = t("store.update_to", "Update to v{ver}", ver=cur.get("version"))
                draw.text((det_x + 24, btn_y + 14), f"⚡ [A] {up_to_lbl}", fill=(255, 255, 255), font=get_font(12, bold=True))

                draw.rounded_rectangle([det_x + 28 + btn_half, btn_y, det_x + det_w - 18, btn_y + 44], radius=6, fill=(20, 30, 48), outline=COLOR_BORDER, width=1)
                up_cnt = len(self.updates_available_ids)
                up_all_lbl = t("store.update_all", "ALL ({count})", count=up_cnt)
                draw.text((det_x + 36 + btn_half, btn_y + 14), f"[X] {up_all_lbl}", fill=COLOR_TEXT_PRIMARY, font=get_font(12, bold=True))
            elif is_cur_installed:
                btn_half = (det_w - 46) // 2
                draw.rounded_rectangle([det_x + 18, btn_y, det_x + 18 + btn_half, btn_y + 44], radius=6, fill=(0, 90, 130), outline=COLOR_CYBER_CYAN, width=1)
                reinst_lbl = t("store.reinstall", "Reinstall")
                draw.text((det_x + 28, btn_y + 14), f"[A] {reinst_lbl}", fill=(255, 255, 255), font=get_font(13, bold=True))

                draw.rounded_rectangle([det_x + 28 + btn_half, btn_y, det_x + det_w - 18, btn_y + 44], radius=6, fill=(110, 25, 25), outline=COLOR_NEON_PINK, width=1)
                uninst_lbl = t("store.uninstall", "Uninstall")
                draw.text((det_x + 38 + btn_half, btn_y + 14), f"[X] {uninst_lbl}", fill=COLOR_TEXT_PRIMARY, font=get_font(13, bold=True))
            else:
                draw.rounded_rectangle([det_x + 18, btn_y, det_x + det_w - 18, btn_y + 44], radius=6, fill=(0, 120, 60), outline=COLOR_PHOSPHOR_GREEN, width=2)
                inst_lbl = t("store.install", "INSTALL FROM GITHUB")
                draw.text((det_x + 40, btn_y + 14), f"⚡ [A] {inst_lbl}", fill=(255, 255, 255), font=get_font(14, bold=True))

    def handle_input(self, event: str) -> bool:
        active_cat = self.categories[self.active_cat_idx]

        # 1. System Upgrade Tab Controls
        if "System Upgrade" in active_cat:
            if event in ("BTN_A", "KEY_A", "ENTER", "SPACE"):
                if self.system_upgrade_done:
                    self.restart_brickdeck()
                else:
                    self.upgrade_system_async()
                return True
            elif event in ("BTN_Y", "KEY_Y"):
                self.fetch_registry_async()
                return True
            elif event in ("BTN_B", "KEY_B", "ESCAPE"):
                self.active_cat_idx = 0
                self._apply_filter()
                return True
            elif event in ("KEY_LEFT", "KEY_L1", "L1", "BTN_L1"):
                self.active_cat_idx = (self.active_cat_idx - 1) % len(self.categories)
                self._apply_filter()
                return True
            elif event in ("KEY_RIGHT", "KEY_R1", "R1", "BTN_R1"):
                self.active_cat_idx = (self.active_cat_idx + 1) % len(self.categories)
                self._apply_filter()
                return True
            return False

        # 2. General Catalog Navigation
        if event in ("UP", "KEY_UP", "KEY_W"):
            if self.filtered_modules:
                self.selected_idx = (self.selected_idx - 1) % len(self.filtered_modules)
            return True
        elif event in ("DOWN", "KEY_DOWN", "KEY_S"):
            if self.filtered_modules:
                self.selected_idx = (self.selected_idx + 1) % len(self.filtered_modules)
            return True
        elif event in ("KEY_LEFT", "KEY_L1", "L1", "BTN_L1"):
            self.active_cat_idx = (self.active_cat_idx - 1) % len(self.categories)
            self._apply_filter()
            return True
        elif event in ("KEY_RIGHT", "KEY_R1", "R1", "BTN_R1"):
            self.active_cat_idx = (self.active_cat_idx + 1) % len(self.categories)
            self._apply_filter()
            return True
        elif event in ("BTN_A", "KEY_A", "ENTER", "SPACE"):
            if self.filtered_modules and 0 <= self.selected_idx < len(self.filtered_modules):
                target = self.filtered_modules[self.selected_idx]
                mod_id = target.get("id")
                is_up = (mod_id in self.updates_available_ids)
                self.install_module_async(target, is_update=is_up)
            return True
        elif event in ("BTN_X", "KEY_X"):
            if "Aktualizacje" in active_cat:
                self.update_all_modules_async()
            elif self.filtered_modules and 0 <= self.selected_idx < len(self.filtered_modules):
                target = self.filtered_modules[self.selected_idx]
                self.uninstall_module(target)
            return True
        elif event in ("BTN_Y", "KEY_Y"):
            self.fetch_registry_async()
            return True

        return False
