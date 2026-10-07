"""Episode 11 transformation Short (plan section 7(b)): gate 1b storyboard stage.

A standalone vertical mini-story on the Episode 11 porch, early-evening light all through. This file holds, for now:
  * Lantern: the paper-lantern pumpkin (plan T1, rough): PK outline (240 x 170) built from five lobes, thin
    pleated paper, wire ribs, a wire ring on top (warm dark inside, never black), a green paper stem curl;
    marker strokes on PK.PATHS; `paper(strokes)` (graded with the scene) and `lit(strokes, level)` (light from
    inside: the paper itself glows, brightest low and in the middle, deeper orange at the edges, ribs darker,
    black ink stays dark, red ink glows deep red, the ring glows bright; steady).
  * the vertical cameras A / B / K of plan b4 (world boxes) and `frame(t)` for the b10 storyboard poses.

Run:  python3 episodes/ep11_short_transform.py --proto        (the lit frame alone -> build/sb1/proto_glow.png)
      python3 episodes/ep11_short_transform.py --storyboard   (b10 frames -> build/sb1/storyboard.png)
      python3 episodes/ep11_short_transform.py --still T      (one storyboard time -> build/sb1/still_T.png)
The full timeline (T3), render_world/make_buses, sound and the render come after gate 1b.
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
from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

import acting as K  # noqa: E402
import ep11_light as L  # noqa: E402
import props_porch as P  # noqa: E402
import props_pumpkin as PK  # noqa: E402
import rig2 as R  # noqa: E402
import rig2_pip as RP  # noqa: E402
from paperlib import Sprite, place  # noqa: E402

RES = hires.RES
OUT = os.path.join(ROOT, "build", "sb1")
FLOOR = P.FLOOR_Y
CAM = K.Cam("vert", P.WORLD_W, P.WORLD_H, P.LAND_Y0, P.VERT_X0, res=RES)
T_LIGHT = 95.0                         # the episode's early-evening light state (before its own glow)
BASE = PK.BASE
GLOW_C = (BASE[0], BASE[1] - 75)
DUSK_SET = (0.62, 0.62, 0.74)          # rough early-evening dimming of the set (the episode's dusk() is local to it)
DUSK_CHAR = (0.80, 0.79, 0.88)         # characters keep more of their colour


def warm(lay, glow, r=300.0, gain=0.85):
    """The lantern's warm light on a layer, by distance (as ep11_light.grade_layer, without its grade)."""
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

# ---------------------------------------------------------------- the paper lantern (T1, rough)
PAPER = np.array((246, 146, 42), np.float32)
CORE = np.array((255, 240, 182), np.float32)     # lit paper right by the light
MID = np.array((255, 168, 58), np.float32)
EDGE = np.array((228, 98, 22), np.float32)       # lit paper on the slant (more paper in the way)
INK_LIT = np.array((58, 32, 26), np.float32)     # black ink with light behind it: still dark
RED_LIT = np.array((236, 44, 40), np.float32)    # red ink passes red light
RING_IN = np.array((128, 70, 40), np.float32)    # inside the ring, unlit: warm dark, never black
RING_LIT = np.array((255, 228, 150), np.float32)
WIRE = (92, 70, 58)
LOBES = ((-84, 36, 70), (-44, 44, 82), (0, 46, 85), (44, 44, 82), (84, 36, 70))   # (cx, rx, ry), centre y -85
RIBS = (-0.53, -0.18, 0.18, 0.53)                # wire ribs (meridians), as a fraction of the half width
RING_C, RING_R = (0, -166), (42, 8)
CANVAS, ORIGIN = (300, 290), (150, 260)
SS = 2                                            # supersampling


