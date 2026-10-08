"""Check HANDOFF.md before it is committed (runs from the git pre-commit hook; mistakes M9, M18, M20).

    python3 tools/handoff_check.py            check the working-tree HANDOFF.md against the last commit
    python3 tools/handoff_check.py --staged   check the staged HANDOFF.md (what the hook uses)
    python3 tools/handoff_check.py --install  install the git pre-commit hook

Fails (exit 1) when:
  1. HANDOFF.md is over 500 words;
  2. a file path it names doesn't exist on disk;
  3. a fact removed since the last commit (a `quoted` item, a file path, or a mistake id like M17) exists nowhere
     else in the repo, i.e. a trim would lose it. Move it to docs/HISTORY.md (or the file it belongs in) first.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAP = 500
PATH_RE = re.compile(r"(?<![\w/])((?:[\w.-]+/)*[\w.-]+\.(?:md|py|mp4|png|txt|sh|json))\b")
TICK_RE = re.compile(r"`([^`]+)`")
MID_RE = re.compile(r"\bM\d{1,3}\b")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


def facts(text):
    out = set(TICK_RE.findall(text)) | set(PATH_RE.findall(text)) | set(MID_RE.findall(text))
    return {f.strip() for f in out if len(f.strip()) > 2}


def found_elsewhere(fact):
    hits = git("grep", "-l", "-F", "--", fact, "--", ".", ":!HANDOFF.md").split()
    if hits:
        return True
    return os.path.exists(os.path.join(ROOT, fact))  # untracked files (output/, Videos/) count


def placeholder(p):
    return any(c in p for c in "<>*") or "NN" in p or "epNN" in p


def main():
    if "--install" in sys.argv:
        hook = os.path.join(ROOT, ".git", "hooks", "pre-commit")
        with open(hook, "w") as f:
            f.write("#!/bin/sh\nif git diff --cached --name-only | grep -qx HANDOFF.md; then\n"
                    "  python3 tools/handoff_check.py --staged || exit 1\nfi\n")
        os.chmod(hook, 0o755)
        print("installed", hook)
        return 0
    new = git("show", ":HANDOFF.md") if "--staged" in sys.argv else open(os.path.join(ROOT, "HANDOFF.md")).read()
    old = git("show", "HEAD:HANDOFF.md")
    errors = []
    words = len(new.split())
    if words > CAP:
        errors.append(f"{words} words (cap {CAP}): cut {words - CAP}, moving facts to docs/HISTORY.md if needed")
    for p in sorted(set(PATH_RE.findall(new))):
        if placeholder(p):
            continue
        if not any(os.path.exists(os.path.join(ROOT, d, p)) for d in ("", "docs", "reviews", "episodes", "tools")):
            errors.append(f"names a path that doesn't exist: {p}")
    for f in sorted(facts(old) - facts(new)):
        if not placeholder(f) and not found_elsewhere(f):
            errors.append(f"removed fact exists nowhere else: {f!r} (move it to docs/HISTORY.md first)")
    if errors:
        print("HANDOFF CHECK FAIL\n  " + "\n  ".join(errors))
        return 1
    print(f"HANDOFF CHECK PASS ({words} words)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
