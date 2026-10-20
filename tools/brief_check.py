"""Check a build brief before it goes to the animator (docs/agents/lead_reference.md 10.11; M26, M27, M30: briefs overrode the file).

    python3 tools/brief_check.py brief.txt        (or:  echo "<brief>" | python3 tools/brief_check.py -)

FAIL (exit 1) when an animator brief does not say "feasibility first" (the animator measures the plan's estimates and returns
numbers before any code edit), or when it sets a tool-call budget (the budget lives in the agent file; a brief that
names one overrides it, e.g. "<=14 calls", "budget 10").
M67/M79: FAIL explicit storyboard/build/edit requests under "Stage: feasibility only".
Negated actions and measurement references remain allowed. This phrase check cannot prove arbitrary prose consistent.
With `--plan <plan.md>`: FAIL a brief that goes on to build ("then build") while the plan's `## Measured checks` still has
an "estimate" row; send "Stage: feasibility only" first, read the numbers, then SendMessage "build" to the same agent (M39).
"""
import re
import sys

BUDGET = re.compile(r"budget|[≤<]=?\s*\d+\s*(?:tool\s*)?(?:calls?|turns?)|\d+\s*(?:tool\s*)?(?:calls?|turns?)\s*(?:max|at most|or fewer)",
                    re.I)


def stage_conflicts(text):
    """Catch explicit production requests under the hook's feasibility-only stage.

    This is a bounded phrase check, not a natural-language intent classifier.
    Read/check/measure references are allowed; negated actions are not requests.
    Match the first Stage line exactly as agent_hooks.stage_of does.
    """
    stage = re.search(r"\bstage:\s*(.+)", text, re.I)
    if not stage or not re.search(r"\bfeasibility only\b", stage.group(1), re.I):
        return []
    action = re.compile(
        r"\b(?:build|render|animate|edit|fix|patch|modify|rewrite)\b"
        r"|\bcode[- ]fix\b|\bmeasure\s*\+\s*storyboard\b"
        r"|\b(?:make|create|produce|return|deliver|draw)\b[^.;\n]{0,80}\bstoryboard\b", re.I)
    conflicts = []
    # Commas/semicolons separate requests, so 'do not edit; then build' still fails.
    for clause in re.split(r"[.;\n,]", text):
        for match in action.finditer(clause):
            prefix = clause[:match.start()].lower()
            if re.search(r"\b(?:no|not|never|without|don't|cannot|can't)\b[^;,.]*$", prefix):
                continue
            # A measurement/reference can name a build or render without asking for it.
            if (re.search(r"\b(?:measure|inspect|read|check|estimate|report)\b[^;,.]*$", prefix)
                    and not re.search(r"\b(?:and|then)\s*$", prefix)):
                continue
            conflicts.append(match.group(0))
    return conflicts


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
    if agent == "animator":
        conflicts = stage_conflicts(text)
        if conflicts:
            fails.append('"Stage: feasibility only" also requests production (' + ", ".join(conflicts) +
                         '); use "Stage: measure + storyboard (feasibility first)" for a storyboard, or '
                         '"feasibility first, then build" for code changes (M67/M79)')
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
