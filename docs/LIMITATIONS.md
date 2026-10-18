# Limitations and how to overcome them (Lead, 8 Oct 2026)

Ranked by how much each one can hurt the goal (YPP: 1,000 subscribers + 8,000 long-form hours). "Fix" = what we can
do; "Owner" = only the owner can decide or do it. Estimates are labelled.

## A. Quality: we can't yet prove a video works for children
| # | Limitation | Evidence | How to overcome |
|---|---|---|---|
| A1 | **The only audience test is an AI reviewer**, never checked against real children (owner rule: no kid tests). | 0 of 4 videos passed gate 2; no real views yet | Fix: from 14 Oct the growth-analyst compares each blind score with real "viewed vs swiped away" and retention (now in its file). If they disagree twice, re-anchor the reviewer's scores to the data. |
| A2 | **Comedy is our weakest skill**: comedy 5, 6, 5, 4 on 4 videos. | blind reviews | Fix: this round-2 Short is the test of the playbook + `plan_check`. If comedy is still <7, stop fixing on paper: study 3-5 winning wordless gags frame by frame, then a rig "acting" toolkit job (bigger takes, squash and stretch) before Episode 12. **18 Oct: rig job done** (eyes, lids, darts, blinks, ears, breath); gag-test clips blind 7 and 7, comedy 6 and 7 (`build/blind_g2/blind_r2.md`, not in git). Left: head squash, mouth shapes, sound slots. |
| A3 | The reviewer watches 1 frame a second plus short strips, not real-time motion with sound; it can misjudge timing. | method in its file | Fix: full-speed strips of every gag window (cheap, add if A1 shows misses). |
| A4 | Scripts check only what can be measured (sizes, times, loudness), not whether a beat reads. | `plan_check`, `handover_check` | Accept: readability stays with the blind reviewer; scripts stop the measurable repeats. |

## B. Production
| # | Limitation | Evidence | How to overcome |
|---|---|---|---|
| B1 | **Paper cut-out rig**: limited poses and turns (>36° crowds the edge), no climbing; this limits acting and comedy. | known traps list | Fix: one rig feature per episode (the "one big new thing" rule), planned as a toolkit job. |
| B2 | **Renders run on the Mac's CPU** (~2 s a frame for lit scenes; a full episode ~25 min); the Mac must stay awake. | ledger | Fix: renders in the background cost no tokens; check sheets before full renders. Option: a cloud session (`setup_cloud.sh`) when the Mac is busy. |
| B3 | All music and sound are made in code (original-only rule); the range of instruments is narrow. | sound scores | Fix: a toolkit job for 2-3 new instrument voices when a review flags sound. |
| B4 | Shell and file traps (zsh reads `=====` as a command; guessed paths). | M24, M25 | Fix: rules-card lines at the next retrain. |

## C. Tokens and time (Pro plan)
| # | Limitation | Evidence | How to overcome |
|---|---|---|---|
| C1 | **Weekly limit at 74% with 4.8 days to the reset (Tue 13 Oct, ~12:30 PM IST).** Today used ~15 points; at that pace it hits 100% about Sat 10 Oct (estimate), and then nothing runs (no agent, no Lead) until Tuesday. | get_usage, ledger | Fix: finish the Halloween Short today (its upload is Sun 18 Oct), then only small jobs until the reset. Owner: the alternative is a bigger plan or extra usage (a cost decision). |
| C2 | The animator uses most of the tokens (Ep 11: 74%; the Short: ~60%). | ledgers | Fix (applied today): ≤12 images per stage, the handover check (no failed render rounds). |
| C3 | Agents can't see their own token use, so budgets are in tool calls. | 8 Oct check | Accept; caps via `maxTurns`. |
| C4 | The 5-hour window: a big agent near the reset gets cut off. | M8 | Fixed: `preflight.py` blocks it. |

## D. Process and people
| # | Limitation | Evidence | How to overcome |
|---|---|---|---|
| D1 | **The owner's time is the bottleneck** for uploads and approvals (full-time job). Waiting: Ep 9 v3 (Thu 15 Oct), Ep 5 v2 (Fri 16 Oct), pilot Short + episode (20-21 Oct). | HANDOFF | Fix: everything ready in `Videos/` with paste-ready text; after the owner picks the file and says yes, the Lead fills Studio details. |
| D2 | Agents start fresh every time: they know only what the files say, and rules pile up. | 25 mistake rows in 1 day | Fix: rule budget (≤+10% per file); repeats become scripts (4 added today). |
| D3 | Several idle Claude sessions exist; two Leads at once broke work before (L9). | ListAgents: 3 idle peers | Owner: archive the old sessions ("Halloween short", the two older "Lead handoff continuation"). |
| D4 | Rules can conflict (the 4,000-word cap vs safety pastes, M23; "gag by 5 s" vs "no gag on the mistake"). | this session | Fix: resolved in `plan_check` (lesson-beat rule); designer aims ≤3,700 words. |

## E. The channel and YouTube rules
| # | Limitation | Evidence | How to overcome |
|---|---|---|---|
| E1 | **No real audience yet**: the live Shorts have had only the owner's views. | analytics log | Wait for 14 Oct data; don't change strategy on <300 views. |
| E2 | Made for Kids: no comments, no notification bell, no personalised ads, no thumbnail A/B tests, Shorts earn almost nothing, and Shorts-feed time doesn't count toward the 8,000 hours. | research docs | Fix: long-form episodes and compilations are the engine; Shorts only for discovery. |
| E3 | **Template risk**: all 8 live Shorts are 0:19 with one title pattern (YouTube's inauthentic-content rule). | spot check 8 Oct | Fix: `title_check.py` (applied today); vary lengths; rotate engines. |
| E4 | 8,000 long-form hours is far away; a 3-minute episode needs ~160,000 full views to make it. | arithmetic (estimate) | Fix: 20-30 min compilations after ~10 passed episodes; day-90 review on 4 Jan 2027. |
| E5 | No paid SEO or third-party data; only free search suggestions and public pages. | owner rule | Accept; free outlier method in use. |

## Firm recommendation
1. **C1 first:** finish the Short today, then only small jobs until Tue 13 Oct; owner decides on a bigger plan only if the Ep 12 dates slip.
2. **A1:** the 14 Oct data review is the most important check we have: it tells us whether our only quality gate predicts real viewers.
3. **A2:** if this Short's comedy is still <7, switch from paper fixes to a rig acting job before Episode 12.
