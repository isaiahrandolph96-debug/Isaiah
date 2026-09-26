# Halfmile

**For the middle of the race.** Heavyweight streetwear basics for people in the middle of something. Everyone films the start and the finish, but nobody films the half mile.

The full brand book is `brand-book.html` (open it in a browser), and the same content is rendered as `brand-book.png`. This file is the short version.

## The brand in five lines
- **Idea:** gym brands sell the finish line and luxury basics sell having arrived. Halfmile sells the middle: quiet clothes, heavy fabric, and a story people recognise from their own life.
- **For:** runners mid-training block, first-time founders and creators, students and apprentices. Age 18 to 34, US first.
- **Voice:** a training partner, not a hype man. Short sentences and real numbers. "Nobody films the half mile." "Still here." "Keep going."
- **Look:** a custom squared wordmark with a split line at the halfway point, and **the Split** mark, a running track that's half covered and half still to go. The colours are Asphalt `#1C1E20`, Chalk `#F2F1EC`, Mondo Blue `#2F4FD8`, Infield `#3E5B45` and Timer `#F2C230`. The type is Archivo (62% width, weight 900) and IBM Plex Mono.
- **Model:** print-on-demand (Printful) first. Move a design to screen printing once it sells about 100 per run.

## Drop 01 "Mile 0.5" (launch mid-November 2026)
| Piece | Blank | Price | Maker cost | You keep |
|---|---|---:|---:|---:|
| Split Tee (front mark and back text) | Comfort Colors 1717 | $40 | ~$20.79 | ~$17.75 |
| Splits Tee | Comfort Colors 1717 | $40 | $15.29 | $23.25 |
| Middle Hoodie (front and back) | Cotton Heritage M2580 | $85 | ~$32.45 | ~$49.78 |
| Split Cap | Yupoong 6245CM, embroidered | $34 | ~$15 | ~$17.70 |
| Lane Beanie | cuffed knit, embroidered | $30 | ~$14 | ~$14.83 |

"You keep" is after Shopify's card fee (2.9% + 30¢) and assumes the customer pays shipping. The tee and hoodie costs are Printful prices for size M (as of September 2026). The back print, cap and beanie costs are estimates, so check them all in Printful's calculator before you publish prices. The sources are listed at the end of `brand-book.html`.

**Lean start budget:** about $640 to $740 before ads. That covers samples, 3 months of Shopify Basic, a domain and the $350 USPTO filing for Class 25, plus your state's LLC fee on top. Selling around 35 tees covers it.

## Before spending money
1. Search USPTO for HALFMILE and HALF MILE in Class 25 (clothing). My web search on 26 Sept 2026 turned up no clothing brand with the name, but `halfmile.com` is taken.
2. Claim the handles and a domain (`wearhalfmile.com`, `halfmile.co` or `halfmileclub.com`). I haven't checked whether they're free.
3. Order a sample of every piece and wash each one five times before you sell it.

## Files
| Path | What |
|---|---|
| `logo/` | Wordmark, the Split mark and the stacked lockup as SVGs, in on-dark, on-light, mono-black and mono-white versions. The logo is pure geometry, so no font is needed |
| `print/` | Print-ready artwork at 4500 × 5400 px on a transparent background (Printful's size for a full front or back print) |
| `mockups/` | Flat mockups of every Drop 01 piece, as SVG and 1200 px PNG |
| `drop-01.png` | The Drop 01 line-up on one page |
| `fonts/` | Archivo and IBM Plex Mono (SIL Open Font License), used for offline renders |
| `tools/` | Generators: `build.py` makes the logos, mockups and brand book, and `render.js` renders the PNGs |

For chest and cap prints, upload the logo SVGs directly (`mark-on-light.svg` for the Split Tee chest, `wordmark-on-dark.svg` for the hoodie chest and `mark-on-dark.svg` for the cap embroidery). All logo files have transparent backgrounds.

## Rebuild
```
python3 clothing-brand/halfmile/tools/build.py
node clothing-brand/halfmile/tools/render.js
```
