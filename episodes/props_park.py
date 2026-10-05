"""Park setting, Pip the duckling, the lost teddy, icons and extra sounds for Episode 4.

Everything is a hand-made paper cut-out (paperlib.Cut) or synthesized sound (numpy),
in the same style as the shared modules, which are only imported, never edited.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import audio as A  # noqa: E402
import scene  # noqa: E402
from characters import (BLINKABLE, EYE, MOUTH_DARK, TONGUE, _contact_shadow, _eyes,  # noqa: E402
                        _mirror)
from characters import SNIP as SNIP_COL  # noqa: E402
from paperlib import Cut, grain, heart_pts, place, rot, star_pts  # noqa: E402,F401

W, H = scene.W, scene.H
GROUND_Y = 1440          # where everyone stands (the grass line)
SEAT_Y = 1285            # top of the bench seat (the teddy sits here)
BENCH_X = 22             # left edge of the bench

SKY_TOP = (126, 196, 242)
SKY_LOW = (206, 236, 250)
HILL_BACK = (164, 214, 156)
HILL_FRONT = (130, 196, 120)
GRASS = (122, 196, 102)
GRASS_LIGHT = (146, 212, 118)
GRASS_DARK = (96, 168, 84)
TRUNK = (152, 104, 72)
TRUNK_DARK = (122, 82, 56)
LEAF = (88, 168, 98)
LEAF_LIGHT = (118, 192, 110)
LEAF_DARK = (68, 142, 84)
WOOD = (232, 158, 96)
WOOD_DARK = (200, 124, 72)
IRON = (74, 98, 116)

TEDDY = (242, 154, 172)
TEDDY_DARK = (214, 112, 136)
TEDDY_LIGHT = (255, 228, 224)
BOW = (228, 58, 76)
BOW_DARK = (182, 36, 56)

DUCK = (255, 214, 70)
DUCK_DARK = (244, 186, 44)
DUCK_BELLY = (255, 238, 164)
BEAK = (255, 148, 44)
BEAK_DARK = (224, 108, 34)
DUCK_CHEEK = (255, 162, 120)


# ================================================================ background
def _sky():
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / 0.66, 0, 1) ** 1.3
    top, low = np.array(SKY_TOP, np.float32), np.array(SKY_LOW, np.float32)
    rgb = top[None, None, :] * (1 - k[..., None]) + low[None, None, :] * k[..., None]
    rgb = np.repeat(rgb, W, axis=1)
    a = np.full((H, W, 1), 255, np.float32)
    img = Image.fromarray(np.concatenate([rgb, a], axis=2).clip(0, 255).astype(np.uint8), "RGBA")
    return grain(img, 0.03)


def _hills():
    c = Cut(1140, 520)
    back = [(0, 520)] + [(x, 150 + 44 * math.sin(x / 150 + 0.6) + 26 * math.sin(x / 61))
                         for x in range(0, 1141, 12)] + [(1140, 520)]
    c.polygon(back, HILL_BACK)
    for cx, cy, r in ((150, 205, 34), (930, 196, 40), (1010, 215, 28)):      # distant round trees
        c.ellipse(cx, cy - 40, r, r * 1.1, (126, 186, 122), sil=False)
    front = [(0, 520)] + [(x, 250 + 36 * math.sin(x / 120 + 2.2) + 18 * math.sin(x / 47 + 1))
                          for x in range(0, 1141, 12)] + [(1140, 520)]
    c.polygon(front, HILL_FRONT)
    return c.finish(pivot=(30, 0), border=5, shadow_alpha=0.18)


def _meadow():
    c = Cut(1160, 700)
    top = [(x, 40 + 10 * math.sin(x / 70) + 6 * math.sin(x / 23)) for x in range(0, 1161, 10)]
    c.polygon([(0, 700)] + top + [(1160, 700)], GRASS)
    for cx, cy, rx, ry in ((200, 190, 260, 44), (820, 300, 300, 50), (400, 470, 380, 60), (950, 560, 240, 40)):
        c.ellipse(cx, cy, rx, ry, GRASS_LIGHT, sil=False)
    rng = np.random.default_rng(4)
    for _ in range(70):                                                   # little grass tufts
        x, y = rng.uniform(20, 1140), rng.uniform(80, 690)
        s = rng.uniform(0.7, 1.3)
        for dx, h, lean in ((-7, 18, -5), (0, 26, 0), (7, 17, 5)):
            c.polygon([(x + dx * s - 4 * s, y), (x + dx * s + 4 * s, y), (x + (dx + lean) * s, y - h * s)],
                      GRASS_DARK, sil=False)
    return c.finish(pivot=(40, 0), border=5, shadow_alpha=0.15)


def _flower(c, x, y, petal, s=1.0):
    c.line([(x, y + 4), (x, y + 46 * s)], 5 * s, (84, 156, 82))
    for i in range(5):
        a = math.radians(i * 72 - 90)
        c.ellipse(x + 13 * s * math.cos(a), y + 13 * s * math.sin(a), 10 * s, 10 * s, petal)
    c.ellipse(x, y, 8 * s, 8 * s, (255, 210, 64), sil=False)


def _flowers_front():
    c = Cut(1080, 380)
    spots = ((70, 120, (255, 255, 255), 1.3), (190, 230, (255, 150, 170), 1.1), (330, 140, (255, 255, 255), 1.0),
             (520, 270, (190, 160, 240), 1.2), (690, 150, (255, 255, 255), 1.1), (860, 250, (255, 150, 170), 1.3),
             (1000, 130, (255, 255, 255), 1.0), (430, 60, (255, 200, 90), 0.9), (770, 40, (190, 160, 240), 0.9))
    for x, y, col, s in spots:
        _flower(c, x, y, col, s)
    return c.finish(pivot=(0, 0), border=4, shadow_alpha=0.2)


def _trunk():
    c = Cut(300, 1020)
    pts = [(70, 1010), (102, 940), (118, 700), (112, 380), (96, 120), (120, 0), (200, 0), (184, 150),
           (196, 420), (204, 700), (212, 930), (258, 1010)]
    c.polygon(pts, TRUNK)
    c.polygon([(186, 330), (300, 190), (300, 240), (200, 390)], TRUNK)            # branch to the right
    for x0, y0, y1 in ((150, 200, 340), (136, 470, 640), (172, 600, 760), (150, 820, 930)):
        c.line([(x0, y0), (x0 + 6, (y0 + y1) / 2), (x0 - 2, y1)], 6, TRUNK_DARK)
    c.ellipse(158, 560, 18, 24, TRUNK_DARK, sil=False)                               # knot hole
    return c.finish(pivot=(0, 0), border=6)


CANOPY_BLOBS = ((300, 250, 175), (150, 330, 150), (460, 330, 150), (230, 140, 135), (400, 150, 130),
                (90, 200, 115), (560, 230, 110), (300, 420, 140), (130, 450, 110), (480, 450, 115),
                (40, 360, 110), (620, 380, 90))


def canopy():
    c = Cut(760, 640)
    for cx, cy, r in CANOPY_BLOBS:
        c.ellipse(cx + 40, cy + 20, r, r * 0.92, LEAF_DARK)
    for cx, cy, r in CANOPY_BLOBS:
        c.ellipse(cx + 34, cy + 6, r * 0.93, r * 0.84, LEAF, sil=False)
    for cx, cy, r in CANOPY_BLOBS[:7]:
        c.ellipse(cx + 10, cy - 18, r * 0.55, r * 0.42, LEAF_LIGHT, sil=False)
    return c.finish(pivot=(380, 320), border=6)


def _bench():
    c = Cut(520, 330)
    for x, out in ((60, -1), (450, 1)):                                      # iron frame, legs splay out
        c.rrect(x - 11, 0, x + 11, 150, 8, IRON)
        c.polygon([(x - 12, 168), (x + 12, 168), (x + 12 + 16 * out, 322), (x - 12 + 16 * out, 322)], IRON)
        c.rrect(x - 22 + 16 * out, 312, x + 22 + 16 * out, 330, 6, IRON)
    for y in (6, 52, 98):                                                    # backrest slats
        c.rrect(8, y, 512, y + 36, 9, WOOD)
        c.line([(30, y + 18), (490, y + 18)], 3, WOOD_DARK)
    c.rrect(0, 175, 520, 204, 9, WOOD)                                       # seat (2 slats)
    c.rrect(0, 207, 520, 234, 9, WOOD_DARK)
    for x in (60, 450):
        for y in (24, 70, 116, 190):
            c.ellipse(x, y, 4, 4, (60, 70, 80), sil=False)                   # bolts
    return c.finish(pivot=(0, 175), border=5)


def _bush(w=300, h=190, seed=1):
    c = Cut(w, h)
    rng = np.random.default_rng(seed)
    blobs = [(w * 0.2, h * 0.62, h * 0.38), (w * 0.45, h * 0.45, h * 0.46), (w * 0.72, h * 0.55, h * 0.42),
             (w * 0.88, h * 0.72, h * 0.3), (w * 0.08, h * 0.78, h * 0.24)]
    for cx, cy, r in blobs:
        c.ellipse(cx, cy, r, r * 0.9, (90, 168, 96))
    for cx, cy, r in blobs[:3]:
        c.ellipse(cx - r * 0.2, cy - r * 0.25, r * 0.5, r * 0.4, (118, 190, 110), sil=False)
    for _ in range(5):
        _flower(c, rng.uniform(w * 0.15, w * 0.85), rng.uniform(h * 0.3, h * 0.6), (255, 255, 255), 0.6)
    return c.finish(pivot=(w / 2, h), border=5)


def sun():
    c = Cut(300, 300)
    for i in range(12):
        a = math.radians(i * 30)
        tip = (150 + 140 * math.cos(a), 150 + 140 * math.sin(a))
        l = (150 + 96 * math.cos(a - 0.17), 150 + 96 * math.sin(a - 0.17))
        r = (150 + 96 * math.cos(a + 0.17), 150 + 96 * math.sin(a + 0.17))
        c.polygon([l, tip, r], (255, 196, 64))
    c.ellipse(150, 150, 92, 92, (255, 216, 72))
    c.ellipse(150, 150, 70, 70, (255, 232, 120), sil=False)
    return c.finish(pivot=(150, 150), border=5, shadow_alpha=0.15)


def cloud(w=300, h=130):
    c = Cut(w, h)
    for fx, fy, fr in ((0.25, 0.62, 0.36), (0.45, 0.42, 0.5), (0.68, 0.5, 0.42), (0.84, 0.66, 0.3), (0.5, 0.72, 0.32)):
        c.ellipse(w * fx, h * fy, h * fr * 1.15, h * fr, (255, 255, 255))
    return c.finish(pivot=(w / 2, h / 2), border=4, shadow_alpha=0.12)


def background():
    """Static park layers. The canopy, clouds and sun are drawn per frame so they can move."""
    bg = _sky()
    place(bg, _hills(), (0, 1010))
    place(bg, _bush(260, 150, 3), (980, 1310))
    place(bg, _meadow(), (0, 1250))
    place(bg, _trunk(), (-70, 450))
    place(bg, _bush(300, 190, 1), (930, 1440))
    place(bg, _bench(), (BENCH_X, SEAT_Y))
    place(bg, _flowers_front(), (0, 1560))
    return bg


# ================================================================ the teddy (icon + sprite)
def draw_teddy(c, cx, cy, size, sil=True, bow=True):
    """A sitting pink teddy with a red bow, fitted to a box `size` px tall centred on (cx, cy)."""
    k = size / 170

    def P(u, v):
        return cx + (u - 75) * k, cy + (v - 85) * k

    def E(u, v, rx, ry, col, s=sil, th=0):
        x, y = P(u, v)
        c.ellipse(x, y, rx * k, ry * k, col, s, theta=th)

    for u in (34, 116):                                    # ears
        E(u, 28, 20, 20, TEDDY)
        E(u, 30, 10, 10, TEDDY_DARK, False)
    E(31, 120, 16, 27, TEDDY, th=28)                       # arms
    E(119, 120, 16, 27, TEDDY, th=-28)
    E(46, 152, 23, 17, TEDDY)                              # legs
    E(104, 152, 23, 17, TEDDY)
    E(75, 124, 42, 39, TEDDY)                              # body
    E(46, 154, 12, 9, TEDDY_LIGHT, False)
    E(104, 154, 12, 9, TEDDY_LIGHT, False)
    E(75, 130, 23, 21, TEDDY_LIGHT, False)                 # tummy
    E(75, 62, 49, 44, TEDDY)                               # head
    E(75, 77, 21, 16, TEDDY_LIGHT, False)                  # muzzle
    E(46, 74, 8, 6, (250, 120, 140), False)                # cheeks
    E(104, 74, 8, 6, (250, 120, 140), False)
    for u in (57, 93):
        E(u, 56, 6, 6.5, EYE, False)
        E(u + 2, 54, 2.2, 2.2, (255, 255, 255), False)
    E(75, 71, 7, 5, (110, 60, 70), False)
    x0, y0 = P(75, 80)
    c.arc(x0 - 6 * k, y0, 6 * k, 5 * k, 10, 170, 2.4 * k, (110, 60, 70))
    c.arc(x0 + 6 * k, y0, 6 * k, 5 * k, 10, 170, 2.4 * k, (110, 60, 70))
    if bow:
        draw_bow(c, *P(75, 101), 54 * k, sil)


def draw_bow(c, cx, cy, size, sil=True):
    s = size / 54
    c.polygon([(cx, cy), (cx - 26 * s, cy - 13 * s), (cx - 24 * s, cy + 13 * s)], BOW, sil)
    c.polygon([(cx, cy), (cx + 26 * s, cy - 13 * s), (cx + 24 * s, cy + 13 * s)], BOW, sil)
    c.ellipse(cx, cy, 7 * s, 7 * s, BOW_DARK, sil)


def teddy():
    c = Cut(180, 196)
    draw_teddy(c, 90, 98, 172)
    return c.finish(pivot=(90, 180), border=5)


TEDDY_HEAD_DY = 180 - (98 + (62 - 85) * 172 / 170)       # pivot -> teddy head centre (px, scale 1)


# ================================================================ Pip the duckling
def _duck_beak(c, cx, cy, kind, k=1.0):
    if kind in ("open", "grin"):
        c.ellipse(cx, cy + 15 * k, 22 * k, 10 * k, BEAK_DARK)
        c.ellipse(cx, cy + 6 * k, 19 * k, 12 * k, MOUTH_DARK, sil=False)
        if kind == "grin":
            c.ellipse(cx, cy + 11 * k, 11 * k, 6 * k, TONGUE, sil=False)
        c.ellipse(cx, cy - 7 * k, 33 * k, 13 * k, BEAK)
        return
    c.ellipse(cx, cy + 9 * k, 24 * k, 9 * k, BEAK_DARK)
    c.ellipse(cx, cy, 33 * k, 13 * k, BEAK)
    if kind == "sad":
        c.arc(cx, cy + 15 * k, 22 * k, 9 * k, 200, 340, 3.2 * k, (170, 76, 26))
    else:
        c.arc(cx, cy - 1 * k, 25 * k, 9 * k, 20, 160, 3.2 * k, (170, 76, 26))


def _duck_tuft(c, cx, cy, k=1.0, sil=True):
    for dx, dy, rx, ry, th in ((-14, 6, 9, 22, 24), (0, 0, 10, 26, 0), (14, 8, 8, 20, -26)):
        c.ellipse(cx + dx * k, cy + dy * k, rx * k, ry * k, DUCK, sil, theta=th)


def duck_head(eyes="normal", beak="smile", look=(0, 0)):
    c = Cut(240, 250)
    _duck_tuft(c, 120, 44)
    c.ellipse(120, 140, 100, 94, DUCK)
    draw_bow(c, 178, 66, 50)
    for x in (62, 178):
        c.ellipse(x, 170, 18, 11, DUCK_CHEEK, sil=False)
    _eyes(c, [(84, 130), (156, 130)], eyes, (13, 17), look)
    _duck_beak(c, 120, 170, beak)
    return c.finish(pivot=(120, 222))


def duck_body():
    c = Cut(200, 200)
    for x in (68, 132):                                     # webbed feet
        c.ellipse(x, 186, 30, 12, BEAK)
        for dx in (-18, 0, 18):
            c.ellipse(x + dx, 192, 9, 7, BEAK)
    c.ellipse(100, 104, 80, 82, DUCK)
    c.ellipse(100, 122, 52, 54, DUCK_BELLY, sil=False)
    return c.finish(pivot=(100, 26))


def duck_wing():
    c = Cut(80, 128)
    c.ellipse(40, 62, 29, 54, DUCK_DARK)
    for dx in (-14, 0, 14):
        c.ellipse(40 + dx, 108, 10, 14, DUCK_DARK)
    c.ellipse(36, 56, 16, 34, DUCK, sil=False)
    return c.finish(pivot=(40, 16))


class Duckling:
    """Pip: a little paper duckling with a red bow. API mirrors characters.Character.draw."""

    def __init__(self, scale=0.9):
        self.s = scale
        self.body = duck_body().scaled(scale)
        self.wing_l = duck_wing().scaled(scale)
        self.wing_r = _mirror(duck_wing()).scaled(scale)
        self.neck_h, self.shoulder, self.head_drop = 168, (70, 34), 14
        self.ground = _contact_shadow(int(150 * scale))
        self._heads = {}

    def head(self, eyes, beak, look, mirrored=False):
        key = (eyes, beak, look, mirrored)
        if key not in self._heads:
            h = duck_head(eyes, beak, look)
            self._heads[key] = (_mirror(h) if mirrored else h).scaled(self.s)
        return self._heads[key]

    def anchor(self, x, base_y, hop=0.0, lean=0.0):
        s = self.s

        def P(dx, dy):
            rx, ry = rot(dx * s, dy * s, lean)
            return x + rx, base_y - hop + ry
        return P

    def shoulder_pt(self, x, base_y, side, hop=0.0, lean=0.0, squash=1.0, turn=1.0):
        P = self.anchor(x, base_y, hop, lean)
        sx = self.shoulder[0] * max(0.05, abs(turn))
        return P(-sx if side == "l" else sx, (-self.neck_h + self.shoulder[1]) * squash)

    def head_pivot(self, x, base_y, hop=0.0, lean=0.0, squash=1.0, head_dy=0.0):
        P = self.anchor(x, base_y, hop, lean)
        return P(0, -self.neck_h * squash + self.head_drop + head_dy)

    def hug_pt(self, x, base_y, hop=0.0, lean=0.0, squash=1.0):
        """Where a hugged teddy's pivot (its bottom) goes."""
        P = self.anchor(x, base_y, hop, lean)
        return P(0, -14 * squash)

    def draw_wings(self, f, x, base_y, hop=0.0, lean=0.0, squash=1.0, wing_l=0.0, wing_r=0.0, turn=1.0, alpha=1.0):
        place(f, self.wing_l, self.shoulder_pt(x, base_y, "l", hop, lean, squash, turn), angle=wing_l + lean,
              alpha=alpha)
        place(f, self.wing_r, self.shoulder_pt(x, base_y, "r", hop, lean, squash, turn), angle=wing_r + lean,
              alpha=alpha)

    def draw(self, f, x, base_y, hop=0.0, lean=0.0, tilt=0.0, wing_l=0.0, wing_r=0.0, eyes="normal",
             beak="smile", look=(0, 0), squash=1.0, head_dy=0.0, blink=False, turn=1.0, alpha=1.0, wings=True):
        if blink and eyes in BLINKABLE:
            eyes = "blink"
        tk = max(0.05, abs(turn))
        place(f, self.ground, (x, base_y + 5), alpha=max(0.25, 1 - hop / 120) * alpha,
              sx=max(0.55, 1 - hop / 250), shadow=False)
        P = self.anchor(x, base_y, hop, lean)
        place(f, self.body, P(0, -self.neck_h * squash), angle=lean, alpha=alpha, sx=tk / math.sqrt(squash),
              sy=squash)
        if wings:
            self.draw_wings(f, x, base_y, hop, lean, squash, wing_l, wing_r, turn, alpha)
        place(f, self.head(eyes, beak, look, turn < 0), self.head_pivot(x, base_y, hop, lean, squash, head_dy),
              angle=lean + tilt, alpha=alpha, sx=tk)


