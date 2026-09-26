"""Build the UNRESTD graffiti tag as pure vector SVG (no font needed to open it).

Library used by build_logos.py, which writes the logo files.

The letters start from Sedgwick Ave Display (SIL Open Font License, which
allows logos made from it) and are converted to outlines. Each letter gets a
small lift so the tag reads as hand-thrown rather than typed. The whole tag leans up 6 degrees. Underneath, a brass underline
swoosh ends in a single drip.
"""
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "fonts" / "SedgwickAveDisplay-400.woff2"
OUT = ROOT / "logo"

BLACK, BRASS, BONE = "#121212", "#B58B4C", "#EEEBE3"

# per-letter hand feel: (lift in px, tilt in degrees, extra gap in px; negative gap = overlap)
# kept subtle: the approved sketch had none, so this only adds a little hand feel
FEEL = {
    "U": (0, 0, 0), "N": (-2, 0, -2), "R": (1, 0, -2), "E": (-2, 0, -2),
    "S": (1, 0, -2), "T": (-3, 0, -2), "D": (-1, 0, 0),
}
SIZE = 170        # font size in px
LEAN = -6         # whole tag leans up to the right


def letters(text="UNRESTD"):
    """Return [(path d, x, advance, bounds)] laid out left to right, in px."""
    font = TTFont(FONT)
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    s = SIZE / font["head"].unitsPerEm
    out, x = [], 0.0
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (s, 0, 0, -s, 0, 0)))   # flip y for SVG
        bp = BoundsPen(gs)
        gs[name].draw(TransformPen(bp, (s, 0, 0, -s, 0, 0)))
        adv = gs[name].width * s
        lift, tilt, gap = FEEL.get(ch, (0, 0, 0))
        out.append((pen.getCommands(), x, lift, tilt, bp.bounds))
        x += adv + gap
    return out, x


def tag_body(ink, accent, outline=None, shadow=None, text="UNRESTD"):
    """The tag as an SVG group, drawn so its visual box starts near (0, 0)."""
    ls, width = letters(text)
    glyphs = []
    for d, x, lift, tilt, (x0, y0, x1, y1) in ls:
        cx, cy = x + (x0 + x1) / 2, (y0 + y1) / 2
        glyphs.append(f'<path d="{d}" transform="translate({x:.1f},{lift}) rotate({tilt} {cx - x:.1f} {cy:.1f})"/>')
    g = "".join(glyphs)
    # brass underline: a marker swoosh tight under the letters, rising to the right,
    # with one drip hanging near the end (same geometry as the approved sketch)
    under = (f'<path d="M10,30 C{width * 0.37:.0f},12 {width * 0.71:.0f},16 {width + 10:.0f},6" '
             f'fill="none" stroke="{accent}" stroke-width="11" stroke-linecap="round"/>')
    dx = width * 0.905
    drip = (f'<path d="M{dx:.0f},12 v34" stroke="{accent}" stroke-width="6" stroke-linecap="round"/>'
            f'<circle cx="{dx:.0f}" cy="54" r="6" fill="{accent}"/>')
    ink_drips = ""
    layers = ""
    if shadow:   # 3D block shadow for big back prints
        layers += f'<g fill="{shadow}" transform="translate(7,7)">{g}</g>'
    if outline:
        layers += f'<g fill="none" stroke="{outline}" stroke-width="10" stroke-linejoin="round">{g}</g>'
    layers += f'<g fill="{ink}">{g}</g>{ink_drips}'
    body = f'<g transform="rotate({LEAN} {width / 2:.0f} {-SIZE * 0.3:.0f})">{layers}{under}{drip}</g>'
    return body, width


def box(width):
    """Padding box (x, y, w, h) that contains the leaning tag, the underline and the drip."""
    return (-30, -SIZE * 1.05 - 20, width + 60, SIZE * 1.05 + 20 + 120)


if __name__ == "__main__":
    import build_logos
    build_logos.main()
