#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/generate_screenshots.py - Headless Screenshot Generator for BrickDeck OS
Renders 1024x768 PNG screenshots for every module in store/registry.json.
"""

import os
import sys
import json
import importlib.util
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "Apps", "BrickDeck"))
from core.canvas import Canvas

REGISTRY_PATH = os.path.join(REPO_ROOT, "store", "registry.json")
STORE_DIR = os.path.join(REPO_ROOT, "store", "modules")
OUTPUT_DIR = os.path.join(REPO_ROOT, "docs", "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_all():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    modules = data.get("modules", [])
    print(f"[*] Starting screenshot generation for {len(modules)} modules...")

    generated = 0
    errors = 0

    for m in modules:
        canon_id = m["id"]
        legacy_id = m.get("legacy_id", canon_id)
        py_path = os.path.join(STORE_DIR, f"{canon_id}.py")
        out_canon = os.path.join(OUTPUT_DIR, f"{canon_id}.png")
        out_legacy = os.path.join(OUTPUT_DIR, f"{legacy_id}.png")

        if not os.path.exists(py_path):
            print(f"[-] Missing python file: {py_path}")
            errors += 1
            continue

        try:
            spec = importlib.util.spec_from_file_location(canon_id, py_path)
            mod_obj = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod_obj)

            cls = None
            for attr_name in dir(mod_obj):
                attr = getattr(mod_obj, attr_name)
                if isinstance(attr, type) and attr_name.endswith("Module") and attr_name != "BaseModule":
                    cls = attr
                    break

            if not cls:
                print(f"[-] No Module class found in {canon_id}")
                errors += 1
                continue

            instance = cls()
            canvas = Canvas(1024, 768)

            # Warm-up tick
            instance.update(0.016)

            # Render
            instance.render(canvas)

            # Save canonical screenshot
            canvas.image.save(out_canon, "PNG", optimize=True)

            # Create or update legacy symlink / copy
            if out_legacy != out_canon:
                if os.path.lexists(out_legacy):
                    os.remove(out_legacy)
                os.symlink(f"{canon_id}.png", out_legacy)

            sz_kb = os.path.getsize(out_canon) // 1024
            print(f"[+] Rendered [{m['num']}/86]: {canon_id}.png ({sz_kb} KB)")
            generated += 1

        except Exception as e:
            print(f"[!] Error rendering {canon_id}: {e}")
            errors += 1

    print(f"\nDone! Successfully generated {generated} screenshots. Errors: {errors}")

if __name__ == "__main__":
    generate_all()
