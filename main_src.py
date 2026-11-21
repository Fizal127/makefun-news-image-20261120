#!/usr/bin/env python3
"""The Day in One Image - Friday 20 November 2026.

make.fun bounty: "Sum up 20 November's world news in one image"
(slug: news-image-20261120). Writes one 1024x1024 PNG to
/output/entry.png (or ./output/entry.png when /output is absent).

Self-contained, standard library only. A small rasterizer with an
embedded 5x7 bitmap font draws a one-page broadsheet of the day's
news, with a hand-drawn bridge pictogram for the lead story and a
globe device at the foot; a minimal PNG encoder (zlib) writes the
bytes. No network, no clock, no randomness: the same bytes come out
on every run.
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024
PAPER = (250, 246, 236)
INK = (18, 18, 18)
MUTED = (96, 90, 78)
NAVY = (27, 52, 88)
RED = (164, 38, 32)
TEAL = (18, 96, 88)

# 5x7 bitmap font: each glyph is 7 rows of 5 bits (MSB = left column).
# All copy is rendered in capitals, broadsheet-headline style.
GLYPHS = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ";": (0, 0x0C, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0, 0x04),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "\u2014": (0, 0, 0, 0x1F, 0, 0, 0),
    "\u2013": (0, 0, 0, 0x1F, 0, 0, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "\u2019": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "*": (0, 0x15, 0x0E, 0x1F, 0x0E, 0x15, 0),
    "\u2022": (0, 0, 0x0C, 0x0C, 0x0C, 0, 0),
    "\u00b7": (0, 0, 0, 0x0C, 0, 0, 0),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
}

# The day's news, Friday 20 November 2026. Facts as reported that day.
TITLE = "The Day in One Image"
KICKER = "One day \u00b7 One world \u00b7 One image"
DATE_LINE = "Friday, 20 November 2026"
STORIES = [
    {
        "tag": "Kyiv \u00b7 The War",
        "headline": "Russia's big barrage hits Kyiv bridges \u2014 and spills into Poland",
        "summary": "More than 400 drones and 110 missiles struck Ukraine; "
        "8 killed, about 30 hurt, and power cut across Kyiv. Two Russian "
        "missiles and a drone fell in Poland, a NATO member.",
        "stat": "462 targets downed \u00b7 NATO: a grave violation",
    },
    {
        "tag": "Shenzhen \u00b7 Diplomacy",
        "headline": "Trump, Xi and Putin pledge more nuclear-risk talks",
        "summary": "A day after their first three-way summit, the leaders "
        "of the three biggest nuclear powers agree to keep talking. "
        "Trump says no rush on Iran \u2014 a decision after Jan 1.",
    },
    {
        "tag": "Markets \u00b7 Tech",
        "headline": "Anthropic's record IPO cools as tech sells off",
        "summary": "Priced at $83, the AI lab's shares opened at $111.50 "
        "on debut, then slid back under $89 as US stocks fell for a "
        "sixth straight day.",
    },
    {
        "tag": "Antalya \u00b7 Climate",
        "headline": "COP31 ends its last day still deadlocked on fossil fuels",
        "summary": "Negotiators fail to bridge the fossil-fuel divide as "
        "the summit reaches its scheduled final day.",
    },
    {
        "tag": "London \u00b7 Europe",
        "headline": "UK and EU strike landmark deal to rebuild ties",
        "summary": "London and Brussels agree to ease trade and youth "
        "mobility, five years after Brexit.",
    },
    {
        "tag": "Riyadh \u00b7 Middle East",
        "headline": "Houthi missile damages Riyadh's tallest tower",
        "summary": "A missile blows out windows across seven to eight "
        "floors of the capital's tallest tower; no injuries reported.",
    },
]
BRIEFS = [
    ("Brussels", "EU pays Kyiv EUR 7.9B, its largest single payment"),
    ("Hanoi", "Vietnam scraps death penalty for drug trafficking"),
    ("Markets", "Bitcoin slides near $61,700, lowest since July"),
]
SOURCES_LINE = "Sources: BBC World \u00b7 All Voices News \u00b7 Daily News \u00b7 Le Monde \u00b7 IANS"


class Canvas:
    """An RGB raster with a few drawing primitives."""

    def __init__(self):
        self.buf = bytearray(bytes(PAPER) * (W * H))

    def rect(self, x, y, w, h, color):
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, W)
        y1 = min(y + h, H)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x0, x1, y, color, t=1):
        self.rect(x0, y, x1 - x0, t, color)

    def vline(self, x, y0, y1, color, t=1):
        self.rect(x, y0, t, y1 - y0, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line, with a square brush of side t."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.rect(x, y, t, t, color)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle_outline(self, cx, cy, r, color, t=2):
        """Midpoint circle outline."""
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.rect(px, py, t, t, color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1


def text_width(s, scale):
    return len(s) * 6 * scale


def draw_text(cv, x, y, s, scale, color):
    """Draw upper-cased bitmap text; returns the x after the last glyph."""
    cx = x
    for ch in s.upper():
        glyph = GLYPHS.get(ch, GLYPHS["?"])
        for r in range(7):
            bits = glyph[r]
            if not bits:
                continue
            for c in range(5):
                if (bits >> (4 - c)) & 1:
                    cv.rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_centered(cv, y, s, scale, color):
    x = (W - text_width(s.upper(), scale)) // 2
    draw_text(cv, x, y, s, scale, color)


def wrap_text(s, max_w, scale):
    """Greedy word wrap of upper-cased text to a pixel width."""
    words = s.upper().split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_width(trial, scale) <= max_w:
            cur = trial
            continue
        if cur:
            lines.append(cur)
        while text_width(word, scale) > max_w:
            n = max(1, max_w // (6 * scale))
            lines.append(word[:n])
            word = word[n:]
        cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, max_w, lines, scale, color, leading=3):
    for line in lines:
        draw_text(cv, x, y, line, scale, color)
        y += 7 * scale + leading
    return y


def draw_story(cv, x, y, width, story, head_scale=3, tag_color=NAVY):
    y = draw_block(cv, x, y, width, [story["tag"]], 2, tag_color, 4)
    y = draw_block(cv, x, y, width,
                   wrap_text(story["headline"], width, head_scale),
                   head_scale, INK, 3)
    y = draw_block(cv, x, y, width,
                   wrap_text(story["summary"], width, 2), 2, INK, 3)
    if story.get("stat"):
        y = draw_block(cv, x, y + 2, width, [story["stat"]], 2, MUTED, 3)
    return y


def draw_bridge(cv, x0, y0, w, h):
    """A bridge under fire: deck, two towers, cables, blast streaks."""
    cv.rect(x0, y0, w, h, (224, 233, 240))
    # River band along the bottom.
    cv.rect(x0, y0 + h - 26, w, 26, NAVY)
    deck_y = y0 + h - 40
    # Towers.
    t1, t2 = x0 + 78, x0 + w - 86
    cv.rect(t1, y0 + 34, 8, deck_y - (y0 + 34), NAVY)
    cv.rect(t2, y0 + 34, 8, deck_y - (y0 + 34), NAVY)
    # Cables fanning from each tower top to the deck.
    for tx in (t1 + 4, t2 + 4):
        for dx in (-64, -32, 0, 32, 64):
            cv.line(tx, y0 + 36, tx + dx, deck_y, NAVY, 2)
    # Deck.
    cv.rect(x0 + 8, deck_y, w - 16, 5, INK)
    # Blast streaks above the left span.
    bx, by = x0 + 52, y0 + 52
    cv.line(bx, by, bx - 16, by - 18, RED, 3)
    cv.line(bx, by, bx + 2, by - 22, RED, 3)
    cv.line(bx, by, bx + 18, by - 12, RED, 3)
    cv.rect(bx - 3, by - 3, 7, 7, RED)
    # Thin border.
    cv.rect(x0, y0, w, 2, INK)
    cv.rect(x0, y0 + h - 2, w, 2, INK)
    cv.rect(x0, y0, 2, h, INK)
    cv.rect(x0 + w - 2, y0, 2, h, INK)


def draw_globe(cv, cx, cy, r):
    """A wireframe globe: outline, two latitude chords, one meridian."""
    cv.circle_outline(cx, cy, r, NAVY, 3)
    for dy in (-r // 2, r // 2):
        half = int((r * r - dy * dy) ** 0.5)
        cv.hline(cx - half, cx + half, cy + dy, NAVY, 2)
    cv.vline(cx, cy - r, cy + r, NAVY, 2)
    # A red dot where the day's lead story happened.
    cv.rect(cx + 16, cy - 24, 7, 7, RED)


def encode_png(w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)
        raw += rgb[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def render():
    cv = Canvas()
    mx, rx = 48, W - 48
    y = 34
    # Kicker + masthead.
    draw_centered(cv, y, KICKER, 2, MUTED)
    y += 7 * 2 + 8
    draw_centered(cv, y, TITLE.upper(), 5, NAVY)
    y += 7 * 5 + 12
    cv.hline(mx, rx, y, NAVY, 3)
    y += 11
    draw_centered(cv, y, DATE_LINE, 2, RED)
    y += 7 * 2 + 10
    cv.hline(mx, rx, y, INK, 2)
    y += 16
    # Lead story, full width, with the bridge pictogram on the right.
    lead_w = 600
    pic_x, pic_w = mx + lead_w + 28, rx - (mx + lead_w + 28)
    lead_bottom = draw_story(cv, mx, y, lead_w, STORIES[0], head_scale=4)
    draw_bridge(cv, pic_x, y, pic_w, 168)
    y = max(lead_bottom, y + 168) + 12
    cv.hline(mx, rx, y, INK, 1)
    y += 14
    # Stories 2 and 3 side by side.
    col_w = (rx - mx - 32) // 2
    y2 = draw_story(cv, mx, y, col_w, STORIES[1])
    y3 = draw_story(cv, mx + col_w + 32, y, col_w, STORIES[2])
    y = max(y2, y3) + 12
    cv.hline(mx, rx, y, INK, 1)
    y += 14
    # Stories 4, 5, 6 in three columns.
    col3 = (rx - mx - 2 * 28) // 3
    ends = []
    for i, story in enumerate(STORIES[3:]):
        ends.append(draw_story(cv, mx + i * (col3 + 28), y, col3, story,
                               head_scale=2))
    y = max(ends) + 16
    # Briefs box.
    box_top = y
    pad = 20
    inner_w = rx - mx - 2 * pad
    by = box_top + pad
    by = draw_block(cv, mx + pad, by, inner_w, ["In Brief"], 3, TEAL, 4)
    by += 4
    for place, text in BRIEFS:
        line = "\u2022 " + place + " \u2014 " + text
        by = draw_block(cv, mx + pad, by, inner_w,
                        wrap_text(line, inner_w, 2), 2, INK, 3)
    box_bottom = by + pad - 3
    cv.hline(mx, rx, box_top, TEAL, 2)
    cv.hline(mx, rx, box_bottom, TEAL, 2)
    cv.vline(mx, box_top, box_bottom, TEAL, 2)
    cv.vline(rx - 2, box_top, box_bottom, TEAL, 2)
    y = box_bottom + 16
    # Footer.
    draw_centered(cv, y, SOURCES_LINE, 2, MUTED)
    y += 7 * 2 + 20
    # Globe device at the foot.
    draw_globe(cv, W // 2, y + 46, 46)
    return cv, y + 46 + 46


def main():
    cv, bottom = render()
    data = encode_png(W, H, cv.buf)
    base = "/output" if os.path.isdir("/output") else "output"
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d, content bottom y=%d)"
          % (path, len(data), W, H, bottom))
    return 0


if __name__ == "__main__":
    sys.exit(main())

