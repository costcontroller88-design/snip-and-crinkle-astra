"""Episode 6 — Achoo! Elbow Sneeze? 🤧

A sunny playroom (striped peach wall, window, paper rainbow, toy shelf, round rug).
Snip holds up the gold star block to finish a tall block tower, but a floating feather lands on
Snip's nose: "ah... ah..." Choice: sneeze into the air, or into your elbow? Snip sneezes into
the air: a giant ACHOO blows the tower over (soft clatter onto the rug), Crinkle's scarf flaps,
and little smiley germs land on every block and on Crinkle. Crinkle shows the elbow sneeze
(a tiny puff, nothing flies). They rebuild (each block's germ pops away), the feather drifts
back down: ah (1)... ah (2)... ah (3)... CHOO into the elbow — the tower only wobbles. Snip puts
the star on top (check, hearts), the signature paw-bump, and Crinkle lifts the star off and
hands it back while the feather floats down again, so the last frame equals the first.

Run:  python3 episodes/ep06_achoo_elbow_sneeze.py            (render -> output/)
      python3 episodes/ep06_achoo_elbow_sneeze.py --stills   (contact sheet -> build/)
      python3 episodes/ep06_achoo_elbow_sneeze.py --keys     (review key frames -> reviews/ep06_keys.png)
"""
import math
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

from PIL import Image  # noqa: E402

import audio as A  # noqa: E402
import icons  # noqa: E402
import props_sneeze as P  # noqa: E402
import scene  # noqa: E402
from characters import Character  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, rot, seg  # noqa: E402

FPS = 30
DUR = 18.0
TY = P.FLOOR_Y
B = P.BLOCK
SN_HOME = 340
CR_HOME = 785                         # keeps his right arm clear of the like/comment buttons
SN_BUMP, CR_BUMP = 356, 770
BUMP_PT = (551, 1292)                 # paws meet in front of the tower, under the star
TX = 548                              # tower x
NB = 3                                # three blocks, then the star on top
SLOTS = [(TX, TY - B / 2 - B * i) for i in range(NB + 1)]
STAR_SLOT = SLOTS[NB]
HOLD = 46                             # block centre above the paw tip when held
CR_REST_L = 346
SN_PARK = -150                        # Snip's right arm tucked behind the head during an elbow sneeze
CR_PARK = 150                         # Crinkle's left arm tucked behind the head

BG = P.background()
BLOCKS = [P.tower_blocks()[i] for i in (0, 2, 3)]      # circle, square, heart
STAR = P.star_block()
FEATHER = P.feather()
BIG_PUFF = P.big_puff()
TINY_PUFF = P.tiny_puff()
WIND = P.wind_lines()
TICKLE = P.tickle_lines()
SCARF = P.scarf_tail()
POP = P.pop_ring()
SN_ELBOW, SN_ELBOW_OFF = P.elbow_pose("snip")
CR_ELBOW, CR_ELBOW_OFF = P.elbow_pose("crinkle")
GERMS = {(i, m): P.germ(P.GERM_COLORS[i % 4], m, i) for i in range(5) for m in ("smile", "giggle", "gasp")}
NUMS = [scene.numeral(n, c) for n, c in ((1, (244, 112, 104)), (2, (255, 196, 52)), (3, (84, 176, 230)))]
BUB_AIR = P.choice_bubble("air", (240, 110, 100))
BUB_ELBOW = P.choice_bubble("elbow", (90, 190, 120))
QMARK = icons.question()
CHECK = icons.check(130)
SPARKLE = scene.sparkle()
HEARTS = [scene.heart(c, 100) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120), (255, 150, 170),
                                       (240, 72, 98), (255, 120, 150))]
SNIP = Character("snip", 1.15)
CR = Character("crinkle", 1.2)

SNIP_BLINKS = (0.35, 5.95, 7.2, 8.4, 12.9, 14.2, 16.25)
CR_BLINKS = (0.6, 1.9, 6.1, 7.85, 9.3, 12.7, 14.3, 16.5)

T_FEATHER_ON = 0.8                    # feather lands on Snip's nose
AH1 = (1.15, 1.85)                    # first tickle: ah... ah...
T_ACHOO = 4.75
T_LANDS = (5.18, 5.3, 5.36)           # when each block lands on the rug
T_STAR_LAND = 5.3
T_PAT = 6.15                          # Crinkle pats the germ off his tummy
T_CR_UP, T_CR_CHOO, T_CR_DOWN = 6.5, 6.85, 7.25
T_REB = 8.05                          # rebuild: block i lifts at T_REB + 0.3*i
T_FEATHER2 = 9.55                     # the feather drifts back onto Snip's nose
AHS = (9.8, 10.25, 10.7)              # ah (1) ... ah (2) ... ah (3)
T_SN_UP, T_CHOO, T_SN_DOWN = 10.78, 11.0, 11.42
T_STAR_UP, T_PLACE0, T_PLACE1 = 11.6, 12.0, 12.32
T_CHECK = 12.38
HEART_PLAN = ((12.6, 290, 880), (12.72, 560, 700), (12.84, 820, 820), (12.96, 420, 680), (13.08, 700, 640),
              (13.2, 220, 700))
T_BUMP = 14.95
T_LIFT0, T_LIFT1, T_GIVE1 = 16.75, 17.0, 17.3

# rest spots on the rug after the tumble (x, y, angle)
LAND = [(612, 1508, 14), (726, 1534, -84), (856, 1504, 96)]
STAR_LAND = (440, 1532, 24)
FEATHER_L = 150 * 1.0                # feather length (quill end to tip) at the drawn scale


# ---------------------------------------------------------------- helpers
def blinking(t, times, d=0.13):
    return any(0 <= t - b < d for b in times)


def spring(t, t0, amp, freq=5.0, damp=4.5):
    if t < t0:
        return 0.0
    dt = t - t0
    return amp * math.exp(-damp * dt) * math.sin(2 * math.pi * freq * dt)


def hop_curve(t, t0, t1, n, height):
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


def ft(t):
    """Time used for every character and prop state: everything holds still during the freeze."""
    return 2.4999 if frozen(t) else t


def pop_scale(t, t0, d=0.3):
    return ease_out_back(seg(t, t0, t0 + d))


def near(a, ref):
    return a + 360 * round((ref - a) / 360)


def aim(ch, st, side, target, ref):
    sh = ch.shoulder_pt(st["x"], TY, side, st["hop"], st["lean"], st["sq"])
    a = math.degrees(math.atan2(target[0] - sh[0], target[1] - sh[1])) - st["lean"]
    return near(a, ref)


def tip(ch, st, side):
    arm = st["arm_l"] if side == "l" else st["arm_r"]
    return ch.paw_tip(st["x"], TY, side, arm, st["hop"], st["lean"], st["sq"])


def nose(st):
    hx, hy = SNIP.head_pivot(st["x"], TY, st["hop"], st["lean"], st["sq"], st["head_dy"])
    ox, oy = rot(0, (170 - 260) * 1.15, st["lean"] + st["tilt"])
    return hx + ox, hy + oy


