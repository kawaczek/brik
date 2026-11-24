"""
BrickDeck Module: Powder & Physics Sandbox (mod_sandbox.py)
Interactive cellular automata falling sand and chemistry physics toy.
Features:
- Real-time physics simulation of Sand, Water, Fire, Gunpowder, Acid, Wood, Lava, Stone, and Sparks
- Explosive chain reactions (Gunpowder + Fire/Spark)
- Chemical reactions (Acid melts stone/wood, Water cools Lava into Stone, Fire burns Wood)
- Fluid dynamics (Water & Lava flow and equalize levels, Sand sinks through Water)
- D-Pad cursor brush with adjustable radius (1px, 3px, 5px, 9px)
- Zero-dongle, 100% offline, smooth 60 FPS interactive physics on ARM64 Linux.
"""

import time
import random
from typing import List, Dict, Tuple, Optional

from PIL import Image

from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN, COLOR_NEON_PINK,
    COLOR_PANEL_BG, COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_STATUS_OK, COLOR_STATUS_WARN, COLOR_STATUS_ERR
)
from core.canvas import get_font
from core.i18n import t

# Simulation Grid Dimensions (Scales 4x to 640x560 on screen)
GRID_W = 160
GRID_H = 140

# Element IDs
E_AIR = 0
E_SAND = 1
E_WATER = 2
E_FIRE = 3
E_POWDER = 4
E_WOOD = 5
E_ACID = 6
E_LAVA = 7
E_STONE = 8
E_SPARK = 9

ELEMENT_DEFS = [
    {
        "id": E_AIR,
        "name": "Pustka (Gumka)",
        "badge": "ERASER",
        "color": (12, 16, 24),
        "desc": "Usuwa cząsteczki i oczyszcza przestrzeń."
    },
    {
        "id": E_SAND,
        "name": "Piasek (Sand)",
        "badge": "GRAVITY",
        "color": (235, 195, 75),
        "desc": "Sypie się pod grawitacją, tworzy stożki, tonie w wodzie."
    },
    {
        "id": E_WATER,
        "name": "Woda (Water)",
        "badge": "LIQUID",
        "color": (40, 140, 245),
        "desc": "Płynna ciecz, gasi ogień, zamienia lawę w kamień."
    },
    {
        "id": E_FIRE,
        "name": "Ogień (Fire)",
        "badge": "HEAT & DANGER",
        "color": (255, 75, 20),
        "desc": "Unosi się w górę, podpala drewno i detonuje proch!"
    },
    {
        "id": E_POWDER,
        "name": "Proch (Gunpowder)",
        "badge": "EXPLOSIVE",
        "color": (135, 135, 145),
        "desc": "Wybuchowy pył – dotknięcie ognia powoduje eksplozję!"
    },
    {
        "id": E_WOOD,
        "name": "Drewno (Wood)",
        "badge": "SOLID",
        "color": (130, 80, 40),
        "desc": "Stała zapora i materiał konstrukcyjny. Może spłonąć."
    },
    {
        "id": E_ACID,
        "name": "Kwas (Acid)",
        "badge": "CORROSIVE",
        "color": (50, 255, 70),
        "desc": "Żrąca ciecz – rozpuszcza piasek, drewno i kamień!"
    },
    {
        "id": E_LAVA,
        "name": "Lawa (Lava)",
        "badge": "MOLTEN",
        "color": (255, 130, 0),
        "desc": "Gorący stop, podpala wszystko. Z wodą tworzy kamień."
    },
    {
        "id": E_STONE,
        "name": "Kamień (Stone)",
        "badge": "UNBREAKABLE",
        "color": (95, 100, 110),
        "desc": "Ciężka, trwała ściana oporowa do budowy koryt i zbiorników."
    },
    {
        "id": E_SPARK,
        "name": "Iskra (Electric Spark)",
        "badge": "TRIGGER",
        "color": (225, 245, 255),
        "desc": "Ultraszybka iskra elektryczna – detonator prochu."
    }
]

# Color palette array indexed by element ID for instant pixel blitting
PALETTE_RGB = [
    (12, 16, 24),     # 0: Air
    (235, 195, 75),   # 1: Sand
    (40, 140, 245),   # 2: Water
    (255, 75, 20),    # 3: Fire
    (135, 135, 145),  # 4: Gunpowder
    (130, 80, 40),    # 5: Wood
    (50, 255, 70),    # 6: Acid
    (255, 130, 0),    # 7: Lava
    (95, 100, 110),   # 8: Stone
    (225, 245, 255),  # 9: Spark
]


