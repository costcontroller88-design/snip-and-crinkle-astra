# Handoff: read this first (written 2026-10-05)

You are continuing work for the owner of the YouTube channel **Snip & Crinkle (@SnipAndCrinkle)**, a wordless kids' Shorts channel made entirely with this code. The owner is not technical and relies on you to make decisions and do the work. They like a thorough analysis from all angles followed by a firm recommendation, and **harsh, honest ratings** (score 1–10 and say what is weak). They are in India.

## Where things stand
- **Channel setup is done:** name, handle, banner and profile picture (`tools/brand.py`), description, keywords, **made for kids = Yes**, country = India, and upload defaults (Education, language "Not applicable", footer description). Optional: default tags are still empty. The owner still has to turn on 2-Step Verification.
- **Episode 1 is final:** `episodes/ep01_v3_can_snip_wait.py` ("Can Snip Wait?"), scored 8/10, and passes `tools/check_video.py`. Render it with `python3 episodes/ep01_v3_can_snip_wait.py`. MP4s are git-ignored.
  - Upload title: `Can Snip Wait? ⏳☕ | Snip & Crinkle #shorts`
  - Upload description (goes above the default footer): "Snip wants the yummy drink… but it's HOT! ✋ or ⏳? What should Snip do? Wait with Snip & Crinkle and count 1, 2, 3 until it's cool! ☕✅"
- **Episodes 2–5 are in progress.** An earlier attempt stopped on a usage limit. Partial work is committed on branches `episode-02` … `episode-05` (props and backgrounds, plus episode scripts for 3 and 4). Follow `EPISODE_GUIDE.md` exactly (rules, 18s template, quality gate).
  - Episode 3 note from the last attempt: the tumble crops Snip off the left edge, and the "idea bulb" collides with the wall picture. Fix both.

## How to work
1. `./setup_cloud.sh` (ffmpeg, Pillow, numpy, Fredoka font).
2. For each episode: continue its branch, render stills, **look at key frames at full size** (props hidden behind characters is the most common bug), render the MP4, run `python3 tools/check_video.py output/<file>.mp4` until it PASSes, and score with the rubric (overall ≥ 8, no item < 7).
3. **Deliver MP4s to the owner as GitHub Release assets** (e.g. `gh release create ep02 output/ep02_*.mp4 --title "Episode 2" --notes "<upload title + description + scorecard>"`), so they can download and upload to YouTube. Also merge finished episode branches into `main`.
4. Report to the owner in plain language: what is done, the scorecards, and exactly what they need to do next.

## Limits
- Don't change YouTube account settings yourself. The owner's permission settings block it, so ask them to click.
- No emoji fonts in videos (use `icons.py` paper icons) and only original synthesized audio. Child-safety accuracy is mandatory: dangerous things are handled by the grown-up's hand.

## Plan after Episodes 2–5
Post one Short every weekday. From week 3, make a weekly ~10-minute compilation of the stories (16:9 for TV) to build the 4,000 watch hours. Review YouTube Studio numbers weekly (viewed vs swiped away, % viewed) and adjust. Goal: 1,000 subscribers plus 4,000 watch hours, then apply to the YouTube Partner Program.
