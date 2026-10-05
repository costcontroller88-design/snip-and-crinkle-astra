"""Episode 10 — Hot Sunny Day? ☀️

A bright beach: a big friendly sun, a gently rolling sea, hot sand, shells, a bucket and a
half-built sandcastle. Snip hop-hops across the hot sand ("ouch-ouch" tiptoe hops, little hot
zigzags under each paw) with an ice lolly and a spade, and dreams of a big castle. Choice: keep
playing in the hot sun, or hat + shade + water? Snip keeps digging in the full sun: the ears wilt
and droop like noodles, the lolly melts and a drip lands — plip! — on Snip's nose, until only the
stick is left. Crinkle arrives wearing TWO sun hats, with a beach umbrella and a water bottle.
He plants the umbrella (shade!), flicks the top hat onto Snip's head (the ears go through the
holes) and hands over the bottle: sip 1, sip 2, sip 3 — Snip's ears spring back up a bit with each
sip. Then they finish the sandcastle together in the shade (towers, a flag, check, hearts), the
signature paw-bump, and a big paper wave washes the beach back to the start (frame 18.0 == 0).

Run:  python3 episodes/ep10_hot_sunny_day.py            (render -> output/)
      python3 episodes/ep10_hot_sunny_day.py --stills   (contact sheet -> build/)
      python3 episodes/ep10_hot_sunny_day.py --keys     (key frames -> reviews/ep10_keys.png)
"""
import math
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import audio as A  # noqa: E402
import icons  # noqa: E402
import props_beach as P  # noqa: E402
import scene  # noqa: E402
from characters import Character  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, rot, seg  # noqa: E402

FPS = 30
DUR = 18.0
TY = P.GROUND_Y
SN_HOME = 330
CR_HOME = 785
CR_REST_L = 346                       # Crinkle's left arm hanging (== -14)
CX = 585                              # the sandcastle (in front, between the friends)
CASTLE_Y = TY + 72
UMB_TILT = 20                         # umbrella leans toward the sun (top to the left)
UMB_BASE = (920, 1462)
BOTTLE_S = 0.8
HP = (540, 1238)                      # bottle hand-off point (above the castle)
BOTTLE_DOWN = (356, 1500)             # where Snip sets the bottle down after drinking
STICK_REST = (262, 1512)
HOP_P = 0.95 / 2.5                    # hot-sand tiptoe hop period (frame 0 is at the top of a hop)
HOP_O = 0.5 - (1.0 / HOP_P) % 1.0     # phase offset: lands exactly on arrival at 0.95

BG = P.background()
SUN = P.sun()
CLOUDS = [(P.cloud(280, 120), 720, 150, 0.0), (P.cloud(220, 96), 960, 470, 2.1), (P.cloud(200, 90), 470, 330, 4.0)]
RIPPLES = [(P.ripple_band(1), 1000, 0.0, 40), (P.ripple_band(2, 6, col=(226, 246, 252)), 1090, 2.0, 55),
           (P.ripple_band(3, 8), 1160, 4.0, 70)]
SWASH = P.swash()
BOAT = P.boat()
HEAT = P.heat_frames(54)
HOT = P.hot_mark()
BITS = P.sand_bits()
PUFF = P.puff()
CASTLE_BASE = P.castle_base()
TOWER_C = P.tower(130, 160, True)
TOWER_S = P.tower(90, 150, False)
FLAG = P.flag()
SPADE = P.spade()
LOLLY = {}
DRIP = P.drip()
SWEAT = P.sweat_drop()
STICK = P.lolly(1.0)
BOTTLES = {k: P.bottle(k / 3).scaled(BOTTLE_S) for k in range(4)}
POLE = P.pole()
CANOPY = P.canopy()
FURLED = P.furled()
CR_HAT = P.sun_hat(False, (240, 118, 70)).scaled(1.2 * 0.95)
THOUGHT = P.thought_castle()
WAVE = P.wave_wipe()
NUMS = [scene.numeral(1, (244, 112, 104)), scene.numeral(2, (255, 196, 52)), scene.numeral(3, (84, 182, 222))]
BUB_SUN = P.choice_bubble("sun", (240, 110, 100))
BUB_SAFE = P.choice_bubble("safe", (90, 190, 120))
QMARK = icons.question()
CHECK = icons.check(150)
SPARKLE = scene.sparkle()
COOL = scene.sparkle((214, 240, 255))
HEARTS = [scene.heart(c, 80) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120), (255, 150, 170))]
SNIP = P.BeachSnip(1.15)
CR = Character("crinkle", 1.2)

SNIP_BLINKS = (1.6, 6.3, 8.2, 12.15, 13.9, 16.6)
CR_BLINKS = (6.62, 9.3, 10.9, 12.95, 14.35, 16.7)
T_DRIP0, T_PLIP = 5.12, 5.4
T_PLANT, T_OPEN = 6.55, 6.75
T_FLICK, T_HAT = 7.35, 7.85
T_GIVE = 8.35
SIPS = (8.8, 9.7, 10.6)
WILT_LEVELS = (1.0, 0.66, 0.33, 0.0)
T_REL, T_DOWN = 11.5, 11.6
PATS_SN = (11.78, 11.98)
PATS_CR = (12.08, 12.28)
T_FLAG = 12.62
T_CHECK = 12.85
HEART_PLAN = ((13.05, 240, 900), (13.2, 470, 800), (13.35, 720, 760), (13.5, 880, 880))
T_WAVE0, T_WAVE1, T_WAVE2, T_WAVE3 = 16.35, 16.9, 17.0, 17.55


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


def g_time(t):
    """Background clock: stands still during the choice freeze, still reaches 18.0 at the loop."""
    if t < 2.5:
        return t
    if t < 4.5:
        return 2.5
    return 2.5 + (t - 4.5) * (DUR - 2.5) / (DUR - 4.5)


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


def hook_tp(t):
    """Hook clock: the hot-sand hop-hop runs from -1.0 (under the loop wave) to 0.95 (arrival)."""
    return t - DUR if t >= T_WAVE1 else t


def hop_q(tp):
    return ((tp + 1.0) / HOP_P + HOP_O) % 1.0


def landings():
    """Hook-clock times when a paw lands on the hot sand."""
    k0 = math.ceil(HOP_O)
    out = []
    k = k0
    while True:
        tl = -1.0 + (k - HOP_O) * HOP_P
        if tl > 0.96:
            return out
        if tl > -1.0:
            out.append(tl)
        k += 1


HOOK_PATH = ((-1.0, 70), (-0.45, 186), (0.0, 205), (0.95, SN_HOME))   # hops on the spot around frame 0


def hook_x(tp):
    for (t0, x0), (t1, x1) in zip(HOOK_PATH, HOOK_PATH[1:]):
        if tp <= t1:
            return lerp(x0, x1, ease_in_out(seg(tp, t0, t1)))
    return SN_HOME


def in_hook(t):
    return t < 0.95 or t >= T_WAVE1