def head_top(st):
    hx, hy = SNIP.head_pivot(st["x"], TY, st["hop"], st["lean"], st["sq"], st["head_dy"])
    ox, oy = rot(0, -246 * 1.15, st["lean"] + st["tilt"])
    return hx + ox, hy + oy


def held_tip():
    """Where Snip's right paw holds the star in the opening shot (just above the tower)."""
    return (STAR_SLOT[0] - 14, STAR_SLOT[1] - 60 + HOLD)


# ---------------------------------------------------------------- Snip
def snip_base():
    return dict(x=SN_HOME, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, arm_l=-14.0, arm_r=14.0, eyes="normal",
                mouth="w", look=(0, 0), head_dy=0.0, ears=[0.0, 0.0], ear_stretch=1.0, elbow=0.0)


def snip_hook_pose(s):
    """The opening pose (t = 0): star held up over the tower, proud look up at it."""
    s.update(lean=-4.0, eyes="sparkle", mouth="smile", look=(6, -8))
    s["arm_r"] = aim(SNIP, s, "r", held_tip(), 150)
    return s


def ah_pose(s, k, wob):
    """Head tips back for an 'ah...' (k = 0..1 how far), eyes squeeze, mouth opens, ears rise."""
    s["head_dy"] = -16 * k
    s["lean"] = s["lean"] * (1 - k) + 6 * k
    s["tilt"] = 5 * k + wob
    s["eyes"] = "closed" if k > 0.35 else s["eyes"]
    s["mouth"] = "O" if k > 0.35 else "o"
    s["ears"] = [-9 * k, 9 * k]
    s["ear_stretch"] = 1 + 0.16 * k
    return s


