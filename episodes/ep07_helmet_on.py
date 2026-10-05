"""Episode 7 — Helmet On? 🚲⛑️

A sunny garden: a curved path, flowers, a white picket fence and an apple tree. Snip sits on a
shiny paper tricycle, bouncing to ride; the bike helmet hangs on a hook on the fence post.
Choice: ride with a bare head, or helmet on? Snip pedals off bare-headed, the front wheel hits a
little bump in the path and BOING -- Snip bounces up (ears poke the apple tree) and lands back on
the seat; a leaf flutters down and lands softly on Snip's bare head. Snip looks at the helmet.
Crinkle brings it and tosses it up like a ring toss... but Snip's tall ears pop it off, boing,
boing! Crinkle shows the ear holes. Helmet on (1) with the ears through the holes, level on the
forehead; strap click (2) under the chin; wiggle test (3) -- it stays snug. Check! A happy, slow
ride round the path (round the tree), hearts, the signature paw-bump, and the loop: unclick,
the ears boing the helmet back onto its hook, Snip rolls back to the start (frame 18.0 == frame 0).

Run:  python3 episodes/ep07_helmet_on.py            (render -> output/)
      python3 episodes/ep07_helmet_on.py --stills   (contact sheet -> build/)
      python3 episodes/ep07_helmet_on.py --keys     (key frames -> reviews/ep07_keys.png)
"""
import math
import os
import subprocess
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

from PIL import Image  # noqa: E402

import audio as A  # noqa: E402
import icons  # noqa: E402
import props_helmet as P  # noqa: E402
import props_park as PK  # noqa: E402
import scene  # noqa: E402
from characters import SNIP_EAR_BASE, SNIP_EAR_TILT, Character  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, rot, seg  # noqa: E402

FPS = 30
DUR = 18.0
G = P.GROUND
SX0, SX1 = 300, 440                   # Snip's start spot / where the trike stops after the bump
SX2 = 380                             # where the ride ends (paw-bump spot)
CR_X = 780
CR_REST_L = 346
EAR_L = 278                           # ear pivot -> ear tip (scale 1.15)
CARRY_RIM = (CR_X, 1425)              # helmet rim centre when Crinkle carries it at his tummy
MEET = (552, 1180)                    # paw-bump meeting point (in the gap between them)
CR_BUMP_X = 760
CANOPY_AT = (300, 350)

BG = P.background()
CANOPY = P.canopy()
TRUNK = P.trunk()
HOOK_SPR = P.hook_sprite()
BUMP = P.bump()
LEAF = P.leaf_sprite()
TRIKE = P.Trike()
HEL = P.Helmet()
SUN = PK.sun()
CLOUDS = [(PK.cloud(300, 130), 640, 330, 0.0), (PK.cloud(240, 110), 960, 560, 2.1), (PK.cloud(210, 96), 820, 140, 4.0)]
BUB_BARE = P.choice_bubble("bare", (240, 110, 100))
BUB_HELMET = P.choice_bubble("helmet", (90, 190, 120))
CALLOUTS = [P.hole_callout(e) for e in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)]
QMARK = icons.question()
CHECK = icons.check(130)
CLICK = P.click_burst()
BOING = P.boing_lines()
GLINT = P.glint()
GLOW = P.soft_glow((255, 240, 140), 300, 235)
SPARKLE = scene.sparkle()
NUMS = [scene.numeral(1, (244, 112, 104)), scene.numeral(2, (255, 196, 52)), scene.numeral(3, (84, 182, 222))]
HEARTS = [scene.heart(c, 80) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120), (255, 150, 170))]
SNIP = Character("snip", 1.15)
CR = Character("crinkle", 1.2)

SNIP_BLINKS = (1.85, 6.35, 9.3, 12.6, 14.1, 16.95)
CR_BLINKS = (7.0, 8.15, 9.6, 12.9, 14.25)
T_GO, T_HIT, T_HOP0, T_HOP1, T_STOP = 4.5, 4.95, 4.98, 5.55, 5.85
T_APEX = (T_HOP0 + T_HOP1) / 2
T_LEAF0, T_LEAF1, T_LEAF_OFF = 5.3, 6.15, 6.95
T_CR0, T_CR1 = 6.3, 6.85
T_GRAB, T_TAKE = 6.95, 7.25
TOSS = ((7.3, 7.58, 7.7, 8.1), (8.2, 8.46, 8.56, 9.0))   # (throw, land on ear tips, BOING, caught)
T_CALL0, T_CALL_EARS, T_CALL1 = 9.05, 9.5, 9.95
T_TOSS3, T_ABOVE, T_ON = 9.95, 10.2, 10.45
COUNTS = (10.45, 10.9, 11.35)
T_CLICK = 10.9
T_WIG0, T_WIG1 = 11.3, 11.9
T_CHECK = 11.92
T_RIDE0, T_TURN1, T_LEFT1, T_TURN2, T_RIDE1 = 12.2, 12.55, 13.25, 13.6, 14.4
HEART_PLAN = ((13.0, 330, 760), (13.3, 600, 700), (13.6, 450, 620), (13.9, 760, 760))
T_UNCLICK, T_POP, T_HANG, T_BACK0, T_BACK1 = 16.42, 16.55, 17.15, 16.9, 17.6


# ---------------------------------------------------------------- helpers (as in the reference episodes)
def blinking(t, times, d=0.13):
    return any(0 <= t - b < d for b in times)


def spring(t, t0, amp, freq=5.0, damp=4.5):
    if t < t0:
        return 0.0
    dt = t - t0
    return amp * math.exp(-damp * dt) * math.sin(2 * math.pi * freq * dt)


def hop_curve(t, t0, t1, n, height):
    """Hop height plus squash/stretch (stretch in the air, squash on take-off and landing)."""
    p = seg(t, t0, t1)
    if 0 < p < 1:
        q = (p * n) % 1.0
        h = height * math.sin(math.pi * q)
        sq = 1 + 0.08 * math.sin(math.pi * q) - 0.12 * (max(0, 1 - q / 0.12) + max(0, 1 - (1 - q) / 0.12))
        return h, sq
    if 0 <= t - t1 < 0.14:
        return 0.0, 1 - 0.1 * (1 - (t - t1) / 0.14)
    return 0.0, 1.0


def breath(t, period=2.0, amp=0.012):
    return 1 + amp * math.sin(2 * math.pi * t / period)


def frozen(t):
    return 2.5 <= t < 4.5


def pop_scale(t, t0, d=0.3):
    return ease_out_back(seg(t, t0, t0 + d))


def ease_in(t):
    t = min(max(t, 0.0), 1.0)
    return t * t


def near(a, ref):
    """Same direction as angle a, unwrapped to be closest to ref (so arms never swing the long way)."""
    return a + 360 * round((ref - a) / 360)


def arc(a, b, s, h):
    """Point on a toss arc from a to b (s in 0..1) that rises h px above the straight line."""
    return (lerp(a[0], b[0], s), lerp(a[1], b[1], s) - h * 4 * s * (1 - s))


def walk_bob(t, t0, t1, steps):
    p = seg(t, t0, t1)
    if 0 < p < 1:
        return 10 * abs(math.sin(math.pi * steps * p)), 4 * math.sin(math.pi * steps * p)
    return 0.0, 0.0


# ---------------------------------------------------------------- the trike's path
def trike_x(t):
    if t < T_GO:
        return SX0
    if t < T_HIT:
        return SX0 + 90 * ease_in(seg(t, T_GO, T_HIT))
    if t < T_RIDE0:
        return 390 + (SX1 - 390) * ease_out(seg(t, T_HIT, T_STOP))
    if t < T_TURN1:
        return lerp(SX1, 425, ease_in_out(seg(t, T_RIDE0, T_TURN1)))
    if t < T_LEFT1:
        return lerp(425, 215, ease_in_out(seg(t, T_TURN1, T_LEFT1)))
    if t < T_TURN2:
        return lerp(215, 205, ease_in_out(seg(t, T_LEFT1, T_TURN2)))
    if t < T_BACK0:
        return lerp(205, SX2, ease_in_out(seg(t, T_TURN2, T_RIDE1)))
    return lerp(SX2, SX0, ease_in_out(seg(t, T_BACK0, T_BACK1)))


