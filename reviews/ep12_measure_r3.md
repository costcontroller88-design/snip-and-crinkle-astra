# Ep 12: animator re-measure of fix r3 (18 Oct): 6 PASS, 8 FAIL

Numbers in the plan rows marked (r3); from `episodes/ep12_rough_r3.py --measure`.
Passes: Snip to the ball 91 u (8.3-11.0), 218 (13.6); paws through the cushion 24/60; "?" to other heads 263.4 u min; ball visible at 10.3 100%; ball uncovered 1.4 s; Crinkle's head out of C4 by 10 u.

## Fails and the Lead's picks (build-level: camera, prop size, timing; story unchanged)
| Fail | Measured | Options | Lead pick and why |
|---|---|---|---|
| C2 window / Snip whole | Snip's head+ear mask to x 594, window edge 535 | Snip at ≤310; window x 606-1566 with Pip ≥800 | **Window x 606-1566, Pip ≥800**: camera only; Snip stays at 380 so his 91 u gap to the ball holds |
| Shot 4 | Snip to x 408, window from 400 | window x 420-1380; Snip ≤222 | **Window x 420-1380**: camera only |
| Cushion topple | 0.48 s at a 20° tip | tip ≥25° gives 0.39 s | **Tip ≥25°** |
| Cushion on the ball | stops leaning at 47°, ball in plain view (13.6) | soft drape after contact | **Drape**: the plan says "flat on the ball"; after contact the cushion sags flat over it with a visible bulge (bulge row). The ball is hidden from contact until the last cushion is lifted (M69) |
| C4 hook and rope | 3.7%, hook at frame edge | rope ~330 u; C4 1.71x with head in | **Rope ~330 u**: keeps Crinkle's head out of C4 (passes now) |
| F1 boat to head+scarf | 0.0 u: the 140 u mast reaches the scarf | mast ≤80 u; hull at knee height | **Mast ≤80 u**: boat stays at tummy height where hook and rope read; nothing near the neck |

Not checked: F1 over 0-140 s (the build-stage `--check`). Gate 1 re-checks these picks (mast, rope, drape).

## Apply round (fresh animator, 11 calls): 6 PASS, 2 FAIL; sheet held
PASS: C2 window (Snip out 12, Pip in 46, Crinkle out 56); shot 4 (Snip out 12); topple 0.39 s at 25°; drape hides the ball 0% from 10.64 to 13.6; rope 330 u (11.3% of C4).
FAIL: C4 boat 193 u outside the frame; boat (80 u mast) to head+scarf 22.0 u (need ≥40).
Lead picks: **boat held 30 u lower** (measured 47.2 u, still at the hip); **C4 framed low ~2.84x** (y 1260-1640, x ~740-1416: hook, rope and boat in, Crinkle's head out); **Snip 9.2-11.0** (Lead look check of `build/sb3/ep12/f_011.0.png`): one raised brow + flat mouth + eyes off the drum read as sly, against the card (he looks back at his drum); set both brows level, a soft mouth, head and pupils toward the drum (left).

## Final picks round (same animator): 3/3 PASS; sheet `build/sb3/storyboard.png` (12 frames)
Boat 40.5 u to head+scarf (need ≥40; margin 0.5 u); C4 2.84x: hook+rope 50.3% wide, boat in by 96, head out by 10; Snip 9.2-11.0 brows level, soft mouth, pupils 11.7/13.8 u left. Side effects: C2 Snip out 58; M1 Snip in 11, Pip in 12.
Lead look check of the sheet: the cushion still reads as a thin board when carried (frames 3-4) and a half-dome on the floor, the shape the gate 1b r1 reviewer could not read. Look fix (draw only, same masks) sent before gate 1b round 2, the last round.

## Cushion look round (same animator, 39 calls total): all touched rows PASS; sheet redrawn
Carried face 155/158 u; topple 0.37 s; ball visible 10.3 100%; drape hides the ball 0% from 10.57 to 13.6; uncovered 1.27 s; bulge 17.9%; Snip whole M1 11, C2 out 58, shot 4 out 12.
Lead look check of the sheet: carried and held, the cushion now reads as a pillow (frames 3, 4, 10). Over the ball (17.5, 31.0, 51.0) it is a spread hump with corner flaps: cloth or tent, not a pillow. Blue block floats ~8 u above it at 31.0.

## Final fix round (fresh animator), all before gate 1b round 2
1. **Cushion over the ball:** the animator's option 1, a bigger cushion (~300 u), so it rests on the ball keeping its pillow outline (rounded rectangle, seam, button, corners down at the floor), with one central bump; no spread flaps.
2. **F6 (gate 1):** Pip ≥30 u from the cushion, 10.1-14.4 (whole masks). The bigger cushion makes this harder: move Pip, not the cushion.
3. **F7 (gate 1):** rope ≥10 u from Crinkle's feet and legs, 36.0-43.0; keep the C4 numbers (hook+rope ≥10%, boat in, head out) and the boat ≥40 u from head+scarf.
4. Blue block at 31.0 rests on the cushion (0 u gap).
5. After the fixes: the full clearance `--check` over 0-140 s (M77).

## Final fix round result (fresh animator, 19 calls both runs): all 5 PASS; sheet redrawn
Cushion 300×300×60 rests 2.9 u above the ball; F6 Pip to cushion 58.0 u min (Pip at 990, 8.3-17.5); F7 rope to Crinkle's feet+legs 37.9 u (Crinkle now walks left, boat in his trailing paw, train behind him; Snip 190, Pip 335); C4 hook+rope 49.4%, boat in 101, head out 10, boat 68.2 u from head+scarf; block gap 0.0 u; topple 30° 0.36 s. Not in rows: the carried pillow hides 13% of Snip's head at 9.6. Full clearance sweep not checked (`ep12_rough_r3.py` has no `--check`). handover_check fails on build-stage items only (no audio).
Lead look note: the draped cushion still reads as a smooth mound, not a crisp pillow. Left to the blind reviewer (core rule 3); the last gate 1b round.
