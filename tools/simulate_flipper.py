#!/usr/bin/env python3
"""
Flipper Zero Virtual Serial Simulator (Mock Device)
Creates a virtual serial port at /tmp/flipper_vserial using Unix PTY.
Simulates Flipper's RPC protocol, live screen streaming, and button inputs.
Allows testing BrickFlipper on PC without physical hardware!
"""

import os
import sys
import pty
import time
import math
import select
import threading

# Helper to encode varint
def encode_varint(value: int) -> bytes:
    data = bytearray()
    while value > 0x7F:
        data.append((value & 0x7F) | 0x80)
        value >>= 7
    data.append(value & 0x7F)
    return bytes(data)

def decode_varint_from_bytes(data: bytes, offset: int = 0):
    result = 0
    shift = 0
    idx = offset
    while idx < len(data):
        b = data[idx]
        idx += 1
        result |= ((b & 0x7F) << shift)
        if not (b & 0x80):
            break
        shift += 7
    return result, idx


class FlipperMock:
    def __init__(self):
        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_name = os.ttyname(self.slave_fd)
        self.symlink_path = "/tmp/flipper_vserial"

        # Setup symlink
        if os.path.exists(self.symlink_path) or os.path.islink(self.symlink_path):
            try:
                os.unlink(self.symlink_path)
            except Exception:
                pass
        os.symlink(self.slave_name, self.symlink_path)

        self.in_rpc_mode = False
        self.streaming = False
        self.running = True
        self.selected_item = 0
        self.menu_items = ["Sub-GHz", "125kHz RFID", "NFC", "Infrared", "iButton", "Bad USB"]
        self.anim_tick = 0

    def generate_screen_buffer(self) -> bytes:
        """Generate a simulated 128x64 SSD1306 buffer (1024 bytes)."""
        buf = bytearray(1024)
        self.anim_tick += 1

        def set_pixel(x, y, val=1):
            if 0 <= x < 128 and 0 <= y < 64:
                page = y >> 3
                bit = y & 7
                if val:
                    buf[page * 128 + x] |= (1 << bit)
                else:
                    buf[page * 128 + x] &= ~(1 << bit)

        # Draw border
        for x in range(128):
            set_pixel(x, 0)
            set_pixel(x, 63)
        for y in range(64):
            set_pixel(0, y)
            set_pixel(127, y)

        # Draw header bar
        for x in range(128):
            set_pixel(x, 10)

        # Draw a simulated bouncing ball / wave in top right
        bx = int(100 + 15 * math.sin(self.anim_tick * 0.2))
        by = int(5 + 3 * math.cos(self.anim_tick * 0.2))
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                set_pixel(bx + dx, by + dy)

        # Draw menu items representation
        for idx in range(len(self.menu_items)):
            base_y = 14 + idx * 8
            if base_y > 55:
                break
            # Highlight selected item
            is_sel = (idx == self.selected_item)
            if is_sel:
                for x in range(4, 124):
                    for y in range(base_y, base_y + 7):
                        set_pixel(x, y, 1)

            # Draw a simulated text line
            for x in range(10, 60 + (idx * 6)):
                set_pixel(x, base_y + 3, 0 if is_sel else 1)

        return bytes(buf)

    def send_screen_frame(self):
        """Send a gui_screen_frame message over master_fd."""
        if not self.streaming:
            return

        frame_data = self.generate_screen_buffer()

        # Build ScreenFrame protobuf: field 1: bytes data (tag 0x0a)
        inner = bytearray()
        inner.append(0x0A)
        inner.extend(encode_varint(len(frame_data)))
        inner.extend(frame_data)

        # Main message:
        # field 1: command_id = 0
        # field 22: gui_screen_frame (tag (22<<3)|2 = 178 = 0xb2, 0x01)
        payload = bytearray()
        payload.extend(b"\x08\x00")
        payload.extend(b"\xb2\x01")
        payload.extend(encode_varint(len(inner)))
        payload.extend(inner)

        full_packet = encode_varint(len(payload)) + payload
        try:
            os.write(self.master_fd, full_packet)
        except Exception:
            pass

    def run(self):
        print("==================================================")
        print("   WIRTUALNY SYMULATOR FLIPPERA ZERO (MOCK)       ")
        print("==================================================")
        print(f"[*] Utworzono wirtualny port: {self.symlink_path} -> {self.slave_name}")
        print("[*] Czekam na polaczenie z BrickFlipper...\n")

        last_frame_time = time.time()
        while self.running:
            r, _, _ = select.select([self.master_fd], [], [], 0.05)
            if r:
                try:
                    data = os.read(self.master_fd, 1024)
                except OSError:
                    break
                if not data:
                    break

                if not self.in_rpc_mode:
                    if b"\r" in data or b"\n" in data:
                        if b"start_rpc_session" in data:
                            self.in_rpc_mode = True
                            os.write(self.master_fd, b"\n")
                            print("[Mock Flipper] Rozpoczeto sesje RPC!")
                        else:
                            os.write(self.master_fd, b">: ")
                else:
                    # Parse RPC commands
                    # Check for gui_start_screen_stream (tag 20 -> 0xa2, 0x01)
                    if b"\xa2\x01" in data:
                        self.streaming = True
                        print("[Mock Flipper] Rozpoczeto strumieniowanie ekranu!")
                    elif b"\xaa\x01" in data:
                        self.streaming = False
                        print("[Mock Flipper] Zatrzymano strumieniowanie ekranu.")
                    elif b"\xba\x01" in data:
                        # Input event received
                        # Check key inside: 0=UP, 1=DOWN, 4=OK, 5=BACK
                        if b"\x08\x00" in data:
                            self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                            print("[Mock Flipper] Wcisnieto: GORA")
                        elif b"\x08\x01" in data:
                            self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                            print("[Mock Flipper] Wcisnieto: DOL")
                        elif b"\x08\x04" in data:
                            print(f"[Mock Flipper] Wcisnieto: OK -> Wybrano: {self.menu_items[self.selected_item]}")
                        elif b"\x08\x05" in data:
                            print("[Mock Flipper] Wcisnieto: WROC (BACK)")

            now = time.time()
            if self.streaming and (now - last_frame_time) >= 0.05:  # ~20 FPS simulation
                self.send_screen_frame()
                last_frame_time = now

    def close(self):
        self.running = False
        try:
            if os.path.exists(self.symlink_path):
                os.unlink(self.symlink_path)
            os.close(self.master_fd)
            os.close(self.slave_fd)
        except Exception:
            pass


if __name__ == "__main__":
    mock = FlipperMock()
    try:
        mock.run()
    except KeyboardInterrupt:
        print("\nZatrzymano symulator.")
    finally:
        mock.close()
