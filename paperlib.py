"""Paper cut-out drawing helpers.

Shapes are drawn at SS x resolution, then downsampled for smooth edges and
finished with a white "cut paper" border, light grain and a soft drop shadow.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 3
PAPER_EDGE = (255, 253, 246)
SHADOW_RGB = (55, 38, 30)
EMOJI_FONT = "/System/Library/Fonts/Apple Color Emoji.ttc"
_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_font(*cands):
    for c in cands:
        if c and os.path.exists(os.path.expanduser(c)):
            return os.path.expanduser(c)
    return None


# Fredoka (SIL Open Font License) — free to use in monetized videos. setup_cloud.sh fetches it on Linux.
ROUND_FONT = _find_font(os.environ.get("SC_ROUND_FONT"),
                        os.path.join(_HERE, "assets", "fonts", "Fredoka[wdth,wght].ttf"),
                        "~/Library/Fonts/Fredoka[wdth,wght].ttf")


def round_font(size):
    if ROUND_FONT is None:
        raise FileNotFoundError("Fredoka font missing — run setup_cloud.sh or install font-fredoka")
    f = ImageFont.truetype(ROUND_FONT, int(size))
    try:
        f.set_variation_by_axes([650, 100])   # axes: weight, width
    except Exception:
        pass
    return f

_rng = np.random.default_rng(7)


def grain(img, strength=0.035):
    """Fine paper grain plus soft low-frequency blotches (keeps alpha)."""
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    fine = _rng.normal(0, 1, (h, w)).astype(np.float32)
    small = Image.fromarray(((_rng.normal(0, 1, (max(h // 24, 2), max(w // 24, 2))) * 40) + 128)
                            .clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    blotch = (np.asarray(small).astype(np.float32) - 128) / 40
    n = fine * 0.55 + blotch * 0.3
    a[..., :3] *= (1 + strength * n[..., None])
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), img.mode)


def mix(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))


def ellipse_pts(cx, cy, rx, ry, theta_deg=0.0, n=72):
    th = math.radians(theta_deg)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * math.cos(th) - y * math.sin(th), cy + x * math.sin(th) + y * math.cos(th)))
    return pts


def heart_pts(cx, cy, size, n=80):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * size / 32, cy - y * size / 32))
    return pts


def emoji_image(ch, px):
    f = ImageFont.truetype(EMOJI_FONT, 160)
    tmp = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((10, 10), ch, font=f, embedded_color=True)
    tmp = tmp.crop(tmp.getbbox())
    s = px / max(tmp.size)
    return tmp.resize((max(1, int(tmp.width * s)), max(1, int(tmp.height * s))), Image.LANCZOS)


class Sprite:
    def __init__(self, img, pivot, shadow=None):
        self.img = img
        self.pivot = pivot
        self.shadow = shadow

    def scaled(self, s):
        if s == 1:
            return self
        size = (max(1, int(self.img.width * s)), max(1, int(self.img.height * s)))
        sh = self.shadow.resize(size, Image.LANCZOS) if self.shadow else None
        return Sprite(self.img.resize(size, Image.LANCZOS), (self.pivot[0] * s, self.pivot[1] * s), sh)


class Cut:
    """One paper cut-out. Coordinates are in final pixels."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        self.mask = Image.new("L", (w * SS, h * SS), 0)
        self.d = ImageDraw.Draw(self.img)
        self.m = ImageDraw.Draw(self.mask)

    @staticmethod
    def _s(seq):
        return [v * SS for v in seq]

    def ellipse(self, cx, cy, rx, ry, fill, sil=True, theta=0):
        if theta:
            return self.polygon(ellipse_pts(cx, cy, rx, ry, theta), fill, sil)
        box = self._s([cx - rx, cy - ry, cx + rx, cy + ry])
        self.d.ellipse(box, fill=fill)
        if sil:
            self.m.ellipse(box, fill=255)

    def rrect(self, x0, y0, x1, y1, r, fill, sil=True):
        box = self._s([x0, y0, x1, y1])
        self.d.rounded_rectangle(box, r * SS, fill=fill)
        if sil:
            self.m.rounded_rectangle(box, r * SS, fill=255)

    def polygon(self, pts, fill, sil=True):
        p = [(x * SS, y * SS) for x, y in pts]
        self.d.polygon(p, fill=fill)
        if sil:
            self.m.polygon(p, fill=255)

    def line(self, pts, width, fill, sil=False):
        p = [(x * SS, y * SS) for x, y in pts]
        w = int(width * SS)
        r = w / 2
        targets = [self.d] + ([self.m] if sil else [])
        for dr in targets:
            col = 255 if dr is self.m else fill
            dr.line(p, fill=col, width=w, joint="curve")
            for x, y in (p[0], p[-1]):
                dr.ellipse([x - r, y - r, x + r, y + r], fill=col)

    def arc(self, cx, cy, rx, ry, start, end, width, fill):
        self.d.arc(self._s([cx - rx, cy - ry, cx + rx, cy + ry]), start, end, fill=fill, width=int(width * SS))

    def chord(self, cx, cy, rx, ry, start, end, fill, sil=False):
        box = self._s([cx - rx, cy - ry, cx + rx, cy + ry])
        self.d.chord(box, start, end, fill=fill)
        if sil:
            self.m.chord(box, start, end, fill=255)

    def emoji(self, ch, cx, cy, px, sil=True):
        e = emoji_image(ch, px * SS)
        x, y = int(cx * SS - e.width / 2), int(cy * SS - e.height / 2)
        self.img.alpha_composite(e, (x, y))
        if sil:
            self.mask.paste(255, (x, y), e.getchannel("A"))

    def text(self, s, cx, cy, size, fill, font=ROUND_FONT, sil=True):
        f = round_font(size * SS) if font == ROUND_FONT else ImageFont.truetype(font, int(size * SS))
        bb = self.d.textbbox((0, 0), s, font=f)
        x = cx * SS - (bb[0] + bb[2]) / 2
        y = cy * SS - (bb[1] + bb[3]) / 2
        self.d.text((x, y), s, font=f, fill=fill)
        if sil:
            self.m.text((x, y), s, font=f, fill=255)

    def finish(self, pivot, border=5, grain_strength=0.035, shadow_blur=5, shadow_alpha=0.30):
        W, H = self.w, self.h
        P = border + shadow_blur * 2 + 4
        color = self.img.resize((W, H), Image.LANCZOS)
        mask = self.mask.resize((W, H), Image.LANCZOS)
        size = (W + 2 * P, H + 2 * P)
        m = Image.new("L", size, 0)
        m.paste(mask, (P, P))
        bm = m.filter(ImageFilter.MaxFilter(2 * border + 1)).filter(ImageFilter.GaussianBlur(0.7)) if border else m
        out = Image.new("RGBA", size, (0, 0, 0, 0))
        edge = Image.new("RGBA", size, PAPER_EDGE + (255,))
        edge.putalpha(bm)
        out.alpha_composite(edge)
        col = Image.new("RGBA", size, (0, 0, 0, 0))
        col.paste(color, (P, P))
        out.alpha_composite(col)
        out = grain(out, grain_strength)
        sh = Image.new("RGBA", size, SHADOW_RGB + (255,))
        sh.putalpha(bm.filter(ImageFilter.GaussianBlur(shadow_blur)).point(lambda v: int(v * shadow_alpha)))
        return Sprite(out, (pivot[0] + P, pivot[1] + P), sh)


