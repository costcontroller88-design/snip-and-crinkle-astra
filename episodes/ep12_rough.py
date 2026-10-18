"""Episode 12 rough playroom set: measure stage + gate-1b storyboard (not the episode).

    python3 episodes/ep12_rough.py --measure     numbers for the plan's Measured checks + Pip-under-A2 test
    python3 episodes/ep12_rough.py --sheet       build/sb1/storyboard.png (the plan's 12 frames, time labels only)
    python3 episodes/ep12_rough.py --still T     one storyboard frame -> build/sb1/ep12/f_T.png

One 1920x1920 world, landscape rows 560..1640, hires.set_res(2); shot = (centre, zoom), zoom <= 2.
Props are flat rough shapes (the real props_playroom.py comes at the toolkit stage).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import hires  # noqa: E402
hires.set_res(2)
import acting as K  # noqa: E402
import rig2 as R  # noqa: E402
import rig2_pip as RP  # noqa: E402

RES = hires.RES
W = H = 1920
FLOOR = 1480                 # feet
GROUND = 1492                # floor props stand a touch downstage of the feet
LAND_Y0 = 560
CAM = K.Cam("land", W, H, LAND_Y0, 0, res=RES)
FW, FH = int(1920 * RES), int(1080 * RES)

RED, BLUE, YEL = (222, 72, 64), (76, 134, 214), (246, 200, 60)
WOOD, WOOD_D, WHITE, INK = (196, 146, 96), (150, 104, 64), (250, 248, 240), (70, 56, 50)
WICKER = (236, 214, 170)

BOX = (300, 480, 1340)                    # toy box x0, x1, top
RUG = (560, 1360)
BALL_R = 55                               # ball 110 units (plan)
BASKET_W, BASKET_H = 150, 100
SHELF = (1440, 1900)                      # widened from 1480-1760: three 150-unit baskets on its top
BASKET_FLOOR = {"red": 1500, "blue": 1660, "yellow": 1820}
YBLOCK = 100                              # Pip's yellow block (C3 needs >= 96 at 2x for 10%)


def S(p):
    return CAM.S(p)


def _w(v):
    return max(1, int(v * RES))


def rect(d, x0, y0, x1, y1, fill, outline=INK, w=3, r=0):
    a, b = S((x0, y0)), S((x1, y1))
    if r:
        d.rounded_rectangle([a, b], radius=r * RES, fill=fill, outline=outline, width=_w(w))
    else:
        d.rectangle([a, b], fill=fill, outline=outline, width=_w(w))


def ell(d, cx, cy, rx, ry, fill, outline=INK, w=3):
    d.ellipse([S((cx - rx, cy - ry)), S((cx + rx, cy + ry))], fill=fill, outline=outline, width=_w(w))


def poly(d, pts, fill, outline=INK):
    d.polygon([S(p) for p in pts], fill=fill, outline=outline)


def star(d, cx, cy, r, fill=WHITE):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    poly(d, pts, fill, None)


# ---------------------------------------------------------------- the set (Pip's reach decides the shelf top)
def _pip_top_arms_up():
    p = RP.PipPerf(RP.PipPuppet(0.9), seed=3, x=960, y=FLOOR, arm_l=180, arm_r=180, elb_l=0, elb_r=0)
    m = alpha(layer(p, 0.0), 160)
    return bbox(m)[1]


def _crinkle_paw_top():
    c = R.Perf2(R.Puppet("crinkle", 1.2), seed=2, x=960, y=FLOOR, arm_l=180, arm_r=180, elb_l=0, elb_r=0)
    return min(c.paw(0.0, "l")[0][1], c.paw(0.0, "r")[0][1])


def layer(perf, t):
    im = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    perf.draw(im, t, CAM)
    return im


def alpha(im, thr=8):
    return np.asarray(im.getchannel("A")) > thr


def bbox(mask):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return (xs.min() / RES, ys.min() / RES + LAND_Y0, (xs.max() + 1) / RES, (ys.max() + 1) / RES + LAND_Y0)


PIP_TOP = _pip_top_arms_up()
CR_PAW_TOP = _crinkle_paw_top()
SHELF_TOP = round(PIP_TOP - 30)          # >= 30 above Pip's highest wing tip


def background():
    im = Image.new("RGBA", (FW, FH), (240, 230, 206, 255))
    d = ImageDraw.Draw(im)
    rect(d, 0, 560, 1920, 1350, (240, 230, 206), None)
    for i in range(14):                                       # paper bunting (circles, no letters)
        x = 160 + i * 120
        ell(d, x, 700 + 18 * math.sin(i), 26, 26, (RED, BLUE, YEL)[i % 3], None)
    rect(d, 0, 1330, 1920, 1352, (226, 208, 178), None)
    rect(d, 0, 1352, 1920, 1640, (222, 184, 140), None)
    for y in (1400, 1460, 1530, 1610):
        d.line([S((0, y)), S((1920, y))], fill=(204, 164, 120), width=_w(2))
    ell(d, (RUG[0] + RUG[1]) / 2, 1500, (RUG[1] - RUG[0]) / 2, 62, (150, 196, 170), (120, 170, 146), 6)
    # shelf: white, top out of Pip's reach, star cubby (the cushion's home) on the lower level
    x0, x1 = SHELF
    rect(d, x0, SHELF_TOP, x1, FLOOR - 6, WHITE, (200, 196, 188), 5)
    mid = (SHELF_TOP + FLOOR) / 2
    d.line([S((x0, mid)), S((x1, mid))], fill=(200, 196, 188), width=_w(5))
    rect(d, x0 + 20, mid + 14, x0 + 250, FLOOR - 20, (232, 236, 246), (200, 196, 188), 3)
    star(d, x0 + 135, mid + 34, 16, BLUE)
    return im


def toybox_back(d):
    x0, x1, top = BOX
    rect(d, x0, top - 20, x1, GROUND - 10, WOOD_D, None)


def toybox_front(d, cushion_in=False):
    x0, x1, top = BOX
    if cushion_in:
        ell(d, 400, top - 4, 80, 34, BLUE)
        star(d, 380, top - 10, 10)
    rect(d, x0, top, x1, GROUND, WOOD, INK, 4, 6)
    star(d, (x0 + x1) / 2, (top + GROUND) / 2, 22, (250, 230, 160))


def ball(d, x, y=GROUND - BALL_R):
    ell(d, x, y, BALL_R, BALL_R, YEL)
    d.chord([S((x - BALL_R, y - 14)), S((x + BALL_R, y + 14))], 0, 360, fill=WHITE)
    ell(d, x, y, BALL_R, BALL_R, None)


def ball_mask(x, y=GROUND - BALL_R):
    im = Image.new("L", (FW, FH), 0)
    ImageDraw.Draw(im).ellipse([S((x - BALL_R, y - BALL_R)), S((x + BALL_R, y + BALL_R))], fill=255)
    return np.asarray(im) > 0


def cushion_pts(cx, base=GROUND, w=240, top=GROUND - 2 * BALL_R - 55):
    pts = [(cx - w / 2, base)]
    for i in range(25):
        a = math.pi * i / 24
        pts.append((cx - w / 2 * math.cos(a), base - (base - top) * math.sin(a) ** 0.6))
    pts.append((cx + w / 2, base))
    return pts


def cushion(d, cx, cy=None, flat=False, w=240):
    if cy is not None:                                     # held / falling: a flat blue pillow
        rect(d, cx - w / 2, cy - 40, cx + w / 2, cy + 40, BLUE, INK, 3, 34)
        for k in (-70, 0, 70):
            star(d, cx + k, cy, 13)
        return
    poly(d, cushion_pts(cx, w=w), BLUE)
    for k in (-60, 0, 60):
        star(d, cx + k, GROUND - 60 + abs(k) * 0.4, 13)


def cushion_mask(cx, w=240):
    im = Image.new("L", (FW, FH), 0)
    ImageDraw.Draw(im).polygon([S(p) for p in cushion_pts(cx, w=w)], fill=255)
    return np.asarray(im) > 0


def block(d, x, s=40, col=RED, base=GROUND):
    rect(d, x - s / 2, base - s, x + s / 2, base, col, INK, 3, 4)


def drum(d, x, base=GROUND):
    rect(d, x - 36, base - 52, x + 36, base, RED, INK, 3, 4)
    ell(d, x, base - 52, 36, 10, (250, 236, 220))


def truck(d, x, base=GROUND):
    rect(d, x - 36, base - 34, x + 30, base - 10, RED, INK, 3, 4)
    rect(d, x + 4, base - 50, x + 30, base - 30, RED, INK, 3, 4)
    for k in (-24, 18):
        ell(d, x + k, base - 9, 9, 9, INK, None)


def boat(d, x, base=GROUND):
    poly(d, [(x - 44, base - 30), (x + 44, base - 30), (x + 30, base), (x - 30, base)], BLUE)
    poly(d, [(x, base - 30), (x, base - 74), (x + 30, base - 34)], WHITE)


def bucket(d, x, base=GROUND):
    poly(d, [(x - 32, base - 56), (x + 32, base - 56), (x + 26, base), (x - 26, base)], BLUE)


def toy_duck(d, x, base=GROUND):
    ell(d, x, base - 16, 24, 16, YEL)
    ell(d, x + 14, base - 38, 13, 13, YEL)


def cup(d, x, base=GROUND):
    poly(d, [(x - 17, base - 36), (x + 17, base - 36), (x + 13, base), (x - 13, base)], YEL)


TRAIN = [(0, 60), (66, 46), (118, 46), (170, 46), (222, 46)]   # engine + 4 carriages: (offset, length)


def train(d, x, base=GROUND, flip=False):
    """x = the engine's nose; flip: runs to the left of x."""
    for off, L in TRAIN:
        a = x - off - L if flip else x + off
        rect(d, a, base - (52 if off == 0 else 40), a + L, base - 10, RED, INK, 3, 5)
        for k in (10, L - 10):
            ell(d, a + k, base - 8, 8, 8, INK, None)
    end = x - 282 if flip else x + 282
    return end


