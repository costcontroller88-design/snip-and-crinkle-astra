# Staging profile and cache correctness — 20 October 2026

Evidence: reviews/astra/01_audit.md section 3 and reviews/stage_kit_trial.md record slow/rejected staging work. A bounded three-case profile now reproduces a literal accepted row, a solved draw request and a refusal, each in an isolated process with an empty private pose-cache path. It records unprofiled cold/warm times, a third profiled call, outcome hashes and code hashes. A timeout remains a timeout and retains completed measurements; it never becomes a pass. No live table, gate or pose-cache file is written by the profiler.

Measured hotspot: the baseline draw profile called gap 1,731 times and _shift 33,270 times; gap consumed 0.175s of the 0.234s profiled call. Refusal used gap 806 times. Replace padded shifted-array copies with overlapping slices; preserve the distance formula, thresholds, sampling, candidate ordering and refusal behavior.

Also fix a correctness defect found during this inspection: the old _code_key tried episodes/characters.py, silently skipping the actual root characters.py. The new persisted pose key includes the existing recursive module-discovery closure, the stage algorithm, fonts, NumPy/Pillow versions and scales. A changed key rejects old disk poses; changes during a running process prevent saving them under a new key. Save completion is atomic. Static discovery remains limited to ordinary Python imports; undeclared dynamic runtime assets must not be assumed covered.

Actual validation:
- Four focused tests PASS: 512 seeded random profile comparisons plus 12 empty/touching/far comparisons, real dependency-closure checks, stale persisted-cache rejection and mid-process change refusal/atomic fresh save.
- Combined REGRESS PASS 173/173; independent baseline with parent settings PASS 150/150. No earlier Astra package required.
- Paired six-batch benchmark, 1,000 profile pairs per batch, alternating original/optimized order: medians 0.0450409s → 0.0347209s (22.9% lower), identical values. Seed 20261020. Reproduce: python3 tools/benchmark_stage_gap.py.
- All three solver cases completed cold/warm/profiled, and every final outcome hash matches baseline, including exact refusal text and accepted rows/shot choices.
- Baseline draw cold/warm: 4.9579/0.1505s; final 5.1569/0.1248s. Baseline refusal: 4.2999/0.0864s; final 4.4643/0.0767s. These single-case wall times include warm-up/runtime variation, so no general end-to-end speedup is claimed. The paired distance benchmark supports the local optimization only.
- No case timed out at 45s. Historical >120s production stalls were not reproduced by these three fixtures; longer production tables remain a profiling/adoption requirement.
- Python checks and git diff --check PASS. Existing ResourceWarnings from the module-discovery reader are observable in focused-test logs; no assertion failed.

Carry stage_kit.py, test_stage_gap.py, the profiler/microbenchmark, regression integration and this report. Use python3 tools/profile_stage_solver.py <new-report.json> --timeout 45. Rollback: revert the destination package; old/new pose-cache keys differ, so incompatible entries are ignored. Scores stay 2/2/4/7/1/4/1; no new production clarity, safety or delivery evidence is claimed.
