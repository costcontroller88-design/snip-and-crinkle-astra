"""Pilot episode: "Oops! A Splash of Blue" (about 2 minutes, landscape, rig v2, rendered at 2x).

Built from reviews/pilot02_plan.md. Snip paints the two friends and needs blue for the sky; Crinkle happily
carries the open blue jar over, trips on a toy block that has been on the rug since the first shot, and the
paint sloshes onto the painting. Snip is sad; Crinkle starts to tiptoe away, hears a sniff, stops, thinks
(sneak away or say sorry?), comes back and says sorry; they hug. Then Crinkle fetches a brush to fix it,
gets a blue dot on his nose (Snip giggles), sees that the splash is whale-shaped, and they trace it and paint
it together: eye, tail, spout, waves, a boat with the two of them, bubbles and a rainbow. They step back:
the new painting is better than the first. Paw-bump.

Run:  python3 episodes/pilot02_splash_of_blue.py             (render -> output/pilot02_splash_of_blue.mp4)
      python3 episodes/pilot02_splash_of_blue.py --keys      (key frames -> reviews/pilot02_keys.png)
      python3 episodes/pilot02_splash_of_blue.py --still T   (one full-size frame -> build/)
      python3 episodes/pilot02_splash_of_blue.py --cuts      (print the shot cut times for check_video)
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

import hires  # noqa: E402

hires.set_res(2)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import acting as K  # noqa: E402
import audio as A  # noqa: E402
import music_extra as MX  # noqa: E402
import props_artcorner as P  # noqa: E402
import props_splash as S  # noqa: E402
import rig2 as R  # noqa: E402
import voices as V  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, seg  # noqa: E402

RES = hires.RES
DUR = 124.0
FLOOR = P.FLOOR_Y

# ---------------------------------------------------------------- staging (world design units)
EASEL_X = 800
CANVAS_XY = (631, 930)                         # canvas top-left
CANVAS_MID = (CANVAS_XY[0] + S.CANVAS_W / 2, CANVAS_XY[1] + S.CANVAS_H / 2)
TABLE_X = 1560
TABLE_Y = FLOOR - S.TABLE_TOP
JAR_RED, JAR_YEL, JAR_BLUE, CUP = (1480, TABLE_Y), (1540, TABLE_Y), (1600, TABLE_Y), (1665, TABLE_Y)
BLOCK = (1190, FLOOR + 8)
SN_P, SN_BACK = 460, 420                       # Snip's painting spot, and a step back
CR_TABLE, CR_P = 1440, 1170                    # Crinkle at the table, and at his painting spot


def cv(u, v):
    """Canvas-local -> world."""
    return CANVAS_XY[0] + u, CANVAS_XY[1] + v


CAM = K.Cam("land", P.WORLD_W, P.WORLD_H, P.LAND_Y0, P.VERT_X0, res=RES)
BG = CAM.crop_bg(P.background())

EASEL = P.easel()
BOARD = P.canvas_board()
SUN = P.paint_sun()
FRIENDS = P.paint_friends()
FLOWER = P.paint_flower((240, 112, 140))
SPLASH = S.splash()
DRIPS = [S.drip(L) for _, _, L in S.DRIPS]
LAYERS = {k: f() for k, f in (("face", S.whale_face), ("tail", S.whale_tail), ("spout", S.spout),
                              ("waves", S.waves), ("boat", S.boat), ("bubbles", S.bubbles),
                              ("rainbow", S.rainbow))}
TRACE = S.trace_dot()
OUTLINE = S.whale_outline()
TABLE = S.table()
JARS = {"red": S.jar((240, 112, 104)), "yellow": S.jar((255, 196, 72)), "blue": S.jar(S.BLUE),
        "blue_empty": S.jar(S.BLUE, 0.08)}
CUP_SPR = S.brush_cup()
BLOCK_SPR = S.block()
BRUSH_SN = S.brush().scaled(1.15)
BRUSH_CR = S.brush(tip=S.BLUE_DARK, handle=(120, 196, 120)).scaled(1.2)
L_SN, L_CR = S.BRUSH_LEN * 1.15, S.BRUSH_LEN * 1.2
CLOUD = S.thought_cloud().scaled(0.95)
BUB_HIDE = P.bubble_hide().scaled(1.2)
BUB_SORRY = P.bubble_sorry().scaled(1.2)
QMARK = S.question().scaled(0.9)
BLUE_NOSE = S.blue_nose().scaled(1.2)
SPECKS = [S.slosh_drop(r) for r in (7, 6, 5, 5)]
SPARK = S.sparkle()
SPARK_S = S.sparkle((255, 240, 160))
HEARTS = [S.heart(c) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120))]
SLOSH = [S.slosh_drop(r) for r in (26, 20, 16, 12, 9)]

SN = R.Perf2(R.Puppet("snip", 1.15), seed=1, x=SN_P, y=FLOOR, turn=0.6, eyes="happy", mouth="smile", brows="calm")
CR = R.Perf2(R.Puppet("crinkle", 1.2), seed=2, x=2250, y=FLOOR, turn=-0.6, eyes="happy", mouth="smile",
             brows="up")

U_SN = (0.82, -0.57)                           # how each friend holds the brush to paint (pointing at canvas)
U_CR = (-0.82, -0.57)


def paw_for_tip(tip, u, L):
    return tip[0] - L * u[0], tip[1] - L * u[1]


# ---------------------------------------------------------------- tool tracks
class Track:
    """Piecewise-linear point track: [(t, (x, y)), ...] spans; tells where a tool tip should point."""

    def __init__(self):
        self.spans = []

    def add(self, keys):
        keys = sorted(keys)
        for span in self.spans:                    # a stroke that starts where another ends continues it
            if abs(span[-1][0] - keys[0][0]) < 1e-6:
                span.extend(keys[1:])
                return
        self.spans.append(keys)

    def at(self, t):
        info = self.info(t)
        return info[0] if info else None

    def info(self, t):
        """(tip, span_start, span_end) while inside a span, else None."""
        for keys in self.spans:
            if keys[0][0] <= t <= keys[-1][0]:
                for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
                    if t0 <= t <= t1:
                        k = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                        return (lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k)), keys[0][0], keys[-1][0]
                return keys[-1][1], keys[0][0], keys[-1][0]
        return None

    def last_end(self, t):
        """(end time, end tip) of the latest span that ended before t."""
        ends = [(keys[-1][0], keys[-1][1]) for keys in self.spans if keys[-1][0] < t]
        return max(ends) if ends else None


SN_TIP, CR_TIP = Track(), Track()


def stroke(perf, side, tips, track, u, L, t0, t1, ease_in=0.35):
    """Paint along canvas-local points `tips` from t0 to t1: the paw follows, the brush tip stays on them."""
    pts = [cv(*p) for p in tips]
    perf.reach(t0 - ease_in, t0, side, paw_for_tip(pts[0], u, L), "io")
    keys = [(t0 - ease_in, pts[0]), (t0, pts[0])]
    n = len(pts)
    for i in range(1, n):
        ti = t0 + (t1 - t0) * i / (n - 1)
        perf.reach(t0 + (t1 - t0) * (i - 1) / (n - 1), ti, side, paw_for_tip(pts[i], u, L), "lin")
        keys.append((ti, pts[i]))
    track.add(keys)


def scrub(perf, side, tip, track, u, L, t0, t1, r=8):
    """Small painting strokes around one canvas-local point."""
    pts = [(tip[0] + r * math.cos(a), tip[1] + r * 0.6 * math.sin(2 * a)) for a in np.linspace(0, 4 * math.pi, 9)]
    stroke(perf, side, pts, track, u, L, t0, t1)


# ---------------------------------------------------------------- ACT 1: Snip paints; Crinkle fetches the blue
# shot 1-2: painting (Snip's brush in the right paw, the far arm on the canvas side)
T_FLOWER = 5.0
scrub(SN, "r", (180, 140), SN_TIP, U_SN, L_SN, 0.6, 2.4, r=10)            # finishing touches on the friends
stroke(SN, "r", [(40, 236), (38, 220), (36, 204)], SN_TIP, U_SN, L_SN, 4.2, T_FLOWER)   # the flower
SN.to(5.3, 5.9, "io", arm_r=10, elb_r=-14)
SN.face(0.0, eyes="happy").face(2.6, eyes="normal").face(4.0, eyes="sparkle").face(5.2, eyes="happy")
# shot 3: steps back, proud... something missing
SN.walk(8.1, 8.6, SN_BACK, steps=1)
SN.to(8.6, 9.0, "io", turn=0.2).face(8.6, eyes="happy", brows="up", mouth="smile_open").ears(8.6, 8.9, "perk")
SN.to(9.6, 10.0, "io", tilt=8, look_x=8, look_y=-8).face(9.6, eyes="normal", brows="think", mouth="hum")
SN.ears(9.6, 10.0, "curious")
SN.to(10.8, 11.2, "io", tilt=0, hturn=0.5, look_x=12, look_y=0).face(10.8, brows="up", mouth="o")
SN.ears(10.8, 11.1, "perk")
# shot 5: Crinkle walks in; waves; Snip points at the blue jar; Crinkle picks it up
CR.walk(13.8, 16.0, CR_TABLE)
SN.to(13.8, 14.2, "io", turn=0.6, hturn=0.0).face(14.6, eyes="sparkle", mouth="smile_open")
SN.arms_front.append((16.0, 17.0))
SN.reach(16.0, 16.3, "l", (SN_BACK - 50, 1150), "back")
for i in range(3):
    SN.to(16.3 + i * 0.2, 16.5 + i * 0.2, "io", elb_l=70 if i % 2 == 0 else 20)
SN.to(16.9, 17.1, "io", arm_l=-10, elb_l=14)
CR.face(16.0, eyes="happy", brows="up", mouth="smile_open")
CR.arms_front.append((16.2, 17.3))
CR.reach(16.2, 16.5, "r", (CR_TABLE + 60, 1110), "back")
for i in range(3):
    CR.to(16.5 + i * 0.2, 16.7 + i * 0.2, "io", elb_r=-70 if i % 2 == 0 else -20)
CR.to(17.1, 17.3, "io", arm_r=10, elb_r=-14)
T_POINT = 17.4
SN.reach(T_POINT, T_POINT + 0.35, "r", (SN_BACK + 400, 1230), "back")     # points (brush and all)
SN.face(T_POINT, eyes="normal", brows="up", mouth="smile_open")
SN.wiggle(T_POINT + 0.4, "arm_r", 4, 3.0, 2.0)
SN.to(18.9, 19.3, "io", arm_r=10, elb_r=-14)
CR.to(17.8, 18.2, "io", turn=0.6, look_x=6, look_y=6).face(17.8, eyes="normal", brows="up", mouth="o")
CR.to(18.5, 18.8, "io", hturn=-1.0, look_x=-8, look_y=0).face(18.5, eyes="happy", mouth="smile_open")
CR.wiggle(18.8, "head_dy", 8, 2.5, 3.0)                                 # nod: sure!
CR.to(19.1, 19.3, "io", hturn=0.0, look_x=8, look_y=8)
JAR_GRAB = (JAR_BLUE[0], JAR_BLUE[1] - 44)
CR.reach(19.3, 19.8, "r", JAR_GRAB, "io")
T_GRAB = 19.8
CR.reach(19.9, 20.3, "r", (JAR_GRAB[0] - 20, JAR_GRAB[1] - 40), "io")
CR.to(20.4, 20.8, "io", turn=-0.6, look_x=-10, look_y=0).face(20.4, eyes="happy", brows="up", mouth="smile")
CR.reach(20.4, 20.8, "r", (CR_TABLE - 40, 1300), "io")                  # carries it in front
# shots 6-7: bouncy walk toward Snip (looking at Snip, not at the floor)... the block
CR.walk(20.9, 22.7, 1360, steps=2)
CR.hop(20.9, 22.7, 2, 14)
CR.walk(22.7, 24.25, 1280, steps=1)
SN.face(21.0, eyes="sparkle", brows="up", mouth="smile_open")
# shot 8: the trip
T_TRIP, T_SLOSH, T_SPLAT = 24.25, 24.6, 24.95
CR.walk(T_TRIP, 25.1, CR_P, steps=3)
CR.to(T_TRIP, T_TRIP + 0.2, "out", lean=8).face(T_TRIP, eyes="wide", brows="up", mouth="O")
CR.reach(T_TRIP, T_SLOSH, "r", (1150, 1350), "out")                      # the arm swings down and forward
CR.to(T_TRIP, T_TRIP + 0.25, "out", arm_l=-150, elb_l=-30)
CR.to(T_TRIP + 0.25, T_TRIP + 0.5, "io", arm_l=-60, elb_l=40)
CR.to(T_TRIP + 0.5, T_TRIP + 0.75, "io", arm_l=-160, elb_l=-20)
CR.to(25.1, 25.5, "back", lean=-4).to(25.5, 25.8, "io", lean=0)
CR.to(25.3, 25.7, "io", arm_l=-10, elb_l=14)
CR.reach(25.3, 25.7, "r", (CR_P - 30, 1300), "io")
CR.face(25.7, eyes="closed", brows="calm", mouth="smile")               # phew
CR.arms_front.append((25.8, 26.5))
CR.reach(25.8, 26.1, "l", (CR_P - 60, 1000), "io")                       # wipes his brow
CR.to(26.1, 26.4, "io", arm_l=-10, elb_l=14)
CR.to(26.6, 26.9, "io", look_x=-4, look_y=10, head_dy=4).face(26.6, eyes="normal", brows="calm", mouth="flat")
CR.face(27.0, eyes="wide", brows="up", mouth="o")                       # the jar is empty...
CR.to(27.3, 27.6, "io", look_x=-12, look_y=-2, head_dy=0, turn=-0.7).face(27.3, brows="worry", mouth="O")
CR.no_blink.append((T_TRIP, 28.6))
SN.face(T_TRIP + 0.1, eyes="wide", brows="up", mouth="o")
SN.to(T_TRIP, T_TRIP + 0.3, "io", look_x=10)
SN.no_blink.append((T_TRIP, 35.0))

# ---------------------------------------------------------------- ACT 2: oh no
T_TAKE = 31.3
SN.to(29.0, 29.2, "io", look_x=-2, look_y=-4, turn=0.3)
SN.face(T_TAKE, eyes="wide", brows="up", mouth="O")
SN.ears(T_TAKE, T_TAKE + 0.2, "alarm", "snap").hop(T_TAKE, T_TAKE + 0.4, 1, 34)
SN.to(T_TAKE, T_TAKE + 0.16, "out", frizz=1.0).to(T_TAKE + 0.5, T_TAKE + 0.9, "io", frizz=0.0)
SN.to(32.2, 32.8, "io", head_dy=14, look_x=6, look_y=6, turn=0.4)
SN.ears(32.2, 33.8, "droop", "io")
SN.face(32.3, eyes="glassy", brows="sad", mouth="frown")
T_SNIFFS = (34.2, 34.45, 42.6, 42.85)
for ts in T_SNIFFS:
    SN.wiggle(ts, "head_dy", -5, 6.0, 6.0)
CR.set(35.4, turn=-0.35, look_x=-10, look_y=2)
CR.face(35.4, eyes="wide", brows="worry", mouth="wobble")
CR.to(35.9, 36.1, "io", look_x=-12, look_y=8)
CR.arms_front.append((36.0, 37.9))
CR.reach(36.0, 36.35, "l", (CR_P - 100, 1170), "back")                   # paw on cheek: uh-oh
CR.face(36.1, mouth="O")
CR.to(37.6, 37.9, "io", arm_l=-10, elb_l=14)
# puts the jar down, tiptoes away looking back... a sniff... stops
CR.to(38.8, 39.2, "io", sq=0.8, turn=-0.4).face(38.8, eyes="normal", brows="worry", mouth="flat")
CR.reach(38.8, 39.3, "r", (CR_P - 70, FLOOR - 46), "io")
T_PUTDOWN = 39.3
CR.to(39.4, 39.8, "io", sq=1.0)
CR.reach(39.4, 39.8, "r", (CR_P + 40, 1360), "io")
CR.to(39.9, 40.3, "io", look_x=-12, look_y=4)
CR.to(40.3, 40.6, "io", turn=0.6, hturn=-1.1, look_x=-12, look_y=0)
CR.reach(40.3, 40.6, "l", (CR_P - 40, 1210), "io")
CR.reach(40.3, 40.6, "r", (CR_P + 110, 1210), "io")
CR.walk(40.6, 42.5, 1420, steps=4)
SN.to(40.0, 40.5, "io", turn=0.6, look_x=8, look_y=6)
CR.to(T_SNIFFS[2] + 0.1, T_SNIFFS[2] + 0.35, "back", hturn=-1.4, look_x=-14, look_y=2)
CR.face(T_SNIFFS[2] + 0.1, eyes="wide", brows="sad", mouth="o")
CR.to(43.2, 43.6, "io", arm_l=-10, elb_l=14, arm_r=10, elb_r=-14)
CR.face(43.4, eyes="glassy", brows="sad", mouth="frown")

# ---------------------------------------------------------------- the choice (a thought)
T_DIM0, T_DIM1 = 44.1, 44.5
T_CLOUD, T_RED, T_GREEN, T_Q, T_PICK = 44.5, 44.8, 45.1, 45.3, 49.4
T_UNDIM0, T_UNDIM1 = 49.9, 50.5
CR.to(45.6, 46.0, "io", turn=0.0, hturn=0.0, look_x=0, look_y=0).face(45.6, eyes="normal", brows="worry", mouth="flat")
CR.to(46.2, 46.5, "io", look_x=-12, look_y=-12, tilt=8)
CR.to(46.9, 47.2, "io", look_x=6, look_y=-14, tilt=-6)
CR.to(47.6, 47.9, "io", look_x=0, look_y=0, tilt=3).face(47.6, brows="up", mouth="smile")
CR.no_blink.append((47.6, 49.4))
CR.wiggle(T_PICK, "head_dy", 9, 2.5, 3.0)
CR.face(50.0, brows="sorry", mouth="flat")

# ---------------------------------------------------------------- ACT 3: sorry, hug
CR.to(50.6, 50.9, "io", turn=-0.6, tilt=0, look_x=-10, look_y=4)
CR.walk(50.8, 52.6, 860, steps=5)
CR.to(50.8, 51.2, "io", head_dy=10)
PAWS = (860 - 4, 1385)
CR.reach(52.8, 53.2, "l", (PAWS[0] - 8, PAWS[1]), "io")
CR.reach(52.8, 53.2, "r", (PAWS[0] + 8, PAWS[1]), "io")
CR.to(52.8, 53.2, "io", head_dy=16, tilt=5, look_y=8).face(52.9, eyes="closed", brows="sorry", mouth="frown")
CR.wiggle(53.4, "lean", 2.5, 1.2, 0.8)
CR.face(54.2, eyes="glassy", brows="worry", mouth="smile")
CR.to(54.2, 54.6, "back", arm_l=-62, elb_l=30, arm_r=62, elb_r=-30, head_dy=0, tilt=0, look_y=0)
SN.to(51.0, 51.4, "io", look_x=10, look_y=4)
SN.to(54.6, 55.0, "io", look_x=10, look_y=0, head_dy=4)
SN.ears(54.8, 55.6, "sad", "io")
SN.face(55.0, eyes="normal", brows="sad", mouth="frown").face(55.4, mouth="smile", brows="calm")
SN.to(55.4, 55.7, "out", head_dy=0)
SN.ears(55.6, 56.1, "up", "back")
T_HUG0, T_HUG1 = 56.2, 58.2
SN.walk(55.6, 56.2, 550, steps=1)
SN.to(T_HUG0, T_HUG0 + 0.4, "back", lean=-6, turn=0.25).face(T_HUG0, eyes="happy", brows="calm", mouth="smile")
SN.reach(T_HUG0, T_HUG0 + 0.4, "r", (760, 1300), "back")
CR.walk(T_HUG0 - 0.3, T_HUG0 + 0.2, 820, steps=1)
CR.to(T_HUG0, T_HUG0 + 0.4, "back", lean=6, turn=-0.25).face(T_HUG0, eyes="happy", brows="calm", mouth="smile")
CR.reach(T_HUG0, T_HUG0 + 0.4, "l", (620, 1330), "back")
HEART_PLAN = ((56.5, 680, 860), (56.8, 760, 810), (57.1, 600, 830))
SN.to(T_HUG1, T_HUG1 + 0.4, "io", lean=0, arm_r=10, elb_r=-14, turn=0.6)
CR.to(T_HUG1, T_HUG1 + 0.4, "io", lean=0, arm_l=-10, elb_l=14, arm_r=10, elb_r=-14, turn=-0.6)
CR.face(T_HUG1 + 0.2, eyes="normal", brows="up", mouth="smile")
SN.face(T_HUG1 + 0.2, eyes="normal", brows="calm", mouth="smile")

# ---------------------------------------------------------------- ACT 4: the fix
# Crinkle: "I'll fix it!" -- points at the painting, paw on chest, hurries for a brush
CR.to(58.8, 59.1, "io", turn=-0.6, look_x=-10, look_y=-6)
CR.reach(58.9, 59.3, "l", (660, 1010), "back")                            # points at the painting
CR.face(59.0, brows="think", mouth="smile_open")
CR.reach(59.6, 59.9, "r", (790, 1330), "back")                             # paw on chest: me!
CR.to(59.6, 59.9, "io", arm_l=-10, elb_l=14)
CR.wiggle(59.9, "head_dy", 6, 2.5, 3.0)
CR.to(60.4, 60.7, "io", turn=0.6, arm_r=10, elb_r=-14, look_x=8, look_y=0)
CR.walk(60.8, 62.6, CR_TABLE, steps=5)
SN.walk(60.4, 61.2, SN_P, steps=1)
SN.to(61.2, 61.6, "io", turn=0.6, look_x=10, look_y=0)
CUP_GRAB = (CUP[0], CUP[1] - 110)
CR.reach(62.7, 63.1, "r", CUP_GRAB, "io")
T_GETBRUSH = 63.1
CR.reach(63.2, 63.4, "r", (CUP_GRAB[0] - 30, CUP_GRAB[1] - 30), "io")
CR.to(63.4, 63.7, "io", turn=-0.6, look_x=-10)
CR.walk(63.6, 64.7, CR_P, steps=3)
CR.reach(63.6, 64.0, "r", (CR_TABLE - 40, 1300), "io")
SWAP = (CR_P - 40, 1300)
CR.reach(64.8, 65.1, "r", (SWAP[0] + 10, SWAP[1]), "io")
CR.reach(64.8, 65.1, "l", (SWAP[0] - 10, SWAP[1]), "io")
T_SWAP = 65.15                                                             # brush changes to the left paw
CR.to(65.3, 65.6, "io", arm_r=10, elb_r=-14)
CR.reach(65.3, 65.6, "l", (CR_P - 150, 1250), "io")
# ---- the blue-nose gag: its own little sequence of close-ups (Crinkle / Snip / Crinkle / both)
# Crinkle thinks, tapping his chin with the brush; the third tap boops his nose: it turns blue. He doesn't notice.
CR.to(65.8, 66.1, "io", turn=-0.3, look_x=-10, look_y=-4)               # turned enough that the brush is in front
CR.face(66.0, eyes="normal", brows="think", mouth="hum")
CR.to(66.1, 66.4, "io", tilt=6)
CR.arms_front.append((66.1, 68.0))
NOSE_LOCAL = (0, -96)
_st = CR.state(66.6)
NOSE_W = CR.a.face_point(_st, NOSE_LOCAL)
CHIN_W = CR.a.face_point(_st, (-4, -12))
U_GAG = (0.42, -0.91)                                                     # brush held upright, bristles to the face


def _cl(p):
    return p[0] - CANVAS_XY[0], p[1] - CANVAS_XY[1]                       # stroke() takes canvas-local points


T_DOT = 67.25
stroke(CR, "l", [_cl(CHIN_W), _cl((CHIN_W[0] - 4, CHIN_W[1] + 26)), _cl(CHIN_W), _cl((CHIN_W[0] - 4, CHIN_W[1] + 26)),
                 _cl(NOSE_W)], CR_TIP, U_GAG, L_CR, 66.4, T_DOT, ease_in=0.3)
stroke(CR, "l", [_cl(NOSE_W), _cl((CHIN_W[0] - 30, CHIN_W[1] + 90))], CR_TIP, U_GAG, L_CR, 67.4, 67.8, ease_in=0.15)
CR.to(67.4, 67.7, "io", tilt=-5)                                          # still thinking: hmm...
CR.to(68.0, 68.4, "io", arm_l=-60, elb_l=40)
# Snip glances over, notices, tries not to laugh (cheeks puffed, paw over mouth)... then giggles
SN.to(67.55, 67.8, "io", look_x=12, look_y=0, turn=0.5).face(67.55, eyes="normal", brows="calm", mouth="smile")
SN.face(67.95, eyes="wide", brows="up", mouth="o")
SN.no_blink.append((67.9, 68.6))
SN.arms_front.append((68.15, 69.3))
_sn = SN.state(68.3)
SN.reach(68.15, 68.4, "l", SN.a.face_point(_sn, (4, -80)), "io")
SN.face(68.38, eyes="closed", brows="up", mouth="blow")
SN.wiggle(68.38, "sq", 0.03, 8.0, 6.0)
T_GIGGLE = 68.5
SN.face(T_GIGGLE, eyes="happy", brows="up", mouth="smile_open")
SN.hop(T_GIGGLE, T_GIGGLE + 0.25, 1, 10).hop(T_GIGGLE + 0.25, T_GIGGLE + 0.5, 1, 10).hop(T_GIGGLE + 0.5, T_GIGGLE + 0.75, 1, 10)
SN.to(69.3, 69.6, "io", arm_l=-10, elb_l=14)
SN.hop(70.0, 70.25, 1, 8).hop(70.25, 70.5, 1, 8).hop(70.85, 71.1, 1, 8)
# Crinkle: puzzled... looks down at his own nose... it's blue! ...and laughs too
CR.to(69.0, 69.25, "io", look_x=-12, look_y=0, tilt=0).face(69.0, eyes="normal", brows="up", mouth="o")
CR.to(69.4, 69.65, "io", look_x=-2, look_y=12).face(69.4, eyes="normal", brows="think", mouth="hum")
T_SEES = 69.75
CR.face(T_SEES, eyes="wide", brows="up", mouth="O").hop(T_SEES, T_SEES + 0.25, 1, 14)
CR.no_blink.append((69.3, 70.1))
T_LAUGH = 70.1
CR.face(T_LAUGH, eyes="happy", brows="up", mouth="smile_open")
CR.to(T_LAUGH, T_LAUGH + 0.3, "io", look_y=0)
CR.hop(T_LAUGH, T_LAUGH + 0.25, 1, 10).hop(T_LAUGH + 0.25, T_LAUGH + 0.5, 1, 10).hop(T_LAUGH + 0.5, T_LAUGH + 0.75, 1, 10)
CR.reach(T_LAUGH, T_LAUGH + 0.3, "r", (CR_P + 20, 1390), "io")           # paw on his tummy, laughing
CR.to(70.9, 71.2, "io", arm_r=10, elb_r=-14)
# both look back at the painting: tilt... tilt... idea!
SN.to(71.2, 71.5, "io", look_x=-2, look_y=-4, turn=0.4).face(71.2, eyes="normal", brows="calm", mouth="smile")
CR.to(71.2, 71.4, "io", look_x=-12, look_y=-4, turn=-0.6).face(71.2, eyes="normal", brows="think", mouth="hum")
CR.to(71.25, 71.55, "io", tilt=12).to(71.6, 71.9, "io", tilt=-10)
T_IDEA = 72.0
CR.to(T_IDEA, T_IDEA + 0.3, "back", tilt=0).face(T_IDEA, eyes="sparkle", brows="up", mouth="smile_open")
CR.hop(T_IDEA, T_IDEA + 0.35, 1, 22)
CR.to(T_IDEA, T_IDEA + 0.35, "snap", arm_r=150, elb_r=-20)
CR.to(72.5, 72.8, "io", arm_r=10, elb_r=-14)
# shot 16: the trace (Crinkle: tail and back; Snip joins: nose and belly)
n_belly, n_tail = 29, len(S.TAIL_EDGE)
CR_PATH = OUTLINE[n_belly - 6:n_belly + n_tail + 12]
SN_PATH = OUTLINE[n_belly + n_tail + 12:] + OUTLINE[:n_belly - 6]
T_TR0, T_TR1, T_TR2, T_TR3 = 73.4, 76.2, 76.6, 79.0
stroke(CR, "l", CR_PATH, CR_TIP, U_CR, L_CR, T_TR0, T_TR1, ease_in=0.5)
stroke(SN, "r", SN_PATH, SN_TIP, U_SN, L_SN, T_TR2, T_TR3, ease_in=0.5)
CR.to(76.4, 76.8, "io", arm_l=-60, elb_l=40)
SN.to(79.2, 79.6, "io", arm_r=10, elb_r=-14)
TRACE_T = {}
for i, p in enumerate(CR_PATH):
    TRACE_T[OUTLINE.index(p)] = T_TR0 + (T_TR1 - T_TR0) * i / (len(CR_PATH) - 1)
for i, p in enumerate(SN_PATH):
    TRACE_T[OUTLINE.index(p)] = T_TR2 + (T_TR3 - T_TR2) * i / (len(SN_PATH) - 1)
T_WHALE = 79.1                                                             # the outline is complete: a whale!
# shot 17: Snip gets it
SN.to(80.0, 80.3, "io", look_x=10, turn=0.6).face(80.0, eyes="sparkle", brows="up", mouth="smile_open")
SN.ears(80.0, 80.3, "perk").hop(80.3, 80.65, 1, 26)
CR.to(80.2, 80.5, "io", look_x=-12, hturn=0.0).face(80.2, eyes="happy", brows="up", mouth="smile_open")
CR.wiggle(80.8, "head_dy", 8, 2.5, 3.0)
SN.wiggle(80.9, "head_dy", 8, 2.5, 3.0)
# shot 18: painting together
LAYER_T = {}
SN.face(83.0, eyes="normal", brows="think", mouth="smile")
scrub(SN, "r", (114, 170), SN_TIP, U_SN, L_SN, 83.4, 84.6, r=10)
LAYER_T["face"] = 84.6
CR.face(86.0, eyes="normal", brows="think", mouth="smile")
stroke(CR, "l", S.TAIL_EDGE, CR_TIP, U_CR, L_CR, 86.6, 88.4)
LAYER_T["tail"] = 88.4
SN.to(89.0, 89.4, "io", arm_r=10, elb_r=-14, look_x=12).face(89.0, eyes="happy", mouth="smile_open")
CR.to(89.0, 89.4, "io", arm_l=-60, elb_l=40, look_x=-12).face(89.2, eyes="happy", mouth="smile_open")
stroke(SN, "r", [(128, 128), (128, 100), (128, 76), (110, 84), (146, 84)], SN_TIP, U_SN, L_SN, 92.0, 93.6)
LAYER_T["spout"] = 93.6
stroke(CR, "l", [(330, 284), (280, 278), (230, 286), (180, 280), (130, 286), (80, 280)], CR_TIP, U_CR, L_CR,
       95.0, 96.8)
LAYER_T["waves"] = 96.8
scrub(SN, "r", (66, 264), SN_TIP, U_SN, L_SN, 98.0, 99.2, r=12)
LAYER_T["boat"] = 99.2
scrub(CR, "l", (246, 238), CR_TIP, U_CR, L_CR, 100.1, 100.9, r=8)
LAYER_T["bubbles"] = 100.9
stroke(CR, "l", [(132, 112), (160, 72), (196, 58), (232, 72), (258, 112)], CR_TIP, U_CR, L_CR, 101.4, 102.8)
LAYER_T["rainbow"] = 102.8
SN.to(93.8, 94.2, "io", arm_r=10, elb_r=-14)
SN.to(99.4, 99.8, "io", arm_r=10, elb_r=-14)
for t0, t1 in ((88.6, 89.0), (97.0, 97.4)):
    CR.to(t0, t1, "io", arm_l=-60, elb_l=40)

# ---------------------------------------------------------------- ACT 5: the reveal (wow) and the paw-bump
CR.to(103.0, 103.4, "io", arm_l=-10, elb_l=14)
SN.walk(103.2, 104.2, 380, steps=1)
CR.walk(103.2, 104.2, 1260, steps=1)
SN.face(103.4, eyes="normal", brows="up", mouth="o")
CR.face(103.4, eyes="normal", brows="up", mouth="o")
SN.to(104.2, 104.6, "io", look_x=6, look_y=-4, turn=0.5)
CR.to(104.2, 104.6, "io", look_x=-8, look_y=-4, turn=-0.5)
SN.face(106.0, eyes="sparkle", brows="up", mouth="O")
CR.face(106.4, eyes="sparkle", brows="up", mouth="O")
SN.no_blink.append((109.8, 111.0))
CR.no_blink.append((110.9, 112.0))
SN.face(110.4, eyes="sparkle", mouth="smile_open")
CR.face(111.4, eyes="sparkle", mouth="smile_open")
# laugh, walk together, paw-bump
SN.face(112.0, eyes="happy", brows="up", mouth="smile_open")
CR.face(112.0, eyes="happy", brows="up", mouth="smile_open")
SN.walk(112.3, 113.8, 610, steps=3)
CR.walk(112.3, 113.8, 990, steps=3)
SN.to(112.3, 112.6, "io", look_x=10, turn=0.5)
CR.to(112.3, 112.6, "io", look_x=-10, turn=-0.5)
T_PAWS = 114.4
PAW_MEET = (800, 1240)
SN.reach(113.9, T_PAWS, "r", (PAW_MEET[0] - 16, PAW_MEET[1]), "snap")
CR.reach(113.9, T_PAWS, "l", (PAW_MEET[0] + 16, PAW_MEET[1]), "snap")
SN.to(115.0, 115.4, "io", arm_r=10, elb_r=-14, turn=0.0, look_x=0)
CR.to(115.0, 115.4, "io", arm_l=-10, elb_l=14, turn=0.0, look_x=0)
SN.walk(115.6, 116.8, SN_P, steps=2)
CR.walk(115.6, 116.8, CR_P, steps=2)
SN.to(115.6, 115.9, "io", turn=-0.4).to(116.8, 117.1, "io", turn=0.1)
CR.to(115.6, 115.9, "io", turn=0.4).to(116.8, 117.1, "io", turn=-0.1)
SN.arms_front.append((117.0, DUR))
SN.reach(117.0, 117.4, "l", (SN_P - 140, 1180), "back")                    # ta-da!
CR.reach(117.0, 117.4, "r", (CR_P + 150, 1170), "back")
SN.ears(117.0, 117.3, "perk").hop(117.0, 117.35, 1, 20)
CR.hop(117.05, 117.4, 1, 18)
SN.face(117.0, eyes="happy", brows="up", mouth="smile_open")
CR.face(117.0, eyes="happy", brows="up", mouth="smile_open")

# ---------------------------------------------------------------- shots: (start, centre, zoom[, end zoom])
SHOTS = [
    (0.0, (960, 1100), 1.0),                    # 1 wide
    (4.0, CANVAS_MID, 1.8),                     # 2 the painting
    (8.0, (SN_BACK + 60, 1110), 1.4),           # 3 Snip: proud... something missing
    (12.0, (1590, 1290), 1.8),                  # 4 the blue jar
    (13.6, (960, 1100), 1.0),                   # 5 Crinkle arrives, picks it up
    (22.7, (1250, 1420), 2.0),                  # 6-7 his feet... the block
    (24.2, (960, 1100), 1.0),                   # 8 the trip, the splash
    (28.6, CANVAS_MID, 1.8),                    # 9 the painting
    (31.2, (SN_BACK, 1030), 1.9),               # 10 Snip
    (35.4, (CR_P, 1060), 1.8),                  # 11 Crinkle: uh-oh
    (38.6, (1240, 1140), 1.25),                 # 12 puts it down, tiptoes away
    (44.0, (1190, 1080), 1.1),                  # 13 the thought
    (50.6, (690, 1130), 1.3),                   # 14 sorry, hug
    (58.6, (960, 1100), 1.0),                   # 15 "I'll fix it", the brush
    (65.8, (1140, 1110), 1.9),                  # 16a Crinkle thinks... boop: a blue nose
    (67.6, (480, 1075), 1.9),                   # 16b Snip notices, tries not to laugh, giggles
    (69.0, (1140, 1100), 1.9),                  # 16c Crinkle: puzzled, looks at his nose, laughs
    (70.8, (820, 1110), 1.2),                   # 16d both laugh; back to the painting; idea!
    (73.0, CANVAS_MID, 1.75),                   # 17 the trace
    (79.8, (820, 1110), 1.2),                   # 18 Snip gets it
    (83.0, cv(112, 168), 1.9),                  # 19 eye
    (86.0, cv(270, 130), 1.9),                  # 20 tail
    (89.0, (820, 1110), 1.2),                   # 21 together
    (91.5, cv(130, 110), 1.9),                  # 22 spout
    (94.5, cv(200, 270), 1.8),                  # 23 waves
    (97.5, cv(80, 250), 1.9),                   # 24 boat
    (100.0, cv(200, 150), 1.6),                 # 25 bubbles, rainbow
    (103.0, (960, 1100), 1.0),                  # 26 step back
    (104.6, CANVAS_MID, 1.0, 1.85, 109.6),      # 27 the reveal: slow push-in
    (109.8, (SN_BACK - 40, 1030), 1.9),         # 28 Snip, amazed
    (110.9, (1260, 1060), 1.9),                 # 29 Crinkle, amazed
    (112.0, (800, 1130), 1.3),                  # 30 paw-bump
    (116.6, (900, 1090), 1.05),                 # 31 final
]


def shot_at(t):
    cur = SHOTS[0]
    for s in SHOTS:
        if t >= s[0]:
            cur = s
    if len(cur) == 5:
        t0, c, z0, z1, te = cur
        return c, lerp(z0, z1, ease_in_out(seg(t, t0 + 0.4, te)))
    return cur[1], cur[2]


# ---------------------------------------------------------------- props over time
def pop(t, t0, d=0.28):
    return ease_out_back(seg(t, t0, t0 + d))


def jar_state(t):
    """(where, holder): 'table', ('held', perf, side), or 'floor'."""
    if t < T_GRAB:
        return "table"
    if t < T_PUTDOWN:
        return "held"
    return "floor"


def jar_angle(t):
    if T_SLOSH - 0.05 <= t < 25.4:
        return 95 * ease_out(seg(t, T_SLOSH - 0.05, T_SLOSH + 0.15)) * (1 - ease_in_out(seg(t, 25.1, 25.4)))
    return 0.0


def jar_sprite(t):
    return JARS["blue"] if t < T_SLOSH + 0.05 else JARS["blue_empty"]


SLOSH_HIT = (890, 1165)                         # where the paint lands on the picture


def slosh(t):
    """Blue paint flung from the jar's mouth (hip height) up onto the painting along a curve that stays
    under Crinkle's snout: it starts thin at the jar and lands on the lower right of the picture."""
    p = seg(t, T_SLOSH, T_SPLAT)
    if not 0 < p < 1:
        return []
    (jx, jy), _ = CR.paw(T_SLOSH, "r")
    p0 = (jx - 30, jy + 5)
    p1 = (p0[0] - 130, p0[1] - 10)
    p2 = SLOSH_HIT
    out = []
    for i, spr in enumerate(SLOSH):
        q = max(0.0, min(1.0, p - 0.08 * i))
        if q <= 0:
            continue
        x = (1 - q) ** 2 * p0[0] + 2 * (1 - q) * q * p1[0] + q * q * p2[0]
        y = (1 - q) ** 2 * p0[1] + 2 * (1 - q) * q * p1[1] + q * q * p2[1]
        out.append((spr, (x, y), 0.45 + 0.55 * min(1.0, q * 3)))
    return out


