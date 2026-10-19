"""Stage kit (docs/stage_kit_proposal.md): fixed sets, camera presets, marks, spots and 16 checked moves.

A plan only picks from this menu, so framing and clearance mistakes (M26, M28, M34, M73, M74, M77) can't be written.
The designer writes the beat table through `python3 tools/stage.py` (reviews/<ep>_stage.md); every call re-checks
the whole table and refuses with the legal choices. An episode script loads the table and adds only bespoke art:

    import stage_kit as SK
    ST = SK.Stage.load("ep11k")                # reviews/ep11k_stage.md -> performers, props, shots
    SK.PROPS["lantern"] = SK.Prop(...)         # an episode prop (box, work points, paths, draw function)
    SK.export(globals(), ST)                   # frame/B/RES/name_of/head_mask/SHEET for tools/clearance_check.py
    ST.still(12.0).save(...); ST.sheet([0.5, 3.0, ...], out)

Marks (x): OFF_L -400, WL 200, A 300, B 640, C 960, D 1280, E 1600, WR 1720, OFF_R 2320 (floor 1480).
Spots: a mark ("B"), or "C.L" / "C.R": with a floor prop on C, the work spot beside it (prop half width + the
character's feet or head + 10 u); without one, a hand-over pair centred on C (both reach the pass point at 85 % of
their reach; measured from the rigs at import). Presets: landscape W 1.0x, ML/MR 1.38x, CL/CR 2.0x; vertical
VW 1.0x, VM 1.38x, VC 2.0x centred on a mark ("VM@C"), feet on the 81 % line (Shorts safe zone).
Sizes: framing (and spacing) use tools/framing_check.sizes() (pose allowance 36 u); props and hand-overs use the
rigs' own masks, measured here at import (a drift past the framing sizes raises, so it fails loudly).
Moves (beat rows "| # | t0-t1 | Who | Move | Arg |"): enter, exit, walk_to, turn, look, nod, shake, react, hop,
pick_up, carry (automatic), put_down, drop, place_on, hand_over, point, hold; "bespoke" rows (<= 2) are the old
measure path: their performer is exempt from the spacing and prop rules, never from framing. Refusals print what would be legal instead.
"""
import math
import os
import re
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import hires  # noqa: E402

if hires.RES == 1.0 and not os.environ.get("STAGE_RES1"):
    hires.set_res(2)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import acting as K  # noqa: E402
import framing_check as FC  # noqa: E402
import rig2 as R  # noqa: E402
import rig2_pip as RP  # noqa: E402
from paperlib import place  # noqa: E402

FLOOR, GROUND, MARGIN = 1480, 1492, 10.0
MARKS = {"OFF_L": -400, "WL": 200, "A": 300, "B": 640, "C": 960, "D": 1280, "E": 1600, "WR": 1720, "OFF_R": 2320}
OFF = ("OFF_L", "OFF_R")
CAST = ("Snip", "Crinkle", "Pip")
SHORT = {"Snip": "sn", "Crinkle": "cr", "Pip": "pp"}
SCALE = {n: s for n, s in {"Snip": 1.15, "Crinkle": 1.2, "Pip": 0.9}.items()}
SCALE.update(FC.bible_scales())
SIZES = FC.sizes()                      # {name: (height, left, right)} with the pose allowance
FACE = {"right": 0.5, "left": -0.5, "front": 0.0}
SPEED = {"Snip": 450.0, "Crinkle": 420.0, "Pip": 300.0}     # u/s at most for a walk
REACH_USE = 0.85                        # hand-overs and work spots use 85 % of the reach (IK slack)
BODY = ("enter", "exit", "walk_to", "turn", "hop", "pick_up", "put_down", "drop", "place_on", "hand_over", "point")
FACEMOVES = ("look", "nod", "shake", "react")
MOVES = BODY + FACEMOVES + ("hold", "bespoke")
MAX_BESPOKE = 2


class Refused(Exception):
    pass


# ---------------------------------------------------------------- presets (camera windows)
def _presets():
    p = {"W": ("land", 1.0, (0.0, 560.0, 1920.0, 1640.0))}
    w, h = 1920 / 1.38, 1080 / 1.38
    p["ML"] = ("land", 1.38, (0.0, 712.0, w, 712.0 + h))
    p["MR"] = ("land", 1.38, (1920 - w, 712.0, 1920.0, 712.0 + h))
    p["CL"] = ("land", 2.0, (0.0, 1000.0, 960.0, 1540.0))
    p["CR"] = ("land", 2.0, (960.0, 1000.0, 1920.0, 1540.0))
    for lab, z in (("VW", 1.0), ("VM", 1.38), ("VC", 2.0)):
        w, h = 1080 / z, 1920 / z
        y1 = 1920.0 if z == 1.0 else min(1920.0, FLOOR + 0.19 * h)
        for m in ("WL", "A", "B", "C", "D", "E", "WR"):
            x0 = MARKS[m] - w / 2
            if x0 >= 0 and x0 + w <= 1920:
                p[f"{lab}@{m}"] = ("vert", z, (x0, y1 - h, x0 + w, y1))
    return p


PRESETS = _presets()


def status(who, x, win, lift=0.0):
    """"in", "out" or "cut" for a standing character at x in window (x0, y0, x1, y1); lift = hop height."""
    h, l, r = SIZES[who]
    x0, y0, x1, y1 = win
    if x + r <= x0 - MARGIN or x - l >= x1 + MARGIN:
        return "out"
    if x - l < x0 + MARGIN or x + r > x1 - MARGIN:
        return "cut"
    if FLOOR - h - lift < y0 + MARGIN or FLOOR > y1 - MARGIN + 6:
        return "cut"
    return "in"


def spacing(a, b):
    """Least distance between two standing characters' centres (a left of b), framing sizes + 10 u."""
    return SIZES[a][2] + SIZES[b][1] + MARGIN


# ---------------------------------------------------------------- rig geometry (measured at import)
_PUP, _GEOM = {}, {}


def puppet(who):
    if who not in _PUP:
        _PUP[who] = (R.Puppet("snip", SCALE["Snip"]) if who == "Snip" else
                     R.Puppet("crinkle", SCALE["Crinkle"]) if who == "Crinkle" else RP.PipPuppet(SCALE["Pip"]))
    return _PUP[who]


def new_perf(who, seed, x, turn):
    cls = RP.PipPerf if who == "Pip" else R.Perf2
    return cls(puppet(who), seed=seed, x=x, y=FLOOR, turn=turn)


class _Cam(K.Cam):
    def __init__(self, x0, y0, w, h, res=None):
        self.res, self.view, self.world = res or hires.RES, "kit", (1920, 1920)
        self.ox, self.oy, self.w, self.h = x0, y0, w, h


