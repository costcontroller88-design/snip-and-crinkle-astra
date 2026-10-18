"""Record the owner's fresh "yes" before the Lead changes anything in YouTube Studio (v4.2; core rule 11, section 4).

    python3 tools/approve.py "<the owner's exact words from chat>"

Appends {time, date, quote} to state/approvals.jsonl. tools/agent_hooks.py lead refuses the Lead's typing, clicking
or form filling on a studio.youtube.com page unless the newest approval is under 30 minutes old. The quote must hold
the owner's yes (yes, ok, okay, haan, approved, go ahead); it is copied from chat, never written by the Lead.
Agents may not run it (scope hook). --file <path> points at a scratch copy (tests).
"""
import datetime
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPROVALS = os.path.join(ROOT, "state", "approvals.jsonl")
YES = re.compile(r"\b(yes|ok|okay|haan|approved?|go ahead)\b", re.I)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    path = APPROVALS
    if "--file" in args:
        i = args.index("--file")
        path = args[i + 1]
        del args[i:i + 2]
    quote = " ".join(args).strip()
    if not YES.search(quote):
        print('FAIL: paste the owner\'s own words holding their yes, e.g. approve.py "yes, schedule it"', file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": time.time(), "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "quote": quote[:300]}) + "\n")
    print(f"approved for 30 minutes: {quote[:80]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
