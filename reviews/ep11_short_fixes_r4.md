# Ep 11 transformation Short: fixes r4 (staging, 8 Oct; from the r3 build, sheet `build/ep11s/r3/sheet_c.png`)

| # | Where | Problem (measured / seen) | Fix wanted |
|---|---|---|---|
| 1 | Camera B3 r3 1.5x (1005, 1180), x 645-1365, 22.2-27.x | Cuts half of Snip's face (left edge) and Crinkle's right ear (head mask at 1260: x 1016-1459) 22.4-25.8 | Refit so every head mask, ears included, is fully in frame; keep the tea-light drop a key size ≥10% (a close-up for the drop is allowed if a wider shot can't hold it) |
| 2 | END r3 1.2x (1020, 1215), 28.6 | Crinkle's raised paw is cut at the right edge | Refit so raised paws stay in frame through the wiggle and spin |
| 3 | Whole plan | plan_check FAIL: 4,029 words (cap 4,000) after the R4-1 r4 paste (M23) | Trim prose to ≤3,700 words; numbers, R-texts and tables unchanged |

Fixed by safety (don't move without saying so; any move goes back to the safety-checker): Snip 660, Crinkle 1260 (lean -6 = away, 24.3-25.3), Pip 740; hand + tea light ≥30, sleeve ≥10 from every head mask 23.0-25.3; R4-1 r4.
Give every new camera its head-mask x spans in the camera row (M34).

## Changes (story-designer r4; plan updated in place, rows marked r4; code not touched)
Masks measured with the code's `head_mask` / `_body_mask` (scratch script); stills `build/ep11s/r4_plan/` (r4_sheet.png).

| # | Shot, time | What changed | Re-check stills |
|---|---|---|---|
| 1 | 11, 22.2-23.0 | B3 → **W** 1.05x (975, 1006), x 461-1489: heads Snip 486-868, Pip 645-858, Crinkle 926-1459; every head ≥25.3 inside | r4_22.60 |
| 1 | 12, 23.0-25.7 | New close-up **D** 1.9x (762, 1186), x 478-1046, y 681-1691: Snip 498-862 and Pip in (≥19.7); Crinkle 1061-1514 fully out (≥14.8, body too); tea light 14.1% (key size kept ≥10); the hand enters from above the frame (hand top 535 < 681 at 23.0) | r4_23.30, r4_24.00, r4_24.80, r4_25.50 |
| 1 | 12, 25.7-26.2 | Cut back to W once his head is back inside (1461 at 25.73); B3 → END pull (25.4-27.8) dropped | r4_25.80 |
| 1 | residual | D crops the lantern's right 34 of 240 (the smile's right end) while it lights up; the whole lit face shows in W from 25.7 | r4_25.50 |
| 2 | 13, 26.2-29.0 | **OPEN, not solvable by cameras or cuts at fixed positions.** Measured (strip shifted right): his head reaches 1586, paws 1592 (28.73); paws past 1489 most of 26.27-29.0, 1575 already at 26.33. The world strip ends at 1500 and a vertical frame is ≤1080 wide (zoom ≥1.0: world 1920 tall), while Snip's head starts at 492: all three need ≥1100. Pip's head overlaps Snip's in x and y, so no frame shows Pip without Snip. W holds the shot meanwhile | r4_27.13, r4_28.73 |
| 2 | options | (a) Acting, no move: paws up over his head, not out; spin on the spot (turn ≤ about +0.3): head and paws ≤ x 1470 26.2-29.0 (estimate), W holds all. (b) Position, safety re-check: after the hand has gone (25.3) Crinkle steps left to 1180 (25.4-26.0) and the strip moves to x 450-1530 (`VERT_X0` 450; every camera still fits): extents −80 → head ≤1506, paws ≤1512 in a 1.0x frame 450-1530 (estimate from the measured extents; F3/R4-1 near the lantern to re-check) | — |
| 3 | whole plan | 4,029 → 3,700 words: prose condensed and redundant table wording cut (numbers and R-texts kept); key-action "uncovered" cells updated to the measured 100% visible (`--check`) | plan_check PASS |
| — | b8, b10, key actions, measured checks | T7 r4 (cameras W, D; cuts 23.0, 25.7; drop B3, END, `T_PULL`; head in/out check per shot, M34); storyboard 24.0 D, 25.8 W, 28.6 W; three r4 measured rows | — |
