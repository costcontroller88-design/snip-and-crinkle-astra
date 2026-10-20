"""Replay the logged mistakes against the checkers (v4.1, v4.2; reliability research row 9: every fixed mistake is a test).

    python3 tools/regress.py        (exit 1 if any case fails; runs from the pre-commit hook on every commit:
                                     the checkers also read reviews/ and state/, audit F3)

Each case names the mistake-log row it guards. A case passes when the checker still catches the bad input AND
still lets the good input through. No model calls, no network; scratch files go to a temp folder, never live files
(M21). Add a case whenever a mistake-log row is APPLIED as a script.
"""
import contextlib
import io
import json
import copy
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
gate.EPISODES = os.path.join(TMP, "episodes")  # M77 gate rule reads rough scripts: a scratch folder, never live ones
os.makedirs(gate.EPISODES)
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


SCRATCH_ROOT = os.path.join(TMP, "root")   # cmd_brief reads <ROOT>/reviews/<ep>_plan.md: a scratch root, never the
os.makedirs(os.path.join(SCRATCH_ROOT, "reviews"))   # live plans (audit F1, 18 Oct: a real ep12 plan turned 2 cases red)


def brief(agent, prompt):
    live, agent_hooks.ROOT = agent_hooks.ROOT, SCRATCH_ROOT
    try:
        return denied(hook(agent_hooks.cmd_brief, {"tool_input": {"subagent_type": agent, "prompt": prompt}}))
    finally:
        agent_hooks.ROOT = live


pipeline_tests = subprocess.run([sys.executable, os.path.join(TOOLS, "test_pipeline_check.py")],
                                capture_output=True, text=True)
case("ASTRA pipeline evidence bindings and prerequisite checks", pipeline_tests.returncode == 0,
     pipeline_tests.stdout + pipeline_tests.stderr if pipeline_tests.returncode else "")

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

# ---- M67/M79: the hook assigns five calls to feasibility only, never production.
for request in ("Measure + storyboard", "Return measurements and a storyboard", "Fix the code",
                "Edit episodes/ep99.py", "Render a storyboard", "Code-fix round", "Do not edit; then build",
                "Measure estimates and then build"):
    case("M67/M79 feasibility-only rejects: " + request,
         brief_check.check("animator: ep99\nStage: feasibility only\n" + request))
for request in ("Measure estimates and return numbers", "Read the existing storyboard; report the render time",
                "No code edits; do not build or render", "Inspect the build and check the render"):
    case("M67/M79 feasibility-only allows: " + request,
         not brief_check.check("animator: ep99\nStage: feasibility only\n" + request))
case("M67 measure + storyboard stage remains valid",
     not brief_check.check("animator: ep99\nStage: measure + storyboard (feasibility first)\nRender a storyboard"))
case("M79 explicit build stage remains valid without open estimates",
     not brief_check.check("animator: ep99\nStage: feasibility first, then build\nFix the code"))
band("ANY AGENT: <60%")
live_root, agent_hooks.ROOT = agent_hooks.ROOT, SCRATCH_ROOT
try:
    rejected = hook(agent_hooks.cmd_brief, {"tool_input": {"subagent_type": "animator",
                    "prompt": "Stage: feasibility only\nRender a storyboard"}})
    accepted = hook(agent_hooks.cmd_brief, {"tool_input": {"subagent_type": "animator",
                    "prompt": "Stage: measure + storyboard (feasibility first)\nRender a storyboard"}})
    case("M67/M79 brief hook rejects for the intended reason and accepts the corrected stage",
         denied(rejected) and "M67/M79" in json.dumps(rejected) and not denied(accepted))
finally:
    agent_hooks.ROOT = live_root
    os.unlink(agent_hooks.BAND)

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
with open(os.path.join(SCRATCH_ROOT, "reviews", "ep98_plan.md"), "w") as f, open(plan) as src:
    f.write(src.read())
with contextlib.redirect_stdout(io.StringIO()):
    gate.main(["set", "ep98", "gate1", "PASS", "--evidence", plan, "--file", agent_hooks.GATES])
