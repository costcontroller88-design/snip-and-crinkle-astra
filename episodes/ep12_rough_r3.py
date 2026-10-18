"""Episode 12 rough set, plan r3: re-measure the (r3) rows (not the episode).

    python3 episodes/ep12_rough_r3.py --measure    numbers for the plan's (r3) Measured rows
    python3 episodes/ep12_rough_r3.py --still T    one frame -> build/sb3/ep12/f_T.png
    python3 episodes/ep12_rough_r3.py --sheet      build/sb3/storyboard.png (12 frames, no captions) + f_T.png

Builds on ep12_rough_r2.py; r3 staging (reviews/ep12_fixes_r3.md): Snip stays at 380 with the cushion upright at his
tummy, paws open 10.1, it drops to his toes and topples forward onto the ball (rigid-slab physics below); he walks to
the drum (240 by 12.8); Crinkle at 1850 to 12.8, 1600 by 14.4; boat at Crinkle's tummy.
Lead picks (reviews/ep12_measure_r3.md): tip 25 deg; soft drape flat over the ball after contact; rope ~330 u;
boat 80 u tall overall (mast); C2 x 606-1566 with Pip at 800; shot 4 x 420-1380.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ep12_rough_r2 as M  # noqa: E402
from ep12_rough_r2 import (B, BALL_R, BALL_X, BLOCK_X, CUSH_W, DOWN, FLOOR, GROUND, INK, RED, RES, S, UP,  # noqa: E402
                           alpha, bbox, block50, body_mask, boat2, bucket2, draw_mask, drum2, fit, head_mask, heap2,
                           hook, inout, layer, margin, mdist, name_of, pct, pip_at, qmark_at, rope, teddy_lying,
                           train2, window)

SN = 380
SN_DRUM = 240
CR_FAR, CR_BACK = 1850, 1600
SLAB_T, SLAB_H = 60, 300          # the cushion upright: 60 thick, 300 tall (final fix round: bigger pillow)
CUSH = 300                        # pillow width = height (square), so it rests on the ball as a pillow
PIVOT = (500, GROUND)             # its front-bottom edge once it lands on his toes
HELD_BOT = 1420                   # bottom edge while held at his tummy
T_OPEN = 10.1
THETA0 = math.radians(30)         # tilt the toes give it (it must pass atan(30/120) = 14 deg to tip forward)
M.ZOOM[97.8] = 1.38
PIP_R3 = 990                      # Pip 8.3-17.5 (F6: whole mask >= 30 u from the cushion 10.1-14.4; C2 needs >= 800)
ROPE_L = 330                      # boat's tow rope, measured along its sag
MAST = 80                         # boat's overall height (hull 38 + mast) so it stays clear of head and scarf
T_DRAPE = 0.15                    # soft cushion: contact -> flat over the ball
HTURN = -0.9                      # Snip's head toward the drum 9.2-11.0 (net head turn -0.6)
BOAT_DY = 30                      # Lead pick: boat held 30 u lower (paws and boat)
BOAT_PX, BOAT_PY = 130, 1400      # F7: trailing paw holding the boat (rope leaves its far end, away from him)
SN_388, PIP_388, CR_388 = 190, 335, 1020   # F7 at 38.8: Snip, Pip left of the cushion; Crinkle walks left, train behind
LEG_BAND = 90                     # F7: feet + legs = his figure within 90 u of the floor line
C4_Y = (1260, 1640)               # C4 framed low, ~2.84x
SHEET = (0.5, 8.3, 9.6, 10.3, 17.5, 24.0, 31.0, 44.0, 51.0, 97.8, 119.0, 136.0)
M_PER_U = None


def m_per_u():
    global M_PER_U
    if M_PER_U is None:
        hs = bbox(body_mask(B.snip(SN)))
        M_PER_U = 0.9 / (FLOOR - hs[1])                    # Snip = 0.9 m tall, ears included
    return M_PER_U


def slab_pts(theta, dy=0.0):
    pts = [(-SLAB_T, -SLAB_H), (0, -SLAB_H), (0, 0), (-SLAB_T, 0)]
    c, s = math.cos(theta), math.sin(theta)
    return [(PIVOT[0] + x * c - y * s, PIVOT[1] + dy + x * s + y * c) for x, y in pts]


def slab_mask(theta, dy=0.0):
    return draw_mask(lambda d: d.polygon([S(p) for p in slab_pts(theta, dy)], fill=(0, 0, 0, 255)))


_BALL = None


# ---------------------------------------------------------------- the cushion as a pillow (look fix)
# Two fabric faces sewn at a perimeter seam: puffy middle (60 thick), thin pinched corners, slightly drawn-in edges,
# a centre button with its dimple, dashed stitching. Drawn in 3D with the room's slight down view (z toward the
# camera shows lower by KZ*z) and turned YAW so its face shows while carried; it tips along its face normal.
KZ = 0.28
YAW = math.radians(40)
PZ0 = -SLAB_H / 2 * math.sin(YAW)        # pivot edge centred 120 u back along the fall line from the ball: the pillow lands
PIVOT = (BALL_X - SLAB_H / 2 * math.cos(YAW), GROUND)   # centred on the ball; the edge crosses Snip's plane (z 0) at his toes
NG = 20
BUMP = 110.0
SEAM0 = 4.0                       # seam height at the corners (down at the floor)
BLUE_D = (55, 95, 180)
STITCH = (225, 235, 255)


def _shape(u, v, H, W, T):
    b = H * (u + 0.06 * np.sin(np.pi * v) * (1 - 2 * u))
    f = W * ((v - 0.5) + 0.06 * np.sin(np.pi * u) * (1 - 2 * v))
    r2 = (u - 0.5) ** 2 + (v - 0.5) ** 2
    sv = T / 2 * np.clip(np.sin(np.pi * u) * np.sin(np.pi * v), 0, 1) ** 0.35 * (1 - 0.3 * np.exp(-r2 / 0.004))
    return b, f, sv


def _place(nn, up, f, y0):
    return (PIVOT[0] + nn * math.cos(YAW) - f * math.sin(YAW), y0 - up, PZ0 + nn * math.sin(YAW) + f * math.cos(YAW))


def pose_topple(u, v, k, th, dy):
    b, f, sv = _shape(u, v, SLAB_H, CUSH, SLAB_T)
    a = -SLAB_T / 2 + (sv if k == 0 else -sv)
    return _place(a * math.cos(th) + b * math.sin(th), -a * math.sin(th) + b * math.cos(th), f, PIVOT[1] + dy)


def pose_drape(u, v, k):
    """Final fix round: the whole pillow rests on the ball as one dome (one central bump), its seam sloping from the
    bump to its whole seam (rounded square) down at the floor; puffy faces kept, no flat skirt or flaps."""
    b, f, sv = _shape(u, v, SLAB_H, CUSH, SLAB_T)
    X, _, Z = _place(b, 0.0, f, GROUND)
    q = np.minimum((np.abs(2 * b / SLAB_H - 1) ** 4 + np.abs(2 * f / CUSH) ** 4) ** 0.25, 1.0)   # rounded-square radius
    hc = SEAM0 + (SLAB_T / 2 + BUMP - SEAM0) * (1 - q ** 2) ** 1.2      # whole perimeter (seam) down at the floor
    lo = np.maximum(hc - sv, 0.0)
    return X, GROUND - (lo if k == 0 else lo + 2 * sv), Z


def pose_flat(u, v, k, cx, bottom, w):
    T = SLAB_T * w / 240
    b, f, sv = _shape(u, v, w, w, T)
    return cx - w / 2 + b, bottom - (T / 2 - sv if k == 0 else T / 2 + sv), f


def _depth(q):
    return float(np.mean(KZ * q[:, 1] - q[:, 2]))


def _scr(p):
    return S((p[0], p[1] + KZ * p[2]))


def pillow_items(P, n=NG):
    u, v = np.meshgrid(np.linspace(0, 1, n + 1), np.linspace(0, 1, n + 1), indexing="ij")
    view = np.array([0.0, -KZ, 1.0]); view /= np.linalg.norm(view)
    L = np.array([-0.35, -0.8, 0.5]); L /= np.linalg.norm(L)
    lu = np.r_[np.linspace(.1, .9, 10), [.9] * 10, np.linspace(.9, .1, 10), [.1] * 10]
    lv = np.r_[[.1] * 10, np.linspace(.1, .9, 10), [.9] * 10, np.linspace(.9, .1, 10)]
    eu = np.r_[np.linspace(0, 1, 4 * n + 1), [1.0] * (4 * n + 1), np.linspace(1, 0, 4 * n + 1), [0.0] * (4 * n + 1)]
    ev = np.r_[[0.0] * (4 * n + 1), np.linspace(0, 1, 4 * n + 1), [1.0] * (4 * n + 1), np.linspace(1, 0, 4 * n + 1)]
    items = []
    for k in (0, 1):
        Q = np.stack([np.asarray(c, float) * np.ones_like(u) for c in P(u, v, k)], -1)
        for i in range(n):
            for j in range(n):
                q = np.array([Q[i, j], Q[i + 1, j], Q[i + 1, j + 1], Q[i, j + 1]])
                nr = np.cross(q[2] - q[0], q[3] - q[1]); ln = np.linalg.norm(nr)
                nr = nr / ln if ln else view
                if nr @ view < 0:
                    nr = -nr
                sh = 0.88 + 0.22 * max(0.0, float(nr @ L))
                items.append((_depth(q), "q", q, tuple(min(255, int(c * sh)) for c in M.BLUE[:3])))
        st = np.stack([np.asarray(c, float) for c in P(lu, lv, k)], -1)
        for i in range(0, len(st) - 1, 2):
            items.append((_depth(st[i:i + 2]) - 1.5, "l", st[i:i + 2], STITCH, 2))
        bc = np.array([float(np.asarray(c)) for c in P(np.array(0.5), np.array(0.5), k)])
        items.append((_depth(bc[None]) - 2.0, "b", bc))
    se = np.stack([np.asarray(c, float) for c in P(eu, ev, 0)], -1)
    for i in range(len(se) - 1):
        items.append((_depth(se[i:i + 2]) - 1.0, "l", se[i:i + 2], BLUE_D, 4))
    return items


def render_items(d, items, ink=True):
    if ink:
        for it in items:
            if it[1] == "q":
                d.polygon([_scr(p) for p in it[2]], fill=INK, outline=INK, width=int(6 * RES))
    for it in sorted(items, key=lambda it: -it[0]):
        if it[1] == "q":
            d.polygon([_scr(p) for p in it[2]], fill=it[3], outline=it[3], width=max(1, int(RES)))
        elif it[1] == "l":
            d.line([_scr(p) for p in it[2]], fill=it[4 - 1], width=int(it[4] * RES))
        else:
            c = _scr(it[2]); r = 8 * RES
            d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=BLUE_D, outline=INK, width=int(2 * RES))


def contact_theta():
    u, v = np.meshgrid(np.linspace(0, 1, 25), np.linspace(0, 1, 25), indexing="ij")
    for kk in range(0, 900):
        th = math.radians(kk / 10)
        for k in (0, 1):
            X, Y, Z = pose_topple(u, v, k, th, 0.0)
            if (np.sqrt((X - BALL_X) ** 2 + (Y - (GROUND - BALL_R)) ** 2 + Z ** 2) <= BALL_R).any():
                return th
    return math.pi / 2


def simulate(dt=1 / 480):
    """(t_land_on_toes, t_contact, theta_c, timeline [(t, theta, dy)]) from paws open at T_OPEN."""
    g = 9.81 / m_per_u()                                    # units / s^2
    drop = GROUND - HELD_BOT
    t_drop = math.sqrt(2 * drop / g)
    th_c = contact_theta()
    h, w = SLAB_H, SLAB_T
    r = math.hypot(h, w) / 2
    phi = math.atan2(w / 2, h / 2)
    inertia = (h * h + w * w) / 3
    th, om, t = THETA0, 0.0, T_OPEN + t_drop
    tl = [(T_OPEN, THETA0, -drop), (t, THETA0, 0.0)]
    while th < th_c:
        om += g * r * math.sin(th - phi) / inertia * dt
        th += om * dt
        t += dt
        tl.append((t, th, 0.0))
    return T_OPEN + t_drop, t, th_c, tl


def slab_at(t, tl):
    if t <= T_OPEN:
        return THETA0 * 0, -(GROUND - HELD_BOT)
    if t <= tl[1][0]:
        u = (t - T_OPEN) / (tl[1][0] - T_OPEN)
        return THETA0 * u, -(GROUND - HELD_BOT) * (1 - u * u)
    for tt, th, dy in tl[1:]:
        if tt >= t:
            return th, dy
    return tl[-1][1], 0.0


def cushion_slab(d, theta, dy):
    pts = slab_pts(theta, dy)
    d.polygon([S(p) for p in pts], fill=M.BLUE, outline=INK, width=int(3 * RES))
    cx = sum(p[0] for p in pts) / 4; cy = sum(p[1] for p in pts) / 4
    B.star(d, cx, cy, 13)


def _resample(chain, n):
    seg = [math.dist(a, b) for a, b in zip(chain, chain[1:])]
    out = []
    for k in range(n):
        s, i = sum(seg) * k / (n - 1), 0
        while i < len(seg) - 1 and s > seg[i]:
            s -= seg[i]; i += 1
        u = s / seg[i] if seg[i] else 0.0
        out.append((chain[i][0] + (chain[i + 1][0] - chain[i][0]) * u, chain[i][1] + (chain[i + 1][1] - chain[i][1]) * u))
    return out


def drape_pts(u):
    """Outline morph from the slab at contact (u=0) to the cushion lying flat over the ball with its bulge (u=1)."""
    s = slab_pts(SIM[2])                               # back-top, front-top, pivot, back-bottom
    c = B.cushion_pts(BALL_X, w=CUSH_W)                # left base, over the bulge, right base
    a = _resample([s[2], s[3], s[0], s[1]], 48) + _resample([s[1], s[2]], 16)
    b = _resample(c, 48) + _resample([c[-1], c[0]], 16)
    return [(p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u) for p, q in zip(a, b)]


def cushion_state(t):
    if t < SIM[1]:
        return f"slab {math.degrees(slab_at(t, SIM[3])[0]):.0f} deg"
    return f"drape {min(1.0, (t - SIM[1]) / T_DRAPE):.2f}"


def cushion_items(t):
    """(items, draped): rigid pillow until contact, then a 0.15 s soft drape over the ball."""
    if t < SIM[1]:
        th, dy = slab_at(t, SIM[3])
        return pillow_items(lambda u, v, k: pose_topple(u, v, k, th, dy)), False
    e = 1 - (1 - min(1.0, (t - SIM[1]) / T_DRAPE)) ** 2

    def P(u, v, k):
        A, Bq = pose_topple(u, v, k, SIM[2], 0.0), pose_drape(u, v, k)
        return tuple(np.asarray(a) + (np.asarray(b) - np.asarray(a)) * e for a, b in zip(A, Bq))
    return pillow_items(P), True


def near_items(t):
    items, draped = cushion_items(t)
    return items if draped else [it for it in items if it[0] < KZ * (GROUND - BALL_R)]


def draw_cushion(d, t, ball_x=None):
    """Pillow at time t; with ball_x the ball is drawn between the pillow's far and near parts (until it lands)."""
    items, draped = cushion_items(t)
    if ball_x is None or draped:
        if ball_x is not None:
            B.ball(d, ball_x)
        return render_items(d, items)
    img = d._image
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); render_items(ImageDraw.Draw(lay), items)
    nm = Image.new("RGBA", img.size, (0, 0, 0, 0)); render_items(ImageDraw.Draw(nm), near_items(t), ink=False)
    near = nm.getchannel("A").point(lambda a: 255 if a else 0).filter(ImageFilter.MaxFilter(int(8 * RES) | 1))
    a = lay.getchannel("A")
    far_l = lay.copy(); far_l.putalpha(ImageChops.multiply(a, ImageChops.invert(near))); img.alpha_composite(far_l)
    B.ball(ImageDraw.Draw(img), ball_x)
    near_l = lay.copy(); near_l.putalpha(ImageChops.multiply(a, near)); img.alpha_composite(near_l)