class Lantern:
    def __init__(self):
        k = RES * SS
        self.k = k
        W, H = int(CANVAS[0] * k), int(CANVAS[1] * k)
        self.size = (W, H)
        x = (np.arange(W) + 0.5) / k - ORIGIN[0]
        y = (np.arange(H) + 0.5) / k - ORIGIN[1]
        X, Y = np.meshgrid(x, y)
        self.X, self.Y = X, Y
        dmin = np.full(X.shape, 9.0, np.float32)
        for cx, rx, ry in LOBES:
            d = ((X - cx) / rx) ** 2 + ((Y + 85) / ry) ** 2
            dmin = np.minimum(dmin, d)
        self.sil = (dmin <= 1.0).astype(np.float32)
        self.lobe_d = dmin                                       # 0 lobe middle .. 1 groove
        nx, ny = X / 120.0, (Y + 85) / 85.0
        self.nx, self.ny = nx, ny
        cosl = np.sqrt(np.clip(1 - ny ** 2, 0.02, 1))
        rib = np.zeros(X.shape, np.float32)
        for xr in RIBS:
            rib = np.maximum(rib, np.exp(-((X - xr * 120 * cosl) / 1.6) ** 2))
        self.rib = rib
        lat = np.arcsin(np.clip(ny, -1, 1)) / (math.pi / 2)        # -1 top .. 1 bottom, ball latitude
        self.pleat = (0.5 + 0.5 * np.cos(lat * math.pi * 6.5)) ** 6     # faint pleat lines
        rx, ry = RING_R
        self.ring_in = (((X - RING_C[0]) / (rx - 2)) ** 2 + ((Y - RING_C[1]) / (ry - 1.5)) ** 2 <= 1).astype(np.float32)
        rr = ((X - RING_C[0]) / rx) ** 2 + ((Y - RING_C[1]) / ry) ** 2
        self.ring_rim = np.exp(-((np.sqrt(rr) - 1.0) / 0.09) ** 2) * (rr < 1.6)
        self._stem = self._stem_layer()

    def _P(self, pts):
        k = self.k
        return [((ORIGIN[0] + px) * k, (ORIGIN[1] + py) * k) for px, py in pts]

    def _ink(self, strokes):
        """Two masks (black, red) of the marker strokes drawn so far (float 0..1)."""
        out = {}
        for ink in ("black", "red"):
            m = Image.new("L", self.size, 0)
            d = ImageDraw.Draw(m)
            w = 5.5 * self.k
            for name, f in (strokes or {}).items():
                if f <= 0 or (PK.PATH_INK[name] == PK.INK) != (ink == "black"):
                    continue
                pts = self._P(PK._partial(PK.PATHS[name], f))
                if len(pts) > 1:
                    d.line(pts, fill=255, width=int(w), joint="curve")
                for px, py in (pts[0], pts[-1]):
                    d.ellipse([px - w / 2, py - w / 2, px + w / 2, py + w / 2], fill=255)
            out[ink] = np.asarray(m.filter(ImageFilter.GaussianBlur(0.35 * self.k)), np.float32) / 255
        return out

    def _stem_layer(self):
        """A curl of green paper and a little leaf beside the ring (opaque paper: never glows)."""
        im = Image.new("RGBA", self.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        k = self.k
        cx, cy = 24, -178
        pts = [(cx + (12 - 1.1 * i) * math.cos(i * 0.55), cy + (12 - 1.1 * i) * math.sin(i * 0.55)) for i in range(9)]
        pts = [(6, -170), (14, -176)] + pts
        d.line(self._P(pts), fill=(84, 138, 62, 255), width=int(4.2 * k), joint="curve")
        leaf = [(-14, -172), (-40, -186), (-52, -176), (-36, -166)]
        d.polygon(self._P(leaf), fill=(104, 160, 74, 255))
        d.line(self._P([(-14, -172), (-46, -177)]), fill=(76, 124, 56, 255), width=int(1.4 * k))
        return im

    def _finish(self, rgb, alpha, shadow):
        rgba = np.dstack([rgb.clip(0, 255), alpha * 255]).astype(np.uint8)
        im = Image.fromarray(rgba, "RGBA")
        im.alpha_composite(self._stem)
        W, H = self.size
        im = im.resize((W // SS, H // SS), Image.LANCZOS)
        return Sprite(im, (ORIGIN[0] * RES, ORIGIN[1] * RES))

    def _alpha(self):
        a = np.maximum(self.sil, self.ring_rim * 0)
        return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5 * self.k)),
                          np.float32) / 255

    def paper(self, strokes=None):
        """The unlit paper lantern (graded with the scene)."""
        nx, ny = self.nx, self.ny
        shade = 1.0 + 0.10 * (-0.5 * nx - 0.8 * ny) - 0.20 * self.lobe_d ** 3
        rgb = PAPER[None, None, :] * shade[..., None]
        rgb *= (1 - 0.10 * self.pleat)[..., None]
        rgb *= (1 - 0.22 * self.rib)[..., None]
        ink = self._ink(strokes)
        rgb = rgb * (1 - ink["black"][..., None]) + np.array(PK.INK, np.float32) * ink["black"][..., None]
        rgb = rgb * (1 - ink["red"][..., None]) + np.array(PK.INK_RED, np.float32) * ink["red"][..., None]
        rgb = rgb * (1 - self.ring_in[..., None]) + RING_IN * self.ring_in[..., None]
        rim = self.ring_rim[..., None]
        rgb = rgb * (1 - rim) + np.array(WIRE, np.float32) * rim
        return self._finish(rgb, self._alpha(), True)

    def lit(self, strokes=None, level=1.0):
        """Light from inside (never graded). level 0..1: the light coming down through the ring (top first)."""
        nx, ny = self.nx, self.ny
        r2 = np.clip(nx ** 2 + ny ** 2 * 0.9, 0, 1)
        slant = r2 ** 1.6                                            # 0 facing us .. 1 at the edge
        dl = (self.X / 120.0) ** 2 + ((self.Y + 22) / 78.0) ** 2         # the light sits low, in the middle
        c1 = np.exp(-dl / 0.16)[..., None]
        rgb = MID * (1 - c1) + CORE * c1
        rgb = rgb * (1 - slant[..., None] * 0.8) + EDGE * (slant[..., None] * 0.8)
        v = 1.08 + 0.26 * np.exp(-dl / 0.4)
        rgb = rgb * v[..., None]
        rgb *= (1 - 0.30 * self.rib)[..., None]                     # wire ribs: soft darker lines
        rgb *= (1 - 0.09 * self.pleat)[..., None]
        rgb *= (1 - 0.12 * self.lobe_d ** 4)[..., None]
        ink = self._ink(strokes)
        rgb = rgb * (1 - ink["black"][..., None]) + INK_LIT * ink["black"][..., None]
        red = RED_LIT * (0.55 + 0.45 * v)[..., None]
        rgb = rgb * (1 - ink["red"][..., None]) + red * ink["red"][..., None]
        rgb = rgb * (1 - self.ring_in[..., None]) + RING_LIT * self.ring_in[..., None]
        rim = self.ring_rim[..., None]
        rgb = rgb * (1 - rim) + np.array(WIRE, np.float32) * 1.4 * rim
        a = self._alpha()
        if level < 0.999:                                           # top-down: the light is still coming in
            lev_y = -170 + 175 * level
            ramp = np.clip((lev_y - self.Y) / 30.0 + 0.5, 0, 1) * min(1.0, level * 1.6)
            a = a * ramp
        return self._finish(rgb, a, False)


