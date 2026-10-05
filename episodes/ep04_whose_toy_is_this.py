"""Episode 4 -- Whose Toy Is This? (park)

Snip finds a pink teddy on a park bench and hugs it. Pip, a little duckling with a red
bow (the teddy wears the same bow), comes looking for it, sad. Choice: keep it, or give
it back? Snip hides the teddy behind their back... and its round ears pop up over Snip's
head. Crinkle arrives with a "whose toy?" sign; they look around (1), go to the owner (2)
and give it back (3). Pip's happy dance, hearts, the signature paw-bump, and a seamless
loop: Pip waves bye so hard the teddy flies back onto the bench (frame 18.0s == frame 0).

Run:  python3 episodes/ep04_whose_toy_is_this.py            (render -> output/)
      python3 episodes/ep04_whose_toy_is_this.py --stills    (contact sheet -> build/)
      python3 episodes/ep04_whose_toy_is_this.py --keys      (8 key frames, 360px wide -> reviews/)
      python3 episodes/ep04_whose_toy_is_this.py --frames 5.6,10.6   (full-size frames -> build/)
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
import scene  # noqa: E402
from characters import BLINKABLE, SNIP_EAR_BASE, SNIP_EAR_TILT, Character  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, rot, seg  # noqa: E402

FPS = 30
DUR = 18.0
GY = PP.GROUND_Y
SNIP_HOME = 420
TEDDY_BENCH = (225, PP.SEAT_Y + 2)
DK_X = 118                            # Pip's spot, in front of the bench
CR_HOME = 800                         # keeps Crinkle's right arm clear of the like/comment buttons
CR_REST_L = 346                       # Crinkle's left arm hanging (== -14)
HUG_L, HUG_R = 44, -44                # Snip's arms wrapped round the teddy
BEHIND_L, BEHIND_R = 30, -30          # Snip's paws tucked behind the back
PIP_TEDDY_S = 0.85                    # teddy scale in Pip's wings

BG = PP.background()
CANOPY = PP.canopy()
SUN = PP.sun()
CLOUDS = [(PP.cloud(300, 130), 720, 330, 0.0), (PP.cloud(240, 110), 960, 610, 2.1), (PP.cloud(210, 96), 560, 150, 4.0)]
TEDDY = PP.teddy()
THOUGHT = PP.thought_bubble()
SIGN = PP.sign_whose()
BUB_KEEP = PP.choice_bubble_park("keep", (240, 110, 100))
BUB_GIVE = PP.choice_bubble_park("give", (90, 190, 120))
QMARK = icons.question()
CHECK = icons.check(130)
SPARKLE = scene.sparkle()
NUMS = [scene.numeral(1, (244, 112, 104)), scene.numeral(2, (255, 196, 52)), scene.numeral(3, (84, 182, 222))]
HEARTS = [scene.heart(c, 80) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120), (255, 150, 170),
                                       (240, 72, 98))]
SMALL_HEARTS = [scene.heart(c, 56) for c in ((255, 120, 150), (240, 72, 98))]
SNIP = Character("snip", 1.15)
CR = Character("crinkle", 1.2)
PIP = PP.Duckling(0.9)

SNIP_BLINKS = (1.9, 6.3, 7.95, 9.95, 12.05, 14.3, 16.9)
CR_BLINKS = (7.3, 9.0, 10.95, 13.0, 14.35)
PIP_BLINKS = (2.25, 5.3, 6.9, 8.2, 9.8, 15.0)
COUNTS = (8.4, 9.4, 10.4)
DANCE_HOPS = (11.9, 12.35, 12.8, 13.25)
HEART_PLAN = ((12.0, 70, 1060), (12.2, 230, 980), (12.45, 150, 900), (12.7, 330, 1010), (12.95, 40, 950))


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


# ---------------------------------------------------------------- Snip
def snip_state(t):
    s = dict(x=SNIP_HOME, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, arm_l=-14.0, arm_r=14.0, eyes="normal",
             mouth="w", look=(0, 0), head_dy=0.0, ears=[0.0, 0.0], ear_stretch=1.0, behind=False)
    idle_ear = 2.0 * math.sin(2 * math.pi * t / 3.0)

    if t < 1.0:                       # HOOK: tiptoe toward the teddy, paw reaching
        p = ease_in_out(seg(t, 0.0, 1.0))
        s.update(x=lerp(SNIP_HOME, 392, p), hop=9 * abs(math.sin(math.pi * t / 0.5)), lean=lerp(4, 8, p),
                 arm_l=lerp(-40, -62, p), eyes="wide", mouth="o", look=(-7, 3))
    elif t < 2.5:                     # DESIRE: scoop it up and hug it
        g = ease_in_out(seg(t, 1.0, 1.3))
        sway = math.sin(2 * math.pi * (t - 1.3) / 0.9) if t > 1.3 else 0.0
        s.update(x=lerp(392, 400, g), lean=lerp(8, 0, g) + 5 * sway, tilt=6 * sway,
                 arm_l=lerp(-62, HUG_L, g), arm_r=lerp(14, HUG_R, g),
                 eyes="wide" if t < 1.15 else "sparkle", mouth="o" if t < 1.15 else "grin",
                 look=(-4, 4) if t < 1.15 else (-2, 7))
        e = spring(t, 1.3, 12, 4.0, 3.0)
        s["ears"] = [e, -e]
    elif t < 4.5:                     # FREEZE for the choice
        return snip_state(2.4999)
    elif t < 6.0:                     # SLAPSTICK: hide it behind the back... the ears pop up
        s["x"] = 400
        if t < 4.62:                  # glance at the duckling
            s.update(arm_l=HUG_L, arm_r=HUG_R, eyes="wide", mouth="o", look=(-8, 1))
        elif t < 4.8:                 # whip it behind the back
            k = ease_in_out(seg(t, 4.62, 4.72))
            s.update(arm_l=lerp(HUG_L, BEHIND_L, k), arm_r=lerp(HUG_R, BEHIND_R, k), behind=t >= 4.68,
                     eyes="closed", mouth="w", sq=1 - 0.06 * math.sin(math.pi * seg(t, 4.62, 4.8)))
        else:
            s.update(arm_l=BEHIND_L, arm_r=BEHIND_R, behind=True)
            if t < 5.0 or 5.35 <= t < 5.55:      # innocent whistle, eyes up and away
                sw = math.sin(2 * math.pi * t / 0.5)
                s.update(eyes="normal", mouth="blow", look=(6, -7), tilt=5 * sw, lean=-2 * sw)
            elif t < 5.15:                        # pop! eyes roll up to look
                s.update(eyes="wide", mouth="o", look=(1, -9))
            elif t < 5.35:                        # squash down to hide it again
                d = math.sin(math.pi * seg(t, 5.15, 5.35))
                s.update(eyes="closed", mouth="w", sq=1 - 0.1 * d, head_dy=12 * d)
            elif t < 5.8:                         # BOING! there it is again
                h, _ = hop_curve(t, 5.55, 5.78, 1, 22)
                s.update(eyes="wide", mouth="O", look=(1, -9), hop=h)
                s["ear_stretch"] = 1 + 0.18 * (1 - ease_in_out(seg(t, 5.6, 5.95)))
                e = spring(t, 5.55, 9, 5.0, 4.0)
                s["ears"] = [-6 + e, 6 - e]
            else:                                 # caught -- sheepish
                droop = 24 * ease_out(seg(t, 5.8, 6.0))
                s.update(eyes="worried", mouth="wobble", look=(4, -3), ears=[droop, -droop])
    elif t < 8.0:                     # CRINKLE helps: "whose toy is this?"
        s["x"] = 400
        out = ease_in_out(seg(t, 7.6, 7.85))
        s.update(behind=t < 7.6, arm_l=lerp(BEHIND_L, HUG_L, out) if t >= 7.6 else BEHIND_L,
                 arm_r=lerp(BEHIND_R, HUG_R, out) if t >= 7.6 else BEHIND_R)
        droop = 24 * (1 - ease_in_out(seg(t, 7.3, 7.9)))
        s.update(eyes="worried" if t < 7.25 else "normal", mouth="wobble" if t < 7.25 else "w",
                 look=(7, -5) if t < 7.6 else (-3, 5), ears=[droop, -droop])
        s["head_dy"] = 14 * (math.sin(math.pi * seg(t, 6.95, 7.2)) + math.sin(math.pi * seg(t, 7.28, 7.53)))
    elif t < 11.5:                    # DO IT RIGHT: 1 look around, 2 go to the owner, 3 give it back
        s.update(x=400, arm_l=HUG_L, arm_r=HUG_R)
        if t < 8.4:                   # look right...
            k = ease_in_out(seg(t, 8.0, 8.3))
            s.update(lean=-6 * k, tilt=-6 * k, look=(8, -2))
        elif t < 8.8:                 # ...look left...
            k = ease_in_out(seg(t, 8.4, 8.7))
            s.update(lean=lerp(-6, 6, k), tilt=lerp(-6, 7, k), look=(-8, 2))
        elif t < 9.25:                # ...there! the duckling is looking for it
            k = ease_in_out(seg(t, 8.85, 9.15))
            s.update(lean=lerp(6, 2, k), tilt=lerp(7, 2, k), look=(-7, 4), eyes="wide" if t < 9.05 else "normal",
                     mouth="o" if t < 9.05 else "w")
            e = spring(t, 8.82, 10, 5.0, 4.0)
            s["ears"] = [e, -e]
        elif t < 10.1:                # hop over to Pip
            h, sq = hop_curve(t, 9.25, 9.7, 1, 34)
            s.update(x=lerp(400, 340, ease_in_out(seg(t, 9.25, 9.7))), hop=h, sq=sq, lean=2, look=(-7, 4),
                     mouth="smile" if t > 9.75 else "w")
        else:                         # hold it out... and let go
            s["x"] = 340
            give = ease_in_out(seg(t, 10.1, 10.45))
            back = ease_in_out(seg(t, 10.55, 10.9))
            s.update(lean=lerp(lerp(2, 10, give), 0, back), arm_l=lerp(lerp(HUG_L, -66, give), -14, back),
                     arm_r=lerp(lerp(HUG_R, -22, give), 14, back), look=(-8, 4),
                     eyes="happy" if t > 10.75 else "normal", mouth="grin" if t > 10.75 else "smile")
            e = spring(t, 10.8, 12, 5.0, 3.5)
            s["ears"] = [e, -e]
        for c in COUNTS:              # little nod on each count
            s["head_dy"] += 8 * math.sin(math.pi * seg(t, c, c + 0.28))
    elif t < 14.0:                    # PAYOFF: hooray with Pip
        s.update(x=340, eyes="happy", mouth="grin", look=(-6, 2))
        up = ease_out_back(seg(t, 11.6, 11.9)) * (1 - ease_in_out(seg(t, 13.5, 13.9)))
        wig = 14 * math.sin(2 * math.pi * (t - 11.6) / 0.45)
        s["arm_l"] = lerp(-14, -150 + wig, up)
        s["arm_r"] = lerp(14, 150 - wig, up)
        for c in (12.35, 13.25):
            h, sq = hop_curve(t, c, c + 0.3, 1, 22)
            if h or sq != 1.0:
                s["hop"], s["sq"] = h, sq
        e = spring(t, 11.6, 12, 5.0, 3.0) + spring(t, 12.35, 8, 5.0, 4.0) + spring(t, 13.25, 8, 5.0, 4.0)
        s["ears"] = [e, -e]
    elif t < 16.0:                    # PAW-BUMP
        h, sq = hop_curve(t, 14.0, 14.5, 1, 30)
        s.update(x=lerp(340, 440, ease_in_out(seg(t, 14.0, 14.5))), hop=h, sq=sq, eyes="happy", mouth="grin",
                 look=(6, -2))
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_r"] = lerp(lerp(14, -6, wind), 165, swing)
        e = spring(t, 15.45, 12, 5.0, 3.5)
        s["ears"] = [e, -e]
    elif t < 17.0:                    # wave bye, step home, watch Pip go
        h, sq = hop_curve(t, 16.0, 16.4, 1, 24)
        s.update(x=lerp(440, SNIP_HOME, ease_in_out(seg(t, 16.0, 16.4))), hop=h, sq=sq,
                 eyes="happy" if t < 16.7 else "normal", mouth="grin" if t < 16.7 else "w",
                 look=(7, -1) if t < 16.25 else (-7, 0))
        s["arm_r"] = lerp(165, 120 + 22 * math.sin((t - 16.0) * 16), ease_out(seg(t, 16.0, 16.15)))
        s["arm_r"] = lerp(s["arm_r"], 14, ease_in_out(seg(t, 16.55, 16.9)))
    else:                             # the teddy is back on the bench... eyes go wide (== frame 0)
        p = ease_in_out(seg(t, 17.1, 18.0))
        s.update(lean=lerp(0, 4, p), arm_l=lerp(-14, -40, ease_in_out(seg(t, 17.35, 18.0))),
                 eyes="wide" if t > 17.15 else "normal", mouth="o" if t > 17.15 else "w",
                 look=(-7, 3) if t > 17.15 else (-6, 1))
        e = spring(t, 17.15, 9, 5.0, 5.5)
        s["ears"] = [e, -e]

    s["ears"][0] += idle_ear
    s["ears"][1] -= idle_ear
    if s["hop"] == 0:
        s["sq"] *= breath(t)
    return s


def snip_hug_pt(sn):
    P = SNIP.anchor(sn["x"], GY, sn["hop"], sn["lean"])
    return P(0, -120 * sn["sq"] + 70)


def draw_snip(f, sn, t, between=None):
    """Character.draw, plus two poses it can't do: paws behind the back, and a prop between ears and face."""
    eyes = sn["eyes"]
    if blinking(t, SNIP_BLINKS) and not frozen(t) and eyes in BLINKABLE:
        eyes = "blink"
    x, hop, lean, sq = sn["x"], sn["hop"], sn["lean"], sn["sq"]
    if not sn["behind"] and between is None:
        SNIP.draw(f, x, GY, hop=hop, lean=lean, head_tilt=sn["tilt"], arm_l=sn["arm_l"], arm_r=sn["arm_r"],
                  eyes=eyes, mouth=sn["mouth"], look=sn["look"], squash=sq, head_dy=sn["head_dy"],
                  ears=tuple(sn["ears"]), ear_stretch=sn["ear_stretch"])
        return
    s = SNIP.s
    place(f, SNIP.ground, (x, GY + 6), alpha=max(0.25, 1 - hop / 160), sx=max(0.6, 1 - hop / 300), shadow=False)
    P = SNIP.anchor(x, GY, hop, lean)

    def arms():
        place(f, SNIP.arm_l, SNIP.shoulder_pt(x, GY, "l", hop, lean, sq), angle=sn["arm_l"] + lean)
        place(f, SNIP.arm_r, SNIP.shoulder_pt(x, GY, "r", hop, lean, sq), angle=sn["arm_r"] + lean)
    if sn["behind"]:
        arms()
    place(f, SNIP.body, P(0, -SNIP.neck_h * sq), angle=lean, sx=1 / math.sqrt(sq), sy=sq)
    if not sn["behind"]:
        arms()
    hx, hy = SNIP.head_pivot(x, GY, hop, lean, sq, sn["head_dy"])
    ha = lean + sn["tilt"]
    for (ox, oy), tilt, extra in zip(SNIP_EAR_BASE, SNIP_EAR_TILT, sn["ears"]):
        ex, ey = rot(ox * s, oy * s, ha)
        place(f, SNIP.ear, (hx + ex, hy + ey), angle=ha + tilt + extra, sy=sn["ear_stretch"])
    if between is not None:
        between(hx, hy, ha)
    place(f, SNIP.head(eyes, sn["mouth"], sn["look"]), (hx, hy), angle=ha)


