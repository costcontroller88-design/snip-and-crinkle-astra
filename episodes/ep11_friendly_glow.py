"""Episode 11 "Pip and the Friendly Glow" (~160 s, landscape 1920x1080 at 30 fps, rig v2, 2x render).

One 1920x1920 porch world (props_porch) filmed by cameras; light from ep11_light; the pumpkin from props_pumpkin;
Snip and Crinkle from rig2, Pip from rig2_pip (rig v2, scale 0.9).

Stage 3, part 1 (this file so far): the Lead's stage-1 fixes (plan section 4, L1-L5) with the real Pip; the
performances cover shots 1-4 (0-12.5 s) and the wow chain (shots 33-40c, 117-148 s). Part 2 fills 12.5-117 and
148-160, the sound (make_buses) and the full render.

Run:  python3 episodes/ep11_friendly_glow.py --check       (Lead's check sheet -> reviews/ep11_check_L.png, numbers)
      python3 episodes/ep11_friendly_glow.py --still T     (one frame through the plan's camera -> build/)
Any other flag is refused (never "render everything" by accident).

    render_world(t, d, cam, bg=None, report=None)  # the world at time t, drawing d, through a K.Cam (RGBA)
    frame(t)                                       # landscape frame through the shot camera (RGB 1920x1080)
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
import rig2_pip as RP  # noqa: E402
from hires import RCut  # noqa: E402
from paperlib import ease_in_out, place, rot, seg  # noqa: E402

RES = hires.RES
DUR = 160.0
FLOOR = P.FLOOR_Y
CAM = K.Cam("land", P.WORLD_W, P.WORLD_H, P.LAND_Y0, P.VERT_X0, res=RES)
WORLD = P.Porch(CAM)
PUMP = PK.Pumpkin()
BOX_SPR = P.marker_box(0)
BOX_SPR3 = P.marker_box(3)


# ---------------------------------------------------------------- Pip with a flat (open) wing
def flat_wing(k):
    """Pip's right wing held open and flat toward the camera (to catch light): a broad rounded blade with four
    short feather tips at its end. Pivot at the elbow; the blade lies along the forearm (sprite +y), its centre
    FLAT_C below the pivot."""
    c = RCut(110, 130, k)
    cx, top = 55, 16
    for ang, L_, w in ((-34, 30, 24), (-11, 36, 26), (11, 36, 26), (34, 30, 24)):
        RP._leaf(c, cx + 0.5 * ang, top + 72, ang, L_, w, RP.DUCK_DARK)
    c.polygon([(cx - 16, top), (cx + 16, top), (cx + 38, top + 40), (cx - 38, top + 40)], RP.DUCK_DARK)
    c.ellipse(cx, top, 16, 16, RP.DUCK_DARK)
    c.ellipse(cx, top + 52, 40, 36, RP.DUCK_DARK)
    c.ellipse(cx - 3, top + 46, 28, 25, RP.WING_LIGHT, sil=False)
    for f in (0.62, 0.95):
        c.arc(cx, top + 52 * f, 22, 9, 30, 150, 2.0, RP.WING_LINE)
    return c.finish(pivot=(cx, top))


WING_SHADE = (0.84, 0.78, 0.95)
FLAT_C = 52                       # blade centre, design units along the forearm from the elbow


class EpPip(RP.PipPuppet):
    """rig2_pip's Pip (unchanged) plus, for this episode: the flat wing (st["flat_r"] > 0.5), drawing one part
    alone (the head, for the face mask; the right wing, for its own light layer) or skipping the right wing."""

    def __init__(self, scale=0.9):
        super().__init__(scale)
        self.flat = flat_wing(self.k)
        self._skip = ()

    def _arm(self, base, cam, st, side):
        if side in self._skip:
            return
        if side == "r" and st.get("flat_r", 0.0) > 0.5:
            S, E, W, fa = self.arm_points(st, side)
            place(base, self.upper, cam.S(S), angle=st["arm_r"] + st["lean"], alpha=st["alpha"])
            place(base, self.flat, cam.S(E), angle=fa, alpha=st["alpha"])
            return
        super()._arm(base, cam, st, side)

    def blade_centre(self, st):
        S, E, W, fa = self.arm_points(st, "r")
        dx, dy = rot(0, FLAT_C * self.s, fa)
        return E[0] + dx, E[1] + dy

    def draw_parts(self, base, cam, st, skip=(), front=False):
        self._skip = skip
        try:
            self.draw(base, cam, st, front)
        finally:
            self._skip = ()

    def draw_head(self, base, cam, st):
        A = st["alpha"]
        p = max(0.0, st.get("puff", 0.0))
        hx, hy = self.head_pivot(st)
        ha = st["lean"] + st["tilt"]
        if p > 0.04:
            place(base, self.fluff, cam.S(self.head_centre(st)), angle=ha, scale=0.86 + 0.14 * min(1.0, p), alpha=A)
        look = (int(round(st["look_x"] / 2) * 2), int(round(st["look_y"] / 2) * 2))
        place(base, self.head(st["eyes"], st["mouth"], look, st["brows"], self._head_turn(st)), cam.S((hx, hy)),
              angle=ha, alpha=A)
        m = st.get("tuft", 0.0)
        m = m + (1.0 - m) * min(1.0, p)
        place(base, self.tuft(m), cam.S(self.tuft_root(st)), angle=ha + st.get("tuft_a", 0.0) * (1 - min(1.0, p)),
              sy=1 + 0.3 * min(1.0, p), alpha=A)

    def head_mask(self, st, cam, size, grow=6):
        m = Image.new("RGBA", size, (0, 0, 0, 0))
        self.draw_head(m, cam, st)
        return L.grow_mask(m.getchannel("A"), int(round(grow * cam.res)))


class EpPipPerf(RP.PipPerf):
    NUM = RP.PipPerf.NUM + ("flat_r",)

    def __init__(self, puppet, seed=0, **init):
        init.setdefault("flat_r", 0.0)
        super().__init__(puppet, seed, **init)

    def reach_blade(self, t0, t1, target, bend=None, ease="io"):
        """Put the flat wing's blade centre on `target` at t1 (IK on the paw point, corrected for the blade)."""
        st = self.state(t1)
        w = list(target)
        for _ in range(8):
            a, b = self.a.ik(st, "r", w, bend)
            st2 = dict(st, arm_r=a, elb_r=b)
            bc = self.a.blade_centre(st2)
            w[0] += target[0] - bc[0]
            w[1] += target[1] - bc[1]
        a, b = self.a.ik(st, "r", w, bend)
        return self.to(t0, t1, ease, arm_r=a, elb_r=b)


