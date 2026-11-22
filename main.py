#!/usr/bin/env python3
"""THE WORLD - Sunday 22 November 2026.

Draws a one-page world-news front page (1024x1024 PNG) summing up the
news of Sunday 22 November 2026, and writes it to /output/entry.png.

Python 3.13 standard library only. No network, no files read, fully
deterministic: the same bytes on every run.

Stories (22 Nov 2026):
  HERO     Gulf war widens - IRGC says 2 US drones down over Hormuz/Qeshm,
           tanker hit off Oman, Hormuz traffic ~65% below pre-war,
           third US carrier arrives.
  UKRAINE  Russia's biggest air attack: 400 drones, 110 missiles;
           debris falls in Poland.
  COP31    Fossil-fuel row deadlocks climate talks.
  PERU     Magnitude 6.9 quake shakes the Andes.
  SHENZHEN Trump, Xi and Putin meet at the APEC summit.
  MEXICO   Cartel boss 'El Chapo Isidro' seized; 11 dead in Sinaloa.
  FOOTER   Oil down more than 3%; Bolsonaro in ICU.
"""

import math
import os
import struct
import zlib
from binascii import crc32

W = 1024
H = 1024

# ---------------------------------------------------------------- font 5x7
# Each glyph is 7 rows of 5 bits, written by hand. All text is rendered
# in capitals from this one font, scaled by an integer factor.

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
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ";": ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
}


def text_width(s, text):
    """Width in pixels of text rendered at integer scale s."""
    if not text:
        return 0
    return len(text) * 6 * s - s


