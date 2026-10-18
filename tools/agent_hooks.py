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
                                         old) allows the agent. v4.2: the gate tracker (state/gates.json, written
                                         only by tools/gate.py) refuses an animator "build" brief before gate1 PASS
                                         and packaging before gate2 PASS (or an --owner-ok record, M44); a brief's
                                         "Stage: <name>" leaves that stage's budget for the agent's count hook.
    python3 tools/agent_hooks.py lead    PreToolUse (settings.json, the Lead only = no agent_type): refuses git push
                                         unless git show --stat ran in the last 10 minutes on the same HEAD (rule 8);
                                         refuses typing, clicking or form filling on a studio.youtube.com page unless
                                         tools/approve.py "<owner quote>" ran in the last 30 minutes (rule 11).
    python3 tools/agent_hooks.py leadpost  PostToolUse (settings.json): records git show --stat and the browser URL.
    Send-back (M62): the app ends a run with a SubagentHandback call, so an agent's Stop-hook send-back comes too
                                         late; a fixable FAIL leaves a note, and the Lead's next Bash or Agent call is
                                         refused once with "send it back (SendMessage)". leadstop: the same at the
                                         Lead's Stop (settings.json), where the app runs it.
    python3 tools/agent_hooks.py selftest  feeds sample events to every hook on scratch state; exit 1 on any wrong
                                         decision. --hook (SessionStart): silent on PASS, one warning line on FAIL.

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
# Stage budgets from the "Inputs and budget" lines of MASTER_PROMPT Appendix A; a brief's "Stage: <name>" picks
# the first key found, in this order ("feasibility first, then build" = build; "feasibility only" = feasibility).
STAGE_BUDGET = {
    "animator": (("short", 30), ("build", 60), ("toolkit", 25), ("prototype", 15), ("storyboard", 25),
                 ("measure", 25), ("fix", 20), ("feasibility", 5)),
    "story-designer": (("fix", 12), ("plan", 25)),
    "safety-checker": (("gate 3", 18), ("gate3", 18), ("gate 1", 14), ("gate1", 14), ("re-check", 14),
                       ("recheck", 14)),
}
PROTECTED = ("tools/", "MASTER_PROMPT.md", "HANDOFF.md", "CLAUDE.md", ".claude/", "docs/agents/", ".git/",
             "reviews/mistake_log.md", "reviews/agent_runs.md", ".preflight_band", "state/")
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
GATES = os.path.join(ROOT, "state", "gates.json")  # tools/gate.py writes it
APPROVALS = os.path.join(ROOT, "state", "approvals.jsonl")  # tools/approve.py appends to it
SENDBACK_MAX_AGE = 1800
PENDING_MAX_AGE = 600  # a stage left by a brief is picked up by the agent's first call within 10 minutes
SHOW_MAX_AGE, APPROVAL_MAX_AGE = 600, 1800
EPISODE = re.compile(r"\bep(?:isode)?[\s_-]?0*(\d{1,2})(?!\d)", re.I)
BUILD = re.compile(r"\bbuild\b(?!/)", re.I)
STUDIO = re.compile(r"studio\.youtube\.com|youtube\.com/upload", re.I)
HANDBACK = "SubagentHandback"
BROWSER_WRITE = ("left_click", "right_click", "double_click", "triple_click", "type", "key", "left_click_drag")
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


def pending_path(agent):
    os.makedirs(STATE, exist_ok=True)
    return os.path.join(STATE, f"pending_{agent}.json")


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


# ---------------------------------------------------------------- count