# ================================================================ icons, bubbles, sign
def draw_bunny_head(c, cx, cy, size):
    """Mini Snip head for icons (size = face width)."""
    k = size / 100
    for side in (-1, 1):
        c.ellipse(cx + side * 20 * k, cy - 62 * k, 14 * k, 40 * k, SNIP_COL["fur"], theta=-side * 10)
        c.ellipse(cx + side * 20 * k, cy - 58 * k, 7 * k, 28 * k, SNIP_COL["ear_in"], sil=False, theta=-side * 10)
    c.ellipse(cx, cy, 50 * k, 43 * k, SNIP_COL["fur"])
    for side in (-1, 1):
        c.ellipse(cx + side * 31 * k, cy + 12 * k, 8 * k, 5 * k, SNIP_COL["cheek"], sil=False)
        c.ellipse(cx + side * 17 * k, cy - 4 * k, 5.5 * k, 7 * k, EYE, sil=False)
        c.ellipse(cx + side * 17 * k + 2 * k, cy - 7 * k, 2 * k, 2 * k, (255, 255, 255), sil=False)
    c.ellipse(cx, cy + 7 * k, 5 * k, 3.5 * k, SNIP_COL["nose"], sil=False)


def draw_duck_head(c, cx, cy, size, happy=True):
    k = size / 100
    _duck_tuft(c, cx, cy - 46 * k, 0.5 * k)
    c.ellipse(cx, cy, 50 * k, 46 * k, DUCK)
    draw_bow(c, cx + 30 * k, cy - 32 * k, 26 * k)
    for side in (-1, 1):
        c.ellipse(cx + side * 31 * k, cy + 14 * k, 8 * k, 5 * k, DUCK_CHEEK, sil=False)
        if happy:
            c.arc(cx + side * 18 * k, cy + 1 * k, 8 * k, 7 * k, 200, 340, 3.5 * k, EYE)
        else:
            c.ellipse(cx + side * 18 * k, cy - 4 * k, 5.5 * k, 7 * k, EYE, sil=False)
    _duck_beak(c, cx, cy + 15 * k, "smile", 0.5 * k)


