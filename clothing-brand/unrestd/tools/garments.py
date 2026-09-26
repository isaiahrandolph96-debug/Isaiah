"""UNRESTD Drop 01 "First Shift": artwork and flat garment mockups, as SVG strings.

Artwork uses Archivo (condensed, 900) and IBM Plex Mono, so render it in a
browser (tools/render.js) to get PNGs. Font sizes in fit() calls were measured
in that browser so each line sets 300 wide without distorting the letters.
"""
from build_logos import wordmark, monogram, patch, H, BLACK, FADED, TAN, MOSS, BRASS, BONE, CORD

FONT_CSS = ("@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900"
            "&family=IBM+Plex+Mono:wght@500;600&display=swap');"
            ".d{font-family:Archivo,'Arial Narrow',sans-serif;font-weight:900;font-stretch:62%;"
            "font-variation-settings:'wdth' 62}"
            ".m{font-family:'IBM Plex Mono',ui-monospace,monospace;font-weight:600}")


# ---------- artwork (each drawn in a 300 x 360 print box) ----------

def fit(text, size, y, ink):
    return (f'<text class="d" x="0" y="{y}" font-size="{size}" textLength="300" '
            f'lengthAdjust="spacing" fill="{ink}">{text}</text>')


def rules(y, ink, n=3):
    return "".join(f'<rect x="0" y="{y + i * 12}" width="300" height="5" fill="{ink}"/>' for i in range(n))


def art_tee_back(ink=BLACK, accent=BRASS):
    """Bone Shift Tee, back: the night-shift line."""
    return (fit("WHILE YOU", 74.6, 56, ink) + fit("SLEPT.", 120.9, 157, ink)
            + rules(180, accent)
            + f'<text class="m" x="0" y="238" font-size="15" fill="{ink}">FIRST SHIFT / DROP 01</text>'
            + f'<text class="m" x="300" y="238" font-size="15" fill="{ink}" text-anchor="end">UNRESTD</text>')


def art_hoodie_back(ink=BLACK, accent=BRASS):
    """Split Zip Hoodie, back: the tagline, stacked."""
    return (fit("NOT DONE", 82.0, 61, ink) + fit("YET.", 188.6, 211, ink)
            + rules(234, accent)
            + f'<text class="m" x="0" y="292" font-size="15" fill="{ink}">REST LATER</text>'
            + f'<text class="m" x="300" y="292" font-size="15" fill="{ink}" text-anchor="end">UNRESTD</text>')


# ---------- placing marks ----------

def placed(art, x, y, w):
    """Place a 300x360 artwork box at (x, y) scaled to width w."""
    return f'<g transform="translate({x},{y}) scale({w / 300})">{art}</g>'


def placed_logo(fn, cols, x, y, w):
    body, lw = fn(*cols)[:2]
    return f'<g transform="translate({x},{y}) scale({w / lw})">{body}</g>'


def placed_tab(cols, x, y, w):
    body, tw, _ = patch(*cols)
    return f'<g transform="translate({x},{y}) scale({w / tw})">{body}</g>'


def split_monogram(ink, cx, y, w):
    """U|D sized so the brass-bar gap sits exactly on a zipper at x = cx:
    U on one side of the zip, D on the other."""
    body, ww, bar = wordmark(ink, "none", "U|D")
    s = w / ww
    return f'<g transform="translate({cx - bar * s},{y}) scale({s})">{body}</g>'


# ---------- garments ----------

LINE = "rgba(0,0,0,.42)"
SHADE = "rgba(0,0,0,.18)"
LIGHT = "rgba(255,255,255,.16)"


def svg(vb, inner, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{label}">'
            f'<style>{FONT_CSS}</style>{inner}</svg>')


def stitch(d, dark):
    """Contrast triple-stitching: the workwear detail."""
    col = "rgba(238,235,227,.35)" if dark else "rgba(0,0,0,.35)"
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.4" stroke-dasharray="4 3"/>'


