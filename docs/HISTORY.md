# History (moved out of HANDOFF.md on 6 Oct 2026 so each session reads only the current state)

Episodes 1-10, channel setup, the pilot's toolkit notes, the old "how to work" steps and upload log, as they stood
in HANDOFF.md. Read only when you need a detail from that time.

Short: `episodes/pilot02_short.py` re-films the episode's performances through a vertical camera (shot list in
`reviews/pilot02_short_plan.md`), cuts the episode's sound effects with the pictures and adds its own music bed.
The episode exposes `render_world(t, d, cam, bg)` and `make_buses()` for this. check_video now allows vertical
videos up to 180 s (Shorts limit).
How to work now (owner's rule, 2026-10-06): design the whole thing first (shot list + every movement checked against
the rig), build in one go, review internally (1-fps sheet, motion strips, full-size close-ups, numeric checks,
check_video) for at most two rounds, and show the owner only the finished piece. No fixable weakness reaches them.
The pilot: `episodes/pilot02_splash_of_blue.py` ("Oops! A Splash of Blue", 124 s, 1920x1080 at 2x render, ~7 min
render on 8 cores). Plan: `reviews/pilot02_plan.md`. Final file: `output/pilot02_final.mp4` (video + rebuilt audio).
Toolkit: `episodes/rig2.py` (turning heads with a ball projection, head-only turn `hturn`, elbows + IK, planted
walking, `face_point`), `episodes/hires.py` (2x sprites), `episodes/props_splash.py` (table, jars, block, whale
splash and its painted layers, thought cloud), `acting.py` brows incl. "think" (do not use "focus": it reads angry).
Pilot v1/v2 (`episodes/pilot01_sorry_test.py`, old rig, 1x) are kept for reference only.


You are continuing work for the owner of the YouTube channel **Snip & Crinkle (@SnipAndCrinkle)**, a wordless kids' Shorts channel made entirely with this code. The owner is not technical and relies on you to make decisions and do the work. They like a thorough analysis from all angles followed by a firm recommendation, and **harsh, honest ratings** (score 1–10 and say what is weak). They are in India.

## Where things stand
- **Channel setup is done:** name, handle, banner and profile picture (`tools/brand.py`), description, keywords, **made for kids = Yes**, country = India, and upload defaults (Education, language "Not applicable", footer description). Optional: default tags are still empty. The owner still has to turn on 2-Step Verification.
- **Episode 1 is final:** `episodes/ep01_v3_can_snip_wait.py` ("Can Snip Wait?"), scored 8/10, and passes `tools/check_video.py`. Render it with `python3 episodes/ep01_v3_can_snip_wait.py`. MP4s are git-ignored.
  - Upload title: `Can Snip Wait? ⏳☕ | Snip & Crinkle #shorts`
  - Upload description (goes above the default footer): "Snip wants the yummy drink… but it's HOT! ✋ or ⏳? What should Snip do? Wait with Snip & Crinkle and count 1, 2, 3 until it's cool! ☕✅"