case("F1 the hook still reads the episode's plan: open estimates refuse a build",
     brief("animator", "animator: ep98 Stage: feasibility first, then build"))

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
wire_parent = os.path.join(TMP, "wiring")
wire_root = os.path.join(wire_parent, "project")
os.makedirs(os.path.join(wire_root, ".claude"))
wire_local = os.path.join(wire_root, ".claude", "settings.json")
wire_outer = os.path.join(wire_parent, ".claude", "settings.json")
with open(os.path.join(ROOT, ".claude", "settings.json")) as f:
    wire_good = f.read()
with open(wire_local, "w") as f:
    f.write(wire_good)
case("ASTRA standalone wiring needs no parent install",
     len(agent_hooks.wiring_checks(wire_root)) == 1 and all(ok for _, ok in agent_hooks.wiring_checks(wire_root)))
os.makedirs(os.path.dirname(wire_outer))
os.symlink(wire_local, wire_outer)
case("ASTRA installed parent wiring is checked",
     len(agent_hooks.wiring_checks(wire_root)) == 2 and all(ok for _, ok in agent_hooks.wiring_checks(wire_root)))
os.unlink(wire_outer)
os.symlink(os.path.join(wire_root, "missing.json"), wire_outer)
case("ASTRA broken parent symlink fails", not all(ok for _, ok in agent_hooks.wiring_checks(wire_root)))
os.unlink(wire_outer)
with open(wire_outer, "w") as f:
    f.write('{}')
case("ASTRA present parent without hooks fails", not all(ok for _, ok in agent_hooks.wiring_checks(wire_root)))
os.unlink(wire_outer)
os.unlink(wire_local)
case("ASTRA missing project config fails", not all(ok for _, ok in agent_hooks.wiring_checks(wire_root)))
with open(wire_local, "w") as f:
    f.write(wire_good.replace('leadpost', 'missing_command'))
case("ASTRA missing project hook fails", not all(ok for _, ok in agent_hooks.wiring_checks(wire_root)))
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
tr5 = os.path.join(TMP, "agent-h1.jsonl")
with open(tr5, "w") as f:
    f.write(json.dumps({"message": {"role": "assistant", "content": [{"type": "tool_use", "id": "h", "name":
            "SubagentHandback", "input": {"message": "All done!"}}]}}) + "\n")
case("M62 after a hand-back the stop hook doesn't 'send back' (the run has ended)", stop("h1", "", tr5) == {})


def leadstop(lead=True, active=False):
    d = {"hook_event_name": "Stop", "stop_hook_active": active}
    if not lead:
        d["agent_type"] = "story-designer"
    return hook(agent_hooks.cmd_leadstop, d)


case("M62 ... the Lead's turn can't end until it sends that agent back once (SendMessage)",
     "'h1'" in leadstop().get("reason", "") and leadstop() == {})
case("M62 a passing hand-back leaves the Lead nothing to do", stop("h2", "", tr4) == {} and leadstop() == {})
stop("h3", "", tr5)
case("M62 the send-back note is for the Lead only, and never loops",
     leadstop(lead=False) == {} and leadstop(active=True) == {} and leadstop().get("decision") == "block"
     and leadstop() == {})
stop("h4", "", tr5)
case("M62 the Lead's next Bash is refused once with the send-back, then runs",
     lead("Bash", {"command": "ls"}) and not lead("Bash", {"command": "ls"}))
stop("h5", "", tr5)
case("M62 ... or its next Agent call", brief("story-designer", "story-designer: ep12 plan") and
     not brief("story-designer", "story-designer: ep12 plan"))
case("every stop writes a run row", sum(1 for _ in open(agent_hooks.RUNS)) >= 4 + 9)

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
        case(f"brief hook wired in {os.path.relpath(sp, os.path.dirname(ROOT))}", ok and any(
            "leadstop" in h["command"] for e in s["hooks"]["Stop"] for h in e["hooks"]))
cp = os.path.join(os.path.dirname(ROOT), ".claude", "settings.json")
case("copilot settings.json is a link to the project's", not os.path.exists(cp) or (
    os.path.islink(cp) and os.path.realpath(cp) == os.path.realpath(os.path.join(ROOT, ".claude", "settings.json"))))

