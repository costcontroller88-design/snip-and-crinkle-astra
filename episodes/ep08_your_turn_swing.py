"""Episode 8 -- Your Turn on the Swing? (playground)

Snip is swinging high on the only swing. Pip the duckling (from Episode 4) waddles up and waits,
sad, wishing for a turn. Choice: keep swinging, or give Pip a turn? Snip keeps swinging and
twisting... the chains twist up, then unwind and spin Snip round and round until Snip is dizzy
(spiral eyes, stars), and the swing slows to a soft stop. Crinkle shows a "take turns" sign. Snip
hops off, holds the swing steady for Pip, and gives gentle pushes from behind: 1, 2, 3. Then Pip
happily gives Snip a turn. Hearts, the signature paw-bump, and a seamless loop: Pip waddles home,
Snip hops back on and swings (frame 18.0s == frame 0).

Safety: the waiting spot is well outside the swing's path, nobody walks in front of a moving
swing, pushes are small and from behind, and every swing comes to a gentle stop before anyone
gets on or off.

Run:  python3 episodes/ep08_your_turn_swing.py            (render -> output/)
      python3 episodes/ep08_your_turn_swing.py --stills    (contact sheet -> build/)
      python3 episodes/ep08_your_turn_swing.py --keys      (8 key frames, 360px wide -> reviews/)
      python3 episodes/ep08_your_turn_swing.py --frames 5.6,10.6   (full-size frames -> build/)
"""
import math
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw  # noqa: E402

import audio as A  # noqa: E402
import icons  # noqa: E402
import props_park as PP  # noqa: E402
import props_swing as PS  # noqa: E402
import scene  # noqa: E402
from characters import BLINKABLE, Character  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, rot, seg  # noqa: E402

FPS = 30
DUR = 18.0
GY = PS.GROUND_Y
SX = PS.SWING_X
HY = PS.HOOK_Y
CDX = PS.CHAIN_DX
CL = PS.CHAIN_L
SEAT_TOP = HY + CL                    # resting seat top (1250)
SIT_DY = 40                           # seat top -> rider's base line
PIP_X = 150                           # Pip's waiting spot, well outside the swing's path
SNIP_OFF = 360                        # where Snip lands when hopping off to the left
SNIP_STAND = 470                      # Snip's spot for the paw-bump (swing stopped behind)
CR_HOME = 860                         # Crinkle while Snip is on the swing
CR_BUMP = 785                         # Crinkle for the paw-bump
CR_REST_L = 346                       # Crinkle's left arm hanging (== -14)
HOOK_AMP = 9.5                        # degrees: Snip's happy swinging (stays clear of Pip's spot)
HOOK_P = 1.5                          # swing period in the hook (18 / 1.5 = 12 whole swings)
PUSH_P = 1.0                          # swing period while Pip swings
PUSHES = (9.5, 10.5, 11.5)            # gentle pushes, counted 1-2-3
PUSH_AMP = (4.0, 5.5, 7.0, 8.0)       # amplitude before push 1, after push 1, 2, 3
PUSH_XS = (219, 197, 174, 159)        # Snip steps back a little as the swing goes higher

BG = PS.background()
CLOUDS = [(PS.cloud(300, 130), 260, 250, 0.0), (PS.cloud(240, 110), 840, 170, 2.1), (PS.cloud(200, 90), 620, 640, 4.0)]
SEAT = PS.seat()
SNIP_FEET = PS.snip_feet()
PIP_FEET = PS.pip_feet()
SIGN = PS.sign_turns()
THOUGHT = PS.thought_swing()
SPIRAL = PS.spiral_eye()
STARS = [PS.dizzy_star(c) for c in ((255, 214, 64), (255, 160, 190), (140, 210, 255))]
SWIRL = PS.swirl_line()
BUB_KEEP = PS.choice_bubble_swing("keep", (240, 110, 100))
BUB_GIVE = PS.choice_bubble_swing("give", (90, 190, 120))
QMARK = icons.question()
CHECK = icons.check(130)
SPARKLE = scene.sparkle()
NUMS = [scene.numeral(1, (244, 112, 104)), scene.numeral(2, (255, 196, 52)), scene.numeral(3, (84, 182, 222))]
HEARTS = [scene.heart(c, 80) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120), (255, 150, 170),
                                       (240, 72, 98), (255, 120, 150))]
SNIP = Character("snip", 1.15)
CR = Character("crinkle", 1.2)
PIP = PP.Duckling(0.9)

SNIP_BLINKS = (1.6, 4.62, 7.75, 9.9, 12.2, 14.2, 16.2)
CR_BLINKS = (7.2, 8.1, 14.6, 15.9)
PIP_BLINKS = (2.25, 5.1, 7.4, 9.7, 11.1, 14.3, 15.0)
HEART_PLAN = ((11.75, 640, 760), (11.95, 470, 700), (13.95, 330, 900), (14.1, 760, 800), (14.25, 160, 1000),
              (14.35, 600, 690))


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


def ease_in(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * t


def near(a, ref):
    """Same direction as angle a, unwrapped to be closest to ref (so limbs never swing the long way)."""
    return a + 360 * round((ref - a) / 360)


def aim_from(sh, target, lean, ref):
    a = math.degrees(math.atan2(target[0] - sh[0], target[1] - sh[1])) - lean
    return near(a, ref)


def arc_hop(t, t0, t1, p0, p1, height):
    """Position along a hop from p0 to p1 (each (x, base_y)), plus squash. Returns x, base_y, sq."""
    k = ease_in_out(seg(t, t0, t1))
    h, sq = hop_curve(t, t0, t1, 1, height)
    return lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k) - h, sq


