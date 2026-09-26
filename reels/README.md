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

## Story animations
`anim.py` draws an animated background for each beat of the story, selected with `bg_spec: {"anim": name}` (optionally on top of a `"map"`):
`village` (night huts, one lit window, a power line sweeps in) · `coins` (funding stacks up) · `pylons` (towers to the horizon, energy pulses on the cables) · `whowins` (dam powers a city skyline) · `build` (a pylon rises with welding sparks) · `feed` (doom-scroll; the Africa story slides past) · `planes` (share: paper planes fly out). Maps also support `"rings"` (pulses from a place), and route ticks are now small pylons.

## Stop motion (story reels with characters)
`stopmo.py` makes cut-out paper stop-motion scenes: 12 poses per second, per-pose boil, cut edges, drop shadows, paper grain, and sepia for flashbacks. Scenes are chosen with `bg_spec: {"anim": "sm_<name>"}`: `sm_rooftop_dawn`, `sm_protest`, `sm_apartment_morning`, `sm_polling`, `sm_tv_results`, `sm_sugar`, `sm_tv_leader`, `sm_rooftop_night`. Puppets: `yasmine()` and `haj()`, with poses and arm angles.
Dialogue scenes use `"lines": [{"who": "narrator|yasmine|haj", "file": "sNN_k.mp3", "say", "show", "tempo"}]`:
- The renderer stitches the clips and drives mouth flaps from the real audio loudness.
- Speaker names show above the captions.
- A missing clip becomes a timed silent placeholder, so you can preview before every voice exists.
- Script-level `"tempo"` speeds all lines; `"note"` shows a disclaimer for the first seconds; `"sub"` adds a caveat under the headline.

## Format library (reuse any format in any story)
`formats.py` holds 10 data-driven video formats. The animated explainer and the map story come from `anim.py` and `mapviz.py`, which makes 12 in total. To use one, set a scene's `bg_spec` to `{"format": "<name>", ...data}`. `render_reel.py` then draws it under the usual header, headline (placed at the top, `head_y` 420), captions and progress bar.
- **Timing:** each format is choreographed on a 6.5 s clock and stretched to the scene's real length.
- **Layout:** content stays between y 540 and 1290, so it never collides with the headline or the Instagram-safe captions.
- **Templates:** `format-templates/script.json` has one ready-to-copy scene per format. Its preview render is `format-templates/format-templates-preview.mp4`, with a `storyboard.jpg`.
- **Sampler:** `format_samples.py` renders the 12-format sampler from the same templates.

