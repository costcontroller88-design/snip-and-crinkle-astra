# Handoff: read this first (updated 2026-10-08)

How we work: `MASTER_PROMPT.md` (**v3.3**, 8 Oct: Ep 11 retro + YouSEO, vidIQ and comedy retraining). Plan, dates and the upload
calendar: `docs/ROADMAP.md`. Code index: `docs/TOOLKIT.md`. History: `docs/HISTORY.md`.

**FIRST (owner, 8 Oct): rate the 6 agents + the Lead 1-10, harshly, from evidence (ledgers, mistake log, blind scores), with fixes; the owner approves changes.**

**Current phase: 0 (to 19 Oct). Step: Episode 11 Halloween transformation Short (Sun 18 Oct). Blind round 1 = overall 7, comedy 4. Fix mode r1 DONE (plan 7(b) rows "r1", change list `reviews/ep11_short_fixes_r1_plan.md`, 30.0 s) and its safety re-check DONE (R2-1..3 + N4 pasted into the plan). Next work package: (1) story-designer fix mode, comedy only: run every 7(b) gag through `docs/COMEDY_PLAYBOOK.md` (7-part test, gag table) and fix the failing parts (≤30 s); this is the test of the comedy retraining; safety-checker only if a gag changed; (2) a FRESH animator builds; Lead renders; blind round 2 is the last. Then packaging, gate 3.** Owner (8 Oct): ignore the weekly limit; 5-hour bands apply, but start no big agent with the reset <90 min away (M8). Plan `reviews/ep11_plan.md` 7(b); ledger `reviews/ep11_short_ledger.md`. **Mistake log habit (owner rule):** `reviews/mistake_log.md` (M16 APPLIED; M1-M15, M17-M19 OPEN); retrain after this Short (MASTER_PROMPT 10.11.9).
After it: **Episode 12 "Tidy up together" + colour sorting** (ROADMAP topic 2); its Short dressed for Diwali, Tue 3 Nov.
Then 13 potty, 14 bedtime, 15 dressed warm, 16 teeth (ROADMAP). Owner ruled (8 Oct): ✓/✗ icons allowed; never a wet bed on screen.

**Episode 11 (Pip and the Friendly Glow): the episode is parked; the transformation Short is queued (owner, 8 Oct).** Round 3 scored 6 (`reviews/ep11_blind_r3.md`); render `output/ep11_friendly_glow.mp4`.

**Retro done (8 Oct):** `reviews/ep11_retro.md` maps every mistake to a rule (MASTER_PROMPT sections 5, 10).
Owner rule (8 Oct): **lesson first, demand second** (MASTER_PROMPT 6): ROADMAP topics need a lesson before use.
Rollback tags: agents-v2-pre-retro, agents-v3-pre-youseo, agents-v3.1-pre-vidiq, agents-v3.2-pre-comedy (`git checkout <tag> -- MASTER_PROMPT.md && python3 tools/build_agents.py`). Comedy yardstick: comedy ≥7 in the Short's round 2 and ≥8 at Ep 12 gate 2.
**Test:** the next episode's gate 1b; judge against the yardstick in `reviews/ep11_retro.md` (gate 1b in 1 round,
gate 2 in ≤2, animator ≤50% of the spend, ≤1 unproven check, one episode ≤1 full 5-hour window). From Episode 12,
the ledger lives in `reviews/epNN_ledger.md`.

Channel data: 2 Shorts live (5 and 6 Oct); Studio on 7 Oct showed only the owner's own views. Checkpoint Wed 14 Oct:
Shorts feed reach, logged in `docs/analytics-log.md`.

Phone verification and 2-Step Verification: on (owner, 8 Oct). Waiting on the owner: upload Ep 9 v3 (Thu 15 Oct) and Ep 5 v2 (Fri 16 Oct); the pilot story Short (Tue 20 Oct) and episode
(Wed 21 Oct), text in `reviews/pilot02_upload.md`.

Notes: `Videos/` holds drafts named "DRAFT-in-review_…" (Episode 11, old render) and "DRAFT-failed-review_…" (the
dropped whale Short): don't upload either. Agent types load from `.claude/agents/` here and through links in
`/Users/quantumair/copilot/.claude/agents/`. Only one Lead session at a time (pre-flight item 1).
