# Pilot part 1: "Oops! Say Sorry" test scene (landscape)

## v2 (34 s), after the owner's viewing
The owner watched v1 and could not understand it: neither the sounds nor the story (the old Shorts were clear to
them). Viewing v1 at 1 frame per second confirmed it: one far wide shot, a 0.3 s accident, 4-5 s stretches with
nothing moving, tiny choice icons, a too-subtle "sorry", and instrument voices that sound like talking. My v1
"story clarity 8" was wrong.

v2 changes: 11 camera shots with close-ups (painting, wobbling pot, splat, Snip's face, Crinkle's face); the pot
rocks 3 times before it tips; the paint flies to a slide-whistle effect, SPLAT, sad trombone; Crinkle's paws fly
up ("oops") and go to his cheeks, drawn in front of his face ("uh-oh"); he tiptoes away glancing back, hears a
sniff and stops; the choice (sneak away or say sorry) with fitted bubbles; he walks back, head down, paws
together, opens his arms; hug, hearts, paw-bump. **No voices**: sound effects and music only, like the old Shorts.
`check_video.py --landscape --no-loop --cuts <shot times>`: PASS (-15.0 LUFS, no gaps, biggest non-cut change 17).

v2 self-score: story clarity 8, acting 8, pacing 8, lesson 9, humour 6, hook 6, vertical framing 4 (not redone).
These self-scores proved unreliable once; **the owner's yes/no on v2 is the real test.**

## v1 (27 s) record

File: `output/pilot01_sorry_test_land.mp4` (render with `python3 episodes/pilot01_sorry_test.py`; `--keys` for
`reviews/pilot01_keys.png`, `--still T [--vert]` for one full-size frame). `tools/check_video.py --landscape --no-loop`: **PASS**
(1920x1080, 27.0 s, -14.3 LUFS, no silent gaps, biggest frame change 14.7).

## Story card
Engine B (Crinkle makes the mistake). Setting: a playroom art corner (new). Snip hums while finishing a painting and
steps back proudly; Crinkle dances in and his big arm swoosh knocks the paint pot; a blue blob sails over Snip's
head and splats on the painting. Snip gasps, then the ears droop with a falling slide-whistle "aww". Crinkle: uh-oh,
paws on cheeks, then he turns to the viewer: sneak away, or say sorry? He looks at each choice, back at the viewer,
and waits (about 4.5 s). Then paw on heart, a slow sorry hum, Snip's ears lift, a small "ok", a hug with hearts,
and Crinkle gets an idea. Outcome so far: making up; part 2 is fixing the painting together. Instruments: marimba,
melodica and soft pads (no ukulele). Not a loop (long-form scene).

## What is new (the new standard being tested)
- **Voices** (`episodes/voices.py`): Snip on a slide whistle (C5), Crinkle on a warm hum-horn (C4), Pip on piccolo
  peeps. No words, only speech shapes. Mouths open from each line's loudness (lip-sync). Checked by spectrogram:
  clean tones with the intended contours. The first version had broadband hiss, found and fixed.
- **Acting** (`episodes/acting.py`): eyebrows, glassy eyes, frown/talk/hum mouths, keyframed poses with wind-up and
  overshoot, Snip's ear moods (droop, alarm, curious, perk), automatic blinks and breathing, a tiny per-drawing
  paper wobble. Built on top of `characters.py` without changing it, so Episodes 1–10 are unaffected.
- **Drawing on twos + parallel render**: 15 drawings a second, 8 cores. **26 s to render 27 s** of 1920x1080
  (Ep 10: about 5 min for 18 s), roughly 17x faster per second of video.
- **One world, two cameras** (`props_artcorner.py`, `acting.Cam`): 1920x1920 set; landscape and vertical views.

## Scorecard (harsh; judged from full-size frames, a frame-by-frame motion strip and measurements)
| Item | Score | Notes |
|---|---|---|
| Story clarity, sound off | 8 | Cause and effect all visible: swoosh, impact star, pot tips, blob over Snip's head, splat. |
| Acting / animation life | 8 | Big step up from about 5: brows, wet eyes, drooping ears and frizz read instantly. Arms are still one stiff piece with no elbow, so paws can't touch the face. |
| Pacing for ages 2–6 | 8 | Beats hold 1–2 s; the viewer gets a 4.5 s pause to answer. |
| Lesson accuracy | 9 | Say sorry after an accident and offer to help: mainstream advice; nothing dangerous or imitable. |
| Lesson visibility | 7 | Choice bubbles, paw on heart, hug. The red "sneak away" icon is still the weakest picture. |
| Voices | 7* | *By measurement only (clean tones, right shapes, in sync). Nobody has listened yet; YouTube data will judge. |
| Humour | 6 | One good gag (paint flies over Snip's head unnoticed). Needs more silliness in part 2. |
| Hook (first 2 s) | 6 | Gentle painting and humming: fine for TV, too slow for a Short. The Short should start at the dance-in. |
| Payoff | 7 | Hug and hearts; the real payoff (fixing the painting) is in part 2. |
| Music variety | 7 | New palette (marimba, melodica, pads). |
| Framing, landscape | 8 | Clear two-shot, faces never covered (Snip stands in front during the hug). |
| Framing, vertical | 4 | **Weakest.** The same world works, but Crinkle is cut off at the right edge; Shorts need their own camera framing per shot. |
| **Overall** | **7.5** | Not yet at the episode bar (8, nothing below 7). |

## Fix next session (part 2)
1. Vertical camera that pans per shot (or tighter staging for the Short cut) so both characters stay in frame.
2. Part 2 story: they turn the splash into something new together (the blob becomes a whale or a pond with ducks),
   with 2–3 real gags. Then join both parts into the ~3-minute pilot.
3. Short cut (25–40 s) starting at the dance-in, plus a looping end.
4. Elbows for both characters' arms (paws to face, hand on heart that actually touches).
5. A clearer red "sneak away" icon.