# ---------------------------------------------------------------- wilt (noodle ears) + props timing
def wilt_at(t):
    if t < 4.65 or t >= T_WAVE1:
        return 0.0
    if t < SIPS[0] + 0.3:
        return ease_in_out(seg(t, 4.65, 5.6))
    w = WILT_LEVELS[0]
    for i, s in enumerate(SIPS):
        t0 = s + 0.3
        if t >= t0:
            a, b = WILT_LEVELS[i], WILT_LEVELS[i + 1]
            x = t - t0
            w = b + (a - b) * math.exp(-6.5 * x) * math.cos(13 * x)     # springy, overshoots a little
    return w


def lolly_melt(t):
    return ease_in_out(seg(t, 4.6, 5.78)) if 4.5 <= t < T_WAVE1 else 0.0


def bottle_level(t):
    return 3 - sum(1 for s in SIPS if t >= s + 0.3)


# ---------------------------------------------------------------- Snip
def snip_state(t):
    if frozen(t):
        return snip_state(2.4999)
    s = dict(x=SN_HOME, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, arm_l=-14.0, arm_r=14.0, eyes="normal",
             mouth="w", look=(0, 0), head_dy=0.0, ears=[0.0, 0.0], ear_stretch=1.0)
    idle_ear = 2.0 * math.sin(2 * math.pi * t / 3.0)

    if in_hook(t):                    # HOOK: ouch-ouch tiptoe hops across the hot sand
        tp = hook_tp(t)
        q = hop_q(tp)
        air = math.sin(math.pi * q)
        s["x"] = hook_x(tp)
        s["hop"] = 32 * air
        s["sq"] = 1 + 0.08 * air - 0.12 * (max(0, 1 - q / 0.14) + max(0, 1 - (1 - q) / 0.14))
        s["lean"] = 5 * math.sin(math.pi * ((tp + 1.0) / HOP_P + HOP_O))     # turning points at hop tops
        s["arm_l"] = -165 + 10 * math.cos(2 * math.pi * q)
        s["arm_r"] = 52 - 18 * math.cos(2 * math.pi * q)
        hot = q < 0.2 or q > 0.9
        s.update(eyes="closed" if hot else "wide", mouth="O" if hot else "o", look=(-3, -2))
        s["ears"] = [-7 * air, 7 * air]
        s["ear_stretch"] = 1 + 0.1 * air
    elif t < 2.5:                     # DESIRE: phew... then sparkly eyes at the dream castle
        h, sq = hop_curve(t, 0.95, 0.95, 1, 0)
        s.update(sq=sq, lean=lerp(0, -4, ease_in_out(seg(t, 1.0, 1.3))), arm_l=-158, arm_r=lerp(52, 34, ease_out(seg(t, 0.95, 1.2))))
        if t < 1.22:
            s.update(eyes="closed", mouth="w", look=(0, 0))
        else:
            s.update(eyes="sparkle", mouth="yum", look=(8, -4), tilt=-5 * ease_out(seg(t, 1.22, 1.5)))
        e = spring(t, 1.22, 10, 4.0, 3.0)
        s["ears"] = [e, -e]
    elif t < 6.0:                     # SLAPSTICK: dig dig dig in the full sun
        k = ease_in_out(seg(t, 4.5, 4.7))
        dig = math.sin(2 * math.pi * (t - 4.5) / 0.3)
        s["lean"] = lerp(-4, -9, k)
        s["arm_l"] = -158
        s["arm_r"] = lerp(34, 46 + 24 * dig, k) if t < 5.85 else lerp(46, 14, ease_in_out(seg(t, 5.85, 6.0)))
        w = wilt_at(t)
        if t < 4.95:
            s.update(eyes="sparkle", mouth="grin", look=(8, 4))
        elif t < T_PLIP:
            s.update(eyes="worried" if w > 0.4 else "normal", mouth="o" if int(t / 0.16) % 2 else "blow", look=(7, 4))
            s["head_dy"] = 8 * w
        elif t < 5.65:                # plip! the drip lands on the nose
            s.update(eyes="wide", mouth="O", look=(0, 9))
            s["head_dy"] = 8 - 12 * math.sin(math.pi * seg(t, T_PLIP, T_PLIP + 0.2))
            s["ear_stretch"] = 1 + 0.1 * math.sin(math.pi * seg(t, T_PLIP, T_PLIP + 0.25))
        else:                         # all melted: just a stick... droopy and hot
            s.update(eyes="worried", mouth="wobble", look=(-2, 6))
            s["head_dy"] = 10
            s["arm_l"] = lerp(-158, -20, ease_in_out(seg(t, 5.8, 6.0)))
        sway = 4 * math.sin(2 * math.pi * t / 1.5) * w
        s["ears"] = [sway, -sway]
    elif t < T_FLICK:                 # Crinkle arrives; the umbrella opens: shade! ahh...
        s.update(lean=lerp(-9, 0, ease_in_out(seg(t, 6.0, 6.3))), eyes="worried", mouth="wobble", look=(9, -2),
                 head_dy=10 * (1 - ease_in_out(seg(t, 7.0, 7.3))))
        if t >= T_OPEN:
            s.update(eyes="wide", mouth="o", look=(4, -9))
        if t >= 7.05:
            s.update(eyes="closed", mouth="smile", look=(0, 0))
            h, sq = hop_curve(t, 7.05, 7.05, 1, 0)
            s["sq"] = 1 - 0.05 * math.sin(math.pi * seg(t, 7.05, 7.3))
        sway = 4 * math.sin(2 * math.pi * t / 1.5)
        s["ears"] = [sway, -sway]
    elif t < 8.0:                     # the hat flies over... and lands on Snip's head
        if t < T_HAT:
            s.update(eyes="wide", mouth="o", look=(7, -9) if t < 7.6 else (1, -9))
        else:
            s.update(eyes="happy", mouth="grin", look=(0, 0))
            s["sq"] = 1 - 0.07 * math.sin(math.pi * seg(t, T_HAT, T_HAT + 0.18))
        e = spring(t, T_HAT, 10, 5.0, 4.0)
        s["ears"] = [e, -e]
    elif t < T_DOWN:                  # take the bottle; sip 1, 2, 3
        s.update(eyes="normal", mouth="w", look=(8, 2))
        if t < T_GIVE + 0.1:
            s["arm_r"] = lerp(14, aim(SNIP, s, "r", HP, 40), ease_in_out(seg(t, 8.05, 8.3)))
            s.update(eyes="sparkle", mouth="o")
        else:
            k = sip_k(t)
            m = mouth(SNIP, s)
            off = straw_offset()
            hold = (m[0] - off[0], m[1] - off[1])
            low = (hold[0] + 22, hold[1] + 52)
            tgt = (lerp(low[0], hold[0], k), lerp(low[1], hold[1], k))
            a_hp = aim(SNIP, s, "r", HP, 40)
            s["arm_r"] = lerp(a_hp, aim(SNIP, s, "r", tgt, -40), ease_in_out(seg(t, T_GIVE + 0.1, T_GIVE + 0.35)))
            for i, sp in enumerate(SIPS):
                if sp - 0.05 <= t < sp + 0.45:
                    s.update(eyes="closed", mouth="blow", look=(0, 0))
                elif sp + 0.45 <= t < sp + 0.85:
                    s.update(eyes="sparkle" if i == 2 else "happy", mouth="grin" if i == 2 else "smile")
            if t >= SIPS[2] + 0.45:
                s.update(eyes="sparkle", mouth="grin", look=(6, -3))
                h, sq = hop_curve(t, 11.05, 11.35, 1, 24)
                s["hop"], s["sq"] = h, sq
                if t >= 11.3:        # set the bottle down on the sand
                    cur = aim(SNIP, s, "r", tgt, -40)
                    s["arm_r"] = lerp(cur, aim(SNIP, s, "r", bottle_grip(BOTTLE_DOWN), 0), ease_in_out(seg(t, 11.3, 11.5)))
                    s["lean"] = -6 * math.sin(math.pi * seg(t, 11.3, 11.75))
        for sp in SIPS:
            e = spring(t, sp + 0.3, 9, 5.0, 4.0)
            s["ears"][0] += e
            s["ears"][1] -= e
    elif t < 14.0:                    # PAYOFF: finish the castle together in the shade
        s.update(eyes="happy", mouth="grin", look=(8, 3))
        a_down = aim(SNIP, s, "r", bottle_grip(BOTTLE_DOWN), 0)
        a_pat = aim(SNIP, s, "r", (CX - 100, 1312), 20)
        k = ease_in_out(seg(t, T_DOWN, T_DOWN + 0.15))
        s["arm_r"] = lerp(a_down, a_pat, k)
        for p in PATS_SN:
            s["arm_r"] -= 16 * math.sin(math.pi * seg(t, p - 0.1, p + 0.08))
        s["arm_r"] = lerp(s["arm_r"], 14, ease_in_out(seg(t, 12.15, 12.4)))
        if t > 12.4:
            s.update(look=(8, -4), eyes="sparkle" if t > T_FLAG else "normal", mouth="grin" if t > T_FLAG else "o")
        if t > 13.0:
            s.update(eyes="happy", mouth="grin")
        h, sq = hop_curve(t, 13.4, 13.72, 1, 26)
        s["hop"], s["sq"] = h, sq
        e = spring(t, 13.4, 12, 5.0, 3.5) + spring(t, PATS_SN[1], 6, 5.0, 4.0)
        s["ears"] = [e, -e]
    elif t < 16.4:                    # PAW-BUMP
        h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
        s.update(x=lerp(SN_HOME, 400, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq, eyes="happy", mouth="grin")
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_r"] = lerp(lerp(14, -6, wind), 165, swing)
        s["arm_r"] = lerp(s["arm_r"], 120, ease_in_out(seg(t, 16.0, 16.35)))
        e = spring(t, 15.45, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
        if t > 16.1:
            s.update(eyes="wide", mouth="o", look=(4, 8))       # ...a big wave!
    else:                             # the wave rises over everything
        s.update(x=400, eyes="wide", mouth="o", look=(4, 8), arm_r=120, arm_l=-120)

    s["ears"][0] += idle_ear
    s["ears"][1] -= idle_ear
    if s["hop"] == 0:
        s["sq"] *= breath(t)
    return s


def sip_k(t):
    """How far the straw is lifted to Snip's mouth (0 = lowered, 1 = sipping)."""
    k = 0.0
    for sp in SIPS:
        k = max(k, ease_in_out(seg(t, sp - 0.2, sp - 0.02)) * (1 - ease_in_out(seg(t, sp + 0.45, sp + 0.62))))
    return k


def straw_offset():
    sx, sy = P.BOTTLE_STRAW_TIP
    px, py = P.BOTTLE_PIVOT
    return ((sx - px) * BOTTLE_S, (sy - py) * BOTTLE_S)


def bottle_grip(foot):
    """Paw position that holds the bottle standing at `foot` (its base on the sand)."""
    return (foot[0], foot[1] - (340 - P.BOTTLE_PIVOT[1]) * BOTTLE_S)


# ---------------------------------------------------------------- Crinkle
def crinkle_state(t):
    s = dict(x=CR_HOME, hop=0.0, sq=1.0, lean=0.0, arm_l=CR_REST_L, arm_r=-15.0, eyes="normal", mouth="smile",
             look=(0, 0), head_dy=0.0, here=True)
    if t < 6.0 or t >= T_WAVE1:
        s.update(x=1500, here=False)
        return s
    if t < T_OPEN:                    # hops in with the umbrella, the bottle and two hats
        h, sq = hop_curve(t, 6.0, 6.5, 2, 30)
        s.update(x=lerp(1500, CR_HOME, ease_out(seg(t, 6.0, 6.5))), hop=h, sq=sq,
                 lean=8 * (1 - ease_out(seg(t, 6.0, 6.6))), look=(-7, 0))
        s.update(eyes="wide" if t > 6.3 else "normal", mouth="o" if t > 6.3 else "smile")
        if t > 6.38:                  # lift... and plant!
            s["hop"] = 26 * math.sin(math.pi * seg(t, 6.38, T_PLANT))
            s["sq"] = 1 - 0.08 * math.sin(math.pi * seg(t, T_PLANT, T_PLANT + 0.16))
            s.update(eyes="closed", mouth="grin")
    elif t < T_FLICK - 0.25:          # the umbrella pops open; looks up, pleased
        s["arm_r"] = lerp(-15, 2, ease_in_out(seg(t, T_OPEN, T_OPEN + 0.2)))
        s.update(eyes="happy" if t > 6.95 else "wide", mouth="grin" if t > 6.95 else "o", look=(-3, -9))
        if t > 7.0:
            s.update(look=(-8, -2))
    elif t < 8.0:                     # head flick: the top hat flies to Snip
        s["arm_r"] = 2
        s["head_dy"] = 14 * math.sin(math.pi * seg(t, T_FLICK - 0.25, T_FLICK)) - 16 * math.sin(math.pi * seg(t, T_FLICK, T_FLICK + 0.2))
        s.update(eyes="closed" if t < T_FLICK + 0.15 else "happy", mouth="grin", look=(-8, -6))
    elif t < T_DOWN:                  # hands over the bottle, then counts the sips
        s["arm_r"] = 2
        s.update(eyes="happy", mouth="smile", look=(-8, 2))
        give = ease_in_out(seg(t, 8.0, 8.28))
        back = ease_in_out(seg(t, T_GIVE + 0.05, T_GIVE + 0.3))
        s["lean"] = 6 * give * (1 - back)
        a = aim(CR, s, "l", HP, 300)
        s["arm_l"] = lerp(lerp(CR_REST_L, a, give), CR_REST_L, back)
        for sp in SIPS:
            s["head_dy"] += 10 * math.sin(math.pi * seg(t, sp, sp + 0.3))
            if 0 <= t - sp < 0.3:
                s["mouth"] = "o"
        h, sq = hop_curve(t, 11.1, 11.4, 1, 20)
        if h or sq != 1.0:
            s["hop"], s["sq"] = h, sq
            s["mouth"] = "grin"
    elif t < 14.0:                    # pats the castle, then plants the flag
        s["arm_r"] = 2
        s.update(eyes="happy", mouth="grin", look=(-8, 3))
        a_pat = aim(CR, s, "l", (CX + 100, 1312), 340)
        a_flag = aim(CR, s, "l", (CX + 4, 1290), 300)
        k = ease_in_out(seg(t, 11.85, 12.0))
        a = lerp(CR_REST_L, a_pat, k)
        for p in PATS_CR:
            a += 14 * math.sin(math.pi * seg(t, p - 0.1, p + 0.08))
        a = lerp(a, a_flag, ease_in_out(seg(t, 12.35, T_FLAG - 0.05)))
        s["arm_l"] = lerp(a, CR_REST_L, ease_in_out(seg(t, T_FLAG + 0.12, T_FLAG + 0.4)))
        s["lean"] = 5 * ease_in_out(seg(t, 12.35, T_FLAG)) * (1 - ease_in_out(seg(t, T_FLAG + 0.1, T_FLAG + 0.4)))
        h, sq = hop_curve(t, 13.45, 13.77, 1, 24)
        s["hop"], s["sq"] = h, sq
    elif t < 16.4:                    # PAW-BUMP
        s["arm_r"] = 2
        h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
        s.update(x=lerp(CR_HOME, 720, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq, eyes="happy", mouth="grin")
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_l"] = lerp(lerp(CR_REST_L, 360, wind), 198, swing)
        s["arm_l"] = lerp(s["arm_l"], 230, ease_in_out(seg(t, 16.0, 16.35)))
        if t > 16.1:
            s.update(eyes="wide", mouth="O", look=(-4, 8))
    else:
        s.update(x=720, arm_r=2, arm_l=230, eyes="wide", mouth="O", look=(-4, 8))
    if s["hop"] == 0:
        s["sq"] *= breath(t + 0.7, 2.25, 0.01)
    return s


# ---------------------------------------------------------------- umbrella, hats, bottle
def umbrella(t, cr):
    """(base_xy, angle, open_k) or None."""
    if t < 6.0 or t >= T_WAVE1:
        return None
    if t < T_PLANT:
        paw = tip(CR, cr, "r")
        ang = UMB_TILT * ease_in_out(seg(t, 6.3, T_PLANT)) + 4 * (1 - seg(t, 6.0, 6.3))
        dx, dy = rot(0, 140, ang)
        return (paw[0] + dx, paw[1] + dy), ang, 0.0
    return UMB_BASE, UMB_TILT, ease_out_back(seg(t, T_OPEN, T_OPEN + 0.32), 1.3)


def apex(base, ang):
    dx, dy = rot(0, -P.UMB_POLE, ang)
    return base[0] + dx, base[1] + dy


def shade_k(t):
    if t < T_OPEN or t >= T_WAVE1:
        return 0.0
    return ease_in_out(seg(t, T_OPEN + 0.05, T_OPEN + 0.4))


def cr_hat_pose(cr, level=0):
    hx, hy = CR.head_pivot(cr["x"], TY, cr["hop"], cr["lean"], cr["sq"], cr["head_dy"])
    dx, dy = rot(0, -(P.CR_HAT_DY + level * 112) * CR.s, cr["lean"])
    return (hx + dx, hy + dy), cr["lean"]


def flying_hat(t, sn, cr):
    """The Snip-hat while it is NOT on Snip's head: stacked on Crinkle's hat, then flying."""
    if t < 6.0 or t >= T_HAT:
        return None
    if t < T_FLICK:
        return cr_hat_pose(cr, 1)
    a0, ang0 = cr_hat_pose(crinkle_state(T_FLICK), 1)
    b, angb = SNIP.hat_pose(sn["x"], TY, sn["hop"], sn["lean"], sn["sq"], sn["head_dy"], sn["tilt"])
    p = seg(t, T_FLICK, T_HAT)
    e = ease_in_out(p)
    x = lerp(a0[0], b[0], e)
    y = lerp(a0[1], b[1], e) - 230 * math.sin(math.pi * p)
    return (x, y), lerp(ang0, angb, e) + 360 * ease_in_out(p)


def bottle_pose(t, sn, cr):
    """(position of the bottle pivot, angle) or None."""
    if t < 6.0 or t >= T_WAVE1:
        return None
    if t < T_GIVE:
        if t >= 8.0:
            a = tip(CR, cr, "l")
            return (a[0], a[1] - 8), 0.0
        a = tip(CR, cr, "l")
        return (a[0] + 6, a[1] - 6), 6.0 * math.sin(t * 3)
    if t < T_REL:
        p = tip(SNIP, sn, "r")
        if t < T_GIVE + 0.12:          # tiny blend so the hand-off doesn't pop
            c = tip(CR, crinkle_state(T_GIVE - 1e-3), "l")
            k = ease_in_out(seg(t, T_GIVE, T_GIVE + 0.12))
            p = (lerp(c[0], p[0], k), lerp(c[1] - 8, p[1], k))
        return p, -8 * sip_k(t)
    g = bottle_grip(BOTTLE_DOWN)
    if t < T_REL + 0.3:                # set down: a little drop and bounce onto the sand
        a = tip(SNIP, snip_state(T_REL - 1e-3), "r")
        p = seg(t, T_REL, T_REL + 0.14)
        bounce = 14 * math.sin(math.pi * seg(t, T_REL + 0.14, T_REL + 0.3))
        return (lerp(a[0], g[0], p), lerp(a[1], g[1], p * p) - bounce), 0.0
    return g, 0.0


# ---------------------------------------------------------------- particles
_PARTS = {}


def particles(key, origin, n, seed, vx_range, vy_range):
    if key not in _PARTS:
        import random
        rnd = random.Random(seed)
        _PARTS[key] = [(rnd.choice(range(len(BITS))), origin[0] + rnd.uniform(-14, 14), origin[1] + rnd.uniform(-8, 8),
                        rnd.uniform(*vx_range), rnd.uniform(*vy_range), rnd.uniform(-500, 500), rnd.uniform(0.6, 1.1))
                       for _ in range(n)]
    return _PARTS[key]


def draw_bits(f, t, t0, origin, n, seed, life=0.5):
    if not (t0 <= t < t0 + life):
        return
    dt = t - t0
    for k, x, y, vx, vy, spin, sc in particles((t0, seed), origin, n, seed, (-260, 120), (-620, -320)):
        px, py = x + vx * dt, y + vy * dt + 0.5 * 2200 * dt * dt
        place(f, BITS[k], (px, min(py, TY + 20)), angle=spin * dt, scale=sc,
              alpha=1 - ease_in_out(seg(t, t0 + life - 0.15, t0 + life)))


def dig_times():
    out, tt = [], 4.62
    while tt < 5.82:
        out.append(tt)
        tt += 0.3
    return out


DIGS = dig_times()


# ---------------------------------------------------------------- shade overlay
def _shade_overlay():
    m = Image.new("L", (scene.W, scene.H), 0)
    d = ImageDraw.Draw(m)
    b = apex(UMB_BASE, UMB_TILT)
    rim_c = (b[0] + rot(0, P.CANOPY_H, UMB_TILT)[0], b[1] + rot(0, P.CANOPY_H, UMB_TILT)[1])
    l = (rim_c[0] + rot(-P.CANOPY_W / 2, 0, UMB_TILT)[0], rim_c[1] + rot(-P.CANOPY_W / 2, 0, UMB_TILT)[1])
    r = (rim_c[0] + rot(P.CANOPY_W / 2, 0, UMB_TILT)[0], rim_c[1] + rot(P.CANOPY_W / 2, 0, UMB_TILT)[1])
    d.polygon([l, r, (r[0] + 60, TY + 60), (l[0] - 40, TY + 60)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(40))
    img = Image.new("RGBA", m.size, (40, 70, 130, 255))
    img.putalpha(m.point(lambda v: int(v * 0.17)))
    return img


SHADE_OVERLAY = _shade_overlay()


def _ground_shade():
    m = Image.new("L", (1100, 200), 0)
    ImageDraw.Draw(m).ellipse([60, 40, 1040, 160], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(14))
    img = Image.new("RGBA", m.size, P.SHADE + (255,))
    img.putalpha(m.point(lambda v: int(v * 0.5)))
    from paperlib import Sprite
    return Sprite(img, (550, 100))


GROUND_SHADE = _ground_shade()


# ---------------------------------------------------------------- frame
def lolly_sprite(m):
    q = round(m * 24) / 24
    if q not in LOLLY:
        LOLLY[q] = P.lolly(q)
    return LOLLY[q]


def draw_scenery(f, t):
    g = g_time(t)
    pulse = 1 + 0.03 * math.cos(2 * math.pi * g / 1.5)          # the sun beams (still at the loop seam)
    place(f, SUN, (230, 290), angle=6 * math.sin(2 * math.pi * g / 6.0), scale=pulse)
    for spr, x, y, ph in CLOUDS:
        place(f, spr, (x + 22 * math.sin(2 * math.pi * g / DUR + ph), y + 5 * math.sin(4 * math.pi * g / DUR + ph)))
    place(f, BOAT, (900 + 10 * math.sin(2 * math.pi * g / 6.0), 952 + 4 * math.sin(2 * math.pi * g / 3.0)),
          angle=4 * math.sin(2 * math.pi * g / 3.0))
    for spr, y, ph, amp in RIPPLES:
        place(f, spr, (amp * math.sin(2 * math.pi * g / 6.0 + ph), y))
    place(f, SWASH, (12 * math.sin(2 * math.pi * g / 9.0), P.SHORE_Y - 76 + 16 * math.sin(2 * math.pi * g / 6.0)))


def draw_castle(f, t):
    built = 11.0 < t < T_WAVE1
    for p, x in ((PATS_SN[1], CX - 100), (PATS_CR[1], CX + 100)):      # side towers (behind the big one)
        if built and t >= p:
            place(f, TOWER_S, (x, CASTLE_Y - 14), scale=pop_scale(t, p, 0.25))
    if built and t >= T_FLAG:
        place(f, FLAG, (CX + 4, CASTLE_Y - 30 - 180), scale=pop_scale(t, T_FLAG, 0.25), angle=3 * math.sin(t * 5))
    wob = 1 - 0.03 * math.sin(math.pi * seg(t, DIGS[-1], DIGS[-1] + 0.2)) if t < 6 else 1
    place(f, TOWER_C, (CX, CASTLE_Y - 30), sy=wob)
    place(f, CASTLE_BASE, (CX, CASTLE_Y))
    for p, x in ((PATS_SN[1], CX - 100), (PATS_CR[1], CX + 100)):      # a puff of sand as each tower pops up
        if built and p <= t < p + 0.45:
            place(f, PUFF, (x, CASTLE_Y + 10), scale=0.7 * pop_scale(t, p, 0.18),
                  alpha=1 - ease_in_out(seg(t, p + 0.2, p + 0.45)))


def heat_idx(g):
    """54 squiggle drawings, 10 cycles per loop: exactly one drawing per video frame."""
    return int(g * 54 * 10 / DUR + 1e-6) % 54


def draw_heat(f, t):
    """Wavy heat rising off the hot sand (and off Snip's head when too hot)."""
    k = 1.0 - shade_k(t)
    if not in_hook(t) and t >= 7.6:
        return
    g = g_time(t)
    idx0 = heat_idx(g)
    for i, (x, y, sc) in enumerate(((150, TY + 40, 1.0), (470, TY + 70, 0.8), (690, TY + 50, 1.1), (900, TY + 80, 0.9),
                                    (40, TY + 110, 0.9), (330, TY + 120, 1.0))):
        place(f, HEAT[(idx0 + i * 17) % 54], (x, y), scale=sc, alpha=0.6 * k)


def render_frame(t):
    f = BG.copy()
    draw_scenery(f, t)
    sn = snip_state(t)
    cr = crinkle_state(t)
    sk = shade_k(t)
    if sk > 0.01:
        place(f, GROUND_SHADE, (600, TY + 18), sx=lerp(0.15, 1.0, sk), alpha=sk, shadow=False)
    draw_heat(f, t)

    # umbrella (behind everyone: it stands behind Crinkle)
    um = umbrella(t, cr)
    if um is not None:
        base, ang, k = um
        place(f, POLE, base, angle=ang)
        top = apex(base, ang)
        if k < 0.5:
            place(f, FURLED, top, angle=ang, sx=1 - 0.6 * min(1, k * 2), alpha=1 - min(1, k * 2.2))
        if k > 0.01:
            place(f, CANOPY, top, angle=ang, sx=max(0.05, lerp(0.1, 1.0, k)), sy=max(0.05, lerp(0.75, 1.0, min(1, k))))
        if T_PLANT <= t < T_PLANT + 0.5:
            place(f, PUFF, (base[0] - 10, TY + 30), scale=0.8 * pop_scale(t, T_PLANT, 0.2),
                  alpha=1 - ease_in_out(seg(t, T_PLANT + 0.25, T_PLANT + 0.5)))


    # Snip (noodle ears; the sun hat with ear holes once it lands)
    wilt = wilt_at(t)
    SNIP.draw(f, sn["x"], TY, hop=sn["hop"], lean=sn["lean"], head_tilt=sn["tilt"], arm_l=sn["arm_l"],
              arm_r=sn["arm_r"], eyes=sn["eyes"], mouth=sn["mouth"], look=sn["look"], squash=sn["sq"],
              head_dy=sn["head_dy"], blink=blinking(t, SNIP_BLINKS) and not frozen(t), ears=tuple(sn["ears"]),
              ear_stretch=sn["ear_stretch"], wilt=(wilt, wilt), hat=T_HAT <= t < T_WAVE1)

    # lolly in the left paw (paw redrawn in front of the face), spade in the right paw
    melt = lolly_melt(t)
    if in_hook(t) or t < 5.8:
        lp = tip(SNIP, sn, "l")
        place(f, lolly_sprite(melt), (lp[0] + 4, lp[1] + 2), angle=-6 + (3 * math.cos(2 * math.pi * hop_q(hook_tp(t))) if in_hook(t) else 0))
        place(f, SNIP.arm_l, SNIP.shoulder_pt(sn["x"], TY, "l", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_l"] + sn["lean"])
    elif 5.8 <= t < T_WAVE1:          # the bare stick drops onto the sand
        p = seg(t, 5.8, 6.05)
        lp = tip(SNIP, snip_state(5.8), "l")
        x = lerp(lp[0], STICK_REST[0], p)
        y = lerp(lp[1], STICK_REST[1], p ** 2) - 60 * math.sin(math.pi * p)
        place(f, STICK, (x, y), angle=lerp(-6, 96, ease_out(p)), scale=0.9)
    if in_hook(t) or t < 5.86:
        rp = tip(SNIP, sn, "r")
        place(f, SPADE, rp, angle=sn["arm_r"] + sn["lean"])
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], TY, "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])
    elif t < 6.2:                     # ...and drops it in the sand behind the castle (plonk)
        s0 = snip_state(5.859)
        rp = tip(SNIP, s0, "r")
        p = seg(t, 5.86, 6.06)
        place(f, SPADE, (rp[0] + 20 * p, rp[1] + 150 * p * p), angle=lerp(s0["arm_r"] + s0["lean"], 80, ease_out(p)))

    # Crinkle with his sun hat (and Snip's hat stacked on top until he flicks it over)
    if cr["here"]:
        CR.draw(f, cr["x"], TY, hop=cr["hop"], lean=cr["lean"], arm_l=cr["arm_l"], arm_r=cr["arm_r"],
                eyes=cr["eyes"], mouth=cr["mouth"], look=cr["look"], squash=cr["sq"], head_dy=cr["head_dy"],
                blink=blinking(t, CR_BLINKS))
        at, ang = cr_hat_pose(cr, 0)
        place(f, CR_HAT, at, angle=ang)

    draw_castle(f, t)

    # the water bottle (lesson prop): always in front, paw redrawn over it
    bp = bottle_pose(t, sn, cr)
    if bp is not None:
        place(f, BOTTLES[bottle_level(t)], bp[0], angle=bp[1])
        if T_GIVE <= t < T_REL:
            place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], TY, "r", sn["hop"], sn["lean"], sn["sq"]),
                  angle=sn["arm_r"] + sn["lean"])
        elif cr["here"] and t < T_GIVE:
            place(f, CR.arm_l, CR.shoulder_pt(cr["x"], TY, "l", cr["hop"], cr["lean"], cr["sq"]),
                  angle=cr["arm_l"] + cr["lean"])

    fh = flying_hat(t, sn, cr)
    if fh is not None:
        place(f, SNIP.hat, fh[0], angle=fh[1])

    # flag in Crinkle's paw before it is planted
    if 12.3 <= t < T_FLAG:
        ct = tip(CR, cr, "l")
        place(f, FLAG, (ct[0] + 4, ct[1] + 30), scale=pop_scale(t, 12.3, 0.2), angle=4)

    # hot-sand zigzags under each landing paw (hook)
    if in_hook(t):
        tp = hook_tp(t)
        for k, tl in enumerate(landings()):
            if 0 <= tp - tl < 0.32:
                p = seg(tp, tl, tl + 0.32)
                place(f, HOT, (hook_x(tl) + (44 if k % 2 else -44), TY + 10), scale=pop_scale(tp, tl, 0.12) * 1.25,
                      alpha=1 - ease_in_out(seg(p, 0.55, 1.0)))

    # slapstick extras: sand flicks, heat off the head, sweat drop, the drip
    for i, d in enumerate(DIGS):
        draw_bits(f, t, d + 0.05, (CX - 120, TY - 40), 4, 30 + i, 0.5)
    if 4.75 <= t < 7.4:
        hx, hy = SNIP.head_pivot(sn["x"], TY, sn["hop"], sn["lean"], sn["sq"], sn["head_dy"])
        g = g_time(t)
        a = ease_in_out(seg(t, 4.75, 5.1)) * (1 - shade_k(t))
        for i, dx in enumerate((-70, 70)):
            place(f, HEAT[(heat_idx(g) + i * 23) % 54], (hx + dx, hy - 290), scale=0.8, alpha=0.9 * a)
    if 4.95 <= t < 5.75:
        hx, hy = SNIP.head_pivot(sn["x"], TY, sn["hop"], sn["lean"], sn["sq"], sn["head_dy"])
        p = seg(t, 4.95, 5.75)
        place(f, SWEAT, (hx + 150, hy - 175 + 90 * p ** 1.5), scale=pop_scale(t, 4.95, 0.2),
              alpha=1 - ease_in_out(seg(p, 0.75, 1.0)))
    if T_DRIP0 <= t < T_PLIP:
        st = snip_state(T_DRIP0)
        lp = tip(SNIP, st, "l")
        m = lolly_melt(T_DRIP0)
        start = (lp[0] + 4 + 46 * m ** 0.8 + 6, lp[1] + 2 - 60 - 118 * (1 - 0.88 * m) + 10)
        hx, hy = SNIP.head_pivot(SN_HOME, TY, 0, snip_state(T_PLIP)["lean"], 1.0, snip_state(T_PLIP)["head_dy"])
        nose = (hx, hy - 90 * SNIP.s - 8)
        p = seg(t, T_DRIP0, T_PLIP)
        place(f, DRIP, (lerp(start[0], nose[0], p), lerp(start[1], nose[1], p) - 70 * math.sin(math.pi * p)),
              scale=1.1, angle=-30 * p)
    if T_PLIP <= t < 6.6:                                    # the drip sits on Snip's nose... then dries off
        hx, hy = SNIP.head_pivot(sn["x"], TY, sn["hop"], sn["lean"], sn["sq"], sn["head_dy"])
        place(f, DRIP, (hx, hy - 90 * SNIP.s - 4), scale=1.05, sy=0.8 - 0.25 * seg(t, T_PLIP, T_PLIP + 0.1) + 0.25,
              alpha=1 - ease_in_out(seg(t, 6.3, 6.6)))

    # shade tint under the umbrella
    if sk > 0.01:
        sh = SHADE_OVERLAY if sk > 0.99 else _fade(SHADE_OVERLAY, sk)
        f.alpha_composite(sh)
    if T_OPEN + 0.25 <= t < 7.6:                              # cool sparkles: ahh, shade
        for i, (dx, dy) in enumerate(((-140, -220), (150, -260), (-40, -330))):
            t0 = T_OPEN + 0.25 + 0.1 * i
            if t0 <= t < t0 + 0.6:
                hx, hy = SNIP.head_pivot(sn["x"], TY)
                place(f, COOL, (hx + dx, hy + dy), scale=0.28 * math.sin(math.pi * seg(t, t0, t0 + 0.6)),
                      angle=(t - t0) * 100)

    # paw-bump: both touching paws in front
    if 14.95 <= t < 16.1:
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], TY, "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])
        place(f, CR.arm_l, CR.shoulder_pt(cr["x"], TY, "l", cr["hop"], cr["lean"], cr["sq"]),
              angle=cr["arm_l"] + cr["lean"])

    # desire: the dream castle
    if 1.25 <= t < 2.45:
        k = pop_scale(t, 1.25, 0.3) * (1 - ease_in_out(seg(t, 2.25, 2.45)))
        place(f, THOUGHT, (575, 860), scale=1.05 * k, angle=3 * math.sin(t * 3))

    # sip numerals 1, 2, 3
    for i, sp in enumerate(SIPS):
        if sp <= t < sp + 0.85:
            out = 1 - ease_in_out(seg(t, sp + 0.65, sp + 0.85))
            place(f, NUMS[i], (560, 220), scale=pop_scale(t, sp, 0.28) * out, angle=-6 + 4 * math.sin(t * 6))

    if T_CHECK <= t < 13.6:
        place(f, CHECK, (585, 1005), scale=pop_scale(t, T_CHECK, 0.25) * (1 - ease_in_out(seg(t, 13.35, 13.6))))
    for i, (t0, x, y) in enumerate(HEART_PLAN):
        if t0 <= t < 14.5:
            p = seg(t, t0, 14.5)
            place(f, HEARTS[i], (x + 10 * math.sin(t * 3 + i), y - 160 * p), scale=pop_scale(t, t0, 0.25),
                  alpha=1 - ease_in_out(seg(t, 14.1, 14.5)), angle=10 * math.sin(t * 2.5 + i))

    if 15.45 <= t < 16.2:
        sn_tip = tip(SNIP, sn, "r")
        cr_tip = tip(CR, cr, "l")
        mid = ((sn_tip[0] + cr_tip[0]) / 2, (sn_tip[1] + cr_tip[1]) / 2 - 10)
        place(f, SPARKLE, (mid[0], mid[1] - 35), scale=pop_scale(t, 15.45, 0.22) * 0.55, angle=(t - 15.45) * 60,
              alpha=1 - ease_in_out(seg(t, 15.9, 16.2)))

    # FREEZE: dim + choice bubbles
    if 2.5 <= t < 4.6:
        dim = 0.32 * ease_in_out(seg(t, 2.5, 2.8)) * (1 - ease_in_out(seg(t, 4.35, 4.6)))
        if dim > 0.01:
            f.alpha_composite(Image.new("RGBA", f.size, (30, 26, 52, int(255 * dim))))
        gone = 1 - ease_in_out(seg(t, 4.4, 4.55))
        pulse_a = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 2.95) / 1.0))
        pulse_b = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 3.45) / 1.0))
        place(f, BUB_SUN, (290, 600), scale=1.25 * pop_scale(t, 2.55) * gone * (pulse_a if t > 2.95 else 1))
        place(f, BUB_SAFE, (790, 600), scale=1.25 * pop_scale(t, 2.7) * gone * (pulse_b if t > 3.45 else 1))
        place(f, QMARK, (540, 500), scale=pop_scale(t, 2.85, 0.25) * gone, angle=8 * math.sin(t * 4))

    f = camera(f, t)

    # the loop: a big paper wave rises over the beach and drains away to the start
    if T_WAVE0 <= t < T_WAVE3:
        if t < T_WAVE2:
            y = lerp(scene.H + 60, -440, ease_in_out(seg(t, T_WAVE0, T_WAVE1)))
        else:
            y = lerp(-440, scene.H + 80, ease_in_out(seg(t, T_WAVE2, T_WAVE3)))
        place(f, WAVE, (40 * math.sin(2 * math.pi * (t - T_WAVE0) / 1.2), y), shadow=False)
    return f


