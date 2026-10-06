"""Episode 11 "Pip and the Friendly Glow" (160 s, landscape 1920x1080 at 30 fps, rig v2, 2x render).

One 1920x1920 porch world (props_porch) filmed by cameras; light from ep11_light; the pumpkin from props_pumpkin;
small props from props_glow; the grown-up's arm from props_hand2; Snip and Crinkle from rig2, Pip from rig2_pip.
Plan: reviews/ep11_plan.md (shot list section 4, with the Lead's L1-L5 and check-sheet decisions).

Run:  python3 episodes/ep11_friendly_glow.py --keys      (key sheet -> reviews/ep11_friendly_glow_keys.png)
      python3 episodes/ep11_friendly_glow.py --cuts      (cut times for check_video)
      python3 episodes/ep11_friendly_glow.py --still T   (one frame through the shot camera -> build/)
      python3 episodes/ep11_friendly_glow.py --check     (the Lead's L-check sheet -> reviews/ep11_check_L.png)
      EP11_RES=3 python3 episodes/ep11_friendly_glow.py --hires40b   (shot 40b at 3x -> build/ep11_40b/)
      python3 episodes/ep11_friendly_glow.py --render    (audio + video -> output/ep11_friendly_glow.mp4)
Any other flag is refused (never "render everything" by accident).

    render_world(t, d, cam, bg=None, report=None)  # the world at time t, drawing d, through a K.Cam (RGBA)
    make_buses()                                   # (music, sfx) Mix buses (the Shorts cut their effects from them)
    render_frame(t, view)                          # one finished landscape frame (for acting.render_video)
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

import hires  # noqa: E402

hires.set_res(float(os.environ.get("EP11_RES", "2")))     # 3 only for the separate shot-40b pass

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import acting as K  # noqa: E402
import audio as A  # noqa: E402
import ep11_light as L  # noqa: E402
import music_extra as MX  # noqa: E402
import props_glow as G  # noqa: E402
import props_hand2 as H  # noqa: E402
import props_porch as P  # noqa: E402
import props_pumpkin as PK  # noqa: E402
import props_splash as S  # noqa: E402
import rig2 as R  # noqa: E402
import rig2_pip as RP  # noqa: E402
from hires import RCut  # noqa: E402
from paperlib import ease_in_out, ease_out_back, lerp, place, rot, seg  # noqa: E402

RES = hires.RES
DUR = 160.0
FLOOR = P.FLOOR_Y
CAM = K.Cam("land", P.WORLD_W, P.WORLD_H, P.LAND_Y0, P.VERT_X0, res=RES)
WORLD = P.Porch(CAM)
PUMP = PK.Pumpkin()
BOXES = [P.marker_box(n) for n in range(4)]
BOOK = {"back": G.sketchbook("back"), "plan": G.sketchbook("plan")}
BOOK_TUCK = G.book_tucked()
BOOK_SCALE = 1.35                     # the sketchbook held up (the plan must read in the close-up)
CRAYON = G.crayon()
CLOTH, CLOTH_CORNER = G.cloth(), G.cloth_corner()
TEA = {False: G.tea_light(False), True: G.tea_light(True)}
TEA_SCALE = 1.4
CHIME = G.chime()
LEAVES = [G.leaf(i) for i in range(3)]
SPARK = S.sparkle()
SPARK_S = S.sparkle((255, 240, 160))
INK_BLACK, INK_RED = (40, 36, 44), (224, 46, 66)
MK = {("sn", "black"): RP.marker_sprite(ink=INK_BLACK, scale=1.15),
      ("cr", "black"): RP.marker_sprite(ink=INK_BLACK, scale=1.2),
      ("pip", "red"): RP.marker_sprite(ink=INK_RED, scale=0.9)}
ARM = H.Arm(upper=720, fore=760)
SLEEVE2 = H.sleeve_end()


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
            S_, E, W, fa = self.arm_points(st, side)
            place(base, self.upper, cam.S(S_), angle=st["arm_r"] + st["lean"], alpha=st["alpha"])
            place(base, self.flat, cam.S(E), angle=fa, alpha=st["alpha"])
            return
        super()._arm(base, cam, st, side)

    def blade_centre(self, st):
        S_, E, W, fa = self.arm_points(st, "r")
        dx, dy = rot(0, FLAT_C * self.s, fa)
        return E[0] + dx, E[1] + dy

    def draw_parts(self, base, cam, st, skip=(), front=False):
        self._skip = skip
        try:
            self.draw(base, cam, st, front)
        finally:
            self._skip = ()

    def draw_head(self, base, cam, st):
        A_ = st["alpha"]
        p = max(0.0, st.get("puff", 0.0))
        hx, hy = self.head_pivot(st)
        ha = st["lean"] + st["tilt"]
        if p > 0.04:
            place(base, self.fluff, cam.S(self.head_centre(st)), angle=ha, scale=0.86 + 0.14 * min(1.0, p),
                  alpha=A_)
        look = (int(round(st["look_x"] / 2) * 2), int(round(st["look_y"] / 2) * 2))
        place(base, self.head(st["eyes"], st["mouth"], look, st["brows"], self._head_turn(st)), cam.S((hx, hy)),
              angle=ha, alpha=A_)
        m = st.get("tuft", 0.0)
        m = m + (1.0 - m) * min(1.0, p)
        place(base, self.tuft(m), cam.S(self.tuft_root(st)), angle=ha + st.get("tuft_a", 0.0) * (1 - min(1.0, p)),
              sy=1 + 0.3 * min(1.0, p), alpha=A_)

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
            bc = self.a.blade_centre(dict(st, arm_r=a, elb_r=b))
            w[0] += target[0] - bc[0]
            w[1] += target[1] - bc[1]
        a, b = self.a.ik(st, "r", w, bend)
        return self.to(t0, t1, ease, arm_r=a, elb_r=b)


# ---------------------------------------------------------------- the cast (positions: plan + Lead L5)
SN_OPEN, CR_OPEN, PIP_OPEN = 400, 805, 1240       # opening: heads apart; Pip in the right heart's beam
SN_BENCH, PIP_BENCH, CR_BENCH = 110, 310, 500     # at the bench (85-98.4): heads apart, Pip in front between,
                                                  # everyone well back from the pumpkin
SN_BACK, PIP_BACK = 490, 690                      # shot 33 step back
CR_ASIDE = 1400                                   # shot 37 step aside
PIP_WING_X = 812                                  # shots 40a-40c
SN_EYES, CR_SMILE, PIP_NOSE = 790, 1080, 845      # where each one draws on the pumpkin
CR_HELP = 1000                                    # after the peekaboo, Crinkle stands at the pumpkin's back right
PIP_HIDE = 790                                    # hiding behind Crinkle (805)

SN = R.Perf2(R.Puppet("snip", 1.15), seed=1, x=SN_OPEN, y=FLOOR, turn=0.4, eyes="happy", mouth="smile",
             brows="calm")
CR = R.Perf2(RP.crinkle(1.2), seed=2, x=CR_OPEN, y=FLOOR, turn=0.6, eyes="closed", mouth="hum")
PIPA = EpPip(0.9)
PIP = EpPipPerf(PIPA, seed=3, x=1100, y=FLOOR, turn=-0.15, eyes="happy", mouth="smile_open")


# ---------------------------------------------------------------- tool tracks (a marker's tip; where it points)
class Track:
    """Piecewise-linear tip track: [(t, (x, y)), ...] spans; tells where a tool tip should point."""

    def __init__(self):
        self.spans = []

    def add(self, keys):
        keys = sorted(keys)
        for span in self.spans:
            if abs(span[-1][0] - keys[0][0]) < 1e-6:
                span.extend(keys[1:])
                return
        self.spans.append(keys)

    def info(self, t):
        for keys in self.spans:
            if keys[0][0] <= t <= keys[-1][0]:
                for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
                    if t0 <= t <= t1:
                        k = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                        return (lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k)), keys[0][0], keys[-1][0]
                return keys[-1][1], keys[0][0], keys[-1][0]
        return None

    def last_end(self, t):
        ends = [(keys[-1][0], keys[-1][1]) for keys in self.spans if keys[-1][0] < t]
        return max(ends) if ends else None


TRACK = {"sn": Track(), "cr": Track(), "pip": Track()}
MK_SCALE = {"sn": 1.15, "cr": 1.2, "pip": 0.9}


def _tip_world(name, f):
    x, y = PK.stroke_tip(name, f)
    return PK.BASE[0] + x, PK.BASE[1] + y


def marker_stroke(who, perf, side, name, t0, t1, u, n=12, lead=0.4, bend=None):
    """Draw stroke `name` on the pumpkin from t0 to t1 (as pumpkin_state reveals it): the paw follows so the marker
    tip (pointing along u) stays on the line; the tip track lets the marker aim at it."""
    L_ = RP.MARKER_TIP * MK_SCALE[who]
    pts = [_tip_world(name, i / (n - 1)) for i in range(n)]
    grip = [(p[0] - L_ * u[0], p[1] - L_ * u[1]) for p in pts]
    perf.reach(t0 - lead, t0, side, grip[0], "io", bend)
    keys = [(t0 - lead, pts[0]), (t0, pts[0])]
    for i in range(1, n):
        ta, tb = t0 + (t1 - t0) * (i - 1) / (n - 1), t0 + (t1 - t0) * i / (n - 1)
        perf.reach(ta, tb, side, grip[i], "lin", bend)
        keys.append((tb, pts[i]))
    TRACK[who].add(keys)


def _blend_angle(a, b, k):
    d = (b - a + 180) % 360 - 180
    return a + d * k


def tool_angle(perf, side, st, track, t, ease=0.3):
    """The tool follows the forearm, except while drawing (it aims at the tip track); it eases between the two."""
    W, fa = perf.paw(t, side, st)
    info = track.info(t)
    if info:
        tip, t0, _ = info
        aim = math.degrees(math.atan2(tip[0] - W[0], tip[1] - W[1]))
        return W, _blend_angle(fa, aim, ease_in_out(seg(t, t0, t0 + ease)))
    end = track.last_end(t)
    if end and t - end[0] < ease:
        tip = end[1]
        aim = math.degrees(math.atan2(tip[0] - W[0], tip[1] - W[1]))
        return W, _blend_angle(aim, fa, ease_in_out(seg(t, end[0], end[0] + ease)))
    return W, fa


# ---------------------------------------------------------------- small acting helpers
def circle_rub(perf, side, c, r, t0, t1, period=0.8, step=0.2):
    """Polishing: the paw goes round a small circle."""
    t = t0
    while t < t1 - 1e-6:
        a = 2 * math.pi * (t + step - t0) / period
        perf.reach(t, min(t1, t + step), side, (c[0] + r * math.cos(a), c[1] + 0.7 * r * math.sin(a)), "lin")
        t += step


def scribble(perf, side, c, t0, t1, rx=9, ry=5, step=0.13):
    """Fast little sketching strokes round a point."""
    t, i = t0, 0
    while t < t1 - 1e-6:
        dx = rx if i % 2 == 0 else -rx
        dy = ry * ((i // 2) % 3 - 1)
        perf.reach(t, min(t1, t + step), side, (c[0] + dx, c[1] + dy), "io")
        t += step
        i += 1


def clap(perf, t0, n, at, dt=0.3):
    for i in range(n):
        a = t0 + i * dt
        perf.reach(a, a + dt * 0.5, "l", (at[0] - 4, at[1]), "io").reach(a, a + dt * 0.5, "r", (at[0] + 4, at[1]), "io")
        perf.reach(a + dt * 0.5, a + dt, "l", (at[0] - 34, at[1] + 6), "io")
        perf.reach(a + dt * 0.5, a + dt, "r", (at[0] + 34, at[1] + 6), "io")


def dance2(perf, t0, t1, beats=4, amp=8.0, hop_h=14):
    """Crinkle's happy wiggle-dance: paws up, lean side to side on each beat, little bounces."""
    perf.to(t0, t0 + 0.25, "io", arm_l=-150, elb_l=20, arm_r=150, elb_r=-20)
    T = (t1 - t0) / beats
    for i in range(beats):
        v = amp if i % 2 == 0 else -amp
        perf.to(t0 + i * T, t0 + (i + 1) * T, "io", lean=v, tilt=0.6 * v)
    perf.to(t1 - 0.05, t1 + 0.3, "io", lean=0, tilt=0, arm_l=-10, elb_l=14, arm_r=10, elb_r=-14)
    perf.hop(t0, t1, beats, hop_h)


def rest_arms(perf, t0, t1):
    return perf.to(t0, t1, "io", arm_l=-10, elb_l=14, arm_r=10, elb_r=-14)


IDEAS = []                                 # (t, perf) a sparkle pops above the head
SPARKLES = []                              # (t, world point, size)


