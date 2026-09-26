"""Build the Halfmile logo SVGs from pure geometry (no fonts needed).

Run:  python3 clothing-brand/halfmile/tools/build_logos.py
Writes clothing-brand/halfmile/logo/*.svg and prints nothing on success.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "logo"

CHALK, ASPHALT, BLUE, YELLOW = "#F2F1EC", "#1C1E20", "#2F4FD8", "#F2C230"

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


def mark(ink, split, size=64):
    """The Split: a running track seen from above. The left half of the track
    is solid (distance covered), the right half is drawn as lane edges only
    (distance to go), and the accent line marks the halfway point."""
    h = size
    w = h * 2.1
    t = h * 0.24                     # track width
    lw = h * 0.055                   # lane-edge line weight
    r = h / 2
    ri = r - t
    half = w / 2
    ring = (f"M{r},0H{w - r}A{r},{r} 0 0 1 {w - r},{h}H{r}A{r},{r} 0 0 1 {r},0z"
            f"M{r},{t}A{ri},{ri} 0 0 0 {r},{h - t}H{w - r}A{ri},{ri} 0 0 0 {w - r},{t}z")
    return (f'<defs><clipPath id="hmL"><rect x="0" y="0" width="{half}" height="{h}"/></clipPath>'
            f'<clipPath id="hmR"><rect x="{half}" y="0" width="{half}" height="{h}"/></clipPath></defs>'
            f'<path d="{ring}" fill="{ink}" fill-rule="evenodd" clip-path="url(#hmL)"/>'
            f'<g clip-path="url(#hmR)" fill="none" stroke="{ink}" stroke-width="{lw}">'
            f'<rect x="{lw / 2}" y="{lw / 2}" width="{w - lw}" height="{h - lw}" rx="{r - lw / 2}"/>'
            f'<rect x="{t - lw / 2}" y="{t - lw / 2}" width="{w - 2 * t + lw}" height="{h - 2 * t + lw}" rx="{ri + lw / 2}"/>'
            f'</g>'
            f'<rect x="{half - lw}" y="0" width="{lw * 2}" height="{t}" fill="{split}"/>'
            f'<rect x="{half - lw}" y="{h - t}" width="{lw * 2}" height="{t}" fill="{split}"/>'), w, h


def svg(inner, w, h, pad, bg=None, title="Halfmile"):
    vb = f"{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}"
    bgr = f'<rect x="{-pad}" y="{-pad}" width="{w + 2 * pad}" height="{h + 2 * pad}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
            f'width="{(w + 2 * pad) * 2:.0f}" height="{(h + 2 * pad) * 2:.0f}" role="img">'
            f"<title>{title}</title>{bgr}{inner}</svg>\n")


def main():
    OUT.mkdir(exist_ok=True)
    variants = {
        # transparent backgrounds, so every file can go straight to a printer
        "on-dark": (CHALK, YELLOW, None),
        "on-light": (ASPHALT, BLUE, None),
        "mono-black": (ASPHALT, ASPHALT, None),
        "mono-white": (CHALK, CHALK, None),
    }
    for name, (ink, split, bg) in variants.items():
        body, w = wordmark(ink, split)
        (OUT / f"wordmark-{name}.svg").write_text(svg(body, w, H, 24, bg, "Halfmile wordmark"))
        m, mw, mh = mark(ink, split)
        (OUT / f"mark-{name}.svg").write_text(svg(m, mw, mh, 12, bg, "Halfmile Split mark"))
        # stacked lockup: mark centred over the wordmark
        scale = 0.9
        mw2 = mw * scale
        lock = (f'<g transform="translate({(w - mw2 * 1.6) / 2},0) scale({scale * 1.6})">{m}</g>'
                f'<g transform="translate(0,{mh * scale * 1.6 + 36})">{body}</g>')
        lh = mh * scale * 1.6 + 36 + H
        (OUT / f"lockup-{name}.svg").write_text(svg(lock, w, lh, 32, bg, "Halfmile lockup"))


if __name__ == "__main__":
    main()
