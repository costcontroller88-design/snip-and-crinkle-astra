# Comedy and character acting from top wordless cartoons (research, 9 Oct 2026)

## Decision first

Adopt the 10 rule changes below. The strongest evidence is for Aardman's Shaun: the whole face is eyes, lids and ears,
plus head and shoulder pose. So the A2 rig job should put its budget into **eye states, lid angle, ears and a breathing
hold**, not into more mouth shapes. Adding these means each emotion must pass an "eyes-only" test. Nothing here
overrides `COMEDY_PLAYBOOK.md` (takes, anticipation, squash and stretch, sound sync, hold ≥1 s are already covered there).
This doc adds only what that file and `research-wordless-craft-oct-2026.md` lack.

## Findings and rule changes

| # | Finding | Owner | Exact rule change (≤25 words) | Source |
|---|---|---|---|---|
| 1 | Shaun's expressions come from eyes, eyelids and ears; with eyes as his only facial feature, animators also work head and shoulder position. | animator | Every emotion must read from eyes, lids, ears, head tilt and shoulders alone. Check by hiding the mouth. | [Annecy 2015 summary](https://www.annecyfestival.com/about/archives/2015/2015-meetings/2015-conference-summaries/summary:100000393398) |
| 2 | Shaun has no eyebrows, so lid position separates angry from sad; showing emotion without dialogue is the hardest task. | animator | Mood lives in the upper-lid angle: down-in for cross, down-out for sad. Test each mood sheet with lids only. | [Daily Mirror via PressReader](https://www.pressreader.com/uk/daily-mirror-northern-ireland/20191017/282213717591332) |
| 3 | Teaching sources: blink about 3-5 frames closing, brief hold, 2-4 opening; top lid leads; blink only on a thought, look or head change. | animator | Blink only when the thought, gaze or head changes. Close 3-5 frames, hold briefly, open 2-4. Never blink at random. | [Animation Mentor blinks](https://www.animationmentor.com/blog/tutorial-animate-blinks-eye-movement/) (search summary; page blocked to fetch) |
| 4 | Eye darts are 1-2 frames, lids follow the eyeball, and a big dart gets a blink. | animator | Eye darts take 1-2 frames, lids follow the pupils, and a big dart gets a blink. Use darts to show "noticing" before the take. | [Animation Mentor blinks](https://www.animationmentor.com/blog/tutorial-animate-blinks-eye-movement/) (same caveat) |
| 5 | A hold stays alive with breathing (chest or shoulders), eye darts, and a slow drift that continues the previous move; head drifts with the body. | animator | Any hold over 0.5 s gets a breath shift plus a drift that continues the last move. No frozen poses; no head drifting against the body. | [AnimSchool moving holds](https://blog.animschool.edu/?p=858) |
| 6 | Hooks: acting is doing or reacting; keep playing one action until something forces a different one; emotion leads to action, thinking to conclusions. | story-designer | Each shot states one action verb for the character ("hides", "tests"). Change the verb only when the plan names the trigger. | [Ed Hooks course notes and summaries](https://thinkinganimation.com/acting-for-animators) (secondary, not the book) |
| 7 | Larva's team says funny faces and gestures start from the body, not from an idea in the head; limbless leads lean on the face. | story-designer | Write each gag as a body or face predicament first (stuck, tangled, swallowed), then add the cause. If it can't be drawn, drop it. | [HanCinema, Dong-A Ilbo interview](https://c.hancinema.net/larva-animation-producers-talk-about-success-secret-55314.html) (search snippet; page did not load) |
| 8 | Tom & Jerry scoring: beats planned before pencil, a sound cue sets up the gag, the action plays, then a drum roll marks the payoff. | story-designer | Mark three sound points per gag: a cue before, silence during the action, a punctuation sound on the payoff. | [Wikipedia: The Yankee Doodle Mouse](https://en.wikipedia.org/wiki/The_Yankee_Doodle_Mouse) |
| 9 | Pingu's voice was improvised gibberish (grammelot); Simon's Cat uses a "vocabulary of noises" with body language; Timmy Time uses animal noises. | story-designer | Give each character a fixed noise vocabulary: one short sound per emotion, no speech-like rhythm. Keep to our no-speech-voice lesson. | [Wikipedia: Pingu](https://en.wikipedia.org/wiki/Pingu); [Skwigly: Simon's Cat](https://skwigly.co.uk/simons-cat); [Jim Hill Media: Timmy Time](https://jimhillmedia.com/toon-thursday-looking-for-some-sheep-thrills-check-out-playhouse-disneys-timmy-time/) |
| 10 | Face-squash teaching: keep eyes and nose on an eyeline; avoid symmetrical expressions; squash late, not early; flip the clip to check. | animator | Keep eyes on one eyeline while squashing. Make every key expression asymmetric (one ear or lid different). Mirror-check each take. | [Brian Lemay exercise notes](https://www.brianlemay.com/Pages/animationschool/animation/3rdsemesteranimation/01meow/meowpoints.html) |

## Ranked rig features for the A2 rig job

1. Eye states (open, half, closed, wide) plus pupil x/y offset, so darts are 1-2 frame swaps.
2. Upper-lid angle, independent of the eyeball (carries mood; findings 1-2).
3. Ear controls with overlap (ears are a third mood channel; finding 1).
4. Head tilt plus shoulder/chest breath loop and drift for moving holds (finding 5).
5. Blink as a state change, with timing presets (3-5 down, 2-4 up) and a motivated-trigger note.
6. Volume-preserving squash and stretch, features pinned to an eyeline, asymmetric offsets allowed.
7. Tiny mouth set (about 4-5 non-speech shapes: closed, small O, gasp, grin, grimace). Shaun's 15 mouth shapes serve sound; we have no speech.
8. Sound-marker slots on the timeline (cue, payoff) for finding 8.

## Evidence limits (read before trusting)

- Searches used: 20 (of 20). Findings 3, 4, 7 rest on a search summary only; the pages were blocked or did not load. Treat as unconfirmed until read.
- The claim that Shaun is "Buster Keaton-like" deadpan appeared in a search summary only; the fetched page did not repeat it. Not used as a rule.
- No sourced material found on Booba's or Mr Bean's animation craft (only business and production facts), on Pingu's face animation, or on Simon's Cat timing. No YouTube talks could be watched or transcribed here; this is text-only research.
- Aardman's director Starzak says wordless was partly a cost choice, and silent comedy travels across cultures ([Cartoon Brew](https://www.cartoonbrew.com/interviews/shaun-sheep-starzak-burton-117561.html)). Timmy Time's 2019 reboot added a narrator ([UK Screen Alliance](https://www.ukscreenalliance.co.uk/?p=5083)): a warning that preschool wordless needs very clear action, not a reason to add narration.
- Starzak's neurolinguistic-programming remark is the director's method, not established science; not used.
- Source-quality note: Hooks and blink/hold advice come from teaching notes aimed at 3D or general animation. They transfer to a cut-out rig in principle, but frame counts should be tested at our 30 fps, drawings on twos.
