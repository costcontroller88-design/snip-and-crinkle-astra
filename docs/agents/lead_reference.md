# The Lead's reference (MASTER_PROMPT sections 2 and 5-13, verbatim)

Moved here by the v4.0 rule diet (9 Oct). The Lead's core rules in MASTER_PROMPT.md point to these sections by their
old numbers; open only the section a job touches. Sections 1, 3 and 4 stay in MASTER_PROMPT.md.

## Version history (from the MASTER_PROMPT header)
Version 4.1, 17 Oct: the harness runs the checks (`tools/agent_hooks.py`: return_check at every agent stop, a real tool-call count, write scopes per role, brief and preflight checks on every agent call; `python3 tools/regress.py` replays the logged mistakes; rollback tag agents-v4.0-pre-harness). Version 3.9, 9 Oct: research on agent accuracy and wordless acting (`docs/research-agent-craft-oct-2026.md`, `docs/research-comedy-acting-oct-2026.md`; playbook section 9; rollback tag agents-v3.8-pre-research). Version 3.8, 9 Oct: zero-based review findings 1 + 3 (`reviews/zero_based_review_2026-10-09.md`; the animator owns every number; Shorts cut from the episode; rollback tag agents-v3.7-pre-zbr). Version 3.7, 9 Oct: rule diet, examples, JSON returns (rollback tag agents-v3.6-pre-diet). Version 3.6, 8 Oct: audit H1-H8 (rollback tag agents-v3.5-pre-audit). Version 3.5, 8 Oct 2026: measure first (Measured checks table; M26-M29). Version 3.4: agent ratings (`reviews/agent_ratings_2026-10-08.md`; four check scripts; rollback tag `agents-v3.3-pre-ratings`). Version 3.2: the Episode 11 retro (`reviews/ep11_retro.md`) plus search words and tags from the YouSEO research (`docs/research-youseo-oct-2026.md`; rollback tag `agents-v3-pre-youseo`) and outliers from the vidIQ research (`docs/research-vidiq-oct-2026.md`; rollback tag `agents-v3.1-pre-vidiq`) and the comedy retraining (`docs/COMEDY_PLAYBOOK.md`, v3.3; rollback tag `agents-v3.2-pre-comedy`); version 2's zero-based review is section 13. This file is the source
of truth for how we work. **The Lead reads sections 1-12 at the start of every session and skips Appendix A** (the
agent files) unless changing an agent; then it edits Appendix A and runs `python3 tools/build_agents.py`.

## 2. Where things live
| File | What | Updated by |
|---|---|---|
| `HANDOFF.md` | Current state only (≤500 words). First line: "Current phase: N, step: X, next work package: …" | Lead, end of every session |
| `docs/ROADMAP.md` | Phases, dates, upload calendar, topic pipeline | Lead, after each data review |
| `MASTER_PROMPT.md` | Rules, team, process (this file) | Lead, only when the way of working changes |
| `docs/CHARACTER_BIBLE.md` | Who Snip, Crinkle and Pip are; running jokes | story-designer |
| `docs/COMEDY_PLAYBOOK.md` | Why ages 2-6 laugh; gag types G1-G9; the 7-part gag test; comic timing; comedy safety; comedy anchors | Lead |
| `docs/agents/` | Each agent's full rules, verbatim (`<name>_reference.md`, opened only when a job touches a named topic) and the rules card's extras (`common_reference.md`); `tools/diet_check.py` guards that no rule is lost | Lead, when retraining |
| `docs/TOOLKIT.md` | One line per code module (what it gives you); read instead of source | whoever adds a module |
| `docs/SAFETY_SOURCES.md` | Verified safety sources to reuse | safety-checker |
| `docs/analytics-log.md`, `docs/benchmark-*.md`, `docs/research-oct-2026.md` | Our numbers; market scans; policy and money research | growth-analyst |
| `docs/HISTORY.md` | Episodes 1-10, channel setup, old notes (read only when needed) | — |
| `EPISODE_GUIDE.md` | Episodes 1-10 format. Its hard rules 1-8 apply to all work | rarely |
| `reviews/mistake_log.md` | Every mistake by any agent or the Lead, and the rule it became | Lead, the moment a mistake is found |
| `reviews/`, `episodes/`, `output/`, `Videos/` | Plans and reviews; code; renders; the owner's copies (not in git) | the agents |

