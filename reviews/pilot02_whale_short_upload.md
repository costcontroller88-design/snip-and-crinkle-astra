# Upload sheet: "Oops! Spilled Paint Becomes a Whale!" (transformation Short, cut from the pilot)

Packaging by the packaging agent, 6 Oct 2026. Nothing here has been done on YouTube. Do not upload until the owner
says go. File: `Videos/pilot02_whale_short.mp4` (vertical 1080x1920, 30 fps, 22.1 s; copy of
`output/pilot02_whale_short.mp4`). Copy-paste text: `Videos/pilot02_whale_short_upload_text.txt`.

## Title (pick A)
Counts are for the lead part (the moment and the lesson words, with emoji) and for the whole title. The whole title
must stay under YouTube's 100 characters, and in the Shorts feed only the first 40-50 characters show, so the moment
comes first.

| | Title | Lead / whole |
|---|---|---|
| **A (pick)** | **Oops! Spilled Paint Becomes a Whale! 🐳🎨 \| Snip & Crinkle \| Kids Cartoon** | 39 / 71 |
| B | From Splat to Whale! Friends Fix a Mistake Together 🐳🌈 \| Snip & Crinkle \| Kids Cartoon | 54 / 86 |

Why A:
- It leads with the exciting moment ("Oops!") and the payoff in plain words, and the first 39 characters show in the
  feed without being cut. It is the transformation-Short pattern the benchmark found strongest (MEOWJI's "Muddy to
  Clean!" and "Uh-Oh! ..." Shorts, KIDZOKI's "Refill the Truck with Colors!").
- "Spilled Paint" is what a parent and a 3-year-old see happen (the cup tips, the paint lands on the picture). "Splash"
  is the pilot's own word but says less. Everything in the title is shown: the spill, the splat, the whale.
- It does not repeat the old Shorts' question style ("Buckle Up? ...") or the pilot's lesson-first style, so the
  growth-analyst gets a third style to compare. The lesson goes in the description.
- Two emoji (whale and palette: the whale is the payoff, the palette says painting). No other brand or character.

B is the alternative: the same pattern ("X to Y") with the lesson words in the title. Take B only if the owner wants
the lesson visible in the title. It is longer, and the feed cuts it after "Friends Fix a Mistake ...".

Note for the comparison: this Short differs from the pilot's 43 s Short in both format (transformation, not story) and
title style (result, not "who and what happens"). The test shows which package wins, not which of the two causes it.

## Description
(Paste this as is. Line 3 uses the proposed new title of the pilot episode; see "Pilot titles" below.)

```
Snip the bunny and Crinkle the bear get an oops: blue paint spills on their picture, and together they paint the splat into a smiling whale with waves, a little boat and a rainbow!
Accidents happen, and friends can turn a mistake into something wonderful together.
Watch the full story: "Oops! Blue Paint Spills! Say Sorry and Fix It Together"
A gentle, wordless story for little ones everywhere, with original art and music.

#shorts #kidscartoon #painting #whale
```

Every claim is in the video: the trip and spill, the splat on the friends' picture, the whale painted in layers
(eye and smile, tail, spout, waves, boat with the two friends, bubbles, rainbow), and the before/after wipe. It does
not say "sorry", because the Short does not show it (the sorry is only in the full story).
Hashtags: #shorts (required for Shorts), #kidscartoon (our standard), #painting and #whale (the topic, and what a
parent might search). Four, no stuffing.

## Cover frame (Shorts use a chosen frame, not a custom thumbnail): 18.4 s
Pick the frame at **18.4 s**: the painting half-way through the before/after wipe. On the left the finished whale
(eye, smile, sun, boat with the two friends), on the right the grey splat it started as, and a white sparkle line
between. Rendered with `python3 episodes/pilot02_whale_short.py --still 18.4` (file
`build/pilot02_whale_short_18.40.png`).

Why this frame:
- **It shows the whole promise of the title in one picture:** "spilled paint" (the splat) and "a whale" (the painting),
  side by side. Nothing else in the Short does that.
- **It reads small.** I checked it at 160 px wide next to the other candidates: the dark-blue splat against the bright
  whale is the clearest contrast of the lot, the whale's eye and the boat still show, and the wipe is about half and
  half (at 18.3 s the whale is only a fifth of the picture; at 18.5 s the splat is nearly gone).
- **Layout.** The painting sits in the middle at about 44% of the height, clear of the bottom 19% (title and caption)
  and the right 12% (buttons). The easel and cream background keep it calm and uncluttered next to the busy feed.
- **No faces to cut off.** In the easel two-shots (such as 17.2 s) the friends sit half off the left and right edges.
  This frame is the painting alone. The cost: it has no face, so it sells the transformation, not the emotion.

Frames I rejected:
- 1.0 s (the bear shocked at the splat): the best face, but the splat is half behind his head and the picture is
  small, so a viewer sees "a bear" and not "spilled paint becomes a whale".
- 17.2 s (both friends laughing at the finished painting): charming, but busy, and the friends' faces are cut by the
  left and right edges.
- 18.8 s (the finished painting alone, no grey half): clean, but it hides the "before", and without it the picture is
  just a whale painting.

