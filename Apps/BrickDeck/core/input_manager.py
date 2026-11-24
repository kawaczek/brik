"""
BrickDeck Input Manager - Unified Gamepad & Keyboard Input Layer
Normalizes Linux evdev hardware events and PC keyboard into unified tokens.
"""

import os
import sys
import glob
import select
import struct
import queue
import threading
import termios
import tty
from typing import Optional

# Standard Normalized Event Names
EVENT_UP        = "UP"
EVENT_DOWN      = "DOWN"
EVENT_LEFT      = "LEFT"
EVENT_RIGHT     = "RIGHT"
EVENT_A         = "BTN_A"
EVENT_B         = "BTN_B"
EVENT_X         = "BTN_X"
EVENT_Y         = "BTN_Y"
EVENT_L1        = "BTN_L1"
EVENT_R1        = "BTN_R1"
EVENT_SELECT    = "SELECT"
EVENT_START     = "START"
EVENT_MENU      = "MENU"
EVENT_QUIT      = "QUIT"

# Linux evdev keycode mapping (Standard gamepad & TrimUI Brick keys)
EVDEV_KEY_MAP = {
    103: EVENT_UP,
    108: EVENT_DOWN,
    105: EVENT_LEFT,
    106: EVENT_RIGHT,
    28:  EVENT_A,      # KEY_ENTER
    57:  EVENT_A,      # KEY_SPACE
    304: EVENT_A,      # BTN_A / BTN_SOUTH
    1:   EVENT_B,      # KEY_ESC
    14:  EVENT_B,      # KEY_BACKSPACE
    305: EVENT_B,      # BTN_B / BTN_EAST
    307: EVENT_X,      # BTN_X / BTN_NORTH
    45:  EVENT_X,      # KEY_X
    308: EVENT_Y,      # BTN_Y / BTN_WEST
    21:  EVENT_Y,      # KEY_Y
    310: EVENT_L1,     # BTN_TL (L1 bumper)
    311: EVENT_R1,     # BTN_TR (R1 bumper)
    314: EVENT_SELECT, # BTN_SELECT
    315: EVENT_START,  # BTN_START
    316: EVENT_MENU,   # BTN_MODE (Menu / Home)
    139: EVENT_MENU,   # KEY_MENU
}

# Terminal / PC Keyboard mapping
KEYBOARD_MAP = {
    "w": EVENT_UP,
    "s": EVENT_DOWN,
    "a": EVENT_LEFT,
    "d": EVENT_RIGHT,
    "\x1b[A": EVENT_UP,
    "\x1b[B": EVENT_DOWN,
    "\x1b[D": EVENT_LEFT,
    "\x1b[C": EVENT_RIGHT,
    "q": EVENT_L1,
    "e": EVENT_R1,
    " ": EVENT_A,
    "\r": EVENT_A,
    "\n": EVENT_A,
    "b": EVENT_B,
    "\x7f": EVENT_B,
    "\x08": EVENT_B,
    "x": EVENT_X,
    "y": EVENT_Y,
    "m": EVENT_MENU,
    "\x1b": EVENT_MENU,
}


class InputManager:
    """Listens for hardware and keyboard inputs in background worker."""

    def __init__(self, enable_terminal: bool = True):
        self.enable_terminal = enable_terminal
        self.events = queue.Queue()
        self.running = False
        self.threads = []
        self._orig_termios = None

    def start(self):
        """Start background input listeners."""
        self.running = True

        # 1. Start evdev listener for /dev/input/event*
        t_evdev = threading.Thread(target=self._evdev_worker, daemon=True)
        t_evdev.start()
        self.threads.append(t_evdev)

        # 2. Start terminal keyboard listener if on PC/TTY
        if self.enable_terminal and sys.stdin.isatty():
            t_term = threading.Thread(target=self._terminal_worker, daemon=True)
            t_term.start()
            self.threads.append(t_term)

    def stop(self):
        """Stop listeners and restore terminal settings."""
        self.running = False
        if self._orig_termios and sys.stdin.isatty():
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._orig_termios)
            except Exception:
                pass

    def poll_event(self) -> Optional[str]:
        """Return next normalized event string, or None."""
        try:
            return self.events.get_nowait()
        except queue.Empty:
            return None

    def _evdev_worker(self):
        """Monitor Linux /dev/input/event* nodes."""
        paths = sorted(glob.glob("/dev/input/event*"))
        fds = []
        for p in paths:
            try:
                fd = os.open(p, os.O_RDONLY | os.O_NONBLOCK)
                fds.append(fd)
            except Exception:
                pass

        if not fds:
            return

        fmt = "llHHi"
        sz = struct.calcsize(fmt)

        while self.running:
            r, _, _ = select.select(fds, [], [], 0.05)
            for fd in r:
                try:
                    data = os.read(fd, sz * 8)
                    for i in range(0, len(data), sz):
                        chunk = data[i:i + sz]
                        if len(chunk) < sz:
                            continue
                        _, _, ev_type, ev_code, ev_value = struct.unpack(fmt, chunk)
                        if ev_type == 1 and ev_value == 1:  # EV_KEY Press
                            if ev_code in EVDEV_KEY_MAP:
                                norm_event = EVDEV_KEY_MAP[ev_code]
                                self.events.put(norm_event)
                except Exception:
                    pass

        for fd in fds:
            try:
                os.close(fd)
            except Exception:
                pass

    def _terminal_worker(self):
        """Read non-blocking keys from terminal on PC."""
        fd = sys.stdin.fileno()
        try:
            self._orig_termios = termios.tcgetattr(fd)
            tty.setraw(fd)
        except Exception:
            return

        while self.running:
            r, _, _ = select.select([sys.stdin], [], [], 0.05)
            if r:
                try:
                    ch = sys.stdin.read(1)
                    if ch == "\x1b":  # Potential escape sequence
                        # Read rest of escape sequence if available
                        r2, _, _ = select.select([sys.stdin], [], [], 0.02)
                        if r2:
                            seq = sys.stdin.read(2)
                            ch += seq
                    if ch in ("\x03",):  # Ctrl+C
                        self.events.put(EVENT_QUIT)
                        break
                    if ch in KEYBOARD_MAP:
                        self.events.put(KEYBOARD_MAP[ch])
                except Exception:
                    break