def choice_bubble_park(kind, ring):
    """'keep' = Snip hugging the teddy; 'give' = the duckling hugging the teddy."""
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    if kind == "keep":
        draw_bunny_head(c, 125, 112, 92)
        draw_teddy(c, 125, 168, 82, sil=False)
        for side in (-1, 1):
            c.ellipse(125 + side * 30, 176, 13, 11, SNIP_COL["fur"], sil=False)
    else:
        draw_duck_head(c, 125, 104, 96)
        draw_teddy(c, 125, 168, 82, sil=False)
        for side in (-1, 1):
            c.ellipse(125 + side * 31, 172, 11, 17, DUCK_DARK, sil=False, theta=side * 30)
    return c.finish(pivot=(125, 125), border=7)


def thought_bubble():
    """Pip's sad thought: a cloud with the lost teddy. Pivot = the smallest trailing dot."""
    c = Cut(230, 250)
    for cx, cy, r in ((115, 92, 72), (58, 100, 46), (172, 100, 46), (86, 52, 44), (148, 50, 46),
                      (115, 140, 50), (66, 136, 38), (166, 136, 38)):
        c.ellipse(cx, cy, r, r * 0.95, (255, 255, 255))
    c.ellipse(96, 204, 15, 14, (255, 255, 255))
    c.ellipse(84, 236, 9, 9, (255, 255, 255))
    draw_teddy(c, 115, 96, 128, sil=False)
    return c.finish(pivot=(84, 236), border=5, shadow_alpha=0.22)


