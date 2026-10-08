# Handoff: read this first (updated 2026-10-09)

How we work: `MASTER_PROMPT.md` (**v3.9**, 9 Oct: research rules from `docs/research-agent-craft-oct-2026.md` and `docs/research-comedy-acting-oct-2026.md`, acting in `docs/COMEDY_PLAYBOOK.md` section 9; v3.8 zero-based review `reviews/zero_based_review_2026-10-09.md`; rollback tag `agents-v3.8-pre-research`). Plan, dates and the upload
calendar: `docs/ROADMAP.md`. Code index: `docs/TOOLKIT.md`. History: `docs/HISTORY.md`. Limits and fixes:
`docs/LIMITATIONS.md`. Audit: `reviews/checkpoint_audit_2026-10-08.md`.

**Current phase: 0 (to 19 Oct). Step: Episode 11 Halloween transformation Short is SCHEDULED in Studio for Sun 18 Oct, 6:00 PM IST (cover 25.9 s; no playlist yet): upload sheet `reviews/ep11_short_transform_upload.md`, gate 3 PASS, files in `Videos/`. Blind round 2 scored overall 7 = round 1 (plateau; `reviews/ep11_short_blind_r2.md`); owner overruled gate 2 on 9 Oct (M44); compare this score with real data (A1). Next work package: a Short safe-zone check script (M42 + audit M5: bottom 19%, right 12% at 50-90% height); review finding 4 (Lead rule diet); audit M1-M11, L1-L3; then after the weekly reset the rig acting job (A2: features ranked in playbook section 9) with review finding 2 (gag clips judged blind before the build); deferred until the 14 Oct data: reviewer comedy rubric and reviewer model (agent-craft rows 6-7), and Episode 12. Test of v3.8 on Ep 12: gate 2 in ≤2 rounds, comedy ≥7, ≤2 safety checks and ≤2 builds per video.**
Round 2 blocking issues: owner judged them fine. Comedy 5 (sense 6), so the yardstick is missed: per `docs/LIMITATIONS.md` A2, a rig acting job before Ep 12.
Usage (9 Oct): 5-hour 16%, weekly 94% (reset Tue 13 Oct ~12:30 PM IST); owner 9 Oct: using the weekly limit is fine. Ledger `reviews/ep11_short_ledger.md`.

**Mistake log habit (owner rule):** `reviews/mistake_log.md`: OPEN: Lead M22, M23, M36, M37, M41, M42, M47, M49, M51; M44 (reviewer calibration: compare with real data first); M50. M33-M35, M38, M40, M43, M45, M48 APPLIED v3.7; M39, M46, M52 APPLIED as scripts. Priority: M42 + audit M5 (safe zones).
Rollback tags: `git tag -l 'agents-*'`; restore with `git checkout <tag> -- MASTER_PROMPT.md && python3 tools/build_agents.py`.

After it: **Episode 12 "Tidy up together" + colour sorting** (ROADMAP topic 2); its Short dressed for Diwali, Tue 3 Nov.
Then 13 potty, 14 bedtime, 15 dressed warm, 16 teeth (ROADMAP). Owner ruled (8 Oct): ✓/✗ icons allowed; never a wet bed on screen.
**Episode 11 (Pip and the Friendly Glow): the episode is parked.** Round 3 scored 6 (`reviews/ep11_blind_r3.md`); render `output/ep11_friendly_glow.mp4`.
**Test:** the next episode's gate 1b against the yardstick in `reviews/ep11_retro.md`. From Episode 12 the ledger lives in `reviews/epNN_ledger.md`.

Channel data: Shorts live since 5 Oct; only the owner's own views so far. Checkpoint Wed 14 Oct: Shorts feed reach, logged in `docs/analytics-log.md`; compare blind scores with real viewed vs swiped away.
Phone verification and 2-Step Verification: on. Waiting on the owner: upload Ep 9 v3 (Thu 15 Oct) and Ep 5 v2 (Fri 16 Oct); the pilot story Short (Tue 20 Oct) and episode (Wed 21 Oct), text in `reviews/pilot02_upload.md`.

Notes: `Videos/` holds drafts named "DRAFT-in-review_…" and "DRAFT-failed-review_…": don't upload them. Agent types load from `.claude/agents/` here and through links in `/Users/quantumair/copilot/.claude/agents/`.