def _mask(img):
    return np.asarray(img.getchannel("A")) > 160


def geom(who, facing):
    """Measured boxes relative to (x, FLOOR) for a still character facing -1/0/1 (world units)."""
    key = (who, facing)
    if key in _GEOM:
        return _GEOM[key]
    res = hires.RES
    cam = _Cam(-500, 500, 1000, 1100, res)
    p = new_perf(who, 0, 0.0, 0.5 * facing)
    st = p.state(0.0)
    im = Image.new("RGBA", (int(1000 * res), int(1100 * res)), (0, 0, 0, 0))
    p.a.draw(im, cam, st)
    m = _mask(im)
    ys, xs = np.nonzero(m)
    U = lambda v, o: v / res + o  # noqa: E731
    body = (U(xs.min(), -500), U(ys.min(), 500) - FLOOR, U(xs.max(), -500), U(ys.max(), 500) - FLOOR)
    feet = m[int((FLOOR - 60 - 500) * res):, :]
    fx = np.nonzero(feet.any(0))[0]
    sy = min(p.a.shoulder(st, "l")[1], p.a.shoulder(st, "r")[1])
    hm = m[:max(0, int((sy - 4 - 500) * res)), :]
    hy, hx = np.nonzero(hm)
    sh = {s: (p.a.shoulder(st, s)[0], p.a.shoulder(st, s)[1]) for s in ("l", "r")}
    g = dict(body=body, feet=(U(fx.min(), -500), U(fx.max(), -500)),
             head=(U(hx.min(), -500), U(hy.min(), 500) - FLOOR, U(hx.max(), -500), U(hy.max(), 500) - FLOOR),
             shoulder=sh, reach=(p.a.L1 + p.a.L2) * p.a.s)
    hgt, l, r = SIZES[who]
    if -body[0] > l + 5 or body[2] > r + 5 or -body[1] > hgt + 5:
        raise RuntimeError(f"stage_kit: {who} measures {body} but framing_check.sizes() says {SIZES[who]}: "
                           "re-measure framing_check.MEASURED before using the kit (size drift)")
    _GEOM[key] = g
    return g


def _reach_band(who, facing):
    g = geom(who, facing)
    side = "r" if facing >= 0 else "l"
    sx, sy = g["shoulder"][side]
    return sx, sy, g["reach"] * REACH_USE


def head_bottom(who):
    """The lowest row of the head as tools/clearance_check sees it (everything above the shoulders - 4 u)."""
    return min(geom(who, 1)["shoulder"]["l"][1], geom(who, 1)["shoulder"]["r"][1]) - 4


def handover_distance(a, b, top=10.0):
    """(centre distance, pass height, pass offset from a) for a (left, facing right) and b (right, facing left);
    the pass point sits low enough that a held prop reaching `top` u above the paw stays 10 u under both heads."""
    ax, ay, ar = _reach_band(a, 1)
    bx, by, br = _reach_band(b, -1)
    lo, hi = max(ay - ar, by - br), min(ay + ar, by + br)
    lo = max(lo, max(head_bottom(a), head_bottom(b)) + MARGIN + top)
    if lo >= hi:
        return None
    H = lo
    ra = ax + math.sqrt(max(0.0, ar * ar - (H - ay) ** 2))
    rb = -bx + math.sqrt(max(0.0, br * br - (H - by) ** 2))
    clear = geom(a, 1)["body"][2] - geom(b, -1)["body"][0] + MARGIN
    D = ra + rb
    if D < clear:
        return None
    return D, H, ra


# ---------------------------------------------------------------- props and sets
class Prop:
    """A prop: box (w, h) standing on its base; points {name: (dx, dy)} and paths {name: f -> (dx, dy)} from the
    base for point(); draw(img, cam, base, t, holder) draws it (base = world point); held: tip length when held."""

    def __init__(self, name, w, h, draw=None, points=None, paths=None, tip=0.0, front=False, base_y=GROUND,
                 hold_box=None, carry=True):
        self.name, self.w, self.h, self.draw_fn, self.carry = name, w, h, draw, carry
        self.hold_box = hold_box or (-w / 2, -h / 2, w / 2, h / 2)      # around the paw while held
        self.points, self.paths, self.tip, self.front, self.base_y = points or {}, paths or {}, tip, front, base_y


_MK = {}


def _draw_marker(img, cam, base, t, held):
    if "spr" not in _MK:
        _MK["spr"] = RP.marker_sprite(body=(96, 170, 236), ink=(40, 36, 44), scale=1.1)
    ang = held[1] if held else 90.0
    place(img, _MK["spr"], cam.S(base), angle=ang, shadow=False)


def _draw_ball(img, cam, base, t, held):
    d = ImageDraw.Draw(img)
    (x, y), r = cam.S((base[0], base[1] - 40)), 40 * cam.res
    d.ellipse([x - r, y - r, x + r, y + r], fill=(222, 72, 64), outline=(70, 56, 50), width=int(3 * cam.res))


def _draw_block(img, cam, base, t, held):
    d = ImageDraw.Draw(img)
    (x, y), r = cam.S((base[0], base[1] - 35)), 35 * cam.res
    d.rectangle([x - r, y - r, x + r, y + r], fill=(246, 200, 60), outline=(70, 56, 50), width=int(3 * cam.res))


LANTERN_STROKES = {"fn": lambda t: {}, "lit": lambda t: 0.0}     # an episode sets these (bespoke art)


def _lantern():
    import props_lantern as PL
    if "lan" not in _MK:
        _MK["lan"] = PL.Lantern()
    return PL, _MK["lan"]


def _draw_lantern(img, cam, base, t, held):
    PL, lan = _lantern()
    strokes, lit = LANTERN_STROKES["fn"](t), LANTERN_STROKES["lit"](t)
    off = (base[0] - PL.BASE[0], base[1] - PL.BASE[1])
    at = cam.S((PL.BASE[0] + off[0], PL.BASE[1] + off[1]))
    place(img, lan.paper(strokes), at, shadow=False)
    if lit > 0:
        place(img, lan.lit(strokes, lit), at, shadow=False)


def _lantern_prop():
    import props_lantern as PL
    bx, by = PL.BASE
    pts = {n: (lambda n: (lambda f: (PL.tip_world(n, f)[0] - bx, PL.tip_world(n, f)[1] - by)))(n) for n in PL.PATHS}
    mids = {n: fn(0.5) for n, fn in pts.items()}
    mids["ring"] = (PL.RING_WORLD[0] - bx, PL.RING_WORLD[1] - by)
    return Prop("lantern", 240, 200, _draw_lantern, points=mids, paths=pts, base_y=by, carry=False)


