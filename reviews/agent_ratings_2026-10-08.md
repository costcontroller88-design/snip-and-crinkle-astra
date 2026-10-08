# Agent and Lead ratings, 8 Oct 2026 (owner asked: harsh, from evidence, with fixes)

Evidence: `reviews/mistake_log.md` (M1-M21), `reviews/ep11_retro_notes.md` (A1-A7, D1-D2, S1-S2, L1-L9),
blind scores (Ep 11 rounds 1-3: overall 6, 6, 6, comedy 5, 6, 5; the Short's round 1: overall 7, comedy 4),
`reviews/ep11_short_ledger.md` (tokens). Since the version 2 rules, **0 of 4 videos passed gate 2** (pass = overall ≥8).

| Who | Score | Mistakes on record | Weakest point (evidence) |
|---|---|---|---|
| fresh-eyes-reviewer | **8** | round-3 overrun (55 calls, 119k vs a ≤40-call budget) | Never wrong on a story read (caught "won't share", "smug", "knife", "no light source"), scores consistent. Weak: one budget blow-out, and it has never been checked against real viewers. |
| safety-checker | **7** | S1, S2 | Cheap (40-44k) and caught M2. Missed the white marker that read as a knife (S2), gave an unchecked "3 steps" (S1), gate 1 took 14 calls vs a budget of 12. |
| growth-analyst | **6** | none logged | Studio log and benchmarks are sound. But its Halloween research fed a topic picked for views, not teaching (retro 13), and the Lead (not the analyst) spotted that all 8 Shorts are 0:19 with one title pattern (template risk). |
| packaging | **5 (unproven)** | early: ran in parallel with a failing review | Not used since the version 2 rules. The live Shorts share one title and description pattern; 0 real views so far, so its titles are untested. |
| animator | **5** | A1-A7, M6, M11, M12, M13 (11) | Look scores 8, but it uses most of the tokens (Ep 11: 74% of 1.66M; the Short: ~590k of ~1.0M) and repeats the same failure: it claims or skips checks (A1, A3, A4, M12, M13) and trades away key sizes (M11). |
| story-designer | **4** | D1, D2, M2-M5, M7, M14-M17 (11) | Root cause of most failed rounds: comedy 5, 6, 5, 4 on 4 videos; key actions staged too small or too fast (M3, M14); plan 11,683 words vs a 4,000 cap. Good: refused "Pip snatches" (M1). |
| Lead (me) | **4** | L1-L9, M1, M8-M10, M18-M21 (17) | The most mistakes of anyone; HANDOFF over the cap 6 times despite 3 rules until a script stopped it; two Leads at once (L9); a big build started at 82% (M8). Good: built the gates and the automation that now catch these. |

## Fixes (owner approves; following the 8 Oct rule, a repeated mistake becomes a script check, not new words)
1. **story-designer: `tools/plan_check.py`** (blocks a plan that fails): ≤4,000 words; every gag-table row has all
   seven parts filled with seconds; every key action row says its duration (≥1.0 s) and object size (≥10% or a
   close-up ≥1.2 s); every storyboard change has its cause frame. Closes M2, M3, M5, M14, M16, M17. Shorts get their own
   plan file. Run it before the comedy fix pass (the next step), so that pass is a fair test.
2. **animator: `tools/handover_check.py`**, the last command before any render chain: a whole `--check` on the final
   code, the audio silence test, key-object sizes against the plan's camera. Closes M6, M11, M12, M13. Plus a token
   cap: a stage that passes ~200k stops and reports.
3. **fresh-eyes-reviewer:** none to its judgment; `maxTurns` 45 already caps it. At the 14 Oct checkpoint, compare
   its Short score with real "viewed vs swiped away".
4. **safety-checker:** gate 1 budget 12 → 14 (the real cost); keep S2's prop check.
5. **packaging:** a check that compares a new title and description with the last 5 and flags the same pattern.
6. **growth-analyst:** each Studio review lists template risks in live uploads (length, title pattern).
7. **Lead: `tools/preflight.py`** at the start of every step: git status, the last ledger row, OPEN mistakes by
   agent, and a stop if the usage reset is less than 90 minutes away. M1, M10 and M19 become one line: "read the file
   that already knows (bible, Studio, benchmarks) before you claim or ask".

Cost: about 1-2% of the 5-hour limit (Lead scripting; no agents). Rollback tag before any change.
