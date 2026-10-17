"""Harness hooks for the agent team (v4.1, 17 Oct 2026; docs/research-agent-reliability-oct-2026.md rows 1-6).

Checks that used to depend on someone remembering them now run on their own, at zero model tokens:

    python3 tools/agent_hooks.py stop    SubagentStop (a Stop hook in each agent's frontmatter): runs return_check on
                                         the agent's last message and compares its tool_calls with the harness count;
                                         a fixable FAIL sends the agent back ONCE with the reason; every run gets a
                                         row in reviews/agent_runs.md (real calls, peak context, verdict).
    python3 tools/agent_hooks.py count   PostToolUse (frontmatter): counts the agent's real tool calls; every 5th call
                                         and at 80%/100% of its largest budget it tells the agent the count.
    python3 tools/agent_hooks.py scope   PreToolUse (frontmatter): each role writes only where its job is; no agent
                                         edits tools/, MASTER_PROMPT.md, HANDOFF.md, CLAUDE.md, .claude/, docs/agents/
                                         or the logs; nobody pushes or hard-resets; only packaging writes Videos/;
                                         the animator never reads blind reviews; the growth-analyst can't type in Studio.
    python3 tools/agent_hooks.py brief   PreToolUse on Agent|Task (the Lead's settings.json): briefs <=6 lines;
                                         animator briefs pass brief_check (with --plan when the plan exists); a
                                         reviewer brief carries no story; the preflight band (.preflight_band, <2 h
                                         old) allows the agent.

Claude Code pipes the event as JSON on stdin. Decisions are JSON on stdout with exit 0. Any error inside this script
allows the action (fail open): the blind reviewer's own guard, tools/blind_guard.py, is the one that fails closed.
Tests: python3 tools/regress.py
"""
import datetime
import json
import os
import re
import shlex
import sys
import tempfile
import time

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.realpath(os.path.dirname(TOOLS))
sys.path.insert(0, TOOLS)

TEAM = ("story-designer", "safety-checker", "animator", "fresh-eyes-reviewer", "packaging", "growth-analyst")
# The largest budget each agent file gives (count warnings); stage budgets are smaller and live in the agent file.
MAX_BUDGET = {"story-designer": 25, "safety-checker": 18, "animator": 60, "fresh-eyes-reviewer": 40,
              "packaging": 15, "growth-analyst": 40}
PROTECTED = ("tools/", "MASTER_PROMPT.md", "HANDOFF.md", "CLAUDE.md", ".claude/", "docs/agents/", ".git/",
             "reviews/mistake_log.md", "reviews/agent_runs.md", ".preflight_band")
WRITE_OK = {  # repo-relative prefixes each role may write (temp folders are always fine)
    "story-designer": ("reviews/", "docs/CHARACTER_BIBLE.md", "build/"),
    "safety-checker": ("reviews/", "build/"),
    "packaging": ("reviews/", "Videos/", "build/"),
    "growth-analyst": ("docs/", "reviews/", "build/"),
    "fresh-eyes-reviewer": ("build/",),
    "animator": ("",),  # anywhere not protected, except Videos/ (the Lead owns renders and the owner's folder)
}
STATE = os.path.join(tempfile.gettempdir(), "snc_agent_hooks")
RUNS = os.path.join(ROOT, "reviews", "agent_runs.md")
BAND = os.path.join(ROOT, ".preflight_band")
BAND_MAX_AGE = 2 * 3600
LEAK = re.compile(r"\bep\s?\d|\bplan\b|\blesson|\bstory\b|story card|\bsnip\b|crinkle|\bpip\b|reviews/|episodes/|"
                  r"\bgag|\bmoral\b", re.I)


def out(obj):
    print(json.dumps(obj))
    return 0


def deny(reason, event="PreToolUse"):
    return out({"hookSpecificOutput": {"hookEventName": event, "permissionDecision": "deny",
                                       "permissionDecisionReason": reason}})


def context(text, event):
    return out({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}})


# ---------------------------------------------------------------- state per agent run

def state_path(agent_id):
    os.makedirs(STATE, exist_ok=True)
    return os.path.join(STATE, re.sub(r"[^\w-]", "_", agent_id or "main") + ".json")