def basket(d, cx, col, base=GROUND, items=()):
    w, h = BASKET_W, BASKET_H
    for fn in items:
        fn(d, cx, base - 40)
    poly(d, [(cx - w / 2, base - h), (cx + w / 2, base - h), (cx + w / 2 - 10, base), (cx - w / 2 + 10, base)], WICKER)
    rect(d, cx - w / 2, base - h, cx + w / 2, base - h + 18, col, INK, 3, 4)
    ell(d, cx, base - h / 2 + 4, 20, 20, col)


def baskets_on_shelf(d):
    for i, col in enumerate((RED, BLUE, YEL)):
        basket(d, SHELF[0] + 80 + 150 * i, col, base=SHELF_TOP)


def baskets_on_floor(d, items=None):
    items = items or {}
    for name, col in (("red", RED), ("blue", BLUE), ("yellow", YEL)):
        basket(d, BASKET_FLOOR[name], col, items=items.get(name, ()))


def qmark(d, cx, cy, s=34):
    """The '?' icon, drawn (not typed)."""
    d.arc([S((cx - s, cy - 2 * s)), S((cx + s, cy))], 190, 405, fill=INK, width=_w(10))
    d.line([S((cx + s * 0.25, cy - s * 0.15)), S((cx, cy + s * 0.5))], fill=INK, width=_w(10))
    ell(d, cx, cy + s * 0.95, 7, 7, INK, None)