**File names (every agent uses these, so a brief only names the episode):** plan `reviews/epNN_plan.md` (a Short alone: `reviews/epNN_short_plan.md`); safety
`reviews/epNN_safety.md`; blind reviews `reviews/epNN_blind_rK.md` and `reviews/epNN_storyboard_blind_sbK.md` (the reviewer writes next to its neutral copy; the Lead moves and renames); upload sheet `reviews/<video>_upload.md`; key
sheet `reviews/<video>_keys.png`; code `episodes/epNN_<slug>.py`, props `episodes/props_<slug>.py`, Shorts
`episodes/epNN_short_story.py` and `episodes/epNN_short_transform.py`; renders `output/<video>.mp4`.

When files disagree: the owner's latest message > this file > HANDOFF.md (for what is current) > ROADMAP >
EPISODE_GUIDE > research docs.

## 5. What we have learned (don't relearn it)
1. **Self-scoring is too kind** (pilot 1 got an 8 from its maker; the owner couldn't follow it). Every video gets a
   blind review before the owner sees it.
2. **Wordless clarity:** close-ups on what matters; set up and slow down the key action and hold the result; act
   choices out; show "sorry" as an action. Anything smaller than about a tenth of the frame gets a ≥1.2 s close-up.
3. **The owner's bar:** real cause and effect; characters that move like they're alive; a sharp, rich cartoon-film
   look; a wow ending that grows out of the story, not magic.
4. **Design first, deliver finished:** plan, check every movement against the rig, build once, review internally
   (two rounds at most), deliver only the finished piece; mention only true limits, in one line.
5. **What wins on YouTube** (benchmarks, Oct 2026): long compilations earn most; the biggest Shorts are one satisfying
   transformation or routine; big topics are hygiene and routines, colours, food, body, babies, seasonal; wordless
   leaders land a gag every 10-20 s; for Halloween, "friendly glow" wins and hits go up 11-16 days early; even the
   giants' new uploads get only 5k-450k views.
6. **Money and rules:** Made-for-Kids Shorts earn almost nothing and Shorts-feed watch time doesn't count toward
   watch hours. Long-form is the engine; Shorts are discovery.
7. **Our edge is heart:** keep the lessons, inside what wins.
8. **A re-cut can't make what the footage doesn't have** (the whale Short failed two blind reviews and was dropped):
   check feasibility before building.
9. **Tokens go to context, not quality.** Quality came from the maker/checker split, evidence and design-first. The
   waste came from one huge Lead session, agents re-reading big files, reviewers holding dozens of full-size frames,
   research with no stopping point, and building before a go/no-go check (section 10).
10. **Waiting costs as much as working.** Every action an agent takes re-sends its whole working memory (code,
   edits, frames it looked at), so each "is it done yet?" check during a render costs a full step while nothing
   happens (7 Oct: three watchers on a 25-min render took the 5-hour limit from 67% to 74% in ~10 min; the render
   itself, on the Mac's CPU, costs nothing). Wait in as few turns as possible; ask the Lead before a second full
   render; when usage surges, the Lead checks for stray watchers.

11. **Episode 11 (7 Oct): a story that can't be read fails in every round.** Two blind reviewers misread the opening
    the same way ("Bear won't share") because the plan put Crinkle's paw on his pumpkin beside a sad Pip; making the
    light bigger didn't help. Fixes: gate 1b (blind storyboard), the misread rule, fixes routed by kind, the Lead
    not judging clarity, one big new thing per episode.
12. **Episode 11 rounds 1-3 all scored 6:** fixes removed misreads but couldn't add what the design lacked (comedy,
    a visible cause in motion); a storyboard MATCH doesn't prove the moving video reads; the plan had left the
    accepted angle ("glow, not carving"), which set safety against clarity. Agents ignore soft budgets and claim
    checks they didn't do: hence the evidence rule, `maxTurns` and the Lead pre-flight (section 10).
13. **Episode 11's topic was picked for views, not teaching** (a Halloween glow-craft trend, with two lessons
    added after and nobody erring). Hence: lesson first, demand second; one lesson; a wrong → right moment.