def load_state(agent_id):
    try:
        with open(state_path(agent_id), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"calls": 0, "blocks": 0}


def save_state(agent_id, st):
    with open(state_path(agent_id), "w", encoding="utf-8") as f:
        json.dump(st, f)


# ---------------------------------------------------------------- count

def cmd_count(d):
    agent, aid = d.get("agent_type", ""), d.get("agent_id", "")
    if agent not in TEAM:
        return 0
    st = load_state(aid)
    st["calls"] += 1
    save_state(aid, st)
    n, cap = st["calls"], MAX_BUDGET[agent]
    if n >= cap:
        msg = f"Hook count: {n} tool calls = your largest budget ({cap}). Start no new work; write your return now."
    elif n == int(cap * 0.8):
        msg = f"Hook count: {n} tool calls (80% of your largest budget {cap}). Finish the current item, then return."
    elif n % 5 == 0:
        msg = f"Hook count: {n} tool calls so far (use this, not your own tally; stage budgets are in your file)."
    else:
        return 0
    return context(msg, "PostToolUse")


# ---------------------------------------------------------------- scope

def rel(path, cwd):
    """('repo', relative path) inside the repo, ('temp', p) in a temp folder, ('outside', p) elsewhere."""
    p = os.path.realpath(os.path.join(cwd or ROOT, os.path.expanduser(path)))
    if p == ROOT:
        return "repo", ""
    if p.startswith(ROOT + "/"):
        return "repo", p[len(ROOT) + 1:]
    tmps = {os.path.realpath(t) for t in (tempfile.gettempdir(), "/tmp", "/private/tmp", "/var/folders")}
    if any(p == t or p.startswith(t.rstrip("/") + "/") for t in tmps):
        return "temp", p
    return "outside", p


def write_reason(agent, path, cwd):
    where, r = rel(path, cwd)
    if where == "temp":
        return None
    if where == "outside":
        return f"{path} is outside the project; write in the repo's build/ or a temp folder"
    for p in PROTECTED:
        if r == p.rstrip("/") or r.startswith(p if p.endswith("/") else p + "\0"):
            return f"{r} is protected (rules, checkers and logs belong to the Lead)"
    if agent != "packaging" and (r == "Videos" or r.startswith("Videos/")):
        return "Videos/ is the owner's folder: only the Lead (and packaging's upload files) write there"
    if not any(r.startswith(ok) for ok in WRITE_OK[agent]):
        return f"{r}: a {agent} writes only in {', '.join(WRITE_OK[agent])}"
    return None


SPLIT = re.compile(r"\|\||&&|[;|\n]")


def bash_targets(cmd):
    """(paths a command writes, a forbidden git action or None). A guard against accidents, not a sandbox."""
    targets, bad = [], None
    for seg in SPLIT.split(cmd):
        try:
            w = shlex.split(seg, posix=True)
        except ValueError:
            w = seg.split()
        if not w:
            continue
        for i, t in enumerate(w):  # redirections: "> f", ">> f", "2>f", ">f"
            m = re.match(r"^\d?>>?(.*)$", t)
            if m:
                tgt = m.group(1) or (w[i + 1] if i + 1 < len(w) else "")
                if tgt and not tgt.startswith("&") and tgt != "/dev/null":
                    targets.append(tgt)
        args = [a for a in w[1:] if not a.startswith("-") and not re.match(r"^\d?>", a)]
        head = os.path.basename(w[0])
        if head in ("cp", "mv", "install", "rsync", "ln") and args:
            targets.append(args[-1])
        elif head in ("rm", "touch", "tee", "rmdir", "truncate") or (head == "sed" and any(a.startswith("-i") for a in w)):
            targets += args if head != "sed" else args[-1:]
        elif head == "git" and args:
            sub = args[0]
            if sub == "push":
                bad = "git push: only the Lead pushes, after git show --stat"
            elif sub == "reset" and "--hard" in w or sub == "clean" or (sub == "tag" and "-d" in w):
                bad = f"git {sub} {'--hard ' if sub == 'reset' else ''}is destructive: ask the Lead"
            elif sub in ("checkout", "restore") and "--" in w:
                targets += w[w.index("--") + 1:]
    return targets, bad


