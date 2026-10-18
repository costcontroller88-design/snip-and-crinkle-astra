"""Framing pre-check on the story-designer's shot rows (M73, M74: rows that failed on simple arithmetic).

    python3 tools/framing_check.py reviews/ep12_plan.md      (tools/plan_check.py runs it too)

The frame is 1920 x 1080 units at 1.0x, so a Z x shot shows 1920/Z wide and 1080/Z tall. Every row of the shot list
(| # | Time (s) | Shot | Whole in frame | ... |) is checked:
  1. height: everyone named whole in frame ("Snip", "Snip incl. ears and feet", "all"; not "Snip's ears") fits the
     frame height with 10 u above and below: Snip (748 u) in a 2.0x shot (540 u) fails (M73). A crouching, sitting
     or lying character ("Snip (crouched)") is skipped.
  2. window: "x a-b" is 1920/Z wide and "y a-b" is 1080/Z tall (±1%).
  3. gap: everyone named out ("Snip, Crinkle wholly out") needs an x in the row ("Snip x 380", "Pip at 800"); their
     side extents must stay 10 u clear of the window (M74: Snip's ear 59 u past a window edge), or, without a
     window, leave a gap of at least the frame width + 20 u (M73: a 960 u window in 787 u of room). Whole-in
     characters with an x must sit inside the window with 10 u to spare.
Sizes: rig2 standing, head turn -0.5..0.5, measured 18 Oct 2026 from the ep12_rough_r2 body masks at the bible's rig
scales (docs/CHARACTER_BIBLE.md, "Size (rig scale)"); if the bible's scale changes, the sizes scale with it. Side
extents add 36 u for poses (paws out, ears; M74 measured Snip at x+214). Exit 1 and list every failure.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLE = os.path.join(ROOT, "docs", "CHARACTER_BIBLE.md")
FRAME_W, FRAME_H = 1920.0, 1080.0
MARGIN = 10.0
POSE = 36.0  # M74: at x 380 Snip's head+ear mask reached x 594 (178 + 36)
# name: (rig scale measured at, height incl. ears, extent left of x, extent right of x), rig units
MEASURED = {"Snip": (1.15, 748, 178, 178), "Crinkle": (1.2, 648, 228, 239), "Pip": (0.9, 343, 95, 96)}
NAMES = tuple(MEASURED)
LOW = re.compile(r"crouch|kneel|sit|lying|lies|squat|bend", re.I)
POS_ONLY = re.compile(r"^(?:r\d\w*:\s*)?(?:%s)\s*(?:at\s+)?(?:x\s*)?[≥≤<>]?=?\s*\d+(?:\.\d+)?$" % "|".join(MEASURED))


def bible_scales(path=BIBLE):
    """{name: rig scale} from the bible's size row (columns in its header order); {} if not found."""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return {}
    head = re.search(r"^\|\s*\|(.+)\|\s*$", text, re.M)
    row = re.search(r"^\|\s*Size \(rig scale\)\s*\|(.+)\|\s*$", text, re.M)
    if not head or not row:
        return {}
    who = [c.strip() for c in head.group(1).split("|")]
    vals = [re.search(r"\(([\d.]+)\)", c) for c in row.group(1).split("|")]
    return {w: float(v.group(1)) for w, v in zip(who, vals) if w in MEASURED and v}


def sizes(scales=None):
    """{name: (height, left extent, right extent)} at the bible's scales, extents with the pose allowance."""
    scales = bible_scales() if scales is None else scales
    out = {}
    for n, (s0, h, l, r) in MEASURED.items():
        k = scales.get(n, s0) / s0
        out[n] = (h * k, l * k + POSE, r * k + POSE)
    return out


def shots(cell):
    """[(label, zoom, (x0, x1) or None, (y0, y1) or None)] from a Shot cell like "M 1.4x; C 2.2x 74.8-76.0"."""
    out = []
    for spec in cell.split(";"):
        spec = spec.strip()
        if not spec:
            continue
        label = spec.split()[0].rstrip(",:")
        zs = [float(z) for z in re.findall(r"(\d+(?:\.\d+)?)\s*x\b", spec)]
        zoom = max(zs) if zs else (1.0 if label.upper().startswith("W") else None)
        xw = re.search(r"\bx\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", spec)
        yw = re.search(r"\by\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", spec)
        out.append((label, zoom, tuple(map(float, xw.groups())) if xw else None,
                    tuple(map(float, yw.groups())) if yw else None))
    return out


