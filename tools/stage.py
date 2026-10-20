"""The designer's only way to stage a beat table (docs/stage_kit_proposal.md, section 4): every call re-checks the
whole table with episodes/stage_kit.py and writes the row, or refuses (exit 1, nothing written) with the legal choices.

    python3 tools/stage.py menu [land|vert]                      marks, presets and who is whole in / out / cut where
    python3 tools/stage.py new ep13 porch vert "Snip@B:right Crinkle@D:left Pip@WL marker@Snip lantern@C" [--light 95]
    python3 tools/stage.py beat ep13 2.0-3.4 Snip walk_to C.L    (moves: see stage_kit; arg words after the move)
    python3 tools/stage.py beat ep13 0.6-2.8 Snip draw lantern.eye_l    an intent row: the kit works out the stand x,
                                     side, lean and crouch (and a walk or turn before it) and a legal frame, writes
                                     them, or refuses with the nearest rows that work  [--no-shot: add no frame]
    python3 tools/stage.py shot ep13 [7] 31.0-33.5 ML ["Snip@B Pip@A Crinkle@WR"]   (placements are asserted)
    python3 tools/stage.py shot ep13 4.0-6.0 VM@group[:Snip+Crinkle]   a vertical frame centred on the group
    python3 tools/stage.py legal ep13 2.0-3.4 Snip walk_to       the spots that move would accept
    python3 tools/stage.py show ep13                              the table's problems (none = PASS) and shot coverage
    python3 tools/stage.py sheet ep13 0.5,3.0,6.2 [out.png]       key-beat stills through the shot cameras
    python3 tools/stage.py covered-sheet ep13 moments.json 0.5,3.0,6.2 build/sb1
                                                               neutral sheet + checked coverage receipt (M82)
    python3 tools/stage.py test [--quick]                         move test: every move x mark x character, rendered
                                                                  and swept (writes reviews/stage_kit_move_test.md)
The table lives in reviews/<ep>_stage.md (the story-designer may run this; only stage.py writes the file).
"""
import copy
import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, os.path.join(ROOT, "episodes"))
sys.path.insert(0, TOOLS)

import stage_kit as SK  # noqa: E402

TEST_MD = os.path.join(ROOT, "reviews", "stage_kit_move_test.md")
TEST_STAMP = os.path.join(ROOT, "state", "stage_kit_test.json")


def refuse(msg, legal=None):
    print("REFUSED:", msg)
    if legal is not None:
        print("legal:", ", ".join(legal) if legal else "nothing at these times: change the times or the others first")
    sys.exit(1)


def write(table, path=None):
    sim = SK.Sim(table)
    table.save(path, sim.framing_rows())


def check_new(old, new, what):
    """Refuse if `new` has a problem `old` didn't have; return the new Sim."""
    before = set(SK.Sim(old).problems()) if old else set()
    sim = SK.Sim(new)
    bad = [p for p in sim.problems() if p not in before]
    return sim, bad


def spots_for(sim):
    return [m for m in SK.MARKS if m not in sim.st.blocked] + \
        [f"{m}.{s}" for m in SK.MARKS if m not in SK.OFF and m not in sim.st.blocked for s in "LR"]


def cmd_new(a):
    if len(a) < 4:
        sys.exit(__doc__)
    ep, set_name, view, places = a[0], a[1], a[2], a[3]
    light = float(a[a.index("--light") + 1]) if "--light" in a else None
    if set_name not in SK.SETS or view not in ("land", "vert"):
        refuse(f"set is one of {', '.join(SK.SETS)}; view land or vert")
    t = SK.Table(ep, set_name, view, light)
    for item in places.split():
        m = re.match(r"^(\w+)@(x:\d+|[\w.]+)(?::(left|right|front))?$", item)
        if not m:
            refuse(f"'{item}': write Who@spot[:facing] or prop@spot / prop@Who")
        who, at, f = m.groups()
        if who not in SK.CAST and who not in SK.PROPS:
            refuse(f"'{who}' is neither a character ({', '.join(SK.CAST)}) nor a kit prop ({', '.join(SK.PROPS)}); "
                   "episode props are added to SK.PROPS in episodes/stage_kit.py")
        t.start[who] = (at, f or "front")
    try:
        sim = SK.Sim(t)
        probs = sim.problems()
    except SK.Refused as e:
        refuse(str(e))
    if probs:
        refuse("; ".join(probs))
    if os.path.exists(t.path(ep)) and "--force" not in a:
        refuse(f"{os.path.relpath(t.path(ep), ROOT)} exists (add --force to start it again)")
    write(t)
    print(f"written {os.path.relpath(t.path(ep), ROOT)}: start", " ".join(f"{w}@{v[0]}" for w, v in t.start.items()))