def trike_k(t):
    """Facing: +1 right, -1 left (paper-puppet turn in between)."""
    if T_RIDE0 <= t < T_TURN1:
        return math.cos(math.pi * ease_in_out(seg(t, T_RIDE0, T_TURN1)))
    if T_TURN1 <= t < T_LEFT1:
        return -1.0
    if T_LEFT1 <= t < T_TURN2:
        return -math.cos(math.pi * ease_in_out(seg(t, T_LEFT1, T_TURN2)))
    return 1.0


def trike_gy(t):
    """Round the tree: the path curves a little further back behind the trunk."""
    return G - 30 * math.sin(math.pi * seg(t, T_TURN1 - 0.1, T_RIDE1 - 0.3)) ** 2


def trike_lift(t):
    """(lift, pitch): the bump. A big jolt when riding fast; a tiny one on the slow, safe ride."""
    if T_HIT - 0.03 <= t < T_HIT + 0.4:
        k = math.sin(math.pi * seg(t, T_HIT - 0.03, T_HIT + 0.4))
        return 34 * k, 7 * math.sin(math.pi * seg(t, T_HIT - 0.03, T_HIT + 0.25))
    if T_TURN2 <= t < T_RIDE1 + 0.3:
        fx = trike_x(t) + P.FRONT_HUB[0]
        d = (fx - P.BUMP_X) / 60
        if abs(d) < 1:
            return 7 * math.cos(math.pi * d / 2) ** 2, 2.5 * math.sin(math.pi * d)
    return 0.0, 0.0


def _wheel_rolls():
    """Wheel angles (deg) from the distance travelled; nudged during the ride so every wheel and the
    pedals land back on their starting angle at the loop point."""
    ts = np.arange(0, DUR + 1e-9, 1 / 600)
    xs = np.array([trike_x(t) for t in ts])
    ks = np.sign(np.array([trike_k(t) for t in ts]) + 1e-9)
    dx = np.diff(xs, prepend=xs[0]) * ks
    out = []
    for r, period in ((P.FRONT_R, 180.0), (P.REAR_R, 72.0)):
        cum = np.cumsum(dx) / r * 180 / math.pi
        net = cum[-1] % period
        corr = -net if net < period / 2 else period - net
        ramp = np.clip((ts - (T_TURN1 + 0.1)) / (T_RIDE1 - T_TURN1 - 0.3), 0, 1)
        out.append(cum + corr * ramp)
    return ts, out[0], out[1]


_TS, _ROLL_F, _ROLL_R = _wheel_rolls()


def rolls(t):
    rock = 22 * math.sin(2 * math.pi * t / 1.0) * (1 - ease_in_out(seg(t, 1.0, 1.5))) if t < 1.5 else 0.0
    rf = float(np.interp(t, _TS, _ROLL_F)) + rock
    rr = float(np.interp(t, _TS, _ROLL_R)) + rock * P.FRONT_R / P.REAR_R
    return rf, rr


# ---------------------------------------------------------------- Snip
def snip_base(st):
    return st["gy"] - P.SEAT_H - st["lift"]


def aim(ch, st, base, side, target, ref):
    sh = ch.shoulder_pt(st["x"], base, side, st["hop"], st["lean"], st["sq"])
    a = math.degrees(math.atan2(target[0] - sh[0], target[1] - sh[1])) - st["lean"]
    return near(a, ref)


def head_pivot(st):
    return SNIP.head_pivot(st["x"], snip_base(st), st["hop"], st["lean"], st["sq"], st["head_dy"])


def ear_tips(st):
    hx, hy = head_pivot(st)
    ha = st["lean"] + st["tilt"]
    tips = []
    for (ox, oy), tilt, extra in zip(SNIP_EAR_BASE, SNIP_EAR_TILT, st["ears"]):
        ex, ey = rot(ox * 1.15, oy * 1.15, ha)
        vx, vy = rot(0, -EAR_L * st["ear_stretch"], ha + tilt + extra)
        tips.append((hx + ex + vx, hy + ey + vy))
    return tips


def chin(st):
    hx, hy = head_pivot(st)
    vx, vy = rot(0, 24, st["lean"] + st["tilt"])
    return hx + vx, hy + vy


def head_top(st):
    hx, hy = head_pivot(st)
    vx, vy = rot(0, -262, st["lean"] + st["tilt"])
    return hx + vx, hy + vy


def ear_squash(t, t_land, t_boing):
    """Ears squashed by the helmet, then a springy BOING."""
    if t < t_land:
        return 1.0
    if t < t_boing:
        return lerp(1.0, 0.8, ease_out(seg(t, t_land, t_boing)))
    if t < t_boing + 0.07:
        return lerp(0.8, 1.25, ease_out(seg(t, t_boing, t_boing + 0.07)))
    return 1.0 + 0.25 * math.exp(-7 * (t - t_boing - 0.07)) * math.cos(2 * math.pi * 4 * (t - t_boing - 0.07))


