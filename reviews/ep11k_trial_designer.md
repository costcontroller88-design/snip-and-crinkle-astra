# ep11k trial: designer report (stage kit, porch, vertical, light 95, 30 s)

**Result:** `python3 tools/stage.py show ep11k` prints `stage: PASS` (17 beats, 10 shots covering 30 of 30 s, 2 bespoke).
The PASS is hollow: the table is legal but does not tell the story. Pip is never on screen, no marker changes hands
after the bespoke take, and no stroke is drawn except by hand-written bespoke text. Criterion (d) (the blind retelling
matches the Short) cannot pass from this table.

## Key beats for the sheet (6 times, what each shows)

| Time (s) | Shot | What the still shows |
|---|---|---|
| 0.5 | VC@B 2x | Snip alone at B with the marker, lantern at the right edge; Crinkle and Pip out of frame |
| 3.0 | VM@C (bespoke span) | The take and give-back (bespoke 1); the kit checks nobody here, so the animator frames it |
| 9.1 | VM@D | Gag 1: Crinkle's quarter turn to front (8.8-9.4) beside the lantern; Snip and Pip out |
| 20.8 | VM@D | Crinkle's hop (20.4-21.2) standing in for the squeak gag (no marker in the kit) |
| 24.0 | VM@C (bespoke span) | The grown-up's hand and the tea light at the lantern (bespoke 2); lantern whole, characters unchecked |
| 28.6 | VM@D | Gag 3: Crinkle's turn right mid-dance (28.5-28.9), lantern lit behind him |

## Layout chosen and why

Lantern C; Snip B (not C.L); Crinkle C.R (x 1276); Pip WL. Snip at C.L (x 686) was tried first (rows 1-5 of the first
run) and abandoned: it cuts Snip in VM@D, the only preset that holds Crinkle, so Crinkle could not be framed at all.

## Refusals hit and how I resolved them

| # | Step | Refusal (short) | Resolution |
|---|---|---|---|
| 1 | Snip walk_to B from C.L (5.9-6.4) | feet within 10 u of the lantern; legal: C.L | Rebuilt with Snip at B from frame 0 (`new --force`) |
| 2 | shot VM@D, Snip@B asserted at 6.4 | Snip is on C.L, not B | Same rebuild |
| 3 | Snip point lantern.eye_l from B | 184 u from the shoulder, reach 180 (4 u short) | Snip `look lantern` instead; her drawing is not in the kit table |
| 4 | Snip point eye_r / heart / smile from C.L | 226 / 209-238 / 289 u vs reach 180 | None legal. Only eye_l (from C.L) and eye_r (from C.R) are reachable by anyone |
| 5 | Pip point heart_l from C.L | 153 u vs reach 122 (from B 677 vs 72 reach) | None legal: Pip cannot draw the nose |
| 6 | Crinkle point smile from C.R | 228 u vs reach 148-199 | None legal: Crinkle cannot draw the smile |
| 7 | hand_over marker Pip / Crinkle (Snip at C.L) | needs a pair on a bare mark | None legal with the lantern in the table (its hold_box makes every pair "reach bands don't meet": probe, not a table row) |
| 8 | Snip put_down C | 232 u vs reach 129 | None legal |
| 9 | Snip place_on bench | Snip faces right: turn to reach | Not retried: the bench is at x 470, nobody can take from it |
| 10 | Pip walk_to C.L (1 s) | 536 u in 1 s too fast; legal WL, A | Not retried: Snip occupies C.L; Pip would have to pass her |
| 11 | Pip / Crinkle pick_up marker | marker is held by Snip: use hand_over | None legal |
| 12 | shot VM@C 23.0-25.7 | Snip and Crinkle cut at 25.4 (shot runs past bespoke 2 at 25.3) | Shot cut at 25.3, VM@D 25.3-25.7 (legal list: VM@D, VC@B) |
| 13 | legal shot at 5.9-7.0 with Snip C.L, Crinkle C.R | empty list | Moved Snip to B |

## What the kit could not express

