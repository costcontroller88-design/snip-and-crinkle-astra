"""Episode 5 — Hold Paws to Cross? 🚦

A sunny street: far sidewalk, a two-lane road with a zebra crossing, a pedestrian light
(red standing figure / green walking figure) and cute paper cars with grown-up drivers.
Snip waits at the far curb and sees a ball on the other side. A car drives past. Choice: run
now, or hold a grown-up's hand? Snip's legs wind up like a cartoon... and skid to a stop right at
the curb edge, teetering, then hop back. Crinkle arrives holding a grown-up's hand and shows the
red standing figure; the grown-up's other hand comes down for Snip. They wait and count 1, 2, 3
while the cars roll to a stop, the light turns green, they look left (car stopped) and right (car
stopped), and cross on the zebra holding the grown-up's hands. Ball! Hearts, the signature
paw-bump, and a paper heart-iris wipes back to the start (frame 18.0 == frame 0).

Run:  python3 episodes/ep05_hold_paws_to_cross.py            (render -> output/)
      python3 episodes/ep05_hold_paws_to_cross.py --stills   (contact sheet -> build/)
      python3 episodes/ep05_hold_paws_to_cross.py --keys     (key frames -> reviews/ep05_keys.png)
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
import props_street as P  # noqa: E402
import scene  # noqa: E402
from characters import Character  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, seg  # noqa: E402

FPS = 30
DUR = 18.0
X0 = P.X0
SN_X, CR_X = 420, 720                 # crossing lanes on the zebra
WAIT_Y = 1112                         # standing on the tactile paving, a step back from the curb
EDGE_Y = 1150                         # Snip's toes at the curb edge (skid stop)
NEAR_Y = 1482                         # safe on the near sidewalk
BALL_AT = (560, 1488)
CR_REST_L = 346
SN_HOLD = -128                        # Snip's left arm up to the grown-up's hand (outer side)
CR_HOLD = 132                         # Crinkle's right arm up to the grown-up's other hand
TOP_LANE_Y, BOT_LANE_Y = 1292, 1430   # car ground lines
LAMP_RED = (P.LIGHT_X, P.LIGHT_Y - 145 + 82)
LAMP_GREEN = (P.LIGHT_X, P.LIGHT_Y - 145 + 208)

BG = P.background()
LIGHT_RED = P.ped_light("red")
LIGHT_GREEN = [P.ped_light("green", ph) for ph in (0, 1)]
GLOW_RED = None   # set below (soft radial glow, no square edge)
GLOW_GREEN = None
CAR_A = P.car((255, 186, 72), "left")
CAR_B = P.car((110, 170, 240), "right")
CAR_C = P.car((240, 132, 160), "left", 270)
BALL = P.ball(58)
DUST = P.dust_puff()
WHIRL = P.whirl_frames(6)
SPEED = P.speed_lines()
GLINT = P.glint()
HAND_SN = P.long_hand(1600)
HAND_CR = P.long_hand(1600, mirror=True)
IRIS = P.HeartIris()
BUB_RUN = P.choice_bubble("run", (240, 110, 100))
BUB_HOLD = P.choice_bubble("hold", (90, 190, 120))
QMARK = icons.question()
CHECK = icons.check(130)
SPARKLE = scene.sparkle()
NUMS = [scene.numeral(1, (244, 112, 104)), scene.numeral(2, (255, 196, 52)), scene.numeral(3, (84, 182, 222))]
HEARTS = [scene.heart(c, 80) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120), (255, 150, 170))]
SNIP = Character("snip", 1.15)
CR = Character("crinkle", 1.2)


def soft_glow(color, r):
    import numpy as np
    from paperlib import Sprite
    yy, xx = np.mgrid[-r:r, -r:r]
    a = np.clip(1 - np.hypot(xx, yy) / r, 0, 1) ** 2 * 170
    img = np.zeros((2 * r, 2 * r, 4), np.uint8)
    img[..., :3] = color
    img[..., 3] = a.astype(np.uint8)
    return Sprite(Image.fromarray(img, "RGBA"), (r, r))


GLOW_RED = soft_glow(P.RED_ON, 130)
GLOW_GREEN = soft_glow(P.GREEN_ON, 130)

SNIP_BLINKS = (1.9, 6.4, 8.0, 9.25, 11.7, 14.3, 17.4)
CR_BLINKS = (7.1, 8.6, 9.9, 12.5, 14.4)
T_WIND, T_DASH, T_SKID, T_BACK = 4.6, 5.0, 5.12, 5.62
T_HAND_SN0, T_HAND_SN1 = 7.35, 7.85   # grown-up's hand comes down for Snip
COUNTS = (8.3, 8.95, 9.6)
T_GREEN = 10.1
T_LOOK_L, T_LOOK_R, T_LOOK_END = 10.2, 10.55, 10.9
T_CROSS0, T_CROSS1 = 11.0, 12.55
T_LET_GO = 12.65
T_BALL = 12.95
HEART_PLAN = ((13.2, 330, 900), (13.4, 560, 820), (13.6, 800, 880), (13.8, 450, 760))
T_IRIS0, T_IRIS1, T_RESET, T_OPEN1 = 16.55, 17.1, 17.18, 17.9


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


def C(x, y):
    """scene -> world canvas coordinates"""
    return (x + X0, y)


def tip(ch, st, side):
    arm = st["arm_l"] if side == "l" else st["arm_r"]
    return ch.paw_tip(st["x"] + X0, st["y"], side, arm, st["hop"], st["lean"], st["sq"])


def walk_bob(t, t0, t1, steps):
    p = seg(t, t0, t1)
    if 0 < p < 1:
        return 10 * abs(math.sin(math.pi * steps * p)), 4 * math.sin(math.pi * steps * p)
    return 0.0, 0.0


def cross_y(t):
    return lerp(WAIT_Y, NEAR_Y, ease_in_out(seg(t, T_CROSS0, T_CROSS1)))


# ---------------------------------------------------------------- Snip
def snip_state(t):
    if frozen(t):
        return snip_state(2.4999)
    s = dict(x=SN_X, y=WAIT_Y, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, arm_l=-14.0, arm_r=14.0, eyes="normal",
             mouth="w", look=(0, 0), head_dy=0.0, ears=[0.0, 0.0], ear_stretch=1.0, frizz=0.0, whirl=0.0,
             hug=False)
    idle_ear = 2.0 * math.sin(2 * math.pi * t / 3.0)

    if t < 1.0 or t >= T_RESET:       # HOOK (and the loop back into it): on tiptoes, eyes on the ball
        p = ease_in_out(seg(t, 0.0, 1.0)) if t < 1.0 else 0.0
        s.update(eyes="wide", mouth="o", look=(4, 9), lean=lerp(-4, -7, p))
        s["head_dy"] = 6 * math.sin(2 * math.pi * t / 0.5) if t < 1.0 else 0.0
        s["arm_r"] = lerp(30, 40, p)
        if t >= T_RESET:
            k = ease_in_out(seg(t, T_RESET, DUR))
            s.update(lean=lerp(0, -4, k), arm_r=lerp(14, 30, k))
            s["head_dy"] = 6 * math.sin(2 * math.pi * t / 0.5) * k
    elif t < 2.5:                     # DESIRE: sparkly eyes; a car zooms past -- eyes follow it
        s.update(lean=-7, arm_r=40, eyes="sparkle", mouth="yum", look=(4, 9))
        e = spring(t, 1.0, 10, 4.0, 3.0)
        s["ears"] = [e, -e]
        if 1.45 <= t < 2.35:
            k = seg(t, 1.45, 2.35)
            s.update(eyes="wide", mouth="o", look=(int(lerp(10, -10, k)), 6), tilt=lerp(-6, 6, k))
    elif t < T_WIND:                  # (after the freeze) wiggle and get ready...
        k = ease_in_out(seg(t, 4.5, T_WIND))
        s.update(lean=lerp(-7, 0, k), eyes="sparkle", mouth="grin", look=(4, 9), sq=lerp(1, 0.9, k))
    elif t < T_DASH:                  # WIND-UP legs: brrrrr!
        s.update(eyes="sparkle", mouth="grin", look=(4, 9), hop=18 + 3 * math.sin(t * 90), sq=1.04)
        s["whirl"] = pop_scale(t, T_WIND, 0.12)
        s["arm_l"], s["arm_r"] = -60 + 20 * math.sin(t * 40), 60 - 20 * math.sin(t * 40)
        s["ears"] = [-16, 16]
        s["ear_stretch"] = 1.15
    elif t < T_SKID:                  # ZOOM toward the road...
        k = ease_in_out(seg(t, T_DASH, T_SKID))
        s.update(y=lerp(WAIT_Y, EDGE_Y, k), hop=18 * (1 - k), eyes="sparkle", mouth="grin", sq=1.08, look=(4, 9))
        s["whirl"] = 1.0
        s["arm_l"], s["arm_r"] = -100, 100
        s["ears"] = [-26, 26]
        s["ear_stretch"] = 1.2
    elif t < T_BACK:                  # SKID! teetering right at the curb edge, arms windmilling
        dt = t - T_SKID
        s.update(y=EDGE_Y, eyes="wide", mouth="O", look=(0, 9))
        s["lean"] = 14 * math.exp(-3.0 * dt) * math.sin(2 * math.pi * 3.2 * dt)
        s["sq"] = 1 - 0.12 * math.exp(-14 * dt)
        s["arm_l"] = -150 + 60 * math.sin(2 * math.pi * 4 * dt)
        s["arm_r"] = 150 - 60 * math.sin(2 * math.pi * 4 * dt + 1)
        s["frizz"] = pop_scale(t, T_SKID, 0.15) * (1 - ease_in_out(seg(t, 5.35, 5.6)))
        s["ears"] = [spring(t, T_SKID, 24, 4, 3), -spring(t, T_SKID, 24, 4, 3)]
        s["ear_stretch"] = 1.15
    elif t < 6.2:                     # hop back -- phew! -- sheepish look at the red light
        h, sq = hop_curve(t, T_BACK, T_BACK + 0.3, 1, 40)
        s.update(y=lerp(EDGE_Y, WAIT_Y, ease_out(seg(t, T_BACK, T_BACK + 0.3))), hop=h, sq=sq, eyes="worried",
                 mouth="wobble", look=(-8, -6))
        droop = 22 * ease_out(seg(t, T_BACK + 0.2, T_BACK + 0.5))
        s["ears"] = [droop, -droop]
        s["arm_l"] = lerp(-150, -14, ease_out(seg(t, T_BACK, T_BACK + 0.25)))
        s["arm_r"] = lerp(150, 14, ease_out(seg(t, T_BACK, T_BACK + 0.25)))
    elif t < T_HAND_SN1:              # Crinkle shows the red light; Snip nods; reaches up for the hand
        droop = 22 * (1 - ease_in_out(seg(t, 6.9, 7.3)))
        s.update(eyes="worried" if t < 6.9 else "normal", mouth="wobble" if t < 6.9 else "w",
                 look=(-8, -6) if t < 7.35 else (-6, -9), ears=[droop, -droop])
        s["head_dy"] = 14 * (math.sin(math.pi * seg(t, 6.95, 7.2)) + math.sin(math.pi * seg(t, 7.25, 7.5)))
        s["arm_l"] = lerp(-14, SN_HOLD, ease_in_out(seg(t, 7.45, T_HAND_SN1)))
    elif t < T_CROSS0:                # holding the grown-up's hand: WAIT, count, green, look both ways
        s.update(arm_l=SN_HOLD, eyes="normal", mouth="w", look=(-6, -8))
        if t < 8.1:
            s.update(eyes="happy", mouth="grin")
            e = spring(t, T_HAND_SN1, 10, 5.0, 3.5)
            s["ears"] = [e, -e]
        for c in COUNTS:
            if 0 <= t - c < 0.3:
                s["mouth"] = "o"
            s["head_dy"] += 12 * math.sin(math.pi * seg(t, c, c + 0.3))
            e = spring(t, c, 7, 5.0, 5.0)
            s["ears"][0] += e
            s["ears"][1] -= e
        if t >= T_GREEN:
            s.update(eyes="sparkle", mouth="grin", look=(-8, -6))
        if T_LOOK_L <= t < T_LOOK_END:  # look LEFT ... then RIGHT
            kl = ease_in_out(seg(t, T_LOOK_L, T_LOOK_L + 0.15)) * (1 - ease_in_out(seg(t, T_LOOK_R, T_LOOK_R + 0.15)))
            kr = ease_in_out(seg(t, T_LOOK_R, T_LOOK_R + 0.15)) * (1 - ease_in_out(seg(t, T_LOOK_END - 0.1, T_LOOK_END)))
            s["tilt"] = 10 * kl - 10 * kr
            s["look"] = (-11, 2) if kl > 0.5 else (11, 2) if kr > 0.5 else (0, 0)
            s["eyes"] = "wide"
            s["mouth"] = "w"
        if t >= T_LOOK_END:
            s["head_dy"] = 12 * math.sin(math.pi * seg(t, T_LOOK_END, T_LOOK_END + 0.25))
    elif t < T_LET_GO + 0.35:         # CROSS holding hands
        bob, sway = walk_bob(t, T_CROSS0, T_CROSS1, 8)
        s.update(y=cross_y(t), hop=bob, lean=sway, arm_l=SN_HOLD, eyes="happy", mouth="grin")
        if t >= T_LET_GO:
            s["arm_l"] = lerp(SN_HOLD, -14, ease_in_out(seg(t, T_LET_GO, T_LET_GO + 0.3)))
    elif t < 14.3:                    # BALL! hug it
        p = ease_in_out(seg(t, 13.0, 13.3))
        h, sq = hop_curve(t, 13.0, 13.3, 1, 26)
        s.update(y=NEAR_Y, x=lerp(SN_X, 470, p), hop=h, sq=sq, eyes="sparkle" if t < 13.3 else "happy",
                 mouth="grin", look=(6, 4))
        if t >= T_BALL:
            k = ease_out(seg(t, T_BALL, T_BALL + 0.2))
            s["arm_l"], s["arm_r"] = lerp(-14, 44, k), lerp(14, -44, k)
            s["hug"] = True
        e = spring(t, 13.3, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
        if 13.6 <= t:
            s["tilt"] = 6 * math.sin(2 * math.pi * 1.4 * (t - 13.6))
    elif t < 16.1:                    # PAW-BUMP (the ball sits by Snip's feet)
        h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
        s.update(y=NEAR_Y, x=lerp(470, 482, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq, eyes="happy",
                 mouth="grin")
        s["arm_l"] = lerp(44, -14, ease_in_out(seg(t, 14.3, 14.55)))
        s["arm_r"] = lerp(-44, 14, ease_in_out(seg(t, 14.3, 14.55)))
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_r"] = lerp(lerp(s["arm_r"], -6, wind), 165, swing)
        e = spring(t, 15.45, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
    else:                             # wave at the camera as the heart closes
        s.update(y=NEAR_Y, x=482, eyes="happy", mouth="grin")
        s["arm_r"] = lerp(165, 150 + 20 * math.sin((t - 16.1) * 16), ease_out(seg(t, 16.1, 16.3)))

    s["ears"][0] += idle_ear
    s["ears"][1] -= idle_ear
    if s["hop"] == 0:
        s["sq"] *= breath(t)
    return s


# ---------------------------------------------------------------- Crinkle
def crinkle_state(t):
    if frozen(t):
        return crinkle_state(2.4999)
    s = dict(x=CR_X, y=WAIT_Y, hop=0.0, sq=1.0, lean=0.0, arm_l=CR_REST_L, arm_r=2.0, eyes="normal",
             mouth="smile", look=(0, 0), head_dy=0.0)
    if t < 6.0 or t >= T_RESET:
        s["x"] = 1600
        return s
    if t < 6.6:                       # walks in holding a grown-up's hand
        bob, sway = walk_bob(t, 6.0, 6.6, 4)
        s.update(x=lerp(1350, CR_X, ease_out(seg(t, 6.0, 6.6))), hop=bob, lean=sway, arm_r=CR_HOLD,
                 eyes="normal", mouth="smile", look=(-8, -2))
    elif t < T_CROSS0:                # shows the red standing figure (points with his free arm), waits, counts
        s.update(arm_r=CR_HOLD, look=(-10, -8), eyes="normal", mouth="smile")
        point = ease_out_back(seg(t, 6.6, 6.85)) * (1 - ease_in_out(seg(t, 7.6, 7.9)))
        s["arm_l"] = lerp(CR_REST_L, 250, point)
        s["head_dy"] = 10 * math.sin(math.pi * seg(t, 6.9, 7.2))
        for c in COUNTS:
            s["head_dy"] += 10 * math.sin(math.pi * seg(t, c, c + 0.3))
            if 0 <= t - c < 0.3:
                s["mouth"] = "o"
        if t >= T_GREEN:
            s.update(eyes="happy", mouth="grin", look=(-8, -6))
        if T_LOOK_L <= t < T_LOOK_END:
            s["look"] = (-11, 2) if t < T_LOOK_R + 0.08 else (11, 2)
            s["eyes"] = "normal"
            s["mouth"] = "smile"
    elif t < T_LET_GO + 0.35:         # cross
        bob, sway = walk_bob(t, T_CROSS0, T_CROSS1, 8)
        s.update(y=cross_y(t), hop=bob, lean=-sway, arm_r=CR_HOLD, eyes="happy", mouth="grin", look=(-4, 4))
        if t >= T_LET_GO:
            s["arm_r"] = lerp(CR_HOLD, 2, ease_in_out(seg(t, T_LET_GO, T_LET_GO + 0.3)))
    elif t < 14.3:                    # cheers for Snip
        h, sq = hop_curve(t, 13.35, 13.67, 1, 24)
        s.update(y=NEAR_Y, hop=h, sq=sq, eyes="happy", mouth="grin", look=(-6, 2))
        s["arm_r"] = lerp(2, 150, ease_out_back(seg(t, 13.3, 13.5))) * (1 - ease_in_out(seg(t, 14.0, 14.3)))
    elif t < 16.1:                    # PAW-BUMP
        h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
        s.update(y=NEAR_Y, x=lerp(CR_X, 780, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq, eyes="happy",
                 mouth="grin")
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_l"] = lerp(lerp(CR_REST_L, 360, wind), 198, swing)
    else:
        s.update(y=NEAR_Y, x=780, eyes="happy", mouth="grin", arm_l=198)
        s["arm_r"] = 140 + 22 * math.sin((t - 16.1) * 16)
    if s["hop"] == 0:
        s["sq"] *= breath(t + 0.7, 2.25, 0.01)
    return s


# ---------------------------------------------------------------- cars, light, ball
def cars(t):
    """List of (sprite, scene_x_of_front_bumper, ground_y)."""
    if frozen(t):
        t = 2.4999
    out = []
    if 1.2 <= t < 2.5:                # car A drives past (top lane, right -> left), well away from Snip
        out.append((CAR_A, lerp(1500, -520, seg(t, 1.2, 2.45)), TOP_LANE_Y))
    if 8.0 <= t < T_IRIS1:            # car B rolls in from the left and stops at its stop line
        x = lerp(-560, P.STOP_LEFT - 14, ease_out(seg(t, 8.0, 9.5)))
        x = lerp(x, 1700, ease_in_out(seg(t, 14.4, 16.4)) ** 1.6)
        out.append((CAR_B, x, BOT_LANE_Y))
    if 8.3 <= t < T_IRIS1:            # car C rolls in from the right and stops at its stop line
        x = lerp(1700, P.STOP_RIGHT + 14, ease_out(seg(t, 8.3, 9.8)))
        x = lerp(x, -700, ease_in_out(seg(t, 14.6, 16.5)) ** 1.6)
        out.append((CAR_C, x, TOP_LANE_Y))
    return out


def light_green(t):
    return T_GREEN <= t < T_RESET


def ball_pos(t, sn):
    if T_BALL <= t < 14.3:
        hp = SNIP.head_pivot(sn["x"] + X0, sn["y"], sn["hop"], sn["lean"], sn["sq"])
        k = ease_out(seg(t, T_BALL, T_BALL + 0.2))
        return (lerp(BALL_AT[0] + X0, hp[0], k), lerp(BALL_AT[1], hp[1] + 120, k)), True
    if 14.3 <= t < T_RESET:
        k = ease_in_out(seg(t, 14.3, 14.55))
        hp = SNIP.head_pivot(sn["x"] + X0, sn["y"])
        return (lerp(hp[0], X0 + 330, k), lerp(hp[1] + 120, NEAR_Y + 4, k) - 60 * math.sin(math.pi * k)), False
    bounce = abs(math.sin(2 * math.pi * t / 1.0)) * 10 if not frozen(t) and t < 2.5 else 0.0
    return (BALL_AT[0] + X0, BALL_AT[1] - bounce), False


def hand_sn(t, sn):
    """Fingertip position of the grown-up's hand for Snip (canvas), or None."""
    if t < T_HAND_SN0 or t >= T_LET_GO + 0.6:
        return None
    tp = tip(SNIP, sn, "l")
    hold = (tp[0] - 4, tp[1] + 16)
    if t < T_HAND_SN1:
        k = ease_out(seg(t, T_HAND_SN0, T_HAND_SN1))
        return (hold[0], lerp(-200, hold[1], k))
    if t >= T_LET_GO:
        k = ease_in_out(seg(t, T_LET_GO, T_LET_GO + 0.6))
        return (hold[0], lerp(hold[1], -300, k))
    return hold