PROPS = {"marker": Prop("marker", 24, 60, _draw_marker, tip=RP.MARKER_TIP * 1.1, hold_box=(-12, -10, 12, 52)),
         "ball": Prop("ball", 80, 80, _draw_ball), "block": Prop("block", 70, 70, _draw_block),
         "lantern": _lantern_prop()}


class Set:
    def __init__(self, name, rows, blocked=(), spots=None):
        self.name, self.rows, self.blocked, self.spots = name, rows, set(blocked), spots or {}
        self._cache = {}

    def background(self, cam, t, light=None):
        if self.name == "porch":
            import props_porch as P
            key = ("porch", cam.ox, cam.oy, cam.w, cam.h, cam.res)
            if key not in self._cache:
                self._cache[key] = P.Porch(cam)
            return self._cache[key].background(light if light is not None else t).convert("RGBA")
        import ep12_rough as E
        if "pr" not in self._cache:
            self._cache["pr"] = E.background()
        r = cam.res
        return self._cache["pr"].crop((int(cam.ox * r), int((cam.oy - E.LAND_Y0) * r),
                                       int((cam.ox + cam.w) * r), int((cam.oy - E.LAND_Y0 + cam.h) * r)))

    def front(self, img, cam, t, light=None):
        if self.name == "porch":
            key = ("porch", cam.ox, cam.oy, cam.w, cam.h, cam.res)
            self._cache[key].front(img, light if light is not None else t)


SETS = {"porch": Set("porch", (0, 1920), blocked=("E", "WR", "OFF_R"), spots={"bench": (470, 1370)}),
        "playroom": Set("playroom", (560, 1640), spots={"box_top": (390, 1340), "shelf_red": (1520, 1300),
                                                        "shelf_blue": (1670, 1300), "shelf_yellow": (1820, 1300)})}


# ---------------------------------------------------------------- the table
def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _span(s):
    a, b = re.split(r"\s*[-–]\s*", s.strip())
    return float(a), float(b)


class Table:
    """reviews/<ep>_stage.md: header, start (cast and props at 0 s), beats and shots."""

    def __init__(self, ep, set_name="porch", view="vert", light=None):
        self.ep, self.set, self.view, self.light = ep, set_name, view, light
        self.start = {}                    # who/prop -> (at, facing)
        self.beats = []                    # (t0, t1, who, move, arg)
        self.shots = []                    # (t0, t1, preset)

    @staticmethod
    def path(ep):
        return os.path.join(ROOT, "reviews", f"{ep}_stage.md")

    @classmethod
    def load(cls, ep, path=None):
        text = open(path or cls.path(ep), encoding="utf-8").read()
        hd = re.search(r"Set:\s*(\w+)\s*·\s*View:\s*(\w+)(?:\s*·\s*Light:\s*([\d.]+))?", text)
        t = cls(ep, hd.group(1), hd.group(2), float(hd.group(3)) if hd.group(3) else None)
        sec = None
        for line in text.splitlines():
            if line.startswith("## "):
                sec = line[3:].split()[0].lower()
                continue
            if not line.startswith("|") or re.match(r"^\|\s*(#|Who|-)", line):
                continue
            c = _cells(line)
            if sec == "start":
                t.start[c[0]] = (c[1], c[2] or "front")
            elif sec == "beats":
                t.beats.append((*_span(c[1]), c[2], c[3], c[4]))
            elif sec == "shots" and "." not in c[0]:
                t.shots.append((*_span(c[1]), c[5]))
        return t

    def save(self, path=None, rows=None):
        L = [f"# {self.ep} stage table (written by tools/stage.py; change it only through stage.py)", "",
             f"Set: {self.set} · View: {self.view}" + (f" · Light: {self.light:g}" if self.light is not None else ""),
             "", "## Start (0.0 s)", "", "| Who | At | Facing |", "|---|---|---|"]
        L += [f"| {w} | {a} | {f} |" for w, (a, f) in self.start.items()]
        L += ["", "## Beats", "", "| # | Time (s) | Who | Move | Arg |", "|---|---|---|---|---|"]
        for i, (t0, t1, w, m, a) in enumerate(sorted(self.beats, key=lambda b: (b[0], b[2])), 1):
            L.append(f"| {i} | {t0:g}-{t1:g} | {w} | {m} | {a} |")
        L += ["", "## Shots", "", "Checked by stage.py and by tools/framing_check.py (one row per still stretch).", "",
              "| # | Time (s) | Shot | Whole in frame | At | Preset |", "|---|---|---|---|---|---|"]
        L += rows if rows is not None else []
        with open(path or self.path(self.ep), "w", encoding="utf-8") as f:
            f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- simulation (arithmetic only)