# ---------------------------------------------------------------- Pip the duckling
def pip_state(t):
    s = dict(x=DK_X, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, wl=-8.0, wr=8.0, eyes="worried", beak="sad",
             look=(0, 0), head_dy=0.0, turn=1.0, hug=False, on=True)
    if t < 1.55 or t >= 17.25:
        s["on"] = False
        return s
    if t < 2.5:                       # waddles in, sad, looking around
        k = ease_out(seg(t, 1.55, 2.35))
        ph = (t - 1.55) / 0.36
        s.update(x=lerp(-140, DK_X, k), lean=7 * math.sin(2 * math.pi * ph) * (1 - seg(t, 2.2, 2.45)),
                 hop=6 * abs(math.sin(math.pi * 2 * ph)) * (1 - seg(t, 2.2, 2.4)),
                 look=(-6, 1) if int(ph) % 2 == 0 else (6, 1))
        if t > 2.3:
            s["look"] = (3, 5)
            s["head_dy"] = 8 * ease_in_out(seg(t, 2.3, 2.5))
    elif t < 4.5:
        return pip_state(2.4999)
    elif t < 8.75:                    # searching the grass, not noticing Snip's secret
        s.update(head_dy=8, look=(-4, 7))
        if 4.9 <= t < 5.9:            # peeks back towards the bench
            k = math.sin(math.pi * seg(t, 4.9, 5.9))
            s.update(lean=10 * k, tilt=8 * k, look=(-8, 5))
        else:
            s["lean"] = 3 * math.sin(2 * math.pi * (t - 4.5) / 1.5)
        sigh = math.sin(math.pi * seg(t, 6.3, 6.9))
        s["head_dy"] += 10 * sigh
        s["sq"] = 1 - 0.05 * sigh
        s["wl"], s["wr"] = -4, 4
        if t > 8.45:
            s.update(look=(2, 2), head_dy=8 * (1 - ease_in_out(seg(t, 8.45, 8.75))))
    elif t < 10.15:                   # sees its teddy! hopeful
        s.update(look=(7, -5), eyes="wide", beak="open" if t < 9.3 else "smile")
        h, sq = hop_curve(t, 8.9, 9.15, 1, 16)
        s["hop"], s["sq"] = h, sq
        s["wl"], s["wr"] = lerp(-8, -30, ease_out(seg(t, 8.9, 9.1))), lerp(8, 30, ease_out(seg(t, 8.9, 9.1)))
        s["tilt"] = -5 * ease_in_out(seg(t, 9.3, 9.6))
    elif t < 10.8:                    # takes it back
        reach = ease_in_out(seg(t, 10.15, 10.45))
        wrap = ease_in_out(seg(t, 10.5, 10.75))
        s.update(look=(7, -3), eyes="sparkle", beak="grin", wl=lerp(lerp(-30, -55, reach), 38, wrap),
                 wr=lerp(lerp(30, 30, reach), -38, wrap), hug=t >= 10.55)
    elif t < 11.6:                    # big hug
        sw = math.sin(2 * math.pi * (t - 10.8) / 0.8)
        s.update(eyes="closed", beak="smile", wl=38, wr=-38, hug=True, lean=5 * sw, tilt=4 * sw,
                 sq=1 - 0.05 * math.sin(math.pi * seg(t, 10.8, 11.1)))
    elif t < 14.0:                    # HAPPY DANCE
        s.update(eyes="happy", beak="grin", look=(0, 0))
        n = sum(1 for c in DANCE_HOPS if t >= c)
        side = -1 if n % 2 else 1
        for c in DANCE_HOPS:
            h, sq = hop_curve(t, c, c + 0.32, 1, 30)
            if h or sq != 1.0:
                s["hop"], s["sq"] = h, sq
        s["lean"] = side * 9 * ease_in_out(seg(t, 11.6, 11.8))
        s["x"] = DK_X + side * 10 * ease_in_out(seg(t, 11.6, 11.8))
        flap = math.sin(2 * math.pi * (t - 11.6) / 0.22)
        s["wl"], s["wr"] = -35 - 25 * flap, 35 + 25 * flap
        tw = seg(t, 13.3, 13.75)
        if 0 < tw < 1:
            s["turn"] = math.cos(2 * math.pi * tw)
        if t > 13.75:
            s.update(lean=lerp(s["lean"], 0, ease_in_out(seg(t, 13.75, 14.0))),
                     x=lerp(s["x"], DK_X, ease_in_out(seg(t, 13.75, 14.0))))
    elif t < 16.0:                    # watches the paw-bump, cuddling the teddy
        sw = math.sin(2 * math.pi * (t - 14.0) / 1.0)
        s.update(eyes="happy", beak="smile" if t < 15.4 else "grin", wl=38, wr=-38, hug=True, lean=4 * sw,
                 look=(7, -4))
        h, sq = hop_curve(t, 15.45, 15.7, 1, 16)
        s["hop"], s["sq"] = h, sq
    elif t < 16.35:                   # waves bye with BOTH wings... and lets go of the teddy
        wave = 18 * math.sin(2 * math.pi * (t - 16.0) / 0.3)
        up = ease_out(seg(t, 16.0, 16.15))
        s.update(eyes="happy", beak="grin", look=(7, -4), wl=lerp(38, -145 + wave, up), wr=lerp(-38, 145 - wave, up))
    else:                             # waddles off home, still waving, not noticing
        k = ease_in(seg(t, 16.4, 17.25))
        ph = (t - 16.4) / 0.3
        s.update(x=lerp(DK_X, -170, k), eyes="happy", beak="grin", look=(-7, 0),
                 lean=-4 + 6 * math.sin(2 * math.pi * ph) * seg(t, 16.4, 16.5),
                 hop=5 * abs(math.sin(math.pi * 2 * ph)) * seg(t, 16.4, 16.5),
                 wl=-10, wr=130 + 20 * math.sin(2 * math.pi * (t - 16.0) / 0.3))
    if s["hop"] == 0:
        s["sq"] *= breath(t, 1.5, 0.015)
    return s