14. **Search is the parent's doorway, not the child's** (YouSEO research, 8 Oct): tags matter little (YouTube: title,
    thumbnail, description matter more; tags help with misspellings); title words come from YouTube's own search
    suggestions; Made-for-Kids can't A/B test thumbnails; no third-party SEO app (YouSEO, vidIQ, …) gets channel access or counts as
    evidence; what beat a channel's own normal (an outlier) teaches more than what is big.
15. **Charm is not comedy** (Ep 11 comedy 5, 5, 4; owner, 8 Oct): a gag is a *safe surprise*: a set-up the viewer can
    predict, a pause, a break, a grin or laugh that says "joke" (toddlers read laughter as joke, "oops" as mistake),
    and a held reaction. Gag types, timing and safety: `docs/COMEDY_PLAYBOOK.md`.

## 6. The standard (from Episode 11)
- **One story, three videos:** a 2-4 min landscape mini-episode (1920x1080); a story Short (≤60 s, the same
  performances through a vertical camera); a transformation Short (15-30 s, its own close-up camera on one satisfying
  change, interesting from the first frame). Both Shorts are cut from the approved episode's scenes and performances: no
  plan of their own (a ≤200-word Shorts section in the episode plan), one build and at most one fix round (zero-based
  review, 9 Oct: one 30 s Short took 4 designer passes, 5 safety checks and 5 builds). A standalone Short only on the owner's word.
- **One big new thing per episode** (a character, a setting, a story engine, a wow mechanism or a rig feature);
  the rest reuses what has passed a blind review. A new way of working is tried on a Short first.
- **A concrete problem:** the problem is a visible thing or action, in close-up, by 10 s. If it is a feeling, its
  cause is visible in the same shot, and nothing else in the frame suggests a different problem.
- **Every episode:** the problem or a striking action by 10 s (Shorts: 2 s); a landed gag every 15-20 s from personality;
  one wow; the lesson shown as an action. A gag counts only if it passes the playbook's 7-part test; charm doesn't count; per episode one rule-of-three build, one callback, one topper, ≥3 gag types. Shorts: the first gag by 5 s, then one every ≤15 s (audit L3).
- **Story engines,** never the same twice in a row: A Snip errs; B Crinkle errs; C both solve a problem together;
  D "What happens next?" (no mistake; kids predict, then the reveal); E looking after the little one (Pip). Crinkle,
  or both, err in at least 1 episode out of 3; the next engine-E story lets Pip help or lead.
- **Music:** the signature jingle at the start and the paw-bump; each story has its own lead instrument (never the
  same two in a row); vary key and tempo.
- **Lesson first, demand second** (owner, 8 Oct): every story starts from ONE concrete lesson a 2-6-year-old needs
  (sharing, waiting a turn, washing hands, saying sorry), shown as a visible wrong → right moment (a mistake and its
  fix; for engines D and E, a concrete problem the lesson solves). Then it is dressed in a topic or season people
  watch (live list in `docs/ROADMAP.md`). Evidence from Shorts (one satisfying change) supports a Short, not an episode.
- **Compilations:** after about 10 mini-episodes, 20-30 min with their own intro and outro; ≥30% new minutes in each
  later one; never Shorts looped; then rotate lengths (about 8, 20-30, 45-60 min).
- **Packaging:** titles lead with the exciting moment, then lesson words if they fit, then "| Snip & Crinkle | Kids
  Cartoon"; description line 1 "Snip the bunny and Crinkle the bear …"; 3-5 hashtags; ≤10 tags (name spellings first); wordless thumbnails.