LANTERN = Lantern()

# ---------------------------------------------------------------- cameras (plan b4), world boxes
CAMS = {"A": ((880, 1250), 1.7), "B": ((950, 1320), 2.0), "K": ((1060, 1180), 1.9),
        "B2": ((920, 1270), 1.8)}   # shot 2: B loosened so the drooping ears stay in frame (Lead, sb1)


def film(f, which):
    (cx, cy), z = CAMS[which]
    w, h = 1080 / z, 1920 / z
    box = [(cx - w / 2 - CAM.ox) * RES, (cy - h / 2 - CAM.oy) * RES, (cx + w / 2 - CAM.ox) * RES,
           (cy + h / 2 - CAM.oy) * RES]
    return f.convert("RGB").resize((1080, 1920), Image.LANCZOS, box=box)


# ---------------------------------------------------------------- storyboard poses (plan b10)
MK = RP.marker_sprite(body=(96, 170, 236), ink=PK.INK, scale=1.1)
MK_S = 1.1


def _tip(name, f):
    x, y = PK.stroke_tip(name, f)
    return BASE[0] + x, BASE[1] + y


def _unit(dx, dy):
    n = math.hypot(dx, dy)
    return dx / n, dy / n


def _perfs(sn, cr, pip):
    """Build the three performers from static pose dicts (no blinks, held poses)."""
    out = []
    for kind, p in (("sn", sn), ("cr", cr), ("pip", pip)):
        p = dict(p)
        reach = p.pop("reach", None)
        back = p.pop("back", False)
        ears = p.pop("ears", None)
        if ears:
            el, er, ek = K.EAR_MOODS[ears]
            p.update(ear_l=el, ear_r=er, ear_k=ek)
        if kind == "sn":
            perf = R.Perf2(R.Puppet("snip", 1.15), seed=1, y=FLOOR, **p)
        elif kind == "cr":
            perf = R.Perf2(RP.crinkle(1.2), seed=2, y=FLOOR, **p)
        else:
            perf = RP.PipPerf(RP.PipPuppet(0.9), seed=3, y=FLOOR, **p)
        perf.blinks = []
        if reach:
            side, target = reach
            perf.reach(0.0, 0.01, side, target)
        out.append((kind, perf, back, reach))
    return out


