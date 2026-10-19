# ep11k stage table (written by tools/stage.py; change it only through stage.py)

Set: porch · View: vert · Light: 95

## Start (0.0 s)

| Who | At | Facing |
|---|---|---|
| Snip | C.L | right |
| Crinkle | C.R | left |
| Pip | WL | right |
| marker | Snip | front |
| lantern | C | front |

## Beats

| # | Time (s) | Who | Move | Arg |
|---|---|---|---|---|
| 1 | 0-0.8 | Crinkle | hop |  |
| 2 | 0-0.9 | Snip | draw | lantern.eye_l 0.3-0.6 |
| 3 | 0.8-1.4 | Crinkle | walk_to | x:1145 |
| 4 | 0.9-1.4 | Snip | draw | lantern.eye_l 0.6-0.75 lean=4 |
| 5 | 1.4-2.4 | Crinkle | take | marker from Snip |
| 6 | 2.4-5.6 | Crinkle | hand_over | marker Snip |
| 7 | 2.7-3.7 | Snip | react | sad |

## Shots

Checked by stage.py and by tools/framing_check.py (one row per still stretch).

| # | Time (s) | Shot | Whole in frame | At | Preset |
|---|---|---|---|---|---|
| 1 | 1.4-5.6 | VW@C 1x x 420-1500 y 0-1920 | Snip, Crinkle; Pip out | Snip x 680, Crinkle x 1145, Pip x 200 | VW@C |
