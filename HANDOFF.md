# Handoff: read this first (updated 2026-10-07)

How we work (rules, the agent team, the pipeline, the token budget): `MASTER_PROMPT.md` (version 2). Plan, dates and
the upload calendar: `docs/ROADMAP.md`. Code index: `docs/TOOLKIT.md`. History (Episodes 1-10, setup): `docs/HISTORY.md`.

**Current phase: 0 (foundations, to 19 Oct); Phase 1 starts 20 Oct. Step: work package "Episode 11" (Pip and the
Friendly Glow), gate 2. Next work package: the Lead checks the new key sheet, then blind review round 2 (the last).**

Done: plan, gate 1, stages 1-3. Blind review round 1 (`reviews/ep11_blind_r1.md`): overall 6; the opening
was misread (hearts too small, dusk too subtle, Pip's hide too quick), a loud sting at 28 s, few gags 32-80 s. The
Lead's fix list `reviews/ep11_fixes_r1.md` (B1-B3, P1-P7) is applied and re-rendered: `output/ep11_friendly_glow.mp4`,
check_video PASS (-14.2 LUFS). Animator's departure to judge: shot 1 is now a 1.75x close on Crinkle, Pip, the
hearts and the sun; Snip first appears at 12.5 s. A copy waiting in `Videos/` is named `DRAFT-in-review_...` (old
render; replace it only after gate 2 passes).

Blind review round 2 (`reviews/ep11_blind_r2.md`): overall 6 again (hook 6, clarity 6, comedy 6, lesson
6; sense, wow, look 8). Same misread as round 1: in 0-17 s Crinkle's paw on his pumpkin in the foreground and Snip
pointing at him read as "Bear won't share", outweighing the faint hearts. The rule allows two rounds, so the Lead
stopped and asked the owner. Lead's recommendation: one structural fix of 0-31 s (Crinkle and the pumpkin out of
Pip's opening; Snip points at the dark wall; stronger gold hearts; shorter 16-31 s) and the comedy beats (62 s
sit-down reads, the stray marker removed, one gag near 44 s), then one final round 3, after the 09:00 limit reset.

The owner approved round 3 (final). **Done 7 Oct evening:** fixes_r2 applied in code; storyboard checks sb2
(cause only guessed) and sb3 (**gate 1b MATCH**: problem, cause, lesson; `reviews/ep11_storyboard_blind_sb3.md`);
further fixes in `reviews/ep11_fixes_sb2.md` (opening: the sun sinks in the same shot as the fading hearts; 133 s
wonder faces + light cone; Safety R1 carry = 7 slow steps; carry restage 32-43 s, closest 170 units). Safety
re-check PASS with R1 (`reviews/ep11_safety.md`).
**Next (after the 23:20 IST limit reset):** resume or brief the animator: build the "Carry restage" section of
fixes_sb2 (shot-11 camera (1100, 1200); Snip and Pip drawn in front of the pumpkin 41.7-43.5 s); give Snip's
marker a coloured body at 133 s (a white one read as a knife); then the 3x hires pass (`EP11_RES=3 ... --hires`),
one full render, check_video, key sheet. Then the Lead checks the key sheet, makes `build/rv3/review_video.mp4`,
and a NEW fresh-eyes-reviewer does round 3 (final).

**Owner request (7 Oct):** once Episode 11's final blind round is done, treat the build as a test case: a retro
from `reviews/ep11_retro_notes.md` (token ledger + findings, kept as we go), then sharpen the agent files (Appendix A,
`tools/build_agents.py`) for better results and lower token use.

Channel data: 2 Shorts live (5 and 6 Oct); Studio on 7 Oct showed only the owner's own views. Checkpoint Wed 14 Oct:
Shorts feed reach, logged in `docs/analytics-log.md` (the owner is signed in to Studio in the built-in browser).

Waiting on the owner: turn on 2-Step Verification and phone verification (custom thumbnails); upload Ep 9 v3
(Thu 15 Oct) and Ep 5 v2 (Fri 16 Oct); the pilot story Short (Tue 20 Oct) and episode (Wed 21 Oct), text in
`reviews/pilot02_upload.md` (titles updated, moment first).

Notes: the whale Short was dropped by the owner (drafts in `Videos/` named "DRAFT-failed-review_…", don't upload).
The agent types load from `.claude/agents/` here and through links in `/Users/quantumair/copilot/.claude/agents/`.