def snip_state(t):
    if frozen(t):
        return snip_state(2.4999)
    lift, pitch = trike_lift(t)
    s = dict(x=trike_x(t), gy=trike_gy(t), k=trike_k(t), lift=lift, pitch=pitch, hop=0.0, sq=1.0, lean=0.0,
             tilt=0.0, arm_l=None, arm_r=None, eyes="normal", mouth="w", look=(0, 0), head_dy=0.0,
             ears=[0.0, 0.0], ear_stretch=1.0, frizz=0.0, seated=1.0, chin_paws=0.0)
    idle_ear = 2.0 * math.sin(2 * math.pi * t / 3.0)
    worn = T_ABOVE <= t < T_POP + 0.15

    if t < 1.0 or t >= T_BACK1:       # HOOK (and the loop back into it): bouncing on the seat, ready to ride
        s.update(eyes="sparkle", mouth="grin", look=(8, -3))
        if t < 1.0:
            s["hop"] = 12 * abs(math.sin(2 * math.pi * t / 0.5))
            e = 5 * math.sin(2 * math.pi * t / 0.5)
            s["ears"] = [e, -e]
        else:
            k = ease_in_out(seg(t, T_BACK1, 17.8))
            s["look"] = (8, -3) if k > 0.5 else (6, 2)
            if t < 17.75:
                s.update(eyes="happy", mouth="grin")
    elif t < 2.5:                     # DESIRE: the shiny trike, the path ahead; ring-ring!
        s.update(eyes="sparkle", mouth="grin", look=(10, 0), lean=-4 * ease_out(seg(t, 1.0, 1.4)))
        e = spring(t, 1.0, 10, 4.0, 3.0) + spring(t, 1.6, 8, 5.0, 4.0)
        s["ears"] = [e, -e]
        s["head_dy"] = 6 * math.sin(math.pi * seg(t, 1.55, 1.75))
    elif t < T_HIT:                   # (after the freeze) pedal off bare-headed: whee!
        k = ease_in_out(seg(t, T_GO, T_GO + 0.25))
        s.update(eyes="sparkle", mouth="grin", look=(10, 0), lean=lerp(-4, -10, k))
        s["ears"] = [14 * k, 14 * k]
    elif t < T_STOP:                  # BUMP! boing up (ears poke the tree) and back down onto the seat
        h, sq = hop_curve(t, T_HOP0, T_HOP1, 1, 175)
        s.update(hop=h, sq=sq, eyes="wide", mouth="O", look=(0, -6), lean=lerp(-10, 0, ease_out(seg(t, T_HIT, 5.2))))
        up = math.sin(math.pi * seg(t, T_HOP0, T_HOP1))
        s["arm_l"], s["arm_r"] = lerp(-20, -150, up), lerp(20, 150, up)
        s["seated"] = 1 - min(1.0, h / 30)
        s["ear_stretch"] = 1 + 0.18 * up
        s["ears"] = [-8 * up, 8 * up]
        if t >= T_HOP1:
            s.update(eyes="closed", mouth="wobble")
            e = spring(t, T_HOP1, 12, 5, 4)
            s["ears"] = [e, -e]
    elif t < T_CR1:                   # a leaf floats down... lands on the bare head. Oh!
        s.update(eyes="wide", mouth="o", look=(-2, -10))
        if t >= T_LEAF1:
            s["head_dy"] = 8 * math.sin(math.pi * seg(t, T_LEAF1, T_LEAF1 + 0.2))
            droop = 16 * ease_out(seg(t, T_LEAF1, T_LEAF1 + 0.3))
            s.update(eyes="worried", mouth="wobble", ears=[droop, -droop])
            if t >= 6.45:             # ...and looks at the helmet on its hook
                s.update(eyes="wide", mouth="o", look=(10, 6))
    elif t < TOSS[0][0]:              # Crinkle arrives and takes the helmet
        s.update(eyes="normal", mouth="w", look=(10, 2))
        droop = 16 * (1 - ease_in_out(seg(t, T_CR1, 7.2)))
        s["ears"] = [droop, -droop]
        if T_LEAF_OFF <= t < T_LEAF_OFF + 0.3:   # shake the leaf off
            s["tilt"] = 7 * math.sin(2 * math.pi * 3 * (t - T_LEAF_OFF)) * (1 - seg(t, T_LEAF_OFF, T_LEAF_OFF + 0.3))
    elif t < T_CALL0:                 # the ear gag: boing, boing!
        s.update(eyes="wide", mouth="o", look=(0, -10))
        for (t0, t_land, t_boing, t_back) in TOSS:
            if t0 <= t < t_back + 0.1:
                s["ear_stretch"] = ear_squash(t, t_land, t_boing)
                if t_land <= t < t_boing:
                    s.update(eyes="closed", mouth="wobble")
                    s["head_dy"] = 10 * ease_out(seg(t, t_land, t_boing))
                elif t >= t_boing:
                    s.update(eyes="wide", mouth="O" if t < t_boing + 0.25 else "o", look=(8, -4))
                    s["head_dy"] = 10 * (1 - ease_out(seg(t, t_boing, t_boing + 0.12)))
                    e = spring(t, t_boing, 10, 6, 4)
                    s["ears"] = [e, -e]
        if t >= TOSS[1][3] - 0.05:
            s.update(eyes="worried", mouth="wobble", look=(9, 0), tilt=8 * ease_out(seg(t, 8.95, 9.05)))
    elif t < T_TOSS3:                 # Crinkle shows the ear holes -- aha!
        s.update(eyes="normal", mouth="o", look=(8, -9), tilt=8 * (1 - ease_in_out(seg(t, T_CALL0, 9.3))))
        if t >= T_CALL_EARS:
            s.update(eyes="sparkle", mouth="grin")
            e = spring(t, T_CALL_EARS, 12, 5, 3.5)
            s["ears"] = [e, -e]
            s["head_dy"] = 10 * math.sin(math.pi * seg(t, 9.55, 9.75))
    elif t < T_RIDE0:                 # DO IT RIGHT: on (1), click (2), wiggle test (3)
        s.update(eyes="happy" if t < T_TOSS3 + 0.1 else "normal", mouth="grin", look=(0, -9))
        if t >= T_ON:
            h, sq = hop_curve(t, T_ON, T_ON + 0.01, 1, 0)
            s.update(eyes="happy", mouth="grin", look=(0, 0))
            s["sq"] = 1 - 0.06 * math.sin(math.pi * seg(t, T_ON, T_ON + 0.15))
        if 10.6 <= t < 11.25:         # paws to the chin: CLICK
            k = ease_in_out(seg(t, 10.6, 10.84)) * (1 - ease_in_out(seg(t, 11.0, 11.25)))
            s["chin_paws"] = k
            s.update(eyes="normal", mouth="o", look=(0, 9))
            if t >= T_CLICK:
                s.update(eyes="happy", mouth="grin")
        if T_WIG0 <= t < T_WIG1:      # wiggle test: shake shake, it stays snug
            p = seg(t, T_WIG0, T_WIG1)
            s["tilt"] = 13 * math.sin(2 * math.pi * 2.5 * p) * math.sin(math.pi * p)
            s.update(eyes="closed", mouth="grin")
        if t >= T_WIG1:
            s.update(eyes="happy", mouth="grin")
            h, sq = hop_curve(t, T_CHECK, T_CHECK + 0.3, 1, 18)
            s["hop"], s["sq"] = h, sq
    elif t < T_RIDE1:                 # the happy, slow ride round the tree
        s.update(eyes="happy", mouth="grin", look=(9 * (1 if s["k"] >= 0 else -1), 0), lean=-4 * s["k"])
        e = 3 * math.sin(2 * math.pi * t / 0.6)
        s["ears"] = [e + 3 * s["k"], -e + 3 * s["k"]]
        if T_RIDE1 - 0.6 <= t:
            s["head_dy"] = 6 * math.sin(math.pi * seg(t, T_RIDE1 - 0.5, T_RIDE1 - 0.2))
    elif t < 16.2:                    # PAW-BUMP
        s.update(eyes="happy", mouth="grin", look=(9, 0))
        h, sq = hop_curve(t, 14.6, 14.9, 1, 14)
        s["hop"], s["sq"] = h, sq
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["_bump"] = (wind, swing)
        s["lean"] = -4 * ease_in_out(seg(t, 14.95, 15.25)) * (1 - ease_in_out(seg(t, 15.95, 16.2)))
        e = spring(t, 15.45, 6, 5.0, 3.5)
        s["ears"] = [e, -e]
    else:                             # loop: unclick, BOING the helmet back onto its hook, roll back
        s.update(eyes="normal", mouth="w", look=(0, 9))
        k = ease_in_out(seg(t, 16.2, 16.38)) * (1 - ease_in_out(seg(t, T_UNCLICK + 0.02, T_UNCLICK + 0.2)))
        s["chin_paws"] = k
        if t >= T_UNCLICK:
            s.update(eyes="happy", mouth="grin", look=(6, -8))
        if T_POP <= t < T_HANG + 0.3:
            s["ear_stretch"] = 1 + 0.22 * math.sin(math.pi * seg(t, T_POP, T_POP + 0.16)) \
                + 0.06 * math.exp(-6 * max(0, t - T_POP - 0.16)) * math.sin(2 * math.pi * 4 * max(0, t - T_POP - 0.16))
            s.update(eyes="wide" if t < T_POP + 0.3 else "happy", mouth="O" if t < T_POP + 0.3 else "grin",
                     look=(9, -4) if t < T_HANG else (9, 4))
        if t >= T_BACK0:
            s.update(eyes="happy", mouth="grin", look=(9, 4))

    if worn:                          # keep the ears in the holes while the helmet is on
        s["ears"] = [max(-3.0, min(3.0, e)) for e in s["ears"]]
        s["ears"][0] += 0.6 * idle_ear
        s["ears"][1] -= 0.6 * idle_ear
    else:
        s["ears"][0] += idle_ear
        s["ears"][1] -= idle_ear
    if s["hop"] == 0:
        s["sq"] *= breath(t)

    # arms: on the handlebar grips unless doing something else
    base = snip_base(s)
    grips = TRIKE.grip_pts(s["x"], s["gy"], s["k"], s["lift"], s["pitch"])
    gl = min(grips, key=lambda p: p[0])
    gr = max(grips, key=lambda p: p[0])
    on_l = aim(SNIP, s, base, "l", (gl[0], gl[1] + 4), 0)
    on_r = aim(SNIP, s, base, "r", (gr[0], gr[1] + 4), 0)
    if s["arm_l"] is None:
        s["arm_l"] = on_l
    if s["arm_r"] is None:
        s["arm_r"] = on_r
    if s["chin_paws"] > 0:
        c = chin(s)
        s["arm_l"] = lerp(on_l, aim(SNIP, s, base, "l", (c[0] - 14, c[1] + 6), on_l), s["chin_paws"])
        s["arm_r"] = lerp(on_r, aim(SNIP, s, base, "r", (c[0] + 14, c[1] + 6), on_r), s["chin_paws"])
    if "_bump" in s:
        wind, swing = s["_bump"]
        up = aim(SNIP, s, base, "r", MEET, on_r)
        s["arm_r"] = lerp(lerp(on_r, on_r - 15, wind), up, swing) if t < 16.0 else \
            lerp(up, on_r, ease_in_out(seg(t, 16.0, 16.2)))
    return s


