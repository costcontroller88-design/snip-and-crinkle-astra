"""Beach setting, sun-safety props, noodle ears and extra sounds for Episode 10 ("Hot Sunny Day?").

Everything is a hand-made paper cut-out (paperlib.Cut) or synthesized sound (numpy), in the same
style as the shared modules, which are only imported, never edited.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import audio as A  # noqa: E402
from characters import (BLINKABLE, EYE, SNIP_EAR_BASE, SNIP_EAR_TILT, SNIP_FACE_CENTER,  # noqa: E402
                        SNIP_FACE_PIVOT, Character)
from characters import SNIP as SNIP_COL  # noqa: E402
from paperlib import Cut, grain, place, rot, star_pts  # noqa: E402

W, H = 1080, 1920
GROUND_Y = 1440          # where everyone stands
HORIZON_Y = 930
SHORE_Y = 1236           # where the sea meets the wet sand

SKY_TOP = (92, 186, 240)
SKY_LOW = (206, 238, 250)
SEA_FAR = (52, 150, 206)
SEA_MID = (70, 182, 216)
SEA_NEAR = (120, 214, 220)
FOAM = (250, 254, 255)
SAND = (248, 220, 160)
SAND_LIGHT = (252, 234, 190)
SAND_DOT = (232, 196, 132)
WET_SAND = (228, 196, 140)
CASTLE = (234, 192, 118)
CASTLE_DARK = (210, 164, 92)
CASTLE_LIGHT = (246, 214, 150)
STRAW = (250, 216, 120)
STRAW_DARK = (226, 184, 86)
UMB_RED = (240, 92, 92)
UMB_CREAM = (255, 246, 226)
BOTTLE = (150, 206, 244)
WATER = (64, 150, 230)
LOLLY_TOP = (255, 140, 52)       # orange tip (drips show up on Snip's pink nose)
LOLLY_MID = (255, 210, 80)
LOLLY_BOT = (246, 96, 132)
STICK = (226, 186, 128)
SHADE = (150, 112, 70)


# ================================================================ background
def _sky():
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / (HORIZON_Y / H), 0, 1) ** 1.4
    top, low = np.array(SKY_TOP, np.float32), np.array(SKY_LOW, np.float32)
    rgb = top[None, None, :] * (1 - k[..., None]) + low[None, None, :] * k[..., None]
    rgb = np.repeat(rgb, W, axis=1)
    a = np.full((H, W, 1), 255, np.float32)
    img = Image.fromarray(np.concatenate([rgb, a], axis=2).clip(0, 255).astype(np.uint8), "RGBA")
    return grain(img, 0.03)


def _sea():
    c = Cut(1140, 420)
    c.rrect(0, 0, 1140, 420, 0, SEA_FAR)
    for i, (y0, col) in enumerate(((70, SEA_MID), (170, (96, 200, 222)), (250, SEA_NEAR))):
        top = [(x, y0 + 7 * math.sin(x / 55 + i * 1.7) + 4 * math.sin(x / 23 + i)) for x in range(0, 1141, 10)]
        c.polygon([(0, 420)] + top + [(1140, 420)], col, sil=False)
    for x, y, w in ((140, 40, 70), (520, 26, 90), (860, 50, 60), (330, 120, 80), (720, 140, 70), (980, 110, 60)):
        c.line([(x - w / 2, y), (x - w / 6, y - 6), (x + w / 6, y), (x + w / 2, y - 6)], 5, (200, 236, 246))
    return c.finish(pivot=(30, 0), border=0, shadow_alpha=0.0)


def _beach():
    c = Cut(1160, 720)
    top = [(x, 40 + 6 * math.sin(x / 80) + 4 * math.sin(x / 31)) for x in range(0, 1161, 10)]
    c.polygon([(0, 720)] + top + [(1160, 720)], WET_SAND)
    dry = [(x, 96 + 10 * math.sin(x / 90 + 1) + 5 * math.sin(x / 37)) for x in range(0, 1161, 10)]
    c.polygon([(0, 720)] + dry + [(1160, 720)], SAND, sil=False)
    for cx, cy, rx, ry in ((220, 250, 280, 40), (860, 330, 300, 46), (420, 520, 380, 56), (980, 600, 230, 40)):
        c.ellipse(cx, cy, rx, ry, SAND_LIGHT, sil=False)
    rng = np.random.default_rng(10)
    for _ in range(170):                                                     # soft sand speckles
        x, y = rng.uniform(10, 1150), rng.uniform(120, 710)
        r = rng.uniform(2.0, 4.2)
        c.ellipse(x, y, r, r * 0.8, SAND_DOT, sil=False)
    return c.finish(pivot=(40, 0), border=4, shadow_alpha=0.12)


def _shell(c, x, y, s, col, dark):
    """A scallop shell, fan opening upward."""
    pts = [(x, y + 6 * s)]
    for i in range(13):
        a = math.radians(200 + i * 140 / 12)
        r = 30 * s * (1 + 0.08 * (i % 2))
        pts.append((x + r * math.cos(a), y + 4 * s + r * math.sin(a)))
    c.polygon(pts, col)
    for a in (-60, -30, 0, 30, 60):
        e = rot(0, -26 * s, a)
        c.line([(x, y + 4 * s), (x + e[0], y + 4 * s + e[1])], 2.4 * s, dark)
    c.rrect(x - 9 * s, y + 2 * s, x + 9 * s, y + 10 * s, 3 * s, dark)


def _starfish(c, x, y, s, rot_deg=-90):
    c.polygon(star_pts(x, y, 34 * s, 15 * s, 5, rot_deg), (255, 150, 92))
    for i in range(5):
        a = math.radians(rot_deg + i * 72)
        for d in (10, 20):
            c.ellipse(x + d * s * math.cos(a), y + d * s * math.sin(a), 2.6 * s, 2.6 * s, (255, 214, 170), sil=False)


def _spiral(c, x, y, s):
    c.ellipse(x, y, 20 * s, 14 * s, (246, 232, 214), theta=-20)
    c.polygon([(x + 12 * s, y - 8 * s), (x + 40 * s, y - 2 * s), (x + 14 * s, y + 10 * s)], (246, 232, 214))
    c.arc(x - 2 * s, y, 11 * s, 8 * s, 0, 330, 2.6 * s, (214, 180, 150))


def _shells_front():
    c = Cut(1080, 380)
    _shell(c, 90, 150, 1.25, (255, 182, 196), (232, 132, 156))
    _starfish(c, 300, 250, 1.2, -80)
    _spiral(c, 520, 120, 1.2)
    _shell(c, 700, 260, 1.0, (255, 226, 160), (226, 180, 104))
    _shell(c, 890, 120, 1.15, (196, 214, 255), (140, 160, 226))
    _starfish(c, 1010, 290, 0.9, -100)
    _spiral(c, 170, 320, 0.9)
    return c.finish(pivot=(0, 0), border=4, shadow_alpha=0.2)


def _bucket():
    c = Cut(170, 190)
    blue, dark = (72, 170, 236), (48, 132, 200)
    c.arc(85, 66, 62, 56, 180, 360, 6, (60, 70, 90))
    c.polygon([(20, 60), (150, 60), (132, 182), (38, 182)], blue)
    c.rrect(12, 52, 158, 74, 9, dark)
    c.polygon(star_pts(85, 124, 28, 12), (255, 214, 64), sil=False)
    return c.finish(pivot=(85, 182), border=5)


def background():
    """Static beach layers. Sun, clouds, sea ripples, the swash and the boat are drawn per frame."""
    bg = _sky()
    place(bg, _sea(), (0, HORIZON_Y))
    place(bg, _beach(), (0, SHORE_Y - 40))
    place(bg, _bucket(), (880, GROUND_Y + 12))
    place(bg, _shells_front(), (0, 1560))
    return bg


def sun():
    """A big friendly paper sun (smiling face; rays have 12-fold symmetry so a 30 deg turn loops)."""
    c = Cut(420, 420)
    for i in range(12):
        a = math.radians(i * 30)
        tip = (210 + 196 * math.cos(a), 210 + 196 * math.sin(a))
        l = (210 + 130 * math.cos(a - 0.15), 210 + 130 * math.sin(a - 0.15))
        r = (210 + 130 * math.cos(a + 0.15), 210 + 130 * math.sin(a + 0.15))
        c.polygon([l, tip, r], (255, 184, 52))
    c.ellipse(210, 210, 128, 128, (255, 210, 64))
    c.ellipse(210, 210, 104, 104, (255, 228, 112), sil=False)
    for x in (172, 248):                                   # happy closed eyes
        c.arc(x, 204, 17, 14, 200, 340, 6, (196, 120, 40))
    c.arc(210, 222, 34, 26, 20, 160, 6, (196, 120, 40))
    for x in (152, 268):
        c.ellipse(x, 236, 16, 10, (255, 170, 100), sil=False)
    return c.finish(pivot=(210, 210), border=6, shadow_alpha=0.12)


def cloud(w=280, h=120):
    c = Cut(w, h)
    for fx, fy, fr in ((0.25, 0.62, 0.36), (0.45, 0.42, 0.5), (0.68, 0.5, 0.42), (0.84, 0.66, 0.3), (0.5, 0.72, 0.32)):
        c.ellipse(w * fx, h * fy, h * fr * 1.15, h * fr, (255, 255, 255))
    return c.finish(pivot=(w / 2, h / 2), border=4, shadow_alpha=0.12)


def ripple_band(seed, n=7, y=26, col=(214, 242, 250)):
    c = Cut(1400, 60)
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = 80 + i * 1240 / n + rng.uniform(-40, 40)
        w = rng.uniform(70, 120)
        c.line([(x - w / 2, y), (x - w / 6, y - 8), (x + w / 6, y), (x + w / 2, y - 8)], 6, col)
    return c.finish(pivot=(160, 30), border=0, shadow_alpha=0.0)


def swash():
    """The thin sheet of sea that slides up the wet sand, with a scalloped foam edge."""
    c = Cut(1240, 110)
    edge = [(x, 70 + 7 * math.sin(x / 34) + 5 * math.sin(x / 13)) for x in range(0, 1241, 8)]
    c.polygon([(0, 0)] + edge + [(1240, 0)], SEA_NEAR)
    c.line(edge, 10, FOAM)
    for x in range(30, 1240, 70):
        c.ellipse(x, 74 + 7 * math.sin(x / 34), 6, 5, FOAM)
    return c.finish(pivot=(80, 0), border=0, shadow_alpha=0.1)


def boat():
    c = Cut(150, 150)
    c.polygon([(20, 104), (130, 104), (112, 132), (38, 132)], (240, 108, 96))
    c.rrect(72, 14, 78, 106, 2, (120, 90, 70))
    c.polygon([(80, 18), (80, 96), (130, 96)], (255, 255, 255))
    c.polygon([(70, 30), (70, 96), (32, 96)], (255, 214, 72))
    return c.finish(pivot=(75, 120), border=4, shadow_alpha=0.12)


def heat_frames(n=16, h=150):
    """Wavy rising heat squiggles (like steam, warm and pale)."""
    frames = []
    for i in range(n):
        ph = 2 * math.pi * i / n
        c = Cut(60, h + 20)
        pts = [(30 + 11 * math.sin(2 * math.pi * y / 60 + ph) * (0.4 + 0.6 * (h - y) / h), y)
               for y in range(h, 10, -5)]
        c.line(pts, 9, (255, 240, 206), sil=True)
        frames.append(c.finish(pivot=(30, h + 4), border=3, shadow_alpha=0.1))
    return frames


def hot_mark():
    """Little 'hot!' zigzags that spring up under a hot paw."""
    c = Cut(130, 90)
    for dx, h in ((-34, 54), (0, 70), (34, 54)):
        x = 65 + dx
        c.line([(x, 84), (x - 7, 84 - h * 0.33), (x + 7, 84 - h * 0.66), (x, 84 - h)], 7, (255, 132, 64), sil=True)
    return c.finish(pivot=(65, 86), border=3, shadow_alpha=0.15)


def sand_bits():
    out = []
    for col, r in ((CASTLE, 9), (CASTLE_DARK, 7), (SAND_LIGHT, 8)):
        c = Cut(30, 30)
        c.ellipse(15, 15, r, r * 0.85, col)
        out.append(c.finish(pivot=(15, 15), border=2, shadow_alpha=0.15))
    return out


def puff():
    c = Cut(200, 110)
    for cx, cy, r in ((50, 70, 34), (96, 52, 44), (146, 68, 36), (100, 82, 30)):
        c.ellipse(cx, cy, r, r * 0.85, (252, 236, 200))
    return c.finish(pivot=(100, 100), border=4, shadow_alpha=0.12)


# ================================================================ sandcastle
def castle_base():
    c = Cut(360, 150)
    c.ellipse(180, 120, 172, 60, CASTLE)
    c.chord(180, 120, 172, 60, 0, 180, CASTLE_DARK, sil=False)
    c.ellipse(180, 104, 150, 42, CASTLE_LIGHT, sil=False)
    _shell(c, 96, 112, 0.5, (255, 182, 196), (232, 132, 156))
    _shell(c, 262, 116, 0.45, (196, 214, 255), (140, 160, 226))
    return c.finish(pivot=(180, 120), border=5)


def tower(w=120, h=150, door=True):
    """A bucket-shaped sand tower with crenellations. Pivot = bottom centre."""
    c = Cut(int(w + 30), int(h + 40))
    x0, x1 = 15, 15 + w
    top = 40
    c.polygon([(x0 + 8, top), (x1 - 8, top), (x1, h + 30), (x0, h + 30)], CASTLE)
    cw = (w - 16) / 5
    for i in range(0, 5, 2):
        cx0 = x0 + 8 + i * cw
        c.rrect(cx0, top - 26, cx0 + cw, top + 4, 4, CASTLE)
    c.rrect(x0 + 6, top - 2, x1 - 6, top + 10, 4, CASTLE_DARK, sil=False)
    for y in (top + 50, top + 92):
        if y < h + 10:
            c.line([(x0 + 10, y), (x1 - 10, y)], 3, CASTLE_DARK)
    if door:
        dx = (x0 + x1) / 2
        c.chord(dx, h + 30, w * 0.18, h * 0.32, 180, 360, (170, 122, 66), sil=False)
    else:
        c.ellipse((x0 + x1) / 2, top + 44, 9, 12, (170, 122, 66), sil=False)
    return c.finish(pivot=((x0 + x1) / 2, h + 30), border=5)


def flag():
    c = Cut(110, 180)
    c.rrect(14, 10, 24, 176, 4, STICK)
    c.polygon([(24, 14), (100, 38), (24, 64)], (240, 80, 90))
    c.polygon(star_pts(48, 39, 11, 5), (255, 230, 90), sil=False)
    return c.finish(pivot=(19, 170), border=4)


# ================================================================ held props
def spade():
    """Kids' plastic spade. Pivot = the grip (top of the handle); blade points down."""
    c = Cut(80, 220)
    c.rrect(26, 4, 54, 30, 10, (240, 96, 96))
    c.rrect(34, 20, 46, 140, 5, (240, 96, 96))
    c.polygon([(12, 136), (68, 136), (62, 196), (40, 214), (18, 196)], (255, 204, 64))
    c.line([(40, 146), (40, 196)], 4, (232, 170, 40))
    return c.finish(pivot=(40, 18), border=4)


