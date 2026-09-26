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
    "ethiopia": (40.0, 9.4, 62.0, 960),
    "horn":   (41.0, 10.5, 44.0, 960),
    "tigray": (38.9, 13.9, 230.0, 930),
    "drc": (23.5, -3.0, 58.0, 900),
    "drc_sw": (17.05, -4.7, 190.0, 900),
}

# approximate coordinates (lon, lat)
PLACES = {
    "Kampala": (32.58, 0.35),
    "Karuma": (32.24, 2.25),
    "Olwiyo": (31.95, 2.93),
    "Bibia": (32.08, 3.52),
    "Nimule": (32.06, 3.60),
    "Juba": (31.58, 4.85),
    "Rabat": (-6.84, 34.02),
    "Bunia": (30.25, 1.56),
    "Abuja": (7.49, 9.06),
    "Mekelle": (39.47, 13.50),
    "Axum": (38.72, 14.12),
    "Shire": (38.28, 14.10),
    "Alamata": (39.55, 12.42),
    "Addis Ababa": (38.76, 9.03),
    "Asmara": (38.93, 15.33),
    "Kinshasa": (15.31, -4.32),
    "Kikwit": (18.82, -5.04),
    "Kenge": (16.90, -4.81),
    "Goma": (29.22, -1.68),
}
ROUTE = ["Olwiyo", "Bibia", "Nimule", "Juba"]