# ---------------------------------------------------------------- the cast (positions: plan + Lead L5)
SN = R.Perf2(R.Puppet("snip", 1.15), seed=1, x=400, y=FLOOR, turn=0.4, eyes="happy", mouth="smile", brows="calm")
CR = R.Perf2(RP.crinkle(1.2), seed=2, x=805, y=FLOOR, turn=0.6, eyes="closed", mouth="hum")
PIPA = EpPip(0.9)
PIP = EpPipPerf(PIPA, seed=3, x=1185, y=FLOOR, turn=-0.15, eyes="happy", mouth="smile_open")

# Lead L5 positions
SN_OPEN, CR_OPEN, PIP_OPEN = 400, 805, 1240       # opening: heads apart (plan 560 / 780); Pip in the
                                                  # right heart's beam, so the other two show on the wall
SN_BENCH, CR_BENCH, PIP_BENCH = 260, 640, 450     # at the bench (part 2): heads apart, Pip in front between
SN_BACK, PIP_BACK = 490, 690                      # shot 33 step back (L5 520/700; 490 keeps Snip's ear off the
                                                  # giant smile's left end)
CR_ASIDE = 1400                                   # shot 37 step aside
PIP_WING_X = 812                                  # shots 40a-40c

# ---- shots 1-4 (0-12.5 s): golden hour, the hearts, then gone
SN.reach(0.0, 0.01, "r", (480, 1310)).reach(0.0, 0.01, "l", (450, 1330))          # sketching (book: part 2)
SN.to(0.0, 0.01, "io", look_y=8, look_x=6)
CR.reach(0.0, 0.01, "r", (884, 1405))                                              # polishing the pumpkin
CR.to(2.0, 2.5, "io", elb_r=-40).to(7.5, 8.0, "io", elb_r=-20)
SN.face(7.0, eyes="normal", mouth="o", brows="up")
# Pip: mid-hop on frame 1 into the middle heart's beam; flaps; the heart on her tummy
PIP.hop(-0.35, 0.75, 1, 30).to(0.0, 0.75, "io", x=PIP_OPEN, turn=0.0)
PIP.to(0.8, 1.2, "io", look_y=10, look_x=0, head_dy=2).flap(1.0, 1.8)
PIP.face(0.9, eyes="sparkle", mouth="smile_open", brows="up").tuft(0.9, 1.3, "up")
PIP.face(2.4, eyes="happy", mouth="smile", brows="calm")
# 4.0 she covers it with her wing, held flat: now the heart is on her wing; giggle
PIP.set(4.05, flat_r=1.0)
PIP.to(4.0, 4.4, "io", look_y=12, look_x=-2, head_dy=2, tilt=-4)
PIP.reach_blade(4.05, 4.55, (L.HEART_XS[2] + 2, L.HEART_Y0 + L.HEART_DY_BODY + 2), bend=-1)
PIP.face(4.6, eyes="sparkle", mouth="smile_open", brows="up").tuft(4.6, 4.7, "flick")
PIP.to(4.7, 4.9, "io", tilt=4).to(5.1, 5.3, "io", tilt=-3).to(5.5, 5.7, "io", tilt=0)
PIP.set(6.05, flat_r=0.0).rest_wings(6.0, 6.3)