def hand_cr(t, cr):
    if t < 6.0 or t >= T_LET_GO + 0.6 or cr["x"] > 1500:
        return None
    tp = tip(CR, cr, "r")
    hold = (tp[0] + 4, tp[1] + 16)
    if t >= T_LET_GO:
        k = ease_in_out(seg(t, T_LET_GO, T_LET_GO + 0.6))
        return (hold[0], lerp(hold[1], -300, k))
    return hold


# ---------------------------------------------------------------- frame
def draw_char(f, ch, st, t, blink_times, frz):
    kw = dict(hop=st["hop"], lean=st["lean"], arm_l=st["arm_l"], arm_r=st["arm_r"], eyes=st["eyes"],
              mouth=st["mouth"], look=st["look"], squash=st["sq"], head_dy=st["head_dy"],
              blink=blinking(t, blink_times) and not frz)
    if ch is SNIP:
        kw.update(head_tilt=st["tilt"], ears=tuple(st["ears"]), ear_stretch=st["ear_stretch"], frizz=st["frizz"])
    ch.draw(f, st["x"] + X0, st["y"], **kw)


def render_frame(t):
    f = BG.copy()
    sn = snip_state(t)
    cr = crinkle_state(t)
    frz = frozen(t)

    # pedestrian light (lit lamp + soft glow)
    if light_green(t):
        place(f, LIGHT_GREEN[int(t * 3) % 2], C(P.LIGHT_X, P.LIGHT_Y))
        place(f, GLOW_GREEN, C(*LAMP_GREEN), alpha=0.55 + 0.15 * math.sin(t * 8), shadow=False)
    else:
        place(f, LIGHT_RED, C(P.LIGHT_X, P.LIGHT_Y))
        pulse = 0.5 + 0.2 * math.sin(t * 8) if not frz else 0.5
        if 6.6 <= t < 7.5 or T_SKID <= t < 6.0:         # extra-bright when it matters
            pulse = 0.85 + 0.15 * math.sin(t * 14)
        place(f, GLOW_RED, C(*LAMP_RED), alpha=pulse, shadow=False)

    # depth-sorted: characters, cars and the ball by their ground line
    items = []
    for spr, x, gy in cars(t):
        items.append((gy, "car", (spr, x, gy)))
    if cr["x"] < 1500:
        items.append((cr["y"], "cr", None))
    items.append((sn["y"] + 0.1, "sn", None))
    bp, held = ball_pos(t, sn)
    if not held:
        items.append((bp[1] + 40, "ball", bp))
    for _, kind, data in sorted(items, key=lambda it: it[0]):
        if kind == "car":
            spr, x, gy = data
            place(f, spr, C(x, gy))
        elif kind == "cr":
            draw_char(f, CR, cr, t, CR_BLINKS, frz)
        elif kind == "sn":
            if sn["whirl"] > 0.01:                       # wind-up legs under Snip
                place(f, WHIRL[int(t * 30) % len(WHIRL)], C(sn["x"], sn["y"] - sn["hop"] + 6), scale=sn["whirl"])
            draw_char(f, SNIP, sn, t, SNIP_BLINKS, frz)
        else:
            place(f, BALL, data, angle=0 if t < 14.3 else -360 * ease_in_out(seg(t, 14.3, 14.55)))

    # hugging the ball: ball in front, paws redrawn over it
    if held:
        place(f, BALL, bp, scale=1.1)
        for side in ("l", "r"):
            spr = SNIP.arm_l if side == "l" else SNIP.arm_r
            place(f, spr, SNIP.shoulder_pt(sn["x"] + X0, sn["y"], side, sn["hop"], sn["lean"], sn["sq"]),
                  angle=(sn["arm_l"] if side == "l" else sn["arm_r"]) + sn["lean"])

    # speed lines, dust and skid
    if T_WIND <= t < T_SKID:
        place(f, SPEED, C(sn["x"] - 110, sn["y"] - 210), angle=90, scale=0.8, alpha=0.9)
    if T_SKID - 0.02 <= t < T_SKID + 0.6:
        k = seg(t, T_SKID - 0.02, T_SKID + 0.6)
        for dx in (-90, 90):
            place(f, DUST, C(sn["x"] + dx * (1 + 0.4 * k), EDGE_Y - 10), scale=0.6 + 0.5 * k, alpha=1 - k)

    # the grown-up's hands (in front of everything): holding paws
    h = hand_cr(t, cr)
    if h is not None:
        place(f, HAND_CR, h)
    h = hand_sn(t, sn)
    if h is not None:
        place(f, HAND_SN, h)

    # desire: the ball glints
    for t0, dx, dy, sc in ((1.05, 34, -40, 0.9), (1.5, -30, 6, 0.7), (2.0, 22, 30, 0.6)):
        if t0 <= t < t0 + 0.5:
            k = math.sin(math.pi * seg(t, t0, t0 + 0.5))
            place(f, GLINT, C(BALL_AT[0] + dx, BALL_AT[1] + dy), scale=sc * k, angle=(t - t0) * 120)

    # counting numerals, then a check when the walking figure lights up
    for i, c in enumerate(COUNTS):
        if c <= t < c + 0.55:
            out = 1 - ease_in_out(seg(t, c + 0.4, c + 0.55))
            place(f, NUMS[i], C(560, 560), scale=pop_scale(t, c, 0.25) * out, angle=-6 + 4 * math.sin(t * 6))
    if T_GREEN <= t < T_GREEN + 0.8:
        place(f, CHECK, C(P.LIGHT_X + 150, P.LIGHT_Y + 30),
              scale=pop_scale(t, T_GREEN, 0.25) * (1 - ease_in_out(seg(t, T_GREEN + 0.6, T_GREEN + 0.8))))
    if 13.0 <= t < 13.6:
        place(f, CHECK, C(560, 760), scale=pop_scale(t, 13.0, 0.25) * (1 - ease_in_out(seg(t, 13.4, 13.6))))

    for i, (t0, x, y) in enumerate(HEART_PLAN):
        if t0 <= t < 14.6:
            p = seg(t, t0, 14.6)
            place(f, HEARTS[i], C(x + 10 * math.sin(t * 3 + i), y - 160 * p), scale=pop_scale(t, t0, 0.25),
                  alpha=1 - ease_in_out(seg(t, 14.2, 14.6)), angle=10 * math.sin(t * 2.5 + i))

    # paw-bump: both touching paws in front, sparkle
    if 14.95 <= t < 16.1:
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"] + X0, sn["y"], "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])
        place(f, CR.arm_l, CR.shoulder_pt(cr["x"] + X0, cr["y"], "l", cr["hop"], cr["lean"], cr["sq"]),
              angle=cr["arm_l"] + cr["lean"])
    if 15.45 <= t < 16.2:
        a, b = tip(SNIP, sn, "r"), tip(CR, cr, "l")
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 10)
        place(f, SPARKLE, (mid[0], mid[1] - 35), scale=pop_scale(t, 15.45, 0.22) * 0.55, angle=(t - 15.45) * 60,
              alpha=1 - ease_in_out(seg(t, 15.9, 16.2)))

    out = camera(f, t)

    # FREEZE: dim + choice bubbles (screen space)
    if 2.5 <= t < 4.6:
        dim = 0.32 * ease_in_out(seg(t, 2.5, 2.8)) * (1 - ease_in_out(seg(t, 4.35, 4.6)))
        if dim > 0.01:
            out.alpha_composite(Image.new("RGBA", out.size, (30, 26, 52, int(255 * dim))))
        gone = 1 - ease_in_out(seg(t, 4.4, 4.55))
        pulse_a = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 2.95) / 1.0))
        pulse_b = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 3.45) / 1.0))
        place(out, BUB_RUN, (290, 560), scale=1.15 * pop_scale(t, 2.55) * gone * (pulse_a if t > 2.95 else 1))
        place(out, BUB_HOLD, (790, 560), scale=1.15 * pop_scale(t, 2.7) * gone * (pulse_b if t > 3.45 else 1))
        place(out, QMARK, (540, 440), scale=pop_scale(t, 2.85, 0.25) * gone, angle=8 * math.sin(t * 4))

    # heart iris back to the start (loop)
    if T_IRIS0 <= t < T_OPEN1:
        if t < T_IRIS1:
            size = lerp(4300, 0, ease_in_out(seg(t, T_IRIS0, T_IRIS1)) ** 0.7)
            ctr = (560, 860)
        elif t < T_RESET + 0.06:
            size, ctr = 0, IRIS_OPEN_AT
        else:
            size = lerp(0, 4300, ease_in_out(seg(t, T_RESET + 0.06, T_OPEN1)) ** 1.6)
            ctr = IRIS_OPEN_AT
        out = IRIS.apply(out, ctr, size)
    return out


