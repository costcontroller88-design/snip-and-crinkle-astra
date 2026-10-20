# Astra carry-over decisions

20 Oct 2026. Carry only merged implementation packages listed below, one at a time. Do not carry the audit-only PR #1. This is a hand-off list for the owner to forward; Astra has not accessed the real repository.

| PR / squash commit | Decision and evidence | Effect in production | Verification and rollback |
|---|---|---|---|
| [#2](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/2) / `9cacdb4386299a473fd41bc00e305f49d869fcaa` | Carry. Standalone selftest incorrectly required a parent install; report: 02_portable_checks.md | Require local hooks; validate parent hooks when present. No gate changes | 154/154 standalone, 155/155 legacy. Revert this commit to roll back |
| [#3](https://github.com/costcontroller88-design/snip-and-crinkle-astra/pull/3) / `edaf3af04fb29ce0cfb2fc13793cea1ae5002fdf` | Carry. M67/M79 caused stop/resume work; report: 03_brief_consistency.md | Reject explicit production requests under feasibility-only; allow corrected stages and measurement requests | 169/169 combined; 164/164 independently on baseline. Revert this commit to roll back |

Each package must pass the destination's regression suite. The Lead may block only for a failed check, hard-rule/safety problem or production clash, explaining it in the PR. No channel publication is authorized by this list.
