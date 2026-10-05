"""High-resolution paper cut-outs (opt-in; Episodes 1-10 keep using paperlib.Cut at 1x).

RCut has the same drawing API as paperlib.Cut and takes the same design coordinates, but renders the
finished sprite at `k` times the pixel size (default: the global RES). Drawing a world at RES=2 and
downscaling to 1920x1080 gives crisp close-ups up to 2x zoom, instead of blurry upscales.

    import hires
    hires.set_res(2)                 # before building any sprites
    c = hires.RCut(300, 290)         # design units, as before
    c.ellipse(150, 150, 140, 122, fill)
    spr = c.finish(pivot=(150, 260)) # pixels are 2x; pivot is in real (2x) pixels
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paperlib  # noqa: E402
from paperlib import PAPER_EDGE, ROUND_FONT, SHADOW_RGB, SS, Sprite, ellipse_pts, grain, round_font  # noqa: E402

RES = 1.0


def set_res(r):
    """Set the render scale for every sprite built afterwards (and the drop-shadow offset)."""
    global RES
    RES = float(r)
    paperlib.SHADOW_OFFSET = (7 * RES, 10 * RES)


class RCut:
    def __init__(self, w, h, k=None):
        self.k = RES if k is None else float(k)
        self.w, self.h = w, h
        self.f = SS * self.k
        size = (max(1, int(math.ceil(w * self.f))), max(1, int(math.ceil(h * self.f))))
        self.img = Image.new("RGBA", size, (0, 0, 0, 0))
        self.mask = Image.new("L", size, 0)
        self.d = ImageDraw.Draw(self.img)
        self.m = ImageDraw.Draw(self.mask)

    def _s(self, seq):
        return [v * self.f for v in seq]

    def _p(self, pts):
        return [(x * self.f, y * self.f) for x, y in pts]

    def ellipse(self, cx, cy, rx, ry, fill, sil=True, theta=0):
        if theta:
            return self.polygon(ellipse_pts(cx, cy, rx, ry, theta), fill, sil)
        box = self._s([cx - rx, cy - ry, cx + rx, cy + ry])
        self.d.ellipse(box, fill=fill)
        if sil:
            self.m.ellipse(box, fill=255)

    def rrect(self, x0, y0, x1, y1, r, fill, sil=True):
        box = self._s([x0, y0, x1, y1])
        self.d.rounded_rectangle(box, r * self.f, fill=fill)
        if sil:
            self.m.rounded_rectangle(box, r * self.f, fill=255)

    def polygon(self, pts, fill, sil=True):
        p = self._p(pts)
        self.d.polygon(p, fill=fill)
        if sil:
            self.m.polygon(p, fill=255)

    def line(self, pts, width, fill, sil=False):
        p = self._p(pts)
        w = max(1, int(width * self.f))
        r = w / 2
        for dr in [self.d] + ([self.m] if sil else []):
            col = 255 if dr is self.m else fill
            dr.line(p, fill=col, width=w, joint="curve")
            for x, y in (p[0], p[-1]):
                dr.ellipse([x - r, y - r, x + r, y + r], fill=col)

    def arc(self, cx, cy, rx, ry, start, end, width, fill):
        self.d.arc(self._s([cx - rx, cy - ry, cx + rx, cy + ry]), start, end, fill=fill,
                   width=max(1, int(width * self.f)))

    def chord(self, cx, cy, rx, ry, start, end, fill, sil=False):
        box = self._s([cx - rx, cy - ry, cx + rx, cy + ry])
        self.d.chord(box, start, end, fill=fill)
        if sil:
            self.m.chord(box, start, end, fill=255)

    def text(self, s, cx, cy, size, fill, sil=True):
        f = round_font(size * self.f)
        bb = self.d.textbbox((0, 0), s, font=f)
        x = cx * self.f - (bb[0] + bb[2]) / 2
        y = cy * self.f - (bb[1] + bb[3]) / 2
        self.d.text((x, y), s, font=f, fill=fill)
        if sil:
            self.m.text((x, y), s, font=f, fill=255)

    def finish(self, pivot, border=5, grain_strength=0.035, shadow_blur=5, shadow_alpha=0.30):
        k = self.k
        W, H = max(1, int(round(self.w * k))), max(1, int(round(self.h * k)))
        b = border * k
        blur = shadow_blur * k
        P = int(math.ceil(b + blur * 2 + 4 * k))
        color = self.img.resize((W, H), Image.LANCZOS)
        mask = self.mask.resize((W, H), Image.LANCZOS)
        size = (W + 2 * P, H + 2 * P)
        m = Image.new("L", size, 0)
        m.paste(mask, (P, P))
        bm = m.filter(ImageFilter.MaxFilter(2 * int(round(b)) + 1)).filter(ImageFilter.GaussianBlur(0.7 * k)) if border else m
        out = Image.new("RGBA", size, (0, 0, 0, 0))
        edge = Image.new("RGBA", size, PAPER_EDGE + (255,))
        edge.putalpha(bm)
        out.alpha_composite(edge)
        col = Image.new("RGBA", size, (0, 0, 0, 0))
        col.paste(color, (P, P))
        out.alpha_composite(col)
        out = grain(out, grain_strength)
        sh = Image.new("RGBA", size, SHADOW_RGB + (255,))
        sh.putalpha(bm.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * shadow_alpha)))
        return Sprite(out, (pivot[0] * k + P, pivot[1] * k + P), sh)


def Cut(w, h):
    """Drop-in for paperlib.Cut that follows the global RES."""
    return RCut(w, h)


__all__ = ["RES", "set_res", "RCut", "Cut", "ROUND_FONT"]