# ---- stored-frame stamps (audit F2: a frame folder is reused only with the current code)
sys.path.insert(0, os.path.join(ROOT, "episodes"))
import framestore  # noqa: E402
from PIL import Image  # noqa: E402

fs_dir, fs_script = os.path.join(TMP, "frames"), os.path.join(TMP, "ep99_fs.py")
with open(fs_script, "w") as f:
    f.write("X = 1\n")
with contextlib.redirect_stderr(io.StringIO()):
    framestore.begin(fs_dir, fs_script)
    Image.new("RGB", (4, 4), (9, 9, 9)).save(framestore.path(fs_dir, 7))
    case("F2 a half-finished pass (no stamp) is not used", framestore.load(fs_dir, 7, fs_script) is None)
    framestore.finish(fs_dir, fs_script)
    case("F2 a stamped frame with the same code is used", framestore.load(fs_dir, 7, fs_script) is not None)
    case("F2 a missing drawing is a miss", framestore.load(fs_dir, 8, fs_script) is None)
    with open(fs_script, "w") as f:
        f.write("X = 2\n")
    framestore.code_hash.cache_clear()
    case("F2 a code change makes the folder stale", framestore.load(fs_dir, 7, fs_script) is None)
    framestore.begin(fs_dir, fs_script)
    case("F2 begin() clears the stamp", framestore.stamp_of(fs_dir) is None)
short_files = [os.path.relpath(f, ROOT) for f in
               framestore.hashed_files(os.path.join(ROOT, "episodes", "ep11_short_transform.py"))]
case("F2 the stamp covers the imports (rig2, rig2_pip, props_hand2, hires, acting), not tools/",
     all(f"episodes/{m}.py" in short_files for m in ("rig2", "rig2_pip", "props_hand2", "hires", "acting"))
     and not any(f.startswith("tools/") for f in short_files))

# ---- render log (audit F7: every render leaves one row: time, cost, ffmpeg result, which code)
import acting  # noqa: E402

rl = os.path.join(TMP, "render_log.md")
acting.log_render(fs_script, "land", 4.0, 60, 8, 14.2, 0, fs_script, log=rl)
acting.log_render(fs_script, "vert", 2.0, 30, 8, 5.0, 1, os.path.join(TMP, "none.mp4"), log=rl)
rows = [ln for ln in open(rl).read().splitlines() if ln.startswith("| ") and "ep99_fs.py" in ln]
case("F7 one row per render, header written once", len(rows) == 2 and open(rl).read().count("| When |") == 1)
case("F7 the row has the cost per video second and the code hash",
     "| 14 | 3.55 | ok | " + framestore.code_hash(fs_script)[:12] in rows[0])
case("F7 an ffmpeg failure is logged as FAIL", "FAIL (exit 1)" in rows[1])
case("F7 render_video logs to reviews/, not build/ (git-ignored)",
     acting.RENDER_LOG == os.path.join(ROOT, "reviews", "render_log.md"))

# ---- check_video argument order (audit F11: flags first used to crash with a JSON error)
import check_video  # noqa: E402

case("F11 the path is found after the flags",
     check_video.path_arg(["cv", "--landscape", "--no-loop", "x.mp4"]) == "x.mp4"
     and check_video.path_arg(["cv", "--cuts", "3.0,5.2", "x.mp4", "--dur", "15-30"]) == "x.mp4"
     and check_video.path_arg(["cv", "x.mp4", "--landscape"]) == "x.mp4")
case("F11 no path, or two, is refused (not guessed)",
     check_video.path_arg(["cv", "--landscape"]) is None and check_video.path_arg(["cv", "a.mp4", "b.mp4"]) is None)

