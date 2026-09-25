#!/usr/bin/env python3
"""Synthesize a royalty-free underscore for reels (no external services).

Hopeful minor-to-major progression (Am - F - C - G) at 100 BPM: warm pad,
pulsing eighth-note bass, soft kick, and shakers that enter after the intro;
the last third brightens. Designed to sit under a voiceover.

Usage: python3 music_bed.py out.wav [seconds]
"""
import sys
import wave

import numpy as np

SR = 44100
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
# chord roots (Hz) and chord tones as semitone offsets
PROG = [(220.00, (0, 3, 7)), (174.61, (0, 4, 7)), (261.63, (0, 4, 7)), (196.00, (0, 4, 7))]


def env(n, a, r):
    e = np.ones(n)
    a, r = int(a * SR), int(r * SR)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def render(seconds):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    L = np.zeros(n)
    R = np.zeros(n)
    rng = np.random.default_rng(7)
    bright_from = seconds * 0.62
    bars = int(np.ceil(seconds / BAR))
    for b in range(bars):
        root, tones = PROG[b % 4]
        s, e = int(b * BAR * SR), min(n, int((b + 1) * BAR * SR))
        if s >= n:
            break
        seg = np.arange(e - s) / SR
        # pad: detuned sines over the chord, an octave spread
        pad = np.zeros(e - s)
        for k, semi in enumerate(tones):
            f = root * 2 ** (semi / 12)
            for det in (-0.004, 0.004):
                pad += np.sin(2 * np.pi * f * (1 + det) * seg + k)
            if b * BAR >= bright_from:
                pad += 0.5 * np.sin(2 * np.pi * f * 2 * seg)  # brighter octave in the lift
        pad *= env(e - s, 0.35, 0.35) * 0.05
        L[s:e] += pad
        R[s:e] += np.roll(pad, 220)
        # bass: eighth-note pulse on the root, an octave down
        for q in range(8):
            qs = s + int(q * BEAT / 2 * SR)
            qe = min(e, qs + int(BEAT / 2 * SR * 0.9))
            if qs >= e:
                break
            qt = np.arange(qe - qs) / SR
            f = root / 2
            tone = np.sin(2 * np.pi * f * qt) + 0.35 * np.sin(2 * np.pi * 2 * f * qt)
            tone *= np.exp(-qt * 7) * 0.16
            L[qs:qe] += tone
            R[qs:qe] += tone
        # drums: soft kick on 1 and 3 (every beat in the lift), shakers on 16ths after the intro
        for q in range(4):
            if q % 2 and b * BAR < bright_from:
                continue
            ks = s + int(q * BEAT * SR)
            if ks >= n:
                break
            ke = min(n, ks + int(0.25 * SR))
            kt = np.arange(ke - ks) / SR
            kick = np.sin(2 * np.pi * (50 + 70 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14) * 0.28
            L[ks:ke] += kick
            R[ks:ke] += kick
        if b * BAR >= BAR * 2:
            for q in range(16):
                hs = s + int(q * BEAT / 4 * SR)
                if hs >= n:
                    break
                he = min(n, hs + int(0.05 * SR))
                ht = np.arange(he - hs) / SR
                amp = (0.05 if q % 2 else 0.028) * (1.3 if b * BAR >= bright_from else 1.0)
                hat = rng.standard_normal(he - hs) * np.exp(-ht * 70) * amp
                hat = np.diff(np.concatenate([[0], hat]))  # crude high-pass
                (L if q % 4 in (1, 2) else R)[hs:he] += hat
                (R if q % 4 in (1, 2) else L)[hs:he] += hat * 0.5
    # gentle overall shape
    shape = env(n, 1.5, 2.5)
    L, R = L * shape, R * shape
    peak = max(np.abs(L).max(), np.abs(R).max()) or 1
    return np.stack([L, R], axis=1) / peak * 0.8


def main():
    out = sys.argv[1]
    secs = float(sys.argv[2]) if len(sys.argv) > 2 else 60
    audio = render(secs)
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())
    print(out)


if __name__ == "__main__":
    main()
