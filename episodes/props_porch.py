"""Episode 11 world: a cosy front porch with a garden, one 1920x1920 world in three painted light states.

    import hires; hires.set_res(2)
    import props_porch as P
    world = P.Porch(cam)            # crops the light states to this camera once
    bg = world.background(t)        # sky (gradient, sun, stars, moon) + porch, crossfaded by time
    world.front(f, t)               # railing and corner post: drawn AFTER the characters
    world.albedo                    # the porch in plain daylight colours (light that lands on it uses this)

The porch is painted once in plain daylight colours (the "albedo"), then relit three times (golden, sunset,
early evening) by smooth light fields; the sky is its own layer so the sun can sink behind the hill and the
stars and moon can fade in behind the porch. Everything is built with hires.Cut, so it stays sharp at 2x.

Layout (design units; FLOOR_Y is the characters' floor line on the deck):
  sky above y 240 and to the right of the house (x > 1286); main roof edge y 190-272; upper storey 272-470;
  porch roof 470-590, eave board 586-618; lower house wall x 0-1270, y 618-1390 (plain: no siding lines);
  door x 160-400 (from y 700); window x 450-640, y 930-1140; bench x 380-560, seat top FLOOR-110;
  projection wall x 680-1240, y 640-1100 (nothing on it); house corner trim x 1258-1286;
  deck y 1390-1560 (x < 1512), fascia 1560-1590, one low step x 760-1160 (1590-1628), path below;
  railing x 1300-1470 (base 1500, top 1282) with three heart cut-outs at FLOOR-150, corner post x 1476-1510;
  garden x > 1512: hill line ~1190, fence 1300-1430, autumn tree at the far right, pumpkin patch and watering
  can near the bottom of the landscape frame; sun r 55 at x 1730 sinking from y 1080 behind the hill.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hires  # noqa: E402
from hires import Cut  # noqa: E402
from paperlib import ease_in_out, grain, heart_pts, mix, place, seg, star_pts  # noqa: E402

WORLD_W, WORLD_H = 1920, 1920
FLOOR_Y = 1480                        # the characters' feet
LAND_Y0 = 560                         # landscape rows 560..1640
VERT_X0 = 420                         # vertical columns 420..1500 (wall, pumpkin and step centred)
EAVE_Y = 600
WALL_TOP = 618
WALL_BASE = 1390                      # where the house wall meets the deck
HOUSE_X1 = 1286                       # right edge of the house (corner trim)
DECK_FRONT = 1560
DECK_X1 = 1512
HILL_Y = 1190

DOOR = (160, 400, 700)                # x0, x1, top
WINDOW = (450, 640, 930, 1140)        # x0, x1, y0, y1
BENCH = (380, 560)                    # x0, x1; seat top at FLOOR_Y - 110
BENCH_SEAT_Y = FLOOR_Y - 110
MARKER_BOX_AT = (520, BENCH_SEAT_Y + 2)
PROJ_WALL = (680, 1240, 640, 1100)    # the plain wall that receives the giant face
RAIL = (1300, 1470, 1282, 1500)       # x0, x1, top, base
RAIL_HEARTS = ((1340, FLOOR_Y - 150), (1386, FLOOR_Y - 150), (1432, FLOOR_Y - 150))
RAIL_HEART_W = 32
POST = (1476, 1510)
STEP = (760, 1160, 1590, 1628)
SUN_X, SUN_Y0, SUN_Y1, SUN_R = 1730, 1040, 1215, 55
MOON_AT = (1560, 700)
TREE_AT = (1895, 1300)

# ---------------------------------------------------------------- daylight colours (albedo)
HOUSE = (250, 234, 200)
TRIM = (255, 250, 238)
ROOF = (184, 98, 78)
ROOF_DARK = (160, 80, 64)
DOOR_COL = (72, 146, 154)
DOOR_DARK = (56, 120, 128)
BRASS = (236, 186, 84)
GLASS = (132, 168, 206)
CURTAIN = (240, 150, 128)
WOOD = (224, 166, 110)
WOOD_LINE = (196, 136, 86)
WOOD_DARK = (176, 116, 74)
BENCH_COL = (138, 182, 156)
BENCH_DARK = (110, 152, 128)
RAIL_COL = (252, 244, 228)
GRASS = (156, 182, 96)
GRASS_DARK = (128, 156, 80)
HILL_FAR = (196, 186, 106)
HILL_NEAR = (164, 176, 92)
SOIL = (154, 104, 72)
STONE = (214, 204, 186)
LEAF = (98, 158, 84)
LEAF_DARK = (76, 132, 70)
PUMPKIN_SMALL = (240, 140, 44)
CAN = (88, 170, 176)
TREE_LEAVES = ((236, 128, 52), (246, 168, 64), (222, 100, 52))
TRUNK = (140, 94, 64)
MUM = ((246, 166, 52), (255, 206, 72), (232, 108, 64))

# ---------------------------------------------------------------- the light script (times in seconds)
T_SUNSET0, T_SUNSET1 = 6.0, 8.6        # golden -> sunset
T_EVE0, T_EVE1 = 8.6, 12.0             # sunset -> early evening
T_DEEP0, T_DEEP1 = 14.0, 96.0          # early evening deepens slowly so the glow will pop
DEEPEST = 0.92
T_SUN0, T_SUN1 = 6.0, 9.6              # the sun sinks behind the hill
T_STAR1, T_MOON = 11.0, 12.0
STARS = (  # (x, y, size, appear time): the first star, then a few more through the evening
    (1420, 655, 16, T_STAR1), (1680, 840, 12, 15.0), (1860, 620, 13, 22.0), (1340, 930, 10, 30.0),
    (1890, 1020, 10, 41.0), (1420, 1060, 9, 52.0), (1780, 735, 9, 63.0), (1620, 590, 11, 75.0),
    # above the roofs (seen by the vertical camera)
    (300, 90, 14, 15.0), (820, 60, 12, 26.0), (1150, 140, 15, 37.0), (560, 170, 10, 48.0), (1500, 260, 12, 20.0),
    (1750, 120, 14, 33.0), (90, 200, 11, 58.0),
)


def state_weights(t):
    """Weights of the three painted states at time t (they sum to 1)."""
    a = ease_in_out(seg(t, T_SUNSET0, T_SUNSET1))
    b = ease_in_out(seg(t, T_EVE0, T_EVE1))
    return {"golden": 1 - a, "sunset": a * (1 - b), "evening": a * b}


def deepen(t):
    """Extra dimming of the whole porch through the evening (1.0 -> DEEPEST)."""
    return 1.0 - (1.0 - DEEPEST) * ease_in_out(seg(t, T_DEEP0, T_DEEP1))


def sun_k(t):
    """Strength of direct sunlight (1 while the sun is up, 0 once it has gone behind the hill)."""
    return 1.0 - ease_in_out(seg(t, T_SUN0 + 0.4, 9.4))


def sun_pos(t):
    return SUN_X, SUN_Y0 + (SUN_Y1 - SUN_Y0) * ease_in_out(seg(t, T_SUN0, T_SUN1))


def hill_y(x):
    return HILL_Y - 18 * math.sin((x - 1286) / 170.0) - 10 * math.sin((x - 1286) / 61.0 + 1.0)


# ---------------------------------------------------------------- helpers
def _R():
    return hires.RES


def _at(x, y):
    return x * _R(), y * _R()


class _Painter:
    """Flat areas drawn with ImageDraw at 2x supersampling (then downsampled once)."""

    def __init__(self, w=WORLD_W, h=WORLD_H, fill=(0, 0, 0, 0)):
        self.k = 2 * _R()
        self.img = Image.new("RGBA", (int(w * self.k), int(h * self.k)), fill)
        self.d = ImageDraw.Draw(self.img)

    def rect(self, x0, y0, x1, y1, col):
        k = self.k
        self.d.rectangle([x0 * k, y0 * k, x1 * k, y1 * k], fill=col)

    def rrect(self, x0, y0, x1, y1, r, col):
        k = self.k
        self.d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], r * k, fill=col)

    def poly(self, pts, col):
        k = self.k
        self.d.polygon([(x * k, y * k) for x, y in pts], fill=col)

    def ellipse(self, cx, cy, rx, ry, col):
        k = self.k
        self.d.ellipse([(cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k], fill=col)

    def line(self, pts, w, col):
        k = self.k
        self.d.line([(x * k, y * k) for x, y in pts], fill=col, width=max(1, int(w * k)), joint="curve")

    def done(self, g=0.03):
        R = _R()
        out = self.img.resize((int(WORLD_W * R), int(WORLD_H * R)), Image.LANCZOS)
        return grain(out, g) if g else out


# ---------------------------------------------------------------- sky (per state)
SKY_STOPS = {
    "golden": ((0, (124, 170, 226)), (520, (176, 200, 230)), (860, (246, 214, 176)), (1080, (255, 214, 140)),
               (1260, (255, 196, 118))),
    "sunset": ((0, (92, 84, 164)), (520, (150, 108, 176)), (860, (232, 136, 160)), (1080, (252, 160, 128)),
               (1260, (255, 176, 108))),
    "evening": ((0, (46, 50, 112)), (520, (72, 70, 146)), (860, (104, 88, 164)), (1080, (150, 104, 168)),
                (1260, (178, 118, 164))),
}
CLOUD_COL = {"golden": (255, 240, 222), "sunset": (255, 196, 206), "evening": (150, 136, 190)}


def _gradient(stops, h):
    ys = np.arange(h, dtype=np.float32) / _R()
    out = np.zeros((h, 3), np.float32)
    sy = [s[0] for s in stops]
    for c in range(3):
        out[:, c] = np.interp(ys, sy, [s[1][c] for s in stops])
    return out


def _cloud(w, h, col):
    c = Cut(w + 20, h + 20)
    for i, (dx, dy, r) in enumerate(((0.28, 0.62, 0.30), (0.5, 0.42, 0.36), (0.72, 0.6, 0.28), (0.5, 0.68, 0.3))):
        c.ellipse(10 + w * dx, 10 + h * dy, w * r, h * r * 1.15 if i == 1 else h * r, col)
    return c.finish(pivot=(10 + w / 2, 10 + h / 2), border=4, shadow_alpha=0.10)


def sky_layer(state):
    R = _R()
    W, H = int(WORLD_W * R), int(WORLD_H * R)
    g = _gradient(SKY_STOPS[state], H)
    arr = np.broadcast_to(g[:, None, :], (H, W, 3)).copy()
    if state in ("golden", "sunset"):           # warm glow round the low sun
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) / R
        sy = 1110 if state == "golden" else 1230
        d2 = ((xx - SUN_X) / 520.0) ** 2 + ((yy - sy) / 300.0) ** 2
        glow = np.exp(-d2)[..., None]
        tint = np.array((255, 236, 170) if state == "golden" else (255, 190, 130), np.float32)
        arr = arr * (1 - 0.55 * glow) + tint * 0.55 * glow
    img = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")
    img = grain(img, 0.018)
    for x, y, w, h in ((1450, 790, 170, 66), (1700, 640, 210, 74), (420, 120, 220, 70), (1250, 60, 160, 56)):
        place(img, _cloud(w, h, CLOUD_COL[state]), _at(x, y))
    return img


# ---------------------------------------------------------------- the porch in daylight colours
def _door():
    x0, x1, top = DOOR
    w, h = x1 - x0, WALL_BASE - top
    c = Cut(w, h)
    c.rrect(0, 0, w, h, 10, TRIM)                                        # frame
    c.rrect(16, 16, w - 16, h + 6, 8, DOOR_COL)
    c.ellipse(w / 2, 108, 62, 62, TRIM, sil=False)                       # round window in the door
    c.ellipse(w / 2, 108, 50, 50, GLASS, sil=False)
    c.line([(w / 2 - 50, 108), (w / 2 + 50, 108)], 6, TRIM)
    c.line([(w / 2, 58), (w / 2, 158)], 6, TRIM)
    c.ellipse(w / 2 - 18, 88, 9, 18, mix(GLASS, (255, 255, 255), 0.45), sil=False, theta=30)
    for y0, y1 in ((200, 400), (430, h - 30)):
        c.rrect(36, y0, w / 2 - 10, y1, 8, DOOR_DARK, sil=False)
        c.rrect(w / 2 + 10, y0, w - 36, y1, 8, DOOR_DARK, sil=False)
    c.ellipse(w - 42, 380, 11, 11, BRASS, sil=False)                     # knob
    c.ellipse(w - 45, 376, 4, 4, (255, 236, 170), sil=False)
    return c.finish(pivot=(0, 0), border=5, shadow_alpha=0.22)


def _window():
    x0, x1, y0, y1 = WINDOW
    w, h = x1 - x0, y1 - y0
    c = Cut(w + 40, h + 60)
    ox = 20
    c.rrect(ox, 0, ox + w, h, 10, TRIM)
    for px0, py0 in ((16, 16), (w / 2 + 6, 16), (16, h / 2 + 6), (w / 2 + 6, h / 2 + 6)):
        c.rrect(ox + px0, py0, ox + px0 + w / 2 - 22, py0 + h / 2 - 22, 5, GLASS, sil=False)
    c.polygon([(ox + 16, 16), (ox + 46, 16), (ox + 30, h - 16), (ox + 16, h - 16)], CURTAIN, sil=False)
    c.polygon([(ox + w - 16, 16), (ox + w - 46, 16), (ox + w - 30, h - 16), (ox + w - 16, h - 16)], CURTAIN,
              sil=False)
    for px, py in ((ox + 60, 40), (ox + w / 2 + 40, h / 2 + 30)):
        c.line([(px, py + 40), (px + 30, py)], 7, mix(GLASS, (255, 255, 255), 0.4))
    c.rrect(0, h - 4, w + 40, h + 14, 5, TRIM)                            # sill
    c.rrect(10, h + 12, w + 30, h + 56, 8, (196, 120, 84))                # flower box
    for i in range(9):
        fx = 24 + i * (w + 4) / 8.5
        col = MUM[i % 3]
        c.ellipse(fx, h + 8 - (i % 2) * 6, 15, 13, LEAF_DARK if i % 4 == 3 else col)
    return c.finish(pivot=(ox, 0), border=5, shadow_alpha=0.22)


def _bench():
    x0, x1 = BENCH
    w = x1 - x0
    c = Cut(w, 240)
    seat = 120                                                           # local y of the seat top
    for lx in (14, w - 34):
        c.rrect(lx, seat, lx + 20, 230, 6, BENCH_DARK)
    c.rrect(10, 200, w - 10, 212, 4, BENCH_DARK)
    for i in range(3):
        c.rrect(8, 10 + i * 30, w - 8, 30 + i * 30, 6, BENCH_COL)         # backrest slats
    for lx in (16, w - 36):
        c.rrect(lx, 0, lx + 20, seat, 6, BENCH_DARK)
    c.rrect(0, seat - 6, w, seat + 18, 8, BENCH_COL)                      # seat
    c.rrect(0, seat + 12, w, seat + 20, 4, BENCH_DARK, sil=False)
    return c.finish(pivot=(0, seat), border=5, shadow_alpha=0.25)


def _fence():
    c = Cut(440, 160)
    for y in (52, 112):
        c.rrect(0, y, 440, y + 16, 5, TRIM)
    for i in range(12):
        x = 8 + i * 37
        c.polygon([(x, 150), (x, 22), (x + 13, 6), (x + 26, 22), (x + 26, 150)], TRIM)
    return c.finish(pivot=(0, 150), border=4, shadow_alpha=0.18)


def _tree():
    c = Cut(340, 520)
    c.polygon([(150, 520), (160, 250), (182, 250), (196, 520)], TRUNK)
    c.line([(170, 330), (120, 260)], 14, TRUNK)
    c.line([(176, 300), (232, 240)], 12, TRUNK)
    for i, (dx, dy, r) in enumerate(((170, 190, 118), (96, 210, 80), (250, 200, 84), (130, 120, 86), (220, 110, 90),
                                     (172, 80, 80), (90, 150, 60), (262, 150, 58))):
        c.ellipse(dx, dy, r, r * 0.92, TREE_LEAVES[i % 3])
    for dx, dy in ((120, 160), (210, 170), (160, 120), (240, 230), (100, 240)):
        c.ellipse(dx, dy, 20, 16, mix(TREE_LEAVES[1], (255, 255, 255), 0.25), sil=False)
    return c.finish(pivot=(173, 520), border=5, shadow_alpha=0.18)


def small_pumpkin(r, col=PUMPKIN_SMALL):
    c = Cut(2 * r + 20, 2 * r + 30)
    cx, cy = r + 10, r + 22
    dark = mix(col, (150, 70, 20), 0.35)
    for dx, w in ((-0.55, 0.5), (0.55, 0.5), (0, 0.62)):
        c.ellipse(cx + dx * r, cy, r * w + 2, r * 0.84 + 2, dark)
        c.ellipse(cx + dx * r, cy, r * w, r * 0.84, col)
    c.ellipse(cx - r * 0.2, cy - r * 0.35, r * 0.18, r * 0.3, mix(col, (255, 255, 255), 0.35), sil=False)
    c.line([(cx, cy - r * 0.8), (cx + 4, cy - r * 0.8 - 14)], 6, (110, 116, 60))
    return c.finish(pivot=(cx, cy + r * 0.84), border=4, shadow_alpha=0.22)


def _leaf(r, ang):
    c = Cut(2 * r + 12, 2 * r + 12)
    c.ellipse(r + 6, r + 6, r, r * 0.8, LEAF, theta=ang)
    c.line([(r + 6, r + 6), (r + 6 + r * 0.7 * math.cos(math.radians(ang)), r + 6 + r * 0.7 *
                             math.sin(math.radians(ang)))], 3, LEAF_DARK)
    return c.finish(pivot=(r + 6, r + 6), border=3, shadow_alpha=0.15)


def watering_can():
    c = Cut(170, 120)
    c.line([(104, 70), (150, 26)], 12, CAN, sil=True)                     # spout
    c.rrect(140, 14, 166, 32, 6, mix(CAN, (40, 40, 60), 0.25))            # rose
    c.arc(54, 40, 34, 30, 180, 360, 9, mix(CAN, (40, 40, 60), 0.2))      # handle
    c.rrect(14, 40, 104, 116, 14, CAN)
    c.rrect(14, 56, 104, 66, 3, mix(CAN, (255, 255, 255), 0.3), sil=False)
    return c.finish(pivot=(60, 116), border=4, shadow_alpha=0.22)


def _bush(w, h, cols):
    c = Cut(w + 20, h + 20)
    for i, (dx, dy, r) in enumerate(((0.25, 0.65, 0.3), (0.5, 0.45, 0.36), (0.75, 0.62, 0.3))):
        c.ellipse(10 + w * dx, 10 + h * dy, w * r, h * r * 1.2, cols[i % len(cols)])
    return c.finish(pivot=(10 + w / 2, 10 + h), border=4, shadow_alpha=0.2)


def _fallen_leaf(col, ang):
    c = Cut(40, 30)
    c.ellipse(20, 15, 15, 8, col, theta=ang)
    return c.finish(pivot=(20, 15), border=2, shadow_alpha=0.15)


def scene_albedo():
    """Everything except the sky and the front railing, in daylight colours (RGBA; the sky is transparent)."""
    p = _Painter()
    # garden ground and hills (right of the house; also under the porch, hidden by it)
    pts = [(x, hill_y(x) - 24) for x in range(1200, 1941, 20)]
    p.poly(pts + [(1940, WORLD_H), (1200, WORLD_H)], HILL_FAR)
    pts = [(x, hill_y(x)) for x in range(1200, 1941, 20)]
    p.poly(pts + [(1940, WORLD_H), (1200, WORLD_H)], HILL_NEAR)
    p.rect(1200, 1290, 1940, WORLD_H, GRASS)
    for i in range(14):                                                 # mown stripes
        y = 1300 + i * 46
        p.rect(1200, y, 1940, y + 14, GRASS_DARK)
    # lawn in front of the porch
    p.rect(-20, 1590, 1940, WORLD_H, GRASS)
    for i in range(8):
        y = 1660 + i * 34 + i * i * 3
        p.rect(-20, y, 1940, y + 10, GRASS_DARK)
    # garden bed (soil) bottom right
    p.ellipse(1720, 1625, 230, 70, SOIL)
    # path from the step towards the camera
    for i, (x, y, rx, ry) in enumerate(((960, 1660, 120, 26), (930, 1730, 132, 30), (980, 1810, 146, 34),
                                        (950, 1900, 160, 38))):
        p.ellipse(x, y + 4, rx + 6, ry + 6, mix(STONE, (120, 110, 100), 0.35))
        p.ellipse(x, y, rx, ry, STONE)
    # sky gap: main roof and upper storey
    p.rect(-20, 272, HOUSE_X1, 470, HOUSE)
    for y in range(300, 470, 28):                                        # clapboard siding upstairs only
        p.rect(-20, y, HOUSE_X1, y + 4, mix(HOUSE, (200, 170, 130), 0.35))
    p.rect(HOUSE_X1 - 26, 272, HOUSE_X1, 470, TRIM)
    for row, y in enumerate(range(190, 256, 22)):                        # main roof edge (shingles)
        for x in range(-40 + (row % 2) * 22, HOUSE_X1 + 30, 44):
            p.rrect(x, y, x + 42, y + 30, 10, ROOF if (x // 44 + row) % 3 else ROOF_DARK)
    p.rect(-20, 252, HOUSE_X1 + 20, 272, TRIM)
    # porch roof (scalloped shingles) and eave board
    for row, y in enumerate(range(466, 590, 24)):
        for x in range(-40 + (row % 2) * 22, 1560, 44):
            p.rrect(x, y, x + 42, y + 32, 12, ROOF if (x // 44 + row) % 3 else ROOF_DARK)
    p.rect(-20, 586, 1546, 618, TRIM)
    p.rect(-20, 612, 1546, 620, mix(TRIM, (180, 150, 120), 0.4))
    # lower house wall: plain paint (the projection lands here)
    p.rect(-20, WALL_TOP, HOUSE_X1, WALL_BASE, HOUSE)
    p.rect(-20, WALL_BASE - 22, HOUSE_X1, WALL_BASE, TRIM)              # skirting
    p.rect(1258, WALL_TOP, HOUSE_X1, WALL_BASE, TRIM)                   # corner trim
    # deck (boards run left-right; gaps widen towards the front)
    p.rect(-20, WALL_BASE, DECK_X1, DECK_FRONT, WOOD)
    ys, y, g = [], WALL_BASE + 12, 14.0
    while y < DECK_FRONT - 4:
        ys.append(y)
        y += g
        g *= 1.09
    for y in ys:
        p.rect(-20, y, DECK_X1, y + 3, WOOD_LINE)
    for i, y in enumerate(ys[:-1]):                                      # board ends
        for x in range(((i * 173) % 300) - 20, DECK_X1, 520):
            p.rect(x, y, x + 3, ys[i + 1], WOOD_LINE)
    p.rect(-20, DECK_FRONT, DECK_X1 + 4, 1592, WOOD_DARK)               # fascia
    p.rect(DECK_X1 - 4, WALL_BASE, DECK_X1 + 6, 1592, WOOD_DARK)        # deck side
    for x in range(40, DECK_X1, 160):                                    # lattice skirt under the fascia
        p.rect(x, 1592, x + 6, 1606, mix(WOOD_DARK, (60, 40, 30), 0.3))
    # the low step
    x0, x1, s0, s1 = STEP
    p.rect(x0, s0 - 2, x1, s0 + 12, WOOD)
    p.rect(x0, s0 + 12, x1, s1, WOOD_DARK)
    p.rect(x0, s0 + 10, x1, s0 + 14, WOOD_LINE)
    img = p.done(0.03)
    # cut-out props
    place(img, _fence(), _at(1512, 1432))
    place(img, _fence(), _at(1512 + 436, 1432))
    place(img, _tree(), _at(*TREE_AT))
    place(img, _door(), _at(DOOR[0], DOOR[2]))
    place(img, _window(), _at(WINDOW[0], WINDOW[2]))
    place(img, _bench(), _at(BENCH[0], BENCH_SEAT_Y))
    attic = Cut(130, 130)
    attic.ellipse(65, 65, 60, 60, TRIM)
    attic.ellipse(65, 65, 48, 48, GLASS, sil=False)
    attic.line([(17, 65), (113, 65)], 6, TRIM)
    attic.line([(65, 17), (65, 113)], 6, TRIM)
    place(img, attic.finish(pivot=(65, 65), border=5), _at(640, 372))
    # garden: pumpkin patch with vines and leaves, watering can, bushes, fallen leaves
    vine = Cut(420, 120)
    vine.line([(10, 70), (80, 50), (150, 80), (230, 54), (300, 84), (400, 60)], 5, LEAF_DARK)
    for cx, cy in ((80, 50), (230, 54), (330, 80)):
        vine.arc(cx, cy - 14, 12, 12, 200, 520, 3, LEAF_DARK)
    place(img, vine.finish(pivot=(0, 0), border=2, shadow_alpha=0.1), _at(1520, 1556))
    for x, y, r, a in ((1560, 1590, 26, -20), (1640, 1572, 30, 30), (1760, 1580, 28, -50), (1850, 1566, 26, 10),
                       (1700, 1640, 30, 70), (1900, 1630, 28, -30)):
        place(img, _leaf(r, a), _at(x, y))
    for x, y, r in ((1600, 1612, 30), (1810, 1612, 38), (1890, 1600, 24), (1720, 1594, 22)):
        place(img, small_pumpkin(r), _at(x, y))
    place(img, watering_can(), _at(1676, 1628))
    place(img, _bush(220, 90, (LEAF, LEAF_DARK)), _at(140, 1650))
    place(img, _bush(200, 80, (LEAF_DARK, LEAF)), _at(1330, 1650))
    for x, y, i, a in ((640, 1612, 0, 20), (700, 1640, 1, -30), (1240, 1620, 2, 50), (1290, 1600, 0, -10),
                       (420, 1630, 2, 35), (1980, 1680, 1, 0), (1100, 1680, 0, 70), (1590, 1680, 1, -40)):
        place(img, _fallen_leaf(TREE_LEAVES[i], a), _at(x, y))
    return img


def railing_albedo():
    """The right railing (three heart cut-outs) and the corner post: drawn in front of the characters."""
    x0, x1, top, base = RAIL
    w = POST[1] - x0 + 20
    h = base - EAVE_Y + 30
    c = Cut(w, h)
    oy = EAVE_Y - 10                                                    # local y = world y - oy
    c.rrect(POST[0] - x0, EAVE_Y + 10 - oy, POST[1] - x0, base + 4 - oy, 6, TRIM)       # corner post
    c.rrect(POST[0] - x0 - 6, base - 30 - oy, POST[1] - x0 + 6, base + 6 - oy, 6, TRIM)
    for px in (0, x1 - x0 - 24):                                        # newel posts
        c.rrect(px, top - 14 - oy, px + 24, base - oy, 6, RAIL_COL)
        c.ellipse(px + 12, top - 18 - oy, 15, 10, RAIL_COL)
    c.rrect(-6, top - oy, x1 - x0 + 6, top + 18 - oy, 6, RAIL_COL)      # top rail
    c.rrect(14, top + 14 - oy, x1 - x0 - 14, base - 12 - oy, 4, RAIL_COL)  # board panel
    c.rrect(-4, base - 16 - oy, x1 - x0 + 4, base - oy, 5, RAIL_COL)    # bottom rail
    for i in range(1, 4):                                               # board seams
        sx = 14 + i * (x1 - x0 - 28) / 4
        c.line([(sx, top + 20 - oy), (sx, top + 40 - oy)], 2, mix(RAIL_COL, (170, 150, 130), 0.5))
        c.line([(sx, base - 40 - oy), (sx, base - 16 - oy)], 2, mix(RAIL_COL, (170, 150, 130), 0.5))
    spr = c.finish(pivot=(0, 0), border=4, shadow_alpha=0.24)
    # cut the hearts out (real holes: whatever is behind shows through)
    k = _R()
    P = spr.pivot
    a = np.asarray(spr.img).copy()
    holes = Image.new("L", spr.img.size, 0)
    hd = ImageDraw.Draw(holes)
    for hx, hy in RAIL_HEARTS:
        pts = heart_pts(hx - x0, hy - oy, RAIL_HEART_W)
        hd.polygon([(P[0] + px * k, P[1] + py * k) for px, py in pts], fill=255)
    hm = np.asarray(holes.filter(ImageFilter.GaussianBlur(0.6 * k))).astype(np.float32) / 255
    rim = np.asarray(holes.filter(ImageFilter.MaxFilter(int(2 * round(2.2 * k)) + 1))
                     .filter(ImageFilter.GaussianBlur(0.8 * k))).astype(np.float32) / 255
    edge = np.clip(rim - hm, 0, 1)[..., None]                           # a slightly darker cut edge
    a[..., :3] = (a[..., :3] * (1 - 0.18 * edge)).astype(np.uint8)
    a[..., 3] = (a[..., 3] * (1 - hm)).astype(np.uint8)
    sh = np.asarray(spr.shadow).copy()
    sh[..., 3] = (sh[..., 3] * (1 - 0.7 * hm)).astype(np.uint8)
    spr.img = Image.fromarray(a, "RGBA")
    spr.shadow = Image.fromarray(sh, "RGBA")
    return spr, (x0, oy)


# ---------------------------------------------------------------- relighting the albedo into the three states
def _field(state, H, W, ppu=None):
    """Per-pixel light multiplier (H, W, 3) for a state over the world (ppu = pixels per design unit)."""
    ppu = _R() if ppu is None else ppu
    h, w = max(2, H // 8), max(2, W // 8)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    y = (yy + 0.5) * (H / h) / ppu
    x = (xx + 0.5) * (W / w) / ppu
    f = np.ones((h, w, 3), np.float32)
    roofs = (y < WALL_TOP) & (x < 1560)
    wall = (x < HOUSE_X1) & (y >= WALL_TOP) & (y < WALL_BASE)
    deck = (y >= WALL_BASE) & (y < 1600) & (x < DECK_X1 + 8)
    garden = ~(roofs | wall | deck)
    under = np.clip(1 - (y - WALL_TOP) / 260.0, 0, 1) * (y > WALL_TOP - 4) * (x < 1520)   # just under the eave
    if state == "golden":
        f[:] = np.array((1.03, 0.97, 0.86), np.float32)
        f *= (1 + 0.05 * (x / WORLD_W))[..., None]                       # the sun is on the right
        f *= (1 - 0.10 * under)[..., None]
        f[garden] *= np.array((1.04, 0.96, 0.82), np.float32)
    elif state == "sunset":
        f[:] = np.array((0.95, 0.80, 0.84), np.float32)
        f *= (1 - 0.14 * under)[..., None]
        f[garden] *= np.array((1.02, 0.88, 0.90), np.float32)
    else:   # early evening: cool shade, darkest under the roof, never black
        top = np.array((0.42, 0.40, 0.62), np.float32)
        low = np.array((0.60, 0.56, 0.80), np.float32)
        k = (np.clip((y - WALL_TOP) / (WALL_BASE - WALL_TOP), 0, 1) ** 0.8)[..., None]
        f[:] = top + (low - top) * k
        f[roofs] = np.array((0.50, 0.48, 0.70), np.float32)
        f[deck] = np.array((0.60, 0.55, 0.78), np.float32)
        f[garden] = np.array((0.52, 0.52, 0.76), np.float32)
        f[garden & (y >= 1592)] = np.array((0.54, 0.54, 0.76), np.float32)
    img = Image.fromarray((f * 100).clip(0, 255).astype(np.uint8), "RGB").filter(ImageFilter.GaussianBlur(2))
    return np.asarray(img.resize((W, H), Image.BILINEAR)).astype(np.float32) / 100


LIFT = {"golden": (0, 0, 0), "sunset": (4, 2, 6), "evening": (10, 9, 20)}


def relight(albedo, state):
    """Light a full-world RGBA albedo image with a state's light field (alpha kept)."""
    a = np.asarray(albedo).astype(np.float32)
    H, W = a.shape[:2]
    f = _field(state, H, W)
    a[..., :3] = a[..., :3] * f + np.array(LIFT[state], np.float32)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


