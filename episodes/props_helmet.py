"""Garden setting, the paper tricycle, the bike helmet, icons and extra sounds for Episode 7.

Everything is a hand-made paper cut-out (paperlib.Cut) or synthesized sound (numpy), in the
same style as the shared modules, which are only imported, never edited. A few park pieces
(sky, sun, clouds, little flowers, bunny-head icon, chirp) are borrowed from props_park.

Coordinates of the helmet are "head-local": (0, 0) is Snip's head pivot (scale 1.15), y down.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audio as A  # noqa: E402
import props_park as PK  # noqa: E402
import scene  # noqa: E402
from characters import EYE  # noqa: E402
from characters import SNIP as SNIP_COL  # noqa: E402
from characters import _mirror  # noqa: E402
from paperlib import Cut, Sprite, grain, heart_pts, place, star_pts  # noqa: E402,F401

W, H = scene.W, scene.H
GROUND = 1500            # where the trike wheels and Crinkle stand (middle of the path)
HOOK = (640, 1000)       # the hook on the fence post (helmet hangs below it by its strap)
BUMP_X = 548             # a little stone hump in the path

GRASS = (128, 200, 104)
GRASS_LIGHT = (150, 214, 120)
GRASS_DARK = (98, 170, 86)
HEDGE = (92, 164, 100)
HEDGE_LIGHT = (116, 186, 112)
FENCE = (255, 250, 238)
FENCE_SHADE = (230, 222, 206)
PATH = (240, 206, 150)
PATH_EDGE = (214, 172, 112)
PATH_STONE = (228, 190, 132)
TRUNK = (150, 102, 70)
TRUNK_DARK = (118, 80, 54)
LEAF = (96, 176, 96)
LEAF_LIGHT = (128, 198, 108)
LEAF_DARK = (72, 148, 82)
APPLE = (240, 84, 84)

TRIKE = (236, 70, 82)            # shiny red frame
TRIKE_DARK = (196, 48, 66)
TRIKE_SHINE = (255, 160, 160)
TYRE = (70, 70, 84)
RIM = (250, 248, 244)
HUB = (255, 206, 72)
SADDLE = (255, 204, 62)
SADDLE_DARK = (226, 164, 40)
GRIP = (84, 182, 222)

HELMET = (255, 150, 40)          # bright orange
HELMET_DARK = (230, 110, 30)
HELMET_STRIPE = (255, 255, 255)
HOLE = (196, 104, 40)
HOLE_RIM = (255, 226, 170)
STRAP = (96, 92, 150)
BUCKLE = (255, 214, 64)
BUCKLE_DARK = (210, 160, 40)

FUR = SNIP_COL["fur"]


# ================================================================ background
def _hedge():
    c = Cut(1160, 300)
    rng = np.random.default_rng(3)
    xs = np.arange(-20, 1180, 70)
    for x in xs:
        r = rng.uniform(70, 105)
        c.ellipse(x, 170 - rng.uniform(0, 40), r, r * 0.9, HEDGE)
    c.rrect(0, 170, 1160, 300, 0, HEDGE)
    for x in xs[::2]:
        c.ellipse(x - 12, 130, 36, 26, HEDGE_LIGHT, sil=False)
    return c.finish(pivot=(40, 0), border=5, shadow_alpha=0.15)


def _fence():
    """White picket fence with a sturdy post that has a hook (the helmet's home)."""
    c = Cut(1140, 300)
    for y in (90, 210):
        c.rrect(0, y, 1140, y + 34, 8, FENCE)
        c.line([(10, y + 28), (1130, y + 28)], 4, FENCE_SHADE)
    for x in range(30, 1140, 78):
        c.polygon([(x - 24, 300), (x - 24, 36), (x, 4), (x + 24, 36), (x + 24, 300)], FENCE)
        c.line([(x + 16, 40), (x + 16, 296)], 4, FENCE_SHADE)
    return c.finish(pivot=(30, 0), border=5, shadow_alpha=0.2)


def _post():
    """The sturdy fence post that carries the hook (taller than the pickets)."""
    c = Cut(100, 380)
    c.rrect(12, 20, 88, 380, 8, (246, 238, 220))
    c.rrect(4, 0, 96, 30, 10, (236, 226, 204))
    c.line([(70, 40), (70, 370)], 4, FENCE_SHADE)
    return c.finish(pivot=(50, 0), border=5, shadow_alpha=0.2)


def hook_sprite():
    """Pivot = the bottom of the hook's curve (where the strap loop rests)."""
    c = Cut(90, 110)
    c.rrect(26, 6, 64, 34, 7, (176, 130, 74))                 # little wooden block
    c.line([(45, 28), (45, 74), (54, 88), (68, 84), (70, 68)], 10, (120, 128, 146), sil=True)
    return c.finish(pivot=(50, 86), border=4)


def _lawn():
    c = Cut(1160, 720)
    top = [(x, 30 + 8 * math.sin(x / 80) + 5 * math.sin(x / 27)) for x in range(0, 1161, 10)]
    c.polygon([(0, 720)] + top + [(1160, 720)], GRASS)
    for cx, cy, rx, ry in ((260, 140, 260, 36), (860, 120, 240, 34), (300, 640, 360, 50), (900, 660, 260, 40)):
        c.ellipse(cx, cy, rx, ry, GRASS_LIGHT, sil=False)
    rng = np.random.default_rng(8)
    for _ in range(46):
        x, y = rng.uniform(20, 1140), rng.uniform(60, 700)
        if 150 < y < 360:
            continue                                  # keep the path area clean
        s = rng.uniform(0.7, 1.2)
        for dx, h, lean in ((-7, 18, -5), (0, 26, 0), (7, 17, 5)):
            c.polygon([(x + dx * s - 4 * s, y), (x + dx * s + 4 * s, y), (x + (dx + lean) * s, y - h * s)],
                      GRASS_DARK, sil=False)
    return c.finish(pivot=(40, 0), border=5, shadow_alpha=0.12)


def _path():
    """A curving garden path: wide in front, curving away behind the tree and up to the fence."""
    c = Cut(1200, 420)
    top = []
    bot = []
    for x in range(0, 1201, 12):
        u = x / 1200
        top.append((x, 150 - 70 * math.exp(-((u - 0.02) / 0.12) ** 2) - 120 * math.exp(-((u - 0.98) / 0.16) ** 2)
                    + 6 * math.sin(x / 90)))
        bot.append((x, 300 + 10 * math.sin(x / 140 + 1) - 40 * math.exp(-((u - 0.98) / 0.2) ** 2)))
    c.polygon(top + bot[::-1], PATH_EDGE)
    inner_t = [(x, y + 12) for x, y in top]
    inner_b = [(x, y - 12) for x, y in bot]
    c.polygon(inner_t + inner_b[::-1], PATH, sil=False)
    rng = np.random.default_rng(5)
    for x in range(30, 1180, 64):                             # little stepping-stone flecks
        y = rng.uniform(175, 280)
        c.ellipse(x + rng.uniform(-14, 14), y, rng.uniform(14, 22), rng.uniform(7, 10), PATH_STONE, sil=False)
    return c.finish(pivot=(60, 150), border=4, shadow_alpha=0.12)


def _flower_bed():
    c = Cut(1100, 160)
    rng = np.random.default_rng(11)
    cols = ((255, 150, 170), (255, 255, 255), (190, 160, 240), (255, 200, 90), (255, 120, 120))
    for i, x in enumerate(range(20, 1100, 52)):
        if 560 < x < 760:
            continue                                   # gap below the hook post
        y = 50 + rng.uniform(-14, 14)
        PK._flower(c, x, y, cols[i % len(cols)], rng.uniform(1.0, 1.35))
    for x in range(0, 1100, 40):
        c.ellipse(x + 10, 140, 34, 22, LEAF_DARK)
    return c.finish(pivot=(0, 0), border=4, shadow_alpha=0.15)


def _flowers_front():
    c = Cut(1080, 360)
    spots = ((60, 110, (255, 255, 255), 1.4), (210, 230, (255, 150, 170), 1.2), (380, 120, (255, 200, 90), 1.1),
             (560, 250, (190, 160, 240), 1.3), (720, 140, (255, 255, 255), 1.2), (880, 240, (255, 150, 170), 1.3),
             (1010, 120, (255, 255, 255), 1.1), (470, 40, (255, 120, 120), 0.9), (800, 30, (190, 160, 240), 0.9))
    for x, y, col, s in spots:
        PK._flower(c, x, y, col, s)
    return c.finish(pivot=(0, 0), border=4, shadow_alpha=0.2)


def background():
    """Static garden layers. Sun, clouds, the tree canopy (shakes) and trunk (in front) are per frame."""
    bg = PK._sky()
    place(bg, _hedge(), (0, 930))
    place(bg, _fence(), (0, 1030))
    place(bg, _post(), (HOOK[0], HOOK[1] - 110))
    place(bg, _lawn(), (0, 1270))
    place(bg, _flower_bed(), (-10, 1250))
    place(bg, _path(), (0, GROUND - 80))
    place(bg, _flowers_front(), (0, 1640))
    return bg


def bump():
    c = Cut(110, 50)
    c.ellipse(55, 34, 50, 22, (176, 168, 160))
    c.ellipse(46, 28, 20, 8, (206, 200, 192), sil=False)
    return c.finish(pivot=(55, 46), border=4, shadow_alpha=0.2)


CANOPY_BLOBS = ((260, 220, 170), (110, 300, 140), (420, 300, 140), (200, 110, 130), (370, 130, 120),
                (60, 160, 110), (520, 220, 100), (280, 380, 120), (90, 410, 100), (470, 400, 100))


def canopy():
    c = Cut(700, 560)
    for cx, cy, r in CANOPY_BLOBS:
        c.ellipse(cx + 40, cy + 20, r, r * 0.92, LEAF_DARK)
    for cx, cy, r in CANOPY_BLOBS:
        c.ellipse(cx + 34, cy + 6, r * 0.93, r * 0.84, LEAF, sil=False)
    for cx, cy, r in CANOPY_BLOBS[:6]:
        c.ellipse(cx + 10, cy - 18, r * 0.55, r * 0.42, LEAF_LIGHT, sil=False)
    for ax, ay in ((150, 330), (330, 260), (470, 370), (230, 430), (520, 250)):   # apples
        c.ellipse(ax, ay, 19, 18, APPLE, sil=False)
        c.ellipse(ax - 6, ay - 6, 5, 4, (255, 190, 190), sil=False)
    return c.finish(pivot=(350, 280), border=6)


def trunk():
    c = Cut(300, 1240)
    pts = [(20, 1240), (60, 1190), (82, 1120), (92, 820), (88, 460), (76, 160), (98, 0), (168, 0), (160, 170),
           (166, 470), (170, 820), (178, 1120), (206, 1192), (270, 1240)]
    c.polygon(pts, TRUNK)
    c.polygon([(160, 260), (290, 120), (300, 160), (170, 320)], TRUNK)             # branch into the leaves
    for x0, y0, y1 in ((122, 230, 380), (110, 520, 700), (140, 760, 930), (118, 990, 1120)):
        c.line([(x0, y0), (x0 + 6, (y0 + y1) / 2), (x0 - 2, y1)], 6, TRUNK_DARK)
    c.ellipse(130, 640, 15, 21, TRUNK_DARK, sil=False)
    for x in (40, 230):                                                             # grass tufts at the roots
        for dx, h, lean in ((-8, 22, -5), (0, 30, 0), (8, 20, 5)):
            c.polygon([(x + dx - 5, 1238), (x + dx + 5, 1238), (x + dx + lean, 1238 - h)], GRASS_DARK)
    return c.finish(pivot=(130, 1240), border=6)


def leaf_sprite():
    c = Cut(90, 60)
    c.ellipse(45, 30, 36, 18, LEAF_LIGHT, theta=-12)
    c.line([(14, 36), (76, 24)], 3, LEAF_DARK)
    c.line([(6, 38), (16, 36)], 4, TRUNK)
    return c.finish(pivot=(45, 30), border=3, shadow_alpha=0.2)


# ================================================================ the tricycle
# All trike pieces are drawn relative to (x, GROUND) where x is Snip's x when seated.
# Facing right; a mirrored copy is used when the trike faces left.
SEAT_H = 175                           # Snip's base_y = GROUND - SEAT_H when seated
FRONT_HUB = (150, -118)
FRONT_R = 118
REAR_HUB = (-112, -72)
REAR_R = 72
CRANK = 40
BAR_Y = -282                           # handlebar height (grips at x = +-92)
BAR_X = (-92, 92)
HIP = ((24, -205), (-26, -205))        # near / far leg starts (on Snip's feet)


def wheel(r, spokes=6):
    c = Cut(2 * r + 20, 2 * r + 20)
    o = r + 10
    c.ellipse(o, o, r, r, TYRE)
    c.ellipse(o, o, r - 15, r - 15, RIM, sil=False)
    for i in range(spokes):
        a = math.radians(i * 360 / spokes)
        c.line([(o, o), (o + (r - 18) * math.cos(a), o + (r - 18) * math.sin(a))], 7, (232, 108, 120))
    c.ellipse(o, o, r * 0.26, r * 0.26, HUB, sil=False)
    c.ellipse(o, o, r * 0.1, r * 0.1, TRIKE_DARK, sil=False)
    c.ellipse(o - r * 0.5, o - r * 0.62, r * 0.12, r * 0.06, (255, 255, 255), sil=False)
    return c.finish(pivot=(o, o), border=4)


def _trike_back():
    """Behind Snip: rear deck, the far rear wheel's axle stub, seat post and saddle."""
    c = Cut(420, 280)
    ox, oy = 230, 260                  # local (0, 0) = Snip x, GROUND
    P = lambda x, y: (ox + x, oy + y)  # noqa: E731
    c.line([P(-112, -72), P(-40, -160), P(-8, -186)], 26, TRIKE)            # rear stay up to the saddle
    c.rrect(*P(-190, -96), *P(-30, -72), 10, TRIKE_DARK)                   # rear step / deck
    c.rrect(*P(-186, -100), *P(-34, -88), 6, TRIKE_SHINE, sil=False)
    c.line([P(-8, -186), P(-8, -150)], 18, (150, 150, 165))                 # seat post
    c.ellipse(*P(-6, -196), 82, 24, SADDLE_DARK)
    c.ellipse(*P(-10, -202), 76, 18, SADDLE, sil=False)
    return c.finish(pivot=(ox, oy), border=5)


def _trike_front():
    """In front of Snip: main tube, fork, handlebar stem and the T-bar with grips, bell and streamers."""
    c = Cut(520, 320)
    ox, oy = 210, 300
    P = lambda x, y: (ox + x, oy + y)  # noqa: E731
    c.line([P(-112, -76), P(30, -170), P(128, -248)], 34, TRIKE)             # main tube
    c.line([P(-100, -84), P(26, -168), P(118, -240)], 8, TRIKE_SHINE)
    c.line([P(150, -118), P(128, -262)], 24, TRIKE_DARK)                     # fork
    c.line([P(128, -262), P(60, BAR_Y + 2), P(0, BAR_Y)], 18, (160, 160, 176))   # stem back to the bar
    c.rrect(*P(BAR_X[0] - 8, BAR_Y - 9), *P(BAR_X[1] + 8, BAR_Y + 9), 9, (176, 176, 192))
    for gx in BAR_X:
        c.rrect(*P(gx - 22, BAR_Y - 16), *P(gx + 22, BAR_Y + 16), 14, GRIP)
    c.ellipse(*P(60, BAR_Y - 26), 20, 16, (255, 214, 64))                   # bell
    c.ellipse(*P(54, BAR_Y - 32), 6, 4, (255, 248, 200), sil=False)
    return c.finish(pivot=(ox, oy), border=5)


def streamer(color):
    c = Cut(40, 90)
    c.polygon([(18, 4), (26, 4), (30, 86), (12, 80)], color)
    return c.finish(pivot=(22, 6), border=3, shadow_alpha=0.15)


def crank():
    """Crank arm + pedal block; pivot at the hub, pedal at (0, +CRANK)."""
    c = Cut(70, 110)
    c.line([(35, 30), (35, 30 + CRANK)], 12, (150, 150, 165))
    c.rrect(14, 30 + CRANK - 10, 56, 30 + CRANK + 10, 6, (80, 80, 96))
    return c.finish(pivot=(35, 30), border=3)


def leg():
    """Snip's lower leg, pointing down; pivot = top (on the body foot), length 100 at scale 1."""
    c = Cut(60, 150)
    c.rrect(10, 10, 50, 120, 20, FUR)
    c.ellipse(34, 118, 26, 18, FUR)
    c.ellipse(34, 122, 14, 8, SNIP_COL["ear_in"], sil=False)
    return c.finish(pivot=(30, 20), border=4)


LEG_LEN = 98


class Trike:
    def __init__(self):
        self.wf = wheel(FRONT_R, 6)
        self.wr = wheel(REAR_R, 5)
        self.back = _trike_back()
        self.front = _trike_front()
        self.back_m = _mirror(self.back)
        self.front_m = _mirror(self.front)
        self.crank = crank()
        self.leg = leg()
        self.streamers = [streamer(c) for c in ((255, 214, 64), (84, 182, 222), (240, 92, 140))]

    @staticmethod
    def pt(x, gy, k, dx, dy, lift=0.0, pitch=0.0):
        """Trike-local offset -> canvas. k = facing (+1 right, -1 left, in between while turning)."""
        a = math.radians(pitch)
        rx = dx * math.cos(a) + dy * math.sin(a)
        ry = -dx * math.sin(a) + dy * math.cos(a)
        return x + rx * k, gy + ry - lift

    def draw_back(self, f, x, gy, k, roll, lift=0.0, pitch=0.0, roll_r=None):
        """Far rear wheel + frame behind Snip."""
        ak = max(0.03, abs(k))
        rr = roll * (FRONT_R / REAR_R) if roll_r is None else roll_r
        place(f, self.wr, self.pt(x, gy, k, REAR_HUB[0] + 34, REAR_HUB[1] - 6, lift, pitch),
              angle=-rr * (1 if k >= 0 else -1), sx=ak)
        spr = self.back if k >= 0 else self.back_m
        place(f, spr, self.pt(x, gy, k, 0, 0, lift, pitch), sx=ak, angle=pitch * (1 if k >= 0 else -1))

    def pedals(self, x, gy, k, roll, lift=0.0, pitch=0.0):
        """(near_pedal, far_pedal) canvas points. roll = wheel angle in degrees (forward > 0)."""
        hub = self.pt(x, gy, k, *FRONT_HUB, lift, pitch)
        a = math.radians(roll)
        near = (hub[0] + CRANK * math.sin(a) * k, hub[1] + CRANK * math.cos(a))
        far = (hub[0] - CRANK * math.sin(a) * k, hub[1] - CRANK * math.cos(a))
        return near, far, hub

    def _leg(self, f, hip, ped, seated=1.0):
        dx, dy = ped[0] - hip[0], ped[1] - hip[1]
        d = math.hypot(dx, dy)
        L = min(d, LEG_LEN * 1.7) * seated + LEG_LEN * (1 - seated)
        ang = math.degrees(math.atan2(dx, dy))     # CCW from straight down
        if seated < 1:
            ang = ang * seated
        place(f, self.leg, hip, angle=ang, sy=L / LEG_LEN)

    def draw_front(self, f, x, gy, k, roll, snip_hop=0.0, lift=0.0, pitch=0.0, t=0.0, seated=1.0, roll_r=None):
        """Far leg + far crank, the front wheel, near crank + near leg, then frame, bar and near rear wheel."""
        ak = max(0.03, abs(k))
        sgn = 1 if k >= 0 else -1
        near, far, hub = self.pedals(x, gy, k, roll, lift, pitch)
        hip_n = (x + HIP[0][0] * k, gy + HIP[0][1] - lift - snip_hop)
        hip_f = (x + HIP[1][0] * k, gy + HIP[1][1] - lift - snip_hop)
        place(f, self.crank, hub, angle=(roll + 180) * sgn, sx=ak)
        self._leg(f, hip_f, far, seated)
        place(f, self.wf, hub, angle=-roll * sgn, sx=ak)
        place(f, self.crank, hub, angle=roll * sgn, sx=ak)
        self._leg(f, hip_n, near, seated)
        spr = self.front if k >= 0 else self.front_m
        place(f, spr, self.pt(x, gy, k, 0, 0, lift, pitch), sx=ak, angle=pitch * sgn)
        rr = roll * (FRONT_R / REAR_R) if roll_r is None else roll_r
        place(f, self.wr, self.pt(x, gy, k, *REAR_HUB, lift, pitch), angle=-rr * sgn, sx=ak)
        for i, (gx, s) in enumerate(((BAR_X[0], 0), (BAR_X[1], 1))):     # streamers flutter
            p = self.pt(x, gy, k, gx, BAR_Y + 10, lift, pitch)
            for j in range(2):
                spr2 = self.streamers[(i + j) % 3]
                place(f, spr2, (p[0] + (j * 8 - 4) * k, p[1]), angle=(18 + 10 * math.sin(t * 9 + i + j)) * sgn
                      + 8 * j * sgn, sx=ak)

    def grip_pts(self, x, gy, k, lift=0.0, pitch=0.0):
        return [self.pt(x, gy, k, gx, BAR_Y, lift, pitch) for gx in BAR_X]


# ================================================================ the helmet
# head-local geometry (Snip at scale 1.15): face centre (0, -126), face radii 161 x 140,
# ear pivots (+-57.5, -207) tilted out 9 degrees.
DOME_C = (0, -188)                     # rim line centre (level on the forehead, above the eyes)
DOME_R = (182, 140)
HOLE_C = ((-74, -310), (74, -310))
HOLE_R = (60, 22)
HCX, HCY = 210, 400                    # head-local (0, 0) inside the helmet cut
HANG_DY = -392                         # head-local point of the strap loop's top (sits on the hook)


def _helmet_dome(c, ox, oy, k=1.0, holes=True, sil=True, hole_open=1.0):
    """Paint the helmet into cut c with head-local origin at (ox, oy), scaled by k."""
    P = lambda x, y: (ox + x * k, oy + y * k)  # noqa: E731
    dome = [P(DOME_C[0] + DOME_R[0] * math.cos(a), DOME_C[1] - DOME_R[1] * math.sin(a))
            for a in np.linspace(0, math.pi, 60)]
    c.polygon(dome + [P(-DOME_R[0], DOME_C[1] + 12), P(DOME_R[0], DOME_C[1] + 12)], HELMET, sil)
    shade = [P(DOME_C[0] + DOME_R[0] * 0.98 * math.cos(a), DOME_C[1] - DOME_R[1] * 0.3 * math.sin(a))
             for a in np.linspace(0, math.pi, 40)]
    c.polygon(shade + [P(-DOME_R[0] * 0.98, DOME_C[1] + 10), P(DOME_R[0] * 0.98, DOME_C[1] + 10)], HELMET_DARK,
              False)
    for sx in (-1, 1):                                                   # white racing stripes (vents)
        pts = [P(sx * 30 + sx * 120 * math.sin(a) * 0.9, DOME_C[1] - 145 * math.cos(a) * 0.98)
               for a in np.linspace(0, 1.15, 20)]
        c.line(pts, 16 * k, HELMET_STRIPE)
    c.ellipse(*P(0, -226), 26 * k, 12 * k, (255, 220, 120), False)                         # front vent
    c.rrect(*P(-DOME_R[0] - 4, DOME_C[1] - 8), *P(DOME_R[0] + 4, DOME_C[1] + 14), 10 * k, HELMET_DARK, sil)
    c.rrect(*P(-DOME_R[0] + 6, DOME_C[1] + 4), *P(DOME_R[0] - 6, DOME_C[1] + 10), 3 * k, (255, 236, 200), False)
    c.ellipse(*P(-96, -282), 34 * k, 14 * k, (255, 206, 140), False, theta=-30)            # shine
    if holes:
        for hx, hy in HOLE_C:
            c.ellipse(*P(hx, hy), (HOLE_R[0] + 7) * k, (HOLE_R[1] * hole_open + 6) * k, HOLE_RIM, False)
            c.ellipse(*P(hx, hy + 2), HOLE_R[0] * k, HOLE_R[1] * hole_open * k, HOLE, False)


def _strap_pts(buckled, hanging=False):
    if hanging:            # off the head: straps dangle straight down from the sides
        return [[(-170, -170), (-176, -60), (-172, 20)], [(170, -170), (176, -60), (172, 20)]]
    if buckled:
        return [[(-168, -170), (-150, -60), (-96, 6), (-14, 22)], [(168, -170), (150, -60), (96, 6), (14, 22)]]
    return [[(-168, -170), (-158, -60), (-146, 24)], [(168, -170), (158, -60), (146, 24)]]


def _straps(c, ox, oy, k=1.0, buckled=False, hanging=False):
    P = lambda x, y: (ox + x * k, oy + y * k)  # noqa: E731
    for side in _strap_pts(buckled, hanging):
        c.line([P(*p) for p in side], 13 * k, STRAP, sil=True)
    if buckled:
        c.rrect(*P(-26, 6), *P(26, 38), 8 * k, BUCKLE)
        c.rrect(*P(-12, 15), *P(12, 29), 4 * k, BUCKLE_DARK, False)
    else:
        ends = [s[-1] for s in _strap_pts(False, hanging)]
        for i, (ex, ey) in enumerate(ends):
            if i == 0:
                c.rrect(*P(ex - 14, ey - 4), *P(ex + 14, ey + 26), 6 * k, BUCKLE)           # female half
            else:
                c.polygon([P(ex - 11, ey - 4), P(ex + 11, ey - 4), P(ex + 7, ey + 26), P(ex - 7, ey + 26)], BUCKLE)
                c.line([P(ex, ey + 2), P(ex, ey + 20)], 4 * k, BUCKLE_DARK)


def _cut_finish(c, pivot, **kw):
    return c.finish(pivot=pivot, **kw)


class Helmet:
    """Layered helmet so Snip's ears can pass through the ear holes.

    dome        : full helmet (back layer, also used whole when held / flying / on the hook)
    front       : the part of the dome below the ear holes, minus the holes (drawn over the ears)
    straps_*    : straps worn open / buckled, and dangling (off the head)
    All share the pivot = Snip's head pivot when worn.
    """

    def __init__(self):
        c = Cut(420, 470)
        _helmet_dome(c, HCX, HCY)
        self.dome = c.finish(pivot=(HCX, HCY), border=5)
        self.front = self._front_layer(self.dome)
        self.straps_open = self._strap_sprite(False)
        self.straps_buckled = self._strap_sprite(True)
        self.straps_hang = self._strap_sprite(False, hanging=True)
        c = Cut(420, 470)
        for sx in (-1, 1):
            c.line([(HCX + sx * 168, HCY - 172), (HCX + sx * 60, HCY - 300), (HCX, HCY + HANG_DY)], 12, STRAP,
                   sil=True)
        self.loop = c.finish(pivot=(HCX, HCY), border=4, shadow_alpha=0.22)

    @staticmethod
    def _front_layer(spr):
        a = np.asarray(spr.img).copy()
        h, w = a.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        ly = yy - spr.pivot[1]
        lx = xx - spr.pivot[0]
        keep = ly > HOLE_C[0][1] + 2
        for hx, hy in HOLE_C:
            inside = ((lx - hx) / (HOLE_R[0] + 2)) ** 2 + ((ly - hy - 2) / (HOLE_R[1] + 2)) ** 2 < 1
            keep &= ~inside
        soft = keep.astype(np.float32)
        a[..., 3] = (a[..., 3] * soft).astype(np.uint8)
        return Sprite(Image.fromarray(a, "RGBA"), spr.pivot, None)

    @staticmethod
    def _strap_sprite(buckled, hanging=False):
        c = Cut(420, 470)
        _straps(c, HCX, HCY, 1.0, buckled, hanging)
        return c.finish(pivot=(HCX, HCY), border=4, shadow_alpha=0.22)


def place_helmet_whole(f, hel, pivot, angle=0.0, scale=1.0, hanging=True, alpha=1.0):
    if hanging:
        place(f, hel.straps_hang, pivot, angle=angle, scale=scale, alpha=alpha)
    place(f, hel.dome, pivot, angle=angle, scale=scale, alpha=alpha)


RIM_DY = -DOME_C[1]                    # pivot is this far below the rim centre


def place_helmet_hanging(f, hel, angle=0.0):
    """On the hook: the strap loop hangs from the hook, the helmet below it."""
    piv = (HOOK[0] - HANG_DY * math.sin(math.radians(angle)), HOOK[1] - HANG_DY * math.cos(math.radians(angle)))
    place(f, hel.loop, piv, angle=angle)
    place(f, hel.dome, piv, angle=angle)
    return piv


# ================================================================ icons, bubbles, callout
def draw_helmet_icon(c, cx, cy, size, holes=True):
    """Helmet alone, fitted to `size` px wide, centred on (cx, cy)."""
    k = size / 380
    _helmet_dome(c, cx, cy + 250 * k, k, holes, sil=False)


def draw_trike_icon(c, cx, cy, size):
    k = size / 200
    P = lambda x, y: (cx + x * k, cy + y * k)  # noqa: E731
    for (hx, hy), r in (((-60, 30), 26), ((62, 18), 38)):
        c.ellipse(*P(hx, hy), r * k, r * k, TYRE, False)
        c.ellipse(*P(hx, hy), (r - 8) * k, (r - 8) * k, RIM, False)
        c.ellipse(*P(hx, hy), 7 * k, 7 * k, HUB, False)
    c.line([P(-60, 30), P(-10, -12), P(52, -40), P(62, 18)], 11 * k, TRIKE)
    c.line([P(52, -40), P(30, -60)], 8 * k, (150, 150, 165))
    c.rrect(*P(14, -70), *P(46, -56), 6 * k, GRIP, False)
    c.ellipse(*P(-16, -20), 28 * k, 9 * k, SADDLE, False)


def draw_bunny(c, cx, cy, size, helmet=False):
    """Mini Snip head (size = face width); optionally wearing the helmet with ears through the holes."""
    k = size / 100
    if not helmet:
        PK.draw_bunny_head(c, cx, cy, size)
        return
    PK.draw_bunny_head(c, cx, cy, size)
    # helmet over the top of the head: dome from the brow up, ears poke out of holes
    hk = size / 330
    _helmet_dome(c, cx, cy + 126 * hk + 4 * k, hk, holes=True, sil=False)
    for side in (-1, 1):
        x = cx + side * 21 * k
        c.ellipse(x, cy - 66 * k, 12 * k, 30 * k, FUR, sil=False, theta=-side * 10)
        c.ellipse(x, cy - 62 * k, 6 * k, 20 * k, SNIP_COL["ear_in"], sil=False, theta=-side * 10)
    c.line([(cx - 44 * k, cy - 8 * k), (cx - 34 * k, cy + 32 * k), (cx, cy + 46 * k)], 4 * k, STRAP)
    c.line([(cx + 44 * k, cy - 8 * k), (cx + 34 * k, cy + 32 * k), (cx, cy + 46 * k)], 4 * k, STRAP)
    c.rrect(cx - 7 * k, cy + 41 * k, cx + 7 * k, cy + 51 * k, 3 * k, BUCKLE, False)


def choice_bubble(kind, ring):
    """'bare' = Snip on the trike with a bare head; 'helmet' = Snip on the trike wearing the helmet."""
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    draw_trike_icon(c, 125, 186, 104)
    draw_bunny(c, 122, 112, 100, helmet=(kind == "helmet"))
    return c.finish(pivot=(125, 125), border=7)


def hole_callout(ears=0.0, ring=(90, 190, 120)):
    """Big round card: the helmet's two ear holes; `ears` (0..1) = how far the ears have come up through them."""
    c = Cut(440, 460)
    c.polygon([(170, 380), (250, 380), (214, 452)], ring)                    # tail -> Crinkle's helmet
    c.ellipse(210, 210, 200, 200, ring)
    c.ellipse(210, 210, 180, 180, (255, 255, 255), sil=False)
    k, op = 1.0, 2.3
    ox, oy = 210, 222 + 250 * k
    _helmet_dome(c, ox, oy, k, holes=True, sil=False, hole_open=op)
    for (hx, hy), side in zip(HOLE_C, (-1, 1)):
        x, y = ox + hx * k, oy + hy * k
        if ears > 0:   # ears come up out of the holes
            ry = 18 + 66 * ears
            c.ellipse(x + side * 6 * ears, y + 10 - ry, 40, ry, FUR, sil=False, theta=-side * 8 * ears)
            c.ellipse(x + side * 6 * ears, y + 18 - ry, 20, max(4, ry - 26), SNIP_COL["ear_in"], sil=False,
                      theta=-side * 8 * ears)
            c.chord(x, y + 2, HOLE_R[0] * k + 7, HOLE_R[1] * op * k + 6, 0, 180, HOLE_RIM)
            c.chord(x, y + 4, HOLE_R[0] * k, HOLE_R[1] * op * k * 0.5, 0, 180, HELMET)
        else:
            c.arc(x, y + 2, HOLE_R[0] * k + 14, HOLE_R[1] * op * k + 13, 0, 360, 6, (255, 196, 40))
    return c.finish(pivot=(214, 452), border=7)


def click_burst():
    c = Cut(200, 200)
    c.polygon(star_pts(100, 100, 92, 40, 8, -90), (255, 236, 120))
    c.ellipse(100, 100, 34, 34, (255, 255, 255), sil=False)
    return c.finish(pivot=(100, 100), border=5, shadow_alpha=0.15)


def boing_lines():
    """Little springy motion lines (drawn above a bouncing thing)."""
    c = Cut(240, 120)
    for dx, h in ((-70, 60), (0, 80), (70, 60)):
        pts = [(120 + dx + 10 * math.sin(i * 1.4), 110 - i * h / 8) for i in range(9)]
        c.line(pts, 7, (255, 255, 255), sil=True)
    return c.finish(pivot=(120, 110), border=3, shadow_alpha=0.15)


def glint():
    c = Cut(120, 120)
    c.polygon(star_pts(60, 60, 54, 12, 4, -90), (255, 255, 255))
    return c.finish(pivot=(60, 60), border=3, shadow_alpha=0.1)


def soft_glow(color, r, strength=170):
    yy, xx = np.mgrid[-r:r, -r:r]
    a = np.clip(1 - np.hypot(xx, yy) / r, 0, 1) ** 2 * strength
    img = np.zeros((2 * r, 2 * r, 4), np.uint8)
    img[..., :3] = color
    img[..., 3] = a.astype(np.uint8)
    return Sprite(Image.fromarray(img, "RGBA"), (r, r))


# ================================================================ sounds (original, synthesized)
SR = A.SR


def _t(d):
    return np.arange(int(d * SR)) / SR


def bell(vel=1.0):
    """Trike bell: ring-ring (two bright metallic dings with a fast tremolo)."""
    out = np.zeros(int(0.9 * SR))
    for i in range(2):
        t = _t(0.5)
        f = 2350
        y = sum(a * np.exp(-t * d) * np.sin(2 * np.pi * f * r * t) for r, a, d in
                ((1, 1, 7), (1.51, 0.5, 9), (2.42, 0.3, 14), (3.1, 0.15, 20)))
        y *= 1 + 0.35 * np.sin(2 * np.pi * 28 * t)
        y *= np.minimum(1, t / 0.002)
        s = int(i * 0.17 * SR)
        out[s:s + len(y)] += y
    return vel * 0.22 * out


def click(vel=1.0):
    """Buckle click: two tiny hard clicks."""
    out = np.zeros(int(0.2 * SR))
    rng = np.random.default_rng(21)
    for i, f in enumerate((3200, 2400)):
        t = _t(0.03)
        y = (np.sin(2 * np.pi * f * t) + 0.5 * rng.normal(0, 1, len(t))) * np.exp(-t * 260)
        s = int(i * 0.045 * SR)
        out[s:s + len(y)] += y
    return vel * 0.6 * out


def squeak_pedal(vel=1.0):
    t = _t(0.12)
    f = 1500 + 500 * np.sin(np.pi * t / 0.12)
    return vel * 0.12 * np.sin(np.pi * t / 0.12) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def rustle(dur=0.6, vel=1.0):
    t = _t(dur)
    n = np.random.default_rng(13).normal(0, 1, len(t))
    y = n - np.convolve(n, np.ones(6) / 6, mode="same")
    env = np.sin(np.pi * t / dur) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 17 * t))
    return vel * 0.5 * env * y


def clink(vel=1.0):
    t = _t(0.6)
    y = sum(a * np.exp(-t * d) * np.sin(2 * np.pi * f * t) for f, a, d in ((1800, 1, 9), (2950, 0.6, 14), (4100, 0.3, 20)))
    return vel * 0.25 * y * np.minimum(1, t / 0.002)


def roll(dur=1.0, vel=1.0):
    """Soft rolling wheels on a garden path (low filtered rumble with a gentle pulse)."""
    t = _t(dur)
    n = np.random.default_rng(17).normal(0, 1, len(t))
    y = np.convolve(n, np.ones(40) / 40, mode="same") - np.convolve(n, np.ones(200) / 200, mode="same")
    env = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.12) * (0.75 + 0.25 * np.sin(2 * np.pi * 7 * t))
    return vel * 3.0 * env * y
