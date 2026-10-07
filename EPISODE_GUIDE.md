# Snip & Crinkle: Episode Production Guide

> This guide covers Episodes 1–10 (18-second Shorts). From Episode 11 the standard is in `MASTER_PROMPT.md`; the
> hard rules below still apply to all work.

A wordless YouTube Shorts series for kids worldwide (ages 2–6). Two paper-cut-out friends, **Snip** (lilac bunny, blue star tee, curious, sometimes makes the mistake) and **Crinkle** (caramel bear, yellow striped scarf, kind helper), learn one safety, kindness or healthy-habit lesson per episode. Every video is made entirely in code: paper art (`paperlib.py`, `characters.py`, `scene.py`, `icons.py`), original synthesized music and sound effects (`audio.py`), and ffmpeg. **Episode 1 is the reference: `episodes/ep01_v3_can_snip_wait.py`.** Read it fully before starting.

## Hard rules (never break)
1. **Wordless.** No spoken or written words except numerals (1, 2, 3), the single "?" icon and ✓/✗ icons (owner, 8 Oct 2026). Story is told by action, icons, music and sound.
2. **No emoji fonts and no third-party art.** Draw every icon as a paper cut-out (see `icons.py` for the style). No brands, logos or known characters.
3. **Original audio only**, made with `audio.py` (add new instruments or sound effects in your own file if needed). No samples or downloaded music.
4. **The lesson must be correct and safe** by mainstream child-safety advice. Dangerous things (hot drinks, roads, sharp objects, medicine) are handled by the **grown-up's paper hand** (`scene.grown_up_hand()`), never by Snip or Crinkle alone. Kids learn to *wait, ask or hold a grown-up's hand*.
5. **YouTube "made for kids" quality principles:** kind, positive behaviour; nothing scary, violent, gross or product-promoting; a clear beginning, middle and end; no keyword stuffing.
6. **Not templated.** Each episode needs a different setting or props, a different kind of mistake, and a different funny moment. Repeating the same scenes with only the lesson swapped can get the channel demonetized.
7. **Music variety.** Keep the signature jingle (start and paw-bump) and the F → G7 loop cadence exactly as they are; they are the channel's theme. Everything else in the story section must sound different from the previous episodes: pick a different accompaniment instrument than the ukulele (`music_extra.comp(..., inst="toy_piano" | "organ" | "steel_pan" | "melodica")`) and give the story its own lead line. Episodes 1–4, 6–8 and 10 all use ukulele + glockenspiel; from Episode 11 on, no two consecutive episodes may share the same accompaniment instrument, and vary the tempo or key now and then (add new instruments to `episodes/music_extra.py`).
8. **Vary who makes the mistake.** Snip errs in Episodes 1–10. From Episode 11 on, let Crinkle (or both) make the mistake in at least one episode out of three, so Snip doesn't become "the naughty one".

## The 18-second story template
| Time | Beat | Notes |
|---|---|---|
| 0–1s | **Hook** | Close-up (camera zoom ~1.6) on the temptation or problem, with a character already in motion. The signature jingle `A.jingle(music, 0.02)` plays. |
| 1–2.5s | **Desire / setup** | Make the viewer want what Snip wants (sparkle eyes, a visual flourish). |
| 2.5–4.5s | **Choice freeze** | Dim the scene. Two bubbles appear: wrong choice (red ring) vs right choice (green ring), with a "?" and tick-tock. Kids shout the answer. |
| 4.5–6s | **Gentle slapstick** | The wrong path *almost* happens and something funny stops it. No injury, no crying. |
| 6–8s | **Crinkle helps** | He arrives with a paper sign or demonstration. |
| 8–11.5s | **Do it right** | Show the correct behaviour step by step, ideally counting 1-2-3 with `scene.numeral`. This doubles as early maths. |
| 11.5–14s | **Payoff** | The reward is clearly visible (✅ via `icons.check`, then hearts). |
| 14–16.5s | **Signature paw-bump** | Both paws meet in front, with a small sparkle and the ending jingle `A.jingle(..., ending=True)`. This is the same in every episode. |
| 16.5–18s | **Seamless loop** | Return to the exact opening state. Crinkle leaves, the temptation reappears, and the camera zooms back to the 0s framing. The last frame must equal the first frame. |