def hump_box():
    """The bulge: screen box of the draped pillow's quads raised above its flat thickness + 10."""
    its = [it for it in pillow_items(pose_drape) if it[1] == "q" and (GROUND - it[2][:, 1]).max() > SLAB_T + 10]
    return bbox(draw_mask(lambda d: render_items(d, its, ink=False)))


def cushion_any(d, cx, cy=None, flat=False, w=240):
    """Replaces B.cushion everywhere: no cy = draped over the ball; cy = lying flat (old 80-tall box, same bottom)."""
    if cy is None:
        return render_items(d, pillow_items(pose_drape))
    return render_items(d, pillow_items(lambda u, v, k: pose_flat(u, v, k, cx, cy + 40, w)))


def boat3(d, x, base=GROUND, strewn=True):
    """r3 boat: hull 38 tall, mast to MAST (80) overall."""
    M.P1.poly(d, [(x - 70, base - 38), (x + 70, base - 38), (x + 50, base), (x - 50, base)], M.BLUE)
    d.line([S((x, base - 38)), S((x, base - MAST))], fill=INK, width=M._w(4))
    M.P1.poly(d, [(x + 4, base - MAST + 4), (x + 4, base - 42), (x + 46, base - 44)], M.WHITE)
    return M.P1.T("boat", (x - 70, base - MAST, x + 70, base), strewn)


