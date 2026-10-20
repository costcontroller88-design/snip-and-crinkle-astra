# Production pipeline and the path to 10/10

Decision: 20 October 2026, following the owner's request for all seven rows to
reach 10/10. Keep the existing six roles, rig, stage kit and independent gates.
Improve the system around those assets. A score is earned by observed outcomes;
implementation tests are not substitutes for production evidence.

## What 10/10 means

These are acceptance criteria chosen before new results, not forecasts. The
master prompt's per-episode targets remain unchanged. Ten means those targets
are demonstrated consistently, including failure handling and reproducibility.
Use three consecutive complete production packages as the reliability trial;
preserve every failed attempt and round in the denominator. Do not cherry-pick.

| Row | Acceptance for a 10/10 workflow rating | Evidence still needed |
|---|---|---|
| Storyboard understanding | Three consecutive first-round matches on problem, cause and lesson; declared moments covered on the actual sheet | Fresh blind retellings and separate comparisons with cards |
| Video story clarity | Episode and both Shorts score at least 8 overall and clarity within two rounds in each of three packages; calibrated independent reviewers | Neutral videos, original reports, reviewer identities, rounds and timestamps |
| Safety readiness | Gates 1 and 3 pass without structural fixes on all three packages; sources current; all hazard-specific restrictions respected | Independent safety reports bound to exact plan/video/package revisions |
| Technical readiness | Final episode and two Shorts pass video, loudness, silence, framing, clearance and regression checks in each package; failures and stale evidence demonstrably block acceptance | Full-length final files, raw check logs, input/code hashes; no waived failures |
| Delivery speed | Each of three paragraph-to-episode-plus-two-Shorts packages completes within 48 elapsed hours and at most two full build rounds | Start/end timestamps, all attempts, render minutes, agent calls and measured token/usage counters |
| Selective re-rendering | Shot-local fixes redraw only affected shots, repeat runs redraw none; clean and cached output pixels agree; dependency/camera/seed changes invalidate correctly; final audio remains continuous | Automated negative tests plus real multi-shot production trials and render receipts |
| Audience evidence | Three successive age-aligned comparisons show improving average view duration and returning-viewer measures with enough data to interpret; growth reviewer accepts the evidence strength | Authorized 7/28-day exports, equal format/windows, views and uncertainty; never synthetic fixtures |

The existing roadmap's approximately 300-view floor is a minimum screening rule,
not proof of statistical significance. Sparse returning-viewer data, traffic mix
changes or incomparable durations leave this row unproven. Report confidence and
alternative explanations. Growth cannot be guaranteed by software or a deadline.

The starting ratings remain 2/2/4/7/1/1/1. Revise each row only from the applicable
evidence above. The rating is workflow reliability, not a claim that every film
deserves a perfect artistic score. No script awards an independent story/safety
verdict. Missing production evidence means unproven, even if all unit tests pass.

## One production package

| Order | Owner | Work and output | Acceptance / failure route |
|---|---|---|---|
| 1 | Owner/production Lead | One paragraph and run start timestamp; one active package | Record scope and preserve all attempts |
| 2 | Story-designer | One concrete causal lesson, wrong-to-right action, current source, key moments, three-part comedy; varied setting/engine/music | Check story card; remove ambiguity in the card before staging |
| 3 | Stage scripts + animator | Stage intent rows, measured geometry and camera coverage; cheap rough stills | Clearance and framing pass; unsupported geometry returns an explicit problem to design |
| 4a | Safety-checker | Review card, measured plan and lesson source | Gate 1; structural failure returns to design |
| 4b | Sheet script + fresh reviewer | Covered neutral sheet, fresh retelling, separate problem/cause/lesson comparison | Gate 1b; a mismatch fixes the cause/action/panel, not the review wording |
| 5 | Animator + render scripts | Build from approved beats; explicit shot dependencies, deterministic seeds and camera; render affected shots | Stop on build failure; cache only complete verified shots |
| 6 | Scripts | Assemble visual stream with one continuous episode audio master; check final encoded output | Video/loudness/silence/jump/framing/clearance checks must pass on this revision |
| 7 | Fresh reviewer | Neutral full video, no card/title/plan; new reviewer each round | Gate 2: at least 8 overall and clarity, at most two rounds; otherwise park and diagnose |
| 8 | Animator + scripts | Two distinct marked beats with vertical camera, context and ending; reuse performance assets | Both Shorts get their own technical and blind checks; never rely on the episode's pass |
| 9 | Packaging + safety | Source-bound text/covers, final gate 3 on episode, both Shorts and text | Changed media/text invalidates its prior evidence |
| 10 | Owner | Watch complete package, decide whether to publish | Fresh explicit approval; pipeline does not upload or publish |
| 11 | Authorized growth role | 7/28-day exports and comparable-cohort review | Feed observed retention problems into the next card; no claimed improvement without data |

