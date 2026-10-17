"""The Lead's pre-flight before each step (docs/agents/lead_reference.md 10.11; agent ratings 8 Oct: L9, M1, M8, M10, M19).

    python3 tools/preflight.py --used 18 --reset-min 264 --weekly 72
    python3 tools/preflight.py --used 18 --reset-min 264 --weekly 72 --log "Gate 1 → safety-checker" --ledger reviews/ep12_ledger.md

--used and --reset-min come from get_usage (5-hour % and minutes to its reset). Prints: git status, the band
verdict (what may start now), the last ledger row, OPEN mistakes by agent, and HANDOFF's word count. --log appends
a dated ledger row with both limits. --ctx <k tokens of the Lead's context>: above 200 it prints "LEAD CODES NOTHING"
(L5, M32: write a <=20-line change spec for a fresh session or agent). --estimate <points of the 5-hour limit> saves
the Lead's own estimate for the work about to start; the next run prints estimate vs actual (points used since). ListAgents is a tool, not a script: run it first (one Lead only).
Weekly pace (audit M6): --weekly-reset-days <d> (days to the weekly reset) with --weekly: if weekly % > (7 - d)/7 x 100
+ 10 the band is at most "SMALL AGENTS ONLY (weekly above pace)", unless --weekly-ok (the owner's word, 9 Oct).
Exit 2 (nothing logged) when --log names an agent the band forbids: SMALL: animator, growth-analyst, general-purpose;
NO AGENT / STOP: any agent.
v4.1: every run writes .preflight_band; tools/agent_hooks.py brief refuses an agent call when that file is missing,
older than 2 hours, or its band forbids the agent. --owner-ok "<the owner's words>" (an owner override in chat, e.g.
"continue, I don't have an issue") makes the band ANY AGENT and records the quote. A set CLAUDE_CODE_SUBAGENT_MODEL
(or _FORCE) is printed as a FAIL line: it silently overrides the models pinned in the agent files.
"""
import json
import time
import argparse
import datetime
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


AGENTS = ["animator", "growth-analyst", "general-purpose", "fresh-eyes-reviewer", "safety-checker", "story-designer",
          "packaging"]
SMALL_FORBIDDEN = ["animator", "growth-analyst", "general-purpose"]


def band(used, reset_min, weekly=None, reset_days=None, weekly_ok=False):
    if used > 85:
        return "STOP: >85%, wait for the reset"
    if used >= 75:
        return "NO AGENT: 75-85%, save and commit"
    if reset_min < 90 and used >= 50:
        return "SMALL AGENTS ONLY: reset <90 min away (M8); no animator or market scan until after it"
    if used >= 60:
        return "SMALL AGENTS ONLY: 60-75% (reviewer, safety, designer, packaging)"
    if weekly is not None and reset_days is not None and not weekly_ok and weekly > (7 - reset_days) / 7 * 100 + 10:
        return "SMALL AGENTS ONLY (weekly above pace)"
    return "ANY AGENT: <60%"


def forbidden(b, text):
    """Agents named in `text` that band `b` forbids."""
    named = [a for a in AGENTS if re.search(rf"(?<![\w-]){a}(?![\w-])", text)]
    if b.startswith(("STOP", "NO AGENT")):
        return named
    if b.startswith("SMALL"):
        return [a for a in named if a in SMALL_FORBIDDEN]
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--used", type=float, required=True)
    ap.add_argument("--reset-min", type=float, required=True)
    ap.add_argument("--weekly", type=float, default=None)
    ap.add_argument("--weekly-reset-days", type=float, default=None, help="days to the weekly reset (with --weekly)")
    ap.add_argument("--weekly-ok", action="store_true", help="the owner's word that the weekly pace is fine")
    ap.add_argument("--ctx", type=float, default=None, help="Lead context in k tokens")
    ap.add_argument("--estimate", type=float, default=None, help="estimated 5-hour points for the next piece of Lead work")
    ap.add_argument("--owner-ok", default=None, help="the owner's override, quoted from chat")
    ap.add_argument("--log", default=None)
    ap.add_argument("--ledger", default=None)
    a = ap.parse_args()
    st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    print("git status:", st.replace("\n", "; ") or "clean")
    b = band(a.used, a.reset_min, a.weekly, a.weekly_reset_days, a.weekly_ok)
    if a.owner_ok:
        b = f"ANY AGENT: owner override ({a.owner_ok[:80]}); computed band was '{b}'"
    print("band:", b)
    with open(os.path.join(ROOT, ".preflight_band"), "w", encoding="utf-8") as fh:
        json.dump({"band": b, "time": time.time()}, fh)
    for var in ("CLAUDE_CODE_SUBAGENT_MODEL", "CLAUDE_CODE_SUBAGENT_MODEL_FORCE"):
        if os.environ.get(var):
            print(f"FAIL {var}={os.environ[var]} overrides the agents' pinned models: unset it")
    if a.weekly is not None and a.weekly_reset_days is not None:
        print(f"weekly pace: {a.weekly:g}% used, {(7 - a.weekly_reset_days) / 7 * 100:g}% of the week gone "
              f"(over pace above {(7 - a.weekly_reset_days) / 7 * 100 + 10:g}%){'; --weekly-ok given' if a.weekly_ok else ''}")
    if a.ctx is not None and a.ctx > 200:
        print(f"LEAD CODES NOTHING: context {a.ctx:g}k > 200k; write a <=20-line change spec for a fresh session or agent (L5, M32)")
    est = os.path.join(ROOT, ".preflight_estimate")
    if os.path.exists(est):
        old = [float(x) for x in open(est, encoding="utf-8").read().split()]
        print(f"last estimate {old[0]:g} points vs actual {a.used - old[1]:g} (5-hour % now {a.used:g}, then {old[1]:g}); "
              "if actual > 1.5x, say so in the mistake log")
        os.remove(est)
    if a.estimate is not None:
        with open(est, "w", encoding="utf-8") as fh:
            fh.write(f"{a.estimate:g} {a.used:g}\n")
        print(f"estimate {a.estimate:g} points saved; the next preflight prints it against the actual")
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
    print("build brief: 'Stage: feasibility first: measure every estimate in the plan's Measured checks, then build' (M27); check the brief: python3 tools/brief_check.py <file>")
    print("times to the owner: a range + the main risk; never 'ready by' before handover_check PASS")
    print("before you claim or ask: read the file that knows (bible: who errs; Studio: account steps; "
          "benchmark docs: channel handles)")
    if a.log:
        bad = forbidden(b, a.log)
        if bad:
            print(f"FAIL band '{b}' forbids {', '.join(bad)}: not logged; start something the band allows", file=sys.stderr)
            sys.exit(2)
        if not ledger:
            raise SystemExit("no ledger: pass --ledger reviews/epNN_ledger.md")
        wk = f"{a.weekly:g}" if a.weekly is not None else "—"
        day = datetime.date.today().strftime("%-d %b")
        with open(ledger, "a", encoding="utf-8") as fh:
            fh.write(f"| {day} | {a.log} | Lead | {a.used:g} | {wk} | preflight: {b} |\n")
        print("logged to", os.path.relpath(ledger, ROOT))


if __name__ == "__main__":
    main()
