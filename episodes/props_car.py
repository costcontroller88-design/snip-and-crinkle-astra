"""Car props for Episode 9 "Buckle Up?": a big cute car seen in cut-away from the side (the near
side is removed like a doll's house), high-back booster seats, three-point seat belts (strap,
silver tongue, red-button buckle), the grown-up driver's arm with grip / pointing / thumbs-up hands,
a steering wheel, scrolling scenery (home street -> trees -> beach), a road, choice-bubble icons,
a beach thought bubble and a few new synthesized sounds.

Everything is drawn as paper cut-outs with paperlib (no emoji, no fonts, no third-party art).
Scene coordinates match the screen at the default framing (zoom 1).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audio as A  # noqa: E402
import props_street as PS  # noqa: E402
import scene  # noqa: E402
from paperlib import Cut, Sprite, grain, mix, place, star_pts  # noqa: E402

W, H = scene.W, scene.H

# ---------------------------------------------------------------- layout (scene coordinates)
BASE = 1330                 # booster cushion top = where the friends sit (character base_y)
ROOF_OUT = 450              # outer roof line
ROOF_IN = 500               # inside of the roof (Snip's ears bonk here)
WIN_TOP, WIN_BOT = 565, 965
NEAR_TOP = 1372             # top edge of the near-side lower door panel (drawn in front)
CAR_BOT = 1528
WHEELS = ((215, 1546), (905, 1546))
WHEEL_R = 92
ROAD_Y = 1636               # where the tyres touch the road
STEER = (1012, 868)         # steering wheel centre
HOUSE_BASE = 1010           # houses stand here (hidden behind the car body)

# ---------------------------------------------------------------- colours
BODY = (236, 92, 86)
BODY_DARK = mix(BODY, (0, 0, 0), 0.18)
BODY_LIGHT = mix(BODY, (255, 255, 255), 0.25)
WALL_IN = (250, 236, 210)
WALL_IN_DARK = (236, 214, 182)
HEADLINER = (255, 247, 232)
BENCH = (122, 140, 188)
BENCH_DARK = (102, 118, 164)
SN_BOOST = (255, 198, 66)
CR_BOOST = (114, 198, 156)
WEB = (54, 62, 98)           # seat-belt webbing
WEB_LINE = (104, 114, 160)
SILVER = (222, 228, 238)
SILVER_DARK = (150, 160, 182)
RECEIVER = (66, 68, 84)
RED_BTN = (240, 70, 70)
SKIN = scene.SKIN
SKIN_LINE = (182, 126, 92)
SLEEVE = scene.SLEEVE
SKY_TOP = (132, 200, 244)
SKY_LOW = (206, 238, 252)
ROAD = (108, 116, 136)
SNIP_FUR = (226, 214, 242)
SNIP_TEE = (80, 182, 235)
SNIP_EAR_IN = (247, 172, 198)


# ---------------------------------------------------------------- sky, clouds, scenery, road
def sky():
    a = np.zeros((H, W, 3), np.float32)
    t = np.clip(np.linspace(0, 1.25, H), 0, 1)[:, None]
    for i in range(3):
        a[..., i] = SKY_TOP[i] + (SKY_LOW[i] - SKY_TOP[i]) * t
    img = grain(Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA"), 0.02)
    place(img, PS._sun().scaled(0.8), (900, 150))
    return img


def clouds(width):
    img = Image.new("RGBA", (width, 520), (0, 0, 0, 0))
    for i, x in enumerate(range(80, width, 430)):
        y = 120 + 110 * ((i * 7) % 3) / 2
        place(img, PS._cloud().scaled(0.75 + 0.2 * ((i * 5) % 3) / 2), (x, y))
    return img


def _umbrella(h=330):
    c = Cut(300, h + 30)
    cx = 150
    c.rrect(cx - 7, 60, cx + 7, h + 20, 6, (236, 236, 240))
    cols = ((240, 92, 88), (255, 255, 255))
    for i in range(6):
        a0, a1 = math.pi + i * math.pi / 6, math.pi + (i + 1) * math.pi / 6
        pts = [(cx, 20)] + [(cx + 140 * math.cos(a0 + (a1 - a0) * k / 8), 104 + 84 * math.sin(a0 + (a1 - a0) * k / 8))
                            for k in range(9)]
        c.polygon(pts, cols[i % 2])
    c.ellipse(cx, 18, 10, 10, (255, 214, 64))
    return c.finish(pivot=(cx, h + 20), border=5, shadow_alpha=0.2)


def _palm(h=640):
    c = Cut(420, h + 40)
    pts = [(210 + 40 * math.sin(math.pi * k / 20) * (k / 20), h + 20 - (h - 90) * k / 20) for k in range(21)]
    c.line(pts, 34, (190, 140, 92), sil=True)
    for k in range(2, 20, 3):
        x, y = pts[k]
        c.line([(x - 16, y), (x + 16, y + 6)], 4, (160, 112, 70))
    tx, ty = pts[-1]
    leaf = (90, 176, 104)
    for ang in (-160, -120, -60, -20, 200, 250):
        a = math.radians(ang)
        lp = [(tx + 150 * math.cos(a) * k / 10, ty + 150 * math.sin(a) * k / 10 + 50 * (k / 10) ** 2) for k in range(11)]
        c.line(lp, 30, leaf if ang % 40 else mix(leaf, (40, 100, 60), 0.3), sil=True)
    for dx in (-14, 14):
        c.ellipse(tx + dx, ty + 18, 16, 16, (150, 100, 60))
    return c.finish(pivot=(pts[0][0], h + 20), border=5, shadow_alpha=0.2)


def _bucket():
    c = Cut(120, 120)
    c.polygon([(20, 40), (100, 40), (90, 112), (30, 112)], (84, 168, 238))
    c.arc(60, 40, 40, 34, 180, 360, 6, (60, 120, 190))
    c.rrect(16, 34, 104, 46, 6, (70, 140, 210))
    return c.finish(pivot=(60, 112), border=4, shadow_alpha=0.2)


BEACH_X = 1150          # strip x where the beach starts (just off screen at the start)
SCENE_W = 2800          # scenery strip width


def scenery():
    """Houses, trees and then the beach on a transparent strip SCENE_W wide (scene y as-is).
    At scroll offset o, strip x = scene x + o."""
    img = Image.new("RGBA", (SCENE_W, 1100), (0, 0, 0, 0))
    # home street: soft pastel houses and trees
    houses = [(-60, 330, 400, (255, 226, 214), (232, 128, 112), (150, 186, 236), 0),
              (320, 280, 330, (214, 236, 246), (110, 146, 206), (240, 150, 110), 2),
              (660, 290, 420, (255, 240, 200), (226, 150, 92), (120, 186, 140), 1)]
    for x, w, h, wall, roof, door, kind in houses:
        place(img, PS._house(w, h, wall, roof, door, kind), (x, HOUSE_BASE))
    for x, h, col in ((290, 470, (116, 190, 112)), (630, 420, (130, 200, 120)), (1010, 520, (124, 194, 116))):
        place(img, PS._tree(h, col), (x, HOUSE_BASE + 4))
    place(img, PS._hedge(BEACH_X + 40), (-20, HOUSE_BASE - 60))
    # the beach: the sea rises high enough to be seen above the car roof (horizon y=320), with a sandy
    # shoreline running diagonally up from the left, a sailboat, gulls; palms and umbrellas in front
    d = ImageDraw.Draw(img)
    hz, sand_y = 320, 885
    shore = [(BEACH_X - 60, 1100), (BEACH_X - 60, 700), (BEACH_X + 300, hz)]
    d.polygon(shore + [(SCENE_W, hz), (SCENE_W, 1100)], fill=(64, 168, 222, 255))
    d.polygon([(BEACH_X + 300, hz), (SCENE_W, hz), (SCENE_W, hz + 16), (BEACH_X + 286, hz + 16)], fill=(44, 140, 200, 255))
    for row, yy in enumerate(range(hz + 50, 860, 70)):
        for x in range(BEACH_X + 40 + 55 * (row % 2), SCENE_W, 120):
            if x > BEACH_X - 60 + (1100 - yy) * 0.0 and yy > hz + (BEACH_X + 300 - x) * (700 - hz) / 360:
                d.arc([x, yy - 12, x + 60, yy + 12], 200, 340, fill=(240, 250, 255, 255), width=5)
    d.polygon([(BEACH_X - 60, 1100), (BEACH_X - 60, 700), (BEACH_X + 300, hz), (BEACH_X + 470, hz),
               (BEACH_X + 140, 1100)], fill=(250, 220, 150, 255))                      # sandy headland
    d.line([(BEACH_X + 470, hz), (BEACH_X + 140, 1100)], fill=(244, 206, 130, 255), width=8)
    d.polygon([(BEACH_X - 120, 1100), (BEACH_X + 60, sand_y + 6), (SCENE_W, sand_y), (SCENE_W, 1100)],
              fill=(250, 220, 150, 255))
    d.rectangle([BEACH_X, sand_y, SCENE_W, sand_y + 10], fill=(244, 206, 130, 255))
    # sailboat on the horizon and a few gulls
    bx = BEACH_X + 760
    d.polygon([(bx - 60, hz - 4), (bx + 60, hz - 4), (bx + 44, hz + 18), (bx - 44, hz + 18)], fill=(232, 96, 90, 255))
    d.polygon([(bx - 4, hz - 8), (bx - 4, hz - 120), (bx - 56, hz - 12)], fill=(255, 250, 240, 255))
    d.polygon([(bx + 4, hz - 8), (bx + 4, hz - 96), (bx + 44, hz - 12)], fill=(255, 214, 120, 255))
    for gx, gy in ((BEACH_X + 420, 190), (BEACH_X + 480, 160), (BEACH_X + 1040, 220)):
        d.arc([gx - 26, gy - 10, gx, gy + 14], 200, 340, fill=(90, 100, 120, 255), width=5)
        d.arc([gx, gy - 10, gx + 26, gy + 14], 200, 340, fill=(90, 100, 120, 255), width=5)
    img = grain(img, 0.025)
    place(img, _palm(620), (BEACH_X + 130, 1000))
    place(img, _umbrella(320), (BEACH_X + 560, 960))
    place(img, _bucket(), (BEACH_X + 700, 950))
    place(img, _umbrella(280), (BEACH_X + 980, 950))
    place(img, _palm(560), (BEACH_X + 1080, 1010))
    return img


DASH_P = 180


def road():
    """Road under the car (a little wider than the screen so the dashes can scroll by DASH_P)."""
    w = W + DASH_P
    img = Image.new("RGBA", (w, H - 1500), ROAD + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 40], fill=(226, 222, 214, 255))          # far sidewalk strip
    d.rectangle([0, 40, w, 56], fill=(244, 240, 232, 255))         # curb
    d.rectangle([0, 56, w, 64], fill=(176, 170, 164, 255))
    for x in range(0, w, DASH_P):
        d.rounded_rectangle([x, 270, x + 100, 286], 7, fill=(246, 246, 240, 255))
    return grain(img, 0.03)


# ---------------------------------------------------------------- the car
def car_back():
    """Far side of the cabin seen through the removed near side: roof, far wall with window
    holes (scenery shows through), seats, dashboard. Pivot = scene (0, 0)."""
    ox, oy = 60, 20                       # canvas = scene + (ox, oy - 430)
    cw, ch = 1220, 1140
    c = Cut(cw, ch)
    S = lambda x, y: (x + ox, y - 430 + oy)  # noqa: E731

    def poly(pts, col, sil=True):
        c.polygon([S(x, y) for x, y in pts], col, sil)

    def rr(x0, y0, x1, y1, r, col, sil=True):
        a, b = S(x0, y0), S(x1, y1)
        c.rrect(a[0], a[1], b[0], b[1], r, col, sil)

    # outer shell silhouette (roof + rear + body) in the body colour
    rr(-40, ROOF_OUT, 1200, CAR_BOT, 150, BODY)
    c.d.polygon([S(x, y) for x, y in ((880, ROOF_OUT - 5), (1210, ROOF_OUT - 5), (1210, 770))], fill=(0, 0, 0, 0))
    c.m.polygon([(x * 3, y * 3) for x, y in (S(880, ROOF_OUT - 5), S(1210, ROOF_OUT - 5), S(1210, 770))], fill=0)
    # inside: headliner + far wall
    rr(0, ROOF_IN, 1200, NEAR_TOP + 60, 110, WALL_IN, sil=False)
    rr(0, ROOF_IN, 1200, WIN_TOP - 6, 40, HEADLINER, sil=False)
    rr(0, WIN_BOT + 30, 1200, WIN_BOT + 52, 10, WALL_IN_DARK, sil=False)      # armrest strip
    # window frames (white) then cut the glass holes
    wins = [(64, 470, 70), (500, 860, 26)]
    for x0, x1, r in wins:
        rr(x0 - 10, WIN_TOP - 10, x1 + 10, WIN_BOT + 10, r + 8, (255, 255, 255), sil=False)
    # front door window (slanted front edge under the windshield)
    poly([(890, WIN_TOP + 30), (945, WIN_TOP + 30), (1200, 800), (1200, WIN_BOT + 10), (890, WIN_BOT + 10)],
         (255, 255, 255), sil=False)
    holes = []
    for x0, x1, r in wins:
        holes.append(("r", (S(x0, WIN_TOP), S(x1, WIN_BOT), r)))
    holes.append(("p", [S(x, y) for x, y in ((900, WIN_TOP + 40), (940, WIN_TOP + 40), (1200, 812), (1200, WIN_BOT),
                                             (900, WIN_BOT))]))
    for kind, data in holes:
        if kind == "r":
            (a0, b0), (a1, b1), r = data
            box = [a0 * 3, b0 * 3, a1 * 3, b1 * 3]
            c.d.rounded_rectangle(box, r * 3, fill=(0, 0, 0, 0))
            c.m.rounded_rectangle(box, r * 3, fill=0)
        else:
            p = [(x * 3, y * 3) for x, y in data]
            c.d.polygon(p, fill=(0, 0, 0, 0))
            c.m.polygon(p, fill=0)
    # rear bench back (Snip) and middle bench back (Crinkle)
    rr(70, 930, 480, NEAR_TOP + 40, 40, BENCH, sil=False)
    rr(500, 930, 875, NEAR_TOP + 40, 40, BENCH, sil=False)
    for x0, x1 in ((70, 480), (500, 875)):
        for k in range(1, 3):
            xx = x0 + (x1 - x0) * k / 3
            c.line([S(xx, 950), S(xx, NEAR_TOP + 20)], 4, BENCH_DARK)
    # dashboard at the front
    rr(985, 905, 1220, 1060, 40, (92, 98, 122), sil=False)
    rr(985, 905, 1220, 930, 12, (120, 128, 154), sil=False)
    # door handles / little details on the far wall
    rr(520, 1000, 590, 1016, 8, WALL_IN_DARK, sil=False)
    spr = c.finish(pivot=(ox, oy - 430), border=6, shadow_alpha=0.22)
    return spr


def glass():
    """Light blue glass tint with two highlight streaks for the window holes (pivot = scene (0,0))."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    md.rounded_rectangle([64, WIN_TOP, 470, WIN_BOT], 70, fill=255)
    md.rounded_rectangle([500, WIN_TOP, 860, WIN_BOT], 26, fill=255)
    md.polygon([(900, WIN_TOP + 40), (940, WIN_TOP + 40), (1200, 812), (1200, WIN_BOT), (900, WIN_BOT)], fill=255)
    tint = Image.new("RGBA", (W, H), (210, 236, 250, 46))
    img.paste(tint, (0, 0), m)
    streak = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(streak)
    for x0, wd in ((120, 40), (180, 16), (560, 36), (612, 14)):
        sd.polygon([(x0 + 120, WIN_TOP), (x0 + 120 + wd, WIN_TOP), (x0 + wd, WIN_BOT), (x0, WIN_BOT)], fill=70)
    streak = Image.fromarray(np.minimum(np.asarray(streak), np.asarray(m)))
    white = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    white.putalpha(streak)
    img.alpha_composite(white)
    return Sprite(img, (0, 0))


