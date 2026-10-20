# Astra carry-over decisions

20 Oct 2026. Carry only merged implementation packages listed below, one at a time. Do not carry the audit-only PR #1. This is a hand-off list for the owner to forward; Astra has not accessed the real repository.

| PR / squash commit | Decision and evidence | Effect in production | Verification and rollback |
|---|---|---|---|
| [#2](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/2) / `9cacdb4386299a473fd41bc00e305f49d869fcaa` | Carry. Standalone selftest incorrectly required a parent install; report: 02_portable_checks.md | Require local hooks; validate parent hooks when present. No gate changes | 154/154 standalone, 155/155 legacy. Revert this commit to roll back |
| [#3](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/3) / `edaf3af04fb29ce0cfb2fc13793cea1ae5002fdf` | Carry. M67/M79 caused stop/resume work; report: 03_brief_consistency.md | Reject explicit production requests under feasibility-only; allow corrected stages and measurement requests | 169/169 combined; 164/164 independently on baseline. Revert this commit to roll back |
| [#4](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/4) / `59611a91cebe83f87811daf845c7288612cd128f` | Carry. M82 omitted key panels despite look checks; report: 04_storyboard_coverage.md | Add covered-sheet generation and private moment/panel integrity checks; adopt this command for stage-kit blind sheets | 170/170 combined; 150/150 independently; 15 focused tests. Revert this commit to roll back |

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

From the destination checkout, the Lead checks/applies each saved patch with
`git apply --check <patch>` then `git apply <patch>`, runs
`python3 tools/regress.py`, and commits that package separately. Production's
later tests can change the count; every case must pass. When applied together in
Astra the result is PASS 170/170 standalone. To roll back a carried package,
revert that destination commit. For PR #4, follow docs/STORYBOARD_COVERAGE.md;
legacy `stage.py sheet` does not enforce the new check. Keep the reviewer blind.

No clearance/framing result, story match, safety pass, finished episode or
production time saving is claimed by these patches. Those remain separate checks.
The next engineering investigation is solver latency with reproducible inputs;
no solver rewrite or shot cache is included in this hand-off.

## Patch checksums

- `02-portable-checks.patch`: `193b76661cbc8f713733efd2696ef44011a253595ea676804ed97eb15a49fb0e`
- `03-brief-consistency.patch`: `1a1f2bdb0340874838b6d08460f987b687c6f2ff8c22768b137cdcbb94085094`
- `04-storyboard-coverage.patch`: `b059cec98cdd897f1294897babec8eef4f41dc5e13625cc9dc3acafa2edce1cc`
