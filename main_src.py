#!/usr/bin/env python3
"""The Day in One Image - Friday 20 November 2026.

make.fun bounty: "Sum up 20 November's world news in one image"
(slug: news-image-20261120). Writes one 1024x1024 PNG to
/output/entry.png (or ./output/entry.png when /output is absent).

Self-contained, standard library only. A small rasterizer with an
embedded 5x7 bitmap font draws a dense one-page front page in the
style of a picture newspaper: a huge date masthead, a strip of six
big numbers, a coloured region bar, three lead stories with large
drawn illustrations (Kyiv bridges under attack, Cyclone Akvan's
landfall, Asia's market sell-off), ten more stories in a grid with
small drawn pictograms, a numbered world map, a 22-item "also on"
list, a date-check box and a sources line — 35 stories in all,
each one checked against reporting of Friday 20 November 2026.
A minimal PNG encoder (zlib) writes the bytes. No network, no
clock, no randomness: the same bytes come out on every run.
"""

import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024
PAPER = (250, 246, 236)
CARD = (255, 253, 247)
INK = (18, 18, 18)
MUTED = (96, 90, 78)
NAVY = (27, 52, 88)
RED = (196, 32, 32)
GOLD = (232, 180, 44)
TEAL = (18, 96, 88)
SKY = (58, 140, 200)
LIGHTSKY = (150, 205, 240)
DUSK = (32, 42, 96)
SUNSET = (240, 110, 50)
GREEN = (34, 139, 70)
DARKGREEN = (18, 64, 52)
SAND = (240, 200, 90)
ROYAL = (40, 80, 180)
PURPLE = (88, 52, 138)
WHITE = (255, 255, 255)
ORANGE = (240, 130, 30)
YELLOW = (250, 210, 60)
LIGHTRED = (255, 140, 120)
LIGHTBLUE = (200, 205, 225)

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
# Every number below was checked against reporting of 20 November 2026;
# figures that could not be verified were dropped or softened.
KICKER_LEFT = "The World in One Day"
KICKER_RIGHT = (
    "35 stories \u00b7 7 regions \u00b7 Every one dated Friday 20 November 2026"
)
MASTHEAD = "Friday 20 November 2026"
SUBHEAD = [
    "Russian missiles hit Kyiv's bridges \u00b7 Cyclone Akvan strikes India",
    "An AI sell-off sinks Asia's markets \u00b7 UK and EU seal a deal",
]
STATS = [
    ("3", "Bridges over the Dnipro", "damaged in Kyiv"),
    ("300,000+", "People moved to shelters", "before Akvan"),
    ("-6.2%", "Taiwan's share index,", "Friday's close"),
    ("110", "Missiles fired at Ukraine", "in one night"),
    ("2.3%", "Japan consumer inflation", "in October"),
    ("118", "Runs by Glenn Phillips", "against India"),
]
REGIONS = [
    ("Europe", 9, NAVY),
    ("Asia", 8, RED),
    ("Mideast", 3, (200, 150, 30)),
    ("Africa", 5, GREEN),
    ("Americas", 4, PURPLE),
    ("Oceania", 3, TEAL),
    ("Global", 3, (90, 90, 90)),
]
LEADS = [
    {
        "num": 1,
        "place": "Kyiv, Ukraine \u00b7 War",
        "banner": "Kyiv",
        "credit": "Officials' count",
        "headline": "Russian missiles hit three Kyiv bridges",
        "summary": (
            "About 110 missiles and 400 drones hit Ukraine overnight; "
            "9 killed, 28 hurt. Power and water cut in Kyiv, and a "
            "missile and a drone fell in Poland. (BBC)"
        ),
    },
    {
        "num": 2,
        "place": "Odisha, India \u00b7 Weather",
        "banner": "Cyclone Akvan",
        "credit": "Weather office",
        "headline": "Cyclone Akvan comes ashore in eastern India",
        "summary": (
            "The storm crossed the coast near Gopalpur from about 8 am. "
            "More than 300,000 people were moved to shelters. No "
            "deaths were reported. (IMD)"
        ),
    },
    {
        "num": 3,
        "place": "Taipei, Seoul, Tokyo \u00b7 Markets",
        "banner": "AI sell-off",
        "credit": "Closing prices",
        "headline": "AI sell-off sinks Asia's stock markets",
        "summary": (
            "Taiwan's index fell 6.2% to end its worst week since 1991. "
            "Seoul lost 5.2% and Tokyo 5.1% as chipmakers led the "
            "slide. (Reuters)"
        ),
    },
]
GRID = [
    {
        "num": 4, "place": "Brussels \u00b7 Diplomacy",
        "banner": "UK-EU deal", "credit": "Agreed \u00b7 Reuters",
        "headline": "UK and EU seal a 'reset' deal",
        "summary": "Food trade, youth visas, carbon link.",
        "pic": "uk_eu",
    },
    {
        "num": 5, "place": "Antalya \u00b7 Climate",
        "banner": "COP31: no deal", "credit": "Ongoing \u00b7 UN News",
        "headline": "COP31's last day: no deal",
        "summary": "The draft text leaves out fossil fuels.",
        "pic": "cop",
    },
    {
        "num": 6, "place": "Poland \u00b7 War",
        "banner": "Poland: missile", "credit": "Minister says \u00b7 Reuters",
        "headline": "Russian missile lands in Poland",
        "summary": "A KH-101 came down in a field.",
        "pic": "poland",
    },
    {
        "num": 7, "place": "Iraq \u00b7 Security",
        "banner": "Iraq: army in", "credit": "Witnessed \u00b7 Reuters",
        "headline": "Iraqi army moves in",
        "summary": "Troops deploy to Jurf al-Sakhar.",
        "pic": "iraq",
    },
    {
        "num": 8, "place": "Rome \u00b7 Labour",
        "banner": "Italy: strike", "credit": "Reported \u00b7 Reuters",
        "headline": "Italy's general strike",
        "summary": "Workers and students march.",
        "pic": "italy",
    },
    {
        "num": 9, "place": "Tokyo \u00b7 Economy",
        "banner": "Japan: +2.3%", "credit": "Official data \u00b7 Reuters",
        "headline": "Japan inflation at 2.3%",
        "summary": "A December rate rise stays in view.",
        "pic": "japan",
    },
    {
        "num": 10, "place": "Seoul \u00b7 Politics",
        "banner": "Seoul: impeach",
        "credit": "Party decision \u00b7 Korea Herald",
        "headline": "Impeach the top judge",
        "summary": "It follows a court reversal.",
        "pic": "seoul",
    },
    {
        "num": 11, "place": "Turkana \u00b7 Energy",
        "banner": "Kenya: oil", "credit": "Ceremony held \u00b7 allAfrica",
        "headline": "Kenya's first oil well",
        "summary": "First crude is due on 1 December.",
        "pic": "kenya",
    },
    {
        "num": 12, "place": "San Salvador \u00b7 Politics",
        "banner": "Bukele: 3rd bid", "credit": "Filed \u00b7 AP",
        "headline": "Bukele seeks a third term",
        "summary": "The vote is on 28 February 2027.",
        "pic": "bukele",
    },
    {
        "num": 13, "place": "Wellington \u00b7 Cricket",
        "banner": "Phillips: 118", "credit": "Scorecard \u00b7 ICC",
        "headline": "Phillips makes 118",
        "summary": "Hundreds v India in all three formats.",
        "pic": "phillips",
    },
]
ALSO = [
    ("14", "Lviv", "A strike on a railway station kills two", "BBC"),
    ("15", "Tallinn", "Estonia shuts its border with Russia", "Reuters"),
    ("16", "Berlin", "Pupils strike over military service", "Al Jazeera"),
    ("17", "London", "General: UK runs cyber attacks abroad", "Sky News"),
    ("18", "Beijing", "China leaves its loan rates unchanged", "Xinhua"),
    ("19", "Tokyo", "SoftBank shares fall more than 14%", "Al Jazeera"),
    ("20", "Seoul", "Kospi index ends the week 8% lower", "Anadolu"),
    ("21", "Ganjam", "209 mm of rain falls as Akvan crosses Odisha", "PTI"),
    ("22", "Lebanon", "Israeli strikes hit south and east", "Anadolu"),
    ("23", "Yemen", "Gunmen fire on a cargo ship off the coast", "UKMTO"),
    ("24", "Abuja", "Court bars new evidence against Tinubu", "Channels TV"),
    ("25", "Kampala", "Police to enforce Ebola ban on rallies", "allAfrica"),
    ("26", "Malawi", "Fuel crisis brings night-long queues", "Al Jazeera"),
    ("27", "Africa", "AFDB warns of debt distress", "allAfrica"),
    ("28", "Las Vegas", "Russell fastest in wet GP practice", "Autosport"),
    ("29", "New York", "Nasdaq futures fall before bell", "24/7 Wall St"),
    ("30", "Washington", "Democrats query law firm free work", "Al Jazeera"),
    ("31", "Wellington", "Nicholls makes 175 not out", "ICC"),
    ("32", "Sydney", "Australian shares slide in the sell-off", "Reuters"),
    ("33", "Antalya", "Panama asks COP31 to cap oil output", "Anadolu"),
    ("34", "Antalya", "EU calls climate draft unacceptable", "RTE"),
    ("35", "Turin", "ATP backs plan to lift player pay", "Anadolu"),
]
DATE_CHECK = (
    "Left out as Thursday 19 November's news: the three-leader summit "
    "in Shenzhen and the Seoul court ruling that set off Friday's "
    "impeachment push. Not yet happened, so not shown: BepiColombo's "
    "entry into orbit round Mercury and any final COP31 text."
)
FOOTER = (
    "Every story here happened, or was first reported, on "
    "Friday 20 November 2026. Officials' counts are attributed."
)
SOURCES_LINE = "Sources named beside each story \u00b7 Original drawings"


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

    def disc(self, cx, cy, r, color):
        """Filled circle, scanline by scanline."""
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - half, cy + dy, 2 * half + 1, 1, color)

    def half_disc_right(self, cx, cy, r, color):
        """Right half of a filled circle."""
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.rect(cx, cy + dy, half + 1, 1, color)

    def ellipse(self, cx, cy, rx, ry, color):
        """Filled ellipse."""
        for dy in range(-ry, ry + 1):
            half = int(rx * (1 - (dy * dy) / (ry * ry)) ** 0.5)
            self.rect(cx - half, cy + dy, 2 * half + 1, 1, color)

    def ellipse_outline(self, cx, cy, rx, ry, color, t=2):
        """Ellipse outline from its scanline chords."""
        for dy in range(-ry, ry + 1):
            half = int(rx * (1 - (dy * dy) / (ry * ry)) ** 0.5)
            self.rect(cx - half, cy + dy, t, t, color)
            self.rect(cx + half, cy + dy, t, t, color)
        for dx in range(-rx, rx + 1):
            half = int(ry * (1 - (dx * dx) / (rx * rx)) ** 0.5)
            self.rect(cx + dx, cy - half, t, t, color)
            self.rect(cx + dx, cy + half, t, t, color)

    def poly(self, pts, color):
        """Filled polygon, scanline fill with integer math."""
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) // (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(xs[i], y, xs[i + 1] - xs[i] + 1, 1, color)

    def burst(self, cx, cy, r, color, core=None):
        """Eight-point starburst: four diamonds plus a bright core."""
        self.poly([(cx - r, cy), (cx, cy - r // 3),
                   (cx + r, cy), (cx, cy + r // 3)], color)
        self.poly([(cx, cy - r), (cx + r // 3, cy),
                   (cx, cy + r), (cx - r // 3, cy)], color)
        d = int(r * 0.7)
        self.poly([(cx - d, cy - d), (cx + d // 3, cy - d // 3),
                   (cx + d, cy + d), (cx - d // 3, cy + d // 3)], color)
        self.poly([(cx + d, cy - d), (cx + d // 3, cy - d // 3),
                   (cx - d, cy + d), (cx - d // 3, cy + d // 3)], color)
        if core is not None:
            self.disc(cx, cy, max(2, r // 3), core)


def outline(cv, x, y, w, h, color, t=2):
    cv.rect(x, y, w, t, color)
    cv.rect(x, y + h - t, w, t, color)
    cv.rect(x, y, t, h, color)
    cv.rect(x + w - t, y, t, h, color)


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


def draw_story(cv, x, y, width, story, head_scale=3, tag_color=NAVY,
               leading=3, stat_color=None):
    y = draw_block(cv, x, y, width, [story["tag"]], 2, tag_color, 4)
    y = draw_block(cv, x, y, width,
                   wrap_text(story["headline"], width, head_scale),
                   head_scale, INK, leading)
    y = draw_block(cv, x, y, width,
                   wrap_text(story["summary"], width, 2), 2, INK, leading)
    if story.get("stat"):
        y = draw_block(cv, x, y + 2, width, [story["stat"]], 2,
                       stat_color or MUTED, leading)
    return y


# --- Small drawn devices -------------------------------------------------

def draw_drone(cv, cx, cy):
    """A quadcopter silhouette with a red light."""
    cv.rect(cx - 5, cy - 2, 10, 4, INK)
    cv.line(cx - 9, cy - 5, cx + 9, cy - 5, INK, 2)
    cv.line(cx - 9, cy + 5, cx + 9, cy + 5, INK, 2)
    for rx in (-11, 11):
        cv.rect(cx + rx - 2, cy - 7, 5, 2, WHITE)
        cv.rect(cx + rx - 2, cy + 6, 5, 2, WHITE)
    cv.rect(cx - 1, cy + 3, 3, 3, RED)


def arrow_left(cv, x, cy, length, color):
    cv.line(x + length, cy, x + 10, cy, color, 3)
    cv.poly([(x, cy), (x + 10, cy - 6), (x + 10, cy + 6)], color)


def arrow_right(cv, x, cy, length, color):
    cv.line(x, cy, x + length - 10, cy, color, 3)
    cv.poly([(x + length, cy), (x + length - 10, cy - 6),
             (x + length - 10, cy + 6)], color)


def flag_us(cv, x, y, w, h):
    for i in range(7):
        y0 = y + i * h // 7
        y1 = y + (i + 1) * h // 7
        cv.rect(x, y0, w, y1 - y0, RED if i % 2 == 0 else WHITE)
    cw, ch = w // 2, 4 * h // 7
    cv.rect(x, y, cw, ch, (30, 50, 130))
    for gx in range(3):
        for gy in range(3):
            cv.rect(x + 3 + gx * 6, y + 3 + gy * 4, 2, 2, WHITE)


def flag_cn(cv, x, y, w, h):
    cv.rect(x, y, w, h, (222, 30, 30))
    cv.poly([(x + 9, y + 4), (x + 13, y + 9), (x + 9, y + 14),
             (x + 5, y + 9)], YELLOW)
    for sx, sy in ((20, 5), (24, 10), (24, 16), (19, 19)):
        cv.rect(x + sx, y + sy, 3, 3, YELLOW)


def flag_ru(cv, x, y, w, h):
    for i, color in enumerate((WHITE, (40, 90, 200), RED)):
        y0 = y + i * h // 3
        y1 = y + (i + 1) * h // 3
        cv.rect(x, y0, w, y1 - y0, color)


def flag_uk(cv, x, y, w, h):
    cv.rect(x, y, w, h, (0, 40, 130))
    cv.line(x, y, x + w, y + h, WHITE, 6)
    cv.line(x + w, y, x, y + h, WHITE, 6)
    cv.rect(x + w // 2 - 5, y, 10, h, WHITE)
    cv.rect(x, y + h // 2 - 5, w, 10, WHITE)
    cv.rect(x + w // 2 - 3, y, 6, h, RED)
    cv.rect(x, y + h // 2 - 3, w, 6, RED)


def flag_eu(cv, x, y, w, h):
    cv.rect(x, y, w, h, (0, 40, 130))
    for k in range(12):
        a = 2 * math.pi * k / 12
        dx = int((w // 2 - 6) * math.cos(a))
        dy = int((h // 2 - 6) * math.sin(a))
        cv.rect(x + w // 2 + dx - 1, y + h // 2 + dy - 1, 3, 3, YELLOW)


# --- Story illustrations -------------------------------------------------

def ill_kyiv(cv, x, y, w, h):
    """Dusk sky over Kyiv: skyline, cable bridge, drones, missile
    trails and blasts on the deck. All positions scale with w."""
    cv.rect(x, y, w, h, DUSK)
    for fx, fy in ((0.09, 0.12), (0.28, 0.22), (0.47, 0.09),
                   (0.72, 0.17), (0.93, 0.11), (0.60, 0.28),
                   (0.19, 0.38)):
        cv.rect(x + int(fx * w), y + int(fy * h), 2, 2, WHITE)
    cv.rect(x, y + h - 56, w, 56, SUNSET)
    cv.rect(x, y + h - 56, w, 4, GOLD)
    for fx, fw, fh in ((0.00, 0.11, 44), (0.12, 0.08, 30),
                       (0.21, 0.12, 58), (0.35, 0.09, 36),
                       (0.46, 0.13, 66), (0.61, 0.08, 40),
                       (0.71, 0.11, 52), (0.84, 0.09, 34),
                       (0.94, 0.06, 46)):
        cv.rect(x + int(fx * w), y + h - fh, int(fw * w), fh, (14, 18, 44))
    deck_y = y + h - 64
    cv.rect(x + 14, deck_y, w - 28, 5, INK)
    t1, t2 = x + int(0.28 * w), x + int(0.66 * w)
    cv.rect(t1, y + 44, 8, deck_y - (y + 44), INK)
    cv.rect(t2, y + 44, 8, deck_y - (y + 44), INK)
    for tx in (t1 + 4, t2 + 4):
        for dx in (-64, -32, 0, 32, 64):
            cv.line(tx, y + 46, tx + dx, deck_y, LIGHTBLUE, 2)
    for fx, fy in ((0.19, 0.16), (0.59, 0.30), (0.90, 0.13)):
        draw_drone(cv, x + int(fx * w), y + int(fy * h))
    cv.line(x + w - 30, y + 12, x + int(0.66 * w), deck_y - 14,
            ORANGE, 4)
    cv.line(x + w - 30, y + 12, x + int(0.66 * w), deck_y - 14,
            WHITE, 2)
    cv.line(x + 70, y + 18, x + int(0.36 * w), deck_y - 26,
            ORANGE, 4)
    cv.line(x + 70, y + 18, x + int(0.36 * w), deck_y - 26,
            WHITE, 2)
    cv.burst(x + int(0.36 * w), deck_y - 4, 18, YELLOW, core=RED)
    cv.burst(x + int(0.80 * w), deck_y - 6, 13, ORANGE, core=YELLOW)


def ill_akvan(cv, x, y, w, h):
    """Cyclone Akvan: spiral storm bands over the Odisha coast,
    green land on the left, sea on the right, rain over the land."""
    cv.rect(x, y, w, h, SKY)
    # Land: green coast on the left with a wavy shoreline.
    cv.poly([(x, y + 26), (x + 78, y + 18), (x + 108, y + 52),
             (x + 92, y + 96), (x + 118, y + 128), (x + 96, y + h),
             (x, y + h)], GREEN)
    cv.ellipse(x + 30, y + 10, 30, 6, WHITE)
    cv.ellipse(x + 230, y + 18, 36, 7, WHITE)
    # Rain over the land.
    for k in range(5):
        cv.line(x + 18 + k * 18, y + 58, x + 30 + k * 18, y + 82,
                LIGHTBLUE, 2)
    # Spiral bands centred over the coast.
    cx, cy = x + 150, y + 78
    for rx, ry in ((18, 10), (36, 20), (56, 30), (78, 42)):
        cv.ellipse_outline(cx, cy, rx, ry, WHITE, 2)
    cv.disc(cx, cy, 6, WHITE)
    # Gopalpur: red dot on the coast, label at the foot of the land.
    cv.disc(x + 100, y + 100, 4, RED)
    cv.circle_outline(x + 100, y + 100, 6, WHITE, 2)
    draw_text(cv, x + 8, y + h - 24, "Gopalpur", 1, WHITE)


def ill_selloff(cv, x, y, w, h):
    """AI sell-off: a red line falls off a cliff over a dark board,
    with ticker rows for the four Asian markets."""
    cv.rect(x, y, w, h, (24, 30, 40))
    for gy in (y + 34, y + 68, y + 102):
        cv.hline(x + 8, x + w - 8, gy, (52, 62, 78), 1)
    pts = [(x + 22, y + 18), (x + 96, y + 30), (x + 158, y + 58),
           (x + 224, y + 96), (x + 300, y + 138)]
    for i in range(4):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                (255, 90, 70), 4)
    cv.disc(pts[0][0], pts[0][1], 5, GOLD)
    cv.disc(pts[4][0], pts[4][1], 5, (255, 90, 70))
    cv.poly([(pts[4][0], pts[4][1] + 14), (pts[4][0] - 7, pts[4][1] + 2),
             (pts[4][0] + 7, pts[4][1] + 2)], (255, 90, 70))
    rows = [("Taipei", "-6.2%", 74), ("Seoul", "-5.2%", 62),
            ("Tokyo", "-5.1%", 61), ("Hong Kong", "-1.9%", 23)]
    for k, (name, pct, bar) in enumerate(rows):
        ry = y + 104 + k * 13
        draw_text(cv, x + 14, ry, name + " " + pct, 1, WHITE)
        cv.rect(x + 132, ry - 1, bar, 9, (255, 90, 70))


# --- Grid pictograms (190x52 each) -------------------------------------

def pic_uk_eu(cv, x, y, w, h):
    """Union Jack and EU flag with two interlocked gold rings."""
    cv.rect(x, y, w, h, ROYAL)
    flag_uk(cv, x + 10, y + 8, 68, 34)
    flag_eu(cv, x + w - 78, y + 8, 68, 34)
    cx, cy = x + w // 2, y + 26
    cv.circle_outline(cx - 11, cy, 13, GOLD, 3)
    cv.circle_outline(cx + 11, cy, 13, GOLD, 3)


def pic_cop(cv, x, y, w, h):
    """A globe split in two: green half, orange half, a white crack
    down the middle and arrows pulling apart."""
    cv.rect(x, y, w, h, SAND)
    cx, cy, r = x + w // 2, y + h // 2, 20
    cv.disc(cx, cy, r, GREEN)
    cv.half_disc_right(cx, cy, r, ORANGE)
    for dy in (-8, 8):
        half = int((r * r - dy * dy) ** 0.5)
        cv.hline(cx - half, cx + half, cy + dy, WHITE, 2)
    cv.ellipse_outline(cx, cy, 6, r, WHITE, 2)
    cv.circle_outline(cx, cy, r, INK, 2)
    cv.line(cx - 2, cy - r + 2, cx + 3, cy - 8, WHITE, 2)
    cv.line(cx + 3, cy - 8, cx - 3, cy, WHITE, 2)
    cv.line(cx - 3, cy, cx + 3, cy + 8, WHITE, 2)
    cv.line(cx + 3, cy + 8, cx - 2, cy + r - 2, WHITE, 2)
    arrow_left(cv, x + 10, cy, 26, GREEN)
    arrow_right(cv, x + w - 36, cy, 26, RED)


def pic_poland(cv, x, y, w, h):
    """A cruise missile streaks over a green field."""
    cv.rect(x, y, w, 30, LIGHTSKY)
    cv.rect(x, y + 30, w, h - 30, GREEN)
    cv.rect(x, y + 30, w, 3, (20, 90, 40))
    cv.ellipse(x + 30, y + 8, 16, 4, WHITE)
    cv.ellipse(x + 140, y + 14, 20, 5, WHITE)
    cv.line(x + 40, y + 10, x + 110, y + 42, (200, 200, 210), 8)
    cv.line(x + 40, y + 10, x + 110, y + 42, INK, 3)
    cv.line(x + 28, y + 6, x + 40, y + 10, ORANGE, 6)
    cv.line(x + 22, y + 4, x + 28, y + 6, YELLOW, 4)
    cv.burst(x + 116, y + 44, 11, YELLOW, core=RED)
    cv.disc(x + 126, y + 38, 5, (200, 200, 210))


def pic_iraq(cv, x, y, w, h):
    """Two army trucks roll across the desert at sunset."""
    cv.rect(x, y, w, h, SAND)
    cv.disc(x + 168, y + 10, 8, GOLD)
    cv.rect(x, y + 36, w, h - 36, (200, 160, 90))
    cv.line(x + 178, y + 36, x + 178, y + 14, (120, 80, 40), 3)
    cv.ellipse(x + 178, y + 12, 12, 4, GREEN)
    cv.rect(x + 16, y + 24, 46, 14, (40, 90, 50))
    cv.rect(x + 62, y + 28, 14, 10, (40, 90, 50))
    cv.rect(x + 66, y + 30, 6, 6, LIGHTBLUE)
    for wx in (24, 48, 70):
        cv.disc(x + wx, y + 40, 4, INK)
    cv.rect(x + 104, y + 28, 36, 11, (60, 110, 65))
    cv.rect(x + 140, y + 31, 10, 8, (60, 110, 65))
    for wx in (112, 130, 146):
        cv.disc(x + wx, y + 41, 3, INK)


def pic_italy(cv, x, y, w, h):
    """A crowd under a red strike banner."""
    cv.rect(x, y, w, h, (240, 230, 210))
    cv.rect(x + 8, y + 8, w - 16, 12, RED)
    draw_text(cv, x + (w - 36) // 2, y + 10, "Strike", 1, WHITE)
    colors = (NAVY, RED, TEAL, GREEN, PURPLE, ORANGE)
    for k, color in enumerate(colors):
        cx = x + 22 + k * 30
        cv.disc(cx, y + 30, 6, color)
        cv.rect(cx - 10, y + 37, 20, h - 37, color)


def pic_japan(cv, x, y, w, h):
    """A red sun over a rising bar chart."""
    cv.rect(x, y, w, h, (250, 240, 220))
    cv.disc(x + 42, y + 26, 17, RED)
    for k, bh in enumerate((10, 16, 22, 28)):
        bx = x + 92 + k * 22
        cv.rect(bx, y + 46 - bh, 14, bh,
                RED if k == 3 else (120, 120, 120))
    cv.rect(x + 88, y + 46, 92, 2, INK)


def pic_seoul(cv, x, y, w, h):
    """A courthouse: pediment, four columns, steps."""
    cv.rect(x, y, w, h, NAVY)
    cv.poly([(x + 24, y + 14), (x + 166, y + 14), (x + 95, y + 2)],
            WHITE)
    for k in range(4):
        cv.rect(x + 32 + k * 30, y + 16, 10, 26, WHITE)
    cv.rect(x + 24, y + 42, 142, 4, WHITE)
    cv.rect(x + 76, y + 30, 12, 12, INK)
    cv.rect(x + 16, y + 46, 158, 4, (200, 200, 210))


def pic_kenya(cv, x, y, w, h):
    """An oil derrick against a desert sunset."""
    cv.rect(x, y, w, 26, SUNSET)
    cv.rect(x, y + 26, w, h - 26, (240, 180, 80))
    cv.disc(x + 164, y + 12, 8, GOLD)
    cv.rect(x, y + 44, w, h - 44, (140, 100, 50))
    cv.line(x + 34, y + 46, x + 56, y + 10, INK, 3)
    cv.line(x + 78, y + 46, x + 56, y + 10, INK, 3)
    cv.line(x + 40, y + 34, x + 72, y + 34, INK, 2)
    cv.line(x + 46, y + 22, x + 66, y + 22, INK, 2)
    cv.line(x + 56, y + 10, x + 96, y + 20, INK, 4)
    cv.disc(x + 56, y + 10, 3, INK)
    cv.disc(x + 98, y + 21, 3, INK)


def pic_bukele(cv, x, y, w, h):
    """A ballot box with a paper slip going in."""
    cv.rect(x, y, w, h, (60, 120, 200))
    cv.rect(x + 66, y + 20, 58, 28, WHITE)
    cv.rect(x + 66, y + 20, 58, 4, RED)
    cv.rect(x + 82, y + 32, 26, 4, INK)
    cv.rect(x + 86, y + 6, 18, 14, WHITE)
    cv.line(x + 90, y + 16, x + 95, y + 11, RED, 2)
    cv.line(x + 95, y + 11, x + 102, y + 18, RED, 2)
    cv.rect(x + 66, y + 40, 58, 8, (200, 210, 230))


def pic_phillips(cv, x, y, w, h):
    """A cricket bat meets the ball on a green pitch."""
    cv.rect(x, y, w, h, GREEN)
    cv.rect(x + 12, y + 8, w - 24, h - 16, (120, 200, 120))
    for sx in (150, 156, 162):
        cv.rect(x + sx, y + 28, 3, 18, YELLOW)
    cv.rect(x + 148, y + 26, 18, 2, YELLOW)
    cv.line(x + 96, y + 12, x + 122, y + 40, (200, 160, 90), 8)
    cv.line(x + 96, y + 12, x + 122, y + 40, (140, 100, 50), 2)
    cv.disc(x + 128, y + 44, 4, RED)


# --- Numbered world map --------------------------------------------------

CONTINENTS = [
    # North America (lon, lat) outline, schematic.
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 70),
     (-80, 70), (-65, 60), (-55, 52), (-60, 45), (-70, 42),
     (-75, 35), (-80, 26), (-85, 20), (-90, 12), (-95, 16),
     (-100, 20), (-105, 22), (-115, 28), (-125, 40), (-125, 48),
     (-135, 58), (-155, 58), (-165, 60)],
    # Greenland.
    [(-55, 60), (-40, 64), (-30, 68), (-25, 70), (-35, 76),
     (-55, 75), (-60, 70)],
    # South America.
    [(-80, 10), (-75, 5), (-70, 10), (-60, 5), (-50, 0),
     (-40, -5), (-35, -10), (-40, -20), (-50, -30), (-60, -35),
     (-70, -40), (-75, -50), (-70, -55), (-75, -45), (-70, -30),
     (-80, -20), (-80, -5)],
    # Africa.
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (40, 15), (45, 11), (50, 10), (45, 0), (40, -10),
     (35, -20), (30, -30), (20, -35), (15, -30), (10, -20),
     (12, -10), (8, 0), (5, 5), (-5, 5), (-15, 5)],
    # Eurasia.
    [(-10, 36), (-5, 44), (-2, 48), (0, 50), (5, 55), (10, 58),
     (18, 56), (25, 60), (30, 65), (40, 68), (50, 70), (60, 70),
     (70, 72), (90, 75), (110, 75), (130, 72), (150, 70),
     (170, 66), (180, 65), (170, 60), (160, 55), (145, 45),
     (140, 40), (130, 35), (125, 30), (120, 25), (110, 20),
     (105, 10), (100, 8), (95, 15), (90, 22), (82, 12),
     (80, 13), (75, 10), (70, 20), (65, 25), (60, 25),
     (55, 26), (50, 29), (45, 30), (40, 36), (35, 36),
     (30, 36), (25, 40), (20, 40), (15, 44), (10, 44),
     (5, 40), (0, 38)],
    # Australia.
    [(113, -22), (114, -30), (115, -35), (120, -34), (130, -32),
     (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (146, -19), (142, -11), (135, -12), (132, -12), (126, -14),
     (122, -17), (114, -20)],
    # Britain, Japan, New Zealand, Madagascar, Indonesia (schematic).
    [(-5, 50), (-2, 53), (0, 52), (1, 51), (-3, 50)],
    [(130, 31), (135, 34), (140, 38), (142, 42), (145, 44),
     (142, 45), (140, 40), (135, 35), (130, 33)],
    [(167, -45), (170, -42), (174, -40), (177, -38), (175, -37),
     (172, -40), (168, -44)],
    [(43, -12), (47, -15), (50, -17), (47, -25), (44, -24),
     (43, -16)],
    [(95, 5), (105, 0), (115, -5), (125, -8), (135, -5),
     (140, -8), (130, -2), (120, 0), (110, 5), (100, 2)],
]
# Story number -> (lon, lat, dx, dy) for the map dots.
# The dx/dy nudges spread the dots where the news clusters (Europe,
# East Asia, the Middle East) so the numbers stay legible at this size.
MAP_DOTS = [
    (1, 30.5, 50.5, 10, -1), (2, 84.9, 19.3, 0, 0),
    (3, 121.6, 25.0, 0, 1), (4, 4.4, 50.8, 5, -9),
    (5, 30.7, 36.9, 2, 6), (6, 23.0, 50.3, 7, 6),
    (7, 44.2, 32.9, 17, -2), (8, 12.5, 41.9, 6, 8),
    (9, 139.7, 35.7, 6, -5), (10, 127.0, 37.6, 2, -7),
    (11, 35.9, 3.5, 10, -6), (12, -89.2, 13.7, 0, 0),
    (13, 174.8, -41.3, -4, -8), (14, 24.0, 49.8, -8, 6),
    (15, 24.7, 59.4, 0, -5), (16, 13.4, 52.5, 11, -6),
    (17, -0.1, 51.5, -4, -4), (18, 116.4, 39.9, -5, -5),
    (19, 139.7, 35.7, 10, 9), (20, 127.0, 37.6, 6, 3),
    (21, 84.9, 19.4, -5, 5), (22, 35.5, 33.9, 13, -7),
    (23, 45.0, 12.8, 13, -3), (24, 7.5, 9.1, 0, 0),
    (25, 32.6, 0.3, 0, 0), (26, 33.8, -14.0, 0, 0),
    (27, -4.0, 5.4, 0, 0), (28, -115.1, 36.2, 0, 0),
    (29, -74.0, 40.7, 0, 0), (30, -77.0, 38.9, 0, 7),
    (31, 174.8, -41.3, 0, 6), (32, 151.2, -33.9, 0, 0),
    (33, 30.7, 36.9, 16, 6), (34, 30.7, 36.9, 4, 14),
    (35, 7.7, 45.1, -9, 4),
]


def draw_map(cv, x, y, w, h):
    """Numbered world map: tan continents on a navy sea."""
    cv.rect(x, y, w, h, NAVY)

    def lonlat(lon, lat):
        px = x + int((lon + 170) / 360 * w)
        py = y + int((80 - lat) / 140 * h)
        return px, py

    for cont in CONTINENTS:
        cv.poly([lonlat(lon, lat) for lon, lat in cont], SAND)
    for num, lon, lat, dx, dy in MAP_DOTS:
        cx, cy = lonlat(lon, lat)
        cx += dx
        cy += dy
        cv.disc(cx, cy, 7, RED)
        s = str(num)
        draw_text(cv, cx - 3 * len(s), cy - 3, s, 1, WHITE)


# --- Small front-page devices --------------------------------------------

def draw_text_right(cv, right_x, y, s, scale, color):
    """Draw text ending at right_x."""
    x = right_x - text_width(s.upper(), scale)
    draw_text(cv, x, y, s, scale, color)
    return x


def label_banner(cv, x, y, text, scale):
    """Red label banner with white text; returns its width."""
    pad = 6 if scale == 2 else 4
    w = text_width(text, scale) + 2 * pad
    h = 7 * scale + 6
    cv.rect(x, y, w, h, RED)
    draw_text(cv, x + pad, y + 3, text, scale, WHITE)
    return w


def credit_strip(cv, x, y, w, text):
    """Black strip with a white credit line."""
    cv.rect(x, y, w, 14, INK)
    draw_text(cv, x + 6, y + 4, text, 1, WHITE)


def num_disc(cv, cx, cy, num, r=7):
    """Red disc with a white number."""
    cv.disc(cx, cy, r, RED)
    s = str(num)
    draw_text(cv, cx - 3 * len(s), cy - 3, s, 1, WHITE)


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
    MX, RX = 16, 1008
    # Kicker line and rules.
    draw_text(cv, MX, 8, KICKER_LEFT, 1, RED)
    draw_text_right(cv, RX, 8, KICKER_RIGHT, 1, INK)
    cv.rect(MX, 22, 992, 3, INK)
    # Masthead and subhead.
    draw_centered(cv, 30, MASTHEAD, 6, INK)
    for i, line in enumerate(SUBHEAD):
        draw_centered(cv, 78 + i * 16, line, 2, MUTED)
    cv.rect(MX, 112, 992, 2, INK)
    # Stat strip: six big numbers with red bars.
    stat_x = MX
    for (num, cap1, cap2), wcol in zip(
            STATS, [166, 165, 165, 165, 165, 166]):
        cv.rect(stat_x, 118, 3, 50, RED)
        draw_text(cv, stat_x + 8, 120, num, 3, INK)
        draw_text(cv, stat_x + 8, 147, cap1, 1, MUTED)
        draw_text(cv, stat_x + 8, 156, cap2, 1, MUTED)
        stat_x += wcol
    # Region bar: segment widths proportional to the story counts.
    total = sum(n for _, n, _ in REGIONS)
    bounds = [MX]
    cum = 0
    for _, n, _ in REGIONS:
        cum += n
        bounds.append(MX + round(992 * cum / total))
    for (name, n, color), x0, x1 in zip(REGIONS, bounds, bounds[1:]):
        cv.rect(x0, 172, x1 - x0, 16, color)
        label = name.upper() + " " + str(n)
        tx = x0 + (x1 - x0 - text_width(label, 1)) // 2
        draw_text(cv, tx, 176, label, 1, WHITE)
    # Three lead stories.
    lead_ills = (ill_kyiv, ill_akvan, ill_selloff)
    lead_x = [MX, 351, 686]
    for lead, x0, ill in zip(LEADS, lead_x, lead_ills):
        ill(cv, x0, 194, 322, 168)
        label_banner(cv, x0, 194, lead["banner"], 2)
        credit_strip(cv, x0, 348, 322, lead["credit"])
        num_disc(cv, x0 + 7, 369, lead["num"])
        draw_text(cv, x0 + 18, 366, lead["place"], 1, RED)
        y = draw_block(cv, x0, 384, 322,
                       wrap_text(lead["headline"], 322, 2), 2, INK, 3)
        draw_block(cv, x0, y + 4, 322,
                   wrap_text(lead["summary"], 322, 1), 1, INK, 3)
    # Ten more stories in a 2x5 grid.
    grid_pics = {
        "uk_eu": pic_uk_eu, "cop": pic_cop, "poland": pic_poland,
        "iraq": pic_iraq, "italy": pic_italy, "japan": pic_japan,
        "seoul": pic_seoul, "kenya": pic_kenya, "bukele": pic_bukele,
        "phillips": pic_phillips,
    }
    for i, story in enumerate(GRID):
        row, col = divmod(i, 5)
        gx = MX + col * 200
        gy = 460 + row * 138
        grid_pics[story["pic"]](cv, gx, gy, 190, 52)
        label_banner(cv, gx, gy, story["banner"], 1)
        credit_strip(cv, gx, gy + 38, 190, story["credit"])
        draw_text(cv, gx, gy + 58, str(story["num"]) + " ", 1, RED)
        draw_text(cv, gx + 18, gy + 58, story["place"], 1, INK)
        y = draw_block(cv, gx, gy + 72, 190,
                       wrap_text(story["headline"], 190, 2), 2, INK, 3)
        draw_block(cv, gx, y + 2, 190,
                   wrap_text(story["summary"], 190, 1), 1, INK, 3)
    # Map and the 22-item list.
    draw_text(cv, MX, 734, "Where it happened", 2, INK)
    draw_text(cv, 262, 734,
              "Also on Friday 20 November \u2014 22 more stories", 2, INK)
    draw_map(cv, MX, 754, 230, 140)
    draw_text(cv, MX, 898, "Numbers match the stories above.", 1, MUTED)
    for i, (num, place, text, src) in enumerate(ALSO):
        col, row = divmod(i, 11)
        ax = 262 + col * 374
        ay = 754 + row * 12
        draw_text(cv, ax, ay, num + " " + place, 1, RED)
        nx = ax + text_width(num + " " + place + " ", 1)
        nx = draw_text(cv, nx, ay, text, 1, INK)
        draw_text(cv, nx + 6, ay, "(" + src + ")", 1, MUTED)
    # Date check and footer.
    outline(cv, MX, 910, 992, 50, RED, 2)
    draw_text(cv, 26, 916, "Date check", 2, RED)
    draw_block(cv, 26, 934, 960,
               wrap_text(DATE_CHECK, 960, 1), 1, INK, 3)
    draw_centered(cv, 970, FOOTER, 1, MUTED)
    draw_centered(cv, 984, SOURCES_LINE, 1, MUTED)
    return cv


def main():
    cv = render()
    data = encode_png(W, H, cv.buf)
    base = "/output" if os.path.isdir("/output") else "output"
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)"
          % (path, len(data), W, H))
    return 0


if __name__ == "__main__":
    sys.exit(main())
