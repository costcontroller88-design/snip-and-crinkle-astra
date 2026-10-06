"""Rig v2 Pip: the little duckling as an articulated paper puppet (Episode 11 onward), plus face extras (N7).

Built on rig2 without editing it (rig2.py and acting.py stay untouched, so the pilot renders exactly as before):
  * ball-projected head and body turns, like Snip and Crinkle; the beak pokes past the outline when she turns;
  * wings as two-bone arms (40 + 44 design units) with a fan of feather tips that can hold a marker;
  * webbed feet with a waddle walk (the body rocks over the planted foot) and a waddle-run;
  * eyes and brows as the others; beak mouths (smile, sad, open grin, o/O, tongue tip either side, flat, wobble);
  * the three-feather tuft as its own piece with moods (up, normal, droop; "flick" springs it);
  * the red bow on the right of her head, which turns with it;
  * the puff-up: she fluffs into a round ball of feathers, tuft straight up, then un-puffs.

    import hires; hires.set_res(2)
    import rig2_pip as RP
    pip = RP.PipPerf(RP.PipPuppet(0.9), seed=3, x=1180, y=FLOOR, turn=-0.4)
    pip.walk(3.0, 4.4, 1000)                       # tiny waddling steps (pip.run(...) for a waddle-run)
    pip.hop(1.0, 1.4, 1, 30); pip.flap(1.0, 1.6)   # joy: hop and flap
    pip.face(10.0, eyes="glassy", brows="sad", mouth="sad").tuft(10.0, 10.5, "droop")
    pip.puff_up(12.8)                              # poof! ... slowly un-puffs (sound: "poof" at 12.8)
    pip.dance(34.3, 36.3, beats=4)                 # the copycat wiggle-dance
    pip.reach(67.0, 67.4, "r", RP.grip_for_tip(tip, u, pip.a.s))   # marker tip on `tip`, pointing along u
    pip.draw(frame, t, cam, drawing)
    RP.draw_held(frame, cam, pip, t, "r", MARKER, RP.marker_angle(u))   # after Pip: marker + feathers over it

Every Perf2 call works as for the others (to, set, face, hop, wiggle, walk, reach, blink, turn, hturn, tilt,
look_x/y, head_dy, sq, arms_front, no_blink). Mouth names from the others map onto beak mouths
("smile_open" -> open grin, "frown" -> sad, "yum" -> tongue tip, ...).

N7: `crinkle()` (and `snip()`) return rig2 puppets that also know "yum_l" (tongue out of the LEFT side of the
mouth, as seen) and "yum_c" (tongue in the middle, for sliding it across); every other mouth is rig2's own.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import acting as K  # noqa: E402
import hires  # noqa: E402
import rig2 as R  # noqa: E402
from characters import EYE, MOUTH_DARK, TONGUE  # noqa: E402
from hires import RCut  # noqa: E402
from paperlib import mix, place, rot  # noqa: E402
from props_park import (BEAK, BEAK_DARK, BOW, BOW_DARK, DUCK, DUCK_BELLY, DUCK_CHEEK,  # noqa: E402
                        DUCK_DARK)

BEAK_LINE = (170, 76, 26)
WING_LIGHT = mix(DUCK_DARK, DUCK, 0.55)
WING_LINE = (222, 150, 30)

# ---------------------------------------------------------------- geometry (design units; scale 0.9 in episodes)
NECK = 176              # neck point above the feet line
HEAD_DROP = 14          # head pivot below the neck point
HEAD_C = 82             # head centre above the head pivot
HEAD_R = (100, 94)
SHOULDER = (70, 34)     # shoulder x from the middle, y below the neck point (puff pushes them out)
L1, L2 = 40, 44         # wing: upper and fore
FOOT_DX = 32
BEAK_R = 140            # the beak sits on a bigger ball than the head, so it pokes past the outline when turned
BEAK_Y = 30             # beak centre below the head centre
TUFT_UP = 80            # tuft root above the head centre
STEP = 58               # default stride (tiny steps)
MARKER_TIP = 46         # grip -> marker tip

TH = R.THETA_HEAD
TB = R.THETA_BODY


def _sd(v):
    return 1 if v >= 0 else -1


# ---------------------------------------------------------------- head (beak, bow, eyes, brows, cheeks)
BEAK_OF = {"smile": "smile", "w": "smile", "hum": "smile", "sad": "sad", "frown": "sad", "wobble": "wobble",
           "flat": "flat", "grin": "grin", "smile_open": "grin", "open": "grin", "o": "o", "oo": "o", "talk": "o",
           "blow": "o", "O": "O", "tongue": "tongue", "yum": "tongue", "tongue_l": "tongue_l", "yum_l": "tongue_l"}


def _beak(c, cx, by, kind, turn):
    a = math.radians(TH * turn)
    sa = math.sin(a)
    xm = cx + BEAK_R * sa
    w = 1.0 + 0.5 * abs(sa)                       # a little longer in profile
    kind = BEAK_OF.get(kind, "smile")
    if kind == "grin":
        c.ellipse(xm, by + 17, 23 * w, 11, BEAK_DARK)
        c.ellipse(xm, by + 7, 19 * w, 12, MOUTH_DARK, sil=False)
        c.ellipse(xm, by + 13, 11 * w, 6, TONGUE, sil=False)
        c.ellipse(xm, by - 6, 33 * w, 13, BEAK)
        return
    if kind in ("o", "O"):
        big = kind == "O"
        c.ellipse(xm, by + (21 if big else 15), (19 if big else 16) * w, (10 if big else 8), BEAK_DARK)
        c.ellipse(xm, by + (9 if big else 6), (13 if big else 9) * w, (13 if big else 8), MOUTH_DARK, sil=False)
        c.ellipse(xm, by - 6, (32 if big else 30) * w, 13, BEAK)
        return
    c.ellipse(xm, by + 9, 24 * w, 9, BEAK_DARK)
    if kind in ("tongue", "tongue_l"):
        side = 1 if kind == "tongue" else -1
        c.ellipse(xm + side * 13 * w, by + 15, 8, 8, TONGUE)
        c.arc(xm + side * 13 * w, by + 14, 3, 5, 270, 90, 1.6, (214, 96, 120))
    c.ellipse(xm, by, 33 * w, 13, BEAK)
    if kind == "sad":
        c.arc(xm, by + 15, 22 * w, 9, 200, 340, 3.2, BEAK_LINE)
    elif kind == "flat":
        c.line([(xm - 21 * w, by + 4), (xm + 21 * w, by + 4)], 3.2, BEAK_LINE)
    elif kind == "wobble":
        c.line([(xm - 22 * w, by + 5), (xm - 8 * w, by + 1), (xm + 7 * w, by + 6), (xm + 22 * w, by + 2)], 3.2,
               BEAK_LINE)
    else:
        c.arc(xm, by - 1, 25 * w, 9, 20, 160, 3.2, BEAK_LINE)


def _bow(c, x, y, size, sx, tilt=-14):
    s = size / 54

    def P(u, v):
        u *= sx
        ca, sn = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        return x + u * ca - v * sn, y + u * sn + v * ca
    for d in (-1, 1):
        c.polygon([P(0, 0), P(d * 27 * s, -14 * s), P(d * 30 * s, 0), P(d * 25 * s, 14 * s)], BOW)
        c.polygon([P(d * 6 * s, -2 * s), P(d * 20 * s, -8 * s), P(d * 20 * s, 6 * s)], BOW_DARK, sil=False)
    kx, ky = P(0, 0)
    c.ellipse(kx, ky, 8 * s * max(0.6, sx), 8 * s, BOW_DARK)


BOW_PHI, BOW_R, BOW_Y = 50.0, 76.0, 72


def _features(c, cx, cy, eyes, brows, look, turn):
    a = math.radians(TH * turn)
    xm, bw = cx + BEAK_R * math.sin(a), 33 * (1.0 + 0.5 * abs(math.sin(a)))
    for side in (-1, 1):                           # cheeks (a cheek behind the turned beak is hidden)
        x, cs = R._proj(cx, 100, side * 33.0, turn)
        if cs > 0.4 and not xm - bw < x < xm + bw:
            c.ellipse(x, cy + 30, 16 * (0.3 + 0.7 * cs), 10, DUCK_CHEEK, sil=False)
    for side in (-1, 1):                           # eyes and brows, as Snip's and Crinkle's
        x, cs = R._proj(cx, 100, side * 21.0, turn)
        if cs < 0.12:
            continue
        w = 0.4 + 0.6 * cs
        lk = (look[0] * w + 4 * turn, look[1])
        K._eyes2(c, [(x, cy - 10)], eyes, (13 * w, 17), lk)
        R._brow1(c, x, cy - 10, brows, (13 * w, 17), lk, 1 if side < 0 else -1)


def pip_head(eyes, mouth, look, brows, turn, k):
    c = RCut(320, 260, k)
    cx, cy = 160, 140
    bx, bcs = R._proj(cx, BOW_R, BOW_PHI, turn)
    far_bow = bcs < 0.12
    if far_bow:                                    # the bow is round the back: it peeks out behind the head
        _bow(c, bx, cy - BOW_Y, 50, 0.45)
    c.ellipse(cx, cy, HEAD_R[0], HEAD_R[1], DUCK)
    _features(c, cx, cy, eyes, brows, look, turn)
    _beak(c, cx, cy + BEAK_Y, mouth, turn)
    if not far_bow:
        _bow(c, bx, cy - BOW_Y, 50, 0.4 + 0.6 * bcs)
    return c.finish(pivot=(cx, cy + HEAD_C))


# ---------------------------------------------------------------- tuft (its own piece)
TUFT_POSE = {   # (angles from straight up, clockwise +), lengths, widths
    "normal": ((-30, 0, 28), (36, 44, 34), (15, 17, 14)),
    "up": ((-13, 0, 12), (44, 54, 42), (14, 16, 13)),
    "droop": ((-132, -84, 128), (31, 36, 30), (15, 16, 14)),
}
TUFT_MOODS = {"up": 1.0, "perk": 0.5, "normal": 0.0, "low": -0.5, "droop": -1.0}


def _tuft_pose(m):
    a, b = TUFT_POSE["normal"], TUFT_POSE["up" if m >= 0 else "droop"]
    u = abs(m)
    return [[x + (y - x) * u for x, y in zip(pa, pb)] for pa, pb in zip(a, b)]


def pip_tuft(m, k):
    c = RCut(220, 200, k)
    B = (110, 128)
    angs, lens, wids = _tuft_pose(m)
    for i in (0, 2, 1):
        a = math.radians(angs[i])
        d = (math.sin(a), -math.cos(a))
        L, w = lens[i], wids[i]
        c.ellipse(B[0] + d[0] * L * 0.52, B[1] + d[1] * L * 0.52, w / 2, L / 2, DUCK, theta=angs[i])
        c.line([(B[0] + d[0] * L * 0.25, B[1] + d[1] * L * 0.25), (B[0] + d[0] * L * 0.8, B[1] + d[1] * L * 0.8)],
               2.2, DUCK_DARK)
    c.ellipse(B[0], B[1], 11, 9, DUCK)
    return c.finish(pivot=B, border=4)


# ---------------------------------------------------------------- body (and the puff ball)
def _fluff(c, cx, cy, rx, ry, f, n, seed=7):
    """A fluffy rim: soft feather tufts of uneven size round an ellipse (the same every drawing)."""
    import random
    rnd = random.Random(seed)
    for i in range(n):
        th = 2 * math.pi * (i + rnd.uniform(-0.3, 0.3)) / n
        ff = f * rnd.uniform(0.6, 1.25)
        dr = rnd.uniform(-0.4, 0.25) * f
        c.ellipse(cx + (rx + dr) * math.cos(th), cy + (ry + dr) * math.sin(th), ff, ff * 0.85, DUCK,
                  theta=math.degrees(th) + 90)


def pip_head_fluff(k):
    """Puffed-up feathers round the head, drawn behind it (scaled in with the puff, like Snip's frizz)."""
    c = RCut(280, 270, k)
    _fluff(c, 140, 135, 98, 92, 17, 20, seed=11)
    c.ellipse(140, 135, 100, 94, DUCK)
    return c.finish(pivot=(140, 135))


def pip_body(turn, p, k):
    c = RCut(320, 300, k)
    cx, ny = 160, 92                               # the neck point
    cy = ny + 78 - 32 * p
    rx, ry = 80 + 38 * p, 82 + 30 * p
    if abs(turn) >= 0.25:                          # the little tail pokes out at the back
        sd = _sd(turn)
        u = min(1.0, (abs(turn) - 0.25) / 0.5)
        tx, ty = cx - sd * (rx - 10 + 16 * u), cy - 8
        c.ellipse(tx, ty, 22, 11, DUCK, theta=sd * 34)
        c.ellipse(tx - sd * 12, ty - 9, 11, 6, DUCK, theta=sd * 50)
    if p > 0.04:                                   # fluffed-up feathers all round
        _fluff(c, cx, cy, rx - 4, ry - 4, 3 + 15 * min(1.0, p), 20)
    c.ellipse(cx, cy, rx, ry, DUCK)
    bx, cs = R._proj(cx, rx, 0, turn, TB)
    bw, bh = (52 + 22 * p) * (0.55 + 0.45 * cs), 54 + 20 * p
    by = cy + 20 + 6 * p
    c.ellipse(bx, by, bw, bh, DUCK_BELLY, sil=False)
    return c.finish(pivot=(cx, ny))


# ---------------------------------------------------------------- wings (two-bone arms with feather tips)
def _leaf(c, x, y, ang, L, w, col, vein=True):
    """A pointed feather from (x, y), `ang` degrees from straight down (+ towards +x), length L, width w."""
    a = math.radians(ang)
    d, n = (math.sin(a), math.cos(a)), (math.cos(a), -math.sin(a))
    side1, side2 = [], []
    for i in range(13):
        u = i / 12
        h = w / 2 * math.sin(math.pi * (0.12 + 0.88 * u)) ** 0.7
        px, py = x + d[0] * L * u, y + d[1] * L * u
        side1.append((px + n[0] * h, py + n[1] * h))
        side2.append((px - n[0] * h, py - n[1] * h))
    c.polygon(side1 + side2[::-1], col)
    if vein:
        c.line([(x + d[0] * L * 0.3, y + d[1] * L * 0.3), (x + d[0] * L * 0.8, y + d[1] * L * 0.8)], 1.8, WING_LINE)


def pip_upper(k):
    c = RCut(56, 22 + L1 + 26, k)
    cx, top = 28, 22
    c.ellipse(cx, top, 23, 23, DUCK_DARK)
    c.polygon([(cx - 23, top), (cx + 23, top), (cx + 17, top + L1), (cx - 17, top + L1)], DUCK_DARK)
    c.ellipse(cx, top + L1, 17, 17, DUCK_DARK)
    c.ellipse(cx - 3, top + 2, 12, 14, WING_LIGHT, sil=False)
    for f in (0.42, 0.78):
        c.arc(cx, top + L1 * f - 6, 13, 8, 30, 150, 2.0, WING_LINE)
    return c.finish(pivot=(cx, top))


FAN = ((-36, 30, 15), (36, 30, 15), (0, 36, 16))
FAN_POINT = ((-18, 22, 13), (18, 22, 13), (0, 46, 15))


def pip_fore(k, point=False):
    c = RCut(90, 18 + L2 + 52, k)
    cx, top = 45, 18
    tip = top + L2
    for ang, L, w in (FAN_POINT if point else FAN):
        _leaf(c, cx, tip - 12, ang, L, w, DUCK_DARK)
    c.ellipse(cx, top, 17, 17, DUCK_DARK)
    c.polygon([(cx - 17, top), (cx + 17, top), (cx + 14, tip - 6), (cx - 14, tip - 6)], DUCK_DARK)
    c.ellipse(cx, tip - 6, 14, 12, DUCK_DARK)
    c.arc(cx, top + L2 * 0.45, 11, 7, 30, 150, 2.0, WING_LINE)
    return c.finish(pivot=(cx, top))


def pip_grip(k):
    """The two front tip feathers, drawn over a held marker so the wing wraps round it."""
    c = RCut(70, 70, k)
    for ang in (52, -44):
        _leaf(c, 35, 29, ang, 25, 13, DUCK_DARK)
    return c.finish(pivot=(35, 35), border=4)


def pip_foot(k, view):
    """view: 0 front, 1 pointing right, -1 pointing left."""
    if view == 0:
        c = RCut(96, 48, k)
        c.ellipse(48, 21, 30, 12, BEAK)
        for dx, dy in ((-20, 28), (0, 32), (20, 28)):
            c.ellipse(48 + dx, dy, 10, 8, BEAK)
        for dx in (-10, 10):
            c.line([(48 + dx * 0.4, 17), (48 + dx * 1.2, 31)], 2.0, BEAK_DARK)
        return c.finish(pivot=(48, 38), border=4)
    c = RCut(110, 52, k)
    x0 = 24
    c.ellipse(x0 + 4, 30, 11, 9, BEAK)
    c.polygon([(x0 + 4, 21), (x0 + 50, 14), (x0 + 62, 30), (x0 + 50, 44), (x0 + 4, 39)], BEAK)
    for dx, dy in ((50, 17), (62, 30), (50, 42)):
        c.ellipse(x0 + dx, dy, 8, 6.5, BEAK)
    for dx, dy in ((44, 20), (54, 30), (44, 40)):
        c.line([(x0 + 12, 30), (x0 + dx, dy)], 2.0, BEAK_DARK)
    spr = c.finish(pivot=(x0 + 22, 44), border=4)
    if view < 0:
        from characters import _mirror
        spr = _mirror(spr)
    return spr


# ---------------------------------------------------------------- the puppet
class PipPuppet(R.Puppet):
    """A rig2 puppet for Pip (kind "pip"). Use it with PipPerf (or plain rig2.Perf2: everything but the waddle,
    flaps, dance and puff helpers works)."""

    def __init__(self, scale=0.9):                 # rig2.Puppet.__init__ only knows Snip and Crinkle: set up here
        self.kind, self.s = "pip", scale
        self.k = k = scale * hires.RES
        self.neck, self.head_drop, self.sh = NECK, HEAD_DROP, SHOULDER
        self.L1, self.L2, self.foot_dx = L1, L2, FOOT_DX
        self._default = ("normal", "smile")
        self.upper, self.fore, self.fore_pt = pip_upper(k), pip_fore(k), pip_fore(k, point=True)
        self.grip = pip_grip(k)
        self.fluff = pip_head_fluff(k)
        self.feet = {v: pip_foot(k, v) for v in (-1, 0, 1)}
        self.ear = self.frizz = None
        self.shadow = R._contact_shadow(int(170 * scale), hires.RES)
        self._heads, self._bodies, self._tufts = {}, {}, {}

    # --- sprites
    def head(self, eyes, mouth, look, brows, turn):
        key = (eyes, mouth, look, brows, R._q(turn, R.TURN_Q))
        if key not in self._heads:
            self._heads[key] = pip_head(eyes, mouth, look, brows, key[-1], self.k)
        return self._heads[key]

    def body(self, turn, puff=0.0):
        key = (R._q(turn, 0.25), R._q(min(1.15, max(0.0, puff)), 0.1))
        if key not in self._bodies:
            self._bodies[key] = pip_body(key[0], key[1], self.k)
        return self._bodies[key]

    def tuft(self, m):
        key = R._q(max(-1.0, min(1.35, m)), 0.1)
        if key not in self._tufts:
            self._tufts[key] = pip_tuft(key, self.k)
        return self._tufts[key]

    # --- geometry (world design units)
    def shoulder(self, st, side):
        p = max(0.0, st.get("puff", 0.0))
        shx, shy = self.sh[0] + 40 * p, self.sh[1] - 16 * p
        Rr = shx / math.sin(math.radians(70))
        sx, _ = R._proj(0, Rr, -70 if side == "l" else 70, st["turn"], TB)
        return self.anchor(st)(sx, (-self.neck + shy) * st["sq"])

    def _head_turn(self, st):
        return max(-1.0, min(1.0, st["turn"] + st.get("hturn", 0.0)))

    def _head_local(self, st, x, y):
        hx, hy = self.head_pivot(st)
        dx, dy = rot(x * self.s, y * self.s, st["lean"] + st["tilt"])
        return hx + dx, hy + dy

    def face_point(self, st, local):
        """World position of a point on the face: local x from the face centre line, y from the head pivot."""
        t = self._head_turn(st)
        return self._head_local(st, 104 * math.sin(math.radians(TH * t)) + local[0], local[1])

    def beak_point(self, st):
        t = self._head_turn(st)
        return self._head_local(st, BEAK_R * math.sin(math.radians(TH * t)), -(HEAD_C - BEAK_Y))

    def head_centre(self, st):
        return self._head_local(st, 0, -HEAD_C)

    def tuft_root(self, st):
        t = self._head_turn(st)
        return self._head_local(st, 42 * math.sin(math.radians(TH * t)), -(HEAD_C + TUFT_UP))

    # --- drawing
    def _arm(self, base, cam, st, side):
        S, E, W, fa = self.arm_points(st, side)
        a = (st["arm_l"] if side == "l" else st["arm_r"]) + st["lean"]
        place(base, self.upper, cam.S(S), angle=a, alpha=st["alpha"])
        fore = self.fore_pt if st.get("point_" + side, 0.0) > 0.5 else self.fore
        place(base, fore, cam.S(E), angle=fa, alpha=st["alpha"])

    def draw(self, base, cam, st, front=False):
        s, t, A = self.s, st["turn"], st["alpha"]
        p = max(0.0, st.get("puff", 0.0))
        place(base, self.shadow, cam.S((st["x"], st["y"] + 6)), alpha=max(0.25, 1 - st["hop"] / 140) * A,
              sx=max(0.6, 1 - st["hop"] / 260) * (1 + 0.3 * p), shadow=False)
        foot = self.feet[1 if t > 0.4 else (-1 if t < -0.4 else 0)]
        for i, side in enumerate((-1, 1)):
            rel, lift = st["feet"][i]
            fdx, _ = R._proj(0, self.foot_dx / 0.5, side * 30, t, TB)
            place(base, foot, cam.S((st["x"] + fdx * s + rel, st["y"] - st["hop"] - lift)), alpha=A)
        far = "r" if t > 0.35 else ("l" if t < -0.35 else None)
        if far and not front:
            self._arm(base, cam, st, far)
        neck = self.anchor(st)(0, -self.neck * st["sq"])
        place(base, self.body(t, p), cam.S(neck), angle=st["lean"], alpha=A, sx=1 / math.sqrt(st["sq"]),
              sy=st["sq"])
        if not front:
            for side in ("l", "r"):
                if side != far:
                    self._arm(base, cam, st, side)
        hx, hy = self.head_pivot(st)
        ha = st["lean"] + st["tilt"]
        th = self._head_turn(st)
        if p > 0.04:                                   # puffed: fluffy feathers round the head too
            place(base, self.fluff, cam.S(self.head_centre(st)), angle=ha, scale=0.86 + 0.14 * min(1.0, p),
                  alpha=A)
        look = (int(round(st["look_x"] / 2) * 2), int(round(st["look_y"] / 2) * 2))
        place(base, self.head(st["eyes"], st["mouth"], look, st["brows"], th), cam.S((hx, hy)), angle=ha, alpha=A)
        m = st.get("tuft", 0.0)
        m = m + (1.0 - m) * min(1.0, p)                # puffed up: the tuft stands straight up, taller
        ta = st.get("tuft_a", 0.0) * (1 - min(1.0, p))
        place(base, self.tuft(m), cam.S(self.tuft_root(st)), angle=ha + ta, sy=1 + 0.3 * min(1.0, p), alpha=A)
        if front:
            for side in ("l", "r"):
                self._arm(base, cam, st, side)


# ---------------------------------------------------------------- the performance
REST = dict(arm_l=-12.0, arm_r=12.0, elb_l=16.0, elb_r=-16.0)


class PipPerf(R.Perf2):
    """Perf2 for Pip: the same timeline calls, plus tuft moods, puff-up, flaps, the copycat dance, a shiver,
    a self-hug, wing points, and a waddle (walk) / waddle-run (run)."""
    NUM = R.Perf2.NUM + ("tuft", "tuft_a", "puff", "point_l", "point_r")

    def __init__(self, puppet, seed=0, **init):
        base = dict(REST, tuft=0.0, tuft_a=0.0, puff=0.0, point_l=0.0, point_r=0.0)
        base.update(init)
        super().__init__(puppet, seed, **base)
        self.runs, self.flaps, self.dances = [], [], []

    # --- authoring
    def walk(self, t0, t1, x1, steps=None):
        """Waddle from wherever x is at t0 to x1 with tiny planted steps (the body rocks over each foot)."""
        if steps is None:
            steps = max(2, int(round(abs(x1 - self._num("x", t0)) / (STEP * self.a.s))))
        return super().walk(t0, t1, x1, steps)

    def run(self, t0, t1, x1, steps=None):
        """Waddle-run: quicker, bigger rock, leaning forward, wings out behind."""
        self.walk(t0, t1, x1, steps)
        self.runs.append((t0, t1))
        return self

    def tuft(self, t0, t1, mood, ease="back"):
        """Tuft moods: "up", "perk", "normal", "low", "droop"; "flick" springs it (t1 unused)."""
        if mood == "flick":
            return self.wiggle(t0, "tuft_a", 24, 4.5, 4.0)
        return self.to(t0, t1, ease, tuft=TUFT_MOODS[mood])

    def puff_up(self, t, hold=0.5, out=0.9, face=True):
        """Startled: poof into a round ball of feathers (0.14 s), tuft straight up; hold; slowly un-puff."""
        self.to(t, t + 0.14, "back", puff=1.0)
        self.to(t + 0.14 + hold, t + 0.14 + hold + out, "io", puff=0.0)
        self.no_blink.append((t, t + 0.14 + hold))
        if face:
            self.face(t, eyes="wide", brows="up", mouth="o")
        return self

    def flap(self, t0, t1, n=None, amp=58):
        """Wings flap out and back n times (default: about 6 a second)."""
        n = n if n is not None else max(1, int(round((t1 - t0) * 6)))
        self.flaps.append((t0, t1, n, amp))
        return self

    def dance(self, t0, t1, beats=4, amp=7.0, bounce=9.0):
        """The happy wiggle-dance in miniature: wings up, side to side on each beat, little bounces, tuft flicks."""
        self.dances.append((t0, t1, beats, amp, bounce))
        return self

    def shiver(self, t0, dur=0.7):
        """A small shiver: fast tiny shake, the tuft dips and comes back."""
        self.wiggle(t0, "x", 2.6, 15.0, 3.5 / dur)
        self.wiggle(t0, "sq", -0.02, 15.0, 3.5 / dur)
        return self.wiggle(t0, "tuft", -0.7, 1.4, 2.5)

    def point(self, t0, t1, side, target, ease="back"):
        """Point the wing straight at a target (the middle feather points)."""
        st = self.state(t1)
        S = self.a.shoulder(st, side)
        d = math.hypot(target[0] - S[0], target[1] - S[1]) or 1.0
        far = (S[0] + (target[0] - S[0]) * 300 / d, S[1] + (target[1] - S[1]) * 300 / d)
        self.set(t0, **{"point_" + side: 1.0})
        return self.reach(t0, t1, side, far, ease)

    def unpoint(self, t0, t1, side, ease="io"):
        self.to(t0, t1, ease, **{("arm_" + side): REST["arm_" + side], ("elb_" + side): REST["elb_" + side]})
        return self.set(t1, **{"point_" + side: 0.0})

    def hug_self(self, t0, t1, ease="io"):
        """Hug herself small: wing tips cross over the tummy, shoulders up, a little squash."""
        st = self.state(t1)
        P = self.a.anchor(st)
        self.reach(t0, t1, "l", P(30, -88), ease, bend=-1)
        self.reach(t0, t1, "r", P(-30, -80), ease, bend=1)
        return self.to(t0, t1, ease, sq=0.93, head_dy=5)

    def rest_wings(self, t0, t1, ease="io"):
        return self.to(t0, t1, ease, **REST)

    # --- evaluation
    def state(self, t, drawing=None):
        s = K.Perf.state(self, t, drawing)
        sc = self.a.s
        feet = [[0.0, 0.0], [0.0, 0.0]]
        for t0, t1, x0, x1, n in self.walks:
            if not t0 <= t <= t1:
                continue
            run = any(abs(a - t0) < 1e-6 and abs(b - t1) < 1e-6 for a, b in self.runs)
            d = 1 if x1 >= x0 else -1
            T = (t1 - t0) / n
            stride = abs(x1 - x0) / n
            env = min(1.0, (t - t0) / (0.5 * T), (t1 - t) / (0.5 * T))
            ph = ((t - t0) / (2 * T)) % 1.0
            lift_h = (15 if run else 11) * sc
            for i, off in enumerate((0.0, 0.5)):
                q = (ph + off) % 1.0
                if q < 0.5:                                  # planted: slides back as the body moves on
                    rel, lift = d * (stride / 2 - stride * q / 0.5), 0.0
                else:                                        # swinging forward
                    u = (q - 0.5) / 0.5
                    rel, lift = d * (-stride / 2 + stride * u), lift_h * math.sin(math.pi * u)
                feet[i] = [rel * env, lift * env]
            s["lean"] += env * ((8.0 if run else 6.0) * math.sin(2 * math.pi * ph) - (9.0 if run else 3.0) * d)
            s["hop"] += (6 if run else 3) * sc * env * (0.5 - 0.5 * math.cos(4 * math.pi * ph))
            flare = env * ((34.0 if run else 9.0) + (10.0 if run else 4.0) * math.sin(4 * math.pi * ph))
            s["arm_l"] -= flare
            s["arm_r"] += flare
            if run:
                s["elb_l"] -= 20 * env
                s["elb_r"] += 20 * env
        s["feet"] = feet
        for t0, t1, n, amp in self.flaps:
            if t0 <= t < t1:
                v = amp * (0.5 - 0.5 * math.cos(2 * math.pi * n * (t - t0) / (t1 - t0)))
                s["arm_l"] -= v
                s["arm_r"] += v
                s["elb_l"] -= 0.3 * v
                s["elb_r"] += 0.3 * v
        for t0, t1, beats, amp, bounce in self.dances:
            if t0 <= t <= t1:
                env = min(1.0, (t - t0) / 0.25, (t1 - t) / 0.25)
                q = (t - t0) / (t1 - t0) * beats                  # beats so far
                side = math.sin(math.pi * q)                      # one side per beat
                s["lean"] += env * amp * side
                s["x"] += env * 4 * sc * side
                s["hop"] += env * bounce * sc * abs(math.sin(math.pi * q))
                for arm, elb, sd in (("arm_l", "elb_l", -1), ("arm_r", "elb_r", 1)):
                    s[arm] += (sd * (134 + 10 * side * sd) - s[arm]) * env
                    s[elb] += (sd * 26 - s[elb]) * env
                s["tuft_a"] += env * 10 * side
                s["tilt"] += env * 5 * side
        p = max(0.0, s["puff"])
        if p > 0:
            s["arm_l"] -= 26 * p
            s["arm_r"] += 26 * p
            s["head_dy"] += 12 * p
        return s


# ---------------------------------------------------------------- holding a marker in a wing tip
def marker_sprite(body=(250, 250, 246), ink=(40, 36, 44), scale=1.0):
    """A chunky kids' marker drawn pointing DOWN from its grip point (pivot), tip at MARKER_TIP * scale."""
    k = scale * hires.RES
    c = RCut(44, 130, k)
    gx, gy = 22, 50
    c.rrect(gx - 10, gy - 44, gx + 10, gy + 26, 9, body)
    c.rrect(gx - 10, gy - 44, gx + 10, gy - 30, 8, ink)
    c.rrect(gx - 10, gy + 4, gx + 10, gy + 10, 2, ink, sil=False)
    c.polygon([(gx - 9, gy + 24), (gx + 9, gy + 24), (gx + 5, gy + 36), (gx - 5, gy + 36)], (200, 200, 194))
    c.polygon([(gx - 5, gy + 35), (gx + 5, gy + 35), (gx + 2, gy + MARKER_TIP), (gx - 2, gy + MARKER_TIP)], ink)
    return c.finish(pivot=(gx, gy), border=4)


def marker_angle(u):
    """Placement angle that points a down-drawn tool along the unit vector u (world)."""
    return math.degrees(math.atan2(u[0], u[1]))


def marker_tip(grip, ang, scale):
    dx, dy = rot(0, MARKER_TIP * scale, ang)
    return grip[0] + dx, grip[1] + dy


def grip_for_tip(tip, u, scale):
    """Where the wing tip must be so the marker's tip lands on `tip` while the marker points along u."""
    return tip[0] - MARKER_TIP * scale * u[0], tip[1] - MARKER_TIP * scale * u[1]


def draw_held(base, cam, perf, t, side, spr, ang, st=None):
    """Draw a held marker (or any down-drawn tool) at the wing tip, then the front feathers over it.
    Call right after perf.draw (or after the prop the wing is in front of). Returns the marker tip."""
    s = st or perf.state(t)
    W, _ = perf.paw(t, side, s)
    place(base, spr, cam.S(W), angle=ang, alpha=s["alpha"])
    place(base, perf.a.grip, cam.S(W), angle=ang, alpha=s["alpha"])
    return marker_tip(W, ang, perf.a.s)


# ---------------------------------------------------------------- N7: tongue out of the left side (others too)
_RIG2_MOUTH = R._mouth2


def _mouth_ext(c, cx, my, kind, k=1.0):
    if kind in ("yum_l", "yum_c"):
        c.arc(cx, my - 6 * k, 24 * k, 18 * k, 25, 155, 5 * k, EYE)
        dx, dy = (-13, 7) if kind == "yum_l" else (0, 10)
        c.ellipse(cx + dx * k, my + dy * k, 8 * k, 7 * k, TONGUE, sil=False)
    else:
        _RIG2_MOUTH(c, cx, my, kind, k)


EXTRA_MOUTHS = ("yum_l", "yum_c")


def _ext_head(fn):
    def head(eyes, mouth, look, brows, turn, k):
        if mouth not in EXTRA_MOUTHS:
            return fn(eyes, mouth, look, brows, turn, k)
        R._mouth2 = _mouth_ext                     # only while this one head is drawn; rig2 is put back at once
        try:
            return fn(eyes, mouth, look, brows, turn, k)
        finally:
            R._mouth2 = _RIG2_MOUTH
    return head


def with_extra_mouths(puppet):
    """Give a rig2 Snip or Crinkle puppet the extra mouths "yum_l" and "yum_c"."""
    puppet._head_fn = _ext_head(puppet._head_fn)
    return puppet


def crinkle(scale=1.2):
    return with_extra_mouths(R.Puppet("crinkle", scale))


def snip(scale=1.15):
    return with_extra_mouths(R.Puppet("snip", scale))
