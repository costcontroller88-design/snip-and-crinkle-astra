"""Props for the pilot episode "Oops! A Splash of Blue" (built with hires.Cut, so they follow hires.RES).

Painting coordinates are canvas-local: (0, 0) is the canvas's top-left corner, the canvas is 338 x 302.
The blue splash is drawn whale-shaped on purpose (head left, tail up on the right), so that later, when
Crinkle traces it, the whale is really there.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from characters import CRINKLE, EYE, SNIP  # noqa: E402
from hires import Cut  # noqa: E402
from paperlib import heart_pts, mix, star_pts  # noqa: E402

CANVAS_W, CANVAS_H = 338, 302
BLUE = (64, 136, 232)
BLUE_DARK = (40, 98, 196)
BLUE_LIGHT = (150, 204, 250)
SEA = (52, 120, 214)
WOOD = (214, 160, 108)
WOOD_DARK = (182, 128, 82)

# The whale splash, canvas-local
WHALE_C = (168, 180)                  # body centre
WHALE_R = (104, 54)
TAIL_BASE = (262, 168)


TAIL_EDGE = [(284, 158), (298, 124), (314, 98), (330, 84), (318, 72), (300, 82), (286, 86), (268, 70),
             (254, 80), (258, 108), (252, 136)]


def whale_outline():
    """Path around the whale (nose, belly, up into the tail, along the back to the nose) for the dotted trace."""
    cx, cy = WHALE_C
    rx, ry = WHALE_R
    pts = [(cx + rx * math.cos(math.pi - math.pi * i / 28), cy + ry * math.sin(math.pi - math.pi * i / 28))
           for i in range(29)]
    pts += TAIL_EDGE
    pts += [(cx + rx * math.cos(1.8 * math.pi - 0.8 * math.pi * i / 24),
             cy + ry * math.sin(1.8 * math.pi - 0.8 * math.pi * i / 24)) for i in range(25)]
    return pts


def _irregular_ellipse(cx, cy, rx, ry, seed, n=64, wob=0.08):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + wob * (math.sin(3 * a + seed) * 0.6 + math.sin(7 * a + 2 * seed) * 0.4)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return pts


def splash():
    """The accidental blue splash: whale-shaped, with ragged splatter and droplets. Pivot = canvas (0, 0)."""
    c = Cut(CANVAS_W + 40, CANVAS_H + 40)
    o = 20
    cx, cy = WHALE_C
    rx, ry = WHALE_R
    body = [(x + o, y + o) for x, y in _irregular_ellipse(cx, cy, rx, ry, 1.3, wob=0.1)]
    c.polygon(body, BLUE)
    for (x, y), r in (((272, 132), 22), ((282, 100), 18), ((268, 82), 13), ((300, 92), 15), ((318, 84), 11),
                      ((300, 112), 12)):
        c.ellipse(x + o, y + o, r, r, BLUE)
    c.polygon([(250 + o, 156 + o), (268 + o, 118 + o), (286 + o, 126 + o), (268 + o, 166 + o)], BLUE)
    for deg, length in ((200, 30), (225, 22), (160, 26), (140, 18), (115, 24), (80, 20), (60, 28), (250, 16),
                        (275, 20), (190, 14)):
        a = math.radians(deg)
        ex, ey = cx + rx * 0.96 * math.cos(a), cy + ry * 0.96 * math.sin(a)
        tx, ty = cx + (rx + length) * math.cos(a), cy + (ry + length) * math.sin(a)
        nx, ny = -math.sin(a) * 7, math.cos(a) * 7
        c.polygon([(ex + nx + o, ey + ny + o), (tx + o, ty + o), (ex - nx + o, ey - ny + o)], BLUE)
        c.ellipse(tx + 9 * math.cos(a) + o, ty + 9 * math.sin(a) + o, 5, 5, BLUE)
    for x, y, r in ((44, 130, 7), (36, 200, 5), (92, 104, 6), (300, 214, 8), (206, 108, 5), (326, 150, 5),
                    (24, 168, 4), (244, 262, 5), (150, 104, 4), (120, 262, 6), (60, 244, 4)):
        c.ellipse(x + o, y + o, r, r, BLUE)
    c.ellipse(130 + o, 160 + o, 40, 14, mix(BLUE, (255, 255, 255), 0.3), sil=False, theta=-8)
    return c.finish(pivot=(o, o), border=0, shadow_alpha=0.0, grain_strength=0.05)


def drip(length):
    c = Cut(22, length + 24)
    c.rrect(7, 0, 15, length, 4, BLUE)
    c.ellipse(11, length, 6, 7, BLUE)
    return c.finish(pivot=(11, 0), border=0, shadow_alpha=0.0, grain_strength=0.05)


DRIPS = ((136, 230, 22), (198, 228, 40))                     # canvas x, start y, length


# --- what they paint onto the whale (canvas-local, pivot = canvas (0, 0) unless said)
def _layer():
    return Cut(CANVAS_W + 40, CANVAS_H + 40), 20


def _done(c, o):
    return c.finish(pivot=(o, o), border=0, shadow_alpha=0.0, grain_strength=0.05)


def whale_face():
    c, o = _layer()
    c.ellipse(112 + o, 164 + o, 15, 15, (255, 255, 255))
    c.ellipse(115 + o, 166 + o, 9, 10, EYE)
    c.ellipse(118 + o, 162 + o, 3.5, 3.5, (255, 255, 255))
    c.arc(132 + o, 186 + o, 40, 20, 20, 150, 5, BLUE_DARK)
    c.ellipse(150 + o, 196 + o, 10, 6, (240, 150, 170), sil=False)
    return _done(c, o)


def whale_tail():
    c, o = _layer()
    edge = [(244, 162)] + TAIL_EDGE + [(240, 150)]
    c.polygon([(x + o, y + o) for x, y in edge], BLUE)
    c.line([(x + o, y + o) for x, y in TAIL_EDGE], 5, BLUE_DARK)
    c.line([(286 + o, 86 + o), (276 + o, 112 + o)], 4, BLUE_DARK)
    for x, y in ((140, 150), (190, 150), (226, 170)):
        c.arc(x + o, y + o, 16, 8, 200, 340, 3, BLUE_LIGHT)            # little skin lines
    return _done(c, o)


def spout():
    """A whale's water spout: a jet up from the blowhole, then two arcs falling left and right."""
    c, o = _layer()
    bx, by = 128, 128
    c.line([(bx + o, by + o), (bx + o, by - 52 + o)], 9, BLUE_LIGHT)
    for sd in (-1, 1):
        pts = [(bx + sd * 46 * math.sin(math.pi * u / 2) + o, by - 52 - 22 * math.sin(math.pi * u) + 26 * u * u + o)
               for u in [i / 12 for i in range(13)]]
        c.line(pts, 7, BLUE_LIGHT)
        for k, (dx, dy) in enumerate(((52, -18), (44, -6), (58, -2))):
            c.ellipse(bx + sd * dx + o, by + dy + o, 5 - k, 5 - k, (210, 236, 255))
    c.ellipse(bx + o, by - 54 + o, 10, 8, (210, 236, 255))
    return _done(c, o)


