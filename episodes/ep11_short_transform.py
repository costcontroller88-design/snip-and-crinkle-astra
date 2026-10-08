"""Episode 11 transformation Short (reviews/ep11_short_plan.md, r3): "Plain Pumpkin Becomes a Glowing Friend!"

30.0 s, vertical 1080x1920, its own performances on the Episode 11 porch (early-evening light all through). Lesson:
when it's a friend's turn, wait until they finish; then it's your turn. One marker (black ink, blue body) passes
Snip -> Crinkle (the take) -> Snip (given back) -> Pip -> Crinkle; the grown-up's hand puts a battery tea light in the
paper lantern (props_lantern) and the whole paper glows.

Run:  python3 episodes/ep11_short_transform.py --still T     (one frame through the shot camera -> build/ep11s/)
      python3 episodes/ep11_short_transform.py --keys        (risky-shot check sheet -> reviews/ep11_short_transform_keys.png)
      python3 episodes/ep11_short_transform.py --cuts        (cut times for check_video)
      python3 episodes/ep11_short_transform.py --check       (measured clearances and gaps, printed)
      EP11S_RES=3 python3 episodes/ep11_short_transform.py --hires   (cameras T 2.6x and G 2.5x, at 3x ->
                                                                    build/ep11s_hi/; run it before --render)
      python3 episodes/ep11_short_transform.py --audio       (sound only -> build/ep11s_audio.wav)
      python3 episodes/ep11_short_transform.py --render      (audio + video -> output/ep11_short_transform.mp4)
Any other flag is refused.

    render_world(t, d, cam=CAM, bg=None)   # the world at time t, drawing d (RGBA, the vertical world strip)
    make_buses()                           # (music, sfx) Mix buses
    render_frame(t, view="vert")           # one finished 1080x1920 frame (for acting.render_video)
"""
import hashlib
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

import hires  # noqa: E402

hires.set_res(float(os.environ.get("EP11S_RES", "2")))     # 3 only for the separate T / G pass (--hires)

import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont  # noqa: E402

import acting as K  # noqa: E402
import audio as A  # noqa: E402
import ep11_light as L  # noqa: E402
import music_extra as MX  # noqa: E402
import props_glow as G  # noqa: E402
import props_hand2 as H  # noqa: E402
import props_lantern as PL  # noqa: E402
import props_porch as P  # noqa: E402
import props_pumpkin as PK  # noqa: E402
import rig2 as R  # noqa: E402
import rig2_pip as RP  # noqa: E402
from hires import RCut  # noqa: E402
from paperlib import ease_in_out, lerp, place, rot, seg  # noqa: E402

RES = hires.RES
DUR = 30.0
SQUEAK_VEL = 1.0                        # R3-1: the big squeak's level (measured against the end chord)
FLOOR = P.FLOOR_Y
CAM = K.Cam("vert", P.WORLD_W, P.WORLD_H, P.LAND_Y0, P.VERT_X0, res=RES)
WORLD = P.Porch(CAM)
LANTERN = PL.Lantern()
BASE = PL.BASE
GLOW_C = (BASE[0], BASE[1] - 75)
T_LIGHT = 95.0                         # the episode's early-evening light state (before its own glow)
DUSK_SET = (0.62, 0.62, 0.74)          # early-evening dimming of the set
DUSK_CHAR = (0.80, 0.79, 0.88)         # characters keep more of their colour
OUT_DIR = os.path.join(ROOT, "build", "ep11s")
HI_DIR = os.path.join(ROOT, "build", "ep11s_hi")


def _unit(dx, dy):
    n = math.hypot(dx, dy)
    return dx / n, dy / n


