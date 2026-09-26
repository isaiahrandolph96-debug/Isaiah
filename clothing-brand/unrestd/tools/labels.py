"""UNRESTD labels and packaging: neck label, care label, hang tag, sticker, mailer.

Each function returns a complete SVG string. The care label carries the details
US law requires on textile products (fibre content, country of origin, the
maker's identity or RN number, care instructions); blanks ("____") are for
the factory's details.
"""
from build_logos import tag, mark, BLACK, FADED, TAN, BRASS, BONE
from garments import FONT_CSS, placed_svg

KRAFT = "#C9AE83"
M = 'class="m"'


def svg(w, h, inner, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
            f'<style>{FONT_CSS}</style>{inner}</svg>')


def neck_label(size="L"):
    """Woven neck label, black damask, folded at both ends."""
    inner = (f'<rect x="10" y="10" width="300" height="110" rx="4" fill="{BLACK}"/>'
             f'<rect x="10" y="10" width="14" height="110" fill="#000" opacity=".35"/>'
             f'<rect x="296" y="10" width="14" height="110" fill="#000" opacity=".35"/>'
             + placed_svg(tag(BONE), 36, 22, 180)
             + f'<rect x="232" y="36" width="1.5" height="58" fill="{BONE}" opacity=".35"/>'
             f'<text {M} x="266" y="80" font-size="40" fill="{BONE}" text-anchor="middle">{size}</text>')
    return svg(320, 130, inner, "Neck label")


def care_label():
    lines = ["SHIFT JACKET", "LOT 001 / 040", "", "SHELL 100% COTTON DUCK", "BODY LINING 100% ACRYLIC",
             "SLEEVE LINING 100% NYLON", "COLLAR 100% COTTON CORD", "", "MADE IN ________", "RN ________", "",
             "MACHINE WASH COLD", "INSIDE OUT, LIKE COLOURS", "DO NOT BLEACH", "TUMBLE DRY LOW", "COOL IRON",
             "", "GETS BETTER WITH WEAR."]
    t = "".join(f'<text {M} x="110" y="{150 + i * 16}" font-size="10.5" fill="{BLACK}" text-anchor="middle">{l}</text>'
                for i, l in enumerate(lines) if l)
    inner = (f'<path d="M10,10 H210 V440 L110,462 L10,440 Z" fill="#F7F5F0" stroke="rgba(0,0,0,.18)"/>'
             + placed_svg(tag(BLACK, accent=BLACK), 40, 30, 140)
             + f'<rect x="50" y="122" width="120" height="1" fill="{BLACK}" opacity=".4"/>' + t)
    return svg(220, 472, inner, "Care label")


def hang_tag():
    """Kraft hang tag, front and back, with a brass eyelet and black string."""
    def card(x, content):
        return (f'<g transform="translate({x},20)">'
                f'<path d="M0,26 L26,0 H214 L240,26 V400 H0 Z" fill="{KRAFT}" stroke="rgba(0,0,0,.2)"/>'
                f'<circle cx="120" cy="30" r="11" fill="{BRASS}"/><circle cx="120" cy="30" r="6" fill="#6b5a3e"/>'
                f'{content}</g>')
    front = (placed_svg(tag(BLACK), 18, 110, 204)
             + f'<text {M} x="120" y="330" font-size="13" fill="{BLACK}" text-anchor="middle">NOT DONE YET</text>'
             + f'<text {M} x="120" y="352" font-size="11" fill="{BLACK}" text-anchor="middle" opacity=".7">DROP 01 · FIRST SHIFT</text>')
    story = ["UNRESTED,", "with the E", "taken out.", "", "We didn't stop", "for it.", "", "Made for the", "night shift,",
             "the 5 a.m. start,", "the business you", "build after work."]
    back = ("".join(f'<text {M} x="26" y="{90 + i * 19}" font-size="13" fill="{BLACK}">{l}</text>'
                    for i, l in enumerate(story) if l)
            + f'<rect x="26" y="336" width="188" height="1" fill="{BLACK}" opacity=".4"/>'
            + f'<text {M} x="26" y="364" font-size="12" fill="{BLACK}">LOT 001 / 040</text>'
            + f'<text {M} x="214" y="364" font-size="12" fill="{BLACK}" text-anchor="end">SIZE L</text>')
    string = f'<path d="M140,50 C170,-10 290,-10 400,50" fill="none" stroke="{BLACK}" stroke-width="3"/>'
    return svg(540, 440, string + card(20, front) + card(280, back), "Hang tag, front and back")


def sticker():
    """Slap sticker: bone vinyl, rounded corners, the tag and one line."""
    inner = (f'<defs><filter id="st-blur"><feGaussianBlur stdDeviation="5"/></filter></defs>'
             f'<rect x="26" y="30" width="440" height="230" rx="22" fill="#000" opacity=".35" filter="url(#st-blur)"/>'
             f'<rect x="20" y="20" width="440" height="230" rx="22" fill="{BONE}"/>'
             f'<rect x="34" y="34" width="412" height="202" rx="14" fill="none" stroke="{BLACK}" stroke-width="3"/>'
             + placed_svg(tag(BLACK), 60, 40, 360)
             + f'<text {M} x="240" y="220" font-size="15" fill="{BLACK}" text-anchor="middle" letter-spacing="4">NOT DONE YET</text>')
    return svg(490, 280, inner, "Slap sticker")


def mailer():
    """Black mailer box, top view, with the tag, a brass lot sticker and the tape line."""
    inner = (f'<rect x="20" y="20" width="560" height="380" rx="8" fill="#1B1B1A"/>'
             f'<rect x="20" y="20" width="560" height="380" rx="8" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="2"/>'
             f'<path d="M20,70 H580" stroke="rgba(255,255,255,.08)" stroke-width="2"/>'
             f'<path d="M270,20 h60 v50 h-60 z" fill="rgba(255,255,255,.04)"/>'
             + placed_svg(tag(BONE), 130, 120, 340)
             + f'<circle cx="500" cy="340" r="36" fill="{BRASS}"/>'
             f'<text {M} x="500" y="334" font-size="11" fill="{BLACK}" text-anchor="middle">LOT</text>'
             f'<text {M} x="500" y="352" font-size="15" fill="{BLACK}" text-anchor="middle">001</text>'
             f'<text {M} x="60" y="372" font-size="12" fill="{BONE}" opacity=".6">WHILE YOU SLEPT, THIS WAS PACKED.</text>')
    return svg(600, 420, inner, "Mailer box, top view")


def all_labels():
    return [
        ("neck-label", "Woven neck label", "Black damask, folded at both ends. Tag and size.", neck_label()),
        ("care-label", "Care label", "White satin, left inside side seam. Fibre, origin, RN, care, lot number.", care_label()),
        ("hang-tag", "Hang tag", "Kraft card, brass eyelet. Front: the tag. Back: the story and the lot number.", hang_tag()),
        ("sticker", "Slap sticker", "One in every order. People put them on toolboxes, lockers and laptops, which is free advertising.", sticker()),
        ("mailer", "Mailer box", "Black board, tag printed in bone, brass lot sticker on the corner.", mailer()),
    ]