def brush_holder(name, t):
    if name == "sn":
        return SN, "r"
    if t < T_GETBRUSH:
        return None
    return (CR, "r") if t < T_SWAP else (CR, "l")


def _blend_angle(a, b, k):
    d = (b - a + 180) % 360 - 180
    return a + d * k


def tool_angle(perf, side, st, tip_track, t, ease=0.3):
    """The tool follows the forearm, except while painting (it aims at the tip track); it eases between the two."""
    W, fa = perf.paw(t, side, st)
    if tip_track is None:
        return W, fa
    info = tip_track.info(t)
    if info:
        tip, t0, _ = info
        aim = math.degrees(math.atan2(tip[0] - W[0], tip[1] - W[1]))
        return W, _blend_angle(fa, aim, ease_in_out(seg(t, t0, t0 + ease)))
    end = tip_track.last_end(t)
    if end and t - end[0] < ease:
        tip = end[1]
        aim = math.degrees(math.atan2(tip[0] - W[0], tip[1] - W[1]))
        return W, _blend_angle(aim, fa, ease_in_out(seg(t, end[0], end[0] + ease)))
    return W, fa


def is_far(st, side):
    return (side == "r" and st["turn"] > 0.35) or (side == "l" and st["turn"] < -0.35)


def draw_canvas(f, t):
    S_ = CAM.S
    place(f, EASEL, S_((EASEL_X, FLOOR)))
    place(f, BOARD, S_(CANVAS_XY))
    place(f, SUN, S_(cv(55, 55)))
    place(f, FRIENDS, S_(cv(168, 178)), scale=0.75)
    if t >= T_FLOWER:
        place(f, FLOWER, S_(cv(36, 214)), scale=pop(t, T_FLOWER))
    if t >= T_SPLAT:
        k = 0.4 + 0.6 * ease_out_back(seg(t, T_SPLAT, T_SPLAT + 0.12))
        hx, hy = SLOSH_HIT
        place(f, SPLASH, S_((hx + (CANVAS_XY[0] - hx) * k, hy + (CANVAS_XY[1] - hy) * k)), scale=k, shadow=False)
        for (x, y, L), spr in zip(S.DRIPS, DRIPS):
            k = ease_out(seg(t, 27.6, 30.6))
            if k > 0.02:
                place(f, spr, S_(cv(x, y)), sy=k, shadow=False)
    for i, p in enumerate(OUTLINE):
        tt = TRACE_T.get(i)
        if tt is not None and tt <= t < LAYER_T["tail"]:
            glow = 1 + 0.35 * math.sin(math.pi * seg(t, T_WHALE + 0.03 * (i % 20), T_WHALE + 0.6 + 0.03 * (i % 20)))
            place(f, TRACE, S_(cv(*p)), scale=glow * min(1, (t - tt) / 0.12 + 0.3))
    for name in ("tail", "waves", "face", "spout", "boat", "bubbles", "rainbow"):
        t0 = LAYER_T[name]
        if t >= t0:
            k = ease_out_back(seg(t, t0, t0 + 0.3))
            place(f, LAYERS[name], S_(CANVAS_XY), alpha=min(1.0, (t - t0) / 0.15), shadow=False,
                  scale=1.0 if name in ("waves", "tail") else 0.96 + 0.04 * k)