CAM0 = (1.4, 480, 950)
def _iris_open_at():
    z, cx, cy = CAM0
    hp = SNIP.head_pivot(SN_X, WAIT_Y)
    face_y = hp[1] - 110 * 1.15
    return ((SN_X - (cx - scene.W / z / 2)) * z, (face_y - (cy - scene.H / z / 2)) * z)


CAM_KEYS = [
    (0.0,) + CAM0, (1.0, 1.42, 480, 950), (1.6, 1.12, 540, 1060), (2.4, 1.12, 540, 1120),
    (2.8, 1.0, 540, 960), (4.5, 1.0, 540, 960), (4.75, 1.3, 460, 1150), (5.75, 1.3, 460, 1150),
    (6.1, 1.0, 560, 960), (6.6, 1.0, 560, 960), (6.95, 1.6, 230, 800), (7.3, 1.6, 230, 800),
    (7.7, 1.0, 540, 960), (T_LOOK_L, 1.0, 540, 960), (T_LOOK_L + 0.25, 1.0, 380, 960),
    (T_LOOK_R, 1.0, 380, 960), (T_LOOK_R + 0.25, 1.0, 700, 960), (T_LOOK_END, 1.0, 700, 960),
    (T_CROSS0 + 0.2, 1.0, 560, 960), (12.9, 1.0, 560, 960), (13.2, 1.12, 580, 1150), (14.4, 1.12, 580, 1150),
    (14.7, 1.0, 600, 960), (15.2, 1.0, 600, 960), (15.45, 1.12, 620, 1180), (16.3, 1.12, 620, 1180),
    (T_IRIS1, 1.0, 600, 960), (T_RESET, 1.0, 600, 960), (T_RESET + 0.01,) + CAM0, (DUR,) + CAM0]

