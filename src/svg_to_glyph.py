"""Convert Media Lab group-glyph reference SVGs to centerline stroke definitions.

Each reference SVG (``reference_glyphs/{slug}.svg``) is a 160×55 lockup:
a rectilinear 7×7 mark in the left 50 px plus a typeset group name on
the right.  Only the square mark is exported as a font glyph.

Usage:
    python3 src/svg_to_glyph.py          # print icon glyphs
    python3 src/svg_to_glyph.py --write  # regenerate group_glyphs.py
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import xml.etree.ElementTree as ET

try:
    import cairosvg
    from PIL import Image
except ImportError as exc:
    cairosvg = None  # type: ignore
    Image = None  # type: ignore
    _IMPORT_ERR = exc
else:
    _IMPORT_ERR = None

CELL = 50 / 7  # SVG units per grid cell
GRID = 7
GLYPH_PX = 50          # icon square width in reference SVG units

GROUPS = [
    'affective-computing',
    'biomechatronics',
    'camera-culture',
    'center-for-constructive-communication',
    'city-science',
    'conformable-decoders',
    'critical-matter',
    'cyborg-psychology',
    'fluid-interfaces',
    'future-sketches',
    'human-dynamics',
    'lifelong-kindergarten',
    'molecular-machines',
    'multisensory-intelligence',
    'nano-cybernetic-biotrek',
    'opera-of-the-future',
    'personal-robots',
    'responsive-environments',
    'sculpting-evolution',
    'signal-kinetics',
    'social-algorithms',
    'space-enabled',
    'tangible-media',
    'viral-communications',
]

# Private Use Area — one codepoint per research group, in GROUPS order.
GROUP_CODEPOINTS = [0xE000 + i for i in range(len(GROUPS))]


def parse_path(d: str):
    """Yield subpaths as lists of (x, y) vertices (SVG coordinates)."""
    tokens = re.findall(r'[MmLlHhVvZz]|-?\d*\.?\d+(?:[eE][+-]?\d+)?', d)
    i = 0
    cx = cy = 0.0
    sx = sy = 0.0
    subpath: list[tuple[float, float]] = []
    cmd: str | None = None

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
        if cmd is None:
            i += 1
            continue

        if cmd in ('M', 'm'):
            x, y = float(tokens[i]), float(tokens[i + 1])
            i += 2
            if cmd == 'm' and subpath:
                cx += x
                cy += y
            else:
                cx, cy = x, y
            sx, sy = cx, cy
            if subpath:
                yield subpath
            subpath = [(cx, cy)]
            cmd = 'L' if cmd == 'M' else 'l'
        elif cmd in ('L', 'l'):
            x, y = float(tokens[i]), float(tokens[i + 1])
            i += 2
            if cmd == 'l':
                cx += x
                cy += y
            else:
                cx, cy = x, y
            subpath.append((cx, cy))
        elif cmd in ('H', 'h'):
            x = float(tokens[i])
            i += 1
            cx = cx + x if cmd == 'h' else x
            subpath.append((cx, cy))
        elif cmd in ('V', 'v'):
            y = float(tokens[i])
            i += 1
            cy = cy + y if cmd == 'v' else y
            subpath.append((cx, cy))

    if subpath:
        yield subpath


def parse_viewbox(root) -> tuple[float, float, float, float]:
    """Return viewBox as (min_x, min_y, width, height)."""
    raw = root.get('viewBox') or root.get('viewbox') or '0 0 160 55'
    parts = [float(v) for v in re.split(r'[,\s]+', raw.strip()) if v]
    if len(parts) != 4:
        return 0.0, 0.0, 160.0, 55.0
    return parts[0], parts[1], parts[2], parts[3]


def normalize_subpath(
    pts: list[tuple[float, float]],
    vbx: float,
    vby: float,
) -> list[tuple[float, float]]:
    """Shift SVG coordinates into the local 160×55 glyph viewBox."""
    return [(x - vbx, y - vby) for x, y in pts]


def _snap(v: float) -> float:
    return round(v / CELL) * CELL


def _snap_subpath(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    return [(_snap(x), _snap(y)) for x, y in pts]


def _is_rectilinear(pts: list[tuple[float, float]], tol: float = 0.15) -> bool:
    """True when every edge is axis-aligned (no curves / diagonals)."""
    if len(pts) < 3:
        return False
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        if abs(x1 - x2) > tol and abs(y1 - y2) > tol:
            return False
    return True


def _fits_glyph_square(pts, max_x: float = GLYPH_PX + 0.5) -> bool:
    if not pts:
        return False
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (
        min(xs) >= -0.5
        and min(ys) >= -0.5
        and max(xs) <= max_x
        and max(ys) <= GLYPH_PX + 0.5
    )


def extract_glyph_subpaths(
    paths: list,
    vbx: float,
    vby: float,
) -> list[list[tuple[float, float]]]:
    """Pull 7×7 mark subpaths from reference lockup SVG path data."""
    snapped: list[list[tuple[float, float]]] = []
    for path in paths:
        if path.get('display') == 'none':
            continue
        for sub in parse_path(path.get('d', '')):
            local = normalize_subpath(sub, vbx, vby)
            if not _is_rectilinear(local):
                continue
            snapped.append(_snap_subpath(local))

    if not snapped:
        return []

    in_place = [s for s in snapped if _fits_glyph_square(s)]
    if in_place:
        return in_place

    # Some references (e.g. city-science) embed the mark at a large offset.
    small = [
        s for s in snapped
        if (max(p[0] for p in s) - min(p[0] for p in s) <= GLYPH_PX + CELL
            and max(p[1] for p in s) - min(p[1] for p in s) <= GLYPH_PX + CELL)
    ]
    if not small:
        return []

    ox = _snap(min(min(p[0] for p in s) for s in small))
    oy = _snap(min(min(p[1] for p in s) for s in small))
    shifted = [
        [(x - ox, y - oy) for x, y in s]
        for s in small
    ]
    return [s for s in shifted if _fits_glyph_square(s)]


def is_glyph_subpath(pts, max_x: float = GLYPH_PX + 0.5) -> bool:
    """Keep rectilinear mark subpaths in the left 50 px — not label outlines."""
    return _is_rectilinear(pts) and _fits_glyph_square(pts, max_x)


def point_in_polygon(x: float, y: float, polygon: list[tuple[float, float]]) -> bool:
    """Ray-casting point-in-polygon test."""
    inside = False
    n = len(polygon)
    if n < 3:
        return False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi
        ):
            inside = not inside
        j = i
    return inside


def rasterize_subpaths(subpaths: list[list[tuple[float, float]]]) -> list[list[bool]]:
    """Fill a 7×7 grid. Font row 0 = baseline, row 6 = cap-height."""
    grid = [[False] * GRID for _ in range(GRID)]
    for cy in range(GRID):
        for cx in range(GRID):
            # Cell center in SVG coords (y-down).
            sx = (cx + 0.5) * CELL
            sy = (GRID - cy - 0.5) * CELL
            winding = 0
            for poly in subpaths:
                if len(poly) < 3:
                    continue
                if point_in_polygon(sx, sy, poly):
                    winding += 1
            grid[cy][cx] = (winding % 2) == 1
    return grid


def _merge_runs(cells: list[bool]):
    """Yield (start, end) index pairs for contiguous True runs."""
    i = 0
    n = len(cells)
    while i < n:
        if not cells[i]:
            i += 1
            continue
        start = i
        while i < n and cells[i]:
            i += 1
        yield start, i


def grid_to_blocks(grid: list[list[bool]]) -> list[tuple]:
    """Convert a filled bitmap to solid horizontal blocks (one per row run).

    Same filled-rectangle model as the MIT wordmark — weight-independent,
    no stroke-expansion gaps.
    """
    rows = len(grid)
    blocks: list[tuple] = []
    for cy in range(rows):
        for x0, x1 in _merge_runs(grid[cy]):
            blocks.append((x0, cy, x1 - x0, 1))
    return blocks


def blocks_to_grid(
    blocks: list[tuple], rows: int, cols: int,
) -> list[list[bool]]:
    grid = [[False] * cols for _ in range(rows)]
    for x, y, w, h in blocks:
        for dy in range(int(h)):
            for dx in range(int(w)):
                cy = int(y) + dy
                cx = int(x) + dx
                if 0 <= cy < rows and 0 <= cx < cols:
                    grid[cy][cx] = True
    return grid


def downsample_grid(
    grid: list[list[bool]], row_factor: int = 2, col_factor: int = 2,
) -> list[list[bool]]:
    """Merge ``row_factor × col_factor`` cells (OR) into one output cell."""
    in_rows = len(grid)
    in_cols = len(grid[0]) if in_rows else 0
    out_rows = in_rows // row_factor
    out_cols = in_cols // col_factor
    out = [[False] * out_cols for _ in range(out_rows)]
    for cy in range(out_rows):
        for cx in range(out_cols):
            filled = False
            for dy in range(row_factor):
                for dx in range(col_factor):
                    iy = cy * row_factor + dy
                    ix = cx * col_factor + dx
                    if iy < in_rows and ix < in_cols and grid[iy][ix]:
                        filled = True
                        break
                if filled:
                    break
            out[cy][cx] = filled
    return out


def dilate_grid(grid: list[list[bool]], radius: int = 1) -> list[list[bool]]:
    """Expand filled cells by ``radius`` for bolder, more readable text."""
    if radius <= 0:
        return grid
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    out = [row[:] for row in grid]
    for cy in range(rows):
        for cx in range(cols):
            if grid[cy][cx]:
                continue
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx]:
                        out[cy][cx] = True
                        break
                if out[cy][cx]:
                    break
    return out


def grid_to_strokes(grid: list[list[bool]]) -> list[tuple]:
    """Convert a filled bitmap to overlapping bar strokes on integer grid lines.

    Per-cell dot strokes leave ~0.1-cell gaps at Regular weight (0.9), which
    show as hairlines when glyphs are scaled up.  Horizontal and vertical runs
    use paired strokes on adjacent grid lines so neighboring cells merge into
    solid fills.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    strokes: list[tuple] = []

    for cy in range(rows):
        for x0, x1 in _merge_runs(grid[cy]):
            strokes.append(('h', cy, x0, x1))
            strokes.append(('h', cy + 1, x0, x1))

    for cx in range(cols):
        col = [grid[ry][cx] for ry in range(rows)]
        for y0, y1 in _merge_runs(col):
            strokes.append(('v', cx, y0, y1))
            strokes.append(('v', cx + 1, y0, y1))

    return list(dict.fromkeys(strokes))