# ================================================================ ACT 1 (0-32): the hearts go, Pip is unsure
# ---- shot 1 (0-4): golden sunset; Pip hops into the right heart's beam; Snip sketches; Crinkle polishes
SN.reach(0.0, 0.01, "l", (430, 1325)).to(0.0, 0.01, "io", look_y=6, look_x=4)
scribble(SN, "r", (468, 1206), 0.0, 4.0)
CR.reach(0.0, 0.01, "r", (884, 1405))
circle_rub(CR, "r", (880, 1400), 14, 0.01, 15.6)
PIP.hop(-0.4, 0.45, 1, 30).to(0.0, 0.45, "io", x=1176, turn=0.0)
PIP.walk(0.55, 1.15, PIP_OPEN)                    # steps into the right heart's beam
PIP.to(0.8, 1.2, "io", look_y=10, look_x=0, head_dy=2).flap(1.0, 1.8)
PIP.face(0.9, eyes="sparkle", mouth="smile_open", brows="up").tuft(0.9, 1.3, "up")
PIP.face(2.4, eyes="happy", mouth="smile", brows="calm")
# ---- shot 2 (4-6): she covers it with her wing, held flat: now the heart is on her wing; giggle
PIP.set(4.05, flat_r=1.0)
PIP.to(4.0, 4.4, "io", look_y=12, look_x=-2, head_dy=2, tilt=-4)
PIP.reach_blade(4.05, 4.55, (L.HEART_XS[2] + 2, L.HEART_Y0 + L.HEART_DY_BODY + 2), bend=-1)
PIP.face(4.6, eyes="sparkle", mouth="smile_open", brows="up").tuft(4.6, 4.7, "flick")
PIP.to(4.7, 4.9, "io", tilt=4).to(5.1, 5.3, "io", tilt=-3).to(5.5, 5.7, "io", tilt=0)
scribble(SN, "r", (468, 1206), 4.0, 6.0, step=0.18)
# ---- shot 3 (6-10): the sun sinks; the hearts rise, turn pink, fade (gone 9.4); Pip hops to keep hers
SN.face(7.0, eyes="normal", mouth="o", brows="up").to(7.0, 7.4, "io", look_x=10, look_y=-6)
PIP.face(6.6, eyes="wide", mouth="o", brows="up").to(6.6, 7.0, "io", look_y=-10, look_x=-8, head_dy=0, tilt=0)
PIP.to(7.0, 7.4, "io", sq=1.06).to(7.8, 8.1, "io", sq=1.03).to(8.1, 8.4, "io", sq=1.07)   # tiptoe after it
PIP.to(8.6, 9.0, "io", sq=1.0)
PIP.face(8.4, eyes="normal", mouth="flat", brows="worry").to(8.4, 8.8, "io", look_y=12, look_x=-2, head_dy=3)
# ---- shot 4 (10-12.5): empty wing; tuft droops, sad beak; she looks round the dim porch; a first star
PIP.to(9.6, 10.2, "io", tilt=0)
PIP.reach_blade(9.7, 10.3, (L.HEART_XS[2] + 30, 1352), bend=-1)        # wing out: she looks under it
PIP.face(10.3, eyes="normal", mouth="sad", brows="sad").tuft(10.4, 11.0, "droop")
PIP.to(10.9, 11.4, "io", hturn=-0.5, look_x=-12, look_y=-6, head_dy=0).to(11.6, 12.1, "io", hturn=0.4, look_x=10,
                                                                         look_y=-8)
PIP.set(11.0, flat_r=0.0).rest_wings(11.0, 11.4)
SN.face(10.0, eyes="normal", mouth="smile", brows="calm").to(10.0, 10.4, "io", look_x=4, look_y=6)
scribble(SN, "r", (468, 1206), 10.0, 14.9, step=0.2)
# ================================================================ shot 5 (12.5-15): a breeze; Pip puffs, hides
BREEZE = 12.6
PIP.to(12.4, 12.7, "io", hturn=0.0, look_x=4, look_y=0)
PIP.puff_up(12.8, hold=0.35, out=0.6)
PIP.face(13.9, eyes="wide", mouth="o", brows="worry")
PIP.run(13.9, 14.8, PIP_HIDE).to(13.9, 14.1, "io", turn=-0.5)
PIP.to(14.8, 15.1, "io", turn=0.0, look_x=0, look_y=0).tuft(14.8, 15.2, "low")
# ================================================================ shot 6 (15-22): "behind you!" peekaboo
SN.face(15.3, eyes="wide", mouth="o", brows="up").ears(15.3, 15.6, "curious")
SN.reach(15.6, 16.0, "r", (690, 1250), "back")                          # points at Crinkle's back
SN.face(16.0, eyes="normal", mouth="o", brows="up").ears(16.1, 16.4, "perk")
CR.reach(15.6, 15.9, "r", CR.a.anchor(CR.state(15.9))(70, -230))         # cloth into the scarf
CR.to(15.9, 16.2, "io", arm_r=10, elb_r=-14)
CR.face(16.3, eyes="normal", mouth="o", brows="up")
CR.to(16.6, 17.0, "io", hturn=0.9, look_x=12)                          # over his left shoulder (our right)
PIP.to(17.0, 17.4, "io", x=596, lean=-6, turn=-0.3).face(17.0, eyes="normal", mouth="smile", brows="up")
PIP.to(17.9, 18.2, "io", x=PIP_HIDE, lean=0, turn=0.0)
CR.to(18.0, 18.4, "io", hturn=-0.9, look_x=-12)                        # ... and the other way
PIP.to(18.5, 18.9, "io", x=1012, lean=6, turn=0.3)
PIP.to(19.2, 19.5, "io", x=PIP_HIDE, lean=0, turn=0.0)
CR.to(19.3, 19.7, "io", hturn=0.9, look_x=12)
SN.face(17.5, eyes="happy", mouth="smile_open", brows="calm")
SN.reach(17.4, 17.7, "r", SN.a.face_point(SN.state(17.7), (12, -52)))  # giggles behind a paw
SN.arms_front.append((17.4, 20.5))
SN.reach(20.3, 20.6, "r", (520, 1330)).face(20.4, eyes="normal", mouth="smile", brows="calm")
SN.ears(20.4, 20.8, "perk")
CR.to(20.2, 20.6, "io", hturn=0.0, look_x=0)
CR.face(20.4, eyes="normal", mouth="smile", brows="up")
CR.walk(20.7, 21.4, CR_HELP).to(20.7, 21.0, "io", turn=-0.3)            # steps aside: there she is
PIP.walk(21.1, 21.8, 770).face(21.5, eyes="wide", mouth="flat", brows="worry")
PIP.to(21.8, 22.1, "io", look_y=-10, look_x=8, head_dy=4, tilt=6).face(22.0, eyes="normal", mouth="flat",
                                                                       brows="sorry")
CR.face(21.6, eyes="normal", mouth="smile", brows="calm").to(21.5, 21.9, "io", look_x=-10, look_y=8)
# ================================================================ shot 7 (22-26): Crinkle crouches to her level
CR.to(22.2, 22.8, "io", sq=0.86, lean=-6, head_dy=10)
PIP.point(22.9, 23.3, "l", (900, 760))                                   # the dark wall under the roof
PIP.to(22.9, 23.3, "io", look_y=-16, look_x=0, tilt=0, turn=0.0)
PIP.unpoint(23.7, 23.9, "l").hug_self(23.9, 24.3).face(23.9, eyes="worried", mouth="wobble", brows="sad")
CR.to(23.2, 23.6, "io", look_y=-14, look_x=-8).face(23.3, eyes="normal", mouth="flat", brows="worry")
CR.to(23.9, 24.2, "io", look_y=8, look_x=-10).face(24.3, eyes="happy", mouth="smile", brows="calm")
TUFT_PAT = 25.0
_ps = PIP.state(TUFT_PAT)
CR.reach(24.5, TUFT_PAT, "l", PIPA.tuft_root(_ps))
PIP.tuft(TUFT_PAT, TUFT_PAT + 0.1, "low").tuft(TUFT_PAT + 0.25, TUFT_PAT + 0.55, "up").tuft(TUFT_PAT + 0.3, 0, "flick")
PIP.face(TUFT_PAT + 0.3, eyes="happy", mouth="smile", brows="calm").rest_wings(25.2, 25.6)
PIP.to(25.2, 25.6, "io", sq=1.0, head_dy=0, look_y=-6, look_x=10)
CR.reach(25.4, 25.8, "l", (870, 1320)).to(25.5, 26.0, "io", sq=1.0, lean=0, head_dy=0)
# ================================================================ shot 8 (26-30): Snip's idea
SN.ears(26.2, 26.7, "sad").face(26.2, eyes="normal", mouth="frown", brows="sad").to(26.2, 26.5, "io", look_x=12,
                                                                                    look_y=6)
SN.to(27.0, 27.3, "io", look_x=14, look_y=10, hturn=0.3)
T_IDEA_SN = 27.8
SN.ears(T_IDEA_SN, T_IDEA_SN + 0.3, "perk").face(T_IDEA_SN, eyes="sparkle", mouth="smile_open", brows="up")
IDEAS.append((T_IDEA_SN, SN))
SN.to(28.2, 28.5, "io", hturn=0.0, look_x=2, look_y=8)
scribble(SN, "r", (468, 1206), 28.4, 29.9, rx=12, ry=6, step=0.1)
# ================================================================ shot 9 (30-32): the plan
T_FLIP = 30.2
SN.reach(29.9, 30.2, "r", (500, 1330)).reach(30.0, 30.4, "l", (460, 1262))
SN.face(30.6, eyes="happy", mouth="smile_open", brows="up")
# ================================================================ shot 10 (32-39): Pip's turn; the dance
PIP.to(32.3, 32.6, "io", tilt=-10, look_x=-14, look_y=0).face(32.3, eyes="normal", mouth="o", brows="up")
PIP.face(32.9, eyes="sparkle", mouth="smile_open", brows="up").to(32.9, 33.2, "io", tilt=0).tuft(32.9, 33.1, "up")
CR.to(32.2, 32.5, "io", hturn=-0.6, look_x=-14, look_y=4).face(32.2, eyes="normal", mouth="o", brows="up")
CR.to(32.7, 32.9, "io", hturn=0.0, look_x=-6, look_y=12)
CR.reach(32.9, 33.15, "l", (980, 1338)).reach(33.25, 33.45, "l", (970, 1352))   # pats it (tap)
CR.reach(33.45, 33.65, "l", (930, 1320)).face(33.3, eyes="happy", mouth="smile_open", brows="up")
CR.to(33.5, 33.62, "io", head_dy=5).to(33.62, 33.8, "io", head_dy=0)            # nod
dance2(CR, 33.8, 35.8)
PIP.dance(34.3, 36.3, beats=4)
SN.face(34.0, eyes="happy", mouth="smile_open", brows="up")
SN.hop(36.4, 36.85, 1, 26).hop(37.0, 37.45, 1, 22).ears(36.4, 36.8, "happy")
PIP.walk(37.3, 38.6, 560).to(38.6, 38.9, "io", turn=-0.3)
SN.reach(38.4, 38.8, "l", (340, 1350)).reach(38.4, 38.8, "r", (470, 1350))   # tucks the book under his arm
T_TUCK = 38.7
# ================================================================ ACT 2 (39-82): drawing the face together
# ---- shot 11 (39-43): markers from the box; red for Pip, black for Crinkle
SN.to(39.0, 39.3, "io", turn=0.6, look_x=10, look_y=10)
SN.reach(39.3, 39.7, "r", (520, 1352)).face(39.4, eyes="normal", mouth="smile", brows="calm")
T_MARKERS = 39.8
SN.reach(39.9, 40.3, "r", (540, 1290))
SN.to(40.3, 40.6, "io", turn=0.3, look_x=12, look_y=6)
SN.reach(40.5, 40.9, "r", (520, 1300))
PIP.reach(40.5, 40.9, "l", (528, 1312)).face(40.9, eyes="sparkle", mouth="smile_open", brows="up")
T_GIVE_PIP = 40.95
PIP.flap(41.1, 41.6)
PIP.to(41.1, 41.4, "io", arm_l=-40, elb_l=30)                              # holds it up proudly
SN.walk(41.3, 42.1, 690).to(41.3, 41.5, "io", turn=0.4)
CR.reach(42.1, 42.5, "l", (842, 1292)).face(42.1, eyes="happy", mouth="smile_open", brows="up")
SN.reach(42.1, 42.5, "r", (832, 1296))
T_GIVE_CR = 42.55
SN.reach(42.7, 43.0, "r", (760, 1330))
CR.reach(42.7, 43.0, "l", (880, 1320))
# ---- shot 12 (43-45): to the pumpkin
SN.walk(43.0, 43.7, SN_EYES).to(43.7, 43.9, "io", turn=0.4, look_x=12, look_y=12)
CR.walk(43.0, 44.0, CR_SMILE).to(44.0, 44.2, "io", turn=-0.3, look_x=-10, look_y=10)
PIP.walk(43.1, 43.8, 580).to(43.8, 44.0, "io", turn=0.3, look_x=10, look_y=4)
# ---- shot 13 (45-49): Snip draws the eyes
U_SN = (0.36, 0.93)
marker_stroke("sn", SN, "r", "eye_l", 45.2, 46.0, U_SN, n=14)
SN.reach(46.1, 46.6, "r", (930, 1310))
marker_stroke("sn", SN, "r", "eye_r", 47.0, 47.8, U_SN, n=14)
SN.reach(47.9, 48.4, "r", (900, 1320))
SN.face(46.1, eyes="happy", mouth="smile", brows="calm").face(47.0, eyes="normal", mouth="smile", brows="think")
SN.face(47.9, eyes="sparkle", mouth="smile_open", brows="up")
# ---- shot 14 (49-53): steps back under the chime, joy hop, ears bonk it
SN.walk(48.6, 49.5, 690, steps=2).to(49.5, 49.8, "io", turn=0.5, look_x=10, look_y=10)
SN.reach(49.4, 49.8, "r", (760, 1330))
T_BONK = 50.11                                      # the right ear tip reaches the chime
SN.hop(50.0, 50.45, 1, 35)
SN.wiggle(T_BONK, "ear_l", 16, 7, 5).wiggle(T_BONK, "ear_r", -16, 7, 5).ears(50.5, 50.8, "happy")
SN.face(50.2, eyes="wide", mouth="o", brows="up").face(50.7, eyes="happy", mouth="smile_open", brows="up")
SN.to(50.5, 50.8, "io", look_y=-14, look_x=0).to(51.5, 51.8, "io", look_y=6, look_x=-10)
PIP.puff_up(50.4, hold=0.3, out=0.6)
PIP.face(51.2, eyes="happy", mouth="smile_open", brows="calm").to(51.2, 51.5, "io", look_y=-8, look_x=6)
SN.face(51.4, eyes="happy", mouth="smile_open", brows="calm")
# ---- shot 15 (53-55): Crinkle crouches, marker ready, tongue out
CR.to(53.0, 53.9, "io", sq=0.84, lean=-8, head_dy=8).face(53.4, eyes="normal", mouth="yum_l", brows="think")
CR.to(53.4, 53.8, "io", look_x=-10, look_y=14)
# ---- shot 16 (55-60): the big smile, slowly; his tongue follows the marker
U_CR = (-0.3, 0.95)
CR.reach(55.0, 55.6, "l", (920, 1385))
marker_stroke("cr", CR, "l", "smile", 56.5, 59.5, U_CR, n=40, lead=0.6)
for tt, m in ((56.5, "yum_l"), (57.2, "yum_c"), (57.8, "yum"), (58.4, "yum_c"), (58.9, "yum_l"), (59.4, "yum_c")):
    CR.face(tt, mouth=m)
