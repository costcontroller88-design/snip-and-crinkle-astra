"""Episode 9 — Buckle Up? 🚗

A big cute red car seen in cut-away from the side (like a doll's house). Snip sits in a yellow
high-back booster in the back seat, Crinkle in a green booster in front of Snip, and the grown-up's
hand rests on the steering wheel. The car is parked. Snip is so excited about the beach trip that
the booster becomes a trampoline. Choice: bounce, or buckle up? Snip bounces higher and higher until
both ears squash against the roof -- BOING! The car does NOT move: the grown-up's hand leaves the
wheel, points at the seat belt and waits, tap-tap-tap. Crinkle points at Snip's belt and a dotted
path shows where it goes (over the shoulder, across the lap). Click (1) Snip's belt, click (2)
Crinkle's belt, (3) the grown-up checks with a thumbs-up. Only then does the car drive off smoothly:
houses, trees and then the beach scroll past the windows. Hearts, the signature paw-bump (seated),
the car stops at the beach and a paper heart-iris wipes back to the start (frame 18.0 == frame 0).

Run:  python3 episodes/ep09_buckle_up.py            (render -> output/)
      python3 episodes/ep09_buckle_up.py --stills   (contact sheet -> build/)
      python3 episodes/ep09_buckle_up.py --keys     (key frames -> reviews/ep09_keys.png)
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
import music_extra as MX  # noqa: E402
import props_car as PC  # noqa: E402
import props_grownup as G  # noqa: E402
import props_street as PS  # noqa: E402
import scene  # noqa: E402
from characters import Character  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, rot, seg  # noqa: E402

FPS = 30
DUR = 18.0
BASE = PC.BASE
SN_X, CR_X = 275, 655
CR_REST_L = 346
HOOK_H = 45                           # bounce height in the hook (ears stay clear of the roof)

# seat-belt geometry, relative to each seat (x, base)
SN_BELT = dict(G=(-125, -262), L=(-132, -70), B=(70, -82), REST=(-160, -148), M=(-10, -170))
CR_BELT = dict(G=(-150, -270), L=(-150, -76), B=(72, -92), REST=(-192, -150), M=(0, -175))
TONGUE_SLOT = 71                      # tongue tip -> webbing slot
TONGUE_GRAB = 46                      # tongue tip -> where a paw holds it

# timeline
T_HAND_OFF, T_POINT = 4.85, 5.2       # grown-up's hand leaves the wheel, points at the belt
T_HIT = 5.55                          # ears squash against the roof
T_SN_GRAB, T_SN_MID, T_SN_PASS, T_SN_CLICK = 8.05, 8.35, 8.62, 9.0
T_CR_GRAB, T_CR_MID, T_CR_PASS, T_CR_CLICK = 9.15, 9.42, 9.68, 10.0
T_THUMB = 10.55                       # count 3: thumbs-up
T_WHEEL = 11.2                        # hand back on the wheel
T_GO, RU, T_STOP, RD = 11.55, 1.0, 16.3, 1.2
V = 360.0                             # cruising scroll speed (px/s)
COUNTS = (T_SN_CLICK, T_CR_CLICK, T_THUMB + 0.05)
HEART_PLAN = ((12.4, 160, 720), (12.6, 450, 640), (12.8, 820, 700), (13.0, 640, 600))
T_IRIS0, T_IRIS1, T_RESET, T_OPEN1 = 16.55, 17.1, 17.18, 17.9

SKY = PC.sky()
CLOUDS = PC.clouds(W_CLOUDS := scene.W + 600)
SCENERY = PC.scenery()
ROAD = PC.road()
CAR_BACK = PC.car_back()
GLASS = PC.glass()
CAR_FRONT = PC.car_front()
WHEEL = PC.wheel()
CAR_SHADOW = PC.car_shadow()
STEER = PC.steering_wheel()
SN_BACK = PC.booster_back(PC.SN_BOOST)
CR_BACK = PC.booster_back(PC.CR_BOOST, 380, 590)
SN_CUSH = PC.booster_cushion(PC.SN_BOOST)
CR_CUSH = PC.booster_cushion(PC.CR_BOOST, 420)
GUIDE = PC.guide_clip()
TONGUE = PC.tongue()
RECEIVER = PC.receiver()
GLOW = PC.glow()
DOT = PC.dot(r=12)
DOT_Y = PC.dot((255, 214, 64), 14)
CLICK = PC.click_star()
BONK = PC.bonk_star()
ARM = G.GrownUpArm(upper=440, fore=440, bend=+1, w_shoulder=136, w_elbow=118, w_wrist=98)  # elbow up, over the seats
H_GRIP = PC.hand_grip()
H_POINT = PC.hand_point()
H_THUMB = PC.hand_thumb()
BUB_BOUNCE = PC.choice_bubble("bounce", (240, 110, 100))
BUB_BUCKLE = PC.choice_bubble("buckle", (90, 190, 120))
THOUGHT = PC.beach_thought()
TDOTS = [PC.thought_dot(r) for r in (16, 24)]
QMARK = icons.question()
CHECK = icons.check(130)
SPARKLE = scene.sparkle()
NUMS = [scene.numeral(1, (244, 112, 104)), scene.numeral(2, (255, 196, 52)), scene.numeral(3, (84, 182, 222))]
HEARTS = [scene.heart(c, 110) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120), (255, 150, 170))]
IRIS = PS.HeartIris()
SNIP = Character("snip", 1.15)
CR = Character("crinkle", 1.2)

SHOULDER = (1330, 760)                # the driver's shoulder, off the right edge of the frame
GRIP_AT = (1055, 772)                 # wrist position with the fist on top of the wheel rim
SNIP_BLINKS = (1.9, 6.6, 7.7, 9.6, 11.9, 13.4, 16.2)
CR_BLINKS = (1.3, 3.0, 6.2, 8.4, 10.6, 12.6, 14.2, 16.0)


# ---------------------------------------------------------------- helpers
def blinking(t, times, d=0.13):
    return any(0 <= t - b < d for b in times)


def spring(t, t0, amp, freq=5.0, damp=4.5):
    if t < t0:
        return 0.0
    dt = t - t0
    return amp * math.exp(-damp * dt) * math.sin(2 * math.pi * freq * dt)


def breath(t, period=2.0, amp=0.012):
    return 1 + amp * math.sin(2 * math.pi * t / period)


def frozen(t):
    return 2.5 <= t < 4.5


def pop_scale(t, t0, d=0.3):
    return ease_out_back(seg(t, t0, t0 + d))


def near(a, ref):
    return a + 360 * round((ref - a) / 360)


def bounce(t, t0, t1, height):
    """One trampoline bounce t0 -> t1: (hop, squash, cushion_sink)."""
    p = seg(t, t0, t1)
    if 0 < p < 1:
        h = height * math.sin(math.pi * p)
        land = max(0.0, 1 - p / 0.13) + max(0.0, 1 - (1 - p) / 0.13)
        return h, 1 + 0.07 * math.sin(math.pi * p) - 0.13 * land, 16 * land
    return 0.0, 1.0, 0.0


# ---------------------------------------------------------------- the drive
def offset(t):
    """How far the car has driven (scenery scroll, px)."""
    if t < T_GO or t >= T_RESET:
        return 0.0
    t_dn = T_STOP - RD
    t = min(t, T_STOP)
    u = min(1.0, (t - T_GO) / RU)
    o = V * RU * (u ** 3 - u ** 4 / 2)
    if t > T_GO + RU:
        o += V * (min(t, t_dn) - T_GO - RU)
    if t > t_dn:
        v = (t - t_dn) / RD
        o += V * RD * (v - (v ** 3 - v ** 4 / 2))
    return o


def speed(t):
    if t < T_GO or t >= T_STOP:
        return 0.0
    return ease_in_out(seg(t, T_GO, T_GO + RU)) * (1 - ease_in_out(seg(t, T_STOP - RD, T_STOP)))


def bob(t):
    k = speed(t)
    if k <= 0:
        return 0.0
    return k * (3.5 * math.sin(2 * math.pi * 2.6 * t) + 2.0 * math.sin(2 * math.pi * 1.1 * t + 1.0))


# ---------------------------------------------------------------- arms and belts
def shoulder(ch, st, side):
    return ch.shoulder_pt(st["x"], st["y"], side, st["hop"], st["lean"], st["sq"])


def reach(ch, st, side, target, ref):
    """Arm angle (and stretch) so the paw lands on target. Paper arms stretch a little."""
    sh = shoulder(ch, st, side)
    dx, dy = target[0] - sh[0], target[1] - sh[1]
    a = math.degrees(math.atan2(dx, dy)) - st["lean"]
    stretch = min(1.4, max(0.75, math.hypot(dx, dy) / ch.arm_len))
    return near(a, ref), stretch


def tip(ch, st, side):
    arm = st["arm_l"] if side == "l" else st["arm_r"]
    k = st["str_l"] if side == "l" else st["str_r"]
    sh = shoulder(ch, st, side)
    vx, vy = rot(0, ch.arm_len * k, arm + st["lean"])
    return sh[0] + vx, sh[1] + vy


def belt_pt(belt, key, x, base):
    dx, dy = belt[key]
    return (x + dx, base + dy)


def tongue_state(t, ch, st, belt, t_grab, t_mid, t_pass, t_click, cbase):
    """(tip position, angle, held_by) of the tongue. Positions follow the paws while held."""
    x = st["x"]
    rest = belt_pt(belt, "REST", x, cbase)
    sway = 0.0
    if ch is SNIP and 4.5 <= t < 6.4 and not frozen(t):
        sway = 10 * math.sin(2 * math.pi * 2.2 * (t - 4.5)) * (1 - seg(t, 5.9, 6.4))
    if t < t_grab or t >= T_RESET:
        return (rest[0] + sway, rest[1]), sway * 0.6, None
    if t >= t_click:
        b = belt_pt(belt, "B", x, cbase)
        return b, 0.0, None
    side = "l" if t < t_pass else "r"
    p = tip(ch, st, side)
    held = (p[0], p[1] + TONGUE_GRAB)
    k = ease_in_out(seg(t, t_grab, t_grab + 0.12))
    pos = (lerp(rest[0], held[0], k), lerp(rest[1], held[1], k))
    ang = lerp(0, 18, ease_in_out(seg(t, t_grab, t_mid))) * (1 - ease_in_out(seg(t, t_pass, t_click - 0.08)))
    return pos, ang, side


def buckling_arms(t, ch, st, belt, times, cbase):
    """Paw targets while buckling: grab the tongue at the side, pull it across the chest, pass it
    to the other paw, push it into the buckle. Updates st arms in place."""
    t_grab, t_mid, t_pass, t_click = times
    x = st["x"]
    rest = belt_pt(belt, "REST", x, cbase)
    mid = belt_pt(belt, "M", x, cbase)
    b = belt_pt(belt, "B", x, cbase)
    grab = (rest[0], rest[1] - TONGUE_GRAB)
    rest_l = st["arm_l"]
    rest_r = st["arm_r"]
    # left paw: up to the tongue, across to the middle, then back down
    if t_grab - 0.3 <= t < t_pass + 0.35:
        if t < t_grab:
            tgt = grab
            k = ease_in_out(seg(t, t_grab - 0.3, t_grab))
        elif t < t_pass:
            tgt = (lerp(grab[0], mid[0], ease_in_out(seg(t, t_grab + 0.05, t_mid))),
                   lerp(grab[1], mid[1], ease_in_out(seg(t, t_grab + 0.05, t_mid))))
            k = 1.0
        else:
            tgt = mid
            k = 1 - ease_in_out(seg(t, t_pass, t_pass + 0.35))
        a, s = reach(ch, st, "l", tgt, -60)
        st["arm_l"] = lerp(rest_l, a, k)
        st["str_l"] = lerp(1.0, s, k)
    # right paw: meets the left paw in the middle, carries the tongue down into the buckle
    if t_mid - 0.15 <= t < t_click + 0.45:
        top = (b[0], b[1] - TONGUE_GRAB)
        if t < t_pass:
            tgt = mid
            k = ease_in_out(seg(t, t_mid - 0.15, t_pass))
        elif t < t_click:
            q = ease_in_out(seg(t, t_pass, t_click - 0.06))
            tgt = (lerp(mid[0], top[0], q), lerp(mid[1], top[1], q))
            k = 1.0
        else:
            tgt = top
            k = 1 - ease_in_out(seg(t, t_click + 0.15, t_click + 0.45))
        a, s = reach(ch, st, "r", tgt, 60)
        st["arm_r"] = lerp(rest_r, a, k)
        st["str_r"] = lerp(1.0, s, k)


# ---------------------------------------------------------------- Snip
def snip_hook(t, s):
    """Gleeful trampoline bouncing (period 0.5 s, peak at t = 0)."""
    q = ((t - 0.25) / 0.5) % 1.0
    up = math.sin(math.pi * q)
    land = max(0.0, 1 - q / 0.13) + max(0.0, 1 - (1 - q) / 0.13)
    s.update(hop=HOOK_H * up, sq=1 + 0.07 * up - 0.12 * land, sink=14 * land, eyes="sparkle", mouth="grin",
             look=(2, -8))
    s["arm_l"], s["arm_r"] = -14 - 70 * up, 14 + 70 * up
    e = 9 * math.sin(2 * math.pi * q)
    s["ears"] = [e, -e]


def snip_state(t):
    if frozen(t):
        return snip_state(2.4999)
    b = bob(t)
    s = dict(x=SN_X, y=BASE + b, hop=0.0, sq=1.0, sink=0.0, lean=0.0, tilt=0.0, arm_l=-14.0, arm_r=14.0,
             str_l=1.0, str_r=1.0, eyes="normal", mouth="w", look=(0, 0), head_dy=0.0, ears=[0.0, 0.0],
             ear_stretch=1.0, ear_wob=0.0)
    idle_ear = 2.0 * math.sin(2 * math.pi * t / 3.0)

    if t < 2.5 or t >= T_RESET:           # HOOK + DESIRE: bouncing in the parked car, dreaming of the beach
        snip_hook(t, s)
        if 1.05 <= t < 2.5:
            s["look"] = (-4, -9)
    elif t < 4.75:                         # (after the freeze) finishes the bounce
        snip_hook(t, s)
    elif t < 6.0:                          # BOING, BOING ... BONK! ears squash against the roof
        if t < 5.2:
            h, sq, sink = bounce(t, 4.75, 5.2, 100)
        else:
            h, sq, sink = bounce(t, 5.2, 5.9, 190)
        if t >= 5.9:
            h, sq, sink = 0.0, 1 - 0.14 * (1 - seg(t, 5.9, 6.0)), 18 * (1 - seg(t, 5.9, 6.0))
        s.update(hop=h, sq=sq, sink=sink, eyes="sparkle", mouth="grin", look=(0, -9))
        up = math.sin(math.pi * seg(t, 4.75, 5.2)) if t < 5.2 else math.sin(math.pi * seg(t, 5.2, 5.9))
        s["arm_l"], s["arm_r"] = -14 - 100 * up, 14 + 100 * up
        if t >= T_HIT:
            s.update(eyes="wide", mouth="O", look=(0, -10))
            s["arm_l"], s["arm_r"] = lerp(-114, -30, seg(t, T_HIT, 5.9)), lerp(114, 30, seg(t, T_HIT, 5.9))
        if t >= 5.85:
            s.update(eyes="worried", mouth="wobble")
        s["ear_wob"] = spring(t, 5.72, 22, 4.0, 3.2)
    elif t < 8.0:                          # dazed, then sheepish; sees the hand + Crinkle pointing; nods
        h = 0.0
        s.update(eyes="worried" if t < 7.15 else "normal", mouth="wobble" if t < 7.15 else "w",
                 look=(0, -10) if t < 6.4 else (6, -5) if t < 6.9 else (-6, 6))
        droop = 26 * ease_out(seg(t, 6.0, 6.4)) * (1 - ease_in_out(seg(t, 7.2, 7.7)))
        s["ears"] = [droop, -droop]
        s["ear_wob"] = spring(t, 5.72, 22, 4.0, 3.2)
        s["head_dy"] = 14 * (math.sin(math.pi * seg(t, 7.2, 7.45)) + math.sin(math.pi * seg(t, 7.5, 7.75)))
        s["tilt"] = -6 * math.sin(math.pi * seg(t, 6.0, 6.9))
    elif t < T_GO:                         # BUCKLE UP: grab, pull across, click (1); then watch Crinkle
        s.update(eyes="normal", mouth="w", look=(-6, 6))
        if t >= T_SN_CLICK:
            s.update(eyes="happy" if t < 9.4 else "normal", mouth="grin" if t < 9.4 else "smile", look=(8, 4))
            e = spring(t, T_SN_CLICK, 12, 5.0, 3.5)
            s["ears"] = [e, -e]
            if t >= 10.4:
                s.update(look=(9, -8), eyes="sparkle" if t >= T_THUMB else "normal",
                         mouth="grin" if t >= T_THUMB else "smile")
        buckling_arms(t, SNIP, s, SN_BELT, (T_SN_GRAB, T_SN_MID, T_SN_PASS, T_SN_CLICK), BASE + b)
    elif t < 14.6:                         # the happy ride: wiggle to the music, look out of the window
        s.update(eyes="happy", mouth="grin", look=(-6, -6))
        if 12.0 <= t < 13.4:
            s.update(eyes="sparkle", look=(-9, -6))
        s["tilt"] = 6 * math.sin(2 * math.pi * 1.0 * (t - T_GO)) * ease_in_out(seg(t, 12.0, 12.4))
        e = 7 * math.sin(2 * math.pi * 2.0 * (t - T_GO))
        s["ears"] = [e, -e]
        if 13.6 <= t:
            s.update(eyes="sparkle", mouth="grin", look=(-10, -2))
    elif t < 16.15:                        # PAW-BUMP (seated)
        s.update(eyes="happy", mouth="grin")
        wind = ease_in_out(seg(t, 14.8, 15.1))
        swing = ease_out_back(seg(t, 15.1, 15.45))
        meet = (PAW_MEET[0] - 24, PAW_MEET[1] + b)
        a, k = reach(SNIP, s, "r", meet, 140)
        s["arm_r"] = lerp(lerp(14, -6, wind), a, swing)
        s["str_r"] = lerp(1.0, k, swing)
        e = spring(t, 15.45, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
        s["head_dy"] = -10 * math.sin(math.pi * seg(t, 15.4, 15.8))
    else:                                  # waves as the heart closes
        s.update(eyes="happy", mouth="grin")
        a, k = reach(SNIP, dict(s, arm_r=0), "r", (PAW_MEET[0] - 24, PAW_MEET[1] + b), 140)
        s["arm_r"] = lerp(a, 150 + 20 * math.sin((t - 16.15) * 16), ease_out(seg(t, 16.15, 16.35)))
        s["str_r"] = lerp(k, 1.0, ease_out(seg(t, 16.15, 16.35)))

    s["ears"][0] += idle_ear + s["ear_wob"]
    s["ears"][1] -= idle_ear + s["ear_wob"]
    s["y"] += s["sink"]
    if s["hop"] == 0 and s["sink"] == 0:
        s["sq"] *= breath(t)
    roof_ears(s, b)
    return s


def roof_ears(s, b):
    """Squash the ears flat (and splay them) where they would poke through the roof."""
    hp = SNIP.head_pivot(s["x"], s["y"], s["hop"], s["lean"], s["sq"], s["head_dy"])
    ear_base = hp[1] - 180 * SNIP.s
    room = ear_base - (PC.ROOF_IN + b) - 6
    full = 255 * SNIP.s * 0.985
    if room < full:
        k = max(0.45, room / full)
        s["ear_stretch"] = k
        splay = 46 * (1 - k)
        s["ears"][0] += splay
        s["ears"][1] -= splay
        s["squashed"] = True


# ---------------------------------------------------------------- Crinkle
def crinkle_state(t):
    if frozen(t):
        return crinkle_state(2.4999)
    b = bob(t)
    s = dict(x=CR_X, y=BASE + b, hop=0.0, sq=1.0, lean=0.0, arm_l=CR_REST_L, arm_r=2.0, str_l=1.0, str_r=1.0,
             eyes="normal", mouth="smile", look=(-7, -3), head_dy=0.0)
    if t < 2.5 or t >= T_RESET:            # sits nicely, smiling at Snip's bouncing
        if 1.05 <= t < 2.5:
            s.update(look=(-6, -9), eyes="sparkle", mouth="grin")
        s["head_dy"] = 4 * math.sin(2 * math.pi * t / 0.5) if t < 1.05 or t >= T_RESET else 0.0
    elif t < 6.0:                          # uh-oh: watches Snip bounce higher and higher
        s.update(eyes="wide", mouth="o", look=(-8, -9), lean=4 * ease_out(seg(t, 4.6, 5.0)))
        if t >= T_HIT:
            s.update(eyes="worried", mouth="o")
    elif t < 8.0:                          # points at Snip's belt
        point = ease_out_back(seg(t, 6.05, 6.35)) * (1 - ease_in_out(seg(t, 7.7, 8.0)))
        s["arm_l"] = lerp(CR_REST_L, -78 + 360, point)
        s.update(eyes="normal", mouth="smile", look=(-9, 5), lean=lerp(4, -4, ease_in_out(seg(t, 6.0, 6.4))))
        s["head_dy"] = 10 * math.sin(math.pi * seg(t, 7.25, 7.55))
    elif t < T_GO:                         # watches Snip click, then buckles up (2)
        s.update(look=(-8, 6), lean=-4 * (1 - ease_in_out(seg(t, 8.0, 8.3))))
        if t >= T_SN_CLICK:
            s.update(eyes="happy" if t < 9.3 else "normal", mouth="grin" if t < 9.3 else "smile", look=(-3, 7))
        if t >= T_CR_CLICK:
            s.update(eyes="happy", mouth="grin", look=(6, -6))
            if t >= 10.4:
                s.update(eyes="sparkle" if t >= T_THUMB else "normal", look=(9, -9))
        buckling_arms(t, CR, s, CR_BELT, (T_CR_GRAB, T_CR_MID, T_CR_PASS, T_CR_CLICK), BASE + b)
        if t < T_CR_GRAB - 0.3:
            s["arm_l"] = CR_REST_L
    elif t < 14.6:                         # the happy ride
        s.update(eyes="happy", mouth="grin", look=(-6, -4))
        s["head_dy"] = 6 * math.sin(2 * math.pi * 2.0 * (t - T_GO))
        if 13.6 <= t:
            s.update(eyes="sparkle", look=(-10, -2))
    elif t < 16.15:                        # PAW-BUMP
        s.update(eyes="happy", mouth="grin", look=(-6, 2))
        wind = ease_in_out(seg(t, 14.8, 15.1))
        swing = ease_out_back(seg(t, 15.1, 15.45))
        a, k = reach(CR, s, "l", (PAW_MEET[0] + 24, PAW_MEET[1] + b), 210)
        s["arm_l"] = lerp(lerp(CR_REST_L, 360, wind), a, swing)
        s["str_l"] = lerp(1.0, k, swing)
        s["head_dy"] = -8 * math.sin(math.pi * seg(t, 15.4, 15.8))
    else:
        s.update(eyes="happy", mouth="grin")
        a, k = reach(CR, dict(s, arm_l=0), "l", (PAW_MEET[0] + 24, PAW_MEET[1] + b), 210)
        s["arm_l"], s["str_l"] = a, k
        s["arm_r"] = lerp(2, 140 + 22 * math.sin((t - 16.15) * 16), ease_out(seg(t, 16.15, 16.35)))
    if s["hop"] == 0:
        s["sq"] *= breath(t + 0.7, 2.25, 0.01)
    return s


PAW_MEET = (452, BASE - 288)


# ---------------------------------------------------------------- the grown-up's hand
def hand_state(t, sn_tongue, cr_tongue):
    """(pose, wrist position, hand angle, scale). The arm reaches in from the right edge."""
    if frozen(t):
        return hand_state(2.4999, sn_tongue, cr_tongue)
    b = bob(t)
    grip = (GRIP_AT[0], GRIP_AT[1] + b)
    sn_buckle = belt_pt(SN_BELT, "B", SN_X, BASE + b)
    sn_buckle = (sn_buckle[0], sn_buckle[1] - 20)
    if t < T_HAND_OFF or t >= T_RESET:
        return "grip", grip, 0.0, 1.0
    if t < T_POINT:                        # lifts off the wheel and reaches back over the seats
        k = ease_in_out(seg(t, T_HAND_OFF, T_POINT))
        pos = (lerp(grip[0], POINT_SN[0], k), lerp(grip[1], POINT_SN[1], k) - 50 * math.sin(math.pi * k))
        if k < 0.5:
            return "grip", pos, 0.0, 1.0
        return "point", pos, aim_hand(pos, sn_buckle), 1.0
    if t < T_SN_CLICK + 0.25:              # points at Snip's belt and waits (tap, tap, tap)
        tap = 0.0
        if t < 7.9:
            tap = abs(math.sin(2 * math.pi * 2.0 * (t - T_POINT))) * ease_in_out(seg(t, T_POINT + 0.15, T_POINT + 0.35))
        target = sn_buckle if t < 7.9 else sn_tongue
        if 7.9 <= t < 8.2:
            k = ease_in_out(seg(t, 7.9, 8.2))
            target = (lerp(sn_buckle[0], sn_tongue[0], k), lerp(sn_buckle[1], sn_tongue[1], k))
        pos = (POINT_SN[0], POINT_SN[1] - 12 * tap)
        return "point", pos, aim_hand(pos, target) + 8 * tap, 1.0
    if t < 10.2:                           # then at Crinkle's belt
        k = ease_in_out(seg(t, T_SN_CLICK + 0.25, T_SN_CLICK + 0.6))
        pos = (lerp(POINT_SN[0], POINT_CR[0], k), lerp(POINT_SN[1], POINT_CR[1], k) - 40 * math.sin(math.pi * k))
        return "point", pos, aim_hand(pos, cr_tongue), 1.0
    if t < T_WHEEL:                        # (3) thumbs-up!
        k = ease_in_out(seg(t, 10.2, T_THUMB - 0.05))
        pos = (lerp(POINT_CR[0], THUMB_AT[0], k), lerp(POINT_CR[1], THUMB_AT[1], k))
        if t < T_THUMB - 0.12:
            return "point", pos, lerp(aim_hand(pos, cr_tongue), 0, k), 1.0
        sc = 1.0 + 0.25 * pop_scale(t, T_THUMB - 0.12, 0.3) * (1 - ease_in_out(seg(t, 10.95, T_WHEEL)))
        return "thumb", pos, 6 * math.sin(2 * math.pi * 2.5 * (t - T_THUMB)) * (1 - seg(t, 10.6, 11.1)), sc
    k = ease_in_out(seg(t, T_WHEEL, T_WHEEL + 0.35))
    pos = (lerp(THUMB_AT[0], grip[0], k), lerp(THUMB_AT[1], grip[1], k) - 30 * math.sin(math.pi * k))
    return ("thumb" if k < 0.5 else "grip"), pos, 0.0, 1.0


POINT_SN = (500, 552)                 # wrist above the gap between the friends' heads
POINT_CR = (968, 640)
THUMB_AT = (1000, 690)


def aim_hand(wrist, target):
    """Angle that turns the left-pointing finger toward target."""
    dx, dy = target[0] - wrist[0], target[1] - wrist[1]
    return math.degrees(math.atan2(dy, -dx))


def draw_hand(f, hs):
    pose, pos, ang, sc = hs
    ARM.draw(f, SHOULDER, pos)
    spr = {"grip": H_GRIP, "point": H_POINT, "thumb": H_THUMB}[pose]
    place(f, spr, pos, angle=ang, scale=sc)


# ---------------------------------------------------------------- frame
_bg_cache = {}


def background(o):
    key = round(o, 1)
    if key in _bg_cache:
        return _bg_cache[key].copy()
    f = SKY.copy()
    co = int(round(o * 0.25))
    f.alpha_composite(CLOUDS.crop((co, 0, co + scene.W, CLOUDS.height)), (0, 0))
    so = int(round(o))
    f.alpha_composite(SCENERY.crop((so, 0, so + scene.W, SCENERY.height)), (0, 0))
    ro = int(round(o)) % PC.DASH_P
    f.alpha_composite(ROAD.crop((ro, 0, ro + scene.W, ROAD.height)), (0, 1500))
    if o == 0:
        _bg_cache[key] = f.copy()
    return f


def draw_char(f, ch, st, t, blink_times):
    kw = dict(hop=st["hop"], lean=st["lean"], arm_l=st["arm_l"], arm_r=st["arm_r"], eyes=st["eyes"],
              mouth=st["mouth"], look=st["look"], squash=st["sq"], head_dy=st["head_dy"],
              blink=blinking(t, blink_times) and not frozen(t))
    if ch is SNIP:
        kw.update(head_tilt=st["tilt"], ears=tuple(st["ears"]), ear_stretch=st["ear_stretch"])
    ch.draw(f, st["x"], st["y"], **kw)


def draw_arms(f, ch, st):
    """Arms redrawn in front of the belt (stretched when reaching)."""
    for side in ("l", "r"):
        spr = ch.arm_l if side == "l" else ch.arm_r
        ang = (st["arm_l"] if side == "l" else st["arm_r"]) + st["lean"]
        k = st["str_l"] if side == "l" else st["str_r"]
        place(f, spr, shoulder(ch, st, side), angle=ang, sy=k)


def draw_belt(f, belt, x, cbase, tpos, tang, glow=0.0):
    g = belt_pt(belt, "G", x, cbase)
    lap = belt_pt(belt, "L", x, cbase)
    sx, sy = rot(0, -TONGUE_SLOT, tang)
    slot = (tpos[0] + sx, tpos[1] + sy)
    draw_strap(f, lap, slot)
    draw_strap(f, g, slot)
    place(f, GUIDE, g)
    return slot


def draw_strap(f, a, b):
    PC.draw_strap(f, a, b, 34)


def render_frame(t):
    frz = frozen(t)
    o = offset(t)
    b = bob(t)
    f = background(o)
    sn = snip_state(t)
    cr = crinkle_state(t)
    sn_base, cr_base = BASE + b, BASE + b

    # the car: shadow, wheels, far side of the cabin, glass
    place(f, CAR_SHADOW, (560, PC.ROAD_Y + 4), shadow=False)
    place(f, CAR_BACK, (0, b))
    place(f, GLASS, (0, b), shadow=False)

    # seats
    cush_sq = 1 - 0.012 * sn["sink"]
    place(f, CR_BACK, (CR_X, cr_base + 20))
    place(f, SN_BACK, (SN_X, sn_base + 20))

    # tongues (where they are this frame)
    sn_t = tongue_state(t, SNIP, sn, SN_BELT, T_SN_GRAB, T_SN_MID, T_SN_PASS, T_SN_CLICK, sn_base)
    cr_t = tongue_state(t, CR, cr, CR_BELT, T_CR_GRAB, T_CR_MID, T_CR_PASS, T_CR_CLICK, cr_base)

    # Crinkle (in his booster) with his belt, arms in front of the belt
    draw_char(f, CR, cr, t, CR_BLINKS)
    place(f, CR_CUSH, (CR_X, cr_base))
    place(f, RECEIVER, belt_pt(CR_BELT, "B", CR_X, cr_base))
    draw_belt(f, CR_BELT, CR_X, cr_base, cr_t[0], cr_t[1])
    place(f, TONGUE, cr_t[0], angle=cr_t[1])
    draw_arms(f, CR, cr)

    # Snip (bouncing!) with the belt
    draw_char(f, SNIP, sn, t, SNIP_BLINKS)
    place(f, SN_CUSH, (SN_X, BASE + b + 0.5 * sn["sink"]), sy=cush_sq)
    # the hanging belt glows while everyone points at it
    gl = 0.0
    if 5.3 <= t < 8.2:
        gl = (0.55 + 0.35 * math.sin(2 * math.pi * 2.0 * t)) * ease_in_out(seg(t, 5.3, 5.6)) * (1 - ease_in_out(seg(t, 7.95, 8.2)))
    if gl > 0.01:
        place(f, GLOW, (sn_t[0][0], sn_t[0][1] - 45), alpha=gl, scale=1.2, shadow=False)
    if gl > 0.01:
        rb = belt_pt(SN_BELT, "B", SN_X, sn_base)
        place(f, GLOW, (rb[0], rb[1] + 20), alpha=gl, scale=1.1, shadow=False)
    place(f, RECEIVER, belt_pt(SN_BELT, "B", SN_X, sn_base))
    draw_belt(f, SN_BELT, SN_X, sn_base, sn_t[0], sn_t[1])
    if sn_t[2] is None:
        place(f, TONGUE, sn_t[0], angle=sn_t[1], scale=1.0 + 0.12 * gl)
    draw_arms(f, SNIP, sn)
    if sn_t[2] is not None:                # the tongue in Snip's paw, in front so it reads
        place(f, TONGUE, sn_t[0], angle=sn_t[1])
    if cr_t[2] is not None:
        place(f, TONGUE, cr_t[0], angle=cr_t[1])

    # dotted path: where the belt goes (over the shoulder, across the lap)
    if 6.55 <= t < 8.15:
        draw_belt_path(f, t, sn_base)

    # the near side of the car (lower door panel) in front of the seats
    place(f, CAR_FRONT, (0, b))
    spin = -math.degrees(o / PC.WHEEL_R)
    for wx, wy in PC.WHEELS:
        place(f, WHEEL, (wx, wy), angle=spin)

    # steering wheel and the grown-up's hand
    place(f, STEER, (PC.STEER[0] - 52, PC.STEER[1] + b))
    hs = hand_state(t, (sn_t[0][0], sn_t[0][1] - 40), (cr_t[0][0], cr_t[0][1] - 40))
    draw_hand(f, hs)

    # bonk on the roof
    if T_HIT - 0.02 <= t < T_HIT + 0.5:
        k = seg(t, T_HIT - 0.02, T_HIT + 0.5)
        for dx, sc in ((-70, 0.6), (70, 0.5), (0, 0.75)):
            place(f, BONK, (SN_X + dx * (1 + 0.5 * k), PC.ROOF_IN + 40 + 30 * k), scale=sc * pop_scale(t, T_HIT - 0.02, 0.15),
                  alpha=1 - ease_in_out(seg(k, 0.5, 1.0)), angle=60 * k * (1 if dx >= 0 else -1))

    # clicks
    for tc, belt, x in ((T_SN_CLICK, SN_BELT, SN_X), (T_CR_CLICK, CR_BELT, CR_X)):
        if tc <= t < tc + 0.5:
            bp = belt_pt(belt, "B", x, BASE + b)
            place(f, CLICK, (bp[0], bp[1] - 10), scale=pop_scale(t, tc, 0.15) * 0.9,
                  alpha=1 - ease_in_out(seg(t, tc + 0.3, tc + 0.5)), angle=40 * seg(t, tc, tc + 0.5))

    # hearts on the happy ride
    for i, (t0, x, y) in enumerate(HEART_PLAN):
        if t0 <= t < 14.3:
            p = seg(t, t0, 14.3)
            place(f, HEARTS[i], (x + 12 * math.sin(t * 3 + i), y - 150 * p + b), scale=pop_scale(t, t0, 0.25),
                  alpha=1 - ease_in_out(seg(t, 13.9, 14.3)), angle=10 * math.sin(t * 2.5 + i))

    # paw-bump: both touching paws in front, sparkle
    if 15.1 <= t < 16.3:
        place(f, SNIP.arm_r, shoulder(SNIP, sn, "r"), angle=sn["arm_r"] + sn["lean"], sy=sn["str_r"])
        place(f, CR.arm_l, shoulder(CR, cr, "l"), angle=cr["arm_l"] + cr["lean"], sy=cr["str_l"])
    if 15.45 <= t < 16.2:
        a, c = tip(SNIP, sn, "r"), tip(CR, cr, "l")
        mid = ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2 - 10)
        place(f, SPARKLE, (mid[0], mid[1] - 40), scale=pop_scale(t, 15.45, 0.22) * 0.6, angle=(t - 15.45) * 60,
              alpha=1 - ease_in_out(seg(t, 15.9, 16.2)))

    out = camera(f, t)

    # thought bubble: the beach!
    if 1.05 <= t < 2.5:
        k = pop_scale(t, 1.05, 0.35) * (1 - ease_in_out(seg(t, 2.2, 2.45)))
        for i, (dx, dy, t0) in enumerate(((440, 610, 1.05), (500, 520, 1.12))):
            place(out, TDOTS[i], (dx, dy), scale=pop_scale(t, t0, 0.2) * (1 - ease_in_out(seg(t, 2.2, 2.45))))
        place(out, THOUGHT, (560, 330), scale=k, angle=2 * math.sin(t * 3))

    # FREEZE: dim + choice bubbles (screen space)
    if 2.5 <= t < 4.6:
        dim = 0.32 * ease_in_out(seg(t, 2.5, 2.8)) * (1 - ease_in_out(seg(t, 4.35, 4.6)))
        if dim > 0.01:
            out.alpha_composite(Image.new("RGBA", out.size, (30, 26, 52, int(255 * dim))))
        gone = 1 - ease_in_out(seg(t, 4.4, 4.55))
        pulse_a = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 2.95) / 1.0))
        pulse_b = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 3.45) / 1.0))
        place(out, BUB_BOUNCE, (290, 330), scale=1.2 * pop_scale(t, 2.55) * gone * (pulse_a if t > 2.95 else 1))
        place(out, BUB_BUCKLE, (790, 330), scale=1.2 * pop_scale(t, 2.7) * gone * (pulse_b if t > 3.45 else 1))
        place(out, QMARK, (540, 230), scale=pop_scale(t, 2.85, 0.25) * gone, angle=8 * math.sin(t * 4))

    # counting numerals (screen space, big)
    for i, c in enumerate(COUNTS):
        if c <= t < c + 0.62:
            k = pop_scale(t, c, 0.25) * (1 - ease_in_out(seg(t, c + 0.45, c + 0.62)))
            place(out, NUMS[i], (540, 200), scale=k, angle=-6 + 4 * math.sin(t * 6))
    if T_THUMB + 0.1 <= t < T_THUMB + 0.9:
        place(out, CHECK, (700, 470), scale=pop_scale(t, T_THUMB + 0.1, 0.25) * (1 - ease_in_out(seg(t, T_THUMB + 0.7, T_THUMB + 0.9))))

    # heart iris back to the start (loop)
    if T_IRIS0 <= t < T_OPEN1:
        if t < T_IRIS1:
            size = lerp(4300, 0, ease_in_out(seg(t, T_IRIS0, T_IRIS1)) ** 0.7)
            ctr = (500, 900)
        elif t < T_RESET + 0.06:
            size, ctr = 0, IRIS_OPEN_AT
        else:
            size = lerp(0, 4300, ease_in_out(seg(t, T_RESET + 0.06, T_OPEN1)) ** 1.6)
            ctr = IRIS_OPEN_AT
        out = IRIS.apply(out, ctr, size)
    return out


def draw_belt_path(f, t, base):
    k = ease_in_out(seg(t, 6.55, 7.0)) * (1 - ease_in_out(seg(t, 7.95, 8.15)))
    g = belt_pt(SN_BELT, "G", SN_X, base)
    lap = belt_pt(SN_BELT, "L", SN_X, base)
    bk = belt_pt(SN_BELT, "B", SN_X, base)
    bk = (bk[0], bk[1] - TONGUE_SLOT + 20)
    draw_len = ease_in_out(seg(t, 6.6, 7.3))
    for a, c in ((g, bk), (lap, bk)):
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        n = int(L / 30)
        for i in range(n + 1):
            u = i / max(1, n)
            if u > draw_len:
                break
            p = (lerp(a[0], c[0], u), lerp(a[1], c[1], u))
            beat = 0.5 + 0.5 * math.sin(2 * math.pi * (1.6 * t - u * 2))
            place(f, DOT_Y if beat > 0.6 else DOT, p, scale=k * (0.9 + 0.25 * beat))


CAM0 = (1.45, 330, 1000)


def _iris_open_at():
    z, cx, cy = CAM0
    hp = SNIP.head_pivot(SN_X, BASE, HOOK_H)
    face_y = hp[1] - 110 * 1.15
    left = min(max(cx - scene.W / z / 2, 0), scene.W - scene.W / z)
    top = min(max(cy - scene.H / z / 2, 0), scene.H - scene.H / z)
    return ((SN_X - left) * z, (face_y - top) * z)


CAM_KEYS = [
    (0.0,) + CAM0, (1.0, 1.47, 330, 1000), (2.3, 1.0, 540, 960), (4.6, 1.0, 540, 960),
    (5.0, 1.08, 470, 920), (6.1, 1.08, 470, 920), (6.5, 1.0, 540, 960), (7.75, 1.0, 540, 960),
    (8.25, 1.14, 482, 1060), (10.1, 1.14, 482, 1060), (10.55, 1.0, 540, 960), (14.7, 1.0, 540, 960),
    (15.05, 1.1, 480, 1010), (16.3, 1.1, 480, 1010), (T_IRIS1, 1.0, 540, 960), (T_RESET, 1.0, 540, 960),
    (T_RESET + 0.01,) + CAM0, (DUR,) + CAM0]

IRIS_OPEN_AT = _iris_open_at()


def camera(f, t):
    z, cx, cy = 1.0, 540, 960
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
    if T_HIT <= t < T_HIT + 0.35:          # little bonk shake, eased in and out
        k = math.sin(math.pi * seg(t, T_HIT, T_HIT + 0.35))
        cy += 4 * k * math.sin(t * 90)
    if z < 1.001 and cx == 540 and cy == 960:
        return f
    w, h = scene.W / z, scene.H / z
    left = min(max(cx - w / 2, 0), scene.W - w)
    top = min(max(cy - h / 2, 0), scene.H - h)
    return f.resize((scene.W, scene.H), Image.BICUBIC, box=(left, top, left + w, top + h))


# ---------------------------------------------------------------- audio
def build_audio(path):
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    M = A.midi
    # hook + desire: boing-boing bouncing, the beach dream
    A.jingle(music, 0.02)
    for tt in (0.25, 0.75, 1.25, 1.75, 2.25):
        sfx.add(tt, A.boing(0.45, 300 + 20 * (tt * 4 % 3)))
    for tt, ch, up in ((1.0, "C", False), (1.25, "C", True), (1.5, "F", False), (1.75, "F", True),
                       (2.0, "G", False), (2.25, "G", True)):
        MX.comp(music, tt, ch, 0.7, up, inst="organ")
    for tt, m in ((1.0, 48), (1.5, 41), (2.0, 43)):
        music.add(tt, A.bass(M(m), 0.5, 0.7))
    sfx.add(1.05, A.twinkle(0.8))
    sfx.add(1.1, PS.chirp(0.4))
    sfx.add(2.4, A.pop(0.6))
    # freeze
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
    # slapstick: boing, BOING, bonk, spring-wobble; the hand points and taps
    sfx.add(4.75, A.boing(0.7, 320))
    sfx.add(5.2, A.boing(0.9, 380))
    for i, m in enumerate((60, 64, 67, 72)):
        music.add(4.75 + i * 0.11, A.pluck(M(m), 0.3, 0.6))
    sfx.add(T_HIT, PC.bonk(1.0))
    sfx.add(T_HIT + 0.03, A.snare_roll(0.12, 0.5))
    sfx.add(T_HIT + 0.15, PC.spring_wobble(0.9, 560, 0.8))
    sfx.add(5.9, A.boing(0.5, 240))
    music.add(6.0, A.wah_down(0.8))
    sfx.add(T_HAND_OFF, A.whoosh(0.4, 0.6))
    tt = T_POINT + 0.25
    while tt < 7.9:
        sfx.add(tt, A.tap(0.55))
        tt += 0.5
    # Crinkle points; the dotted belt path draws itself
    sfx.add(6.1, A.glock(M(91), 1.2, 0.7))
    sfx.add(6.15, A.glock(M(88), 1.2, 0.5))
    for tt, ch in ((6.5, "Am"), (7.0, "F"), (7.5, "C")):
        MX.comp(music, tt, ch, 0.55, inst="organ")
        music.add(tt, A.bass(M({"Am": 45, "F": 41, "C": 48}[ch]), 0.5, 0.6))
    sfx.add(6.6, A.twinkle(0.6, (96, 100, 103, 108)))
    for tt in (7.25, 7.5):
        sfx.add(tt, A.tap(0.5))
    # buckle up: zip, CLICK (1); zip, CLICK (2); thumbs-up (3)
    for t_grab, t_click in ((T_SN_GRAB, T_SN_CLICK), (T_CR_GRAB, T_CR_CLICK)):
        sfx.add(t_grab - 0.05, A.pop(0.4))
        sfx.add(t_grab + 0.05, PC.belt_zip(t_click - t_grab - 0.1, 0.8))
        sfx.add(t_click, PC.buckle_click(1.0))
    tt = 7.95
    while tt < T_THUMB:
        sfx.add(tt, PS.tick(0.35, 1500 if round((tt - 7.95) / 0.33) % 2 == 0 else 1200))
        tt += 0.33
    for c, m in zip(COUNTS, (84, 88, 91)):
        sfx.add(c + 0.04, A.glock(M(m), 1.2, 0.9))
        music.add(c, A.ks_pluck(M(m - 24), 1.0, 0.8))
        music.add(c, A.bass(M(48), 0.4, 0.5))
    sfx.add(10.3, A.whoosh(0.35, 0.5))
    sfx.add(T_THUMB + 0.1, A.chime_up(1.0))
    sfx.add(T_THUMB + 0.15, A.twinkle(0.6))
    MX.comp(music, T_THUMB, "C", 0.7, inst="organ")
    sfx.add(T_WHEEL + 0.3, A.tap(0.5))
    # the drive: a soft purr and a happy tune
    sfx.add(T_GO - 0.1, PC.engine(T_STOP - T_GO + 0.5, 0.6, 1.0, 1.4))
    melody = (72, 76, 79, 76, 74, 77, 81, 77, 76, 79, 84, 79, 77, 76, 74, 72)
    for i, m in enumerate(melody):
        tt = T_GO + 0.1 + i * 0.25
        if tt < 15.3:
            music.add(tt, MX.steel_pan(M(m), 0.5, 0.6))          # beach-bound: steel pan lead
    for i, ch in enumerate(("C", "F", "G", "C", "Am", "F")):
        tt = T_GO + i * 0.5
        MX.comp(music, tt, ch, 0.6, inst="organ")
        MX.comp(music, tt + 0.25, ch, 0.5, True, inst="organ")
        music.add(tt, A.bass(M({"C": 48, "F": 41, "G": 43, "Am": 45}[ch]), 0.45, 0.7))
    for tt, ch, up in ((14.5, "F", False), (14.75, "G", True)):
        MX.comp(music, tt, ch, 0.7, up, inst="organ")
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.45))
    sfx.add(12.4, A.twinkle(0.6))
    sfx.add(13.7, PS.chirp(0.5))
    music.add(13.0, A.shaker(0.4))
    # paw-bump (signature)
    sfx.add(14.85, A.snare_roll(0.6, 0.8))
    sfx.add(15.45, A.boop(0.9))
    A.jingle(music, 15.47, 1.0, ending=True)
    sfx.add(15.5, A.twinkle(0.8))
    # car stops at the beach, heart iris, back to the start
    A.strum(music, 16.3, "F", 0.5)
    A.strum(music, 16.8, "G7", 0.5)
    sfx.add(T_IRIS0, PS.slide_whistle(500, 1400, 0.55, 0.6))
    sfx.add(T_IRIS1, A.pop(0.7))
    sfx.add(T_RESET + 0.1, PS.slide_whistle(1400, 700, 0.5, 0.5))
    for tt in (17.25, 17.75):
        sfx.add(tt, A.boing(0.45, 300))
    sfx.add(17.45, A.uh_oh(0.6))
    music.add(17.2, A.pad([M(55), M(59), M(62)], 0.8, 0.25))

    m = A.reverb(music.normalized(), 0.24)
    s = A.reverb(sfx.normalized(), 0.08)
    y = 0.55 * m / max(1e-9, abs(m).max()) + 0.7 * s / max(1e-9, abs(s).max())
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.01)


# ---------------------------------------------------------------- output
def render(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    wav = os.path.join(ROOT, "build", "ep09_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep09_buckle_up.mp4")
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
    times = times or [0.0, 1.8, 3.4, 4.9, 5.55, 6.2, 7.2, 8.3, 8.8, 9.05, 9.6, 10.05, 10.7, 12.0,
                      13.0, 14.0, 15.6, 16.4, 16.9, 17.5, 17.99]
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


KEYS = [(0.0, "0.0s hook: boing!"), (3.4, "3.4s choice"), (5.6, "5.6s ears bonk the roof"),
        (7.2, "7.2s belt goes here"), (9.05, "9.0s click 1"), (10.05, "10.0s click 2"),
        (10.75, "10.7s 3: thumbs-up"), (15.6, "15.6s ride + paw-bump")]


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
        stills(os.path.join(ROOT, "build", "ep09_stills.png"))
    elif "--keys" in sys.argv:
        os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
        key_sheet(os.path.join(ROOT, "reviews", "ep09_keys.png"))
    else:
        render(os.path.join(ROOT, "output"))
