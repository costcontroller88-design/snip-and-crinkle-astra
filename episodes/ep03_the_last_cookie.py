"""Episode 3 — The Last Cookie? 🍪

An evening kitchen (twilight wallpaper, warm pendant lamp, sunset window, gingham cloth).
One cookie is left on the plate and the cookie jar is empty. Snip AND Crinkle reach for it at
the same time. Choice: grab it (tug-of-war) or break it in half? They try grabbing: a
tug-of-war, the paws slip, both tumble back onto their soft bottoms and rock like roly-polys,
while the cookie flips into the air and lands back on the plate, wobbling like a coin.
Crinkle gets an idea (paper light bulb), breaks the cookie in half — count 1, 2 — and shows the
halves are the same (they bob like a balance and settle level, twin sparkles). He gives one
half to Snip; both munch happily (check, hearts), the signature paw-bump, and a grown-up's
hand sets down another cookie, so the last frame equals the first.

Run:  python3 episodes/ep03_the_last_cookie.py            (render -> output/)
      python3 episodes/ep03_the_last_cookie.py --stills   (contact sheet -> build/)
      python3 episodes/ep03_the_last_cookie.py --keys     (review key frames -> reviews/ep03_keys.png)
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
import props_cookie as P  # noqa: E402
import scene  # noqa: E402
from characters import Character  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, rot, seg  # noqa: E402

FPS = 30
DUR = 18.0
TY = scene.TABLE_Y
R = P.COOKIE_R
SN_HOME = 320
CR_HOME = 785                         # keeps his right arm clear of the like/comment buttons
CR_DEMO = 640                         # where Crinkle stands to break the cookie
HOLD_L, HOLD_R = 212, 148              # Crinkle's arms holding the halves up and out, clear of his face
CR_REST_L = 346                       # Crinkle's left arm hanging (== -14)
PLATE_X = 535
PLATE_Y = TY + 8
REST = (PLATE_X, TY - 14 - R)         # cookie centre standing on the plate
SN_DEMO = 292                         # Snip's spot while Crinkle demonstrates
SN_FALL = SN_HOME + 32                # where Snip lands (kept in from the left edge)

BG = P.background()
PLATE = P.plate()
COOKIE = P.cookie()
HALF = {(side, b): P.cookie_half(side, b) for side in "lr" for b in (0, 1, 2)}
CRUMBS = P.crumbs()
BULB = P.idea_bulb()
POOF = P.poof()
WOB = P.wobble_lines()
HAND = scene.grown_up_hand()
NUMS = [scene.numeral(1, (244, 112, 104)), scene.numeral(2, (255, 196, 52))]
BUB_GRAB = P.choice_bubble("grab", (240, 110, 100))
BUB_SHARE = P.choice_bubble("share", (90, 190, 120))
QMARK = icons.question()
CHECK = icons.check(130)
SPARKLE = scene.sparkle()
GLINT = scene.sparkle((255, 250, 226))
HEARTS = [scene.heart(c, 80) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120), (255, 150, 170))]
SNIP = Character("snip", 1.15)
CR = Character("crinkle", 1.2)

SNIP_BLINKS = (1.4, 6.55, 8.75, 9.85, 11.25, 14.3, 16.7)
CR_BLINKS = (1.6, 6.15, 8.95, 11.35, 13.95, 16.95)
T_GRAB, T_TUG, T_SLIP, T_LAND, T_SETTLE = 4.5, 4.76, 5.25, 5.45, 5.85
T_IDEA = 6.35
T_CRACK = 7.8
COUNTS = (8.45, 9.1)
T_SAME = 10.05
T_GIVE0, T_GIVE1 = 10.35, 10.85
BITES = (11.95, 12.45, 12.95)
T_GONE = 13.08
HEART_PLAN = ((13.2, 230, 860), (13.35, 470, 760), (13.5, 760, 700), (13.65, 380, 640))
T_HAND0, T_HAND1, T_HAND2, T_HAND3 = 16.25, 16.9, 17.0, 17.5


# ---------------------------------------------------------------- helpers (as in the reference episode)
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


def near(a, ref):
    """Same direction as angle a, unwrapped to be closest to ref (so arms never swing the long way)."""
    return a + 360 * round((ref - a) / 360)


def aim(ch, st, side, target, ref):
    sh = ch.shoulder_pt(st["x"], TY, side, st["hop"], st["lean"], st["sq"])
    a = math.degrees(math.atan2(target[0] - sh[0], target[1] - sh[1])) - st["lean"]
    return near(a, ref)


def tip(ch, st, side):
    arm = st["arm_l"] if side == "l" else st["arm_r"]
    return ch.paw_tip(st["x"], TY, side, arm, st["hop"], st["lean"], st["sq"])


def mouth(ch, st):
    return ch.mouth_pt(st["x"], TY, st["hop"], st["lean"], st["sq"], st["head_dy"], st.get("tilt", 0.0))


def tug_phase(t):
    return math.sin(2 * math.pi * (t - T_TUG) / 0.26) * ease_in_out(seg(t, T_TUG, T_TUG + 0.1))


def tug_target(t):
    """Where both paws aim during the grab/tug (the cookie's nominal centre)."""
    k = ease_out(seg(t, T_GRAB, T_TUG))
    return (lerp(REST[0], PLATE_X - 14 * tug_phase(t), k), lerp(REST[1], 1150, k))


# ---------------------------------------------------------------- Snip
def snip_state(t):
    if frozen(t):
        return snip_state(2.4999)
    s = dict(x=SN_HOME, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, arm_l=-14.0, arm_r=14.0, eyes="normal",
             mouth="w", look=(0, 0), head_dy=0.0, ears=[0.0, 0.0], ear_stretch=1.0)
    idle_ear = 2.0 * math.sin(2 * math.pi * t / 3.0)

    if t < 1.0:                       # HOOK: paw creeps toward the last cookie
        p = ease_in_out(seg(t, 0.0, 1.0))
        s.update(lean=lerp(-6, -9, p), arm_r=lerp(26, 42, p), eyes="wide", mouth="o", look=(7, 4))
    elif t < 2.5:                     # DESIRE: sparkly eyes... then a side-eye: Crinkle wants it too!
        s.update(lean=-9, arm_r=42, eyes="sparkle", mouth="yum", look=(6, 4), tilt=-5 * ease_out(seg(t, 1.0, 1.4)))
        e = spring(t, 1.0, 10, 4.0, 3.0)
        s["ears"] = [e, -e]
        if 1.75 <= t < 2.2:
            s.update(eyes="wide", mouth="o", look=(10, -3))
            s["head_dy"] = -10 * math.sin(math.pi * seg(t, 1.75, 1.95))
    elif t < T_SLIP:                  # GRAB + TUG-OF-WAR
        k = ease_out(seg(t, T_GRAB, T_TUG))
        ph = tug_phase(t)
        s.update(x=SN_HOME + 6 * k, lean=lerp(-9, 7 + 7 * ph, k), eyes="wide" if t < T_TUG else "closed",
                 mouth="O" if t < T_TUG else "flat", look=(7, 0))
        s["ears"] = [lerp(0, 16 + 4 * ph, k), lerp(0, 10 + 4 * ph, k)]
        s["arm_l"] = lerp(-14, -40, k)
        s["arm_r"] = aim(SNIP, s, "r", (tug_target(t)[0] - 62, tug_target(t)[1] + 6), 60)
        s["arm_r"] = lerp(42, s["arm_r"], k)
    elif t < 6.3:                     # SLIP! tumble back onto a soft bottom, rock like a roly-poly
        if t < T_LAND:
            p = ease_out(seg(t, T_SLIP, T_LAND))
            s.update(x=lerp(SN_HOME + 6, SN_FALL, p), lean=lerp(14, 26, p), hop=46 * math.sin(math.pi * p),
                     eyes="wide", mouth="O", look=(4, -6))
            s["arm_l"], s["arm_r"] = lerp(-40, -150, p), lerp(70, 150, p)
            s["ears"] = [lerp(18, -14, p), lerp(12, 22, p)]
            s["ear_stretch"] = lerp(1.0, 1.2, p)
        else:
            dt = t - T_LAND
            s["x"] = SN_FALL
            s["lean"] = 26 * math.exp(-4.2 * dt) * math.cos(2 * math.pi * 1.45 * dt)
            s["sq"] = 1 - 0.14 * math.exp(-12 * dt)
            down = ease_in_out(seg(t, 5.5, 5.85))
            s["arm_l"], s["arm_r"] = lerp(-150, -14, down), lerp(150, 14, down)
            s["ear_stretch"] = lerp(1.2, 1.0, ease_out(seg(t, 5.45, 5.8)))
            e = spring(t, T_LAND, 16, 3.5, 3.0)
            s["ears"] = [e, -e]
            if t < 5.75:
                s.update(eyes="wide", mouth="O", look=(4, -4))
            elif t < 6.05:
                s.update(eyes="wide", mouth="o", look=(8, 5))           # the cookie is back on the plate!?
            else:
                droop = 18 * ease_out(seg(t, 6.05, 6.25))
                s.update(eyes="normal", mouth="wobble", look=(9, -2))   # sheepish look at Crinkle
                s["ears"] = [e + droop, -e - droop]
    elif t < T_CRACK:                 # Crinkle's idea: Snip watches, curious
        p = ease_in_out(seg(t, 6.3, 6.7))
        s["x"] = lerp(SN_FALL, SN_DEMO, p)
        droop = 18 * (1 - ease_in_out(seg(t, 6.4, 6.8)))
        s["ears"] = [droop, -droop]
        if t < 6.45:
            s.update(eyes="normal", mouth="wobble", look=(9, -2))
        elif t < 7.05:
            s.update(eyes="wide", mouth="o", look=(8, -8), tilt=6 * ease_out(seg(t, 6.45, 6.7)))
            e = spring(t, 6.45, 9, 5.0, 4.0)
            s["ears"] = [droop + e, -droop - e]
        else:
            s.update(eyes="normal", mouth="w", look=(9, -1), tilt=lerp(6, 3, seg(t, 7.05, 7.3)))
            s["head_dy"] = 8 * math.sin(math.pi * seg(t, 7.3, 7.6))
    elif t < T_GIVE0:                 # CRACK, then count 1-2 and compare
        s.update(x=SN_DEMO, eyes="wide" if t < 8.2 else "normal", mouth="o" if t < 8.2 else "w", look=(8, -7))
        e = spring(t, T_CRACK, 10, 5.0, 4.0)
        s["ears"] = [e, -e]
        s["ear_stretch"] = 1 + 0.12 * math.sin(math.pi * seg(t, T_CRACK, T_CRACK + 0.3))
        for c in COUNTS:
            h, sq = hop_curve(t, c, c + 0.32, 1, 18)
            if h or sq != 1.0:
                s["hop"], s["sq"] = h, sq
            if 0 <= t - c < 0.3:
                s["mouth"] = "o"
            e = spring(t, c, 7, 5.0, 5.0)
            s["ears"][0] += e
            s["ears"][1] -= e
        if t >= T_SAME - 0.05:        # "they're the same!"
            s.update(eyes="sparkle", mouth="grin", look=(8, -5))
            s["head_dy"] = 12 * math.sin(math.pi * seg(t, T_SAME, T_SAME + 0.25))
    elif t < 11.6:                    # receives the half from Crinkle
        s.update(x=SN_DEMO, eyes="sparkle", mouth="grin" if t > T_GIVE1 else "yum", look=(8, 0))
        if t < T_GIVE1:
            target = handoff_pt(t)
            s["arm_r"] = lerp(14, aim(SNIP, s, "r", target, 60), ease_in_out(seg(t, T_GIVE0, T_GIVE0 + 0.25)))
        else:
            h, sq = hop_curve(t, 10.95, 11.27, 1, 22)
            s.update(hop=h, sq=sq, eyes="happy")
            a_give = aim(SNIP, dict(s, hop=0.0, sq=1.0), "r", handoff_pt(T_GIVE1), 60)
            s["arm_r"] = lerp(a_give, 150, ease_in_out(seg(t, T_GIVE1, T_GIVE1 + 0.3)))
            e = spring(t, T_GIVE1, 12, 5.0, 3.5)
            s["ears"] = [e, -e]
    elif t < T_GONE + 0.15:           # MUNCH
        s.update(x=SN_DEMO, eyes="happy", mouth="blow", look=(6, 4))
        to_mouth = ease_in_out(seg(t, 11.6, 11.85))
        s["arm_r"] = lerp(150, 212, to_mouth)
        if t > T_GONE:
            s["arm_r"] = lerp(212, 14, ease_in_out(seg(t, T_GONE, T_GONE + 0.3)))
        s["mouth"] = munch_mouth(t, 0.0)
        s["eyes"] = "closed" if any(0 <= t - b < 0.25 for b in BITES) else "happy"
        s["head_dy"] = sum(10 * math.sin(math.pi * seg(t, b, b + 0.2)) for b in BITES)
    elif t < 14.6:                    # yum! happy hop
        h, sq = hop_curve(t, 13.55, 13.87, 1, 26)
        s.update(x=SN_DEMO, hop=h, sq=sq, eyes="happy", mouth="grin" if t > 13.4 else "blow")
        s["arm_r"] = lerp(212, 14, ease_in_out(seg(t, T_GONE, T_GONE + 0.3)))
        e = spring(t, 13.5, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
    elif t < 16.0:                    # PAW-BUMP
        h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
        s.update(x=lerp(SN_DEMO, 362, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq, eyes="happy",
                 mouth="grin")
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_r"] = lerp(lerp(14, -6, wind), 165, swing)
        e = spring(t, 15.45, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
    elif t < 17.0:                    # hop home, look up at the grown-up's hand bringing a cookie
        h, sq = hop_curve(t, 16.0, 16.45, 1, 30)
        s.update(x=lerp(362, SN_HOME, ease_in_out(seg(t, 16.0, 16.45))), hop=h, sq=sq, lean=0,
                 eyes="happy" if t < 16.55 else "normal", mouth="grin" if t < 16.55 else "w",
                 look=(7, 0) if t < 16.55 else (5, -7))
        s["arm_r"] = lerp(165, 14, ease_out(seg(t, 16.0, 16.3)))
    else:                             # ANOTHER last cookie... eyes go wide, paw starts creeping (== frame 0)
        p = ease_in_out(seg(t, 17.1, 18.0))
        s.update(lean=lerp(0, -6, p), arm_r=lerp(14, 26, ease_in_out(seg(t, 17.35, 18.0))),
                 eyes="wide" if t > 17.15 else "normal", mouth="o" if t > 17.15 else "w",
                 look=(7, 4) if t > 17.15 else (5, -7))
        e = spring(t, 17.15, 9, 5.0, 4.0) * (1 - ease_in_out(seg(t, 17.55, 18.0)))
        s["ears"] = [e, -e]

    s["ears"][0] += idle_ear
    s["ears"][1] -= idle_ear
    if s["hop"] == 0:
        s["sq"] *= breath(t)
    return s


def munch_mouth(t, delay):
    for b in BITES:
        b += delay
        if b - 0.14 <= t < b:
            return "O"
        if b <= t < b + 0.12:
            return "o"
    return "blow"


# ---------------------------------------------------------------- Crinkle
def crinkle_state(t):
    if frozen(t):
        return crinkle_state(2.4999)
    s = dict(x=CR_HOME, hop=0.0, sq=1.0, lean=0.0, arm_l=CR_REST_L, arm_r=2.0, eyes="normal", mouth="smile",
             look=(0, 0), head_dy=0.0)
    if t < 1.0:                       # HOOK: his paw creeps in too
        p = ease_in_out(seg(t, 0.0, 1.0))
        s.update(lean=lerp(5, 8, p), arm_l=lerp(336, 318, p), eyes="wide", mouth="o", look=(-7, 4))
    elif t < 2.5:                     # DESIRE
        s.update(lean=8, arm_l=318, eyes="sparkle", mouth="yum", look=(-6, 4))
        s["head_dy"] = 6 * math.sin(math.pi * seg(t, 1.1, 1.5))
        if 1.8 <= t < 2.25:
            s.update(eyes="wide", mouth="o", look=(-10, -3))
    elif t < T_SLIP:                  # GRAB + TUG
        k = ease_out(seg(t, T_GRAB, T_TUG))
        ph = tug_phase(t)
        s.update(x=CR_HOME, lean=lerp(8, -7 + 7 * ph, k), eyes="wide" if t < T_TUG else "closed",
                 mouth="O" if t < T_TUG else "flat", look=(-7, 0))
        s["arm_r"] = lerp(2, 40, k)
        a = aim(CR, s, "l", (tug_target(t)[0] + 62, tug_target(t)[1] + 6), 300)
        s["arm_l"] = lerp(318, a, k)
    elif t < 6.3:                     # SLIP! plop onto his soft bottom, rock back up
        if t < T_LAND:
            p = ease_out(seg(t, T_SLIP, T_LAND))
            s.update(x=CR_HOME, lean=lerp(-14, -18, p), hop=34 * math.sin(math.pi * p),
                     eyes="wide", mouth="O", look=(-4, -6))
            s["arm_l"], s["arm_r"] = lerp(290, 200, p), lerp(40, 160, p)
        else:
            dt = t - T_LAND
            s["x"] = CR_HOME
            s["lean"] = -18 * math.exp(-4.2 * dt) * math.cos(2 * math.pi * 1.45 * dt)
            s["sq"] = 1 - 0.12 * math.exp(-12 * dt)
            down = ease_in_out(seg(t, 5.5, 5.85))
            s["arm_l"], s["arm_r"] = lerp(200, CR_REST_L, down), lerp(160, 2, down)
            if t < 5.75:
                s.update(eyes="wide", mouth="O", look=(-4, -4))
            elif t < 6.05:
                s.update(eyes="wide", mouth="o", look=(-8, 5))
            else:
                s.update(eyes="normal", mouth="wobble", look=(-9, -2))
    elif t < 6.75:                    # IDEA! (light bulb)
        h, sq = hop_curve(t, T_IDEA, T_IDEA + 0.3, 1, 22)
        s.update(x=CR_HOME, hop=h, sq=sq, eyes="sparkle" if t >= T_IDEA else "normal",
                 mouth="grin" if t >= T_IDEA else "wobble", look=(-6, -6) if t >= T_IDEA else (-9, -2))
        s["arm_r"] = lerp(2, 165, ease_out_back(seg(t, T_IDEA, T_IDEA + 0.25)))
        s["arm_r"] = lerp(s["arm_r"], 2, ease_in_out(seg(t, 6.6, 6.75)))
    elif t < T_CRACK:                 # picks up the cookie and shows it to Snip
        s["x"] = lerp(CR_HOME, CR_DEMO, ease_in_out(seg(t, 6.75, 7.05)))
        bend = ease_in_out(seg(t, 6.85, 7.0)) * (1 - ease_in_out(seg(t, 7.05, 7.25)))
        s["lean"] = 14 * bend + 4 * ease_in_out(seg(t, 7.25, 7.45))
        s.update(eyes="normal", mouth="smile", look=(-6, 4) if t < 7.2 else (-8, -1))
        c = cookie_center_whole(t)
        s["arm_l"] = lerp(CR_REST_L, aim(CR, s, "l", (c[0] - R + 16, c[1] + 10), 360), ease_in_out(seg(t, 6.8, 7.0)))
        s["arm_r"] = lerp(2, aim(CR, s, "r", (c[0] + R - 16, c[1] + 10), 0), ease_in_out(seg(t, 6.8, 7.0)))
        if t > 7.5:                   # squeeze... (gentle "hmm")
            s.update(eyes="closed", mouth="o")
            s["head_dy"] = 4 * math.sin(math.pi * seg(t, 7.5, T_CRACK))
    elif t < T_GIVE0:                 # CRACK! lift the halves: 1, 2 ... and they balance level
        s.update(x=CR_DEMO, eyes="wide" if t < 8.1 else "happy", mouth="o" if t < 8.1 else "grin")
        c = cookie_center_whole(T_CRACK - 0.001)
        st = dict(s, lean=4.0)
        a_l0 = aim(CR, st, "l", (c[0] - R + 16, c[1] + 10), HOLD_L)
        a_r0 = aim(CR, st, "r", (c[0] + R - 16, c[1] + 10), HOLD_R)
        up = ease_in_out(seg(t, 8.0, 8.35))
        s["lean"] = lerp(4, 0, up)
        bob_l, bob_r = balance_bob(t)
        s["arm_l"] = lerp(a_l0, HOLD_L, up) + bob_l
        s["arm_r"] = lerp(a_r0, HOLD_R, up) + bob_r
        if COUNTS[0] <= t < COUNTS[1]:
            s["look"] = (-6, -6)
        elif COUNTS[1] <= t < 9.55:
            s["look"] = (6, -6)
        elif t >= 9.55:
            s["look"] = (-3, -5) if t < T_SAME else (-8, -2)
        for c_t in COUNTS:
            s["head_dy"] += 10 * math.sin(math.pi * seg(t, c_t, c_t + 0.3))
            if 0 <= t - c_t < 0.3:
                s["mouth"] = "o"
        s["head_dy"] += 12 * math.sin(math.pi * seg(t, T_SAME, T_SAME + 0.25))
    elif t < 11.6:                    # gives the "1" half to Snip, keeps the "2" half
        s.update(x=CR_DEMO, eyes="happy", mouth="grin", look=(-8, 0))
        give = ease_in_out(seg(t, T_GIVE0, T_GIVE1))
        back = ease_in_out(seg(t, T_GIVE1, T_GIVE1 + 0.35))
        s["lean"] = 6 * give * (1 - back)
        a = aim(CR, s, "l", handoff_pt(min(t, T_GIVE1)), 270)
        s["arm_l"] = lerp(lerp(HOLD_L, a, give), CR_REST_L, back)
        s["arm_r"] = HOLD_R
    elif t < T_GONE + 0.15:           # MUNCH
        s.update(x=CR_DEMO, eyes="happy", mouth="blow", look=(-6, 4))
        s["arm_r"] = lerp(HOLD_R, 214, ease_in_out(seg(t, 11.6, 11.85)))
        if t > T_GONE:
            s["arm_r"] = lerp(214, 2, ease_in_out(seg(t, T_GONE, T_GONE + 0.3)))
        s["mouth"] = munch_mouth(t, 0.08)
        s["eyes"] = "closed" if any(0 <= t - b - 0.08 < 0.25 for b in BITES) else "happy"
        s["head_dy"] = sum(10 * math.sin(math.pi * seg(t, b + 0.08, b + 0.28)) for b in BITES)
    elif t < 14.6:                    # yum! happy hop
        h, sq = hop_curve(t, 13.6, 13.92, 1, 24)
        s.update(x=CR_DEMO, hop=h, sq=sq, eyes="happy", mouth="grin" if t > 13.45 else "blow", look=(-6, 2))
        s["arm_r"] = lerp(214, 2, ease_in_out(seg(t, T_GONE, T_GONE + 0.3)))
    elif t < 16.0:                    # PAW-BUMP
        h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
        s.update(x=lerp(CR_DEMO, 677, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq, eyes="happy", mouth="grin")
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_l"] = lerp(lerp(CR_REST_L, 360, wind), 198, swing)
    elif t < 17.0:                    # hops back to his spot
        h, sq = hop_curve(t, 16.05, 16.75, 2, 30)
        s.update(x=lerp(677, CR_HOME, ease_in_out(seg(t, 16.05, 16.75))), hop=h, sq=sq, eyes="happy",
                 mouth="grin", look=(-6, -4))
        s["arm_l"] = lerp(198, CR_REST_L, ease_out(seg(t, 16.0, 16.25)))
        if t > 16.75:
            s.update(eyes="normal", mouth="smile", look=(-7, -6))
    else:                             # ANOTHER cookie! his paw starts creeping too (== frame 0)
        p = ease_in_out(seg(t, 17.1, 18.0))
        s.update(lean=lerp(0, 5, p), arm_l=lerp(CR_REST_L, 336, ease_in_out(seg(t, 17.35, 18.0))),
                 eyes="wide" if t > 17.18 else "normal", mouth="o" if t > 17.18 else "smile",
                 look=(-7, 4) if t > 17.18 else (-7, -6))
        s["head_dy"] = -10 * math.sin(math.pi * seg(t, 17.18, 17.4))
    if s["hop"] == 0:
        s["sq"] *= breath(t + 0.7, 2.25, 0.01)
    return s


def balance_bob(t):
    """Crinkle's arms bob like a balance scale, then settle level: the halves weigh the same."""
    if t < 9.55:
        return 0.0, 0.0
    p = seg(t, 9.55, T_SAME)
    a = 16 * math.sin(2 * math.pi * 2 * p) * (1 - p)
    return a, a


# ---------------------------------------------------------------- the cookie
def cookie_center_whole(t):
    """Centre of the whole cookie while Crinkle picks it up and holds it at his chin."""
    hold = (CR_DEMO, 1148)
    k = ease_in_out(seg(t, 7.0, 7.25))
    c = (lerp(REST[0], hold[0], k), lerp(REST[1], hold[1], k))
    if t > 7.5:
        c = (c[0] + 1.6 * math.sin(t * 90), c[1])
    return c


def handoff_pt(t):
    return (450, 1140)


def half_pivot(side, centroid, angle):
    """Pivot (break-edge middle) for a half whose visual centre should land on `centroid`."""
    off = -P.HALF_CENTROID if side == "l" else P.HALF_CENTROID
    ox, oy = rot(off, 0, angle)
    return centroid[0] - ox, centroid[1] - oy


def cookie_items(t, sn, cr):
    """What to draw for the cookie: list of (sprite, pivot_xy, angle, scale, sx, sy)."""
    if t < T_GRAB:
        return [(COOKIE, REST, 0.0, 1.0, 1.0, 1.0)]
    if t < T_SLIP:
        k = ease_out(seg(t, T_GRAB, T_TUG))
        a, b = tip(SNIP, sn, "r"), tip(CR, cr, "l")
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 4)
        c = (lerp(REST[0], mid[0], k), lerp(REST[1], mid[1], k))
        strain = abs(tug_phase(t)) * (1 if t > T_TUG else 0)
        return [(COOKIE, c, 3 * tug_phase(t), 1.0, 1 + 0.05 * strain, 1 - 0.04 * strain)]
    if t < T_SETTLE:                  # flips up and lands back on the plate
        s0 = cookie_items(T_SLIP - 1e-4, snip_state(T_SLIP - 1e-4), crinkle_state(T_SLIP - 1e-4))[0][1]
        p = seg(t, T_SLIP, T_SETTLE)
        x = lerp(s0[0], REST[0], p)
        y = lerp(s0[1], REST[1], p) - 4 * 470 * p * (1 - p)
        return [(COOKIE, (x, y), 720 * ease_out(p), 1.0, 1.0, 1.0)]
    if t < 6.85:                      # rocks to a stop like a coin, upright on the plate
        dt = t - T_SETTLE
        ang = 16 * math.exp(-5.5 * dt) * math.sin(2 * math.pi * 3.2 * dt)
        bottom = (REST[0], REST[1] + R)
        ox, oy = rot(0, -R, ang)
        return [(COOKIE, (bottom[0] + ox, bottom[1] + oy), ang, 1.0, 1.0, 1.0)]
    if t < T_CRACK:
        return [(COOKIE, cookie_center_whole(t), 0.0, 1.0, 1.0, 1.0)]
    if t < T_GONE + 0.25:
        return halves(t, sn, cr)
    if t < T_HAND0:
        return []
    if t < T_HAND1:
        fy = hand_y(t)
        return [(COOKIE, (REST[0], fy + R - 22), 0.0, 1.0, 1.0, 1.0)]
    return [(COOKIE, REST, 0.0, 1.0, 1.0, 1.0)]


def hand_y(t):
    """Fingertip height of the grown-up's hand (None when off screen)."""
    land = REST[1] - R + 22
    if t < T_HAND0 or t >= T_HAND3:
        return None
    if t < T_HAND1:
        return lerp(-650, land, ease_out(seg(t, T_HAND0, T_HAND1)))
    if t < T_HAND2:
        return land
    return lerp(land, -700, ease_in_out(seg(t, T_HAND2, T_HAND3)))


def bites_at(t, delay=0.0):
    return sum(1 for b in BITES[:2] if t >= b + delay)


def halves(t, sn, cr):
    out = []
    c0 = cookie_center_whole(T_CRACK - 0.001)
    lt, rt = tip(CR, cr, "l"), tip(CR, cr, "r")
    if t < 8.0:                       # snap! the halves open like a book
        p = ease_out(seg(t, T_CRACK, T_CRACK + 0.18))
        for side, sgn in (("l", -1), ("r", 1)):
            piv = (c0[0] + sgn * 16 * p, c0[1] + 4 * p)
            out.append((HALF[(side, 0)], piv, -sgn * 9 * p, 1.0, 1.0, 1.0))
        return out
    up = ease_in_out(seg(t, 8.0, 8.35))
    for side, sgn, tp in (("l", -1, lt), ("r", 1, rt)):
        start = (c0[0] + sgn * 16 + sgn * P.HALF_CENTROID, c0[1] + 4)
        held = (tp[0], tp[1] - 52)
        cen = (lerp(start[0], held[0], up), lerp(start[1], held[1], up))
        ang = -sgn * 9 * (1 - up)
        sc = 1.0
        for i, c_t in enumerate(COUNTS):          # each half hops as it is counted
            if (side == "l" and i == 0) or (side == "r" and i == 1):
                cen = (cen[0], cen[1] - 34 * math.sin(math.pi * seg(t, c_t, c_t + 0.3)))
                sc = 1 + 0.12 * math.sin(math.pi * seg(t, c_t, c_t + 0.3))
        b = 0
        if side == "l" and t >= T_GIVE0:        # Snip's half: handed over, then munched
            give = ease_in_out(seg(t, T_GIVE0, T_GIVE1))
            cen_g = (handoff_pt(t)[0], handoff_pt(t)[1] - 46)
            cen = (lerp(cen[0], cen_g[0], give), lerp(cen[1], cen_g[1], give))
            if t >= T_GIVE1:
                st = tip(SNIP, sn, "r")
                hold = (st[0], st[1] - 46)
                if t >= 11.6:
                    m = mouth(SNIP, sn)
                    k = ease_in_out(seg(t, 11.6, 11.85))
                    hold = (lerp(hold[0], lerp(st[0], m[0], 0.55), k), lerp(hold[1], lerp(st[1], m[1], 0.55) + 6, k))
                    ang = lerp(0, -28, k)
                cen = hold
            b = bites_at(t)
            if t >= BITES[2]:
                sc *= 1 - ease_in_out(seg(t, BITES[2], BITES[2] + 0.12))
        if side == "r" and t >= 11.6:          # Crinkle's half to his mouth
            m = mouth(CR, cr)
            k = ease_in_out(seg(t, 11.6, 11.85))
            target = (lerp(tp[0], m[0], 0.5), lerp(tp[1], m[1], 0.5) + 4)
            cen = (lerp(held[0], target[0], k), lerp(held[1], target[1], k))
            ang = lerp(0, 150, k)
            b = bites_at(t, 0.08)
            if t >= BITES[2] + 0.08:
                sc *= 1 - ease_in_out(seg(t, BITES[2] + 0.08, BITES[2] + 0.2))
        if sc > 0.02:
            out.append((HALF[(side, b)], half_pivot(side, cen, ang), ang, sc, 1.0, 1.0))
    return out


# ---------------------------------------------------------------- crumbs
_CRUMB_CACHE = {}


def crumb_particles(t0, origin, n, seed, spread=1.0):
    key = (t0, origin, n, seed)
    if key not in _CRUMB_CACHE:
        import random
        rnd = random.Random(seed)
        parts = []
        for i in range(n):
            ang = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05)
            sp = rnd.uniform(220, 520) * spread
            parts.append((rnd.choice(range(len(CRUMBS))), origin[0] + rnd.uniform(-30, 30),
                          origin[1] + rnd.uniform(-20, 20), sp * math.cos(ang), sp * math.sin(ang),
                          rnd.uniform(-400, 400), rnd.uniform(0.6, 1.1)))
        _CRUMB_CACHE[key] = parts
    return _CRUMB_CACHE[key]


def draw_crumbs(f, t, t0, origin, n, seed, spread=1.0, life=0.9):
    if not (t0 <= t < t0 + life):
        return
    dt = t - t0
    for (k, x, y, vx, vy, spin, sc) in crumb_particles(t0, origin, n, seed, spread):
        px = x + vx * dt
        py = y + vy * dt + 0.5 * 1900 * dt * dt
        if py > TY - 6:
            py = TY - 6
        place(f, CRUMBS[k], (px, py), angle=spin * dt, scale=sc, alpha=1 - ease_in_out(seg(t, t0 + life - 0.3, t0 + life)))


# ---------------------------------------------------------------- frame
def render_frame(t):
    f = BG.copy()
    sn = snip_state(t)
    cr = crinkle_state(t)
    place(f, PLATE, (PLATE_X, PLATE_Y))

    snip_blink = blinking(t, SNIP_BLINKS) and not frozen(t)
    SNIP.draw(f, sn["x"], TY, hop=sn["hop"], lean=sn["lean"], head_tilt=sn["tilt"], arm_l=sn["arm_l"],
              arm_r=sn["arm_r"], eyes=sn["eyes"], mouth=sn["mouth"], look=sn["look"], squash=sn["sq"],
              head_dy=sn["head_dy"], blink=snip_blink, ears=tuple(sn["ears"]), ear_stretch=sn["ear_stretch"])
    CR.draw(f, cr["x"], TY, hop=cr["hop"], lean=cr["lean"], arm_l=cr["arm_l"], arm_r=cr["arm_r"],
            eyes=cr["eyes"], mouth=cr["mouth"], look=cr["look"], squash=cr["sq"], head_dy=cr["head_dy"],
            blink=blinking(t, CR_BLINKS) and not frozen(t))

    # the cookie (lesson-critical) is always drawn IN FRONT of both characters
    for spr, piv, ang, sc, sx, sy in cookie_items(t, sn, cr):
        place(f, spr, piv, angle=ang, scale=sc, sx=sx, sy=sy)

    # tug-of-war: gripping paws in front of the cookie
    if T_GRAB + 0.08 <= t < T_SLIP:
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], TY, "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])
        place(f, CR.arm_l, CR.shoulder_pt(cr["x"], TY, "l", cr["hop"], cr["lean"], cr["sq"]),
              angle=cr["arm_l"] + cr["lean"])
    # paw-bump: both touching paws in front
    if 14.95 <= t < 16.1:
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], TY, "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])
        place(f, CR.arm_l, CR.shoulder_pt(cr["x"], TY, "l", cr["hop"], cr["lean"], cr["sq"]),
              angle=cr["arm_l"] + cr["lean"])

    # the grown-up's hand sets down a new cookie (loop)
    hy = hand_y(t)
    if hy is not None:
        place(f, HAND, (REST[0], hy))

    # desire: the cookie glints
    for t0, dx, dy, sc in ((1.1, 38, -40, 0.32), (1.55, -42, 10, 0.24), (2.0, 20, 38, 0.2)):
        if t0 <= t < t0 + 0.5:
            k = math.sin(math.pi * seg(t, t0, t0 + 0.5))
            place(f, GLINT, (REST[0] + dx, REST[1] + dy), scale=sc * k, angle=(t - t0) * 120)

    # tug strain lines
    if T_TUG <= t < T_SLIP:
        c = cookie_items(t, sn, cr)[0][1]
        j = 3 * math.sin(t * 70)
        for sgn in (-1, 1):
            place(f, WOB, (c[0] + sgn * (R + 26) + j, c[1] - R - 10), scale=0.8, angle=sgn * 20)

    # soft-landing puffs
    if T_LAND - 0.02 <= t < 6.0:
        k = pop_scale(t, T_LAND - 0.02, 0.2)
        a = 1 - ease_in_out(seg(t, 5.7, 6.0))
        place(f, POOF, (sn["x"] - 70, TY + 6), scale=0.9 * k, alpha=a)
        place(f, POOF, (cr["x"] + 80, TY + 6), scale=0.9 * k, alpha=a)

    # idea bulb
    if T_IDEA <= t < 6.95:
        k = pop_scale(t, T_IDEA, 0.25) * (1 - ease_in_out(seg(t, 6.75, 6.95)))
        hp = CR.head_pivot(cr["x"], TY, cr["hop"], cr["lean"], cr["sq"], cr["head_dy"])
        place(f, BULB, (hp[0] - 150, hp[1] - 400), scale=0.8 * k, angle=10 + 6 * math.sin((t - T_IDEA) * 9))  # clear of the wall picture

    # crumbs: the crack and every bite
    draw_crumbs(f, t, T_CRACK, (CR_DEMO, 1150), 12, 7, 1.0, 0.9)
    for i, b in enumerate(BITES):
        m = mouth(SNIP, snip_state(b))
        draw_crumbs(f, t, b, (m[0] + 30, m[1] + 30), 5, 20 + i, 0.6, 0.6)
        m = mouth(CR, crinkle_state(b + 0.08))
        draw_crumbs(f, t, b + 0.08, (m[0] + 30, m[1] + 30), 5, 40 + i, 0.6, 0.6)

    # counting numerals over each half
    for i, c_t in enumerate(COUNTS):
        if c_t <= t < T_GIVE0 + 0.2:
            out = 1 - ease_in_out(seg(t, T_GIVE0, T_GIVE0 + 0.2))
            x = (480, 800)[i]
            place(f, NUMS[i], (x, 660), scale=0.8 * pop_scale(t, c_t, 0.28) * out, angle=(-6, 6)[i] + 3 * math.sin(t * 6 + i))

    # same size! twin sparkles on both halves
    if T_SAME <= t < T_SAME + 0.6:
        for spr, piv, ang, sc, sx, sy in cookie_items(t, sn, cr):
            k = math.sin(math.pi * seg(t, T_SAME, T_SAME + 0.6))
            place(f, SPARKLE, (piv[0], piv[1] - 70), scale=0.36 * k, angle=(t - T_SAME) * 90)

    if 11.45 <= t < 12.3:
        place(f, CHECK, (470, 600), scale=pop_scale(t, 11.45, 0.25) * (1 - ease_in_out(seg(t, 12.05, 12.3))))

    for i, (t0, x, y) in enumerate(HEART_PLAN):
        if t0 <= t < 14.6:
            p = seg(t, t0, 14.6)
            place(f, HEARTS[i], (x + 10 * math.sin(t * 3 + i), y - 160 * p), scale=pop_scale(t, t0, 0.25),
                  alpha=1 - ease_in_out(seg(t, 14.2, 14.6)), angle=10 * math.sin(t * 2.5 + i))

    if 15.45 <= t < 16.2:
        sn_tip = SNIP.paw_tip(sn["x"], TY, "r", sn["arm_r"], sn["hop"], sn["lean"], sn["sq"])
        cr_tip = CR.paw_tip(cr["x"], TY, "l", cr["arm_l"], cr["hop"], cr["lean"], cr["sq"])
        mid = ((sn_tip[0] + cr_tip[0]) / 2, (sn_tip[1] + cr_tip[1]) / 2 - 10)
        place(f, SPARKLE, (mid[0], mid[1] - 35), scale=pop_scale(t, 15.45, 0.22) * 0.55, angle=(t - 15.45) * 60,
              alpha=1 - ease_in_out(seg(t, 15.9, 16.2)))

    # FREEZE: dim + choice bubbles
    if 2.5 <= t < 4.6:
        dim = 0.32 * ease_in_out(seg(t, 2.5, 2.8)) * (1 - ease_in_out(seg(t, 4.35, 4.6)))
        if dim > 0.01:
            shade = Image.new("RGBA", f.size, (30, 26, 52, int(255 * dim)))
            f.alpha_composite(shade)
        gone = 1 - ease_in_out(seg(t, 4.4, 4.55))
        pulse_a = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 2.95) / 1.0))
        pulse_b = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 3.45) / 1.0))
        place(f, BUB_GRAB, (300, 640), scale=pop_scale(t, 2.55) * gone * (pulse_a if t > 2.95 else 1))
        place(f, BUB_SHARE, (780, 640), scale=pop_scale(t, 2.7) * gone * (pulse_b if t > 3.45 else 1))
        place(f, QMARK, (540, 540), scale=pop_scale(t, 2.85, 0.25) * gone, angle=8 * math.sin(t * 4))

    return camera(f, t)


