# vidIQ (Play Store) research, 8 Oct 2026: what to learn, what to skip

**Decision first.** Don't install it, don't subscribe, and don't connect the channel. It is far bigger and more
established than YouSEO, but its connection needs YouTube's "Manage your YouTube account" permission, and that access
is the owner's alone to give. One idea is worth copying, and it is free: **outliers**, meaning a channel's videos that
beat that channel's own usual views. The growth-analyst now finds them on the public Videos tab with one script (tested
below). The Instagram half doesn't apply to us (hard rule 4: no child-directed social accounts). Rating *for our
channel*: 4/10. It is a good tool for adult talking-head creators, and the one useful part costs nothing to copy.
See `docs/research-youseo-oct-2026.md` for the tag and search-word rules, which apply to vidIQ too.

## 1. What the app is (Play Store listing, read 8 Oct 2026)
- "vidIQ for YouTube & Instagram" by vidIQ, `com.vidiq.app`. 4.4 stars from 3.85 lakh reviews, 50 lakh+ downloads,
  rated 3+, updated 1 Oct 2026. Claims "30M+ creators".
- Tools: keyword research and a tag generator, an AI Coach with "daily video ideas" and trends, a thumbnail maker that
  compares against competitors, Instagram Reels analytics and hashtags, and Shorts clipping. Its web tools also have
  Outliers, competitor tracking and view prediction.
- Plans: Boost about $199 a year; Max about $39-49 a month. These are third-party figures that disagree with each other,
  and no rupee prices were found ([1of10](https://1of10.com/blog/vidiq-pricing/),
  [OutlierKit](https://outlierkit.com/resources/vidiq-pricing/)).
- **Data:** it *shares* email, user IDs, device IDs, app interactions and in-app search history with third parties
  for analytics. It collects name, photos, videos and files.
- **Channel access:** it asks for analytics reporting **and "Manage your YouTube account"** (view and manage videos,
  playlists and activity). vidIQ says it never changes a channel, but that is its own promise
  ([vidIQ help 3457281](https://support.vidiq.com/en/articles/3457281-what-youtube-permissions-does-vidiq-need-and-why-do-we-need-them)).
- **Reviews:** the "most helpful" ones are paid users who can't reach premium features or got no refund, and a beginner
  who found the score explanations behind the paywall (about 8.99 a month).

## 2. Features against YouTube's rules and our channel
| Feature | Use for us? | Why |
|---|---|---|
| Keywords, tag generator | No (already covered free) | Tags play a minimal role; we use YouTube's own search suggestions (YouSEO doc) |
| AI Coach, daily ideas, view prediction | No | Views-first topic picking broke Ep 11 (lesson 13); our topics are lesson first |
| Thumbnail maker and compare | No | Our thumbnails come from the episode's world, checked at 160 px; Made-for-Kids can't A/B test |
| Instagram Reels | No | Hard rule 4: no child-directed social accounts |
| Channel analytics | No | We read Studio ourselves (standing read-only permission); it would need write-level access |
| **Outliers** (videos beating their own channel's usual views) | **Yes, free** | It turns a market scan from "what is big" into "what beat its own normal": a fairer signal of what a topic or title adds |

## 3. The free outlier method, tested 8 Oct 2026
The score is a video's views divided by the channel's usual views. vidIQ doesn't publish its formula
([vidIQ help 9660010](https://support.vidiq.com/en/articles/9660010-outliers)). We use the **median** of the last
30 uploads, so one hit doesn't inflate the baseline. We also compare only videos at least 14 days old, because a
1-day-old video isn't comparable.
Built-in browser on a channel's `/videos` tab. Each card's text reads "… | 38K | 1d ago", so the snippet parses the
number before "ago":
```js
const toN=s=>{const m=s.match(/\|\s*([\d.,]+)\s*([KMB]?)\s*(views)?\s*\|\s*[^|]*ago/i);return m?parseFloat(m[1].replace(/,/g,''))*({K:1e3,M:1e6,B:1e9}[(m[2]||'').toUpperCase()]||1):null};
const rows=[...document.querySelectorAll('ytd-rich-item-renderer')].slice(0,30).map(e=>{const t=e.innerText.replace(/\n+/g,' | ');return{n:toN(t),t:t.slice(0,110)}}).filter(r=>r.n);
const s=rows.map(r=>r.n).sort((a,b)=>a-b),med=s[Math.floor(s.length/2)];
rows.sort((a,b)=>b.n-a.n).slice(0,6).map(r=>(r.n/med).toFixed(1)+'x '+r.t)
```
Test result on Oddbods: 30 uploads, median 88K views. The top outliers were only 1.8-2.2x: *"Who's Stealing While They
Sleep?"*, *"Rowdy!"*, *"Would You Like S'more?"*, *"Newt Tries to Help Fuse… It Gets WORSE!"*. Their titles are a
question or a mishap, plus an emoji, plus "Full Episode | Funny Cartoons for Kids". They are a mix of 7, 21 and 42
minutes long. Small spreads like this mean that, for a big channel, the format matters more than any one topic.

## 4. Agent changes made (MASTER_PROMPT v3.2; rollback tag `agents-v3.1-pre-vidiq`)
- **growth-analyst:** each market scan lists every benchmark channel's outliers (≥1.5x the median of its last 30
  uploads, only videos ≥14 days old) with their title pattern, length and topic. Once we have ≥10 uploads, it runs
  the same ratio on our own videos.
- **Lesson 14** now names vidIQ too: no third-party tool gets channel access, and their scores are not evidence.