class Sim:
    """Positions, facing, holders and hops over time, from a table; problems() lists every broken rule."""

    def __init__(self, table):
        self.t = table
        self.st = SETS[table.set]
        self.cast = [w for w in table.start if w in CAST]
        self.props = [p for p in table.start if p not in CAST]
        self.end = max([b[1] for b in table.beats] + [s[1] for s in table.shots] + [0.0])
        self.errors = []
        self._build()

    # --- spots
    def floor_prop_at(self, mark, t):
        for p in self.props:
            at = self.prop_where(p, t)
            if at == ("floor", mark):
                return p
        return None

    def spot_x(self, who, spot, t, partner=None):
        if spot in MARKS:
            if spot in self.st.blocked:
                raise Refused(f"{spot} is off the {self.st.name} set (blocked: {', '.join(sorted(self.st.blocked))})")
            return MARKS[spot]
        m = re.match(r"^([A-E]|WL|WR)\.(L|R)$", spot or "")
        if not m:
            raise Refused(f"'{spot}' is not a mark or spot: use {', '.join(MARKS)} or <mark>.L / <mark>.R")
        mk, side = m.groups()
        M = MARKS[mk]
        f = 1 if side == "L" else -1
        prop = self.floor_prop_at(mk, t)
        if prop:
            P = PROPS[prop]
            g = geom(who, f)
            feet = g["feet"][1] if f > 0 else -g["feet"][0]
            head = (g["head"][2] if f > 0 else -g["head"][0]) if FLOOR + g["head"][3] > P.base_y - P.h - MARGIN else 0
            return M - f * (P.w / 2 + max(feet, head) + MARGIN)
        other = partner or self.who_at(f"{mk}.{'R' if side == 'L' else 'L'}", t, exclude=who)
        if not other:
            raise Refused(f"{spot} is a hand-over spot: its partner must stand on {mk}.{'R' if side == 'L' else 'L'} "
                          f"first (or put a floor prop on {mk} to make it a work spot)")
        a, b = (who, other) if side == "L" else (other, who)
        ho = handover_distance(a, b, self.pair_top())
        if not ho:
            raise Refused(f"no hand-over pair for {a} (left) and {b} (right): their reach bands don't meet")
        return M - f * ho[0] / 2

    def pair_top(self):
        return max([-PROPS[p].hold_box[1] for p in self.props if PROPS[p].carry] + [10.0])

    def who_at(self, spot, t, exclude=None):
        for w in self.cast:
            if w != exclude and self.spot_of(w, t) == spot:
                return w
        return None

    # --- timeline
    def _build(self):
        self.track = {w: [(0.0, None, self.t.start[w][0])] for w in self.cast}   # (t, x or None, spot)
        self.face = {w: [(0.0, FACE.get(self.t.start[w][1], 0.0))] for w in self.cast}
        self.hold = {p: [(0.0, self.t.start[p][0])] for p in self.props}         # (t, where)
        self.hops, self.points, self.bespoke = {w: [] for w in self.cast}, [], []
        self.walks = {w: [] for w in self.cast}
        for b in sorted(self.t.beats, key=lambda b: (b[0], b[2])):
            try:
                self._apply(*b)
            except Refused as e:
                self.errors.append(f"beat {b[0]:g}-{b[1]:g} {b[2]} {b[3]} {b[4]}: {e}")

    def spot_of(self, who, t):
        s = self.track[who][0][2]
        for tt, _, sp in self.track[who]:
            if tt <= t + 1e-9:
                s = sp
        return s

    def x(self, who, t):
        for t0, t1, x0, x1 in self.walks[who]:
            if t0 <= t <= t1:
                return x0 + (x1 - x0) * (t - t0) / (t1 - t0)
        x = None
        for tt, xx, sp in self.track[who]:
            if tt <= t + 1e-9:
                x = xx if xx is not None else self._x0(who)
        return x

    def _x0(self, who):
        sp = self.t.start[who][0]
        if not hasattr(self, "_x0c"):
            self._x0c = {}
        if who not in self._x0c:
            self._x0c[who] = self.spot_x(who, sp, 0.0)
        return self._x0c[who]

    def facing(self, who, t):
        v = 0.0
        for tt, f in self.face[who]:
            if tt <= t + 1e-9:
                v = f
        return v

    def prop_where(self, p, t):
        """("floor", mark) / ("spot", name) / ("held", who)."""
        w = self.hold[p][0][1]
        for tt, ww in self.hold[p]:
            if tt <= t + 1e-9:
                w = ww
        if w in CAST:
            return ("held", w)
        if w.startswith("spot:"):
            return ("spot", w[5:])
        return ("floor", w)

    def holding(self, who, t):
        return [p for p in self.props if self.prop_where(p, t) == ("held", who)]

    def lift(self, who, t):
        return max([40 * SCALE[who] for a, b in self.hops[who] if a - 1e-9 <= t <= b + 1e-9] + [0.0])

    def on_stage(self, who, t):
        x = self.x(who, t)
        return -200 < x < 2120

    def _apply(self, t0, t1, who, move, arg):
        if move not in MOVES:
            raise Refused(f"unknown move '{move}': use {', '.join(MOVES)}")
        if who not in self.cast and move != "bespoke":
            raise Refused(f"{who} is not in the start table ({', '.join(self.cast)})")
        if t1 <= t0:
            raise Refused("the end time must be after the start")
        a = arg.split()
        if move == "bespoke":
            self.bespoke.append((t0, t1, who, arg))
            if len(self.bespoke) > MAX_BESPOKE:
                raise Refused(f"more than {MAX_BESPOKE} bespoke beats: stage the rest with kit moves")
            return
        if move in ("enter", "exit", "walk_to"):
            if move == "exit":
                a = [a[0] if a else ("OFF_L" if self.x(who, t0) < 960 else "OFF_R")]
            if move == "enter" and self.spot_of(who, t0) not in OFF:
                raise Refused(f"{who} is on stage at {t0:g}: enter starts from OFF_L / OFF_R (use walk_to)")
            if move == "exit" and a[0] not in OFF:
                raise Refused("exit goes to OFF_L or OFF_R")
            if move == "walk_to" and a[0] in OFF:
                raise Refused("walking off stage is 'exit'")
            if self.holding(who, t0) and any(self.prop_where(p, t0)[0] == "floor" for p in self.props) and False:
                pass
            x0 = self.x(who, t0)
            x1 = self.spot_x(who, a[0], t1)
            if abs(x1 - x0) / (t1 - t0) > SPEED[who] and move == "walk_to":
                raise Refused(f"{abs(x1 - x0):.0f} u in {t1 - t0:g} s is faster than {SPEED[who]:g} u/s: "
                              f"give it at least {abs(x1 - x0) / SPEED[who]:.1f} s")
            if abs(x1 - x0) > 1:
                self.face[who].append((t0, 0.5 if x1 > x0 else -0.5))
                self.walks[who].append((t0, t1, x0, x1))
            self.track[who].append((t1, x1, a[0]))
            return
        if move == "turn":
            if not a or a[0] not in FACE:
                raise Refused("turn takes left, right or front")
            self.face[who].append((t0, FACE[a[0]]))
            return
        if move in ("look", "nod", "shake", "hold"):
            if move == "look" and (not a or a[0] not in list(self.cast) + self.props + ["camera", "up", "down"]):
                raise Refused(f"look at one of {', '.join(list(self.cast) + self.props)}, camera, up or down")
            if move in ("nod", "shake") and not 0.3 <= t1 - t0 <= 1.5:
                raise Refused(f"{move} lasts 0.3-1.5 s")
            return
        if move == "react":
            if not a or a[0] not in R.EMOTES:
                raise Refused(f"react takes one of {', '.join(R.EMOTES)}")
            if t1 - t0 < 1.0:
                raise Refused("a reaction is held at least 1.0 s (key actions >= 1.0 s)")
            return
        if move == "hop":
            self.hops[who].append((t0, t1))
            return
        f = self.facing(who, t0)
        if move == "pick_up":
            p = a[0] if a else ""
            if p not in self.props or not PROPS[p].carry:
                raise Refused(f"no prop '{p}' to pick up ({', '.join(q for q in self.props if PROPS[q].carry)})")
            if self.holding(who, t0):
                raise Refused(f"{who} already holds {self.holding(who, t0)[0]}")
            wh = self.prop_where(p, t0)
            pt = self._prop_point(p, wh, t0)
            self._need_reach(who, t0, pt, 0.0)
            self._need_clear(who, t0, p, pt)
            self.hold[p].append(((t0 + t1) / 2, who))
            return
        if move in ("put_down", "place_on", "drop"):
            held = self.holding(who, t0)
            if not held:
                raise Refused(f"{who} holds nothing at {t0:g}")
            p = held[0]
            if move == "drop":
                x = self.x(who, t0) + f * (geom(who, 1 if f >= 0 else -1)["reach"] * 0.8)
                self._clear_floor(p, x, t0, t1, who)
                self.hold[p].append((t0, f"x:{x:.0f}"))
                return
            if move == "place_on":
                if not a or a[0] not in self.st.spots:
                    raise Refused(f"place_on takes a set spot: {', '.join(self.st.spots) or 'none on this set'}")
                self._need_reach(who, t0, self.st.spots[a[0]], 0.0)
                self._need_clear(who, t0, p, self.st.spots[a[0]])
                self.hold[p].append(((t0 + t1) / 2, "spot:" + a[0]))
                return
            mk = a[0] if a else ""
            if mk not in MARKS or mk in OFF:
                raise Refused("put_down takes a mark (A-E, WL, WR): the prop stands on it")
            x = MARKS[mk]
            self._clear_floor(p, x, t0, t1, who)
            self._need_reach(who, t0, (x, PROPS[p].base_y - PROPS[p].h), 0.0)
            self.hold[p].append(((t0 + t1) / 2, mk))
            return
        if move == "hand_over":
            if len(a) < 2 or a[1] not in self.cast:
                raise Refused("hand_over takes '<prop> <receiver> [take]'")
            p, rcv = a[0], a[1]
            if self.prop_where(p, t0) != ("held", who):
                raise Refused(f"{who} doesn't hold {p} at {t0:g}")
            if self.holding(rcv, t0):
                raise Refused(f"{rcv}'s paws are full")
            s1, s2 = self.spot_of(who, t0), self.spot_of(rcv, t0)
            m1, m2 = re.match(r"^(\w+)\.(L|R)$", s1 or ""), re.match(r"^(\w+)\.(L|R)$", s2 or "")
            if not (m1 and m2 and m1.group(1) == m2.group(1) and m1.group(2) != m2.group(2)
                    and not self.floor_prop_at(m1.group(1), t0)):
                raise Refused(f"a hand-over needs a pair: {who} and {rcv} on <mark>.L and <mark>.R with nothing "
                              f"on the mark (now {s1} and {s2})")
            fl = 0.5 if m1.group(2) == "L" else -0.5
            if self.facing(who, t0) != fl or self.facing(rcv, t0) != -fl:
                raise Refused(f"{who} and {rcv} must face each other (turn first)")
            self.hold[p].append((t0 + 0.55 * (t1 - t0), rcv))
            return
        if move == "point":
            tgt = a[0] if a else ""
            held = self.holding(who, t0)
            tip = PROPS[held[0]].tip if held else 0.0
            for pt in self._targets(tgt, t0):
                self._need_reach(who, t0, pt, tip)
            self.points.append((t0, t1, who, tgt))
            return

    def _prop_point(self, p, wh, t):
        P = PROPS[p]
        if wh[0] == "spot":
            return self.st.spots[wh[1]]
        if wh[0] == "floor":
            x = MARKS[wh[1]] if wh[1] in MARKS else float(wh[1][2:])
            return (x, P.base_y - P.h)
        raise Refused(f"{p} is held by {wh[1]}: use hand_over")

    def _targets(self, tgt, t):
        if tgt in self.cast:
            return [(self.x(tgt, t), FLOOR - SIZES[tgt][0] * 0.4)]
        if tgt in MARKS:
            return [(MARKS[tgt], FLOOR - 200)]
        pn, _, part = tgt.partition(".")
        if pn not in self.props:
            raise Refused(f"point at a character, a mark or <prop>.<point|path> ({', '.join(self.props)})")
        P = PROPS[pn]
        wh = self.prop_where(pn, t)
        bx, by = (MARKS[wh[1]], P.base_y) if wh[0] == "floor" else self._prop_point(pn, wh, t)
        if part in P.points:
            return [(bx + P.points[part][0], by + P.points[part][1])]
        if part in P.paths:
            return [(bx + P.paths[part](f)[0], by + P.paths[part](f)[1]) for f in np.linspace(0, 1, 6)]
        if not part:
            return [(bx, by - P.h / 2)]
        raise Refused(f"{pn} has points {', '.join(P.points) or '-'} and paths {', '.join(P.paths) or '-'}")

    def _need_reach(self, who, t, pt, tip):
        f = self.facing(who, t)
        side = 1 if pt[0] >= self.x(who, t) else -1
        if f and side != (1 if f > 0 else -1):
            raise Refused(f"{who} faces {'right' if f > 0 else 'left'}: turn to reach ({pt[0]:.0f}, {pt[1]:.0f})")
        sx, sy, r = _reach_band(who, side)
        d = math.hypot(pt[0] - (self.x(who, t) + sx), pt[1] - sy)
        if d > r / REACH_USE * 0.95 + tip:
            raise Refused(f"({pt[0]:.0f}, {pt[1]:.0f}) is {d:.0f} u from {who}'s shoulder; the reach is "
                          f"{r / REACH_USE * 0.95 + tip:.0f}: stand closer (a work spot <mark>.L/.R)")

    def _need_clear(self, who, t, p, top):
        """A prop standing with its top at `top` must stay 10 u from every head (clearance_check's head rows)."""
        P = PROPS[p]
        x0, x1, y0, y1 = top[0] - P.w / 2, top[0] + P.w / 2, top[1], top[1] + P.h
        for w in self.cast:
            if not self.on_stage(w, t):
                continue
            g = geom(w, 1 if self.facing(w, t) >= 0 else -1)
            hx0, hx1, hy1 = self.x(w, t) + g["head"][0], self.x(w, t) + g["head"][2], head_bottom(w)
            if x0 < hx1 + MARGIN and hx0 - MARGIN < x1 and y0 < hy1 + MARGIN:
                raise Refused(f"{p} at ({top[0]:.0f}, {top[1]:.0f}) would sit by {w}'s head (bottom y {hy1:.0f}): "
                              "use another spot or mark")

    def _clear_floor(self, p, x, t0, t1, who):
        P = PROPS[p]
        for w in self.cast:
            for tt in (t0, t1):
                fx0, fx1 = self.feet_box(w, tt)
                if fx0 - MARGIN < x + P.w / 2 and x - P.w / 2 < fx1 + MARGIN:
                    raise Refused(f"{p} at x {x:.0f} would be on or by {w}'s feet ({fx0:.0f}-{fx1:.0f})")

    def feet_box(self, w, t):
        f = self.facing(w, t)
        g = geom(w, 1 if f > 0 else -1 if f < 0 else 0)
        x = self.x(w, t)
        walking = any(a <= t <= b for a, b, *_ in self.walks[w])
        pad = 95 * SCALE[w] / 2 if walking else 0.0
        return x + g["feet"][0] - pad, x + g["feet"][1] + pad

    # --- the rules, sampled
    def times(self, t0=0.0, t1=None):
        t1 = self.end if t1 is None else t1
        ts = set(np.round(np.arange(t0, t1 + 1e-9, 0.1), 3))
        for b in self.t.beats:
            ts |= {b[0], b[1]}
        return sorted(t for t in ts if t0 - 1e-9 <= t <= t1 + 1e-9)

    def problems(self):
        out = list(self.errors)
        skip = lambda t, w: any(a - 1e-9 <= t <= b + 1e-9 and who == w for a, b, who, _ in self.bespoke)  # noqa
        busy = {}
        for t0, t1, w, m, a in self.t.beats:
            k = "face" if m in FACEMOVES else "body"
            if m in ("hold", "bespoke"):
                continue
            for u0, u1, m2 in busy.get((w, k), []):
                if t0 < u1 - 1e-9 and u0 < t1 - 1e-9:
                    out.append(f"beat {t0:g}-{t1:g} {w} {m}: overlaps {w} {m2} {u0:g}-{u1:g}")
            busy.setdefault((w, k), []).append((t0, t1, m))
        seen = set()
        for t in self.times():
            on = [w for w in self.cast if self.on_stage(w, t) and not skip(t, w)]
            xs = sorted((self.x(w, t), w) for w in on)
            for (xa, a), (xb, b) in zip(xs, xs[1:]):
                pair = (re.match(r"^(\w+)\.L$", self.spot_of(a, t) or "") and
                        self.spot_of(b, t) == self.spot_of(a, t)[:-1] + "R" and
                        not any(a2 <= t <= b2 for a2, b2, *_ in self.walks[a] + self.walks[b]))
                need = (geom(a, 1)["body"][2] - geom(b, -1)["body"][0] + MARGIN) if pair else spacing(a, b)
                if xb - xa < need - 0.5:
                    msg = f"{t:.1f} s: {a} (x {xa:.0f}) and {b} (x {xb:.0f}) are {xb - xa:.0f} u apart; need {need:.0f}"
                    if (a, b, "sp") not in seen:
                        out.append(msg + (" (leave one empty mark between them, or use a hand-over pair)"))
                        seen.add((a, b, "sp"))
            for p in self.props:
                wh = self.prop_where(p, t)
                if wh[0] != "floor":
                    continue
                P = PROPS[p]
                x = MARKS[wh[1]] if wh[1] in MARKS else float(wh[1][2:])
                for w in on:
                    fx0, fx1 = self.feet_box(w, t)
                    if fx0 - MARGIN < x + P.w / 2 and x - P.w / 2 < fx1 + MARGIN and (p, w) not in seen:
                        out.append(f"{t:.1f} s: {w}'s feet ({fx0:.0f}-{fx1:.0f}) within {MARGIN:g} u of {p} "
                                   f"({x - P.w / 2:.0f}-{x + P.w / 2:.0f}): stand on {wh[1]}.L / {wh[1]}.R")
                        seen.add((p, w))
        for i, (s0, s1, pre) in enumerate(self.t.shots):
            out += [f"shot {i + 1} {pre} {s0:g}-{s1:g}: {m}" for m in self.shot_problems(s0, s1, pre)]
        return out

    def shot_problems(self, s0, s1, pre):
        if pre not in PRESETS:
            return [f"unknown preset (legal: {', '.join(PRESETS)})"]
        view, z, win = PRESETS[pre]
        if view != self.t.view:
            return [f"{pre} is a {view} preset; this table is {self.t.view}"]
        if win[1] < self.st.rows[0] or win[3] > self.st.rows[1]:
            return [f"{pre} shows rows the {self.st.name} set doesn't have ({self.st.rows[0]}-{self.st.rows[1]})"]
        out, seen = [], set()
        for t in self.times(s0, s1):
            for w in self.cast:
                if not self.on_stage(w, t) or w in seen or self.entering(w, t):
                    continue
                if status(w, self.x(w, t), win, self.lift(w, t)) == "cut":
                    lift = " (hopping)" if self.lift(w, t) else ""
                    out.append(f"{w} at x {self.x(w, t):.0f}{lift} is cut at {t:.1f} s")
                    seen.add(w)
        return out

    def entering(self, w, t):
        """Inside an enter or exit beat: crossing the frame edge is the point of it."""
        return any(b[2] == w and b[3] in ("enter", "exit") and b[0] - 1e-9 <= t <= b[1] + 1e-9 for b in self.t.beats)

    def legal_presets(self, s0, s1):
        return [p for p, (v, z, w) in PRESETS.items() if v == self.t.view and not self.shot_problems(s0, s1, p)]

    def framing_rows(self):
        """Shot rows for tools/framing_check.py: one per stretch where nobody moves."""
        rows = []
        for i, (s0, s1, pre) in enumerate(self.t.shots, 1):
            view, z, (x0, y0, x1, y1) = PRESETS[pre]
            cuts = sorted({s0, s1} | {e for b in self.t.beats if b[3] in ("walk_to", "enter", "exit")
                                      for e in (b[0], b[1]) if s0 < e < s1})
            for j, (a, b) in enumerate(zip(cuts, cuts[1:])):
                for tt in ((a, b) if any(w[0] < b and a < w[1] for v in self.walks.values() for w in v) else (a,)):
                    on = [w for w in self.cast if self.on_stage(w, tt)]
                    whole = [w for w in on if status(w, self.x(w, tt), (x0, y0, x1, y1)) == "in"]
                    out = [w for w in on if w not in whole]
                    cell = ", ".join(whole) + (f"; {', '.join(out)} out" if out else "")
                    at = ", ".join(f"{w} x {self.x(w, tt):.0f}" for w in on)
                    num = f"{i}" if not rows or rows[-1].split("|")[1].strip().split(".")[0] != str(i) else \
                        f"{i}.{sum(1 for r in rows if r.split('|')[1].strip().split('.')[0] == str(i))}"
                    rows.append(f"| {num} | {a:g}-{b:g} | {pre} {z:g}x x {x0:.0f}-{x1:.0f} y {y0:.0f}-{y1:.0f} | "
                                f"{cell or '-'} | {at or '-'} | {pre} |")
        return rows