CAM0 = (1.6, 548, 1185)
CAM_KEYS = [
    (0.0,) + CAM0, (1.0, 1.63, 548, 1185), (1.7, 1.12, 540, 1060), (2.4, 1.12, 540, 1060),
    (2.8, 1.0, 540, 960), (4.6, 1.0, 540, 960), (4.95, 1.06, 545, 1020), (5.1, 1.06, 545, 1020),
    (5.45, 1.0, 540, 960),            # only a gentle push-in on the tug, so the tumble stays in frame
    (7.2, 1.0, 540, 960), (7.55, 1.18, 600, 1060), (8.05, 1.18, 600, 1060),
    (8.5, 1.0, 540, 960), (9.6, 1.0, 540, 960), (9.9, 1.08, 590, 960), (10.4, 1.08, 590, 960),
    (10.7, 1.0, 540, 960), (11.6, 1.0, 540, 960), (11.9, 1.1, 480, 1050), (13.1, 1.1, 480, 1050),
    (13.4, 1.0, 540, 960), (15.2, 1.0, 540, 960), (15.45, 1.12, 520, 1060), (15.9, 1.12, 520, 1060),
    (16.3, 1.0, 540, 960), (17.0, 1.0, 540, 960), (DUR,) + CAM0]


def camera(f, t):
    z, cx, cy = 1.0, 540, 960
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
    for t0, d, amp in ((T_LAND, 0.36, 6), (T_CRACK, 0.24, 4)):
        if t0 <= t < t0 + d:      # little bump shakes (eased in and out, so no hard jump)
            k = math.sin(math.pi * seg(t, t0, t0 + d))
            cx += amp * k * math.sin(t * 95)
            cy += amp * 0.8 * k * math.cos(t * 81)
            z = max(z, 1 + 0.02 * k)
    if z < 1.001:
        return f
    w, h = scene.W / z, scene.H / z
    left = min(max(cx - w / 2, 0), scene.W - w)
    top = min(max(cy - h / 2, 0), scene.H - h)
    return f.resize((scene.W, scene.H), Image.BICUBIC, box=(left, top, left + w, top + h))


