"""Props, scenery and sounds for Episode 2, "Wash Before You Munch?" (bathroom).

Everything here is hand-built paper cut-outs (paperlib.Cut) or synthesized audio (numpy),
in the same style as scene.py / icons.py / audio.py. Shared modules are not modified.

Layout: the characters stand *behind* a two-basin wash counter, so the counter is drawn in
front of them and their paws, the water, soap and foam all sit in front of their tummies.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import audio as A  # noqa: E402
from paperlib import (SHADOW_OFFSET, SS, Cut, Sprite, _composite_clipped,  # noqa: E402
                      _transform, grain, heart_pts, place, star_pts)

W, H = 1080, 1920
FLOOR_Y = 1440                 # where the characters' feet are (hidden behind the counter)
COUNTER_X = 92                 # counter sprite left edge
COUNTER_TOP = 1334             # top of the counter's surface band
SURFACE_Y = 1362               # where things "sit" on the counter
ARM_CLIP = 1374                # arms redrawn in front of the counter are clipped below this line

# palette
TILE = (186, 226, 242)
TILE_ALT = (172, 216, 236)
GROUT = (246, 251, 253)
WALL_TOP = (255, 241, 212)
TRIM = (110, 190, 222)
FLOOR_A = (250, 247, 240)
FLOOR_B = (164, 214, 226)
CAB = (248, 172, 150)
CAB_PANEL = (252, 198, 178)
CAB_DARK = (218, 136, 116)
TOP = (253, 251, 246)
TOP_EDGE = (226, 222, 214)
BASIN_IN = (184, 210, 226)
CHROME = (198, 212, 226)
CHROME_HI = (240, 246, 252)
CHROME_DARK = (150, 168, 186)
WATER = (128, 196, 240)
WATER_HI = (226, 244, 255)
SOAP = (255, 150, 186)
SOAP_HI = (255, 206, 222)
MUD = (132, 88, 52)
MUD_DARK = (104, 68, 40)
APPLE = (232, 58, 62)
APPLE_DARK = (196, 40, 52)
APPLE_FLESH = (255, 244, 206)
LEAF = (98, 182, 86)
STEM = (122, 84, 52)
TOWEL = (255, 208, 84)
TOWEL_STRIPE = (110, 176, 232)
SNIP_FUR = (226, 214, 242)
EYE = (38, 32, 44)


# ---------------------------------------------------------------- background
def _wall():
    k = 2
    img = Image.new("RGBA", (W * k, H * k), WALL_TOP + (255,))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(21)
    # bubble wallpaper on the upper wall
    for row in range(7):
        for col in range(10):
            x = (col * 118 + (59 if row % 2 else 0) + 20) * k
            y = (row * 92 + 46) * k
            r = (10 + 5 * ((row + col) % 3)) * k
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 252, 244), width=3 * k)
            d.ellipse([x - r * 0.45 - r * 0.2, y - r * 0.45 - r * 0.2, x - r * 0.45 + r * 0.2,
                       y - r * 0.45 + r * 0.2], fill=(255, 252, 244))
    # tiled wall
    t, g, top = 96, 6, 640
    d.rectangle([0, (top - 46) * k, W * k, H * k], fill=GROUT)
    for x0 in range(0, W, 120):           # trim row
        d.rounded_rectangle([(x0 + 4) * k, (top - 40) * k, (x0 + 116) * k, (top - 8) * k], 10 * k, fill=TRIM)
    for row in range(9):
        for col in range(12):
            x0 = col * t - 30
            y0 = top + row * t
            c = TILE if (row + col) % 5 else TILE_ALT
            v = int(rng.integers(-5, 6))
            c = tuple(max(0, min(255, ch + v)) for ch in c)
            d.rounded_rectangle([(x0 + g) * k, (y0 + g) * k, (x0 + t) * k, (y0 + t) * k], 9 * k, fill=c)
            # soft shine on each tile
            d.rounded_rectangle([(x0 + g + 10) * k, (y0 + g + 8) * k, (x0 + g + 34) * k, (y0 + g + 14) * k],
                                3 * k, fill=tuple(min(255, ch + 22) for ch in c))
    # baseboard + floor
    d.rectangle([0, (FLOOR_Y - 10) * k, W * k, (FLOOR_Y + 8) * k], fill=(236, 242, 246))
    for row in range(5):
        for col in range(10):
            x0, y0 = col * 120 - 40, FLOOR_Y + 8 + row * 100
            c = FLOOR_A if (row + col) % 2 else FLOOR_B
            d.rectangle([x0 * k, y0 * k, (x0 + 120) * k, (y0 + 100) * k], fill=c)
    return grain(img.resize((W, H), Image.LANCZOS), 0.03)


def _mirror():
    c = Cut(280, 420)
    frame = (250, 196, 86)
    c.rrect(0, 0, 280, 420, 140, frame)
    c.rrect(20, 20, 260, 400, 120, (212, 238, 248), sil=False)
    c.rrect(20, 300, 260, 400, 40, (198, 230, 244), sil=False)
    for (x0, y0, w, hgt) in ((70, 120, 34, 150), (128, 110, 16, 110)):
        c.polygon([(x0, y0 + hgt), (x0 + w, y0 + hgt - 40), (x0 + w + 60, y0 - 30), (x0 + 60, y0 + 10)],
                  (250, 253, 255), sil=False)
    for i in range(8):                       # little studs on the frame
        a = math.pi + i * math.pi / 7
        c.ellipse(140 + 130 * math.cos(a), 140 + 130 * math.sin(a), 5, 5, (255, 232, 160), sil=False)
    return c.finish(pivot=(140, 210), border=6)


def _porthole():
    c = Cut(220, 220)
    c.ellipse(110, 110, 106, 106, (252, 249, 240))
    c.ellipse(110, 110, 84, 84, (156, 212, 246), sil=False)
    c.ellipse(140, 80, 24, 24, (255, 210, 70), sil=False)
    for cx, cy, r in ((70, 120, 22), (94, 110, 28), (122, 124, 20)):
        c.ellipse(cx, cy, r, r * 0.85, (255, 255, 255), sil=False)
    c.line([(26, 110), (194, 110)], 8, (252, 249, 240))
    c.line([(110, 26), (110, 194)], 8, (252, 249, 240))
    return c.finish(pivot=(110, 110), border=6)


def _shelf():
    c = Cut(260, 230)
    c.rrect(0, 196, 260, 222, 8, (214, 160, 108))
    # potted plant
    for i, (dx, ang) in enumerate(((-26, -24), (0, 0), (26, 22), (-12, -8))):
        c.ellipse(70 + dx, 104 + abs(dx) * 0.5, 17, 56, (96, 176, 110) if i % 2 else (78, 156, 96), theta=ang)
    c.polygon([(36, 140), (104, 140), (96, 198), (44, 198)], (110, 190, 222))
    c.rrect(30, 132, 110, 150, 6, (130, 204, 232))
    # toothbrush cup with a lilac and a caramel toothbrush
    c.rrect(170, 50, 184, 160, 6, (226, 214, 242))
    c.rrect(166, 36, 188, 66, 6, (255, 255, 255))
    c.rrect(196, 60, 210, 160, 6, (198, 134, 80))
    c.rrect(192, 46, 214, 76, 6, (255, 255, 255))
    c.rrect(156, 120, 226, 198, 16, (255, 214, 64))
    c.ellipse(191, 158, 12, 12, (255, 236, 150), sil=False)
    return c.finish(pivot=(0, 0), border=5)


def background():
    bg = _wall()
    place(bg, _porthole(), (170, 330))
    place(bg, _shelf(), (800, 300))
    place(bg, _mirror(), (540, 700))
    place(bg, towel_ring(), (545, 1110))
    return bg


# ---------------------------------------------------------------- counter (drawn in FRONT of the characters)
BASIN_X = {"snip": 330, "crinkle": 765}


def counter():
    w, h = 900, 380
    c = Cut(w, h)
    c.rrect(0, 0, w, 58, 16, TOP)                              # surface band
    c.rrect(0, 44, w, 64, 6, TOP_EDGE)                         # front lip
    c.rrect(14, 62, w - 14, h - 26, 6, CAB)                    # cabinet front
    c.rrect(30, h - 34, w - 30, h, 6, CAB_DARK)                # toe kick
    for x0 in (40, 250, 470, 680):                             # door panels
        c.rrect(x0, 90, x0 + 180, h - 56, 22, CAB_PANEL, sil=False)
        c.rrect(x0 + 16, 106, x0 + 164, h - 72, 16, CAB, sil=False)
    for x in (214, 278, 646, 710):
        c.ellipse(x, 210, 11, 11, (255, 220, 120), sil=False)
        c.ellipse(x - 3, 207, 4, 4, (255, 244, 200), sil=False)
    for who in ("snip", "crinkle"):                            # basins set into the surface
        bx = BASIN_X[who] - COUNTER_X
        c.ellipse(bx, 26, 80, 19, (255, 255, 255), sil=False)
        c.ellipse(bx, 28, 68, 13, BASIN_IN, sil=False)
        c.ellipse(bx, 33, 60, 8, (168, 196, 214), sil=False)
        c.ellipse(bx, 31, 8, 3, CHROME_DARK, sil=False)
    return c.finish(pivot=(0, 0), border=5)


def faucet(post_h=150, flip=False):
    """Arched faucet. Post at the outer side, spout arcing in to a nozzle over the basin centre.
    Pivot = the nozzle mouth (where the water starts)."""
    w = 130
    hh = post_h + 70
    c = Cut(w, hh)
    base_y = hh - 12
    px, nx = 30, 100
    top = base_y - post_h
    c.ellipse(px, base_y, 28, 10, CHROME_DARK)
    c.rrect(px - 13, top + 30, px + 13, base_y, 10, CHROME)
    arc = [(65 - 35 * math.cos(math.pi * i / 24), top + 32 - 32 * math.sin(math.pi * i / 24)) for i in range(25)]
    c.line(arc, 24, CHROME, sil=True)
    c.rrect(nx - 13, top + 26, nx + 13, top + 52, 8, CHROME)
    c.ellipse(nx, top + 52, 10, 4, (96, 112, 130), sil=False)
    c.line([(px - 5, top + 40), (px - 5, base_y - 8)], 4, CHROME_HI)
    c.line([(p[0] - 1, p[1] - 6) for p in arc[3:20]], 4, CHROME_HI)
    spr = c.finish(pivot=(nx, top + 54), border=5)
    if flip:
        img = spr.img.transpose(Image.FLIP_LEFT_RIGHT)
        sh = spr.shadow.transpose(Image.FLIP_LEFT_RIGHT)
        spr = Sprite(img, (img.width - spr.pivot[0], spr.pivot[1]), sh)
    return spr


def lever():
    """Round tap handle on the counter (a cross handle that turns). Pivot = centre."""
    c = Cut(84, 84)
    c.rrect(32, 4, 52, 80, 9, (250, 252, 255))
    c.rrect(4, 32, 80, 52, 9, (250, 252, 255))
    c.ellipse(42, 42, 19, 19, CHROME)
    c.ellipse(42, 42, 9, 9, (90, 170, 236), sil=False)
    return c.finish(pivot=(42, 42), border=4)


def lever_base():
    c = Cut(90, 30)
    c.ellipse(45, 15, 40, 11, CHROME_DARK)
    return c.finish(pivot=(45, 15), border=4)


def water_frames(length, n=8):
    frames = []
    for i in range(n):
        ph = i / n
        c = Cut(60, int(length) + 30)
        c.rrect(18, 0, 42, length, 12, WATER, sil=True)
        y = -40 + 40 * ph
        while y < length:
            pts = [(30 + 6 * math.sin((yy - y) / 9), yy) for yy in range(int(max(4, y)), int(min(length - 6, y + 22)), 3)]
            if len(pts) > 1:
                c.line(pts, 4, WATER_HI)
            y += 40
        frames.append(c.finish(pivot=(30, 0), border=3, shadow_alpha=0.16))
    return frames


def splash():
    c = Cut(170, 80)
    for (x, y, r) in ((30, 50, 9), (52, 28, 7), (85, 18, 8), (118, 28, 7), (140, 50, 9), (70, 56, 6), (102, 58, 6)):
        c.ellipse(x, y, r, r * 1.2, WATER)
        c.ellipse(x - r * 0.3, y - r * 0.4, r * 0.3, r * 0.3, WATER_HI, sil=False)
    return c.finish(pivot=(85, 50), border=3, shadow_alpha=0.15)


def drip(color=WATER):
    c = Cut(30, 40)
    c.polygon([(15, 2), (24, 22), (6, 22)], color)
    c.ellipse(15, 25, 10, 11, color)
    return c.finish(pivot=(15, 20), border=3, shadow_alpha=0.15)


# ---------------------------------------------------------------- apples, plate
def _apple_into(c, cx, cy, s=1.0, bites=0, shine=True):
    r = 34 * s
    c.ellipse(cx - 13 * s, cy, r * 0.82, r * 0.95, APPLE)
    c.ellipse(cx + 13 * s, cy, r * 0.82, r * 0.95, APPLE)
    c.ellipse(cx, cy + 6 * s, r * 0.9, r * 0.82, APPLE)
    c.ellipse(cx + 18 * s, cy + 10 * s, r * 0.45, r * 0.55, APPLE_DARK, sil=False)
    c.ellipse(cx + 13 * s, cy + 6 * s, r * 0.55, r * 0.7, APPLE, sil=False)
    if shine:
        c.ellipse(cx - 18 * s, cy - 10 * s, 7 * s, 11 * s, (255, 168, 160), sil=False, theta=20)
    c.line([(cx, cy - r * 0.78), (cx + 3 * s, cy - r * 1.25)], 6 * s, STEM, sil=True)
    c.ellipse(cx + 16 * s, cy - r * 1.12, 15 * s, 7 * s, LEAF, sil=True, theta=-28)
    if bites:
        bite_centres = [(cx + 30 * s, cy - 16 * s), (cx + 34 * s, cy + 12 * s)][:bites]
        _bite(c, bite_centres, 15 * s)


def _bite(c, centres, r):
    """Scalloped bite: cream flesh rim inside the apple, then cut the notch out of the paper."""
    flesh = Image.new("L", c.mask.size, 0)
    fd = ImageDraw.Draw(flesh)
    for (x, y) in centres:
        for dx, dy in ((0, 0), (0, -r * 0.8), (0, r * 0.8)):
            rr = (r + 7) * SS
            fd.ellipse([(x + dx) * SS - rr, (y + dy) * SS - rr, (x + dx) * SS + rr, (y + dy) * SS + rr], fill=255)
    flesh = Image.fromarray((np.asarray(flesh, np.float32) * np.asarray(c.mask, np.float32) / 255).astype(np.uint8))
    c.img.paste(APPLE_FLESH + (255,), (0, 0), flesh)
    for (x, y) in centres:
        for dx, dy in ((0, 0), (0, -r * 0.8), (0, r * 0.8)):
            rr = r * 0.62 * SS if dy else r * SS
            box = [(x + dx) * SS - rr, (y + dy) * SS - rr, (x + dx) * SS + rr, (y + dy) * SS + rr]
            c.d.ellipse(box, fill=(0, 0, 0, 0))
            c.m.ellipse(box, fill=0)


def apple(bites=0):
    c = Cut(100, 110)
    _apple_into(c, 48, 62, 1.0, bites)
    return c.finish(pivot=(48, 62), border=5)


def apple_glint():
    c = Cut(60, 60)
    c.polygon(star_pts(30, 30, 28, 7, 4, -90), (255, 255, 255))
    return c.finish(pivot=(30, 30), border=0, shadow_alpha=0.0)


def plate():
    c = Cut(180, 44)
    c.ellipse(90, 22, 88, 18, (255, 255, 255))
    c.ellipse(90, 20, 70, 11, (240, 244, 248), sil=False)
    c.arc(90, 22, 82, 15, 15, 165, 4, (120, 186, 232))
    return c.finish(pivot=(90, 22), border=4)


# ---------------------------------------------------------------- soap, towel, foam, bubbles
def soap_bar():
    c = Cut(100, 70)
    c.rrect(6, 14, 94, 64, 20, SOAP)
    c.rrect(18, 20, 82, 34, 8, SOAP_HI, sil=False)
    for (x, y, r) in ((30, 12, 8), (46, 6, 6), (62, 11, 7)):
        c.ellipse(x, y, r, r, (248, 252, 255))
    return c.finish(pivot=(50, 40), border=5)


def soap_dish():
    c = Cut(130, 40)
    c.ellipse(65, 22, 62, 15, (126, 204, 226))
    c.ellipse(65, 19, 50, 9, (160, 222, 238), sil=False)
    return c.finish(pivot=(65, 20), border=4)


def towel_ring():
    c = Cut(90, 70)
    c.ellipse(45, 10, 14, 9, CHROME_DARK)
    c.arc(45, 40, 30, 26, 0, 360, 7, CHROME)
    return c.finish(pivot=(45, 10), border=4)


def towel_hanging():
    """Hand towel hanging over the ring. Pivot = top centre (the ring)."""
    c = Cut(140, 190)
    c.rrect(14, 6, 126, 178, 18, TOWEL)
    for y in (122, 140):
        c.rrect(14, y, 126, y + 10, 2, TOWEL_STRIPE, sil=False)
    for x in range(22, 122, 13):
        c.line([(x, 174), (x, 186)], 5, TOWEL, sil=True)
    c.rrect(30, 6, 110, 20, 8, (255, 226, 140), sil=False)
    return c.finish(pivot=(70, 8), border=5)


def foam():
    c = Cut(220, 170)
    rng = np.random.default_rng(5)
    blobs = [(110, 90, 52), (64, 98, 40), (156, 98, 40), (90, 54, 36), (136, 56, 34), (110, 120, 40),
             (42, 70, 26), (178, 70, 26), (110, 28, 24)]
    for (x, y, r) in blobs:
        c.ellipse(x + 3, y + 4, r, r * 0.95, (222, 238, 252))
    for (x, y, r) in blobs:
        c.ellipse(x, y, r * 0.9, r * 0.86, (255, 255, 255), sil=False)
    for _ in range(9):
        x, y, r = rng.uniform(40, 180), rng.uniform(30, 130), rng.uniform(5, 11)
        c.arc(x, y, r, r, 0, 360, 2.5, (176, 214, 240))
        c.ellipse(x - r * 0.35, y - r * 0.35, r * 0.25, r * 0.25, (176, 214, 240), sil=False)
    return c.finish(pivot=(110, 90), border=4, shadow_alpha=0.18)


def bubble(r=26, ring_only=False):
    c = Cut(int(2 * r + 12), int(2 * r + 12))
    cx = cy = r + 6
    if ring_only:
        c.arc(cx, cy, r, r, 0, 360, 4, (150, 204, 236))
        c.line([(cx - r * 0.75 + 3 * math.cos(a), cy - r * 0.1 - r * 0.6 * math.sin(a)) for a in
                np.linspace(0.2, 1.4, 8)], 1, (255, 255, 255))
        pts = [(cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a)) for a in np.linspace(3.5, 4.6, 8)]
        c.line(pts, max(3, r * 0.12), (255, 255, 255), sil=True)
        c.arc(cx, cy, r - 4, r - 4, 20, 70, 3, (236, 170, 226))
        return c.finish(pivot=(cx, cy), border=2, shadow_alpha=0.12)
    c.ellipse(cx, cy, r, r, (232, 246, 255))
    c.arc(cx, cy, r, r, 0, 360, 3, (164, 212, 240))
    c.arc(cx, cy, r - 5, r - 5, 20, 80, 3, (236, 176, 228))
    c.ellipse(cx - r * 0.38, cy - r * 0.38, r * 0.22, r * 0.16, (255, 255, 255), sil=False, theta=-40)
    return c.finish(pivot=(cx, cy), border=3, shadow_alpha=0.15)


# ---------------------------------------------------------------- germs (friendly!)
GERM_COLORS = ((150, 214, 88), (102, 202, 150), (188, 216, 70))


def germ(color, mood="smile", wave=0, seed=0):
    """Round, smiley green blob with tiny arms. mood: smile | gasp | giggle | worried.
    wave: 0 = arms down, 1 = left arm up, 2 = right arm up, 3 = both up."""
    c = Cut(96, 90)
    cx, cy = 48, 48
    bumps = 6 + seed % 3
    pts = [(cx + (25 + 3.2 * math.sin(bumps * a + seed)) * math.cos(a),
            cy + (23 + 3.2 * math.sin(bumps * a + seed)) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 64)]
    left_up = wave in (1, 3)
    right_up = wave in (2, 3)
    c.ellipse(cx - 30, cy - 14 if left_up else cy + 8, 6, 11, color, theta=35 if left_up else -30)
    c.ellipse(cx + 30, cy - 14 if right_up else cy + 8, 6, 11, color, theta=-35 if right_up else 30)
    c.polygon(pts, color)
    hi = tuple(min(255, v + 40) for v in color)
    c.ellipse(cx - 9, cy - 13, 6, 3, hi, sil=False, theta=-20)
    for ex in (-9, 9):
        if mood == "giggle":
            c.arc(cx + ex, cy - 2, 6, 5, 200, 340, 3, EYE)
        else:
            big = 1.25 if mood == "gasp" else 1.0
            c.ellipse(cx + ex, cy - 3, 7 * big, 8 * big, (255, 255, 255), sil=False)
            c.ellipse(cx + ex + 1, cy - 2, 4 * big, 5 * big, EYE, sil=False)
            c.ellipse(cx + ex + 2.5, cy - 4.5, 1.6, 1.6, (255, 255, 255), sil=False)
    if mood == "gasp":
        c.ellipse(cx, cy + 11, 5, 6, (110, 40, 60), sil=False)
    elif mood == "worried":
        c.line([(cx - 7, cy + 12), (cx - 2, cy + 9), (cx + 3, cy + 12), (cx + 7, cy + 9)], 2.5, EYE)
    elif mood == "giggle":
        c.chord(cx, cy + 6, 9, 9, 0, 180, (110, 40, 60))
    else:
        c.arc(cx, cy + 5, 8, 6, 20, 160, 3, EYE)
    c.ellipse(cx - 15, cy + 7, 4, 2.5, (250, 160, 170), sil=False)
    c.ellipse(cx + 15, cy + 7, 4, 2.5, (250, 160, 170), sil=False)
    return c.finish(pivot=(cx, cy), border=3, shadow_alpha=0.22)


# ---------------------------------------------------------------- mud on Snip's paws
def mud_overlay(variant=0, mirror=False):
    """Brown paper mud spots shaped to fit Snip's arm cut-out (same canvas and pivot as characters.snip_arm),
    so it can be placed exactly like the arm: same shoulder point, same angle."""
    c = Cut(60, 150)
    spots = (((22, 116, 10, 8), (38, 130, 10, 8), (31, 101, 6, 5), (18, 135, 5, 4), (42, 112, 5, 5)),
             ((36, 118, 10, 8), (22, 130, 10, 8), (29, 102, 6, 5), (42, 136, 5, 4), (17, 112, 5, 5)))[variant]
    for (x, y, rx, ry) in spots:
        pts = [(x + rx * (1 + 0.18 * math.sin(5 * a + x)) * math.cos(a), y + ry * (1 + 0.18 * math.sin(5 * a + y)) * math.sin(a))
               for a in np.linspace(0, 2 * math.pi, 28)]
        c.polygon(pts, MUD)
        c.ellipse(x - rx * 0.3, y - ry * 0.3, rx * 0.3, ry * 0.25, (160, 116, 76), sil=False)
    spr = c.finish(pivot=(30, 26), border=2, shadow_alpha=0.12, shadow_blur=2)
    if mirror:
        img = spr.img.transpose(Image.FLIP_LEFT_RIGHT)
        sh = spr.shadow.transpose(Image.FLIP_LEFT_RIGHT)
        spr = Sprite(img, (img.width - spr.pivot[0], spr.pivot[1]), sh)
    return spr


# ---------------------------------------------------------------- choice bubbles (no emoji: paper drawings)
def _paw(c, x0, y0, x1, y1, ang_pts=None):
    c.line([(x0, y0), (x1, y1)], 44, SNIP_FUR, sil=False)


def choice_muddy(ring=(240, 110, 100)):
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    _apple_into(c, 150, 150, 1.12)
    c.line([(52, 70), (100, 118)], 46, SNIP_FUR)               # lilac paw reaching for the apple
    c.rrect(30, 40, 72, 82, 16, (80, 182, 235), sil=False)     # blue sleeve (Snip's tee)
    for (x, y, r) in ((84, 104, 9), (102, 118, 7), (70, 92, 6)):
        c.ellipse(x, y, r, r * 0.85, MUD, sil=False)
    gx, gy = 106, 84                                           # a tiny germ on the paw
    pts = [(gx + (13 + 1.8 * math.sin(6 * a)) * math.cos(a), gy + (12 + 1.8 * math.sin(6 * a)) * math.sin(a))
           for a in np.linspace(0, 2 * math.pi, 40)]
    c.polygon(pts, GERM_COLORS[0], sil=False)
    for ex in (-4, 4):
        c.ellipse(gx + ex, gy - 2, 3.4, 3.8, (255, 255, 255), sil=False)
        c.ellipse(gx + ex + 0.6, gy - 1.5, 1.9, 2.3, EYE, sil=False)
    c.arc(gx, gy + 3, 4, 3, 20, 160, 1.6, EYE)
    return c.finish(pivot=(125, 125), border=7)


def choice_soap(ring=(90, 190, 120)):
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    c.rrect(66, 126, 184, 186, 24, SOAP, sil=False)
    c.rrect(82, 134, 168, 150, 8, SOAP_HI, sil=False)
    for (x, y, r) in ((92, 104, 22), (132, 92, 28), (168, 112, 18), (110, 62, 14), (158, 60, 11)):
        c.ellipse(x, y, r, r, (232, 246, 255), sil=False)
        c.arc(x, y, r, r, 0, 360, 3, (150, 204, 236))
        c.ellipse(x - r * 0.35, y - r * 0.38, r * 0.22, r * 0.16, (255, 255, 255), sil=False, theta=-40)
    return c.finish(pivot=(125, 125), border=7)


def shake_lines():
    c = Cut(120, 120)
    for k, r in enumerate((40, 54)):
        c.arc(60, 60, r, r, 200, 250, 6, (120, 110, 150))
        c.arc(60, 60, r, r, 20, 70, 6, (120, 110, 150))
    return c.finish(pivot=(60, 60), border=3, shadow_alpha=0.1)


def grown_up_arm_long():
    """Same grown-up as scene.grown_up_hand(), with a sleeve long enough to reach the counter from the
    top of the frame. Pivot = fingertips."""
    sleeve = (96, 128, 186)
    skin = (206, 150, 112)
    L = 1000
    c = Cut(230, L + 150)
    c.rrect(45, 0, 185, L, 26, sleeve)
    c.rrect(36, L - 40, 194, L + 12, 16, (244, 244, 248))
    c.rrect(52, L - 4, 178, L + 90, 44, skin)
    for x in (70, 98, 126, 154):
        c.rrect(x - 14, L + 50, x + 14, L + 130, 14, skin)
    for x in (84, 112, 140):
        c.line([(x, L + 70), (x, L + 120)], 3, (182, 126, 92))
    c.polygon([(40 + 18 * math.cos(a), L + 50 + 46 * math.sin(a)) for a in [i * math.pi / 18 for i in range(36)]],
              skin)
    return c.finish(pivot=(115, L + 118))


def sparkle_small(color=(255, 255, 255)):
    c = Cut(70, 70)
    c.polygon(star_pts(35, 35, 32, 8, 4, -90), color)
    return c.finish(pivot=(35, 35), border=3, shadow_alpha=0.12)


def mini_heart(color, size=60):
    c = Cut(size + 20, size + 20)
    c.polygon(heart_pts((size + 20) / 2, (size + 20) / 2 + 3, size), color)
    return c.finish(pivot=((size + 20) / 2, (size + 20) / 2), border=4)


# ---------------------------------------------------------------- drawing helpers
def place_clipped(base, spr, at, angle=0.0, scale=1.0, y_max=None, shadow_from=None, alpha=1.0):
    """Like paperlib.place, but nothing is drawn below y_max, and the drop shadow is only drawn from
    y = shadow_from down (used to redraw arms in front of the counter without doubling their shadow)."""
    if alpha <= 0.003:
        return
    if spr.shadow is not None and shadow_from is not None:
        sh, px, py = _transform(spr.shadow, spr.pivot, angle, scale, scale, alpha)
        x0, y0 = at[0] - px + SHADOW_OFFSET[0], at[1] - py + SHADOW_OFFSET[1]
        top = max(0, int(round(shadow_from - y0)))
        bot = sh.height if y_max is None else min(sh.height, int(round(y_max - y0)))
        if bot > top:
            _composite_clipped(base, sh.crop((0, top, sh.width, bot)), x0, y0 + top)
    img, px, py = _transform(spr.img, spr.pivot, angle, scale, scale, alpha)
    x0, y0 = at[0] - px, at[1] - py
    bot = img.height if y_max is None else min(img.height, int(round(y_max - y0)))
    if bot > 0:
        _composite_clipped(base, img.crop((0, 0, img.width, bot)) if bot < img.height else img, x0, y0)


# ---------------------------------------------------------------- sounds (all synthesized)
SR = A.SR
_rng = np.random.default_rng(31)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def water_run(dur, vel=1.0):
    """Running tap: bright filtered noise with a gentle bubbly flutter. Fades in and out."""
    t = _t(dur)
    n = _rng.normal(0, 1, len(t))
    y = _lp(n, 4) - _lp(n, 22)
    flutter = 0.75 + 0.25 * np.sin(2 * np.pi * 7.3 * t) * np.sin(2 * np.pi * 1.7 * t + 1)
    env = np.minimum(1, t / 0.06) * np.minimum(1, (dur - t) / 0.12)
    bub = np.zeros(len(t))
    for k in range(int(dur * 9)):
        s = int(_rng.uniform(0, max(0.01, dur - 0.08)) * SR)
        tt = _t(0.05)
        f = _rng.uniform(700, 1300) * (1 + 3 * tt)
        g = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 70)
        bub[s:s + len(g)] += 0.08 * g[:len(bub) - s]
    return vel * env * (0.55 * flutter * y + bub)


def squish(vel=1.0):
    t = _t(0.28)
    n = _rng.normal(0, 1, len(t))
    y = _lp(n, 14) - _lp(n, 60)
    wob = 0.6 + 0.4 * np.sin(2 * np.pi * (18 - 30 * t) * t)
    f = 260 + 220 * np.exp(-t * 12)
    tone = 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR)
    return vel * 1.4 * np.sin(np.pi * t / 0.28) ** 1.5 * (wob * y + tone)


def giggle(vel=1.0, base=1250):
    """Tiny high 'hee-hee-hee' (three squeaky chirps)."""
    out = np.zeros(int(0.5 * SR))
    for i in range(3):
        t = _t(0.085)
        f = base * (1 + 0.05 * i) * (1 + 0.18 * np.sin(np.pi * t / 0.085)) * (1 + 0.02 * np.sin(2 * np.pi * 38 * t))
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = np.sin(ph) + 0.3 * np.sin(2 * ph)
        env = np.sin(np.pi * t / 0.085) ** 1.2
        s = int(i * 0.12 * SR)
        out[s:s + len(t)] += vel * 0.45 * env * y
    return out


def gasp(vel=1.0):
    t = _t(0.16)
    f = 700 + 900 * t / 0.16
    return vel * 0.45 * np.sin(np.pi * t / 0.16) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def crunch(vel=1.0):
    out = np.zeros(int(0.35 * SR))
    for i, (d, g) in enumerate(((0.0, 1.0), (0.045, 0.8), (0.08, 0.9), (0.13, 0.6), (0.17, 0.5))):
        t = _t(0.05)
        n = _rng.normal(0, 1, len(t))
        n = n - _lp(n, 3)
        s = int(d * SR)
        out[s:s + len(t)] += g * np.exp(-t * 90) * n
    t = _t(0.12)
    out[:len(t)] += 0.5 * np.exp(-t * 40) * np.sin(2 * np.pi * 120 * t)
    return vel * 0.9 * out


def splash(vel=1.0):
    t = _t(0.6)
    n = _rng.normal(0, 1, len(t))
    y = _lp(n, 3) - _lp(n, 30)
    f = 520 * np.exp(-t * 5) + 160
    bloop = 0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return vel * (0.9 * np.exp(-t * 6) * A._attack(t, 800) * y + bloop)


def fluff(dur=0.5, vel=1.0):
    t = _t(dur)
    n = _rng.normal(0, 1, len(t))
    y = _lp(n, 10) - _lp(n, 80)
    trem = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 6 * t))
    return vel * 1.3 * np.sin(np.pi * t / dur) * trem * y


def squeak(vel=1.0, up=True):
    t = _t(0.13)
    f0, f1 = (900, 1500) if up else (1500, 900)
    f = (f0 + (f1 - f0) * t / 0.13) * (1 + 0.03 * np.sin(2 * np.pi * 45 * t))
    return vel * 0.35 * np.sin(np.pi * t / 0.13) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def bubble_pop(vel=1.0, base=900):
    t = _t(0.07)
    f = base + 9000 * t
    return vel * np.exp(-t * 60) * A._attack(t, 4000) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def plip(vel=1.0):
    t = _t(0.12)
    f = 1500 * np.exp(-t * 10) + 500
    return vel * 0.5 * np.exp(-t * 30) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def rattle(dur=0.5, vel=1.0, rate=14):
    out = np.zeros(int((dur + 0.15) * SR))
    k = 0
    while k / rate < dur:
        s = int(k / rate * SR)
        h = A.shaker(0.8 + 0.2 * (k % 2))
        out[s:s + len(h)] += h
        k += 1
    return vel * 2.2 * out
