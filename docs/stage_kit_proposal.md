# Stage kit proposal (design only, 19 Oct 2026)

**Problem.** Ep 12 took 4 rough scripts (2,374 lines), 3 restages, 19 agent runs (303 tool calls) and about 92
five-hour points, and gate 1 still failed. The framing and clearance mistakes (M26, M28, M34, M73, M74, M77) share
one cause: the plan invents x and zoom numbers, they fail when measured, and someone restages. **Fix: the plan only
picks from a fixed, pre-tested menu of sets, cameras, marks and moves,** so rows that break framing or clearance
can't be written.

## 1. Sets

| Set | Source | Fixed furniture (background, not clearance-checked) |
|---|---|---|
| Playroom | `episodes/ep12_rough.py` (FLOOR 1480) | toy box x 300-480, rug 560-1360, shelf 1440-1900 with 3 baskets |
| Porch | `episodes/props_porch.py` (2x, 3 light states) | railing and post drawn in front |

The park (`props_park.py`) comes later, after a port from the old 1x pipeline. All sets share the same marks.

## 2. Camera presets and marks

Computed from `tools/framing_check.py`: heights Snip 748, Crinkle 648, Pip 343 u; side extents with the pose
allowance 214/214, 264/275, 131/132; margin 10 u.

**Marks (x):** OFF_L −400 · WL 200 · A 300 · B 640 · C 960 · D 1280 · E 1600 · WR 1720 · OFF_R 2320.

| Preset | Windows (x; y) | Whole in at | Wholly out at | Forbidden (cut) |
|---|---|---|---|---|
| **Wide 1.0x** | W 0-1920; 560-1640 | all: A-E; Pip also WL, WR | all: OFF | Snip, Crinkle: WL, WR |
| **Medium 1.38x** | ML 0-1391, MR 529-1920; y 712-1495 | ML: A, B, C (Pip also WL). MR: C, D, E (Pip also WR) | ML: OFF, WR (Pip also E). MR: OFF, WL (Snip, Pip also A) | ML: Snip, Crinkle at WL, D, E; Pip at D. MR: Snip at B, WR; Crinkle at A, B, WR; Pip at B |
| **Close-up 2.0x** | CL 0-960, CR 960-1920; y 1000-1540 | Pip only: CL at WL, A, B; CR at D, E, WR | CL: OFF, D, E, WR. CR: OFF, WL, A, B | any other mark |

Two traps are built in. A 2.0x frame is 540 u tall, so it never holds Snip or Crinkle whole (M73); their faces go in
the medium. At 1.38x the strip beside a medium window is 529 u, narrower than Crinkle (539 u). So a big friend left
out of a medium stands on a wing or off stage, and no wide shot follows while they are there. (At 1.40x Snip would
have only 3 u to spare.)

**Spacing.** Marks are 320 u apart, but two standing characters need 355-499 u between centres; Snip at B and
Crinkle at C would overlap by 158 u. Rule: one empty mark between any two characters, except on a hand-over spot.
The kit computes those spots from each rig's shoulder and reach (Snip and Crinkle about 450 u apart, measured at
build; bodies clear at 416 u).

## 3. Move library (16 moves)

Built on `rig2.Perf2` (`walk`, `reach`, `to`, `emote`, `dart`, `hop`, `acting()`) and `rig2_pip.PipPerf`. Moves take
marks and slot names, never raw x, and are refused the moment a clearance rule fails.

| Move | Clearance built in |
|---|---|
| `enter`, `exit`, `walk_to(mark)` | refused if the swept footprint crosses a prop or a character; steps of 95 u x scale |
| `turn`, `look`, `nod`, `shake` | head turn clamped to ±0.5, the range the sizes were measured at |
| `react(emote)` | the 5 `EMOTES`, held ≥1.0 s |
| `hop` | wide only for Snip and Crinkle (20 u headroom in medium) |
| `pick_up(prop)` | the prop sits on the mark's reach slot; the holder's paw contact is allowed by the kit |
| `carry` (automatic) | fixed held offset, ≥10 u from the head, the scarf and the 90 u leg band |
| `put_down(slot)`, `drop` | the slot is clear of every footprint at that beat; never on the feet |
| `place_on(spot)` | fixed spots: box top, shelf, baskets |
| `hand_over(prop)` | only on a hand-over spot pair, facing; the prop passes at the midpoint |
| `point`, `hold` | arm capped at reach; A2 breath and auto blinks |

**Tested:** once, at kit build, every move is rendered at every mark for every character and run through
`clearance_check` and the framing arithmetic.

## 4. Workflow

