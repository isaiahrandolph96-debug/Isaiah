# Africa Blind Spot: growth playbook

## 1. What your Tigray reels already do well
- **A strong brand promise:** "the stories others miss" is on every frame and in the end card.
- **Consistent look:** gold and white type on dark painterly art. It's recognisable in a fast scroll.
- **Word-by-word captions:** most Reels are watched on mute, so these carry the story.
- **A share call to action:** "Send this to someone who hasn't heard" asks for shares, which spread a Reel further than likes do.
- **A human detail:** "In Mekelle, a garlic seller told AP…" makes a distant conflict feel personal.

## 2. Fixes that should lift watch time
| Seen in your reels | Change |
|---|---|
| `tigray-escalation` opens with ~2 s of "AFRICA THIS WEEK" before the story | Open on the hook in frame 1 (your `threads-final-v2` edit already does this). Move the bumper after the hook, or drop it. |
| One headline and background held for ~9 s (e.g. "3 AIRPORTS SEIZED") | Change something every 2–4 s: a new crop, zoom, stat or map pin. |
| The hook states the topic ("TIGRAY / WAR IS BACK") | Lead with stakes or a surprise: "3 AIRPORTS SEIZED IN 48 HOURS" or "THE WAR NOBODY IS COVERING". |
| Numbers only as text | Animate the key number (bars, chips, counters). The Ebola reel shows how. |
| No question for viewers | Ask one specific question in the caption and pin a reply. Comments drive distribution. |
| Black end card lasts ~2 s | Keep it under 1.5 s, or finish on the CTA so the Reel loops cleanly. |

## 3. Content system (sustainable for one person)
| Day | Format | Series |
|---|---|---|
| Mon | Reel, 45–60 s | **Blind Spot of the Week**: the biggest under-covered story |
| Tue | Carousel, 6–8 slides | **Numbers Don't Lie**: one striking statistic, explained |
| Wed | Reel, 30 s | **Africa Rising**: business, tech, sport or culture wins |
| Thu | Carousel | **Myth vs Reality**: correct a stereotype with sources |
| Fri | Reel, 60 s | **Africa This Week**: 5 stories in 60 seconds |
| Daily | Stories | poll, quiz, "what should we cover next?" |

Keep the ratio at about 2 hopeful or explanatory posts for every hard-news post, so the page doesn't feel like it's all crisis.

## 4. Distribution
- **Post natively on each platform:** Instagram Reels, TikTok, YouTube Shorts and Facebook, plus an X/Threads thread and a LinkedIn post for the business stories. See each reel's `POST.md`.
- **Timing:** 12:00–14:00 WAT (European lunch, US East Coast morning). Test 18:00–20:00 WAT.
- **Collaborations:** use Instagram's Collab feature with diaspora pages, African journalists and country-focused accounts. Their audience sees the post in their own feed.
- **Engage right after posting:** reply to every comment in the first hour, and pin the sources comment.
- **Hashtags:** 3 brand/topic tags plus 5 country/city tags plus 2 broad tags. Country and city tags reach diaspora audiences.
- **WhatsApp Channel:** a daily one-liner linking to the Reel. It's a strong channel for African audiences.

## 5. Credibility (your competitive edge)
- Put a source line on every carousel and a pinned sources comment on every Reel.
- Use **"as of [date]"** on every figure. Numbers change fast.
- Check superlatives. This briefing first called the Ebola outbreak "the largest ever". It's the **second-largest**. Being the page that gets it right builds trust over time.

## 6. What to measure each week
| Metric | Why | Target to aim for |
|---|---|---|
| 3-second hold rate | shows whether the hook works | > 60% |
| Average watch time / % watched | retention drives reach | > 50% on 60 s Reels |
| Shares per 1,000 views | the "blind spot" promise is working | rising week over week |
| Saves | educational value | rising |
| Follows per Reel | converting viewers into followers | log per post |

Metricool is connected, so I can pull these each week and tell you which series and hooks are winning.

## 7. Production pipeline (already built)
`briefings/` (daily research) → pick the most under-covered story → `reels/<slug>/script.json` → ElevenLabs backgrounds and voice → `render_reel.py` → MP4, cover and `POST.md`.
Can be automated as a daily scheduled task: briefing plus one Reel draft for you to review each morning.