def draw_room_props(f, t):
    S_ = CAM.S
    place(f, TABLE, S_((TABLE_X, FLOOR)))
    place(f, JARS["red"], S_(JAR_RED))
    place(f, JARS["yellow"], S_(JAR_YEL))
    if jar_state(t) == "table":
        place(f, JARS["blue"], S_(JAR_BLUE))
    place(f, CUP_SPR, S_(CUP))
    if jar_state(t) == "floor":
        place(f, JARS["blue_empty"], S_((CR_P - 70, FLOOR + 2)))


def draw_brush(f, t, who, st_of):
    h = brush_holder(who, t)
    if h is None:
        return
    perf, side = h
    st = st_of[id(perf)]
    track = SN_TIP if who == "sn" else CR_TIP
    W, ang = tool_angle(perf, side, st, track, t)
    place(f, BRUSH_SN if who == "sn" else BRUSH_CR, CAM.S(W), angle=ang)


def draw_blue_nose(f, t, cr):
    nx, ny = CR.a.face_point(cr, NOSE_LOCAL)
    ht = max(-1.0, min(1.0, cr["turn"] + cr.get("hturn", 0.0)))
    w = 0.6 + 0.4 * math.cos(math.radians(R.THETA_HEAD * ht))
    k = ease_out_back(seg(t, T_DOT, T_DOT + 0.15))
    place(f, BLUE_NOSE, CAM.S((nx, ny)), angle=cr["lean"] + cr["tilt"], sx=w * k, sy=k, shadow=False)
    q = seg(t, T_DOT, T_DOT + 0.35)                            # tiny paint specks fly off the boop
    if 0 < q < 1:
        for i, spr in enumerate(SPECKS):
            a = math.radians(200 + i * 45)
            place(f, spr, CAM.S((nx + 70 * q * math.cos(a), ny + 70 * q * math.sin(a) + 40 * q * q)),
                  scale=1 - 0.5 * q, shadow=False)


