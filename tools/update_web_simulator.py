#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/update_web_simulator.py - Integrates all 39 modules into TrimUI Brick Web Simulator
AND adds the optional Python WASM (Pyodide) runner for executing raw .py files!
"""

import os

INDEX_PATH = "index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the CSS to include .wasm-toggle-btn
if ".wasm-toggle-btn" not in content:
    css_insert = """
    /* Python WASM Toggle Button */
    .wasm-toggle-btn {
      background: rgba(20, 30, 45, 0.85);
      border: 1px solid var(--accent-amber);
      color: var(--accent-amber);
      padding: 5px 12px;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-size: 11px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .wasm-toggle-btn:hover {
      background: var(--accent-amber);
      color: #0b0f19;
      box-shadow: 0 0 10px rgba(255, 170, 0, 0.4);
    }
    .wasm-toggle-btn.active {
      background: var(--accent-green);
      border-color: var(--accent-green);
      color: #0b0f19;
      font-weight: 700;
      box-shadow: 0 0 12px rgba(0, 255, 136, 0.5);
    }
    """
    content = content.replace("/* Container */", css_insert + "\n    /* Container */")

# 2. Update the header bar inside .screen-header-bar
old_header_pattern = """            <div class="screen-header-bar">
              <span>⚡ BRICKDECK OS // IPS DISPLAY</span>
              <div>
                <label>MODUŁ: </label>
                <select id="demoSelect" class="demo-selector">"""

new_header_pattern = """            <div class="screen-header-bar">
              <span>⚡ BRICKDECK OS // IPS DISPLAY</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <label>MODUŁ: </label>
                <select id="demoSelect" class="demo-selector">
                </select>
                <button id="btnToggleWasm" class="wasm-toggle-btn" title="Opcjonalny tryb Pyodide WebAssembly (odpala surowy kod Pythona w przeglądarce)">
                  🐍 Tryb Python WASM (Opcja)
                </button>
              </div>
            </div>"""

if 'id="btnToggleWasm"' not in content:
    # replace until </select>
    start_pos = content.find('<div class="screen-header-bar">')
    end_pos = content.find('</select>', start_pos) + len('</select>')
    # also include enclosing </div> if needed
    after_select = content.find('</div>', end_pos) + len('</div>')
    old_block = content[start_pos:after_select]
    content = content[:start_pos] + new_header_pattern + content[after_select:]

# 3. Update the script section
parts = content.split("  <script>")
html_prefix = parts[0]

new_script = """  <script>
    // ========================================================
    // BRICKDECK OS // UNIVERSAL TRIMUI BRICK SIMULATOR (ALL 39 APPS)
    // + OPTIONAL PYTHON WEBASSEMBLY (PYODIDE) ENGINE
    // ========================================================

    const canvas = document.getElementById('brickCanvas');
    const ctx = canvas.getContext('2d');
    const demoSelect = document.getElementById('demoSelect');
    const btnToggleWasm = document.getElementById('btnToggleWasm');

    // Input state
    const inputState = {
      up: false, down: false, left: false, right: false,
      a: false, b: false, x: false, y: false, l1: false, r1: false,
      menu: false, select: false
    };

    let lastButtonPressed = null;
    let buttonToastTimer = 0;

    function triggerButtonToast(name) {
      lastButtonPressed = name;
      buttonToastTimer = 45; // frames
    }

    // List of all 39 modules in system
    let allModules = [
      { id: "mod_raycaster", name: "3D Cyber-Maze Raycaster", category: "Gry & 3D", interactive: true },
      { id: "mod_artillery", name: "Cyber Artillery (Tank Wars)", category: "Gry & 3D", interactive: true },
      { id: "mod_asteroids", name: "Vector Space Combat 360°", category: "Gry & 3D", interactive: true },
      { id: "mod_sandbox", name: "Powder & Physics Sandbox", category: "Gry & 3D", interactive: true },
      { id: "mod_tamagotchi", name: "CyberPet Pocket Virtual Monster", category: "Gry & 3D", interactive: true },
      { id: "mod_lunar_lander", name: "Apollo Cyber Lander", category: "Gry & 3D", interactive: false },
      { id: "mod_lockpick", name: "Safe Cracker & Lockpicking", category: "Cyber & Hacking", interactive: false },
      { id: "mod_pipe_hack", name: "Circuit Conduit Hacker", category: "Gry & 3D", interactive: false },
      { id: "mod_life", name: "Conway's Game of Life", category: "Nauka & Kosmos", interactive: true },
      { id: "mod_synth", name: "8-Bit Cyber Synth & Tracker", category: "Audio & Radio", interactive: true },
      { id: "mod_mandelbrot", name: "Mandelbrot & Julia Fractals", category: "Nauka & Kosmos", interactive: true },
      { id: "mod_auth", name: "Tactical 2FA TOTP Vault", category: "Cyber & Hacking", interactive: true },
      { id: "mod_dice", name: "RPG Companion & Entropy Dice", category: "Narzędzia & Net", interactive: true },
      { id: "mod_clock", name: "Desk Clock & MZK Gorzów", category: "Narzędzia & Net", interactive: true },
      { id: "mod_mzk_map", name: "Gorzów Live Transit Fleet Radar", category: "Narzędzia & Net", interactive: false },
      { id: "mod_rain", name: "Storm & Rain Radar IMGW", category: "Nauka & Kosmos", interactive: false },
      { id: "mod_air_radar", name: "Global Aerospace & Satellites", category: "Nauka & Kosmos", interactive: false },
      { id: "mod_marine", name: "Global Marine Traffic & AIS Radar", category: "Narzędzia & Net", interactive: false },
      { id: "mod_blitz", name: "Blitzortung Global Lightning Radar", category: "Nauka & Kosmos", interactive: false },
      { id: "mod_sky", name: "Planetarium & ISS Passes", category: "Nauka & Kosmos", interactive: false },
      { id: "mod_space", name: "NOAA Space Weather & Aurora Oval", category: "Nauka & Kosmos", interactive: false },
      { id: "mod_crypto", name: "Tactical Cipher & Enigma Lab", category: "Cyber & Hacking", interactive: false },
      { id: "mod_seismo", name: "Global Seismology & Drum Seismograph", category: "Nauka & Kosmos", interactive: false },
      { id: "mod_survival", name: "Tactical Survival Platform", category: "Narzędzia & Net", interactive: false },
      { id: "mod_flipper", name: "Flipper Zero Companion", category: "Cyber & Hacking", interactive: false },
      { id: "mod_pwngotchi", name: "Pwngotchi Pocket Companion", category: "Cyber & Hacking", interactive: false },
      { id: "mod_radio", name: "Cyber Radio & Audio Spectrum", category: "Multimedia & Audio", interactive: false },
      { id: "mod_netscan", name: "LAN Discovery & Port Recon", category: "Cyber & Hacking", interactive: false },
      { id: "mod_radar", name: "Tactical BLE 360 Radar", category: "Cyber & Hacking", interactive: false },
      { id: "mod_wifi", name: "Wi-Fi Spectrum Analyzer", category: "Cyber & Hacking", interactive: false },
      { id: "mod_pinouts", name: "Hardware Pinouts Cheat-Sheet", category: "Narzędzia & Net", interactive: false },
      { id: "mod_calc", name: "CIDR & Hacker Utils", category: "Narzędzia & Net", interactive: false },
      { id: "mod_qr", name: "Barcode & QR Code Generator", category: "Narzędzia & Net", interactive: false },
      { id: "mod_hass", name: "Home Assistant Controller", category: "Narzędzia & Net", interactive: false },
      { id: "mod_uart", name: "UART Serial Monitor", category: "Narzędzia & Net", interactive: false },
      { id: "mod_camera", name: "CamScope Borescope & Camera", category: "Narzędzia & Net", interactive: false },
      { id: "mod_diag", name: "Hardware Diagnostic Lab", category: "Narzędzia & Net", interactive: false },
      { id: "mod_system", name: "System Telemetry & i18n", category: "Narzędzia & Net", interactive: false },
      { id: "mod_store", name: "BrickStore GitHub App Store", category: "Narzędzia & Net", interactive: false }
    ];

    let currentModuleIdx = 0;
    let currentDemo = 'mod_raycaster';
    let isLauncherOpen = false;
    let launcherCursor = 0;

    // Screenshot cache
    const screenshotCache = {};
    allModules.forEach(m => {
      const img = new Image();
      img.src = `docs/screenshots/${m.id}.png`;
      screenshotCache[m.id] = img;
    });

    // Populate Selector with ALL 39 modules
    function populateDropdown() {
      demoSelect.innerHTML = '';
      const categories = [...new Set(allModules.map(m => m.category))];
      categories.forEach(cat => {
        const group = document.createElement('optgroup');
        group.label = cat;
        allModules.filter(m => m.category === cat).forEach(m => {
          const opt = document.createElement('option');
          opt.value = m.id;
          opt.textContent = `${m.interactive ? '🎮 ' : '📱 '}${m.name}`;
          group.appendChild(opt);
        });
        demoSelect.appendChild(group);
      });
      demoSelect.value = currentDemo;
    }
    populateDropdown();

    // ========================================================
    // OPTIONAL PYTHON WEBASSEMBLY (PYODIDE) ENGINE
    // ========================================================
    let wasmActive = false;
    let wasmLoaded = false;
    let wasmLoading = false;
    let wasmStatus = "";
    let pyodideInstance = null;
    let wasmOffscreenCanvas = document.createElement('canvas');
    wasmOffscreenCanvas.width = 1024;
    wasmOffscreenCanvas.height = 768;
    let wasmOffCtx = wasmOffscreenCanvas.getContext('2d');

    async function initPyodideWasm() {
      if (wasmLoaded || wasmLoading) return;
      wasmLoading = true;
      wasmStatus = "Pobieranie silnika Pyodide WASM...";

      try {
        if (!window.loadPyodide) {
          await new Promise((resolve, reject) => {
            const s = document.createElement('script');
            s.src = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js";
            s.onload = resolve;
            s.onerror = reject;
            document.head.appendChild(s);
          });
        }

        wasmStatus = "Inicjalizacja maszyny wirtualnej CPython...";
        pyodideInstance = await loadPyodide();

        wasmStatus = "Ładowanie biblioteki graficznej Pillow (PIL)...";
        await pyodideInstance.loadPackage("pillow");

        wasmStatus = "Wstrzykiwanie środowiska BrickDeck Core...";
        pyodideInstance.runPython(`
import sys, types
from PIL import Image, ImageDraw, ImageFont

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
    def draw_card(self, x, y, w, h, title="", subtitle="", border_color=(0, 200, 255), fill_color=(16, 24, 36)):
        self.draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=8, fill=fill_color, outline=border_color, width=2)
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
    def update(self, dt): pass
    def render(self, canvas): pass
    def handle_input(self, event): return False
    def get_hotkey_hints(self): return []

c_mod = types.ModuleType("core.canvas")
c_mod.Canvas = Canvas
c_mod.get_font = get_font

b_mod = types.ModuleType("core.module_base")
b_mod.BaseModule = BaseModule

core_pkg = types.ModuleType("core")
core_pkg.canvas = c_mod
core_pkg.module_base = b_mod

sys.modules["core"] = core_pkg
sys.modules["core.canvas"] = c_mod
sys.modules["core.module_base"] = b_mod

py_canvas = Canvas()
py_mod = None
`);
        wasmLoaded = true;
        wasmLoading = false;
        await loadRawPythonModule(currentDemo);
      } catch (err) {
        console.error("Pyodide WASM error:", err);
        wasmStatus = "Błąd ładowania Pyodide WASM.";
        wasmLoading = false;
        wasmActive = false;
        btnToggleWasm.classList.remove('active');
        btnToggleWasm.textContent = "🐍 Tryb Python WASM (Opcja)";
      }
    }

    async function loadRawPythonModule(modId) {
      if (!wasmLoaded || !pyodideInstance) return;
      wasmStatus = `Pobieranie ${modId}.py z repozytorium...`;
      try {
        let code = "";
        let resp = await fetch(`store/modules/${modId}.py`);
        if (!resp.ok) {
          resp = await fetch(`Apps/BrickDeck/modules/${modId}.py`);
        }
        if (resp.ok) {
          code = await resp.text();
        } else {
          throw new Error("Nie można pobrać pliku .py");
        }

        pyodideInstance.globals.set("raw_py_code", code);
        pyodideInstance.globals.set("raw_mod_id", modId);

        pyodideInstance.runPython(`
import sys

# Clean previous module
if 'user_mod' in sys.modules:
    del sys.modules['user_mod']

# Create and exec module namespace
user_mod = types.ModuleType("user_mod")
exec(raw_py_code, user_mod.__dict__)

# Find Module Class
mod_cls = None
for attr_name in dir(user_mod):
    if attr_name.endswith("Module") and attr_name != "BaseModule":
        mod_cls = getattr(user_mod, attr_name)
        break

if mod_cls:
    py_mod = mod_cls()
    py_canvas.clear()
else:
    py_mod = None
`);
        wasmStatus = "";
      } catch (e) {
        console.warn("WASM Module Load Fallback:", e);
        wasmStatus = `Błąd uruchamiania ${modId}.py w WASM.`;
      }
    }

    btnToggleWasm.addEventListener('click', async () => {
      wasmActive = !wasmActive;
      if (wasmActive) {
        btnToggleWasm.classList.add('active');
        btnToggleWasm.textContent = "🐍 Python WASM: AKTYWNY";
        if (!wasmLoaded) {
          await initPyodideWasm();
        } else {
          await loadRawPythonModule(currentDemo);
        }
      } else {
        btnToggleWasm.classList.remove('active');
        btnToggleWasm.textContent = "🐍 Tryb Python WASM (Opcja)";
      }
    });

    // ========================================================
    // INTERACTIVE ENGINES FOR CORE MODULES (FAST JS ENGINE)
    // ========================================================

    // 1. Raycaster 3D
    const rayDemo = {
      map: [
        1,1,1,1,1,1,1,1,1,1,1,1,
        1,0,0,0,0,0,1,0,0,0,0,1,
        1,0,2,2,0,0,1,0,3,3,0,1,
        1,0,2,0,0,0,0,0,0,3,0,1,
        1,0,2,0,1,1,0,0,0,3,0,1,
        1,0,0,0,1,0,0,2,0,0,0,1,
        1,1,0,1,1,0,1,2,2,0,0,1,
        1,0,0,0,0,0,1,0,0,0,0,1,
        1,0,3,3,0,0,1,0,2,2,0,1,
        1,0,3,0,0,0,0,0,0,0,0,1,
        1,0,0,0,0,0,0,0,0,0,0,1,
        1,1,1,1,1,1,1,1,1,1,1,1
      ],
      mapW: 12, mapH: 12,
      px: 2.5, py: 2.5, angle: 0.2, score: 1500,
      update() {
        const spd = (inputState.b ? 0.08 : 0.045);
        if (inputState.left) this.angle -= 0.045;
        if (inputState.right) this.angle += 0.045;
        const dx = Math.cos(this.angle) * spd, dy = Math.sin(this.angle) * spd;
        if (inputState.up) {
          if (this.map[Math.floor(this.py) * this.mapW + Math.floor(this.px + dx)] === 0) this.px += dx;
          if (this.map[Math.floor(this.py + dy) * this.mapW + Math.floor(this.px)] === 0) this.py += dy;
        }
        if (inputState.down) {
          if (this.map[Math.floor(this.py) * this.mapW + Math.floor(this.px - dx)] === 0) this.px -= dx;
          if (this.map[Math.floor(this.py - dy) * this.mapW + Math.floor(this.px)] === 0) this.py -= dy;
        }
      },
      render() {
        const w = canvas.width, h = canvas.height;
        ctx.fillStyle = '#0a0f1d'; ctx.fillRect(0, 0, w, h / 2);
        ctx.fillStyle = '#0f172a'; ctx.fillRect(0, h / 2, w, h / 2);
        const numRays = 160, fov = 1.1, sliceW = w / numRays;
        for (let r = 0; r < numRays; r++) {
          const rayAngle = (this.angle - fov / 2) + (r / numRays) * fov;
          const sinA = Math.sin(rayAngle), cosA = Math.cos(rayAngle);
          let dist = 0, hit = 0, side = 0, rx = this.px, ry = this.py;
          while (hit === 0 && dist < 16) {
            dist += 0.05; rx = this.px + cosA * dist; ry = this.py + sinA * dist;
            const mx = Math.floor(rx), my = Math.floor(ry);
            if (mx >= 0 && mx < this.mapW && my >= 0 && my < this.mapH) {
              const tile = this.map[my * this.mapW + mx];
              if (tile > 0) { hit = tile; side = (Math.abs(rx - Math.round(rx)) < Math.abs(ry - Math.round(ry))) ? 0 : 1; }
            }
          }
          if (hit > 0) {
            const corrected = dist * Math.cos(rayAngle - this.angle);
            const lineH = Math.min(h, (h / corrected) * 1.2);
            const top = (h - lineH) / 2;
            const fog = Math.max(0.1, 1 - dist / 12);
            let col = (hit === 1) ? `rgb(0, ${Math.floor(210 * fog)}, ${Math.floor(255 * fog)})` :
                      (hit === 2) ? `rgb(${Math.floor(255 * fog)}, ${Math.floor(160 * fog)}, 0)` :
                                    `rgb(${Math.floor(200 * fog)}, 0, ${Math.floor(255 * fog)})`;
            if (side === 1) col = `rgb(0, ${Math.floor(130 * fog)}, ${Math.floor(170 * fog)})`;
            ctx.fillStyle = col; ctx.fillRect(r * sliceW, top, sliceW + 1, lineH);
          }
        }
        const mmSz = 80, cs = mmSz / this.mapW;
        ctx.fillStyle = 'rgba(6, 10, 16, 0.85)'; ctx.fillRect(w - mmSz - 12, 12, mmSz, mmSz);
        ctx.strokeStyle = '#00f0ff'; ctx.strokeRect(w - mmSz - 12, 12, mmSz, mmSz);
        for (let my = 0; my < this.mapH; my++) {
          for (let mx = 0; mx < this.mapW; mx++) {
            if (this.map[my * this.mapW + mx] > 0) { ctx.fillStyle = '#00f0ff'; ctx.fillRect(w - mmSz - 12 + mx * cs, 12 + my * cs, cs, cs); }
          }
        }
        ctx.fillStyle = '#ff3366'; ctx.beginPath(); ctx.arc(w - mmSz - 12 + this.px * cs, 12 + this.py * cs, 3, 0, Math.PI * 2); ctx.fill();
        renderHUD("🕹️ 3D RAYCASTER // CYBER-MAZE", `POZ: (${this.px.toFixed(1)}, ${this.py.toFixed(1)}) | Pkt: ${this.score}`);
      }
    };

    // 2. Powder & Physics Sandbox
    const sandDemo = {
      gw: 100, gh: 75, grid: new Uint8Array(100 * 75), brushX: 50, brushY: 30, material: 1,
      init() {
        this.grid.fill(0);
        for (let x = 10; x < 90; x++) this.grid[65 * this.gw + x] = 5;
        for (let y = 45; y < 65; y++) { this.grid[y * this.gw + 25] = 5; this.grid[y * this.gw + 75] = 5; }
      },
      update() {
        if (inputState.left) this.brushX = Math.max(2, this.brushX - 1);
        if (inputState.right) this.brushX = Math.min(this.gw - 3, this.brushX + 1);
        if (inputState.up) this.brushY = Math.max(2, this.brushY - 1);
        if (inputState.down) this.brushY = Math.min(this.gh - 3, this.brushY + 1);
        if (inputState.x) { this.material = (this.material % 4) + 1; inputState.x = false; }
        if (inputState.a || Math.random() < 0.25) {
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              const idx = (this.brushY + dy) * this.gw + (this.brushX + dx);
              if (this.grid[idx] === 0) this.grid[idx] = this.material;
            }
          }
        }
        for (let y = this.gh - 2; y >= 1; y--) {
          for (let x = 1; x < this.gw - 1; x++) {
            const idx = y * this.gw + x, elem = this.grid[idx];
            if (elem === 1) {
              const b = (y + 1) * this.gw + x;
              if (this.grid[b] === 0 || this.grid[b] === 2) { const s = this.grid[b]; this.grid[b] = 1; this.grid[idx] = s; }
              else if (this.grid[b - 1] === 0) { this.grid[b - 1] = 1; this.grid[idx] = 0; }
              else if (this.grid[b + 1] === 0) { this.grid[b + 1] = 1; this.grid[idx] = 0; }
            } else if (elem === 2) {
              const b = (y + 1) * this.gw + x;
              if (this.grid[b] === 0) { this.grid[b] = 2; this.grid[idx] = 0; }
              else { const d = Math.random() < 0.5 ? -1 : 1; if (this.grid[y * this.gw + (x + d)] === 0) { this.grid[y * this.gw + (x + d)] = 2; this.grid[idx] = 0; } }
            } else if (elem === 3) {
              if (Math.random() < 0.15) this.grid[idx] = 0;
              else if (this.grid[(y - 1) * this.gw + x] === 0) { this.grid[(y - 1) * this.gw + x] = 3; this.grid[idx] = 0; }
            }
          }
        }
      },
      render() {
        const w = canvas.width, h = canvas.height, cw = w / this.gw, ch = h / this.gh;
        ctx.fillStyle = '#080c14'; ctx.fillRect(0, 0, w, h);
        for (let y = 0; y < this.gh; y++) {
          for (let x = 0; x < this.gw; x++) {
            const e = this.grid[y * this.gw + x];
            if (!e) continue;
            ctx.fillStyle = (e === 1) ? '#eab308' : (e === 2) ? '#0284c7' : (e === 3) ? '#ef4444' : (e === 4) ? '#22c55e' : '#64748b';
            ctx.fillRect(x * cw, y * ch, cw + 0.5, ch + 0.5);
          }
        }
        ctx.strokeStyle = '#00f0ff'; ctx.strokeRect(this.brushX * cw - 4, this.brushY * ch - 4, 8, 8);
        const matNames = ["", "PIASEK (Sand)", "WODA (Water)", "OGIEŃ (Fire)", "KWAS (Acid)"];
        renderHUD("⏳ POWDER & PHYSICS SANDBOX", `MATERIAŁ: ${matNames[this.material]} | [X]: Zmień | [A]: Syp`);
      }
    };
    sandDemo.init();

    // 3. CyberPet Tamagotchi
    const tamaDemo = {
      hunger: 85, happy: 90, anim: 0,
      update() {
        this.anim += 0.08;
        if (inputState.a) { this.hunger = Math.min(100, this.hunger + 10); inputState.a = false; }
        if (inputState.x) { this.happy = Math.min(100, this.happy + 10); inputState.x = false; }
      },
      render() {
        const w = canvas.width, h = canvas.height, cx = w / 2, cy = h / 2 - 20, bob = Math.sin(this.anim) * 10;
        ctx.fillStyle = '#06100c'; ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = '#10b981'; ctx.fillRect(cx - 60, cy - 60 + bob, 120, 110);
        ctx.strokeStyle = '#34d399'; ctx.lineWidth = 4; ctx.strokeRect(cx - 60, cy - 60 + bob, 120, 110);
        ctx.beginPath(); ctx.moveTo(cx, cy - 60 + bob); ctx.lineTo(cx, cy - 85 + bob); ctx.stroke();
        ctx.fillStyle = '#fbbf24'; ctx.beginPath(); ctx.arc(cx, cy - 90 + bob, 7, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#06100c'; ctx.fillRect(cx - 40, cy - 25 + bob, 22, 22); ctx.fillRect(cx + 18, cy - 25 + bob, 22, 22);
        ctx.beginPath(); ctx.arc(cx, cy + 15 + bob, 24, 0, Math.PI); ctx.stroke();
        renderHUD("👾 CYBERPET // VIRTUAL MONSTER", `GŁÓD: ${this.hunger}% | HUMOR: ${this.happy}% | [A]: Karm | [X]: Baw`);
      }
    };

    // 4. Cyber Artillery
    const tankDemo = {
      angle: 45, power: 60, projX: 0, projY: 0, pvx: 0, pvy: 0, flying: false,
      update() {
        if (inputState.up) this.angle = Math.min(85, this.angle + 1);
        if (inputState.down) this.angle = Math.max(5, this.angle - 1);
        if (inputState.right) this.power = Math.min(100, this.power + 1);
        if (inputState.left) this.power = Math.max(10, this.power - 1);
        if (inputState.a && !this.flying) {
          this.flying = true; const rad = (this.angle * Math.PI) / 180;
          this.projX = 80 + Math.cos(rad) * 20; this.projY = 380 - Math.sin(rad) * 20;
          this.pvx = Math.cos(rad) * (this.power * 0.18); this.pvy = -Math.sin(rad) * (this.power * 0.18);
          inputState.a = false;
        }
        if (this.flying) {
          this.pvy += 0.25; this.projX += this.pvx; this.projY += this.pvy;
          if (this.projY > 400 || this.projX > 640) this.flying = false;
        }
      },
      render() {
        const w = canvas.width, h = canvas.height;
        ctx.fillStyle = '#0a0f1d'; ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = '#1e293b'; ctx.beginPath(); ctx.moveTo(0, h); ctx.lineTo(0, 390);
        ctx.quadraticCurveTo(200, 320, 400, 410); ctx.quadraticCurveTo(520, 430, w, 370); ctx.lineTo(w, h); ctx.fill();
        ctx.fillStyle = '#00f0ff'; ctx.fillRect(66, 385, 28, 14);
        const rad = (this.angle * Math.PI) / 180;
        ctx.strokeStyle = '#00f0ff'; ctx.lineWidth = 4;
        ctx.beginPath(); ctx.moveTo(80, 385); ctx.lineTo(80 + Math.cos(rad) * 20, 385 - Math.sin(rad) * 20); ctx.stroke();
        ctx.fillStyle = '#ef4444'; ctx.fillRect(520, 375, 28, 14);
        if (this.flying) { ctx.fillStyle = '#ffaa00'; ctx.beginPath(); ctx.arc(this.projX, this.projY, 4, 0, Math.PI * 2); ctx.fill(); }
        renderHUD("💥 CYBER ARTILLERY // TANK WARS", `KĄT: ${this.angle}° | MOC: ${this.power}% | [A]: Ognia!`);
      }
    };

    // 5. Asteroids 360°
    const astDemo = {
      shipX: 320, shipY: 240, shipAngle: -Math.PI / 2, vx: 0, vy: 0,
      bullets: [], asteroids: [], score: 2400,
      init() {
        this.asteroids = [];
        for (let i = 0; i < 6; i++) {
          this.asteroids.push({
            x: Math.random() * 640, y: Math.random() * 480,
            vx: (Math.random() - 0.5) * 2, vy: (Math.random() - 0.5) * 2, r: 24
          });
        }
      },
      update() {
        if (inputState.left) this.shipAngle -= 0.08;
        if (inputState.right) this.shipAngle += 0.08;
        if (inputState.up) { this.vx += Math.cos(this.shipAngle) * 0.25; this.vy += Math.sin(this.shipAngle) * 0.25; }
        this.shipX = (this.shipX + this.vx + 640) % 640;
        this.shipY = (this.shipY + this.vy + 480) % 480;
        this.vx *= 0.98; this.vy *= 0.98;
        if (inputState.a) {
          this.bullets.push({ x: this.shipX, y: this.shipY, vx: Math.cos(this.shipAngle) * 7, vy: Math.sin(this.shipAngle) * 7, ttl: 40 });
          inputState.a = false;
        }
        this.bullets.forEach(b => { b.x += b.vx; b.y += b.vy; b.ttl--; });
        this.bullets = this.bullets.filter(b => b.ttl > 0);
        this.asteroids.forEach(a => { a.x = (a.x + a.vx + 640) % 640; a.y = (a.y + a.vy + 480) % 480; });
      },
      render() {
        const w = canvas.width, h = canvas.height;
        ctx.fillStyle = '#060a12'; ctx.fillRect(0, 0, w, h);
        ctx.strokeStyle = '#00ffcc'; ctx.lineWidth = 2;
        this.asteroids.forEach(a => { ctx.beginPath(); ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2); ctx.stroke(); });
        ctx.fillStyle = '#ffea00';
        this.bullets.forEach(b => { ctx.beginPath(); ctx.arc(b.x, b.y, 3, 0, Math.PI * 2); ctx.fill(); });
        ctx.save(); ctx.translate(this.shipX, this.shipY); ctx.rotate(this.shipAngle);
        ctx.strokeStyle = '#00f0ff'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(16, 0); ctx.lineTo(-12, -10); ctx.lineTo(-6, 0); ctx.lineTo(-12, 10); ctx.closePath(); ctx.stroke();
        ctx.restore();
        renderHUD("☄️ ASTEROIDS 360° // VECTOR COMBAT", `WYNIK: ${this.score} | [▲]: Ciąg | [◄►]: Obrót | [A]: Laser`);
      }
    };
    astDemo.init();

    // 6. Conway's Game of Life
    const lifeDemo = {
      cols: 48, rows: 36, grid: [], gen: 0,
      init() {
        this.grid = new Uint8Array(this.cols * this.rows);
        for (let i = 0; i < this.grid.length; i++) this.grid[i] = Math.random() < 0.2 ? 1 : 0;
      },
      update() {
        const next = new Uint8Array(this.cols * this.rows);
        for (let y = 0; y < this.rows; y++) {
          for (let x = 0; x < this.cols; x++) {
            let n = 0;
            for (let dy = -1; dy <= 1; dy++) {
              for (let dx = -1; dx <= 1; dx++) {
                if (dx === 0 && dy === 0) continue;
                const nx = (x + dx + this.cols) % this.cols, ny = (y + dy + this.rows) % this.rows;
                n += this.grid[ny * this.cols + nx];
              }
            }
            const idx = y * this.cols + x;
            if (this.grid[idx] === 1) next[idx] = (n === 2 || n === 3) ? 1 : 0;
            else next[idx] = (n === 3) ? 1 : 0;
          }
        }
        this.grid = next; this.gen++;
      },
      render() {
        const w = canvas.width, h = canvas.height, cw = w / this.cols, ch = h / this.rows;
        ctx.fillStyle = '#060f08'; ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = '#00ff88';
        for (let y = 0; y < this.rows; y++) {
          for (let x = 0; x < this.cols; x++) {
            if (this.grid[y * this.cols + x]) ctx.fillRect(x * cw + 1, y * ch + 1, cw - 1, ch - 1);
          }
        }
        renderHUD("🧬 CONWAY'S GAME OF LIFE", `GENERACJA: ${this.gen} | B3/S23 | [X]: Losuj nową zupę`);
      }
    };
    lifeDemo.init();

    // 7. 8-Bit Cyber Synth
    const synthDemo = {
      bpm: 128, step: 0, tick: 0,
      tracks: ["KICK", "SNARE", "HI-HAT", "BASS", "LEAD"],
      matrix: [
        [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
        [0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0],
        [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
        [1,0,1,0, 0,1,0,1, 1,0,1,0, 0,1,1,0],
        [0,1,0,1, 1,0,1,0, 0,1,0,1, 1,0,0,1]
      ],
      update() {
        this.tick++;
        if (this.tick % 7 === 0) this.step = (this.step + 1) % 16;
      },
      render() {
        const w = canvas.width, h = canvas.height;
        ctx.fillStyle = '#100818'; ctx.fillRect(0, 0, w, h);
        ctx.strokeStyle = '#c040fb'; ctx.lineWidth = 2; ctx.beginPath();
        for (let x = 0; x < w; x += 4) {
          const y = 80 + Math.sin(x * 0.05 + this.step) * 25 + Math.sin(x * 0.12) * 10;
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
        const startY = 150, stepW = 32, trackH = 45;
        this.tracks.forEach((t, ti) => {
          ctx.fillStyle = '#a855f7'; ctx.font = 'bold 12px "Fira Code", monospace';
          ctx.fillText(t, 20, startY + ti * trackH + 25);
          for (let s = 0; s < 16; s++) {
            const sx = 100 + s * stepW, sy = startY + ti * trackH;
            const on = this.matrix[ti][s], isCur = (s === this.step);
            ctx.fillStyle = isCur ? '#ffffff' : on ? '#9333ea' : '#271838';
            ctx.fillRect(sx, sy, stepW - 4, trackH - 8);
          }
        });
        renderHUD("🎹 8-BIT CYBER SYNTH // TRACKER", `TEMPO: ${this.bpm} BPM | KROK: ${this.step + 1}/16 | [L1/R1]: BPM`);
      }
    };

    // 8. Mandelbrot Explorer
    const mandelDemo = {
      zoom: 120, cx: -0.7, cy: 0.0,
      update() {
        if (inputState.left) this.cx -= 20 / this.zoom;
        if (inputState.right) this.cx += 20 / this.zoom;
        if (inputState.up) this.cy -= 20 / this.zoom;
        if (inputState.down) this.cy += 20 / this.zoom;
        if (inputState.a) this.zoom *= 1.1;
        if (inputState.b) this.zoom = Math.max(40, this.zoom / 1.1);
      },
      render() {
        const w = canvas.width, h = canvas.height;
        ctx.fillStyle = '#06060c'; ctx.fillRect(0, 0, w, h);
        const step = 8;
        for (let py = 40; py < h; py += step) {
          const ci = (py - h / 2) / this.zoom + this.cy;
          for (let px = 0; px < w; px += step) {
            const cr = (px - w / 2) / this.zoom + this.cx;
            let zr = 0, zi = 0, it = 0;
            while (zr*zr + zi*zi <= 4 && it < 24) {
              const tr = zr*zr - zi*zi + cr; zi = 2*zr*zi + ci; zr = tr; it++;
            }
            if (it === 24) ctx.fillStyle = '#000000';
            else {
              const g = Math.floor((it / 24) * 255);
              ctx.fillStyle = `rgb(${g}, ${Math.floor(g*0.4)}, 255)`;
            }
            ctx.fillRect(px, py, step, step);
          }
        }
        renderHUD("🌀 MANDELBROT FRACTAL LAB", `Re: ${this.cx.toFixed(4)} | Im: ${this.cy.toFixed(4)} | Zoom: ${this.zoom.toFixed(0)}x | [A/B]: Zoom`);
      }
    };

    // 9. 2FA TOTP Vault
    const authDemo = {
      accounts: [
        { name: "GitHub // kawaczek", code: "749 201" },
        { name: "Google Cloud Platform", code: "183 940" },
        { name: "AWS Root Infrastructure", code: "612 045" },
        { name: "ProtonMail Secure", code: "921 553" }
      ],
      sec: 24,
      update() {
        if (Math.random() < 0.05) this.sec = (this.sec > 1) ? this.sec - 1 : 30;
      },
      render() {
        const w = canvas.width, h = canvas.height;
        ctx.fillStyle = '#081018'; ctx.fillRect(0, 0, w, h);
        this.accounts.forEach((acc, i) => {
          const y = 60 + i * 95;
          ctx.fillStyle = '#101c2b'; ctx.fillRect(40, y, w - 80, 80);
          ctx.strokeStyle = '#00f0ff'; ctx.lineWidth = 1; ctx.strokeRect(40, y, w - 80, 80);
          ctx.fillStyle = '#e2e8f0'; ctx.font = 'bold 16px "Fira Code", monospace';
          ctx.fillText(acc.name, 60, y + 32);
          ctx.fillStyle = '#00ff88'; ctx.font = 'bold 26px "Fira Code", monospace';
          ctx.fillText(acc.code, 60, y + 65);
          ctx.fillStyle = '#ffaa00'; ctx.font = '12px "Fira Code", monospace';
          ctx.fillText(`Ważność: ${this.sec}s`, w - 180, y + 50);
        });
        renderHUD("🛡️ TACTICAL 2FA TOTP // VAULT", `AIR-GAPPED HARDWARE MODE | RFC 6238`);
      }
    };

    // 10. RPG Companion & Dice
    const diceDemo = {
      sides: 20, lastRoll: 18,
      update() {
        if (inputState.a) {
          this.lastRoll = Math.floor(Math.random() * this.sides) + 1;
          inputState.a = false;
        }
      },
      render() {
        const w = canvas.width, h = canvas.height;
        ctx.fillStyle = '#120e06'; ctx.fillRect(0, 0, w, h);
        ctx.strokeStyle = '#ffaa00'; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(w / 2, h / 2, 90, 0, Math.PI * 2); ctx.stroke();
        ctx.fillStyle = (this.lastRoll === 20) ? '#00ff88' : '#ffea00';
        ctx.font = 'bold 54px "Fira Code", monospace'; ctx.textAlign = 'center';
        ctx.fillText(`${this.lastRoll}`, w / 2, h / 2 + 18);
        ctx.textAlign = 'left';
        renderHUD("🎲 TACTICAL RPG COMPANION", `KOŚĆ: k${this.sides} | [A]: Rzuć kością (/dev/urandom)`);
      }
    };

    // 11. Desk Clock & MZK
    const clockDemo = {
      render() {
        const w = canvas.width, h = canvas.height;
        ctx.fillStyle = '#070b12'; ctx.fillRect(0, 0, w, h);
        const now = new Date();
        const timeStr = now.toTimeString().split(' ')[0];
        ctx.fillStyle = '#00f0ff'; ctx.font = 'bold 56px "Fira Code", monospace'; ctx.textAlign = 'center';
        ctx.fillText(timeStr, w / 2, 170);
        ctx.fillStyle = '#94a3b8'; ctx.font = '18px "Fira Code", monospace';
        ctx.fillText("GORZÓW WLKP. // POGODA: 21°C SŁONECZNIE", w / 2, 230);
        ctx.fillStyle = '#1e293b'; ctx.fillRect(60, 270, w - 120, 160);
        ctx.fillStyle = '#ffaa00'; ctx.font = 'bold 14px "Fira Code", monospace'; ctx.textAlign = 'left';
        ctx.fillText("LINIA   KIERUNEK               ODJAZD", 80, 305);
        ctx.fillStyle = '#00ff88';
        ctx.fillText("104     SŁONECZNA              ZA 2 MIN", 80, 340);
        ctx.fillText("126     OS. STASZICA           ZA 5 MIN", 80, 375);
        ctx.fillText("T2      WIEPRZYCE              ZA 7 MIN", 80, 410);
        renderHUD("🕒 DESK CLOCK // MZK GORZÓW", `SYNCHRONIZACJA NTP | OPEN-METEO`);
      }
    };

    // Helper: HUD overlay
    function renderHUD(title, sub) {
      const w = canvas.width;
      ctx.fillStyle = 'rgba(8, 14, 24, 0.9)'; ctx.fillRect(0, 0, w, 36);
      ctx.fillStyle = '#00f0ff'; ctx.font = 'bold 13px "Fira Code", monospace';
      ctx.fillText(title, 14, 23);
      ctx.fillStyle = '#00ff88'; ctx.font = 'bold 12px "Fira Code", monospace';
      ctx.fillText(sub, w - 340, 23);
    }

    // ========================================================
    // UNIVERSAL SCREENSHOT-BASED LIVE SIMULATOR FOR ALL APPS
    // ========================================================
    let radarSweep = 0;
    function renderUniversalApp(modId) {
      const w = canvas.width, h = canvas.height;
      const img = screenshotCache[modId];
      if (img && img.complete && img.naturalWidth > 0) {
        ctx.drawImage(img, 0, 0, w, h);
      } else {
        ctx.fillStyle = '#080c14'; ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = '#00f0ff'; ctx.font = 'bold 20px "Fira Code", monospace'; ctx.textAlign = 'center';
        ctx.fillText(`ŁADOWANIE: ${modId}...`, w / 2, h / 2);
        ctx.textAlign = 'left';
      }

      ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
      for (let y = 0; y < h; y += 4) ctx.fillRect(0, y, w, 1);

      if (['mod_air_radar', 'mod_marine', 'mod_radar', 'mod_blitz', 'mod_sky'].includes(modId)) {
        radarSweep = (radarSweep + 0.03) % (Math.PI * 2);
        ctx.strokeStyle = 'rgba(0, 255, 180, 0.35)'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(w / 2, h / 2);
        ctx.lineTo(w / 2 + Math.cos(radarSweep) * 200, h / 2 + Math.sin(radarSweep) * 200);
        ctx.stroke();
      }

      ctx.fillStyle = 'rgba(6, 12, 20, 0.75)'; ctx.fillRect(0, 0, w, 28);
      ctx.fillStyle = '#00f0ff'; ctx.font = 'bold 11px "Fira Code", monospace';
      ctx.fillText(`TRIMUI // ${modId.toUpperCase()}`, 12, 18);
      ctx.fillStyle = '#00ff88';
      const now = new Date();
      ctx.fillText(`🔋 98% | Wi-Fi 📶 | ${now.toTimeString().split(' ')[0]}`, w - 210, 18);

      if (buttonToastTimer > 0) {
        buttonToastTimer--;
        ctx.fillStyle = 'rgba(0, 240, 255, 0.85)';
        ctx.fillRect(w / 2 - 80, h - 45, 160, 28);
        ctx.fillStyle = '#050a14'; ctx.font = 'bold 12px "Fira Code", monospace'; ctx.textAlign = 'center';
        ctx.fillText(`PRZYCISK: [${lastButtonPressed}]`, w / 2, h - 26);
        ctx.textAlign = 'left';
      }
    }

    // ========================================================
    // BRICKDECK OS CAROUSEL LAUNCHER MODE
    // ========================================================
    function renderLauncher() {
      const w = canvas.width, h = canvas.height;
      ctx.fillStyle = 'rgba(6, 10, 18, 0.95)'; ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = '#00f0ff'; ctx.font = 'bold 22px "Rajdhani", sans-serif'; ctx.textAlign = 'center';
      ctx.fillText("BRICKDECK OS // WYBIERZ APLIKACJĘ", w / 2, 50);

      const cardW = 200, cardH = 260;
      for (let offset = -1; offset <= 1; offset++) {
        const idx = (launcherCursor + offset + allModules.length) % allModules.length;
        const mod = allModules[idx];
        const cx = w / 2 + offset * 220, cy = h / 2 + 10;
        const isCur = (offset === 0);

        ctx.fillStyle = isCur ? '#142032' : '#0c1420';
        ctx.fillRect(cx - cardW / 2, cy - cardH / 2, cardW, cardH);
        ctx.strokeStyle = isCur ? '#00f0ff' : '#223248'; ctx.lineWidth = isCur ? 3 : 1;
        ctx.strokeRect(cx - cardW / 2, cy - cardH / 2, cardW, cardH);

        const img = screenshotCache[mod.id];
        if (img && img.complete) {
          ctx.drawImage(img, cx - cardW / 2 + 10, cy - cardH / 2 + 10, cardW - 20, 120);
        }

        ctx.fillStyle = isCur ? '#ffffff' : '#829ab5';
        ctx.font = 'bold 13px "Rajdhani", sans-serif';
        ctx.fillText(mod.name, cx, cy + 30);

        ctx.fillStyle = '#00ff88'; ctx.font = '11px "Fira Code", monospace';
        ctx.fillText(mod.category, cx, cy + 55);
      }
      ctx.textAlign = 'left';
      ctx.fillStyle = '#ffaa00'; ctx.font = 'bold 12px "Fira Code", monospace';
      ctx.fillText("◀ ▶: Przeglądaj | [A]: Uruchom | [MENU]: Zamknij", 20, h - 20);
    }

    // ========================================================
    // MAIN SIMULATOR LOOP
    // ========================================================
    function mainLoop() {
      const w = canvas.width, h = canvas.height;

      if (isLauncherOpen) {
        renderLauncher();
      } else if (wasmActive) {
        // --- WASM MODE RUNNER ---
        if (!wasmLoaded || wasmLoading) {
          ctx.fillStyle = '#08101a'; ctx.fillRect(0, 0, w, h);
          ctx.fillStyle = '#ffaa00'; ctx.font = 'bold 18px "Fira Code", monospace'; ctx.textAlign = 'center';
          ctx.fillText("🐍 PYODIDE WEBASSEMBLY RUNNER", w / 2, h / 2 - 30);
          ctx.fillStyle = '#00f0ff'; ctx.font = '14px "Fira Code", monospace';
          ctx.fillText(wasmStatus || "Inicjalizacja silnika Pythona w przeglądarce...", w / 2, h / 2 + 10);
          ctx.fillStyle = '#829ab5'; ctx.font = '12px "Fira Code", monospace';
          ctx.fillText("Pobieranie WebAssembly (tylko raz, potem pamięć cache)", w / 2, h / 2 + 40);
          ctx.textAlign = 'left';
        } else {
          try {
            const hasMod = pyodideInstance.runPython(`py_mod is not None`);
            if (hasMod) {
              const rawBytes = pyodideInstance.runPython(`
py_mod.update(0.016)
py_canvas.clear()
py_mod.render(py_canvas)
py_canvas.image.tobytes("raw", "RGBA")
`);
              const imgData = new ImageData(new Uint8ClampedArray(rawBytes.toJs()), 1024, 768);
              wasmOffCtx.putImageData(imgData, 0, 0);
              ctx.drawImage(wasmOffscreenCanvas, 0, 0, w, h);

              // Badge
              ctx.fillStyle = 'rgba(0, 255, 136, 0.9)'; ctx.fillRect(w - 240, 10, 230, 24);
              ctx.fillStyle = '#000'; ctx.font = 'bold 11px "Fira Code", monospace';
              ctx.fillText("🐍 PYTHON WASM // LIVE .PY", w - 230, 26);
            } else {
              renderUniversalApp(currentDemo);
            }
          } catch (e) {
            console.error("Pyodide execution error:", e);
            renderUniversalApp(currentDemo);
          }
        }
      } else {
        // --- FAST JS MODE (DEFAULT) ---
        if (currentDemo === 'mod_raycaster') { rayDemo.update(); rayDemo.render(); }
        else if (currentDemo === 'mod_sandbox') { sandDemo.update(); sandDemo.render(); }
        else if (currentDemo === 'mod_tamagotchi') { tamaDemo.update(); tamaDemo.render(); }
        else if (currentDemo === 'mod_artillery') { tankDemo.update(); tankDemo.render(); }
        else if (currentDemo === 'mod_asteroids') { astDemo.update(); astDemo.render(); }
        else if (currentDemo === 'mod_life') { lifeDemo.update(); lifeDemo.render(); }
        else if (currentDemo === 'mod_synth') { synthDemo.update(); synthDemo.render(); }
        else if (currentDemo === 'mod_mandelbrot') { mandelDemo.update(); mandelDemo.render(); }
        else if (currentDemo === 'mod_auth') { authDemo.update(); authDemo.render(); }
        else if (currentDemo === 'mod_dice') { diceDemo.update(); diceDemo.render(); }
        else if (currentDemo === 'mod_clock') { clockDemo.render(); }
        else {
          renderUniversalApp(currentDemo);
        }
      }
      requestAnimationFrame(mainLoop);
    }
    requestAnimationFrame(mainLoop);

    // Switch demo via Dropdown
    demoSelect.addEventListener('change', async (e) => {
      currentDemo = e.target.value;
      currentModuleIdx = allModules.findIndex(m => m.id === currentDemo);
      isLauncherOpen = false;
      if (wasmActive && wasmLoaded) {
        await loadRawPythonModule(currentDemo);
      }
    });

    // Public helper to launch any app from store buttons
    window.launchInSimulator = async function(modId) {
      currentDemo = modId;
      demoSelect.value = modId;
      currentModuleIdx = allModules.findIndex(m => m.id === modId);
      isLauncherOpen = false;
      if (wasmActive && wasmLoaded) {
        await loadRawPythonModule(currentDemo);
      }
      document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });
    };

    // Cycle modules with L1 / R1
    async function switchModule(delta) {
      currentModuleIdx = (currentModuleIdx + delta + allModules.length) % allModules.length;
      currentDemo = allModules[currentModuleIdx].id;
      demoSelect.value = currentDemo;
      triggerButtonToast(delta > 0 ? "R1 // DALEJ" : "L1 // WRÓĆ");
      if (wasmActive && wasmLoaded) {
        await loadRawPythonModule(currentDemo);
      }
    }

    // Pass input to Python WASM if active
    function sendInputToWasm(keyName) {
      if (wasmActive && wasmLoaded && pyodideInstance) {
        try {
          pyodideInstance.runPython(`
if py_mod and hasattr(py_mod, 'handle_input'):
    py_mod.handle_input("${keyName}")
`);
        } catch (e) {}
      }
    }

    // Touch & Button bindings
    function bindBtn(id, key, toastName, pyKey) {
      const el = document.getElementById(id);
      if (!el) return;
      const press = () => {
        inputState[key] = true;
        el.classList.add('pressed');
        if (toastName) triggerButtonToast(toastName);
        if (pyKey) sendInputToWasm(pyKey);

        if (key === 'l1') switchModule(-1);
        if (key === 'r1') switchModule(1);
        if (key === 'menu') isLauncherOpen = !isLauncherOpen;
        if (isLauncherOpen) {
          if (key === 'left') launcherCursor = (launcherCursor - 1 + allModules.length) % allModules.length;
          if (key === 'right') launcherCursor = (launcherCursor + 1) % allModules.length;
          if (key === 'a') {
            currentDemo = allModules[launcherCursor].id;
            demoSelect.value = currentDemo;
            currentModuleIdx = launcherCursor;
            isLauncherOpen = false;
            if (wasmActive && wasmLoaded) loadRawPythonModule(currentDemo);
          }
        }
      };
      const release = () => { inputState[key] = false; el.classList.remove('pressed'); };
      el.addEventListener('mousedown', press);
      window.addEventListener('mouseup', release);
      el.addEventListener('touchstart', (e) => { e.preventDefault(); press(); });
      el.addEventListener('touchend', (e) => { e.preventDefault(); release(); });
    }

    bindBtn('btnUp', 'up', '▲ GÓRA', 'KEY_UP');
    bindBtn('btnDown', 'down', '▼ DÓŁ', 'KEY_DOWN');
    bindBtn('btnLeft', 'left', '◀ LEWO', 'KEY_LEFT');
    bindBtn('btnRight', 'right', '▶ PRAWO', 'KEY_RIGHT');
    bindBtn('btnA', 'a', 'A // AKCJA', 'KEY_A');
    bindBtn('btnB', 'b', 'B // COFNIJ', 'KEY_B');
    bindBtn('btnX', 'x', 'X // TRYB', 'KEY_X');
    bindBtn('btnY', 'y', 'Y // INFO', 'KEY_Y');
    bindBtn('btnL1', 'l1', 'L1', 'KEY_L1');
    bindBtn('btnR1', 'r1', 'R1', 'KEY_R1');
    bindBtn('btnMenu', 'menu', 'MENU', 'KEY_MENU');
    bindBtn('btnSelect', 'select', 'SELECT', 'KEY_SELECT');

    // PC Keyboard Listener
    window.addEventListener('keydown', (e) => {
      if (['ArrowUp', 'KeyW'].includes(e.code)) { inputState.up = true; triggerButtonToast('▲'); sendInputToWasm('KEY_UP'); }
      if (['ArrowDown', 'KeyS'].includes(e.code)) { inputState.down = true; triggerButtonToast('▼'); sendInputToWasm('KEY_DOWN'); }
      if (['ArrowLeft', 'KeyA'].includes(e.code)) {
        inputState.left = true;
        sendInputToWasm('KEY_LEFT');
        if (isLauncherOpen) launcherCursor = (launcherCursor - 1 + allModules.length) % allModules.length;
      }
      if (['ArrowRight', 'KeyD'].includes(e.code)) {
        inputState.right = true;
        sendInputToWasm('KEY_RIGHT');
        if (isLauncherOpen) launcherCursor = (launcherCursor + 1) % allModules.length;
      }
      if (['KeyJ', 'Space'].includes(e.code)) {
        inputState.a = true;
        triggerButtonToast('A');
        sendInputToWasm('KEY_A');
        if (isLauncherOpen) {
          currentDemo = allModules[launcherCursor].id;
          demoSelect.value = currentDemo;
          currentModuleIdx = launcherCursor;
          isLauncherOpen = false;
          if (wasmActive && wasmLoaded) loadRawPythonModule(currentDemo);
        }
      }
      if (['KeyK'].includes(e.code)) { inputState.b = true; triggerButtonToast('B'); sendInputToWasm('KEY_B'); }
      if (['KeyU'].includes(e.code)) { inputState.x = true; triggerButtonToast('X'); sendInputToWasm('KEY_X'); }
      if (['KeyI'].includes(e.code)) { inputState.y = true; triggerButtonToast('Y'); sendInputToWasm('KEY_Y'); }
      if (['KeyQ'].includes(e.code)) { switchModule(-1); }
      if (['KeyE'].includes(e.code)) { switchModule(1); }
      if (['KeyM', 'Escape'].includes(e.code)) { isLauncherOpen = !isLauncherOpen; }
    });

    window.addEventListener('keyup', (e) => {
      if (['ArrowUp', 'KeyW'].includes(e.code)) inputState.up = false;
      if (['ArrowDown', 'KeyS'].includes(e.code)) inputState.down = false;
      if (['ArrowLeft', 'KeyA'].includes(e.code)) inputState.left = false;
      if (['ArrowRight', 'KeyD'].includes(e.code)) inputState.right = false;
      if (['KeyJ', 'Space'].includes(e.code)) inputState.a = false;
      if (['KeyK'].includes(e.code)) inputState.b = false;
      if (['KeyU'].includes(e.code)) inputState.x = false;
      if (['KeyI'].includes(e.code)) inputState.y = false;
    });

    // ========================================================
    // STORE CATALOG LOADER & CARDS
    // ========================================================
    let modulesData = [];

    async function loadModules() {
      try {
        const res = await fetch('store/registry.json');
        if (res.ok) {
          const data = await res.json();
          modulesData = data.modules || [];
        }
      } catch (err) {
        console.warn('Fallback store load');
      }

      renderCards('all');
    }

    function renderCards(category) {
      const grid = document.getElementById('appsGrid');
      grid.innerHTML = '';

      const filtered = (category === 'all') 
        ? modulesData 
        : modulesData.filter(m => m.category === category);

      if (!filtered.length) {
        grid.innerHTML = '<p style="color:var(--text-muted); grid-column: 1/-1;">Brak modułów w wybranej kategorii.</p>';
        return;
      }

      filtered.forEach(m => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
          <div>
            <img src="docs/screenshots/${m.id}.png" alt="${m.name}" class="card-img" loading="lazy" onerror="this.style.display='none'">
            <div class="card-top">
              <div class="card-title">${m.name}</div>
              <span class="card-tag">${m.category}</span>
            </div>
            <p class="card-desc">${m.description}</p>
          </div>
          <div>
            <div class="card-meta">
              <span>Rozmiar: ${m.size_kb} KB</span>
              <span>v${m.version || '1.0'}</span>
            </div>
            <div class="card-actions" style="display:flex; flex-direction:column; gap:8px;">
              <button onclick="launchInSimulator('${m.id}')" class="card-btn" style="background:var(--accent-purple); color:#fff; border-color:var(--accent-purple);">
                🎮 Zagraj w Symulatorze
              </button>
              <a href="${m.download_url}" download="${m.id}.py" class="card-btn">
                Pobierz ${m.id}.py
              </a>
            </div>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderCards(btn.dataset.cat);
      });
    });

    loadModules();
  </script>
</body>
</html>
"""

final_html = html_prefix + new_script
with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(final_html)

print("[+] Successfully updated index.html with optional Python WASM (Pyodide) runner!")
