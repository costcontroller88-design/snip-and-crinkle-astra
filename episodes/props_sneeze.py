"""Props, scenery and sounds for Episode 6, "Achoo! Elbow Sneeze?" (playroom).

Paper cut-outs (paperlib.Cut) and synthesized audio only. Shared modules are not modified.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import audio as A  # noqa: E402
from characters import CRINKLE, SNIP, Character  # noqa: E402
from paperlib import Cut, grain, heart_pts, mix, place, star_pts  # noqa: E402

W, H = 1080, 1920
FLOOR_Y = 1440
BLOCK = 92                      # block edge (front face)

WALL = (255, 226, 200)
WALL_STRIPE = (255, 236, 216)
FLOOR = (226, 170, 116)
FLOOR_LINE = (204, 148, 98)
RUG = (124, 196, 220)
RUG_IN = (255, 250, 236)
BLOCK_COLORS = ((240, 96, 92), (255, 196, 60), (84, 176, 230), (110, 196, 120))
STAR_GOLD = (255, 206, 60)
PUFF = (236, 244, 252)
PUFF_DARK = (206, 222, 240)


# ---------------------------------------------------------------- background
def _wall():
    k = 2
    img = Image.new("RGBA", (W * k, H * k), WALL + (255,))
    d = ImageDraw.Draw(img)
    for x in range(-40, W + 80, 120):                      # soft vertical stripes
        d.rectangle([x * k, 0, (x + 56) * k, FLOOR_Y * k], fill=WALL_STRIPE)
    for row in range(16):                                  # tiny dots inside the stripes
        for x in range(-12, W + 80, 120):
            y = row * 96 + 40 + (48 if (x // 120) % 2 else 0)
            d.ellipse([(x - 6) * k, (y - 6) * k, (x + 6) * k, (y + 6) * k], fill=(255, 214, 184))
    d.rectangle([0, (FLOOR_Y - 26) * k, W * k, (FLOOR_Y + 4) * k], fill=(255, 252, 244))   # skirting board
    d.rectangle([0, (FLOOR_Y + 4) * k, W * k, H * k], fill=FLOOR)
    for y in range(FLOOR_Y + 70, H, 90):
        d.rectangle([0, y * k, W * k, (y + 4) * k], fill=FLOOR_LINE)
    for i, y in enumerate(range(FLOOR_Y + 4, H, 90)):
        for x in range(-100 + (i % 2) * 160, W, 320):
            d.rectangle([x * k, y * k, (x + 4) * k, (y + 70) * k], fill=FLOOR_LINE)
    return grain(img.resize((W, H), Image.LANCZOS), 0.03)


def _rug():
    c = Cut(1000, 300)
    c.ellipse(500, 150, 492, 140, RUG)
    c.ellipse(500, 150, 440, 118, RUG_IN, sil=False)
    c.ellipse(500, 150, 380, 96, (255, 214, 120), sil=False)
    c.ellipse(500, 150, 320, 76, (250, 150, 160), sil=False)
    c.ellipse(500, 150, 250, 56, RUG_IN, sil=False)
    for i in range(36):                                    # fringe dots
        a = 2 * math.pi * i / 36
        c.ellipse(500 + 470 * math.cos(a), 150 + 130 * math.sin(a), 7, 7, (255, 255, 255), sil=False)
    return c.finish(pivot=(500, 150), border=5, shadow_alpha=0.15)


def _window():
    c = Cut(330, 360)
    c.rrect(0, 0, 330, 360, 24, (255, 255, 255))
    c.rrect(18, 18, 312, 342, 16, (164, 214, 246), sil=False)
    c.ellipse(240, 92, 40, 40, (255, 214, 80), sil=False)
    for cx, cy, r in ((90, 130, 30), (124, 116, 36), (160, 132, 26)):
        c.ellipse(cx, cy, r, r * 0.85, (255, 255, 255), sil=False)
    c.ellipse(200, 280, 70, 40, (140, 206, 120), sil=False)
    c.ellipse(90, 300, 90, 46, (120, 192, 110), sil=False)
    c.rrect(156, 18, 174, 342, 6, (255, 255, 255), sil=False)
    c.rrect(18, 170, 312, 188, 6, (255, 255, 255), sil=False)
    for x0, x1 in ((0, 70), (260, 330)):                   # little curtains
        c.polygon([(x0, 0), (x1, 0), ((x0 + x1) / 2 + (12 if x0 == 0 else -12), 360), (x0, 360) if x0 == 0 else (x1, 360)],
                  (250, 150, 160))
    return c.finish(pivot=(0, 0), border=6)


def _rainbow():
    c = Cut(360, 200)
    for i, col in enumerate(((240, 96, 92), (255, 170, 70), (255, 214, 72), (110, 196, 120), (84, 176, 230))):
        r = 170 - i * 22
        c.chord(180, 186, r, r, 180, 360, col)
    c.chord(180, 186, 60, 60, 180, 360, WALL, sil=False)
    for cx in (40, 320):
        for dx, dy, r in ((-20, 0, 26), (10, -12, 30), (36, 2, 24)):
            c.ellipse(cx + dx, 182 + dy, r, r * 0.85, (255, 255, 255))
    return c.finish(pivot=(180, 100), border=5, shadow_alpha=0.2)


def _shelf():
    c = Cut(300, 300)
    c.rrect(0, 270, 300, 292, 6, (214, 160, 108))
    # stacking-rings toy
    c.rrect(52, 120, 64, 268, 6, (196, 136, 84))
    for i, (w, col) in enumerate(((52, (240, 96, 92)), (44, (255, 196, 60)), (36, (110, 196, 120)), (28, (84, 176, 230)))):
        y = 256 - i * 30
        c.ellipse(58, y, w, 15, col)
    c.ellipse(58, 120, 12, 12, (240, 96, 92))
    # toy drum
    c.rrect(120, 200, 200, 268, 12, (84, 176, 230))
    c.ellipse(160, 200, 40, 12, (255, 252, 240))
    for x in (126, 146, 166, 186):
        c.line([(x, 206), (x + 12, 262)], 4, (255, 214, 72))
    # books (no text)
    for i, (x, h, col) in enumerate(((216, 120, (240, 150, 160)), (240, 100, (255, 196, 60)), (262, 132, (110, 196, 120)))):
        c.rrect(x, 268 - h, x + 22, 268, 4, col)
    # a soft feather pillow
    c.ellipse(240, 110, 52, 34, (255, 244, 250))
    c.ellipse(240, 110, 40, 24, (252, 220, 236), sil=False)
    return c.finish(pivot=(0, 0), border=5)


def background():
    bg = _wall()
    place(bg, _window(), (60, 300))
    place(bg, _rainbow(), (560, 360))
    place(bg, _shelf(), (760, 560))
    place(bg, _rug(), (540, FLOOR_Y + 120))
    return bg


# ---------------------------------------------------------------- blocks, feather
def _emblem(c, kind, cx, cy, s, col=(255, 255, 255)):
    if kind == "circle":
        c.ellipse(cx, cy, s * 0.3, s * 0.3, col, sil=False)
    elif kind == "triangle":
        c.polygon([(cx, cy - s * 0.32), (cx + s * 0.32, cy + s * 0.26), (cx - s * 0.32, cy + s * 0.26)], col, sil=False)
    elif kind == "square":
        c.rrect(cx - s * 0.27, cy - s * 0.27, cx + s * 0.27, cy + s * 0.27, s * 0.06, col, sil=False)
    elif kind == "heart":
        c.polygon(heart_pts(cx, cy + s * 0.03, s * 0.6), col, sil=False)
    elif kind == "star":
        c.polygon(star_pts(cx, cy + s * 0.02, s * 0.36, s * 0.15), col, sil=False)


def block(color, emblem, s=BLOCK):
    """A wooden toy block: front face + a lighter top face. Pivot = centre of the front face."""
    d = s * 0.22
    c = Cut(int(s + d + 10), int(s + d + 10))
    ox, oy = 4, d + 4
    top = mix(color, (255, 255, 255), 0.35)
    side = mix(color, (0, 0, 0), 0.15)
    c.polygon([(ox, oy), (ox + d, oy - d), (ox + s + d, oy - d), (ox + s, oy)], top)
    c.polygon([(ox + s, oy), (ox + s + d, oy - d), (ox + s + d, oy + s - d), (ox + s, oy + s)], side)
    c.rrect(ox, oy, ox + s, oy + s, s * 0.08, color)
    c.rrect(ox + s * 0.08, oy + s * 0.08, ox + s * 0.92, oy + s * 0.92, s * 0.06, mix(color, (255, 255, 255), 0.12), sil=False)
    _emblem(c, emblem, ox + s / 2, oy + s / 2, s)
    return c.finish(pivot=(ox + s / 2, oy + s / 2), border=4)


def tower_blocks():
    return [block(col, em) for col, em in zip(BLOCK_COLORS, ("circle", "triangle", "square", "heart"))]


def star_block():
    return block(STAR_GOLD, "star")


def feather():
    c = Cut(80, 170)
    pts = [(40 + 26 * math.sin(math.pi * t) * (1 - 0.3 * t), 160 - 150 * t) for t in np.linspace(0, 1, 30)]
    pts += [(40 - 22 * math.sin(math.pi * t) * (1 - 0.3 * t), 10 + 150 * t) for t in np.linspace(0, 1, 30)][::-1][::-1]
    left = [(40 - 22 * math.sin(math.pi * t) * (1 - 0.3 * t), 160 - 150 * t) for t in np.linspace(0, 1, 30)]
    right = [(40 + 26 * math.sin(math.pi * t) * (1 - 0.3 * t), 160 - 150 * t) for t in np.linspace(0, 1, 30)]
    c.polygon(right + left[::-1], (255, 246, 252))
    for t in np.linspace(0.15, 0.85, 7):
        y = 160 - 150 * t
        c.line([(40, y), (40 + 18 * math.sin(math.pi * t), y - 14)], 2, (240, 200, 226))
        c.line([(40, y), (40 - 16 * math.sin(math.pi * t), y - 14)], 2, (240, 200, 226))
    c.line([(40, 168), (40, 20)], 3, (236, 170, 206))
    return c.finish(pivot=(40, 160), border=3, shadow_alpha=0.15)


# ---------------------------------------------------------------- sneeze effects
def big_puff():
    """Sneeze cloud blowing to the right. Pivot = the mouth end (left)."""
    c = Cut(560, 320)
    blobs = [(70, 160, 46), (140, 150, 66), (220, 160, 84), (310, 150, 100), (410, 162, 110), (300, 90, 60),
             (420, 84, 64), (300, 230, 64), (430, 240, 66), (500, 150, 52)]
    for (x, y, r) in blobs:
        c.ellipse(x + 4, y + 6, r, r * 0.86, PUFF_DARK)
    for (x, y, r) in blobs:
        c.ellipse(x, y, r * 0.9, r * 0.8, PUFF, sil=False)
    return c.finish(pivot=(30, 160), border=4, shadow_alpha=0.15)


def tiny_puff():
    c = Cut(110, 80)
    for (x, y, r) in ((30, 44, 18), (56, 34, 22), (80, 46, 16)):
        c.ellipse(x, y, r, r * 0.85, PUFF)
    return c.finish(pivot=(55, 40), border=3, shadow_alpha=0.12)


def wind_lines():
    c = Cut(260, 200)
    for i, (y, l) in enumerate(((30, 200), (80, 240), (130, 210), (176, 150))):
        pts = [(10 + x, y + 10 * math.sin(x / 30 + i)) for x in range(0, l, 8)]
        c.line(pts, 8, (255, 255, 255), sil=True)
    return c.finish(pivot=(10, 100), border=3, shadow_alpha=0.12)


def tickle_lines():
    c = Cut(120, 120)
    for k, r in enumerate((30, 46)):
        c.arc(60, 60, r, r, 200, 250, 5, (150, 120, 170))
        c.arc(60, 60, r, r, 290, 340, 5, (150, 120, 170))
    return c.finish(pivot=(60, 60), border=3, shadow_alpha=0.1)


# ---------------------------------------------------------------- elbow-sneeze arm pose
def _elbow_arm(points, fur, width, sleeve=None, paw=None):
    """Bent arm (shoulder -> elbow -> wrist) as one cut-out. points are relative to the shoulder."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    pad = width + 20
    x0, y0 = min(xs) - pad, min(ys) - pad
    w, h = int(max(xs) - x0 + pad), int(max(ys) - y0 + pad)
    c = Cut(w, h)
    loc = [(x - x0, y - y0) for x, y in points]
    c.line(loc, width, fur, sil=True)
    if paw is not None:
        c.ellipse(loc[-1][0], loc[-1][1], width * 0.32, width * 0.26, paw, sil=False)
    if sleeve is not None:
        c.ellipse(loc[0][0], loc[0][1], width * 0.62, width * 0.58, sleeve)
    return c.finish(pivot=loc[0], border=4)


