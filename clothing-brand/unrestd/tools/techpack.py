"""Shift Jacket tech pack: the spec a factory quotes and samples from.

Writes tools/tech-pack.html; render.js prints it to ../tech-pack-shift-jacket.pdf.
All measurements are a starting spec for a cropped, boxy work jacket. Confirm
them on the first proto sample, adjust once, then lock them.
"""
from pathlib import Path

import garments as G
from build_logos import tag, BLACK, BONE, TAN, FADED, CORD, BRASS
from garments import placed_svg

TOOLS = Path(__file__).resolve().parent

SIZES = ["S", "M", "L", "XL", "XXL"]
POM = [  # letter, point of measure, tolerance, S..XXL (inches)
    ("A", "Chest, 1\" below armhole, full circumference", "±½", ["46", "48", "50", "52", "54"]),
    ("B", "Body length, high point shoulder to hem", "±½", ["24½", "25", "25½", "26", "26½"]),
    ("C", "Sleeve length, shoulder point to cuff edge", "±½", ["24½", "25", "25½", "26", "26½"]),
    ("D", "Across shoulder, seam to seam", "±¼", ["19", "19¾", "20½", "21¼", "22"]),
    ("E", "Hem width, waistband relaxed, full", "±½", ["42", "44", "46", "48", "50"]),
    ("F", "Collar length, along neck seam", "±¼", ["18", "18½", "19", "19½", "20"]),
]
BOM = [  # item, specification, placement, colour by colourway
    ("Shell", "12 oz (about 400 gsm) 100% cotton duck canvas, pre-shrunk", "Body, sleeves, pockets", "Black · Faded Black (garment washed) · Duck Tan"),
    ("Body lining", "Blanket lining, 100% acrylic, striped", "Body", "Red and black stripe, all colourways"),
    ("Sleeve lining", "Quilted nylon taffeta, light poly fill", "Sleeves", "Black"),
    ("Collar", "8-wale cotton corduroy", "Collar", "Black · Black · Brown"),
    ("Main zip", "#5 brass, antique finish, separating, one-way", "Centre front", "Brass"),
    ("Chest zip", "#3 brass, antique finish", "Left chest welt pocket", "Brass"),
    ("Snaps", "15 mm brass snaps", "Waistband side tabs (2), cuffs (2)", "Antique brass"),
    ("Thread", "Poly-core, Tex 70 on main seams", "All seams", "Contrast bone on Black and Faded Black; tonal on Duck Tan"),
    ("Woven tab", "55 × 22 mm woven damask, merrowed edge (artwork: woven-tab-black.svg)", "Left chest, 1.5 cm below the zip welt", "Black with bone tag"),
    ("Neck label", "60 × 25 mm woven, end-folded (artwork: labels/neck-label.svg)", "Centre back neck", "Black with bone tag"),
    ("Care label", "Printed satin (artwork: labels/care-label.svg)", "Left inside side seam, 10 cm above hem", "White"),
    ("Lot label", "Printed satin, \"LOT ___ / 040\", numbered in sequence", "Inside left facing, chest height", "White"),
    ("Hang tag", "350 gsm kraft, brass eyelet, black cotton string", "Through the main zip pull", "Kraft"),
    ("Back embroidery (optional)", "Chain-stitched tag, about 26 cm wide (artwork: tag-bone.svg)", "Centre back, 8 cm below collar seam", "Bone and brass thread"),
]
BUILD = [
    "Cropped, boxy body. Set-in sleeve with a 2 cm dropped shoulder.",
    "Triple-needle felled seams at shoulders, armholes and side seams.",
    "Bar tacks at every pocket end, the zip ends and the snap tabs.",
    "3.5 cm canvas waistband with a snap tab at each side seam. 6 cm band cuffs with one snap.",
    "Slash hand pockets bagged in lining fabric. Left chest zip welt pocket.",
    "Blanket lining in the body, quilted nylon in the sleeves, so the jacket slides on over a hoodie.",
    "Shrinkage no more than 3% after three home washes. Wash-test one sample before bulk.",
    "Fold with the tag facing up, polybag with a size sticker, 10 per carton.",
]
ORDER = {"S": 4, "M": 10, "L": 12, "XL": 9, "XXL": 5}


def pom_overlay():
    """Measurement lines and letters drawn over the front flat."""
    red = "#C0392B"
    def line(x1, y1, x2, y2, letter, lx, ly):
        return (f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{red}" stroke-width="2" stroke-dasharray="6 4"/>'
                f'<circle cx="{x1}" cy="{y1}" r="3" fill="{red}"/><circle cx="{x2}" cy="{y2}" r="3" fill="{red}"/>'
                f'<circle cx="{lx}" cy="{ly}" r="11" fill="{red}"/>'
                f'<text x="{lx}" y="{ly + 5}" font-family="IBM Plex Mono, monospace" font-weight="600" '
                f'font-size="14" fill="#fff" text-anchor="middle">{letter}</text>')
    return (line(104, 200, 336, 200, "A", 220, 214) + line(160, 56, 160, 394, "B", 172, 300)
            + line(92, 70, 30, 410, "C", 48, 250) + line(92, 66, 348, 66, "D", 300, 52)
            + line(102, 376, 338, 376, "E", 260, 376) + line(152, 50, 288, 50, "F", 220, 36))


def with_overlay(svg, overlay):
    return svg.replace("</svg>", overlay + "</svg>")


