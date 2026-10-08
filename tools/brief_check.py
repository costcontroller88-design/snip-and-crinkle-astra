"""Check a build brief before it goes to the animator (MASTER_PROMPT 10.11; M26, M27, M30: briefs overrode the file).

    python3 tools/brief_check.py brief.txt        (or:  echo "<brief>" | python3 tools/brief_check.py -)

FAIL (exit 1) when an animator brief does not say "feasibility first" (the animator measures the plan's estimates and returns
numbers before any code edit), or when it sets a tool-call budget (the budget lives in the agent file; a brief that
names one overrides it, e.g. "<=14 calls", "budget 10").
With `--plan <plan.md>`: FAIL a brief that goes on to build ("then build") while the plan's `## Measured checks` still has
an "estimate" row; send "Stage: feasibility only" first, read the numbers, then SendMessage "build" to the same agent (M39).
"""
import re
import sys

BUDGET = re.compile(r"budget|[≤<]=?\s*\d+\s*(?:tool\s*)?(?:calls?|turns?)|\d+\s*(?:tool\s*)?(?:calls?|turns?)\s*(?:max|at most|or fewer)",
                    re.I)


def open_estimates(plan):
    rows, on = [], False
    for line in open(plan, encoding="utf-8"):
        if line.startswith("## "):
            on = line.startswith("## Measured checks")
        elif on and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and "estimate" in cells[2].lower():
                rows.append(cells[0][:60])
    return rows


def check(text, plan=None):
    fails = []
    if plan and "feasibility only" not in text.lower() and "then build" in text.lower():
        est = open_estimates(plan)
        if est:
            fails.append(f'{len(est)} open estimate(s) in the plan ({est[0]}...): brief "Stage: feasibility only" first (M39)')
    agent = text.strip().split(":", 1)[0].strip().lower()
    # M46 (twice): "feasibility first" applies to animator build briefs only; a general-purpose agent has no
    # agent file, so its budget lives in its spec and the budget rule is skipped too.
    if agent == "animator" and "feasibility first" not in text.lower() and "feasibility only" not in text.lower():
        fails.append('no "feasibility first": measure every estimate and return numbers before any code edit (M27)')
    for m in ([] if agent == "general-purpose" else BUDGET.finditer(text)):
        fails.append(f'the brief sets a budget ("{m.group(0).strip()}"); the budget lives in the agent file (10.11.7)')
    return fails


def main():
    args = sys.argv[1:]
    plan = None
    if "--plan" in args:
        i = args.index("--plan")
        plan = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        sys.exit(__doc__)
    text = sys.stdin.read() if args[0] == "-" else open(args[0], encoding="utf-8").read()
    fails = check(text, plan)
    for f in fails:
        print("FAIL", f)
    print("brief_check:", "PASS" if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
