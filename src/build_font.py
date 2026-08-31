"""Build the MIT Media Lab Font family from centerline glyph sources.

Pipeline overview
-----------------
For every (family, weight) pair the build does roughly:

    glyphs.GLYPHS  ->  centerline strokes
                       (per glyph: list of ('h'|'v', ...) tuples)
                ↓
        stroke_to_contour()      (expands each centerline into a
                                   filled rectangle of thickness w,
                                   extending w/2 at each end so
                                   perpendicular strokes meet flush)
                ↓
        build_tt_glyph()         (draws contours into a TTGlyphPen
                                   ->  glyf table outline)
        build_cff_glyph()        (draws contours into a T2CharStringPen
                                   ->  CFF charstring)
                ↓
        FontBuilder              (assembles the head, hhea, hmtx, name,
                                   OS/2, post, cmap, glyf or CFF tables)
                ↓
        <family>-<weight>.ttf
        <family>-<weight>.otf

Weight is just a number (in cell units) plugged into ``stroke_to_contour``.
The same ``GLYPHS`` source produces all six weights — there are no
separate "Bold" or "Thin" outline sources.

Coordinate convention
---------------------
- 1 cell = 100 font units; UPM = 1000.
- Centerlines are described in *cells*, then multiplied by ``UNIT`` to
  get font units before being handed to the pen.
- Sidebearing is added on the left at outline time and on the right by
  setting the advance width to ``body_width + 2 * sidebearing``.
- The sidebearing is *weight-aware* (see ``build_one``): heavier weights
  get more sidebearing so adjacent strokes keep ≥0.55 cells of clear
  space between letters.

Run from anywhere in the repo:
    python3 src/build_font.py                   # all weights
    python3 src/build_font.py strict bold       # one weight

Output lands in <repo_root>/dist/MITMediaLabFont-{Weight}.{ttf,otf}.
"""

from __future__ import annotations

import importlib
import math
import sys
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

# ---------- font-wide metrics ---------------------------------------------
UNIT = 100         # font units per cell
UPM = 1000         # font UnitsPerEm
CAP_HEIGHT = 700   # 7 cells × 100 units
ASCENDER = 850     # head/hhea ascent — leaves room above the cap-line
DESCENDER = -250   # head/hhea descent — fits the 2-cell descenders
BODY_TOP = CAP_HEIGHT / UNIT       # 7.0 cells — clip above cap
BODY_BOTTOM = DESCENDER / UNIT     # -2.5 cells — clip below descender
SIDEBEARING_CELLS = 1.0   # minimum sidebearing in cells (per-side)
# Tabular figures: all digits share this body width (cells). Narrower digit
# outlines are centered inside the advance via extra left sidebearing.
TABULAR_DIGIT_CELLS = 7
DIGITS = set('0123456789')

# Basic kerning pairs (glyph name pairs → delta in font units). Negative =
# closer. Applied to both TTF and OTF via a format-0 `kern` table.
KERN_PAIRS = {
    ('T', 'A'): -80, ('T', 'a'): -90, ('T', 'e'): -80, ('T', 'o'): -80,
    ('T', 'c'): -70, ('T', 'u'): -60, ('T', 'y'): -70,
    ('V', 'A'): -100, ('V', 'a'): -90, ('V', 'e'): -80, ('V', 'o'): -80,
    ('Y', 'A'): -90, ('Y', 'a'): -80, ('Y', 'e'): -70, ('Y', 'o'): -70,
    ('A', 'V'): -90, ('A', 'T'): -70, ('A', 'Y'): -80, ('A', 'W'): -60,
    ('L', 'T'): -90, ('L', 'V'): -80, ('L', 'Y'): -80,
    ('F', 'A'): -70, ('P', 'A'): -80, ('P', 'a'): -60,
    ('r', 'a'): -40, ('r', 'e'): -40, ('r', 'o'): -40,
}

# Per-style: (stroke weight in cells, OS/2 usWeightClass).
# Weight is the thickness of every stroke in that style, in cell units.
STYLES = {
    'Thin':     (0.35, 100),
    'Light':    (0.6,  300),
    'Regular':  (0.9,  400),
    'Medium':   (1.15, 500),
    'Bold':     (1.4,  700),
    'Black':    (1.8,  900),
}

