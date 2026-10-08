# Episode 11 transformation Short plan: "Plain Pumpkin Becomes a Glowing Friend!" (r3)

**Length:** 30.0 s
**Lesson beat:** 0.9-6.4 s
Vertical 1080x1920, `episodes/ep11_short_transform.py`; the Ep 11 porch, early-evening light all through. Reused rigs and props as built. One new thing: a paper-lantern pumpkin that glows through its
paper. Change lists: `reviews/ep11_short_fixes_{sb1,r1,r1_plan,r2,r3}.md`.

## b0. Feasibility
| Can we? | Answer |
|---|---|
| Rig, reach, props | Yes: all built (r1); `puff_up` in `rig2_pip`. |
| Light | Whole paper glows. |
| Time, source | Build by 15 Oct for 18 Oct; sources as gate 1 (AAP). |

## b1. Story card
**Lesson: when it's a friend's turn, wait until they finish; then it's your turn.** Wrong → right: Crinkle, bouncing,
eyes only on the pumpkin, takes the marker out of Snip's paw while she is halfway round the first eye → he sees the
half eye and her empty paw, puts the marker back with its tip where the line stopped, then waits (paws behind his back,
copying Pip) and gets his turn from Pip. The marker carries it: Snip → Crinkle (wrong) → Snip → Pip → Crinkle.
**Angle (ROADMAP, quoted):** "A plain pumpkin gets a paper/paint face and glows (battery light placed by the
grown-up's paper hand)"; Short: "a 20-30 s 'Plain Pumpkin Becomes a Glowing Friend!' transformation Short".
**Engine:** B (Crinkle errs; trait 3). **Setting:** Ep 11 porch, early evening. **Outcome:** a face drawn in three
turns glows as one face. **Wow:** the whole paper lights from inside; the black lines stay dark. **Music:** glock lead (music box), pluck bass, organ pad under the glow; F major, 104 bpm,
straight. **Safety:** markers without caps, tips only on the lantern; the take is a slow pinch, never a tug; the tea
light is touched only by the grown-up's hand (white body, side switch, LED dome, never opened, steady glow, no flame,
flicker or smoke), goes in through the top ring and stays inside; no candle, no cutting, no tool; nobody climbs; the
glow is a warm wash, never a beam on a face; nobody laughs at Crinkle (only he laughs, at himself). From 21.2 to the end, nobody touches the lantern: no paw, wing or foot on the paper or over the top ring; Crinkle's
wiggle-dance arms stay on the side away from the lantern; Pip dances in place (gate 1, F3).

