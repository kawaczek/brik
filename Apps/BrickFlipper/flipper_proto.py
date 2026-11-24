#!/usr/bin/env python3
"""
Zero-dependency Flipper Zero RPC & Serial Protocol Client
Communicates with Flipper Zero over USB Serial or BLE using raw Protobuf frames.
"""

import os
import sys
import time
import glob
import serial
from typing import Optional, Tuple, Callable

# Flipper Protobuf Field Constants (Main message)
FIELD_COMMAND_ID = 1
FIELD_COMMAND_STATUS = 2
FIELD_HAS_NEXT = 3
FIELD_PING_REQUEST = 4
FIELD_PING_RESPONSE = 5
FIELD_GUI_START_SCREEN_STREAM = 20
FIELD_GUI_STOP_SCREEN_STREAM = 21
FIELD_GUI_SCREEN_FRAME = 22
FIELD_GUI_SEND_INPUT = 23

# Input Keys
KEY_UP = 0
KEY_DOWN = 1
KEY_RIGHT = 2
KEY_LEFT = 3
KEY_OK = 4
KEY_BACK = 5

KEY_NAMES = {
    KEY_UP: "UP",
    KEY_DOWN: "DOWN",
    KEY_RIGHT: "RIGHT",
    KEY_LEFT: "LEFT",
    KEY_OK: "OK",
    KEY_BACK: "BACK",
}

# Input Types
TYPE_PRESS = 0
TYPE_RELEASE = 1
TYPE_SHORT = 2
TYPE_LONG = 3
TYPE_REPEAT = 4


def encode_varint(value: int) -> bytes:
    """Encode an integer as a standard Protobuf varint."""
    data = bytearray()
    while value > 0x7F:
        data.append((value & 0x7F) | 0x80)
        value >>= 7
    data.append(value & 0x7F)
    return bytes(data)


def decode_varint(stream) -> Optional[int]:
    """Read and decode a Protobuf varint from a readable stream or Serial."""
    result = 0
    shift = 0
    while True:
        b = stream.read(1)
        if not b:
            return None
        byte = b[0]
        result |= ((byte & 0x7F) << shift)
        if not (byte & 0x80):
            break
        shift += 7
        if shift >= 64:
            raise ValueError("Varint too long")
    return result


