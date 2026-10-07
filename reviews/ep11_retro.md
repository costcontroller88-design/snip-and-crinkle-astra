# Episode 11 retro: what changed in the agent files, and why (8 Oct 2026)

Source: `reviews/ep11_retro_notes.md` (ledger, findings 1-14, mistakes, owner requirements, coverage review).
Rollback: `git checkout agents-v2-pre-retro -- MASTER_PROMPT.md && python3 tools/build_agents.py`.

## Result of the test case
Episode 11 failed three blind rounds at overall 6 (round 3: comedy 5; blocking: no visible light source for the
hearts 0-14 s, the carving hidden under the hand 88-90 s). The owner paused it (8 Oct) and asked for the retro first.
Spend logged for the round-3 work: ~1.66M subagent tokens (animator ~1.23M = 74%), ~5 Lead hours.

## New findings from round 3 (added to the notes' 14)
15. **Soft caps are ignored:** "feasibility ≤5 tool calls" took 22; the video review took 55 calls / 119k (the
    storyboard checks 7 calls / 17-19k). Caps need a hard limit in the file (`maxTurns`) and a stated budget.
16. **A storyboard MATCH doesn't prove the video reads:** gate 1b matched on the cause (sb3), but in motion the
    reviewer saw no light source. The Lead's key sheet labelled "2.5 s sunbeams through the railing hearts" and the
    Lead passed it, though no beam was visible at 1,600 px.
17. **The plan drifted from the accepted angle** (ROADMAP: "friendly glow, not pumpkin carving") into a grown-up
    carving, which set safety (don't show cutting in detail) against clarity (show the key action): blocking 2.
18. **Comedy was never checked before the video:** 5-6 in every round; the gag map was only a plan table.
19. **Fix rounds hit a ceiling:** rounds 1-3 all scored 6. Fixes removed misreads but couldn't add what the design
    lacked (lesson 8 again, for whole episodes).

## Mistakes → rules (each in one place only; the rule budget below)
| Mistakes | Rule or check | Where |
|---|---|---|
| A1, A3, A6, A7 (check claims without proof) | **Evidence rule:** every claimed check carries a still's path or a measured number from a script; no evidence = "not checked" | Rules card (all agents) |
| A7, 15 (caps overrun) | Tool-call budget per stage in each file + a hard `maxTurns`; at the cap, stop and report | Rules card + frontmatter |
| A5, D1, S1 (infeasible fixes) | **Feasibility pass:** any fix list gets a "can each line be built? numbers" pass in ≤5 calls before building; designers and safety read real positions from the code | animator, story-designer, safety-checker |
| A2 (stale reused frames) | No reuse of rendered frames across rounds unless the shot's code is unchanged (checked, e.g. a hash) | animator |
| A3, A4, 13 (fix applied in one place) | A still at every time a change touches, listed fix by fix | animator |
| A1, 16 (key sheet blind spots) | **Key sheet from the changes:** every changed shot + its boundaries + the fixed beats; the Lead treats any label it can't see at 1,600 px as a build miss | animator + Lead pre-flight |
| D2, 17 (plan sets up a wrong reading / leaves the angle) | The story card quotes the accepted ROADMAP angle; any departure is flagged first in the return. Safety-hidden key actions get a staged before/after (a cutaway with a clear sound), planned, not left to the build | story-designer, safety-checker |
| 18 (comedy unchecked) | The storyboard includes the 2 strongest gags; the storyboard reviewer lists which frames look funny | story-designer, fresh-eyes-reviewer |
| 5 (several fix files) | One source of truth: after each round the designer folds fixes into the plan (or one cumulative fix file) | story-designer |
| S2 (knife read missed) | Gate 3 looks at frames around every hazard and cutting scene (props near hands) | safety-checker |
| 19 (plateau) | If a round scores the same overall as the last, stop fixing: the owner decides (redesign, salvage or drop) | MASTER_PROMPT 8 |
| L1, L2, L5, L6, L7, L8, L9 (Lead) | **Lead pre-flight checklist** (≤10 lines): one Lead only, usage bands, route by kind, designer picks frames, proof for every exception, ≤3 code steps, HANDOFF word count | MASTER_PROMPT 10 |
| L3, L4, 1, 10 (pricing) | Real prices from the ledger; the animator codes, the Lead renders in one background command | MASTER_PROMPT 8, 10 |

## Token checkpoints
- The Lead runs get_usage before every spawn and after every return and logs both limits in a ledger row.
- **Bands (5-hour limit):** <60% anything; 60-75% small agents only (reviewer, safety, designer, packaging);
  75-85% no agent, save and commit; >85% stop until the reset. **Weekly:** above the even pace (days used / 7 + 10
  points), small agents only.
- **Budgets per stage** (tool calls; hard cap `maxTurns` a little above): see each agent file.

## Rule budget
Each agent file has a word cap (its size on 8 Oct + 10%, the rules card counted once); a new rule merges or replaces
an old one. Yardstick for the next episode (coverage review 1): gate 1b in 1 round, gate 2 in ≤2, animator ≤50% of
the spend, ≤1 claim without evidence, one episode ≤1 full 5-hour window. Compare after it; keep, change or roll back.
