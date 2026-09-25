#!/usr/bin/env python3
"""Render a sampler reel: a ~6.5 s mini example of every Africa Blind Spot video format.

Usage: python3 format_samples.py <out_dir> [--endcard brand_reel.mp4]
Uses only facts verified in this repo's briefings (as of 25 Sept 2026).
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim  # noqa: E402
import mapviz  # noqa: E402
import render_reel as R  # noqa: E402

W, H, FPS = R.W, R.H, R.FPS
GOLD, WHITE, GREY = R.GOLD, R.WHITE, R.GREY
F = R.font
SEG = 6.5  # seconds per format
HERE = os.path.dirname(os.path.abspath(__file__))


def e(x):
    return R.ease_out(x)


def dark_bg(glow=(90, 62, 14)):
    img = anim.gradient((8, 7, 6), (20, 15, 8)).copy()
    anim.put_glow(img, 540, 1100, 520, glow, 0.45)
    return img


def text(d, xy, s, size, col=WHITE, anchor="mm", stroke=3, alpha=255):
    d.text(xy, s, font=F(size), fill=(*col[:3], int(alpha)), anchor=anchor, stroke_width=stroke,
           stroke_fill=(0, 0, 0, int(alpha * 0.85)))


def wrap(d, s, size, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=F(size)) > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    return lines + [cur]


# ---------------------------------------------------------------- 1. explainer

def f_explainer(t):
    p = t / SEG
    img = anim.render({"anim": "pylons"}, p, t).convert("RGBA")
    img.alpha_composite(R.headline_layer(["UP TO", "1,000 MEGAWATTS"], 1, cy=420))
    img.alpha_composite(R.chips_layer(p * 1.4, {"chips": [{"label": "VOLTAGE", "value": "400 kV"},
                                                          {"label": "CAPACITY", "value": "1,000 MW", "hi": True}]}))
    return img, "Uganda's new line to South Sudan is built to carry up to 1,000 megawatts."


# ---------------------------------------------------------------- 2. map story

def f_map(t):
    p = t / SEG
    spec = {"view": "east", "highlight": ["Uganda", "S. Sudan"],
            "label_pos": {"Uganda": [33.1, 2.6], "S. Sudan": [33.2, 5.35]},
            "route": {"grow": [0.1, 0.8], "places": ["Olwiyo", "Nimule", "Juba"],
                      "label_side": {"Olwiyo": "l", "Nimule": "r", "Juba": "l"},
                      "segments": [{"between": ["Olwiyo", "Nimule"], "text": "UGANDA · 150 KM"},
                                   {"between": ["Nimule", "Juba"], "text": "SOUTH SUDAN · 149 KM"}]}}
    img = mapviz.render(spec, p, t).convert("RGBA")
    img.alpha_composite(R.headline_layer(["299 KM", "OF POWER LINE"], 0, cy=420))
    return img, "A 299 km power line from Olwiyo, through Nimule, to Juba."


# ---------------------------------------------------------------- 3. data race

RACE = [("PAM", 87, 97, GOLD), ("RNI", 102, 66, (70, 110, 170)),
        ("ISTIQLAL", 81, 65, (190, 70, 60)), ("PJD", 13, 54, (70, 150, 110))]


def f_race(t):
    img = dark_bg()
    d = ImageDraw.Draw(img, "RGBA")
    k = e((t - 0.8) / 4.0)
    vals = [(n, a + (b - a) * k, c) for n, a, b, c in RACE]
    order = sorted(vals, key=lambda r: -r[1])
    ranks = {n: i for i, (n, _, _) in enumerate(order)}
    if not hasattr(f_race, "pos"):
        f_race.pos = {n: float(i) for i, (n, _, _, _) in enumerate(sorted(RACE, key=lambda r: -r[1]))}
    for n, v, c in vals:  # bars glide to their new rank
        f_race.pos[n] += (ranks[n] - f_race.pos[n]) * 0.18
    year = 2021 + int(round(5 * k))
    text(d, (880, 640), str(year), 120, (255, 255, 255), alpha=70, stroke=0)
    for n, v, c in vals:
        y = 760 + f_race.pos[n] * 150
        wbar = 700 * v / 110
        d.rounded_rectangle((110, y, 110 + wbar, y + 100), radius=12, fill=(*c, 255))
        text(d, (130, y + 50), n, 36, (20, 16, 10), anchor="lm", stroke=0)
        text(d, (130 + wbar, y + 50), f"  {int(round(v))}", 44, WHITE, anchor="lm")
    img.alpha_composite(R.headline_layer(["MOROCCO'S PARLIAMENT", "SEATS · 2021 → 2026"], 1, cy=420))
    return img, "Morocco's parliament: seats won in 2021 versus 2026."


# ---------------------------------------------------------------- 4. roundup

ROUND = [("MOROCCO", "PAM wins most seats (97). Turnout: 38%.", "Rabat"),
         ("UGANDA → SOUTH SUDAN", "$121M power line gets under way.", "Juba"),
         ("DR CONGO", "Ebola: 7,773 cases, 2nd-largest outbreak on record.", "Bunia"),
         ("NIGERIA", "Minerals investment framework signed with the US.", "Abuja")]


def f_roundup(t):
    i = min(3, int(t / (SEG / 4)))
    lt = t - i * SEG / 4
    title, body, place = ROUND[i]
    spec = {"view": "africa", "highlight": [], "labels": False, "dim": 0.8,
            "rings": {"at": place, "start": 0.0, "radius": 160}, "capitals": [place]}
    img = mapviz.render(spec, 0.5, t).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    a = e(lt / 0.25)
    y0 = 1180 + (1 - a) * 80
    d.rounded_rectangle((70, y0, 1010, y0 + 250), radius=24, fill=(12, 10, 8, int(225 * a)), outline=(*GOLD, int(255 * a)), width=4)
    text(d, (110, y0 + 60), f"{i + 1}/4  {title}", 40, GOLD, anchor="lm", alpha=255 * a)
    for k, ln in enumerate(wrap(d, body, 38, 860)):
        text(d, (110, y0 + 130 + k * 50), ln, 38, WHITE, anchor="lm", alpha=255 * a)
    img.alpha_composite(R.headline_layer(["AFRICA", "THIS WEEK"], 1, cy=420))
    return img, None


# ---------------------------------------------------------------- 5. quiz

CLUES = ["Its parliament has 395 seats", "It co-hosts the 2030 World Cup", "Its capital is Rabat"]


def f_quiz(t):
    reveal = t > 5.0
    if reveal:
        spec = {"view": "africa", "highlight": [], "labels": False, "dim": 0.85,
                "rings": {"at": "Rabat", "radius": 200}, "capitals": ["Rabat"]}
        img = mapviz.render(spec, 0.5, t).convert("RGBA")
    else:
        img = dark_bg((40, 60, 120))
    d = ImageDraw.Draw(img, "RGBA")
    img.alpha_composite(R.headline_layer(["GUESS", "THE COUNTRY"], 1, cy=420))
    if not reveal:
        for k, c in enumerate(CLUES):
            a = e((t - 0.3 - k * 1.1) / 0.3)
            if a <= 0:
                continue
            y = 700 + k * 150
            d.rounded_rectangle((90, y, 990, y + 110), radius=20, fill=(20, 20, 30, int(230 * a)), outline=(*GOLD, int(200 * a)), width=3)
            text(d, (130, y + 55), f"CLUE {k + 1}", 30, GOLD, anchor="lm", alpha=255 * a)
            text(d, (310, y + 55), c, 34, WHITE, anchor="lm", alpha=255 * a)
        if t > 3.6:  # countdown ring
            n = 3 - int((t - 3.6) / 0.47)
            frac = ((t - 3.6) % 0.47) / 0.47
            d.arc((440, 1180, 640, 1380), -90, -90 + 360 * (1 - frac), fill=GOLD, width=12)
            text(d, (540, 1280), str(max(1, n)), 90, WHITE)
    else:
        a = e((t - 5.0) / 0.3)
        s = 0.7 + 0.3 * a
        text(d, (540, 1150), "MOROCCO", int(110 * s), GOLD, alpha=255 * a, stroke=5)
        text(d, (540, 1250), "Did you get it? Comment below", 34, WHITE, alpha=255 * a)
    return img, None


# ---------------------------------------------------------------- 6. myth vs reality

def f_myth(t):
    img = dark_bg()
    d = ImageDraw.Draw(img, "RGBA")
    img.alpha_composite(R.headline_layer(["MYTH", "VS REALITY"], 1, cy=420))
    a = e((t - 0.3) / 0.3)
    d.rounded_rectangle((90, 620, 990, 900), radius=24, fill=(60, 16, 16, int(230 * a)), outline=(200, 60, 60, int(255 * a)), width=4)
    text(d, (540, 690), "MYTH", 36, (230, 110, 110), alpha=255 * a)
    text(d, (540, 790), "“Africa is a country”", 56, WHITE, alpha=255 * a)
    if t > 1.8:  # stamp a red X across the myth
        k = e((t - 1.8) / 0.25)
        d.line([(160, 650), (160 + 760 * k, 650 + 220 * k)], fill=(220, 40, 40, 255), width=16)
        d.line([(920, 650), (920 - 760 * k, 650 + 220 * k)], fill=(220, 40, 40, 255), width=16)
    b = e((t - 2.6) / 0.35)
    if b > 0:
        y = 980 + (1 - b) * 60
        d.rounded_rectangle((90, y, 990, y + 330), radius=24, fill=(12, 34, 20, int(235 * b)), outline=(*GOLD, int(255 * b)), width=4)
        text(d, (540, y + 70), "REALITY", 36, GOLD, alpha=255 * b)
        text(d, (540, y + 160), "54 countries", 70, WHITE, alpha=255 * b, stroke=4)
        text(d, (540, y + 250), "1.4+ billion people", 48, WHITE, alpha=255 * b)
    return img, None


# ---------------------------------------------------------------- 7. timeline

TL = [("SEPT 2021", "RNI wins the election (102 seats)"),
      ("SEPT–OCT 2025", "Gen Z 212 youth protests"),
      ("FEB 2026", "Akhannouch steps down as RNI leader"),
      ("23 SEPT 2026", "Morocco votes; turnout 38%"),
      ("24 SEPT 2026", "PAM comes first with 97 seats")]


def f_timeline(t):
    img = dark_bg()
    d = ImageDraw.Draw(img, "RGBA")
    shown = t / 1.1
    scroll = max(0.0, shown - 3.2) * 150
    x = 170
    d.line([(x, 720), (x, 1500)], fill=(*GOLD, 120), width=5)
    for k, (date, what) in enumerate(TL):
        a = e(shown - k)
        if a <= 0:
            continue
        y = 820 + k * 170 - scroll
        a *= max(0.0, min(1.0, (y - 700) / 110))  # fade out under the headline
        if a <= 0 or y > 1520:
            continue
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(*GOLD, int(255 * a)))
        text(d, (x + 50, y - 26), date, 34, GOLD, anchor="lm", alpha=255 * a)
        text(d, (x + 50, y + 24), what, 34, WHITE, anchor="lm", alpha=255 * a)
    img.alpha_composite(R.headline_layer(["HOW WE GOT HERE", "MOROCCO 2021 → 2026"], 1, cy=420))
    return img, None


# ---------------------------------------------------------------- 8. then vs now

def people(d, cx, cy, filled, col, a):
    for k in range(10):
        x = cx - 180 + (k % 5) * 90
        y = cy + (k // 5) * 150
        c = (*col, int(255 * a)) if k < filled else (90, 86, 80, int(255 * a))
        d.ellipse((x - 18, y - 70, x + 18, y - 34), fill=c)
        d.rounded_rectangle((x - 26, y - 28, x + 26, y + 40), radius=12, fill=c)


def f_thenvsnow(t):
    img = dark_bg()
    d = ImageDraw.Draw(img, "RGBA")
    img.alpha_composite(R.headline_layer(["MOROCCO VOTER TURNOUT", "THEN VS NOW"], 1, cy=420))
    slider = 1080 * (1 - e((t - 1.5) / 2.5))
    then = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dt = ImageDraw.Draw(then, "RGBA")
    text(dt, (540, 700), "2021", 60, WHITE)
    text(dt, (540, 800), "50%", 130, WHITE, stroke=5)
    people(dt, 540, 1030, 5, (200, 200, 200), 1)
    now = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dn = ImageDraw.Draw(now, "RGBA")
    text(dn, (540, 700), "2026", 60, GOLD)
    text(dn, (540, 800), "38%", 130, GOLD, stroke=5)
    people(dn, 540, 1030, 4, GOLD, 1)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rectangle((0, 0, slider, H), fill=255)
    img.paste(then, (0, 0), Image.composite(then.getchannel("A"), Image.new("L", (W, H), 0), mask))
    inv = Image.new("L", (W, H), 0)
    ImageDraw.Draw(inv).rectangle((slider, 0, W, H), fill=255)
    img.paste(now, (0, 0), Image.composite(now.getchannel("A"), Image.new("L", (W, H), 0), inv))
    if 5 < slider < W - 5:
        d.line([(slider, 600), (slider, 1400)], fill=GOLD, width=6)
        d.ellipse((slider - 28, 1000 - 28, slider + 28, 1000 + 28), fill=GOLD)
    return img, None


# ---------------------------------------------------------------- 9. kinetic typography

QUOTE = ["“THE", "SAHEL", "MUST", "NOT", "BE", "ABANDONED", "TO", "ITS", "DESOLATE", "FATE.”"]
QGOLD = {"SAHEL", "ABANDONED"}


def f_kinetic(t):
    img = dark_bg((60, 40, 20))
    d = ImageDraw.Draw(img, "RGBA")
    lines = [QUOTE[0:2], QUOTE[2:5], QUOTE[5:6], QUOTE[6:9], QUOTE[9:10]]
    k = 0
    for li, ln in enumerate(lines):
        y = 640 + li * 140
        size = 110 if any(w.strip("“”.") in QGOLD for w in ln) else 84
        widths = [d.textlength(w + " ", font=F(size)) for w in ln]
        x = 540 - sum(widths) / 2
        for w, wd in zip(ln, widths):
            a = e((t - 0.25 - k * 0.32) / 0.2)
            if a > 0:
                s = size * (1.25 - 0.25 * a)
                col = GOLD if w.strip("“”.") in QGOLD else WHITE
                text(d, (x + wd / 2, y), w, int(s), col, alpha=255 * a, stroke=4)
            x += wd
            k += 1
    a = e((t - 4.0) / 0.4)
    text(d, (540, 1390), "Bassirou Diomaye Faye, President of Senegal", 32, WHITE, alpha=255 * a)
    text(d, (540, 1440), "UN General Assembly · Sept 2026", 28, GOLD, alpha=255 * a)
    return img, None


# ---------------------------------------------------------------- 10. whiteboard / doodle

def wobble(pts, amt, seed):
    r = np.random.default_rng(seed)
    return [(x + r.uniform(-amt, amt), y + r.uniform(-amt, amt)) for x, y in pts]


def f_whiteboard(t):
    img = Image.new("RGBA", (W, H), (244, 240, 230, 255))
    d = ImageDraw.Draw(img, "RGBA")
    ink = (30, 34, 44, 255)
    red = (200, 50, 40, 255)
    # draw a parliament half-circle as the "pen" moves along it
    k = e(t / 2.2)
    n = int(60 * k)
    arc = [(540 + 380 * math.cos(math.pi + math.pi * i / 60), 1150 + 380 * math.sin(math.pi + math.pi * i / 60)) for i in range(n + 1)]
    if len(arc) > 1:
        d.line(wobble(arc, 1.5, 3), fill=ink, width=7, joint="curve")
        pen = arc[-1]
    else:
        pen = (160, 1150)
    # seat dots appear, then the majority line
    dots = int(40 * e((t - 1.6) / 1.4))
    for i in range(dots):
        a = math.pi + math.pi * (i + 0.5) / 40
        for rr in (250, 310):
            x, y = 540 + rr * math.cos(a), 1150 + rr * math.sin(a)
            d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=ink, width=3)
    if t > 3.2:
        m = e((t - 3.2) / 0.6)
        d.line([(540, 1150), (540, 1150 - 420 * m)], fill=red, width=6)
        pen = (540, 1150 - 420 * m)
    word = "198 = MAJORITY"
    shown = word[:int(len(word) * e((t - 3.9) / 1.2))]
    if shown:
        d.text((540, 640), shown, font=F(64), fill=red, anchor="mm")
        pen = (540 + d.textlength(shown, font=F(64)) / 2, 660)
    shown2 = "395 SEATS"[:int(9 * e((t - 1.0) / 1.0))]
    if shown2:
        d.text((540, 1230), shown2, font=F(56), fill=ink, anchor="mm")
    # marker pen
    px, py = pen
    d.polygon([(px, py), (px + 30, py - 70), (px + 60, py - 55), (px + 18, py + 8)], fill=(40, 90, 200, 255))
    d.polygon([(px + 30, py - 70), (px + 60, py - 55), (px + 110, py - 190), (px + 80, py - 205)], fill=(30, 30, 36, 255))
    hl = R.headline_layer(["HOW A COALITION", "WORKS"], 1, cy=420)
    img.alpha_composite(hl)
    return img, None


# ---------------------------------------------------------------- 11. animated carousel

SLIDES = [("7,773", "confirmed Ebola cases in DR Congo (as of 22 Sept)"),
          ("2ND", "largest Ebola outbreak on record"),
          ("NO", "approved vaccine yet for this strain (Bundibugyo)")]


def f_carousel(t):
    img = dark_bg((20, 20, 30))
    d = ImageDraw.Draw(img, "RGBA")
    img.alpha_composite(R.headline_layer(["SWIPE", "CAROUSEL"], 1, cy=420))
    pos = 0.0
    for k in range(1, 3):
        pos += e((t - k * 2.0) / 0.45)
    cw = 820
    for i, (big, small) in enumerate(SLIDES):
        x0 = 130 + (i - pos) * (cw + 40)
        if x0 > W or x0 + cw < 0:
            continue
        d.rounded_rectangle((x0, 600, x0 + cw, 1440), radius=30, fill=(18, 16, 12, 255), outline=(*GOLD, 255), width=4)
        text(d, (x0 + cw / 2, 680), f"{i + 1}/3 · EBOLA IN DR CONGO", 30, GOLD)
        text(d, (x0 + cw / 2, 930), big, 170, GOLD, stroke=5)
        for k, ln in enumerate(wrap(d, small, 44, cw - 100)):
            text(d, (x0 + cw / 2, 1120 + k * 60), ln, 44, WHITE)
        text(d, (x0 + cw / 2, 1380), "Sources: WHO · CDC · UN", 24, (180, 176, 168), stroke=0)
    active = int(round(pos))
    for k in range(3):
        c = GOLD if k == active else (110, 106, 100)
        d.ellipse((490 + k * 40 - 10, 1480 - 10, 490 + k * 40 + 10, 1480 + 10), fill=c)
    return img, None


# ---------------------------------------------------------------- 12. audiogram

AUDIO = os.path.join(HERE, "uganda-southsudan-power-60s", "vo", "01.mp3")
_env = {}


def audio_env():
    if "lv" not in _env:
        raw = subprocess.run([R.FFMPEG, "-v", "error", "-i", AUDIO, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        a = np.frombuffer(raw, np.float32)
        hop = 16000 // FPS
        rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)])
        _env["lv"] = rms / (rms.max() + 1e-6)
        _env["dur"] = len(a) / 16000
    return _env["lv"], _env["dur"]


def f_audiogram(t):
    lv, dur = audio_env()
    spec = {"view": "region", "highlight": ["Uganda", "S. Sudan"], "dim": 0.35, "labels": False}
    img = mapviz.render(spec, 0.5, t).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    img.alpha_composite(R.headline_layer(["AUDIOGRAM", "LISTEN IN"], 1, cy=420))
    d.ellipse((440, 600, 640, 800), fill=(18, 16, 12, 255), outline=GOLD, width=5)
    text(d, (540, 680), "ABS", 60, GOLD)
    text(d, (540, 740), "PODCAST", 22, WHITE, stroke=0)
    i = int((t - 0.3) * FPS)
    for b in range(36):  # waveform bars from the real audio
        j = i - (18 - b) * 2
        v = lv[j] if 0 <= j < len(lv) else 0.02
        h = 20 + 360 * v
        x = 540 - 36 * 14 + b * 28
        d.rounded_rectangle((x, 1030 - h / 2, x + 16, 1030 + h / 2), radius=8, fill=(*GOLD, 230))
    return img, "In South Sudan, only about 1 in 20 people has electricity. That could be about to change."


FORMATS = [("ANIMATED EXPLAINER", f_explainer), ("MAP STORY", f_map), ("DATA RACE", f_race),
           ("WEEKLY ROUNDUP", f_roundup), ("QUIZ", f_quiz), ("MYTH VS REALITY", f_myth),
           ("TIMELINE", f_timeline), ("THEN VS NOW", f_thenvsnow), ("KINETIC QUOTE", f_kinetic),
           ("WHITEBOARD", f_whiteboard), ("CAROUSEL", f_carousel), ("AUDIOGRAM", f_audiogram)]


def label_chip(i, name):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    s = f"FORMAT {i + 1} OF {len(FORMATS)} · {name}"
    tw = d.textlength(s, font=F(30))
    d.rounded_rectangle((540 - tw / 2 - 24, 238, 540 + tw / 2 + 24, 294), radius=28, fill=(0, 0, 0, 170), outline=(*GOLD, 255), width=3)
    d.text((540, 266), s, font=F(30), fill=GOLD, anchor="mm")
    return lay


def main():
    out_dir = sys.argv[1]
    endcard = sys.argv[sys.argv.index("--endcard") + 1] if "--endcard" in sys.argv else None
    os.makedirs(os.path.join(out_dir, "build"), exist_ok=True)
    R.CAP_Y, R.CAP_W = 1380, 780
    header = R.header_layer()
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    cap_font = F(44)
    total = SEG * len(FORMATS)
    audiogram_start = SEG * 11 + 0.3
    # audio: music bed + whooshes + the audiogram's voice clip
    music = os.path.join(out_dir, "build", "music.wav")
    subprocess.run([sys.executable, os.path.join(HERE, "music_bed.py"), music, str(total + 1), "2"], check=True,
                   capture_output=True)
    whoosh = os.path.join(HERE, "uganda-southsudan-power-60s", "audio", "whoosh.mp3")
    ins = ["-i", music, "-i", AUDIO]
    fc = [f"[0:a]volume=0.5,atrim=0:{total:.2f}[m]",
          f"[1:a]loudnorm=I=-16:TP=-1.5,adelay={int(audiogram_start * 1000)}|{int(audiogram_start * 1000)}[v]"]
    labels = ["[m]", "[v]"]
    for k in range(1, len(FORMATS)):
        ins += ["-i", whoosh]
        ms = int((k * SEG - 0.25) * 1000)
        fc.append(f"[{k + 1}:a]volume=0.35,adelay={ms}|{ms}[w{k}]")
        labels.append(f"[w{k}]")
    fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,alimiter=limit=0.95[a]")
    mix = os.path.join(out_dir, "build", "mix.wav")
    subprocess.run([R.FFMPEG, "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[a]",
                    "-ac", "2", "-t", f"{total:.2f}", mix], check=True)
    body = os.path.join(out_dir, "build", "body.mp4")
    enc = subprocess.Popen([R.FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", mix, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", body], stdin=subprocess.PIPE)
    n = int(total * FPS)
    prev = None
    for i, (name, fn) in enumerate(FORMATS):
        chip = label_chip(i, name)
        if hasattr(f_race, "pos"):
            del f_race.pos
        for fr in range(int(SEG * FPS)):
            t = fr / FPS
            frame, cap = fn(t)
            frame = frame.convert("RGBA")
            frame.alpha_composite(header)
            frame.alpha_composite(chip)
            if cap:  # word-by-word caption, timed evenly across the segment
                words = cap.split()
                pages = R.caption_pages(words, probe, cap_font)
                active = int(len(words) * min(1, t / (SEG * 0.85)))
                pi = 0
                for k, pg in enumerate(pages):
                    if active >= pg[0][0]:
                        pi = k
                frame.alpha_composite(R.caption_layer(words, pages[pi], active, cap_font))
            g = i * SEG * FPS + fr
            dd = ImageDraw.Draw(frame, "RGBA")
            dd.rectangle((0, H - 9, W, H - 3), fill=(255, 255, 255, 40))
            dd.rectangle((0, H - 9, int(W * g / n), H - 3), fill=(*GOLD, 230))
            if prev is not None and fr < 5:
                frame = Image.blend(prev, frame, (fr + 1) / 6)
            if fr == int(SEG * FPS) - 1:
                prev = frame.copy()
            enc.stdin.write(frame.convert("RGB").tobytes())
        print(f"{i + 1}/{len(FORMATS)} {name}", file=sys.stderr)
    enc.stdin.close()
    enc.wait()
    out = os.path.join(out_dir, "format-samples.mp4")
    if endcard:
        tail = os.path.join(out_dir, "build", "endcard.mp4")
        start = R.audio_duration(endcard) - 1.6
        subprocess.run([R.FFMPEG, "-v", "error", "-y", "-ss", f"{start:.2f}", "-i", endcard, "-vf",
                        f"scale={W}:{H},fps={FPS},setsar=1", "-af", "aresample=48000", "-ac", "2", "-c:v", "libx264",
                        "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", tail], check=True)
        subprocess.run([R.FFMPEG, "-v", "error", "-y", "-i", body, "-i", tail, "-filter_complex",
                        "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
                        "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-movflags", "+faststart", out], check=True)
    else:
        os.replace(body, out)
    print(out)


if __name__ == "__main__":
    main()