# ---------------------------------------------------------------- cast
def snip(x, **kw):
    p = R.Perf2(R.Puppet("snip", 1.15), seed=1, x=x, y=FLOOR, **kw)
    p.acting(blink="soft", auto_blink=False)
    return p


def crinkle(x, **kw):
    p = R.Perf2(R.Puppet("crinkle", 1.2), seed=2, x=x, y=FLOOR, **kw)
    p.acting(blink="soft", auto_blink=False)
    return p


def pip(x, **kw):
    return RP.PipPerf(RP.PipPuppet(0.9), seed=3, x=x, y=FLOOR, **kw)


T_DRAW = 1.0


def head_mask(perf, t=T_DRAW):
    m = alpha(layer(perf, t), 160)
    st = perf.state(t)
    sy = min(perf.a.shoulder(st, "l")[1], perf.a.shoulder(st, "r")[1])
    m = m.copy()
    m[max(0, int((sy - 4 - LAND_Y0) * RES)):, :] = False
    return m


def window(centre, z):
    w, h = 1920 / z, 1080 / z
    x0 = min(max(centre[0] - w / 2, 0), 1920 - w)
    y0 = min(max(centre[1] - h / 2, LAND_Y0), LAND_Y0 + 1080 - h)
    return (x0, y0, x0 + w, y0 + h)


def fit(boxes, z):
    """Centre a camera of zoom z on the union of world boxes (heads and objects that must be whole)."""
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    return window(((x0 + x1) / 2, (y0 + y1) / 2), z)


def margin(win, b):
    """Smallest distance (design units) from box b to the window edges (negative = cut)."""
    return min(b[0] - win[0], b[1] - win[1], win[2] - b[2], win[3] - b[3])


# ---------------------------------------------------------------- the 12 storyboard frames
BALL_REST = 780                           # ball at rest by the box (Snip at 500, facing it)
BLOCK_X = 990