def dim_k(t):
    return ease_in_out(seg(t, T_DIM0, T_DIM1)) * (1 - ease_in_out(seg(t, T_UNDIM0, T_UNDIM1)))


def draw_thought(f, t, cr):
    if not T_CLOUD <= t < T_UNDIM1 + 0.1:
        return
    out = ease_in_out(seg(t, T_UNDIM0 - 0.1, T_UNDIM1 - 0.2))
    hx, hy = CR.a.head_pivot(cr)
    anchor = (hx - 130, hy - 160)
    k = pop(t, T_CLOUD, 0.35)
    place(f, CLOUD, CAM.S(anchor), scale=k, alpha=1 - out)
    cx, cy = anchor[0] - 290 * k, anchor[1] - 225 * k
    red_out = ease_in_out(seg(t, T_PICK, T_PICK + 0.3))
    pulse = 1 + 0.2 * math.sin(math.pi * seg(t, T_PICK, T_PICK + 0.45))
    place(f, BUB_HIDE, CAM.S((cx - 150, cy + 10)), scale=pop(t, T_RED) * (1 - red_out), alpha=1 - out)
    place(f, BUB_SORRY, CAM.S((cx + 150, cy + 10)), scale=pop(t, T_GREEN) * pulse, alpha=1 - out)
    if t >= T_Q:
        place(f, QMARK, CAM.S((cx, cy - 140)), angle=6 * math.sin(2 * math.pi * t), scale=pop(t, T_Q) * (1 - red_out),
              alpha=1 - out)


