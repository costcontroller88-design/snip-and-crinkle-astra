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

A2 acting (all off by default, so older episodes draw exactly as before; COMEDY_PLAYBOOK section 9):
    snip.acting(overlap=1.0, breath=True, ears=True, blink="soft")   # switch on ear overlap, breath + drift loop,
                                                   # Crinkle's sliding ears and lid-driven blink presets (auto blinks too)
    snip.emote(2.0, 2.3, "cross")                  # eye state: curious / cross / sad / delighted / neutral
                                                   # (eyes, upper-lid angle, lower lid, ears, tilt, look, shoulders)
    snip.to(2.0, 2.3, lid=0.4, lid_ang=20, lid_lo=0.2, lid_d=0.1)   # raw lids: closure 0..1, angle + = down-in
                                                   # (cross), - = down-out (sad); lower lid 0..1; right-lid extra
    snip.dart(3.0, 10, -2)                         # eyes jump in 2 frames; a dart of >= 10 units gets a quick blink
    snip.blink(3.5, preset="slow")                 # presets quick (3/1/2 frames) soft (4/2/3) slow (5/3/4)
    mouth="none" hides the mouth (eyes-only test).

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


# ---------------------------------------------------------------- heads (true three-quarter turn)
# Features sit on a ball: a feature at angle phi (degrees from the front) moves to x = R*sin(phi + THETA*turn)
# and is foreshortened by cos(phi + THETA*turn). Turning wraps the face around the head, narrows the far eye,
# and pushes the snout past the outline, as a real three-quarter view does.
THETA_HEAD = 36.0
THETA_BODY = 30.0
EYE = (38, 32, 44)


def _proj(cx, R, phi, turn, theta=THETA_HEAD):
    a = math.radians(phi + theta * turn)
    return cx + R * math.sin(a), math.cos(a)


def _brow1(c, x, y, kind, r, look, inner_dir):
    from acting import BROWS
    if not kind or kind == "none":
        return
    rx, ry = r
    lift, rise, arch = BROWS[kind]
    L = rx * 2.3
    cx, cy = x + look[0] * 0.35, y - ry * (1.75 + lift) + look[1] * 0.25
    d = inner_dir
    c.line([(cx - d * L / 2, cy + rise * L / 2), (cx, cy - arch * L), (cx + d * L / 2, cy - rise * L / 2)],
           ry * 0.31, EYE)


# ---------------------------------------------------------------- A2: lids, eye states, blink presets
EYE_SCALE = {"normal": (1.0, 1.0), "wide": (1.3, 1.28), "sparkle": (1.32, 1.3), "glassy": (1.18, 1.15)}
BLINK_PRESETS = {"quick": (3, 1, 2), "soft": (4, 2, 3), "slow": (5, 3, 4)}   # frames at 30 fps: close, hold, open
K.EAR_MOODS.setdefault("cross", (24, -14, 0.88))
K.EAR_MOODS.setdefault("glum", (52, -40, 0.93))
EMOTES = {   # eye state + the body that goes with it; asymmetric on purpose (playbook 9.6)
    "neutral": dict(eyes="normal", brows="calm", lid=0.0, lid_ang=0, lid_lo=0.0, lid_d=0.0, ears="up", tilt=0,
                    look=(0, 0), head_dy=0, arms=(-10, 10), sq=1.0),
    "curious": dict(eyes="wide", brows="up", lid=0.0, lid_ang=0, lid_lo=0.0, lid_d=0.2, ears="curious", tilt=11,
                    look=(7, -5), head_dy=0, arms=(-12, 12), sq=1.01),
    "cross": dict(eyes="normal", brows="none", lid=0.45, lid_ang=24, lid_lo=0.2, lid_d=0.05, ears="cross", tilt=-4,
                  look=(0, 3), head_dy=6, arms=(-4, 4), sq=0.98),
    "sad": dict(eyes="normal", brows="sad", lid=0.4, lid_ang=-26, lid_lo=0.0, lid_d=0.1, ears="glum", tilt=7,
                look=(-2, 7), head_dy=9, arms=(-3, 3), sq=0.96),
    "delighted": dict(eyes="sparkle", brows="up", lid=0.0, lid_ang=0, lid_lo=0.5, lid_d=0.0, ears="happy", tilt=-8,
                      look=(0, -3), head_dy=-5, arms=(-28, 26), sq=1.03),
}