# ---------------------------------------------------------------- Crinkle
def cr_tip(st, side):
    arm = st["arm_l"] if side == "l" else st["arm_r"]
    return CR.paw_tip(st["x"], G, side, arm, st["hop"], st["lean"], st["sq"])


def cr_aim(st, side, target, ref):
    sh = CR.shoulder_pt(st["x"], G, side, st["hop"], st["lean"], st["sq"])
    a = math.degrees(math.atan2(target[0] - sh[0], target[1] - sh[1])) - st["lean"]
    return near(a, ref)


def carry_arms(st):
    return (cr_aim(st, "l", (CARRY_RIM[0] - 78, CARRY_RIM[1] - 30), 40),
            cr_aim(st, "r", (CARRY_RIM[0] + 78, CARRY_RIM[1] - 30), -40))


def crinkle_state(t):
    if frozen(t):
        return crinkle_state(2.4999)
    s = dict(x=CR_X, hop=0.0, sq=1.0, lean=0.0, arm_l=CR_REST_L, arm_r=2.0, eyes="normal", mouth="smile",
             look=(0, 0), head_dy=0.0)
    if t < T_CR0 or t >= 16.95:
        s["x"] = 1600
        return s
    carry_l, carry_r = carry_arms(s)
    if t < T_CR1:                     # walks in along the path
        bob, sway = walk_bob(t, T_CR0, T_CR1, 4)
        s.update(x=lerp(1400, CR_X, ease_out(seg(t, T_CR0, T_CR1))), hop=bob, lean=sway, look=(-9, 0))
    elif t < TOSS[0][0]:              # takes the helmet off the hook
        s.update(look=(-9, -4), eyes="normal", mouth="smile")
        grab = cr_aim(s, "l", (P.HOOK[0] - 40, 1200), 200)
        reach = ease_in_out(seg(t, T_CR1 - 0.05, T_GRAB))
        s["arm_l"] = lerp(CR_REST_L, grab, reach)
        if t >= T_GRAB:
            k = ease_in_out(seg(t, T_GRAB, T_TAKE))
            s["arm_l"] = lerp(grab, carry_l, k)
            s["arm_r"] = lerp(2, carry_r, k)
            s["look"] = (-9, 2)
    elif t < T_CALL0:                 # tosses it up like a ring toss... boing! catches it
        s.update(arm_l=carry_l, arm_r=carry_r, look=(-8, -9), mouth="smile")
        for (t0, t_land, t_boing, t_back) in TOSS:
            if t0 <= t < t_back + 0.1:
                up = ease_out(seg(t, t0, t0 + 0.12)) * (1 - ease_in_out(seg(t, t0 + 0.2, t_land)))
                catch = ease_in_out(seg(t, t_back - 0.2, t_back))
                s["arm_l"] = lerp(carry_l, 170, up)
                s["arm_r"] = lerp(carry_r, -170 + 360, up) if up > 0 else carry_r
                if t >= t_land:
                    s["arm_l"] = lerp(lerp(carry_l, 230, 1 - catch), carry_l, catch)
                    s["arm_r"] = lerp(lerp(carry_r, 130, 1 - catch), carry_r, catch)
                if t >= t_boing:
                    s.update(eyes="wide", mouth="o", look=(-6, -10) if t < t_back - 0.2 else (-4, 4))
                if t_back <= t:
                    h, sq = hop_curve(t, t_back, t_back + 0.2, 1, 12)
                    s["hop"], s["sq"] = h, sq
        if t >= TOSS[1][3]:
            s.update(eyes="worried", mouth="o", look=(-4, 6))
    elif t < T_TOSS3:                 # idea! shows the ear holes
        s.update(arm_l=carry_l, arm_r=carry_r, eyes="happy" if t < 9.35 else "normal", mouth="grin",
                 look=(-2, -10) if t < 9.6 else (-9, -4))
        s["head_dy"] = 10 * math.sin(math.pi * seg(t, T_CALL0, T_CALL0 + 0.25))
        h, sq = hop_curve(t, T_CALL0, T_CALL0 + 0.28, 1, 20)
        s["hop"], s["sq"] = h, sq
    elif t < T_RIDE0:                 # gentle toss: on (1); counts click (2) and wiggle (3)
        s.update(arm_l=carry_l, arm_r=carry_r, look=(-9, -6), mouth="smile")
        up = ease_out(seg(t, T_TOSS3, T_TOSS3 + 0.12)) * (1 - ease_in_out(seg(t, T_TOSS3 + 0.3, T_ON + 0.1)))
        s["arm_l"] = lerp(CR_REST_L if t >= T_TOSS3 else carry_l, 175, up) if t >= T_TOSS3 else carry_l
        s["arm_r"] = lerp(2, 185, up) if t >= T_TOSS3 else carry_r
        if t >= T_TOSS3 + 0.3:
            k = ease_in_out(seg(t, T_TOSS3 + 0.3, T_ON + 0.1))
            s["arm_l"] = lerp(175, CR_REST_L, k)
            s["arm_r"] = lerp(185, 2, k)
        for c in COUNTS:
            s["head_dy"] += 10 * math.sin(math.pi * seg(t, c, c + 0.28))
            if 0 <= t - c < 0.28:
                s["mouth"] = "o"
        if t >= T_CHECK:
            h, sq = hop_curve(t, T_CHECK, T_CHECK + 0.3, 1, 26)
            s.update(hop=h, sq=sq, eyes="happy", mouth="grin")
            s["arm_r"] = lerp(2, 150, ease_out_back(seg(t, T_CHECK, T_CHECK + 0.2)))
    elif t < T_RIDE1:                 # cheers while Snip rides round the tree
        sn_x = trike_x(t)
        s.update(eyes="happy", mouth="grin", look=(-9, -2) if sn_x < CR_X - 200 else (-6, 2))
        s["arm_r"] = 150 + 18 * math.sin((t - T_RIDE0) * 12)
        s["arm_l"] = lerp(CR_REST_L, 200, ease_out(seg(t, 13.0, 13.25))) * 1.0
        s["arm_l"] = near(s["arm_l"] + 14 * math.sin((t - 13.0) * 12) * seg(t, 13.0, 13.25), 200)
        if t >= T_RIDE1 - 0.6:
            k = ease_in_out(seg(t, T_RIDE1 - 0.6, T_RIDE1 - 0.2))
            s["arm_r"] = lerp(s["arm_r"], 2, k)
            s["arm_l"] = lerp(s["arm_l"], CR_REST_L, k)
        h, sq = hop_curve(t, 13.6, 13.92, 1, 24)
        s["hop"], s["sq"] = h, sq
    elif t < 16.2:                    # PAW-BUMP
        s.update(eyes="happy", mouth="grin", look=(-8, -2),
                 x=lerp(CR_X, CR_BUMP_X, ease_in_out(seg(t, 14.6, 14.9))))
        h, sq = hop_curve(t, 14.6, 14.9, 1, 14)
        if t >= 15.0:
            h = 30 * ease_in_out(seg(t, 15.0, 15.3)) * (1 - ease_in_out(seg(t, 15.95, 16.2)))
            sq = 1.0
        s["hop"], s["sq"] = h, sq
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        up = cr_aim(s, "l", MEET, 200)
        s["arm_l"] = lerp(lerp(CR_REST_L, 360, wind), up, swing)
        if t >= 16.0:
            s["arm_l"] = lerp(up, CR_REST_L, ease_in_out(seg(t, 16.0, 16.2)))
    else:                             # waves bye and hops away
        h, sq = hop_curve(t, 16.25, 16.95, 2, 40)
        s.update(x=lerp(CR_BUMP_X, 1450, ease_in_out(seg(t, 16.25, 16.95))), hop=h, sq=sq, eyes="happy", mouth="grin",
                 lean=-6)
        s["arm_r"] = 140 + 22 * math.sin((t - 16.2) * 16)
    if s["hop"] == 0:
        s["sq"] *= breath(t + 0.7, 2.25, 0.01)
    return s


