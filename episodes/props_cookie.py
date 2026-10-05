"""Props, scenery and sounds for Episode 3 — The Last Cookie? 🍪

Evening kitchen (twilight-indigo striped wallpaper, a warm pendant lamp, a sunset window with
curtains, a gingham tablecloth), an empty glass cookie jar, a plate, the cookie and its two
EQUAL halves (mirror images, same chips, same size), paper icons (idea bulb, choice bubbles,
crumbs, landing puffs) and a few new synthesized sound effects. Everything is drawn in code.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import audio as A
import scene
from paperlib import Cut, grain, heart_pts, mix, place, star_pts

W, H = scene.W, scene.H
TABLE_Y = scene.TABLE_Y

# ---------------------------------------------------------------- palette
WALL = (96, 92, 158)            # twilight indigo
WALL_STRIPE = (108, 104, 170)
WALL_STAR = (150, 146, 206)
GLOW = (255, 204, 128)          # warm lamp light
CLOTH = (255, 244, 230)
CLOTH_BAND = (246, 162, 150)
CLOTH_CROSS = (228, 104, 98)
CLOTH_TOP = (252, 226, 214)

DOUGH_EDGE = (206, 138, 66)
DOUGH = (236, 178, 100)
DOUGH_IN = (246, 200, 126)
DOUGH_BREAK = (222, 160, 88)
CHIP = (92, 56, 42)
CHIP_HI = (142, 98, 76)

COOKIE_R = 80
LAMP_X = 535
LAMP_BULB_Y = 318


# ---------------------------------------------------------------- background
def _wall():
    img = Image.new("RGBA", (W, H), WALL + (255,))
    d = ImageDraw.Draw(img)
    sw = 68
    for i, x in enumerate(range(0, W + sw, sw)):
        if i % 2:
            d.rectangle([x, 0, x + sw - 1, H], fill=WALL_STRIPE)
    # tiny 4-point paper stars on the light stripes
    k = 3
    stars = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    ds = ImageDraw.Draw(stars)
    for row in range(16):
        for i, x in enumerate(range(0, W + sw, sw)):
            if i % 2 == 0:
                continue
            cx = x + sw / 2
            cy = 70 + row * 124 + (62 if (i // 2) % 2 else 0)
            ds.polygon([(px * k, py * k) for px, py in star_pts(cx, cy, 11, 4, 4, -90)], fill=WALL_STAR)
    img.alpha_composite(stars.resize((W, H), Image.LANCZOS))
    return grain(img, 0.03)


def _radial(cx, cy, rx, ry, power=1.6):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip(1 - r, 0, 1) ** power


def _light(img):
    """Warm lamp glow (screen blend) + a soft light cone + darker evening corners."""
    a = np.asarray(img).astype(np.float32) / 255.0
    rgb = a[..., :3]
    glow = 0.85 * _radial(LAMP_X, LAMP_BULB_Y + 60, 700, 900)[..., None]
    g = np.array(GLOW, np.float32) / 255.0
    rgb = 1 - (1 - rgb) * (1 - glow * g)
    # light cone from the lamp down to the table
    cone = Image.new("L", (W, H), 0)
    ImageDraw.Draw(cone).polygon([(LAMP_X - 80, LAMP_BULB_Y), (LAMP_X + 80, LAMP_BULB_Y),
                                  (LAMP_X + 330, TABLE_Y), (LAMP_X - 330, TABLE_Y)], fill=255)
    cone = np.asarray(cone.filter(ImageFilter.GaussianBlur(28))).astype(np.float32) / 255.0
    fade = np.linspace(1.0, 0.45, H, dtype=np.float32)[:, None]
    c = (0.16 * cone * fade)[..., None]
    rgb = 1 - (1 - rgb) * (1 - c * g)
    # evening vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2)
    rgb *= (1 - 0.30 * np.clip(v - 0.35, 0, 1) ** 1.3)[..., None]
    a[..., :3] = np.clip(rgb, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8), "RGBA")


def _window():
    c = Cut(420, 470)
    frame = (250, 240, 222)
    c.rrect(30, 20, 390, 400, 18, frame)
    bands = [(52, 60, 128), (74, 70, 148), (112, 80, 160), (168, 92, 156), (226, 116, 136), (250, 160, 112),
             (255, 200, 120)]
    for x0, y0 in ((50, 40), (220, 40), (50, 220), (220, 220)):
        for i, col in enumerate(bands):
            yt = 40 + i * 50
            yb = yt + 50
            top, bot = max(yt, y0), min(yb, y0 + 160)
            if bot > top:
                c.rrect(x0, top, x0 + 150, bot, 0, col, sil=False)
    # hills and rooftops silhouette in the lower panes
    hill = (70, 52, 104)
    c.polygon([(50, 380), (50, 330), (110, 300), (170, 318), (200, 300), (200, 380)], hill, sil=False)
    c.polygon([(220, 380), (220, 310), (262, 310), (262, 284), (292, 262), (322, 284), (322, 318), (370, 300),
               (370, 380)], hill, sil=False)
    c.rrect(282, 296, 300, 312, 2, (255, 214, 120), sil=False)       # a lit little window far away
    # crescent moon + stars
    c.ellipse(300, 100, 34, 34, (255, 240, 196), sil=False)
    c.ellipse(316, 90, 30, 30, bands[0], sil=False)
    for sx, sy, r in ((92, 78, 9), (150, 128, 6), (252, 160, 7), (120, 172, 5)):
        c.polygon(star_pts(sx, sy, r, r * 0.42, 4, -90), (255, 236, 170), sil=False)
    # window bars
    c.rrect(200, 40, 220, 380, 4, frame, sil=False)
    c.rrect(50, 200, 370, 220, 4, frame, sil=False)
    # curtains (mustard) and sill
    cur = (246, 186, 72)
    cur_d = (226, 156, 54)
    c.polygon([(0, 0), (92, 0), (70, 160), (40, 300), (60, 430), (0, 430)], cur)
    c.polygon([(420, 0), (328, 0), (350, 160), (380, 300), (360, 430), (420, 430)], cur)
    for x0, x1 in ((22, 34), (386, 398)):
        c.line([(x0, 10), (x1 - 8, 200), (x0 + 2, 420)], 5, cur_d)
    c.rrect(10, 405, 410, 440, 10, (236, 222, 200))
    c.rrect(0, 0, 420, 22, 10, (164, 110, 76))
    return c.finish(pivot=(0, 0), border=6)


def _lamp():
    c = Cut(260, 360)
    c.line([(130, 0), (130, 214)], 7, (64, 52, 72), sil=True)
    c.ellipse(130, 330 - 20, 44, 34, (255, 246, 206))           # bulb peeking below the shade
    c.chord(130, 312, 116, 120, 180, 360, (244, 150, 70))         # dome shade
    c.rrect(14, 300, 246, 324, 10, (226, 120, 58))
    c.rrect(108, 186, 152, 204, 6, (226, 120, 58))
    for x in (60, 100, 160, 200):
        c.ellipse(x, 262, 9, 9, (255, 206, 120), sil=False)
    return c.finish(pivot=(130, 0), border=5)


def _frame_picture():
    c = Cut(200, 230)
    c.rrect(0, 0, 200, 230, 22, (232, 196, 140))
    c.rrect(18, 18, 182, 212, 14, (255, 248, 232), sil=False)
    c.polygon(heart_pts(100, 120, 112), (240, 110, 130), sil=False)
    c.ellipse(76, 98, 10, 7, (255, 210, 220), sil=False)
    return c.finish(pivot=(100, 0), border=6)


def _table():
    c = Cut(1120, 520)
    c.rrect(0, 0, 1120, 86, 14, CLOTH_TOP)
    c.rrect(0, 64, 1120, 520, 0, CLOTH)
    sq = 56
    for x in range(0, 1120, sq * 2):
        c.rrect(x, 70, x + sq, 520, 0, CLOTH_BAND, sil=False)
    for y in range(70 + sq, 520, sq * 2):
        c.rrect(0, y, 1120, y + sq, 0, CLOTH_BAND, sil=False)
        for x in range(0, 1120, sq * 2):
            c.rrect(x, y, x + sq, y + sq, 0, CLOTH_CROSS, sil=False)
    # lace trim along the table edge
    for x in range(14, 1120, 28):
        c.ellipse(x, 88, 14, 12, (255, 255, 255))
        c.ellipse(x, 86, 4, 4, CLOTH_TOP, sil=False)
    c.rrect(0, 60, 1120, 78, 0, (255, 255, 255), sil=False)
    return c.finish(pivot=(0, 0), border=5)


def cookie_jar():
    """An EMPTY glass cookie jar (just crumbs) with a cookie-picture label — it really is the last cookie."""
    c = Cut(200, 250)
    glass = (214, 232, 244)
    c.rrect(52, 12, 148, 40, 12, (232, 96, 88))                   # lid knob + lid
    c.ellipse(100, 14, 18, 14, (244, 120, 108))
    c.rrect(30, 34, 170, 58, 12, (232, 96, 88))
    c.rrect(38, 54, 162, 72, 6, glass)                             # neck
    c.rrect(14, 66, 186, 246, 46, glass)                           # body
    c.rrect(26, 80, 174, 234, 38, (226, 240, 250), sil=False)      # inner glass (empty!)
    c.rrect(36, 92, 52, 210, 8, (250, 253, 255), sil=False)        # highlight
    c.rrect(150, 110, 160, 170, 5, (250, 253, 255), sil=False)
    for cx, cy, r, col in ((70, 224, 6, DOUGH), (96, 228, 4, DOUGH_EDGE), (122, 225, 5, DOUGH),
                           (140, 229, 3, CHIP), (84, 229, 3, CHIP), (108, 222, 4, DOUGH_IN)):
        c.ellipse(cx, cy, r, r * 0.8, col, sil=False)
    # label: a little cookie picture, no words
    c.ellipse(100, 150, 44, 44, (255, 246, 226), sil=False)
    _cookie_art(c, 100, 150, 30)
    return c.finish(pivot=(100, 246), border=5)


def plate():
    c = Cut(280, 64)
    c.ellipse(140, 48, 72, 13, (222, 226, 236))                     # foot
    c.ellipse(140, 28, 134, 24, (255, 255, 255))                   # plate
    c.ellipse(140, 28, 120, 19, (92, 176, 206), sil=False)          # blue rim band
    c.ellipse(140, 27, 106, 15, (250, 252, 255), sil=False)
    c.ellipse(140, 29, 80, 9, (232, 240, 248), sil=False)
    return c.finish(pivot=(140, 54), border=4)


def background():
    bg = _wall()
    bg = _light(bg)
    place(bg, _window(), (40, 330))
    place(bg, _frame_picture(), (865, 420))
    place(bg, _table(), (-20, TABLE_Y - 40))
    place(bg, cookie_jar(), (118, TABLE_Y + 2))
    place(bg, _lamp(), (LAMP_X, -10))
    # warm pool of lamp light on the tablecloth
    pool = Image.new("L", (W, H), 0)
    ImageDraw.Draw(pool).ellipse([LAMP_X - 330, TABLE_Y - 36, LAMP_X + 330, TABLE_Y + 70], fill=255)
    pool = pool.filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * 0.22))
    warm = Image.new("RGBA", (W, H), (255, 236, 170, 255))
    warm.putalpha(pool)
    bg.alpha_composite(warm)
    return bg


# ---------------------------------------------------------------- cookie
_CHIPS = ((-0.50, -0.40, 0.17), (-0.24, 0.10, 0.15), (-0.54, 0.36, 0.13), (-0.20, -0.66, 0.11),
          (-0.26, 0.62, 0.12))


def _chip(c, x, y, r, k):
    pts = []
    for i in range(9):
        a = 2 * math.pi * i / 9 + k
        rr = r * (1 + 0.18 * math.sin(3 * a + k * 2))
        pts.append((x + rr * math.cos(a), y + rr * 0.86 * math.sin(a)))
    c.polygon(pts, CHIP, sil=False)
    c.ellipse(x - r * 0.3, y - r * 0.32, r * 0.28, r * 0.2, CHIP_HI, sil=False)


def _cookie_art(c, cx, cy, r, sil=False):
    c.ellipse(cx, cy, r, r, DOUGH_EDGE, sil=sil)
    c.ellipse(cx - r * 0.02, cy - r * 0.03, r * 0.9, r * 0.9, DOUGH, sil=False)
    c.ellipse(cx - r * 0.08, cy - r * 0.1, r * 0.62, r * 0.6, DOUGH_IN, sil=False)
    for sgn in (-1, 1):                 # mirror-symmetric chips -> the two halves are equal
        for i, (dx, dy, rr) in enumerate(_CHIPS):
            _chip(c, cx + sgn * dx * r, cy + dy * r, rr * r, 0.7 * i + (0.35 if sgn > 0 else 0))
    for dx, dy in ((-0.7, -0.1), (0.66, -0.04), (-0.05, -0.5), (0.1, 0.4), (-0.42, 0.72), (0.44, 0.74)):
        c.ellipse(cx + dx * r, cy + dy * r, r * 0.035, r * 0.035, DOUGH_EDGE, sil=False)


def _crack(r, pad):
    """Shared break line (top -> bottom) so the two halves fit together exactly."""
    n = 8
    pts = []
    for i in range(n + 1):
        y = -r - 4 + (2 * r + 8) * i / n
        x = 0 if i in (0, n) else (0.07 * r if i % 2 else -0.07 * r)
        pts.append((pad + r + x, pad + r + y))
    return pts


def _bite(c, cx, cy, r):
    """Scalloped bite: three overlapping circles removed from the piece."""
    for dx, dy, k in ((-0.5, 0.18, 0.56), (0.0, 0.0, 0.6), (0.5, 0.18, 0.56)):
        box = c._s([cx + dx * r - k * r, cy + dy * r - k * r, cx + dx * r + k * r, cy + dy * r + k * r])
        c.d.ellipse(box, fill=(0, 0, 0, 0))
        c.m.ellipse(box, fill=0)


def cookie(r=COOKIE_R):
    pad = 14
    c = Cut(2 * (r + pad), 2 * (r + pad))
    _cookie_art(c, r + pad, r + pad, r, sil=True)
    return c.finish(pivot=(r + pad, r + pad), border=5)


def cookie_half(side, bites=0, r=COOKIE_R):
    """side 'l' keeps the left half (flat break edge on its right). Pivot = middle of the break edge,
    which is the whole cookie's centre, so the two halves tile back into the whole cookie."""
    pad = 14
    S = 2 * (r + pad)
    c = Cut(S, S)
    cx = cy = r + pad
    _cookie_art(c, cx, cy, r, sil=True)
    crack = _crack(r, pad)
    far = S + 10 if side == "l" else -10
    erase = crack + [(far, crack[-1][1] + 20), (far, crack[0][1] - 20)]
    c.d.polygon([(x * 3, y * 3) for x, y in erase], fill=(0, 0, 0, 0))
    c.m.polygon([(x * 3, y * 3) for x, y in erase], fill=0)
    c.line(crack, 5, DOUGH_BREAK)
    sgn = -1 if side == "l" else 1
    if bites >= 1:
        _bite(c, cx + sgn * r * 0.62, cy - r * 0.86, r * 0.42)
    if bites >= 2:
        _bite(c, cx + sgn * r * 0.98, cy - r * 0.05, r * 0.46)
    return c.finish(pivot=(cx, cy), border=5)