class FlipperClient:
    def __init__(self, port: Optional[str] = None, baudrate: int = 230400, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.command_id = 0
        self.connected = False
        self.streaming = False

    @staticmethod
    def auto_detect_port() -> Optional[str]:
        """Find connected Flipper Zero serial device."""
        # 1. By USB ID
        by_id = glob.glob("/dev/serial/by-id/*Flipper*")
        if by_id and os.path.exists(by_id[0]):
            return by_id[0]

        # 2. Virtual simulator port
        if os.path.exists("/tmp/flipper_vserial"):
            return "/tmp/flipper_vserial"

        # 3. Standard /dev/ttyACM* devices
        acm_list = sorted(glob.glob("/dev/ttyACM*"))
        if acm_list:
            return acm_list[0]

        # 4. Fallback macOS / other Linux ports
        cu_list = glob.glob("/dev/cu.usbmodemflip_*")
        if cu_list:
            return cu_list[0]

        return None

    def connect(self, retry_count: int = 3) -> bool:
        """Connect to Flipper Zero and initialize RPC mode."""
        port = self.port or self.auto_detect_port()
        if not port:
            print("[FlipperClient] No Flipper Zero device detected.")
            return False

        print(f"[FlipperClient] Connecting to {port} @ {self.baudrate} baud...")
        try:
            self.ser = serial.Serial(port, baudrate=self.baudrate, timeout=self.timeout)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

            # Synchronize with Flipper CLI prompt
            time.sleep(0.1)
            self.ser.write(b"\r\n")
            time.sleep(0.1)

            # Look for command prompt
            resp = self.ser.read_all()
            if b">: " not in resp:
                # Send another break/newline
                self.ser.write(b"\r\n")
                time.sleep(0.1)
                resp += self.ser.read_all()

            # Start RPC Session
            self.ser.write(b"start_rpc_session\r\n")
            time.sleep(0.05)
            ack = self.ser.readline()

            self.connected = True
            print(f"[FlipperClient] RPC session established successfully on {port}!")
            return True
        except Exception as e:
            print(f"[FlipperClient] Connection error: {e}")
            self.close()
            return False

    def close(self):
        """Cleanly close RPC session and serial port."""
        if self.ser and self.ser.is_open:
            if self.streaming:
                try:
                    self.stop_screen_stream()
                except Exception:
                    pass
            try:
                self.ser.close()
            except Exception:
                pass
        self.connected = False
        self.streaming = False

    def _next_command_id(self) -> int:
        self.command_id += 1
        return self.command_id

    def _send_message(self, payload: bytes):
        """Send length-delimited protobuf message."""
        length_varint = encode_varint(len(payload))
        self.ser.write(length_varint + payload)
        self.ser.flush()

    def start_screen_stream(self) -> bool:
        """Tell Flipper to begin continuous live screen streaming."""
        cmd_id = self._next_command_id()
        # Main message:
        # tag 1 (command_id): b'\x08' + varint
        # tag 20 (gui_start_screen_stream_request, wire 2): (20<<3)|2 = 162 = b'\xa2\x01'
        # length 0: b'\x00'
        payload = b"\x08" + encode_varint(cmd_id) + b"\xa2\x01\x00"
        self._send_message(payload)
        self.streaming = True
        return True

    def stop_screen_stream(self) -> bool:
        """Tell Flipper to stop screen stream."""
        cmd_id = self._next_command_id()
        # tag 21 (gui_stop_screen_stream_request, wire 2): (21<<3)|2 = 170 = b'\xaa\x01'
        payload = b"\x08" + encode_varint(cmd_id) + b"\xaa\x01\x00"
        self._send_message(payload)
        self.streaming = False
        return True

    def send_input_event(self, key: int, press_type: int):
        """
        Send a key press/release event to Flipper Zero.
        key: KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_BACK
        press_type: TYPE_PRESS, TYPE_RELEASE, TYPE_SHORT
        """
        cmd_id = self._next_command_id()

        # SendInputEventRequest inner message:
        # field 1: InputKey (enum, varint) -> tag (1<<3)|0 = 0x08
        # field 2: InputType (enum, varint) -> tag (2<<3)|0 = 0x10
        inner = bytearray()
        inner.extend(b"\x08" + encode_varint(key))
        inner.extend(b"\x10" + encode_varint(press_type))

        # Main message:
        # field 1: command_id (varint)
        # field 23: gui_send_input_event_request (tag (23<<3)|2 = 186 = 0xba, 0x01)
        payload = bytearray()
        payload.extend(b"\x08" + encode_varint(cmd_id))
        payload.extend(b"\xba\x01")
        payload.extend(encode_varint(len(inner)))
        payload.extend(inner)

        self._send_message(bytes(payload))

    def send_short_click(self, key: int):
        """Helper to send a full SHORT press to Flipper."""
        self.send_input_event(key, TYPE_PRESS)
        self.send_input_event(key, TYPE_SHORT)
        self.send_input_event(key, TYPE_RELEASE)

    def read_screen_frame(self, timeout_sec: float = 0.5) -> Optional[bytes]:
        """
        Read the next protobuf message from serial and extract 1024-byte screen frame.
        Returns 1024 bytes (SSD1306 display memory) or None if timeout.
        """
        if not self.ser or not self.ser.is_open:
            return None

        orig_timeout = self.ser.timeout
        self.ser.timeout = timeout_sec
        try:
            msg_len = decode_varint(self.ser)
            if msg_len is None:
                return None

            raw_msg = self.ser.read(msg_len)
            if len(raw_msg) < msg_len:
                return None

            # Parse fields in Main message to find gui_screen_frame (tag 22 -> 178 = 0xb2, 0x01)
            idx = 0
            while idx < len(raw_msg):
                # Decode tag as varint
                tag_val = 0
                shift = 0
                while idx < len(raw_msg):
                    b = raw_msg[idx]
                    idx += 1
                    tag_val |= ((b & 0x7F) << shift)
                    if not (b & 0x80):
                        break
                    shift += 7

                wire_type = tag_val & 0x07
                field_num = tag_val >> 3

                if field_num == FIELD_GUI_SCREEN_FRAME and wire_type == 2:
                    # Inside ScreenFrame: field 1 is bytes data (tag 0x0a)
                    # Read length of ScreenFrame message
                    frame_len = 0
                    sh = 0
                    while idx < len(raw_msg):
                        b = raw_msg[idx]
                        idx += 1
                        frame_len |= ((b & 0x7F) << sh)
                        if not (b & 0x80):
                            break
                        sh += 7

                    # Look for inner tag 0x0A (field 1, wire 2)
                    frame_end = idx + frame_len
                    while idx < frame_end:
                        inner_tag = raw_msg[idx]
                        idx += 1
                        if inner_tag == 0x0A:
                            # Read length of data (should be 1024)
                            data_len = 0
                            dsh = 0
                            while idx < frame_end:
                                db = raw_msg[idx]
                                idx += 1
                                data_len |= ((db & 0x7F) << dsh)
                                if not (db & 0x80):
                                    break
                                dsh += 7
                            data = raw_msg[idx:idx + data_len]
                            return data
                        else:
                            break
                elif wire_type == 0:  # Varint
                    while idx < len(raw_msg) and (raw_msg[idx] & 0x80):
                        idx += 1
                    idx += 1
                elif wire_type == 2:  # Length-delimited
                    length = 0
                    sh = 0
                    while idx < len(raw_msg):
                        db = raw_msg[idx]
                        idx += 1
                        length |= ((db & 0x7F) << sh)
                        if not (db & 0x80):
                            break
                        sh += 7
                    idx += length
                elif wire_type == 5:  # 32-bit
                    idx += 4
                elif wire_type == 1:  # 64-bit
                    idx += 8
                else:
                    break

            return None
        finally:
            self.ser.timeout = orig_timeout