def cmd_count(d):
    agent, aid = d.get("agent_type", ""), d.get("agent_id", "")
    if agent not in TEAM:
        return 0
    st = load_state(aid)
    st["calls"] += 1
    if st["calls"] == 1:  # the agent's first call picks up the stage its brief named
        p = pending_path(agent)
        try:
            with open(p, encoding="utf-8") as f:
                pend = json.load(f)
            os.remove(p)
            if time.time() - pend.get("time", 0) < PENDING_MAX_AGE:
                st["stage"], st["stage_budget"] = pend["stage"], pend["budget"]
        except (OSError, ValueError, KeyError):
            pass
    save_state(aid, st)
    n, cap = st["calls"], MAX_BUDGET[agent]
    stage, sb = st.get("stage"), st.get("stage_budget")
    if sb and n >= sb:
        msg = f"Hook count: {n} tool calls = your '{stage}' stage budget ({sb}). Start no new work; write your return now."
    elif n >= cap:
        msg = f"Hook count: {n} tool calls = your largest budget ({cap}). Start no new work; write your return now."
    elif sb and n == int(sb * 0.8):
        msg = f"Hook count: {n} tool calls (80% of your '{stage}' stage budget {sb}). Finish the current item, then return."
    elif n == int(cap * 0.8):
        msg = f"Hook count: {n} tool calls (80% of your largest budget {cap}). Finish the current item, then return."
    elif n % 5 == 0:
        msg = f"Hook count: {n} tool calls so far (use this, not your own tally; " + (
            f"your '{stage}' stage budget is {sb})." if sb else "stage budgets are in your file).")
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
        if any(os.path.basename(a) in ("gate.py", "approve.py") for a in w) and "show" not in w:
            bad = "only the Lead records gates and owner approvals (tools/gate.py, tools/approve.py)"
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
                    for c in m.get("content", []):  # the desktop app delivers the report as a tool call (M61)
                        if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == HANDBACK:
                            t = str((c.get("input") or {}).get("message", ""))
                    if t.strip():
                        text = t
    except OSError:
        pass
    return text


def handed_back(d):
    """True when the agent's transcript ends its run with a SubagentHandback call."""
    try:
        with open(agent_transcript(d) or "", encoding="utf-8") as f:
            return bool(re.search(r'"name":\s*"' + HANDBACK + '"', f.read()))
    except OSError:
        return False


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
                    if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") != HANDBACK:
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
    text = last_text_from_transcript(agent_transcript(d) or "") or d.get("last_assistant_message")
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
    can_block = fixable and st.get("blocks", 0) < 1 and not d.get("stop_hook_active") and not handed_back(d)
    rc = "PASS" if not problems and not fixable else "FAIL: " + "; ".join((fixable + record_only))[:160].replace("|", "/")
    if can_block:
        st["blocks"] = st.get("blocks", 0) + 1
        save_state(aid, st)
        log_run(agent, js.get("verdict", "?") if isinstance(js, dict) else "?", real, reported, budget, peak, out_tok,
                rc, True)
        return out({"decision": "block", "reason": "return_check FAIL (fix only these, with no new work, then end "
                    "with the corrected JSON block): " + "; ".join(fixable)})
    if fixable and handed_back(d) and not d.get("stop_hook_active"):
        with open(pending_path("sendback_" + agent), "w", encoding="utf-8") as f:
            json.dump({"agent_id": aid, "reasons": fixable, "time": time.time()}, f)
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
    sb = None if d.get("agent_type") else take_sendback()
    if sb:
        return deny(sb)
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
    ep = episode(prompt)
    if agent == "animator" and ep and BUILD.search(prompt) and not gate_ok(ep, "gate1"):
        return deny(f"agent_hooks brief: {ep} gate1 is not PASS in state/gates.json; a build waits for the safety "
                    f"PASS (python3 tools/gate.py set {ep} gate1 PASS --evidence reviews/{ep}_safety.md)")
    if agent == "packaging" and ep and not gate_ok(ep, "gate2"):
        return deny(f"agent_hooks brief: {ep} gate2 is not PASS in state/gates.json; packaging waits for the blind "
                    f"review PASS (tools/gate.py set {ep} gate2 PASS --evidence <blind review>, or --owner-ok "
                    "\"<the owner's words>\" as in M44)")
    if agent == "animator":
        import brief_check
        text = prompt if prompt.lower().startswith("animator") else "animator: " + prompt
        plan = os.path.join(ROOT, "reviews", f"{ep}_plan.md") if ep else None
        fails = brief_check.check(text, plan if plan and os.path.exists(plan) else None)
        if fails:
            return deny("agent_hooks brief (brief_check): " + "; ".join(fails))
    st = stage_of(agent, prompt)
    if st:
        with open(pending_path(agent), "w", encoding="utf-8") as f:
            json.dump({"stage": st[0], "budget": st[1], "time": time.time()}, f)
    return 0


def episode(text):
    m = EPISODE.search(text)
    return f"ep{int(m.group(1)):02d}" if m else None


def gate_ok(ep, gate):
    rec = (load_json(GATES, {}).get(ep) or {}).get(gate) or {}
    return rec.get("result") == "PASS" or bool(rec.get("owner_ok"))


