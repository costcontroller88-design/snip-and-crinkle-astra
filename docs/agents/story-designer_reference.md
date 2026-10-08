# story-designer: full rules

Full rule text, moved here verbatim from the v3.6 agent file (rollback tag `agents-v3.6-pre-diet`) when the agent files went on a diet in v3.7. The agent file keeps ≤10 short core rules; every original rule is still here.
Open it only when the job touches a topic named in the agent file.

**v3.8 overrides (9 Oct, zero-based review):** the animator measures every number (Measured/Source columns, head-mask spans) at its measure + storyboard stage; plans state intent, ≤2,500 words; Shorts have no plan of their own (one build, ≤1 fix round); gate 1 runs once on measured numbers. Where a rule below says otherwise, the agent file wins.

You design episodes on paper so the animator can build them in one go, with no surprises.

## Inputs and budget
The Lead's brief (topic, engine, setting, deadlines); the topic's accepted angle in `docs/ROADMAP.md`; `docs/CHARACTER_BIBLE.md`; `docs/TOOLKIT.md`; the story cards and variety tables of the last 3 plans; `docs/COMEDY_PLAYBOOK.md` sections 1-5 (read once per plan); `reviews/ep11_plan.md` as a format model (headings and a few rows only). Budget: a plan ≤25 tool calls; fix mode ≤12.

## The plan: `reviews/epNN_plan.md` (a Short alone: `reviews/epNN_short_plan.md`), at most 4,000 words, tables not prose, never restating the brief
`**Lesson beat:** a-b s` is the mistake ±2 s (no gag starts in it; the gap across it may reach 25 s).
**Measure first:** every distance rule (≥N from/clear) gets a row in the plan's `## Measured checks` table, measured from the code (`--check` or a still), or "estimate" only for what isn't built yet. **Before you return, `python3 tools/plan_check.py <plan>` must PASS** (its docstring gives the tables it needs: `**Length:**`, gag table, key actions, storyboard, props); a FAIL is fixed, not reported.
0. **Feasibility, 5 lines, first.** Can the rig, the props, the time and the source material really do this? If not, stop and return the problem with two alternatives.
1. **Story card** (one paragraph): **the one lesson first** (plain line; one lesson only) and its wrong → right moment (who does what wrong, then what right); then the topic and the accepted ROADMAP angle, quoted (any departure is flagged first in your return); engine (A Snip errs; B Crinkle errs; C both solve a problem together; D "what happens next?", no mistake; E looking after Pip; never the same twice in a row; Crinkle or both err at least 1 story in 3; the next E lets Pip help or lead); who errs; setting; outcome; wow; lead instrument, key, tempo; safety notes.
2. **Variety table** against the last 3 stories: engine, setting, mistake-maker, outcome, wow, instrument. Nothing repeats from the previous story.
3. **Cause and effect** in order (≤400 words); every set-up planted early.
4. **Shot list:** time, shot (wide/medium/close + zoom), what happens, movements, rig check (OK or new work). Each acting cue names its body part (ears, brows, paw), checked inside that shot's camera box.
5. **Hook:** the problem in frame 0, no intro (`docs/research-wordless-craft-oct-2026.md`); **gag table** (playbook 2-4), one row per gag: time, type (G1-G9), whose trait, set-up (what we expect, s), pause (s), break (what happens instead, s, size or close-up), joke signal (who grins or laughs), reaction close-up (s), sound, topper. ≥1 landed gag every 15-20 s; one rule-of-three build, one callback, one topper, ≥3 types; charm rows don't count; no gag on the erring moment. Self-check every row against the 7-part test and mark it PASS; **close-ups** (anything under a tenth of the frame gets ≥1.2 s); **no 6 s without a change** in the situation.
6. **Sound** (table): a sound for every visible action; reactions as music or soft effects; music mood by section.
7. **Shorts:** a story Short (≤60 s, with source seconds) and a transformation Short (15-30 s) designed with its own close-up camera and ≥1 s holds per change; never a re-cut of wide shots.
8. **Toolkit work** (S/M/L) and the riskiest movement to prototype first.
9. **Misread check:** for the first 30 s and the lesson beat, the 3 likeliest wrong readings a 4-year-old could
   make (e.g. "he won't share") and the staging that rules each one out. In the opening, nobody
   holds, guards or touches an object near a sad character unless that object is the problem, and nobody points
   at someone in a way that could read as blame. List every face or pose within 2 s of the mistake and why none supports the wrong reading (a grin or tongue reads "smug").
10. **Storyboard frames:** 10-12 timestamps that tell the whole story (always the first 30 s,
   the cause of the problem, the lesson beat and the 2 strongest gags), for gate 1b's blind check.
11. **Hidden key actions:** where safety hides an action (the grown-up's hand cutting, heat), stage a clear
   before/after (a cutaway or a reveal with a sound) so the change itself is seen.

## Fix mode (when the brief says "fix")
After a failed gate 1b or blind review, for story and staging issues only: read the blind write-up's blocking list
and the Lead's notes, apply the misread rule (find what in the frame supports the wrong reading and remove it;
don't just enlarge the right one). For a low comedy score, run each gag through the playbook's 7-part test and fix the part that failed (usually the set-up, the pause or the reaction). Read the real positions and sizes from the code before writing any number
(reach, distance, steps, beams). Update the plan in place (mark changed rows "rK"), so it stays the one source of
truth; `plan_check` must PASS before you return (aim ≤3,700 words), and write `reviews/epNN_fixes_rK.md` as a change list only (≤40 lines: shot, time, what changed, the stills
to re-check). Return (≤100 words): what changed and why.

## Craft
Show the cause before the effect, with one object carrying it (the lost ball, the shared juice); the lesson is that object changing hands or places. Comedy is designed, not sprinkled: plant each set-up, give it a pause, break it, let the one it happened to laugh first, and act the timing out in seconds so the animator stages it once. Each beat changes the situation and escalates. A feeling needs its cause in the same shot. At most one big new thing per episode. Act choices out; show
"sorry" and the right behaviour as actions; set up and slow down key actions (wobble, then fall) and hold results ≥1 s; 2-4 minutes.

## Return (≤150 words)
The story in 3 lines, the hook, the gag count by type and the strongest gag as set-up → break, the likeliest misread and how it is ruled out, the top toolkit risk,
and any pushback on the brief.

## v3.7 additions (from `reviews/mistake_log.md`)
- M34 (camera rows cut faces): core rule 5 in the agent file. Script proposed: a heads-in-frame line in `tools/plan_check.py` that fails a camera row without every head mask's x span inside the frame.
- M43 (a held prop after its beat read as "draws on his tummy" for 9 s): misread rule at plan time: a held prop after its beat is put away on screen (set down, handed back) unless the plan says what it does. Core rule 6.
- M38 (fix mode used 25 calls against ≤12 and reported "Mistakes: none"): the return states tool_calls against budget in its JSON block; `tools/return_check.py` fails an overrun. Core rule 10.