def pip_hug_pt(pp):
    return PIP.anchor(pp["x"], GY, pp["hop"], pp["lean"])(0, -22 * pp["sq"])


def draw_pip(f, pp, t, teddy=None):
    blink = blinking(t, PIP_BLINKS) and not frozen(t)
    PIP.draw(f, pp["x"], GY, hop=pp["hop"], lean=pp["lean"], tilt=pp["tilt"], wing_l=pp["wl"], wing_r=pp["wr"],
             eyes=pp["eyes"], beak=pp["beak"], look=pp["look"], squash=pp["sq"], head_dy=pp["head_dy"],
             blink=blink, turn=pp["turn"], wings=not pp["hug"])
    if teddy is not None:
        teddy()
    if pp["hug"]:
        PIP.draw_wings(f, pp["x"], GY, pp["hop"], pp["lean"], pp["sq"], pp["wl"], pp["wr"], pp["turn"])


# ---------------------------------------------------------------- Crinkle
def crinkle_state(t):
    s = dict(x=CR_HOME, hop=0.0, sq=1.0, lean=0.0, tilt=0.0, arm_l=CR_REST_L, arm_r=2.0, eyes="normal",
             mouth="smile", look=(0, 0), head_dy=0.0, sign=0.0)
    if t < 6.0 or t >= 16.8:
        s["x"] = 1450
        return s
    if t < 8.0:                       # slides in, double-take at the teddy ears, shows the sign
        s["x"] = lerp(1450, CR_HOME, ease_out_back(seg(t, 6.0, 6.5), 1.2))
        s["lean"] = 12 * (1 - ease_out(seg(t, 6.0, 6.9)))
        if t < 6.75:
            s.update(eyes="wide" if t > 6.35 else "normal", mouth="o" if t > 6.35 else "smile", look=(-7, -7))
            s["head_dy"] = -10 * math.sin(math.pi * seg(t, 6.35, 6.6))
        else:
            s.update(eyes="normal", mouth="smile", look=(-6, -1), tilt=8 * ease_in_out(seg(t, 6.8, 7.1)))
        up = ease_out_back(seg(t, 6.7, 7.0)) * (1 - ease_in_out(seg(t, 7.7, 8.0)))
        s["arm_l"] = lerp(CR_REST_L, 194, up)
        s["sign"] = pop_scale(t, 6.8, 0.3) * (1 - ease_in_out(seg(t, 7.65, 7.9)))
        if t > 7.6:
            s["tilt"] = 8 * (1 - ease_in_out(seg(t, 7.6, 7.9)))
    elif t < 11.5:                    # looks around with Snip, then cheers Snip on
        if t < 8.4:
            k = ease_in_out(seg(t, 8.0, 8.3))
            s.update(lean=-5 * k, tilt=-6 * k, look=(8, -2))
        elif t < 8.8:
            k = ease_in_out(seg(t, 8.4, 8.7))
            s.update(lean=lerp(-5, 5, k), tilt=lerp(-6, 6, k), look=(-8, 3))
        else:
            k = ease_in_out(seg(t, 8.85, 9.2))
            s.update(lean=lerp(5, 0, k), tilt=lerp(6, 0, k), look=(-8, 4), eyes="happy" if 8.85 < t < 9.3 else "normal")
        for c in COUNTS:
            s["head_dy"] += 10 * math.sin(math.pi * seg(t, c, c + 0.3))
            if 0 <= t - c < 0.3:
                s["mouth"] = "o"
        if t > 10.75:
            s.update(eyes="happy", mouth="grin")
    elif t < 14.0:                    # hooray!
        s.update(eyes="happy", mouth="grin", look=(-7, 2))
        up = ease_out_back(seg(t, 11.65, 11.95)) * (1 - ease_in_out(seg(t, 13.5, 13.9)))
        wig = 12 * math.sin(2 * math.pi * (t - 11.65) / 0.45)
        s["arm_l"] = lerp(CR_REST_L, 215 - wig, up)
        s["arm_r"] = lerp(2, 145 + wig, up)
        h, sq = hop_curve(t, 12.8, 13.1, 1, 24)
        s["hop"], s["sq"] = h, sq
    elif t < 16.0:                    # paw-bump
        h, sq = hop_curve(t, 14.0, 14.5, 1, 20)
        s.update(x=lerp(CR_HOME, 755, ease_in_out(seg(t, 14.0, 14.5))), hop=h, sq=sq, eyes="happy", mouth="grin",
                 look=(-6, 0))
        wind = ease_in_out(seg(t, 15.0, 15.2))
        swing = ease_out_back(seg(t, 15.2, 15.45))
        s["arm_l"] = lerp(lerp(CR_REST_L, 360, wind), 198, swing)
    else:                             # waves bye and hops away
        h, sq = hop_curve(t, 16.05, 16.8, 2, 40)
        s.update(x=lerp(755, 1450, ease_in_out(seg(t, 16.05, 16.8))), hop=h, sq=sq, eyes="happy", mouth="grin",
                 lean=-6)
        s["arm_l"] = lerp(198, CR_REST_L, ease_out(seg(t, 16.0, 16.2)))
        s["arm_r"] = 140 + 22 * math.sin((t - 16.0) * 16)
    if s["hop"] == 0:
        s["sq"] *= breath(t + 0.7, 2.25, 0.01)
    return s