def rope_len(a, b, sag=40):
    pts = [(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u + sag * math.sin(math.pi * u)) for u in np.linspace(0, 1, 12)]
    return sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))


def snip_r3(x, t):
    # r3 look pick: both brows level (calm), soft resting mouth, no tilt; head and pupils to the drum (left)
    p = B.snip(x, turn=0.3, hturn=HTURN if t >= 9.2 else 0.0, mouth="w", eyes="normal", brows="calm")
    p.emote(0, 0.3, "neutral")
    if t >= 9.2:
        p.dart(0.5, -12, 5, blink=False)              # down-left: the drum is on the floor to his left
    if t < T_OPEN:
        p.reach(0, 0.3, "r", (x + 118, 1290)); p.reach(0, 0.3, "l", (x + 70, 1330))
    else:
        p.reach(0, 0.3, "r", (x + 70, 1210)); p.reach(0, 0.3, "l", (x - 60, 1230))     # paws open
    return p


def frame(T_):
    if not (8.3 <= T_ <= 14.4 or T_ in (17.5, 36.6, 38.8)):
        return M.frame(T_)
    del M.CUR[:]
    bg = M.P1.background2()
    d = ImageDraw.Draw(bg)
    up, under, cast, over, down, info, extra = [], [], [], [], [], {}, []
    win = None
    up += [lambda d: drum2(d, M.DRUM_X, UP)]
    if 8.3 <= T_ <= 12.8:
        sn = snip_r3(SN, T_)
        pp = pip_at(PIP_R3, turn=0.6 if T_ == 8.3 else -0.4, eyes="normal", mouth="o",
                    brows="calm" if T_ == 8.3 else "worry")
        if T_ == 8.3:
            pp.reach(0, 0.3, "r", (PIP_R3 + 85, 1370)); pp.reach(0, 0.3, "l", (PIP_R3 - 70, 1360))
        cr = B.crinkle(CR_FAR, turn=-0.5, eyes="normal", mouth="smile")
        cast = [sn, pp, cr]
        up += [lambda d: teddy_lying(d, 860, UP), lambda d: boat3(d, 1230, UP)]
        down += [lambda d: bucket2(d, 1050, DOWN), lambda d: heap2(d, 1130, DOWN)]
        bx = BLOCK_X - 92 if T_ == 8.3 else BALL_X
        info["ball_x"] = bx
        info["cushion"] = cushion_state(T_)
        over += [lambda d: block50(d, BLOCK_X, RED, name="red block"), lambda d: draw_cushion(d, T_, ball_x=bx)]
        if T_ == 8.3:
            win = (606, 1100, 1566, 1640)
        else:
            win = (0, 1640 - 1080 / 1.4, 1920 / 1.4, 1640)
            win = (0, max(560, min(win[1], bbox(body_mask(sn))[1] - 12)), 1371.4, 0)
            win = (win[0], win[1], win[2], win[1] + 1080 / 1.4)
    elif 12.8 < T_ <= 14.4:
        sn = B.snip(SN_DRUM, turn=-0.5, eyes="normal", mouth="flat")
        pp = B.pip(PIP_R3, turn=-0.3, eyes="normal", brows="worry", mouth="flat")
        cr = B.crinkle(CR_FAR - (CR_FAR - CR_BACK) * 0.5, turn=-0.5, eyes="normal", mouth="smile")
        cast = [sn, pp, cr]
        over += [lambda d: B.ball(d, BALL_X), lambda d: B.cushion(d, BALL_X, w=CUSH_W)]
        win = (420, 1100, 1380, 1640)
    elif T_ == 17.5:
        sn = B.snip(SN_DRUM, turn=-0.5, eyes="normal", mouth="flat")
        pp = B.pip(PIP_R3 + 40, turn=-0.3, eyes="normal", brows="worry", mouth="flat", look_x=-10)
        pp.reach(0, 0.3, "r", (PIP_R3, 1390)); pp.reach(0, 0.3, "l", (PIP_R3 + 80, 1390))
        cr = B.crinkle(CR_BACK, turn=-0.5, eyes="normal", brows="worry", mouth="smile")
        cast = [sn, pp, cr]
        under += [lambda d: B.ball(d, BALL_X), lambda d: B.cushion(d, BALL_X, w=CUSH_W)]
        hm = head_mask(pp)
        hb = bbox(hm)
        qx, qy = hb[0] - 40, hb[1] + 40
        while mdist(draw_mask(lambda d: qmark_at(d, qx, qy)), hm) > 14:
            qx += 4
        over += [lambda d: qmark_at(d, qx, qy)]
        extra.append(("q", lambda d: qmark_at(d, qx, qy)))
        info["q"] = (qx, qy)
        heads = [bbox(head_mask(p)) for p in (pp, cr)] + [(qx - 32, qy - 64, qx + 32, qy + 40), M.BULGE]
        w0 = fit(heads, 1.4)
        win = (470, w0[1], 1841, w0[3])
    else:                                              # 36.6 C4 / 38.8 W: boat at his tummy, arm forward
        cx = 1180 if T_ == 36.6 else CR_388
        cr = B.crinkle(cx, turn=-0.5, eyes="normal", brows="up", mouth="o" if T_ == 36.6 else "smile_open")
        cr.reach(0, 0.3, "r", (cx + BOAT_PX, BOAT_PY))       # F7: boat in his trailing paw, at his side
        pl = cr.paw(B.T_DRAW, "r")[0]
        bxc, bb = pl[0] + 20, pl[1] + 34
        stern = (bxc + 52, bb - 8)                        # the boat's far end, away from him
        hb = bbox(head_mask(cr))
        dx = 100
        while rope_len(stern, (stern[0] + dx - 6, GROUND - 54)) < ROPE_L:
            dx += 1
        hk = (stern[0] + dx, GROUND - 58)                 # rope ROPE_L u along its sag
        rp = (stern, (hk[0] - 6, hk[1] + 4))
        under += [lambda d: train2(d, hk[0] - 2, GROUND, flip=False, strewn=False)]
        extra.append(("train", lambda d: train2(d, hk[0] - 2, GROUND, flip=False, strewn=False)))
        over += [lambda d: boat3(d, bxc, bb, strewn=False), lambda d: hook(d, *hk), lambda d: rope(d, *rp, sag=40)]
        extra.append(("rope+hook", lambda d: (rope(d, *rp, sag=40), hook(d, *hk))))
        extra.append(("boat", lambda d: boat3(d, bxc, bb, strewn=False)))
        info.update(hook=hk, rope=rp, boat=(bxc, bb), head=hb)
        cast = [cr]
        if T_ == 38.8:
            cast = [B.snip(SN_388, turn=0.4, eyes="happy", mouth="smile_open"), cr,
                    B.pip(PIP_388, turn=0.4, eyes="happy", mouth="smile_open")]
            win = window((960, 1100), 1.0)
        else:
            y0 = max(C4_Y[0], hb[3] + 10)
            w = 1920 * (C4_Y[1] - y0) / 1080
            xm = (hk[0] + 16 + bxc - 70) / 2
            win = (xm - w / 2, y0, xm + w / 2, C4_Y[1])
        under += [lambda d: B.cushion(d, BALL_X, w=CUSH_W), lambda d: drum2(d, BALL_X, GROUND - 165, strewn=False)]
    for fn in up + under:
        fn(d)
    layers = [layer(p, B.T_DRAW) for p in cast]
    for L in layers:
        bg.alpha_composite(L)
    d = ImageDraw.Draw(bg)
    for fn in over + down:
        fn(d)
    info.update(cast=cast, layers=layers, heads={name_of(p): (p, bbox(head_mask(p))) for p in cast},
                toys=list(M.CUR), extra=extra)
    return bg, win, info