def draw_fx(f, t, sn, cr):
    S_ = CAM.S
    for spr, p, sc in slosh(t):
        place(f, spr, S_(p), scale=sc)
    for i, (t0, x, y) in enumerate(HEART_PLAN):
        p = seg(t, t0, t0 + 1.4)
        if 0 < p < 1:
            place(f, HEARTS[i], S_((x + 14 * math.sin(6 * p + i), y - 150 * p)), scale=pop(t, t0, 0.3),
                  alpha=1 - ease_in_out(seg(p, 0.65, 1.0)))
    k = seg(t, T_IDEA, T_IDEA + 0.9)
    if 0 < k < 1:
        hx, hy = CR.a.head_pivot(cr)
        place(f, SPARK, S_((hx + 40, hy - 420)), scale=0.45 * math.sin(math.pi * k), angle=50 * k)
    kp = seg(t, T_PAWS, T_PAWS + 0.6)
    if 0 < kp < 1:
        place(f, SPARK, S_(PAW_MEET), scale=0.5 * math.sin(math.pi * kp), angle=40 * kp)
    if 3.4 <= t < 8.0 or 104.8 <= t < 112.0:                     # the painting twinkles
        spots = ((cv(60, 50), 3.6), (cv(250, 120), 4.3), (cv(36, 200), 5.4)) if t < 8 else \
                ((cv(128, 70), 105.4), (cv(196, 70), 106.2), (cv(66, 250), 107.0), (cv(300, 100), 107.8),
                 (cv(240, 280), 108.6), (cv(128, 60), 109.4))
        for p, t0 in spots:
            q = seg(t, t0, t0 + 0.9)
            if 0 < q < 1:
                place(f, SPARK_S, S_(p), scale=0.16 * math.sin(math.pi * q), angle=60 * q)
    if 12.3 <= t < 13.6:
        q = seg(t, 12.4, 13.3)
        place(f, SPARK_S, S_((JAR_BLUE[0] + 30, JAR_BLUE[1] - 90)), scale=0.2 * math.sin(math.pi * q), angle=50 * q)


