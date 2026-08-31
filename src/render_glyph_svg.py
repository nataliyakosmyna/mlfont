"""Export individual glyphs as standalone SVG files.

Uses the same ``glyphs.GLYPHS`` source as ``build_font.py``, so SVGs
always match the font. Useful for documentation, embedding individual
letters into other materials, or comparing against the original Media
Lab reference glyphs in ``../reference_glyphs/``.

Each SVG sits on a 7-cell-tall viewBox at 50 px / cell (matching the
Media Lab reference SVG convention). Glyphs with descenders extend
below the baseline within the viewBox.

Usage (run from anywhere; output lands in <repo_root>/dist/svg/):

    python3 src/render_glyph_svg.py A                 # one glyph at Regular
    python3 src/render_glyph_svg.py A B M K --weight bold
    python3 src/render_glyph_svg.py --all             # every glyph
    python3 src/render_glyph_svg.py --weights all     # one subfolder per weight
    python3 src/render_glyph_svg.py A --grid          # add a 7×7 grid overlay
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from glyphs import GLYPHS

UNIT_PX = 50           # match the Media Lab reference: 50px per cell
BODY_H = 7             # cells

WEIGHTS = {
    'thin':    0.35,
    'light':   0.6,
    'regular': 0.9,
    'medium':  1.15,
    'bold':    1.4,
    'black':   1.8,
}


def rect_path(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def diag_path(x1, y1, x2, y2, t):
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length
    ex, ey = dx / length * (t / 2), dy / length * (t / 2)
    half = t / 2
    return [
        (x1 - ex + nx * half, y1 - ey + ny * half),
        (x2 + ex + nx * half, y2 + ey + ny * half),
        (x2 + ex - nx * half, y2 + ey - ny * half),
        (x1 - ex - nx * half, y1 - ey - ny * half),
    ]


def stroke_to_poly(stroke, w):
    half = w / 2
    kind = stroke[0]
    if kind == 'h':
        _, y, x1, x2 = stroke
        return rect_path(x1 - half, y - half, (x2 - x1) + w, w)
    if kind == 'v':
        _, x, y1, y2 = stroke
        return rect_path(x - half, y1 - half, w, (y2 - y1) + w)
    if kind == 'd':
        _, x1, y1, x2, y2 = stroke
        return diag_path(x1, y1, x2, y2, w)
    raise ValueError(kind)


def glyph_svg(char, weight_cells, fg='#000', show_grid=False):
    g = GLYPHS[char]
    body_w = g['w']
    margin = 0.5
    vw = (body_w + 2 * margin) * UNIT_PX
    vh = (BODY_H + 2 * margin) * UNIT_PX

    if g.get('blocks'):
        polys = [rect_path(x, y, bw, bh) for x, y, bw, bh in g['blocks']]
    else:
        polys = [stroke_to_poly(s, weight_cells) for s in g['s']]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {vw:.1f} {vh:.1f}" width="{vw:.0f}" height="{vh:.0f}">'
    ]
    if show_grid:
        parts.append('<g stroke="#e5e1d6" stroke-width="0.5" fill="none">')
        for i in range(BODY_H + 1):
            y = (margin + i) * UNIT_PX
            parts.append(
                f'<line x1="{margin*UNIT_PX:.1f}" y1="{y:.1f}" '
                f'x2="{(margin+body_w)*UNIT_PX:.1f}" y2="{y:.1f}"/>'
            )
        for i in range(body_w + 1):
            x = (margin + i) * UNIT_PX
            parts.append(
                f'<line x1="{x:.1f}" y1="{margin*UNIT_PX:.1f}" '
                f'x2="{x:.1f}" y2="{(margin+BODY_H)*UNIT_PX:.1f}"/>'
            )
        parts.append('</g>')

    parts.append(f'<g fill="{fg}">')
    for poly in polys:
        pts = ' '.join(
            f'{(margin + x) * UNIT_PX:.2f},'
            f'{(margin + BODY_H - y) * UNIT_PX:.2f}'   # flip y for SVG
            for x, y in poly
        )
        parts.append(f'<polygon points="{pts}"/>')
    parts.append('</g></svg>')
    return '\n'.join(parts)


CHAR_TO_NAME = {
    ' ': 'space', '.': 'period', ',': 'comma', ':': 'colon',
    ';': 'semicolon', '-': 'hyphen', '_': 'underscore', '/': 'slash',
    '\\': 'backslash', '!': 'exclamation', '?': 'question', '(': 'lparen',
    ')': 'rparen', '[': 'lbracket', ']': 'rbracket', '+': 'plus',
    '=': 'equal', '"': 'quotedbl', "'": 'quotesingle', '#': 'hash',
    '&': 'ampersand', '@': 'at', '·': 'middot', '×': 'multiply',
    '©': 'copyright',
    '$': 'dollar', '%': 'percent', '*': 'asterisk',
    '<': 'less', '>': 'greater', '{': 'lbrace', '}': 'rbrace',
    '|': 'bar', '^': 'caret', '`': 'grave', '~': 'tilde',
    '‘': 'quoteleft', '’': 'quoteright',
    '“': 'quotedblleft', '”': 'quotedblright',
    '–': 'endash', '—': 'emdash', '−': 'minus',
    '…': 'ellipsis', '•': 'bullet',
    '°': 'degree', '±': 'plusminus', '÷': 'divide',
    '≤': 'lessequal', '≥': 'greaterequal', '≠': 'notequal',
    '≈': 'approx', '¹': 'onesuperior', '²': 'twosuperior',
    '³': 'threesuperior', 'µ': 'mu', 'π': 'pi',
    '′': 'prime', '″': 'dblprime',
    '®': 'registered', '™': 'trademark',
    '€': 'euro', '£': 'sterling',
    '¿': 'questiondown', '¡': 'exclamdown', '§': 'section',
    '←': 'arrowleft', '→': 'arrowright',
    '↑': 'arrowup', '↓': 'arrowdown',
    'á': 'aacute', 'é': 'eacute', 'í': 'iacute', 'ó': 'oacute', 'ú': 'uacute',
    'à': 'agrave', 'è': 'egrave', 'ù': 'ugrave',
    'ä': 'adieresis', 'ë': 'edieresis', 'ï': 'idieresis',
    'ö': 'odieresis', 'ü': 'udieresis',
    'ñ': 'ntilde', 'ç': 'ccedilla',
    'Á': 'Aacute', 'É': 'Eacute', 'Í': 'Iacute', 'Ó': 'Oacute', 'Ú': 'Uacute',
    'Ä': 'Adieresis', 'Ö': 'Odieresis', 'Ü': 'Udieresis', 'Ñ': 'Ntilde',
    'ß': 'germandbls', 'æ': 'ae', 'œ': 'oe', 'Æ': 'AE', 'Œ': 'OE',
    '∞': 'infinity', '√': 'radical', '∑': 'summation', '∏': 'product',
    '∂': 'partialdiff', '½': 'onehalf', '¼': 'onequarter', '¾': 'threequarters',
}


def safe_name(char):
    return CHAR_TO_NAME.get(char, char if char.isalnum() else f'u{ord(char):04X}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('chars', nargs='*', help='specific characters to export')
    ap.add_argument('--all', action='store_true', help='export every glyph')
    ap.add_argument('--weight', default='regular',
                    help=f'one of {",".join(WEIGHTS)} (default regular)')
    ap.add_argument('--weights', help='comma-separated list, or "all"')
    ap.add_argument('--grid', action='store_true', help='draw 7x7 grid overlay')
    args = ap.parse_args()

    if args.weights == 'all':
        weights = list(WEIGHTS)
    elif args.weights:
        weights = args.weights.split(',')
    else:
        weights = [args.weight]

    chars = args.chars
    if args.all:
        chars = [c for c in GLYPHS if c != ' ']

    if not chars:
        ap.error('pass one or more characters, or --all')

    # Output sits in the repo's top-level `dist/svg/`.
    base = Path(__file__).resolve().parent.parent / 'dist' / 'svg'
    base.mkdir(parents=True, exist_ok=True)

    count = 0
    for weight_name in weights:
        weight_cells = WEIGHTS[weight_name.lower()]
        out_dir = base if len(weights) == 1 else base / weight_name.lower()
        out_dir.mkdir(parents=True, exist_ok=True)
        for ch in chars:
            if ch not in GLYPHS:
                print(f'  skip unknown: {ch!r}')
                continue
            svg = glyph_svg(ch, weight_cells, show_grid=args.grid)
            out_path = out_dir / f'{safe_name(ch)}.svg'
            out_path.write_text(svg)
            count += 1
    print(f'wrote {count} svg(s) under {base}')


if __name__ == '__main__':
    main()
