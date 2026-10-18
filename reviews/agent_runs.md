# Agent runs (written by tools/agent_hooks.py stop; the Lead reads it with tail)

| When | Agent | Verdict | Calls real / reported / budget | Peak context | Output | return_check | Sent back |
|---|---|---|---|---|---|---|---|
| 17 Oct 16:37 | packaging | ? | 2 / ? / ? | 8k | 0k | FAIL: no final message found | yes |
| 17 Oct 16:38 | packaging | DONE | 1 / 1 / 15 | 8k | 0k | FAIL: check 1 (file written): cited file does not exist: Crinkle/build/smoke_v42/sheet2.md; fix: cite a file this session wrote | yes |
| 17 Oct 16:38 | packaging | DONE | 1 / 1 / 15 | 8k | 0k | PASS | no |
| 18 Oct 13:22 | packaging | ? | 1 / ? / ? | 9k | 0k | FAIL: no ```json block found | no |
| 18 Oct 13:23 | packaging | ? | 1 / ? / ? | 9k | 0k | FAIL: no ```json block found | no |
| 18 Oct 13:24 | packaging | ? | 1 / ? / ? | 8k | 0k | FAIL: no ```json block found | no |
| 18 Oct 13:24 | packaging | ? | 1 / ? / ? | 8k | 0k | FAIL: no ```json block found | no |
| 18 Oct 13:25 | packaging | ? | 1 / ? / ? | 8k | 0k | FAIL: no ```json block found | no |
| 18 Oct 13:28 | packaging | DONE | 1 / 1 / 15 | 9k | 0k | PASS | no |
| 18 Oct 13:52 | animator | PARTIAL | 22 / 23 / 25 | 100k | 11k | FAIL: check 8 (handover_check): evidence has no number or file path: 'FAIL: no key actions / measured checks table (no plan for rigtest)'; fix: cite the still or the  | no |
| 18 Oct 13:53 | animator | PARTIAL | 22 / 24 / 25 | 102k | 11k | PASS | no |
| 18 Oct 13:55 | fresh-eyes-reviewer | FAIL | 13 / 13 / 40 | 40k | 5k | PASS | no |
| 18 Oct 13:59 | animator | PASS | 30 / 10 / 20 | 124k | 12k | FAIL: tool_calls says 10, the harness counted 30: report the true count; over budget: 30 real calls > budget 20 | no |
| 18 Oct 13:59 | animator | PASS | 30 / 30 / 20 | 126k | 12k | FAIL: over budget: tool_calls 30 > budget 20 | no |
| 18 Oct 14:02 | fresh-eyes-reviewer | PASS | 19 / 18 / 40 | 62k | 5k | PASS | no |
| 18 Oct 14:23 | story-designer | PASS | 20 / 18 / 25 | 118k | 0k | FAIL: check 4 (Measured checks rows (16)): evidence says estimate/looks: 'not checked: all estimate, for the animator to measure'; fix: measure it or write 'not check | no |
| 18 Oct 14:23 | story-designer | PASS | 20 / 20 / 25 | 120k | 0k | PASS | no |
| 18 Oct 14:25 | animator | PARTIAL | 5 / 5 / 5 | 30k | 0k | FAIL: check 2 (Measured column filled): evidence has no number or file path: 'not checked'; fix: cite the still or the measured number; check 3 (head-mask spans per c | no |
| 18 Oct 14:25 | animator | PARTIAL | 5 / 7 / 5 | 31k | 0k | FAIL: over budget: tool_calls 7 > budget 5 | no |
| 18 Oct 14:41 | animator | PARTIAL | 19 / 20 / 25 | 108k | 11k | PASS | no |
| 18 Oct 14:47 | story-designer | DONE | 9 / 10 / 12 | 55k | 0k | FAIL: check 1 (plan_check): evidence says estimate/looks: 'python3 tools/plan_check.py reviews/ep12_plan.md -> plan_check: PASS (15 estimates noted)'; fix: measure it | no |
| 18 Oct 14:48 | story-designer | DONE | 9 / 11 / 12 | 57k | 0k | PASS | no |
| 18 Oct 15:12 | animator | PARTIAL | 16 / 17 / 25 | 151k | 2k | PASS | no |
| 18 Oct 15:15 | fresh-eyes-reviewer | DONE | 6 / 7 / 10 | 18k | 2k | PASS | no |
| 18 Oct 15:17 | safety-checker | FAIL | 15 / 13 / 14 | 50k | 0k | PASS | no |
| 18 Oct 15:23 | story-designer | PASS | 9 / 8 / 12 | 52k | 0k | FAIL: check 4 (restaged numbers): evidence says estimate/looks: '23 estimates listed by plan_check NOTE'; fix: measure it or write 'not checked' | no |
| 18 Oct 15:23 | story-designer | PASS | 9 / 10 / 12 | 53k | 0k | PASS | no |
