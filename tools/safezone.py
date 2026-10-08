"""Shorts safe zones (M42, audit M5): YouTube's buttons and caption cover the bottom 19% of a vertical Short and the
right 12% between 50% and 90% of the height; nothing important may sit there.

In a Short script's --check (handover_check needs a `safezone <t>` line at every `keysize <t>` time):
    import safezone as SZ                                   (tools/ on sys.path)
    m = SZ.to_frame(mask, RES, (CAM.ox, CAM.oy), c, z)      a canvas mask -> the 1080x1920 output frame (film()'s crop)
    lines.append(SZ.line(t, "tea light", m))                'safezone 24.30 tea light ok' or '... FAIL right 3.1% ...'
A mask is a PIL "L" image (>0 = the object); a 4-tuple is taken as a bounding box in output-frame pixels.

On a still, for the Lead's look at a key sheet:
    python3 tools/safezone.py --overlay frame.png [out.png]   draws the two zones in red
"""
import sys

import numpy as np
from PIL import Image, ImageDraw

W, H = 1080, 1920
BOTTOM = (0, round(0.81 * H), W, H)                          # x0, y0, x1, y1
RIGHT = (round(0.88 * W), round(0.50 * H), W, round(0.90 * H))
ZONES = (("bottom", BOTTOM), ("right", RIGHT))


def to_frame(mask, res, origin, centre, zoom, size=(W, H)):
    """A mask drawn on the camera canvas (size*res px, world origin `origin`) -> the output frame, cropped exactly
    as a vertical film() does: a window of size/zoom around `centre`, clamped inside the canvas."""
    w, h = size[0] / zoom, size[1] / zoom
    x0 = min(max(centre[0] - w / 2, origin[0]), origin[0] + size[0] - w)
    y0 = min(max(centre[1] - h / 2, origin[1]), origin[1] + size[1] - h)
    box = ((x0 - origin[0]) * res, (y0 - origin[1]) * res, (x0 + w - origin[0]) * res, (y0 + h - origin[1]) * res)
    return mask.resize(size, Image.NEAREST, box=box)


def overlap(obj):
    """{zone: % of the object's pixels inside it}; a bbox counts its area."""
    if isinstance(obj, tuple):
        a = np.zeros((H, W), bool)
        x0, y0, x1, y1 = (int(round(v)) for v in obj)
        a[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
    else:
        a = np.asarray(obj.convert("L")) > 0
    n = a.sum()
    if not n:
        return None
    return {name: 100.0 * a[z[1]:z[3], z[0]:z[2]].sum() / n for name, z in ZONES}


def line(t, name, obj):
    o = overlap(obj)
    if o is None:
        return f"safezone {t:.2f} {name} FAIL not in frame"
    bad = [f"{k} {v:.1f}%" for k, v in o.items() if v > 0]
    return f"safezone {t:.2f} {name} " + ("ok" if not bad else "FAIL " + ", ".join(bad) + " of its pixels")


def overlay(src, out):
    im = Image.open(src).convert("RGB")
    sx, sy = im.width / W, im.height / H
    d = ImageDraw.Draw(im, "RGBA")
    for _, z in ZONES:
        d.rectangle([z[0] * sx, z[1] * sy, z[2] * sx - 1, z[3] * sy - 1], fill=(255, 0, 0, 70), outline=(255, 0, 0))
    im.save(out)
    print("wrote", out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "--overlay":
        overlay(a[1], a[2] if len(a) > 2 else a[1].rsplit(".", 1)[0] + "_zones.png")
    else:
        sys.exit(__doc__)
