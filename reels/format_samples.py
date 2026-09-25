#!/usr/bin/env python3
"""Render a sampler reel: a ~6.5 s mini example of every Africa Blind Spot video format.

Usage: python3 format_samples.py <out_dir> [--endcard brand_reel.mp4]
Uses only facts verified in this repo's briefings (as of 25 Sept 2026).
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim  # noqa: E402
import formats  # noqa: E402
import mapviz  # noqa: E402
import render_reel as R  # noqa: E402

W, H, FPS = R.W, R.H, R.FPS
GOLD = R.GOLD
F = R.font
SEG = 6.5  # seconds per format
HERE = os.path.dirname(os.path.abspath(__file__))


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


# ---------------------------------------------------------------- 3-12. the shared format library
# The data lives in format-templates/script.json (one ready-to-copy scene per format),
# so the sampler and real reels draw every format with the same code (formats.py).

TEMPLATES = json.load(open(os.path.join(HERE, "format-templates", "script.json")))["scenes"]
AUDIO = os.path.join(HERE, "format-templates", "vo", "audiogram.mp3")


def from_library(k, caption=False):
    sc = TEMPLATES[k]
    ctx = {"vo": AUDIO, "reel_dir": os.path.join(HERE, "format-templates")}

    def fn(t):
        img = formats.render(sc["bg_spec"], t / SEG, t, SEG, ctx)
        img.alpha_composite(R.headline_layer(sc["head"], sc.get("gold", 1), cy=420))
        return img, (sc["lines"][0]["show"] if caption else None)
    return fn


FORMATS = [("ANIMATED EXPLAINER", f_explainer), ("MAP STORY", f_map), ("DATA RACE", from_library(2, True)),
           ("WEEKLY ROUNDUP", from_library(3)), ("QUIZ", from_library(4)), ("MYTH VS REALITY", from_library(5)),
           ("TIMELINE", from_library(6)), ("THEN VS NOW", from_library(7)), ("KINETIC QUOTE", from_library(8)),
           ("WHITEBOARD", from_library(9)), ("CAROUSEL", from_library(10)), ("AUDIOGRAM", from_library(11, True))]


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
