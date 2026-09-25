# Africa Blind Spot: reels

Each folder is one reel: `script.json` (scenes, headlines, narration, captions, background treatment), `bg/` (backgrounds), `vo/` (one voice clip per scene), the rendered MP4, a cover and a `POST.md` with captions and cross-platform copy.

## House style (from the Tigray reference reels)
| Element | Spec |
|---|---|
| Format | 1080×1920, 30 fps, ~60 s |
| Header | "AFRICA BLIND SPOT", gold `#D4AA34`, letter-spaced, short gold underline, top centre |
| Headline | 2 lines, heavy sans, uppercase, centre of frame; one line white, the key word/line gold; pops in on each scene |
| Captions | 2-line pages near the bottom; each word turns gold as it is spoken |
| Backgrounds | dark, painterly/cinematic, heavily graded and vignetted, slow push-in |
| Pace | new scene every 4–7 s; one idea per scene |
| Ending | "SEND THIS TO / SOMEONE WHO HASN'T HEARD", then the black end card "AFRICA BLIND SPOT · FOLLOW FOR THE STORIES OTHERS MISS" |

## Render
```bash
pip install pillow numpy imageio-ffmpeg
python3 render_reel.py ebola-blindspot-60s --endcard <a reference reel with the brand end card>.mp4
```
- Voice clips: ElevenLabs, voice "Yusuf Hakeem Kiser" (`nJvj5shg2xu1GKGxqfkE`), `eleven_multilingual_v2`. Write numbers out in `say` (TTS) and as digits in `show` (captions).
- Backgrounds: gpt-image-2 at 9:16, prompt pattern "Vertical cinematic digital painting, dark moody palette … calm dark area across the middle … No text."
- Data scenes: `"special": "bars" | "chips" | "ranks"` render animated stat graphics.

## Map scenes
`mapviz.py` draws animated maps with real country borders (Natural Earth via `pip install "geopandas<1.0"`). In `bg_spec`, use `{"map": {"view" | "from"/"to": "africa|region|east", "highlight": [...], "route": {"grow": [start, end], "flow": true, "places": [...]}, "dim": 0.5}}`. Routes and places live in `mapviz.PLACES` / `ROUTE`.

## Sound
- `music_bed.py out.wav 50` synthesizes a royalty-free underscore (100 BPM, Am–F–C–G, builds in the last third).
- `render_reel.py ... --music audio/music.wav --music-vol 0.28 --sfx audio/whoosh.mp3 --sfx-vol 0.45`: the voice is loudness-normalized to -16 LUFS, the music is ducked under it, and the whoosh plays on every scene change.
- Other polish: crossfades between scenes, a gold progress bar, caption timing snapped to real pauses in the voice, `"count"` for count-up numbers, `"gap"` to tighten pacing.
