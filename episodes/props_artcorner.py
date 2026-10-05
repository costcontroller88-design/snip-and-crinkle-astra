"""Props for the pilot: a playroom art corner, built as one 1920x1920 world.

The landscape camera (1920x1080) sees rows LAND_Y0..LAND_Y0+1080; the vertical camera (1080x1920)
sees columns VERT_X0..VERT_X0+1080. Landscape is the main view; vertical Shorts need their own staging or a panning camera.
Snip paints at an easel on the left; Crinkle's paint pot sits on a little stool between them.
"""
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from characters import CRINKLE, EYE, SNIP  # noqa: E402
import hires  # noqa: E402
from hires import Cut  # noqa: E402  (follows hires.RES; 1x unless an episode raises it)
from paperlib import grain, heart_pts, mix, place, star_pts  # noqa: E402

WORLD_W, WORLD_H = 1920, 1920
FLOOR_Y = 1500                        # where the characters' feet stand
LAND_Y0 = 560
VERT_X0 = 420
WALL_BOTTOM = 1380

WALL = (255, 236, 212)
WALL_DOT = (255, 245, 230)
WAINSCOT = (186, 226, 212)
TRIM = (255, 252, 244)
WOOD = (236, 186, 128)
WOOD_LINE = (214, 160, 104)
RUG = (116, 192, 196)
RUG_IN = (150, 212, 208)
PAINT_BLUE = (64, 136, 232)
PAINT_BLUE_DARK = (44, 104, 196)
CANVAS = (461, 930, 799, 1232)        # x0, y0, x1, y1 of the paper on the easel
EASEL_X = 630
STOOL_X = 1220
POT_AT = (1220, 1352)                 # pot base point (on the stool top)


# ---------------------------------------------------------------- background
def _at(x, y):
    """Design units -> pixels at the current render scale."""
    return x * hires.RES, y * hires.RES


def _gallery(img):
    """A string of children's drawings pinned with pegs across the wall."""
    pts = [(x, 640 + 50 * math.sin(math.pi * (x - 100) / 1400)) for x in range(100, 1501, 20)]
    s = Cut(1520, 720)
    s.line(pts, 4, (150, 112, 92), sil=True)
    place(img, s.finish(pivot=(0, 0), border=0, shadow_alpha=0.2), _at(0, 0))
    pics = [(330, (255, 214, 92), "sun"), (640, (140, 200, 120), "house"), (950, (120, 190, 236), "fish"),
            (1260, (240, 150, 170), "rainbow")]
    for i, (x, col, kind) in enumerate(pics):
        y = 640 + 50 * math.sin(math.pi * (x - 100) / 1400)
        tilt = (-4, 3, -2, 4)[i]
        p = Cut(190, 170)
        p.rrect(0, 0, 190, 170, 6, (255, 253, 247))
        if kind == "sun":
            p.ellipse(95, 90, 34, 34, col, sil=False)
            for k in range(8):
                a = k * math.pi / 4
                p.line([(95 + 46 * math.cos(a), 90 + 46 * math.sin(a)), (95 + 62 * math.cos(a), 90 + 62 * math.sin(a))],
                       6, col)
        elif kind == "house":
            p.polygon([(50, 90), (95, 46), (140, 90)], (236, 112, 96), sil=False)
            p.rrect(58, 88, 132, 140, 4, col, sil=False)
            p.rrect(86, 108, 104, 140, 3, (150, 104, 80), sil=False)
        elif kind == "fish":
            p.ellipse(88, 90, 46, 28, col, sil=False)
            p.polygon([(130, 90), (158, 66), (158, 114)], col, sil=False)
            p.ellipse(68, 84, 6, 6, EYE, sil=False)
        else:
            for k, rc in enumerate(((240, 112, 104), (255, 196, 72), (120, 196, 120), (100, 160, 236))):
                p.arc(95, 128, 74 - k * 13, 64 - k * 13, 180, 360, 11, rc)
        spr = p.finish(pivot=(95, 8), border=4, shadow_alpha=0.18)
        place(img, spr, _at(x, y + 4), angle=tilt)
        peg = Cut(22, 44)
        peg.rrect(0, 0, 22, 44, 5, (240, 120, 96) if i % 2 else (255, 204, 72))
        place(img, peg.finish(pivot=(11, 22), border=3), _at(x, y))


