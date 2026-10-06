"""Episode 11, stage 1: prototype stills of the riskiest movement (the "wow chain"), plan section 8.

Renders, in the porch world under the right light, with rig2 Snip and Crinkle and a plain grey Pip stand-in
(scale 0.9; rig v2 Pip is being built separately):
    99 s the glowing face from the front; 120.6 s mid-turn at 90 degrees; 123.5 s the small smile on Crinkle's
    chest; 131.2 s halfway through his step aside (the soft wipe); 133 s the giant face with all three friends;
    144 s Pip's wing in the light (close, plus a medium view showing the wing-shaped gap in the wall face);
    and the light states: 2 s golden (a heart on the stand-in's tummy), 8 s sunset, 60 s early evening.

Run:  python3 episodes/ep11_proto.py              (all stills -> build/ep11_proto_*.png, sheet -> reviews/)
      python3 episodes/ep11_proto.py --still T    (one frame, plan framing -> build/)
Prints the numeric checks: mean luma (early evening, pre-glow) and light-to-face clearances.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

import hires  # noqa: E402

hires.set_res(2)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import acting as K  # noqa: E402
import ep11_light as L  # noqa: E402
import props_porch as P  # noqa: E402
import props_pumpkin as PK  # noqa: E402
import rig2 as R  # noqa: E402
from hires import RCut  # noqa: E402
from paperlib import ease_in_out, lerp, mix, place, rot, seg  # noqa: E402

RES = hires.RES
FLOOR = P.FLOOR_Y
CAM = K.Cam("land", P.WORLD_W, P.WORLD_H, P.LAND_Y0, P.VERT_X0, res=RES)
WORLD = P.Porch(CAM)
PUMP = PK.Pumpkin()
BOX_SPR = P.marker_box(0)
BOX_SPR3 = P.marker_box(3)


# ---------------------------------------------------------------- Pip stand-in (plain grey, Pip's size)
GREY = (160, 160, 168)
GREY_D = (128, 128, 138)
GREY_L = (190, 190, 198)
GREY_B = (112, 112, 122)


class PipStandIn:
    """A plain grey silhouette at Pip's size (0.9): head centre at the big friends' shoulder height, a beak that
    shows where she looks, wings as simple feathered shapes (about 92 units long), webbed feet."""

    def __init__(self, scale=0.9):
        self.s = scale
        self.k = scale * RES
        self.neck, self.head_drop, self.sh = 168, 14, (63, 34)
        self._heads = {}
        c = RCut(200, 200, self.k)
        c.ellipse(100, 104, 80, 82, GREY)
        c.ellipse(100, 122, 52, 54, GREY_L, sil=False)
        self.body = c.finish(pivot=(100, 26))
        c = RCut(80, 130, self.k)
        c.ellipse(40, 60, 26, 48, GREY_D)
        for dx in (-13, 0, 13):
            c.ellipse(40 + dx, 104, 9, 14, GREY_D)
        c.ellipse(37, 54, 14, 30, GREY, sil=False)
        self.wing = c.finish(pivot=(40, 16))
        c = RCut(40, 60, self.k)                             # two-part wing (like rig v2: about 40 + 44)
        c.ellipse(20, 26, 14, 24, GREY_D)
        self.w_upper = c.finish(pivot=(20, 6))
        c = RCut(44, 72, self.k)
        c.ellipse(22, 28, 15, 26, GREY_D)
        for dx in (-10, 0, 10):
            c.ellipse(22 + dx, 54, 7, 11, GREY_D)
        c.ellipse(20, 26, 8, 16, GREY, sil=False)
        self.w_fore = c.finish(pivot=(22, 6))
        self.U, self.F = 36.0, 48.0                          # world units at 0.9 (forearm incl. feather tips)
        c = RCut(80, 40, self.k)
        c.ellipse(40, 18, 30, 12, GREY_B)
        for dx in (-18, 0, 18):
            c.ellipse(40 + dx, 24, 9, 7, GREY_B)
        self.foot = c.finish(pivot=(40, 30))
        c = RCut(140, 120, self.k)
        c.text("Pip stand-in", 70, 60, 26, (90, 90, 100))
        self.label = c.finish(pivot=(70, 60), border=4, shadow_alpha=0.15)

    def head(self, turn, up):
        key = (round(turn, 1), round(up, 1))
        if key not in self._heads:
            c = RCut(260, 270, self.k)
            o = (130, 232)                                   # pivot (neck)
            for dx, dy, rx, ry, th in ((-14, 6, 9, 22, 24), (0, 0, 10, 26, 0), (14, 8, 8, 20, -26)):
                c.ellipse(o[0] + dx + 10 * key[0], o[1] - 178 + dy, rx, ry, GREY, theta=th)
            c.ellipse(o[0], o[1] - 82, 100, 94, GREY)
            bx = o[0] + 62 * math.sin(math.radians(50 * key[0]))
            by = o[1] - 52 - 16 * key[1]
            w = 1 - 0.35 * abs(key[0])
            c.ellipse(bx + 6 * key[0], by + 8, 24 * w, 9, GREY_B)
            c.ellipse(bx + 6 * key[0], by, 33 * w, 13, GREY_B)
            self._heads[key] = (c.finish(pivot=o), (bx - o[0], by - o[1], 33 * w, 13))
        return self._heads[key]

    def anchor(self, st):
        s = self.s

        def Pp(dx, dy):
            rx, ry = rot(dx * s, dy * s, st["lean"])
            return st["x"] + rx, st["y"] - st["hop"] + ry
        return Pp

    def head_pivot(self, st):
        return self.anchor(st)(0, -self.neck + self.head_drop)

    def shoulder(self, st, side):
        return self.anchor(st)(-self.sh[0] if side == "l" else self.sh[0], -self.neck + self.sh[1] + 12)

    def wing_angle(self, st, side):
        tgt = st.get("wing_" + side)
        if tgt is None:
            return st["lean"] + (-12 if side == "l" else 12) + st.get("flap", 0) * (-1 if side == "l" else 1)
        S = self.shoulder(st, side)
        return math.degrees(math.atan2(tgt[0] - S[0], tgt[1] - S[1]))

    def beak(self, st):
        """Beak outline points (world) for clearance checks."""
        spr, (bx, by, rx, ry) = self.head(st["turn"], st["up"])
        hx, hy = self.head_pivot(st)
        pts = []
        for i in range(32):
            a = 2 * math.pi * i / 32
            px, py = rot((bx + rx * math.cos(a)) * self.s, (by + ry * math.sin(a)) * self.s, st["lean"])
            pts.append((hx + px, hy + py))
        return pts

    def draw(self, base, cam, st, parts=("feet", "wing_l", "body", "head", "wing_r")):
        S = cam.S
        if "feet" in parts:
            for side in (-1, 1):
                place(base, self.foot, S((st["x"] + side * 30 * self.s, st["y"] - st["hop"] + 3)))
        if "wing_l" in parts:
            place(base, self.wing, S(self.shoulder(st, "l")), angle=self.wing_angle(st, "l"))
        if "body" in parts:
            place(base, self.body, S(self.anchor(st)(0, -self.neck)), angle=st["lean"])
        if "head" in parts:
            spr, _ = self.head(st["turn"], st["up"])
            place(base, spr, S(self.head_pivot(st)), angle=st["lean"] + st.get("tilt", 0))
        if "wing_r" in parts:
            if st.get("wing_r") is None:
                place(base, self.wing, S(self.shoulder(st, "r")), angle=self.wing_angle(st, "r"))
            else:
                Sh = self.shoulder(st, "r")
                E, T = self.wing_ik(Sh, st["wing_r"])
                place(base, self.w_upper, S(Sh), angle=math.degrees(math.atan2(E[0] - Sh[0], E[1] - Sh[1])))
                place(base, self.w_fore, S(E), angle=math.degrees(math.atan2(T[0] - E[0], T[1] - E[1])))

    def wing_ik(self, Sh, T, bend=-1):
        """Elbow for a two-part wing reaching its feather tips to T (elbow up, so the forearm lies flat)."""
        dx, dy = T[0] - Sh[0], T[1] - Sh[1]
        d = min(max(math.hypot(dx, dy), 1e-3), (self.U + self.F) * 0.999)
        base = math.atan2(dy, dx)
        a = math.acos(max(-1.0, min(1.0, (self.U ** 2 + d * d - self.F ** 2) / (2 * self.U * d))))
        ang = base + bend * a
        E = (Sh[0] + self.U * math.cos(ang), Sh[1] + self.U * math.sin(ang))
        T2 = (Sh[0] + d * math.cos(base), Sh[1] + d * math.sin(base))
        return E, T2

    def head_mask(self, st, cam, size, grow=6):
        m = Image.new("RGBA", size, (0, 0, 0, 0))
        self.draw(m, cam, st, parts=("head",))
        return L.grow_mask(m.getchannel("A"), int(round(grow * cam.res)))


PIP = PipStandIn()

# ---------------------------------------------------------------- performances (only what the stills need)
# Early (light states): Snip sketching under the chime, Crinkle polishing, Pip with the hearts; at 60 s the
# eyes and smile are drawn and Crinkle is still crouched by the pumpkin.
SN0 = R.Perf2(R.Puppet("snip", 1.15), seed=1, x=560, y=FLOOR, turn=0.4, eyes="happy", mouth="smile", brows="calm")
CR0 = R.Perf2(R.Puppet("crinkle", 1.2), seed=2, x=780, y=FLOOR, turn=0.6, eyes="closed", mouth="hum")
SN0.reach(0.0, 0.01, "r", (650, 1300)).reach(0.0, 0.01, "l", (600, 1320))
CR0.reach(0.0, 0.01, "r", (872, 1405))
CR0.to(2.0, 2.5, "io", elb_r=-40).to(7.5, 8.0, "io", elb_r=-20)
SN0.face(7.0, eyes="normal", mouth="o", brows="up")
SN0.walk(48.6, 49.4, 680, steps=2).to(49.4, 49.8, "io", turn=0.6)
SN0.face(52.0, eyes="sparkle", mouth="smile_open", brows="up").ears(52.0, 52.4, "perk")
CR0.walk(43.0, 45.0, 1160).to(45.0, 45.3, "io", turn=-0.6)
CR0.to(53.0, 54.0, "io", sq=0.86, lean=-6, head_dy=10).face(53.0, eyes="normal", mouth="yum", brows="think")
CR0.reach(55.5, 56.4, "l", (1062, 1420)).reach(59.6, 60.0, "l", (1095, 1350))
CR0.face(59.7, eyes="happy", mouth="smile_open", brows="up")


def pip0(t):
    st = dict(x=1130, y=FLOOR, hop=0.0, lean=0.0, turn=-0.2, up=0.0, wing_l=None, wing_r=None, flap=0.0)
    if t < 6:
        st["hop"] = 22 * max(0.0, math.sin(math.pi * (t % 0.8) / 0.8)) if t < 1.0 else 0.0
        st["flap"] = 30 * abs(math.sin(2 * math.pi * t * 2.0))
        st["turn"], st["up"] = 0.1, 0.2
    elif t < 10:
        st["x"] = 1150
        st["hop"] = 30 * max(0.0, math.sin(math.pi * seg(t, 7.6, 8.4)))
        st["up"] = 0.9
        st["wing_r"] = (1226, 1250)
    else:
        st.update(x=640, turn=0.4, up=0.2)
    return st


# Late (the wow chain, 95-148 s)
SN = R.Perf2(R.Puppet("snip", 1.15), seed=1, x=640, y=FLOOR, turn=0.6, eyes="normal", mouth="smile", brows="calm")
CR = R.Perf2(R.Puppet("crinkle", 1.2), seed=2, x=500, y=FLOOR, turn=0.5, eyes="normal", mouth="smile")
# 98.5 the glow
SN.face(98.5, eyes="wide", mouth="o", brows="up").ears(98.5, 98.8, "alarm")
SN.face(98.9, eyes="sparkle", mouth="smile_open", brows="up").ears(98.9, 99.3, "perk")
CR.face(98.5, eyes="wide", mouth="o", brows="up").face(99.3, eyes="sparkle", mouth="smile_open")
# 102.5 they come closer
SN.walk(102.6, 104.0, 720)
CR.walk(102.5, 104.5, 1130).to(104.5, 104.8, "io", turn=-0.5)
CR.face(104.5, eyes="happy", mouth="smile_open", brows="calm")
# 117 Snip (and Pip) step back left; Crinkle walks behind the pumpkin
SN.walk(117.0, 117.8, 520).face(117.8, eyes="normal", mouth="o", brows="up").ears(117.8, 118.1, "perk")
CR.walk(117.0, 118.0, 960).to(117.6, 118.0, "io", turn=0.0)
PAW_L, PAW_R = (862, 1402), (1058, 1402)
CR_ASIDE = 1400                                   # plan: 1340 (his ear then overlaps the face)
CR.reach(118.0, 118.3, "l", PAW_L).reach(118.0, 118.3, "r", PAW_R)
CR.face(118.0, eyes="normal", mouth="smile", brows="think").to(118.0, 118.3, "io", look_y=10, head_dy=6)
CR.to(118.3, 118.6, "io", sq=0.94, lean=3).face(118.3, eyes="closed", mouth="blow", brows="think")
CR.to(119.0, 119.3, "io", sq=1.0, lean=0).face(119.0, eyes="normal", mouth="o", brows="up")
for a, b in ((119.5, 120.6), (120.9, 122.0)):
    CR.to(a, a + 0.25, "io", sq=0.95, lean=-3).to(b - 0.25, b, "io", sq=1.0, lean=0)
    CR.face(a, eyes="normal", mouth="blow", brows="think").face(b + 0.15, eyes="happy", mouth="smile", brows="calm")
CR.to(122.0, 122.5, "io", look_y=12, head_dy=8)
# 125 the others see the smile on his tummy
SN.face(123.0, eyes="normal", mouth="smile", brows="calm")
SN.face(125.0, eyes="sparkle", mouth="smile_open", brows="up").reach(125.0, 125.4, "r", (790, 1270), "back")
SN.to(125.9, 126.2, "io", arm_r=10, elb_r=-14)
# 127 Crinkle looks up (?), then down: his tummy is smiling; laughs and wiggles
CR.to(127.0, 127.3, "io", arm_l=-10, elb_l=14, arm_r=10, elb_r=-14)
CR.to(127.0, 127.3, "io", look_x=-10, look_y=-4, head_dy=0).face(127.0, eyes="normal", mouth="o", brows="up")
CR.to(127.9, 128.2, "io", look_x=0, look_y=14, head_dy=12).face(127.9, eyes="wide", mouth="O", brows="up")
CR.face(128.5, eyes="happy", mouth="smile_open", brows="up").to(128.5, 128.8, "io", head_dy=4, look_y=6)
for i in range(4):
    v = 10 if i % 2 == 0 else -10
    CR.to(128.6 + i * 0.35, 128.95 + i * 0.35, "io", x=960 + v, lean=0.6 * v)
CR.to(130.0, 130.4, "io", x=960, lean=0)
# 130.5 the step aside: the smile slides off him onto the wall
CR.walk(130.5, 132.0, CR_ASIDE).to(130.5, 131.0, "io", turn=-0.4, look_y=-12, look_x=-6, head_dy=0)
CR.face(130.6, eyes="wide", mouth="O", brows="up").face(132.6, eyes="sparkle", mouth="smile_open")
SN.to(130.4, 130.8, "io", look_y=-14, tilt=-4, hturn=0.25).face(130.6, eyes="wide", mouth="O", brows="up")
SN.ears(130.6, 130.9, "alarm").face(132.2, eyes="sparkle", mouth="smile_open").ears(132.2, 132.6, "happy")
# 141 Pip's wing game: the big two laugh
SN.to(141.0, 141.4, "io", look_y=6, look_x=10, tilt=0, hturn=0.0).face(141.0, eyes="happy", mouth="smile_open")
CR.to(141.0, 141.4, "io", look_x=-12, look_y=6, turn=-0.5).face(141.0, eyes="happy", mouth="smile_open")


PIP_BACK = 700                                    # plan: 720
PIP_WING_X, PIP_WING_TIP = 812, (934.7, 1339)       # plan: x 820 and a 0.6x pattern on the wing


def pip(t):
    st = dict(x=600, y=FLOOR, hop=0.0, lean=0.0, turn=0.4, up=0.1, wing_l=None, wing_r=None, flap=0.0)
    if t >= 102.5:
        st.update(x=lerp(600, 850, ease_in_out(seg(t, 102.5, 104.2))), lean=0.0, turn=0.3)
    if t >= 117.0:
        st.update(x=lerp(850, PIP_BACK, ease_in_out(seg(t, 117.0, 117.9))), turn=0.4)
    if t >= 130.6:
        st.update(turn=0.25, up=0.9)
    if t >= 141.0:
        st.update(x=lerp(PIP_BACK, PIP_WING_X, ease_in_out(seg(t, 141.0, 142.2))), turn=-0.3, up=0.25)
        k = ease_in_out(seg(t, 142.4, 143.3))
        if k > 0:
            st["wing_r"] = (lerp(880, PIP_WING_TIP[0], k), lerp(1440, PIP_WING_TIP[1], k))
    return st


# ---------------------------------------------------------------- the pumpkin over time
def pumpkin_state(t):
    strokes = {}
    for name, a, b in (("eye_l", 45.2, 46.0), ("eye_r", 47.0, 47.8), ("smile", 56.5, 59.5), ("heart_l", 67.0, 67.9),
                       ("heart_r", 68.2, 69.1)):
        if t > a:
            strokes[name] = seg(t, a, b)
    holes = {}
    for name, a in (("eye_l", 85.6), ("eye_r", 86.4), ("heart", 87.2), ("smile", 88.0)):
        if t > a:
            holes[name] = seg(t, a, a + (0.4 if name == "smile" else 0.15))
    lid = "none"
    if t >= 89.4:
        lid = "on"
    if 90.4 <= t < 97.4:
        lid = "off"
    rotd = 90 * ease_in_out(seg(t, 119.5, 120.6)) + 90 * ease_in_out(seg(t, 120.9, 122.0))
    return dict(strokes=strokes, holes=holes, lid=lid, rot=rotd, lit=L.glow_k(t))


def proj_k(rotd):
    """How much of the cut face points at the wall (and at whoever stands behind the pumpkin)."""
    return ease_in_out(seg(rotd, 150.0, 179.0))


def chest_plane(rotd):
    return L.CHEST.shifted(dx=(180.0 - rotd) * 2.2)


# ---------------------------------------------------------------- one frame of the world
def render_world(t, d=None, cam=None, report=None):
    cam = cam or CAM
    late = t >= 90
    sn_p, cr_p = (SN, CR) if late else (SN0, CR0)
    sn, cr = sn_p.state(t, d), cr_p.state(t, d)
    ps = pip(t) if late else pip0(t)
    pk = pumpkin_state(t)
    glow = pk["lit"]
    size = (int(cam.w * cam.res), int(cam.h * cam.res))
    f = WORLD.background(t)
    place(f, BOX_SPR if t > 43 else BOX_SPR3, cam.S(P.MARKER_BOX_AT))
    # layers (drawn alone, so light can be clipped to each)
    wing_reach = ps.get("wing_r") is not None
    pip_parts = ("feet", "wing_l", "body", "head") if wing_reach else ("feet", "wing_l", "body", "head", "wing_r")
    lay_pip = L.Layer.of(size, lambda im: PIP.draw(im, cam, ps, parts=pip_parts), head=PIP.head_mask(ps, cam, size))
    lay_wing = L.Layer.of(size, lambda im: PIP.draw(im, cam, ps, parts=("wing_r",))) if wing_reach else None
    lay_sn = L.Layer.of(size, lambda im: sn_p.draw(im, t, cam, st=sn), head=L.head_mask(sn_p.a, sn, cam, size))
    lay_cr = L.Layer.of(size, lambda im: cr_p.draw(im, t, cam, st=cr), head=L.head_mask(cr_p.a, cr, cam, size))
    arms_over = (late and 118.0 <= t < 127.3) or (not late and t < 10)
    lay_arms = None
    if arms_over:
        sides = ("l", "r") if late else ("r",)
        lay_arms = L.Layer.of(size, lambda im: [cr_p.a._arm(im, cam, cr, s) for s in sides])
    # light on the porch (before anyone stands in front of it)
    caught = L.sun_light(f, t, cam, WORLD.albedo, occluders=[lay_pip])
    facing = max(0.0, math.cos(math.radians(pk["rot"])))
    L.floor_pool(f, cam, WORLD.albedo, glow, facing, side=math.sin(math.radians(pk["rot"])))
    pkk = proj_k(pk["rot"]) * glow
    occ = []
    if lay_cr is not None:
        occ.append((lay_cr.solid(), lay_cr.box, L.CHEST))
    if lay_wing is not None:
        occ.append((lay_wing.solid(), lay_wing.box, L.WING))
    Iw, bw = L.wall_light(f, cam, WORLD.albedo, pkk, occ)
    # characters: grade, warm glow, beams (never on faces)
    lit = {}
    if not late or t < 102.5:            # by the bench / opening: Crinkle behind Snip, Pip in front
        order = [("cr", lay_cr), ("sn", lay_sn), ("pip", lay_pip)]
    else:
        order = [("sn", lay_sn), ("cr", lay_cr), ("pip", lay_pip)]
    for name, lay in order:
        L.grade_layer(lay, t, glow, L.GLOW_AT, cam)
        if name == "pip":
            lit["pip_heart"] = L.heart_on_layer(lay, caught)
        if name == "cr" and pkk > 0:
            ck = ease_in_out(seg(pk["rot"], 140.0, 178.0)) * glow
            lit["cr"] = (L.beam_on_layer(lay, chest_plane(pk["rot"]), cam, ck), lay)
        lay.paste(f)
    # the pumpkin (a prop: graded with the dusk), its own light, then paws/wing over it
    spr = PUMP.paper(rot=pk["rot"], strokes=pk["strokes"], holes=pk["holes"], lid=pk["lid"])
    lay_pk = L.Layer.of(size, lambda im: place(im, spr, cam.S(PK.BASE)))
    L.grade_layer(lay_pk, t)
    lay_pk.paste(f)
    em = PUMP.emissive(rot=pk["rot"], lit=glow, holes=pk["holes"], lid=pk["lid"])
    if em is not None:
        place(f, em, cam.S(PK.BASE), shadow=False)
    if lay_arms is not None:
        L.grade_layer(lay_arms, t, glow, L.GLOW_AT, cam)
        lay_arms.paste(f)
    if lay_wing is not None:
        L.grade_layer(lay_wing, t, glow, L.GLOW_AT, cam)
        lit["wing"] = (L.beam_on_layer(lay_wing, L.WING, cam, pkk), lay_wing)
        lay_wing.paste(f)
    L.halo(f, cam, glow * (0.65 + 0.35 * facing))
    WORLD.front(f, t)
    L.rail_glow(f, t, cam)
    place(f, PIP.label, cam.S((ps["x"], ps["y"] + 22)), shadow=False, scale=0.8)
    if report is not None:
        report.update(dict(sn=sn, cr=cr, pip=ps, lit=lit, wall=(Iw, bw), pk=pk))
    return f


# ---------------------------------------------------------------- framing (the plan's shots at these times)
STILLS = [
    (2.0, (980, 1100), 1.0, "2 s golden: heart on the stand-in's tummy"),
    (8.0, (980, 1100), 1.0, "8 s sunset"),
    (60.0, (960, 1100), 1.0, "60 s early evening (wide)"),
    (99.0, (960, 1300), 1.9, "99 s the glow (close 1.9)"),
    (120.6, (960, 1180), 1.15, "120.6 s mid-turn, 90 deg"),
    (123.5, (960, 1290), 1.9, "123.5 s smile on his chest (close 1.9)"),
    (131.2, (960, 1080), 1.0 + 0.15 * (1 - ease_in_out(seg(131.2, 130.4, 131.6))), "131.2 s halfway: the soft wipe"),
    (133.0, (960, 1080), 1.0, "133 s the giant face"),
    (144.0, (920, 1290), 1.9, "144 s smile on the wing (close 1.9)"),
    (144.0, (960, 1100), 1.15, "144 s wing-shaped gap (medium-wide)"),
]
EXTRA = [(95.5, (960, 1100), 1.0, "95.5 s pre-glow (darkest, luma check)")]


def frame(t, centre, z, report=None):
    d = K.drawing_of(t)
    f = render_world(t, d, report=report)
    if z > 1.0001:
        f = K.zoom(f, z, CAM.S(centre))
    return f.resize((1920, 1080), Image.LANCZOS).convert("RGB")


def muzzle_pts(perf, st, n=36):
    """Crinkle's muzzle outline (world), from the rig: the muzzle ellipse 74 x 54 at head-local y -72."""
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        out.append(perf.a.face_point(st, (74 * math.cos(a) * 0.9, -72 + 54 * math.sin(a))))
    return out