class SandboxModule(BaseModule):
    name = "Powder & Physics Sandbox"
    short_name = "Sandbox"
    icon = "💥"
    accent_color = (255, 170, 0)

    def __init__(self, app_context=None):
        super().__init__(app_context)

        # Simulation grid array (flattened 1D array for max speed)
        self.grid = bytearray(GRID_W * GRID_H)
        self.fire_life = bytearray(GRID_W * GRID_H)

        # Cursor state
        self.cursor_x = GRID_W // 2
        self.cursor_y = GRID_H // 3
        self.brush_sizes = [1, 2, 4, 7]
        self.brush_idx = 1  # 2 radius (approx 5x5)
        self.active_elem_idx = 1  # Sand by default

        # Control states
        self.is_pouring = False
        self.is_erasing = False
        self.is_paused = False

        # Pre-build initial sandbox floor and container
        self._init_default_scene()

        # Telemetry
        self.active_particles = 0
        self.sim_fps = 60.0
        self.last_sim_time = time.time()
        self.frame_count = 0

    def _init_default_scene(self):
        self.grid = bytearray(GRID_W * GRID_H)
        self.fire_life = bytearray(GRID_W * GRID_H)

        # Draw stone floor and boundary walls
        for x in range(GRID_W):
            self.grid[(GRID_H - 1) * GRID_W + x] = E_STONE
            self.grid[(GRID_H - 2) * GRID_W + x] = E_STONE
            self.grid[x] = E_STONE

        for y in range(GRID_H):
            self.grid[y * GRID_W] = E_STONE
            self.grid[y * GRID_W + (GRID_W - 1)] = E_STONE

        # Draw a couple of fun initial funnels / platforms
        for x in range(25, 75):
            self.grid[60 * GRID_W + x] = E_WOOD
        for x in range(85, 135):
            self.grid[85 * GRID_W + x] = E_WOOD

        # Add initial pool of water and heap of gunpowder
        for y in range(95, 115):
            for x in range(25, 65):
                self.grid[y * GRID_W + x] = E_WATER

        for y in range(120, 136):
            for x in range(95, 130):
                self.grid[y * GRID_W + x] = E_POWDER

    def get_hotkey_hints(self):
        e_info = ELEMENT_DEFS[self.active_elem_idx]
        b_size = self.brush_sizes[self.brush_idx] * 2 + 1
        pause_lbl = "Wznów" if self.is_paused else "Pauza"
        return [
            ("L1/R1", f"Materiał: {e_info['badge']}"),
            ("D-Pad", "Kursor"),
            ("A", "Wylewaj / Syp"),
            ("B", "Gumka"),
            ("X", f"Pędzel: {b_size}px"),
            ("Y", "Wyczyść / Scena")
        ]

    def _apply_brush(self, elem_id: int):
        radius = self.brush_sizes[self.brush_idx]
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    gx = self.cursor_x + dx
                    gy = self.cursor_y + dy
                    if 1 <= gx < GRID_W - 1 and 1 <= gy < GRID_H - 1:
                        idx = gy * GRID_W + gx
                        # Don't overwrite indestructible outer boundary stone
                        if elem_id == E_AIR or self.grid[idx] != E_STONE or gy < GRID_H - 3:
                            self.grid[idx] = elem_id
                            if elem_id == E_FIRE:
                                self.fire_life[idx] = random.randint(15, 30)

    def update(self, dt: float):
        now = time.time()
        self.frame_count += 1
        if now - self.last_sim_time >= 0.5:
            self.sim_fps = self.frame_count / (now - self.last_sim_time)
            self.frame_count = 0
            self.last_sim_time = now

        # Continuous pouring if A or B is held
        if self.is_pouring:
            self._apply_brush(ELEMENT_DEFS[self.active_elem_idx]["id"])
        elif self.is_erasing:
            self._apply_brush(E_AIR)

        if self.is_paused:
            return

        # =============================================================
        # PHYSICAL SIMULATION TICK
        # Update from bottom to top so particles settle cleanly
        # =============================================================
        particle_counter = 0

        # Alternate horizontal scanning direction each frame to avoid left/right bias
        x_indices = list(range(1, GRID_W - 1))
        if self.frame_count % 2 == 0:
            x_indices.reverse()

        for y in range(GRID_H - 2, 0, -1):
            row = y * GRID_W
            below = (y + 1) * GRID_W
            above = (y - 1) * GRID_W

            for x in x_indices:
                idx = row + x
                cell = self.grid[idx]
                if cell == E_AIR:
                    continue

                particle_counter += 1

                # -----------------------------------------------------
                # 1. SAND (Opadanie, stożki, tonięcie w wodzie)
                # -----------------------------------------------------
                if cell == E_SAND:
                    b_idx = below + x
                    # Fall straight down into air or water (sand sinks in water!)
                    if self.grid[b_idx] == E_AIR:
                        self.grid[b_idx] = E_SAND
                        self.grid[idx] = E_AIR
                    elif self.grid[b_idx] == E_WATER:
                        self.grid[b_idx] = E_SAND
                        self.grid[idx] = E_WATER
                    else:
                        # Slide diagonally down-left or down-right
                        roll_dir = random.choice([-1, 1])
                        b_side = below + x + roll_dir
                        if self.grid[b_side] in (E_AIR, E_WATER):
                            swap_cell = self.grid[b_side]
                            self.grid[b_side] = E_SAND
                            self.grid[idx] = swap_cell
                        else:
                            b_other = below + x - roll_dir
                            if self.grid[b_other] in (E_AIR, E_WATER):
                                swap_cell = self.grid[b_other]
                                self.grid[b_other] = E_SAND
                                self.grid[idx] = swap_cell

                # -----------------------------------------------------
                # 2. GUNPOWDER (Sypie się jak piasek, detonuje w ogniu)
                # -----------------------------------------------------
                elif cell == E_POWDER:
                    b_idx = below + x
                    if self.grid[b_idx] == E_AIR:
                        self.grid[b_idx] = E_POWDER
                        self.grid[idx] = E_AIR
                    else:
                        roll_dir = random.choice([-1, 1])
                        b_side = below + x + roll_dir
                        if self.grid[b_side] == E_AIR:
                            self.grid[b_side] = E_POWDER
                            self.grid[idx] = E_AIR

                # -----------------------------------------------------
                # 3. WATER (Ciecz: opada, płynie poziomo, gasi ogień)
                # -----------------------------------------------------
                elif cell == E_WATER:
                    b_idx = below + x
                    if self.grid[b_idx] == E_AIR:
                        self.grid[b_idx] = E_WATER
                        self.grid[idx] = E_AIR
                    elif self.grid[b_idx] == E_FIRE:
                        # Water quenches fire
                        self.grid[b_idx] = E_AIR
                        self.grid[idx] = E_AIR
                    elif self.grid[b_idx] == E_LAVA:
                        # Water cools lava into stone
                        self.grid[b_idx] = E_STONE
                        self.grid[idx] = E_AIR
                    else:
                        # Flow sideways
                        flow_dir = random.choice([-1, 1])
                        side_idx = row + x + flow_dir
                        if self.grid[side_idx] == E_AIR:
                            self.grid[side_idx] = E_WATER
                            self.grid[idx] = E_AIR
                        elif self.grid[side_idx] == E_FIRE:
                            self.grid[side_idx] = E_AIR
                            self.grid[idx] = E_AIR
                        else:
                            other_side = row + x - flow_dir
                            if self.grid[other_side] == E_AIR:
                                self.grid[other_side] = E_WATER
                                self.grid[idx] = E_AIR

                # -----------------------------------------------------
                # 4. FIRE (Płomień: unosi się, podpala proch/drewno)
                # -----------------------------------------------------
                elif cell == E_FIRE:
                    if self.fire_life[idx] > 0:
                        self.fire_life[idx] -= 1
                    else:
                        self.grid[idx] = E_AIR
                        continue

                    # Check 4-neighbors for combustible materials
                    for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                        n_idx = ny * GRID_W + nx
                        n_val = self.grid[n_idx]
                        if n_val == E_POWDER:
                            # EXPLOSION! Detonate surrounding gunpowder in radius
                            for ex in range(max(1, nx - 3), min(GRID_W - 1, nx + 4)):
                                for ey in range(max(1, ny - 3), min(GRID_H - 1, ny + 4)):
                                    e_i = ey * GRID_W + ex
                                    if self.grid[e_i] in (E_POWDER, E_WOOD, E_AIR):
                                        self.grid[e_i] = E_FIRE
                                        self.fire_life[e_i] = random.randint(20, 45)
                        elif n_val == E_WOOD:
                            if random.random() < 0.15:
                                self.grid[n_idx] = E_FIRE
                                self.fire_life[n_idx] = random.randint(25, 50)
                        elif n_val == E_WATER:
                            self.grid[idx] = E_AIR
                            break

                    # Rise upwards randomly
                    up_idx = above + x + random.choice([-1, 0, 1])
                    if self.grid[up_idx] == E_AIR and random.random() < 0.5:
                        self.grid[up_idx] = E_FIRE
                        self.fire_life[up_idx] = self.fire_life[idx]
                        self.grid[idx] = E_AIR

                # -----------------------------------------------------
                # 5. ACID (Kwas: rozpuszcza piasek, drewno, kamień)
                # -----------------------------------------------------
                elif cell == E_ACID:
                    b_idx = below + x
                    if self.grid[b_idx] == E_AIR:
                        self.grid[b_idx] = E_ACID
                        self.grid[idx] = E_AIR
                    elif self.grid[b_idx] in (E_SAND, E_WOOD, E_STONE, E_POWDER):
                        # Dissolve!
                        self.grid[b_idx] = E_AIR
                        self.grid[idx] = E_AIR
                    else:
                        flow_dir = random.choice([-1, 1])
                        s_idx = row + x + flow_dir
                        if self.grid[s_idx] == E_AIR:
                            self.grid[s_idx] = E_ACID
                            self.grid[idx] = E_AIR
                        elif self.grid[s_idx] in (E_SAND, E_WOOD, E_STONE):
                            self.grid[s_idx] = E_AIR
                            self.grid[idx] = E_AIR

                # -----------------------------------------------------
                # 6. LAVA (Lawa: podpala, twardnieje w wodzie)
                # -----------------------------------------------------
                elif cell == E_LAVA:
                    b_idx = below + x
                    if self.grid[b_idx] == E_AIR:
                        self.grid[b_idx] = E_LAVA
                        self.grid[idx] = E_AIR
                    elif self.grid[b_idx] == E_WATER:
                        self.grid[b_idx] = E_STONE
                        self.grid[idx] = E_AIR
                    else:
                        if random.random() < 0.4:
                            flow_dir = random.choice([-1, 1])
                            s_idx = row + x + flow_dir
                            if self.grid[s_idx] == E_AIR:
                                self.grid[s_idx] = E_LAVA
                                self.grid[idx] = E_AIR
                            elif self.grid[s_idx] == E_WATER:
                                self.grid[s_idx] = E_STONE
                                self.grid[idx] = E_AIR

                # -----------------------------------------------------
                # 7. SPARK (Iskra: detonuje proch, gaśnie)
                # -----------------------------------------------------
                elif cell == E_SPARK:
                    # Explodes any touching gunpowder
                    for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                        n_idx = ny * GRID_W + nx
                        if self.grid[n_idx] == E_POWDER:
                            self.grid[n_idx] = E_FIRE
                            self.fire_life[n_idx] = random.randint(30, 60)
                    self.grid[idx] = E_AIR

        self.active_particles = particle_counter

    def render(self, canvas):
        # 1. Main Card Wrapper
        active_e = ELEMENT_DEFS[self.active_elem_idx]
        b_size = self.brush_sizes[self.brush_idx] * 2 + 1
        status_lbl = "PAUSED" if self.is_paused else f"{self.sim_fps:.0f} FPS"

        canvas.draw_card(
            x=25, y=66, w=974, h=638,
            title=f"💥 POWDER & PHYSICS SANDBOX: {active_e['name'].upper()}",
            subtitle=f"Cząstki: {self.active_particles}  |  Pędzel: {b_size}px  |  Status: {status_lbl}  |  Sterowanie: D-Pad + [A]",
            border_color=self.accent_color
        )

        # -------------------------------------------------------------
        # Left Panel: Simulation Viewport (x=40, y=116, w=640, h=560)
        # -------------------------------------------------------------
        vx, vy, vw, vh = 40, 116, 640, 560
        canvas.draw.rounded_rectangle([(vx, vy), (vx + vw, vy + vh)], radius=8, fill=(12, 16, 24), outline=COLOR_BORDER, width=2)

        # Render Simulation Grid using ultra-fast Image blit
        # Build raw RGB buffer
        raw_rgb = bytearray(GRID_W * GRID_H * 3)
        p_idx = 0
        for i in range(GRID_W * GRID_H):
            elem = self.grid[i]
            r, g, b = PALETTE_RGB[elem]
            # Extra fire flicker effect
            if elem == E_FIRE:
                flicker = random.randint(-20, 20)
                r = max(0, min(255, r + flicker))
                g = max(0, min(255, g + flicker))
            raw_rgb[p_idx] = r
            raw_rgb[p_idx + 1] = g
            raw_rgb[p_idx + 2] = b
            p_idx += 3

        sim_img = Image.frombytes("RGB", (GRID_W, GRID_H), bytes(raw_rgb))
        resized_sim = sim_img.resize((vw - 4, vh - 4), Image.NEAREST)
        canvas.image.paste(resized_sim, (vx + 2, vy + 2))

        # Render Cursor Crosshair
        scale_x = (vw - 4) / float(GRID_W)
        scale_y = (vh - 4) / float(GRID_H)
        c_px = int(vx + 2 + self.cursor_x * scale_x)
        c_py = int(vy + 2 + self.cursor_y * scale_y)
        b_radius_px = int(self.brush_sizes[self.brush_idx] * scale_x)

        # Crosshair reticle
        cur_col = active_e["color"] if not self.is_erasing else (255, 50, 50)
        canvas.draw.ellipse([(c_px - b_radius_px, c_py - b_radius_px), (c_px + b_radius_px, c_py + b_radius_px)], outline=cur_col, width=2)
        canvas.draw.line([(c_px - b_radius_px - 4, c_py), (c_px + b_radius_px + 4, c_py)], fill=cur_col, width=1)
        canvas.draw.line([(c_px, c_py - b_radius_px - 4), (c_px, c_py + b_radius_px + 4)], fill=cur_col, width=1)

        # On-screen Pouring Status Pill
        if self.is_pouring:
            canvas.draw_badge(vx + 14, vy + 12, "● SYPANIE: WŁĄCZONE (Naciśnij [A] lub Spację)", bg_color=(20, 120, 50), text_color=(255, 255, 255))
        elif self.is_erasing:
            canvas.draw_badge(vx + 14, vy + 12, "● GUMKA: WŁĄCZONA (Naciśnij [B])", bg_color=(120, 30, 30), text_color=(255, 255, 255))
        else:
            canvas.draw_badge(vx + 14, vy + 12, "○ SYPANIE: WYŁĄCZONE (Naciśnij [A] lub rysuj myszką)", bg_color=(36, 46, 64), text_color=COLOR_TEXT_PRIMARY)

        # -------------------------------------------------------------
        # Right Panel: Element Palette & Chemical Inspector (x=700, y=116, w=284, h=560)
        # -------------------------------------------------------------
        rx, ry, rw, rh = 700, 116, 284, 560
        canvas.draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=8, fill=(16, 20, 28), outline=COLOR_BORDER, width=1)

        # Header
        canvas.draw.text((rx + 14, ry + 12), "PALETA MATERIAŁÓW (L1/R1)", fill=COLOR_CYBER_CYAN, font=get_font(11, bold=True))
        canvas.draw.line([(rx + 12, ry + 32), (rx + rw - 12, ry + 32)], fill=COLOR_BORDER, width=1)

        # Elements Grid
        item_y = ry + 42
        for idx, elem in enumerate(ELEMENT_DEFS):
            if elem["id"] == E_AIR:
                continue  # Skip air in palette (B button is eraser)
            is_sel = (idx == self.active_elem_idx)

            fill_c = (26, 36, 48) if is_sel else (20, 24, 32)
            outline_c = elem["color"] if is_sel else (34, 42, 54)

            canvas.draw.rounded_rectangle([(rx + 10, item_y), (rx + rw - 10, item_y + 40)], radius=5, fill=fill_c, outline=outline_c, width=2 if is_sel else 1)

            # Color icon swatch
            canvas.draw.rectangle([(rx + 18, item_y + 10), (rx + 38, item_y + 30)], fill=elem["color"])
            # Label
            t_col = COLOR_TEXT_PRIMARY if is_sel else COLOR_TEXT_SECONDARY
            canvas.draw.text((rx + 46, item_y + 8), elem["name"], fill=t_col, font=get_font(10, bold=is_sel))
            canvas.draw.text((rx + 46, item_y + 24), elem["badge"], fill=COLOR_TEXT_MUTED, font=get_font(8, bold=True))

            item_y += 46

        # Active Material Info Card at bottom
        canvas.draw.line([(rx + 12, ry + rh - 105), (rx + rw - 12, ry + rh - 105)], fill=COLOR_BORDER, width=1)
        canvas.draw.text((rx + 14, ry + rh - 95), active_e["name"].upper(), fill=active_e["color"], font=get_font(11, bold=True))
        canvas.draw.text((rx + 14, ry + rh - 76), active_e["desc"], fill=COLOR_TEXT_SECONDARY, font=get_font(9))

        canvas.draw.text((rx + 14, ry + rh - 30), f"Pędzel: {b_size}px [X]  |  [Y]: Menu/Clear", fill=COLOR_TEXT_MUTED, font=get_font(9))

    # -----------------------------------------------------------------
    # INPUT HANDLING
    # -----------------------------------------------------------------
    def handle_pointer(self, cx: int, cy: int, is_down: bool) -> bool:
        """Handle direct mouse or touch interaction on simulation screen or palette."""
        vx, vy, vw, vh = 40, 116, 640, 560
        rx, ry, rw, rh = 700, 116, 284, 560

        # Check simulation viewport
        if vx <= cx <= vx + vw and vy <= cy <= vy + vh:
            grid_x = int((cx - vx - 2) * GRID_W / (vw - 4))
            grid_y = int((cy - vy - 2) * GRID_H / (vh - 4))
            self.cursor_x = max(2, min(GRID_W - 3, grid_x))
            self.cursor_y = max(2, min(GRID_H - 3, grid_y))
            self.is_pouring = is_down
            if is_down:
                self.is_erasing = False
                self._apply_brush(ELEMENT_DEFS[self.active_elem_idx]["id"])
            return True

        # Check palette item clicks
        if rx <= cx <= rx + rw and ry + 42 <= cy <= ry + rh - 110:
            item_y = ry + 42
            for idx, elem in enumerate(ELEMENT_DEFS):
                if elem["id"] == E_AIR:
                    continue
                if item_y <= cy <= item_y + 42:
                    self.active_elem_idx = idx
                    return True
                item_y += 46

        if not is_down:
            self.is_pouring = False
        return False

    def handle_input(self, event: str) -> bool:
        # Move Cursor D-Pad (with 3-cell step)
        step = 3
        if event in ("DPAD_UP", "w", "W", "UP"):
            self.cursor_y = max(2, self.cursor_y - step)
            return True
        elif event in ("DPAD_DOWN", "s", "S", "DOWN"):
            self.cursor_y = min(GRID_H - 3, self.cursor_y + step)
            return True
        elif event in ("DPAD_LEFT", "LEFT"):
            self.cursor_x = max(2, self.cursor_x - step)
            return True
        elif event in ("DPAD_RIGHT", "RIGHT"):
            self.cursor_x = min(GRID_W - 3, self.cursor_x + step)
            return True

        # Pour element: A button / Space / Enter
        elif event in ("BTN_A", "a", "A", "KEY_A", "KEY_ENTER", "SPACE", " "):
            self.is_pouring = not self.is_pouring
            self.is_erasing = False
            return True

        # Eraser: B button
        elif event in ("BTN_B", "b", "B"):
            self.is_erasing = not self.is_erasing
            self.is_pouring = False
            return True

        # Change Material: L1 / R1
        elif event in ("BTN_L1", "l1", "L1"):
            self.active_elem_idx = (self.active_elem_idx - 1) % len(ELEMENT_DEFS)
            if self.active_elem_idx == 0:  # Skip air in palette
                self.active_elem_idx = len(ELEMENT_DEFS) - 1
            return True
        elif event in ("BTN_R1", "r1", "R1"):
            self.active_elem_idx = (self.active_elem_idx + 1) % len(ELEMENT_DEFS)
            if self.active_elem_idx == 0:
                self.active_elem_idx = 1
            return True

        # Change Brush Size: X
        elif event in ("BTN_X", "x", "X"):
            self.brush_idx = (self.brush_idx + 1) % len(self.brush_sizes)
            return True

        # Actions Menu / Reset: Y
        elif event in ("BTN_Y", "y", "Y"):
            self._init_default_scene()
            return True

        return False