# ---- M75, M76, M80, M81: a resumed agent reports its own run; the harness counts the calls since its last hand-back
def handback_tr(name, runs, end_handback=False, final=None):
    """A transcript of runs of n tool calls each, every run but the last ended by a SubagentHandback (a resume);
    `final` is the last run's return text."""
    path, k = os.path.join(TMP, name), 0
    with open(path, "w") as f:
        for i, n in enumerate(runs):
            for _ in range(n):
                k += 1
                f.write(json.dumps({"message": {"role": "assistant", "content": [{"type": "tool_use", "id": f"u{k}",
                        "name": "Bash"}]}}) + "\n")
            if i < len(runs) - 1 or end_handback:
                f.write(json.dumps({"message": {"role": "assistant", "content": [{"type": "tool_use", "id": f"hb{i}",
                        "name": "SubagentHandback", "input": {"message": "x"}}]}}) + "\n")
                f.write(json.dumps({"message": {"role": "user", "content": "The coordinator sent a message while you "
                        "were working:\nnext stage"}}) + "\n")
        if final:
            f.write(json.dumps({"message": {"role": "assistant", "content": [{"type": "text", "text": final}]}}) + "\n")
    return path


rs = handback_tr("agent-r1.jsonl", [24, 7], final=ret(good_ev, calls=8, budget=20))
case("M75 a resumed agent's own count (8 of the harness's 7 this run) is not sent back",
     stop("r1", ret(good_ev, calls=8, budget=20), rs) == {}
     and "| 7 (of 31 in all runs) / 8 / 20 |" in open(agent_hooks.RUNS).read().splitlines()[-1])
r2 = stop("r2", ret(good_ev, calls=4, budget=20), handback_tr("agent-r2.jsonl", [24, 12],
                                                                      final=ret(good_ev, calls=4, budget=20)))
case("M76 a real undercount in the resumed run is still sent back, with the harness's count for this run",
     r2.get("decision") == "block" and "counted 12 calls in this run" in r2.get("reason", ""))
case("M80 a run that only fixes its return (0 calls) counts 0, the hand-back ended run counts its own",
     agent_hooks.transcript_stats(handback_tr("agent-r3.jsonl", [24, 7, 0], end_handback=True))[0] == 0 and
     agent_hooks.transcript_stats(handback_tr("agent-r4.jsonl", [24, 7], end_handback=True))[::3] == (7, 31))

# ---- M73, M74: framing pre-check on the designer's shot rows (tools/framing_check.py; plan_check runs it)
import framing_check  # noqa: E402
import plan_check  # noqa: E402

SZ = framing_check.sizes()


def frow(shot, whole, rest="x"):
    return framing_check.check_row("t", ["t", "1-2", shot, whole, rest], SZ)


case("M73 Snip whole in a 2.0x shot fails on height; at 1.4x passes",
     any("tall" in f for f in frow("C 2.0x", "Snip incl. ears")) and not frow("M 1.4x", "Snip incl. ears, Pip"))
case("M73 a 960 u frame in 787 u of room between the out characters fails",
     any("widest gap" in f for f in frow("C2 2.0x", "ball; Snip, Crinkle wholly out", "Snip x 380, Crinkle x 1653")))
case("M74 Snip's ear past the window edge fails (x 380, window 535); window 606 passes",
     any("clear window" in f for f in frow("C2 2.0x (x 535-1495)", "ball; Snip, Crinkle wholly out",
                                           "Snip x 380, Crinkle x 1850"))
     and not frow("C2 2.0x (x 606-1566)", "ball, Pip at 800; Snip, Crinkle wholly out", "Snip x 380, Crinkle x 1850"))
case("M73 an out character without an x fails (the gap can't be checked)",
     any("no x in the row" in f for f in frow("C2 2.0x", "ball; Snip wholly out")))
case("a window the wrong width for its zoom fails", any("u wide" in f for f in frow("C 2.0x (x 400-1300)", "ball")))
case("crouched characters and parts ('Snip's ears') skip the height check",
     not frow("C 2.0x", "Snip (crouched), Snip's ears, ball"))
case("sizes follow the bible's rig scale",
     framing_check.bible_scales() == {"Snip": 1.15, "Crinkle": 1.2, "Pip": 0.9}
     and framing_check.sizes({"Snip": 2.3})["Snip"][0] == 2 * framing_check.MEASURED["Snip"][1])
