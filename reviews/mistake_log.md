# Mistake log (all agents and the Lead; owner rule, 8 Oct 2026)

The Lead adds a row the moment a mistake is found (by a reviewer, a gate, the Lead, the owner, or an agent's own
"Mistakes:" line). Retraining: after every finished video, and at once for a repeat or a safety miss, the Lead turns
each OPEN row into a rule or check in MASTER_PROMPT Appendix A (rule budget: ≤+10% words per file), tags the old
version for rollback, runs `python3 tools/build_agents.py`, and marks the row APPLIED with the commit. A row that
repeats an APPLIED one means the rule didn't work: rewrite it, don't add a second one.
Older history: `reviews/ep11_retro.md` (L1-L8, A1-A6, D1-D2, S1-S2).

| # | Date | Agent | Mistake | Evidence | Cost | Rule or check proposed | Status |
|---|---|---|---|---|---|---|---|
| M1 | 8 Oct | Lead | Go/no-go offered Pip as the one who errs; the character bible says Pip never snatches | designer pushback, ep11 plan 7(b) | none (caught) | Lead pre-flight: check `docs/CHARACTER_BIBLE.md` before naming who errs | OPEN |
| M2 | 8 Oct | story-designer | Plan called the take "a slow pinch" but timed pinch + lift at 0.6 s | safety gate 1, F2 | one safety fix | Designer self-check: every "slow" or "hold" in a plan has ≥0.6 s per motion | OPEN |
| M3 | 8 Oct | story-designer | The key action (the marker taken) staged only in a wide shot, against lesson 2 (small things get a ≥1.2 s close-up) | gate 1b round 1 risk, `reviews/ep11_short_storyboard_blind_sb1.md` | a fix-mode pass | Designer: list each key action with its object's size in frame; under 1/10 of the width → close-up ≥1.2 s | OPEN |
| M4 | 8 Oct | story-designer | Camera B spec ("heads in the top third") cut off Snip's drooping ears, the cue the beat depends on | still 3.0 s, sb1 | Lead code fix (camera B2) | Designer: for each acting cue, name the body part and check it is inside that shot's camera box | OPEN |
| M5 | 8 Oct | story-designer | Storyboard frames (b10) left out the cause of the wow (the hand putting the light in) and Pip's hand-over, so the reviewer read the glow as magic | gate 1b round 1 | a doubt in gate 1b | Designer: storyboard frames must include the cause of every change, not only the result | OPEN |
| M6 | 8 Oct | animator | Delivered the sheet with a known key-cue miss (ears cut) instead of fixing a two-line camera change | animator return, sb1 | Lead fix | Animator: a key cue it can see is missing gets fixed (≤3 code steps) before the sheet, not listed | OPEN |
| M7 | 8 Oct | story-designer | One marker (black ink) but the plan has Pip draw a red heart: a prop-continuity gap found only in fix mode | designer return, fix sb1; `MK` ink = `PK.INK` | none (caught before build) | Designer: a props table with every object's colour/state per shot; the same object never changes without a visible cause | OPEN (Lead: heart drawn black) |