def poses(t):
    """Pose dicts and the marker (holder, tip or None, direction) for each b10 time."""
    eye = lambda f: {"eye_l": f}                                     # noqa: E731
    u_sn = _unit(0.42, 1.0)                                          # Snip draws from up-left
    if t < 1.0:
        tip = _tip("eye_l", 0.2)
        g = RP.grip_for_tip(tip, u_sn, MK_S)
        return dict(cam="A", strokes=eye(0.2), lit=0.0,
                    sn=dict(x=790, turn=0.5, eyes="open", mouth="smile", brows="think", look_x=4, look_y=4,
                            reach=("r", g)),
                    cr=dict(x=1080, turn=-0.5, eyes="sparkle", mouth="smile_open", brows="up", hop=8, look_x=-6,
                            look_y=4, arm_l=150, elb_l=-110, arm_r=-150, elb_r=110),
                    pip=dict(x=640, turn=0.3, eyes="open", mouth="smile", lean=3, back=True, arm_l=25, arm_r=-25),
                    marker=("sn", tip, u_sn))
    if t < 2.0:
        g_sn = RP.grip_for_tip(_tip("eye_l", 0.5), u_sn, MK_S)
        held = (1006, 1298)
        return dict(cam="A", strokes=eye(0.5), lit=0.0,
                    sn=dict(x=790, turn=0.5, eyes="open", mouth="oo", brows="up", look_x=4, look_y=2,
                            reach=("r", (g_sn[0] - 4, g_sn[1] - 4))),
                    cr=dict(x=1080, turn=-0.5, eyes="sparkle", mouth="smile_open", brows="up", lean=-10, sq=0.92,
                            look_x=-6, look_y=6, reach=("l", held), arm_r=-40, elb_r=60),
                    pip=dict(x=640, turn=0.3, eyes="open", mouth="smile", lean=-2, back=True, arm_l=25, arm_r=-25),
                    marker=("cr", None, _unit(0.25, 1.0)))
    if t < 4.0:
        g_sn = RP.grip_for_tip(_tip("eye_l", 0.5), u_sn, MK_S)
        u_cr = _unit(-0.4, 1.0)
        tip = (1018, 1418)                                           # 20 short of the smile's right end
        return dict(cam="B2", strokes=eye(0.5), lit=0.0,
                    sn=dict(x=790, turn=0.5, eyes="glassy", mouth="frown", brows="sad", ears="droop", look_x=5,
                            look_y=6, head_dy=4, reach=("r", (g_sn[0] - 14, g_sn[1] - 10))),
                    cr=dict(x=1080, turn=-0.5, eyes="open", mouth="yum_l", brows="think", lean=-8, sq=0.94,
                            look_x=-7, look_y=2, reach=("l", RP.grip_for_tip(tip, u_cr, MK_S))),
                    pip=dict(x=640, turn=0.3, back=True, arm_l=25, arm_r=-25),
                    marker=("cr", tip, u_cr))
    if t < 5.0:
        tip = _tip("eye_l", 0.5)
        g = RP.grip_for_tip(tip, u_sn, MK_S)
        return dict(cam="B2", strokes=eye(0.5), lit=0.0,
                    sn=dict(x=790, turn=0.5, eyes="glassy", mouth="frown", brows="sad", ears="droop", look_x=4,
                            look_y=6, head_dy=4, reach=("r", g)),
                    cr=dict(x=1080, turn=-0.5, eyes="open", mouth="oo", brows="sorry", lean=-6, sq=0.95, head_dy=5,
                            look_x=-6, look_y=3, reach=("l", (g[0] + 46, g[1] - 22))),
                    pip=dict(x=640, turn=0.3, back=True, arm_l=25, arm_r=-25),
                    marker=("sn", tip, u_sn))
    if t < 10.0:
        tip = _tip("eye_l", 0.5)
        g = RP.grip_for_tip((tip[0] - 6, tip[1] - 14), u_sn, MK_S)
        return dict(cam="A", strokes=eye(0.5), lit=0.0,
                    sn=dict(x=790, turn=0.5, hturn=0.3, eyes="happy", mouth="smile", brows="calm", ears="happy",
                            look_x=6, reach=("r", g)),
                    cr=dict(x=1100, turn=-0.35, eyes="happy", mouth="smile", lean=6, back=True, arm_l=28, arm_r=-28,
                            look_x=-6),
                    pip=dict(x=640, turn=0.35, eyes="happy", mouth="smile", lean=4, back=True, arm_l=25, arm_r=-25,
                             look_x=6),
                    marker=("sn", None, u_sn))
    face = {"eye_l": 1.0, "eye_r": 1.0, "heart_l": 1.0, "heart_r": 1.0}
    if t < 18.0:
        hand = (932, 1322)                                           # right of Pip's face, over the ring
        return dict(cam="A", strokes=face, lit=0.0,
                    sn=dict(x=700, turn=0.35, eyes="happy", mouth="smile", ears="happy", look_x=6, look_y=2),
                    cr=dict(x=1100, turn=-0.5, eyes="sparkle", mouth="smile_open", brows="up", lean=-10, sq=0.9,
                            look_x=-7, look_y=4, reach=("l", (hand[0] + 22, hand[1] - 22))),
                    pip=dict(x=830, turn=0.5, eyes="happy", mouth="smile_open", look_x=6, look_y=-6,
                             reach=("r", (hand[0] - 14, hand[1] + 14))),
                    marker=("pip", None, _unit(0.35, -1.0)))
    if t < 22.0:
        f = 0.45
        tip = _tip("smile", f)
        u_cr = _unit(-0.45, 1.0)
        return dict(cam="B", strokes=dict(face, smile=f), lit=0.0,
                    sn=dict(x=700, turn=0.35, eyes="happy", mouth="smile", ears="happy", look_x=6, look_y=6),
                    cr=dict(x=1085, turn=-0.5, eyes="open", mouth="yum_l", brows="think", lean=-12, sq=0.88,
                            look_x=-8, look_y=8, reach=("l", RP.grip_for_tip(tip, u_cr, MK_S))),
                    pip=dict(x=820, turn=0.35, eyes="happy", mouth="yum", look_x=6, look_y=6),
                    marker=("cr", tip, u_cr))
    full = dict(face, smile=1.0)
    return dict(cam="B", strokes=full, lit=1.0,
                sn=dict(x=700, turn=0.35, eyes="sparkle", mouth="smile_open", brows="up", ears="perk", look_x=6,
                        look_y=6, arm_l=-30, arm_r=40, elb_r=-60),
                cr=dict(x=1100, turn=-0.35, eyes="sparkle", mouth="smile_open", brows="up", look_x=-6, look_y=6,
                        arm_l=150, elb_l=-110, arm_r=-150, elb_r=110),
                pip=dict(x=820, turn=0.35, eyes="sparkle", mouth="smile_open", look_x=6, look_y=6),
                marker=None)


