"""Cut-out paper stop-motion scenes for Africa Blind Spot story reels.

Everything is animated "on twos" (12 poses per second, each held for two or
three video frames), moving pieces get a tiny per-pose boil (jitter), and every
paper piece has a cut edge and a drop shadow. Sets are built once per scene
and cached; puppets and props are redrawn at each new pose.

Scenes are chosen with bg_spec {"anim": "sm_<name>"} and receive ctx from the
renderer: {"speaker": "narrator" | "yasmine" | "haj" | None, "level": 0-1 mouth
openness, "line": index of the current line, "line_p": progress through it}.
"""
import math
import zlib
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
POSE_FPS = 12
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

GOLD = (212, 170, 52)
SKIN_Y = (158, 104, 74)
SKIN_H = (140, 94, 66)
HAIR = (34, 24, 20)
TEAL = (36, 118, 116)
TEAL_D = (26, 88, 88)
JEANS = (44, 58, 92)
CREAM = (230, 216, 182)
CREAM_D = (196, 180, 144)
TRIM = (122, 84, 48)
WHITE = (242, 238, 228)


def font(size, serif=False):
    return ImageFont.truetype(SERIF if serif else BOLD, size)


def crc(*parts):
    return zlib.crc32("|".join(map(str, parts)).encode())


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def darker(c, k=0.72):
    return tuple(int(v * k) for v in c[:3]) + ((c[3],) if len(c) == 4 else ())


# ----------------------------------------------------------------- paper stage

