#!/usr/bin/env python3
"""Draw the entry image for make.fun competition news-image-20261118.

A one-page newspaper front page summing up the world news of
Wednesday 18 November 2026, drawn entirely with PIL shapes and type.
Output: entry.png (1024x1024) next to this script.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)      # #f7f3ea
INK = (26, 26, 26)           # #1a1a1a
RED = (179, 32, 42)          # #b3202a
FAINT = (120, 112, 96)       # muted warm grey for hairlines / waves
GOLD = (176, 141, 46)        # sparing third tone for one icon

W = H = 1024
MARGIN = 40
CONTENT_W = W - 2 * MARGIN

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_BOLD = os.path.join(FONT_DIR, "liberation", "LiberationSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "liberation", "LiberationSerif-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "liberation", "LiberationSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "liberation", "LiberationSans-Regular.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start_size, max_width, min_size=14):
    """Largest font size (<= start_size) at which text fits max_width."""
    size = start_size
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return font(path, min_size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def centered(draw, cx, y, text, fnt, fill=INK):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text,
              font=fnt, fill=fill)


def spaced(draw, cx, y, text, fnt, fill=INK, tracking=6):
    """Draw text with extra letter tracking, centred on cx."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


# ------------------------------------------------------------------- icons
# Each icon draws inside the box (x0, y0, x1, y1).

def icon_summit(d, box):
    """Three overlapping circles: three leaders at one table."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = 30
    d.ellipse([cx - r - 26, cy - r + 6, cx + r - 26, cy + r + 6],
              outline=INK, width=5)
    d.ellipse([cx - r + 26, cy - r + 6, cx + r + 26, cy + r + 6],
              outline=RED, width=5)
    d.ellipse([cx - r, cy - r - 12, cx + r, cy + r - 12],
              outline=GOLD, width=5)


def icon_gulf(d, box):
    """A tanker on waves, a missile arc rising toward a sun."""
    x0, y0, x1, y1 = box
    # sun
    sx, sy, sr = x1 - 34, y0 + 20, 13
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=RED)
    # missile arc (dashed): from ship up toward the sun
    pts = []
    for t in range(21):
        f = t / 20
        px = x0 + 52 + f * (sx - x0 - 66)
        py = y1 - 44 - math.sin(f * math.pi * 0.62) * 52 - f * 8
        pts.append((px, py))
    for i in range(0, len(pts) - 1, 2):
        d.line([pts[i], pts[i + 1]], fill=INK, width=4)
    # ship hull + bridge block
    hx0, hy = x0 + 22, y1 - 40
    hx1 = x0 + 108
    d.polygon([(hx0, hy), (hx1, hy), (hx1 - 12, hy + 14), (hx0 + 10, hy + 14)],
              fill=INK)
    d.rectangle([hx0 + 16, hy - 13, hx0 + 44, hy], fill=INK)
    d.rectangle([hx0 + 52, hy - 8, hx1 - 14, hy], outline=INK, width=4)
    # waves
    for row, wy in enumerate((y1 - 18, y1 - 6)):
        for wx in range(x0 + 6 + row * 14, x1 - 22, 34):
            d.arc([wx, wy - 7, wx + 24, wy + 7], 180, 360, fill=FAINT, width=3)


def _sag(d, xa, ya, xb, yb, sag, fill, width=4):
    """A cable hanging between two points, drawn as a shallow parabola."""
    pts = []
    for i in range(25):
        f = i / 24
        px = xa + (xb - xa) * f
        py = ya + (yb - ya) * f + sag * 4 * f * (1 - f)
        pts.append((px, py))
    d.line(pts, fill=fill, width=width)


def icon_bridge(d, box):
    """A suspension bridge over water, one span broken (the strike)."""
    x0, y0, x1, y1 = box
    deck_y = y1 - 32
    mid = (x0 + x1) // 2
    top_y = y0 + 10
    # towers
    for tx in (x0 + 28, x1 - 28):
        d.line([(tx, top_y), (tx, deck_y)], fill=INK, width=5)
    # main cables: shore to tower, tower to tower (sagging), tower to shore
    _sag(d, x0 + 4, deck_y - 6, x0 + 28, top_y, 4, INK)
    _sag(d, x0 + 28, top_y, x1 - 28, top_y, 26, INK)
    _sag(d, x1 - 28, top_y, x1 - 4, deck_y - 6, 4, INK)
    # hangers from the centre cable down to the deck
    for f in (0.18, 0.34, 0.5, 0.66, 0.82):
        hx = (x0 + 28) + (x1 - 28 - x0 - 28) * f
        hy = top_y + 26 * 4 * f * (1 - f)
        d.line([(hx, hy), (hx, deck_y)], fill=FAINT, width=3)
    # deck in two pieces with a gap in the middle
    d.line([(x0 + 4, deck_y), (mid - 15, deck_y)], fill=INK, width=6)
    d.line([(mid + 15, deck_y), (x1 - 4, deck_y)], fill=INK, width=6)
    # fallen piece, tilted into the water
    d.line([(mid - 13, deck_y + 3), (mid + 9, deck_y + 17)], fill=RED, width=6)
    # water
    for wx in range(x0 + 8, x1 - 26, 36):
        d.arc([wx, deck_y + 10, wx + 24, deck_y + 24], 180, 360,
              fill=FAINT, width=3)


def icon_climate(d, box):
    """A leaf inside a circle: the planet and the talks."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = 38
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=5)
    # leaf: a pointed-oval outline built from two sine-bowed sides,
    # running from lower-left to upper-right, with a vein down its spine
    ax, ay = cx - 19, cy + 19          # leaf base
    bx, by = cx + 19, cy - 19          # leaf tip
    dx, dy = bx - ax, by - ay
    px, py = -dy, dx                   # perpendicular direction
    norm = math.hypot(px, py)
    px, py = px / norm, py / norm
    side_a, side_b = [], []
    for i in range(21):
        f = i / 20
        off = math.sin(f * math.pi) * 13
        side_a.append((ax + dx * f + px * off, ay + dy * f + py * off))
        side_b.append((ax + dx * f - px * off, ay + dy * f - py * off))
    d.line(side_a, fill=RED, width=4)
    d.line(side_b, fill=RED, width=4)
    d.line([(ax, ay), (bx, by)], fill=RED, width=3)


