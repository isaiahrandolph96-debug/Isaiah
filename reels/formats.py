#!/usr/bin/env python3
"""Reusable video formats for Africa Blind Spot reels.

Each format is a data-driven scene background: pick it in a scene's `bg_spec` with
`{"format": "<name>", ...data}` and render_reel.py draws it every frame, under the
house header, the scene headline (use `"head_y": 420`), captions and progress bar.

Formats (full schemas and examples in README.md → "Format library"; a ready-to-copy
scene for each one is in format-templates/script.json):
    race        bars re-rank from one year to another          (elections, rankings, budgets)
    roundup     story cards with a pulsing pin on the map      (weekly news roundups)
    quiz        clues, a countdown, then the answer on the map (engagement posts)
    myth        a myth is struck out, the reality slides in    (myth-busting, misinformation)
    timeline    dated events appear and scroll                 (background, "how we got here")
    thenvsnow   a slider wipes from THEN to NOW                (one strong comparison)
    kinetic     a quote appears word by word                   (speeches, statements)
    whiteboard  a marker draws the idea on a board             (how a system works)
    carousel    swipe cards, one fact per card                 (fact lists; also works as a photo carousel)
    audiogram   waveform driven by the real narration          (interview or podcast clips)

The animated explainer and the map story are made with anim.py (+ "special": "chips")
and mapviz.py as before.

Timing: every format is designed on a 6.5 s clock and stretched to the scene's real
length, so the same spec works for a 5 s scene or a 12 s one. Content stays inside
y 540..1290, clear of the headline above and the Instagram-safe captions below.
"""
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw

import anim
import mapviz
import render_reel as R

W, H, FPS = R.W, R.H, R.FPS
GOLD, WHITE = R.GOLD, R.WHITE
F = R.font
DESIGN = 6.5  # seconds each format is choreographed for
TOP, BOTTOM = 540, 1290  # content box: below the headline, above the captions
PALETTE = [GOLD, (70, 110, 170), (190, 70, 60), (70, 150, 110), (150, 90, 170), (200, 130, 50), (90, 160, 180)]


def e(x):
    return R.ease_out(x)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def dark_bg(glow=(90, 62, 14)):
    img = anim.gradient((8, 7, 6), (20, 15, 8)).copy()
    anim.put_glow(img, 540, 1000, 520, glow, 0.45)
    return img


def text(d, xy, s, size, col=WHITE, anchor="mm", stroke=3, alpha=255):
    d.text(xy, s, font=F(int(size)), fill=(*col[:3], int(alpha)), anchor=anchor, stroke_width=stroke,
           stroke_fill=(0, 0, 0, int(alpha * 0.85)))


def fit(d, s, size, max_w, floor=22):
    """Largest font size <= size at which s fits in max_w."""
    while size > floor and d.textlength(s, font=F(int(size))) > max_w:
        size -= 2
    return size


def wrap(d, s, size, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=F(int(size))) > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    return lines + [cur]


def color(c, i):
    return tuple(c) if c else PALETTE[i % len(PALETTE)]


# ---------------------------------------------------------------- race

_race = {}


def race(spec, u, t, ctx):
    """{"items": [[name, from, to, color?], ...], "from_label": "2021", "to_label": "2026", "max": 110}"""
    items = [(it[0], it[1], it[2], color(it[3] if len(it) > 3 else None, i)) for i, it in enumerate(spec["items"])]
    img = dark_bg()
    d = ImageDraw.Draw(img, "RGBA")
    k = e((u - 0.8) / 4.0)
    vals = [(n, a + (b - a) * k, c) for n, a, b, c in items]
    ranks = {n: i for i, (n, _, _) in enumerate(sorted(vals, key=lambda r: -r[1]))}
    st = _race.get(id(spec))
    if st is None or u < st["u"]:  # new scene (or rewound): start from the opening order
        st = {"pos": {n: float(i) for i, (n, *_) in enumerate(sorted(items, key=lambda r: -r[1]))}}
    st["u"] = u
    _race[id(spec)] = st
    for n, _, _ in vals:  # bars glide to their new rank
        st["pos"][n] += (ranks[n] - st["pos"][n]) * 0.18
    fl, tl = str(spec.get("from_label", "")), str(spec.get("to_label", ""))
    if fl.isdigit() and tl.isdigit():
        label = str(int(fl) + int(round((int(tl) - int(fl)) * k)))
    else:
        label = tl if k > 0.5 else fl
    text(d, (880, 630), label, 120, WHITE, alpha=70, stroke=0)
    vmax = spec.get("max") or max(max(a, b) for _, a, b, _ in items) * 1.13
    step = min(150, (BOTTOM - 40 - 720) / max(1, len(items)))
    bh = step * 0.67
    for n, v, c in vals:
        y = 720 + st["pos"][n] * step
        wbar = max(8, 700 * v / vmax)
        d.rounded_rectangle((110, y, 110 + wbar, y + bh), radius=12, fill=(*c, 255))
        text(d, (130, y + bh / 2), n, fit(d, n, 36, max(60, wbar - 40)), (20, 16, 10), anchor="lm", stroke=0)
        text(d, (130 + wbar, y + bh / 2), f"  {v:,.{spec.get('decimals', 0)}f}{spec.get('suffix', '')}", 44, WHITE, anchor="lm")
    return img