def min_dist(pts_lit, outline):
    return min(L.clearance(pts_lit, p) for p in outline)


def checks(t, rep, img):
    out = []
    if t in (60.0, 95.5):
        out.append(f"luma {t:.1f}s = {L.luma(img):.1f}")
    lit = rep["lit"]
    if "cr" in lit and lit["cr"][0] is not None:
        I, lay = lit["cr"]
        pts = L.lit_points(I, lay.box, CAM, 0.02)
        chin = CR.a.face_point(rep["cr"], (0, -18))
        out.append(f"{t:.1f}s Crinkle: pattern edge to chin {L.clearance(pts, chin):.0f}, to muzzle outline "
                   f"{min_dist(pts, muzzle_pts(CR, rep['cr'])):.0f} (units; lit px {len(pts)})")
    if "wing" in lit and lit["wing"][0] is not None:
        I, lay = lit["wing"]
        pts = L.lit_points(I, lay.box, CAM, 0.02)
        beak = PIP.beak(rep["pip"])
        # the cone where the light passes at her own depth (chest plane), as if nothing blocked it
        pb = L._clip_box(L._pbox(L.CHEST, CAM), (10 ** 6, 10 ** 6))
        cone = L.lit_points(L.pattern(L.CHEST, CAM, pb), pb, CAM, 0.02)
        out.append(f"{t:.1f}s Pip: wing light to beak {min_dist(pts, beak):.0f}; beam at her depth to beak "
                   f"{min_dist(cone, beak):.0f} (units; lit px on wing {len(pts)})")
    return out


