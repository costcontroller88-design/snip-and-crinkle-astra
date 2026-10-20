# Production pipeline — 20 October 2026

The owner requested all seven scorecard rows at 10/10. docs/ASTRA_PRODUCTION_PIPELINE.md now defines the full paragraph-to-episode-plus-two-Shorts workflow, failure routing, six implementation/adoption milestones and measurable acceptance criteria. Ten requires repeated production outcomes; it is not awarded from a code test.

Evidence problem: reviews/astra/01_audit.md sections 2–5 records failed story rounds and no complete <=48-hour episode-plus-two-Shorts trial; tools/gate.py:1–16 accepts existing report paths without binding report contents to the reviewed media. This package does not change that gate tracker. It adds a read-only companion, tools/pipeline_check.py, to detect stale/missing evidence across 15 prerequisites. Changed videos, plans, reports and retellings invalidate the corresponding documentary result. Declared maker-as-reviewer, non-blind review, poor scores, excess rounds, structural safety fixes and override-based acceptance are blocked.

Actual validation:
- Nine focused tests PASS, including changed retelling invalidating an old comparison.
- Combined REGRESS PASS 171/171.
- Independent replay on the original baseline in the supported parent-settings layout: REGRESS PASS 150/150. Neither earlier Astra implementation is required.
- Initialized an empty real run under build/astra/production-pipeline: ready_for_owner_review=false, all 15 checks BLOCKED. No fabricated reviews entered.
- git diff --check PASS. No live gate state written; no agent launched or briefed.

Limitations: this validates documentary contracts and hashes, not reviewer identity/authenticity, semantics, policy or source freshness. Dependency snapshots must be complete. Ready-for-owner-review never authorizes publication. Independent reviews and authorized audience exports remain external requirements. Scores remain 2/2/4/7/1/1/1 until outcome evidence warrants change.

Carry: checker, its test, regression integration and the production-pipeline document/report. Rollback: revert the destination package commit. Next implementation: selective rendering with corruption/invalidation/equivalence tests and a measured actual-rig trial.
