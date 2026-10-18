"""Full prop clearance sweep over an episode rough script (M77: a Lead pick was checked only on the rows that failed,
and the new rope lay across a foot; the drape covered Pip's feet).

    python3 tools/clearance_check.py episodes/ep12_rough_r3.py --check [--need 10] [--times 9.6,36.6]
                                     [--allow sn.paws@9.6] [--allow cr.paws]

Runs the script's own set-up (its __main__ block with no flags; the script is not changed), then for every frame
time it defines (its SHEET and FRAMES, and those of the rough script it builds on, `M`; plus --times) renders the
frame and finds every prop pixel: the frame minus its background and minus the characters' own layers (toys, ropes,
the cushion, the "?"). It measures the gap from the props to each character's head (Crinkle's scarf too, when the
script has head_scarf), feet (the lowest 60 u of the figure) and paws (a 30 u disc at each paw). A gap under --need
fails, unless --allow names that <who>.<part> (sn, pp, cr; head, feet, paws), for all times or "@<time>": a held prop
touches its holder's paws by design. A frame that can't be rendered is "not checked" and the sweep can't PASS.

The result goes to state/clearance.json under the episode (script, code hash, PASS/FAIL, times, allowed contacts).
tools/gate.py refuses gate1 or gate1b PASS while the episode's newest rough script has no PASS for its current code.
Exit 1 on FAIL. The pure parts (prop_mask, gap, sweep_frame) are tested in tools/regress.py.
"""
import argparse
import datetime
import json
import os
import re
import runpy
import sys
import time

import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
EPISODES = os.path.join(ROOT, "episodes")
STAMPS = os.path.join(ROOT, "state", "clearance.json")
NEED = 10.0
FOOT_BAND, PAW_R = 60.0, 30.0
TOL = 24  # channel difference that counts as a prop pixel (a re-composite is exact; this only absorbs rounding)
PARTS = ("head", "feet", "paws")


# ---------------------------------------------------------------- pure parts (no episode code)

def prop_mask(img, bg, layers, tol=TOL):
    """Pixels where the frame differs from its background with only the characters composited on it."""
    from PIL import Image
    exp = bg.copy()
    for L in layers:
        exp.alpha_composite(L)
    a = np.asarray(img.convert("RGBA")).astype(np.int16)
    b = np.asarray(exp.convert("RGBA") if isinstance(exp, Image.Image) else exp).astype(np.int16)
    return np.abs(a - b)[..., :3].max(-1) > tol


def gap(props, part, step, need):
    """(gap in units, (col, row) of the nearest prop pixel) between two masks at `step` pixels per unit; the search
    stops at need + 2 units, so a far gap comes back as need + 2."""
    ys, xs = np.nonzero(part)
    if len(xs) == 0:
        return None, None
    pad = int((need + 2) * step)
    r0, r1 = max(0, ys.min() - pad), ys.max() + pad + 1
    c0, c1 = max(0, xs.min() - pad), xs.max() + pad + 1
    k = max(1, int(step))
    P, Q = props[r0:r1:k, c0:c1:k], part[r0:r1:k, c0:c1:k]
    both = P & Q
    if both.any():
        y, x = np.argwhere(both)[0]
        return 0.0, (c0 + x * k, r0 + y * k)
    pp, qq = np.argwhere(P), np.argwhere(Q)
    if not len(pp):
        return need + 2, None
    best, at = 1e9, None
    for i in range(0, len(pp), 2000):
        d = np.sqrt(((pp[i:i + 2000, None, :] - qq[None, :, :]) ** 2).sum(-1)).min(1)
        j = int(d.argmin())
        if d[j] < best:
            best, at = float(d[j]), pp[i + j]
    best *= k / step
    return min(best, need + 2), (c0 + at[1] * k, r0 + at[0] * k)


def sweep_frame(props, parts, step, need, allowed=()):
    """[(who.part, gap, at, allowed)] for every part closer than `need` to a prop. parts: {"sn.feet": mask, ...}."""
    hits = []
    for key, m in parts.items():
        g, at = gap(props, m, step, need)
        if g is not None and g < need:
            hits.append((key, round(g, 1), at, key in allowed))
    return hits


