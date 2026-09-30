"""Storyboard check for a rendered reel: one frame per scene, at the exact scene midpoints.

    python3 storyboard.py <reel_dir> <reel.mp4> [--out storyboard.jpg] [--cols 5]

Scene timing is rebuilt the way render_reel.py builds it: the voice clip length
(or the text-led estimate, words / read_wps + 0.3, when a clip is missing), plus
the scene "gap" and "hold". Each tile is labelled with its scene number and
timestamp. Instagram UI zones (--ig-safe) are outlined in red, so overlaps show.
"""
import argparse
import json
import os
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TW, TH = 432, 768  # tile size (0.4 x 1080x1920)


def clip_len(path):
    out = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True).stderr
    h, m, s = out.split("Duration: ")[1].split(",")[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def scene_times(rd, script):
    wps, gap = script.get("read_wps", 2.7), script.get("gap", 0.0)
    line_gap = 0.12  # render_reel.LINE_GAP
    t, out = 0.0, []
    for i, sc in enumerate(script["scenes"], 1):
        if "lines" in sc:
            d = 0.0
            for k, ln in enumerate(sc["lines"]):
                src = os.path.join(rd, "vo", ln["file"])
                d += clip_len(src) / ln.get("tempo", script.get("tempo", 1.0)) if os.path.exists(src) else \
                    (len(ln["say"].split()) / wps + 0.3) / ln.get("tempo", script.get("tempo", 1.0))
                d += line_gap if k < len(sc["lines"]) - 1 else 0
        else:
            d = clip_len(os.path.join(rd, "vo", f"{i:02d}.mp3"))
        d += sc.get("gap", gap) + sc.get("hold", 0.0)
        out.append((t, d))
        t += d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir")
    ap.add_argument("video")
    ap.add_argument("--out")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--no-zones", action="store_true")
    a = ap.parse_args()
    script = json.load(open(os.path.join(a.reel_dir, "script.json")))
    times = scene_times(a.reel_dir, script)
    rows = -(-len(times) // a.cols)
    sheet = Image.new("RGB", (a.cols * TW, rows * (TH + 44)), (0, 0, 0))
    font = ImageFont.truetype(BOLD, 26)
    for i, (s, d) in enumerate(times):
        mid = s + d / 2
        png = f"/tmp/_sb_{os.getpid()}_{i}.png"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{mid:.3f}", "-i", a.video, "-frames:v", "1", png], check=True)
        fr = Image.open(png).convert("RGB").resize((TW, TH))
        os.remove(png)
        if not a.no_zones:  # Reels UI: top 140, right 120 (y 1020-1760), bottom from y 1560
            z, k = ImageDraw.Draw(fr), TW / 1080
            z.line([(0, 140 * k), (TW, 140 * k)], fill=(255, 60, 60), width=1)
            z.rectangle(((1080 - 120) * k, 1020 * k, TW - 1, 1760 * k), outline=(255, 60, 60))
            z.line([(0, 1560 * k), (TW, 1560 * k)], fill=(255, 60, 60), width=1)
        x, y = (i % a.cols) * TW, (i // a.cols) * (TH + 44)
        sheet.paste(fr, (x, y + 44))
        ImageDraw.Draw(sheet).text((x + 12, y + 8), f"{i + 1:02d}  @ {mid:5.2f}s", font=font, fill=(212, 170, 52))
    out = a.out or os.path.join(a.reel_dir, "storyboard.jpg")
    sheet.save(out, quality=88)
    print(out, f"({len(times)} scenes, {times[-1][0] + times[-1][1]:.1f}s before end card)")


if __name__ == "__main__":
    main()