# ---- placeholder bridge (part 2 replaces it with acts 1-3): where everyone is when the glow starts
SN.set(90.0, x=SN_BENCH, turn=0.6, look_x=0, look_y=0, arm_l=-10, arm_r=10, elb_l=14, elb_r=-14)
SN.face(90.0, eyes="normal", mouth="smile", brows="calm")
CR.set(90.0, x=CR_BENCH, turn=0.5, elb_r=-14, arm_r=10)
CR.face(90.0, eyes="normal", mouth="smile", brows="calm")
PIP.set(90.0, x=PIP_BENCH, turn=0.3, look_x=0, look_y=0, head_dy=0, tilt=0)
PIP.face(90.0, eyes="normal", mouth="smile", brows="calm").tuft(90.0, 90.01, "normal")
# 102.5 they come closer (shot 29)
SN.walk(102.6, 104.0, 720)
CR.walk(102.5, 104.5, 1130).to(104.5, 104.8, "io", turn=-0.5)
PIP.walk(102.5, 104.2, 850)

# ---- shot 33 (117-123): Snip and Pip step back; Crinkle walks behind the pumpkin and turns it
SN.walk(117.0, 117.8, SN_BACK).face(117.8, eyes="normal", mouth="o", brows="up").ears(117.8, 118.1, "perk")
PIP.walk(117.0, 117.9, PIP_BACK).to(117.9, 118.2, "io", turn=0.35)
CR.walk(117.0, 118.0, 960).to(117.6, 118.0, "io", turn=0.0)
PAW_L, PAW_R = (862, 1402), (1058, 1402)
CR.reach(118.0, 118.3, "l", PAW_L).reach(118.0, 118.3, "r", PAW_R)
CR.face(118.0, eyes="normal", mouth="smile", brows="think").to(118.0, 118.3, "io", look_y=10, head_dy=4)
CR.to(118.3, 118.6, "io", sq=0.94, lean=3).face(118.3, eyes="closed", mouth="blow", brows="think")
CR.to(119.0, 119.3, "io", sq=1.0, lean=0).face(119.0, eyes="normal", mouth="o", brows="up")
for a, b in ((119.5, 120.6), (120.9, 122.0)):
    CR.to(a, a + 0.25, "io", sq=0.95, lean=-3).to(b - 0.25, b, "io", sq=1.0, lean=0)
    CR.face(a, eyes="normal", mouth="blow", brows="think").face(b + 0.15, eyes="happy", mouth="smile", brows="calm")