CR.face(59.7, eyes="happy", mouth="smile_open", brows="up")
CR.reach(59.7, 60.2, "l", (960, 1330)).to(60.2, 60.9, "io", sq=1.0, lean=0, head_dy=0, look_y=6)
# ---- shot 17 (60-62): two round eyes and a big smile
SN.face(60.3, eyes="sparkle", mouth="smile_open", brows="up")
# ---- shot 18 (62-66): "me?"; "go on!"
PIP.point(62.3, 62.7, "r", (960, 1420)).face(62.3, eyes="normal", mouth="o", brows="up")
PIP.unpoint(62.9, 63.1, "r")
PIP.reach(63.1, 63.5, "r", PIPA.anchor(PIP.state(63.5))(-6, -110)).face(63.3, eyes="wide", mouth="smile",
                                                                        brows="up")
PIP.to(63.1, 63.5, "io", tilt=-8)
for perf, tt in ((SN, 63.8), (CR, 63.9)):
    perf.to(tt, tt + 0.12, "io", head_dy=6).to(tt + 0.12, tt + 0.3, "io", head_dy=0)
    perf.face(tt, eyes="happy", mouth="smile_open", brows="up")
SN.walk(64.0, 64.6, 620, steps=2)
SN.reach(64.6, 64.95, "r", (880, 1300), "back").face(64.6, eyes="sparkle", mouth="smile_open", brows="up")
PIP.reach(64.0, 64.3, "r", PIPA.anchor(PIP.state(64.3))(-10, -96)).reach(64.0, 64.3, "l",
                                                                          PIPA.anchor(PIP.state(64.3))(10, -100))
T_SWAP = 64.25                                                            # the red marker goes to the right wing
PIP.rest_wings(64.4, 64.7).to(64.4, 64.7, "io", tilt=0)
PIP.face(64.6, eyes="sparkle", mouth="smile_open", brows="up")
PIP.walk(64.9, 65.9, PIP_NOSE).to(65.9, 66.1, "io", turn=0.2, look_x=12, look_y=12)
SN.reach(65.4, 65.8, "r", (700, 1330))
# ---- shot 19 (66-71): Pip draws the heart nose, a tiny tongue tip out (copying Crinkle)
U_PIP = (0.5, 0.87)
PIP.face(66.6, eyes="normal", mouth="yum", brows="think")
marker_stroke("pip", PIP, "r", "heart_l", 67.0, 67.9, U_PIP, n=14, lead=0.5)
PIP.reach(67.95, 68.15, "r", RP.grip_for_tip(_tip_world("heart_r", 0.0), U_PIP, 0.9))
marker_stroke("pip", PIP, "r", "heart_r", 68.2, 69.1, U_PIP, n=14, lead=0.05)
PIP.face(68.2, mouth="yum_l").face(69.2, eyes="sparkle", mouth="smile_open", brows="up")
PIP.reach(69.2, 69.6, "r", (930, 1330))
# ---- shot 20 (71-74): claps, hops, proud flaps
clap(SN, 71.2, 4, (720, 1270))
SN.hop(72.4, 72.85, 1, 24)
CR.to(70.8, 71.2, "io", turn=-0.4)
clap(CR, 71.4, 3, (1000, 1255))
PIP.rest_wings(70.6, 71.0).flap(71.1, 72.3).face(71.1, eyes="sparkle", mouth="smile_open", brows="up")
PIP.hop(71.2, 71.6, 1, 16)
rest_arms(SN, 72.4, 72.7)
rest_arms(CR, 72.4, 72.7)
# ---- shot 21 (74-78): the plan beside the pumpkin; three heads tilt
T_UNTUCK = 73.6
SN.reach(73.4, 73.8, "l", (560, 1330)).reach(73.9, 74.4, "l", (720, 1290))
SN.face(74.0, eyes="normal", mouth="smile", brows="think").to(74.4, 74.8, "io", look_x=14, look_y=6)
for perf, tt, pip in ((SN, 75.0, False), (PIP, 75.4, True), (CR, 75.8, False)):
    perf.to(tt, tt + 0.25, "back", tilt=-12 if not pip else -14)
for perf in (SN, PIP, CR):
    perf.to(76.6, 76.9, "back", tilt=12)
for perf in (SN, PIP, CR):
    perf.to(77.5, 77.8, "io", tilt=0)
CR.face(75.8, eyes="normal", mouth="o", brows="up")
PIP.face(75.4, eyes="normal", mouth="o", brows="up")
# ---- shot 22 (78-82): Snip asks the grown-up; thumbs-up, then "wait there"
SN.to(78.1, 78.5, "io", turn=-0.6, look_x=-12, look_y=-8).face(78.2, eyes="normal", mouth="smile_open", brows="up")
SN.reach(78.3, 78.7, "l", (480, 1180))                                   # holds up the plan
SN.reach(78.9, 79.3, "r", (760, 1290), "back")                           # points at the pumpkin
SN.face(80.4, eyes="sparkle", mouth="smile_open", brows="up").ears(80.4, 80.7, "perk")
SN.face(81.1, eyes="normal", mouth="o", brows="up").to(81.1, 81.3, "io", head_dy=4).to(81.3, 81.5, "io", head_dy=0)
for perf in (PIP, CR):
    perf.to(79.8, 80.2, "io", look_x=-14, look_y=-10)
PIP.face(80.4, eyes="sparkle", mouth="smile", brows="up")
CR.face(80.4, eyes="happy", mouth="smile", brows="calm")
T_THUMB, T_PALM = 80.3, 81.0
# ---- shot 23 (82-85): step back to the bench; markers back in the box
T_RETUCK = 82.05
SN.reach(81.8, 82.1, "l", (340, 1350)).reach(81.8, 82.1, "r", (470, 1340))
SN.walk(82.1, 83.9, SN_BENCH).to(82.2, 82.4, "io", turn=-0.3, look_x=0, look_y=0)
SN.reach(82.5, 82.85, "r", (528, 1350))                                   # his marker into the box
T_BOX_SN = 82.8
SN.reach(83.0, 83.3, "r", (230, 1330)).to(83.9, 84.2, "io", turn=0.4)
CR.walk(82.3, 84.2, CR_BENCH).to(82.3, 82.6, "io", turn=-0.4, look_x=-6, look_y=10)
PIP.walk(82.4, 84.3, PIP_BENCH).to(82.4, 82.6, "io", turn=-0.3)
CR.reach(82.5, 82.9, "r", PIPA.anchor(PIP.state(82.9))(30, -60), "io")     # a paw behind her back
for tt in np.arange(82.9, 84.2, 0.25):
    CR.reach(tt, tt + 0.25, "r", PIPA.anchor(PIP.state(tt + 0.25))(40, -60), "lin")
CR.reach(83.5, 83.85, "l", (528, 1352))                                     # marker into the box
T_BOX_CR = 83.85
CR.to(84.2, 84.5, "io", turn=-0.2)
PIP.reach(83.4, 83.75, "r", (526, 1350))
T_BOX_PIP = 83.75
PIP.to(84.3, 84.5, "io", turn=0.2)
CR.reach(84.6, 85.0, "l", (390, 1360)).reach(84.6, 85.0, "r", (610, 1360))
PIP.rest_wings(83.8, 84.1)
# ================================================================ ACT 3 (85-98.4): the grown-up cuts, the light
# friends at the bench, looking at each other (nobody looks at or goes to the pumpkin before 98.4)
SN.to(84.0, 84.4, "io", look_x=8, look_y=8).face(84.2, eyes="normal", mouth="smile", brows="calm")
CR.face(84.5, eyes="normal", mouth="smile", brows="calm").to(84.6, 85.0, "io", look_x=-10, look_y=10, hturn=-0.4)
PIP.to(85.0, 85.4, "io", x=PIP_BENCH + 30, lean=5, look_x=8, look_y=-10).face(85.0, eyes="normal", mouth="smile",
                                                                              brows="up")
TOKS = (85.6, 86.4, 87.2, 88.0, 89.4)
for tt, side in ((86.4, "l"), (87.2, "r")):
    SN.wiggle(tt, "ear_" + side, -18 if side == "l" else 18, 6, 6)
    SN.face(tt, eyes="closed").face(tt + 0.25, eyes="normal")
PIP.to(86.4, 86.6, "io", tilt=-6).to(87.4, 87.8, "io", tilt=0).face(86.4, eyes="closed", mouth="flat")
PIP.face(86.8, eyes="normal", mouth="smile", brows="up")
SN.to(88.6, 89.2, "io", look_y=-14, look_x=6).face(88.6, eyes="normal", mouth="smile", brows="calm")   # stars
PIP.to(90.0, 90.5, "io", look_y=-14, look_x=-6)
CR.to(91.0, 91.5, "io", look_y=-12, look_x=-4, hturn=-0.2)
# ================================================================ the glow (98.5-110)
for perf in (SN, PIP, CR):
    perf.to(98.4, 98.8, "io", look_x=12, look_y=4, hturn=0.0, lean=0, tilt=0)
SN.face(98.5, eyes="wide", mouth="o", brows="up").ears(98.5, 98.8, "alarm")
SN.face(98.9, eyes="sparkle", mouth="smile_open", brows="up").ears(98.9, 99.3, "perk")
CR.face(98.5, eyes="wide", mouth="O", brows="up").face(99.3, eyes="sparkle", mouth="smile_open")
PIP.face(98.6, eyes="wide", mouth="o", brows="up").face(99.4, eyes="sparkle", mouth="smile_open", brows="up")
PIP.tuft(99.4, 99.7, "up")
SN.to(98.4, 98.8, "io", turn=0.6)
CR.to(98.4, 98.8, "io", turn=0.5)
PIP.to(98.4, 98.8, "io", turn=0.4)
# shot 29 (102.5-105): closer
SN.walk(101.4, 104.0, 720)
CR.walk(101.8, 104.5, 1130).to(104.5, 104.8, "io", turn=-0.5)
CR.face(104.5, eyes="happy", mouth="smile_open", brows="calm")
PIP.walk(102.5, 104.2, 850).to(104.2, 104.4, "io", turn=0.0, look_x=0, look_y=6)
# shot 30 (105-110): three smiles in a row
SN.to(105.4, 105.9, "io", lean=8, head_dy=10, turn=0.0, look_x=0, look_y=0)
SN.face(105.6, eyes="wide", mouth="smile_open", brows="up")
PIP.face(106.2, eyes="wide", mouth="smile_open", brows="up").to(106.2, 106.5, "io", look_x=0, look_y=0)
CR.face(106.8, eyes="happy", mouth="smile_open", brows="up").wiggle(106.8, "lean", 3, 4, 3)
SN.to(108.4, 108.9, "io", lean=0, head_dy=0, turn=0.4).face(108.6, eyes="happy", mouth="smile_open", brows="calm")
# shot 31 (110-113.5): Pip glances back up at the dark wall; a shiver; edges toward Snip
PIP.to(110.3, 110.7, "io", hturn=-0.4, look_y=-16, look_x=-6).face(110.6, eyes="normal", mouth="flat", brows="worry")
PIP.shiver(111.2)
PIP.walk(112.0, 112.8, 800).to(112.8, 113.1, "io", hturn=0.0, look_x=-8, look_y=-4)
# shot 32 (113.5-117): Crinkle saw her look; tilt... tilt... idea
CR.to(113.7, 114.1, "io", look_y=-14, look_x=-8, hturn=-0.2).face(113.7, eyes="normal", mouth="flat", brows="think")
CR.to(114.5, 114.9, "io", look_y=12, look_x=-10, hturn=-0.1)
CR.to(115.0, 115.25, "back", tilt=-10).to(115.5, 115.75, "back", tilt=10)
T_IDEA_CR = 116.0
CR.to(115.95, 116.2, "io", tilt=0).face(T_IDEA_CR, eyes="sparkle", mouth="smile_open", brows="up")
IDEAS.append((T_IDEA_CR, CR))
CR.to(116.4, 116.52, "io", head_dy=6).to(116.52, 116.7, "io", head_dy=0)
# ================================================================ ACT 4 (117-160): the friendly glow on the wall
# ---- shot 33 (117-123): Snip and Pip step back; Crinkle turns the pumpkin
SN.walk(117.0, 117.8, SN_BACK).face(117.8, eyes="normal", mouth="o", brows="up").ears(117.8, 118.1, "perk")
PIP.walk(117.0, 117.9, PIP_BACK).to(117.9, 118.2, "io", turn=0.35)
CR.walk(117.0, 118.0, 960).to(117.6, 118.0, "io", turn=0.0, hturn=0.0)
PAW_L, PAW_R = (862, 1402), (1058, 1402)
CR.reach(118.0, 118.3, "l", PAW_L).reach(118.0, 118.3, "r", PAW_R)
CR.face(118.0, eyes="normal", mouth="smile", brows="think").to(118.0, 118.3, "io", look_y=10, head_dy=0, look_x=0)
CR.to(118.3, 118.6, "io", sq=0.94, lean=3).face(118.3, eyes="closed", mouth="blow", brows="think")
CR.to(119.0, 119.3, "io", sq=1.0, lean=0).face(119.0, eyes="normal", mouth="o", brows="up")
for a, b, e in ((119.5, 120.6, 120.6), (120.9, 122.0, 121.45)):      # the strain eases before the light lands
    CR.to(a, a + 0.25, "io", sq=0.95, lean=-3).to(e - 0.25, e, "io", sq=1.0, lean=0)
    CR.face(a, eyes="normal", mouth="blow", brows="think").face(b + 0.15, eyes="happy", mouth="smile", brows="calm")