# ---------------------------------------------------------------- sprites that move with time
def sun_sprite():
    R = _R()
    n = int(360 * R)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    c = n / 2
    d = np.hypot(xx - c, yy - c) / R
    glow = np.exp(-((d / 120.0) ** 2)) * 0.6
    img = np.zeros((n, n, 4), np.float32)
    img[..., 0], img[..., 1], img[..., 2] = 255, 214, 120
    img[..., 3] = glow * 255
    out = Image.fromarray(img.astype(np.uint8), "RGBA")
    disc = Cut(2 * SUN_R + 20, 2 * SUN_R + 20)
    disc.ellipse(SUN_R + 10, SUN_R + 10, SUN_R, SUN_R, (255, 190, 60))
    disc.ellipse(SUN_R + 10, SUN_R + 10, SUN_R * 0.72, SUN_R * 0.72, (255, 214, 96), sil=False)
    disc.ellipse(SUN_R + 10 - 16, SUN_R + 10 - 18, 15, 11, (255, 240, 180), sil=False)
    d_spr = disc.finish(pivot=(SUN_R + 10, SUN_R + 10), border=4, shadow_alpha=0.0)
    place(out, d_spr, (c, c), shadow=False)
    from paperlib import Sprite
    return Sprite(out, (c, c))


def star_sprite(size):
    c = Cut(2 * size + 16, 2 * size + 16)
    c.polygon(star_pts(size + 8, size + 8, size, size * 0.34, 4, -90), (255, 244, 186))
    return c.finish(pivot=(size + 8, size + 8), border=3, shadow_alpha=0.0)


