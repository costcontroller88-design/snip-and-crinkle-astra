# What is missing: agents and channel (Lead, 16 Oct 2026)

Day 11 since the first upload. Search not cut short. Not opened: YouTube's own YouTube Kids help page (criteria not
found), the vidIQ and AIR pages (search summaries only, not used as evidence). Access labels: R = read directly,
Y = YouTube page read in the browser, P = this repo or Studio, S = search summary only, I = my inference.

## Decision
The plan is sound; execution is not keeping up with it. For the next two weeks: ship long-form, raise the number
of different Shorts, and turn the 9 Oct reliability findings into scripts. Freeze rule-writing until then.

## Channel gaps (ranked)
1. **No long-form video yet** (P). Watch hours come only from long-form; new applicants need 8,000 h from 1 Feb 2027.
   ROADMAP target by 4 Jan: about 10 mini-episodes. Done: 0 (Ep 11 parked, pilot episode due Wed 21 Oct).
2. **Too few tries for a hit** (Y, one channel only). One YouTube search ("kids cartoon good habits shorts", past
   week) returned 20 new Shorts from about 18 channels (17 views to 1M). BRELUFI (93 videos, 130 subs): most Shorts
   3-104 views, rare ones 20-35K. Our 2-40 views after 8 Shorts is normal, not a failure signal.
3. **Same shape every time** (P): all 8 Shorts are 0:19, one title formula and one closing description paragraph.
   Non-AI stop-motion and animation channels were demonetized as "inauthentic" in 2026; some reversed on appeal
   (R: Riddance, 6 May 2026). The 9 Oct scan asked for a sameness check and a provenance pack; neither exists.
4. **Polluted data** (P): 5 viewers in 28 days, most views are the owner's replays.
5. **YouTube Kids app** (R: Fortune, 1 Apr 2026, YouTube spokesperson): AI content in the app is limited to
   "a small set of high-quality channels". Our art is code-drawn, not generative AI; how YouTube classifies it is
   unknown (I).
6. **Translated titles and descriptions** (I): the videos are wordless, so only the text is language-bound.
   Not tested; low cost, low priority.

## Agent gaps (ranked)
1. **Process outruns output** (P): 59 logged mistakes, MASTER_PROMPT v4.0, 15 check scripts, no commit since 9 Oct,
   0 long-form videos. Blind AI scores have not been checked against real viewers (A1), so extra review rounds buy
   unproven quality. Missing: a weekly output target the Lead is held to, and one review round for Shorts.
2. **Checks still depend on memory** (P): no `.claude/settings.json`, no SubagentStop hook running `return_check.py`,
   no regression cases from the mistake log. All recommended 9 Oct (`research-agent-reliability-oct-2026.md`).
3. **Nothing runs on a schedule** (P): the 14 Oct Studio checkpoint was missed (done 16 Oct). No reach-drop alarm.
4. **No sameness or provenance tool** (P): see channel gap 3.

## Next work package (proposed, owner approves)
1. Ship the pilot episode on 21 Oct; Episode 12 as long-form next.
2. Build `tools/sameness_check.py` (length, title shape, description overlap across the last 10 uploads) and the
   SubagentStop hook. Both cost no model tokens when they run.
3. A scheduled read-only Studio check every second Friday (next: 30 Oct).
4. Owner: upload Ep 9 v3 and Ep 5 v2 Shorts; don't replay our Shorts while signed in to the channel.

Not claimed: that more Shorts will bring a hit (one channel, one search), or that the code-drawn style is safe from
an "inauthentic" flag. This is an in-project reading, not an outside review.

Sources: [Riddance, 6 May 2026](https://substack.riddance.ai/p/youtubes-ai-moderation-is-backfiring);
[Fortune, 1 Apr 2026](https://fortune.com/2026/04/01/ai-slop-200-organizations-letter-youtube-google/);
YouTube search and youtube.com/@BRELUFI/shorts (read 16 Oct 2026); Studio (read-only, 16 Oct 2026).
