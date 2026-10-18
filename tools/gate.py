"""The gate tracker (v4.2): state/gates.json holds each episode's gate results; only this script writes it.

    python3 tools/gate.py set ep12 gate1 PASS --evidence reviews/ep12_safety.md
    python3 tools/gate.py set ep11 gate2 FAIL --evidence reviews/ep11_short_blind_r2.md --owner-ok "<owner's words>"
    python3 tools/gate.py show [ep12]

Gates: gate1 (safety, the plan), gate1b (blind storyboard retelling), gate2 (blind review), gate3 (safety, the
video and upload text). Results: PASS, FAIL or none (clears it). --evidence must name an existing file (the review
that decided it); --owner-ok "<the owner's words>" records an owner override (M44) and makes --evidence optional.
tools/agent_hooks.py brief reads it: an animator "build" brief waits for gate1 PASS, packaging for gate2 PASS or an
owner-ok. Agents may not run `set` (scope hook). --file <path> points at a scratch copy (tests).
"""
import argparse
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATES = os.path.join(ROOT, "state", "gates.json")
NAMES = ("gate1", "gate1b", "gate2", "gate3")


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Record or show gate results (state/gates.json).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set")
    s.add_argument("episode")
    s.add_argument("gate", choices=NAMES)
    s.add_argument("result", choices=("PASS", "FAIL", "none"))
    s.add_argument("--evidence")
    s.add_argument("--owner-ok")
    s.add_argument("--file", default=GATES)
    sh = sub.add_parser("show")
    sh.add_argument("episode", nargs="?")
    sh.add_argument("--file", default=GATES)
    a = ap.parse_args(argv)
    gates = load(a.file)
    if a.cmd == "show":
        print(json.dumps(gates.get(a.episode, {}) if a.episode else gates, indent=1))
        return 0
    if not re.fullmatch(r"ep\d{2}", a.episode):
        print(f"FAIL: episode must look like ep12, not '{a.episode}'", file=sys.stderr)
        return 1
    owner = (a.owner_ok or "").strip()
    if a.evidence:
        ev = a.evidence if os.path.isabs(a.evidence) else os.path.join(ROOT, a.evidence)
        if not os.path.isfile(ev):
            print(f"FAIL: evidence file {a.evidence} does not exist; nothing recorded", file=sys.stderr)
            return 1
    elif not owner and a.result != "none":
        print("FAIL: --evidence <existing file> is required (or --owner-ok \"<the owner's words>\")", file=sys.stderr)
        return 1
    ep = gates.setdefault(a.episode, {})
    if a.result == "none":
        ep.pop(a.gate, None)
    else:
        ep[a.gate] = {"result": a.result, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                      "evidence": a.evidence or ""}
        if owner:
            ep[a.gate]["owner_ok"] = owner
    os.makedirs(os.path.dirname(os.path.abspath(a.file)), exist_ok=True)
    with open(a.file, "w", encoding="utf-8") as f:
        json.dump(gates, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"{a.episode} {a.gate}: {a.result}" + (f" (owner ok: {owner[:60]})" if owner else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