def rainbow():
    """The final touch: a small rainbow in the spout's spray."""
    c, o = _layer()
    for k, col in enumerate(((240, 112, 104), (255, 196, 72), (120, 196, 120), (100, 160, 236))):
        c.arc(196 + o, 112 + o, 66 - k * 9, 56 - k * 9, 190, 350, 8, col)
    return _done(c, o)


def waves():
    c, o = _layer()
    pts = [(0 + o, 302 + o)]
    for x in range(0, CANVAS_W + 1, 4):
        pts.append((x + o, 262 + 8 * math.sin(x / 18) + o))
    pts.append((CANVAS_W + o, 302 + o))
    c.polygon(pts, SEA)
    for x in range(10, CANVAS_W, 38):
        c.arc(x + o, 270 + 8 * math.sin(x / 18) + o, 14, 8, 200, 340, 4, (220, 240, 255))
    return _done(c, o)


def boat():
    c, o = _layer()
    x, y = 66, 258
    c.polygon([(x - 46 + o, y + o), (x + 46 + o, y + o), (x + 32 + o, y + 22 + o), (x - 32 + o, y + 22 + o)],
              (232, 96, 88))
    c.rrect(x - 46 + o, y - 4 + o, x + 46 + o, y + 4 + o, 3, (250, 220, 120))
    # the two friends in the boat
    sx, sy = x - 18, y - 18
    c.ellipse(sx - 6 + o, sy - 24 + o, 4, 11, SNIP["fur"], theta=-8)
    c.ellipse(sx + 6 + o, sy - 24 + o, 4, 11, SNIP["fur"], theta=8)
    c.ellipse(sx + o, sy + o, 14, 13, SNIP["fur"])
    bx, by = x + 18, y - 17
    c.ellipse(bx - 10 + o, by - 11 + o, 5, 5, CRINKLE["fur"])
    c.ellipse(bx + 10 + o, by - 11 + o, 5, 5, CRINKLE["fur"])
    c.ellipse(bx + o, by + o, 15, 13, CRINKLE["fur"])
    for ex, ey in ((sx - 5, sy - 1), (sx + 5, sy - 1), (bx - 5, by - 1), (bx + 5, by - 1)):
        c.ellipse(ex + o, ey + o, 2, 2, EYE)
    c.arc(sx + o, sy + 4 + o, 4, 3, 20, 160, 1.6, EYE)
    c.arc(bx + o, by + 5 + o, 4, 3, 20, 160, 1.6, EYE)
    return _done(c, o)


