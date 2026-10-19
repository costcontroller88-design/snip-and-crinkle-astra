# Stage kit trial: the Ep 11 transformation Short on the kit (19 Oct 2026)

Kit: `episodes/stage_kit.py`, `tools/stage.py` (built 19 Oct; move test `reviews/stage_kit_move_test.md`). Trial per
`docs/stage_kit_proposal.md` section 6. Designer run: story-designer on Sonnet, 21 calls, 115k tokens; its table is
`reviews/ep11k_stage.md` and its notes, including every refusal, are in `reviews/ep11k_trial_designer.md`.

## Result: FAIL (stopped after the designer step)

| Criterion | Result | Evidence |
|---|---|---|
| (a) no measure round | **Met** | every row came from `stage.py`; nothing was measured (the designer ran 3 read-only `Sim` probes, which went around the tool) |
| (b) script ≤300 lines | Not run | no animator run (see "Why stopped") |
| (c) clearance and framing pass first time | **Fail** | `framing_check` failed shots 2 and 8 (Snip and Crinkle cut in VM@C) where `stage.py` had said PASS: a kit bug (a bespoke row skipped framing for everyone), fixed after the trial |
| (d) blind retelling matches the published Short | **Cannot pass** | the table drops Pip's turn, the nose, the smile, the second eye and every marker pass; gags 1-3 became a turn and hops |
| (e) a sheet in ≤4 agent runs | Not run | |
| (f) the designer step works on Sonnet | **Partly** | Sonnet used the tool correctly and logged every refusal; the story it could stage isn't the Short's |

**Why stopped.** The kit can't express this story, so an animator run and a blind review (about 8-10 more points) would
only confirm (d). Nothing was retired: section 5 waits for a passed trial and the owner's word.

## What the kit could not do (the designer's findings, checked)

1. **One floor prop with three friends around it.** With the lantern (240 u) on C, the work spots are Snip at 686 and
   Crinkle at 1276. Feet stay 10 u clear, and Crinkle's low round body counts as feet, so the pair spans 472-1551 u,
   wider than any vertical frame (1080 u). Shorts can't show both at the lantern. The old Short used depth instead:
   Crinkle stood behind the lantern.
2. **Reach.** From a work spot each friend reaches one lantern point: Snip eye_l, Crinkle eye_r. The nose and smile are
   out of reach for everyone, and Pip needs 153 u against a reach of 122. The rig has no lean or crouch move.
3. **Passing.** Crinkle and Pip have no hand-over pair: his round body stops him reaching low enough while their bodies
   stay 10 u apart. Snip and Pip pass at 295 u apart, Snip and Crinkle at 497. There is no "take" move.
4. **Order on the floor.** Nobody can pass anybody, so Pip, left of Snip, never reaches the lantern.
5. **Gag moves.** Sway, wiggle-dance, squeak, grin and bow aren't in the 16 moves. Two bespoke rows can't cover three
   gags plus the hand.

## Kit bugs the trial found (fixed 19 Oct, regress case "KIT trial bugs")

- The lantern's default hold box (100 u) raised every hand-over pass point above the reach. Now only props that can be
  carried count, and the lantern can't be picked up.
- A bespoke row skipped framing for everyone in its time span, so `stage.py` passed shots that `framing_check` failed.
  Now a bespoke row exempts only its own performer from the spacing and prop rules, never from framing. The kit and
  `framing_check` agree on `reviews/ep11k_stage.md`: 4 cuts each.

## Points (five-hour window)

| Step | Estimate | Real |
|---|---|---|
| Kit: 2 sets, 3 landscape and 3 vertical presets, 16 moves, `stage.py`, move test, 12 regress cases | 25 | about 17 |
| Trial: designer run (Sonnet) and the bug fixes | 10 | about 9 |
| **Total** | **35** | **about 26** (0% → 26%) |

## Recommendation (owner's decision)