def stage_of(agent, prompt):
    """(stage key, budget) from the brief's "Stage: <name>" line, or None."""
    m = re.search(r"\bstage:\s*(.+)", prompt, re.I)
    if not m or agent not in STAGE_BUDGET:
        return None
    for key, budget in STAGE_BUDGET[agent]:
        if re.search(r"\b" + re.escape(key) + r"\b", m.group(1), re.I):
            return key, budget
    return None


# ---------------------------------------------------------------- lead (the Lead's own risky actions)

LEAD_STATE = "lead"  # state file name in STATE


def git_head():
    import subprocess
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                              timeout=5).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def git_runs(cmd, sub, flag=""):
    """True when a segment of the command runs `git <sub>` (with `flag`), not when the words sit in a heredoc."""
    for seg in SPLIT.split(cmd):
        try:
            w = shlex.split(seg, posix=True)
        except ValueError:
            w = seg.split()
        while w and re.match(r"^\w+=", w[0]):  # VAR=value prefixes
            w = w[1:]
        if w and os.path.basename(w[0]) == "git" and sub in w[1:] and (not flag or flag in w):
            return True
    return False


def browser_steps(tool, ti):
    """(tool short name, input) for a browser call; a browser_batch yields each of its items."""
    short = tool.rsplit("__", 1)[-1]
    if short == "browser_batch":
        return [(a.get("name", ""), a.get("input") or {}) for a in ti.get("actions") or [] if isinstance(a, dict)]
    return [(short, ti)]


def is_browser(tool):
    return tool.startswith(("mcp__Claude_Browser__", "mcp__claude-in-chrome__"))


def cmd_lead(d):
    if d.get("agent_type"):
        return 0  # agents are guarded by their own scope hook
    tool, ti = d.get("tool_name", ""), d.get("tool_input") or {}
    if tool == "Bash":
        sb = take_sendback()
        if sb:
            return deny(sb)
    st = load_state(LEAD_STATE)
    if tool == "Bash" and git_runs(ti.get("command", ""), "push"):
        age = time.time() - st.get("show_time", 0)
        if age > SHOW_MAX_AGE:
            return deny("agent_hooks lead: run git show --stat first and read it (core rule 8); last one "
                        + (f"{age / 60:.0f} min ago" if st.get("show_time") else "never"))
        if st.get("show_head") and st["show_head"] != git_head():
            return deny("agent_hooks lead: HEAD changed since your last git show --stat; run it again (core rule 8)")
    elif is_browser(tool):
        tabs, last = dict(st.get("tabs") or {}), st.get("last_url", "")
        for short, inp in browser_steps(tool, ti):
            if short == "navigate":
                last = tabs[str(inp.get("tabId", ""))] = inp.get("url", "")
                continue
            url = tabs.get(str(inp.get("tabId")), last) if inp.get("tabId") else last
            write = short in ("form_input", "javascript_tool", "file_upload", "upload_image") or (
                short == "computer" and inp.get("action") in BROWSER_WRITE)
            if write and STUDIO.search(url or ""):
                rows = [ln for ln in open(APPROVALS, encoding="utf-8")] if os.path.exists(APPROVALS) else []
                t = json.loads(rows[-1]).get("time", 0) if rows else 0
                if time.time() - t > APPROVAL_MAX_AGE:
                    return deny("agent_hooks lead: a Studio change needs the owner's fresh yes: python3 tools/approve.py"
                                " \"<the owner's exact words>\" (core rule 11; valid 30 minutes)")
    return 0


def cmd_leadpost(d):
    if d.get("agent_type"):
        return 0
    tool, ti = d.get("tool_name", ""), d.get("tool_input") or {}
    st = load_state(LEAD_STATE)
    if tool == "Bash" and git_runs(ti.get("command", ""), "show", "--stat"):
        st["show_time"], st["show_head"] = time.time(), git_head()
    elif is_browser(tool):
        resp = json.dumps(d.get("tool_response", ""))[:3000]
        st.setdefault("tabs", {})
        for short, inp in browser_steps(tool, ti):
            if short in ("navigate", "preview_start") and inp.get("url"):
                url = inp["url"] + (" studio.youtube.com" if STUDIO.search(resp) else "")
                st["tabs"][str(inp.get("tabId", ""))] = st["last_url"] = url
    else:
        return 0
    save_state(LEAD_STATE, st)
    return 0


# ---------------------------------------------------------------- selftest (SessionStart health check)