shot_plan = ("**Length:** 120 s\n**Lesson beat:** 20-24 s\n\n| # | Time (s) | Shot | Whole in frame | What happens |\n"
             "|---|---|---|---|---|\n| 3 | 9.2-12.8 | C 2.0x | Snip incl. ears and feet | x |\n")
case("M73 plan_check runs the framing check", any("Snip is 748 u tall" in f for f in plan_check.check(shot_plan)))

# ---- M77: the full prop clearance sweep (tools/clearance_check.py) and the gate that waits for it
import clearance_check  # noqa: E402
import numpy as np  # noqa: E402
from PIL import ImageDraw  # noqa: E402

bg = Image.new("RGBA", (200, 100), (255, 255, 255, 255))
ch = Image.new("RGBA", (200, 100), (0, 0, 0, 0))
ImageDraw.Draw(ch).rectangle([50, 20, 80, 90], fill=(200, 0, 0, 255))
img = bg.copy()
ImageDraw.Draw(img).line([(20, 85), (120, 85)], fill=(0, 0, 255, 255), width=3)    # a rope behind the figure
img.alpha_composite(ch)
ImageDraw.Draw(img).rectangle([100, 0, 110, 10], fill=(0, 160, 0, 255))           # a toy drawn over everything
pm = clearance_check.prop_mask(img, bg, [ch])
case("M77 prop pixels = the frame minus the background and the characters' layers",
     pm[85, 30] and pm[85, 110] and pm[5, 105] and not pm[85, 65] and not pm[50, 150] and not pm[50, 65])
body = np.asarray(ch.getchannel("A")) > 160
feet, head = body.copy(), body.copy()
feet[:80] = False
head[36:] = False
hits = clearance_check.sweep_frame(pm, {"xx.feet": feet, "xx.head": head}, 1, 10)
case("M77 a rope across the feet is a contact; a toy 25 u from the head is not",
     [h[0] for h in hits] == ["xx.feet"] and hits[0][1] <= 1)
case("M77 --allow names who.part, for all times or one",
     clearance_check.allowed_at(["sn.paws", "cr.feet@38.8"], 38.8) == {"sn.paws", "cr.feet"}
     and clearance_check.allowed_at(["cr.feet@38.8"], 36.6) == set()
     and clearance_check.sweep_frame(pm, {"xx.feet": feet}, 1, 10, {"xx.feet"})[0][3])
ST = os.path.join(TMP, "clearance.json")
for nm in ("ep97_rough.py", "ep97_rough_r2.py"):
    with open(os.path.join(gate.EPISODES, nm), "w") as f:
        f.write("X = 1\n")
rough = os.path.join(gate.EPISODES, "ep97_rough_r2.py")
g97 = lambda *extra: run_quiet(gate.main, ["set", "ep97", "gate1", "PASS", "--evidence", plan, "--file", G,
                                           "--clearance", ST, *extra])
case("M77 gate1 PASS refused while the newest rough script has no clearance sweep",
     clearance_check.newest_rough("ep97", gate.EPISODES) == rough and g97() == 1)
clearance_check.stamp(os.path.join(gate.EPISODES, "ep97_rough.py"), {"result": "PASS", "times": [1.0],
                      "not_checked": [], "hits": []}, 10, [], ST)
case("M77 ... a sweep of an older rough script doesn't count", g97() == 1)
clearance_check.stamp(rough, {"result": "FAIL", "times": [1.0], "not_checked": [],
                              "hits": [{"time": 1.0, "part": "cr.feet", "allowed": False}]}, 10, [], ST)
case("M77 ... a FAIL sweep doesn't count", g97() == 1)
clearance_check.stamp(rough, {"result": "PASS", "times": [1.0], "not_checked": [], "hits": []}, 10, [], ST)
case("M77 ... a PASS sweep of the current code lets gate1 pass", g97() == 0)
with open(rough, "a") as f:
    f.write("Y = 2\n")
case("M77 ... a code change after the sweep refuses gate1b again",
     run_quiet(gate.main, ["set", "ep97", "gate1b", "PASS", "--evidence", plan, "--file", G, "--clearance", ST]) == 1)
