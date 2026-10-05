"""Street props for Episode 5 "Hold Paws to Cross?": sidewalk, road, zebra crossing,
pedestrian light (red standing / green walking figures), cute stopped cars, a ball,
wind-up legs, dust, the grown-up's long arm, choice-bubble icons, a heart iris and
a few new synthesized sound effects.

Everything is drawn as paper cut-outs with paperlib (no emoji, no fonts, no third-party art).

Scene coordinates match the screen at the default framing (camera centre 540, zoom 1).
The world canvas is wider than the screen (WORLD_W) so the camera can pan left and right
to the stopped cars while the friends look both ways: canvas_x = scene_x + X0.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import audio as A  # noqa: E402
import scene  # noqa: E402
from paperlib import (SS, Cut, Sprite, grain, heart_pts, mix, place,  # noqa: E402
                      star_pts)

W, H = scene.W, scene.H
X0 = 170                      # canvas x of scene x = 0
WORLD_W = W + 2 * X0          # scene x from -170 to 1250

# ---------------------------------------------------------------- layout (scene y)
HOUSE_BASE = 948              # houses stand on the back edge of the far sidewalk
FAR_WALK_TOP = 940
FAR_CURB = 1150               # top edge of the far curb (where Snip's toes stop)
ROAD_TOP = 1168               # under the far curb face
LANE_Y = 1303                 # lane divider
ROAD_BOT = 1438
NEAR_WALK = 1458              # near sidewalk starts after the near curb top
FAR_FEET = 1142               # friends waiting at the far curb
NEAR_FEET = 1480              # friends safe on the near sidewalk

# zebra crossing: (y, x_left, x_right) at the far and near edge
ZEB_FAR = (ROAD_TOP + 4, 215, 865)
ZEB_NEAR = (ROAD_BOT - 4, 188, 892)
STOP_LEFT = 168               # stop line for the lane that comes from the left (bottom lane)
STOP_RIGHT = 912              # stop line for the lane that comes from the right (top lane)

LIGHT_X = 86                  # pedestrian light pole
LIGHT_Y = 612                 # light box centre

# ---------------------------------------------------------------- colours
SKY_TOP = (140, 204, 244)
SKY_LOW = (204, 236, 250)
WALK = (226, 222, 214)
WALK_LINE = (204, 198, 190)
CURB = (244, 240, 232)
CURB_SHADE = (176, 170, 164)
ROAD = (108, 116, 136)
ROAD_DARK = (96, 104, 124)
ZEBRA = (250, 250, 246)
DASH = (246, 246, 240)
TACTILE = (250, 204, 86)
SLEEVE = scene.SLEEVE
SKIN = scene.SKIN
SNIP_FUR = (226, 214, 242)
SNIP_TEE = (80, 182, 235)
BOX = (56, 62, 80)
BOX_RIM = (86, 94, 116)
LAMP_OFF = (30, 33, 44)
RED_ON = (255, 76, 64)
RED_DIM = (96, 46, 50)
GREEN_ON = (64, 232, 120)
GREEN_DIM = (36, 84, 62)


def to_canvas(x, y):
    return x + X0, y


# ---------------------------------------------------------------- background
def _sky():
    k = 2
    w, h = WORLD_W, 1000
    a = np.zeros((h, w, 3), np.float32)
    t = np.linspace(0, 1, h)[:, None]
    for i in range(3):
        a[..., i] = SKY_TOP[i] + (SKY_LOW[i] - SKY_TOP[i]) * t
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
    return grain(img, 0.02), k


def _cloud(w=300, h=130, color=(255, 255, 255)):
    c = Cut(w, h)
    c.ellipse(w * 0.30, h * 0.62, w * 0.24, h * 0.30, color)
    c.ellipse(w * 0.52, h * 0.45, w * 0.24, h * 0.40, color)
    c.ellipse(w * 0.74, h * 0.62, w * 0.20, h * 0.28, color)
    c.rrect(w * 0.10, h * 0.55, w * 0.92, h * 0.90, h * 0.18, color)
    return c.finish(pivot=(w / 2, h / 2), border=5, shadow_alpha=0.12)


def _sun():
    c = Cut(240, 240)
    c.polygon(star_pts(120, 120, 112, 86, 14, -90), (255, 214, 92))
    c.ellipse(120, 120, 78, 78, (255, 196, 60), sil=False)
    c.ellipse(96, 98, 16, 12, (255, 228, 140), sil=False)
    return c.finish(pivot=(120, 120), border=6, shadow_alpha=0.15)


def _house(w, h, wall, roof, door, kind=0):
    """A simple paper house (no signs, no text). Pivot = bottom-left."""
    roof_h = 120 if kind != 2 else 54
    c = Cut(w + 40, h + roof_h + 20)
    ox, base = 20, h + roof_h + 10
    top = base - h
    c.rrect(ox, top, ox + w, base, 6, wall)
    if kind == 2:                       # flat roof with a trim and a little awning
        c.rrect(ox - 12, top - 34, ox + w + 12, top + 6, 8, roof)
        aw = top + h * 0.42
        for i in range(6):
            col = (255, 255, 255) if i % 2 else mix(roof, (255, 255, 255), 0.25)
            x0 = ox + 10 + i * (w - 20) / 6
            c.rrect(x0, aw, x0 + (w - 20) / 6, aw + 34, 4, col)
    else:
        c.polygon([(ox - 18, top + 4), (ox + w / 2, top - roof_h), (ox + w + 18, top + 4)], roof)
        if kind == 1:
            c.rrect(ox + w * 0.68, top - roof_h + 10, ox + w * 0.68 + 30, top - 30, 4, mix(roof, (0, 0, 0), 0.15))
    win = (236, 246, 252)
    frame = (255, 255, 255)
    cols = 2 if w < 260 else 3
    rows = 2
    ww, wh = 58, 64
    for r in range(rows):
        for ci in range(cols):
            cx = ox + w * (ci + 1) / (cols + 1)
            cy = top + 50 + r * 112 + wh / 2
            if kind == 2 and r == 1:
                continue
            c.rrect(cx - ww / 2 - 6, cy - wh / 2 - 6, cx + ww / 2 + 6, cy + wh / 2 + 6, 8, frame, sil=False)
            c.rrect(cx - ww / 2, cy - wh / 2, cx + ww / 2, cy + wh / 2, 6, win, sil=False)
            c.line([(cx, cy - wh / 2), (cx, cy + wh / 2)], 4, frame)
            c.line([(cx - ww / 2, cy), (cx + ww / 2, cy)], 4, frame)
    dw = 64
    dx = ox + (w * 0.5 if cols == 2 else w * 0.5)
    c.rrect(dx - dw / 2, base - 120, dx + dw / 2, base, 26, door, sil=False)
    c.ellipse(dx + 18, base - 60, 5, 5, (255, 226, 120), sil=False)
    return c.finish(pivot=(ox, base), border=5, shadow_alpha=0.22)


def _tree(h=330, leaf=(116, 190, 112)):
    c = Cut(260, h + 20)
    c.rrect(116, h * 0.55, 144, h + 10, 8, (176, 120, 80))
    dark = mix(leaf, (40, 90, 50), 0.35)
    for cx, cy, r, col in ((130, h * 0.32, 100, leaf), (78, h * 0.44, 66, dark), (184, h * 0.44, 66, dark),
                           (130, h * 0.22, 74, mix(leaf, (255, 255, 255), 0.12))):
        c.ellipse(cx, cy, r, r * 0.92, col)
    return c.finish(pivot=(130, h + 10), border=5, shadow_alpha=0.22)


def _hedge(w):
    c = Cut(w, 80)
    green = (122, 196, 118)
    for i, x in enumerate(range(0, w + 1, 46)):
        c.ellipse(x, 36 + 6 * math.sin(i * 1.7), 34, 30, green if i % 2 else (108, 182, 106))
    c.rrect(0, 36, w, 76, 8, (108, 182, 106))
    for i, x in enumerate(range(30, w, 120)):
        col = ((255, 170, 190), (255, 230, 120), (255, 255, 255))[i % 3]
        c.ellipse(x, 30 + 8 * math.sin(i), 8, 8, col, sil=False)
    return c.finish(pivot=(0, 76), border=4, shadow_alpha=0.2)


def _pole_static():
    """Pole + push-button box of the pedestrian light (the lit box is drawn per frame)."""
    h = FAR_CURB - 14 - (LIGHT_Y + 120)
    c = Cut(90, h + 20)
    c.rrect(33, 0, 57, h + 10, 10, (150, 158, 176))
    c.rrect(29, h - 2, 61, h + 14, 6, (126, 134, 152))
    c.rrect(26, 150, 64, 222, 10, (255, 206, 72))       # push-button box
    c.ellipse(45, 186, 11, 11, (240, 112, 96), sil=False)
    c.rrect(30, 22, 60, 30, 3, (126, 134, 152), sil=False)
    return c.finish(pivot=(45, h + 10), border=4, shadow_alpha=0.22)


def _ground_layer():
    """Sidewalks, curbs, road, zebra crossing and road markings, drawn flat at 2x and grained."""
    k = 2
    w, h = WORLD_W, H - FAR_WALK_TOP + 40
    y0 = FAR_WALK_TOP - 20
    img = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    S = lambda x, y: ((x + X0) * k, (y - y0) * k)  # noqa: E731

    def rect(x0, ya, x1, yb, col):
        d.rectangle([*S(x0, ya), *S(x1, yb)], fill=col)

    def poly(pts, col):
        d.polygon([S(x, y) for x, y in pts], fill=col)

    def line(pts, wd, col):
        d.line([S(x, y) for x, y in pts], fill=col, width=int(wd * k))

    # far sidewalk with slab joints converging gently towards the road vanishing point
    rect(-X0, y0, W + X0, FAR_CURB, WALK)
    for yy in (FAR_WALK_TOP + 62, FAR_WALK_TOP + 136):
        line([(-X0, yy), (W + X0, yy)], 3, WALK_LINE)
    for xx in range(-X0 - 60, W + X0 + 100, 150):
        line([(xx + 18, FAR_WALK_TOP), (xx, FAR_CURB)], 3, WALK_LINE)
    # far curb face
    rect(-X0, FAR_CURB, W + X0, ROAD_TOP, CURB)
    line([(-X0, FAR_CURB + 1), (W + X0, FAR_CURB + 1)], 3, (255, 255, 255))
    line([(-X0, ROAD_TOP - 1), (W + X0, ROAD_TOP - 1)], 3, CURB_SHADE)
    # road
    rect(-X0, ROAD_TOP, W + X0, ROAD_BOT, ROAD)
    rect(-X0, ROAD_TOP, W + X0, ROAD_TOP + 10, ROAD_DARK)
    # lane divider dashes (stop at the crossing)
    for xx in range(-X0 - 40, W + X0 + 60, 130):
        if ZEB_FAR[1] - 60 < xx + 70 and xx < ZEB_NEAR[2] + 50:
            continue
        d.rounded_rectangle([*S(xx, LANE_Y - 6), *S(xx + 70, LANE_Y + 6)], 6 * k, fill=DASH)
    # stop lines across each lane, set well back from the zebra
    rect(STOP_LEFT - 8, LANE_Y + 8, STOP_LEFT + 8, ROAD_BOT - 8, DASH)
    rect(STOP_RIGHT - 8, ROAD_TOP + 14, STOP_RIGHT + 8, LANE_Y - 8, DASH)
    # zebra stripes (bars parallel to the traffic, stacked across the road)
    (yf, lf, rf), (yn, ln, rn) = ZEB_FAR, ZEB_NEAR
    n = 7
    for i in range(n):
        u0 = (i + 0.18) / n
        u1 = (i + 0.78) / n
        ya, yb = yf + (yn - yf) * u0, yf + (yn - yf) * u1
        la, lb = lf + (ln - lf) * u0, lf + (ln - lf) * u1
        ra, rb = rf + (rn - rf) * u0, rf + (rn - rf) * u1
        poly([(la, ya), (ra, ya), (rb, yb), (lb, yb)], ZEBRA)
    # near curb top + shadow
    rect(-X0, ROAD_BOT, W + X0, NEAR_WALK, CURB)
    line([(-X0, ROAD_BOT + 1), (W + X0, ROAD_BOT + 1)], 3, (255, 255, 255))
    line([(-X0, NEAR_WALK), (W + X0, NEAR_WALK)], 4, CURB_SHADE)
    # near sidewalk slabs
    rect(-X0, NEAR_WALK + 2, W + X0, y0 + h, WALK)
    for yy in (NEAR_WALK + 96, NEAR_WALK + 250, NEAR_WALK + 440):
        line([(-X0, yy), (W + X0, yy)], 3, WALK_LINE)
    for xx in range(-X0 - 80, W + X0 + 120, 210):
        line([(xx, NEAR_WALK + 2), (xx - 30, y0 + h)], 3, WALK_LINE)
    # tactile paving at both ends of the crossing
    for (ya, yb, xl, xr) in ((FAR_CURB - 58, FAR_CURB - 8, ZEB_FAR[1] + 30, ZEB_FAR[2] - 30),
                             (NEAR_WALK + 8, NEAR_WALK + 70, ZEB_NEAR[1] + 20, ZEB_NEAR[2] - 20)):
        d.rounded_rectangle([*S(xl, ya), *S(xr, yb)], 6 * k, fill=TACTILE)
        rows = 3
        for r in range(rows):
            yy = ya + (yb - ya) * (r + 0.5) / rows
            for xx in np.arange(xl + 14, xr - 6, 24):
                rr = 3.2 + (yy - FAR_CURB) * 0.004
                d.ellipse([*S(xx - rr, yy - rr * 0.7), *S(xx + rr, yy + rr * 0.7)], fill=(236, 182, 64))
    img = img.resize((w, h), Image.LANCZOS)
    return grain(img, 0.03), y0


def _flowers(w):
    c = Cut(w, 120)
    for i, x in enumerate(range(20, w, 70)):
        hgt = 60 + 18 * math.sin(i * 2.3)
        c.line([(x, 118), (x + 4, 118 - hgt)], 6, (96, 170, 96))
        c.ellipse(x + 14, 118 - hgt * 0.5, 14, 7, (110, 186, 104), theta=-30)
        col = ((255, 150, 170), (255, 214, 80), (190, 160, 240), (255, 255, 255))[i % 4]
        for a in range(5):
            ang = a * 2 * math.pi / 5
            c.ellipse(x + 4 + 13 * math.cos(ang), 118 - hgt + 13 * math.sin(ang), 10, 10, col)
        c.ellipse(x + 4, 118 - hgt, 8, 8, (255, 196, 60), sil=False)
    return c.finish(pivot=(0, 118), border=4, shadow_alpha=0.2)


def background():
    """The whole street, on a canvas WORLD_W wide (scene x = canvas x - X0)."""
    sky, _ = _sky()
    bg = Image.new("RGBA", (WORLD_W, H), SKY_LOW + (255,))
    bg.paste(sky, (0, 0))
    P = lambda x, y: (x + X0, y)  # noqa: E731
    place(bg, _sun(), P(930, 150))
    for (x, y, s) in ((150, 150, 1.0), (640, 250, 0.8), (1110, 330, 0.7), (-60, 380, 0.75)):
        place(bg, _cloud().scaled(s), P(x, y))
    # houses and trees behind the far sidewalk (soft pastels so the friends pop)
    houses = [(-170, 300, 420, (255, 226, 214), (232, 128, 112), (150, 186, 236), 0),
              (175, 330, 330, (214, 236, 246), (110, 146, 206), (240, 150, 110), 2),
              (560, 280, 450, (255, 240, 200), (226, 150, 92), (120, 186, 140), 1),
              (890, 330, 380, (232, 222, 248), (150, 120, 196), (240, 120, 130), 0)]
    for x, w, h, wall, roof, door, kind in houses:
        place(bg, _house(w, h, wall, roof, door, kind), P(x, HOUSE_BASE))
    place(bg, _tree(360), P(500, HOUSE_BASE + 6))
    place(bg, _tree(300, (130, 200, 120)), P(1210, HOUSE_BASE + 6))
    place(bg, _tree(320, (124, 194, 116)), P(-120, HOUSE_BASE + 6))
    hedge = _hedge(WORLD_W + 40)
    place(bg, hedge, (-20, FAR_WALK_TOP + 12))
    ground, y0 = _ground_layer()
    bg.alpha_composite(ground, (0, y0))
    place(bg, _pole_static(), P(LIGHT_X, FAR_CURB - 14))
    place(bg, _flowers(WORLD_W), (0, H + 6))
    return bg.convert("RGBA")


# ---------------------------------------------------------------- pedestrian light
def draw_ped_stand(c, cx, cy, h, col, sil=False):
    """Standing figure: feet together, arms down (the 'wait' figure)."""
    s = h / 100
    c.ellipse(cx, cy - 38 * s, 11 * s, 11 * s, col, sil)
    c.rrect(cx - 13 * s, cy - 25 * s, cx + 13 * s, cy + 14 * s, 7 * s, col, sil)
    c.rrect(cx - 21 * s, cy - 23 * s, cx - 14 * s, cy + 10 * s, 4 * s, col, sil)
    c.rrect(cx + 14 * s, cy - 23 * s, cx + 21 * s, cy + 10 * s, 4 * s, col, sil)
    c.rrect(cx - 12 * s, cy + 10 * s, cx - 2 * s, cy + 48 * s, 5 * s, col, sil)
    c.rrect(cx + 2 * s, cy + 10 * s, cx + 12 * s, cy + 48 * s, 5 * s, col, sil)


def draw_ped_walk(c, cx, cy, h, col, phase=0, sil=False):
    """Walking figure mid-stride, leaning forward (the 'go' figure). phase 0/1 swaps the stride."""
    s = h / 100
    k = 1.0 if phase == 0 else 0.55
    c.ellipse(cx + 4 * s, cy - 38 * s, 11 * s, 11 * s, col, sil)
    c.polygon([(cx - 8 * s, cy - 25 * s), (cx + 12 * s, cy - 25 * s), (cx + 6 * s, cy + 12 * s),
               (cx - 12 * s, cy + 12 * s)], col, sil)
    c.line([(cx + 8 * s, cy - 20 * s), (cx + 8 * s + 14 * k * s, cy - 4 * s), (cx + 8 * s + 20 * k * s, cy + 6 * s)],
           7 * s, col, sil)
    c.line([(cx - 6 * s, cy - 20 * s), (cx - 6 * s - 14 * k * s, cy - 4 * s), (cx - 6 * s - 18 * k * s, cy + 8 * s)],
           7 * s, col, sil)
    c.line([(cx + 2 * s, cy + 8 * s), (cx + 2 * s + 18 * k * s, cy + 28 * s), (cx + 2 * s + 26 * k * s, cy + 48 * s)],
           9 * s, col, sil)
    c.line([(cx - 4 * s, cy + 8 * s), (cx - 4 * s - 12 * k * s, cy + 30 * s), (cx - 4 * s - 26 * k * s, cy + 46 * s)],
           9 * s, col, sil)


def ped_light(state, phase=0):
    """Signal box. state: 'red' (standing figure lit) or 'green' (walking figure lit)."""
    w, h = 150, 290
    c = Cut(w, h)
    c.rrect(0, 0, w, h, 26, BOX)
    c.rrect(6, 6, w - 6, h - 6, 22, BOX_RIM, sil=False)
    c.rrect(14, 14, w - 14, h - 14, 16, BOX, sil=False)
    for cy, on, lit_col, dim_col in ((82, state == "red", RED_ON, RED_DIM), (208, state == "green", GREEN_ON, GREEN_DIM)):
        c.chord(w / 2, cy - 6, 62, 62, 180, 360, BOX_RIM)            # visor
        c.ellipse(w / 2, cy, 54, 54, mix(LAMP_OFF, lit_col, 0.22) if on else LAMP_OFF, sil=False)
        col = lit_col if on else dim_col
        if cy < 150:
            draw_ped_stand(c, w / 2, cy + 2, 86, col)
        else:
            draw_ped_walk(c, w / 2 - 3, cy + 2, 86, col, phase)
        if on:
            c.ellipse(w / 2 - 26, cy - 30, 9, 6, mix(lit_col, (255, 255, 255), 0.6), sil=False)
    return c.finish(pivot=(w / 2, h / 2), border=6, shadow_alpha=0.3)


def lamp_glow(color, r=120):
    size = 2 * r + 40
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse([20, 20, size - 20, size - 20], fill=150)
    m = m.filter(ImageFilter.GaussianBlur(r * 0.35))
    img = Image.new("RGBA", (size, size), color + (255,))
    img.putalpha(m)
    return Sprite(img, (size / 2, size / 2))


# ---------------------------------------------------------------- cars
def car(body=(255, 186, 72), facing="right", w=290):
    """A cute rounded paper car seen from the side, with a grown-up driver. Pivot = ground under the front bumper."""
    h = 176
    c = Cut(w + 20, h + 10)
    ox = 10
    dark = mix(body, (0, 0, 0), 0.18)
    glass = (200, 232, 248)
    # cabin
    c.polygon([(ox + w * 0.20, 82), (ox + w * 0.32, 14), (ox + w * 0.70, 14), (ox + w * 0.84, 82)], body)
    c.rrect(ox + w * 0.30, 10, ox + w * 0.72, 40, 18, body)
    c.polygon([(ox + w * 0.27, 80), (ox + w * 0.36, 26), (ox + w * 0.50, 26), (ox + w * 0.50, 80)], glass, sil=False)
    c.polygon([(ox + w * 0.54, 80), (ox + w * 0.54, 26), (ox + w * 0.67, 26), (ox + w * 0.78, 80)], glass, sil=False)
    # driver: a grown-up head and shoulder in the front window
    c.ellipse(ox + w * 0.64, 50, 15, 16, SKIN, sil=False)
    c.rrect(ox + w * 0.57, 64, ox + w * 0.72, 82, 8, SLEEVE, sil=False)
    # body
    c.rrect(ox, 72, ox + w, 142, 34, body)
    c.rrect(ox + 4, 112, ox + w - 4, 126, 6, dark, sil=False)
    c.line([(ox + w * 0.52, 84), (ox + w * 0.52, 136)], 3, dark)
    c.rrect(ox + w * 0.60, 96, ox + w * 0.66, 102, 3, (255, 255, 255), sil=False)
    # lights and bumpers
    c.ellipse(ox + w - 14, 92, 13, 11, (255, 236, 140), sil=False)
    c.rrect(ox + 4, 84, ox + 18, 104, 5, (250, 110, 100), sil=False)
    c.rrect(ox + w - 22, 124, ox + w + 6, 140, 7, (210, 214, 224))
    c.rrect(ox - 6, 124, ox + 22, 140, 7, (210, 214, 224))
    # wheels
    for wx in (ox + w * 0.22, ox + w * 0.78):
        c.ellipse(wx, 142, 30, 30, (58, 60, 72))
        c.ellipse(wx, 142, 13, 13, (214, 218, 228), sil=False)
    spr = c.finish(pivot=(ox + w + 6, 172), border=5, shadow_alpha=0.28)
    if facing == "left":
        img = spr.img.transpose(Image.FLIP_LEFT_RIGHT)
        sh = spr.shadow.transpose(Image.FLIP_LEFT_RIGHT)
        spr = Sprite(img, (img.width - spr.pivot[0], spr.pivot[1]), sh)
    return spr


# ---------------------------------------------------------------- small props
def ball(r=58):
    c = Cut(2 * r + 20, 2 * r + 20)
    cx = cy = r + 10
    c.ellipse(cx, cy, r, r, (84, 168, 238))
    c.chord(cx, cy, r, r, 200, 340, (255, 212, 66), sil=False)
    c.chord(cx, cy, r, r, 20, 160, (250, 112, 118), sil=False)
    c.polygon(star_pts(cx, cy, r * 0.5, r * 0.22), (255, 255, 255), sil=False)
    c.ellipse(cx - r * 0.45, cy - r * 0.45, r * 0.16, r * 0.11, (255, 255, 255), sil=False, theta=-35)
    return c.finish(pivot=(cx, cy), border=5)


def dust_puff(col=(236, 228, 214)):
    c = Cut(170, 120)
    for cx, cy, r in ((50, 74, 38), (88, 52, 46), (126, 76, 36), (86, 86, 34)):
        c.ellipse(cx, cy, r, r * 0.9, col)
    c.ellipse(70, 50, 12, 8, (255, 255, 255), sil=False)
    return c.finish(pivot=(85, 70), border=4, shadow_alpha=0.12)


def whirl_frames(n=6, fur=SNIP_FUR):
    """Cartoon wind-up legs: a blur-wheel of paws spinning under Snip."""
    frames = []
    line_col = mix(fur, (120, 100, 160), 0.45)
    for i in range(n):
        c = Cut(250, 120)
        c.ellipse(125, 60, 112, 46, mix(fur, (255, 255, 255), 0.35))
        ph = 2 * math.pi * i / n
        for k in range(4):
            a = ph + k * math.pi / 2
            x, y = 125 + 78 * math.cos(a), 60 + 26 * math.sin(a)
            c.ellipse(x, y, 34, 17, fur, sil=False)
        for k, rr in enumerate((96, 70)):
            a0 = math.degrees(ph) + k * 90
            c.arc(125, 60, rr, rr * 0.4, a0, a0 + 120, 4, line_col)
        frames.append(c.finish(pivot=(125, 72), border=4, shadow_alpha=0.18))
    return frames


def speed_lines(color=(255, 255, 255)):
    c = Cut(260, 200)
    for i, (y, l) in enumerate(((30, 200), (80, 250), (130, 210), (176, 150))):
        c.line([(250 - l, y), (250, y)], 10 - i, color, sil=True)
    return c.finish(pivot=(250, 100), border=3, shadow_alpha=0.12)


def skid_mark(length):
    c = Cut(int(length) + 30, 40)
    for y in (12, 28):
        c.line([(10, y), (length + 10, y)], 9, (150, 140, 132), sil=True)
    return c.finish(pivot=(length + 10, 20), border=0, shadow_alpha=0.0)


def glint(col=(255, 255, 255)):
    c = Cut(80, 80)
    c.polygon(star_pts(40, 40, 36, 8, 4, -90), col)
    return c.finish(pivot=(40, 40), border=3, shadow_alpha=0.12)


def long_hand(extra=1500, mirror=False):
    """scene.grown_up_hand() with its sleeve continued upward by `extra` px, so the grown-up's arm
    always reaches past the top of the frame. Pivot stays at the fingertips."""
    spr = scene.grown_up_hand()
    img, sh = spr.img, spr.shadow
    cut = 70                                  # row inside the sleeve where we splice
    strip_h = 160
    strip = img.crop((0, cut, img.width, cut + strip_h))
    sh_strip = sh.crop((0, cut, sh.width, cut + strip_h))
    new_h = img.height - cut + extra
    out = Image.new("RGBA", (img.width, new_h), (0, 0, 0, 0))
    out_sh = Image.new("RGBA", (img.width, new_h), (0, 0, 0, 0))
    y = extra
    while y > 0:
        y -= strip_h
        out.paste(strip, (0, y))
        out_sh.paste(sh_strip, (0, y))
    out.paste(img.crop((0, cut, img.width, img.height)), (0, extra))
    out_sh.paste(sh.crop((0, cut, sh.width, sh.height)), (0, extra))
    pivot = (spr.pivot[0], spr.pivot[1] - cut + extra)
    if mirror:
        out, out_sh = out.transpose(Image.FLIP_LEFT_RIGHT), out_sh.transpose(Image.FLIP_LEFT_RIGHT)
        pivot = (out.width - pivot[0], pivot[1])
    return Sprite(out, pivot, out_sh)


# ---------------------------------------------------------------- choice icons
def draw_run_icon(c, cx, cy, size):
    """Snip dashing onto the road: a little bunny running with speed lines over an asphalt strip."""
    s = size / 140
    X = lambda v: cx + v * s  # noqa: E731
    Y = lambda v: cy + v * s  # noqa: E731
    c.rrect(X(-66), Y(30), X(66), Y(62), 10 * s, ROAD, sil=False)
    for xx in (-46, -10, 26):
        c.rrect(X(xx), Y(43), X(xx + 22), Y(49), 3 * s, DASH, sil=False)
    for yy, l in ((-34, 34), (-14, 42), (6, 30)):
        c.line([(X(-64), Y(yy)), (X(-64 + l), Y(yy))], 5 * s, (160, 170, 190))
    c.line([(X(2), Y(10)), (X(-14), Y(30)), (X(-30), Y(28))], 11 * s, SNIP_FUR)
    c.line([(X(10), Y(10)), (X(28), Y(22)), (X(36), Y(38))], 11 * s, SNIP_FUR)
    c.ellipse(X(6), Y(-6), 22 * s, 24 * s, SNIP_TEE, sil=False)
    c.line([(X(-6), Y(-14)), (X(-26), Y(-2))], 9 * s, SNIP_FUR)
    c.line([(X(18), Y(-14)), (X(36), Y(-26))], 9 * s, SNIP_FUR)
    c.ellipse(X(14), Y(-44), 13 * s, 30 * s, SNIP_FUR, sil=False, theta=-28)
    c.ellipse(X(32), Y(-42), 12 * s, 28 * s, SNIP_FUR, sil=False, theta=-8)
    c.ellipse(X(22), Y(-30), 25 * s, 22 * s, SNIP_FUR, sil=False)
    c.ellipse(X(31), Y(-33), 4 * s, 5 * s, (38, 32, 44), sil=False)
    c.ellipse(X(33), Y(-22), 6 * s, 6 * s, (120, 40, 60), sil=False)


def draw_hold_icon(c, cx, cy, size):
    """A grown-up's hand (blue sleeve) holding a small lilac paw."""
    s = size / 140
    X = lambda v: cx + v * s  # noqa: E731
    Y = lambda v: cy + v * s  # noqa: E731
    c.rrect(X(-8), Y(8), X(22), Y(76), 15 * s, SNIP_FUR, sil=False)          # Snip's arm, from below
    c.rrect(X(-14), Y(50), X(28), Y(80), 10 * s, SNIP_TEE, sil=False)
    c.rrect(X(-28), Y(-80), X(28), Y(-22), 12 * s, SLEEVE, sil=False)         # grown-up sleeve, from above
    c.rrect(X(-32), Y(-30), X(32), Y(-14), 6 * s, (244, 244, 248), sil=False)
    c.rrect(X(-26), Y(-18), X(26), Y(20), 18 * s, SKIN, sil=False)
    for fx in (-16, -5, 6, 17):
        c.rrect(X(fx - 6), Y(4), X(fx + 6), Y(30), 6 * s, SKIN, sil=False)
    c.ellipse(X(-28), Y(2), 9 * s, 16 * s, SKIN, sil=False, theta=-25)
    for fx in (-10, 1, 12):
        c.line([(X(fx), Y(10)), (X(fx), Y(26))], 2 * s, (182, 126, 92))
    for hx in (-30, 34):
        c.polygon([(X(hx) + dx, Y(-52) + dy) for dx, dy in
                   [(math.cos(a) * 8 * s * (1 if i % 2 == 0 else 0.4), math.sin(a) * 8 * s * (1 if i % 2 == 0 else 0.4))
                    for i, a in enumerate([j * math.pi / 4 for j in range(8)])]], (255, 214, 64), sil=False)


