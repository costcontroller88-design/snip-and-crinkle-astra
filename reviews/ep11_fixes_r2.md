# Episode 11: Lead fix list after blind review round 2 (7 Oct). Round 3 is final (owner approved)

Two blind reviewers misread 0-17 s the same way: "Bear won't share the pumpkin". Crinkle's paw on his pumpkin in the
foreground beside a sad Pip, and Snip pointing at Crinkle, outweigh the faint hearts. Everything from ~32 s on works
(sense, wow, look 8). Fix the cause by restaging, then lift the comedy. Don't touch shared modules; don't commit.

## S1 opening restaged (0-12.5 s): Pip and the light, no pumpkin
- Crinkle and the pumpkin are NOT in Pip's opening shots. Snip and Crinkle sit at the bench (left), Snip sketching,
  Crinkle humming with his eyes closed; the pumpkin stands beside the bench, nobody touching it, out of shot until
  ~32 s. The camera stays on Pip, the railing, the wall and the sun.
- Light hearts saturated gold (not pale yellow) with a slightly darker, cooler wall around them. As the sun dips they
  go out one by one, each with a small sparkle-out and a soft descending glock note, the last under Pip's wing.
- Empty wing close ≥ 1.5 s, then she looks at the now-dark, empty wall (hold the empty wall ≥ 1.2 s).

## S2 hiding and comforting (12.5-31 s, about 5 s shorter)
- The breeze startles her; she runs to the bench and hides behind Crinkle. Snip points at PIP (paw clearly on her,
  not on Crinkle); Crinkle turns, finds her: surprise → gentle smile (never guilty or caught).
- Pip points at the dark wall where her hearts were (cut to the empty wall), hugs herself; Crinkle comforts her;
  Snip's thinking pose → idea. Cut dead time so 16-31 s has one clear action at a time.
- The plan in the sketchbook: a close at ≥ 2.2x held ≥ 1.5 s, glow lines bright.

## C1 comedy, a gag at least every 20 s from 32 to 80 s
- ~44 s: Pip sneaks one extra dot onto the pumpkin; Snip notices, tilts his head; Pip grins (copycat cheek).
- ~62 s: Crinkle's sit-down reads as a gag: a clear wobble, he plops onto his bottom (boing), laughs at himself,
  the others giggle with him. Remove the marker that lands under the pumpkin (it reads as a mistake), or he finds
  it under himself as the punchline.
- Keep the chime bonk (~50 s) in a medium with its sound and a held reaction.

## Small
- ~84 s: hold the grown-up's thumbs-up a beat longer before the hand comes to the pumpkin.
- 116-131 s: make sure one shot shows the pumpkin's quarter turn to the wall clearly (the round-2 viewer missed it).
- 141-146 s: hold the wing close +0.5 s.

## Order and budget (MASTER_PROMPT 10.10)
1. Storyboard sheet (gate 1b) `build/sb2/storyboard.png`, labels = times only: 1, 5, 9, 11, 14, 18, 24, 30, 44,
   62, 131, 144 s. Return and stop. A NEW fresh-eyes-reviewer retells it blind; the Lead compares the problem, its
   cause and the lesson with the story card. Build only on a match.
2. After the go (resumed): one full render, waited on in a single foreground call or one chained watcher;
   check_video; key sheet; return. No second render without asking.
