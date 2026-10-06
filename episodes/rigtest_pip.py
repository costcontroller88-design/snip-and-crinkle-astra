"""Pip in rig v2: test sheet for Episode 11 (plan items N1 and N7), rendered at 2x.

Rows: turns (body and head-only); the waddle walk, the waddle-run, a wing reaching to a point with a marker
(tip on the target), a wing point; faces; tuft moods, puff-up and the copycat dance; Pip (0.9) beside Snip (1.15)
and Crinkle (1.2); Crinkle's tongue right / middle / left (N7).

Run:  python3 episodes/rigtest_pip.py            (-> reviews/ep11_pip_rig.png)
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

import hires  # noqa: E402

hires.set_res(2)

from PIL import Image, ImageDraw  # noqa: E402

import paperlib  # noqa: E402
import rig2 as R  # noqa: E402
import rig2_pip as RP  # noqa: E402

RES = hires.RES
FLOOR = 1000
WALL, FLOOR_COL, FLOOR_LINE = (244, 234, 222), (226, 200, 166), (200, 168, 130)
INK = (60, 50, 70)

PIP = RP.PipPuppet(0.9)
MARKER = RP.marker_sprite((250, 250, 246), (220, 50, 60), scale=0.9)


class PanelCam:
    def __init__(self, x0, y0):
        self.ox, self.oy, self.res = x0, y0, RES

    def S(self, p):
        return (p[0] - self.ox) * self.res, (p[1] - self.oy) * self.res


def canvas(x0, y0, w, h):
    img = Image.new("RGBA", (int(w * RES), int(h * RES)), WALL + (255,))
    d = ImageDraw.Draw(img)
    fy = (FLOOR - y0) * RES
    if fy < img.height:
        d.rectangle([0, fy, img.width, img.height], fill=FLOOR_COL + (255,))
        d.line([(0, fy), (img.width, fy)], fill=FLOOR_LINE + (255,), width=int(2 * RES))
    return img, PanelCam(x0, y0)


def pip(**init):
    base = dict(x=500, y=FLOOR)
    base.update(init)
    p = RP.PipPerf(PIP, seed=3, **base)
    p.blinks = []
    return p


def body_panel(perf, t=1.0, cx=None, w=340, h=420, extra=None, others=()):
    cx = perf.state(t)["x"] if cx is None else cx
    img, cam = canvas(cx - w / 2, FLOOR + 50 - h, w, h)
    for o in others:
        o.draw(img, t, cam)
    st = perf.state(t)
    perf.draw(img, t, cam, st=st)
    if extra:
        extra(img, cam, st)
    return img


def face_panel(perf, t=1.0, w=300, h=300):
    st = perf.state(t)
    hx, hy = perf.a.head_centre(st)
    img, cam = canvas(hx - w / 2, hy - h / 2 + 20, w, h)
    perf.draw(img, t, cam, st=st)
    return img


def cross(img, cam, p, col=(40, 120, 220), r=7):
    d = ImageDraw.Draw(img)
    x, y = cam.S(p)
    r *= RES
    d.line([(x - r, y), (x + r, y)], fill=col + (255,), width=int(1.5 * RES))
    d.line([(x, y - r), (x, y + r)], fill=col + (255,), width=int(1.5 * RES))


def ring(img, cam, p, col=(40, 120, 220), r=5):
    d = ImageDraw.Draw(img)
    x, y = cam.S(p)
    r *= RES
    d.ellipse([x - r, y - r, x + r, y + r], outline=col + (255,), width=int(1.2 * RES))


def hline(img, cam, y, col, label=None):
    d = ImageDraw.Draw(img)
    _, py = cam.S((0, y))
    for x in range(0, img.width, int(14 * RES)):
        d.line([(x, py), (x + 8 * RES, py)], fill=col + (255,), width=int(1.5 * RES))
    if label:
        d.text((8, py - 34), label, fill=col + (255,), font=paperlib.round_font(26))


# ---------------------------------------------------------------- rows
def row_turns():
    out = []
    for lab, kw in (("front", {}), ("3/4 right (turn 0.6)", dict(turn=0.6, look_x=6)),
                    ("3/4 left (turn -0.6)", dict(turn=-0.6, look_x=-6)), ("full right (turn 1)", dict(turn=1.0)),
                    ("full left (turn -1)", dict(turn=-1.0)), ("head only right (hturn 0.8)", dict(hturn=0.8, look_x=8)),
                    ("head only left (hturn -0.8)", dict(hturn=-0.8, look_x=-8))):
        out.append((lab, body_panel(pip(**kw))))
    return out


def row_moves():
    out = []
    w = pip(x=420, turn=0.6)
    w.walk(0.0, 2.0, 640)                                   # tiny steps
    n = w.walks[0][4]
    T = 2.0 / n
    for i, f in enumerate((0.5, 0.75, 1.0, 1.25)):
        tt = 2 * T + f * T
        out.append((f"walk {i + 1} ({n} steps)", body_panel(w, tt)))
    r = pip(x=380, turn=0.7)
    r.run(0.0, 1.0, 700)
    n = r.walks[0][4]
    out.append(("waddle-run", body_panel(r, 2.25 / n)))
    # wing reach with a marker: tip on the target, marker pointing right and a little up
    m = pip(x=440, turn=0.3, look_x=8, look_y=4)
    target = (600, FLOOR - 112)
    u = (0.94, -0.34)
    m.reach(0.0, 0.5, "r", RP.grip_for_tip(target, u, PIP.s), "io")
    m.set(0.0, mouth="tongue", brows="think")

    def held(img, cam, st):
        tip = RP.draw_held(img, cam, m, 1.0, "r", MARKER, RP.marker_angle(u), st)
        cross(img, cam, target)
        ring(img, cam, tip, (220, 60, 60), 4)
    out.append(("wing + marker: tip on target", body_panel(m, 1.0, cx=500, extra=held)))
    lo = pip(x=440, turn=0.3, look_x=8, look_y=6, eyes="happy", mouth="grin")
    lo.reach(0.0, 0.4, "r", (520, FLOOR - 70), "snap")
    out.append(("low wing-bump", body_panel(lo, 1.0, cx=480, extra=lambda img, cam, st: cross(img, cam, (520, FLOOR - 70)))))
    pt = pip(x=440, turn=0.4, look_x=8, look_y=-6)
    pt.point(0.0, 0.4, "r", (900, 600))
    pt.set(0.0, eyes="normal", brows="up", mouth="o")
    out.append(("point (wing)", body_panel(pt, 1.0, cx=500)))
    up = pip(x=470, turn=0.3, look_x=4, look_y=-10)
    up.reach(0.0, 0.4, "r", (580, FLOOR - 172))
    up.set(0.0, tilt=-4, mouth="smile", eyes="sparkle")
    out.append(("wing reach up", body_panel(up, 1.0, cx=510)))
    return out


def row_faces():
    out = []
    j = pip(eyes="sparkle", brows="up", mouth="grin", tuft=1.0)
    j.flap(0.0, 1.0, n=3)
    out.append(("joy (flap, tuft up)", face_panel(j, 0.5 / 3)))
    out.append(("sad", face_panel(pip(eyes="glassy", brows="sad", mouth="sad", tuft=-1.0, head_dy=8, look_y=6,
                                       look_x=-2))))
    s = pip()
    s.puff_up(0.0)
    out.append(("surprise: puff-up", face_panel(s, 0.3)))
    out.append(("unsure", face_panel(pip(eyes="normal", brows="worry", mouth="wobble", tuft=-0.5, look_x=-8,
                                          hturn=-0.25))))
    out.append(("tongue tip (copying)", face_panel(pip(eyes="normal", brows="think", mouth="tongue", look_x=6,
                                                        look_y=8, turn=0.3))))
    out.append(("eyes closed, happy", face_panel(pip(eyes="happy", brows="calm", mouth="smile", tilt=8))))
    out.append(("closed, snuggle", face_panel(pip(eyes="closed", brows="calm", mouth="smile", tilt=-10, lean=4))))
    return out


def row_tuft():
    out = []
    for lab, m in (("tuft up", 1.0), ("tuft normal", 0.0), ("tuft droop", -1.0)):
        out.append((lab, face_panel(pip(tuft=m, eyes="normal", mouth="smile" if m >= 0 else "sad",
                                         brows="up" if m > 0 else ("sad" if m < 0 else "calm")))))
    f = pip()
    f.tuft(0.0, 0.0, "flick")
    out.append(("tuft flick", face_panel(f, 0.05)))
    p = pip()
    p.puff_up(0.0, hold=0.5, out=1.0)
    out.append(("puffed up", body_panel(p, 0.4)))
    out.append(("un-puffing (half)", body_panel(p, 0.64 + 0.5)))
    d = pip(turn=0.2, eyes="happy", mouth="grin")
    d.dance(0.0, 2.0, beats=4)
    out.append(("copycat dance", body_panel(d, 0.25)))
    h = pip(eyes="normal", brows="worry", mouth="wobble", tuft=-0.5, look_x=-6)
    h.hug_self(0.0, 0.4)
    out.append(("hugs herself", body_panel(h, 1.0)))
    return out


def row_lineup():
    sn = R.Perf2(R.Puppet("snip", 1.15), seed=1, x=300, y=FLOOR, turn=0.3, eyes="normal", mouth="smile")
    cr = R.Perf2(RP.crinkle(1.2), seed=2, x=760, y=FLOOR, turn=-0.3, eyes="normal", mouth="smile")
    pp = pip(x=530, look_y=-6)
    for p in (sn, cr):
        p.blinks = []
    t = 1.0
    img, cam = canvas(80, FLOOR + 50 - 900, 920, 900)
    sn.draw(img, t, cam)
    cr.draw(img, t, cam)
    st = pp.state(t)
    pp.draw(img, t, cam, st=st)
    s_sh = sn.a.shoulder(sn.state(t), "l")[1]
    c_sh = cr.a.shoulder(cr.state(t), "l")[1]
    hc = PIP.head_centre(st)[1]
    d = ImageDraw.Draw(img)
    f = paperlib.round_font(34)
    for i, (yy, col, lab) in enumerate(((s_sh, (60, 120, 200), "Snip's shoulder"),
                                        (c_sh, (200, 110, 50), "Crinkle's shoulder"),
                                        (hc, (60, 160, 90), "Pip's head centre"))):
        hline(img, cam, yy, col)
        d.text((24, 24 + 44 * i), f"{lab}: {FLOOR - yy:.0f} above the floor", fill=col + (255,), font=f)
    out = [("Snip 1.15, Pip 0.9, Crinkle 1.2", img.resize((img.width * 2 // 3, img.height * 2 // 3), Image.LANCZOS))]
    for lab, mouth in (("Crinkle yum (right)", "yum"), ("yum_c (middle)", "yum_c"), ("yum_l (LEFT, N7)", "yum_l")):
        c = R.Perf2(RP.crinkle(1.2), seed=2, x=500, y=FLOOR, turn=-0.15, eyes="normal", brows="think", mouth=mouth,
                    look_x=-4, look_y=10)
        c.blinks = []
        st = c.state(t)
        hx, hy = c.a.face_point(st, (0, -60))
        img, cam = canvas(hx - 160, hy - 190, 320, 300)
        c.draw(img, t, cam, st=st)
        out.append((lab, img))
    return out


def sheet(path):
    rows = [("Turns (ball-projected head and body; beak pokes past the outline)", row_turns()),
            ("Waddle walk, waddle-run, wing + marker, point, reach", row_moves()),
            ("Faces (2x close-ups)", row_faces()),
            ("Tuft moods, puff-up, copycat dance, self-hug", row_tuft()),
            ("Sizes and N7", row_lineup())]
    gap, lab_h, title_h = 16, 44, 56
    width = max(sum(im.width for _, im in r) + gap * (len(r) + 1) for _, r in rows)
    height = sum(title_h + lab_h + max(im.height for _, im in r) + gap for _, r in rows) + gap
    out = Image.new("RGB", (width, height), (250, 248, 244))
    d = ImageDraw.Draw(out)
    f_title, f_lab = paperlib.round_font(40), paperlib.round_font(28)
    y = gap
    for title, r in rows:
        d.text((gap, y), title, fill=INK, font=f_title)
        y += title_h
        x = gap
        for lab, im in r:
            d.text((x + 4, y + 4), lab, fill=INK, font=f_lab)
            out.paste(im.convert("RGB"), (x, y + lab_h))
            x += im.width + gap
        y += lab_h + max(im.height for _, im in r) + gap
    out.save(path)
    print("wrote", path, out.size)


if __name__ == "__main__":
    sheet(os.path.join(ROOT, "reviews", "ep11_pip_rig.png"))