CR.to(122.0, 122.5, "io", look_y=12, head_dy=0)        # eyes down at the pumpkin; chin up, clear of the light
PIP.face(118.3, eyes="normal", mouth="o", brows="up").face(122.3, eyes="normal", mouth="smile", brows="calm")
# 125 the others see the smile on his tummy
SN.face(123.0, eyes="normal", mouth="smile", brows="calm")
SN.face(125.0, eyes="sparkle", mouth="smile_open", brows="up").reach(125.0, 125.4, "r", (630, 1270), "back")
SN.to(125.9, 126.2, "io", arm_r=10, elb_r=-14)
PIP.face(125.1, eyes="sparkle", mouth="smile_open", brows="up").flap(125.3, 126.6)
# 127 Crinkle looks up (?), then down: his tummy is smiling; laughs and wiggles (part 2 polishes)
CR.to(127.0, 127.3, "io", arm_l=-10, elb_l=14, arm_r=10, elb_r=-14)
CR.to(127.0, 127.3, "io", look_x=-10, look_y=-4, head_dy=0).face(127.0, eyes="normal", mouth="o", brows="up")
CR.to(127.9, 128.2, "io", look_x=0, look_y=14, head_dy=0, tilt=4).face(127.9, eyes="wide", mouth="O", brows="up")
CR.face(128.5, eyes="happy", mouth="smile_open", brows="up").to(128.5, 128.8, "io", head_dy=0, look_y=8, tilt=0)
for i in range(4):
    v = 10 if i % 2 == 0 else -10
    CR.to(128.6 + i * 0.35, 128.95 + i * 0.35, "io", x=960 + v, lean=0.6 * v)
CR.to(130.0, 130.4, "io", x=960, lean=0)
# ---- shot 37 (130-136): the step aside; the smile slides off him onto the wall
CR.walk(130.5, 132.0, CR_ASIDE).to(130.5, 131.0, "io", turn=-0.4, look_y=-12, look_x=-6, head_dy=0)
CR.face(130.6, eyes="wide", mouth="O", brows="up").face(132.6, eyes="sparkle", mouth="smile_open")
SN.to(130.4, 130.8, "io", look_y=-14, tilt=-4, hturn=0.25).face(130.6, eyes="wide", mouth="O", brows="up")
SN.ears(130.6, 130.9, "alarm").face(132.2, eyes="sparkle", mouth="smile_open").ears(132.2, 132.6, "happy")
PIP.to(130.6, 131.0, "io", look_y=-14, look_x=4, head_dy=0, turn=0.25).face(130.7, eyes="wide", mouth="o",
                                                                              brows="up")
PIP.face(132.3, eyes="sparkle", mouth="smile", brows="up").tuft(132.3, 132.6, "up")     # a smile by ~133 s
PIP.face(133.4, eyes="sparkle", mouth="smile_open", brows="up")
# ---- shots 40a-40c (141-148): Pip catches the smile on her flat wing
SN.to(141.0, 141.4, "io", look_y=6, look_x=10, tilt=0, hturn=0.0).face(141.0, eyes="happy", mouth="smile_open")
CR.to(141.0, 141.4, "io", look_x=-12, look_y=6, turn=-0.5).face(141.0, eyes="happy", mouth="smile_open")
PIP.walk(141.0, 142.2, PIP_WING_X).to(141.0, 141.5, "io", turn=-0.05, look_y=4, look_x=10)
PIP.set(142.4, flat_r=1.0)
WING_TIP = (942, 1326)                            # where the blade's centre goes (set by the clearance check)
PIP.to(142.4, 143.2, "io", lean=3, tilt=12, look_x=16, look_y=8)        # leans her head away from the light
PIP.reach_blade(142.4, 143.2, WING_TIP, bend=1)
PIP.face(143.3, eyes="happy", mouth="smile_open", brows="up").tuft(143.3, 143.4, "flick")


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


def wing_plane(st):
    """The wing's light: the 0.5x pattern centred on the flat blade (the beam is fixed in space, so it is set from
    where the wing ends up and stays there)."""
    return L.Plane(WING_TIP, L.WING.sx, blur=L.WING.blur, name="wing")