def _on_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def _lids(c, x, y, r, kind, lid, ang, lo, side, fur):
    """Upper lid (closure 0..1, angle: + = inner end down, - = outer end down) and lower lid (0..1) cut in fur over
    one open eye at (x, y) (look already applied, so the lids follow the pupils). side -1 = the left eye."""
    sx, sy = EYE_SCALE[kind]
    rx, ry = r[0] * sx, r[1] * sy
    inner = -side
    if lid > 0.001 or abs(ang) > 0.1:
        yl = y - ry + 2 * ry * lid
        half = rx * 1.5
        dy = math.tan(math.radians(ang)) * half
        a, b = (x - inner * half, yl - dy), (x + inner * half, yl + dy)
        top = y - ry * 1.55 - abs(dy)
        c.polygon([a, b, (b[0], top), (a[0], top)], fur, sil=False)
        pts = [(a[0] + (b[0] - a[0]) * i / 40, a[1] + (b[1] - a[1]) * i / 40) for i in range(41)]
        pts = [q for q in pts if _on_ellipse(q[0], q[1], x, y, rx * 1.12, ry * 1.12)]
        if len(pts) >= 2:
            c.line(pts, rx * 0.26, EYE)
    if lo > 0.001:
        ex_, ey_ = rx * 1.1, ry * 1.1                 # clipped to the eye's own outline (never over a muzzle)
        yb = y + ey_ - 2 * ey_ * lo
        arch = [(x + u * ex_, yb + (y - yb) * u * u) for u in [i / 10 - 1 for i in range(21)]]
        rim = [(x + ex_ * math.cos(math.radians(d)), y + ey_ * math.sin(math.radians(d))) for d in range(0, 181, 10)]
        c.polygon(arch + rim, fur, sil=False)


def _features(c, cx, R, ey, phi_e, r_eye, eyes, brows, look, turn, cheek_y, phi_c, cheek_r, cheek_col, puff,
              lids=None, fur=None):
    for i, side in enumerate((-1, 1)):
        x, cs = _proj(cx, R, side * phi_c, turn)
        if cs > 0.15:
            w = 0.3 + 0.7 * cs
            rx = (cheek_r[0] + (5 if puff else 0)) * w
            c.ellipse(x, cheek_y, rx, cheek_r[1] + (4 if puff else 0), cheek_col, sil=False)
    for i, side in enumerate((-1, 1)):
        x, cs = _proj(cx, R, side * phi_e, turn)
        if cs < 0.12:
            continue
        w = 0.4 + 0.6 * cs
        lk = (look[0] * w + 4 * turn, look[1])
        kind, li = eyes, 0.0
        if lids:
            li = min(1.0, lids[0] + (lids[3] if side > 0 else 0.0))
            if eyes in EYE_SCALE and li >= 0.9:
                kind = "blink"
        _eyes2(c, [(x, ey)], kind, (r_eye[0] * w, r_eye[1]), lk)
        if lids and kind in EYE_SCALE:
            _lids(c, x + lk[0], ey + lk[1], (r_eye[0] * w, r_eye[1]), kind, li, lids[1], lids[2], side, fur)
        _brow1(c, x, ey, brows, (r_eye[0] * w, r_eye[1]), lk, 1 if side < 0 else -1)


def snip_head(eyes, mouth, look, brows, turn, k, lids=None):
    ox = 30                                            # margin for the snout poking past the outline
    c = RCut(360, 290, k)
    cx = 150 + ox
    c.ellipse(cx, 150, 140, 122, SNIP["fur"])
    if abs(turn) > 0.3:                                # cheek/snout bulge on the side the face points to
        sd = 1 if turn > 0 else -1
        u = (abs(turn) - 0.3) / 0.7
        c.ellipse(cx + sd * (122 + 12 * u), 174, 24, 24, SNIP["fur"])
    _features(c, cx, 140, 138, 19.6, (15, 20), eyes, brows, look, turn, 186, 32, (22, 13), SNIP["cheek"],
              mouth == "blow", lids, SNIP["fur"])
    nx, ncs = _proj(cx, 146, 0, turn)
    c.ellipse(nx, 170, 13 * (0.6 + 0.4 * ncs), 9, SNIP["nose"], sil=False)
    mx, mcs = _proj(cx, 138, 0, turn)
    if mouth != "none":
        _mouth2(c, mx, 186, mouth, 0.8 + 0.2 * mcs)
    return c.finish(pivot=(cx, 260))