# ---------------------------------------------------------------- the teddy
def teddy_rise(t):
    """How far the hidden teddy pokes up behind Snip's head (px above the head pivot) + its wobble."""
    if t < 5.0:
        r = 60
    elif t < 5.15:
        r = 60 + 80 * ease_out_back(seg(t, 5.0, 5.15), 3.0)
    elif t < 5.35:
        r = lerp(140, 60, ease_in_out(seg(t, 5.15, 5.32)))
    elif t < 5.55:
        r = 60
    elif t < 6.75:
        r = 60 + 125 * ease_out_back(seg(t, 5.55, 5.72), 3.5)
    elif t < 7.35:
        r = lerp(185, 140, ease_in_out(seg(t, 6.75, 7.0)))
    else:
        r = lerp(140, 0, ease_in(seg(t, 7.35, 7.6)))
    wob = spring(t, 5.0, 10, 4.0, 5.0) + spring(t, 5.55, 16, 3.5, 2.6)
    return r, wob


def teddy_state(t, sn, pp):
    """(layer, x, y, angle, scale, squash_y). Layers: bench, snip (in Snip's arms), behind (between Snip's
    ears and face), pip (in Pip's wings), air (flying, drawn on top)."""
    bx, by = TEDDY_BENCH
    if t < 1.0 or t >= 16.8:
        sy = 1 - 0.12 * math.sin(math.pi * seg(t, 16.8, 16.98)) if t >= 16.8 else 1.0
        return ("bench", bx, by, 0.0, 1.0, sy)
    hx, hy = snip_hug_pt(sn)
    if t < 1.3:
        k = ease_in_out(seg(t, 1.0, 1.3))
        return ("snip", lerp(bx, hx, k), lerp(by, hy, k) - 50 * math.sin(math.pi * k), 10 * math.sin(math.pi * k),
                1.0, 1.0)
    if t < 4.62:
        return ("snip", hx, hy, sn["lean"], 1.0, 1.0)
    if t < 4.7:
        k = ease_in(seg(t, 4.62, 4.7))
        return ("snip", hx + 95 * k, hy - 10 * k, sn["lean"] - 15 * k, 1 - 0.25 * k, 1.0)
    if t < 7.6:
        return ("behind", 0, 0, 0, 1.0, 1.0)
    if t < 7.85:
        k = ease_out(seg(t, 7.6, 7.85))
        return ("snip", lerp(hx + 95, hx, k), lerp(hy - 10, hy, k), lerp(-15, sn["lean"], k), lerp(0.75, 1, k), 1.0)
    if t < 10.1:
        return ("snip", hx, hy, sn["lean"], 1.0, 1.0)
    tip = SNIP.paw_tip(sn["x"], GY, "l", sn["arm_l"], sn["hop"], sn["lean"], sn["sq"])
    hold = (tip[0] - 4, tip[1] + 72)
    if t < 10.5:
        k = ease_in_out(seg(t, 10.1, 10.45))
        return ("snip", lerp(hx, hold[0], k), lerp(hy, hold[1], k), sn["lean"] * (1 - k) + 6 * k, 1.0, 1.0)
    px, py = pip_hug_pt(pp)
    if t < 10.8:
        k = ease_in_out(seg(t, 10.5, 10.75))
        s5 = snip_state(10.5)
        tip_g = SNIP.paw_tip(s5["x"], GY, "l", s5["arm_l"], s5["hop"], s5["lean"], s5["sq"])
        h0 = (tip_g[0] - 4, tip_g[1] + 72)
        return ("pip", lerp(h0[0], px, k), lerp(h0[1], py, k), lerp(6, pp["lean"], k), lerp(1, PIP_TEDDY_S, k), 1.0)
    if t < 16.2:
        return ("pip", px, py, pp["lean"], PIP_TEDDY_S, 1.0)
    p0 = pip_state(16.2)
    x0, y0 = pip_hug_pt(p0)
    k = seg(t, 16.2, 16.8)
    return ("air", lerp(x0, bx, k), lerp(y0, by, k) - 300 * math.sin(math.pi * k), 360 * ease_in_out(k),
            lerp(PIP_TEDDY_S, 1.0, k), 1.0)


