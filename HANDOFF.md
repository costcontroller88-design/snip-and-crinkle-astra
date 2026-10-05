# Handoff: read this first (written 2026-10-05)

You are continuing work for the owner of the YouTube channel **Snip & Crinkle (@SnipAndCrinkle)**, a wordless kids' Shorts channel made entirely with this code. The owner is not technical and relies on you to make decisions and do the work. They like a thorough analysis from all angles followed by a firm recommendation, and **harsh, honest ratings** (score 1–10 and say what is weak). They are in India.

## Where things stand
- **Channel setup is done:** name, handle, banner and profile picture (`tools/brand.py`), description, keywords, **made for kids = Yes**, country = India, and upload defaults (Education, language "Not applicable", footer description). Optional: default tags are still empty. The owner still has to turn on 2-Step Verification.
- **Episode 1 is final:** `episodes/ep01_v3_can_snip_wait.py` ("Can Snip Wait?"), scored 8/10, and passes `tools/check_video.py`. Render it with `python3 episodes/ep01_v3_can_snip_wait.py`. MP4s are git-ignored.
  - Upload title: `Can Snip Wait? ⏳☕ | Snip & Crinkle #shorts`
  - Upload description (goes above the default footer): "Snip wants the yummy drink… but it's HOT! ✋ or ⏳? What should Snip do? Wait with Snip & Crinkle and count 1, 2, 3 until it's cool! ☕✅"
- **Episodes 2–5 are finished** (merged into `main`), each scored 8/10 overall with no item below 7, and each passes `tools/check_video.py`. Scorecards, remaining weaknesses and upload text are in `reviews/epNN.md`; key-frame sheets in `reviews/epNN_keys.png`.
  - Ep 2 `episodes/ep02_wash_before_you_munch.py` (bathroom, friendly germs, wet-soap-scrub-rinse-dry)
  - Ep 3 `episodes/ep03_the_last_cookie.py` (evening kitchen, tug-of-war tumble, break in half and share)
  - Ep 4 `episodes/ep04_whose_toy_is_this.py` (park, teddy ears pop up, give the toy back to the duckling)
  - Ep 5 `episodes/ep05_hold_paws_to_cross.py` (street, wind-up legs skid, wait for green, look both ways, hold a grown-up's hand)
- **Delivered:** the MP4s for Episodes 1–5 are attached to GitHub Releases `ep01` … `ep05` (each release note has the upload title, description and scorecard).
- **Tips learned:** zooms or fast pans over fine stripes (zebra crossing, gingham cloth) trip the "harsh jump" check; keep zooms slow (≤ ~0.35 zoom/s) or pan sideways instead. Review single frames with `render_frame(t)` to review before a full render (~5 min per episode).

## How to work
1. `./setup_cloud.sh` (ffmpeg, Pillow, numpy, Fredoka font).
2. For each episode: continue its branch, render stills, **look at key frames at full size** (props hidden behind characters is the most common bug), render the MP4, run `python3 tools/check_video.py output/<file>.mp4` until it PASSes, and score with the rubric (overall ≥ 8, no item < 7).
3. **Deliver MP4s to the owner as GitHub Release assets** (`gh release` uses GraphQL, which is blocked in cloud sessions: create the release with `gh api repos/<owner>/<repo>/releases -f tag_name=epNN ...` and upload the MP4 to `https://uploads.github.com/.../releases/<id>/assets?name=...`), so they can download and upload to YouTube. Also merge finished episode branches into `main`.
4. Report to the owner in plain language: what is done, the scorecards, and exactly what they need to do next.

## Limits
- Don't change YouTube account settings yourself. The owner's permission settings block it, so ask them to click.
- No emoji fonts in videos (use `icons.py` paper icons) and only original synthesized audio. Child-safety accuracy is mandatory: dangerous things are handled by the grown-up's hand.

## Next (after Episodes 1–5)
Post one Short every weekday. From week 3, make a weekly ~10-minute compilation of the stories (16:9 for TV) to build the 4,000 watch hours. Review YouTube Studio numbers weekly (viewed vs swiped away, % viewed) and adjust. Goal: 1,000 subscribers plus 4,000 watch hours, then apply to the YouTube Partner Program.
