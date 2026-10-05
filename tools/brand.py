"""Channel art: YouTube banner (2560x1440, safe area 1546x423 centred) and profile picture (800x800).

    python3 tools/brand.py   -> output/brand/banner.png, output/brand/profile.png
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image, ImageDraw  # noqa: E402

import scene  # noqa: E402
from characters import Character, crinkle_head, snip_ear, snip_face  # noqa: E402
from paperlib import Cut, grain, heart_pts, place, star_pts  # noqa: E402

OUT = os.path.join(ROOT, "output", "brand")
BLUE, YELLOW, BROWN = (72, 172, 230), (255, 190, 48), (214, 118, 58)


def wall(w, h, color=scene.WALL, dot=scene.WALL_DOT):
    img = Image.new("RGBA", (w * 2, h * 2), color + (255,))
    d = ImageDraw.Draw(img)
    for row in range(h // 52 + 2):
        for col in range(w // 60 + 2):
            x, y = (col * 240 + (120 if row % 2 else 0)), row * 208 + 80
            d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=dot)
    return grain(img.resize((w, h), Image.LANCZOS), 0.035)


def title_cut(size=150, gap=34):
    from paperlib import round_font
    f = round_font(size)
    parts = (("Snip", BLUE), ("&", YELLOW), ("Crinkle", BROWN))
    widths = [f.getbbox(w)[2] - f.getbbox(w)[0] for w, _ in parts]
    total = sum(widths) + gap * (len(parts) - 1)
    c = Cut(int(total) + 60, int(size * 1.6))
    x = 30
    for (word, col), w in zip(parts, widths):
        c.text(word, x + w / 2, size * 0.8, size, col)
        x += w + gap
    return c.finish(pivot=((total + 60) / 2, size * 0.8), border=12)


def small(kind, color):
    c = Cut(120, 120)
    if kind == "heart":
        c.polygon(heart_pts(60, 64, 92), color)
    else:
        c.polygon(star_pts(60, 62, 54, 24), color)
    return c.finish(pivot=(60, 60), border=6)


def garland(width):
    c = Cut(width, 230)
    pts = [(x, 40 + 70 * math.sin(math.pi * x / width)) for x in range(0, width + 1, 20)]
    c.line(pts, 6, (150, 110, 90))
    for i, x in enumerate(range(70, width, 130)):
        y = 40 + 70 * math.sin(math.pi * x / width)
        c.polygon([(x - 50, y), (x + 50, y), (x, y + 110)], scene.FLAG_COLORS[i % 4])
    return c.finish(pivot=(0, 0), border=5)


def banner():
    W, H = 2560, 1440
    b = wall(W, H)
    place(b, garland(W), (0, 150))
    # table strip along the bottom (outside the mobile safe area)
    t = Cut(2600, 360)
    t.rrect(0, 0, 2600, 70, 14, scene.WOOD_TOP)
    t.rrect(0, 56, 2600, 360, 0, scene.WOOD_FRONT)
    place(b, t.finish(pivot=(0, 0)), (-20, 1150))
    # mobile safe area 1546x423 centred: x 507..2053, y 508..931 — title AND both faces live inside it
    title = title_cut()
    place(b, title, (1280, 720))
    half = (title.img.width - 2 * 30) / 2
    k = 0.72
    face, ear = snip_face("happy", "grin").scaled(k), snip_ear().scaled(k)
    sx, sy = 1280 - half - 135, 900
    for (ox, oy), tilt in (((-50, -180), 14), ((50, -180), -4)):
        place(b, ear, (sx + ox * k, sy + oy * k), angle=tilt)
    place(b, face, (sx, sy), angle=6)
    place(b, crinkle_head("happy", "grin").scaled(0.7), (1280 + half + 140, 900), angle=-6)
    for kind, col, x, y, s in (("heart", (240, 72, 98), 1280 - half + 40, 560, 0.45),
                               ("star", YELLOW, 1280 + half - 40, 565, 0.45),
                               ("star", BLUE, 1280 - 120, 880, 0.35), ("heart", (255, 120, 150), 1280 + 140, 885, 0.35)):
        place(b, small(kind, col), (x, y), scale=s, angle=-12 if x < 1280 else 12)
    return b.convert("RGB")


def profile():
    S = 800
    p = Image.new("RGBA", (S, S), (255, 214, 92, 255))
    p = grain(p, 0.03)
    d = ImageDraw.Draw(p)
    d.ellipse([60, 60, S - 60, S - 60], fill=(255, 226, 130))
    k = 1.25
    face = snip_face("happy", "grin").scaled(k)
    ear = snip_ear().scaled(k)
    sx, sy = 300, 610
    for (ox, oy), tilt in (((-50, -180), 12), ((50, -180), -6)):
        place(p, ear, (sx + ox * k, sy + oy * k), angle=tilt)
    place(p, face, (sx, sy))
    place(p, crinkle_head("happy", "grin").scaled(1.2), (530, 660))
    return p.convert("RGB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    banner().save(os.path.join(OUT, "banner.png"), optimize=True)
    profile().save(os.path.join(OUT, "profile.png"), optimize=True)
    print("wrote", OUT)