def draw_teddy(f, st, sx=1.0):
    _, x, y, ang, sc, sy = st
    place(f, TEDDY, (x, y), angle=ang, scale=sc, sx=sx, sy=sy)


# ---------------------------------------------------------------- frame
def render_frame(t):
    f = BG.copy()
    place(f, SUN, (880, 230), angle=30 * t / DUR)
    for spr, x, y, ph in CLOUDS:
        place(f, spr, (x + 18 * math.sin(2 * math.pi * t / DUR + ph), y + 4 * math.sin(4 * math.pi * t / DUR + ph)))
    place(f, CANOPY, (210 + 5 * math.sin(2 * math.pi * t / 6.0), 420 + 2 * math.sin(4 * math.pi * t / 6.0)))

    sn, cr, pp = snip_state(t), crinkle_state(t), pip_state(t)
    td = teddy_state(t, sn, pp)

    # teddy on the bench (behind everyone) + the hook's twinkle
    if td[0] == "bench":
        draw_teddy(f, td)

    # Snip (with the teddy tucked between ears and face when it's hidden "behind")
    between = None
    if td[0] == "behind":
        rise, wob = teddy_rise(t)

        def between(hx, hy, ha):
            dx, dy = rot(0, -rise, ha)
            place(f, TEDDY, (hx + dx, hy + dy), angle=ha + wob)
    draw_snip(f, sn, t, between)
    if td[0] == "snip":
        draw_teddy(f, td)
        place(f, SNIP.arm_l, SNIP.shoulder_pt(sn["x"], GY, "l", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_l"] + sn["lean"])
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], GY, "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])

    # desire hearts from the hug
    for i, t0 in enumerate((1.45, 1.8)):
        if t0 <= t < 2.5:
            p = seg(t, t0, 2.5)
            hx, hy = snip_hug_pt(sn)
            place(f, SMALL_HEARTS[i], (hx + (-60 if i else 60) + 8 * math.sin(t * 4 + i), hy - 200 - 170 * p),
                  scale=pop_scale(t, t0, 0.25), alpha=1 - ease_in_out(seg(t, 2.2, 2.5)), angle=12 * math.sin(t * 3 + i))

    # Crinkle (sign held behind his paw)
    cr_tip = CR.paw_tip(cr["x"], GY, "l", cr["arm_l"], cr["hop"], cr["lean"], cr["sq"])
    if cr["sign"] > 0.01:
        place(f, SIGN, (cr_tip[0] + 30, cr_tip[1] - 70), scale=0.9 * cr["sign"], angle=3 * math.sin(t * 5))
    CR.draw(f, cr["x"], GY, hop=cr["hop"], lean=cr["lean"], head_tilt=cr["tilt"], arm_l=cr["arm_l"],
            arm_r=cr["arm_r"], eyes=cr["eyes"], mouth=cr["mouth"], look=cr["look"], squash=cr["sq"],
            head_dy=cr["head_dy"], blink=blinking(t, CR_BLINKS) and not frozen(t))

    # Pip in front (she's small, and her face carries the lesson)
    if pp["on"]:
        turn_k = abs(pp["turn"])
        draw_pip(f, pp, t, (lambda: draw_teddy(f, td, turn_k)) if td[0] == "pip" else None)

    # paw-bump: both touching paws in front
    if 14.95 <= t < 16.1:
        place(f, SNIP.arm_r, SNIP.shoulder_pt(sn["x"], GY, "r", sn["hop"], sn["lean"], sn["sq"]),
              angle=sn["arm_r"] + sn["lean"])
        place(f, CR.arm_l, CR.shoulder_pt(cr["x"], GY, "l", cr["hop"], cr["lean"], cr["sq"]),
              angle=cr["arm_l"] + cr["lean"])

    if td[0] == "air":
        draw_teddy(f, td)

    # Pip's sad thought: her teddy
    if pp["on"] and 2.1 <= t < 9.75:
        hx, hy = PIP.head_pivot(pp["x"], GY, pp["hop"], pp["lean"], pp["sq"], pp["head_dy"])
        k = pop_scale(t, 2.1, 0.3) * (1 - ease_in_out(seg(t, 9.45, 9.75)))
        k *= 1 + 0.15 * math.sin(math.pi * seg(t, 8.85, 9.2))
        place(f, THOUGHT, (hx - 8, hy - 186 + 5 * math.sin(2 * math.pi * t / 1.5)), scale=k)

    # pop sparkles where the teddy pokes up
    for t0 in (5.0, 5.55):
        if t0 <= t < t0 + 0.4:
            hx, hy = SNIP.head_pivot(sn["x"], GY, sn["hop"], sn["lean"], sn["sq"], sn["head_dy"])
            place(f, SPARKLE, (hx + 95, hy - 320), scale=0.32 * pop_scale(t, t0, 0.15),
                  alpha=1 - ease_in_out(seg(t, t0 + 0.2, t0 + 0.4)), angle=(t - t0) * 90)

    # hook twinkle on the teddy (wraps across the loop point)
    tw = (t - 17.55) % DUR
    if tw < 1.35:
        place(f, SPARKLE, (TEDDY_BENCH[0] + 62, TEDDY_BENCH[1] - 150), scale=0.26 * math.sin(math.pi * tw / 1.35),
              angle=tw * 70)

    # counting numerals
    for i, c in enumerate(COUNTS):
        if c <= t < c + 0.95:
            out = 1 - ease_in_out(seg(t, c + 0.75, c + 0.95))
            place(f, NUMS[i], (560, 660), scale=pop_scale(t, c, 0.28) * out, angle=-6 + 4 * math.sin(t * 6))

    if 11.5 <= t < 12.3:
        place(f, CHECK, (DK_X + 10, 985), scale=pop_scale(t, 11.5, 0.25) * (1 - ease_in_out(seg(t, 12.05, 12.3))))

    for i, (t0, x, y) in enumerate(HEART_PLAN):
        if t0 <= t < 14.1:
            p = seg(t, t0, 14.1)
            place(f, HEARTS[i], (x + 10 * math.sin(t * 3 + i), y - 170 * p), scale=pop_scale(t, t0, 0.25),
                  alpha=1 - ease_in_out(seg(t, 13.7, 14.1)), angle=10 * math.sin(t * 2.5 + i))

    if 15.45 <= t < 16.2:
        sn_tip = SNIP.paw_tip(sn["x"], GY, "r", sn["arm_r"], sn["hop"], sn["lean"], sn["sq"])
        c_tip = CR.paw_tip(cr["x"], GY, "l", cr["arm_l"], cr["hop"], cr["lean"], cr["sq"])
        mid = ((sn_tip[0] + c_tip[0]) / 2, (sn_tip[1] + c_tip[1]) / 2 - 10)
        place(f, SPARKLE, (mid[0], mid[1] - 35), scale=pop_scale(t, 15.45, 0.22) * 0.55, angle=(t - 15.45) * 60,
              alpha=1 - ease_in_out(seg(t, 15.9, 16.2)))

    # FREEZE: dim + choice bubbles (keep it? / give it back?)
    if 2.5 <= t < 4.6:
        dim = 0.32 * ease_in_out(seg(t, 2.5, 2.8)) * (1 - ease_in_out(seg(t, 4.35, 4.6)))
        if dim > 0.01:
            f.alpha_composite(Image.new("RGBA", f.size, (30, 26, 52, int(255 * dim))))
        gone = 1 - ease_in_out(seg(t, 4.4, 4.55))
        pulse_a = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 2.95) / 1.0))
        pulse_b = 1 + 0.12 * max(0.0, math.sin(2 * math.pi * (t - 3.45) / 1.0))
        place(f, BUB_KEEP, (300, 600), scale=pop_scale(t, 2.55) * gone * (pulse_a if t > 2.95 else 1))
        place(f, BUB_GIVE, (780, 600), scale=pop_scale(t, 2.7) * gone * (pulse_b if t > 3.45 else 1))
        place(f, QMARK, (540, 520), scale=pop_scale(t, 2.85, 0.25) * gone, angle=8 * math.sin(t * 4))

    return camera(f, t)