HALF_CENTROID = 4 * COOKIE_R / (3 * math.pi)   # distance of a half-disc's centre of mass from its flat edge


def crumbs():
    out = []
    cols = (DOUGH, DOUGH_EDGE, DOUGH_IN, CHIP, DOUGH)
    for i, col in enumerate(cols):
        c = Cut(40, 40)
        n = 6
        pts = [(20 + (9 + 3 * math.sin(i + 2.1 * k)) * math.cos(2 * math.pi * k / n),
                20 + (8 + 3 * math.cos(i * 1.3 + k)) * math.sin(2 * math.pi * k / n)) for k in range(n)]
        c.polygon(pts, col)
        out.append(c.finish(pivot=(20, 20), border=3, shadow_alpha=0.2))
    return out


# ---------------------------------------------------------------- icons
def idea_bulb():
    c = Cut(240, 300)
    ray = (255, 214, 64)
    for a in (-150, -115, -65, -30, 0, 180, -90):
        if a in (0, 180):
            continue
        ra = math.radians(a)
        c.line([(120 + 92 * math.cos(ra), 112 + 92 * math.sin(ra)),
                (120 + 118 * math.cos(ra), 112 + 118 * math.sin(ra))], 14, ray, sil=True)
    c.ellipse(120, 112, 66, 66, (255, 238, 120))
    c.polygon([(84, 150), (156, 150), (144, 206), (96, 206)], (255, 238, 120))
    c.ellipse(100, 92, 16, 22, (255, 252, 214), sil=False)
    c.line([(102, 196), (110, 140), (120, 160), (130, 140), (138, 196)], 6, (244, 156, 60))
    for y in (206, 226, 246):
        c.rrect(92, y, 148, y + 18, 8, (176, 180, 198))
    c.rrect(104, 262, 136, 276, 6, (130, 132, 150))
    return c.finish(pivot=(120, 276), border=6)