def car_front():
    """Near-side lower door panel (drawn in front of the seats), with wheel arches. Pivot = scene (0,0)."""
    ox, oy = 60, 20
    top = NEAR_TOP
    cw, chh = 1220, CAR_BOT - top + 60
    c = Cut(cw, chh)
    S = lambda x, y: (x + ox, y - top + oy)  # noqa: E731
    a, b = S(-40, top), S(1200, CAR_BOT)
    c.rrect(a[0], a[1], b[0], b[1], 60, BODY)
    a, b = S(-40, top), S(1200, top + 22)
    c.rrect(a[0], a[1], b[0], b[1], 10, BODY_LIGHT, sil=False)
    a, b = S(-36, CAR_BOT - 52), S(1200, CAR_BOT - 30)
    c.rrect(a[0], a[1], b[0], b[1], 8, BODY_DARK, sil=False)
    for x in (490, 880):
        c.line([S(x, top + 30), S(x, CAR_BOT - 60)], 4, BODY_DARK)
    for x in (400, 790):
        a, b = S(x, top + 52), S(x + 64, top + 68)
        c.rrect(a[0], a[1], b[0], b[1], 8, (255, 255, 255), sil=False)
    # rear light
    a, b = S(-36, top + 26), S(-6, top + 80)
    c.rrect(a[0], a[1], b[0], b[1], 10, (255, 196, 70), sil=False)
    # wheel arches (cut out)
    for wx, wy in WHEELS:
        cx, cy = S(wx, wy)
        r = WHEEL_R + 16
        c.d.ellipse([(cx - r) * 3, (cy - r) * 3, (cx + r) * 3, (cy + r) * 3], fill=(40, 40, 52, 255))
        c.m.ellipse([(cx - r) * 3, (cy - r) * 3, (cx + r) * 3, (cy + r) * 3], fill=255)
    return c.finish(pivot=(ox, oy - top), border=6, shadow_alpha=0.25)


