#!/usr/bin/env python3
"""Render an Africa Blind Spot reel (1080x1920, 30fps) in the house style.

House style (matched from the Tigray reference reels):
  * small gold "AFRICA BLIND SPOT" header with a short underline
  * big two-line uppercase headline, one line white and one gold
  * word-by-word captions near the bottom: spoken words turn gold
  * dark, slowly zooming cinematic backgrounds
  * "send this to someone who hasn't heard" CTA, then the brand end card

Usage:
  python3 render_reel.py <reel_dir> [--endcard path.mp4 --endcard-start SECONDS]

<reel_dir> must contain script.json, bg/<name>.png for image scenes and
vo/NN.mp3 (one voice clip per scene, 01-based).
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W, H, FPS = 1080, 1920, 30
GOLD = (212, 170, 52)
WHITE = (246, 244, 238)
GREY = (120, 116, 108)
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SCENE_GAP = 0.30  # silence after each voice clip, seconds (script.json "gap" overrides)
XFADE = 6  # frames of crossfade between scenes
# caption placement; --ig-safe moves them clear of Instagram's bottom overlay and side buttons
CAP_Y, CAP_W, GRID_Y = 1545, 860, 990
CRF, PRESET = "19", "medium"

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = "ffmpeg"


def font(size):
    return ImageFont.truetype(BOLD, size)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def audio_duration(path):
    out = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"no duration for {path}")


def speech_bounds(path, total):
    """Return (start, end) of speech inside a clip using ffmpeg silencedetect."""
    out = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", path, "-af", "silencedetect=n=-40dB:d=0.15", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts, ends = [], []
    for line in out.splitlines():
        if "silence_start:" in line:
            starts.append(float(line.split("silence_start:")[1].split()[0]))
        if "silence_end:" in line:
            ends.append(float(line.split("silence_end:")[1].split()[0]))
    begin = ends[0] if starts and starts[0] <= 0.02 and ends else 0.0
    finish = starts[-1] if starts and starts[-1] > total - 1.0 and starts[-1] > begin else total
    return begin, finish


def pauses(path, s0, s1):
    """Silences inside the speech window: list of (start, end)."""
    out = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", path, "-af", "silencedetect=n=-36dB:d=0.11", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    st, res = None, []
    for line in out.splitlines():
        if "silence_start:" in line:
            st = float(line.split("silence_start:")[1].split()[0])
        if "silence_end:" in line and st is not None:
            en = float(line.split("silence_end:")[1].split()[0])
            if st > s0 + 0.05 and en < s1 - 0.05:
                res.append((st, en))
            st = None
    return res


LINE_GAP = 0.12  # pause between dialogue lines inside a scene


def build_lines(rd, work, idx, sc, default_tempo=1.0, read_wps=2.7):
    """Concatenate a scene's dialogue lines (one clip per line) into one clip.

    Missing clips become silent placeholders timed from the word count, so the
    film can be previewed before every voice is recorded, or posted as a text-led
    reel (script "read_wps" sets the reading pace). Returns (path, spans).
    """
    parts, spans, t = [], [], 0.0
    for k, ln in enumerate(sc["lines"]):
        src = os.path.join(rd, "vo", ln["file"])
        synthetic = not os.path.exists(src)
        out = os.path.join(work, f"line_{idx:02d}_{k}.wav")
        if synthetic:
            est = (len(ln["say"].split()) / read_wps + 0.3) / ln.get("tempo", default_tempo)
            subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                            "-t", f"{est:.2f}", out], check=True)
        else:
            tempo = ln.get("tempo", default_tempo)
            subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-af",
                            f"atempo={tempo},loudnorm=I=-18:TP=-2:LRA=11,aresample=44100", "-ac", "1", out], check=True)
        dur = audio_duration(out)
        if synthetic:
            a, b, g = 0.15, dur - 0.15, []
        else:
            a, b = speech_bounds(out, dur)
            g = pauses(out, a, b)
        spans.append(dict(start=t, end=t + dur, who=ln["who"], synthetic=synthetic, s0=t + a, s1=t + b,
                          gaps=[(x + t, y + t) for x, y in g], show=ln["show"]))
        parts.append(out)
        t += dur + (LINE_GAP if k < len(sc["lines"]) - 1 else 0)
    path = os.path.join(work, f"scene_{idx:02d}.wav")
    ins, fc = [], []
    for k, pth in enumerate(parts):
        ins += ["-i", pth]
        pad = LINE_GAP if k < len(parts) - 1 else 0
        fc.append(f"[{k}:a]apad=pad_dur={pad}[p{k}]")
    fc.append("".join(f"[p{k}]" for k in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[o]")
    subprocess.run([FFMPEG, "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[o]", path], check=True)
    return path, spans


def envelope(path, spans, fps):
    """Mouth-open level per video frame from the clip's loudness (synthetic lines flap)."""
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32)
    hop = int(16000 / fps)
    n = len(a) // hop + 1
    rms = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2)) if a[i * hop:(i + 1) * hop].size else 0
                    for i in range(n)])
    lvl = np.zeros(n)
    for sp in spans:
        i0, i1 = int(sp["s0"] * fps), int(sp["s1"] * fps) + 1
        if sp["synthetic"]:
            for i in range(i0, min(i1, n)):
                lvl[i] = 0.35 + 0.35 * math.sin(i / fps * 2 * math.pi * 4.5)
        else:
            seg = rms[i0:i1]
            ref = np.percentile(seg, 90) if seg.size else 1
            lvl[i0:i1] = np.clip(seg / (ref * 0.8 + 1e-6), 0, 1)
    return lvl