def _offset_strokes(strokes: list[tuple], dx: float) -> list[tuple]:
    out: list[tuple] = []
    for stroke in strokes:
        kind = stroke[0]
        if kind == 'h':
            _, y, x1, x2 = stroke
            out.append(('h', y, x1 + dx, x2 + dx))
        elif kind == 'v':
            _, x, y1, y2 = stroke
            out.append(('v', x + dx, y1, y2))
        else:
            out.append(stroke)
    return out


def body_width_blocks(blocks: list[tuple], min_w: int = GRID) -> int | float:
    if not blocks:
        return min_w
    return max(min_w, max(x + w for x, _y, w, _h in blocks))


def _offset_blocks(blocks: list[tuple], dx: float) -> list[tuple]:
    return [(x + dx, y, w, h) for x, y, w, h in blocks]


def body_width(strokes: list[tuple], min_w: int = GRID) -> int:
    """Return glyph width in grid cells.

    Bar strokes sit on integer grid lines; line *n* is the right/bottom edge of
    cell *n − 1*, so the extent is ``max(x2)`` for horizontal runs and ``max(x)``
    for verticals — not ``x + 1`` on verticals (that wrongly adds a column).
    """
    max_extent = 0
    for kind, *rest in strokes:
        if kind == 'h':
            _, x1, x2 = rest
            max_extent = max(max_extent, x2)
        elif kind == 'v':
            x, y1, y2 = rest
            max_extent = max(max_extent, x)
    if not strokes:
        return min_w
    return max(min_w, max_extent)


