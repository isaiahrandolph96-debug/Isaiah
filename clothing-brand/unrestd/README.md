# UNRESTD

**Not done yet.** Duck canvas workwear and heavyweight basics for the ones still up: the night shift, the 5 a.m. start, the business you build after the day job ends.

UNRESTD is UNRESTED with the E taken out, because we didn't stop for it. The brass bar in the logo marks where the E used to be.

The full brand book is `brand-book.html` (open it in a browser), and the same content is rendered as `brand-book.png`.

## Name status (checked 26 Sept 2026)
- **Domains available** (Vercel registrar check): `unrestd.com`, `wearunrestd.com`, `unrestd.co` and `unrestd.shop`. `unrested.com` is taken. Buy `unrestd.com` soon, because "available" only means nobody owns it right now.
- **Risk:** a small brand called **Unrest Clothing** exists (`unrestclothing.com`, @unrestclth). A name this close can cause a trademark conflict in Class 25 (clothing). Get a USPTO search done, ideally by a trademark attorney, before you order stock.
- **Handles:** not checked yet. Try @unrestd, then @wearunrestd.

## The brand in five lines
- **Idea:** restless, not reckless. UNRESTD is about never settling, not about never sleeping. The brand never glamorises burnout or makes fun of rest.
- **Look:** the brand has three logo pieces:
  - A custom squared wordmark with a brass bar where the E would be.
  - A wide stitched woven tab, deliberately not square so it can't be confused with Carhartt's label.
  - A U|D monogram.

  The palette is Black Duck `#121212`, Faded Black `#3B3B39`, Duck Tan `#C2A878`, Moss `#4A4F36`, Bone `#EEEBE3` and Brass `#B58B4C`. The type is Archivo (62% width, weight 900) and IBM Plex Mono.
- **Voice:** the person next to you on the late shift. "Not done yet." "While you slept." "Rest later." "The E is on break."
- **For:** night shifts and early starts (trades, warehouses, kitchens, hospitals, drivers), people with side businesses, and people who dress black-on-black. Age 18 to 34, US first.
- **Model:** the jackets are made in a numbered small batch and sold on pre-order. The basics are print-on-demand through Printful.

## Drop 01 "First Shift" (doors open early November 2026)
| Piece | Made by | Price | Cost | You keep |
|---|---|---:|---:|---:|
| Shift Jacket (black, faded black, duck tan) | small batch | $165 | ~$38–73 landed | ~$87–122 |
| Night Shift Jacket (hooded) | small batch | $185 | ~$43–83 landed | ~$96–136 |
| Split Zip Hoodie (U and D either side of the zip; NOT DONE YET. on the back) | Printful | $95 | ~$38 | ~$54 |
| Shift Tee (black with a tonal U\|D, or bone with WHILE YOU SLEPT. on the back) | Printful | $42 | ~$15–21 | ~$19–25 |
| Watch Beanie | Printful | $32 | ~$14 | ~$17 |

"You keep" is after Shopify's 2.9% + 30¢ card fee. Every cost except the $15.29 Printful tee is an estimate, so get three factory quotes and check Printful's calculator before you set prices.

**Budget:** about $1,060–2,270 before the first batch. The first batch of 40 Shift Jackets costs another $1,520–2,920. Selling those 40 jackets at $165 brings in about $6,400 after fees, which covers everything.

## Files
| Path | What |
|---|---|
| `logo/` | Wordmark, U\|D monogram and woven tab as SVGs with transparent backgrounds, ready to print or embroider |
| `print/` | Back-print artwork at 4500 × 5400 px on a transparent background: `shift-tee-back.png` and `split-zip-hoodie-back.png` |
| `mockups/` | Flat drawings of every Drop 01 piece, including all three Shift Jacket colours, as SVG and 1200 px PNG. These are the starting point for the tech packs |
| `drop-01.png` | The Drop 01 line-up on one page |
| `fonts/` | Archivo and IBM Plex Mono (SIL Open Font License, licence files included), used for offline renders |
| `tools/` | Generators: `build.py` makes the logos, mockups and brand book, and `render.js` renders the PNGs |

## Rebuild
```
python3 clothing-brand/unrestd/tools/build.py
node clothing-brand/unrestd/tools/render.js
```
