"""Playground setting, the swing, the "take turns" sign, choice bubbles, dizzy eyes and extra
sounds for Episode 8.

Everything is a hand-made paper cut-out (paperlib.Cut) or synthesized sound (numpy), in the same
style as the shared modules, which are only imported, never edited. Pip the duckling and its mini
icons come from props_park so Pip looks exactly as in Episode 4.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audio as A  # noqa: E402
import props_park as PP  # noqa: E402
import scene  # noqa: E402
from characters import EYE  # noqa: E402
from characters import SNIP as SNIP_COL  # noqa: E402
from paperlib import Cut, grain, place, star_pts  # noqa: E402

W, H = scene.W, scene.H
GROUND_Y = 1440          # where everyone stands
SWING_X = 560            # the swing's resting centre
HOOK_Y = 380             # where the chains hang from the top bar
CHAIN_DX = 125           # chains hang this far left/right of the swing centre
CHAIN_L = 870            # hook -> seat top
SEAT_HW = 138            # half width of the seat plank

SKY_TOP = (120, 184, 236)
SKY_LOW = (255, 222, 196)
TILE_A = (236, 148, 124)
TILE_B = (244, 166, 142)
TILE_SEAM = (250, 190, 168)
FRAME = (78, 120, 214)          # swing frame: blue pipes with yellow joints
FRAME_DARK = (58, 92, 176)
JOINT = (255, 200, 64)
SEAT = (238, 88, 84)
SEAT_DARK = (198, 60, 66)
CHAIN_DARK = (92, 98, 116)
CHAIN_LIGHT = (196, 202, 216)
SLIDE = (255, 196, 60)
SLIDE_DARK = (236, 156, 40)
LADDER = (232, 96, 96)
SAND = (246, 214, 150)
SAND_DARK = (226, 186, 118)
RIM = (222, 140, 92)
FENCE = ((255, 170, 160), (255, 222, 140), (170, 220, 170), (190, 180, 240))


# ================================================================ background
def _sky():
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / 0.7, 0, 1) ** 1.4
    top, low = np.array(SKY_TOP, np.float32), np.array(SKY_LOW, np.float32)
    rgb = top[None, None, :] * (1 - k[..., None]) + low[None, None, :] * k[..., None]
    rgb = np.repeat(rgb, W, axis=1)
    a = np.full((H, W, 1), 255, np.float32)
    img = Image.fromarray(np.concatenate([rgb, a], axis=2).clip(0, 255).astype(np.uint8), "RGBA")
    return grain(img, 0.03)


def _lollipop_trees():
    """Round little trees on sticks, far away behind the fence."""
    c = Cut(1140, 420)
    for x, r, col in ((90, 120, (126, 196, 132)), (300, 96, (150, 206, 120)), (560, 80, (126, 196, 132)),
                      (790, 92, (150, 206, 120)), (1030, 124, (126, 196, 132))):
        c.rrect(x - 12, 160, x + 12, 420, 8, (176, 128, 92))
        c.ellipse(x, 170, r, r * 0.95, col)
        c.ellipse(x - r * 0.3, 170 - r * 0.3, r * 0.4, r * 0.3, (186, 228, 160), sil=False)
    return c.finish(pivot=(30, 0), border=5, shadow_alpha=0.15)


def _fence():
    c = Cut(1140, 220)
    c.rrect(0, 70, 1140, 96, 8, (250, 244, 232))
    c.rrect(0, 150, 1140, 176, 8, (250, 244, 232))
    for i, x in enumerate(range(10, 1140, 76)):
        col = FENCE[i % 4]
        c.polygon([(x, 40), (x + 26, 6), (x + 52, 40), (x + 52, 220), (x, 220)], col)
    return c.finish(pivot=(30, 0), border=5, shadow_alpha=0.18)


def _slide():
    """A little slide far back (ladder on the right, chute down to the left)."""
    c = Cut(420, 360)
    for x in (300, 380):                                        # ladder rails
        c.rrect(x - 9, 40, x + 9, 360, 6, LADDER)
    for y in range(90, 350, 52):
        c.rrect(300, y, 380, y + 12, 5, LADDER)
    c.rrect(250, 40, 400, 62, 8, SLIDE_DARK)                    # platform
    for x in (262, 388):
        c.rrect(x - 7, 0, x + 7, 50, 5, LADDER)                 # handrail posts
    c.rrect(255, 0, 395, 14, 7, LADDER)
    c.polygon([(256, 46), (300, 62), (70, 330), (0, 360), (0, 320), (40, 300)], SLIDE)   # chute
    c.polygon([(300, 62), (288, 48), (40, 300), (64, 312)], SLIDE_DARK, sil=False)
    return c.finish(pivot=(0, 360), border=5, shadow_alpha=0.2)


def _tiles():
    """Soft rubber playground tiles, rows getting a little taller towards the viewer."""
    top = 1320
    c = Cut(W, H - top)
    c.rrect(0, 0, W, H - top, 0, TILE_A)
    y, row = 0.0, 0
    while y < H - top:
        hgt = 60 + row * 26
        off = 0 if row % 2 == 0 else 0.5
        wdt = 180 + row * 30
        x = -wdt * off
        col = 0
        while x < W:
            if (row + col) % 2 == 0:
                c.rrect(x + 3, y + 3, x + wdt - 3, y + hgt - 3, 10, TILE_B, sil=False)
            x += wdt
            col += 1
        c.line([(0, y), (W, y)], 4, TILE_SEAM)
        y += hgt
        row += 1
    return c.finish(pivot=(0, 0), border=0, shadow_alpha=0.0)


def _frame():
    """The swing frame: a top bar with splayed legs at each end."""
    c = Cut(1000, 1140)
    ox, oy = 100, 330                                           # sprite offset (world x - ox, y - oy)

    def P(x, y):
        return x - ox, y - oy
    for (x0, x1) in ((205, 140), (915, 980)):                   # legs
        c.line([P(x0, 365), P(x1, 1455)], 34, FRAME, sil=True)
        c.line([P(x0 + 5, 380), P(x1 + 5, 1440)], 8, FRAME_DARK)
        c.ellipse(*P(x1, 1450), 34, 14, FRAME_DARK)
    c.rrect(*P(150, 346), *P(970, 386), 20, FRAME)              # top bar
    c.line([P(170, 372), P(950, 372)], 6, FRAME_DARK)
    for x in (205, 915):
        c.ellipse(*P(x, 366), 34, 34, JOINT)
        c.ellipse(*P(x, 366), 12, 12, (230, 160, 40), sil=False)
    for x in (SWING_X - CHAIN_DX, SWING_X + CHAIN_DX):          # chain hooks
        c.rrect(*P(x - 16, 372), *P(x + 16, HOOK_Y + 10), 8, (150, 156, 172))
    return c.finish(pivot=(0, 0), border=5, shadow_alpha=0.22)


def _sandpit():
    c = Cut(440, 220)
    c.ellipse(220, 120, 216, 96, RIM)
    c.ellipse(220, 116, 192, 78, SAND, sil=False)
    for cx, cy, r in ((120, 120, 30), (300, 100, 40), (230, 150, 24)):
        c.ellipse(cx, cy, r * 1.4, r * 0.6, SAND_DARK, sil=False)
    c.polygon([(250, 70), (300, 70), (292, 128), (258, 128)], (84, 182, 222))     # bucket
    c.ellipse(275, 70, 26, 8, (60, 150, 196))
    c.arc(275, 64, 22, 30, 190, 350, 4, (60, 150, 196))
    c.line([(140, 60), (196, 118)], 8, (240, 118, 70))                            # spade
    c.ellipse(204, 126, 18, 12, (240, 118, 70), theta=40)
    return c.finish(pivot=(0, 0), border=5, shadow_alpha=0.2)


def cloud(w=300, h=130):
    return PP.cloud(w, h)


def background():
    """Static playground layers (clouds are drawn per frame so they can drift)."""
    bg = _sky()
    place(bg, _lollipop_trees(), (0, 905))
    place(bg, _slide(), (640, 1300))
    place(bg, _fence(), (0, 1120))
    place(bg, _tiles(), (0, 1320))
    place(bg, _frame(), (100, 330))
    place(bg, _sandpit(), (-70, 1540))
    return bg


# ================================================================ the swing seat and dangling feet
def seat():
    c = Cut(2 * SEAT_HW + 20, 64)
    cx = SEAT_HW + 10
    c.rrect(10, 4, 2 * SEAT_HW + 10, 46, 18, SEAT)
    c.rrect(22, 30, 2 * SEAT_HW - 2, 44, 8, SEAT_DARK, sil=False)
    for s in (-1, 1):
        c.ellipse(cx + s * CHAIN_DX, 14, 13, 13, (150, 156, 172))
        c.ellipse(cx + s * CHAIN_DX, 14, 6, 6, (110, 116, 132), sil=False)
    return c.finish(pivot=(cx, 8), border=4, shadow_alpha=0.25)


def snip_feet():
    """Snip's two feet dangling over the front of the seat. Pivot = between them at seat top."""
    c = Cut(200, 110)
    for x in (62, 138):
        c.ellipse(x, 62, 34, 40, SNIP_COL["fur"])
        c.ellipse(x, 84, 18, 12, SNIP_COL["ear_in"], sil=False)
    return c.finish(pivot=(100, 22), border=5)


