"""Write the agent files from MASTER_PROMPT.md (Appendix A) into .claude/agents/.

    python3 tools/build_agents.py           (write or refresh every agent file)
    python3 tools/build_agents.py --check   (only report files that differ; exits 1 if any do)

MASTER_PROMPT.md is the source: edit an agent there, then run this.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCK = re.compile(r"^File: `(\.claude/agents/[\w-]+\.md)`\n````markdown\n(.*?)\n````$", re.M | re.S)


def main():
    with open(os.path.join(ROOT, "MASTER_PROMPT.md"), encoding="utf-8") as f:
        blocks = BLOCK.findall(f.read())
    if not blocks:
        sys.exit("no agent blocks found in MASTER_PROMPT.md")
    check = "--check" in sys.argv
    stale = 0
    for rel, body in blocks:
        path = os.path.join(ROOT, rel)
        new = body + "\n"
        old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if old == new:
            print("same    ", rel)
            continue
        stale += 1
        if check:
            print("differs ", rel)
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        print("wrote   ", rel)
    return 1 if check and stale else 0


if __name__ == "__main__":
    sys.exit(main())