# ---------------------------------------------------------------- one frame of the world
def render_world(t, d=None, cam=None, bg=None, report=None):
    cam = cam or CAM
    sn, cr, ps = SN.state(t, d), CR.state(t, d), PIP.state(t, d)
    pk = pumpkin_state(t)
    glow = pk["lit"]
    facing = max(0.0, math.cos(math.radians(pk["rot"])))
    glow_ch = glow * (0.3 + 0.7 * facing)            # turned to the wall, little of its light comes our way
    f = bg.copy() if bg is not None else WORLD.background(t)
    size = f.size
    place(f, BOX_SPR if t > 43 else BOX_SPR3, cam.S(P.MARKER_BOX_AT))
    flat = ps["flat_r"] > 0.5
    lay_pip = L.Layer.of(size, lambda im: PIPA.draw_parts(im, cam, ps, skip=("r",) if flat else ()),
                         head=PIPA.head_mask(ps, cam, size))
    lay_wing = L.Layer.of(size, lambda im: PIPA._arm(im, cam, ps, "r")) if flat else None
    lay_sn = L.Layer.of(size, lambda im: SN.draw(im, t, cam, st=sn), head=L.head_mask(SN.a, sn, cam, size))
    lay_cr = L.Layer.of(size, lambda im: CR.draw(im, t, cam, st=cr), head=L.head_mask(CR.a, cr, cam, size))
    arms = ("l", "r") if 118.0 <= t < 127.3 else (("r",) if t < 12.5 else ())
    lay_arms = L.Layer.of(size, lambda im: [CR.a._arm(im, cam, cr, s) for s in arms]) if arms else None
    # light on the porch (before anyone stands in front of it)
    caught = L.sun_light(f, t, cam, WORLD.albedo, occluders=[lay_wing, lay_pip])
    L.floor_pool(f, cam, WORLD.albedo, glow, facing, side=math.sin(math.radians(pk["rot"])))
    pkk = proj_k(pk["rot"]) * glow
    occ = []
    if lay_cr is not None:
        occ.append((lay_cr.solid(), lay_cr.box, L.CHEST))
    if lay_wing is not None and pkk > 0:
        occ.append((lay_wing.solid(), lay_wing.box, wing_plane(ps)))
    Iw, bw = L.wall_light(f, cam, WORLD.albedo, pkk, occ)
    # characters: grade, warm glow, sun and beams (never on faces)
    lit = {}
    order = [("sn", lay_sn), ("cr", lay_cr), ("pip", lay_pip)]
    ck = ease_in_out(seg(pk["rot"], 140.0, 178.0)) * glow
    for name, lay in order:
        L.grade_layer(lay, t, glow_ch, L.GLOW_AT, cam)
        L.rail_shade(lay, t, cam)
        if name == "pip":
            lit["pip_heart"] = (L.heart_on_layer(lay, caught, t, cam), lay)
        if name == "cr" and pkk > 0:
            lit["cr"] = (L.beam_on_layer(lay, chest_plane(pk["rot"]), cam, ck), lay)
        if lay is not None:
            lay.paste(f)
    # the pumpkin (a prop: graded with the set), its own light, then paws / wing over it
    spr = PUMP.paper(rot=pk["rot"], strokes=pk["strokes"], holes=pk["holes"], lid=pk["lid"])
    lay_pk = L.Layer.of(size, lambda im: place(im, spr, cam.S(PK.BASE)))
    L.grade_layer(lay_pk, t, prop=True)
    lay_pk.paste(f)
    em = PUMP.emissive(rot=pk["rot"], lit=glow, holes=pk["holes"], lid=pk["lid"])
    if em is not None:
        place(f, em, cam.S(PK.BASE), shadow=False)
    if lay_arms is not None:
        L.grade_layer(lay_arms, t, glow_ch, L.GLOW_AT, cam)
        if pkk > 0:
            L.beam_on_layer(lay_arms, chest_plane(pk["rot"]), cam, ck)
        lay_arms.paste(f)
    if lay_wing is not None:
        L.grade_layer(lay_wing, t, glow_ch, L.GLOW_AT, cam)
        L.rail_shade(lay_wing, t, cam)
        if pkk > 0:
            L.shade_layer(lay_wing, WING_SHADE, pkk)    # Lead L3: the rest of the held-up wing in evening shade
        lit["wing_heart"] = (L.heart_on_layer(lay_wing, caught, t, cam), lay_wing)
        if pkk > 0:
            lit["wing"] = (L.beam_on_layer(lay_wing, wing_plane(ps), cam, pkk, bloom=3.0, own=(0.75, 0.25)),
                           lay_wing)                     # Lead L3: warm near-white on the yellow wing
        lay_wing.paste(f)
    L.halo(f, cam, glow * (0.25 + 0.75 * facing))     # turned to the wall: only a faint glow comes our way
    WORLD.front(f, t)
    L.rail_glow(f, t, cam)
    if report is not None:
        report.update(dict(sn=sn, cr=cr, pip=ps, lit=lit, wall=(Iw, bw), pk=pk))
    return f


