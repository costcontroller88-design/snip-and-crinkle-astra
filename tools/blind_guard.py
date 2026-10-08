"""PreToolUse hook that keeps the fresh-eyes-reviewer blind (audit M1, 9 Oct).

Set in the reviewer's frontmatter in MASTER_PROMPT.md Appendix A (`hooks: PreToolUse`, matcher Read|Bash|Glob|Grep;
code.claude.com/docs/en/sub-agents: frontmatter `hooks` run only while that subagent runs). Claude Code pipes the call
as JSON on stdin ({"tool_name", "tool_input", "cwd", ...}); exit 2 blocks it and the one-line reason on stderr goes to
the reviewer. Exit 0 allows.

  Denied: anything under the repo's reviews/, episodes/, output/, Videos/, docs/ (except
          docs/agents/fresh-eyes-reviewer_reference.md), and MASTER_PROMPT.md, HANDOFF.md, CLAUDE.md. Glob and Grep
          also may not start at the repo root or above it (they would walk the denied folders), and a Grep/Glob with
          no path is searched from the repo, so it is denied too.
  Allowed: build/, the system temp folders, and the reviewer's own two files
          (.claude/agents/fresh-eyes-reviewer.md, docs/agents/fresh-eyes-reviewer_reference.md).
Bash: every path-like word in the command is checked the same way; a relative word that names a denied folder is
denied wherever the shell is (it may follow a `cd`). This is a guard against accidents, not a sandbox: shell
wildcards, variables and `eval` can still get round it.

    echo '{"tool_name":"Read","tool_input":{"file_path":"reviews/ep11_plan.md"}}' | python3 tools/blind_guard.py
"""
import json
import os
import re
import shlex
import sys

ROOT = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DENIED_DIRS = {"reviews", "episodes", "output", "videos", "docs"}
DENIED_FILES = {"master_prompt.md", "handoff.md", "claude.md"}
OWN = {os.path.join(ROOT, ".claude", "agents", "fresh-eyes-reviewer.md"),
       os.path.join(ROOT, "docs", "agents", "fresh-eyes-reviewer_reference.md")}
OWN_NAMES = [".claude/agents/fresh-eyes-reviewer.md", "docs/agents/fresh-eyes-reviewer_reference.md"]


def judge(path, cwd, walk=False):
    """Reason string if `path` is off limits, else None. walk: a tool that would traverse the folder."""
    p = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
    if p in OWN:
        return None
    if p == ROOT or ROOT.startswith(p.rstrip("/") + "/") or p == "/":
        return f"{path or '.'} is the repo root or above it" if walk else None
    if p.startswith(ROOT + "/"):
        rel = p[len(ROOT) + 1:].split("/")
        if rel[0].lower() in DENIED_DIRS or (len(rel) == 1 and rel[0].lower() in DENIED_FILES):
            return f"{rel[0]}{'/' if rel[0].lower() in DENIED_DIRS else ''} is off limits to the blind reviewer"
    return None


def bash_reason(cmd, cwd):
    for n in OWN_NAMES:
        cmd = cmd.replace(n, "OWNFILE")
    try:
        words = shlex.split(cmd, posix=True)
    except ValueError:
        words = cmd.split()
    first = words[0] if words else ""
    for w in words:
        for part in re.split(r"[=;|&<>()]", w):
            if not part or not ("/" in part or part.startswith((".", "~")) or part.lower() in DENIED_FILES
                                or part.lower() in DENIED_DIRS):
                continue
            segs = [s.lower() for s in part.split("/") if s]
            if not part.startswith(("/", "~")) and (set(segs) & DENIED_DIRS or set(segs) & DENIED_FILES):
                return f"'{part}' names a folder or file off limits to the blind reviewer"
            r = judge(part, cwd, walk=first not in ("ls", "cd", "pwd", "stat", "echo"))
            if r:
                return r
    return None


def main():
    try:
        d = json.load(sys.stdin)
        tool, ti = d["tool_name"], d.get("tool_input") or {}
        cwd = d.get("cwd") or os.getcwd()
    except (ValueError, KeyError, TypeError):
        print("blind_guard: unreadable hook input, blocked", file=sys.stderr)
        sys.exit(2)
    reason = None
    if tool == "Read":
        reason = judge(ti.get("file_path", ""), cwd)
    elif tool in ("Glob", "Grep"):
        reason = judge(ti.get("path") or ".", cwd, walk=True)
        if not reason and tool == "Glob":
            pat = ti.get("pattern", "")
            reason = judge(pat.split("*")[0] or ".", os.path.join(cwd, ti.get("path") or ""), walk=True) \
                if os.path.isabs(pat) else None
    elif tool == "Bash":
        reason = bash_reason(ti.get("command", ""), cwd)
    if reason:
        print(f"blind_guard: {reason}; the reviewer sees only the video, its own two files and temp/build", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
