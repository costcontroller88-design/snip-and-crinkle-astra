"""Check a plan before it leaves the story-designer (agent ratings 8 Oct: M2, M3, M5, M7, M14, M16, M17).

    python3 tools/plan_check.py reviews/ep12_plan.md
    python3 tools/plan_check.py reviews/ep11_short_plan.md

Exits 1 and lists every failure. A plan must contain a line `**Length:** <seconds> s` (≤60 s counts as a Short) and
a line `**Lesson beat:** <a>-<b> s` (the mistake +-2 s; H1), and
these tables (header cells in this order; extra text after a header word is fine, e.g. "Set-up (s)"):

  Gag table (docs/COMEDY_PLAYBOOK.md sections 3-4):
  | Time (s) | Type | Trait | Set-up (s) | Pause (s) | Break (s) | Break size (%) | Joke signal | Reaction (s) | Sound | Topper | Test |
    Time "a-b"; Type G1-G9; set-up ≥1.5; pause 0.3-0.6; break ≥0.8; break size ≥10 (% of frame width, or a close-up);
    reaction ≥1.0; Test says PASS; no empty cell (write "none" for no topper). Density: Shorts first gag by 5 s, then
    a gag every ≤15 s (or by 2 s after the lesson beat when the mistake is the hook); episodes every ≤20 s, except
    that the gap across the lesson beat may reach 25 s; no gag starts inside the lesson beat (playbook 4: none on the
    erring moment). Never the same type twice in a row. Episodes: ≥3 types, a G4 or G5
    (rule of three), a row whose Trait says "callback", ≥1 topper.
  Key actions table (lesson 2; M3, M14):
  | Key action | Time (s) | Object | Size (%) | Uncovered (s) |
    every key action (the cause, the mistake, the fix, the wow's cause) lasts ≥1.0 s, its object ≥10% of the frame
    width in that shot, uncovered ≥1.0 s.
  Storyboard table (gate 1b; M5):
  | Frame (s) | Shot | Shows |
    episodes 10-12 frames, Shorts 6-12, but up to 14 (PASS with a WARN line) when the key actions need more frames
    (audit M11: the fewest frames that touch every key action's span, plus 2 for set-up and finish, exceed the cap);
    a frame inside every key action's time span (so the cause of every change is on the sheet).
  Props table (M7):
  | Prop | Colour | ... |  every object's colour and state; no empty cell.
  Measured checks table, under a `## Measured checks` heading (M26-M29: measure first):
  | Check | Need | Measured | Source |
    one row for every distance rule in the plan ("≥N from", "≥N clear", "≥N and"; also "at least N", ">= N" and
    "N or more" before from/clear/and; audit L1): Need is that N; Measured is a
    number from the real code with its Source (`--check` or a still path), or "estimate" (allowed in a plan for a
    scene not built yet; tools/handover_check.py fails on any estimate left, so the animator measures before building).
    A measured value below its Need fails.
Also: ≤2,500 words (v3.8; M17; the measured checks table is data and doesn't count), and a misread check section.
Framing (M73, M74): tools/framing_check.py runs on the shot list (| # | Time | Shot | Whole in frame | ...): character
height against the frame height at each zoom, window widths, and out characters' x against the window or the gap.
"""
import re
import sys

NUM = re.compile(r"-?\d+(?:\.\d+)?")
WORD_CAP = 2500  # v3.8 (zero-based review 9 Oct): numbers moved to the animator
ACROSS_LESSON = 25