def frame(T):
    """Returns (image 3840x2160, camera window, info dict) for a storyboard time."""
    bg = background()
    d = ImageDraw.Draw(bg)
    toybox_back(d)
    behind, front, cast, req, info = [], [], [], [], {}
    after = []                                            # (fn) drawn after the characters

    if T == 0.5:
        sn = snip(420, turn=0.5, eyes="happy", mouth="smile_open"); sn.emote(0, 0.3, "delighted")
        sn.reach(0, 0.3, "r", (520, 1330)); sn.reach(0, 0.3, "l", (470, 1300))
        pp = pip(760, turn=0.5, eyes="happy", mouth="smile_open"); pp.reach(0, 0.3, "r", (840, 1420))
        cr = crinkle(1180, turn=-0.5, eyes="happy", mouth="smile"); cr.reach(0, 0.3, "l", (1090, 1430))
        cast = [sn, pp, cr]
        behind += [lambda d: baskets_on_shelf(d), lambda d: block(d, BLOCK_X), lambda d: boat(d, 640),
                   lambda d: block(d, 1290, 40, BLUE), lambda d: toy_duck(d, 1320), lambda d: drum(d, 230)]
        after += [lambda d: ball(d, 900), lambda d: truck(d, 540, 1380), lambda d: toybox_front(d, True)]
        win = window((960, 1100), 1.0)
    elif T == 4.0:
        sn = snip(520, turn=0.3, eyes="closed", mouth="smile_open", head_dy=34, sq=0.9)
        sn.ears(0, 0.3, "droop"); sn.reach(0, 0.3, "r", (600, 1420)); sn.reach(0, 0.3, "l", (430, 1430))
        pp = pip(820, turn=-0.4, eyes="happy", mouth="smile_open"); pp.flap(0.5, 1.4)
        cr = crinkle(1180, turn=-0.5, eyes="happy", mouth="smile_open")
        cast = [sn, pp, cr]
        behind += [lambda d: baskets_on_shelf(d), lambda d: block(d, BLOCK_X), lambda d: boat(d, 700),
                   lambda d: toy_duck(d, 1320)]
        after += [lambda d: train(d, 610), lambda d: ball(d, 900), lambda d: toybox_front(d, True)]
        win = window((960, 1100), 1.0)
    elif T == 8.3:
        pp = pip(760, turn=0.6, eyes="open", mouth="o"); pp.reach(0, 0.3, "r", (860, 1400))
        pp.reach(0, 0.3, "l", (700, 1380))
        cr = crinkle(1230, turn=-0.5, eyes="open", mouth="smile"); cr.reach(0, 0.3, "l", (1140, 1430))
        cast = [pp, cr]
        behind += [lambda d: block(d, BLOCK_X)]
        after += [lambda d: ball(d, BLOCK_X - 80)]
        info["ball_x"] = BLOCK_X - 80
        win = window((870, 1300), 2.0)
    elif T == 10.2:
        sn = snip(470, turn=-1.0, eyes="open", mouth="smile", lean=-35, head_dy=120)
        sn.emote(0, 0.3, "neutral"); sn.reach(0, 0.3, "l", (380, 1400)); sn.reach(0, 0.3, "r", (600, 1180))
        pp = pip(940, turn=-0.6, eyes="open", mouth="o")
        cast = [sn, pp]
        behind += [lambda d: ball(d, BALL_REST)]
        after += [lambda d: cushion(d, BALL_REST - 20, 1300), lambda d: toybox_front(d)]
        info["ball_x"] = BALL_REST; info["cushion_w"] = 240
        win = window((750, 1115), 1.4)            # plan 1.6: Snip whole + box/ball need <= 1.40
    elif T == 17.5:
        pp = pip(840, turn=-0.2, eyes="open", brows="worry", mouth="flat")
        pp.reach(0, 0.3, "r", (800, 1390)); pp.reach(0, 0.3, "l", (880, 1390))
        cr = crinkle(1040, turn=-0.6, eyes="open", brows="worry", mouth="smile", head_dy=30, lean=-8)
        cast = [pp, cr]
        behind += [lambda d: cushion(d, BALL_REST)]
        after += [lambda d: qmark(d, 860, 1150)]
        win = window((930, 1290), 1.5)
    elif T == 24.0:
        cr = crinkle(1010, turn=-0.4, eyes="wide", brows="up", mouth="smile_open")
        cr.hop(0.8, 1.2, 1, 30); cr.arms_front.append((0, 9))
        cr.reach(0, 0.3, "l", (975, 1110)); cr.reach(0, 0.3, "r", (1045, 1110))
        pp = pip(800, turn=0.6, eyes="happy", mouth="smile_open"); pp.tuft(0, 0.3, "up")
        cast = [pp, cr]
        win = window((960, 1240), 1.8)
    elif T == 31.0:
        sn = snip(470, turn=0.6, eyes="open", brows="sad", mouth="flat"); sn.emote(0, 0.3, "sad")
        sn.ears(0, 0.3, "droop"); sn.reach(0, 0.3, "r", (540, 1290)); sn.reach(0, 0.3, "l", (505, 1300))
        pp = pip(900, turn=-0.5, eyes="open", brows="worry", mouth="flat")
        cast = [sn, pp]
        behind += [lambda d: cushion(d, BALL_REST), lambda d: block(d, 800, 40, BLUE)]
        after += [lambda d: drum(d, 530, 1330)]
        info["heap"] = True
        win = window((760, 1115), 1.4)            # plan 1.5 -> 1.40 (fit)
    elif T == 38.8:
        sn = snip(500, turn=0.4, eyes="happy", mouth="smile_open")
        pp = pip(840, turn=0.4, eyes="happy", mouth="smile_open")
        cr = crinkle(1120, turn=-0.6, eyes="happy", mouth="smile")
        cast = [sn, pp, cr]
        behind += [lambda d: baskets_on_shelf(d), lambda d: cushion(d, BALL_REST), lambda d: drum(d, BALL_REST, 1370),
                   lambda d: boat(d, 650), lambda d: block(d, 790, 40, BLUE), lambda d: toy_duck(d, 690)]
        after += [lambda d: train(d, 1182), lambda d: d.line([S((1150, 1350)), S((1182, 1462))], fill=INK, width=_w(4)),
                  lambda d: toybox_front(d)]
        info["heap"] = True
        win = window((960, 1100), 1.0)
    elif T == 51.2:
        cr = crinkle(1360, turn=0.5, eyes="happy", mouth="smile", lean=8)
        cr.reach(0, 0.3, "r", (1470, 1400)); cr.reach(0, 0.3, "l", (1430, 1410))
        pp = pip(1090, turn=0.5, eyes="happy", mouth="smile_open")
        cast = [pp, cr]
        after += [lambda d: baskets_on_floor(d, {"red": (lambda d, x, b: train(d, x - 110, b - 30),)})]
        info["key"] = [(BASKET_FLOOR["red"] - 140, GROUND - 120, BASKET_FLOOR["red"] + BASKET_W / 2, GROUND)]
        win = window((1400, 1200), 1.3)
    elif T == 63.0:
        sn = snip(480, turn=0.5, eyes="happy", mouth="smile_open")
        cr = crinkle(1020, turn=0.5, eyes="happy", mouth="smile_open")
        pp = pip(1360, turn=0.6, eyes="happy", mouth="smile")
        cast = [sn, cr, pp]
        behind += [lambda d: cushion(d, BALL_REST), lambda d: drum(d, BALL_REST, 1370), lambda d: bucket(d, 860)]
        after += [lambda d: baskets_on_floor(d, {"red": (drum,), "blue": (boat,)}), lambda d: teddy(d, 1372),
                  lambda d: toybox_front(d)]
        info["teddy"] = True; info["heap"] = True
        win = window((960, 1100), 1.0)
    elif T == 97.8:
        sn = snip(560, turn=0.5, eyes="happy", mouth="smile_open"); sn.emote(0, 0.3, "delighted")
        sn.reach(0, 0.3, "r", (560, 1300)); sn.reach(0, 0.3, "l", (690, 1300))
        pp = pip(900, turn=-0.5, eyes="happy", mouth="smile_open", arm_l=150, arm_r=150)
        cast = [sn, pp]
        behind += [lambda d: ball(d, BALL_REST)]
        after += [lambda d: cushion(d, 625, 1290, w=220)]
        info["key"] = [(BALL_REST - BALL_R, GROUND - 2 * BALL_R, BALL_REST + BALL_R, GROUND), (515, 1250, 735, 1330)]
        info["ball_x"] = BALL_REST
        win = window((740, 1115), 1.4)            # plan 1.5 -> 1.40 (fit)
    elif T == 119.0:
        pp = pip(1700, turn=0.6, eyes="happy", mouth="smile_open")
        pp.reach(0, 0.3, "r", (1790, 1340)); pp.reach(0, 0.3, "l", (1760, 1350))
        cast = [pp]
        after += [lambda d: baskets_on_floor(d, {"red": (drum,), "blue": (boat,), "yellow": (toy_duck,)}),
                  lambda d: ball(d, 1815, 1360)]
        info["key"] = [(1815 - BALL_R, 1305, 1820 + BASKET_W / 2, GROUND)]
        win = window((1700, 1320), 1.8)
    else:
        raise SystemExit(f"no storyboard frame at {T}")

    for fn in behind:
        fn(d)
    layers = [layer(p, T_DRAW) for p in cast]
    for L in layers:
        bg.alpha_composite(L)
    d = ImageDraw.Draw(bg)
    for fn in after:
        fn(d)
    info["cast"] = cast
    info["layers"] = layers
    return bg, win, info