## Technical conventions
- Canvas 1080×1920, 30 fps, `TABLE_Y = 1440` (or your setting's floor line). Snip scale 1.15, Crinkle scale 1.2; Crinkle's home x is about 785.
- **Arm angles** are degrees counter-clockwise from hanging down. Left arm out = negative; right arm out = positive. Crinkle's resting left arm is `346` (same as -14) so that raising it swings outward through 270, not across his body.
- **Draw lesson-critical props in front of the characters.** In v2 the sand timer, steam heart and straw were hidden behind heads. Draw the prop *after* `Character.draw`, and redraw arms in front for paw-bumps (see v3).
- **Safe zones:** keep faces and key props out of the right column (x > 950, y 980–1700, the like/comment buttons) and out of the bottom band (y > 1560, the title and caption).
- **Loop:** every periodic function needs a period that divides the duration (breathing 2.0s, ear idle 3.0s, steam phase `int(t * 16 * 13 / DUR)`). The state at t = DUR must equal t = 0.
- **Blinking, ears, breathing and squash-and-stretch** are already in `Character.draw`. Use `hop_curve()` for hops with squash, and `spring()` for ear wiggles.
- **The grown-up's arm:** use `episodes/props_grownup.py` (`GrownUpArm(...).draw_reaching(...)` or `.draw(...)`), a jointed paper arm with an elbow, tapered sleeve, cuff and open hand, solved from a shoulder that sits off-frame. Do not hang a long straight sleeve from the top of the frame (that "pole" arm was the weakest visual in Episodes 5 and 9 v1). For a grown-up holding two paws, put both shoulders together above the frame (one person), elbows out.
- **Don't edit shared modules** (`paperlib.py`, `characters.py`, `scene.py`, `audio.py`, `icons.py`). Put new backgrounds, props and icons in a new file `episodes/props_<slug>.py` or inside your episode file. This avoids merge conflicts between episodes made in parallel.

## Quality gate (all must pass before you finish)
1. `python3 episodes/epNN_<slug>.py --stills`, then **look at key frames at full size** (at least 360px wide; tiny thumbnails hide problems). For each beat, ask: is the key prop clearly visible and not hidden? Is the lesson readable with the sound off?
2. Render the video, then run `python3 tools/check_video.py output/epNN_<slug>.mp4`. It must print `RESULT: PASS`.
3. **Score honestly** with this rubric (out of 10, overall at least 8): hook, choice clarity, humor, lesson accuracy, lesson visibility, payoff, paw-bump, loop, animation life, safe zones. If any item is below 7, fix it and re-render (up to 3 rounds). Do not inflate scores. Say plainly what is still weak.

## Deliverables (per episode, on branch `episode-NN`)
- `episodes/epNN_<slug>.py` (plus `episodes/props_<slug>.py` if used)
- `reviews/epNN.md`: the scorecard table, a list of remaining weaknesses, and the upload text (title with a question and two emoji, a 3-line description, hashtags `#kids #shorts` plus 2–3 topical ones). Emoji are fine in *titles*, just not drawn in the video.
- `reviews/epNN_keys.png`: a full-size key-frame sheet (about 8 frames, 360px wide each)
- **Do not commit MP4s or `build/`** (they're git-ignored). Commit and push the branch, and report the scorecard in your final message.

## Episode briefs
### Episode 2: "Wash Before You Munch?" 🧼 (bathroom)
Snip runs in from playing (muddy paws shown by brown paper spots) and reaches for an apple or sandwich. **Choice:** apple-with-dirty-paws vs soap bubbles. **Slapstick:** Snip's muddy paw leaves a big muddy print on the snack, or a germ-cartoon (friendly green blobs, not scary) wiggles on the paw. Crinkle shows **soap, scrub (count 1-2-3 with bubbles growing), rinse, dry**. Payoff: clean sparkly paws, then they eat. New setting: a bathroom with a paper sink, mirror and tiles.

### Episode 3: "The Last Cookie?" 🍪 (kitchen, but a different time of day and props)
One cookie left on a plate, and both reach for it. **Choice:** grab it all vs break it in half. **Slapstick:** a tug-of-war that ends with both tumbling backwards (soft landing, no one hurt). Crinkle (or Snip, to vary who errs) **breaks it in half**. Show the count "1, 2" halves and that both halves are equal. Payoff: both munch happily. Vary the kitchen: evening light, a different wall colour, a cookie jar.

### Episode 4: "Whose Toy Is This?" 🧸 (park)
Snip finds a lost teddy on a park bench and hugs it. **Choice:** keep it vs give it back. A small new friend (a little paper duckling or chick) is sad and searching. **Slapstick:** Snip hides the teddy behind their back, but its ears pop out. Crinkle helps them **look around and return it**. Payoff: the duckling's happy dance, and hearts. New setting: a park with grass, a tree, a bench and sky.

### Episode 5: "Hold Paws to Cross?" 🚦 (sidewalk and crossing)
Snip sees a ball, a friend or the playground across the road and wants to run. **Choice:** run now vs stop and hold a grown-up's hand. **Slapstick:** Snip's feet skid to a cartoon stop at the curb (wind-up legs). The **grown-up's paper hand** comes down. They **stop, look left and right (eyes and head turn), and wait for the green walking light**; count 1-2-3 for the light. Payoff: they cross *holding the grown-up's hand* on the zebra crossing. No cars hitting anything. Cars can be seen stopped. New setting: a sidewalk, road, zebra crossing and a pedestrian light drawn with a walking-figure icon.

### Episode 6: "Achoo! Elbow Sneeze?" 🤧 (playroom)
Snip and Crinkle are building a tall block tower on a rug. Snip's nose starts to tickle ("ah… ah…"). **Choice:** sneeze into the air vs sneeze into your elbow. **Slapstick:** a giant ACHOO blows the tower over and a puff of friendly little germs lands on the blocks and on Crinkle (nothing gross: a pale puff cloud and smiley germs, no drips). Crinkle shows the elbow sneeze. **Do it right:** they rebuild, Snip's nose tickles again, "ah (1)… ah (2)… ah (3)… CHOO" into the elbow: a tiny puff, the tower stays standing. Payoff: the tower gets a star on top, hearts. New setting: a playroom with a rug, toy shelf, window and blocks.

### Episode 7: "Helmet On?" 🚲 (garden path)
Snip wants to ride a shiny tricycle round the garden path. The helmet sits on a hook. **Choice:** ride with a bare head vs helmet on. **Slapstick:** Snip pedals off bare-headed, a bump in the path bounces Snip up in the air (boing) and back onto the seat; a falling leaf lands softly on Snip's bare head — Snip realises the head has no protection. When Crinkle brings the helmet, Snip's tall ears pop it off twice (boing, boing) until Crinkle shows the ear holes. **Do it right:** helmet on (1), strap click (2), wiggle test (3). Payoff: a happy ride round the path. New setting: a garden with a curved path, flowers, a fence and a tree.

### Episode 8: "Your Turn on the Swing?" 🛝 (playground)
Snip is on the only swing; Pip the duckling (from Ep 4) waits with a sad face. **Choice:** keep swinging vs give Pip a turn. **Slapstick:** Snip keeps swinging and twisting; the chains twist up and the swing spins Snip round and round until Snip is dizzy (spiral eyes, soft stop, no fall). Crinkle shows a "your turn / my turn" sign. **Do it right:** Snip helps Pip onto the swing and gives gentle pushes, counting 1, 2, 3, then Pip gives Snip a turn. Payoff: both laughing, hearts. New setting: a playground with a swing frame, sandpit, slide in the background.

### Episode 9: "Buckle Up?" 🚗 (car)
The friends hop into the back seat of a parked car (seen in cut-away from the side) for a trip to the beach. The grown-up's hand is on the steering wheel. **Choice:** bounce on the seat vs buckle up. **Slapstick:** Snip bounces on the seat like a trampoline, ears squash against the roof and spring back; the car does NOT move — the grown-up's hand points at the seat belt and waits. **Do it right:** click (1) Snip's belt, click (2) Crinkle's belt, (3) the grown-up checks with a thumbs-up; only then the car drives off smoothly. Payoff: happy ride, scenery scrolling past the window. New setting: car interior + street outside.

### Episode 10: "Hot Sunny Day?" ☀️ (beach)
A bright, hot beach. Snip hop-hops across the hot sand to build a sandcastle in the full sun. **Choice:** keep playing in the sun vs hat + water + shade. **Slapstick:** Snip keeps digging; the ears slowly wilt and droop like noodles, a melting ice lolly drips onto Snip's nose (no injury, just silly). Crinkle arrives with a sun hat, a water bottle and a beach umbrella. **Do it right:** hat on, sit in the shade, drink water: sip 1, sip 2, sip 3 — the ears spring back up with each sip. Payoff: the sandcastle finished in the shade, hearts. New setting: a beach with sea, sand, umbrella, shells.
