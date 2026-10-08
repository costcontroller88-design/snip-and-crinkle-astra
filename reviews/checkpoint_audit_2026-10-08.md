# Checkpoint audit, 8 Oct 2026 (read-only; MASTER_PROMPT v3.5)
Appendix A matches all 6 agent files (scripted compare). Ledger: `reviews/ep11_short_ledger.md`.

## Findings
| ID | Sev | Where | What | Fix (paste-ready) |
|---|---|---|---|---|
| H1 | HIGH | plan_check density; playbook 4 | "No gag inside the lesson beat" (mistake→fix) + a gag every ≤20 s + "gags before the problem, after the fix": a wrong→right span over ~20 s can't pass. | plan_check: `**Lesson beat:**` = the mistake ±2 s; the gap across it may reach 25 s. Playbook 4: "No gag within 2 s of the mistake or on the sad character; between problem and fix, gags come from the helper's trait." |
| H2 | HIGH | §8.3; fix mode | plan_check runs only inside the designer; the Lead's gate-1 pastes go unchecked (M23: 4,187 words). Fix mode never runs it. | §8.3: "After pasting, the Lead runs `python3 tools/plan_check.py <plan>`; FAIL → fix mode." Fix mode: "plan_check must PASS before you return; aim ≤3,700 words." |
| H3 | HIGH | §9 vs §8.7 | Gate 2 pass needs "safety PASS", but gate 3 follows packaging, which waits for gate 2: circular. | §9: "**Gate 2 pass:** no blocking issue, overall ≥8, no item <7, check_video PASS. **Upload:** gate 2 + gate 3 PASS." |
| H4 | HIGH | packaging; title_check | Packaging isn't told to write `**Title:**` lines, pick first; with none, title_check prints PASS on 0 titles. | Packaging: "Write each option as `**Title:** <text>`, your pick first." Script: exit 1 if no `**Title:**` line. |
| H5 | HIGH | title_check `--title` | Growth-analyst's live title is compared with its own quote in analytics-log and its own sheet: always FAIL. | In `--title` mode skip old titles whose core words equal the new one's. |
| H6 | HIGH | §10.11 | Repeats still words only: L3, L5→M32; D2→M15; M1/M10/M19; L1/L2→M27. | preflight `--ctx <k>` (>200: "LEAD CODES NOTHING") and `--estimate <pts>` (next run prints estimate vs actual). New `tools/brief_check.py`: FAIL a build brief without "feasibility first" or with a budget. |
| H7 | HIGH | mistake_log | M22-M25, M30-M32 OPEN; M31, M32 are repeats ("apply at once"). | Rules card: "Separators: `echo ---`, never `echo ===` (zsh)." "Module paths come from `docs/TOOLKIT.md`, never guessed." Then H8. |
| H8 | HIGH | Budgets | Briefs override files (fix ≤14 vs 12; re-scope ≤10 vs 14), against §10.11.7. Unlogged overruns: designer fix r1 19 vs 12; animator fix K 27 vs 20. Designer has now overrun twice: M30 trigger met. | maxTurns = top budget + 2: designer 27, safety 20, animator 62, reviewer 42, packaging 17, growth 42. §10.9 add: "every ledger overrun is a row." |
| M1 | MED | reviewer vs rules card | The card gives the blind reviewer `episodes/epNN_<slug>.py`, TOOLKIT and "your playbook section" (none named); its file says open nothing; it has Bash in the repo. Blindness is words only. | build_agents: reviewer card without Files/Toolkit/Comedy lines; neutral copy in the scratchpad; PreToolUse hook denying reviewer reads under the repo. |
| M2 | MED | §8.6, §2, §9 | "One review covers both" Shorts, but brief and reviewer take one video; `epNN_blind_rK` collides; a transformation Short must score ≥7 on lesson. | §2: `reviews/epNN_short_blind_rK.md`. Brief: `Videos: <a>, <b>`. Reviewer: "Score each video; lesson n/a for a transformation Short." |
| M3 | MED | handover `--verify` | Hashes every repo .py: a parallel stage or Short build breaks the episode's `.ok`. | Hash the script, its repo imports, the plan. |
| M4 | MED | handover `plan_for` | A Short with no short plan falls back to the episode plan: keysize at episode times. | FAIL when `*short*` has no `epNN_short_plan.md`. |
| M5 | MED | check_video | No script checks Shorts safe zones (bottom 19%, right 12%) or lengths (≤60, 15-30 s). | `--check` prints `safezone <t> ok/FAIL` per key object; handover fails on FAIL; check_video `--dur 15-30`. |
| M6 | MED | preflight `band()` | Ignores `--weekly` ("ANY AGENT" at weekly 74-77%); advisory only. | Weekly > days/7×100+10 → "SMALL AGENTS ONLY"; exit 2 if `--log` names a forbidden agent. |
| M7 | MED | safety-checker | Gate 1 inputs omit `## Measured checks`, yet check 2 needs it; it "adds a row to the plan" while it "never edits" and the Lead pastes. | Inputs: "+ the plan's `## Measured checks`". Check 2: "Put the row in the FIX text; the Lead pastes it." |
| M8 | MED | designer vs plan_check | Gag table merges break and size, lacks `Break size (%)` and `Test`, says "whose trait" not "callback"; `**Lesson beat:**` and the key-actions table unnamed: FAIL loops. | Item 5: paste `\| Time (s) \| Type \| Trait \| Set-up (s) \| Pause (s) \| Break (s) \| Break size (%) \| Joke signal \| Reaction (s) \| Sound \| Topper \| Test \|`, `\| Key action \| Time (s) \| Object \| Size (%) \| Uncovered (s) \|`, "`callback` in Trait; a `**Lesson beat:** a-b s` line". |
| M9 | MED | §3b; fix mode | Fix mode reads a "blocking list" storyboard output lacks; the Lead's MATCH leaves no record. | Storyboard output: "`**Risky frames:**` (s, other reading)". Fix mode: "or risky frames". §3b: "log card vs retelling (problem, cause, lesson) in the ledger." |
| M10 | MED | §8.0, 4a, 8 | No evidence for go/no-go, prototype look, or the +10% rule budget. | Go/no-go = first ledger row; build_agents fails a file over +10% words vs the last tag. |
| M11 | MED | §3b vs plan_check | "10-12 stills" vs Shorts 6-12; key actions + first 30 s + 2 gags can exceed 12. | §3b: "10-12 (a Short 6-12)"; plan_check allows 14 when key actions need it. |
| L1 | LOW | plan_check regex | Only "≥N from/clear/and"; "at least 10 units" escapes. | Also match `at least N`, `>= N`, `N or more`. |
| L2 | LOW | animator, growth | No `tools:` line: all tools; "never touch YouTube" is words. | Animator: `tools: Read, Write, Edit, Bash`. |
| L3 | LOW | §5.5, §6, playbook, plan_check | Density 10-20 / 15-20 / Shorts 10-15 / ≤15. | §6: "Shorts: first gag by 5 s, then every ≤15 s." |