# ---------------------------------------------------------------- roundup

def roundup(spec, u, t, ctx):
    """{"items": [{"title", "body", "place", "view"?}, ...], "view"?}
    place: a mapviz.PLACES name. The map centres on it unless a "view" is given (see mapviz.resolve_view)."""
    items = spec["items"]
    n = len(items)
    i = min(n - 1, int(u / (DESIGN / n)))
    lt = u - i * DESIGN / n
    it = items[i]
    mspec = {"view": it.get("view", spec.get("view", it["place"])), "highlight": it.get("highlight", []), "labels": False, "dim": 0.8,
             "rings": {"at": it["place"], "start": 0.0, "radius": 160}, "capitals": [it["place"]]}
    img = mapviz.render(mspec, 0.5, t).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    a = e(lt / 0.25)
    body = wrap(d, it["body"], 38, 860)
    hgt = 110 + 50 * len(body)
    y0 = BOTTOM - 20 - hgt + (1 - a) * 80
    d.rounded_rectangle((70, y0, 1010, y0 + hgt), radius=24, fill=(12, 10, 8, int(225 * a)), outline=(*GOLD, int(255 * a)), width=4)
    title = f"{i + 1}/{n}  {it['title']}"
    text(d, (110, y0 + 55), title, fit(d, title, 40, 860), GOLD, anchor="lm", alpha=255 * a)
    for k, ln in enumerate(body):
        text(d, (110, y0 + 115 + k * 50), ln, 38, WHITE, anchor="lm", alpha=255 * a)
    return img


# ---------------------------------------------------------------- quiz

def quiz(spec, u, t, ctx):
    """{"clues": [3 short clues], "answer": "MOROCCO", "place": "Rabat", "prompt": "Did you get it? Comment below"}"""
    clues = spec["clues"]
    reveal_at = 5.0
    if u > reveal_at and spec.get("place"):
        mspec = {"view": spec.get("view", spec["place"]), "highlight": spec.get("highlight", []), "labels": False,
                 "dim": 0.85, "rings": {"at": spec["place"], "radius": 200}, "capitals": [spec["place"]]}
        img = mapviz.render(mspec, 0.5, t).convert("RGBA")
    else:
        img = dark_bg((40, 60, 120))
    d = ImageDraw.Draw(img, "RGBA")
    if u <= reveal_at:
        gap = 3.3 / max(1, len(clues))
        step = min(150, 420 / max(1, len(clues)))
        for k, c in enumerate(clues):
            a = e((u - 0.3 - k * gap) / 0.3)
            if a <= 0:
                continue
            y = 640 + k * step
            d.rounded_rectangle((90, y, 990, y + step - 40), radius=20, fill=(20, 20, 30, int(230 * a)),
                                outline=(*GOLD, int(200 * a)), width=3)
            text(d, (130, y + (step - 40) / 2), f"CLUE {k + 1}", 30, GOLD, anchor="lm", alpha=255 * a)
            text(d, (310, y + (step - 40) / 2), c, fit(d, c, 34, 650), WHITE, anchor="lm", alpha=255 * a)
        if u > 3.6:  # countdown ring
            n = 3 - int((u - 3.6) / 0.47)
            frac = ((u - 3.6) % 0.47) / 0.47
            d.arc((460, 1100, 620, 1260), -90, -90 + 360 * (1 - frac), fill=GOLD, width=12)
            text(d, (540, 1180), str(max(1, n)), 80, WHITE)
    else:
        a = e((u - reveal_at) / 0.3)
        s = 0.7 + 0.3 * a
        ans = spec["answer"]
        text(d, (540, 1110), ans, fit(d, ans, 110, 900) * s, GOLD, alpha=255 * a, stroke=5)
        text(d, (540, 1215), spec.get("prompt", "Did you get it? Comment below"), 34, WHITE, alpha=255 * a)
    return img


