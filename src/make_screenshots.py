#!/usr/bin/env python3
"""Generate README screenshots under docs/screenshots/."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
OUT = ROOT / 'docs' / 'screenshots'
BG = '#f4f4f2'
FG = '#0a0a0a'
MUTED = '#8a8b8c'
ACCENT = '#a31f34'


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    path = DIST / f'MITMediaLabFont-{weight}.ttf'
    return ImageFont.truetype(str(path), size=size)


def save(img: Image.Image, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    img.save(path)
    print(f'  {path}')


def specimen() -> None:
    w, h = 1200, 640
    img = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(img)
    d.text((48, 40), 'MIT MEDIA LAB FONT', fill=FG, font=font('Black', 64))
    d.text((48, 130), 'A 7×7 grid typeface', fill=MUTED, font=font('Regular', 28))
    d.text((48, 220), 'THE QUICK BROWN FOX', fill=FG, font=font('Bold', 48))
    d.text((48, 290), 'jumps over the lazy dog', fill=FG, font=font('Medium', 40))
    d.text((48, 370), '0123456789  ±÷∞∑√  áéñüß', fill=FG, font=font('Regular', 36))
    d.text((48, 450), 'Media Lab · CC BY-NC-SA 4.0', fill=ACCENT, font=font('Bold', 28))
    save(img, 'specimen.png')


def weights() -> None:
    names = ['Thin', 'Light', 'Regular', 'Medium', 'Bold', 'Black']
    w, h = 1200, 120 + 72 * len(names)
    img = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(img)
    y = 40
    for name in names:
        d.text((48, y), f'{name}', fill=MUTED, font=font('Regular', 22))
        d.text((220, y - 4), 'MIT MEDIA LAB', fill=FG, font=font(name, 44))
        y += 72
    save(img, 'weights.png')


def charset() -> None:
    lines = [
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'abcdefghijklmnopqrstuvwxyz',
        '0123456789 .,;:!?-+*/=()[]{}',
        'áéíóúñüß æœ ©®™ €£  ←→↑↓',
        '∞√∑∏∂ ≤≥≠≈ ±÷ ½¼¾',
    ]
    w, h = 1200, 80 + 70 * len(lines)
    img = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(img)
    y = 36
    for line in lines:
        d.text((40, y), line, fill=FG, font=font('Regular', 32))
        y += 70
    save(img, 'charset.png')


def sizes() -> None:
    sizes = [12, 16, 24, 36, 48, 72, 96]
    w, h = 1200, 80 + sum(s + 28 for s in sizes)
    img = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(img)
    y = 32
    for s in sizes:
        d.text((40, y), f'{s}px', fill=MUTED, font=font('Regular', 18))
        d.text((120, y), 'Media Lab Font', fill=FG, font=font('Bold', s))
        y += s + 28
    save(img, 'sizes.png')


def main() -> None:
    print('screenshots →', OUT)
    specimen()
    weights()
    charset()
    sizes()


if __name__ == '__main__':
    main()
