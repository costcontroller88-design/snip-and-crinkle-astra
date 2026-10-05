"""Pilot test scene: "Oops! Say Sorry" (first half of the pilot long-form episode).

The pilot's job is to prove the new standard before Episode 11: instrument voices with lip-sync,
eyebrows and bigger acting (wind-up and overshoot), Snip's ears showing feelings, drawing on twos
with a paper wobble, slower toddler pacing, Crinkle asking the viewer and waiting, and one world
filmed in both landscape (long-form) and vertical (Shorts).

Story engine B (Crinkle makes the mistake). Snip hums while finishing a painting, steps back proudly.
Crinkle dances in, giggles back at Snip, and his big happy arm swoosh knocks the paint pot: a blue
blob sails over Snip's head and SPLATS on the painting. Snip gasps; the ears droop; a sad slide-whistle
"aww". Crinkle: uh-oh, paws to mouth. He turns to the viewer and asks (hum, shrug): sneak away, or say
sorry? Long pause while he looks at each choice and back at the viewer. Then he walks over, paw on
heart, a slow sorry hum; Snip's ears lift, a small "ok", a hug with hearts. Crinkle gets an idea...
(the second half, fixing the painting together, comes next session).

Run:  python3 episodes/pilot01_sorry_test.py              (landscape render -> output/)
      python3 episodes/pilot01_sorry_test.py --vert       (vertical render)
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

DUR = 27.0
FLOOR = P.FLOOR_Y
SN_X, SN_BACK = 900, 960
CR_X, CR_START, CR_NEAR = 1480, 2200, 1330
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
IDEA = scene.sparkle()
HEARTS = [scene.heart(c, 74) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120))]

SN_ACT = K.Actor("snip", 1.15)
CR_ACT = K.Actor("crinkle", 1.2)
BRUSH_LEN = 166                        # paw to bristle tip


def aim_from(actor, x, side, target, lean=0.0, y=FLOOR):
    sh = actor.shoulder_pt(x, y, side, 0.0, lean, 1.0)
    return math.degrees(math.atan2(target[0] - sh[0], target[1] - sh[1])) - lean


def brush_tip(x, arm, lean=0.0):
    px, py = SN_ACT.paw_tip(x, FLOOR, "l", arm, 0.0, lean, 1.0)
    a = math.radians(arm + lean)
    return px + BRUSH_LEN * math.sin(a), py + BRUSH_LEN * math.cos(a)


# ---------------------------------------------------------------- timing
T_DAB1, T_DAB2 = 1.3, 2.2
DAB1_A, DAB2_A = -148.0, -162.0
FLOWER_AT = brush_tip(SN_X, DAB1_A, 2.0)
FLOWER_AT = (FLOWER_AT[0], FLOWER_AT[1] + 20)          # the flower head sits where the brush touched
HEART_AT = brush_tip(SN_X, DAB2_A, 2.0)
SUN_AT, FRIENDS_AT = (528, 992), (598, 1148)
SPLAT_AT = (648, 1116)
T_BUMP, T_SPLAT = 5.62, 6.06
POT_TOP = (P.POT_AT[0] - 10, P.POT_AT[1] - 120)
T_DIM0, T_DIM1, T_UNDIM0, T_UNDIM1 = 11.3, 11.75, 16.8, 17.5
T_RED, T_GREEN, T_Q, T_PICK = 11.6, 11.9, 12.1, 16.3
T_HUG0, T_HUG1 = 21.9, 23.8
HEART_PLAN = ((22.25, 1110, 830), (22.5, 1210, 780), (22.75, 1010, 800))
T_IDEA = 25.0
ZOOM_FOCUS_WORLD = (CR_X, 1060)

# ---------------------------------------------------------------- Snip's performance
SN = K.Perf(SN_ACT, seed=1, x=SN_X, y=FLOOR, lean=2.0, arm_l=-140.0, arm_r=14.0, eyes="happy", mouth="smile",
            brows="calm", look_x=-10.0, ear_l=-4.0, ear_r=4.0, ear_k=1.04)
SN.say(0.45, V.snip("hum"))
SN.say(1.75, V.snip("hum2", 0.85))
(SN.to(0.25, 0.6, "io", arm_l=-152).to(0.6, 0.95, "io", arm_l=-138).to(0.95, T_DAB1, "antic", arm_l=DAB1_A)
   .to(T_DAB1, 1.6, "out", arm_l=-140).to(1.6, T_DAB2, "antic", arm_l=DAB2_A).to(T_DAB2, 2.55, "out", arm_l=-150))
SN.face(0.0, eyes="happy").face(1.2, eyes="normal").face(2.4, eyes="sparkle")
SN.wiggle(T_DAB1, "ear_r", 9).wiggle(T_DAB2, "ear_l", -9)
# step back, ta-da!
SN.to(2.6, 3.0, "io", x=SN_BACK, arm_l=-30, lean=0).hop(2.6, 3.0, 1, 22)
SN.to(3.0, 3.35, "snap", arm_r=140, arm_l=-100).ears(3.0, 3.3, "perk")
SN.face(3.0, eyes="happy", brows="up", mouth="smile_open")
SN.say(3.05, V.snip("ta_da"))
SN.to(3.9, 4.3, "io", arm_r=14, arm_l=-20)
# Crinkle's dancing in: look over, giggle
SN.to(4.0, 4.3, "out", look_x=10, lean=-3).face(4.0, eyes="normal", brows="up", mouth="smile")
SN.say(4.5, V.snip("giggle", 0.9))
SN.face(4.5, eyes="happy")
# back to admiring the painting (so the bump happens behind Snip's back)
SN.to(5.2, 5.5, "io", look_x=-10, lean=2).face(5.2, eyes="sparkle", brows="calm", mouth="smile")
SN.ears(5.2, 5.6, "happy")
# SPLAT: gasp, ears shoot up, fur frizz, a little jump
SN.face(T_SPLAT + 0.02, eyes="wide", brows="up", mouth="O")
SN.ears(T_SPLAT + 0.02, T_SPLAT + 0.22, "alarm", "snap").hop(T_SPLAT + 0.02, T_SPLAT + 0.36, 1, 28)
SN.to(T_SPLAT + 0.02, T_SPLAT + 0.18, "out", frizz=0.9).to(T_SPLAT + 0.3, T_SPLAT + 0.6, "io", frizz=0.0)
SN.to(T_SPLAT, T_SPLAT + 0.2, "back", arm_l=-60, arm_r=60)
SN.say(T_SPLAT + 0.05, V.snip("gasp"))
SN.no_blink.append((T_SPLAT, T_SPLAT + 0.8))
# sadness: ears droop slowly, glassy eyes, a falling "aww"
SN.to(6.7, 7.3, "io", arm_l=-12, arm_r=12, head_dy=12, lean=3, look_x=-10, look_y=4)
SN.ears(6.8, 8.2, "droop", "io")
SN.face(6.9, eyes="glassy", brows="sad", mouth="frown")
SN.say(7.0, V.snip("aww"))
SN.say(8.3, V.snip("sniff", 0.8))
SN.wiggle(8.3, "head_dy", -3, 6.0, 6.0)
# Crinkle comes over and says sorry: Snip turns to him, ears lift a little
SN.to(19.0, 19.5, "io", look_x=10, look_y=0, lean=-1)
SN.ears(19.4, 20.0, "sad", "io")
SN.face(19.6, eyes="normal", brows="sad", mouth="frown")
SN.face(21.2, mouth="smile", brows="calm")
SN.to(21.2, 21.6, "out", head_dy=0)
SN.say(21.3, V.snip("mm_ok", 0.9))
SN.ears(21.5, 22.1, "up", "back")
# hug
SN.to(T_HUG0, T_HUG0 + 0.4, "back", x=SN_HUG, lean=-6, arm_r=100).face(T_HUG0, eyes="happy", mouth="smile")
SN.to(T_HUG1, T_HUG1 + 0.4, "io", x=SN_BACK, lean=0, arm_r=14)
SN.face(T_HUG1 + 0.2, eyes="normal")
# Crinkle's idea: Snip looks at the painting, curious, then excited
SN.to(24.9, 25.2, "out", look_x=-10, look_y=0).ears(24.9, 25.3, "curious")
SN.say(25.25, V.snip("hm_q"))
SN.face(25.9, eyes="sparkle", brows="up", mouth="smile_open").ears(25.9, 26.2, "perk")
SN.to(25.9, 26.2, "back", look_x=8)

# ---------------------------------------------------------------- Crinkle's performance
CR = K.Perf(CR_ACT, seed=2, x=CR_START, y=FLOOR, arm_l=-150.0, arm_r=150.0, eyes="happy", mouth="smile",
            brows="up")
CR.say(3.5, V.crinkle("dance"))
CR.to(3.7, 5.0, "lin", x=CR_X).hop(3.7, 5.0, 4, 46)
for i in range(4):
    t0 = 3.7 + i * 0.325
    CR.to(t0, t0 + 0.32, "io", arm_l=-150 + 28 * (i % 2 == 0), arm_r=150 - 28 * (i % 2 == 1),
          lean=4 * (1 if i % 2 else -1))
CR.to(5.0, 5.3, "out", arm_l=-172, arm_r=172, lean=-3)                  # wind up the big swoosh...
BUMP_A = aim_from(CR_ACT, CR_X, "l", (P.POT_AT[0] + 4, P.POT_AT[1] - 70), lean=5)
CR.to(5.3, T_BUMP, "in", arm_l=BUMP_A, arm_r=70, lean=5)                # ...whoosh, right into the pot
CR.face(T_BUMP + 0.01, eyes="wide", brows="up", mouth="O")
CR.wiggle(T_BUMP, "arm_l", 8).to(T_BUMP, T_BUMP + 0.3, "back", lean=0)
CR.say(T_BUMP + 0.06, V.crinkle("oops"))
CR.to(T_BUMP, T_BUMP + 0.1, "out", look_x=-10, look_y=8)
CR.to(5.78, 5.95, "io", look_x=-12, look_y=-10)                        # follows the flying paint
CR.to(T_SPLAT, T_SPLAT + 0.12, "out", look_x=-12, look_y=0)
CR.to(6.3, 6.8, "io", arm_l=-14, arm_r=14)
CR.face(6.7, eyes="normal", brows="worry", mouth="wobble")
CR.to(6.6, 7.0, "io", look_x=-10, look_y=2)
# uh-oh: paws on cheeks
MOUTH_L = (CR_X - 100, 1165)
MOUTH_R = (CR_X + 100, 1165)
CR.to(8.4, 8.75, "back", arm_l=aim_from(CR_ACT, CR_X, "l", MOUTH_L), arm_r=aim_from(CR_ACT, CR_X, "r", MOUTH_R),
      head_dy=6)
CR.face(8.4, eyes="wide", brows="worry")
CR.say(8.75, V.crinkle("uh_oh"))
CR.to(9.6, 10.0, "io", arm_l=-14, arm_r=14, head_dy=0)
# turns to the viewer and asks
CR.to(10.0, 10.4, "out", look_x=0, look_y=0, tilt=6).face(10.0, eyes="normal", brows="worry", mouth="flat")
CR.to(10.45, 10.8, "back", arm_l=-62, arm_r=62).wiggle(10.45, "head_dy", -4, 3.0, 4.0)
CR.say(10.6, V.crinkle("hm_q"))
CR.to(11.2, 11.5, "io", arm_l=-14, arm_r=14)
# the choice: look at each bubble, back at the viewer, a little nod -- and wait
CR.to(12.4, 12.7, "io", look_x=-12, look_y=-8, tilt=10).face(12.4, brows="worry")
CR.to(13.6, 13.9, "io", look_x=12, look_y=-8, tilt=-8).face(13.6, brows="calm")
CR.to(14.8, 15.1, "io", look_x=0, look_y=0, tilt=3).face(14.8, brows="up", mouth="smile")
CR.wiggle(15.3, "head_dy", 7, 2.2, 2.5)
CR.no_blink.append((15.2, 16.2))
# the answer: yes, say sorry
CR.say(16.35, V.crinkle("mm_hm"))
CR.wiggle(16.35, "head_dy", 8, 2.5, 3.0)
CR.face(16.8, brows="sorry", mouth="flat")
CR.to(16.8, 17.1, "io", tilt=0, look_x=-10, look_y=2)
CR.to(17.4, 18.5, "io", x=CR_NEAR).hop(17.4, 18.5, 3, 16)
PAW_HEART = aim_from(CR_ACT, CR_NEAR, "r", (CR_NEAR - 10, 1300))
CR.to(18.5, 18.9, "back", arm_r=PAW_HEART, head_dy=14, tilt=6)
CR.face(18.8, eyes="closed", brows="sorry", mouth="flat")
CR.say(18.9, V.crinkle("sorry"))
CR.face(20.85, eyes="glassy", brows="worry", mouth="smile")
CR.to(20.9, 21.3, "back", arm_l=-62, arm_r=62, head_dy=0, tilt=0)         # opens his arms: a hug?
CR.to(T_HUG0, T_HUG0 + 0.4, "back", x=CR_HUG, lean=6, arm_l=-60, arm_r=30).face(T_HUG0, eyes="happy", brows="calm")
CR.to(T_HUG1, T_HUG1 + 0.4, "io", x=CR_NEAR, lean=0, arm_l=-14, arm_r=14)
CR.face(T_HUG1 + 0.2, eyes="normal", mouth="smile")
# an idea!
CR.to(24.0, 24.35, "io", look_x=-12, look_y=0, arm_r=aim_from(CR_ACT, CR_NEAR, "r", (CR_NEAR + 30, 1170)))
CR.face(24.0, brows="focus", mouth="hum")
CR.face(T_IDEA, eyes="sparkle", brows="up", mouth="smile_open")
CR.to(T_IDEA, T_IDEA + 0.35, "snap", arm_r=150, arm_l=-150).hop(T_IDEA, T_IDEA + 0.35, 1, 24)
CR.say(T_IDEA + 0.1, V.crinkle("fix_it"))
CR.to(26.0, 26.4, "io", arm_l=-120, arm_r=120)


# ---------------------------------------------------------------- props over time
def pot_pose(t):
    """(angle, base point, paint level index) of the pot on the stool."""
    if t < T_BUMP:
        return 0.0, P.POT_AT, 4
    k = ease_out_back(seg(t, T_BUMP, T_BUMP + 0.22), 1.2)
    ang = 90 * k
    base = (P.POT_AT[0] - 8 * k, P.POT_AT[1] - 66 * math.sin(math.radians(min(ang, 90))))
    lvl = 4 if t < T_BUMP + 0.12 else 1
    return ang, base, lvl


BLOB_PATH = smooth_curve(POT_TOP, (1000, 190), SPLAT_AT, 40)


def blob_pose(t):
    p = seg(t, T_BUMP + 0.04, T_SPLAT)
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


def zoom_k(t):
    return 1 + 0.16 * ease_in_out(seg(t, 10.0, 11.0)) * (1 - ease_in_out(seg(t, 17.3, 18.4)))


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
    if t >= T_SPLAT:
        place(f, SPLAT, S(SPLAT_AT), scale=0.35 + 0.65 * ease_out_back(seg(t, T_SPLAT, T_SPLAT + 0.14)))
        for i, (dx, dy) in enumerate(((-60, 70), (10, 88), (74, 66))):
            k = ease_out(seg(t, T_SPLAT + 0.2 + 0.15 * i, T_SPLAT + 1.6 + 0.2 * i))
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
    place(f, BUB_HIDE, S((CR_X - 290, 800 + bob)), scale=pop(t, T_RED) * (1 - red_out), alpha=1 - out)
    place(f, BUB_SORRY, S((CR_X + 290, 800 - bob)), scale=pop(t, T_GREEN) * pulse, alpha=1 - out)
    if t >= T_Q:
        sway = 6 * math.sin(2 * math.pi * t / 1.0)
        place(f, QMARK, S((CR_X, 745)), angle=sway, scale=pop(t, T_Q) * (1 - red_out), alpha=1 - out)


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
        shade = Image.new("RGBA", f.size, (40, 30, 50, int(110 * k)))
        f.alpha_composite(shade)
    if not hug:
        CR.draw(f, tq, cam, st=cr)
    bp = blob_pose(tq)
    if bp:
        for i, drop in enumerate(DROPS):
            tb = blob_pose(tq - 0.035 * (i + 1))
            if tb:
                place(f, drop, cam.S(tb[0]))
        place(f, BLOB, cam.S(bp[0]), angle=bp[1])
    kb = seg(tq, T_BUMP, T_BUMP + 0.3)
    if 0 < kb < 1:
        place(f, BONK, cam.S((P.POT_AT[0] + 50, P.POT_AT[1] - 90)), scale=0.45 * math.sin(math.pi * kb))
    draw_hearts(f, tq, cam)
    if tq >= T_IDEA:
        place(f, IDEA, cam.S((CR_NEAR + 10, 760)), scale=0.55 * pop(tq, T_IDEA), angle=12 * math.sin(tq * 4),
              alpha=1 - ease_in_out(seg(tq, 26.2, 26.8)))
    draw_bubbles(f, tq, cam)
    if view == "land":
        f = K.zoom(f, zoom_k(tq), cam.S(ZOOM_FOCUS_WORLD))
    return f


# ---------------------------------------------------------------- sound
def splat_snd(vel=1.0):
    t = A._t(0.55)
    n = np.random.default_rng(5).normal(0, 1, len(t))
    wet = (A._lowpass(n, 6) - A._lowpass(n, 70)) * A._attack(t, 3000) * np.exp(-t * 12)
    thump = np.sin(2 * np.pi * np.cumsum(110 - 60 * t) / A.SR) * np.exp(-t * 18)
    return vel * (1.5 * wet + 0.9 * thump)


def build_audio(path):
    M = A.midi
    music, sfx, vox = A.Mix(DUR), A.Mix(DUR), A.Mix(DUR)
    beat = 0.6

    def arp(t0, chord, beats, vel=0.42, inst=A.marimba, octave=0):
        notes = MX.CHORDS[chord]
        for b in range(beats * 2):
            music.add(t0 + b * beat / 2, inst(M(notes[b % len(notes)] + octave), 0.55, vel * (1 if b % 2 == 0 else 0.7)))

    A.jingle(music, 0.0, 0.9)
    # happy painting groove (C F C G)
    for t0, ch, root in ((0.9, "C", 48), (2.1, "F", 41), (3.3, "C", 48), (4.5, "G", 43)):
        arp(t0, ch, 2)
        music.add(t0, A.bass(M(root), 0.5, 0.7))
        music.add(t0 + 2 * beat, A.bass(M(root), 0.4, 0.5))
    for i in range(14):
        music.add(0.9 + i * beat / 2, A.shaker(0.4))
    for tt in (T_DAB1, T_DAB2):
        sfx.add(tt, A.pop(0.7))
        sfx.add(tt, A.glock(M(91 if tt == T_DAB1 else 96), 0.8, 0.45))
    sfx.add(3.05, A.twinkle(0.6))
    sfx.add(2.95, A.tap(0.5))
    for i in range(4):
        sfx.add(3.7 + i * 0.325 + 0.3, A.tap(0.55))
    # bump, flight, splat
    sfx.add(T_BUMP, A.woodblock(False, 0.9))
    sfx.add(T_BUMP + 0.01, A.glock(M(100), 0.4, 0.35))
    sfx.add(T_BUMP + 0.18, A.tap(0.7))
    sfx.add(T_BUMP + 0.05, A.whoosh(0.42, 0.8))
    sfx.add(T_SPLAT, splat_snd(1.0))
    sfx.add(T_SPLAT + 0.05, A.boing(0.35, 300))
    # sad: soft pads
    music.add(6.35, A.pad([M(57), M(60), M(64)], 2.8, 0.5))
    music.add(9.0, A.pad([M(53), M(57), M(60)], 2.6, 0.45))
    for tt, m in ((7.1, 76), (7.7, 72), (8.3, 69)):
        music.add(tt, A.glock(M(m), 1.0, 0.18))
    # the choice: tick-tock, waiting pad
    music.add(11.3, A.pad([M(50), M(57), M(62)], 2.6, 0.4))
    music.add(13.7, A.pad([M(55), M(59), M(62)], 2.8, 0.4))
    for i in range(8):
        sfx.add(12.2 + i * 0.5, A.woodblock(i % 2 == 0, 0.5))
    sfx.add(T_RED, A.pop(0.7))
    sfx.add(T_GREEN, A.pop(0.7))
    sfx.add(T_Q, A.boop(0.6))
    sfx.add(T_PICK, A.chime_up(0.8))
    # sorry: tender pad + slow glock
    music.add(16.4, A.pad([M(48), M(55), M(64)], 2.6, 0.42))
    music.add(18.8, A.pad([M(53), M(57), M(65)], 2.4, 0.4))
    music.add(21.0, A.pad([M(55), M(59), M(62)], 1.2, 0.4))
    for i in range(3):
        sfx.add(17.4 + i * 0.37 + 0.3, A.tap(0.4))
    for tt, m in ((19.0, 72), (19.6, 71), (20.2, 69), (20.8, 67)):
        music.add(tt, A.glock(M(m), 1.0, 0.16))
    # hug: warm and happy (melodica lead, marimba)
    for t0, ch, root in ((21.6, "F", 41), (22.8, "C", 48), (24.0, "F", 41), (25.2, "G", 43)):
        arp(t0, ch, 2, 0.32)
        music.add(t0, A.bass(M(root), 0.5, 0.55))
    for tt, m, d in ((21.9, 72, 0.5), (22.5, 76, 0.5), (23.1, 79, 0.9), (24.0, 77, 0.5), (24.6, 76, 0.5)):
        music.add(tt, MX.melodica(M(m), d, 0.32))
    sfx.add(T_HUG0 + 0.1, A.twinkle(0.6))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.35))
    sfx.add(T_IDEA, A.chime_up(0.7, (84, 88, 91, 96)))
    sfx.add(T_IDEA + 0.32, A.tap(0.5))
    music.add(26.0, A.pad([M(55), M(59), M(62), M(67)], 1.2, 0.35))
    music.add(26.4, A.glock(M(91), 0.6, 0.3))
    # voices
    for perf in (SN, CR):
        for t0, line in perf.lines:
            vox.add(t0, line.y)

    m = A.reverb(music.normalized(), 0.22)
    s = A.reverb(sfx.normalized(), 0.08)
    v = A.reverb(vox.normalized(), 0.12)
    nm = lambda x: x / max(1e-9, abs(x).max())  # noqa: E731
    y = 0.42 * nm(m) + 0.55 * nm(s) + 0.8 * nm(v)
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.4)


# ---------------------------------------------------------------- output
KEYS = [(1.33, "1.3 dab"), (3.2, "3.2 ta-da!"), (4.6, "4.6 dance in"), (5.66, "5.7 bump"),
        (5.9, "5.9 over Snip's head"), (6.2, "6.2 SPLAT"), (7.9, "7.9 aww (ears droop)"),
        (8.9, "8.9 uh-oh"), (10.8, "10.8 asks the viewer"), (12.6, "12.6 hide?"), (13.8, "13.8 or sorry?"),
        (15.4, "15.4 waits for you"), (19.4, "19.4 sorry"), (21.5, "21.5 ok"), (22.6, "22.6 hug"),
        (25.4, "25.4 idea!")]


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
    elif "--audio" in sys.argv:
        build_audio(os.path.join(ROOT, "build", "pilot01_audio.wav"))
    else:
        view = "vert" if "--vert" in sys.argv else "land"
        wav = os.path.join(ROOT, "build", "pilot01_audio.wav")
        build_audio(wav)
        out = os.path.join(ROOT, "output", f"pilot01_sorry_test_{view}.mp4")
        K.render_video(os.path.abspath(__file__), out, wav, DUR, view)