def parse_viewbox_from_svg(svg_text: str) -> tuple[float, float, float, float]:
    m = re.search(r'viewBox=["\']([^"\']+)["\']', svg_text)
    if not m:
        return 0.0, 0.0, 160.0, 55.0
    parts = [float(v) for v in re.split(r'[,\s]+', m.group(1).strip()) if v]
    if len(parts) != 4:
        return 0.0, 0.0, 160.0, 55.0
    return parts[0], parts[1], parts[2], parts[3]


def svg_raster_to_glyph(
    svg_path: Path | None = None,
    *,
    svg_text: str | None = None,
    rows: int = GRID,
    cols: int | None = None,
    px_per_cell: int = 32,
    dark_ratio: float = 0.35,
) -> dict:
    """Rasterize an arbitrary SVG (including curved text) onto the font grid."""
    if cairosvg is None or Image is None:
        raise RuntimeError(
            'svg_raster_to_glyph requires cairosvg and Pillow; '
            f'missing dependency: {_IMPORT_ERR}'
        )

    if svg_text is None:
        if svg_path is None:
            raise ValueError('svg_path or svg_text required')
        svg_text = svg_path.read_text()
    _, _, vb_w, vb_h = parse_viewbox_from_svg(svg_text)
    if cols is None:
        cols = max(rows, int(round(vb_w / vb_h * rows)))

    width_px = cols * px_per_cell
    height_px = rows * px_per_cell
    png = cairosvg.svg2png(
        bytestring=svg_text.encode('utf-8'),
        output_width=width_px,
        output_height=height_px,
        background_color='white',
    )
    im = Image.open(io.BytesIO(png)).convert('L')

    grid = [[False] * cols for _ in range(rows)]
    for cy in range(rows):
        for cx in range(cols):
            x0 = cx * px_per_cell
            x1 = min((cx + 1) * px_per_cell, width_px)
            y0_img = height_px - (cy + 1) * px_per_cell
            y1_img = height_px - cy * px_per_cell
            y0_img = max(y0_img, 0)
            dark = 0
            total = 0
            for py in range(y0_img, y1_img):
                for px in range(x0, x1):
                    if im.getpixel((px, py)) < 128:
                        dark += 1
                    total += 1
            grid[cy][cx] = total > 0 and dark / total >= dark_ratio

    # Trim empty right columns (lockups only).
    while cols > rows and not any(grid[cy][cols - 1] for cy in range(rows)):
        cols -= 1
        for row in grid:
            del row[-1]

    blocks = grid_to_blocks(grid)
    return {'w': body_width_blocks(blocks, min_w=cols), 'blocks': blocks}