# ---------------------------------------------------------------- the helmet
def carry_pivot():
    return (CARRY_RIM[0], CARRY_RIM[1] + P.RIM_DY)


def hang_pivot(angle=0.0):
    a = math.radians(angle)
    return (P.HOOK[0] - P.HANG_DY * math.sin(a), P.HOOK[1] - P.HANG_DY * math.cos(a))


def tips_pivot(sn):
    """Helmet sitting on top of the ear tips (rim a little below the tips)."""
    (lx, ly), (rx, ry) = ear_tips(sn)
    return ((lx + rx) / 2, (ly + ry) / 2 + 40 + P.RIM_DY)


def worn_pivot(sn, u=0.0):
    hx, hy = head_pivot(sn)
    vx, vy = rot(0, -u, sn["lean"] + sn["tilt"])
    return hx + vx, hy + vy


def u_above(sn):
    """How far up the head axis the helmet must be so its rim clears the ear tips."""
    hx, hy = head_pivot(sn)
    tip_y = min(p[1] for p in ear_tips(sn))
    return (hy - P.RIM_DY) - (tip_y - 24)


def helmet_state(t, sn):
    """-> (mode, pivot, angle, straps, scale). mode: hang | whole | worn."""
    if frozen(t):
        t = 2.4999
    if t < T_GRAB:
        sw = 0.0
        if T_CR1 - 0.05 <= t:
            sw = 4 * math.sin(2 * math.pi * 3 * (t - T_CR1))
        return ("hang", hang_pivot(sw), sw, None, 1.0)
    if t < T_TAKE:                    # pops off the hook into Crinkle's arms
        k = ease_in_out(seg(t, T_GRAB, T_TAKE))
        p = arc(hang_pivot(), carry_pivot(), k, 70)
        return ("whole", p, 6 * math.sin(math.pi * k), "hang", 1 + 0.08 * math.sin(math.pi * k))
    if t < TOSS[0][0]:
        return ("whole", carry_pivot(), 0.0, "hang", 1.0)
    for i, (t0, t_land, t_boing, t_back) in enumerate(TOSS):
        if t0 <= t < t_land:
            k = seg(t, t0, t_land)
            return ("whole", arc(carry_pivot(), tips_pivot(snip_state(t_land)), ease_out(k), 220), -14 * k, "hang", 1)
        if t_land <= t < t_boing:
            wob = 5 * math.sin(2 * math.pi * 6 * (t - t_land))
            return ("whole", tips_pivot(sn), wob, "hang", 1.0)
        if t_boing <= t < t_back:
            k = seg(t, t_boing, t_back)
            src = tips_pivot(snip_state(t_boing))
            h = 330 if i == 0 else 470
            spin = -24 * math.sin(math.pi * k) if i == 0 else -360 * ease_in_out(k)
            return ("whole", arc(src, carry_pivot(), k, h), spin, "hang", 1.0)
        if t_back <= t < (TOSS[i + 1][0] if i == 0 else T_TOSS3):
            return ("whole", carry_pivot(), 0.0, "hang", 1.0)
    if t < T_ABOVE:                   # gentle toss to just above the ears, lined up
        k = ease_out(seg(t, T_TOSS3, T_ABOVE))
        sn_a = snip_state(T_ABOVE)
        dst = worn_pivot(sn_a, u_above(sn_a))
        return ("whole", arc(carry_pivot(), dst, k, 160), 0.0, "hang", 1.0)
    if t < T_ON:                      # ...and slides down the ears through the holes (1)
        k = ease_in(seg(t, T_ABOVE, T_ON))
        u = lerp(u_above(snip_state(T_ABOVE)), 0, k)
        return ("worn", worn_pivot(sn, u), sn["lean"] + sn["tilt"], "hang", 1.0)
    if t < T_POP:
        straps = "buckled" if T_CLICK <= t < T_UNCLICK else "open"
        return ("worn", worn_pivot(sn), sn["lean"] + sn["tilt"], straps, 1.0)
    t_off = T_POP + 0.2
    if t < t_off:                     # the ears BOING it up off the head...
        k = ease_out(seg(t, T_POP, t_off))
        return ("worn", worn_pivot(sn, u_above(sn) * k), sn["lean"] + sn["tilt"], "hang", 1.0)
    if t < T_HANG:                    # ...and it flies back onto its hook
        k = ease_in_out(seg(t, t_off, T_HANG))
        src = worn_pivot(snip_state(t_off), u_above(snip_state(t_off)))
        return ("whole", arc(src, hang_pivot(), k, 160), 0.0, "hang", 1.0)
    dt = t - T_HANG
    sw = -9 * math.exp(-4 * dt) * math.sin(2 * math.pi * 1.6 * dt) * (1 - ease_in_out(seg(t, 17.5, 17.95)))
    return ("hang", hang_pivot(sw), sw, None, 1.0)


def draw_worn(f, sn, piv, ang, straps):
    """Back of the helmet, the ears (through the holes), the front of the helmet, straps."""
    place(f, HEL.dome, piv, angle=ang)
    hx, hy = head_pivot(sn)
    ha = sn["lean"] + sn["tilt"]
    for (ox, oy), tilt, extra in zip(SNIP_EAR_BASE, SNIP_EAR_TILT, sn["ears"]):
        ex, ey = rot(ox * 1.15, oy * 1.15, ha)
        place(f, SNIP.ear, (hx + ex, hy + ey), angle=ha + tilt + extra, sy=sn["ear_stretch"])
    place(f, HEL.front, piv, angle=ang)
    spr = {"buckled": HEL.straps_buckled, "open": HEL.straps_open, "hang": HEL.straps_hang}[straps]
    place(f, spr, piv, angle=ang)


# ---------------------------------------------------------------- leaf
def leaf_pos(t, sn):
    """-> (pos, angle, alpha) or None"""
    if frozen(t) or t < T_LEAF0 or t >= 7.9:
        return None
    if t < T_LEAF1:
        p = seg(t, T_LEAF0, T_LEAF1)
        top = head_top(snip_state(T_LEAF1))
        x = lerp(500, top[0], p) + 60 * math.sin(2 * math.pi * 1.6 * p) * (1 - p)
        y = lerp(500, top[1], ease_in_out(p))
        return (x, y), 40 * math.sin(2 * math.pi * 1.6 * p) * (1 - p), 1.0
    if t < T_LEAF_OFF:
        top = head_top(sn)
        return top, sn["tilt"] + 4 * math.sin(t * 6), 1.0
    p = seg(t, T_LEAF_OFF, 7.6)
    top = head_top(snip_state(T_LEAF_OFF))
    x = top[0] + 140 * p + 40 * math.sin(2 * math.pi * 1.4 * p)
    y = lerp(top[1], G - 10, ease_in_out(p))
    return (x, y), 50 * math.sin(2 * math.pi * 1.4 * p), 1 - ease_in_out(seg(t, 7.6, 7.9))