def bubbles():
    c, o = _layer()
    for x, y, r in ((238, 250, 9), (252, 232, 6), (244, 216, 4), (262, 250, 5)):
        c.ellipse(x + o, y + o, r, r, (220, 240, 255))
        c.ellipse(x - r * 0.3 + o, y - r * 0.3 + o, r * 0.3, r * 0.3, (255, 255, 255), sil=False)
    return _done(c, o)


def sun_face():
    c, o = _layer()
    for x in (47, 63):
        c.ellipse(x + o, 52 + o, 3, 4, EYE)
    c.arc(55 + o, 60 + o, 9, 6, 20, 160, 2.5, EYE)
    return _done(c, o)


def trace_dot():
    """Navy dot with a thin white edge: shows on the white paper and on the blue paint."""
    c = Cut(20, 20)
    c.ellipse(10, 10, 6, 6, (30, 50, 110))
    return c.finish(pivot=(10, 10), border=2, shadow_alpha=0.2)


# --- room props
def table():
    """Low paint table; pivot at floor centre; top surface at 150 above the floor."""
    c = Cut(300, 170)
    c.rrect(26, 24, 50, 170, 8, WOOD_DARK)
    c.rrect(250, 24, 274, 170, 8, WOOD_DARK)
    c.rrect(0, 10, 300, 36, 10, WOOD)
    c.rrect(0, 30, 300, 38, 4, WOOD_DARK, sil=False)
    return c.finish(pivot=(150, 168), border=5)


TABLE_TOP = 150


def jar(color, level=1.0):
    """Open paint jar; pivot at the base centre."""
    c = Cut(70, 92)
    glass = (226, 240, 250)
    c.rrect(6, 14, 64, 90, 14, glass)
    if level > 0:
        top = 88 - 66 * level
        c.rrect(10, top, 60, 86, 11, color, sil=False)
        c.ellipse(35, top + 3, 24, 5, mix(color, (255, 255, 255), 0.25), sil=False)
    c.rrect(2, 8, 68, 20, 6, (255, 255, 255))
    c.ellipse(20, 52, 4, 14, (255, 255, 255), sil=False)
    return c.finish(pivot=(35, 90), border=4)


def brush_cup():
    """A cup with two brushes, standing on the easel tray; pivot at the base centre."""
    c = Cut(70, 150)
    for x, col, tip in ((26, (120, 196, 120), (240, 112, 104)), (44, (240, 196, 72), (120, 170, 236))):
        c.rrect(x - 5, 20, x + 5, 120, 4, col)
        c.polygon([(x - 6, 22), (x + 6, 22), (x + 3, 2), (x - 3, 2)], tip)
    c.rrect(8, 84, 62, 148, 10, (255, 204, 72))
    c.rrect(8, 84, 62, 96, 6, (255, 226, 130), sil=False)
    return c.finish(pivot=(35, 148), border=4)