# ---------------------------------------------------------------- the swing
def swing_state(t):
    """theta: pendulum angle (deg, + = to the right); spin: rider's turn about the chains (deg);
    twist: how wound-up the chains are (0..1)."""
    if frozen(t):
        return swing_state(2.4999)
    th, spin = 0.0, 0.0
    if t < 2.5:
        th = HOOK_AMP * math.cos(2 * math.pi * t / HOOK_P)
    elif t < 5.3:                     # keeps swinging... slowing as Snip twists round and round
        tau = t - 2.0
        th = HOOK_AMP * (1 - ease_in_out(seg(t, 4.55, 5.3))) * math.cos(2 * math.pi * tau / HOOK_P)
        spin = -540 * ease_in_out(seg(t, 4.6, 5.3))
    elif t < 5.6:                     # all wound up
        spin = -540
    elif t < 6.7:                     # WHIRR: unwinds, spinning Snip round 2.5 times
        spin = -540 + 900 * ease_in_out(seg(t, 5.6, 6.7))
    elif t < 7.4:                     # wobbles to a soft stop
        spin = 360 + 22 * math.exp(-5.5 * (t - 6.7)) * math.sin(2 * math.pi * 2.2 * (t - 6.7))
    elif t < 9.15:                    # still; little jiggles as Snip hops off and Pip hops on
        th = spring(t, 8.05, 1.2, 1.6, 3.0) + spring(t, 9.0, 1.4, 1.4, 3.0)
    elif t < PUSHES[0]:               # Snip gently draws the seat back
        th = -PUSH_AMP[0] * ease_in_out(seg(t, 9.15, PUSHES[0])) + spring(t, 9.0, 1.4, 1.4, 3.0)
    elif t < 12.5:                    # gentle pushes 1-2-3, each at the back of the swing
        a = PUSH_AMP[0]
        for i, c in enumerate(PUSHES):
            a += (PUSH_AMP[i + 1] - PUSH_AMP[i]) * ease_in_out(seg(t, c, c + 0.3))
        th = -a * math.cos(2 * math.pi * (t - PUSHES[0]) / PUSH_P)
    elif t < 13.0:                    # Snip catches the seat and brings it softly to a stop
        th = -PUSH_AMP[3] * (1 - ease_in_out(seg(t, 12.5, 12.95)))
    elif t < 13.8:                    # Pip hops off, Snip hops on
        th = spring(t, 13.1, 1.0, 1.6, 3.0) + spring(t, 13.72, 1.3, 1.5, 3.0)
    elif t < 14.45:                   # a little happy sway, then still
        th = 2.2 * math.sin(math.pi * seg(t, 13.8, 14.45)) * math.sin(2 * math.pi * (t - 13.8) / 0.65) \
            + spring(t, 13.72, 1.3, 1.5, 3.0)
    elif t < 16.9:
        th = spring(t, 14.6, 1.0, 1.6, 3.0) + spring(t, 16.75, 1.0, 1.6, 3.0)
    else:                             # off again (== the hook)
        th = HOOK_AMP * ease_in_out(seg(t, 16.9, 18.0)) * math.cos(2 * math.pi * t / HOOK_P) \
            + spring(t, 16.75, 1.0, 1.6, 3.0)
    twist = max(0.0, -spin) / 540
    return dict(theta=th, spin=spin, twist=twist)


def theta_vel(t):
    if frozen(t):
        return 0.0
    return (swing_state(t + 0.02)["theta"] - swing_state(t - 0.02)["theta"]) / 0.04


def seat_pt(sw):
    """Centre of the seat top."""
    th = math.radians(sw["theta"])
    L = CL - 70 * sw["twist"]
    return SX + CL * math.sin(th), HY + L * math.cos(th) + CL * (1 - math.cos(th)) * 0.0


def chain_strands(sw):
    th = math.radians(sw["theta"])
    d = (math.sin(th), math.cos(th))
    n = (math.cos(th), -math.sin(th))
    sx_, sy_ = seat_pt(sw)
    sc = math.cos(math.radians(sw["spin"]))
    b = sw["twist"]
    pinch = min(1.0, b * 2.5)
    strands = []
    for i in (-1, 1):
        hook = (SX + i * CDX, HY)
        end = (sx_ + i * CDX * sc, sy_ + 6)
        if b <= 0.001:
            strands.append([hook, end])
            continue
        P0 = (SX, HY)
        u_p = 70.0
        u_b = u_p + 260 * b
        g = lerp(CDX, 12, pinch)
        pts = [hook]
        ph = math.radians(sw["spin"]) * 0.5
        nb = 2.5 * b
        for k in range(0, 21):
            u = lerp(u_p, u_b, k / 20)
            v = i * g * math.cos(2 * math.pi * nb * k / 20 + ph)
            pts.append((P0[0] + d[0] * u + n[0] * v, P0[1] + d[1] * u + n[1] * v))
        pts.append(end)
        strands.append(pts)
    return strands


