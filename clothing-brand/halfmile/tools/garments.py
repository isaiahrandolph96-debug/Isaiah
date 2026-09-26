"""Halfmile Drop 01 artwork and flat garment mockups, as SVG strings.

Artwork uses Archivo (condensed, 900) and IBM Plex Mono from Google Fonts,
so render it in a browser (tools/render.js) to get PNGs.
"""
from build_logos import wordmark, mark, CHALK, ASPHALT, BLUE, YELLOW, H

INFIELD = "#3E5B45"
FONT_CSS = ("@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900"
            "&family=IBM+Plex+Mono:wght@500;600&display=swap');"
            ".d{font-family:Archivo,'Arial Narrow',sans-serif;font-weight:900;font-stretch:62%;"
            "font-variation-settings:'wdth' 62}"
            ".m{font-family:'IBM Plex Mono',ui-monospace,monospace;font-weight:600}")


# ---------- artwork (each drawn in a 300 x 360 print box) ----------

# Font sizes below are measured so each line sets exactly 300 wide in Archivo
# at 62% width, weight 900; textLength only mops up sub-pixel rounding and
# adjusts spacing, never glyph shapes.

def fit(text, size, y, ink):
    return (f'<text class="d" x="0" y="{y}" font-size="{size}" textLength="300" '
            f'lengthAdjust="spacing" fill="{ink}">{text}</text>')


def art_split_back(ink=ASPHALT, accent=BLUE):
    t = fit("NOBODY", 96.9, 72, ink) + fit("FILMS THE", 78.3, 140, ink) + fit("HALF MILE.", 74.1, 205, ink)
    lanes = "".join(f'<rect x="0" y="{226 + i * 12}" width="300" height="5" fill="{accent}"/>' for i in range(3))
    cap = f'<text class="m" x="0" y="284" font-size="15" fill="{ink}">MILE 0.5 / DROP 01</text>'
    cap2 = f'<text class="m" x="300" y="284" font-size="15" fill="{ink}" text-anchor="end">HALFMILE</text>'
    return t + lanes + cap + cap2


def art_splits(ink=CHALK, accent=YELLOW):
    rows = [("0.1", "STARTED"), ("0.2", "STILL FRESH"), ("0.3", "DOUBT"), ("0.4", "QUIET"), ("0.5", "KEEP GOING")]
    out = [fit("SPLITS", 115.4, 86, ink)]
    for i, (mi, word) in enumerate(rows):
        y = 146 + i * 46
        col = accent if mi == "0.5" else ink
        out.append(f'<rect x="0" y="{y - 32}" width="300" height="2" fill="{ink}" opacity=".5"/>')
        out.append(f'<text class="m" x="0" y="{y}" font-size="22" fill="{col}">{mi} MI</text>')
        out.append(f'<text class="m" x="300" y="{y}" font-size="22" fill="{col}" text-anchor="end">{word}</text>')
    out.append(f'<rect x="0" y="{146 + 4 * 46 + 14}" width="300" height="2" fill="{ink}" opacity=".5"/>')
    return "".join(out)


def art_still_here(ink=CHALK, accent=YELLOW):
    return fit("STILL", 144.9, 106, ink) + fit("HERE.", 138.4, 220, ink) + \
        f'<rect x="0" y="240" width="300" height="8" fill="{accent}"/>'


def placed(art, x, y, w):
    """Place a 300x360 artwork box at (x, y) scaled to width w."""
    return f'<g transform="translate({x},{y}) scale({w / 300})">{art}</g>'


def placed_mark(ink, split, x, y, w):
    m, mw, _ = mark(ink, split)
    return f'<g transform="translate({x},{y}) scale({w / mw})">{m}</g>'


def placed_wordmark(ink, split, x, y, w):
    body, ww = wordmark(ink, split)
    return f'<g transform="translate({x},{y}) scale({w / ww})">{body}</g>'


# ---------- garments ----------

LINE = "rgba(0,0,0,.38)"
SHADE = "rgba(0,0,0,.16)"


def svg(vb, inner, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{label}">'
            f'<style>{FONT_CSS}</style>{inner}</svg>')


def tee(fill, graphic="", back=False, label="T-shirt"):
    body = ("M138,22 C{a} L338,48 L396,132 L344,166 L314,128 L316,424 C240,432 160,432 84,424 "
            "L86,128 L56,166 L4,132 L62,48 Z").format(
        a="160,34 240,34 262,22" if back else "158,58 242,58 262,22")
    neck = ("" if back else
            f'<path d="M138,22 C170,14 230,14 262,22 C242,58 158,58 138,22 Z" fill="{SHADE}"/>')
    rib = ('<path d="M138,22 C160,34 240,34 262,22" fill="none" stroke="{l}" stroke-width="7" opacity=".5"/>' if back else
           '<path d="M138,22 C158,58 242,58 262,22" fill="none" stroke="{l}" stroke-width="7" opacity=".5"/>').format(l=LINE)
    seams = (f'<g fill="none" stroke="{LINE}" stroke-width="1.5">'
             '<path d="M72,46 Q92,90 86,128"/><path d="M328,46 Q308,90 314,128"/>'
             '<path d="M13,127 L61,158" stroke-dasharray="4 4"/><path d="M387,127 L339,158" stroke-dasharray="4 4"/>'
             '<path d="M86,414 C160,422 240,422 314,414" stroke-dasharray="4 4"/></g>')
    inner = (f'<path d="{body}" fill="{fill}" stroke="{LINE}" stroke-width="2" stroke-linejoin="round"/>'
             f'{neck}{rib}{seams}{graphic}')
    return svg("-10 0 420 440", inner, label)