def _tug_paw(c, x, y, sgn, fur, line, cuff=None):
    """A paw entering from the bubble edge (sgn=-1 from the left, +1 from the right) gripping at (x, y)."""
    c.line([(x + sgn * 70, y + 6), (x + sgn * 8, y)], 30, fur)
    if cuff:
        c.rrect(x + sgn * 70 - 16, y - 18, x + sgn * 70 + 16, y + 26, 10, cuff)
    c.ellipse(x, y, 22, 24, fur)
    for dy in (-12, 0, 12):
        c.line([(x - sgn * 4, y + dy), (x - sgn * 16, y + dy)], 3, line)


def choice_bubble(kind, ring):
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    if kind == "grab":
        # one cookie, two paws pulling it apart in a tug-of-war
        _cookie_art(c, 125, 132, 50)
        _tug_paw(c, 82, 132, -1, (226, 214, 242), (190, 176, 216), (80, 182, 235))
        _tug_paw(c, 168, 132, 1, (198, 134, 80), (150, 96, 58))
        for sgn in (-1, 1):
            for k, dy in enumerate((-58, -40)):
                x0 = 125 + sgn * (40 + 10 * k)
                c.line([(x0, 132 + dy), (x0 + sgn * 26, 132 + dy - 8)], 6, (240, 110, 100))
    else:
        r = 52
        for side, dx, ang in (("l", -20, 8), ("r", 20, -8)):
            sub = Cut(140, 140)
            _cookie_art(sub, 70, 70, r)
            crack = _crack(r, 18)
            far = 150 if side == "l" else -10
            er = crack + [(far, crack[-1][1] + 20), (far, crack[0][1] - 20)]
            sub.d.polygon([(x * 3, y * 3) for x, y in er], fill=(0, 0, 0, 0))
            sub.line(crack, 4, DOUGH_BREAK)
            piece = sub.img.rotate(ang, resample=Image.BICUBIC, center=(70 * 3, 70 * 3))
            c.img.alpha_composite(piece, (int((125 + dx - 70) * 3), int((128 - 70) * 3)))
    return c.finish(pivot=(125, 125), border=7)


