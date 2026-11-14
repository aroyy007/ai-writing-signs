#!/usr/bin/env python3
"""Package skills/ai-writing-signs into dist/ai-writing-signs.skill (a zip) for Claude.ai upload."""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "ai-writing-signs"
SRC = ROOT / "skills" / NAME
OUT = ROOT / "dist" / f"{NAME}.skill"
SKIP_PARTS = {"__pycache__", ".DS_Store"}


def main():
    if not (SRC / "SKILL.md").is_file():
        sys.exit(f"missing {SRC / 'SKILL.md'}")
    OUT.parent.mkdir(exist_ok=True)
    files = sorted(p for p in SRC.rglob("*") if p.is_file() and not SKIP_PARTS & set(p.parts))
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, Path(NAME) / p.relative_to(SRC))
    print(f"wrote {OUT.relative_to(ROOT)} ({len(files)} files)")


if __name__ == "__main__":
    main()