def moon_sprite(r=34):
    c = Cut(2 * r + 20, 2 * r + 20)
    pts = []
    for i in range(41):                                                 # outer arc (left side)
        a = math.radians(90 + 180 * i / 40)
        pts.append((r + 10 + r * math.cos(a), r + 10 - r * math.sin(a)))
    for i in range(41):                                                 # inner arc back up
        a = math.radians(270 - 180 * i / 40)
        pts.append((r + 10 - 0.25 * r + 0.62 * r * math.cos(a), r + 10 - r * math.sin(a)))
    c.polygon(pts, (252, 244, 214))
    return c.finish(pivot=(r + 10, r + 10), border=3, shadow_alpha=0.0)


def marker_box(markers=0):
    """Small card box for the markers (on the bench); pivot at the base centre. Marker ends, never caps."""
    c = Cut(110, 110)
    for i in range(markers):
        col = ((40, 36, 48), (40, 36, 48), (220, 52, 62))[i % 3]
        x = 34 + i * 20
        c.rrect(x, 8, x + 14, 70, 6, col)
        c.rrect(x + 2, 12, x + 12, 20, 3, mix(col, (255, 255, 255), 0.35), sil=False)
    c.rrect(10, 46, 100, 104, 10, (244, 196, 78))
    c.rrect(10, 46, 100, 58, 5, (236, 164, 60), sil=False)
    c.polygon(star_pts(55, 80, 15, 6.5), (255, 248, 230), sil=False)
    return c.finish(pivot=(55, 104), border=4, shadow_alpha=0.22)