def _fade(img, k):
    out = img.copy()
    out.putalpha(img.getchannel("A").point(lambda v: int(v * k)))
    return out


CAM0 = (1.5, 330, 905)
CAM_KEYS = [
    (0.0,) + CAM0, (0.95,) + CAM0, (2.3, 1.12, 470, 1000), (2.8, 1.0, 540, 960),
    (4.6, 1.0, 540, 960), (5.1, 1.14, 400, 1060), (5.8, 1.14, 400, 1060), (6.3, 1.0, 540, 960),
    (8.45, 1.0, 540, 960), (8.75, 1.08, 470, 900), (10.95, 1.08, 470, 900), (11.4, 1.0, 540, 960),
    (15.0, 1.0, 540, 960), (15.45, 1.1, 545, 1040), (15.9, 1.1, 545, 1040), (16.35, 1.0, 540, 960),
    (T_WAVE1 - 0.001, 1.0, 540, 960), (T_WAVE1,) + CAM0, (DUR,) + CAM0]


def camera(f, t):
    z, cx, cy = 1.0, 540, 960
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
    if T_PLANT <= t < T_PLANT + 0.24:  # a little thunk shake (eased in and out)
        k = math.sin(math.pi * seg(t, T_PLANT, T_PLANT + 0.24))
        cx += 4 * k * math.sin(t * 95)
        cy += 3 * k * math.cos(t * 81)
        z = max(z, 1 + 0.015 * k)
    if z < 1.001:
        return f
    w, h = scene.W / z, scene.H / z
    left = min(max(cx - w / 2, 0), scene.W - w)
    top = min(max(cy - h / 2, 0), scene.H - h)
    return f.resize((scene.W, scene.H), Image.BICUBIC, box=(left, top, left + w, top + h))


