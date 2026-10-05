"""Episode 1 (v2) — Can Snip Wait? ⏳

Hook in second 0, a "✋ or ⏳?" choice for kids to shout at, a gentle slapstick
startle, counting while the drink cools, a grown-up handling the hot cups,
the signature paw-bump, and a seamless loop (frame 18.0s == frame 0).

Run:  python3 episodes/ep01_v2_can_snip_wait.py            (render -> output/)
      python3 episodes/ep01_v2_can_snip_wait.py --stills    (contact sheet)
"""
import math
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402

import audio as A  # noqa: E402
import scene  # noqa: E402
from characters import Character  # noqa: E402
from paperlib import (ease_in_out, ease_out, ease_out_back, lerp, place,  # noqa: E402
                      seg)

FPS = 30
DUR = 18.0
TY = scene.TABLE_Y
CUP_X = 545
CUP_S = 1.15
CUP_REST_Y = TY + 8
RIM_DY = (196 - 34) * CUP_S          # cup pivot (bottom) -> rim
CR_REST_L = 346                      # Crinkle's left arm hanging (== -14)

BG = scene.background_v2()
CUP = scene.cup().scaled(CUP_S)
STEAM = [s.scaled(CUP_S) for s in scene.steam_frames(16)]
HAND = scene.grown_up_hand()
HEART_STEAM = scene.steam_heart()
SIGN_NO = scene.sign_no_touch()
TIMER = scene.hourglass_frames(24)
NUMS = [scene.numeral(1, (244, 112, 104)), scene.numeral(2, (255, 196, 52)), scene.numeral(3, (84, 182, 222))]
BUB_HAND = scene.choice_bubble("✋", (240, 110, 100))
BUB_WAIT = scene.choice_bubble("⏳", (90, 190, 120))
QMARK = scene.icon("❓", 120)
CHECK = scene.icon("✅", 120)
BURST = scene.steam_burst()
SPARKLE = scene.sparkle()
HEARTS = [scene.heart(c, 80) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120), (255, 150, 170))]
SNIP = Character("snip", 1.15)
CR = Character("crinkle", 1.2)

SNIP_BLINKS = (1.75, 6.1, 7.9, 9.55, 12.15, 14.35, 16.75)
CR_BLINKS = (6.95, 8.15, 9.7, 12.75, 14.3)
COUNTS = (9.0, 10.0, 11.0)
HEART_PLAN = ((13.5, 250, 900), (13.65, 445, 850), (13.8, 545, 990), (13.95, 330, 790))


# ---------------------------------------------------------------- helpers
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


