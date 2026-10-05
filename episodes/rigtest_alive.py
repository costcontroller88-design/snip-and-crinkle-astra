"""Rig v2 test: "Do they look alive?" (about 14 s, landscape, rendered at 2x for sharp close-ups).

Snip and Crinkle WALK in from opposite sides (planted steps, arm swing), TURN to face each other, wave
with bending elbows, Crinkle HANDS Snip a paintbrush (paw to paw), a sharp close-up of Snip's happy face,
then a real paw-bump. Only the owner's yes/no matters: do they look alive?

Run:  python3 episodes/rigtest_alive.py              (render -> output/rigtest_alive.mp4)
      python3 episodes/rigtest_alive.py --keys       (key frames -> reviews/rigtest_keys.png)
      python3 episodes/rigtest_alive.py --still T    (one full-size frame -> build/)
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

import hires  # noqa: E402

hires.set_res(2)                                  # everything below is built at 2x

from PIL import Image, ImageDraw  # noqa: E402

import acting as K  # noqa: E402
import audio as A  # noqa: E402
import music_extra as MX  # noqa: E402
import props_artcorner as P  # noqa: E402
import rig2 as R  # noqa: E402
import scene  # noqa: E402
from paperlib import ease_in_out, ease_out_back, place, seg  # noqa: E402

RES = hires.RES
DUR = 14.0
FLOOR = P.FLOOR_Y
SN_X, CR_X, CR_NEAR = 720, 1250, 1150
HAND = (925, 1265)                                # where the brush changes paws
PAW_MEET = (932, 1245)

CAM = K.Cam("land", P.WORLD_W, P.WORLD_H, P.LAND_Y0, P.VERT_X0, res=RES)
BG = CAM.crop_bg(P.background())
EASEL = P.easel()
BOARD = P.canvas_board()
SUN = P.paint_sun()
BRUSH = P.brush().scaled(1.15)

SN = R.Perf2(R.Puppet("snip", 1.15), seed=1, x=-260, y=FLOOR, turn=0.7, eyes="normal", mouth="smile", brows="calm")
CR = R.Perf2(R.Puppet("crinkle", 1.2), seed=2, x=2240, y=FLOOR, turn=-0.7, eyes="normal", mouth="smile",
             brows="calm")


def _sparkle():
    c = hires.RCut(300, 300)
    from paperlib import star_pts
    c.polygon(star_pts(150, 150, 140, 34, 4, -90), (255, 214, 64))
    for a, r, d in ((45, 16, 92), (135, 12, 100), (225, 14, 96), (315, 12, 104)):
        x, y = 150 + d * math.cos(math.radians(a)), 150 + d * math.sin(math.radians(a))
        c.polygon(star_pts(x, y, r * 2.2, r * 0.6, 4, -90), (255, 255, 255))
    return c.finish(pivot=(150, 150), border=5)


SPARK = _sparkle()

# ---------------------------------------------------------------- the performances
# walk in from both sides
SN.walk(0.3, 3.0, SN_X)
CR.walk(0.7, 3.4, CR_X)
SN.face(1.2, eyes="normal", brows="calm").blink(1.6)
# Crinkle carries the brush in his left paw, held up a little
CR.set(0.0, arm_l=-30, elb_l=60)
# they see each other: brows up, big smiles
SN.face(3.0, eyes="sparkle", brows="up", mouth="smile_open")
CR.face(3.4, eyes="happy", brows="up", mouth="smile_open")
SN.ears(3.0, 3.3, "perk")
# Snip waves with the near paw, drawn in front of the head so the wave is seen
SN.arms_front.append((3.4, 5.05))
SN.reach(3.4, 3.75, "l", (SN_X - 40, 1140), "back")
for i in range(4):
    t0 = 3.75 + i * 0.22
    SN.to(t0, t0 + 0.22, "io", elb_l=70 if i % 2 == 0 else 20)
SN.to(4.7, 5.0, "io", arm_l=-10, elb_l=14)
# Crinkle waves back with his free (near) paw
CR.arms_front.append((3.9, 5.55))
CR.reach(3.9, 4.25, "r", (CR_X + 60, 1110), "back")
for i in range(4):
    t0 = 4.25 + i * 0.22
    CR.to(t0, t0 + 0.22, "io", elb_r=-70 if i % 2 == 0 else -20)
CR.to(5.15, 5.45, "io", arm_r=10, elb_r=-14)
# the brush: Crinkle steps closer, both turn a little toward the camera, he offers, Snip takes
CR.walk(5.0, 5.6, CR_NEAR, steps=1)
SN.to(5.0, 5.4, "io", turn=0.3).face(5.0, eyes="normal", mouth="smile")
CR.to(5.3, 5.7, "io", turn=-0.3).face(5.3, eyes="normal", mouth="smile")
CR.reach(5.6, 6.0, "l", HAND, "back")
SN.reach(5.8, 6.15, "r", HAND, "back")
T_GIVE = 6.2
CR.to(6.4, 6.8, "io", arm_l=-10, elb_l=14)
SN.reach(6.4, 6.85, "r", (SN_X + 150, 1300), "back")             # holds it up beside the face
SN.face(6.4, eyes="sparkle", brows="up", mouth="smile_open").ears(6.4, 6.7, "happy")
SN.wiggle(6.9, "ear_k", 0.1, 4.0, 3.0)
CR.face(6.5, eyes="happy", mouth="smile")
# close-up: Snip turns to the camera, then to Crinkle with a big thank-you smile
SN.to(7.3, 7.7, "io", turn=0.0, look_x=0)
SN.face(7.7, eyes="happy", brows="up", mouth="smile_open")
SN.to(8.6, 9.0, "io", turn=0.55, look_x=6).face(8.6, eyes="sparkle", mouth="smile_open")
SN.hop(9.2, 9.55, 1, 26)
# paw-bump (Snip keeps the brush in the right paw and bumps with it, brush and all)
SN.to(10.0, 10.4, "io", turn=0.35)
CR.to(10.0, 10.4, "io", turn=-0.35)
T_BUMP = 11.0
CR.reach(10.55, T_BUMP, "l", (PAW_MEET[0] + 18, PAW_MEET[1]), "snap")
SN.reach(10.55, T_BUMP, "r", (PAW_MEET[0] - 18, PAW_MEET[1]), "snap")
SN.face(T_BUMP, eyes="happy", mouth="smile_open")
CR.face(T_BUMP, eyes="happy", mouth="smile_open")
SN.to(11.7, 12.1, "io", arm_r=10, elb_r=-14, turn=0.0)
CR.to(11.7, 12.1, "io", arm_l=-10, elb_l=14, turn=0.0)
SN.hop(12.3, 12.7, 1, 30)
CR.hop(12.4, 12.8, 1, 26)
SN.ears(12.3, 12.6, "perk")

SHOTS = [
    (0.0, (960, 1100), 1.0),
    (7.3, (SN_X + 40, 1080), 1.9),                # sharp close-up on Snip
    (10.0, (935, 1150), 1.3),
]


def shot_at(t):
    cur = SHOTS[0]
    for s in SHOTS:
        if t >= s[0]:
            cur = s
    return cur


# ---------------------------------------------------------------- drawing
def brush_holder(t):
    return (CR, "l") if t < T_GIVE else (SN, "r")


def draw_brush(f, t, st):
    perf, side = brush_holder(t)
    W, fa = perf.paw(t, side, st[id(perf)])
    ang = fa if perf is CR else 180 + 12 * ease_in_out(seg(t, T_GIVE, T_GIVE + 0.4)) + (fa - 180) * (1 - ease_in_out(seg(t, T_GIVE, T_GIVE + 0.4)))
    place(f, BRUSH, CAM.S(W), angle=ang)                      # Snip holds it upright once it's his


def render_frame(t, view="land"):
    d = K.drawing_of(t)
    tq = d / K.DPS
    f = BG.copy()
    place(f, EASEL, CAM.S((P.EASEL_X, FLOOR)))
    place(f, BOARD, CAM.S(P.CANVAS[:2]))
    place(f, SUN, CAM.S((528, 992)))
    sn, cr = SN.state(tq, d), CR.state(tq, d)
    st = {id(SN): sn, id(CR): cr}
    perf, side = brush_holder(tq)
    holder_turn = st[id(perf)]["turn"]
    far = (side == "r" and holder_turn > 0.35) or (side == "l" and holder_turn < -0.35)
    if far and perf is SN:
        draw_brush(f, tq, st)
    SN.draw(f, tq, CAM, st=sn)
    if far and perf is CR:
        draw_brush(f, tq, st)
    CR.draw(f, tq, CAM, st=cr)
    if not far:
        draw_brush(f, tq, st)
    kp = seg(tq, T_BUMP, T_BUMP + 0.6)
    if 0 < kp < 1:
        place(f, SPARK, CAM.S(PAW_MEET), scale=0.5 * math.sin(math.pi * kp), angle=40 * kp)
    _, centre, z = shot_at(tq)
    f = K.zoom(f, z * 1.0, CAM.S(centre)) if z > 1.0001 else f
    return f.resize((1920, 1080), Image.LANCZOS)


# ---------------------------------------------------------------- sound
def build_audio(path):
    M = A.midi
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    beat = 0.6
    A.jingle(music, 0.0, 0.8)
    for t0, ch, root in ((0.6, "C", 48), (1.8, "F", 41), (3.0, "C", 48), (4.2, "G", 43), (5.4, "C", 48),
                         (6.6, "F", 41), (7.8, "C", 48), (9.0, "G", 43), (10.2, "C", 48), (11.4, "F", 41),
                         (12.6, "C", 48)):
        notes = MX.CHORDS[ch]
        for b in range(4):
            music.add(t0 + b * beat / 2, A.marimba(M(notes[b % 4]), 0.5, 0.38 if b % 2 == 0 else 0.26))
        music.add(t0, A.bass(M(root), 0.5, 0.6))
    for i, tt in enumerate(sorted(SN.footfalls() + CR.footfalls())):
        sfx.add(tt, A.tap(0.55 + 0.1 * (i % 2)))
    for tt in (3.75, 4.25):
        sfx.add(tt, A.twinkle(0.5))
    sfx.add(T_GIVE, A.pop(0.7))
    sfx.add(T_GIVE + 0.05, A.chime_up(0.6))
    sfx.add(7.7, A.twinkle(0.6))
    sfx.add(9.2, A.boing(0.35, 420))
    sfx.add(T_BUMP - 0.5, A.snare_roll(0.45, 0.6))
    sfx.add(T_BUMP, A.boop(0.9))
    A.jingle(music, T_BUMP + 0.02, 1.0, ending=True)
    sfx.add(T_BUMP + 0.05, A.twinkle(0.8))
    sfx.add(12.3, A.boing(0.3, 380))
    sfx.add(12.4, A.boing(0.3, 300))
    music.add(13.0, A.pad([M(48), M(55), M(64)], 1.0, 0.3))
    m = A.reverb(music.normalized(), 0.22)
    s = A.reverb(sfx.normalized(), 0.08)
    nm = lambda x: x / max(1e-9, abs(x).max())  # noqa: E731
    y = 0.5 * nm(m) + 0.65 * nm(s)
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95), fade_out=0.5)


KEYS = [(1.2, "1.2 walking in"), (2.4, "2.4 steps"), (3.6, "3.6 they see each other"), (4.2, "4.2 waves"),
        (5.9, "5.9 hands over the brush"), (6.9, "6.9 Snip looks at it"), (8.0, "8.0 close-up (sharp?)"),
        (9.3, "9.3 thank-you smile"), (11.05, "11.0 paw-bump"), (12.5, "12.5 happy hop")]


def key_sheet(path, keys=KEYS, w=480):
    import paperlib
    h = int(w * 1080 / 1920)
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
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "output"), exist_ok=True)
    if "--keys" in sys.argv:
        key_sheet(os.path.join(ROOT, "reviews", "rigtest_keys.png"))
    elif "--still" in sys.argv:
        tt = float(sys.argv[sys.argv.index("--still") + 1])
        out = os.path.join(ROOT, "build", f"rigtest_{tt:.2f}.png")
        render_frame(tt).convert("RGB").save(out)
        print("wrote", out)
    else:
        wav = os.path.join(ROOT, "build", "rigtest_audio.wav")
        build_audio(wav)
        K.render_video(os.path.abspath(__file__), os.path.join(ROOT, "output", "rigtest_alive.mp4"), wav, DUR, "land")