case("M77 an owner-ok still records (M44)", g97("--owner-ok", "go ahead, I checked it") == 0)

# ---- stage kit (docs/stage_kit_proposal.md): the menu refuses the framing and clearance mistakes up front
sys.path.insert(0, os.path.join(ROOT, "episodes"))
import stage_kit as SK  # noqa: E402


def kit(start, beats=(), shots=(), set_name="playroom", view="land"):
    t = SK.Table("ep98", set_name, view)
    t.start = dict(start)
    t.beats, t.shots = list(beats), list(shots)
    try:
        return SK.Sim(t).problems()
    except SK.Refused as e:
        return [str(e)]


ST3 = {"Snip": ("B", "right"), "Crinkle": ("D", "left"), "Pip": ("WL", "right")}
case("KIT presets reproduce the proposal's table (ML holds Snip at A-C, cuts her at D; MR cuts Crinkle at A)",
     SK.status("Snip", SK.MARKS["C"], SK.PRESETS["ML"][2]) == "in"
     and SK.status("Snip", SK.MARKS["D"], SK.PRESETS["ML"][2]) == "cut"
     and SK.status("Crinkle", SK.MARKS["A"], SK.PRESETS["MR"][2]) == "cut"
     and SK.status("Pip", SK.MARKS["WR"], SK.PRESETS["W"][2]) == "in"
     and SK.status("Snip", SK.MARKS["WR"], SK.PRESETS["W"][2]) == "cut")
case("KIT M73 a 2.0x shot never holds Snip whole: CL with Snip on stage is refused; Pip alone in CL passes",
     any("Snip" in p and "cut" in p for p in kit({"Snip": ("A", "right")}, shots=[(0, 2, "CL")]))
     and not kit({"Pip": ("A", "right"), "Snip": ("E", "left")}, shots=[(0, 2, "CL")]))
case("KIT spacing: Snip on B and Crinkle on C (one mark apart) is refused; B and D pass",
     any("apart" in p for p in kit({"Snip": ("B", "right"), "Crinkle": ("C", "left")}))
     and not kit(ST3, shots=[(0, 2, "W")]))
case("KIT M34 a walk that crosses a medium window's edge mid-shot is refused (cut on the way)",
     any("cut" in p for p in kit({"Snip": ("A", "right")}, [(0.5, 4.0, "Snip", "walk_to", "E")], [(0, 4, "ML")]))
     and not kit({"Snip": ("A", "right")}, [(0.5, 2.5, "Snip", "walk_to", "C")], [(0, 3, "ML")]))
case("KIT a walk through another character is refused",
     any("apart" in p for p in kit(ST3, [(0.5, 3.0, "Snip", "walk_to", "E")])))
case("KIT hop: Snip may hop in W, not in ML (no headroom)",
     not kit(ST3, [(0.5, 1.3, "Snip", "hop", "")], [(0, 2, "W")])
     and any("hopping" in p for p in kit(ST3, [(0.5, 1.3, "Snip", "hop", "")], [(0, 2, "ML")])))
HO = {"Snip": ("C.L", "right"), "Crinkle": ("C.R", "left"), "block": ("Snip", "")}
case("KIT hand_over only on a facing pair: C.L/C.R passes; B/D is refused",
     not kit(HO, [(0.5, 1.7, "Snip", "hand_over", "block Crinkle")])
     and any("pair" in p for p in kit({"Snip": ("B", "right"), "Crinkle": ("D", "left"), "block": ("Snip", "")},
                                      [(0.5, 1.7, "Snip", "hand_over", "block Crinkle")])))
case("KIT a prop put down on someone's feet is refused",
     any("feet" in p for p in kit({"Snip": ("B", "right"), "Crinkle": ("D", "left"), "block": ("Snip", "")},
                                  [(0.5, 1.5, "Snip", "put_down", "D")])))
case("KIT react is held >= 1.0 s; an unknown move or emote is refused",
     any("1.0 s" in p for p in kit(ST3, [(0.5, 1.0, "Snip", "react", "sad")]))
     and any("react takes" in p for p in kit(ST3, [(0.5, 1.6, "Snip", "react", "angry")])))
