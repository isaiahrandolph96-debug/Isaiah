"""Build the UNRESTD logo SVGs from pure geometry (no fonts needed).

Run:  python3 clothing-brand/unrestd/tools/build_logos.py
Writes clothing-brand/unrestd/logo/*.svg and prints nothing on success.

The name is UNRESTED with the E taken out. The wordmark marks the spot: a
brass bar stands where the missing E would be, between the T and the D.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "logo"

# Workwear palette: duck canvas, brass hardware, a bone tee underneath
BLACK, FADED, TAN, MOSS, BRASS, BONE, CORD = (
    "#121212", "#3B3B39", "#C2A878", "#4A4F36", "#B58B4C", "#EEEBE3", "#5A3E2B")

H, S, W, GAP = 100, 24, 62, 10   # cap height, stroke, letter width, letter gap
C = 22                           # chamfer size
NAME = "UNREST|D"                # "|" is where the brass bar goes


def rects(*rs):
    return "".join(f"M{x},{y}h{w}v{h}h{-w}z" for x, y, w, h in rs)


def letter(ch):
    """Return (path data, fill rule, advance width) for one squared capital.
    Rect unions use nonzero; shapes with a counter use evenodd."""
    if ch == "U":
        return (f"M0,0H{S}V{H - S}H{W - S}V0H{W}V{H - C}L{W - C},{H}H{C}L0,{H - C}z", "nonzero", W)
    if ch == "N":
        nw, t = 84, 18            # wider than the rest so the diagonal has room
        d = rects((0, 0, S, H), (nw - S, 0, S, H)) + \
            f"M{S - 2},0H{S + t}L{nw - S + 2},{H}H{nw - S - t}z"
        return d, "nonzero", nw
    if ch == "R":
        d = (f"M0,{H}V0H{W - C}L{W},{C}V50L{W - 10},58L{W},66V{H}H{W - S}V70H{S}V{H}z"
             f"M{S},{S}V46H{W - S}V{S}z")
        return d, "evenodd", W
    if ch == "E":
        return rects((0, 0, S, H), (0, 0, W - 2, S), (0, 40, W - 10, 21), (0, H - S, W - 2, S)), "nonzero", W - 2
    if ch == "S":
        d = (f"M{C},0H{W}V{S}H{S}V38H{W - C}L{W},{38 + C}V{H}H0V{H - S}H{W - S}V62H{C}L0,{62 - C}V{C}z")
        return d, "nonzero", W
    if ch == "T":
        return rects((0, 0, W, S), (W / 2 - S / 2, 0, S, H)), "nonzero", W
    if ch == "D":
        d = (f"M0,0H{W - C}L{W},{C}V{H - C}L{W - C},{H}H0z"
             f"M{S},{S}V{H - S}H{W - S}V{S}z")
        return d, "evenodd", W
    raise ValueError(ch)


def glyph(ch, x):
    d, rule, w = letter(ch)
    return f'<path transform="translate({x},0)" d="{d}" fill-rule="{rule}"/>', w


def wordmark(ink, split, text=NAME):
    """Return (svg body, width, x of the bar's centre)."""
    parts, x, bar = [], 0, None
    for ch in text:
        if ch == "|":
            bar = x + 4
            x = bar + 6 + 14
            continue
        p, w = glyph(ch, x)
        parts.append(p)
        x += w + GAP
    body = f'<g fill="{ink}">{"".join(parts)}</g>'
    if bar is not None:
        body += f'<rect x="{bar}" y="-14" width="6" height="{H + 28}" fill="{split}"/>'
    return body, x - GAP, (bar + 3 if bar is not None else None)


def monogram(ink, split):
    """U|D: the first and last letters around the brass bar. For tee chests,
    beanie cuffs and inside collars."""
    body, w, _ = wordmark(ink, split, "U|D")
    return body, w


def patch(bg, ink, split, stitch):
    """The woven tab: a wide stitched rectangle carrying the wordmark.
    Deliberately wide (about 3:1), never square."""
    body, w, _ = wordmark(ink, split)
    px, py = 70, 46
    W2, H2 = w + 2 * px, H + 2 * py
    return (f'<rect x="0" y="0" width="{W2}" height="{H2}" rx="10" fill="{bg}"/>'
            f'<rect x="16" y="16" width="{W2 - 32}" height="{H2 - 32}" rx="4" fill="none" '
            f'stroke="{stitch}" stroke-width="5" stroke-dasharray="16 10"/>'
            f'<g transform="translate({px},{py})">{body}</g>'), W2, H2


def svg(inner, w, h, pad, title="UNRESTD"):
    vb = f"{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
            f'width="{(w + 2 * pad) * 2:.0f}" height="{(h + 2 * pad) * 2:.0f}" role="img">'
            f"<title>{title}</title>{inner}</svg>\n")


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
        body, w, _ = wordmark(ink, split)
        (OUT / f"wordmark-{name}.svg").write_text(svg(body, w, H, 24, "UNRESTD wordmark"))
        body, w = monogram(ink, split)
        (OUT / f"monogram-{name}.svg").write_text(svg(body, w, H, 20, "UNRESTD monogram"))
    for name, cols in {"black": (BLACK, BONE, BRASS, BONE), "tan": (TAN, BLACK, BRASS, BLACK)}.items():
        body, w, h = patch(*cols)
        (OUT / f"woven-tab-{name}.svg").write_text(svg(body, w, h, 0, "UNRESTD woven tab"))


if __name__ == "__main__":
    main()