def _ease(t, keys):
    """Piecewise eased value [(t, v), ...] (numbers or points)."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            if isinstance(v0, tuple):
                return lerp(v0[0], v1[0], k), lerp(v0[1], v1[1], k)
            return lerp(v0, v1, k)
    return keys[-1][1]


def _lin(t, keys):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            return lerp(v0, v1, seg(t, t0, t1))
    return keys[-1][1]


# ---------------------------------------------------------------- the one marker
MK_S = 1.1
MK = RP.marker_sprite(body=(96, 170, 236), ink=PK.INK, scale=MK_S)
TIP_L = RP.MARKER_TIP * MK_S            # grip point -> tip
CAP = 46.0                              # r1: a pinch at the very top end: the paw this far behind the grip point
U_SN, U_PIP, U_CR = _unit(0.39, 0.92), _unit(-0.22, 0.98), _unit(-0.3, 0.95)
U_GIVE = _unit(0.97, -0.24)             # Pip holds it up to Crinkle, pointing at his paw (tip away from every face)
ANG = {k: RP.marker_angle(u) for k, u in (("sn", U_SN), ("pip", U_PIP), ("cr", U_CR), ("give", U_GIVE))}
A_HANG, A_HOLD, A_FLAT, A_REST = 40.0, -12.0, 90.0, 80.0    # A_FLAT: lying flat, tip pointing right (away)
A_BELLY = RP.marker_angle(_unit(-0.45, 0.89))    # r2 (R3-2): at belly height, tip down-left at the lantern
C = PL.C_STOP

STROKE_KEYS = {"eye_l": [(0.0, 0.30), (0.6, 0.50), (0.9, C), (10.7, C), (11.2, 1.0)],
               "eye_r": [(12.2, 0.0), (12.6, 1.0)],
               "heart_l": [(14.4, 0.0), (15.0, 1.0)], "heart_r": [(15.1, 0.0), (15.7, 1.0)],
               "smile": [(18.4, 0.0), (20.0, 1.0)]}


def strokes_at(t):
    out = {}
    for name, keys in STROKE_KEYS.items():
        if t >= keys[0][0]:
            out[name] = _lin(t, keys)
    return out


def follow(perf, side, name, t0, t1, f0, f1, u, off=0.0, lead=0.0, n=None):
    """The paw follows the marker tip along stroke `name` (fraction f0 -> f1, t0 -> t1), marker pointing along u."""
    Lm = TIP_L + off

    def grip(f):
        x, y = PL.tip_world(name, f)
        return x - Lm * u[0], y - Lm * u[1]
    if lead:
        perf.reach(t0 - lead, t0, side, grip(f0), "io")
    n = n or max(4, int((t1 - t0) * 16))
    for i in range(n):
        ta, tb = t0 + (t1 - t0) * i / n, t0 + (t1 - t0) * (i + 1) / n
        perf.reach(ta, tb, side, grip(lerp(f0, f1, (i + 1) / n)), "lin")


# ---------------------------------------------------------------- performers
SN = R.Perf2(R.Puppet("snip", 1.15), seed=1, x=790, y=FLOOR, turn=0.5, eyes="normal", mouth="smile", brows="think",
             look_x=4, look_y=6)
CR = R.Perf2(RP.crinkle(1.2), seed=2, x=1080, y=FLOOR, turn=-0.5, eyes="sparkle", mouth="smile_open", brows="up",
             look_x=-6, look_y=6, arm_l=150, elb_l=-110, arm_r=-150, elb_r=110)
PIPA = RP.PipPuppet(0.9)
PIP = RP.PipPerf(PIPA, seed=3, x=640, y=FLOOR, turn=0.3, eyes="normal", mouth="smile", look_x=6, look_y=6,
                 arm_l=25, arm_r=-25)
BACK = {"pip": [(-1.0, 12.9)], "cr": [(6.9, 17.1)], "sn": []}       # paws / wings behind the back (T2)
SN_X1, PIP_X1, CR_X1, CR_XW = 700, 740, 1260, 1100                  # after the turns; CR_XW: his waiting spot
SN_X2 = 660                                                         # r3: Snip's spot from 22.8 (hand gap)
BELLY_D = (36, 1372)                                                # r3: belly height, paw clear of the lantern

# ---- shot 1 + 1b (0-2.8): Snip draws; Crinkle bounces, leans in and takes the marker (the take, camera T 2.6x)
SN.reach(-0.3, 0.0, "r", (PL.tip_world("eye_l", 0.30)[0] - TIP_L * U_SN[0],
                          PL.tip_world("eye_l", 0.30)[1] - TIP_L * U_SN[1]))
follow(SN, "r", "eye_l", 0.0, 0.6, 0.30, 0.50, U_SN)
follow(SN, "r", "eye_l", 0.6, 0.9, 0.50, C, U_SN)
W_SN = SN.paw(0.9, "r")[0]                                          # her paw stays exactly here until 5.9
for _t in np.arange(0.9, 5.89, 0.2):                                # (re-aimed every 0.2 s: breathing never moves it)
    SN.reach(float(_t), float(min(5.9, _t + 0.2)), "r", W_SN, "lin")
CAP_P = (W_SN[0] - CAP * U_SN[0], W_SN[1] - CAP * U_SN[1])          # the marker's very top end (where he pinches)
SLID = (CAP_P[0] - 70 * U_SN[0], CAP_P[1] - 70 * U_SN[1])           # 1.2-1.9: slid up along its own axis
LIFT = (1010, 1262)                                                 # tip stays above the paper
CR.hop(0.0, 0.3, 1, 6)
CR.to(0.3, 0.6, "io", lean=-10, sq=0.92)
CR.reach(0.3, 0.6, "l", (CAP_P[0] + 40, CAP_P[1] - 24))             # in from the upper right
CR.reach(0.6, 0.9, "l", CAP_P, "io")                                # slow pinch at the top end (no tug)
for _t in np.arange(0.9, 1.19, 0.1):                                # both paws on it, still (0.9-1.2)
    CR.reach(float(_t), float(min(1.2, _t + 0.1)), "l", CAP_P, "lin")
for _i in range(7):                                                 # slides up along its own axis out of her open
    _k0, _k1 = ease_in_out(_i / 7), ease_in_out((_i + 1) / 7)       # fingers (re-aimed every 0.1 s: never sideways)
    CR.reach(1.2 + 0.1 * _i, 1.3 + 0.1 * _i, "l", (lerp(CAP_P[0], SLID[0], _k1), lerp(CAP_P[1], SLID[1], _k1)), "lin")
CR.reach(1.9, 2.3, "l", LIFT, "io")                                 # carried up and right, eyes on the lantern
CR.face(0.85, eyes="normal", mouth="smile", brows="up").to(0.7, 0.9, "io", look_x=-10, look_y=8)   # R1
SN.face(1.25, mouth="o", brows="up").to(1.9, 2.1, "io", look_x=8, look_y=9)   # eyes: the C, then her empty paw
SN.ears(2.9, 3.3, "sad").to(3.0, 3.4, "io", head_dy=4, look_x=4, look_y=6)   # looks at the eye, not at him
SN.face(3.1, eyes="glassy", brows="sad", mouth="frown").face(5.5, eyes="normal")
# ---- shot 2 (2.8-6.5, B2): he crouches to draw; looks; understands; gives it back; bows
TIP_CR = (1018, 1418)                                               # 20 short of the smile's end: no mark
P_DRAW = (TIP_CR[0] - (TIP_L + CAP) * U_CR[0], TIP_CR[1] - (TIP_L + CAP) * U_CR[1])
CR.to(2.8, 3.2, "io", lean=-8, sq=0.94).face(2.8, eyes="normal", mouth="smile", brows="up")   # no tongue (R1)
CR.reach(2.8, 3.2, "l", P_DRAW)
CR.to(2.8, 3.0, "io", look_x=-10, look_y=4)
CR.to(3.2, 3.35, "io", look_x=-13, look_y=9)                         # the half eye (held 3.2-3.75)
CR.to(3.75, 3.9, "io", look_x=-10, look_y=-10)                       # Snip's teary face (held to 4.25)
CR.face(4.25, mouth="o", brows="sorry").to(4.25, 4.5, "io", sq=0.97, head_dy=5, lean=-6)
CR.reach(4.5, 5.4, "l", CAP_P, "io")                                 # slowly back: tip onto the line's end
CR.face(5.2, eyes="normal", mouth="smile", brows="sorry")
CR_HP = CR.a.head_pivot(CR.state(5.3))
CHEST = (CR_HP[0] + 22, CR_HP[1] + 110)                             # r2: >= 40 clear of the marker by 5.55
CR.reach(5.4, 5.8, "l", CHEST, "out")                                # lets go at 5.4: open paw straight to his chest
CR.to(5.8, 6.0, "io", lean=-9, head_dy=14).to(6.0, 6.2, "io", lean=-7, head_dy=4)   # a small bow
SN.to(5.4, 5.6, "io", look_x=4, look_y=9)                            # the marker back in her paw
SN.ears(6.0, 6.2, "happy", "back").face(6.0, eyes="happy", mouth="smile", brows="calm")
SN.to(6.2, 6.3, "io", head_dy=10).to(6.3, 6.4, "io", head_dy=0)     # nod
# ---- shot 3 (6.5-9.6, A): he copies Pip's waiting pose; gag 1 (G4): two sways, still, the third swings him round
CR.to(6.5, 6.9, "io", lean=0, sq=1.0, head_dy=0, turn=-0.35).walk(6.5, 6.9, CR_XW, steps=1)
CR.face(6.6, eyes="happy", mouth="smile", brows="calm").to(6.6, 6.8, "io", look_x=-12, look_y=2)
CR.to(6.7, 6.9, "io", arm_l=-10, elb_l=0, arm_r=10, elb_r=0)        # r3 (R4-1): paws hidden behind his body
t = 0.0
while t < 6.6:                                                        # Pip's small waiting sway
    PIP.to(t, t + 0.55, "io", lean=3 if int(t / 0.55) % 2 == 0 else -3)
    t += 0.55
PIP.to(6.6, 6.9, "io", lean=0)
for a, b, k in ((6.9, 7.4, 1), (7.4, 7.9, -1), (7.9, 8.4, 0)):       # two sways side by side, in time
    CR.to(a, b, "io", lean=6 * k)
    PIP.to(a, b, "io", lean=4 * k)
CR.to(8.8, 9.1, "io", turn=0.0, lean=-10).wiggle(9.1, "tilt", 3, 5.0, 6.0)  # the third swings him a quarter round
                                                                     # (r3: lean -10 = away from the lantern)
CR.to(9.4, 9.6, "io", turn=-0.35, lean=0)                            # ... and back, feet down
PIP.to(8.8, 9.2, "io", lean=4).to(9.2, 9.6, "io", lean=0)            # Pip's third sway stays small
PIP.to(6.6, 6.8, "io", look_x=10, look_y=0, hturn=0.25).face(6.8, eyes="happy", mouth="smile", brows="calm")
PIP.to(8.3, 8.5, "io", look_x=8, look_y=8, hturn=0.0).face(8.4, eyes="normal", mouth="smile", brows="calm")
SN.reach(6.5, 6.8, "r", (W_SN[0] - 6, W_SN[1] - 16))                 # tip just off the paper while she watches
SN.to(6.5, 6.7, "io", look_x=10, look_y=0).face(8.6, eyes="normal", mouth="smile", brows="calm")   # R3-4
# ---- shot 4 (9.6-10.6, K): his sheepish grin at once, blink, one belly bounce
CR.face(9.6, eyes="happy", mouth="smile_open", brows="sorry").blink(9.85)
CR.hop(9.8, 10.2, 1, 8)
CR.face(10.3, eyes="normal", mouth="smile", brows="calm").to(10.3, 10.5, "io", look_x=-10, look_y=8)
t = 10.6
while t < 16.8:                                                       # keeps swaying gently while he waits
    CR.to(t, t + 0.7, "io", lean=-3 if int((t - 10.6) / 0.7) % 2 == 0 else 3)
    t += 0.7
PIP.face(9.7, eyes="happy", mouth="smile", brows="calm")
t = 9.6
while t < 12.6:
    PIP.to(t, t + 0.55, "io", lean=3 if int((t - 9.6) / 0.55) % 2 == 0 else -3)
    t += 0.55
SN.face(9.7, eyes="happy", mouth="smile", brows="calm").to(10.3, 10.5, "io", look_x=4, look_y=6)
SN.face(10.4, eyes="normal", brows="think")
# ---- shot 5 (10.6-12.8, B): Snip closes the C into an O, then the second eye, quicker
follow(SN, "r", "eye_l", 10.7, 11.2, C, 1.0, U_SN, lead=0.2, n=8)
SN.face(11.25, eyes="happy", mouth="smile", brows="calm")
SN.reach(11.3, 11.6, "r", (SN.paw(11.2, "r")[0][0] - 4, SN.paw(11.2, "r")[0][1] - 14))
SN.face(11.9, eyes="normal", brows="think")
follow(SN, "r", "eye_r", 12.2, 12.6, 0.0, 1.0, U_SN, lead=0.3, n=8)
SN.face(12.65, eyes="sparkle", mouth="smile_open", brows="up").reach(12.62, 12.85, "r", (860, 1305))
# ---- shot 6 (12.8-14.3, A): Snip gives the marker to Pip, steps back, sweeps a paw; Pip waddles in
M_GIVE = (755, 1404)                              # keys1 K2: low, >= 30 from Pip's face
SN.to(12.8, 13.05, "io", turn=-0.3, look_x=-8, look_y=6).face(12.85, eyes="happy", mouth="smile_open", brows="up")
SN.reach(12.85, 13.15, "r", M_GIVE)
PIP.to(12.75, 12.9, "io", arm_l=-12, elb_l=16, arm_r=12, elb_r=-16).face(12.9, eyes="sparkle", mouth="smile_open")
PIP_TAKE = (M_GIVE[0] + 18, M_GIVE[1])           # the marker is held flat for the give
PIP.reach(12.95, 13.2, "r", PIP_TAKE)
SN.reach(13.25, 13.45, "r", (770, 1360)).walk(13.3, 13.8, SN_X1, steps=2)
SN.to(13.4, 13.7, "io", turn=0.35, look_x=8, look_y=6)
SN.reach(13.55, 13.85, "r", (820, 1300), "back").reach(14.1, 14.4, "r", (760, 1395))
PIP.walk(13.4, 14.2, 830, steps=4).to(14.2, 14.35, "io", turn=0.3, look_x=10, look_y=10)
PIP.reach(13.3, 13.6, "r", (742, 1402))                             # carried flat, low in front of her tummy (K2)
H_WAIT, H_PIP = (968, 1332), (975, 1322)
# ---- shot 7 (14.3-16.7, B): Pip draws the heart nose (black), her own tongue-tip concentration
PIP.to(14.1, 14.4, "io", tilt=7).to(15.75, 16.1, "io", tilt=0)            # head tipped away from the marker
follow(PIP, "r", "heart_l", 14.4, 15.0, 0.0, 1.0, U_PIP, lead=0.25, n=10)
PIP.reach(15.0, 15.1, "r", (PL.tip_world("heart_r", 0)[0] - TIP_L * U_PIP[0],
                            PL.tip_world("heart_r", 0)[1] - TIP_L * U_PIP[1]))
follow(PIP, "r", "heart_r", 15.1, 15.7, 0.0, 1.0, U_PIP, n=10)
for tt, m in ((14.45, "yum"), (14.8, "yum_l"), (15.15, "yum"), (15.5, "yum_l")):
    PIP.face(tt, mouth=m, brows="think")
PIP.face(15.75, eyes="sparkle", mouth="smile_open", brows="up").reach(15.75, 15.9, "r", H_WAIT)   # off the face
PIP.to(15.75, 15.9, "io", turn=0.25)
CR.face(14.4, eyes="happy", mouth="smile", brows="calm")
# ---- shot 8 (16.7-18.3, A): Pip holds the marker up to Crinkle: his turn, given by her
PIP.to(16.7, 17.0, "io", turn=0.25, look_x=10, look_y=-10).to(16.8, 17.2, "io", lean=6).to(17.6, 17.9, "io", lean=0)
PIP.face(16.8, eyes="happy", mouth="smile_open", brows="up").reach(16.8, 17.2, "r", H_PIP)
G_GIVE = (H_PIP[0] + CAP * U_GIVE[0], H_PIP[1] + CAP * U_GIVE[1])  # the marker's grip point while she holds it up
P_TAKE = (G_GIVE[0] + 5 * U_GIVE[0], G_GIVE[1] + 5 * U_GIVE[1])
CR.to(17.05, 17.2, "io", arm_l=-10, elb_l=14, arm_r=10, elb_r=-14).to(17.1, 17.4, "io", sq=0.9, lean=-10)
CR.to(16.9, 17.1, "io", look_x=-8, look_y=6)
CR.reach(17.2, 17.6, "l", P_TAKE)
CR.face(17.6, eyes="sparkle", mouth="smile_open", brows="up")       # R1: first sparkle at 17.6
PIP.rest_wings(17.65, 17.95).walk(17.65, 18.15, PIP_X1, steps=2).to(18.0, 18.3, "io", turn=0.35, look_x=10, look_y=8)
CR.reach(17.65, 18.0, "l", (1058, 1322)).wiggle(17.7, "lean", 4, 5, 3).to(18.0, 18.2, "io", sq=0.96, lean=-4)
# ---- shot 9 (18.3-21.2, B): gag 2 (G8): the slow smile, tongue sliding; still; the tip lifts with a big squeak
CR.to(18.2, 18.4, "io", sq=0.88, lean=-12).face(18.3, eyes="normal", mouth="yum_l", brows="think")
CR.to(18.3, 18.5, "io", look_x=-8, look_y=10)
follow(CR, "l", "smile", 18.4, 20.0, 0.0, 1.0, U_CR, off=-5, lead=0.2, n=26)
for tt, m in ((18.8, "yum_c"), (19.2, "yum"), (19.6, "yum_c"), (19.95, "yum_l")):
    CR.face(tt, mouth=m)
_se = PL.tip_world("smile", 1.0)
G_END = (_se[0] - (TIP_L - 5) * U_CR[0], _se[1] - (TIP_L - 5) * U_CR[1])
CR.reach(20.0, 20.4, "l", G_END, "lin")                              # the pause: tip still at the line's end
CR.face(20.4, eyes="wide", brows="up", mouth="o")                    # the take: tongue in, eyes wide, head still
CR.reach(20.4, 20.5, "l", (G_END[0] + 4, G_END[1] - 6), "out")        # the tip lifts (the squeak)
BELLY = (CR_XW + BELLY_D[0], BELLY_D[1])
CR.reach(20.5, 21.0, "l", BELLY, "io")                               # back and down to belly height (R3-2)
CR.to(20.5, 21.0, "io", sq=0.96, lean=-5).to(20.5, 21.0, "io", look_x=-4, look_y=12)   # eyes on the marker
PIP.face(18.7, mouth="yum").face(19.5, mouth="smile").to(18.4, 18.6, "io", look_x=10, look_y=10)
PIP.puff_up(20.6, hold=1.46, out=0.3)                                # a ball 20.74-22.2, un-puffs 22.2-22.5
PIP.face(21.0, eyes="normal", mouth="smile", brows="calm")           # R3-3: a closed smile while still round
SN.face(18.5, eyes="happy", mouth="smile", brows="calm").face(20.4, eyes="normal", mouth="smile", brows="calm")
# ---- shot 10 (21.2-22.2, K): he blinks at the marker and laughs at it (held at belly height)
CR.blink(21.3)
CR.face(21.4, eyes="happy", mouth="smile_open", brows="up").hop(21.4, 22.2, 2, 10)
# ---- shot 11 (22.2-23.0, B3): Pip un-puffs and giggles at her feathers; Crinkle to 1260, front; Snip to 660
PIP.to(22.2, 22.4, "io", look_x=4, look_y=16).face(22.5, eyes="happy", mouth="smile_open", brows="up")
PIP.hop(22.5, 22.8, 1, 10)
SN.ears(22.5, 22.7, "perk").ears(22.7, 22.9, "happy").face(22.5, eyes="happy", mouth="smile", brows="calm")
CR.walk(22.2, 22.8, CR_X1, steps=2).to(22.2, 22.5, "io", sq=1.0, lean=0).to(22.2, 22.8, "io", turn=0.0)
SN.walk(22.2, 22.8, SN_X2, steps=2)
BELLY2 = (CR_X1 + BELLY_D[0], BELLY_D[1])
CR.reach(22.2, 22.8, "l", BELLY2, "io")
CR.face(22.3, eyes="happy", mouth="smile", brows="calm")
# ---- shot 12 (23.0-26.2, B3): the hand and the tea light; the glow
for perf, lx in ((SN, 6), (CR, -6), (PIP, 6)):
    perf.to(22.95, 23.25, "io", look_x=lx, look_y=-12)
    perf.face(23.0, eyes="normal", mouth="smile", brows="up")
    perf.to(24.5, 25.1, "io", look_x=lx, look_y=10)
    perf.face(25.4, eyes="sparkle", mouth="smile_open", brows="up")
SN.ears(25.4, 25.7, "perk")
CR.to(24.05, 24.3, "io", lean=-6).to(25.3, 25.8, "io", lean=0)               # r3: leans 6 away (24.3-25.3;
CR.to(25.5, 25.9, "io", turn=-0.35)                                         # + is toward the lantern); turns back
PIP.to(22.9, 23.3, "io", lean=-5).to(25.4, 25.8, "io", lean=0)
SN.to(22.9, 23.3, "io", lean=-5).to(25.4, 25.8, "io", lean=0)
# ---- shot 13 (26.2-29.0, B3 -> END): Snip hops; gag 3 (G5): two wiggles, still, the third spins him round
SN.to(26.4, 26.6, "io", sq=0.92).hop(26.6, 27.0, 1, 26).to(27.0, 27.2, "io", sq=1.0)
TUMMY = BELLY2
CR.to(26.2, 26.4, "io", arm_r=150, elb_r=-20)                       # right paw up: the side away from the lantern
CR.face(26.4, eyes="happy", mouth="smile_open", brows="up")
for i, (a, b) in enumerate(((26.4, 26.775), (26.775, 27.15), (27.15, 27.525), (27.525, 27.9))):
    CR.to(a, b, "io", lean=7 if i % 2 == 0 else -7, tilt=4 if i % 2 == 0 else -4)
CR.hop(26.4, 27.9, 4, 12)
CR.to(27.9, 28.2, "io", sq=0.9, lean=0, tilt=0)                      # squashes down, still (the pause)
CR.to(28.2, 28.5, "io", turn=0.55, sq=1.0, lean=7, tilt=4)          # wiggle 3 swings him right round, feet down
CR.to(28.5, 28.75, "io", lean=-7, tilt=-4).to(28.75, 29.0, "io", lean=7, tilt=4)   # dances on, the wrong way
# ---- shot 14 (29.0-30.0, K2): he looks back over his shoulder, blinks, laughs at himself
CR.to(29.0, 29.2, "io", lean=0, tilt=0, hturn=-0.6, look_x=-10, look_y=2).blink(29.2)
CR.to(29.05, 29.3, "io", arm_r=10, elb_r=-14)
CR.face(29.3, eyes="happy", mouth="smile_open", brows="up").hop(29.3, 30.0, 3, 10)
PIP.dance(26.8, 27.9, beats=3, amp=5.0, bounce=6.0).face(26.8, eyes="happy", mouth="smile", brows="up")
PIP.face(27.9, eyes="normal", mouth="smile", brows="think")         # R3-4: a serious copy, beak closed
PIP.to(28.6, 28.9, "io", turn=-0.45).dance(28.9, 29.5, beats=2, amp=4.0, bounce=4.0)
PIP.face(29.35, eyes="happy", mouth="smile", brows="calm")
SN.face(27.9, eyes="normal", mouth="smile", brows="calm").face(29.35, eyes="happy", mouth="smile", brows="calm")


# ---------------------------------------------------------------- the marker's holder schedule
def marker_pose(t):
    """(who, side, off, angle): the marker's grip point is the holder's paw + off along the marker."""
    if t < 1.2:
        return "sn", "r", 0.0, ANG["sn"]
    if t < 5.4:
        ang = _ease(t, [(1.9, ANG["sn"]), (2.3, A_HANG), (2.8, A_HANG), (3.2, ANG["cr"]), (4.5, ANG["cr"]),
                        (5.4, ANG["sn"])])
        return "cr", "l", CAP, ang
    if t < 13.2:
        return "sn", "r", 0.0, _ease(t, [(12.6, ANG["sn"]), (12.85, A_REST), (12.9, A_REST), (13.15, A_FLAT)])
    if t < 17.6:
        off = _ease(t, [(13.2, -18.0), (13.6, 0.0), (15.75, 0.0), (15.9, CAP)])
        ang = _ease(t, [(13.2, A_FLAT), (13.6, A_FLAT), (14.2, A_FLAT), (14.4, ANG["pip"]), (15.75, ANG["pip"]),
                        (15.9, ANG["give"])])
        return "pip", "r", off, ang
    ang = _ease(t, [(17.6, ANG["give"]), (18.0, A_FLAT), (18.2, A_FLAT), (18.4, ANG["cr"]), (20.5, ANG["cr"]),
                    (21.0, A_BELLY)])
    return "cr", "l", -5.0, ang


PERFS = {"sn": SN, "cr": CR, "pip": PIP}


def marker_grip(t, sts):
    """World grip point and angle of the marker, and its holder's paw."""
    who, side, off, ang = marker_pose(t)
    W, _ = PERFS[who].paw(t, side, sts[who])
    dx, dy = rot(0, off, ang)
    return (W[0] + dx, W[1] + dy), ang, W, who