def sign_whose():
    """Crinkle's paper sign: the teddy and a '?' -- whose toy is this?"""
    c = Cut(440, 570)
    scene._sign_card(c)
    draw_teddy(c, 140, 125, 196, sil=False)
    c.text("?", 320, 128, 190, (230, 72, 72), sil=False)
    return c.finish(pivot=(220, 552))


# ================================================================ sounds (original, synthesized)
SR = A.SR


def _t(d):
    return np.arange(int(d * SR)) / SR


def whistle(notes=((84, 0.16), (88, 0.12), (83, 0.3)), vel=1.0):
    """An innocent little whistle: sine with vibrato and breath, gliding between notes."""
    dur = sum(d for _, d in notes) + 0.08
    t = _t(dur)
    f = np.zeros_like(t)
    edge = 0.0
    for i, (m, d) in enumerate(notes):
        i0, i1 = int(edge * SR), int((edge + d) * SR) if i < len(notes) - 1 else len(t)
        f[i0:i1] = A.midi(m)
        edge += d
    f = np.convolve(f, np.ones(600) / 600, mode="same")
    f[:300] = f[300]
    f[-300:] = f[-301]
    f *= 1 + 0.012 * np.sin(2 * np.pi * 6.5 * t)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    breath = np.random.default_rng(5).normal(0, 1, len(t))
    breath = np.convolve(breath, np.ones(8) / 8, mode="same") * 0.05
    env = np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.06)
    return vel * 0.45 * env * (y + breath)