def _window():
    c = Cut(340, 380)
    c.rrect(0, 0, 340, 380, 18, TRIM)
    sky = (160, 214, 246)
    for x0, y0 in ((18, 18), (176, 18), (18, 196), (176, 196)):
        c.rrect(x0, y0, x0 + 146, y0 + 166, 9, sky, sil=False)
    for cx, cy, r in ((80, 92, 24), (108, 80, 30), (138, 94, 22)):
        c.ellipse(cx, cy, r, r * 0.85, (255, 255, 255), sil=False)
    c.ellipse(250, 300, 70, 56, (110, 190, 116), sil=False)
    c.ellipse(210, 330, 50, 40, (96, 176, 104), sil=False)
    c.ellipse(258, 92, 30, 30, (255, 214, 80), sil=False)
    return c.finish(pivot=(0, 0), border=6)


def _shelf():
    c = Cut(330, 420)
    wood = (214, 160, 108)
    c.rrect(0, 0, 330, 420, 12, wood)
    c.rrect(14, 14, 316, 196, 8, (190, 136, 90), sil=False)
    c.rrect(14, 214, 316, 406, 8, (190, 136, 90), sil=False)
    # crayon cups
    for i, (x, col) in enumerate(((70, (240, 112, 104)), (150, (255, 196, 72)), (230, (100, 170, 236)))):
        for k in range(3):
            c.rrect(x - 26 + k * 18, 70 - (k % 2) * 14, x - 14 + k * 18, 140, 4,
                    ((240, 112, 104), (120, 196, 120), (150, 120, 220))[(i + k) % 3], sil=False)
        c.rrect(x - 34, 116, x + 34, 192, 10, col, sil=False)
    # blocks
    for x, y, col in ((70, 350, (255, 196, 72)), (150, 350, (100, 170, 236)), (110, 286, (240, 112, 104)),
                      (240, 350, (140, 200, 120))):
        c.rrect(x - 34, y - 34, x + 34, y + 34, 6, col, sil=False)
        c.ellipse(x, y, 13, 13, mix(col, (255, 255, 255), 0.4), sil=False)
    return c.finish(pivot=(0, 0), border=5)


def _plant():
    c = Cut(260, 330)
    for i, (dx, ang) in enumerate(((-46, -30), (0, 0), (44, 28), (-22, -12), (24, 14))):
        c.ellipse(130 + dx * 1.2, 110 + abs(dx) * 0.6, 24, 82, (96, 176, 110) if i % 2 else (78, 156, 96), theta=ang)
    c.polygon([(80, 190), (180, 190), (166, 320), (94, 320)], (240, 150, 110))
    c.rrect(70, 180, 190, 210, 8, (248, 168, 128))
    return c.finish(pivot=(130, 320), border=5)


def _bunting():
    c = Cut(1200, 200)
    pts = [(x, 30 + 60 * math.sin(math.pi * x / 1200)) for x in range(0, 1201, 20)]
    c.line(pts, 5, (150, 112, 92))
    cols = [(244, 112, 104), (255, 206, 72), (84, 182, 222), (150, 206, 120), (196, 160, 236)]
    for i, x in enumerate(range(60, 1200, 110)):
        y = 30 + 60 * math.sin(math.pi * x / 1200)
        c.polygon([(x - 42, y), (x + 42, y), (x, y + 92)], cols[i % 5])
    return c.finish(pivot=(0, 0), border=5)