def load(ep):
    if not os.path.exists(SK.Table.path(ep)):
        refuse(f"no table for {ep}: run stage.py new first")
    return SK.Table.load(ep)


def cmd_beat(a):
    flags = [x for x in a if x.startswith("--")]
    a = [x for x in a if not x.startswith("--")]
    if len(a) < 4:
        sys.exit(__doc__)
    ep, span, who, move, arg = a[0], a[1], a[2], a[3], " ".join(a[4:])
    old = load(ep)
    t0, t1 = SK._span(span)
    try:
        new, rows, shot = SK.solve(old, t0, t1, who, move, arg, add_shot="--no-shot" not in flags)
    except SK.Refused as e:
        SK.save_cache()
        refuse(str(e), legal_spots(old, t0, t1, who, move) if move in ("walk_to", "enter") else None)
    write(new)
    SK.save_cache()
    print(f"beat {t0:g}-{t1:g} {who} {move} {arg}: OK, wrote {SK.fmt_rows(rows)}" +
          (f"; shot {t0:g}-{t1:g} {shot}" if shot else "") + f" ({len(new.beats)} beats)")


def legal_spots(table, t0, t1, who, move):
    out = []
    sim0 = SK.Sim(table)
    for sp in spots_for(sim0):
        if sp in SK.OFF:
            continue
        new = copy.deepcopy(table)
        new.beats.append((t0, t1, who, move, sp))
        if not [p for p in SK.Sim(new).problems() if p not in set(sim0.problems())]:
            out.append(sp)
    return out


def cmd_shot(a):
    if len(a) < 3:
        sys.exit(__doc__)
    ep, rest = a[0], a[1:]
    if re.match(r"^\d+$", rest[0]) and len(rest) >= 3:
        rest = rest[1:]
    span, pre, places = rest[0], rest[1], rest[2] if len(rest) > 2 else ""
    old = load(ep)
    t0, t1 = SK._span(span)
    sim0 = SK.Sim(old)
    g = re.match(r"^(VW|VM|VC)@group(?::([\w+]+))?$", pre)
    if g:
        names = sim0.group_presets(t0, t1, tuple(g.group(2).split("+")) if g.group(2) else None)
        pre = next(n for n in names if n.startswith(g.group(1)))
    for s0, s1, p in old.shots:
        if t0 < s1 - 1e-9 and s0 < t1 - 1e-9:
            refuse(f"overlaps shot {s0:g}-{s1:g} {p}")
    for item in places.split():
        m = re.match(r"^(\w+)@([\w.]+)$", item)
        if not m or m.group(1) not in sim0.cast:
            refuse(f"'{item}': write Who@spot for a character in the table")
        now = sim0.spot_of(m.group(1), t0)
        if now != m.group(2):
            refuse(f"{m.group(1)} is on {now} at {t0:g} s, not {m.group(2)} (move with a beat first)")
    new = copy.deepcopy(old)
    new.shots.append((t0, t1, pre))
    new.shots.sort()
    sim, bad = check_new(old, new, "shot")
    if bad:
        refuse(" | ".join(bad), sim0.legal_presets(t0, t1))
    write(new)
    print(f"shot {t0:g}-{t1:g} {pre}: OK")


def cmd_legal(a):
    ep, span, who, move = a[0], a[1], a[2], a[3]
    t0, t1 = SK._span(span)
    tab = load(ep)
    if move == "shot":
        print("legal:", ", ".join(SK.Sim(tab).legal_presets(t0, t1)))
    elif move in SK.INTENT:
        try:
            _, rows, shot = SK.solve(tab, t0, t1, who, move, " ".join(a[4:]))
            print("would write:", SK.fmt_rows(rows) + (f"; shot {shot}" if shot else ""))
        except SK.Refused as e:
            print("REFUSED:", e)
        SK.save_cache()
    else:
        print("legal:", ", ".join(legal_spots(tab, t0, t1, who, move)))


