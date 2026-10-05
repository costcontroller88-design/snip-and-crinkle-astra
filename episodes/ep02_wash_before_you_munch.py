"""Episode 2 — Wash Before You Munch? 🧼

A bright bathroom: two basins set in a pink wash counter, a round mirror, a porthole window.
Snip has come in from playing with muddy paws and reaches for one of two shiny apples. Choice:
muddy paw + apple, or soap bubbles? The paw creeps closer... and three friendly little germs pop
up on it and wave hello! Snip shakes the paw; the germs hang on, giggling. Crinkle arrives with a
bar of soap and mimes a scrub. Snip turns on the tap (wet), turns it off, catches the soap Crinkle
tosses over, and scrubs while counting 1, 2, 3 — each count, one germ floats away in a bubble,
waving bye. Toss the soap back, rinse, dry on the towel (flung back onto its hook), clean paws
sparkle, then both munch their apples. Signature paw-bump; Snip hops out to play again, a
grown-up's hand brings two new apples, and Snip hops back in with muddy paws (frame 18.0 == 0).

Run:  python3 episodes/ep02_wash_before_you_munch.py            (render -> output/)
      python3 episodes/ep02_wash_before_you_munch.py --stills   (contact sheet -> build/)
      python3 episodes/ep02_wash_before_you_munch.py --keys     (key frames -> reviews/ep02_keys.png)
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
import props_wash as PW  # noqa: E402
import scene  # noqa: E402
from characters import Character  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, seg  # noqa: E402

FPS = 30
DUR = 18.0
FY = PW.FLOOR_Y
SN_HOME = 330
CR_HOME = 785
CR_REST_L = 366                       # Crinkle's left arm hanging slightly inward (== 6), clear of the apples
NOZ = (PW.BASIN_X["snip"], 1244)      # Snip's tap nozzle (water starts here)
NOZ_CR = (PW.BASIN_X["crinkle"], 1244)
LEVER_AT = (412, 1338)
LEVER_CR = (868, 1338)
SOAP_DISH_AT = (880, PW.SURFACE_Y - 6)   # Crinkle puts the soap down here
APPLE_S = 1.45
PLATE_AT = (566, PW.SURFACE_Y + 2)
A1 = (538, 1312)                      # Snip's apple
A2 = (598, 1306)                      # Crinkle's apple
HOOK = (110, 1090)                    # towel hook, within reach of Snip's left paw
TOWEL_HANG = (HOOK[0], HOOK[1] + 30)
WASH_L, WASH_R = 52, -52              # Snip's arms with both paws under the tap

SNIP = Character("snip", 1.15)
CR = Character("crinkle", 1.2)
COUNTER = PW.counter()
FAUCET = PW.faucet(150)
FAUCET_CR = PW.faucet(150, flip=True)
LEVER = PW.lever()
LEVER_BASE = PW.lever_base()
WATER = PW.water_frames(108, 8)
SPLASH = PW.splash_sprite()
DRIP = PW.drip()
PLATE = PW.plate().scaled(1.25)
APPLES = [PW.apple(b).scaled(APPLE_S) for b in (0, 1, 2)]
GLINT = PW.apple_glint()
SOAP = PW.soap_bar()
DISH = PW.soap_dish()
TOWEL = PW.towel_hanging()
RING = PW.towel_ring()
FOAM = PW.foam()
BUBBLES = [PW.bubble(r) for r in (16, 22, 28)]
RING_BUBBLE = PW.bubble(46, ring_only=True)
GERMS = {(i, mood, wave): PW.germ(PW.GERM_COLORS[i], mood, wave, seed=i)
         for i in range(3) for mood in ("smile", "gasp", "giggle", "worried") for wave in range(4)}
MUD_L = PW.mud_overlay(0)
MUD_R = PW.mud_overlay(1, mirror=True)
SHAKE = PW.shake_lines()
SMALL_SPARK = PW.sparkle_small()
HAND = scene.grown_up_hand()
NUMS = [scene.numeral(1, (244, 112, 104)), scene.numeral(2, (255, 196, 52)), scene.numeral(3, (84, 182, 222))]
BUB_MUD = PW.choice_muddy()
BUB_SOAP = PW.choice_soap()
QMARK = icons.question()
CHECK = icons.check(130)
SPARKLE = scene.sparkle()
HEARTS = [scene.heart(c, 80) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120), (255, 150, 170))]


def _bg():
    bg = PW._wall()
    place(bg, PW._porthole(), (170, 330))
    place(bg, PW._shelf(), (800, 300))
    place(bg, PW._mirror(), (548, 720))
    place(bg, RING, HOOK)
    return bg


BG = _bg()

SNIP_BLINKS = (1.75, 6.2, 7.95, 9.45, 11.0, 14.3, 17.0)
CR_BLINKS = (6.9, 8.3, 9.9, 12.4, 14.35)
T_REACH, T_GERMS = 4.5, 4.82
TAP_ON1, TAP_OFF1, TAP_ON2, TAP_OFF2 = 7.92, 8.5, 10.72, 11.32
WATER1 = (8.04, 8.6)
WATER2 = (10.84, 11.42)
TOSS1 = (8.58, 8.86)                  # Crinkle -> Snip
TOSS2 = (10.48, 10.72)                # Snip -> Crinkle
COUNTS = (9.05, 9.65, 10.25)
T_TOWEL0, T_TOWEL1, T_FLING0, T_FLING1 = 11.45, 11.58, 11.95, 12.22
T_TADA = 12.22
T_TAKE = 12.62
BITES = (13.12, 13.48, 13.84)
T_GONE = BITES[2] + 0.12
HEART_PLAN = ((13.25, 200, 900), (13.45, 470, 820), (13.65, 760, 760), (13.85, 340, 700))
T_HAND0, T_HAND1, T_HAND2, T_HAND3 = 16.25, 16.85, 16.95, 17.45
T_BACK0, T_BACK1 = 16.9, 17.3


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
    sh = ch.shoulder_pt(st["x"], FY, side, st["hop"], st["lean"], st["sq"])
    a = math.degrees(math.atan2(target[0] - sh[0], target[1] - sh[1])) - st["lean"]
    return near(a, ref)


def tip(ch, st, side):
    arm = st["arm_l"] if side == "l" else st["arm_r"]
    return ch.paw_tip(st["x"], FY, side, arm, st["hop"], st["lean"], st["sq"])


def mouth(ch, st):
    return ch.mouth_pt(st["x"], FY, st["hop"], st["lean"], st["sq"], st["head_dy"], st.get("tilt", 0.0))


def tap_k(t, t0):
    """0 -> 1 -> 0 paw dab toward the tap lever starting at t0."""
    return ease_in_out(seg(t, t0, t0 + 0.1)) * (1 - ease_in_out(seg(t, t0 + 0.16, t0 + 0.28)))


def scrub(t):
    return 7 * math.sin(2 * math.pi * 6 * t) if COUNTS[0] - 0.15 <= t < TOSS2[0] - 0.05 else 0.0


def arc(p0, p1, k, height):
    return (lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k) - 4 * height * k * (1 - k))


# ---------------------------------------------------------------- Snip
def snip_state(t):
    if frozen(t):
        return snip_state(2.4999)
    s = dict(x=SN_HOME, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, arm_l=-14.0, arm_r=14.0, eyes="normal",
             mouth="w", look=(0, 0), head_dy=0.0, ears=[0.0, 0.0], ear_stretch=1.0, frizz=0.0)
    idle_ear = 2.0 * math.sin(2 * math.pi * t / 3.0)

    if t < 1.0:                       # HOOK: the muddy paw creeps toward the shiny apple
        p = ease_in_out(seg(t, 0.0, 1.0))
        s.update(lean=lerp(-6, -9, p), eyes="wide", mouth="o", look=(7, 4))
        s["arm_r"] = aim(SNIP, s, "r", (lerp(470, 480, p), lerp(1320, 1306, p)), 30)
    elif t < 2.5:                     # DESIRE: sparkly eyes, yum
        s.update(lean=-9, eyes="sparkle", mouth="yum", look=(6, 3), tilt=-5 * ease_out(seg(t, 1.0, 1.4)))
        s["arm_r"] = aim(SNIP, s, "r", (480, 1306), 30)
        e = spring(t, 1.0, 10, 4.0, 3.0)
        s["ears"] = [e, -e]
    elif t < T_GERMS:                 # the paw creeps closer...
        p = ease_in_out(seg(t, T_REACH, T_GERMS))
        s.update(lean=lerp(-9, -12, p), eyes="sparkle", mouth="yum", look=(6, 3), tilt=lerp(-5, 0, p))
        s["arm_r"] = aim(SNIP, s, "r", (lerp(480, 494, p), lerp(1306, 1298, p)), 30)
    elif t < 6.0:                     # GERMS pop up and wave! Snip yanks the paw up and shakes it
        yank = ease_out_back(seg(t, T_GERMS + 0.05, T_GERMS + 0.25))
        s.update(lean=lerp(-12, 4, ease_out(seg(t, T_GERMS, T_GERMS + 0.2))), eyes="wide", mouth="O", look=(6, 4))
        base = aim(SNIP, dict(s, lean=-12), "r", (494, 1298), 30)
        s["arm_r"] = lerp(base, 128, yank)
        s["ears"] = [lerp(0, -10, yank), lerp(0, 10, yank)]
        s["ear_stretch"] = 1 + 0.2 * yank * (1 - ease_in_out(seg(t, 5.55, 5.85)))
        s["frizz"] = pop_scale(t, T_GERMS + 0.03, 0.15) * (1 - ease_in_out(seg(t, 5.1, 5.35)))
        if 5.05 <= t < 5.6:           # shake shake shake!
            s["arm_r"] = 128 + 22 * math.sin(2 * math.pi * 7 * (t - 5.05))
            s["lean"] = 4 + 3 * math.sin(2 * math.pi * 7 * (t - 5.05) + 1)
            s.update(eyes="closed", mouth="flat")
        if t >= 5.6:                  # they're still there... worried look at the paw
            down = ease_in_out(seg(t, 5.6, 5.95))
            s["arm_r"] = lerp(128, 112, down)
            s["lean"] = lerp(4, 0, down)
            droop = 24 * ease_out(seg(t, 5.6, 5.9))
            s.update(eyes="worried", mouth="wobble", look=(7, -3), ears=[droop, -droop], tilt=6 * down)
    elif t < 7.9:                     # Crinkle shows the soap; Snip watches, then nods
        s.update(eyes="worried" if t < 6.75 else "normal", mouth="wobble" if t < 6.75 else "w", look=(8, -4))
        s["arm_r"] = lerp(112, 100, ease_in_out(seg(t, 6.0, 6.4)))
        droop = 24 * (1 - ease_in_out(seg(t, 6.75, 7.2)))
        s["ears"] = [droop, -droop]
        s["tilt"] = 6 * (1 - ease_in_out(seg(t, 6.0, 6.5)))
        s["head_dy"] = 14 * (math.sin(math.pi * seg(t, 7.3, 7.55)) + math.sin(math.pi * seg(t, 7.6, 7.85)))
    elif t < T_TADA:                  # WASH: wet, soap, scrub 1-2-3, rinse, dry
        s.update(look=(0, 6), eyes="normal", mouth="w")
        into = ease_in_out(seg(t, 7.9, 8.1))
        s["arm_l"] = lerp(-14, WASH_L, into)
        s["arm_r"] = lerp(100, WASH_R, into)
        for t0 in (TAP_ON1, TAP_OFF1, TAP_ON2, TAP_OFF2):
            k = tap_k(t, t0)
            if k > 0:
                s["arm_r"] = lerp(WASH_R if t0 > 8 else s["arm_r"], aim(SNIP, s, "r", LEVER_AT, 0), k)
        if TOSS1[0] <= t < TOSS1[1] + 0.2:   # catch the soap
            s.update(eyes="wide", mouth="o", look=(8, -4) if t < TOSS1[1] - 0.1 else (0, 6))
        sc = scrub(t)
        s["arm_l"] += sc
        s["arm_r"] += sc
        if COUNTS[0] - 0.15 <= t < TOSS2[0]:
            s.update(eyes="happy", mouth="grin")
        for c in COUNTS:
            if 0 <= t - c < 0.3:
                s["mouth"] = "o"
            s["head_dy"] += 12 * math.sin(math.pi * seg(t, c, c + 0.3))
            e = spring(t, c, 7, 5.0, 5.0)
            s["ears"][0] += e
            s["ears"][1] -= e
        if TOSS2[0] - 0.05 <= t < TOSS2[1]:  # flick the soap back
            k = math.sin(math.pi * seg(t, TOSS2[0] - 0.05, TOSS2[1]))
            s["arm_r"] = lerp(WASH_R, 60, k)
            s.update(look=(8, -3), eyes="normal", mouth="w")
        if WATER2[0] <= t < WATER2[1]:
            s.update(eyes="sparkle", mouth="w")
        if t >= T_TOWEL0:             # grab the towel, rub, fling it back onto the hook
            k = ease_out(seg(t, T_TOWEL0, T_TOWEL1))
            s["arm_l"] = lerp(WASH_L, aim(SNIP, s, "l", TOWEL_HANG, -60), k * (1 - ease_in_out(seg(t, T_TOWEL1, T_TOWEL1 + 0.12))))
            s["arm_l"] = lerp(s["arm_l"], WASH_L, ease_in_out(seg(t, T_TOWEL1, T_TOWEL1 + 0.12)))
            rub = 9 * math.sin(2 * math.pi * 5 * (t - T_TOWEL1)) if T_TOWEL1 <= t < T_FLING0 else 0.0
            s["arm_l"] += rub
            s["arm_r"] -= rub
            s.update(eyes="closed", mouth="w")
            if t >= T_FLING0:
                k = ease_out_back(seg(t, T_FLING0, T_FLING0 + 0.14))
                s["arm_l"] = lerp(WASH_L, -150, k)
                s.update(eyes="happy", mouth="grin", look=(-8, -6))
    elif t < T_TAKE:                  # TA-DA: clean paws up!
        h, sq = hop_curve(t, T_TADA, T_TADA + 0.3, 1, 22)
        up = ease_out_back(seg(t, T_TADA, T_TADA + 0.2))
        s.update(hop=h, sq=sq, eyes="sparkle", mouth="grin", look=(0, -4))
        s["arm_l"] = lerp(-150, -150, up)
        s["arm_r"] = lerp(WASH_R, 150, up)
        e = spring(t, T_TADA, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
    elif t < T_GONE + 0.2:            # MUNCH
        take = ease_in_out(seg(t, T_TAKE, T_TAKE + 0.22))
        lift = ease_in_out(seg(t, T_TAKE + 0.3, T_TAKE + 0.5))
        s.update(x=lerp(SN_HOME, SN_HOME + 22, take), lean=-10 * take * (1 - lift), eyes="sparkle", mouth="yum",
                 look=(7, 4))
        a_r = aim(SNIP, s, "r", (A1[0] - 30, A1[1] + 8), 40)
        a_l = aim(SNIP, s, "l", (A1[0] - 70, A1[1] + 24), 60)
        m = mouth(SNIP, s)
        held = (m[0] + 14, m[1] + 40)
        s["arm_r"] = lerp(lerp(150, a_r, take), aim(SNIP, s, "r", (held[0] + 34, held[1] + 18), -150), lift)
        s["arm_l"] = lerp(lerp(-150, a_l, take), aim(SNIP, s, "l", (held[0] - 34, held[1] + 18), 150), lift)
        if t >= T_TAKE + 0.5:
            s["mouth"] = munch_mouth(t, 0.0)
            s["eyes"] = "closed" if any(0 <= t - b < 0.25 for b in BITES) else "happy"
            s["head_dy"] = sum(10 * math.sin(math.pi * seg(t, b, b + 0.2)) for b in BITES)
        if t >= T_GONE:
            k = ease_in_out(seg(t, T_GONE, T_GONE + 0.2))
            s["arm_l"] = lerp(s["arm_l"], -14, k)
            s["arm_r"] = lerp(s["arm_r"], 14, k)
    elif t < 14.6:                    # yum! happy hop
        h, sq = hop_curve(t, 14.05, 14.37, 1, 26)
        s.update(x=SN_HOME + 22, hop=h, sq=sq, eyes="happy", mouth="grin" if t > 13.95 else "blow")
        e = spring(t, 14.05, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
    elif t < 16.0:                    # PAW-BUMP
        h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
        s.update(x=lerp(SN_HOME + 22, 398, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq, eyes="happy",
                 mouth="grin")
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_r"] = lerp(lerp(14, -6, wind), 165, swing)
        e = spring(t, 15.45, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
    elif t < T_BACK0:                 # wave bye and hop out to play
        h, sq = hop_curve(t, 16.05, 16.5, 1, 36)
        s.update(x=lerp(398, -260, ease_in_out(seg(t, 16.05, 16.5))), hop=h, sq=sq, eyes="happy", mouth="grin",
                 look=(-6, 0), lean=6)
        s["arm_r"] = lerp(165, 120 + 22 * math.sin((t - 16.0) * 16), ease_out(seg(t, 16.0, 16.15)))
    else:                             # ...and back in with muddy paws: apples! (== frame 0)
        h, sq = hop_curve(t, T_BACK0, T_BACK1, 1, 40)
        s.update(x=lerp(-260, SN_HOME, ease_out(seg(t, T_BACK0, T_BACK1))), hop=h, sq=sq,
                 lean=lerp(-6, 0, seg(t, T_BACK0, T_BACK1)), look=(6, 0))
        p = ease_in_out(seg(t, 17.35, 18.0))
        if t >= T_BACK1:
            s["lean"] = lerp(0, -6, p)
        s.update(eyes="wide" if t > 17.4 else "normal", mouth="o" if t > 17.4 else "w",
                 look=(7, 4) if t > 17.4 else (6, 0))
        rest = aim(SNIP, dict(s, x=SN_HOME, hop=0.0, sq=1.0, lean=-6.0), "r", (470, 1320), 30)
        s["arm_r"] = lerp(14, rest, ease_in_out(seg(t, 17.45, 18.0)))
        e = spring(t, 17.4, 9, 5.0, 4.0) * (1 - ease_in_out(seg(t, 17.6, 18.0)))
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
             look=(0, 0), head_dy=0.0, soap=None)
    if t < 6.0 or t >= 16.85:
        s["x"] = 1450
        return s
    if t < 6.9:                       # slides in, holds the soap up high
        s["x"] = lerp(1450, CR_HOME, ease_out_back(seg(t, 6.0, 6.5), 1.2))
        s["lean"] = 12 * (1 - ease_out(seg(t, 6.0, 6.9)))
        s["arm_l"] = lerp(CR_REST_L, 194, ease_out_back(seg(t, 6.3, 6.55)))
        s.update(eyes="worried" if t < 6.5 else "normal", mouth="o" if t < 6.5 else "smile", look=(-7, 2))
        s["soap"] = "paw"
    elif t < 7.85:                    # mimes a scrub: paws together, bubbles!
        k = ease_in_out(seg(t, 6.9, 7.1))
        rub = 8 * math.sin(2 * math.pi * 6 * (t - 7.1)) if t > 7.1 else 0.0
        s["arm_l"] = lerp(194, 414, k) + rub          # 414 == 54 (inward), swung round through 270
        s["arm_r"] = lerp(2, -54, k) + rub
        s.update(eyes="happy" if t > 7.15 else "normal", mouth="grin" if t > 7.15 else "smile", look=(-7, 4))
        s["soap"] = "paw"
        s["head_dy"] = 6 * math.sin(2 * math.pi * 3 * max(0.0, t - 7.1))
    elif t < TOSS1[1]:                # nods at Snip's tap, then tosses the soap
        k = ease_in_out(seg(t, 7.85, 8.05))
        s["arm_l"] = lerp(414, 394, k)
        s["arm_r"] = lerp(-54, 2, k)
        s.update(look=(-8, 3), eyes="normal", mouth="smile")
        if t >= TOSS1[0] - 0.12:
            p = seg(t, TOSS1[0] - 0.12, TOSS1[0] + 0.05)
            s["arm_l"] = lerp(394, 215, ease_out(p))
        s["soap"] = "paw" if t < TOSS1[0] else None
    elif t < T_TAKE:                  # cheers Snip on, counts along, catches the soap back
        s.update(eyes="happy", mouth="smile", look=(-8, 4))
        s["arm_l"] = lerp(215, CR_REST_L, ease_in_out(seg(t, TOSS1[1], TOSS1[1] + 0.25)))
        for c in COUNTS:
            s["head_dy"] += 10 * math.sin(math.pi * seg(t, c, c + 0.3))
            if 0 <= t - c < 0.3:
                s["mouth"] = "o"
        if TOSS2[0] - 0.15 <= t:     # catch!
            k = ease_out(seg(t, TOSS2[0] - 0.15, TOSS2[1] - 0.05)) * (1 - ease_in_out(seg(t, TOSS2[1] + 0.2, TOSS2[1] + 0.45)))
            s["arm_l"] = lerp(CR_REST_L, 215, k)
            s["soap"] = "paw" if t >= TOSS2[1] else None
            if t >= TOSS2[1] + 0.45:
                s["soap"] = "dish"
        if t >= T_TADA:
            h, sq = hop_curve(t, T_TADA + 0.05, T_TADA + 0.35, 1, 18)
            s.update(hop=h, sq=sq, eyes="happy", mouth="grin")
            s["arm_r"] = lerp(2, 150, ease_out_back(seg(t, T_TADA, T_TADA + 0.2)))
    elif t < T_GONE + 0.3:            # MUNCH
        take = ease_in_out(seg(t, T_TAKE, T_TAKE + 0.22))
        lift = ease_in_out(seg(t, T_TAKE + 0.3, T_TAKE + 0.5))
        s.update(eyes="sparkle" if t < T_TAKE + 0.5 else "happy", mouth="yum", look=(-6, 4), soap="dish")
        s["lean"] = 8 * take * (1 - lift)
        a_l = aim(CR, s, "l", (A2[0] + 6, A2[1] + 10), 360)
        m = mouth(CR, s)
        held = (m[0] - 16, m[1] + 44)
        s["arm_r"] = lerp(lerp(150, 2, take), aim(CR, s, "r", (held[0] + 36, held[1] + 20), -150), lift)
        s["arm_l"] = lerp(lerp(CR_REST_L, a_l, take), aim(CR, s, "l", (held[0] - 36, held[1] + 20), 150), lift)
        if t >= T_TAKE + 0.5:
            s["mouth"] = munch_mouth(t, 0.08)
            s["eyes"] = "closed" if any(0 <= t - b - 0.08 < 0.25 for b in BITES) else "happy"
            s["head_dy"] = sum(10 * math.sin(math.pi * seg(t, b + 0.08, b + 0.28)) for b in BITES)
        if t >= T_GONE + 0.08:
            k = ease_in_out(seg(t, T_GONE + 0.08, T_GONE + 0.3))
            s["arm_l"] = lerp(s["arm_l"], CR_REST_L, k)
            s["arm_r"] = lerp(s["arm_r"], 2, k)
    elif t < 14.6:
        h, sq = hop_curve(t, 14.1, 14.42, 1, 24)
        s.update(hop=h, sq=sq, eyes="happy", mouth="grin" if t > 14.0 else "blow", look=(-6, 2), soap="dish")
    elif t < 16.0:                    # PAW-BUMP
        h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
        s.update(x=lerp(CR_HOME, 712, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq, eyes="happy", mouth="grin",
                 soap="dish")
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_l"] = lerp(lerp(CR_REST_L, 380, wind), 198, swing)
    else:                             # waves bye, takes the soap, hops away
        h, sq = hop_curve(t, 16.1, 16.85, 2, 40)
        s.update(x=lerp(712, 1450, ease_in_out(seg(t, 16.1, 16.85))), hop=h, sq=sq, eyes="happy", mouth="grin",
                 lean=-6, soap="paw")
        s["arm_l"] = lerp(198, 200, ease_out(seg(t, 16.0, 16.2)))
        s["arm_r"] = 140 + 22 * math.sin((t - 16.0) * 16)
    if s["hop"] == 0:
        s["sq"] *= breath(t + 0.7, 2.25, 0.01)
    return s


# ---------------------------------------------------------------- props state
def lever_angle(t):
    a = 90 * ease_out_back(seg(t, TAP_ON1 + 0.06, TAP_ON1 + 0.16))
    a -= 90 * ease_out_back(seg(t, TAP_OFF1 + 0.06, TAP_OFF1 + 0.16))
    a += 90 * ease_out_back(seg(t, TAP_ON2 + 0.06, TAP_ON2 + 0.16))
    a -= 90 * ease_out_back(seg(t, TAP_OFF2 + 0.06, TAP_OFF2 + 0.16))
    return a


def water_on(t):
    for w0, w1 in (WATER1, WATER2):
        if w0 <= t < w1:
            return ease_out(seg(t, w0, w0 + 0.08)), 1 - ease_in_out(seg(t, w1 - 0.08, w1))
    return 0.0, 0.0


def mud_level(t):
    if t < COUNTS[0]:
        return 1.0
    if t < WATER2[1]:
        return lerp(1.0, 0.0, ease_in_out(seg(t, COUNTS[0], WATER2[1] - 0.1)))
    if t < T_BACK0:
        return 0.0
    return 1.0


def foam_scale(t):
    if t < TOSS1[1] + 0.05 or t >= WATER2[1]:
        return 0.0
    k = 0.32 * ease_out_back(seg(t, TOSS1[1] + 0.05, TOSS1[1] + 0.3))
    for i, c in enumerate(COUNTS):
        k += 0.24 * ease_out_back(seg(t, c, c + 0.25))
    return k * (1 - ease_in_out(seg(t, WATER2[0] + 0.05, WATER2[1] - 0.05)))


def apple_items(t, sn, cr):
    """(sprite, centre, angle, scale) for both apples."""
    out = []
    if t < T_TAKE or t >= T_HAND1:
        return [(APPLES[0], A1, 0.0, 1.0), (APPLES[0], A2, 0.0, 1.0)]
    if t < T_GONE + 0.3:
        for who, ch, st, rest, delay in (("s", SNIP, sn, A1, 0.0), ("c", CR, cr, A2, 0.08)):
            take = ease_in_out(seg(t, T_TAKE, T_TAKE + 0.22))
            lift = ease_in_out(seg(t, T_TAKE + 0.3, T_TAKE + 0.5))
            m = mouth(ch, st)
            held = (m[0] + (14 if who == "s" else -16), m[1] + (40 if who == "s" else 44))
            c = (lerp(rest[0], held[0], lift), lerp(rest[1], held[1], lift) - 14 * take * (1 - lift))
            b = sum(1 for x in BITES[:2] if t >= x + delay)
            sc = 1.0 - ease_in_out(seg(t, BITES[2] + delay, BITES[2] + delay + 0.14))
            if sc > 0.02:
                out.append((APPLES[b], c, (-8 if who == "s" else 8) * lift, sc))
        return out
    if t < T_HAND0:
        return []
    fy = hand_y(t)
    return [(APPLES[0], (A1[0], fy + 52), 0.0, 1.0), (APPLES[0], (A2[0], fy + 46), 0.0, 1.0)]


def hand_y(t):
    land = A1[1] - 52
    if t < T_HAND0 or t >= T_HAND3:
        return None
    if t < T_HAND1:
        return lerp(-700, land, ease_out(seg(t, T_HAND0, T_HAND1)))
    if t < T_HAND2:
        return land
    return lerp(land, -700, ease_in_out(seg(t, T_HAND2, T_HAND3)))


def soap_pos(t, sn, cr):
    """Where the soap is, or None."""
    if TOSS1[0] <= t < TOSS1[1]:
        p0 = tip(CR, crinkle_state(TOSS1[0] - 1e-3), "l")
        p1 = snip_paws(t, sn)
        return arc((p0[0], p0[1] - 20), (p1[0], p1[1] - 26), seg(t, TOSS1[0], TOSS1[1]), 220), 540 * seg(t, *TOSS1)
    if TOSS1[1] <= t < TOSS2[0]:
        p = snip_paws(t, sn)
        return (p[0], p[1] - 26 + 4 * math.sin(2 * math.pi * 6 * t)), 0.0
    if TOSS2[0] <= t < TOSS2[1]:
        p0 = snip_paws(TOSS2[0], snip_state(TOSS2[0]))
        p1 = tip(CR, crinkle_state(TOSS2[1]), "l")
        return arc((p0[0], p0[1] - 26), (p1[0], p1[1] - 20), seg(t, *TOSS2), 200), -540 * seg(t, *TOSS2)
    if cr["soap"] == "paw" and cr["x"] < 1300:
        p = tip(CR, cr, "l")
        return (p[0], p[1] - 20), 0.0
    if cr["soap"] == "dish":
        return (SOAP_DISH_AT[0], SOAP_DISH_AT[1] - 20), 0.0
    return None


def snip_paws(t, sn):
    a, b = tip(SNIP, sn, "l"), tip(SNIP, sn, "r")
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def towel_state(t, sn):
    """(centre_pivot, angle, sx) of the towel."""
    if t < T_TOWEL0 or t >= T_FLING1 + 0.6:
        sw = spring(t, T_FLING1, 14, 2.2, 3.0) if t >= T_FLING1 else 0.0
        return TOWEL_HANG, sw, 1.0
    paws = snip_paws(t, sn)
    at_paws = (paws[0] + 6 * math.sin(2 * math.pi * 5 * t), paws[1] - 70)
    if t < T_TOWEL1:
        k = ease_out(seg(t, T_TOWEL0, T_TOWEL1))
        return (lerp(TOWEL_HANG[0], at_paws[0], k), lerp(TOWEL_HANG[1], at_paws[1], k)), -30 * k, 1.0
    if t < T_FLING0:
        return at_paws, 4 * math.sin(2 * math.pi * 5 * t), 1.0
    if t < T_FLING1:
        k = seg(t, T_FLING0, T_FLING1)
        p0 = snip_paws(T_FLING0, snip_state(T_FLING0))
        c = arc((p0[0], p0[1] - 70), TOWEL_HANG, ease_in_out(k), 160)
        return c, 360 * ease_in_out(k), 1.0
    return TOWEL_HANG, spring(t, T_FLING1, 14, 2.2, 3.0), 1.0


GERM_HOME = ((-58, -70), (8, -112), (70, -60))   # offsets from Snip's right paw tip


def germ_items(t, sn):
    """(sprite, centre, angle, scale, in_bubble_scale) for the three germs."""
    if not (T_GERMS <= t < COUNTS[2] + 1.0):
        return []
    tp = tip(SNIP, sn, "r")
    out = []
    for i, (dx, dy) in enumerate(GERM_HOME):
        t_pop = T_GERMS + 0.06 * i
        if t < t_pop:
            continue
        sc = 1.2 * pop_scale(t, t_pop, 0.22)
        wave = (1, 2)[int((t * 6 + i) % 2)]
        mood = "smile"
        if t < T_GERMS + 0.45:
            mood = "giggle"
        elif 5.05 <= t < 5.6:           # holding on tight while Snip shakes!
            mood, wave = ("gasp", 3) if i == 1 else ("giggle", 3)
        elif t < 6.4:
            mood = "giggle"
        elif TOSS1[1] <= t:
            mood = "worried" if t < COUNTS[0] else "smile"
        jig = 6 * math.sin(2 * math.pi * 4 * t + i * 2)
        lag = 0.0
        if 5.05 <= t < 5.6:
            lag = 16 * math.sin(2 * math.pi * 7 * (t - 5.05) - 1.2 - i * 0.4)
        c = (tp[0] + dx + lag, tp[1] + dy + jig * 0.5)
        bub = 0.0
        ang = 10 * math.sin(2 * math.pi * 2 * t + i)
        if t >= COUNTS[i]:              # off it goes, in a bubble, waving bye
            k = seg(t, COUNTS[i], COUNTS[i] + 0.95)
            c = (c[0] + 60 * (i - 1) + 30 * math.sin(k * 6), c[1] - 520 * ease_in_out(k))
            bub = pop_scale(t, COUNTS[i], 0.2)
            mood, wave = "giggle", (1, 2)[int((t * 6 + i) % 2)]
            if k >= 0.82:
                continue
        out.append((GERMS[(i, mood, wave)], c, ang, sc, bub))
    return out


# ---------------------------------------------------------------- frame
def draw_arms(f, ch, st, mud=0.0):
    for side in ("l", "r"):
        spr = ch.arm_l if side == "l" else ch.arm_r
        sh = ch.shoulder_pt(st["x"], FY, side, st["hop"], st["lean"], st["sq"])
        ang = (st["arm_l"] if side == "l" else st["arm_r"]) + st["lean"]
        PW.place_clipped(f, spr, sh, angle=ang, y_max=PW.ARM_CLIP, shadow_from=PW.COUNTER_TOP)
        if mud > 0.01:
            PW.place_clipped(f, MUD_L if side == "l" else MUD_R, sh, angle=ang, y_max=PW.ARM_CLIP, alpha=mud)


def render_frame(t):
    f = BG.copy()
    sn = snip_state(t)
    cr = crinkle_state(t)
    towel = towel_state(t, sn)
    towel_in_use = T_TOWEL0 <= t < T_FLING1

    if not towel_in_use:
        place(f, TOWEL, towel[0], angle=towel[1])

    snip_blink = blinking(t, SNIP_BLINKS) and not frozen(t)
    SNIP.draw(f, sn["x"], FY, hop=sn["hop"], lean=sn["lean"], head_tilt=sn["tilt"], arm_l=sn["arm_l"],
              arm_r=sn["arm_r"], eyes=sn["eyes"], mouth=sn["mouth"], look=sn["look"], squash=sn["sq"],
              head_dy=sn["head_dy"], blink=snip_blink, ears=tuple(sn["ears"]), ear_stretch=sn["ear_stretch"],
              frizz=sn["frizz"])
    if cr["x"] < 1300:
        CR.draw(f, cr["x"], FY, hop=cr["hop"], lean=cr["lean"], arm_l=cr["arm_l"], arm_r=cr["arm_r"],
                eyes=cr["eyes"], mouth=cr["mouth"], look=cr["look"], squash=cr["sq"], head_dy=cr["head_dy"],
                blink=blinking(t, CR_BLINKS) and not frozen(t))

    # the wash counter in front of both, then everything on it
    place(f, COUNTER, (PW.COUNTER_X, PW.COUNTER_TOP))
    place(f, FAUCET, NOZ)
    place(f, FAUCET_CR, NOZ_CR)
    place(f, LEVER_BASE, (LEVER_AT[0], LEVER_AT[1] + 12))
    place(f, LEVER, LEVER_AT, angle=-lever_angle(t))
    place(f, LEVER_BASE, (LEVER_CR[0], LEVER_CR[1] + 12))
    place(f, LEVER, LEVER_CR)
    place(f, DISH, SOAP_DISH_AT)
    place(f, PLATE, PLATE_AT)
    holding = T_TAKE <= t < T_GONE + 0.3
    if not holding:
        for spr, c, ang, sc in apple_items(t, sn, cr):
            place(f, spr, c, angle=ang, scale=sc)

    # arms in front of the counter (paws on the counter / in the basin), with mud
    draw_arms(f, SNIP, sn, mud_level(t))
    if cr["x"] < 1300:
        draw_arms(f, CR, cr)

    # foam around Snip's paws (scrub), bubbles drifting up
    fs = foam_scale(t)
    paws = snip_paws(t, sn)
    if fs > 0.01:
        place(f, FOAM, (paws[0], paws[1] - 18), scale=fs, angle=4 * math.sin(2 * math.pi * 6 * t))
    for i in range(7):
        t0 = 9.0 + i * 0.22
        if t0 <= t < t0 + 1.1 and t < WATER2[1]:
            k = seg(t, t0, t0 + 1.1)
            place(f, BUBBLES[i % 3], (paws[0] - 50 + 20 * i + 18 * math.sin(k * 7 + i), paws[1] - 60 - 420 * k),
                  scale=pop_scale(t, t0, 0.2) * (1 - ease_in_out(seg(k, 0.8, 1.0))))
    if 6.9 <= t < 8.0 and cr["x"] < 1300:          # Crinkle's mime bubbles
        cp = ((tip(CR, cr, "l")[0] + tip(CR, cr, "r")[0]) / 2, (tip(CR, cr, "l")[1] + tip(CR, cr, "r")[1]) / 2)
        for i in range(4):
            t0 = 7.1 + i * 0.18
            if t0 <= t < t0 + 0.8:
                k = seg(t, t0, t0 + 0.8)
                place(f, BUBBLES[i % 3], (cp[0] - 30 + 22 * i + 14 * math.sin(k * 6 + i), cp[1] - 70 - 300 * k),
                      scale=pop_scale(t, t0, 0.2) * (1 - ease_in_out(seg(k, 0.75, 1.0))))

    # running water, pouring onto the paws (in front, so it reads)
    w_in, w_out = water_on(t)
    if w_in > 0.01 and w_out > 0.01:
        fr = WATER[int(t * 24) % len(WATER)]
        top = NOZ[1] + (1 - w_out) * 100
        place(f, fr, (NOZ[0], top), sx=1.7, sy=w_in * (1 - (top - NOZ[1]) / 108))


    # soap (lesson-critical) in front
    sp = soap_pos(t, sn, cr)
    if sp is not None:
        place(f, SOAP, sp[0], angle=sp[1], scale=1.15)

    # splash where the water hits the paws
    if w_in > 0.5 and w_out > 0.2:
        place(f, SPLASH, (paws[0], paws[1] - 8), scale=0.9 + 0.08 * math.sin(t * 40), alpha=min(w_in, w_out))
    if WATER2[1] <= t < WATER2[1] + 0.5:          # drips after the rinse
        for i, dx in enumerate((-18, 14)):
            k = seg(t, WATER2[1] + 0.1 * i, WATER2[1] + 0.1 * i + 0.35)
            if 0 < k < 1:
                place(f, DRIP, (paws[0] + dx, paws[1] + 6 + 70 * k * k), alpha=1 - k)

    # the towel while in use (in front of the paws)
    if towel_in_use:
        place(f, TOWEL, towel[0], angle=towel[1])

    # germs (in front of everything on the paw)
    for spr, c, ang, sc, bub in germ_items(t, sn):
        place(f, spr, c, angle=ang, scale=sc)
        if bub > 0.01:
            place(f, RING_BUBBLE, c, scale=1.45 * bub)

    # apples held up to munch (in front of the paws)
    if holding:
        for spr, c, ang, sc in apple_items(t, sn, cr):
            place(f, spr, c, angle=ang, scale=sc)
        for i, b in enumerate(BITES):
            for who, ch, st, d in (("s", SNIP, sn, 0.0), ("c", CR, cr, 0.08)):
                if b + d <= t < b + d + 0.3:
                    m = mouth(ch, st)
                    k = seg(t, b + d, b + d + 0.3)
                    place(f, SMALL_SPARK, (m[0] + (40 if who == "s" else -40), m[1] + 10 - 40 * k),
                          scale=0.6 * math.sin(math.pi * k), angle=k * 90)

    # desire: the apple glints
    for t0, dx, dy, sc in ((1.1, 30, -36, 0.9), (1.55, -26, 10, 0.7), (2.0, 20, 30, 0.6)):
        if t0 <= t < t0 + 0.5:
            k = math.sin(math.pi * seg(t, t0, t0 + 0.5))
            place(f, GLINT, (A1[0] + dx, A1[1] + dy), scale=sc * k, angle=(t - t0) * 120)

    # shake lines
    if 5.05 <= t < 5.6:
        tp = tip(SNIP, sn, "r")
        place(f, SHAKE, (tp[0] + 10, tp[1] - 30), scale=0.9 + 0.1 * math.sin(t * 50))

    # the grown-up's hand brings two new apples (loop)
    hy = hand_y(t)
    if hy is not None:
        place(f, HAND, ((A1[0] + A2[0]) / 2, hy))

    # counting numerals
    for i, c in enumerate(COUNTS):
        if c <= t < c + 0.55:
            out = 1 - ease_in_out(seg(t, c + 0.4, c + 0.55))
            place(f, NUMS[i], (540, 640), scale=pop_scale(t, c, 0.25) * out, angle=-6 + 4 * math.sin(t * 6))

    # clean paws: sparkles + check
    if T_TADA <= t < T_TAKE:
        for side in ("l", "r"):
            p = tip(SNIP, sn, side)
            k = math.sin(math.pi * seg(t, T_TADA + 0.08, T_TAKE))
            place(f, SPARKLE, (p[0], p[1] - 14), scale=0.32 * k, angle=(t - T_TADA) * 120)
        place(f, CHECK, (540, 760), scale=pop_scale(t, T_TADA + 0.05, 0.25) * (1 - ease_in_out(seg(t, T_TAKE - 0.15, T_TAKE))))

    for i, (t0, x, y) in enumerate(HEART_PLAN):
        if t0 <= t < 14.6:
            p = seg(t, t0, 14.6)
            place(f, HEARTS[i], (x + 10 * math.sin(t * 3 + i), y - 160 * p), scale=pop_scale(t, t0, 0.25),
                  alpha=1 - ease_in_out(seg(t, 14.2, 14.6)), angle=10 * math.sin(t * 2.5 + i))

    # paw-bump: both touching paws in front, sparkle
    if 14.95 <= t < 16.1:
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], FY, "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])
        place(f, CR.arm_l, CR.shoulder_pt(cr["x"], FY, "l", cr["hop"], cr["lean"], cr["sq"]),
              angle=cr["arm_l"] + cr["lean"])
    if 15.45 <= t < 16.2:
        a, b = tip(SNIP, sn, "r"), tip(CR, cr, "l")
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 10)
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
        place(f, BUB_MUD, (300, 600), scale=1.1 * pop_scale(t, 2.55) * gone * (pulse_a if t > 2.95 else 1))
        place(f, BUB_SOAP, (780, 600), scale=1.1 * pop_scale(t, 2.7) * gone * (pulse_b if t > 3.45 else 1))
        place(f, QMARK, (540, 500), scale=pop_scale(t, 2.85, 0.25) * gone, angle=8 * math.sin(t * 4))

    return camera(f, t)


CAM0 = (1.6, 440, 1110)
CAM_KEYS = [
    (0.0,) + CAM0, (1.0, 1.63, 440, 1110), (1.45, 1.15, 480, 1100), (2.4, 1.15, 480, 1100),
    (2.8, 1.1, 540, 1000), (4.5, 1.1, 540, 1000), (4.75, 1.35, 430, 1150), (5.6, 1.35, 430, 1150),
    (6.0, 1.1, 540, 1000), (7.8, 1.1, 540, 1000), (8.1, 1.18, 480, 1090), (11.4, 1.18, 480, 1090),
    (11.7, 1.12, 420, 1080), (12.6, 1.12, 420, 1080), (12.9, 1.1, 540, 1000),
    (15.2, 1.1, 540, 1000), (15.45, 1.12, 550, 1060), (15.9, 1.12, 550, 1060), (16.3, 1.1, 540, 1000),
    (17.3, 1.1, 540, 1000), (DUR,) + CAM0]


def camera(f, t):
    z, cx, cy = 1.0, 540, 960
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
    if T_GERMS <= t < T_GERMS + 0.3:  # little startle shake
        k = 1 - seg(t, T_GERMS, T_GERMS + 0.3)
        cx += 7 * k * math.sin(t * 95)
        cy += 5 * k * math.cos(t * 81)
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
    for tt, ch, up in ((1.0, "C", False), (1.25, "C", True), (1.5, "Am", False), (1.75, "Am", True),
                       (2.0, "F", False), (2.25, "G", True)):
        A.strum(music, tt, ch, 0.7, up)
    for tt, m in ((1.0, 48), (1.5, 45), (2.0, 41), (2.25, 43)):
        music.add(tt, A.bass(M(m), 0.5, 0.7))
    sfx.add(1.1, A.twinkle(0.8))
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
    # creep... germs pop up, giggle, shake shake, uh-oh
    for i, m in enumerate((64, 65, 66, 67)):
        music.add(4.5 + i * 0.08, A.pluck(M(m - 12), 0.3, 0.6))
    for i in range(3):
        sfx.add(T_GERMS + 0.06 * i, PW.bubble_pop(0.8, 700 + 150 * i))
    sfx.add(T_GERMS + 0.05, PW.gasp(0.9))
    sfx.add(T_GERMS + 0.2, PW.giggle(0.9, 1250))
    sfx.add(T_GERMS + 0.05, A.boing(0.7, 340))
    sfx.add(5.05, PW.rattle(0.5, 0.8))
    sfx.add(5.2, PW.giggle(0.7, 1400))
    sfx.add(5.62, PW.giggle(0.6, 1150))
    music.add(5.6, A.wah_down(0.8))
    # Crinkle + soap + mime
    sfx.add(5.98, A.whoosh(0.5, 1.0))
    sfx.add(6.42, A.glock(M(91), 1.2, 0.8))
    sfx.add(6.47, A.glock(M(88), 1.2, 0.55))
    sfx.add(6.45, A.twinkle(0.6))
    for tt, ch in ((6.6, "F"), (7.1, "C"), (7.6, "G")):
        A.strum(music, tt, ch, 0.55)
        music.add(tt, A.bass(M({"F": 41, "C": 48, "G": 43}[ch]), 0.5, 0.6))
    for i in range(4):
        sfx.add(7.1 + i * 0.18, PW.bubble_pop(0.4, 1000 + 120 * i))
    for tt in (7.3, 7.6):
        sfx.add(tt, A.tap(0.5))
    # tap on, wet, tap off, soap toss, scrub + count, toss back, rinse, towel
    for t0 in (TAP_ON1, TAP_OFF1, TAP_ON2, TAP_OFF2):
        sfx.add(t0 + 0.08, PW.squeak(0.6, up=t0 in (TAP_ON1, TAP_ON2)))
    sfx.add(WATER1[0], PW.water_run(WATER1[1] - WATER1[0], 0.8))
    sfx.add(WATER2[0], PW.water_run(WATER2[1] - WATER2[0], 0.8))
    sfx.add(WATER1[0] + 0.05, PW.splash(0.4))
    sfx.add(TOSS1[0], A.whoosh(0.3, 0.6))
    sfx.add(TOSS1[1], PW.plip(0.9))
    sfx.add(TOSS1[1] + 0.03, A.pop(0.5))
    tt = COUNTS[0] - 0.15
    while tt < TOSS2[0] - 0.1:
        sfx.add(tt, PW.squish(0.35))
        tt += 0.33
    for i, (c, m) in enumerate(zip(COUNTS, (84, 88, 91))):
        sfx.add(c, A.glock(M(m), 1.2, 0.9))
        music.add(c, A.ks_pluck(M(m - 24), 1.0, 0.8))
        music.add(c, A.bass(M(48), 0.4, 0.5))
        sfx.add(c + 0.15, PW.giggle(0.45, 1300 + 100 * i))
        sfx.add(c + 0.8, PW.bubble_pop(0.7, 800 + 100 * i))
    for tt, ch in ((9.05, "C"), (9.65, "F"), (10.25, "G")):
        A.strum(music, tt, ch, 0.5)
    sfx.add(TOSS2[0], A.whoosh(0.3, 0.6))
    sfx.add(TOSS2[1], PW.plip(0.8))
    sfx.add(WATER2[0] + 0.05, PW.splash(0.6))
    for i in range(2):
        sfx.add(WATER2[1] + 0.1 * i + 0.3, PW.plip(0.4))
    sfx.add(T_TOWEL0, A.whoosh(0.25, 0.6))
    sfx.add(T_TOWEL1, PW.fluff(0.4, 0.8))
    sfx.add(T_FLING0, A.whoosh(0.3, 0.6))
    sfx.add(T_FLING1, A.tap(0.6))
    # ta-da clean paws
    sfx.add(T_TADA, A.chime_up(0.9))
    sfx.add(T_TADA + 0.05, A.twinkle(0.8))
    A.strum(music, T_TADA, "C", 0.7)
    music.add(T_TADA, A.bass(M(48), 0.5, 0.7))
    # munch munch munch + happy strums
    sfx.add(T_TAKE, A.pop(0.5))
    for b in BITES:
        sfx.add(b, PW.crunch(1.0))
        sfx.add(b + 0.08, PW.crunch(0.8))
    for tt, ch, up in ((12.85, "F", False), (13.1, "C", False), (13.35, "C", True), (13.6, "G", False),
                       (13.85, "G", True), (14.1, "Am", False), (14.35, "F", True)):
        A.strum(music, tt, ch, 0.75, up)
    for tt, m in ((13.1, 48), (13.6, 43), (14.1, 45), (14.35, 41)):
        music.add(tt, A.bass(M(m), 0.45, 0.8))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.45))
    sfx.add(14.05, A.boing(0.35, 340))
    # paw-bump (signature)
    sfx.add(14.85, A.snare_roll(0.6, 0.8))
    sfx.add(15.45, A.boop(0.9))
    A.jingle(music, 15.47, 1.0, ending=True)
    sfx.add(15.5, A.twinkle(0.8))
    # bye, new apples, back in muddy, uh-oh (leads into the jingle at 0:00)
    sfx.add(16.05, A.boing(0.35, 300))
    sfx.add(16.12, A.boing(0.3, 330))
    sfx.add(16.3, A.whoosh(0.5, 0.6))
    sfx.add(T_HAND1, A.tap(0.8))
    A.strum(music, 16.3, "F", 0.5)
    A.strum(music, 16.8, "G7", 0.5)
    sfx.add(T_BACK0, A.boing(0.4, 280))
    sfx.add(T_BACK1 - 0.02, PW.squish(0.8))
    sfx.add(17.4, A.uh_oh(0.9))
    for i, m in enumerate((64, 65, 66)):
        music.add(17.55 + i * 0.13, A.pluck(M(m - 12), 0.3, 0.55))
    music.add(17.3, A.pad([M(55), M(59), M(62)], 0.7, 0.25))

    m = A.reverb(music.normalized(), 0.24)
    s = A.reverb(sfx.normalized(), 0.08)
    y = 0.55 * m / max(1e-9, abs(m).max()) + 0.7 * s / max(1e-9, abs(s).max())
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.01)


# ---------------------------------------------------------------- output
def render(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    wav = os.path.join(ROOT, "build", "ep02_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep02_wash_before_you_munch.mp4")
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
    times = times or [0.0, 1.8, 3.4, 4.9, 5.3, 5.8, 6.6, 7.4, 8.3, 8.75, 9.2, 9.8, 10.4, 10.6,
                      11.1, 11.7, 12.4, 13.2, 15.6, 17.1, 17.99]
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


KEYS = [(0.0, "0.0s hook"), (3.4, "3.4s choice"), (5.25, "5.3s germs hang on"), (6.6, "6.6s Crinkle + soap"),
        (9.2, "9.2s scrub: 1"), (11.1, "11.1s rinse"), (12.4, "12.4s clean paws"), (15.6, "15.6s paw-bump")]


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
        stills(os.path.join(ROOT, "build", "ep02_stills.png"))
    elif "--keys" in sys.argv:
        os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
        key_sheet(os.path.join(ROOT, "reviews", "ep02_keys.png"))
    else:
        render(os.path.join(ROOT, "output"))