Keep the kit. The landscape menu, spacing, framing, hops and walks work, and the move test passes: 173 moves accepted,
163 refused, 0 failed. Don't retire any check yet. Before a second trial, add three things to the kit:
(1) **depth for a floor prop**: a prop drawn in front, with feet allowed behind it, and the clearance sweep still
judging heads and paws; (2) **lean and crouch reach**, with the work points measured from them; (3) a **take** move,
plus sway and wiggle moves for gags. Then rerun this trial. If the owner would rather not, use the kit only on
landscape episodes that have no shared floor prop (Ep 12's playroom fits).

## Round 2: kit v2 (19 Oct 2026)

Kit v2 (commit 5591604, plus a fix commit with this record) works staging out instead of only refusing:
intent rows (`stage.py beat ep 0.6-2.8 Snip draw lantern.eye_l` writes the walk/turn, the pose `lean= sq=`
and a frame, or refuses with "nearest that work"), silhouettes from rendered masks, depth behind a front prop
(feet hidden; heads and resting paws 10 u), take, draw (stroke reveal), sway, wiggle, spin, bow, puff,
general hand-over pass points with lean/crouch (Crinkle-Pip), group-centred vertical frames (`VM@group`).
Tests: `stage.py test` PASS (267 ok, 237 refused, 0 failed of 504; the first runs found 4 kit bugs, all
fixed: arm over the lantern covered the chin, walking-feet allowance, low pass points, carried marker size,
now measured from its sprite); `regress.py` 149/149 (7 new v2 cases).

### Result: FAIL so far (stopped after the designer step: band SMALL AGENTS ONLY, 60-75%)

| Criterion | Result | Evidence |
|---|---|---|
| (a) no measure round | **Met** | every row through `stage.py`; no probes (designer log, `## Round 2` in `reviews/ep11k_trial_designer.md`) |
| (b) script ≤300 lines | Not run | the animator is outside the 60-75% band; waits for the reset |
| (c) clearance and framing first time | Not run | no full table |
| (d) blind retelling matches | **Not yet** | the table covers 0-5.6 s only (draw, the take across the lantern top, give-back, Snip sad) |
| (e) a sheet in ≤4 agent runs | Not met yet | 1 run, partial sheet `reviews/ep11k_sheet_r2.png` (3 stills) |
| (f) designer on Sonnet | **Partly** | Sonnet used the solver correctly; 25 calls, 9 refusals, stuck at 5.6 s |

**What blocked the designer (checked):** (1) after the take nobody could step away: a friend turning away from a close
pair fell back to the v1 spacing (488 u); fixed after the run (silhouettes 10 u apart are enough; regress 149/149).
(2) `new` refused `x:<n>` start spots; fixed. (3) Long solver chains took >120 s per call. Real limits the kit now
reports (not bugs): Pip can't draw the nose with her head 10 u clear of the lantern (her head is level with its top);
a friend can't idle at the lantern with a paw over it (step back after drawing); Snip and Crinkle at their lantern
work spots don't fit one vertical frame with the marker readable.

### Points (five-hour window)

| Step | Estimate | Real |
|---|---|---|
| Kit v2: solver, silhouettes, depth, 8 moves, group frames, tests (4 bug rounds) | 12-15 | **about 32** (28% → 60%) |
| Trial: designer run (Sonnet) + 2 fixes from it | 10 (whole trial) | **about 14** (60% → 74%), designer step only |

The kit estimate was about 2x low: the move test's renders found four bugs the arithmetic missed, and each round
re-rendered 504 cases. Nothing retired.

### Next (after the reset, a fresh session; about 15-20 points)
Re-run the designer from the existing 0-5.6 s table (the two fixes unblock 5.6-30 s); stage Pip's nose as a
nose-point gag or give the nose to Snip if the owner accepts the change; then the animator (`episodes/ep11k.py`
≤300 lines + sheet), `clearance_check`, `framing_check`, and a gate 1b blind check of the sheet.
