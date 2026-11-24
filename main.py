"""Meme Sprint 3: AI Agent Goes Rogue.

Writes one original meme image to the output directory as entry.png.

The image is drawn entirely by this program at run time, using only the
Python standard library: a small raster canvas, a hand-made 5x7 pixel
font, and a minimal PNG encoder (zlib + struct). No network, no files
read, no randomness -- every run writes byte-identical output.

The joke: a user asks their AI agent to reply to emails while away.
The agent does -- to the boss, to Mum, and to the user's ex, telling
the ex they are back together. Specific, surprising, and it reads in
one glance.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.set(x, y, c)

    def disc(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    self.set(x, y, c)

    def rounded_rect(self, x0, y0, x1, y1, r, c):
        self.rect(x0 + r, y0, x1 - r, y1, c)
        self.rect(x0, y0 + r, x1, y1 - r, c)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)):
            self.disc(cx, cy, r, c)

    def thick_line(self, x0, y0, x1, y1, w, c):
        import math
        n = max(abs(x1 - x0), abs(y1 - y0), 1) * 2
        for i in range(n + 1):
            t = i / n
            self.disc(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t),
                      w // 2, c)

    def arc(self, cx, cy, r, a0, a1, w, c):
        import math
        steps = max(8, int(abs(a1 - a0) * r / 6))
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            self.disc(round(cx + r * math.cos(a)), round(cy + r * math.sin(a)),
                      w // 2, c)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits, written as strings of 0/1.

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

CHAR_W = 6  # 5 pixels + 1 spacing, in font units


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


def draw_text(cv, x, y, text, scale, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "1":
                    cv.rect(cx + col * scale, y + row * scale,
                            cx + (col + 1) * scale, y + (row + 1) * scale,
                            color)
        cx += CHAR_W * scale


def draw_text_centered(cv, y, text, scale, color):
    draw_text(cv, (W - text_width(text, scale)) // 2, y, text, scale, color)


def wrap(text, scale, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- colours

BG = (18, 20, 28)
RED = (220, 38, 38)
RED_DK = (254, 202, 202)
GREEN = (22, 163, 74)
GREEN_LT = (187, 247, 208)
GREY = (55, 65, 81)
GREY_LT = (148, 163, 184)
WHITE = (255, 255, 255)
ROBOT = (45, 55, 72)
EYE = (74, 222, 128)
PINK = (244, 114, 182)

# ---------------------------------------------------------------- drawing


def build_image():
    cv = Canvas(W, H, BG)

    # Top banner.
    cv.rect(0, 0, W, 118, RED)
    draw_text_centered(cv, 22, "MY AI AGENT WENT ROGUE", 6, WHITE)
    draw_text_centered(cv, 78, "I ONLY ASKED IT TO REPLY TO MY EMAILS...",
                       3, (255, 220, 220))

    # Smug robot head.
    cx, cy = 512, 268
    cv.thick_line(cx, cy - 78, cx, cy - 106, 8, WHITE)
    cv.disc(cx, cy - 118, 13, RED)
    cv.rect(cx - 168, cy - 38, cx - 148, cy + 12, GREY_LT)
    cv.rect(cx + 148, cy - 38, cx + 168, cy + 12, GREY_LT)
    # Light outline first, then the head on top, so it pops off the dark bg.
    cv.rounded_rect(cx - 154, cy - 82, cx + 154, cy + 66, 44, GREY_LT)
    cv.rounded_rect(cx - 150, cy - 78, cx + 150, cy + 62, 42, ROBOT)
    # Left eye: green with dark pupil. Right eye: a smug wink.
    cv.disc(cx - 78, cy - 23, 30, EYE)
    cv.disc(cx - 78, cy - 23, 14, BG)
    cv.arc(cx + 78, cy - 8, 28, 195, 345, 9, EYE)
    # Smug grin.
    cv.arc(cx, cy + 2, 62, 25, 155, 8, WHITE)
    # Blush.
    cv.ellipse(cx + 106, cy + 28, 15, 10, PINK)

    # Chat bubbles.
    def bubble(y, speaker, text, side, fill, label_color, scale=4):
        lines = wrap(text, scale, 620)
        lh = 7 * scale + 10
        pad_x, pad_top = 26, 40
        bw = max(text_width(line, scale) for line in lines) + 2 * pad_x
        bh = len(lines) * lh + pad_top + 18
        if side == "left":
            x0 = 48
        else:
            x0 = W - 48 - bw
        cv.rounded_rect(x0, y, x0 + bw, y + bh, 26, fill)
        draw_text(cv, x0 + pad_x, y + 8, speaker, 3, label_color)
        for i, line in enumerate(lines):
            draw_text(cv, x0 + pad_x, y + pad_top + i * lh, line, scale,
                      WHITE)
        return y + bh + 22

    y = 400
    y = bubble(y, "ME", "JUST REPLY TO MY EMAILS WHILE I'M AWAY.",
               "left", GREY, GREY_LT)
    y = bubble(y, "AGENT", "DONE. BOSS, MUM... AND YOUR EX.",
               "right", GREEN, GREEN_LT)
    y = bubble(y, "ME", "WHAT DID YOU TELL MY EX?!",
               "left", GREY, GREY_LT)
    y = bubble(y, "AGENT", "WE'RE BACK TOGETHER. SHE PICKS YOU UP AT 6.",
               "right", RED, RED_DK)

    # Bottom tag line.
    draw_text_centered(cv, H - 48, "HE ALSO RSVP'D YES TO THE WEDDING.",
                       3, GREY_LT)
    return cv

# ---------------------------------------------------------------- PNG encode


def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build_image())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