# ---------------------------------------------------------------- myth vs reality

def myth(spec, u, t, ctx):
    """{"myth": "Africa is a country", "reality": "54 countries", "detail": "1.4+ billion people"}"""
    img = dark_bg()
    d = ImageDraw.Draw(img, "RGBA")
    a = e((u - 0.3) / 0.3)
    d.rounded_rectangle((90, 590, 990, 830), radius=24, fill=(60, 16, 16, int(230 * a)), outline=(200, 60, 60, int(255 * a)), width=4)
    text(d, (540, 645), "MYTH", 36, (230, 110, 110), alpha=255 * a)
    m = f"“{spec['myth']}”"
    text(d, (540, 740), m, fit(d, m, 56, 820), WHITE, alpha=255 * a)
    if u > 1.8:  # stamp a red X across the myth
        k = e((u - 1.8) / 0.25)
        d.line([(160, 620), (160 + 760 * k, 620 + 190 * k)], fill=(220, 40, 40, 255), width=16)
        d.line([(920, 620), (920 - 760 * k, 620 + 190 * k)], fill=(220, 40, 40, 255), width=16)
    b = e((u - 2.6) / 0.35)
    if b > 0:
        y = 890 + (1 - b) * 60
        d.rounded_rectangle((90, y, 990, y + 330), radius=24, fill=(12, 34, 20, int(235 * b)), outline=(*GOLD, int(255 * b)), width=4)
        text(d, (540, y + 65), "REALITY", 36, GOLD, alpha=255 * b)
        r = spec["reality"]
        text(d, (540, y + 160), r, fit(d, r, 70, 820), WHITE, alpha=255 * b, stroke=4)
        if spec.get("detail"):
            text(d, (540, y + 255), spec["detail"], fit(d, spec["detail"], 48, 820), WHITE, alpha=255 * b)
    return img


# ---------------------------------------------------------------- timeline

def timeline(spec, u, t, ctx):
    """{"events": [[date, what], ...]}  (any number; older ones scroll up under the headline)"""
    ev = spec["events"]
    img = dark_bg()
    d = ImageDraw.Draw(img, "RGBA")
    per = min(1.1, 5.2 / max(1, len(ev)))  # seconds between events
    shown = u / per
    step, first = 150, 700
    fits = int((BOTTOM - 60 - first) / step) + 1  # events visible at once
    scroll = max(0.0, shown - fits + 0.2) * step
    x = 170
    d.line([(x, 600), (x, BOTTOM - 30)], fill=(*GOLD, 120), width=5)
    for k, (date, what) in enumerate(ev):
        a = e(shown - k)
        y = first + k * step - scroll
        a *= clamp((y - 580) / 110)  # fade out under the headline
        if a <= 0 or y > BOTTOM - 40:
            continue
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(*GOLD, int(255 * a)))
        text(d, (x + 50, y - 26), date, 34, GOLD, anchor="lm", alpha=255 * a)
        text(d, (x + 50, y + 24), what, fit(d, what, 34, 820), WHITE, anchor="lm", alpha=255 * a)
    return img


# ---------------------------------------------------------------- then vs now

