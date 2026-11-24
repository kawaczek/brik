#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/generate_screenshots.py - Headless Screenshot Generator for BrickDeck OS
Renders 1024x768 PNG screenshots for every module in Apps/BrickDeck/modules and store/modules.
"""

import os
import sys
import importlib
import importlib.util
import traceback
from PIL import Image

sys.path.insert(0, os.path.abspath("Apps/BrickDeck"))
from core.canvas import Canvas

OUTPUT_DIR = os.path.abspath("docs/screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODULE_DIRS = [
    ("Apps/BrickDeck/modules", "modules"),
    ("store/modules", "store.modules")
]

def generate_all():
    generated = 0
    errors = 0

    for dir_path, pkg_prefix in MODULE_DIRS:
        if not os.path.exists(dir_path):
            continue

        for fname in sorted(os.listdir(dir_path)):
            if not fname.startswith("mod_") or not fname.endswith(".py"):
                continue

            mod_id = fname[:-3]
            out_file = os.path.join(OUTPUT_DIR, f"{mod_id}.png")

            try:
                # Import module dynamically
                if pkg_prefix == "modules":
                    mod_obj = importlib.import_module(f"modules.{mod_id}")
                else:
                    spec = importlib.util.spec_from_file_location(mod_id, os.path.join(dir_path, fname))
                    mod_obj = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod_obj)

                # Find module class
                cls = None
                for attr_name in dir(mod_obj):
                    attr = getattr(mod_obj, attr_name)
                    if isinstance(attr, type) and attr_name.endswith("Module") and attr_name != "BaseModule":
                        cls = attr
                        break

                if not cls:
                    print(f"[-] No Module class found in {fname}")
                    continue

                instance = cls()
                canvas = Canvas(1024, 768)

                # Warm-up tick
                instance.update(0.016)

                # Render to canvas
                instance.render(canvas)

                # Save screenshot
                canvas.image.save(out_file, "PNG", optimize=True)
                print(f"[+] Rendered: {mod_id}.png ({os.path.getsize(out_file) // 1024} KB)")
                generated += 1

            except Exception as e:
                print(f"[!] Error rendering {mod_id}: {e}")
                errors += 1

    print(f"\nDone! Successfully generated {generated} screenshots. Errors: {errors}")

if __name__ == "__main__":
    generate_all()