def wheel():
    r = WHEEL_R
    c = Cut(2 * r + 20, 2 * r + 20)
    cx = cy = r + 10
    c.ellipse(cx, cy, r, r, (58, 60, 72))
    c.ellipse(cx, cy, r * 0.56, r * 0.56, (214, 218, 228), sil=False)
    for k in range(5):
        a = k * 2 * math.pi / 5
        c.line([(cx, cy), (cx + r * 0.48 * math.cos(a), cy + r * 0.48 * math.sin(a))], 9, (170, 176, 194))
    c.ellipse(cx, cy, r * 0.16, r * 0.16, BODY, sil=False)
    c.ellipse(cx + r * 0.36, cy - r * 0.2, 7, 7, (255, 255, 255), sil=False)
    return c.finish(pivot=(cx, cy), border=4, shadow_alpha=0.25)


def car_shadow():
    m = Image.new("L", (1400, 120), 0)
    ImageDraw.Draw(m).ellipse([60, 30, 1340, 90], fill=120)
    img = Image.new("RGBA", m.size, (40, 40, 56, 255))
    img.putalpha(m.filter(ImageFilter.GaussianBlur(14)))
    return Sprite(img, (700, 60))


def steering_wheel():
    c = Cut(200, 300)
    c.line([(110, 160), (196, 250)], 26, (80, 84, 104), sil=True)                # column to the dashboard
    pts = [(100 + 34 * math.cos(a) * math.cos(0.3) - 112 * math.sin(a) * math.sin(0.3),
            150 + 34 * math.cos(a) * math.sin(0.3) + 112 * math.sin(a) * math.cos(0.3))
           for a in np.linspace(0, 2 * math.pi, 50)]
    c.line(pts, 24, (70, 74, 92), sil=True)
    c.ellipse(108, 156, 22, 26, (92, 98, 122))
    return c.finish(pivot=(100, 150), border=4, shadow_alpha=0.25)


