# YouSEO (Play Store) research, 8 Oct 2026: what to learn, what to skip

**Decision first.** Don't install it, don't subscribe, and never give it channel access. Two of its ideas are worth
copying, and both are free: (1) choose title words from YouTube's own search suggestions, and (2) put name misspellings
in a small Tags field. Both are now in the packaging and growth-analyst agent files (MASTER_PROMPT v3.1). Rating of
the app *for our channel*: 3/10. It is built for adult creators who talk on camera and want search traffic, and we are
neither of those.

## 1. What the app is (Play Store listing, read 8 Oct 2026)
- "YouSEO: SEO Tools, Tags & AI" by Crinet Technologies LLP (Ahmedabad, founded 2024), package
  `youseo.organicgrowth.channelseotool`. 4.8 stars from 68.1K reviews, 10 lakh+ downloads, rated 3+, updated 1 Oct
  2026, #7 top-grossing in Video Players & Editors. Annual plan ₹1,499 (taken from user reviews).
- Tools: keyword research ("search volume, competition"), tag generator, AI titles ("can double your CTR"), thumbnail
  maker and analyser, a pre-publish "SEO score", channel analytics, AI script writer and teleprompter, trending ideas,
  Shorts hashtags, competitor tags, best time to post, community posts, an "AI coach".
- Data it collects: name, email, purchase history, device IDs, diagnostics. It says it shares nothing with third parties.
  The analytics tools need the channel's account linked.
- **Trust signals don't fit together.** Most reviews give 5 stars, yet the three "most helpful" reviews are ₹1,499
  refund complaints. One of them says *"I'm giving this App a 5 star review for keeping this at the top"* and then
  calls the app useless. The developer's reply is the same each time ("write to support@"). The 160K-device figure
  comes from the developer's own post. Treat the star rating as weak evidence.

## 2. Each feature against YouTube's own rules and our channel
| Feature | What YouTube says | Use for us? |
|---|---|---|
| Tag generator | "Tags play a minimal role in your video's discovery"; they help mainly when a name is often misspelled; title, thumbnail and description matter more ([Help 146402](https://support.google.com/youtube/answer/146402)). Search ranks by relevance (title, tags, description, content), engagement (watch time) and quality ([Help 16090438](https://support.google.com/youtube/answer/16090438)) | **Small yes, free:** ≤10 tags, mostly name spellings (see 3) |
| Keyword volume | Its "volumes" are the app's own estimates; YouTube's own suggestions are free and real ([live test in 3](#3-checked-free-replacements)) | **No app;** use YouTube's search suggestions |
| AI titles "double CTR" | Clickbait is against policy ([spam policy 2801973](https://support.google.com/youtube/answer/2801973)); our titles must be moment-first and honest | **No** |
| Hashtag optimiser | Over 60 hashtags means all of them are ignored; unrelated or excessive hashtags can be removed; "ordinary descriptive tags or repetitive sentences" in the description are prohibited ([Help 6390658](https://support.google.com/youtube/answer/6390658)) | Keep our 3-5 |
| Thumbnail A/B | YouTube's own Test & compare: "You cannot use this feature on videos that are made for kids" ([Help 13861714](https://support.google.com/youtube/answer/13861714)) | **No:** keep our 160 px check |
| SEO score | A score from a third-party tool proves nothing (our evidence rule) | Our own pre-publish checklist (packaging rules) |
| Trending ideas | Topics picked for views broke Ep 11 (lesson 13: lesson first) | Demand evidence only, after the lesson is chosen |
| Script writer, teleprompter | We are wordless | No |
| Channel analytics, AI coach | We read Studio ourselves (standing read-only permission) | **No:** it would need channel access |

**Why search matters less for us:** children aged 2-6 don't type. Made-for-Kids videos "are more likely to be
recommended alongside other kids' videos" ([Help 9528076](https://support.google.com/youtube/answer/9528076)). In YouTube
Kids, Preschool search only returns content for ages 4 and under, and parents can turn search off
([YT Kids 6172308](https://support.google.com/youtubekids/answer/6172308)). Search is the *parent's* doorway, so title
words should be the words parents type. Watch time and retention still decide most of our reach.

## 3. Checked free replacements
1. **Search suggestions** (what people type, in YouTube's own order), from a script or the built-in browser:
   `curl -s "https://suggestqueries-clients6.youtube.com/complete/search?client=youtube&ds=yt&hl=en&gl=in&q=<words>"`.
   Test results, 8 Oct: "colour sorting for" → *colour sorting for toddlers*, *colour sorting activity for toddlers*;
   "tidy up" → *tidy up song*; "halloween for toddlers" → *…songs*, *…videos*. "snip and crinkle" → *sound*, *asmr*,
   *windows*: our name collides with ASMR searches, so the name variants belong in tags.
2. **Competitors' tags:** a public watch page carries them in `"keywords":[…]` (`ytInitialPlayerResponse.videoDetails.keywords`).
   Test result, 8 Oct, an Oddbods full-episode video: *cartoons no language*, *cartoon for kids*, *funny cartoon* and the
   misspelling *odbods*. A leading wordless channel tags its own misspelling and "no language".

## 4. Agent changes made (MASTER_PROMPT v3.1, tag `agents-v3-pre-youseo` for rollback)
- **packaging:** title words from the growth-analyst's suggestion list, with the parent phrase in the first ~40
  characters; a Tags field of ≤10 (name spellings, the characters, 2-3 topic words, "cartoon no words"); no tags or
  keyword lists in the description; no A/B thumbnail tests (not allowed for Made for Kids); no third-party SEO apps or scores.
- **growth-analyst:** each proposed topic carries its top 5 search suggestions (endpoint above); competitors' tags are
  read from the watch page; search words rank below watch time and retention; no paid SEO tools and no channel access.