def head_scarf(p):
    """Head mask plus, for Crinkle, the scarf's own pixels (band, stripes, tail), closed by 3 units."""
    m = head_mask(p)
    if name_of(p) != "cr":
        return m
    L = np.asarray(layer(p, B.T_DRAW)).astype(int)
    col = np.array(M.R.CRINKLE["scarf"][:3])
    sc = (np.abs(L[..., :3] - col).sum(-1) < 70) & (L[..., 3] > 160)
    sb = bbox(sc)
    orange = (L[..., 0] > 190) & (L[..., 1] > 60) & (L[..., 1] < 160) & (L[..., 2] < 110) & (L[..., 3] > 160)
    box = np.zeros_like(sc)
    box[int((sb[1] - B.LAND_Y0) * RES):int((sb[3] - B.LAND_Y0) * RES), int(sb[0] * RES):int(sb[2] * RES)] = True
    sc = sc | (orange & box)
    k = int(3 * RES)
    grown = sc.copy()
    for dx in range(-k, k + 1, 2):
        for dy in range(-k, k + 1, 2):
            grown |= np.roll(np.roll(sc, dy, 0), dx, 1)
    return m | grown


def measure():
    global THETA0
    pr = print
    t_land, t_c, th_c, tl = SIM
    pr(f"[topple] scale {1000 * m_per_u():.3f} mm/u; drop to his toes {GROUND - HELD_BOT}u = {t_land - T_OPEN:.2f}s; "
       f"tilt {math.degrees(THETA0):.0f} deg -> contact on the ball at {math.degrees(th_c):.1f} deg, t {t_c:.2f} "
       f"(paws open {T_OPEN} -> contact {t_c - T_OPEN:.2f}s; topple alone {t_c - t_land:.2f}s); far edge x "
       f"{PIVOT[0] + SLAB_H * math.sin(th_c):.0f}")
    for th0 in (20, 25, 30):
        keep = THETA0; THETA0 = math.radians(th0)
        s = simulate(); THETA0 = keep
        pr(f"   tilt {th0} deg: paws open -> contact {s[1] - T_OPEN:.2f}s")
    bm = B.ball_mask(BALL_X)
    for t in (10.1, 10.2, 10.3, 10.4, round(t_c, 3), round(t_c + 0.05, 3), round(t_c + 0.1, 3), round(t_c + T_DRAPE, 3),
              11.0, 13.6):
        cm = draw_mask(lambda d: render_items(d, near_items(t)))
        pr(f"[ball visible t={t}] {100 * (bm & ~cm).sum() / bm.sum():.0f}% ({cushion_state(t)})")
    up = pillow_items(lambda u, v, k: pose_topple(u, v, k, 0.0, 0.0))
    fx = [_scr(p)[0] / RES for it in up if it[1] == "q" and it[2][0][0] == it[2][0][0] for p in it[2]]
    fm = bbox(draw_mask(lambda d: render_items(d, [it for it in up if it[1] == "q" and it[3] != 0][:NG * NG])))
    am = bbox(draw_mask(lambda d: render_items(d, up)))
    pr(f"[pillow carried] face (camera side) x {fm[0]:.0f}-{fm[2]:.0f} = {fm[2] - fm[0]:.0f}u wide of {am[2] - am[0]:.0f}u, "
       f"{am[3] - am[1]:.0f}u tall; contact {math.degrees(th_c):.1f} deg")
    dm = draw_mask(lambda d: render_items(d, pillow_items(pose_drape)))
    db = bbox(dm)
    zc = -PZ0 / math.cos(YAW) * math.sin(YAW)
    pr(f"[pivot] edge centre x {PIVOT[0]:.0f} z {PZ0:.0f}; crosses z 0 at x {PIVOT[0] + PZ0 / math.cos(YAW) * math.sin(YAW):.0f}")
    pr(f"[bulge] hump box x {M.BULGE[0]:.0f}-{M.BULGE[2]:.0f} y {M.BULGE[1]:.0f}-{M.BULGE[3]:.0f}")
    pr(f"[pillow draped] bbox x {db[0]:.0f}-{db[2]:.0f} y {db[1]:.0f}-{db[3]:.0f}; top over the ball GROUND-{GROUND - db[1]:.0f}; "
       f"ball hidden {100 - 100 * (bm & ~dm).sum() / bm.sum():.0f}%")
    for T_ in (8.3, 9.6, 10.3, 11.0, 13.6, 17.5, 36.6, 97.8):
        img, win, info = frame(T_)
        hs = " ".join(f"{k}:{'/'.join(map(str, inout(win, b)))}" for k, (p, b) in info["heads"].items())
        wh = " ".join(f"{k}:{'/'.join(map(str, inout(win, bbox(body_mask(p)))))}" for k, (p, b) in info["heads"].items())
        line = [f"[{T_}] win x {win[0]:.0f}-{win[2]:.0f} y {win[1]:.0f}-{win[3]:.0f} z {1920 / (win[2] - win[0]):.2f}",
                f"heads {hs}", f"whole {wh}"]
        if "sn" in info["heads"] and T_ < 15:
            line.append(f"Snip to ball {B._dist_to_ball(layer(info['heads']['sn'][0], B.T_DRAW), BALL_X):.0f}u")
        if T_ == 8.3:
            line.append(f"ball/block margins {margin(win, (info['ball_x'] - BALL_R, GROUND - 110, info['ball_x'] + BALL_R, GROUND)):.0f}/"
                        f"{margin(win, (BLOCK_X - 25, GROUND - 50, BLOCK_X + 25, GROUND)):.0f}")
        if T_ in (9.6, 10.3, 11.0):
            st = info["heads"]["sn"][0].state(B.T_DRAW)
            ht = max(-1, min(1, st["turn"] + st.get("hturn", 0)))
            offs = [round(st["look_x"] * (0.4 + 0.6 * M.R._proj(180, 140, sd * 19.6, ht)[1]) * 1.15, 1) for sd in (-1, 1)]
            line.append(f"Snip pupils look_x {st['look_x']:.1f}, head turn {ht:.2f}, tilt {st.get('tilt', 0):.1f}, "
                        f"offset per eye (u, - = left) {offs}")
        if T_ in (9.6, 10.3):
            line.append(f"drum margin {margin(win, (M.DRUM_X - 65, UP - 112, M.DRUM_X + 65, UP)):.0f}")
        if T_ == 17.5:
            qm = draw_mask(info["extra"][0][1])
            line.append(f"bulge (draped pillow) {pct(M.BULGE, win)}% of frame, margin {margin(win, M.BULGE):.0f}")
            line.append("'?' to heads " + str({k: round(mdist(qm, head_mask(p)), 1) for k, (p, b) in info["heads"].items()}))
        if T_ == 36.6:
            hk, rp = info["hook"], info["rope"]
            pts = [q for q in rope(ImageDraw.Draw(img), *rp, sag=40)]
            inside = [q for q in pts if win[0] <= q[0] <= win[2]]
            xs = [q[0] for q in inside] + [hk[0] - 16, hk[0] + 10]
            ys = [q[1] for q in inside] + [hk[1] - 10, hk[1] + 10]
            line.append(f"rope {rope_len(*rp):.0f}u along its sag")
            line.append(f"hook+rope in frame {pct((min(xs), min(ys), max(xs), max(ys)), win)} (rope span x "
                        f"{rp[1][0]:.0f}-{rp[0][0]:.0f}); boat x {info['boat'][0]:.0f} (in frame: "
                        f"{inout(win, (info['boat'][0] - 70, info['boat'][1] - MAST, info['boat'][0] + 70, info['boat'][1]))})")
            cr = info["heads"]["cr"][1]
            ux = [cr, (hk[0] - 16, hk[1] - 10, hk[0] + 10, hk[1] + 10), (rp[1][0], rp[0][1], rp[0][0], rp[1][1] + 40)]
            line.append(f"2.4x on hook+rope with head out: x1 {cr[0] - 10:.0f}, hook margin {hk[0] - 16 - (cr[0] - 10 - 800):.0f}")
        pr(" | ".join(line))
    for T_ in (36.6, 38.8):
        img, win, info = frame(T_)
        for nm, fn in info["extra"]:
            m = draw_mask(fn)
            pr(f"[F1 {T_}] {nm} to head+scarf " + str({name_of(p): round(mdist(m, head_scarf(p)), 1) for p in info["cast"]}))
    for T_ in (31.0, 33.0):
        img, win, info = M.frame(T_)
        pr(f"[{T_} r2 staging] Snip to ball {B._dist_to_ball(layer(info['heads']['sn'][0], B.T_DRAW), BALL_X):.0f}u")