def elbow_pose(kind, head_dy=18.0):
    """(sprite, shoulder offset from the feet) for a sneeze into the elbow.
    Snip uses the right arm, Crinkle the left; the crook of the elbow covers nose and mouth."""
    if kind == "snip":
        ch = Character("snip", 1.15)
        sh = ch.shoulder_pt(0, 0, "r")
        mouth = ch.mouth_pt(0, 0, head_dy=head_dy)
        elbow = (mouth[0] + 8, mouth[1] - 4)
        wrist = (mouth[0] + 124, mouth[1] - 36)
        pts = [(0, 0), (elbow[0] - sh[0], elbow[1] - sh[1]), (wrist[0] - sh[0], wrist[1] - sh[1])]
        return _elbow_arm(pts, SNIP["fur"], 44, sleeve=SNIP["tee"]), sh
    ch = Character("crinkle", 1.2)
    sh = ch.shoulder_pt(0, 0, "l")
    mouth = ch.mouth_pt(0, 0, head_dy=head_dy)
    elbow = (mouth[0] - 10, mouth[1] - 8)
    wrist = (mouth[0] - 146, mouth[1] - 44)
    pts = [(0, 0), (elbow[0] - sh[0], elbow[1] - sh[1]), (wrist[0] - sh[0], wrist[1] - sh[1])]
    return _elbow_arm(pts, CRINKLE["fur"], 52, paw=CRINKLE["muzzle"]), sh