def marker_tip_world(t, sts):
    g, ang, _, _ = marker_grip(t, sts)
    return RP.marker_tip(g, ang, MK_S)


def arms_over(t):
    """Arms drawn again after the lantern (they reach over it), in this order; the marker goes over all of them."""
    out = []
    if t < 12.9:
        out.append(("sn", "r"))
    if 0.3 <= t < 5.8 or 17.15 <= t < 21.0:
        out.append(("cr", "l"))
    if 14.1 <= t < 17.65:
        out.append(("pip", "r"))
    return out


def back_now(who, t):
    return any(a <= t < b for a, b in BACK[who])


# ---------------------------------------------------------------- the grown-up's hand and the tea light (22-24.9)
def tea_light_round(on=False):
    """The episode's round battery tea light (white body, side switch, LED dome; never open; no flame)."""
    c = RCut(84, 70)
    cx, top = 42, 34
    c.ellipse(cx, top + 15, 30, 10, (226, 226, 230))
    c.rrect(cx - 30, top, cx + 30, top + 15, 1, (238, 238, 242))
    c.ellipse(cx, top, 30, 10, G.WHITE)
    c.ellipse(cx, top + 0.5, 25, 7.5, (244, 244, 246), sil=False)
    c.ellipse(cx, top + 1.5, 11, 4, (214, 214, 220), sil=False)
    c.ellipse(cx, top - 6, 9, 10, G.LED_ON if on else G.LED_OFF)
    c.ellipse(cx - 3, top - 10, 3, 3.5, (255, 252, 230) if on else (255, 255, 255), sil=False)
    c.rrect(cx + 23, top + 4, cx + 29, top + 11, 2, G.SWITCH, sil=False)
    return c.finish(pivot=(cx, top), border=3, shadow_alpha=0.22)


