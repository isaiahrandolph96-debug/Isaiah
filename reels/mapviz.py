"""Animated map backgrounds for Africa Blind Spot reels.

Country borders come from the Natural Earth low-res dataset bundled with
geopandas<1.0. Everything is drawn per frame so views can glide and routes
can grow, in the reel palette (dark ground, muted borders, gold highlights).
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
GOLD = (212, 170, 52)
WHITE = (246, 244, 238)
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# named views: centre lon, centre lat, pixels per degree, screen y of the centre
VIEWS = {
    "africa": (18.0, 2.0, 14.5, 980),
    "region": (33.0, 5.5, 46.0, 1000),
    "east":   (32.2, 3.7, 175.0, 1060),
}

# approximate coordinates (lon, lat)
PLACES = {
    "Kampala": (32.58, 0.35),
    "Karuma": (32.24, 2.25),
    "Olwiyo": (31.95, 2.93),
    "Bibia": (32.08, 3.52),
    "Nimule": (32.06, 3.60),
    "Juba": (31.58, 4.85),
}
ROUTE = ["Olwiyo", "Bibia", "Nimule", "Juba"]

LABELS = {"Uganda": "UGANDA", "S. Sudan": "SOUTH SUDAN", "Kenya": "KENYA", "Ethiopia": "ETHIOPIA",
          "Sudan": "SUDAN", "Dem. Rep. Congo": "DR CONGO", "Tanzania": "TANZANIA"}

_COUNTRIES = None
_BASE = None


def _font(size):
    return ImageFont.truetype(BOLD, size)


def countries():
    global _COUNTRIES
    if _COUNTRIES is None:
        import warnings
        warnings.filterwarnings("ignore")
        import geopandas as gpd
        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        world = world[world.continent.isin(["Africa", "Asia"])]
        out = []
        for name, geom in zip(world.name, world.geometry):
            polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
            rings = [np.asarray(p.exterior.coords) for p in polys]
            rp = geom.representative_point()
            out.append((name, rings, (rp.x, rp.y), geom.bounds))
        _COUNTRIES = out
    return _COUNTRIES


def base():
    global _BASE
    if _BASE is None:
        img = Image.new("RGB", (W, H), (9, 8, 7))
        glow = Image.new("RGB", (W, H), (0, 0, 0))
        ImageDraw.Draw(glow).ellipse((-100, 500, W + 100, 1500), fill=(60, 42, 14))
        _BASE = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(220)), 0.5)
    return _BASE


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def view_at(spec, p):
    a = VIEWS[spec.get("from", spec.get("view", "east"))]
    b = VIEWS[spec.get("to", spec.get("view", "east"))]
    e = ease(p)
    cx = a[0] + (b[0] - a[0]) * e
    cy = a[1] + (b[1] - a[1]) * e
    s = math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * e) * (1 + 0.04 * p)  # slow push
    sy = a[3] + (b[3] - a[3]) * e
    return cx, cy, s, sy


def project(lon, lat, v):
    cx, cy, s, sy = v
    k = math.cos(math.radians(cy))
    return W / 2 + (lon - cx) * s * k, sy - (lat - cy) * s


def route_points(v):
    return [project(*PLACES[n], v) for n in ROUTE]


def partial(pts, frac):
    """Polyline truncated to `frac` of its length, and the head point."""
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    target = sum(seg) * max(0.0, min(1.0, frac))
    out, acc = [pts[0]], 0.0
    for i, L in enumerate(seg):
        if acc + L >= target:
            t = (target - acc) / L if L else 0
            head = (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t)
            out.append(head)
            return out, head
        out.append(pts[i + 1])
        acc += L
    return out, pts[-1]


def point_at(pts, frac):
    return partial(pts, frac)[1]


def render(spec, p, t):
    """Return an RGB frame for map spec at scene progress p (0-1) and time t (s)."""
    v = view_at(spec, p)
    img = base().copy().convert("RGBA")
    d = ImageDraw.Draw(img)
    hl = set(spec.get("highlight", []))
    glow_c = spec.get("glow_country")
    pulse = 0.5 + 0.5 * math.sin(t * 3.0)
    for name, rings, rp, bounds in countries():
        x0, y0 = project(bounds[0], bounds[3], v)
        x1, y1 = project(bounds[2], bounds[1], v)
        if x1 < -50 or x0 > W + 50 or y1 < -50 or y0 > H + 50:
            continue
        is_hl = name in hl
        fill = (58, 46, 22) if is_hl else (24, 22, 19)
        if name == glow_c:
            fill = tuple(int(c) for c in np.array((58, 46, 22)) + np.array((50, 38, 8)) * pulse)
        line = GOLD if is_hl else (86, 76, 56)
        for r in rings:
            pts = [project(lon, lat, v) for lon, lat in r]
            if len(pts) > 2:
                d.polygon(pts, fill=fill)
                d.line(pts + [pts[0]], fill=line, width=3 if is_hl else 2, joint="curve")
    # country labels
    if spec.get("labels", True):
        for name, rings, rp, bounds in countries():
            if name in LABELS and (name in hl or spec.get("all_labels")):
                x, y = project(*spec.get("label_pos", {}).get(name, rp), v)
                if 40 < x < W - 40 and 300 < y < H - 300:
                    f = _font(30 if v[2] < 100 else 38)
                    col = GOLD if name in hl else (150, 140, 120)
                    d.text((x, y), LABELS[name], font=f, fill=(*col, 230), anchor="mm",
                           stroke_width=3, stroke_fill=(0, 0, 0, 200))
    # route
    rs = spec.get("route")
    if rs:
        pts = route_points(v)
        a0, a1 = rs.get("grow", [0.0, 0.0])
        frac = 1.0 if a1 <= a0 else ease((p - a0) / (a1 - a0))
        line, head = partial(pts, frac)
        if len(line) > 1:
            d.line(line, fill=(*GOLD, 70), width=22, joint="curve")
            d.line(line, fill=(*GOLD, 140), width=11, joint="curve")
            d.line(line, fill=(255, 236, 170, 255), width=5, joint="curve")
            # pylon ticks every ~34px along the drawn line
            if rs.get("ticks", True) and v[2] > 150:
                total = sum(math.dist(line[i], line[i + 1]) for i in range(len(line) - 1))
                n = int(total // 34)
                full = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
                for k in range(1, n + 1):
                    q = k * 34 / full
                    a = point_at(pts, max(0, q - 0.004))
                    b = point_at(pts, min(1, q + 0.004))
                    c = point_at(pts, q)
                    dx, dy = b[0] - a[0], b[1] - a[1]
                    L = math.hypot(dx, dy) or 1
                    nx, ny = -dy / L * 12, dx / L * 12
                    d.line([(c[0] - nx, c[1] - ny), (c[0] + nx, c[1] + ny)], fill=(*GOLD, 200), width=3)
        if frac < 1:
            r_ = 14 + 5 * pulse
            d.ellipse((head[0] - r_, head[1] - r_, head[0] + r_, head[1] + r_), fill=(255, 236, 170, 255))
        if rs.get("flow"):
            for k in range(6):
                q = (t * 0.22 + k / 6) % 1.0
                x, y = point_at(pts, q)
                d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 250, 220, 255))
        # places
        for name in rs.get("places", []):
            x, y = project(*PLACES[name], v)
            reached = name not in ROUTE or frac >= ROUTE.index(name) / (len(ROUTE) - 1) - 0.02
            if not reached or not (0 < x < W and 0 < y < H):
                continue
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=WHITE, outline=(0, 0, 0), width=3)
            side = rs.get("label_side", {}).get(name, "r")
            f = _font(38)
            if side == "r":
                d.text((x + 26, y), name.upper(), font=f, fill=WHITE, anchor="lm", stroke_width=3,
                       stroke_fill=(0, 0, 0))
            else:
                d.text((x - 26, y), name.upper(), font=f, fill=WHITE, anchor="rm", stroke_width=3,
                       stroke_fill=(0, 0, 0))
    out = img.convert("RGB")
    dim = spec.get("dim", 1.0)
    if dim < 1.0:
        out = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), out, dim)
    return out
