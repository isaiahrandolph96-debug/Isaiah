"""Build everything for the Halfmile brand kit.

    python3 clothing-brand/halfmile/tools/build.py   # logos, mockup SVGs, brand-book.html, print.html
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
    ("split-tee-back", "split-tee-front", "Split Tee", "$40",
     "The flagship. A small Split mark on the chest, and the whole idea of the brand across the back.",
     "Chalk · Comfort Colors 1717 · 6.1 oz garment-dyed cotton", True),
    ("splits-tee", None, "Splits Tee", "$40",
     "Five split times from start to “keep going”, set in mono like a race printout.",
     "Asphalt · Comfort Colors 1717", False),
    ("middle-hoodie-back", "middle-hoodie", "Middle Hoodie", "$85",
     "The wordmark on the chest and STILL HERE. on the back. The hero piece for cold months.",
     "Asphalt · Cotton Heritage M2580 · 8.5 oz fleece", False),
    ("split-cap", None, "Split Cap", "$34",
     "A low-profile dad hat with the Split embroidered on the front.",
     "Mondo Blue · Yupoong 6245CM · embroidered", False),
    ("lane-beanie", None, "Lane Beanie", "$30",
     "A cuffed knit beanie with a small woven 0.5 label. The gift pick.",
     "Infield · cuffed knit · embroidered", False),
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
    for pid, s in shots.items():
        (ROOT / "mockups" / f"{pid}.svg").write_text(s + "\n")

    html = (TOOLS / "brand-book.template.html").read_text()
    html = html.replace("</style>", CARD_CSS + "</style>", 1)
    rep = {
        "{{WORDMARK_HERO}}": hero_wordmark(),
        "{{LOCKUP_DARK}}": inline("lockup-on-dark.svg"),
        "{{WORDMARK_LIGHT}}": inline("wordmark-on-light.svg"),
        "{{MARK_BLUE}}": inline("mark-mono-white.svg"),
        "{{MARK_YELLOW}}": inline("mark-mono-black.svg"),
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
