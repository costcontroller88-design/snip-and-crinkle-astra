# Stage kit move test (19 Oct 2026; `python3 tools/stage.py test`)

Kit code hash f35dd9321822. ok = the kit accepts the move and the rendered frames are clear (clearance sweep, 10 u, the holder's paws allowed) and nobody is cut in W; R = the kit refuses it (reason below); X = accepted but the render touches or cuts (a kit bug).

| Who | Move | WL | A | B | C | D | E | WR |
|---|---|---|---|---|---|---|---|---|
| Snip | enter | R | ok | ok | ok | ok | ok | R |
| Snip | exit | R | ok | ok | ok | ok | ok | R |
| Snip | walk_to | R | ok | ok | ok | ok | ok | R |
| Snip | turn | R | ok | ok | ok | ok | ok | R |
| Snip | look | R | ok | ok | ok | ok | ok | R |
| Snip | nod | R | ok | ok | ok | ok | ok | R |
| Snip | shake | R | ok | ok | ok | ok | ok | R |
| Snip | react | R | ok | ok | ok | ok | ok | R |
| Snip | hop | R | ok | ok | ok | ok | ok | R |
| Snip | hold | R | ok | ok | ok | ok | ok | R |
| Snip | point | R | R | R | R | R | R | R |
| Snip | pick_up | R | ok | R | R | R | R | R |
| Snip | put_down | R | R | R | R | R | R | R |
| Snip | place_on | R | ok | R | R | R | R | R |
| Snip | drop | R | R | R | R | R | R | R |
| Snip | hand_over | R | R | ok | ok | ok | R | R |
| Crinkle | enter | R | ok | ok | ok | ok | ok | R |
| Crinkle | exit | R | ok | ok | ok | ok | ok | R |
| Crinkle | walk_to | R | ok | ok | ok | ok | ok | R |
| Crinkle | turn | R | ok | ok | ok | ok | ok | R |
| Crinkle | look | R | ok | ok | ok | ok | ok | R |
| Crinkle | nod | R | ok | ok | ok | ok | ok | R |
| Crinkle | shake | R | ok | ok | ok | ok | ok | R |
| Crinkle | react | R | ok | ok | ok | ok | ok | R |
| Crinkle | hop | R | ok | ok | ok | ok | ok | R |
| Crinkle | hold | R | ok | ok | ok | ok | ok | R |
| Crinkle | point | R | R | R | R | R | R | R |
| Crinkle | pick_up | R | ok | R | R | R | R | R |
| Crinkle | put_down | R | R | R | R | R | R | R |
| Crinkle | place_on | R | ok | R | R | R | R | R |
| Crinkle | drop | R | R | R | R | R | R | R |
| Crinkle | hand_over | R | R | ok | ok | ok | R | R |
| Pip | enter | ok | ok | ok | ok | ok | ok | ok |
| Pip | exit | ok | ok | ok | ok | ok | ok | ok |
| Pip | walk_to | R | R | R | R | R | R | R |
| Pip | turn | ok | ok | ok | ok | ok | ok | ok |
| Pip | look | ok | ok | ok | ok | ok | ok | ok |
| Pip | nod | ok | ok | ok | ok | ok | ok | ok |
| Pip | shake | ok | ok | ok | ok | ok | ok | ok |
| Pip | react | ok | ok | ok | ok | ok | ok | ok |
| Pip | hop | ok | ok | ok | ok | ok | ok | ok |
| Pip | hold | ok | ok | ok | ok | ok | ok | ok |
| Pip | point | R | R | R | R | R | R | R |
| Pip | pick_up | R | R | R | R | R | R | R |
| Pip | put_down | R | R | R | R | R | R | R |
| Pip | place_on | R | R | R | R | R | R | R |
| Pip | drop | R | R | R | R | R | R | R |
| Pip | hand_over | R | R | R | R | R | R | R |

## Refusals and failures

- R Snip enter at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 3.1 s
- R Snip enter at WR: shot 1 W 0-3.2: Snip at x 1720 is cut at 3.1 s
- R Snip exit at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip exit at WR: shot 1 W 0-3.2: Snip at x 1720 is cut at 0.0 s
- R Snip walk_to at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip walk_to at WR: shot 1 W 0-3.2: Snip at x 1720 is cut at 0.0 s
- R Snip turn at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip turn at WR: shot 1 W 0-3.2: Snip at x 1720 is cut at 0.0 s
- R Snip look at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip look at WR: shot 1 W 0-3.2: Snip at x 1720 is cut at 0.0 s
- R Snip nod at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip nod at WR: shot 1 W 0-3.2: Snip at x 1720 is cut at 0.0 s
- R Snip shake at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip shake at WR: shot 1 W 0-3.2: Snip at x 1720 is cut at 0.0 s
- R Snip react at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip react at WR: shot 1 W 0-3.2: Snip at x 1720 is cut at 0.0 s
- R Snip hop at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip hop at WR: shot 1 W 0-3.2: Snip at x 1720 is cut at 0.0 s
- R Snip hold at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip hold at WR: shot 1 W 0-3.2: Snip at x 1720 is cut at 0.0 s
- R Snip point at WL: beat 0.5-1.2 Snip point E: (1600, 1280) is 1288 u from Snip's shoulder; the reach is 129: stand closer (a work spot <mark>.L/.R)
- R Snip point at A: beat 0.5-1.2 Snip point E: (1600, 1280) is 1188 u from Snip's shoulder; the reach is 129: stand closer (a work spot <mark>.L/.R)
- R Snip point at B: beat 0.5-1.2 Snip point E: (1600, 1280) is 848 u from Snip's shoulder; the reach is 129: stand closer (a work spot <mark>.L/.R)
- R Snip point at C: beat 0.5-1.2 Snip point E: (1600, 1280) is 528 u from Snip's shoulder; the reach is 129: stand closer (a work spot <mark>.L/.R)
- R Snip point at D: beat 0.5-1.2 Snip point E: (1600, 1280) is 208 u from Snip's shoulder; the reach is 129: stand closer (a work spot <mark>.L/.R)
- R Snip point at E: beat 0.5-1.2 Snip point A: (300, 1280) is 1188 u from Snip's shoulder; the reach is 129: stand closer (a work spot <mark>.L/.R)
- R Snip point at WR: beat 0.5-1.2 Snip point A: (300, 1280) is 1308 u from Snip's shoulder; the reach is 129: stand closer (a work spot <mark>.L/.R)
- R Snip pick_up at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip pick_up at B: beat 0.5-1.5 Snip pick_up block: Snip faces right: turn to reach (390, 1340)
- R Snip put_down at WL: beat 0.5-1.5 Snip put_down A: block at x 300 would be on or by Snip's feet (76-344)
- R Snip put_down at B: beat 0.5-1.5 Snip put_down C: (960, 1422) is 260 u from Snip's shoulder; the reach is 129: stand closer (a work spot <mark>.L/.R)
- R Snip put_down at C: beat 0.5-1.5 Snip put_down B: Snip faces right: turn to reach (640, 1422)
- R Snip put_down at D: beat 0.5-1.5 Snip put_down C: Snip faces right: turn to reach (960, 1422)
- R Snip put_down at E: beat 0.5-1.5 Snip put_down D: Snip faces right: turn to reach (1280, 1422)
- R Snip put_down at WR: beat 0.5-1.5 Snip put_down A: Snip faces right: turn to reach (300, 1422)
- R Snip place_on at WL: shot 1 W 0-3.2: Snip at x 200 is cut at 0.0 s
- R Snip place_on at B: beat 0.5-1.5 Snip place_on box_top: Snip faces right: turn to reach (390, 1340)
- R Snip drop at WL: beat 0.5-1.5 Snip drop : block at x 254 would be on or by Snip's feet (76-344)
- R Snip drop at A: beat 0.5-1.5 Snip drop : block at x 354 would be on or by Snip's feet (176-444)
- R Snip drop at B: beat 0.5-1.5 Snip drop : block at x 694 would be on or by Snip's feet (516-784)
- R Snip drop at C: beat 0.5-1.5 Snip drop : block at x 1014 would be on or by Snip's feet (836-1104)
- R Snip drop at D: beat 0.5-1.5 Snip drop : block at x 1334 would be on or by Snip's feet (1156-1424)
- R Snip drop at E: beat 0.5-1.5 Snip drop : block at x 1654 would be on or by Snip's feet (1476-1744)
- R Snip drop at WR: beat 0.5-1.5 Snip drop : block at x 1774 would be on or by Snip's feet (1596-1864)
- R Snip hand_over at WL: shot 1 W 0-3.2: Snip at x -41 is cut at 0.0 s
- R Snip hand_over at A: shot 1 W 0-3.2: Snip at x 59 is cut at 0.0 s
- R Snip hand_over at E: shot 1 W 0-3.2: Crinkle at x 1841 is cut at 0.0 s
- R Snip hand_over at WR: shot 1 W 0-3.2: Crinkle at x 1961 is cut at 0.0 s
- R Crinkle enter at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 3.1 s
- R Crinkle enter at WR: shot 1 W 0-3.2: Crinkle at x 1720 is cut at 3.1 s
- R Crinkle exit at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle exit at WR: shot 1 W 0-3.2: Crinkle at x 1720 is cut at 0.0 s
- R Crinkle walk_to at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle walk_to at WR: shot 1 W 0-3.2: Crinkle at x 1720 is cut at 0.0 s
- R Crinkle turn at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle turn at WR: shot 1 W 0-3.2: Crinkle at x 1720 is cut at 0.0 s
- R Crinkle look at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle look at WR: shot 1 W 0-3.2: Crinkle at x 1720 is cut at 0.0 s
- R Crinkle nod at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle nod at WR: shot 1 W 0-3.2: Crinkle at x 1720 is cut at 0.0 s
- R Crinkle shake at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle shake at WR: shot 1 W 0-3.2: Crinkle at x 1720 is cut at 0.0 s
- R Crinkle react at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle react at WR: shot 1 W 0-3.2: Crinkle at x 1720 is cut at 0.0 s
- R Crinkle hop at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle hop at WR: shot 1 W 0-3.2: Crinkle at x 1720 is cut at 0.0 s
- R Crinkle hold at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle hold at WR: shot 1 W 0-3.2: Crinkle at x 1720 is cut at 0.0 s
- R Crinkle point at WL: beat 0.5-1.2 Crinkle point E: (1600, 1280) is 1258 u from Crinkle's shoulder; the reach is 148: stand closer (a work spot <mark>.L/.R)
- R Crinkle point at A: beat 0.5-1.2 Crinkle point E: (1600, 1280) is 1158 u from Crinkle's shoulder; the reach is 148: stand closer (a work spot <mark>.L/.R)
- R Crinkle point at B: beat 0.5-1.2 Crinkle point E: (1600, 1280) is 818 u from Crinkle's shoulder; the reach is 148: stand closer (a work spot <mark>.L/.R)
- R Crinkle point at C: beat 0.5-1.2 Crinkle point E: (1600, 1280) is 498 u from Crinkle's shoulder; the reach is 148: stand closer (a work spot <mark>.L/.R)
- R Crinkle point at D: beat 0.5-1.2 Crinkle point E: (1600, 1280) is 180 u from Crinkle's shoulder; the reach is 148: stand closer (a work spot <mark>.L/.R)
- R Crinkle point at E: beat 0.5-1.2 Crinkle point A: (300, 1280) is 1158 u from Crinkle's shoulder; the reach is 148: stand closer (a work spot <mark>.L/.R)
- R Crinkle point at WR: beat 0.5-1.2 Crinkle point A: (300, 1280) is 1278 u from Crinkle's shoulder; the reach is 148: stand closer (a work spot <mark>.L/.R)
- R Crinkle pick_up at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle pick_up at B: beat 0.5-1.5 Crinkle pick_up block: Crinkle faces right: turn to reach (390, 1340)
- R Crinkle put_down at WL: beat 0.5-1.5 Crinkle put_down A: block at x 300 would be on or by Crinkle's feet (40-385)
- R Crinkle put_down at B: beat 0.5-1.5 Crinkle put_down C: (960, 1422) is 247 u from Crinkle's shoulder; the reach is 148: stand closer (a work spot <mark>.L/.R)
- R Crinkle put_down at C: beat 0.5-1.5 Crinkle put_down B: Crinkle faces right: turn to reach (640, 1422)
- R Crinkle put_down at D: beat 0.5-1.5 Crinkle put_down C: Crinkle faces right: turn to reach (960, 1422)
- R Crinkle put_down at E: beat 0.5-1.5 Crinkle put_down D: Crinkle faces right: turn to reach (1280, 1422)
- R Crinkle put_down at WR: beat 0.5-1.5 Crinkle put_down A: Crinkle faces right: turn to reach (300, 1422)
- R Crinkle place_on at WL: shot 1 W 0-3.2: Crinkle at x 200 is cut at 0.0 s
- R Crinkle place_on at B: beat 0.5-1.5 Crinkle place_on box_top: Crinkle faces right: turn to reach (390, 1340)
- R Crinkle drop at WL: beat 0.5-1.5 Crinkle drop : block at x 262 would be on or by Crinkle's feet (40-385)
- R Crinkle drop at A: beat 0.5-1.5 Crinkle drop : block at x 362 would be on or by Crinkle's feet (140-485)
- R Crinkle drop at B: beat 0.5-1.5 Crinkle drop : block at x 702 would be on or by Crinkle's feet (480-825)
- R Crinkle drop at C: beat 0.5-1.5 Crinkle drop : block at x 1022 would be on or by Crinkle's feet (800-1145)
- R Crinkle drop at D: beat 0.5-1.5 Crinkle drop : block at x 1342 would be on or by Crinkle's feet (1120-1465)
- R Crinkle drop at E: beat 0.5-1.5 Crinkle drop : block at x 1662 would be on or by Crinkle's feet (1440-1785)
- R Crinkle drop at WR: beat 0.5-1.5 Crinkle drop : block at x 1782 would be on or by Crinkle's feet (1560-1905)
- R Crinkle hand_over at WL: shot 1 W 0-3.2: Crinkle at x -41 is cut at 0.0 s
- R Crinkle hand_over at A: shot 1 W 0-3.2: Crinkle at x 59 is cut at 0.0 s
- R Crinkle hand_over at E: shot 1 W 0-3.2: Snip at x 1841 is cut at 0.0 s
- R Crinkle hand_over at WR: shot 1 W 0-3.2: Snip at x 1961 is cut at 0.0 s
- R Pip walk_to at WL: beat 0.5-2.5 Pip walk_to C: 760 u in 2 s is faster than 300 u/s: give it at least 2.5 s
- R Pip walk_to at A: beat 0.5-2.5 Pip walk_to C: 660 u in 2 s is faster than 300 u/s: give it at least 2.2 s
- R Pip walk_to at B: beat 0.5-2.5 Pip walk_to D: 640 u in 2 s is faster than 300 u/s: give it at least 2.1 s
- R Pip walk_to at C: beat 0.5-2.5 Pip walk_to A: 660 u in 2 s is faster than 300 u/s: give it at least 2.2 s
- R Pip walk_to at D: beat 0.5-2.5 Pip walk_to B: 640 u in 2 s is faster than 300 u/s: give it at least 2.1 s
- R Pip walk_to at E: beat 0.5-2.5 Pip walk_to C: 640 u in 2 s is faster than 300 u/s: give it at least 2.1 s
- R Pip point at WL: beat 0.5-1.2 Pip point E: (1600, 1280) is 1335 u from Pip's shoulder; the reach is 72: stand closer (a work spot <mark>.L/.R)
- R Pip point at A: beat 0.5-1.2 Pip point E: (1600, 1280) is 1235 u from Pip's shoulder; the reach is 72: stand closer (a work spot <mark>.L/.R)
- R Pip point at B: beat 0.5-1.2 Pip point E: (1600, 1280) is 896 u from Pip's shoulder; the reach is 72: stand closer (a work spot <mark>.L/.R)
- R Pip point at C: beat 0.5-1.2 Pip point E: (1600, 1280) is 578 u from Pip's shoulder; the reach is 72: stand closer (a work spot <mark>.L/.R)
- R Pip point at D: beat 0.5-1.2 Pip point E: (1600, 1280) is 263 u from Pip's shoulder; the reach is 72: stand closer (a work spot <mark>.L/.R)
- R Pip point at E: beat 0.5-1.2 Pip point A: (300, 1280) is 1235 u from Pip's shoulder; the reach is 72: stand closer (a work spot <mark>.L/.R)
- R Pip point at WR: beat 0.5-1.2 Pip point A: (300, 1280) is 1355 u from Pip's shoulder; the reach is 72: stand closer (a work spot <mark>.L/.R)
- R Pip pick_up at WL: beat 0.5-1.5 Pip pick_up block: (390, 1340) is 124 u from Pip's shoulder; the reach is 72: stand closer (a work spot <mark>.L/.R)
- R Pip pick_up at A: beat 0.5-1.5 Pip pick_up block: block at (390, 1340) would sit by Pip's head (bottom y 1348): use another spot or mark
- R Pip pick_up at B: beat 0.5-1.5 Pip pick_up block: Pip faces right: turn to reach (390, 1340)
- R Pip put_down at WL: beat 0.5-1.5 Pip put_down A: block at x 300 would be on or by Pip's feet (120-292)
- R Pip put_down at B: beat 0.5-1.5 Pip put_down C: (960, 1422) is 263 u from Pip's shoulder; the reach is 72: stand closer (a work spot <mark>.L/.R)
- R Pip put_down at C: beat 0.5-1.5 Pip put_down B: Pip faces right: turn to reach (640, 1422)
- R Pip put_down at D: beat 0.5-1.5 Pip put_down C: Pip faces right: turn to reach (960, 1422)
- R Pip put_down at E: beat 0.5-1.5 Pip put_down D: Pip faces right: turn to reach (1280, 1422)
- R Pip put_down at WR: beat 0.5-1.5 Pip put_down A: Pip faces right: turn to reach (300, 1422)
- R Pip place_on at WL: beat 0.5-1.5 Pip place_on box_top: (390, 1340) is 124 u from Pip's shoulder; the reach is 72: stand closer (a work spot <mark>.L/.R)
- R Pip place_on at A: beat 0.5-1.5 Pip place_on box_top: block at (390, 1340) would sit by Pip's head (bottom y 1348): use another spot or mark
- R Pip place_on at B: beat 0.5-1.5 Pip place_on box_top: Pip faces right: turn to reach (390, 1340)
- R Pip drop at WL: beat 0.5-1.5 Pip drop : block at x 230 would be on or by Pip's feet (120-292)
- R Pip drop at A: beat 0.5-1.5 Pip drop : block at x 330 would be on or by Pip's feet (220-392)
- R Pip drop at B: beat 0.5-1.5 Pip drop : block at x 670 would be on or by Pip's feet (560-732)
- R Pip drop at C: beat 0.5-1.5 Pip drop : block at x 990 would be on or by Pip's feet (880-1052)
- R Pip drop at D: beat 0.5-1.5 Pip drop : block at x 1310 would be on or by Pip's feet (1200-1372)
- R Pip drop at E: beat 0.5-1.5 Pip drop : block at x 1630 would be on or by Pip's feet (1520-1692)
- R Pip drop at WR: beat 0.5-1.5 Pip drop : block at x 1750 would be on or by Pip's feet (1640-1812)
- R Pip hand_over at WL: no hand-over pair for Pip (left) and Crinkle (right): their reach bands don't meet

Result: PASS (173 ok, 163 refused, 0 failed of 336)
