#!/usr/bin/env python3
"""
BrickDeck OS - Modular Cyberdeck GUI Framework for TrimUI Brick
Renders a tactical multi-tool dashboard on 1024x768 display with D-Pad & gamepad navigation.
"""

import os
import sys
import time
import argparse
import glob
import json
import importlib
import inspect
from typing import List, Optional

from core.theme import SCREEN_WIDTH, SCREEN_HEIGHT
from core.canvas import Canvas
from core.display_driver import DisplayDriver
from core.input_manager import (
    InputManager, EVENT_L1, EVENT_R1, EVENT_MENU, EVENT_QUIT
)
from core.module_base import BaseModule


class FallbackEmptyModule(BaseModule):
    """Fallback module displayed when no user modules are enabled."""
    name = "BrickDeck OS"
    short_name = "Pusty"

    def render(self, canvas):
        canvas.draw_text("BRAK AKTYWNYCH MODULOW", 512, 350, font_size=24, color=(255, 100, 100), anchor="mm")
        canvas.draw_text("Sprawdz plik modules.json i wlacz conajmniej jeden modul.", 512, 390, font_size=16, color=(160, 160, 160), anchor="mm")


class BrickDeckApp:
    """Main BrickDeck Application Coordinator."""

    def __init__(self, mode: str = "auto", config_path: Optional[str] = None):
        self.mode = mode
        self.running = True
        self.canvas = Canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.display = DisplayDriver(mode=mode)
        self.input_mgr = InputManager(enable_terminal=(mode == "term" or mode == "auto"))

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = config_path or os.path.join(base_dir, "modules.json")

        # Dynamically load modules from configuration
        self.modules = self._load_modules()
        if not self.modules:
            print("[!] Brak aktywnych modulow. Ladowanie modulu awaryjnego.")
            self.modules = [FallbackEmptyModule(self)]

        self.active_module_idx = 0
        self.clock_module_idx = 0
        for i, mod in enumerate(self.modules):
            if "clock" in mod.__class__.__name__.lower() or "clock" in getattr(mod, "short_name", "").lower():
                self.clock_module_idx = i
                break

        self.saved_module_idx = 0
        self.is_in_screensaver = False
        self.last_user_input_time = time.time()
        self.screensaver_timeout_sec = 60.0

        # Load screensaver timeout from transit_config if available
        transit_cfg = os.path.join(base_dir, "transit_config.json")
        if os.path.exists(transit_cfg):
            try:
                with open(transit_cfg, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.screensaver_timeout_sec = float(cfg.get("screensaver_timeout_sec", 60.0))
            except Exception:
                pass

        self.sys_info = {
            "battery": 88,
            "wifi": True,
            "bluetooth": True
        }

    def _instantiate_module(self, mod_id: str) -> Optional[BaseModule]:
        """Dynamically import and instantiate module class by ID."""
        try:
            mod_pkg = importlib.import_module(f"modules.{mod_id}")
            for attr_name in dir(mod_pkg):
                attr = getattr(mod_pkg, attr_name)
                if (inspect.isclass(attr) and
                        issubclass(attr, BaseModule) and
                        attr is not BaseModule and
                        attr.__module__ == mod_pkg.__name__):
                    return attr(self)
            print(f"[!] Brak podklasy BaseModule w pliku {mod_id}.py")
        except Exception as e:
            print(f"[!] Blad importu modulu {mod_id}: {e}")
        return None

    def _load_modules(self) -> List[BaseModule]:
        """Dynamically load modules based on modules.json configuration and auto-discovery."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        modules_dir = os.path.join(base_dir, "modules")
        config_path = self.config_path

        loaded_modules: List[BaseModule] = []
        configured_ids = set()
        auto_discover = True

        # 1. Read modules.json if available
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg_data = json.load(f)
                    auto_discover = cfg_data.get("auto_discover", True)
                    entries = cfg_data.get("modules", [])
                    for entry in entries:
                        mod_id = entry.get("id")
                        configured_ids.add(mod_id)
                        if not entry.get("enabled", True):
                            continue
                        mod_instance = self._instantiate_module(mod_id)
                        if mod_instance:
                            loaded_modules.append(mod_instance)
            except Exception as e:
                print(f"[!] Blad odczytu {config_path}: {e}")

        # 2. Auto-discovery of new modules not present in modules.json
        if auto_discover and os.path.exists(modules_dir):
            discovered_files = sorted(glob.glob(os.path.join(modules_dir, "mod_*.py")))
            new_entries = []
            for filepath in discovered_files:
                filename = os.path.basename(filepath)
                mod_id = os.path.splitext(filename)[0]
                if mod_id not in configured_ids:
                    mod_instance = self._instantiate_module(mod_id)
                    if mod_instance:
                        loaded_modules.append(mod_instance)
                        configured_ids.add(mod_id)
                        new_entries.append({
                            "id": mod_id,
                            "enabled": True,
                            "name": getattr(mod_instance, "name", mod_id)
                        })
            # If new modules were discovered, update modules.json
            if new_entries and os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        cfg_data = json.load(f)
                    cfg_data.setdefault("modules", []).extend(new_entries)
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(cfg_data, f, indent=4, ensure_ascii=False)
                    print(f"[*] Wykryto i zarejestrowano {len(new_entries)} nowych modulow w {os.path.basename(config_path)}")
                except Exception as e:
                    print(f"[!] Nie udalo sie zaktualizowac {config_path}: {e}")

        return loaded_modules

    def run(self):
        """Main framework execution loop."""
        print("==================================================")
        print("        ⚡ BRICKDECK MODULAR GUI FRAMEWORK        ")
        print("==================================================")

        # 1. Initialize Display Output
        active_mode = self.display.initialize()
        print(f"[*] Aktywny sterownik wyswietlania: {active_mode.upper()}")

        # 2. Initialize Modules
        for mod in self.modules:
            mod.on_load()
        self.modules[self.active_module_idx].on_activate()

        # 3. Start Input Listener
        self.input_mgr.start()
        print(f"[*] Zaladowano {len(self.modules)} modulow systemowych.")
        print("[*] Sterowanie: [L1/R1 lub Q/E] Zmiana modulu | [Strzalki/WSAD] Ruch | [Spacja] A | [Esc/M] Wyjscie\n")

        last_time = time.time()
        fps_target = 30.0 if active_mode == "term" else 60.0
        frame_delay = 1.0 / fps_target

        try:
            while self.running:
                now = time.time()
                dt = now - last_time
                last_time = now

                # A. Handle Inputs
                while True:
                    ev = self.input_mgr.poll_event()
                    if not ev:
                        break

                    # Reset idle timer on any input
                    self.last_user_input_time = now

                    # If screensaver was active, any key wakes up to previous module
                    if self.is_in_screensaver:
                        self.is_in_screensaver = False
                        self._switch_to_module(self.saved_module_idx)
                        print(f"[Screensaver] Wybudzono system do modulu: {self.modules[self.saved_module_idx].name}")
                        continue

                    if ev in (EVENT_MENU, EVENT_QUIT):
                        self.running = False
                        break
                    elif ev == EVENT_L1:
                        self._switch_module(-1)
                    elif ev == EVENT_R1:
                        self._switch_module(1)
                    else:
                        # Delegate event to active module
                        active_mod = self.modules[self.active_module_idx]
                        active_mod.handle_input(ev)

                if not self.running:
                    break

                # Check Idle Screensaver Activation
                if not self.is_in_screensaver and self.screensaver_timeout_sec > 0:
                    if (now - self.last_user_input_time) >= self.screensaver_timeout_sec:
                        if self.active_module_idx != self.clock_module_idx:
                            self.saved_module_idx = self.active_module_idx
                            self.is_in_screensaver = True
                            self._switch_to_module(self.clock_module_idx)
                            print("[Screensaver] Bezczynnosc -> Uruchomiono wygaszacz z zegarem i odjazdami MZK!")

                # B. Update Module Logic
                active_mod = self.modules[self.active_module_idx]
                active_mod.update(dt)

                # C. Render UI
                self.canvas.clear()
                # 1. Top Header Bar
                self.canvas.draw_header(self.active_module_idx, self.modules, self.sys_info)
                # 2. Active Module Workspace
                active_mod.render(self.canvas)
                # 3. Bottom Hotkeys Footer
                self.canvas.draw_footer(active_mod.get_hotkey_hints())
                # 4. Present Frame to Hardware / Terminal
                self.display.render(self.canvas)

                # D. Frame Rate Sleep
                elapsed = time.time() - now
                sleep_time = max(0.001, frame_delay - elapsed)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def _switch_module(self, delta: int):
        """Switch active module by delta (-1 for prev, +1 for next)."""
        new_idx = (self.active_module_idx + delta) % len(self.modules)
        self._switch_to_module(new_idx)

    def _switch_to_module(self, target_idx: int):
        """Switch directly to module by index."""
        if target_idx == self.active_module_idx:
            return
        old_idx = self.active_module_idx
        self.modules[old_idx].on_deactivate()

        self.active_module_idx = target_idx % len(self.modules)
        new_mod = self.modules[self.active_module_idx]
        new_mod.on_activate()
        print(f"[BrickDeck] Przelaczono na modul: {new_mod.name}")

    def shutdown(self):
        """Clean shutdown of all framework components."""
        print("\n[*] Zamykanie BrickDeck OS...")
        self.running = False
        self.input_mgr.stop()
        for mod in self.modules:
            try:
                mod.on_deactivate()
            except Exception:
                pass
        self.display.close()
        print("[*] Zamknieto pomyslnie. Do widzenia!")


def main():
    parser = argparse.ArgumentParser(description="BrickDeck OS - TrimUI Brick GUI Framework")
    parser.add_argument("--mode", choices=["auto", "fb", "term", "pygame"], default="auto",
                        help="Sterownik obrazu (auto, fb, term, pygame)")
    args = parser.parse_args()

    app = BrickDeckApp(mode=args.mode)
    app.run()


if __name__ == "__main__":
    main()