# ---------------------------------------------------------------- boosters
def booster_back(col, w=350, h=575):
    """High-back booster: back + head wings, with a red shoulder-belt guide on the left wing."""
    c = Cut(w + 20, h + 20)
    cx = (w + 20) / 2
    dark = mix(col, (0, 0, 0), 0.14)
    c.rrect(10, 10, w + 10, h + 10, 60, dark)
    c.rrect(36, 30, w - 16, h - 10, 46, col, sil=False)
    c.rrect(10, 10, 58, h * 0.48, 26, mix(col, (255, 255, 255), 0.18), sil=False)        # head wings
    c.rrect(w - 38, 10, w + 10, h * 0.48, 26, mix(col, (255, 255, 255), 0.18), sil=False)
    for k in (0.3, 0.55, 0.8):
        c.line([(70, h * k), (w - 50, h * k)], 4, dark)
    return c.finish(pivot=(cx, h + 10), border=5, shadow_alpha=0.22)


def booster_cushion(col, w=380):
    c = Cut(w + 20, 110)
    dark = mix(col, (0, 0, 0), 0.14)
    c.rrect(10, 10, w + 10, 100, 34, dark)
    c.rrect(16, 10, w + 4, 46, 22, col, sil=False)
    return c.finish(pivot=((w + 20) / 2, 26), border=5, shadow_alpha=0.25)


