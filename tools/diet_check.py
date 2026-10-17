"""Check that a rule diet lost no rule (MASTER_PROMPT Appendix A, v3.7).

    python3 tools/diet_check.py                       (old = git tag agents-v3.6-pre-diet)
    python3 tools/diet_check.py --old <tag-or-commit>
    python3 tools/diet_check.py --lead                (v4.0 Lead diet: old = agents-v3.9-pre-lead-diet, the text
                                                       BEFORE Appendix A; found anywhere in the new MASTER_PROMPT.md
                                                       or docs/agents/*.md)

Takes the OLD Appendix A (`git show <tag>:MASTER_PROMPT.md`, from "## Appendix A" on), splits it into bullets
(lines starting "- " or "1. ", with their continuation lines) and into sentences, and keeps those holding a rule
word (never, always, must, only, ≤, ≥, M<digits>). FAIL (exit 1) if any such bullet or sentence is found neither
in the NEW Appendix A nor in any docs/agents/*.md file (whitespace normalised). Prints the missing ones.
"""
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULE = re.compile(r"\b(never|always|must|only)\b|≤|≥|\bM\d+", re.I)
BULLET = re.compile(r"^\s*(?:[-*]|\d+\.)\s")
FRONT = re.compile(r"^(name|description|tools|disallowedTools|model|maxTurns|effort|omitClaudeMd|hooks): ")
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z*`(\[\"])")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def appendix(text):
    i = text.find("## Appendix A")
    if i < 0:
        sys.exit("no '## Appendix A' heading found")
    return text[i:]


def units(text):
    """Bullets (continuation lines joined) and sentences of the text, normalised."""
    out, cur = [], []
    for line in text.splitlines() + [""]:
        if not line.strip() or line.strip() == "---" or line.startswith("#") or line.startswith("```") or line.startswith("````"):
            if cur:
                out.append(" ".join(cur))
                cur = []
            continue
        if FRONT.match(line):  # v4.1: each frontmatter setting is its own unit, so a new setting loses no rule
            if cur:
                out.append(" ".join(cur))
                cur = []
            out.append(line.strip())
            continue
        if BULLET.match(line) and cur:
            out.append(" ".join(cur))
            cur = []
        cur.append(line.strip())
    res = set()
    for u in out:
        res.add(norm(u))
        for s in SENT.split(u):
            res.add(norm(s))
    return res


def main():
    lead = "--lead" in sys.argv
    old_ref = "agents-v3.9-pre-lead-diet" if lead else "agents-v3.6-pre-diet"
    if "--old" in sys.argv:
        old_ref = sys.argv[sys.argv.index("--old") + 1]
    old = subprocess.run(["git", "show", f"{old_ref}:MASTER_PROMPT.md"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout
    new = open(os.path.join(ROOT, "MASTER_PROMPT.md"), encoding="utf-8").read()
    corpus = new if lead else appendix(new)
    refs = sorted(glob.glob(os.path.join(ROOT, "docs", "agents", "*.md")))
    for p in refs:
        corpus += "\n" + open(p, encoding="utf-8").read()
    hay = norm(corpus)
    part = old[:old.find("## Appendix A")] if lead else appendix(old)
    need = sorted(u for u in units(part) if RULE.search(u) and len(u) > 3)
    missing = [u for u in need if u not in hay]
    print(f"old rule units: {len(need)}; reference files: {len(refs)}; missing: {len(missing)}")
    if missing:
        print("DIET_CHECK FAIL")
        for u in missing:
            print("  -", u[:200])
        return 1
    print("DIET_CHECK PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
