"""Rig v2: Snip and Crinkle as articulated paper puppets that feel alive.

What is new compared with characters.Character (which stays as it is for Episodes 1-10):
  * heads (and bodies) TURN: turn=-1..1 slides the face toward the side the character is facing, so
    the friends can look at each other, not only at the camera;
  * two-part arms with ELBOWS and round paws, posed by angles or by reaching for a point (IK), so
    paws can hold, give and take things, touch cheeks, hug and paw-bump for real;
  * separate FEET that WALK: planted steps, a body bob and arm swing (no more hopping everywhere);
  * built with hires.RCut at the current render scale, so close-ups stay sharp.

    import hires; hires.set_res(2)
    import rig2 as R
    snip = R.Perf2(R.Puppet("snip", 1.15), seed=1, x=300, y=FLOOR)
    snip.walk(0.5, 2.5, 760)                       # steps from x=300 to 760
    snip.to(2.5, 2.9, "io", turn=0.6)              # turn to face right
    snip.reach(3.0, 3.4, "r", (900, 1250))         # right paw reaches for a point (elbow bends)
    snip.draw(frame, t, cam, drawing)

Arm angles: degrees counter-clockwise from hanging straight down (as before); elb_* bends the forearm
relative to the upper arm. Feet stand at (x, y); everything else is in design units times the scale.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import acting as K  # noqa: E402
import hires  # noqa: E402
from acting import _brows, _eyes2, _mouth2  # noqa: E402
from characters import CRINKLE, SNIP  # noqa: E402
from hires import RCut  # noqa: E402
from paperlib import Sprite, place, rot, spiky_ellipse_pts, star_pts  # noqa: E402

TURN_Q = 0.1                          # head/body turn is drawn in steps of 0.1


def _q(v, step):
    return round(round(v / step) * step, 3)


# ---------------------------------------------------------------- heads
def snip_head(eyes, mouth, look, brows, turn, k):
    c = RCut(300, 290, k)
    c.ellipse(150, 150, 140, 122, SNIP["fur"])
    sp = 1 - 0.14 * abs(turn)
    sh = 36 * turn
    puff = mouth == "blow"
    for side in (-1, 1):
        far = side * turn < -0.05
        rx = (27 if puff else 22) * (0.72 if far else 1.0)
        c.ellipse(150 + side * 74 * sp + sh * 0.8, 186, rx, 17 if puff else 13, SNIP["cheek"], sil=False)
    pts = [(150 - 47 * sp + sh, 138), (150 + 47 * sp + sh, 138)]
    lk = (look[0] + int(round(4 * turn)), look[1])
    _eyes2(c, pts, eyes, (15, 20), lk)
    _brows(c, pts, brows, (15, 20), lk)
    c.ellipse(150 + 48 * turn, 170, 13, 9, SNIP["nose"], sil=False)
    _mouth2(c, 150 + 42 * turn, 186, mouth)
    return c.finish(pivot=(150, 260))


def crinkle_head(eyes, mouth, look, brows, turn, k):
    c = RCut(340, 330, k)
    fur = CRINKLE["fur"]
    for x in (70, 270):
        c.ellipse(x + 26 * turn, 74, 56, 56, fur)
        c.ellipse(x + 26 * turn, 78, 31, 31, CRINKLE["ear_in"], sil=False)
    c.ellipse(170, 190, 160, 128, fur)
    sp = 1 - 0.12 * abs(turn)
    c.ellipse(170 + 44 * turn, 240, 74 * (1 - 0.1 * abs(turn)), 54, CRINKLE["muzzle"], sil=False)
    puff = mouth == "blow"
    for side in (-1, 1):
        far = side * turn < -0.05
        rx = (30 if puff else 22) * (0.72 if far else 1.0)
        c.ellipse(170 + side * 92 * sp + 30 * turn, 224, rx, 19 if puff else 13, CRINKLE["cheek"], sil=False)
    pts = [(170 - 60 * sp + 38 * turn, 170), (170 + 60 * sp + 38 * turn, 170)]
    lk = (look[0] + int(round(4 * turn)), look[1])
    _eyes2(c, pts, eyes, (16, 21), lk)
    _brows(c, pts, brows, (16, 21), lk)
    c.ellipse(170 + 52 * turn, 216, 27, 18, CRINKLE["nose"], sil=False)
    c.ellipse(161 + 52 * turn, 211, 8, 4, (140, 104, 88), sil=False)
    _mouth2(c, 170 + 46 * turn, 250, mouth, 1.1)
    return c.finish(pivot=(170, 312))


def snip_ear(k):
    c = RCut(110, 290, k)
    c.ellipse(55, 145, 46, 132, SNIP["fur"])
    c.ellipse(55, 163, 24, 96, SNIP["ear_in"], sil=False)
    return c.finish(pivot=(55, 255))


def snip_frizz(k):
    c = RCut(380, 350, k)
    c.polygon(spiky_ellipse_pts(190, 175, 150, 132, 34, 20), SNIP["fur"])
    return c.finish(pivot=(190, 175))


# ---------------------------------------------------------------- bodies (feet are separate now)
def snip_body(turn, k):
    c = RCut(240, 232, k)
    c.ellipse(120, 122, 100, 106, SNIP["tee"])
    c.chord(120, 18, 42, 26, 0, 180, SNIP["fur"])
    sx = 1 - 0.22 * abs(turn)
    star = [(120 + 26 * turn + (x - 120) * sx, y) for x, y in star_pts(120, 130, 32, 14.4)]
    c.polygon(star, SNIP["star"], sil=False)
    return c.finish(pivot=(120, 20))


def crinkle_body(turn, k):
    c = RCut(290, 254, k)
    c.ellipse(145, 136, 125, 114, CRINKLE["fur"])
    c.ellipse(145 + 30 * turn, 162, 72 * (1 - 0.12 * abs(turn)), 70, CRINKLE["muzzle"], sil=False)
    c.polygon([(196, 44), (238, 44), (248, 130), (210, 134)], CRINKLE["scarf"])
    c.polygon([(214, 92), (243, 90), (245, 106), (216, 108)], CRINKLE["stripe"], sil=False)
    c.rrect(42, 12, 248, 60, 24, CRINKLE["scarf"])
    for x in (88, 136, 184):
        xs = x + 14 * turn
        c.rrect(xs, 12, xs + 18, 60, 4, CRINKLE["stripe"], sil=False)
    return c.finish(pivot=(145, 22))


def _foot(rx, ry, col, k):
    c = RCut(rx * 2 + 12, ry * 2 + 12, k)
    c.ellipse(rx + 6, ry + 6, rx, ry, col)
    return c.finish(pivot=(rx + 6, ry * 2 + 6))


# ---------------------------------------------------------------- arms (upper arm + forearm with paw)
def snip_upper(k):
    c = RCut(48, 96, k)
    c.rrect(5, 4, 43, 86, 19, SNIP["fur"])
    c.rrect(0, 0, 48, 42, 20, SNIP["tee"])
    return c.finish(pivot=(24, 20))


def snip_fore(k):
    c = RCut(46, 92, k)
    c.rrect(5, 0, 41, 66, 18, SNIP["fur"])
    c.ellipse(23, 64, 21, 20, SNIP["fur"])
    return c.finish(pivot=(23, 16))


def crinkle_upper(k):
    c = RCut(58, 106, k)
    c.rrect(4, 4, 54, 96, 25, CRINKLE["fur"])
    return c.finish(pivot=(29, 24))


def crinkle_fore(k):
    c = RCut(56, 110, k)
    c.rrect(5, 0, 51, 80, 23, CRINKLE["fur"])
    c.ellipse(28, 78, 26, 25, CRINKLE["fur"])
    c.ellipse(28, 86, 15, 11, CRINKLE["muzzle"], sil=False)
    return c.finish(pivot=(28, 22))


SPEC = {
    "snip": dict(neck=230, head_drop=9, shoulder=(92, 52), L1=50, L2=48, foot_dx=40, foot=(44, 22), shadow_w=200,
                 default=("normal", "w")),
    "crinkle": dict(neck=248, head_drop=8, shoulder=(112, 64), L1=56, L2=56, foot_dx=50, foot=(50, 22),
                    shadow_w=240, default=("normal", "smile")),
}


def _contact_shadow(w, k):
    W, H = int((w + 80) * k), int(120 * k)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([40 * k, 45 * k, (40 + w) * k, 75 * k], fill=110)
    img = Image.new("RGBA", (W, H), (55, 38, 30, 255))
    img.putalpha(m.filter(ImageFilter.GaussianBlur(9 * k)))
    return Sprite(img, (W / 2, 60 * k))


class Puppet:
    def __init__(self, kind, scale=1.0):
        self.kind, self.s = kind, scale
        self.k = scale * hires.RES
        sp = SPEC[kind]
        self.neck, self.head_drop, self.sh = sp["neck"], sp["head_drop"], sp["shoulder"]
        self.L1, self.L2, self.foot_dx = sp["L1"], sp["L2"], sp["foot_dx"]
        self._default = sp["default"]
        k = self.k
        if kind == "snip":
            self.upper, self.fore = snip_upper(k), snip_fore(k)
            self.ear, self.frizz = snip_ear(k), snip_frizz(k)
            self.foot = _foot(*sp["foot"], SNIP["fur"], k)
            self._head_fn, self._body_fn = snip_head, snip_body
        else:
            self.upper, self.fore = crinkle_upper(k), crinkle_fore(k)
            self.ear = self.frizz = None
            self.foot = _foot(*sp["foot"], CRINKLE["foot"], k)
            self._head_fn, self._body_fn = crinkle_head, crinkle_body
        self.shadow = _contact_shadow(int(sp["shadow_w"] * scale), hires.RES)
        self._heads, self._bodies = {}, {}

    # --- sprites
    def head(self, eyes, mouth, look, brows, turn):
        key = (eyes, mouth, look, brows, _q(turn, TURN_Q))
        if key not in self._heads:
            self._heads[key] = self._head_fn(eyes, mouth, look, brows, key[-1], self.k)
        return self._heads[key]

    def body(self, turn):
        key = _q(turn, 0.25)
        if key not in self._bodies:
            self._bodies[key] = self._body_fn(key, self.k)
        return self._bodies[key]

    # --- geometry (world design units)
    def anchor(self, st):
        s, lean = self.s, st["lean"]
        bx, by = st["x"], st["y"] - st["hop"]

        def P(dx, dy):
            rx, ry = rot(dx * s, dy * s, lean)
            return bx + rx, by + ry
        return P

    def shoulder(self, st, side):
        t = st["turn"]
        sx = self.sh[0] * (1 - 0.25 * abs(t)) * (-1 if side == "l" else 1) + 14 * t
        return self.anchor(st)(sx, (-self.neck + self.sh[1]) * st["sq"])

    def arm_points(self, st, side):
        """Shoulder, elbow, paw centre, and the forearm angle (incl. lean)."""
        a = (st["arm_l"] if side == "l" else st["arm_r"]) + st["lean"]
        b = st["elb_l"] if side == "l" else st["elb_r"]
        S = self.shoulder(st, side)
        ex, ey = rot(0, self.L1 * self.s, a)
        E = (S[0] + ex, S[1] + ey)
        px, py = rot(0, self.L2 * self.s, a + b)
        return S, E, (E[0] + px, E[1] + py), a + b

    def ik(self, st, side, target, bend=None):
        """(shoulder angle, elbow bend) that put this paw's centre on `target`. Elbows point outward by default."""
        bend = (1 if side == "l" else -1) if bend is None else bend
        S = self.shoulder(st, side)
        L1, L2 = self.L1 * self.s, self.L2 * self.s
        dx, dy = target[0] - S[0], target[1] - S[1]
        d = min(max(math.hypot(dx, dy), abs(L1 - L2) + 1e-3), (L1 + L2) * 0.999)
        theta = math.degrees(math.atan2(dx, dy))
        alpha = math.degrees(math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)))))
        beta = math.degrees(math.acos(max(-1, min(1, (L1 * L1 + L2 * L2 - d * d) / (2 * L1 * L2)))))
        return theta + bend * alpha - st["lean"], -bend * (180 - beta)

    def head_pivot(self, st):
        return self.anchor(st)(0, -self.neck * st["sq"] + self.head_drop + st["head_dy"])

    # --- drawing
    def _arm(self, base, cam, st, side):
        S, E, W, fa = self.arm_points(st, side)
        a = (st["arm_l"] if side == "l" else st["arm_r"]) + st["lean"]
        place(base, self.upper, cam.S(S), angle=a, alpha=st["alpha"])
        place(base, self.fore, cam.S(E), angle=fa, alpha=st["alpha"])

    def draw(self, base, cam, st, front=False):
        s, t, A = self.s, st["turn"], st["alpha"]
        place(base, self.shadow, cam.S((st["x"], st["y"] + 6)), alpha=max(0.25, 1 - st["hop"] / 160) * A,
              sx=max(0.6, 1 - st["hop"] / 300), shadow=False)
        for i, side in enumerate((-1, 1)):
            rel, lift = st["feet"][i]
            fx = st["x"] + (side * self.foot_dx * (1 - 0.3 * abs(t)) + 10 * t) * s + rel
            place(base, self.foot, cam.S((fx, st["y"] - st["hop"] - lift)), alpha=A)
        far = "r" if t > 0.35 else ("l" if t < -0.35 else None)
        if far and not front:
            self._arm(base, cam, st, far)
        P = self.anchor(st)
        neck = P(0, -self.neck * st["sq"])
        place(base, self.body(t), cam.S(neck), angle=st["lean"], alpha=A, sx=1 / math.sqrt(st["sq"]), sy=st["sq"])
        if not front:
            for side in ("l", "r"):
                if side != far:
                    self._arm(base, cam, st, side)
        hx, hy = self.head_pivot(st)
        ha = st["lean"] + st["tilt"]
        if self.ear is not None:
            if st["frizz"] > 0.01:
                cx, cy = rot(0, -110 * s, ha)
                place(base, self.frizz, cam.S((hx + cx, hy + cy)), angle=ha, scale=st["frizz"], alpha=A)
            for (ox, oy), tilt, extra in zip(((-50, -180), (50, -180)), (9, -9), (st["ear_l"], st["ear_r"])):
                ex, ey = rot((ox + 22 * t) * s, oy * s, ha)
                place(base, self.ear, cam.S((hx + ex, hy + ey)), angle=ha + tilt + extra, sy=st["ear_k"], alpha=A)
        look = (int(round(st["look_x"] / 2) * 2), int(round(st["look_y"] / 2) * 2))
        place(base, self.head(st["eyes"], st["mouth"], look, st["brows"], t), cam.S((hx, hy)), angle=ha, alpha=A)
        if front:
            for side in ("l", "r"):
                self._arm(base, cam, st, side)


