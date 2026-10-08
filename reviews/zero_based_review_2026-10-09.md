# Zero-based review of the agent team, 9 Oct 2026 (owner asked; v3.7 just applied)

Question asked of every part: "If we started today, would we build it this way?" Evidence: `reviews/mistake_log.md`
(M1-M52), `reviews/agent_ratings_2026-10-08.md`, `reviews/ep11_short_ledger.md`, blind scores, the six agent files.
Bias note: the Lead wrote v3.7 and grades itself here; every claim below cites a file or a number.

## The one result that matters
**0 of 5 videos have passed gate 2 since version 2** (Ep 11 rounds 1-3: 6, 6, 6; the Short: 7, 7; comedy 4-6 every
time; the Short shipped on the owner's overrule, M44). Versions 3.0-3.7 fixed compliance (overruns fell from 43/30
and 25/12 to 32/30 and 19/18; scripts now catch skipped checks) and tokens, but **no score moved**. The bottleneck
is the design of the story and the gags, and how numbers move between agents, not the number of rules.

## Finding 1: three agents own one plan's numbers (the costliest pattern)
The 30-second Short took 4 designer passes, 5 safety checks and 5 animator builds (ledger, 8 Oct): roughly 2M tokens
(estimate from the ledger rows; ~1.0M at the 8 Oct ratings plus the later rounds). The cycle: the designer writes
sizes and distances, safety sets limits on them, the animator measures and finds they can't be built, back to the
designer. Mistakes from this one hand-off: M26-M31, M34, M35, M38, M39, M40 (11 rows).
**Fix:** whoever measures owns the numbers. The designer writes the story card, the gag map, the beats and *intent*
("close-up ≥1.2 s", "lantern whole in frame"); the animator's feasibility stage turns intent into measured numbers
and renders the gate-1b storyboard in the same session; safety runs gate 1 once, on measured numbers. Plan cap
4,000 → 2,000 words.

## Finding 2: comedy is designed on paper and first tested after a full build
Gate 1b checks the problem, cause and lesson, not the jokes; lesson 12 says a storyboard match doesn't prove motion.
So every comedy failure was found at gate 2, after the most expensive step.
**Fix:** a gag test before the build: the animator renders each gag as a short low-resolution clip; a new blind
reviewer marks each LANDED or NOT (no story given). Only landed gags go into the build. Do it together with the rig
acting job (A2), because a stiff rig can't land a gag (`docs/LIMITATIONS.md` A2).

## Finding 3: effort is not matched to money
Shorts earn almost nothing and their feed time doesn't count toward the 8,000 hours (lesson 6), yet the Short got
the full pipeline and more tokens than a whole episode should. **Fix:** a Short gets no plan of its own (it is cut
from an approved episode's footage), one build and at most one fix round; long-form episodes get the full pipeline.

## Finding 4: the Lead's own rules were never dieted
v3.7 cut every agent file by 31-51%; the Lead's sections 1-12 (~300 lines) were untouched, and the Lead still has the
most mistakes (21 rows, 9 OPEN, M52 a repeat this session). **Fix:** the same diet for sections 1-12: ≤12 core rules,
the rest moved verbatim to a reference file, checked by `tools/diet_check.py`.

## Each agent, from scratch
| Agent | Keep? | Score now (8 Oct) | Evidence | Change |
|---|---|---|---|---|
| fresh-eyes-reviewer | Keep | 8 (8) | Never wrong on a story read; one possible over-call (M44) | None until the 14 Oct data calibrates it |
| safety-checker | Keep | 6 (7) | M35, M40: FIX numbers not measured; M45 overrun; gate 3 on the Short found nothing new | Gate 1 once, on measured numbers (Finding 1); re-checks only changed rows |
| animator | Keep, more scope | 6 (5) | Look 8; handover_check now holds; overruns M33, M39 | Owns all numbers + the storyboard + gag clips |
| story-designer | Keep, narrower | 4 (4) | Comedy 4-6 on all 5 videos; M34, M38, M43 since 8 Oct | Story, gags and intent only; plan ≤2,000 words |
| packaging | Keep | 6 (5) | 36k tokens, title_check PASS; one miss (M48) | None |
| growth-analyst | Keep, idle | 6 (6) | No real views yet | Until ~300 views, the Lead reads Studio in one step; the analyst does the monthly scan |
| Lead | — | 4 (4) | 21 mistakes, 9 OPEN | Finding 4 |
| **The system** | — | **4** | 0/5 gate-2 passes | Findings 1-3 |

No new agent: each one starts with no memory and re-reads files (lesson 9); the failures above are hand-offs and
untested comedy, which more agents would make worse.

## Recommendation (in this order)
1. **Finding 1 + 3 now** (pipeline text in section 8 and three agent files; small; rollback tag `agents-v3.7-pre-zbr`).
2. **Finding 2 with the A2 rig acting job** after the weekly reset (Tue 13 Oct); first used on Episode 12's Short.
3. **Finding 4** as its own small job.
**Test:** Episode 12: gate-2 pass in ≤2 rounds; comedy ≥7; ≤2 safety checks and ≤2 builds per video.