# ---------------------------------------------------------------- cameras (plan shot list; L3: 40b at 2.8x)
SHOTS = [   # (start, end, centre at start, zoom at start, centre at end, zoom at end)
    (0.0, 4.0, (980, 1100), 1.0, None, None),
    (4.0, 6.0, (1190, 1300), 1.9, None, None),
    (6.0, 10.0, (980, 1100), 1.0, None, None),
    (10.0, 12.5, (1180, 1300), 1.9, None, None),
    (117.0, 123.0, (960, 1180), 1.15, None, None),
    (123.0, 125.0, (960, 1280), 1.9, None, None),
    (125.0, 127.0, (760, 1200), 1.5, None, None),
    (127.0, 130.0, (960, 1130), 1.6, None, None),
    (130.0, 136.0, (960, 1080), 1.15, (960, 1080), 1.0),
    (136.0, 138.5, (720, 1210), 1.9, None, None),
    (138.5, 141.0, (960, 1150), 1.2, None, None),
    (141.0, 143.5, (900, 1150), 1.4, None, None),
    (143.5, 145.0, (900, 1280), 2.8, None, None),
    (145.0, 148.0, (960, 1100), 1.15, None, None),
]


def camera(t):
    for t0, t1, c0, z0, c1, z1 in SHOTS:
        if t0 <= t < t1:
            if c1 is None:
                return c0, z0
            if t0 == 130.0:                           # shot 37: pull back 1.15 -> 1.0 during the step aside
                u = ease_in_out(seg(t, 130.4, 131.6))
            else:
                u = ease_in_out(seg(t, t0, t1))
            return (c0[0] + (c1[0] - c0[0]) * u, c0[1] + (c1[1] - c0[1]) * u), z0 + (z1 - z0) * u
    return (960, 1100), 1.0


def frame(t, report=None, centre=None, z=None):
    d = K.drawing_of(t)
    f = render_world(t, d, report=report)
    c, zz = camera(t)
    c, zz = centre or c, z or zz
    if zz > 1.0001:
        f = K.zoom(f, zz, CAM.S(c))
    return f.resize((1920, 1080), Image.LANCZOS).convert("RGB")


# ---------------------------------------------------------------- numeric checks (carry-forward 2; rules card)
def _edge_pts(mask, box, cam, thresh, step=2):
    """World points on the edge of (mask >= thresh), mask over box (frame pixels)."""
    m = mask >= thresh
    if not m.any():
        return np.zeros((0, 2), np.float32)
    e = m.copy()
    e[1:-1, 1:-1] = m[1:-1, 1:-1] & ~(m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:])
    ys, xs = np.nonzero(e)
    pts = np.stack([(xs + box[0]) / cam.res + cam.ox, (ys + box[1]) / cam.res + cam.oy], 1)
    return pts[::step]


def _min_d(a, b):
    if len(a) == 0 or len(b) == 0:
        return float("inf")
    best = float("inf")
    for i in range(0, len(a), 2000):
        d = ((a[i:i + 2000, None, :] - b[None, :, :]) ** 2).sum(-1)
        best = min(best, float(d.min()))
    return math.sqrt(best)


