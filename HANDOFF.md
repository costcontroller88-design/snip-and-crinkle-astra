# Handoff: read this first (updated 2026-10-07)

How we work (rules, the agent team, the pipeline, the token budget): `MASTER_PROMPT.md` (version 2). Plan, dates and
the upload calendar: `docs/ROADMAP.md`. Code index: `docs/TOOLKIT.md`. History (Episodes 1-10, setup): `docs/HISTORY.md`.

**Current phase: 0 (foundations, to 19 Oct); Phase 1 starts 20 Oct. Step: work package "Episode 11" (Pip and the
Friendly Glow), gate 2. Next work package: the Lead checks the new key sheet, then blind review round 2 (the last).**

Done: plan, gate 1, stages 1-3. Blind review round 1 (`reviews/review_video_blind_r1.md`): overall 6; the opening
was misread (hearts too small, dusk too subtle, Pip's hide too quick), a loud sting at 28 s, few gags 32-80 s. The
Lead's fix list `reviews/ep11_fixes_r1.md` (B1-B3, P1-P7) is applied and re-rendered: `output/ep11_friendly_glow.mp4`,
check_video PASS (-14.2 LUFS). Animator's departure to judge: shot 1 is now a 1.75x close on Crinkle, Pip, the
hearts and the sun; Snip first appears at 12.5 s. A copy waiting in `Videos/` is named `DRAFT-in-review_...` (old
render; replace it only after gate 2 passes).

Paused at 05:40 on 7 Oct: the 5-hour limit was at ~85% (resets ~09:00 IST). Section 10.10 now lists every token
saver (no polling, check sheets, ask before a second render, stop above ~85%).

Next steps:
1. Lead: `get_usage`; view `reviews/ep11_friendly_glow_keys.png` at ~1,600 px, mainly 0-16 s (hearts, sunbeams,
   dusk, Pip hiding) and the 1.75x opening.
2. Neutral copy to `build/rv2/review_video.mp4`; a NEW fresh-eyes-reviewer, round 2. Pass: overall ≥8, no item
   below 7. If it fails, stop and give the owner a recommendation (no round 3).
3. Then stage 4 (the two Shorts), packaging, gate 3. Shorts due Sun 18 and Mon 19 Oct; episode Sat 24 Oct.

Waiting on the owner: turn on 2-Step Verification and phone verification (custom thumbnails); upload Ep 9 v3
(Thu 15 Oct) and Ep 5 v2 (Fri 16 Oct); the pilot story Short (Tue 20 Oct) and episode (Wed 21 Oct), text in
`reviews/pilot02_upload.md` (titles updated, moment first).

Notes: the whale Short was dropped by the owner (drafts in `Videos/` named "DRAFT-failed-review_…", don't upload).
The agent types load from `.claude/agents/` here and through links in `/Users/quantumair/copilot/.claude/agents/`.
