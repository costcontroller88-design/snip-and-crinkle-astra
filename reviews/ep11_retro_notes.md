# Episode 11 retro notes (test case for retraining the agents; owner request 7 Oct)

Running log, filled as the build goes; the retro after the final blind round turns it into agent changes.
Token cost = subagent tokens from each return; "limit" = 5-hour limit % before -> after.

## Ledger (7 Oct, round-3 work)
| Step | Agent | Tokens | Tool uses | Time | Limit | Result |
|---|---|---|---|---|---|---|
| Storyboard sb2 (applies fixes_r2 in code + 12 stills) | animator | 354k | 70 | 43 min | 5 -> 32% | Built; flagged one infeasible fix (pumpkin out of shot at x 960) and moved it |
| Blind storyboard check sb2 | fresh-eyes-reviewer | 19k | 7 | 1 min | ~0 | Problem + lesson match; cause only guessed; "Bear won't share" gone |
| Fix mode after sb2 | story-designer | 53k | 16 | 3 min | 32 -> 36% | fixes_sb2.md, 9 re-check frames |
| Safety re-check of restaged shots | safety-checker | 25k | 8 | 0.5 min | ~1% | PASS + one fix (pumpkin carry, never checked) |
| Storyboard sb3, attempt 1 | animator (new) | 272k | 46 | 29 min | 36 -> ? | No sheet: 3 fixes infeasible (beams behind Pip's head, 144 s wing reach, 830-unit carry vs "3 steps"); built the 130-133 s fixes |
| Storyboard sb3, resumed with Lead decisions | animator (resumed) | 208k | 13 | 10 min | 57 -> 64% | Sheet done; 2 issues left (144 s wing overlap, carry path crossing at 36.8 s) |
| Blind storyboard check sb3 | fresh-eyes-reviewer | 17k | 7 | 1 min | ~0 | MATCH on problem, cause, lesson; side risk: Snip's white marker reads as a knife (133 s) |
| Fix mode: carry path 32-43 s | story-designer | 78k | 15 | 9 min | 64 -> 71% | Restage, closest 170 units; computed from the real code positions |
| Final code (carry, marker colour), no render | animator (resumed) | 236k | 17 | 4 min | 71 -> ? | Code done; returned exact commands; render run by the Lead in one background job |
| Render chain (hires + render + check + keys) | Lead (Bash, background) | ~0 | 1 | 42 min | 0 | check_video PASS -14.2 LUFS; the key sheet showed 4 build misses |
| Lead diagnosis + 3 small code fixes + 2 stills | Lead | ~10 steps | | 20 min | 79 -> 81% | camera and reuse fixed; 2 misses left for a fresh animator |

## Findings so far (candidate agent changes)
1. **Gate 1b cost estimate was wrong:** MASTER_PROMPT says ~3% of a 5-hour limit; the first sheet cost ~27%,
   because "storyboard" meant applying all staging fixes in code and rendering stills at 2x/3x. Either price it
   honestly or make the storyboard pass cheaper (fewer tool rounds, fewer self-viewed frames, lower-res stills).
2. **The Lead bypassed routing:** fixes_r2 (a staging fix) was written by the Lead, not the story-designer. Result:
   one infeasible placement (found by the animator) and a new action (the pumpkin carry) that no safety check saw.
   Rule exists (section 8); enforce it in the Lead's own checklist.
3. **The Lead picked the storyboard times** and left out the lesson beat. The designer should always pick them
   (plan section 10 / fix files), and the sheet must include the lesson beat.
4. **The blind storyboard check is cheap and sharp** (19k tokens): it found the real remaining gap (cause not in the
   same shot as the feeling) and three side misreads (sleepy eyes, fear faces, a phantom lamp).
5. **Small agents are cheap** (designer 53k, safety 25k, reviewer 19k); the animator is ~85% of the spend. Where the
   animator's tokens go is the main lever (code reading, render waits, frames viewed).
6. **Fixes written without the rig numbers fail at build time:** fixes_sb2 asked for beams, a 40-unit reach and a
   3-step carry that the geometry can't give; found only after 272k animator tokens. A cheap feasibility pass (the
   animator answers "can each line be built? numbers" in a few tool calls) before the full storyboard build, or the
   designer reading the rig numbers (positions, sizes) before writing a fix.
7. **Safety fixes need the same feasibility check:** R1's "at most 3 steps" didn't fit an 830-unit carry.
8. **Resuming a big agent is expensive per step:** 208k tokens for 13 tool uses (~16k per step, its context
   re-sent each time). Fine for a short finish; for a long job, a fresh agent with a short fix file.
9. **Prop colours carry safety meaning:** a plain white marker near a cutting scene reads as a knife. Markers keep
   a coloured cap/body in every shot after the hand cuts.
10. **Split "code" from "render" (owner's question, 7 Oct):** the render costs no tokens, but the agent around it
    does. The Lead nearly waited 3 h for a reset by pricing "build + render" as one agent job. Better: the animator
    codes and checks stills, returns the exact commands, and the Lead runs the render as one background command
    (notified on exit, zero polling). Candidate rule for the animator file and section 10.
11. **The Lead's key-sheet look paid for itself:** it caught 4 build misses (Snip in the opening camera, gold
    cut-outs after sunset, stale reused 40b frames, a white "knife" marker) before the final blind round.
12. **Never reuse rendered frames across rounds** after any staging change; the animator's "nothing there changed"
    was wrong. Reuse only with a check that the shot's code is unchanged (e.g. a hash of the shot's inputs).
13. **"Applied" needs a still at every time the change touches**, not one: the marker went blue at 133 s only.
14. **The Lead fixing code is a false economy past ~3 steps:** each Lead step re-sends ~170k; diagnosis is the
    Lead's job, the fix belongs to a fresh animator with a short fix file.
