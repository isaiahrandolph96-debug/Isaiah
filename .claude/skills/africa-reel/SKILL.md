---
name: africa-reel
description: Make an Africa Blind Spot Instagram Reel from a news story to the approved standard (reference: reels/uganda-southsudan-power-60s). Use when asked to make, redo or improve a reel or video for Africa Blind Spot.
---

# Africa Blind Spot reel: production checklist

The reference reel is `reels/uganda-southsudan-power-60s/` (see its `storyboard.jpg`, `script.json` and `POST.md`). Match or beat it on every point below.

## 1. Research (no unsourced numbers)
- Web-search the story. Collect 4–6 hard facts: money, distance, people, dates, a comparison, and "why it matters".
- Cross-check every superlative and headline number against a second source. Note "as of" dates.
- Look for a relatable human-scale number for the hook (e.g. "only 1 in 20 has electricity").

## 2. Script: 9–10 scenes, 45–60 s
Arc: **hook stat → what happened → the money → the scale (map) → the key spec → who wins / why it matters → bigger picture → timeline → "why isn't this on your feed?" blind-spot line → "Send this to someone who hasn't heard."**
- `reels/<slug>/script.json`, one scene per beat: `head` (2 short lines, one gold), `say` (TTS: numbers written out), `show` (captions: digits), `bg_spec`.
- One idea per scene, about 8–16 spoken words. Add `"gap": 0.18`. The CTA scene gets `"hold": 1.2` and reuses `reels/ebola-blindspot-60s/vo/10.mp3`.

## 3. A story-driven animated background for every scene
Pick from, or add to, `reels/anim.py` and `reels/mapviz.py`:
- Maps: `{"map": {"from"/"to"/"view", "highlight", "route": {"grow", "flow", "places", "segments"}, "rings", "capitals", "dim"}}`. Add new places and routes to `mapviz.PLACES` and `ROUTE`.
- Scenes: `village`, `coins`, `pylons`, `whowins`, `build`, `feed`, `planes`. Overlays: `ranks` (with `ranks_y`), `chips`, `bars`, `count`.
- If no existing animation fits the story, **write a new one in `anim.py`** (drawn per frame, in the reel palette) instead of using a static background. Record it in `reels/README.md`.

## 4. Voice and sound
- ElevenLabs `creative_generate_speech`: voice `nJvj5shg2xu1GKGxqfkE`, `eleven_multilingual_v2`, `generations_count: 1`, at most 2 at a time. Save to `vo/NN.mp3`.
- Music: `python3 reels/music_bed.py reels/<slug>/audio/music.wav 55`. Whoosh: reuse `reels/uganda-southsudan-power-60s/audio/whoosh.mp3`.

## 5. Render (Instagram-safe)
```bash
cd reels && python3 render_reel.py <slug> --ig-safe \
  --music <slug>/audio/music.wav --music-vol 0.28 \
  --sfx uganda-southsudan-power-60s/audio/whoosh.mp3 --sfx-vol 0.45 \
  --endcard <brand reel>.mp4 --out <slug>/<slug>-IG-reel.mp4
```

## 6. Verify (required before delivering)
- Compute each scene's midpoint from the clip durations plus the gap and hold. Grab one frame per scene into `storyboard.jpg` (5×2 grid with labels) and **look at it**.
- Check: nothing covered by the Reels UI (top 140 px, right 120 px from y 1020 to 1760, bottom from y 1560), no text collisions, each animation readable, captions in sync.
- Check audio levels with volumedetect: voice around -21 dB mean while speaking, music clearly below it.

## 7. Deliver
- Make `cover.jpg` (the headline over the key visual) and write `POST.md`: an IG caption with a question, hashtags, a pinned sources comment, TikTok/Shorts text, Stories, an X thread and a LinkedIn post.
- Commit and push. Send the MP4, storyboard and cover to the user, and paste the ready-to-copy caption in chat.

## 8. Grow
Before finishing, name the improvement this reel added over the reference, and make sure it lives in the shared tools (`render_reel.py`, `anim.py`, `mapviz.py`), not in a one-off script.
