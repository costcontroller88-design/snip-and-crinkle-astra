# Portable verification — 19 Oct 2026

Evidence: tools/agent_hooks.py baseline lines 665–670 requires an optional parent config; tools/regress.py baseline lines 375–388 already treats it as optional. Audit: 01_audit.md section 0.

Change: selftest now requires the project settings, and checks parent settings only if they exist (including a broken symlink). It uses the original hook predicate. No gates, permission checks, agent files or render code changed.

Measured results:
- Before, standalone: REGRESS FAIL: 147/148 cases.
- Before, legacy parent-symlink layout: REGRESS PASS: 149/149 cases.
- After, standalone: REGRESS PASS: 154/154 cases.
- After, legacy parent-symlink layout: REGRESS PASS: 155/155 cases.
- Six added cases: standalone; installed parent; broken parent symlink; parent missing hooks; missing project config; missing project hook. Negative fixtures prove the wiring checks can still fail.
- git diff --check: PASS.

Independent carry-over: tools/agent_hooks.py and tools/regress.py apply to the baseline; no prior Astra code package is required. Documentation and M86 describe this work only. Rollback: revert the package's squash commit.

Scorecard, in master-prompt row order: 2/2/4/7/1/1/1 (engineering evidence rating, not video scores). Technical readiness rises 6→7 because standalone and original layouts work; story clarity remains the weakest production outcome. No new creative, safety, elapsed-production or audience result claimed.

Own mistake logged: M86 OPEN (oversized local source transfers; corrected and verified). Next: reject contradictory stage briefs, then storyboard coverage.
