#!/usr/bin/env python3
"""Split a day's NARRATIONS.md into clean CapCut-ready text files.

Usage: python3 narrations/split.py narrations/YYYY-MM-DD

Each story in NARRATIONS.md is a "## N. Title" block with its narration between
a line containing only <<< and a line containing only >>>. Writes NN-slug.txt per
story, prints word counts and estimated duration, and warns about characters that
text-to-speech reads badly.
"""
import os
import re
import sys
import unicodedata

BAD = {"%": "percent", "$": "dollars", "~": "about", "&": "and", "/": "or / per", "(": "bracket", "*": "asterisk",
       "#": "hash"}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def main():
    day = sys.argv[1]
    text = open(os.path.join(day, "NARRATIONS.md"), encoding="utf-8").read()
    stories = re.findall(r"^## (\d+)\. (.+?)$(.*?)^<<<$\n(.*?)\n^>>>$", text, re.S | re.M)
    if not stories:
        sys.exit("no stories found")
    total = 0
    for num, title, _meta, body in stories:
        body = body.strip()
        path = os.path.join(day, f"{int(num):02d}-{slug(title)}.txt")
        open(path, "w", encoding="utf-8").write(body + "\n")
        words = len(body.split())
        total += words
        warn = sorted({c for c in body if c in BAD})
        flag = f"  WARNING, TTS-unfriendly: {' '.join(warn)}" if warn else ""
        print(f"{int(num):2d}. {title[:48]:48s} {words:4d} words  ~{words / 2.5:4.0f} s{flag}")
    print(f"{len(stories)} narrations, {total} words, ~{total / 2.5 / 60:.1f} min in total")


if __name__ == "__main__":
    main()