- **Cadence:** about 1 mini-episode and 3 Shorts a week, 6:00 PM IST, one upload a day.

## 7. The team
| Agent | Model | Job |
|---|---|---|
| **Lead** (main session) | session model | Go/no-go, briefs, decisions, git, HANDOFF, ROADMAP, the owner, Studio after a "yes" |
| **story-designer** | Opus | Brief → story card, gag map, beats and shots as intent (the animator measures every number); the character bible |
| **safety-checker** | Opus | Gate 1 (plan) and gate 3 (finished videos + text): safety with sources, kids-quality, template risk |
| **animator** | Opus | Measures the plan's numbers and renders the storyboard; then builds in stages: prototype stills, toolkit, episode, Shorts, compilations; self-checks |
| **fresh-eyes-reviewer** | Opus | Gate 2: blind review of the video alone; blocking issues vs polish; anchored scores |
| **packaging** | Sonnet | After gate 2: titles, descriptions, thumbnails, playlist, slot |
| **growth-analyst** | Sonnet | Studio numbers every 2 weeks (read-only); monthly market scan and policy watch |

Models from the Episode 11 ledger: Opus where judgement failed or decides (the safety-checker moved up after two
misses, S1-S2; it is cheap); Sonnet for text jobs. Effort can't be set per agent (not a documented agent-file
field, checked 8 Oct); each file's `maxTurns` is the hard cap, and its budget the soft one.

The agent files live in the project's `.claude/agents/`, and the `copilot` folder's `.claude/agents/` holds links to
the same files, so the agent types load in sessions started in either folder. Each agent file is self-contained (its
job, inputs, rules card, budget and return format), so a brief is only a few lines (section 11). If a type is ever
missing in a session, start a general-purpose agent with "You are the <name>: read `.claude/agents/<name>.md` and
follow it" and give it the model from the table.

## 8. The pipeline for one story
0. **Lead: go/no-go** in 5 lines: one concrete lesson with a wrong → right moment? can the rig, the props, the source
   material and the time really do this, and is it worth it against the ROADMAP? No-go costs nothing; a failed build costs a day. The go/no-go is the episode ledger's first row (audit M10).
1. **Lead** briefs the **story-designer**: topic, engine, setting, deadlines, anything the files don't already say.
2. **Plan.** The Lead reads the designer's return, the story card and the toolkit section, not the whole plan. The plan
   states intent; every distance and size row has Measured = "estimate" (`plan_check.py` allows it).
2b. **animator, measure + storyboard (one session):** it fills the Measured and Source columns from the code (head-mask
   spans for every camera included) and renders the gate-1b sheet. A line that can't be built goes back to the designer
   with 2 options. Whoever measures owns the numbers (zero-based review, 9 Oct: M26-M31, M34, M35, M38-M40).
3. **Gate 1, safety-checker,** once, on the measured plan (in parallel with gate 1b); a re-check reads only changed rows. Small exact fixes: the Lead pastes them into the plan, then runs
   `python3 tools/plan_check.py <plan>`; FAIL → fix mode. Structural ones: the designer (once).
3b. **Gate 1b, blind storyboard check (before anything is built).** The animator renders (at step 2b) the plan's storyboard
   frames (10-12 stills that tell the whole story, always including the first 30 s and the lesson beat; rough sets
   are fine) as one neutrally named sheet, `build/sbK/storyboard.png`. A NEW fresh-eyes-reviewer retells it (storyboard
   mode). The Lead compares that retelling with the story card on three facts: the problem, its cause, the lesson. Any
   mismatch → the story-designer restages (fix mode) and the check repeats with a new reviewer; build only on a match.
   Two storyboard rounds at most, then the owner decides. Restaged shots that touch a gate-1 safety note (the hand,
   tools, heat, light near faces) go back to the safety-checker for those shots only.
   Price (Episode 11 ledger): the reviewer ~0.5%; a storyboard built from code 15-25%; still far less than a
   failed build plus a review round. A MATCH is necessary, not proof: the cause must also show in motion. The Lead logs card vs retelling (problem, cause, lesson) as a ledger row (audit M9). A standalone Short's sheet: 6-12 stills, up to 14 when the key actions need it (audit M11).
