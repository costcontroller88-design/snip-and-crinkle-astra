# Handoff: read this first (updated 2026-10-08, evening)

How we work: `MASTER_PROMPT.md` (**v3.5**, 8 Oct: agent ratings, check scripts, measure first). Plan, dates and the upload
calendar: `docs/ROADMAP.md`. Code index: `docs/TOOLKIT.md`. History: `docs/HISTORY.md`. Limits and fixes:
`docs/LIMITATIONS.md`. Ratings: `reviews/agent_ratings_2026-10-08.md`.

**Current phase: 0 (to 19 Oct). Step: Episode 11 Halloween transformation Short (Sun 18 Oct; build by 15 Oct). Next work package (owner, 8 Oct): (1) apply audit H1-H8 from `reviews/checkpoint_audit_2026-10-08.md` (a fresh agent with the report as spec, tested on scratch copies; the Lead verifies; M1-M11, L1-L3 after the Short); (2) a FRESH animator: stage "feasibility first": measure the 4 estimates in the plan's `## Measured checks` (M26-M29), then build the r3 rows of `reviews/ep11_short_plan.md` (checklist `reviews/ep11_short_fixes_r3.md`; R4-1, R4-2 pasted; the WIP code is committed); last command `tools/handover_check.py` must PASS; `--keys`. Lead: key sheet look, render chain (starts `--verify`), then blind round 2 (the last; plateau rule). Then packaging (`title_check`), gate 3.**
Open for the animator: hand-to-Crinkle gap 5.5 at 24.8 (need ≥30; else Crinkle at 1290); the gate post over Crinkle at the end (stills END 28.6, K2 29.5); camera G needs hires like T. No safety re-check for Snip's step to 660.
Usage: weekly 81% at 8:10 PM IST, likely out by Sat 10 Oct (reset Tue 13 Oct): finish the Short, then small jobs (`docs/LIMITATIONS.md` C1). Ledger `reviews/ep11_short_ledger.md`.

**Mistake log habit (owner rule):** `reviews/mistake_log.md`: M16 and 19 rows APPLIED on 8 Oct (v3.4); M22-M25, M30-M32 OPEN; M26-M29 APPLIED (v3.5). Retrain after this Short (MASTER_PROMPT 10.11.9). Priorities: M32 (Lead codes nothing above ~200k context); M24/M25 → rules card; M30/M31 → `maxTurns`.
Rollback tags: agents-v2-pre-retro, agents-v3-pre-youseo, agents-v3.1-pre-vidiq, agents-v3.2-pre-comedy, agents-v3.3-pre-ratings, agents-v3.4-pre-measure (`git checkout <tag> -- MASTER_PROMPT.md && python3 tools/build_agents.py`). Comedy yardstick: comedy ≥7 in the Short's round 2 and ≥8 at Ep 12 gate 2; if <7, switch to a rig acting job before Ep 12 (`docs/LIMITATIONS.md` A2).

After it: **Episode 12 "Tidy up together" + colour sorting** (ROADMAP topic 2); its Short dressed for Diwali, Tue 3 Nov.
Then 13 potty, 14 bedtime, 15 dressed warm, 16 teeth (ROADMAP). Owner ruled (8 Oct): ✓/✗ icons allowed; never a wet bed on screen.
**Episode 11 (Pip and the Friendly Glow): the episode is parked.** Round 3 scored 6 (`reviews/ep11_blind_r3.md`); render `output/ep11_friendly_glow.mp4`.
**Test:** the next episode's gate 1b against the yardstick in `reviews/ep11_retro.md`. From Episode 12 the ledger lives in `reviews/epNN_ledger.md`.

Channel data: Shorts live since 5 Oct; only the owner's own views so far. Checkpoint Wed 14 Oct: Shorts feed reach, logged in `docs/analytics-log.md`; compare blind scores with real viewed vs swiped away.
Phone verification and 2-Step Verification: on. Waiting on the owner: upload Ep 9 v3 (Thu 15 Oct) and Ep 5 v2 (Fri 16 Oct); the pilot story Short (Tue 20 Oct) and episode (Wed 21 Oct), text in `reviews/pilot02_upload.md`.

Notes: `Videos/` holds drafts named "DRAFT-in-review_…" and "DRAFT-failed-review_…": don't upload them. Agent types load from `.claude/agents/` here and through links in `/Users/quantumair/copilot/.claude/agents/`. Only one Lead session at a time: old Lead sessions archived 8 Oct (owner).