def cmd_scope(d):
    agent, tool, ti = d.get("agent_type", ""), d.get("tool_name", ""), d.get("tool_input") or {}
    cwd = d.get("cwd") or ROOT
    if agent not in TEAM:
        return 0
    reason = None
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        reason = write_reason(agent, ti.get("file_path") or ti.get("notebook_path") or "", cwd)
    elif tool == "Read" and agent == "animator":
        where, r = rel(ti.get("file_path", ""), cwd)
        if where == "repo" and r.startswith("reviews/") and "blind" in r:
            reason = "the animator works from the fix file, never the blind reviews (animator inputs)"
    elif tool == "Bash":
        targets, reason = bash_targets(ti.get("command", ""))
        for t in targets:
            reason = reason or write_reason(agent, t, cwd)
    elif tool.startswith("mcp__") and "Browser" in tool:
        act = ti.get("action", "")
        if agent != "growth-analyst":
            reason = "only the growth-analyst opens the browser (Studio, read-only)"
        elif tool.endswith(("form_input", "javascript_tool")) or act in ("type", "key", "left_click_drag"):
            reason = "Studio is read-only for agents: no typing, form filling or scripts (core rule 1)"
    return deny(f"agent_hooks scope: {reason}") if reason else 0


# ---------------------------------------------------------------- stop

def last_text_from_transcript(path):
    text = ""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    m = json.loads(line).get("message") or {}
                except ValueError:
                    continue
                if m.get("role") == "assistant":
                    t = "".join(c.get("text", "") for c in m.get("content", []) if isinstance(c, dict)
                                and c.get("type") == "text")
                    if t.strip():
                        text = t
    except OSError:
        pass
    return text


def agent_transcript(d):
    p = d.get("agent_transcript_path")
    if p and os.path.exists(p):
        return p
    tp, aid = d.get("transcript_path") or "", d.get("agent_id") or ""
    if tp and aid:
        cand = os.path.join(tp[:-6] if tp.endswith(".jsonl") else tp, "subagents", f"agent-{aid}.jsonl")
        if os.path.exists(cand):
            return cand
    return None