- **Episodes 2–5 are finished** (merged into `main`), each scored 8/10 overall with no item below 7, and each passes `tools/check_video.py`. Scorecards, remaining weaknesses and upload text are in `reviews/epNN.md`; key-frame sheets in `reviews/epNN_keys.png`.
  - Ep 2 `episodes/ep02_wash_before_you_munch.py` (bathroom, friendly germs, wet-soap-scrub-rinse-dry)
  - Ep 3 `episodes/ep03_the_last_cookie.py` (evening kitchen, tug-of-war tumble, break in half and share)
  - Ep 4 `episodes/ep04_whose_toy_is_this.py` (park, teddy ears pop up, give the toy back to the duckling)
  - Ep 5 `episodes/ep05_hold_paws_to_cross.py` (street, wind-up legs skid, wait for green, look both ways, hold a grown-up's hand)
- **Episodes 6–10 are finished** (made in five parallel cloud sessions, one per episode, then checked and merged into `main` by the coordinating session). Each scored 8/10 overall with no item below 7 and passes `tools/check_video.py` (re-verified by re-rendering). Reviews in `reviews/ep06.md` … `reviews/ep10.md`.
  - Ep 6 `episodes/ep06_achoo_elbow_sneeze.py` (playroom, block tower blown down by a sneeze, sneeze into the elbow)
  - Ep 7 `episodes/ep07_helmet_on.py` (garden, tricycle, helmet popped off by the ears, helmet + strap click + wiggle test)
  - Ep 8 `episodes/ep08_your_turn_swing.py` (playground, twist-and-spin dizzy gag, take turns with Pip, gentle pushes)
  - Ep 9 `episodes/ep09_buckle_up.py` (car cut-away, bouncing on the booster, click-click-thumbs-up before the car moves)
  - Ep 10 `episodes/ep10_hot_sunny_day.py` (beach, hot-sand hops, noodle ears, hat + shade + water sips)
- **Delivered:** the MP4s for Episodes 6–10 were sent to the owner in the Claude chat (2026-10-05); Episodes 9 and 10 take ~12 min each to render.
- **Delivered:** the MP4s for Episodes 1–5 were sent to the owner directly in the Claude chat (2026-10-05). GitHub Releases could not be created: cloud sessions get "Creating, editing, or deleting releases is not permitted for this session type" (HTTP 403). MP4s are git-ignored; re-render any episode with `python3 episodes/<file>.py` (~5 min each).
- **Ep 5 and Ep 9 v2 (2026-10-05):** jointed grown-up arm (`episodes/props_grownup.py`) and their own story music (`episodes/music_extra.py`: toy piano + melodica for Ep 5, organ + steel pan for Ep 9). Both pass `check_video.py`; v2 scorecards appended to `reviews/ep05.md` and `reviews/ep09.md`. MP4s delivered to the owner's Mac as `Videos/ep05_hold_paws_to_cross_v2.mp4` and `Videos/ep09_buckle_up_v2.mp4`; Ep 9 then got a v3 (drive livelier, stops at a visible beach, beach-ball wipe loop instead of the heart iris), delivered as `Videos/ep09_buckle_up_v3.mp4`. Upload v3, not v2. New guide rules 7 (music variety) and 8 (vary who makes the mistake).
- **YouTube uploads (2026-10-05):** Ep 10 published. Scheduled 6:00 PM IST: Ep 1 (6 Oct), Ep 3 (7), Ep 4 (8), Ep 2 (9), Ep 6 (12), Ep 7 (13), Ep 8 (14). All in the public playlist "Snip & Crinkle Stories". Ep 9 v3 and Ep 5 v2 are not uploaded yet (planned: 15 and 16 Oct).
- **Tips learned:** zooms or fast pans over fine stripes (zebra crossing, gingham cloth) trip the "harsh jump" check; keep zooms slow (≤ ~0.35 zoom/s) or pan sideways instead. Review frames with `python3 tools/review_frames.py <episode.py> out.png t1 t2 …` and measure jumps with `python3 tools/frame_jumps.py <episode.py> t0 t1 …` before a full render. Parallel cloud sessions (one per episode, each on its own branch, never touching shared files) worked well for batches.

## Strategy research
Read `docs/research-oct-2026.md` (5 Oct 2026): key points are to vary story engines (inauthentic-content policy), make original long-form 20–30 min compilations the monetization engine, plan for the 1 Feb 2027 YPP bar (8,000 hours or 20M Shorts views), and use plain-language titles ("<Lesson>! Kids Safety Cartoon | Snip & Crinkle").

## How to work (Episodes 1–10, old format; new work follows MASTER_PROMPT.md)
1. `./setup_cloud.sh` (ffmpeg, Pillow, numpy, Fredoka font).
2. For each episode: continue its branch, render stills, **look at key frames at full size** (props hidden behind characters is the most common bug), render the MP4, run `python3 tools/check_video.py output/<file>.mp4` until it PASSes, and score with the rubric (overall ≥ 8, no item < 7).
3. **Deliver MP4s to the owner** by sending the files in the chat (GitHub Releases are blocked in cloud sessions). Also merge finished episode branches into `main`.
4. Report to the owner in plain language: what is done, the scorecards, and exactly what they need to do next.

## Limits
- Don't change YouTube account settings yourself. The owner's permission settings block it, so ask them to click.
- No emoji fonts in videos (use `icons.py` paper icons) and only original synthesized audio. Child-safety accuracy is mandatory: dangerous things are handled by the grown-up's hand.

## Pilot and test plan (decided 2026-10-06)
- **Owner's role is uploading only.** No listening, kid-testing or voice recording. Design every check to need none of that.
- **Owner said yes to reading YouTube Studio** in the built-in browser, read-only, about every 2 weeks. Never change
  anything there without a fresh "yes" in chat.
- **Test:** the 10 current Shorts (Ep 10 live; Ep 1, 3, 4, 2, 6, 7, 8 scheduled 6-14 Oct; Ep 9 v3 and Ep 5 v2 planned
  15-16 Oct) are the baseline. Record each one's views, viewed vs swiped away, average % viewed and subs gained at
  7 days old. From about 20 Oct, upload 3 new-style Shorts + the 3-minute pilot and compare at 7 days. Draw no
  conclusion until each has a few hundred views. If the new style wins, it becomes the standard from Ep 11.
- **New-standard toolkit** (pilot part 1, `reviews/pilot01.md`, scored 7.5):
  - `episodes/voices.py`: instrument voices + lip-sync. **Not used for characters any more** (the owner found
    them confusing); kept only as a sound-effect generator (e.g. the slide whistle for flying things).
  - `episodes/acting.py`: `Actor` (eyebrows, glassy eyes, extra mouths), `Perf` timelines (`to` with eases
    io/out/back/antic/snap, `face`, `ears` moods, `say`, `hop`, `wiggle`), paper wobble, `Cam` (landscape/vertical
    views of one world), `render_video` (15 drawings/s on twos, 8 cores: ~1 s of render per 1 s of 1080p video),
    `arms_front` spans (paws on cheeks drawn over the head). Camera shots: list of (start, centre, zoom) cuts.
  - `episodes/props_artcorner.py`: the art-corner world (1920x1920).
  - `episodes/pilot01_sorry_test.py`: the 27 s test scene. `tools/check_video.py --landscape --no-loop --cuts t1,t2,...` for long-form.
  - `characters.py` was not changed; Episodes 1-10 render exactly as before.
- Strategy and the reviewed master prompt: see `docs/research-oct-2026.md`. Plan for 8,000 long-form hours
  (Feb 2027 rule); long-form is the money engine, Shorts are discovery.

## Episode 11 "Pip and the Friendly Glow" (6-8 Oct 2026): paused after 3 blind rounds
Plan, gate 1, stages 1-3 (6-7 Oct). Blind rounds: r1 overall 6 (opening misread "Bear won't share"), r2 6 (same
misread), r3 6 (misread gone; blocking: no visible light source for the hearts 0-14 s, the carving hidden under the
hand 88-90 s; comedy 5). Storyboard checks sb2 (cause guessed), sb3 MATCH. Final render `output/ep11_friendly_glow.mp4`
(commit d6b2959, check_video PASS -14.2 LUFS). Files: `reviews/ep11_*`. The owner paused it on 8 Oct and asked for
the retro first: `reviews/ep11_retro.md` (MASTER_PROMPT version 3; rollback tag `agents-v2-pre-retro`).

**8 Oct 2026, evening (Lead session 2):** audit H1-H8 applied by a fresh Sonnet agent (MASTER_PROMPT v3.6, rollback tag
`agents-v3.5-pre-audit`; M24, M25, M30-M32 APPLIED). Ep 11 transformation Short built in three passes: r3 (stopped: R4-1
lantern gap measured whole masks, M35; B3/END cut faces, M34), r4 (cameras W 1.05x + D 1.79x; stopped: gag 3 had no room
at 1260, R4-1 (a) hit the drawing paw, M40), r5 (Option A: Crinkle walks to 1180 in W 25.7-26.2; R4-1 r5 exemption
6.5-21.2; handover_check PASS). New script checks: brief_check `--plan` (feasibility only while estimates are open, M39),
plan_check reads ≤ limits. Render check_video PASS -13.5 LUFS. Blind r2: overall 7 (r1 7), comedy 5.
