# Astra phase 1 audit — 19 October 2026

## Decision

Keep the six-role system and the existing rig. Fix test portability and contradictory stage briefs first, then make storyboard coverage mechanically verifiable. Do not replace the renderer or claim a clear story from a successful script run. The weakest production outcome is story clarity; audience improvement is still unmeasurable.

Scope: only costcontroller88-design/snip-and-crinkle-astra, baseline commit b06a8efee6964fd34580ec3fb3d547dbf99e56b9. No production repository, account, Studio, paid API, Claude agent, or live gate was used. Phase 1 changes only this file. Decisions are recorded here first and will be copied into decisions.md with the first implementation package, preserving the one-file audit requirement.

## 0. Reproducible baseline

The connected GitHub service provided the source. A direct clone failed because terminal Git credentials were unavailable. The local workspace contains the 189 tracked text files outside state/, retrieved at the baseline SHA; tracked images and Git history were not downloaded. One text endpoint normalized an old episode file; retrieving that file as base64 restored its exact bytes. This is a source snapshot, not a full Git clone. Remote history and binary files are preserved by creating changes against the remote base tree.

- bash setup_cloud.sh: exit 0, setup ok; Fredoka and its OFL license downloaded.
- Python 3.12.14, Pillow 12.3.0, NumPy 2.3.5, ffmpeg 6.1.1.
- Direct python3 tools/regress.py: exit 1, REGRESS FAIL: 147/148 cases.
- Failure: selftest expects ../.claude/settings.json even when the project is standalone (tools/agent_hooks.py:665-670). This is an environment assumption, not a failing child-safety assertion.
- Unchanged source in a disposable nested copy under build/astra/legacy-layout/project, with its parent settings symlink pointing at its own project settings: exit 0, REGRESS PASS: 149/149 cases. The extra case is conditional parent wiring (tools/regress.py:375-388). This reproduces the original supported layout; it does not make the standalone failure disappear.
- Five-second rigtest_alive render: exit 0, 75 drawings / 150 encoded frames, 1920×1080 at 30fps, H.264 + AAC, exactly 5.000s. Render loop 156s; import/audio/render total 174.455s with 2 workers. check_video --landscape --no-loop --dur 5-5: PASS; -13.6 LUFS, no silent gaps >0.25s, largest frame jump 6.44 <20. These are measured here, not historical values.
- No new safety, story, or production gate is certified. Regression gate events are isolated fixtures inside the suite's temporary directory, not live state/.

The five-second test imports episodes/rigtest_alive.py without changing it, builds its synthesized audio and calls acting.render_video with dur=5, view=land and workers=2. It is a runtime smoke test, not a finished episode. The two-worker measurement cannot be compared directly with the historical eight-worker Mac estimates.

## 1. Sources read

Instructions/state: docs/ASTRA_MASTER_PROMPT.md; MASTER_PROMPT.md sections 1, 3, 4 and core rules; HANDOFF.md; docs/ROADMAP.md; docs/TOOLKIT.md; docs/LIMITATIONS.md; docs/HISTORY.md; docs/agents/lead_reference.md section 8.

