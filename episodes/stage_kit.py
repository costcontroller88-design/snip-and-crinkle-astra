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

v2 (19 Oct): the kit works staging out instead of only refusing.
- Spots "x:<n>" (any floor x; the solver writes them). Reach moves take a pose: "lean=<0-12>" (degrees toward the
  target) and "sq=<0.88-1>" (crouch; head_dy follows): the reach is measured from the posed rig shoulder.
- Silhouettes: every check near a prop or between close friends uses the rendered masks as 4 u row profiles
  (posed, cached in build/stage_pose_cache.json), not boxes, so a round head beside a round lantern is judged right.
- Depth: a floor prop with front=True (the lantern) is drawn over the cast; feet may hide behind it, heads stay
  10 u from it and resting paws (30 u discs) 10 u from it. The paw at work and its prop are drawn over it.
  "walk_to <spot> front": the walker is drawn in front and may cross the others; standing, heads stay 10 u apart.
- New moves: take (<prop> [from <who>], the taker pinches it from the holder's paw), draw (<prop>.<path> [f0-f1],
  the held tip follows the path and reveals the stroke), sway [n], wiggle [up], spin [left|right], bow, puff (Pip);
  hand_over finds a pass point for any facing pair in reach (poses "lean= sq=" for the giver, "rlean= rsq=" for
  the receiver), so Crinkle-Pip passes work with a lean and a crouch.
- Vertical frames centred on the group: "VW|VM|VC@x<n>" (stage.py writes it from "@group").
- solve(): an intent row ("Snip draw lantern.eye_l") gets a stand x, side, lean and crouch, a walk or turn before it
  and a legal frame; it refuses only when nothing works, and then lists the nearest rows that do.
"""
import copy
import hashlib
import json
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
GAGS = ("sway", "wiggle", "spin", "bow", "puff")
BODY = ("enter", "exit", "walk_to", "turn", "hop", "pick_up", "put_down", "drop", "place_on", "hand_over", "point",
        "take", "draw") + GAGS
FACEMOVES = ("look", "nod", "shake", "react")
MOVES = BODY + FACEMOVES + ("hold", "bespoke")
REACHES = ("pick_up", "put_down", "place_on", "drop", "hand_over", "take", "point", "draw")
INTENT = ("pick_up", "put_down", "place_on", "hand_over", "take", "point", "draw")
MAX_BESPOKE = 2
LEANS, SQS = (0, 4, 8, 12), (1.0, 0.94, 0.88)    # the solver's poses: lean (deg toward the target), crouch (rig sq)
MAX_LEAN, MIN_SQ = 12.0, 0.88
CROUCH_DY = 50.0                        # head_dy per unit of crouch (1 - sq), design units
PAW_R = 30.0                            # tools/clearance_check paw disc
POSE_OUT = 0.3                          # a pose eases back over 0.3 s after its beat


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
VZOOM = {"VW": 1.0, "VM": 1.38, "VC": 2.0}


def preset(name):
    """(view, zoom, window) for a menu preset or a group-centred vertical one ("VM@x812"); None if unknown."""
    if name in PRESETS:
        return PRESETS[name]
    m = re.match(r"^(VW|VM|VC)@x(-?\d+)$", name or "")
    if not m:
        return None
    z = VZOOM[m.group(1)]
    w, h = 1080 / z, 1920 / z
    y1 = 1920.0 if z == 1.0 else min(1920.0, FLOOR + 0.19 * h)
    x0 = max(0.0, min(1920.0 - w, float(m.group(2)) - w / 2))
    return ("vert", z, (x0, y1 - h, x0 + w, y1))


def status_ext(L, T, R, win):
    """status() for a measured extent: left and right x, top y (feet on FLOOR)."""
    x0, y0, x1, y1 = win
    if R <= x0 - MARGIN or L >= x1 + MARGIN:
        return "out"
    if L < x0 + MARGIN or R > x1 - MARGIN or T < y0 + MARGIN or FLOOR > y1 - MARGIN + 6:
        return "cut"
    return "in"


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


# ---------------------------------------------------------------- v2 silhouettes (4 u row profiles)
GRID_Y0, BAND, GRID_N = 400.0, 4.0, 300          # world rows 400-1600
NAN = float("nan")
_LO, _POSED, _SHP, _PPROF = {}, {}, {}, {}
CACHE = os.path.join(ROOT, "build", "stage_pose_cache.json")
_DISK = {"loaded": False, "dirty": False, "data": {}}


def _empty():
    return np.full(GRID_N, NAN), np.full(GRID_N, NAN)


def _prof_from_mask(m, ox, oy, res):
    """Row profile (x0, x1 arrays on the world band grid) of a boolean mask whose pixel (0, 0) is world (ox, oy)."""
    x0, x1 = _empty()
    rows = np.nonzero(m.any(1))[0]
    if not len(rows):
        return x0, x1
    first = m.argmax(1)[rows]
    last = m.shape[1] - 1 - m[:, ::-1].argmax(1)[rows]
    j = np.floor((oy + rows / res - GRID_Y0) / BAND).astype(int)
    ok = (j >= 0) & (j < GRID_N)
    np.fmin.at(x0, j[ok], (ox + first / res)[ok])
    np.fmax.at(x1, j[ok], (ox + (last + 1) / res)[ok])
    return x0, x1


def _shift(a, s):
    """Move a profile s bands down (negative: up)."""
    out = np.full_like(a, NAN)
    if s > 0:
        out[s:] = a[:-s]
    elif s < 0:
        out[:s] = a[-s:]
    else:
        out[:] = a
    return out


def place_prof(prof, dx=0.0, lift=0.0):
    s = int(round(lift / BAND))
    return _shift(prof[0], -s) + dx, _shift(prof[1], -s) + dx


def box_prof(x0, y0, x1, y1):
    a, b = _empty()
    j0, j1 = max(0, int((y0 - GRID_Y0) // BAND)), min(GRID_N - 1, int((y1 - GRID_Y0) // BAND))
    if j1 >= j0:
        a[j0:j1 + 1], b[j0:j1 + 1] = x0, x1
    return a, b


def gap(A, B, need=MARGIN):
    """Least distance between two placed profiles, searched up to need + 2 u (a far gap comes back as need + 2)."""
    best, k = need + 2.0, int((need + 2) // BAND) + 1
    for s in range(-k, k + 1):
        b0, b1 = _shift(B[0], s), _shift(B[1], s)
        both = ~np.isnan(A[0]) & ~np.isnan(b0)
        if not both.any():
            continue
        gx = float(np.maximum(np.maximum(b0 - A[1], A[0] - b1), 0.0)[both].min())
        best = min(best, math.hypot(gx, max(0.0, (abs(s) - 1) * BAND)))
        if best == 0.0:
            break
    return best


def _code_key():
    h = hashlib.sha1()
    for f in ("rig2.py", "rig2_pip.py", "acting.py", "characters.py"):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    h.update(repr(sorted(SCALE.items())).encode() + b"v2a")
    return h.hexdigest()[:16]


def _disk():
    if not _DISK["loaded"]:
        _DISK["loaded"] = True
        try:
            d = json.load(open(CACHE))
            if d.get("key") == _code_key():
                _DISK["data"] = d["data"]
        except (OSError, ValueError, KeyError):
            pass
    return _DISK["data"]


def save_cache():
    if _DISK["dirty"]:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        json.dump({"key": _code_key(), "data": _DISK["data"]}, open(CACHE, "w"))
        _DISK["dirty"] = False


def _lo_puppet(who):
    """A 1x-resolution puppet for silhouettes (same geometry as the real one; 4x fewer pixels)."""
    if who not in _LO:
        old = hires.RES
        hires.set_res(1)
        try:
            _LO[who] = (R.Puppet("snip", SCALE["Snip"]) if who == "Snip" else
                        R.Puppet("crinkle", SCALE["Crinkle"]) if who == "Crinkle" else RP.PipPuppet(SCALE["Pip"]))
        finally:
            hires.set_res(old)
    return _LO[who]


def _posed_state(who, f, lean, sq, arms):
    pup = _lo_puppet(who)
    cls = RP.PipPerf if who == "Pip" else R.Perf2
    st = cls(pup, seed=0, x=0.0, y=FLOOR, turn=0.5 * f).state(0.0)
    st.update(lean=float(lean), sq=float(sq), head_dy=CROUCH_DY * (1 - sq))
    if arms == "up":
        st.update(arm_l=-150.0, arm_r=150.0, elb_l=-10.0, elb_r=10.0)
    if arms == "puff" and who == "Pip":
        st["puff"] = 1.0
    return pup, st


def _q(lean, sq):
    return float(round(lean)), round(float(sq) / 0.02) * 0.02


def shoulder_posed(who, f, side, lean=0.0, sq=1.0):
    """World (dx, y) of a shoulder ("l"/"r") for who at x 0 facing f (-1/0/1), rig lean (deg), crouch sq."""
    key = (who, f, side, round(lean, 2), round(sq, 3))
    if key not in _SHP:
        pup, st = _posed_state(who, f, lean, sq, "rest")
        _SHP[key] = pup.shoulder(st, side)
    return _SHP[key]


def reach_len(who):
    return geom(who, 1)["reach"]


def posed(who, f, lean=0.0, sq=1.0, arms="rest"):
    """Silhouette of who at x 0 facing f (-1/0/1), rig lean (deg), crouch sq, arms rest/up/puff: body and head
    profiles, paw and shoulder points, extent (left, top, right) and the feet band's top y."""
    lean, sq = _q(lean, sq)
    key = f"{who}|{f}|{lean:g}|{sq:g}|{arms}"
    if key in _POSED:
        return _POSED[key]
    d = _disk().get(key)
    if d is None:
        pup, st = _posed_state(who, f, lean, sq, arms)
        img = Image.new("RGBA", (900, 1100), (0, 0, 0, 0))
        pup.draw(img, _Cam(-450, 480, 900, 1100, 1), st)
        m = _mask(img)
        sy = min(pup.shoulder(st, "l")[1], pup.shoulder(st, "r")[1]) - 4
        hm = m.copy()
        hm[max(0, int(sy - 480)):, :] = False
        body, head = _prof_from_mask(m, -450, 480, 1), _prof_from_mask(hm, -450, 480, 1)
        ys = np.nonzero(m.any(1))[0]
        d = {"body": [[None if v != v else round(v, 1) for v in a] for a in body],
             "head": [[None if v != v else round(v, 1) for v in a] for a in head],
             "paws": {s: list(pup.arm_points(st, s)[2]) for s in "lr"},
             "sh": {s: list(pup.shoulder(st, s)) for s in "lr"},
             "foot_top": float(480 + ys.max() + 1 - 60) if len(ys) else FLOOR - 60}
        _DISK["data"][key] = d
        _DISK["dirty"] = True
    arr = lambda L: tuple(np.array([NAN if v is None else v for v in a], float) for a in L)  # noqa: E731
    body, head = arr(d["body"]), arr(d["head"])
    ok = ~np.isnan(body[0])
    js = np.nonzero(ok)[0]
    g = dict(body=body, head=head, paws={s: tuple(v) for s, v in d["paws"].items()},
             sh={s: tuple(v) for s, v in d["sh"].items()}, foot_top=d["foot_top"],
             left=float(np.nanmin(body[0])), right=float(np.nanmax(body[1])), top=GRID_Y0 + BAND * js.min())
    _POSED[key] = g
    return g


