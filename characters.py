"""Snip (paper bunny) and Crinkle (paper bear), built from paper parts.

Snip's ears are separate pieces so they can wiggle, droop and shoot up.
Both characters support blinking, breathing (squash), and per-shot expressions.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

from paperlib import Cut, Sprite, place, rot, spiky_ellipse_pts, star_pts

EYE = (38, 32, 44)
WHITE = (255, 255, 255)
MOUTH_DARK = (120, 40, 60)
TONGUE = (240, 128, 150)

SNIP = dict(fur=(226, 214, 242), ear_in=(247, 172, 198), tee=(80, 182, 235),
            star=(255, 214, 64), nose=(240, 118, 160), cheek=(242, 178, 210))
CRINKLE = dict(fur=(198, 134, 80), ear_in=(150, 96, 58), muzzle=(246, 224, 190),
               nose=(72, 46, 36), cheek=(226, 140, 110), foot=(150, 96, 58),
               scarf=(255, 204, 62), stripe=(240, 118, 70))

BLINKABLE = ("normal", "wide", "worried", "sparkle")


def _eyes(c, pts, kind, r, look=(0, 0)):
    rx, ry = r
    lx, ly = look
    for i, (x, y) in enumerate(pts):
        s = -1 if i == 0 else 1
        ex, ey = x + lx, y + ly
        if kind in ("normal", "worried"):
            c.ellipse(ex, ey, rx, ry, EYE, sil=False)
            c.ellipse(ex + rx * 0.35, ey - ry * 0.38, rx * 0.38, rx * 0.38, WHITE, sil=False)
        elif kind == "wide":
            c.ellipse(ex, ey, rx * 1.3, ry * 1.28, EYE, sil=False)
            c.ellipse(ex + rx * 0.45, ey - ry * 0.45, rx * 0.48, rx * 0.48, WHITE, sil=False)
            c.ellipse(ex - rx * 0.4, ey + ry * 0.5, rx * 0.2, rx * 0.2, WHITE, sil=False)
        elif kind == "sparkle":
            c.ellipse(ex, ey, rx * 1.32, ry * 1.3, EYE, sil=False)
            c.polygon(star_pts(ex + rx * 0.3, ey - ry * 0.3, rx * 0.75, rx * 0.3, 4, -90), WHITE, sil=False)
            c.ellipse(ex - rx * 0.5, ey + ry * 0.55, rx * 0.22, rx * 0.22, WHITE, sil=False)
        elif kind == "happy":
            c.arc(x, y + ry * 0.55, rx * 1.15, ry * 0.9, 200, 340, rx * 0.42, EYE)
        elif kind == "closed":
            c.arc(x, y - ry * 0.3, rx * 1.1, ry * 0.7, 20, 160, rx * 0.4, EYE)
        elif kind == "blink":
            c.arc(x, y - ry * 0.1, rx * 1.05, ry * 0.35, 15, 165, rx * 0.36, EYE)
        if kind == "worried":
            c.line([(x + s * rx * 1.1, y - ry * 1.45), (x - s * rx * 0.9, y - ry * 1.95)], rx * 0.38, EYE)


def _mouth(c, cx, my, kind, k=1.0):
    if kind == "w":
        c.arc(cx - 9 * k, my, 9 * k, 8 * k, 10, 170, 4 * k, EYE)
        c.arc(cx + 9 * k, my, 9 * k, 8 * k, 10, 170, 4 * k, EYE)
    elif kind == "smile":
        c.arc(cx, my - 6 * k, 24 * k, 18 * k, 25, 155, 5 * k, EYE)
    elif kind == "yum":
        c.arc(cx, my - 6 * k, 24 * k, 18 * k, 25, 155, 5 * k, EYE)
        c.ellipse(cx + 13 * k, my + 7 * k, 8 * k, 7 * k, TONGUE, sil=False)
    elif kind == "grin":
        c.chord(cx, my - 6 * k, 26 * k, 26 * k, 0, 180, MOUTH_DARK)
        c.chord(cx, my + 12 * k, 13 * k, 8 * k, 180, 360, TONGUE)
    elif kind == "o":
        c.ellipse(cx, my + 6 * k, 10 * k, 12 * k, MOUTH_DARK, sil=False)
    elif kind == "O":
        c.ellipse(cx, my + 8 * k, 14 * k, 17 * k, MOUTH_DARK, sil=False)
    elif kind == "blow":
        c.ellipse(cx, my + 6 * k, 7 * k, 7 * k, MOUTH_DARK, sil=False)
    elif kind == "flat":
        c.line([(cx - 12 * k, my + 4 * k), (cx + 12 * k, my + 4 * k)], 4 * k, EYE)
    elif kind == "wobble":
        c.line([(cx - 14 * k, my + 6 * k), (cx - 5 * k, my + 1 * k), (cx + 5 * k, my + 7 * k),
                (cx + 14 * k, my + 2 * k)], 4 * k, EYE)


# ---------- Snip ----------
SNIP_FACE_PIVOT = (150, 260)
SNIP_FACE_CENTER = (150, 150)
SNIP_EAR_BASE = ((-50, -180), (50, -180))   # ear pivots relative to face pivot
SNIP_EAR_TILT = (9, -9)
SNIP_MOUTH = (150, 186)


def snip_face(eyes="normal", mouth="w", look=(0, 0)):
    c = Cut(300, 290)
    c.ellipse(150, 150, 140, 122, SNIP["fur"])
    puff = mouth == "blow"
    for x in (76, 224):
        c.ellipse(x, 186, 27 if puff else 22, 17 if puff else 13, SNIP["cheek"], sil=False)
    _eyes(c, [(103, 138), (197, 138)], eyes, (15, 20), look)
    c.ellipse(150, 170, 13, 9, SNIP["nose"], sil=False)
    _mouth(c, 150, 186, mouth)
    return c.finish(pivot=SNIP_FACE_PIVOT)


def snip_ear():
    c = Cut(110, 290)
    c.ellipse(55, 145, 46, 132, SNIP["fur"])
    c.ellipse(55, 163, 24, 96, SNIP["ear_in"], sil=False)
    return c.finish(pivot=(55, 255))


def snip_frizz():
    c = Cut(380, 350)
    c.polygon(spiky_ellipse_pts(190, 175, 150, 132, 34, 20), SNIP["fur"])
    return c.finish(pivot=(190, 175))


def snip_body():
    c = Cut(240, 252)
    fur = SNIP["fur"]
    c.ellipse(80, 228, 44, 22, fur)
    c.ellipse(160, 228, 44, 22, fur)
    c.ellipse(120, 122, 100, 106, SNIP["tee"])
    c.chord(120, 18, 42, 26, 0, 180, fur)
    c.polygon(star_pts(120, 130, 32, 14.4), SNIP["star"], sil=False)
    return c.finish(pivot=(120, 20))


def snip_arm():
    c = Cut(60, 150)
    c.rrect(9, 10, 51, 144, 21, SNIP["fur"])
    c.rrect(4, 4, 56, 54, 22, SNIP["tee"])
    return c.finish(pivot=(30, 26))


# ---------- Crinkle ----------
CRINKLE_MOUTH = (170, 250)


def crinkle_head(eyes="normal", mouth="smile", look=(0, 0)):
    c = Cut(340, 330)
    fur = CRINKLE["fur"]
    for x in (70, 270):
        c.ellipse(x, 74, 56, 56, fur)
        c.ellipse(x, 78, 31, 31, CRINKLE["ear_in"], sil=False)
    c.ellipse(170, 190, 160, 128, fur)
    c.ellipse(170, 240, 74, 54, CRINKLE["muzzle"], sil=False)
    puff = mouth == "blow"
    for x in (78, 262):
        c.ellipse(x, 224, 30 if puff else 22, 19 if puff else 13, CRINKLE["cheek"], sil=False)
    _eyes(c, [(110, 170), (230, 170)], eyes, (16, 21), look)
    c.ellipse(170, 216, 27, 18, CRINKLE["nose"], sil=False)
    c.ellipse(161, 211, 8, 4, (140, 104, 88), sil=False)
    _mouth(c, 170, 250, mouth, 1.1)
    return c.finish(pivot=(170, 312))


def crinkle_body():
    c = Cut(290, 272)
    c.ellipse(95, 248, 50, 22, CRINKLE["foot"])
    c.ellipse(195, 248, 50, 22, CRINKLE["foot"])
    c.ellipse(145, 136, 125, 114, CRINKLE["fur"])
    c.ellipse(145, 162, 72, 70, CRINKLE["muzzle"], sil=False)
    c.polygon([(196, 44), (238, 44), (248, 130), (210, 134)], CRINKLE["scarf"])
    c.polygon([(214, 92), (243, 90), (245, 106), (216, 108)], CRINKLE["stripe"], sil=False)
    c.rrect(42, 12, 248, 60, 24, CRINKLE["scarf"])
    for x in (88, 136, 184):
        c.rrect(x, 12, x + 18, 60, 4, CRINKLE["stripe"], sil=False)
    return c.finish(pivot=(145, 22))


def crinkle_arm():
    c = Cut(72, 162)
    c.rrect(8, 8, 64, 154, 28, CRINKLE["fur"])
    c.ellipse(36, 132, 17, 13, CRINKLE["muzzle"], sil=False)
    return c.finish(pivot=(36, 30))


def _mirror(spr):
    img = spr.img.transpose(Image.FLIP_LEFT_RIGHT)
    sh = spr.shadow.transpose(Image.FLIP_LEFT_RIGHT) if spr.shadow else None
    return Sprite(img, (img.width - spr.pivot[0], spr.pivot[1]), sh)


def _contact_shadow(w):
    m = Image.new("L", (w + 80, 120), 0)
    ImageDraw.Draw(m).ellipse([40, 45, 40 + w, 75], fill=110)
    img = Image.new("RGBA", m.size, (55, 38, 30, 255))
    img.putalpha(m.filter(ImageFilter.GaussianBlur(9)))
    return Sprite(img, (img.width / 2, 60))


class Character:
    def __init__(self, kind, scale=1.0):
        self.kind, self.s = kind, scale
        if kind == "snip":
            self.body, arm = snip_body(), snip_arm()
            self.neck_h, self.shoulder, self.head_drop = 230, (92, 52), 9
            self._head_fn, self._default = snip_face, ("normal", "w")
            self.ear = snip_ear().scaled(scale)
            self.frizz = snip_frizz().scaled(scale)
            self.mouth_local = (SNIP_MOUTH[0] - SNIP_FACE_PIVOT[0], SNIP_MOUTH[1] - SNIP_FACE_PIVOT[1])
            foot_w = 200
        else:
            self.body, arm = crinkle_body(), crinkle_arm()
            self.neck_h, self.shoulder, self.head_drop = 248, (112, 64), 8
            self._head_fn, self._default = crinkle_head, ("normal", "smile")
            self.ear = None
            self.mouth_local = (0, CRINKLE_MOUTH[1] - 312)
            foot_w = 240
        self.body = self.body.scaled(scale)
        self.arm_l = arm.scaled(scale)
        self.arm_r = _mirror(arm).scaled(scale)
        self.arm_len = (self.arm_l.img.height - self.arm_l.pivot[1]) - 40 * scale
        self.ground = _contact_shadow(int(foot_w * scale))
        self._heads = {}

    def head(self, eyes, mouth, look):
        key = (eyes, mouth, look)
        if key not in self._heads:
            self._heads[key] = self._head_fn(eyes, mouth, look).scaled(self.s)
        return self._heads[key]

    def anchor(self, x, base_y, hop=0.0, lean=0.0):
        s = self.s
        bx, by = x, base_y - hop

        def P(dx, dy):
            rx, ry = rot(dx * s, dy * s, lean)
            return bx + rx, by + ry
        return P

    def shoulder_pt(self, x, base_y, side, hop=0.0, lean=0.0, squash=1.0):
        P = self.anchor(x, base_y, hop, lean)
        sx = -self.shoulder[0] if side == "l" else self.shoulder[0]
        return P(sx, (-self.neck_h + self.shoulder[1]) * squash)

    def paw_tip(self, x, base_y, side, arm_angle, hop=0.0, lean=0.0, squash=1.0):
        sh = self.shoulder_pt(x, base_y, side, hop, lean, squash)
        vx, vy = rot(0, self.arm_len, arm_angle + lean)
        return sh[0] + vx, sh[1] + vy

    def head_pivot(self, x, base_y, hop=0.0, lean=0.0, squash=1.0, head_dy=0.0):
        P = self.anchor(x, base_y, hop, lean)
        return P(0, -self.neck_h * squash + self.head_drop + head_dy)

    def mouth_pt(self, x, base_y, hop=0.0, lean=0.0, squash=1.0, head_dy=0.0, head_tilt=0.0):
        hx, hy = self.head_pivot(x, base_y, hop, lean, squash, head_dy)
        mx, my = rot(self.mouth_local[0] * self.s, self.mouth_local[1] * self.s, lean + head_tilt)
        return hx + mx, hy + my

    def draw(self, base, x, base_y, hop=0.0, lean=0.0, head_tilt=0.0, arm_l=0.0, arm_r=0.0,
             eyes=None, mouth=None, look=(0, 0), alpha=1.0, squash=1.0, head_dy=0.0,
             blink=False, ears=(0.0, 0.0), ear_stretch=1.0, frizz=0.0):
        """arm_l/arm_r are degrees CCW from hanging down (arm_l<0 swings out left, arm_r>0 out right).
        squash < 1 squashes the body down onto the feet, > 1 stretches it up."""
        eyes = eyes or self._default[0]
        mouth = mouth or self._default[1]
        if blink and eyes in BLINKABLE:
            eyes = "blink"
        s = self.s
        ground_a = max(0.25, 1 - hop / 160) * alpha
        place(base, self.ground, (x, base_y + 6), alpha=ground_a, sx=max(0.6, 1 - hop / 300), shadow=False)
        P = self.anchor(x, base_y, hop, lean)
        neck = P(0, -self.neck_h * squash)
        place(base, self.body, neck, angle=lean, alpha=alpha, sx=1 / math.sqrt(squash), sy=squash)
        place(base, self.arm_l, self.shoulder_pt(x, base_y, "l", hop, lean, squash), angle=arm_l + lean, alpha=alpha)
        place(base, self.arm_r, self.shoulder_pt(x, base_y, "r", hop, lean, squash), angle=arm_r + lean, alpha=alpha)
        hx, hy = self.head_pivot(x, base_y, hop, lean, squash, head_dy)
        ha = lean + head_tilt
        if self.ear is not None:
            if frizz > 0.01:
                cx, cy = rot(0, (SNIP_FACE_CENTER[1] - SNIP_FACE_PIVOT[1]) * s, ha)
                place(base, self.frizz, (hx + cx, hy + cy), angle=ha, scale=frizz, alpha=alpha)
            for (ox, oy), tilt, extra in zip(SNIP_EAR_BASE, SNIP_EAR_TILT, ears):
                ex, ey = rot(ox * s, oy * s, ha)
                place(base, self.ear, (hx + ex, hy + ey), angle=ha + tilt + extra, sy=ear_stretch, alpha=alpha)
        place(base, self.head(eyes, mouth, look), (hx, hy), angle=ha, alpha=alpha)