CR.to(122.0, 122.5, "io", look_y=12, head_dy=0)        # eyes down at the pumpkin; chin up, clear of the light
PIP.face(118.3, eyes="normal", mouth="o", brows="up").face(122.3, eyes="normal", mouth="smile", brows="calm")
# 125 the others see the smile on his tummy
SN.face(123.0, eyes="normal", mouth="smile", brows="calm")
SN.face(125.0, eyes="sparkle", mouth="smile_open", brows="up").reach(125.0, 125.4, "r", (700, 1270), "back")
SN.reach(125.8, 126.1, "r", SN.a.face_point(SN.state(126.1), (12, -52)))
SN.arms_front.append((125.8, 126.9))
SN.reach(126.8, 127.1, "r", (600, 1340))
PIP.face(125.1, eyes="sparkle", mouth="smile_open", brows="up").flap(125.3, 126.6)
# 127 Crinkle looks up at them, then down: his tummy is smiling; laughs and wiggles
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
# ---- shot 38-39 (136-141): Pip's grin, flaps; Snip hops; Crinkle laughs and wiggles
PIP.face(136.2, eyes="wide", mouth="o", brows="up").face(136.9, eyes="sparkle", mouth="smile_open", brows="up")
PIP.tuft(136.9, 137.2, "up").tuft(137.0, 0, "flick").flap(137.2, 138.4)
SN.hop(138.7, 139.15, 1, 28).hop(139.4, 139.85, 1, 24).wiggle(138.8, "ear_l", 12, 5, 3).wiggle(138.8, "ear_r", -12, 5, 3)
CR.face(138.6, eyes="happy", mouth="smile_open", brows="up").wiggle(138.8, "lean", 5, 3, 2)
# ---- shots 40a-40c (141-148): Pip catches the face on her flat wing
SN.to(141.0, 141.4, "io", look_y=6, look_x=10, tilt=0, hturn=0.0).face(141.0, eyes="happy", mouth="smile_open")
CR.to(141.0, 141.4, "io", look_x=-12, look_y=6, turn=-0.5).face(141.0, eyes="happy", mouth="smile_open")
PIP.walk(141.0, 142.2, PIP_WING_X).to(141.0, 141.5, "io", turn=-0.05, look_y=4, look_x=10)
PIP.set(142.4, flat_r=1.0)
WING_TIP = (942, 1326)                            # where the blade's centre goes (set by the clearance check)
WING_OUT = (900, 1418)                            # wing lowered beside her: out of the light
PIP.to(142.4, 143.2, "io", lean=3, tilt=12, look_x=16, look_y=8)        # leans her head away from the light
PIP.reach_blade(142.4, 143.2, WING_TIP, bend=1)
PIP.face(143.3, eyes="happy", mouth="smile_open", brows="up").tuft(143.3, 143.4, "flick")
WING_GAME = [(145.0, 145.35, WING_OUT), (145.6, 145.9, WING_TIP), (146.4, 146.7, WING_OUT), (147.0, 147.3, WING_TIP),
             (147.7, 148.0, WING_OUT)]
for a, b, p in WING_GAME:
    PIP.reach_blade(a, b, p, bend=1)
    PIP.face(b, eyes="happy" if p == WING_TIP else "sparkle", mouth="smile_open", brows="up")
for tt in (145.95, 147.35):
    SN.face(tt, eyes="happy", mouth="smile_open", brows="calm")
    CR.face(tt, eyes="happy", mouth="smile_open", brows="up")
PIP.set(148.1, flat_r=0.0).rest_wings(148.0, 148.3).to(148.0, 148.3, "io", lean=0, tilt=0, look_y=-10, look_x=4)
PIP.walk(148.1, 148.6, 770)                                              # a step back: her face clear of the light
# ---- shot 41 (148-153): paw-bump in the light; then the low three-way bump
SN.walk(147.4, 148.4, 720).to(148.4, 148.6, "io", turn=0.4, look_x=10, look_y=-2)
CR.walk(147.3, 148.5, 1170).to(148.5, 148.7, "io", turn=-0.3, look_x=-10, look_y=-2)   # clear of the beam
BUMP = (952, 1290)
T_BUMP = 149.0
SN.reach(148.6, T_BUMP, "r", (BUMP[0] - 14, BUMP[1]), "snap")
CR.reach(148.6, T_BUMP, "l", (BUMP[0] + 14, BUMP[1]), "snap")
SN.face(T_BUMP, eyes="sparkle", mouth="smile_open", brows="up")
CR.face(T_BUMP, eyes="sparkle", mouth="smile_open", brows="up")
PIP.face(149.2, eyes="wide", mouth="o", brows="up").to(149.2, 149.5, "io", look_y=-16, look_x=6)
SN.to(149.6, 150.0, "io", look_y=12, look_x=4).reach(149.6, 150.0, "r", (820, 1340))
CR.to(149.6, 150.0, "io", look_y=12, look_x=-14).reach(149.6, 150.0, "l", (1060, 1330))
SN.to(150.2, 150.8, "io", sq=0.86, head_dy=10, lean=4)
CR.to(150.2, 150.8, "io", sq=0.84, head_dy=10, lean=-6)
LOW = (895, 1390)
T_LOW = 151.2
SN.reach(150.6, T_LOW, "r", (LOW[0] - 16, LOW[1] - 6), "snap")
CR.reach(150.6, T_LOW, "l", (LOW[0] + 18, LOW[1] - 4), "snap")
PIP.reach(150.6, T_LOW, "r", (LOW[0], LOW[1] - 14), "snap").face(150.6, eyes="sparkle", mouth="smile_open", brows="up")
for perf in (SN, CR):
    perf.face(T_LOW, eyes="happy", mouth="smile_open", brows="up")
SPARKLES += [(T_BUMP, BUMP, 0.32), (T_LOW, (LOW[0], LOW[1] - 30), 0.22)]
for perf in (SN, CR):
    perf.to(151.8, 152.4, "io", sq=1.0, head_dy=0, lean=0)
    rest_arms(perf, 151.8, 152.3)
PIP.rest_wings(151.8, 152.2)
# ---- shot 42 (153-160): the end: Pip snuggles against Snip; Crinkle waves up at the giant face
SN.walk(153.1, 154.1, 600).to(154.1, 154.4, "io", turn=0.3, look_x=8, look_y=-12)
PIP.walk(153.2, 154.0, 705).to(154.0, 154.4, "io", turn=-0.4, lean=-6, look_x=-6, look_y=-10)
CR.walk(153.1, 154.6, 1340).to(154.6, 154.9, "io", turn=-0.3, look_y=-14, look_x=-8)
CR.reach(155.0, 155.4, "r", (1440, 1080))
for i in range(5):
    CR.reach(155.4 + i * 0.45, 155.625 + i * 0.45, "r", (1470, 1090), "io")
    CR.reach(155.625 + i * 0.45, 155.85 + i * 0.45, "r", (1430, 1080), "io")
CR.face(155.0, eyes="happy", mouth="smile_open", brows="up")
SN.reach(155.6, 156.1, "r", PIPA.anchor(PIP.state(156.1))(-40, -150))      # an arm round Pip
PIP.face(156.5, eyes="closed", mouth="smile", brows="calm").to(156.5, 157.2, "io", tilt=-8)
SN.face(156.8, eyes="happy", mouth="smile", brows="calm")


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
    if 90.5 <= t < 97.4:
        lid = "off"
    rotd = 90 * ease_in_out(seg(t, 119.5, 120.6)) + 90 * ease_in_out(seg(t, 120.9, 122.0))
    return dict(strokes=strokes, holes=holes, lid=lid, rot=rotd, lit=L.glow_k(t))


def proj_k(rotd):
    """How much of the cut face points at the wall (and at whoever stands behind the pumpkin)."""
    return ease_in_out(seg(rotd, 150.0, 179.0))


def chest_plane(rotd):
    return L.CHEST.shifted(dx=(180.0 - rotd) * 2.2)


WING_PLANE = L.Plane(WING_TIP, L.WING.sx, blur=L.WING.blur, name="wing")
BUMP_PLANE = L.Plane((958, 1296), 0.6, blur=1.2, name="bump")


# ---------------------------------------------------------------- the grown-up's hand (79.6-82.2, 84.4-98.4)
SH_LEFT = (-700, 300)                     # shoulder far off the left (thumbs-up, "wait there")
SH_TOP = (1250, -250)                     # shoulder above the porch roof (the pumpkin work: clear of the friends)
LID_GRIP = (8, -26)                       # the stem, relative to the lid sprite's pivot
LID_ON = (PK.BASE[0] + PK.LID_C[0], PK.BASE[1] + PK.LID_C[1])
LID_DECK = (1170, 1497)
REST_W = (1150, 1300)                     # steadying hand flat on the pumpkin's top right (clear of the eyes)
TEA_HOLD = (958, 1270)                    # the tea light's top above the opening
TEA_IN = (958, 1470)                      # ... at the bottom inside
TEA_OFF = (34, 15)                        # grip point relative to the light's top centre (fingers on its right side)
T_CLICK = 93.0


def _path(t, keys):
    """Piecewise eased path [(t, (x, y)), ...]."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            return lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k)
    return keys[-1][1]


def hand_state(t):
    """What the grown-up's hand does now: dict(shoulder, bend, hand, grip or wrist, holds, light_top, lid_at, ...)."""
    if 79.6 <= t < 82.2:
        w = _path(t, [(79.6, (-160, 760)), (80.15, (330, 860)), (81.6, (330, 860)), (82.2, (-180, 760))])
        hand = "thumb" if t < T_PALM else "palm"
        squash = 1.0 - 0.8 * max(0.0, 1 - abs(t - T_PALM) / 0.12)
        return dict(shoulder=SH_LEFT, bend=1, hand=hand, wrist=w, sx=squash)
    if not 84.4 <= t < 98.4:
        return None
    lid_grip_on = (LID_ON[0] + LID_GRIP[0], LID_ON[1] + LID_GRIP[1])
    lid_grip_deck = (LID_DECK[0] + LID_GRIP[0], LID_DECK[1] + LID_GRIP[1])
    tea_g = lambda p: (p[0] + TEA_OFF[0], p[1] + TEA_OFF[1])                # noqa: E731
    st = dict(shoulder=SH_TOP, bend=-1, hand="pinch", holds=None, sx=1.0)
    if t < 90.3:                                       # comes in, rests on the pumpkin while the shapes are cut
        st.update(hand="rest", wrist=_path(t, [(84.4, (1200, 560)), (85.0, REST_W)]), angle=-160)
        tap = sum(math.exp(-((t - tk) / 0.05) ** 2) for tk in TOKS)
        st["sleeve_tap"] = tap
        return st
    if t < 91.6:                                       # lifts the lid by its stem, sets it beside the pumpkin
        g = _path(t, [(90.3, (1080, 1300)), (90.5, lid_grip_on), (90.9, (1010, 1230)), (91.4, lid_grip_deck),
                      (91.6, (1220, 1380))])
        st.update(grip=g)
        if 90.5 <= t < 91.4:
            st["lid_at"] = (g[0] - LID_GRIP[0], g[1] - LID_GRIP[1])
        return st
    if t < 92.0:
        st.update(grip=_path(t, [(91.6, (1220, 1380)), (92.0, (1260, 600))]))
        return st
    if t < 96.85:                                      # brings the tea light, clicks it on, lowers it in
        top = _path(t, [(92.0, (1060, 600)), (92.5, TEA_HOLD), (95.6, TEA_HOLD), (96.8, TEA_IN)])
        st.update(grip=tea_g(top), light_top=top, holds="tea")
        if T_CLICK - 0.08 <= t < T_CLICK + 0.14:
            st["hand"] = "press"
        return st
    if t < 97.6:                                       # the lid back on
        g = _path(t, [(96.85, tea_g(TEA_IN)), (97.0, (1060, 1330)), (97.12, lid_grip_deck), (97.4, lid_grip_on),
                      (97.6, (1040, 1240))])
        st.update(grip=g)
        if 97.12 <= t < 97.4:
            st["lid_at"] = (g[0] - LID_GRIP[0], g[1] - LID_GRIP[1])
        return st
    st.update(grip=_path(t, [(97.6, (1040, 1240)), (98.4, (1250, 560))]))   # leaves
    return st


