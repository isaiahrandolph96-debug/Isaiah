---
name: daily-narrations
description: Produce Africa Blind Spot's five daily narrations (voiceover scripts for CapCut) from the day's top five Africa stories. Use when asked for the daily narrations, the day's scripts, or "narrations from today's briefing".
---

# Africa Blind Spot: the five daily narrations

The owner needs **five narrations every day**, one per top story from the daily briefing. They paste them into CapCut (text-to-speech or their own voice). Each must be **informative, clear to a first-time reader, and match the severity of the story in tone**.

## 1. Pick the day's top five
- Start from today's briefing in `briefings/` (write or refresh it first if it's stale). Research with web search, and prefer items dated today or the last 48 h.
- Rank by **human stakes first** (lives, displacement, rights), then **reach** (how many people are affected), then **newness**, then **the blind-spot factor** (big but under-covered).
- Spread the list across regions (North, West, Central, East, Southern Africa, the Horn) and across topics (conflict, health, climate, politics, economy, culture or sport). Aim for **no more than 2 conflict stories**, and **at least one** hopeful, economic or culture story. Cover at least 3 different regions.
- For a continuing story, only include it if something **new** happened. Lead with the new development.

## 2. Assign a severity tier (it sets the tone)
| Tier | Use for | Tone and writing | CapCut voice and music |
|---|---|---|---|
| **1: CRITICAL** | War, mass killing, famine, mass displacement | Grave, calm, restrained. Short sentences. No hype, no exclamation marks, no "shocking". Let the facts carry the weight. Humanise with one concrete detail. | Deep, calm voice at 0.9× speed. Low drone or no music. Long pauses. |
| **2: SERIOUS** | Epidemics, deadly disasters, violent crime, repression | Measured and empathetic. Explain the risk plainly. Include hope or help where it's real (for example, helplines). | Calm voice at 0.95×. Soft, sombre bed. |
| **3: DEVELOPING** | Elections, protests, policy, diplomacy | Neutral and explanatory, like a good teacher. Always present each side fairly. | Neutral voice at 1.0×. Light, neutral bed. |
| **4: OPPORTUNITY** | Economy, infrastructure, investment, tech | Clear and forward-looking, not promotional. Note who benefits and the risks. | Warm voice at 1.0×. Light, upbeat bed. |
| **5: HUMAN INTEREST** | Sport, culture, people | Warm and lively, but respectful, especially when there's a darker thread. | Bright voice at 1.0–1.05×. Upbeat bed. |

## 3. Structure of every narration (150–230 words, about 60–90 s)
1. **Hook (1–2 sentences):** the stake or the most striking fact. No "Hello" and no intro.
2. **What happened:** who, what, where and when, with dates. Name the country *and* where it is ("Mali, in West Africa's Sahel").
3. **Context for first-time readers:** explain every group, acronym and place the first time ("JNIM, an armed group linked to al-Qaeda"). No jargon.
4. **Why it matters:** to people there, to the region, to the listener.
5. **What's next:** one or two things to watch.
6. **Sign-off:** "This is Africa Blind Spot." Tier 1–2 stories end there. Tier 3–5 stories can add "Follow for the stories others miss."

## 4. Writing for the ear (so text-to-speech reads it well)
- Short sentences, one idea each. Active voice.
- Numbers: use digits for the captions, but no symbols. Write "percent", "dollars" and "kilometres"; avoid "~", "%", "$", "&" and "/".
- Attribute in speech: "according to Reuters", "Human Rights Watch says", "the group claims". Say "reportedly" or "unconfirmed" when that's the truth.
- No brackets, no emojis, no markdown inside the narration text.
- Add a **pronunciation note** in the metadata for hard names (it isn't read aloud).

## 5. Facts and ethics (non-negotiable)
- Every number has a named source in the story's `Sources` line. For disputed figures, give the range and say who says what.
- Separate claims by armed groups ("the group claims") from verified facts.
- Include the government's or the other side's position in any accusation story.
- Include no graphic detail beyond what's needed. Give helpline info for gender-based violence and suicide stories where it exists.
- State "as of <date>" in the file header. If a story is still unfolding (a match, a vote count), label it **PREVIEW** or **DEVELOPING** and say what to update.

## 6. Output
- Write `narrations/YYYY-MM-DD/NARRATIONS.md` in the format of `narrations/2026-09-26/NARRATIONS.md` (that day had ten stories; from 27 Sept 2026 onward there are five). Each story is a `## N. Title` block with metadata bullets (Tier, Tone, Length, Voice/music, On-screen title, Pronunciation, Sources) and the narration between `<<<` and `>>>` lines.
- Run `python3 narrations/split.py narrations/YYYY-MM-DD` to write clean `01-*.txt` … `05-*.txt` files, ready to paste into CapCut. It also prints word counts and flags symbols that TTS reads badly.
- Commit and push. Send the owner `NARRATIONS.md` and the folder's txt files, and list the five with their tiers in chat.