# ---------------------------------------------------------------- Snip
def snip_state(t):
    s = dict(x=330, hop=0.0, sq=1.0, lean=-8.0, tilt=0.0, arm_l=-14.0, arm_r=14.0, eyes="normal",
             mouth="w", look=(0, 0), head_dy=0.0, ears=[0.0, 0.0], ear_stretch=1.0, frizz=0.0)
    idle_ear = 2.0 * math.sin(2 * math.pi * t / 3.0)

    if t < 1.0:                       # HOOK: paw sneaks toward the steaming cup
        p = ease_in_out(seg(t, 0.0, 1.0))
        s.update(lean=lerp(-8, -10, p), arm_r=lerp(30, 52, p), eyes="wide", mouth="o", look=(7, 3))
    elif t < 2.5:                     # DESIRE: sparkly eyes, yum, steam heart
        s.update(lean=-10, arm_r=52, eyes="sparkle", mouth="yum", look=(5, -6), tilt=-4 * ease_out(seg(t, 1.0, 1.4)))
        e = spring(t, 1.0, 10, 4.0, 3.0)
        s["ears"] = [e, -e]
    elif t < 4.5:                     # FREEZE for the choice
        s.update(lean=-10, arm_r=52, eyes="sparkle", mouth="yum", look=(5, -6), tilt=-4)
        e = spring(2.5, 1.0, 10, 4.0, 3.0)
        s["ears"] = [e, -e]
        return s
    elif t < 4.85:                    # the paw creeps closer...
        p = ease_in_out(seg(t, 4.5, 4.85))
        s.update(lean=lerp(-10, -12, p), arm_r=lerp(52, 68, p), eyes="sparkle", mouth="yum", look=(6, 2),
                 tilt=lerp(-4, 0, p))
    elif t < 6.0:                     # PSSHH! startle
        h, sq = hop_curve(t, 4.88, 5.3, 1, 70)
        s.update(x=lerp(330, 290, ease_out(seg(t, 4.88, 5.25))), hop=h, sq=sq, eyes="wide", mouth="O",
                 lean=lerp(6, 0, ease_out(seg(t, 5.2, 5.8))), look=(6, 0))
        up = 1 - ease_in_out(seg(t, 5.3, 5.6))
        s["arm_l"], s["arm_r"] = lerp(-14, -150, up), lerp(14, 150, up)
        stiff = 1 - ease_in_out(seg(t, 5.45, 5.85))
        s["ears"] = [lerp(0, -9, stiff), lerp(0, 9, stiff)]
        s["ear_stretch"] = lerp(1.0, 1.22, stiff)
        s["frizz"] = pop_scale(t, 4.88, 0.15) * (1 - ease_in_out(seg(t, 5.35, 5.7)))
        if t > 5.55:
            droop = ease_out(seg(t, 5.55, 5.9)) * 26
            s.update(eyes="worried", mouth="wobble", ears=[droop, -droop])
        return s
    elif t < 8.0:                     # Crinkle warns; Snip understands and nods
        s["x"] = 290
        droop = 26 * (1 - ease_in_out(seg(t, 7.0, 7.6)))
        s.update(eyes="worried" if t < 7.1 else "normal", mouth="wobble" if t < 7.1 else "w",
                 look=(6, -5), ears=[droop, -droop], lean=0)
        s["head_dy"] = 14 * (math.sin(math.pi * seg(t, 7.15, 7.45)) + math.sin(math.pi * seg(t, 7.55, 7.85)))
    elif t < 11.4:                    # wait & count 1-2-3
        s.update(x=290, lean=0, look=(7, -6))
        for c in COUNTS:
            h, sq = hop_curve(t, c, c + 0.32, 1, 18)
            if h or sq != 1.0:
                s["hop"], s["sq"] = h, sq
            if 0 <= t - c < 0.3:
                s["mouth"] = "o"
            e = spring(t, c, 7, 5.0, 5.0)
            s["ears"][0] += e
            s["ears"][1] -= e
    elif t < 12.4:                    # it's cool now!
        s.update(x=290, lean=0, look=(6, 2), eyes="sparkle" if t > 12.0 else "normal",
                 mouth="yum" if t > 12.0 else "w")
    elif t < 13.4:                    # step in and sip
        h, sq = hop_curve(t, 12.4, 12.75, 1, 20)
        p = ease_in_out(seg(t, 12.4, 12.8))
        sip = 1.5 * math.sin(2 * math.pi * 3 * max(0.0, t - 12.85)) if t > 12.85 else 0.0
        s.update(x=lerp(290, 385, p), hop=h, sq=sq, lean=lerp(0, -14, p) + sip, look=(6, 3),
                 eyes="closed" if t > 12.8 else "sparkle", mouth="blow" if t > 12.8 else "yum")
    elif t < 14.6:                    # "ahh" — happy
        h, sq = hop_curve(t, 13.6, 13.92, 1, 26)
        s.update(x=385, hop=h, sq=sq, lean=lerp(-14, 0, ease_out(seg(t, 13.4, 13.7))), eyes="happy", mouth="grin")
        e = spring(t, 13.5, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
    elif t < 16.0:                    # paw-bump
        h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
        s.update(x=lerp(385, 415, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq, lean=0, eyes="happy",
                 mouth="grin")
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_r"] = lerp(lerp(14, -6, wind), 165, swing)
        e = spring(t, 15.45, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
    elif t < 17.0:                    # wave bye to Crinkle, hop home, look up at the grown-up's hand
        h, sq = hop_curve(t, 16.0, 16.45, 1, 30)
        s.update(x=lerp(415, 330, ease_in_out(seg(t, 16.0, 16.45))), hop=h, sq=sq, lean=0,
                 eyes="happy" if t < 16.6 else "normal", mouth="grin" if t < 16.6 else "w",
                 look=(7, 0) if t < 16.6 else (4, -7))
        s["arm_r"] = lerp(165, 120 + 22 * math.sin((t - 16.0) * 16), ease_out(seg(t, 16.0, 16.15)))
        s["arm_r"] = lerp(s["arm_r"], 14, ease_in_out(seg(t, 16.55, 16.9)))
    else:                             # a NEW hot cup... eyes go wide, paw starts sneaking (== frame 0)
        p = ease_in_out(seg(t, 17.1, 18.0))
        s.update(lean=lerp(0, -8, p), arm_r=lerp(14, 30, ease_in_out(seg(t, 17.4, 18.0))),
                 eyes="wide" if t > 17.15 else "normal", mouth="o" if t > 17.15 else "w",
                 look=(7, 3) if t > 17.15 else (4, -7))
        e = spring(t, 17.15, 9, 5.0, 4.0)
        s["ears"] = [e, -e]

    s["ears"][0] += idle_ear
    s["ears"][1] -= idle_ear
    if s["hop"] == 0:
        s["sq"] *= breath(t)
    return s


# ---------------------------------------------------------------- Crinkle
def crinkle_state(t):
    s = dict(x=810, hop=0.0, sq=1.0, lean=0.0, arm_l=CR_REST_L, arm_r=14.0, eyes="normal", mouth="smile",
             look=(0, 0), head_dy=0.0, prop=None)
    if t < 6.0 or t >= 16.8:
        s["x"] = 1450
        return s
    if t < 8.0:                       # slides in with the warning sign
        s["x"] = lerp(1450, 810, ease_out_back(seg(t, 6.0, 6.5), 1.2))
        s["lean"] = 12 * (1 - ease_out(seg(t, 6.0, 6.9)))
        s["arm_l"] = lerp(CR_REST_L, 192, ease_out_back(seg(t, 6.35, 6.65)))
        s.update(eyes="worried" if t < 7.0 else "normal", mouth="o" if t < 7.0 else "smile", look=(-6, 0))
        s["prop"] = ("sign", pop_scale(t, 6.45), 0.0)
        s["head_dy"] = 12 * math.sin(math.pi * seg(t, 7.2, 7.5))
    elif t < 11.6:                    # shows the sand timer, flips it, counts
        s["arm_l"] = 192
        s.update(look=(-3, -7), eyes="normal", mouth="smile")
        if t < 8.25:
            s["prop"] = ("sign", 1 - ease_in_out(seg(t, 8.0, 8.25)), 0.0)
        elif t < 8.9:
            s["prop"] = ("timer0", pop_scale(t, 8.25, 0.25), 180 * ease_out_back(seg(t, 8.5, 8.85)))
        else:
            lv = 1 - seg(t, 8.9, 11.2)
            shrink = 1 - ease_in_out(seg(t, 11.25, 11.45))
            s["prop"] = ("timer", shrink, lv)
            s["arm_l"] = lerp(192, CR_REST_L, ease_in_out(seg(t, 11.3, 11.6)))
        for c in COUNTS:
            s["head_dy"] += 10 * math.sin(math.pi * seg(t, c, c + 0.3))
            if 0 <= t - c < 0.3:
                s["mouth"] = "o"
    elif t < 12.4:                    # carefully checks the cup: cool!
        reach = ease_in_out(seg(t, 11.6, 11.9)) * (1 - ease_in_out(seg(t, 12.1, 12.4)))
        s.update(arm_l=lerp(CR_REST_L, 318, reach), lean=6 * reach, look=(-6, 3),
                 eyes="happy" if t > 12.0 else "normal", mouth="grin" if t > 12.0 else "o")
    elif t < 14.6:                    # watches Snip sip, then a happy hop
        h, sq = hop_curve(t, 13.6, 13.92, 1, 24)
        s.update(hop=h, sq=sq, eyes="happy", mouth="smile" if t < 13.4 else "grin", look=(-6, 2))
    elif t < 16.0:                    # paw-bump
        h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
        s.update(x=lerp(810, 730, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq, eyes="happy", mouth="grin")
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_l"] = lerp(lerp(CR_REST_L, 360, wind), 198, swing)
    else:                             # waves bye and hops away
        h, sq = hop_curve(t, 16.05, 16.8, 2, 40)
        s.update(x=lerp(730, 1450, ease_in_out(seg(t, 16.05, 16.8))), hop=h, sq=sq, eyes="happy", mouth="grin",
                 lean=-6)
        s["arm_l"] = lerp(198, CR_REST_L, ease_out(seg(t, 16.0, 16.2)))
        s["arm_r"] = 140 + 22 * math.sin((t - 16.0) * 16)
    if s["hop"] == 0:
        s["sq"] *= breath(t + 0.7, 2.25, 0.01)
    return s


# ---------------------------------------------------------------- cups, steam, straw
def cup_positions(t):
    """Returns list of (cup_x, cup_y, has_steam, carried, steam_level, hand_y_or_None)."""
    out = []
    rest = CUP_REST_Y
    grip_dy = -RIM_DY + 12           # hand fingertip relative to cup pivot
    # cup A — removed by the grown-up at 14.1
    if t < 14.75:
        y = rest - 1700 * ease_in(seg(t, 14.15, 14.75))
        steam = steam_level(t)
        hand = None
        if 13.7 <= t:
            hand = lerp(-700, rest + grip_dy, ease_out(seg(t, 13.7, 14.0))) if t < 14.15 else y + grip_dy
        out.append((CUP_X, y, steam, t >= 14.15, hand))
    # cup B — brought in by the grown-up from 16.3
    if t >= 16.3:
        y = lerp(rest - 1750, rest, ease_out(seg(t, 16.3, 16.95)))
        hand = y + grip_dy if t < 17.05 else lerp(rest + grip_dy, -700, ease_in_out(seg(t, 17.05, 17.6)))
        out.append((CUP_X, y, 1.0, t < 16.95, hand if t < 17.6 else None))
    return out


def ease_in(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * t


def steam_level(t):
    lv = 1.0
    for i, c in enumerate(COUNTS):
        lv = min(lv, 1 - (i + 1) / 3 * ease_in_out(seg(t, c, c + 0.35)) if t >= c else lv)
    return max(0.0, lv)


def draw_steam(f, x, y, level, t):
    if level <= 0.02:
        return
    idx0 = int(t * 16 * 13 / DUR)
    for i, dx in enumerate((-50, 0, 50)):
        place(f, STEAM[(idx0 + i * 5) % 16], (x + dx, y - RIM_DY - 6), sy=level, alpha=min(1, level * 1.6) * (0.95 - 0.1 * i))


_straw_cache = {}


def straw_for(tip):
    key = (round(tip[0] / 2) * 2, round(tip[1] / 2) * 2)
    if key not in _straw_cache:
        bottom = (CUP_X + 10, CUP_REST_Y - RIM_DY + 70)
        bend = (CUP_X + 10, min(bottom[1] - 120, key[1] + 50))
        _straw_cache[key] = scene.straw_sprite(bottom, key, bend)
    return _straw_cache[key]


def straw_tip(t, sn):
    straight = (CUP_X + 10, CUP_REST_Y - RIM_DY - 150)
    mouth = SNIP.mouth_pt(sn["x"], TY, sn["hop"], sn["lean"], sn["sq"], sn["head_dy"], sn["tilt"])
    mouth = (mouth[0] + 4, mouth[1] + 4)
    k = ease_in_out(seg(t, 12.45, 12.8)) * (1 - ease_in_out(seg(t, 13.4, 13.7)))
    return (lerp(straight[0], mouth[0], k), lerp(straight[1], mouth[1], k))


# ---------------------------------------------------------------- frame
def render_frame(t):
    f = BG.copy()
    sn = snip_state(t)
    cr = crinkle_state(t)
    cups = cup_positions(t)

    # cups resting on the table (behind the characters)
    for (x, y, steam, carried, hand) in cups:
        if carried:
            continue
        if 12.2 <= t < 14.15:
            tip = straw_tip(t, sn)
            place(f, straw_for(tip), (CUP_X + 10, CUP_REST_Y - RIM_DY + 70), sy=pop_scale(t, 12.2, 0.2))
        place(f, CUP, (x, y))
        draw_steam(f, x, y, steam, t)

    # steam heart drifting up (desire)
    if 1.1 <= t < 2.45:
        p = seg(t, 1.1, 2.45)
        place(f, HEART_STEAM, (lerp(CUP_X, 565, p), lerp(1230, 880, ease_out(p))), scale=lerp(0.5, 1.1, p),
              alpha=math.sin(math.pi * min(1, p * 1.15)) if p < 0.87 else max(0, 1 - (p - 0.87) * 8),
              angle=6 * math.sin(t * 5))

    snip_blink = blinking(t, SNIP_BLINKS) and not frozen(t)
    SNIP.draw(f, sn["x"], TY, hop=sn["hop"], lean=sn["lean"], head_tilt=sn["tilt"], arm_l=sn["arm_l"],
              arm_r=sn["arm_r"], eyes=sn["eyes"], mouth=sn["mouth"], look=sn["look"], squash=sn["sq"],
              head_dy=sn["head_dy"], blink=snip_blink, ears=tuple(sn["ears"]), ear_stretch=sn["ear_stretch"],
              frizz=sn["frizz"])

    if cr["prop"] is not None:
        kind, k, v = cr["prop"]
        tip = CR.paw_tip(cr["x"], TY, "l", cr["arm_l"], cr["hop"], cr["lean"], cr["sq"])
        if kind == "sign" and k > 0.01:
            place(f, SIGN_NO, tip, scale=k, angle=3 * math.sin(t * 5))
        elif kind == "timer0" and k > 0.01:
            place(f, TIMER[0], (tip[0], tip[1] - 100), scale=k, angle=v)
        elif kind == "timer" and k > 0.01:
            place(f, TIMER[int(round(v * (len(TIMER) - 1)))], (tip[0], tip[1] - 100), scale=k,
                  angle=2 * math.sin(t * 4))
    CR.draw(f, cr["x"], TY, hop=cr["hop"], lean=cr["lean"], arm_l=cr["arm_l"], arm_r=cr["arm_r"],
            eyes=cr["eyes"], mouth=cr["mouth"], look=cr["look"], squash=cr["sq"], head_dy=cr["head_dy"],
            blink=blinking(t, CR_BLINKS))

    # carried cups + the grown-up's hand (in front of everything)
    for (x, y, steam, carried, hand) in cups:
        if carried:
            if 14.15 <= t < 14.75:
                place(f, straw_for((CUP_X + 10, CUP_REST_Y - RIM_DY - 150)), (CUP_X + 10, y - RIM_DY + 70))
            place(f, CUP, (x, y))
            draw_steam(f, x, y, steam, t)
        if hand is not None:
            place(f, HAND, (x, hand))

    # PSSHH burst
    if 4.85 <= t < 5.7:
        place(f, BURST, (CUP_X, CUP_REST_Y - RIM_DY + 10), scale=pop_scale(t, 4.85, 0.18),
              alpha=1 - ease_in_out(seg(t, 5.35, 5.7)), angle=4 * math.sin(t * 20))

    # counting numerals
    for i, c in enumerate(COUNTS):
        if c <= t < c + 0.95:
            out = 1 - ease_in_out(seg(t, c + 0.75, c + 0.95))
            place(f, NUMS[i], (540, 640), scale=pop_scale(t, c, 0.28) * out, angle=-6 + 4 * math.sin(t * 6))

    if 12.0 <= t < 12.55:
        place(f, CHECK, (CUP_X, 1150), scale=pop_scale(t, 12.0, 0.25) * (1 - ease_in_out(seg(t, 12.35, 12.55))))

    for i, (t0, x, y) in enumerate(HEART_PLAN):
        if t0 <= t < 14.7:
            p = seg(t, t0, 14.7)
            place(f, HEARTS[i], (x + 10 * math.sin(t * 3 + i), y - 160 * p), scale=pop_scale(t, t0, 0.25),
                  alpha=1 - ease_in_out(seg(t, 14.3, 14.7)), angle=10 * math.sin(t * 2.5 + i))

    if 15.45 <= t < 16.2:
        sn_tip = SNIP.paw_tip(sn["x"], TY, "r", sn["arm_r"], sn["hop"], sn["lean"], sn["sq"])
        cr_tip = CR.paw_tip(cr["x"], TY, "l", cr["arm_l"], cr["hop"], cr["lean"], cr["sq"])
        mid = ((sn_tip[0] + cr_tip[0]) / 2, (sn_tip[1] + cr_tip[1]) / 2 - 10)
        place(f, SPARKLE, mid, scale=pop_scale(t, 15.45, 0.22) * 0.9, angle=(t - 15.45) * 60,
              alpha=1 - ease_in_out(seg(t, 15.9, 16.2)))

    # FREEZE: dim + choice bubbles
    if 2.5 <= t < 4.6:
        dim = 0.32 * ease_out(seg(t, 2.5, 2.62)) * (1 - ease_in_out(seg(t, 4.4, 4.58)))
        if dim > 0.01:
            shade = Image.new("RGBA", f.size, (30, 26, 52, int(255 * dim)))
            f.alpha_composite(shade)
        gone = 1 - ease_in_out(seg(t, 4.4, 4.55))
        pulse_a = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 2.95) / 1.0))
        pulse_b = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 3.45) / 1.0))
        place(f, BUB_HAND, (300, 600), scale=pop_scale(t, 2.55) * gone * (pulse_a if t > 2.95 else 1))
        place(f, BUB_WAIT, (780, 600), scale=pop_scale(t, 2.7) * gone * (pulse_b if t > 3.45 else 1))
        place(f, QMARK, (540, 520), scale=pop_scale(t, 2.85, 0.25) * gone, angle=8 * math.sin(t * 4))

    return camera(f, t)