# ---------------------------------------------------------------- frame
def draw_snip(f, sn, t, frz):
    base = snip_base(sn)
    rf, rr = rolls(t if not frz else 2.4999)
    x, gy, k = sn["x"], sn["gy"], sn["k"]
    TRIKE.draw_back(f, x, gy, k, rf, sn["lift"], sn["pitch"], rr)
    SNIP.draw(f, x, base, hop=sn["hop"], lean=sn["lean"], head_tilt=sn["tilt"], arm_l=sn["arm_l"],
              arm_r=sn["arm_r"], eyes=sn["eyes"], mouth=sn["mouth"], look=sn["look"], squash=sn["sq"],
              head_dy=sn["head_dy"], blink=blinking(t, SNIP_BLINKS) and not frz, ears=tuple(sn["ears"]),
              ear_stretch=sn["ear_stretch"], frizz=sn["frizz"])
    TRIKE.draw_front(f, x, gy, k, rf, sn["hop"], sn["lift"], sn["pitch"], t if not frz else 2.4999,
                     sn["seated"], rr)
    snip_arms(f, sn)


def snip_arms(f, sn):
    base = snip_base(sn)
    for side in ("l", "r"):
        spr = SNIP.arm_l if side == "l" else SNIP.arm_r
        place(f, spr, SNIP.shoulder_pt(sn["x"], base, side, sn["hop"], sn["lean"], sn["sq"]),
              angle=(sn["arm_l"] if side == "l" else sn["arm_r"]) + sn["lean"])


def render_frame(t):
    f = BG.copy()
    frz = frozen(t)
    tt = 2.4999 if frz else t
    sn = snip_state(t)
    cr = crinkle_state(t)
    hm = helmet_state(t, sn)

    # sky: sun and drifting clouds (periodic so the loop closes)
    place(f, SUN, (930, 250), angle=30 * tt / DUR)
    for spr, x, y, ph in CLOUDS:
        place(f, spr, (x + 26 * math.sin(2 * math.pi * tt / DUR + ph), y))
    # the apple tree's leaves (shake when Snip's ears poke them)
    shake = 0.0
    if T_APEX - 0.05 <= tt < T_APEX + 0.9:
        shake = 9 * math.exp(-5 * max(0.0, tt - T_APEX)) * math.sin(2 * math.pi * 7 * (tt - T_APEX)) \
            * min(1.0, (tt - T_APEX + 0.05) / 0.08)
    place(f, CANOPY, (CANOPY_AT[0] + shake + 4 * math.sin(2 * math.pi * tt / 6.0), CANOPY_AT[1] + 2 * math.sin(4 * math.pi * tt / 6.0)))
    place(f, BUMP, (P.BUMP_X, G + 4))

    # the helmet on its hook (behind everyone), glowing when Snip looks at it
    mode, piv, ang, straps, sc = hm
    if mode == "hang":
        if 6.45 <= tt < 7.0:
            g = math.sin(math.pi * seg(tt, 6.45, 7.0))
            place(f, GLOW, (piv[0], piv[1] - P.RIM_DY - 60), alpha=g * (0.8 + 0.2 * math.sin(tt * 20)),
                  shadow=False)
        P.place_helmet_hanging(f, HEL, ang)
    place(f, HOOK_SPR, P.HOOK)

    draw_snip(f, sn, tt, frz)

    # the leaf (on Snip's bare head)
    lp = leaf_pos(t, sn)
    if lp is not None:
        place(f, LEAF, lp[0], angle=lp[1], alpha=lp[2], scale=1.7)

    # helmet worn (ears through the holes) / flying / on the ear tips
    if mode == "worn":
        draw_worn(f, sn, piv, ang, straps)
        if sn["chin_paws"] > 0:
            snip_arms(f, sn)
    carried = mode == "whole" and (T_GRAB <= tt < TOSS[0][0] + 0.02 or abs(piv[0] - carry_pivot()[0]) < 1
                                   and abs(piv[1] - carry_pivot()[1]) < 1)
    if cr["x"] < 1500:
        CR.draw(f, cr["x"], G, hop=cr["hop"], lean=cr["lean"], arm_l=cr["arm_l"], arm_r=cr["arm_r"],
                eyes=cr["eyes"], mouth=cr["mouth"], look=cr["look"], squash=cr["sq"], head_dy=cr["head_dy"],
                blink=blinking(t, CR_BLINKS) and not frz)
    if mode == "whole":               # flying / on the ear tips / in Crinkle's arms (in front of him)
        P.place_helmet_whole(f, HEL, piv, ang, sc)
    if carried:                       # in Crinkle's arms: paws over its rim
        for side in ("l", "r"):
            spr = CR.arm_l if side == "l" else CR.arm_r
            place(f, spr, CR.shoulder_pt(cr["x"], G, side, cr["hop"], cr["lean"], cr["sq"]),
                  angle=(cr["arm_l"] if side == "l" else cr["arm_r"]) + cr["lean"])

    # the apple tree trunk in front (the path goes round behind it)
    place(f, TRUNK, (20, 1600))

    # ---- effects
    if tt < 2.5:                      # the shiny trike glints; ring-ring
        for t0, dx, dy, s0 in ((0.25, 30, -170, 0.9), (1.15, -120, -90, 0.8), (1.9, 150, -118, 0.7)):
            if t0 <= tt < t0 + 0.5:
                k = math.sin(math.pi * seg(tt, t0, t0 + 0.5))
                place(f, GLINT, (sn["x"] + dx, G + dy), scale=s0 * k, angle=(tt - t0) * 140)
        for t0 in (0.55, 1.55):
            if t0 <= tt < t0 + 0.4:
                k = math.sin(math.pi * seg(tt, t0, t0 + 0.4))
                bp = TRIKE.pt(sn["x"], G, 1, 60, P.BAR_Y - 40)
                place(f, BOING, (bp[0], bp[1] - 10), scale=0.45 * k, alpha=k)
    if T_HIT <= tt < T_HIT + 0.45:    # BOING lines at the bump
        k = math.sin(math.pi * seg(tt, T_HIT, T_HIT + 0.45))
        place(f, BOING, (sn["x"] + 150, G - 40), scale=0.9 * k, alpha=k)
    for (t0, t_land, t_boing, t_back) in TOSS:
        if t_boing <= tt < t_boing + 0.35:
            k = math.sin(math.pi * seg(tt, t_boing, t_boing + 0.35))
            tp = tips_pivot(snip_state(t_boing))
            place(f, BOING, (tp[0], tp[1] - P.RIM_DY - 140), scale=1.1 * k, alpha=k)
    if T_POP <= tt < T_POP + 0.35:
        k = math.sin(math.pi * seg(tt, T_POP, T_POP + 0.35))
        hx, hy = head_pivot(sn)
        place(f, BOING, (hx, hy - 560), scale=0.9 * k, alpha=k)

    # Crinkle's idea: the ear holes
    if T_CALL0 <= tt < T_CALL1:
        k = pop_scale(tt, T_CALL0, 0.3) * (1 - ease_in_out(seg(tt, T_CALL1 - 0.18, T_CALL1)))
        e = ease_out(seg(tt, T_CALL_EARS - 0.15, T_CALL_EARS + 0.1))
        spr = CALLOUTS[int(round(e * (len(CALLOUTS) - 1)))]
        if T_CALL_EARS <= tt < T_CALL_EARS + 0.15:
            k *= 1 + 0.08 * math.sin(math.pi * seg(tt, T_CALL_EARS, T_CALL_EARS + 0.15))
        place(f, spr, (CR_X - 10, 800), scale=0.95 * k * (1 + 0.03 * math.sin(tt * 10)))

    # counting numerals 1-2-3, the buckle click, check
    for i, c in enumerate(COUNTS):
        if c <= tt < c + 0.6:
            out = 1 - ease_in_out(seg(tt, c + 0.42, c + 0.6))
            place(f, NUMS[i], (CR_X, 650), scale=pop_scale(tt, c, 0.25) * out, angle=-6 + 4 * math.sin(tt * 6))
    if T_CLICK <= tt < T_CLICK + 0.4:
        k = pop_scale(tt, T_CLICK, 0.15) * (1 - ease_in_out(seg(tt, T_CLICK + 0.25, T_CLICK + 0.4)))
        c = chin(sn)
        place(f, CLICK, (c[0], c[1] + 30), scale=0.95 * k, angle=(tt - T_CLICK) * 90)
    if T_WIG0 <= tt < T_WIG1:         # wiggle test: little motion marks either side of the helmet
        k = math.sin(math.pi * seg(tt, T_WIG0, T_WIG1))
        hx, hy = head_pivot(sn)
        for side in (-1, 1):
            place(f, BOING, (hx + side * 245, hy - 190), angle=side * 90, scale=0.8 * k, alpha=k)
    if T_CHECK <= tt < T_CHECK + 0.6:
        place(f, CHECK, (CR_X, 650), scale=pop_scale(tt, T_CHECK, 0.25) * (1 - ease_in_out(seg(tt, T_CHECK + 0.4,
                                                                                              T_CHECK + 0.6))))
    for i, (t0, x, y) in enumerate(HEART_PLAN):
        if t0 <= tt < 14.6:
            p = seg(tt, t0, 14.6)
            place(f, HEARTS[i], (x + 10 * math.sin(tt * 3 + i), y - 160 * p), scale=pop_scale(tt, t0, 0.25),
                  alpha=1 - ease_in_out(seg(tt, 14.2, 14.6)), angle=10 * math.sin(tt * 2.5 + i))

    # paw-bump: both touching paws in front, sparkle
    if 14.95 <= tt < 16.1:
        base = snip_base(sn)
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], base, "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])
        place(f, CR.arm_l, CR.shoulder_pt(cr["x"], G, "l", cr["hop"], cr["lean"], cr["sq"]),
              angle=cr["arm_l"] + cr["lean"])
    if 15.45 <= tt < 16.2:
        a = SNIP.paw_tip(sn["x"], snip_base(sn), "r", sn["arm_r"], sn["hop"], sn["lean"], sn["sq"])
        b = cr_tip(cr, "l")
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 10)
        place(f, SPARKLE, (mid[0] - 10, mid[1] - 70), scale=pop_scale(tt, 15.45, 0.22) * 0.5, angle=(tt - 15.45) * 60,
              alpha=1 - ease_in_out(seg(tt, 15.9, 16.2)))

    out = camera(f, tt)

    # FREEZE: dim + choice bubbles (screen space)
    if 2.5 <= t < 4.6:
        dim = 0.32 * ease_in_out(seg(t, 2.5, 2.8)) * (1 - ease_in_out(seg(t, 4.35, 4.6)))
        if dim > 0.01:
            out.alpha_composite(Image.new("RGBA", out.size, (30, 26, 52, int(255 * dim))))
        gone = 1 - ease_in_out(seg(t, 4.4, 4.55))
        pulse_a = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 2.95) / 1.0))
        pulse_b = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 3.45) / 1.0))
        place(out, BUB_BARE, (290, 430), scale=1.2 * pop_scale(t, 2.55) * gone * (pulse_a if t > 2.95 else 1))
        place(out, BUB_HELMET, (790, 430), scale=1.2 * pop_scale(t, 2.7) * gone * (pulse_b if t > 3.45 else 1))
        place(out, QMARK, (540, 320), scale=pop_scale(t, 2.85, 0.25) * gone, angle=8 * math.sin(t * 4))
    return out