Safety-plan review and blind storyboard review can be independent parallel
production activities. Astra does not launch or brief the Claude team. A failed
story gate goes back to story/staging; a technical failure goes to the relevant
script or builder. Two failed blind rounds stop further rendering until design
changes. No silent third round or reset of the trial clock.

## Implemented evidence contract

`tools/pipeline_check.py` reads a package manifest and checks 15 documentary
requirements and their prerequisites. It binds each report to its current input
files and binds the storyboard comparison to the actual retelling. It rejects
missing/changed reports, missing Shorts, stale media, declared maker-as-reviewer,
non-blind reviews, low scores, excess rounds, structural safety fixes and owner
overrides as evidence of meeting this quality target.

```bash
python3 tools/pipeline_check.py template build/run01/manifest.json
python3 tools/pipeline_check.py check build/run01/manifest.json
```

Keep all run artifacts beneath that directory (copy the actual source snapshots
and media, or use links resolving inside the run). `episode_source`, `rough` and
Short source artifacts must be dependency manifests containing the hashes of all
their code/assets, not only the entry script. Update them when a dependency changes.
The checker validates the supplied snapshots; it does not discover undeclared
dependencies. Keep private manifests and reports away from blind reviewers.

The template deliberately contains no PASS entries. Each evidence record names
the check, role, raw report and hash, and an exact map of input artifact hashes.
Example record schema (placeholder values; never evidence):

```json
{
  "result": "PASS",
  "role": "fresh-eyes-reviewer",
  "report": "private/review.txt",
  "report_sha256": "<SHA256 of original report>",
  "inputs": {"episode": "<SHA256 of the reviewed MP4>"},
  "reviewer": "<independent reviewer identity>",
  "blind": true,
  "round": 1,
  "overall": 8,
  "clarity": 8
}
```

The checker is a read-only evidence auditor, not an authenticated review service
or replacement for gate.py. It cannot tell whether someone invented a report or
lied about their identity; the production Lead must verify provenance. Technical
records must cite the actual checker output, not a hand-written assurance. A
`DOCUMENTED_PASS` means the documentary contract is satisfied. It never means
Astra judged the film safe or clear. Publication still requires fresh owner approval.

## Engineering sequence and stop conditions

1. Production contract + evidence checker: make missing/stale evidence visible.
   Exit: positive/negative fixtures pass; empty real run remains blocked.
2. Selective shot renderer: explicit local inputs, dependency hashes and integrity
   receipts; continuous final audio. Exit: cold/warm/one-shot-edit tests, corrupted
   cache refusal, clean-vs-cached pixel equivalence and measured real-rig reuse.
3. Stage-kit profiling: capture deterministic expensive/rejected solver cases;
   optimize the dominant measured cost while preserving legal results and geometry
   checks. Exit: before/after time distribution and identical accepted/refused cases.
4. Production integration: the authorized production team uses the checked sheet,
   evidence contract and shot adapter for one complete episode plus two Shorts.
   Exit: final technical checks and independent gates pass; no Astra self-review.
5. Reliability trial: three consecutive packages with complete timing/retry records.
   Exit: per-row acceptance above. Preserve failures and rollback regressions.
6. Audience validation: compare sufficiently observed published packages at equal
   ages. Exit: growth reviewer accepts improvement and uncertainty; otherwise
   diagnose and iterate. This step needs real data over time.

Work packages remain small PRs, regression PASS before merge, with carry-over and
rollback instructions. Do not replace the rig, weaken child-safety rules, add paid
services, publish, access the production repository or launch Claude agents.
Those boundaries come from docs/ASTRA_MASTER_PROMPT.md and remain in force.

## Implementation status, 20 October 2026

Engineering milestones 1–3 are implemented in merged PRs #6–#8: evidence auditing,
selective rendering and bounded staging profiling/optimization. Combined regression
is PASS 173/173. This completes the initial engineering work, not the production
acceptance trial. Milestones 4–6 still require complete production packages,
independent reviewers and sufficiently observed real audience results. Current
scores: 2/2/4/7/1/4/1; details in reviews/astra/09_delivery_status.md.