def tables(text):
    """Every markdown table as (header cells, rows of cells)."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = cells(lines[i])
            rows, i = [], i + 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            out.append((head, rows))
        else:
            i += 1
    return out


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def find(tabs, *words):
    for head, rows in tabs:
        low = " ".join(head).lower()
        if all(w in low for w in words):
            return head, rows
    return None


def num(cell, i=0):
    ns = NUM.findall(cell.replace("–", "-").replace(" - ", "-"))
    return float(ns[i].lstrip("-")) if len(ns) > i else None


def span(cell):
    ns = [float(n.lstrip("-")) for n in NUM.findall(cell.replace("–", "-"))]
    return (ns[0], ns[1] if len(ns) > 1 else ns[0]) if ns else None


ACROSS = r"(?=\s*(?:units\s*)?(?:from|clear|and\b))"
RULE_RE = re.compile(r"(?:≥|>=|at least)\s*(\d+(?:\.\d+)?)" + ACROSS + r"|(\d+(?:\.\d+)?)\s*(?:units\s*)?or more" + ACROSS)
MAX_FRAMES = 14  # audit M11


def stab(spans):
    """Fewest frame times that touch every (a, b) span (greedy)."""
    n, last = 0, None
    for a, b in sorted(spans, key=lambda s: s[1]):
        if last is None or a > last + 0.05:
            n, last = n + 1, b
    return n


def measured(tabs):
    """Rows of the measured checks table as (check, need, value or None for an estimate, source)."""
    t = find(tabs, "need", "measured", "source")
    if not t:
        return None
    out = []
    for r in t[1]:
        r = r + [""] * (4 - len(r))
        est = "estimate" in (r[2] + r[3]).lower()
        need = num(r[1])
        if need is not None and r[1].strip().startswith(("≤", "<=")):
            need = -need  # an upper limit: compared as -val >= -need
        out.append((r[0], need, None if est else num(r[2]), r[3]))
    return out


def measure_fails(rows, allow_estimates):
    fails = []
    for chk, need, val, src in rows:
        tag = f"measured check '{chk[:40]}'"
        if need is None:
            fails.append(f"{tag}: Need has no number")
        elif val is None:
            if not allow_estimates:
                fails.append(f"{tag}: still an estimate: measure it from the code before building")
        elif need < 0 and val > -need:
            fails.append(f"{tag}: measured {val:g} > limit {-need:g}")
        elif need >= 0 and val < need:
            fails.append(f"{tag}: measured {val:g} < need {need:g}")
        if not src.strip():
            fails.append(f"{tag}: no Source (`--check` or a still path)")
    return fails


def check(text):
    fails = []
    words = len(re.sub(r"(?ms)^## Measured checks.*?(?=^## |\Z)", "", text).split())
    if words > WORD_CAP:
        fails.append(f"plan is {words} words (cap {WORD_CAP}): cut prose, keep tables")
    m = re.search(r"\*\*Length:\*\*\s*([\d.]+)\s*s", text)
    if not m:
        return fails + ["no `**Length:** <seconds> s` line"]
    length = float(m.group(1))
    short = length <= 60
    lb = re.search(r"\*\*Lesson beat:\*\*\s*([\d.]+)\s*[-–]\s*([\d.]+)\s*s", text)
    if not lb:
        return fails + ["no `**Lesson beat:** <a>-<b> s` line"]
    lesson = (float(lb.group(1)), float(lb.group(2)))
    if "misread" not in text.lower():
        fails.append("no misread check section")
    tabs = tables(text)

    gag = find(tabs, "pause", "break", "joke signal")
    if not gag:
        fails.append("no gag table (columns: Time | Type | Trait | Set-up | Pause | Break | Break size | Joke signal | "
                     "Reaction | Sound | Topper | Test)")
    else:
        head, rows = gag
        if len(head) < 12:
            fails.append(f"gag table has {len(head)} columns, needs 12")
        starts, types, toppers, callback = [], [], 0, False
        for r in rows:
            r = r + [""] * (12 - len(r))
            tag = f"gag at {r[0] or '?'}"
            if any(not c for c in r[:12]):
                fails.append(f"{tag}: an empty cell (write 'none' for no topper)")
            sp, ty = span(r[0]), re.search(r"G[1-9]", r[1])
            if not sp:
                fails.append(f"{tag}: no time")
            else:
                starts.append(sp[0])
                if lesson[0] <= sp[0] < lesson[1]:
                    fails.append(f"{tag}: starts inside the lesson beat {lesson[0]:g}-{lesson[1]:g} s")
            if not ty:
                fails.append(f"{tag}: type is not G1-G9")
            else:
                types.append(ty.group(0))
            for idx, name, lo, hi in ((3, "set-up", 1.5, None), (4, "pause", 0.3, 0.6), (5, "break", 0.8, None),
                                      (6, "break size %", 10, None), (8, "reaction", 1.0, None)):
                v = num(r[idx])
                if v is None:
                    fails.append(f"{tag}: {name} has no number")
                elif v < lo or (hi is not None and v > hi):
                    fails.append(f"{tag}: {name} {v:g} outside {lo:g}{'-' + format(hi, 'g') if hi else '+'}")
            if "PASS" not in r[11].upper():
                fails.append(f"{tag}: 7-part test not marked PASS")
            if r[10].strip().lower() not in ("", "none", "-", "—", "no"):
                toppers += 1
            callback |= "callback" in r[2].lower()
        for a, b in zip(types, types[1:]):
            if a == b:
                fails.append(f"gag type {a} twice in a row")
        starts.sort()
        if not starts:
            fails.append("gag table has no rows")
        else:
            first, gap = (max(5, lesson[1] + 2), 15) if short else (20, 20)
            if starts[0] > first:
                fails.append(f"first gag at {starts[0]:g} s (by {first} s)")
            for a, b in zip(starts, starts[1:] + [length]):
                # the gap across the lesson beat (the mistake +-2 s) may reach 25 s: no gag on the erring moment
                limit = max(gap, ACROSS_LESSON) if a < lesson[1] and b > lesson[0] else gap
                if b - a > limit:
                    fails.append(f"{b - a:.1f} s without a gag after {a:g} s (max {limit})")
        if not short:
            if len(set(types)) < 3:
                fails.append(f"{len(set(types))} gag types (needs ≥3)")
            if not {"G4", "G5"} & set(types):
                fails.append("no rule-of-three build (G4 or G5)")
            if not callback:
                fails.append("no callback (a row whose Trait says 'callback')")
            if not toppers:
                fails.append("no topper")

    keys = find(tabs, "key action", "uncovered")
    spans = []
    if not keys:
        fails.append("no key actions table (Key action | Time | Object | Size (%) | Uncovered (s))")
    else:
        for r in keys[1]:
            r = r + [""] * (5 - len(r))
            tag = f"key action '{r[0][:30]}'"
            sp = span(r[1])
            if not sp:
                fails.append(f"{tag}: no time")
                continue
            spans.append((sp, tag))
            if sp[1] - sp[0] < 1.0 - 1e-9:
                fails.append(f"{tag}: lasts {sp[1] - sp[0]:.2f} s (≥1.0)")
            size, unc = num(r[3]), num(r[4])
            if size is None or size < 10:
                fails.append(f"{tag}: object size {size} % of width (≥10, or stage it in a close-up)")
            if unc is None or unc < 1.0:
                fails.append(f"{tag}: uncovered {unc} s (≥1.0)")

    sb = find(tabs, "frame", "shows")
    if not sb:
        fails.append("no storyboard table (Frame (s) | Shot | Shows)")
    else:
        times = [num(r[0]) for r in sb[1] if num(r[0]) is not None]
        lo, hi = (6, 12) if short else (10, 12)
        if hi < len(times) <= MAX_FRAMES and stab([s for s, _ in spans]) + 2 > hi:
            print(f"WARN storyboard has {len(times)} frames (normal {lo}-{hi}): allowed up to {MAX_FRAMES} because the key actions need them")
        elif not lo <= len(times) <= hi:
            fails.append(f"storyboard has {len(times)} frames ({lo}-{hi}; up to {MAX_FRAMES} when the key actions need more)")
        for (a, b), tag in spans:
            if not any(a - 0.05 <= t <= b + 0.05 for t in times):
                fails.append(f"{tag}: no storyboard frame inside {a:g}-{b:g} s (the cause must be on the sheet)")

    rows = measured(tabs)
    needs = sorted({float(a or b) for a, b in RULE_RE.findall(text)})
    if needs and rows is None:
        fails.append(f"no measured checks table (Check | Need | Measured | Source) for the plan's distance rules {needs}")
    elif rows is not None:
        have = {r[1] for r in rows}
        for n in needs:
            if n not in have:
                fails.append(f"distance rule ≥{n:g} has no measured checks row (Need {n:g})")
        fails += measure_fails(rows, allow_estimates=True)
        est = [r[0] for r in rows if r[2] is None]
        if est:
            print(f"NOTE {len(est)} estimate(s) the animator must measure before building: {est}")

    import framing_check
    fails += framing_check.check(text)

    props = find(tabs, "prop", "colour")
    if not props:
        fails.append("no props table (Prop | Colour | ...)")
    else:
        for r in props[1]:
            if any(not c for c in r):
                fails.append(f"prop '{r[0]}': an empty cell")
    return fails


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    fails = check(open(sys.argv[1], encoding="utf-8").read())
    for f in fails:
        print("FAIL", f)
    print("plan_check:", "PASS" if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