def cmd_show(a):
    tab = load(a[0])
    sim = SK.Sim(tab)
    probs = sim.problems()
    cov, gaps, last = 0.0, [], 0.0
    for s0, s1, p in tab.shots:
        if s0 > last + 1e-6:
            gaps.append(f"{last:g}-{s0:g}")
        cov += s1 - s0
        last = max(last, s1)
    if last < sim.end - 1e-6:
        gaps.append(f"{last:g}-{sim.end:g}")
    for p in probs:
        print("PROBLEM", p)
    print(f"{len(tab.beats)} beats, {len(tab.shots)} shots, {len(sim.bespoke)} bespoke; shots cover {cov:g} of "
          f"{sim.end:g} s" + (f"; no shot at {', '.join(gaps)}" if gaps else ""))
    print("stage:", "PASS" if not probs and not gaps else "FAIL")
    return 0 if not probs and not gaps else 1


def cmd_menu(a):
    view = a[0] if a else "land"
    print("marks:", "  ".join(f"{m} {x}" for m, x in SK.MARKS.items()))
    print("spacing (centres, framing sizes + 10):", ", ".join(f"{x}-{y} {SK.spacing(x, y):.0f}" for x in SK.CAST
                                                              for y in SK.CAST if x != y))
    for a_, b_ in (("Snip", "Crinkle"), ("Crinkle", "Snip"), ("Snip", "Pip"), ("Pip", "Snip"), ("Crinkle", "Pip"),
                   ("Pip", "Crinkle")):
        ho = SK.handover_distance(a_, b_)
        print(f"hand-over pair {a_} (L) + {b_} (R):", f"{ho[0]:.0f} u apart, pass at y {ho[1]:.0f}" if ho else "none")
    print("v2 work spots beside the lantern (front prop; centre distance):",
          ", ".join(f"{w} {SK.front_spot(w, 'lantern', 1):.0f}" for w in SK.CAST))
    print("v2 poses: lean=0-12 (deg toward the target), sq=0.88-1 (crouch); passes: lean= sq= (giver), rlean= rsq= "
          "(receiver); moves: take, draw, sway, wiggle [up], spin [left|right], bow, puff (Pip); walk_to <spot> front;"
          " vertical frames VW|VM|VC@x<n> (shot ... VM@group)")
    for name, (v, z, win) in SK.PRESETS.items():
        if v != view:
            continue
        row = []
        for w in SK.CAST:
            st = {m: SK.status(w, x, win) for m, x in SK.MARKS.items()}
            row.append(f"{w}: in {' '.join(m for m in st if st[m] == 'in') or '-'} / cut "
                       f"{' '.join(m for m in st if st[m] == 'cut') or '-'}")
        print(f"{name} {z:g}x x {win[0]:.0f}-{win[2]:.0f} y {win[1]:.0f}-{win[3]:.0f} :: " + " | ".join(row))


def cmd_sheet(a):
    st = SK.Stage.load(a[0])
    times = [float(x) for x in a[1].split(",")]
    out = a[2] if len(a) > 2 else os.path.join(ROOT, "build", a[0], "sheet.png")
    print(st.sheet(times, out))


def cmd_covered_sheet(a):
    """Opt-in coverage check; leaves the legacy sheet command unchanged."""
    if len(a) != 4:
        sys.exit(__doc__)
    import storyboard_check
    ep, requirements, samples, out = a
    try:
        times = [float(x) for x in samples.split(",")]
        st = SK.Stage.load(ep)
        for t in times:
            if not any(start <= t < end for start, end, _ in st.table.shots):
                raise ValueError(f"no explicit shot at {t:g}; refusing the renderer's fallback camera")
        print(storyboard_check.write_bundle(st.still, times, st.sim.end, requirements, SK.Table.path(ep), out))
        print("Declared coverage and file integrity PASS; blind story and safety reviews still required.")
    except (OSError, ValueError, TypeError) as exc:
        refuse(str(exc))


# ---------------------------------------------------------------- move test
MOVE_CASES = ("enter", "exit", "walk_to", "turn", "look", "nod", "shake", "react", "hop", "hold", "point",
              "pick_up", "put_down", "place_on", "drop", "hand_over",
              "take", "sway", "wiggle", "spin", "bow", "puff", "draw", "pass")      # v2: the last 8


