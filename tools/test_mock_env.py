#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import types
import os
from PIL import Image, ImageDraw, ImageFont

# 1. Setup mock environment
def get_font(size=14, bold=False):
    return ImageFont.load_default()

class Canvas:
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (width, height), (10, 15, 24, 255))
        self.draw = ImageDraw.Draw(self.image)
    def clear(self, bg_color=(10, 15, 24, 255)):
        self.draw.rectangle([(0, 0), (self.width, self.height)], fill=bg_color)
    def draw_card(self, x, y, w, h, title="", subtitle="", border_color=(0, 200, 255), fill_color=(16, 24, 36), radius=8):
        self.draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=radius, fill=fill_color, outline=border_color, width=2)
        if title:
            self.draw.text((x + 14, y + 12), title, fill=(240, 245, 255), font=get_font(15, bold=True))
        if subtitle:
            self.draw.text((x + 14, y + 36), subtitle, fill=(130, 160, 190), font=get_font(12))
    def draw_badge(self, x, y, text, bg_color=(30, 45, 65), text_color=(240, 245, 255)):
        bw = len(text) * 8 + 14
        self.draw.rounded_rectangle([(x, y), (x + bw, y + 24)], radius=4, fill=bg_color, outline=(0, 200, 255))
        self.draw.text((x + 6, y + 4), text, fill=text_color, font=get_font(11, bold=True))

class BaseModule:
    def __init__(self, app_context=None):
        self.app_context = app_context
        self.accent_color = (0, 240, 255)
    def update(self, dt): pass
    def render(self, canvas): pass
    def handle_input(self, event): return False
    def get_hotkey_hints(self): return []

c_mod = types.ModuleType("core.canvas")
c_mod.Canvas = Canvas
c_mod.get_font = get_font

b_mod = types.ModuleType("core.module_base")
b_mod.BaseModule = BaseModule

t_mod = types.ModuleType("core.theme")
t_mod.SCREEN_WIDTH = 1024
t_mod.SCREEN_HEIGHT = 768
t_mod.HEADER_HEIGHT = 50
t_mod.FOOTER_HEIGHT = 44
t_mod.COLOR_BG_DARK = (10, 15, 24, 255)
t_mod.COLOR_PANEL_BG = (14, 20, 32, 255)
t_mod.COLOR_PANEL_ALT = (20, 30, 45, 255)
t_mod.COLOR_BORDER = (40, 60, 85, 255)
t_mod.COLOR_BORDER_LIGHT = (60, 85, 120, 255)
t_mod.COLOR_CYBER_CYAN = (0, 240, 255, 255)
t_mod.COLOR_FLIPPER_AMBER = (255, 170, 0, 255)
t_mod.COLOR_PHOSPHOR_GREEN = (0, 255, 136, 255)
t_mod.COLOR_NEON_PINK = (255, 0, 128, 255)
t_mod.COLOR_ELECTRIC_BLUE = (0, 140, 255, 255)
t_mod.COLOR_TEXT_PRIMARY = (240, 245, 255, 255)
t_mod.COLOR_TEXT_SECONDARY = (160, 180, 210, 255)
t_mod.COLOR_TEXT_MUTED = (100, 125, 155, 255)
t_mod.COLOR_STATUS_OK = (0, 255, 136, 255)
t_mod.COLOR_STATUS_WARN = (255, 170, 0, 255)
t_mod.COLOR_STATUS_ERR = (255, 60, 60, 255)

i_mod = types.ModuleType("core.i18n")
i_mod.t = lambda k, default=None: default or k

qr_mod = types.ModuleType("core.qr_engine")
qr_mod.generate_qr_matrix = lambda d: [[1 if (x+y)%2==0 else 0 for x in range(25)] for y in range(25)]
qr_mod.generate_code128 = lambda d: "10101100110"
qr_mod.generate_ean13 = lambda d: "10100011010"

surv_mod = types.ModuleType("core.survival_engine")
class MockSurvival:
    def get_categories(self): return ["Woda", "Ogień", "Schronienie", "Apteczka"]
    def get_articles_by_category(self, cat): return [{"id": "1", "title": "Uzdatnianie wody", "desc": "Gotowanie i filtry"}]
    def get_article(self, aid): return {"title": "Uzdatnianie wody", "content": "Gotuj wodę minimum 3 minuty."}
surv_mod.SurvivalEngine = MockSurvival

core_pkg = types.ModuleType("core")
core_pkg.canvas = c_mod
core_pkg.module_base = b_mod
core_pkg.theme = t_mod
core_pkg.i18n = i_mod
core_pkg.qr_engine = qr_mod
core_pkg.survival_engine = surv_mod

sys.modules["core"] = core_pkg
sys.modules["core.canvas"] = c_mod
sys.modules["core.module_base"] = b_mod
sys.modules["core.theme"] = t_mod
sys.modules["core.i18n"] = i_mod
sys.modules["core.qr_engine"] = qr_mod
sys.modules["core.survival_engine"] = surv_mod

# serial mock
serial_mock = types.ModuleType("serial")
class MockSerial:
    def __init__(self, *args, **kwargs): pass
    def write(self, data): pass
    def read(self, size=1): return b""
    def readline(self): return b"[WASM] Serial loopback ready\n"
    @property
    def in_waiting(self): return 0
    def close(self): pass
serial_mock.Serial = MockSerial
sys.modules["serial"] = serial_mock

# flipper_proto mock
flip_mock = types.ModuleType("flipper_proto")
class MockFlipper: pass
flip_mock.FlipperProto = MockFlipper
sys.modules["flipper_proto"] = flip_mock

# ssl mock if needed
if "ssl" not in sys.modules:
    ssl_mock = types.ModuleType("ssl")
    ssl_mock.CERT_NONE = 0
    ssl_mock.create_default_context = lambda: types.SimpleNamespace(check_hostname=False, verify_mode=0)
    sys.modules["ssl"] = ssl_mock

# 2. Test importing all modules from both directories
dirs = ["Apps/BrickDeck/modules", "store/modules"]
canvas = Canvas()

tested = 0
passed = 0
failed = []

for d in dirs:
    if not os.path.exists(d): continue
    for fname in sorted(os.listdir(d)):
        if fname.startswith("mod_") and fname.endswith(".py"):
            tested += 1
            path = os.path.join(d, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    code = f.read()
                mod_ns = types.ModuleType("test_mod")
                exec(code, mod_ns.__dict__)
                
                cls = None
                for attr in dir(mod_ns):
                    if attr.endswith("Module") and attr != "BaseModule":
                        cls = getattr(mod_ns, attr)
                        break
                if cls:
                    instance = cls()
                    instance.update(0.016)
                    canvas.clear()
                    instance.render(canvas)
                    passed += 1
                else:
                    failed.append((fname, "No Module class found"))
            except Exception as e:
                failed.append((fname, str(e)))

print(f"Results: {passed}/{tested} modules passed render test successfully!")
if failed:
    print("Failures:")
    for f, err in failed:
        print(f"  [-] {f}: {err}")