# ---------------------------------------------------------------- performance
class Perf2(K.Perf):
    NUM = K.NUM + ("turn", "elb_l", "elb_r")

    def __init__(self, puppet, seed=0, **init):
        base = dict(arm_l=-10.0, arm_r=10.0, elb_l=14.0, elb_r=-14.0, turn=0.0)
        base.update(init)
        super().__init__(puppet, seed, **base)
        self.walks = []

    def walk(self, t0, t1, x1, steps=None):
        """Walk from wherever x is at t0 to x1, with planted steps."""
        x0 = self._num("x", t0)
        if steps is None:
            steps = max(2, int(round(abs(x1 - x0) / (95 * self.a.s))))
        self.to(t0, t1, "lin", x=x1)
        self.walks.append((t0, t1, x0, x1, steps))
        return self

    def reach(self, t0, t1, side, target, ease="io", bend=None):
        st = self.state(t1)
        a, b = self.a.ik(st, side, target, bend)
        if side == "l":
            return self.to(t0, t1, ease, arm_l=a, elb_l=b)
        return self.to(t0, t1, ease, arm_r=a, elb_r=b)

    def footfalls(self):
        out = []
        for t0, t1, x0, x1, n in self.walks:
            T = (t1 - t0) / n
            out += [t0 + T * (j + 1) for j in range(n)]
        return out

    def state(self, t, drawing=None):
        s = super().state(t, drawing)
        feet = [[0.0, 0.0], [0.0, 0.0]]
        for t0, t1, x0, x1, n in self.walks:
            if not t0 <= t <= t1:
                continue
            d = 1 if x1 >= x0 else -1
            T = (t1 - t0) / n
            stride = abs(x1 - x0) / n
            env = min(1.0, (t - t0) / (0.5 * T), (t1 - t) / (0.5 * T))
            ph = ((t - t0) / (2 * T)) % 1.0
            for i, off in enumerate((0.0, 0.5)):
                q = (ph + off) % 1.0
                if q < 0.5:                                  # planted: slides back as the body moves on
                    rel, lift = d * (stride / 2 - stride * q / 0.5), 0.0
                else:                                        # swinging forward
                    u = (q - 0.5) / 0.5
                    rel, lift = d * (-stride / 2 + stride * u), 16 * self.a.s * math.sin(math.pi * u)
                feet[i] = [rel * env, lift * env]
            s["hop"] += 6 * self.a.s * env * (0.5 - 0.5 * math.cos(4 * math.pi * ph))
            sw = 14 * env * math.sin(2 * math.pi * ph)
            s["arm_l"] += sw
            s["arm_r"] += sw
            s["lean"] -= 2.5 * d * env
        s["feet"] = feet
        return s

    def draw(self, base, t, cam, drawing=None, st=None):
        s = st or self.state(t, drawing)
        front = any(a <= t < b for a, b in self.arms_front)
        self.a.draw(base, cam, s, front)
        return s

    def paw(self, t, side, st=None):
        """World paw centre and forearm angle (for holding props)."""
        s = st or self.state(t)
        _, _, W, fa = self.a.arm_points(s, side)
        return W, fa
