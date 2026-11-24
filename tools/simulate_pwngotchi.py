#!/usr/bin/env python3
"""
Simulated Pwngotchi HTTP Server (Mock Device)
Serves dynamic /ui PNG snapshots of a virtual Pwngotchi with animated faces and stats.
Allows testing Brickgotchi on PC without real hardware!
"""

import io
import time
import http.server
import socketserver
from PIL import Image, ImageDraw, ImageFont

PORT = 8080
FACES = [
    ("(◕‿‿◕)", "Szukam znajomych w poblizu..."),
    ("( ⚆_⚆)", "Widze nowa siec Wi-Fi!"),
    ("(⌐■_■)", "Wszystko pod pelna kontrola."),
    ("(♥‿‿♥)", "O! Znalazlem innego Pwngotchi!"),
    ("(⇀‿‿↼)", "Odpoczywam sobie w kieszeni... (zzZ)"),
    ("(^‿‿^)", "Ale super ekran ma ten TrimUI Brick!")
]

tick = 0

def generate_pwngotchi_image() -> bytes:
    """Generate a realistic 250x122 monochrome Pwngotchi screen image."""
    global tick
    tick += 1

    width, height = 250, 122
    img = Image.new("L", (width, height), 255)  # White background
    draw = ImageDraw.Draw(img)

    # Top border / status line
    ch_num = (tick % 13) + 1
    bat = 100 - (tick % 40)
    uptime_min = tick * 2
    header_text = f"CH {ch_num:02d}  |  UP {uptime_min//60:02d}:{uptime_min%60:02d}  |  BAT {bat}%"
    draw.text((8, 6), header_text, fill=0)
    draw.line([(0, 20), (width, 20)], fill=0, width=1)

    # Face & Mood
    face_idx = (tick // 3) % len(FACES)
    face_ascii, mood_text = FACES[face_idx]

    # Draw large face in center
    draw.text((60, 42), face_ascii, fill=0)

    # Bottom status message
    draw.line([(0, 95), (width, 95)], fill=0, width=1)
    draw.text((8, 102), mood_text, fill=0)

    # Save to PNG bytes
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


class PwngotchiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/ui", "/ui.png"):
            png_bytes = generate_pwngotchi_image()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(png_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(png_bytes)
        elif self.path in ("/", "/index.html"):
            html = """<html><head><title>Mock Pwngotchi</title></head>
            <body style='background:#222;color:#fff;text-align:center;'>
            <h1>Mock Pwngotchi Server</h1>
            <p>Live /ui feed:</p>
            <img src='/ui' style='border:2px solid cyan; border-radius:8px; margin:20px;' id='screen'>
            <script>setInterval(() => { document.getElementById('screen').src = '/ui?' + new Date().getTime(); }, 1000);</script>
            </body></html>"""
            b = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        else:
            self.send_error(404, "File Not Found")

    def log_message(self, format, *args):
        # Suppress noisy HTTP logs
        pass


def main():
    print("==================================================")
    print("      SYMULATOR PWNGOTCHI HTTP (MOCK SERVER)      ")
    print("==================================================")
    print(f"[*] Serwer uruchomiony pod adresem: http://127.0.0.1:{PORT}/ui")
    print("[*] Czekam na zapytania od Brickgotchi...\n")

    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PwngotchiHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nZatrzymano symulator Pwngotchi.")


if __name__ == "__main__":
    main()