| Story need | Why not | Cost |
|---|---|---|
| Snip, Crinkle and the lantern in one vertical frame | Spacing 488-499 u plus the 240 u lantern: no preset holds both big characters at work spots; Crinkle at C.R is "cut" in every preset but VM@D/VW@D, and Snip at C.L is cut in both. Porch blocks E, so nobody waits wholly out on the right | Two-character moments (the take, the lesson) fall into bespoke 1; every other shot is a single |
| The take (Crinkle pinches the marker from Snip) | No move takes a prop from a holder; `hand_over` is giver-driven and needs a bare mark | Bespoke 1 (0.9-5.9) covers take and give-back, the lesson's key action |
| Drawing eye_r, nose, smile | Work spots reach one point each (eye_l from C.L, eye_r from C.R); the lantern is wider than any arm | Strokes are lantern art only; no `point` rows for them |
| Marker passing Snip -> Pip -> Crinkle | Lantern in the table kills every hand-over pair; put_down/pick_up has no reachable mark | Marker stays with Snip after the bespoke |
| Three characters taking turns at one lantern | Floor order cannot change (no passing), so only the rightmost of the left group can reach the lantern; Pip behind Snip stays behind | Pip is never on screen (WL, out of every shot) |
| Waiting "copying Pip" | Pip and Crinkle never share a frame (Pip@WL out of VM@D; Pip beside Crinkle is spacing-illegal) | Gag 1 is Crinkle's turn only |
| Sway, squeak, wiggle-dance, grin, bow | No such moves; 5 emotes only (neutral, curious, cross, sad, delighted); `hold` is free text | Stood in by turn, hop, react |
| Gag 2 (marker squeak) | Needs the marker in Crinkle's paw | Replaced by a hop; not a gag as designed |
| Light and glow | The kit has no lit-state move; the lantern glows only through the animator's prop code | Bespoke 2 text; light is the table's header value 95 |

## Verdict for the owner

Criteria: (a) no measure round: met, nothing was measured. (b), (c), (e), (f): not tested (no script, sheet or Sonnet run).
(d): will fail. Cheapest fixes, in order: make the lantern's hold_box small so hand_over pairs exist; add a "take"
move; give work spots a wider reach or put the lantern's drawing points within reach of C.L/C.R; unblock E on the porch
or add a preset that holds Snip at C.L and Crinkle at C.R.

## Round 2 (kit v2; story restaged by intent rows; stopped at the budget, table not complete)

**Result:** `stage.py show ep11k` = FAIL (7 beats, shots missing; 0 bespoke used). Only 0-5.6 s are staged (draw, take, long hand_over, sad); 5.6-30 s unstaged.
Layout: Snip C.L, Crinkle C.R, Pip WL (Pip at A was moved to WL so Snip may step back), marker@Snip, lantern C.
Worked: `draw lantern.eye_l 0.3-0.6` (frame 0 = eye 30% drawn); the solver added Crinkle `walk_to x:1145` before `take marker from Snip` (take across the lantern top works); long `hand_over` 2.4-5.6 (pause as one row); Snip `react sad`.

| # | Refusal | Choice |
|---|---|---|
| 1 | `new` with `Snip@x:708` | start spots are marks only; used C.L and a 0.3-0.6 stroke fraction (eye starts 30% done, as designed) |
| 2 | Snip draw eye_l 0-0.5 from C.L: 196 u vs reach 180 | stroke fraction 0.3-0.6 instead |
| 3 | Crinkle `take` from C.R: 269 u vs 148 | accepted solver's walk to x:1145 (0.8-1.4); the 0.9 take slips to 1.4 |
| 4 | Any row after the take: Snip-Crinkle 465 u, need 488 (the take pair is legal only inside its row) | no fix found: Snip walk 1.6/1.9 and Crinkle walk D at 2.4 all refused; poses `lean=12 sq=0.88` typed on `take` are dropped, x stays 1145. Worked around by one long `hand_over` 2.4-5.6 |
| 5 | Crinkle rest after the give-back: resting paw 0 u from the lantern at 6.0 | not solved; every later Crinkle/Snip row refused |
| 6 | Snip draw eye_l 0.75-1.0 from 680: 181 vs 180 | solver wants Snip x:709, then (1) of 4/5 again |
| 7 | Snip draw eye_r: 270 u; solver wants x:806 | not reachable from the left of a 240 u lantern without crowding Crinkle |
| 8 | shot VM@group 0-5.6: Crinkle at 1272 cut at 0.0 | no frame holds Snip 680 and Crinkle 1272; shots left unwritten |
| 9 | Gag 1 (Crinkle copies Pip) | Pip and Crinkle never share a frame (Pip must sit left of Snip, 355 u; Crinkle right of the lantern); no row tried |

**Still not expressible:** the take's end state (pair 465 u apart vs 488 spacing; a take leaves nowhere legal to go); two characters plus the lantern in one vertical frame at frame 0; Snip drawing eye_r/nose/smile (reach); a marker pass Snip -> Pip -> Crinkle around a 240 u lantern; Pip beside Crinkle for gag 1; pose args on `take`; unnamed start x.
Runtime: chained solves for 15+ rows took more than 120 s.

Row 8 update: VM@group refused 1.4-5.6 (Crinkle cut at 1145); the kit offered VW@C and VW@x943 (1x, so the marker is small); VW@C 1.4-5.6 written. 0-1.4 has no legal frame (Crinkle at 1272 and Pip at WL are cut in VW, Crinkle cut in VM).
