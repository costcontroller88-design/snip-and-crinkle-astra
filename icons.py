"""Hand-made paper icons (no emoji fonts): fire, hand, hourglass, check, question mark.

Each draw_* function paints into an existing Cut at (cx, cy) fitting a `size` box,
so icons can sit on cards/bubbles (sil=False) or be standalone cut-outs (sil=True).
"""
from paperlib import Cut, star_pts  # noqa: F401

FIRE_OUT = (238, 72, 52)
FIRE_MID = (252, 146, 46)
FIRE_IN = (255, 220, 84)
HAND = (255, 204, 112)
HAND_LINE = (226, 160, 76)
CHECK_BG = (78, 186, 104)
WOOD = (196, 136, 84)
GLASS = (226, 240, 250)
SAND = (240, 196, 104)

_FLAME = [(50, 0), (60, 22), (74, 12), (76, 38), (92, 52), (96, 78), (88, 104), (70, 124), (50, 130),
          (30, 124), (12, 104), (4, 78), (10, 54), (24, 40), (22, 16), (38, 30)]


def _fit(pts, cx, cy, size, k=1.0, dy=0.0):
    s = size / 130 * k
    return [(cx + (x - 50) * s, cy + (y - 65) * s + dy * size) for x, y in pts]


def draw_fire(c, cx, cy, size, sil=False):
    c.polygon(_fit(_FLAME, cx, cy, size), FIRE_OUT, sil)
    c.polygon(_fit(_FLAME, cx, cy, size, 0.66, 0.12), FIRE_MID, False)
    c.polygon(_fit(_FLAME, cx, cy, size, 0.36, 0.25), FIRE_IN, False)


def draw_hand(c, cx, cy, size, sil=False):
    s = size / 140
    X = lambda v: cx + v * s  # noqa: E731
    Y = lambda v: cy + v * s  # noqa: E731
    for fx, top in ((-36, -64), (-12, -74), (12, -70), (36, -56)):
        c.rrect(X(fx - 11), Y(top), X(fx + 11), Y(10), 11 * s, HAND, sil)
    c.ellipse(X(-50), Y(14), 14 * s, 34 * s, HAND, sil, theta=-38)
    c.rrect(X(-48), Y(-10), X(48), Y(66), 30 * s, HAND, sil)
    for fx in (-24, 0, 24):
        c.line([(X(fx), Y(-10)), (X(fx), Y(8))], 3 * s, HAND_LINE)


def draw_hourglass(c, cx, cy, size, sil=False, level=0.5):
    s = size / 230
    X = lambda v: cx + (v - 80) * s  # noqa: E731
    Y = lambda v: cy + (v - 115) * s  # noqa: E731
    c.rrect(X(0), Y(0), X(160), Y(26), 10 * s, WOOD, sil)
    c.rrect(X(0), Y(204), X(160), Y(230), 10 * s, WOOD, sil)
    c.rrect(X(8), Y(20), X(22), Y(210), 6 * s, WOOD, sil)
    c.rrect(X(138), Y(20), X(152), Y(210), 6 * s, WOOD, sil)
    c.polygon([(X(30), Y(28)), (X(130), Y(28)), (X(84), Y(113)), (X(76), Y(113))], GLASS, sil)
    c.polygon([(X(76), Y(117)), (X(84), Y(117)), (X(130), Y(202)), (X(30), Y(202))], GLASS, sil)
    ht = 82 * level ** 0.5
    if ht > 1:
        w = 98 * ht / 85
        c.polygon([(X(80 - w / 2), Y(113 - ht)), (X(80 + w / 2), Y(113 - ht)), (X(80), Y(113))], SAND, False)
    hb = 64 * (1 - level) ** 0.6
    if hb > 1:
        c.polygon([(X(34), Y(202)), (X(126), Y(202)), (X(94), Y(202 - hb)), (X(66), Y(202 - hb))], SAND, False)


def draw_check(c, cx, cy, size, sil=False):
    r = size / 2
    c.rrect(cx - r, cy - r, cx + r, cy + r, r * 0.3, CHECK_BG, sil)
    c.line([(cx - r * 0.5, cy + r * 0.02), (cx - r * 0.12, cy + r * 0.4), (cx + r * 0.55, cy - r * 0.42)],
           r * 0.26, (255, 255, 255))


def draw_no(c, cx, cy, size, color=(226, 48, 48)):
    r = size / 2
    c.arc(cx, cy, r, r, 0, 360, size * 0.09, color)
    d = r * 0.7
    c.line([(cx - d, cy - d), (cx + d, cy + d)], size * 0.09, color)


def question(color=(230, 72, 72), px=130):
    c = Cut(px + 30, px + 40)
    c.text("?", (px + 30) / 2, (px + 40) / 2, px * 1.1, color)
    return c.finish(pivot=((px + 30) / 2, (px + 40) / 2), border=8)


def check(px=120):
    c = Cut(px + 20, px + 20)
    draw_check(c, (px + 20) / 2, (px + 20) / 2, px, sil=True)
    return c.finish(pivot=((px + 20) / 2, (px + 20) / 2), border=6)