def selftest():
    """[(name, ok)] from sample events fed through dispatch() on scratch state; live files are never touched."""
    import shutil
    g = globals()
    keep = {k: g[k] for k in ("STATE", "RUNS", "BAND", "GATES", "APPROVALS")}
    tmp = tempfile.mkdtemp(prefix="snc_selftest_")
    g.update(STATE=os.path.join(tmp, "s"), RUNS=os.path.join(tmp, "runs.md"), BAND=os.path.join(tmp, "band"),
             GATES=os.path.join(tmp, "gates.json"), APPROVALS=os.path.join(tmp, "approvals.jsonl"))
    res = []

    def run(cmd, d):
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            dispatch(cmd, json.dumps(d))
        s = buf.getvalue().strip()
        return json.loads(s) if s else {}

    def denies(cmd, d):
        return (run(cmd, d).get("hookSpecificOutput") or {}).get("permissionDecision") == "deny"

    def ok(name, cond):
        res.append((name, bool(cond)))

    def br(agent, prompt):
        return denies("brief", {"tool_input": {"subagent_type": agent, "prompt": prompt}})

    try:
        sc = lambda tool, ti: denies("scope", {"agent_type": "animator", "agent_id": "x", "tool_name": tool,
                                               "tool_input": ti, "cwd": ROOT})
        ok("scope: animator can't edit tools/", sc("Edit", {"file_path": "tools/preflight.py"}))
        ok("scope: animator may write episodes/", not sc("Write", {"file_path": "episodes/ep99_x.py"}))
        ok("scope: agents can't flip a gate", sc("Bash", {"command": "python3 tools/gate.py set ep99 gate1 PASS"}))
        ok("brief: no preflight band refuses", br("packaging", "packaging: ep99 upload sheet"))
        with open(BAND, "w") as f:
            json.dump({"band": "ANY AGENT: <60%", "time": time.time()}, f)
        ok("brief: packaging before gate2 refused", br("packaging", "packaging: ep99 upload sheet"))
        ok("brief: animator build before gate1 refused", br("animator", "animator: ep99 Stage: feasibility first, then build"))
        with open(GATES, "w") as f:
            json.dump({"ep99": {"gate1": {"result": "PASS"}, "gate2": {"result": "FAIL", "owner_ok": "ship it"}}}, f)
        ok("brief: packaging with an owner-ok allowed", not br("packaging", "packaging: ep99 upload sheet"))
        ok("brief: animator build after gate1 allowed",
           not br("animator", "animator: ep99 Stage: feasibility first, then build"))
        ok("brief: 'Stage: feasibility only' leaves budget 5", not br("animator", "animator: ep99 Stage: feasibility "
                                                                     "only") and '"budget": 5' in open(pending_path("animator")).read())
        ok("brief: 7 lines refused", br("story-designer", "\n".join("x" * 7)))
        cnt = lambda: run("count", {"agent_type": "animator", "agent_id": "c1"})
        msgs = [cnt() for _ in range(5)]
        ok("count: stage budget picked up (feasibility 5 -> warn at 4 and 5)",
           "80%" in json.dumps(msgs[3]) and "stage budget (5)" in json.dumps(msgs[4]) and msgs[0] == {})
        sp = lambda aid, text: run("stop", {"agent_type": "packaging", "agent_id": aid, "last_assistant_message": text})
        ok("stop: a return without JSON is sent back once", sp("s1", "done").get("decision") == "block")
        ok("stop: ... and allowed the second time", sp("s1", "done") == {} and os.path.exists(RUNS))
        ap = lambda: run("leadstop", {"hook_event_name": "Stop"})
        note = lambda aid: json.dump({"agent_id": aid, "reasons": ["no json"], "time": time.time()},
                                     open(pending_path("sendback_packaging"), "w"))
        note("s8")
        ok("lead: the next Bash is refused once with the send-back", "'s8'" in json.dumps(run("lead", {
            "tool_name": "Bash", "tool_input": {"command": "ls"}})) and not denies("lead", {
            "tool_name": "Bash", "tool_input": {"command": "ls"}}))
        note("s9")
        ok("leadstop: the Lead is told once to send a failed hand-back back", "'s9'" in ap().get("reason", "")
           and ap() == {})
        lb = lambda cmd: denies("lead", {"tool_name": "Bash", "tool_input": {"command": cmd}})
        ok("lead: git push without git show --stat refused", lb("git push"))
        run("leadpost", {"tool_name": "Bash", "tool_input": {"command": "git show --stat"}})
        ok("lead: git push after git show --stat allowed", not lb("git push origin main"))
        ok("lead: an agent's call is not the Lead's", not denies("lead", {"agent_type": "packaging", "tool_name":
                                                                          "Bash", "tool_input": {"command": "x"}}))
        nav = {"tool_name": "mcp__Claude_Browser__navigate", "tool_input": {"url": "https://studio.youtube.com/x"}}
        run("leadpost", nav)
        fi = {"tool_name": "mcp__Claude_Browser__form_input", "tool_input": {"ref": "r1", "value": "x"}}
        ok("lead: Studio form_input without approval refused", denies("lead", fi))
        with open(APPROVALS, "a") as f:
            f.write(json.dumps({"time": time.time(), "quote": "yes, schedule it"}) + "\n")
        ok("lead: Studio form_input with a fresh approval allowed", not denies("lead", fi))
        for sp in (os.path.join(ROOT, ".claude", "settings.json"),
                   os.path.join(os.path.dirname(ROOT), ".claude", "settings.json")):
            hooks = json.dumps(load_json(sp, {}).get("hooks", {}))
            ok(f"wiring: {os.path.relpath(sp, os.path.dirname(ROOT))} runs brief, lead, leadpost, leadstop, selftest",
               all(f'\\"$f\\" {c} ' in hooks for c in ("brief", "lead", "leadpost", "leadstop",
                                                                         "selftest")))
        for name in TEAM:
            head = open(os.path.join(ROOT, ".claude", "agents", f"{name}.md"), encoding="utf-8").read().split("\n---\n")[0]
            ok(f"wiring: {name} runs scope, count, stop", all(f'"$f" {c}' in head for c in ("scope", "count", "stop")))
    except Exception as e:  # a crash is a failed health check, not a pass
        res.append((f"selftest crashed: {type(e).__name__}: {e}", False))
    finally:
        g.update(keep)
        shutil.rmtree(tmp, ignore_errors=True)
    return res


