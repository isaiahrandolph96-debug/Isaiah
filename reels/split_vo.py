#!/usr/bin/env python3
"""Split one full voiceover take into per-scene clips (vo/01.mp3, vo/02.mp3, ...).

The house voice is recorded as ONE take of the whole script (every scene's "say"
line, joined by blank lines), so the delivery stays even and it costs one request.
This tool finds the paragraph pauses between scenes, cuts there, trims long
internal pauses and speeds the read up slightly, then prints a speaking-rate check
per clip (chars/s should be similar for every clip; an outlier means a bad cut).

Usage:
  python3 split_vo.py <reel_dir> [--take <reel_dir>/vo/full.mp3] [--tempo 1.1] [--pause 0.32]
  python3 split_vo.py <reel_dir> --print-script   # the text to send to the TTS
"""
import argparse
import json
import os
import re
import subprocess

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = "ffmpeg"


def says(script):
    out = []
    for sc in script["scenes"]:
        out.append(" ".join(ln["say"] for ln in sc["lines"]) if "lines" in sc else sc["say"])
    return out


def duration(path):
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: ([\d:.]+)", err).group(1).split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def silences(path, min_dur=0.28):
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", path, "-af", f"silencedetect=n=-40dB:d={min_dur}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    ends = re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", err)
    return [(float(e) - float(d) / 2, float(d)) for e, d in ends]  # (midpoint, length)


def find_cuts(texts, sil, total):
    """Paragraph breaks are the longer pauses near where the character count says they should be.
    Each cut re-anchors the estimate for the rest of the take."""
    speech0 = sil[0][0] + sil[0][1] / 2 if sil and sil[0][0] < 0.8 else 0.0
    speech1 = sil[-1][0] - sil[-1][1] / 2 if sil and sil[-1][0] > total - 0.8 else total
    cuts, t0 = [0.0], speech0
    for i in range(len(texts) - 1):
        rest = sum(len(x) for x in texts[i:])
        exp = t0 + (speech1 - t0) * len(texts[i]) / rest
        cand = [s for s in sil if cuts[-1] + 1.0 < s[0] < speech1 - 0.5]
        mid, ln = min(cand, key=lambda s: abs(s[0] - exp) - 3.0 * s[1])
        cuts.append(mid)
        t0 = mid + ln / 2
    cuts.append(total)
    return cuts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir")
    ap.add_argument("--take", help="full take (default <reel_dir>/vo/full.mp3)")
    ap.add_argument("--tempo", type=float, default=1.1, help="speed-up without pitch change")
    ap.add_argument("--pause", type=float, default=0.32, help="internal pauses longer than this are trimmed")
    ap.add_argument("--print-script", action="store_true")
    a = ap.parse_args()
    script = json.load(open(os.path.join(a.reel_dir, "script.json")))
    texts = says(script)
    if a.print_script:
        print("\n\n".join(texts))
        return
    take = a.take or os.path.join(a.reel_dir, "vo", "full.mp3")
    total = duration(take)
    cuts = find_cuts(texts, silences(take), total)
    af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_duration=0.02,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB:start_duration=0.02,areverse,"
          f"silenceremove=stop_periods=-1:stop_duration={a.pause}:stop_threshold=-42dB:stop_silence=0.26,"
          f"atempo={a.tempo},apad=pad_dur=0.12")
    rates = []
    for i, text in enumerate(texts):
        out = os.path.join(a.reel_dir, "vo", f"{i + 1:02d}.mp3")
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{cuts[i]:.3f}", "-to", f"{cuts[i + 1]:.3f}", "-i", take,
                        "-af", af, "-ar", "44100", "-b:a", "192k", out], check=True)
        d = duration(out)
        rates.append(len(text) / d)
        print(f"{out}  cut {cuts[i]:6.2f}-{cuts[i + 1]:6.2f}s  {d:5.2f}s  {rates[-1]:4.1f} chars/s  | {text[:48]}")
    body = sorted(rates[:-1]) if len(rates) > 2 else rates  # the short CTA line reads fast; ignore it
    med = body[len(body) // 2]
    odd = [i + 1 for i, r in enumerate(rates[:-1]) if abs(r - med) / med > 0.3]
    print("CHECK: speaking rate consistent" if not odd else f"CHECK: clips {odd} look mis-cut (rate far from {med:.1f})")


if __name__ == "__main__":
    main()
