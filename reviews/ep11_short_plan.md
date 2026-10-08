# Episode 11 transformation Short plan: "Plain Pumpkin Becomes a Glowing Friend!" (r2, 8 Oct: comedy fix + `plan_check` format)

**Length:** 30.0 s
**Lesson beat:** 0.9-6.4 s
Vertical 1080x1920, `episodes/ep11_short_transform.py`; the Ep 11 porch, early-evening light all through (no railing
hearts, sunset or wall projection). Reused: `props_porch`, `ep11_light`, rig2 Snip and Crinkle, `rig2_pip` (incl.
`puff_up`), `props_hand2`, the marker, `PK.FEATURES`. One new thing: a paper-lantern pumpkin that glows through its
paper. Earlier change lists: `reviews/ep11_short_fixes_sb1.md`, `_r1.md`, `_r1_plan.md`; this round `_r2.md`.

## b0. Feasibility
| Can we? | Answer |
|---|---|
| Rig, reach, props | Yes: all built in r1 (take reach measured: W_SN (903, 1327), CAP_P (888, 1291)); `puff_up` exists in `rig2_pip`. |
| Light | A paper lantern diffuses: the whole paper glows, no projection planes. |
| Time, source | Estimate 2-3 min render; build by 15 Oct for 18 Oct. AAP HealthyChildren.org: markers for little ones; battery light, not a candle. |

## b1. Story card
**Lesson: when it's a friend's turn, wait until they finish; then it's your turn.** Wrong → right: Crinkle, bouncing,
eyes only on the pumpkin, takes the marker out of Snip's paw while she is halfway round the first eye → he sees the
half eye and her empty paw, puts the marker back with its tip where the line stopped, then waits (paws behind his back,
copying Pip) and gets his turn from Pip. The marker carries it: Snip → Crinkle (wrong) → Snip → Pip → Crinkle.
**Angle (ROADMAP, quoted):** "A plain pumpkin gets a paper/paint face and glows (battery light placed by the
grown-up's paper hand)"; Short: "a 20-30 s 'Plain Pumpkin Becomes a Glowing Friend!' transformation Short".
**Engine:** B (Crinkle errs; trait 3). **Setting:** Ep 11 porch, early evening. **Outcome:** a face drawn in three
turns glows as one face. **Wow:** the whole paper lights from inside; the black lines stay dark (r2: the heart is
black too; one marker). **Music:** glock lead (music box), pluck bass, organ pad under the glow; F major, 104 bpm,
straight. **Safety:** markers without caps, tips only on the lantern; the take is a slow pinch, never a tug; the tea
light is touched only by the grown-up's hand (white body, side switch, LED dome, never opened, steady glow, no flame,
flicker or smoke), goes in through the top ring and stays inside; no candle, no cutting, no tool; nobody climbs; the
glow is a warm wash, never a beam on a face; nobody laughs at Crinkle (only he laughs, at himself). From 21.2 (r2; was
20.9) to the end, nobody touches the lantern: no paw, wing or foot on the paper or over the top ring; Crinkle's
wiggle-dance arms stay on the side away from the lantern; Pip dances in place (gate 1, F3).

