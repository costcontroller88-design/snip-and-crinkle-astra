# Character bible: Snip, Crinkle and Pip

Written 6 Oct 2026 by the story-designer, from Episodes 1–10, the pilot "Oops! A Splash of Blue" and the rig
(`episodes/rig2.py`, `episodes/acting.py`). Updated by the story-designer when an episode adds something on screen.
Every plan uses this file for gags: a gag must come from a trait or a running joke below.

## The three at a glance

| | Snip | Crinkle | Pip |
|---|---|---|---|
| Who | lilac bunny | caramel bear | little yellow duckling |
| Size (rig scale) | tall, mostly ears (1.15) | big and round (1.2) | small: her head reaches their shoulders (0.9) |
| Speed | quick: acts first, thinks after | slow and careful: thinks first | tiny steps, a beat behind the big two |
| Core | curious | kind | cautious, then brave |
| Comedy engine | the ears | things land on him and he's the last to notice | the copycat |
| Feelings show in | the ears (before the face) | the whole body (dance, slumped shoulders) | the feathers (tuft up or down, the puff-up) |
| Pronoun in our notes | "Snip" or "they" (no fixed gender on screen) | he | she (set in Episode 4) |

Snip and Crinkle are best friends, not siblings. Pip is a younger friend from the neighbourhood. The two big
friends look after her, and she adores them and copies everything they do.

---

## Snip

**Look.** Lilac paper bunny (fur 226,214,242), very tall ears with pink insides, pink nose and cheeks, blue tee
with a yellow star. The ears are separate pieces, so they move with every feeling. When shocked, the fur
"frizzes" into a spiky halo for a moment.

**Traits.**
1. Curious: has to look, touch (when safe) and try. First to notice anything new.
2. Quick and impulsive: hops before looking, starts drawing before planning. Most of Snip's mistakes come from
   speed, never from meanness.
3. Imaginative: sees a picture in everything (the splash that was a whale) and has the ideas.

**Hobby.** Drawing and painting. Snip paints at the easel in the art corner (pilot) and carries a sketchbook. When
Snip has an idea, Snip draws it, so the audience sees the idea.

**Gentle fear.** Sudden loud noises (a pop, a bang, a clatter): the ears flatten for a second, then spring back.

**Running joke: the tall ears get in the way, and they always tell the truth.** They pop a helmet off (Ep 7),
squash against the car roof (Ep 9), wilt like noodles in the heat (Ep 10), bonk into things hanging overhead, and
show what Snip feels a beat before the face does (they droop while Snip is still trying to smile).

**How Snip shows feelings** (rig names in brackets).
- Joy: ears shoot up and wiggle (`perk`, `happy`), sparkle or happy eyes, `smile_open`, two or three little hops.
- Sadness: ears droop flat (`droop`, `sad`), `glassy` eyes, `sad` brows, `frown`, head down (`head_dy`), a sniff.
- Surprise: ears snap up (`alarm`), fur frizz, `wide` eyes, `up` brows, `O` mouth, one hop.
- Curious: one ear bends over (`curious`), head tilt, `think` brows (never `focus`: it reads as angry).

**Never.** Never mocks anyone (laughs with, not at). Never touches heat, roads, sharp things or medicine alone.
Never gives up on a picture. Never stays cross: Snip forgives fast.

---

## Crinkle

**Look.** Caramel paper bear (fur 198,134,80), round ears, cream muzzle and tummy patch, dark brown nose, a yellow
scarf with orange stripes and a hanging end. Big, soft and round: the gentle giant of the three.

**Traits.**
1. Kind: notices when someone is sad and does something about it. Comes back to say sorry (pilot).
2. Slow and careful: does things one step at a time, tongue poking out when concentrating. Steady paws.
3. A little oblivious: so busy with the job in front of him that he misses what is happening on or behind him.
   When he is bouncy and happy he can also forget to look down (the pilot's trip over the toy block).

**Hobby.** Gardening. He grows vegetables and pumpkins, carries a watering can, and is proud of what he grows
(first shown in Episode 11).

**Gentle fear.** Wobbly high places: ladders, rocking stools, wobbly bridges. He is big and careful, and he never
climbs.

**Running jokes.**
- Something lands on Crinkle and he is the last to notice: a blue paint dot on his nose (pilot), a smile of light
  on his tummy (Ep 11). Everyone else sees it first; when he finally looks, he laughs the hardest.
- The happy wiggle-dance: side to side, paws up, bottom wiggling. It can go a little too far (bumps, wobbles).

**How Crinkle shows feelings.**
- Joy: the wiggle-dance (lean ±8°, paws up, small bounces), `happy` eyes, `smile_open`.
- Sadness: head down, paws together in front, shoulders sag (`sq` below 1), `sorry` or `sad` brows, `glassy` eyes,
  `wobble` or `frown` mouth, slow steps.
- Surprise: a hop with paws to his cheeks (`arms_front`), `wide` eyes, `up` brows, `O` mouth.
- Concentrating: crouched, `think` brows, tongue poking out of the side of his mouth (`yum`; a left-side version
  is new work in Ep 11).

**Never.** Never pushes or hurries a friend. Never leaves a friend sad. Never laughs at someone else's mistake (he
laughs at his own). Never climbs, even to help.

