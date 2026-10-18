"""Episode 12 rough set, plan r2: re-measure the r2 estimate rows + gate-1b storyboard sb3 (not the episode).

    python3 episodes/ep12_rough_r2.py --measure    numbers for the plan's r2 Measured rows
    python3 episodes/ep12_rough_r2.py --sheet      build/sb3/storyboard.png (12 frames, no captions) + build/sb3/ep12/f_T.png
    python3 episodes/ep12_rough_r2.py --still T    one frame -> build/sb3/ep12/f_T.png

Reuses ep12_rough.py (set, cast, helpers) and ep12_rough_r1.py (r1 toy shapes). r2 staging (plan section 4):
no chest or lid; drum far left (x 180); Snip 300 (truck leaves his paw) -> 400 (gag 1, sit-down on bare floor)
-> 500 at 9.6 (cushion at chest, eyes on the drum, lets go); ball rests at 640 under the cushion; Pip 760 in the
ball game; Crinkle 1680 at 7.2-9.2; gag 3 on the boat's tow rope (nothing near a neck or scarf).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ep12_rough as B  # noqa: E402
import ep12_rough_r1 as P1  # noqa: E402
from ep12_rough import (BALL_R, BASKET_FLOOR, BASKET_H, BASKET_W, BLUE, FLOOR, GROUND, INK, RED, RES,  # noqa: E402
                        SHELF, WHITE, YEL, alpha, bbox, ell, fit, head_mask, layer, margin, rect, shoot, window, S, _w)
from ep12_rough_r1 import (CUR, DOWN, UP, block50, boat2, bucket2, cup2, drum2, duck2, heap2, inb, pct,  # noqa: E402
                           pip_at, teddy_lying, train2, train_stack, truck2, covered, inout)

R = B.R
RP = B.RP
OUT = os.path.join(B.ROOT, "build", "sb3")
RUG = (560, 1360)
DRUM_X = 180
BALL_X = 640
BLOCK_X = 1000
PIP_X = 760
CR_GAME = 1680
SN_TRUCK, SN_GAG1, SN_REL = 300, 400, 500
CUSH_W = 240
HELD_CY = 1300                  # held cushion centre at Snip's chest (flat pillow 80 tall)
T_REL, T_FLUMP = 9.6, 10.2
LIFTS = [(45.6, 47.6), (47.7, 49.7), (49.8, 51.8)]   # each: 0.4 grip on the shelf, 1.2 down, 0.4 set
ZOOM = {0.5: 1.0, 8.3: 2.0, 9.6: 1.4, 10.0: 2.0, 17.5: 1.4, 24.0: 1.4, 31.0: 1.4, 44.0: 1.3, 51.0: 1.3,
        97.8: 1.4, 119.0: 1.8, 136.0: 1.0}
FRAMES = tuple(ZOOM)


# ---------------------------------------------------------------- masks and distances
def draw_mask(fn):
    im = Image.new("RGBA", (B.FW, B.FH), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im))
    return alpha(im, 0)


def box_mask(b):
    return draw_mask(lambda d: d.rectangle([S((b[0], b[1])), S((b[2], b[3]))], fill=(0, 0, 0, 255)))


def _edge_pts(m):
    m = m[::int(RES), ::int(RES)]
    e = m.copy()
    e[1:-1, 1:-1] &= ~(m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:])
    ys, xs = np.nonzero(e)
    return np.stack([xs, ys], 1).astype(float)


def mdist(a, b):
    """Smallest gap between two masks, design units (0 = touching or overlapping)."""
    if (a & b).any():
        return 0.0
    pa, pb = _edge_pts(a), _edge_pts(b)
    best = 1e9
    for i in range(0, len(pa), 400):
        d = np.sqrt(((pa[i:i + 400, None, :] - pb[None, :, :]) ** 2).sum(-1)).min()
        best = min(best, d)
    return float(best)


def body_mask(p):
    return alpha(layer(p, B.T_DRAW), 160)


def neck_mask(p, t=B.T_DRAW):
    """Head plus neck and scarf: the whole figure above shoulder line + 40."""
    m = body_mask(p).copy()
    st = p.state(t)
    sy = max(p.a.shoulder(st, "l")[1], p.a.shoulder(st, "r")[1])
    m[max(0, int((sy + 40 - B.LAND_Y0) * RES)):, :] = False
    hb = bbox(head_mask(p, t))
    m[:, :max(0, int((hb[0] - 10) * RES))] = False
    m[:, int((hb[2] + 10) * RES):] = False
    if name_of(p) == "cr":                             # whole scarf incl. the tail: figure pixels in the scarf's box
        L = np.asarray(layer(p, t)).astype(int)
        col = np.array(R.CRINKLE["scarf"][:3])
        sc = (np.abs(L[..., :3] - col).sum(-1) < 60) & (L[..., 3] > 160)
        sb = bbox(sc)
        box = np.zeros_like(m)
        box[int((sb[1] - B.LAND_Y0) * RES):int((sb[3] - B.LAND_Y0) * RES), int(sb[0] * RES):int(sb[2] * RES)] = True
        m = head_mask(p, t) | (body_mask(p) & box)
    return m


def name_of(p):
    return "pp" if isinstance(p, RP.PipPerf) else ("sn" if p.a.kind == "snip" else "cr")


# ---------------------------------------------------------------- cast in r2 poses
def snip_carry(x, look_drum=True):
    """Cushion at chest, body toward the ball, head and eyes back to the drum (curious, no grin)."""
    p = B.snip(x, turn=0.3, hturn=-0.75, mouth="flat")
    p.emote(0, 0.3, "curious")
    if look_drum:
        p.dart(0.5, -12, -2, blink=False)
    p.reach(0, 0.3, "r", (x + 120, HELD_CY + 10)); p.reach(0, 0.3, "l", (x + 40, HELD_CY + 22))
    return p


def cushion_cy(t):
    """Flat cushion centre: held to T_REL, then eased down to rest on the ball at T_FLUMP (plan timing)."""
    land = GROUND - 2 * BALL_R - 40 + 6
    if t <= T_REL:
        return HELD_CY
    u = min(1.0, (t - T_REL) / (T_FLUMP - T_REL))
    return HELD_CY + (land - HELD_CY) * u * u


def held_cushion(d, cy=HELD_CY):
    B.cushion(d, BALL_X, cy, w=CUSH_W)


def cushion_box(cy):
    return (BALL_X - CUSH_W / 2, cy - 40, BALL_X + CUSH_W / 2, cy + 40)


BULGE = (BALL_X - CUSH_W / 2, GROUND - 2 * BALL_R - 55, BALL_X + CUSH_W / 2, GROUND)
BALL = (BALL_X - BALL_R, GROUND - 2 * BALL_R, BALL_X + BALL_R, GROUND)


def hook(d, x, y):
    d.arc([S((x - 8, y - 8)), S((x + 8, y + 8))], 270, 180, fill=INK, width=_w(5))
    d.line([S((x - 14, y)), S((x - 8, y))], fill=INK, width=_w(5))


def rope(d, a, b, sag=18):
    pts = [(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u + sag * math.sin(math.pi * u)) for u in np.linspace(0, 1, 12)]
    d.line([S(q) for q in pts], fill=(150, 110, 70), width=_w(5))
    return pts


def qmark_at(d, cx, cy):
    B.qmark(d, cx, cy, 30)


def mess_wide(up, down, truck=True):
    up += [lambda d: drum2(d, DRUM_X, UP), lambda d: teddy_lying(d, 860, UP), lambda d: boat2(d, 1230, UP)]
    down += [lambda d: train2(d, 560, DOWN), lambda d: bucket2(d, 1050, DOWN), lambda d: heap2(d, 1130, DOWN)]


# ---------------------------------------------------------------- frames
def frame(T_):
    del CUR[:]
    bg = P1.background2()
    d = ImageDraw.Draw(bg)
    up, under, cast, over, down, req, info = [], [], [], [], [], [], {}
    win = None
    extra = []                      # (name, mask-drawing fn) for distance checks
    if T_ == 0.5:
        sn = B.snip(SN_TRUCK, turn=0.6, eyes="happy", mouth="smile_open"); sn.emote(0, 0.3, "delighted")
        sn.reach(0, 0.3, "l", (SN_TRUCK - 95, 1330)); sn.reach(0, 0.3, "r", (SN_TRUCK + 70, 1300))
        pp = pip_at(PIP_X, turn=0.5, eyes="happy", mouth="smile_open"); pp.reach(0, 0.3, "r", (PIP_X + 80, 1400))
        cr = B.crinkle(CR_GAME, turn=-0.5, eyes="happy", mouth="smile"); cr.reach(0, 0.3, "l", (CR_GAME - 120, 1420))
        cast = [sn, pp, cr]
        mess_wide(up, down)
        paw = sn.paw(B.T_DRAW, "l")[0]
        sm = body_mask(sn)
        tx, tb = paw[0] - 40, paw[1] + 24 + 110
        while mdist(box_mask((tx - 70, tb - 110, tx + 70, tb)), sm) < 14:
            tx -= 6
        info["truck"] = (tx - 70, tb - 110, tx + 70, tb)
        over += [lambda d: truck2(d, tx, tb, strewn=False), lambda d: block50(d, BLOCK_X, RED, name="red block"),
                 lambda d: B.ball(d, 1240), lambda d: B.cushion(d, 470, 1440, w=200)]
        win = window((960, 1100), 1.0)
    elif T_ == 4.4:                                    # gag 1 break: popped free, soft sit-down on bare floor
        sn = B.snip(SN_GAG1, turn=0.3, eyes="closed", mouth="smile_open", head_dy=40, sq=0.86)
        sn.ears(0, 0.3, "droop"); sn.reach(0, 0.3, "r", (SN_GAG1 + 90, 1400)); sn.reach(0, 0.3, "l", (SN_GAG1 + 50, 1410))
        pp = pip_at(PIP_X, turn=-0.4, eyes="happy", mouth="smile_open")
        cr = B.crinkle(CR_GAME, turn=-0.5, eyes="happy", mouth="smile_open")
        cast = [sn, pp, cr]
        up += [lambda d: drum2(d, DRUM_X, UP), lambda d: teddy_lying(d, 860, UP), lambda d: boat2(d, 1230, UP)]
        down += [lambda d: bucket2(d, 1050, DOWN), lambda d: heap2(d, 1130, DOWN)]
        over += [lambda d: train2(d, SN_GAG1 + 80, GROUND, strewn=False), lambda d: B.cushion(d, 470, 1440, w=200),
                 lambda d: block50(d, BLOCK_X, RED, name="red block"), lambda d: B.ball(d, 1240)]
        win = window((960, 1100), 1.0)
    elif T_ in (8.3, 9.6, 10.0):
        sx = SN_GAG1 + (SN_REL - SN_GAG1) * min(1.0, (T_ - 7.2) / (T_REL - 7.2))
        sn = snip_carry(sx, look_drum=T_ >= 9.2)
        if T_ == 10.0:
            sn.reach(0, 0.3, "r", (sx + 70, 1340)); sn.reach(0, 0.3, "l", (sx + 30, 1350))
        pp = pip_at(PIP_X, turn=0.6 if T_ == 8.3 else -0.4, eyes="normal", mouth="o",
                    brows="calm" if T_ == 8.3 else "worry")
        if T_ == 8.3:
            pp.reach(0, 0.3, "r", (PIP_X + 85, 1370)); pp.reach(0, 0.3, "l", (PIP_X - 70, 1360))
        cr = B.crinkle(CR_GAME, turn=-0.5, eyes="normal", mouth="smile"); cr.reach(0, 0.3, "l", (CR_GAME - 120, 1420))
        cast = [sn, pp, cr]
        up += [lambda d: drum2(d, DRUM_X, UP), lambda d: teddy_lying(d, 860, UP), lambda d: boat2(d, 1230, UP)]
        down += [lambda d: bucket2(d, 1050, DOWN), lambda d: heap2(d, 1130, DOWN)]
        bx = BLOCK_X - 92 if T_ == 8.3 else BALL_X
        info["ball_x"] = bx
        over += [lambda d: block50(d, BLOCK_X, RED, name="red block"), lambda d: B.ball(d, bx)]
        cy = cushion_cy(T_ if T_ != 8.3 else 0)
        info["cushion"] = cushion_box(cy)
        over += [lambda d: held_cushion(d, cy)]
        bb = (bx - BALL_R, GROUND - 2 * BALL_R, bx + BALL_R, GROUND)
        info["ball"] = bb
        if T_ == 8.3:                                  # C2: ball, block, Pip's head and wings; Snip and Crinkle out
            pb = bbox(body_mask(pp))
            need = [bbox(head_mask(pp)), (pb[0], pb[1], pb[2], pb[1] + 200), bb, (BLOCK_X - 25, GROUND - 50, BLOCK_X + 25, GROUND)]
            w0 = fit(need, 2.0)
            snx1 = max(bbox(body_mask(snip_carry(x)))[2] for x in (SN_GAG1 + 100 * (9.2 - 7.2) / 2.4, sx))
            crx0 = bbox(body_mask(cr))[0]
            x0 = min(max(w0[0], snx1 + 12), crx0 - 12 - 960)
            win = (x0, w0[1], x0 + 960, w0[3])
            info["c2_bounds"] = (snx1, crx0)
        elif T_ == 9.6:
            req = [bbox(body_mask(sn)), info["cushion"], bb]
        else:
            req = [info["cushion"], bb]
    elif T_ == 13.6:                                   # shot 4: the bulge; Snip off to the drum
        sn = B.snip(380, turn=-0.5, eyes="normal", mouth="flat"); sn.emote(0, 0.3, "neutral")
        cast = [sn]
        over += [lambda d: B.cushion(d, BALL_X, w=CUSH_W)]
        req = [BULGE]
    elif T_ == 17.5:
        sn = B.snip(260, turn=-0.6, eyes="normal", mouth="flat")
        pp = B.pip(860, turn=-0.3, eyes="normal", brows="worry", mouth="flat", look_x=-10)
        pp.reach(0, 0.3, "r", (820, 1390)); pp.reach(0, 0.3, "l", (900, 1390))
        cr = B.crinkle(1150, turn=-0.6, eyes="normal", brows="worry", mouth="smile", head_dy=10)
        cr.reach(0, 0.3, "l", (965, 1180))
        cast = [sn, pp, cr]
        under += [lambda d: B.cushion(d, BALL_X, w=CUSH_W)]
        down += [lambda d: train2(d, 560, DOWN), lambda d: bucket2(d, 1050, DOWN), lambda d: heap2(d, 1130, DOWN)]
        up += [lambda d: drum2(d, DRUM_X, UP)]
        hm = head_mask(pp)
        hb = bbox(hm)
        qx, qy = hb[0] - 40, hb[1] + 40
        while mdist(draw_mask(lambda d: qmark_at(d, qx, qy)), hm) > 14:
            qx += 4
        info["q"] = (qx, qy)
        over += [lambda d: qmark_at(d, qx, qy)]
        extra.append(("q", lambda d: qmark_at(d, qx, qy)))
        req = ["pp", "cr", (qx - 32, qy - 64, qx + 32, qy + 40), BULGE]
        w0 = fit([bbox(head_mask(p)) for p in cast[1:]] + [req[2], BULGE], 1.4)
        sb = bbox(body_mask(sn))
        sx0, sy0 = sb[0] - 12, sb[1] - 12
        win = (sx0, sy0, sx0 + w0[2] - w0[0], sy0 + w0[3] - w0[1])
    elif T_ == 24.0:
        cr = B.crinkle(1060, turn=-0.4, eyes="happy", brows="up", mouth="smile_open", head_dy=-10, tilt=-12)
        cr.hop(0.8, 1.2, 1, 30)
        cr.reach(0, 0.3, "l", (1020, 1330)); cr.reach(0, 0.3, "r", (1100, 1330))
        pp = B.pip(840, turn=0.6, eyes="happy", mouth="smile_open"); pp.tuft(0, 0.3, "up")
        cast = [pp, cr]
        under += [lambda d: B.cushion(d, BALL_X, w=CUSH_W)]
        down += [lambda d: bucket2(d, 960, DOWN), lambda d: heap2(d, 1180, DOWN)]
        req = ["pp", "cr"]
    elif T_ in (31.0, 33.0):
        if T_ == 31.0:
            sn = B.snip(860, turn=0.5, eyes="normal", brows="sad", mouth="flat"); sn.emote(0, 0.3, "sad")
            sn.ears(0, 0.3, "droop"); sn.to(0, 0.3, look_x=8, look_y=4)
            sn.reach(0, 0.3, "l", (800, 1262)); sn.reach(0, 0.3, "r", (925, 1262))
            over += [lambda d: drum2(d, 862, 1330, strewn=False)]
        else:                                          # the drum set on the cushion (measure only)
            sn = B.snip(840, turn=-0.5, eyes="normal", mouth="flat")
            sn.reach(0, 0.3, "l", (712, 1270)); sn.reach(0, 0.3, "r", (735, 1250))
            under += [lambda d: drum2(d, BALL_X, GROUND - 2 * BALL_R - 55, strewn=False)]
        pp = B.pip(1180, turn=0.5, eyes="normal", brows="worry", mouth="flat", look_x=8)
        cast = [sn, pp]
        under = [lambda d: B.cushion(d, BALL_X, w=CUSH_W), lambda d: block50(d, BALL_X - 40, BLUE, GROUND - 165)] + under
        down += [lambda d: train2(d, 470, DOWN), lambda d: bucket2(d, 1050, DOWN), lambda d: heap2(d, 1130, DOWN)]
        req = ["sn", "pp", (BALL_X - 120, GROUND - 215, BALL_X + 120, GROUND)]
    elif T_ in (36.6, 38.8, 44.0):
        cx = {36.6: 1180, 38.8: 1250, 44.0: 1330}[T_]
        cr = B.crinkle(cx, turn=0.5 if T_ < 44 else -0.3, eyes="wide" if T_ == 44.0 else "normal",
                       brows="up", mouth="smile_open" if T_ == 38.8 else "o")
        if T_ == 44.0:
            cr.emote(0, 0.3, "curious")
        # the boat in the left paw, arm down (the scarf tail hangs right; the sail stays below the head)
        cr.reach(0, 0.3, "l", (cx - 150, 1460) if T_ < 44 else (cx - 170, 1300))
        paw = cr.paw(B.T_DRAW, "l")[0]
        info["boat_paw"] = paw
        boat_base = paw[1] + (34 if T_ < 44 else 160)    # 44.0: held by the rope, the boat hangs below the paw
        stern = (paw[0] + 46, boat_base - 6)
        if T_ < 44:
            hk = (stern[0] + 14, GROUND - 58)
            tx = hk[0] + 2                              # engine front (right end) just under the rope
            under += [lambda d: train2(d, tx, GROUND, flip=True, strewn=False)]
            rp = (stern, (hk[0] + 6, hk[1] + 4))
        else:                                          # unhooked: boat on its rope (left), train in the right paw
            cr.reach(0, 0.3, "r", (cx + 170, 1320))
            pq = cr.paw(B.T_DRAW, "r")[0]
            hk = (pq[0] - 26, pq[1] + 12)
            over += [lambda d: train2(d, pq[0] - 20, pq[1] + 52, strewn=False)]
            rp = ((paw[0], paw[1]), (paw[0] - 50, boat_base - 40))
        over += [lambda d: boat2(d, paw[0], boat_base, strewn=False), lambda d: hook(d, *hk),
                 lambda d: rope(d, *rp, sag=10 if T_ < 44 else 0)]
        extra.append(("rope+hook", lambda d: (rope(d, *rp), hook(d, *hk))))
        extra.append(("boat", lambda d: boat2(d, paw[0], boat_base, strewn=False)))
        if T_ == 44.0:
            extra.append(("train", lambda d: train2(d, pq[0] - 20, pq[1] + 52, strewn=False)))
        info["c4"] = [(hk[0] - 16, hk[1] - 10, hk[0] + 10, hk[1] + 10), (min(rp[0][0], rp[1][0]), rp[0][1],
                      max(rp[0][0], rp[1][0]), rp[1][1] + 12), (paw[0] - 28, paw[1] - 28, paw[0] + 28, paw[1] + 28)]
        cast = [cr]
        if T_ >= 38.8:
            sn = B.snip(900 if T_ == 38.8 else 960, turn=0.4, eyes="happy", mouth="smile_open")
            pp = B.pip(1720 if T_ == 38.8 else 740, turn=-0.4 if T_ == 38.8 else 0.4, eyes="happy", mouth="smile_open")
            cast = [sn, cr, pp]
            up += [lambda d: B.baskets_on_shelf(d)]
        under += [lambda d: B.cushion(d, BALL_X, w=CUSH_W), lambda d: drum2(d, BALL_X, GROUND - 165, strewn=False)]
        down += [lambda d: teddy_lying(d, 640, DOWN), lambda d: bucket2(d, 960, DOWN)]
        if T_ == 36.6:
            win = fit(info["c4"], 2.0)
        elif T_ == 38.8:
            win = window((960, 1100), 1.0)
        else:
            req = ["cr", "sn", "pp", (SHELF[0], B.SHELF_TOP - BASKET_H, SHELF[1], FLOOR)]
    elif T_ == 51.0:
        cr = B.crinkle(1700, turn=0.3, eyes="happy", mouth="smile")
        u = (T_ - (LIFTS[2][0] + 0.4)) / 1.2
        by = (B.SHELF_TOP) + (GROUND - B.SHELF_TOP) * u
        info["lift_y"] = by
        cr.reach(0, 0.3, "r", (1850, by - 30)); cr.reach(0, 0.3, "l", (1790, by - 34))
        sn = B.snip(1360, turn=0.5, eyes="happy", mouth="smile_open")
        sn.reach(0, 0.3, "r", (1470, 1360)); sn.reach(0, 0.3, "l", (1440, 1372))
        pp = B.pip(1110, turn=0.5, eyes="happy", mouth="smile_open")
        cast = [pp, sn, cr]
        under += [lambda d: B.cushion(d, BALL_X, w=CUSH_W), lambda d: drum2(d, BALL_X, GROUND - 165, strewn=False)]
        over += [lambda d: P1.basket2(d, BASKET_FLOOR["red"], RED, items=(train_stack,)),
                 lambda d: P1.basket2(d, BASKET_FLOOR["blue"], BLUE),
                 lambda d: P1.basket2(d, BASKET_FLOOR["yellow"], YEL, base=by)]
        info["key"] = [(1425, 1300, 1575, GROUND)]
        req = ["pp", "sn", "cr", (SHELF[0], B.SHELF_TOP - BASKET_H, SHELF[1], FLOOR)]
    elif T_ == 63.0:
        sn = B.snip(760, turn=0.4, eyes="happy", mouth="smile_open")
        cr = B.crinkle(560, turn=0.5, eyes="happy", mouth="smile_open")
        px = info["pip_x"] = 1330
        pp = B.pip(px, turn=0.6, eyes="happy", mouth="smile")
        cast = [cr, sn, pp]
        under += [lambda d: B.cushion(d, BALL_X, w=CUSH_W), lambda d: drum2(d, BALL_X, GROUND - 165, strewn=False)]
        over += [lambda d: P1.baskets_floor(d, {"red": (train_stack,), "blue": (inb(boat2),)}), lambda d: B.teddy(d, px)]
        down += [lambda d: bucket2(d, 700, DOWN), lambda d: truck2(d, 860, DOWN), lambda d: heap2(d, 960, DOWN)]
        win = window((960, 1100), 1.0)
    elif T_ == 97.8:
        sn = B.snip(860, turn=-0.5, eyes="happy", mouth="smile_open")
        sn.reach(0, 0.3, "r", (775, 1268)); sn.reach(0, 0.3, "l", (700, 1262))
        pp = B.pip(1120, turn=-0.5, eyes="happy", mouth="smile_open", arm_l=150, arm_r=150)
        cast = [sn, pp]
        over += [lambda d: B.ball(d, BALL_X), lambda d: B.cushion(d, 705, 1275, w=220)]
        info["key"] = [BALL, (595, 1235, 815, 1315)]
        req = ["sn", "pp", BALL, (595, 1235, 815, 1315)]
    elif T_ == 119.0:
        pp = B.pip(1700, turn=0.6, eyes="happy", mouth="smile_open")
        pp.reach(0, 0.3, "r", (1790, 1340)); pp.reach(0, 0.3, "l", (1760, 1350))
        cast = [pp]
        over += [lambda d: P1.baskets_floor(d, {"red": (train_stack, inb(drum2)), "blue": (inb(boat2), inb(bucket2)),
                                                "yellow": (inb(duck2),)}), lambda d: B.ball(d, 1815, 1360)]
        info["key"] = [(1815 - BALL_R, 1305, 1820 + BASKET_W / 2, GROUND)]
        win = window((1700, 1320), 1.8)
    elif T_ == 136.0:
        sn = B.snip(830, turn=0.5, eyes="happy", mouth="smile_open"); sn.emote(0, 0.3, "delighted")
        sn.reach(0, 0.3, "r", (930, 1250))
        pp = B.pip(1010, turn=-0.3, eyes="happy", mouth="smile_open", arm_l=150, arm_r=150)
        cr = B.crinkle(1170, turn=-0.5, eyes="happy", mouth="smile_open"); cr.emote(0, 0.3, "delighted")
        cr.reach(0, 0.3, "l", (1050, 1240))
        cast = [sn, pp, cr]
        over += [lambda d: P1.baskets_floor(d, {"red": (train_stack, inb(drum2)), "blue": (inb(boat2), inb(bucket2)),
                                                "yellow": (inb(duck2), lambda d, x, b: B.ball(d, x, b - 30))}),
                 lambda d: B.cushion(d, SHELF[0] + 135, 1400, w=180)]
        win = window((960, 1100), 1.0)
    else:
        raise SystemExit(f"no frame at {T_}")

    for fn in up + under:
        fn(d)
    layers = [layer(p, B.T_DRAW) for p in cast]
    for L in layers:
        bg.alpha_composite(L)
    d = ImageDraw.Draw(bg)
    for fn in over + down:
        fn(d)
    heads = {name_of(p): (p, bbox(head_mask(p))) for p in cast}
    if win is None:
        boxes = [heads[r][1] if isinstance(r, str) else r for r in req]
        win = fit(boxes, ZOOM.get(T_, 2.0))
    info.update(cast=cast, layers=layers, heads=heads, toys=list(CUR), extra=extra)
    return bg, win, info


# ---------------------------------------------------------------- sheet
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


# ---------------------------------------------------------------- measure
def whole(win, p):
    return inout(win, bbox(body_mask(p)))


def measure():
    pr = print
    res = {}
    # 1-2: C2 window and Pip's eyes
    img, win, info = frame(8.3)
    hs = {k: inout(win, b) for k, (p, b) in info["heads"].items()}
    pr(f"[C2 8.3] win x {win[0]:.0f}-{win[2]:.0f} y {win[1]:.0f}-{win[3]:.0f}; heads {hs}; Snip whole "
       f"{whole(win, info['heads']['sn'][0])}; bounds Snip x1 max(7.2-9.2) {info['c2_bounds'][0]:.0f}, Crinkle x0 "
       f"{info['c2_bounds'][1]:.0f}; ball {100 * 2 * BALL_R / 960:.1f}%; Pip wings margin "
       f"{margin(win, bbox(body_mask(info['heads']['pp'][0]))):.0f} (body, feet may be cut)")
    pp = info["heads"]["pp"][0]
    st = pp.state(B.T_DRAW)
    pr(f"[Pip eyes 8.3] eyes={st['eyes']!r}; rig2_pip eye ry 17 x scale 0.9 -> open eye {2 * 17 * 0.9:.1f}u tall; "
       f"Pip rig has no upper lid")
    # 3-4: truck at 0.5
    img, win, info = frame(0.5)
    sn = info["heads"]["sn"][0]
    pm = body_mask(sn)
    tb = info["truck"]
    pr(f"[0.5] truck box {tuple(round(v) for v in tb)}; gap to Snip's whole mask {mdist(box_mask(tb), pm):.1f}u; "
       f"size {max(pct(tb, win))}% (w {pct(tb, win)[0]}, h {pct(tb, win)[1]}); Snip whole {whole(win, sn)}; "
       f"heads {[(k, inout(win, b)) for k, (p, b) in info['heads'].items()]}; rug strewn {covered(info['toys'])}%")
    # 5: Snip whole 0-14.4 per shot
    rows = [(0.5, "shot 1 W")]
    for T_, nm in ((0.5, "1 W"), (4.4, "1 W gag1"), (8.3, "2 C2"), (9.6, "3 M1"), (10.0, "3 C inset"), (13.6, "4 C")):
        img, win, info = frame(T_)
        s = info["heads"]["sn"][0]
        pr(f"[Snip whole {T_} shot {nm}] win x {win[0]:.0f}-{win[2]:.0f} y {win[1]:.0f}-{win[3]:.0f} z "
           f"{1920 / (win[2] - win[0]):.2f}: Snip {whole(win, s)}; heads "
           f"{[(k, inout(win, b)) for k, (p, b) in info['heads'].items()]}")
        if T_ == 13.6:
            for x in (500, 440):
                pr(f"   shot 4 with Snip at {x}: {inout(win, bbox(body_mask(B.snip(x, turn=-0.5))))}")
        if T_ == 4.4:
            sm = body_mask(s)
            ds = sorted((round(mdist(box_mask(b), sm)), n) for n, b, st in info["toys"])
            pr(f"   F3 toys to Snip's whole mask at the sit-down: {ds[:4]}; Snip size in W {pct(bbox(sm), win)}")
        if T_ == 9.6:
            pr(f"   cushion {100 * CUSH_W / (win[2] - win[0]):.1f}% of width")
            st = s.state(B.T_DRAW)
            ht = max(-1, min(1, st["turn"] + st.get("hturn", 0)))
            offs = []
            for side in (-1, 1):
                _, cs = R._proj(180, 140, side * 19.6, ht)
                w = 0.4 + 0.6 * cs
                offs.append(round(st["look_x"] * w * 1.15, 1))
            pr(f"   Snip pupils: look_x {st['look_x']:.1f}, head turn {ht:.2f}, offset per eye (u, - = left) {offs}")
        if T_ == 10.0:
            pr(f"   cushion {100 * CUSH_W / (win[2] - win[0]):.1f}% of width")
    # Snip's pupils across 9.2-11.0
    for t in (9.2, 9.6, 10.4, 11.0):
        s = snip_carry(SN_REL)
        st = s.state(B.T_DRAW)
        pr(f"   pupil look_x at shot time {t}: {st['look_x']:.1f} (held from the dart; rough holds one pose)")
        break
    # 9-10: ball visible under the falling cushion
    bm = B.ball_mask(BALL_X)
    vis = []
    for k in range(0, 31):
        t = 9.0 + k / 24 * 1.0 if k < 25 else 9.0 + k / 24
        cy = cushion_cy(t)
        cm = box_mask(cushion_box(cy))
        vis.append((round(t, 3), round(100 * (bm & ~cm).sum() / bm.sum())))
    pr("[ball visible % under the cushion, 9.0-10.25]", [v for v in vis if v[0] in (9.0, 9.6) or v[0] >= 9.9])
    drop = (GROUND - 2 * BALL_R) - (HELD_CY + 40)
    hs = bbox(body_mask(B.snip(SN_REL)))
    m_per_u = 0.9 / (FLOOR - hs[1])
    pr(f"[fall] cushion bottom to ball top at release {drop}u; Snip mask height {FLOOR - hs[1]:.0f}u; "
       f"real fall time if Snip is 0.9 m tall: {math.sqrt(2 * drop * m_per_u / 9.81):.2f}s")
    # 11: Snip to ball 7-97
    for T_ in (8.3, 9.6, 10.0, 13.6, 31.0, 33.0):
        img, win, info = frame(T_)
        s = info["heads"]["sn"][0]
        bx = info.get("ball_x", BALL_X)
        if T_ == 8.3:
            bx = BALL_X                                 # resting spot; ball still rolling at 8.3
        pr(f"[Snip to ball {T_}] {B._dist_to_ball(layer(s, B.T_DRAW), BALL_X):.0f}u (ball at rest x {BALL_X})")
    # 12-14: "?" and bulge at 17.5
    img, win, info = frame(17.5)
    qm = draw_mask(info["extra"][0][1])
    for k, (p, b) in info["heads"].items():
        pr(f"[17.5] '?' to {k} head mask {mdist(qm, head_mask(p)):.1f}u; head {inout(win, b)}")
    pr(f"[17.5] win x {win[0]:.0f}-{win[2]:.0f} z {1920 / (win[2] - win[0]):.2f}; bulge {pct(BULGE, win)} margin "
       f"{margin(win, BULGE):.0f}; Snip whole {whole(win, info['heads']['sn'][0])}")
    # 15: basket lifts
    img, win, info = frame(51.0)
    sh = (SHELF[0], B.SHELF_TOP - BASKET_H, SHELF[1], FLOOR)
    pr(f"[51.0] win x {win[0]:.0f}-{win[2]:.0f} y {win[1]:.0f}-{win[3]:.0f}; shelf margin {margin(win, sh):.0f}; "
       f"heads {[(k, inout(win, b)) for k, (p, b) in info['heads'].items()]}; yellow basket at y {info['lift_y']:.0f}; "
       f"each lift down {LIFTS[0][1] - LIFTS[0][0] - 0.8:.1f}s between shelf top {B.SHELF_TOP} and floor; "
       f"key {pct(info['key'][0], win)}; cr head box {tuple(round(v) for v in info['heads']['cr'][1])}")
    # 16, 17, 18: C4, F1, head masks per row
    for T_ in (36.6, 38.8, 44.0):
        img, win, info = frame(T_)
        line = [f"[{T_}] win x {win[0]:.0f}-{win[2]:.0f} y {win[1]:.0f}-{win[3]:.0f} z {1920 / (win[2] - win[0]):.2f}"]
        line.append("heads " + str([(k, inout(win, b)) for k, (p, b) in info["heads"].items()]))
        for nm, fn in info["extra"]:
            m = draw_mask(fn)
            line.append(f"{nm} to neck/scarf masks " + str({name_of(p): round(mdist(m, neck_mask(p)), 1) for p in info["cast"]}))
        line.append(f"boat paw {tuple(round(v) for v in info['boat_paw'])}, head bottoms "
                    f"{ {k: round(b[3]) for k, (p, b) in info['heads'].items()} }")
        if T_ == 36.6:
            u = info["c4"]
            line.append(f"hook+rope {pct((min(b[0] for b in u[:2]), min(b[1] for b in u[:2]), max(b[2] for b in u[:2]), max(b[3] for b in u[:2])), win)}")
            cr = info["heads"]["cr"]
            ux = info["c4"] + [cr[1]]
            x0 = min(b[0] for b in ux); y0 = min(b[1] for b in ux); x1 = max(b[2] for b in ux); y1 = max(b[3] for b in ux)
            line.append(f"zoom with Crinkle's head wholly in (10u): {min(1920 / (x1 - x0 + 20), 1080 / (y1 - y0 + 20)):.2f}")
        if T_ == 38.8:
            line.append(f"train in W {100 * 440 / (win[2] - win[0]):.1f}%w")
        pr(" | ".join(line))
    # 19: rows' head margins (frames that exist)
    for T_ in (0.5, 9.6, 10.0, 13.6, 17.5, 24.0, 31.0, 44.0, 51.0, 97.8, 119.0, 136.0):
        img, win, info = frame(T_)
        hb = [b for p, b in info["heads"].values()]
        pr(f"[heads {T_}] z {1920 / (win[2] - win[0]):.2f} head union y {min(b[1] for b in hb):.0f}-{max(b[3] for b in hb):.0f} " + " ".join(
            f"{k}:{'/'.join(map(str, inout(win, b)))}" for k, (p, b) in info["heads"].items()))
    # 20: F4 Pip's teddy path 62-66.4
    img, win, info = frame(63.0)
    toys = [(n, b) for n, b, s in info["toys"] if s]
    for px in (1330, 1380, 1430):
        pm = body_mask(B.pip(px, turn=0.6)) | box_mask((px - 64, 1100, px + 64, FLOOR - 26))
        ds = sorted((round(mdist(box_mask(b), pm)), n) for n, b in toys)
        pr(f"[F4 Pip+teddy at {px}] nearest toys {ds[:2]}")
    pr(f"[63.0] rug strewn {covered(info['toys'])}% (toys left of the path)")


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
