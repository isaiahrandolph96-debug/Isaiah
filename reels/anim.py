"""Story-driven animated backgrounds for Africa Blind Spot reels.

Each background is drawn per frame from primitives (no external assets), in the
reel palette: night-dark grounds, warm amber light, gold accents. Select one with
bg_spec {"anim": "<name>", ...}; if the spec also has "map", the map is drawn
first and the animation is layered on top of it.

    render(spec, p, t, base=None) -> RGB image
      p: progress through the scene (0-1), t: seconds since the scene started
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
GOLD = (212, 170, 52)
WARM = (255, 214, 130)
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def _font(size):
    return ImageFont.truetype(BOLD, size)


@lru_cache(maxsize=16)
def gradient(top, bottom, horizon=None, below=None):
    """Vertical gradient top->bottom (or top->horizon colour at y=horizon, then -> below)."""
    y = np.linspace(0, 1, H)[:, None]
    if horizon is None:
        g = np.array(top) * (1 - y) + np.array(bottom) * y
    else:
        hy = horizon / H
        a = np.clip(y / hy, 0, 1)
        sky = np.array(top) * (1 - a) + np.array(bottom) * a
        b = np.clip((y - hy) / (1 - hy), 0, 1)
        ground = np.array(below[0]) * (1 - b) + np.array(below[1]) * b
        g = np.where(y < hy, sky, ground)
    img = np.repeat(g[:, None, :], W, axis=1).reshape(H, W, 3)
    return Image.fromarray(img.astype(np.uint8)).convert("RGBA")


@lru_cache(maxsize=32)
def glow(radius, color, strength=1.0):
    """Soft radial glow sprite (RGBA)."""
    s = radius * 2
    y, x = np.ogrid[-radius:radius, -radius:radius]
    d = np.sqrt(x * x + y * y) / radius
    a = np.clip(1 - d, 0, 1) ** 2 * 255 * strength
    img = np.zeros((s, s, 4), np.uint8)
    img[..., :3] = color
    img[..., 3] = a.astype(np.uint8)
    return Image.fromarray(img)


def put_glow(img, x, y, radius, color, strength=1.0):
    g = glow(int(radius), tuple(color), round(strength, 2))
    img.alpha_composite(g, (int(x - radius), int(y - radius)))


def stars(img, t, n=140, top=0, bottom=900, seed=3):
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(img, "RGBA")
    xs, ys = rng.uniform(0, W, n), rng.uniform(top, bottom, n)
    ph, sp, sz = rng.uniform(0, 6.28, n), rng.uniform(1, 3, n), rng.choice([1, 1, 2, 2, 3], n)
    for x, y, a, s, r in zip(xs, ys, ph, sp, sz):
        al = int(90 + 110 * (0.5 + 0.5 * math.sin(t * s + a)))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(235, 230, 215, al))


def pylon(d, x, base, h, col, width=None, arms=True):
    """Lattice transmission tower silhouette. Returns the cable attachment points."""
    lw = width or max(2, int(h / 110))
    bw, tw = h * 0.30, h * 0.07
    top = base - h
    L0, R0 = (x - bw / 2, base), (x + bw / 2, base)
    L1, R1 = (x - tw / 2, top + h * 0.12), (x + tw / 2, top + h * 0.12)
    d.line([L0, L1], fill=col, width=lw)
    d.line([R0, R1], fill=col, width=lw)
    d.line([L1, (x, top), R1], fill=col, width=lw)
    # X bracing between the legs
    levels = 6
    for i in range(levels):
        f0, f1 = i / levels, (i + 1) / levels
        a = (L0[0] + (L1[0] - L0[0]) * f0, base - (base - L1[1]) * f0)
        b = (R0[0] + (R1[0] - R0[0]) * f0, a[1])
        c = (L0[0] + (L1[0] - L0[0]) * f1, base - (base - L1[1]) * f1)
        e = (R0[0] + (R1[0] - R0[0]) * f1, c[1])
        d.line([a, e], fill=col, width=max(1, lw - 1))
        d.line([b, c], fill=col, width=max(1, lw - 1))
        d.line([c, e], fill=col, width=max(1, lw - 1))
    tips = []
    if arms:
        for fy, fw in ((0.70, 0.62), (0.86, 0.46)):
            y = base - h * fy
            half = h * fw / 2
            d.line([(x - half, y), (x + half, y)], fill=col, width=lw)
            d.line([(x - half, y), (x - h * 0.05, y + h * 0.06)], fill=col, width=max(1, lw - 1))
            d.line([(x + half, y), (x + h * 0.05, y + h * 0.06)], fill=col, width=max(1, lw - 1))
            tips += [(x - half, y + h * 0.03), (x + half, y + h * 0.03)]
    return tips


def sag(a, b, k=0.08, n=16):
    """Points of a sagging cable between a and b."""
    pts = []
    L = math.dist(a, b)
    for i in range(n + 1):
        u = i / n
        pts.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u + math.sin(math.pi * u) * L * k))
    return pts


def along(pts, q):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    target, acc = sum(seg) * q, 0
    for i, L in enumerate(seg):
        if acc + L >= target:
            u = (target - acc) / (L or 1)
            return pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u
        acc += L
    return pts[-1]


def pulse(img, x, y, r=26):
    put_glow(img, x, y, r, WARM, 1.0)
    ImageDraw.Draw(img).ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 250, 225, 255))


# --------------------------------------------------------------------- scenes

def village(spec, p, t, base):
    """Night village: 20 tukuls, only one window lit; a power line glows at the end."""
    img = gradient((4, 6, 18), (26, 18, 10), 1060, ((14, 12, 10), (6, 6, 6))).copy()
    stars(img, t, bottom=950)
    put_glow(img, 820, 330, 90, (230, 225, 200), 0.35)  # moon haze
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((800, 310, 840, 350), fill=(225, 220, 200, 220))
    # rolling ground
    d.polygon([(0, 1110)] + [(x, 1085 + 18 * math.sin(x / 140)) for x in range(0, W + 1, 40)] + [(W, H), (0, H)],
              fill=(16, 14, 12, 255))
    lit_slot = spec.get("lit_slot", 13)
    on = p > spec.get("lit_at", 0.22)
    flick = 0.85 + 0.15 * math.sin(t * 9) * math.sin(t * 3.3)
    rows = [(1170, 92, (24, 22, 19), 54), (1340, 108, (32, 29, 25), 0)]
    slot = 0
    for base_y, w, col, off in rows:
        for i in range(10):
            x = 54 + i * 108 if off == 0 else 108 + i * 108  # back row sits between front huts
            h = w * 0.62
            if on and slot == lit_slot:
                put_glow(img, x, base_y - h * 0.4, 260, (255, 190, 90), 0.7 * flick)
                put_glow(img, x, base_y + 20, 200, (255, 170, 70), 0.35 * flick)
            d.rectangle((x - w / 2, base_y - h, x + w / 2, base_y), fill=(*col, 255))
            d.polygon([(x - w * 0.66, base_y - h + 4), (x + w * 0.66, base_y - h + 4), (x, base_y - h - w * 0.78)],
                      fill=(col[0] + 8, col[1] + 6, col[2] + 2, 255))
            wx, wy = x - w * 0.14, base_y - h * 0.62
            win = (255, 214, 130, 255) if (on and slot == lit_slot) else (44, 40, 34, 255)
            d.rectangle((wx - w * 0.11, wy - w * 0.1, wx + w * 0.11, wy + w * 0.1), fill=win)
            d.rectangle((x + w * 0.08, base_y - h * 0.55, x + w * 0.28, base_y), fill=(12, 11, 10, 255))
            slot += 1
    # the change: a power line sweeps in along the horizon
    lp = ease((p - spec.get("line_at", 0.62)) / 0.3)
    if lp > 0:
        y0 = 1000
        xs = W * lp
        cable = [(x, y0 + 14 * math.sin(x / 90) ** 2) for x in range(0, int(xs) + 1, 12)]
        if len(cable) > 1:
            d.line(cable, fill=(*GOLD, 90), width=12)
            d.line(cable, fill=(255, 236, 170, 255), width=3)
        for k, px in enumerate(range(90, int(xs), 260)):
            pylon(d, px, y0 + 70, 110, (*GOLD, 200), width=2, arms=False)
        put_glow(img, xs, y0, 60, WARM, 0.9)
    return img


def coins(spec, p, t, base):
    """Funding: gold coins drop and stack into rising columns."""
    img = gradient((8, 7, 5), (20, 14, 6)).copy()
    put_glow(img, 540, 1250, 520, (120, 80, 16), 0.45)
    d = ImageDraw.Draw(img, "RGBA")
    base_y, rx, ry, th = 1300, 68, 20, 13
    xs = [190, 365, 540, 715, 890]
    targets = [7, 10, 12, 9, 11]
    d.ellipse((60, base_y - 10, 1020, base_y + 40), fill=(0, 0, 0, 120))
    for i, (x, n_max) in enumerate(zip(xs, targets)):
        e = ease((p - 0.04 - 0.05 * i) / 0.72) * n_max
        n = int(e)
        for k in range(n):
            y = base_y - k * th
            d.rectangle((x - rx, y - ry, x + rx, y), fill=(150, 108, 26, 255))
            d.ellipse((x - rx, y + -ry * 2 + ry, x + rx, y + ry), fill=(150, 108, 26, 255))
            d.ellipse((x - rx, y - ry * 2, x + rx, y), fill=(222, 178, 60, 255), outline=(120, 86, 18, 255), width=2)
            d.ellipse((x - rx * 0.62, y - ry * 1.62, x + rx * 0.62, y - ry * 0.38), outline=(170, 128, 36, 255), width=2)
        # the next coin falling onto the stack
        frac = e - n
        if n < n_max and frac > 0:
            top = base_y - n * th
            y = top - 360 * (1 - frac) ** 2
            a = int(255 * min(1, frac * 3))
            d.ellipse((x - rx, y - ry * 2, x + rx, y), fill=(232, 190, 70, a), outline=(120, 86, 18, a), width=2)
        if n and (int(t * 3) + i) % 4 == 0:  # glint
            gx, gy = x + rx * 0.35, base_y - (n - 1) * th - ry * 1.2
            put_glow(img, gx, gy, 18, (255, 245, 210), 0.9)
    return img


def pylons(spec, p, t, base):
    """Transmission towers marching to the horizon; energy races along the cables."""
    hz = 1240
    img = gradient((6, 8, 20), (140, 78, 22), hz, ((22, 16, 10), (8, 7, 6))).copy()
    put_glow(img, 780, hz, 520, (255, 150, 50), 0.55)
    stars(img, t, n=70, bottom=700, seed=5)
    d = ImageDraw.Draw(img, "RGBA")
    vx, vy = 790, hz
    spacing, drift = 1.25, (t * 0.18) % 1.25
    towers = []
    for k in range(8):
        z = 0.72 + k * spacing - drift
        s = 1 / z
        x = vx + (330 - vx) * s
        b = vy + (1760 - vy) * s
        towers.append((z, x, b, 880 * s))
    towers.sort(key=lambda r: -r[0])  # far first
    tipsets = []
    for z, x, b, h in towers:
        pylon(d, x + max(1, h / 300), b, h, (120, 80, 34, 255))  # warm rim light from the sunset
        tipsets.append((z, pylon(d, x, b, h, (34, 27, 20, 255))))
    tipsets.sort(key=lambda r: r[0])  # near -> far
    cables = []
    for c in range(4):
        pts = []
        for (_, a), (_, b2) in zip(tipsets, tipsets[1:]):
            pts += sag(a[c], b2[c], 0.05, 10)
        cables.append(pts)
        d.line(pts, fill=(70, 54, 34, 255), width=3)
    for c, pts in enumerate(cables):
        for k in range(3):
            q = (t * 0.28 + k / 3 + c * 0.11) % 1.0
            x, y = along(pts, q ** 1.6)  # decelerate as pulses recede
            pulse(img, x, y, 30 if q < 0.4 else 18)
    return img


def whowins(spec, p, t, base):
    """A Ugandan dam sends power along a line; a South Sudan skyline lights up."""
    img = gradient((5, 7, 18), (24, 17, 10), 1300, ((14, 12, 10), (6, 6, 6))).copy()
    stars(img, t, n=90, bottom=860, seed=9)
    d = ImageDraw.Draw(img, "RGBA")
    g = 1300
    # reservoir + dam (left)
    d.polygon([(0, 1085), (95, 1085), (80, g), (0, g)], fill=(18, 34, 52, 255))
    d.polygon([(70, g), (380, g), (345, 1085), (100, 1085)], fill=(46, 44, 42, 255))
    for i in range(6):
        d.line([(100 + i * 43, 1085), (80 + i * 50, g)], fill=(36, 34, 32, 255), width=2)
    for k in range(10):  # spillway water
        x = 170 + k * 12
        off = (t * 420 + k * 37) % 200
        for y in range(1100 + int(off) - 200, g, 200):
            if y > 1090:
                d.line([(x, y), (x + 3, y + 60)], fill=(170, 200, 230, 170), width=3)
    put_glow(img, 225, g - 20, 120, (120, 170, 220), 0.35)
    d.text((225, 1030), "UGANDA", font=_font(32), fill=GOLD, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    # city (right)
    rng = np.random.default_rng(11)
    lit = ease((p - 0.28) / 0.55)
    x = 640
    while x < 1060:
        bw = int(rng.integers(52, 92))
        bh = int(rng.integers(120, 330))
        d.rectangle((x, g - bh, x + bw, g), fill=(24, 22, 26, 255))
        for wy in range(g - bh + 16, g - 14, 26):
            for wx in range(x + 9, x + bw - 12, 18):
                on = rng.random() < lit
                col = (255, 214, 130, 255) if on else (40, 38, 42, 255)
                d.rectangle((wx, wy, wx + 8, wy + 12), fill=col)
        x += bw + 6
    if lit > 0.05:
        put_glow(img, 850, g - 120, 280, (255, 180, 80), 0.35 * lit)
    d.text((850, 905), "SOUTH SUDAN", font=_font(32), fill=GOLD, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    # line: dam -> pylon -> city
    tips = pylon(d, 510, g, 260, (40, 34, 26, 255), arms=True)
    route = sag((345, 1095), tips[1], 0.06, 12) + sag(tips[1], (650, g - 150), 0.06, 12)
    d.line(route, fill=(*GOLD, 70), width=12)
    d.line(route, fill=(230, 200, 120, 255), width=3)
    if p > 0.08:
        for k in range(4):
            pulse(img, *along(route, (t * 0.55 + k / 4) % 1.0), r=22)
    return img


def build(spec, p, t, base):
    """Construction: a pylon rises from the ground up, with welding sparks."""
    img = gradient((6, 6, 8), (22, 16, 8)).copy()
    put_glow(img, 540, 1250, 520, (110, 78, 18), 0.45)
    d = ImageDraw.Draw(img, "RGBA")
    g, h = 1330, 540
    d.line([(60, g), (1020, g)], fill=(*GOLD, 120), width=3)
    for i in range(12):  # ground grid
        x = 60 + i * 87
        d.line([(x, g), (540 + (x - 540) * 1.6, g + 120)], fill=(60, 48, 24, 110), width=1)
    ghost = layer_pylon(h, (60, 52, 40, 255))
    img.alpha_composite(ghost)
    b = ease((p - 0.04) / 0.78)
    cut = int(g - h * 1.05 * b)
    solid = layer_pylon(h, (*GOLD, 255))
    img.alpha_composite(solid.crop((0, cut, W, H)), (0, cut))
    if 0.02 < b < 0.999:
        rng = np.random.default_rng(int(t * 30))
        half = h * 0.15 * (1 - (g - cut) / h) + 20
        for _ in range(14):
            sx = 540 + rng.choice([-1, 1]) * half * rng.uniform(0.2, 1)
            vx, vy = rng.uniform(-220, 220), rng.uniform(-260, -40)
            age = rng.uniform(0, 0.35)
            x1, y1 = sx + vx * age, cut + vy * age + 900 * age * age
            d.line([(sx + vx * age * 0.6, cut + vy * age * 0.6 + 900 * (age * 0.6) ** 2), (x1, y1)],
                   fill=(255, 220, 140, 255), width=3)
        put_glow(img, 540, cut, 70, (255, 200, 110), 0.8)
    return img


@lru_cache(maxsize=4)
def layer_pylon(h, col):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pylon(ImageDraw.Draw(lay, "RGBA"), 540, 1330, h, col, width=6)
    return lay


FEED_COLORS = [(92, 60, 120), (40, 90, 130), (140, 60, 70), (60, 110, 80), (130, 90, 40), (70, 70, 140)]
FEED_TAGS = ["#celebrity", "#football", "#memes", "#fashion", "#drama", "#music", "#viral", "#gaming"]


def feed(spec, p, t, base):
    """Doom-scroll: trending cards fly past; the one gold Africa card barely registers."""
    img = gradient((6, 7, 14), (12, 10, 16)).copy()
    d = ImageDraw.Draw(img, "RGBA")
    px0, py0, px1, py1 = 250, 590, 830, 1320
    put_glow(img, 540, 955, 420, (60, 80, 160), 0.35)
    d.rounded_rectangle((px0 - 14, py0 - 14, px1 + 14, py1 + 14), radius=56, fill=(30, 30, 36, 255))
    screen = Image.new("RGBA", (px1 - px0, py1 - py0), (14, 14, 20, 255))
    sd = ImageDraw.Draw(screen, "RGBA")
    ch, gap = 170, 16
    speed = 520 * (1 - 0.35 * ease((t - 2.4) / 1.2))
    off = t * speed
    gold_i = spec.get("gold_card", 6)
    for i in range(40):
        y = 20 + i * (ch + gap) - off
        if y > screen.height or y + ch < 0:
            continue
        if i == gold_i:
            sd.rounded_rectangle((16, y, screen.width - 16, y + ch), radius=18, fill=(40, 32, 14, 255),
                                 outline=(*GOLD, 255), width=3)
            sd.text((40, y + 50), "AFRICA · NEW POWER LINE", font=_font(30), fill=GOLD, anchor="lm")
            sd.text((40, y + 100), "Uganda → South Sudan", font=_font(28), fill=(230, 220, 200), anchor="lm")
            continue
        c = FEED_COLORS[i % len(FEED_COLORS)]
        sd.rounded_rectangle((16, y, screen.width - 16, y + ch), radius=18, fill=(26, 26, 34, 255))
        sd.rounded_rectangle((32, y + 16, 200, y + ch - 16), radius=12, fill=(*c, 255))
        sd.ellipse((220, y + 26, 262, y + 68), fill=(90, 90, 100, 255))
        sd.rounded_rectangle((276, y + 34, 500, y + 56), radius=8, fill=(70, 70, 80, 255))
        sd.text((222, y + 110), FEED_TAGS[i % len(FEED_TAGS)] + "  ▲", font=_font(26), fill=(200, 200, 210), anchor="lm")
    mask = Image.new("L", screen.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, screen.width - 1, screen.height - 1), radius=44, fill=255)
    img.paste(screen, (px0, py0), mask)
    d.rounded_rectangle((470, py0 + 10, 610, py0 + 36), radius=13, fill=(30, 30, 36, 255))
    return img


def planes(spec, p, t, base):
    """Share: paper planes fly out from East Africa across the map."""
    img = (base.convert("RGBA") if base is not None else gradient((6, 6, 8), (14, 12, 10)).copy())
    d = ImageDraw.Draw(img, "RGBA")
    ox, oy = spec.get("origin", (720, 1060))
    targets = [(-80, 420), (1160, 380), (-80, 1500), (1160, 1560), (300, -80), (880, -80), (1160, 900), (-80, 950)]
    for k, (tx, ty) in enumerate(targets):
        start = 0.05 + k * 0.07
        dur = 0.55
        q = (p - start) / dur
        if q <= 0:
            continue
        q = min(q, 1.0)
        cx, cy = (ox + tx) / 2 + (ty - oy) * 0.25, (oy + ty) / 2 - (tx - ox) * 0.25
        def bez(u):
            return ((1 - u) ** 2 * ox + 2 * (1 - u) * u * cx + u * u * tx,
                    (1 - u) ** 2 * oy + 2 * (1 - u) * u * cy + u * u * ty)
        for s in range(0, int(q * 30)):  # dotted trail
            x, y = bez(s / 30)
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(*GOLD, 150))
        x, y = bez(q)
        x2, y2 = bez(min(1, q + 0.02))
        ang = math.atan2(y2 - y, x2 - x)
        ca, sa = math.cos(ang), math.sin(ang)
        pts = [(34, 0), (-22, -18), (-12, 0), (-22, 18)]
        poly = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]
        if q < 1:
            d.polygon(poly, fill=(250, 240, 215, 255), outline=(0, 0, 0, 255))
            d.line([poly[0], poly[2]], fill=(170, 150, 110, 255), width=2)
    put_glow(img, ox, oy, 60, WARM, 0.6 + 0.3 * math.sin(t * 5))
    return img


SCENES = {"village": village, "coins": coins, "pylons": pylons, "whowins": whowins,
          "build": build, "feed": feed, "planes": planes}


def render(spec, p, t, base=None, ctx=None):
    if spec["anim"].startswith("sm_"):  # cut-out stop-motion scenes
        import stopmo
        return stopmo.render(spec, p, t, ctx)
    return SCENES[spec["anim"]](spec, p, t, base).convert("RGB")