Fallback: if the app only offers a few frames to choose from, take the one closest to a half-wiped painting; if none
is close, use 18.8 s (the clean finished whale painting). The first frame of the video (the trip) is what plays in the
feed, so this choice only affects the cover on the channel's Shorts tab, search and shelves. I have not checked the
current Studio screen: the Lead or the owner should look for where the frame can be chosen (in the YouTube Studio
mobile app for Shorts, as far as I know).

## Settings sheet
- Made for Kids = **Yes**. Category: Education. Language: Not applicable. No AI / altered-content label (stylised
  animation).
- Playlists: "Snip & Crinkle Stories" (exists). Add "Kindness & Sharing" once it is created: the lesson (a mistake
  turned into something good together) fits it, and it puts the pilot episode and both pilot Shorts in the same
  playlist so a viewer who finishes one is offered the others.
- Related video (if Studio offers it for Shorts): the pilot episode "Oops! A Splash of Blue", so the Short sends
  viewers to the long video. This only works because the episode is live first (see the slot).
- Visibility: schedule it for the slot below. Nothing is set until the owner says "yes".

## Slot: confirmed, Thu 22 Oct 2026, 6:00 PM IST
Calendar check: Thu 15 Ep 9 v3, Fri 16 Ep 5 v2, Sun 18 and Mon 19 Halloween Shorts, Tue 20 pilot story Short, Wed 21
pilot episode, **Thu 22 this Short**, Sat 24 Halloween episode. One upload a day, no clash.

Why Thursday 22 and not another day:
- **After the pilot episode on purpose.** The Short-before-long rule is met by the 43 s story Short on Tue 20. This one
  is a second feeder: when it goes up, the episode is live, so line 3 of the description and the related-video link
  point at a real video, and it gives the episode a second push in its first week.
- **Not on the Halloween days.** Sun 18, Mon 19 and Sat 24 belong to Episode 11, the seasonal push (last year's hits
  went up 11-16 days before Halloween). Thu 22 does not compete with them.
- **A fair test date.** At 7 days old it is Thu 29 Oct, inside the 28 Oct - 4 Nov gate. The pilot Short is read on Tue
  27 Oct, so both Shorts are judged against the baseline Shorts from the same fortnight.
- **The one weak point:** three uploads of the same story in three days (Tue, Wed, Thu). The whale Short looks and moves
  differently (the camera stays on the painting; no story), and the gap on Fri 23 stops it touching Ep 11. If the pilot
  episode slips, move this Short with it: keep it after the episode, never before.
- Do not move it to Sat 17 or Fri 23. Sat 17 would go up before the episode exists; Fri 23 would put a non-Halloween
  upload right next to the Halloween episode on Sat 24.

What to compare at 7 days (for the growth-analyst, under about 300 views say "too early"): viewed vs swiped away and
average % viewed against the 10 old Shorts and against the pilot's 43 s Short; subscribers gained; and how many
viewers go on to the pilot episode (if the related-video link is used).

## Pilot titles (`reviews/pilot02_upload.md`): my verdict for the Lead
Not edited. Both fail my title rules, so I would change both.

What is wrong with both:
- **The channel tag is in the wrong order.** The standard ends "| Snip & Crinkle | Kids Cartoon"; both pilot titles
  end "Kids Cartoon | Snip & Crinkle".
- **They lead with the lesson, not the exciting moment.** The benchmark gave the pilot a 5 for packaging because of
  exactly this ("lesson-first title"), and it found that "sorry" is owned by songs while story videos on it are small.
  A parent sees the lesson but not what happens.
- **The Short's title says almost nothing:** its lead part is under 20 characters.

| | Now | I would change it to | Lead / whole |
|---|---|---|---|
| Long video (2:04) | Say Sorry and Fix It Together! 🐳🎨 Kids Cartoon \| Snip & Crinkle | **Oops! Blue Paint Spills! Say Sorry and Fix It Together 🎨🐳 \| Snip & Crinkle \| Kids Cartoon** | 57 / 89 |
| Short (0:43) | Oops! Say Sorry! 🎨💙 Kids Cartoon \| Snip & Crinkle | **Crinkle Trips and Spills the Paint! Then a Sorry Hug 🎨💙 \| Snip & Crinkle \| Kids Cartoon** | 55 / 87 |

Why these two: the long video keeps all the lesson words the Lead already chose, but opens with the moment ("Oops!
Blue Paint Spills!"). The Short names who and what happens, which is the story it tells, and keeps the sorry as
the hug (the wordless way the story shows it). Only the long title and the whale Short start with "Oops!", which is
the pilot week's hook word; the Short does not, so three titles in a row do not look the same.
Both keep two emoji, no other brand, and promise nothing the videos do not show.

If the Lead changes the long video's title, the pilot Short's line 3 should read:
`Watch the full story: "Oops! Blue Paint Spills! Say Sorry and Fix It Together"` (now:
`Watch the full story on our channel: "Say Sorry and Fix It Together!"`). If the Lead keeps the old long title,
line 3 of the whale Short's description must be changed to match it:
`Watch the full story: "Say Sorry and Fix It Together!"`.

## Status (Lead, 6 Oct 2026)
DROPPED by the owner (6 Oct, no rebuild). NOT FOR UPLOAD. The Short failed gate 2 twice (blind reviews: 7/10, then 6/10; pass is 8). Per MASTER_PROMPT.md
section 9 the Lead stopped after two rounds and reported to the owner with a recommendation. The draft video and
text in `Videos/` are renamed "DRAFT-failed-review_…" so they can't be uploaded by mistake.