CAM_KEYS = [
    (0.0, 1.6, 480, 1150), (1.0, 1.63, 480, 1150), (1.45, 1.12, 470, 1080), (2.45, 1.12, 470, 1080),
    (2.65, 1.0, 540, 960), (4.6, 1.0, 540, 960), (4.85, 1.3, 470, 1150), (5.25, 1.3, 470, 1150),
    (5.7, 1.0, 540, 960), (8.6, 1.0, 540, 960), (11.2, 1.08, 560, 1000), (11.5, 1.0, 540, 960),
    (12.5, 1.0, 540, 960), (12.9, 1.25, 470, 1130), (13.5, 1.25, 470, 1130), (13.9, 1.0, 540, 960),
    (15.2, 1.0, 540, 960), (15.45, 1.12, 550, 1060), (15.9, 1.12, 550, 1060), (16.3, 1.0, 540, 960),
    (17.0, 1.0, 540, 960), (DUR, 1.6, 480, 1150)]


def camera(f, t):
    z, cx, cy = 1.0, 540, 960
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
    if 4.85 <= t < 5.3:  # camera shake on PSSHH
        k = 1 - seg(t, 4.85, 5.3)
        cx += 9 * k * math.sin(t * 95)
        cy += 7 * k * math.cos(t * 81)
        z = max(z, 1.02)
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
    # hook + desire
    A.jingle(music, 0.02)
    for tt, ch, up in ((1.0, "C", False), (1.25, "C", True), (1.5, "F", False), (1.75, "F", True),
                       (2.0, "G", False), (2.25, "G", True)):
        A.strum(music, tt, ch, 0.7, up)
    music.add(1.0, A.bass(M(48), 0.5, 0.7))
    music.add(1.5, A.bass(M(53), 0.5, 0.7))
    music.add(2.0, A.bass(M(55), 0.5, 0.7))
    sfx.add(1.0, A.twinkle(0.9))
    sfx.add(2.4, A.pop(0.6))
    # freeze: tick-tock + soft pad
    music.add(2.55, A.pad([M(48), M(55)], 2.0, 0.25))
    k = 0
    tt = 2.75
    while tt < 4.4:
        sfx.add(tt, A.woodblock(k % 2 == 0, 0.8))
        tt += 0.25
        k += 1
    for tt in (2.55, 2.7):
        sfx.add(tt, A.pop(0.7))
    sfx.add(2.85, A.glock(M(91), 0.6, 0.4))
    sfx.add(4.42, A.pop(0.6))
    # sneaky creep, then PSSHH + startle + sad trombone
    for i, m in enumerate((64, 65, 66, 67)):
        music.add(4.5 + i * 0.085, A.pluck(M(m - 12), 0.3, 0.6))
    sfx.add(4.85, A.psshh(1.0))
    sfx.add(4.9, A.boing(0.9, 320))
    sfx.add(4.88, A.snare_roll(0.15, 0.8))
    music.add(5.35, A.wah_down(0.9))
    # Crinkle + warning sign
    sfx.add(5.98, A.whoosh(0.5, 1.0))
    sfx.add(6.45, A.glock(M(91), 1.2, 0.8))
    sfx.add(6.5, A.glock(M(88), 1.2, 0.55))
    for tt, ch in ((6.6, "Am"), (7.1, "F"), (7.6, "C")):
        A.strum(music, tt, ch, 0.55)
        music.add(tt, A.bass(M({"Am": 45, "F": 41, "C": 48}[ch]), 0.5, 0.6))
    for tt in (7.2, 7.6):
        sfx.add(tt, A.tap(0.5))
    # timer + counting
    sfx.add(8.0, A.whoosh(0.3, 0.45))
    sfx.add(8.27, A.pop(0.6))
    sfx.add(8.5, A.whoosh(0.35, 0.7))
    sfx.add(8.85, A.tap(0.9))
    tt, k = 8.9, 0
    while tt < 11.2:
        sfx.add(tt, A.woodblock(k % 2 == 0, 0.45))
        tt += 0.5
        k += 1
    for c, m in zip(COUNTS, (84, 88, 91)):
        sfx.add(c, A.glock(M(m), 1.2, 0.9))
        music.add(c, A.ks_pluck(M(m - 24), 1.0, 0.8))
        music.add(c, A.bass(M(48), 0.4, 0.5))
        sfx.add(c + 0.02, A.tap(0.5))
    sfx.add(11.25, A.chime_up(0.9))
    # check the cup, straw, sip, ahh
    sfx.add(11.88, A.tap(0.5))
    sfx.add(12.0, A.glock(M(96), 1.0, 0.7))
    sfx.add(12.02, A.twinkle(0.7))
    sfx.add(12.2, A.pop(0.7))
    sfx.add(12.6, A.tap(0.4))
    sfx.add(12.85, A.slurp(1.0))
    music.add(13.35, A.pad([M(60), M(64), M(67)], 1.2, 0.5))
    sfx.add(13.4, A.twinkle(0.8, (96, 100, 103, 108)))
    for tt, ch, up in ((13.5, "C", False), (13.75, "C", True), (14.0, "G", False), (14.25, "G", True),
                       (14.5, "Am", False), (14.75, "F", False)):
        A.strum(music, tt, ch, 0.8, up)
    for tt, m in ((13.5, 48), (14.0, 43), (14.5, 45), (14.75, 41)):
        music.add(tt, A.bass(M(m), 0.45, 0.8))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.45))
    sfx.add(13.6, A.boing(0.35, 340))
    sfx.add(14.15, A.whoosh(0.5, 0.6))
    # paw-bump
    sfx.add(14.85, A.snare_roll(0.6, 0.8))
    sfx.add(15.45, A.boop(0.9))
    A.jingle(music, 15.47, 1.0, ending=True)
    sfx.add(15.5, A.twinkle(0.8))
    # bye + new cup + uh-oh, leading back into the jingle at 0:00
    sfx.add(16.05, A.boing(0.35, 300))
    sfx.add(16.42, A.boing(0.3, 330))
    sfx.add(16.4, A.whoosh(0.5, 0.6))
    sfx.add(16.95, A.tap(0.9))
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
    wav = os.path.join(ROOT, "build", "ep01_v2_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep01_v2_can_snip_wait.mp4")
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
    times = times or [0.0, 1.8, 3.4, 5.0, 6.8, 8.7, 10.2, 12.0, 13.0, 13.7, 15.6, 16.5, 17.5, 17.99]
    cols = 7
    rows = math.ceil(len(times) / cols)
    sheet = Image.new("RGB", (216 * cols, 404 * rows), "white")
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i, tt in enumerate(times):
        im = render_frame(tt).convert("RGB").resize((216, 384))
        x, y = (i % cols) * 216, (i // cols) * 404
        sheet.paste(im, (x, y + 20))
        d.text((x + 6, y + 4), f"{tt:.1f}s", fill="black")
    sheet.save(path)
    print("wrote", path)


if __name__ == "__main__":
    if "--stills" in sys.argv:
        stills(os.path.join(ROOT, "build", "ep01_v2_stills.png"))
    else:
        render(os.path.join(ROOT, "output"))