def contact_sheet(items, path, w=640):
    import paperlib
    h = int(w * 1080 / 1920)
    cols = 3
    rows = math.ceil(len(items) / cols)
    sheet = Image.new("RGB", (w * cols + 10 * (cols + 1), (h + 40) * rows + 10), (250, 248, 244))
    d = ImageDraw.Draw(sheet)
    font = paperlib.round_font(22)
    for i, (img, label) in enumerate(items):
        x = 10 + (i % cols) * (w + 10)
        y = 10 + (i // cols) * (h + 40)
        d.text((x + 3, y + 4), label, fill=(60, 50, 70), font=font)
        sheet.paste(img.resize((w, h), Image.LANCZOS), (x, y + 34))
    sheet.save(path)
    print("wrote", path)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    if "--still" in sys.argv:
        tt = float(sys.argv[sys.argv.index("--still") + 1])
        cand = [s for s in STILLS + EXTRA if abs(s[0] - tt) < 1e-6] or [(tt, (960, 1080), 1.0, "")]
        rep = {}
        img = frame(tt, cand[0][1], cand[0][2], rep)
        out = os.path.join(ROOT, "build", f"ep11_proto_{tt:.2f}.png")
        img.save(out)
        print("wrote", out)
        for line in checks(tt, rep, img):
            print(line)
    else:
        items, lines = [], []
        order = [STILLS[i] for i in (3, 4, 5, 6, 7, 8, 9, 0, 1, 2)] + EXTRA
        for i, (tt, c, z, label) in enumerate(order):
            rep = {}
            img = frame(tt, c, z, rep)
            tag = f"{tt:.2f}" + ("_wide" if (tt == 144.0 and z < 1.5) else "")
            img.save(os.path.join(ROOT, "build", f"ep11_proto_{tag}.png"))
            if (tt, label) not in [(e[0], e[3]) for e in EXTRA]:
                items.append((img, label))
            lines += checks(tt, rep, img)
            print("rendered", tag, flush=True)
        contact_sheet(items, os.path.join(ROOT, "reviews", "ep11_proto_wow.png"))
        print("\n".join(lines))