## b2. Variety
| | Ep 9 | Ep 10 | Ep 11 episode (previous) | **This Short** |
|---|---|---|---|---|
| Engine | A | A | E | **B (Crinkle errs)** |
| Setting | car + street | beach | porch at dusk | porch (**repeat: Lead's decision**) |
| Mistake-maker | Snip | Snip | nobody | **Crinkle** |
| Outcome | drive to the beach | castle finished | dark spot → giant smile | **a face made in turns glows** |
| Wow | car drives off | ears spring back | projected smile on the wall | **glow through paper** |
| Lead instrument | organ comp + steel pan | ukulele + glock | organ, F, 116 swung | **glock (music box), F, 104 straight** |

## b3. Cause and effect
Frame 0: plain lantern (BASE 960, 1505), wire ring, stem.
1. Crinkle pinches the marker; the eye stops as a "C"; it slides out of Snip's open fingers.
2. Her empty paw; ears droop. 3. He sees the half eye, then her teary face.
4. He gives it back, tip on the line's end; bow; her nod (6.4: the fix).
5. He copies Pip's waiting pose (gag 1). 6. Snip finishes the eyes, passes to Pip (waiting first).
7. Pip draws the nose, hands it to Crinkle. 8. His smile stroke ends in a big squeak (gag 2).
9. The hand clicks the tea light on, lowers it in; the paper glows. 10. Gag 3 in the glow (callback of 5).

## b4. Shot list
Cameras r3: A 1.7x (880, 1250), x 562-1198; B 2.0x (950, 1320) (shots 5, 7, 9); B2 1.8x (920, 1270), x 620-1220 (2.8-4.5); **G r3** 2.5x (990, 1180), x 774-1206 (4.5-5.9); **B3 r3** 1.5x (1005, 1180), x 645-1365 (22.2-29.0; Crinkle's head mask at 1260 meas. x 1016-1459; tea light 11.1%, from the meas. 14.8% at 2.0x; y raised from the still's 1290 to drop the path, estimate); K 1.9x (1060, 1180); T 2.6x (958, 1300); **END r3** 1.2x (1020, 1215) (his body mask meas. to x 1500 at 27.0); **K2 r3** 1.9x (1260, 1138) = `head_pivot(29.5)` - 42 in y, him at 1260 (meas.). Stills, r3 positions patched in, code unchanged: `build/ep11s/r3_cams_1600.png`. Bottom 19%: deck only. Marker box meas. 46-76 wide (2.9-6.4); lantern mask x 840-1080, y 1319-1505; tea light 69 wide (`TEA_S`).

| # | Time (s) | Cam | What happens | Movements | Rig check |
|---|---|---|---|---|---|
| 1 | 0.0-0.6 | A | Frame 0: Snip (790, turn +0.5) has the marker on the lantern, eye 30% drawn; Pip (640) waits, wings behind back, small sway; Crinkle (1080, turn -0.5) bounces on his toes, paws up at chest, sparkle eyes locked on the lantern. Eye 30→50% (0.0-0.6). One bounce (0.0-0.3); Crinkle leans in, left paw rising toward the marker's top end (0.3-0.6). | stroke reveal; bounce; lean -10, sq 0.92 | OK (built) |
| 1b r3 | 0.6-2.8 | T | **The take, ≥1.0 s with both paws, never covered (B1).** Snip draws 50%→"C" (0.6-0.9; eye_l key (0.9, C_STOP)). Crinkle's left paw comes in from the upper right (0.6-0.9) and pinches the very top end (CAP 46). From 0.85 his eyes are `normal` (no sparkle), brows up, closed `smile`, pupils on the eye spot, never on Snip or the camera (R1). Both paws on the marker, still (0.9-1.2; still 1.0). 1.2: the tip lifts 3 off the paper, the eye stops as a "C"; Snip's fingers open, her paw does not move (W_SN fixed to 2.8). 1.2-1.9: the marker slides slowly up along its own axis (about 70) out of her open fingers, never sideways, no jerk. 1.9-2.3: he carries it up and right to LIFT (1010, 1262), eyes still on the lantern. Snip's empty paw, loosely open, in place 1.9-2.8 (0.9 s); her eyes: the "C" (1.25, mouth `o`), then her empty paw (2.0). **Visibility r3:** 0.9-2.3 the marker drawn over both arms, ≥95% of its pixels visible in every frame (`--check`; Lead r3); both pairs of eyes in frame (stills 1.0, 2.4). | pinch, hold, slide, lift | OK (built) |
| 2 r3 | 2.8-4.5 | B2 | Both faces. Ears droop (2.9-3.3; in B2, meas.); glassy eyes, sad brows (3.1; never angry); Snip looks at the eye, not at Crinkle; her paw stays open beside it. Crinkle crouches toward the smile spot, eager closed smile, brows up, **no tongue** (R1), tip stops 20 short at (1018, 1418) (2.8-3.2). **Realisation 1.3 s:** eyes to the half eye, held (3.2-3.75); eyes up to Snip's teary face, held (3.75-4.25); O mouth, sorry brows, shoulders sag (4.25-4.5). | look; sq 0.94 | OK (built); r3 cut at 4.5 |
| 2b r3 | 4.5-5.9 | G | **Give-back 0.9 s:** he lowers it slowly, pinching only its top end, tip onto the line's end, into her open fingers (4.5-5.4); the marker drawn over both arms, ≥95% of its pixels visible (`--check`; Lead r3); 10.6-15.3% of the width (meas. 46-66 wide x 2.5; was 9.3-11.0% in B2). **Lets go at 5.4**; open paw, palm toward himself, straight back to his chest (5.4-5.8), **≥30 clear by 5.55** (r3; meas. 33.0-33.9 at 5.55-5.8, vs the old ≥40); then Snip's fingers close (5.8-5.9). Never two grips; the marker does not move from 5.4 (meas. 0.1). Both faces in frame. | place; paw → chest | camera G new (S); stills G 4.8, 5.6 |
| 3 r3 | 5.9-9.6 | A | Bow, paw on chest (5.8-6.2); Snip's ears spring up (6.0), nod (6.2-6.4) (r3: from B2). Crinkle straightens, half step back to 1100 (6.5-6.9), paws behind his back like Pip (6.9). **Gag 1:** two sways with Pip, in time, lean ±6 (6.9-8.4); both upright and still (8.4-8.8); Pip sways small, his third sway swings him a quarter round (turn -0.35 → 0.0), lean +10, away from the lantern, feet down, tiny wobble (8.8-9.4), swings back (9.4-9.6). The lantern is drawn in front of every body and never moves (no shift, tilt or wobble). Crinkle's and Pip's visible paws and wings stay ≥10 from the lantern mask, ring included, 6.5-10.6 (`--check`). Snip's drawing paw and marker are exempt (the lesson). Bodies, heads, ears and feet may stand behind it (gate 1 R4-1). | sway; turn swing; arms back | T2 + turn built; retime |
| 4  | 9.6-10.6 | K | Sheepish grin at once (9.6), blink, one belly bounce (9.8-10.2), calm waiting smile. **Nobody reacts to his slip before he grins (9.6) or at his laugh (29.3): no bigger smile, giggle note, pointing or covered mouth from Snip or Pip (gate 1 r1, R2-3).** **R3-4:** 8.8-9.6 and 28.2-29.3: Snip's eyes `normal`, mouth `smile` (soft, closed); Pip a calm sway (8.8-9.6) and a serious copy with a closed beak (28.2-29.3); no `smile_open`, `happy` eyes or giggle from either until his grin (9.6) or laugh (29.3). | face; bounce | OK |
| 5  | 10.6-12.8 | B | Snip closes the C into an O (10.7-11.2); hold (11.2-12.2); second eye, quicker (12.2-12.6); hold (12.6-12.8, then in A). | stroke reveal | OK, retime |
| 6  | 12.8-14.3 | A | Snip gives the marker to Pip (12.9-13.3), steps back to 700, sweeps a paw (13.3-13.8); Pip waddles in front of Snip to the nose spot (13.4-14.3). | give; walks; sweep | OK, retime |
| 7  | 14.3-16.7 | B | Pip draws the black heart nose: left half (14.4-15.0), right half (15.1-15.7), tongue tip; wing back by 15.9; hold (15.7-16.7). | wing IK, `draw_held` | OK, retime |
| 8  | 16.7-18.3 | A | Pip holds the marker up toward Crinkle (16.8-17.2); he crouches and takes it over the lantern's top at about (915, 1320) (17.2-17.6); sparkle eyes, small wiggle (17.6-18.2). Pip walks to 740 (17.6-18.1). | crouch; reach | OK, retime |
| 9 r3 | 18.3-21.2 | B | **Gag 2:** the slow smile stroke (18.4-20.0), tongue `yum_l` ↔ `yum`, low squeaks; Pip copies the tongue (18.7). Tip still at the line's end, tongue out (20.0-20.4). The tip lifts with a big squeak (20.4): tongue in, eyes `wide`, brows up, head still (held 20.5-21.0); his paw eases back and down to belly height (20.5-21.0), tip pointing at the lantern, away from him; the tip never rises above his chin and stays ≥60 from every head mask 20.4-22.8 (`--check`) (R3-2); Pip `puff_up` into a ball, tuft up (20.6-21.2). Pip's ball stands behind the lantern, which is drawn in front and does not move; her wings stay ≥10 from the lantern mask 20.6-21.2 (`--check`). **R3-3:** Pip's ball face: eyes `wide`, beak small `o` (20.6-20.9), then a closed smile from 21.0 while still round; no shaking, no shrinking back, no wing over her eyes. Crinkle's eyes stay on the marker 21.2-22.2, never on Pip. Snip keeps a soft closed smile 20.4-22.5. Nobody laughs or giggles at Pip before her own giggle (22.5). | IK on the curve; take; puff | **T5 new (S)**: still 20.7 |
| 10  | 21.2-22.2 | K | Blink at the marker (21.2-21.4); grin; laughs at it: `happy`, `smile_open`, two belly bounces (21.4-22.2). He looks down at the marker held at belly height; it is never raised to his face; the bounces go straight up and down (R3-2). | face; bounce | OK |
| 11 r3 | 22.2-23.0 | B3 | Pip un-puffs (22.2-22.5), looks at her own feathers and giggles (hop, grin beak, 22.5-22.8); Snip's ears wiggle. Crinkle steps back to 1260 (r3; was 1200) and faces front (turn 0) (22.2-22.8). Snip steps back to 660 (r3; was 700: her head was then nearest the hand, meas. 1.0 at 23.47; 40.7 at 660) (22.2-22.8). Finished face, nothing on the lantern. All three clear before the hand enters at 23.0 (safety N4; `--check` window from 22.8). | un-puff; walk | OK |
| 12 r3 | 23.0-26.2 | B3 | The hand comes straight down, pinching the tea light at its top rim (23.0-23.5); click, LED dome lit (23.7); hold (23.7-24.3); lowered through the ring (24.3-25.0), the paper lights top down, then all; hand leaves upward (25.0-25.3); hold the glow (25.3-26.2). 23.0-25.3: the hand and tea light stay ≥30 and the sleeve ≥10 from every head mask, ears included (`--check`). The arm never crosses a face or an ear. Fix by staging (his x, turn, lean +6 away), never by drawing the arm behind him. **r3:** at 1260, turn 0 he meas. 5.5 at 24.8, so he also leans +6 away 24.3-25.3, watching the light (estimate +30; if `--check` <30, stand at 1290). Pip meas. 48.5. | `H.Arm.draw_to` | OK (built), +1.0 s |
| 13 r3 | 26.2-29.0 | B3 → END, pull 25.4-27.8 (built) | Snip hops (26.6). **Gag 3:** wiggles 1, 2, paws up (26.4-27.6), Pip copies small and late (26.8-27.9); he squashes down, still (27.9-28.2); wiggle 3 swings him right round (turn -0.35 → +0.55, 28.2-28.5); he wiggles on facing the wrong way (28.5-29.0); Pip turns round too, very serious (28.6). **F3:** from 21.2 no paw, wing, foot or marker touches the paper or goes over the top ring: visible paws, wings and markers ≥1 from the lantern mask 21.2-22.8 and ≥10 22.8-30.0, incl. the spin and Pip's turn (`--check`); the lantern is drawn in front of every body and never moves; Crinkle at 1260 from 22.8 (R4-2), Pip at 740. Snip at 660 (r3). | turn swing, paws up | T4 built; retime |
| 14 r3 | 29.0-30.0 | K2 | He looks back over his shoulder (hturn), blinks (29.0-29.3); laughs at himself, paws on tummy, three belly bounces (29.3-30.0), lit by the glow; end chord 29.7. | hturn; bounce | K2 r3 (1260, 1138) (meas.); still K2 29.5 |

Cuts (r3): 0.6, 2.8, 4.5, 5.9, 9.6, 10.6, 12.8, 14.3, 16.7, 18.3, 21.2, 22.2 (to B3), 29.0. Code keys as built (`--cuts`).

## b5. Hook and gags
**Hook:** frame 0 mid-action; the pinch at 0.9, the "C" at 1.2, the marker out of Snip's paw by 1.9. The mistake is
the hook.

| Time (s) | Type | Trait | Set-up (s) | Pause (s) | Break (s) | Break size (%) | Joke signal | Reaction (s) | Sound | Topper | Test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6.9-10.6 r2 | G4 copycat breaks (flipped: he copies Pip) | Crinkle: the dance goes a little too far | 1.5 (6.9-8.4): two sways side by side; we expect a third the same | 0.4 (8.4-8.8): both still; tick-tock rests | 0.8 (8.8-9.6): his sway swings him a quarter round, wobble, back | 36 (estimate) | Crinkle grins at himself at 9.6; nobody else reacts (R2-3) | 1.0 (9.6-10.6, K) | tick-tock; rest; wobbly glock bend up and back (never down); one low giggle note | none | PASS (7-part test) |
| 18.3-23.0 r2 | G8 fooled sense (a big squeak; only the marker) | Crinkle: tongue-out concentration broken by a tiny surprise; Pip: the puff-up | 1.7 (18.3-20.0): the slow stroke, tongue sliding, the same soft squeaks as every stroke | 0.4 (20.0-20.4): tip still, tongue out; one held note | 0.8 (20.4-21.2): the tip lifts with one big squeak; tongue in, eyes wide | 28 (estimate) | Crinkle grins and laughs at the marker by 21.4; Pip giggles at her own feathers, never at him | 1.0 (21.2-22.2, K) | rubber-toy squeak (synth, 0.3 s, soft attack, no click), no louder than the end chord at 29.7 (momentary within 3 LU, `ebur128`); no sting, crash or drum hit (R3-1); feather "fwump"; low giggle run; Pip's two octaves up | Pip copies his small take as a full puff-up (20.6), un-puffs and giggles (22.2-22.8) | PASS (7-part test) |
| 26.2-30.0 r2 | G5 too far | Crinkle: the wiggle-dance goes too far; callback of the 8.8 sway | 1.5 (26.4-27.9): wiggles 1 and 2; Pip copies; we expect a third the same | 0.3 (27.9-28.2): he squashes down, still; music rests | 0.8 (28.2-29.0): wiggle 3 spins him right round; he dances on facing the wrong way | 30 (estimate) | Crinkle looks back, blinks, laughs at himself by 29.3 | 1.0 (29.0-30.0, K2) | boings; rest; paper swish; two rising glock notes on the look back; giggle run; end chord | Pip copies the wrong-way dance, very serious (28.6) | PASS (7-part test) |
**Close-ups:** T 2.2 s, B2 1.7 s, G 1.4 s (r3), K 1.0, K 1.0, K2 1.0; holds: O 1.0, heart 1.0, finished face 0.8 (+0.7 before the click), lit dome 1.3 seen,
glow to the end. No 6 s without a change (longest shot 3.7 s).

## b6. Sound (no voices; effects from the episode's banks)
| Action | Sound |
|---|---|
| Bounce; marker strokes | soft boings; short soft squeaks (Snip mid, Pip higher, Crinkle lower, slower) |
| The take (r1) | a tiny paper tick (0.9); the squeak stops, a soft "plip" (1.2), Snip's phrase breaks off; a soft paper slide (1.2-1.9); near-silence |
| Ears droop | two falling glock notes |
| Crinkle understands (r1) | one soft low organ note, held and fading (4.25; no pitch bend, no falling "wah-wah" or sad-trombone figure; not a voice) (gate 1 r1, R2-1) |
| Hand-overs; sorry bow | small tap; warm pad swell, two soft chords (instruments only; no vocal, choir, crowd or "aww" sample) (gate 1, F1) |
| Gags 1-3 | as the gag table; every pause is a music rest or one held note; accents go up, never down; the squeak's level per R3-1 |
| Pip's waddle; hand; click | pitter-pats; soft whoosh; small click + rising sparkle (23.7) |
| Paper glows | rising glock run into a warm F add9 chord, soft shimmer |
| Music by section | 0-1.2 bouncy tune, breaks off at 1.2; pad to 6.5; tick-tock 6.5-9.6 (rest 8.4-8.8); turn phrases 10.6-20.0 (Snip resolves at 11.2); held note 20.0-20.4; careful chord 23.0-25.0; swell 25.0-26.2; reprise 26.2-27.9; rest 27.9-28.2; reprise under the giggle; end chord 29.7 |

## b7. Shorts
Own timeline and close cameras (b4); holds ≥1 s (b5).

## b8. Toolkit work
| # | Work | Size |
|---|---|---|
| T1-T4 | r1 builds | built (r1); r2 retimes from 6.5 |
| T5 r2 | Gag 2 take and Pip's `puff_up` (shot 9); camera K2; synth squeak and "fwump" | S |
| T6 r3 | Cameras G, B3, END 1.2x; cuts 4.5, 5.9; Crinkle 1260 (lean +6 24.3-25.3), Snip 660 from 22.2; G in the hires pass (2.5x, like T); `--check`: ≥95% visible, let-go ≥30, R4-1 scopes, hand gap per head | S |
**Riskiest, prototype first (r3):** the hand gap at 24.8 (Crinkle's lean); then G 4.8, 5.6; gag 2 stills 20.2, 20.7, 21.6; then 9.1, 28.6, 29.5.

## b9. Misread check
| Moment | Likely wrong reading (age 4) | Staging that rules it out |
|---|---|---|
| 0-1.2 | "Snip hogs the marker" | The eye only just started; Pip waits calmly; Snip passes it on unasked at 12.9. |
| 0-2.8 | "Two markers; he draws next to her" | One marker, both paws on it in T; the "C" and her empty paw. |
| 0.9-1.9 | "A tug-of-war" | Her paw never moves; fingers open first; a slow slide along its axis. |
| 0.85-3.2 (R1) | "Bear looks smug / teasing" | No tongue until 18.4 (while drawing); no sparkle until 17.6; eyes on the lantern, never on Snip or the camera. |
| 2.3-4.5 | "He spoiled the drawing" | His tip stops 20 short: no stray line. |
| 4.5-5.9 | "Still tugging" / "she demands it back" | He lets go first (5.4), open paw to his chest; her paw never moves toward him. |
| 3.2-6.5 (lesson) | "Snip told him off" | No pointing, frowning or reaching; ears droop (sad, not angry); he works it out by looking. |
| 6.5-10.6 | "He's punished" / "he's falling" | By choice he copies Pip; quarter turn, feet down, back by himself, grinning at once. |
| 20.4-22.8 | "He broke it / did wrong" or "Pip is scared" | The smile is whole; the squeak comes with the tip lifting; he laughs within 1.0 s; Pip un-puffs at once and giggles at her own feathers. |
| 23.0-26.2 | "A fire" / "a scary face" | The click and lit LED dome come first; steady glow, no flame; everyone smiles. |
| 28.2-30.0 | "He's leaving" / "they laugh at him" | Paws up, smiling, wiggling in rhythm; Pip copies (a game); only he laughs, after looking back. |

## b10. Storyboard frames (gate 1b)
| Frame (s) | Shot | Shows |
|---|---|---|
| 0.0 | A | Frame 0: marker on the plain lantern, Pip waiting, Crinkle bouncing |
| 1.0 | T | Both paws on the marker, all of it seen |
| 2.4 | T | The "C", Snip's empty paw, the marker at Crinkle's chest |
| 4.0 | B2 | He looks at Snip's teary face |
| 5.0 r3 | G | The give-back, the whole marker in view |
| 9.1 | A | Gag 1: his sway swung a quarter round, Pip's small |
| 17.2 | A | Pip holding the marker up to Crinkle |
| 20.7 | B | Gag 2: his take (tongue in, eyes wide), Pip a feather ball |
| 24.0 r3 | B3 | The lit LED dome above the ring |
| 25.8 r3 | B3 | The glowing face |
| 28.6 | END | Gag 3: Crinkle dancing the wrong way, Pip copying |
| 29.5 | K2 | He laughs at himself, lit by the glow |

## Key actions
| Key action | Time (s) | Object | Size (%) | Uncovered (s) |
|---|---|---|---|---|
| The mistake: the take | 0.9-2.3 | the marker | 15.9 (meas. 15.9-20.3 in T) | 1.4 (r3: drawn over both arms, ≥95% of its pixels visible every frame; `--check`; not checked yet) |
| The fix: the give-back | 4.5-5.9 | the marker | 10.6 r3 (meas. 10.6-15.3 in G) | 1.4 (r3: as the take; not checked yet) |
| His turn, given by Pip | 16.8-17.8 | the marker | 17.7 (meas. 17.7-17.9 in A) | 1.0 (target; not measured) |
| The wow's cause: the tea light goes in | 23.0-25.0 | the tea light | 11.1 r3 (meas. 14.8 at 2.0x; x 1.5/2.0 in B3) | 1.3 (estimate) |

## Measured checks (the animator measures every estimate first and updates this table from the final `--check`)
| Check | Need | Measured | Source |
|---|---|---|---|
| Hand and tea light to Crinkle's head 23.0-25.3 (at 1260, +6 lean) | 30 | estimate (5.5 without the lean) | estimate; `--check` r2 at 1260 |
| Hand and tea light to Snip's head 23.0-25.3 (at 660) | 30 | 40.7 | `--check` (designer r3) |
| Sleeve to every head mask, ears included, 23.0-25.3 | 10 | estimate | estimate |
| Let-go: Crinkle's paw to the marker by 5.55 | 30 | 33.0 | `--check` r2 build, 5.55-5.80 |
| Marker tip to every head mask 20.4-22.8 | 60 | 134.8 | `--check` r2 build |
| Visible paws, wings, marker to the lantern mask (R4-1; Snip's drawing paw exempt 6.5-10.6) | 10 | estimate | estimate |
| Paws, wings, markers to the lantern mask 21.2-22.8 | 1 | estimate | estimate |

## b11. Hidden key actions
None: click, lowering and glow all shown (shot 12).

## Props
| Prop | Colour | State |
|---|---|---|
| Paper-lantern pumpkin | orange paper, softer orange ribs; green stem curl and leaf; wire ring dark warm inside | plain at 0.0; face drawn in turns; glowing from 24.3 |
| Marker (one) | blue body, black ink | no cap; Snip → Crinkle → Snip → Pip → Crinkle |
| Drawn face | black: two round eyes, heart nose, big smile (r2: heart black, not red) | stays dark when lit |
| Battery tea light | white body, side switch, warm LED dome | off until 23.7, then steady inside; never opened, no flame |
| Grown-up's arm and hand | as `props_hand2` (sleeve, cuff) | from above, 23.0-25.3 only |
| Porch deck | as `props_porch`, early-evening grade | warm halo and floor pool from 24.3 |