CAM_KEYS = [
    (0.0, 1.6, 320, 1140), (1.0, 1.63, 320, 1140), (1.5, 1.15, 430, 1090), (2.4, 1.15, 430, 1090),
    (2.8, 1.0, 540, 960), (4.6, 1.0, 540, 960), (4.85, 1.28, 410, 1060), (5.9, 1.28, 410, 1060),
    (6.35, 1.0, 540, 960), (8.0, 1.0, 540, 960), (8.3, 1.05, 600, 980), (8.7, 1.05, 470, 980),
    (9.2, 1.0, 540, 960), (9.9, 1.0, 540, 960), (10.3, 1.12, 400, 1080), (11.3, 1.12, 400, 1080),
    (11.9, 1.08, 470, 1030), (13.8, 1.08, 470, 1030), (14.3, 1.0, 540, 960), (15.2, 1.0, 540, 960),
    (15.45, 1.12, 580, 1060), (15.9, 1.12, 580, 1060), (16.3, 1.0, 540, 960), (17.0, 1.0, 540, 960),
    (DUR, 1.6, 320, 1140)]


def camera(f, t):
    z, cx, cy = 1.0, 540, 960
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
    if 5.55 <= t < 5.85:              # a little bump on the BOING
        k = 1 - seg(t, 5.55, 5.85)
        cy += 8 * k * math.sin(t * 90)
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
    # park birds, soft, scattered (and a quiet bed so there is never dead air)
    for tt, b in ((0.55, 3000), (3.15, 3300), (5.95, 2900), (7.05, 3200), (9.95, 3100), (14.15, 3300),
                  (16.95, 3000)):
        sfx.add(tt, PP.chirp(0.7, b))
    # hook: tiptoes toward the teddy
    A.jingle(music, 0.02)
    for i, tt in enumerate((0.12, 0.62)):
        music.add(tt, A.pluck(M(67 + 2 * i), 0.25, 0.5))
    sfx.add(0.3, A.twinkle(0.35, (103, 107, 110)))
    # desire: scoop + squeeze + warm strums
    sfx.add(1.0, A.pop(0.6))
    sfx.add(1.05, A.whoosh(0.3, 0.4))
    sfx.add(1.32, PP.squeak(0.9))
    sfx.add(1.35, A.twinkle(0.8))
    for tt, ch, up in ((1.0, "F", False), (1.25, "F", True), (1.5, "C", False), (1.75, "C", True)):
        A.strum(music, tt, ch, 0.7, up)
    music.add(1.0, A.bass(M(41), 0.5, 0.7))
    music.add(1.5, A.bass(M(48), 0.5, 0.7))
    for tt in (1.45, 1.8):
        sfx.add(tt, A.pop(0.4))
    # Pip waddles in, sad
    tt = 1.6
    while tt < 2.35:
        sfx.add(tt, A.tap(0.35))
        tt += 0.18
    A.strum(music, 2.0, "Am", 0.55)
    music.add(2.0, A.bass(M(45), 0.5, 0.6))
    sfx.add(2.12, A.pop(0.5))
    sfx.add(2.15, PP.sad_coo(0.9))
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
    # slapstick: whip it behind, whistle, pop, push, BOING
    sfx.add(4.6, A.whoosh(0.25, 0.9))
    sfx.add(4.8, PP.whistle(((84, 0.12), (88, 0.1), (83, 0.18)), 0.9))
    for i, m in enumerate((55, 59, 62, 59)):
        music.add(4.75 + i * 0.12, A.pluck(M(m), 0.25, 0.45))
    sfx.add(5.0, A.pop(0.9))
    sfx.add(5.0, A.boing(0.6, 380))
    sfx.add(5.17, A.tap(0.8))
    sfx.add(5.36, PP.whistle(((86, 0.1), (83, 0.12)), 0.7))
    sfx.add(5.55, A.boing(1.0, 300))
    sfx.add(5.55, A.snare_roll(0.12, 0.7))
    sfx.add(5.56, PP.squeak(0.6))
    sfx.add(5.78, PP.slide_whistle(False, 0.4, 0.7))
    music.add(5.8, A.pluck(M(50), 0.4, 0.5))
    music.add(5.95, A.pluck(M(47), 0.5, 0.5))
    # Crinkle: arrives, double-take, "whose toy?" sign, Snip nods
    sfx.add(5.98, A.whoosh(0.5, 1.0))
    sfx.add(6.38, A.boing(0.35, 420))
    sfx.add(6.85, A.pop(0.7))
    sfx.add(6.88, A.glock(M(88), 1.0, 0.7))
    sfx.add(7.02, A.glock(M(91), 1.0, 0.6))
    for tt, ch in ((6.6, "Dm"), (7.1, "G"), (7.6, "C")):
        A.strum(music, tt, ch, 0.55)
        music.add(tt, A.bass(M({"Dm": 50, "G": 43, "C": 48}[ch]), 0.5, 0.6))
    for tt in (6.97, 7.3):
        sfx.add(tt, A.tap(0.5))
    sfx.add(7.6, A.whoosh(0.3, 0.6))
    sfx.add(7.8, PP.squeak(0.5))
    # 1-2-3: look around, go to the owner, give it back
    sfx.add(8.02, A.whoosh(0.3, 0.35))
    sfx.add(8.42, A.whoosh(0.3, 0.35))
    sfx.add(8.85, A.twinkle(0.6))
    sfx.add(8.9, PP.quack(0.8, 1.15))
    tt, k = 8.0, 0
    while tt < 11.0:
        sfx.add(tt, A.woodblock(k % 2 == 0, 0.35))
        tt += 0.5
        k += 1
    for c, m in zip(COUNTS, (84, 88, 91)):
        sfx.add(c, A.glock(M(m), 1.2, 0.9))
        music.add(c, A.ks_pluck(M(m - 24), 1.0, 0.8))
        music.add(c, A.bass(M(48), 0.4, 0.5))
    sfx.add(9.27, A.boing(0.4, 330))
    sfx.add(10.1, A.whoosh(0.25, 0.4))
    sfx.add(10.5, A.pop(0.7))
    sfx.add(10.55, PP.squeak(0.8))
    sfx.add(10.6, A.chime_up(0.9))
    sfx.add(10.82, PP.quack(0.9, 1.1))
    sfx.add(11.02, PP.quack(0.8, 1.25))
    music.add(10.8, A.pad([M(60), M(64), M(67)], 1.0, 0.45))
    # payoff: check, happy dance, hearts
    sfx.add(11.5, A.glock(M(96), 1.0, 0.7))
    sfx.add(11.52, A.twinkle(0.7))
    for tt, ch, up in ((11.6, "C", False), (11.825, "C", True), (12.05, "G", False), (12.275, "G", True),
                       (12.5, "Am", False), (12.725, "Am", True), (12.95, "F", False), (13.175, "F", True),
                       (13.4, "C", False), (13.625, "G", True)):
        A.strum(music, tt, ch, 0.8, up)
    for tt, m in ((11.6, 48), (12.05, 43), (12.5, 45), (12.95, 41), (13.4, 48), (13.625, 43)):
        music.add(tt, A.bass(M(m), 0.4, 0.8))
    for i, c in enumerate(DANCE_HOPS):
        sfx.add(c, PP.quack(0.75, 1.0 + 0.08 * (i % 2)))
        sfx.add(c + 0.02, A.clap(0.7))
    sfx.add(13.3, PP.slide_whistle(True, 0.45, 0.6))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.4))
    sfx.add(12.35, A.boing(0.3, 340))
    # paw-bump
    sfx.add(14.0, A.boing(0.35, 300))
    sfx.add(14.85, A.snare_roll(0.6, 0.8))
    sfx.add(15.45, A.boop(0.9))
    A.jingle(music, 15.47, 1.0, ending=True)
    sfx.add(15.5, A.twinkle(0.8))
    # bye-bye wave... the teddy flies back onto the bench... uh-oh!
    sfx.add(16.0, PP.quack(0.7, 1.15))
    sfx.add(16.05, A.boing(0.35, 300))
    sfx.add(16.42, A.boing(0.3, 330))
    sfx.add(16.2, PP.slide_whistle(True, 0.3, 0.6))
    sfx.add(16.5, PP.slide_whistle(False, 0.3, 0.6))
    sfx.add(16.8, PP.flump(1.0))
    tt = 16.45
    while tt < 17.2:
        sfx.add(tt, A.tap(0.25))
        tt += 0.15
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
    wav = os.path.join(ROOT, "build", "ep04_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep04_whose_toy_is_this.mp4")
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
    times = times or [0.0, 1.0, 2.0, 3.4, 4.9, 5.2, 5.7, 6.5, 7.2, 8.6, 9.5, 10.6, 11.2, 11.8, 12.6, 13.5,
                      15.6, 16.4, 16.7, 17.5, 17.99]
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


KEY_TIMES = (0.0, 2.1, 3.4, 5.7, 7.2, 10.6, 12.6, 15.6)


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
        p = os.path.join(ROOT, "build", f"ep04_f{tt:05.2f}.png")
        render_frame(tt).convert("RGB").resize((w, int(w * 16 / 9)), Image.LANCZOS).save(p)
        print("wrote", p)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    if "--stills" in sys.argv:
        stills(os.path.join(ROOT, "build", "ep04_stills.png"))
    elif "--keys" in sys.argv:
        os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
        keys(os.path.join(ROOT, "reviews", "ep04_keys.png"))
    elif "--frames" in sys.argv:
        frames([float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")])
    else:
        render(os.path.join(ROOT, "output"))