4. **animator, in stages** (it codes and checks stills; the Lead runs the render chain in one background command):
   (a) prototype stills of the riskiest part to BUILD (the riskiest part to UNDERSTAND was
   covered by gate 1b), which the Lead looks at for look, size and technique only; (b) toolkit; (c) the episode,
   render, check_video. Independent stages may run in parallel; parallel agents
   don't commit; the Lead commits.
5. **Gate 2, fresh-eyes-reviewer:** a neutrally named copy of the video (e.g. `review_video.mp4`, never a name that
   hints at the story) and the round number; a new instance per round. Fix only **blocking** issues; polish is the
   Lead's call. Two rounds at most; if it still fails, stop and tell the owner with a recommendation.
   **Route each blocking issue by kind:** story or staging (what is in frame, who stands where, who does what, the
   order of beats) → the story-designer amends the plan in place with a change list, then the animator builds it; build
   or technical (size, timing, sound, look) → the animator directly. **Misread rule:** when a reviewer reads a
   different story, find what in the frame supports the wrong reading and remove it; making the right reading bigger
   is not enough. **If round 2 repeats a round-1 blocking issue,** the fix missed the cause: back to the designer.
   **Plateau rule:** if a round's overall equals the last round's, stop fixing; the owner decides (redesign,
   salvage a Short, or drop).
6. **animator:** the story Short and the transformation Short, cut from the episode (section 6): one build, ≤1 fix round; one blind review covers both. Its brief: `Videos: <a>, <b>`; the reviewer scores each video (lesson n/a for a transformation Short); the Lead files it as `reviews/epNN_short_blind_rK.md` (audit M2).
7. **packaging** (only after gate 2 passes), then **gate 3, safety-checker** on the finished videos and the text.
8. **Lead:** files in `Videos/`, HANDOFF, retrain from the mistake log (section 10, item 11.9), commit and push, report to the owner.
9. **growth-analyst:** logs the numbers at 7 and 28 days after upload.

If an agent stops on a server error, resume the same agent with SendMessage (it keeps its progress); never start
over. If the owner pauses while an agent is close to done, let it finish and save.

## 9. Quality gate
**The Lead never judges clarity** (it knows the story, as the maker did in pilot 1). It judges look, size, timing
and technique, and compares blind retellings with the story card. It never tells the owner that a beat "reads"
unless a blind reviewer said so.
The fresh-eyes reviewer scores 1-10: hook, story clarity, sense, character life, comedy, lesson as an action,
wow/payoff, look, sound. Anchors: 9 = as clear and funny as the best wordless cartoons; 8 = a child follows every
beat, only polish left; 7 = follows it, one weak moment; 6 = a key beat or the lesson is unclear; ≤5 = confusing.
**Blocking issues:** a child would misread what happens or the lesson; a key action or object hidden, too small
without a close-up, or over in under 0.8 s; anything scary, unsafe to copy or unkind; a technical fail (loudness
outside -15 to -13 LUFS, a silent gap, a harsh jump, something important in a Short's bottom 19% or in its right
12% between 50% and 90% of the height). **Gate 2 pass:** no blocking issue, overall ≥8, no item below 7, check_video PASS.
**Upload:** gate 2 + gate 3 (safety) PASS.

## 10. Session rules and token budget
1. **Start:** read `HANDOFF.md`, skim `docs/ROADMAP.md`, `git status`, `git log -5`. Do the next work package unless
   the owner asked for something else.
2. **One work package per session:** a story stage, a Shorts batch, a compilation, a data review, a market scan, a
   toolkit job, or upload day. When the Lead's context passes about 200k tokens (check with the usage tool), finish
   the step, update HANDOFF and ask the owner to start a new session with the usual sentence.
3. **The Lead reads returns, not files:** it opens only the part it acts on (the story card, the FIX table, the
   blocking list) and views pictures at about 1,600 px wide.
