"""Episode 12 rough set, plan r1: re-measure + gate-1b storyboard sb2 (not the episode).

    python3 episodes/ep12_rough_r1.py --measure    numbers for the plan's r1 rows and the gag break sizes
    python3 episodes/ep12_rough_r1.py --sheet      build/sb2/storyboard.png (12 frames, no captions) + build/sb2/ep12/f_T.png
    python3 episodes/ep12_rough_r1.py --still T    one frame -> build/sb2/ep12/f_T.png

Reuses ep12_rough.py (set, cast, helpers). r1 staging measured here:
  * toy chest: its width is set by Snip's head (below the ear base) plus 12 a side; the lid stands upright on a stay
    at the chest's back edge, layered in front of Snip (a lid hinged at the left end would show only its edge);
  * Snip behind the chest 7.6-12.8 with his whole head mask left of the close-ups; Crinkle catches at 1680 so the
    2.0x close-ups (8.3, 10.2) hold every head wholly in or wholly out;
  * the mess on three lanes: UP (behind the cast), MID (the ball's lane), DOWN (in front, tops below the ball);
  * Pip a step upstage in the ball game, so the veered ball passes in front of her toes.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ep12_rough as B  # noqa: E402
from ep12_rough import (BALL_R, BASKET_FLOOR, BASKET_H, BASKET_W, BLUE, FLOOR, GROUND, INK, RED, RES,  # noqa: E402
                        SHELF, WHITE, WOOD, WOOD_D, YEL, alpha, bbox, ell, fit, head_mask, layer, margin, poly, rect,
                        shoot, star, window, S, _w)

RP = B.RP
OUT = os.path.join(B.ROOT, "build", "sb2")
UP, DOWN = 1420, 1604
RUG = (560, 1360)
BOX1, BOX_TOP = 480, 1340
BALL_X = 635                     # ball at rest by the chest's right end; cushion 515-755
BLOCK_X = 1300
CR_GAME = 1680
PIP_GAME_Y = 1440                # Pip 40 upstage in the ball game
PIP_G7_Y = 1430                  # gag 7: Pip 50 upstage of the ball's lane
TOE_H = 15                       # Pip's toe height (rough)
CUR = []                         # (name, box, strewn) of the toys drawn in the current frame


def pip_at(x, y=FLOOR, **kw):
    return RP.PipPerf(RP.PipPuppet(0.9), seed=3, x=x, y=y, **kw)


def snip_behind(x, out=True):
    p = B.snip(x, turn=0.5, eyes="open", mouth="smile", head_dy=80)
    p.emote(0, 0.3, "neutral")
    dx = 0 if out else -70
    p.reach(0, 0.3, "r", (BOX1 + 30 + dx, 1294)); p.reach(0, 0.3, "l", (BOX1 + 2 + dx, 1306))
    return p


def below_ears(m):
    rows = np.nonzero(m.any(axis=1))[0]
    runs = []
    for y in rows:
        xs = np.nonzero(m[y])[0]
        runs.append(max(len(s) for s in np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)))
    runs = np.array(runs)
    eb = rows[int(np.argmax(runs >= 0.5 * runs.max()))]
    m2 = m.copy()
    m2[:eb] = False
    return m2, eb


# ---------------------------------------------------------------- layout from Snip's head
SNIP_BOX_X = 290
for _ in range(2):
    SNIP_BOX_X = round(SNIP_BOX_X - (bbox(head_mask(snip_behind(SNIP_BOX_X)))[2] - (BOX1 - 12)))
_hm = head_mask(snip_behind(SNIP_BOX_X))
_full = bbox(_hm)
_be = bbox(below_ears(_hm)[0])
BOX0 = int(math.floor(_be[0] - 12))
LID_TOP = int(math.floor(_be[1] - 8))
SNIP_HEAD_X1 = _full[2]
C2X0 = SNIP_HEAD_X1 + 12


def T(name, box, strewn=True):
    CUR.append((name, box, strewn))
    return box


# ---------------------------------------------------------------- props (rough, r1 sizes)
def box_back(d):
    rect(d, BOX0, BOX_TOP - 20, BOX1, GROUND - 10, WOOD_D, None)


def lid(d):
    rect(d, BOX0 + 4, LID_TOP, BOX1 - 4, BOX_TOP - 12, (214, 166, 112), INK, 4, 10)
    star(d, (BOX0 + BOX1) / 2, (LID_TOP + BOX_TOP) / 2, 26, (250, 230, 160))
    d.line([S((BOX1 - 12, LID_TOP + 90)), S((BOX1 - 5, BOX_TOP - 4))], fill=INK, width=_w(5))   # the stay


def box_front(d, cushion_in=False):
    if cushion_in:
        ell(d, (BOX0 + BOX1) / 2, BOX_TOP - 6, 110, 36, BLUE)
        star(d, (BOX0 + BOX1) / 2 - 20, BOX_TOP - 12, 12)
    rect(d, BOX0, BOX_TOP, BOX1, GROUND, WOOD, INK, 4, 6)
    star(d, (BOX0 + BOX1) / 2, (BOX_TOP + GROUND) / 2, 26, (250, 230, 160))


def occluder():
    im = Image.new("RGBA", (B.FW, B.FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lid(d); box_front(d)
    return alpha(im, 0)


def drum2(d, x, base=GROUND, strewn=True):
    rect(d, x - 65, base - 100, x + 65, base, RED, INK, 3, 6)
    for k in range(5):
        d.line([S((x - 60 + 26 * k, base - 88)), S((x - 47 + 26 * k, base - 14))], fill=WHITE, width=_w(3))
    ell(d, x, base - 100, 65, 12, (250, 236, 220))
    return T("drum", (x - 65, base - 112, x + 65, base), strewn)


def truck2(d, x, base=GROUND, strewn=True):
    rect(d, x - 70, base - 62, x + 70, base - 18, RED, INK, 3, 6)
    rect(d, x + 14, base - 110, x + 66, base - 58, RED, INK, 3, 6)
    rect(d, x + 26, base - 100, x + 56, base - 76, (200, 226, 240), INK, 2, 3)
    for k in (-44, 42):
        ell(d, x + k, base - 18, 18, 18, INK, None)
    return T("truck", (x - 70, base - 110, x + 70, base), strewn)


def boat2(d, x, base=GROUND, strewn=True):
    poly(d, [(x - 70, base - 50), (x + 70, base - 50), (x + 50, base), (x - 50, base)], BLUE)
    d.line([S((x, base - 50)), S((x, base - 140))], fill=INK, width=_w(4))
    poly(d, [(x + 4, base - 136), (x + 4, base - 56), (x + 58, base - 60)], WHITE)
    return T("boat", (x - 70, base - 140, x + 70, base), strewn)


def bucket2(d, x, base=GROUND, strewn=True):
    poly(d, [(x - 48, base - 80), (x + 48, base - 80), (x + 38, base), (x - 38, base)], BLUE)
    d.arc([S((x - 44, base - 120)), S((x + 44, base - 40))], 180, 360, fill=INK, width=_w(4))
    return T("bucket", (x - 48, base - 80, x + 48, base), strewn)


def block50(d, x, col=RED, base=GROUND, name="block", strewn=True):
    rect(d, x - 25, base - 50, x + 25, base, col, INK, 3, 5)
    return T(name, (x - 25, base - 50, x + 25, base), strewn)


def duck2(d, x, base=GROUND, strewn=True):
    ell(d, x, base - 22, 34, 22, YEL)
    ell(d, x + 20, base - 54, 18, 18, YEL)
    poly(d, [(x + 36, base - 58), (x + 50, base - 52), (x + 36, base - 48)], (240, 150, 60))
    ell(d, x + 24, base - 58, 3, 3, INK, None)
    return T("duck", (x - 34, base - 72, x + 50, base), strewn)


def cup2(d, x, base=GROUND, strewn=True):
    poly(d, [(x - 22, base - 50), (x + 22, base - 50), (x + 17, base), (x - 17, base)], YEL)
    return T("cup", (x - 22, base - 50, x + 22, base), strewn)


def teddy_lying(d, x0, base=GROUND, strewn=True):
    ell(d, x0 + 200, base - 52, 118, 52, YEL)
    for k in (150, 250):
        ell(d, x0 + k, base - 12, 30, 14, YEL)
    ell(d, x0 + 62, base - 62, 60, 60, YEL)
    for k in (22, 100):
        ell(d, x0 + k, base - 112, 18, 18, YEL)
    ell(d, x0 + 44, base - 70, 5, 5, INK, None); ell(d, x0 + 78, base - 70, 5, 5, INK, None)
    d.arc([S((x0 + 46, base - 62)), S((x0 + 78, base - 40))], 20, 160, fill=INK, width=_w(3))
    return T("teddy", (x0, base - 130, x0 + 318, base), strewn)


PIECES = [(0, 100, 80)] + [(107 + 85 * i, 78, 66) for i in range(4)]     # engine + 4 carriages = 440 long


def train2(d, x, base=GROUND, flip=False, strewn=True):
    xs = []
    for off, L, h in PIECES:
        a = x - off - L if flip else x + off
        rect(d, a, base - h, a + L, base - 12, RED, INK, 3, 6)
        if off == 0:
            cx = a + L - 30 if flip else a + 18
            rect(d, cx, base - 100, cx + 20, base - h, RED, INK, 3, 3)
        for k in (14, L - 14):
            ell(d, a + k, base - 12, 12, 12, INK, None)
        xs += [a, a + L]
    return T("train", (min(xs), base - 100, max(xs), base), strewn)


def train_stack(d, cx, base):
    """The unhooked pieces end-on in a basket (3 below, 2 poking up)."""
    for k, dy in ((-48, 0), (0, 0), (48, 0), (-24, 60), (24, 60)):
        rect(d, cx + k - 22, base - dy - 66, cx + k + 22, base - dy, RED, INK, 3, 6)
        ell(d, cx + k, base - dy - 10, 9, 9, INK, None)


def heap2(d, x0, base=GROUND, strewn=True):
    block50(d, x0 + 30, RED, base, strewn=False); block50(d, x0 + 85, BLUE, base, strewn=False)
    block50(d, x0 + 140, YEL, base, strewn=False); cup2(d, x0 + 185, base, strewn=False)
    duck2(d, x0 + 58, base - 50, strewn=False); block50(d, x0 + 135, RED, base - 50, strewn=False)
    for _ in range(6):
        CUR.pop()
    return T("heap", (x0, base - 122, x0 + 207, base), strewn)


def basket2(d, cx, col, base=GROUND, items=()):
    for fn in items:
        fn(d, cx, base - 40)
    w, h = BASKET_W, BASKET_H
    poly(d, [(cx - w / 2, base - h), (cx + w / 2, base - h), (cx + w / 2 - 10, base), (cx - w / 2 + 10, base)], B.WICKER)
    rect(d, cx - w / 2, base - h, cx + w / 2, base - h + 18, col, INK, 3, 4)
    ell(d, cx, base - h / 2 + 4, 20, 20, col)


def baskets_floor(d, items):
    for name, col in (("red", RED), ("blue", BLUE), ("yellow", YEL)):
        basket2(d, BASKET_FLOOR[name], col, items=items.get(name, ()))


def inb(fn):
    return lambda d, x, b: fn(d, x, b, strewn=False)


def background2():
    im = B.background()
    ell(ImageDraw.Draw(im), 960, 1522, 400, 104, (150, 196, 170), (120, 170, 146), 6)
    return im


def mess_start(up, down):
    up += [lambda d: drum2(d, 640, UP), lambda d: teddy_lying(d, 760, UP), lambda d: boat2(d, 1200, UP)]
    down += [lambda d: train2(d, 470, DOWN), lambda d: bucket2(d, 960, DOWN), lambda d: heap2(d, 1340, DOWN)]


# ---------------------------------------------------------------- the 12 storyboard frames (plan r1)
FRAMES = (0.5, 8.3, 9.6, 10.2, 17.5, 24.0, 31.0, 38.8, 51.2, 63.0, 97.8, 119.0)
ZOOM = {0.5: 1.0, 8.3: 2.0, 9.6: 1.4, 10.2: 2.0, 17.5: 1.4, 24.0: 1.4, 31.0: 1.4, 38.8: 1.0, 51.2: 1.3, 63.0: 1.0,
        97.8: 1.4, 119.0: 1.8}


def frame(T_):
    del CUR[:]
    bg = background2()
    d = ImageDraw.Draw(bg)
    box_back(d)
    up, under, cast, over, down, req, info = [], [], [], [], [], [], {}
    cushion_box = (BALL_X - 120, GROUND - 165, BALL_X + 120, GROUND)
    ball_box = (BALL_X - BALL_R, GROUND - 2 * BALL_R, BALL_X + BALL_R, GROUND)
    chest = (BOX0, LID_TOP, BOX1, GROUND)
    win = None
    if T_ == 0.5:
        sn = B.snip(620, turn=0.4, eyes="happy", mouth="smile_open"); sn.emote(0, 0.3, "delighted")
        sn.reach(0, 0.3, "r", (735, 1290)); sn.reach(0, 0.3, "l", (650, 1300))
        pp = pip_at(900, PIP_GAME_Y, turn=0.5, eyes="happy", mouth="smile_open"); pp.reach(0, 0.3, "r", (980, 1400))
        cr = B.crinkle(CR_GAME, turn=-0.5, eyes="happy", mouth="smile"); cr.reach(0, 0.3, "l", (1560, 1420))
        cast = [sn, pp, cr]
        mess_start(up, down)
        over += [lambda d: lid(d), lambda d: box_front(d, True), lambda d: block50(d, BLOCK_X, RED, name="red block"),
                 lambda d: B.ball(d, 1000), lambda d: truck2(d, 690, 1345, strewn=False)]
        win = window((960, 1100), 1.0)
    elif T_ in (8.3, 9.6, 10.2):
        sn = snip_behind(SNIP_BOX_X, out=T_ == 9.6)
        pp = pip_at(900, PIP_GAME_Y, turn=0.6 if T_ == 8.3 else -0.5, eyes="open", mouth="o",
                    brows="worry" if T_ > 9 else "calm")
        if T_ == 8.3:
            pp.reach(0, 0.3, "r", (985, 1370)); pp.reach(0, 0.3, "l", (830, 1360))
        cr = B.crinkle(CR_GAME, turn=-0.5, eyes="open", mouth="smile"); cr.reach(0, 0.3, "l", (1560, 1420))
        cast = [sn, pp, cr]
        mess_start(up, down)
        up += [lambda d: truck2(d, 1060, UP)]
        if T_ == 9.6:
            under += [lambda d: B.cushion(d, BOX1 + 110, 1300)]
        over += [lambda d: lid(d), lambda d: box_front(d, T_ == 8.3)]
        if T_ == 8.3:
            over += [lambda d: block50(d, BLOCK_X, RED, name="red block"), lambda d: B.ball(d, BLOCK_X - 92)]
            info["ball_x"] = BLOCK_X - 92
            win = (C2X0, 1080, C2X0 + 960, 1620)
        else:
            over += [lambda d: block50(d, BLOCK_X, RED, name="red block"), lambda d: B.ball(d, BALL_X)]
            if T_ == 10.2:
                over += [lambda d: B.cushion(d, BALL_X)]
                win = (C2X0, 1080, C2X0 + 960, 1620)
            info["ball_x"] = BALL_X
        info["cushion_w"] = 240
        info["snip_behind"] = True
        if T_ == 9.6:
            req = ["sn", chest, ball_box, (BOX1 - 10, 1260, BOX1 + 230, 1340)]
    elif T_ == 17.5:
        pp = B.pip(820, turn=-0.2, eyes="open", brows="worry", mouth="flat")
        pp.reach(0, 0.3, "r", (780, 1390)); pp.reach(0, 0.3, "l", (870, 1390))
        cr = B.crinkle(1060, turn=-0.6, eyes="open", brows="worry", mouth="smile", head_dy=50, lean=-8)
        cr.reach(0, 0.3, "l", (880, 1160))
        cast = [pp, cr]
        under += [lambda d: B.cushion(d, BALL_X)]
        down += [lambda d: train2(d, 470, DOWN), lambda d: bucket2(d, 960, DOWN), lambda d: heap2(d, 1180, DOWN)]
        over += [lambda d: B.qmark(d, 830, 1080)]
        req = ["pp", "cr", (790, 1005, 870, 1120), cushion_box]
    elif T_ == 24.0:
        cr = B.crinkle(1060, turn=-0.4, eyes="wide", brows="up", mouth="smile_open")
        cr.hop(0.8, 1.2, 1, 30); cr.arms_front.append((0, 9))
        cr.reach(0, 0.3, "l", (1025, 1110)); cr.reach(0, 0.3, "r", (1095, 1110))
        pp = B.pip(850, turn=0.6, eyes="happy", mouth="smile_open"); pp.tuft(0, 0.3, "up")
        cast = [pp, cr]
        under += [lambda d: B.cushion(d, BALL_X)]
        down += [lambda d: bucket2(d, 960, DOWN), lambda d: heap2(d, 1180, DOWN)]
        req = ["pp", "cr"]
    elif T_ == 31.0:
        sn = B.snip(900, turn=0.5, eyes="open", brows="sad", mouth="flat"); sn.emote(0, 0.3, "sad")
        sn.ears(0, 0.3, "droop"); sn.reach(0, 0.3, "l", (735, 1262)); sn.reach(0, 0.3, "r", (865, 1262))
        pp = B.pip(1150, turn=-0.5, eyes="open", brows="worry", mouth="flat")
        cast = [sn, pp]
        under += [lambda d: B.cushion(d, BALL_X), lambda d: block50(d, BALL_X - 40, BLUE, GROUND - 150)]
        over += [lambda d: drum2(d, 800, 1330, strewn=False)]
        down += [lambda d: train2(d, 470, DOWN), lambda d: bucket2(d, 1000, DOWN), lambda d: heap2(d, 1180, DOWN)]
        info["heap"] = True
        req = ["sn", "pp", (BALL_X - 120, GROUND - 215, BALL_X + 120, GROUND)]
    elif T_ == 38.8:
        sn = B.snip(920, turn=0.4, eyes="happy", mouth="smile_open")
        cr = B.crinkle(1300, turn=-0.6, eyes="happy", mouth="smile")
        pp = B.pip(1720, turn=-0.4, eyes="happy", mouth="smile_open")
        cast = [sn, cr, pp]
        up += [lambda d: B.baskets_on_shelf(d), lambda d: boat2(d, 1010, UP)]
        under += [lambda d: B.cushion(d, BALL_X), lambda d: drum2(d, BALL_X, GROUND - 158, strewn=False)]
        over += [lambda d: lid(d), lambda d: box_front(d), lambda d: train2(d, 1362),
                 lambda d: d.line([S((1330, 1350)), S((1362, 1440))], fill=INK, width=_w(4))]
        down += [lambda d: teddy_lying(d, 640, DOWN), lambda d: truck2(d, 1080, DOWN), lambda d: bucket2(d, 1240, DOWN)]
        info["heap"] = True
        win = window((960, 1100), 1.0)
    elif T_ == 51.2:
        cr = B.crinkle(1360, turn=0.5, eyes="happy", mouth="smile", lean=8)
        cr.reach(0, 0.3, "r", (1530, 1330)); cr.reach(0, 0.3, "l", (1450, 1335))
        pp = B.pip(1090, turn=0.5, eyes="happy", mouth="smile_open")
        cast = [pp, cr]
        under += [lambda d: B.cushion(d, BALL_X), lambda d: drum2(d, BALL_X, GROUND - 158, strewn=False)]
        over += [lambda d: baskets_floor(d, {"red": (train_stack,)}),
                 lambda d: rect(d, 1440, 1300, 1540, 1368, RED, INK, 3, 6)]
        info["key"] = [(1425, 1300, 1575, GROUND)]
        req = ["pp", "cr", (1425, 1300, 1575, GROUND)]
    elif T_ == 63.0:
        sn = B.snip(1120, turn=-0.4, eyes="happy", mouth="smile_open")
        cr = B.crinkle(720, turn=0.5, eyes="happy", mouth="smile_open")
        pp = B.pip(1360, turn=0.6, eyes="happy", mouth="smile")
        cast = [cr, sn, pp]
        under += [lambda d: B.cushion(d, BALL_X), lambda d: drum2(d, BALL_X, GROUND - 158, strewn=False)]
        over += [lambda d: baskets_floor(d, {"red": (train_stack,), "blue": (inb(boat2),)}), lambda d: B.teddy(d, 1360),
                 lambda d: lid(d), lambda d: box_front(d)]
        down += [lambda d: bucket2(d, 820, DOWN), lambda d: truck2(d, 980, DOWN), lambda d: heap2(d, 1080, DOWN)]
        info["teddy"] = True; info["heap"] = True
        win = window((960, 1100), 1.0)
    elif T_ == 97.8:
        sn = B.snip(860, turn=-0.5, eyes="happy", mouth="smile_open")
        sn.reach(0, 0.3, "r", (775, 1268)); sn.reach(0, 0.3, "l", (700, 1262))
        pp = B.pip(1120, turn=-0.5, eyes="happy", mouth="smile_open", arm_l=150, arm_r=150)
        cast = [sn, pp]
        over += [lambda d: B.ball(d, BALL_X), lambda d: B.cushion(d, 700, 1275, w=220)]
        info["key"] = [ball_box, (590, 1235, 810, 1315)]
        req = ["sn", "pp", ball_box, (590, 1235, 810, 1315)]
    elif T_ == 119.0:
        pp = B.pip(1700, turn=0.6, eyes="happy", mouth="smile_open")
        pp.reach(0, 0.3, "r", (1790, 1340)); pp.reach(0, 0.3, "l", (1760, 1350))
        cast = [pp]
        over += [lambda d: baskets_floor(d, {"red": (train_stack, inb(drum2)), "blue": (inb(boat2), inb(bucket2)),
                                             "yellow": (inb(duck2),)}), lambda d: B.ball(d, 1815, 1360)]
        info["key"] = [(1815 - BALL_R, 1305, 1820 + BASKET_W / 2, GROUND)]
        win = window((1700, 1320), 1.8)
    else:
        raise SystemExit(f"no storyboard frame at {T_}")

    for fn in up + under:
        fn(d)
    layers = [layer(p, B.T_DRAW) for p in cast]
    for L in layers:
        bg.alpha_composite(L)
    d = ImageDraw.Draw(bg)
    for fn in over + down:
        fn(d)
    heads = {}
    for p in cast:
        nm = "pp" if isinstance(p, RP.PipPerf) else ("sn" if p.a.kind == "snip" else "cr")
        heads[nm] = (p, bbox(head_mask(p)))
    if win is None:
        boxes = [heads[r][1] if isinstance(r, str) else r for r in req]
        win = fit(boxes, ZOOM[T_])
    info.update(cast=cast, layers=layers, heads=heads, toys=list(CUR))
    return bg, win, info


def inout(win, b):
    m = margin(win, b)
    if m >= 0:
        return "in", round(m)
    sep = max(win[0] - b[2], b[0] - win[2], win[1] - b[3], b[1] - win[3])
    return ("out", round(sep)) if sep >= 0 else ("CUT", round(m))


def sheet():
    os.makedirs(os.path.join(OUT, "ep12"), exist_ok=True)
    tw, th, g = 780, 439, 12
    sh = Image.new("RGB", (3 * tw + 4 * g, 4 * th + 5 * g), (250, 250, 250))
    for i, T_ in enumerate(FRAMES):
        img, win, _ = frame(T_)
        full = shoot(img, win)
        full.save(os.path.join(OUT, "ep12", f"f_{T_:05.1f}.png"))
        sh.paste(full.resize((tw, th), Image.LANCZOS), (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sh.save(os.path.join(OUT, "storyboard.png"))
    print("sheet", os.path.join(OUT, "storyboard.png"), sh.size)


# ---------------------------------------------------------------- shot table (plan r1 zooms)
def _boxes():
    mid = (B.SHELF_TOP + FLOOR) / 2
    bf = {k: (x - BASKET_W / 2, GROUND - BASKET_H, x + BASKET_W / 2, GROUND) for k, x in BASKET_FLOOR.items()}
    return dict(box=(BOX0, LID_TOP, BOX1, GROUND), ball=(BALL_X - BALL_R, GROUND - 110, BALL_X + BALL_R, GROUND),
                heap=(BALL_X - 120, GROUND - 280, BALL_X + 120, GROUND), fall=(BOX1 - 10, 1260, BOX1 + 230, 1340),
                shelf=(SHELF[0], B.SHELF_TOP - BASKET_H, SHELF[1], FLOOR),
                cubby=(SHELF[0] + 20, mid + 14, SHELF[0] + 250, FLOOR - 20), rug=(RUG[0], 1418, RUG[1], 1626),
                red=bf["red"], blue=bf["blue"], yellow=bf["yellow"], hook=(1320, 1340, 1380, 1470),
                c21=(1760, 1305, 1895, GROUND))


SHOT_ROWS = [
    (1, 1.0, dict(sn=620, pip=900, cr=1680), "sn pip cr", "box shelf"),
    (3, 1.4, dict(snb=SNIP_BOX_X, pip=900), "snb pip", "box ball fall"),
    (5, 1.4, dict(pip=820, cr=1060), "pip cr", ""),
    (6, 1.4, dict(pip=850, cr=1060), "pip cr", ""),
    (7, 1.4, dict(sn=900, pip=1150), "sn pip", "heap"),
    (8, 1.0, dict(sn=880, pip=1150, cr=1450), "sn pip cr", "heap"),
    (10, 1.0, dict(sn=920, cr=1300, pip=1720), "sn pip cr", "hook"),
    (11, 1.3, dict(pip=1090, cr=1360), "pip cr", "shelf"),
    (13, 1.0, dict(cr=720, sn=1120, pip=1360), "sn pip cr", "red blue yellow"),
    (14, 1.4, dict(sn=1600, pip=1780), "sn pip", "blue"),
    (15, 1.0, dict(pip=700, sn=1000, cr=1300), "sn pip cr", "red blue yellow"),
    (16, 1.4, dict(cr=1480, sn=1720), "cr sn", "blue"),
    (17, 1.4, dict(sn=860, pip=1120), "sn pip", "heap"),
    (19, 1.45, dict(pip=1200, sn=1380), "sn pip", "cubby"),
    (20, 1.28, dict(pip=700, cr=1000, sn=1250), "sn pip cr", "rug red blue yellow"),
    (21, 1.8, dict(pip=1700), "pip", "c21 yellow"),
    (22, 1.0, dict(sn=1100, cr=1400, pip=1700), "sn pip cr", "red blue yellow"),
    (23, 1.4, dict(cr=1600, pip=1760), "cr pip", "yellow"),
    (24, 1.0, dict(sn=760, pip=960, cr=1160), "sn pip cr", "rug"),
]
MAKE = dict(B.MAKE, snb=snip_behind)


def shot_table():
    Bx = _boxes()
    rows = []
    for n, z, who, heads, objs in SHOT_ROWS:
        hb = {k: bbox(head_mask(MAKE[k](x))) for k, x in who.items()}
        need = [hb[k] for k in heads.split()] + [Bx[o] for o in objs.split()]
        win = fit(need, z)
        rows.append((n, z, min(round(margin(win, hb[k])) for k in heads.split()),
                     {o: round(margin(win, Bx[o])) for o in objs.split()}))
    return rows


# ---------------------------------------------------------------- measure
def pct(b, win):
    return round(100 * (b[2] - b[0]) / (win[2] - win[0]), 1), round(100 * (b[3] - b[1]) / (win[3] - win[1]), 1)


def covered(toys):
    iv = sorted((max(b[0], RUG[0]), min(b[2], RUG[1])) for _, b, s in toys if s and b[2] > RUG[0] and b[0] < RUG[1])
    tot, cur = 0, None
    for a, c in iv:
        if cur is None or a > cur[1]:
            if cur:
                tot += cur[1] - cur[0]
            cur = [a, c]
        else:
            cur[1] = max(cur[1], c)
    if cur:
        tot += cur[1] - cur[0]
    return round(100 * tot / (RUG[1] - RUG[0]))


def measure():
    pr = print
    pr(f"layout: chest x {BOX0}-{BOX1} ({BOX1 - BOX0} wide), lid {LID_TOP}-{BOX_TOP} ({BOX_TOP - LID_TOP} tall), "
       f"Snip behind at x {SNIP_BOX_X}, his head mask x1 {SNIP_HEAD_X1:.0f}, close-up x0 {C2X0:.0f}")
    occ = occluder()
    snip_d = []
    for T_ in FRAMES:
        img, win, info = frame(T_)
        line = [f"t={T_} z={1920 / (win[2] - win[0]):.2f} win x {win[0]:.0f}-{win[2]:.0f} y {win[1]:.0f}-{win[3]:.0f}"]
        line.append("heads " + " ".join(f"{k}:{'/'.join(map(str, inout(win, b)))}" for k, (p, b) in info["heads"].items()))
        if T_ == 8.3:
            line.append(f"ball {100 * 2 * BALL_R / (win[2] - win[0]):.1f}%")
        if T_ in (9.6, 10.2):
            line.append(f"cushion {100 * 240 / (win[2] - win[0]):.1f}%")
            p, _ = info["heads"]["sn"]
            be, eb = below_ears(head_mask(p))
            line.append(f"Snip face/head px past lid {int((be & ~occ).sum())}; ear px above lid "
                        f"{int((head_mask(p) & ~be & ~occ).sum())}")
        if "key" in info:
            ks = info["key"]
            line.append(f"key {100 * (max(b[2] for b in ks) - min(b[0] for b in ks)) / (win[2] - win[0]):.1f}%w")
        for p, L in zip(info["cast"], info["layers"]):
            if not isinstance(p, RP.PipPerf) and p.a.kind == "snip" and 7 < T_ < 97:
                dd = B._dist_to_ball(L, BALL_X)
                snip_d.append((T_, round(dd)))
                line.append(f"Snip to ball {dd:.0f}u")
            nm = "pip" if isinstance(p, RP.PipPerf) else p.a.kind
            w_, h_ = pct(bbox(alpha(L, 160)), win)
            line.append(f"{nm} {w_}w/{h_}h")
        if "teddy" in info:
            pl = [L for p, L in zip(info["cast"], info["layers"]) if isinstance(p, RP.PipPerf)][0]
            line.append(f"Pip feet below teddy {bbox(alpha(pl, 160))[3] - (FLOOR - 26):.0f}u, teddy "
                        f"{B.TEDDY_H:.0f} tall = {100 * B.TEDDY_H / (win[3] - win[1]):.1f}%h")
        if T_ in (0.5, 38.8, 63.0):
            line.append("toys " + " ".join(f"{n}:{max(pct(b, win))}" for n, b, s in info["toys"] if n not in ("block", "cup", "duck")))
            line.append(f"rug strewn {covered(info['toys'])}%")
        pr(" | ".join(line))
    pr("Snip paws/body to ball (u):", snip_d, "min", min(d for _, d in snip_d))
    _, w4, i4 = B.frame(4.0)
    sl = [L for p, L in zip(i4["cast"], i4["layers"]) if not isinstance(p, RP.PipPerf) and p.a.kind == "snip"][0]
    pr("gag 1 (4.0, W, sb1 staging) Snip", pct(bbox(alpha(sl, 160)), w4))
    pm = alpha(layer(B.pip(960), B.T_DRAW), 160)
    pb = bbox(pm)
    pr(f"gag 7/8 Pip in a 2.0x close-up: {100 * (pb[2] - pb[0]) / 960:.1f}w/{100 * (pb[3] - pb[1]) / 540:.1f}h")
    pr(f"gag 5 bucket 96u in C 2.2x: {100 * 96 * 2.2 / 1920:.1f}%; rim margin {(BASKET_W - 96) / 2:.0f}u")
    pr(f"gag 6 tower 3 x 50u above the rim in M 1.4x: {100 * 150 / (1080 / 1.4):.1f}%h")
    fp = math.sqrt(BALL_R ** 2 - (BALL_R - TOE_H) ** 2)
    pr(f"ball past Pip's toes (gag 7, Pip {GROUND - PIP_G7_Y}u upstage of the lane): clearance {GROUND - PIP_G7_Y - fp:.0f}u; "
       f"ball game pass {GROUND - PIP_GAME_Y - fp:.0f}u")
    pr("ball px under cushion:", int((B.ball_mask(BALL_X) & ~B.cushion_mask(BALL_X)).sum()))
    pr("--- shot table r1 (min head margin, object margins)")
    for n, z, mh, mo in shot_table():
        pr(f"shot {n} z{z}: heads {mh} objs {mo}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--still" in a:
        T_ = float(a[a.index("--still") + 1])
        img, win, _ = frame(T_)
        os.makedirs(os.path.join(OUT, "ep12"), exist_ok=True)
        shoot(img, win).save(os.path.join(OUT, "ep12", f"f_{T_:05.1f}.png"))
    if "--sheet" in a:
        sheet()
    if "--measure" in a:
        measure()
