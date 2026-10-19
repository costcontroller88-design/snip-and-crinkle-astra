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