TEA = {False: tea_light_round(False), True: tea_light_round(True)}
TEA_S = 1.15                            # 69 wide: fits the 84-wide ring
ARM = H.Arm(upper=720, fore=760)
T_HAND = (23.0, 25.3)
T_CLICK = 23.7
TEA_HOLD = (961, 1250)                  # the light's top, held above the ring
TEA_IN = (961, 1356)                    # let go just inside the ring: only the narrow fingers go in (keys1 K1);
                                        # the light sits on the bottom inside, out of sight (the paper glows)
TEA_GRIP = (0, -3)                      # pinched at its top rim, from straight above
T_GLOW = (24.55, 25.2)


def tea_top(t):
    return _ease(t, [(23.0, (961, 640)), (23.5, TEA_HOLD), (24.3, TEA_HOLD), (24.85, TEA_IN), (25.0, TEA_IN)])


def hand_state(t):
    if not T_HAND[0] <= t < T_HAND[1]:
        return None
    if t < 25.0:
        top = tea_top(t)
        grip = (top[0] + TEA_GRIP[0], top[1] + TEA_GRIP[1])
        hand = "press" if T_CLICK - 0.08 <= t < T_CLICK + 0.14 else "pinch"
        return dict(grip=grip, hand=hand, top=top)
    g0 = (TEA_IN[0] + TEA_GRIP[0], TEA_IN[1] + TEA_GRIP[1])
    return dict(grip=_ease(t, [(25.0, g0), (25.3, (961, 640))]), hand="pinch", top=None)


def glow_k(t):
    return ease_in_out(seg(t, *T_GLOW))


def draw_hand(im, cam, hs, t):
    hand = H.HANDS[hs["hand"]]
    g = hs["grip"]
    sh = (g[0] - 4, g[1] - 1612)                  # the arm comes straight down (the grown-up lowers the whole arm)
    W = ARM.wrist_for(sh, g, hand, -1)
    ARM.draw_hand(im, cam, sh, W, hand, -1)
    if hs["top"] is not None:           # keys1 K1: fingers pinch the far rim, so the light and its LED dome stay in front
        place(im, TEA[t >= T_CLICK], cam.S(hs["top"]), scale=TEA_S)


# ---------------------------------------------------------------- the world
def warm(lay, glow, r=300.0, gain=0.85):
    """The lantern's warm light on a layer, by distance."""
    if lay is None or glow <= 0.003:
        return
    a = L._arr(lay.img)
    alb = a[..., :3].copy()
    wx, wy = L._world(CAM, *L._grid(lay.box))
    d2 = (wx - GLOW_C[0]) ** 2 + ((wy - GLOW_C[1]) * 1.15) ** 2
    L._add_light(a[..., :3], alb, L.WARM, glow * gain * np.exp(-d2 / (2 * r ** 2)))
    lay.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def dusk(img, mul):
    a = np.asarray(img, np.float32).copy()
    a[..., :3] *= np.array(mul, np.float32)[None, None, :]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), img.mode)


_BG = {}


def background():
    if "bg" not in _BG:
        _BG["bg"] = dusk(WORLD.background(T_LIGHT), DUSK_SET)
    return _BG["bg"].copy()


def _draw_puppet(perf, im, t, d, st, back):
    if not back:
        perf.draw(im, t, CAM, drawing=d, st=st)
        return
    for side in ("l", "r"):                       # T2: paws / wings behind the back, drawn before the body
        perf.a._arm(im, CAM, st, side)
    perf.a._arm = lambda *a, **k: None
    try:
        perf.draw(im, t, CAM, drawing=d, st=st)
    finally:
        del perf.a._arm


class _Empty:
    def paste(self, f):
        pass


def _char_layer(size, fn, glow):
    lay = L.Layer.of(size, fn)
    if lay is None:
        return _Empty()
    L.grade_layer(lay, T_LIGHT, 0, None, CAM)
    lay.img = dusk(lay.img, DUSK_CHAR)
    warm(lay, glow)
    return lay


def states(t, d=None):
    return {k: p.state(t, d) for k, p in PERFS.items()}


def draw_marker(im, t, sts):
    g, ang, W, who = marker_grip(t, sts)
    place(im, MK, CAM.S(g), angle=ang)
    if who == "pip":
        place(im, PIPA.grip, CAM.S(W), angle=ang)


def render_world(t, d=None, cam=None, bg=None):
    d = K.drawing_of(t) if d is None else d
    glow = glow_k(t)
    f = bg if bg is not None else background()
    size = f.size
    L.floor_pool(f, CAM, WORLD.albedo, glow, 1.0)
    WORLD.front(f, T_LIGHT)                       # r3: railing and corner post behind the characters (Crinkle at 1260)
    sts = states(t, d)
    for who in (("sn", "cr", "pip") if 2.8 <= t < 6.5 else ("cr", "sn", "pip")):
        perf, st = PERFS[who], sts[who]
        back = back_now(who, t)
        _char_layer(size, lambda im, perf=perf, st=st, back=back: _draw_puppet(perf, im, t, d, st, back),
                    glow).paste(f)
    strokes = strokes_at(t)
    lay_pk = L.Layer.of(size, lambda im: place(im, LANTERN.paper(strokes), CAM.S(BASE)))
    L.grade_layer(lay_pk, T_LIGHT, prop=True)
    lay_pk.img = dusk(lay_pk.img, DUSK_CHAR)
    lay_pk.paste(f)
    if glow > 0.003:
        place(f, LANTERN.lit(strokes, glow), CAM.S(BASE), shadow=False)
    over = arms_over(t)

    def draw_over(im):
        for who, side in over:
            PERFS[who].a._arm(im, CAM, sts[who], side)
        draw_marker(im, t, sts)
    _char_layer(size, draw_over, glow).paste(f)
    hs = hand_state(t)
    if hs:
        lay_h = _char_layer(size, lambda im: draw_hand(im, CAM, hs, t), glow)
        if not isinstance(lay_h, _Empty):
            PL.inside_clip(lay_h, CAM)
        lay_h.paste(f)
        if hs["top"] is not None and t >= T_CLICK and hs["top"][1] < PL.RING_WORLD[1] - 4:
            led = (hs["top"][0], hs["top"][1] - 7 * TEA_S)
            L.halo(f, CAM, 1.0, at=led, strength=0.30, sigma=7.0)      # the LED dome's own small glow
    L.halo(f, CAM, glow, at=GLOW_C, strength=0.40, sigma=125.0)
    return f


# ---------------------------------------------------------------- cameras (plan b4; vertical)
CAMS = {"A": ((880, 1250), 1.7), "T": ((958, 1300), 2.6), "B2": ((920, 1270), 1.8), "K": ((1060, 1180), 1.9),
        "B": ((950, 1320), 2.0), "G": ((990, 1180), 2.5), "B3": ((1005, 1180), 1.5)}   # r3: G give-back, B3 22.2-29
_hp = CR.a.head_pivot(CR.state(29.5))
CAMS["K2"] = ((round(_hp[0]), round(_hp[1] - 42)), 1.9)   # on his head at x 1260 (K's offset from the head)
END_C, END_Z = (1020, 1215), 1.2      # r3: Crinkle at 1260 (his body to x 1500)
T_PULL = (25.4, 27.8)                  # B3 1.5x -> END 1.2x (peak 0.15x/s; rule <= 0.35)
SHOTS = [(0.0, "A"), (0.6, "T"), (2.8, "B2"), (4.5, "G"), (5.9, "A"), (9.6, "K"), (10.6, "B"), (12.8, "A"),
         (14.3, "B"), (16.7, "A"), (18.3, "B"), (21.2, "K"), (22.2, "B3"), (29.0, "K2")]
CUTS = [s[0] for s in SHOTS[1:]]        # the pull back is not a cut


