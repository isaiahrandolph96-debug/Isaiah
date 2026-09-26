"""Build the UNRESTD logo files: the graffiti tag, the short UD mark and the woven tabs.

Run:  python3 clothing-brand/unrestd/tools/build_logos.py
Writes clothing-brand/unrestd/logo/*.svg (transparent backgrounds, pure vector).

The tag itself is drawn in build_tag.py. Every function here returns
(svg body, width, height) with the origin at the top-left corner, so garments
and pages can place it like an image.
"""
from pathlib import Path

from build_tag import tag_body, box

OUT = Path(__file__).resolve().parent.parent / "logo"

# Workwear palette: duck canvas, brass hardware, a bone tee underneath
BLACK, FADED, TAN, MOSS, BRASS, BONE, CORD = (
    "#121212", "#3B3B39", "#C2A878", "#4A4F36", "#B58B4C", "#EEEBE3", "#5A3E2B")


def _boxed(body, width):
    x, y, w, h = box(width)
    return f'<g transform="translate({-x:.1f},{-y:.1f})">{body}</g>', w, h


def tag(ink, accent=BRASS, outline=None, shadow=None):
    """The full UNRESTD tag with the brass swoosh and drip."""
    return _boxed(*tag_body(ink, accent, outline, shadow))


def mark(ink, accent=BRASS):
    """UD: the short tag for tee chests, beanie cuffs and inside collars."""
    return _boxed(*tag_body(ink, accent, text="UD"))


def patch(bg, ink, accent, stitch):
    """The woven tab: a wide stitched rectangle carrying the tag.
    Deliberately wide (about 2.5:1), never square."""
    body, w, h = tag(ink, accent)
    px, py = 50, 20
    W2, H2 = w + 2 * px, h + 2 * py
    return (f'<rect x="0" y="0" width="{W2:.0f}" height="{H2:.0f}" rx="14" fill="{bg}"/>'
            f'<rect x="20" y="20" width="{W2 - 40:.0f}" height="{H2 - 40:.0f}" rx="6" fill="none" '
            f'stroke="{stitch}" stroke-width="6" stroke-dasharray="18 12"/>'
            f'<g transform="translate({px},{py})">{body}</g>'), W2, H2


def svg(inner, w, h, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'width="{w * 2:.0f}" height="{h * 2:.0f}" role="img"><title>{title}</title>{inner}</svg>\n')


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    tags = {
        "bone": dict(ink=BONE),                                   # on black, faded black, moss
        "black": dict(ink=BLACK),                                 # on bone and duck tan
        "mono-bone": dict(ink=BONE, accent=BONE),
        "mono-black": dict(ink=BLACK, accent=BLACK),
        "3d-bone": dict(ink=BONE, outline=BLACK, shadow=BRASS),   # big back prints on black
        "3d-black": dict(ink=BLACK, outline=BONE, shadow=BRASS),  # big back prints on tan and bone
    }
    for name, kw in tags.items():
        (OUT / f"tag-{name}.svg").write_text(svg(*tag(**kw), "UNRESTD tag"))
    for name, kw in {"bone": dict(ink=BONE), "black": dict(ink=BLACK),
                     "tonal-faded": dict(ink=FADED, accent=FADED)}.items():
        (OUT / f"mark-ud-{name}.svg").write_text(svg(*mark(**kw), "UNRESTD UD mark"))
    for name, cols in {"black": (BLACK, BONE, BRASS, BONE), "tan": (TAN, BLACK, BRASS, BLACK)}.items():
        (OUT / f"woven-tab-{name}.svg").write_text(svg(*patch(*cols), "UNRESTD woven tab"))


if __name__ == "__main__":
    main()
