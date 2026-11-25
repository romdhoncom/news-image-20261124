#!/usr/bin/env python3
"""news-image-20261124: Tuesday 24 November 2026 in one image.

Pure Python standard library only: own raster canvas, own 5x7 bitmap
font, own PNG encoder. No network, no randomness, no timestamps in the
output, so two runs write byte-identical files.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 247, 238)
INK = (22, 22, 22)
SOFT_INK = (70, 70, 66)
RED = (178, 34, 34)
DARK_RED = (122, 20, 20)
BLUE = (31, 58, 95)
SEA = (191, 217, 232)
LAND = (216, 200, 162)
LAND_DARK = (190, 172, 130)
GOLD = (201, 162, 39)
GREY = (120, 120, 116)
LIGHT_GREY = (228, 226, 220)
WHITE = (255, 255, 255)
SKY = (205, 224, 238)
DUSK = (238, 205, 160)
GREEN = (46, 110, 62)
ORANGE = (224, 122, 40)
YELLOW = (240, 200, 60)

# ------------------------------------------------------------------- font
# Classic 5x7 bitmap font. Each glyph: 5 columns, one byte per column,
# bit 0 is the top row. Space is one blank column wide in the renderer.
FONT = {
    ' ': (0x00, 0x00, 0x00, 0x00, 0x00),
    '!': (0x00, 0x00, 0x5F, 0x00, 0x00),
    '"': (0x00, 0x07, 0x00, 0x07, 0x00),
    '#': (0x14, 0x7F, 0x14, 0x7F, 0x14),
    '$': (0x24, 0x2A, 0x7F, 0x2A, 0x12),
    '%': (0x23, 0x13, 0x08, 0x64, 0x62),
    '&': (0x36, 0x49, 0x55, 0x22, 0x50),
    "'": (0x00, 0x05, 0x03, 0x00, 0x00),
    '(': (0x00, 0x1C, 0x22, 0x41, 0x00),
    ')': (0x00, 0x41, 0x22, 0x1C, 0x00),
    '*': (0x14, 0x08, 0x3E, 0x08, 0x14),
    '+': (0x08, 0x08, 0x3E, 0x08, 0x08),
    ',': (0x00, 0x50, 0x30, 0x00, 0x00),
    '-': (0x08, 0x08, 0x08, 0x08, 0x08),
    '.': (0x00, 0x60, 0x60, 0x00, 0x00),
    '/': (0x20, 0x10, 0x08, 0x04, 0x02),
    '0': (0x3E, 0x51, 0x49, 0x45, 0x3E),
    '1': (0x00, 0x42, 0x7F, 0x40, 0x00),
    '2': (0x42, 0x61, 0x51, 0x49, 0x46),
    '3': (0x21, 0x41, 0x45, 0x4B, 0x31),
    '4': (0x18, 0x14, 0x12, 0x7F, 0x10),
    '5': (0x27, 0x45, 0x45, 0x45, 0x39),
    '6': (0x3C, 0x4A, 0x49, 0x49, 0x30),
    '7': (0x01, 0x71, 0x09, 0x05, 0x03),
    '8': (0x36, 0x49, 0x49, 0x49, 0x36),
    '9': (0x06, 0x49, 0x49, 0x29, 0x1E),
    ':': (0x00, 0x36, 0x36, 0x00, 0x00),
    ';': (0x00, 0x56, 0x36, 0x00, 0x00),
    '<': (0x08, 0x14, 0x22, 0x41, 0x00),
    '=': (0x14, 0x14, 0x14, 0x14, 0x14),
    '>': (0x00, 0x41, 0x22, 0x14, 0x08),
    '?': (0x02, 0x01, 0x51, 0x09, 0x06),
    '@': (0x32, 0x49, 0x79, 0x41, 0x3E),
    'A': (0x7E, 0x11, 0x11, 0x11, 0x7E),
    'B': (0x7F, 0x49, 0x49, 0x49, 0x36),
    'C': (0x3E, 0x41, 0x41, 0x41, 0x22),
    'D': (0x7F, 0x41, 0x41, 0x22, 0x1C),
    'E': (0x7F, 0x49, 0x49, 0x49, 0x41),
    'F': (0x7F, 0x09, 0x09, 0x09, 0x01),
    'G': (0x3E, 0x41, 0x49, 0x49, 0x7A),
    'H': (0x7F, 0x08, 0x08, 0x08, 0x7F),
    'I': (0x00, 0x41, 0x7F, 0x41, 0x00),
    'J': (0x20, 0x41, 0x41, 0x3F, 0x01),
    'K': (0x7F, 0x08, 0x14, 0x22, 0x41),
    'L': (0x7F, 0x40, 0x40, 0x40, 0x40),
    'M': (0x7F, 0x02, 0x0C, 0x02, 0x7F),
    'N': (0x7F, 0x04, 0x08, 0x10, 0x7F),
    'O': (0x3E, 0x41, 0x41, 0x41, 0x3E),
    'P': (0x7F, 0x09, 0x09, 0x09, 0x06),
    'Q': (0x3E, 0x41, 0x51, 0x21, 0x5E),
    'R': (0x7F, 0x09, 0x19, 0x29, 0x46),
    'S': (0x46, 0x49, 0x49, 0x49, 0x31),
    'T': (0x01, 0x01, 0x7F, 0x01, 0x01),
    'U': (0x3F, 0x40, 0x40, 0x40, 0x3F),
    'V': (0x1F, 0x20, 0x40, 0x20, 0x1F),
    'W': (0x3F, 0x40, 0x38, 0x40, 0x3F),
    'X': (0x63, 0x14, 0x08, 0x14, 0x63),
    'Y': (0x07, 0x08, 0x70, 0x08, 0x07),
    'Z': (0x61, 0x51, 0x49, 0x45, 0x43),
    '[': (0x00, 0x7F, 0x41, 0x41, 0x00),
    '\\': (0x02, 0x04, 0x08, 0x10, 0x20),
    ']': (0x00, 0x41, 0x41, 0x7F, 0x00),
    '^': (0x04, 0x02, 0x01, 0x02, 0x04),
    '_': (0x40, 0x40, 0x40, 0x40, 0x40),
    '`': (0x00, 0x01, 0x02, 0x04, 0x00),
    'a': (0x20, 0x54, 0x54, 0x54, 0x78),
    'b': (0x7F, 0x48, 0x44, 0x44, 0x38),
    'c': (0x38, 0x44, 0x44, 0x44, 0x20),
    'd': (0x38, 0x44, 0x44, 0x48, 0x7F),
    'e': (0x38, 0x54, 0x54, 0x54, 0x18),
    'f': (0x08, 0x7E, 0x09, 0x01, 0x02),
    'g': (0x0C, 0x52, 0x52, 0x52, 0x3E),
    'h': (0x7F, 0x08, 0x04, 0x04, 0x78),
    'i': (0x00, 0x44, 0x7D, 0x40, 0x00),
    'j': (0x20, 0x40, 0x44, 0x3D, 0x00),
    'k': (0x7F, 0x10, 0x28, 0x44, 0x00),
    'l': (0x00, 0x41, 0x7F, 0x40, 0x00),
    'm': (0x7C, 0x04, 0x18, 0x04, 0x78),
    'n': (0x7C, 0x08, 0x04, 0x04, 0x78),
    'o': (0x38, 0x44, 0x44, 0x44, 0x38),
    'p': (0x7C, 0x14, 0x14, 0x14, 0x08),
    'q': (0x08, 0x14, 0x14, 0x18, 0x7C),
    'r': (0x7C, 0x08, 0x04, 0x04, 0x08),
    's': (0x48, 0x54, 0x54, 0x54, 0x20),
    't': (0x04, 0x3F, 0x44, 0x40, 0x20),
    'u': (0x3C, 0x40, 0x40, 0x20, 0x7C),
    'v': (0x1C, 0x20, 0x40, 0x20, 0x1C),
    'w': (0x3C, 0x40, 0x30, 0x40, 0x3C),
    'x': (0x44, 0x28, 0x10, 0x28, 0x44),
    'y': (0x0C, 0x50, 0x50, 0x50, 0x3C),
    'z': (0x44, 0x64, 0x54, 0x4C, 0x44),
    '{': (0x00, 0x08, 0x36, 0x41, 0x00),
    '|': (0x00, 0x00, 0x7F, 0x00, 0x00),
    '}': (0x00, 0x41, 0x36, 0x08, 0x00),
    '~': (0x08, 0x04, 0x08, 0x10, 0x08),
    '•': (0x00, 0x0E, 0x0E, 0x0E, 0x00),
}

# Normalise fancy punctuation to the ASCII glyphs the font carries.
_CLEAN = {
    '’': "'", '‘': "'", '“': '"', '”': '"',
    '–': '-', '—': '-', '…': '.', '·': '•', '×': 'x',
}


def clean(text):
    return ''.join(_CLEAN.get(ch, ch) for ch in text)


def text_width(text, scale):
    text = clean(text)
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    text = clean(text)
    words = text.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single word too wide: hard-split it.
            while text_width(word, scale) > max_width:
                cut = max_width // (6 * scale)
                lines.append(word[:cut])
                word = word[cut:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i], self.pix[i + 1], self.pix[i + 2] = color

    def hline(self, x0, x1, y, color):
        if y < 0 or y >= self.h:
            return
        x0 = max(0, x0)
        x1 = min(self.w - 1, x1)
        for x in range(x0, x1 + 1):
            i = (y * self.w + x) * 3
            self.pix[i], self.pix[i + 1], self.pix[i + 2] = color

    def rect(self, x, y, w, h, color):
        for yy in range(max(0, y), min(self.h, y + h)):
            self.hline(x, x + w - 1, yy, color)

    def frame(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def ring(self, cx, cy, r, color, t=1):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            dx2 = int(math.sqrt(max(0, (r - t) * (r - t) - dy * dy))) if abs(dy) < r - t + 1 else 0
            self.hline(cx - dx, cx - dx2, cy + dy, color)
            self.hline(cx + dx2, cx + dx, cy + dy, color)

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

    def poly(self, pts, color):
        """Scanline-filled polygon; pts is a list of (x, y)."""
        if len(pts) < 3:
            return
        min_y = max(0, min(y for _, y in pts))
        max_y = min(self.h - 1, max(y for _, y in pts))
        n = len(pts)
        for y in range(min_y, max_y + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(math.ceil(xs[i])), int(math.floor(xs[i + 1])), y, color)

    def char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch, FONT['?'])
        for col in range(5):
            bits = glyph[col]
            for row in range(7):
                if bits & (1 << row):
                    self.rect(x + col * scale, y + row * scale, scale, scale, color)

    def text(self, x, y, s, scale, color):
        s = clean(s)
        cx = x
        for ch in s:
            self.char(cx, y, ch, scale, color)
            cx += 6 * scale
        return cx

    def text_centered(self, cx, y, s, scale, color):
        w = text_width(s, scale)
        return self.text(cx - w // 2, y, s, scale, color)

    def text_block(self, x, y, s, scale, color, max_width, line_h=None):
        """Wrapped paragraph; returns the y just below the last line."""
        if line_h is None:
            line_h = 7 * scale + 3
        for line in wrap_text(s, max_width, scale):
            self.text(x, y, line, scale, color)
            y += line_h
        return y


# --------------------------------------------------------------------- png
def _chunk(tag, data):
    out = struct.pack('>I', len(data)) + tag + data
    return out + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path, canvas):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        start = y * canvas.w * 3
        raw += canvas.pix[start:start + canvas.w * 3]
    ihdr = struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr)
           + _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + _chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------ lead pictures
def burst(c, cx, cy, r, color, color2):
    """Explosion starburst: alternating long/short spikes."""
    for k in range(12):
        ang = k * math.pi / 6
        r2 = r if k % 2 == 0 else r // 2
        x2 = int(cx + r2 * math.cos(ang))
        y2 = int(cy + r2 * math.sin(ang))
        c.line(cx, cy, x2, y2, color)
        c.line(cx, cy, x2, y2, color2)
    c.circle(cx, cy, r // 2, color2)
    c.circle(cx, cy, r // 4, WHITE)


def scene_huawei(c, x, y, w, h):
    """US courthouse: pediment, columns, steps, flag."""
    c.rect(x, y, w, h, (206, 216, 226))
    c.rect(x, y + h - 26, w, 26, (150, 158, 168))
    # steps
    c.rect(x + 8, y + h - 34, w - 16, 8, (190, 196, 204))
    c.rect(x + 22, y + h - 42, w - 44, 8, (205, 210, 218))
    # building body
    c.rect(x + 30, y + 58, w - 60, h - 100, (232, 234, 236))
    # pediment
    c.poly([(x + 24, y + 58), (x + w // 2, y + 22), (x + w - 24, y + 58)], (226, 228, 230))
    c.circle(x + w // 2, y + 44, 7, (150, 40, 40))
    # columns
    for i in range(5):
        cx = x + 48 + i * ((w - 96) // 4)
        c.rect(cx - 6, y + 62, 12, h - 108, (248, 248, 246))
        c.rect(cx - 9, y + 58, 18, 6, (210, 212, 214))
        c.rect(cx - 9, y + h - 52, 18, 6, (210, 212, 214))
    # door
    c.rect(x + w // 2 - 14, y + h - 78, 28, 36, (60, 60, 66))
    # flag
    c.line(x + w // 2, y + 22, x + w // 2, y + 2, INK)
    c.poly([(x + w // 2, y + 2), (x + w // 2 + 22, y + 7), (x + w // 2, y + 12)], RED)
    # gavel stamp
    c.rect(x + w - 62, y + h - 58, 54, 20, RED)
    c.text(x + w - 57, y + h - 55, 'GUILTY', 1, WHITE)


def scene_hormuz(c, x, y, w, h):
    """Container ship in the strait, explosion above, mines in the water."""
    c.rect(x, y, w, h, SKY)
    c.circle(x + w - 18, y + 18, 10, (240, 210, 110))
    # sea
    c.rect(x, y + h - 40, w, 40, (52, 102, 148))
    c.rect(x, y + h - 40, w, 2, (120, 170, 210))
    # ship hull
    c.poly([(x + 8, y + h - 56), (x + w - 8, y + h - 56),
            (x + w - 22, y + h - 40), (x + 22, y + h - 40)], (40, 44, 50))
    # containers, sized to the box
    cols = [(178, 60, 50), (60, 120, 70), (210, 160, 50), (60, 90, 150)]
    cw = (w - 36) // 4
    for i in range(4):
        cx = x + 14 + i * cw
        c.rect(cx, y + h - 80, cw - 4, 22, cols[i % 4])
        c.rect(cx, y + h - 80, cw - 4, 2, (255, 255, 255))
    # bridge
    c.rect(x + w - 30, y + h - 96, 18, 38, (230, 230, 228))
    c.rect(x + w - 30, y + h - 96, 18, 5, (40, 60, 90))
    # explosion
    burst(c, x + w // 3, y + 34, 18, ORANGE, YELLOW)
    # mines
    for mx, my in [(x + 16, y + h - 18), (x + w - 20, y + h - 14),
                   (x + w // 2 + 24, y + h - 22)]:
        c.circle(mx, my, 5, (20, 20, 20))
        for ang in range(0, 360, 45):
            ex = int(mx + 8 * math.cos(math.radians(ang)))
            ey = int(my + 8 * math.sin(math.radians(ang)))
            c.line(mx, my, ex, ey, (20, 20, 20))


def scene_gaza(c, x, y, w, h):
    """City skyline at dusk, smoke plume, strike flash."""
    c.rect(x, y, w, h, DUSK)
    c.circle(x + 24, y + 22, 12, (240, 200, 120))
    # buildings
    heights = [62, 84, 70, 96, 58, 88, 74, 66]
    bx = x + 6
    for i, bh in enumerate(heights):
        bw = (w - 12) // len(heights)
        c.rect(bx, y + h - 30 - bh, bw - 3, bh, (52, 48, 52) if i % 2 else (68, 62, 66))
        # windows
        for wy in range(y + h - 30 - bh + 8, y + h - 34, 12):
            for wx in range(bx + 3, bx + bw - 6, 8):
                c.rect(wx, wy, 3, 4, (240, 200, 110))
        bx += bw
    # smoke plume
    for i, (sx, sy, sr) in enumerate([(0, 0, 16), (6, -18, 13), (-4, -34, 11), (4, -48, 9)]):
        c.circle(x + w // 2 + 30 + sx, y + 62 + sy, sr, (120, 116, 112))
    # strike flash
    burst(c, x + w // 2 + 30, y + 66, 20, ORANGE, YELLOW)
    # ground
    c.rect(x, y + h - 30, w, 30, (40, 38, 40))


def scene_sparta(c, x, y, w, h):
    """Cargo ship in the Gulf of Finland, drone above, blast on deck."""
    c.rect(x, y, w, h, (196, 214, 228))
    c.circle(x + 18, y + 16, 9, (240, 210, 110))
    # sea
    c.rect(x, y + h - 38, w, 38, (70, 110, 150))
    c.rect(x, y + h - 38, w, 2, (140, 180, 215))
    # hull
    c.poly([(x + 8, y + h - 54), (x + w - 8, y + h - 54),
            (x + w - 22, y + h - 38), (x + 22, y + h - 38)], (90, 90, 94))
    # containers, sized to the box
    cw = (w - 36) // 4
    for i in range(4):
        cx = x + 14 + i * cw
        c.rect(cx, y + h - 76, cw - 4, 20,
               (150, 60, 50) if i % 2 else (60, 100, 130))
    # blast on deck
    burst(c, x + w // 2, y + h - 82, 16, ORANGE, YELLOW)
    # drone
    dx, dy = x + w - 24, y + 26
    c.rect(dx - 12, dy - 2, 24, 5, (30, 30, 30))
    c.rect(dx - 2, dy - 7, 4, 14, (30, 30, 30))
    for rx in (dx - 15, dx + 15):
        c.line(rx - 7, dy - 8, rx + 7, dy - 8, (30, 30, 30))
        c.line(rx - 7, dy + 8, rx + 7, dy + 8, (30, 30, 30))
    c.line(dx, dy + 7, dx, dy + 20, (30, 30, 30))
    c.circle(dx, dy + 22, 3, RED)


def scene_riyadh(c, x, y, w, h):
    """PIF tower: tall tapering tower, skyline, smoke at the crown."""
    c.rect(x, y, w, h, (210, 222, 236))
    c.circle(x + w - 28, y + 22, 13, (240, 205, 110))
    # distant skyline
    for i, bh in enumerate([40, 56, 48, 64, 44]):
        bx = x + 8 + i * 26
        c.rect(bx, y + h - 24 - bh, 22, bh, (150, 158, 170))
    # PIF tower: tapering, slightly twisted silhouette
    tx = x + w // 2
    top = y + 8
    base = y + h - 24
    c.poly([(tx - 10, top), (tx + 10, top), (tx + 26, base), (tx - 26, base)],
           (52, 68, 96))
    # diagonal cladding lines
    for i in range(9):
        yy = top + 10 + i * ((base - top - 10) // 9)
        half = 10 + (yy - top) * 16 // (base - top)
        c.line(tx - half, yy, tx + half, yy + 6, (120, 140, 170))
    # lit windows band
    c.rect(tx - 14, top + 34, 28, 5, (240, 200, 110))
    # smoke at the crown
    for sx, sy, sr in [(0, -2, 10), (8, -12, 8), (-6, -20, 7)]:
        c.circle(tx + sx, top + sy, sr, (110, 106, 102))
    burst(c, tx, top + 2, 12, ORANGE, YELLOW)
    # ground
    c.rect(x, y + h - 24, w, 24, (60, 62, 66))


SCENES = {
    'huawei': scene_huawei,
    'hormuz': scene_hormuz,
    'gaza': scene_gaza,
    'sparta': scene_sparta,
    'riyadh': scene_riyadh,
}

# ---------------------------------------------------------------- world map
# Simplified continent outlines, (lon, lat) pairs, equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-80, 73), (-75, 72), (-70, 62), (-65, 60), (-60, 47), (-70, 42),
     (-75, 35), (-80, 32), (-85, 30), (-90, 21), (-95, 19), (-97, 16),
     (-92, 15), (-86, 13), (-83, 9), (-79, 9), (-85, 11), (-90, 14),
     (-95, 16), (-105, 20), (-110, 23), (-115, 29), (-120, 34), (-125, 40),
     (-125, 49), (-130, 55), (-135, 58), (-145, 60), (-155, 58), (-165, 60)],
    # Greenland
    [(-58, 64), (-52, 70), (-45, 76), (-30, 76), (-22, 70), (-25, 65),
     (-35, 60), (-45, 60), (-55, 60)],
    # South America
    [(-79, 9), (-72, 12), (-64, 11), (-60, 8), (-52, 5), (-50, 0),
     (-44, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-52, -33),
     (-58, -38), (-65, -41), (-68, -50), (-70, -54), (-73, -50), (-73, -40),
     (-72, -30), (-70, -20), (-77, -12), (-80, -5), (-81, 0)],
    # Africa
    [(-17, 15), (-15, 27), (-10, 31), (-5, 35), (0, 36), (10, 37),
     (11, 34), (20, 32), (30, 31), (32, 31), (35, 28), (34, 27),
     (37, 22), (40, 15), (43, 11), (48, 11), (51, 12), (44, 5),
     (42, 0), (40, -5), (36, -12), (32, -18), (30, -26), (26, -33),
     (20, -35), (17, -32), (15, -27), (12, -18), (9, -1), (9, 4),
     (4, 6), (-8, 5), (-13, 8)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-4, 49), (0, 50), (3, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (25, 65),
     (20, 66), (18, 69), (25, 71), (30, 70), (35, 68), (40, 68), (45, 66),
     (40, 64), (35, 62), (30, 60), (28, 58), (24, 57), (21, 54), (19, 54),
     (15, 54), (12, 55), (8, 54), (5, 53), (0, 51), (-2, 49), (-5, 48),
     (-8, 44)],
    # Asia
    [(30, 62), (40, 64), (50, 68), (60, 69), (70, 72), (80, 73), (90, 75),
     (100, 76), (110, 76), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 66), (170, 66), (178, 65), (170, 60), (162, 58), (158, 52),
     (150, 59), (142, 55), (140, 45), (135, 43), (130, 42), (127, 40),
     (126, 38), (122, 38), (120, 32), (122, 28), (118, 25), (110, 21),
     (108, 18), (105, 10), (103, 8), (100, 8), (98, 10), (95, 15),
     (92, 21), (88, 22), (85, 19), (80, 15), (77, 8), (75, 10),
     (72, 20), (68, 23), (66, 25), (62, 25), (58, 26), (56, 26),
     (52, 27), (50, 29), (48, 29), (44, 29), (40, 30), (38, 31),
     (36, 36), (35, 36), (33, 35), (30, 36), (28, 38), (27, 40),
     (28, 45), (30, 48), (30, 55), (30, 60)],
    # Australia
    [(114, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (137, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    # Sumatra
    [(95, 5), (98, 2), (100, 0), (103, -3), (105, -5), (104, -6), (100, -2),
     (97, 2)],
    # Borneo
    [(109, 1), (112, 3), (115, 5), (117, 6), (118, 2), (116, -2), (113, -3),
     (110, -1)],
    # Java
    [(106, -6), (110, -7), (114, -8), (114, -9), (108, -8)],
    # New Guinea
    [(131, -1), (136, -2), (140, -4), (144, -6), (147, -8), (141, -8),
     (136, -6), (132, -4)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-2, 55), (-4, 58), (-6, 56)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 39),
     (141, 41), (143, 42), (140, 38), (137, 36), (134, 34), (131, 32)],
    # Madagascar
    [(44, -16), (47, -15), (50, -17), (48, -22), (45, -25), (43, -21)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (175, -37), (173, -41), (170, -44)],
]

# (number, lon, lat, label)
PINS = [
    (1, -74, 40.7, 'NEW YORK'),
    (2, 56.5, 26.5, 'HORMUZ'),
    (3, 34.5, 31.5, 'GAZA'),
    (4, 24, 59.5, 'GULF OF FINLAND'),
    (5, 46.7, 24.6, 'RIYADH'),
    (6, 30.5, 39.8, 'ESKISEHIR'),
    (7, -75.5, 10.4, 'CARTAGENA'),
    (8, 45, 12.8, 'ADEN'),
    (9, 20, 32.1, 'BENGHAZI'),
    (10, 35.2, 47.8, 'ZAPORIZHZHIA'),
    (11, 127, 37.5, 'SEOUL'),
    (12, 29.5, 1.5, 'ITURI'),
]


def draw_map(c, x, y, w, h):
    c.rect(x, y, w, h, SEA)
    # faint graticule
    for lon in range(-150, 181, 30):
        gx = x + int((lon + 180) / 360 * w)
        c.line(gx, y, gx, y + h, (170, 200, 220))
    for lat in (60, 30, 0, -30):
        gy = y + int((80 - lat) / 130 * h)
        c.line(x, gy, x + w, gy, (170, 200, 220))
    # continents
    for poly in CONTINENTS:
        pts = [(x + int((lon + 180) / 360 * w),
                y + int((80 - lat) / 130 * h)) for lon, lat in poly]
        c.poly(pts, LAND)
        # outline
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            c.line(x1, y1, x2, y2, LAND_DARK)
    # pins
    for num, lon, lat, _label in PINS:
        px = x + int((lon + 180) / 360 * w)
        py = y + int((80 - lat) / 130 * h)
        c.circle(px, py, 6, RED)
        c.ring(px, py, 6, WHITE, 1)
        c.circle(px, py, 2, WHITE)
        lab = str(num)
        lx = px + 9
        ly = py - 4
        if lx + text_width(lab, 1) > x + w - 2:
            lx = px - 9 - text_width(lab, 1)
        c.text(lx, ly, lab, 1, DARK_RED)
    c.frame(x, y, w, h, INK, 2)


# -------------------------------------------------------------------- data
HERO = {
    'kicker': 'TOP STORY  -  UNITED STATES',
    'headline': 'HUAWEI FOUND GUILTY IN U.S. FRAUD TRIAL',
    'summary': ('A Brooklyn jury convicts the Chinese telecom giant on 10 of '
                '12 counts - bank fraud, wire fraud, sanctions violations '
                'and stealing trade secrets. It cleared Huawei of '
                'racketeering and obstructing justice. Sentencing is set '
                'for 14 September 2027.'),
    'scene': 'huawei',
}

LEADS = [
    {
        'kicker': 'STRAIT OF HORMUZ',
        'headline': 'IRGC HITS SHIP IN HORMUZ STRAIT',
        'summary': ("Iran's navy says it hit a container ship in the "
                    "strait; four tankers struck mines."),
        'scene': 'hormuz',
    },
    {
        'kicker': 'GAZA',
        'headline': 'HAMAS SECURITY CHIEF KILLED IN GAZA',
        'summary': ('Israeli strike kills Hamas security chief Naeem Abu '
                    'Nahel and six others in Gaza.'),
        'scene': 'gaza',
    },
    {
        'kicker': 'UKRAINE',
        'headline': 'UKRAINE HITS RUSSIAN SHIP SPARTA II',
        'summary': ('Ukrainian drones hit the Russian cargo ship Sparta II '
                    'in the Gulf of Finland.'),
        'scene': 'sparta',
    },
    {
        'kicker': 'SAUDI ARABIA',
        'headline': "DRONE HITS RIYADH'S PIF TOWER",
        'summary': ('Suspected drone strike hits the 385 m PIF tower; at '
                    'least 11 people wounded.'),
        'scene': 'riyadh',
    },
]

# 36 more stories, one line each (duplicates of the leads removed).
MORE = [
    'TURKEY HELICOPTER CRASH KILLS 5 CREW',
    'CARTAGENA GUNMEN HOLD 25 HOSTAGE',
    'HOUTHIS 60 KM FROM ADEN, READY TO HIT',
    'UK SANCTIONS HOUTHIS, FOUR OFFICIALS',
    "LIBYA'S HAFTAR VISITS TURKEY, MEETS ERDOGAN",
    'SENEGAL REGAIN AFRICA CUP AFTER APPEAL',
    'NVIDIA SOARS 31% AS HUANG RETURNS',
    'COP31 FALLOUT: 90+ NATIONS REJECT DRAFT',
    'NATO SENDS AWACS TO POLAND',
    'SEVEN NATIONS BACK EU VISA CURBS ON RUSSIA',
    'GERMANY FIRST INTO UKRAINE DELTA SYSTEM',
    'EU PROPOSES 22ND SANCTIONS PACKAGE',
    'NEARLY 700,000 RUSSIAN TROOPS LOST',
    'RUSSIAN JETS ENTER S. KOREA AIR ZONE',
    'IRAQ PM TAKES OVER KURDISH OILFIELDS',
    'FIGHTING IN ITURI TRAPS EBOLA TEAMS',
    'UN URGES PROBE INTO BENGHAZI ATTACKS',
    'NATO CHIEF: WE WILL DEFEND SPACE',
    'ZELENSKY: UKRAINE MUST JOIN NATO',
    'PUTIN OPEN TO ARTICLE 5-STYLE GUARANTEES',
    'VANCE, RUBIO MEET QATAR PM AT WHITE HOUSE',
    'US DRONE TRACKED EL CHAPO ISIDRO',
    'UAE BUS CRASH KILLS 13, INJURES 14',
    "POPE'S PRIVATE DIARY RELEASED",
    'SUPER BOWL 61 TO BE SHOWN IN IMAX',
    'THANKSGIVING DINNER UP 6.3% THIS YEAR',
    'WALMART $35 THANKSGIVING MEAL GOES VIRAL',
    'WALL ST REBOUNDS ON NVIDIA NEWS',
    'S. KOREA OFFERS $375,000 TO CATCH AI CHEATS',
    'REP. JIMMY GOMEZ RESIGNS AFTER ETHICS FINDING',
    'TRUMP TO SPEED UP FEDERAL DEATH SENTENCES',
    "BEST BUY, DICK'S, DOLLAR TREE REPORT",
    'KING TIDES HIT US WEST COAST',
    'FLOODING CONTINUES IN FLORIDA',
    'IOWA ARMY BLAST CLEARED BY COURT',
    'UN WORKER KILLED IN GAZA STRIKES',
]


# ------------------------------------------------------------------ layout
def build():
    c = Canvas(W, H, PAPER)

    # ---- masthead
    c.rect(0, 0, W, 6, INK)
    c.text_centered(W // 2, 16, 'THE WORLD IN ONE PAGE', 2, RED)
    c.text_centered(W // 2, 36, 'TUESDAY 24 NOVEMBER 2026', 5, INK)
    c.rect(16, 84, W - 32, 2, INK)
    c.rect(16, 89, W - 32, 1, INK)
    c.text_centered(
        W // 2, 97,
        '41 STORIES FROM AROUND THE WORLD - FIRST REPORTED TUESDAY 24 NOVEMBER 2026',
        1, SOFT_INK)

    # ---- hero lead: Huawei
    hx, hy, hw, hh = 16, 118, 420, 196
    c.frame(hx, hy, hw, hh, INK, 2)
    SCENES[HERO['scene']](c, hx + 2, hy + 2, hw - 4, hh - 4)
    tx = 452
    c.text(tx, 122, HERO['kicker'], 2, RED)
    y = 142
    for line in wrap_text(HERO['headline'], W - 16 - tx, 3):
        c.text(tx, y, line, 3, INK)
        y += 24
    y += 6
    c.text_block(tx, y, HERO['summary'], 2, SOFT_INK, W - 16 - tx, 17)
    # number badge on the hero picture
    c.circle(hx + 18, hy + 18, 11, RED)
    c.text(hx + 14, hy + 14, '1', 1, WHITE)

    # ---- four leads, 2 x 2 grid
    cell_w, cell_h = 494, 116
    for i, lead in enumerate(LEADS):
        cx = 16 + (i % 2) * (cell_w + 4)
        cy = 330 + (i // 2) * (cell_h + 8)
        px, py, pw, ph = cx, cy, 150, cell_h
        c.frame(px, py, pw, ph, INK, 1)
        SCENES[lead['scene']](c, px + 1, py + 1, pw - 2, ph - 2)
        c.circle(px + 14, py + 14, 10, RED)
        c.text(px + 11, py + 10, str(i + 2), 1, WHITE)
        tx2 = cx + 162
        tw = 16 + cell_w - 162 + 4 - 8
        c.text(tx2, cy + 2, lead['kicker'], 1, RED)
        yy = cy + 14
        for line in wrap_text(lead['headline'], tw, 2):
            c.text(tx2, yy, line, 2, INK)
            yy += 16
        yy += 2
        c.text_block(tx2, yy, lead['summary'], 1, SOFT_INK, tw, 10)

    # ---- world map
    my = 566
    c.text(16, my, 'THE WORLD - 12 PLACES IN THE NEWS', 2, INK)
    c.text(W - 16 - text_width('RED DOT = WHERE IT HAPPENED', 1), my + 4,
           'RED DOT = WHERE IT HAPPENED', 1, RED)
    draw_map(c, 16, my + 24, W - 32, 168)
    legend = '  '.join('%d %s' % (n, lab) for n, _lo, _la, lab in PINS)
    leg_y = my + 24 + 168 + 8
    for line in wrap_text(legend, W - 32, 1):
        c.text(16, leg_y, line, 1, SOFT_INK)
        leg_y += 10

    # ---- 36 more stories
    sy = 800
    c.rect(16, sy - 6, W - 32, 2, INK)
    c.text(16, sy, 'AND 36 MORE', 2, INK)
    c.text(W - 16 - text_width('TUESDAY 24 NOVEMBER 2026', 1), sy + 4,
           'TUESDAY 24 NOVEMBER 2026', 1, SOFT_INK)
    col_w = 320
    col_x = [16, 352, 688]
    for col in range(3):
        x = col_x[col]
        y = sy + 24
        for item in MORE[col * 12:(col + 1) * 12]:
            c.text(x, y, '•', 1, RED)
            c.text(x + 10, y, item, 1, INK)
            y += 11

    # ---- sources line
    c.text(16, 962,
           'SOURCES: REUTERS - AP - DAILY SUMMARY OF WORLD - THE DAILY EDITION',
           1, SOFT_INK)

    # ---- date-check strip
    c.rect(0, 984, W, H - 984, INK)
    c.text_centered(W // 2, 990,
                    'ALL STORIES FIRST REPORTED TUESDAY 24 NOVEMBER 2026',
                    2, WHITE)
    c.text_centered(
        W // 2, 1008,
        'ICJ MYANMAR RULING WAS 19 NOV - EL CHAPO ISIDRO CAPTURE WAS 20 NOV '
        '- COP31 COLLAPSE WAS 23 NOV',
        1, (200, 200, 196))
    return c


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', 'out')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'entry.png')
    canvas = build()
    size = write_png(path, canvas)
    print('wrote %s (%d bytes, %dx%d)' % (path, size, W, H))


if __name__ == '__main__':
    main()