# ---------------------------------------------------------------- audio
def build_audio(path):
    music, sfx, amb = A.Mix(DUR), A.Mix(DUR), A.Mix(DUR)
    M = A.midi
    amb.add(0.0, P.sea(DUR + 0.5, 1.0, 6.0))
    # HOOK: jingle + hot-sand hop-hop (a yip and a sizzle on every landing, leading in from the loop)
    A.jingle(music, 0.02)
    for k, tl in enumerate(landings()):
        tt = tl if tl >= 0 else tl + DUR
        if tt < DUR - 0.05:
            sfx.add(tt, P.yip(0.8, 820 + 90 * (k % 3)))
            sfx.add(tt, P.sizzle(0.2, 0.9))
    sfx.add(0.97, A.tap(0.6))
    # desire: phew + dream castle
    music.add(1.0, A.pad([M(60), M(64), M(67)], 1.3, 0.35))
    for tt, ch, up in ((1.25, "C", False), (1.5, "C", True), (1.75, "F", False), (2.0, "F", True),
                       (2.25, "G", False)):
        A.strum(music, tt, ch, 0.6, up)
    for tt, m in ((1.25, 72), (1.5, 76), (1.75, 77), (2.0, 81), (2.25, 79)):
        music.add(tt, P.steelpan(M(m), 0.8, 0.8))
    sfx.add(1.25, A.pop(0.7))
    sfx.add(1.3, A.twinkle(0.9))
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
    # slapstick: dig dig dig, the ears wilt, the lolly drips (plip!), wah-wah
    for i, d in enumerate(DIGS):
        sfx.add(d, P.scrape(0.9))
        music.add(d, A.pluck(M(55 + (i % 2) * 5), 0.25, 0.5))
    sfx.add(4.65, P.droop_whistle(1.0, 0.9))
    sfx.add(4.95, A.pop(0.4))
    sfx.add(T_PLIP, P.plip(1.0))
    sfx.add(T_PLIP + 0.02, A.boing(0.3, 360))
    music.add(5.55, A.wah_down(0.85))
    sfx.add(6.0, A.tap(0.4))
    # Crinkle: whoosh in, thunk (plant), fwump (umbrella opens), ahh
    sfx.add(5.95, A.whoosh(0.5, 0.9))
    sfx.add(6.12, A.boing(0.3, 300))
    sfx.add(6.37, A.boing(0.3, 330))
    sfx.add(T_PLANT, P.thunk(1.0))
    sfx.add(T_OPEN, P.fwump(1.0))
    sfx.add(T_OPEN + 0.04, A.pop(0.7))
    sfx.add(7.0, P.ahh(0.9))
    sfx.add(7.02, A.chime_up(0.6, (84, 88, 91)))
    for tt, ch in ((6.6, "F"), (7.1, "C")):
        A.strum(music, tt, ch, 0.55)
        music.add(tt, A.bass(M({"F": 41, "C": 48}[ch]), 0.5, 0.6))
    # hat toss: flick, slide whistle up and down, plop + ear boing
    sfx.add(T_FLICK - 0.05, A.pop(0.6))
    sfx.add(T_FLICK, P.droop_whistle(0.25, 0.5)[::-1])
    sfx.add(T_FLICK + 0.25, P.droop_whistle(0.25, 0.5))
    sfx.add(T_HAT, A.tap(0.8))
    sfx.add(T_HAT + 0.02, A.boing(0.6, 280))
    A.strum(music, T_HAT, "G", 0.6)
    music.add(T_HAT, A.bass(M(43), 0.5, 0.6))
    # bottle + sip 1, 2, 3 (ears spring up a little on each)
    sfx.add(T_GIVE, A.pop(0.7))
    A.strum(music, T_GIVE, "C", 0.5)
    for i, (sp, m) in enumerate(zip(SIPS, (84, 88, 91))):
        sfx.add(sp, A.glock(M(m), 1.2, 0.9))
        music.add(sp, A.ks_pluck(M(m - 24), 1.0, 0.8))
        music.add(sp, A.bass(M(48), 0.4, 0.5))
        sfx.add(sp + 0.02, A.slurp(0.7))
        sfx.add(sp + 0.25, P.gulp(0.8))
        sfx.add(sp + 0.3, P.spring_up(0.8, 380 + 90 * i))
    for tt, ch in ((9.25, "F"), (10.15, "G")):
        A.strum(music, tt, ch, 0.4, True)
    sfx.add(11.0, A.chime_up(0.9))
    sfx.add(11.05, A.boing(0.35, 340))
    sfx.add(T_DOWN, A.tap(0.5))
    # payoff: pat pat, towers pop, flag, check, hearts (summery steel-pan + uke)
    for p in PATS_SN + PATS_CR:
        sfx.add(p, A.tap(0.7))
    for p in (PATS_SN[1], PATS_CR[1], T_FLAG):
        sfx.add(p, A.pop(0.8))
    sfx.add(T_FLAG, A.twinkle(0.7))
    sfx.add(T_CHECK, A.glock(M(96), 1.0, 0.7))
    sfx.add(T_CHECK + 0.02, A.twinkle(0.7))
    for tt, ch, up in ((11.6, "C", False), (11.85, "C", True), (12.1, "F", False), (12.35, "F", True),
                       (12.6, "G", False), (12.85, "G", True), (13.1, "C", False), (13.35, "C", True),
                       (13.6, "F", False), (13.85, "G", True)):
        A.strum(music, tt, ch, 0.7, up)
    for tt, m in ((11.6, 48), (12.1, 41), (12.6, 43), (13.1, 48), (13.6, 41)):
        music.add(tt, A.bass(M(m), 0.45, 0.8))
    for tt, m in ((12.85, 79), (13.1, 84), (13.35, 83), (13.6, 81), (13.85, 79)):
        music.add(tt, P.steelpan(M(m), 0.7, 0.7))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.45))
    sfx.add(13.4, A.boing(0.35, 340))
    for tt, ch, up in ((14.1, "Am", False), (14.35, "Am", True), (14.6, "F", False)):
        A.strum(music, tt, ch, 0.6, up)
    for tt, m in ((14.1, 45), (14.6, 41)):
        music.add(tt, A.bass(M(m), 0.45, 0.7))
    sfx.add(14.6, A.boing(0.3, 300))
    # paw-bump (signature)
    sfx.add(14.85, A.snare_roll(0.6, 0.8))
    sfx.add(15.45, A.boop(0.9))
    A.jingle(music, 15.47, 1.0, ending=True)
    sfx.add(15.5, A.twinkle(0.8))
    # the loop wave: uh-oh, splash, bubbles, and the hot hops start again
    sfx.add(16.1, A.uh_oh(0.7))
    sfx.add(T_WAVE0, P.splash(0.9, 1.0))
    sfx.add(T_WAVE1 - 0.05, P.bubbles(0.7, 0.8))
    A.strum(music, 16.4, "F", 0.5)
    A.strum(music, 16.9, "G7", 0.5)
    music.add(17.0, A.pad([M(55), M(59), M(62)], 1.0, 0.25))
    for i, m in enumerate((67, 69, 71)):
        music.add(17.45 + i * 0.16, P.steelpan(M(m), 0.4, 0.5))

    m = A.reverb(music.normalized(), 0.24)
    s = A.reverb(sfx.normalized(), 0.08)
    a = amb.normalized()
    y = 0.55 * m / max(1e-9, abs(m).max()) + 0.7 * s / max(1e-9, abs(s).max()) + 0.12 * a / max(1e-9, abs(a).max())
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.01)