def lolly(melt):
    """An ice lolly on a stick, melting and drooping to the right. Pivot = held point on the stick."""
    c = Cut(170, 240)
    sx, sy = 60, 210
    c.rrect(sx - 7, sy - 70, sx + 7, sy + 22, 6, STICK)
    m = max(0.0, min(1.0, melt))
    h = 118 * (1 - 0.88 * m)
    if m < 0.995:
        droop = 46 * m ** 0.8
        base_y = sy - 60
        n = 16

        def edge(v, side):
            w = 30 * (1 + 0.15 * m * v)
            return (sx + side * w + droop * v ** 2, base_y - h * v)
        left = [edge(i / n, -1) for i in range(n + 1)]
        right = [edge(i / n, 1) for i in range(n, -1, -1)]
        tx, ty = sx + droop, base_y - h
        cap = [(tx + 30 * math.cos(a), ty + 22 * math.sin(a) * (1 - 0.4 * m))
               for a in np.linspace(math.pi, 2 * math.pi, 14)]
        c.polygon(left + cap + right, LOLLY_TOP)
        for v0, v1, col in ((0.0, 0.33, LOLLY_BOT), (0.33, 0.62, LOLLY_MID)):
            pts = [edge(v0 + (v1 - v0) * i / 6, -1) for i in range(7)]
            pts += [edge(v1 - (v1 - v0) * i / 6, 1) for i in range(7)]
            c.polygon(pts, col, sil=False)
        c.line([edge(0.5, -0.45), edge(0.95, -0.45)], 6, (255, 236, 240))
        for i, dx in enumerate((-20, 4, 24)):                              # drips hanging under the ice
            if m > 0.12 + 0.12 * i:
                dl = 10 + 26 * min(1, (m - 0.12 - 0.12 * i) * 3)
                x = sx + dx + 4
                c.line([(x, base_y), (x, base_y + dl)], 9, LOLLY_TOP)
                c.ellipse(x, base_y + dl, 7, 8, LOLLY_TOP)
    return c.finish(pivot=(sx, sy), border=4)