def icon_chip(d, box):
    """A computer chip: square die, inner core, pins on every side."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    half = 30
    d.rectangle([cx - half, cy - half, cx + half, cy + half],
                outline=INK, width=5)
    d.rectangle([cx - 13, cy - 13, cx + 13, cy + 13], outline=RED, width=4)
    for f in (-0.62, 0.0, 0.62):
        off = int(f * half)
        # top and bottom pins
        d.line([(cx + off, cy - half - 11), (cx + off, cy - half)],
               fill=INK, width=5)
        d.line([(cx + off, cy + half), (cx + off, cy + half + 11)],
               fill=INK, width=5)
        # left and right pins
        d.line([(cx - half - 11, cy + off), (cx - half, cy + off)],
               fill=INK, width=5)
        d.line([(cx + half, cy + off), (cx + half + 11, cy + off)],
               fill=INK, width=5)


def icon_cyclone(d, box):
    """A spiral swirl: the storm making landfall."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    pts = []
    steps = 140
    for i in range(steps + 1):
        f = i / steps
        ang = f * math.pi * 5.2
        rad = 4 + f * 36
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.line(pts, fill=INK, width=6, joint="curve")
    ex, ey = pts[-1]
    d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=RED)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)


# ------------------------------------------------------------------ stories
STORIES = [
    ("SHENZHEN SUMMIT", icon_summit,
     "Xi and Putin meet in Shenzhen; Trump joins Thursday - "
     "Ukraine and Iran top the agenda."),
    ("GULF ESCALATION", icon_gulf,
     "US strikes Iran missile site on Qeshm Island; five Iranian "
     "tankers sunk; oil near $93."),
    ("UKRAINE STRIKES BRIDGE", icon_bridge,
     "Ukraine hits the Kerch Bridge to Crimea for a second night; "
     "Europe joins peace talks."),
    ("COP31 DECISIVE WEEK", icon_climate,
     "Climate talks in Antalya split over fossil-fuel phase-out; "
     "island nations plead for funds."),
    ("NVIDIA AFTER HUANG", icon_chip,
     "Board rules out Jensen Huang's return; revenue doubles to "
     "$115.8B on AI demand."),
    ("CYCLONE AKVAN", icon_cyclone,
     "Severe cyclone bears down on India's Odisha coast; "
     "evacuations under way."),
]

