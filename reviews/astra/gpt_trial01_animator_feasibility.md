# Animator source audit — feasibility only

**Decision: a narrow implementation is plausible, but the 240–360-second episode and two Shorts are not yet measured or build-ready.** The simpler candidate—ball always visible, a misplaced toy interrupts shared play, toys return to visible homes, play resumes—avoids the old cushion/search/rope mechanics. It still needs explicit prop ownership, placement and ball-motion contracts.

Audit scope: `costcontroller88-design/snip-and-crinkle-astra` at `0cdcca812c5abf39d9a3bb5854b6c3fc1074ac7a`, read-only through GitHub. No commands, renders, geometry measurements or checks ran. No clarity, safety or technical verdict is issued.

## Source facts and limits

| Item | Supported by inspected source | Unsupported or missing | Unmeasured here |
|---|---|---|---|
| Existing episode | `reviews/ep12_plan.md` specifies **140 seconds**. `ep12_rough_r3.py` describes itself as remeasurement, “not the episode.” | A continuous 240–360-second implementation | All new timing and geometry |
| Rough entry point | r3 imports r2 and patches earlier drawing functions. Its CLI offers `--sheet`, `--still`, `--measure`, `--final`. | Audio, production rendering and full `--check` entry point | Rough execution |
| Continuous movement | r3 `frame(T_)` handles a time interval plus exact times such as 17.5, 36.6 and 38.8, otherwise delegating to r2 | Treating snapshot branches as verified continuous animation | Interstitial motion and cut boundaries |
| Stage kit | `Stage.load`, `Stage.draw`, `Stage.still`, camera presets, existing rigs, reach, carried ownership, pickup, handover and placement | Complete tidying-specific scene semantics | Legal placements for this candidate |
| Registered props | `PROPS` contains **marker, ball, block, lantern** | Picture baskets and actual tidying toy registrations | Their masks, grip offsets and sizes |
| Playroom | `Set.background` reuses `ep12_rough.background()`; playroom spots include shelf positions | A verified vertical playroom background; basket interior/completion state | Vertical crop coverage |
| Placement | `place_on` reaches a named set spot and transfers a prop there halfway through the beat | Container insertion, rim occlusion, filled-home bookkeeping | Whether existing placement suffices visually |
| Ball roll/contact | No `roll` or ball-contact move appears in `MOVES` | A checked ball-roll/contact primitive | Contact, stopping and clear-lane replay |
| Selective rendering | `shot_render.render/encode` implements content keys, frame verification, atomic completion and continuous WAV encoding | Automatic slicing of stage state or dependency inference | Episode-length cache adoption |
| Two Shorts | Vertical presets and safe-zone tools exist | Two implemented cuts with complete context and endings | Framing, audio, timing and final files |

The old plan’s optional story-Short segment list totals **59.8 seconds**, despite its “55 s” label. It is not a locked second Short.

## Smallest engineering sequence

1. **Freeze the simpler causal sequence and its two Short extracts.** Allocate 240–360 seconds through additional visible play/put-away/application beats, not a global stretch of the 140-second rough. Declare shot boundaries, key actions and neutral-sheet moments. Preserve the failed old revision as lineage.

2. **Create one new production episode entry script.** Use `Stage.load(...)`, `Stage.draw(...)`/`still(...)` and `SK.export(...)`, retaining existing rigs and render infrastructure. Do not turn the r3 monkey-patched measurement CLI into the production renderer. Expose the standard `render_world(t,d,cam,bg)`, `make_buses()`, `--still`, `--keys`, `--cuts` and complete `--check` interfaces.

3. **Add only the episode’s prop registrations and fixed home locations.**
   - Reuse selected existing toy artwork through small `Prop` adapters with accurate dimensions, carry boxes and draw functions.
   - Register a few fixed picture baskets or open home trays at reachable locations.
   - Prefer visible open homes where `place_on home_slot` suffices. This avoids a general container system.
   - If baskets must hide toys, add a small episode-local placement state: held → visible crossing of rim → stored. Draw the front rim after the toy. Preserve unique ownership and deterministic stored positions.
   - Ensure the picture identifying each home is readable; do not substitute textual labels.

4. **Implement one reusable episode-local ball path.** Declare start, release, contact and stop, with a visible source of motion. Reuse the same lane for the blocked and cleared demonstrations. A fixed toy obstruction must stop the ball, not a walking character. This can be one bounded bespoke action family; do not introduce a general physics engine. The kit limits bespoke beats to two and exempts their performer from some spacing rules, so explicit checks remain necessary.

5. **Prototype the two semantic risks before the whole timeline:** ball contacts the misplaced toy; toy visibly reaches its matching home. Then compose pickup, carry, placement, looks and reactions from existing moves. Avoid shelf lifting, cushion draping, rope towing, blind carrying and falling toys unless separately justified by the revised design.

6. **Add the shot-cache adapter after the renderer is deterministic.** Use consecutive integer drawing ranges at 15 drawings/s. Declare camera, seed, beat data, incoming performer state, prop ownership, home occupancy and ball state in every shot contract. Hash entry code, imports, stage data, prop art, fonts and external/generated assets. Materialize downstream state after edits; duration changes invalidate later absolute drawing ranges. Keep shot-local edits in configuration rather than shared Python constants.

7. **Render a clean/cached comparison before adoption.** Reuse drawings for audio-only edits, but encode one continuous master WAV again. Re-film two marked sequences vertically with their own context, ending, music and remapped sound effects. Reusing a performance does not imply that landscape frame PNGs can serve a vertical camera.

## Geometry and implementation acceptance

All items below are future acceptance requirements, not observed results:

- Every shot boundary and motion extremum: heads, ears, tuft, paws and key props remain correctly framed; key actions meet the measured size/duration requirements.
- Every active drawing: ownership is unique; release and acquisition are continuous; visible contact causes ball stopping; no teleportation, foot sliding or unsupported resting positions.
- Pickup/placement: measured posed reach, carried-prop silhouette, face clearance, clear walking corridor and no body entry into homes.
- Ball demonstration: unobscured contact and sufficient visible lane before/after; ball never needs a hazardous person/toy collision to explain the problem.
- The whole 240–360-second timeline receives clearance coverage. Sheet-time exports alone are insufficient. Review `CLEARANCE_ALLOW` entries; broad holder/front-prop allowances must not conceal unintended contact.
- Vertical versions receive their own safe-zone evidence for each key object: bottom 19%, and right 12% over the specified middle/lower region.
- Existing r3 close-ups of **2.84× and 2.2×** cannot silently carry into a standard 2× production render. Restage within 2× or explicitly raise the relevant shot’s render scale.
- Each gag receives measured drawing-by-drawing timing and a visible reaction; sound accent one drawing after visual accent. A long episode needs additional developed beats, not static holds beyond six seconds.
- Cache tests must show: unchanged repeat draws none; a genuinely independent shot edit redraws only that shot; changed incoming state invalidates dependents; camera/seed/assets invalidate correctly; clean and cached frames agree; final audio remains continuous.
- Final checks and independent reviews attach to exact source/media revisions. Stop on any unsupported movement, unexplained exception, stale evidence or failed dependency/equivalence test.

## Runtime evidence

The recorded stage-rig cache experiment was **0.6 seconds, three shots, nine drawings**:

| Recorded case | Drawing/cache time | Redrawn drawings |
|---|---:|---:|
| Cold | 23.1297 s | 9 |
| Warm | 0.0098 s | 0 |
| Middle-shot edit | 7.4248 s | 3 |
| Clean edited rebuild | 15.0893 s | 9 |

These exclude final encoding and include unequal warm-up conditions. **They do not support an episode runtime forecast.** Cache misses are serial; cold rendering can be slower than the established multiprocess renderer.

`TOOLKIT.md` provides an approximate historical **3.5 rendering seconds per landscape video second on eight cores**. Applied arithmetically, that is **14–21 minutes for 240–360 seconds**, only as a rough planning allowance for a comparable conventional render. The same source’s “about 11 min for 160 s” is not exactly consistent with that rate. Neither figure predicts new scene complexity, the serial adapter, full checks, editing, sound production or vertical Shorts.

No defensible total package ETA is established. Measure a representative production shot and the complete cache adapter before committing one. The reported 22.9% stage-gap microbenchmark improvement is local arithmetic optimization, not a full-build speedup.

## Failure lineage and stops

- Gate 1b round 1: **MISMATCH**; the ball was absent from the retelling.
- Gate 1b round 2: **MISMATCH**; deliberate hiding was inferred and the reveal was not understood.
- **F8 remains unresolved in the old revision:** Crinkle foot/leg-to-cushion-and-drum clearance required ≥30 design units over 36–43 seconds; the recorded ~25-pixel observation was an estimate.
- Removing that action in the new candidate can make F8 inapplicable to the new staging only after source mapping and replacement evidence. It does not retroactively close the old failure.
- The revised design requires new measured coverage and independent review. No silent third round, erased attempt count or inherited approval.
- If ordinary pickup/placement cannot be made legal, choose a simpler home location or return the movement to design; do not weaken thresholds or expand bespoke exemptions.

## Sources and audit accounting

Pinned source references: [rough r3](https://github.com/costcontroller88-design/snip-and-crinkle-astra/blob/0cdcca812c5abf39d9a3bb5854b6c3fc1074ac7a/episodes/ep12_rough_r3.py), [stage kit](https://github.com/costcontroller88-design/snip-and-crinkle-astra/blob/0cdcca812c5abf39d9a3bb5854b6c3fc1074ac7a/episodes/stage_kit.py), [shot renderer](https://github.com/costcontroller88-design/snip-and-crinkle-astra/blob/0cdcca812c5abf39d9a3bb5854b6c3fc1074ac7a/episodes/shot_render.py), [recorded cache trial](https://github.com/costcontroller88-design/snip-and-crinkle-astra/blob/0cdcca812c5abf39d9a3bb5854b6c3fc1074ac7a/reviews/astra/07_selective_rendering.md), [ledger](https://github.com/costcontroller88-design/snip-and-crinkle-astra/blob/0cdcca812c5abf39d9a3bb5854b6c3fc1074ac7a/reviews/ep12_ledger.md), [safety lineage](https://github.com/costcontroller88-design/snip-and-crinkle-astra/blob/0cdcca812c5abf39d9a3bb5854b6c3fc1074ac7a/reviews/ep12_safety.md).

Accounting: **8 `functions.exec` batches**, containing **27 GitHub read requests**, plus one parent status message. One guessed render-log path returned 404; one requested safety line range was empty and then corrected. Token telemetry unavailable. `return_check`, `handover_check`, measurements and all renders were **not run**.

**Mistakes:** batching stayed within eight orchestration calls but exceeded eight if the budget counts individual GitHub requests; this distinction must remain explicit.

```json
{"agent":"animator","verdict":"PARTIAL","tool_calls":27,"budget":8,"checks":[{"name":"source feasibility audit","evidence":"Pinned source inspection only; no execution evidence"}],"files":[],"not_done":["Geometry measurements","Implementation","Storyboard review","Full-length rendering","Two Shorts","Cache production equivalence","Technical and independent gates","return_check"],"orchestration_batches":8,"parent_status_messages":1,"token_telemetry":"unavailable"}
```
