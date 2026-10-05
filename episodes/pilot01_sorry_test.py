"""Pilot test scene v2: "Oops! Say Sorry" (first half of the pilot long-form episode).

v1 failed the owner's first viewing (2026-10-06): one far wide shot, a half-second accident, long still
stretches, tiny choice pictures, a too-subtle "sorry", and instrument "voices" that sounded like talking
nobody could follow. The owner found the old Shorts clear, so v2 tells the same story the way they do:
close-ups on what matters, the accident set up and slowed down, the choice acted out, "sorry" shown as
actions, and no voices at all (only sound effects and music). Kept from v1: eyebrows, ear feelings,
wind-up/overshoot acting, drawing on twos and the parallel renderer.

Shots: wide (Snip paints) -> close-up of the painting -> Snip proud -> wide (Crinkle dances in, swoosh,
bump) -> close-up: the pot wobbles 3 times and tips -> wide: the paint sails over Snip's head (slide
whistle), SPLAT -> close-up of the ruined painting (sad trombone) -> close-up of Snip: shock, then the
ears droop -> close-up of Crinkle: uh-oh -> Crinkle tiptoes away, hears a sniff, stops -> the choice
(sneak away or say sorry?) and a wait -> he walks back, head down, paws together, opens his arms -> hug,
hearts, paw-bump.

Run:  python3 episodes/pilot01_sorry_test.py              (landscape render -> output/)
      python3 episodes/pilot01_sorry_test.py --keys       (key frames -> reviews/pilot01_keys.png)
      python3 episodes/pilot01_sorry_test.py --still T    (one full-size frame -> build/)
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import acting as K  # noqa: E402
import audio as A  # noqa: E402
import icons  # noqa: E402
import music_extra as MX  # noqa: E402
import props_artcorner as P  # noqa: E402
import scene  # noqa: E402
import voices as V  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, seg, smooth_curve  # noqa: E402

DUR = 34.0
FLOOR = P.FLOOR_Y
SN_X, SN_BACK = 900, 960
CR_X, CR_START, CR_SNEAK, CR_NEAR = 1480, 2200, 1640, 1330
SN_HUG, CR_HUG = 1020, 1300

CAMS = {v: K.Cam(v, P.WORLD_W, P.WORLD_H, P.LAND_Y0, P.VERT_X0) for v in ("land", "vert")}
WORLD_BG = P.background()
BGS = {v: c.crop_bg(WORLD_BG) for v, c in CAMS.items()}

EASEL = P.easel()
BOARD = P.canvas_board()
STOOL = P.stool()
POTS = {k: P.pot(k / 4) for k in range(5)}
BRUSH = P.brush().scaled(1.15)
SUN = P.paint_sun()
FRIENDS = P.paint_friends()
FLOWER = P.paint_flower((240, 112, 140))
PHEART = P.paint_heart()
SPLAT = P.splat().scaled(0.8)
DRIPS = [P.drip(n) for n in (60, 90, 50)]
BLOB = P.blob().scaled(1.45)
DROPS = [P.droplet(r) for r in (13, 10, 7)]
BONK = scene.sparkle((255, 230, 120))
BUB_HIDE = P.bubble_hide()
BUB_SORRY = P.bubble_sorry()
QMARK = icons.question()
SPARKLE = scene.sparkle()
HEARTS = [scene.heart(c, 80) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120))]
TWINKLES = [scene.sparkle((255, 236, 140)) for _ in range(3)]

SN_ACT = K.Actor("snip", 1.15)
CR_ACT = K.Actor("crinkle", 1.2)
BRUSH_LEN = 166


def aim_from(actor, x, side, target, lean=0.0, y=FLOOR):
    sh = actor.shoulder_pt(x, y, side, 0.0, lean, 1.0)
    return math.degrees(math.atan2(target[0] - sh[0], target[1] - sh[1])) - lean


def brush_tip(x, arm, lean=0.0):
    px, py = SN_ACT.paw_tip(x, FLOOR, "l", arm, 0.0, lean, 1.0)
    a = math.radians(arm + lean)
    return px + BRUSH_LEN * math.sin(a), py + BRUSH_LEN * math.cos(a)


# ---------------------------------------------------------------- timing
T_DAB1, T_DAB2, T_DAB3 = 1.3, 2.2, 3.9
DAB1_A, DAB2_A = -148.0, -162.0
FLOWER_AT = brush_tip(SN_X, DAB1_A, 2.0)
FLOWER_AT = (FLOWER_AT[0], FLOWER_AT[1] + 20)
HEART_AT = brush_tip(SN_X, DAB2_A, 2.0)
SUN_AT, FRIENDS_AT = (528, 992), (598, 1148)
CANVAS_MID = ((P.CANVAS[0] + P.CANVAS[2]) / 2, (P.CANVAS[1] + P.CANVAS[3]) / 2)
SPLAT_AT = (648, 1116)
T_BUMP = 8.9
T_TIP, T_LAUNCH, T_SPLAT = 10.3, 10.45, 11.9
POT_MOUTH = (P.POT_AT[0] - 70, P.POT_AT[1] - 70)
T_TAKE = 14.0                                   # Snip's big reaction (on the cut to the close-up)
T_SNIFF = 21.5
T_DIM0, T_DIM1, T_UNDIM0, T_UNDIM1 = 23.1, 23.5, 26.3, 26.9
T_RED, T_GREEN, T_Q, T_PICK = 23.35, 23.65, 23.9, 26.0
T_HUG0, T_HUG1 = 30.1, 31.5
T_BUMP_PAWS = 32.1
HEART_PLAN = ((30.4, 1110, 830), (30.65, 1210, 780), (30.9, 1010, 800))
PAW_MEET = (1145, 1215)

# Shots: (start, centre in world, zoom). Cuts are instant; the last one runs to the end.
SNIP_HEAD = (SN_BACK, 1020)
CR_HEAD = (CR_X, 1060)
SHOTS = [
    (0.0, (960, 1100), 1.0),                   # wide: Snip paints
    (3.0, CANVAS_MID, 1.75),                   # close-up: the painting (and the last dab)
    (5.2, (SN_BACK, 1120), 1.35),              # Snip, proud
    (6.6, (960, 1100), 1.0),                   # wide: Crinkle dances in, swoosh, bump
    (8.95, (1300, 1200), 1.8),                 # close-up: the pot wobbles... and tips
    (11.0, (960, 1100), 1.0),                  # wide: the paint sails over Snip's head, SPLAT
    (12.1, CANVAS_MID, 1.75),                  # close-up: the ruined painting
    (13.95, SNIP_HEAD, 1.7),                   # close-up: Snip
    (17.4, CR_HEAD, 1.6),                      # close-up: Crinkle, uh-oh
    (19.6, (1460, 1110), 1.2),                 # Crinkle sneaks away... stops
    (22.9, (1300, 1100), 1.1),                 # the choice
    (27.0, (1150, 1120), 1.15),                # sorry, hug, paw-bump
]


def shot_at(t):
    cur = SHOTS[0]
    for s in SHOTS:
        if t >= s[0]:
            cur = s
    return cur


# ---------------------------------------------------------------- Snip's performance
SN = K.Perf(SN_ACT, seed=1, x=SN_X, y=FLOOR, lean=2.0, arm_l=-140.0, arm_r=14.0, eyes="happy", mouth="smile",
            brows="calm", look_x=-10.0, ear_l=-4.0, ear_r=4.0, ear_k=1.04)
(SN.to(0.25, 0.6, "io", arm_l=-152).to(0.6, 0.95, "io", arm_l=-138).to(0.95, T_DAB1, "antic", arm_l=DAB1_A)
   .to(T_DAB1, 1.6, "out", arm_l=-140).to(1.6, T_DAB2, "antic", arm_l=DAB2_A).to(T_DAB2, 2.55, "out", arm_l=-150))
SN.face(0.0, eyes="happy").face(1.2, eyes="normal").face(2.4, eyes="sparkle")
SN.wiggle(T_DAB1, "ear_r", 9).wiggle(T_DAB2, "ear_l", -9)
# close-up of the painting: a last little dab, then hold
SN.to(3.3, T_DAB3, "antic", arm_l=-150).to(T_DAB3, 4.3, "out", arm_l=-140)
# step back, proud
SN.to(5.2, 5.6, "io", x=SN_BACK, arm_l=-30, lean=0).hop(5.2, 5.6, 1, 22)
SN.to(5.6, 5.95, "snap", arm_r=140, arm_l=-100).ears(5.6, 5.9, "perk")
SN.face(5.6, eyes="happy", brows="up", mouth="smile_open")
SN.to(6.6, 7.0, "io", arm_r=14, arm_l=-20)
# Crinkle dances in: Snip looks over and waves
SN.to(7.0, 7.3, "out", look_x=10, lean=-3).face(7.0, eyes="normal", brows="up", mouth="smile")
SN.to(7.3, 7.55, "back", arm_r=150).to(7.55, 7.75, "io", arm_r=120).to(7.75, 7.95, "io", arm_r=150)
SN.to(7.95, 8.25, "io", arm_r=14)
# back to admiring the painting (so the bump and the flying paint happen behind Snip's back)
SN.to(8.2, 8.5, "io", look_x=-10, lean=2).face(8.2, eyes="happy", brows="calm", mouth="smile")
SN.ears(8.2, 8.6, "happy")
SN.wiggle(9.6, "lean", 2.0, 0.8, 0.4)                                  # contented sway
# SPLAT: a flinch in the wide shot...
SN.face(T_SPLAT + 0.03, eyes="wide", brows="up", mouth="o")
SN.ears(T_SPLAT + 0.03, T_SPLAT + 0.2, "alarm", "snap")
SN.no_blink.append((T_SPLAT, T_TAKE + 1.0))
# ...and the big take on the close-up: gasp, ears shoot up, fur frizz, a jump
SN.face(T_TAKE, eyes="wide", brows="up", mouth="O")
SN.hop(T_TAKE, T_TAKE + 0.4, 1, 34).wiggle(T_TAKE, "ear_k", 0.12, 4.0, 3.0)
SN.to(T_TAKE, T_TAKE + 0.16, "out", frizz=1.0).to(T_TAKE + 0.5, T_TAKE + 0.9, "io", frizz=0.0)
SN.to(T_TAKE, T_TAKE + 0.2, "back", arm_l=-70, arm_r=70)
# sadness: ears droop slowly, wet eyes, frown
SN.to(14.7, 15.3, "io", arm_l=-12, arm_r=12, head_dy=14, lean=3, look_x=-10, look_y=4)
SN.ears(14.6, 16.3, "droop", "io")
SN.face(14.8, eyes="glassy", brows="sad", mouth="frown")
SN.wiggle(16.7, "head_dy", -4, 6.0, 6.0).wiggle(16.95, "head_dy", -4, 6.0, 6.0)      # sniff sniff
SN.wiggle(T_SNIFF, "head_dy", -5, 6.0, 6.0).wiggle(T_SNIFF + 0.25, "head_dy", -5, 6.0, 6.0)
# Crinkle comes back: Snip looks up at him, ears lift, smile
SN.to(28.9, 29.3, "io", look_x=10, look_y=0, lean=-1, head_dy=6)
SN.ears(29.2, 29.8, "sad", "io")
SN.face(29.3, eyes="normal", brows="sad", mouth="frown")
SN.face(29.7, mouth="smile", brows="calm")
SN.to(29.7, 30.0, "out", head_dy=0)
SN.ears(29.8, 30.3, "up", "back")
# hug
SN.to(T_HUG0, T_HUG0 + 0.4, "back", x=SN_HUG, lean=-6, arm_r=100).face(T_HUG0, eyes="happy", mouth="smile")
SN.to(T_HUG1, T_HUG1 + 0.4, "io", x=SN_BACK, lean=0, arm_r=14)
SN.face(T_HUG1 + 0.2, eyes="happy", brows="up", mouth="smile_open")
# paw-bump
SN.to(T_BUMP_PAWS - 0.35, T_BUMP_PAWS, "snap", arm_r=aim_from(SN_ACT, SN_BACK, "r", PAW_MEET), look_x=8)
SN.to(T_BUMP_PAWS + 0.9, T_BUMP_PAWS + 1.3, "io", arm_r=14, look_x=0)
SN.face(T_BUMP_PAWS + 0.9, eyes="happy")

# ---------------------------------------------------------------- Crinkle's performance
CR = K.Perf(CR_ACT, seed=2, x=CR_START, y=FLOOR, arm_l=-150.0, arm_r=150.0, eyes="happy", mouth="smile",
            brows="up")
CR.to(6.8, 8.1, "lin", x=CR_X).hop(6.8, 8.1, 4, 46)
for i in range(4):
    t0 = 6.8 + i * 0.325
    CR.to(t0, t0 + 0.32, "io", arm_l=-150 + 28 * (i % 2 == 0), arm_r=150 - 28 * (i % 2 == 1),
          lean=4 * (1 if i % 2 else -1))
CR.to(8.1, 8.55, "out", arm_l=-172, arm_r=172, lean=-3)                 # wind up the big swoosh...
BUMP_A = aim_from(CR_ACT, CR_X, "l", (P.POT_AT[0] + 4, P.POT_AT[1] - 70), lean=5)
CR.to(8.55, T_BUMP, "in", arm_l=BUMP_A, arm_r=70, lean=5)               # ...right into the pot
CR.face(T_BUMP + 0.01, eyes="wide", brows="up", mouth="O")
CR.to(T_BUMP + 0.08, T_BUMP + 0.35, "back", arm_l=-155, arm_r=155, lean=0)   # paws fly up: oops!
CR.to(T_BUMP, T_BUMP + 0.12, "out", look_x=-12, look_y=8)               # stares at the wobbling pot
CR.no_blink.append((T_BUMP, 12.0))
CR.to(T_LAUNCH, T_LAUNCH + 0.25, "io", look_x=-12, look_y=-10)          # follows the flying paint
CR.to(11.2, 11.6, "io", look_x=-12, look_y=0)
CR.to(11.4, 11.9, "io", arm_l=-14, arm_r=14)
CR.face(12.0, eyes="wide", brows="worry", mouth="wobble")
# close-up on Crinkle: looks at the painting, at sad Snip... uh-oh, paws on cheeks
CR.set(17.4, look_x=-12, look_y=2)
CR.face(17.4, eyes="wide", brows="worry", mouth="wobble")
CR.to(17.9, 18.15, "io", look_x=-10, look_y=6)
CR.arms_front.append((18.3, 19.7))
CR.to(18.3, 18.65, "back", arm_l=aim_from(CR_ACT, CR_X, "l", (CR_X - 100, 1165)),
      arm_r=aim_from(CR_ACT, CR_X, "r", (CR_X + 100, 1165)), head_dy=6)
CR.face(18.3, mouth="O")
CR.to(19.4, 19.7, "io", arm_l=-14, arm_r=14, head_dy=0)
# sneaks away (tiptoe), hears a sniff, stops and looks back
CR.face(19.7, eyes="normal", brows="worry", mouth="flat")
CR.to(19.7, 20.0, "out", arm_l=-120, arm_r=120, look_x=-12, lean=-6)     # glances back at Snip as he goes
CR.to(20.0, 21.3, "lin", x=CR_SNEAK).hop(20.0, 21.3, 4, 18)
CR.to(T_SNIFF + 0.05, T_SNIFF + 0.3, "back", look_x=-14, look_y=2, lean=4, arm_l=-14, arm_r=14)
CR.face(T_SNIFF + 0.05, eyes="wide", brows="sad")
CR.face(22.3, eyes="glassy", brows="sad", mouth="frown")
CR.to(22.3, 22.7, "io", lean=0, head_dy=8)
# the choice: look at the viewer, at each choice, back at the viewer -- and wait
CR.to(23.4, 23.7, "io", look_x=0, look_y=0, head_dy=0, tilt=6).face(23.4, eyes="normal", brows="worry", mouth="flat")
CR.to(24.1, 24.4, "io", look_x=-12, look_y=-8, tilt=10)
CR.to(24.8, 25.1, "io", look_x=12, look_y=-8, tilt=-8)
CR.to(25.4, 25.7, "io", look_x=0, look_y=0, tilt=3).face(25.4, brows="up", mouth="smile")
CR.no_blink.append((25.4, 26.3))
CR.wiggle(T_PICK, "head_dy", 9, 2.5, 3.0)                               # nod: yes, say sorry
CR.face(26.5, brows="sorry", mouth="flat")
CR.to(26.5, 26.8, "io", tilt=0, look_x=-12, look_y=2)
# walks back, head down, paws together: sorry
CR.to(27.0, 28.1, "io", x=CR_NEAR).hop(27.0, 28.1, 3, 16)
PAWS_L = aim_from(CR_ACT, CR_NEAR, "l", (CR_NEAR + 6, 1370))
PAWS_R = aim_from(CR_ACT, CR_NEAR, "r", (CR_NEAR - 6, 1370))
CR.to(28.2, 28.6, "io", arm_l=PAWS_L, arm_r=PAWS_R, head_dy=16, tilt=5, look_y=8)
CR.face(28.3, eyes="closed", brows="sorry", mouth="frown")
CR.wiggle(28.7, "lean", 2.5, 1.2, 0.8)                                  # shy little sway
CR.face(29.3, eyes="glassy", brows="worry", mouth="smile")
CR.to(29.3, 29.7, "back", arm_l=-62, arm_r=62, head_dy=0, tilt=0, look_y=0, look_x=-10)   # opens his arms
CR.to(T_HUG0, T_HUG0 + 0.4, "back", x=CR_HUG, lean=6, arm_l=-60, arm_r=30).face(T_HUG0, eyes="happy", brows="calm")
CR.to(T_HUG1, T_HUG1 + 0.4, "io", x=CR_NEAR, lean=0, arm_l=-14, arm_r=14)
CR.face(T_HUG1 + 0.2, eyes="happy", brows="up", mouth="smile_open")
CR.to(T_BUMP_PAWS - 0.35, T_BUMP_PAWS, "snap", arm_l=aim_from(CR_ACT, CR_NEAR, "l", PAW_MEET), look_x=-8)
CR.to(T_BUMP_PAWS + 0.9, T_BUMP_PAWS + 1.3, "io", arm_l=-14, look_x=0)


# ---------------------------------------------------------------- props over time
def pot_pose(t):
    """(angle, base point, paint level index): rocks 3 times after the bump, then tips over."""
    if t < T_BUMP:
        return 0.0, P.POT_AT, 4
    if t < T_TIP:
        dt = t - T_BUMP
        ang = 13 * math.sin(2 * math.pi * dt / 0.46) * (1 - 0.25 * dt)
        lift = 70 * abs(math.sin(math.radians(ang))) * 0.5
        return ang, (P.POT_AT[0], P.POT_AT[1] - lift), 4
    k = ease_out_back(seg(t, T_TIP, T_TIP + 0.22), 1.2)
    ang = 90 * k
    base = (P.POT_AT[0] - 8 * k, P.POT_AT[1] - 66 * math.sin(math.radians(min(ang, 90))))
    return ang, base, (4 if t < T_LAUNCH else 1)


BLOB_PATH = smooth_curve(POT_MOUTH, (1010, 210), SPLAT_AT, 60)


def blob_pose(t):
    p = seg(t, T_LAUNCH, T_SPLAT)
    if not 0 < p < 1:
        return None
    i = min(len(BLOB_PATH) - 2, int(p * (len(BLOB_PATH) - 1)))
    f = p * (len(BLOB_PATH) - 1) - i
    (x0, y0), (x1, y1) = BLOB_PATH[i], BLOB_PATH[i + 1]
    ang = -math.degrees(math.atan2(y1 - y0, x1 - x0))
    return (lerp(x0, x1, f), lerp(y0, y1, f)), ang + 180


def pop(t, t0, d=0.28):
    return ease_out_back(seg(t, t0, t0 + d))


def dim_k(t):
    return ease_in_out(seg(t, T_DIM0, T_DIM1)) * (1 - ease_in_out(seg(t, T_UNDIM0, T_UNDIM1)))


# ---------------------------------------------------------------- drawing
def draw_set(f, t, cam):
    S = cam.S
    place(f, STOOL, S((P.STOOL_X, FLOOR)))
    ang, base, lvl = pot_pose(t)
    place(f, POTS[lvl], S(base), angle=ang)
    place(f, EASEL, S((P.EASEL_X, FLOOR)))
    place(f, BOARD, S(P.CANVAS[:2]))
    place(f, SUN, S(SUN_AT))
    place(f, FRIENDS, S(FRIENDS_AT))
    if t >= T_DAB1:
        place(f, FLOWER, S(FLOWER_AT), scale=pop(t, T_DAB1))
    if t >= T_DAB2:
        place(f, PHEART, S(HEART_AT), scale=pop(t, T_DAB2))
    if 3.2 <= t < 5.2:                          # the painting twinkles in its close-up
        for i, (x, y) in enumerate(((520, 960), (720, 1010), (600, 1210))):
            k = math.sin(math.pi * seg(t, 3.3 + 0.35 * i, 4.2 + 0.35 * i))
            if k > 0.02:
                place(f, TWINKLES[i], S((x, y)), scale=0.22 * k)
    if t >= T_SPLAT:
        place(f, SPLAT, S(SPLAT_AT), scale=0.35 + 0.65 * ease_out_back(seg(t, T_SPLAT, T_SPLAT + 0.14)))
        for i, (dx, dy) in enumerate(((-60, 70), (10, 88), (74, 66))):
            k = ease_out(seg(t, T_SPLAT + 0.2 + 0.2 * i, T_SPLAT + 2.0 + 0.25 * i))
            if k > 0.02:
                place(f, DRIPS[i], S((SPLAT_AT[0] + dx, SPLAT_AT[1] + dy)), sy=k, shadow=False)


def draw_brush(f, t, cam, st):
    px, py = SN_ACT.paw_tip(st["x"], st["y"], "l", st["arm_l"], st["hop"], st["lean"], st["sq"])
    place(f, BRUSH, cam.S((px, py)), angle=st["arm_l"] + st["lean"])


def draw_bubbles(f, t, cam):
    S = cam.S
    if t < T_RED or t >= T_UNDIM1 + 0.1:
        return
    out = ease_in_out(seg(t, T_UNDIM0, T_UNDIM1))
    red_out = ease_in_out(seg(t, T_PICK, T_PICK + 0.3))
    pulse = 1 + 0.22 * math.sin(math.pi * seg(t, T_PICK, T_PICK + 0.45))
    bob = 6 * math.sin(2 * math.pi * t / 1.6)
    place(f, BUB_HIDE, S((1150, 750 + bob)), scale=pop(t, T_RED) * (1 - red_out), alpha=1 - out)
    place(f, BUB_SORRY, S((1650, 750 - bob)), scale=pop(t, T_GREEN) * pulse, alpha=1 - out)
    if t >= T_Q:
        sway = 6 * math.sin(2 * math.pi * t / 1.0)
        place(f, QMARK, S((1400, 730)), angle=sway, scale=pop(t, T_Q) * (1 - red_out), alpha=1 - out)


def draw_hearts(f, t, cam):
    for i, (t0, x, y) in enumerate(HEART_PLAN):
        p = seg(t, t0, t0 + 1.4)
        if 0 < p < 1:
            place(f, HEARTS[i], cam.S((x + 14 * math.sin(6 * p + i), y - 150 * p)), scale=pop(t, t0, 0.3),
                  alpha=1 - ease_in_out(seg(p, 0.65, 1.0)))


def render_frame(t, view="land"):
    d = K.drawing_of(t)
    tq = d / K.DPS
    cam = CAMS[view]
    f = BGS[view].copy()
    draw_set(f, tq, cam)
    sn = SN.state(tq, d)
    cr = CR.state(tq, d)
    hug = T_HUG0 <= tq < T_HUG1 + 0.3            # in the hug Snip stands in front, so both faces show
    if hug:
        CR.draw(f, tq, cam, st=cr)
    SN.draw(f, tq, cam, st=sn)
    draw_brush(f, tq, cam, sn)
    k = dim_k(tq)
    if k > 0.001:
        f.alpha_composite(Image.new("RGBA", f.size, (40, 30, 50, int(110 * k))))
    if not hug:
        CR.draw(f, tq, cam, st=cr)
    bp = blob_pose(tq)
    if bp:
        for i, drop in enumerate(DROPS):
            tb = blob_pose(tq - 0.05 * (i + 1))
            if tb:
                place(f, drop, cam.S(tb[0]))
        place(f, BLOB, cam.S(bp[0]), angle=bp[1])
    kb = seg(tq, T_BUMP, T_BUMP + 0.3)
    if 0 < kb < 1:
        place(f, BONK, cam.S((P.POT_AT[0] + 50, P.POT_AT[1] - 90)), scale=0.45 * math.sin(math.pi * kb))
    draw_hearts(f, tq, cam)
    kp = seg(tq, T_BUMP_PAWS, T_BUMP_PAWS + 0.6)
    if 0 < kp < 1:
        place(f, SPARKLE, cam.S(PAW_MEET), scale=0.5 * math.sin(math.pi * kp), angle=40 * kp)
    draw_bubbles(f, tq, cam)
    if view == "land":
        _, centre, z = shot_at(tq)
        f = K.zoom(f, z, cam.S(centre))
    return f


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
    y = (A._lowpass(n, 4) - A._lowpass(n, 30)) * np.sin(np.pi * t / 0.12) ** 2
    return vel * 0.9 * y


def slide_whistle():
    """Cartoon flight sound for the paint (an effect, not a voice): up, then a long fall."""
    return V.SNIP.say([V.S(0.35, -7, 12, gap=0.0), V.S(1.0, 12, -10)], 0.9).y


def build_audio(path):
    M = A.midi
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    beat = 0.6

    def arp(t0, chord, beats, vel=0.42, inst=A.marimba):
        notes = MX.CHORDS[chord]
        for b in range(beats * 2):
            music.add(t0 + b * beat / 2, inst(M(notes[b % len(notes)]), 0.55, vel * (1 if b % 2 == 0 else 0.7)))

    A.jingle(music, 0.0, 0.9)
    # happy painting groove, then a bouncier dance when Crinkle arrives
    for t0, ch, root in ((0.9, "C", 48), (2.1, "F", 41), (3.3, "C", 48), (4.5, "F", 41), (5.7, "C", 48),
                         (6.9, "G", 43), (8.1, "C", 48)):
        arp(t0, ch, 2)
        music.add(t0, A.bass(M(root), 0.5, 0.7))
        music.add(t0 + 2 * beat, A.bass(M(root), 0.4, 0.5))
    for i in range(26):
        music.add(0.9 + i * beat / 2, A.shaker(0.4))
    for tt, m in ((T_DAB1, 91), (T_DAB2, 96), (T_DAB3, 98)):
        sfx.add(tt, A.pop(0.7))
        sfx.add(tt, A.glock(M(m), 0.8, 0.45))
    sfx.add(3.4, A.twinkle(0.7))
    sfx.add(5.55, A.tap(0.5))
    sfx.add(5.65, A.chime_up(0.7))
    for i in range(4):
        sfx.add(6.8 + i * 0.325 + 0.3, A.tap(0.6))
        sfx.add(6.8 + i * 0.325 + 0.15, A.boing(0.25, 420 + 40 * i))
    for tt in (7.35, 7.75):
        sfx.add(tt, A.woodblock(True, 0.4))
    # the swoosh, the bump, the wobble (tock-tock-tock), the tip, the flight, SPLAT
    sfx.add(8.6, A.whoosh(0.35, 0.7))
    sfx.add(T_BUMP, A.woodblock(False, 1.0))
    sfx.add(T_BUMP + 0.01, A.glock(M(100), 0.4, 0.35))
    for i in range(3):
        sfx.add(T_BUMP + 0.12 + i * 0.46, A.woodblock(i % 2 == 0, 0.8 - 0.1 * i))
        sfx.add(T_BUMP + 0.35 + i * 0.46, A.woodblock(i % 2 == 1, 0.7 - 0.1 * i))
    music.add(T_BUMP + 0.1, A.pad([M(55), M(59), M(62)], 1.5, 0.35))            # suspense: hold a chord
    sfx.add(T_TIP + 0.15, A.tap(0.8))
    sfx.add(T_LAUNCH - 0.05, slide_whistle())
    sfx.add(T_SPLAT, splat_snd(1.0))
    sfx.add(T_SPLAT + 0.05, A.boing(0.3, 300))
    sfx.add(12.3, A.wah_down(1.0))                                               # sad trombone: oh no
    # Snip's take, then sadness
    sfx.add(T_TAKE, A.boing(0.6, 520))
    sfx.add(T_TAKE, A.pop(0.6))
    music.add(14.6, A.pad([M(57), M(60), M(64)], 3.0, 0.5))
    for tt, m in ((15.0, 76), (15.6, 74), (16.2, 72), (16.8, 69)):
        music.add(tt, A.glock(M(m), 1.0, 0.22))
    for tt in (16.7, 16.95, T_SNIFF, T_SNIFF + 0.25):
        sfx.add(tt, sniff_snd(0.8))
    # Crinkle: uh-oh
    music.add(17.4, A.pad([M(53), M(57), M(60)], 2.4, 0.45))
    sfx.add(18.45, A.uh_oh(0.9))
    # tiptoe away (sneaky low steps), the sniff, he stops
    for i in range(4):
        sfx.add(20.0 + i * 0.325 + 0.3, A.marimba(M(45 + (i % 2) * 3), 0.25, 0.6))
    music.add(19.7, A.pad([M(50), M(57), M(62)], 1.8, 0.3))
    sfx.add(T_SNIFF + 0.35, A.boop(0.35))
    music.add(21.8, A.pad([M(57), M(60), M(64)], 1.5, 0.4))
    # the choice: tick-tock, waiting pad
    music.add(23.1, A.pad([M(50), M(57), M(62)], 1.8, 0.4))
    music.add(24.7, A.pad([M(55), M(59), M(62)], 1.8, 0.4))
    for i in range(5):
        sfx.add(23.95 + i * 0.5, A.woodblock(i % 2 == 0, 0.5))
    sfx.add(T_RED, A.pop(0.7))
    sfx.add(T_GREEN, A.pop(0.7))
    sfx.add(T_Q, A.boop(0.6))
    sfx.add(T_PICK, A.chime_up(0.8))
    # sorry: tender pad, soft falling melodica sigh, then warm and happy
    music.add(26.4, A.pad([M(48), M(55), M(64)], 2.0, 0.42))
    for i in range(3):
        sfx.add(27.0 + i * 0.37 + 0.3, A.tap(0.4))
    music.add(28.4, A.pad([M(53), M(57), M(65)], 1.8, 0.4))
    for tt, m, dd in ((28.5, 72, 0.4), (28.9, 71, 0.4), (29.3, 67, 0.7)):
        music.add(tt, MX.melodica(M(m), dd, 0.3))
    for t0, ch, root in ((29.8, "F", 41), (31.0, "C", 48)):
        arp(t0, ch, 2, 0.32)
        music.add(t0, A.bass(M(root), 0.5, 0.55))
    for tt, m, dd in ((30.1, 72, 0.5), (30.7, 76, 0.5), (31.3, 79, 0.8)):
        music.add(tt, MX.melodica(M(m), dd, 0.32))
    sfx.add(T_HUG0 + 0.1, A.twinkle(0.6))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.35))
    # paw-bump (signature)
    sfx.add(T_BUMP_PAWS - 0.55, A.snare_roll(0.5, 0.7))
    sfx.add(T_BUMP_PAWS, A.boop(0.9))
    A.jingle(music, T_BUMP_PAWS + 0.02, 1.0, ending=True)
    sfx.add(T_BUMP_PAWS + 0.05, A.twinkle(0.8))
    music.add(33.0, A.pad([M(48), M(55), M(64)], 1.0, 0.3))

    m = A.reverb(music.normalized(), 0.22)
    s = A.reverb(sfx.normalized(), 0.08)
    nm = lambda x: x / max(1e-9, abs(x).max())  # noqa: E731
    y = 0.5 * nm(m) + 0.7 * nm(s)
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.5)


# ---------------------------------------------------------------- output
KEYS = [(1.3, "1.3 Snip paints"), (4.0, "4.0 the painting"), (5.9, "5.9 proud"), (7.6, "7.6 Crinkle dances in"),
        (8.92, "8.9 bump!"), (9.6, "9.6 wobble..."), (10.5, "10.5 tips over"), (11.4, "11.4 paint flies"),
        (12.6, "12.6 SPLAT"), (14.15, "14.2 Snip: shock"), (16.4, "16.4 sad"), (18.8, "18.8 Crinkle: uh-oh"),
        (20.6, "20.6 tiptoes away"), (22.6, "22.6 hears the sniff"), (24.3, "24.3 what should he do?"),
        (28.8, "28.8 sorry"), (29.9, "29.9 hug?"), (30.8, "30.8 hug"), (32.3, "32.3 paw-bump")]


def key_sheet(path, keys=KEYS, w=480, view="land"):
    import paperlib
    h = int(w * (1080 / 1920 if view == "land" else 1920 / 1080))
    cols = 4
    rows = math.ceil(len(keys) / cols)
    sheet = Image.new("RGB", (w * cols + 10 * (cols + 1), (h + 44) * rows + 10), (250, 248, 244))
    d = ImageDraw.Draw(sheet)
    font = paperlib.round_font(22)
    for i, (tt, label) in enumerate(keys):
        im = render_frame(tt, view).convert("RGB").resize((w, h), Image.LANCZOS)
        x = 10 + (i % cols) * (w + 10)
        y = 10 + (i // cols) * (h + 44)
        d.text((x + 4, y + 4), label, fill=(60, 50, 70), font=font)
        sheet.paste(im, (x, y + 34))
    sheet.save(path)
    print("wrote", path)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "output"), exist_ok=True)
    if "--keys" in sys.argv:
        key_sheet(os.path.join(ROOT, "reviews", "pilot01_keys.png"))
    elif "--still" in sys.argv:
        tt = float(sys.argv[sys.argv.index("--still") + 1])
        view = "vert" if "--vert" in sys.argv else "land"
        out = os.path.join(ROOT, "build", f"pilot01_{view}_{tt:.2f}.png")
        render_frame(tt, view).convert("RGB").save(out)
        print("wrote", out)
    else:
        view = "vert" if "--vert" in sys.argv else "land"
        wav = os.path.join(ROOT, "build", "pilot01_audio.wav")
        build_audio(wav)
        out = os.path.join(ROOT, "output", f"pilot01_sorry_test_{view}.mp4")
        K.render_video(os.path.abspath(__file__), out, wav, DUR, view)