CAM0 = (1.5, 420, 1150)
CAM_KEYS = [
    (0.0,) + CAM0, (0.9,) + CAM0, (2.35, 1.0, 540, 960), (4.6, 1.0, 540, 960),
    (4.9, 1.0, 540, 960), (5.25, 1.06, 500, 900), (5.6, 1.06, 500, 900), (6.15, 1.14, 470, 980),
    (6.4, 1.14, 470, 980), (7.0, 1.0, 540, 960), (14.5, 1.0, 540, 960), (15.2, 1.1, 560, 1060),
    (16.1, 1.1, 560, 1060), (DUR,) + CAM0]


def camera(f, t):
    z, cx, cy = 1.0, 540, 960
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
    if T_HIT <= t < T_HIT + 0.35:     # a little jolt at the bump (eased in and out)
        k = math.sin(math.pi * seg(t, T_HIT, T_HIT + 0.35))
        cx += 4 * k * math.sin(t * 90)
        cy += 4 * k * math.cos(t * 77)
    w, h = scene.W / z, scene.H / z
    left = min(max(cx - w / 2, 0), scene.W - w)
    top = min(max(cy - h / 2, 0), scene.H - h)
    if z < 1.001 and left == 0 and top == 0:
        return f
    return f.resize((scene.W, scene.H), Image.BICUBIC, box=(left, top, left + w, top + h))