def lid_where(t):
    """The lid sprite's position when it is off the pumpkin and not in the hand (else None)."""
    if 91.4 <= t < 97.12:
        return LID_DECK
    return None


def tea_on(t):
    return t >= T_CLICK


def _inside_clip(lay, cam):
    """Hide what goes down into the opening: below the front rim, inside the pumpkin."""
    if lay is None:
        return
    xx, yy = L._grid(lay.box)
    wx, wy = L._world(cam, xx, yy)
    dx = (wx - LID_ON[0]) / PK.LID_R[0]
    rim = LID_ON[1] + PK.LID_R[1] * np.sqrt(np.clip(1 - dx * dx, 0, 1))
    inside = (np.abs(dx) < 1.0) & (wy > rim)
    a = np.asarray(lay.img).astype(np.float32)
    a[..., 3] *= (1 - inside)
    lay.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def draw_hand(im, cam, hs):
    hand = H.HANDS[hs["hand"]]
    if "wrist" in hs:
        W = hs["wrist"]
        E, fa = ARM.draw(im, cam, hs["shoulder"], W, hs["bend"])
        ang = 0.0 if hand.upright else hs.get("angle", fa + hs.get("turn", 0.0))
        place(im, hand.spr, cam.S(W), angle=ang, sx=hs.get("sx", 1.0))
        return
    W = ARM.wrist_for(hs["shoulder"], hs["grip"], hand, hs["bend"], hs.get("turn", 0.0))
    if hs.get("holds") == "tea":
        place(im, TEA[tea_on(T_NOW[0])], cam.S(hs["light_top"]), scale=TEA_SCALE)
    ARM.draw_hand(im, cam, hs["shoulder"], W, hand, hs["bend"], hs.get("turn", 0.0))


T_NOW = [0.0]


# ---------------------------------------------------------------- held props
def book_state(t):
    """(where, view, flip squash) of Snip's sketchbook: 'paw_l' (held up), 'tucked'."""
    if t < T_TUCK or T_UNTUCK <= t < T_RETUCK:
        view = "back" if t < T_FLIP + 0.2 else "plan"
        sq = abs(math.cos(math.pi * seg(t, T_FLIP, T_FLIP + 0.4))) if T_FLIP <= t < T_FLIP + 0.4 else 1.0
        return "paw_l", view, max(0.06, sq)
    return "tucked", None, 1.0


def crayon_in_paw(t):
    """Snip holds the crayon only while sketching; otherwise it is clipped on the book (never near a mouth)."""
    return t < 15.1 or 28.2 <= t < 30.0


def markers_in_box(t):
    n = 3 if t < T_MARKERS else 0
    n += (t >= T_BOX_SN) + (t >= T_BOX_CR) + (t >= T_BOX_PIP)
    return min(3, n)


def sn_markers(t):
    """How many markers Snip holds (fan in the right paw)."""
    if T_MARKERS <= t < T_GIVE_PIP:
        return 3
    if T_GIVE_PIP <= t < T_GIVE_CR:
        return 2
    if T_GIVE_CR <= t < T_BOX_SN:
        return 1
    return 0


def draw_snip_props(im, cam, st, t, layer="all"):
    where, view, sq = book_state(t)
    if where == "tucked":
        a = SN.a.anchor(st)
        place(im, BOOK_TUCK, cam.S(a(-96, -150)), angle=st["lean"] + 8)
        SN.a._arm(im, cam, st, "l")
    if crayon_in_paw(t):
        W, fa = SN.paw(t, "r", st)
        place(im, CRAYON, cam.S(W), angle=fa)
    n = sn_markers(t)
    if n:
        W, ang = tool_angle(SN, "r", st, TRACK["sn"], t)
        for i in range(n):
            spr = MK[("pip", "red")] if (n == 3 and i == 2) else MK[("sn", "black")]
            place(im, spr, cam.S(W), angle=ang + (i - (n - 1) / 2) * 14)
    if where == "paw_l":
        W, _ = SN.paw(t, "l", st)
        place(im, BOOK[view], cam.S((W[0] + 6, W[1] + 12)), sx=sq, angle=st["lean"] * 0.5, scale=BOOK_SCALE)
        if not crayon_in_paw(t) and t < T_TUCK:                  # the crayon clipped in the spiral
            top = (W[0] + 6 + 30 * BOOK_SCALE * sq, W[1] + 12 - (G.BOOK_H + 12) * BOOK_SCALE)
            place(im, CRAYON, cam.S(top), angle=90 + st["lean"] * 0.5)
        SN.a._arm(im, cam, st, "l")


def draw_crinkle_props(im, cam, st, t, over=False):
    if t < 15.75:
        W, _ = CR.paw(t, "r", st)
        place(im, CLOTH, cam.S(W))
        if over:
            CR.a._arm(im, cam, st, "r")
    else:
        place(im, CLOTH_CORNER, cam.S(CR.a.anchor(st)(70, -232)), angle=st["lean"])
    if T_GIVE_CR <= t < T_BOX_CR:
        W, ang = tool_angle(CR, "l", st, TRACK["cr"], t)
        place(im, MK[("cr", "black")], cam.S(W), angle=ang)


def pip_marker_side(t):
    if T_GIVE_PIP <= t < T_SWAP:
        return "l"
    if T_SWAP <= t < T_BOX_PIP:
        return "r"
    return None


def draw_pip_marker(im, cam, st, t):
    side = pip_marker_side(t)
    if side is None:
        return
    W, ang = tool_angle(PIP, side, st, TRACK["pip"], t)
    place(im, MK[("pip", "red")], cam.S(W), angle=ang)
    place(im, PIPA.grip, cam.S(W), angle=ang)


def arms_over(t):
    """Arms (and what they hold) drawn again after the pumpkin, because they touch or reach over it."""
    out = []
    if t < 15.75:
        out.append(("cr", "r"))
    if 44.6 <= t < 48.6:
        out.append(("sn", "r"))
    if 54.9 <= t < 60.4:
        out.append(("cr", "l"))
    if 32.85 <= t < 33.7:
        out.append(("cr", "l"))
    if 66.3 <= t < 69.8:
        out.append(("pip", "r"))
    if 118.0 <= t < 127.3:
        out += [("cr", "l"), ("cr", "r")]
    if 148.7 <= t < 149.7:
        out += [("sn", "r"), ("cr", "l")]
    if 150.7 <= t < 151.9:
        out += [("sn", "r"), ("cr", "l"), ("pip", "r")]
    return out


# ---------------------------------------------------------------- the chime, the leaves, sparkles
CHIME_KICKS = [(BREEZE, 9.0), (T_BONK, 16.0)]


def chime_angle(t):
    a = 0.0
    for t0, amp in CHIME_KICKS:
        if t >= t0:
            dt = t - t0
            a += amp * math.exp(-dt * 1.6) * math.sin(2 * math.pi * 1.3 * dt)
    return a


LEAF_RUNS = [(12.6, 1.5, 1560, 1525, 0), (12.85, 1.6, 1600, 1545, 1), (13.1, 1.5, 1580, 1510, 2)]


def draw_leaves(f, cam, t):
    for t0, dur, x0, y0, i in LEAF_RUNS:
        u = seg(t, t0, t0 + dur)
        if 0 < u < 1:
            x = x0 - 1500 * u
            y = y0 - 14 * abs(math.sin(math.pi * 3 * u)) - 6 * u
            place(f, LEAVES[i], cam.S((x, y)), angle=360 * 2 * u * (1 if i % 2 else -1))


def draw_fx(f, cam, t, sts):
    for t0, perf in IDEAS:
        u = seg(t, t0, t0 + 1.2)
        if 0 < u < 1:
            st = sts[id(perf)]
            hx, hy = perf.a.head_pivot(st)
            up = 290 if perf is SN else 250
            k = ease_out_back(seg(t, t0, t0 + 0.3)) * (1 - ease_in_out(seg(t, t0 + 0.9, t0 + 1.2)))
            place(f, SPARK, cam.S((hx + 40, hy - up)), scale=0.36 * k, angle=20 * u, shadow=False)
    for t0, p, s in SPARKLES:
        u = seg(t, t0, t0 + 0.8)
        if 0 < u < 1:
            k = ease_out_back(seg(t, t0, t0 + 0.2)) * (1 - ease_in_out(seg(t, t0 + 0.5, t0 + 0.8)))
            place(f, SPARK_S, cam.S((p[0], p[1] - 40)), scale=s * k, angle=30 * u, shadow=False)


# ---------------------------------------------------------------- one frame of the world
def order_at(t):
    if 14.8 <= t < 21.6:                                   # Pip hides behind Crinkle
        return ["pip", "cr", "sn"]
    if 147.3 <= t < 148.6:
        return ["sn", "cr", "pip"]
    return ["sn", "cr", "pip"]