# ---------------------------------------------------------------- audio
def build_audio(path):
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    M = A.midi
    # hook + desire (evening: a gentle F - C - G turn)
    A.jingle(music, 0.02)
    for tt, ch, up in ((1.0, "F", False), (1.25, "F", True), (1.5, "C", False), (1.75, "C", True),
                       (2.0, "G", False), (2.25, "G", True)):
        A.strum(music, tt, ch, 0.65, up)
    for tt, m in ((1.0, 41), (1.5, 48), (2.0, 43)):
        music.add(tt, A.bass(M(m), 0.5, 0.7))
    sfx.add(1.1, A.twinkle(0.8))
    for tt, m in ((1.75, 79), (1.82, 83)):        # "hm? you too?"
        sfx.add(tt, A.marimba(M(m), 0.4, 0.6))
    sfx.add(2.4, A.pop(0.6))
    # freeze: tick-tock + soft pad
    music.add(2.55, A.pad([M(53), M(57), M(60)], 2.0, 0.25))
    tt, k = 2.75, 0
    while tt < 4.4:
        sfx.add(tt, A.woodblock(k % 2 == 0, 0.8))
        tt += 0.25
        k += 1
    for tt in (2.55, 2.7):
        sfx.add(tt, A.pop(0.7))
    sfx.add(2.85, A.glock(M(91), 0.6, 0.4))
    sfx.add(4.42, A.pop(0.6))
    # grab + tug-of-war
    sfx.add(4.5, A.whoosh(0.25, 0.8))
    sfx.add(4.62, A.pop(0.7))
    sfx.add(T_TUG, P.creak(0.57, 1.0))
    for i in range(5):
        tt = T_TUG + i * 0.13
        music.add(tt, A.pluck(M(45 if i % 2 else 52), 0.25, 0.8))
        music.add(tt, A.bass(M(40 if i % 2 else 47), 0.2, 0.6))
    # slip! cookie flips up and back down, soft bump landings, coin wobble
    sfx.add(T_SLIP, A.pop(1.0))
    sfx.add(T_SLIP + 0.01, P.slide_whistle(0.28, 520, 1500, 0.9))
    sfx.add(T_SLIP + 0.3, P.slide_whistle(0.3, 1500, 640, 0.8))
    sfx.add(T_LAND, P.thump(1.0))
    sfx.add(T_LAND + 0.03, P.thump(0.8))
    sfx.add(T_LAND + 0.05, A.boing(0.45, 220))
    sfx.add(5.62, A.boing(0.3, 260))
    sfx.add(T_SETTLE, P.coin_wobble(0.62, 0.9))
    for i, m in enumerate((72, 71, 69, 67)):      # "oops" tumble-down
        music.add(5.5 + i * 0.12, A.marimba(M(m), 0.4, 0.5))
    # idea! pick up, show, crack
    sfx.add(T_IDEA, P.ding(1.0))
    sfx.add(T_IDEA + 0.02, A.chime_up(0.6))
    A.strum(music, 6.4, "C", 0.6)
    music.add(6.4, A.bass(M(48), 0.5, 0.6))
    sfx.add(6.75, A.whoosh(0.3, 0.5))
    sfx.add(7.0, A.tap(0.6))
    A.strum(music, 6.9, "Am", 0.5)
    music.add(6.9, A.bass(M(45), 0.5, 0.5))
    A.strum(music, 7.4, "F", 0.5)
    music.add(7.4, A.bass(M(41), 0.5, 0.5))
    sfx.add(7.5, P.creak(0.28, 0.35))
    sfx.add(T_CRACK, P.crack(1.0))
    sfx.add(T_CRACK + 0.02, A.snare_roll(0.08, 0.6))
    # count 1, 2 + balance + "same!"
    A.strum(music, 8.05, "C", 0.5)
    for c, m in zip(COUNTS, (84, 88)):
        sfx.add(c, A.glock(M(m), 1.2, 0.9))
        music.add(c, A.ks_pluck(M(m - 24), 1.0, 0.8))
        music.add(c, A.bass(M(48), 0.4, 0.5))
        sfx.add(c + 0.02, A.tap(0.5))
    A.strum(music, 9.1 + 0.25, "G", 0.45, True)
    for i, tt in enumerate((9.58, 9.8, 9.95)):
        sfx.add(tt, A.boing(0.28, 300 if i % 2 else 250))
    sfx.add(T_SAME, A.glock(M(91), 1.0, 0.8))
    sfx.add(T_SAME + 0.16, A.glock(M(91), 1.0, 0.8))
    sfx.add(T_SAME + 0.05, A.twinkle(0.6))
    A.strum(music, T_SAME, "C", 0.6)
    music.add(T_SAME, A.bass(M(48), 0.5, 0.6))
    # give + check
    sfx.add(T_GIVE0, A.whoosh(0.4, 0.5))
    sfx.add(T_GIVE1, A.pop(0.8))
    A.strum(music, T_GIVE1, "F", 0.6)
    music.add(T_GIVE1, A.bass(M(41), 0.5, 0.6))
    sfx.add(11.45, A.glock(M(96), 1.0, 0.7))
    sfx.add(11.47, A.twinkle(0.7))
    # munch munch munch + happy strums
    for b in BITES:
        sfx.add(b, P.crunch(1.0))
        sfx.add(b + 0.08, P.crunch(0.8))
        sfx.add(b + 0.2, P.nom(0.6))
    for tt, ch, up in ((11.6, "C", False), (11.85, "C", True), (12.1, "G", False), (12.35, "G", True),
                       (12.6, "Am", False), (12.85, "Am", True), (13.1, "F", False), (13.35, "F", True),
                       (13.6, "C", False), (13.85, "C", True), (14.1, "G", False), (14.35, "G", True)):
        A.strum(music, tt, ch, 0.7, up)
    for tt, m in ((11.6, 48), (12.1, 43), (12.6, 45), (13.1, 41), (13.6, 48), (14.1, 43)):
        music.add(tt, A.bass(M(m), 0.45, 0.8))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.45))
    sfx.add(13.55, A.boing(0.35, 340))
    # paw-bump (signature)
    sfx.add(14.85, A.snare_roll(0.6, 0.8))
    sfx.add(15.45, A.boop(0.9))
    A.jingle(music, 15.47, 1.0, ending=True)
    sfx.add(15.5, A.twinkle(0.8))
    # hop home, the grown-up's hand brings another cookie, uh-oh! (leads into the jingle at 0:00)
    sfx.add(16.05, A.boing(0.35, 300))
    sfx.add(16.42, A.boing(0.3, 330))
    sfx.add(16.25, A.whoosh(0.5, 0.6))
    sfx.add(T_HAND1, A.tap(0.9))
    sfx.add(T_HAND1 + 0.02, A.glock(M(96), 0.6, 0.35))
    A.strum(music, 16.3, "F", 0.5)
    A.strum(music, 16.8, "G7", 0.5)
    sfx.add(17.15, A.uh_oh(0.9))
    for i, m in enumerate((64, 65, 66)):
        music.add(17.45 + i * 0.15, A.pluck(M(m - 12), 0.3, 0.55))
    music.add(17.15, A.pad([M(55), M(59), M(62)], 0.85, 0.25))

    m = A.reverb(music.normalized(), 0.24)
    s = A.reverb(sfx.normalized(), 0.08)
    y = 0.55 * m / max(1e-9, abs(m).max()) + 0.7 * s / max(1e-9, abs(s).max())
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.01)


# ---------------------------------------------------------------- output
def render(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    wav = os.path.join(ROOT, "build", "ep03_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep03_the_last_cookie.mp4")
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
    times = times or [0.0, 1.9, 3.4, 4.6, 4.95, 5.4, 5.95, 6.5, 7.3, 7.9, 8.6, 9.3, 10.1, 10.7,
                      11.5, 12.3, 13.6, 15.6, 16.6, 17.5, 17.99]
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


KEYS = [(0.0, "0.0s hook"), (3.4, "3.4s choice"), (4.95, "5.0s tug-of-war"), (5.5, "5.5s tumble"),
        (8.65, "8.7s break: 1"), (10.1, "10.1s 1, 2: same"), (12.3, "12.3s munch"), (15.6, "15.6s paw-bump")]


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
        stills(os.path.join(ROOT, "build", "ep03_stills.png"))
    elif "--keys" in sys.argv:
        os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
        key_sheet(os.path.join(ROOT, "reviews", "ep03_keys.png"))
    else:
        render(os.path.join(ROOT, "output"))
