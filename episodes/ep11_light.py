"""Episode 11 light (plan N3): dusk grade, railing hearts, the pumpkin's glow and the projected smile.

Per frame, in camera pixels (the frame is RGBA, cam.res pixels per design unit):

    bg = world.background(t)                           # props_porch
    layers = [L.Layer.of(f.size, lambda im: perf.draw(im, t, cam, st=st), head=L.head_mask(perf.a, st, cam, f.size))]
    L.sun_light(bg, t, cam, world.albedo, occluders=[pip_layer])  # railing shadow band, golden hearts (+ gaps)
    L.floor_pool(bg, t, cam, world.albedo, glow)       # warm pool on the deck round the pumpkin
    L.wall_light(bg, t, cam, world.albedo, k, occ)     # the giant face (with the soft wipe / wing-shaped gap)
    for lay in layers:
        L.light_layer(lay, t, cam, glow=glow, beams=[(plane, k)], hearts=...)   # grade + warm light + pattern
        lay.paste(bg)
    ... pumpkin (graded layer + its emissive light) ...
    L.halo(bg, cam, glow)                              # soft bloom round the lit pumpkin
    world.front(bg, t)

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
CHAR_GRADE = {   # multiply, then lift (0..255): faces stay readable in every state
    "golden": ((1.03, 0.96, 0.86), (6, 3, 0)),
    "sunset": ((0.97, 0.84, 0.88), (6, 2, 8)),
    "evening": ((0.72, 0.69, 0.88), (14, 12, 26)),
}


def grade(t):
    """(mul rgb, add rgb) for characters and props at time t (follows the porch's light states)."""
    w = P.state_weights(t)
    mul = np.zeros(3, np.float32)
    add = np.zeros(3, np.float32)
    for s, wt in w.items():
        m, a = CHAR_GRADE[s]
        mul += wt * np.array(m, np.float32)
        add += wt * np.array(a, np.float32)
    d = 1.0 - (1.0 - P.deepen(t)) * 0.6            # characters dim a little less than the porch
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


def _lit(rgb, albedo, tint, I, own=0.0):
    """Move each pixel towards its warm-lit colour (albedo x tint, mixed with `own` of the light's own colour) by I.
    Projected light keeps its colour: a cream tummy turns warm yellow, not white; `own` keeps shapes readable on
    surfaces close to the light's colour (caramel fur, grey feathers)."""
    target = np.minimum(albedo * tint[None, None, :], 255.0)
    if own:
        target = target * (1 - own) + LIGHT_OWN[None, None, :] * own
    k = np.clip(I, 0, 1)[..., None]
    rgb += (target - rgb) * k


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
CHEST = Plane((960, 1270), 0.8, blur=2.0, name="chest")
WING = Plane((916, 1318), 0.5, blur=1.2, name="wing")

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
    _lit(sub[..., :3], alb, col, I * gain)
    _put(f, sub, box)
    return I, box


def _pbox(plane, cam):
    x0, y0, x1, y1 = plane.extent(1.25)
    a = cam.S((x0, y0))
    b = cam.S((x1, y1))
    return a[0], a[1], b[0], b[1]


def beam_on_layer(lay, plane, cam, k, part=None, col=WARM_PATTERN, gain=0.92):
    """The pattern landing on a layer (a body, or `part` of it such as a wing), never on its face.
    Returns the intensity map (crop-sized) for checks."""
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
    _lit(a[..., :3], alb, col * BODY_BOOST, I * gain, own=0.45)
    lay.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    return I


# ---------------------------------------------------------------- grade and warm light on a layer
def grade_layer(lay, t, glow=0.0, glow_at=None, cam=None, glow_r=300.0, glow_gain=0.40):
    """Dusk grade, then the pumpkin's warm light by distance (additive, on top of the grade)."""
    if lay is None:
        return
    a = _arr(lay.img)
    lay.albedo = a[..., :3].copy()
    mul, add = grade(t)
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
HEART_W = 46
HEART_DX = 0                         # where a body in front of the wall catches a heart (relative)


def heart_state(t):
    """(y, colour 0..1, strength) of the hearts on the wall: rise a little, turn pink, fade (gone 9.4)."""
    u = ease_in_out(seg(t, P.T_SUN0, 9.4))
    y = (P.FLOOR_Y - 110) + ((P.FLOOR_Y - 150) - (P.FLOOR_Y - 110)) * u
    col = HEART_GOLD * (1 - u) + HEART_PINK * u
    k = 1.0 - ease_in_out(seg(t, 7.6, 9.4))
    return y, col, k


def _hearts_map(cam, box, y, dx=0.0, size=HEART_W, which=(0, 1, 2)):
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    m = Image.new("L", (W * 2, H * 2), 0)
    d = ImageDraw.Draw(m)
    for i in which:
        pts = heart_pts(HEART_XS[i] + dx, y, size)
        d.polygon([((cam.S(p)[0] - x0) * 2, (cam.S(p)[1] - y0) * 2) for p in pts], fill=255)
    m = m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.6 * cam.res))
    return np.asarray(m).astype(np.float32) / 255