| Format | Use it for | `bg_spec` |
|---|---|---|
| Animated explainer | infrastructure, economy, "how big is it" | `{"anim": "pylons"}` + scene `"special": "chips"` (any `anim.py` scene) |
| Map story | borders, routes, where it happened | `{"map": {...}}` (see Map scenes) |
| `race` | elections, rankings, budgets over time | `{"format": "race", "from_label": "2021", "to_label": "2026", "items": [["PAM", 87, 97], ["RNI", 102, 66, [70,110,170]]], "suffix": "", "decimals": 0}`: `[name, from, to, colour?]`; bars re-rank as they grow |
| `roundup` | weekly news roundups | `{"format": "roundup", "items": [{"title": "DR CONGO", "body": "Ebola: 7,773 cases…", "place": "Bunia"}]}`: one card per item, the map centres on each `place` |
| `quiz` | engagement ("guess the country / number") | `{"format": "quiz", "clues": ["…", "…", "…"], "answer": "MOROCCO", "place": "Rabat", "prompt": "Did you get it? Comment below"}` |
| `myth` | myth-busting, misinformation | `{"format": "myth", "myth": "Africa is a country", "reality": "54 countries", "detail": "1.4+ billion people"}` |
| `timeline` | background, "how we got here" | `{"format": "timeline", "events": [["SEPT 2021", "RNI wins the election"], …]}` (any number; they scroll) |
| `thenvsnow` | one strong before/after number | `{"format": "thenvsnow", "then": {"label": "2021", "value": "50%", "filled": 5}, "now": {"label": "2026", "value": "38%", "filled": 4}}`: `filled` (0–10) draws "N in 10" people icons, or use `"note": "text"` |
| `kinetic` | speeches, statements, quotes | `{"format": "kinetic", "quote": "…", "gold": ["SAHEL"], "by": "Name, role", "where": "Venue · date"}` |
| `whiteboard` | how a system works (coalitions, loans, supply chains) | `{"format": "whiteboard", "items": [{"type": "hemicycle", "at": [540,1170], "r": 330, "split": true}, {"type": "text", "text": "198 = MAJORITY", "at": [540,700], "color": "red"}, {"type": "arrow", "from": [x,y], "to": [x,y]}, {"type": "circle", "at": [x,y], "r": 80}, {"type": "line", …}]}`: drawn in order by a marker; colours `ink/red/blue/green/gold`; optional `start`/`len` per item; keep inside x 90–990, y 570–1260 |
| `carousel` | 2–5 key facts; also works as a static carousel post | `{"format": "carousel", "tag": "EBOLA IN DR CONGO", "source": "Sources: WHO · CDC · UN", "slides": [["7,773", "confirmed cases"], …]}` |
| `audiogram` | interview or podcast clips, strong quotes | `{"format": "audiogram", "badge": "ABS", "badge_sub": "PODCAST", "map": {mapviz spec, optional}, "audio": "vo/x.mp3" (optional)}`: without `audio`, the waveform follows the scene's own narration |

Maps (roundup, quiz, any `"map"`) accept `"view"` as a view name (`africa`, `region`, `east`), a `PLACES` name (centred on it) or `[lon, lat, px_per_degree, screen_y]`. Add new places to `mapviz.PLACES`.
To add a format, write `def name(spec, u, t, ctx)` in `formats.py` (u = design-clock seconds, 0 to 6.5), register it in `FORMATS`, add a template scene, and re-render the templates preview to check it.

## Text-led reels (no voice)
When no voice clips exist (or credits are out), write scenes with `"lines"` and leave `vo/` empty. Captions then run as read-along text at the script's `"read_wps"` (words per second; 3.0 to 3.1 suits short punchy lines), over the music bed. Drop the MP3s into `vo/` later and re-render to add the voice. Example: `ethiopia-tigray-30s/`.

## Breaking-news map tools (added for ethiopia-tigray-30s)
- `"pins"`: events that drop in one by one with a red shock ring and a label: `[{"at": "Mekelle", "start": 0.48, "label": "MEKELLE", "side": "l"}]`.
- `"rings"` accepts a list, each with an optional `"color"` (e.g. red `[225,70,50]` for conflict).
- `"tags"`: big faint names for areas with no country polygon: `[{"at": [lon, lat], "text": "TIGRAY"}]`.
- `"label_max_y"`: keeps country labels above the captions (use 1270 with `--ig-safe`).
- New views `ethiopia`, `horn`, `tigray`; new places Mekelle, Axum, Shire, Alamata, Addis Ababa, Asmara.
- `anim` `feed` takes `"card_title"` and `"card_sub"` for the Africa card that scrolls past.

## Flight paths (added for congo-plane-crash-35s)
- `"flight"` in a map spec: a plane glyph flies a leg, and can divert to circle a place. For example: `{"from": "Kikwit", "to": "Kinshasa", "divert": "Kenge", "fly": [0.25, 0.95], "circle_from": 0.96, "radius": 120, "size": 44, "planned": true, "label_side": {"Kenge": "t"}}`. `planned` draws the intended route dashed; `circle_from` (scene progress) starts the circling; `fade_at` fades the plane out.
- New views: `drc` and `drc_sw`. New places: Kinshasa, Kikwit, Kenge, Goma.
- CTA headlines now shrink to fit, so long lines like "WHY DOES THIS KEEP HAPPENING?" never run off the screen.
