# YouTube reliability scan for agent-run kids channels, 9 Oct 2026

Evidence labels: **[official]** = YouTube Help or blog page read 9 Oct 2026. **[secondary]** = news or analysis. **[weak]** = vendor blog or creator anecdote; use as a prompt to check, never as proof. Compared with `research-policy-safety-oct-2026.md` and `research-synthesis-oct-2026.md` (8 Oct); only new or changed items are listed.

## Decision

No new rule blocks us. Five changes, ranked:

1. **"Unsatisfying or off-putting" is now written on the official inauthentic-content page.** The 8 Oct scan found no 2026 rewrite; today's read shows the page names emotionally manipulative formulas as ineligible, next to generic and template content. Our safety gate must check distress and manipulation, not only sameness.
2. **Enforcement is channel-wide, and detection works on whole groups of channels.** One bad pattern can cost every video. A Google paper (platform unnamed) describes cluster detection. A human-made channel (Kurzgesagt, Aug 2026) was wrongly hit: reach fell with no notice. We need a sameness check before upload and a reach-drop alarm after.
3. **YouTube now labels AI automatically** (May 2026), using its own detection and C2PA metadata. Animation stays exempt from disclosure, but a wrong auto-label can be permanent. Check our files carry no AI-tool provenance metadata.
4. **YouTube Kids AI labels: pledged, still no date.** YouTube says AI in YouTube Kids is limited to "a small set of high-quality channels". Five AI kids channels lost YPP after a New York Times test. Do not claim in text anything about the making that we cannot back.
5. **Keep a provenance pack per episode** for any appeal (creator advice, weak evidence, but free for us because the repo already holds the records).

## Findings and script checks

| # | Finding | Which agent | Exact change (≤25 words) | Source link |
|---|---|---|---|---|
| 1 | Official page lists "unsatisfying or off-putting" content: emotionally manipulative formulas, disturbing, nonsensical, shocking. [official] | safety-checker | Add gate-1 and gate-3 line: scenes of distress or fear listed with seconds; fail if one lasts over 5 s without a visible fix. | https://support.google.com/youtube/answer/1311392 |
| 2 | Policy applies to the channel as a whole; one pattern can remove monetization everywhere. [official] | safety-checker | Script `sameness_check`: compare this episode's engine, setting, solver and ending beat with the last 5; fail if fewer than 2 differ. | https://support.google.com/youtube/answer/1311392 |
| 3 | Google paper describes catching spam by cluster (shared templates and infrastructure), ~50,000 clusters in 6 months; YouTube attribution unconfirmed. [secondary] | growth-analyst | Keep upload cadence at or below current plan; never publish near-identical Shorts in one batch. Log uploads per week in analytics-log. | https://www.seo-day.de/news/article/google-research-reveals-pattern-level-ai-video-spam?lang=en |
| 4 | Kurzgesagt's human-made video was wrongly down-ranked (Jul-Aug 2026); no notice, YouTube staff confirmed a problem after contact. [secondary] | growth-analyst | Each 2-week read: flag any video with impressions under 50% of the trailing 5-video median; report to Lead, never act in Studio. | https://www.dexerto.com/youtube/youtubes-ai-slop-detector-incorrectly-targets-kurzgesagt-as-other-creators-fear-same-fate-3395930/ |
| 5 | YouTube auto-labels content from its own AI tools, files with C2PA metadata, or systems that detect AI. Unrealistic animation needs no disclosure; some labels cannot be changed. [official] | packaging | Script `provenance_scan`: search final mp4 and assets for C2PA/JUMBF markers; fail if found. Upload sheet states "AI use: No (animation)". | https://support.google.com/youtube/answer/14328491 |
| 6 | May 2026 update moves labels under the player for realistic content; animated content keeps the label in the expanded description. [secondary] | packaging | After each upload, owner checks the public page for any "altered or synthetic" label; owner reports it to Lead the same day. | https://minimatters.com/youtube-ai-content-labeling-update-in-may-2026/ |
| 7 | YouTube pledged clearer AI labels for kids; no date. Fairplay says animated kids content will be under-labelled. YouTube limits AI in YouTube Kids to a small set of channels. [secondary] | growth-analyst | Monthly: search for "YouTube Kids AI label" launch; if dated, tell Lead and safety-checker within the same session. | https://fairplayforkids.org/statement-on-youtubes-pledge-to-clearly-label-ai-videos/ |
| 8 | After a New York Times test, five AI kids channels were removed from YPP (reported); the channels showed glitches, bad lip-sync, keyword-string titles. [secondary] | packaging | Title check script: reject keyword strings, repeated words, and more than 2 hashtags; title must name the one lesson shown. | https://mezha.ua/en/news/youtube-shows-kids-ai-videos-308931/ |
| 9 | Official page also bars AI personas giving health, legal or finance advice. [official] | safety-checker | Add line to gate 3: no adult-advice framing in text; potty and bedtime videos make no health claims, only show routine. | https://support.google.com/youtube/answer/1311392 |
| 10 | Creators who appeal advise a video or document showing the production process; do not delete videos first. [weak] | packaging | Script `provenance_pack`: per episode write story card, gate reports, render log and date into one folder. Never delete uploaded videos. | https://www.subsub.io/blog/youtube-channel-reviews-unsatisfying-off-putting-content |
| 11 | Partner Program terms: new rules and Shorts payout floor start 1 Feb 2027; existing partners must accept terms in Studio before then. [official] | growth-analyst | Not applicable until we are in YPP. When accepted into YPP, add "accept new terms" to the owner checklist. | https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/ |

## Practitioner evidence (all weak)

- I found **no Reddit threads or creator-video transcripts** I could open; the searches returned vendor blogs, news and freelancer listings. Treat everything below as anecdote.
- Channels reported removed or demonetised share: many uploads a day, identical templates, text-to-speech, no editing layer. Vendor figures (for example "18,000 channels", "$9.8M a year") appear in one blog each and are not confirmed.
- Reported survivors: a point of view, one upload a day or fewer, real variety between videos, AI as a tool not the whole process.
- A one-person Python project makes stickman animation with no AI services; no monetisation result is reported, so it tells us nothing about approval.
- Appeal deadline: one blog says 7 days; the official page says **21 days** after a YPP suspension, with re-application possible after 90 days [official: https://support.google.com/youtube/answer/1727191]. Follow the date shown in Studio.

## Unchanged since last scan

- Entry bar from 1 Feb 2027 (8,000 watch hours or 20M Shorts views) and the 10M Shorts payout floor: now also confirmed on the official blog post of 10 Aug 2026 (it was a news report before).
- Inauthentic-content rename (15 Jul 2025) and the six low-quality kids principles: same wording.
- AI disclosure not needed for clearly unrealistic animation: re-read today on the official page, same answer.
- Made for Kids settings and COPPA: no change found; keep MFK set correctly.
- No official page found for YouTube Kids AI labels, kids "quality principles" beyond the six, or a human-review step in YPP checks.
