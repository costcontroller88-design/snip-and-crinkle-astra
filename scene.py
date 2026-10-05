"""Shared scenery and props for Snip & Crinkle episodes."""
import math

from PIL import Image, ImageDraw

from paperlib import SS, Cut, grain, heart_pts, place

W, H = 1080, 1920
TABLE_Y = 1440

WALL = (186, 226, 208)
WALL_DOT = (204, 236, 221)
WOOD_TOP = (246, 196, 140)
WOOD_FRONT = (228, 152, 94)
WOOD_LINE = (208, 132, 80)
FLAG_COLORS = [(244, 112, 104), (255, 206, 72), (84, 182, 222), (196, 160, 236)]


def _wall():
    k = 2
    img = Image.new("RGBA", (W * k, H * k), WALL + (255,))
    d = ImageDraw.Draw(img)
    for row in range(20):
        for col in range(11):
            x = (col * 120 + (60 if row % 2 else 0)) * k
            y = (row * 104 + 40) * k
            r = 13 * k
            d.ellipse([x - r, y - r, x + r, y + r], fill=WALL_DOT)
    return grain(img.resize((W, H), Image.LANCZOS), 0.035)


def _window():
    c = Cut(380, 420)
    c.rrect(0, 0, 380, 420, 20, (252, 249, 240))
    sky = (156, 212, 246)
    for x0, y0 in ((20, 20), (200, 20), (20, 220), (200, 220)):
        c.rrect(x0, y0, x0 + 160, y0 + 180, 10, sky, sil=False)
    c.ellipse(292, 96, 42, 42, (255, 210, 70), sil=False)
    for cx, cy, r in ((70, 120, 26), (100, 108, 32), (132, 122, 24)):
        c.ellipse(cx, cy, r, r * 0.85, (255, 255, 255), sil=False)
    c.ellipse(260, 330, 60, 40, (255, 255, 255), sil=False)
    c.ellipse(300, 318, 40, 34, (255, 255, 255), sil=False)
    return c.finish(pivot=(0, 0), border=6)


def _garland():
    c = Cut(1080, 230)
    pts = [(x, 40 + 70 * math.sin(math.pi * x / 1080)) for x in range(0, 1081, 20)]
    c.line(pts, 5, (150, 110, 90))
    for i, x in enumerate(range(60, 1080, 120)):
        y = 40 + 70 * math.sin(math.pi * x / 1080)
        c.polygon([(x - 46, y), (x + 46, y), (x, y + 104)], FLAG_COLORS[i % 4])
    return c.finish(pivot=(0, 0), border=5)


def _shelf_plant():
    c = Cut(320, 330)
    for i, (dx, ang) in enumerate(((-40, -28), (0, 0), (40, 26), (-20, -10), (22, 12))):
        c.ellipse(160 + dx * 1.2, 120 + abs(dx) * 0.6, 26, 84, (96, 176, 110) if i % 2 else (78, 156, 96),
                  theta=ang)
    c.polygon([(110, 190), (210, 190), (196, 290), (124, 290)], (224, 118, 82))
    c.rrect(100, 180, 220, 210, 8, (236, 136, 96))
    c.rrect(0, 288, 320, 322, 8, (214, 160, 108))
    return c.finish(pivot=(0, 0), border=5)


def _table():
    c = Cut(1120, 520)
    c.rrect(0, 0, 1120, 80, 14, WOOD_TOP)
    c.rrect(0, 60, 1120, 520, 0, WOOD_FRONT)
    c.rrect(0, 56, 1120, 76, 0, (236, 172, 112), sil=False)
    for y in (140, 230, 330, 420):
        pts = [(x, y + 10 * math.sin(x / 90 + y)) for x in range(0, 1121, 20)]
        c.line(pts, 4, WOOD_LINE)
    return c.finish(pivot=(0, 0), border=5)


def background():
    bg = _wall()
    place(bg, _garland(), (0, 80))
    place(bg, _window(), (80, 300))
    place(bg, _shelf_plant(), (700, 560))
    place(bg, _table(), (-20, TABLE_Y - 40))
    return bg


def cup():
    c = Cut(240, 200)
    red = (236, 86, 86)
    c.ellipse(186, 110, 44, 52, red)
    c.d.ellipse(c._s([164, 80, 208, 140]), fill=(0, 0, 0, 0))
    c.m.ellipse(c._s([164, 80, 208, 140]), fill=0)
    c.rrect(20, 30, 180, 196, 28, red)
    c.ellipse(100, 34, 80, 14, (204, 62, 68))
    c.ellipse(100, 35, 68, 9, (124, 72, 52), sil=False)
    c.polygon(heart_pts(100, 118, 54), (255, 240, 236), sil=False)
    return c.finish(pivot=(100, 196))