## b2. Variety (the Ep 11 episode is parked; it is still the previous story)
| | Ep 9 | Ep 10 | Ep 11 episode (previous) | **This Short** |
|---|---|---|---|---|
| Engine | A | A | E | **B (Crinkle errs)** |
| Setting | car + street | beach | porch at dusk | porch at dusk (**repeat: the Lead's reuse decision**) |
| Mistake-maker | Snip | Snip | nobody | **Crinkle** |
| Outcome | drive to the beach | castle finished | dark spot → giant smile | **a face made in turns glows** |
| Wow | car drives off | ears spring back | projected smile on the wall | **glow through paper** |
| Lead instrument | organ comp + steel pan | ukulele + glock | organ, F, 116 swung | **glock (music box), F, 104 straight** |

## b3. Cause and effect
Frame 0: the plain orange lantern (BASE 960, 1505; 240 x 170) with a wire ring on top and a green stem curl; the one
marker (blue body, black ink) in Snip's paw, tip on the lantern; Pip waiting at 640, wings behind her back; Crinkle at
1080, bouncing.
1. Crinkle pinches the marker's top end; the tip lifts, the eye stops as a "C"; it slides out of Snip's opened fingers.
2. Her paw stays up, empty; she looks at the half eye; ears droop.
3. He crouches to draw (tip stops short, no mark), sees the half eye, then her teary face.
4. He gives it back, tip on the line's end; paw to chest, a bow; her ears spring up, a nod (6.4: the fix).
5. (r2) He copies Pip's waiting pose; two sways together; his third swings him a quarter round (gag 1). He grins.
6. Snip closes the "C" into an "O", draws the second eye, gives the marker to Pip (she was waiting first).
7. Pip draws the heart nose, then holds the marker up to Crinkle: his turn.
8. (r2) His slow smile stroke ends with one big squeak as the tip lifts: tongue in, eyes wide; Pip puffs into a ball; he laughs, she un-puffs and giggles (gag 2).
9. The hand brings a battery tea light from above, clicks it on above the ring, lowers it in; the paper glows, lines dark, warm halo and floor pool.
10. (r2) The dance in the glow: two wiggles, a wind-up, the third spins him right round (gag 3, callback of 5); Pip copies; he looks back and laughs at himself.

## b4. Shot list
Cameras: A 1.7x (880, 1250), view x 562-1198; B 2.0x (950, 1320), view x 680-1220; B2 1.8x (920, 1270); K 1.9x (1060,
1180); T 2.6x (958, 1300) (built 2.4x); END 1.4x (975, 1215); **K2 r2** 1.9x on Crinkle's head at x 1200 (estimate
(1230, 1180); the animator reads `head_pivot`). Bottom 19%: deck only. Built (r1): marker box 66-88 wide; lantern mask
x 840-1080, y 1319-1505; tea light 69 wide (`TEA_S`).

