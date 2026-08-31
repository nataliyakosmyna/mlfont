"""Parse a Media Lab group-glyph SVG and extract just the geometric mark
(throw away the typeset group name) as a list of axis-aligned rectangles
on a 7x7 cell grid.

Usage:  python3 _parse.py biomechatronics
"""
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


def parse_path(d: str):
    """Walk the SVG path and yield each subpath as a list of (x, y) points
    in the order they appear (no curves expected)."""
    tokens = re.findall(r'[MmLlHhVvZz]|-?\d*\.?\d+', d)
    i = 0
    cx = cy = 0.0
    sx = sy = 0.0
    subpath = []
    cmd = None
    while i < len(tokens):
        t = tokens[i]
        if t in 'MmLlHhVvZz':
            cmd = t
            i += 1
            if cmd in 'Zz':
                if subpath:
                    yield subpath
                subpath = []
                cx, cy = sx, sy
                continue
            continue
        if cmd in ('M', 'm'):
            x, y = float(tokens[i]), float(tokens[i+1]); i += 2
            if cmd == 'm' and subpath:
                cx += x; cy += y
            else:
                cx, cy = x, y
            sx, sy = cx, cy
            if subpath:
                yield subpath
            subpath = [(cx, cy)]
            cmd = 'L' if cmd == 'M' else 'l'
        elif cmd in ('L', 'l'):
            x, y = float(tokens[i]), float(tokens[i+1]); i += 2
            if cmd == 'l': cx += x; cy += y
            else: cx, cy = x, y
            subpath.append((cx, cy))
        elif cmd in ('H', 'h'):
            x = float(tokens[i]); i += 1
            cx = cx + x if cmd == 'h' else x
            subpath.append((cx, cy))
        elif cmd in ('V', 'v'):
            y = float(tokens[i]); i += 1
            cy = cy + y if cmd == 'v' else y
            subpath.append((cx, cy))
    if subpath:
        yield subpath


def is_glyph_subpath(pts, viewbox_w=160, viewbox_h=55):
    """Filter: keep subpaths whose bounding box lies in the leftmost 50px
    (the glyph area). The text labels live to the right of x≈55."""
    xs = [p[0] for p in pts]
    return max(xs) <= 50.5


def cells_from_path(pts, cell=50/7):
    """Walk a rectilinear subpath and report the cell-grid rectangle list.
    Each subpath in the source is an outer or inner contour of a polygon;
    rather than reconstruct polygons, just print the bounding box and the
    raw cell-aligned coordinates so a human can interpret."""
    xs = [round(p[0] / cell, 3) for p in pts]
    ys = [round(p[1] / cell, 3) for p in pts]
    return list(zip(xs, ys))


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else 'biomechatronics'
    svg_path = Path(__file__).parent / f'{name}.svg'
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {'s': 'http://www.w3.org/2000/svg'}
    paths = root.findall('.//s:path', ns) or root.findall('.//path')

    cell = 50 / 7  # the glyph occupies a 50x50 box on a 7x7 grid
    print(f'cell = {cell:.4f}, glyph in cols 0..7 (x=0..50), rows 0..7 (y=0..50)')

    for path in paths:
        d = path.get('d', '')
        subpaths = list(parse_path(d))
        glyph_subs = [s for s in subpaths if is_glyph_subpath(s)]
        print(f'{len(subpaths)} subpaths total, {len(glyph_subs)} in glyph area')
        for k, sub in enumerate(glyph_subs):
            cells = cells_from_path(sub)
            xs = [p[0] for p in cells]
            ys = [p[1] for p in cells]
            print(f'  subpath {k}: bbox cells x={min(xs):.2f}..{max(xs):.2f}'
                  f' y={min(ys):.2f}..{max(ys):.2f}  ({len(cells)} points)')
            for px, py in cells:
                print(f'    ({px:.2f}, {py:.2f})')


if __name__ == '__main__':
    main()