class Stage:
    """Draws paper pieces with cut edges, drop shadows and per-pose boil."""

    def __init__(self, img, pose_id, boil=1.0):
        self.img = img
        self.d = ImageDraw.Draw(img, "RGBA")
        self.pose = pose_id
        self.boil = boil

    def _jit(self, key, amt):
        r = crc(self.pose, key)
        dx = ((r & 0xFF) / 255 - 0.5) * 3.2 * amt * self.boil
        dy = (((r >> 8) & 0xFF) / 255 - 0.5) * 3.2 * amt * self.boil
        da = (((r >> 16) & 0xFF) / 255 - 0.5) * 1.0 * amt * self.boil
        return dx, dy, da

    def piece(self, pts, col, key, boil=1.0, shadow=(7, 9, 60), edge=True, pivot=None):
        if boil:
            dx, dy, da = self._jit(key, boil)
            cx, cy = pivot or (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
            ca, sa = math.cos(math.radians(da)), math.sin(math.radians(da))
            pts = [(cx + (x - cx) * ca - (y - cy) * sa + dx, cy + (x - cx) * sa + (y - cy) * ca + dy) for x, y in pts]
        if shadow:
            ox, oy, a = shadow
            self.d.polygon([(x + ox, y + oy) for x, y in pts], fill=(0, 0, 0, a))
        self.d.polygon(pts, fill=col)
        if edge:
            self.d.line(pts + [pts[0]], fill=darker(col), width=2)
        return pts

    def text(self, xy, s, size, col, key, anchor="mm", serif=False, boil=0.6, angle=0):
        dx, dy, _ = self._jit(key, boil)
        if angle:
            f = font(size, serif)
            tw, th = int(self.d.textlength(s, font=f)) + 20, size + 20
            lay = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
            ImageDraw.Draw(lay).text((tw / 2, th / 2), s, font=f, fill=col, anchor="mm")
            lay = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
            self.img.alpha_composite(lay, (int(xy[0] - lay.width / 2 + dx), int(xy[1] - lay.height / 2 + dy)))
        else:
            self.d.text((xy[0] + dx, xy[1] + dy), s, font=font(size, serif), fill=col, anchor=anchor)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def oval(cx, cy, rx, ry, key="", n=30, rough=0.03):
    ph = (crc(key) % 628) / 100
    return [(cx + rx * (1 + rough * math.sin(3 * a + ph)) * math.cos(a),
             cy + ry * (1 + rough * math.sin(3 * a + ph)) * math.sin(a))
            for a in (2 * math.pi * i / n for i in range(n))]


def torn_band(y0, y1, key, amp=10):
    """Horizontal paper band with torn top edge."""
    r = np.random.default_rng(crc(key))
    top = [(x, y0 + r.uniform(-amp, amp)) for x in range(-20, W + 40, 40)]
    return top + [(W + 20, y1), (-20, y1)]


def rot(pts, cx, cy, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


@lru_cache(maxsize=4)
def grain(seed):
    r = np.random.default_rng(seed)
    n = r.normal(0, 1, (H // 2 + 20, W // 2 + 20)).astype(np.float32)
    img = Image.fromarray(np.clip(128 + n * 14, 0, 255).astype(np.uint8)).resize((W + 40, H + 40), Image.BILINEAR)
    return img


def finish(img, pose_id, sepia=0.0, vignette=0.35, flicker=0.02):
    """Paper grain, gentle exposure flicker, optional sepia (for flashbacks)."""
    g = grain(pose_id % 3)
    ox, oy = crc(pose_id, "gx") % 40, crc(pose_id, "gy") % 40
    gn = np.asarray(g.crop((ox, oy, ox + W, oy + H)), dtype=np.float32) / 128.0
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    a *= (0.9 + 0.1 * gn)[..., None]
    a *= 1 + flicker * (((crc(pose_id, "fl") % 100) / 100) - 0.5)
    if sepia:
        lum = a.mean(axis=2, keepdims=True)
        sep = np.concatenate([lum * 1.07, lum * 0.92, lum * 0.72], axis=2)
        a = a * (1 - sepia) + sep * sepia
    if vignette:
        y, x = np.ogrid[0:H, 0:W]
        dd = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        a *= (1 - vignette * np.clip(dd, 0, 1) ** 2)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ----------------------------------------------------------------- puppets

def arm(st, sx, sy, ang, face, length, width, sleeve, hand, key, boil=1.0):
    # length may be shortened by callers to suggest a bent (folded) arm
    """Arm hinged at the shoulder. ang in degrees: 0 = hanging down, 90 = straight forward."""
    dx, dy = face * math.sin(math.radians(ang)), math.cos(math.radians(ang))
    nx, ny = -dy, dx
    ex, ey = sx + dx * length, sy + dy * length
    w = width / 2
    st.piece([(sx + nx * w, sy + ny * w), (ex + nx * w * 0.8, ey + ny * w * 0.8),
              (ex - nx * w * 0.8, ey - ny * w * 0.8), (sx - nx * w, sy - ny * w)], sleeve, key + "arm",
             boil=boil, pivot=(sx, sy))
    st.piece(oval(ex + dx * 10, ey + dy * 10, width * 0.42, width * 0.46, key + "hand"), hand, key + "hand", boil=boil)
    return ex + dx * 14, ey + dy * 14


def head_y(st, cx, cy, face, s, mouth, blink, key, look=0):
    """Yasmine's head: hair behind, face, bun, eyes, brows, mouth."""
    st.piece(oval(cx - face * 6 * s, cy - 6 * s, 66 * s, 70 * s, key + "hair"), HAIR, key + "hair")
    st.piece(oval(cx - face * 58 * s, cy - 36 * s, 26 * s, 24 * s, key + "bun"), HAIR, key + "bun")
    st.piece(oval(cx + face * 6 * s, cy + 4 * s, 54 * s, 60 * s, key + "face"), SKIN_Y, key + "face", shadow=None)
    st.piece([(cx - face * 58 * s, cy - 26 * s), (cx + face * 58 * s, cy - 38 * s),
              (cx + face * 40 * s, cy - 64 * s), (cx - face * 30 * s, cy - 70 * s)], HAIR, key + "fringe", shadow=None)
    ex = cx + face * (22 + look) * s
    for i, off in enumerate((0, 30)):
        x = ex + face * off * s - face * 14 * s
        if blink:
            st.d.line([(x - 7 * s, cy - 4 * s), (x + 7 * s, cy - 4 * s)], fill=(30, 20, 18), width=3)
        else:
            st.d.ellipse((x - 5 * s, cy - 11 * s, x + 5 * s, cy + 2 * s), fill=(28, 18, 16))
        st.d.line([(x - 10 * s, cy - 22 * s), (x + 8 * s, cy - 24 * s)], fill=HAIR, width=int(4 * s))
    mx, my = cx + face * 26 * s, cy + 32 * s
    if mouth > 0.12:
        h = (4 + 18 * mouth) * s
        st.d.ellipse((mx - 11 * s, my - h / 2, mx + 11 * s, my + h / 2), fill=(96, 30, 34))
    else:
        st.d.line([(mx - 10 * s, my), (mx + 10 * s, my)], fill=(92, 42, 38), width=int(3 * s))


def yasmine(st, x, y, s=1.0, face=1, pose="stand", arm_f=8, arm_b=-6, mouth=0.0, blink=False,
            walk=0, hold=None, look=0, key="Y"):
    """x, y = hip point. pose: stand | sit | walk. hold: None | card | sign | card_pocket."""
    def P(px, py):
        return (x + face * px * s, y + py * s)

    if pose == "sit":
        st.piece([P(-10, -20), P(120, -24), P(126, 20), P(-10, 22)], JEANS, key + "thigh")
        st.piece([P(96, -4), P(134, -4), P(150, 190), P(112, 196)], JEANS, key + "shin")
        st.piece(oval(*P(140, 204), 30 * s, 14 * s, key + "shoe"), WHITE, key + "shoe")
    else:
        sw = math.sin(walk) * 14 if pose == "walk" else 0
        for i, (lx, a) in enumerate(((-18, sw), (18, -sw))):
            hx, hy = P(lx, 0)
            fx = hx + face * math.sin(math.radians(a)) * 250 * s
            fy = hy + math.cos(math.radians(a)) * 250 * s
            st.piece([(hx - 17 * s, hy), (hx + 17 * s, hy), (fx + 15 * s, fy), (fx - 15 * s, fy)], JEANS, key + f"leg{i}",
                     pivot=(hx, hy))
            st.piece(oval(fx + face * 12 * s, fy + 6 * s, 30 * s, 13 * s, key + f"shoe{i}"), WHITE, key + f"shoe{i}")
    # back arm, hood, torso, front arm
    sb = P(-50, -190)
    arm(st, *sb, arm_b, face, 180 * s, 36 * s, TEAL_D, SKIN_Y, key + "ab")
    st.piece(oval(*P(-8, -200), 72 * s, 32 * s, key + "hood"), TEAL_D, key + "hood")
    st.piece([P(-80, 6), P(82, 6), P(72, -206), P(-72, -206)], TEAL, key + "torso")
    st.piece([P(-48, -60), P(52, -60), P(46, -10), P(-44, -10)], TEAL_D, key + "pocket", shadow=None)
    st.piece(rect(*P(-14, -236), *P(14, -200)) if face > 0 else rect(*P(14, -236), *P(-14, -200)), SKIN_Y,
             key + "neck", shadow=None)
    head_y(st, *P(0, -290), face, s, mouth, blink, key, look)
    hx, hy = arm(st, *P(50, -190), arm_f, face, 180 * s, 36 * s, TEAL, SKIN_Y, key + "af")
    if hold == "card":
        st.piece(rect(hx - 26 * s, hy - 40 * s, hx + 26 * s, hy + 2 * s), (150, 196, 150), key + "card")
        st.d.line([(hx - 16 * s, hy - 28 * s), (hx + 14 * s, hy - 28 * s)], fill=(60, 90, 60), width=3)
    if hold == "sign":
        bx, by = hx, hy - 150 * s
        st.piece([(hx - 5, hy), (hx + 5, hy), (bx + 5, by + 40 * s), (bx - 5, by + 40 * s)], (150, 110, 60), key + "stick")
        pts = st.piece(rect(bx - 190 * s, by - 90 * s, bx + 190 * s, by + 60 * s), (206, 170, 118), key + "sign")
        cx = sum(p[0] for p in pts) / 4
        cy = sum(p[1] for p in pts) / 4
        st.text((cx, cy - 30 * s), "HOSPITALS,", int(40 * s), (40, 28, 20), key + "t1", serif=True)
        st.text((cx, cy + 24 * s), "NOT STADIUMS", int(40 * s), (150, 30, 30), key + "t2", serif=True)
    return hx, hy


def haj(st, x, y, s=1.0, face=1, pose="stand", arm_f=10, arm_b=-6, mouth=0.0, blink=False, walk=0,
        lean=0, key="H", hand_up=None, arm_len=1.0):
    """x, y = feet (stand/walk) or seat point (sit)."""
    def P(px, py):
        return (x + face * px * s, y + py * s)

    if pose == "sit":
        body_top = -300
        st.piece([P(-120, 0), P(140, 0), P(96, -230), P(-78, -240)], CREAM, key + "robe", pivot=P(0, 0))
        st.piece(oval(*P(118, -8), 42 * s, 16 * s, key + "slip"), (222, 180, 62), key + "slip")
        shoulder_y = -236
        hx0 = 0
    else:
        sw = math.sin(walk) * 16 if pose == "walk" else 0
        for i, off in enumerate((-30 + sw, 34 - sw)):
            st.piece(oval(*P(off + 18, -8), 36 * s, 15 * s, key + f"slip{i}"), (222, 180, 62), key + f"slip{i}")
        st.piece([P(-40, -472), P(-100, -440), P(-74, -330)], CREAM_D, key + "hoodback")
        st.piece([P(-80, -476), P(80, -476), P(112, -20), P(-108, -20)], CREAM, key + "robe")
        st.d.line([P(12, -474), P(16, -24)], fill=TRIM, width=int(7 * s))
        for b in range(9):
            bx, by = P(20, -440 + b * 44)
            st.d.ellipse((bx - 5 * s, by - 5 * s, bx + 5 * s, by + 5 * s), fill=TRIM)
        body_top = -520
        shoulder_y = -452
        hx0 = 0
    # head (with lean)
    cx, cy = P(hx0 + lean * 0.6, body_top - 34)
    arm(st, *P(-50, shoulder_y), arm_b, face, 200 * s, 40 * s, CREAM_D, SKIN_H, key + "ab")
    st.piece(oval(cx + face * 4 * s, cy, 55 * s, 62 * s, key + "face"), SKIN_H, key + "face")
    st.piece(oval(cx, cy - 46 * s, 54 * s, 26 * s, key + "cap"), WHITE, key + "cap")
    beard = [(cx - face * 34 * s, cy + 6 * s), (cx + face * 56 * s, cy + 4 * s), (cx + face * 50 * s, cy + 46 * s),
             (cx + face * 12 * s, cy + 78 * s), (cx - face * 26 * s, cy + 50 * s)]
    st.piece(beard, (226, 224, 218), key + "beard", shadow=None)
    ex = cx + face * 22 * s
    for off in (0, 28):
        exx = ex + face * off * s - face * 8 * s
        if blink:
            st.d.line([(exx - 7 * s, cy - 10 * s), (exx + 7 * s, cy - 10 * s)], fill=(30, 20, 18), width=3)
        else:
            st.d.ellipse((exx - 5 * s, cy - 16 * s, exx + 5 * s, cy - 4 * s), fill=(28, 18, 16))
        st.d.line([(exx - 11 * s, cy - 26 * s), (exx + 9 * s, cy - 24 * s)], fill=(236, 234, 226), width=int(6 * s))
    mx, my = cx + face * 30 * s, cy + 26 * s
    h = (3 + 16 * mouth) * s if mouth > 0.12 else 3 * s
    st.d.ellipse((mx - 12 * s, my - h / 2, mx + 12 * s, my + h / 2), fill=(90, 36, 34))
    st.d.line([(mx - 20 * s, my - 10 * s), (mx + 22 * s, my - 12 * s)], fill=(238, 236, 230), width=int(7 * s))
    ang = hand_up if hand_up is not None else arm_f
    return arm(st, *P(52, shoulder_y), ang, face, 200 * s * arm_len, 40 * s, CREAM, SKIN_H, key + "af")


def mouth_of(ctx, who):
    if not ctx or ctx.get("speaker") != who:
        return 0.0
    return ctx.get("level", 0.0)


def blink_at(pose_id, key):
    return (pose_id + crc(key) % 37) % 41 == 0


# ----------------------------------------------------------------- sets

def sky_bands(img, bands, key):
    st = Stage(img, 0, boil=0)
    for i, (y0, y1, col) in enumerate(bands):
        st.piece(torn_band(y0, y1, key + str(i)), col, key + str(i), boil=0, shadow=(0, 6, 40), edge=False)


def skyline(st, base, cols, key, lit=None, pose=0, minaret=True):
    r = np.random.default_rng(crc(key))
    x = -20
    i = 0
    while x < W + 20:
        bw = int(r.integers(70, 150))
        bh = int(r.integers(90, 260))
        st.piece(rect(x, base - bh, x + bw, base + 400), cols[i % len(cols)], f"{key}{i}", boil=0, shadow=(5, 6, 50))
        if lit is not None:
            for wy in range(base - bh + 20, base - 12, 34):
                for wx in range(x + 14, x + bw - 14, 26):
                    on = r.random() < lit
                    st.d.rectangle((wx, wy, wx + 12, wy + 16), fill=(255, 214, 130, 255) if on else (40, 40, 52, 255))
        x += bw + int(r.integers(-10, 14))
        i += 1
    if minaret:  # Hassan II-style square minaret on the skyline
        mx = 150
        st.piece(rect(mx, base - 520, mx + 70, base), cols[0], key + "min", boil=0)
        st.piece(rect(mx - 6, base - 540, mx + 76, base - 505), darker(cols[0], 0.9), key + "min2", boil=0)
        st.piece(rect(mx + 20, base - 590, mx + 50, base - 540), cols[0], key + "min3", boil=0)


@lru_cache(maxsize=4)
def sky_rooftop(night):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if night:
        sky_bands(img, [(-40, 700, (12, 16, 40)), (640, 1000, (20, 24, 56)), (940, 1200, (34, 30, 64))], "rn")
    else:
        sky_bands(img, [(-40, 520, (40, 52, 110)), (460, 760, (104, 78, 138)), (700, 940, (226, 128, 124)),
                        (880, 1120, (246, 170, 110)), (1060, 1200, (252, 206, 140))], "rd")
    return img


@lru_cache(maxsize=4)
def set_rooftop(night):
    """Skyline, distant stadium and roof on a transparent layer (sky drawn separately)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    st = Stage(img, 0, boil=0)
    far = [(92, 70, 120), (84, 66, 112)] if not night else [(26, 26, 50), (30, 30, 58)]
    skyline(st, 1080, far, "far" + str(night), minaret=True)
    near = [(236, 226, 206), (220, 206, 184), (244, 236, 220)] if not night else [(40, 40, 60), (46, 44, 66)]
    skyline(st, 1180, near, "near" + str(night), lit=(0.35 if night else None), minaret=False)
    stadium(st, 820, 1110, night, 0, crane=not night, scale=0.7)  # the half-built / floodlit stadium
    # roof floor and parapet
    st.piece(rect(-20, 1300, W + 20, H + 20), (176, 118, 82) if not night else (60, 44, 40), "floor", boil=0)
    for i in range(8):
        st.d.line([(0, 1330 + i * 80), (W, 1330 + i * 80)], fill=(0, 0, 0, 40), width=2)
    st.piece(rect(-20, 1170, W + 20, 1310), (218, 196, 164) if not night else (86, 76, 80), "parapet", boil=0)
    # satellite dishes
    for dx in (120, 930):
        st.piece(oval(dx, 1100, 44, 30, "dish" + str(dx)), (228, 228, 228) if not night else (90, 90, 100), "dish" + str(dx), boil=0)
        st.d.line([(dx, 1120), (dx + 6, 1172)], fill=(80, 80, 80), width=5)
    return img


def moon_stars(img, t, pose):
    d = ImageDraw.Draw(img, "RGBA")
    r = np.random.default_rng(5)
    for i in range(90):
        x, y = r.uniform(0, W), r.uniform(0, 820)
        a = 110 + int(100 * (0.5 + 0.5 * math.sin(pose * 0.7 + i)))
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(240, 236, 210, a))
    d.ellipse((780, 250, 870, 340), fill=(240, 232, 200, 255))
    d.ellipse((806, 238, 896, 328), fill=(12, 16, 40, 255))  # crescent


def stadium(st, x, y, lit, pose, crane=True, scale=1.0, beams=False):
    s = scale
    st.piece(oval(x, y, 190 * s, 62 * s, "stad"), (150, 150, 160) if not lit else (180, 180, 190), "stad", boil=0.3 * (s < 1 and 0 or 1))
    st.piece(oval(x, y + 6 * s, 150 * s, 40 * s, "stadin"), (70, 90, 70) if not lit else (90, 150, 90), "stadin", boil=0, shadow=None)
    if crane:
        st.d.line([(x + 120 * s, y + 10 * s), (x + 120 * s, y - 250 * s)], fill=(230, 180, 40, 255), width=max(3, int(8 * s)))
        st.d.line([(x + 40 * s, y - 240 * s), (x + 260 * s, y - 250 * s)], fill=(230, 180, 40, 255), width=max(3, int(7 * s)))
        st.d.line([(x + 230 * s, y - 248 * s), (x + 230 * s, y - 150 * s)], fill=(60, 60, 60, 255), width=2)
    if lit:
        for k, bx in enumerate((x - 170 * s, x + 170 * s)):
            st.d.line([(bx, y - 20 * s), (bx, y - 170 * s)], fill=(200, 200, 210, 255), width=max(2, int(6 * s)))
            st.d.rectangle((bx - 22 * s, y - 186 * s, bx + 22 * s, y - 168 * s), fill=(255, 252, 230, 255))


def floodlights(img, x, y, s, pose):
    """Soft translucent beams from the stadium floodlights (drawn on their own layer)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k, bx in enumerate((x - 170 * s, x + 170 * s)):
        sgn = 1 if k else -1
        d.polygon([(bx - 12, y - 180 * s), (bx + 12, y - 180 * s), (bx + 240 * sgn, y - 900), (bx + 60 * sgn, y - 940)],
                  fill=(255, 248, 210, 70 + 8 * (pose % 2)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))


def hospital(st, x, y):
    st.piece(rect(x - 150, y - 260, x + 150, y + 60), (58, 64, 76), "hosp", boil=0)
    for wy in range(y - 230, y + 30, 40):
        for wx in range(x - 125, x + 125, 34):
            on = crc(wx, wy) % 9 == 0
            st.d.rectangle((wx, wy, wx + 16, wy + 20), fill=(230, 210, 150, 255) if on else (36, 40, 50, 255))
    st.piece(rect(x - 60, y - 320, x + 60, y - 262), (70, 40, 44), "hsign", boil=0)
    st.d.text((x, y - 291), "HÔPITAL", font=font(22), fill=(150, 90, 90), anchor="mm")


@lru_cache(maxsize=4)
def set_apartment(night):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    st = Stage(img, 0, boil=0)
    wall = (238, 222, 196) if not night else (110, 90, 80)
    st.piece(rect(-20, -20, W + 20, 1060), wall, "wall", boil=0, shadow=None)
    # zellige band
    cols = [(34, 104, 88), (36, 64, 122), (236, 230, 214), (190, 150, 60)]
    if night:
        cols = [darker(c, 0.5) for c in cols]
    for j, y in enumerate(range(1000, 1330, 62)):
        for i, x in enumerate(range(-10, W + 10, 62)):
            c = cols[(i + j) % 3]
            st.d.rectangle((x, y, x + 60, y + 60), fill=c + (255,))
            star = oval(x + 30, y + 30, 18, 18, "", n=8, rough=0)
            st.d.polygon(star, fill=cols[3] + (255,))
            st.d.polygon(rot(star, x + 30, y + 30, 22.5), fill=cols[3] + (255,))
    st.d.line([(0, 996), (W, 996)], fill=darker(wall), width=6)
    # horseshoe-arch window
    ax, ay = 540, 700
    win = [(ax - 150, ay + 260), (ax - 150, ay)] + [(ax + 170 * math.cos(a), ay - 60 + 190 * math.sin(a))
                                                     for a in np.linspace(math.pi * 0.95, math.pi * 2.05, 24)] + [(ax + 150, ay), (ax + 150, ay + 260)]
    st.piece(win, (150, 190, 220) if not night else (20, 24, 50), "win", boil=0)
    st.d.line([(ax, ay - 240), (ax, ay + 260)], fill=(120, 90, 60, 255), width=10)
    st.d.line([(ax - 150, ay + 60), (ax + 150, ay + 60)], fill=(120, 90, 60, 255), width=10)
    # floor
    st.piece(rect(-20, 1330, W + 20, H + 20), (150, 96, 64) if not night else (70, 46, 36), "floor", boil=0)
    for i in range(0, W, 120):
        st.d.line([(i, 1330), (i - 200, H)], fill=(0, 0, 0, 30), width=2)
    # sedari (low sofa) with cushions
    st.piece(rect(600, 1170, 1100, 1350), (150, 40, 44) if not night else (70, 24, 28), "sofa", boil=0)
    for k in range(3):
        st.piece(oval(680 + k * 140, 1150, 66, 50, f"cush{k}"), (206, 150, 50) if not night else (90, 70, 30), f"cush{k}", boil=0)
    return img


def tea_table(st, x, y, pose, steam=True, key="T"):
    st.piece(oval(x, y + 70, 200, 34, key + "tl"), (120, 80, 50), key + "tl", boil=0)
    st.piece(rect(x - 160, y + 70, x + 160, y + 170), (110, 72, 44), key + "tb", boil=0)
    st.piece(oval(x, y + 56, 190, 40, key + "tray"), (214, 172, 70), key + "tray", boil=0.3)
    st.piece([(x - 40, y + 50), (x + 40, y + 50), (x + 30, y - 30), (x - 30, y - 30)], (196, 200, 208), key + "pot", boil=0.5)
    st.piece(oval(x, y - 34, 26, 14, key + "lid"), (210, 214, 220), key + "lid", boil=0.5)
    st.d.line([(x + 38, y + 10), (x + 90, y - 30)], fill=(190, 194, 202, 255), width=8)
    for k, gx in enumerate((x - 120, x - 80, x + 100)):
        st.piece([(gx - 16, y + 50), (gx + 16, y + 50), (gx + 20, y), (gx - 20, y)], (200, 140, 60, 200), key + f"g{k}", boil=0.6)
    if steam:
        for k in range(3):
            ph = ((pose + k * 5) % 15) / 15
            sy = y - 60 - ph * 160
            st.d.ellipse((x + 90 - 16 + math.sin(ph * 6 + k) * 10, sy - 16, x + 90 + 16 + math.sin(ph * 6 + k) * 10, sy + 16),
                         fill=(255, 255, 255, int(150 * (1 - ph))))


# ----------------------------------------------------------------- scenes

def pose_of(t):
    return int(t * POSE_FPS)


def tq(t):
    return pose_of(t) / POSE_FPS


def sm_rooftop_dawn(spec, p, t, ctx):
    pose = pose_of(t)
    img = sky_rooftop(False).copy()
    st = Stage(img, pose)
    sun_y = 930 - 110 * ease(tq(t) / 6)  # rises above the far skyline
    put = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(put).ellipse((620 - 150, sun_y - 150, 620 + 150, sun_y + 150), fill=(255, 190, 110, 90))
    img.alpha_composite(put.filter(ImageFilter.GaussianBlur(30)))
    st.d.ellipse((620 - 80, sun_y - 80, 620 + 80, sun_y + 80), fill=(252, 150, 60, 255))
    img.alpha_composite(set_rooftop(False))
    # laundry line
    st.d.line([(40, 980), (500, 1010)], fill=(60, 50, 40, 255), width=3)
    for k, (cx, col) in enumerate(((120, (196, 60, 60)), (230, (60, 120, 190)), (340, (230, 190, 70)))):
        sw = math.sin(pose * 0.9 + k) * 6
        st.piece(rot(rect(cx - 36, 990, cx + 36, 1090), cx, 990, sw), col, f"cloth{k}", boil=0.4, pivot=(cx, 990))
    # Yasmine sits on the parapet, turning her voter card
    flip = math.sin(pose * 0.5)
    yasmine(st, 520, 1172, s=1.05, face=1, pose="sit", arm_f=62 + 8 * flip, arm_b=-10,
            mouth=mouth_of(ctx, "yasmine"), blink=blink_at(pose, "Y"), hold="card", look=4)
    return finish(img, pose)


def sm_protest(spec, p, t, ctx):
    pose = pose_of(t)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    sky_bands(img, [(-40, 900, (16, 20, 44)), (860, 1100, (28, 30, 60))], "pn")
    st = Stage(img, pose)
    # palms and street lamps
    for k, x in enumerate((80, 1000)):
        st.piece(rect(x - 10, 700, x + 10, 1250), (40, 34, 30), f"palm{k}", boil=0.3)
        for j in range(6):
            a = -150 + j * 60
            st.piece(rot([(x, 700), (x + 150, 690), (x + 130, 720)], x, 700, a), (30, 60, 40), f"fr{k}{j}", boil=0.6)
    for k, x in enumerate((300, 780)):
        st.d.line([(x, 1250), (x, 760)], fill=(60, 60, 70, 255), width=8)
        st.d.ellipse((x - 70, 700, x + 70, 820), fill=(255, 220, 140, 60))
        st.d.ellipse((x - 14, 750, x + 14, 776), fill=(255, 226, 150, 255))
    st.piece(rect(-20, 1240, W + 20, H + 20), (46, 44, 52), "road", boil=0)
    # marching crowd: three rows moving in stop-motion steps
    step = pose * 7
    for row, (yb, sc, col) in enumerate(((1180, 0.55, (24, 26, 40)), (1260, 0.72, (34, 34, 52)), (1360, 0.9, (46, 44, 64)))):
        for k in range(9):
            x = (k * 150 + step * (1 + row * 0.2) + row * 60) % (W + 300) - 150
            bob = 6 * math.sin(pose * 1.4 + k)
            st.piece(oval(x, yb - 170 * sc + bob, 34 * sc, 36 * sc, f"h{row}{k}"), col, f"h{row}{k}", boil=0.8)
            st.piece([(x - 60 * sc, yb + bob), (x + 60 * sc, yb + bob), (x + 44 * sc, yb - 130 * sc + bob),
                      (x - 44 * sc, yb - 130 * sc + bob)], col, f"b{row}{k}", boil=0.8)
            if (k + row) % 3 == 0:
                lx, ly = x + 40 * sc, yb - 230 * sc + bob
                st.d.ellipse((lx - 26, ly - 26, lx + 26, ly + 26), fill=(255, 240, 180, 50))
                st.d.rectangle((lx - 6, ly - 10, lx + 6, ly + 10), fill=(255, 244, 200, 255))
    shout = mouth_of(ctx, "yasmine")
    pump = 30 * shout
    yasmine(st, 560, 1400, s=0.95, face=1, pose="walk", walk=pose * 0.9, arm_f=165 - pump * 0.3, arm_b=-12,
            mouth=shout, blink=False, hold="sign", look=6)
    return finish(img, pose, sepia=0.35)


def sm_apartment_morning(spec, p, t, ctx):
    pose = pose_of(t)
    img = set_apartment(False).copy()
    st = Stage(img, pose)
    st.d.polygon([(420, 600), (660, 600), (780, 1330), (300, 1330)], fill=(255, 240, 200, 22))  # light beam
    tea_table(st, 560, 1250, pose)
    line = (ctx or {}).get("line", 0)
    speaking_h = mouth_of(ctx, "haj")
    # Haj: buttoning his djellaba (line 0), then pointing at Yasmine on "change the seats"
    alen = 1.0
    if line == 0:  # buttoning: hand folded to the chest, working down the buttons
        af, alen = 62 + 10 * math.sin(pose * 1.3), 0.42
    elif line == 2 and (ctx or {}).get("line_p", 0) > 0.6:
        af = 95  # points at Yasmine: "So change the seats."
    else:
        af = 20
    haj(st, 290, 1470, s=1.0, face=1, arm_f=af, arm_len=alen, mouth=speaking_h, blink=blink_at(pose, "H"))
    yasmine(st, 800, 1200, s=0.95, face=-1, pose="sit", arm_f=30, arm_b=-8,
            mouth=mouth_of(ctx, "yasmine"), blink=blink_at(pose, "Y"), look=-2)
    return finish(img, pose)


def sm_polling(spec, p, t, ctx):
    pose = pose_of(t)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    st = Stage(img, pose)
    st.piece(rect(-20, -20, W + 20, 1180), (214, 206, 176), "cwall", boil=0, shadow=None)
    st.piece(rect(-20, 1180, W + 20, H + 20), (150, 120, 90), "cfloor", boil=0)
    # blackboard with chalk turnout: 10 figures, ~4 filled (38%)
    st.piece(rect(90, 520, 990, 900), (40, 70, 56), "board", boil=0)
    st.d.rectangle((90, 520, 990, 900), outline=(120, 90, 60, 255), width=14)
    st.text((540, 580), "BUREAU DE VOTE", 44, (236, 236, 226), "chalk1", serif=True, boil=0.2)
    shown = int(10 * ease(p / 0.8))
    for k in range(10):
        fx, fy = 160 + k * 78, 760
        c = (236, 200, 90, 255) if k < 4 and k < shown else (220, 220, 210, 160)
        st.d.ellipse((fx - 14, fy - 70, fx + 14, fy - 42), outline=c, width=4, fill=c if (k < 4 and k < shown) else None)
        st.d.line([(fx, fy - 42), (fx, fy)], fill=c, width=4)
        st.d.line([(fx - 20, fy - 26), (fx + 20, fy - 26)], fill=c, width=4)
        st.d.line([(fx, fy), (fx - 16, fy + 30)], fill=c, width=4)
        st.d.line([(fx, fy), (fx + 16, fy + 30)], fill=c, width=4)
    st.text((540, 858), "4 IN 10 VOTED", 34, (236, 200, 90), "chalk2", serif=True, boil=0.2)
    # booths with curtains, all empty, plus the ballot box
    for k, bx in enumerate((150, 360, 570)):
        st.piece(rect(bx, 960, bx + 170, 1300), (200, 196, 190), f"booth{k}", boil=0.2)
        sway = 4 * math.sin(pose * 0.7 + k)
        st.piece(rect(bx + 10 + sway, 980, bx + 160 + sway, 1260), (70, 100, 150), f"cur{k}", boil=0.4)
    st.piece(rect(770, 1080, 960, 1300), (120, 86, 56), "desk", boil=0)
    st.piece(rect(800, 960, 930, 1086), (190, 220, 235, 200), "box", boil=0.3)
    st.d.rectangle((840, 956, 890, 964), fill=(40, 40, 40, 255))
    # Haj walks in to vote; Yasmine turns away at the door and leaves
    hx = 40 + 300 * ease(tq(t) / 2.6)
    walking = tq(t) < 2.6
    haj(st, hx, 1560, s=0.9, face=1, pose="walk" if walking else "stand", walk=pose * 1.2,
        arm_f=20, blink=blink_at(pose, "H"))
    leave = ease((tq(t) - 1.6) / 2.2)
    yx = 920 + 260 * leave
    yasmine(st, yx, 1300, s=0.9, face=(-1 if leave < 0.05 else 1), pose="walk" if 0.05 < leave < 1 else "stand",
            walk=pose * 1.1, arm_f=6, arm_b=-6, blink=blink_at(pose, "Y"))
    return finish(img, pose)


def results_tv(st, x, y, w, h, pose, bars, ctx_line, line_p, key="tv"):
    st.piece(rect(x - 20, y - 20, x + w + 20, y + h + 60), (60, 50, 44), key + "case", boil=0.3)
    st.piece(rect(x, y, x + w, y + h), (24, 32, 44), key + "scr", boil=0.2, shadow=None)
    st.d.text((x + w / 2, y + 34), "RESULTS · 24 SEPT", font=font(26), fill=(230, 230, 230), anchor="mm")
    n = len(bars)
    bw = w / (n * 1.6)
    for i, b in enumerate(bars):
        val = b["value"]
        if "from" in b and b.get("when_line") is not None:
            if ctx_line < b["when_line"]:
                val = b["from"]
            elif ctx_line == b["when_line"]:
                val = b["from"] + (b["value"] - b["from"]) * ease(line_p / 0.6)
        grow = ease((tq_global[0] - 0.1 * i) / 1.2)
        bh = (h - 150) * val / 110 * grow
        bx = x + bw * 0.6 + i * bw * 1.6
        st.piece(rect(bx, y + h - 50 - bh, bx + bw, y + h - 50), b["color"], key + f"bar{i}", boil=0.5, shadow=None)
        st.d.text((bx + bw / 2, y + h - 22), b["label"], font=font(22), fill=(230, 230, 230), anchor="mm")
        st.d.text((bx + bw / 2, y + h - 64 - bh), str(int(round(val * grow))), font=font(30), fill=(255, 255, 255), anchor="mm")


tq_global = [0.0]


def sm_tv_results(spec, p, t, ctx):
    pose = pose_of(t)
    tq_global[0] = tq(t)
    img = set_apartment(True).copy()
    st = Stage(img, pose)
    st.d.ellipse((140, 560, 520, 940), fill=(255, 200, 120, 40))  # lamp glow
    st.piece(rect(310, 740, 350, 980), (80, 60, 40), "lamp", boil=0.2)
    st.piece([(250, 740), (410, 740), (370, 640), (290, 640)], (230, 190, 120), "shade", boil=0.3)
    st.piece(rect(560, 1000, 1000, 1180), (90, 60, 40), "cab", boil=0)
    ctx = ctx or {}
    bars = [{"label": "PAM", "value": 97, "color": GOLD},
            {"label": "RNI", "value": 66, "from": 102, "when_line": 1, "color": (70, 110, 170)},
            {"label": "ISTIQ.", "value": 65, "color": (190, 70, 60)},
            {"label": "PJD", "value": 54, "from": 13, "when_line": 2, "color": (70, 150, 110)}]
    results_tv(st, 580, 620, 400, 360, pose, bars, ctx.get("line", 0), ctx.get("line_p", 0))
    laugh = 10 * math.sin(pose * 2.5) if ctx.get("line") == 2 else 0
    haj(st, 330, 1420 + laugh, s=0.95, face=1, pose="sit", lean=18, arm_f=70,
        mouth=mouth_of(ctx, "haj"), blink=blink_at(pose, "H"))
    yasmine(st, 900, 1310, s=0.78, face=-1, pose="stand", arm_f=110, arm_b=100,
            mouth=mouth_of(ctx, "yasmine"), blink=blink_at(pose, "Y"))
    return finish(img, pose, vignette=0.5)


def sugar_pile(st, x, y, n, key, cube=26):
    """Isometric pile of sugar cubes; n controls pile size (not a literal count)."""
    k = 0
    rows = max(1, int(math.sqrt(n)))
    for r in range(rows):
        for c in range(rows - r):
            cx = x + (c - (rows - r - 1) / 2) * cube * 1.1
            cy = y - r * cube * 0.8
            top = [(cx, cy - cube * 0.5), (cx + cube * 0.5, cy - cube * 0.25), (cx, cy), (cx - cube * 0.5, cy - cube * 0.25)]
            st.piece(top, (250, 250, 246), f"{key}t{k}", boil=0.4, shadow=(3, 4, 40), edge=True)
            st.piece([(cx - cube * 0.5, cy - cube * 0.25), (cx, cy), (cx, cy + cube * 0.5), (cx - cube * 0.5, cy + cube * 0.25)],
                     (222, 222, 216), f"{key}l{k}", boil=0.4, shadow=None)
            st.piece([(cx + cube * 0.5, cy - cube * 0.25), (cx, cy), (cx, cy + cube * 0.5), (cx + cube * 0.5, cy + cube * 0.25)],
                     (200, 200, 194), f"{key}r{k}", boil=0.4, shadow=None)
            k += 1


def flag(st, x, y, text, col, key):
    st.d.line([(x, y), (x, y - 110)], fill=(200, 170, 110, 255), width=4)
    f = font(26)
    tw = st.d.textlength(text, font=f) + 24
    st.piece(rect(x, y - 110, x + tw, y - 70), col, key, boil=0.6, shadow=(3, 4, 60))
    st.d.text((x + 12, y - 90), text, font=f, fill=(20, 16, 12), anchor="lm")


def sm_sugar(spec, p, t, ctx):
    pose = pose_of(t)
    ctx = ctx or {}
    img = Image.new("RGBA", (W, H), (30, 22, 18, 255))
    st = Stage(img, pose)
    # a big engraved brass tray, seen from above
    st.piece(oval(540, 1080, 520, 520, "tray"), (206, 164, 64), "tray", boil=0.2)
    for r in (470, 420):
        st.d.ellipse((540 - r, 1080 - r, 540 + r, 1080 + r), outline=(150, 112, 40, 255), width=4)
    for k in range(16):
        a = k * math.pi / 8
        st.d.line([(540 + 420 * math.cos(a), 1080 + 420 * math.sin(a)), (540 + 470 * math.cos(a), 1080 + 470 * math.sin(a))],
                  fill=(150, 112, 40, 255), width=3)
    for k, gx in enumerate((250, 330)):  # tea glasses pushed aside
        st.piece(oval(gx, 720, 34, 34, f"gl{k}"), (200, 140, 60, 210), f"gl{k}", boil=0.3)
        st.d.ellipse((gx - 34, 686, gx + 34, 754), outline=(240, 230, 200, 200), width=3)
    line, lp = ctx.get("line", 0), ctx.get("line_p", 0)
    # line 0: PAM alone; line 1 ("So who joins them?"): partners slide in; line 2: the RNI is pushed away
    stage_p = {0: 0.0, 1: 0.15 + 0.85 * lp, 2: 1.0}.get(line, 1.0)
    total = 97
    sugar_pile(st, 540, 1130, 36, "pam", cube=40)
    flag(st, 560, 1060, "PAM 97", GOLD, "fpam")
    moves = [("ISTIQLAL 65", 25, (190, 70, 60), (110, 1120), (360, 1180), 0.0),
             ("MP 29", 9, (150, 110, 170), (980, 1470), (720, 1230), 0.3),
             ("UC 17", 4, (110, 160, 190), (990, 1150), (770, 1050), 0.55)]
    hand_at = None
    for name, n, col, a, b, start in moves:
        k = round(ease((stage_p - start) / 0.3) * 6) / 6  # stop-motion steps
        x, y = a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
        sugar_pile(st, x, y, n, "p" + name, cube=40)
        flag(st, x + 16, y - 50, name, col, "f" + name)
        if 0 < k < 1:
            hand_at = (x - 70, y + 30)
        if k >= 1:
            total += int(name.split()[-1])
    rk = ease(lp / 0.5) if line == 2 else 0
    rx, ry = 300 - 150 * rk, 1440 + 110 * rk
    sugar_pile(st, rx, ry, 16, "rni", cube=40)
    flag(st, rx + 16, ry - 50, "RNI 66", (70, 110, 170), "frni")
    if line == 2:
        hand_at = (rx + 110, ry + 40)
        if lp > 0.4:
            st.d.line([(rx - 80, ry - 90), (rx + 80, ry + 40)], fill=(200, 40, 40, 255), width=12)
            st.d.line([(rx + 80, ry - 90), (rx - 80, ry + 40)], fill=(200, 40, 40, 255), width=12)
    ok = total >= 198
    st.piece(rect(560, 560, 1010, 690), (250, 244, 226), "tot", boil=0.4)
    st.d.text((785, 604), f"{total} / 198 SEATS", font=font(42), fill=(40, 120, 60) if ok else (30, 24, 20), anchor="mm")
    st.d.text((785, 654), "MAJORITY ✓" if ok else "NEEDED TO GOVERN", font=font(26),
              fill=(40, 120, 60) if ok else (120, 100, 80), anchor="mm")
    if hand_at:  # grandfather's hand, a cut-out sleeve coming in from the bottom edge
        hx, hy = hand_at
        st.piece([(hx - 44, hy + 30), (hx + 44, hy + 30), (hx + 70, H + 40), (hx - 70, H + 40)], CREAM, "sleeve", boil=0.8)
        st.piece(oval(hx, hy + 10, 50, 44, "hhand"), SKIN_H, "hhand", boil=0.8)
    return finish(img, pose, vignette=0.45)


def sm_tv_leader(spec, p, t, ctx):
    pose = pose_of(t)
    img = set_apartment(True).copy()
    st = Stage(img, pose)
    # big TV: a podium and a speaker silhouette (no likeness), with a lower third
    x, y, w, h = 60, 560, 720, 520
    st.piece(rect(x - 30, y - 30, x + w + 30, y + h + 80), (56, 46, 40), "tvc", boil=0.3)
    st.piece(rect(x, y, x + w, y + h), (40, 70, 96), "tvs", boil=0.2, shadow=None)
    st.d.rectangle((x, y, x + w, y + h), fill=(60, 100, 130, 255))
    for k in range(6):
        st.d.rectangle((x + 40 + k * 125, y + 40, x + 90 + k * 125, y + 180), fill=(170, 40, 50, 255) if k % 2 else (40, 120, 70, 255))
    cx = x + w / 2
    st.piece(oval(cx, y + 250, 50, 58, "spk_h"), (50, 40, 44), "spk_h", boil=0.6)
    st.piece([(cx - 110, y + 470), (cx + 110, y + 470), (cx + 80, y + 300), (cx - 80, y + 300)], (50, 40, 44), "spk_b", boil=0.6)
    st.piece(rect(cx - 150, y + 380, cx + 150, y + h), (120, 90, 60), "podium", boil=0.3)
    st.d.line([(cx - 20, y + 380), (cx - 40, y + 320)], fill=(30, 30, 30, 255), width=5)
    st.d.line([(cx + 20, y + 380), (cx + 40, y + 320)], fill=(30, 30, 30, 255), width=5)
    st.d.rectangle((x, y + h - 110, x + w, y + h - 30), fill=(250, 250, 250, 235))
    st.d.text((x + 24, y + h - 84), "FATIMA-ZAHRA EL MANSOURI", font=font(30), fill=(20, 20, 20), anchor="lm")
    st.d.text((x + 24, y + h - 48), "PAM LEADER", font=font(24), fill=(150, 110, 20), anchor="lm")
    # TV glow on Yasmine, seen from behind-side
    yasmine(st, 880, 1450, s=1.05, face=-1, pose="stand", arm_f=10, arm_b=-4,
            mouth=mouth_of(ctx, "yasmine"), blink=blink_at(pose, "Y"), look=-6)
    return finish(img, pose, vignette=0.55)


def sm_rooftop_night(spec, p, t, ctx):
    pose = pose_of(t)
    img = sky_rooftop(True).copy()
    moon_stars(img, t, pose)
    floodlights(img, 820, 1110, 0.7, pose)
    img.alpha_composite(set_rooftop(True))
    st = Stage(img, pose)
    hospital(st, 300, 1120)
    # Yasmine looks at her voter card, then slips it into her hoodie pocket
    k = ease((tq(t) - 1.2) / 1.4)
    arm_f = 70 - 60 * k
    yasmine(st, 470, 1172, s=1.05, face=1, pose="sit", arm_f=arm_f, arm_b=-10,
            mouth=mouth_of(ctx, "yasmine"), blink=blink_at(pose, "Y"), hold="card" if k < 0.9 else None, look=8 - 10 * k)
    return finish(img, pose, vignette=0.5)


SCENES = {
    "sm_rooftop_dawn": sm_rooftop_dawn,
    "sm_protest": sm_protest,
    "sm_apartment_morning": sm_apartment_morning,
    "sm_polling": sm_polling,
    "sm_tv_results": sm_tv_results,
    "sm_sugar": sm_sugar,
    "sm_tv_leader": sm_tv_leader,
    "sm_rooftop_night": sm_rooftop_night,
}

_cache = {}


def render(spec, p, t, ctx=None):
    """Stop-motion frames are held: identical pose + ctx returns the cached image."""
    name = spec["anim"]
    pose = pose_of(t)
    c = ctx or {}
    lvl = round(c.get("level", 0) * 4) / 4
    key = (name, pose, c.get("speaker"), lvl, c.get("line"), round(c.get("line_p", 0), 1))
    if key not in _cache:
        if len(_cache) > 64:
            _cache.clear()
        ctx2 = dict(c, level=lvl)
        _cache[key] = SCENES[name](spec, p, t, ctx2).convert("RGB")
    return _cache[key]
