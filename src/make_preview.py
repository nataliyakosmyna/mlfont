#!/usr/bin/env python3
"""Render a glyph-grid PNG for visual QA (dist/preview-glyphs.png)."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from glyphs import GLYPHS  # noqa: E402

FONT = ROOT / 'dist' / 'MITMediaLabFont-Regular.ttf'
OUT = ROOT / 'dist' / 'preview-glyphs.png'

CELL = 72
PAD = 8
COLS = 16


def main() -> None:
    chars = [c for c in GLYPHS if c != ' ']
    # Prefer printable / named order: ASCII-ish first, then rest by codepoint
    chars.sort(key=lambda c: (ord(c) >= 0xE000, ord(c)))
    rows = (len(chars) + COLS - 1) // COLS
    img = Image.new('RGB', (COLS * CELL, rows * CELL), '#f4f4f2')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(FONT), size=36)
    label = ImageFont.load_default()

    for i, ch in enumerate(chars):
        r, c = divmod(i, COLS)
        x0, y0 = c * CELL, r * CELL
        draw.rectangle([x0, y0, x0 + CELL - 1, y0 + CELL - 1], outline='#d6d5d2')
        # Glyph centered
        bbox = draw.textbbox((0, 0), ch, font=font)
        gw, gh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        gx = x0 + (CELL - gw) // 2 - bbox[0]
        gy = y0 + (CELL - gh) // 2 - bbox[1] - 4
        draw.text((gx, gy), ch, fill='#0a0a0a', font=font)
        cp = f'U+{ord(ch):04X}'
        draw.text((x0 + 2, y0 + CELL - 12), cp, fill='#8a8b8c', font=label)

    OUT.parent.mkdir(exist_ok=True)
    img.save(OUT)
    print(f'wrote {OUT} ({len(chars)} glyphs)')


if __name__ == '__main__':
    main()
