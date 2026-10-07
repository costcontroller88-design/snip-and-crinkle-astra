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

Blind review round 2 (`reviews/ep11_blind_r2.md`): overall 6 again; the same misread ("Bear won't share") in
0-17 s, so the Lead stopped and asked the owner.

The owner approved round 3 (final). **Done 7 Oct evening:** fixes_r2 applied in code; storyboard checks sb2
(cause only guessed) and sb3 (**gate 1b MATCH**: problem, cause, lesson; `reviews/ep11_storyboard_blind_sb3.md`);
further fixes in `reviews/ep11_fixes_sb2.md` (opening: the sun sinks in the same shot as the fading hearts; 133 s
wonder faces + light cone; Safety R1 carry = 7 slow steps; carry restage 32-43 s, closest 170 units). Safety
re-check PASS with R1 (`reviews/ep11_safety.md`).
**Done 21:01:** final code built and rendered (`output/ep11_friendly_glow.mp4`, check_video PASS -14.2 LUFS), but
the Lead's key-sheet look found 4 build misses; 2 fixed by the Lead (uncommitted code is committed).
**Next (after the 23:20 IST reset):** a NEW animator with `reviews/ep11_fixes_r3pre.md` (code + stills only, returns
the commands); the Lead runs the render chain in one background command (zero polling), looks at the key sheet,
makes `build/rv3/review_video.mp4`, then a NEW fresh-eyes-reviewer, round 3 (final). Then the retro (below).

**Owner request (7 Oct):** once Episode 11's final blind round is done, treat the build as a test case: a retro
from `reviews/ep11_retro_notes.md` (token ledger + findings, kept as we go), then sharpen the agent files (Appendix A,
`tools/build_agents.py`) for better results and lower token use: the mistake log, token checkpoints, and the model and effort per task (requirements at the end of the retro notes).

Channel data: 2 Shorts live (5 and 6 Oct); Studio on 7 Oct showed only the owner's own views. Checkpoint Wed 14 Oct:
Shorts feed reach, logged in `docs/analytics-log.md` (the owner is signed in to Studio in the built-in browser).

Waiting on the owner: turn on 2-Step Verification and phone verification (custom thumbnails); upload Ep 9 v3
(Thu 15 Oct) and Ep 5 v2 (Fri 16 Oct); the pilot story Short (Tue 20 Oct) and episode (Wed 21 Oct), text in
`reviews/pilot02_upload.md` (titles updated, moment first).

Notes: the whale Short was dropped by the owner (drafts in `Videos/` named "DRAFT-failed-review_…", don't upload).
The agent types load from `.claude/agents/` here and through links in `/Users/quantumair/copilot/.claude/agents/`.
