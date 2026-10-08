"""Check a build brief before it goes to the animator (MASTER_PROMPT 10.11; M26, M27, M30: briefs overrode the file).

    python3 tools/brief_check.py brief.txt        (or:  echo "<brief>" | python3 tools/brief_check.py -)

FAIL (exit 1) when the brief does not say "feasibility first" (the animator measures the plan's estimates and returns
numbers before any code edit), or when it sets a tool-call budget (the budget lives in the agent file; a brief that
names one overrides it, e.g. "<=14 calls", "budget 10").
"""
import re
import sys

BUDGET = re.compile(r"budget|[≤<]=?\s*\d+\s*(?:tool\s*)?(?:calls?|turns?)|\d+\s*(?:tool\s*)?(?:calls?|turns?)\s*(?:max|at most|or fewer)",
                    re.I)


def check(text):
    fails = []
    if "feasibility first" not in text.lower():
        fails.append('no "feasibility first": measure every estimate and return numbers before any code edit (M27)')
    for m in BUDGET.finditer(text):
        fails.append(f'the brief sets a budget ("{m.group(0).strip()}"); the budget lives in the agent file (10.11.7)')
    return fails


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    text = sys.stdin.read() if sys.argv[1] == "-" else open(sys.argv[1], encoding="utf-8").read()
    fails = check(text)
    for f in fails:
        print("FAIL", f)
    print("brief_check:", "PASS" if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
