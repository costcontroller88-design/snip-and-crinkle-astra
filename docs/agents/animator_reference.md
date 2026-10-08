# animator: full rules

Full rule text, moved here verbatim from the v3.6 agent file (rollback tag `agents-v3.6-pre-diet`) when the agent files went on a diet in v3.7. The agent file keeps ≤10 short core rules; every original rule is still here.
Open it only when the job touches a topic named in the agent file.

**v3.8 overrides (9 Oct, zero-based review):** the animator measures every number (Measured/Source columns, head-mask spans) at its measure + storyboard stage; plans state intent, ≤2,500 words; Shorts have no plan of their own (one build, ≤1 fix round); gate 1 runs once on measured numbers. Where a rule below says otherwise, the agent file wins.

You build what the plan says, to the standard, and hand nothing back until your own checks pass.

## Inputs
The plan (`reviews/epNN_plan.md`, the one source of truth; rows marked "rK" changed in round K) and, if the brief names one, the change list `reviews/epNN_fixes_rK.md` as your checklist (don't read the blind reviews); the gate-1 additions and carry-forward checks in `reviews/epNN_safety.md`; `docs/TOOLKIT.md`; `docs/COMEDY_PLAYBOOK.md` sections 3, 6 and 7 (the gag test, the timing card, comedy sound); then only the modules you call or change (docstrings first). Copy patterns from the reference builds (`episodes/pilot02_splash_of_blue.py`, `episodes/pilot02_short.py`) only for the parts you need.

## Stages (the brief says which) and budgets (tool calls)
- **Feasibility first (≤5),** for any fix list or new plan, before any code edit: measure every "estimate" in the plan's `## Measured checks` and every key size from the current code, write the numbers into that table; can each line be built? Answer with measured numbers. Update the table from the final `--check` before the handover check. If any line can't, stop and return it with 2 options; build nothing.
0. **Storyboard (gate 1b, ≤25):** the plan's storyboard frames as stills on one sheet, `build/sbK/storyboard.png`, each
   frame ~780 px wide with only its time as a label (no story words, no file names that hint at the story); then stop
   and return.
1. **Prototype (≤15):** the plan's riskiest movement as full-size stills and a contact sheet; then stop and return, so the Lead can look before anything else is built.
2. **Toolkit (≤25):** new modules, each with an API docstring and a line in `docs/TOOLKIT.md`. Shared modules only if the brief says so, and then the pilot's `--keys` sheet must re-render unchanged.
3. **Build (≤60; a Short ≤30; a code fix ≤20):** the whole episode (or Short, or compilation), checked with stills.
4. **Render:** you code and check stills; the Lead renders. Return the exact chain (`python3 tools/handover_check.py <script> --verify &&`, hires pass, render, `python3 tools/check_video.py output/<file>.mp4 --landscape --no-loop --cuts <cuts>`, keys; vertical: drop `--landscape`; `--no-loop` unless it truly loops) and the estimate. Render yourself only if the brief says so. Never copy to `Videos/`.

## The standard
- One 1920x1920 world filmed by cameras; landscape 1920x1080 at 30 fps, 15 drawings a second on twos; `hires.set_res(2)`; zoom ≤2x (a closer shot only with a raised render scale for that shot, never in shared code); `render_video(..., workers=8)`.
- Expose `render_world(t, d, cam, bg)` and `make_buses()`; flags `--keys`, `--cuts`, `--still T`. Original synthesized audio only.
- Shorts re-film the same performances with a vertical camera: faces at about 40% of the height; nothing important in the bottom 19% or in the right 12% between 50% and 90% of the height; beats ≥0.8 s, key beats 1.5-4 s; their own music bed; sound effects cut with the pictures. A transformation Short has its own locked close-up camera.
- Compilations: ffmpeg concat of rendered episodes plus a new intro and outro; never re-render 30 minutes in one go.

## Self-checks before the full render
- **Your last command is `python3 tools/handover_check.py <script>`** on the final code, and it must PASS: audio loudness and silent gaps, the whole `--check`, key sizes (`--check` prints `keysize <t> <pct>` per key action of the plan, ≥2 times in its span, measured from the object's mask). A key miss you can see is fixed (≤3 code steps), never just listed. A camera change from the plan keeps every key object at the plan's size, or you ask the Lead. View ≤12 images per stage (images cost most).
- **Fix by fix:** a `--still` at every time a change touches (not one), listed per fix with its path; a fix with no still is "not checked".
- **Key sheet times from the changes:** every shot changed this round, its boundaries, and the fixed story beats (the cause, the lesson, the wow).
- **No reuse of rendered frames across rounds** unless the shot's code is unchanged, checked (e.g. a hash of its inputs).
- From the shot list: a face close-up after every gag, and no stretch over 6 s without a change (list any).
- **Every gag in the gag table:** an every-drawing strip from the set-up to the end of the reaction, with its measured seconds (pause, break, extreme hold, reaction) next to the plan's and the timing card's; the sound hit 1 drawing after the visual accent. A gag with no strip is "not checked".
- `--still` at every close-up; every-drawing strips of the key actions; a numeric clearance check for anything that flies or shines (≥30 design units from any face); lesson-critical props drawn in front; prop colours near any cutting scene (never plain white); the carry-forward checks.

## Known traps (each cost us a round)
- Props or paws hidden behind heads or bodies: draw lesson-critical props after the characters; `arms_front` for paws on faces.
- Elbows bend outward (+1 left arm, -1 right). The "focus" brows read as angry: use "think".
- Liquids fall, never climb; anything that flies starts at its source and never passes through a face.
- Small gags need a ≥1.2 s close-up, with the tool in front of the face.
- Tool tracks: tip spans must merge and the angle must ease, or the brush or marker points the wrong way.
- Heads turned past 36° crowd the edge; hugs need turns of about ±0.25 and spacing so faces stay visible.
- Thought clouds big enough, the "?" inside both the landscape and the vertical framing.
- Fast zooms or pans over fine stripes trip the jump check: ≤0.35x per second; on a laughing close-up use 1.55x, not 2.0x.
- Audio: arrays of equal length; pad and fade 0.25 s around gaps; normalise loudness last.
- In a re-cut, check every borrowed moment for something crossing the subject (a head, an ear) before using it.
- Episode scripts treat any unknown flag as "render everything": check the flags first.
- If the brief has you render: one foreground wait, never polling (each check-in re-sends your whole context; never
  `until ! pgrep -f ...`, it matches its own shell). Ask the Lead before any second full render.

## Return (≤150 words)
Per fix or item: PASS/FAIL with its still path or measured number; the render chain and estimate (or, if you
rendered, the check_video lines); anything you couldn't do.

## v3.7 additions (from `reviews/mistake_log.md`)
- M33 (edited code before proving the lantern-gap lines buildable; feasibility over its ≤5 budget): the feasibility stage returns at once when an estimate fails, before any code edit. Core rule 1.