def guide_clip():
    c = Cut(70, 60)
    c.rrect(8, 8, 62, 52, 16, (232, 80, 74))
    c.rrect(20, 22, 50, 38, 6, (150, 40, 44), sil=False)
    return c.finish(pivot=(35, 30), border=4, shadow_alpha=0.25)


# ---------------------------------------------------------------- seat belt
_strap_cache = {}


def strap(p0, p1, width=32):
    """A straight paper strap of webbing from p0 to p1 (scene coords). Returns (sprite, at)."""
    key = (round(p0[0] / 2), round(p0[1] / 2), round(p1[0] / 2), round(p1[1] / 2), width)
    if key not in _strap_cache:
        x0, y0 = min(p0[0], p1[0]) - width, min(p0[1], p1[1]) - width
        w = int(abs(p1[0] - p0[0]) + 2 * width) + 2
        h = int(abs(p1[1] - p0[1]) + 2 * width) + 2
        c = Cut(w, h)
        a, b = (p0[0] - x0, p0[1] - y0), (p1[0] - x0, p1[1] - y0)
        c.line([a, b], width, WEB, sil=True)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L > 1:
            nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
            for s in (-0.28, 0.28):
                o = (nx * width * s, ny * width * s)
                c.line([(a[0] + o[0], a[1] + o[1]), (b[0] + o[0], b[1] + o[1])], 2.5, WEB_LINE)
        if len(_strap_cache) > 600:
            _strap_cache.clear()
        _strap_cache[key] = (c.finish(pivot=(0, 0), border=3, shadow_alpha=0.28, shadow_blur=4), (x0, y0))
    spr, (x0, y0) = _strap_cache[key]
    return spr, (x0, y0)


def draw_strap(f, p0, p1, width=32):
    spr, at = strap(p0, p1, width)
    place(f, spr, at)


def tongue():
    """The silver latch plate. Pivot = its tip (the end that clicks into the buckle); it points down."""
    c = Cut(70, 110)
    c.rrect(10, 8, 60, 52, 12, SILVER_DARK)
    c.rrect(14, 12, 56, 48, 10, SILVER, sil=False)
    c.rrect(22, 22, 48, 32, 4, (90, 96, 120), sil=False)           # slot for the webbing
    c.rrect(20, 48, 50, 100, 8, SILVER_DARK)
    c.rrect(24, 50, 46, 96, 6, SILVER, sil=False)
    c.ellipse(35, 82, 6, 6, (120, 128, 150), sil=False)
    c.ellipse(24, 18, 5, 3, (255, 255, 255), sil=False)
    return c.finish(pivot=(35, 98), border=4, shadow_alpha=0.3)


def receiver():
    """Buckle receiver on a short stalk. Pivot = the slot on top (where the tongue goes in)."""
    c = Cut(90, 190)
    c.rrect(30, 70, 60, 186, 10, (80, 82, 96))
    c.rrect(10, 8, 80, 96, 18, RECEIVER)
    c.rrect(22, 8, 68, 18, 5, (30, 30, 40), sil=False)
    c.rrect(22, 38, 68, 76, 12, RED_BTN, sil=False)
    c.ellipse(34, 48, 8, 5, (255, 170, 170), sil=False)
    return c.finish(pivot=(45, 12), border=4, shadow_alpha=0.3)


def glow(color=(255, 230, 120), r=90):
    yy, xx = np.mgrid[-r:r, -r:r]
    a = np.clip(1 - np.hypot(xx, yy) / r, 0, 1) ** 1.6 * 200
    img = np.zeros((2 * r, 2 * r, 4), np.uint8)
    img[..., :3] = color
    img[..., 3] = a.astype(np.uint8)
    return Sprite(Image.fromarray(img, "RGBA"), (r, r))


