"""Replay the logged mistakes against the checkers (v4.1, v4.2; reliability research row 9: every fixed mistake is a test).

    python3 tools/regress.py        (exit 1 if any case fails; runs from the pre-commit hook when tools/,
                                     MASTER_PROMPT.md or .claude/ change)

Each case names the mistake-log row it guards. A case passes when the checker still catches the bad input AND
still lets the good input through. No model calls, no network; scratch files go to a temp folder, never live files
(M21). Add a case whenever a mistake-log row is APPLIED as a script.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import agent_hooks  # noqa: E402
import approve  # noqa: E402
import brief_check  # noqa: E402
import build_agents  # noqa: E402
import gate  # noqa: E402
import preflight  # noqa: E402
import return_check  # noqa: E402

TMP = tempfile.mkdtemp(prefix="snc_regress_")
agent_hooks.STATE = os.path.join(TMP, "state")
agent_hooks.RUNS = os.path.join(TMP, "agent_runs.md")
agent_hooks.BAND = os.path.join(TMP, "band.json")
agent_hooks.GATES = os.path.join(TMP, "gates.json")
agent_hooks.APPROVALS = os.path.join(TMP, "approvals.jsonl")
results = []


def case(cid, ok, note=""):
    results.append((cid, bool(ok), note))


def ret(checks, calls=10, budget=20, files=None, fence=True):
    j = json.dumps({"agent": "animator", "verdict": "PASS", "tool_calls": calls, "budget": budget, "checks": checks,
                    "files": files or [], "not_done": []})
    return f"Done.\n```json\n{j}\n```" if fence else j


def hook(fn, d):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(d)
    s = buf.getvalue().strip()
    return json.loads(s) if s else {}


def denied(r):
    return (r.get("hookSpecificOutput") or {}).get("permissionDecision") == "deny"


def scope(agent, tool, ti):
    return denied(hook(agent_hooks.cmd_scope, {"agent_type": agent, "agent_id": "t", "tool_name": tool,
                                               "tool_input": ti, "cwd": ROOT}))


def band(text, age=0):
    import time
    with open(agent_hooks.BAND, "w") as f:
        json.dump({"band": text, "time": time.time() - age}, f)


def brief(agent, prompt):
    return denied(hook(agent_hooks.cmd_brief, {"tool_input": {"subagent_type": agent, "prompt": prompt}}))


# ---- return_check (M38, M50, M56, evidence rule)
good_ev = [{"name": "loudness", "evidence": "-16.2 LUFS"}, {"name": "file", "evidence": "MASTER_PROMPT.md and 3 s"}]
case("M56 fragment without its fence fails", return_check.check(ret(good_ev, fence=False)))
case("M38/M50 over budget fails", return_check.check(ret(good_ev, calls=32, budget=30)))
case("evidence 'looks fine' fails", return_check.check(ret([{"name": "x", "evidence": "looks fine"}])))
case("cited file that doesn't exist fails", return_check.check(ret([{"name": "x", "evidence": "build/none/x_9.png"}])))
case("M61 an absolute path with spaces in the evidence is found",
     not return_check.check(ret([{"name": "x", "evidence": os.path.join(return_check.ROOT, "MASTER_PROMPT.md") + " (Write ok)"}])))
case("an honest return passes", not return_check.check(ret(good_ev, files=["MASTER_PROMPT.md"])))

# ---- brief_check (M26, M27, M30, M39, M46, M52)
case("M27 animator brief without 'feasibility first' fails", brief_check.check("animator: ep12 build the episode"))
case("M26/M30 a budget in the brief fails", brief_check.check("animator: ep12 feasibility first, <=14 calls"))
case("M46/M52 packaging and general-purpose briefs pass",
     not brief_check.check("packaging: ep12 upload sheet") and not brief_check.check("general-purpose: spec, 30 calls"))
plan = os.path.join(TMP, "ep99_plan.md")
with open(plan, "w") as f:
    f.write("## Measured checks\n| Check | Need | Measured |\n|---|---|---|\n| lantern gap | 30 | estimate |\n")
case("M39 'then build' with open estimates fails", brief_check.check("animator: ep99 feasibility first, then build", plan))

# ---- blind_guard (M1, M57): exit 2 blocks
def guard(tool, ti):
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "blind_guard.py")], cwd=ROOT, capture_output=True,
                       input=json.dumps({"tool_name": tool, "tool_input": ti, "cwd": ROOT}), text=True)
    return p.returncode


case("M1 reviewer reading a plan is blocked", guard("Read", {"file_path": "reviews/ep11_plan.md"}) == 2)
case("M1 reviewer Glob from the repo root is blocked", guard("Glob", {"pattern": "**/*.md"}) == 2)
case("M1 reviewer 'cat ../reviews' via Bash is blocked", guard("Bash", {"command": "cat reviews/ep11_safety.md"}) == 2)
case("reviewer may read its own reference",
     guard("Read", {"file_path": "docs/agents/fresh-eyes-reviewer_reference.md"}) == 0)
p = subprocess.run([sys.executable, os.path.join(TOOLS, "blind_guard.py")], input="not json", capture_output=True,
                   text=True)
case("M57 blind_guard fails closed on bad input", p.returncode == 2)

# ---- build_agents (M59) and drift
case("M59 unquoted ': ' in frontmatter is caught", build_agents.yaml_trap("---\ndescription: blind review: titles\n---\n"))
chk = subprocess.run([sys.executable, os.path.join(TOOLS, "build_agents.py"), "--check"], cwd=ROOT, capture_output=True)
case("agent files match Appendix A (build_agents --check)", chk.returncode == 0)

# ---- preflight bands (M8, L1)
case("M8 band at 80% forbids every agent", preflight.forbidden(preflight.band(80, 200), "fresh-eyes-reviewer"))
case("M8 reset <90 min forbids the animator, allows the reviewer",
     preflight.forbidden(preflight.band(55, 60), "animator") and
     not preflight.forbidden(preflight.band(55, 60), "fresh-eyes-reviewer"))

# ---- agent_hooks scope (role separation, research row 3)
case("animator may not edit a checker", scope("animator", "Edit", {"file_path": "tools/handover_check.py"}))
case("animator may write episode code", not scope("animator", "Write", {"file_path": "episodes/ep99_x.py"}))
case("animator may not copy into Videos/ (core rule 7)", scope("animator", "Bash", {"command": "cp output/a.mp4 Videos/"}))
case("animator may not read blind reviews", scope("animator", "Read", {"file_path": "reviews/ep11_blind_r3.md"}))
case("animator may not sed -i the master prompt",
     scope("animator", "Bash", {"command": "sed -i '' 's/a/b/' MASTER_PROMPT.md"}))
case("packaging may write its upload text", not scope("packaging", "Write", {"file_path": "Videos/x_upload_text.txt"}))
case("safety-checker may not edit episodes", scope("safety-checker", "Edit", {"file_path": "episodes/ep11_x.py"}))
case("no agent pushes", scope("story-designer", "Bash", {"command": "git add -A && git push"}))
case("no agent writes the mistake log", scope("story-designer", "Write", {"file_path": "reviews/mistake_log.md"}))
case("a check piped to build/ is allowed",
     not scope("story-designer", "Bash", {"command": "python3 tools/plan_check.py reviews/ep12_plan.md > build/pc.txt"}))
case("growth-analyst can't type or fill forms in Studio",
     scope("growth-analyst", "mcp__Claude_Browser__form_input", {"ref": "r1", "value": "x"}) and
     scope("growth-analyst", "mcp__Claude_Browser__computer", {"action": "type", "text": "x"}))
case("growth-analyst may take a screenshot",
     not scope("growth-analyst", "mcp__Claude_Browser__computer", {"action": "screenshot"}))
case("the Lead itself is never scoped", not scope("", "Edit", {"file_path": "tools/preflight.py"}))

# ---- agent_hooks brief (core rules 1 and 4)
if os.path.exists(agent_hooks.BAND):
    os.remove(agent_hooks.BAND)
case("L1/M8 no preflight: agent call refused", brief("packaging", "packaging: ep12"))
band("SMALL AGENTS ONLY: 60-75% (reviewer, safety, designer, packaging)")
case("L1/M8 band forbids the animator", brief("animator", "animator: ep12 feasibility first"))
band("ANY AGENT: <60%")
case("a stale preflight (3 h) is refused", (band("ANY AGENT: <60%", age=3 * 3600), brief("packaging", "p: ep12"))[1])
band("ANY AGENT: <60%")
with contextlib.redirect_stdout(io.StringIO()):
    gate.main(["set", "ep12", "gate1", "PASS", "--evidence", plan, "--file", agent_hooks.GATES])
case("M26 7-line brief refused", brief("story-designer", "\n".join(f"line {i}" for i in range(7))))
case("M27 animator brief without feasibility refused", brief("animator", "animator: ep12 build it"))
case("blind brief naming the episode refused", brief("fresh-eyes-reviewer", "Round 2: build/blind/ep12_cut.mp4"))
case("neutral blind brief allowed", not brief("fresh-eyes-reviewer", "Round 2: review build/blind/v_r2.mp4"))
case("a good animator brief allowed", not brief("animator", "animator: ep12 Stage: feasibility first, then build"))

# ---- v4.2 gate tracker (tools/gate.py; review: no gate-order enforcement; M44 owner override)
G = agent_hooks.GATES


def run_quiet(fn, argv):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(argv)


case("gate.py refuses a result without evidence", run_quiet(gate.main, ["set", "ep13", "gate2", "PASS", "--file", G]) == 1
     and "ep13" not in json.load(open(G)))
case("gate.py refuses evidence that doesn't exist",
     run_quiet(gate.main, ["set", "ep13", "gate2", "PASS", "--evidence", "reviews/none_x.md", "--file", G]) == 1)
case("gate.py records PASS with date and evidence",
     run_quiet(gate.main, ["set", "ep13", "gate1", "PASS", "--evidence", plan, "--file", G]) == 0
     and json.load(open(G))["ep13"]["gate1"]["result"] == "PASS" and json.load(open(G))["ep13"]["gate1"]["date"])
case("gate.py 'none' clears a gate", run_quiet(gate.main, ["set", "ep13", "gate1", "none", "--file", G]) == 0
     and "gate1" not in json.load(open(G))["ep13"])
case("animator build before gate1 PASS refused", brief("animator", "animator: ep13 Stage: feasibility first, then build"))
case("animator feasibility-only before gate1 allowed (no build yet)",
     not brief("animator", "animator: ep13 Stage: feasibility only"))
case("'Episode 13' in words is the same episode", brief("animator", "animator: Episode 13 feasibility first, then build"))
case("packaging before gate2 PASS refused", brief("packaging", "packaging: ep12 upload sheet"))
run_quiet(gate.main, ["set", "ep12", "gate2", "FAIL", "--evidence", plan, "--owner-ok", "it's fine, go ahead", "--file", G])
case("M44 packaging after an owner-ok on gate2 allowed",
     not brief("packaging", "packaging: ep12 upload sheet") and json.load(open(G))["ep12"]["gate2"]["owner_ok"])
run_quiet(gate.main, ["set", "ep13", "gate2", "PASS", "--evidence", plan, "--file", G])
case("packaging after gate2 PASS allowed", not brief("packaging", "packaging: ep13 upload sheet"))
case("an agent may not flip a gate or record an approval",
     scope("animator", "Bash", {"command": "python3 tools/gate.py set ep13 gate1 PASS --evidence x"}) and
     scope("packaging", "Bash", {"command": "python3 tools/approve.py 'yes'"}) and
     scope("story-designer", "Write", {"file_path": "state/gates.json"}))
case("an agent may read the gates", not scope("packaging", "Bash", {"command": "python3 tools/gate.py show ep13"}))


# ---- v4.2 stage budgets (review: stage budgets not enforced)
def pending(agent):
    try:
        return json.load(open(agent_hooks.pending_path(agent)))
    except OSError:
        return {}


def counts(agent, aid, n):
    return [json.dumps(hook(agent_hooks.cmd_count, {"agent_type": agent, "agent_id": aid})) for _ in range(n)]


brief("animator", "animator: ep12 Stage: feasibility only")
case("'Stage: feasibility only' leaves the animator budget 5", pending("animator").get("budget") == 5)
c = counts("animator", "st1", 5)
case("count warns at 80% (4) and 100% (5) of the stage budget",
     "80% of your 'feasibility'" in c[3] and "stage budget (5)" in c[4] and c[2] == "{}")
case("the pending stage is used once", not os.path.exists(agent_hooks.pending_path("animator")))
brief("animator", "animator: ep12 Stage: feasibility first, then build")
case("'feasibility first, then build' is the build budget 60", pending("animator").get("budget") == 60)
brief("story-designer", "story-designer: ep12 Stage: fix mode r2")
case("story-designer fix mode is 12", pending("story-designer").get("budget") == 12)
brief("safety-checker", "safety-checker: ep12 Stage: gate 3")
case("safety-checker gate 3 is 18", pending("safety-checker").get("budget") == 18)
os.remove(agent_hooks.pending_path("safety-checker"))
brief("safety-checker", "safety-checker: ep12 gate 1")
case("no 'Stage:' line, no stage budget", pending("safety-checker") == {})
with open(agent_hooks.pending_path("story-designer"), "w") as f:
    json.dump({"stage": "fix", "budget": 12, "time": 0}, f)
c = counts("story-designer", "st2", 10)
case("a stale pending stage (>10 min) is ignored", "'fix'" not in "".join(c) and "5 tool calls" in c[4])


# ---- v4.2 Lead guards (review: the Lead's own risky actions unchecked; core rules 8, 11)
def lead(tool, ti, agent=""):
    d = {"tool_name": tool, "tool_input": ti}
    if agent:
        d["agent_type"] = agent
    return denied(hook(agent_hooks.cmd_lead, d))


def leadpost(tool, ti, resp=""):
    hook(agent_hooks.cmd_leadpost, {"tool_name": tool, "tool_input": ti, "tool_response": resp})


def lead_state(**kw):
    st = agent_hooks.load_state(agent_hooks.LEAD_STATE)
    st.update(kw)
    agent_hooks.save_state(agent_hooks.LEAD_STATE, st)


PUSH = "git " + "push"
case("M47 Lead push without git show --stat refused", lead("Bash", {"command": PUSH + " origin main"}))
case("words in a heredoc are not a push", not lead("Bash", {"command": "python3 - <<'EOF'\nx = '" + PUSH + "'\nEOF"}))
leadpost("Bash", {"command": "cd x && git show --stat HEAD"})
case("Lead push within 10 min of git show --stat allowed", not lead("Bash", {"command": PUSH}))
lead_state(show_time=agent_hooks.time.time() - 11 * 60)
case("a git show --stat 11 min old is stale", lead("Bash", {"command": "cd x && " + PUSH}))
lead_state(show_time=agent_hooks.time.time(), show_head="0000000")
case("a new commit after git show --stat refuses the push", lead("Bash", {"command": PUSH}))
case("an agent's call is not the Lead's (scope hook guards agents)",
     not lead("Bash", {"command": PUSH}, agent="packaging"))
FI = ("mcp__Claude_Browser__form_input", {"ref": "r1", "value": "Title"})
leadpost("mcp__Claude_Browser__navigate", {"url": "https://www.youtube.com/@SnipAndCrinkle"})
case("form_input outside Studio is not guarded", not lead(*FI))
leadpost("mcp__Claude_Browser__navigate", {"url": "https://studio.youtube.com/channel/x/videos"})
case("M49 Studio form_input without the owner's yes refused", lead(*FI))
case("Studio click and type refused, screenshot allowed",
     lead("mcp__Claude_Browser__computer", {"action": "left_click", "coordinate": [1, 1]}) and
     lead("mcp__Claude_Browser__computer", {"action": "type", "text": "x"}) and
     not lead("mcp__Claude_Browser__computer", {"action": "screenshot"}))
leadpost("mcp__Claude_Browser__navigate", {"url": "http://localhost:8000"})
case("a batch that navigates to Studio then types is refused",
     lead("mcp__Claude_Browser__browser_batch", {"actions": [
         {"name": "navigate", "input": {"url": "https://studio.youtube.com/x"}},
         {"name": "computer", "input": {"action": "type", "text": "x"}}]}))
leadpost("mcp__claude-in-chrome__navigate", {"url": "https://youtube.com/upload", "tabId": 7})
case("Chrome's Studio tab is guarded too",
     lead("mcp__claude-in-chrome__form_input", {"ref": "r1", "value": "x", "tabId": 7}))
case("approve.py refuses words without a yes",
     run_quiet(approve.main, ["looks good to me", "--file", agent_hooks.APPROVALS]) == 1)
with open(agent_hooks.APPROVALS, "a") as f:
    f.write(json.dumps({"time": agent_hooks.time.time() - 31 * 60, "quote": "yes"}) + "\n")
case("an approval 31 min old is stale", lead("mcp__claude-in-chrome__form_input", {"ref": "r", "value": "x", "tabId": 7}))
run_quiet(approve.main, ["yes, schedule it for 6 PM", "--file", agent_hooks.APPROVALS])
case("a fresh approve.py record allows the Studio edit",
     not lead("mcp__claude-in-chrome__form_input", {"ref": "r", "value": "x", "tabId": 7}))

# ---- v4.2 health check (agent_hooks.py selftest; SessionStart)
st_res = agent_hooks.selftest()
case("selftest PASS on the live wiring", all(ok for _, ok in st_res), [n for n, ok in st_res if not ok])
keep_st, keep_argv = agent_hooks.selftest, sys.argv
agent_hooks.selftest, sys.argv = (lambda: [("forced", False), ("x", True)]), ["agent_hooks.py", "selftest", "--hook"]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = agent_hooks.cmd_selftest()
agent_hooks.selftest, sys.argv = keep_st, keep_argv
case("SessionStart: a failed selftest prints one warning line, exit 0",
     rc == 0 and buf.getvalue().count("\n") == 1 and buf.getvalue().startswith("WARNING"))


# ---- agent_hooks stop (research rows 1, 6)
def stop(aid, text, transcript=None, active=False):
    d = {"agent_type": "animator", "agent_id": aid, "last_assistant_message": text, "stop_hook_active": active}
    if transcript:
        d["agent_transcript_path"] = transcript
    return hook(agent_hooks.cmd_stop, d)


case("a return without JSON is sent back once", stop("a1", "All done!").get("decision") == "block")
case("... and allowed the second time (no loop)", stop("a1", "All done!") == {})
case("over budget alone is logged, not sent back", stop("a2", ret(good_ev, calls=32, budget=30)) == {})
tr = os.path.join(TMP, "agent-a3.jsonl")
with open(tr, "w") as f:
    for i in range(10):
        f.write(json.dumps({"requestId": f"r{i}", "message": {"role": "assistant", "usage": {"input_tokens": 5,
                "cache_read_input_tokens": 1000 * i, "output_tokens": 50},
                "content": [{"type": "tool_use", "id": f"t{i}"}]}}) + "\n")
case("M38 a tool count 3+ below the harness count is sent back",
     stop("a3", ret(good_ev, calls=5, budget=20), tr).get("decision") == "block")
tr4 = os.path.join(TMP, "agent-a4.jsonl")
with open(tr4, "w") as f:
    f.write(json.dumps({"message": {"role": "assistant", "content": [{"type": "tool_use", "id": "w1", "name": "Write"}]}})
            + "\n" + json.dumps({"message": {"role": "assistant", "content": [{"type": "tool_use", "id": "h1",
            "name": "SubagentHandback", "input": {"message": ret(good_ev, calls=1, budget=15)}}]}}) + "\n")
case("M61 a report delivered by SubagentHandback is read (not 'no final message')",
     stop("a4", "", tr4) == {} and "| 1 / 1 / 15 |" in open(agent_hooks.RUNS).read().splitlines()[-1])
case("every stop writes a run row", sum(1 for _ in open(agent_hooks.RUNS)) >= 4 + 5)

# ---- wiring: each agent file carries its hooks; both settings files carry the brief hook
for name in agent_hooks.TEAM:
    t = open(os.path.join(ROOT, ".claude", "agents", f"{name}.md"), encoding="utf-8").read()
    head = t.split("\n---\n", 1)[0]
    ok = "agent_hooks.py" in head and all(f"\"$f\" {c}" in head for c in ("scope", "count", "stop"))
    if name == "fresh-eyes-reviewer":
        ok = ok and "blind_guard.py" in head
    case(f"{name} frontmatter wires scope, count, stop", ok)
for sp in (os.path.join(ROOT, ".claude", "settings.json"),
           os.path.join(os.path.dirname(ROOT), ".claude", "settings.json")):
    if os.path.exists(sp) or sp.startswith(ROOT):
        try:
            s = json.load(open(sp))
            ok = any("agent_hooks.py" in h["command"] and "brief" in h["command"]
                     for e in s["hooks"]["PreToolUse"] for h in e["hooks"])
        except (OSError, ValueError, KeyError):
            ok = False
        case(f"brief hook wired in {os.path.relpath(sp, os.path.dirname(ROOT))}", ok)
cp = os.path.join(os.path.dirname(ROOT), ".claude", "settings.json")
case("copilot settings.json is a link to the project's", not os.path.exists(cp) or (
    os.path.islink(cp) and os.path.realpath(cp) == os.path.realpath(os.path.join(ROOT, ".claude", "settings.json"))))

fails = [r for r in results if not r[1]]
for cid, ok, note in results:
    if not ok or "-v" in sys.argv:
        print(("PASS " if ok else "FAIL ") + cid, note)
print(f"REGRESS {'PASS' if not fails else 'FAIL'}: {len(results) - len(fails)}/{len(results)} cases")
sys.exit(1 if fails else 0)