def people(d, cx, cy, filled, col):
    for k in range(10):
        x = cx - 180 + (k % 5) * 90
        y = cy + (k // 5) * 150
        c = (*col, 255) if k < filled else (90, 86, 80, 255)
        d.ellipse((x - 18, y - 70, x + 18, y - 34), fill=c)
        d.rounded_rectangle((x - 26, y - 28, x + 26, y + 40), radius=12, fill=c)


def thenvsnow(spec, u, t, ctx):
    """{"then": {"label": "2021", "value": "50%", "filled": 5}, "now": {"label": "2026", "value": "38%", "filled": 4}}
    "filled" (0-10) is optional: it draws a 10-person icon row, i.e. "5 in 10"."""
    img = dark_bg()
    d = ImageDraw.Draw(img, "RGBA")
    slider = W * (1 - e((u - 1.5) / 2.5))
    sides = []
    for key, col in (("then", (200, 200, 200)), ("now", GOLD)):
        s = spec[key]
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay, "RGBA")
        text(dl, (540, 640), s["label"], 60, WHITE if key == "then" else GOLD)
        text(dl, (540, 760), s["value"], fit(dl, s["value"], 130, 900), WHITE if key == "then" else GOLD, stroke=5)
        if "filled" in s:
            people(dl, 540, 1000, s["filled"], col)
        elif s.get("note"):
            text(dl, (540, 960), s["note"], fit(dl, s["note"], 44, 860), WHITE)
        sides.append(lay)
    for lay, box in ((sides[0], (0, 0, slider, H)), (sides[1], (slider, 0, W, H))):
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).rectangle(box, fill=255)
        img.paste(lay, (0, 0), Image.composite(lay.getchannel("A"), Image.new("L", (W, H), 0), mask))
    if 5 < slider < W - 5:
        d.line([(slider, 570), (slider, BOTTOM - 20)], fill=GOLD, width=6)
        d.ellipse((slider - 28, 900 - 28, slider + 28, 900 + 28), fill=GOLD)
    return img


# ---------------------------------------------------------------- kinetic quote

def kinetic(spec, u, t, ctx):
    """{"quote": "The Sahel must not be abandoned to its desolate fate.", "gold": ["SAHEL", "ABANDONED"],
        "by": "Bassirou Diomaye Faye, President of Senegal", "where": "UN General Assembly · Sept 2026"}"""
    img = dark_bg((60, 40, 20))
    d = ImageDraw.Draw(img, "RGBA")
    gold = {g.upper() for g in spec.get("gold", [])}
    words = f"“{spec['quote'].upper()}”".split()
    key = lambda w: w.strip("“”.,!?;:")  # noqa: E731
    lines, cur = [], []  # gold words get a line of their own when they are long
    for w in words:
        if key(w) in gold and len(key(w)) > 6:
            if cur:
                lines.append(cur)
            lines.append([w])
            cur = []
            continue
        if cur and d.textlength(" ".join(cur + [w]), font=F(84)) > 900:
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    lh = min(130, (1110 - 630) / max(1, len(lines) - 1)) if len(lines) > 1 else 0
    per = min(0.32, 3.4 / max(1, len(words)))
    k = 0
    for li, ln in enumerate(lines):
        y = 630 + li * lh
        size = 110 if any(key(w) in gold for w in ln) else 84
        size = fit(d, " ".join(ln), size, 960)
        widths = [d.textlength(w + " ", font=F(size)) for w in ln]
        x = 540 - sum(widths) / 2
        for w, wd in zip(ln, widths):
            a = e((u - 0.25 - k * per) / 0.2)
            if a > 0:
                col = GOLD if key(w) in gold else WHITE
                text(d, (x + wd / 2, y), w, size * (1.25 - 0.25 * a), col, alpha=255 * a, stroke=4)
            x += wd
            k += 1
    a = e((u - 4.0) / 0.4)
    if spec.get("by"):
        text(d, (540, 1215), spec["by"], fit(d, spec["by"], 32, 940), WHITE, alpha=255 * a)
    if spec.get("where"):
        text(d, (540, 1258), spec["where"], 28, GOLD, alpha=255 * a)
    return img


# ---------------------------------------------------------------- whiteboard

def _wobble(pts, amt, seed):
    r = np.random.default_rng(seed)
    return [(x + r.uniform(-amt, amt), y + r.uniform(-amt, amt)) for x, y in pts]


INK = {"ink": (30, 34, 44), "red": (200, 50, 40), "blue": (40, 90, 200), "green": (40, 140, 70), "gold": (190, 140, 20)}