def quack(vel=1.0, pitch=1.0):
    """A small, friendly duckling 'quack' (nasal buzz with a falling pitch)."""
    d = 0.17
    t = _t(d)
    f = pitch * (620 - 300 * t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = sum(np.sin(h * ph) / h ** 0.8 for h in range(1, 9))
    y = y * (0.6 + 0.4 * np.sin(2 * np.pi * 1300 * t))          # nasal formant-ish ripple
    env = np.minimum(1, t / 0.012) * np.exp(-t * 7) * np.minimum(1, (d - t) / 0.03)
    return vel * 0.22 * env * y


def chirp(vel=1.0, base=3000):
    """A tiny park bird chirp: two quick rising sine blips."""
    out = np.zeros(int(0.22 * SR))
    for i in range(2):
        t = _t(0.055)
        f = base + 1600 * t / 0.055
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.055)
        s = int(i * 0.09 * SR)
        out[s:s + len(y)] += y
    return vel * 0.16 * out


def squeak(vel=1.0):
    """A soft toy squeeze squeak."""
    t = _t(0.2)
    f = 1100 + 700 * np.sin(np.pi * t / 0.2)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return vel * 0.3 * np.sin(np.pi * t / 0.2) ** 0.7 * y


def slide_whistle(up=True, dur=0.45, vel=1.0):
    t = _t(dur)
    p = t / dur
    f = 500 + 900 * (p if up else 1 - p) ** 1.2
    y = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.01 * np.sin(2 * np.pi * 7 * t))) / SR)
    return vel * 0.35 * np.sin(np.pi * p) ** 0.5 * y


def flump(vel=1.0):
    """A soft plush landing."""
    t = _t(0.25)
    n = np.random.default_rng(9).normal(0, 1, len(t))
    n = np.convolve(n, np.ones(30) / 30, mode="same")
    tone = np.sin(2 * np.pi * (110 - 40 * t) * t)
    return vel * (2.2 * n + 0.6 * tone) * np.exp(-t * 18) * np.minimum(1, t / 0.005)


def sad_coo(vel=1.0):
    """Pip's small sad 'coo': a soft falling glide, not crying."""
    d = 0.7
    t = _t(d)
    f = A.midi(76) * (1 - 0.16 * (t / d) ** 1.4) * (1 + 0.01 * np.sin(2 * np.pi * 5 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.25 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return vel * 0.3 * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.2) * y