def snip_state(t):
    t = ft(t)
    s = snip_base()
    idle_ear = 2.0 * math.sin(2 * math.pi * t / 3.0)

    if t < AH1[0]:                    # HOOK: star held high... a feather lands on the nose
        snip_hook_pose(s)
        if t >= T_FEATHER_ON - 0.05:
            s.update(eyes="wide", mouth="o", look=(1, 9))
            s["tilt"] = 3 * math.sin(2 * math.pi * 11 * t) * seg(t, T_FEATHER_ON, T_FEATHER_ON + 0.1)
            e = spring(t, T_FEATHER_ON, 8, 6.0, 4.0)
            s["ears"] = [e, -e]
    elif t < T_ACHOO:                 # DESIRE / TENSION: ah... ah... (frozen at the peak during the choice)
        snip_hook_pose(s)
        k1 = ease_out(seg(t, AH1[0], AH1[0] + 0.3)) * 0.55
        k2 = ease_out(seg(t, AH1[1], AH1[1] + 0.35)) * 0.45
        k3 = ease_in_out(seg(t, 4.5, 4.7)) * 0.15        # one last breath in, after the freeze
        wob = 2.5 * math.sin(2 * math.pi * 9 * t)
        ah_pose(s, k1 + k2 + k3, wob)
        s["arm_r"] = aim(SNIP, dict(s, lean=-4.0, hop=0.0), "r", held_tip(), 150) + 4 * math.sin(2 * math.pi * 3 * t)
        s["arm_l"] = -14 - 20 * (k1 + k2)
    elif t < 5.45:                    # ACHOO! head snaps forward, the star flies out of the paw
        p = ease_out(seg(t, T_ACHOO, T_ACHOO + 0.1))
        back = ease_in_out(seg(t, 5.0, 5.45))
        s.update(eyes="closed", mouth="O" if t < 5.15 else "o")
        s["lean"] = lerp(7, -12, p) * (1 - back) + -3 * back
        s["head_dy"] = lerp(-19, 16, p) * (1 - back)
        s["sq"] = 1 - 0.08 * p * (1 - back)
        s["ear_stretch"] = lerp(1.18, 1.0, p)
        e = spring(t, T_ACHOO, 26, 3.5, 3.0)
        s["ears"] = [e, -e]
        s["arm_r"] = lerp(150, 175, p) * (1 - back) + 14 * back
        s["arm_l"] = lerp(-40, -70, p) * (1 - back) - 14 * back
        if t > 5.2:
            s.update(eyes="wide", look=(9, 6))
    elif t < 6.3:                     # oops... looks at the mess, ears droop
        s.update(lean=-3 * (1 - seg(t, 5.45, 5.7)), eyes="wide", mouth="wobble", look=(9, 6))
        droop = 18 * ease_out(seg(t, 5.6, 5.9))
        s["ears"] = [droop, -droop]
        if t > 5.95:
            s.update(eyes="normal", look=(9, -1))
    elif t < 7.9:                     # watches Crinkle's elbow sneeze, then nods
        s.update(eyes="wide", mouth="o", look=(9, -4))
        droop = 18 * (1 - ease_in_out(seg(t, 6.4, 6.8)))
        e = spring(t, T_CR_CHOO, 9, 5.0, 4.0)
        s["ears"] = [droop + e, -droop - e]
        if t > 7.3:
            s.update(eyes="sparkle", mouth="smile", look=(8, -2))
            s["head_dy"] = 10 * math.sin(math.pi * seg(t, 7.4, 7.6)) + 10 * math.sin(math.pi * seg(t, 7.62, 7.82))
    elif t < T_FEATHER2 - 0.1:        # REBUILD: tosses blocks 0 and 2, then looks up (the feather!)
        s.update(eyes="happy", mouth="grin", look=(8, -4))
        for i in (0, 2):
            t0 = T_REB + 0.3 * i
            k = math.sin(math.pi * seg(t, t0 - 0.08, t0 + 0.2))
            s["arm_r"] = max(s["arm_r"], 14 + 110 * k)
            s["lean"] += -6 * k
        if t > 9.0:
            s.update(eyes="wide", mouth="o", look=(4, -10))
            s["head_dy"] = -6 * ease_out(seg(t, 9.0, 9.2))
    elif t < T_SN_UP:                 # tickle again: ah (1) ... ah (2) ... ah (3)
        s.update(eyes="wide", mouth="o", look=(1, 9), head_dy=-6.0)
        k = 0.0
        for i, a in enumerate(AHS):
            k += ease_out(seg(t, a, a + 0.25)) * (0.3, 0.3, 0.3)[i]
        wob = 2.5 * math.sin(2 * math.pi * 9 * t) * seg(t, AHS[0], AHS[0] + 0.1)
        if k > 0:
            ah_pose(s, k, wob)
            s["head_dy"] -= 6 * (1 - seg(t, AHS[0], AHS[0] + 0.25))
        s["arm_l"] = -14 - 18 * k
    elif t < T_SN_DOWN:               # ... CHOO into the elbow
        s.update(eyes="closed", mouth="O", head_dy=18.0, lean=0.0, arm_r=SN_PARK, elbow=1.0)
        s["ear_stretch"] = lerp(1.14, 1.0, ease_out(seg(t, T_CHOO, T_CHOO + 0.2)))
        e = spring(t, T_CHOO, 18, 4.0, 3.5)
        s["ears"] = [-6 + e, 6 - e]
        s["sq"] = 1 - 0.06 * math.sin(math.pi * seg(t, T_CHOO, T_CHOO + 0.2))
        if t < T_CHOO:
            s["head_dy"] = lerp(-10, 18, ease_out(seg(t, T_SN_UP, T_SN_UP + 0.12)))
        if t > T_CHOO + 0.25:
            s["mouth"] = "w"
    elif t < 14.0:                    # PAYOFF: proud smile, star into the paw, onto the top!
        s.update(eyes="happy", mouth="grin", look=(8, -4))
        e = spring(t, T_SN_DOWN, 10, 5.0, 4.0)
        s["ears"] = [e, -e]
        s["head_dy"] = 18 * (1 - ease_out(seg(t, T_SN_DOWN, T_SN_DOWN + 0.2)))
        if t < T_STAR_UP + 0.3:
            k = ease_in_out(seg(t, T_STAR_UP - 0.1, T_STAR_UP + 0.15))
            s["arm_r"] = lerp(14, 60, k)
            s["lean"] = -6 * k
        elif t < T_PLACE1 + 0.1:
            s.update(eyes="sparkle", mouth="smile", look=(6, -8), lean=-5.0)
            k = ease_in_out(seg(t, T_STAR_UP + 0.3, T_PLACE0))
            s["arm_r"] = lerp(60, aim(SNIP, s, "r", star_place_tip(), 150), k)
            if t > T_PLACE0:
                s["arm_r"] = aim(SNIP, s, "r", star_place_tip(), 150)
        else:
            down = ease_in_out(seg(t, T_PLACE1 + 0.1, T_PLACE1 + 0.4))
            s["lean"] = -5 * (1 - down)
            s["arm_r"] = lerp(aim(SNIP, dict(s, lean=-5.0), "r", star_place_tip(), 150), 14, down)
            for h0 in (12.55, 13.25):
                h, sq = hop_curve(t, h0, h0 + 0.34, 1, 26)
                if h or sq != 1.0:
                    s["hop"], s["sq"] = h, sq
            if t > 12.5:
                s["arm_l"] = -14 - 130 * math.sin(math.pi * seg(t, 12.5, 13.9)) ** 0.5
    elif t < 16.1:                    # PAW-BUMP
        h, sq = hop_curve(t, 14.0, 14.4, 1, 20)
        s.update(x=lerp(SN_HOME, SN_BUMP, ease_in_out(seg(t, 14.0, 14.4))), hop=h, sq=sq, eyes="happy",
                 mouth="grin", look=(8, 0))
        wind = ease_in_out(seg(t, 14.5, 14.7))
        swing = ease_out_back(seg(t, 14.7, T_BUMP))
        back = ease_in_out(seg(t, 15.7, 16.0))
        a_bump = aim(SNIP, dict(s, hop=0.0, sq=1.0), "r", (BUMP_PT[0] - 6, BUMP_PT[1]), 90)
        s["arm_r"] = lerp(lerp(lerp(14, -6, wind), a_bump, swing), 14, back)
        e = spring(t, T_BUMP, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
        h2, sq2 = hop_curve(t, 15.7, 16.05, 1, 22)
        if h2 or t >= 15.7:
            s["x"] = lerp(SN_BUMP, SN_HOME, ease_in_out(seg(t, 15.7, 16.05)))
            s["hop"], s["sq"] = h2, sq2
    else:                             # LOOP: ear flick sends the feather up; Crinkle hands the star back
        s.update(eyes="happy" if t < 16.5 else "normal", mouth="grin" if t < 16.5 else "smile", look=(8, -6))
        e = spring(t, 16.3, 14, 5.0, 3.0)
        s["ears"] = [e, -e]
        if t > 16.5:
            s["look"] = (2, -10) if t < 16.95 else (6, -8)
        rise = ease_in_out(seg(t, T_LIFT1, T_GIVE1))
        hook = snip_hook_pose(snip_base())
        s["arm_r"] = lerp(14, hook["arm_r"], rise)
        s["lean"] = lerp(0, -4, rise)
        if t > T_GIVE1:
            s.update(eyes="sparkle", look=(6, -8))
        s["ears"][0] *= 1 - seg(t, 17.6, 18.0)
        s["ears"][1] *= 1 - seg(t, 17.6, 18.0)

    s["ears"][0] += idle_ear
    s["ears"][1] -= idle_ear
    if s["hop"] == 0:
        s["sq"] *= breath(t)
    return s


def star_place_tip():
    return (STAR_SLOT[0] - 4, STAR_SLOT[1] + HOLD - 6)


# ---------------------------------------------------------------- Crinkle
def crinkle_state(t):
    t = ft(t)
    s = dict(x=CR_HOME, hop=0.0, sq=1.0, lean=0.0, arm_l=CR_REST_L, arm_r=2.0, eyes="normal", mouth="smile",
             look=(-6, -4), head_dy=0.0, elbow=0.0)
    if t < 1.0:                       # HOOK: watching the tower, happy
        s.update(look=(-7, -5))
        if t > T_FEATHER_ON + 0.05:
            s.update(eyes="wide", mouth="o", look=(-9, -2))
    elif t < T_ACHOO:                 # uh-oh... leans back, paws up
        k = ease_out(seg(t, 1.2, 1.6)) * 0.6 + ease_out(seg(t, 1.9, 2.3)) * 0.4
        s.update(eyes="wide", mouth="o" if t < 1.9 else "O", look=(-10, -1))
        s["lean"] = -6 * k
        s["arm_l"] = lerp(CR_REST_L, 300, k)
        s["arm_r"] = lerp(2, 40, k)
        s["head_dy"] = -6 * k
    elif t < 6.0:                     # blown back by the sneeze wind, then shakes it off
        p = ease_out(seg(t, T_ACHOO + 0.08, T_ACHOO + 0.25))
        back = ease_in_out(seg(t, 5.45, 5.85))
        s.update(eyes="closed" if t < 5.5 else "wide", mouth="O" if t < 5.5 else "o", look=(-6, 6))
        s["x"] = CR_HOME + 18 * p * (1 - back)
        s["lean"] = (-6 + -10 * p) * (1 - back) + 2.5 * math.sin(2 * math.pi * 5 * t) * back * (1 - seg(t, 5.7, 6.0))
        s["arm_l"] = lerp(300, 250, p) * (1 - back) + CR_REST_L * back
        s["arm_r"] = lerp(40, 80, p) * (1 - back) + 2 * back
        if t > 5.5:
            s["look"] = (-2, 9)       # a germ on my tummy!
    elif t < T_CR_UP - 0.1:           # pats the germ off, smiles at Snip: "watch this!"
        s.update(eyes="normal", mouth="o", look=(-2, 9))
        k = math.sin(math.pi * seg(t, T_PAT - 0.15, T_PAT + 0.15))
        s["arm_r"] = 2 + 40 * k
        if t > T_PAT + 0.1:
            s.update(eyes="happy", mouth="grin", look=(-8, -2))
    elif t < T_CR_DOWN:               # ELBOW SNEEZE demo
        s.update(eyes="closed", mouth="O", head_dy=18.0, arm_l=CR_PARK, elbow=1.0)
        if t < T_CR_UP:
            s["head_dy"] = 18 * ease_out(seg(t, T_CR_UP - 0.1, T_CR_UP))
        if t > T_CR_CHOO:
            s["sq"] = 1 - 0.05 * math.sin(math.pi * seg(t, T_CR_CHOO, T_CR_CHOO + 0.2))
        if t > T_CR_CHOO + 0.2:
            s["mouth"] = "smile"
    elif t < 7.95:                    # "see? into your elbow!" nods at Snip
        s.update(eyes="happy", mouth="grin", look=(-8, -2))
        s["head_dy"] = 18 * (1 - ease_out(seg(t, T_CR_DOWN, T_CR_DOWN + 0.2)))
        s["head_dy"] += 9 * math.sin(math.pi * seg(t, 7.45, 7.65))
        k = ease_in_out(seg(t, 7.3, 7.5)) * (1 - ease_in_out(seg(t, 7.7, 7.9)))
        s["arm_l"] = lerp(CR_REST_L, 250, k)             # opens his paw towards Snip: your turn
    elif t < T_FEATHER2:              # REBUILD: tosses blocks 1 and 3
        s.update(eyes="happy", mouth="grin", look=(-7, -4))
        for i in (1,):
            t0 = T_REB + 0.3 * i
            k = math.sin(math.pi * seg(t, t0 - 0.08, t0 + 0.2))
            s["arm_l"] = min(s["arm_l"], CR_REST_L - 110 * k)
            s["lean"] += 5 * k
        if t > 9.0:
            s.update(eyes="wide", mouth="o", look=(-8, -9))
    elif t < T_SN_DOWN + 0.1:         # watches Snip count the ahs... and the elbow sneeze
        s.update(eyes="wide", mouth="o", look=(-9, -3))
        for a in AHS:
            s["head_dy"] += 5 * math.sin(math.pi * seg(t, a, a + 0.25))
        if t > T_CHOO:
            s.update(eyes="sparkle", mouth="grin")
    elif t < 14.0:                    # PAYOFF: claps and cheers
        s.update(eyes="happy", mouth="grin", look=(-7, -4))
        clap = max(0.0, math.sin(2 * math.pi * (t - 12.4) / 0.36)) if 12.4 < t < 13.85 else 0.0
        up = ease_in_out(seg(t, 12.3, 12.45)) * (1 - ease_in_out(seg(t, 13.8, 13.98)))
        s["arm_l"] = lerp(CR_REST_L, 220 + 22 * clap, up)
        s["arm_r"] = lerp(2, 140 - 22 * clap, up)
        h, sq = hop_curve(t, 12.9, 13.24, 1, 22)
        s["hop"], s["sq"] = h, sq
    elif t < 16.1:                    # PAW-BUMP
        h, sq = hop_curve(t, 14.0, 14.4, 1, 20)
        s.update(x=lerp(CR_HOME, CR_BUMP, ease_in_out(seg(t, 14.0, 14.4))), hop=h, sq=sq, eyes="happy",
                 mouth="grin", look=(-8, 0))
        wind = ease_in_out(seg(t, 14.5, 14.7))
        swing = ease_out_back(seg(t, 14.7, T_BUMP))
        back = ease_in_out(seg(t, 15.7, 16.0))
        a_bump = aim(CR, dict(s, hop=0.0, sq=1.0), "l", (BUMP_PT[0] + 6, BUMP_PT[1]), 270)
        s["arm_l"] = lerp(lerp(lerp(CR_REST_L, 360, wind), a_bump, swing), CR_REST_L, back)
        h2, sq2 = hop_curve(t, 15.75, 16.1, 1, 22)
        if t >= 15.75:
            s["x"] = lerp(CR_BUMP, CR_HOME, ease_in_out(seg(t, 15.75, 16.1)))
            s["hop"], s["sq"] = h2, sq2
    else:                             # LOOP: lifts the star off the tower and hands it to Snip, back home
        s.update(eyes="happy", mouth="grin", look=(-7, -8))
        c = star_center(t)
        if t < 17.45:
            reach = ease_in_out(seg(t, 16.45, T_LIFT0))
            st = dict(s)
            a = aim(CR, st, "l", (c[0] + 10, c[1] + HOLD), 200)
            s["arm_l"] = lerp(CR_REST_L, a, reach)
            if t > T_GIVE1:
                s["arm_l"] = lerp(a, CR_REST_L, ease_in_out(seg(t, T_GIVE1, 17.45)))
        else:
            s.update(eyes="normal", mouth="smile", look=(-7, -5))
    if s["hop"] == 0:
        s["sq"] *= breath(t + 0.7, 2.25, 0.01)
    return s


# ---------------------------------------------------------------- blocks + star
def arc(p, a, b, h):
    return (lerp(a[0], b[0], p), lerp(a[1], b[1], p) - h * 4 * p * (1 - p))


def block_state(i, t):
    """(x, y, angle, standing_in_tower, germ_alpha) for tower block i."""
    t = ft(t)
    slot = SLOTS[i]
    lx, ly, la = LAND[i]
    t_fall = T_ACHOO + 0.1 + 0.05 * (NB - 1 - i)         # top blocks get blown first
    t_up = T_REB + 0.3 * i
    if t < t_fall:
        return slot[0], slot[1], 0.0, True, 0.0
    if t < T_LANDS[i]:
        p = seg(t, t_fall, T_LANDS[i])
        x, y = arc(ease_out(p) * 0.4 + p * 0.6, slot, (lx, ly), 70 + 50 * i)
        return x, y, la * p, False, 0.0
    if t < t_up:
        dt = t - T_LANDS[i]
        bounce = 14 * math.exp(-7 * dt) * abs(math.sin(2 * math.pi * 2.5 * dt))
        germ = 0.0
        return lx, ly - bounce, la, False, germ
    if t < t_up + 0.32:
        p = ease_in_out(seg(t, t_up, t_up + 0.32))
        x, y = arc(p, (lx, ly), slot, 150)
        return x, y, lerp(la, near(0, la) if abs(la) < 120 else 360 * round(la / 360), p), False, 0.0
    return slot[0], slot[1], 0.0, True, 0.0


def tower_wobble(t):
    t = ft(t)
    if T_CHOO + 0.05 <= t < T_CHOO + 0.9:
        dt = t - T_CHOO - 0.05
        return 2.6 * math.exp(-4 * dt) * math.sin(2 * math.pi * 3 * dt)
    return 0.0


def star_center(t):
    """Star block centre and angle."""
    t = ft(t)
    if t < T_ACHOO + 0.03:
        return star_in_paw(t)
    if t < T_STAR_LAND:
        p = seg(t, T_ACHOO + 0.03, T_STAR_LAND)
        a = star_in_paw(T_ACHOO + 0.02)
        x, y = arc(p, a[:2], STAR_LAND[:2], 160)
        return x, y, STAR_LAND[2] * p + 300 * p
    if t < T_STAR_UP:
        dt = t - T_STAR_LAND
        return STAR_LAND[0], STAR_LAND[1] - 12 * math.exp(-7 * dt) * abs(math.sin(2 * math.pi * 2.5 * dt)), \
            STAR_LAND[2] + 300
    if t < T_STAR_UP + 0.3:                              # hops up into Snip's paw
        p = ease_in_out(seg(t, T_STAR_UP, T_STAR_UP + 0.3))
        sn = snip_state(T_STAR_UP + 0.3)
        tp = tip(SNIP, sn, "r")
        x, y = arc(p, STAR_LAND[:2], (tp[0], tp[1] - HOLD), 140)
        return x, y, lerp(STAR_LAND[2] + 300, 360, p)
    if t < T_PLACE1:
        sn = snip_state(t)
        tp = tip(SNIP, sn, "r")
        held = (tp[0], tp[1] - HOLD)
        if t > T_PLACE0:
            k = ease_out(seg(t, T_PLACE0, T_PLACE1))
            held = (lerp(held[0], STAR_SLOT[0], k), lerp(held[1], STAR_SLOT[1], k) - 30 * math.sin(math.pi * k))
        return held[0], held[1], 0.0
    if t < T_LIFT0:
        return STAR_SLOT[0], STAR_SLOT[1], 0.0
    if t < T_LIFT1:                                      # Crinkle lifts it off
        k = ease_in_out(seg(t, T_LIFT0, T_LIFT1))
        return STAR_SLOT[0], STAR_SLOT[1] - 40 * k, -6 * math.sin(math.pi * k)
    if t < T_GIVE1:                                      # ... and hands it to Snip
        k = ease_in_out(seg(t, T_LIFT1, T_GIVE1))
        a = star_in_paw(0.0)
        return lerp(STAR_SLOT[0], a[0], k), lerp(STAR_SLOT[1] - 40, a[1], k), 0.0
    return star_in_paw(t)


def star_in_paw(t):
    sn = snip_state(t)
    tp = tip(SNIP, sn, "r")
    return tp[0], tp[1] - HOLD, 0.0


# ---------------------------------------------------------------- feather
def feather_state(t):
    """(tip_x, tip_y, angle, visible): the feather's TIP position (it tickles with the tip)."""
    t = ft(t)
    u = t - DUR if t >= 16.4 else t
    if u < T_FEATHER_ON:                                 # flicked off Snip's head, see-saws down onto the nose
        rest = head_top(snip_state(16.4))
        n = nose(snip_state(T_FEATHER_ON))
        keys = [(-1.1, rest[0] - 40, rest[1], 92), (-0.55, 430, 730, 110), (0.0, 610, 772, -24),
                (0.45, 470, 930, 96), (T_FEATHER_ON, n[0] + 2, n[1] + 2, 60)]
        if u < keys[0][0]:
            return keys[0][1], keys[0][2], 92.0, True
        for (u0, x0, y0, a0), (u1, x1, y1, a1) in zip(keys, keys[1:]):
            if u <= u1:
                q = ease_in_out(seg(u, u0, u1))
                return lerp(x0, x1, q), lerp(y0, y1, q) - 18 * math.sin(math.pi * q), lerp(a0, a1, q), True
    if t < T_ACHOO:                                      # tickling the nose
        n = nose(snip_state(t))
        return n[0] + 2, n[1] + 2, 60 + 6 * math.sin(2 * math.pi * 7 * t), True
    if t < 5.4:                                          # whoosh! blown up and away
        n = nose(snip_state(T_ACHOO))
        p = ease_in_out(seg(t, T_ACHOO, 5.4))
        return n[0] + 520 * p, n[1] - 1000 * p * p, 60 + 540 * p, t < 5.38
    if t < 9.0:
        return 0, 0, 0, False
    if t < T_FEATHER2:                                   # floats back down onto the nose
        n = nose(snip_state(T_FEATHER2))
        p = seg(t, 9.0, T_FEATHER2)
        q = ease_out(p)
        x = lerp(n[0] + 200, n[0] + 2, q) + 50 * math.sin(2 * math.pi * 1.2 * p) * (1 - p)
        y = lerp(260, n[1] + 2, q)
        return x, y, lerp(20, 60, q) + 25 * math.sin(2 * math.pi * 1.4 * p) * (1 - p), True
    if t < T_CHOO:
        n = nose(snip_state(t))
        return n[0] + 2, n[1] + 2, 60 + 6 * math.sin(2 * math.pi * 7 * t), True
    if t < 11.8:                                         # pops up and flutters onto Snip's head
        n = nose(snip_state(T_CHOO - 0.01))
        h = head_top(snip_state(11.8))
        p = seg(t, T_CHOO, 11.8)
        x = lerp(n[0] + 2, h[0] - 40, ease_in_out(p)) + 40 * math.sin(2 * math.pi * p) * (1 - p)
        y = lerp(n[1], h[1], ease_in_out(p)) - 170 * math.sin(math.pi * min(1, p * 1.4)) * (1 - p * 0.5)
        return x, y, lerp(60, 92, p) + 40 * math.sin(2 * math.pi * 1.5 * p) * (1 - p), True
    h = head_top(snip_state(t))                          # rests on Snip's head
    return h[0] - 40, h[1], 92.0, True


# ---------------------------------------------------------------- germs
GERM_TARGETS = [("b", 0), ("b", 1), ("b", 2), ("s", 0), ("c", 0)]


def germ_target(j, t):
    kind, i = GERM_TARGETS[j]
    if kind == "b":
        x, y, ang, _, _ = block_state(i, t)
        return x, y - 58
    if kind == "s":
        x, y, _ = star_center(t)
        return x, y - 58
    cr = crinkle_state(t)
    return cr["x"] - 30, TY - 150 * 1.2 * cr["sq"] - cr["hop"]


def germ_items(t):
    """[(sprite, xy, angle, scale)] for the friendly germs (they ride the sneeze, sit, then pop away)."""
    t = ft(t)
    out = []
    if t < T_ACHOO + 0.05:
        return out
    m = SNIP.mouth_pt(*(lambda s: (s["x"], TY, s["hop"], s["lean"], s["sq"], s["head_dy"]))(snip_state(T_ACHOO + 0.1)))
    for j in range(5):
        t0 = T_ACHOO + 0.08 + 0.05 * j
        t1 = 5.25 + 0.04 * j
        t_pop = germ_pop_time(j)
        if t < t0 or t >= t_pop + 0.01:
            continue
        if t < t1:
            p = seg(t, t0, t1)
            tg = germ_target(j, t1 + 0.2)
            x, y = arc(ease_out(p), (m[0] + 60, m[1]), tg, 120 + 30 * j)
            out.append((GERMS[(j, "gasp")], (x, y), 360 * p, lerp(0.6, 1.15, p)))
        else:
            x, y = germ_target(j, t)
            wig = math.sin(2 * math.pi * 3 * t + j)
            mood = "giggle" if int((t * 2.5 + j * 0.4)) % 2 else "smile"
            out.append((GERMS[(j, mood)], (x, y + 2 * wig), 8 * wig, 1.15))
    return out


def germ_pop_time(j):
    kind = GERM_TARGETS[j][0]
    return T_REB + 0.3 * j if kind == "b" else T_STAR_UP if kind == "s" else T_PAT + 0.05


def germ_pops(t):
    """(xy, t0) for every germ that pops away (block lifted / Crinkle's pat)."""
    out = []
    for j in range(5):
        t_pop = germ_pop_time(j)
        out.append((germ_target(j, t_pop - 0.01), t_pop))
    return out


# ---------------------------------------------------------------- drawing helpers
def draw_char(f, ch, st, blink, elbow_spr, elbow_off, kind):
    kw = dict(hop=st["hop"], lean=st["lean"], arm_l=st["arm_l"], arm_r=st["arm_r"], eyes=st["eyes"],
              mouth=st["mouth"], look=st["look"], squash=st["sq"], head_dy=st["head_dy"], blink=blink)
    if kind == "snip":
        kw.update(head_tilt=st["tilt"], ears=tuple(st["ears"]), ear_stretch=st["ear_stretch"])
    ch.draw(f, st["x"], TY, **kw)
    if st.get("elbow", 0) > 0:
        place(f, elbow_spr, (st["x"] + elbow_off[0], TY - st["hop"] + elbow_off[1] * st["sq"]))


def draw_block(f, spr, x, y, ang, scale=1.0):
    place(f, spr, (x, y), angle=ang, scale=scale)


# ---------------------------------------------------------------- frame
def render_frame(t):
    f = BG.copy()
    tt = ft(t)
    sn = snip_state(t)
    cr = crinkle_state(t)
    wob = tower_wobble(t)

    # standing tower blocks sit behind the characters' arms
    states = [block_state(i, t) for i in range(NB)]
    for i, (x, y, ang, standing, _) in enumerate(states):
        if standing:
            bx, by = rot(x - TX, y - TY, wob)
            draw_block(f, BLOCKS[i], TX + bx, TY + by, ang + wob)
    sc = star_center(t)
    star_on_top = T_PLACE1 <= tt < T_LIFT0
    if star_on_top:
        bx, by = rot(sc[0] - TX, sc[1] - TY, wob)
        draw_block(f, STAR, TX + bx, TY + by, wob)

    draw_char(f, SNIP, sn, blinking(t, SNIP_BLINKS) and not frozen(t), SN_ELBOW, SN_ELBOW_OFF, "snip")
    draw_char(f, CR, cr, blinking(t, CR_BLINKS) and not frozen(t), CR_ELBOW, CR_ELBOW_OFF, "crinkle")

    # the scarf flaps in the sneeze wind
    if T_ACHOO + 0.06 <= tt < 5.75:
        k = ease_out(seg(tt, T_ACHOO + 0.06, T_ACHOO + 0.2)) * (1 - ease_in_out(seg(tt, 5.45, 5.75)))
        nk = CR.anchor(cr["x"], TY, cr["hop"], cr["lean"])(70, -cr_neck())
        place(f, SCARF, nk, angle=-8 + 10 * math.sin(2 * math.pi * 7 * tt), sx=max(0.05, k), sy=1.0)

    # moving / fallen blocks and the star are drawn in front
    for i, (x, y, ang, standing, _) in enumerate(states):
        if not standing:
            draw_block(f, BLOCKS[i], x, y, ang)
    if not star_on_top:
        draw_block(f, STAR, sc[0], sc[1], sc[2])

    # feather
    fx, fy, fa, vis = feather_state(t)
    if vis:
        vx, vy = rot(0, -FEATHER_L, fa)
        place(f, FEATHER, (fx - vx, fy - vy), angle=fa, scale=1.0)
    # Snip's elbow arm is drawn again so it covers the feather on the nose
    if sn["elbow"] > 0:
        place(f, SN_ELBOW, (sn["x"] + SN_ELBOW_OFF[0], TY - sn["hop"] + SN_ELBOW_OFF[1] * sn["sq"]))

    # tickle lines around the nose
    for a0, a1 in ((T_FEATHER_ON, T_ACHOO), (T_FEATHER2, T_SN_UP)):
        if a0 + 0.1 <= tt < a1:
            n = nose(sn)
            k = 0.85 + 0.15 * math.sin(2 * math.pi * 6 * tt)
            place(f, TICKLE, (n[0] - 10, n[1] - 6), scale=k, alpha=min(1.0, (tt - a0 - 0.1) / 0.15))

    # ACHOO: big puff + wind lines
    if T_ACHOO <= tt < 5.9:
        m = SNIP.mouth_pt(sn["x"], TY, sn["hop"], sn["lean"], sn["sq"], sn["head_dy"], sn["tilt"])
        grow = ease_out(seg(tt, T_ACHOO, T_ACHOO + 0.22))
        drift = 120 * ease_out(seg(tt, T_ACHOO + 0.2, 5.9))
        a = 1 - ease_in_out(seg(tt, 5.05, 5.5))
        place(f, BIG_PUFF, (m[0] + 16 + drift, m[1] - 6), angle=-4, scale=0.2 + 0.62 * grow, alpha=a)
        wa = math.sin(math.pi * seg(tt, T_ACHOO + 0.12, 5.4))
        place(f, WIND, (690 + 140 * seg(tt, T_ACHOO, 5.4), 800), scale=0.75, alpha=wa)

    for spr, xy, ang, s_ in germ_items(t):
        place(f, spr, xy, angle=ang, scale=s_)
    for xy, t0 in germ_pops(t):
        if t0 <= tt < t0 + 0.35:
            k = seg(tt, t0, t0 + 0.35)
            place(f, POP, xy, scale=0.5 + 0.7 * k, alpha=1 - k)
            place(f, SPARKLE, xy, scale=0.22 * math.sin(math.pi * k), angle=k * 90)

    # Crinkle's elbow demo: a tiny puff stays at the elbow
    if T_CR_CHOO <= tt < T_CR_DOWN + 0.1:
        m = CR.mouth_pt(cr["x"], TY, cr["hop"], cr["lean"], cr["sq"], cr["head_dy"])
        k = pop_scale(tt, T_CR_CHOO, 0.2) * (1 - ease_in_out(seg(tt, T_CR_DOWN - 0.15, T_CR_DOWN + 0.1)))
        place(f, TINY_PUFF, (m[0] - 70, m[1] - 34), scale=0.8 * k)
    if T_CR_CHOO + 0.12 <= tt < T_CR_DOWN:
        m = CR.mouth_pt(cr["x"], TY, cr["hop"], cr["lean"], cr["sq"], cr["head_dy"])
        k = math.sin(math.pi * seg(tt, T_CR_CHOO + 0.12, T_CR_DOWN))
        place(f, SPARKLE, (m[0] - 120, m[1] - 70), scale=0.3 * k, angle=(tt - T_CR_CHOO) * 90)
    # Snip's elbow sneeze: tiny puff
    if T_CHOO <= tt < T_SN_DOWN + 0.1:
        m = SNIP.mouth_pt(sn["x"], TY, sn["hop"], sn["lean"], sn["sq"], sn["head_dy"])
        k = pop_scale(tt, T_CHOO, 0.2) * (1 - ease_in_out(seg(tt, T_SN_DOWN - 0.15, T_SN_DOWN + 0.1)))
        place(f, TINY_PUFF, (m[0] + 74, m[1] - 52), scale=1.05 * k)

    # counting numerals over Snip's head
    for i, a in enumerate(AHS):
        if a <= tt < T_SN_DOWN:
            out = 1 - ease_in_out(seg(tt, T_SN_DOWN - 0.2, T_SN_DOWN))
            place(f, NUMS[i], (450 + 130 * i, 640), scale=0.62 * pop_scale(tt, a, 0.28) * out,
                  angle=(-6, 0, 6)[i] + 3 * math.sin(tt * 6 + i))

    # paw-bump: both touching paws in front
    if 14.75 <= tt < 15.8:
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], TY, "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])
        place(f, CR.arm_l, CR.shoulder_pt(cr["x"], TY, "l", cr["hop"], cr["lean"], cr["sq"]),
              angle=cr["arm_l"] + cr["lean"])
    if T_BUMP <= tt < 15.7:
        a_ = SNIP.paw_tip(sn["x"], TY, "r", sn["arm_r"], sn["hop"], sn["lean"], sn["sq"])
        b_ = CR.paw_tip(cr["x"], TY, "l", cr["arm_l"], cr["hop"], cr["lean"], cr["sq"])
        mid = ((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2 - 10)
        place(f, SPARKLE, (mid[0], mid[1] - 30), scale=pop_scale(tt, T_BUMP, 0.22) * 0.4,
              angle=(tt - T_BUMP) * 60, alpha=1 - ease_in_out(seg(tt, 15.4, 15.7)))

    # payoff: check + hearts
    if T_CHECK <= tt < 13.6:
        place(f, CHECK, (528, 790), scale=pop_scale(tt, T_CHECK, 0.25) * (1 - ease_in_out(seg(tt, 13.35, 13.6))))
    for i, (t0, x, y) in enumerate(HEART_PLAN):
        if t0 <= tt < 14.2:
            p = seg(tt, t0, 14.2)
            place(f, HEARTS[i], (x + 10 * math.sin(tt * 3 + i), y - 160 * p), scale=pop_scale(tt, t0, 0.25),
                  alpha=1 - ease_in_out(seg(tt, 13.8, 14.2)), angle=10 * math.sin(tt * 2.5 + i))

    # FREEZE: dim + choice bubbles
    if 2.5 <= t < 4.6:
        dim = 0.32 * ease_in_out(seg(t, 2.5, 2.8)) * (1 - ease_in_out(seg(t, 4.35, 4.6)))
        if dim > 0.01:
            f.alpha_composite(Image.new("RGBA", f.size, (30, 26, 52, int(255 * dim))))
        gone = 1 - ease_in_out(seg(t, 4.4, 4.55))
        pulse_a = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 2.95) / 1.0))
        pulse_b = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 3.45) / 1.0))
        place(f, BUB_AIR, (320, 610), scale=1.3 * pop_scale(t, 2.55) * gone * (pulse_a if t > 2.95 else 1))
        place(f, BUB_ELBOW, (790, 610), scale=1.3 * pop_scale(t, 2.7) * gone * (pulse_b if t > 3.45 else 1))
        place(f, QMARK, (555, 450), scale=pop_scale(t, 2.85, 0.25) * gone, angle=8 * math.sin(t * 4))

    return camera(f, t)