_tv = SK.Table("ep98", "porch", "vert")
_tv.start = {"Snip": ("C.L", "right"), "Crinkle": ("C.R", "left"), "block": ("Snip", "")}
_tv.shots = [(0, 2, "VW@C")]
_rows = SK.Sim(_tv).framing_rows()
_md = "| # | Time (s) | Shot | Whole in frame | At | Preset |\n|---|---|---|---|---|---|\n" + "\n".join(_rows)
case("KIT the rows stage.py writes pass framing_check, vertical windows included",
     not kit(_tv.start, shots=_tv.shots, set_name="porch", view="vert") and _rows and not framing_check.check(_md))
_lan = {"Snip": ("A.L", "right"), "Crinkle": ("A.R", "left"), "marker": ("Snip", ""), "lantern": ("D", "")}
case("KIT trial bugs: a floor prop (the lantern) leaves hand-over pairs alone; a bespoke row never exempts framing",
     not kit(_lan, [(0.5, 1.7, "Snip", "hand_over", "marker Crinkle")], set_name="porch", view="vert")
     and any("cut" in p for p in kit(ST3, [(0.5, 2.0, "Snip", "bespoke", "x")], [(0, 2, "ML")])))
case("KIT framing_check knows vertical: Crinkle whole in VC 2.0x (540 u wide) fails",
     any("not inside" in f or "wide" in f for f in
         frow("VC@C 2x x 690-1230 y 702-1662", "Crinkle", "Crinkle x 960")))

# ---- stage kit v2: the kit works staging out (intent rows, depth, lean/crouch, take, gags, group frames)
def kitv2(start, beats=(), shots=()):
    t = SK.Table("ep98", "porch", "vert")
    t.start = dict(start)
    t.beats, t.shots = list(beats), list(shots)
    return t


def kitp_land(t, beats):
    t = copy.deepcopy(t)
    t.beats = list(beats)
    return kitp(t)


def kitp(t):
    try:
        return SK.Sim(t).problems()
    except SK.Refused as e:
        return [str(e)]


LANT = {"Snip": ("x:400", "right"), "Crinkle": ("x:1300", "left"), "marker": ("Snip", ""),
        "lantern": ("C", "")}
try:
    _t, _rows, _shot = SK.solve(kitv2(LANT), 0.5, 1.9, "Snip", "draw", "lantern.eye_l")
    _ok = _rows[0][3] == "walk_to" and _rows[-1][3] == "draw" and _shot and not kitp(_t)
except SK.Refused as e:
    _ok, _rows, _t = False, [], kitv2(LANT)
case("KIT v2 intent row: 'Snip draw lantern.eye_l' gets a stand x (walk), the draw and a legal frame", _ok, str(_rows)[:120])
case("KIT v2 depth: feet may hide behind the lantern while the paw works; an idle Pip with her head by it is refused",
     not kitp(kitv2(LANT, [(0.5, 1.4, "Snip", "walk_to", "x:720"), (1.4, 2.4, "Snip", "draw", "lantern.eye_l")]))
     and 720 + SK.geom("Snip", 1)["feet"][1] > 840 + 10
     and any("Pip's head" in p or "Pip's resting" in p for p in kitp(kitv2({"Pip": ("x:800", "right"), "lantern": ("C", "")}))))
PASS = {"Pip": ("C.L", "right"), "Snip": ("x:300", "right"), "Crinkle": ("x:1300", "left"), "marker": ("Pip", ""),
        "lantern": ("C", "")}
_pp = SK.Table("ep98", "playroom", "land")
_pp.start = {"Pip": ("B", "right"), "Crinkle": ("x:1060", "left"), "marker": ("Pip", "")}
_pp.shots = [(0, 3.2, "W")]
_far = copy.deepcopy(_pp)
_far.start["Crinkle"] = ("x:1500", "left")
try:
    _, _pr, _ = SK.solve(_pp, 0.9, 2.1, "Pip", "hand_over", "marker Crinkle", add_shot=False)