def cmd_selftest():
    res = selftest()
    bad = [n for n, ok in res if not ok]
    if "--hook" in sys.argv:
        if bad:
            print(f"WARNING: agent_hooks selftest FAIL ({len(bad)}/{len(res)}): {bad[0]}. The harness checks may not "
                  "run: python3 tools/agent_hooks.py selftest, fix before any agent call.")
        return 0
    for n, ok in res:
        print(("PASS " if ok else "FAIL ") + n)
    print(f"SELFTEST {'PASS' if not bad else 'FAIL'}: {len(res) - len(bad)}/{len(res)}")
    return 1 if bad else 0


def take_sendback():
    """The Lead's send-back order for agents whose hand-back FAILED return_check (each note is used once), or None.
    The app runs no hook on SubagentHandback or after an Agent call (M62), so the Lead's next Bash or Agent call (and
    its Stop, where that fires) carries it."""
    notes = []
    for agent in TEAM:
        p = pending_path("sendback_" + agent)
        sb = load_json(p, None)
        if sb:
            os.remove(p)
            if time.time() - sb.get("time", 0) < SENDBACK_MAX_AGE:
                notes.append(f"{agent} '{sb['agent_id']}': " + "; ".join(sb["reasons"]))
    if not notes:
        return None
    return ("agent_hooks: an agent's return FAILS return_check. First send it back once with SendMessage (only these "
            "fixes, no new work), then read its new return (core rule 5); this call was not run: " + " | ".join(notes))


def cmd_leadstop(d):
    if d.get("agent_type") or d.get("stop_hook_active"):
        return 0
    reason = take_sendback()
    return out({"decision": "block", "reason": reason}) if reason else 0


def dispatch(cmd, raw):
    d = json.loads(raw)
    return {"count": cmd_count, "scope": cmd_scope, "stop": cmd_stop, "brief": cmd_brief, "lead": cmd_lead,
            "leadpost": cmd_leadpost, "leadstop": cmd_leadstop}[cmd](d) or 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "selftest":
        return cmd_selftest()
    try:
        return dispatch(cmd, sys.stdin.read())
    except Exception as e:  # fail open: a broken hook must never trap an agent
        print(f"agent_hooks {cmd}: internal error, allowed ({type(e).__name__}: {e})", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
