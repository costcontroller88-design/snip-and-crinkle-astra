"""Check an agent's return: the last ```json block must be valid and honest.

    python3 tools/return_check.py <file>     (a saved return)
    python3 tools/return_check.py -          (the return on stdin)

FAIL (exit 1) if: no ```json block or invalid JSON; a key of the return schema is missing; verdict not one of
PASS|FAIL|DONE|PARTIAL; tool_calls or budget not a number; tool_calls > budget; a check without a name or with
empty evidence, evidence that says "estimate" or "looks", evidence with no number or file path, a cited path that
doesn't exist; a listed file that doesn't exist (relative paths are
tried from the current folder, then from the project root); files, checks or not_done not lists.
A FAIL is a mistake-log row (docs/agents/lead_reference.md 10.11 item 10).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = ("agent", "verdict", "tool_calls", "budget", "checks", "files", "not_done")
VERDICTS = ("PASS", "FAIL", "DONE", "PARTIAL")
BLOCK = re.compile(r"```json[ \t]*\n(.*?)\n[ \t]*```", re.S)
SOFT = re.compile(r"\b(estimates?|estimated|looks?)\b", re.I)
# Research 9 Oct (docs/research-agent-craft-oct-2026.md rows 1-2): evidence must be a number or a path, and a cited path must exist.
PATH = re.compile(r"[\w./-]*/[\w.-]+\.(?:png|jpe?g|md|mp4|wav|py|txt|json|csv)\b")


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def check(text):
    """Return the list of problems (empty = PASS)."""
    blocks = BLOCK.findall(text)
    if not blocks:
        return ["no ```json block found"]
    try:
        d = json.loads(blocks[-1])
    except ValueError as e:
        return [f"last json block is not valid JSON: {e}"]
    if not isinstance(d, dict):
        return ["last json block is not an object"]
    bad = [f"missing key: {k}" for k in KEYS if k not in d]
    if bad:
        return bad
    if d["verdict"] not in VERDICTS:
        bad.append(f"verdict {d['verdict']!r} is not one of {'|'.join(VERDICTS)}")
    if not num(d["tool_calls"]) or not num(d["budget"]):
        bad.append("tool_calls and budget must be numbers")
    elif d["tool_calls"] > d["budget"]:
        bad.append(f"over budget: tool_calls {d['tool_calls']} > budget {d['budget']}")
    for k in ("checks", "files", "not_done"):
        if not isinstance(d[k], list):
            bad.append(f"{k} must be a list")
    if bad:
        return bad
    for i, c in enumerate(d["checks"], 1):
        if not isinstance(c, dict) or not str(c.get("name", "")).strip():
            bad.append(f"check {i}: no name")
            continue
        ev = c.get("evidence")
        if not isinstance(ev, str) or not ev.strip():
            bad.append(f"check {i} ({c['name']}): empty evidence")
        elif SOFT.search(ev):
            bad.append(f"check {i} ({c['name']}): evidence says estimate/looks: {ev!r}; fix: measure it or write 'not checked'")
        else:
            paths = PATH.findall(ev)
            if not paths and not re.search(r"\d", ev):
                bad.append(f"check {i} ({c['name']}): evidence has no number or file path: {ev!r}; fix: cite the still or the measured number")
            for f in paths:
                if not (os.path.exists(f) or os.path.exists(os.path.join(ROOT, f))):
                    bad.append(f"check {i} ({c['name']}): cited file does not exist: {f}; fix: cite a file this session wrote")
    for f in d["files"]:
        if not isinstance(f, str) or not f.strip():
            bad.append(f"bad file entry: {f!r}")
        elif not (os.path.exists(f) or os.path.exists(os.path.join(ROOT, f))):
            bad.append(f"file does not exist: {f}")
    return bad


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    arg = sys.argv[1]
    text = sys.stdin.read() if arg == "-" else open(arg, encoding="utf-8").read()
    bad = check(text)
    if bad:
        print("RETURN_CHECK FAIL")
        for b in bad:
            print("  -", b)
        return 1
    print("RETURN_CHECK PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