def build():
    front = with_overlay(G.work_jacket(BLACK, "#1E1E1E", G.TAB_BLACK, "Shift Jacket front, measurement points"), pom_overlay())
    back = G.work_jacket_back(BLACK, "#1E1E1E", placed_svg(tag(BONE), 118, 150, 204))
    tan = G.work_jacket(TAN, CORD, G.TAB_BLACK, "Duck Tan")
    faded = G.work_jacket(FADED, "#2A2A29", G.TAB_BLACK, "Faded Black")
    logo = placed_svg(tag(BLACK), 0, 0, 220)
    rows = "".join(f"<tr><td class=l>{l}</td><td>{n}</td><td class=c>{t}</td>" + "".join(f"<td class=c>{v}</td>" for v in vals) + "</tr>"
                   for l, n, t, vals in POM)
    bom = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in BOM)
    build = "".join(f"<li>{x}</li>" for x in BUILD)
    order = "".join(f"<td class=c>{ORDER[s]}</td>" for s in SIZES)
    html = f"""<!doctype html><meta charset=utf-8><title>UNRESTD Shift Jacket Tech Pack</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
@page{{size:Letter;margin:12mm}}
body{{font-family:Archivo,Arial,sans-serif;color:#121212;margin:0;font-size:11px}}
.page{{page-break-after:always}}
.head{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid #121212;padding-bottom:8px;margin-bottom:12px}}
.head svg{{width:180px;height:auto}}
.meta{{font-family:'IBM Plex Mono',monospace;font-size:10px;text-align:right;line-height:1.5}}
h1{{font-stretch:62%;font-variation-settings:'wdth' 62;font-weight:900;font-size:34px;margin:0;line-height:1;text-transform:uppercase}}
h2{{font-stretch:62%;font-variation-settings:'wdth' 62;font-weight:900;font-size:18px;margin:14px 0 6px;text-transform:uppercase}}
.flats{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.flat{{background:#E4E0D6;padding:6px}} .flat svg{{width:100%;height:auto;display:block}}
.cap{{font-family:'IBM Plex Mono',monospace;font-size:9.5px;margin-top:3px}}
.ways{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}
.ways .flat svg{{height:150px}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #BDB8AC;padding:4px 6px;text-align:left;vertical-align:top}}
th{{background:#121212;color:#EEEBE3;font-family:'IBM Plex Mono',monospace;font-size:9.5px;font-weight:500}}
td.c{{text-align:center;font-family:'IBM Plex Mono',monospace}} td.l{{font-weight:900;color:#C0392B;text-align:center}}
ul{{margin:4px 0;padding-left:16px}} li{{margin:2px 0}}
.note{{font-size:10px;color:#5C5850}}
.sign{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px}}
.sign div{{border-top:1px solid #121212;padding-top:4px;font-family:'IBM Plex Mono',monospace;font-size:9.5px}}
</style>
<div class="page">
  <div class="head"><div><svg viewBox="0 0 220 110">{logo}</svg><h1>Shift Jacket</h1></div>
    <div class="meta">TECH PACK · STYLE UD-J01<br>VERSION 1 · 26 SEPT 2026<br>DROP 01 “FIRST SHIFT”<br>BRAND: UNRESTD · unrestd.com</div></div>
  <div class="flats">
    <div class="flat">{front}<div class="cap">FRONT · measurement points A–F (see size chart)</div></div>
    <div class="flat">{back}<div class="cap">BACK · optional chain-stitched tag, centre back</div></div>
  </div>
  <h2>Colourways</h2>
  <div class="ways">
    <div class="flat">{G.work_jacket(BLACK, "#1E1E1E", G.TAB_BLACK)}<div class="cap">01 BLACK · black cord collar · 24 units</div></div>
    <div class="flat">{faded}<div class="cap">02 FADED BLACK · garment washed · pre-order only</div></div>
    <div class="flat">{tan}<div class="cap">03 DUCK TAN · brown cord collar · 16 units</div></div>
  </div>
  <h2>Size chart (inches, garment measurements)</h2>
  <table><tr><th></th><th>Point of measure</th><th>Tol.</th>{''.join(f'<th>{s}</th>' for s in SIZES)}</tr>{rows}</table>
  <p class="note">This is a starting spec for a cropped, boxy fit. Make the proto in size L, fit it on a person, adjust once, then grade +2" chest per size.</p>
</div>
<div class="page">
  <div class="head"><div><svg viewBox="0 0 220 110">{logo}</svg><h1>Materials &amp; build</h1></div>
    <div class="meta">STYLE UD-J01 · SHIFT JACKET<br>PAGE 2 OF 2</div></div>
  <h2>Bill of materials</h2>
  <table><tr><th>Item</th><th>Specification</th><th>Placement</th><th>Colour</th></tr>{bom}</table>
  <h2>Construction</h2><ul>{build}</ul>
  <h2>First order</h2>
  <table><tr><th>Stage</th>{''.join(f'<th>{s}</th>' for s in SIZES)}<th>Total</th></tr>
    <tr><td>Proto sample</td><td class=c>–</td><td class=c>–</td><td class=c>1 per colour</td><td class=c>–</td><td class=c>–</td><td class=c>3</td></tr>
    <tr><td>Bulk, lot 001, all colours (Black 24, Duck Tan 16)</td>{order}<td class=c>40</td></tr></table>
  <p class="note">Please quote: sample price, per-unit price at 40 and at 100 units, lead time for samples and for bulk, and shipping to the US. Every jacket gets a numbered lot label, 001 to 040.</p>
  <div class="sign"><div>Brand approval</div><div>Factory approval</div><div>Date</div></div>
</div>"""
    (TOOLS / "tech-pack.html").write_text(html)


if __name__ == "__main__":
    build()