# ---------------------------------------------------------------- Snip
def snip_state(t):
    """mode: 'seat' (riding), 'stand' (on the ground), 'hop' (between seat and ground)."""
    s = dict(mode="seat", x=SX, base=SEAT_TOP + SIT_DY, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, arm_l=-14.0,
             arm_r=14.0, eyes="normal", mouth="w", look=(0, 0), head_dy=0.0, ears=[0.0, 0.0], ear_stretch=1.0,
             dizzy=0.0, grip=True, push=False, steady=False)
    if frozen(t):
        return snip_state(2.4999)
    idle_ear = 2.0 * math.sin(2 * math.pi * t / 3.0)

    if t < 2.5:                       # HOOK + DESIRE: swinging high, eyes shining... not noticing Pip
        v = theta_vel(t)
        s.update(eyes="sparkle" if t < 1.05 else "happy", mouth="grin" if v * (1 if t < 1.0 else 1) > -999 else "w",
                 look=(4, -4))
        s["ears"] = [-0.9 * v, -0.9 * v]
        s["lean"] = 0.25 * swing_state(t)["theta"]
    elif t < 5.6:                     # twisting round and round... all wound up... uh-oh
        sw = swing_state(t)
        s["lean"] = 0.25 * sw["theta"]
        if t < 5.3:
            s.update(eyes="happy", mouth="grin")
            v = theta_vel(t)
            s["ears"] = [-0.9 * v, -0.9 * v]
        else:
            s.update(eyes="wide", mouth="o", look=(0, -9))
            e = spring(t, 5.3, 8, 5.0, 4.0)
            s["ears"] = [e, -e]
            s["head_dy"] = -6 * math.sin(math.pi * seg(t, 5.3, 5.45))
    elif t < 6.7:                     # WHIRR -- spinning
        sp = math.sin(math.pi * seg(t, 5.6, 6.7))
        s.update(eyes="wide", mouth="O", ears=[-30 * sp, 30 * sp], ear_stretch=1 + 0.12 * sp)
    elif t < 7.65:                    # dizzy: spiral eyes, wobbly head
        s["dizzy"] = 1 - ease_in_out(seg(t, 7.35, 7.6))
        w = 2 * math.pi * (t - 6.7) / 0.7
        s.update(eyes="normal", mouth="wobble", tilt=9 * math.sin(w), lean=3 * math.sin(w + 1.2),
                 head_dy=5 * math.cos(w))
        droop = 22 * ease_out(seg(t, 6.7, 6.95))
        s["ears"] = [droop + 10 * math.sin(w), -droop + 10 * math.sin(w)]
        if t > 7.35:                  # shakes it off
            k = seg(t, 7.35, 7.65)
            s["tilt"] = 10 * math.sin(2 * math.pi * 2 * k) * (1 - k)
            s["lean"] = 0.0
            s["head_dy"] = 0.0
            s["ears"] = [lerp(droop, 0, k), lerp(-droop, 0, k)]
            s.update(eyes="closed", mouth="w")
    elif t < 7.95:                    # sees the sign... oh! nods, looks at Pip
        s.update(eyes="normal", mouth="o" if t < 7.75 else "smile", look=(7, -6) if t < 7.75 else (-8, 3))
        s["head_dy"] = 12 * math.sin(math.pi * seg(t, 7.72, 7.92))
    elif t < 8.3:                     # hops off to the left
        x, base, sq = arc_hop(t, 7.95, 8.3, (SX, SEAT_TOP + SIT_DY), (SNIP_OFF, GY), 70)
        s.update(mode="hop" if t < 8.3 else "stand", x=x, base=base, sq=sq, grip=False, eyes="normal",
                 mouth="smile", look=(-7, 2), arm_l=-40, arm_r=40)
    elif t < 9.0:                     # "your turn!" -- points at the swing, then holds it steady for Pip
        s.update(mode="stand", x=SNIP_OFF, base=GY, grip=False, look=(-8, 2), mouth="smile")
        if t < 8.6:
            up = ease_out_back(seg(t, 8.3, 8.48))
            s["arm_r"] = lerp(14, 100 + 6 * math.sin(2 * math.pi * (t - 8.3) / 0.3), up)
            s["look"] = (-8, 2) if t < 8.42 else (7, 0)
        else:
            s.update(steady=True, look=(6, 0))
            s["lean"] = -6 * ease_in_out(seg(t, 8.6, 8.8))
        e = spring(t, 8.3, 8, 5.0, 4.0)
        s["ears"] = [e, -e]
    elif t < 12.95:                   # behind the swing: gentle pushes, 1-2-3
        s.update(mode="stand", base=GY, grip=False, push=True, look=(7, 1), mouth="smile")
        s["x"] = lerp(SNIP_OFF, PUSH_XS[0], ease_in_out(seg(t, 9.0, 9.3)))
        h, sq = hop_curve(t, 9.0, 9.3, 1, 14)
        s["hop"], s["sq"] = h, sq
        for i, c in enumerate(PUSHES):
            s["x"] += (PUSH_XS[i + 1] - PUSH_XS[i]) * ease_in_out(seg(t, c + 0.3, c + 0.6))
            h, sq = hop_curve(t, c + 0.3, c + 0.6, 1, 10)
            if h or sq != 1.0:
                s["hop"], s["sq"] = h, sq
        for i, c in enumerate(PUSHES):
            k = math.sin(math.pi * seg(t, c - 0.08, c + 0.32))
            s["lean"] -= 9 * k
            if 0 <= t - c < 0.3:
                s["mouth"] = "o"
            s["head_dy"] += 8 * math.sin(math.pi * seg(t, c, c + 0.28))
            e = spring(t, c, 7, 5.0, 5.0)
            s["ears"][0] += e
            s["ears"][1] -= e
        if t > 11.75:
            s.update(eyes="happy", mouth="grin")
        if t > 12.5:                  # catches and steadies the seat, softly
            s["x"] = lerp(PUSH_XS[3], 250, ease_in_out(seg(t, 12.5, 12.95)))
            s.update(eyes="normal", mouth="smile")
    elif t < 13.45:                   # steps back to make room, watches Pip hop off
        s.update(mode="stand", base=GY, grip=False, look=(7, 2), mouth="smile")
        s["x"] = lerp(250, 160, ease_in_out(seg(t, 12.95, 13.2)))
        if t > 13.3:                  # Pip says "your turn!" -- sparkle
            s.update(eyes="sparkle", mouth="grin")
            e = spring(t, 13.3, 10, 5.0, 4.0)
            s["ears"] = [e, -e]
    elif t < 13.8:                    # hops onto the swing
        x, base, sq = arc_hop(t, 13.45, 13.8, (160, GY), (SX, SEAT_TOP + SIT_DY), 110)
        s.update(mode="hop", x=x, base=base, sq=sq, grip=False, eyes="sparkle", mouth="grin", arm_l=-50, arm_r=50)
    elif t < 14.55:                   # PAYOFF: a happy little sway, both laughing
        s.update(eyes="happy", mouth="grin")
        e = spring(t, 13.8, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
        s["head_dy"] = 6 * math.sin(2 * math.pi * (t - 13.8) / 0.3) * (1 - seg(t, 13.9, 14.5))
    elif t < 14.9:                    # hops off in front of the stopped swing
        x, base, sq = arc_hop(t, 14.55, 14.9, (SX, SEAT_TOP + SIT_DY), (SNIP_STAND, GY), 60)
        s.update(mode="hop", x=x, base=base, sq=sq, grip=False, eyes="happy", mouth="grin", arm_l=-40, arm_r=40)
    elif t < 16.0:                    # PAW-BUMP
        s.update(mode="stand", x=SNIP_STAND, base=GY, grip=False, eyes="happy", mouth="grin", look=(6, -2))
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_r"] = lerp(lerp(14, -6, wind), 165, swing)
        e = spring(t, 15.45, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
        h, sq = hop_curve(t, 14.9, 15.04, 1, 0)
        s["sq"] = sq
    elif t < 16.45:                   # waves bye
        s.update(mode="stand", x=SNIP_STAND, base=GY, grip=False, eyes="happy", mouth="grin", look=(7, -1))
        s["arm_r"] = lerp(165, 120 + 22 * math.sin((t - 16.0) * 16), ease_out(seg(t, 16.0, 16.15)))
    elif t < 16.8:                    # hops back onto the swing
        x, base, sq = arc_hop(t, 16.45, 16.8, (SNIP_STAND, GY), (SX, SEAT_TOP + SIT_DY), 90)
        s.update(mode="hop", x=x, base=base, sq=sq, grip=False, eyes="happy", mouth="grin", arm_l=-40,
                 arm_r=lerp(120, 40, ease_out(seg(t, 16.45, 16.6))))
    else:                             # and off again! (== frame 0)
        k = ease_in_out(seg(t, 16.95, 17.6))
        v = theta_vel(t)
        s.update(eyes="sparkle" if t > 17.3 else "happy", mouth="grin", look=(4, -4) if t > 17.3 else (0, 0))
        s["ears"] = [-0.9 * v * k, -0.9 * v * k]
        s["lean"] = 0.25 * swing_state(t)["theta"]

    if s["mode"] == "seat":
        sw = swing_state(t)
        sx_, sy_ = seat_pt(sw)
        s["x"], s["base"] = sx_, sy_ + SIT_DY
    s["ears"][0] += idle_ear
    s["ears"][1] -= idle_ear
    if s["hop"] == 0 and s["mode"] != "hop":
        s["sq"] *= breath(t)
    return s


def snip_seat_arms(sn, sw):
    """Arm angles so Snip's paws hold the chains (in un-spun coordinates)."""
    out = []
    for side, i, ref in (("l", -1, -15), ("r", 1, 15)):
        sh = SNIP.shoulder_pt(sn["x"], sn["base"], side, sn["hop"], sn["lean"], sn["sq"])
        target = (sn["x"] + i * CDX, sh[1] + 95)
        out.append(aim_from(sh, target, sn["lean"], ref))
    return out


def pip_back_pt(pp_x, base):
    """A point on the back (left side) of Pip, where Snip's paws push."""
    return pp_x - 58, base - 112


def snip_push_arms(sn, t, sw):
    sp = seat_pt(sw)
    target = pip_back_pt(sp[0], sp[1] + SIT_DY)
    out = []
    for side, dy, ref in (("l", 18, 70), ("r", -12, 80)):
        sh = SNIP.shoulder_pt(sn["x"], sn["base"], side, sn["hop"], sn["lean"], sn["sq"])
        tg = (target[0], target[1] + dy)
        dist = math.hypot(tg[0] - sh[0], tg[1] - sh[1])
        a = aim_from(sh, tg, sn["lean"], ref)
        reach = SNIP.arm_len + 6
        if dist > reach:              # can't reach: paws stay up and ready
            a = lerp(a, ref, min(1.0, (dist - reach) / 60))
        out.append(a)
    return out


# ---------------------------------------------------------------- Pip the duckling
def pip_state(t):
    s = dict(mode="stand", x=PIP_X, base=GY, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, wl=-8.0, wr=8.0, eyes="worried",
             beak="sad", look=(0, 0), head_dy=0.0, turn=1.0, on=True)
    if frozen(t):
        return pip_state(2.4999)
    if t < 1.15 or t >= 17.3:
        s["on"] = False
        return s
    if t < 2.5:                       # waddles in, looks up at the swing, sad, waiting
        k = ease_out(seg(t, 1.15, 2.1))
        ph = (t - 1.15) / 0.36
        s.update(x=lerp(-150, PIP_X, k), lean=7 * math.sin(2 * math.pi * ph) * (1 - seg(t, 1.95, 2.2)),
                 hop=6 * abs(math.sin(math.pi * 2 * ph)) * (1 - seg(t, 1.95, 2.15)), look=(7, -4), eyes="normal",
                 beak="smile")
        if t > 2.0:
            s.update(eyes="worried", beak="sad", look=(8, -6))
            s["head_dy"] = 6 * ease_in_out(seg(t, 2.1, 2.4))
            s["wl"], s["wr"] = -4, 4
    elif t < 5.5:                     # waits... watching Snip twist round
        s.update(look=(8, -6), head_dy=6, wl=-4, wr=4)
        sw = 2 * math.pi * (t - 4.5) / 1.6
        s["lean"] = 3 * math.sin(sw)
        if t > 4.55:
            s.update(eyes="normal", beak="sad", look=(8, -7))
    elif t < 6.9:                     # oh no -- Snip is spinning!
        s.update(eyes="wide", beak="open", look=(8, -7))
        s["wl"] = lerp(-8, -40, ease_out(seg(t, 5.6, 5.8)))
        s["wr"] = lerp(8, 40, ease_out(seg(t, 5.6, 5.8)))
        s["tilt"] = 6 * math.sin(2 * math.pi * (t - 5.6) / 0.5)
    elif t < 8.3:                     # looks at Crinkle's sign... hopeful
        s.update(eyes="normal", beak="smile" if t > 7.4 else "sad", look=(8, -8))
        s["head_dy"] = -4 * ease_in_out(seg(t, 7.3, 7.6))
    elif t < 8.6:                     # Snip says "your turn!" -- yay!
        h, sq = hop_curve(t, 8.4, 8.6, 1, 22)
        s.update(eyes="sparkle", beak="grin", look=(7, -3), hop=h, sq=sq,
                 wl=lerp(-8, -45, ease_out(seg(t, 8.38, 8.5))), wr=lerp(8, 45, ease_out(seg(t, 8.38, 8.5))))
    elif t < 8.9:                     # waddles to the swing
        k = ease_in_out(seg(t, 8.6, 8.9))
        ph = (t - 8.6) / 0.3
        s.update(x=lerp(PIP_X, 440, k), eyes="sparkle", beak="grin", look=(7, -2),
                 lean=-6 * math.sin(2 * math.pi * ph), hop=6 * abs(math.sin(2 * math.pi * ph)))
    elif t < 9.15:                    # hops up onto the seat (Snip holds it still)
        x, base, sq = arc_hop(t, 8.9, 9.15, (440, GY), (SX, SEAT_TOP + SIT_DY), 80)
        s.update(mode="hop", x=x, base=base, sq=sq, eyes="happy", beak="grin", wl=-60, wr=60)
    elif t < 13.0:                    # swinging! wheee
        s.update(mode="seat", eyes="happy" if t > 9.45 else "sparkle", beak="grin")
        v = theta_vel(t)
        s["tilt"] = -0.4 * v * 0.1
        for c in PUSHES:
            s["head_dy"] -= 6 * math.sin(math.pi * seg(t, c, c + 0.3))
        if 12.5 < t:
            s.update(eyes="normal", beak="smile", look=(-6, 2))
    elif t < 13.3:                    # hops off to the left
        x, base, sq = arc_hop(t, 13.0, 13.3, (SX, SEAT_TOP + SIT_DY), (365, GY), 60)
        s.update(mode="hop", x=x, base=base, sq=sq, eyes="happy", beak="grin", wl=-40, wr=40)
    elif t < 13.55:                   # "your turn, Snip!" -- wing towards the swing
        up = ease_out_back(seg(t, 13.3, 13.45))
        s.update(x=365, eyes="happy", beak="grin", look=(-6, 0), wr=lerp(8, 100, up),
                 wl=-8)
    elif t < 13.95:                   # back to the side, out of the swing's way
        k = ease_in_out(seg(t, 13.55, 13.95))
        ph = (t - 13.55) / 0.2
        s.update(x=lerp(365, PIP_X, k), eyes="happy", beak="grin", look=(7, -4),
                 lean=6 * math.sin(2 * math.pi * ph), hop=5 * abs(math.sin(2 * math.pi * ph)))
    elif t < 16.3:                    # laughing, cheering, watching the paw-bump
        s.update(eyes="happy", beak="grin", look=(7, -4))
        for c in (14.0, 14.4, 15.45):
            h, sq = hop_curve(t, c, c + 0.3, 1, 26)
            if h or sq != 1.0:
                s["hop"], s["sq"] = h, sq
        flap = math.sin(2 * math.pi * (t - 13.95) / 0.25) * (1 - seg(t, 14.7, 14.9))
        s["wl"], s["wr"] = -30 - 25 * flap, 30 + 25 * flap
        if t > 14.9:
            s["wl"], s["wr"] = -8, 8
    else:                             # waves bye and waddles home
        k = ease_in(seg(t, 16.55, 17.3))
        ph = (t - 16.55) / 0.3
        wave = 130 + 20 * math.sin(2 * math.pi * (t - 16.3) / 0.3)
        s.update(x=lerp(PIP_X, -170, k), eyes="happy", beak="grin", look=(7, -1) if t < 16.55 else (-7, 0),
                 wr=wave, wl=-10, lean=-4 + 6 * math.sin(2 * math.pi * ph) * seg(t, 16.55, 16.65),
                 hop=5 * abs(math.sin(2 * math.pi * ph)) * seg(t, 16.55, 16.65))
    if s["mode"] == "seat":
        sw = swing_state(t)
        sx_, sy_ = seat_pt(sw)
        s["x"], s["base"] = sx_, sy_ + SIT_DY
    if s["hop"] == 0 and s["mode"] != "hop":
        s["sq"] *= breath(t, 1.5, 0.015)
    return s


def pip_seat_wings(pp):
    out = []
    for side, i, ref in (("l", -1, -40), ("r", 1, 40)):
        sh = PIP.shoulder_pt(pp["x"], pp["base"], side, pp["hop"], pp["lean"], pp["sq"])
        target = (pp["x"] + i * CDX, sh[1] + 70)
        out.append(aim_from(sh, target, pp["lean"], ref))
    return out


# ---------------------------------------------------------------- Crinkle
def crinkle_state(t):
    s = dict(x=CR_HOME, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, arm_l=CR_REST_L, arm_r=2.0, eyes="normal",
             mouth="smile", look=(0, 0), head_dy=0.0, sign=0.0, on=True)
    if t < 6.6 or 8.85 <= t < 13.95 or t >= 16.8:
        s["on"] = False
        s["x"] = 1450
        return s
    if t < 8.3:                       # slides in, worried at the spinning, shows the "take turns" sign
        s["x"] = lerp(1450, CR_HOME, ease_out(seg(t, 6.6, 7.1)))
        s["lean"] = 12 * (1 - ease_out(seg(t, 6.6, 7.4)))
        if t < 7.1:
            s.update(eyes="wide", mouth="o", look=(-7, -4))
        else:
            s.update(look=(-7, -3), tilt=6 * ease_in_out(seg(t, 7.2, 7.5)))
        up = ease_out_back(seg(t, 7.0, 7.3)) * (1 - ease_in_out(seg(t, 8.0, 8.3)))
        s["arm_l"] = lerp(CR_REST_L, 194, up)
        s["sign"] = pop_scale(t, 7.05, 0.3) * (1 - ease_in_out(seg(t, 7.95, 8.2)))
        s["head_dy"] = 10 * math.sin(math.pi * seg(t, 7.75, 7.95))
    else:                             # thumbs-up wave and steps aside to give them room
        s.update(eyes="happy", mouth="grin", look=(-6, 0))
        h, sq = hop_curve(t, 8.4, 8.85, 1, 30)
        s.update(x=lerp(CR_HOME, 1450, ease_in(seg(t, 8.4, 8.85))), hop=h, sq=sq, lean=-6)
        s["arm_r"] = 140 + 22 * math.sin((t - 8.3) * 16)
    if 13.95 <= t < 16.0:
        s = dict(x=CR_HOME, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, arm_l=CR_REST_L, arm_r=2.0, eyes="happy",
                 mouth="grin", look=(-7, 0), head_dy=0.0, sign=0.0, on=True)
        if t < 14.6:                  # comes back, cheering
            s["x"] = lerp(1450, CR_HOME, ease_out(seg(t, 13.95, 14.45)))
            s["lean"] = 10 * (1 - ease_out(seg(t, 13.95, 14.6)))
            up = ease_out_back(seg(t, 14.1, 14.35))
            s["arm_r"] = lerp(2, 150 + 10 * math.sin((t - 14.1) * 14), up)
        else:                         # paw-bump
            h, sq = hop_curve(t, 14.6, 14.95, 1, 18)
            s.update(x=lerp(CR_HOME, CR_BUMP, ease_in_out(seg(t, 14.6, 14.95))), hop=h, sq=sq)
            s["arm_r"] = lerp(150, 2, ease_out(seg(t, 14.6, 14.8)))
            wind = ease_in_out(seg(t, 15.0, 15.2))
            swing = ease_out_back(seg(t, 15.2, 15.45))
            s["arm_l"] = lerp(lerp(CR_REST_L, 360, wind), 198, swing)
    elif 16.0 <= t < 16.8:            # waves bye and hops away
        s = dict(x=CR_BUMP, hop=0.0, sq=1.0, lean=-6, tilt=0.0, arm_l=CR_REST_L, arm_r=2.0, eyes="happy",
                 mouth="grin", look=(-6, 0), head_dy=0.0, sign=0.0, on=True)
        h, sq = hop_curve(t, 16.05, 16.8, 2, 40)
        s.update(x=lerp(CR_BUMP, 1450, ease_in_out(seg(t, 16.05, 16.8))), hop=h, sq=sq)
        s["arm_l"] = lerp(198, CR_REST_L, ease_out(seg(t, 16.0, 16.2)))
        s["arm_r"] = 140 + 22 * math.sin((t - 16.0) * 16)
    if s["hop"] == 0:
        s["sq"] *= breath(t + 0.7, 2.25, 0.01)
    return s


# ---------------------------------------------------------------- drawing
def draw_snip_char(f, sn, t, arms=None):
    eyes = sn["eyes"]
    blink = blinking(t, SNIP_BLINKS) and not frozen(t) and eyes in BLINKABLE and sn["dizzy"] < 0.01
    al, ar = arms if arms is not None else (sn["arm_l"], sn["arm_r"])
    SNIP.draw(f, sn["x"], sn["base"], hop=sn["hop"], lean=sn["lean"], head_tilt=sn["tilt"], arm_l=al, arm_r=ar,
              eyes=eyes, mouth=sn["mouth"], look=sn["look"], squash=sn["sq"], head_dy=sn["head_dy"], blink=blink,
              ears=tuple(sn["ears"]), ear_stretch=sn["ear_stretch"])
    if sn["dizzy"] > 0.01:            # spiral eyes on top of the normal eyes
        hx, hy = SNIP.head_pivot(sn["x"], sn["base"], sn["hop"], sn["lean"], sn["sq"], sn["head_dy"])
        ha = sn["lean"] + sn["tilt"]
        for i, ex in enumerate((-47, 47)):
            dx, dy = rot(ex * SNIP.s, -122 * SNIP.s, ha)
            place(f, SPIRAL, (hx + dx, hy + dy), angle=(-1 if i else 1) * t * 420, scale=sn["dizzy"])


def draw_arms(f, ch, x, base, st, al, ar):
    place(f, ch.arm_l, ch.shoulder_pt(x, base, "l", st["hop"], st["lean"], st["sq"]), angle=al + st["lean"])
    place(f, ch.arm_r, ch.shoulder_pt(x, base, "r", st["hop"], st["lean"], st["sq"]), angle=ar + st["lean"])


def draw_rider_layer(f, sw, t, sn, pp):
    """Seat + whoever sits on it, squeezed sideways when the chains spin the seat round."""
    sp = seat_pt(sw)
    sc = math.cos(math.radians(sw["spin"]))
    if abs(sc) > 0.999:
        target, ox, oy = f, 0, 0
    else:
        x0, y0 = int(sp[0] - 330), int(sp[1] - 860)
        target = Image.new("RGBA", (660, 1000), (0, 0, 0, 0))
        ox, oy = x0, y0

    def sh(st):
        d = dict(st)
        d["x"] = st["x"] - ox
        d["base"] = st["base"] - oy
        return d
    seat_at = (sp[0] - ox, sp[1] - oy)
    if sn is not None:
        s2 = sh(sn)
        draw_snip_char(target, s2, t, snip_seat_arms(s2, sw))
        place(target, SEAT, seat_at)
        place(target, SNIP_FEET, (seat_at[0], seat_at[1] + 10))
        al, ar = snip_seat_arms(s2, sw)
        draw_arms(target, SNIP, s2["x"], s2["base"], s2, al, ar)
    elif pp is not None:
        p2 = sh(pp)
        wl, wr = pip_seat_wings(p2)
        PIP.draw(target, p2["x"], p2["base"], hop=p2["hop"], lean=p2["lean"], tilt=p2["tilt"], wing_l=wl, wing_r=wr,
                 eyes=p2["eyes"], beak=p2["beak"], look=p2["look"], squash=p2["sq"], head_dy=p2["head_dy"],
                 blink=blinking(t, PIP_BLINKS) and not frozen(t), wings=False)
        place(target, SEAT, seat_at)
        place(target, PIP_FEET, (seat_at[0], seat_at[1] + 14))
        PIP.draw_wings(target, p2["x"], p2["base"], p2["hop"], p2["lean"], p2["sq"], wl, wr)
    else:
        place(target, SEAT, seat_at)
    if target is not f:
        bb = target.getbbox()
        if bb is None:
            return
        w = max(2, int(round(target.width * max(0.14, abs(sc)))))
        img = target.resize((w, target.height), Image.BICUBIC)
        if sc < 0:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        f.alpha_composite(img, (int(round(sp[0] - w / 2)), oy))


def draw_pip_standing(f, pp, t):
    PIP.draw(f, pp["x"], pp["base"], hop=pp["hop"], lean=pp["lean"], tilt=pp["tilt"], wing_l=pp["wl"],
             wing_r=pp["wr"], eyes=pp["eyes"], beak=pp["beak"], look=pp["look"], squash=pp["sq"],
             head_dy=pp["head_dy"], blink=blinking(t, PIP_BLINKS) and not frozen(t), turn=pp["turn"])


def render_frame(t):
    f = BG.copy()
    for spr, x, y, ph in CLOUDS:
        place(f, spr, (x + 22 * math.sin(2 * math.pi * t / DUR + ph), y + 4 * math.sin(4 * math.pi * t / DUR + ph)))

    sw = swing_state(t)
    sn, cr, pp = snip_state(t), crinkle_state(t), pip_state(t)

    # Crinkle (behind the swing), sign held up in front of him
    if cr["on"]:
        CR.draw(f, cr["x"], GY, hop=cr["hop"], lean=cr["lean"], head_tilt=cr["tilt"], arm_l=cr["arm_l"],
                arm_r=cr["arm_r"], eyes=cr["eyes"], mouth=cr["mouth"], look=cr["look"], squash=cr["sq"],
                head_dy=cr["head_dy"], blink=blinking(t, CR_BLINKS) and not frozen(t))

    # Snip standing / hopping (behind the swing, except in front of the stopped swing for the paw-bump)
    snip_front = 14.7 <= t < 16.45
    arms = None
    if sn["mode"] != "seat" and not snip_front:
        arms = None
        if sn["steady"]:
            sh = SNIP.shoulder_pt(sn["x"], sn["base"], "r", sn["hop"], sn["lean"], sn["sq"])
            sp = seat_pt(sw)
            arms = (sn["arm_l"], aim_from(sh, (sp[0] - CDX, sp[1] - 120), sn["lean"], 60))
        elif sn["push"]:
            arms = tuple(snip_push_arms(sn, t, sw))
        draw_snip_char(f, sn, t, arms)

    # the swing: chains, then seat + rider
    PS.draw_chains(f, chain_strands(sw))
    rider_snip = sn if sn["mode"] == "seat" else None
    rider_pip = pp if (pp["on"] and pp["mode"] == "seat") else None
    draw_rider_layer(f, sw, t, rider_snip, rider_pip)

    # Snip's paws in front (steadying the chain / pushing Pip's back / paw-bump)
    if sn["mode"] != "seat" and (sn["steady"] or sn["push"]):
        draw_arms(f, SNIP, sn["x"], sn["base"], sn, *arms)

    if snip_front:
        draw_snip_char(f, sn, t)

    # Pip on the ground / hopping
    if pp["on"] and pp["mode"] != "seat":
        draw_pip_standing(f, pp, t)

    # Crinkle's sign
    if cr["on"] and cr["sign"] > 0.01:
        tip = CR.paw_tip(cr["x"], GY, "l", cr["arm_l"], cr["hop"], cr["lean"], cr["sq"])
        place(f, SIGN, (tip[0] + 25, tip[1] - 120), scale=1.05 * cr["sign"], angle=3 * math.sin(t * 5),
              alpha=min(1.0, cr["sign"] * 2.5))
        place(f, CR.arm_l, CR.shoulder_pt(cr["x"], GY, "l", cr["hop"], cr["lean"], cr["sq"]),
              angle=cr["arm_l"] + cr["lean"])

    # paw-bump: both touching paws in front
    if 14.95 <= t < 16.1:
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], GY, "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])
        place(f, CR.arm_l, CR.shoulder_pt(cr["x"], GY, "l", cr["hop"], cr["lean"], cr["sq"]),
              angle=cr["arm_l"] + cr["lean"])

    # spin streaks + dizzy stars
    spin_speed = abs(swing_state(t + 0.02)["spin"] - swing_state(t - 0.02)["spin"]) / 0.04 if not frozen(t) else 0
    if spin_speed > 200 and sn["mode"] == "seat":
        a = min(1.0, (spin_speed - 200) / 500)
        hx, hy = SNIP.head_pivot(sn["x"], sn["base"])
        for i, (dx, dy, ang) in enumerate(((-230, -120, 150), (230, -100, -30), (-210, 130, 170), (210, 150, -10))):
            place(f, SWIRL, (hx + dx, hy + dy), angle=ang + 20 * math.sin(t * 12 + i), alpha=0.85 * a)
    if 6.55 <= t < 7.6 and sn["mode"] == "seat":
        k = pop_scale(t, 6.55, 0.25) * (1 - ease_in_out(seg(t, 7.35, 7.6)))
        hx, hy = SNIP.head_pivot(sn["x"], sn["base"], 0, sn["lean"], sn["sq"], sn["head_dy"])
        for i, st in enumerate(STARS):
            a = 2 * math.pi * (t * 1.4 + i / 3)
            place(f, st, (hx + 150 * math.cos(a), hy - 300 + 34 * math.sin(a)), scale=k * (1.35 + 0.25 * math.sin(a)),
                  angle=t * 200)

    # Pip's wish: a turn on the swing
    if pp["on"] and 2.05 <= t < 8.4 and pp["mode"] == "stand":
        hx, hy = PIP.head_pivot(pp["x"], GY, pp["hop"], pp["lean"], pp["sq"], pp["head_dy"])
        k = pop_scale(t, 2.05, 0.3) * (1 - ease_in_out(seg(t, 8.1, 8.4)))
        k *= 1 + 0.12 * math.sin(math.pi * seg(t, 7.3, 7.7))
        place(f, THOUGHT, (hx - 4, hy - 200 + 5 * math.sin(2 * math.pi * t / 1.5)), scale=1.15 * k)

    # hook sparkle on Snip swinging (wraps across the loop point)
    tw = (t - 17.55) % DUR
    if tw < 1.2 and sn["mode"] == "seat":
        hx, hy = SNIP.head_pivot(sn["x"], sn["base"], 0, sn["lean"], sn["sq"])
        place(f, SPARKLE, (hx + 190, hy - 230), scale=0.26 * math.sin(math.pi * tw / 1.2), angle=tw * 70)

    # counting numerals
    for i, c in enumerate(PUSHES):
        if c <= t < c + 0.9:
            out = 1 - ease_in_out(seg(t, c + 0.7, c + 0.9))
            place(f, NUMS[i], (560, 600), scale=pop_scale(t, c, 0.28) * out, angle=-6 + 4 * math.sin(t * 6))

    if 13.85 <= t < 14.6:
        place(f, CHECK, (560, 560), scale=pop_scale(t, 13.85, 0.25) * (1 - ease_in_out(seg(t, 14.35, 14.6))))

    for i, (t0, x, y) in enumerate(HEART_PLAN):
        end = 12.6 if t0 < 13 else 14.75
        if t0 <= t < end:
            p = seg(t, t0, end)
            place(f, HEARTS[i], (x + 10 * math.sin(t * 3 + i), y - 170 * p), scale=pop_scale(t, t0, 0.25),
                  alpha=1 - ease_in_out(seg(t, end - 0.35, end)), angle=10 * math.sin(t * 2.5 + i))

    if 15.45 <= t < 16.2:
        sn_tip = SNIP.paw_tip(sn["x"], GY, "r", sn["arm_r"], sn["hop"], sn["lean"], sn["sq"])
        c_tip = CR.paw_tip(cr["x"], GY, "l", cr["arm_l"], cr["hop"], cr["lean"], cr["sq"])
        mid = ((sn_tip[0] + c_tip[0]) / 2, (sn_tip[1] + c_tip[1]) / 2 - 10)
        place(f, SPARKLE, (mid[0], mid[1] - 35), scale=pop_scale(t, 15.45, 0.22) * 0.55, angle=(t - 15.45) * 60,
              alpha=1 - ease_in_out(seg(t, 15.9, 16.2)))

    # FREEZE: dim + choice bubbles (keep swinging? / give Pip a turn?)
    if 2.5 <= t < 4.6:
        dim = 0.32 * ease_in_out(seg(t, 2.5, 2.8)) * (1 - ease_in_out(seg(t, 4.35, 4.6)))
        if dim > 0.01:
            f.alpha_composite(Image.new("RGBA", f.size, (30, 26, 52, int(255 * dim))))
        gone = 1 - ease_in_out(seg(t, 4.4, 4.55))
        pulse_a = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 2.95) / 1.0))
        pulse_b = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 3.45) / 1.0))
        place(f, BUB_KEEP, (300, 620), scale=1.1 * pop_scale(t, 2.55) * gone * (pulse_a if t > 2.95 else 1))
        place(f, BUB_GIVE, (780, 620), scale=1.1 * pop_scale(t, 2.7) * gone * (pulse_b if t > 3.45 else 1))
        place(f, QMARK, (540, 520), scale=pop_scale(t, 2.85, 0.25) * gone, angle=8 * math.sin(t * 4))

    return camera(f, t)


