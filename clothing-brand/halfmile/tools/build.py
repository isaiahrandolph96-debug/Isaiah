"""Build everything for the Halfmile brand kit.

    python3 clothing-brand/halfmile/tools/build.py   # logos, mockup SVGs, brand-book.html (template + body), print.html
    node    clothing-brand/halfmile/tools/render.js  # PNG mockups, print files, brand sheet
"""
import re
from pathlib import Path

import build_logos as L
import garments as G

ROOT = Path(__file__).resolve().parent.parent
TOOLS = Path(__file__).resolve().parent


def inline(path):
    """Read a logo SVG for inlining: drop the fixed size and the <title>."""
    s = (ROOT / "logo" / path).read_text()
    s = re.sub(r' width="[\d.]+" height="[\d.]+"', "", s, count=1)
    return re.sub(r"<title>.*?</title>", "", s).strip()


def hero_wordmark():
    body, w = L.wordmark("currentColor", "SPLIT")
    body = body.replace('fill="SPLIT"', 'style="fill:var(--split)"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -16 {w + 4} {L.H + 32}" '
            f'aria-hidden="true">{body}</svg>')


CARDS = [
    # id of main shot, id of inset shot (or None), name, price, blurb, spec, featured
    ("shift-jacket-black", "shift-jacket-tan", "Shift Jacket", "$165",
     "The hero piece. A cropped 12 oz duck canvas work jacket with a cord collar, blanket lining and "
     "a brass zip. Comes in black, faded black and duck tan.",
     "Small batch · pre-order · 12 oz cotton duck", True),
    ("night-shift-jacket", None, "Night Shift Jacket", "$185",
     "A hooded duck canvas jacket with a quilted lining and knit cuffs, for the coldest shifts.",
     "Small batch · pre-order · black", False),
    ("split-zip-hoodie", "split-zip-hoodie-back", "Split Zip Hoodie", "$95",
     "HALF on one side of the zip and MILE on the other, so the zipper is the split line. "
     "BUILT FOR THE LONG MIDDLE. runs across the back.",
     "Duck tan · heavyweight full zip · print-on-demand", False),
    ("shift-tee-black", "shift-tee-bone-back", "Shift Tee", "$42",
     "The tee under the jacket. Black with a tonal monogram, or bone with the back print.",
     "Comfort Colors 1717 · print-on-demand", False),
    ("watch-beanie", None, "Watch Beanie", "$32",
     "A black rib knit with the tab on the cuff. It's embroidered at launch, and becomes woven once you order patches.",
     "Black · print-on-demand embroidery", False),
]


def cards(shots):
    out = []
    for main, inset, name, price, blurb, spec, feat in CARDS:
        ins = f'<div class="inset" aria-hidden="true">{shots[inset]}</div>' if inset else ""
        view = "Back, with the front inset" if inset else "Front"
        out.append(
            f'<article class="card{" feat" if feat else ""}">'
            f'<div class="shot" id="m-{main}" title="{name}, {view.lower()}">{shots[main]}{ins}</div>'
            f'<div class="row"><h3>{name}</h3><span class="price">{price}</span></div>'
            f'<p>{blurb}</p><div class="spec-line">{spec}</div></article>')
    return "".join(out)


CARD_CSS = """
.drop{grid-template-columns:repeat(4,minmax(0,1fr))}
.card.feat{grid-column:span 2;grid-row:span 2}
.card.feat h3{font-size:34px}
.shot{position:relative}
.shot .inset{position:absolute;right:5%;bottom:5%;width:32%;aspect-ratio:1/1;background:var(--tile);
  border:1.5px solid rgba(0,0,0,.18);padding:3%}
@media (max-width:900px){.drop{grid-template-columns:repeat(2,minmax(0,1fr))}.card.feat{grid-row:auto}}
@media (max-width:520px){.drop{grid-template-columns:1fr}.card.feat{grid-column:auto}}
"""


def main():
    L.main()
    shots = {p["id"]: p["svg"] for p in G.products()}
    (ROOT / "mockups").mkdir(exist_ok=True)
    for old in (ROOT / "mockups").glob("*.*"):
        old.unlink()
    for pid, s in shots.items():
        (ROOT / "mockups" / f"{pid}.svg").write_text(s + "\n")

    html = (TOOLS / "brand-book.template.html").read_text()
    html = html.replace("</style>", CARD_CSS + "</style>", 1)
    html = html.replace("{{BODY}}", (TOOLS / "brand-book.body.html").read_text())
    rep = {
        "{{WORDMARK_HERO}}": hero_wordmark(),
        "{{TAB_BLACK}}": inline("woven-tab-black.svg"),
        "{{TAB_TAN}}": inline("woven-tab-tan.svg"),
        "{{WORDMARK_BLACK}}": inline("wordmark-black.svg"),
        "{{MONOGRAM_BONE}}": inline("monogram-bone.svg"),
        "{{PRODUCT_CARDS}}": cards(shots),
    }
    for k, v in rep.items():
        html = html.replace(k, v)
    (ROOT / "brand-book.html").write_text(html)

    # print.html: one 1500 x 1800 CSS-px box per design (x3 scale = 4500 x 5400 px)
    boxes = "".join(
        f'<div class="pf" id="p-{name}"><svg xmlns="http://www.w3.org/2000/svg" viewBox="-15 -18 330 396">'
        f'<style>{G.FONT_CSS}</style>{art}</svg></div>'
        for name, art, _ in G.print_files())
    (TOOLS / "print.html").write_text(
        "<!doctype html><meta charset=utf-8><style>body{margin:0;background:transparent}"
        ".pf{width:1500px;height:1800px}.pf svg{width:100%;height:100%;display:block}</style>" + boxes)


if __name__ == "__main__":
    main()