# Hand-authored when the published SVG ships text labels only (FAY identity).
MANUAL_GLYPHS: dict[str, dict] = {
    'center-for-constructive-communication': {
        'w': 7,
        's': [
            # Top C (opens downward)
            ('v', 2, 4, 7), ('v', 5, 4, 7), ('h', 7, 2, 5),
            # Bottom-left C (opens east)
            ('v', 0, 0, 3), ('v', 3, 0, 2),
            ('h', 3, 0, 3), ('h', 0, 0, 3), ('h', 1, 0, 3),
            # Bottom-right C (opens west)
            ('v', 4, 0, 3), ('v', 7, 0, 3),
            ('h', 3, 4, 7), ('h', 0, 4, 7),
        ],
    },
}


def _strokes_to_blocks(
    strokes: list[tuple], rows: int, cols: int, weight: float = 1.0,
) -> list[tuple]:
    """Rasterize centerline strokes to solid blocks (for manual overrides)."""
    import math
    from build_font import stroke_to_contour

    grid = [[False] * cols for _ in range(rows)]
    for stroke in strokes:
        contour = stroke_to_contour(stroke, weight)
        xs = [p[0] for p in contour]
        ys = [p[1] for p in contour]
        x0 = max(0, int(math.floor(min(xs))))
        x1 = min(cols, int(math.ceil(max(xs))))
        y0 = max(0, int(math.floor(min(ys))))
        y1 = min(rows, int(math.ceil(max(ys))))
        for cy in range(y0, y1):
            for cx in range(x0, x1):
                grid[cy][cx] = True
    return grid_to_blocks(grid)