def crinkle_head(eyes, mouth, look, brows, turn, k, lids=None, cears=None):
    ox = 40
    c = RCut(420, 330, k)
    cx = 170 + ox
    fur = CRINKLE["fur"]
    for side in (-1, 1):
        if cears is None:
            x, cs = _proj(cx, 160, side * 38.7, turn)
            y = 74
        else:                                          # A2: the ear slides along the head (+ = down and out)
            a = min(68.0, max(26.0, 38.7 + 0.45 * (cears[0] if side < 0 else -cears[1])))
            x, cs = _proj(cx, 160, side * a, turn)
            y = 190 - 148.5 * math.cos(math.radians(a))
        c.ellipse(x, y, 56, 56, fur)
        if cs > 0.2:
            c.ellipse(x + 4 * turn, y + 4, 31 * (0.5 + 0.5 * cs), 31, CRINKLE["ear_in"], sil=False)
    c.ellipse(cx, 190, 160, 128, fur)
    mzx, mcs = _proj(cx, 150, 0, turn)
    mrx = 74 * (0.55 + 0.45 * mcs)
    c.ellipse(mzx, 240, mrx, 54, CRINKLE["muzzle"], sil=abs(turn) > 0.3)
    _features(c, cx, 160, 170, 22.0, (16, 21), eyes, brows, look, turn, 224, 35, (22, 13), CRINKLE["cheek"],
              mouth == "blow", lids, fur)
    nx, ncs = _proj(cx, 165, 0, turn)
    c.ellipse(nx, 216, 27 * (0.6 + 0.4 * ncs), 18, CRINKLE["nose"], sil=False)
    c.ellipse(nx - 9 * ncs, 211, 8 * ncs, 4, (140, 104, 88), sil=False)
    mx, _ = _proj(cx, 156, 0, turn)
    if mouth != "none":
        _mouth2(c, mx, 250, mouth, 1.1 * (0.8 + 0.2 * mcs))
    return c.finish(pivot=(cx, 312))


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
    sx_c, cs = _proj(120, 100, 0, turn, THETA_BODY)
    sx = 0.5 + 0.5 * cs
    star = [(sx_c + (x - 120) * sx, y) for x, y in star_pts(120, 130, 32, 14.4)]
    c.polygon(star, SNIP["star"], sil=False)
    return c.finish(pivot=(120, 20))


def crinkle_body(turn, k):
    c = RCut(290, 254, k)
    c.ellipse(145, 136, 125, 114, CRINKLE["fur"])
    px, cs = _proj(145, 125, 0, turn, THETA_BODY)
    c.ellipse(px, 162, 72 * (0.55 + 0.45 * cs), 70, CRINKLE["muzzle"], sil=False)
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
def snip_upper(k, L1):
    c = RCut(48, 20 + L1 + 20, k)
    c.rrect(5, 4, 43, 20 + L1 + 16, 19, SNIP["fur"])
    c.rrect(0, 0, 48, 42, 20, SNIP["tee"])
    return c.finish(pivot=(24, 20))


def snip_fore(k, L2):
    c = RCut(46, 16 + L2 + 24, k)
    c.rrect(5, 0, 41, 16 + L2 + 2, 18, SNIP["fur"])
    c.ellipse(23, 16 + L2, 21, 20, SNIP["fur"])
    return c.finish(pivot=(23, 16))


def crinkle_upper(k, L1):
    c = RCut(58, 24 + L1 + 26, k)
    c.rrect(4, 4, 54, 24 + L1 + 16, 25, CRINKLE["fur"])
    return c.finish(pivot=(29, 24))


def crinkle_fore(k, L2):
    c = RCut(56, 22 + L2 + 32, k)
    c.rrect(5, 0, 51, 22 + L2 + 2, 23, CRINKLE["fur"])
    c.ellipse(28, 22 + L2, 26, 25, CRINKLE["fur"])
    c.ellipse(28, 22 + L2 + 8, 15, 11, CRINKLE["muzzle"], sil=False)
    return c.finish(pivot=(28, 22))