# ---------------------------------------------------------------- performances (the moves, on the rigs)
class Stage:
    def __init__(self, table):
        self.table = table
        self.sim = Sim(table)
        self.set = SETS[table.set]
        self.perfs = {}
        self.post, self.extra_back, self.extra_front = None, None, None
        self._program()

    @classmethod
    def load(cls, ep, path=None):
        return cls(Table.load(ep, path))

    def _program(self):
        S = self.sim
        for i, w in enumerate(S.cast):
            p = new_perf(w, i + 1, S._x0(w), S.facing(w, 0.0))
            p.acting(breath=True, blink="soft")
            self.perfs[w] = p
        for t0, t1, w, m, a in sorted(self.table.beats, key=lambda b: (b[0], b[2])):
            if w not in self.perfs or m in ("hold", "bespoke"):
                continue
            p, a = self.perfs[w], a.split()
            f = S.facing(w, t0 + 1e-6)
            if m in ("enter", "exit", "walk_to"):
                x1 = S.x(w, t1)
                if abs(x1 - p._num("x", t0)) > 1:
                    p.to(t0, min(t1, t0 + 0.2), "io", turn=0.5 if x1 > p._num("x", t0) else -0.5)
                    p.walk(t0, t1, x1)
            elif m == "turn":
                p.to(t0, t1, "io", turn=FACE[a[0]], hturn=0.0)
            elif m == "look":
                tgt = a[0]
                tx = {"camera": None, "up": None, "down": None}.get(tgt, "x")
                if tx is None:
                    p.to(t0, t1, "io", hturn=-p._num("turn", t0), look_x=0, look_y={"up": -8, "down": 8}.get(tgt, 0))
                else:
                    pt = S._targets(tgt, t0)[0]
                    d = 1 if pt[0] > S.x(w, t0) else -1
                    want = max(-0.5, min(0.5, 0.5 * d)) - p._num("turn", t0)
                    dy = max(-8, min(8, (pt[1] - (FLOOR - SIZES[w][0] * 0.75)) / 25))
                    p.to(t0, t1, "io", hturn=want, look_x=6 * d, look_y=dy)
            elif m == "nod":
                mid = (t0 + t1) / 2
                p.to(t0, mid, "io", head_dy=10 * SCALE[w], tilt=3).to(mid, t1, "io", head_dy=0, tilt=0)
            elif m == "shake":
                base = p._num("hturn", t0)
                n = 4
                for k in range(n):
                    a0, a1 = t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n
                    v = base + (0.2 if k % 2 == 0 else -0.2) if k < n - 1 else base
                    p.to(a0, a1, "io", hturn=max(-0.5 - p._num("turn", t0), min(0.5 - p._num("turn", t0), v)))
            elif m == "react":
                p.emote(t0, min(t1, t0 + 0.3), a[0])
            elif m == "hop":
                p.hop(t0, t1, max(1, int(round((t1 - t0) / 0.4))), 40 * SCALE[w])
            elif m in ("pick_up", "put_down", "place_on", "drop", "hand_over", "point"):
                self._arm_move(p, w, t0, t1, m, a, f)
        for w, p in self.perfs.items():           # carry: arms to the carry pose whenever a prop arrives
            for pn in S.props:
                for tt, ww in S.hold[pn][1:]:
                    if ww == w and not any(b[0] <= tt + 0.3 <= b[1] and b[2] == w and b[3] == "point"
                                           for b in self.table.beats):
                        side = self.hand(w, tt + 0.01)
                        p.reach(tt, tt + 0.3, side, self.carry_point(w, tt + 0.3))

    def hand(self, w, t):
        return "r" if self.sim.facing(w, t) >= 0 else "l"

    def carry_point(self, w, t):
        f = 1 if self.sim.facing(w, t) >= 0 else -1
        sx, sy, r = _reach_band(w, f)
        return self.sim.x(w, t) + sx + f * 0.5 * r, sy + 0.75 * r

    def _arm_move(self, p, w, t0, t1, m, a, f):
        S, side = self.sim, self.hand(w, t0)
        mid = (t0 + t1) / 2
        if m == "point":
            held = S.holding(w, t0)
            pts = S._targets(a[0], t0)
            tip = PROPS[held[0]].tip if held else 0.0
            n = len(pts)
            for k, pt in enumerate(pts):
                ta = t0 + (t1 - t0) * (0.3 if n > 1 else 1.0) * (k / max(1, n - 1)) if n > 1 else t0
                tb = t0 + 0.3 * (t1 - t0) if k == 0 else t0 + 0.3 * (t1 - t0) + 0.7 * (t1 - t0) * k / (n - 1)
                p.reach(ta if k else t0, tb, side, self._paw_for(w, t0, pt, tip))
            return
        if m == "hand_over":
            rcv = a[1]
            q = self.perfs[rcv]
            ho = handover_distance(*((w, rcv) if f > 0 else (rcv, w)), S.pair_top())
            left = w if f > 0 else rcv
            P = (S.x(left, t0) + ho[2], ho[1])
            take = len(a) > 2 and a[2] == "take"
            g1, r1 = (0.45, 0.35) if take else (0.35, 0.45)
            p.reach(t0, t0 + g1 * (t1 - t0), side, P)
            q.reach(t0, t0 + r1 * (t1 - t0), self.hand(rcv, t0), P)
            p.to(t0 + 0.6 * (t1 - t0), t1, "io", **{f"arm_{side}": 10 if side == "r" else -10,
                                                   f"elb_{side}": -14 if side == "r" else 14})
            return
        if m == "pick_up":
            pt = S._prop_point(a[0], S.prop_where(a[0], t0), t0)
            p.reach(t0, mid, side, pt)
            return
        held = S.holding(w, t0)[0]
        if m == "drop":
            return
        pt = S.st.spots[a[0]] if m == "place_on" else (MARKS[a[0]], PROPS[held].base_y - PROPS[held].h)
        p.reach(t0, mid, side, pt)
        p.to(mid + 0.05, t1, "io", **{f"arm_{side}": 10 if side == "r" else -10})

    def _paw_for(self, w, t, pt, tip):
        if not tip:
            return pt
        sx, sy, _ = _reach_band(w, 1 if pt[0] >= self.sim.x(w, t) else -1)
        S = (self.sim.x(w, t) + sx, sy)
        d = math.hypot(pt[0] - S[0], pt[1] - S[1]) or 1.0
        return pt[0] - tip * (pt[0] - S[0]) / d, pt[1] - tip * (pt[1] - S[1]) / d

    # --- drawing
    def held_pose(self, pn, w, t, st):
        side = self.hand(w, t)
        W, fa = self.perfs[w].paw(t, side, st)
        return W, fa

    def draw(self, t, cam, layers_out=None, post=True):
        """The world at t through cam (RGBA, cam-sized): set, floor props, characters, held props, set front."""
        S = self.sim
        d = K.drawing_of(t)
        tq = d / K.DPS
        bg = background(self, cam, tq)
        img = bg.copy()
        sts = {w: p.state(tq, d) for w, p in self.perfs.items()}
        front_props = []
        for pn in S.props:
            wh = S.prop_where(pn, tq)
            P = PROPS[pn]
            if wh[0] == "held":
                continue
            base = (MARKS[wh[1]], P.base_y) if wh[0] == "floor" and wh[1] in MARKS else \
                (float(wh[1][2:]), P.base_y) if wh[0] == "floor" else S.st.spots[wh[1]]
            (front_props if P.front else [None]).append((pn, base))
            if not P.front and P.draw_fn:
                P.draw_fn(img, cam, base, tq, None)
        if self.extra_back:
            self.extra_back(img, cam, tq)
        size = img.size
        for w, p in self.perfs.items():
            L = Image.new("RGBA", size, (0, 0, 0, 0))
            p.draw(L, tq, cam, d, sts[w])
            if layers_out is not None:
                layers_out.append((p, L))
            img.alpha_composite(L)
        for pn in S.props:
            wh = S.prop_where(pn, tq)
            if wh[0] == "held" and PROPS[pn].draw_fn:
                W, fa = self.held_pose(pn, wh[1], tq, sts[wh[1]])
                ang = self._held_angle(pn, wh[1], tq, W)
                hb = PROPS[pn].hold_box
                PROPS[pn].draw_fn(img, cam, (W[0], W[1] + hb[3]) if pn != "marker" else W, tq, (wh[1], ang))
        for pn, base in front_props:
            if pn and PROPS[pn].draw_fn:
                PROPS[pn].draw_fn(img, cam, base, tq, None)
        if self.extra_front:
            self.extra_front(img, cam, tq)
        fl = Image.new("RGBA", size, (0, 0, 0, 0))
        self.set.front(fl, cam, tq, self.table.light)
        img.alpha_composite(fl)
        if layers_out is not None:
            layers_out.append((None, fl))
        if self.post and post:
            img = self.post(img, cam, tq)
        return img, sts

    def _held_angle(self, pn, w, t, W):
        for t0, t1, ww, tgt in self.sim.points:
            if ww == w and t0 <= t <= t1 + 0.2:
                pt = self.sim._targets(tgt, t0)
                k = min(len(pt) - 1, int((t - t0) / max(1e-6, t1 - t0) * len(pt)))
                return math.degrees(math.atan2(pt[k][0] - W[0], pt[k][1] - W[1]))
        f = 1 if self.sim.facing(w, t) >= 0 else -1
        return math.degrees(math.atan2(0.45 * f, 0.9))

    def shot_at(self, t):
        for s0, s1, pre in self.table.shots:
            if s0 - 1e-9 <= t < s1 - 1e-9:
                return pre
        return self.table.shots[-1][2] if self.table.shots else ("W" if self.table.view == "land" else "VW@C")

    def still(self, t):
        view, z, (x0, y0, x1, y1) = PRESETS[self.shot_at(t)]
        cam = _Cam(x0, y0, x1 - x0, y1 - y0)
        img, _ = self.draw(t, cam)
        out = (1920, 1080) if view == "land" else (1080, 1920)
        return img.convert("RGB").resize(out, Image.LANCZOS)

    def sheet(self, times, out, label=True):
        """A key-beat sheet: stills through the shot cameras, time labels only (wordless)."""
        ims = [self.still(t) for t in times]
        w, h = (480, 270) if self.table.view == "land" else (270, 480)
        cols = 3
        rows = (len(ims) + cols - 1) // cols
        sh = Image.new("RGB", (cols * w + (cols + 1) * 12, rows * (h + 30) + 12), (250, 248, 242))
        dr = ImageDraw.Draw(sh)
        for i, (t, im) in enumerate(zip(times, ims)):
            x, y = 12 + (i % cols) * (w + 12), 12 + (i // cols) * (h + 30)
            sh.paste(im.resize((w, h), Image.LANCZOS), (x, y))
            if label:
                dr.text((x, y + h + 4), f"{i + 1}   {t:.1f} s", fill=(60, 50, 50))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        sh.save(out)
        return out


def background(stage, cam, t):
    """The set alone (clearance_check wraps this to learn the prop-free background)."""
    return stage.set.background(cam, t, stage.table.light)


# ---------------------------------------------------------------- clearance_check hooks
CLEAR_BAND = (0.0, 300.0, 1920.0, 1500.0)    # the world rows the sweep looks at (x0, y0, w, h)


def export(g, stage, sheet_times=None):
    """Give an episode script the names tools/clearance_check.py reads (frame, B, RES, name_of, head_mask, SHEET,
    CLEARANCE_ALLOW: the holder's paws while it holds a prop, which the kit allows by design)."""
    B = SimpleNamespace(T_DRAW=0.0, LAND_Y0=CLEAR_BAND[1])
    cam = _Cam(*CLEAR_BAND)
    names = {id(p): SHORT[w] for w, p in stage.perfs.items()}

    def frame(t):
        B.T_DRAW = K.drawing_of(t) / K.DPS
        lay = []
        img, sts = stage.draw(t, cam, lay, post=False)
        cast = [p for p, _ in lay if p is not None]
        layers = [L for _, L in lay]
        return img, PRESETS[stage.shot_at(t)][2], {"cast": cast, "layers": layers}

    def head_mask(p, t=None):
        L = Image.new("RGBA", (int(cam.w * cam.res), int(cam.h * cam.res)), (0, 0, 0, 0))
        st = p.state(B.T_DRAW if t is None else t)
        p.a.draw(L, cam, st)
        m = _mask(L).copy()
        sy = min(p.a.shoulder(st, "l")[1], p.a.shoulder(st, "r")[1])
        m[max(0, int((sy - 4 - cam.oy) * cam.res)):, :] = False
        return m

    times = sheet_times or [round((a + b) / 2, 2) for a, b, _ in stage.table.shots]
    allow = []
    for t in times:
        for w in stage.perfs:
            if stage.sim.holding(w, t) or any(b[0] <= t <= b[1] and b[2] == w and b[3] in
                                              ("hand_over", "pick_up", "put_down", "place_on", "drop")
                                              for b in stage.table.beats):
                allow.append(f"{SHORT[w]}.paws@{t:g}")
            for b in stage.table.beats:
                if b[3] == "hand_over" and b[0] <= t <= b[1] and b[4].split()[1] == w:
                    allow.append(f"{SHORT[w]}.paws@{t:g}")
    g.update(frame=frame, B=B, RES=hires.RES, name_of=lambda p: names[id(p)], head_mask=head_mask,
             SHEET=tuple(times), CLEARANCE_ALLOW=tuple(sorted(set(allow))), STAGE=stage)