def cr_neck():
    return CR.neck_h - 26


CAM0 = (1.35, 548, 990)
CAM1 = (1.1, 560, 1040)
CAM_KEYS = [
    (0.0,) + CAM0, (0.9,) + CAM0, (2.4,) + CAM1, (6.0,) + CAM1, (6.6, 1.2, 610, 1080), (7.5, 1.2, 610, 1080),
    (8.0,) + CAM1, (9.3,) + CAM1, (9.8, 1.24, 480, 1060), (11.4, 1.24, 480, 1060), (11.95,) + CAM1,
    (14.5,) + CAM1, (14.85, 1.2, 575, 1080), (15.75, 1.2, 575, 1080), (DUR,) + CAM0]


def camera(f, t):
    z, cx, cy = 1.0, 540, 960
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
    for t0, d, amp in ((T_ACHOO, 0.45, 9), (5.2, 0.3, 4)):
        if t0 <= t < t0 + d:          # eased bump shakes
            k = math.sin(math.pi * seg(t, t0, t0 + d))
            cx += amp * k * math.sin(t * 95)
            cy += amp * 0.8 * k * math.cos(t * 81)
    w, h = scene.W / z, scene.H / z
    left = min(max(cx - w / 2, 0), scene.W - w)
    top = min(max(cy - h / 2, 0), scene.H - h)
    return f.resize((scene.W, scene.H), Image.BICUBIC, box=(left, top, left + w, top + h))