def render_world(t, d=None, cam=None, bg=None, report=None):
    cam = cam or CAM
    T_NOW[0] = t
    sn, cr, ps = SN.state(t, d), CR.state(t, d), PIP.state(t, d)
    sts = {id(SN): sn, id(CR): cr, id(PIP): ps}
    pk = pumpkin_state(t)
    glow = pk["lit"]
    facing = max(0.0, math.cos(math.radians(pk["rot"])))
    glow_ch = glow * (0.3 + 0.7 * facing)            # turned to the wall, little of its light comes our way
    f = bg.copy() if bg is not None else WORLD.background(t)
    size = f.size
    place(f, BOXES[markers_in_box(t)], cam.S(P.MARKER_BOX_AT))
    place(f, CHIME, cam.S(G.CHIME_AT), angle=chime_angle(t), scale=1.15)
    flat = ps["flat_r"] > 0.5
    over = arms_over(t)
    pip_skip = ("r",) if flat or ("pip", "r") in over else ()

    def draw_pip(im):
        PIPA.draw_parts(im, cam, ps, skip=pip_skip)
        if ("pip", pip_marker_side(t) or "") not in over:
            draw_pip_marker(im, cam, ps, t)

    def draw_sn(im):
        SN.draw(im, t, cam, st=sn)
        if ("sn", "r") not in over:
            draw_snip_props(im, cam, sn, t)
        else:
            draw_snip_props_book_only(im, cam, sn, t)

    def draw_cr(im):
        CR.draw(im, t, cam, st=cr)
        draw_crinkle_props(im, cam, cr, t)

    lay = {"pip": L.Layer.of(size, draw_pip, head=PIPA.head_mask(ps, cam, size)),
           "sn": L.Layer.of(size, draw_sn, head=L.head_mask(SN.a, sn, cam, size)),
           "cr": L.Layer.of(size, draw_cr, head=L.head_mask(CR.a, cr, cam, size))}
    lay_wing = L.Layer.of(size, lambda im: PIPA._arm(im, cam, ps, "r")) if flat else None

    def draw_over(im):
        for who, side in over:
            if who == "cr":
                if side == "r" and t < 15.75:
                    draw_crinkle_props(im, cam, cr, t, over=True)
                    continue
                CR.a._arm(im, cam, cr, side)
                if T_GIVE_CR <= t < T_BOX_CR and side == "l":
                    W, ang = tool_angle(CR, "l", cr, TRACK["cr"], t)
                    place(im, MK[("cr", "black")], cam.S(W), angle=ang)
            elif who == "sn":
                SN.a._arm(im, cam, sn, side)
                n = sn_markers(t)
                if n and side == "r":
                    W, ang = tool_angle(SN, "r", sn, TRACK["sn"], t)
                    place(im, MK[("sn", "black")], cam.S(W), angle=ang)
            else:
                PIPA._arm(im, cam, ps, side)
                if pip_marker_side(t) == side:
                    draw_pip_marker(im, cam, ps, t)
    lay_arms = L.Layer.of(size, draw_over) if over else None
    hs = hand_state(t)
    lay_hand = L.Layer.of(size, lambda im: draw_hand(im, cam, hs)) if hs else None
    # light on the porch (before anyone stands in front of it)
    caught = L.sun_light(f, t, cam, WORLD.albedo, occluders=[lay_wing, lay["pip"]])
    L.floor_pool(f, cam, WORLD.albedo, glow, facing, side=math.sin(math.radians(pk["rot"])))
    pkk = proj_k(pk["rot"]) * glow
    occ = []
    if lay["cr"] is not None:
        occ.append((lay["cr"].solid(), lay["cr"].box, L.CHEST))
    if lay_wing is not None and pkk > 0:
        occ.append((_beam_part(lay_wing, WING_PLANE, cam), lay_wing.box, WING_PLANE))
    bump_light = lay_arms is not None and 148.7 <= t < 149.7 and pkk > 0
    if bump_light:
        occ.append((_beam_part(lay_arms, BUMP_PLANE, cam), lay_arms.box, BUMP_PLANE))
    Iw, bw = L.wall_light(f, cam, WORLD.albedo, pkk, occ)
    # characters: grade, warm glow, sun and beams (never on faces)
    lit = {}
    ck = ease_in_out(seg(pk["rot"], 140.0, 178.0)) * glow
    for name in order_at(t):
        ly = lay[name]
        L.grade_layer(ly, t, glow_ch, L.GLOW_AT, cam)
        L.rail_shade(ly, t, cam)
        if name == "pip":
            lit["pip_heart"] = (L.heart_on_layer(ly, caught, t, cam), ly)
        if name == "cr" and pkk > 0:
            lit["cr"] = (L.beam_on_layer(ly, chest_plane(pk["rot"]), cam, ck), ly)
        if ly is not None:
            ly.paste(f)
    draw_leaves(f, cam, t)
    # the second sleeve behind the pumpkin (it never shows a hand or anything in it)
    if hs and "sleeve_tap" in hs:
        k = ease_in_out(seg(t, 84.8, 85.2)) * (1 - ease_in_out(seg(t, 89.9, 90.3)))
        if k > 0.01:
            tap = hs["sleeve_tap"]
            at = (1000 + 3 * tap, 1420 + 30 * (1 - k) - 3 * tap)      # mostly hidden: only the cuff peeks
            lay_sl = L.Layer.of(size, lambda im: place(im, SLEEVE2, cam.S(at), angle=145))
            L.grade_layer(lay_sl, t, glow_ch, L.GLOW_AT, cam)
            lay_sl.paste(f)
    # the pumpkin (a prop: graded with the set), its own light, the lid on the deck
    spr = PUMP.paper(rot=pk["rot"], strokes=pk["strokes"], holes=pk["holes"], lid=pk["lid"])
    lay_pk = L.Layer.of(size, lambda im: place(im, spr, cam.S(PK.BASE)))
    L.grade_layer(lay_pk, t, prop=True)
    lay_pk.paste(f)
    em = PUMP.emissive(rot=pk["rot"], lit=glow, holes=pk["holes"], lid=pk["lid"])
    if em is not None:
        place(f, em, cam.S(PK.BASE), shadow=False)
    lid_at = (hs or {}).get("lid_at") or lid_where(t)
    if lid_at is not None:
        lay_lid = L.Layer.of(size, lambda im: place(im, PUMP.lid_sprite(), cam.S(lid_at)))
        L.grade_layer(lay_lid, t, prop=True)
        lay_lid.paste(f)
    if lay_arms is not None:
        L.grade_layer(lay_arms, t, glow_ch, L.GLOW_AT, cam)
        if 118.0 <= t < 127.3 and pkk > 0:
            L.beam_on_layer(lay_arms, chest_plane(pk["rot"]), cam, ck)
        if bump_light:
            lit["bump"] = (L.beam_on_layer(lay_arms, BUMP_PLANE, cam, pkk, own=(0.6, 0.35)), lay_arms)
        lay_arms.paste(f)
    if lay_wing is not None:
        L.grade_layer(lay_wing, t, glow_ch, L.GLOW_AT, cam)
        L.rail_shade(lay_wing, t, cam)
        if pkk > 0:
            L.shade_layer(lay_wing, WING_SHADE, pkk)    # Lead L3: the rest of the held-up wing in evening shade
        lit["wing_heart"] = (L.heart_on_layer(lay_wing, caught, t, cam), lay_wing)
        if pkk > 0:
            lit["wing"] = (L.beam_on_layer(lay_wing, WING_PLANE, cam, pkk, bloom=3.0, own=(0.75, 0.25)),
                           lay_wing)                     # Lead L3: warm near-white on the yellow wing
        lay_wing.paste(f)
    if lay_hand is not None:
        L.grade_layer(lay_hand, t, glow_ch, L.GLOW_AT, cam)
        if 95.5 <= t < 97.0:
            _inside_clip(lay_hand, cam)
        lay_hand.paste(f)
        if hs.get("holds") == "tea" and tea_on(t) and t < 96.3:
            top = hs["light_top"]
            L.halo(f, cam, 1.0, at=(top[0], top[1] - 8), strength=0.45, sigma=10.0)
    L.halo(f, cam, glow * (0.25 + 0.75 * facing))     # turned to the wall: only a faint glow comes our way
    WORLD.front(f, t)
    L.rail_glow(f, t, cam)
    draw_fx(f, cam, t, sts)
    if report is not None:
        report.update(dict(sn=sn, cr=cr, pip=ps, lit=lit, wall=(Iw, bw), pk=pk))
    return f


def draw_snip_props_book_only(im, cam, st, t):
    """Snip's props when his right arm is drawn again over the pumpkin (the marker goes with that arm)."""
    where, view, sq = book_state(t)
    if where == "tucked":
        place(im, BOOK_TUCK, cam.S(SN.a.anchor(st)(-96, -150)), angle=st["lean"] + 8)
        SN.a._arm(im, cam, st, "l")


def _beam_part(lay, plane, cam):
    """The part of a layer that stands in the beam on `plane` (what it takes away from the wall)."""
    pb = L._clip_box(L._pbox(plane, cam), (10 ** 6, 10 ** 6))
    box = lay.box
    full = np.zeros((box[3] - box[1], box[2] - box[0]), np.float32)
    ix0, iy0 = max(box[0], pb[0]), max(box[1], pb[1])
    ix1, iy1 = min(box[2], pb[2]), min(box[3], pb[3])
    if ix1 > ix0 and iy1 > iy0:
        pat = L.pattern(plane, cam, (ix0, iy0, ix1, iy1))
        full[iy0 - box[1]:iy1 - box[1], ix0 - box[0]:ix1 - box[0]] = np.clip(pat * 2.5, 0, 1)
    return lay.solid() * full


# ---------------------------------------------------------------- cameras (plan shot list; L3: 40b at 2.8x)
SHOTS = [   # (start, centre, zoom[, zoom_to, ease_from, ease_to])
    (0.0, (980, 1100), 1.0),                     # 1 golden: the hearts
    (4.0, (1190, 1300), 1.9),                    # 2 the heart on her wing
    (6.0, (980, 1100), 1.0),                     # 3 the sun goes down
    (10.0, (1200, 1290), 1.9),                   # 4 empty wing
    (12.5, (1000, 1180), 1.4),                   # 5 the breeze; poof; she hides
    (15.0, (760, 1150), 1.2),                    # 6 behind you!
    (22.0, (880, 1220), 1.6),                    # 7 Crinkle crouches to her
    (26.0, (440, 1110), 1.6),                    # 8 Snip's idea
    (30.0, (470, 1215), 2.0),                    # 9 the plan
    (32.0, (760, 1120), 1.15),                   # 10 the dance
    (39.0, (580, 1200), 1.5),                    # 11 markers
    (43.0, (900, 1180), 1.2),                    # 12 to the pumpkin
    (45.0, (960, 1380), 1.9),                    # 13 eyes
    (49.0, (720, 920), 1.4),                     # 14 the chime
    (53.0, (1080, 1250), 1.3),                   # 15 Crinkle gets ready
    (55.0, (1010, 1320), 1.8),                   # 16 the smile
    (60.0, (960, 1400), 1.9),                    # 17 the face so far
    (62.0, (760, 1200), 1.4),                    # 18 me? go on!
    (66.0, (910, 1330), 1.9),                    # 19 the heart nose
    (71.0, (900, 1180), 1.3),                    # 20 claps
    (74.0, (860, 1150), 1.2),                    # 21 plan vs pumpkin
    (78.0, (960, 1100), 1.0),                    # 22 the grown-up
    (82.0, (560, 1180), 1.3),                    # 23 to the bench
    (85.0, (1100, 1340), 2.0),                   # 24a the hand; tok
    (86.2, (330, 1150), 1.6),                    # 25 the friends: tok, tok
    (87.6, (1100, 1340), 2.0),                   # 24b holes, the lid
    (92.0, (1070, 1290), 2.0),                   # 26 the tea light: click
    (95.0, (1100, 1340), 2.0),                   # 27 it goes in: the face lights up
    (98.5, (1000, 1300), 1.9, 1.3, 100.2, 102.2),  # 28 THE GLOW, pull back
    (102.5, (880, 1200), 1.4),                   # 29 closer
    (105.0, (860, 1270), 1.7),                   # 30 three smiles
    (110.0, (900, 1000), 1.4),                   # 31 Pip glances back
    (113.5, (1130, 1100), 1.6),                  # 32 Crinkle's idea
    (117.0, (960, 1180), 1.15),                  # 33 the turn
    (123.0, (960, 1280), 1.9),                   # 34 the smile on his tummy
    (125.0, (700, 1200), 1.5),                   # 35 they see it
    (127.0, (960, 1130), 1.6),                   # 36 he sees it
    (130.0, (960, 1080), 1.15, 1.0, 130.4, 131.6),  # 37 THE WOW
    (136.0, (730, 1260), 1.9),                   # 38 Pip's grin
    (138.5, (960, 1150), 1.2),                   # 39 everyone
    (141.0, (900, 1150), 1.4),                   # 40a the wing goes up
    (143.5, (880, 1290), 2.8),                   # 40b a tiny glowing face on her wing
    (145.0, (960, 1100), 1.15),                  # 40c in, out
    (148.0, (960, 1250), 1.4),                   # 41 paw-bump
    (153.0, (960, 1080), 1.0, 1.05, 153.5, 159.0),  # 42 the end
]
CUTS = [s[0] for s in SHOTS[1:]]


def shot_at(t):
    cur = SHOTS[0]
    for s in SHOTS:
        if t >= s[0] - 1e-9:
            cur = s
    if len(cur) == 6:
        _, c, z0, z1, a, b = cur
        return c, lerp(z0, z1, ease_in_out(seg(t, a, b)))
    return cur[1], cur[2]


def shoot(f, centre, z, cam=None):
    """Crop the world frame to the shot (zoom z about the world point `centre`) and size it to 1920x1080."""
    cam = cam or CAM
    w, h = f.size
    cw, ch = w / z, h / z
    cx, cy = cam.S(centre)
    x0 = min(max(cx - cw / 2, 0), w - cw)
    y0 = min(max(cy - ch / 2, 0), h - ch)
    return f.resize((1920, 1080), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


HI40B = os.path.join(ROOT, "build", "ep11_40b")


def render_frame(t, view="land", report=None, centre=None, z=None):
    d = K.drawing_of(t)
    tq = d / K.DPS
    if 143.5 - 1e-6 <= tq < 145.0 and centre is None and RES == 2:
        p = os.path.join(HI40B, f"d{d:05d}.png")
        if os.path.exists(p):
            return Image.open(p).convert("RGB")
    f = render_world(tq, d, report=report)
    c, zz = shot_at(tq)
    return shoot(f, centre or c, z or zz).convert("RGB")


def frame(t, report=None, centre=None, z=None):
    return render_frame(t, "land", report, centre, z)


# ---------------------------------------------------------------- sound (no voices: effects and music only)
BEAT = 60.0 / 116.0
SW = 2.0 / 3.0                                   # swing: the off-beat eighth lands two thirds into the beat
ROOTS = {"F": 41, "Bb": 46, "C": 48, "C7": 48, "Dm": 50, "Gm": 43}
CH = dict(MX.CHORDS, C7=(58, 60, 64, 67), Gm=(58, 62, 67, 70))
TUNE = [(0, 72, .5), (SW, 69, .3), (1, 65, .5), (2, 69, .5), (2 + SW, 72, .3), (3, 77, .9),
        (4, 74, .5), (4 + SW, 70, .3), (5, 74, .5), (6, 77, .5), (7, 74, .9),
        (8, 72, .5), (8 + SW, 70, .3), (9, 67, .5), (10, 70, .5), (10 + SW, 72, .3), (11, 76, .9),
        (12, 77, .5), (13, 72, .5), (14, 69, .5), (15, 65, 1.2)]
PROG = ["F", "Bb", "C7", "F"]


def giggle_snd(vel=1.0, base=84):
    out = np.zeros(int(0.9 * A.SR))
    for i, m in enumerate((0, 4, 2, 7, 4, 9)):
        g = MX.toy_piano(A.midi(base + m), 0.3, 0.6 * vel)
        s = int(i * 0.1 * A.SR)
        out[s:s + len(g)] += g[:len(out) - s]
    return out


def peep(vel=1.0, f0=1500):
    t = A._t(0.09)
    return vel * 0.5 * np.sin(2 * np.pi * np.cumsum(f0 + 900 * t / 0.09) / A.SR) * np.sin(np.pi * t / 0.09)


def _sum(*sigs):
    """Add signals of different lengths (padded with silence)."""
    n = max(len(x) for x in sigs)
    out = np.zeros(n)
    for x in sigs:
        out[:len(x)] += x
    return out


def poof(vel=1.0):
    return _sum(A.whoosh(0.3, 0.6 * vel), 0.6 * A.pop(vel))


def tok(vel=1.0):
    """A soft woody tap (the cutting): never a saw or scrape; no louder than the footsteps."""
    return A.woodblock(False, 0.32 * vel)


def thoonk(vel=1.0):
    t = A._t(0.3)
    return vel * 0.5 * np.sin(2 * np.pi * np.cumsum(220 - 120 * t) / A.SR) * np.exp(-t * 14) * A._attack(t, 1500)


def click(vel=1.0):
    t = A._t(0.03)
    n = np.random.default_rng(3).normal(0, 1, len(t))
    return vel * 0.5 * n * np.exp(-t * 300)


def rumble(dur=1.0, vel=1.0):
    t = A._t(dur)
    n = np.random.default_rng(8).normal(0, 1, len(t))
    return vel * 0.5 * A._lowpass(n, 90) * 6 * np.sin(np.pi * t / dur) ** 2


def squeak(dur=0.3, vel=1.0, f0=2100):
    t = A._t(dur)
    f = f0 + 250 * np.sin(2 * np.pi * 7 * t)
    return vel * 0.12 * np.sin(2 * np.pi * np.cumsum(f) / A.SR) * np.sin(np.pi * t / dur)


def scratch(dur=0.3, vel=1.0, seed=4):
    t = A._t(dur)
    n = np.random.default_rng(seed).normal(0, 1, len(t))
    return vel * 0.25 * (n - A._lowpass(n, 4)) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / dur)