def cushion_top_h(x0, x1, z0=-25.0, z1=25.0):
    """Highest point of the draped pillow's top face over a footprint (design units above GROUND)."""
    u, v = np.meshgrid(np.linspace(0, 1, 201), np.linspace(0, 1, 201), indexing="ij")
    X, Y, Z = (np.asarray(c, float) * np.ones_like(u) for c in pose_drape(u, v, 1))
    sel = (X >= x0) & (X <= x1) & (Z >= z0) & (Z <= z1)
    return float((GROUND - Y[sel]).max()) if sel.any() else 0.0


_BLOCK50 = M.block50
BLOCK_ON = {}


def block_rest(d, x, col, base=GROUND, *a, **kw):
    """The blue block set on the cushion (31.0): its bottom on the pillow's top face (0 u gap)."""
    if col == M.BLUE and abs(base - (GROUND - 165)) < 1:
        base = GROUND - cushion_top_h(x - 25, x + 25)
        BLOCK_ON[x] = base
    return _BLOCK50(d, x, col, base, *a, **kw)


def legs_mask(p):
    m = body_mask(p).copy()
    bot = bbox(m)[3]
    m[:max(0, int((bot - LEG_BAND - B.LAND_Y0) * RES)), :] = False
    return m


def measure_final():
    pr = print
    dm = draw_mask(lambda d: render_items(d, pillow_items(pose_drape)))
    db = bbox(dm)
    pr(f"[cushion r4] {CUSH}x{CUSH}x{SLAB_T}; draped bbox x {db[0]:.0f}-{db[2]:.0f} y {db[1]:.0f}-{db[3]:.0f}; "
       f"top GROUND-{cushion_top_h(BALL_X - 5, BALL_X + 5, -5, 5):.0f}; contact {SIM[1]:.2f}s")
    worst = (1e9, None)
    pm = {}
    for T_ in (10.1, 10.2, 10.3, 10.4, 10.49, 10.55, 10.64, 10.8, 11.0, 12.0, 12.8, 13.6, 14.4):
        key = "a" if T_ <= 12.8 else "b"
        if key not in pm:
            img, win, info = frame(T_)
            pm[key] = body_mask(info["heads"]["pp"][0])
        cm = draw_mask(lambda d: render_items(d, cushion_items(T_)[0]))
        g = mdist(cm, pm[key])
        worst = min(worst, (g, T_))
        pr(f"[F6 {T_}] cushion to Pip whole mask {g:.1f}u")
    pr(f"[F6] min {worst[0]:.1f}u at {worst[1]} (need 30) {'PASS' if worst[0] >= 30 else 'FAIL'}; Pip x {PIP_R3}")
    img, win, info = frame(9.6)
    hm = head_mask(info["heads"]["sn"][0])
    cm = draw_mask(lambda d: render_items(d, cushion_items(9.6)[0]))
    pr(f"[9.6 carried] Snip head hidden by the pillow {100 * (hm & cm).sum() / hm.sum():.0f}%")
    for T_ in (36.6, 38.8):
        img, win, info = frame(T_)
        cr = info["heads"]["cr"][0]
        rm = draw_mask(dict(info["extra"])["rope+hook"])
        g = mdist(rm, legs_mask(cr))
        pr(f"[F7 {T_}] rope+hook to Crinkle feet+legs ({LEG_BAND}u band) {g:.1f}u (need 10) {'PASS' if g >= 10 else 'FAIL'}")
        dmk = draw_mask(lambda d: render_items(d, pillow_items(pose_drape)))
        tm = draw_mask(dict(info["extra"])["train"])
        pr(f"[F7 {T_}] train box x {bbox(tm)[0]:.0f}-{bbox(tm)[2]:.0f}; train to cushion {mdist(tm, dmk):.1f}u; "
           f"Crinkle to cushion {mdist(body_mask(cr), dmk):.1f}u; win x {win[0]:.0f}-{win[2]:.0f}")
        if T_ == 38.8:
            for p in info["cast"]:
                if name_of(p) != "cr":
                    pr(f"[F7 38.8] rope+hook to {name_of(p)} feet+legs {mdist(rm, legs_mask(p)):.1f}u")
    u, v = np.meshgrid(np.linspace(0, 1, 201), np.linspace(0, 1, 201), indexing="ij")
    X, Y, Z = (np.asarray(c, float) * np.ones_like(u) for c in pose_drape(u, v, 0))
    r = np.hypot(X - BALL_X, Z)
    on = r < BALL_R
    ball_top = BALL_R + np.sqrt(np.maximum(BALL_R ** 2 - r ** 2, 0))
    pr(f"[drape] underside to ball min {((GROUND - Y) - ball_top)[on].min():.1f}u; underside below floor "
       f"{int(((GROUND - Y) < -0.01).sum())} pts; corner seam heights {[round(float(GROUND - Y[i, j]), 1) for i, j in ((0, 0), (0, -1), (-1, 0), (-1, -1))]}")
    img, win, info = M.frame(31.0)
    bx = BALL_X - 40
    pr(f"[block 31.0] base y {BLOCK_ON.get(bx, float('nan')):.1f}; pillow top under it GROUND-{cushion_top_h(bx - 25, bx + 25):.1f} "
       f"-> gap {BLOCK_ON.get(bx, float('nan')) - (GROUND - cushion_top_h(bx - 25, bx + 25)):.1f}u")


