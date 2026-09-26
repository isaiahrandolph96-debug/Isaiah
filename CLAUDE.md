# Africa Blind Spot: project guide

Africa news and stories for social media ("The stories others miss"). This repo holds daily briefings (`briefings/`), reels (`reels/`) and the growth playbook (`GROWTH-PLAYBOOK.md`).

## The standard
`reels/uganda-southsudan-power-60s/` is the **reference reel**. The owner approved it as the baseline: every new reel must match or exceed it, never fall below it. See `reels/uganda-southsudan-power-60s/storyboard.jpg`. To make a reel, follow `.claude/skills/africa-reel/SKILL.md` (`/africa-reel`).

Reusable formats (data race, roundup, quiz, myth vs reality, timeline, then vs now, kinetic quote, whiteboard, carousel, audiogram, plus the explainer and map story) live in `reels/formats.py`; copy a scene from `reels/format-templates/script.json` to use one in any story.

Daily output: five narrations (CapCut voiceover scripts) from the day's top five stories, following `.claude/skills/daily-narrations/SKILL.md`, saved in `narrations/YYYY-MM-DD/`. The tone matches the severity of each story, and every narration must be clear to a first-time reader.

Non-negotiables for every reel:
1. **Facts first.** Every number has a source listed in `script.json` → `sources` and in the post's pinned comment. Check superlatives ("largest", "first") against two sources. State "as of <date>".
2. **Hook in frame 1.** No intro bumper before the hook. Lead with the stake or the surprising number.
3. **Every scene has a story-driven animated background** that shows what the narrator is saying (`reels/anim.py`, `reels/mapviz.py`). No static or generic backgrounds.
4. **House style:** gold "AFRICA BLIND SPOT" header, two-line headline (white plus gold), word-by-word gold captions, gold progress bar, crossfades, brand end card.
5. **Sound:** voice normalized to -16 LUFS, a music bed ducked under it, a whoosh on scene changes.
6. **Instagram-safe export** (`--ig-safe`): text clear of the Reels UI, H.264 High, CRF 16, AAC 48 kHz.
7. **Verify before delivering:** render a storyboard of one frame per scene at the exact scene midpoints, and look at it. Check the safe zones, legibility, overlaps and that each animation reads.
8. **Ship the full pack:** MP4, `cover.jpg`, `storyboard.jpg` and `POST.md` (IG caption, pinned sources comment, TikTok/Shorts, Stories, X thread, LinkedIn). Commit and push.

"Only grow from here": each new reel should add at least one improvement (a new animation type, better pacing, a new data graphic) and fold it back into the shared tools, so every future reel benefits.

## Environment notes
- The Python tools need `pip install pillow numpy imageio-ffmpeg "geopandas<1.0"`. ffmpeg comes from `imageio_ffmpeg.get_ffmpeg_exe()`.
- The brand end card is taken from the owner's reference reels (the last ~2.2 s). Ask for one if it isn't in the session.
- ElevenLabs is on the free plan: voice clips allow at most 2 concurrent requests, images have a daily cap, and credits can run out. The music bed is made locally with `reels/music_bed.py`. Media downloads only work from storage.googleapis.com; Canva, Unsplash and Wikipedia downloads are blocked.
- The voice is "Yusuf Hakeem Kiser" (`nJvj5shg2xu1GKGxqfkE`, `eleven_multilingual_v2`). Reuse identical lines, such as the CTA clip, instead of regenerating them.
