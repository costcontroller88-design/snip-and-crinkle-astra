"""Crinkle's big pumpkin for Episode 11: every stage of it, built with hires.Cut (sharp at 2x).

    import hires; hires.set_res(2)
    import props_pumpkin as PK
    pk = PK.Pumpkin()
    spr = pk.paper(rot=0, strokes={"eye_l": 1.0, "smile": 0.4}, holes={}, lid="on")   # the paper prop
    em = pk.emissive(rot=0, lit=1.0, holes=PK.ALL_HOLES, lid="on")                    # its own light
    place(f, spr, cam.S(PK.BASE))            # graded with the scene (it is lit by the dusk)
    place(f, em, cam.S(PK.BASE), shadow=False)   # light from inside: never graded, composited after
    tip = PK.stroke_tip("smile", 0.4)        # where the marker tip is now (base-relative; add BASE)

Stages:
  * plain: ten lobes with grooves (they slide as it turns), curly stem, tendril;
  * marker strokes that grow along their paths (eyes and smile in black, the heart nose in red, two halves);
  * holes popping per shape: the unlit hollow is warm dark orange-brown with a lighter cut face along the bottom
    (never black: Ep 11 safety F5);
  * the lid line, the lid sprite (with the stem) lifted off and put back, and the opening while it is off;
  * lit: the holes glow warm yellow, brightening from the top down as the light goes down inside, plus a faint
    glow through the skin and a thin glow along the lid line (steady: no flicker);
  * rot 0 -> 180 degrees: face features sit on a ball, so they slide round, squeeze at the edge and disappear;
    at 180 we see the back (ribs, stem, tendril curling the other way, the glowing lid line).

Face design (camera side, base = (0, 0), y up is negative): round eyes r 22 at (+-48, -112); red heart nose
40 wide at (0, -84); smile crescent 140 wide, 26 thick, centre line lowest at (0, -38). Symmetric.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hires  # noqa: E402
from hires import Cut  # noqa: E402
from paperlib import Sprite, ease_out_back, mix  # noqa: E402

BASE = (960, 1505)                    # world position of the pumpkin's base centre
RX, RY = 120, 85                      # body half-size
CY = -RY                              # body centre (base-relative)
TOP = -2 * RY
LIGHT_AT = (0, -10)                   # the battery tea light sits on the bottom inside

SKIN = (246, 146, 42)
SKIN_LIGHT = (255, 178, 82)
SKIN_DARK = (214, 108, 30)
GROOVE = (182, 84, 26)
STEM = (122, 118, 58)
STEM_DARK = (96, 90, 44)
VINE = (96, 150, 70)
FLESH = (252, 204, 124)               # the cut face of the shell
HOLLOW = (174, 92, 44)                # inside, unlit: warm dark orange-brown (never black)
INK = (40, 34, 46)
INK_RED = (224, 46, 66)
LIT_IN = (255, 238, 156)              # the hollow lit from inside
LIT_EDGE = (255, 174, 64)             # the cut face lit from inside
GLOW = (255, 196, 96)

EYE_R = 22
EYES = {"eye_l": (-48, -112), "eye_r": (48, -112)}
HEART_C, HEART_W = (0, -84), 40
SMILE_W, SMILE_TIP_Y = 70, -64        # half width; tips
SMILE_LO, SMILE_HI = -25, -51         # lower and upper edge at the middle
PATTERN_C = (0, -80)                  # centre of the face pattern (for the projection)
LID_C, LID_R = (0, -152), (44, 10)    # the lid line (seen slightly from above)
ALL_HOLES = {"eye_l": 1.0, "eye_r": 1.0, "heart": 1.0, "smile": 1.0}
CANVAS, ORIGIN = (300, 290), (150, 260)


# ---------------------------------------------------------------- face shapes and marker paths
def _circle(c, r, start_deg=-90, n=48, closed=True):
    out = []
    for i in range(n + (1 if closed else 0)):
        a = math.radians(start_deg + 360 * i / n)
        out.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return out


def _heart_xy(t, size=HEART_W, c=HEART_C):
    x = 16 * math.sin(t) ** 3
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return c[0] + x * size / 32, c[1] - y * size / 32 + 2


def _smile_edge(lower, n=30):
    pts = []
    for i in range(n + 1):
        u = -1 + 2 * i / n
        x = SMILE_W * u
        if lower:
            y = SMILE_LO + (SMILE_TIP_Y - SMILE_LO) * u * u
        else:
            y = SMILE_HI + (SMILE_TIP_Y - SMILE_HI) * u * u
        pts.append((x, y))
    return pts


def smile_poly():
    lo = _smile_edge(True)
    hi = _smile_edge(False)
    tips = []
    for side in (1, -1):                                  # rounded tips
        cx, cy = side * (SMILE_W - 2), SMILE_TIP_Y - 1
        for i in range(7):
            a = math.radians(-90 + 180 * i / 6) if side > 0 else math.radians(90 + 180 * i / 6)
            tips.append((cx + 4 * math.cos(a), cy + 4 * math.sin(a)))
    return lo + tips[:7] + hi[::-1] + tips[7:]


def heart_poly(n=64):
    return [_heart_xy(2 * math.pi * i / n) for i in range(n)]


FEATURES = {"eye_l": _circle(EYES["eye_l"], EYE_R), "eye_r": _circle(EYES["eye_r"], EYE_R),
            "heart": heart_poly(), "smile": smile_poly()}
# marker paths: eyes start at the top and go round; the smile is one closed outline; the heart in two halves
PATHS = {
    "eye_l": _circle(EYES["eye_l"], EYE_R, -90, 40),
    "eye_r": _circle(EYES["eye_r"], EYE_R, -90, 40),
    "smile": _smile_edge(True) + _smile_edge(False)[::-1],
    "heart_l": [_heart_xy(2 * math.pi - math.pi * i / 32) for i in range(33)],
    "heart_r": [_heart_xy(math.pi * i / 32) for i in range(33)],
}
PATH_INK = {"eye_l": INK, "eye_r": INK, "smile": INK, "heart_l": INK_RED, "heart_r": INK_RED}


def _plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def _partial(pts, f):
    """The first fraction f of a polyline (by length), ending exactly at the tip."""
    if f >= 1:
        return list(pts)
    if f <= 0:
        return [pts[0]]
    want = _plen(pts) * f
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if want <= L:
            k = want / L if L else 0
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
            return out
        out.append(b)
        want -= L
    return out


def stroke_tip(name, f, rot=0.0):
    """Base-relative position of the marker tip on a stroke `name` at fraction f (front view unless rot)."""
    x, y = _partial(PATHS[name], max(1e-4, f))[-1]
    if rot:
        x, y, _ = wrap(x, y, rot)
    return x, y


# ---------------------------------------------------------------- the ball mapping (turning)
def wrap(x, y, rot):
    """Front-view surface point -> (x', y, facing) after turning the pumpkin by rot degrees (face slides right).
    facing = cos of the surface angle (1 = facing the camera; <= 0 = on the back, clamped to the edge)."""
    dy = (y - CY) / RY
    r = RX * math.sqrt(max(0.0, 1 - min(1.0, dy * dy)))
    if r < 1e-3 or not rot:
        return x, y, 1.0 if r >= 1e-3 else 0.0
    phi = math.asin(max(-1.0, min(1.0, x / r)))
    a = phi + math.radians(rot)
    c = math.cos(a)
    if c < 0:
        a = math.copysign(math.pi / 2, math.sin(a))
    return r * math.sin(a), y, c


def _wrap_poly(pts, rot):
    out = [wrap(x, y, rot) for x, y in pts]
    vis = max(c for _, _, c in out)
    return [(x, y) for x, y, _ in out], vis


def _shrink(pts, k, dy=0.0):
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return [(cx + (x - cx) * k, cy + (y - cy) * k + dy) for x, y in pts]


# ---------------------------------------------------------------- drawing
def _lobes(c, o, rot):
    items = []
    for k in range(10):
        a = math.radians(k * 36 + rot)
        cs, sn = math.cos(a), math.sin(a)
        if cs < -0.3:
            continue
        x = 94 * sn
        hw = 22 + 26 * max(cs, 0.0)
        ry = RY * (0.90 + 0.10 * max(cs, 0.0))
        items.append((cs, k, x, hw, ry))
    items.sort()
    for cs, k, x, hw, ry in items:
        shade = 0.5 + 0.5 * max(-1.0, cs)
        col = mix(SKIN_DARK, SKIN, min(1.0, shade * 1.15))
        cy = CY + (RY - ry)
        c.ellipse(o[0] + x, o[1] + cy, hw + 3.5, ry + 1.5, GROOVE)
        c.ellipse(o[0] + x, o[1] + cy, hw, ry, col)
        if cs > 0.55:                                     # soft highlight on the front lobes
            c.ellipse(o[0] + x - hw * 0.35, o[1] + cy - ry * 0.42, hw * 0.22, ry * 0.32,
                      mix(col, SKIN_LIGHT, 0.75), sil=False, theta=-8)


def _stem(c, o, rot, lid_off=False, lid_dy=0.0):
    k = math.cos(math.radians(rot))                       # curl direction flips as it turns
    pts = [(0, -154), (2 * k, -166), (7 * k, -176), (14 * k, -182)]       # short: the chest smile clears it
    pts = [(o[0] + x, o[1] + y + lid_dy) for x, y in pts]
    c.line(pts, 15, STEM_DARK, sil=True)
    c.line(pts[:-1], 11, STEM, sil=False)
    c.ellipse(pts[-1][0], pts[-1][1], 8, 6, STEM_DARK)
    # tendril: a curly vine from the stem base
    tp = []
    for i in range(36):
        u = i / 35
        ang = u * 3.4 * math.pi
        rr = 14 * (1 - 0.6 * u)
        x = 14 + 30 * u + rr * math.sin(ang)
        y = -160 - 8 * u - rr * (1 - math.cos(ang)) * 0.8
        tp.append((o[0] + x * k * (0.9 if k > 0 else 1.0), o[1] + y + lid_dy))
    c.line(tp, 3.6, VINE, sil=True)
    leaf_x = o[0] + 22 * k
    c.ellipse(leaf_x, o[1] - 162 + lid_dy, 13 * max(0.35, abs(k)), 8, VINE, theta=-20 * k)


def _hole(c, pts, p, sil=False):
    """A cut hole: the lit-less hollow (warm dark orange-brown) with the cut face showing along the bottom."""
    if p <= 0:
        return
    s = 0.85 + 0.15 * ease_out_back(min(1.0, p))
    a = min(1.0, p * 3)
    face = _shrink(pts, s)
    hollow = _shrink(pts, s * 0.94, dy=-3.2)
    c.polygon(face, mix(SKIN, FLESH, a), sil=False)
    c.polygon(hollow, mix(SKIN_DARK, HOLLOW, a), sil=False)


class Pumpkin:
    """Sprite factory with caches (rot is drawn in 2-degree steps)."""

    def __init__(self):
        self._paper, self._emis, self._lid = {}, {}, None

    @staticmethod
    def _key(d):
        return tuple(sorted((k, round(v, 3)) for k, v in (d or {}).items() if v > 0))

    def paper(self, rot=0.0, strokes=None, holes=None, lid="on"):
        """The pumpkin as paper. lid: 'none' (plain, no cut), 'on' (lid line), 'off' (opening, no stem)."""
        rot = round(rot / 2.0) * 2.0
        key = (rot, self._key(strokes), self._key(holes), lid)
        if key not in self._paper:
            if len(self._paper) > 400:
                self._paper.clear()
            self._paper[key] = self._draw_paper(rot, strokes or {}, holes or {}, lid)
        return self._paper[key]

    def _draw_paper(self, rot, strokes, holes, lid):
        c = Cut(*CANVAS)
        o = ORIGIN
        _lobes(c, o, rot)
        # holes (cut shapes), then marker lines that are not cut yet
        for name in ("eye_l", "eye_r", "heart", "smile"):
            p = holes.get(name, 0.0)
            if p > 0:
                pts, vis = _wrap_poly(FEATURES[name], rot)
                if vis > 0.02:
                    _hole(c, [(o[0] + x, o[1] + y) for x, y in pts], p)
        for name, f in strokes.items():
            feat = "heart" if name.startswith("heart") else name
            if holes.get(feat, 0.0) >= 0.34 or f <= 0:
                continue
            part = _partial(PATHS[name], f)
            seg_pts = []
            for x, y in part:
                wx, wy, cs = wrap(x, y, rot)
                if cs > 0.05:
                    seg_pts.append((o[0] + wx, o[1] + wy))
                elif len(seg_pts) > 1:
                    c.line(seg_pts, 5.5, PATH_INK[name])
                    seg_pts = []
                else:
                    seg_pts = []
            if len(seg_pts) > 1:
                c.line(seg_pts, 5.5, PATH_INK[name])
            elif len(seg_pts) == 1:
                x, y = seg_pts[0]
                c.ellipse(x, y, 2.8, 2.8, PATH_INK[name], sil=False)
        # top: lid line or opening, then stem
        lx, ly = o[0] + LID_C[0], o[1] + LID_C[1]
        if lid == "off":
            c.ellipse(lx, ly + 1.5, LID_R[0] + 1, LID_R[1] + 1.5, FLESH, sil=False)
            c.ellipse(lx, ly - 0.5, LID_R[0] - 3, LID_R[1] - 2.5, HOLLOW, sil=False)
        else:
            if lid == "on":
                c.arc(lx, ly, LID_R[0], LID_R[1], 0, 360, 2.4, mix(GROOVE, (90, 40, 20), 0.4))
            _stem(c, o, rot)
        return c.finish(pivot=o, border=5, shadow_alpha=0.28)

    def lid_sprite(self, rot=0.0):
        """The lid (a little dome of shell with the stem), pivot at the lid-line centre."""
        if self._lid is None:
            c = Cut(140, 110)
            o = (70, 92)
            c.ellipse(o[0], o[1] - 6, LID_R[0] + 2, 16, SKIN)
            for x in (-24, 0, 24):
                c.line([(o[0] + x * 0.8, o[1] - 20), (o[0] + x, o[1] + 4)], 2.2, GROOVE)
            c.ellipse(o[0], o[1] + 2, LID_R[0], LID_R[1] - 2, FLESH, sil=False)
            c.ellipse(o[0], o[1] + 2, LID_R[0] - 8, LID_R[1] - 5, mix(FLESH, HOLLOW, 0.3), sil=False)
            _stem(c, (o[0] - LID_C[0], o[1] - LID_C[1]), 0.0)
            self._lid = c.finish(pivot=o, border=4, shadow_alpha=0.25)
        return self._lid

    # ------------------------------------------------------------ its own light (emissive, never graded)
    def emissive(self, rot=0.0, lit=1.0, holes=None, lid="on", level=None):
        """Light from inside: lit holes (top-down by `level` 0..1, default = lit), a faint glow through the skin
        and a thin glow along the lid line. Returns a Sprite aligned with paper() (same pivot)."""
        if lit <= 0.003:
            return None
        rot = round(rot / 2.0) * 2.0
        level = lit if level is None else level
        key = (rot, round(lit, 2), round(level, 2), self._key(holes), lid)
        if key not in self._emis:
            if len(self._emis) > 300:
                self._emis.clear()
            self._emis[key] = self._draw_emissive(rot, lit, level, holes or {}, lid)
        return self._emis[key]

    def _draw_emissive(self, rot, lit, level, holes, lid):
        k = hires.RES
        ss = 2
        W, H = int(CANVAS[0] * k), int(CANVAS[1] * k)
        o = (ORIGIN[0], ORIGIN[1])

        def P(pts):
            return [((o[0] + x) * k * ss, (o[1] + y) * k * ss) for x, y in pts]
        col = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(col)
        halo = Image.new("L", (W * ss, H * ss), 0)
        hd = ImageDraw.Draw(halo)
        for name in ("eye_l", "eye_r", "heart", "smile"):
            if holes.get(name, 0.0) < 0.5:
                continue
            pts, vis = _wrap_poly(FEATURES[name], rot)
            if vis <= 0.02:
                continue
            fade = min(1.0, vis / 0.35)
            face = P(pts)
            hollow = P(_shrink(pts, 0.94, dy=-3.2))
            d.polygon(face, fill=LIT_EDGE + (int(255 * fade),))
            d.polygon(hollow, fill=LIT_IN + (int(255 * fade),))
            hd.polygon(face, fill=int(150 * fade))
        # the opening while the lid is off, or the thin line of light round the lid
        lx, ly = LID_C
        if lid == "off":
            box = [((o[0] + lx - LID_R[0] + 3) * k * ss), ((o[1] + ly - LID_R[1] + 2) * k * ss),
                   ((o[0] + lx + LID_R[0] - 3) * k * ss), ((o[1] + ly + LID_R[1] - 1) * k * ss)]
            d.ellipse(box, fill=LIT_IN + (230,))
            hd.ellipse(box, fill=160)
        elif lid == "on":
            box = [((o[0] + lx - LID_R[0]) * k * ss), ((o[1] + ly - LID_R[1]) * k * ss),
                   ((o[0] + lx + LID_R[0]) * k * ss), ((o[1] + ly + LID_R[1]) * k * ss)]
            d.arc(box, 0, 360, fill=LIT_EDGE + (150,), width=max(1, int(1.8 * k * ss)))
            hd.arc(box, 0, 360, fill=70, width=max(1, int(5 * k * ss)))
        col = col.resize((W, H), Image.LANCZOS)
        halo = halo.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(7 * k))
        out = Image.new("RGBA", (W, H), GLOW + (0,))
        out.putalpha(halo)
        out.alpha_composite(col.filter(ImageFilter.GaussianBlur(0.6 * k)))
        # a faint glow through the skin (the body silhouette)
        skin = Image.new("L", (W, H), 0)
        ImageDraw.Draw(skin).ellipse([(o[0] - RX + 8) * k, (o[1] + TOP + 10) * k, (o[0] + RX - 8) * k,
                                      (o[1] - 6) * k], fill=58)
        skin = skin.filter(ImageFilter.GaussianBlur(14 * k))
        sk = Image.new("RGBA", (W, H), (255, 170, 70, 0))
        sk.putalpha(skin)
        sk.alpha_composite(out)
        out = sk
        # top-down reveal and overall level
        ramp = Image.new("L", (1, H), 0)
        lev_y = o[1] + (-140 + 125 * level)                  # canvas design y of the light level
        for y in range(H):
            yy = y / k
            v = max(0.0, min(1.0, (lev_y - yy) / 18.0 + 0.5))
            ramp.putpixel((0, y), int(255 * v * min(1.0, lit)))
        ramp = ramp.resize((W, H))
        a = out.getchannel("A")
        from PIL import ImageChops
        out.putalpha(ImageChops.multiply(a, ramp))
        return Sprite(out, (o[0] * k, o[1] * k))


def pattern_shapes():
    """The cut face as polygons (base-relative, front view): what the light passes through."""
    return [FEATURES["eye_l"], FEATURES["eye_r"], FEATURES["heart"], FEATURES["smile"]]
