#!/usr/bin/env python3
"""Render Open Graph / social card image with all brand + group marks.

Usage:
    python3 src/make_og.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from brand_glyphs import (  # noqa: E402
    MEDIA_LAB_CODEPOINT,
    MIT_CODEPOINT,
    MIT_FIT,
    MIT_WIDTH_CELLS,
)
from glyphs import GLYPHS  # noqa: E402
from svg_to_glyph import GRID  # noqa: E402

OUT = ROOT / 'web' / 'static' / 'og.png'

W, H = 1200, 630
DARK = (10, 10, 10)
CREAM = (236, 232, 222)
MUTED = (150, 146, 138)
RED = (163, 31, 52)


def glyph_blocks(char: str) -> list[tuple]:
    g = GLYPHS[char]
    if g.get('blocks'):
        return list(g['blocks'])
    blocks = []
    for kind, *rest in g['s']:
        if kind == 'h':
            y, x1, x2 = rest
            blocks.append((x1, y - 0.5, max(0.01, x2 - x1), 1.0))
        elif kind == 'v':
            x, y1, y2 = rest
            blocks.append((x - 0.5, y1, 1.0, max(0.01, y2 - y1)))
    return blocks


def draw_glyph(
    im: Image.Image,
    char: str,
    origin: tuple[float, float],
    cell: float,
    color: tuple[int, int, int],
    *,
    rows: int = 7,
) -> None:
    d = ImageDraw.Draw(im)
    ox, oy = origin
    for x, y, bw, bh in glyph_blocks(char):
        top = rows - (y + bh)
        x0 = ox + x * cell
        y0 = oy + top * cell
        d.rectangle(
            [x0, y0, x0 + bw * cell - 0.25, y0 + bh * cell - 0.25],
            fill=color,
        )


def draw_mit_fit(
    im: Image.Image,
    origin: tuple[float, float],
    box: float,
    color: tuple[int, int, int],
) -> float:
    """Draw MIT wordmark scaled to fit inside a ``box``×``box`` square."""
    cell = box / MIT_WIDTH_CELLS
    h = GRID * cell
    ox, oy = origin
    draw_glyph(im, chr(MIT_CODEPOINT), (ox, oy + (box - h) / 2), cell, color)
    return box


def draw_mit_cap(
    im: Image.Image,
    origin: tuple[float, float],
    cap_px: float,
    color: tuple[int, int, int],
) -> float:
    """Draw MIT wordmark at native proportions with height ``cap_px``."""
    cell = cap_px / GRID
    draw_glyph(im, chr(MIT_CODEPOINT), origin, cell, color)
    return MIT_WIDTH_CELLS * cell


def load_fonts():
    dist = ROOT / 'dist'
    paths = [dist / f'MITMediaLabFont-{w}.ttf'
             for w in ('Black', 'Bold', 'Medium', 'Regular')]
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f'missing {p.name}; build fonts first')
    return (
        ImageFont.truetype(str(paths[0]), 44),
        ImageFont.truetype(str(paths[1]), 22),
        ImageFont.truetype(str(paths[2]), 18),
        ImageFont.truetype(str(paths[3]), 18),
    )


def _smoothstep(t: float) -> float:
    t = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
    return t * t * (3.0 - 2.0 * t)


def _smootherstep(t: float) -> float:
    t = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def apply_content_gradient(im: Image.Image) -> Image.Image:
    base = im.convert('RGBA')
    alpha = Image.new('L', (W, H), 0)
    px = alpha.load()
    core_l, core_r, core_t, core_b = 160, 980, 140, 460
    feather_x, feather_y, peak = 260.0, 220.0, 230
    for y in range(H):
        if y < core_t:
            vy = 1.0 - _smootherstep((core_t - y) / feather_y)
        elif y > core_b:
            vy = 1.0 - _smootherstep((y - core_b) / feather_y)
        else:
            vy = 1.0
        for x in range(W):
            if x < core_l:
                vx = 1.0 - _smootherstep((core_l - x) / feather_x)
            elif x > core_r:
                vx = 1.0 - _smootherstep((x - core_r) / feather_x)
            else:
                vx = 1.0
            px[x, y] = int(peak * _smoothstep(vx * vy))
    overlay = Image.new('RGBA', (W, H), (*DARK, 0))
    overlay.putalpha(alpha)
    return Image.alpha_composite(base, overlay).convert('RGB')


def main() -> None:
    icons = [chr(cp) for cp in range(0xE000, 0xE018)]
    mit = chr(MIT_CODEPOINT)
    ml = chr(MEDIA_LAB_CODEPOINT)
    mosaic_marks = [mit, ml, *icons]

    og = Image.new('RGB', (W, H), DARK)
    cell_bg = 9.0
    mark = GRID * cell_bg
    gap_x, gap_y = 22, 26
    cols = 13
    step_x = mark + gap_x
    step_y = mark + gap_y
    x0 = (W - (cols * step_x - gap_x)) / 2
    i, y = 0, -12.0
    mosaic_color = (58, 56, 52)
    while y < H + mark:
        for c in range(cols):
            draw_glyph(
                og, mosaic_marks[i % len(mosaic_marks)],
                (x0 + c * step_x, y), cell_bg, mosaic_color,
            )
            i += 1
        y += step_y

    og = apply_content_gradient(og)
    d = ImageDraw.Draw(og)
    title, sub, small, body = load_fonts()

    feat = 112
    left, top, stack_gap = 72, 100, 56

    # Featured column: MIT fit-to-box so it matches Media Lab square
    draw_mit_fit(og, (left, top), feat, CREAM)
    d.text((left, top + feat + 10), 'U+E030', fill=MUTED, font=small)
    ml_top = top + feat + stack_gap
    draw_glyph(og, ml, (left, ml_top), feat / GRID, CREAM)
    d.text((left, ml_top + feat + 10), 'MEDIA LAB', fill=CREAM, font=sub)
    d.text((left, ml_top + feat + 36), 'U+E031', fill=MUTED, font=small)

    tx = left + feat + 56
    ty = top
    title_text = 'MEDIA LAB FONT'
    tb = d.textbbox((0, 0), title_text, font=title)
    title_ink_h = tb[3] - tb[1]
    mit_w = draw_mit_cap(og, (tx, ty + 6), title_ink_h, CREAM)
    d.text((tx + mit_w + 14, ty + 6 - tb[1]), title_text, fill=CREAM, font=title)
    d.multiline_text(
        (tx, ty + title_ink_h + 36),
        'A 7×7 grid typeface with the official wordmark,\nMedia Lab mark, and 24 research group symbols.',
        fill=MUTED, font=body, spacing=10,
    )
    d.text(
        (tx, ty + title_ink_h + 104),
        'Thin · Light · Regular · Medium · Bold · Black',
        fill=(110, 106, 98), font=small,
    )
    d.rectangle([tx, ty + title_ink_h + 136, tx + 56, ty + title_ink_h + 139], fill=RED)

    foot_y = ty + title_ink_h + 166
    foot_label = 'Media Lab'
    fb = d.textbbox((0, 0), foot_label, font=small)
    foot_ink_h = fb[3] - fb[1]
    foot_w = draw_mit_cap(og, (tx, foot_y), foot_ink_h, CREAM)
    d.text((tx + foot_w + 10, foot_y - fb[1]), foot_label, fill=MUTED, font=small)
    d.text((tx, foot_y + 36), 'Nataliya Kosmyna · Eugene Hauptmann', fill=CREAM, font=sub)
    d.text((tx, foot_y + 68), '© 2026 · CC BY-NC-SA 4.0', fill=(110, 106, 98), font=small)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    og.save(OUT, 'PNG', optimize=True)
    print(f'wrote {OUT} ({OUT.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