def sun_light(f, t, cam, albedo, occluders=()):
    """Golden hour: the railing's soft shadow band on the lower wall and deck, the three hearts of light inside it,
    and a body standing in a beam catches its heart (its shadow leaves a gap on the wall).
    occluders: [Layer]. Returns {layer: heart intensity map} for the hearts that land on bodies."""
    sk = P.sun_k(t)
    y, col, hk = heart_state(t)
    caught = {}
    if sk <= 0.003 and hk <= 0.003:
        return caught
    box = _clip_box((cam.S((960, 1250))[0], cam.S((960, 1250))[1], cam.S((1500, 1520))[0],
                     cam.S((1500, 1520))[1]), f.size)
    sub = _arr(f.crop(box))
    xx, yy = _grid(box)
    wx, wy = _world(cam, xx, yy)
    # railing shadow band: on the wall (x 1060..1262, y 1300..1390) and across the deck towards the railing
    wall_band = (_soft(wx, 1000, 1262, 36) * _soft(wy, 1302, P.WALL_BASE + 6, 30) * (wx < P.HOUSE_X1))
    deck_band = _soft(wy, P.WALL_BASE, 1478, 8) * _soft(wx - (wy - P.WALL_BASE) * 1.9, 1000, 1262, 40)
    band = np.maximum(wall_band, deck_band) * 0.30 * sk
    sub[..., :3] *= (1 - band)[..., None]
    if hk > 0.003:
        alb = _arr(albedo.crop(box))[..., :3]
        I = _hearts_map(cam, box, y) * hk
        for lay in occluders:                         # bodies in front: catch the heart, cast a gap
            if lay is None:
                continue
            sol = np.zeros(I.shape, np.float32)
            ox0, oy0 = max(box[0], lay.box[0]), max(box[1], lay.box[1])
            ox1, oy1 = min(box[2], lay.box[2]), min(box[3], lay.box[3])
            if ox1 <= ox0 or oy1 <= oy0:
                continue
            s = lay.solid()
            sol[oy0 - box[1]:oy1 - box[1], ox0 - box[0]:ox1 - box[0]] = \
                s[oy0 - lay.box[1]:oy1 - lay.box[1], ox0 - lay.box[0]:ox1 - lay.box[0]]
            shift = int(round(HEART_DX * cam.res))
            shadow = np.zeros_like(sol)                       # her shadow on the wall, offset to the left
            if shift < sol.shape[1]:
                shadow[:, :sol.shape[1] - shift] = sol[:, shift:]
            on_her = _hearts_map(cam, box, y + 4, dx=HEART_DX) * sol
            blocked = np.clip(on_her.max() * 4, 0, 1) if on_her.size else 0
            I = I * (1 - shadow * blocked)
            caught[id(lay)] = (on_her * hk, box)
        _lit(sub[..., :3], alb, col, I * 0.92)
    _put(f, sub, box)
    return caught


def heart_on_layer(lay, caught):
    """Put the heart a body caught (from sun_light) onto that body's layer, never on its face."""
    if lay is None or id(lay) not in caught:
        return None
    I, box = caught[id(lay)]
    full = np.zeros((lay.box[3] - lay.box[1], lay.box[2] - lay.box[0]), np.float32)
    ox0, oy0 = max(box[0], lay.box[0]), max(box[1], lay.box[1])
    ox1, oy1 = min(box[2], lay.box[2]), min(box[3], lay.box[3])
    full[oy0 - lay.box[1]:oy1 - lay.box[1], ox0 - lay.box[0]:ox1 - lay.box[0]] = \
        I[oy0 - box[1]:oy1 - box[1], ox0 - box[0]:ox1 - box[0]]
    if lay.head is not None:
        full = full * (1 - lay.head)
    a = _arr(lay.img)
    alb = lay.albedo if getattr(lay, "albedo", None) is not None else a[..., :3].copy()
    _lit(a[..., :3], alb, HEART_GOLD * BODY_BOOST, full * 0.92, own=0.4)
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
        I = _hearts_map_at(cam, box, hx, hy, P.RAIL_HEART_W + 2) * 0.55 * sk
        _add_light(sub[..., :3], np.full_like(sub[..., :3], 255), np.minimum(col, 1) * 0.9, I)
        _put(f, sub, box)


def _hearts_map_at(cam, box, x, y, size):
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    m = Image.new("L", (W * 2, H * 2), 0)
    pts = heart_pts(x, y, size)
    ImageDraw.Draw(m).polygon([((cam.S(p)[0] - x0) * 2, (cam.S(p)[1] - y0) * 2) for p in pts], fill=255)
    m = m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.2 * cam.res))
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
