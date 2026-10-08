"""The Lead's pre-flight before each step (MASTER_PROMPT 10.11; agent ratings 8 Oct: L9, M1, M8, M10, M19).

    python3 tools/preflight.py --used 18 --reset-min 264 --weekly 72
    python3 tools/preflight.py --used 18 --reset-min 264 --weekly 72 --log "Gate 1 → safety-checker" --ledger reviews/ep12_ledger.md

--used and --reset-min come from get_usage (5-hour % and minutes to its reset). Prints: git status, the band
verdict (what may start now), the last ledger row, OPEN mistakes by agent, and HANDOFF's word count. --log appends
a dated ledger row with both limits. ListAgents is a tool, not a script: run it first (one Lead only).
"""
import argparse
import datetime
import glob
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def band(used, reset_min):
    if used > 85:
        return "STOP: >85%, wait for the reset"
    if used >= 75:
        return "NO AGENT: 75-85%, save and commit"
    if reset_min < 90 and used >= 50:
        return "SMALL AGENTS ONLY: reset <90 min away (M8); no animator or market scan until after it"
    if used >= 60:
        return "SMALL AGENTS ONLY: 60-75% (reviewer, safety, designer, packaging)"
    return "ANY AGENT: <60%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--used", type=float, required=True)
    ap.add_argument("--reset-min", type=float, required=True)
    ap.add_argument("--weekly", type=float, default=None)
    ap.add_argument("--log", default=None)
    ap.add_argument("--ledger", default=None)
    a = ap.parse_args()
    st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    print("git status:", st.replace("\n", "; ") or "clean")
    print("band:", band(a.used, a.reset_min))
    ledgers = sorted(glob.glob(os.path.join(ROOT, "reviews", "*ledger*.md")), key=os.path.getmtime)
    ledger = os.path.join(ROOT, a.ledger) if a.ledger else (ledgers[-1] if ledgers else None)
    if ledger and os.path.exists(ledger):
        rows = [ln for ln in open(ledger, encoding="utf-8") if ln.startswith("|") and not ln.startswith("|---")]
        print("last ledger row:", os.path.relpath(ledger, ROOT), rows[-1].strip()[:200] if rows else "none")
    log = open(os.path.join(ROOT, "reviews", "mistake_log.md"), encoding="utf-8").read()
    open_rows = re.findall(r"^\| (M\d+) \| [^|]*\| ([^|]+?) \|.*\| OPEN[^|]*\|?\s*$", log, re.M)
    by = {}
    for mid, who in open_rows:
        by.setdefault(who.strip(), []).append(mid)
    print("OPEN mistakes:", "; ".join(f"{w} {','.join(ids)}" for w, ids in by.items()) or "none")
    words = len(open(os.path.join(ROOT, "HANDOFF.md"), encoding="utf-8").read().split())
    print(f"HANDOFF: {words} words (cap 500)")
    print("build brief: 'Stage: feasibility first: measure every estimate in the plan's Measured checks, then build' (M27)")
    print("times to the owner: a range + the main risk; never 'ready by' before handover_check PASS")
    print("before you claim or ask: read the file that knows (bible: who errs; Studio: account steps; "
          "benchmark docs: channel handles)")
    if a.log:
        if not ledger:
            raise SystemExit("no ledger: pass --ledger reviews/epNN_ledger.md")
        wk = f"{a.weekly:g}" if a.weekly is not None else "—"
        day = datetime.date.today().strftime("%-d %b")
        with open(ledger, "a", encoding="utf-8") as fh:
            fh.write(f"| {day} | {a.log} | Lead | {a.used:g} | {wk} | preflight: {band(a.used, a.reset_min)} |\n")
        print("logged to", os.path.relpath(ledger, ROOT))


if __name__ == "__main__":
    main()