FOOTER_LINES = [
    "Peltola wins Alaska - Democrats take the US Senate 56-44",
    "UN warns Gaza faces deadly winter cold",
    "Voyager 1 reaches one light-day from Earth",
]


# -------------------------------------------------------------------- draw
def draw_panel(d, x, y, w, headline, icon_fn, sub):
    """One news panel: icon, headline, sub-line. Returns nothing."""
    icon_fn(d, (x + w // 2 - 55, y + 0, x + w // 2 + 55, y + 80))

    # largest headline size that wraps to at most two lines
    size = 38
    while size > 22:
        head_font = font(SERIF_BOLD, size)
        head_lines = wrap(d, headline, head_font, w - 16)
        if len(head_lines) <= 2:
            break
        size -= 2
    hy = y + 88
    for line in head_lines:
        centered(d, x + w // 2, hy, line, head_font, INK)
        hy += head_font.size + 4

    sub_font = font(SANS, 22)
    sub_lines = wrap(d, sub, sub_font, w - 20)
    sy = hy + 4
    for line in sub_lines:
        centered(d, x + w // 2, sy, line, sub_font, INK)
        sy += 27


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    cx = W // 2

    # ---- masthead
    d.line([(MARGIN, 34), (W - MARGIN, 34)], fill=INK, width=3)
    spaced(d, cx, 46, "THE WORLD IN ONE DAY", font(SANS_BOLD, 27), INK, 8)
    d.line([(MARGIN, 88), (W - MARGIN, 88)], fill=INK, width=1)

    day_font = fit_font(d, "WEDNESDAY", SERIF_BOLD, 64, CONTENT_W)
    centered(d, cx, 100, "WEDNESDAY", day_font, RED)
    date_font = fit_font(d, "18 NOVEMBER 2026", SERIF_BOLD, 118, CONTENT_W)
    centered(d, cx, 168, "18 NOVEMBER 2026", date_font, INK)

    d.line([(MARGIN, 292), (W - MARGIN, 292)], fill=INK, width=5)
    d.line([(MARGIN, 302), (W - MARGIN, 302)], fill=INK, width=1)

    # ---- story grid: 3 columns x 2 rows
    grid_top = 310
    grid_bottom = 892
    gutter = 18
    col_w = (CONTENT_W - 2 * gutter) // 3
    row_h = (grid_bottom - grid_top - gutter) // 2

    for i, (headline, icon_fn, sub) in enumerate(STORIES):
        col, row = i % 3, i // 3
        px = MARGIN + col * (col_w + gutter)
        py = grid_top + row * (row_h + gutter)
        draw_panel(d, px, py, col_w, headline, icon_fn, sub)

    # hairline separators between columns and rows
    for col in (1, 2):
        sx = MARGIN + col * col_w + (col - 1) * gutter + gutter // 2
        d.line([(sx, grid_top + 4), (sx, grid_bottom - 4)], fill=FAINT, width=1)
    mid_y = grid_top + row_h + gutter // 2
    d.line([(MARGIN, mid_y), (W - MARGIN, mid_y)], fill=FAINT, width=1)

    # ---- footer strip
    d.line([(MARGIN, 906), (W - MARGIN, 906)], fill=RED, width=4)
    foot_font = font(SANS_BOLD, 25)
    fy = 918
    for line in FOOTER_LINES:
        centered(d, cx, fy, line, foot_font, INK)
        fy += 31

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