## Budgets (tool calls)
| Agent | File | maxTurns | Ledger |
|---|---|---|---|
| story-designer | plan 25, fix 12 | 30 | fix r1 19 (unlogged); r3 16 (M31) |
| safety-checker | 14 / 18 | 22 | 14, 11, 9, 12 (M30; within file) |
| animator | 5-60 by stage | 70 | fix K 27 vs 20 (unlogged); r2 skipped feasibility (M26) |
| fresh-eyes | 40 / 10 | 45 | 19, 8 |
| packaging | 15 | 20 | — |
| growth | 40 / 25 | 45 | — |

## Coverage
| IDs | Prevented by | Type | Flag |
|---|---|---|---|
| M2, M3, M14 | plan_check key actions (declared, never measured for uncovered) | SCRIPT | partial |
| M11 | handover_check keysize | SCRIPT | |
| M5, L2 | plan_check storyboard | SCRIPT | L2: no lesson-beat frame rule |
| M7 | plan_check props (presence only) | SCRIPT | partial |
| M16 (repeat) | plan_check gag table; anchors | SCRIPT | H1 |
| M17 | plan_check words | SCRIPT | |
| M6, M12, M13 | handover_check | SCRIPT | M6 storyboard stage: none |
| A5→M26, A6 | handover estimates; feasibility | SCRIPT + STAGE | |
| D1→M28 | plan_check measured rows | SCRIPT | L1 |
| S1→M29 | safety words | WORDS | REPEAT |
| M9, M18, M20, L8 | handoff_check hook | SCRIPT | |
| M8 | preflight band | SCRIPT (advisory) | M6 |
| L3, L5→M32 | — | WORDS | REPEAT, OPEN |
| M1, M10, M19 | preflight line (checks nothing) | WORDS | REPEAT class |
| L1, L2, M27 | brief template | WORDS | REPEAT class |
| D2→M15, M4 | misread rule; gate 1b | WORDS + STAGE | REPEAT |
| A1-A4 | animator still rules | WORDS | A3/A4 repeat |
| S2 | gate 3 | STAGE | no "no white near cuts" check |
| L4 | Lead render chain | STAGE | |
| L6, L7, L9, M21 | Lead rules | WORDS | |
| M22-M25 | — | WORDS | OPEN |
| M30, M31 | — | WORDS | OPEN, REPEAT |
| A7 | no such row (log: A1-A6) | — | brief error |
