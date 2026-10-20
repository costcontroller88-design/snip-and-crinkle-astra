# Astra carry-over decisions

20 Oct 2026. Carry only merged implementation packages listed below, one at a time. Do not carry the audit-only PR #1. This is a hand-off list for the owner to forward; Astra has not accessed the real repository.

| PR / squash commit | Decision and evidence | Effect in production | Verification and rollback |
|---|---|---|---|
| [#2](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/2) / `9cacdb4386299a473fd41bc00e305f49d869fcaa` | Carry. Standalone selftest incorrectly required a parent install; report: 02_portable_checks.md | Require local hooks; validate parent hooks when present. No gate changes | 154/154 standalone, 155/155 legacy. Revert this commit to roll back |
| [#3](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/3) / `edaf3af04fb29ce0cfb2fc13793cea1ae5002fdf` | Carry. M67/M79 caused stop/resume work; report: 03_brief_consistency.md | Reject explicit production requests under feasibility-only; allow corrected stages and measurement requests | 169/169 combined; 164/164 independently on baseline. Revert this commit to roll back |
| [#4](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/4) / `59611a91cebe83f87811daf845c7288612cd128f` | Carry. M82 omitted key panels despite look checks; report: 04_storyboard_coverage.md | Add covered-sheet generation and private moment/panel integrity checks; adopt this command for stage-kit blind sheets | 170/170 combined; 150/150 independently; 15 focused tests. Revert this commit to roll back |
| [#6](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/6) / `ac0a46b7dadb7fcd4aac67cd5a7c72ed6361d291` | Carry. Full pipeline and evidence contract; report: 06_production_pipeline.md | Read-only audit of 15 production requirements, report/input hashes and independent-review declarations | 171/171 combined; 150/150 independent. Revert destination commit |
| [#7](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/7) / `bd22b5fa631964504c38f09b73fec0dfcfd76159` | Carry. Whole-timeline redraw waste; report: 07_selective_rendering.md | Opt-in complete-shot cache with integrity checks and continuous final audio; existing defaults preserved | 172/172 combined; 150/150 independent; rig edit redraws 3/9 with clean-equivalent output. Revert destination commit |
| [#8](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/8) / `2a81b77469b34fb3094a3a95071d7e4e0dd9bd74` | Carry. Measured gap-allocation hotspot and missing root character dependency; report: 08_stage_profiling.md | Faster distance calculation, bounded profiling, complete persisted pose dependency keys | 173/173 combined; 150/150 independent; 524 equal distances and unchanged solver decisions. Revert destination commit |

Each package must pass the destination's regression suite. The Lead may block only for a failed check, hard-rule/safety problem or production clash, explaining it in the PR. No channel publication is authorized by this list.

## Exact hand-off for the Lead

The owner forwards this file; the owner does not need to inspect or run code.
Use the standalone patches below, one at a time, rather than cherry-picking the
whole Astra squash commits. The patches include implementation, tests and each
package's report/docs. They exclude Astra-only cumulative decisions, hand-off and
mistake-log edits, which would otherwise create bookkeeping dependencies.

Each complete patch was applied to a fresh baseline snapshot and its resulting
code compared byte-for-byte with the independently tested version. The baseline
is `b06a8efee6964fd34580ec3fb3d547dbf99e56b9` in Astra. Actual production changes
since that copy are unknown; do not overwrite a conflict.

| Package | Standalone patch | Expected regress total when applied alone to the original supported layout |
|---|---|---|
| PR #2 | `patches/02-portable-checks.patch` | PASS 155/155 (154/154 without parent installation) |
| PR #3 | `patches/03-brief-consistency.patch` | PASS 164/164 |
| PR #4 | `patches/04-storyboard-coverage.patch` | PASS 150/150, including the 15-test coverage suite |
| PR #6 | `patches/06-production-pipeline.patch` | PASS 150/150, including nine evidence-contract tests |
| PR #7 | `patches/07-selective-rendering.patch` | PASS 150/150, including nine cache/encode tests |
| PR #8 | `patches/08-stage-profiling.patch` | PASS 150/150, including four geometry/cache tests |

From the destination checkout, the Lead checks/applies each saved patch with
`git apply --check <patch>` then `git apply <patch>`, runs
`python3 tools/regress.py`, and commits that package separately. Production's
later tests can change the count; every case must pass. When applied together in
Astra the result is PASS 173/173 standalone. To roll back a carried package,
revert that destination commit. For PR #4, follow docs/STORYBOARD_COVERAGE.md;
legacy `stage.py sheet` does not enforce the new check. Keep the reviewer blind.

No clearance/framing result, story match, safety pass, finished episode or
production time saving is claimed by these patches. Those remain separate checks.
PR #8 completes the initial solver investigation and local optimization. PR #7 adds an opt-in shot cache. Full episode migration, complete production trials, independent reviews and real audience validation remain outstanding; see docs/ASTRA_PRODUCTION_PIPELINE.md and 09_delivery_status.md.

## Patch checksums

- `02-portable-checks.patch`: `193b76661cbc8f713733efd2696ef44011a253595ea676804ed97eb15a49fb0e`
- `03-brief-consistency.patch`: `1a1f2bdb0340874838b6d08460f987b687c6f2ff8c22768b137cdcbb94085094`
- `04-storyboard-coverage.patch`: `b059cec98cdd897f1294897babec8eef4f41dc5e13625cc9dc3acafa2edce1cc`
- `06-production-pipeline.patch`: `1074c08215886fe1f904b849c2843c00e56cbb01c7e0978b200a293b3696d5f5`
- `07-selective-rendering.patch`: `2f56ff553277a651471cc10a814c819574d67e210b9f720b95f7354b66767f98`
- `08-stage-profiling.patch`: `0423a7f7b76d192aee9318829110a5d065b2d2cef7890485b7450e94fb0fcd25`

## Next production evidence

Apply the listed packages individually and run destination checks. Then validate
one complete 4–6 minute episode plus two Shorts using the pipeline contract;
retain all attempts, elapsed time, source hashes and original independent reports.
Only the production team operates its agents and gate tracker. Astra did not run
those agents or access Studio. Do not treat the synthetic cache/geometry fixtures
as a production package. Three consecutive qualifying packages are required for
the 10/10 reliability trial; audience evidence additionally needs authorized,
age-aligned 7/28-day exports with enough data to interpret. The owner still gives
a fresh approval before any publication.