def drip():
    c = Cut(40, 56)
    c.polygon([(20, 4), (32, 30), (20, 50), (8, 30)], LOLLY_TOP)
    c.ellipse(20, 34, 13, 15, LOLLY_TOP)
    c.ellipse(16, 30, 3.5, 5, (255, 220, 228), sil=False)
    return c.finish(pivot=(20, 34), border=3)


def sweat_drop():
    c = Cut(44, 64)
    c.polygon([(22, 4), (36, 34), (22, 58), (8, 34)], (150, 210, 250))
    c.ellipse(22, 40, 15, 17, (150, 210, 250))
    c.ellipse(17, 36, 4, 6, (255, 255, 255), sil=False)
    return c.finish(pivot=(22, 40), border=3)


def draw_drop(c, cx, cy, size, col=WATER, sil=False):
    k = size / 100
    c.polygon([(cx, cy - 50 * k), (cx + 30 * k, cy), (cx - 30 * k, cy)], col, sil)
    c.ellipse(cx, cy + 10 * k, 34 * k, 36 * k, col, sil)
    c.ellipse(cx - 12 * k, cy + 2 * k, 7 * k, 11 * k, (255, 255, 255), sil=False)


BOTTLE_STRAW_TIP = (54, 14)      # straw tip in bottle-sprite pixels (before scaling)
BOTTLE_PIVOT = (110, 250)