def hoodie(fill, graphic="", label="Hoodie"):
    body = ("M150,60 L84,84 C60,92 48,110 44,140 L18,400 L70,410 L96,200 L98,452 L342,452 L344,200 "
            "L370,410 L422,400 L396,140 C392,110 380,92 356,84 L290,60 Z")
    inner = (f'<path d="{body}" fill="{fill}" stroke="{LINE}" stroke-width="2" stroke-linejoin="round"/>'
             f'<g fill="{fill}" stroke="{LINE}" stroke-width="2">'
             '<path d="M18,400 L70,410 L66,442 L14,432 Z"/><path d="M422,400 L370,410 L374,442 L426,432 Z"/>'
             '<rect x="98" y="448" width="244" height="28"/>'
             '<path d="M140,330 L300,330 L318,424 L122,424 Z"/>'
             '<path d="M150,60 C138,-4 302,-4 290,60 C280,102 160,102 150,60 Z"/></g>'
             f'<path d="M172,58 C178,18 262,18 268,58 C258,88 182,88 172,58 Z" fill="{SHADE}"/>'
             f'<g stroke="{LINE}" stroke-width="1.5" fill="none">'
             '<path d="M140,330 L122,424" /><path d="M300,330 L318,424"/>'
             '<path d="M104,462 H336" stroke-dasharray="4 4"/>'
             '<path d="M96,200 Q100,160 84,86"/><path d="M344,200 Q340,160 356,86"/></g>'
             f'<g stroke="{CHALK if fill == ASPHALT else ASPHALT}" stroke-width="4" stroke-linecap="round" opacity=".8">'
             '<path d="M200,88 L194,176"/><path d="M240,88 L246,176"/></g>'
             f'{graphic}')
    return svg("0 -10 440 494", inner, label)


def cap(fill, graphic="", label="Cap"):
    inner = (f'<path d="M40,170 C40,60 110,30 180,30 C250,30 320,60 320,170 Z" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
             f'<g fill="none" stroke="{LINE}" stroke-width="1.5">'
             '<path d="M112,38 Q88,100 98,170"/><path d="M248,38 Q272,100 262,170"/>'
             '<path d="M52,160 C120,150 240,150 308,160" stroke-dasharray="4 4"/></g>'
             f'<circle cx="180" cy="32" r="7" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
             f'<path d="M14,172 C60,148 300,148 346,172 C336,214 24,214 14,172 Z" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
             f'<path d="M14,172 C60,148 300,148 346,172 C336,214 24,214 14,172 Z" fill="{SHADE}"/>'
             f'{graphic}')
    return svg("0 0 360 230", inner, label)


def beanie(fill, graphic="", label="Beanie"):
    ribs = "".join(f'<path d="M{x},156 V238"/>' for x in range(52, 250, 9))
    inner = (f'<path d="M52,170 C52,40 248,40 248,170 Z" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
             f'<rect x="40" y="148" width="220" height="96" rx="12" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
             f'<g stroke="{SHADE}" stroke-width="2">{ribs}</g>'
             f'{graphic}')
    return svg("20 30 260 230", inner, label)


def label_05():
    return ('<rect x="124" y="176" width="52" height="32" fill="#F2F1EC" stroke="rgba(0,0,0,.25)"/>'
            f'<text class="m" x="150" y="199" font-size="17" text-anchor="middle" fill="{ASPHALT}">0.5</text>')


# ---------- the Drop 01 line-up ----------

def products():
    return [
        dict(id="split-tee-back", name="Split Tee", view="Back",
             svg=tee(CHALK, placed(art_split_back(), 110, 92, 180), back=True, label="Split Tee, back")),
        dict(id="split-tee-front", name="Split Tee", view="Front",
             svg=tee(CHALK, placed_mark(ASPHALT, BLUE, 238, 96, 46), label="Split Tee, front")),
        dict(id="splits-tee", name="Splits Tee", view="Front",
             svg=tee(ASPHALT, placed(art_splits(), 118, 86, 164), label="Splits Tee, front")),
        dict(id="middle-hoodie", name="Middle Hoodie", view="Front",
             svg=hoodie(ASPHALT, placed_wordmark(CHALK, YELLOW, 170, 126, 100), label="Middle Hoodie, front")),
        dict(id="middle-hoodie-back", name="Middle Hoodie", view="Back",
             svg=hoodie(ASPHALT, placed(art_still_here(), 140, 110, 160), label="Middle Hoodie, back")),
        dict(id="split-cap", name="Split Cap", view="Front",
             svg=cap(BLUE, placed_mark(CHALK, YELLOW, 146, 88, 68), label="Split Cap")),
        dict(id="lane-beanie", name="Lane Beanie", view="Front",
             svg=beanie(INFIELD, label_05(), label="Lane Beanie")),
    ]


def print_files():
    """Front/back artwork at print-box proportions (Printful: 4500 x 5400 px)."""
    return [
        ("split-tee-back", art_split_back(), CHALK),
        ("splits-tee-front", art_splits(), ASPHALT),
        ("middle-hoodie-back", art_still_here(), ASPHALT),
    ]