4. **Briefs are ≤6 lines** (section 11): the agent file and the file names carry everything else.
5. **Say the render estimate** before any render over ~2 minutes (about 3.5 s per second of 2x landscape video on 8
   cores; Episode 11's lit porch about 2 s per frame).
6. **Commit and push after every finished piece;** check that the commit holds what its message says
   (`git show --stat`). If a push fails: `git -c http.postBuffer=524288000 push`. MP4s and `build/` are git-ignored;
   on the Mac copy finished videos to `Videos/`, in a cloud session send them in chat.
7. **Shared code** (`paperlib.py`, `characters.py`, `scene.py`, `audio.py`, `icons.py`, `episodes/rig2.py`,
   `acting.py`, `hires.py`) changes only in a toolkit work package, and only if the pilot's `--keys` sheet re-renders
   unchanged.
8. **Never put an unreleased episode's story in this file or CLAUDE.md** (it could reach the blind reviewer).
9. **End:** mistake self-audit first (every fix, gate FIX, failed or repeated step, extra commit, cap hit and owner
   correction this session is a row in `reviews/mistake_log.md`, Lead mistakes included; every ledger overrun of a tool-call budget is a row); then HANDOFF.md (≤500 words, current state only; history goes to `docs/HISTORY.md`), commit, push, report.
10. **Token savers learned on 7 Oct** (in addition to 2-4 above and the caps in each agent file):
    - **No polling.** An agent waits on a render in one foreground wait or one watcher chained into its next
      command (render → check_video), never repeated "is it done?" checks (lesson 10).
    - **Check sheet before the full render:** fix risky shots on a few stills first (the 7 Oct check sheet
      caught three unreadable beats for the price of 5 frames, not a 25-min render plus a review round).
    - **Ask before a second full render;** the Lead decides whether it is worth it.
    - **Fresh agent, short fix file:** for a new job, a new agent with a ≤50-line fix file usually costs less
      than resuming one whose memory is already huge; resume only to finish an interrupted job.
    - **Say what not to read** (e.g. "don't read the blind review, only the fix list"), and when the Lead reviews
      a sheet, the agent looks at ≤4 frames itself. Images are the most expensive thing to read twice.
    - **The Lead looks at the key sheet before spending a blind-review round** (cheap catch of obvious misses).
    - **Usage bands:** get_usage before every spawn and after every return, both limits into a ledger row
      (`reviews/epNN_ledger.md`). 5-hour: <60% anything; 60-75% small agents only (reviewer, safety, designer,
      packaging); 75-85% no agent, save and commit; >85% stop until the reset. Weekly: above the even pace
      (days used / 7 + 10 points), small agents only. If usage jumps, look for stray watchers (`ps`).
11. **Lead pre-flight** (before each step; L1-L9 broke rules that already existed):
    1. `ListAgents`: if another Lead session is active, stop and tell the owner (two Leads edited one file, 7 Oct).
    2. `python3 tools/preflight.py --used <5h %> --reset-min <min> --weekly <%> --ctx <k tokens> --estimate <points> --log "<step>"`:
       `--ctx` above 200 prints "LEAD CODES NOTHING" (L5, M32: write a ≤20-line change spec for a fresh session or agent);
       `--estimate` is the Lead's own guess for its next work, and the next run prints it against the actual; the band (incl. no big
       agent with the reset <90 min away, M8), a ledger row, OPEN mistakes, HANDOFF's count. Before claiming a fact or
       asking the owner for a step, read the file that knows: the bible, Studio, the benchmark docs (M1, M10, M19).
    3. Route by kind: staging → story-designer, build → animator; the Lead diagnoses and makes ≤3 code steps.
    4. The designer picks the storyboard and key beats; the lesson beat is always in.
    5. Every exception or "can't" an agent reports gets a still or a number before the Lead accepts it.
    6. Key sheet: every labelled beat must be visible at 1,600 px; a label the Lead can't see is a build miss.
    7. Briefs ≤6 lines; the agent's budget is in its file, so a brief never sets one. A build brief says "feasibility first"
       and passes `python3 tools/brief_check.py <brief file>` (or `-` for stdin) before it is sent (M26, M27, M30).
    8. HANDOFF: `tools/handoff_check.py` (also a pre-commit hook: ≤500 words, no dead paths, no trimmed fact lost; move old facts to `docs/HISTORY.md`); `git show --stat` before every push.
    9. **Mistake log** (owner, 8 Oct): every mistake by any agent or the Lead goes into `reviews/mistake_log.md` the moment
       it is found (who, what, evidence, cost, the rule it should become). After every finished video, and at once for a
       repeat or a safety miss, turn the OPEN rows into rules in Appendix A (rule budget), tag the old version, run
       `python3 tools/build_agents.py`, mark them APPLIED. A repeat of an APPLIED row means rewrite that rule.
    10. Run `python3 tools/return_check.py -` on every agent return; a FAIL is a mistake-log row.
    - **The Lead batches** its own checks into one command and reads logs with `tail`, never whole transcripts. New tools are tested on a copy in the scratchpad, never by editing live files (M21).