def dot(col=(255, 255, 255), r=9):
    c = Cut(2 * r + 12, 2 * r + 12)
    c.ellipse(r + 6, r + 6, r, r, col)
    return c.finish(pivot=(r + 6, r + 6), border=3, shadow_alpha=0.25)


def click_star(col=(255, 214, 64)):
    c = Cut(170, 170)
    c.polygon(star_pts(85, 85, 80, 34, 8, -90), col)
    c.polygon(star_pts(85, 85, 40, 18, 8, -68), (255, 255, 255), sil=False)
    return c.finish(pivot=(85, 85), border=4, shadow_alpha=0.15)


def bonk_star():
    c = Cut(150, 150)
    c.polygon(star_pts(75, 75, 70, 30, 5, -90), (255, 226, 92))
    c.ellipse(64, 66, 10, 7, (255, 255, 255), sil=False)
    return c.finish(pivot=(75, 75), border=4, shadow_alpha=0.15)


# ---------------------------------------------------------------- the grown-up's arm and hands
def sleeve(length=1300, thick=128):
    """Long sleeve, cuff at the left end (pivot), running right off the frame."""
    c = Cut(length, thick + 20)
    c.rrect(0, 10, length, thick + 10, 32, SLEEVE)
    c.rrect(0, 4, 44, thick + 16, 16, (244, 244, 248))
    return c.finish(pivot=(18, (thick + 20) / 2), border=5, shadow_alpha=0.25)


def _thumb_ellipse(c, cx, cy, rx, ry):
    c.ellipse(cx, cy, rx, ry, SKIN)


def hand_grip():
    """A fist gripping the wheel rim, knuckles to the left. Pivot = wrist (right side)."""
    c = Cut(190, 150)
    c.rrect(36, 28, 170, 124, 40, SKIN)
    for y in (46, 68, 90, 110):
        c.ellipse(42, y, 16, 13, SKIN)
    for y in (57, 79, 100):
        c.line([(34, y), (84, y)], 3, SKIN_LINE)
    c.ellipse(108, 32, 50, 16, SKIN)
    c.line([(70, 34), (140, 30)], 3, SKIN_LINE)
    return c.finish(pivot=(166, 76), border=4, shadow_alpha=0.28)


def hand_point():
    """Index finger pointing left. Pivot = wrist (right side)."""
    c = Cut(290, 150)
    c.rrect(126, 30, 270, 126, 40, SKIN)
    c.rrect(14, 34, 170, 68, 17, SKIN)                     # index finger
    c.ellipse(30, 48, 9, 6, (232, 182, 150), sil=False)    # nail
    for y in (82, 102, 120):
        c.ellipse(132, y, 18, 12, SKIN)
    for y in (92, 112):
        c.line([(118, y), (168, y)], 3, SKIN_LINE)
    c.ellipse(196, 28, 44, 15, SKIN)                       # thumb along the top
    return c.finish(pivot=(262, 78), border=4, shadow_alpha=0.28)


def hand_thumb():
    """Thumbs-up: a fist (knuckles left) with the thumb straight up. Pivot = wrist (right side)."""
    c = Cut(220, 250)
    c.rrect(46, 108, 196, 218, 40, SKIN)
    for y in (126, 150, 174, 198):
        c.ellipse(52, y, 18, 14, SKIN)
    for y in (138, 162, 186):
        c.line([(44, y), (100, y)], 3, SKIN_LINE)
    c.rrect(84, 14, 134, 128, 25, SKIN)                    # thumb up
    c.ellipse(109, 34, 13, 10, (232, 182, 150), sil=False)
    c.line([(86, 104), (132, 104)], 3, SKIN_LINE)
    return c.finish(pivot=(190, 164), border=5, shadow_alpha=0.28)


# ---------------------------------------------------------------- choice bubbles
def _mini_bunny(c, X, Y, s, arms_up=False, eyes="happy"):
    c.ellipse(X(-14), Y(-62), 9 * s, 24 * s, SNIP_FUR, sil=False, theta=-8)
    c.ellipse(X(14), Y(-62), 9 * s, 24 * s, SNIP_FUR, sil=False, theta=8)
    c.ellipse(X(-14), Y(-60), 4 * s, 15 * s, SNIP_EAR_IN, sil=False, theta=-8)
    c.ellipse(X(14), Y(-60), 4 * s, 15 * s, SNIP_EAR_IN, sil=False, theta=8)
    if arms_up:
        c.line([(X(-18), Y(4)), (X(-36), Y(-20))], 10 * s, SNIP_FUR)
        c.line([(X(18), Y(4)), (X(36), Y(-20))], 10 * s, SNIP_FUR)
    c.ellipse(X(0), Y(14), 27 * s, 25 * s, SNIP_TEE, sil=False)
    c.polygon(star_pts(X(0), Y(16), 10 * s, 4.5 * s), (255, 214, 64), sil=False)
    c.ellipse(X(0), Y(-26), 27 * s, 23 * s, SNIP_FUR, sil=False)
    for ex in (-10, 10):
        if eyes == "happy":
            c.arc(X(ex), Y(-26), 5 * s, 4 * s, 200, 340, 3 * s, (38, 32, 44))
        else:
            c.ellipse(X(ex), Y(-28), 3.5 * s, 4.5 * s, (38, 32, 44), sil=False)
    c.ellipse(X(0), Y(-17), 3.5 * s, 2.5 * s, (240, 118, 160), sil=False)
    c.chord(X(0), Y(-13), 7 * s, 7 * s, 0, 180, (120, 40, 60))


