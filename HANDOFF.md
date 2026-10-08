# Handoff: read this first (updated 2026-10-08, night)

How we work: `MASTER_PROMPT.md` (**v3.6**, 8 Oct: audit H1-H8; rollback tag `agents-v3.5-pre-audit`). Plan, dates and the upload
calendar: `docs/ROADMAP.md`. Code index: `docs/TOOLKIT.md`. History: `docs/HISTORY.md`. Limits and fixes:
`docs/LIMITATIONS.md`. Audit: `reviews/checkpoint_audit_2026-10-08.md`.

**Current phase: 0 (to 19 Oct). Step: Episode 11 Halloween transformation Short (Sun 18 Oct; build by 15 Oct) is at the PLATEAU: blind round 2 scored overall 7, the same as round 1 (`reviews/ep11_short_blind_r2.md`; render `output/ep11_short_transform.mp4`, check_video PASS). Next work package (owner: no preference, so the Lead's plan, 8 Oct): after the weekly reset (Tue 13 Oct), one targeted fix round, then blind round 3, packaging (`title_check`), gate 3, upload Sun 18 Oct.**
Round 2 blocking issues (staging and cameras → story-designer, then animator):
1. 21-30 s: the marker held at Crinkle's belly (R3-2) reads as "Bear draws on his tummy" for 9 s. Misread rule: he puts it away on screen (M43; safety re-check of that beat).
2. 23.5-24.5 s: the tea light reads ~6% wide with no close-up; `--check` measured 13.3% in D. Measure the light alone first (10.11.5).
3. 24-25.5 s: the lit pumpkin's right eye is in the right-12% Shorts zone (Lead's D 1.79x, M42). Do audit M5 (safe-zone `--check`) first.
Comedy 5 (sense 6), so the yardstick is missed: per `docs/LIMITATIONS.md` A2, a rig acting job before Ep 12.
Usage: 5-hour 72%, weekly 91% (reset Tue 13 Oct ~12:30 PM IST): small jobs only until then (C1). Ledger `reviews/ep11_short_ledger.md`.

**Mistake log habit (owner rule):** `reviews/mistake_log.md`: OPEN M22, M23, M33-M38, M40-M43 (M39 APPLIED as a script). Retrain after this Short (MASTER_PROMPT 10.11.9); then audit M1-M11, L1-L3. Priorities: M42 + audit M5 (safe zones), M43 (misread at plan time), M35/M40 (safety rules tested on measured runs), M33/M38 (overruns).
Rollback tags: agents-v2-pre-retro, agents-v3-pre-youseo, agents-v3.1-pre-vidiq, agents-v3.2-pre-comedy, agents-v3.3-pre-ratings, agents-v3.4-pre-measure, agents-v3.5-pre-audit (`git checkout <tag> -- MASTER_PROMPT.md && python3 tools/build_agents.py`).

After it: **Episode 12 "Tidy up together" + colour sorting** (ROADMAP topic 2); its Short dressed for Diwali, Tue 3 Nov.
Then 13 potty, 14 bedtime, 15 dressed warm, 16 teeth (ROADMAP). Owner ruled (8 Oct): ✓/✗ icons allowed; never a wet bed on screen.
**Episode 11 (Pip and the Friendly Glow): the episode is parked.** Round 3 scored 6 (`reviews/ep11_blind_r3.md`); render `output/ep11_friendly_glow.mp4`.
**Test:** the next episode's gate 1b against the yardstick in `reviews/ep11_retro.md`. From Episode 12 the ledger lives in `reviews/epNN_ledger.md`.

Channel data: Shorts live since 5 Oct; only the owner's own views so far. Checkpoint Wed 14 Oct: Shorts feed reach, logged in `docs/analytics-log.md`; compare blind scores with real viewed vs swiped away.
Phone verification and 2-Step Verification: on. Waiting on the owner: upload Ep 9 v3 (Thu 15 Oct) and Ep 5 v2 (Fri 16 Oct); the pilot story Short (Tue 20 Oct) and episode (Wed 21 Oct), text in `reviews/pilot02_upload.md`.

Notes: `Videos/` holds drafts named "DRAFT-in-review_…" and "DRAFT-failed-review_…": don't upload them. Agent types load from `.claude/agents/` here and through links in `/Users/quantumair/copilot/.claude/agents/`. Only one Lead session at a time: old Lead sessions archived 8 Oct (owner).