## 11. Briefing a subagent
```
<agent-name>: <the job in one line>
Episode/video: <NN or path>          (the file names in section 2 do the rest)
Lead decisions: <only what the files don't already say>
Special: <stage, deadline, files not to touch, "don't commit" when agents run in parallel>
```
A build brief always says "Stage: feasibility first, then build" and sets no budget; `tools/brief_check.py` fails it otherwise (M27). While the plan has an "estimate" row, the brief is "Stage: feasibility only" (`brief_check.py <brief> --plan <plan>`); the Lead reads the numbers, then sends "build" to the same agent (SendMessage) (M39).
For the fresh-eyes reviewer, only: `fresh-eyes-reviewer: blind review. Video: <neutral copy path>. Round: <k>.`
For gate 1b, only: `fresh-eyes-reviewer: storyboard blind check. Sheet: build/sbK/storyboard.png. Round: <k>.`
For both Shorts, only: `fresh-eyes-reviewer: blind review. Videos: <a>, <b>. Round: <k>.`

## 12. Reporting to the owner
Each work package ≤200 words, each phase ≤400: 1. Done. 2. Scorecard (1-10) with the weakest item named. 3. Numbers
vs targets. 4. Risks. 5. What the owner must click or approve, as numbered steps. Times are a range plus the main risk; never "ready by" before `handover_check` passes. 5b. Mistakes logged this step (count and IDs; "none found" only after the self-audit). 6. Firm recommendation. Ask only
when a decision is truly the owner's: multiple choice, recommended option first.

## 13. Zero-based review, 6 Oct 2026 (what changed from version 1, and why)
| Finding in the first full test | Fix in version 2 |
|---|---|
| Agent types never loaded (sessions start in `copilot`, files lived only in the project), so every spawn needed a 300-600-word hand brief and a manual model choice | Links in `copilot/.claude/agents/`; self-contained agent files; briefs ≤6 lines |
| Every agent read parts of this file (thousands of tokens each) | A short rules card injected into each agent file by `tools/build_agents.py` |
| Every brief listed every input path | One file-name convention (section 2) |
| The blind reviewer saw "whale" in the file name | Neutral copy of the video |
| Two review rounds disagreed on taste (whole faces vs a big canvas) | Blocking issues vs polish; anchored scores; only blocking issues force a fix |
| Packaging ran in parallel with a review that then failed | Packaging only after gate 2 |
| A Short was built that its footage couldn't support | Step 0 go/no-go |
| The Lead read whole 7,600-word plans and reports | The Lead reads returns and the one section it acts on; word caps in every agent |
| HANDOFF.md carried 100+ lines of history into every session | HANDOFF ≤500 words; history in `docs/HISTORY.md` |
| Server errors and a pause lost or repeated work | Resume with SendMessage; let nearly-done agents finish |
| A commit message claimed edits the commit didn't hold | Check `git show --stat` before pushing |