def _draw_puppet(perf, im, st, back):
    if not back:
        perf.draw(im, 0.5, CAM, st=st)
        return
    for side in ("l", "r"):                                         # paws/wings behind the back (T2, rough)
        perf.a._arm(im, CAM, st, side)
    perf.a._arm = lambda *a, **k: None
    try:
        perf.draw(im, 0.5, CAM, st=st)
    finally:
        del perf.a._arm


def _marker_place(im, perf, st, side, tip, u):
    W, fa = perf.paw(0.5, side, st)
    if tip is not None:
        ang = math.degrees(math.atan2(tip[0] - W[0], tip[1] - W[1]))
    else:
        ang = RP.marker_angle(u)
    if hasattr(perf.a, "grip"):
        RP.draw_held(im, CAM, perf, 0.5, side, MK, ang, st=st)
    else:
        place(im, MK, CAM.S(W), angle=ang)


def frame(t):
    """The b10 storyboard frame at time t: (vertical frame 1080x1920, camera letter)."""
    p = poses(t)
    glow = p["lit"]
    f = dusk(frame.world.background(T_LIGHT), DUSK_SET)
    size = f.size
    L.floor_pool(f, CAM, frame.world.albedo, glow, 1.0)
    perfs = _perfs(p["sn"], p["cr"], p["pip"])
    sts = {k: perf.state(0.5) for k, perf, _, _ in perfs}
    holder = p["marker"][0] if p["marker"] else None
    over = []
    for kind, perf, back, reach in perfs:
        st = sts[kind]

        def draw(im, perf=perf, st=st, back=back):
            _draw_puppet(perf, im, st, back)
        lay = L.Layer.of(size, draw)
        L.grade_layer(lay, T_LIGHT, 0, None, CAM)
        lay.img = dusk(lay.img, DUSK_CHAR)
        warm(lay, glow)
        lay.paste(f)
        if reach or kind == holder:
            over.append((kind, perf, st, reach[0] if reach else "l"))
    lay_pk = L.Layer.of(size, lambda im: place(im, LANTERN.paper(p["strokes"]), CAM.S(BASE)))
    L.grade_layer(lay_pk, T_LIGHT, prop=True)
    lay_pk.img = dusk(lay_pk.img, DUSK_CHAR)
    lay_pk.paste(f)
    if glow > 0:
        place(f, LANTERN.lit(p["strokes"], glow), CAM.S(BASE), shadow=False)

    def draw_over(im):                      # paws reaching in front of the lantern, and the marker (drawn last)
        for kind, perf, st, side in over:
            perf.a._arm(im, CAM, st, side)
        for kind, perf, st, side in over:          # the marker goes over every paw (lesson-critical)
            if kind == holder:
                _, tip, u = p["marker"]
                _marker_place(im, perf, st, side, tip, u)
    if over:
        lay_o = L.Layer.of(size, draw_over)
        L.grade_layer(lay_o, T_LIGHT, 0, None, CAM)
        lay_o.img = dusk(lay_o.img, DUSK_CHAR)
        lay_o.paste(f)
    L.halo(f, CAM, glow, at=GLOW_C, strength=0.40, sigma=125.0)
    frame.world.front(f, T_LIGHT)
    return film(f, p["cam"]), p["cam"]