def _case(who, mark, move):
    """(table, sample times) for one move at one mark, on the playroom (every mark is usable there)."""
    t = SK.Table("kittest", "playroom", "land")
    start = "OFF_L" if move == "enter" else mark
    t.start[who] = (start, "right" if move != "enter" else "right")
    beats = []
    if move == "enter":
        beats.append((0.5, 3.0, who, "enter", mark))
    elif move == "exit":
        beats.append((0.5, 3.0, who, "exit", "OFF_R"))
    elif move == "walk_to":
        order = ["A", "B", "C", "D", "E"]
        dest = "C" if mark in ("WL", "WR", "A", "E") else {"B": "D", "C": "A", "D": "B"}[mark]
        beats.append((0.5, 2.5, who, "walk_to", dest))
    elif move == "turn":
        beats.append((0.5, 0.9, who, "turn", "left"))
    elif move == "look":
        beats.append((0.5, 0.9, who, "look", "camera"))
    elif move in ("nod", "shake"):
        beats.append((0.5, 1.3, who, move, ""))
    elif move == "react":
        beats.append((0.5, 1.6, who, "react", "delighted"))
    elif move == "hop":
        beats.append((0.5, 1.3, who, "hop", ""))
    elif move == "hold":
        beats.append((0.5, 1.5, who, "hold", ""))
    elif move == "point":
        beats.append((0.5, 1.2, who, "point", "E" if SK.MARKS[mark] < 1400 else "A"))
        if SK.MARKS[mark] >= 1400:
            t.start[who] = (mark, "left")
    elif move in ("pick_up", "put_down", "place_on", "drop"):
        t.start["block"] = ("spot:box_top" if move == "pick_up" else who, "")
        if move == "pick_up":
            beats.append((0.5, 1.5, who, "pick_up", "block"))
        else:
            arg = {"put_down": next((m for m in ("A", "B", "C", "D", "E", "WR", "WL")
                                     if abs(SK.MARKS[m] - SK.MARKS[mark]) == 320), "A"),
                   "place_on": "box_top", "drop": ""}[move]
            beats.append((0.5, 1.5, who, move, arg))
    elif move == "hand_over":
        other = "Crinkle" if who != "Crinkle" else "Snip"
        t.start[who] = (f"{mark}.L", "right")
        t.start[other] = (f"{mark}.R", "left")
        t.start["block"] = (who, "")
        beats.append((0.5, 1.7, who, "hand_over", f"block {other}"))
    elif move == "take":                  # the solver places the taker
        other = "Crinkle" if who != "Crinkle" else "Snip"
        t.start[who] = (mark, "right")
        t.start[other] = (f"x:{min(1900, SK.MARKS[mark] + 520):.0f}", "left")
        t.start["marker"] = (other, "")
        t.shots = [(0.0, 3.2, "W")]
        return _solved(t, (0.9, 2.1, who, "take", "marker")), [1.0, 1.4, 1.9]
    elif move in ("sway", "wiggle", "spin", "bow", "puff"):
        beats.append((0.5, {"spin": 1.3, "bow": 1.5}.get(move, 1.7), who, move, "up" if move == "wiggle" else ""))
    elif move == "draw":                  # the solver places who; the lantern stands on the mark (porch floor)
        t = SK.Table("kittest", "porch", "land")
        t.start = {who: (f"x:{max(20, SK.MARKS[mark] - 330):.0f}", "right"), "marker": (who, ""), "lantern": (mark, "")}
        t.shots = [(0.0, 3.2, "W")]
        return _solved(t, (0.5, 1.9, who, "draw", "lantern.eye_l")), [0.8, 1.2, 1.7]
    elif move == "pass":                  # the solver finds lean / crouch passes (Crinkle-Pip included)
        other = "Pip" if who != "Pip" else "Crinkle"
        t.start[who] = (mark, "right")
        t.start[other] = (f"x:{min(1900, SK.MARKS[mark] + 420):.0f}", "left")
        t.start["marker"] = (who, "")
        t.shots = [(0.0, 3.2, "W")]
        return _solved(t, (0.9, 2.1, who, "hand_over", f"marker {other}")), [1.0, 1.4, 1.9]
    t.beats = beats
    t.shots = [(0.0, 3.2, "W")]          # the kit judges framing only against a declared shot
    return t, [0.6, 1.0, 1.4, 2.4] if move in ("enter", "exit", "walk_to") else [0.8, 1.1, 1.5]


def _solved(t, beat):
    try:
        return SK.solve(t, *beat, add_shot=False, nearest=False)[0]
    except SK.Refused as e:
        return str(e)