def render_frame(t, view="land"):
    d = K.drawing_of(t)
    tq = d / K.DPS
    f = BG.copy()
    draw_room_props(f, tq)
    draw_canvas(f, tq)
    sn, cr = SN.state(tq, d), CR.state(tq, d)
    st_of = {id(SN): sn, id(CR): cr}
    hug = T_HUG0 <= tq < T_HUG1 + 0.3
    jar_held = jar_state(tq) == "held"
    cr_brush = brush_holder("cr", tq)
    order = [("cr", cr), ("sn", sn)] if hug else [("sn", sn), ("cr", cr)]
    for who, st in order:
        perf = SN if who == "sn" else CR
        tools_behind, tools_front = [], []
        if who == "sn":
            (tools_behind if is_far(st, "r") else tools_front).append("brush_sn")
        else:
            if jar_held:
                (tools_behind if is_far(st, "r") else tools_front).append("jar")
            if cr_brush:
                (tools_behind if is_far(st, cr_brush[1]) else tools_front).append("brush_cr")
        dimmed_out = who == "cr" and dim_k(tq) > 0.001
        if dimmed_out:
            continue
        for tool in tools_behind:
            _draw_tool(f, tq, tool, st_of)
        perf.draw(f, tq, CAM, st=st)
        if who == "cr" and tq >= T_DOT:
            draw_blue_nose(f, tq, cr)
        for tool in tools_front:
            _draw_tool(f, tq, tool, st_of)
    k = dim_k(tq)
    if k > 0.001:
        f.alpha_composite(Image.new("RGBA", f.size, (40, 30, 50, int(110 * k))))
        for tool in (["jar"] if jar_held else []):
            _draw_tool(f, tq, tool, st_of)
        CR.draw(f, tq, CAM, st=cr)
        draw_thought(f, tq, cr)
    kb = ease_out(seg(tq, T_TRIP, T_TRIP + 0.35))
    place(f, BLOCK_SPR, CAM.S((BLOCK[0] - 46 * kb, BLOCK[1] - 30 * math.sin(math.pi * kb))), angle=90 * kb)
    draw_fx(f, tq, sn, cr)
    centre, z = shot_at(tq)
    if z > 1.0001:
        f = K.zoom(f, z, CAM.S(centre))
    return f.resize((1920, 1080), Image.LANCZOS)