def background():
    W, H = WORLD_W, WORLD_H
    R = hires.RES
    k = 2 * R
    img = Image.new("RGBA", (int(W * k), int(H * k)), WALL + (255,))
    d = ImageDraw.Draw(img)
    for row in range(22):
        for col in range(18):
            x = (col * 116 + (58 if row % 2 else 0)) * k
            y = (row * 100 + 30) * k
            r = 9 * k
            d.polygon([(px * k, py * k) for px, py in star_pts(x / k, y / k, r / k * 1.4, r / k * 0.6, 4, -90)],
                      fill=WALL_DOT)
    d.rectangle([0, 1180 * k, W * k, WALL_BOTTOM * k], fill=WAINSCOT)
    for x in range(0, W, 64):
        d.rectangle([x * k, 1196 * k, (x + 6) * k, WALL_BOTTOM * k], fill=mix(WAINSCOT, (255, 255, 255), 0.25))
    d.rectangle([0, 1170 * k, W * k, 1190 * k], fill=TRIM)
    d.rectangle([0, WALL_BOTTOM * k, W * k, H * k], fill=WOOD)
    for y in range(WALL_BOTTOM + 60, H, 70):
        d.rectangle([0, y * k, W * k, (y + 5) * k], fill=WOOD_LINE)
    for i, y in enumerate(range(WALL_BOTTOM, H, 70)):
        for x in range((i % 3) * 210, W, 640):
            d.rectangle([x * k, y * k, (x + 5) * k, (y + 65) * k], fill=WOOD_LINE)
    d.rectangle([0, WALL_BOTTOM * k, W * k, (WALL_BOTTOM + 14) * k], fill=(214, 160, 108))
    img = grain(img.resize((int(W * R), int(H * R)), Image.LANCZOS), 0.03)
    # rug
    rug = Cut(1700, 330)
    rug.ellipse(850, 165, 840, 158, RUG)
    rug.ellipse(850, 165, 770, 126, RUG_IN, sil=False)
    rug.ellipse(850, 165, 690, 98, RUG, sil=False)
    for i in range(40):
        a = 2 * math.pi * i / 40
        rug.ellipse(850 + 805 * math.cos(a), 165 + 142 * math.sin(a), 9, 7, TRIM, sil=False)
    place(img, rug.finish(pivot=(850, 165), border=4, shadow_alpha=0.15), _at(960, 1580))
    place(img, _bunting(), _at(360, 250))
    _gallery(img)
    place(img, _window(), _at(1640, 640))
    place(img, _shelf(), _at(40, 980))
    place(img, _plant(), _at(1860, 1560))
    return img


# ---------------------------------------------------------------- easel, painting, stool, pot
def easel():
    """A-frame easel; pivot at the floor between the front legs."""
    c = Cut(480, 610)
    wood, dark = (206, 150, 96), (176, 120, 74)
    c.polygon([(214, 0), (244, 0), (370, 602), (336, 602)], dark)          # back leg (right)
    c.polygon([(222, 0), (252, 0), (120, 602), (86, 602)], wood)           # front-left leg
    c.polygon([(228, 0), (258, 0), (396, 602), (362, 602)], wood)          # front-right leg
    c.rrect(40, 330, 440, 360, 8, wood)                                    # tray (the canvas sits on it)
    c.rrect(40, 354, 440, 366, 4, dark, sil=False)
    for x, col in ((70, (240, 112, 104)), (100, (255, 196, 72)), (410, (120, 196, 120))):
        c.rrect(x - 7, 316, x + 7, 334, 3, col, sil=False)                  # paint dots on the tray
    return c.finish(pivot=(240, 602), border=5)


def canvas_board():
    x0, y0, x1, y1 = CANVAS
    c = Cut(x1 - x0, y1 - y0)
    c.rrect(0, 0, x1 - x0, y1 - y0, 6, (255, 254, 250))
    c.rrect(0, y1 - y0 - 40, x1 - x0, y1 - y0, 0, (226, 244, 222), sil=False)     # pale grass band
    return c.finish(pivot=(0, 0), border=6, shadow_alpha=0.22)


def _painted(c):
    return c.finish(pivot=(c.w / 2, c.h / 2), border=0, shadow_alpha=0.0, grain_strength=0.05)


def paint_sun():
    c = Cut(120, 120)
    c.ellipse(60, 60, 30, 30, (255, 204, 64))
    for k in range(8):
        a = k * math.pi / 4
        c.line([(60 + 38 * math.cos(a), 60 + 38 * math.sin(a)), (60 + 54 * math.cos(a), 60 + 54 * math.sin(a))],
               8, (255, 196, 52))
    return _painted(c)


def paint_flower(col):
    c = Cut(70, 120)
    c.line([(35, 50), (35, 116)], 7, (100, 180, 100))
    c.ellipse(48, 92, 12, 7, (110, 190, 110), theta=-30)
    for k in range(5):
        a = k * 2 * math.pi / 5 - math.pi / 2
        c.ellipse(35 + 17 * math.cos(a), 40 + 17 * math.sin(a), 12, 12, col)
    c.ellipse(35, 40, 9, 9, (255, 214, 80))
    return _painted(c)