def word_times(words, s0, s1, gaps):
    """Start time of each word. Phrase breaks (after , . ? ! :) snap to real pauses."""
    weights = [len(w) + 2 for w in words]
    total = sum(weights)
    est, acc = [], 0
    for w_ in weights:
        est.append(s0 + (s1 - s0) * acc / total)
        acc += w_
    breaks = [i + 1 for i, w in enumerate(words[:-1]) if w[-1] in ",.?!:;"]
    anchors = {0: s0}
    used = set()
    for b in breaks:
        guess = est[b]
        cand = [(abs(g[1] - guess), k) for k, g in enumerate(gaps) if k not in used]
        if cand:
            dist, k = min(cand)
            if dist < 0.9:
                used.add(k)
                anchors[b] = gaps[k][1]
    keys = sorted(anchors) + [len(words)]
    times = [0.0] * len(words)
    for a, b in zip(keys, keys[1:]):
        t0 = anchors[a]
        t1 = anchors.get(b, s1) if b < len(words) else s1
        if b < len(words):
            # speech of this phrase ends where its pause began
            t1 = min([g[0] for g in gaps if abs(g[1] - anchors[b]) < 1e-6] or [t1])
        seg_w = sum(weights[a:b])
        acc = 0
        for i in range(a, b):
            times[i] = t0 + (t1 - t0) * acc / seg_w
            acc += weights[i]
    return times


# ---------------------------------------------------------------- backgrounds