def allowed_at(allow, t):
    """The who.part keys --allow lets touch at time t ("sn.paws" always, "sn.paws@9.6" only then)."""
    out = set()
    for a in allow:
        key, _, when = a.partition("@")
        if not when or abs(float(when) - t) < 1e-6:
            out.add(key)
    return out


# ---------------------------------------------------------------- the episode script

def load(script):
    """The script's globals after its own __main__ set-up (no flags), and a list that collects each background."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
    argv, sys.argv = sys.argv, [script]
    try:
        g = runpy.run_path(script, run_name="__main__")
    finally:
        sys.argv = argv
    bgs = []
    here = os.path.dirname(os.path.abspath(script))
    spaces = [g] + [vars(m) for m in list(sys.modules.values())
                    if getattr(m, "__file__", None) and os.path.dirname(os.path.abspath(m.__file__)) == here]
    for ns in spaces:
        for name in ("background2", "background"):
            fn = ns.get(name)
            if callable(fn) and not getattr(fn, "_clearance", False):
                def wrap(*a, _fn=fn, **kw):
                    im = _fn(*a, **kw)
                    bgs.append(im.copy())
                    return im
                wrap._clearance = True
                ns[name] = wrap
    return g, bgs


def frame_times(g, extra=()):
    ts = set(extra)
    for ns in (g, vars(g["M"]) if "M" in g and hasattr(g["M"], "__dict__") else {}):
        for name in ("SHEET", "FRAMES"):
            ts |= {float(t) for t in ns.get(name, ()) or ()}
    return sorted(ts)


def part_masks(g, p, layer_img):
    """{"<who>.head|feet|paws": mask} for one cast member (masks at the frame's pixel grid)."""
    B, res = g["B"], g["RES"]
    who = g["name_of"](p)
    body = np.asarray(layer_img.getchannel("A")) > 160
    head = (g.get("head_scarf") or g["head_mask"])(p)
    ys = np.nonzero(body.any(1))[0]
    feet = body.copy()
    if len(ys):
        feet[:max(0, int(ys.max() - FOOT_BAND * res)), :] = False
    paws = np.zeros_like(body)
    yy, xx = np.ogrid[:body.shape[0], :body.shape[1]]
    for side in ("l", "r"):
        try:
            pt = p.paw(B.T_DRAW, side)[0]
        except Exception:  # a performer without paw points: no paw mask, the head and feet still count
            continue
        cx, cy = pt[0] * res, (pt[1] - B.LAND_Y0) * res
        paws |= (xx - cx) ** 2 + (yy - cy) ** 2 <= (PAW_R * res) ** 2
    return {f"{who}.head": head, f"{who}.feet": feet, f"{who}.paws": paws & body if (paws & body).any() else paws}


def name_at(g, info, at):
    """The toy (or extra item) at a prop pixel, for the report."""
    res, y0 = g["RES"], g["B"].LAND_Y0
    x, y = at[0] / res, at[1] / res + y0
    for name, box, *_ in info.get("toys", ()):
        if box[0] - 6 <= x <= box[2] + 6 and box[1] - 6 <= y <= box[3] + 6:
            return name
    for name, fn in info.get("extra", ()):
        try:
            if g["draw_mask"](fn)[at[1], at[0]]:
                return name
        except Exception:
            pass
    return f"prop at ({x:.0f}, {y:.0f})"


def sweep(script, need=NEED, extra=(), allow=(), log=print):
    g, bgs = load(script)
    res = {"hits": [], "not_checked": [], "times": []}
    for t in frame_times(g, extra):
        del bgs[:]
        try:
            img, win, info = g["frame"](t)
            props = prop_mask(img, bgs[-1], info["layers"])
            parts = {}
            for p, L in zip(info["cast"], info["layers"]):
                parts.update(part_masks(g, p, L))
        except Exception as e:  # a frame the script can't draw is reported, never passed
            res["not_checked"].append(f"{t:g} ({type(e).__name__}: {e})"[:120])
            log(f"[{t:g}] not checked: {type(e).__name__}: {e}")
            continue
        res["times"].append(t)
        hits = sweep_frame(props, parts, g["RES"], need, allowed_at(allow, t))
        for key, d, at, ok in hits:
            what = name_at(g, info, at) if at is not None else "?"
            res["hits"].append({"time": t, "part": key, "gap": d, "prop": what, "allowed": ok})
        log(f"[{t:g}] " + ("clear" if not hits else "; ".join(
            f"{k} {d:g} u from {name_at(g, info, at) if at is not None else '?'}{' (allowed)' if ok else ''}"
            for k, d, at, ok in hits)))
    res["result"] = "PASS" if res["times"] and not res["not_checked"] and not any(
        not h["allowed"] for h in res["hits"]) else "FAIL"
    return res


def stamp(script, res, need, allow, path=None):
    sys.path.insert(0, EPISODES)
    import framestore
    path = path or STAMPS
    ep = re.match(r"(ep\d+)", os.path.basename(script)).group(1)
    data = {}
    if os.path.exists(path):
        data = json.load(open(path, encoding="utf-8"))
    data[ep] = {"script": os.path.relpath(os.path.abspath(script), ROOT), "hash": framestore.code_hash(script),
                "result": res["result"], "need": need, "allow": list(allow), "times": res["times"],
                "not_checked": res["not_checked"], "date": f"{datetime.datetime.now():%Y-%m-%d %H:%M}",
                "fails": [h for h in res["hits"] if not h["allowed"]][:20]}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


# ---------------------------------------------------------------- gate.py asks this

def newest_rough(ep, episodes=None):
    """The episode's newest rough script (ep12_rough.py < _r1 < _r2 ...), or None."""
    d = episodes or EPISODES
    best = None
    for f in os.listdir(d) if os.path.isdir(d) else ():
        m = re.match(re.escape(ep) + r"_rough(?:_r(\d+))?\.py$", f)
        if m and (best is None or int(m.group(1) or 0) > best[0]):
            best = (int(m.group(1) or 0), os.path.join(d, f))
    return best[1] if best else None


def gate_problem(ep, episodes=None, path=None):
    """None when the episode may pass a gate; else what to run (M77)."""
    rough = newest_rough(ep, episodes)
    if not rough:
        return None
    rel = os.path.relpath(rough, ROOT)
    rec = {}
    if os.path.exists(path or STAMPS):
        rec = json.load(open(path or STAMPS, encoding="utf-8")).get(ep) or {}
    run = f"python3 tools/clearance_check.py {rel} --check (M77: the full prop clearance sweep before a gate)"
    if rec.get("script") != rel:
        return f"no clearance sweep for {rel}: run {run}"
    if rec.get("result") != "PASS":
        return f"the clearance sweep of {rel} is {rec.get('result')} ({len(rec.get('fails', []))} contacts): fix, then {run}"
    sys.path.insert(0, EPISODES)
    import framestore
    framestore.code_hash.cache_clear() if hasattr(framestore.code_hash, "cache_clear") else None
    if rec.get("hash") != framestore.code_hash(rough):
        return f"{rel} (or a file it imports) changed since its clearance sweep ({rec.get('date')}): run {run}"
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Full prop-to-head/feet/paws clearance sweep of an episode rough script.")
    ap.add_argument("script")
    ap.add_argument("--check", action="store_true", required=True)
    ap.add_argument("--need", type=float, default=NEED)
    ap.add_argument("--times", default="")
    ap.add_argument("--allow", action="append", default=[])
    ap.add_argument("--file", help="stamp file (tests)")
    a = ap.parse_args(argv)
    for x in a.allow:
        if not re.match(r"^(sn|pp|cr)\.(head|feet|paws)(@[\d.]+)?$", x):
            ap.error(f"--allow {x}: use <sn|pp|cr>.<head|feet|paws>[@<time>]")
    t0 = time.time()
    extra = [float(x) for x in a.times.split(",") if x.strip()]
    res = sweep(a.script, a.need, extra, a.allow)
    stamp(a.script, res, a.need, a.allow, a.file)
    bad = [h for h in res["hits"] if not h["allowed"]]
    print(f"clearance_check: {res['result']}: {len(res['times'])} frames, {len(bad)} contacts under {a.need:g} u, "
          f"{len(res['not_checked'])} not checked ({time.time() - t0:.0f} s); stamped in "
          f"{os.path.relpath(a.file or STAMPS, ROOT)}")
    return 0 if res["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