def poof():
    c = Cut(240, 130)
    for cx, cy, r in ((60, 80, 36), (100, 60, 44), (150, 66, 40), (190, 86, 30), (124, 92, 34)):
        c.ellipse(cx, cy, r, r * 0.86, (250, 248, 255))
    return c.finish(pivot=(120, 110), border=4, shadow_alpha=0.15)


def wobble_lines():
    c = Cut(70, 120)
    for i, x in enumerate((14, 36, 58)):
        pts = [(x + 5 * math.sin(y / 9 + i), y) for y in range(10, 110 - abs(i - 1) * 20, 5)]
        c.line(pts, 6, (255, 246, 214), sil=True)
    return c.finish(pivot=(35, 60), border=3, shadow_alpha=0.15)


# ---------------------------------------------------------------- sounds (original synthesis)
_rng = np.random.default_rng(303)
SR = A.SR


def _t(d):
    return np.arange(int(d * SR)) / SR


def _lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def crunch(vel=1.0, dur=0.34, n=6):
    """Bitey cookie crunch: a cluster of crackly noise grains."""
    out = np.zeros(int((dur + 0.08) * SR))
    starts = np.sort(_rng.uniform(0, dur - 0.04, n))
    for i, s0 in enumerate(starts):
        t = _t(0.05)
        nz = _rng.normal(0, 1, len(t))
        g = (nz - _lp(nz, 3)) * 0.6 + (_lp(nz, 3) - _lp(nz, 14)) * 0.9
        g *= np.exp(-t * (70 + 25 * i)) * (1 - 0.1 * i)
        k = int(s0 * SR)
        out[k:k + len(g)] += g
    return vel * 0.9 * out