def bottle(level=1.0):
    """A kids' water bottle with a flip-up straw. Pivot = where the paw holds it (lower body)."""
    c = Cut(220, 360)
    bx0, bx1, by0, by1 = 50, 170, 104, 340
    c.line([(110, 70), (98, 40), (72, 24), (54, 14)], 13, (255, 255, 255), sil=True)    # straw
    c.line([(110, 70), (98, 40), (72, 24), (54, 14)], 6, (130, 210, 250))
    c.rrect(66, 62, 154, 112, 14, (255, 255, 255))                                       # cap
    c.rrect(66, 92, 154, 112, 6, (226, 236, 246), sil=False)
    c.rrect(bx0, by0, bx1, by1, 30, BOTTLE)
    wl = by0 + 24 + (by1 - by0 - 50) * (1 - level)
    if level > 0.02:
        c.rrect(bx0 + 10, wl, bx1 - 10, by1 - 10, 22, WATER, sil=False)
        c.line([(bx0 + 16, wl + 2), (bx1 - 16, wl + 2)], 4, (170, 220, 255))
    c.rrect(bx0 + 4, 196, bx1 - 4, 268, 8, (255, 255, 255), sil=False)                  # label
    draw_drop(c, 110, 236, 66)
    c.line([(bx0 + 18, by0 + 30), (bx0 + 18, by0 + 80)], 7, (220, 242, 255))
    return c.finish(pivot=BOTTLE_PIVOT, border=5)


def sun_hat(holes=False, ribbon=(84, 160, 230)):
    """A wide straw sun hat. Pivot = brim centre. Snip's has two ear holes in the crown."""
    c = Cut(440, 200)
    c.ellipse(220, 150, 210, 40, STRAW)
    c.ellipse(220, 156, 186, 26, STRAW_DARK, sil=False)
    c.ellipse(220, 158, 150, 18, STRAW, sil=False)
    c.chord(220, 140, 118, 126, 180, 360, STRAW)
    c.rrect(104, 112, 336, 146, 10, ribbon)
    c.polygon(star_pts(310, 128, 22, 9), (255, 234, 120), sil=False)
    for x in (150, 200, 250, 290):                       # weave marks
        c.line([(x, 40 + abs(x - 220) * 0.5), (x - 6, 106)], 3, STRAW_DARK)
    if holes:
        for x in (162, 278):
            c.ellipse(x, 76, 30, 16, (150, 112, 62), sil=False)
            c.ellipse(x, 79, 26, 11, (110, 80, 46), sil=False)
    return c.finish(pivot=(220, 150), border=5)


# ---------------------------------------------------------------- the beach umbrella
UMB_POLE = 1130          # pole length (base in the sand -> apex)
CANOPY_W, CANOPY_H = 940, 230


def pole():
    c = Cut(40, UMB_POLE + 30)
    c.rrect(10, 10, 30, UMB_POLE + 20, 9, (250, 250, 252))
    for y in range(60, UMB_POLE, 120):
        c.rrect(10, y, 30, y + 40, 4, UMB_RED, sil=False)
    return c.finish(pivot=(20, UMB_POLE + 18), border=4)