LABELS = {"Dem. Rep. Congo": "DR CONGO", "Angola": "ANGOLA", "Congo": "CONGO", "Eritrea": "ERITREA", "Djibouti": "DJIBOUTI", "Somalia": "SOMALIA", "Uganda": "UGANDA", "S. Sudan": "SOUTH SUDAN", "Kenya": "KENYA", "Ethiopia": "ETHIOPIA",
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


def resolve_view(v, scale=24.0, screen_y=820):
    """A view is a VIEWS name, a PLACES name (centred on that place) or [lon, lat, px_per_degree, screen_y]."""
    if isinstance(v, (list, tuple)):
        return tuple(v)
    if v in VIEWS:
        return VIEWS[v]
    lon, lat = PLACES[v]
    return (lon, lat, scale, screen_y)


def view_at(spec, p):
    a = resolve_view(spec.get("from", spec.get("view", "east")))
    b = resolve_view(spec.get("to", spec.get("view", "east")))
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


def stop_fracs(pts):
    """Fraction of the route length at which each stop is reached."""
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total, acc, out = sum(seg) or 1, 0.0, [0.0]
    for L in seg:
        acc += L
        out.append(acc / total)
    return out


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
                if 40 < x < W - 40 and 300 < y < spec.get("label_max_y", H - 300):  # keep clear of captions
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
            # small pylons every ~46px along the drawn line
            if rs.get("ticks", True) and v[2] > 150:
                total = sum(math.dist(line[i], line[i + 1]) for i in range(len(line) - 1))
                n = int(total // 46)
                full = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
                for k in range(1, n + 1):
                    q = k * 46 / full
                    c = point_at(pts, q)
                    # little pylon that pops up just behind the growing head
                    behind = (frac - q) * full
                    sc = min(1.0, max(0.0, behind / 40)) if frac < 1 else 1.0
                    if sc > 0:
                        x, y, h = c[0], c[1], 30 * sc
                        col = (255, 236, 170, 255)
                        d.line([(x - 8 * sc, y + 6), (x, y - h), (x + 8 * sc, y + 6)], fill=(0, 0, 0, 200), width=6)
                        d.line([(x - 8 * sc, y + 6), (x, y - h), (x + 8 * sc, y + 6)], fill=col, width=3)
                        d.line([(x - 12 * sc, y - h * 0.62), (x + 12 * sc, y - h * 0.62)], fill=col, width=3)
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
            reached = name not in ROUTE or frac >= stop_fracs(pts)[ROUTE.index(name)] - 0.02
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
        # segment labels, e.g. "UGANDA · 150 KM", once the line has passed them
        for sg in rs.get("segments", []):
            i0, i1 = ROUTE.index(sg["between"][0]), ROUTE.index(sg["between"][1])
            if frac < stop_fracs(pts)[i1] - 0.02:
                continue
            a0, a1 = project(*PLACES[sg["between"][0]], v), project(*PLACES[sg["between"][1]], v)
            mx, my = (a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2
            f = _font(32)
            tw = d.textlength(sg["text"], font=f)
            x = mx + 34 if sg.get("side", "r") == "r" else mx - 34 - tw
            d.rounded_rectangle((x - 14, my - 28, x + tw + 14, my + 28), radius=10, fill=(12, 10, 6, 215),
                                outline=(*GOLD, 255), width=2)
            d.text((x, my), sg["text"], font=f, fill=GOLD, anchor="lm")
    # big faint area names with no country polygon, e.g. a region: [{"at": [lon, lat], "text": "TIGRAY"}]
    for tg in spec.get("tags", []):
        x, y = project(*tg["at"], v)
        d.text((x, y), tg["text"], font=_font(tg.get("size", 64)), fill=(*GOLD, tg.get("alpha", 110)), anchor="mm")
    # pulse rings radiating from a place (e.g. a new connection); one spec or a list
    rgs = spec.get("rings")
    for rg in (rgs if isinstance(rgs, list) else [rgs] if rgs else []):
        if p < rg.get("start", 0.0):
            continue
        x, y = project(*PLACES[rg["at"]], v)
        col = tuple(rg.get("color", GOLD))
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1.0
            r = 24 + ph * rg.get("radius", 300)
            d.ellipse((x - r, y - r, x + r, y + r), outline=(*col, int(220 * (1 - ph))), width=4)
    # event pins that drop in one by one: [{"at": place, "start": p, "label": "MEKELLE AIRPORT", "side": "r|l"}]
    for pn in spec.get("pins", []):
        k = (p - pn.get("start", 0.0)) / 0.06
        if k <= 0:
            continue
        x, y = project(*PLACES[pn["at"]], v)
        s = min(1.0, k) * (1 + 0.35 * max(0.0, 1 - abs(k - 1) * 2))  # pop with a little overshoot
        col = tuple(pn.get("color", (225, 70, 50)))
        if k < 6:  # one strong shock ring as it lands
            r = 20 + 170 * min(1.0, k / 6)
            d.ellipse((x - r, y - r, x + r, y + r), outline=(*col, int(230 * (1 - min(1.0, k / 6)))), width=6)
        d.ellipse((x - 20 * s, y - 20 * s, x + 20 * s, y + 20 * s), fill=(*col, 255), outline=(0, 0, 0), width=3)
        d.ellipse((x - 7 * s, y - 7 * s, x + 7 * s, y + 7 * s), fill=WHITE)
        if pn.get("label") and k >= 1:
            f = _font(pn.get("size", 34))
            tw = d.textlength(pn["label"], font=f)
            lx = x + 36 if pn.get("side", "r") == "r" else x - 36 - tw
            d.rounded_rectangle((lx - 14, y - 27, lx + tw + 14, y + 27), radius=10, fill=(12, 10, 6, 225),
                                outline=(*col, 255), width=3)
            d.text((lx, y), pn["label"], font=f, fill=WHITE, anchor="lm")
    # a plane flying a leg, then (optionally) diverting to circle a place:
    # {"from": "Kikwit", "to": "Kinshasa", "divert": "Kenge", "fly": [p0, p1], "circle_from": p, "radius": px,
    #  "planned": true, "fade_at": p}
    fl = spec.get("flight")
    if fl:
        a = project(*PLACES[fl["from"]], v)
        b = project(*PLACES[fl["to"]], v)
        if fl.get("planned", True):  # the intended route, dashed
            n = 40
            for k in range(0, n, 2):
                p0 = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
                p1 = (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)
                d.line([p0, p1], fill=(230, 220, 200, 150), width=4)
        tgt = project(*PLACES[fl["divert"]], v) if fl.get("divert") else b
        f0, f1 = fl.get("fly", [0.0, 0.5])
        cf = fl.get("circle_from")
        r = fl.get("radius", 90)
        if cf is not None and p >= cf:  # circling the diversion point
            ang = -(t - 0) * 2.2
            x, y = tgt[0] + r * math.cos(ang), tgt[1] + r * math.sin(ang)
            heading = ang - math.pi / 2
            trail = [(tgt[0] + r * math.cos(ang + k * 0.12), tgt[1] + r * math.sin(ang + k * 0.12)) for k in range(0, 18)]
            d.line(trail, fill=(255, 236, 170, 110), width=3)
        else:
            q = ease(max(0.0, min(1.0, (p - f0) / max(0.01, f1 - f0))))
            stop = tgt if cf is not None else b
            x, y = a[0] + (stop[0] - a[0]) * q, a[1] + (stop[1] - a[1]) * q
            heading = math.atan2(stop[1] - a[1], stop[0] - a[0])
            d.line([a, (x, y)], fill=(255, 236, 170, 230), width=5)
        alpha = 255
        if fl.get("fade_at") is not None and p > fl["fade_at"]:
            alpha = int(255 * max(0.0, 1 - (p - fl["fade_at"]) / 0.08))
        if alpha > 0:  # plane glyph pointing along its heading
            s = fl.get("size", 26)
            ca, sa = math.cos(heading), math.sin(heading)
            pts = [(1.0, 0), (-0.6, 0.55), (-0.3, 0), (-0.6, -0.55)]
            poly = [(x + s * (px * ca - py * sa), y + s * (px * sa + py * ca)) for px, py in pts]
            d.polygon(poly, fill=(255, 250, 235, alpha), outline=(0, 0, 0, alpha))
        for name in {fl["from"], fl["to"], fl.get("divert")} - {None}:  # endpoint dots + names
            px_, py_ = project(*PLACES[name], v)
            d.ellipse((px_ - 9, py_ - 9, px_ + 9, py_ + 9), fill=WHITE, outline=(0, 0, 0), width=2)
            side = fl.get("label_side", {}).get(name, "b")
            f = _font(32)
            pos = {"b": (px_, py_ + 36, "mm"), "t": (px_, py_ - 36, "mm"), "r": (px_ + 22, py_, "lm"), "l": (px_ - 22, py_, "rm")}[side]
            d.text(pos[:2], name.upper(), font=f, fill=WHITE, anchor=pos[2], stroke_width=3, stroke_fill=(0, 0, 0))
    # capital markers for orientation
    for name in spec.get("capitals", []):
        x, y = project(*PLACES[name], v)
        if 0 < x < W and 250 < y < H - 250:
            d.rectangle((x - 8, y - 8, x + 8, y + 8), fill=WHITE, outline=(0, 0, 0), width=2)
            d.text((x + 20, y), name.upper(), font=_font(30), fill=(225, 220, 210), anchor="lm",
                   stroke_width=3, stroke_fill=(0, 0, 0))
    out = img.convert("RGB")
    dim = spec.get("dim", 1.0)
    if dim < 1.0:
        out = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), out, dim)
    return out