# ---------------------------------------------------------------- audio
def build_audio(path):
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    M = A.midi
    # hook: proud tower music, the feather floats down
    A.jingle(music, 0.02)
    sfx.add(0.05, A.twinkle(0.5))
    for i, m in enumerate((88, 86, 84, 83)):            # floaty feather notes
        sfx.add(0.1 + i * 0.17, A.glock(M(m), 0.6, 0.3))
    sfx.add(T_FEATHER_ON, A.boop(0.6))
    # desire/tension: ah... ah...
    for tt, ch in ((1.0, "C"), (1.5, "Am"), (2.0, "F")):
        A.strum(music, tt, ch, 0.5)
    for tt, m in ((1.0, 48), (1.5, 45), (2.0, 41)):
        music.add(tt, A.bass(M(m), 0.5, 0.6))
    sfx.add(AH1[0], P.ah(0.9, 300, 430, 0.45))
    sfx.add(AH1[1], P.ah(1.0, 340, 520, 0.55))
    # freeze: tick-tock + soft pad
    music.add(2.45, A.pad([M(53), M(57), M(60)], 2.25, 0.45))
    tt, k = 2.75, 0
    while tt < 4.4:
        sfx.add(tt, A.woodblock(k % 2 == 0, 0.8))
        tt += 0.25
        k += 1
    for tt in (2.55, 2.7):
        sfx.add(tt, A.pop(0.7))
    sfx.add(2.85, A.glock(M(91), 0.6, 0.4))
    sfx.add(4.42, A.pop(0.6))
    sfx.add(4.5, P.ah(1.0, 380, 600, 0.26))
    # ACHOO! clatter of blocks, soft bumps
    sfx.add(T_ACHOO, P.achoo(1.0, True))
    sfx.add(T_ACHOO + 0.05, A.whoosh(0.7, 0.8))
    sfx.add(T_ACHOO + 0.08, P.swish(0.6, 0.6))
    sfx.add(5.1, P.clatter(9, 0.9, 0.4))
    sfx.add(T_STAR_LAND, A.boing(0.4, 300))
    for j in range(5):
        sfx.add(5.25 + 0.04 * j, A.pop(0.35))
    for i, m in enumerate((72, 71, 69, 67)):            # "oops" tumble-down
        music.add(5.45 + i * 0.12, A.marimba(M(m), 0.4, 0.5))
    music.add(5.45, A.bass(M(43), 0.6, 0.5))
    sfx.add(T_PAT + 0.05, A.pop(0.8))
    sfx.add(T_PAT + 0.07, A.twinkle(0.4))
    # Crinkle's elbow demo
    A.strum(music, 6.3, "C", 0.55)
    music.add(6.3, A.bass(M(48), 0.5, 0.6))
    sfx.add(T_CR_UP - 0.08, A.whoosh(0.25, 0.4))
    sfx.add(T_CR_CHOO, P.achoo(0.9, False))
    A.strum(music, 6.8, "G", 0.5)
    music.add(6.8, A.bass(M(43), 0.5, 0.5))
    sfx.add(T_CR_CHOO + 0.22, A.chime_up(0.55))
    A.strum(music, 7.3, "F", 0.5)
    music.add(7.3, A.bass(M(41), 0.5, 0.5))
    for tt in (7.45, 7.65):
        sfx.add(tt, A.tap(0.4))
    # rebuild: three tosses up the scale
    for i in range(NB):
        t0 = T_REB + 0.3 * i
        sfx.add(t0, A.pop(0.5))
        sfx.add(t0 + 0.02, A.glock(M((84, 86, 88, 91)[i]), 0.5, 0.5))
        sfx.add(t0 + 0.32, P.clack(0.6))
        music.add(t0, A.pluck(M((60, 62, 64, 67)[i]), 0.3, 0.6))
    A.strum(music, 7.9, "C", 0.5)
    A.strum(music, 8.4, "G", 0.5, True)
    music.add(8.4, A.bass(M(43), 0.5, 0.5))
    # the feather drifts back: ah (1) ah (2) ah (3) CHOO into the elbow
    for i, m in enumerate((88, 86, 84, 83, 81)):
        sfx.add(9.0 + i * 0.12, A.glock(M(m), 0.5, 0.25))
    A.strum(music, 9.0, "Am", 0.45)
    music.add(9.0, A.pad([M(57), M(60), M(64)], 0.9, 0.2))
    sfx.add(T_FEATHER2, A.boop(0.5))
    for i, a in enumerate(AHS):
        sfx.add(a, P.ah(0.8 + 0.1 * i, 300 + 40 * i, 430 + 50 * i, 0.38))
        sfx.add(a + 0.02, A.glock(M((84, 88, 91)[i]), 1.0, 0.7))
        music.add(a, A.bass(M((48, 50, 52)[i]), 0.4, 0.5))
    music.add(9.75, A.pad([M(53), M(57), M(60)], 1.2, 0.18))
    sfx.add(T_SN_UP - 0.06, A.whoosh(0.22, 0.4))
    sfx.add(T_CHOO, P.achoo(1.0, False))
    sfx.add(T_CHOO + 0.08, P.clack(0.3))
    sfx.add(T_CHOO + 0.25, A.chime_up(0.6))
    A.strum(music, T_CHOO + 0.05, "C", 0.6)
    music.add(T_CHOO + 0.05, A.bass(M(48), 0.5, 0.6))
    # payoff: star on top, check, hearts
    sfx.add(T_STAR_UP, A.pop(0.6))
    sfx.add(T_STAR_UP + 0.3, A.tap(0.5))
    sfx.add(T_PLACE1, P.clack(1.0))
    sfx.add(T_CHECK, A.glock(M(96), 1.0, 0.7))
    sfx.add(T_CHECK + 0.02, A.twinkle(0.7))
    for tt, ch, up in ((11.5, "F", False), (11.75, "F", True), (12.0, "G", False), (12.25, "G", True),
                       (12.4, "C", False), (12.65, "C", True), (12.9, "Am", False), (13.15, "Am", True),
                       (13.4, "F", False), (13.65, "F", True), (13.9, "G", False), (14.15, "G", True)):
        A.strum(music, tt, ch, 0.65, up)
    for tt, m in ((11.5, 41), (12.0, 43), (12.4, 48), (12.9, 45), (13.4, 41), (13.9, 43)):
        music.add(tt, A.bass(M(m), 0.45, 0.8))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.45))
    for i in range(4):
        sfx.add(12.5 + 0.36 * i, A.clap(0.45))
    sfx.add(12.55, A.boing(0.35, 340))
    sfx.add(13.25, A.boing(0.3, 360))
    # paw-bump (signature)
    sfx.add(14.35, A.snare_roll(0.6, 0.8))
    sfx.add(T_BUMP, A.boop(0.9))
    A.jingle(music, T_BUMP + 0.02, 1.0, ending=True)
    sfx.add(T_BUMP + 0.05, A.twinkle(0.8))
    # loop: ear flick, the star is handed back, the feather floats... (leads into the jingle at 0:00)
    sfx.add(15.72, A.boing(0.3, 300))
    sfx.add(15.77, A.boing(0.3, 280))
    sfx.add(16.1, A.twinkle(0.35))
    sfx.add(16.3, A.boing(0.25, 420))
    sfx.add(16.55, A.whoosh(0.3, 0.3))
    A.strum(music, 16.3, "F", 0.5)
    music.add(16.3, A.bass(M(41), 0.5, 0.5))
    sfx.add(T_LIFT0, A.tap(0.5))
    sfx.add(T_GIVE1, A.pop(0.6))
    A.strum(music, 16.9, "G7", 0.5)
    music.add(16.9, A.bass(M(43), 0.5, 0.5))
    sfx.add(17.45, A.boing(0.3, 300))
    for i, m in enumerate((91, 89, 88, 86)):
        sfx.add(17.2 + i * 0.17, A.glock(M(m), 0.6, 0.25))
    music.add(17.3, A.pad([M(55), M(59), M(62)], 0.75, 0.22))

    m = A.reverb(music.normalized(), 0.24)
    s = A.reverb(sfx.normalized(), 0.08)
    y = 0.55 * m / max(1e-9, abs(m).max()) + 0.7 * s / max(1e-9, abs(s).max())
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.01)


# ---------------------------------------------------------------- output
def render(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    wav = os.path.join(ROOT, "build", "ep06_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep06_achoo_elbow_sneeze.mp4")
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
    times = times or [0.0, 0.85, 1.9, 3.4, 4.8, 5.0, 5.4, 6.2, 6.9, 7.5, 8.3, 9.4, 9.9, 10.75,
                      11.1, 11.8, 12.4, 13.2, 15.2, 16.6, 17.2, 17.99]
    cols = 7
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


KEYS = [(0.85, "0.9s hook: feather"), (3.4, "3.4s choice"), (5.0, "5.0s ACHOO!"), (6.2, "6.2s germs everywhere"),
        (6.95, "7.0s elbow sneeze"), (10.3, "10.3s ah 1, 2..."), (11.1, "11.1s choo in the elbow"),
        (15.2, "15.2s paw-bump")]


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
        stills(os.path.join(ROOT, "build", "ep06_stills.png"))
    elif "--keys" in sys.argv:
        os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
        key_sheet(os.path.join(ROOT, "reviews", "ep06_keys.png"))
    else:
        render(os.path.join(ROOT, "output"))