def canopy():
    """Open umbrella canopy. Pivot = apex (top of the pole)."""
    W2, Hc = CANOPY_W, CANOPY_H
    c = Cut(W2 + 40, Hc + 120)
    ax, ay = (W2 + 40) / 2, 40
    rim_y = ay + Hc
    n = 8
    pts_rim = [(20 + W2 * i / n, rim_y) for i in range(n + 1)]

    def rib(xr, k=14):
        """Curved rib from the apex to rim point xr (the outermost ribs follow the dome edge)."""
        return [(ax + (xr - ax) * v, rim_y - Hc * (1 - v * v) ** 0.85) for v in np.linspace(0, 1, k)]
    for i in range(n):
        x0, x1 = pts_rim[i][0], pts_rim[i + 1][0]
        scallop = [(x, rim_y + 26 * math.sin(math.pi * (x - x0) / (x1 - x0))) for x in np.linspace(x0, x1, 12)]
        c.polygon(rib(x0) + scallop + rib(x1)[::-1], UMB_RED if i % 2 == 0 else UMB_CREAM)
    for i in range(1, n):
        c.line(rib(pts_rim[i][0]), 3, (214, 120, 110))
    c.ellipse(ax, ay - 8, 14, 16, (255, 214, 72))
    return c.finish(pivot=(ax, ay), border=5)


def furled():
    """The closed umbrella's wrapped canopy (hangs from the apex). Pivot = apex."""
    c = Cut(100, 330)
    c.polygon([(50, 10), (82, 70), (70, 300), (50, 318), (30, 300), (18, 70)], UMB_RED)
    c.polygon([(50, 16), (64, 90), (56, 296), (50, 300)], UMB_CREAM, sil=False)
    c.rrect(26, 150, 74, 168, 6, (255, 214, 72))
    c.ellipse(50, 4, 12, 14, (255, 214, 72))
    return c.finish(pivot=(50, 10), border=4)


# ================================================================ icons, bubbles
def draw_bunny_head(c, cx, cy, size, ears_droop=0.0, hat=False):
    """Mini Snip head for icons (size = face width)."""
    k = size / 100
    for side in (-1, 1):
        if ears_droop > 0:
            th = side * (10 + 70 * ears_droop)
            ex, ey = cx + side * 20 * k, cy - 34 * k
            dx, dy = rot(0, -30 * k, -th)
            c.ellipse(ex + dx, ey + dy, 13 * k, 36 * k, SNIP_COL["fur"], theta=-th)
            c.ellipse(ex + dx * 1.1, ey + dy * 1.1, 6 * k, 25 * k, SNIP_COL["ear_in"], sil=False, theta=-th)
        else:
            c.ellipse(cx + side * 20 * k, cy - 62 * k, 14 * k, 40 * k, SNIP_COL["fur"], theta=-side * 10)
            c.ellipse(cx + side * 20 * k, cy - 58 * k, 7 * k, 28 * k, SNIP_COL["ear_in"], sil=False, theta=-side * 10)
    c.ellipse(cx, cy, 50 * k, 43 * k, SNIP_COL["fur"])
    for side in (-1, 1):
        c.ellipse(cx + side * 31 * k, cy + 12 * k, 8 * k, 5 * k, SNIP_COL["cheek"], sil=False)
        if ears_droop > 0:
            c.arc(cx + side * 17 * k, cy - 2 * k, 7 * k, 5 * k, 20, 160, 3 * k, EYE)
        else:
            c.ellipse(cx + side * 17 * k, cy - 4 * k, 5.5 * k, 7 * k, EYE, sil=False)
            c.ellipse(cx + side * 17 * k + 2 * k, cy - 7 * k, 2 * k, 2 * k, (255, 255, 255), sil=False)
    c.ellipse(cx, cy + 7 * k, 5 * k, 3.5 * k, SNIP_COL["nose"], sil=False)
    if hat:
        c.ellipse(cx, cy - 26 * k, 66 * k, 12 * k, STRAW)
        c.chord(cx, cy - 28 * k, 36 * k, 34 * k, 180, 360, STRAW)
        c.rrect(cx - 36 * k, cy - 40 * k, cx + 36 * k, cy - 30 * k, 3 * k, (84, 160, 230), sil=False)


def draw_mini_sun(c, cx, cy, r):
    for i in range(12):
        a = math.radians(i * 30)
        tip = (cx + r * 1.55 * math.cos(a), cy + r * 1.55 * math.sin(a))
        l = (cx + r * math.cos(a - 0.2), cy + r * math.sin(a - 0.2))
        rr = (cx + r * math.cos(a + 0.2), cy + r * math.sin(a + 0.2))
        c.polygon([l, tip, rr], (255, 184, 52), sil=False)
    c.ellipse(cx, cy, r, r, (255, 210, 64), sil=False)


def draw_mini_bottle(c, cx, cy, h):
    k = h / 100
    c.rrect(cx - 18 * k, cy - 30 * k, cx + 18 * k, cy + 50 * k, 10 * k, BOTTLE, sil=False)
    c.rrect(cx - 14 * k, cy - 6 * k, cx + 14 * k, cy + 46 * k, 8 * k, WATER, sil=False)
    c.rrect(cx - 13 * k, cy - 44 * k, cx + 13 * k, cy - 28 * k, 4 * k, (255, 255, 255), sil=False)
    c.line([(cx, cy - 44 * k), (cx - 8 * k, cy - 54 * k)], 4 * k, (130, 210, 250))


