# Halfmile

**Built for the long middle.** Duck canvas jackets and heavyweight basics for people putting in the work nobody films: the shift, the commute, the years between starting and making it.

The full brand book is `brand-book.html` (open it in a browser), and the same content is rendered as `brand-book.png`. This is v2, rebuilt around the owner's workwear references: black-on-black duck canvas, tan work jackets over white tees, olive cargos, brass zips, beanies and boots.

## The brand in five lines
- **Idea:** workwear toughness, worn on the street. Tonal black-on-black or tan-on-tan, with one brass detail.
- **For:** trades and long-shift workers, builders in the middle years, and people who dress black-on-black. Age 18 to 34, US first.
- **Voice:** the person next to you on the shift. Few words and real details. "Clocked in." "Nobody films the half mile." "12 oz. Breaks in, not down."
- **Look:** the brand has three logo pieces:
  - A custom squared wordmark with a **brass split line**.
  - A wide stitched **woven tab**, deliberately not square, so it can't be confused with Carhartt's label.
  - An **H|M monogram**.

  The colours are Black Duck `#121212`, Faded Black `#3B3B39`, Duck Tan `#C2A878`, Moss `#4A4F36`, Bone `#EEEBE3` and Brass `#B58B4C`. The type is Archivo (62% width, weight 900) and IBM Plex Mono.
- **Model:** the jackets are made in a numbered small batch and sold on pre-order. The basics are print-on-demand through Printful.

## Drop 01 "First Shift" (doors open early November 2026)
| Piece | Made by | Price | Cost | You keep |
|---|---|---:|---:|---:|
| Shift Jacket (black, faded black, duck tan) | small batch | $165 | ~$38–73 landed | ~$87–122 |
| Night Shift Jacket (hooded) | small batch | $185 | ~$43–83 landed | ~$96–136 |
| Split Zip Hoodie (duck tan) | Printful | $95 | ~$38 | ~$54 |
| Shift Tee (black monogram, or bone with the back print) | Printful | $42 | ~$15–21 | ~$19–25 |
| Watch Beanie | Printful | $32 | ~$14 | ~$17 |

The duck canvas jackets can't be print-on-demand. Blank canvas jackets from workwear makers (Berne, DRI DUCK) come with the maker's branding at $65–89 each, which leaves no margin. So the jackets are made to the Halfmile design by a low-minimum factory (20 to 50 pieces per design). "You keep" is after Shopify's 2.9% + 30¢ card fee. Every cost except the $15.29 Printful tee is an estimate, so get three factory quotes and check Printful's calculator before you set prices. The sources are at the end of `brand-book.html`.

**Budget:** about $1,060–2,270 before the first batch (samples, tech packs, tabs, Shopify, a domain and the $350 USPTO filing). The first batch of 40 Shift Jackets costs another $1,520–2,920. Selling those 40 jackets at $165 brings in about $6,400 after fees, which covers everything.

## Before spending money
1. Search USPTO for HALFMILE and HALF MILE in Class 25 (clothing), and check the social handles. As of 26 Sept 2026 no clothing brand with the name turned up, but `halfmile.com` is taken.
2. Get quotes from three factories and pay for a sample before you pay for a batch.
3. Put a clear ship-by date on every pre-order. The FTC's mail-order rule applies.

## Files
| Path | What |
|---|---|
| `logo/` | Wordmark, H\|M monogram and woven tab as SVGs with transparent backgrounds, ready to print or embroider |
| `print/` | Back-print artwork at 4500 × 5400 px on a transparent background, for the Shift Tee and the Split Zip Hoodie |
| `mockups/` | Flat drawings of every Drop 01 piece, including all three Shift Jacket colours, as SVG and 1200 px PNG. These are the starting point for the tech packs |
| `drop-01.png` | The Drop 01 line-up on one page |
| `fonts/` | Archivo and IBM Plex Mono (SIL Open Font License, licence files included), used for offline renders |
| `tools/` | Generators: `build.py` makes the logos, mockups and brand book, and `render.js` renders the PNGs |

## Rebuild
```
python3 clothing-brand/halfmile/tools/build.py
node clothing-brand/halfmile/tools/render.js
```