def wrap_text(text, s, maxw):
    """Greedy word wrap; returns a list of lines fitting maxw pixels."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(s, trial) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur or not lines:
            lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
def _lerp(a, b, t):
    return int(a + (b - a) * t + 0.5)


def _mix(c1, c2, t):
    return (_lerp(c1[0], c2[0], t), _lerp(c1[1], c2[1], t), _lerp(c1[2], c2[2], t))


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.buf[i] = c[0]
                self.buf[i + 1] = c[1]
                self.buf[i + 2] = c[2]
                i += 3

    def vgrad(self, x, y, w, h, c1, c2):
        for yy in range(h):
            t = yy / max(1, h - 1)
            self.rect(x, y + yy, w, 1, _mix(c1, c2, t))

    def hgrad(self, x, y, w, h, c1, c2):
        for xx in range(w):
            t = xx / max(1, w - 1)
            self.rect(x + xx, y, 1, h, _mix(c1, c2, t))

    def frame(self, x, y, w, h, c, t=3):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.px(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=3):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, cy + dy, t, 1, c)
            self.rect(cx + dx - t + 1, cy + dy, t, 1, c)
        for dx in range(-r, r + 1):
            dy = int(math.sqrt(max(0, r * r - dx * dx)))
            self.rect(cx + dx, cy - dy, 1, t, c)
            self.rect(cx + dx, cy + dy - t + 1, 1, t, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    def star(self, cx, cy, r, c):
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((cx + int(rr * math.cos(ang)), cy + int(rr * math.sin(ang))))
        self.poly(pts, c)

    def burst(self, cx, cy, r, c_core, c_mid, c_tip):
        """Explosion starburst: radial spikes + hot core."""
        for k in range(14):
            ang = k * math.pi / 7 + 0.22
            ln = r if k % 2 == 0 else int(r * 0.55)
            x1 = cx + int(ln * math.cos(ang))
            y1 = cy + int(ln * math.sin(ang))
            self.line(cx, cy, x1, y1, c_tip, 2)
        for k in range(8):
            ang = k * math.pi / 4 + 0.5
            ln = int(r * 0.7)
            self.line(cx, cy, cx + int(ln * math.cos(ang)),
                      cy + int(ln * math.sin(ang)), c_mid, 2)
        self.disc(cx, cy, max(3, r // 3), c_core)
        self.disc(cx, cy, max(2, r // 6), (255, 246, 200))

    def text(self, x, y, s, c, txt, align="l"):
        txt = txt.upper()
        w = text_width(s, txt)
        if align == "c":
            x -= w // 2
        elif align == "r":
            x -= w
        cx = x
        for ch in txt:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * s, y + row * s, s, s, c)
            cx += 6 * s
        return w

    def text_3d(self, x, y, s, txt, face, shades):
        """Layered offset copies (dark to light) + bright face: 3D title."""
        for (dx, dy), col in shades:
            self.text(x + dx, y + dy, s, col, txt)
        self.text(x, y, s, face, txt)


# ------------------------------------------------------------------- png
def encode_png(c):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += c.buf[y * stride:(y + 1) * stride]
    data = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload +
                struct.pack(">I", crc32(tag + payload) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", data) + chunk(b"IEND", b""))


# ------------------------------------------------------- deterministic rng
_RNG_STATE = [20261122]


def rnd(n):
    """Deterministic LCG, same sequence on every run."""
    _RNG_STATE[0] = (_RNG_STATE[0] * 1103515245 + 12345) & 0x7FFFFFFF
    return _RNG_STATE[0] % n

# ---------------------------------------------------------------- palette
NAVY = (16, 31, 60)
NAVY_DK = (10, 20, 42)
CREAM = (243, 233, 210)
PAPER = (250, 247, 238)
GOLD = (217, 169, 59)
GOLD_LT = (240, 200, 100)
INK = (24, 24, 28)
WHITE = (255, 255, 255)
RED = (178, 34, 34)
RED_DK = (122, 20, 20)
TEAL = (14, 110, 105)
ORANGE = (224, 123, 46)
AMBER = (242, 169, 80)
DUSK1 = (43, 30, 74)
DUSK2 = (146, 62, 52)
SEA1 = (13, 59, 67)
SEA2 = (7, 34, 43)
SMOKE = (96, 92, 88)
SMOKE_LT = (150, 142, 132)


def skyline(c, x, y, w, base, heights, win_c):
    """Black city silhouette with lit windows, sitting on base line."""
    bx = x
    i = 0
    while bx < x + w - 8:
        bw = 18 + rnd(30)
        bh = heights[i % len(heights)]
        c.rect(bx, base - bh, bw, bh, (12, 12, 20))
        if bh > 26:
            c.disc(bx + bw // 2, base - bh - 8, 7, (12, 12, 20))
        for wy in range(base - bh + 8, base - 6, 14):
            for wx in range(bx + 5, bx + bw - 4, 11):
                if rnd(3) == 0:
                    c.rect(wx, wy, 3, 4, win_c)
        bx += bw + 4
        i += 1


def windows(c, x, y, w, h, col):
    for wy in range(y + 6, y + h - 4, 12):
        for wx in range(x + 6, x + w - 5, 10):
            if rnd(3) == 0:
                c.rect(wx, wy, 3, 4, col)


def smoke_column(c, x, y, h, r0):
    """Rising smoke: stacked discs, widening and paling with height."""
    steps = 7
    for i in range(steps):
        t = i / (steps - 1)
        yy = y - int(h * t)
        rr = int(r0 * (1 + t * 1.6))
        col = _mix((70, 66, 62), SMOKE_LT, t)
        c.disc(x + (rnd(7) - 3), yy, rr, col)


def palm(c, x, y, s, col):
    """Small palm silhouette, base at (x, y), height ~ s."""
    c.line(x, y, x + 2, y - s, col, 2)
    for k in range(5):
        ang = -math.pi * (0.15 + 0.17 * k)
        x1 = x + 2 + int((s * 0.55) * math.cos(ang))
        y1 = y - s + int((s * 0.4) * math.sin(ang)) + 3
        c.line(x + 2, y - s, x1, y1, col, 2)
    c.disc(x + 1, y - s - 2, 3, col)


# -------------------------------------------------------------------- hero
def draw_hero(c):
    x, y, w, h = 8, 116, 1008, 244
    # Dusk sky over the Strait: violet down to burning amber.
    c.vgrad(x, y, w, 150, DUSK1, (196, 96, 48))
    c.vgrad(x, y + 150, w, 30, (196, 96, 48), AMBER)
    # Low sun, half-veiled by smoke.
    c.disc(x + 872, y + 128, 26, (255, 214, 130))
    c.disc(x + 872, y + 128, 20, (255, 232, 170))
    # Distant carrier silhouette on the horizon.
    c.rect(x + 700, y + 168, 150, 8, (20, 16, 26))
    c.rect(x + 742, y + 150, 10, 20, (20, 16, 26))
    c.rect(x + 780, y + 156, 34, 14, (20, 16, 26))
    # Sea.
    c.vgrad(x, y + 180, w, 64, SEA1, SEA2)
    for wy in range(y + 186, y + 240, 9):
        c.line(x + 12 + rnd(40), wy, x + w - 12 - rnd(40), wy,
               (52, 110, 118), 1)
    # Tanker silhouette, bow to the right, funnel smoking.
    c.rect(x + 180, y + 196, 380, 26, (10, 10, 14))
    c.rect(x + 196, y + 178, 46, 18, (10, 10, 14))
    c.rect(x + 300, y + 182, 60, 14, (10, 10, 14))
    c.rect(x + 420, y + 172, 18, 24, (10, 10, 14))
    c.rect(x + 520, y + 196, 40, 10, (10, 10, 14))
    windows(c, x + 196, y + 178, 46, 18, GOLD_LT)
    smoke_column(c, x + 429, y + 168, 84, 7)
    # Two drones in the sky, one going down in flames.
    c.line(x + 120, y + 40, x + 210, y + 96, (230, 220, 190), 2)
    c.disc(x + 210, y + 96, 4, (255, 240, 200))
    c.rect(x + 200, y + 88, 20, 6, (30, 28, 26))
    c.line(x + 640, y + 30, x + 600, y + 88, (230, 220, 190), 2)
    c.rect(x + 590, y + 82, 20, 6, (30, 28, 26))
    c.burst(x + 596, y + 104, 16, (255, 180, 60), (255, 120, 30), (255, 90, 20))
    # Explosion on the tanker deck and a fireball off Oman.
    c.burst(x + 540, y + 192, 20, (255, 190, 70), (255, 130, 40), (255, 100, 25))
    c.burst(x + 660, y + 210, 13, (255, 180, 60), (255, 120, 30), (255, 90, 20))
    smoke_column(c, x + 664, y + 204, 60, 6)
    # Shoreline strip with palms along the bottom of the picture.
    c.rect(x, y + 224, w, 20, (8, 26, 30))
    for px in (60, 250, 470, 690, 900, 985):
        palm(c, x + px, y + 242, 18, (4, 14, 16))
    # Kicker chip, top left.
    c.rect(x + 12, y + 12, 196, 32, RED)
    c.text(x + 24, y + 20, 2, WHITE, "WAR - THE GULF")
    # Star + pull line chip, top right.
    c.rect(x + 668, y + 12, 328, 32, NAVY_DK)
    c.frame(x + 668, y + 12, 328, 32, GOLD, 2)
    c.star(x + 692, y + 28, 11, GOLD)
    c.text(x + 712, y + 20, 2, GOLD_LT, '"WAR AT THE STRAIT"')
    # Location pill, bottom left above the palms.
    c.rect(x + 12, y + 168, 228, 28, NAVY_DK)
    c.frame(x + 12, y + 168, 228, 28, GOLD, 2)
    c.disc(x + 28, y + 182, 4, GOLD)
    c.text(x + 40, y + 176, 2, WHITE, "STRAIT OF HORMUZ")


# ------------------------------------------------------------------ panels
def panel_shell(c, x, y, w, h):
    c.rect(x, y, w, h, PAPER)
    c.frame(x, y, w, h, NAVY, 3)


def kicker_chip(c, x, y, txt, col):
    w = text_width(2, txt) + 20
    c.rect(x, y, w, 26, col)
    c.text(x + 10, y + 6, 2, WHITE, txt)
    return w


def panel_text(c, x, y, w, headline, body, head_c=INK):
    """Headline (up to 2 lines, 35px) + body (up to 2 lines, 14px)."""
    lines = wrap_text(headline, 5, w)
    yy = y
    for ln in lines[:2]:
        c.text(x, yy, 5, head_c, ln)
        yy += 35
    blines = wrap_text(body, 2, w)
    yy += 2
    for ln in blines[:2]:
        c.text(x, yy, 2, (74, 74, 78), ln)
        yy += 15


def draw_ukraine(c, x, y, w, h):
    panel_shell(c, x, y, w, h)
    ih = 96
    c.vgrad(x + 3, y + 3, w - 6, ih, (44, 34, 78), (198, 102, 52))
    skyline(c, x + 3, y + 3, w - 6, y + 3 + ih, [34, 52, 40, 60, 46], GOLD_LT)
    for (tx, ty, hx, hy) in ((40, 44, 90, 80), (170, 40, 200, 76), (260, 48, 285, 74)):
        c.line(x + tx, y + ty, x + hx, y + hy, (240, 228, 190), 2)
        c.disc(x + hx, y + hy, 4, (255, 244, 210))
    c.burst(x + 120, y + 80, 14, (255, 180, 60), (255, 120, 30), (255, 90, 20))
    kicker_chip(c, x + 12, y + 12, "WAR - UKRAINE - 22 NOV", RED)
    panel_text(c, x + 12, y + 3 + ih + 8, w - 24,
               "BIGGEST AIR RAID",
               "400 DRONES, 110 MISSILES - DEBRIS FALLS IN POLAND.")


def draw_cop31(c, x, y, w, h):
    panel_shell(c, x, y, w, h)
    ih = 96
    c.vgrad(x + 3, y + 3, w - 6, ih, (10, 84, 78), (36, 140, 110))
    # Globe: warm oceans, green land, latitude lines.
    gx, gy, gr = x + 95, y + 68, 30
    c.disc(gx, gy, gr, (28, 110, 150))
    c.disc(gx - 9, gy - 7, 9, (74, 160, 90))
    c.disc(gx + 11, gy + 10, 10, (74, 160, 90))
    c.disc(gx + 7, gy - 13, 6, (74, 160, 90))
    c.ring(gx, gy, gr, (220, 235, 220), 2)
    c.line(gx - gr, gy, gx + gr, gy, (220, 235, 220), 1)
    c.line(gx - 24, gy - 17, gx + 24, gy - 17, (220, 235, 220), 1)
    c.line(gx - 24, gy + 17, gx + 24, gy + 17, (220, 235, 220), 1)
    # Deadlock: two arrows pushing at each other across the globe.
    c.line(x + 190, y + 44, x + 250, y + 44, GOLD_LT, 3)
    c.poly([(x + 250, y + 36), (x + 250, y + 52), (x + 264, y + 44)], GOLD_LT)
    c.line(x + 300, y + 74, x + 240, y + 74, GOLD_LT, 3)
    c.poly([(x + 240, y + 66), (x + 240, y + 82), (x + 226, y + 74)], GOLD_LT)
    # Podium silhouettes at the foot of the picture.
    for px in (170, 220, 270):
        c.rect(x + px, y + 78, 26, 21, (10, 20, 26))
    kicker_chip(c, x + 12, y + 12, "CLIMATE - COP31 - 22 NOV", TEAL)
    panel_text(c, x + 12, y + 3 + ih + 8, w - 24,
               "COP31 DEADLOCK",
               "FOSSIL-FUEL ROW DEADLOCKS COP31 NEGOTIATIONS.")


def draw_peru(c, x, y, w, h):
    panel_shell(c, x, y, w, h)
    ih = 96
    c.vgrad(x + 3, y + 3, w - 6, ih, (122, 74, 44), (232, 170, 96))
    c.disc(x + 300, y + 28, 16, (255, 226, 160))
    # Andes: three peaks, snow caps, quake cracks.
    c.poly([(x + 10, y + 99), (x + 90, y + 44), (x + 170, y + 99)], (74, 46, 30))
    c.poly([(x + 90, y + 44), (x + 108, y + 62), (x + 72, y + 62)], WHITE)
    c.poly([(x + 130, y + 99), (x + 205, y + 56), (x + 285, y + 99)], (58, 36, 24))
    c.poly([(x + 205, y + 56), (x + 220, y + 72), (x + 190, y + 72)], WHITE)
    c.poly([(x + 240, y + 99), (x + 295, y + 68), (x + 330, y + 99)], (88, 56, 36))
    for (cx0, cy0) in ((96, 64), (200, 76), (292, 84)):
        c.line(x + cx0, y + cy0, x + cx0 + 10, y + cy0 + 12, (255, 120, 40), 2)
        c.line(x + cx0 + 10, y + cy0 + 12, x + cx0 - 2, y + cy0 + 24, (255, 120, 40), 2)
    c.disc(x + 60, y + 88, 10, (210, 180, 140))
    c.disc(x + 84, y + 92, 8, (210, 180, 140))
    kicker_chip(c, x + 12, y + 12, "QUAKE - PERU - 22 NOV", (146, 84, 32))
    panel_text(c, x + 12, y + 3 + ih + 8, w - 24,
               "6.9 QUAKE HITS ANDES",
               "MAGNITUDE 6.9 TREMOR SHAKES THE ANDES.")


def draw_shenzhen(c, x, y, w, h):
    panel_shell(c, x, y, w, h)
    ih = 108
    c.vgrad(x + 3, y + 3, w - 6, ih, (122, 26, 26), (196, 84, 44))
    skyline(c, x + 3, y + 3, w - 6, y + 3 + ih, [26, 40, 32], GOLD_LT)
    # Three flags on poles: United States, China, Russia.
    fy = y + 44
    poles = (x + 60, x + 210, x + 360)
    for px in poles:
        c.line(px, fy, px, fy + 62, GOLD_LT, 2)
    # United States: stripes + blue canton.
    fx = poles[0] + 3
    for i in range(6):
        c.rect(fx, fy + i * 8, 84, 8, WHITE if i % 2 == 0 else RED)
    c.rect(fx, fy, 36, 24, (30, 60, 140))
    # China: red field, gold star.
    fx = poles[1] + 3
    c.rect(fx, fy, 84, 48, (222, 32, 32))
    c.star(fx + 20, fy + 16, 10, GOLD)
    # Russia: white, blue, red bands.
    fx = poles[2] + 3
    c.rect(fx, fy, 84, 16, WHITE)
    c.rect(fx, fy + 16, 84, 16, (30, 80, 180))
    c.rect(fx, fy + 32, 84, 16, RED)
    kicker_chip(c, x + 12, y + 12, "DIPLOMACY - SHENZHEN - 22 NOV", (176, 92, 20))
    panel_text(c, x + 12, y + 3 + ih + 8, w - 24,
               "THREE LEADERS, ONE TABLE",
               "TRUMP, XI AND PUTIN MEET AT APEC SUMMIT.")


def draw_mexico(c, x, y, w, h):
    panel_shell(c, x, y, w, h)
    ih = 108
    c.vgrad(x + 3, y + 3, w - 6, ih, (150, 84, 44), (232, 158, 88))
    c.disc(x + 470, y + 28, 16, (255, 226, 160))
    # Desert mesas and cacti.
    c.poly([(x + 10, y + 111), (x + 60, y + 62), (x + 120, y + 62),
            (x + 170, y + 111)], (96, 52, 28))
    c.poly([(x + 180, y + 111), (x + 230, y + 74), (x + 300, y + 74),
            (x + 350, y + 111)], (78, 42, 24))
    c.poly([(x + 340, y + 111), (x + 400, y + 82), (x + 470, y + 82),
            (x + 500, y + 111)], (96, 52, 28))
    for (cx0, ch) in ((40, 34), (330, 28), (455, 30)):
        c.line(x + cx0, y + 108, x + cx0, y + 108 - ch, (52, 74, 40), 4)
        c.line(x + cx0, y + 108 - ch + 10, x + cx0 - 10, y + 108 - ch + 10,
               (52, 74, 40), 3)
        c.line(x + cx0 - 10, y + 108 - ch + 10, x + cx0 - 10,
               y + 108 - ch + 20, (52, 74, 40), 3)
    # Helicopter with searchlight over the desert.
    hx, hy = x + 350, y + 34
    c.line(hx - 34, hy, hx + 34, hy, (24, 20, 20), 3)
    c.line(hx, hy, hx, hy + 6, (24, 20, 20), 2)
    c.disc(hx, hy + 10, 9, (24, 20, 20))
    c.line(hx + 8, hy + 8, hx + 44, hy + 2, (24, 20, 20), 2)
    c.line(hx - 6, hy + 4, hx - 26, hy + 22, (24, 20, 20), 2)
    c.poly([(hx - 4, hy + 16), (hx + 4, hy + 16), (hx + 26, hy + 58),
            (hx - 18, hy + 58)], (255, 240, 180))
    kicker_chip(c, x + 12, y + 12, "CARTEL - MEXICO - 22 NOV", (120, 24, 24))
    panel_text(c, x + 12, y + 3 + ih + 8, w - 24,
               "'EL CHAPO ISIDRO' HELD",
               "CARTEL BOSS SEIZED - 11 DEAD IN SINALOA VIOLENCE.")

# ------------------------------------------------------------------ layout
def draw_masthead(c):
    c.rect(0, 0, W, 108, NAVY)
    c.text_3d(24, 14, 10, "THE WORLD", (245, 238, 220),
              [((4, 4), (58, 44, 16)), ((3, 3), (120, 90, 30)),
               ((2, 2), (170, 130, 45)), ((1, 1), (210, 165, 70))])
    c.text(1000, 44, 3, GOLD, "SUNDAY, 22 NOVEMBER 2026", align="r")
    c.text(24, 90, 2, GOLD_LT, "WORLD NEWS IN ONE PAGE")
    c.rect(0, 108, W, 4, GOLD)


def draw_headline_band(c):
    c.rect(8, 360, 1008, 124, NAVY)
    c.rect(8, 360, 1008, 3, GOLD)
    c.text(24, 370, 8, WHITE, "GULF WAR WIDENS")
    c.text(24, 434, 3, GOLD_LT,
           "IRGC: 2 U.S. DRONES DOWN - TANKER HIT OFF OMAN")
    c.text(24, 460, 3, GOLD_LT,
           "HORMUZ TRAFFIC DOWN 65% - 3RD CARRIER ARRIVES")


def draw_seal(c):
    cx, cy, r = 935, 468, 32
    c.disc(cx, cy, r, GOLD)
    c.disc(cx, cy, r - 4, NAVY)
    c.ring(cx, cy, r - 4, GOLD, 2)
    c.star(cx, cy - 7, 10, GOLD)
    c.text(cx, cy + 8, 1, GOLD_LT, "NOV 22", align="c")


def draw_footer(c):
    c.rect(0, 948, W, 76, NAVY)
    c.rect(0, 948, W, 3, GOLD)
    c.text(24, 972, 3, WHITE, "ALSO: OIL DOWN 3% - BOLSONARO IN ICU")
    c.text(1000, 956, 2, GOLD, "22 NOV 2026", align="r")
    # Barcode, bottom right.
    widths = [3, 1, 2, 1, 1, 3, 2, 2, 1, 1, 3, 1, 2, 3, 1, 1, 2, 1, 3, 2,
              1, 2, 1, 3, 1, 1, 2, 2, 1, 3, 1, 2, 1, 1, 3, 2, 1, 1, 2, 3]
    bx = 868
    for i, wd in enumerate(widths):
        if i % 2 == 0:
            c.rect(bx, 978, wd, 30, WHITE)
        bx += wd + 1


def draw_page(c):
    c.rect(0, 0, W, H, CREAM)
    draw_masthead(c)
    draw_hero(c)
    draw_headline_band(c)
    # Row 1: three panels.
    draw_ukraine(c, 8, 492, 330, 216)
    draw_cop31(c, 347, 492, 330, 216)
    draw_peru(c, 686, 492, 330, 216)
    # Row 2: two wide panels.
    draw_shenzhen(c, 8, 716, 500, 224)
    draw_mexico(c, 516, 716, 500, 224)
    draw_seal(c)
    draw_footer(c)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    try:
        os.chmod(outdir, 0o755)
    except OSError:
        pass
    _RNG_STATE[0] = 20261122
    c = Canvas(W, H, CREAM)
    draw_page(c)
    data = encode_png(c)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o644)


if __name__ == "__main__":
    main()
