# Engineering audit, Phase 0 (+ safe parts of Phases 1-6), 18 Oct 2026

Brief: `Snip_and_Crinkle_Optimized_Master_Prompt.md`. Read-only; no source file changed. Labels: VERIFIED / INFERRED /
UNVERIFIED / BLOCKED.

## D. Working tree at start (VERIFIED)
- Root: `/Users/quantumair/copilot/Project Snip and Crinkle`, branch `main`, level with `origin/main`, HEAD `7b4edf5`
  (179 commits). Untracked: `Images/`, `Videos/`, the new master-prompt file. Nothing staged or modified.
- Tools on hand: Python 3.13.14, numpy 2.5.3, Pillow 12.3.0, ffmpeg 9.0.2, 10 CPU cores. No blockers to reading.

## A. Repository map (VERIFIED)
| Area | What it is |
|---|---|
| `episodes/` (51 .py, ~29k lines) | One script per episode, short or rig test. New pipeline (Ep 11+): `hires.py`, `rig2.py`, `rig2_pip.py`, `acting.py` (`render_video`), `props_*`, `music_extra.py`. Old 1x pipeline (Ep 1-10): root `paperlib.py`, `characters.py`, `scene.py`, `icons.py`, `audio.py` |
| `tools/` (21 .py) | Deterministic checks: `check_video`, `plan_check`, `brief_check`, `handover_check`, `safezone`, `title_check`, `preflight`, `gate`, `approve`, `return_check`, `diet_check`, `build_agents`, `blind_guard`, `agent_hooks`, `regress` |
| `.claude/` | `settings.json` (Lead hooks), `agents/*.md` (6 agents, generated from MASTER_PROMPT Appendix A) |
| `state/gates.json` | Gate results per episode; only `tools/gate.py` writes it |
| `reviews/`, `docs/` | Plans, ledgers, blind reviews, mistake log, agent-run log; research, bible, playbook, roadmap |
| `build/` (2.1 GB), `output/` (422 MB), `Videos/` (590 MB) | Intermediate frames/WAVs, renders, owner-facing drafts (git-ignored) |

Tests: `python3 tools/regress.py` (97 cases, 0.2 s) and `python3 tools/agent_hooks.py selftest` (28 cases). Run by the
pre-commit hook only when `tools/`, `MASTER_PROMPT.md` or `.claude/` change. No CI.

## B. Actual execution flow (VERIFIED from source unless marked)
| Stage | Who / what | Inputs → outputs | Failure handling |
|---|---|---|---|
| 0 Pre-flight | Lead runs `preflight.py` | usage % → `.preflight_band` (2 h life) | `agent_hooks brief` refuses agent calls without a fresh band |
| 1 Plan | story-designer (LLM) → `plan_check.py` | topic brief → `reviews/epNN_plan.md` | plan_check FAIL → redo |
| 2 Gate 1 | safety-checker (LLM) → `gate.py set` | plan → `reviews/epNN_safety.md`, `state/gates.json` | hook refuses an animator "build" brief until gate1 PASS |
| 3 Storyboard + gate 1b | animator → `epNN_rough.py` → `build/sbN/storyboard.png`; blind reviewer retells it | | MISMATCH → restage |
| 4 Audio | `build_audio()` in the episode script: numpy synth → `build/epNN_audio.wav` | deterministic (seeded RNG) | none needed |
| 5 Render | `acting.render_video`: 8 spawn workers draw 15 drawings/s, each written twice to make 30 fps, piped as raw RGB to ffmpeg (x264 crf 18, loudnorm −14 LUFS) → `output/*.mp4` | Ep 11 reads stored 3x frames from `build/ep11_hi_r3/` | no resume; a crash means re-render from frame 0 (INFERRED) |
| 6 Handover + QA | `handover_check.py --verify` (module hash), `check_video.py` (ffprobe, loudness, silence, frame jumps) | mp4 → RESULT PASS/FAIL | |
| 7 Gates 2, 3 | blind reviewer (guarded by `blind_guard.py`, fails closed), safety-checker | blind copy, upload text | |
| 8 Packaging | packaging agent → `Videos/` + upload text; the owner uploads by hand | | hook refuses before gate2 PASS or owner-ok |

There are no model API calls in code (grep for anthropic/openai/requests/urllib: none). All LLM work runs through
Claude Code subagents, so prompt caching belongs to Claude Code, not to this repo (6.1 = NOT APPLICABLE at code level).