def _trap(p, r=0.15):
    """0..1 with a trapezoid speed (eased ends r, constant middle): the zoom never goes faster than it must."""
    v = 1.0 / (1 - r)
    if p <= 0:
        return 0.0
    if p >= 1:
        return 1.0
    if p < r:
        return v * p * p / (2 * r)
    if p > 1 - r:
        q = 1 - p
        return 1 - v * q * q / (2 * r)
    return v * (p - r / 2)


def shot_at(t):
    name = [s[1] for s in SHOTS if t >= s[0] - 1e-9][-1]
    c, z = CAMS[name]
    if t >= T_PULL[0] and name != "K2":
        k = _trap(seg(t, *T_PULL))
        c = (lerp(c[0], END_C[0], k), lerp(c[1], END_C[1], k))
        z = lerp(z, END_Z, k)
    return name, c, z


def film(f, c, z):
    w, h = 1080 / z, 1920 / z
    x0 = min(max(c[0] - w / 2, CAM.ox), CAM.ox + 1080 - w)
    y0 = min(max(c[1] - h / 2, CAM.oy), CAM.oy + 1920 - h)
    box = ((x0 - CAM.ox) * RES, (y0 - CAM.oy) * RES, (x0 + w - CAM.ox) * RES, (y0 + h - CAM.oy) * RES)
    return f.convert("RGB").resize((1080, 1920), Image.LANCZOS, box=box)


def code_hash():
    h = hashlib.sha1()
    for p in (__file__, PL.__file__):
        with open(p, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:12]


def hi_range():
    return [(0.6, 2.8), (4.5, 5.9)]     # cameras T (2.6x) and G (2.5x) at render scale 3


def render_frame(t, view="vert", fresh=False):
    d = K.drawing_of(t)
    tq = d / K.DPS
    name, c, z = shot_at(tq)
    if not fresh and RES < 2.5 and z > 2.0 + 1e-6:
        p = os.path.join(HI_DIR, f"d{d:05d}.png")
        stamp = os.path.join(HI_DIR, "code_hash.txt")
        if os.path.exists(p) and os.path.exists(stamp) and open(stamp).read().strip() == code_hash():
            return Image.open(p).convert("RGB")
    return film(render_world(tq, d), c, z)


# ---------------------------------------------------------------- checks (numbers, not looks)
def _mask_of(draw):
    m = Image.new("RGBA", (int(1080 * RES), int(1920 * RES)), (0, 0, 0, 0))
    draw(m)
    return m.getchannel("A").point(lambda v: 255 if v > 40 else 0)


def _edge_pts(mask, step=1):
    a = np.asarray(mask) > 0
    if not a.any():
        return np.zeros((0, 2), np.float32)
    er = np.asarray(mask.filter(ImageFilter.MinFilter(3))) > 0
    ys, xs = np.nonzero(a & ~er)
    pts = np.stack([xs / RES + CAM.ox, ys / RES + CAM.oy], 1).astype(np.float32)
    return pts[::step]


def _gap(ma, mb, pad=160):
    """Smallest distance (design units) between two masks (0 if they overlap); looks near mask a only."""
    bb = ma.getbbox()
    if bb is None or mb.getbbox() is None:
        return float("inf")
    p = int(pad * RES)
    box = (max(0, bb[0] - p), max(0, bb[1] - p), min(ma.size[0], bb[2] + p), min(ma.size[1], bb[3] + p))
    ma, mb = ma.crop(box), mb.crop(box)
    if mb.getbbox() is None:
        return float(pad)
    if (np.asarray(ImageChops.multiply(ma, mb)) > 0).any():
        return 0.0
    a, b = _edge_pts(ma, 2), _edge_pts(mb, 2)
    if len(a) == 0 or len(b) == 0:
        return float(pad)
    best = 1e18
    for i in range(0, len(a), 400):
        dd = ((a[i:i + 400, None, :] - b[None, :, :]) ** 2).sum(-1)
        best = min(best, float(dd.min()))
    return min(float(pad), math.sqrt(best))


def head_mask(who, st):
    return L.head_mask(PERFS[who].a, st, CAM, (int(1080 * RES), int(1920 * RES)), grow=0).point(
        lambda v: 255 if v > 40 else 0)


def _arm_mask(who, side, sts):
    return _mask_of(lambda im: PERFS[who].a._arm(im, CAM, sts[who], side))


def _body_mask(who, t, sts):
    return _mask_of(lambda im: _draw_puppet(PERFS[who], im, t, K.drawing_of(t), sts[who], back_now(who, t)))


def _mk_only(t, sts):
    g, ang, _, _ = marker_grip(t, sts)
    return _mask_of(lambda im: place(im, MK, CAM.S(g), angle=ang))


def _pct(mask, t):
    """The object's mask width as % of the frame width, through the shot camera at time t."""
    bb = mask.getbbox()
    return 0.0 if bb is None else (bb[2] - bb[0]) / RES * shot_at(t)[2] / 1080 * 100


def _vis_arm(who, side, t, sts):
    """The visible part of a paw / wing (R4-1): its arm mask, minus the body when it is behind the back."""
    perf = PERFS[who]
    m = _arm_mask(who, side, sts)
    if back_now(who, t):
        perf.a._arm = lambda *a, **k: None
        try:
            body = _mask_of(lambda im: perf.draw(im, t, CAM, drawing=K.drawing_of(t), st=sts[who]))
        finally:
            del perf.a._arm
        m = ImageChops.subtract(m, body)
    return m


def _frame_mask(t):
    """The shot camera's frame at time t as a world mask (what the viewer sees)."""
    _, c, z = shot_at(t)
    w, h = 1080 / z, 1920 / z
    x0 = min(max(c[0] - w / 2, CAM.ox), CAM.ox + 1080 - w)
    y0 = min(max(c[1] - h / 2, CAM.oy), CAM.oy + 1920 - h)
    m = Image.new("L", (int(1080 * RES), int(1920 * RES)), 0)
    ImageDraw.Draw(m).rectangle([(x0 - CAM.ox) * RES, (y0 - CAM.oy) * RES, (x0 + w - CAM.ox) * RES,
                                 (y0 + h - CAM.oy) * RES], fill=255)
    return m


def _frac_visible(t, sts):
    """r3 (Lead): share of the marker's pixels seen: inside the shot's frame and under nothing drawn after it (the
    marker is drawn after both arms and the lantern; only the grown-up's hand comes later)."""
    mk = _mk_only(t, sts)
    covers = [ImageChops.invert(_frame_mask(t))]
    hs = hand_state(t)
    if hs:
        covers.append(_mask_of(lambda im: draw_hand(im, CAM, hs, t)))
    return _frac_clear(mk, covers)


def _hand_masks(t):
    """(hand + tea light, sleeve) masks of the grown-up's arm at time t."""
    hs = hand_state(t)
    g = hs["grip"]
    sh = (g[0] - 4, g[1] - 1612)
    full = _mask_of(lambda im: draw_hand(im, CAM, hs, t))
    slv = _mask_of(lambda im: ARM.draw(im, CAM, sh, ARM.wrist_for(sh, g, H.HANDS[hs["hand"]], -1), -1))
    return ImageChops.subtract(full, slv), slv


def _frac_clear(mk, covers):
    a = np.asarray(mk) > 0
    c = np.zeros_like(a)
    for m in covers:
        c |= np.asarray(m) > 0
    return float((a & ~c).sum()) / max(1, int(a.sum()))


def drawings(a, b, step=1):
    return [d / K.DPS for d in range(int(math.ceil(a * K.DPS - 1e-6)), int(math.ceil(b * K.DPS - 1e-6)), step)]


def _moving(perf, ts, keys=("lean", "turn", "tilt", "sq", "hturn"), eps=(0.3, 0.01, 0.3, 0.004, 0.01)):
    """Per drawing: True if any body key changed more than eps since the previous drawing."""
    sv = [perf.state(t) for t in ts]
    return [False] + [any(abs(sv[i].get(k, 0) - sv[i - 1].get(k, 0)) > e for k, e in zip(keys, eps))
                      for i in range(1, len(ts))]


def _still_spans(perf, a, b):
    ts = drawings(a, b)
    mv = _moving(perf, ts)
    out, s = [], None
    for t, m in zip(ts, mv):
        if not m and s is None:
            s = t
        elif m and s is not None:
            out.append((round(s, 2), round(t, 2)))
            s = None
    if s is not None:
        out.append((round(s, 2), round(b, 2)))
    return out


def gag_timing():
    """Measured from the performances (every drawing), against the plan's gag table."""
    lines = []
    st1 = [s for s in _still_spans(CR, 8.2, 9.0) if s[1] - s[0] >= 0.2]
    turn = [(CR.state(t)["turn"], t) for t in drawings(8.8, 9.6)]
    lines.append(f"gag 1 (plan: set-up 6.9-8.4, pause 8.4-8.8, break 8.8-9.6, reaction 9.6-10.6 in K): Crinkle still "
                 f"{st1}; Pip still {[s for s in _still_spans(PIP, 8.2, 9.0) if s[1] - s[0] >= 0.2]}; turn peak "
                 f"{max(turn)[0]:.2f} at {max(turn)[1]:.2f}; back to {CR.state(9.6)['turn']:.2f} at 9.6; grin face "
                 f"at 9.6 '{CR.state(9.6).get('mouth')}' in camera {shot_at(9.6)[0]}")
    tips = [(t, marker_tip_world(t, states(t))) for t in drawings(19.8, 20.6)]
    still = [round(t, 2) for (t, p), (_, q) in zip(tips[1:], tips[:-1]) if math.hypot(p[0] - q[0], p[1] - q[1]) < 0.3]
    puff = [t for t in drawings(20.4, 22.6) if PIP.state(t).get("puff", 0) > 0.95]
    lines.append(f"gag 2 (plan: set-up 18.3-20.0, pause 20.0-20.4, break 20.4-21.2, reaction 21.2-22.2 in K): tip still "
                 f"{still[0] if still else None}-{still[-1] if still else None}; take face at 20.4 "
                 f"'{CR.state(20.45).get('eyes')}'; Pip a full ball {puff[0]:.2f}-{puff[-1]:.2f}; his laugh face at "
                 f"21.4 '{CR.state(21.45).get('mouth')}' in camera {shot_at(21.4)[0]}")
    st3 = [s for s in _still_spans(CR, 27.7, 28.4) if s[1] - s[0] >= 0.2]
    wrong = [t for t in drawings(28.2, 29.0) if CR.state(t)["turn"] > 0.5]
    lines.append(f"gag 3 (plan: set-up 26.4-27.9, pause 27.9-28.2, break 28.2-29.0, reaction 29.0-30.0 in K2): Crinkle "
                 f"still {st3}; facing the wrong way (turn > 0.5) from {wrong[0]:.2f}; look back hturn "
                 f"{CR.state(29.25)['hturn']:.2f} in camera {shot_at(29.25)[0]}; laugh face at 29.3 "
                 f"'{CR.state(29.35).get('mouth')}'")
    return lines


