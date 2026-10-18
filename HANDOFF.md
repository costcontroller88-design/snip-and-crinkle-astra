# Handoff: read this first (updated 2026-10-18)

How we work: `MASTER_PROMPT.md` (**v4.2**, 17 Oct: hooks (`tools/agent_hooks.py`, `tools/gate.py`) run return_check, brief, preflight, gate, stage and Lead checks, write scopes; runs logged in `reviews/agent_runs.md`; tests `python3 tools/regress.py`; v4.0: the Lead's 12 core rules, the rest in `docs/agents/lead_reference.md`; versions in the MASTER_PROMPT header). Plan, dates and the upload
calendar: `docs/ROADMAP.md`. Code index: `docs/TOOLKIT.md`. History: `docs/HISTORY.md`. Limits and fixes:
`docs/LIMITATIONS.md`. Audit: `reviews/checkpoint_audit_2026-10-08.md`.

**Current phase: 0 (to 19 Oct). Step: the A2 rig acting job is DONE (18 Oct). `episodes/rig2.py` `acting()` (`docs/TOOLKIT.md`). Gag test: round 2 scored 7 and 7 (`docs/HISTORY.md`). Carry into Ep 12: every exit or lift-off needs a visible cause. A2 left: head squash, mouth shapes, sound slots. Ep 11 Halloween Short was scheduled for 18 Oct 6:00 PM IST (no playlist yet); compare blind scores with real data (A1). Ep 12 (18 Oct, 3 restages, sheet `build/sb3/`): gate 1 FAIL (F1-F7 fixed; 1 new FIX F8, not measured); gate 1b round 2 (last) MISMATCH. **Waiting on the owner's pick** (options: `reviews/ep12_ledger.md`, "Owner decision"); then that fix round, gate 1b round 3 if approved, a gag test. Proposed 16 Oct, owner to approve: a sameness-check script and a Studio check every second Friday (`docs/research-gaps-oct-2026.md`). Test of v3.8 on Ep 12: gate 2 in ≤2 rounds, comedy ≥7, ≤2 builds (≤2 safety checks: missed, 3 at gate 1).**
Deferred: reviewer comedy rubric and model (agent-craft rows 6-7).


**Mistake log habit (owner rule):** `reviews/mistake_log.md`: OPEN: M63, M67 (Lead brief), M64 (animator loudness), M66, M68 (Lead estimates), M69 (Lead fix pick), M70, M78, M81 (safety), M71 (return wording), M72-M76, M80 (animator; M75/M76/M80 count repeats → script due), M73-M74 (designer geometry → script due), M77, M79, M82 (Lead); M44 (reviewer calibration: compare with real data first); M50. M33-M35, M38, M40, M43, M45, M48 APPLIED v3.7; M39, M42, M46, M52, M54, M55 APPLIED as scripts.
Rollback tags: `git tag -l 'agents-*'`; restore with `git checkout <tag> -- MASTER_PROMPT.md && python3 tools/build_agents.py`.

After it: **Episode 12 "Tidy up together" + colour sorting** (ROADMAP topic 2); its Short dressed for Diwali, Tue 3 Nov.
Then 13 potty, 14 bedtime, 15 dressed warm, 16 teeth (ROADMAP). Owner ruled (8 Oct): ✓/✗ icons allowed; never a wet bed on screen.
**Episode 11 (Pip and the Friendly Glow): the episode is parked.** Round 3 scored 6 (`reviews/ep11_blind_r3.md`); render `output/ep11_friendly_glow.mp4`.
**Test:** the next episode's gate 1b against the yardstick in `reviews/ep11_retro.md`. From Episode 12 the ledger lives in `reviews/epNN_ledger.md`.

Channel data: Shorts live since 5 Oct; only the owner's own views so far. Studio 16 Oct: 5 viewers in 28 days, too few to judge (`docs/analytics-log.md`); next check Fri 30 Oct.
Phone verification and 2-Step Verification: on. Waiting on the owner: upload Ep 9 v3 and Ep 5 v2 (were due 15-16 Oct, not yet up); the pilot story Short (Tue 20 Oct) and episode (Wed 21 Oct), text in `reviews/pilot02_upload.md`.

Notes: `Videos/` holds drafts named "DRAFT-in-review_…" and "DRAFT-failed-review_…": don't upload them. Agent types load from `.claude/agents/` here and through links in `/Users/quantumair/copilot/.claude/agents/`.