def choice_bubble(kind, ring):
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    if kind == "run":
        draw_run_icon(c, 125, 128, 150)
    else:
        draw_hold_icon(c, 125, 128, 150)
    return c.finish(pivot=(125, 125), border=7)


# ---------------------------------------------------------------- heart iris (screen space)
class HeartIris:
    def __init__(self, color=(250, 150, 172)):
        k = 4
        sheet = Image.new("RGBA", (W // k, H // k), color + (255,))
        d = ImageDraw.Draw(sheet)
        for row in range(0, H // k + 20, 26):
            for col in range(0, W // k + 20, 26):
                x = col + (13 if (row // 26) % 2 else 0)
                d.ellipse([x - 4, row - 4, x + 4, row + 4], fill=mix(color, (255, 255, 255), 0.25))
        self.sheet = grain(sheet.resize((W, H), Image.BICUBIC), 0.03)
        self.edge = Image.new("RGBA", (W, H), (255, 253, 246, 255))
        self.shadow = Image.new("RGBA", (W, H), (55, 38, 30, 255))

    def apply(self, frame, center, size):
        """Cover the frame with a paper sheet that has a heart-shaped hole of width ~size."""
        if size > 4200:
            return frame
        q = 4
        cx, cy = center

        def mask(sz, scale=1):
            m = Image.new("L", (W // scale, H // scale), 255)
            if sz > 2:
                pts = heart_pts(cx / scale, cy / scale + sz * 0.06 / scale, sz / scale, 120)
                ImageDraw.Draw(m).polygon(pts, fill=0)
            return m
        small = mask(size + 20, q).filter(ImageFilter.GaussianBlur(3))
        sh = Image.new("L", (W // q, H // q), 0)
        sh.paste(small, (2, 3))
        sh = sh.resize((W, H), Image.BILINEAR).point(lambda v: int(v * 0.32))
        out = frame.copy()
        shadow = self.shadow.copy()
        shadow.putalpha(sh)
        out.alpha_composite(shadow)
        edge = self.edge.copy()
        edge.putalpha(mask(size))
        out.alpha_composite(edge)
        sheet = self.sheet.copy()
        sheet.putalpha(mask(size + 22))
        out.alpha_composite(sheet)
        return out


# ---------------------------------------------------------------- sounds (original, synthesized)
SR = A.SR
_rng = np.random.default_rng(55)


def _t(d):
    return np.arange(int(d * SR)) / SR


def windup(dur=0.9, vel=1.0, f0=70, f1=300):
    """Brrrrr! Paws spinning faster and faster (rising buzzy motor)."""
    t = _t(dur)
    f = f0 + (f1 - f0) * (t / dur) ** 1.4
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sign(np.sin(ph)) * 0.35 + np.sin(2 * ph) * 0.4
    trem = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * np.cumsum(14 + 30 * t / dur) / SR))
    n = _rng.normal(0, 1, len(t))
    n = np.convolve(n, np.ones(6) / 6, mode="same")
    env = np.minimum(1, t / 0.06) * np.minimum(1, (dur - t) / 0.04)
    return vel * 0.42 * env * trem * (tone + 0.25 * n)


def squeak(vel=1.0, dur=0.42):
    """Sneaker-squeak skid: a bright rubbery glide with fast vibrato."""
    t = _t(dur)
    f = 1500 + 520 * np.sin(np.pi * t / dur) - 260 * t / dur + 60 * np.sin(2 * np.pi * 38 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    env = np.minimum(1, t / 0.02) * (1 - t / dur) ** 0.6
    return vel * 0.5 * env * y


def slide_whistle(f0, f1, dur=0.5, vel=1.0, wobble=0.0, wob_rate=5.0):
    t = _t(dur)
    f = f0 * (f1 / f0) ** (t / dur)
    f = f * (1 + wobble * np.sin(2 * np.pi * wob_rate * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    breath = np.convolve(_rng.normal(0, 1, len(t)), np.ones(8) / 8, mode="same")
    env = np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.06)
    return vel * 0.45 * env * (np.sin(ph) + 0.08 * breath)


def putt(dur=1.0, vel=1.0):
    """A gentle little car engine rolling in and slowing to a stop (soft putt-putt, no horn)."""
    t = _t(dur)
    rate = 11 - 7 * (t / dur) ** 0.7
    ph = np.cumsum(rate) / SR
    pulses = (np.sin(2 * np.pi * ph) > 0.55).astype(float)
    pulses = np.convolve(pulses, np.ones(220) / 220, mode="same")
    body = np.sin(2 * np.pi * 62 * t) + 0.5 * np.sin(2 * np.pi * 124 * t)
    n = np.convolve(_rng.normal(0, 1, len(t)), np.ones(30) / 30, mode="same")
    env = np.minimum(1, t / 0.25) * np.clip((dur - t) / 0.35, 0, 1)
    return vel * 0.9 * env * pulses * (body + 0.6 * n)


def chirp(vel=1.0, base=3600, n=3):
    out = np.zeros(int(0.5 * SR))
    for i in range(n):
        d = 0.06
        t = _t(d)
        f = base * (1.25 - 0.35 * t / d) * (1 + 0.04 * i)
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
        s = int(i * 0.09 * SR)
        out[s:s + len(y)] += y
    return vel * 0.22 * out


def tick(vel=1.0, f=1750):
    t = _t(0.03)
    return vel * 0.5 * np.exp(-t * 160) * np.sin(2 * np.pi * f * t)


def phew(vel=1.0):
    t = _t(0.6)
    f = 900 * (0.55 ** (t / 0.6))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    n = _rng.normal(0, 1, len(t))
    n = np.convolve(n, np.ones(12) / 12, mode="same") - np.convolve(n, np.ones(80) / 80, mode="same")
    env = np.minimum(1, t / 0.05) * np.exp(-t * 4)
    return vel * 0.5 * env * (0.6 * tone + 1.4 * n)