---

## Pip

**Look.** A little yellow paper duckling (body 255,214,70; wings 244,186,44; belly 255,238,164), an orange beak, a
three-feather tuft on her head, rosy cheeks, a red bow on the right side of her head, orange webbed feet, small
wings she uses like hands. In Episodes 4 and 8 she was built for the old 1x rig (`episodes/props_park.py`,
`Duckling`); from Episode 11 she needs rig v2 (head and body turns, wings as two-bone arms that can hold things,
walking feet, eyebrows, beak mouths).

**Traits.**
1. Cautious: new, big or dark things make her stop and check. She hides behind the nearest big friend, then peeks.
2. A copycat: copies whatever the big friends do, a beat late and in miniature (their dance, their head tilt,
   their concentration face).
3. Brave in small steps, and full of giggles once she feels safe. She is fair and patient: she waited her turn on
   the swing (Ep 8).

**Hobby.** Chasing sunbeams and splashing in puddles. Her favourite thing is her pink teddy with a bow (Ep 4).

**Gentle fear.** The dark, and big shadows. Also being left behind.

**Running joke: the copycat.** Whatever Snip or Crinkle do, Pip does too, smaller and a moment later, very
seriously. Her second signature is the **puff-up**: when startled she fluffs into a round ball of feathers with her
tuft straight up, then slowly un-puffs.

**How Pip shows feelings.**
- Joy: wings flap fast, little hops, tuft springs up, `sparkle` eyes, open grin beak, a waddle-wiggle.
- Sadness: tuft droops, sad beak, wings hang, looks at her feet, a soft falling "coo" sound (a sound effect, never
  a voice).
- Surprise or unsure: the puff-up, `wide` eyes, a tiny hop backwards, then a dash behind a friend.

**Never.** Never wanders off alone (she always stays near a friend). Never snatches or pushes in. Never laughs at
anyone. Writers' rule: Pip is never only the sad one. In every story she also gets joy and a contribution of her
own (an idea, a drawing, a game).

---

## The grown-up

Only a paper arm and hand (blue sleeve, white cuff), reaching in from off-frame; never a face or a full body
(`episodes/props_grownup.py`; thumbs-up hand in `episodes/props_car.py`). The grown-up handles heat, roads,
water, fire, sharp things and medicine, gives thumbs-ups, and helps when the friends ask. The friends ask by
showing (pointing, holding up a drawing), never with words.

## Already established on screen (keep it consistent)

| Where | What it set up |
|---|---|
| Ep 1–3, 5–7, 9, 10 | Snip makes the mistake, Crinkle helps with a sign or a demo; Crinkle is the steady helper |
| Ep 4 (park) | Snip finds Pip's lost pink teddy, hides it (the teddy's ears pop up), gives it back; Pip's happy dance |
| Ep 7 (garden) | Snip's tall ears pop the helmet off, twice, until Crinkle shows the ear holes |
| Ep 8 (playground) | Pip waits patiently for a turn on the swing; Snip gives her a turn and pushes, 1-2-3; Pip gives Snip a turn back |
| Ep 9 (car) | Snip's ears squash on the car roof and spring back |
| Ep 10 (beach) | Snip's ears wilt like noodles in the heat and spring back with each sip of water |
| Pilot (art corner) | Snip paints at the easel; Crinkle trips carrying blue paint, nearly sneaks away, says sorry; the blue-nose gag (he is the last to notice); the splash becomes a whale |
| Every episode | The signature jingle at the start and at the paw-bump; the paw-bump itself |

## Rules for writing them

1. Wordless: no voices, no talking sounds. Reactions are musical or soft effects (a giggle as a little run of
   notes, a sniff, a gasp of breath). Pip's peeps are rare sound effects on actions, never conversation.
2. Gags come from the traits above. The comedy is never at the expense of the one who is sad, unsure or wrong.
3. Rotate who makes the mistake; Pip is a "little one to look after" (engine E), not a third mistake-maker.
4. Reach and size are real: Pip can't reach what Snip and Crinkle reach; nobody climbs to fix that. The big
   friends bring things down to her level, or crouch.
5. **Comic engines** (gag types and the 7-part gag test: `docs/COMEDY_PLAYBOOK.md`). Each character gets laughs
   their own way; a gag that any of them could do is a "clothesline" gag: rewrite it.
   - **Snip: speed and ears.** Rushes in before looking (G5 too far, G6 funny body); the ears tell the truth a beat
     early or get in the way (G2 wrong feature). Snip's joke signal: ears wiggle and a hop-giggle.
   - **Crinkle: oblivious and too much.** The last to notice (G3, then a slow double take); the wiggle-dance that
     goes too far (G5); careful tongue-out concentration broken by a tiny surprise. Laughs hardest at himself.
   - **Pip: copycat and puff-up.** Copies a beat late and seriously, and the third copy breaks (G4); startled by
     something harmless into a feather ball, then un-puffs (G8, a take). Her giggle is the audience's permission to laugh.