CAM_KEYS = [
    (0.0, 1.45, 560, 1000), (1.0, 1.47, 560, 1000), (2.3, 1.0, 540, 960), (4.5, 1.0, 540, 960),
    (5.1, 1.1, 500, 980), (6.3, 1.1, 500, 980), (6.8, 1.0, 540, 960), (9.2, 1.0, 540, 960),
    (9.6, 1.12, 470, 1060), (12.6, 1.12, 470, 1060), (13.0, 1.0, 540, 960), (15.2, 1.0, 540, 960),
    (15.45, 1.08, 540, 1060), (15.9, 1.08, 540, 1060), (16.3, 1.0, 540, 960), (16.6, 1.0, 540, 960),
    (DUR, 1.45, 560, 1000)]


def camera(f, t):
    z, cx, cy = 1.0, 540, 960
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
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
    # playground birds, soft, scattered
    for tt, b in ((0.7, 3000), (3.2, 3300), (7.0, 2900), (12.8, 3200), (16.9, 3000)):
        sfx.add(tt, PP.chirp(0.6, b))
    # a soft bed under everything (no dead air)
    for tt, ch in ((0.0, (48, 55, 64)), (4.5, (45, 52, 60)), (8.0, (41, 48, 57)), (12.5, (43, 50, 59)),
                   (16.5, (48, 55, 64))):
        music.add(tt, A.pad([M(m) for m in ch], 4.6 if tt < 16 else 2.0, 0.12))
    # hook: swinging high, wheee, creaks on each swing
    A.jingle(music, 0.02)
    for tt in (0.375, 1.125, 1.875):
        sfx.add(tt, PS.creak(0.8, up=(tt * 2 / HOOK_P) % 2 < 1))
    sfx.add(0.3, PS.wheee(0.55, 0.8))
    sfx.add(1.05, PS.wheee(0.55, 0.7))
    sfx.add(1.0, A.twinkle(0.5))
    for tt, ch, up in ((1.0, "C", False), (1.25, "C", True), (1.5, "F", False), (1.75, "F", True)):
        A.strum(music, tt, ch, 0.65, up)
    music.add(1.0, A.bass(M(48), 0.5, 0.7))
    music.add(1.5, A.bass(M(41), 0.5, 0.7))
    # Pip waddles in, sad
    tt = 1.2
    while tt < 2.1:
        sfx.add(tt, A.tap(0.3))
        tt += 0.18
    A.strum(music, 2.0, "Am", 0.55)
    music.add(2.0, A.bass(M(45), 0.5, 0.6))
    sfx.add(2.05, A.pop(0.5))
    sfx.add(2.1, PP.sad_coo(0.9))
    # freeze: tick-tock + soft pad
    music.add(2.55, A.pad([M(45), M(52), M(57)], 2.0, 0.25))
    k, tt = 0, 2.75
    while tt < 4.4:
        sfx.add(tt, A.woodblock(k % 2 == 0, 0.8))
        tt += 0.25
        k += 1
    for tt in (2.55, 2.7):
        sfx.add(tt, A.pop(0.7))
    sfx.add(2.85, A.glock(M(91), 0.6, 0.4))
    sfx.add(4.42, A.pop(0.6))
    # slapstick: keeps swinging and twisting... wound up... WHIRR... dizzy
    sfx.add(4.6, PS.creak(0.7, True))
    sfx.add(4.6, PS.ratchet(10, 0.7, 0.9))
    for i, m in enumerate((55, 59, 62, 65, 67)):
        music.add(4.6 + i * 0.13, A.pluck(M(m), 0.25, 0.45))
    sfx.add(5.32, A.uh_oh(0.8))
    sfx.add(5.6, PS.whirr(1.1, 1.0))
    sfx.add(5.6, PP.slide_whistle(True, 0.5, 0.5))
    sfx.add(6.1, PP.slide_whistle(False, 0.6, 0.5))
    sfx.add(6.7, PS.dizzy(0.9, 0.9))
    sfx.add(6.75, A.twinkle(0.5, (96, 100, 103, 100, 96)))
    music.add(6.75, A.wah_down(0.6))
    sfx.add(6.4, PP.quack(0.6, 1.2))
    # Crinkle + take-turns sign; Snip shakes it off and nods
    sfx.add(6.58, A.whoosh(0.5, 1.0))
    sfx.add(7.05, A.pop(0.7))
    sfx.add(7.08, A.glock(M(88), 1.0, 0.7))
    sfx.add(7.22, A.glock(M(91), 1.0, 0.6))
    for tt, ch in ((7.1, "Dm"), (7.6, "G")):
        A.strum(music, tt, ch, 0.55)
        music.add(tt, A.bass(M({"Dm": 50, "G": 43}[ch]), 0.5, 0.6))
    sfx.add(7.36, A.whoosh(0.25, 0.4))
    sfx.add(7.75, A.tap(0.5))
    # "your turn!": Snip hops off, Pip yay, Crinkle steps aside, Pip hops on
    sfx.add(7.95, A.boing(0.4, 330))
    sfx.add(8.3, A.tap(0.6))
    sfx.add(8.42, PP.quack(0.85, 1.15))
    sfx.add(8.45, A.twinkle(0.6))
    sfx.add(8.4, A.boing(0.3, 300))
    for tt, ch in ((8.1, "C"), (8.6, "F")):
        A.strum(music, tt, ch, 0.55)
        music.add(tt, A.bass(M({"C": 48, "F": 41}[ch]), 0.5, 0.6))
    tt = 8.62
    while tt < 8.9:
        sfx.add(tt, A.tap(0.3))
        tt += 0.1
    sfx.add(8.9, A.boing(0.45, 360))
    sfx.add(9.12, A.tap(0.6))
    sfx.add(9.15, PS.creak(0.5, False))
    # gentle pushes 1-2-3
    tt, k = 9.0, 0
    while tt < 12.4:
        sfx.add(tt, A.woodblock(k % 2 == 0, 0.3))
        tt += 0.5
        k += 1
    for i, (c, m) in enumerate(zip(PUSHES, (84, 88, 91))):
        sfx.add(c, A.glock(M(m), 1.2, 0.9))
        music.add(c, A.ks_pluck(M(m - 24), 1.0, 0.8))
        music.add(c, A.bass(M(48), 0.4, 0.5))
        sfx.add(c + 0.02, A.tap(0.5))
        sfx.add(c + 0.25, PS.creak(0.5, True))
        sfx.add(c + 0.12, PP.quack(0.6, 1.1 + 0.08 * i))
    sfx.add(11.75, PS.wheee(0.6, 0.6))
    sfx.add(11.8, A.chime_up(0.8))
    for tt, _, _ in HEART_PLAN[:2]:
        sfx.add(tt, A.pop(0.4))
    # Snip catches the seat; Pip hops off: "your turn!"; Snip hops on; both laugh
    sfx.add(12.5, A.tap(0.5))
    music.add(12.5, A.pad([M(60), M(64), M(67)], 1.0, 0.4))
    sfx.add(13.02, A.boing(0.35, 340))
    sfx.add(13.32, PP.quack(0.8, 1.2))
    sfx.add(13.35, A.twinkle(0.6))
    sfx.add(13.45, A.boing(0.45, 300))
    sfx.add(13.72, A.tap(0.6))
    sfx.add(13.85, A.glock(M(96), 1.0, 0.7))
    sfx.add(13.87, A.twinkle(0.7))
    sfx.add(13.9, PS.giggle(0.9, 760))
    sfx.add(14.0, PP.quack(0.7, 1.25))
    sfx.add(14.4, PP.quack(0.7, 1.15))
    for tt, _, _ in HEART_PLAN[2:]:
        sfx.add(tt, A.pop(0.4))
    for tt, ch, up in ((13.0, "Am", False), (13.25, "Am", True), (13.5, "F", False), (13.75, "F", True),
                       (14.0, "C", False), (14.25, "C", True), (14.5, "G", False), (14.75, "G", True)):
        A.strum(music, tt, ch, 0.8, up)
    for tt, m in ((13.0, 45), (13.5, 41), (14.0, 48), (14.5, 43)):
        music.add(tt, A.bass(M(m), 0.45, 0.8))
    sfx.add(13.95, A.whoosh(0.45, 0.8))
    # paw-bump
    sfx.add(14.55, A.boing(0.35, 320))
    sfx.add(14.85, A.snare_roll(0.6, 0.8))
    sfx.add(15.45, A.boop(0.9))
    A.jingle(music, 15.47, 1.0, ending=True)
    sfx.add(15.5, A.twinkle(0.8))
    # bye-bye; Pip waddles home; Snip hops back on... wheee (leads into the jingle at 0:00)
    sfx.add(16.0, PP.quack(0.7, 1.15))
    sfx.add(16.05, A.boing(0.35, 300))
    sfx.add(16.42, A.boing(0.3, 330))
    sfx.add(16.45, A.boing(0.4, 360))
    tt = 16.55
    while tt < 17.3:
        sfx.add(tt, A.tap(0.25))
        tt += 0.15
    A.strum(music, 16.3, "F", 0.5)
    A.strum(music, 16.8, "G7", 0.5)
    sfx.add(16.8, A.tap(0.6))
    sfx.add(17.2, PS.creak(0.6, True))
    sfx.add(17.35, PS.giggle(0.6, 820))
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
    wav = os.path.join(ROOT, "build", "ep08_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep08_your_turn_swing.mp4")
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
    times = times or [0.0, 1.0, 2.0, 3.4, 4.9, 5.4, 6.0, 6.9, 7.4, 8.4, 8.75, 9.5, 10.5, 11.5,
                      12.2, 13.35, 14.1, 15.6, 16.6, 17.5, 17.99]
    cols = 7
    rows = math.ceil(len(times) / cols)
    sheet = Image.new("RGB", (216 * cols, 404 * rows), "white")
    d = ImageDraw.Draw(sheet)
    for i, tt in enumerate(times):
        im = render_frame(tt).convert("RGB").resize((216, 384), Image.LANCZOS)
        x, y = (i % cols) * 216, (i // cols) * 404
        sheet.paste(im, (x, y + 20))
        d.text((x + 6, y + 4), f"{tt:.1f}s", fill="black")
    sheet.save(path)
    print("wrote", path)


KEY_TIMES = (0.0, 3.4, 5.4, 6.9, 7.5, 10.5, 14.1, 15.6)


def keys(path, times=KEY_TIMES, w=360):
    h = int(w * 16 / 9)
    sheet = Image.new("RGB", (w * 4, (h + 30) * 2), "white")
    d = ImageDraw.Draw(sheet)
    for i, tt in enumerate(times):
        im = render_frame(tt).convert("RGB").resize((w, h), Image.LANCZOS)
        x, y = (i % 4) * w, (i // 4) * (h + 30)
        sheet.paste(im, (x, y + 30))
        d.text((x + 8, y + 9), f"{tt:.1f}s", fill="black")
    sheet.save(path)
    print("wrote", path)


def frames(times, w=540):
    for tt in times:
        p = os.path.join(ROOT, "build", f"ep08_f{tt:05.2f}.png")
        render_frame(tt).convert("RGB").resize((w, int(w * 16 / 9)), Image.LANCZOS).save(p)
        print("wrote", p)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    if "--stills" in sys.argv:
        stills(os.path.join(ROOT, "build", "ep08_stills.png"))
    elif "--keys" in sys.argv:
        os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
        keys(os.path.join(ROOT, "reviews", "ep08_keys.png"))
    elif "--frames" in sys.argv:
        frames([float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")])
    else:
        render(os.path.join(ROOT, "output"))
