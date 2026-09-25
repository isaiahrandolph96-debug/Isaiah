# Post pack: "Yasmine's Vote" (stop motion)

**Files:** `morocco-stopmotion-PREVIEW.mp4` (57 s, 1080×1920, Instagram-safe) · `cover.jpg` · `storyboard.jpg`
**Facts as of:** provisional results, 24 Sept 2026 · **Dramatization:** the characters are fictional; the events and figures are real (shown on screen).

## ⚠️ Before posting: record the 5 missing voice lines
The ElevenLabs free credits ran out mid-production. These lines currently play as captions over music only:

| File | Voice | Line |
|---|---|---|
| `vo/s05_2.mp3` | Yasmine: Laloosh (`e69QIFnbVVXTRO1LrTN8`) | "And Akhannouch's party crashed. A hundred and two seats, down to sixty-six." |
| `vo/s05_3.mp3` | Haj Ahmed: Amir (`J8qhTPFlbVBa24VtZvhY`) | "And the Islamists are back. Thirteen to fifty-four!" |
| `vo/s06_1.mp3` | Haj Ahmed: Amir | "Three hundred ninety-five seats. You need one ninety-eight. Pam has ninety-seven." |
| `vo/s07_1.mp3` | Yasmine: Laloosh | "If the King picks her, she'd be our first woman head of government." |
| `vo/s08_1.mp3` | Narrator: Yusuf (`nJvj5shg2xu1GKGxqfkE`) | "New parliament. Same questions. And it barely made the news. That's the blind spot." |

That's about 390 characters, roughly 400 credits. Once they exist, re-run the same render command and the puppets' mouths sync automatically:
```bash
cd reels && python3 render_reel.py morocco-stopmotion-60s --ig-safe \
  --music morocco-stopmotion-60s/audio/music.wav --music-vol 0.26 \
  --sfx morocco-stopmotion-60s/audio/whoosh.mp3 --sfx-vol 0.35 \
  --endcard <brand reel>.mp4 --endcard-len 1.6 --out morocco-stopmotion-60s/morocco-stopmotion-60s-IG-reel.mp4
```
You can also record them yourself with any voice actor and drop the MP3s into `vo/` under those names.

---

## Instagram caption
> Morocco just voted, and most people didn't. 🗳️ A stop-motion story.
>
> 🇲🇦 Turnout: 38% (down from 50% in 2021)
> 🥇 PAM first with 97 seats; the King picks the next head of government from it
> 📉 RNI: 102 → 66 seats · 📈 Islamist PJD: 13 → 54
> 🧩 198 seats needed to govern; no coalition agreed yet
>
> Would you have voted? Tell us in the comments. 👇
>
> Send this to someone who hasn't heard. Follow @africablindspot for the stories others miss.
>
> Dramatization: characters are fictional; events and figures are real.
>
> #AfricaBlindSpot #Morocco #Maroc #MoroccoElections #StopMotion #Casablanca #Rabat #GenZ212 #NorthAfrica #AfricaNews

**Pinned first comment (sources):** Moroccan Interior Ministry provisional results (24 Sept 2026) via Maroc.ma · Hespress · Al Jazeera · The National · Morocco World News

## TikTok / Shorts
**Title:** Morocco just voted. Most people didn't. 🇲🇦 (stop motion) #shorts
**Caption:** 38% turnout. PAM first. Islamists back. A stop-motion story about Morocco's election. #Morocco #StopMotion #AfricaBlindSpot

## Stories
1. Poll: "Would you vote if you lived in Morocco?" YES / NO
2. Quiz: "What share of Moroccans voted?" 18% / **38%** ✅ / 58%
3. Slider: "How much do you trust elections to change things?"
4. Behind the scenes: the sugar-cube parliament frame, captioned "How coalitions work 🧊"

## X / Threads thread
1. Morocco just held an election, and 6 in 10 voters stayed home. We told it as a stop-motion story. 🧵
2. Turnout: 38%, down from 50% in 2021.
3. PAM came first with 97 of 395 seats. The King picks the head of government from the largest party.
4. The ruling RNI fell from 102 seats to 66. The Islamist PJD came back from 13 to 54.
5. 198 seats are needed to govern, and no coalition is agreed yet. [Reel link]