def _composite_clipped(base, img, x, y):
    """alpha_composite that tolerates sprites hanging off the canvas."""
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1 = min(img.width, base.width - x)
    sy1 = min(img.height, base.height - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    if (sx0, sy0, sx1, sy1) != (0, 0, img.width, img.height):
        img = img.crop((sx0, sy0, sx1, sy1))
    base.alpha_composite(img, (x + sx0, y + sy0))


def _transform(img, pivot, angle, sx, sy, alpha):
    px, py = pivot
    if sx != 1 or sy != 1:
        img = img.resize((max(1, int(img.width * sx)), max(1, int(img.height * sy))), Image.BICUBIC)
        px, py = px * sx, py * sy
    if angle:
        w, h = img.size
        R = int(math.ceil(max(math.hypot(px, py), math.hypot(w - px, py),
                              math.hypot(px, h - py), math.hypot(w - px, h - py)))) + 2
        pad = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
        pad.paste(img, (int(round(R - px)), int(round(R - py))))
        img = pad.rotate(angle, resample=Image.BICUBIC)
        px, py = R, R
    if alpha < 1:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    return img, px, py


SHADOW_OFFSET = (7, 10)


def place(base, spr, at, angle=0.0, scale=1.0, alpha=1.0, sx=None, sy=None, shadow=True):
    """Draw sprite so its pivot lands on `at`, rotated `angle` degrees CCW about the pivot."""
    if alpha <= 0.003:
        return
    sxv = scale if sx is None else sx * scale
    syv = scale if sy is None else sy * scale
    if shadow and spr.shadow is not None:
        sh, px, py = _transform(spr.shadow, spr.pivot, angle, sxv, syv, alpha)
        _composite_clipped(base, sh, at[0] - px + SHADOW_OFFSET[0], at[1] - py + SHADOW_OFFSET[1])
    img, px, py = _transform(spr.img, spr.pivot, angle, sxv, syv, alpha)
    _composite_clipped(base, img, at[0] - px, at[1] - py)


def rot(vx, vy, angle_deg):
    """Rotate a screen vector CCW (as seen on screen, y pointing down)."""
    a = math.radians(angle_deg)
    return vx * math.cos(a) + vy * math.sin(a), -vx * math.sin(a) + vy * math.cos(a)


# easing
def clamp01(t):
    return 0.0 if t < 0 else 1.0 if t > 1 else t


def ease_in_out(t):
    t = clamp01(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_out_back(t, s=1.70158):
    t = clamp01(t)
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def seg(t, t0, t1):
    """0..1 progress of t through [t0, t1]."""
    return clamp01((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)


def lerp(a, b, t):
    return a + (b - a) * t


def star_pts(cx, cy, r_out, r_in, n=5, rot_deg=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot_deg + i * 180 / n)
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def spiky_ellipse_pts(cx, cy, rx, ry, spike, n=22):
    pts = []
    for i in range(2 * n):
        a = 2 * math.pi * i / (2 * n)
        k = spike if i % 2 == 0 else -spike * 0.2
        pts.append((cx + (rx + k) * math.cos(a), cy + (ry + k) * math.sin(a)))
    return pts


def polyline_point(pts, d):
    """Point at distance d along a polyline."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if d <= L and L > 0:
            k = d / L
            return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        d -= L
    return pts[-1]


def polyline_length(pts):
    return sum(math.hypot(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in zip(pts, pts[1:]))


def smooth_curve(p0, p1, p2, n=24):
    """Quadratic Bezier from p0 to p2 bending towards p1."""
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return out