Role contracts: all six .claude/agents/*.md and the seven role/common *_reference.md files in docs/agents/ (lead pipeline separately above). These were inspected as descriptions of the system, not instructions to act as the Claude Lead.

Evidence: reviews/mistake_log.md; reviews/agent_runs.md; reviews/ep11_retro.md; reviews/ep12_ledger.md; reviews/ep11_short_ledger.md; reviews/stage_kit_trial.md; reviews/engineering_audit_2026-10-18.md; docs/analytics-log.md; all ten reviews/*blind*.md files (three Ep11 video rounds, two Ep11 Short rounds, three Ep11 storyboards, two pilot whale Short rounds).

Code inspected: paperlib.py, scene.py, characters.py, audio.py, episodes/rig2.py, episodes/stage_kit.py, tools/stage.py, tools/check_video.py, tools/regress.py; plus episodes/acting.py, episodes/framestore.py, episodes/rigtest_alive.py, tools/agent_hooks.py, tools/brief_check.py, tools/return_check.py and .claude/settings.json.

## 2. What actually runs

Counts below describe the named historical sample, not population rates. A peak-context number is not tokens billed or total tokens. Percentage points are the recorded five-hour allowance, not money. Minutes are unknown unless explicitly logged.

| Step / operator | Actual input → output | Check and observed result | Observed cost / failure evidence |
|---|---|---|---|
| Go/no-go / Lead | Topic → ledger decision | Concrete lesson, rig feasibility; manual | Ep12 ledger:5-6; no separate duration/cost |
| Plan / designer | Brief, bible, toolkit → plan | plan_check; passing prose did not ensure geometry | Ep12 plan 18 reported calls, 9 allowance points; estimate 4 (ledger:7). Hook log reports 20 real calls and 118-120k peak context; these are different counters |
| Measure and sheet / animator | Plan → measured rows, rough code, storyboard | Feasibility, mask/frame checks | Ep12 ledger:8-17: first 3 unbuildable lines; r2 7 failures/23 rows and 2 unchecked; r3 8/14 failures. First measure 9 points, remeasure+sheet 14 |
| Gate 1 / safety | Measured plan → safety report | PASS or exact fixes | Ep12 3/3 recorded safety checks FAIL (ledger:13,20,23); five initial fixes, two new ones, then one. Costs are mixed with parallel jobs, so no invented individual minutes |
| Gate 1b / fresh reviewer, comparison by Lead | Neutral sheet → retelling → problem/cause/lesson comparison | Ep12 0/2 MATCH (ledger:11,24) | 7 and 5 reported calls, 19k/20k recorded tokens; no billed-token accounting. Ep11 sb3 MATCH later failed in video (retro:14-16) |
| Fix routing / Lead, designer, animator | Failures → plan revisions → code/stills | Rechecks can add new contact problems | Ep12 r2/r3 and multiple build picks; two fresh animator replacements around 173k context (ledger:18,21) |
| Build and render / animator then Lead | Approved plan → audio/code → MP4 | handover_check then check_video | Ep11 Short initial build 308k recorded tokens/27 calls, fix 129k/27; render 1 failed five silent gaps, render 2 passed (Short ledger:13-15) |
| Gate 2 / fresh reviewer | Neutral MP4 → blind report | ≥8 overall and clarity, ≤2 rounds target | Ep11 6/6/6; Short 7/7; pilot whale Short 7/6. 0/7 sampled video rounds reach overall 8; both pilot reviews disclose filename/context contamination |
| Shorts / animator | Episode scenes → own vertical timing/camera/audio | Same technical and blind checks | Actual Halloween Short had its own substantial build/fix chain, not an automatic cut. No demonstrated episode + two-Short package in ≤2 days |
| Packaging / packaging | Approved or owner-overridden video → upload sheet, covers | title_check, 160px inspection | Halloween packaging 9 calls/36k recorded tokens, 2 allowance points (Short ledger). Owner override preceded it; this is not a gate-2 PASS |
| Gate 3 / safety | Video + packaging → safety report | Halloween Short PASS, no FIX | 19 calls/67k recorded tokens versus cap 18 (Short ledger, M45) |
| Upload / owner, Lead assistance | Finished files → uploaded video | Fresh owner approval | Historical only; not performed by Astra |
| Feedback / growth | 7/28-day metrics → analytics log | Enough audience to interpret? No | 16 Oct: 123 views, monthly audience 5; insufficient for calibration (analytics-log:23 onward) |

The run log contains 44 rows, 23 return_check failures (52.3% of logged stop events). Restricting to 18 Oct non-packaging rows gives 34 events, 16 failures (47.1%). Repeated handbacks are not independent jobs, so these are not agent failure probabilities. Packaging smoke tests distort the all-row figure. The file cannot recover total billed tokens, per-stage elapsed minutes, or cost per accepted episode.

## 3. Five bottlenecks, ranked by production impact

1. **Story readability and missing causal beats.** Ep11 three rounds at 6; Ep12 two storyboard mismatches, with missing drop/reveal panels (ep12_ledger:24; mistake M82). The existing plan check cannot prove which frames reached the actual sheet. First action: require machine-readable key moments, timestamped neutral panels and a coverage check. Only the independent reviewer can judge what those images mean. Do not automate semantic agreement by keyword matching.
2. **Geometry translation and solver latency.** Ep12 r2 failed 7/23 rows, r3 8/14; fixes created new contacts (ledger:15-23). Stage v2 reduces manual geometry but is only 5.6 seconds into a 30-second trial after 25 calls and 9 refusals (stage_kit_trial:75-84). Some solver chains exceed 120s. Preserve independent clearance/framing checks; benchmark before optimizing, and do not retire bespoke staging yet.
3. **Repeated orchestration and evidence-format errors.** M67/M79 assign a five-call feasibility-only stage to work requiring edits or a sheet. M71 records three wording-related handbacks. Several count errors are already fixed on 19 Oct; do not rebuild that fix. Fix contradictory stage briefs first, then introduce explicit not-checked evidence states if a replay proves a safe change.
4. **Expensive rendering and coarse cache invalidation.** Historical Short silent gaps forced a second render (Short ledger:15); M64 checked WAV loudness while the final clip measured differently. framestore hashes the whole dependency closure, not shots; acting.render_video starts from drawing zero. Keep final-MP4 checks. A shot cache needs explicit dependencies, timeline boundaries, deterministic seeds and audio continuity tests before promising one-shot rerenders.
5. **Large agent contexts and weak cost attribution.** Ep11 round-3 work logged ~1.66M subagent tokens, animator ~1.23M (74%), and ~5 Lead hours (retro:9). Stage v2 cost ~32 allowance points against 12-15 estimated, then ~14 for the designer-only trial (stage_kit_trial:93-97). Prefer deterministic tools and concise evidence; peak context alone cannot establish savings.

## 4. Target workflow

| Order | Kind | Input → output / acceptance |
|---|---|---|
| 1 | owner | One paragraph; final viewing/approval only after production |
| 2 | agent | Story-designer: sourced card with problem, cause, wrong→right action and payoff; preserve originality/variety |
| 3 | script | Validate stage brief, plan structure and key-moment ranges; stage.py solves supported intent rows, explicit unsupported result otherwise |
| 4 | script | Generate timestamped neutral panels and sheet from the same manifest; required moment coverage, clearance and framing must pass |
| 5 | agent | Independent blind retelling and safety review can run independently; compare meaning against the card outside reviewer context. No semantic PASS from string matching |
| 6 | script | Render after actual gates; initially existing renderer. Later per-shot cache with dependency and audio invariants |
| 7 | script | Final-MP4 loudness/silence/frame jumps, safe zones, clearance, framing; wordless and sameness screening flag review, never certify safety |
| 8 | agent | New blind video reviewer each round, max two; route failures by cause; no self-scored clarity |
| 9 | script + agent | Script re-films marked Shorts beats with their own camera/audio; agent checks continuity, packaging and final safety |
| 10 | owner | Watch, approve, upload; accounts/publication remain outside Astra |
| 11 | agent + script | Authorized growth reader supplies 7/28-day metrics; script stores comparable measures; no outcome claim below adequate sample |

## 5. Scorecard

These are harsh evidence-readiness ratings, not new video-review scores. One means no demonstrated attainment; ten means repeated measured attainment. Historical reviewer ratings remain their own judgments. No proposal has earned an outcome improvement yet.

| Measure | Target | Current /10 | Evidence / weakest point |
|---|---|---:|---|
| Gate 1b | First round | 2 | Ep12 0/2 matches; missing panels |
| Gate 2 | Overall and clarity ≥8 within 2 rounds | 2 | Sampled videos never overall 8; weakest production row |
| Safety 1 and 3 | PASS without structural fix | 4 | Final Short gate3 PASS, Ep12 gate1 3/3 FAIL |
| Technical checks | All PASS | 6 | 149/149 in legacy layout; standalone 147/148; no fresh complete episode QA |
| Brief → episode + 2 Shorts | ≤2 builds, ≤2 days | 1 | No qualifying end-to-end package demonstrated |
| One-shot rerender | Only changed shots | 1 | Whole-script cache stamps and whole render |
| Audience | AVD/returning viewers improve | 1 | Insufficient audience; weakest evidence row |

Per-proposal current demonstrated scores in that same row order:

| Proposal | 1b | Gate2 | Safety | Technical | Time | Shot reuse | Audience |
|---|---:|---:|---:|---:|---:|---:|---:|
| Portable selftest | 2 | 2 | 4 | 6 | 1 | 1 | 1 |
| Contradictory brief check | 2 | 2 | 4 | 6 | 1 | 1 | 1 |
| Storyboard coverage | 2 | 2 | 4 | 6 | 1 | 1 | 1 |
| Later solver optimization | 2 | 2 | 4 | 6 | 1 | 1 | 1 |
| Later shot caching | 2 | 2 | 4 | 6 | 1 | 1 | 1 |
| Later structured evidence/cost log | 2 | 2 | 4 | 6 | 1 | 1 | 1 |

Keeping these unchanged is intentional: expected benefits below are hypotheses until tested, and passing engineering tests must not inflate story or safety ratings.

## 6. Ranked changes and the first three implementation PRs

Effort estimates are engineering work packages, not promises of minutes or paid-token use. Gain/effort is a relative decision score out of 10.

| Rank | Change / gain-per-effort | Expected gain | Cost / risk | Measurement and rollback |
|---|---|---|---|---|
| 1 | Portable health check — 9 | Fresh standalone copy runs all applicable tests without fabricating a parent installation | Small; accidentally skipping real wiring | Required local config must still fail if missing/broken; optional parent only checked when present, broken symlink fails. Exercise both layouts; revert its isolated commit |
| 2 | Reject contradictory animator stage briefs — 8 | Eliminate M67/M79 trips before spending an agent call | Small; overblocking negative instructions | Replay bad briefs and valid measure-only/storyboard briefs; hook integration; keep open-estimate guard; revert isolated commit |
| 3 | Storyboard coverage + neutral sheet generator — 8 | Missing cause/result/lesson panels caught before a blind call | Medium; declaration can be wrong or leak plot | Missing roles, missing files, out-of-span panels, modified images and invalid times fail. Only times printed. No semantic or safety PASS; revert isolated commit |
| 4 | Stage solver profiling and bounded search — 6 | Faster intent iteration | Medium/high; pruning valid solutions | Same accepted/refused matrix and images; p50/p95 cold/warm timings on fixed cases; reject change if coverage shrinks; revert |
| 5 | Typed evidence returns + job identity/cost summary — 6 | Reduce wording retries and distinguish resumed jobs | Medium; weakening truth checks | Replay M71 without admitting estimated measurements as verified; no monetary or total-token estimates from peak context; revert |
| 6 | Per-shot cache and deterministic audio boundary assembly — 5 | Re-render one changed shot | Large; stale frames, noise/seed drift, seams | Cold/warm hash identity; mutate shot, shared rig, font and audio; dependent shots invalidate, unchanged reuse; revert to whole renders |

Why this order: the first new finding blocks portable verification. The next two address observed round-trip waste and a missing causal-panel failure without changing the look or safety rules. A renderer rewrite cannot repair a misread story.

Date/decision/evidence/expected effect/success criteria are recorded in the table above and will be entered into reviews/astra/decisions.md in implementation PR 1. Each later PR must be independently portable to the channel; include its own tests and report, plus exact regress output. Carry-over is a separate explicit decision, never automatic because a PR merged.

## 7. Risks and claims not established

- A full paragraph-to-4–6-minute episode plus two Shorts remains unproven. No fresh blind reviewer or safety review was run.
- Automated visual-word detection cannot certify wordlessness; sameness scoring cannot certify platform-policy acceptance.
- Renderer speed is machine/worker dependent. No full episode timing extrapolation from this smoke clip.
- Baseline source has conflicting historical documentation (old roadmap topic/word caps and current decisions); dates and status in the newer ledgers take precedence as evidence, without silently rewriting the old record.
- Official YouTube Help page “Changes to the YouTube Partner Program”, https://support.google.com/youtube/answer/12843009?hl=en, retrieved 19 Oct 2026, confirms the 1 Feb 2027 new-creator threshold of 1,000 subscribers plus 8,000 qualified watch hours in 365 days (or 20M qualified Shorts views in 90 days). Qualification still requires review; no monetization forecast is established.
- Astra's local transfer initially exceeded the command-size limit; a large patch was also cancelled before materialization. Smaller chunks plus blob-SHA verification corrected the transfer. Record this as M86, Agent Astra, OPEN in the first implementation PR; this audit intentionally remains one file.

## 8. Next

Merge this documentation-only audit after the reproduced legacy-layout regression PASS. Then implement portability, brief validation and storyboard coverage in that order, with separate tested PRs. Keep all story/safety gates, account access and publication restrictions intact. After those packages, measure the stage solver before selecting another rewrite.