# ---------------------------------------------------------------- output
def render(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    wav = os.path.join(ROOT, "build", "ep10_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep10_hot_sunny_day.mp4")
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
    times = times or [0.0, 0.5, 1.8, 3.4, 4.8, 5.3, 5.7, 6.4, 6.9, 7.6, 8.2, 8.9, 9.8, 10.7,
                      11.3, 12.0, 12.7, 13.3, 15.6, 16.6, 17.3]
    cols = 7
    rows = math.ceil(len(times) / cols)
    sheet = Image.new("RGB", (216 * cols, 404 * rows), "white")
    d = ImageDraw.Draw(sheet)
    for i, tt in enumerate(times):
        im = render_frame(tt).convert("RGB").resize((216, 384))
        x, y = (i % cols) * 216, (i // cols) * 404
        sheet.paste(im, (x, y + 20))
        d.text((x + 6, y + 4), f"{tt:.2f}s", fill="black")
    sheet.save(path)
    print("wrote", path)


KEYS = [(0.0, "0.0s hot sand hook"), (3.4, "3.4s choice"), (5.45, "5.5s noodle ears + plip"),
        (6.95, "7.0s shade!"), (7.95, "8.0s hat on"), (9.95, "10.0s sip 2"), (12.9, "12.9s castle done"),
        (15.6, "15.6s paw-bump")]


def key_sheet(path, keys=KEYS, w=360):
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
        stills(os.path.join(ROOT, "build", "ep10_stills.png"))
    elif "--keys" in sys.argv:
        os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
        key_sheet(os.path.join(ROOT, "reviews", "ep10_keys.png"))
    else:
        render(os.path.join(ROOT, "output"))