TEDDY_H = None


def teddy(d, x):
    """The big teddy held in front of Pip: only her feet show below it."""
    global TEDDY_H
    p = pip(x)
    top = bbox(alpha(layer(p, 0.0), 160))[1] - 8
    bot = FLOOR - 26
    TEDDY_H = bot - top
    ell(d, x, (top + bot) / 2 + 20, 64, (bot - top) / 2 - 18, YEL)
    ell(d, x, top + 40, 46, 40, YEL)
    for k in (-34, 34):
        ell(d, x + k, top + 8, 14, 14, YEL)
    ell(d, x - 14, top + 36, 4, 4, INK, None); ell(d, x + 14, top + 36, 4, 4, INK, None)


def shoot(img, win, size=(1920, 1080)):
    box = (win[0] * RES, (win[1] - LAND_Y0) * RES, win[2] * RES, (win[3] - LAND_Y0) * RES)
    return img.convert("RGB").resize(size, Image.LANCZOS, box=box)


FRAMES = (0.5, 4.0, 8.3, 10.2, 17.5, 24.0, 31.0, 38.8, 51.2, 63.0, 97.8, 119.0)


def sheet():
    out = os.path.join(ROOT, "build", "sb1")
    os.makedirs(os.path.join(out, "ep12"), exist_ok=True)
    tw, th, lab = 780, 439, 40
    sh = Image.new("RGB", (3 * tw + 4 * 12, 4 * (th + lab) + 5 * 12), (250, 250, 250))
    try:
        font = ImageFont.load_default(size=30)
    except TypeError:
        font = ImageFont.load_default()
    for i, T in enumerate(FRAMES):
        img, win, _ = frame(T)
        full = shoot(img, win)
        full.save(os.path.join(out, "ep12", f"f_{T:05.1f}.png"))
        x, y = 12 + (i % 3) * (tw + 12), 12 + (i // 3) * (th + lab + 12)
        ImageDraw.Draw(sh).text((x + 4, y + 4), f"{T:.1f} s", fill=(30, 30, 30), font=font)
        sh.paste(full.resize((tw, th), Image.LANCZOS), (x, y + lab))
    sh.save(os.path.join(out, "storyboard.png"))
    print("sheet", os.path.join(out, "storyboard.png"), sh.size)


# ---------------------------------------------------------------- the 24 shot cameras (plan zooms; staging from this set)
def _boxes():
    mid = (SHELF_TOP + FLOOR) / 2
    bf = {k: (x - BASKET_W / 2, GROUND - BASKET_H, x + BASKET_W / 2, GROUND) for k, x in BASKET_FLOOR.items()}
    return dict(
        box=(BOX[0], BOX[2] - 20, BOX[1], GROUND), ball=(BALL_REST - BALL_R, GROUND - 110, BALL_REST + BALL_R, GROUND),
        heap=(BALL_REST - 120, GROUND - 132, BALL_REST + 120, GROUND), fall=(BALL_REST - 140, 1260, BALL_REST + 100, 1340),
        shelf=(SHELF[0], SHELF_TOP - BASKET_H, SHELF[1], FLOOR), cubby=(SHELF[0] + 20, mid + 14, SHELF[0] + 250, FLOOR - 20),
        rug=(RUG[0], 1438, RUG[1], 1562), red=bf["red"], blue=bf["blue"], yellow=bf["yellow"],
        roll=(BLOCK_X - 80 - BALL_R, GROUND - 110, BLOCK_X + 20, GROUND), wing=(690, 1340, 830, 1440),
        hook=(1120, 1340, 1242, 1470), c3=(1700, 1330, 1895, GROUND), c21=(1760, 1305, 1895, GROUND))


# (shot, zoom, {who: x}, heads that must be whole, objects that must be whole)
SHOT_ROWS = [
    (1, 1.0, dict(sn=420, pip=760, cr=1180), "sn pip cr", "box shelf"),
    (2, 2.0, dict(pip=760, cr=1230), "", "roll wing"),
    (3, 1.6, dict(sn=500, pip=940), "sn", "box ball fall"),
    (4, 2.0, dict(sn=500, pip=940), "", "heap"),
    (5, 1.5, dict(pip=840, cr=1040), "pip cr", ""),
    (6, 1.8, dict(pip=890, cr=1010), "pip cr", ""),
    (7, 1.5, dict(sn=470, pip=900), "sn pip", "heap"),
    (8, 1.0, dict(sn=500, pip=840, cr=1120), "sn pip cr", "heap"),
    (9, 2.0, dict(sn=560, pip=840, cr=1120), "", "hook"),
    (10, 1.0, dict(sn=560, pip=840, cr=1120), "sn pip cr", "hook"),
    (11, 1.3, dict(pip=1180, cr=1360), "pip cr", "shelf"),
    (12, 2.0, dict(pip=1700), "", "c3"),
    (13, 1.0, dict(sn=660, cr=1020, pip=1360), "sn pip cr", "red blue yellow"),
    (14, 1.5, dict(sn=1600, pip=1780), "sn pip", "blue"),
    (15, 1.0, dict(pip=700, sn=1000, cr=1300), "sn pip cr", "red blue yellow"),
    (16, 1.6, dict(cr=1600, sn=1780), "cr sn", "blue"),
    (17, 1.5, dict(sn=560, pip=900), "sn pip", "heap"),
    (18, 2.0, dict(sn=560, pip=900), "", "ball"),
    (19, 1.5, dict(pip=1200, sn=1380), "sn pip", "cubby"),
    (20, 1.4, dict(pip=700, cr=1000, sn=1250), "sn pip cr", "rug red blue yellow"),
    (21, 1.8, dict(pip=1700), "pip", "c21 yellow"),
    (22, 1.0, dict(sn=1100, cr=1400, pip=1700), "sn pip cr", "red blue yellow"),
    (23, 1.5, dict(cr=1600, pip=1760), "cr pip", "yellow"),
    (24, 1.0, dict(sn=760, pip=960, cr=1160), "sn pip cr", "rug"),
]
MAKE = {"sn": lambda x: snip(x, turn=0.3), "cr": lambda x: crinkle(x, turn=-0.3), "pip": lambda x: pip(x, turn=0.3)}


def shot_table():
    B = _boxes()
    rows = []
    for n, z, who, heads, objs in SHOT_ROWS:
        hb = {k: bbox(head_mask(MAKE[k](x))) for k, x in who.items()}
        need = [hb[k] for k in heads.split()] + [B[o] for o in objs.split()]
        win = fit(need, z)
        ms = {k: round(margin(win, hb[k])) for k in heads.split()}
        mo = {o: round(margin(win, B[o])) for o in objs.split()}
        ux0 = min(b[0] for b in need); uy0 = min(b[1] for b in need)
        ux1 = max(b[2] for b in need); uy1 = max(b[3] for b in need)
        zmax = min(1920 / (ux1 - ux0 + 20), 1080 / (uy1 - uy0 + 20), 2.0)
        ms["zmax(10u)"] = round(zmax, 2)
        rows.append((n, z, win, ms, mo))
    return rows


# ---------------------------------------------------------------- measure
def _dist_to_ball(L, bx, by=GROUND - BALL_R):
    ys, xs = np.nonzero(alpha(L, 160))
    wx, wy = xs / RES, ys / RES + LAND_Y0
    return float(np.sqrt((wx - bx) ** 2 + (wy - by) ** 2).min() - BALL_R)


def pip_a2_test():
    p = pip(960)
    try:
        p.acting(blink="soft")
        for i, name in enumerate(("sad", "delighted", "curious", "cross", "neutral")):
            p.emote(0.2 + i, 0.5 + i, name)
        p.dart(5.0, 10, -2)
        p.blink(5.5, preset="slow")
        p.blink(6.0, preset="quick")
    except Exception as e:  # noqa: BLE001
        return f"A2 calls FAIL: {e!r}", None
    ts = (0.0, 1.0, 2.0, 3.0, 4.0, 4.9, 5.1, 5.62, 6.04)
    ims = []
    for t in ts:
        try:
            ims.append(layer(p, t))
        except Exception as e:  # noqa: BLE001
            return f"A2 draw FAIL at {t}: {e!r}", None
    hb = bbox(head_mask(p, 0.0))
    box = (int(hb[0] * RES), int((hb[1] - LAND_Y0) * RES), int(hb[2] * RES), int((hb[3] - LAND_Y0) * RES) + 40)
    base = np.asarray(ims[0].crop(box)).astype(int)
    diffs = {t: int((np.abs(np.asarray(im.crop(box)).astype(int) - base).sum(axis=2) > 40).sum()) for t, im in zip(ts, ims)}
    strip = Image.new("RGB", ((box[2] - box[0]) * len(ts), box[3] - box[1]), (255, 255, 255))
    for i, im in enumerate(ims):
        strip.paste(im.crop(box), ((box[2] - box[0]) * i, 0), im.crop(box))
    path = os.path.join(ROOT, "build", "sb1", "ep12", "pip_a2.png")
    strip.save(path)
    return diffs, path


def measure(frames):
    out = []
    pr = lambda *a: out.append(" ".join(str(x) for x in a))  # noqa: E731
    pr("PIP_TOP (arms up, world y)", round(PIP_TOP), "SHELF_TOP", SHELF_TOP, "-> shelf top above wing tip:", round(PIP_TOP - SHELF_TOP))
    pr("Crinkle paw top (arms up)", round(CR_PAW_TOP), "basket band on shelf top at", SHELF_TOP - BASKET_H + 9,
       "-> reach margin:", round(SHELF_TOP - BASKET_H + 9 - CR_PAW_TOP))
    pm = alpha(layer(pip(960), 0.0), 160)
    bot = pm[-1:0:-1].any(axis=1).argmax()
    rows = pm[pm.shape[0] - 1 - bot - int(12 * RES): pm.shape[0] - bot].any(axis=0)
    xs = np.nonzero(rows)[0]
    gaps = np.diff(xs)
    pr("Pip foot gap (units):", round((gaps.max() - 1) / RES, 1) if len(gaps) else 0, "ball 110 ->",
       round((gaps.max() - 1) / RES - 2 * BALL_R, 1) if len(gaps) else -110)
    for T, (img, win, info) in frames.items():
        ww = win[2] - win[0]
        line = [f"t={T} win=({win[0]:.0f},{win[1]:.0f})-({win[2]:.0f},{win[3]:.0f}) z={1920 / ww:.2f}"]
        if T == 8.3:
            line.append(f"ball width {100 * 2 * BALL_R / ww:.1f}%")
        if T == 10.2:
            line.append(f"cushion width {100 * info['cushion_w'] / ww:.1f}%")
        if "key" in info:
            ks = info["key"]
            x0 = min(b[0] for b in ks); x1 = max(b[2] for b in ks)
            line.append(f"key width {100 * (x1 - x0) / ww:.1f}%")
        sn = [L for p, L in zip(info["cast"], info["layers"]) if p.a.kind == "snip"] if info["cast"] else []
        if sn and ("heap" in info or ("ball_x" in info and T < 97)):
            line.append(f"Snip mask to ball {_dist_to_ball(sn[0], BALL_REST):.0f} u")
        if "teddy" in info:
            pl = [L for p, L in zip(info["cast"], info["layers"]) if isinstance(p, RP.PipPerf)][0]
            pb = bbox(alpha(pl, 160))
            line.append(f"Pip feet below teddy {pb[3] - (FLOOR - 26):.0f} u (teddy {TEDDY_H:.0f} tall, {100 * 128 / ww:.1f}% w)")
        for p, L in zip(info["cast"], info["layers"]):
            b = bbox(alpha(L, 160))
            nm = "pip" if isinstance(p, RP.PipPerf) else p.a.kind
            line.append(f"{nm} {100 * (b[2] - b[0]) / ww:.0f}%w {100 * (b[3] - b[1]) / (win[3] - win[1]):.0f}%h")
        pr(" | ".join(line))
    vis = int((ball_mask(BALL_REST) & ~cushion_mask(BALL_REST)).sum())
    pr("ball pixels visible under the cushion:", vis)
    pr("bucket in blue basket: rim margin", (BASKET_W - 64) / 2)
    pr("ball path 107.6-118 to nearest floor toy (red basket):", BASKET_FLOOR["red"] - BASKET_W / 2 - (1250 - 60 + BALL_R) - 0)
    pr("--- shot table: head margins / object margins (units)")
    for n, z, win, ms, mo in shot_table():
        pr(f"shot {n} z{z} x {win[0]:.0f}-{win[2]:.0f} y {win[1]:.0f}-{win[3]:.0f} heads {ms} objs {mo}")
    d, path = pip_a2_test()
    pr("Pip A2 test (changed px in head box vs t=0):", d, path)
    print("\n".join(out))


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--still" in a:
        T = float(a[a.index("--still") + 1])
        img, win, _ = frame(T)
        os.makedirs(os.path.join(ROOT, "build", "sb1", "ep12"), exist_ok=True)
        shoot(img, win).save(os.path.join(ROOT, "build", "sb1", "ep12", f"f_{T:05.1f}.png"))
    if "--sheet" in a or "--all" in a:
        sheet()
    if "--measure" in a or "--all" in a:
        measure({T: frame(T) for T in (4.0, 8.3, 10.2, 24.0, 31.0, 38.8, 51.2, 63.0, 97.8, 119.0)})