def cover(img, w, h):
    s = max(w / img.width, h / img.height)
    img = img.resize((math.ceil(img.width * s), math.ceil(img.height * s)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def vignette(w, h, strength=0.55):
    y, x = np.ogrid[0:h, 0:w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
    return (1 - strength * np.clip(d, 0, 1) ** 1.6)[..., None]


VIG = None


def grade(img, bright=0.58, tint=None, sat=1.0, blur=0):
    """Darken and colour-grade a background so white/gold text reads clearly."""
    global VIG
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    if sat != 1.0:
        g = a.mean(axis=2, keepdims=True)
        a = g + (a - g) * sat
    if tint is not None:
        a = a * 0.6 + np.array(tint, np.float32) * (a.mean(axis=2, keepdims=True) / 255.0) * 0.4 * 2.2
    if VIG is None or VIG.shape[:2] != a.shape[:2]:
        VIG = vignette(a.shape[1], a.shape[0])
    a = a * bright * VIG
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


class VideoBG:
    """Stock/own footage as a scene background: cover-cropped to 9:16, graded dark, looped if short.
    spec: {"video": "file.mov" (in bg/), "start": s, "speed": 1.0, "bright": 0.55, "sat": 0.9}"""

    def __init__(self, reel_dir, spec):
        self.path = os.path.join(reel_dir, "bg", spec["video"])
        self.spec = spec
        self.proc = None

    def _open(self):
        sp = self.spec
        vf = (f"setpts=PTS/{sp.get('speed', 1.0)},scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H},fps={FPS}")
        self.proc = subprocess.Popen([FFMPEG, "-v", "error", "-ss", str(sp.get("start", 0)), "-i", self.path,
                                      "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)

    def next(self):
        for _ in range(2):
            if self.proc is None:
                self._open()
            buf = self.proc.stdout.read(W * H * 3)
            if len(buf) == W * H * 3:
                img = Image.fromarray(np.frombuffer(buf, np.uint8).reshape(H, W, 3))
                return grade(img, self.spec.get("bright", 0.55), self.spec.get("tint"), self.spec.get("sat", 0.9))
            self.proc.kill()
            self.proc = None  # clip ended: loop it
        raise RuntimeError(f"cannot read video {self.path}")

    def close(self):
        if self.proc:
            self.proc.kill()


def load_bg(reel_dir, spec):
    if "video" in spec:
        return VideoBG(reel_dir, spec)
    if "map" in spec or "anim" in spec or "format" in spec:
        return spec  # drawn per frame by mapviz / anim / formats
    return _load_image_bg(reel_dir, spec)


def _load_image_bg(reel_dir, spec):
    """spec: {"src": file, "crop": [x0,y0,x1,y1] fractions, "bright", "tint", "sat", "blur"}"""
    if spec.get("src") is None:
        base = Image.new("RGB", (W, H), tuple(spec.get("color", (10, 10, 14))))
        glow = Image.new("RGB", (W, H), (0, 0, 0))
        d = ImageDraw.Draw(glow)
        c = tuple(spec.get("glow", (120, 60, 10)))
        d.ellipse((W * 0.05, H * 0.30, W * 0.95, H * 0.75), fill=c)
        base = Image.blend(base, glow.filter(ImageFilter.GaussianBlur(260)), 0.55)
        return grade(base, bright=1.0)
    img = Image.open(os.path.join(reel_dir, "bg", spec["src"])).convert("RGB")
    if "crop" in spec:
        x0, y0, x1, y1 = spec["crop"]
        img = img.crop((int(x0 * img.width), int(y0 * img.height), int(x1 * img.width), int(y1 * img.height)))
    # render ~12% oversize so we can slow-zoom without upscaling artefacts
    big = cover(img, int(W * 1.12), int(H * 1.12))
    return grade(big, spec.get("bright", 0.58), spec.get("tint"), spec.get("sat", 1.0), spec.get("blur", 0))


def bg_frame(big, t, dur, zoom_in=True):
    p = t / max(dur, 0.01)
    z = 1.0 + 0.10 * (p if zoom_in else 1 - p)  # slow push-in (or pull-out)
    # visible window shrinks as zoom increases and stays centred
    ch = min(big.height, int(big.height / z))
    cw = int(ch * W / H)
    x, y = (big.width - cw) // 2, (big.height - ch) // 2
    return big.crop((x, y, x + cw, y + ch)).resize((W, H), Image.BILINEAR)


# ---------------------------------------------------------------- text layers

def draw_text(d, xy, text, f, fill, stroke=4, anchor="mm", spacing=0):
    x, y = xy
    if spacing:
        widths = [d.textlength(ch, font=f) + spacing for ch in text]
        total = sum(widths) - spacing
        cx = x - total / 2
        for ch, w_ in zip(text, widths):
            d.text((cx + 3, y + 4), ch, font=f, fill=(0, 0, 0, 150), anchor="lm")
            d.text((cx, y), ch, font=f, fill=fill, anchor="lm", stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
            cx += w_
        return
    d.text((x + 3, y + 5), text, font=f, fill=(0, 0, 0, 160), anchor=anchor)
    d.text((x, y), text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 210))


def header_layer():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_text(d, (W / 2, 172), "AFRICA BLIND SPOT", font(40), GOLD, stroke=2, spacing=2)
    d.rectangle((W / 2 - 55, 206, W / 2 + 55, 210), fill=GOLD)
    return layer


def fit_font(d, lines, max_w, start=100, floor=58):
    size = start
    while size > floor:
        f = font(size)
        if all(d.textlength(l, font=f) <= max_w for l in lines):
            return f
        size -= 4
    return font(floor)


def headline_layer(lines, gold_idx, cta=False, cy=960):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if cta:
        f1 = fit_font(d, [lines[0]], W - 120, start=50, floor=34)  # shrink long CTA lines to fit
        f2 = fit_font(d, [lines[1]], W - 120, start=46, floor=30)
        draw_text(d, (W / 2, 900), lines[0], f1, WHITE, stroke=3)
        draw_text(d, (W / 2, 962), lines[1], f2, GOLD, stroke=3)
        return layer
    f = fit_font(d, lines, W - 120)
    lh = f.size * 1.12
    y0 = cy - lh * (len(lines) - 1) / 2
    for i, l in enumerate(lines):
        draw_text(d, (W / 2, y0 + i * lh), l, f, GOLD if i == gold_idx else WHITE, stroke=5)
    return layer


def wrap_words(words, f, d, max_w):
    lines, cur = [], []
    for i, w in enumerate(words):
        trial = " ".join(words[j] for j in cur + [i])
        if cur and d.textlength(trial, font=f) > max_w:
            lines.append(cur)
            cur = [i]
        else:
            cur.append(i)
    if cur:
        lines.append(cur)
    return lines


def caption_pages(words, d, f, max_w=None):
    max_w = max_w or CAP_W
    """Split words into 2-line pages, like the reference reels."""
    lines = wrap_words(words, f, d, max_w)
    return [lines[i:i + 2] for i in range(0, len(lines), 2)]


SPEAKER_LABELS = {"yasmine": "YASMINE", "haj": "HAJ AHMED"}


def caption_layer(words, page, active, f, label=None):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lh = f.size * 1.18
    y0 = CAP_Y - lh * (len(page) - 1) / 2
    if label:  # who is speaking, for dialogue scenes
        lf = font(28)
        tw = d.textlength(label, font=lf)
        ly = y0 - lh * 0.5 - 34
        d.rounded_rectangle((W / 2 - tw / 2 - 16, ly - 20, W / 2 + tw / 2 + 16, ly + 20), radius=10, fill=(0, 0, 0, 150))
        d.text((W / 2, ly), label, font=lf, fill=GOLD, anchor="mm")
    for li, idxs in enumerate(page):
        text_w = d.textlength(" ".join(words[i] for i in idxs), font=f)
        x = W / 2 - text_w / 2
        y = y0 + li * lh
        for i in idxs:
            w = words[i]
            col = GOLD if i <= active else WHITE
            d.text((x + 2, y + 3), w, font=f, fill=(0, 0, 0, 170), anchor="lm")
            d.text((x, y), w, font=f, fill=col, anchor="lm", stroke_width=3, stroke_fill=(0, 0, 0, 220))
            x += d.textlength(w + " ", font=f)
    return layer


# ---------------------------------------------------------------- special scenes

def bars_layer(p, spec):
    """Animated comparison bars (e.g. days to reach 1,000 cases)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    items = spec["bars"]
    vmax = max(b["value"] for b in items)
    if spec.get("bars_title"):
        a = int(255 * ease_out(p / 0.1))
        d.text((130, 945), spec["bars_title"], font=font(30), fill=(*GOLD, a), anchor="ls")
    y = 1010
    for k, b in enumerate(items):
        grow = ease_out((p - 0.12 - 0.18 * k) / 0.45)
        full = 820 * b["value"] / vmax
        col = GOLD if b.get("hi") else GREY
        d.text((130, y), b["label"], font=font(34), fill=WHITE, anchor="ls", stroke_width=2, stroke_fill=(0, 0, 0))
        d.rounded_rectangle((130, y + 14, 130 + max(8, full * grow), y + 64), radius=8, fill=col)
        if grow > 0.95:
            d.text((140 + full * grow, y + 40), b["value_label"], font=font(34), fill=WHITE, anchor="lm",
                   stroke_width=2, stroke_fill=(0, 0, 0)) if full < 640 else \
                d.text((120 + full * grow, y + 40), b["value_label"], font=font(34), fill=(20, 16, 8), anchor="rm")
        y += 130
    return layer


def chips_layer(p, spec):
    """Two stat chips, e.g. ITURI -26% / NORTH KIVU +73%."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k, c in enumerate(spec["chips"]):
        a = ease_out((p - 0.2 - 0.25 * k) / 0.2)
        if a <= 0:
            continue
        cx = W / 2 + (k - 0.5) * 440
        box = (cx - 195, 980, cx + 195, 1150)
        d.rounded_rectangle(box, radius=18, fill=(10, 10, 10, int(190 * a)),
                            outline=(*(GOLD if c.get("hi") else GREY), int(255 * a)), width=4)
        d.text((cx, 1030), c["label"], font=font(32), fill=(*WHITE, int(255 * a)), anchor="mm")
        d.text((cx, 1100), c["value"], font=font(64), fill=(*(GOLD if c.get("hi") else WHITE), int(255 * a)),
               anchor="mm")
    return layer


def ranks_layer(p, spec):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = spec.get("ranks_y", 1000)
    for k, r in enumerate(spec["ranks"]):
        a = ease_out((p - 0.15 - 0.2 * k) / 0.2)
        if a <= 0:
            continue
        col = GOLD if r.get("hi") else WHITE
        d.text((W / 2, y), r["text"], font=font(40), fill=(*col, int(255 * a)), anchor="mm",
               stroke_width=3, stroke_fill=(0, 0, 0, int(220 * a)))
        y += 72
    return layer


def grid_layer(p, t, spec):
    """N light bulbs, `lit` of them glowing: e.g. 1 in 20 people with power."""
    n, lit, cols = spec.get("grid_n", 20), spec.get("grid_lit", 1), 5
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rows = math.ceil(n / cols)
    gap = 150
    x0 = W / 2 - gap * (cols - 1) / 2
    y0 = GRID_Y
    for k in range(n):
        a = ease_out((p - 0.05 - k * 0.012) / 0.12)
        if a <= 0:
            continue
        cx, cy = x0 + (k % cols) * gap, y0 + (k // cols) * 118
        on = k < lit and p > 0.35
        if on:
            glow = 0.75 + 0.25 * math.sin(t * 4)
            d.ellipse((cx - 52, cy - 58, cx + 52, cy + 46), fill=(*GOLD, int(60 * glow)))
        col = (255, 226, 130) if on else (70, 66, 60)
        d.ellipse((cx - 30, cy - 38, cx + 30, cy + 22), fill=(*col, int(255 * a)))
        d.rectangle((cx - 15, cy + 18, cx + 15, cy + 38), fill=(*((150, 130, 80) if on else (55, 52, 48)), int(255 * a)))
    return layer


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir")
    ap.add_argument("--endcard", help="video to take the brand end card from")
    ap.add_argument("--endcard-start", type=float, default=None, help="seconds into --endcard")
    ap.add_argument("--out", default=None)
    ap.add_argument("--music", help="music bed, looped and ducked under the voice")
    ap.add_argument("--music-vol", type=float, default=0.22)
    ap.add_argument("--sfx", help="transition sound played at each scene change")
    ap.add_argument("--sfx-vol", type=float, default=0.35)
    ap.add_argument("--endcard-len", type=float, default=2.2)
    ap.add_argument("--ig-safe", action="store_true",
                    help="Instagram Reels export: captions inside the safe zone, higher-quality encode")
    args = ap.parse_args()
    if args.ig_safe:
        global CAP_Y, CAP_W, GRID_Y, CRF, PRESET
        CAP_Y, CAP_W, GRID_Y, CRF, PRESET = 1380, 780, 920, "16", "slow"

    rd = args.reel_dir
    script = json.load(open(os.path.join(rd, "script.json")))
    scenes = script["scenes"]
    work = os.path.join(rd, "build")
    os.makedirs(work, exist_ok=True)

    # --- audio timeline
    gap_s = script.get("gap", SCENE_GAP)
    timeline, t = [], 0.0
    for i, sc in enumerate(scenes, 1):
        spans = None
        if "lines" in sc:
            vo, spans = build_lines(rd, work, i, sc, script.get("tempo", 1.0), script.get("read_wps", 2.7))
        else:
            vo = os.path.join(rd, "vo", f"{i:02d}.mp3")
        dur = audio_duration(vo)
        s0, s1 = (spans[0]["s0"], spans[-1]["s1"]) if spans else speech_bounds(vo, dur)
        hold = sc.get("hold", 0.0)  # extra seconds on screen after the voice
        timeline.append(dict(start=t, dur=dur + gap_s + hold, vo=vo, speech=(s0, s1), pad=gap_s + hold,
                             gaps=[] if spans else pauses(vo, s0, s1), spans=spans,
                             env=envelope(vo, spans, FPS) if spans else None))
        t += dur + gap_s + hold
    total = t

    # voice track: clips placed back to back with gaps
    inputs, filt = [], []
    for k, seg in enumerate(timeline):
        inputs += ["-i", seg["vo"]]
        filt.append(f"[{k}:a]aresample=44100,apad=pad_dur={seg['pad']:.3f}[a{k}]")
    filt.append("".join(f"[a{k}]" for k in range(len(timeline))) + f"concat=n={len(timeline)}:v=0:a=1,"
                "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100[vo]")
    voice = os.path.join(work, "voice.wav")
    subprocess.run([FFMPEG, "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt),
                    "-map", "[vo]", "-ac", "2", voice], check=True)
    if args.music or args.sfx:
        mixed = os.path.join(work, "mix.wav")
        ins, fc, labels = ["-i", voice], ["[0:a]asplit=2[vox][key]"], ["[vox]"]
        n = 1
        if args.music:
            ins += ["-stream_loop", "-1", "-i", args.music]
            fc.append(f"[{n}:a]aresample=44100,atrim=0:{total:.2f},volume={args.music_vol},"
                      f"afade=t=in:d=0.6,afade=t=out:st={max(0, total - 1.8):.2f}:d=1.8[mus]")
            fc.append("[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[duck]")
            labels.append("[duck]")
            n += 1
        else:
            fc[0] = "[0:a]anull[vox]"
        if args.sfx:
            for k, seg in enumerate(timeline[1:], 1):
                ins += ["-i", args.sfx]
                ms = int(max(0, seg["start"] - 0.25) * 1000)
                fc.append(f"[{n}:a]aresample=44100,volume={args.sfx_vol},adelay={ms}|{ms}[s{k}]")
                labels.append(f"[s{k}]")
                n += 1
        fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,"
                  "alimiter=limit=0.95[out]")
        subprocess.run([FFMPEG, "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc),
                        "-map", "[out]", "-ac", "2", "-t", f"{total:.2f}", mixed], check=True)
        voice = mixed

    # --- frames
    header = header_layer()
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    cap_font = font(44)
    silent = os.path.join(work, "body.mp4")
    enc = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", voice,
                            "-c:v", "libx264", "-preset", PRESET, "-crf", CRF, "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "160k", "-shortest", silent], stdin=subprocess.PIPE)

    nframes = int(round(total * FPS))
    cache = {}
    prev_last = None
    for sc_i, (sc, seg) in enumerate(zip(scenes, timeline)):
        big = load_bg(rd, sc["bg_spec"])
        head_y = sc.get("head_y", 420 if "format" in sc["bg_spec"] else 760 if sc.get("special") else 960)
        head = headline_layer(sc["head"], sc.get("gold", 1), sc.get("cta", False), head_y)
        spans = seg["spans"]
        if spans:
            words, pages, times, who_of_word = [], [], [], []
            for sp in spans:
                ws = sp["show"].split()
                base_i = len(words)
                for pg in caption_pages(ws, probe, cap_font):
                    pages.append([[base_i + i for i in ln] for ln in pg])
                times += word_times(ws, sp["s0"], sp["s1"], sp["gaps"])
                who_of_word += [sp["who"]] * len(ws)
                words += ws
        else:
            words = sc["show"].split()
            pages = caption_pages(words, probe, cap_font)
            # word timings, proportional to word length inside the speech window
            s0, s1 = seg["speech"]
            times = word_times(words, s0, s1, seg["gaps"])
            who_of_word = None
        count = sc.get("count")
        count_cache = {}
        cache.pop("sub_layer", None)
        f0 = int(round(seg["start"] * FPS))
        f1 = min(nframes, int(round((seg["start"] + seg["dur"]) * FPS)))
        for fr in range(f0, f1):
            lt = fr / FPS - seg["start"]
            p = lt / seg["dur"]
            if isinstance(big, VideoBG):
                frame = big.next().convert("RGBA")
            elif isinstance(big, dict):
                import anim
                import mapviz
                ctx = None
                if spans:
                    cur = 0
                    for k, sp in enumerate(spans):
                        if lt >= sp["start"]:
                            cur = k
                    sp = spans[cur]
                    talking = sp["s0"] - 0.05 <= lt <= sp["s1"] + 0.05
                    env = seg["env"]
                    ctx = {"speaker": sp["who"] if talking else None,
                           "level": float(env[min(len(env) - 1, int(lt * FPS))]) if talking else 0.0,
                           "line": cur, "line_p": max(0.0, min(1.0, (lt - sp["start"]) / max(0.01, sp["end"] - sp["start"])))}
                if "format" in big:  # reusable video formats (race, quiz, timeline, ...)
                    import formats
                    fctx = dict(ctx or {}, vo=seg["vo"], reel_dir=rd)
                    frame = formats.render(big, p, lt, seg["dur"], fctx)
                else:
                    base = mapviz.render(big["map"], p, lt) if "map" in big else None
                    frame = (anim.render(big, p, lt, base, ctx) if "anim" in big else base).convert("RGBA")
            else:
                frame = bg_frame(big, lt, seg["dur"], zoom_in=sc_i % 2 == 0).convert("RGBA")
            frame.alpha_composite(header)
            if count and lt < count.get("dur", 1.0) + 0.1:
                val = int(round(count["to"] * ease_out(lt / count.get("dur", 1.0))))
                if val not in count_cache:
                    lines = list(sc["head"])
                    lines[count.get("line", 0)] = f'{count.get("prefix", "")}{val:,}{count.get("suffix", "")}'
                    count_cache[val] = headline_layer(lines, sc.get("gold", 1), False, head_y)
                head_now = count_cache[val]
            else:
                head_now = head
            # headline pops in over 0.3s
            pop = ease_out(lt / 0.3)
            if pop < 1:
                s = 0.86 + 0.14 * pop
                hl = head_now.resize((int(W * s), int(H * s)), Image.BILINEAR)
                a = np.asarray(hl).copy()
                a[..., 3] = (a[..., 3] * pop).astype(np.uint8)
                hl = Image.fromarray(a)
                frame.alpha_composite(hl, ((W - hl.width) // 2, int(head_y - head_y * s)))
            else:
                frame.alpha_composite(head_now)
            if sc.get("sub"):  # small persistent line under the headline (e.g. a caveat)
                if "sub_layer" not in cache:
                    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    ImageDraw.Draw(lay).text((W / 2, head_y + 118), sc["sub"], font=font(30), fill=WHITE, anchor="mm",
                                             stroke_width=3, stroke_fill=(0, 0, 0))
                    cache["sub_layer"] = lay
                frame.alpha_composite(cache["sub_layer"])
            if sc.get("note") and lt < sc.get("note_secs", 3.5):  # e.g. "Dramatization..." disclaimer
                ImageDraw.Draw(frame).text((W / 2, 250), sc["note"], font=font(26), fill=(235, 230, 215), anchor="mm",
                                           stroke_width=3, stroke_fill=(0, 0, 0))
            special = sc.get("special")
            if special == "bars":
                frame.alpha_composite(bars_layer(p, sc))
            elif special == "chips":
                frame.alpha_composite(chips_layer(p, sc))
            elif special == "ranks":
                frame.alpha_composite(ranks_layer(p, sc))
            elif special == "grid":
                frame.alpha_composite(grid_layer(p, lt, sc))
            # captions
            active = max([i for i, tt in enumerate(times) if lt >= tt] or [-1])
            pi = 0
            for k, pg in enumerate(pages):
                if active >= pg[0][0]:
                    pi = k
            spk = who_of_word[pages[pi][0][0]] if who_of_word and pages else None
            key = (sc_i, pi, active, spk)
            if key not in cache:
                sub = cache.get("sub_layer")
                cache.clear()
                if sub is not None and sc.get("sub"):
                    cache["sub_layer"] = sub
                cache[key] = caption_layer(words, pages[pi], active, cap_font,
                                           label=SPEAKER_LABELS.get(spk))
            frame.alpha_composite(cache[key])
            # progress bar keeps viewers oriented (and watching to the end)
            d = ImageDraw.Draw(frame, "RGBA")
            d.rectangle((0, H - 9, W, H - 3), fill=(255, 255, 255, 40))
            d.rectangle((0, H - 9, int(W * fr / max(1, nframes - 1)), H - 3), fill=(*GOLD, 230))
            # quick fade from black at the very start, crossfade between scenes
            k = fr - f0
            if fr < 6:
                frame = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), frame, fr / 6)
            elif sc_i > 0 and k < XFADE and prev_last is not None:
                frame = Image.blend(prev_last, frame, (k + 1) / (XFADE + 1))
            if fr == f1 - 1:
                prev_last = frame.copy()
            enc.stdin.write(frame.convert("RGB").tobytes())
        if isinstance(big, VideoBG):
            big.close()
        print(f"scene {sc_i + 1}/{len(scenes)} done", file=sys.stderr)
    enc.stdin.close()
    enc.wait()

    out = args.out or os.path.join(rd, os.path.basename(os.path.normpath(rd)) + ".mp4")
    if args.endcard:
        start = args.endcard_start
        if start is None:
            start = audio_duration(args.endcard) - args.endcard_len
        tail = os.path.join(work, "endcard.mp4")
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{start:.2f}", "-i", args.endcard,
                        "-vf", f"scale={W}:{H},fps={FPS},setsar=1", "-af", "aresample=44100", "-ac", "2",
                        "-c:v", "libx264", "-preset", PRESET, "-crf", CRF, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                        tail], check=True)
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", silent, "-i", tail, "-filter_complex",
                        "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", PRESET, "-crf", CRF, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                        "-profile:v", "high", "-level", "4.1", "-ar", "48000", "-movflags", "+faststart", out],
                       check=True)
    else:
        os.replace(silent, out)
    print(out)


if __name__ == "__main__":
    main()
