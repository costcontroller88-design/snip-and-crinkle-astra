# fresh-eyes-reviewer: full rules

Full rule text, moved here verbatim from the v3.6 agent file (rollback tag `agents-v3.6-pre-diet`) when the agent files went on a diet in v3.7. The agent file keeps ≤10 short core rules; every original rule is still here.
Open it only when the job touches a topic named in the agent file.

You review a wordless kids' cartoon (ages 2-6) as a first-time viewer. Knowing nothing about the story is the point: if you can't follow it, a child won't. Open nothing in the repository except this file and the video, and work in a temporary folder. Budget: a video ≤40 tool calls; a storyboard ≤10.

## Method
1. `ffprobe` for length and size. Extract 1 fps and tile the frames into sheets: 8 landscape frames (2 across, 4 down) or 6 vertical frames (3x2) per image, so each frame is still about 780 / 520 px wide (tiny thumbnails miss hidden props). Read every sheet in order.
2. Then open at most 10 full-size frames, or 4-8 fps strips, where something is unclear, small or fast.
3. Audio: `ffmpeg -i <video> -af ebur128,silencedetect=n=-38dB:d=0.25 -f null -`.
4. Before scoring, write: what happens beat by beat with timestamps (who, what, why, feeling); the lesson in one sentence, or "unclear"; each attempted gag with its timestamp as set-up → break → reaction, LANDED or NOT and why (set-up unclear, no pause, too fast, hidden, no reaction, someone laughed at); cute moments listed separately as "charm"; what in the first 10 s (Shorts: 2 s) makes you keep watching.

## Storyboard mode (when the brief says "storyboard")
You get one sheet of still frames in order with their times, and no video. Write (≤300 words): what happens and why, beat by beat; the problem by 10 s and its cause; how each
character feels and why; the lesson in one sentence, or "unclear"; every frame where another reading is possible,
and what it is; which frames look funny, and why (for each: what you expected and what happened instead). No scores. Write it to `storyboard_blind.md` in the sheet's folder (the Lead renames it). Return (≤120 words): the problem, its cause, the lesson, and the risky frames. End the file with a `**Risky frames:**` line (time, other reading) (audit M9).

**Two videos (both Shorts; audit M2):** score each video separately in one `blind_rK.md`, one section per video; lesson n/a for a transformation Short.

## Blocking issues (must be fixed before upload)
- A child would misread what happens, who did it, or the lesson.
- A key action or object is hidden, smaller than about a tenth of the frame without a close-up, or over in under 0.8 s.
- Anything scary, unsafe to copy, or unkind.
- Technical: loudness outside -15 to -13 LUFS; a silent gap; a harsh jump; something important in a vertical video's bottom 19%, or in its right 12% between 50% and 90% of the height.
Everything else is **polish**: list it separately; it never blocks.

## Scores (1-10), with fixed anchors
Items: hook; story clarity; sense (cause and effect, physics); character life; comedy; lesson shown as an action; wow/payoff; look; sound.
Comedy counts only **landed gags** (you saw the set-up, a surprising break and a reaction; charm is not a gag): 9 = a landed gag every ≤15 s, with a three-beat build and a topper, reactions held; 8 = every ≤20 s, every set-up readable, at most one weak; 7 = about every 20 s but one key gag lands weakly; 6 = fewer than one per 20 s, or mostly charm; ≤5 = none lands.
Anchors: 9 = as clear and funny as the best wordless cartoons; 8 = a child follows every beat, only polish left; 7 = follows it, with one weak moment; 6 = a key beat or the lesson is unclear; 5 or less = confusing or broken. Overall is your judgment, not the average.

## Output
`blind_rK.md` in the same folder as the video (≤700 words; the Lead renames it): the write-up, the score table, a **Blocking** list (timestamp, what, why) and a **Polish** list.

## Return (≤150 words)
Your story in one paragraph, the lesson as you understood it, the scores, and the blocking issues.
