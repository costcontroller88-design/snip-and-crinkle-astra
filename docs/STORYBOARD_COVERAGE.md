# Storyboard coverage (M82)

Use this before sending a stage-kit storyboard to blind review. It checks that the
declared key moments have samples on the delivered sheet. It cannot decide what a
panel means. It neither records nor replaces gate 1, 1b, 2 or 3.

## Builder inputs

Keep a private JSON file beside the plan. Version 1 requires `problem`, `cause`,
`lesson` and `payoff`; add every story-specific key moment as another unique ID
(for example `loss` or `reveal`). Choose narrow windows from the actual beat table,
then have the plan's owner confirm they represent the card. Broad windows or a
wrong declaration can pass without showing the intended action.

This is a schema example, not an episode or a recommendation for its timing:

```json
{
  "version": 1,
  "moments": [
    {"id": "cause", "start": 0.2, "end": 0.8},
    {"id": "problem", "start": 1.2, "end": 1.8},
    {"id": "lesson", "start": 2.2, "end": 2.8},
    {"id": "payoff", "start": 3.2, "end": 3.8}
  ]
}
```

Times are seconds. Windows include both endpoints; all times must be finite,
nonnegative and less than the table duration. Supply increasing, distinct sample
times (at most 48). Each moment needs at least one sample inside its window. One
sample may cover multiple declared windows; that is not a semantic judgment.

## Generate and check

```bash
python3 tools/stage.py covered-sheet epNN reviews/epNN_moments.json 0.4,1.4,2.4,3.4 build/sb01
python3 tools/storyboard_check.py build/sb01 --requirements reviews/epNN_moments.json --source reviews/epNN_stage.md
```

The table must already exist. Every sample must have an explicit shot; the tool
refuses the renderer's fallback camera. It calls the stage's own `still(t)`, saves
neutral numbered panels, assembles them chronologically without cropping or
stretching, and labels only panel numbers and timestamps. A completed directory
appears only after verification. Use a fresh revision directory for each attempt;
existing results are never overwritten.

Outputs:

| File | Reader | Purpose |
|---|---|---|
| `storyboard.png` | Blind reviewer | Actual neutral sheet; no moment names or plot labels |
| `panel_001.png`, etc. | Builder | Exact sampled images used for the sheet |
| `receipt.json` | Builder | Times, sizes, panel/sheet hashes, table/requirements hashes and coverage mapping |

Give the reviewer **only** `build/sb01/storyboard.png` and the round number. Keep
the parent directory neutral too. Do not share the moment file, receipt, source
table or this checker's detailed errors with a blind reviewer. These files are
not additional reviewer inputs.

Verification exits 1 for missing samples, invalid declarations, stale table or
requirements bytes, missing/changed panels, or a sheet that differs from the
declared panels. It reconstructs the sheet as well as checking hashes. This is
accidental-staleness/integrity checking, not tamper-proof provenance: the receipt
is not signed. It does not hash renderer dependencies, so regenerate after any
renderer change. It cannot prove that supplied declarations match the story card.

The legacy `stage.py sheet` command remains available and **does not** perform
this coverage check. Use `covered-sheet` for the checked workflow. Bespoke episode
renderers are not integrated by this change. Clearance, framing, blind review and
safety checks still run separately; a coverage PASS must never be reported as one
of those passes.

## Verification and rollback

`python3 tools/test_storyboard_check.py` runs isolated positive and negative
fixtures, and `python3 tools/regress.py` includes that suite. No live gate or agent
is invoked. Revert the package commit to remove the command, checker, tests and
documentation; existing neutral image outputs remain ordinary PNGs.