def steam_frames(n=16):
    frames = []
    for i in range(n):
        ph = 2 * math.pi * i / n
        c = Cut(70, 190)
        pts = [(35 + 16 * math.sin(2 * math.pi * y / 80 + ph) * (0.4 + 0.6 * (170 - y) / 170), y)
               for y in range(170, 14, -6)]
        c.line(pts, 15, (238, 244, 252), sil=True)
        frames.append(c.finish(pivot=(35, 176), border=4, shadow_alpha=0.18))
    return frames


def _sign_card(c):
    c.rrect(206, 210, 234, 560, 10, (214, 170, 112))
    c.rrect(0, 0, 440, 250, 34, (255, 248, 228))


def sign_no_touch(paper=False):
    c = Cut(440, 570)
    _sign_card(c)
    if paper:
        import icons
        icons.draw_fire(c, 115, 125, 160)
        icons.draw_hand(c, 318, 128, 132)
        icons.draw_no(c, 318, 125, 176)
        return c.finish(pivot=(220, 552))
    c.emoji("🔥", 115, 125, 150, sil=False)
    c.emoji("✋", 318, 125, 136, sil=False)
    c.arc(318, 125, 86, 86, 0, 360, 15, (226, 48, 48))
    c.line([(258, 65), (378, 185)], 15, (226, 48, 48))
    return c.finish(pivot=(220, 552))


def sign_ok():
    c = Cut(440, 570)
    _sign_card(c)
    c.emoji("☕", 125, 125, 140, sil=False)
    c.emoji("✅", 320, 125, 140, sil=False)
    return c.finish(pivot=(220, 552))


def icon(ch, px=110):
    c = Cut(px + 20, px + 20)
    c.emoji(ch, (px + 20) / 2, (px + 20) / 2, px)
    return c.finish(pivot=((px + 20) / 2, (px + 20) / 2), border=6)


def heart(color=(240, 72, 98), size=96):
    c = Cut(size + 20, size + 20)
    c.polygon(heart_pts((size + 20) / 2, (size + 20) / 2 + 4, size), color)
    c.ellipse((size + 20) / 2 - size * 0.22, (size + 20) / 2 - size * 0.12, size * 0.1, size * 0.07,
              (255, 220, 228), sil=False)
    return c.finish(pivot=((size + 20) / 2, (size + 20) / 2), border=5)


def puff():
    c = Cut(150, 110)
    for i, y in enumerate((25, 55, 85)):
        pts = [(140 - x, y + 7 * math.sin(x / 14 + i)) for x in range(0, 121 - i * 20, 6)]
        c.line(pts, 9, (226, 240, 255), sil=True)
    return c.finish(pivot=(140, 55), border=4, shadow_alpha=0.15)


def banner(text, left_emoji, right_emoji):
    c = Cut(800, 200)
    c.rrect(40, 30, 760, 175, 48, (255, 214, 70))
    c.text(text, 400, 104, 84, (214, 66, 56), sil=False)
    c.emoji(left_emoji, 52, 100, 110)
    c.emoji(right_emoji, 748, 100, 110)
    return c.finish(pivot=(400, 100), border=7)


# ---------------------------------------------------------------- v2 props
from paperlib import polyline_length, polyline_point, smooth_curve, star_pts  # noqa: E402

SKIN = (206, 150, 112)
SLEEVE = (96, 128, 186)


def _clock():
    c = Cut(200, 200)
    c.ellipse(100, 100, 92, 92, (255, 214, 92))
    c.ellipse(100, 100, 74, 74, (255, 252, 242), sil=False)
    for i in range(12):
        a = math.radians(i * 30)
        c.ellipse(100 + 60 * math.sin(a), 100 - 60 * math.cos(a), 5, 5, (200, 150, 90), sil=False)
    c.line([(100, 100), (100, 56)], 8, (70, 60, 70))
    c.line([(100, 100), (132, 112)], 8, (70, 60, 70))
    c.ellipse(100, 100, 9, 9, (240, 112, 104), sil=False)
    return c.finish(pivot=(100, 100), border=6)


def background_v2():
    """Kitchen, decluttered: garland, small window, a clock (it's a waiting story)."""
    bg = _wall()
    place(bg, _garland(), (0, 80))
    win = _window().scaled(0.8)
    place(bg, win, (70, 300))
    place(bg, _clock(), (880, 470))
    place(bg, _table(), (-20, TABLE_Y - 40))
    return bg


def grown_up_hand():
    """A grown-up's arm reaching down from above; pivot = fingertips (where it grips a cup rim)."""
    c = Cut(230, 620)
    c.rrect(45, 0, 185, 470, 26, SLEEVE)
    c.rrect(36, 430, 194, 482, 16, (244, 244, 248))
    c.rrect(52, 466, 178, 560, 44, SKIN)
    for x in (70, 98, 126, 154):
        c.rrect(x - 14, 520, x + 14, 600, 14, SKIN)
    for x in (84, 112, 140):
        c.line([(x, 540), (x, 590)], 3, (182, 126, 92))
    c.polygon([(p[0], p[1]) for p in
               [(40 + 18 * math.cos(a) - 0, 520 + 46 * math.sin(a)) for a in
                [i * math.pi / 18 for i in range(36)]]], SKIN)
    return c.finish(pivot=(115, 588))