def pip_feet():
    c = Cut(170, 90)
    for x in (55, 115):
        c.rrect(x - 6, 0, x + 6, 50, 5, PP.BEAK_DARK)
        c.ellipse(x, 58, 26, 13, PP.BEAK)
        for dx in (-15, 0, 15):
            c.ellipse(x + dx, 66, 8, 7, PP.BEAK)
    return c.finish(pivot=(85, 4), border=4)


# ================================================================ icons
def _mini_swing(c, cx, top, bottom, hw):
    for s in (-1, 1):
        c.line([(cx + s * hw, top), (cx + s * hw, bottom)], 5, CHAIN_DARK)
    c.rrect(cx - hw - 14, top - 6, cx + hw + 14, top + 4, 4, FRAME, sil=False)
    c.rrect(cx - hw - 10, bottom - 4, cx + hw + 10, bottom + 12, 6, SEAT, sil=False)


def choice_bubble_swing(kind, ring):
    """'keep' = Snip stays on the swing; 'give' = Pip gets a turn."""
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    _mini_swing(c, 125, 44, 182, 62)
    if kind == "keep":
        PP.draw_bunny_head(c, 125, 136, 88)
    else:
        PP.draw_duck_head(c, 125, 136, 92)
    return c.finish(pivot=(125, 125), border=7)