def groups(cell, labels):
    """{shot index: (whole-in names, out names)}; a group led by "C:" or "C7:" belongs to that shot, others to the first."""
    res = {}
    for g in cell.split(";"):
        g = g.strip()
        m = re.match(r"^(\w+):\s*(.*)$", g)
        i = 0
        if m and m.group(1) in labels:
            i, g = labels.index(m.group(1)), m.group(2)
        whole, out = res.setdefault(i, ([], []))
        is_out = re.search(r"\bout\b", g, re.I)
        items = [it.strip() for it in re.sub(r"[()]", ",", g).split(",") if it.strip()]
        if all(POS_ONLY.match(it) for it in items):
            continue  # a group of positions only ("Snip x 380, Crinkle x 1850") names no one in or out
        for item in g.split(","):  # "Snip (crouched)" stays one item, so the crouch is seen
            if re.match(r"^all\b", item, re.I) and not is_out:
                whole += [n for n in NAMES if n not in whole]
                continue
            for n in NAMES:
                lst = out if is_out else whole
                if re.search(r"\b" + n + r"\b(?!'s)", item) and not LOW.search(item) and n not in lst:
                    lst.append(n)
    return res


def positions(text):
    """{name: x} from "Snip x 380", "Pip at 800", "Pip at x 990", "Pip ≥800" in the row."""
    pos = {}
    for n in NAMES:
        m = re.search(r"\b" + n + r"\b\s*(?:at\s+)?(?:x\s*)?(?:[≥≤<>]=?\s*)?(\d{2,4}(?:\.\d+)?)\b(?!\s*[-–]\s*\d)(?!\s*(?:s\b|u\b|%|x\b))",
                      text)
        if m:
            pos[n] = float(m.group(1))
    return pos


def check_row(num, row, sz):
    fails = []
    shot_cell, whole_cell = row[2], row[3]
    sh = shots(shot_cell)
    labels = [s[0] for s in sh]
    pos = positions(" | ".join(row[2:]))
    for i, (whole, out) in groups(whole_cell, labels).items():
        if i >= len(sh):
            continue
        label, zoom, xw, yw = sh[i]
        if not zoom:
            continue
        w, h = FRAME_W / zoom, FRAME_H / zoom
        tag = f"shot {num} {label} {zoom:g}x"
        if xw and abs((xw[1] - xw[0]) - w) > 0.01 * w:
            fails.append(f"{tag}: window x {xw[0]:g}-{xw[1]:g} is {xw[1] - xw[0]:.0f} u wide; {zoom:g}x is {w:.0f} u")
        if yw and abs((yw[1] - yw[0]) - h) > 0.01 * h:
            fails.append(f"{tag}: window y {yw[0]:g}-{yw[1]:g} is {yw[1] - yw[0]:.0f} u tall; {zoom:g}x is {h:.0f} u")
        for n in whole:
            if sz[n][0] + 2 * MARGIN > h:
                fails.append(f"{tag}: {n} is {sz[n][0]:.0f} u tall (+{2 * MARGIN:g} margin) but the frame is {h:.0f} u "
                             f"tall; whole in needs ≤{FRAME_H / (sz[n][0] + 2 * MARGIN):.2f}x (or mark him crouched)")
            if xw and n in pos:
                a, b = pos[n] - sz[n][1], pos[n] + sz[n][2]
                if a < xw[0] + MARGIN or b > xw[1] - MARGIN:
                    fails.append(f"{tag}: {n} at x {pos[n]:g} spans {a:.0f}-{b:.0f}, not inside window "
                                 f"{xw[0]:g}-{xw[1]:g} by {MARGIN:g} u")
        missing = [n for n in out if n not in pos]
        if missing:
            fails.append(f"{tag}: {', '.join(missing)} out but no x in the row: write e.g. '{missing[0]} x 380' "
                         "so the gap can be checked")
        spans = sorted((pos[n] - sz[n][1], pos[n] + sz[n][2], n) for n in out if n in pos)
        if xw:
            for a, b, n in spans:
                if b > xw[0] - MARGIN and a < xw[1] + MARGIN:
                    fails.append(f"{tag}: {n} at x {pos[n]:g} spans {a:.0f}-{b:.0f}; it must clear window "
                                 f"{xw[0]:g}-{xw[1]:g} by {MARGIN:g} u")
        elif spans:
            edges = [0.0] + [e for a, b, _ in spans for e in (a, b)] + [FRAME_W]
            room = max(edges[k + 1] - edges[k] for k in range(0, len(edges) - 1, 2))
            if room < w + 2 * MARGIN:
                fails.append(f"{tag}: the widest gap clear of {', '.join(n for _, _, n in spans)} is {room:.0f} u; "
                             f"the frame is {w:.0f} u (+{2 * MARGIN:g})")
    return fails


def check(text, sz=None):
    sz = sz or sizes()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import plan_check
    t = plan_check.find(plan_check.tables(text), "shot", "whole")
    if not t:
        return []
    fails = []
    for row in t[1]:
        if len(row) >= 4:
            fails += check_row(row[0], row, sz)
    return fails


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    fails = check(open(sys.argv[1], encoding="utf-8").read())
    for f in fails:
        print("FAIL", f)
    print("framing_check:", "PASS" if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