**1. Story check first.** After the story card, the kit draws a 6-frame sheet of the key beats in seconds. The
blind retelling (gate 1b) runs on it before any shot plan exists, so a misread story (Ep 12's MISMATCH) costs one
small round, not a restage.

**2. One checked step at a time.** The designer builds the shot list through `tools/stage.py`, for example
`stage.py shot ep13 7 31.0-33.5 ML "Snip@B Pip@A Crinkle@WR"`. Each call writes the row or refuses with the legal
choices. Evidence: in [Authoring for Living Worlds](https://arxiv.org/abs/2604.10383) (2026), agents limited to
checked tools wrote 20 of 25 working plans on a budget model; a flagship model with written rules wrote 0 of 50.
"Measured checks" keeps only off-kit items, so there is no measure round.

**3. A cheaper designer.** The designer runs on Opus. Once the tool enforces the rules, the trial runs it on Sonnet.

**Animator.** One `episodes/epNN.py`: the beat table `stage.py` wrote, plus any bespoke gag code. A restage edits
rows. Expect about 300 lines instead of 2,374.

## 5. Retire after a passed trial

- **MASTER_PROMPT:** designer rules 3 and 5, animator rule 1 (measure first) and safety rule 3 (a FIX with a
  number) apply only to bespoke beats. Otherwise a FIX names a mark, slot or move.
- **Tools:** `framing_check.py` becomes the kit's test; the `gate.py` M77 refusal becomes a kit PASS.
- **Hooks:** the "feasibility only" stage budget goes (M67, M79); `return_check` "estimate" send-backs (M71) fire on
  off-kit rows only.
- **Kept:** one full clearance sweep at the final build, and the blind review. Passing checks isn't the same as
  working: in an [ICAPS 2026 demo](https://icaps26.icaps-conference.org/files/demos/icaps26-demo_paper_12.pdf),
  plans that passed every check worked only 73% of the time.

**Saving, estimated from `agent_runs.md` (Ep 12).** About 13 of the 19 runs were measure, picks or geometry-fix
rounds. With the kit: about 4 runs to gates 1 and 1b (designer about 10 calls, sheet 15, safety 14, reviewer 6),
plus one story-fix round of about 4 runs. **About 8 runs and 85 calls instead of 19 and 303: roughly 11 runs, 200
calls and 60 five-hour points saved per episode.** It rests on one episode; the trial must confirm it.

## 6. Risks and trial

| Risk | Mitigation |
|---|---|
| Story bent to fit the kit | ≤2 bespoke beats per episode on the old measure path |
| No big-friend face close-up | reactions in medium; a tested face crop later |
| Box arithmetic misses odd shapes | the final clearance sweep |
| Size drift (new scale, crouch) | marks derived from `framing_check.sizes()` at import, so they fail loudly |
| Vertical Shorts | the trial derives vertical windows the same way |
| Build cost | about 2 animator runs, about 25 points, once |

**Trial: rebuild the Ep 11 transformation Short** (porch, 30 s, 1,298 lines, 7 fix files, 4 marker hand-overs) with
the kit only. Criteria: (a) no measure round: every designer step is settled by `stage.py`; (b) script ≤300 lines;
(c) `clearance_check` and `framing_check` pass first time; (d) the blind retelling matches the published Short;
(e) a sheet in ≤4 agent runs; (f) the designer step also passes on Sonnet.

## Go/no-go for the owner

| Decision | Call | Cost | Gain |
|---|---|---|---|
| Build the kit (2 sets, 3 presets, 16 moves, `stage.py`, move test) | **GO** | about 25 points, once | framing and clearance mistakes can't be written |
| Trial on the Ep 11 Short | **GO** | about 10 points | proof against a 7-fix-file baseline |
| Retire the section 5 items | **Only if (a)-(e) pass** | 1 Lead round | about 11 runs and 200 calls per episode |
| Designer on Sonnet | **Only if (f) passes** | none | cheaper planning every episode |
| Park set | **Later** | 1 build run | a third set |
| Ep 12 on the old path | **NO**: pause, then restage on the kit | none | avoids a 4th old-path restage |

**Recommendation: GO on the build and the trial. Retire checks based on the trial numbers, not this estimate.**

## Built and trialled (19 Oct 2026)

Built as designed: `episodes/stage_kit.py` and `tools/stage.py`, with `framing_check` reading vertical windows and
`clearance_check` taking the kit's holder-paw allowances. The landscape presets reproduce the table in section 2
exactly. Measured at build: hand-over pairs Snip-Crinkle 497 u apart (pass at y 1282), Snip-Pip 295 u (y 1368),
Crinkle-Pip none. The porch blocks E, WR and OFF_R (off the deck). The move test passes: 173 moves accepted,
163 refused, 0 failed of 336. **Trial: FAIL** (`reviews/stage_kit_trial.md`): (a) met; (c) failed on a kit bug, since
fixed; (d) can't pass, because the kit can't put three friends around one floor prop, reach its far points, or pass
between Crinkle and Pip. Nothing in section 5 is retired. Next step for the owner: add depth for floor props,
lean/crouch reach and a take move, then rerun the trial.
