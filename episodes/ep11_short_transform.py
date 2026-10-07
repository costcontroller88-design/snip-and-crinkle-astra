"""Episode 11 transformation Short (plan section 7(b), r2 + sb1): "Plain Pumpkin Becomes a Glowing Friend!"

29.4 s, vertical 1080x1920, its own performances on the Episode 11 porch (early-evening light all through). Lesson:
when it's a friend's turn, wait until they finish; then it's your turn. One marker (black ink, blue body) passes
Snip -> Crinkle (the take) -> Snip (given back) -> Pip -> Crinkle; the grown-up's hand puts a battery tea light in the
paper lantern (props_lantern) and the whole paper glows.

Run:  python3 episodes/ep11_short_transform.py --still T     (one frame through the shot camera -> build/ep11s/)
      python3 episodes/ep11_short_transform.py --keys        (risky-shot check sheet -> reviews/ep11_short_transform_keys.png)
      python3 episodes/ep11_short_transform.py --cuts        (cut times for check_video)
      python3 episodes/ep11_short_transform.py --check       (measured clearances and gaps, printed)
      EP11S_RES=3 python3 episodes/ep11_short_transform.py --hires   (camera T, 2.6x, at 3x -> build/ep11s_hi/;
                                                                    run it before --render)
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

hires.set_res(float(os.environ.get("EP11S_RES", "2")))     # 3 only for the separate camera-T pass (--hires)

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
DUR = 29.4
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
CAP = 40.0                              # a pinch near the top end: the paw this far behind the grip point
U_SN, U_PIP, U_CR = _unit(0.39, 0.92), _unit(0.5, 0.87), _unit(-0.3, 0.95)
U_GIVE = _unit(0.97, -0.24)             # Pip holds it up to Crinkle, pointing at his paw (tip away from every face)
ANG = {k: RP.marker_angle(u) for k, u in (("sn", U_SN), ("pip", U_PIP), ("cr", U_CR), ("give", U_GIVE))}
A_HANG, A_HOLD, A_FLAT = 4.0, -12.0, 90.0    # A_FLAT: lying flat, tip pointing right (away)
C = PL.C_STOP

STROKE_KEYS = {"eye_l": [(0.0, 0.30), (0.6, 0.50), (0.8, C), (8.6, C), (9.1, 1.0)],
               "eye_r": [(10.2, 0.0), (10.8, 1.0)],
               "heart_l": [(13.8, 0.0), (14.5, 1.0)], "heart_r": [(14.7, 0.0), (15.4, 1.0)],
               "smile": [(18.4, 0.0), (20.6, 1.0)]}


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
BACK = {"pip": [(-1.0, 11.9)], "cr": [(5.9, 16.8)], "sn": []}       # paws / wings behind the back (T2)
SN_X1, PIP_X1, CR_X1 = 700, 770, 1200                               # after the turns (and clear of the hand)

# ---- shot 1 + 1b (0-2.0): Snip draws; Crinkle bounces, leans in and takes the marker (the take, camera T)
SN.reach(-0.3, 0.0, "r", (PL.tip_world("eye_l", 0.30)[0] - TIP_L * U_SN[0],
                          PL.tip_world("eye_l", 0.30)[1] - TIP_L * U_SN[1]))
follow(SN, "r", "eye_l", 0.0, 0.6, 0.30, 0.50, U_SN)
follow(SN, "r", "eye_l", 0.6, 0.8, 0.50, C, U_SN)
W_SN = SN.paw(0.8, "r")[0]                                          # her paw stays exactly here until 5.4
for _t in np.arange(0.8, 5.39, 0.2):                                # (re-aimed every 0.2 s: breathing never moves it)
    SN.reach(float(_t), float(min(5.4, _t + 0.2)), "r", W_SN, "lin")
CAP_P = (W_SN[0] - CAP * U_SN[0], W_SN[1] - CAP * U_SN[1])          # the marker's top end (where he pinches)
LIFT = (1006, 1298)
CR.hop(0.0, 0.3, 1, 6)
CR.to(0.3, 0.6, "io", lean=-10, sq=0.92)
CR.reach(0.3, 0.8, "l", (CAP_P[0] + 34, CAP_P[1] - 30))
CR.reach(0.8, 1.0, "l", CAP_P, "io")                                # slow pinch (no tug)
CR.reach(1.1, 1.6, "l", LIFT, "io")                                 # tip leaves the paper at 1.1: the "C"
SN.face(1.15, mouth="o", brows="up").to(1.6, 1.8, "io", look_x=8, look_y=9)   # eyes: the C, then her empty paw
SN.ears(2.1, 2.5, "sad").to(2.2, 2.6, "io", head_dy=4, look_x=4, look_y=6)
SN.face(2.3, eyes="glassy", brows="sad", mouth="frown").face(3.8, eyes="normal")
# ---- shot 2 (2.0-5.4, B2): he crouches to draw; looks; understands; gives it back; bows
TIP_CR = (1018, 1418)                                               # 20 short of the smile's end: no mark
P_DRAW = (TIP_CR[0] - (TIP_L + CAP) * U_CR[0], TIP_CR[1] - (TIP_L + CAP) * U_CR[1])
CR.to(2.0, 2.5, "io", lean=-8, sq=0.94).face(2.0, eyes="normal", mouth="yum_l", brows="think")
CR.reach(2.0, 2.5, "l", P_DRAW)
CR.to(2.5, 2.65, "io", look_x=-10, look_y=4).to(2.75, 2.9, "io", look_x=-13, look_y=9)
CR.to(3.0, 3.15, "io", look_x=-10, look_y=-10)
CR.face(3.2, mouth="o", brows="sorry").to(3.2, 3.5, "io", sq=0.97, head_dy=5, lean=-6)
CR.reach(3.5, 4.0, "l", CAP_P, "io")                                # fits it into her open fingers, tip on the line
CR.face(3.9, eyes="normal", mouth="smile", brows="sorry")
CR_HP = CR.a.head_pivot(CR.state(3.95))
CHEST = (CR_HP[0] - 22, CR_HP[1] + 108)
CR.reach(4.0, 4.4, "l", CHEST, "out")                               # lets go; open paw straight back to his chest
CR.to(4.4, 4.75, "io", lean=-14, head_dy=10).to(4.75, 5.1, "io", lean=-6, head_dy=4)   # a small bow
SN.ears(4.8, 5.0, "happy", "back").face(4.8, eyes="happy", mouth="smile", brows="calm")
SN.to(4.95, 5.1, "io", head_dy=10).to(5.1, 5.3, "io", head_dy=0)                        # nod
# ---- shot 3 (5.4-7.2, A): he straightens, half step back, copies Pip's waiting pose; they sway together
CR.to(5.4, 5.8, "io", lean=0, sq=1.0, head_dy=0, turn=-0.35).walk(5.4, 5.8, 1100, steps=1)
CR.face(5.5, eyes="happy", mouth="smile", brows="calm").to(5.5, 5.7, "io", look_x=-12, look_y=2)
CR.to(5.6, 5.9, "io", arm_l=28, elb_l=0, arm_r=-28, elb_r=0)
for i, (a, b) in enumerate(((6.2, 6.7), (6.7, 7.2))):
    CR.to(a, b, "io", lean=6 if i == 0 else -6)
t = 7.2
while t < 16.4:                                                       # keeps swaying gently while he waits
    CR.to(t, t + 0.7, "io", lean=-3 if int((t - 7.2) / 0.7) % 2 == 0 else 3)
    t += 0.7
CR.to(7.0, 7.3, "io", look_x=-10, look_y=8)                          # eyes on Snip's drawing
t = 0.0
while t < 11.6:                                                       # Pip's small waiting sway
    PIP.to(t, t + 0.55, "io", lean=3 if int(t / 0.55) % 2 == 0 else -3)
    t += 0.55
PIP.to(6.1, 6.3, "io", look_x=10, look_y=0, hturn=0.25).face(6.3, eyes="happy", mouth="smile_open", brows="calm")
PIP.to(7.3, 7.5, "io", look_x=8, look_y=8, hturn=0.0).face(7.4, eyes="normal", mouth="smile")
SN.reach(5.4, 5.7, "r", (W_SN[0] - 6, W_SN[1] - 16))                 # tip just off the paper while she watches
SN.to(5.5, 5.7, "io", look_x=10, look_y=0).face(5.5, eyes="happy", mouth="smile", brows="calm")
SN.to(6.3, 6.5, "io", hturn=-0.35, look_x=-10, look_y=2).to(6.95, 7.15, "io", hturn=0.0, look_x=4, look_y=6)
SN.face(7.1, eyes="normal", brows="think")
# ---- shot 5 (8.4-11.8, B): Snip closes the C, then the second eye
follow(SN, "r", "eye_l", 8.6, 9.1, C, 1.0, U_SN, lead=0.2, n=8)
SN.face(9.15, eyes="happy", mouth="smile", brows="calm")
SN.reach(9.2, 9.5, "r", (SN.paw(9.1, "r")[0][0] - 4, SN.paw(9.1, "r")[0][1] - 14))
SN.face(10.0, eyes="normal", brows="think")
follow(SN, "r", "eye_r", 10.2, 10.8, 0.0, 1.0, U_SN, lead=0.35, n=10)
SN.face(10.85, eyes="sparkle", mouth="smile_open", brows="up").reach(10.9, 11.3, "r", (885, 1290))
# ---- shot 6 (11.8-13.6, A): Snip gives the marker to Pip, steps back, sweeps a paw; Pip waddles in
M_GIVE = (742, 1330)
SN.to(11.8, 12.05, "io", turn=-0.3, look_x=-8, look_y=6).face(11.8, eyes="happy", mouth="smile_open", brows="up")
SN.reach(11.85, 12.15, "r", M_GIVE)
PIP.to(11.75, 11.9, "io", arm_l=-12, elb_l=16, arm_r=12, elb_r=-16).face(11.9, eyes="sparkle", mouth="smile_open")
PIP_TAKE = (M_GIVE[0] + 18 * U_SN[0], M_GIVE[1] + 18 * U_SN[1])
PIP.reach(11.95, 12.2, "r", PIP_TAKE)
SN.reach(12.25, 12.45, "r", (770, 1360)).walk(12.3, 12.8, SN_X1, steps=2)
SN.to(12.4, 12.7, "io", turn=0.35, look_x=8, look_y=6)
SN.reach(12.55, 12.85, "r", (820, 1300), "back").reach(13.2, 13.5, "r", (760, 1395))
PIP.walk(12.45, 13.5, 845, steps=4).to(13.5, 13.65, "io", turn=0.3, look_x=10, look_y=10)
PIP.reach(12.3, 12.6, "r", (742, 1384))                             # carried flat in front of her tummy
H_WAIT, H_PIP = (968, 1332), (975, 1322)
# ---- shot 7 (13.6-16.6, B): Pip draws the heart nose (black), tongue tip out, copying Crinkle
follow(PIP, "r", "heart_l", 13.8, 14.5, 0.0, 1.0, U_PIP, lead=0.3, n=12)
PIP.reach(14.5, 14.7, "r", (PL.tip_world("heart_r", 0)[0] - TIP_L * U_PIP[0],
                            PL.tip_world("heart_r", 0)[1] - TIP_L * U_PIP[1]))
follow(PIP, "r", "heart_r", 14.7, 15.4, 0.0, 1.0, U_PIP, n=12)
for tt, m in ((13.85, "yum"), (14.3, "yum_l"), (14.75, "yum"), (15.2, "yum_l")):
    PIP.face(tt, mouth=m, brows="think")
PIP.face(15.5, eyes="sparkle", mouth="smile_open", brows="up").reach(15.45, 15.9, "r", H_WAIT)   # off the face, ready
PIP.to(15.45, 15.9, "io", turn=0.25)
CR.face(14.0, eyes="happy", mouth="smile", brows="calm")
# ---- shot 8 (16.6-18.2, A): Pip holds the marker up to Crinkle: his turn, given by her
PIP.to(16.6, 16.9, "io", turn=0.25, look_x=10, look_y=-10).to(16.7, 17.1, "io", lean=6).to(17.4, 17.7, "io", lean=0).face(16.7, eyes="happy", mouth="smile_open", brows="up")
PIP.reach(16.7, 17.1, "r", H_PIP)
G_GIVE = (H_PIP[0] + CAP * U_GIVE[0], H_PIP[1] + CAP * U_GIVE[1])  # the marker's grip point while she holds it up
P_TAKE = (G_GIVE[0] + 5 * U_GIVE[0], G_GIVE[1] + 5 * U_GIVE[1])
CR.to(16.75, 16.9, "io", arm_l=-10, elb_l=14, arm_r=10, elb_r=-14).to(16.8, 17.1, "io", sq=0.9, lean=-10)
CR.face(16.8, eyes="sparkle", mouth="smile_open", brows="up").to(16.8, 17.0, "io", look_x=-8, look_y=6)
CR.reach(16.95, 17.3, "l", P_TAKE)
PIP.rest_wings(17.4, 17.7).walk(17.6, 18.1, PIP_X1, steps=2).to(17.9, 18.2, "io", turn=0.35, look_x=10, look_y=8)
CR.reach(17.4, 17.8, "l", (1055, 1290)).wiggle(17.5, "lean", 4, 5, 3).to(17.8, 18.1, "io", sq=0.96, lean=-4)
# ---- shot 9 (18.2-22.0, B): the big smile, slowly; his tongue slides with the marker; paw out; he holds it flat on his tummy
CR.to(18.2, 18.4, "io", sq=0.88, lean=-12).face(18.3, eyes="normal", mouth="yum_l", brows="think")
CR.to(18.3, 18.5, "io", look_x=-8, look_y=10)
follow(CR, "l", "smile", 18.4, 20.6, 0.0, 1.0, U_CR, off=-5, lead=0.2, n=36)
for tt, m in ((19.0, "yum_c"), (19.5, "yum"), (20.0, "yum_c"), (20.4, "yum_l")):
    CR.face(tt, mouth=m)
CR.face(20.65, eyes="happy", mouth="smile_open", brows="up")
CR.to(20.6, 21.0, "io", sq=1.0, lean=0)
CR.reach(20.6, 20.95, "l", (1104, 1336))                            # paw out to his chest, below his face
CR.walk(20.95, 21.6, CR_X1, steps=2)                                # makes room for the hand (clearance check)
CR.reach(21.6, 21.9, "l", (CR_X1 + 8, 1386))                        # ... then on his tummy, clear of the lantern
PIP.face(18.6, mouth="yum").face(19.4, mouth="smile").to(18.4, 18.6, "io", look_x=10, look_y=10)
SN.face(18.5, eyes="happy", mouth="smile", brows="calm")
# ---- shots 10-11 (22.0-29.4): the hand and the tea light; the glow; the dance
for perf, lx in ((SN, 6), (CR, -6), (PIP, 6)):
    perf.to(22.05, 22.35, "io", look_x=lx, look_y=-12)
    perf.face(22.1, eyes="normal", mouth="smile", brows="up")
    perf.to(23.7, 24.4, "io", look_x=lx, look_y=10)
    perf.face(24.6, eyes="sparkle", mouth="smile_open", brows="up")
SN.ears(24.6, 24.9, "perk")
CR.to(21.9, 22.3, "io", lean=-9).to(24.6, 25.0, "io", lean=0)                # leans out of the hand's way
PIP.to(21.9, 22.3, "io", lean=6).to(24.6, 25.0, "io", lean=0)
SN.to(21.9, 22.3, "io", lean=5).to(24.6, 25.0, "io", lean=0)
SN.to(26.7, 26.9, "io", sq=0.92).hop(26.9, 27.3, 1, 26).to(27.3, 27.5, "io", sq=1.0)
T_DANCE = (26.8, 28.0)
TUMMY = (CR_X1 + 8, 1388)
CR.reach(26.4, 26.8, "l", TUMMY).to(26.4, 26.8, "io", arm_r=150, elb_r=-20)
for i in range(4):
    a = T_DANCE[0] + i * 0.3
    CR.to(a, a + 0.3, "io", lean=7 if i % 2 == 0 else -7, tilt=4 if i % 2 == 0 else -4)
CR.to(28.0, 28.35, "io", lean=0, tilt=0, arm_r=10, elb_r=-14).hop(T_DANCE[0], T_DANCE[1], 4, 12)
CR.face(26.8, eyes="happy", mouth="smile_open", brows="up")
PIP.dance(27.2, 28.4, beats=4).face(27.2, eyes="happy", mouth="smile_open", brows="up")
SN.face(27.4, eyes="happy", mouth="smile_open", brows="up")


# ---------------------------------------------------------------- the marker's holder schedule
def marker_pose(t):
    """(who, side, off, angle): the marker's grip point is the holder's paw + off along the marker."""
    if t < 1.1:
        return "sn", "r", 0.0, ANG["sn"]
    if t < 4.0:
        ang = _ease(t, [(1.1, ANG["sn"]), (1.7, A_HANG), (2.0, A_HANG), (2.5, ANG["cr"]), (3.5, ANG["cr"]),
                        (4.0, ANG["sn"])])
        return "cr", "l", CAP, ang
    if t < 12.2:
        return "sn", "r", 0.0, ANG["sn"]
    if t < 17.3:
        off = _ease(t, [(12.2, -18.0), (12.6, 0.0), (15.45, 0.0), (15.9, CAP)])
        ang = _ease(t, [(12.2, ANG["sn"]), (12.6, A_FLAT), (13.5, A_FLAT), (13.75, ANG["pip"]), (15.45, ANG["pip"]),
                        (15.9, ANG["give"])])
        return "pip", "r", off, ang
    if t < 20.95:
        ang = _ease(t, [(17.3, ANG["give"]), (17.8, A_HOLD), (18.2, A_HOLD), (18.4, ANG["cr"]), (20.6, ANG["cr"]),
                        (20.95, A_FLAT)])
        return "cr", "l", -5.0, ang
    return "cr", "l", -5.0, A_FLAT


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
    if t < 11.9:
        out.append(("sn", "r"))
    if 0.3 <= t < 5.0 or 16.85 <= t < 21.0:
        out.append(("cr", "l"))
    if 13.4 <= t < 17.75:
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
T_HAND = (22.0, 24.9)
T_CLICK = 22.7
TEA_HOLD = (955, 1250)                  # the light's top, held above the ring
TEA_IN = (955, 1484)                    # ... on the bottom inside
TEA_GRIP = (0, -3)                      # pinched at its top rim, from straight above
T_GLOW = (23.95, 24.75)


def tea_top(t):
    return _ease(t, [(22.0, (955, 640)), (22.5, TEA_HOLD), (23.7, TEA_HOLD), (24.5, TEA_IN)])


def hand_state(t):
    if not T_HAND[0] <= t < T_HAND[1]:
        return None
    if t < 24.5:
        top = tea_top(t)
        grip = (top[0] + TEA_GRIP[0], top[1] + TEA_GRIP[1])
        hand = "press" if T_CLICK - 0.08 <= t < T_CLICK + 0.14 else "pinch"
        return dict(grip=grip, hand=hand, top=top)
    g0 = (TEA_IN[0] + TEA_GRIP[0], TEA_IN[1] + TEA_GRIP[1])
    return dict(grip=_ease(t, [(24.5, g0), (24.9, (955, 640))]), hand="pinch", top=None)


def glow_k(t):
    return ease_in_out(seg(t, *T_GLOW))


def draw_hand(im, cam, hs, t):
    hand = H.HANDS[hs["hand"]]
    g = hs["grip"]
    sh = (g[0] - 4, g[1] - 1612)                  # the arm comes straight down (the grown-up lowers the whole arm)
    if hs["top"] is not None:
        place(im, TEA[t >= T_CLICK], cam.S(hs["top"]), scale=TEA_S)
    W = ARM.wrist_for(sh, g, hand, -1)
    ARM.draw_hand(im, cam, sh, W, hand, -1)


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
    sts = states(t, d)
    for who in (("sn", "cr", "pip") if 2.0 <= t < 5.4 else ("cr", "sn", "pip")):
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
    WORLD.front(f, T_LIGHT)
    return f


# ---------------------------------------------------------------- cameras (plan b4; vertical)
CAMS = {"A": ((880, 1250), 1.7), "T": ((950, 1300), 2.6), "B2": ((920, 1270), 1.8), "K": ((1060, 1180), 1.9),
        "B": ((950, 1320), 2.0), "B3": ((990, 1290), 1.6)}   # B3: the light goes in (room for the hand, Crinkle in)
END_C, END_Z = (975, 1215), 1.4
T_PULL = (26.0, 28.0)
SHOTS = [(0.0, "A"), (0.6, "T"), (2.0, "B2"), (5.4, "A"), (7.2, "K"), (8.4, "B"), (11.8, "A"), (13.6, "B"),
         (16.6, "A"), (18.2, "B"), (22.0, "B3")]
CUTS = [s[0] for s in SHOTS[1:]]        # 26.0 is not a cut (the pull back starts)


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
    if t >= T_PULL[0]:
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
    return [(0.6, 2.0)]


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


def checks():
    lines = []
    # 1. the give-back: his paw's gap from the marker (>= 40 by 4.15); the marker still from 4.0
    for tt in (4.0, 4.1, 4.15, 4.2, 4.4):
        sts = states(tt)
        paw = _mask_of(lambda im: CR.a._arm(im, CAM, sts["cr"], "l"))
        mk = _mask_of(lambda im: draw_marker(im, tt, sts))
        lines.append(f"give-back {tt:.2f}: Crinkle's arm to marker gap {_gap(paw, mk):.1f}")
    tips = [marker_tip_world(tt, states(tt)) for tt in np.arange(4.0, 5.36, 1 / 15)]
    mv = max(math.hypot(p[0] - tips[0][0], p[1] - tips[0][1]) for p in tips)
    lines.append(f"marker tip movement 4.0-5.35: max {mv:.2f} units; tip {tuple(round(v, 1) for v in tips[0])}, "
                 f"C end {tuple(round(v, 1) for v in PL.tip_world('eye_l', C))}")
    # 2. the take: Snip's paw does not move 0.8-2.0; marker's path
    ps = [SN.paw(tt, "r")[0] for tt in np.arange(0.8, 2.01, 1 / 15)]
    lines.append(f"Snip's paw movement 0.8-2.0: {max(math.hypot(p[0] - ps[0][0], p[1] - ps[0][1]) for p in ps):.2f}")
    # 3. marker to Pip's face at the hand-up, and marker tip to every face over the whole Short
    worst = {}
    for tt in list(np.arange(16.6, 17.8, 1 / 15)) + [17.3]:
        sts = states(tt)
        mk = _mask_of(lambda im: draw_marker(im, tt, sts))
        worst[round(tt, 2)] = _gap(mk, head_mask("pip", sts["pip"]))
    lines.append(f"marker to Pip's head 17.3: {worst[17.3]:.1f}; min 16.6-17.8: {min(worst.values()):.1f} "
                 f"at {min(worst, key=worst.get)}")
    tipmin = (1e9, None)
    body = {}
    for tt in np.arange(0.0, DUR, 0.2):
        sts = states(tt)
        tip = marker_tip_world(tt, sts)
        tm = Image.new("L", (int(1080 * RES), int(1920 * RES)), 0)
        x, y = CAM.S(tip)
        ImageDraw.Draw(tm).ellipse([x - 2, y - 2, x + 2, y + 2], fill=255)
        mk = _mask_of(lambda im: draw_marker(im, tt, sts))
        for who in ("sn", "cr", "pip"):
            hmk = head_mask(who, sts[who])
            g = _gap(tm, hmk)
            if g < tipmin[0]:
                tipmin = (g, (round(float(tt), 1), who))
            gb = _gap(mk, hmk)
            if gb < body.get(who, (1e9,))[0]:
                body[who] = (round(gb, 1), round(float(tt), 1))
    lines.append(f"marker tip to nearest head (whole Short, every 0.2 s): {tipmin[0]:.1f} at {tipmin[1]}")
    lines.append(f"whole marker to each head (min, at): {body}")
    # 4. the hand and the tea light: gap to every head, 22.0-24.9
    hm = (1e9, None)
    for tt in np.arange(22.0, 24.9, 1 / 15):
        sts = states(tt)
        hs = hand_state(tt)
        hmask = _mask_of(lambda im: draw_hand(im, CAM, hs, tt))
        for who in ("sn", "cr", "pip"):
            g = _gap(hmask, head_mask(who, sts[who]))
            if g < hm[0]:
                hm = (g, (round(float(tt), 2), who))
    lines.append(f"hand + tea light to nearest head 22.0-24.9: {hm[0]:.1f} at {hm[1]}")
    # 5. the lantern from 22.0: nobody's paw, wing or foot on it (arms over it, or anything over the ring)
    for tt in np.arange(22.0, DUR, 0.25):
        if arms_over(tt):
            lines.append(f"!! arms drawn over the lantern at {tt:.2f}")
            break
    else:
        lines.append("no arm drawn over the lantern 22.0-29.4 (arms_over empty)")
    return lines


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


def make_buses():
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    # 0-1.1: the bouncy glock tune, broken off at the tip's lift
    tune(music, 0.0, upto=1.1, vel=0.5)
    bass_bars(music, 0.0, 1.1)
    sfx.add(0.0, A.boing(0.28, 300))
    sfx.add(0.27, A.boing(0.22, 320))
    squeaks(sfx, 0.02, 0.8, 2100)
    sfx.add(1.1, A.pop(0.35))                                            # the "plip" as the tip leaves the paper
    # 1.1-5.4: near-silence, falling notes, a soft pad, the understanding, the sorry swell
    music.add(2.2, A.glock(M(81), 1.0, 0.3))
    music.add(2.5, A.glock(M(77), 1.4, 0.28))
    music.add(2.6, A.pad([M(62), M(65), M(69)], 2.8, 0.18))
    music.add(3.2, organ_bend(220.0, 174.6, 0.75, 0.9))
    sfx.add(4.0, A.tap(0.45))                                            # the marker back in her paw
    music.add(4.4, A.pad([M(58), M(62), M(65)], 1.2, 0.26))
    music.add(4.9, A.pad([M(57), M(60), M(65)], 1.6, 0.26))
    music.add(4.8, A.glock(M(84), 0.6, 0.25))
    # 5.4-8.4: the patient tick-tock
    for i, tt in enumerate(np.arange(5.4, 8.4, BEAT)):
        sfx.add(float(tt), A.woodblock(i % 2 == 0, 0.16))
    for tt, m in ((5.4, 77), (6.55, 81), (7.7, 84)):
        music.add(tt, A.glock(M(m), 1.4, 0.24))
    bass_bars(music, 5.4, 8.4, vel=0.3)
    sfx.add(5.6, A.tap(0.25))
    # 8.4-22.0: the turns
    bass_bars(music, 8.4, 22.0, vel=0.32)
    tune(music, 8.6 - 2 * BEAT * 0.5, upto=9.05, vel=0.42, step=0.5)    # Snip's phrase again ...
    music.add(9.1, A.glock(M(89), 1.6, 0.5))                             # ... resolved: the C closes into an O
    music.add(9.1, A.pad([M(65), M(69), M(72)], 1.4, 0.18))
    squeaks(sfx, 8.6, 9.1, 2100)
    for i, m in enumerate((81, 84, 89)):
        music.add(10.2 + 0.2 * i, A.glock(M(m), 0.9, 0.36))
    squeaks(sfx, 10.2, 10.8, 2100)
    sfx.add(12.2, A.tap(0.4))                                            # to Pip
    for tt in PIP.footfalls():
        sfx.add(tt, A.woodblock(True, 0.09))
    for tt in SN.footfalls() + CR.footfalls():
        sfx.add(tt, A.tap(0.22))
    for i, m in enumerate((96, 93, 89)):                                 # Pip's phrase: an octave up, shorter
        music.add(13.8 + 0.23 * i, A.glock(M(m), 0.6, 0.3))
        music.add(14.7 + 0.23 * i, A.glock(M(m + 3 if i == 0 else m), 0.6, 0.3))
    squeaks(sfx, 13.8, 14.5, 2600, gap=0.2, dur=0.16)
    squeaks(sfx, 14.7, 15.4, 2600, gap=0.2, dur=0.16)
    for tt in (13.9, 18.5):                                              # the tongue trills
        sfx.add(tt, A.glock(M(98), 0.25, 0.16))
        sfx.add(tt + 0.08, A.glock(M(101), 0.25, 0.16))
    sfx.add(17.3, A.tap(0.4))                                            # to Crinkle
    sfx.add(17.5, A.boing(0.2, 340))
    for i, m in enumerate((53, 57, 60, 65)):                             # Crinkle's phrase: low organ, slow
        music.add(18.4 + 0.55 * i, MX.organ(A.midi(m), 0.6, 0.45))
    squeaks(sfx, 18.4, 20.6, 1700, gap=0.45, dur=0.4)
    # 22.0-26.0: the hand, the click, the glow
    sfx.add(21.95, A.whoosh(0.5, 0.3))
    music.add(22.0, A.pad([M(53), M(60), M(65)], 2.6, 0.2))             # a held, careful chord
    sfx.add(T_CLICK, click(0.5))
    sfx.add(T_CLICK + 0.05, A.twinkle(0.18))
    for i, m in enumerate((77, 81, 84, 89, 93, 96)):                     # the rising run as it goes in ...
        music.add(23.95 + 0.11 * i, A.glock(M(m), 1.2, 0.26 + 0.02 * i))
    music.add(24.65, A.pad([M(53), M(65), M(69), M(72), M(79)], 2.4, 0.3))   # ... into F add9
    music.add(24.65, A.glock(M(91), 2.0, 0.26))
    sfx.add(24.7, A.twinkle(0.14, notes=(103, 108, 101, 106, 110)))
    sfx.add(24.5, A.whoosh(0.4, 0.22))
    music.add(25.3, MX.organ(A.midi(53), 2.0, 0.22))
    # 26.0-29.4: the bouncy reprise, the dance, the end chord
    tune(music, 26.0, vel=0.46)
    bass_bars(music, 26.0, 28.6, vel=0.4)
    for i in range(4):
        sfx.add(T_DANCE[0] + 0.3 * i, A.boing(0.22, 260))
        sfx.add(27.2 + 0.3 * i, A.boing(0.14, 520))
    sfx.add(26.95, A.boing(0.25, 300))
    music.add(28.6, A.pad([M(53), M(65), M(69), M(72)], 1.0, 0.3))
    for m in (77, 81, 84):
        music.add(28.6, A.glock(M(m), 1.0, 0.3))
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
    pre = ms[(ts > 22.5) & (ts <= 24.5)]
    swell = ms[(ts > 24.5) & (ts <= 26.0)]
    print(f"audio {lufs} LUFS; glow swell max {swell.max():.1f} vs previous 2 s max {pre.max():.1f} / "
          f"min {pre.min():.1f} (rise over the max {swell.max() - pre.max():.1f} LU)")


# ---------------------------------------------------------------- key sheet
KEYS = [0.7, 0.9, 1.0, 1.1, 1.3, 1.6, 1.9,                     # the take (camera T)
        3.6, 3.9, 4.0, 4.15, 4.25, 4.4, 4.6,                   # the give-back (B2)
        22.3, 22.7, 23.4, 23.9, 24.1, 24.35, 24.7, 25.5]       # the light in (B)


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