def _draw_item(d, it, k, seed):
    """Draw one doodle item at progress k (0..1). Returns where the pen is."""
    col = (*INK.get(it.get("color", "ink"), INK["ink"]), 255)
    typ = it["type"]
    if typ == "text":
        s = it["text"][:int(len(it["text"]) * k)]
        size = it.get("size", 56)
        x, y = it["at"]
        if not s:
            return x - d.textlength(it["text"], font=F(size)) / 2, y
        d.text((x, y), s, font=F(size), fill=col, anchor="mm")
        full = d.textlength(it["text"], font=F(size))
        return x - full / 2 + d.textlength(s, font=F(size)), y + size * 0.3
    if typ in ("line", "arrow"):
        (x0, y0), (x1, y1) = it["from"], it["to"]
        xe, ye = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        d.line(_wobble([(x0, y0), ((x0 + xe) / 2, (y0 + ye) / 2), (xe, ye)], 1.5, seed), fill=col, width=7, joint="curve")
        if typ == "arrow" and k > 0.95:
            ang = math.atan2(y1 - y0, x1 - x0)
            for s in (-1, 1):
                d.line([(x1, y1), (x1 - 40 * math.cos(ang + s * 0.5), y1 - 40 * math.sin(ang + s * 0.5))], fill=col, width=7)
        return xe, ye
    if typ == "circle":
        cx, cy = it["at"]
        r = it.get("r", 80)
        n = max(1, int(48 * k))
        pts = [(cx + r * math.cos(-math.pi / 2 + 2 * math.pi * i / 48), cy + r * math.sin(-math.pi / 2 + 2 * math.pi * i / 48))
               for i in range(n + 1)]
        d.line(_wobble(pts, 1.5, seed), fill=col, width=6, joint="curve")
        return pts[-1]
    if typ == "hemicycle":  # a parliament: arc, then seat dots, then an optional split line
        cx, cy = it["at"]
        r = it.get("r", 330)
        ka, kd, kl = clamp(k / 0.45), clamp((k - 0.35) / 0.45), clamp((k - 0.85) / 0.15)
        n = int(60 * ka)
        pts = [(cx + r * math.cos(math.pi + math.pi * i / 60), cy + r * math.sin(math.pi + math.pi * i / 60)) for i in range(n + 1)]
        pen = pts[-1]
        if len(pts) > 1:
            d.line(_wobble(pts, 1.5, seed), fill=col, width=7, joint="curve")
        for i in range(int(40 * kd)):
            a = math.pi + math.pi * (i + 0.5) / 40
            for rr in (r * 0.66, r * 0.82):
                x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
                d.ellipse((x - 8, y - 8, x + 8, y + 8), outline=col, width=3)
                pen = (x, y)
        if it.get("split") and kl > 0:
            red = (*INK["red"], 255)
            d.line([(cx, cy), (cx, cy - (r + 30) * kl)], fill=red, width=6)
            pen = (cx, cy - (r + 30) * kl)
        return pen
    raise ValueError(f"unknown whiteboard item {typ}")


def whiteboard(spec, u, t, ctx):
    """{"items": [{"type": "hemicycle", "at": [540, 1180], "r": 330, "split": true},
                  {"type": "text", "text": "395 SEATS", "at": [540, 1240], "size": 52},
                  {"type": "text", "text": "198 = MAJORITY", "at": [540, 690], "color": "red"},
                  {"type": "arrow"|"line", "from": [x, y], "to": [x, y]}, {"type": "circle", "at": [x, y], "r": 80}]}
    Items are drawn in order (the pen moves between them); "start"/"len" (design seconds) override the timing.
    Colours: ink, red, blue, green, gold. Keep items inside x 90..990, y 570..1260."""
    img = dark_bg((40, 40, 40))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((60, TOP, 1020, BOTTOM - 10), radius=18, fill=(244, 240, 230, 255), outline=(150, 150, 150, 255), width=10)
    items = spec["items"]
    slot = 5.2 / max(1, len(items))
    pen = (160, 1180)
    for i, it in enumerate(items):
        s0 = it.get("start", 0.2 + i * slot)
        ln = it.get("len", slot * 0.95)
        k = clamp((u - s0) / ln)
        if k <= 0:
            continue
        pen = _draw_item(d, it, e(k) if it["type"] == "text" else k, seed=i + 3)  # pen follows the newest stroke
    px, py = pen  # marker pen
    d.polygon([(px, py), (px + 30, py - 70), (px + 60, py - 55), (px + 18, py + 8)], fill=(40, 90, 200, 255))
    d.polygon([(px + 30, py - 70), (px + 60, py - 55), (px + 110, py - 190), (px + 80, py - 205)], fill=(30, 30, 36, 255))
    return img


