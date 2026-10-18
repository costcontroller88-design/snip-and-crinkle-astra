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