# ---------------------------------------------------------------- choice bubbles
def _mini_snip(c, cx, cy, s):
    fur = SNIP["fur"]
    for dx, th in ((-16, -12), (16, 12)):
        c.ellipse(cx + dx * s, cy - 44 * s, 11 * s, 30 * s, fur, sil=False, theta=th)
        c.ellipse(cx + dx * s, cy - 40 * s, 5 * s, 20 * s, SNIP["ear_in"], sil=False, theta=th)
    c.ellipse(cx, cy, 36 * s, 31 * s, fur, sil=False)
    c.ellipse(cx, cy + 6 * s, 4 * s, 3 * s, SNIP["nose"], sil=False)


def choice_bubble(kind, ring):
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    if kind == "air":                                       # sneezing out into the air: a big spray cloud
        _mini_snip(c, 82, 140, 1.15)
        for (x, y, r) in ((128, 140, 20), (156, 126, 26), (186, 142, 30), (160, 168, 22), (196, 112, 18)):
            c.ellipse(x, y, r, r * 0.86, PUFF_DARK, sil=False)
            c.ellipse(x - 2, y - 2, r * 0.8, r * 0.7, PUFF, sil=False)
        for (x, y) in ((150, 112), (182, 140), (166, 168), (200, 120)):
            c.ellipse(x, y, 6, 6, (150, 214, 88), sil=False)
        c.ellipse(82, 150, 6, 7, (120, 40, 60), sil=False)
    else:                                                   # into the elbow: arm across the face, tiny puff
        _mini_snip(c, 112, 140, 1.15)
        c.line([(176, 196), (112, 152), (164, 124)], 18, SNIP["fur"])
        c.ellipse(176, 196, 13, 12, SNIP["tee"], sil=False)
        for (x, y, r) in ((90, 160, 7), (82, 150, 6)):
            c.ellipse(x, y, r, r, PUFF_DARK, sil=False)
    return c.finish(pivot=(125, 125), border=7)


