# Pilot episode plan: "Oops! A Splash of Blue" (~2 min, landscape, rig v2, 2x render)

Written BEFORE building (owner's rule, 2026-10-06: design first, no fixable weakness reaches the owner).
Owner's bar: everything happens like real life, characters move like they are alive, real-cartoon-film look,
and a wow ending: the mistake becomes a masterpiece.

## Why every step makes sense (cause and effect)
- Snip is painting a picture of the two friends and needs BLUE for the sky. The blue jar is on the paint
  table across the room. Snip points; Crinkle, happy to help, carries the open jar over.
- A toy block lies on the rug from the very first shot (set up, so the trip is fair and expected).
- Crinkle bounces along looking at Snip, not at the floor; his foot catches the block; he stumbles toward
  the easel and the open jar sloshes: the paint lands on the painting at short range. Paint falls the way
  paint falls (forward and down in a short arc, then drips run down). No one is hurt.
- He was trying to help, so his first instinct to tiptoe away (embarrassed) and his choice to say sorry
  are both believable.
- The fix is believable too: the splash really is whale-shaped (drawn that way), Crinkle traces it with
  his paw so the viewer sees it, and they paint the rest together with the brushes already there.

## Staging (world units; easel moved to the centre)
- Easel centre x 800 (canvas 631-969, y 930-1232). Snip paints from its LEFT (x 470, facing right).
- Paint table on the right (x 1500) with red, yellow and blue jars and a brush cup. Crinkle enters from the right.
- Toy block on the rug at x 1060 (between table and easel), visible from shot 1.

## Shot list (s = seconds)
| # | Time | Shot | What happens | Movements needed (rig check) |
|---|---|---|---|---|
| 1 | 0-4 | Wide | Art corner. Snip paints at the easel (jingle). Table with jars; block on rug. | paw holds brush; dab strokes (IK to canvas) |
| 2 | 4-9 | Close: canvas | Snip's brush adds a sun and a flower next to the two friends. | brush tip on canvas; pop-in strokes |
| 3 | 9-12.5 | Medium: Snip | Steps back, proud; tilts head: something missing. Looks at the sky area, then over to the right. | walk 1 step; head tilt; look |
| 4 | 12.5-14 | Insert: table | The blue jar on the table (Snip's point of view). | camera only |
| 5 | 14-21 | Wide | Crinkle walks in from the right, waves; Snip waves, points at the blue jar; Crinkle nods, picks it up. | walk; turn; wave (front arm); point (straight arm); grab (paw to jar, jar follows paw) |
| 6 | 21-24 | Wide | Crinkle carries the jar toward Snip, bouncy happy steps, looking at Snip. | walk with bounce; hold jar upright |
| 7 | 24-25.5 | Close: floor | His foot steps toward the block (suspense: kids see it coming). | feet visible, block |
| 8 | 25.5-29 | Wide | Trip: foot hits block (bonk), stumble 3 quick steps, arms windmill, jar tips: blue paint sloshes onto the painting; he catches his balance. | stumble steps; arm circles; jar angle; slosh arc 0.35 s |
| 9 | 29-31.5 | Close: canvas | The blue splash covers the friends; drips run down; sad trombone. | drips grow |
| 10 | 31.5-35.5 | Close: Snip | Shock (frizz, ears up), then ears droop, wet eyes, sniff. | existing |
| 11 | 35.5-38.5 | Close: Crinkle | Looks at the jar, the painting, Snip: uh-oh, paws on cheeks. | paws in front of face |
| 12 | 38.5-43 | Medium | Puts the jar down, tiptoes away looking back; Snip sniffs; he stops. | place prop; tiptoe walk |
| 13 | 43-49.5 | Medium + dim | Thought bubble from Crinkle's head: sneak away / say sorry, "?"; he looks at you; waits; nods. Green chosen. | thought-bubble prop |
| 14 | 49.5-58 | Medium two-shot | Walks back, head down, paws together; opens his arms; Snip looks up, ears rise; hug; hearts. | walk; paws together; hug (Snip in front) |
| 15 | 58-64 | Medium | Both look at the painting; Crinkle tilts his head one way, then the other... idea! (sparkle) | head tilts |
| 16 | 64-69 | Close: canvas | Crinkle's paw traces the splash: a dotted outline appears: it's a whale! | paw follows a path (IK keyframes) |
| 17 | 69-73 | Medium | Snip gets it: ears perk, big smile; both take brushes (Crinkle from the brush cup). | grab brush |
| 18 | 73-93 | Close/medium montage | Together they paint: eye and smile (Snip), tail (Crinkle), water spout (Snip), waves (Crinkle), a boat with the two friends (Snip), sun smile (Crinkle). Gag: Snip dots Crinkle's nose blue; they giggle (laughing bodies, no voices). | brush to canvas; brush to nose (face point) |
| 19 | 93-105 | Reveal (wow) | They step back. Slow push-in on the new painting; music swells; sparkles on the spout and waves. Cut to both faces: amazed, then laughing. | slow camera move |
| 20 | 105-114 | Medium two-shot | They look at each other; paw-bump with sparkle; jingle. | paw-bump |
| 21 | 114-120 | Wide | Pull back: the friends side by side in front of their whale painting; final pose; music ends. | camera |

## Sound (no voices)
Footsteps on every foot plant; jar clink on pick-up; suspense pad before the trip; bonk + scuffle + slosh +
splat; drips; sad trombone; sniffs; tick-tock and chime for the choice; twinkle for the hug; idea chime;
a rising note for each part of the whale (they build a little tune); full arrangement for the reveal; jingle.

## Quality checklist (run before the owner sees anything)
1. Sense: every action has a visible cause; characters react only to what they could see or hear.
2. Real: travel is walking (no sliding or hopping across the room); faces turn to whoever they look at;
   paws really touch what they hold; props never float.
3. Clarity: every key moment has a close-up or lasts at least 1 s; nothing important hidden behind a character;
   the story reads from a 1-frame-per-second sheet.
4. Sharp: no zoom above 2x at 2x render.
5. Sound: every visible action has a sound; music matches the mood; no silent gaps.
6. Technical: check_video PASS (--landscape --no-loop --cuts ...), -14 LUFS.
7. Safety and lesson: the trip is gentle, nobody is hurt; the lesson (say sorry, fix it together) is clear.
Review method: 1-fps sheet of the whole video, motion strips of the trip, the pick-up and the paw-bump, and
full-size frames of every close-up. Fix everything found; at most two rounds; then deliver.

## Changed from what the owner was told
- The accident: Crinkle trips on a toy block while carrying the blue paint to help (instead of bumping the
  easel). Reason: paint on the easel tray sits BELOW the picture and cannot pour up onto it; carrying an
  open jar and tripping is what really happens.
- No hanging the painting on the string at the end: the string is far above their reach, and climbing would
  not be safe to show. They finish in front of the painting instead.