def _arrow_arc(c, cx, cy, r, a0, a1, col, width=13):
    """Curved arrow along a circle from angle a0 to a1 (degrees, screen coords), head at a1."""
    n = 24
    pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
            cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    c.line(pts[:-3], width, col)
    tip = pts[-1]
    d = 1 if a1 > a0 else -1
    tang = math.radians(a1 + d * 90)                            # direction of travel
    back = (tip[0] - 30 * math.cos(tang), tip[1] - 30 * math.sin(tang))
    nx, ny = -math.sin(tang), math.cos(tang)
    c.polygon([(tip[0] + 6 * math.cos(tang), tip[1] + 6 * math.sin(tang)),
               (back[0] + 20 * nx, back[1] + 20 * ny), (back[0] - 20 * nx, back[1] - 20 * ny)], col)


def sign_turns():
    """Crinkle's sign: Snip and Pip with two curved arrows going round -- take turns."""
    c = Cut(440, 570)
    scene._sign_card(c)
    PP.draw_bunny_head(c, 108, 146, 116)
    PP.draw_duck_head(c, 332, 136, 118)
    _arrow_arc(c, 220, 140, 112, 212, 328, (90, 190, 120))      # over the top: Snip -> Pip
    _arrow_arc(c, 220, 140, 112, 32, 148, (84, 150, 230))       # underneath: Pip -> Snip
    return c.finish(pivot=(220, 552))


def thought_swing():
    """Pip's wish: a cloud with Pip on a little swing. Pivot = the smallest trailing dot."""
    c = Cut(230, 250)
    for cx, cy, r in ((115, 92, 72), (58, 100, 46), (172, 100, 46), (86, 52, 44), (148, 50, 46),
                      (115, 140, 50), (66, 136, 38), (166, 136, 38)):
        c.ellipse(cx, cy, r, r * 0.95, (255, 255, 255))
    c.ellipse(96, 204, 15, 14, (255, 255, 255))
    c.ellipse(84, 236, 9, 9, (255, 255, 255))
    _mini_swing(c, 115, 36, 150, 50)
    PP.draw_duck_head(c, 115, 112, 72)
    return c.finish(pivot=(84, 236), border=5, shadow_alpha=0.22)


def spiral_eye(r=27):
    """A dizzy spiral that covers one of Snip's eyes (fur-coloured disc + dark spiral)."""
    s = int(2 * r + 6)
    c = Cut(s, s)
    cx = cy = s / 2
    c.ellipse(cx, cy, r, r, SNIP_COL["fur"])
    pts = []
    turns = 2.6
    for i in range(80):
        k = i / 79
        a = 2 * math.pi * turns * k
        rr = 2 + (r - 6) * k
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    c.line(pts, 4.6, EYE)
    return c.finish(pivot=(cx, cy), border=0, shadow_alpha=0.0)


def dizzy_star(col=(255, 214, 64)):
    c = Cut(70, 70)
    c.polygon(star_pts(35, 35, 30, 13), col)
    return c.finish(pivot=(35, 35), border=4, shadow_alpha=0.15)


def swirl_line(r=60, sweep=110):
    """A curved white motion line (spin streak)."""
    s = 2 * r + 30
    c = Cut(s, s)
    pts = [(s / 2 + r * math.cos(math.radians(a)), s / 2 + r * math.sin(math.radians(a))) for a in range(0, sweep, 6)]
    c.line(pts, 9, (255, 255, 255), sil=True)
    return c.finish(pivot=(s / 2, s / 2), border=0, shadow_alpha=0.15)