def _draw_tool(f, t, tool, st_of):
    if tool == "jar":
        st = st_of[id(CR)]
        W, _ = CR.paw(t, "r", st)
        ang = jar_angle(t)
        dx, dy = R.rot(0, 44, ang)
        place(f, jar_sprite(t), CAM.S((W[0] + dx, W[1] + dy)), angle=ang)
    elif tool == "brush_sn":
        draw_brush(f, t, "sn", st_of)
    elif tool == "brush_cr":
        draw_brush(f, t, "cr", st_of)


# ---------------------------------------------------------------- sound (no voices: effects and music only)
def splat_snd(vel=1.0):
    t = A._t(0.55)
    n = np.random.default_rng(5).normal(0, 1, len(t))
    wet = (A._lowpass(n, 6) - A._lowpass(n, 70)) * A._attack(t, 3000) * np.exp(-t * 12)
    thump = np.sin(2 * np.pi * np.cumsum(110 - 60 * t) / A.SR) * np.exp(-t * 18)
    return vel * (1.5 * wet + 0.9 * thump)


def sniff_snd(vel=1.0):
    t = A._t(0.12)
    n = np.random.default_rng(9).normal(0, 1, len(t))
    return vel * 0.9 * (A._lowpass(n, 4) - A._lowpass(n, 30)) * np.sin(np.pi * t / 0.12) ** 2


def clink(vel=1.0):
    a, b = A.glock(A.midi(98), 0.5, 0.5 * vel), A.glock(A.midi(103), 0.5, 0.3 * vel)
    return a + b


def giggle_snd(vel=1.0):
    out = np.zeros(int(0.9 * A.SR))
    for i, m in enumerate((84, 88, 86, 91, 88, 93)):
        g = MX.toy_piano(A.midi(m), 0.3, 0.6 * vel)
        s = int(i * 0.11 * A.SR)
        out[s:s + len(g)] += g[:len(out) - s]
    return out