_FSPOT = {}


def front_spot(who, prop, f):
    """Work spot beside a front prop: the least centre distance at which who, standing and facing it (f = 1 from
    the left), keeps its head 10 u and its resting paws (30 u discs) 10 u from the prop's silhouette."""
    key = (who, prop, f)
    if key not in _FSPOT:
        F = place_prof(prop_prof(prop), 0.0)
        g = posed(who, f)
        d = PROPS[prop].w / 2
        while d < 900:
            x = -f * d
            if gap(place_prof(g["head"], x), F) >= MARGIN and all(
                    gap(box_prof(x + px - PAW_R, py - PAW_R, x + px + PAW_R, py + PAW_R), F) >= MARGIN
                    for px, py in g["paws"].values()):
                break
            d += 2
        _FSPOT[key] = d
    return _FSPOT[key]


def prop_prof(name):
    """Silhouette of a floor prop standing with its base at (0, base_y), from its own draw function."""
    if name not in _PPROF:
        P = PROPS[name]
        res = hires.RES
        x0, y0, w, h = -P.w, P.base_y - P.h - 80, 2 * P.w, P.h + 120
        cam = _Cam(x0, y0, w, h, res)
        img = Image.new("RGBA", (int(w * res), int(h * res)), (0, 0, 0, 0))
        if P.draw_fn:
            P.draw_fn(img, cam, (0.0, P.base_y), 0.0, None)
            _PPROF[name] = _prof_from_mask(_mask(img), x0, y0, res)
        else:
            _PPROF[name] = box_prof(-P.w / 2, P.base_y - P.h, P.w / 2, P.base_y)
    return _PPROF[name]


# ---------------------------------------------------------------- props and sets
PIP_ANGLE = 90.0                        # Pip holds a carried marker level, tip forward


def hold_box(p, who, f):
    """The box a held prop covers around its holder's paw (Pip carries the marker level: its own box)."""
    P = PROPS[p]
    if who == "Pip" and P.name == "marker":
        if f not in _PIPBOX:
            _PIPBOX[f] = _held_box(_draw_marker, (PIP_ANGLE * (1 if f >= 0 else -1),))
        return _PIPBOX[f]
    return P.hold_box


_PIPBOX = {}


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


_CUR = []                               # the Stage being drawn (its draw rows reveal the strokes)


def _draw_lantern(img, cam, base, t, held):
    PL, lan = _lantern()
    strokes, lit = LANTERN_STROKES["fn"](t), LANTERN_STROKES["lit"](t)
    if not strokes and _CUR:
        strokes = _CUR[-1].strokes("lantern", t)
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
    return Prop("lantern", 240, 200, _draw_lantern, points=mids, paths=pts, base_y=by, carry=False, front=True)


def _held_box(draw, angles=(-27.0, 0.0, 27.0)):
    """The box (around the paw) a held prop really covers, measured from its sprite at the carry angles."""
    res = hires.RES
    cam = _Cam(-120, -120, 240, 240, res)
    img = Image.new("RGBA", (int(240 * res), int(240 * res)), (0, 0, 0, 0))
    for a in angles:
        draw(img, cam, (0.0, 0.0), 0.0, ("", a))
    ys, xs = np.nonzero(_mask(img))
    return tuple(float(v) for v in (xs.min() / res - 122, ys.min() / res - 122, xs.max() / res - 118, ys.max() / res - 118))