def rustle(dur=1.2, vel=1.0):
    t = A._t(dur)
    n = np.random.default_rng(12).normal(0, 1, len(t))
    return vel * 0.4 * (A._lowpass(n, 3) - A._lowpass(n, 25)) * np.sin(np.pi * t / dur) ** 2


def chime_ring(vel=1.0, seed=1):
    r = np.random.default_rng(seed)
    out = np.zeros(int(2.0 * A.SR))
    for i in range(6):
        m = int(r.choice((96, 99, 101, 103, 106, 108)))
        g = A.glock(A.midi(m), 1.4, 0.3 * vel * (1 - i / 8))
        s = int((i * 0.09 + r.uniform(0, 0.05)) * A.SR)
        out[s:s + len(g)] += g[:len(out) - s]
    return out


def make_buses():
    """The episode's music and sound-effect buses (the Shorts cut their effects from these)."""
    M = A.midi
    music, sfx = A.Mix(DUR), A.Mix(DUR)

    def groove(t0, t1, vel=0.32, lead=True, bass=True, comp=True, prog=PROG, glock_every=0, tiptoe=False):
        """Swung organ groove in F from t0 to t1: pluck bass with chromatic steps, organ off-beat chords, the tune."""
        bar = 4 * BEAT
        t, i = t0, 0
        while t < t1 - 0.05:
            ch = prog[i % len(prog)]
            nxt = prog[(i + 1) % len(prog)]
            root = ROOTS[ch]
            if bass:
                for b, m in ((0, root), (2, root + 7 if not tiptoe else root + 4),
                             (3 + SW, ROOTS[nxt] + (1 if ROOTS[nxt] < root else -1))):
                    if t + b * BEAT < t1:
                        music.add(t + b * BEAT, A.pluck(M(m), 0.35, 0.75 * vel / 0.32))
            if comp:
                for b in (SW, 1 + SW, 2 + SW, 3 + SW) if not tiptoe else (SW, 2 + SW):
                    if t + b * BEAT < t1:
                        for m in CH[ch]:
                            music.add(t + b * BEAT, MX.organ(M(m), 0.18, 0.22 * vel / 0.32))
            if lead:
                for bt, m, dd in TUNE:
                    if 4 * (i % 4) <= bt < 4 * (i % 4) + 4:
                        tt = t + (bt - 4 * (i % 4)) * BEAT
                        if tt < t1:
                            music.add(tt, MX.organ(M(m), dd * BEAT, 0.5 * vel / 0.32))
            if glock_every and i % glock_every == 0:
                music.add(t + 3 * BEAT, A.glock(M(CH[ch][-1] + 12), 1.0, 0.2))
            if tiptoe:
                music.add(t + BEAT, A.woodblock(True, 0.18))
                music.add(t + 3 * BEAT, A.woodblock(False, 0.18))
            t += bar
            i += 1
        return t

    def held(t0, dur, notes, vel=0.35):
        music.add(t0, A.pad([M(n) for n in notes], dur, vel))

    def bed(t0, t1, vel=0.1):
        """A soft organ-pad bed under everything (follows the chords bar by bar): no silent gaps."""
        bar = 4 * BEAT
        t, i = t0, 0
        while t < t1 - 0.1:
            ch = PROG[i % len(PROG)]
            dur = min(bar + 1.6, t1 - t + 0.8)
            music.add(t - 0.8, A.pad([M(n - 12) for n in CH[ch][:3]], dur, vel))
            t += bar
            i += 1

    # ---- music by section (plan section 6)
    bed(1.0, 159.9, 0.28)
    A.jingle(music, 0.0, 0.9)
    groove(0.9, 6.0, vel=0.34, glock_every=1)
    groove(6.0, 9.6, vel=0.24, lead=False)
    for i, m in enumerate((84, 81, 77, 72)):
        music.add(6.4 + i * 0.75, A.glock(M(m), 1.2, 0.3))                    # hearts fade, sun sets
    held(9.4, 5.8, (53, 60, 65, 69), 0.32)
    for tt, m in ((10.2, 77), (11.4, 74), (12.6, 72), (13.8, 69)):
        music.add(tt, A.glock(M(m), 1.4, 0.16))
    groove(15.0, 22.0, vel=0.26, lead=False, tiptoe=True)
    held(22.0, 4.2, (58, 62, 65), 0.32)
    held(26.0, 2.0, (53, 57, 60), 0.3)
    for i, m in enumerate((65, 69, 72, 77, 81)):
        music.add(27.8 + i * 0.1, MX.organ(M(m), 0.3, 0.32))                  # the idea arpeggio
    held(28.4, 3.6, (53, 60, 65, 69), 0.3)
    groove(32.0, 45.0, vel=0.32)
    groove(45.0, 78.0, vel=0.24, lead=False, glock_every=4)
    groove(78.0, 85.0, vel=0.22, lead=False)
    groove(85.0, 92.0, vel=0.16, lead=False, comp=False)                       # careful version
    held(85.0, 7.5, (53, 57, 60), 0.22)
    held(92.0, 3.6, (53, 60, 65, 67), 0.26)                                    # held chord as the light clicks
    held(95.4, 3.0, (53, 57, 60, 65), 0.3)
    held(98.4, 4.4, (53, 60, 65, 67, 69), 0.42)                                # THE GLOW: F add9 swell
    for i, m in enumerate((84, 88, 91, 96, 91, 88)):
        music.add(98.7 + i * 0.4, A.glock(M(m), 1.2, 0.2))
    groove(102.5, 110.0, vel=0.26, glock_every=2)
    held(110.0, 7.2, (46, 53, 58, 65), 0.28)                                   # Bb over F: thinking
    for i in range(6):
        music.add(113.6 + i * 0.55, A.woodblock(i % 2 == 0, 0.15))
    groove(117.0, 129.0, vel=0.24, lead=False)
    for i, m in enumerate((41, 43, 45, 46, 48, 50)):                           # bass walking up under the pushes
        music.add(118.3 + i * 0.62, A.pluck(M(m), 0.4, 0.5))
    held(129.0, 2.4, (48, 55, 64), 0.3)
    held(129.6, 2.6, (46, 53, 58, 62, 65), 0.34)                               # the swell starts >= 1 s early
    held(131.6, 1.9, (48, 55, 60, 64, 67), 0.4)
    held(133.0, 3.4, (41, 53, 60, 65, 69, 72), 0.5)
    for i, m in enumerate((72, 77, 81, 84, 81, 84, 89)):
        music.add(133.0 + i * 0.36, MX.organ(M(m), 0.34, 0.42))
    for i in range(8):
        music.add(133.2 + i * 0.45, A.glock(M((96, 100, 103, 108)[i % 4]), 1.0, 0.16))
    groove(136.4, 148.2, vel=0.3, glock_every=2)
    held(147.9, 2.0, (41, 53, 57, 60), 0.25)
    groove(149.5, 153.0, vel=0.24, lead=False)
    held(153.0, 6.95, (41, 53, 57, 60, 65), 0.3)                               # lullaby
    for i, (m, dd) in enumerate(((72, 1.0), (69, 1.0), (65, 1.6), (67, 1.0), (69, 2.0))):
        music.add(153.4 + sum(x[1] for x in ((72, 1.0), (69, 1.0), (65, 1.6), (67, 1.0), (69, 2.0))[:i]),
                  MX.organ(M(m), dd, 0.28))
    # ---- effects
    sfx.add(0.4, A.twinkle(0.4))
    sfx.add(0.45, peep(0.6))                                                   # hop lands
    sfx.add(1.15, A.glock(M(96), 0.8, 0.3))                                     # the heart lands on her
    for tt in (1.0, 1.4):
        sfx.add(tt, peep(0.45, 1700))
    sfx.add(4.55, A.twinkle(0.5))
    sfx.add(4.55, A.glock(M(96), 1.0, 0.35))
    sfx.add(4.8, giggle_snd(0.5, 88))
    for tt in np.arange(0.2, 6.0, 0.6):
        sfx.add(tt, scratch(0.35, 0.35, int(tt * 10)))                         # Snip sketching
    for tt in np.arange(0.0, 15.6, 0.8):
        sfx.add(tt, rustle(0.6, 0.18))                                         # polishing
    for tt in (7.0, 8.1):
        sfx.add(tt, A.glock(M(91), 0.5, 0.18))                                  # tiptoe up
    music.add(11.0, A.glock(M(108), 0.6, 0.18))                                # first star
    music.add(12.0, A.glock(M(103), 0.6, 0.12))                                # moon
    sfx.add(BREEZE, rustle(1.6, 0.8))
    sfx.add(BREEZE + 0.05, chime_ring(0.7, 2))
    sfx.add(12.8, poof(0.9))
    sfx.add(13.4, A.whoosh(0.4, 0.3))
    sfx.add(15.3, A.boop(0.35))
    sfx.add(15.8, A.chime_up(0.4, (79, 84)))
    sfx.add(16.0, A.whoosh(0.2, 0.25))                                         # cloth tucked
    for tt in (16.6, 18.0, 19.3):
        sfx.add(tt, A.woodblock(True, 0.4))
    for tt in (17.0, 18.5):
        sfx.add(tt, A.boop(0.3))
    for tt in (17.6, 18.8, 19.8):
        sfx.add(tt, giggle_snd(0.4, 84))
    sfx.add(21.5, A.boop(0.45))
    sfx.add(23.0, A.boop(0.25))
    sfx.add(TUFT_PAT, A.tap(0.35))
    sfx.add(TUFT_PAT + 0.3, A.boing(0.35, 600))
    sfx.add(26.2, A.pad([M(57), M(60), M(64)], 1.2, 0.25))                     # aww
    sfx.add(T_IDEA_SN, A.chime_up(0.8))
    for tt in np.arange(28.4, 29.9, 0.12):
        sfx.add(tt, scratch(0.12, 0.35, int(tt * 100)))
    sfx.add(T_FLIP, A.whoosh(0.3, 0.35))
    sfx.add(T_FLIP + 0.4, A.twinkle(0.4))
    sfx.add(32.9, A.glock(M(96), 0.6, 0.3))
    sfx.add(33.05, A.tap(0.35))
    sfx.add(33.45, A.tap(0.35))
    for i in range(4):
        sfx.add(33.8 + i * 0.5, A.boing(0.35, 300))
        sfx.add(34.3 + i * 0.5, A.boing(0.25, 600))
    for tt in (36.85, 37.45):
        sfx.add(tt, A.tap(0.35))
    sfx.add(36.4, giggle_snd(0.5, 79))
    sfx.add(T_TUCK, A.whoosh(0.2, 0.2))
    sfx.add(T_MARKERS, A.tap(0.4))
    sfx.add(T_MARKERS + 0.05, A.pop(0.3))
    sfx.add(T_GIVE_PIP, A.tap(0.35))
    sfx.add(T_GIVE_PIP + 0.1, peep(0.5))
    sfx.add(T_GIVE_CR, A.tap(0.35))
    for name, a, b in (("eye_l", 45.2, 46.0), ("eye_r", 47.0, 47.8), ("heart_l", 67.0, 67.9), ("heart_r", 68.2, 69.1)):
        sfx.add(a, squeak(b - a, 0.9, 2000 if "eye" in name else 2300))
    for a in np.arange(56.5, 59.5, 0.5):
        sfx.add(a, squeak(0.45, 0.9, 1800))
    for tt, (m1, m2) in ((56.5, (77, 76)), (57.2, (76, 77)), (57.8, (77, 76)), (58.4, (76, 77)), (58.9, (77, 76))):
        sfx.add(tt, MX.organ(M(m1), 0.08, 0.25))
        sfx.add(tt + 0.09, MX.organ(M(m2), 0.08, 0.25))
    sfx.add(48.0, A.twinkle(0.35))
    sfx.add(T_BONK, A.glock(M(101), 1.0, 0.7))
    sfx.add(T_BONK + 0.02, chime_ring(0.8, 5))
    sfx.add(T_BONK + 0.05, A.boing(0.4, 420))
    sfx.add(50.4, poof(0.7))
    sfx.add(51.2, giggle_snd(0.5, 88))
    sfx.add(51.4, giggle_snd(0.45, 79))
    sfx.add(53.4, A.boop(0.25))
    sfx.add(60.0, A.twinkle(0.4))
    sfx.add(62.3, A.boop(0.3))
    sfx.add(63.3, A.boop(0.4))
    sfx.add(63.8, A.tap(0.25))
    sfx.add(64.7, A.whoosh(0.3, 0.3))
    sfx.add(T_SWAP, A.tap(0.25))
    sfx.add(69.2, A.chime_up(0.6))
    for i in range(4):
        sfx.add(71.35 + i * 0.3, A.clap(0.6))
    for i in range(3):
        sfx.add(71.55 + i * 0.3, A.clap(0.5))
    sfx.add(71.1, peep(0.5))
    for i, tt in enumerate((75.0, 75.4, 75.8)):
        sfx.add(tt, A.boop(0.4 + 0.1 * i))
    sfx.add(76.6, A.boop(0.7))
    sfx.add(78.7, A.whoosh(0.25, 0.25))
    sfx.add(79.7, A.whoosh(0.5, 0.45))                                          # the hand arrives
    sfx.add(T_THUMB, A.chime_up(0.6, (84, 91)))
    sfx.add(T_PALM, A.tap(0.35))
    sfx.add(81.7, A.whoosh(0.4, 0.3))
    for tt in (T_BOX_SN, T_BOX_CR, T_BOX_PIP):
        sfx.add(tt, A.tap(0.35))
    sfx.add(84.5, A.whoosh(0.45, 0.35))
    sfx.add(85.0, A.tap(0.3))
    for tt in TOKS:
        sfx.add(tt, tok(1.0))
    sfx.add(88.2, tok(0.8))
    sfx.add(90.5, thoonk(0.6))
    sfx.add(91.4, A.tap(0.3))
    sfx.add(92.1, A.whoosh(0.3, 0.3))
    sfx.add(T_CLICK, click(0.7))
    sfx.add(T_CLICK + 0.05, A.chime_up(0.5, (91, 96, 100)))
    for i, m in enumerate((79, 84, 88)):
        sfx.add(96.0 + i * 0.4, A.glock(M(m), 1.4, 0.5))                       # eyes, heart, smile light up
    sfx.add(97.15, A.tap(0.25))
    sfx.add(97.4, thoonk(0.6))
    sfx.add(97.7, A.whoosh(0.4, 0.3))
    sfx.add(98.6, A.pad([M(65), M(69), M(72)], 1.5, 0.3))                      # aww
    sfx.add(99.4, A.twinkle(0.5))
    sfx.add(105.6, A.boop(0.35))
    sfx.add(106.2, A.boop(0.45))
    sfx.add(106.8, giggle_snd(0.6, 72))                                        # Crinkle laughs
    sfx.add(111.2, A.blow(0.3, 0.15))
    sfx.add(T_IDEA_CR, A.chime_up(0.8))
    sfx.add(116.4, A.tap(0.25))
    sfx.add(118.3, A.blow(0.6, 0.35))                                          # push 1: won't budge
    sfx.add(119.5, rumble(1.1, 0.8))
    sfx.add(120.9, rumble(1.1, 0.8))
    sfx.add(121.8, A.boop(0.5))                                                # the smile on his tummy
    sfx.add(125.0, A.boop(0.35))
    sfx.add(125.3, giggle_snd(0.5, 84))
    sfx.add(125.6, giggle_snd(0.4, 91))
    sfx.add(127.9, A.boing(0.4, 500))
    for i in range(4):
        sfx.add(128.6 + i * 0.35, MX.organ(M(72 + (i % 2) * 3), 0.2, 0.3))
    sfx.add(128.5, giggle_snd(0.6, 72))
    sfx.add(130.6, A.whoosh(0.9, 0.35))                                        # soft whoosh: the reveal
    for i in range(6):
        sfx.add(131.4 + i * 0.35, A.twinkle(0.25))
    sfx.add(136.9, A.chime_up(0.5))
    sfx.add(137.2, peep(0.5))
    for tt in (139.15, 139.85):
        sfx.add(tt, A.tap(0.3))
    sfx.add(139.0, giggle_snd(0.5, 79))
    sfx.add(143.2, A.boop(0.5))
    sfx.add(143.6, giggle_snd(0.55, 88))
    for a, b, p in WING_GAME:
        sfx.add(b, A.boop(0.45) if p == WING_TIP else A.boop(0.3))
        if p == WING_TIP:
            sfx.add(b + 0.1, giggle_snd(0.45, 88))
    for tt in (145.95, 147.35):
        sfx.add(tt + 0.2, giggle_snd(0.35, 76))
    sfx.add(T_BUMP - 0.6, A.snare_roll(0.55, 0.5))
    sfx.add(T_BUMP, A.boop(0.9))
    A.jingle(music, T_BUMP + 0.02, 1.0, ending=True)
    sfx.add(T_BUMP + 0.05, A.twinkle(0.7))
    sfx.add(T_LOW, A.boop(0.45))
    sfx.add(T_LOW + 0.05, A.twinkle(0.5))
    for i in range(5):
        sfx.add(155.4 + i * 0.45, A.whoosh(0.2, 0.08))
    sfx.add(156.5, A.pad([M(65), M(69), M(72)], 1.8, 0.2))
    # footsteps (Pip: lighter, higher pat-pats)
    for perf, vel in ((SN, 0.45), (CR, 0.5)):
        for tt in perf.footfalls():
            sfx.add(tt, A.tap(vel))
    for tt in PIP.footfalls():
        sfx.add(tt, 0.5 * A.tap(1.0)[::2])                                    # light, high pat
    for perf in (SN, CR, PIP):
        for t0, t1, n, hgt in perf.hops:
            if t1 > 0 and hgt >= 20:
                sfx.add(t1, A.tap(0.3))
    for t0, t1, n, amp in PIP.flaps:
        for k in range(n):
            sfx.add(t0 + (k + 0.5) * (t1 - t0) / n, A.whoosh(0.08, 0.12))
    return music, sfx