# Families this script can build. The pipeline supports multiple glyph
# source modules in principle; today we ship a single family.
#     internal_name : (module_name, postscript_family, display_family)
FAMILIES = {
    'strict': ('glyphs', 'MITMediaLabFont', 'MIT Media Lab Font'),
}


# ---------- geometry helpers ---------------------------------------------

def rect_path(x, y, w, h):
    """Return a CCW rectangle as four (x, y) points."""
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def diag_path(x1, y1, x2, y2, t):
    """Return a CCW rectangle of thickness ``t`` along an arbitrary diagonal
    centerline from (x1, y1) to (x2, y2). Endpoints are extended along the
    stroke direction by ``t/2`` so corners join cleanly with perpendicular
    strokes. Not used by the current font (no diagonal strokes), kept for
    legacy support."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length          # unit normal
    ex, ey = dx / length * (t / 2), dy / length * (t / 2)  # axial extension
    half = t / 2.0
    x1e, y1e = x1 - ex, y1 - ey
    x2e, y2e = x2 + ex, y2 + ey
    return [
        (x1e + nx * half, y1e + ny * half),
        (x2e + nx * half, y2e + ny * half),
        (x2e - nx * half, y2e - ny * half),
        (x1e - nx * half, y1e - ny * half),
    ]


def clip_contour(contour, x_min, x_max, y_min, y_max):
    """Clip an axis-aligned rectangle contour to integer cell bounds."""
    xs = [p[0] for p in contour]
    ys = [p[1] for p in contour]
    x0 = max(min(xs), x_min)
    x1 = min(max(xs), x_max)
    y0 = max(min(ys), y_min)
    y1 = min(max(ys), y_max)
    if x1 <= x0 or y1 <= y0:
        return None
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def stroke_to_contour(stroke, weight_cells):
    """Expand a centerline stroke into a filled-rectangle contour.

    Returns a list of four (x, y) corner points in cell units.

    The rectangle's width along the stroke axis is ``(length + weight)``:
    each endpoint is extended outward by ``weight/2`` so two perpendicular
    strokes sharing a corner overlap perfectly with no gap at any weight.
    """
    kind = stroke[0]
    w = weight_cells
    half = w / 2
    if kind == 'h':
        _, y, x1, x2 = stroke
        return rect_path(x1 - half, y - half, (x2 - x1) + w, w)
    if kind == 'v':
        _, x, y1, y2 = stroke
        return rect_path(x - half, y1 - half, w, (y2 - y1) + w)
    if kind == 'd':
        _, x1, y1, x2, y2 = stroke
        return diag_path(x1, y1, x2, y2, w)
    raise ValueError(f'unknown stroke kind: {kind!r}')


def _letter_stroke_scale(weight_cells: float) -> float:
    """Uniform scale so block marks match letter ink height at ``weight_cells``.

    Vertical strokes extend by ``weight/2`` at each end; total ink height is
    ``cap + weight`` cells. Native wordmark blocks are exactly cap-tall.
    """
    return 1.0 + weight_cells / BODY_TOP


def _draw_blocks(pen, blocks, sidebearing, reverse, body_w,
                 uniform_scale=1.0, y_offset_cells=0.0):
    """Draw filled rectangles (brand / group marks).

    ``uniform_scale`` scales every block from the origin (baseline left).
    ``y_offset_cells`` shifts ink vertically — used so the wordmark bbox
    matches letter strokes (``-weight/2`` below baseline).
    """
    body_w = body_w * uniform_scale
    half = -y_offset_cells  # offset is negative; ink grows above cap by this
    y_min = BODY_BOTTOM
    y_max = BODY_TOP * uniform_scale + half + 0.01
    for x, y, bw, bh in blocks:
        x = x * uniform_scale
        y = y * uniform_scale + y_offset_cells
        bw = bw * uniform_scale
        bh = bh * uniform_scale
        contour = rect_path(x, y, bw, bh)
        contour = clip_contour(
            contour, 0.0, float(body_w), y_min, y_max)
        if contour is None:
            continue
        pts = [
            (round((sidebearing + cx) * UNIT), round(cy * UNIT))
            for cx, cy in contour
        ]
        if reverse:
            pts = list(reversed(pts))
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()


def _draw_glyph(pen, glyph, weight_cells, sidebearing, reverse):
    """Draw either fixed blocks or weight-dependent strokes."""
    body_w = glyph['w']
    if glyph.get('blocks'):
        scale = (_letter_stroke_scale(weight_cells)
                 if glyph.get('match_letter_stroke') else 1.0)
        y_off = (-weight_cells / 2.0
                 if glyph.get('match_letter_stroke') else 0.0)
        _draw_blocks(
            pen, glyph['blocks'], sidebearing, reverse, body_w,
            uniform_scale=scale,
            y_offset_cells=y_off,
        )
    else:
        _draw_strokes(
            pen, glyph['s'], weight_cells, sidebearing, reverse, body_w=body_w)


def _draw_strokes(pen, strokes, weight_cells, sidebearing, reverse, body_w=None):
    """Draw every stroke's filled rectangle into the given fontTools pen.

    Each stroke is independently moveTo'd / lineTo'd / closePath'd —
    we don't attempt to merge overlapping rectangles into a single
    contour. The font format handles overlapping contours fine and the
    rasterizer treats them as a single filled region.

    Outlines are snapped to integer font units so scaled text stays
    pixel-aligned.  Stroke outlines are not clipped — corner extensions
    are required for clean joins between perpendicular strokes.

    ``reverse`` controls winding direction: TrueType wants outer contours
    *clockwise*, CFF/PostScript wants them *counter-clockwise*. Our
    rectangles are CCW out of ``rect_path``, so the TTF path reverses.
    """
    for stroke in strokes:
        contour = stroke_to_contour(stroke, weight_cells)
        pts = [
            (round((sidebearing + cx) * UNIT), round(cy * UNIT))
            for cx, cy in contour
        ]
        if reverse:
            pts = list(reversed(pts))
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()


def build_tt_glyph(glyph, weight_cells, sidebearing):
    """Build a single TrueType ``glyf`` outline from a glyph dict."""
    pen = TTGlyphPen(None)
    _draw_glyph(pen, glyph, weight_cells, sidebearing, reverse=True)
    return pen.glyph()


def build_cff_glyph(glyph, weight_cells, sidebearing, width):
    """Build a single CFF/T2 charstring from a glyph dict."""
    pen = T2CharStringPen(width, None)
    _draw_glyph(pen, glyph, weight_cells, sidebearing, reverse=False)
    return pen.getCharString()


def _common_setup(fb, glyph_order, cmap, advances, style_name, weight_class,
                  display_family, ps_family):
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupHorizontalMetrics({n: (advances[n], 0) for n in glyph_order})
    fb.setupHorizontalHeader(ascent=ASCENDER, descent=DESCENDER)
    fb.setupNameTable({
        'copyright': 'Copyright (c) 2026 Nataliya Kosmyna and Eugene Hauptmann. Licensed under CC BY-NC-SA 4.0.',
        'familyName': display_family,
        'styleName': style_name,
        'uniqueFontIdentifier': f'{ps_family}-{style_name}-1.0',
        'fullName': f'{display_family} {style_name}',
        'version': 'Version 1.000',
        'psName': f'{ps_family}-{style_name}',
        'designer': 'Nataliya Kosmyna and Eugene Hauptmann',
        'description': 'A 7x7 grid typeface in the spirit of the MIT Media Lab generative identity. Generated from a single centerline-stroke source.',
        'manufacturer': 'Nataliya Kosmyna and Eugene Hauptmann',
        'licenseDescription': 'CC BY-NC-SA 4.0. See https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode',
        'licenseInfoURL': 'https://creativecommons.org/licenses/by-nc-sa/4.0/',
    })
    fb.setupOS2(
        sTypoAscender=ASCENDER,
        sTypoDescender=DESCENDER,
        usWinAscent=ASCENDER,
        usWinDescent=-DESCENDER,
        sxHeight=500,
        sCapHeight=CAP_HEIGHT,
        achVendID='MLGR',
        usWeightClass=weight_class,
    )
    fb.setupPost()


def _glyph_sidebearing(glyph, default_sb, char=None):
    if glyph.get('square'):
        return 0.0
    sb = default_sb * float(glyph.get('sb_scale', 1.0))
    if 'sb' in glyph:
        sb = float(glyph['sb'])
    # Center tabular digits inside a fixed advance.
    if char in DIGITS:
        pad = (TABULAR_DIGIT_CELLS - glyph['w']) / 2.0
        sb = sb + max(0.0, pad)
    return sb


def _glyph_advance(glyph, default_sb, char=None, weight_cells=0.0):
    if glyph.get('square'):
        return CAP_HEIGHT
    sb = _glyph_sidebearing(glyph, default_sb, char)
    body_w = glyph['w']
    if glyph.get('match_letter_stroke'):
        body_w *= _letter_stroke_scale(weight_cells)
    if char in DIGITS:
        return int((TABULAR_DIGIT_CELLS + 2 * default_sb * float(glyph.get('sb_scale', 1.0))) * UNIT)
    return int((body_w + 2 * sb) * UNIT)


def _add_kern_table(font_path, glyphs_dict):
    """Attach a legacy format-0 kern table for basic pair spacing."""
    from fontTools.ttLib import TTFont, newTable

    font = TTFont(font_path)
    pairs = {}
    for (left, right), value in KERN_PAIRS.items():
        if left not in glyphs_dict or right not in glyphs_dict:
            continue
        ln = f'u{ord(left):04X}'
        rn = f'u{ord(right):04X}'
        if ln in font.getGlyphOrder() and rn in font.getGlyphOrder():
            pairs[(ln, rn)] = value
    if not pairs:
        return
    kern = newTable('kern')
    kern.version = 0
    sub = newTable('kern').__class__  # placeholder — build format 0 below
    from fontTools.ttLib.tables._k_e_r_n import KernTable_format_0
    subtable = KernTable_format_0()
    subtable.coverage = 1  # horizontal
    subtable.version = 0
    subtable.kernTable = pairs
    kern.kernTables = [subtable]
    font['kern'] = kern
    font.save(font_path)
    del sub  # silence unused if any


def _add_kern_table(font_path, glyphs_dict):
    """Attach a legacy format-0 kern table for basic pair spacing."""
    from fontTools.ttLib import TTFont, newTable
    from fontTools.ttLib.tables._k_e_r_n import KernTable_format_0

    font = TTFont(font_path)
    order = set(font.getGlyphOrder())
    pairs = {}
    for (left, right), value in KERN_PAIRS.items():
        if left not in glyphs_dict or right not in glyphs_dict:
            continue
        ln = f'u{ord(left):04X}'
        rn = f'u{ord(right):04X}'
        if ln in order and rn in order:
            pairs[(ln, rn)] = value
    if not pairs:
        return
    subtable = KernTable_format_0()
    subtable.coverage = 1  # horizontal
    subtable.version = 0
    subtable.kernTable = pairs
    kern = newTable('kern')
    kern.version = 0
    kern.kernTables = [subtable]
    font['kern'] = kern
    font.save(font_path)


def build_one(family_key, style_name, glyphs_dict, out_dir):
    weight_cells, weight_class = STYLES[style_name]
    _, ps_family, display_family = FAMILIES[family_key]

    # Weight-aware sidebearing: a stroke at the glyph's body edge extends
    # by w/2 outward. With a fixed 1.0-cell sidebearing the Black weight
    # (w=1.8) leaves only 0.1 cells of clearance, so adjacent letters
    # actually overlap by ~0.8 cells horizontally. Grow the sidebearing
    # so we always keep a minimum visual gap of ~0.55 cells between
    # neighboring strokes regardless of weight.
    sidebearing = max(SIDEBEARING_CELLS, weight_cells / 2 + 0.55)

    char_order = [' '] + [c for c in glyphs_dict if c != ' ']
    glyph_names = ['.notdef'] + [f'u{ord(c):04X}' for c in char_order]
    cmap = {ord(c): name for c, name in zip(char_order, glyph_names[1:])}

    # .notdef — empty box with an X (missing-glyph convention)
    notdef_glyph = {
        'w': 6,
        's': [
            ('h', 0, 0, 6), ('h', 7, 0, 6),
            ('v', 0, 0, 7), ('v', 6, 0, 7),
            ('v', 1, 1, 1), ('v', 2, 2, 2), ('v', 3, 3, 3),
            ('v', 4, 4, 4), ('v', 5, 5, 5),
            ('v', 5, 1, 1), ('v', 4, 2, 2), ('v', 3, 3, 3),
            ('v', 2, 4, 4), ('v', 1, 5, 5),
        ],
    }
    notdef_w = int((6 + 2 * sidebearing) * UNIT)

    advances = {'.notdef': notdef_w}
    glyph_order = ['.notdef']
    glyph_sidebearings = {'.notdef': sidebearing}
    for c, name in zip(char_order, glyph_names[1:]):
        g = glyphs_dict[c]
        sb = _glyph_sidebearing(g, sidebearing, c)
        glyph_sidebearings[name] = sb
        advances[name] = _glyph_advance(g, sidebearing, c, weight_cells)
        glyph_order.append(name)

    # ---- TTF (glyf) ----
    tt_glyphs = {'.notdef': build_tt_glyph(
        notdef_glyph, weight_cells, glyph_sidebearings['.notdef'])}
    for c, name in zip(char_order, glyph_names[1:]):
        tt_glyphs[name] = build_tt_glyph(
            glyphs_dict[c], weight_cells, glyph_sidebearings[name])

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyf(tt_glyphs)
    _common_setup(fb, glyph_order, cmap, advances, style_name, weight_class,
                  display_family, ps_family)
    ttf_path = out_dir / f'{ps_family}-{style_name}.ttf'
    fb.save(ttf_path)
    _add_kern_table(ttf_path, glyphs_dict)

    # ---- OTF (CFF) ----
    cff_charstrings = {'.notdef': build_cff_glyph(
        notdef_glyph, weight_cells, glyph_sidebearings['.notdef'], notdef_w)}
    for c, name in zip(char_order, glyph_names[1:]):
        cff_charstrings[name] = build_cff_glyph(
            glyphs_dict[c], weight_cells, glyph_sidebearings[name],
            advances[name])

    fb2 = FontBuilder(UPM, isTTF=False)
    fb2.setupGlyphOrder(glyph_order)
    fb2.setupCharacterMap(cmap)
    fb2.setupCFF(
        psName=f'{ps_family}-{style_name}',
        fontInfo={
            'FullName': f'{display_family} {style_name}',
            'FamilyName': display_family,
            'Weight': style_name,
            'version': '1.000',
        },
        charStringsDict=cff_charstrings,
        privateDict={},
    )
    _common_setup(fb2, glyph_order, cmap, advances, style_name, weight_class,
                  display_family, ps_family)
    otf_path = out_dir / f'{ps_family}-{style_name}.otf'
    fb2.save(otf_path)
    _add_kern_table(otf_path, glyphs_dict)

    return ttf_path, otf_path


def main():
    # Always emit into the repo's top-level `dist/` regardless of where
    # the script is run from. src/build_font.py lives one level under root.
    out_dir = Path(__file__).resolve().parent.parent / 'dist'
    out_dir.mkdir(exist_ok=True)

    args = sys.argv[1:]
    if args:
        family_keys = [args[0]]
        style_names = [args[1].capitalize()] if len(args) > 1 else list(STYLES)
    else:
        family_keys = list(FAMILIES)
        style_names = list(STYLES)

    for fk in family_keys:
        mod_name, ps_family, _ = FAMILIES[fk]
        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            print(f'skip {fk}: module {mod_name}.py not found')
            continue
        for style in style_names:
            ttf, otf = build_one(fk, style, mod.GLYPHS, out_dir)
            print(f'  {ttf.name}  ({ttf.stat().st_size} bytes)  '
                  f'+ {otf.name}  ({otf.stat().st_size} bytes)  '
                  f'weight={STYLES[style][0]} cells')


if __name__ == '__main__':
    main()