def transcript_stats(path):
    """(tool calls, peak context tokens, output tokens) from an agent transcript; Nones if unreadable."""
    if not path:
        return None, None, None
    tools, peak, outs = set(), 0, {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                m = e.get("message") or {}
                if m.get("role") != "assistant":
                    continue
                for c in m.get("content", []):
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        tools.add(c.get("id"))
                u = m.get("usage") or {}
                ctx = sum(u.get(k, 0) or 0 for k in ("input_tokens", "cache_creation_input_tokens",
                                                       "cache_read_input_tokens"))
                peak = max(peak, ctx)
                outs[e.get("requestId") or m.get("id") or len(outs)] = u.get("output_tokens", 0) or 0
    except OSError:
        return None, None, None
    return len(tools), peak, sum(outs.values())


def log_run(agent, verdict, real, reported, budget, peak, out_tok, rc, blocked):
    new = not os.path.exists(RUNS)
    with open(RUNS, "a", encoding="utf-8") as f:
        if new:
            f.write("# Agent runs (written by tools/agent_hooks.py stop; the Lead reads it with tail)\n\n"
                    "| When | Agent | Verdict | Calls real / reported / budget | Peak context | Output | "
                    "return_check | Sent back |\n|---|---|---|---|---|---|---|---|\n")
        k = lambda v: f"{v / 1000:.0f}k" if isinstance(v, (int, float)) else "?"
        f.write(f"| {datetime.datetime.now():%d %b %H:%M} | {agent} | {verdict} | {real if real is not None else '?'}"
                f" / {reported} / {budget} | {k(peak)} | {k(out_tok)} | {rc} | {'yes' if blocked else 'no'} |\n")


def cmd_stop(d):
    agent, aid = d.get("agent_type", ""), d.get("agent_id", "")
    if agent not in TEAM:
        return 0
    import return_check
    text = d.get("last_assistant_message") or last_text_from_transcript(agent_transcript(d) or "")
    real, peak, out_tok = transcript_stats(agent_transcript(d))
    st = load_state(aid)
    if real is None:
        real = st.get("calls") or None
    problems = return_check.check(text) if text else ["no final message found"]
    record_only = [p for p in problems if p.startswith("over budget")]
    fixable = [p for p in problems if p not in record_only]
    try:
        js = json.loads(return_check.BLOCK.findall(text)[-1])
    except (IndexError, ValueError, TypeError):
        js = {}
    reported = js.get("tool_calls", "?") if isinstance(js, dict) else "?"
    budget = js.get("budget", "?") if isinstance(js, dict) else "?"
    if isinstance(reported, int) and real and real - reported >= 3:
        fixable.append(f"tool_calls says {reported}, the harness counted {real}: report the true count")
    if isinstance(budget, int) and real and real > budget and not record_only:
        record_only.append(f"over budget: {real} real calls > budget {budget}")
    can_block = fixable and st.get("blocks", 0) < 1 and not d.get("stop_hook_active")
    rc = "PASS" if not problems and not fixable else "FAIL: " + "; ".join((fixable + record_only))[:160].replace("|", "/")
    if can_block:
        st["blocks"] = st.get("blocks", 0) + 1
        save_state(aid, st)
        log_run(agent, js.get("verdict", "?") if isinstance(js, dict) else "?", real, reported, budget, peak, out_tok,
                rc, True)
        return out({"decision": "block", "reason": "return_check FAIL (fix only these, with no new work, then end "
                    "with the corrected JSON block): " + "; ".join(fixable)})
    log_run(agent, js.get("verdict", "?") if isinstance(js, dict) else "?", real, reported, budget, peak, out_tok, rc,
            False)
    try:
        os.remove(state_path(aid))
    except OSError:
        pass
    return 0


# ---------------------------------------------------------------- brief (the Lead's Agent calls)

def read_band():
    try:
        with open(BAND, encoding="utf-8") as f:
            b = json.load(f)
        return b if time.time() - b.get("time", 0) < BAND_MAX_AGE else None
    except (OSError, ValueError):
        return None


def cmd_brief(d):
    ti = d.get("tool_input") or {}
    agent = ti.get("subagent_type", "")
    if agent not in TEAM:
        return 0
    prompt = ti.get("prompt", "")
    lines = [ln for ln in prompt.splitlines() if ln.strip()]
    if len(lines) > 6:
        return deny(f"agent_hooks brief: {len(lines)} lines (core rule 4: <=6; the agent file carries the rest)")
    b = read_band()
    if not b:
        return deny("agent_hooks brief: no preflight in the last 2 hours. Run get_usage, then python3 "
                    "tools/preflight.py --used <5h %> --reset-min <min> --weekly <%> (core rule 1)")
    import preflight
    if preflight.forbidden(b["band"], agent):
        return deny(f"agent_hooks brief: preflight band '{b['band']}' forbids {agent} (core rule 1)")
    if agent == "fresh-eyes-reviewer":
        m = LEAK.search(prompt)
        if m:
            return deny(f"agent_hooks brief: a blind brief may not mention '{m.group(0)}': give only the neutral "
                        "copy's path and the round number")
    if agent == "animator":
        import brief_check
        text = prompt if prompt.lower().startswith("animator") else "animator: " + prompt
        ep = re.search(r"\bep(\d{2})", prompt, re.I)
        plan = os.path.join(ROOT, "reviews", f"ep{ep.group(1)}_plan.md") if ep else None
        fails = brief_check.check(text, plan if plan and os.path.exists(plan) else None)
        if fails:
            return deny("agent_hooks brief (brief_check): " + "; ".join(fails))
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        d = json.load(sys.stdin)
        return {"count": cmd_count, "scope": cmd_scope, "stop": cmd_stop, "brief": cmd_brief}[cmd](d) or 0
    except Exception as e:  # fail open: a broken hook must never trap an agent
        print(f"agent_hooks {cmd}: internal error, allowed ({type(e).__name__}: {e})", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