def crack(vel=1.0):
    """Cookie snapping in half: sharp snap + a little patter of crumbs."""
    t = _t(0.35)
    nz = _rng.normal(0, 1, len(t))
    snap = (nz - _lp(nz, 2)) * np.exp(-t * 120)
    f = 1700 * np.exp(-t * 30) + 600
    tone = 0.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 60)
    out = snap + tone
    for s0 in (0.07, 0.11, 0.16, 0.2, 0.26):
        tt = _t(0.02)
        g = _rng.normal(0, 1, len(tt)) * np.exp(-tt * 300) * 0.35
        k = int(s0 * SR)
        out[k:k + len(g)] += g
    return vel * 0.9 * out


def creak(dur=0.55, vel=1.0):
    """Rubbery tug-of-war 'nnngh' strain: buzzy tone wobbling up."""
    t = _t(dur)
    f = 190 + 120 * t / dur + 22 * np.sin(2 * np.pi * 8 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)
    y = _lp(y, 6)
    env = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.06) * (0.75 + 0.25 * np.sin(2 * np.pi * 12 * t))
    return vel * 0.35 * env * y


def slide_whistle(dur=0.5, f0=600, f1=1400, vel=1.0):
    t = _t(dur)
    f = f0 * (f1 / f0) ** (t / dur) * (1 + 0.015 * np.sin(2 * np.pi * 7 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.12 * np.sin(2 * ph)
    env = np.minimum(1, t / 0.04) * np.minimum(1, (dur - t) / 0.06)
    return vel * 0.4 * env * y


def thump(vel=1.0):
    """Soft bottom-landing 'poomf' (no hurt): low sine plus a cushiony puff."""
    t = _t(0.4)
    f = 95 * np.exp(-t * 4) + 50
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    nz = _rng.normal(0, 1, len(t))
    puff = (_lp(nz, 20) - _lp(nz, 90)) * np.exp(-t * 14) * 2.0
    return vel * 0.8 * (body + puff) * np.minimum(1, t / 0.004)


def coin_wobble(dur=0.7, vel=1.0):
    """The cookie rocking to a stop on the plate: clicks speeding up and fading, then 'ting'."""
    out = np.zeros(int((dur + 1.0) * SR))
    tt, gap, k = 0.0, 0.11, 0
    while tt < dur:
        t = _t(0.05)
        f = 1250 if k % 2 else 980
        g = np.sin(2 * np.pi * f * t) * np.exp(-t * 90) * (1 - 0.7 * tt / dur)
        s = int(tt * SR)
        out[s:s + len(g)] += g * 0.5
        tt += gap
        gap = max(0.025, gap * 0.8)
        k += 1
    g = A.glock(A.midi(100), 0.9, 0.5)
    s = int(dur * SR)
    out[s:s + len(g)] += g
    return vel * out


def ding(vel=1.0):
    out = np.zeros(int(1.4 * SR))
    for i, m in enumerate((91, 96, 103)):
        g = A.glock(A.midi(m), 1.1, vel * 0.55)
        s = int(i * 0.06 * SR)
        out[s:s + len(g)] += g
    return out


def nom(vel=1.0):
    """A tiny happy 'mm!' made from a soft filtered tone."""
    t = _t(0.22)
    f = 260 + 90 * t / 0.22
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.35 * np.sin(2 * ph)
    env = np.sin(np.pi * t / 0.22) ** 1.5
    return vel * 0.45 * env * y