except SK.Refused as e:
    _pr = [("", "", "", "", str(e))]
case("KIT v2 Crinkle-Pip pass: the solver finds the lean/crouch pass Pip -> Crinkle; with Crinkle 860 u off it's refused",
     "hand_over" in _pr[-1][3] and any("pair" in p for p in kitp_land(_far, [(0.9, 2.1, "Pip", "hand_over", "marker Crinkle")])),
     str(_pr)[:160])
TK = {"Pip": ("x:300", "right"), "Snip": ("x:712", "right"), "Crinkle": ("x:1300", "left"), "marker": ("Snip", ""),
      "lantern": ("C", "")}
_d = [(0.0, 1.2, "Snip", "draw", "lantern.eye_l 0-0.67")]
case("KIT v2 take: Crinkle pinches the marker from Snip's paw at the C after walking in; from x 1300 it's out of reach",
     not kitp(kitv2(TK, _d + [(1.2, 1.8, "Crinkle", "walk_to", "x:1149"), (1.8, 2.8, "Crinkle", "take", "marker")]))
     and any("reach" in p for p in kitp(kitv2(TK, _d + [(1.2, 2.8, "Crinkle", "take", "marker")]))))
G3 = {"Snip": ("B", "right"), "Crinkle": ("D", "left"), "Pip": ("WL", "right")}
_spin = SK.Table("ep98", "playroom", "land")
_spin.start = dict(G3)
_spin.beats = [(0.5, 1.3, "Snip", "spin", "left")]
case("KIT v2 gags: sway, wiggle up, spin, bow pass in W; spin ends facing the other way; only Pip puffs",
     all(not kit(G3, [(0.5, 1.7, "Snip", m, a)], [(0, 2, "W")]) for m, a in
         (("sway", ""), ("wiggle", "up"), ("bow", ""))) and not kit(G3, [(0.5, 1.3, "Snip", "spin", "left")], [(0, 2, "W")])
     and SK.Sim(_spin).facing("Snip", 1.4) < 0 and any("only Pip" in p for p in kit(G3, [(0.5, 1.7, "Snip", "puff", "")]))
     and not kit(G3, [(0.5, 1.7, "Pip", "puff", "")], [(0, 2, "W")]))
_gt = kitv2({"Snip": ("C.L", "right"), "Crinkle": ("C.R", "left")})
_gp = SK.Sim(_gt).group_presets(0, 2)
_gw = next(n for n in _gp if n.startswith("VW"))
case("KIT v2 vertical frames centred on the group: VW@x<centre> holds Snip and Crinkle at C.L / C.R whole",
     SK.preset("VM@x960")[2][0] == 960 - 1080 / 1.38 / 2 and not SK.Sim(_gt).shot_problems(0, 2, _gw)
     and all(SK.status_ext(*SK.Sim(_gt).extent(w, 1.0), SK.preset(_gw)[2]) == "in" for w in ("Snip", "Crinkle")))
_busy = kitv2(LANT)
try:
    SK.solve(_busy, 0.0, 0.5, "Snip", "draw", "lantern.eye_l", add_shot=False)
    _msg = ""
except SK.Refused as e:
    _msg = str(e)
case("KIT v2 no solution: the refusal lists the nearest rows that work (later, or the partner moving)",
     "nearest that work" in _msg, _msg[-160:])

# ---- M82: required storyboard samples and the delivered sheet agree (temporary fixtures only).
storyboard_tests = subprocess.run([sys.executable, os.path.join(TOOLS, "test_storyboard_check.py")],
                                 capture_output=True, text=True)
case("M82 storyboard coverage and integrity tests", storyboard_tests.returncode == 0,
     storyboard_tests.stdout + storyboard_tests.stderr if storyboard_tests.returncode else "")

fails = [r for r in results if not r[1]]
for cid, ok, note in results:
    if not ok or "-v" in sys.argv:
        print(("PASS " if ok else "FAIL ") + cid, note)
print(f"REGRESS {'PASS' if not fails else 'FAIL'}: {len(results) - len(fails)}/{len(results)} cases")
sys.exit(1 if fails else 0)