# ================================================================ chains (drawn per frame, supersampled)
def draw_chains(f, strands, ss=2):
    """strands: list of polylines in frame coords. Paper-ish chain: dark outline, light dashed links."""
    xs = [p[0] for s in strands for p in s]
    ys = [p[1] for s in strands for p in s]
    x0, y0 = int(min(xs)) - 16, int(min(ys)) - 16
    x1, y1 = int(max(xs)) + 16, int(max(ys)) + 16
    w, h = (x1 - x0) * ss, (y1 - y0) * ss
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    def loc(p):
        return ((p[0] - x0) * ss, (p[1] - y0) * ss)
    for s in strands:
        pts = [loc(p) for p in s]
        d.line(pts, fill=CHAIN_DARK + (255,), width=12 * ss, joint="curve")
        for p in (pts[0], pts[-1]):
            d.ellipse([p[0] - 6 * ss, p[1] - 6 * ss, p[0] + 6 * ss, p[1] + 6 * ss], fill=CHAIN_DARK + (255,))
    for s in strands:                                            # light links, dashed along each strand
        pts = [loc(p) for p in s]
        acc = 0.0
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay)
            if L < 1e-6:
                continue
            k = 0.0
            while k < L:
                ph = (acc + k) % (22 * ss)
                if ph < 13 * ss:
                    e = min(L, k + 13 * ss - ph)
                    d.line([(ax + (bx - ax) * k / L, ay + (by - ay) * k / L),
                            (ax + (bx - ax) * e / L, ay + (by - ay) * e / L)], fill=CHAIN_LIGHT + (255,), width=4 * ss)
                    k = e + 0.01
                else:
                    k += 22 * ss - ph
            acc += L
    lay = lay.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    f.alpha_composite(lay, (x0, y0))


# ================================================================ sounds (original, synthesized)
SR = A.SR


def _t(d):
    return np.arange(int(d * SR)) / SR


def creak(vel=1.0, up=True):
    """A soft swing-chain squeak: a short rough glide."""
    d = 0.22
    t = _t(d)
    f = (820 + 420 * t / d) if up else (1240 - 420 * t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.2 * np.sin(3.01 * ph)
    y *= 0.7 + 0.3 * np.sign(np.sin(2 * np.pi * 70 * t))
    env = np.sin(np.pi * t / d) ** 1.5
    return vel * 0.16 * env * y


def ratchet(n=8, dur=0.7, vel=1.0):
    """Chains twisting up: quick little clicks, speeding up."""
    out = np.zeros(int((dur + 0.1) * SR))
    for i in range(n):
        tt = dur * (i / n) ** 0.8
        t = _t(0.03)
        click = np.sin(2 * np.pi * (2400 + 300 * (i % 2)) * t) * np.exp(-t * 180)
        s = int(tt * SR)
        out[s:s + len(click)] += click
    return vel * 0.35 * out


def whirr(dur=1.0, vel=1.0):
    """Spinning round: a whirly tone that speeds up then slows (rate follows the spin)."""
    t = _t(dur)
    p = t / dur
    speed = np.sin(np.pi * p) ** 0.8
    f = 380 + 520 * speed
    ph = 2 * np.pi * np.cumsum(f) / SR
    wob = 0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(4 + 14 * speed) / SR)
    y = np.sin(ph) * (0.6 + 0.4 * wob)
    return vel * 0.3 * speed * y


def dizzy(dur=1.0, vel=1.0):
    """Woozy 'wooo-wooo': a sliding, wobbling tone falling slowly."""
    t = _t(dur)
    f = A.midi(79) * (1 - 0.25 * t / dur) * (1 + 0.08 * np.sin(2 * np.pi * 4.5 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.25)
    return vel * 0.3 * env * y


def giggle(vel=1.0, base=740, n=4):
    """A tiny 'hee-hee-hee' made of short falling sine syllables."""
    out = np.zeros(int((0.13 * n + 0.2) * SR))
    for i in range(n):
        d = 0.09
        t = _t(d)
        f = base * (1.0 - 0.04 * i) * (1 - 0.18 * t / d)
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.sin(np.pi * t / d)
        s = int(i * 0.13 * SR)
        out[s:s + len(y)] += y
    return vel * 0.28 * out


def wheee(dur=0.6, vel=1.0):
    """A happy rising-then-falling whistle glide for swinging high."""
    t = _t(dur)
    p = t / dur
    f = 700 + 700 * np.sin(np.pi * p) ** 0.7
    y = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.01 * np.sin(2 * np.pi * 7 * t))) / SR)
    return vel * 0.25 * np.sin(np.pi * p) ** 0.5 * y
