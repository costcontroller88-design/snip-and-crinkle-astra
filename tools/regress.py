"""Replay the logged mistakes against the checkers (v4.1; reliability research row 9: every fixed mistake is a test).

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
import brief_check  # noqa: E402
import build_agents  # noqa: E402
import preflight  # noqa: E402
import return_check  # noqa: E402

TMP = tempfile.mkdtemp(prefix="snc_regress_")
agent_hooks.STATE = os.path.join(TMP, "state")
agent_hooks.RUNS = os.path.join(TMP, "agent_runs.md")
agent_hooks.BAND = os.path.join(TMP, "band.json")
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
case("M26 7-line brief refused", brief("story-designer", "\n".join(f"line {i}" for i in range(7))))
case("M27 animator brief without feasibility refused", brief("animator", "animator: ep12 build it"))
case("blind brief naming the episode refused", brief("fresh-eyes-reviewer", "Round 2: build/blind/ep12_cut.mp4"))
case("neutral blind brief allowed", not brief("fresh-eyes-reviewer", "Round 2: review build/blind/v_r2.mp4"))
case("a good animator brief allowed", not brief("animator", "animator: ep12 Stage: feasibility first, then build"))

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
case("every stop writes a run row", sum(1 for _ in open(agent_hooks.RUNS)) >= 4 + 4)

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

fails = [r for r in results if not r[1]]
for cid, ok, note in results:
    if not ok or "-v" in sys.argv:
        print(("PASS " if ok else "FAIL ") + cid, note)
print(f"REGRESS {'PASS' if not fails else 'FAIL'}: {len(results) - len(fails)}/{len(results)} cases")
sys.exit(1 if fails else 0)