def paint_friends():
    """Snip and Crinkle painted by Snip: wobbly and sweet."""
    c = Cut(180, 140)
    # bunny
    c.ellipse(46, 18, 9, 26, SNIP["fur"], theta=-8)
    c.ellipse(66, 18, 9, 26, SNIP["fur"], theta=8)
    c.ellipse(56, 62, 28, 26, SNIP["fur"])
    c.rrect(36, 86, 76, 132, 14, SNIP["tee"])
    # bear
    c.ellipse(108, 46, 10, 10, CRINKLE["fur"])
    c.ellipse(144, 46, 10, 10, CRINKLE["fur"])
    c.ellipse(126, 66, 28, 25, CRINKLE["fur"])
    c.rrect(104, 88, 148, 134, 16, CRINKLE["fur"])
    c.rrect(104, 88, 148, 98, 4, CRINKLE["scarf"])
    for x, y in ((48, 60), (64, 60), (118, 64), (134, 64)):
        c.ellipse(x, y, 3.5, 3.5, EYE)
    c.arc(56, 70, 7, 5, 20, 160, 3, EYE)
    c.arc(126, 74, 7, 5, 20, 160, 3, EYE)
    c.polygon(heart_pts(91, 54, 26), (240, 90, 120))
    return _painted(c)


def paint_heart():
    c = Cut(60, 60)
    c.polygon(heart_pts(30, 32, 44), (240, 90, 120))
    return _painted(c)


def splat():
    """The big blue splash on the painting (irregular blob + droplets)."""
    c = Cut(300, 260)
    pts = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        r = 92 + 18 * math.sin(5 * a + 0.6) + 12 * math.sin(9 * a + 1.3) + (26 if i % 7 == 0 else 0)
        pts.append((150 + r * math.cos(a) * 1.05, 128 + r * math.sin(a) * 0.9))
    c.polygon(pts, PAINT_BLUE)
    for x, y, r in ((40, 40, 12), (262, 70, 10), (32, 200, 9), (270, 210, 13), (150, 18, 8), (220, 26, 7)):
        c.ellipse(x, y, r, r, PAINT_BLUE)
    c.ellipse(118, 98, 26, 14, mix(PAINT_BLUE, (255, 255, 255), 0.35), sil=False, theta=-20)
    return c.finish(pivot=(150, 128), border=0, shadow_alpha=0.0, grain_strength=0.04)


def drip(length=90):
    c = Cut(24, length + 20)
    c.rrect(4, 0, 20, length, 8, PAINT_BLUE)
    c.ellipse(12, length, 10, 11, PAINT_BLUE)
    return c.finish(pivot=(12, 0), border=0, shadow_alpha=0.0, grain_strength=0.04)


def blob():
    """Flying paint: a fat teardrop pointing along its flight (pivot at the head)."""
    c = Cut(120, 70)
    c.ellipse(86, 35, 30, 28, PAINT_BLUE)
    c.polygon([(86, 8), (8, 35), (86, 62)], PAINT_BLUE)
    c.ellipse(94, 26, 9, 6, mix(PAINT_BLUE, (255, 255, 255), 0.4), sil=False)
    return c.finish(pivot=(86, 35), border=4, shadow_alpha=0.2)


def puddle():
    c = Cut(230, 70)
    c.ellipse(115, 35, 108, 26, PAINT_BLUE)
    c.ellipse(40, 40, 30, 14, PAINT_BLUE)
    c.ellipse(100, 30, 40, 8, mix(PAINT_BLUE, (255, 255, 255), 0.3), sil=False)
    return c.finish(pivot=(115, 35), border=0, shadow_alpha=0.0)


def stool():
    """Little wooden stool; pivot at floor centre."""
    c = Cut(200, 170)
    wood, dark = (230, 168, 104), (196, 136, 82)
    c.rrect(20, 40, 44, 170, 8, dark)
    c.rrect(156, 40, 180, 170, 8, dark)
    c.rrect(26, 110, 174, 126, 5, dark)
    c.rrect(0, 18, 200, 50, 14, wood)
    return c.finish(pivot=(100, 168), border=5)