def _glyph_blocks(glyph: dict, rows: int = GRID, cols: int = GRID,
                    dx: float = 0, weight: float = 1.0) -> list[tuple]:
    if glyph.get('blocks'):
        blocks = glyph['blocks']
    elif glyph.get('s'):
        blocks = _strokes_to_blocks(glyph['s'], rows, cols, weight=weight)
    else:
        return []
    return _offset_blocks(blocks, dx) if dx else list(blocks)


def svg_to_glyph(svg_path: Path, slug: str | None = None) -> dict:
    if slug and slug in MANUAL_GLYPHS:
        manual = MANUAL_GLYPHS[slug]
        if manual.get('blocks'):
            return manual
        blocks = _strokes_to_blocks(manual['s'], GRID, GRID)
        return {'w': manual['w'], 'blocks': blocks, 'square': True}

    tree = ET.parse(svg_path)
    root = tree.getroot()
    vbx, vby, _, _ = parse_viewbox(root)
    ns = {'s': 'http://www.w3.org/2000/svg'}
    paths = root.findall('.//s:path', ns) or root.findall('.//path')

    glyph_subs = extract_glyph_subpaths(paths, vbx, vby)

    if not glyph_subs:
        raise ValueError(f'no glyph geometry in {svg_path.name}')

    grid = rasterize_subpaths(glyph_subs)
    blocks = grid_to_blocks(grid)
    glyph = {'w': body_width_blocks(blocks, min_w=GRID), 'blocks': blocks, 'square': True}
    return glyph


def format_glyph(char: str, slug: str, glyph: dict) -> str:
    cp = ord(char)
    lines = [f"    # {slug} — U+{cp:04X}"]
    parts = [f"'w': {glyph['w']}"]
    if glyph.get('square'):
        parts.append("'square': True")
    head = ', '.join(parts)
    if glyph.get('blocks'):
        lines.append(f"    {char!r}: {{{head}, 'blocks': [")
        for block in glyph['blocks']:
            lines.append(f"        {block!r},")
    else:
        lines.append(f"    {char!r}: {{{head}, 's': [")
        for stroke in glyph['s']:
            lines.append(f"        {stroke!r},")
    lines.append('    ]},')
    return '\n'.join(lines)


def generate_module(ref_dir: Path) -> str:
    parts = [
        '"""MIT Media Lab research group symbols (Private Use Area).',
        '',
        'Icons parsed from the 7×7 mark in ``reference_glyphs/{slug}.svg``.',
        'Regenerate with ``python3 src/svg_to_glyph.py --write``.',
        '"""',
        '',
        'GROUP_SLUGS = [',
    ]
    for slug in GROUPS:
        parts.append(f"    {slug!r},")
    parts.append(']')
    parts.append('')
    parts.append('GROUP_GLYPHS = {')

    for slug, cp in zip(GROUPS, GROUP_CODEPOINTS):
        char = chr(cp)
        ref_path = ref_dir / f'{slug}.svg'
        if not ref_path.exists():
            raise FileNotFoundError(f'missing {ref_path}')
        glyph = svg_to_glyph(ref_path, slug=slug)
        parts.append(format_glyph(char, slug, glyph))

    parts.append('}')
    parts.append('')
    return '\n'.join(parts)


def main():
    ref_dir = Path(__file__).resolve().parent.parent / 'reference_glyphs'
    write = '--write' in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith('-')]

    if write:
        out = Path(__file__).resolve().parent / 'group_glyphs.py'
        out.write_text(generate_module(ref_dir))
        print(f'wrote {out}')
        return

    targets = names or GROUPS
    for slug in targets:
        glyph = svg_to_glyph(ref_dir / f'{slug}.svg', slug=slug)
        cp = GROUP_CODEPOINTS[GROUPS.index(slug)]
        key = 'blocks' if glyph.get('blocks') else 's'
        print(f'# {slug} U+{cp:04X}  w={glyph["w"]}  {key}={len(glyph[key])}')
        print(format_glyph(chr(cp), slug, glyph))
        print()


if __name__ == '__main__':
    main()
