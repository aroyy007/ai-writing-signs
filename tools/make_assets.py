#!/usr/bin/env python3
"""Regenerate docs/assets/demo.gif and docs/assets/social-preview.png.

Dev-only: needs Pillow (pip install pillow) and the macOS Menlo/Helvetica fonts,
or pass --mono / --sans paths to other TTF fonts. The GIF shows real scan.py output.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "skills" / "ai-writing-signs" / "scripts" / "scan.py"
OUT = ROOT / "docs" / "assets"

BG, BAR, FG, DIM = (22, 24, 29), (40, 43, 51), (220, 223, 228), (120, 126, 138)
RED, YEL, GRN, CYA, MAG = (240, 98, 98), (229, 192, 123), (126, 211, 135), (97, 205, 220), (198, 140, 230)


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except OSError:
        sys.exit(f"font not found: {path} (use --mono/--sans)")


def scan_lines(path, max_lines):
    out = subprocess.run([sys.executable, "-I", str(SCAN), str(path)], capture_output=True,
                         text=True, check=True).stdout.splitlines()
    out = [l for l in out if not l.startswith("typography:") and not l.startswith("invisible:")]
    return out[:max_lines]


def segments(line):
    """Split a report line into (text, colour) segments."""
    if line.startswith("words="):
        head, _, verdict = line.partition("->")
        col = GRN if "low density" in verdict else (RED if ("high" in verdict or "hard" in verdict) else YEL)
        return [(head + "-> ", DIM), (verdict.strip(), col)]
    if line.startswith("categories:"):
        return [("categories: ", DIM), (line[len("categories: "):], YEL)]
    if line.startswith("  L"):
        return [(line, FG)]
    if line.startswith('    "'):
        return [(line, DIM)]
    if line.startswith("    ") and ":" in line:
        name, _, rest = line.partition(":")
        return [(name + ":", CYA), (rest, RED)]
    if line.startswith("flagged"):
        return [(line, MAG)]
    return [(line, FG)]


def clip(line, n):
    return line if len(line) <= n else line[: n - 3] + "..."


def make_gif(mono_path):
    W, LH, PAD, COLS = 1000, 21, 18, 98
    f = font(mono_path, 15)
    before = ["$ python3 scan.py examples/before.md"] + [clip(l, COLS) for l in scan_lines(ROOT / "examples/before.md", 22)]
    after = ["$ python3 scan.py examples/after.md"] + [clip(l, COLS) for l in scan_lines(ROOT / "examples/after.md", 4)]
    H = 38 + PAD * 2 + LH * (len(before) + 1)

    def frame(lines, typed=None):
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, W, 30], fill=BAR)
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            d.ellipse([14 + i * 20, 9, 26 + i * 20, 21], fill=c)
        d.text((W // 2 - 70, 7), "ai-writing-signs", font=f, fill=DIM)
        y = 30 + PAD
        for i, line in enumerate(lines):
            x = PAD
            if line.startswith("$ "):
                text = line if typed is None or i != len(lines) - 1 else line[:typed]
                d.text((x, y), "$ ", font=f, fill=GRN)
                d.text((x + f.getlength("$ "), y), text[2:], font=f, fill=FG)
                if typed is not None and i == len(lines) - 1:
                    cx = x + f.getlength(text)
                    d.rectangle([cx + 1, y + 2, cx + 9, y + 18], fill=FG)
            else:
                for seg, col in segments(line):
                    d.text((x, y), seg, font=f, fill=col)
                    x += f.getlength(seg)
            y += LH
        return im

    frames, durs = [], []

    def add(im, ms):
        frames.append(im)
        durs.append(ms)

    def play(cmd_and_output, hold):
        cmd = cmd_and_output[0]
        for n in range(2, len(cmd) + 1, 2):
            add(frame([cmd], typed=n), 45)
        add(frame([cmd], typed=len(cmd)), 400)
        for k in range(2, len(cmd_and_output) + 1):
            add(frame(cmd_and_output[:k]), 70)
        frames[-1:] = [frames[-1]]
        durs[-1] = hold

    play(before, 3800)
    play(after, 3500)
    OUT.mkdir(parents=True, exist_ok=True)
    pal = [im.convert("P", palette=Image.ADAPTIVE, colors=64) for im in frames]
    pal[0].save(OUT / "demo.gif", save_all=True, append_images=pal[1:], duration=durs, loop=0, optimize=True)
    print(f"wrote docs/assets/demo.gif ({len(frames)} frames)")


def make_preview(mono_path, sans_path):
    W, H = 1280, 640
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    title, sub, mono = font(sans_path, 84, 1), font(sans_path, 32), font(mono_path, 26)
    d.text((80, 110), "ai-writing-signs", font=title, fill=FG)
    d.text((84, 225), "Find and fix the signs of unedited AI writing.", font=sub, fill=DIM)
    d.text((84, 270), "A Claude skill + a dependency-free Python scanner.", font=sub, fill=DIM)
    rows = [
        ["delve", "tapestry", "pivotal role", "serves as a testament"],
        ["not just X, it's Y", ", underscoring", "experts agree"],
        ["oaicite", "utm_source=chatgpt.com", "U+200B", "In conclusion,"],
    ]
    y = 360
    for row in rows:
        x = 84
        for chip in row:
            w = mono.getlength(chip)
            d.rounded_rectangle([x, y, x + w + 32, y + 50], radius=10, fill=BAR)
            d.text((x + 16, y + 10), chip, font=mono, fill=RED)
            d.line([x + 14, y + 26, x + w + 18, y + 26], fill=RED, width=2)
            x += w + 48
        y += 66
    d.text((84, 575), "github.com/aroyy007/ai-writing-signs", font=font(mono_path, 22), fill=CYA)
    im.save(OUT / "social-preview.png", optimize=True)
    print("wrote docs/assets/social-preview.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mono", default="/System/Library/Fonts/Menlo.ttc")
    ap.add_argument("--sans", default="/System/Library/Fonts/Helvetica.ttc")
    a = ap.parse_args()
    make_gif(a.mono)
    make_preview(a.mono, a.sans)