IRIS_OPEN_AT = _iris_open_at()


def camera(f, t):
    z, cx, cy = 1.0, 540, 960
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
    if T_SKID <= t < T_SKID + 0.3:    # little skid shake
        k = math.sin(math.pi * seg(t, T_SKID, T_SKID + 0.3))
        cx += 6 * k * math.sin(t * 95)
        cy += 5 * k * math.cos(t * 81)
    w, h = scene.W / z, scene.H / z
    left = min(max(cx + X0 - w / 2, 0), P.WORLD_W - w)
    top = min(max(cy - h / 2, 0), scene.H - h)
    return f.resize((scene.W, scene.H), Image.BICUBIC, box=(left, top, left + w, top + h))


# ---------------------------------------------------------------- audio
def build_audio(path):
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    M = A.midi
    # hook + desire; a car putts past
    A.jingle(music, 0.02)
    for tt, ch, up in ((1.0, "C", False), (1.25, "C", True), (1.5, "G", False), (1.75, "G", True),
                       (2.0, "Am", False), (2.25, "F", True)):
        A.strum(music, tt, ch, 0.7, up)
    for tt, m in ((1.0, 48), (1.5, 43), (2.0, 45), (2.25, 41)):
        music.add(tt, A.bass(M(m), 0.5, 0.7))
    sfx.add(0.3, P.chirp(0.6))
    sfx.add(1.05, A.twinkle(0.7))
    sfx.add(1.2, P.putt(1.25, 0.8))
    sfx.add(1.5, A.whoosh(0.7, 0.7))
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
    # wind-up, dash, skid, teeter, phew
    sfx.add(T_WIND, P.windup(T_DASH - T_WIND + 0.05, 0.9))
    sfx.add(T_DASH, A.whoosh(0.2, 0.9))
    sfx.add(T_SKID - 0.04, P.squeak(1.0))
    sfx.add(T_SKID + 0.08, P.slide_whistle(1200, 700, 0.45, 0.6, wobble=0.06, wob_rate=9))
    sfx.add(T_SKID + 0.05, A.snare_roll(0.15, 0.5))
    sfx.add(T_BACK, A.boing(0.6, 300))
    sfx.add(T_BACK + 0.32, P.phew(0.8))
    music.add(T_BACK + 0.1, A.wah_down(0.8))
    # Crinkle + the red light; the grown-up's hand comes down
    for i in range(4):
        sfx.add(6.0 + i * 0.15, A.tap(0.35))
    sfx.add(6.7, A.glock(M(91), 1.2, 0.8))
    sfx.add(6.75, A.glock(M(88), 1.2, 0.55))
    for tt, ch in ((6.6, "Am"), (7.1, "F"), (7.6, "C")):
        A.strum(music, tt, ch, 0.55)
        music.add(tt, A.bass(M({"Am": 45, "F": 41, "C": 48}[ch]), 0.5, 0.6))
    for tt in (6.95, 7.25):
        sfx.add(tt, A.tap(0.5))
    sfx.add(T_HAND_SN0, A.whoosh(0.5, 0.6))
    sfx.add(T_HAND_SN1, A.pop(0.7))
    sfx.add(T_HAND_SN1 + 0.02, A.twinkle(0.6))
    # wait: tick-tock, count 1-2-3, cars roll in and stop, GREEN chime
    sfx.add(8.0, P.putt(1.5, 0.6))
    sfx.add(8.3, P.putt(1.5, 0.5))
    tt = 8.05
    while tt < T_GREEN - 0.05:
        sfx.add(tt, P.tick(0.6, 1750 if round((tt - 8.05) / 0.325) % 2 == 0 else 1400))
        tt += 0.325
    for c, m in zip(COUNTS, (84, 88, 91)):
        sfx.add(c, A.glock(M(m), 1.2, 0.9))
        music.add(c, A.ks_pluck(M(m - 24), 1.0, 0.8))
        music.add(c, A.bass(M(48), 0.4, 0.5))
        sfx.add(c + 0.02, A.tap(0.5))
    sfx.add(T_GREEN, A.chime_up(1.0))
    sfx.add(T_GREEN + 0.05, A.twinkle(0.6))
    A.strum(music, T_GREEN, "C", 0.7)
    music.add(T_GREEN, A.bass(M(48), 0.5, 0.7))
    sfx.add(T_LOOK_L, A.whoosh(0.25, 0.5))
    sfx.add(T_LOOK_L + 0.18, A.marimba(M(72), 0.4, 0.6))
    sfx.add(T_LOOK_R, A.whoosh(0.25, 0.5))
    sfx.add(T_LOOK_R + 0.18, A.marimba(M(76), 0.4, 0.6))
    sfx.add(T_LOOK_END, A.marimba(M(79), 0.5, 0.7))
    # cross: walking plucks
    for i in range(8):
        tt = T_CROSS0 + i * (T_CROSS1 - T_CROSS0) / 8
        music.add(tt, A.pluck(M((60, 64, 67, 72, 67, 64, 65, 67)[i]), 0.3, 0.6))
        sfx.add(tt, A.tap(0.35))
    for tt, ch in ((11.0, "C"), (11.5, "F"), (12.0, "G")):
        A.strum(music, tt, ch, 0.5)
        music.add(tt, A.bass(M({"C": 48, "F": 41, "G": 43}[ch]), 0.45, 0.6))
    sfx.add(T_LET_GO, A.pop(0.5))
    sfx.add(T_LET_GO + 0.1, A.whoosh(0.5, 0.5))
    # BALL + hearts
    sfx.add(T_BALL, A.boing(0.6, 340))
    sfx.add(13.0, A.glock(M(96), 1.0, 0.7))
    sfx.add(13.02, A.twinkle(0.8))
    for tt, ch, up in ((13.0, "C", False), (13.25, "C", True), (13.5, "G", False), (13.75, "G", True),
                       (14.0, "Am", False), (14.25, "F", True), (14.5, "F", False)):
        A.strum(music, tt, ch, 0.8, up)
    for tt, m in ((13.0, 48), (13.5, 43), (14.0, 45), (14.5, 41)):
        music.add(tt, A.bass(M(m), 0.45, 0.8))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.45))
    sfx.add(13.35, A.boing(0.35, 340))
    sfx.add(14.35, A.boing(0.4, 260))
    sfx.add(14.5, P.putt(1.8, 0.45))
    # paw-bump (signature)
    sfx.add(14.85, A.snare_roll(0.6, 0.8))
    sfx.add(15.45, A.boop(0.9))
    A.jingle(music, 15.47, 1.0, ending=True)
    sfx.add(15.5, A.twinkle(0.8))
    # heart iris close + open, back to the start
    A.strum(music, 16.3, "F", 0.5)
    A.strum(music, 16.8, "G7", 0.5)
    sfx.add(T_IRIS0, P.slide_whistle(500, 1400, 0.55, 0.6))
    sfx.add(T_IRIS1, A.pop(0.7))
    sfx.add(T_RESET + 0.1, P.slide_whistle(1400, 700, 0.5, 0.5))
    sfx.add(T_RESET + 0.3, P.chirp(0.5))
    sfx.add(17.45, A.uh_oh(0.8))
    for i, m in enumerate((64, 65, 66)):
        music.add(17.55 + i * 0.13, A.pluck(M(m - 12), 0.3, 0.55))
    music.add(17.2, A.pad([M(55), M(59), M(62)], 0.8, 0.25))

    m = A.reverb(music.normalized(), 0.24)
    s = A.reverb(sfx.normalized(), 0.08)
    y = 0.55 * m / max(1e-9, abs(m).max()) + 0.7 * s / max(1e-9, abs(s).max())
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.01)


# ---------------------------------------------------------------- output
def render(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    wav = os.path.join(ROOT, "build", "ep05_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep05_hold_paws_to_cross.mp4")
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
    times = times or [0.0, 1.8, 3.4, 4.8, 5.3, 5.8, 6.4, 7.1, 7.9, 8.6, 9.6, 10.3, 10.7, 11.6,
                      12.3, 13.4, 15.6, 16.8, 17.3, 17.7, 17.99]
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


KEYS = [(0.0, "0.0s hook"), (3.4, "3.4s choice"), (5.3, "5.3s skid at the curb"), (7.1, "7.1s red = wait"),
        (9.6, "9.6s count 3, cars stop"), (10.35, "10.4s look left"), (11.8, "11.8s cross holding hands"),
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
        stills(os.path.join(ROOT, "build", "ep05_stills.png"))
    elif "--keys" in sys.argv:
        os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
        key_sheet(os.path.join(ROOT, "reviews", "ep05_keys.png"))
    else:
        render(os.path.join(ROOT, "output"))