def draw_mini_umbrella(c, cx, cy, w):
    k = w / 200
    for i in range(6):
        x0 = cx - 100 * k + i * 200 * k / 6
        x1 = x0 + 200 * k / 6
        pts = [(cx, cy - 46 * k)]
        for x in np.linspace(x0, x1, 6):
            pts.append((x, cy + 6 * k * math.sin(math.pi * (x - x0) / (x1 - x0))))
        c.polygon(pts, UMB_RED if i % 2 == 0 else UMB_CREAM, sil=False)
    c.line([(cx, cy - 46 * k), (cx, cy + 90 * k)], 5 * k, (250, 250, 252))


def choice_bubble(kind, ring):
    """'sun' = Snip with droopy ears under the hot sun; 'safe' = hat + shade + water."""
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    if kind == "sun":
        draw_mini_sun(c, 125, 70, 30)
        draw_bunny_head(c, 125, 160, 92, ears_droop=1.0)
    else:
        draw_mini_umbrella(c, 125, 78, 170)
        draw_bunny_head(c, 108, 162, 84, hat=True)
        draw_mini_bottle(c, 180, 168, 58)
    return c.finish(pivot=(125, 125), border=7)


def draw_castle_icon(c, cx, cy, size):
    k = size / 100
    c.ellipse(cx, cy + 38 * k, 56 * k, 14 * k, CASTLE_DARK, sil=False)
    for dx, w, h in ((-34, 20, 44), (34, 20, 44), (0, 28, 70)):
        x = cx + dx * k
        c.polygon([(x - w * 0.8 * k, cy + 38 * k - h * k), (x + w * 0.8 * k, cy + 38 * k - h * k),
                   (x + w * k, cy + 38 * k), (x - w * k, cy + 38 * k)], CASTLE, sil=False)
        for j in (-1, 0, 1):
            c.rrect(x + j * w * 0.55 * k - 4 * k, cy + 38 * k - h * k - 9 * k, x + j * w * 0.55 * k + 4 * k,
                    cy + 38 * k - h * k + 1, 1.5 * k, CASTLE, sil=False)
    c.line([(cx, cy - 34 * k), (cx, cy - 66 * k)], 3 * k, (150, 110, 70))
    c.polygon([(cx, cy - 66 * k), (cx + 26 * k, cy - 58 * k), (cx, cy - 50 * k)], (240, 80, 90), sil=False)
    c.chord(cx, cy + 38 * k, 8 * k, 16 * k, 180, 360, (170, 122, 66), sil=False)


def thought_castle():
    """Snip's dream: a big finished sandcastle. Pivot = the smallest trailing dot."""
    c = Cut(260, 280)
    for cx, cy, r in ((130, 100, 80), (66, 108, 50), (194, 108, 50), (98, 56, 48), (166, 54, 50),
                      (130, 150, 56), (74, 146, 42), (188, 146, 42)):
        c.ellipse(cx, cy, r, r * 0.95, (255, 255, 255))
    c.ellipse(70, 226, 16, 15, (255, 255, 255))
    c.ellipse(52, 262, 10, 10, (255, 255, 255))
    draw_castle_icon(c, 130, 104, 150)
    return c.finish(pivot=(52, 262), border=5, shadow_alpha=0.22)


def wave_wipe():
    """A tall paper wave that rises over the screen and drains away (the loop transition).
    Pivot = top-left at the crest line."""
    Wd, Hd = 1240, 2500
    c = Cut(Wd, Hd)
    crest = [(x, 120 + 34 * math.sin(x / 70) + 14 * math.sin(x / 29)) for x in range(0, Wd + 1, 8)]
    c.polygon([(0, Hd)] + crest + [(Wd, Hd)], SEA_NEAR)
    band = [(x, 210 + 30 * math.sin(x / 80 + 1.3) + 10 * math.sin(x / 33)) for x in range(0, Wd + 1, 8)]
    c.polygon([(0, Hd)] + band + [(Wd, Hd)], SEA_MID, sil=False)
    band2 = [(x, 420 + 36 * math.sin(x / 95 + 2.1)) for x in range(0, Wd + 1, 8)]
    c.polygon([(0, Hd)] + band2 + [(Wd, Hd)], SEA_FAR, sil=False)
    c.line(crest, 22, FOAM)
    for x in range(20, Wd, 56):
        y = 120 + 34 * math.sin(x / 70) + 14 * math.sin(x / 29)
        c.ellipse(x, y - 10, 16, 14, FOAM)
    rng = np.random.default_rng(3)
    for _ in range(60):
        x, y = rng.uniform(40, Wd - 40), rng.uniform(260, Hd - 100)
        r = rng.uniform(8, 22)
        c.arc(x, y, r, r, 0, 360, 3.5, (200, 240, 250))
    return c.finish(pivot=(80, 120), border=0, shadow_alpha=0.0)


# ================================================================ Snip with noodle ears + a hat
_EAR_CACHE = {}


def _bend(side, B, q, u, u0):
    v = max(0.0, (u - u0) / (1 - u0))
    return side * (B * v ** 0.85 + 0.35 * abs(q) * math.sin(3 * math.pi * v) * v)