# ---------------------------------------------------------------- carousel

def carousel(spec, u, t, ctx):
    """{"slides": [[big, small], ...], "tag": "EBOLA IN DR CONGO", "source": "Sources: WHO · CDC · UN"}"""
    slides = spec["slides"]
    n = len(slides)
    img = dark_bg((20, 20, 30))
    d = ImageDraw.Draw(img, "RGBA")
    per = DESIGN / n
    pos = sum(e((u - k * per) / 0.45) for k in range(1, n))
    cw = 820
    for i, (big, small) in enumerate(slides):
        x0 = 130 + (i - pos) * (cw + 40)
        if x0 > W or x0 + cw < 0:
            continue
        d.rounded_rectangle((x0, 570, x0 + cw, 1235), radius=30, fill=(18, 16, 12, 255), outline=(*GOLD, 255), width=4)
        if spec.get("tag"):
            text(d, (x0 + cw / 2, 635), f"{i + 1}/{n} · {spec['tag']}", 30, GOLD)
        text(d, (x0 + cw / 2, 830), big, fit(d, big, 170, cw - 80), GOLD, stroke=5)
        for k, ln in enumerate(wrap(d, small, 44, cw - 100)[:4]):
            text(d, (x0 + cw / 2, 1000 + k * 58), ln, 44, WHITE)
        if spec.get("source"):
            text(d, (x0 + cw / 2, 1200), spec["source"], 24, (180, 176, 168), stroke=0)
    active = int(round(pos))
    for k in range(n):
        c = GOLD if k == active else (110, 106, 100)
        x = 540 + (k - (n - 1) / 2) * 40
        d.ellipse((x - 10, 1265 - 10, x + 10, 1265 + 10), fill=c)
    return img


# ---------------------------------------------------------------- audiogram

_env = {}


def _levels(path):
    if path not in _env:
        raw = subprocess.run([R.FFMPEG, "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        a = np.frombuffer(raw, np.float32)
        hop = 16000 // FPS
        rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)])
        _env[path] = rms / (rms.max() + 1e-6)
    return _env[path]


def audiogram(spec, u, t, ctx):
    """{"badge": "ABS", "badge_sub": "PODCAST", "map": {mapviz spec, optional}, "audio": "vo/01.mp3" (optional),
        "offset": seconds into the audio (optional)}
    With no "audio", the waveform follows the scene's own voice clip, so it moves with the narration."""
    ctx = ctx or {}
    path = spec.get("audio")
    if path and not os.path.isabs(path):
        path = os.path.join(ctx.get("reel_dir", "."), path)
    path = path or ctx.get("vo")
    lv = _levels(path) if path else np.zeros(1)
    if spec.get("map"):
        img = mapviz.render(spec["map"], 0.5, t).convert("RGBA")
    else:
        img = dark_bg()
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((440, 590, 640, 790), fill=(18, 16, 12, 255), outline=GOLD, width=5)
    text(d, (540, 670), spec.get("badge", "ABS"), 60, GOLD)
    text(d, (540, 730), spec.get("badge_sub", "PODCAST"), 22, WHITE, stroke=0)
    i = int((t + spec.get("offset", 0.0)) * FPS)
    for b in range(36):  # waveform bars from the real audio
        j = i - (18 - b) * 2
        v = lv[j] if 0 <= j < len(lv) else 0.02
        h = 20 + 340 * v
        x = 540 - 36 * 14 + b * 28
        d.rounded_rectangle((x, 1030 - h / 2, x + 16, 1030 + h / 2), radius=8, fill=(*GOLD, 230))
    return img


FORMATS = {"race": race, "roundup": roundup, "quiz": quiz, "myth": myth, "timeline": timeline,
           "thenvsnow": thenvsnow, "kinetic": kinetic, "whiteboard": whiteboard, "carousel": carousel,
           "audiogram": audiogram}


def render(spec, p, t, dur, ctx=None):
    """Full-frame RGBA background for format spec["format"] at local time t of a scene lasting dur seconds."""
    u = t * DESIGN / max(dur, 0.01)  # design clock
    return FORMATS[spec["format"]](spec, u, t, ctx).convert("RGBA")
