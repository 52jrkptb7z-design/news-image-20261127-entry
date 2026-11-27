#!/usr/bin/env python3
"""The World in One Day - 27 November 2026.

Draws a broadsheet-style front page summing up Friday 27 November 2026
with pure Python 3 standard library: an own 5x7 bitmap font and an own
PNG encoder. No network, no randomness, no timestamps - the output is
byte-identical on every run.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 231)
INK = (22, 22, 22)
RED = (174, 32, 32)
NAVY = (24, 36, 66)
NAVY2 = (34, 50, 88)
YELLOW = (255, 212, 64)
SKY = (140, 175, 210)
BLUE = (38, 86, 158)
GOLD = (214, 176, 58)
GREY = (96, 93, 86)
WHITE = (250, 250, 248)

# ---------------------------------------------------------------- font ----
# Own 5x7 bitmap font. Each glyph is 7 rows of 5 cells ('#' = on).
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_width(text, scale):
    """Pixel width of text at the given scale."""
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if text_width(trial, scale) <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[base:base + 3] = bytes(color)
                base += 3

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            half = int((r * r - (yy - cy) ** 2) ** 0.5)
            for xx in range(cx - half, cx + half + 1):
                self.set(xx, yy, color)

    def polygon(self, points, color):
        """Even-odd scanline fill for a simple polygon."""
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    nodes.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            nodes.sort()
            for j in range(0, len(nodes) - 1, 2):
                for x in range(int(nodes[j]), int(nodes[j + 1]) + 1):
                    self.set(x, y, color)

    def text(self, x, y, s, scale, color):
        """Draw text at top-left (x, y); returns pixel width used."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch.upper(), FONT['?'])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '#':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx - x - scale

    def text_center(self, y, s, scale, color, cx=512):
        w = text_width(s, scale)
        self.text(cx - w // 2, y, s, scale, color)


# ----------------------------------------------------------------- png ----
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(c):
    raw = bytearray()
    stride = c.w * 3
    for y in range(c.h):
        raw.append(0)
        raw += c.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ------------------------------------------------------------- drawing ----
def draw_lightning(c, x, y, s):
    """Jagged lightning bolt, drawn as a polygon, scaled by s."""
    pts = [
        (x + 8 * s, y), (x + 16 * s, y), (x + 11 * s, y + 14 * s),
        (x + 18 * s, y + 14 * s), (x + 4 * s, y + 32 * s),
        (x + 9 * s, y + 15 * s), (x + 3 * s, y + 15 * s),
    ]
    c.polygon(pts, YELLOW)


def draw_rain(c, x0, y0, x1, y1, color, step=34):
    for x in range(x0, x1, step):
        for k in range(3):
            xx = x + k * 9
            yy = y0 + k * 12
            if xx < x1 and yy < y1:
                c.line(xx, yy, xx - 7, yy + 16, color)


def draw_drone(c, x, y, s):
    """Simple quadcopter silhouette."""
    body = (60, 60, 60)
    c.rect(x, y + 6 * s, 16 * s, 4 * s, body)
    c.rect(x + 5 * s, y + 4 * s, 6 * s, 3 * s, body)
    for dx, dy in ((0, 0), (14 * s, 0), (0, 8 * s), (14 * s, 8 * s)):
        c.disc(x + dx + s, y + dy + s, 2 * s, body)
        c.rect(x + dx - 2 * s, y + dy, 6 * s, s, body)
    # explosion starburst
    import math
    cx, cy = x + 26 * s, y + 5 * s
    for k in range(8):
        a = math.radians(k * 45)
        r = 7 * s if k % 2 == 0 else 3 * s
        c.line(cx, cy, cx + int(r * math.cos(a)), cy + int(r * math.sin(a)), GOLD)
    c.disc(cx, cy, 2 * s, GOLD)


def draw_warning_triangle(c, x, y, s):
    pts = [(x + 8 * s, y), (x + 16 * s, y + 14 * s), (x, y + 14 * s)]
    c.polygon(pts, GOLD)
    c.text(x + 6 * s, y + 5 * s, "!", 2, INK)


def draw_front_page():
    c = Canvas(W, H, PAPER)
    m = 28  # margin
    inner = W - 2 * m

    # --- masthead ------------------------------------------------------
    c.hline(m, 26, inner, INK, 4)
    c.text_center(44, "THE WORLD IN ONE DAY", 7, INK)
    c.hline(m, 130, inner, INK, 2)
    c.text_center(146, "FRIDAY 27 NOVEMBER 2026", 4, RED)
    c.hline(m, 182, inner, INK, 4)

    # --- hero: Thanksgiving storm --------------------------------------
    hy, hh = 196, 300
    c.rect(m, hy, inner, hh, NAVY)
    c.rect(m, hy, inner, 6, YELLOW)
    draw_lightning(c, m + 30, hy + 26, 3)
    draw_rain(c, m + 260, hy + 20, m + inner - 20, hy + 150, SKY)
    c.text(m + 30, hy + 148, "UNITED STATES - THE STORM", 2, YELLOW)
    hero_head = "THANKSGIVING STORM LEAVES NEARLY A MILLION IN THE DARK"
    lines = wrap_text(hero_head, 5, inner - 60)
    yy = hy + 172
    for ln in lines:
        c.text(m + 30, yy, ln, 5, WHITE)
        yy += 5 * 8 - 2
    yy += 6
    c.text(m + 30, yy, "Power out for 961,000 homes at the peak. 400+ flights cancelled.", 2, WHITE)
    yy += 20
    c.text(m + 30, yy, "Macy's parade postponed - a first in its 100-year history.", 2, WHITE)

    # --- middle row: two stories ---------------------------------------
    my, mh = 512, 236
    colw = (inner - 16) // 2
    # left: Kuwait
    c.rect(m, my, colw, mh, PAPER)
    c.rect(m, my, colw, mh, INK)  # placeholder overwritten below
    c.rect(m + 2, my + 2, colw - 4, mh - 4, PAPER)
    c.text(m + 16, my + 14, "MIDDLE EAST", 2, RED)
    c.hline(m + 16, my + 40, colw - 32, INK, 2)
    lines = wrap_text("DRONES HIT KUWAIT SITE; 2 ITALIANS KILLED", 3, colw - 32)
    yy = my + 54
    for ln in lines:
        c.text(m + 16, yy, ln, 3, INK)
        yy += 3 * 8
    yy += 6
    body = ("Kuwait says Iranian drones hit a vital military site. "
            "Iran denies any role. Two more people hurt.")
    for ln in wrap_text(body, 2, colw - 32):
        c.text(m + 16, yy, ln, 2, INK)
        yy += 22
    draw_drone(c, m + colw - 128, my + mh - 56, 1)
    # right: Ukraine
    rx = m + colw + 16
    c.rect(rx, my, colw, mh, PAPER)
    c.rect(rx, my, colw, mh, INK)
    c.rect(rx + 2, my + 2, colw - 4, mh - 4, PAPER)
    c.text(rx + 16, my + 14, "UKRAINE", 2, RED)
    c.hline(rx + 16, my + 40, colw - 32, INK, 2)
    # blue-over-yellow flag bars
    c.rect(rx + colw - 96, my + 14, 80, 10, BLUE)
    c.rect(rx + colw - 96, my + 24, 80, 10, GOLD)
    lines = wrap_text("ZELENSKY WARNS OF NEW MASS RUSSIAN STRIKE", 3, colw - 32)
    yy = my + 54
    for ln in lines:
        c.text(rx + 16, yy, ln, 3, INK)
        yy += 3 * 8
    yy += 6
    body = ("Kyiv says Russia is readying a big attack on energy sites. "
            "Trump says he pressed Putin to pull back and hopes for a deal soon.")
    for ln in wrap_text(body, 2, colw - 32):
        c.text(rx + 16, yy, ln, 2, INK)
        yy += 22

    # --- AFP row --------------------------------------------------------
    ay, ah = 764, 110
    c.rect(m, ay, inner, ah, (232, 228, 218))
    c.rect(m, ay, inner, ah, INK)
    c.rect(m + 2, ay + 2, inner - 4, ah - 4, (232, 228, 218))
    draw_warning_triangle(c, m + 22, ay + 30, 3)
    c.text(m + 96, ay + 16, "MEDIA - FRANCE", 2, RED)
    c.text(m + 96, ay + 44, "CYBERATTACK HITS NEWS AGENCY AFP", 3, INK)
    c.text(m + 96, ay + 76,
           "Its AFP Forum platform is offline after an overnight intrusion.",
           2, INK)

    # --- in brief -------------------------------------------------------
    by = 890
    c.text(m, by, "IN BRIEF", 2, RED)
    c.hline(m + 118, by + 8, inner - 118, INK, 2)
    briefs = [
        "EU leaders split over a 45bn euro loan for Ukraine.",
        "Kyiv hit by missiles overnight; 7 people hurt.",
        "US envoy: Putin agreed not to use nuclear arms.",
    ]
    yy = by + 28
    for b in briefs:
        c.disc(m + 8, yy + 6, 4, RED)
        c.text(m + 24, yy, b, 2, INK)
        yy += 24
    c.hline(m, 996, inner, INK, 4)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = draw_front_page()
    data = encode_png(canvas)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