def noodle_ear(side, wilt, s):
    """Snip's ear as a bendy noodle. side=+1 left ear (droops left), -1 right ear (droops right).
    wilt 0 = the normal upright ear; 1 = hanging down like a cooked noodle. Pivot = ear base."""
    q = round(wilt * 40) / 40
    key = (side, q, s)
    if key in _EAR_CACHE:
        return _EAR_CACHE[key]
    L = 264 * s
    u0 = 22 * s / L                       # the part below the pivot stays put
    R = int(L + 40)
    c = Cut(2 * R, 2 * R)
    piv = (R, R)
    B = math.radians(190) * q
    n = 40
    centre = []
    for i in range(n + 1):
        u = i / n
        centre.append(u)
    pts = []
    x, y = piv[0], piv[1] + u0 * L
    prev_u = 0.0
    for u in centre:
        if u > 0:
            du = u - prev_u
            um = (u + prev_u) / 2
            th = _bend(side, B, q, um, u0)
            x += -math.sin(th) * du * L
            y += -math.cos(th) * du * L
        th = _bend(side, B, q, u, u0)
        pts.append((x, y, th, u))
        prev_u = u

    def outline(half_w, a, b):
        left, right = [], []
        for x, y, th, u in pts:
            if u < a - 1e-6 or u > b + 1e-6:
                continue
            v = (u - a) / (b - a)
            w = half_w * math.sqrt(max(0.0, 1 - (2 * v - 1) ** 2))
            nx, ny = -math.cos(th), math.sin(th)        # normal to the direction (-sin, -cos)
            left.append((x + nx * w, y + ny * w))
            right.append((x - nx * w, y - ny * w))
        return left + right[::-1]
    c.polygon(outline(46 * s, 0.0, 1.0), SNIP_COL["fur"])
    c.polygon(outline(24 * s, 18 / 264, 210 / 264), SNIP_COL["ear_in"], sil=False)
    spr = c.finish(pivot=piv)
    _EAR_CACHE[key] = spr
    return spr


HAT_DY = 196             # Snip's worn hat: brim centre above the face pivot (unscaled px)


class BeachSnip(Character):
    """Snip whose ears can wilt like noodles and who can wear a sun hat (ears through the holes)."""

    def __init__(self, scale=1.15):
        super().__init__("snip", scale)
        self.hat = sun_hat(holes=True).scaled(scale * 0.98)

    def hat_pose(self, x, base_y, hop=0.0, lean=0.0, squash=1.0, head_dy=0.0, head_tilt=0.0):
        hx, hy = self.head_pivot(x, base_y, hop, lean, squash, head_dy)
        ha = lean + head_tilt
        dx, dy = rot(0, -HAT_DY * self.s, ha)
        return (hx + dx, hy + dy), ha

    def draw(self, base, x, base_y, hop=0.0, lean=0.0, head_tilt=0.0, arm_l=0.0, arm_r=0.0,
             eyes=None, mouth=None, look=(0, 0), alpha=1.0, squash=1.0, head_dy=0.0,
             blink=False, ears=(0.0, 0.0), ear_stretch=1.0, frizz=0.0, wilt=(0.0, 0.0), hat=False):
        eyes = eyes or self._default[0]
        mouth = mouth or self._default[1]
        if blink and eyes in BLINKABLE:
            eyes = "blink"
        s = self.s
        place(base, self.ground, (x, base_y + 6), alpha=max(0.25, 1 - hop / 160) * alpha,
              sx=max(0.6, 1 - hop / 300), shadow=False)
        P = self.anchor(x, base_y, hop, lean)
        place(base, self.body, P(0, -self.neck_h * squash), angle=lean, alpha=alpha, sx=1 / math.sqrt(squash),
              sy=squash)
        place(base, self.arm_l, self.shoulder_pt(x, base_y, "l", hop, lean, squash), angle=arm_l + lean, alpha=alpha)
        place(base, self.arm_r, self.shoulder_pt(x, base_y, "r", hop, lean, squash), angle=arm_r + lean, alpha=alpha)
        hx, hy = self.head_pivot(x, base_y, hop, lean, squash, head_dy)
        ha = lean + head_tilt

        def draw_ears():
            for (ox, oy), tilt, extra, side, w in zip(SNIP_EAR_BASE, SNIP_EAR_TILT, ears, (1, -1), wilt):
                ex, ey = rot(ox * s, oy * s, ha)
                place(base, noodle_ear(side, w, s), (hx + ex, hy + ey), angle=ha + tilt + extra, sy=ear_stretch,
                      alpha=alpha)
        if frizz > 0.01:
            cx, cy = rot(0, (SNIP_FACE_CENTER[1] - SNIP_FACE_PIVOT[1]) * s, ha)
            place(base, self.frizz, (hx + cx, hy + cy), angle=ha, scale=frizz, alpha=alpha)
        if not hat:
            draw_ears()
        place(base, self.head(eyes, mouth, look), (hx, hy), angle=ha, alpha=alpha)
        if hat:
            at, a = self.hat_pose(x, base_y, hop, lean, squash, head_dy, head_tilt)
            place(base, self.hat, at, angle=a, alpha=alpha)
            draw_ears()


CR_HAT_DY = 214          # Crinkle's worn hat: brim centre above his head pivot (unscaled px)


# ================================================================ sounds (original, synthesized)
SR = A.SR


def _t(d):
    return np.arange(int(d * SR)) / SR


def steelpan(f, dur=0.9, vel=1.0):
    """A bright steel-drum-like tone (inharmonic-ish partials, quick bloom)."""
    t = _t(dur)
    y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 4)
         + 0.32 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 7) + 0.12 * np.sin(2 * np.pi * f * 4.2 * t) * np.exp(-t * 12))
    env = (1 - np.exp(-t * 300)) * np.exp(-t * 3.2)
    return vel * 0.5 * env * y