def hourglass_frames(levels=24):
    frames = []
    wood, glass, sand = (196, 136, 84), (226, 240, 250), (240, 196, 104)
    for i in range(levels + 1):
        lv = i / levels  # share of sand still in the top bulb
        c = Cut(160, 230)
        c.rrect(0, 0, 160, 26, 10, wood)
        c.rrect(0, 204, 160, 230, 10, wood)
        c.rrect(8, 20, 22, 210, 6, wood)
        c.rrect(138, 20, 152, 210, 6, wood)
        c.polygon([(30, 28), (130, 28), (84, 113), (76, 113)], glass)
        c.polygon([(76, 117), (84, 117), (130, 202), (30, 202)], glass)
        ht = 82 * math.sqrt(lv)
        if ht > 1:
            w = 98 * ht / 85
            c.polygon([(80 - w / 2, 113 - ht), (80 + w / 2, 113 - ht), (80, 113)], sand, sil=False)
        hb = 64 * (1 - lv) ** 0.6
        if hb > 1:
            c.polygon([(34, 202), (126, 202), (80 + 14, 202 - hb), (80 - 14, 202 - hb)], sand, sil=False)
        if 0.01 < lv < 0.99:
            c.line([(80, 113), (80, 202 - hb)], 4, sand)
        frames.append(c.finish(pivot=(80, 115), border=5))
    return frames


def numeral(n, color):
    c = Cut(220, 260)
    c.text(str(n), 110, 130, 230, color)
    return c.finish(pivot=(110, 130), border=9)


def choice_bubble(ch, ring):
    c = Cut(250, 250)
    c.ellipse(125, 125, 116, 116, ring)
    c.ellipse(125, 125, 98, 98, (255, 255, 255), sil=False)
    if ch in ("hand", "wait"):
        import icons
        if ch == "hand":
            icons.draw_hand(c, 125, 130, 118)
        else:
            icons.draw_hourglass(c, 125, 125, 140, level=0.6)
    else:
        c.emoji(ch, 125, 125, 132, sil=False)
    return c.finish(pivot=(125, 125), border=7)


def steam_burst():
    c = Cut(380, 320)
    c.polygon(star_pts(190, 180, 168, 104, 14, -90), (255, 226, 92))
    for cx, cy, r in ((130, 190, 62), (190, 150, 76), (252, 190, 60), (160, 232, 54), (222, 232, 54)):
        c.ellipse(cx, cy, r, r * 0.92, (250, 252, 255), sil=False)
    return c.finish(pivot=(190, 290), border=6)


def steam_heart():
    c = Cut(180, 170)
    pts = heart_pts(90, 88, 128)
    c.line(pts + pts[:2], 13, (238, 244, 252), sil=True)
    return c.finish(pivot=(90, 88), border=4, shadow_alpha=0.18)


def sparkle(color=(255, 214, 64)):
    c = Cut(300, 300)
    c.polygon(star_pts(150, 150, 140, 34, 4, -90), color)
    for a, r, d in ((45, 16, 92), (135, 12, 100), (225, 14, 96), (315, 12, 104)):
        x, y = 150 + d * math.cos(math.radians(a)), 150 + d * math.sin(math.radians(a))
        c.polygon(star_pts(x, y, r * 2.2, r * 0.6, 4, -90), (255, 255, 255))
    return c.finish(pivot=(150, 150), border=5)


def straw_sprite(p_bottom, p_tip, bend, width=15):
    """A striped bendy straw drawn from cup (p_bottom) to tip, bending through `bend`."""
    xs = [p_bottom[0], p_tip[0], bend[0]]
    ys = [p_bottom[1], p_tip[1], bend[1]]
    x0, y0 = min(xs) - 20, min(ys) - 20
    w, h = int(max(xs) - x0 + 20), int(max(ys) - y0 + 20)
    c = Cut(w, h)
    loc = lambda p: (p[0] - x0, p[1] - y0)  # noqa: E731
    pts = smooth_curve(loc(p_bottom), loc(bend), loc(p_tip), 30)
    c.line(pts, width, (255, 255, 255), sil=True)
    L = polyline_length(pts)
    d = 6.0
    while d < L - 4:
        seg_pts = [polyline_point(pts, d + k) for k in range(0, int(width * 0.8), 3)]
        c.line(seg_pts, width, (236, 84, 96))
        d += width * 1.75
    spr = c.finish(pivot=loc(p_bottom), border=3, shadow_alpha=0.2)
    return spr