# ---------------------------------------------------------------- audio
def build_audio(path):
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    M = A.midi
    # hook + desire: jingle, bouncy seat, ring-ring!
    A.jingle(music, 0.02)
    for tt in (0.12, 0.37, 0.62, 0.87):
        sfx.add(tt, P.squeak_pedal(0.7))
    sfx.add(0.55, P.bell(0.9))
    sfx.add(1.55, P.bell(0.8))
    sfx.add(0.25, A.twinkle(0.5))
    sfx.add(1.2, PK.chirp(0.6))
    for tt, ch, up in ((1.0, "C", False), (1.25, "C", True), (1.5, "F", False), (1.75, "F", True),
                       (2.0, "G", False), (2.25, "G", True)):
        A.strum(music, tt, ch, 0.7, up)
    for tt, m in ((1.0, 48), (1.5, 41), (2.0, 43)):
        music.add(tt, A.bass(M(m), 0.5, 0.7))
    sfx.add(1.15, A.twinkle(0.7))
    sfx.add(2.4, A.pop(0.6))
    # freeze: tick-tock + soft pad
    music.add(2.55, A.pad([M(48), M(55), M(64)], 2.0, 0.25))
    tt, k = 2.75, 0
    while tt < 4.4:
        sfx.add(tt, A.woodblock(k % 2 == 0, 0.8))
        tt += 0.25
        k += 1
    for tt in (2.55, 2.7):
        sfx.add(tt, A.pop(0.7))
    sfx.add(2.85, A.glock(M(91), 0.6, 0.4))
    sfx.add(4.42, A.pop(0.6))
    # pedal off (whee), BUMP boing, rustle, the leaf lands, uh-oh
    sfx.add(T_GO, P.roll(T_HIT - T_GO + 0.1, 0.8))
    for i in range(4):
        sfx.add(T_GO + i * 0.11, P.squeak_pedal(0.8))
    sfx.add(T_GO, PK.slide_whistle(True, 0.4, 0.5))
    sfx.add(T_HIT, A.tap(1.0))
    sfx.add(T_HIT + 0.02, A.boing(1.0, 240))
    sfx.add(T_APEX - 0.05, P.rustle(0.6, 0.8))
    sfx.add(T_HOP1, PK.flump(0.9))
    sfx.add(T_HOP1 + 0.02, A.boing(0.4, 330))
    sfx.add(T_LEAF0 + 0.1, PK.slide_whistle(False, 0.8, 0.3))
    sfx.add(T_LEAF1, A.tap(0.5))
    sfx.add(T_LEAF1 + 0.05, A.glock(M(88), 0.6, 0.35))
    music.add(T_LEAF1 + 0.15, A.wah_down(0.75))
    sfx.add(6.45, A.twinkle(0.5, (96, 100, 103)))
    # Crinkle walks in, takes the helmet off the hook
    for i in range(4):
        sfx.add(T_CR0 + 0.05 + i * 0.14, A.tap(0.35))
    sfx.add(T_GRAB, P.clink(0.6))
    sfx.add(T_GRAB + 0.02, A.pop(0.6))
    for tt, ch in ((6.6, "Am"), (7.1, "F")):
        A.strum(music, tt, ch, 0.5)
        music.add(tt, A.bass(M({"Am": 45, "F": 41}[ch]), 0.5, 0.55))
    # the ear gag: whoosh up, squish, BOING (x2, the second one higher)
    for i, (t0, t_land, t_boing, t_back) in enumerate(TOSS):
        sfx.add(t0, A.whoosh(0.35, 0.7))
        sfx.add(t_land, A.tap(0.6))
        sfx.add(t_land + 0.01, P.squeak_pedal(0.9))
        sfx.add(t_boing, A.boing(1.0, 300 + 60 * i))
        sfx.add(t_boing + 0.03, A.snare_roll(0.12, 0.4))
        if i == 1:
            sfx.add(t_boing + 0.05, PK.slide_whistle(True, 0.4, 0.45))
        sfx.add(t_back, PK.flump(0.6))
        music.add(t0, A.pluck(M(67 + 2 * i), 0.3, 0.6))
        music.add(t_boing, A.pluck(M(72 + 2 * i), 0.3, 0.6))
    A.strum(music, 7.6, "G", 0.5)
    A.strum(music, 8.4, "C", 0.5)
    music.add(8.95, A.pad([M(55), M(59), M(62)], 0.6, 0.3))
    # idea: the ear holes
    sfx.add(T_CALL0, A.chime_up(0.9))
    sfx.add(T_CALL_EARS, A.twinkle(0.7))
    sfx.add(T_CALL_EARS + 0.05, A.boop(0.5))
    for tt, ch in ((T_CALL0, "C"), (9.5, "F")):
        A.strum(music, tt, ch, 0.55)
        music.add(tt, A.bass(M({"C": 48, "F": 41}[ch]), 0.45, 0.6))
    # DO IT RIGHT: on (1) - slide down the ears, plop; click (2); wiggle test (3); check
    sfx.add(T_TOSS3, A.whoosh(0.3, 0.5))
    sfx.add(T_ABOVE, PK.slide_whistle(False, 0.25, 0.55))
    sfx.add(T_ON, PK.flump(0.8))
    sfx.add(T_CLICK, P.click(1.0))
    for i in range(5):
        sfx.add(T_WIG0 + 0.05 + i * 0.12, A.woodblock(i % 2 == 0, 0.35))
    for c, m in zip(COUNTS, (84, 88, 91)):
        sfx.add(c, A.glock(M(m), 1.2, 0.9))
        music.add(c, A.ks_pluck(M(m - 24), 1.0, 0.8))
        music.add(c, A.bass(M(48), 0.4, 0.5))
    sfx.add(T_CHECK, A.glock(M(96), 1.0, 0.7))
    sfx.add(T_CHECK + 0.02, A.twinkle(0.8))
    sfx.add(T_CHECK, A.boing(0.35, 340))
    # the slow, happy ride round the tree
    sfx.add(T_RIDE0, P.roll(T_RIDE1 - T_RIDE0, 0.5))
    sfx.add(T_RIDE0 + 0.1, P.bell(0.6))
    for i in range(10):
        tt = T_RIDE0 + 0.2 + i * 0.22
        music.add(tt, A.pluck(M((60, 64, 67, 72, 67, 64, 65, 69, 67, 72)[i]), 0.3, 0.55))
    for tt, ch in ((12.2, "C"), (12.7, "F"), (13.2, "C"), (13.7, "G"), (14.2, "C")):
        A.strum(music, tt, ch, 0.65)
        music.add(tt, A.bass(M({"C": 48, "F": 41, "G": 43}[ch]), 0.45, 0.65))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.45))
    sfx.add(13.6, A.boing(0.35, 340))
    sfx.add(14.15, P.bell(0.55))
    # paw-bump (signature)
    sfx.add(14.85, A.snare_roll(0.6, 0.8))
    sfx.add(15.45, A.boop(0.9))
    A.jingle(music, 15.47, 1.0, ending=True)
    sfx.add(15.5, A.twinkle(0.8))
    # loop: unclick, BOING the helmet back onto its hook, roll back to the start
    sfx.add(T_UNCLICK, P.click(0.8))
    sfx.add(T_POP, A.boing(0.9, 320))
    sfx.add(T_POP + 0.1, A.whoosh(0.5, 0.6))
    sfx.add(T_HANG, P.clink(0.8))
    sfx.add(16.3, A.boing(0.35, 300))
    sfx.add(16.62, A.boing(0.3, 330))
    sfx.add(T_BACK0, P.roll(T_BACK1 - T_BACK0, 0.5))
    for i in range(4):
        sfx.add(T_BACK0 + 0.05 + i * 0.16, P.squeak_pedal(0.6))
    A.strum(music, 16.3, "F", 0.5)
    A.strum(music, 16.8, "G7", 0.5)
    music.add(17.2, A.pad([M(55), M(59), M(62)], 0.8, 0.25))
    sfx.add(17.6, P.bell(0.45))
    for i, m in enumerate((64, 65, 66)):
        music.add(17.45 + i * 0.15, A.pluck(M(m - 12), 0.3, 0.55))

    m = A.reverb(music.normalized(), 0.24)
    s = A.reverb(sfx.normalized(), 0.08)
    y = 0.55 * m / max(1e-9, abs(m).max()) + 0.7 * s / max(1e-9, abs(s).max())
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.01)


# ---------------------------------------------------------------- output
def render(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    wav = os.path.join(ROOT, "build", "ep07_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep07_helmet_on.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{scene.W}x{scene.H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    t0 = time.time()
    for i in range(n):
        proc.stdin.write(render_frame(i / FPS).convert("RGB").tobytes())
        if i % 90 == 0:
            print(f"frame {i}/{n}  {time.time() - t0:.0f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", out, f"in {time.time() - t0:.0f}s")
    return out


def stills(path, times=None):
    times = times or [0.0, 1.8, 3.4, 4.8, 5.27, 5.9, 6.5, 7.15, 7.65, 8.75, 9.3, 9.8, 10.3, 10.95,
                      11.6, 12.4, 12.9, 13.5, 14.2, 15.6, 16.7, 17.3, 17.99]
    cols = 8
    rows = math.ceil(len(times) / cols)
    sheet = Image.new("RGB", (216 * cols, 404 * rows), "white")
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i, tt in enumerate(times):
        im = render_frame(tt).convert("RGB").resize((216, 384))
        x, y = (i % cols) * 216, (i // cols) * 404
        sheet.paste(im, (x, y + 20))
        d.text((x + 6, y + 4), f"{tt:.2f}s", fill="black")
    sheet.save(path)
    print("wrote", path)


KEYS = [(0.0, "0.0s hook"), (3.4, "3.4s choice"), (5.27, "5.3s bump: boing!"), (6.5, "6.5s leaf on bare head"),
        (7.65, "7.7s ears pop it off"), (9.7, "9.7s the ear holes"), (10.95, "11.0s click (2)"),
        (15.6, "15.6s paw-bump")]


def key_sheet(path, keys=KEYS, w=360):
    from PIL import ImageDraw
    import paperlib
    h = int(w * scene.H / scene.W)
    cols = 4
    rows = math.ceil(len(keys) / cols)
    sheet = Image.new("RGB", (w * cols + 10 * (cols + 1), (h + 44) * rows + 10), (250, 248, 244))
    d = ImageDraw.Draw(sheet)
    font = paperlib.round_font(22)
    for i, (tt, label) in enumerate(keys):
        im = render_frame(tt).convert("RGB").resize((w, h), Image.LANCZOS)
        x = 10 + (i % cols) * (w + 10)
        y = 10 + (i // cols) * (h + 44)
        d.text((x + 4, y + 4), label, fill=(60, 50, 70), font=font)
        sheet.paste(im, (x, y + 34))
    sheet.save(path)
    print("wrote", path)


if __name__ == "__main__":
    if "--stills" in sys.argv:
        os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
        stills(os.path.join(ROOT, "build", "ep07_stills.png"))
    elif "--keys" in sys.argv:
        os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
        key_sheet(os.path.join(ROOT, "reviews", "ep07_keys.png"))
    else:
        render(os.path.join(ROOT, "output"))
