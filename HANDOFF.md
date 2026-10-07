# Handoff: read this first (updated 2026-10-08)

How we work: `MASTER_PROMPT.md` (**version 3** since 8 Oct: the Episode 11 retro). Plan, dates and the upload
calendar: `docs/ROADMAP.md`. Code index: `docs/TOOLKIT.md`. History: `docs/HISTORY.md`.

**Current phase: 0 (foundations, to 19 Oct); Phase 1 starts 20 Oct. Step: the Episode 11 Halloween transformation Short (Sun 18 Oct) has a plan and has passed gate 1 (8 Oct). Next work package: gate 1b, starting the storyboard sheet with a prototype still of the light through the paper. Start it no earlier than Tue 13 Oct (the weekly limit reset; it was at 60%, above even pace).** Plan: `reviews/ep11_plan.md` 7(b), 29.4 s, taking turns (Crinkle takes the marker mid-turn, gives it back, waits), a paper-lantern pumpkin with a drawn face, the light put in by the grown-up's hand, no cutting. Safety: `reviews/ep11_safety.md` (last section). Ledger: `reviews/ep11_short_ledger.md`. Build, review and gate 3 by Sat 17 Oct.
After it: **Episode 12 "Tidy up together" + colour sorting** (Lead go, 8 Oct; ROADMAP topic 2; evidence
`docs/research-synthesis-oct-2026.md`, confirmed by the 4-way research of 8 Oct); its Short dressed for Diwali, Tue 3 Nov.
Then 13 potty, 14 bedtime, 15 dressed warm, 16 teeth (ROADMAP). Owner ruled (8 Oct): ✓/✗ icons allowed; never a wet bed on screen.

**Episode 11 (Pip and the Friendly Glow): the episode is parked; the transformation Short is queued (owner, 8 Oct).** Round 3 scored 6 (`reviews/ep11_blind_r3.md`); render `output/ep11_friendly_glow.mp4`. The owner chose "retro first", then queued the Short (8 Oct).

**Retro done (8 Oct):** `reviews/ep11_retro.md` maps every mistake to a rule. Changes: the evidence rule and tool-call
budgets on the rules card; `maxTurns` hard caps in every agent file; the safety-checker on Opus; a feasibility pass
before any build; key sheets from the changes; the plan as the one source of truth; the plateau rule; the Lead
pre-flight checklist and usage bands (section 10, items 10-11). Effort can't be set per agent (not documented).
Owner rule (8 Oct): **lesson first, demand second** (MASTER_PROMPT 6): ROADMAP topics need a lesson before use.
Rollback: `git checkout agents-v2-pre-retro -- MASTER_PROMPT.md && python3 tools/build_agents.py`.
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