def checks():
    lines = []

    def ok(v, need, txt, ge=True):
        good = v >= need if ge else v <= need
        lines.append(f"{'ok  ' if good else 'FAIL'} {txt}: {v:.1f} (need {'>=' if ge else '<='} {need:g})")
    # 1. the take and the give-back: the marker drawn over both arms, >= 95% of its pixels seen, every drawing (r3)
    for a, b, tag in ((0.9, 2.3, "the take"), (4.5, 5.9, "the give-back")):
        worst = (2.0, None)
        for tt in drawings(a, b):
            sts = states(tt)
            worst = min(worst, (_frac_visible(tt, sts), round(tt, 2)))
            if (tt < 5.4 and ("cr", "l") not in arms_over(tt)) or ("sn", "r") not in arms_over(tt):
                lines.append(f"FAIL marker not drawn over both arms at {tt:.2f}")
        ok(worst[0] * 100, 95, f"{tag} {a}-{b}: marker % of pixels visible, in frame (min, at {worst[1]}; cameras "
                               f"{sorted(set(shot_at(x)[0] for x in drawings(a, b)))})")
    # 2. key sizes (handover_check): the key object's mask width as % of the frame width
    for tt in (1.0, 1.6, 2.2, 4.6, 5.2, 5.8, 16.9, 17.3, 17.7):
        lines.append(f"keysize {tt:.2f} {_pct(_mk_only(tt, states(tt)), tt):.1f}   (marker, camera {shot_at(tt)[0]})")
    for tt in (23.3, 23.8, 24.3, 24.7):
        hs = hand_state(tt)
        m = _mask_of(lambda im: place(im, TEA[tt >= T_CLICK], CAM.S(hs["top"]), scale=TEA_S))
        lines.append(f"keysize {tt:.2f} {_pct(m, tt):.1f}   (tea light, camera {shot_at(tt)[0]})")
    # 3. the let-go: his paw clear of the marker (>= 30 by 5.55, r3); the marker and her paw still
    for tt in (5.4, 5.47, 5.55, 5.6, 5.8):
        sts = states(tt)
        g = _gap(_arm_mask("cr", "l", sts), _mask_of(lambda im: draw_marker(im, tt, sts)))
        if tt >= 5.55:
            ok(g, 30, f"give-back {tt:.2f}: Crinkle's arm to the marker gap")
        else:
            lines.append(f"give-back {tt:.2f}: Crinkle's arm to the marker gap {g:.1f}")
    tips = [marker_tip_world(tt, states(tt)) for tt in drawings(5.4, 5.9)]
    ok(max(math.hypot(p[0] - tips[0][0], p[1] - tips[0][1]) for p in tips), 1.0, "marker tip movement 5.4-5.9",
       ge=False)
    lines.append(f"tip at 5.4 {tuple(round(v, 1) for v in tips[0])}; the C's end "
                 f"{tuple(round(v, 1) for v in PL.tip_world('eye_l', C))}")
    ps = [SN.paw(tt, "r")[0] for tt in drawings(0.9, 5.9)]
    ok(max(math.hypot(p[0] - ps[0][0], p[1] - ps[0][1]) for p in ps), 1.0, "Snip's paw movement 0.9-5.9", ge=False)
    gs = [marker_grip(tt, states(tt))[0] for tt in drawings(1.2, 1.9) + [1.9]]
    side = max(abs((g[0] - gs[0][0]) * U_SN[1] - (g[1] - gs[0][1]) * U_SN[0]) for g in gs)
    ok(side, 3.0, f"the slide 1.2-1.9 along its own axis: sideways units (slid {math.hypot(gs[-1][0] - gs[0][0], gs[-1][1] - gs[0][1]):.0f})",
       ge=False)
    # 4. the marker and faces
    worst = (1e9, None)
    for tt in drawings(16.7, 18.0):
        sts = states(tt)
        worst = min(worst, (_gap(_mask_of(lambda im: draw_marker(im, tt, sts)), head_mask("pip", sts["pip"])),
                            round(tt, 2)))
    ok(worst[0], 30, f"marker to Pip's head 16.7-18.0 (min, at {worst[1]})")
    tipmin, lowest = (1e9, None), (1e9, None)
    for tt in [round(x, 2) for x in np.arange(0.0, DUR, 0.2)] + drawings(20.4, 22.8):
        sts = states(tt)
        tip = marker_tip_world(tt, sts)
        tm = Image.new("L", (int(1080 * RES), int(1920 * RES)), 0)
        x, y = CAM.S(tip)
        ImageDraw.Draw(tm).ellipse([x - 2, y - 2, x + 2, y + 2], fill=255)
        for who in ("sn", "cr", "pip"):
            hm = head_mask(who, sts[who])
            g = _gap(tm, hm)
            tipmin = min(tipmin, (g, (round(float(tt), 2), who)))
            if 20.4 <= tt <= 22.8:
                lowest = min(lowest, (g, (round(float(tt), 2), who)))
                if who == "cr":
                    chin = hm.getbbox()[3] / RES + CAM.oy
                    if tip[1] < chin:
                        lines.append(f"FAIL marker tip above his chin at {tt:.2f}")
    ok(tipmin[0], 30, f"marker tip to the nearest head, whole Short (min, at {tipmin[1]})")
    ok(lowest[0], 60, f"R3-2: marker tip to every head 20.4-22.8, every drawing (min, at {lowest[1]})")
    # 5. the lantern (gate 1 R4-1): visible paws, wings and markers to the lantern mask, ring included (bodies, heads,
    #    ears and feet may stand behind it; Snip's drawing paw and marker exempt 6.5-10.6)
    lan = _mask_of(lambda im: place(im, LANTERN.paper({}), CAM.S(BASE)))
    for a, b, whos, need, tag in ((6.5, 10.6, ("cr", "pip"), 10, "R4-1 paws, wings"),
                                  (20.6, 21.2, ("pip",), 10, "puff-up wings"),
                                  (21.2, 22.8, ("sn", "cr", "pip", "mk"), 1, "F3 nothing on it"),
                                  (22.8, DUR, ("sn", "cr", "pip", "mk"), 10, "N4/F3")):
        worst = (1e9, None)
        for tt in drawings(a, b):
            sts = states(tt)
            for who in whos:
                ms = [("", _mk_only(tt, sts))] if who == "mk" else [(sd, _vis_arm(who, sd, tt, sts)) for sd in "lr"]
                for sd, m in ms:
                    worst = min(worst, (_gap(m, lan), (round(tt, 2), who + sd)))
        ok(worst[0], need, f"{tag} {a}-{b:g}: to the lantern (min, at {worst[1]})")
    # 6. the hand and the tea light
    hm = {}
    for tt in drawings(23.0, 25.3):
        sts = states(tt)
        hand, slv = _hand_masks(tt)
        for who in ("sn", "cr", "pip"):
            h = head_mask(who, sts[who])
            for k, m in (("hand", hand), ("sleeve", slv)):
                hm[(k, who)] = min(hm.get((k, who), (1e9, None)), (_gap(m, h), round(float(tt), 2)))
    for who, name in (("cr", "Crinkle (1260, leans 6 away)"), ("sn", "Snip (660)"), ("pip", "Pip (740)")):
        ok(hm[("hand", who)][0], 30, f"hand + tea light to {name}'s head 23.0-25.3 (min, at {hm[('hand', who)][1]})")
        ok(hm[("sleeve", who)][0], 10, f"sleeve to {name}'s head 23.0-25.3 (min, at {hm[('sleeve', who)][1]})")
    worst = (0, 0.0)
    for tt in drawings(24.3, 25.3):
        hs = hand_state(tt)
        lay = L.Layer.of(lan.size, lambda im: draw_hand(im, CAM, hs, tt))
        PL.inside_clip(lay, CAM)
        hmk = Image.new("L", lan.size, 0)
        hmk.paste(lay.img.getchannel("A").point(lambda v: 255 if v > 40 else 0), lay.box[:2])
        a = np.asarray(ImageChops.multiply(hmk, lan)) > 0
        a[:int((PL.RING_WORLD[1] + PL.RING_R[1] - CAM.oy) * RES)] = False
        worst = max(worst, (int(a.sum()), round(float(tt), 2)))
    lines.append(f"hand pixels over the lantern paper below the ring rim 24.3-25.3: {worst[0]} (max, at {worst[1]})")
    bad = [round(tt, 2) for tt in drawings(21.2, DUR) if arms_over(tt)]
    lines.append(f"{'FAIL' if bad else 'ok  '} arms drawn over the lantern 21.2-30.0: {bad[:3] or 'none'}")
    # 7. the camera: zoom and pan speed, stretches without a change
    ts = drawings(0.0, DUR)
    zr, pr = [], []
    for a, b in zip(ts[:-1], ts[1:]):
        (na, ca, za), (nb, cb, zb) = shot_at(a), shot_at(b)
        if na == nb:
            zr.append((abs(zb - za) * 15, round(float(a), 2)))
            pr.append((math.hypot(cb[0] - ca[0], cb[1] - ca[1]) * 15, round(float(a), 2)))
    ok(max(zr)[0], 0.35, f"camera max zoom rate x/s (at {max(zr)[1]}; pan max {max(pr)[0]:.1f} units/s at "
                         f"{max(pr)[1]})", ge=False)
    edges = sorted(set([0.0] + CUTS + list(T_PULL) + [DUR]))
    long = [(a, b) for a, b in zip(edges[:-1], edges[1:]) if b - a > 6.0]
    lines.append(f"{'FAIL' if long else 'ok  '} stretches > 6 s without a cut or camera move: {long or 'none'}; "
                 f"longest {max(b - a for a, b in zip(edges[:-1], edges[1:])):.1f} s")
    return lines + gag_timing()