SPEC = {
    "snip": dict(neck=230, head_drop=9, shoulder=(92, 44), L1=60, L2=58, foot_dx=40, foot=(44, 22), shadow_w=200,
                 default=("normal", "w")),
    "crinkle": dict(neck=248, head_drop=8, shoulder=(112, 56), L1=66, L2=64, foot_dx=50, foot=(50, 22),
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
            self.upper, self.fore = snip_upper(k, self.L1), snip_fore(k, self.L2)
            self.ear, self.frizz = snip_ear(k), snip_frizz(k)
            self.foot = _foot(*sp["foot"], SNIP["fur"], k)
            self._head_fn, self._body_fn = snip_head, snip_body
        else:
            self.upper, self.fore = crinkle_upper(k, self.L1), crinkle_fore(k, self.L2)
            self.ear = self.frizz = None
            self.foot = _foot(*sp["foot"], CRINKLE["foot"], k)
            self._head_fn, self._body_fn = crinkle_head, crinkle_body
        self.shadow = _contact_shadow(int(sp["shadow_w"] * scale), hires.RES)
        self._heads, self._bodies = {}, {}

    # --- sprites
    def head(self, eyes, mouth, look, brows, turn, lids=None, cears=None):
        tq = _q(turn, TURN_Q)
        kw = {}
        if lids:
            kw["lids"] = lids
        if cears is not None and self.kind == "crinkle":
            kw["cears"] = cears
        key = (eyes, mouth, look, brows, tq) + ((tuple(sorted(kw.items())),) if kw else ())
        if key not in self._heads:
            self._heads[key] = self._head_fn(eyes, mouth, look, brows, tq, self.k, **kw)
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
        R = self.sh[0] / math.sin(math.radians(70))
        sx, _ = _proj(0, R, -70 if side == "l" else 70, st["turn"], THETA_BODY)
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

    def face_point(self, st, local):
        """World position of a point on the face, given in head-local design units (x from the face centre,
        y from the head pivot), following turn, tilt and lean (e.g. the nose, for a paint dot)."""
        t = max(-1.0, min(1.0, st["turn"] + st.get("hturn", 0.0)))
        R = 146 if self.kind == "snip" else 165
        x = R * math.sin(math.radians(THETA_HEAD * t)) + local[0]
        hx, hy = self.head_pivot(st)
        dx, dy = rot(x * self.s, local[1] * self.s, st["lean"] + st["tilt"])
        return hx + dx, hy + dy

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
            fdx, _ = _proj(0, self.foot_dx / 0.5, side * 30, t, THETA_BODY)
            fx = st["x"] + fdx * s + rel
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
        t = max(-1.0, min(1.0, st["turn"] + st.get("hturn", 0.0)))   # the head can look away from the body
        if self.ear is not None:
            if st["frizz"] > 0.01:
                cx, cy = rot(0, -110 * s, ha)
                place(base, self.frizz, cam.S((hx + cx, hy + cy)), angle=ha, scale=st["frizz"], alpha=A)
            for (ox, oy), tilt, extra in zip(((-50, -180), (50, -180)), (9, -9), (st["ear_l"], st["ear_r"])):
                px, _ = _proj(0, 115, math.degrees(math.asin(ox / 115)), t)
                ex, ey = rot(px * s, oy * s, ha)
                place(base, self.ear, cam.S((hx + ex, hy + ey)), angle=ha + tilt + extra, sy=st["ear_k"], alpha=A)
        look = (int(round(st["look_x"] / 2) * 2), int(round(st["look_y"] / 2) * 2))
        place(base, self.head(st["eyes"], st["mouth"], look, st["brows"], t, st.get("lids"), st.get("cears")),
              cam.S((hx, hy)), angle=ha, alpha=A)
        if front:
            for side in ("l", "r"):
                self._arm(base, cam, st, side)


# ---------------------------------------------------------------- performance
class Perf2(K.Perf):
    NUM = K.NUM + ("turn", "hturn", "elb_l", "elb_r", "lid", "lid_ang", "lid_lo", "lid_d")

    def __init__(self, puppet, seed=0, **init):
        base = dict(arm_l=-10.0, arm_r=10.0, elb_l=14.0, elb_r=-14.0, turn=0.0, hturn=0.0,
                    lid=0.0, lid_ang=0.0, lid_lo=0.0, lid_d=0.0)
        base.update(init)
        super().__init__(puppet, seed, **base)
        self.walks = []
        self.a2 = None                 # A2 acting switches (see acting()); None = the old rig, unchanged
        self.pblinks = []              # (start, preset) lid-driven blinks

    # --- A2 acting
    def acting(self, overlap=1.0, breath=True, ears=True, blink="soft", auto_blink=True):
        """Switch on the A2 rig: ear overlap (spring lag on head angle, hop and squash), a breath + drift loop for
        moving holds, Crinkle's sliding ears (ear_l/ear_r and ear moods), and blink presets (auto blinks too, unless
        auto_blink=False: then blink only where you call blink() or dart())."""
        self.a2 = dict(overlap=overlap, breath=breath, ears=ears, blink=blink)
        if blink:
            if auto_blink:
                self.pblinks += [(b, blink) for b in self.blinks]
            self.blinks = []
        return self

    def blink(self, *times, preset=None):
        p = preset or (self.a2 and self.a2["blink"])
        if not p:
            return super().blink(*times)
        self.pblinks += [(round(b * K.DPS) / K.DPS, p) for b in times]   # start on a drawing: the closed one shows
        return self

    def dart(self, t, look_x, look_y, frames=2, blink=None):
        """Eye dart (playbook 9.4): the eyes jump in `frames` frames; a dart of >= 10 units gets a quick blink."""
        x0, y0 = self._num("look_x", t), self._num("look_y", t)
        self.to(t, t + frames / K.FPS, "out", look_x=look_x, look_y=look_y)
        if blink or (blink is None and math.hypot(look_x - x0, look_y - y0) >= 10):
            self.blink(t, preset="quick")
        return self

    def emote(self, t0, t1, name, ease="io", body=True):
        """Eye state with its body (EMOTES): eyes + brows switch at t0, lids/ears/tilt/look ease to t1."""
        e = EMOTES[name]
        self.face(t0, eyes=e["eyes"], brows=e["brows"])
        self.to(t0, t1, ease, lid=e["lid"], lid_ang=e["lid_ang"], lid_lo=e["lid_lo"], lid_d=e["lid_d"])
        self.ears(t0, t1, e["ears"])
        if body:
            self.to(t0, t1, ease, tilt=e["tilt"], look_x=e["look"][0], look_y=e["look"][1], head_dy=e["head_dy"],
                    arm_l=e["arms"][0], arm_r=e["arms"][1], sq=e["sq"])
        return self

    def _drive(self, t):
        h = self._num("hop", t) + self.a.neck * self.a.s * (self._num("sq", t) - 1)
        for t0, t1, n, hgt in self.hops:
            if t0 <= t < t1:
                h += hgt * math.sin(math.pi * (((t - t0) / (t1 - t0) * n) % 1.0))
        return self._num("lean", t) + self._num("tilt", t), h

    def _ear_lag(self, t, win=0.8, dt=1 / 120):
        """Follow-through: a damped spring chases the head angle and height; returns (angle lag, height lag)."""
        w, z = 2 * math.pi * 2.6, 0.3
        n = int(win / dt)
        a, h = self._drive(t - win)
        xa, xh, va, vh = a, h, 0.0, 0.0
        for i in range(1, n + 1):
            a, h = self._drive(t - win + i * dt)
            va += (-w * w * (xa - a) - 2 * z * w * va) * dt
            vh += (-w * w * (xh - h) - 2 * z * w * vh) * dt
            xa += va * dt
            xh += vh * dt
        return xa - a, xh - h

    def _blink_lid(self, t):
        v = 0.0
        if any(a <= t < b for a, b in self.no_blink):
            return v
        for b, p in self.pblinks:
            c, h, o = BLINK_PRESETS[p]
            u = round((t - b) * K.FPS, 4)
            if 0 <= u < c:
                v = max(v, u / c)
            elif c <= u <= c + h:
                v = 1.0
            elif c + h < u < c + h + o:
                v = max(v, 1 - (u - c - h) / o)
        return v

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
        if self.a2:
            A2 = self.a2
            if A2["breath"]:                                 # moving hold: chest + shoulders breathe, head drifts
                b = math.sin(2 * math.pi * t / 2.8 + self.seed)
                s["sq"] *= 1 + 0.01 * b
                s["arm_l"] -= 1.6 * b
                s["arm_r"] += 1.6 * b
                s["head_dy"] -= 1.5 * self.a.s * b
                s["tilt"] += 1.2 * math.sin(2 * math.pi * t / 5.3 + 2 * self.seed)
            if A2["overlap"]:
                g = A2["overlap"]
                la, lh = self._ear_lag(t)
                splay = max(-5.0, min(22.0, -0.6 * lh))     # rising: tips drag outward; never cross inward
                s["ear_l"] += g * (1.3 * la + splay)
                s["ear_r"] += g * (1.3 * la - splay)
                s["ear_k"] = max(0.8, min(1.25, s["ear_k"] + g * 0.004 * lh))
            if A2["ears"] and self.a.kind == "crinkle":
                s["cears"] = (_q(s["ear_l"], 4), _q(s["ear_r"], 4))
        lid = s["lid"]
        bl = self._blink_lid(t) if self.pblinks else 0.0
        lid = lid + (1 - lid) * bl
        vals = (_q(lid, 0.1), _q(s["lid_ang"], 5.0), _q(s["lid_lo"], 0.1), _q(s["lid_d"], 0.1))
        s["lids"] = vals if any(abs(v) > 1e-9 for v in vals) else None
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