| # | Time (s) | Cam | What happens | Movements | Rig check |
|---|---|---|---|---|---|
| 1 | 0.0-0.6 | A | Frame 0: Snip (790, turn +0.5) has the marker on the lantern, eye 30% drawn; Pip (640) waits, wings behind back, small sway; Crinkle (1080, turn -0.5) bounces on his toes, paws up at chest, sparkle eyes locked on the lantern. Eye 30→50% (0.0-0.6). One bounce (0.0-0.3); Crinkle leans in, left paw rising toward the marker's top end (0.3-0.6). | stroke reveal; bounce; lean -10, sq 0.92 | OK (built) |
| 1b r1 | 0.6-2.8 | T | **The take, ≥1.0 s with both paws, never covered (B1).** Snip draws 50%→"C" (0.6-0.9; eye_l key (0.9, C_STOP)). Crinkle's left paw comes in from the upper right (0.6-0.9) and pinches the very top end (CAP 46). From 0.85 his eyes are `normal` (no sparkle), brows up, closed `smile`, pupils on the eye spot, never on Snip or the camera (R1). Both paws on the marker, still (0.9-1.2; still 1.0). 1.2: the tip lifts 3 off the paper, the eye stops as a "C"; Snip's fingers open, her paw does not move (W_SN fixed to 2.8). 1.2-1.9: the marker slides slowly up along its own axis (about 70) out of her open fingers, never sideways, no jerk. 1.9-2.3: he carries it up and right to LIFT (1010, 1262), eyes still on the lantern. Snip's empty paw, loosely open, in place 1.9-2.8 (0.9 s); her eyes: the "C" (1.25, mouth `o`), then her empty paw (2.0). **Visibility:** 0.9-2.3 the marker is drawn over both arms; ≥50% of its pixels outside both arm masks in every frame (`--check`); both pairs of eyes in frame (stills 1.0, 2.4). | pinch, hold, slide, lift | OK (built) |
| 2 r1 | 2.8-6.5 | B2 | Both faces. Ears droop (2.9-3.3); glassy eyes, sad brows (3.1; never angry); Snip looks at the eye, not at Crinkle; her paw stays open beside it. Crinkle crouches toward the smile spot, eager closed smile, brows up, **no tongue** (R1), tip stops 20 short at (1018, 1418) (2.8-3.2). **Realisation 1.3 s:** eyes to the half eye, held (3.2-3.75); eyes up to Snip's teary face, held (3.75-4.25); O mouth, sorry brows, shoulders sag (4.25-4.5). **Give-back 0.9 s:** he lowers it slowly, pinching only its top end, the whole marker in view (≥50% uncovered), tip onto the line's end, into her open fingers (4.5-5.4); **lets go at 5.4**; open paw, palm toward himself, straight back to his chest (5.4-5.8), ≥40 clear by 5.55; then Snip's fingers close (5.8-5.9). Never two grips; the marker does not move from 5.4. Bow, paw on chest (5.8-6.2); Snip's ears spring up (6.0), nod (6.2-6.4). | look; sq 0.94; place; paw → chest | OK (built) |
| 3 r2 | 6.5-9.6 | A | Crinkle straightens, half step back to 1100 (6.5-6.9), paws behind his back like Pip (6.9). **Gag 1:** two sways with Pip, in time, lean ±6 (6.9-8.4); both upright and still (8.4-8.8); Pip sways small, his third sway swings him a quarter round (turn -0.35 → 0.0), lean +10, away from the lantern, feet down, tiny wobble (8.8-9.4), swings back (9.4-9.6). Every mask ≥10 from the lantern 6.5-10.6, measured by `--check` (gate 1 r1, R2-2). | sway; turn swing; arms back | T2 + turn built; retime |
| 4 r2 | 9.6-10.6 | K | Sheepish grin at once (9.6), blink, one belly bounce (9.8-10.2), calm waiting smile. **Nobody reacts to his slip before he grins (9.6) or at his laugh (29.3): no bigger smile, giggle note, pointing or covered mouth from Snip or Pip (gate 1 r1, R2-3).** | face; bounce | OK |
| 5 r2 | 10.6-12.8 | B | Snip closes the C into an O (10.7-11.2); hold (11.2-12.2); second eye, quicker (12.2-12.6); hold (12.6-12.8, then in A). | stroke reveal | OK, retime |
| 6 r2 | 12.8-14.3 | A | Snip gives the marker to Pip (12.9-13.3), steps back to 700, sweeps a paw (13.3-13.8); Pip waddles in front of Snip to the nose spot (13.4-14.3). | give; walks; sweep | OK, retime |
| 7 r2 | 14.3-16.7 | B | Pip draws the black heart nose: left half (14.4-15.0), right half (15.1-15.7), tongue tip; wing back by 15.9; hold (15.7-16.7). | wing IK, `draw_held` | OK, retime |
| 8 r2 | 16.7-18.3 | A | Pip holds the marker up toward Crinkle (16.8-17.2); he crouches and takes it over the lantern's top at about (915, 1320) (17.2-17.6); sparkle eyes, small wiggle (17.6-18.2). Pip walks to 740 (r2; was 770) (17.6-18.1). | crouch; reach | OK, retime |
| 9 r2 | 18.3-21.2 | B | **Gag 2:** the slow smile stroke (18.4-20.0), tongue `yum_l` ↔ `yum`, low squeaks; Pip copies the tongue (18.7). Tip still at the line's end, tongue out (20.0-20.4). The tip lifts with a big squeak (20.4): tongue in, eyes `wide`, brows up, head still (held 20.5-21.0); paw eases straight back, tip away from every face, no jerk; Pip `puff_up` into a ball, tuft up (20.6-21.2), ≥10 from the lantern (`--check`). | IK on the curve; take; puff | **T5 new (S)**: still 20.7 |
| 10 r2 | 21.2-22.2 | K | Blink at the marker (21.2-21.4); grin; laughs at it: `happy`, `smile_open`, two belly bounces (21.4-22.2). | face; bounce | OK |
| 11 r2 | 22.2-23.0 | B | Pip un-puffs (22.2-22.5), looks at her own feathers and giggles (hop, grin beak, 22.5-22.8); Snip's ears wiggle. Crinkle steps back to 1200 (22.2-22.8). Finished face, nothing on the lantern. All three clear before the hand enters at 23.0 (safety N4; `--check` window from 22.8). | un-puff; walk | OK |
| 12 r2 | 23.0-26.2 | B | The hand comes straight down, pinching the tea light at its top rim (23.0-23.5); click, LED dome lit (23.7); hold (23.7-24.3); lowered through the ring (24.3-25.0), the paper lights top down, then all; hand leaves upward (25.0-25.3); hold the glow (25.3-26.2). | `H.Arm.draw_to` | OK (built), +1.0 s |
| 13 r2 | 26.2-29.0 | B → END, pull 26.2-27.8 | Snip hops (26.6). **Gag 3:** wiggles 1, 2, paws up (26.4-27.6), Pip copies small and late (26.8-27.9); he squashes down, still (27.9-28.2); wiggle 3 swings him right round (turn -0.35 → +0.55, 28.2-28.5); he wiggles on facing the wrong way (28.5-29.0); Pip turns round too, very serious (28.6). **F3:** Crinkle at 1200, Pip at 740; every mask ≥10 from the lantern mask 21.2-30.0 (`--check`). | turn swing, paws up | T4 built; retime |
| 14 r2 | 29.0-30.0 | K2 | He looks back over his shoulder (hturn), blinks (29.0-29.3); laughs at himself, paws on tummy, three belly bounces (29.3-30.0), lit by the glow; end chord 29.7. | hturn; bounce | **K2 new (S)**: still 29.5 |

