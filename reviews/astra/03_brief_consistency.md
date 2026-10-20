# Brief consistency — 20 Oct 2026

Evidence: reviews/mistake_log.md:78 (M67) and :90 (M79): production requested under feasibility-only caused an early stop and another round trip. tools/agent_hooks.py:481–489 selects the stage and budget from the first Stage line.

Change: tools/brief_check.py rejects explicit build/render/edit/fix requests or storyboard deliverables under that stage. Measurement references and negated actions remain allowed. The existing pre-call hook already invokes this checker, so no agent contract or live gate changes are needed. This is a bounded phrase check, not a proof that arbitrary English is consistent.

Validation (actual runs):
- Combined checkout: REGRESS PASS 169/169, up from 154/154.
- Independent baseline replay in the original parent-settings layout, with only this package's code diff: REGRESS PASS 164/164, up from 149/149. It does not require PR #2.
- Fifteen new cases cover contradictory briefs, legitimate measurements/negations, corrected stages and the actual pre-call hook. The integration case asserts the M67/M79 rejection reason and acceptance of a corrected stage; all fixtures use temporary state.
- git diff --check PASS.

Expected gain: avoid the known M67/M79 stop/resume round trip. Production calls/time saved: unmeasured, not claimed. Existing M39 open-estimate checks remain in place. Rollback: revert this package's squash commit.

Scorecard in prompt order: 2/2/4/7/1/1/1; no newly reviewed story or safety evidence. Story clarity remains the weakest production outcome; audience outcome remains unmeasured. M87 OPEN records my initial weak integration assertion and its correction. M88 OPEN records a skipped nested patch and premature draft test total; the corrected independent replay actually passed 164/164.
