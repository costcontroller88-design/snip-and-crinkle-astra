"""The paper-lantern pumpkin (Episode 11 transformation Short, plan 7(b) T1), built at the current render scale.

    import hires; hires.set_res(2)
    import props_lantern as PL
    lan = PL.Lantern()
    spr = lan.paper({"eye_l": PL.C_STOP, "heart_l": 1.0})   # unlit paper with marker lines (graded with the scene)
    em = lan.lit(strokes, level)                            # light from inside (never graded; composite after)
    place(f, spr, cam.S(PL.BASE)); place(f, em, cam.S(PL.BASE), shadow=False)
    tip = PL.tip_world("eye_l", 0.4)                        # world point of the marker tip on a stroke at fraction f
    PL.inside_clip(lay, cam)                                # hide what goes down through the ring (hand, tea light)

What it is: the PK (props_pumpkin) outline and size (240 x 170, base at PK.BASE) built from five lobes of thin pleated
orange paper, four soft wire ribs, a wire ring opening on top (84 wide; warm dark inside, never black) and a curl of
green paper stem with a leaf beside it (opaque paper: never glows). No holes, no cutting, no tool.

Strokes (one black marker; Lead, 8 Oct: the heart nose is black too): the PK face design. The eyes start at the
lower right (+60 deg) and go under, up the left side and over the top, so the part drawn so far reads as a "C" the
right way round; the take freezes the left eye at C_STOP (2/3 round: a C with its opening on the right, the marker
tip at its upper end, so the drawing paw sits above the eye, not over it). heart_l / heart_r and
smile are PK.PATHS.

`lit(strokes, level)`: the whole paper glows (brightest low in the middle, where the tea light sits; deeper orange at
the edges, where there is more paper on the slant; ribs as soft darker lines; faint pleats); black ink stays dark
on top; the ring glows bright. level 0..1 is the light coming down through the ring (the paper lights from the top
down, then all of it). Steady: nothing in it changes with time. Sprites are cached by (strokes, level).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hires  # noqa: E402
import props_pumpkin as PK  # noqa: E402
from paperlib import Sprite  # noqa: E402

BASE = PK.BASE
INK = PK.INK
PAPER = np.array((246, 146, 42), np.float32)
CORE = np.array((255, 240, 182), np.float32)     # lit paper right by the light
MID = np.array((255, 168, 58), np.float32)
EDGE = np.array((228, 98, 22), np.float32)       # lit paper on the slant (more paper in the way)
INK_LIT = np.array((58, 32, 26), np.float32)     # black ink with light behind it: still dark
RING_IN = np.array((128, 70, 40), np.float32)    # inside the ring, unlit: warm dark, never black
RING_LIT = np.array((255, 228, 150), np.float32)
WIRE = (92, 70, 58)
LOBES = ((-84, 36, 70), (-44, 44, 82), (0, 46, 85), (44, 44, 82), (84, 36, 70))   # (cx, rx, ry), centre y -85
RIBS = (-0.53, -0.18, 0.18, 0.53)                # wire ribs (meridians), as a fraction of the half width
RING_C, RING_R = (0, -166), (42, 8)              # base-relative
RING_WORLD = (BASE[0] + RING_C[0], BASE[1] + RING_C[1])
CANVAS, ORIGIN = (300, 290), (150, 260)
SS = 2                                            # supersampling
C_STOP = 2.0 / 3.0                                # the left eye at the take: a "C" (opening on the right)


def _eye_path(c, r, start=60.0, n=48):
    """Round from `start` (deg, screen: 0 = right, 90 = bottom): under the bottom, up the left side, over the top
    (clockwise on screen) and back to the start."""
    return [(c[0] + r * math.cos(math.radians(start + 360 * i / n)), c[1] + r * math.sin(math.radians(start + 360 * i / n)))
            for i in range(n + 1)]


PATHS = {"eye_l": _eye_path(PK.EYES["eye_l"], PK.EYE_R), "eye_r": _eye_path(PK.EYES["eye_r"], PK.EYE_R),
         "heart_l": PK.PATHS["heart_l"], "heart_r": PK.PATHS["heart_r"], "smile": PK.PATHS["smile"]}


def tip(name, f):
    """Base-relative marker tip on stroke `name` at fraction f."""
    return PK._partial(PATHS[name], max(1e-4, f))[-1]


def tip_world(name, f):
    x, y = tip(name, f)
    return BASE[0] + x, BASE[1] + y


def inside_clip(lay, cam):
    """Hide the part of a layer that has gone down into the ring (below its front rim): the paper is in front of it."""
    if lay is None:
        return
    xx = np.arange(lay.box[0], lay.box[2]) + 0.5
    yy = np.arange(lay.box[1], lay.box[3]) + 0.5
    wx = xx[None, :] / cam.res + cam.ox
    wy = yy[:, None] / cam.res + cam.oy
    dx = (wx - RING_WORLD[0]) / RING_R[0]
    rim = RING_WORLD[1] + RING_R[1] * np.sqrt(np.clip(1 - dx * dx, 0, 1))
    inside = (np.abs(dx) < 1.0) & (wy > rim)
    a = np.asarray(lay.img).astype(np.float32)
    a[..., 3] *= (1 - inside)
    lay.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


class Lantern:
    def __init__(self):
        k = hires.RES * SS
        self.k = k
        W, H = int(CANVAS[0] * k), int(CANVAS[1] * k)
        self.size = (W, H)
        x = (np.arange(W) + 0.5) / k - ORIGIN[0]
        y = (np.arange(H) + 0.5) / k - ORIGIN[1]
        X, Y = np.meshgrid(x, y)
        self.X, self.Y = X, Y
        dmin = np.full(X.shape, 9.0, np.float32)
        for cx, rx, ry in LOBES:
            dmin = np.minimum(dmin, ((X - cx) / rx) ** 2 + ((Y + 85) / ry) ** 2)
        self.sil = (dmin <= 1.0).astype(np.float32)
        self.lobe_d = dmin                                       # 0 lobe middle .. 1 groove
        self.nx, self.ny = X / 120.0, (Y + 85) / 85.0
        cosl = np.sqrt(np.clip(1 - self.ny ** 2, 0.02, 1))
        rib = np.zeros(X.shape, np.float32)
        for xr in RIBS:
            rib = np.maximum(rib, np.exp(-((X - xr * 120 * cosl) / 1.6) ** 2))
        self.rib = rib
        lat = np.arcsin(np.clip(self.ny, -1, 1)) / (math.pi / 2)
        self.pleat = (0.5 + 0.5 * np.cos(lat * math.pi * 6.5)) ** 6     # faint pleat lines
        rx, ry = RING_R
        self.ring_in = (((X - RING_C[0]) / (rx - 2)) ** 2 + ((Y - RING_C[1]) / (ry - 1.5)) ** 2 <= 1).astype(np.float32)
        rr = ((X - RING_C[0]) / rx) ** 2 + ((Y - RING_C[1]) / ry) ** 2
        self.ring_rim = np.exp(-((np.sqrt(rr) - 1.0) / 0.09) ** 2) * (rr < 1.6)
        self.alpha = np.asarray(Image.fromarray((self.sil * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(0.5 * k)), np.float32) / 255
        self._stem = self._stem_layer()
        self._cache = {}

    def _P(self, pts):
        k = self.k
        return [((ORIGIN[0] + px) * k, (ORIGIN[1] + py) * k) for px, py in pts]

    def _ink(self, strokes):
        m = Image.new("L", self.size, 0)
        d = ImageDraw.Draw(m)
        w = 5.5 * self.k
        for name, f in (strokes or {}).items():
            if f <= 0:
                continue
            pts = self._P(PK._partial(PATHS[name], f))
            if len(pts) > 1:
                d.line(pts, fill=255, width=int(w), joint="curve")
            for px, py in (pts[0], pts[-1]):
                d.ellipse([px - w / 2, py - w / 2, px + w / 2, py + w / 2], fill=255)
        return (np.asarray(m.filter(ImageFilter.GaussianBlur(0.35 * self.k)), np.float32) / 255)[..., None]

    def _stem_layer(self):
        im = Image.new("RGBA", self.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        k = self.k
        cx, cy = 24, -178
        pts = [(6, -170), (14, -176)] + [(cx + (12 - 1.1 * i) * math.cos(i * 0.55), cy + (12 - 1.1 * i) * math.sin(i * 0.55))
                                         for i in range(9)]
        d.line(self._P(pts), fill=(84, 138, 62, 255), width=int(4.2 * k), joint="curve")
        d.polygon(self._P([(-14, -172), (-40, -186), (-52, -176), (-36, -166)]), fill=(104, 160, 74, 255))
        d.line(self._P([(-14, -172), (-46, -177)]), fill=(76, 124, 56, 255), width=int(1.4 * k))
        return im

    def _finish(self, rgb, alpha):
        im = Image.fromarray(np.dstack([rgb.clip(0, 255), alpha * 255]).astype(np.uint8), "RGBA")
        im.alpha_composite(self._stem)
        W, H = self.size
        im = im.resize((W // SS, H // SS), Image.LANCZOS)
        return Sprite(im, (ORIGIN[0] * hires.RES, ORIGIN[1] * hires.RES))

    @staticmethod
    def _key(strokes):
        return tuple(sorted((k, round(v, 3)) for k, v in (strokes or {}).items() if v > 0))

    def _cached(self, key, make):
        if key not in self._cache:
            if len(self._cache) > 64:
                self._cache.clear()
            self._cache[key] = make()
        return self._cache[key]

    def paper(self, strokes=None):
        """The unlit paper lantern (graded with the scene)."""
        return self._cached(("paper", self._key(strokes)), lambda: self._paper(strokes))

    def _paper(self, strokes):
        shade = 1.0 + 0.10 * (-0.5 * self.nx - 0.8 * self.ny) - 0.20 * self.lobe_d ** 3
        rgb = PAPER[None, None, :] * shade[..., None]
        rgb *= (1 - 0.10 * self.pleat)[..., None]
        rgb *= (1 - 0.22 * self.rib)[..., None]
        ink = self._ink(strokes)
        rgb = rgb * (1 - ink) + np.array(INK, np.float32) * ink
        rgb = rgb * (1 - self.ring_in[..., None]) + RING_IN * self.ring_in[..., None]
        rim = self.ring_rim[..., None]
        rgb = rgb * (1 - rim) + np.array(WIRE, np.float32) * rim
        return self._finish(rgb, self.alpha)

    def lit(self, strokes=None, level=1.0):
        """Light from inside (never graded). level 0..1: the light coming down through the ring (top first)."""
        level = round(float(np.clip(level, 0, 1)), 3)
        return self._cached(("lit", self._key(strokes), level), lambda: self._lit(strokes, level))

    def _lit(self, strokes, level):
        nx, ny = self.nx, self.ny
        slant = np.clip(nx ** 2 + ny ** 2 * 0.9, 0, 1) ** 1.6             # 0 facing us .. 1 at the edge
        dl = (self.X / 120.0) ** 2 + ((self.Y + 22) / 78.0) ** 2           # the light sits low, in the middle
        c1 = np.exp(-dl / 0.16)[..., None]
        rgb = MID * (1 - c1) + CORE * c1
        rgb = rgb * (1 - slant[..., None] * 0.8) + EDGE * (slant[..., None] * 0.8)
        v = 1.08 + 0.26 * np.exp(-dl / 0.4)
        rgb = rgb * v[..., None]
        rgb *= (1 - 0.30 * self.rib)[..., None]
        rgb *= (1 - 0.09 * self.pleat)[..., None]
        rgb *= (1 - 0.12 * self.lobe_d ** 4)[..., None]
        ink = self._ink(strokes)
        rgb = rgb * (1 - ink) + INK_LIT * ink
        rgb = rgb * (1 - self.ring_in[..., None]) + RING_LIT * self.ring_in[..., None]
        rim = self.ring_rim[..., None]
        rgb = rgb * (1 - rim) + np.array(WIRE, np.float32) * 1.4 * rim
        a = self.alpha
        if level < 0.999:
            lev_y = -170 + 175 * level
            a = a * np.clip((lev_y - self.Y) / 30.0 + 0.5, 0, 1) * min(1.0, level * 1.6)
        return self._finish(rgb, a)