def pot(level=1.0):
    """Paint pot (a jar) with blue paint and a brush; pivot at the base centre."""
    c = Cut(130, 190)
    glass = (226, 240, 250)
    c.line([(84, 10), (70, 96)], 9, (214, 160, 108), sil=True)            # brush handle
    c.rrect(10, 70, 120, 186, 22, glass)
    if level > 0:
        top = 186 - 104 * level
        c.rrect(16, top, 114, 180, 18, PAINT_BLUE, sil=False)
        c.ellipse(65, top + 4, 48, 9, mix(PAINT_BLUE, (255, 255, 255), 0.25), sil=False)
    c.rrect(4, 62, 126, 80, 8, (255, 204, 72))                            # rim
    c.ellipse(36, 128, 7, 22, (255, 255, 255), sil=False)                 # glint
    return c.finish(pivot=(65, 186), border=5)


def brush(tip=(255, 196, 52)):
    """Snip's paintbrush; pivot at the handle end held in the paw, pointing down."""
    c = Cut(40, 170)
    c.rrect(13, 0, 27, 116, 7, (240, 112, 104))
    c.rrect(11, 108, 29, 126, 3, (200, 204, 214))
    c.polygon([(11, 124), (29, 124), (26, 158), (20, 168), (14, 158)], tip)
    return c.finish(pivot=(20, 24), border=4)


# ---------------------------------------------------------------- choice bubbles
def _mini_crinkle(c, x, y, r, look=0, sad=False):
    fur = CRINKLE["fur"]
    c.ellipse(x - r * 0.72, y - r * 0.72, r * 0.34, r * 0.34, fur)
    c.ellipse(x + r * 0.72, y - r * 0.72, r * 0.34, r * 0.34, fur)
    c.ellipse(x, y, r, r * 0.86, fur)
    c.ellipse(x + look * r * 0.1, y + r * 0.3, r * 0.42, r * 0.3, CRINKLE["muzzle"], sil=False)
    for s in (-1, 1):
        c.ellipse(x + s * r * 0.36 + look * r * 0.16, y - r * 0.06, r * 0.1, r * 0.13, EYE, sil=False)
    c.ellipse(x + look * r * 0.1, y + r * 0.18, r * 0.14, r * 0.1, CRINKLE["nose"], sil=False)


def _mini_snip(c, x, y, r):
    fur = SNIP["fur"]
    c.ellipse(x - r * 0.4, y - r * 1.15, r * 0.26, r * 0.7, fur, theta=-10)
    c.ellipse(x + r * 0.4, y - r * 1.15, r * 0.26, r * 0.7, fur, theta=10)
    c.ellipse(x, y, r, r * 0.88, fur)
    for s in (-1, 1):
        c.arc(x + s * r * 0.36, y + r * 0.02, r * 0.14, r * 0.12, 200, 340, r * 0.07, EYE)
    c.ellipse(x, y + r * 0.2, r * 0.1, r * 0.07, SNIP["nose"], sil=False)


def bubble_hide(ring=(240, 110, 100)):
    """Red choice: Crinkle tiptoes away from the mess (paw prints leading off, looking back)."""
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    c.ellipse(66, 172, 30, 10, PAINT_BLUE, sil=False)                     # the spill left behind
    for x, y in ((92, 170), (114, 182), (136, 170), (158, 182)):          # paw prints walking away
        c.ellipse(x, y, 7, 9, CRINKLE["foot"], sil=False)
        for dx in (-6, 0, 6):
            c.ellipse(x + dx, y - 11, 2.6, 2.6, CRINKLE["foot"], sil=False)
    _mini_crinkle(c, 162, 106, 40, look=1)
    for i, y in enumerate((92, 108, 124)):                                # speed lines (sneaking off)
        c.line([(96 - i * 4, y), (114 - i * 4, y)], 4, (180, 170, 180))
    return c.finish(pivot=(125, 125), border=7)


def bubble_sorry(ring=(90, 190, 120)):
    """Green choice: Crinkle and Snip together, a heart between them (say sorry, make up)."""
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    _mini_snip(c, 86, 144, 34)
    _mini_crinkle(c, 164, 140, 38)
    c.polygon(heart_pts(125, 76, 50), (240, 72, 98), sil=False)
    return c.finish(pivot=(125, 125), border=7)


def droplet(r=16):
    c = Cut(2 * r + 4, 2 * r + 4)
    c.ellipse(r + 2, r + 2, r, r, PAINT_BLUE)
    c.ellipse(r - r * 0.25, r - r * 0.3, r * 0.3, r * 0.22, mix(PAINT_BLUE, (255, 255, 255), 0.4), sil=False)
    return c.finish(pivot=(r + 2, r + 2), border=3, shadow_alpha=0.2)