def _head_pts(draw_head, cam, size):
    m = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_head(m)
    a = np.asarray(m.getchannel("A")).astype(np.float32) / 255
    bb = m.getchannel("A").getbbox()
    if bb is None:
        return np.zeros((0, 2), np.float32)
    return _edge_pts(a[bb[1]:bb[3], bb[0]:bb[2]], bb, cam, 0.5, step=3)


def _ellipse(c, rx, ry, n=48):
    return np.array([(c[0] + rx * math.cos(2 * math.pi * i / n), c[1] + ry * math.sin(2 * math.pi * i / n))
                     for i in range(n)], np.float32)


def checks(t, rep):
    out = []
    size = (int(CAM.w * CAM.res), int(CAM.h * CAM.res))
    lit = rep["lit"]
    ps, cr = rep["pip"], rep["cr"]

    def pip_head(im):
        PIPA.draw_head(im, CAM, ps)
    pip_face = _head_pts(pip_head, CAM, size)
    beak = _ellipse(PIPA.beak_point(ps), 30 * PIPA.s, 16 * PIPA.s)
    for key, what in (("pip_heart", "heart on Pip's body"), ("wing_heart", "heart on Pip's wing"),
                      ("wing", "smile on Pip's wing")):
        if key in lit and lit[key][0] is not None:
            I, lay = lit[key]
            pts = _edge_pts(I, lay.box, CAM, 0.02)
            if len(pts):
                out.append(f"{t:.1f}s {what}: light edge to Pip's head outline {_min_d(pts, pip_face):.0f}, "
                           f"to beak {_min_d(pts, beak):.0f} units")
    if "cr" in lit and lit["cr"][0] is not None:
        I, lay = lit["cr"]
        pts = _edge_pts(I, lay.box, CAM, 0.02)

        def cr_head(im):
            m = L.head_mask(CR.a, cr, CAM, size, grow=0)
            im.paste(Image.new("RGBA", size, (0, 0, 0, 255)), (0, 0), m)
        cr_face = _head_pts(cr_head, CAM, size)
        chin = CR.a.face_point(cr, (0, -18))
        out.append(f"{t:.1f}s smile on Crinkle: light edge to his head outline {_min_d(pts, cr_face):.0f}, "
                   f"to chin {_min_d(pts, np.array([chin], np.float32)):.0f} units; lowest lit y "
                   f"{pts[:, 1].max():.0f}, stem top y {PK.BASE[1] - 189.5:.0f}")
    return out


# ---------------------------------------------------------------- the Lead's check sheet
CHECK = [
    (2.0, None, None, "2 s golden: the hearts on the wall (wide)"),
    (4.8, None, None, "4.8 s the heart on Pip's wing (close 1.9)"),
    (123.5, (960, 1280), 1.9, "123.5 s the smile on Crinkle's tummy (close 1.9)"),
    (133.0, None, None, "133 s the giant face (wide)"),
    (143.5, None, None, "143.5 s the smile on Pip's wing (close 2.8)"),
]


def contact_sheet(items, path, w=780):
    import paperlib
    h = int(w * 1080 / 1920)
    cols = 2
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
    args = sys.argv[1:]
    if args[:1] == ["--still"] and len(args) == 2:
        tt = float(args[1])
        rep = {}
        cand = [c for c in CHECK if abs(c[0] - tt) < 1e-6]
        img = frame(tt, rep, *(cand[0][1:3] if cand else (None, None)))
        out = os.path.join(ROOT, "build", f"ep11_{tt:.2f}.png")
        img.save(out)
        print("wrote", out)
        print("\n".join(checks(tt, rep)))
    elif args == ["--check"]:
        items, lines = [], []
        for tt, c, z, label in CHECK:
            rep = {}
            img = frame(tt, rep, c, z)
            img.save(os.path.join(ROOT, "build", f"ep11_check_{tt:.2f}.png"))
            items.append((img, label))
            lines += checks(tt, rep)
            print("rendered", tt, flush=True)
        contact_sheet(items, os.path.join(ROOT, "reviews", "ep11_check_L.png"))
        print("\n".join(lines))
    else:
        sys.exit("usage: ep11_friendly_glow.py --check | --still T   (part 2 adds --keys, --cuts, the render)")