def zipper(x, y1, y2):
    return (f'<path d="M{x},{y1} V{y2}" stroke="{BRASS}" stroke-width="4"/>'
            f'<path d="M{x},{y1} V{y2}" stroke="rgba(0,0,0,.35)" stroke-width="1.2" stroke-dasharray="2 2"/>'
            f'<rect x="{x - 4}" y="{y2 - 26}" width="8" height="22" rx="2" fill="{BRASS}" stroke="rgba(0,0,0,.4)"/>')


def work_jacket(fill, collar, tab_cols, label="Shift Jacket"):
    """Cropped duck canvas work jacket: cord collar, brass zip, blanket lining."""
    dark = fill in (BLACK, FADED, MOSS)
    body = ("M150,52 L92,68 C72,74 62,90 58,114 L30,392 L80,402 L104,186 L104,362 L336,362 "
            "L336,186 L360,402 L410,392 L382,114 C378,90 368,74 348,68 L290,52 Z")
    inner = (
        f'<path d="{body}" fill="{fill}" stroke="{LINE}" stroke-width="2" stroke-linejoin="round"/>'
        # waistband and cuffs
        f'<g fill="{fill}" stroke="{LINE}" stroke-width="2">'
        '<rect x="102" y="358" width="236" height="36" rx="2"/>'
        '<path d="M30,392 L80,402 L76,430 L26,420 Z"/><path d="M410,392 L360,402 L364,430 L414,420 Z"/></g>'
        f'<rect x="102" y="358" width="236" height="36" fill="{SHADE}" opacity=".5"/>'
        # blanket lining peeking at the open neck
        '<path d="M178,54 L220,112 L262,54 Z" fill="#8C2F2B" opacity=".9"/>'
        '<path d="M186,54 L220,100 L254,54" fill="none" stroke="#2A2A2A" stroke-width="2" opacity=".5"/>'
        # collar (corduroy)
        f'<g fill="{collar}" stroke="{LINE}" stroke-width="2" stroke-linejoin="round">'
        '<path d="M220,46 L150,50 L130,66 L178,118 L216,62 Z"/><path d="M220,46 L290,50 L310,66 L262,118 L224,62 Z"/></g>'
        '<g stroke="rgba(0,0,0,.22)" stroke-width="1">'
        + "".join(f'<path d="M{140 + i * 7},{60 + i * 5} L{176 + i * 4},{104 - i * 3}"/>' for i in range(5))
        + "".join(f'<path d="M{300 - i * 7},{60 + i * 5} L{264 - i * 4},{104 - i * 3}"/>' for i in range(5))
        + '</g>'
        + zipper(220, 112, 392)
        # chest zip pocket (wearer's left) and the woven tab under it
        + f'<path d="M248,150 H320" stroke="{BRASS}" stroke-width="3"/>'
        + stitch("M244,144 H324 V156 H244 Z", dark)
        + placed_tab(tab_cols, 252, 166, 64)
        # slash hand pockets
        + f'<path d="M126,246 L146,318" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>'
        + f'<path d="M314,246 L294,318" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>'
        + stitch("M92,70 Q106,120 104,186", dark) + stitch("M348,70 Q334,120 336,186", dark)
        + stitch("M106,366 H334", dark) + stitch("M106,386 H334", dark)
        + stitch("M150,56 L150,360", dark) + stitch("M290,56 L290,360", dark)
    )
    return svg("0 30 440 410", inner, label)