def build_audio(path):
    music, sfx = make_buses()
    m = A.reverb(music.normalized(), 0.22)
    s = A.reverb(sfx.normalized(), 0.08)
    nm = lambda x: x / max(1e-9, abs(x).max())  # noqa: E731
    y = 0.55 * nm(m) + 0.7 * nm(s)
    y = y / max(1.0, abs(y).max() / 0.95)
    for _ in range(3):                    # bring it near -14 LUFS here (a soft limiter keeps the peaks), so the
        A.write_wav(path, y, fade_out=0.25)   # encoder's loudnorm only trims
        lufs = _lufs(path)
        if lufs is None or abs(lufs + 14.0) < 0.4:
            break
        g = 10 ** ((-14.0 - lufs) / 20)
        y = 0.97 * np.tanh(y * g / 0.97)
    A.write_wav(path, y, fade_out=0.25)
    print("audio loudness", _lufs(path), "LUFS")


def _lufs(path):
    import re
    import subprocess
    err = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True,
                         text=True).stderr
    v = re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", err, re.M)
    return float(v[-1]) if v else None


# ---------------------------------------------------------------- numeric checks (carry-forward 2; rules card)
def _edge_pts(mask, box, cam, thresh, step=2):
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


def _head_pts_from(mask_img, cam):
    a = np.asarray(mask_img).astype(np.float32) / 255
    bb = mask_img.getbbox()
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
    ps, cr, sn = rep["pip"], rep["cr"], rep["sn"]
    faces = {"Pip": _head_pts_from(PIPA.head_mask(ps, CAM, size, grow=0), CAM),
             "Crinkle": _head_pts_from(L.head_mask(CR.a, cr, CAM, size, grow=0), CAM),
             "Snip": _head_pts_from(L.head_mask(SN.a, sn, CAM, size, grow=0), CAM)}
    beak = _ellipse(PIPA.beak_point(ps), 30 * PIPA.s, 16 * PIPA.s)
    for key, what in (("pip_heart", "heart on Pip"), ("wing_heart", "heart on Pip's wing"), ("wing", "face on Pip's wing"),
                      ("cr", "smile on Crinkle"), ("bump", "light on the paws")):
        if key in lit and lit[key][0] is not None:
            I, lay = lit[key]
            pts = _edge_pts(I, lay.box, CAM, 0.02)
            if len(pts):
                ds = ", ".join(f"{k} {_min_d(pts, v):.0f}" for k, v in faces.items())
                out.append(f"{t:.1f}s {what}: light edge to heads: {ds}; to Pip's beak {_min_d(pts, beak):.0f}")
    return out


# ---------------------------------------------------------------- the Lead's check sheet, the key sheet
CHECK = [
    (2.0, None, None, "2 s golden: the hearts on the wall (wide)"),
    (4.8, None, None, "4.8 s the heart on Pip's wing (close 1.9)"),
    (123.5, (960, 1280), 1.9, "123.5 s the smile on Crinkle's tummy (close 1.9)"),
    (133.0, None, None, "133 s the giant face (wide)"),
    (143.5, None, None, "143.5 s the smile on Pip's wing (close 2.8)"),
]

KEYS = [(1.0, "1 hop into the light"), (4.8, "2 heart on her wing"), (8.2, "3 sunset"), (10.6, "4 empty wing"),
        (12.95, "5 poof!"), (14.4, "5 hides"), (17.3, "6 peek"), (18.7, "6 peek"), (19.0, "6 Snip giggles"),
        (21.7, "6 found"), (23.2, "7 the dark wall"), (24.2, "7 hugs herself"), (25.1, "7 pat"),
        (27.9, "8 idea!"), (29.2, "8 scribble"), (31.0, "9 the plan"), (34.8, "10 dance"), (40.95, "11 red for Pip"),
        (42.55, "11 black for Crinkle"), (45.6, "13 left eye"), (47.6, "13 right eye"), (50.2, "14 bonk!"),
        (50.6, "14 poof"), (54.2, "15 ready"), (57.5, "16 the smile"), (61.0, "17 face"), (63.4, "18 me?"),
        (64.8, "18 go on!"), (67.5, "19 heart"), (68.8, "19 heart"), (71.6, "20 claps"), (75.2, "21 tilt"),
        (76.9, "21 tilt"), (80.5, "22 thumbs-up"), (81.3, "22 wait there"), (83.4, "23 to the bench"),
        (85.7, "24a tok"), (86.5, "25 ears"), (88.5, "24b holes"), (90.8, "24b lid off"), (93.1, "26 click"),
        (96.2, "27 it goes in"), (99.0, "28 THE GLOW"), (101.8, "28 pull back"), (104.0, "29 closer"),
        (106.4, "30 three smiles"), (111.2, "31 still dark"), (116.1, "32 idea"), (118.6, "33 push"),
        (120.6, "33 turn"), (122.6, "33 turned"), (123.5, "34 tummy"), (125.6, "35 they see"),
        (128.3, "36 he sees"), (131.2, "37 the wipe"), (133.0, "37 THE WOW"), (137.0, "38 Pip"),
        (139.5, "39 joy"), (142.0, "40a wing up"), (144.0, "40b face on the wing"), (146.0, "40c in"),
        (146.8, "40c out"), (149.0, "41 paw-bump"), (151.25, "41 low bump"), (156.0, "42 wave"), (158.5, "42 end")]


def contact_sheet(items, path, w=780, cols=2):
    import paperlib
    h = int(w * 1080 / 1920)
    rows = math.ceil(len(items) / cols)
    sheet = Image.new("RGB", (w * cols + 10 * (cols + 1), (h + 40) * rows + 10), (250, 248, 244))
    d = ImageDraw.Draw(sheet)
    font = paperlib.round_font(22 if w > 500 else 18)
    for i, (img, label) in enumerate(items):
        x = 10 + (i % cols) * (w + 10)
        y = 10 + (i // cols) * (h + 40)
        d.text((x + 3, y + 4), label, fill=(60, 50, 70), font=font)
        sheet.paste(img.resize((w, h), Image.LANCZOS), (x, y + 34))
    sheet.save(path)
    print("wrote", path)


def _key_one(args):
    tt, label = args
    return render_frame(tt).resize((400, 225), Image.LANCZOS).tobytes(), label


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "output"), exist_ok=True)
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
            items.append((img, label))
            lines += checks(tt, rep)
        contact_sheet(items, os.path.join(ROOT, "reviews", "ep11_check_L.png"))
        print("\n".join(lines))
    elif args == ["--keys"]:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(8) as pool:
            res = pool.map(_key_one, KEYS)
        items = [(Image.frombytes("RGB", (400, 225), b), lab) for b, lab in res]
        contact_sheet(items, os.path.join(ROOT, "reviews", "ep11_friendly_glow_keys.png"), w=400, cols=6)
    elif args == ["--cuts"]:
        print(",".join(f"{c:g}" for c in CUTS))
    elif args == ["--hires40b"]:
        if RES < 2.5:
            sys.exit("run with EP11_RES=3")
        os.makedirs(HI40B, exist_ok=True)
        for d in range(int(round(143.5 * K.DPS)), int(round(145.0 * K.DPS))):
            tq = d / K.DPS
            f = render_world(tq, d)
            c, z = shot_at(tq)
            shoot(f, c, z).convert("RGB").save(os.path.join(HI40B, f"d{d:05d}.png"))
            print("40b", d, flush=True)
    elif args == ["--render"]:
        wav = os.path.join(ROOT, "build", "ep11_audio.wav")
        build_audio(wav)
        K.render_video(os.path.abspath(__file__), os.path.join(ROOT, "output", "ep11_friendly_glow.mp4"), wav, DUR,
                       "land")
    elif args == ["--audio"]:
        build_audio(os.path.join(ROOT, "build", "ep11_audio.wav"))
    else:
        sys.exit("usage: ep11_friendly_glow.py --keys | --cuts | --still T | --check | --hires40b | --render | --audio")
