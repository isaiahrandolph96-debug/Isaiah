"""Build the Halfmile logo SVGs from pure geometry (no fonts needed).

Run:  python3 clothing-brand/halfmile/tools/build_logos.py
Writes clothing-brand/halfmile/logo/*.svg and prints nothing on success.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "logo"

# Workwear palette (v2): duck canvas, brass hardware, a bone tee underneath
BLACK, FADED, TAN, MOSS, BRASS, BONE, CORD = (
    "#121212", "#3B3B39", "#C2A878", "#4A4F36", "#B58B4C", "#EEEBE3", "#5A3E2B")

H, S, W, GAP = 100, 24, 62, 10   # cap height, stroke, letter width, letter gap
C = 22                           # chamfer on the tops of A and M


def rects(*rs):
    return "".join(f"M{x},{y}h{w}v{h}h{-w}z" for x, y, w, h in rs)


def letter(ch, x):
    """Return (path data, advance width) for one squared athletic capital."""
    if ch == "H":
        d = rects((0, 0, S, H), (W - S, 0, S, H), (0, 38, W, S))
        w = W
    elif ch == "A":
        mt, mb = 50, 70
        d = (f"M0,{H}V{C}L{C},0H{W - C}L{W},{C}V{H}H{W - S}V{mb}H{S}V{H}z"
             f"M{S},{S}V{mt}H{W - S}V{S}z")
        w = W
    elif ch == "L":
        d = rects((0, 0, S, H), (0, H - S, W - 4, S))
        w = W - 4
    elif ch == "F":
        d = rects((0, 0, S, H), (0, 0, W - 2, S), (0, 42, W - 12, 21))
        w = W - 2
    elif ch == "M":
        mw, stem, sb = 94, 20, 72
        d = (f"M0,{H}V{C}L{C},0H{mw - C}L{mw},{C}V{H}H{mw - S}V{S}"
             f"H{mw / 2 + stem / 2}V{sb}H{mw / 2 - stem / 2}V{S}H{S}V{H}z")
        w = mw
    elif ch == "I":
        d = rects((0, 0, S, H))
        w = S
    elif ch == "E":
        d = rects((0, 0, S, H), (0, 0, W - 2, S), (0, 40, W - 10, 21), (0, H - S, W - 2, S))
        w = W - 2
    else:
        raise ValueError(ch)
    rule = "evenodd" if ch in "AM" else "nonzero"   # rect unions must not XOR
    return f'<path transform="translate({x},0)" d="{d}" fill-rule="{rule}"/>', w


def wordmark(ink, split):
    """HALF | MILE with a thin split line where the half-mile mark falls."""
    parts, x = [], 0
    for ch in "HALF":
        p, w = letter(ch, x)
        parts.append(p)
        x += w + GAP
    split_x = x + 4
    x = split_x + 6 + 14
    for ch in "MILE":
        p, w = letter(ch, x)
        parts.append(p)
        x += w + GAP
    total = x - GAP
    body = (f'<g fill="{ink}">{"".join(parts)}</g>'
            f'<rect x="{split_x}" y="-14" width="6" height="{H + 28}" fill="{split}"/>')
    return body, total


def monogram(ink, split):
    """H | M: the two outer letters of the wordmark around the split line.
    Small enough to embroider on a tee chest or a beanie cuff."""
    h, hw = letter("H", 0)
    m, mw = letter("M", 0)
    sx = hw + 12
    body = (f'<g fill="{ink}">{h}<g transform="translate({sx + 6 + 12},0)">{m}</g></g>'
            f'<rect x="{sx}" y="-12" width="6" height="{H + 24}" fill="{split}"/>')
    return body, sx + 6 + 12 + mw


def patch(bg, ink, split, stitch):
    """The woven tab: a wide stitched rectangle carrying the wordmark.
    Deliberately wide (about 3:1), never square."""
    body, w = wordmark(ink, split)
    px, py = 70, 46
    W2, H2 = w + 2 * px, H + 2 * py
    return (f'<rect x="0" y="0" width="{W2}" height="{H2}" rx="10" fill="{bg}"/>'
            f'<rect x="16" y="16" width="{W2 - 32}" height="{H2 - 32}" rx="4" fill="none" '
            f'stroke="{stitch}" stroke-width="5" stroke-dasharray="16 10"/>'
            f'<g transform="translate({px},{py})">{body}</g>'), W2, H2


def svg(inner, w, h, pad, bg=None, title="Halfmile"):
    vb = f"{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}"
    bgr = f'<rect x="{-pad}" y="{-pad}" width="{w + 2 * pad}" height="{h + 2 * pad}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
            f'width="{(w + 2 * pad) * 2:.0f}" height="{(h + 2 * pad) * 2:.0f}" role="img">'
            f"<title>{title}</title>{bgr}{inner}</svg>\n")


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    # transparent backgrounds, so every file can go straight to a printer or embroiderer
    variants = {
        "bone": (BONE, BRASS),       # for black, faded black and moss garments
        "black": (BLACK, BRASS),     # for bone and tan garments
        "mono-black": (BLACK, BLACK),
        "mono-bone": (BONE, BONE),
    }
    for name, (ink, split) in variants.items():
        body, w = wordmark(ink, split)
        (OUT / f"wordmark-{name}.svg").write_text(svg(body, w, H, 24, None, "Halfmile wordmark"))
        body, w = monogram(ink, split)
        (OUT / f"monogram-{name}.svg").write_text(svg(body, w, H, 20, None, "Halfmile monogram"))
    for name, cols in {"black": (BLACK, BONE, BRASS, BONE), "tan": (TAN, BLACK, BRASS, BLACK)}.items():
        body, w, h = patch(*cols)
        (OUT / f"woven-tab-{name}.svg").write_text(svg(body, w, h, 0, None, "Halfmile woven tab"))


if __name__ == "__main__":
    main()
