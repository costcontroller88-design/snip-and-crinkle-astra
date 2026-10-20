# Astra decisions

| Date | Decision | Evidence | Expected effect | Success criterion |
|---|---|---|---|---|
| 19 Oct 2026 | Keep six roles and existing rig; no broad rewrite | 01_audit.md sections 2–6; ep11_retro.md:7–20 | Remove measured waste while preserving art/safety | Separately verified changes; no invented story passes |
| 19 Oct 2026 | First: portable selftest; second: contradictory brief validation; third: storyboard coverage | agent_hooks.py baseline:665–670; mistake_log M67/M79/M82 | Reliable verification, fewer avoidable calls and missing panels | Both install layouts tested; bad briefs refused; missing required panels fail |
| 19 Oct 2026 | Project configuration is required; parent configuration is optional only when absent | Baseline 147/148 standalone vs 149/149 original layout | Standalone cloud checkout works without a fabricated installation | Missing/broken project hooks and installed broken parent still fail |
| 19 Oct 2026 | Leave clarity and safety ratings unchanged by engineering passes | Ep11 storyboard MATCH later failed video; ep11_retro.md:14–16 | Preserve independent judgments | No gate state written; no self-certified story/safety |