# ---------------------------------------------------------------- sound (no voices: effects and music only)
BEAT = 60.0 / 104.0
M = A.midi


def squeaks(sfx, t0, t1, f0, gap=0.27, dur=0.24, vel=0.5):
    t = t0
    i = 0
    while t < t1 - 0.05:
        sfx.add(t, A_squeak(min(dur, t1 - t), vel * (0.9 + 0.1 * (i % 2)), f0 + 120 * (i % 3)))
        t += gap
        i += 1


def A_squeak(dur=0.3, vel=1.0, f0=2100):
    tt = A._t(dur)
    f = f0 + 250 * np.sin(2 * np.pi * 7 * tt)
    return vel * 0.12 * np.sin(2 * np.pi * np.cumsum(f) / A.SR) * np.sin(np.pi * tt / dur)


def click(vel=1.0):
    tt = A._t(0.03)
    n = np.random.default_rng(3).normal(0, 1, len(tt))
    return vel * 0.5 * n * np.exp(-tt * 300)


def organ_bend(f0, f1, dur, vel=1.0):
    """A low organ note bending down (Crinkle understands: an instrument, never a voice)."""
    tt = A._t(dur)
    f = f0 * (f1 / f0) ** np.clip((tt - 0.1) / (dur - 0.2), 0, 1)
    ph = 2 * np.pi * np.cumsum(f) / A.SR
    y = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(4 * ph)
    env = np.clip(tt / 0.06, 0, 1) * np.clip((dur - tt) / 0.25, 0, 1)
    return vel * 0.22 * y * env


TUNE = [(0, 84, .45), (.5, 81, .45), (1, 77, .45), (1.5, 81, .45), (2, 84, .9), (3, 89, 1.4)]   # C A F A | C . F


def tune(music, t0, upto=None, vel=0.5, oct=0, step=1.0):
    for b, m, d in TUNE:
        tt = t0 + b * BEAT * step
        if upto is not None and tt >= upto:
            return
        music.add(tt, A.glock(M(m + oct), d * 1.6, vel))


def bass_bars(music, t0, t1, prog=("F", "Bb", "C", "F"), vel=0.45):
    roots = {"F": 41, "Bb": 46, "C": 48}
    bar, i, t = 4 * BEAT, 0, t0
    while t < t1 - 0.05:
        r = roots[prog[i % len(prog)]]
        for b, m in ((0, r), (2, r + 7)):
            if t + b * BEAT < t1:
                music.add(t + b * BEAT, A.pluck(M(m), 0.4, vel))
        t += bar
        i += 1


def toy_squeak(dur=0.3, vel=1.0):
    """r2 gag 2: a rubber-toy squeak (synth): rising, soft attack (no click), 0.3 s (R3-1)."""
    tt = A._t(dur)
    f = 900 + 700 * np.clip(tt / (dur * 0.6), 0, 1) + 60 * np.sin(2 * np.pi * 18 * tt)
    ph = 2 * np.pi * np.cumsum(f) / A.SR
    y = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    env = np.clip(tt / 0.04, 0, 1) * np.clip((dur - tt) / 0.08, 0, 1)
    return vel * 0.16 * y * env


def fwump(vel=1.0):
    """A soft feather 'fwump': low filtered air, no attack click."""
    tt = A._t(0.28)
    n = np.random.default_rng(7).normal(0, 1, len(tt))
    k = np.ones(40) / 40
    lo = np.convolve(n, k, "same")
    env = np.clip(tt / 0.03, 0, 1) * np.exp(-tt * 12)
    return vel * 0.9 * lo * env + vel * 0.05 * np.sin(2 * np.pi * 110 * tt) * env


def glock_bend(m, dur=0.8, up=0.12, vel=0.3):
    """Gag 1: a wobbly glock bend up and back (never below the start note)."""
    tt = A._t(dur)
    f = A.midi(m) * (1 + up * np.sin(np.pi * tt / dur) + 0.012 * np.sin(2 * np.pi * 7 * tt))
    ph = 2 * np.pi * np.cumsum(f) / A.SR
    return vel * 0.25 * (np.sin(ph) + 0.3 * np.sin(4 * ph)) * np.exp(-tt * 2.2) * np.clip(tt / 0.01, 0, 1)


def giggle_run(music, t0, notes, gap=0.09, vel=0.4, glock=False):
    """An instrument giggle (never a voice): quick bouncing notes."""
    for i, m in enumerate(notes):
        music.add(t0 + gap * i, A.glock(M(m), 0.3, vel) if glock else A.pluck(M(m), 0.22, vel))


def make_buses():
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    # a soft dusk bed under everything, so no gap falls silent (check_video, Lead)
    for t0 in np.arange(0.8, 28.0, 2.0):
        music.add(float(t0), A.pad([M(53), M(60)], 3.0, 0.1))
    # 0-1.2: the bouncy glock tune, broken off as the tip lifts
    tune(music, 0.0, upto=1.2, vel=0.5)
    bass_bars(music, 0.0, 1.2)
    sfx.add(0.0, A.boing(0.28, 300))
    sfx.add(0.27, A.boing(0.22, 320))
    squeaks(sfx, 0.02, 0.9, 2100)
    sfx.add(0.9, click(0.18))                                            # the pinch: a tiny paper tick
    sfx.add(1.2, A.pop(0.35))                                            # the "plip" as the tip leaves the paper
    sfx.add(1.2, A.whoosh(0.7, 0.1))                                     # a soft paper slide (1.2-1.9)
    # 1.9-6.5: near-silence, falling notes, a soft pad, the understanding, the sorry swell
    music.add(2.95, A.glock(M(81), 1.0, 0.3))                            # ears droop
    music.add(3.2, A.glock(M(77), 1.4, 0.28))
    music.add(2.8, A.pad([M(62), M(65), M(69)], 3.6, 0.18))
    music.add(4.25, organ_bend(196.0, 196.0, 1.3, 0.9))                  # one low held note, no bend (R2-1)
    sfx.add(5.4, A.tap(0.45))                                            # the marker back in her paw
    music.add(5.8, A.pad([M(58), M(62), M(65)], 1.2, 0.26))
    music.add(6.2, A.pad([M(57), M(60), M(65)], 1.4, 0.26))
    music.add(6.0, A.glock(M(84), 0.6, 0.25))                            # her ears spring up
    # 6.5-10.6: gag 1: tick-tock, the rest, the wobbly bend, one low giggle note
    for i, tt in enumerate(np.arange(6.5, 8.4, BEAT)):
        sfx.add(float(tt), A.woodblock(i % 2 == 0, 0.16))
    for tt, m in ((6.9, 77), (7.4, 81), (7.9, 84)):
        music.add(tt, A.glock(M(m), 0.9, 0.24))
    bass_bars(music, 6.5, 8.4, vel=0.3)
    sfx.add(6.6, A.tap(0.25))
    music.add(8.8, glock_bend(84, 0.8, 0.12, 0.34))
    music.add(9.6, A.pluck(M(53), 0.35, 0.5))
    sfx.add(9.8, A.boing(0.2, 260))
    # 10.6-20.0: the turns
    bass_bars(music, 10.6, 20.0, vel=0.32)
    tune(music, 10.7 - 2 * BEAT * 0.5, upto=11.15, vel=0.42, step=0.5)  # Snip's phrase again ...
    music.add(11.2, A.glock(M(89), 1.6, 0.5))                            # ... resolved: the C closes into an O
    music.add(11.2, A.pad([M(65), M(69), M(72)], 1.4, 0.18))
    squeaks(sfx, 10.7, 11.2, 2100)
    for i, m in enumerate((81, 84, 89)):
        music.add(12.2 + 0.13 * i, A.glock(M(m), 0.9, 0.36))
    squeaks(sfx, 12.2, 12.6, 2100)
    sfx.add(13.2, A.tap(0.4))                                            # to Pip
    for tt in PIP.footfalls():
        sfx.add(tt, A.woodblock(True, 0.09))
    for tt in SN.footfalls() + CR.footfalls():
        sfx.add(tt, A.tap(0.22))
    for i, m in enumerate((96, 93, 89)):                                 # Pip's phrase: an octave up, shorter
        music.add(14.4 + 0.2 * i, A.glock(M(m), 0.6, 0.3))
        music.add(15.1 + 0.2 * i, A.glock(M(m + 3 if i == 0 else m), 0.6, 0.3))
    squeaks(sfx, 14.4, 15.0, 2600, gap=0.2, dur=0.16)
    squeaks(sfx, 15.1, 15.7, 2600, gap=0.2, dur=0.16)
    for tt in (14.45, 18.45, 18.7):                                      # the tongue trills
        sfx.add(tt, A.glock(M(98), 0.25, 0.16))
        sfx.add(tt + 0.08, A.glock(M(101), 0.25, 0.16))
    sfx.add(17.6, A.tap(0.4))                                            # to Crinkle
    sfx.add(17.75, A.boing(0.2, 340))
    for i, m in enumerate((53, 57, 60, 65)):                             # Crinkle's phrase: low organ, slow
        music.add(18.4 + 0.4 * i, MX.organ(A.midi(m), 0.45, 0.45))
    squeaks(sfx, 18.4, 20.0, 1700, gap=0.45, dur=0.4)
    # 20.0-23.0: gag 2: one held note, the big squeak, the fwump, giggles
    music.add(20.0, MX.organ(A.midi(65), 0.5, 0.35))
    sfx.add(20.4, toy_squeak(0.3, SQUEAK_VEL))
    sfx.add(20.6, fwump(0.5))
    giggle_run(music, 21.4, (53, 57, 55, 60, 57, 62), gap=0.1, vel=0.42)
    sfx.add(21.45, A.boing(0.2, 240))
    sfx.add(21.85, A.boing(0.2, 250))
    sfx.add(22.2, fwump(0.25))
    giggle_run(music, 22.5, (89, 93, 91, 96), gap=0.08, vel=0.3, glock=True)   # Pip's, two octaves up
    # 23.0-26.2: the hand, the click, the glow
    sfx.add(22.95, A.whoosh(0.5, 0.3))
    music.add(23.0, A.pad([M(53), M(60), M(65)], 2.0, 0.2))             # a held, careful chord
    sfx.add(T_CLICK, click(0.5))
    sfx.add(T_CLICK + 0.05, A.twinkle(0.18))
    for i, m in enumerate((77, 81, 84, 89, 93, 96)):                     # the rising run as it goes in ...
        music.add(24.45 + 0.11 * i, A.glock(M(m), 1.2, 0.26 + 0.02 * i))
    music.add(25.1, A.pad([M(53), M(65), M(69), M(72), M(79)], 1.6, 0.3))   # ... into F add9 (swell 25.0-26.2)
    music.add(25.1, A.glock(M(91), 1.6, 0.26))
    sfx.add(25.15, A.twinkle(0.14, notes=(103, 108, 101, 106, 110)))
    sfx.add(24.85, A.whoosh(0.4, 0.22))
    music.add(25.5, MX.organ(A.midi(53), 1.0, 0.22))
    # 26.2-30.0: gag 3: the reprise, the rest, the swish, the look back, the giggle, the end chord
    tune(music, 26.2, upto=27.9, vel=0.46)
    bass_bars(music, 26.2, 27.9, vel=0.4)
    for i in range(4):
        sfx.add(26.4 + 0.375 * i, A.boing(0.22, 260))
    for i in range(3):
        sfx.add(26.8 + 0.37 * i, A.boing(0.14, 520))
    sfx.add(26.6, A.boing(0.25, 300))
    sfx.add(28.2, A.whoosh(0.3, 0.25))                                   # paper swish: the spin
    sfx.add(28.5, A.boing(0.2, 280))
    sfx.add(28.75, A.boing(0.2, 300))
    music.add(29.05, A.glock(M(81), 0.5, 0.3))                           # two rising notes on the look back
    music.add(29.2, A.glock(M(84), 0.5, 0.32))
    giggle_run(music, 29.3, (53, 57, 55, 60), gap=0.1, vel=0.4)
    music.add(29.7, A.pad([M(53), M(65), M(69), M(72)], 0.3, 0.3))     # the end chord
    for m in (77, 81, 84):
        music.add(29.7, A.glock(M(m), 0.3, 0.3))
    return music, sfx