# ---------------------------------------------------------------- sounds (all synthesized, wordless)
SR = A.SR
_rng = np.random.default_rng(61)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def ah(vel=1.0, f0=300, f1=460, dur=0.42):
    """A small rising 'ahh' breath before a sneeze (wordless vowel made from harmonics + breath)."""
    t = _t(dur)
    f = f0 + (f1 - f0) * (t / dur) ** 1.5
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = sum(a * np.sin(k * ph) for k, a in ((1, 1.0), (2, 0.55), (3, 0.35), (4, 0.18), (5, 0.1)))
    n = _lp(_rng.normal(0, 1, len(t)), 6)
    env = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.06)
    return vel * 0.35 * env * (y + 0.6 * n)


def achoo(vel=1.0, big=True):
    """The sneeze: a short breath-in, then a burst of noise with a falling tone."""
    d = 0.55 if big else 0.25
    t = _t(d)
    n = _rng.normal(0, 1, len(t))
    burst = n - _lp(n, 4 if big else 12)
    f = (900 if big else 500) * np.exp(-t * 6) + 180
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = A._attack(t, 1500) * np.exp(-t * (5 if big else 14))
    y = env * (1.1 * burst + 0.45 * tone)
    if not big:
        y = _lp(y, 18)                                       # muffled into the elbow
    return vel * (1.0 if big else 1.6) * y


def clatter(n=8, vel=1.0, spread=0.7):
    out = np.zeros(int((spread + 0.3) * SR))
    for i in range(n):
        s = int(_rng.uniform(0, spread) * (i + 1) / n * SR)
        h = A.woodblock(bool(i % 2), 0.6 + 0.4 * _rng.random())
        f = 1 + 0.25 * _rng.normal()
        h = np.interp(np.arange(0, len(h), f), np.arange(len(h)), h)
        out[s:s + len(h)] += h[:len(out) - s]
    return vel * out


def swish(dur=0.5, vel=1.0):
    t = _t(dur)
    n = _rng.normal(0, 1, len(t))
    y = _lp(n, 10) - _lp(n, 60)
    return vel * 1.2 * np.sin(np.pi * t / dur) ** 2 * y


def clack(vel=1.0):
    return vel * A.woodblock(False, 1.0)