Cuts (r2): 0.6, 2.8, 6.5, 9.6, 10.6, 12.8, 14.3, 16.7, 18.3, 21.2, 22.2, 29.0. Code (r2): `DUR` 30.0; `T_PULL` (26.2, 27.8);
`T_CLICK` 23.7; `PIP_X1` 740; `BACK` pip (-1.0, 12.9), cr (6.9, 17.1); eye_l (0.0, 0.30), (0.6, 0.50), (0.9, C),
(10.7, C), (11.2, 1.0); eye_r 12.2-12.6; heart_l 14.4-15.0; heart_r 15.1-15.7; smile 18.4-20.0.

## b5. Hook and gags
**Hook:** frame 0 mid-action; the pinch at 0.9, the "C" at 1.2, the marker out of Snip's paw by 1.9. The mistake is
the hook, so gag 1 starts right after the fix. **Why r1 failed the 7-part test:** the sway slip had no pattern and no
pause (parts 2, 3); the end had a 0.6 s set-up, no pause, no face close-up (2, 3, 6); 8.3-26.5 had no gag. **r2:** a
two-beat pattern before every break, a still pause with the music resting, a face close-up after every break, and a
middle gag from the bible line "careful tongue-out concentration broken by a tiny surprise".

| Time (s) | Type | Trait | Set-up (s) | Pause (s) | Break (s) | Break size (%) | Joke signal | Reaction (s) | Sound | Topper | Test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6.9-10.6 r2 | G4 copycat breaks (flipped: he copies Pip) | Crinkle: the dance can go a little too far; copying Pip's pose | 1.5 (6.9-8.4): two sways side by side; we expect a third the same | 0.4 (8.4-8.8): both still; tick-tock rests | 0.8 (8.8-9.6): his sway swings him a quarter round, wobble, back | 36 (estimate: body about 230 wide in A's 636 view) | Crinkle grins at himself at 9.6; nobody else reacts (R2-3) | 1.0 (9.6-10.6, K) | tick-tock; rest; wobbly glock bend up and back (never down); one low giggle note | none | PASS: trait; 1.5 pattern; 0.4 still; 0.8 at 36%; his grin at once; K 1.0; feet down, ≥10 from the lantern |
| 18.3-23.0 r2 | G8 fooled sense (a big squeak; only the marker) | Crinkle: tongue-out concentration broken by a tiny surprise; Pip: the puff-up | 1.7 (18.3-20.0): the slow stroke, tongue sliding, the same soft squeaks as every stroke | 0.4 (20.0-20.4): tip still, tongue out; one held note | 0.8 (20.4-21.2): the tip lifts with one big squeak; tongue in, eyes wide | 28 (estimate: head about 150 wide in B's 540 view) | Crinkle grins and laughs at the marker by 21.4; Pip giggles at her own feathers, never at him | 1.0 (21.2-22.2, K) | big rubber-toy squeak (synth, 0.3 s, soft attack); feather "fwump"; low giggle run; Pip's two octaves up | Pip copies his small take as a full puff-up (20.6), un-puffs and giggles (22.2-22.8) | PASS: trait; 1.7 set-up; 0.4 still; 0.8 at 28%; his laugh within 1.0; K 1.0; harmless sound, tip away from faces, line already whole |
| 26.2-30.0 r2 | G5 too far | Crinkle: the wiggle-dance goes too far; callback of the 8.8 sway | 1.5 (26.4-27.9): wiggles 1 and 2; Pip copies; we expect a third the same | 0.3 (27.9-28.2): he squashes down, still; music rests | 0.8 (28.2-29.0): wiggle 3 spins him right round; he dances on facing the wrong way | 30 (estimate: body about 230 wide in END's 771 view) | Crinkle looks back, blinks, laughs at himself by 29.3 | 1.0 (29.0-30.0, K2) | boings; rest; paper swish; two rising glock notes on the look back; giggle run; end chord | Pip copies the wrong-way dance, very serious (28.6) | PASS: running joke + callback; 1.5 pattern; 0.3 still; 0.8 at 30%; his laugh in 0.3; K2 1.0; feet down, ≥10 from the lantern |

**Charm (not counted):** the bounce (0-0.6), Pip's tongue copy (18.7), Snip's hop (26.6). **Close-ups:** T 2.2 s, B2
3.7 s, K 1.0, K 1.0, K2 1.0; holds: O 1.0, heart 1.0, finished face 0.8 (+0.7 before the click), lit dome 1.3 seen,
glow to the end. No 6 s without a change (longest shot 3.7 s).

## b6. Sound (no voices; effects from the episode's banks)
| Action | Sound |
|---|---|
| Bounce; marker strokes | soft boings; short soft squeaks (Snip mid, Pip higher, Crinkle lower, slower) |
| The take (r1) | the pinch: a tiny paper tick (0.9); the tip lifts: the squeak stops, a soft "plip" (1.2), Snip's glock phrase breaks off mid-bar; the slide out: a soft paper slide (1.2-1.9); then near-silence |
| Ears droop | two falling glock notes |
| Crinkle understands (r1) | one soft low organ note, held and fading (4.25; no pitch bend, no falling "wah-wah" or sad-trombone figure; not a voice) (gate 1 r1, R2-1) |
| Hand-overs; sorry bow | small tap; warm pad swell, two soft chords (instruments only; no vocal, choir, crowd or "aww" sample) (gate 1, F1) |
| Gags 1-3 (r2) | as the gag table; every pause is a music rest or one held note; accents go up, never down |
| Pip's waddle; hand; click | pitter-pats; soft whoosh; small click + rising sparkle (23.7) |
| Paper glows | rising glock run into a warm F add9 chord, soft shimmer |
| Music by section (r2) | 0-1.2 bouncy tune, breaks off at 1.2; pad to 6.5; tick-tock 6.5-9.6 (rest 8.4-8.8); turn phrases 10.6-20.0 (Snip resolves at 11.2); held note 20.0-20.4; careful chord 23.0-25.0; swell 25.0-26.2; reprise 26.2-27.9; rest 27.9-28.2; reprise under the giggle; end chord 29.7 |

## b7. Shorts
This is the transformation Short: own timeline and cameras (T, B, B2, K, K2, END), holds ≥1 s on the O, the heart and the glow.

## b8. Toolkit work
| # | Work | Size |
|---|---|---|
| T1-T4 | Lantern prop, paws behind backs, the Short script, take slide and turn swings | built (r1); r2 retimes from 6.5 |
| T5 r2 | Gag 2: Crinkle's small take (tongue in, `wide`, paw eases back, head still); Pip's `puff_up` at 740 with a `--check` gap; camera K2; synth squeak and "fwump" | S |
**Riskiest, prototype first:** gag 2 at phone size: stills 20.2 (tongue out, tip at the line's end), 20.7 (his take
and Pip's ball readable in B, the ball clear of the lantern), 21.6 (K laugh); then 9.1, 28.6, 29.5.

## b9. Misread check
| Moment | Likely wrong reading (age 4) | Staging that rules it out |
|---|---|---|
| 0-1.2 | "Snip hogs the marker" | The eye only just started; Pip waits calmly; Snip passes it on unasked at 12.9. |
| 0-2.8 | "Two markers; he draws next to her" | One marker in the T close, both paws on it; the eye stops as a "C" as it slides out; her paw left empty. |
| 0.9-1.9 | "A tug-of-war" | Snip's paw never moves; her fingers open before the marker moves; it slides along its own axis, slowly. |
| 0.85-3.2 (R1) | "Bear looks smug / teasing" | No tongue until 18.4 (while drawing); no sparkle until 17.6; eyes on the lantern, never on Snip or the camera. |
| 2.3-4.5 | "He spoiled the drawing" | His tip stops 20 short: no stray line; the only change is the "C" beside her empty paw. |
| 4.5-5.9 | "Still tugging" / "she demands it back" | He lets go first (5.4), open paw to his chest; her paw never moves toward him. |
| 3.2-6.5 (lesson) | "Snip told him off" | No pointing, frowning or reaching; ears droop (sad, not angry); he works it out by looking. |
| 6.5-10.6 (r2) | "He's punished" / "he's falling" | He copies Pip's pose by choice; a quarter turn and wobble, feet down, back by himself, grinning at once. |
| 20.4-22.8 (r2) | "He broke it / did wrong" or "Pip is scared" | The smile is whole; the squeak comes with the tip lifting; he laughs within 1.0 s; Pip un-puffs at once and giggles at her own feathers. |
| 23.0-26.2 | "A fire" / "a scary face" | The click and lit LED dome come first; steady glow, no flame; everyone smiles. |
| 28.2-30.0 (r2) | "He's leaving" / "they laugh at him" | Paws up, smiling, wiggling in rhythm; Pip copies (a game); only he laughs, after looking back. |

## b10. Storyboard frames (gate 1b)
| Frame (s) | Shot | Shows |
|---|---|---|
| 0.0 | A | Frame 0: marker on the plain lantern, Pip waiting, Crinkle bouncing |
| 1.0 | T | Both paws on the marker, all of it seen |
| 2.4 | T | The "C", Snip's empty paw, the marker at Crinkle's chest |
| 4.0 | B2 | He looks at Snip's teary face |
| 5.0 | B2 | The give-back, the whole marker in view |
| 9.1 | A | Gag 1: his sway swung a quarter round, Pip's small |
| 17.2 | A | Pip holding the marker up to Crinkle |
| 20.7 | B | Gag 2: his take (tongue in, eyes wide), Pip a feather ball |
| 24.0 | B | The lit LED dome above the ring |
| 25.8 | B | The glowing face |
| 28.6 | END | Gag 3: Crinkle dancing the wrong way, Pip copying |
| 29.5 | K2 | He laughs at himself, lit by the glow |

## Key actions
| Key action | Time (s) | Object | Size (%) | Uncovered (s) |
|---|---|---|---|---|
| The mistake: the take | 0.9-2.3 | the marker | 15 (built box 66-88 x 2.4-2.6 / 1080 = 15-21) | 1.4 (target ≥50% of pixels clear every frame; `--check` measures) |
| The fix: the give-back | 4.5-5.9 | the marker | 11 (66-88 x 1.8 / 1080 = 11-15, computed) | 1.4 (target; `--check` measures) |
| His turn, given by Pip | 16.8-17.8 | the marker | 10 (66-88 x 1.7 / 1080 = 10-14, computed) | 1.0 (target; not measured) |
| The wow's cause: the tea light goes in | 23.0-25.0 | the tea light | 12 (69 x 2.0 / 1080 = 12.8, from `TEA_S`) | 1.3 (estimate: pinched at its top rim; dome seen 23.7-25.0) |

## b11. Hidden key actions
None: the click (LED dome seen) above the ring, the lowering and the glow are all shown.

## Props
| Prop | Colour | State |
|---|---|---|
| Paper-lantern pumpkin | orange paper, softer orange ribs; green stem curl and leaf; wire ring dark warm inside | plain at 0.0; face drawn in turns; glowing from 24.3 |
| Marker (one) | blue body, black ink | no cap; Snip → Crinkle → Snip → Pip → Crinkle |
| Drawn face | black: two round eyes, heart nose, big smile (r2: heart black, not red) | stays dark when lit |
| Battery tea light | white body, side switch, warm LED dome | off until 23.7, then steady inside; never opened, no flame |
| Grown-up's arm and hand | as `props_hand2` (sleeve, cuff) | from above, 23.0-25.3 only |
| Porch deck | as `props_porch`, early-evening grade | warm halo and floor pool from 24.3 |