def brush(tip=(255, 196, 52), handle=(240, 112, 104)):
    """A paintbrush held in a paw; pivot at the handle end, bristles pointing 'down' (along the forearm)."""
    c = Cut(40, 170)
    c.rrect(13, 0, 27, 116, 7, handle)
    c.rrect(11, 108, 29, 126, 3, (200, 204, 214))
    c.polygon([(11, 124), (29, 124), (26, 158), (20, 168), (14, 158)], tip)
    return c.finish(pivot=(20, 24), border=4)


BRUSH_LEN = 144                       # pivot to bristle tip (design units, before any scaling)


def block():
    """A wooden toy block with a painted star; pivot at the bottom centre."""
    c = Cut(84, 84)
    c.rrect(4, 4, 80, 80, 10, (240, 112, 104))
    c.rrect(14, 14, 70, 70, 8, (255, 140, 128), sil=False)
    c.polygon(star_pts(42, 43, 20, 9), (255, 220, 90), sil=False)
    return c.finish(pivot=(42, 80), border=4)


def thought_cloud():
    """A big thought cloud with a trail of little puffs toward the lower right (the thinker's head)."""
    c = Cut(640, 400)
    for x, y, r in ((150, 150, 110), (300, 110, 130), (460, 150, 110), (230, 230, 100), (390, 235, 100),
                    (90, 220, 70), (530, 225, 70)):
        c.ellipse(x, y, r, r * 0.9, (255, 255, 255))
    for x, y, r in ((520, 320, 26), (565, 352, 17), (598, 378, 10)):
        c.ellipse(x, y, r, r, (255, 255, 255))
    return c.finish(pivot=(598, 378), border=5, shadow_alpha=0.22)


def question():
    c = Cut(130, 150)
    c.text("?", 65, 78, 140, (230, 72, 72))
    return c.finish(pivot=(65, 75), border=7)


def nose_dot():
    c = Cut(30, 30)
    c.ellipse(15, 15, 10, 9, BLUE)
    return c.finish(pivot=(15, 15), border=0, shadow_alpha=0.0)


def sparkle(color=(255, 214, 64)):
    c = Cut(300, 300)
    c.polygon(star_pts(150, 150, 140, 34, 4, -90), color)
    for a, r, d in ((45, 16, 92), (135, 12, 100), (225, 14, 96), (315, 12, 104)):
        x, y = 150 + d * math.cos(math.radians(a)), 150 + d * math.sin(math.radians(a))
        c.polygon(star_pts(x, y, r * 2.2, r * 0.6, 4, -90), (255, 255, 255))
    return c.finish(pivot=(150, 150), border=5)


def heart(color=(240, 72, 98), size=80):
    c = Cut(size + 20, size + 20)
    c.polygon(heart_pts((size + 20) / 2, (size + 20) / 2 + 4, size), color)
    c.ellipse((size + 20) / 2 - size * 0.22, (size + 20) / 2 - size * 0.12, size * 0.1, size * 0.07,
              (255, 220, 228), sil=False)
    return c.finish(pivot=((size + 20) / 2, (size + 20) / 2), border=5)


def slosh_drop(r):
    c = Cut(2 * r + 6, 2 * r + 6)
    c.ellipse(r + 3, r + 3, r, r * 0.9, BLUE)
    c.ellipse(r + 3 - r * 0.3, r + 3 - r * 0.3, r * 0.3, r * 0.22, mix(BLUE, (255, 255, 255), 0.4), sil=False)
    return c.finish(pivot=(r + 3, r + 3), border=3, shadow_alpha=0.2)


def blue_nose():
    """Crinkle's nose after the brush boops it: the whole nose bright blue, with a shine and two speckles."""
    c = Cut(80, 56)
    c.ellipse(40, 28, 30, 21, BLUE)
    c.ellipse(31, 21, 9, 4.5, mix(BLUE, (255, 255, 255), 0.55), sil=False)
    c.ellipse(70, 40, 4, 4, BLUE)
    c.ellipse(9, 44, 3, 3, BLUE)
    return c.finish(pivot=(40, 28), border=0, shadow_alpha=0.0)
