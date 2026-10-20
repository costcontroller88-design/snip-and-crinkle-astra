# Storyboard coverage — 20 Oct 2026

Evidence: reviews/mistake_log.md:93 (M82) and reviews/ep12_ledger.md:24: the delivered sheet omitted key moments despite repeated look checks. Existing episodes/stage_kit.py:1800–1817 composes whatever sample times it receives.

Change: a new `stage.py covered-sheet` command renders declared samples through the actual stage cameras. A private requirements file must declare problem, cause, lesson, payoff and any extra moments. Missing time-window samples fail before rendering; timestamps without an explicit shot fail instead of using a fallback camera. A private receipt binds table/requirements hashes, samples, panel sizes and image hashes. Verification reconstructs the neutral sheet and compares pixels. Existing output revisions are preserved, incomplete bundles are removed. The existing sheet command is unchanged and does not gain coverage checking.

Validation (actual runs):
- Combined REGRESS PASS 170/170 (previous 169/169). The added regression case runs 15 focused tests, all PASS.
- Independent replay: this package's code diff and new modules on the original baseline with parent settings: REGRESS PASS 150/150 (baseline149). Neither PR #2 nor #3 is required.
- Actual rig: four stills at 0.4, 1.4, 2.4, 3.4 seconds from a temporary four-second, single-character stage; bundle rendered in 12.364 seconds. CLI verification PASS, four declared moments covered.
- Visual inspection: 1488×616 sheet, four ordered panels, no crop/stretch, neutral numeric labels. This stationary fixture tests rendering, not a story. No clarity/safety verdict is inferred.
- Python compilation and git diff --check PASS.

Limitations: declarations are supplied by the builder; their story meaning cannot be validated by this script. Broad or mistaken windows can pass. The receipt is unsigned and does not hash renderer code, so regenerate after renderer changes. The command is opt-in and covers stage-kit sheets only; adoption, fewer blind-review rounds and production savings are unmeasured. Share only the neutral storyboard PNG, never requirements or receipts, with the blind reviewer. No gate state or agent contract changed.

Carry independently with docs/STORYBOARD_COVERAGE.md and the toolkit pointer. Rollback: revert this package's squash commit. Scorecard in prompt order remains 2/2/4/7/1/1/1. Story clarity is the weakest measured production outcome; audience evidence, elapsed delivery and shot reuse remain unproven. No new own mistake was found in this package.