## C. Risk register and ranked backlog
| ID | Class | Finding | Evidence | Impact | Proposed action |
|---|---|---|---|---|---|
| F1 | VERIFIED | **The regression suite is red: 95/97.** Two cases (`regress.py:157`, `:213`) send an "ep12" animator brief; `agent_hooks.cmd_brief` reads the *live* `reviews/ep12_plan.md` (`agent_hooks.py:446`), which has 23 open estimates since commit `7b4edf5`, so brief_check correctly refuses it. The guard is right; the test leaks live repo state. That commit didn't touch `tools/`, so the pre-commit hook skipped regress and the break went in unnoticed | `brief_check.check(...)` returns the M39 refusal with the live plan and `[]` without it | The next commit that touches `tools/` or `MASTER_PROMPT.md` is blocked, and someone may be tempted to weaken the test | **Batch 1** (below) |
| F2 | VERIFIED | **Stored-frame caches don't know when the code changed.** Ep 11 `render_frame` (`ep11_friendly_glow.py:1834-1841`) reuses `build/ep11_hi_r3/dNNNNN.png` keyed only by drawing number. The frames date from 7 Oct; `rig2.py` changed on 18 Oct. A stale reuse already happened once (comment at line 1816: "the old frames were stale", fixed by hand by renaming the folder). The Short's cache does have a stamp (`ep11_short_transform.py:585`), but it hashes only 2 files, not `rig2`, `rig2_pip`, `props_hand2`, `hires` or `acting` | source + file dates | A re-render can silently mix old and new drawings. Low today (Ep 11 is parked), but Ep 12+ will copy the pattern | Batch 2: one shared stamp helper = hash of the script plus its repo imports (reuse `handover_check`'s import list); a mismatch means re-render |
| F3 | VERIFIED | Regress runs only when `tools/` etc. change, but checkers also read `reviews/*_plan.md` and `state/` | `.git/hooks/pre-commit` | This is how F1 slipped in | Part of Batch 1: always run regress (0.2 s) |
| F4 | VERIFIED | 4 stale git worktrees registered at an old path (`/Users/quantumair/copilot/snip-and-crinkle/...`, episodes 2-5), all "prunable", plus 16 MB copies in `.claude/worktrees/` | `git worktree list` | Clutter only | `git worktree prune` + remove the folder: **needs your yes (a delete)** |
| F5 | VERIFIED | No retention rule for `build/` (2.1 GB; `ep11_hi_r3` alone 788 MB) | `du` | Disk only | Later: a list of what's safe to clear once an episode ships (no deletes without a yes) |
| F6 | INFERRED | `Images/` (banner, profile) is untracked, so it isn't backed up to the private repo | `git status` | Brand art lost if the Mac is lost | Commit it (small PNGs) or add it to `.gitignore` on purpose |
| F7 | INFERRED | Render time isn't logged: `render_video` prints timings to the terminal only; TOOLKIT's "3.5 s per video second" is a documented claim I did not re-measure | `acting.py:403-425` | No baseline for render cost | Batch 3: append one line per render (script, frames, seconds, code hash) to a log |
| F8 | VERIFIED (absence) | Hard rule 5 "not templated" has no structured episode registry or sameness check; the proposed sameness script (16 Oct) is still waiting for the owner | `docs/research-gaps-oct-2026.md`, no registry file | YouTube "inauthentic content" risk grows with the library | Already proposed; I'd keep it as the next creative-quality step after Batch 1-2 |
| F9 | VERIFIED (by design) | `agent_hooks.py` fails open on any internal error; only `blind_guard.py` fails closed | docstring | A broken hook silently stops guarding | Covered by the SessionStart selftest (28/28 PASS today); no change |

Not a problem (examined): no secrets in tracked code (grep); `setup_cloud.sh` downloads only the OFL font from Google
Fonts' GitHub; audio and drawing noise use fixed seeds (repeatable output).

## Phase 1 baseline (what exists)
- **Measured today:** regress 95/97 FAIL; selftest 28/28 PASS; disk use as above; regress runtime 0.2 s.
- **Existing telemetry:** `reviews/agent_runs.md`, 27 agent runs since 17 Oct (real vs reported calls, peak context,
  return_check verdict). Peak context ranges from 8k to 151k (animator).
- **Not available:** total tokens per accepted episode (the log keeps peak context, not totals); render time history;
  cache hit/miss counts. I ran no renders (11+ min each, and not needed for Phase 0).

## Phase 4 agent architecture: recommendation
Keep the 6 agents. No new agents: every deterministic job (gates, briefs, budgets, cache stamps, video QA) is already
a script, or should become one (F2, F7). A "cache manager" should be a small helper module, not an agent.

## Proposed first implementation batch (needs your OK)
**Batch 1: make the safety tests honest again (F1 + F3).** Change only `tools/regress.py` and the pre-commit hook:
1. Run the two ep12 brief cases against a scratch copy of the repo's `reviews/` folder, so live plans can't change
   test results (the guard itself stays exactly as it is).
2. Run regress on every commit, not only when `tools/` changes.

Accept when `regress.py` gives 97/97 and still fails if the M39 check in `brief_check` is switched off (proves the test can
still fail). Undo: `git revert` of one commit.

## Implementation log
**Batch 1 (F1 + F3), done 18 Oct, owner OK in chat ("Yes, implement Batch 1").**
- `tools/regress.py`: the `brief()` helper runs `agent_hooks.cmd_brief` with `ROOT` pointed at a scratch folder, so no
  live `reviews/*_plan.md` can change a result. New case "F1 the hook still reads the episode's plan": an
  open-estimate plan in the scratch `reviews/` must still refuse a build brief. The guard (`agent_hooks.py`,
  `brief_check.py`) is unchanged.
- `tools/handoff_check.py --install`: the pre-commit hook now runs regress on every commit (0.2 s); reinstalled.
- Results: regress 98/98 PASS (was 95/97); selftest 28/28 PASS. Mutation check: with brief_check's open-estimate
  refusal switched off in memory, regress goes red (96/98: M39 and F1 fail), so the tests can still fail.
- Undo: `git revert <this commit>`, then `python3 tools/handoff_check.py --install`.
- Next proposed: Batch 2 (F2, code-hash stamp for stored frames). Not started.

**Batch 2 (F2), done 18 Oct, owner OK in chat ("Yes, implement Batch 2").**
- New `episodes/framestore.py`: a stored frame is reused only when its folder's `STAMP` equals the sha256 of the
  script plus every repo module it imports (`handover_check.modules`, `tools/` left out). `begin()` clears the stamp
  before a pass and `finish()` writes it atomically after the last frame, so a half-finished pass is never used. A
  stale or unstamped folder prints one warning, and those frames are drawn fresh.
- Wired into `ep11_friendly_glow.py` (it had no stamp) and `ep11_short_transform.py` (its stamp covered 2 files; it
  now covers 19 files, the script included, `rig2`, `rig2_pip`, `props_hand2`, `hires` and `acting` among them). Same file names, same `--hires` flags.
- Tests: regress 104/104 (6 new F2 cases); selftest 28/28. Mutation check: with `load()` ignoring the stamp, regress
  goes red (102/104). Live: one frame from each script, rendered from a cached range, printed the warning and drew
  fresh at the right size (Short 1080x1920 in 9.6 s; Ep 11 1920x1080).
- **Effect now:** `build/ep11_hi_r3/` and `build/ep11s_hi/` have no valid stamp (their old frames cannot be proven
  current), so a re-render of either draws the close shots at 2x until `--hires` is run again. Both are finished
  or parked; nothing was deleted (the old `build/ep11s_hi/code_hash.txt` is left in place).
- Side effect: because the scripts now import `framestore` (which imports `handover_check`), `handover_check
  --modules` for these scripts also lists `tools/handover_check.py`, `check_video.py` and `plan_check.py`. A
  handover `.ok` is therefore also invalidated when those checkers change. That is stricter, not looser.
- Undo: `git revert <this commit>`.

**Batch 3 (F7), done 18 Oct, owner OK in chat ("Yes, implement Batch 3").**
- `episodes/acting.py`: `render_video` now keeps ffmpeg's exit code and calls a new `log_render`, which appends one
  row to `reviews/render_log.md` (tracked, unlike `build/`): when, script, view, video length, drawings, workers,
  render seconds, render seconds per video second, ffmpeg ok/FAIL, framestore code hash and file size. Any error
  in the hash is written into the row and never stops a finished render. Render behaviour is otherwise unchanged.
  Ep 1-10 scripts have their own ffmpeg code and are not covered (they are finished).
- Tests: regress 108/108 (4 new F7 cases). Real run: `rigtest_acting` (4.6 s, 69 drawings, 8 workers) rendered into
  the scratchpad with a scratch log: 4 s, 0.82 render s per video s, ffmpeg ok, 1.1 MB. That is one sample from a
  light rig test, not an episode baseline; TOOLKIT's figure for Ep 11 (≈3.5 s per video s) is still unmeasured
  here. `check_video` on that file: loudness FAIL, as expected, because the real `--render` path runs
  `trim_loudness` afterwards and the test skipped it. All other checks passed.
- The real log starts with the next production render. Undo: `git revert <this commit>`.
- Noticed, not changed: (F10) `render_video` still prints "wrote" when ffmpeg fails; the log now shows FAIL, but
  the caller isn't stopped. (F11) `check_video.py` needs the file path first; flags first crash with a JSON error.

**Batch 4 (F10, F11), done 18 Oct, owner OK in chat ("Fix F10 ... and F11 ... as a small Batch 4").**
- F10 `episodes/acting.py`: if ffmpeg dies mid-stream (broken pipe), `render_video` stops drawing. On any non-zero
  exit it logs the FAIL row and then raises `RuntimeError`, so the caller (`trim_loudness`, the render chain) stops
  and never prints "wrote". Live: a missing WAV raised "ffmpeg exited 254" and logged `FAIL (exit 254)`; a good
  render still wrote and logged `ok` (4 s, 0.82 s per video s).
- F11 `tools/check_video.py`: new `path_arg` takes the one argument that is neither a flag nor a flag's value;
  no path, or two paths, prints the usage and exits 1. Live: flags first or last give the same result.
- Tests: regress 110/110 (2 new F11 cases). The F10 check is a live one-off, not in regress, because it starts a
  render pool and regress must stay at about 0.2 s. Undo: `git revert <this commit>`.

**F4 done 18 Oct, owner OK in chat ("Yes, prune the 4 stale git worktrees").** Checked first: branches `episode-02`
to `05` have 0 commits not in main, and every tracked file in the 4 folders is identical to its branch; the extras
were old build frames (≈15 MB) and font copies (the font still loads from `~/Library/Fonts`). Ran `git worktree
prune` and removed the 4 folders under `.claude/worktrees/` (git-ignored). The branches are kept.