def active_jacket(fill, tab_cols, label="Night Shift Jacket"):
    """Hooded duck canvas jacket: quilted lining, knit cuffs and waistband."""
    dark = fill in (BLACK, FADED, MOSS)
    body = ("M150,62 L86,84 C62,92 50,110 46,140 L20,396 L72,406 L98,200 L98,372 L342,372 "
            "L342,200 L368,406 L420,396 L394,140 C390,110 378,92 354,84 L290,62 Z")
    ribs = "".join(f'<path d="M{x},376 V404"/>' for x in range(104, 340, 6))
    inner = (
        f'<path d="{body}" fill="{fill}" stroke="{LINE}" stroke-width="2" stroke-linejoin="round"/>'
        # hood, with the quilted lining showing inside
        f'<path d="M150,62 C136,-6 304,-6 290,62 C282,102 158,102 150,62 Z" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
        '<path d="M170,60 C176,16 264,16 270,60 C260,90 180,90 170,60 Z" fill="#2B2B2B"/>'
        '<g stroke="rgba(255,255,255,.12)" stroke-width="1" fill="none">'
        '<path d="M180,30 L250,80"/><path d="M200,22 L262,66"/><path d="M178,54 L224,86"/>'
        '<path d="M260,30 L190,80"/><path d="M240,22 L178,66"/><path d="M262,54 L216,86"/></g>'
        # knit cuffs and waistband
        f'<g fill="{BLACK}" stroke="{LINE}" stroke-width="2">'
        '<rect x="98" y="372" width="244" height="36"/>'
        '<path d="M20,396 L72,406 L68,440 L16,430 Z"/><path d="M420,396 L368,406 L372,440 L424,430 Z"/></g>'
        f'<g stroke="{LIGHT}" stroke-width="1.5">{ribs}</g>'
        + zipper(220, 92, 406)
        # chest patch pocket with the tab
        + f'<rect x="246" y="138" width="70" height="62" fill="{fill}" stroke="{LINE}" stroke-width="1.5"/>'
        + stitch("M250,142 H312 V196 H250 Z", dark)
        + placed_tab(tab_cols, 249, 150, 64)
        # lower pockets with flaps
        + f'<g fill="{fill}" stroke="{LINE}" stroke-width="1.5"><rect x="118" y="270" width="78" height="80"/>'
        '<rect x="244" y="270" width="78" height="80"/></g>'
        + stitch("M122,274 H192 V346 H122 Z", dark) + stitch("M248,274 H318 V346 H248 Z", dark)
        + stitch("M86,86 Q100,140 98,200", dark) + stitch("M354,86 Q340,140 342,200", dark)
        + '<g stroke="rgba(238,235,227,.7)" stroke-width="3" stroke-linecap="round">'
          '<path d="M200,90 L196,150"/><path d="M240,90 L244,150"/></g>'
    )
    return svg("0 -8 440 460", inner, label)


def tee(fill, graphic="", back=False, label="T-shirt"):
    body = ("M138,22 C{a} L338,48 L396,132 L344,166 L314,128 L316,424 C240,432 160,432 84,424 "
            "L86,128 L56,166 L4,132 L62,48 Z").format(
        a="160,34 240,34 262,22" if back else "158,58 242,58 262,22")
    neck = "" if back else f'<path d="M138,22 C170,14 230,14 262,22 C242,58 158,58 138,22 Z" fill="{SHADE}"/>'
    rib = '<path d="M138,22 C{c}" fill="none" stroke="{l}" stroke-width="7" opacity=".5"/>'.format(
        c="160,34 240,34 262,22" if back else "158,58 242,58 262,22", l=LINE)
    seams = (f'<g fill="none" stroke="{LINE}" stroke-width="1.5">'
             '<path d="M72,46 Q92,90 86,128"/><path d="M328,46 Q308,90 314,128"/>'
             '<path d="M13,127 L61,158" stroke-dasharray="4 4"/><path d="M387,127 L339,158" stroke-dasharray="4 4"/>'
             '<path d="M86,414 C160,422 240,422 314,414" stroke-dasharray="4 4"/></g>')
    inner = (f'<path d="{body}" fill="{fill}" stroke="{LINE}" stroke-width="2" stroke-linejoin="round"/>'
             f'{neck}{rib}{seams}{graphic}')
    return svg("-10 0 420 440", inner, label)