def _momentary(path):
    import re
    import subprocess
    err = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True,
                         text=True).stderr
    ts, ms = [], []
    for m in re.finditer(r"t:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+|-inf)", err):
        ts.append(float(m.group(1)))
        ms.append(-70.0 if "inf" in m.group(2) else float(m.group(2)))
    v = re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", err, re.M)
    return np.array(ts), np.array(ms), (float(v[-1]) if v else None)


def build_audio(path):
    music, sfx = make_buses()
    m = A.reverb(music.normalized(), 0.22)
    s = A.reverb(sfx.normalized(), 0.08)
    nm = lambda x: x / max(1e-9, abs(x).max())  # noqa: E731
    y = 0.6 * nm(m) + 0.6 * nm(s)
    y = y / max(1.0, abs(y).max() / 0.95)
    A.write_wav(path, y, fade_out=0.25)
    for _ in range(3):                                   # loudness last: bring it near -14 LUFS
        _, _, lufs = _momentary(path)
        g = 10 ** ((-14.0 - lufs) / 20)
        y = 0.97 * np.tanh(y * g / 0.97)
        A.write_wav(path, y, fade_out=0.25)
    ts, ms, lufs = _momentary(path)
    pre = ms[(ts > 23.5) & (ts <= 25.0)]
    swell = ms[(ts > 25.0) & (ts <= 26.2)]
    sq = ms[(ts > 20.35) & (ts <= 20.9)].max()
    chord = ms[(ts > 29.7) & (ts <= 30.0)].max()
    print(f"audio {lufs} LUFS; glow swell max {swell.max():.1f} vs previous 1.5 s max {pre.max():.1f} / "
          f"min {pre.min():.1f} (rise over the max {swell.max() - pre.max():.1f} LU)")
    print(f"{'ok  ' if sq - chord <= 3.0 else 'FAIL'} R3-1: big squeak momentary max {sq:.1f} vs end chord "
          f"{chord:.1f} LUFS (difference {sq - chord:+.1f} LU, need <= +3)")


# ---------------------------------------------------------------- key sheet (r3: every changed shot, its edges, beats)
KEYS = [0.0, 0.6, 1.0, 1.5, 2.2, 2.4, 2.8, 3.5, 4.0, 4.5, 4.8, 5.0, 5.6, 5.9, 6.0, 6.3, 6.8, 8.6, 9.1, 9.6,
        10.6, 12.8, 14.3, 16.7, 17.2, 18.3, 20.2, 20.7, 21.2, 21.6, 22.2, 22.8, 23.1, 23.2, 23.4, 24.0, 24.8, 25.8,
        26.2, 27.0, 27.5, 28.0, 28.4, 28.6, 29.0, 29.5, 29.9]          # r3: changed shots, their edges, the beats


def sheet(frames, path, w=480, cols=8):
    h = int(w * 1920 / 1080)
    gap, lab = 16, 40
    rows = (len(frames) + cols - 1) // cols
    S = Image.new("RGB", (cols * w + (cols + 1) * gap, rows * (h + lab) + (rows + 1) * gap), (34, 34, 40))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(S)
    for i, (t, im) in enumerate(frames):
        r, c = divmod(i, cols)
        x, y = gap + c * (w + gap), gap + r * (h + lab + gap)
        d.text((x + 4, y + 4), f"{t:.2f} s", fill=(240, 240, 240), font=font)
        S.paste(im.resize((w, h), Image.LANCZOS), (x, y + lab))
    S.save(path)
    print("wrote", path, S.size)


def _key_one(t):
    im = render_frame(t, fresh=True)
    return t, im.tobytes(), L.luma(im)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    args = sys.argv[1:]
    if args[:1] == ["--still"] and len(args) >= 2:
        for a in args[1:]:
            tt = float(a)
            im = render_frame(tt, fresh=True)
            p = os.path.join(OUT_DIR, f"s_{tt:05.2f}_r{RES:g}.png")
            im.save(p)
            print(p, shot_at(tt)[0], "luma", round(L.luma(im), 1))
    elif args == ["--keys"] or args[:1] == ["--sheet"]:
        import multiprocessing as mp
        times = KEYS if args == ["--keys"] else [float(a) for a in args[1:]]
        with mp.get_context("fork").Pool(8) as pool:
            res = pool.map(_key_one, times)
        for t, _, lu in res:
            print(f"{t:.2f} luma {lu:.1f}")
        frames = [(t, Image.frombytes("RGB", (1080, 1920), b)) for t, b, _ in res]
        out = (os.path.join(ROOT, "reviews", "ep11_short_transform_keys.png") if args == ["--keys"]
               else os.path.join(OUT_DIR, "sheet.png"))
        sheet(frames, out)
    elif args == ["--cuts"]:
        print(",".join(f"{c:g}" for c in CUTS))
    elif args == ["--check"]:
        print("\n".join(checks()))
    elif args == ["--hires"]:
        if RES < 2.5:
            sys.exit("run with EP11S_RES=3")
        os.makedirs(HI_DIR, exist_ok=True)
        for a, b in hi_range():
            for d in range(int(math.ceil(a * K.DPS - 1e-6)), int(math.ceil(b * K.DPS - 1e-6))):
                render_frame(d / K.DPS, fresh=True).save(os.path.join(HI_DIR, f"d{d:05d}.png"))
                print("hi", d, flush=True)
        with open(os.path.join(HI_DIR, "code_hash.txt"), "w") as fh:
            fh.write(code_hash())
    elif args == ["--audio"]:
        build_audio(os.path.join(ROOT, "build", "ep11s_audio.wav"))
    elif args == ["--render"]:
        if RES > 2.5:
            sys.exit("render at the normal scale (no EP11S_RES)")
        wav = os.path.join(ROOT, "build", "ep11s_audio.wav")
        build_audio(wav)
        K.render_video(os.path.abspath(__file__), os.path.join(ROOT, "output", "ep11_short_transform.mp4"), wav, DUR,
                       "vert")
    else:
        sys.exit("usage: ep11_short_transform.py --still T [T ...] | --keys | --sheet T ... | --cuts | --check | "
                 "--hires | --audio | --render")
