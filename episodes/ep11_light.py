"""Episode 11 light (plan N3): dusk grade, railing hearts, the pumpkin's glow and the projected smile.

Per frame, in camera pixels (the frame is RGBA, cam.res pixels per design unit):

    bg = world.background(t)                           # props_porch (wall in the roof's shade at golden hour)
    lay = L.Layer.of(bg.size, lambda im: perf.draw(im, t, cam, st=st), head=L.head_mask(perf.a, st, cam, bg.size))
    caught = L.sun_light(bg, t, cam, world.albedo, occluders=[wing, pip])   # FRONT FIRST: who catches a heart
    L.floor_pool(bg, cam, world.albedo, glow, facing)  # warm pool on the deck round the pumpkin
    L.wall_light(bg, cam, world.albedo, k, occ)        # the giant face: near-white core, soft bloom, gaps
    for lay in layers:
        L.grade_layer(lay, t, glow, L.GLOW_AT, cam)    # dusk grade (characters keep their colour; prop=True: set)
        L.rail_shade(lay, t, cam)                      # a body in the railing's shadow
        L.heart_on_layer(lay, caught, t, cam)          # a caught heart, near-white, never on the face
        L.beam_on_layer(lay, plane, cam, k)            # the projected face on a body / wing (golden edge, white core)
        lay.paste(bg)
    ... pumpkin (graded layer + its emissive light); L.shade_layer(lay, mul, k) darkens one surface ...
    L.halo(bg, cam, glow)                              # soft bloom round the lit pumpkin
    world.front(bg, t); L.rail_glow(bg, t, cam)        # railing, then its sunlit cut-outs

Rules built in (Ep 11 safety, carry-forward 1 and 2):
  * never black: the grade multiplies and then lifts (a cool floor), so faces always stay readable;
  * projected light lands only on bodies, wings, paws and the wall: every layer's head mask is cut out of the
    light it receives (the head still blocks light, so the wall keeps the right gap);
  * the pattern is soft-edged, warm yellow-orange, brightest in the middle, with a faint warm wash on the wall.

Projection geometry. The tea light sits low inside the pumpkin (x 960); a cut face lets through a pattern that
gets bigger the farther it travels. A "plane" is where the light lands: its centre in world units and its scale
against the face design (props_pumpkin.FEATURES, centred on PATTERN_C). Light blocked on one plane leaves the
same shape, scaled up, missing on the planes behind it (map_mask).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import props_porch as P  # noqa: E402
import props_pumpkin as PK  # noqa: E402
from paperlib import ease_in_out, heart_pts, place, seg  # noqa: E402

WARM = np.array((255, 178, 84), np.float32) / 255          # the pumpkin's light (yellow-orange)
WARM_PATTERN = np.array((1.10, 0.88, 0.50), np.float32)   # tint of a surface lit by the projected face
BODY_BOOST = 1.38                                          # light on fur/feathers: clearly brighter than dusk
HEART_GOLD = np.array((1.18, 0.92, 0.46), np.float32)     # tint of a surface lit by a golden heart
HEART_PINK = np.array((1.14, 0.80, 0.88), np.float32)


# ---------------------------------------------------------------- the grade for characters and props
CHAR_GRADE = {   # multiply, then lift (0..255): characters keep most of their colour (Lead L4)
    "golden": ((1.03, 0.96, 0.86), (6, 3, 0)),
    "sunset": ((0.98, 0.88, 0.91), (5, 2, 6)),
    "evening": ((0.88, 0.85, 0.94), (8, 7, 16)),
}
PROP_GRADE = {   # props sit in the set's light: graded more than the characters
    "golden": ((1.03, 0.96, 0.86), (6, 3, 0)),
    "sunset": ((0.97, 0.84, 0.88), (6, 2, 8)),
    "evening": ((0.74, 0.71, 0.88), (14, 12, 26)),
}


def grade(t, prop=False):
    """(mul rgb, add rgb) for characters (or props) at time t (follows the porch's light states)."""
    w = P.state_weights(t)
    table = PROP_GRADE if prop else CHAR_GRADE
    mul = np.zeros(3, np.float32)
    add = np.zeros(3, np.float32)
    for s, wt in w.items():
        m, a = table[s]
        mul += wt * np.array(m, np.float32)
        add += wt * np.array(a, np.float32)
    d = 1.0 - (1.0 - P.deepen(t)) * (0.6 if prop else 0.35)     # characters dim less than the porch
    return mul * d, add


# ---------------------------------------------------------------- layers
class Layer:
    """Something drawn on its own transparent layer (camera pixels), cropped to what it covers."""

    def __init__(self, img, box, head=None):
        self.img, self.box = img, box                  # img: RGBA crop; box: (x0, y0, x1, y1) in the frame
        self.head = head                               # float32 mask (crop-sized) of the face (gets no beams)
        self.extra = None                              # optional float32 mask of a part on another plane

    @classmethod
    def of(cls, size, draw, head=None, pad=2):
        full = Image.new("RGBA", size, (0, 0, 0, 0))
        draw(full)
        bb = full.getchannel("A").point(lambda v: 255 if v > 3 else 0).getbbox()
        if bb is None:
            return None
        bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(size[0], bb[2] + pad), min(size[1], bb[3] + pad))
        h = None
        if head is not None:
            h = np.asarray(head.crop(bb)).astype(np.float32) / 255
        return cls(full.crop(bb), bb, h)

    def solid(self):
        """Where the layer is solid paper (not its soft drop shadows): 0..1."""
        a = np.asarray(self.img.getchannel("A")).astype(np.float32) / 255
        return np.clip((a - 0.45) / 0.3, 0, 1)

    def paste(self, f):
        f.alpha_composite(self.img, (self.box[0], self.box[1]))