TIMES = (0.0, 1.5, 3.0, 4.4, 6.6, 17.3, 19.5, 25.5)


def sheet(frames, path, w=780):
    h = int(w * 1920 / 1080)
    cols, gap, lab = 4, 30, 64
    rows = (len(frames) + cols - 1) // cols
    S = Image.new("RGB", (cols * w + (cols + 1) * gap, rows * (h + lab) + (rows + 1) * gap), (34, 34, 40))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 44)
    except OSError:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(S)
    for i, (t, im) in enumerate(frames):
        r, c = divmod(i, cols)
        x, y = gap + c * (w + gap), gap + r * (h + lab + gap)
        d.text((x + 4, y + 6), f"{t:.1f} s", fill=(240, 240, 240), font=font)
        S.paste(im.resize((w, h), Image.LANCZOS), (x, y + lab))
    S.save(path)
    return S.size


def main():
    os.makedirs(OUT, exist_ok=True)
    frame.world = P.Porch(CAM)
    args = sys.argv[1:]
    if "--proto" in args:
        im, _ = frame(25.5)
        im.save(os.path.join(OUT, "proto_glow.png"))
        print("proto ->", os.path.join(OUT, "proto_glow.png"), "luma", round(L.luma(im), 1))
    elif "--still" in args:
        t = float(args[args.index("--still") + 1])
        im, cam = frame(t)
        im.save(os.path.join(OUT, f"still_{t:05.1f}.png"))
        print("still", t, cam)
    elif "--storyboard" in args:
        frames = []
        for t in TIMES:
            im, cam = frame(t)
            im.save(os.path.join(OUT, f"f_{t:04.1f}.png"))
            frames.append((t, im))
            print(f"{t:5.1f} cam {cam}")
        print("sheet", sheet(frames, os.path.join(OUT, "storyboard.png")))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