def sea(dur, vel=1.0, period=6.0):
    """Soft sea wash: filtered noise that swells every `period` seconds."""
    rng = np.random.default_rng(21)
    n = rng.normal(0, 1, int(dur * SR))
    k = 60
    y = np.convolve(n, np.ones(k) / k, mode="same") - np.convolve(n, np.ones(400) / 400, mode="same")
    t = _t(dur)
    swell = 0.45 + 0.55 * np.sin(np.pi * (t % period) / period) ** 2
    return vel * 3.0 * swell * y


def yip(vel=1.0, base=880):
    """A tiny 'ow!' squeak (rising then dropping), no words."""
    d = 0.14
    t = _t(d)
    f = base * (1 + 0.5 * np.sin(np.pi * t / d))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return vel * 0.32 * np.sin(np.pi * t / d) ** 0.6 * y


def sizzle(dur=0.22, vel=1.0):
    rng = np.random.default_rng(5)
    t = _t(dur)
    n = rng.normal(0, 1, len(t))
    y = n - np.convolve(n, np.ones(3) / 3, mode="same")
    crackle = (rng.uniform(0, 1, len(t)) > 0.995).astype(float) * rng.normal(0, 3, len(t))
    return vel * 0.35 * (np.exp(-t * 14) * y + np.exp(-t * 10) * crackle)


def scrape(vel=1.0):
    """Spade in sand: a short gritty 'shk'."""
    rng = np.random.default_rng(8)
    t = _t(0.16)
    n = rng.normal(0, 1, len(t))
    y = np.convolve(n, np.ones(4) / 4, mode="same") - np.convolve(n, np.ones(30) / 30, mode="same")
    return vel * 1.4 * np.sin(np.pi * t / 0.16) ** 1.5 * y


def droop_whistle(dur=1.0, vel=1.0):
    """A slow, wobbly slide down: ears wilting like noodles."""
    t = _t(dur)
    p = t / dur
    f = 1100 * (1 - 0.6 * p ** 1.2) * (1 + 0.03 * np.sin(2 * np.pi * 5 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return vel * 0.3 * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.12) * y


def plip(vel=1.0):
    """A water drop: a fast upward blip."""
    t = _t(0.12)
    f = 700 + 2600 * (t / 0.12) ** 0.7
    return vel * 0.6 * np.exp(-t * 30) * (1 - np.exp(-t * 3000)) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def thunk(vel=1.0):
    t = _t(0.22)
    f = 120 - 50 * t
    rng = np.random.default_rng(12)
    n = np.convolve(rng.normal(0, 1, len(t)), np.ones(25) / 25, mode="same")
    return vel * (np.sin(2 * np.pi * np.cumsum(f) / SR) + 1.6 * n) * np.exp(-t * 20) * (1 - np.exp(-t * 2000))


def fwump(vel=1.0):
    """The umbrella popping open: a soft air whoomp."""
    t = _t(0.4)
    rng = np.random.default_rng(13)
    n = rng.normal(0, 1, len(t))
    y = np.convolve(n, np.ones(40) / 40, mode="same") - np.convolve(n, np.ones(300) / 300, mode="same")
    tone = np.sin(2 * np.pi * (90 + 120 * np.exp(-t * 12)) * t)
    env = (1 - np.exp(-t * 200)) * np.exp(-t * 9)
    return vel * (6.0 * y + 0.7 * tone) * env


def gulp(vel=1.0):
    """A cartoon gulp: a low bubbly bloop."""
    t = _t(0.22)
    f = 260 + 260 * np.sin(np.pi * t / 0.22)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return vel * 0.5 * np.sin(np.pi * t / 0.22) ** 0.8 * y


def spring_up(vel=1.0, base=420):
    """Ears springing back up: a rising boing."""
    t = _t(0.45)
    f = base * (1 + 1.2 * (1 - np.exp(-t * 9))) + 60 * np.exp(-4 * t) * np.sin(2 * np.pi * 12 * t)
    return vel * 0.6 * np.exp(-t * 5) * (1 - np.exp(-t * 900)) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def splash(dur=0.9, vel=1.0):
    rng = np.random.default_rng(17)
    t = _t(dur)
    n = rng.normal(0, 1, len(t))
    y = np.convolve(n, np.ones(6) / 6, mode="same") - np.convolve(n, np.ones(90) / 90, mode="same")
    env = np.minimum(1, t / 0.15) * np.exp(-np.maximum(0, t - 0.2) * 4)
    return vel * 2.2 * env * y


def bubbles(dur=0.6, vel=1.0, seed=4):
    out = np.zeros(int(dur * SR))
    rng = np.random.default_rng(seed)
    for _ in range(int(dur * 14)):
        s = int(rng.uniform(0, dur - 0.08) * SR)
        t = _t(0.06)
        f = rng.uniform(700, 1500) * (1 + 2.5 * t / 0.06)
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 50)
        out[s:s + len(b)] += 0.25 * b
    return vel * out


def ahh(vel=1.0):
    """A cool, relieved 'ahh' made of a soft vowel-ish pad (no words)."""
    d = 0.9
    t = _t(d)
    f0 = A.midi(72) * (1 - 0.05 * t / d)
    ph = 2 * np.pi * np.cumsum(f0 * np.ones_like(t)) / SR
    y = sum(np.sin(h * ph) * (1 / h) * (1.6 if h in (2, 3) else 1.0) for h in range(1, 7))
    env = np.minimum(1, t / 0.12) * np.minimum(1, (d - t) / 0.35)
    return vel * 0.22 * env * y