# ---------------------------------------------------------------- the world as seen by one camera
STATES = ("golden", "sunset", "evening")


class Porch:
    """The porch world cropped to one camera, ready to paint backgrounds by time."""

    def __init__(self, cam, states=STATES):
        self.cam = cam
        alb_full = scene_albedo()
        self.albedo = cam.crop_bg(alb_full)
        H, W = self.albedo.size[1], self.albedo.size[0]
        self.sky, self.scene = {}, {}
        for s in states:
            self.sky[s] = cam.crop_bg(sky_layer(s))
            lit = relight(alb_full, s)
            self.scene[s] = cam.crop_bg(lit)
        del alb_full
        rail, (rx0, ry0) = railing_albedo()
        self.rail_at = (rx0, ry0)
        self.rail_albedo = rail
        self.rail = {}
        for s in states:
            img = rail.img
            # light the railing with the field at its world position
            a = np.asarray(img).astype(np.float32)
            f = _rail_field(s, img.size, rail.pivot, (rx0, ry0))
            a[..., :3] = a[..., :3] * f + np.array(LIFT[s], np.float32)
            from paperlib import Sprite
            self.rail[s] = Sprite(Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA"), rail.pivot, rail.shadow)
        self.sun = sun_sprite()
        self.stars = [(x, y, star_sprite(sz), t0) for x, y, sz, t0 in STARS]
        self.moon = moon_sprite()
        self.size = self.albedo.size

    @staticmethod
    def _mix(layers, w):
        items = [(layers[s], w[s]) for s in STATES if w.get(s, 0) > 1e-4 and s in layers]
        if len(items) == 1:
            return items[0][0].copy()
        (a, wa), (b, wb) = items[0], items[1]
        return Image.blend(a, b, wb / (wa + wb))

    def sky_at(self, t):
        w = state_weights(t)
        sky = self._mix(self.sky, w)
        S = self.cam.S
        sk = sun_k(t)
        sx, sy = sun_pos(t)
        if sy < SUN_Y1 - 2:
            place(sky, self.sun, S((sx, sy)), alpha=0.6 + 0.4 * sk, shadow=False)
        night = w["evening"]
        for x, y, spr, t0 in self.stars:
            k = ease_in_out(seg(t, t0, t0 + 1.2)) * night
            if k > 0.01:
                tw = 1 + 0.12 * math.sin(2 * math.pi * (t * 0.7 + x * 0.013))
                place(sky, spr, S((x, y)), scale=k * tw, alpha=min(1.0, k * 1.2), shadow=False)
        k = ease_in_out(seg(t, T_MOON, T_MOON + 1.5)) * night
        if k > 0.01:
            place(sky, self.moon, S(MOON_AT), alpha=k, angle=-20, shadow=False)
        return sky

    def background(self, t):
        """Sky, sun, stars and moon, then the porch, crossfaded and dimmed by time (RGBA, camera pixels)."""
        f = self.sky_at(t)
        f.alpha_composite(self._mix(self.scene, state_weights(t)))
        k = deepen(t)
        if k < 0.999:
            a = f.getchannel("A")
            f = ImageEnhance.Brightness(f.convert("RGB")).enhance(k).convert("RGBA")
            f.putalpha(a)
        return f

    def front(self, f, t, grade=None):
        """The railing and the corner post, drawn after the characters."""
        spr = self._rail_sprite(t)
        place(f, spr, self.cam.S(self.rail_at))

    def _rail_sprite(self, t):
        w = state_weights(t)
        items = [(self.rail[s], w[s]) for s in STATES if w[s] > 1e-4]
        if len(items) == 1:
            spr = items[0][0]
        else:
            from paperlib import Sprite
            (a, wa), (b, wb) = items[0], items[1]
            spr = Sprite(Image.blend(a.img, b.img, wb / (wa + wb)), a.pivot, a.shadow)
        k = deepen(t)
        if k < 0.999:
            from paperlib import Sprite
            al = spr.img.getchannel("A")
            im = ImageEnhance.Brightness(spr.img.convert("RGB")).enhance(k).convert("RGBA")
            im.putalpha(al)
            spr = Sprite(im, spr.pivot, spr.shadow)
        return spr


def _rail_field(state, size, pivot, origin):
    """Light field values for the railing sprite (uses the world position of each sprite pixel)."""
    R = _R()
    W, H = size
    full = _field(state, WORLD_H // 2, WORLD_W // 2, 0.5)                  # coarse world field
    fy = full.shape[0] / (WORLD_H * R)
    ys = ((np.arange(H) - pivot[1]) / R + origin[1]) * R * fy
    xs = ((np.arange(W) - pivot[0]) / R + origin[0]) * R * fy
    yi = np.clip(ys.astype(int), 0, full.shape[0] - 1)
    xi = np.clip(xs.astype(int), 0, full.shape[1] - 1)
    return full[yi][:, xi]