def head_mask(puppet, st, cam, size, grow=6):
    """The face of a rig2 puppet as a mask (L, frame-sized), grown by `grow` design units for safety."""
    m = Image.new("RGBA", size, (0, 0, 0, 0))
    hx, hy = puppet.head_pivot(st)
    ha = st["lean"] + st["tilt"]
    tt = max(-1.0, min(1.0, st["turn"] + st.get("hturn", 0.0)))
    look = (int(round(st["look_x"] / 2) * 2), int(round(st["look_y"] / 2) * 2))
    place(m, puppet.head(st["eyes"], st["mouth"], look, st["brows"], tt), cam.S((hx, hy)), angle=ha, shadow=False)
    return grow_mask(m.getchannel("A"), int(round(grow * cam.res)))


def grow_mask(a, r):
    """Dilate an L mask by about r pixels, fast: only round its bounding box, at a quarter of the resolution."""
    bb = a.getbbox()
    if r <= 0 or bb is None:
        return a
    x0, y0 = max(0, bb[0] - r - 4), max(0, bb[1] - r - 4)
    x1, y1 = min(a.width, bb[2] + r + 4), min(a.height, bb[3] + r + 4)
    crop = a.crop((x0, y0, x1, y1))
    q = 4
    small = crop.resize((max(1, crop.width // q), max(1, crop.height // q)), Image.BOX)
    small = small.point(lambda v: 255 if v > 0 else 0).filter(ImageFilter.MaxFilter(2 * int(math.ceil(r / q)) + 1))
    big = small.resize(crop.size, Image.BILINEAR).point(lambda v: 255 if v > 40 else 0)
    from PIL import ImageChops
    out = Image.new("L", a.size, 0)
    out.paste(ImageChops.lighter(big, crop), (x0, y0))
    return out


# ---------------------------------------------------------------- numpy helpers
def _arr(img):
    return np.asarray(img).astype(np.float32)


def _put(f, arr, box):
    f.paste(Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA"), (box[0], box[1]))


def _clip_box(box, size):
    x0, y0, x1, y1 = box
    return (max(0, int(x0)), max(0, int(y0)), min(size[0], int(math.ceil(x1))), min(size[1], int(math.ceil(y1))))


def _grid(box):
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    return xx, yy


def _world(cam, xx, yy):
    return xx / cam.res + cam.ox, yy / cam.res + cam.oy


def _soft_add(rgb, addv):
    """rgb += addv, easing off as a channel nears white (unlit pixels are untouched; nothing flattens to white)."""
    rgb += addv * (1.0 - np.clip(rgb / 255.0, 0, 1) ** 2)


def _add_light(rgb, albedo, col, I):
    """Warm light added on top: albedo x colour x I (rgb, albedo 0..255; col 0..1; I 0..1)."""
    _soft_add(rgb, albedo * col[None, None, :] * I[..., None])


LIGHT_OWN = np.array((255, 222, 120), np.float32)         # the colour of the light itself
NEAR_WHITE = np.array((255, 248, 220), np.float32)        # the bright core of a projected shape (Lead L2, L3)
BLOOM_COL = np.array((1.0, 0.86, 0.58), np.float32)       # soft bloom round projected light


def _lit(rgb, albedo, tint, I, own=0.0, own_col=LIGHT_OWN):
    """Move each pixel towards its warm-lit colour (albedo x tint, mixed with `own` of the light's own colour) by I.
    `own` may be a number or a map (e.g. more near-white in the bright core of a shape)."""
    target = np.minimum(albedo * tint[None, None, :], 255.0)
    if np.any(np.asarray(own) > 0):
        o = np.asarray(own, np.float32)
        o = o[..., None] if o.ndim == 2 else o
        target = target * (1 - o) + own_col[None, None, :] * o
    k = np.clip(I, 0, 1)[..., None]
    rgb += (target - rgb) * k


def _blur(I, sigma_px):
    """Gaussian blur of a 0..1 map (for bloom)."""
    if sigma_px <= 0.3:
        return I
    img = Image.fromarray((np.clip(I, 0, 1) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(sigma_px))
    return np.asarray(img).astype(np.float32) / 255


def _bloom(rgb, I, sigma_px, gain, clip=None, col=BLOOM_COL):
    """A soft warm bloom round lit shapes (added, easing off near white); `clip` keeps it on one surface."""
    B = _blur(I, sigma_px) * gain
    if clip is not None:
        B = B * clip
    _soft_add(rgb, 255.0 * col[None, None, :] * B[..., None])


# ---------------------------------------------------------------- planes and the face pattern
class Plane:
    """Where the pumpkin's light lands: centre (world units) and scale against the face design."""

    def __init__(self, c, sx, sy=None, blur=2.0, wash=0.0, name=""):
        self.c, self.sx, self.sy = c, sx, sx if sy is None else sy
        self.blur, self.wash, self.name = blur, wash, name

    def shifted(self, dx=0.0, dy=0.0):
        return Plane((self.c[0] + dx, self.c[1] + dy), self.sx, self.sy, self.blur, self.wash, self.name)

    def to_world(self, u, v):
        """Face-design point (base-relative) -> world."""
        return (self.c[0] + (u - PK.PATTERN_C[0]) * self.sx, self.c[1] + (v - PK.PATTERN_C[1]) * self.sy)

    def extent(self, margin=1.0):
        hw, hh = 72 * self.sx * margin, 58 * self.sy * margin
        if self.wash:
            hw, hh = max(hw, 120 * self.sx), max(hh, 95 * self.sy)
        return self.c[0] - hw, self.c[1] - hh, self.c[0] + hw, self.c[1] + hh


WALL = Plane((960, 866), 3.6, 3.6 * 1.1, blur=7.0, wash=0.15, name="wall")
CHEST = Plane((960, 1275), 0.8, 0.62, blur=1.2, name="chest")  # Lead L2: 0.8x, raised: the smile on the
                                                                # cream tummy, clear of the stem; his round
                                                                # tummy leans back, so it lands a little flatter
WING = Plane((946, 1318), 0.5, blur=1.0, name="wing")        # Lead L3 (set from the episode's wing pose)

_PAT = {}


def pattern(plane, cam, box):
    """Light intensity of the face pattern on a plane, over `box` (frame pixels): soft-edged, brightest in the
    middle, plus the faint wash if the plane has one. float32 array (box-sized)."""
    key = (plane.c, plane.sx, plane.sy, plane.blur, plane.wash, box, cam.res, cam.ox, cam.oy)
    if key in _PAT:
        return _PAT[key]
    if len(_PAT) > 64:
        _PAT.clear()
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    ss = 2
    m = Image.new("L", (W * ss, H * ss), 0)
    d = ImageDraw.Draw(m)
    for poly in PK.pattern_shapes():
        pts = []
        for u, v in poly:
            wx, wy = plane.to_world(u, v)
            px, py = cam.S((wx, wy))
            pts.append(((px - x0) * ss, (py - y0) * ss))
        d.polygon(pts, fill=255)
    m = m.resize((W, H), Image.LANCZOS)
    sig = plane.blur * cam.res
    if sig > 0.3:
        m = m.filter(ImageFilter.GaussianBlur(sig))
    pat = np.asarray(m).astype(np.float32) / 255
    xx, yy = _grid(box)
    wx, wy = _world(cam, xx, yy)
    u = (wx - plane.c[0]) / plane.sx
    v = (wy - plane.c[1]) / plane.sy
    prof = 0.60 + 0.40 * np.exp(-(u * u + v * v) / (2 * 52.0 ** 2))       # brightest in the middle
    out = pat * prof
    if plane.wash:
        wash = plane.wash * np.exp(-((u / 105.0) ** 2 + (v / 82.0) ** 2) * 1.6)
        out = 1 - (1 - out) * (1 - wash)
    _PAT[key] = out
    return out


def map_mask(mask, mbox, src, dst, cam, dbox, blur_units=None):
    """Shadow of `mask` (float32 over mbox, lying on plane src) as it falls on plane dst, over dbox."""
    x0, y0, x1, y1 = dbox
    W, H = x1 - x0, y1 - y0
    r = cam.res
    kx, ky = src.sx / dst.sx, src.sy / dst.sy
    # dst pixel (rel) -> src pixel (rel to mbox)
    cx = (cam.ox - dst.c[0]) * kx * r + (src.c[0] - cam.ox) * r
    cy = (cam.oy - dst.c[1]) * ky * r + (src.c[1] - cam.oy) * r
    a = kx
    c = kx * x0 + cx - mbox[0]
    e = ky
    f_ = ky * y0 + cy - mbox[1]
    img = Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8), "L")
    out = img.transform((W, H), Image.AFFINE, (a, 0, c, 0, e, f_), resample=Image.BILINEAR)
    if blur_units is None:                       # penumbra grows with the distance between the planes
        blur_units = 4.0 * (dst.sx / max(src.sx, 1e-3) - 1.0)
    sig = blur_units * r
    if sig > 0.3:
        out = out.filter(ImageFilter.GaussianBlur(sig))
    return np.asarray(out).astype(np.float32) / 255


# ---------------------------------------------------------------- the wall: the giant face with its gaps
def wall_light(f, cam, albedo, k, occluders=(), plane=WALL, col=WARM_PATTERN, gain=0.95):
    """Paint the projected face on the wall. occluders: [(mask float32, mbox, plane_it_lies_on)].
    Returns the intensity map and its box (for checks)."""
    if k <= 0.003:
        return None, None
    box = _clip_box([v * 1 for v in _pbox(plane, cam)], f.size)
    I = pattern(plane, cam, box) * k
    for mask, mbox, src in occluders:
        if mask is None:
            continue
        g = map_mask(mask, mbox, src, plane, cam, box)
        I = I * (1 - g)
    sub = _arr(f.crop(box))
    alb = _arr(albedo.crop(box))[..., :3]
    core = np.clip((I / max(k, 1e-3) - 0.66) / 0.34, 0, 1)          # Lead L4: a brighter core ...
    _lit(sub[..., :3], alb, col, I * gain, own=0.15 + 0.55 * core, own_col=NEAR_WHITE)
    _bloom(sub[..., :3], I, WALL_BLOOM * cam.res, 0.42)               # ... and a soft bloom: light, not paint
    _put(f, sub, box)
    return I, box


WALL_BLOOM = 16.0                                                    # design units


def _pbox(plane, cam):
    x0, y0, x1, y1 = plane.extent(1.25)
    a = cam.S((x0, y0))
    b = cam.S((x1, y1))
    return a[0], a[1], b[0], b[1]


def beam_on_layer(lay, plane, cam, k, part=None, col=WARM_PATTERN, gain=0.97, bloom=3.0, own=(0.2, 0.7)):
    """The pattern landing on a layer (a body, or `part` of it such as a wing), never on its face: near-white warm
    in its bright core, with a soft bloom kept on that surface. Returns the intensity map (crop-sized) for checks."""
    if lay is None or k <= 0.003:
        return None
    box = lay.box
    pb = _clip_box(_pbox(plane, cam), (10 ** 6, 10 ** 6))
    ix0, iy0 = max(box[0], pb[0]), max(box[1], pb[1])
    ix1, iy1 = min(box[2], pb[2]), min(box[3], pb[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return None
    full = np.zeros((box[3] - box[1], box[2] - box[0]), np.float32)
    full[iy0 - box[1]:iy1 - box[1], ix0 - box[0]:ix1 - box[0]] = pattern(plane, cam, (ix0, iy0, ix1, iy1))
    clip = lay.solid() if part is None else part
    I = full * clip * k
    if lay.head is not None:
        I = I * (1 - lay.head)
    a = _arr(lay.img)
    alb = lay.albedo if getattr(lay, "albedo", None) is not None else a[..., :3].copy()
    core = np.clip((I / max(k, 1e-3) - 0.6) / 0.4, 0, 1)
    _lit(a[..., :3], alb, col * BODY_BOOST, I * gain, own=own[0] + own[1] * core, own_col=NEAR_WHITE)  # golden edge,
    surf = clip if lay.head is None else clip * (1 - lay.head)                                     # white core
    _bloom(a[..., :3], I, bloom * cam.res, 0.22, clip=surf)
    lay.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    return I


# ---------------------------------------------------------------- grade and warm light on a layer
def grade_layer(lay, t, glow=0.0, glow_at=None, cam=None, glow_r=300.0, glow_gain=0.40, prop=False):
    """Dusk grade, then the pumpkin's warm light by distance (additive, on top of the grade)."""
    if lay is None:
        return
    a = _arr(lay.img)
    lay.albedo = a[..., :3].copy()
    mul, add = grade(t, prop)
    a[..., :3] = a[..., :3] * mul[None, None, :] + add[None, None, :]
    if glow > 0.003 and glow_at is not None:
        xx, yy = _grid(lay.box)
        wx, wy = _world(cam, xx, yy)
        d2 = (wx - glow_at[0]) ** 2 + ((wy - glow_at[1]) * 1.15) ** 2
        I = glow * glow_gain * np.exp(-d2 / (2 * glow_r ** 2))
        _add_light(a[..., :3], lay.albedo, WARM, I)
    lay.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


# ---------------------------------------------------------------- golden hour: the railing hearts
HEART_XS = (1040, 1130, 1220)
HEART_W = 76                         # Lead L1: each heart on the wall at least 70 units wide
HEART_W_BODY = 50                    # the same beam caught nearer the railing (on Pip): a little smaller
HEART_DY_BODY = 88                   # ... and lower on screen: she stands in front of the wall, nearer the camera
                                     # (rule: >= 30 units from her head; see the episode's checks)
HEART_LIGHT = np.array((255, 246, 214), np.float32)       # sunlight through the cut-outs: warm near-white ...
HEART_LIGHT_PINK = np.array((255, 226, 230), np.float32)  # ... turning pink as the sun goes down
HEART_Y0, HEART_Y1 = P.FLOOR_Y - 155, P.FLOOR_Y - 185   # whole hearts on the wall, above the pumpkin's top
RAIL_SHADE_K = 0.14                  # how much the railing's shadow darkens a body standing in it


def heart_state(t):
    """(y, colour 0..1, strength) of the hearts on the wall: rise a little, turn pink, fade (gone 9.4)."""
    u = ease_in_out(seg(t, P.T_SUN0, 9.4))
    y = HEART_Y0 + (HEART_Y1 - HEART_Y0) * u
    col = HEART_GOLD * (1 - u) + HEART_PINK * u
    k = 1.0 - ease_in_out(seg(t, 7.6, 9.4))
    return y, col, k


def heart_light(t):
    u = ease_in_out(seg(t, P.T_SUN0, 9.4))
    return HEART_LIGHT * (1 - u) + HEART_LIGHT_PINK * u


def _hearts_map(cam, box, y, dx=0.0, size=HEART_W, which=(0, 1, 2), blur=1.6):
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    m = Image.new("L", (W * 2, H * 2), 0)
    d = ImageDraw.Draw(m)
    for i in which:
        pts = heart_pts(HEART_XS[i] + dx, y, size)
        d.polygon([((cam.S(p)[0] - x0) * 2, (cam.S(p)[1] - y0) * 2) for p in pts], fill=255)
    m = m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(blur * cam.res))
    return np.asarray(m).astype(np.float32) / 255


def _sun_box(f, cam):
    a, b = cam.S((960, 1250)), cam.S((1500, 1520))
    return _clip_box((a[0], a[1], b[0], b[1]), f.size)


def _into(arr_box, lay):
    """Copy of a map over arr_box, cut to a layer's box (zeros where they don't overlap)."""
    arr, box = arr_box
    full = np.zeros((lay.box[3] - lay.box[1], lay.box[2] - lay.box[0]), np.float32)
    ox0, oy0 = max(box[0], lay.box[0]), max(box[1], lay.box[1])
    ox1, oy1 = min(box[2], lay.box[2]), min(box[3], lay.box[3])
    if ox1 > ox0 and oy1 > oy0:
        full[oy0 - lay.box[1]:oy1 - lay.box[1], ox0 - lay.box[0]:ox1 - lay.box[0]] = \
            arr[oy0 - box[1]:oy1 - box[1], ox0 - box[0]:ox1 - box[0]]
    return full


def sun_light(f, t, cam, albedo, occluders=()):
    """Golden hour: the wall sits in the roof's shade (props_porch); the railing adds a soft shadow band, and the low
    sun shines through its three heart cut-outs: bright warm near-white hearts on the wall (Lead L1).
    occluders: Layers standing in the beams, FRONT FIRST (e.g. [Pip's wing, Pip]): each catches the part of a heart
    that nothing in front of it took. Returns {id(layer): (heart map, box)}."""
    sk = P.sun_k(t)
    y, col, hk = heart_state(t)
    caught = {}
    if sk <= 0.003 and hk <= 0.003:
        return caught
    box = _sun_box(f, cam)
    sub = _arr(f.crop(box))
    xx, yy = _grid(box)
    wx, wy = _world(cam, xx, yy)
    band = _rail_band(wx, wy) * 0.42 * sk
    sub[..., :3] *= (1 - band)[..., None]
    if hk > 0.003:
        alb = _arr(albedo.crop(box))[..., :3]
        I = _hearts_map(cam, box, y, blur=1.0) * hk
        covered = np.zeros(I.shape, np.float32)
        for lay in occluders:
            if lay is None:
                continue
            cx = ((lay.box[0] + lay.box[2]) / 2) / cam.res + cam.ox      # a body catches the beam it stands in
            mine = tuple(i for i, hx in enumerate(HEART_XS) if abs(hx - cx) < 32)
            on_body = (_hearts_map(cam, box, HEART_Y0 + HEART_DY_BODY, size=HEART_W_BODY, blur=1.0, which=mine)
                       if mine else np.zeros(I.shape, np.float32))
            sol = np.zeros(I.shape, np.float32)
            ox0, oy0 = max(box[0], lay.box[0]), max(box[1], lay.box[1])
            ox1, oy1 = min(box[2], lay.box[2]), min(box[3], lay.box[3])
            if ox1 <= ox0 or oy1 <= oy0:
                continue
            s = lay.solid()
            sol[oy0 - box[1]:oy1 - box[1], ox0 - box[0]:ox1 - box[0]] = \
                s[oy0 - lay.box[1]:oy1 - lay.box[1], ox0 - lay.box[0]:ox1 - lay.box[0]]
            caught[id(lay)] = (on_body * sol * (1 - covered) * hk, box)
            covered = np.maximum(covered, sol)
        I = I * (1 - covered)                          # the bodies take the light; the wall behind them gets none
        _lit(sub[..., :3], alb, col, I * 0.97, own=0.72, own_col=heart_light(t))
        _bloom(sub[..., :3], I, 4.0 * cam.res, 0.15)
    _put(f, sub, box)
    return caught


def _rail_band(wx, wy):
    """Where the railing's shadow falls (wall and deck), 0..1."""
    wall_band = (_soft(wx, 1000, 1262, 36) * _soft(wy, 1262, P.WALL_BASE + 6, 30) * (wx < P.HOUSE_X1))
    deck_band = _soft(wy, P.WALL_BASE, 1478, 8) * _soft(wx - (wy - P.WALL_BASE) * 1.9, 1000, 1262, 40)
    return np.maximum(wall_band, deck_band)


def rail_shade(lay, t, cam):
    """A body standing between the railing and the wall is in the railing's shadow below its top (so a caught heart
    reads bright): darken it there, softly."""
    sk = P.sun_k(t)
    if lay is None or sk <= 0.003:
        return
    xx, yy = _grid(lay.box)
    wx, wy = _world(cam, xx, yy)
    sh = _soft(wx, 1000, 1290, 40) * np.clip((wy - (P.RAIL[2] + 10)) / 30.0, 0, 1) * RAIL_SHADE_K * sk
    if lay.head is not None:
        sh = sh * (1 - lay.head)
    a = _arr(lay.img)
    a[..., :3] *= (1 - sh)[..., None]
    lay.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def shade_layer(lay, mul, k=1.0):
    """Darken a layer (e.g. a surface turned away from the dusk light): rgb *= mix(1, mul, k)."""
    if lay is None or k <= 0.003:
        return
    a = _arr(lay.img)
    m = 1 + (np.array(mul, np.float32) - 1) * k
    a[..., :3] *= m[None, None, :]
    lay.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def heart_on_layer(lay, caught, t, cam):
    """Put the heart a body caught (from sun_light) onto that body's layer, never on its face: near-white warm with
    a soft bloom kept on that surface."""
    if lay is None or id(lay) not in caught:
        return None
    full = _into(caught[id(lay)], lay)
    if lay.head is not None:
        full = full * (1 - lay.head)
    a = _arr(lay.img)
    alb = lay.albedo if getattr(lay, "albedo", None) is not None else a[..., :3].copy()
    _lit(a[..., :3], alb, HEART_GOLD * BODY_BOOST, full * 0.97, own=0.75, own_col=heart_light(t))
    surf = lay.solid() if lay.head is None else lay.solid() * (1 - lay.head)
    _bloom(a[..., :3], full, 3.5 * cam.res, 0.4, clip=surf)
    lay.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    return full


def rail_glow(f, t, cam):
    """The cut-outs glow warm while the sun shines through them (drawn after the railing)."""
    sk = P.sun_k(t)
    if sk <= 0.003:
        return
    y_, col, _ = heart_state(t)
    for hx, hy in P.RAIL_HEARTS:
        r = 30
        box = _clip_box((cam.S((hx - r, hy - r))[0], cam.S((hx - r, hy - r))[1], cam.S((hx + r, hy + r))[0],
                         cam.S((hx + r, hy + r))[1]), f.size)
        if box[2] <= box[0]:
            continue
        sub = _arr(f.crop(box))
        I = _hearts_map_at(cam, box, hx, hy, P.RAIL_HEART_W + 2) * sk           # the low sun right behind the cut-outs
        _lit(sub[..., :3], np.full_like(sub[..., :3], 255), np.ones(3, np.float32), I, own=1.0,
             own_col=np.minimum(heart_light(t) * np.array((1.0, 0.97, 0.86), np.float32), 255))
        _put(f, sub, box)


def _hearts_map_at(cam, box, x, y, size):
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    m = Image.new("L", (W * 2, H * 2), 0)
    pts = heart_pts(x, y, size)
    ImageDraw.Draw(m).polygon([((cam.S(p)[0] - x0) * 2, (cam.S(p)[1] - y0) * 2) for p in pts], fill=255)
    m = m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2 * cam.res))
    return np.asarray(m).astype(np.float32) / 255


def _soft(v, a, b, w):
    return np.clip((v - a) / w + 0.5, 0, 1) * np.clip((b - v) / w + 0.5, 0, 1)


# ---------------------------------------------------------------- the pumpkin's glow on the porch
GLOW_AT = (PK.BASE[0], PK.BASE[1] - 85)


def glow_k(t, t_on=95.6, t_full=96.8):
    """The pumpkin's own light: 0 before the tea light goes in, rising as it goes down inside, then steady."""
    return ease_in_out(seg(t, t_on, t_full))


def floor_pool(f, cam, albedo, glow, facing=1.0, side=0.0):
    """A warm pool of light on the deck round the pumpkin (and a little on the wall base behind it).
    facing: 1 = the face points at the camera (pool spreads forward), 0 = it points at the wall."""
    if glow <= 0.003:
        return
    cx, cy = PK.BASE[0] + 230 * side, PK.BASE[1] + 8 * facing - 10 * (1 - facing)
    box = _clip_box((cam.S((cx - 620, P.WALL_BASE - 160))[0], cam.S((cx - 620, P.WALL_BASE - 160))[1],
                     cam.S((cx + 620, 1640))[0], cam.S((cx + 620, 1640))[1]), f.size)
    sub = _arr(f.crop(box))
    alb = _arr(albedo.crop(box))[..., :3]
    xx, yy = _grid(box)
    wx, wy = _world(cam, xx, yy)
    on_deck = np.clip((wy - P.WALL_BASE) / 10 + 0.5, 0, 1)
    pool = np.exp(-(((wx - cx) / 470.0) ** 2 + ((wy - cy) / 95.0) ** 2) * 1.4) * on_deck
    wall = np.exp(-(((wx - cx) / 330.0) ** 2 + ((wy - P.WALL_BASE) / 120.0) ** 2) * 1.5) * (1 - on_deck)
    I = glow * (0.62 * pool + 0.22 * wall)
    _add_light(sub[..., :3], alb, WARM, I)
    _put(f, sub, box)


def halo(f, cam, glow, at=GLOW_AT, strength=0.22, sigma=105.0):
    """A soft warm bloom round the lit pumpkin (over everything; soft, never a hard ring)."""
    if glow <= 0.003:
        return
    r = sigma * 2.6
    box = _clip_box((cam.S((at[0] - r * 1.3, at[1] - r))[0], cam.S((at[0] - r * 1.3, at[1] - r))[1],
                     cam.S((at[0] + r * 1.3, at[1] + r))[0], cam.S((at[0] + r * 1.3, at[1] + r))[1]), f.size)
    sub = _arr(f.crop(box))
    xx, yy = _grid(box)
    wx, wy = _world(cam, xx, yy)
    I = glow * strength * np.exp(-(((wx - at[0]) / 1.3) ** 2 + (wy - at[1]) ** 2) / (2 * sigma ** 2))
    _soft_add(sub[..., :3], (255 * WARM)[None, None, :] * I[..., None] * 0.9)
    _put(f, sub, box)


# ---------------------------------------------------------------- checks
def luma(img):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    return float((0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]).mean())


def lit_points(I, box, cam, thresh=0.02):
    """World coordinates of every pixel where projected light is visible (intensity >= thresh)."""
    if I is None:
        return np.zeros((0, 2), np.float32)
    ys, xs = np.nonzero(I >= thresh)
    return np.stack([(xs + box[0]) / cam.res + cam.ox, (ys + box[1]) / cam.res + cam.oy], 1)


def clearance(pts, p):
    """Smallest distance (design units) from point p to any lit point."""
    if len(pts) == 0:
        return float("inf")
    return float(np.sqrt(((pts - np.array(p, np.float32)) ** 2).sum(1)).min())