def build_audio(path):
    M = A.midi
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    beat = 0.6

    def groove(t0, chords, vel=0.38, inst=A.marimba, bass=True, shaker=True):
        t = t0
        for ch, root in chords:
            notes = MX.CHORDS[ch]
            for b in range(4):
                music.add(t + b * beat / 2, inst(M(notes[b % 4]), 0.5, vel if b % 2 == 0 else vel * 0.7))
            if bass:
                music.add(t, A.bass(M(root), 0.5, 0.6))
            if shaker:
                for b in range(4):
                    music.add(t + b * beat / 2, A.shaker(0.3))
            t += 2 * beat
        return t

    I_IV_V = [("C", 48), ("F", 41), ("G", 43), ("C", 48)]
    A.jingle(music, 0.0, 0.9)
    groove(0.8, I_IV_V * 3)                                       # painting (0.8-15.2)
    groove(15.2, [("F", 41), ("C", 48), ("G", 43), ("C", 48)] * 2 + [("F", 41), ("G", 43)], vel=0.42)  # helper
    # suspense at the feet shot, then silence-ish for the trip
    music.add(22.7, A.pad([M(50), M(55), M(62)], 1.7, 0.35))
    for i in range(6):
        sfx.add(22.8 + i * 0.25, A.woodblock(i % 2 == 0, 0.35))
    # props and actions
    for tt in (T_FLOWER, 1.4, 2.0):
        sfx.add(tt, A.pop(0.5))
    sfx.add(T_FLOWER, A.glock(M(96), 0.8, 0.4))
    sfx.add(4.5, A.twinkle(0.5))
    sfx.add(12.4, A.twinkle(0.6))
    sfx.add(T_GRAB, clink(1.0))
    sfx.add(T_GETBRUSH, clink(0.7))
    sfx.add(T_SWAP, A.tap(0.4))
    sfx.add(T_TRIP, A.woodblock(False, 1.0))
    sfx.add(T_TRIP + 0.02, A.boing(0.5, 360))
    sfx.add(T_SLOSH, A.whoosh(0.4, 0.9))
    sfx.add(T_SPLAT, splat_snd(1.0))
    sfx.add(25.8, A.chime_up(0.4, (79, 84)))                    # phew
    sfx.add(27.0, A.boop(0.5))
    music.add(26.9, A.pad([M(50), M(53), M(57)], 2.3, 0.4))           # worried hush before the close-up
    sfx.add(28.9, A.wah_down(1.0))                              # sad trombone
    music.add(29.0, A.pad([M(57), M(60), M(64)], 2.2, 0.45))
    sfx.add(T_TAKE, A.boing(0.6, 520))
    sfx.add(T_TAKE, A.pop(0.6))
    music.add(31.3, A.pad([M(57), M(60), M(64)], 4.2, 0.5))
    for tt, m in ((32.4, 76), (33.0, 74), (33.6, 72), (34.2, 69)):
        music.add(tt, A.glock(M(m), 1.0, 0.22))
    for tt in T_SNIFFS:
        sfx.add(tt, sniff_snd(0.8))
    music.add(35.4, A.pad([M(53), M(57), M(60)], 3.3, 0.45))
    sfx.add(36.2, A.uh_oh(0.9))
    music.add(38.6, A.pad([M(50), M(57), M(62)], 3.0, 0.32))
    sfx.add(T_PUTDOWN, A.tap(0.5))
    music.add(41.5, A.pad([M(57), M(60), M(64)], 2.6, 0.38))
    # the thought
    sfx.add(T_CLOUD, A.boop(0.6))
    sfx.add(T_RED, A.pop(0.7))
    sfx.add(T_GREEN, A.pop(0.7))
    sfx.add(T_Q, A.boop(0.5))
    music.add(44.1, A.pad([M(50), M(57), M(62)], 2.8, 0.4))
    music.add(46.9, A.pad([M(55), M(59), M(62)], 2.7, 0.4))
    for i in range(7):
        sfx.add(46.0 + i * 0.5, A.woodblock(i % 2 == 0, 0.45))
    sfx.add(T_PICK, A.chime_up(0.8))
    # sorry, hug
    music.add(49.6, A.pad([M(48), M(55), M(64)], 3.0, 0.4))
    music.add(52.6, A.pad([M(53), M(57), M(65)], 2.4, 0.4))
    for tt, m, dd in ((53.0, 72, 0.45), (53.5, 71, 0.45), (54.0, 67, 0.8)):
        music.add(tt, MX.melodica(M(m), dd, 0.3))
    t = groove(55.0, [("F", 41), ("C", 48), ("G", 43)], vel=0.3, shaker=False)
    for tt, m, dd in ((56.2, 72, 0.5), (56.8, 76, 0.5), (57.4, 79, 0.9)):
        music.add(tt, MX.melodica(M(m), dd, 0.32))
    sfx.add(T_HUG0 + 0.1, A.twinkle(0.6))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.35))
    # the fix: bouncy determined music
    groove(58.6, [("C", 48), ("G", 43), ("F", 41), ("C", 48)] * 3, vel=0.34, inst=MX.toy_piano)
    for tt in (66.61, 67.04):
        sfx.add(tt, A.woodblock(True, 0.3))                       # tap, tap (on the chin)
    sfx.add(T_DOT, A.boop(0.9))
    sfx.add(T_DOT, A.pop(0.6))
    sfx.add(T_DOT + 0.02, splat_snd(0.18))
    sfx.add(67.95, A.glock(M(100), 0.5, 0.35))                   # Snip notices
    sfx.add(68.38, A.blow(0.3, 0.35))                            # pfff (holding it in)
    sfx.add(T_GIGGLE, giggle_snd(0.8))
    sfx.add(69.0, A.boop(0.35))
    sfx.add(T_SEES, A.boing(0.45, 500))
    sfx.add(T_LAUGH, giggle_snd(0.7))
    sfx.add(70.85, giggle_snd(0.45))
    sfx.add(T_IDEA, A.chime_up(0.9, (84, 88, 91, 96)))
    # the trace: a soft rising glide while the dots appear, then the whale twinkle
    music.add(73.0, A.pad([M(48), M(55), M(64)], 6.6, 0.3))
    for i in range(14):
        sfx.add(73.5 + i * 0.4, A.glock(M(72 + (i * 2) % 14), 0.3, 0.12))
    sfx.add(T_WHALE, A.chime_up(0.9))
    sfx.add(T_WHALE + 0.2, A.twinkle(0.8))
    sfx.add(80.3, A.boing(0.35, 420))
    # painting together: each part adds a note to a little tune
    groove(81.0, [("C", 48), ("F", 41), ("G", 43), ("C", 48), ("F", 41), ("C", 48), ("G", 43), ("C", 48)] * 2
           + [("F", 41), ("G", 43)], vel=0.3)
    for name, m in (("face", 72), ("tail", 76), ("spout", 79), ("waves", 81), ("boat", 84), ("bubbles", 86),
                    ("rainbow", 88)):
        sfx.add(LAYER_T[name], A.pop(0.6))
        sfx.add(LAYER_T[name], A.glock(M(m), 1.0, 0.5))
    sfx.add(LAYER_T["rainbow"] + 0.1, A.chime_up(0.8, (84, 88, 91, 96, 100)))
    # the reveal: full and warm
    music.add(104.6, A.pad([M(48), M(55), M(64), M(67)], 2.6, 0.5))
    music.add(107.2, A.pad([M(53), M(57), M(65), M(69)], 2.6, 0.5))
    for i, m in enumerate((72, 76, 79, 84, 79, 76, 77, 81, 84, 89)):
        music.add(104.8 + i * 0.5, MX.melodica(M(m), 0.45, 0.3))
    for i in range(6):
        sfx.add(105.4 + i * 0.8, A.twinkle(0.35))
    sfx.add(109.8, A.chime_up(0.6))
    music.add(109.6, A.pad([M(48), M(55), M(64), M(67)], 2.7, 0.45))  # holds through the amazed faces
    groove(112.0, [("C", 48), ("F", 41), ("G", 43)], vel=0.36)
    sfx.add(T_PAWS - 0.5, A.snare_roll(0.45, 0.6))
    sfx.add(T_PAWS, A.boop(0.9))
    A.jingle(music, T_PAWS + 0.02, 1.0, ending=True)
    sfx.add(T_PAWS + 0.05, A.twinkle(0.8))
    groove(115.6, [("F", 41), ("C", 48), ("G", 43), ("C", 48)], vel=0.32)
    sfx.add(117.0, A.chime_up(0.8))
    music.add(120.4, A.pad([M(48), M(55), M(64), M(72)], 4.0, 0.4))
    # footsteps (soft; tiptoes softer)
    for perf in (SN, CR):
        for tt in perf.footfalls():
            soft = 0.25 if 40.6 <= tt <= 42.6 else 0.5
            sfx.add(tt, A.tap(soft))
    m = A.reverb(music.normalized(), 0.22)
    s = A.reverb(sfx.normalized(), 0.08)
    nm = lambda x: x / max(1e-9, abs(x).max())  # noqa: E731
    y = 0.5 * nm(m) + 0.7 * nm(s)
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.25)


# ---------------------------------------------------------------- output
KEYS = [(2.0, "1 Snip paints"), (5.6, "2 the painting"), (10.0, "3 something missing"), (12.8, "4 the blue jar"),
        (16.6, "5 hello!"), (17.9, "5 Snip points"), (19.9, "5 picks it up"), (21.6, "6 carries it"),
        (23.6, "7 the block"), (24.5, "8 trip!"), (24.85, "8 slosh"), (26.0, "8 phew"), (29.8, "9 the painting"),
        (31.5, "10 Snip: shock"), (33.9, "10 sad"), (36.8, "11 uh-oh"), (39.1, "12 puts it down"),
        (41.4, "12 tiptoes away"), (43.0, "12 the sniff"), (46.4, "13 sneak or sorry?"), (53.5, "14 sorry"),
        (56.8, "14 hug"), (59.2, "15 I'll fix it"), (63.0, "15 a brush"), (66.8, "16a thinking (tap, tap)"),
        (67.3, "16a boop!"), (68.3, "16b Snip: pfff"), (68.7, "16b giggles"), (69.55, "16c looks at his nose"),
        (69.85, "16c it's blue!"), (70.4, "16c laughs"), (72.2, "16d idea!"), (75.0, "17 trace"), (79.4, "17 a whale!"),
        (84.4, "19 eye"), (88.2, "20 tail"), (90.0, "21 together"), (93.4, "22 spout"), (96.6, "23 waves"),
        (99.1, "24 boat"), (102.7, "25 rainbow"), (106.0, "27 reveal"), (109.0, "27 reveal (close)"),
        (110.5, "28 Snip amazed"), (111.5, "29 Crinkle amazed"), (114.5, "30 paw-bump"), (118.5, "31 ta-da")]


def key_sheet(path, keys=KEYS, w=400):
    import paperlib
    h = int(w * 1080 / 1920)
    cols = 6
    rows = math.ceil(len(keys) / cols)
    sheet = Image.new("RGB", (w * cols + 8 * (cols + 1), (h + 36) * rows + 8), (250, 248, 244))
    d = ImageDraw.Draw(sheet)
    font = paperlib.round_font(19)
    for i, (tt, label) in enumerate(keys):
        im = render_frame(tt).convert("RGB").resize((w, h), Image.LANCZOS)
        x = 8 + (i % cols) * (w + 8)
        y = 8 + (i // cols) * (h + 36)
        d.text((x + 3, y + 3), label, fill=(60, 50, 70), font=font)
        sheet.paste(im, (x, y + 28))
    sheet.save(path)
    print("wrote", path)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "output"), exist_ok=True)
    if "--keys" in sys.argv:
        key_sheet(os.path.join(ROOT, "reviews", "pilot02_keys.png"))
    elif "--cuts" in sys.argv:
        print(",".join(str(s[0]) for s in SHOTS[1:]))
    elif "--still" in sys.argv:
        tt = float(sys.argv[sys.argv.index("--still") + 1])
        out = os.path.join(ROOT, "build", f"pilot02_{tt:.2f}.png")
        render_frame(tt).convert("RGB").save(out)
        print("wrote", out)
    else:
        wav = os.path.join(ROOT, "build", "pilot02_audio.wav")
        build_audio(wav)
        K.render_video(os.path.abspath(__file__), os.path.join(ROOT, "output", "pilot02_splash_of_blue.mp4"),
                       wav, DUR, "land")
