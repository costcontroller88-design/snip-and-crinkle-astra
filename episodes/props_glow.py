"""Episode 11 small props (plan N6), built with hires.Cut (sharp at 2x). Sizes are world design units.

    import hires; hires.set_res(2)
    import props_glow as G
    G.sketchbook("back" | "plan")   # Snip's sketchbook, pivot at the bottom centre (where a paw holds it)
    G.book_tucked()                 # the closed book seen edge-on, tucked under an arm (pivot at its centre)
    G.crayon()                      # a short blue crayon pointing DOWN from its grip (pivot), tip at CRAYON_TIP
    G.cloth(), G.cloth_corner()     # the polishing cloth (pivot centre); the corner peeking out of the scarf
    G.tea_light(on)                 # battery tea light: white body, side switch, LED dome; pivot at the top of
                                    # the body (where fingers hold it); never shown open
    G.chime()                       # wind chime, pivot at the hanging point; rotate by the swing angle
    G.leaf(i)                       # one of three autumn leaves (pivot centre)
    G.CHIME_AT, G.CHIME_LOW         # where it hangs (under the eave) and its lowest point below the hook

Markers come from rig2_pip.marker_sprite (no caps are ever shown); sparkles from props_splash.sparkle.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hires import Cut  # noqa: E402
from paperlib import heart_pts, mix, star_pts  # noqa: E402

KRAFT = (214, 176, 128)
KRAFT_DARK = (182, 142, 96)
PAGE = (252, 250, 242)
SPIRAL = (150, 150, 160)
ORANGE = (246, 146, 42)
ORANGE_DARK = (214, 108, 30)
INK = (40, 34, 46)
RED = (224, 46, 66)
GLOW_Y = (255, 206, 60)
GLOW_BRIGHT = (255, 178, 20)          # Episode 11 round 3: the plan's glow lines, bright and saturated
DUCK = (255, 214, 64)
BEAK = (250, 150, 50)
CRAYON = (72, 140, 230)
CLOTH = (190, 160, 230)
CLOTH_DARK = (160, 128, 206)
WHITE = (250, 250, 248)
SWITCH = (176, 180, 188)
LED_OFF = (236, 234, 220)
LED_ON = (255, 236, 150)
WOOD = (196, 136, 86)
METAL = (196, 206, 214)
METAL_LIGHT = (232, 238, 244)

BOOK_W, BOOK_H = 126, 96
CRAYON_TIP = 34
CHIME_AT = (780, 596)                 # hook under the eave board, above Snip's right ear in shot 14
CHIME_LOW = 90                        # lowest point below the hook at scale 1 (the episode hangs it at 1.15:
                                      # its bottom ~25 above Snip's resting ear tips)


def sketchbook(view="back"):
    c = Cut(BOOK_W + 16, BOOK_H + 24)
    x0, y0 = 8, 14
    x1, y1 = x0 + BOOK_W, y0 + BOOK_H
    if view == "back":
        c.rrect(x0, y0, x1, y1, 6, KRAFT)
        c.rrect(x0 + 8, y0 + 10, x1 - 8, y1 - 8, 4, mix(KRAFT, (255, 255, 255), 0.12), sil=False)
        c.polygon(star_pts((x0 + x1) / 2, (y0 + y1) / 2 + 2, 16, 7), (255, 214, 64), sil=False)
    else:
        c.rrect(x0, y0, x1, y1, 6, PAGE)
        cx, cy = x0 + 50, y0 + 56
        c.ellipse(cx, cy, 52, 46, mix(PAGE, GLOW_Y, 0.35), sil=False)     # a warm glow behind it (round 3)
        for a in (-150, -120, -90, -60, -30, 0, 180, 150, 30):      # bright glow lines round the pumpkin
            r0, r1 = 37, 53
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            c.line([(cx + r0 * ca, cy + r0 * sa * 0.9), (cx + r1 * ca, cy + r1 * sa * 0.9)], 4.6, GLOW_BRIGHT)
        c.ellipse(cx, cy, 32, 27, ORANGE)
        for dx in (-14, 0, 14):
            c.arc(cx + dx, cy, 8, 25, 70, 290, 1.6, ORANGE_DARK)
        c.line([(cx, cy - 26), (cx + 2, cy - 33)], 3.4, (110, 120, 60))
        for ex in (-11, 11):
            c.ellipse(cx + ex, cy - 8, 5, 5, INK, sil=False)
        c.polygon(heart_pts(cx, cy - 1, 8), RED, sil=False)
        c.arc(cx, cy + 3, 15, 10, 15, 165, 3.0, INK)
        px, py = x0 + 102, y0 + 70                                    # tiny smiling Pip
        c.ellipse(px, py + 9, 11, 10, DUCK, sil=False)
        c.ellipse(px, py - 6, 11, 11, DUCK, sil=False)
        c.ellipse(px, py - 3, 6, 3, BEAK, sil=False)
        for ex in (-4, 4):
            c.ellipse(px + ex, py - 9, 1.6, 1.8, INK, sil=False)
        c.arc(px, py - 3, 4, 3, 20, 160, 1.4, (170, 76, 26))
        c.line([(px, py - 17), (px + 1, py - 22)], 2.4, DUCK)
    for i in range(8):                                                # spiral at the top
        x = x0 + 12 + i * (BOOK_W - 24) / 7
        c.ellipse(x, y0, 3.2, 5.5, SPIRAL, sil=False)
    return c.finish(pivot=((x0 + x1) / 2, y1), border=4, shadow_alpha=0.24)


def book_tucked():
    """The sketchbook under Snip's arm: its kraft cover with the yellow star toward us (ep11 r3pre: the old edge-on
    white page strip read as a white marker or a knife)."""
    w = 56
    c = Cut(w + 12, BOOK_W + 12)
    c.rrect(6, 6, 6 + w, BOOK_W + 6, 5, KRAFT)
    c.rrect(12, 14, w, BOOK_W - 2, 3, mix(KRAFT, (255, 255, 255), 0.12), sil=False)
    c.polygon(star_pts(6 + w / 2, (BOOK_W + 12) / 2, 13, 5.5), (255, 214, 64), sil=False)
    return c.finish(pivot=((w + 12) / 2, (BOOK_W + 12) / 2), border=4, shadow_alpha=0.2)


def crayon():
    c = Cut(24, 70)
    gx, gy = 12, 22
    c.rrect(gx - 6, gy - 18, gx + 6, gy + 22, 4, CRAYON)
    c.rrect(gx - 6, gy - 4, gx + 6, gy + 4, 1, mix(CRAYON, (255, 255, 255), 0.4), sil=False)
    c.polygon([(gx - 6, gy + 21), (gx + 6, gy + 21), (gx + 1.5, gy + CRAYON_TIP), (gx - 1.5, gy + CRAYON_TIP)],
              mix(CRAYON, INK, 0.2))
    return c.finish(pivot=(gx, gy), border=3)


def cloth():
    c = Cut(70, 64)
    c.polygon([(8, 14), (58, 6), (62, 52), (12, 58)], CLOTH)
    c.polygon([(36, 10), (58, 6), (60, 30)], CLOTH_DARK, sil=False)
    for y in (24, 38):
        c.line([(16, y), (52, y - 4)], 1.6, CLOTH_DARK)
    return c.finish(pivot=(35, 32), border=4, shadow_alpha=0.22)


def cloth_corner():
    c = Cut(40, 40)
    c.polygon([(6, 8), (32, 6), (20, 34)], CLOTH)
    c.line([(12, 12), (26, 11)], 1.4, CLOTH_DARK)
    return c.finish(pivot=(19, 8), border=3, shadow_alpha=0.18)


def tea_light(on=False):
    """A battery tea light seen from the side, a little from above: white body, side switch, LED dome."""
    c = Cut(70, 64)
    cx, top = 35, 30                                  # pivot: top of the body (centre)
    c.ellipse(cx, top - 8, 9, 10, LED_ON if on else LED_OFF)        # the LED dome (no flame shape)
    c.rrect(cx - 23, top, cx + 23, top + 22, 6, WHITE)
    c.ellipse(cx, top + 1, 23, 5, mix(WHITE, (200, 200, 206), 0.25), sil=False)
    c.ellipse(cx, top - 1, 9, 3, LED_ON if on else LED_OFF, sil=False)
    c.rrect(cx + 15, top + 8, cx + 22, top + 15, 2, SWITCH, sil=False)  # the side switch
    for x in (-14, -4, 6):
        c.line([(cx + x, top + 5), (cx + x, top + 20)], 1.0, (226, 226, 230))
    return c.finish(pivot=(cx, top), border=3, shadow_alpha=0.22)


def chime():
    c = Cut(70, CHIME_LOW + 20)
    hx, hy = 35, 6
    c.line([(hx, hy), (hx, hy + 30)], 1.6, (120, 110, 100))
    c.ellipse(hx, hy + 34, 24, 6, WOOD)
    for dx, L_ in ((-15, 30), (0, 38), (15, 32)):
        c.line([(hx + dx * 0.7, hy + 36), (hx + dx, hy + 46)], 1.0, (120, 110, 100))
        c.rrect(hx + dx - 3.5, hy + 46, hx + dx + 3.5, hy + 46 + L_, 3, METAL)
        c.line([(hx + dx - 1, hy + 50), (hx + dx - 1, hy + 40 + L_)], 1.2, METAL_LIGHT)
    c.line([(hx, hy + 36), (hx, hy + 78)], 0.9, (120, 110, 100))
    c.polygon(heart_pts(hx, hy + 80, 12), (240, 112, 104))             # a little paper heart at the bottom
    return c.finish(pivot=(hx, hy), border=3, shadow_alpha=0.18)


LEAF_COLS = ((236, 128, 52), (246, 176, 64), (214, 92, 52))


def leaf(i=0):
    col = LEAF_COLS[i % 3]
    c = Cut(44, 34)
    pts = []
    for k in range(24):
        a = 2 * math.pi * k / 24
        r = 1 + 0.18 * math.cos(5 * a)
        pts.append((22 + 17 * r * math.cos(a), 17 + 11 * r * math.sin(a)))
    c.polygon(pts, col)
    c.line([(6, 17), (38, 17)], 1.4, mix(col, (90, 50, 30), 0.4))
    return c.finish(pivot=(22, 17), border=3, shadow_alpha=0.2)