def run_case(args):
    who, mark, move = args
    import numpy as np
    sys.path.insert(0, TOOLS)
    import clearance_check as CC
    t, times = _case(who, mark, move)
    if isinstance(t, str):
        return who, mark, move, "R", t[:140]
    try:
        sim = SK.Sim(t)
        probs = sim.problems()
    except SK.Refused as e:
        probs = [str(e)]
    if probs:
        return who, mark, move, "R", probs[0][:140]
    st = SK.Stage(t)
    g = {}
    SK.export(g, st, times)
    hits = []
    for tt in times:
        bgs = []
        orig = SK.background

        def bgw(*aa, **kw):
            im = orig(*aa, **kw)
            bgs.append(im.copy())
            return im
        SK.background = bgw
        try:
            img, win, info = g["frame"](tt)
        finally:
            SK.background = orig
        props = CC.prop_mask(img, bgs[-1], info["layers"])
        parts = {}
        for p, L in zip(info["cast"], info["layers"]):
            parts.update(CC.part_masks(g, p, L))
        allow = CC.allowed_at(g["CLEARANCE_ALLOW"], tt)
        for key, d, at, ok in CC.sweep_frame(props, parts, g["RES"], 10.0, allow):
            if not ok:
                hits.append(f"{tt:g} {key} {d:g} u")
    for tt in times:     # framing: everyone on stage must be in or out of W, never cut
        for w in sim.cast:
            if sim.on_stage(w, tt) and not sim.entering(w, tt) and SK.status(w, sim.x(w, tt), SK.PRESETS["W"][2], sim.lift(w, tt)) == "cut" \
                    and not (mark in ("WL", "WR") and w != "Pip"):
                hits.append(f"{tt:g} {w} cut in W")
    return who, mark, move, ("X" if hits else "ok"), "; ".join(hits)[:160]


def cmd_test(a):
    import datetime
    import multiprocessing as mp
    marks = ("WL", "A", "B", "C", "D", "E", "WR")
    moves = MOVE_CASES if "--quick" not in a else ("walk_to", "hand_over", "point", "place_on")
    cases = [(w, m, mv) for w in SK.CAST for mv in moves for m in marks]
    with mp.get_context("fork").Pool(8) as pool:
        res = pool.map(run_case, cases)
    import framestore
    code = framestore.code_hash(os.path.join(ROOT, "episodes", "stage_kit.py"))
    SK.save_cache()
    bad = [r for r in res if r[3] == "X"]
    L = [f"# Stage kit move test ({datetime.date.today():%d %b %Y}; `python3 tools/stage.py test`)", "",
         f"Kit code hash {code[:12]}. ok = the kit accepts the move and the rendered frames are clear (clearance "
         "sweep, 10 u, the holder's paws allowed) and nobody is cut in W; R = the kit refuses it (reason below); "
         "X = accepted but the render touches or cuts (a kit bug).", "",
         "| Who | Move | " + " | ".join(marks) + " |", "|---|---|" + "---|" * len(marks)]
    by = {(w, mv, m): (s, why) for w, m, mv, s, why in res}
    for w in SK.CAST:
        for mv in moves:
            L.append(f"| {w} | {mv} | " + " | ".join(by[(w, mv, m)][0] for m in marks) + " |")
    L += ["", "## Refusals and failures", ""]
    seen = set()
    for w, m, mv, s, why in res:
        if s != "ok" and (mv, why[:60]) not in seen:
            L.append(f"- {s} {w} {mv} at {m}: {why}")
            seen.add((mv, why[:60]))
    L += ["", f"Result: {'PASS' if not bad else 'FAIL'} ({sum(r[3] == 'ok' for r in res)} ok, "
              f"{sum(r[3] == 'R' for r in res)} refused, {len(bad)} failed of {len(res)})"]
    if "--quick" not in a:
        with open(TEST_MD, "w", encoding="utf-8") as f:
            f.write("\n".join(L) + "\n")
        os.makedirs(os.path.dirname(TEST_STAMP), exist_ok=True)
        json.dump({"hash": code, "result": "PASS" if not bad else "FAIL", "date": f"{datetime.datetime.now():%Y-%m-%d %H:%M}"},
                  open(TEST_STAMP, "w"), indent=1)
    print("\n".join(L[-1:]))
    for r in bad:
        print("X", r)
    return 0 if not bad else 1


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, a = argv[0], argv[1:]
    try:
        fn = {"new": cmd_new, "beat": cmd_beat, "shot": cmd_shot, "legal": cmd_legal, "show": cmd_show,
              "menu": cmd_menu, "sheet": cmd_sheet, "covered-sheet": cmd_covered_sheet, "test": cmd_test}[cmd]
    except KeyError:
        sys.exit(__doc__)
    try:
        return fn(a) or 0
    except SK.Refused as e:
        refuse(str(e))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