PROPS = {"marker": Prop("marker", 24, 60, _draw_marker, tip=RP.MARKER_TIP * 1.1, hold_box=_held_box(_draw_marker)),
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
    """Positions, facing, holders, poses and hops over time, from a table; problems() lists every broken rule."""

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
        m = re.match(r"^x:(-?\d+(?:\.\d+)?)$", spot or "")
        if m:
            x = float(m.group(1))
            if not 0 <= x <= 1920:
                raise Refused(f"x:{x:g} is off the floor (0-1920; OFF_L / OFF_R for exits)")
            return x
        m = re.match(r"^([A-E]|WL|WR)\.(L|R)$", spot or "")
        if not m:
            raise Refused(f"'{spot}' is not a mark or spot: use {', '.join(MARKS)}, <mark>.L / <mark>.R or x:<n>")
        mk, side = m.groups()
        M = MARKS[mk]
        f = 1 if side == "L" else -1
        prop = self.floor_prop_at(mk, t)
        if prop and PROPS[prop].front:
            return M - f * front_spot(who, prop, f)
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
        self.poses = {w: [] for w in self.cast}      # (t0, t1, [(facing or None, rig lean, sq, arms, lift)])
        self.active = {w: [] for w in self.cast}     # (t0, t1, side, kind): a paw at work (exempt near props)
        self.reach_pts = {w: [] for w in self.cast}  # (t0, t1, [points]) for framing
        self.arm = {w: [] for w in self.cast}        # (t0, t1, pts, tip, side): where the paw goes (take needs it)
        self.z = {w: [(0.0, 0)] for w in self.cast}  # 1: drawn in front (after a "front" walk)
        self.fwalks = {w: [] for w in self.cast}     # walks in front: crossing allowed
        self.strokes, self.passes = [], []           # draw reveals; (t0, t1, giver, taker, prop, point, kind)
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

    def fsign(self, who, t):
        f = self.facing(who, t)
        return 1 if f > 0 else -1 if f < 0 else 0

    def zorder(self, who, t):
        v = 0
        for tt, z in self.z[who]:
            if tt <= t + 1e-9:
                v = z
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

    def prop_x(self, p, t):
        wh = self.prop_where(p, t)
        if wh[0] != "floor":
            return None
        return MARKS[wh[1]] if wh[1] in MARKS else float(wh[1][2:])

    def holding(self, who, t):
        return [p for p in self.props if self.prop_where(p, t) == ("held", who)]

    def lift(self, who, t):
        return max([40 * SCALE[who] for a, b in self.hops[who] if a - 1e-9 <= t <= b + 1e-9] + [0.0])

    def on_stage(self, who, t):
        x = self.x(who, t)
        return -200 < x < 2120

    def walking(self, who, t):
        return any(a <= t <= b for a, b, *_ in self.walks[who])

    # --- poses (v2)
    def variants(self, w, t):
        """[(facing, rig lean, sq, arms, lift)] the silhouette may take at t (rest, plus any pose or gag span)."""
        fs, lift = self.fsign(w, t), self.lift(w, t)
        out = [(fs, 0.0, 1.0, "rest", lift)]
        for a, b, vs in self.poses[w]:
            if a - 1e-9 <= t <= b + 1e-9:
                out += [(fs if f is None else f, ln, sq, arms, max(lift, lf)) for f, ln, sq, arms, lf in vs]
        return out

    def busy_sides(self, w, t):
        return {s for a, b, s, _ in self.active[w] if a - 1e-9 <= t <= b + 1e-9}

    def extent(self, w, t):
        """(left x, top y, right x) of who at t: the framing size, every pose it may take, and paws at work."""
        h, l, r = SIZES[w]
        x, lift = self.x(w, t), self.lift(w, t)
        L, T, Rr = x - l, FLOOR - h - lift, x + r
        vs = self.variants(w, t)
        if len(vs) > 1:
            for f, ln, sq, arms, lf in vs:
                g = posed(w, f, ln, sq, arms)
                L, T, Rr = min(L, x + g["left"]), min(T, g["top"] - lf), max(Rr, x + g["right"])
        for a, b, pts in self.reach_pts[w]:
            if a - 1e-9 <= t <= b + 1e-9:
                for px, py in pts:
                    L, T, Rr = min(L, px - PAW_R), min(T, py - PAW_R), max(Rr, px + PAW_R)
        return L, T, Rr

    @staticmethod
    def _pose_args(arg):
        kw = dict(re.findall(r"\b(lean|sq|rlean|rsq)=(-?[\d.]+)", arg))
        words = [w for w in arg.split() if "=" not in w]
        out = {k: float(v) for k, v in kw.items()}
        for k in ("lean", "rlean"):
            if not 0 <= out.get(k, 0) <= MAX_LEAN:
                raise Refused(f"{k} is 0-{MAX_LEAN:g} (degrees toward the target)")
        for k in ("sq", "rsq"):
            if not MIN_SQ - 1e-9 <= out.get(k, 1.0) <= 1.0:
                raise Refused(f"{k} is {MIN_SQ:g}-1.0 (a crouch)")
        return words, out.get("lean", 0.0), out.get("sq", 1.0), out.get("rlean", 0.0), out.get("rsq", 1.0)

    def _lead(self, who, t0):
        """A reach right after a walk lifts the arm during the walk-in (at most 1 s of it)."""
        return max([min(1.0, b - a) for a, b, *_ in self.walks[who] if abs(b - t0) < 0.05] + [0.0])

    def _pose(self, who, t0, t1, side, lean, sq, kind):
        """Record a reach pose (lean toward `side`) and the paw at work."""
        lead = self._lead(who, t0)
        if lean or sq < 1:
            self.poses[who].append((t0, t1 + POSE_OUT, [(None, -lean * side, sq, "rest", 0.0)]))
        self.active[who].append((t0 - lead, t1 + POSE_OUT, "r" if side > 0 else "l", kind))

    def shoulder(self, who, t, side, lean=0.0, sq=1.0):
        """World shoulder for a reach toward side (+1 right / -1 left), leaning `lean` degrees that way."""
        fs = self.fsign(who, t)
        dx, y = shoulder_posed(who, fs, "r" if side > 0 else "l", -lean * side, sq)
        return self.x(who, t) + dx, y

    def _apply(self, t0, t1, who, move, arg):
        if move not in MOVES:
            raise Refused(f"unknown move '{move}': use {', '.join(MOVES)}")
        if who not in self.cast and move != "bespoke":
            raise Refused(f"{who} is not in the start table ({', '.join(self.cast)})")
        if t1 <= t0:
            raise Refused("the end time must be after the start")
        if move == "bespoke":
            self.bespoke.append((t0, t1, who, arg))
            if len(self.bespoke) > MAX_BESPOKE:
                raise Refused(f"more than {MAX_BESPOKE} bespoke beats: stage the rest with kit moves")
            return
        a, lean, sq, rlean, rsq = self._pose_args(arg)
        if move in ("enter", "exit", "walk_to"):
            front = "front" in a
            a = [w for w in a if w != "front"]
            if move == "exit":
                a = [a[0] if a else ("OFF_L" if self.x(who, t0) < 960 else "OFF_R")]
            if move == "enter" and self.spot_of(who, t0) not in OFF:
                raise Refused(f"{who} is on stage at {t0:g}: enter starts from OFF_L / OFF_R (use walk_to)")
            if move == "exit" and a[0] not in OFF:
                raise Refused("exit goes to OFF_L or OFF_R")
            if move == "walk_to" and (not a or a[0] in OFF):
                raise Refused("walking off stage is 'exit'" if a else "walk_to takes a spot")
            x0 = self.x(who, t0)
            x1 = self.spot_x(who, a[0], t1)
            if abs(x1 - x0) / (t1 - t0) > SPEED[who] and move == "walk_to":
                raise Refused(f"{abs(x1 - x0):.0f} u in {t1 - t0:g} s is faster than {SPEED[who]:g} u/s: "
                              f"give it at least {abs(x1 - x0) / SPEED[who]:.1f} s")
            if abs(x1 - x0) > 1:
                self.face[who].append((t0, 0.5 if x1 > x0 else -0.5))
                self.walks[who].append((t0, t1, x0, x1))
            if front:
                self.fwalks[who].append((t0, t1))
            self.z[who].append((t0, 1 if front else 0))
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
        if move in GAGS:
            return self._gag(t0, t1, who, move, a)
        f = self.facing(who, t0)
        if move == "pick_up":
            p = a[0] if a else ""
            if p not in self.props or not PROPS[p].carry:
                raise Refused(f"no prop '{p}' to pick up ({', '.join(q for q in self.props if PROPS[q].carry)})")
            if self.holding(who, t0):
                raise Refused(f"{who} already holds {self.holding(who, t0)[0]}")
            wh = self.prop_where(p, t0)
            pt = self._prop_point(p, wh, t0)
            self._need_reach(who, t0, pt, 0.0, lean, sq)
            self._need_clear(who, t0, p, pt)
            self._arm(who, t0, t1, [pt], 0.0, lean, sq, move)
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
                self._need_reach(who, t0, self.st.spots[a[0]], 0.0, lean, sq)
                self._need_clear(who, t0, p, self.st.spots[a[0]])
                self._arm(who, t0, t1, [self.st.spots[a[0]]], 0.0, lean, sq, move)
                self.hold[p].append(((t0 + t1) / 2, "spot:" + a[0]))
                return
            mk = a[0] if a else ""
            if mk not in MARKS or mk in OFF:
                raise Refused("put_down takes a mark (A-E, WL, WR): the prop stands on it")
            x = MARKS[mk]
            self._clear_floor(p, x, t0, t1, who)
            pt = (x, PROPS[p].base_y - PROPS[p].h)
            self._need_reach(who, t0, pt, 0.0, lean, sq)
            self._arm(who, t0, t1, [pt], 0.0, lean, sq, move)
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
            self._facing_pair(who, rcv, t0, "a hand-over needs a pair")
            P = self.pass_point(who, rcv, t0, p, lean, sq, rlean, rsq)
            if P is None:
                l, r = sorted((who, rcv), key=lambda w: self.x(w, t0))
                raise Refused(f"no hand-over pair for {l} (left) and {r} (right) here: their reach bands don't meet "
                              f"clear of heads and floor props (lean/sq them, or move closer)")
            sg = 1 if self.x(rcv, t0) > self.x(who, t0) else -1
            self._pose(who, t0, t1, sg, lean, sq, "give")
            self._pose(rcv, t0, t1, -sg, rlean, rsq, "receive")
            for w in (who, rcv):
                self.reach_pts[w].append((t0, t1, [P]))
            self.arm[rcv].append((t0, t1, [P], 0.0, -sg))
            self.passes.append((t0, t1, who, rcv, p, P, "hand_over"))
            self.hold[p].append((t0 + 0.55 * (t1 - t0), rcv))
            return
        if move == "take":
            p = a[0] if a else ""
            wh = self.prop_where(p, t0) if p in self.props else ("none", "")
            if wh[0] != "held":
                raise Refused(f"take takes a prop someone holds ({', '.join(q for q in self.props if self.prop_where(q, t0)[0] == 'held') or 'none held'}); "
                              "a prop on the floor is pick_up")
            giver = wh[1]
            if giver == who:
                raise Refused(f"{who} already holds {p}")
            if len(a) > 2 and a[1] == "from" and a[2] != giver:
                raise Refused(f"{a[2]} doesn't hold {p} at {t0:g} ({giver} does)")
            if self.holding(who, t0):
                raise Refused(f"{who}'s paws are full")
            self._facing_pair(who, giver, t0, "a take needs a pair")
            G = self.paw_at(giver, t0)
            sg = 1 if G[0] >= self.x(who, t0) else -1
            self._need_reach(who, t0, G, 0.0, lean, sq)
            hb = hold_box(p, giver, self.fsign(giver, t0) or 1)
            box = box_prof(G[0] + hb[0], G[1] + hb[1], G[0] + hb[2], G[1] + hb[3])
            for w in (who, giver):
                for v in self._variants_with(w, t0, -lean * sg if w == who else 0.0, sq if w == who else 1.0):
                    if gap(place_prof(posed(w, *v[:4])["head"], self.x(w, t0), v[4]), box) < MARGIN:
                        raise Refused(f"{p} at {who}'s paw would come within {MARGIN:g} u of {w}'s head")
            self._pose(who, t0, t1, sg, lean, sq, "take")
            self.active[giver].append((t0, t1 + POSE_OUT, "r" if -sg > 0 else "l", "give"))
            self.reach_pts[who].append((t0, t1, [G]))
            self.arm[who].append((t0, t1, [G], 0.0, sg))
            self.passes.append((t0, t1, giver, who, p, G, "take"))
            self.hold[p].append((t0 + 0.55 * (t1 - t0), who))
            return
        if move in ("point", "draw"):
            tgt = a[0] if a else ""
            held = self.holding(who, t0)
            tip = PROPS[held[0]].tip if held else 0.0
            f0, f1 = 0.0, 1.0
            if move == "draw":
                if not tip:
                    raise Refused(f"draw needs a held prop with a tip (a marker): {who} holds {held[0] if held else 'nothing'}")
                pn, _, part = tgt.partition(".")
                if pn not in self.props or part not in PROPS[pn].paths:
                    raise Refused(f"draw takes <prop>.<path>: {', '.join(f'{q}.{n}' for q in self.props for n in PROPS[q].paths) or 'no prop with paths'}")
                if len(a) > 1:
                    m = re.match(r"^(\d*\.?\d+)-(\d*\.?\d+)$", a[1])
                    if not m or not 0 <= float(m.group(1)) < float(m.group(2)) <= 1:
                        raise Refused("draw's second word is the part of the path, e.g. 0-0.67 (fractions)")
                    f0, f1 = float(m.group(1)), float(m.group(2))
            pts = self._targets(tgt, t0, f0, f1, move == "draw")
            for pt in pts:
                self._need_reach(who, t0, pt, tip, lean, sq)
            if held:                         # the held prop's back end stays 10 u from its holder's head
                side = 1 if pts[0][0] >= self.x(who, t0) else -1
                S = self.shoulder(who, t0, side, lean, sq)
                back = -PROPS[held[0]].hold_box[1] * 0.85
                H = [place_prof(posed(who, *v[:4])["head"], self.x(who, t0), v[4])
                     for v in self._variants_with(who, t0, -lean * side, sq)]
                for pt in pts:
                    P = self.paw_for(who, t0, pt, tip, lean, sq)
                    d = math.hypot(pt[0] - S[0], pt[1] - S[1]) or 1.0
                    ux, uy = (pt[0] - S[0]) / d, (pt[1] - S[1]) / d
                    near = []
                    for k in np.linspace(-back, tip, 7):     # the marker as 7 small boxes along its axis
                        cx, cy = P[0] + ux * k, P[1] + uy * k
                        near.append(box_prof(cx - 12, cy - 12, cx + 12, cy + 12))
                    if any(gap(h, b) < MARGIN for h in H for b in near):
                        raise Refused(f"the {held[0]}'s end would come within {MARGIN:g} u of {who}'s head drawing "
                                      f"({pt[0]:.0f}, {pt[1]:.0f}): stand further off or lower (sq=)")
            self._arm(who, t0, t1, pts, tip, lean, sq, move)
            self.points.append((t0, t1, who, tgt))
            if move == "draw":
                self.strokes.append((t0, t1, tgt.partition(".")[0], tgt.partition(".")[2], f0, f1))
            return

    def _gag(self, t0, t1, who, move, a):
        fs = self.fsign(who, t0)
        if move == "sway":
            if t1 - t0 < 0.6:
                raise Refused("a sway lasts at least 0.6 s")
            self.poses[who].append((t0, t1, [(None, 6.0, 1.0, "rest", 0.0), (None, -6.0, 1.0, "rest", 0.0)]))
        elif move == "wiggle":
            if t1 - t0 < 0.6:
                raise Refused("a wiggle lasts at least 0.6 s")
            arms = "up" if "up" in a else "rest"
            lf = 12 * SCALE[who]
            self.poses[who].append((t0, t1, [(None, 7.0, 1.0, arms, lf), (None, -7.0, 1.0, arms, lf)]))
            if arms == "up":
                self.active[who] += [(t0, t1, "l", "wiggle"), (t0, t1, "r", "wiggle")]
            if self.holding(who, t0):
                raise Refused(f"{who} holds {self.holding(who, t0)[0]}: put it down before a wiggle")
        elif move == "spin":
            end = a[0] if a else ("right" if fs < 0 else "left")
            if end not in ("left", "right"):
                raise Refused("spin takes left or right (the way it ends facing)")
            if not 0.3 <= t1 - t0 <= 1.5:
                raise Refused("a spin lasts 0.3-1.5 s")
            self.poses[who].append((t0, t1, [(f, 0.0, 1.0, "rest", 0.0) for f in (-1, 0, 1)]))
            self.face[who].append((t1, FACE[end]))
        elif move == "bow":
            if not 0.6 <= t1 - t0 <= 2.0:
                raise Refused("a bow lasts 0.6-2.0 s")
            self.poses[who].append((t0, t1, [(None, -10.0 * (fs or 1), 1.0, "rest", 0.0)]))
        elif move == "puff":
            if who != "Pip":
                raise Refused("only Pip puffs up")
            if t1 - t0 < 1.0:
                raise Refused("a puff-up is held at least 1.0 s")
            self.poses[who].append((t0, t1, [(None, 0.0, 1.0, "puff", 0.0)]))

    def _variants_with(self, w, t, lean, sq):
        return self.variants(w, t) + ([(self.fsign(w, t), lean, sq, "rest", self.lift(w, t))] if lean or sq < 1 else [])

    def _facing_pair(self, a, b, t, what):
        xa, xb = self.x(a, t), self.x(b, t)
        d = 1 if xb > xa else -1
        if self.fsign(a, t) != d or self.fsign(b, t) != -d:
            raise Refused(f"{what}: {a} and {b} must face each other (turn first; now {self.spot_of(a, t)} and "
                          f"{self.spot_of(b, t)})")

    def _arm(self, who, t0, t1, pts, tip, lean, sq, kind):
        side = 1 if pts[0][0] >= self.x(who, t0) else -1
        self._pose(who, t0, t1, side, lean, sq, kind)
        self.reach_pts[who].append((t0, t1, [self.paw_for(who, t0, pt, tip, lean, sq) for pt in pts]))
        self.arm[who].append((t0, t1, pts, tip, side, lean, sq))

    def paw_for(self, who, t, pt, tip, lean=0.0, sq=1.0):
        """The paw centre that puts a held tip of length `tip` on pt (the tip points away from the shoulder)."""
        if not tip:
            return pt
        S = self.shoulder(who, t, 1 if pt[0] >= self.x(who, t) else -1, lean, sq)
        d = math.hypot(pt[0] - S[0], pt[1] - S[1]) or 1.0
        return pt[0] - tip * (pt[0] - S[0]) / d, pt[1] - tip * (pt[1] - S[1]) / d

    def carry_point(self, w, t):
        """The carry pose: paw forward and low; else tucked to the chest; else high and forward at the shoulder:
        the first whose paw keeps 10 u from front props and whose prop keeps 10 u from every head and feet
        (its holder's too); a carried prop stays 16 u above its holder's feet band."""
        f = 1 if self.facing(w, t) >= 0 else -1
        sx, sy, r = _reach_band(w, f)
        x = self.x(w, t)
        held = self.holding(w, t)
        low = sy + 0.75 * r
        hb = hold_box(held[0], w, f) if held else (-PAW_R, -PAW_R, PAW_R, PAW_R)
        if held:
            low = min(low, posed(w, f)["foot_top"] - MARGIN - 6 - hb[3])
        opts = [(x + sx + f * 0.5 * r, low), (x + 0.5 * sx, min(low, sy + 0.6 * r)), (x + sx + f * 0.9 * r, min(low, sy - 0.3 * r))]
        for W in opts:
            disc = box_prof(W[0] - PAW_R, W[1] - PAW_R, W[0] + PAW_R, W[1] + PAW_R)
            box = box_prof(W[0] + hb[0], W[1] + hb[1], W[0] + hb[2], W[1] + hb[3])
            bad = any(gap(place_prof(prop_prof(q), qx), disc) < MARGIN for q in self.props
                      for qx in [self.prop_x(q, t)] if qx is not None and PROPS[q].front and abs(qx - x) < 700)
            for o in self.cast:
                if bad or not self.on_stage(o, t) or abs(self.x(o, t) - W[0]) > 400:
                    continue
                pg = posed(o, self.fsign(o, t))
                bad = gap(place_prof(pg["head"], self.x(o, t)), box) < MARGIN or \
                    gap(self._feet_prof(o, t, pg), box) < MARGIN
            if not bad:
                return W
        return opts[1]

    def paw_at(self, w, t):
        """Where w's working paw is at t (the last reach that started by t), else the carry point."""
        last = None
        for rec in self.arm[w]:
            if rec[0] <= t + 1e-9:
                last = rec
        if last is None or self.walking(w, t) or any(a < t and b > last[0] for a, b, *_ in self.walks[w]):
            return self.carry_point(w, t)
        t0, t1, pts, tip = last[:4]
        lean, sq = (last[5], last[6]) if len(last) > 5 else (0.0, 1.0)
        n = len(pts)
        if n == 1:
            k = 0
        else:
            u = (t - t0 - 0.3 * (t1 - t0)) / max(1e-6, 0.7 * (t1 - t0))
            k = int(round(max(0.0, min(1.0, u)) * (n - 1)))
        return self.paw_for(w, t0, pts[k], tip, lean, sq)

    def pass_point(self, g, r, t, p, lean=0.0, sq=1.0, rlean=0.0, rsq=1.0):
        """A point both paws reach (85 % of the reach) where the held prop stays 10 u from both heads; 10 u from a
        floor prop (paws too, as 30 u discs), or for a front prop (drawn behind the working paws) outside its
        silhouette; nearest the middle of the shoulders."""
        xg, xr = self.x(g, t), self.x(r, t)
        sg = 1 if xr > xg else -1
        Sg, Sr = self.shoulder(g, t, sg, lean, sq), self.shoulder(r, t, -sg, rlean, rsq)
        rg, rr = reach_len(g) * REACH_USE, reach_len(r) * REACH_USE
        hb = hold_box(p, g, sg) if p in PROPS else (-12, -10, 12, 52)
        heads = []
        for w, ln, s in ((g, -lean * sg, sq), (r, rlean * sg, rsq)):
            for v in self._variants_with(w, t, ln, s):
                pg = posed(w, *v[:4])
                heads.append(place_prof(pg["head"], self.x(w, t), v[4]))
                heads.append(self._feet_prof(w, t, pg, v[4]))
        floors = [(place_prof(prop_prof(q), self.prop_x(q, t)), PROPS[q].front) for q in self.props
                  if self.prop_x(q, t) is not None]
        xs = np.arange(min(Sg[0], Sr[0]) - rg, max(Sg[0], Sr[0]) + rr + 1, 4.0)
        ys = np.arange(1100.0, FLOOR - 20, 4.0)
        X, Y = np.meshgrid(xs, ys)
        ok = (np.hypot(X - Sg[0], Y - Sg[1]) <= rg) & (np.hypot(X - Sr[0], Y - Sr[1]) <= rr)
        if not ok.any():
            return None
        mid = ((Sg[0] + Sr[0]) / 2, max(Sg[1], Sr[1]) + 40)
        cand = sorted(zip(X[ok], Y[ok]), key=lambda q: math.hypot(q[0] - mid[0], q[1] - mid[1]))
        for px, py in cand[:400]:
            box = box_prof(px + hb[0], py + hb[1], px + hb[2], py + hb[3])
            if any(gap(H, box) < MARGIN for H in heads):
                continue
            disc = box_prof(px - PAW_R, py - PAW_R, px + PAW_R, py + PAW_R)
            dot = box_prof(px - 1, py - 1, px + 1, py + 1)
            if any((gap(F, dot, 1.0) < 1.0) if front else (gap(F, box) < MARGIN or gap(F, disc) < MARGIN)
                   for F, front in floors):
                continue        # a front prop: the paws at work are drawn over it, never inside its silhouette
            return float(px), float(py)
        return None

    def _prop_point(self, p, wh, t):
        P = PROPS[p]
        if wh[0] == "spot":
            return self.st.spots[wh[1]]
        if wh[0] == "floor":
            x = MARKS[wh[1]] if wh[1] in MARKS else float(wh[1][2:])
            return (x, P.base_y - P.h)
        raise Refused(f"{p} is held by {wh[1]}: use take or hand_over")

    def _targets(self, tgt, t, f0=0.0, f1=1.0, path=False):
        if tgt in self.cast:
            return [(self.x(tgt, t), FLOOR - SIZES[tgt][0] * 0.4)]
        if tgt in MARKS:
            return [(MARKS[tgt], FLOOR - 200)]
        pn, _, part = tgt.partition(".")
        if pn not in self.props:
            raise Refused(f"point at a character, a mark or <prop>.<point|path> ({', '.join(self.props)})")
        P = PROPS[pn]
        wh = self.prop_where(pn, t)
        bx, by = (self.prop_x(pn, t), P.base_y) if wh[0] == "floor" else self._prop_point(pn, wh, t)
        if part in P.paths and (path or (f0, f1) != (0.0, 1.0)):
            n = max(3, int(round(6 * (f1 - f0))) + 1)
            return [(bx + P.paths[part](f)[0], by + P.paths[part](f)[1]) for f in np.linspace(f0, f1, n)]
        if part in P.points:
            return [(bx + P.points[part][0], by + P.points[part][1])]
        if part in P.paths:
            return [(bx + P.paths[part](f)[0], by + P.paths[part](f)[1]) for f in np.linspace(0, 1, 6)]
        if not part:
            return [(bx, by - P.h / 2)]
        raise Refused(f"{pn} has points {', '.join(P.points) or '-'} and paths {', '.join(P.paths) or '-'}")

    def _need_reach(self, who, t, pt, tip, lean=0.0, sq=1.0):
        f = self.facing(who, t)
        side = 1 if pt[0] >= self.x(who, t) else -1
        if f and side != (1 if f > 0 else -1):
            raise Refused(f"{who} faces {'right' if f > 0 else 'left'}: turn to reach ({pt[0]:.0f}, {pt[1]:.0f})")
        sx, sy = self.shoulder(who, t, side, lean, sq)
        d = math.hypot(pt[0] - sx, pt[1] - sy)
        lim = reach_len(who) * 0.95 + tip
        if d > lim:
            pose = f" (lean {lean:g}, sq {sq:g})" if lean or sq < 1 else ""
            raise Refused(f"({pt[0]:.0f}, {pt[1]:.0f}) is {d:.0f} u from {who}'s shoulder{pose}; the reach is "
                          f"{lim:.0f}: stand closer (x:<n>), lean (lean=4-12) or crouch (sq=0.94/0.88)")

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

    def problems(self, w0=None, w1=None):
        """Every broken rule; with w0-w1 only the sampled rules and shots in that window (the solver's quick look)."""
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
        lo, hi = (0.0, None) if w0 is None else (max(0.0, w0), min(self.end, w1))
        for t in self.times(lo, hi):
            on = [w for w in self.cast if self.on_stage(w, t) and not skip(t, w)]
            xs = sorted((self.x(w, t), w) for w in on)
            for i, (xa, a) in enumerate(xs):
                for xb, b in xs[i + 1:]:
                    if xb - xa > 800 or (a, b, "sp") in seen:
                        continue
                    msg = self._pair_problem(a, xa, b, xb, t, adjacent=(xs[i + 1][1] == b))
                    if msg:
                        out.append(msg)
                        seen.add((a, b, "sp"))
            for w in on:
                if (w, "carry") not in seen:
                    msg = self._carry_problem(w, t, on)
                    if msg:
                        out.append(f"{t:.1f} s: {msg}")
                        seen.add((w, "carry"))
            for p in self.props:
                wh = self.prop_where(p, t)
                if wh[0] != "floor":
                    continue
                P = PROPS[p]
                x = self.prop_x(p, t)
                for w in on:
                    if (p, w) in seen:
                        continue
                    if P.front:
                        msg = self._front_problem(p, x, w, t)
                        if msg:
                            out.append(f"{t:.1f} s: {msg}")
                            seen.add((p, w))
                        continue
                    fx0, fx1 = self.feet_box(w, t)
                    if fx0 - MARGIN < x + P.w / 2 and x - P.w / 2 < fx1 + MARGIN:
                        out.append(f"{t:.1f} s: {w}'s feet ({fx0:.0f}-{fx1:.0f}) within {MARGIN:g} u of {p} "
                                   f"({x - P.w / 2:.0f}-{x + P.w / 2:.0f}): stand on {wh[1]}.L / {wh[1]}.R")
                        seen.add((p, w))
        for i, (s0, s1, pre) in enumerate(self.t.shots):
            if w0 is not None and (s1 < w0 or s0 > w1):
                continue
            out += [f"shot {i + 1} {pre} {s0:g}-{s1:g}: {m}" for m in self.shot_problems(s0, s1, pre)]
        return out

    def _pair_problem(self, a, xa, b, xb, t, adjacent=True):
        """a stands left of b. v1: framing sizes + 10 apart (a facing pair: bodies + 10); v2: a front walk
        crosses freely, a friend standing in front keeps heads 10 u apart, posed friends keep silhouettes 10 u apart."""
        if any(u <= t <= v for w in (a, b) for u, v in self.fwalks[w]):
            return None
        posed_pair = len(self.variants(a, t)) > 1 or len(self.variants(b, t)) > 1
        if self.zorder(a, t) != self.zorder(b, t):
            for va in self.variants(a, t):
                for vb in self.variants(b, t):
                    d = gap(place_prof(posed(a, *va[:4])["head"], xa, va[4]),
                            place_prof(posed(b, *vb[:4])["head"], xb, vb[4]))
                    if d < MARGIN:
                        return (f"{t:.1f} s: {b if self.zorder(b, t) else a} stands in front, but {a} (x {xa:.0f}) and "
                                f"{b} (x {xb:.0f}) heads are {d:.0f} u apart; need {MARGIN:g}")
            return None
        if not adjacent:
            return None
        walking = any(u <= t <= v for u, v, *_ in self.walks[a] + self.walks[b])
        pair = (re.match(r"^(\w+)\.L$", self.spot_of(a, t) or "") and
                self.spot_of(b, t) == self.spot_of(a, t)[:-1] + "R" and not walking)
        facing = self.fsign(a, t) > 0 and self.fsign(b, t) < 0
        if pair:
            need = geom(a, 1)["body"][2] - geom(b, -1)["body"][0] + MARGIN
        elif facing:
            need = None
        else:
            need = spacing(a, b)
        if need is not None and xb - xa < need - 0.5:
            return (f"{t:.1f} s: {a} (x {xa:.0f}) and {b} (x {xb:.0f}) are {xb - xa:.0f} u apart; need {need:.0f} "
                    "(leave one empty mark between them, or use a hand-over pair)")
        if facing or posed_pair:
            want = MARGIN
            for va in self.variants(a, t):
                for vb in self.variants(b, t):
                    d = gap(place_prof(posed(a, *va[:4])["body"], xa, va[4]),
                            place_prof(posed(b, *vb[:4])["body"], xb, vb[4]), want)
                    if d < want:
                        return (f"{t:.1f} s: {a} (x {xa:.0f}) and {b} (x {xb:.0f}) silhouettes are {d:.0f} u apart"
                                f"{' (posed)' if posed_pair else ''}; need {want:g} (move apart or lean less)")
        return None

    def _feet_prof(self, w, t, pg, lift=0.0):
        body = place_prof(pg["body"], self.x(w, t), lift)
        ys = GRID_Y0 + BAND * np.arange(GRID_N)
        return tuple(np.where(ys >= pg["foot_top"] - lift - 4, a, NAN) for a in body)

    def _carry_problem(self, w, t, on):
        """A prop carried (no reach at work) keeps 10 u from every head and feet, its holder's too."""
        held = self.holding(w, t)
        if not held or self.busy_sides(w, t) or self.walking(w, t):
            return None
        W = self.carry_point(w, t)
        hb = hold_box(held[0], w, 1 if self.facing(w, t) >= 0 else -1)
        box = box_prof(W[0] + hb[0], W[1] + hb[1], W[0] + hb[2], W[1] + hb[3])
        for o in on:
            if abs(self.x(o, t) - W[0]) > 400:
                continue
            for v in self.variants(o, t):
                pg = posed(o, *v[:4])
                for part, P in (("head", place_prof(pg["head"], self.x(o, t), v[4])),
                                ("feet", self._feet_prof(o, t, pg, v[4]))):
                    d = gap(P, box)
                    if d < MARGIN:
                        return (f"{held[0]} carried by {w} is {d:.0f} u from {o}'s {part}; need {MARGIN:g} "
                                "(put it down, pass it on or stand apart)")
        return None

    def _front_problem(self, p, x, w, t):
        """Depth: feet may hide behind a front prop; heads 10 u from it, resting paws (30 u discs) 10 u from it."""
        F = place_prof(prop_prof(p), x)
        xw = self.x(w, t)
        if xw + 450 < x - PROPS[p].w or xw - 450 > x + PROPS[p].w:
            return None
        busy = self.busy_sides(w, t)
        carry = ("r" if self.facing(w, t) >= 0 else "l") if self.holding(w, t) else None
        for v in self.variants(w, t):
            g = posed(w, *v[:4])
            d = gap(place_prof(g["head"], xw, v[4]), F)
            if d < MARGIN:
                return f"{w}'s head (x {xw:.0f}) is {d:.0f} u from {p}; need {MARGIN:g} (stand further off or lean less)"
            for s, (px, py) in g["paws"].items():
                if s in busy:
                    continue
                if s == carry:
                    cx, cy = self.carry_point(w, t)
                    px, py = cx - xw, cy + v[4]
                d = gap(box_prof(xw + px - PAW_R, py - v[4] - PAW_R, xw + px + PAW_R, py - v[4] + PAW_R), F)
                if d < MARGIN:
                    return (f"{w}'s resting {'left' if s == 'l' else 'right'} paw (x {xw + px:.0f}) is {d:.0f} u from "
                            f"{p}; need {MARGIN:g} (feet may hide behind it, paws may not)")
        return None

    def shot_problems(self, s0, s1, pre):
        ps = preset(pre)
        if ps is None:
            return [f"unknown preset (legal: {', '.join(PRESETS)}, or VW/VM/VC@x<n>)"]
        view, z, win = ps
        if view != self.t.view:
            return [f"{pre} is a {view} preset; this table is {self.t.view}"]
        if win[1] < self.st.rows[0] or win[3] > self.st.rows[1]:
            return [f"{pre} shows rows the {self.st.name} set doesn't have ({self.st.rows[0]}-{self.st.rows[1]})"]
        out, seen = [], set()
        for t in self.times(s0, s1):
            for w in self.cast:
                if not self.on_stage(w, t) or w in seen or self.entering(w, t):
                    continue
                if status_ext(*self.extent_lr(w, t), win) == "cut":
                    lift = " (hopping)" if self.lift(w, t) else ""
                    out.append(f"{w} at x {self.x(w, t):.0f}{lift} is cut at {t:.1f} s")
                    seen.add(w)
        return out

    def extent_lr(self, w, t):
        L, T, Rr = self.extent(w, t)
        return L, T, Rr

    def entering(self, w, t):
        """Inside an enter or exit beat: crossing the frame edge is the point of it."""
        return any(b[2] == w and b[3] in ("enter", "exit") and b[0] - 1e-9 <= t <= b[1] + 1e-9 for b in self.t.beats)

    def group_presets(self, s0, s1, who=None):
        """Vertical frames centred on a group (all on stage, each pair, each one) over s0-s1: VC, VM, VW@x<n>."""
        on = [w for w in self.cast if any(self.on_stage(w, t) for t in (s0, (s0 + s1) / 2, s1))]
        groups = [tuple(who)] if who else [tuple(on)] + [(a, b) for i, a in enumerate(on) for b in on[i + 1:]] + \
            [(a,) for a in on]
        out = []
        for g in groups:
            ts = self.times(s0, s1)
            L = min(self.extent(w, t)[0] for w in g for t in ts)
            Rr = max(self.extent(w, t)[2] for w in g for t in ts)
            for lab in ("VC", "VM", "VW"):
                name = f"{lab}@x{(L + Rr) / 2:.0f}"
                if name not in out:
                    out.append(name)
        return out

    def legal_presets(self, s0, s1):
        names = [p for p, (v, z, w) in PRESETS.items() if v == self.t.view]
        if self.t.view == "vert":
            names += self.group_presets(s0, s1)
        return [p for p in names if not self.shot_problems(s0, s1, p)]

    def framing_rows(self):
        """Shot rows for tools/framing_check.py: one per stretch where nobody moves."""
        rows = []
        for i, (s0, s1, pre) in enumerate(self.t.shots, 1):
            view, z, (x0, y0, x1, y1) = preset(pre)
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
            p = self.perfs[w]
            a, lean, sq, rlean, rsq = S._pose_args(a)
            a = [x for x in a if x != "front"]
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
            elif m in GAGS:
                self._gag(p, w, t0, t1, m, a, f)
            elif m in REACHES:
                self._arm_move(p, w, t0, t1, m, a, f, lean, sq, rlean, rsq)
        for w, p in self.perfs.items():           # carry: arms to the carry pose at the start and whenever a prop arrives
            if S.holding(w, 0.0):
                p.reach(0.0, 0.01, self.hand(w, 0.0), S.carry_point(w, 0.0))
            for pn in S.props:
                for tt, ww in S.hold[pn][1:]:
                    if ww == w and not any(b[0] <= tt + 0.3 <= b[1] and b[2] == w and b[3] in ("point", "draw")
                                           for b in self.table.beats):
                        side = self.hand(w, tt + 0.01)
                        p.reach(tt, tt + 0.3, side, S.carry_point(w, tt + 0.3))

    def hand(self, w, t):
        return "r" if self.sim.facing(w, t) >= 0 else "l"

    def carry_point(self, w, t):
        return self.sim.carry_point(w, t)

    def _lean(self, p, w, t0, t1, side, lean, sq):
        """Ease into the pose (lean toward side, crouch) by a quarter of the beat; ease back after it."""
        if not (lean or sq < 1):
            return
        e = min(0.3, 0.25 * (t1 - t0))
        p.to(t0, t0 + e, "io", lean=-lean * side, sq=sq, head_dy=CROUCH_DY * (1 - sq))
        p.to(t1, t1 + POSE_OUT, "io", lean=0.0, sq=1.0, head_dy=0.0)

    def _rest(self, p, side, t0, t1):
        p.to(t0, t1, "io", **{f"arm_{side}": 10 if side == "r" else -10, f"elb_{side}": -14 if side == "r" else 14})

    def _arm_move(self, p, w, t0, t1, m, a, f, lean, sq, rlean, rsq):
        S = self.sim
        lead = S._lead(w, t0)
        mid = (t0 + t1) / 2
        if m in ("point", "draw"):
            held = S.holding(w, t0)
            f0, f1 = 0.0, 1.0
            if m == "draw" and len(a) > 1:
                f0, f1 = (float(v) for v in a[1].split("-"))
            pts = S._targets(a[0], t0, f0, f1, m == "draw")
            tip = PROPS[held[0]].tip if held else 0.0
            side_n = 1 if pts[0][0] >= S.x(w, t0) else -1
            side = "r" if side_n > 0 else "l"
            self._lean(p, w, t0, t1, side_n, lean, sq)
            n = len(pts)
            for k, pt in enumerate(pts):
                ta = t0 - lead if k == 0 else t0 + 0.3 * (t1 - t0) + 0.7 * (t1 - t0) * (k - 1) / max(1, n - 1)
                tb = t0 + 0.3 * (t1 - t0) if k == 0 else t0 + 0.3 * (t1 - t0) + 0.7 * (t1 - t0) * k / (n - 1)
                if n == 1:
                    tb = t1
                p.reach(ta, tb, side, S.paw_for(w, t0, pt, tip, lean, sq))
            return
        if m in ("hand_over", "take"):
            rec = next(r for r in S.passes if r[0] == t0 and r[1] == t1 and (r[2] == w if m == "hand_over" else r[3] == w))
            _, _, giver, taker, pn, P, kind = rec
            g, q = self.perfs[giver], self.perfs[taker]
            sg = 1 if S.x(taker, t0) > S.x(giver, t0) else -1
            gs, ts = ("r" if sg > 0 else "l"), ("l" if sg > 0 else "r")
            if kind == "take":
                self._lean(q, taker, t0, t1, -sg, lean, sq)
                P = g.paw(t0, gs)[0]                          # the giver's real paw: pinch the prop where it is
                q.reach(t0 - S._lead(taker, t0), t0 + 0.45 * (t1 - t0), ts, P)
                self._rest(g, gs, t0 + 0.6 * (t1 - t0), t1)
                return
            take = len(a) > 2 and a[2] == "take"
            g1, r1 = (0.45, 0.35) if take else (0.35, 0.45)
            self._lean(g, giver, t0, t1, sg, lean, sq)
            self._lean(q, taker, t0, t1, -sg, rlean, rsq)
            g.reach(t0 - lead, t0 + g1 * (t1 - t0), gs, P)
            q.reach(t0 - S._lead(taker, t0), t0 + r1 * (t1 - t0), ts, P)
            self._rest(g, gs, t0 + 0.6 * (t1 - t0), t1)
            return
        side_n = 1 if f >= 0 else -1
        side = "r" if side_n > 0 else "l"
        if m == "pick_up":
            pt = S._prop_point(a[0], S.prop_where(a[0], t0), t0)
            self._lean(p, w, t0, t1, 1 if pt[0] >= S.x(w, t0) else -1, lean, sq)
            p.reach(t0 - lead, mid, side, pt)
            return
        held = S.holding(w, t0)[0]
        if m == "drop":
            return
        pt = S.st.spots[a[0]] if m == "place_on" else (MARKS[a[0]], PROPS[held].base_y - PROPS[held].h)
        self._lean(p, w, t0, t1, 1 if pt[0] >= S.x(w, t0) else -1, lean, sq)
        p.reach(t0 - lead, mid, side, pt)
        p.to(mid + 0.05, t1, "io", **{f"arm_{side}": 10 if side == "r" else -10})

    def _gag(self, p, w, t0, t1, m, a, f):
        d = t1 - t0
        fs = 1 if f > 0 else -1 if f < 0 else 1
        if m == "sway":
            n = int(a[0]) if a and a[0].isdigit() else max(1, int(round(d / 0.75)))
            for k in range(2 * n):
                p.to(t0 + d * k / (2 * n), t0 + d * (k + 1) / (2 * n), "io",
                     lean=0.0 if k == 2 * n - 1 else (6.0 if k % 2 == 0 else -6.0))
        elif m == "wiggle":
            n = max(2, int(round(d / 0.35)))
            if w == "Pip":
                p.dance(t0, t1, beats=n)
            else:
                for k in range(n):
                    p.to(t0 + d * k / n, t0 + d * (k + 1) / n, "io", lean=0.0 if k == n - 1 else (7.0 if k % 2 == 0 else -7.0))
                p.hop(t0, t1, n, 12 * SCALE[w])
                if "up" in a:
                    p.to(t0, t0 + 0.2, "io", arm_l=-150, arm_r=150, elb_l=-10, elb_r=10)
                    p.to(t1 - 0.2, t1, "io", arm_l=-10, arm_r=10, elb_l=14, elb_r=-14)
        elif m == "spin":
            end = a[0] if a else ("right" if f < 0 else "left")
            p.to(t0, t0 + 0.4 * d, "io", turn=0.0, hturn=0.0)
            p.to(t0 + 0.4 * d, t1, "back", turn=FACE[end])
            p.hop(t0, t1, 1, 10 * SCALE[w])
        elif m == "bow":
            p.to(t0, t0 + 0.4 * d, "io", lean=-10.0 * fs, head_dy=10 * SCALE[w])
            p.to(t0 + 0.6 * d, t1, "io", lean=0.0, head_dy=0.0)
        elif m == "puff" and w == "Pip":
            p.puff_up(t0, hold=max(0.0, d - 1.04), out=min(0.9, d - 0.14))

    def strokes(self, prop, t):
        """{path: fraction drawn} at t from the draw rows (a stroke follows the tip: 30 % in, then the path)."""
        out = {}
        for t0, t1, pn, path, f0, f1 in sorted(self.sim.strokes):
            if pn != prop or t < t0 + 0.3 * (t1 - t0):
                if pn == prop and path not in out and t >= t0:
                    out[path] = max(out.get(path, 0.0), f0)
                continue
            u = min(1.0, (t - t0 - 0.3 * (t1 - t0)) / max(1e-6, 0.7 * (t1 - t0)))
            out[path] = max(out.get(path, 0.0), f0 + (f1 - f0) * u)
        return {k: v for k, v in out.items() if v > 0}

    # --- drawing
    def held_pose(self, pn, w, t, st):
        side = self.hand(w, t)
        W, fa = self.perfs[w].paw(t, side, st)
        return W, fa

    def draw(self, t, cam, layers_out=None, post=True):
        """The world at t through cam (RGBA, cam-sized): set, back props, the cast (front walkers last), front props,
        paws at work and held props over them, set front."""
        S = self.sim
        _CUR.append(self)
        try:
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
                base = (S.prop_x(pn, tq), P.base_y) if wh[0] == "floor" else S.st.spots[wh[1]]
                (front_props if P.front else [None]).append((pn, base))
                if not P.front and P.draw_fn:
                    P.draw_fn(img, cam, base, tq, None)
            if self.extra_back:
                self.extra_back(img, cam, tq)
            size = img.size
            for w in sorted(self.perfs, key=lambda w: S.zorder(w, tq)):
                p = self.perfs[w]
                L = Image.new("RGBA", size, (0, 0, 0, 0))
                p.draw(L, tq, cam, d, sts[w])
                if layers_out is not None:
                    layers_out.append((p, L))
                img.alpha_composite(L)
            fp = Image.new("RGBA", size, (0, 0, 0, 0))
            for pn, base in front_props:
                if pn and PROPS[pn].draw_fn:
                    PROPS[pn].draw_fn(fp, cam, base, tq, None)
            img.alpha_composite(fp)
            if front_props:                              # the arm at work stays over a front prop (only there)
                al = Image.new("RGBA", size, (0, 0, 0, 0))
                for w, p in self.perfs.items():
                    for side in S.busy_sides(w, tq):
                        p.a._arm(al, cam, sts[w], side)
                a = np.minimum(np.asarray(al.getchannel("A")), np.asarray(fp.getchannel("A")))
                al.putalpha(Image.fromarray(a))
                img.alpha_composite(al)
            for pn in S.props:
                wh = S.prop_where(pn, tq)
                if wh[0] == "held" and PROPS[pn].draw_fn:
                    W, fa = self.held_pose(pn, wh[1], tq, sts[wh[1]])
                    ang = self._held_angle(pn, wh[1], tq, W)
                    hb = PROPS[pn].hold_box
                    PROPS[pn].draw_fn(img, cam, (W[0], W[1] + hb[3]) if pn != "marker" else W, tq, (wh[1], ang))
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
        finally:
            _CUR.pop()

    def _held_angle(self, pn, w, t, W):
        for t0, t1, ww, tgt in self.sim.points:
            if ww == w and t0 <= t <= t1 + 0.2:
                try:
                    dr = [q for q in self.sim.strokes if q[0] == t0 and f"{q[2]}.{q[3]}" == tgt]
                    pt = self.sim._targets(tgt, t0, *(dr[0][4:6] if dr else (0.0, 1.0)), bool(dr))
                except Refused:
                    break
                k = min(len(pt) - 1, int((t - t0) / max(1e-6, t1 - t0) * len(pt)))
                return math.degrees(math.atan2(pt[k][0] - W[0], pt[k][1] - W[1]))
        f = 1 if self.sim.facing(w, t) >= 0 else -1
        if w == "Pip" and pn == "marker":
            return PIP_ANGLE * f
        return math.degrees(math.atan2(0.45 * f, 0.9))

    def shot_at(self, t):
        for s0, s1, pre in self.table.shots:
            if s0 - 1e-9 <= t < s1 - 1e-9:
                return pre
        return self.table.shots[-1][2] if self.table.shots else ("W" if self.table.view == "land" else "VW@C")

    def still(self, t):
        view, z, (x0, y0, x1, y1) = preset(self.shot_at(t))
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
        return img, preset(stage.shot_at(t))[2], {"cast": cast, "layers": layers}

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
            S = stage.sim                       # v2: paws at a take, pass or draw; feet hidden behind a front prop
            if any(a <= t <= b and k in ("take", "give", "receive", "draw") for a, b, _, k in S.active[w]):
                allow.append(f"{SHORT[w]}.paws@{t:g}")
            for pn in S.props:
                x = S.prop_x(pn, t)
                if x is not None and PROPS[pn].front and S.on_stage(w, t):
                    F = place_prof(prop_prof(pn), x)
                    for v in S.variants(w, t):
                        pg = posed(w, *v[:4])
                        body = place_prof(pg["body"], S.x(w, t), v[4])
                        feet = tuple(np.where(GRID_Y0 + BAND * np.arange(GRID_N) >= pg["foot_top"] - v[4] - 4, a, NAN)
                                     for a in body)
                        if gap(feet, F, 60.0) < 60.0:
                            allow.append(f"{SHORT[w]}.feet@{t:g}")
    g.update(frame=frame, B=B, RES=hires.RES, name_of=lambda p: names[id(p)], head_mask=head_mask,
             SHEET=tuple(times), CLEARANCE_ALLOW=tuple(sorted(set(allow))), STAGE=stage)


# ---------------------------------------------------------------- v2: intent rows (the solver)
def _body_free(table, who, t):
    """When who's body is free before t: the latest end of its body beats that start before t."""
    return max([b[1] for b in table.beats if b[2] == who and b[3] in BODY and b[0] < t - 1e-9] + [0.0])


def fmt_rows(rows):
    return "; ".join(f"{a:g}-{b:g} {w} {m} {g}".strip() for a, b, w, m, g in rows)


def _try(table, rows, shots, old, window):
    new = copy.deepcopy(table)
    new.beats += rows
    new.shots = sorted(new.shots + list(shots))
    try:
        sim = Sim(new)
        bad = [p for p in (sim.problems() if window is None else sim.problems(*window)) if p not in old]
    except Refused as e:
        return new, [str(e)], None
    return new, bad, sim


def _pose_txt(lean, sq, r=""):
    return (f" {r}lean={lean:g}" if lean else "") + (f" {r}sq={sq:g}" if sq < 1 else "")


def _candidates(sim, t0, t1, who, move, arg, mover=None):
    """Rows to try, cheapest first: [walk_to x:<n>] [turn] move-with-pose. `mover` walks (the performer by default;
    for take / hand_over it may be the partner)."""
    mover = mover or who
    words, _, _, _, _ = Sim._pose_args(arg)
    words = [w for w in words if w != "front"]
    core = " ".join(words)
    pts, tip, partner = None, 0.0, None
    if move in ("point", "draw"):
        held = sim.holding(who, t0)
        tip = PROPS[held[0]].tip if held else 0.0
        f0, f1 = (0.0, 1.0)
        if move == "draw" and len(words) > 1 and re.match(r"^\d*\.?\d+-\d*\.?\d+$", words[1]):
            f0, f1 = (float(v) for v in words[1].split("-"))
        pts = sim._targets(words[0], t0, f0, f1, move == "draw")
    elif move == "pick_up":
        pts = [sim._prop_point(words[0], sim.prop_where(words[0], t0), t0)]
    elif move == "place_on":
        pts = [sim.st.spots[words[0]]] if words and words[0] in sim.st.spots else None
    elif move == "put_down":
        held = sim.holding(who, t0)
        pts = [(MARKS[words[0]], PROPS[held[0]].base_y - PROPS[held[0]].h)] if held and words and words[0] in MARKS else None
    elif move == "take":
        wh = sim.prop_where(words[0], t0) if words and words[0] in sim.props else ("none", "")
        partner = wh[1] if wh[0] == "held" else None
        pts = [sim.paw_at(partner, t0)] if partner and mover == who else None
    elif move == "hand_over":
        partner = words[1] if len(words) > 1 and words[1] in sim.cast else None
    if pts is None and partner is None:
        return []
    other = partner if mover == who else who
    x_now, f_now = sim.x(mover, t0), sim.fsign(mover, t0)
    tx = sum(p[0] for p in pts) / len(pts) if pts and mover == who else sim.x(other, t0)
    out = []
    span = 460 if pts and mover == who else 640
    for x in np.arange(round(tx) - span, round(tx) + span + 1, 8.0):
        if not 20 <= x <= 1900:
            continue
        side = 1 if tx >= x else -1
        rposes = [(0, 1.0)] if move not in ("hand_over",) else [(0, 1.0), (8, 0.94), (12, 0.88)]
        for lean in LEANS:
            for sq in SQS:
                if pts and mover == who:
                    dx, sy = shoulder_posed(who, side, "r" if side > 0 else "l", -lean * side, sq)
                    if any(math.hypot(p[0] - x - dx, p[1] - sy) > reach_len(who) * 0.95 + tip for p in pts):
                        continue
                elif move == "hand_over":         # both shoulders within reach of one point (some receiver pose)
                    xg, xo = (x, tx) if mover == who else (tx, x)
                    sg_ = 1 if xo > xg else -1
                    dg = shoulder_posed(who, sg_, "r" if sg_ > 0 else "l", -lean * sg_, sq)
                    do = shoulder_posed(partner, -sg_, "l" if sg_ > 0 else "r", 12.0 * sg_, 0.88)
                    if math.hypot(xg + dg[0] - xo - do[0], dg[1] - do[1]) > (reach_len(who) + reach_len(partner)) * REACH_USE:
                        continue
                cost = abs(x - x_now) / 40 + lean / 4 + (1 - sq) * 30 + (2 if side != f_now else 0)
                for rl, rs in rposes:
                    out.append((cost + rl / 6 + (1 - rs) * 20, float(x), side, lean, sq, rl, rs))
    out.sort()
    rows_out, seen = [], set()
    free = _body_free(sim.t, mover, t0)
    for cost, x, side, lean, sq, rl, rs in out:
      fs = side
      dx = abs(x - x_now)
      for inside in (False, True):
        rows, mt0 = [], t0
        if dx > 1:
            need = math.ceil(max(0.6, dx / SPEED[mover] * 1.15) * 10) / 10
            wdir = 1 if x > x_now else -1
            tt = 0.3 if wdir != fs else 0.0
            ws = round(t0 - tt - need, 2)
            if not inside and ws >= free - 1e-9 and ws >= 0:
                rows.append((ws, round(ws + need, 2), mover, "walk_to", f"x:{x:.0f}"))
                if tt:
                    rows.append((round(t0 - 0.3, 2), t0, mover, "turn", "right" if fs > 0 else "left"))
            elif inside and mover == who and t1 - t0 - need - tt >= 0.6:
                rows.append((t0, round(t0 + need, 2), mover, "walk_to", f"x:{x:.0f}"))
                mt0 = round(t0 + need + tt, 2)
                if tt:
                    rows.append((round(mt0 - 0.3, 2), mt0, mover, "turn", "right" if fs > 0 else "left"))
            else:
                continue
        elif fs != f_now:
            if not inside and t0 - 0.3 >= free - 1e-9:
                rows.append((round(t0 - 0.3, 2), t0, mover, "turn", "right" if fs > 0 else "left"))
            elif inside and mover == who and t1 - t0 >= 0.9:
                rows.append((t0, round(t0 + 0.3, 2), mover, "turn", "right" if fs > 0 else "left"))
                mt0 = round(t0 + 0.3, 2)
            else:
                continue
        elif inside:
            continue
        g = core + _pose_txt(lean, sq) + (_pose_txt(rl, rs, "r") if move == "hand_over" else "")
        key = (round(x), tuple((r[0], r[3]) for r in rows), g)
        if key in seen:
            continue
        seen.add(key)
        rows.append((mt0, t1, who, move, g))
        rows_out.append(rows)
      if len(rows_out) >= 240:
          break
    return rows_out


def pick_shot(table, t0, t1, who, also=()):
    """The tightest legal frame for t0-t1 with who (and `also`) whole in and nobody cut; None if none."""
    sim = Sim(table)
    if table.view == "vert":
        names = sim.group_presets(t0, t1, (who,) + tuple(also)) + sim.group_presets(t0, t1) + \
            [p for p, v in PRESETS.items() if v[0] == "vert"]
    else:
        names = sorted((p for p, v in PRESETS.items() if v[0] == "land"), key=lambda p: -PRESETS[p][1])
    names = sorted(dict.fromkeys(names), key=lambda p: -preset(p)[1])
    for pre in names:
        if sim.shot_problems(t0, t1, pre):
            continue
        win = preset(pre)[2]
        if all(status_ext(*sim.extent(w, t), win) == "in" for w in (who,) + tuple(also) for t in sim.times(t0, t1)):
            return pre
    return None


def _finish(table, rows, t0, t1, who, move, arg, add_shot, old):
    if not add_shot or any(s0 < t1 - 1e-9 and t0 < s1 - 1e-9 for s0, s1, _ in table.shots):
        return table, rows, None
    sim = Sim(table)
    also = []
    words = arg.split()
    if move == "hand_over" and len(words) > 1:
        also = [words[1]]
    if move == "take" and words and words[0] in sim.props:
        wh = sim.prop_where(words[0], t0)
        also = [wh[1]] if wh[0] == "held" else []
    pre = pick_shot(table, t0, t1, who, also)
    if pre:
        new, bad, _ = _try(table, [], [(t0, t1, pre)], old | set(sim.problems()), None)
        if not bad:
            return new, rows, pre
    return table, rows, None


def solve(table, t0, t1, who, move, arg, add_shot=True, nearest=True):
    """An intent row: the literal row if it works, else the cheapest stand x, side, lean and crouch (with a walk
    and/or turn before it) that passes every rule; plus the tightest legal shot when none covers t0-t1.
    Returns (new table, rows added, shot preset or None). Refused lists the nearest rows that do work."""
    old = set(Sim(table).problems())
    lit = [(t0, t1, who, move, arg)]
    new, bad, sim = _try(table, lit, [], old, None)
    if not bad:
        return _finish(new, lit, t0, t1, who, move, arg, add_shot, old)
    first = bad[0]
    sim0 = Sim(table)
    if move not in INTENT or who not in sim0.cast:
        raise Refused(" | ".join(bad))
    misses = []
    for mover in (who,):
        for rows in _candidates(sim0, t0, t1, who, move, arg, mover):
            new, bad, _ = _try(table, rows, [], old, (rows[0][0] - 0.1, t1 + POSE_OUT + 0.3))
            if not bad:
                new, bad, _ = _try(table, rows, [], old, None)
            if not bad:
                return _finish(new, rows, t0, t1, who, move, arg, add_shot, old)
            if len(misses) < 3 and not any(bad[0][:40] == m[1][:40] for m in misses):
                misses.append((rows, bad[0]))
    if not nearest:
        raise Refused(first)
    works = []
    words = arg.split()
    partner = None
    if move == "hand_over" and len(words) > 1:
        partner = words[1]
    elif move == "take" and words and words[0] in sim0.props and sim0.prop_where(words[0], t0)[0] == "held":
        partner = sim0.prop_where(words[0], t0)[1]
    if partner:
        for rows in _candidates(sim0, t0, t1, who, move, arg, partner)[:40]:
            new, bad, _ = _try(table, rows, [], old, None)
            if not bad:
                works.append(f"if {partner} moves first: {fmt_rows(rows)}")
                break
    for k in range(1, 9):
        if len(works) >= 3:
            break
        try:
            _, rows, _ = solve(table, t0 + 0.5 * k, t1 + 0.5 * k, who, move, arg, add_shot=False, nearest=False)
            works.append(f"later: {fmt_rows(rows)}")
            break
        except Refused:
            continue
    msg = f"{first} | the solver found no stand x, side, lean or crouch for {who} {move} {arg} at {t0:g}-{t1:g}"
    if works:
        msg += " | nearest that work: " + " || ".join(works)
    elif misses:
        msg += " | nearest tries (each still breaks a rule): " + " || ".join(f"{fmt_rows(r)} -> {b}" for r, b in misses)
    raise Refused(msg)