SIM = None
if __name__ == "__main__":
    M.block50 = block_rest
    SIM = simulate()
    M.boat2 = M.P1.boat2 = boat3
    B.cushion = cushion_any
    M.BULGE = hump_box()
    a = sys.argv[1:]
    if "--sheet" in a:
        os.makedirs(os.path.join(M.OUT, "ep12"), exist_ok=True)
        tw, th_, g = 780, 439, 12
        sh = Image.new("RGB", (3 * tw + 4 * g, 4 * th_ + 5 * g), (250, 250, 250))
        for i, T_ in enumerate(SHEET):
            img, win, _ = frame(T_)
            full = B.shoot(img, win)
            full.save(os.path.join(M.OUT, "ep12", f"f_{T_:05.1f}.png"))
            sh.paste(full.resize((tw, th_), Image.LANCZOS), (g + (i % 3) * (tw + g), g + (i // 3) * (th_ + g)))
        sh.save(os.path.join(M.OUT, "storyboard.png"))
        print("sheet", os.path.join(M.OUT, "storyboard.png"), sh.size)
    if "--still" in a:
        T_ = float(a[a.index("--still") + 1])
        img, win, _ = frame(T_)
        os.makedirs(os.path.join(M.OUT, "ep12"), exist_ok=True)
        B.shoot(img, win).save(os.path.join(M.OUT, "ep12", f"f_{T_:05.1f}.png"))
    if "--measure" in a:
        measure()
        measure_final()
    if "--final" in a:
        measure_final()