def zip_hoodie(fill, graphic="", back=False, label="Zip hoodie"):
    body = ("M150,60 L84,84 C60,92 48,110 44,140 L18,400 L70,410 L96,200 L98,452 L342,452 L344,200 "
            "L370,410 L422,400 L396,140 C392,110 380,92 356,84 L290,60 Z")
    front = "" if back else (
        f'<path d="M172,58 C178,18 262,18 268,58 C258,88 182,88 172,58 Z" fill="{SHADE}"/>'
        + zipper(220, 86, 476)
        + f'<path d="M132,330 L150,420" stroke="{LINE}" stroke-width="3"/><path d="M308,330 L290,420" stroke="{LINE}" stroke-width="3"/>'
        + '<g stroke="rgba(0,0,0,.55)" stroke-width="3" stroke-linecap="round"><path d="M204,88 L198,168"/><path d="M236,88 L242,168"/></g>')
    hood = ('<path d="M150,60 C138,-4 302,-4 290,60 C280,40 160,40 150,60 Z"/>' if back else
            '<path d="M150,60 C138,-4 302,-4 290,60 C280,102 160,102 150,60 Z"/>')
    inner = (f'<path d="{body}" fill="{fill}" stroke="{LINE}" stroke-width="2" stroke-linejoin="round"/>'
             f'<g fill="{fill}" stroke="{LINE}" stroke-width="2">'
             '<path d="M18,400 L70,410 L66,442 L14,432 Z"/><path d="M422,400 L370,410 L374,442 L426,432 Z"/>'
             f'<rect x="98" y="448" width="244" height="28"/>{hood}</g>'
             + (f'<path d="M172,58 C178,18 262,18 268,58 C258,88 182,88 172,58 Z" fill="{SHADE}"/>' if not back else "")
             + f'<g stroke="{LINE}" stroke-width="1.5" fill="none"><path d="M104,462 H336" stroke-dasharray="4 4"/>'
             '<path d="M96,200 Q100,160 84,86"/><path d="M344,200 Q340,160 356,86"/></g>'
             f'{graphic}{front}')
    return svg("0 -10 440 494", inner, label)


def beanie(fill, graphic="", label="Beanie"):
    ribs = "".join(f'<path d="M{x},156 V238"/>' for x in range(52, 250, 9))
    inner = (f'<path d="M52,170 C52,40 248,40 248,170 Z" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
             f'<rect x="40" y="148" width="220" height="96" rx="12" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
             f'<g stroke="{LIGHT}" stroke-width="2">{ribs}</g>'
             f'{graphic}')
    return svg("20 30 260 230", inner, label)


# ---------- the Drop 01 line-up ----------

TAB_BLACK = (BLACK, BONE, BRASS, BONE)
TAB_TAN = (TAN, BLACK, BRASS, BLACK)


def products():
    return [
        dict(id="shift-jacket-black", svg=work_jacket(BLACK, "#1E1E1E", TAB_BLACK, "Shift Jacket, black")),
        dict(id="shift-jacket-tan", svg=work_jacket(TAN, CORD, TAB_BLACK, "Shift Jacket, duck tan")),
        dict(id="shift-jacket-faded", svg=work_jacket(FADED, "#2A2A29", TAB_BLACK, "Shift Jacket, faded black")),
        dict(id="night-shift-jacket", svg=active_jacket(BLACK, TAB_BLACK, "Night Shift Jacket, black")),
        dict(id="split-zip-hoodie", svg=zip_hoodie(TAN, split_monogram(BLACK, 220, 140, 110), label="Split Zip Hoodie, front")),
        dict(id="split-zip-hoodie-back", svg=zip_hoodie(TAN, placed(art_hoodie_back(), 130, 96, 180), back=True,
                                                         label="Split Zip Hoodie, back")),
        dict(id="shift-tee-black", svg=tee(BLACK, placed_logo(monogram, (FADED, FADED), 240, 96, 42),
                                           label="Shift Tee, black, tonal monogram")),
        dict(id="shift-tee-bone-back", svg=tee(BONE, placed(art_tee_back(), 110, 92, 180), back=True,
                                               label="Shift Tee, bone, back")),
        dict(id="watch-beanie", svg=beanie(BLACK, placed_tab(TAB_BLACK, 110, 180, 80), label="Watch Beanie")),
    ]


def print_files():
    """Back artwork at print-box proportions (Printful: 4500 x 5400 px)."""
    return [
        ("shift-tee-back", art_tee_back(), BONE),
        ("split-zip-hoodie-back", art_hoodie_back(), TAN),
    ]