def draw_bounce_icon(c, cx, cy, size):
    """Snip bouncing up off the seat (no belt), with motion lines."""
    s = size / 140
    X = lambda v: cx + v * s  # noqa: E731
    Y = lambda v: cy + v * s  # noqa: E731
    c.rrect(X(-58), Y(46), X(58), Y(70), 10 * s, SN_BOOST, sil=False)
    for dx in (-22, 0, 22):
        c.line([(X(dx), Y(36)), (X(dx), Y(44))], 4 * s, (160, 170, 190))
    for sx in (-1, 1):
        c.line([(X(52 * sx), Y(4)), (X(52 * sx), Y(-30))], 5 * s, (160, 170, 190))
        c.line([(X(52 * sx - 8), Y(-20)), (X(52 * sx), Y(-30)), (X(52 * sx + 8), Y(-20))], 5 * s, (160, 170, 190))
    _mini_bunny(c, X, lambda v: Y(v - 12), s, arms_up=True)


def draw_buckle_icon(c, cx, cy, size):
    """Snip sitting in the booster with the belt across shoulder and lap, buckled."""
    s = size / 140
    X = lambda v: cx + v * s  # noqa: E731
    Y = lambda v: cy + v * s  # noqa: E731
    c.rrect(X(-48), Y(-56), X(48), Y(50), 16 * s, SN_BOOST, sil=False)
    c.rrect(X(-58), Y(40), X(58), Y(66), 10 * s, mix(SN_BOOST, (0, 0, 0), 0.12), sil=False)
    _mini_bunny(c, X, lambda v: Y(v + 8), s, eyes="open")
    c.line([(X(-28), Y(-2)), (X(22), Y(38))], 9 * s, WEB)                 # shoulder belt
    c.line([(X(-30), Y(34)), (X(22), Y(38))], 9 * s, WEB)                 # lap belt
    c.rrect(X(16), Y(32), X(34), Y(60), 4 * s, RECEIVER, sil=False)
    c.rrect(X(19), Y(40), X(31), Y(50), 3 * s, RED_BTN, sil=False)
    c.rrect(X(14), Y(26), X(28), Y(36), 3 * s, SILVER, sil=False)


def choice_bubble(kind, ring):
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    if kind == "bounce":
        draw_bounce_icon(c, 125, 130, 150)
    else:
        draw_buckle_icon(c, 125, 128, 150)
    return c.finish(pivot=(125, 125), border=7)


def beach_thought():
    """Thought cloud with a little beach inside (sun, sea, sand, umbrella, bucket)."""
    w, h = 520, 330
    c = Cut(w, h)
    white = (255, 255, 255)
    for cx, cy, r in ((120, 150, 100), (230, 110, 110), (350, 120, 104), (420, 190, 90), (290, 220, 110),
                      (150, 230, 90)):
        c.ellipse(cx, cy, r, r * 0.85, white)
    c.rrect(110, 130, 410, 270, 60, white)
    # inside: a rounded beach window
    x0, y0, x1, y1 = 120, 82, 400, 262
    c.rrect(x0, y0, x1, y1, 50, (170, 222, 248), sil=False)
    c.rrect(x0, 170, x1, 210, 0, (64, 168, 222), sil=False)
    c.rrect(x0, 200, x1, y1, 50, (250, 220, 150), sil=False)
    c.rrect(x0, 200, x1, 230, 0, (250, 220, 150), sil=False)
    for xx in (150, 230, 310):
        c.arc(xx + 25, 186, 22, 8, 200, 340, 4, (240, 250, 255))
    c.polygon(star_pts(340, 128, 34, 26, 12, -90), (255, 214, 92), sil=False)
    c.ellipse(340, 128, 22, 22, (255, 196, 60), sil=False)
    c.line([(210, 238), (210, 140)], 5, (236, 236, 240))
    for i in range(4):
        a0 = math.pi + i * math.pi / 4
        pts = [(210, 132)] + [(210 + 62 * math.cos(a0 + k * math.pi / 32), 160 + 34 * math.sin(a0 + k * math.pi / 32))
                              for k in range(9)]
        c.polygon(pts, ((240, 92, 88), (255, 255, 255))[i % 2], sil=False)
    c.polygon([(290, 214), (330, 214), (324, 246), (296, 246)], (84, 168, 238), sil=False)
    c.ellipse(170, 236, 18, 18, (255, 120, 140), sil=False)
    c.chord(170, 236, 18, 18, 200, 340, (255, 214, 64), sil=False)
    return c.finish(pivot=(w / 2, h / 2), border=7, shadow_alpha=0.22)


def thought_dot(r):
    c = Cut(2 * r + 14, 2 * r + 14)
    c.ellipse(r + 7, r + 7, r, r, (255, 255, 255))
    return c.finish(pivot=(r + 7, r + 7), border=5, shadow_alpha=0.22)


# ---------------------------------------------------------------- sounds (original, synthesized)
SR = A.SR
_rng = np.random.default_rng(99)


def _t(d):
    return np.arange(int(d * SR)) / SR


def buckle_click(vel=1.0):
    """CLICK! A bright metallic latch: two quick snaps with a ring."""
    out = np.zeros(int(0.4 * SR))
    for i, (d, f) in enumerate(((0.0, 3100), (0.045, 4200))):
        t = _t(0.18)
        n = _rng.normal(0, 1, len(t))
        snap = (n - np.convolve(n, np.ones(4) / 4, mode="same")) * np.exp(-t * 260)
        ring = np.sin(2 * np.pi * f * t) * np.exp(-t * 40) * 0.5 + np.sin(2 * np.pi * f * 1.48 * t) * np.exp(-t * 55) * 0.3
        s = int(d * SR)
        out[s:s + len(t)] += (1.2 * snap + ring) * (1.0 if i else 0.8)
    return vel * 0.55 * out


def belt_zip(dur=0.45, vel=1.0):
    """Webbing sliding out of the retractor: a soft rising zzzip."""
    t = _t(dur)
    n = _rng.normal(0, 1, len(t))
    band = np.convolve(n, np.ones(3) / 3, mode="same") - np.convolve(n, np.ones(14) / 14, mode="same")
    ratchet = 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * np.cumsum(40 + 50 * t / dur) / SR))
    env = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.08)
    return vel * 0.5 * env * ratchet * band


def bonk(vel=1.0):
    """A soft cartoon bonk on the padded roof: a hollow low knock that bends down."""
    t = _t(0.35)
    f = 260 * (0.6 ** (t / 0.35))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 2.7) / SR) * np.exp(-t * 20)
    return vel * 0.9 * np.exp(-t * 10) * np.minimum(1, t / 0.003) * y


def spring_wobble(vel=1.0, base=520, dur=0.7):
    """Boi-oi-oing: ears springing back."""
    t = _t(dur)
    f = base * (1 + 0.35 * np.exp(-t * 4) * np.sin(2 * np.pi * 9 * t)) * (1 + 0.15 * t)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return vel * 0.45 * np.exp(-t * 3.5) * np.minimum(1, t / 0.01) * y


def engine(dur=5.0, vel=1.0, start=0.8, stop=1.0):
    """A soft, friendly car hum that purrs up and settles down (no horn, nothing loud)."""
    t = _t(dur)
    up = np.clip(t / start, 0, 1)
    down = np.clip((dur - t) / stop, 0, 1)
    speed = up ** 2 * (3 - 2 * up) * down ** 2 * (3 - 2 * down)
    f = 48 + 30 * speed
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    putt = 0.75 + 0.25 * np.sin(2 * np.pi * np.cumsum(9 + 10 * speed) / SR)
    n = np.convolve(_rng.normal(0, 1, len(t)), np.ones(60) / 60, mode="same")
    env = np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.2) * (0.55 + 0.45 * speed)
    return vel * 0.5 * env * putt * (tone + 1.5 * n)


def music_note(col=(120, 96, 200)):
    """A paper eighth note (an icon, not a word) floating out of the car on the happy ride."""
    c = Cut(120, 170)
    c.ellipse(38, 134, 28, 21, col, theta=-20)
    c.rrect(56, 22, 68, 136, 6, col)
    c.polygon([(62, 22), (104, 46), (104, 74), (66, 54)], col)
    return c.finish(pivot=(60, 90), border=4, shadow_alpha=0.18)


class BeachBallWipe:
    """A giant paper beach ball that rolls across the screen and hides the jump back to the start.
    Pastel wedges and a slow spin keep the frame-to-frame change gentle."""
    R = 1180

    def __init__(self):
        R = self.R
        D = 2 * R + 40
        c = Cut(D, D)
        cx = cy = D / 2
        cols = [(250, 150, 140), (255, 250, 240), (140, 196, 236), (255, 222, 130), (255, 250, 240), (150, 214, 160)]
        for i, col in enumerate(cols):
            a0, a1 = math.radians(i * 60), math.radians((i + 1) * 60)
            pts = [(cx, cy)] + [(cx + R * math.cos(a0 + (a1 - a0) * k / 24), cy + R * math.sin(a0 + (a1 - a0) * k / 24))
                                for k in range(25)]
            c.polygon(pts, col)
        c.ellipse(cx, cy, 150, 150, (255, 250, 240))
        c.ellipse(cx, cy, 70, 70, (250, 150, 140), sil=False)
        c.ellipse(cx - R * 0.42, cy - R * 0.45, R * 0.16, R * 0.08, (255, 255, 255), sil=False, theta=-35)
        self.spr = c.finish(pivot=(cx, cy), border=8, shadow_alpha=0.22, shadow_blur=8)

    def draw(self, f, cx, cy, angle):
        place(f, self.spr, (cx, cy), angle=angle)
