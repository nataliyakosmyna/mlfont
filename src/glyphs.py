"""
MIT Media Lab Font — glyph sources (centerline form, weight-agnostic).

This module is the *single source of truth* for every glyph in the font.
Each glyph is described as a list of axis-aligned strokes; ``build_font.py``
reads the same source six times (once per weight) to produce all the
TTF + OTF outlines, and ``render_glyph_svg.py`` reads it to export
standalone glyph SVGs. There is no separate "outline" or "vector" source.

Coordinate system
-----------------
- One cell == 100 font units; UPM is 1000.
- Origin (0, 0) is the baseline at the left edge of the glyph body.
- ``y`` grows upward (typographic convention, not screen convention).
- Cap-height is 7 cells (y = 7). Lowercase x-height is 5 cells (y = 5).
- Ascenders rise to y = 7. Descenders drop to y = -2.

Stroke kinds
------------
Each entry in ``GLYPHS[char]['s']`` is a tuple describing one centerline
stroke. There are only two kinds:

    ('h', y, x1, x2)    horizontal centerline at y from x1 to x2
    ('v', x, y1, y2)    vertical   centerline at x from y1 to y2

A zero-length stroke (``y1 == y2`` or ``x1 == x2``) renders as a single
``w × w`` square at that point — that's how dots (``.``, ``i``-tittle,
etc.) and pixel-grid staircase cells are defined.

Stroke geometry
---------------
At build time, each centerline is expanded into a filled rectangle of
thickness ``w`` (the per-weight stroke weight, in cell units). The
rectangle is *extended* by ``w/2`` along the stroke axis at each end so
that two perpendicular strokes meet flush at corners with no gap. See
``build_font.stroke_to_contour`` for the math.

Design rules
------------
- Only horizontal and vertical strokes. No diagonals, no curves.
- "Diagonal" letters (A, K, M, N, V, W, X, Y, Z, and their lowercase
  forms plus 7) are approximated by single-cell staircase strokes.
- All centerlines sit on **integer** cell positions. Sub-cell positions
  cause strokes to look 1 pixel offset relative to integer-aligned
  strokes in neighboring letters.
- Per-glyph body width is set on each entry (``'w'``). The build script
  adds a weight-aware sidebearing.
- Heavy letters whose "natural" centerline is at a half cell (T, Y, 0,
  +, =, #, B's middle bar...) use even widths so the centerline lands on
  an integer column.

Layout of the GLYPHS dict
-------------------------
``GLYPHS[char] = {'w': <body_width_in_cells>, 's': [stroke, ...]}``

Order in the file:
    1. Space
    2. Uppercase A..Z
    3. Numerals 0..9
    4. Punctuation
    5. Lowercase a..z (at the bottom, marked by a banner comment)
    6. Research group symbols — square icons (PUA U+E000–U+E017)
    7. Brand symbols — MIT wordmark U+E030, Media Lab mark U+E031

Grid ``M``, ``I``, and ``T`` follow the 2023 MIT parent-brand logo
(``reference_glyphs/MIT_logo_2023.svg``, Matthew Carter). The PUA MIT
glyph (U+E030) is the full wordmark, not the single letter ``M``.
"""

GLYPHS = {
    ' ': {'w': 4, 's': []},

    # A — two full-height stems closed at top, with a full-width crossbar
    # at mid-height. Simple block A; no apex notch (the notch read as a
    # split letter at small sizes).
    'A': {'w': 6, 'sb_scale': 0.85, 's': [
        ('v', 0, 0, 7),       # left stem
        ('v', 6, 0, 7),       # right stem
        ('h', 7, 0, 6),       # top bar
        ('h', 4, 0, 6),       # crossbar
    ]},
    # B — perimeter rectangle with a middle bar that stops one cell short
    # of the right edge, creating the open horseshoe negative space of the
    # biomechatronics reference. Symmetric upper and lower bowls.
    # B — integer-aligned middle bar at y=4 (was y=3.5). Bowls are very
    # slightly asymmetric (upper 3 cells tall, lower 4 cells tall) which
    # matches how most B's are drawn anyway and removes the sub-cell
    # offset where the middle bar met the right edge.
    'B': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('h', 7, 0, 6),
        ('h', 0, 0, 6),
        ('h', 4, 0, 6),
        ('v', 6, 4, 7),
        ('v', 6, 0, 4),
    ]},
    'C': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('h', 7, 0, 7),
        ('h', 0, 0, 7),
    ]},
    # D — closed body with a single-pixel notch at the top-right and
    # bottom-right corners. Top and bottom bars stop one cell short of
    # the right edge; the right wall sits inset 1 row from top and bottom.
    'D': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('h', 7, 0, 6),
        ('h', 0, 0, 6),
        ('v', 7, 1, 6),
    ]},
    'E': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('h', 7, 0, 7),
        ('h', 4, 0, 6),
        ('h', 0, 0, 7),
    ]},
    'F': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('h', 7, 0, 7),
        ('h', 4, 0, 6),
    ]},
    'G': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('h', 7, 0, 7),
        ('h', 0, 0, 7),
        ('v', 7, 0, 4),
        ('h', 4, 3, 7),
    ]},
    'H': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('v', 7, 0, 7),
        ('h', 4, 0, 7),
    ]},
    # I — cap-height letter with top and bottom bars.
    'I': {'w': 2, 's': [
        ('v', 1, 0, 7),
        ('h', 7, 0, 2),
        ('h', 0, 0, 2),
    ]},
    # J — full-height right stem connected via the baseline bar to a
    # short left wall, forming a closed hook with no gap at the corner.
    'J': {'w': 6, 's': [
        ('v', 6, 0, 7),       # right stem (extends to baseline)
        ('h', 0, 0, 6),       # bottom bar
        ('v', 0, 0, 2),       # short left wall of the hook
    ]},
    # K — stem on left + two single-cell diagonal staircase arms diverging
    # from mid-stem out to the top-right and bottom-right corners. Pure
    # H/V grid can't draw a true diagonal, so the cells double up at
    # heavier weights to form solid arms; at thin weights they read as
    # dots, which is honest to the pixel-grid aesthetic.
    'K': {'w': 5, 's': [
        ('v', 0, 0, 7),
        ('v', 1, 3, 4),
        ('v', 2, 5, 5), ('v', 3, 6, 6), ('v', 4, 7, 7),
        ('v', 2, 2, 2), ('v', 3, 1, 1), ('v', 4, 0, 0),
    ]},
    'L': {'w': 6, 'sb_scale': 0.9, 's': [
        ('v', 0, 0, 7),
        ('h', 0, 0, 6),
    ]},
    # M — three pillars (2023 MIT wordmark): outer stems full height,
    # middle stem raised ~1.5 cells above the baseline.
    'M': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('v', 6, 0, 7),
        ('v', 3, 2, 7),
    ]},
    # N — two full-height pillars connected by a single-cell diagonal
    # staircase from the top-left to the bottom-right. Reads as N, not
    # as Π-with-extra-stem (which is what the old design read as, and
    # also what the old M used to look like).
    'N': {'w': 6, 's': [
        ('v', 0, 0, 7),
        ('v', 6, 0, 7),
        ('v', 1, 6, 6), ('v', 2, 5, 5), ('v', 3, 4, 4),
        ('v', 4, 3, 3), ('v', 5, 2, 2),
    ]},
    'O': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('v', 7, 0, 7),
        ('h', 7, 0, 7),
        ('h', 0, 0, 7),
    ]},
    'P': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('h', 7, 0, 6),
        ('h', 3, 0, 6),
        ('v', 6, 3, 7),
    ]},
    # Q — O with a small notched tail at the bottom-right corner.
    'Q': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('v', 7, 0, 7),
        ('h', 7, 0, 7),
        ('h', 0, 0, 5),
        ('v', 5, 0, 2),
        ('h', 2, 5, 7),
    ]},
    # R — P with a stepped leg that sits inboard of the bowl edge so it
    # reads as a leg, not as a continuation of the right edge (which would
    # make R look like D or B).
    # R — stem + closed bowl in the upper half + straight leg dropping to
    # the baseline from the bowl's bottom corner. The middle bar extends
    # one cell past the bowl to anchor the leg cleanly.
    'R': {'w': 5, 's': [
        ('v', 0, 0, 7),     # stem
        ('h', 7, 0, 4),     # top of bowl
        ('v', 4, 4, 7),     # bowl right vertical
        ('h', 4, 0, 5),     # middle bar (extends to leg)
        ('v', 5, 0, 4),     # leg
    ]},
    'S': {'w': 7, 's': [
        ('h', 7, 0, 7),
        ('v', 0, 3, 7),
        ('h', 3, 0, 7),
        ('v', 7, 0, 3),
        ('h', 0, 0, 7),
    ]},
    # T — symmetric cap-height letter (full-width bar, centered stem).
    'T': {'w': 5, 'sb_scale': 0.75, 's': [
        ('h', 7, 0, 5),
        ('v', 2, 0, 7),
    ]},
    'U': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('v', 7, 0, 7),
        ('h', 0, 0, 7),
    ]},
    # V — two-step staircase chevron narrowing to a single-cell apex at
    # the baseline. Tall pillars at the corners step inward, meeting at
    # the bottom-center.
    'V': {'w': 6, 'sb_scale': 0.75, 's': [
        ('v', 0, 5, 7),       # left outer (3 cells)
        ('v', 6, 5, 7),       # right outer (3 cells)
        ('v', 1, 3, 4),       # left step 1 (2 cells)
        ('v', 5, 3, 4),       # right step 1 (2 cells)
        ('v', 2, 2, 2),       # left step 2 (1 cell)
        ('v', 4, 2, 2),       # right step 2 (1 cell)
        ('v', 3, 0, 1),       # apex (2 cells at the baseline)
    ]},
    # W — inverted M.
    'W': {'w': 6, 's': [
        ('v', 0, 0, 7),
        ('v', 3, 1, 7),
        ('v', 6, 0, 7),
        ('h', 1, 0, 6),
    ]},
    # X — two diagonal staircases of single cells crossing at center.
    'X': {'w': 6, 's': [
        ('v', 0, 0, 0), ('v', 1, 1, 1), ('v', 2, 2, 2),
        ('v', 6, 0, 0), ('v', 5, 1, 1), ('v', 4, 2, 2),
        ('v', 0, 7, 7), ('v', 1, 6, 6), ('v', 2, 5, 5),
        ('v', 6, 7, 7), ('v', 5, 6, 6), ('v', 4, 5, 5),
        ('v', 3, 3, 4),
    ]},
    # Y — single stem with wide top fork.
    # Y — width 6, stem at x=3 (integer aligned, was 3.5).
    'Y': {'w': 6, 'sb_scale': 0.75, 's': [
        ('v', 3, 0, 4),
        ('v', 0, 4, 7),
        ('v', 6, 4, 7),
        ('h', 4, 0, 6),
    ]},
    # Z — top bar, single-cell diagonal staircase from top-right to
    # bottom-left, bottom bar. Reads as Z (not S) because the path is
    # a clean diagonal, not an S-curve.
    'Z': {'w': 6, 's': [
        ('h', 7, 0, 6),
        ('v', 6, 6, 6), ('v', 5, 5, 5), ('v', 4, 4, 4),
        ('v', 3, 3, 3), ('v', 2, 2, 2), ('v', 1, 1, 1),
        ('h', 0, 0, 6),
    ]},

    # 0 — closed oval with a diagonal slash (top-left to bottom-right).
    '0': {'w': 6, 's': [
        ('v', 0, 0, 7),
        ('v', 6, 0, 7),
        ('h', 7, 0, 6),
        ('h', 0, 0, 6),
        ('v', 1, 5, 5), ('v', 2, 4, 4), ('v', 3, 3, 3),
        ('v', 4, 2, 2), ('v', 5, 1, 1),
    ]},
    '1': {'w': 4, 's': [
        ('v', 2, 0, 7),
        ('h', 5, 0, 2),
        ('h', 0, 0, 4),
    ]},
    '2': {'w': 7, 's': [
        ('h', 7, 0, 7),
        ('v', 7, 3, 7),
        ('h', 3, 0, 7),
        ('v', 0, 0, 3),
        ('h', 0, 0, 7),
    ]},
    '3': {'w': 7, 's': [
        ('h', 7, 0, 6),
        ('v', 6, 0, 7),
        ('h', 3, 2, 6),
        ('h', 0, 0, 6),
    ]},
    '4': {'w': 7, 's': [
        ('v', 0, 3, 7),
        ('h', 3, 0, 7),
        ('v', 6, 0, 7),
    ]},
    # 5 — top bar matches the width of the middle/bottom bars (was one cell
    # too long, which made it look like it had a serif sticking out right).
    '5': {'w': 6, 's': [
        ('h', 7, 0, 6),
        ('v', 0, 3, 7),
        ('h', 3, 0, 6),
        ('v', 6, 0, 3),
        ('h', 0, 0, 6),
    ]},
    # 6 — closed lower bowl with a hook rising up the left to a top bar
    # that lands flush at the top-left corner of the stem (no gap).
    '6': {'w': 6, 's': [
        ('v', 0, 0, 7),       # left stem (full)
        ('h', 7, 0, 6),       # top bar (flush to stem)
        ('h', 4, 0, 6),       # middle bar (bowl top)
        ('v', 6, 0, 4),       # right wall of bowl
        ('h', 0, 0, 6),       # bottom bar
    ]},
    # 7 — top bar with a single-cell diagonal staircase leg from
    # top-right down to the baseline at the left.
    # 7 — top bar + diagonal staircase from the top-right corner
    # (directly under the bar's right end) down to the baseline at the
    # left edge. Single-cell steps, lands flat at (0, 0).
    '7': {'w': 6, 's': [
        ('h', 7, 0, 6),
        ('v', 6, 6, 6), ('v', 5, 5, 5), ('v', 4, 4, 4),
        ('v', 3, 3, 3), ('v', 2, 2, 2), ('v', 1, 1, 1),
        ('v', 0, 0, 0),
    ]},
    '8': {'w': 7, 's': [
        ('v', 0, 0, 7),
        ('v', 7, 0, 7),
        ('h', 7, 0, 7),
        ('h', 3, 0, 7),
        ('h', 0, 0, 7),
    ]},
    '9': {'w': 7, 's': [
        ('h', 7, 0, 7),
        ('v', 7, 0, 7),
        ('v', 0, 3, 7),
        ('h', 3, 0, 7),
    ]},

    # Dots use a single zero-length stroke (renders as a w×w square that
    # scales with weight), so the dot stays connected at every weight —
    # the old 2-h-stroke "1×1 square outline" construction left a visible
    # gap of (1−w) cells, which read as two stacked dashes at Thin.
    '.': {'w': 2, 's': [('v', 1, 1, 1)]},
    ',': {'w': 2, 's': [('v', 1, -1, -1)]},
    ':': {'w': 2, 's': [('v', 1, 1, 1), ('v', 1, 5, 5)]},
    ';': {'w': 2, 's': [('v', 1, 5, 5), ('v', 1, -1, -1)]},
    '-': {'w': 5, 's': [('h', 3, 0, 5)]},
    '_': {'w': 7, 's': [('h', -1, 0, 7)]},
    '!': {'w': 2, 's': [('v', 1, 2, 7), ('v', 1, 1, 1)]},
    '?': {'w': 5, 's': [
        ('h', 7, 0, 5),
        ('v', 5, 4, 7),
        ('h', 4, 2, 5),
        ('v', 2, 2, 4),
        ('v', 2, 1, 1),
    ]},
    '(': {'w': 4, 's': [('v', 0, 1, 6), ('h', 1, 0, 1), ('h', 6, 0, 1)]},
    ')': {'w': 4, 's': [('v', 4, 1, 6), ('h', 1, 3, 4), ('h', 6, 3, 4)]},
    '[': {'w': 4, 's': [('v', 0, 0, 7), ('h', 0, 0, 4), ('h', 7, 0, 4)]},
    ']': {'w': 4, 's': [('v', 4, 0, 7), ('h', 0, 0, 4), ('h', 7, 0, 4)]},
    # + and = on integer cells. Slight asymmetry (cross centers at x=3,y=4
    # instead of 3.5,3.5; = stripes at y=2 and y=5 instead of 2.5 and 4.5)
    # is invisible in practice and removes the sub-cell offset.
    '+': {'w': 6, 's': [('h', 4, 1, 6), ('v', 3, 1, 6)]},
    '=': {'w': 6, 's': [('h', 5, 0, 6), ('h', 2, 0, 6)]},
    # · — middle dot (mid x-height), distinct from baseline '.'
    '·': {'w': 2, 's': [('v', 1, 3, 3)]},
    # × — compact saltire (staircase X) centered on the body
    '×': {'w': 5, 's': [
        ('v', 0, 5, 5), ('v', 1, 4, 4), ('v', 2, 3, 3), ('v', 3, 4, 4), ('v', 4, 5, 5),
        ('v', 0, 1, 1), ('v', 1, 2, 2), ('v', 3, 2, 2), ('v', 4, 1, 1),
    ]},
    # © — outer square with an open C inside
    '©': {'w': 7, 's': [
        ('v', 0, 1, 6), ('v', 7, 1, 6),
        ('h', 7, 1, 6), ('h', 0, 1, 6),
        ('v', 2, 2, 5),
        ('h', 5, 2, 5),
        ('h', 2, 2, 5),
    ]},

    # --- ASCII leftovers ---
    # $ — cleaner S + through-stem (stem stops short of top/bottom bars)
    '$': {'w': 6, 's': [
        ('h', 7, 1, 5),
        ('v', 1, 4, 7),
        ('h', 4, 1, 5),
        ('v', 5, 0, 4),
        ('h', 0, 1, 5),
        ('v', 3, 1, 6),
    ]},
    # % — separated ovals + clear slash
    '%': {'w': 7, 's': [
        ('v', 0, 5, 7), ('v', 2, 5, 7), ('h', 7, 0, 2), ('h', 5, 0, 2),
        ('v', 1, 1, 1), ('v', 2, 2, 2), ('v', 3, 3, 3),
        ('v', 4, 4, 4), ('v', 5, 5, 5),
        ('v', 5, 0, 2), ('v', 7, 0, 2), ('h', 2, 5, 7), ('h', 0, 5, 7),
    ]},
    # * — six-point star on H/V grid (center + arms)
    '*': {'w': 5, 's': [
        ('v', 2, 1, 6),
        ('h', 4, 0, 5),
        ('v', 0, 5, 5), ('v', 4, 5, 5),
        ('v', 0, 2, 2), ('v', 4, 2, 2),
    ]},
    # < > — staircase chevrons
    '<': {'w': 5, 's': [
        ('v', 4, 6, 6), ('v', 3, 5, 5), ('v', 2, 4, 4),
        ('v', 1, 3, 3), ('v', 0, 2, 3),
        ('v', 1, 2, 2), ('v', 2, 1, 1), ('v', 3, 0, 0), ('v', 4, 0, 0),
    ]},
    '>': {'w': 5, 's': [
        ('v', 0, 6, 6), ('v', 1, 5, 5), ('v', 2, 4, 4),
        ('v', 3, 3, 3), ('v', 4, 2, 3),
        ('v', 3, 2, 2), ('v', 2, 1, 1), ('v', 1, 0, 0), ('v', 0, 0, 0),
    ]},
    '{': {'w': 4, 's': [
        ('v', 2, 0, 7),
        ('h', 7, 2, 4),
        ('h', 0, 2, 4),
        ('h', 4, 0, 2),
    ]},
    '}': {'w': 4, 's': [
        ('v', 2, 0, 7),
        ('h', 7, 0, 2),
        ('h', 0, 0, 2),
        ('h', 4, 2, 4),
    ]},
    '|': {'w': 1, 's': [('v', 0, 0, 7)]},
    '^': {'w': 5, 's': [
        ('v', 0, 4, 4), ('v', 1, 5, 5), ('v', 2, 6, 7),
        ('v', 3, 5, 5), ('v', 4, 4, 4),
    ]},
    '`': {'w': 2, 's': [('v', 0, 5, 6)]},
    '~': {'w': 6, 's': [
        ('h', 4, 0, 2), ('v', 2, 3, 4),
        ('h', 3, 2, 4), ('v', 4, 3, 4),
        ('h', 4, 4, 6),
    ]},

    # --- Typography ---
    '‘': {'w': 2, 's': [('v', 0, 5, 7)]},          # left single
    '’': {'w': 2, 's': [('v', 1, 5, 7)]},          # right single
    '“': {'w': 4, 's': [('v', 0, 5, 7), ('v', 2, 5, 7)]},
    '”': {'w': 4, 's': [('v', 1, 5, 7), ('v', 3, 5, 7)]},
    '–': {'w': 5, 's': [('h', 3, 0, 5)]},          # en dash
    '—': {'w': 8, 's': [('h', 3, 0, 8)]},          # em dash
    '−': {'w': 5, 's': [('h', 3, 0, 5)]},          # minus
    '…': {'w': 6, 's': [
        ('v', 0, 1, 1), ('v', 3, 1, 1), ('v', 6, 1, 1),
    ]},
    '•': {'w': 3, 's': [
        ('v', 1, 2, 4), ('h', 4, 0, 3), ('h', 2, 0, 3),
    ]},

    # --- Science / academic ---
    '°': {'w': 3, 's': [
        ('v', 0, 5, 7), ('v', 3, 5, 7),
        ('h', 7, 0, 3), ('h', 5, 0, 3),
    ]},
    '±': {'w': 6, 's': [
        ('h', 5, 1, 6), ('v', 3, 2, 7),
        ('h', 1, 1, 6),
    ]},
    '÷': {'w': 5, 's': [
        ('v', 2, 5, 5),
        ('h', 3, 0, 5),
        ('v', 2, 1, 1),
    ]},
    '≤': {'w': 5, 's': [
        ('v', 4, 6, 6), ('v', 3, 5, 5), ('v', 2, 4, 4),
        ('v', 1, 3, 3), ('v', 0, 2, 3),
        ('v', 1, 2, 2), ('v', 2, 1, 1), ('v', 3, 1, 1),
        ('h', 0, 0, 5),
    ]},
    '≥': {'w': 5, 's': [
        ('v', 0, 6, 6), ('v', 1, 5, 5), ('v', 2, 4, 4),
        ('v', 3, 3, 3), ('v', 4, 2, 3),
        ('v', 3, 2, 2), ('v', 2, 1, 1), ('v', 1, 1, 1),
        ('h', 0, 0, 5),
    ]},
    '≠': {'w': 6, 's': [
        ('h', 5, 0, 6), ('h', 2, 0, 6),
        ('v', 1, 0, 0), ('v', 2, 1, 1), ('v', 3, 3, 3),
        ('v', 4, 4, 4), ('v', 5, 6, 6),
    ]},
    '≈': {'w': 6, 's': [
        ('h', 5, 0, 2), ('v', 2, 4, 5), ('h', 4, 2, 4),
        ('v', 4, 4, 5), ('h', 5, 4, 6),
        ('h', 2, 0, 2), ('v', 2, 1, 2), ('h', 1, 2, 4),
        ('v', 4, 1, 2), ('h', 2, 4, 6),
    ]},
    # Superscripts — mini digits in the upper half
    '¹': {'w': 3, 's': [
        ('v', 1, 3, 7), ('h', 5, 0, 1), ('h', 3, 0, 3),
    ]},
    '²': {'w': 4, 's': [
        ('h', 7, 0, 4), ('v', 4, 5, 7), ('h', 5, 0, 4),
        ('v', 0, 3, 5), ('h', 3, 0, 4),
    ]},
    '³': {'w': 4, 's': [
        ('h', 7, 0, 3), ('v', 4, 3, 7),
        ('h', 5, 1, 4), ('h', 3, 0, 3),
    ]},
    'µ': {'w': 4, 's': [
        ('v', 0, -2, 5),      # descender stem
        ('v', 4, 0, 5),
        ('h', 0, 0, 4),
    ]},
    'π': {'w': 5, 's': [
        ('h', 5, 0, 5),
        ('v', 1, 0, 5),
        ('v', 4, 0, 5),
    ]},
    '′': {'w': 2, 's': [('v', 1, 4, 7)]},
    '″': {'w': 4, 's': [('v', 1, 4, 7), ('v', 3, 4, 7)]},

    # --- Legal / brand / currency / Spanish / arrows ---
    # ® — R in a square (mirrors ©)
    '®': {'w': 7, 's': [
        ('v', 0, 1, 6), ('v', 7, 1, 6),
        ('h', 7, 1, 6), ('h', 0, 1, 6),
        ('v', 2, 2, 5),
        ('h', 5, 2, 4),
        ('v', 4, 3, 5),
        ('h', 3, 2, 4),
        ('v', 4, 2, 3),
    ]},
    # ™ — clearer raised T·M
    '™': {'w': 8, 's': [
        ('h', 7, 0, 3), ('v', 1, 4, 7),
        ('v', 4, 4, 7), ('h', 7, 4, 8),
        ('v', 6, 4, 6), ('v', 8, 4, 7),
    ]},
    # € — C with two crossbars
    '€': {'w': 6, 's': [
        ('v', 0, 0, 7),
        ('h', 7, 0, 6),
        ('h', 0, 0, 6),
        ('h', 5, 0, 4),
        ('h', 2, 0, 4),
    ]},
    # £ — L with mid crossbar and curled top
    '£': {'w': 6, 's': [
        ('v', 1, 0, 7),
        ('h', 7, 1, 5),
        ('v', 5, 5, 7),
        ('h', 3, 0, 4),
        ('h', 0, 1, 6),
    ]},
    # ¿ ¡ — inverted ? and !
    '¿': {'w': 5, 's': [
        ('v', 2, 5, 5),
        ('v', 2, 2, 4),
        ('h', 2, 2, 5),
        ('v', 5, 0, 2),
        ('h', 0, 0, 5),
    ]},
    '¡': {'w': 2, 's': [('v', 1, 5, 5), ('v', 1, 0, 4)]},
    # § — two offset S bowls (less stacked noise)
    '§': {'w': 5, 's': [
        ('h', 7, 1, 5), ('v', 1, 5, 7), ('h', 5, 1, 5), ('v', 5, 4, 5),
        ('h', 4, 1, 4),
        ('v', 1, 2, 3), ('h', 2, 1, 5), ('v', 5, 0, 2), ('h', 0, 0, 4),
    ]},
    # Arrows
    '←': {'w': 7, 's': [
        ('h', 3, 0, 7),
        ('v', 0, 3, 3), ('v', 1, 2, 4), ('v', 2, 1, 5),
    ]},
    '→': {'w': 7, 's': [
        ('h', 3, 0, 7),
        ('v', 7, 3, 3), ('v', 6, 2, 4), ('v', 5, 1, 5),
    ]},
    '↑': {'w': 5, 's': [
        ('v', 2, 0, 7),
        ('v', 0, 4, 4), ('v', 1, 5, 5), ('v', 2, 6, 7),
        ('v', 3, 5, 5), ('v', 4, 4, 4),
    ]},
    '↓': {'w': 5, 's': [
        ('v', 2, 0, 7),
        ('v', 0, 2, 2), ('v', 1, 1, 1), ('v', 2, 0, 0),
        ('v', 3, 1, 1), ('v', 4, 2, 2),
    ]},

    # Slash and backslash as orthogonal "staircase" markers, matching style.
    '/': {'w': 5, 's': [
        ('v', 0, 0, 2), ('h', 2, 0, 2),
        ('v', 2, 2, 5), ('h', 5, 2, 4),
        ('v', 4, 5, 7),
    ]},
    '\\': {'w': 5, 's': [
        ('v', 5, 0, 2), ('h', 2, 3, 5),
        ('v', 3, 2, 5), ('h', 5, 1, 3),
        ('v', 1, 5, 7),
    ]},
    '"': {'w': 4, 's': [('v', 1, 5, 7), ('v', 3, 5, 7)]},
    "'": {'w': 2, 's': [('v', 1, 5, 7)]},
    '#': {'w': 6, 's': [('v', 2, 0, 7), ('v', 4, 0, 7), ('h', 5, 0, 6), ('h', 2, 0, 6)]},
    # & — stylized figure-8 with a tall tail extending up-right from the
    # bottom-right corner. Pure H/V can't draw the conventional ampersand
    # curve; the tail does the work of marking it as "&" vs "B" or "8".
    # & — Caslon-style asymmetric figure-8: smaller upper bowl (cols 1..4)
    # sits on top of a larger lower bowl (cols 0..4), with a 2-step
    # staircase tail kicking up to the right from the lower-right corner.
    # The asymmetric bowls + the kicking tail differentiate it from B
    # and 8 (both of which are symmetric) and from 7 (no top bar).
    '&': {'w': 6, 's': [
        ('h', 7, 1, 4),       # upper bowl top
        ('v', 1, 5, 7),       # upper bowl left
        ('v', 4, 5, 7),       # upper bowl right
        ('h', 5, 1, 4),       # waist
        ('v', 0, 0, 5),       # lower bowl left
        ('v', 4, 0, 5),       # lower bowl right
        ('h', 0, 0, 4),       # bottom
        ('v', 5, 0, 1),       # tail step 1
        ('v', 6, 1, 2),       # tail step 2 (kick up-right)
    ]},
    # @ — outer rectangle whose bottom-right corner opens out to a tail
    # that drops below and curls back; inside sits a fully-formed "a"
    # (closed loop + internal divider). All strokes on integer cells so
    # they line up with strokes in the rest of the font (no sub-cell
    # offsets at junctions).
    '@': {'w': 8, 's': [
        ('v', 0, 0, 7),
        ('v', 8, 1, 7),       # right wall stops above baseline (opens for tail)
        ('h', 7, 0, 8),
        ('h', 0, 0, 6),       # bottom only spans to col 6
        ('v', 6, 0, 1),       # tail drop on the left side of opening
        # Inner "a": closed rectangle (cols 2..6, rows 2..6) + divider
        ('v', 2, 2, 6),
        ('v', 6, 2, 6),
        ('h', 6, 2, 6),
        ('h', 2, 2, 6),
        ('h', 4, 2, 6),       # divider of the 'a' counter
    ]},

    # === LOWERCASE ===
    # x-height = 5 cells (lowercase tops at y=5). Ascenders rise to the
    # cap-line at y=7 (b, d, f, h, k, l, t). Descenders drop to y=-2
    # (g, j, p, q, y). All strokes on integer centerlines, like uppercase.

    'a': {'w': 4, 's': [
        ('v', 0, 0, 5),
        ('v', 4, 0, 5),
        ('h', 5, 0, 4),
        ('h', 3, 0, 4),       # waist
        ('h', 0, 0, 4),
    ]},
    'b': {'w': 4, 's': [
        ('v', 0, 0, 7),       # left ascender + stem
        ('v', 4, 0, 5),       # bowl right
        ('h', 5, 0, 4),       # bowl top
        ('h', 0, 0, 4),       # bowl bottom
    ]},
    'c': {'w': 4, 's': [
        ('v', 0, 0, 5),
        ('h', 5, 0, 4),
        ('h', 0, 0, 4),
    ]},
    'd': {'w': 4, 's': [
        ('v', 4, 0, 7),       # right ascender + stem
        ('v', 0, 0, 5),       # bowl left
        ('h', 5, 0, 4),       # bowl top
        ('h', 0, 0, 4),       # bowl bottom
    ]},
    'e': {'w': 4, 's': [
        ('v', 0, 0, 5),
        ('h', 5, 0, 4),
        ('h', 3, 0, 4),       # middle bar (closes upper counter)
        ('v', 4, 3, 5),       # right wall (upper half only — opens at bottom-right)
        ('h', 0, 0, 4),
    ]},
    'f': {'w': 3, 's': [
        ('v', 1, 0, 6),       # stem
        ('h', 7, 1, 3),       # top hook
        ('h', 4, 0, 3),       # crossbar
    ]},
    'g': {'w': 4, 's': [
        ('v', 0, 2, 5),       # bowl left
        ('v', 4, -2, 5),      # right stem + descender (full)
        ('h', 5, 0, 4),       # bowl top
        ('h', 2, 0, 4),       # bowl bottom
        ('h', -2, 0, 4),      # descender hook
    ]},
    'h': {'w': 4, 's': [
        ('v', 0, 0, 7),       # left ascender stem
        ('v', 4, 0, 5),       # right stem (x-height only)
        ('h', 5, 0, 4),       # arch
    ]},
    'i': {'w': 1, 's': [
        ('v', 0, 0, 4),       # stem (slightly shorter to leave room for dot)
        ('v', 0, 6, 6),       # dot
    ]},
    'j': {'w': 2, 's': [
        ('v', 1, -2, 4),      # stem + descender
        ('v', 1, 6, 6),       # dot
        ('h', -2, 0, 1),      # descender hook bottom
        ('v', 0, -2, -1),     # descender hook left
    ]},
    'k': {'w': 4, 's': [
        ('v', 0, 0, 7),       # left ascender stem
        ('v', 1, 2, 3),       # junction
        ('v', 2, 4, 4), ('v', 3, 5, 5),  # upper arm
        ('v', 2, 1, 1), ('v', 3, 0, 0),  # lower arm
    ]},
    'l': {'w': 1, 's': [
        ('v', 0, 0, 7),
    ]},
    'm': {'w': 6, 's': [
        ('v', 0, 0, 5),
        ('v', 3, 0, 4),       # middle pillar (slightly shorter, like uppercase M)
        ('v', 6, 0, 5),
        ('h', 5, 0, 6),
    ]},
    'n': {'w': 4, 's': [
        ('v', 0, 0, 5),
        ('v', 4, 0, 5),
        ('h', 5, 0, 4),
    ]},
    'o': {'w': 4, 's': [
        ('v', 0, 0, 5),
        ('v', 4, 0, 5),
        ('h', 5, 0, 4),
        ('h', 0, 0, 4),
    ]},
    'p': {'w': 4, 's': [
        ('v', 0, -2, 5),      # left stem with descender
        ('v', 4, 0, 5),       # bowl right
        ('h', 5, 0, 4),
        ('h', 0, 0, 4),
    ]},
    'q': {'w': 4, 's': [
        ('v', 4, -2, 5),      # right stem with descender
        ('v', 0, 0, 5),       # bowl left
        ('h', 5, 0, 4),
        ('h', 0, 0, 4),
    ]},
    'r': {'w': 3, 's': [
        ('v', 0, 0, 5),       # stem
        ('h', 5, 0, 3),       # top
        ('v', 3, 4, 5),       # tiny hook descending from top-right
    ]},
    's': {'w': 4, 's': [
        ('h', 5, 0, 4),
        ('v', 0, 3, 5),       # upper-left wall
        ('h', 3, 0, 4),       # middle
        ('v', 4, 0, 3),       # lower-right wall
        ('h', 0, 0, 4),
    ]},
    't': {'w': 3, 's': [
        ('v', 1, 0, 6),       # stem (slight ascender)
        ('h', 5, 0, 3),       # crossbar
    ]},
    'u': {'w': 4, 's': [
        ('v', 0, 0, 5),
        ('v', 4, 0, 5),
        ('h', 0, 0, 4),
    ]},
    'v': {'w': 4, 's': [
        ('v', 0, 3, 5),
        ('v', 4, 3, 5),
        ('v', 1, 2, 2),
        ('v', 3, 2, 2),
        ('v', 2, 0, 1),
    ]},
    'w': {'w': 6, 's': [
        ('v', 0, 0, 5),
        ('v', 3, 1, 5),       # middle pillar (slightly shorter)
        ('v', 6, 0, 5),
        ('h', 0, 0, 6),
    ]},
    'x': {'w': 4, 's': [
        ('v', 0, 0, 0), ('v', 1, 1, 1),
        ('v', 4, 0, 0), ('v', 3, 1, 1),
        ('v', 0, 5, 5), ('v', 1, 4, 4),
        ('v', 4, 5, 5), ('v', 3, 4, 4),
        ('v', 2, 2, 3),       # center cross
    ]},
    'y': {'w': 4, 's': [
        ('v', 0, 3, 5),       # upper-left
        ('v', 4, -2, 5),      # right stem + descender
        ('v', 1, 2, 2),
        ('v', 2, 1, 1),
        ('v', 3, 0, 0),
        ('h', -2, 0, 4),      # descender hook
    ]},
    'z': {'w': 4, 's': [
        ('h', 5, 0, 4),
        ('v', 4, 4, 4), ('v', 3, 3, 3),
        ('v', 2, 2, 2), ('v', 1, 1, 1),
        ('h', 0, 0, 4),
    ]},
}

# ---------------------------------------------------------------------------
# Accented Latin — base letter + accent marks (uppercase accents sit at y=8,
# above the 7-cell cap; lowercase accents use y=6–7 above x-height).
# ---------------------------------------------------------------------------

def _accented(base: str, accents: list, *, drop_tittle: bool = False, w: int | None = None) -> dict:
    src = GLYPHS[base]
    strokes = list(src['s'])
    if drop_tittle:
        # Remove the i/j tittle (zero-length stroke at y=6).
        strokes = [
            s for s in strokes
            if not (s[0] == 'v' and len(s) == 4 and s[2] == 6 and s[3] == 6)
        ]
    return {'w': src['w'] if w is None else w, 's': strokes + accents}


def _acute(w: int, y0: int = 6) -> list:
    cx = max(0, min(w - 1, w // 2))
    return [('v', cx, y0, y0), ('v', min(w, cx + 1), y0 + 1, y0 + 1)]


def _grave(w: int, y0: int = 6) -> list:
    cx = max(0, min(w, w // 2 + (1 if w > 2 else 0)))
    return [('v', cx, y0 + 1, y0 + 1), ('v', max(0, cx - 1), y0, y0)]


def _umlaut(w: int, y: int = 6) -> list:
    return [
        ('v', max(0, w // 2 - 1), y, y),
        ('v', min(w, w // 2 + 1), y, y),
    ]


def _tilde(w: int, y: int = 6) -> list:
    # Compact ~ above the letter
    x0 = max(0, w // 2 - 2)
    return [
        ('h', y + 1, x0, x0 + 1),
        ('v', x0 + 1, y, y + 1),
        ('h', y, x0 + 1, x0 + 2),
        ('v', x0 + 2, y, y + 1),
        ('h', y + 1, x0 + 2, x0 + 3),
    ]


def _cedilla(w: int) -> list:
    cx = w // 2
    return [('v', cx, -2, 0), ('h', -2, cx, min(w, cx + 2))]


_ACCENTED = {
    # lowercase acute / grave / umlaut
    'á': _accented('a', _acute(4)),
    'é': _accented('e', _acute(4)),
    'í': _accented('i', _acute(2), drop_tittle=True, w=2),
    'ó': _accented('o', _acute(4)),
    'ú': _accented('u', _acute(4)),
    'à': _accented('a', _grave(4)),
    'è': _accented('e', _grave(4)),
    'ù': _accented('u', _grave(4)),
    'ä': _accented('a', _umlaut(4)),
    'ë': _accented('e', _umlaut(4)),
    'ï': _accented('i', _umlaut(2), drop_tittle=True, w=2),
    'ö': _accented('o', _umlaut(4)),
    'ü': _accented('u', _umlaut(4)),
    'ñ': _accented('n', _tilde(4)),
    'ç': _accented('c', _cedilla(4)),
    # uppercase (accents above cap-line)
    'Á': _accented('A', _acute(6, y0=7)),
    'É': _accented('E', _acute(7, y0=7)),
    'Í': _accented('I', _acute(2, y0=7), w=2),
    'Ó': _accented('O', _acute(7, y0=7)),
    'Ú': _accented('U', _acute(7, y0=7)),
    'Ä': _accented('A', _umlaut(6, y=8)),
    'Ö': _accented('O', _umlaut(7, y=8)),
    'Ü': _accented('U', _umlaut(7, y=8)),
    'Ñ': _accented('N', _tilde(6, y=7)),
    # ligatures / special
    'ß': {
        'w': 5,
        's': [
            ('v', 0, 0, 7),
            ('h', 7, 0, 3),
            ('v', 3, 5, 7),
            ('h', 5, 0, 3),
            ('v', 3, 2, 4),
            ('h', 2, 0, 4),
            ('v', 4, 0, 2),
            ('h', 0, 0, 4),
        ],
    },
    'æ': {
        'w': 7,
        's': [
            ('v', 0, 0, 5),
            ('v', 3, 0, 5),
            ('h', 5, 0, 3),
            ('h', 2, 0, 3),
            ('h', 0, 0, 3),
            ('v', 7, 0, 5),
            ('h', 5, 3, 7),
            ('h', 2, 3, 7),
            ('h', 0, 3, 7),
        ],
    },
    'œ': {
        'w': 7,
        's': [
            ('v', 0, 0, 5),
            ('v', 3, 0, 5),
            ('h', 5, 0, 3),
            ('h', 0, 0, 3),
            ('h', 5, 3, 7),
            ('h', 3, 3, 7),
            ('v', 7, 3, 5),
            ('h', 0, 3, 7),
        ],
    },
    'Æ': {
        'w': 8,
        's': [
            ('v', 0, 0, 7),
            ('v', 4, 0, 7),
            ('h', 7, 0, 4),
            ('h', 4, 0, 4),
            ('h', 7, 4, 8),
            ('h', 4, 4, 8),
            ('h', 0, 4, 8),
        ],
    },
    'Œ': {
        'w': 9,
        's': [
            ('v', 0, 0, 7),
            ('v', 4, 0, 7),
            ('h', 7, 0, 4),
            ('h', 0, 0, 4),
            ('h', 7, 4, 9),
            ('h', 4, 4, 9),
            ('h', 0, 4, 9),
            ('v', 9, 0, 7),
        ],
    },

    # --- Math / fractions ---
    '∞': {'w': 7, 's': [
        ('v', 0, 2, 5), ('v', 3, 2, 5), ('h', 5, 0, 3), ('h', 2, 0, 3),
        ('v', 4, 2, 5), ('v', 7, 2, 5), ('h', 5, 4, 7), ('h', 2, 4, 7),
    ]},
    '√': {'w': 6, 's': [
        ('v', 0, 2, 3), ('v', 1, 1, 2), ('v', 2, 0, 4),
        ('h', 4, 2, 6), ('v', 6, 4, 7),
    ]},
    '∑': {'w': 6, 's': [
        ('h', 7, 0, 6), ('v', 0, 5, 7),
        ('v', 0, 3, 4), ('v', 1, 3, 4), ('v', 2, 3, 4),
        ('v', 3, 3, 4), ('v', 4, 3, 4), ('v', 5, 3, 4),
        ('v', 0, 0, 2), ('h', 0, 0, 6),
    ]},
    '∏': {'w': 6, 's': [
        ('h', 7, 0, 6), ('v', 0, 0, 7), ('v', 6, 0, 7),
    ]},
    '∂': {'w': 5, 's': [
        ('v', 4, 0, 7),
        ('h', 7, 1, 4), ('v', 1, 4, 7),
        ('h', 4, 1, 4), ('v', 1, 0, 3),
        ('h', 0, 1, 4),
    ]},
    '½': {'w': 7, 's': [
        ('v', 1, 4, 7), ('h', 7, 0, 2),
        ('v', 0, 0, 0), ('v', 1, 1, 1), ('v', 2, 2, 2),
        ('v', 3, 3, 3), ('v', 4, 4, 4), ('v', 5, 5, 5),
        ('h', 3, 4, 7), ('v', 4, 0, 1), ('v', 7, 0, 3),
        ('h', 1, 4, 7), ('h', 0, 4, 7),
    ]},
    '¼': {'w': 7, 's': [
        ('v', 0, 5, 7), ('v', 2, 4, 7), ('h', 4, 0, 2),
        ('v', 0, 0, 0), ('v', 1, 1, 1), ('v', 2, 2, 2),
        ('v', 3, 3, 3), ('v', 4, 4, 4), ('v', 5, 5, 5),
        ('h', 3, 4, 7), ('v', 4, 0, 1), ('v', 7, 0, 3),
        ('h', 1, 4, 7), ('h', 0, 4, 7),
    ]},
    '¾': {'w': 7, 's': [
        ('h', 7, 0, 3), ('v', 3, 5, 7), ('h', 5, 0, 3),
        ('v', 0, 4, 5), ('h', 4, 0, 3),
        ('v', 0, 0, 0), ('v', 1, 1, 1), ('v', 2, 2, 2),
        ('v', 3, 3, 3), ('v', 4, 4, 4), ('v', 5, 5, 5),
        ('h', 3, 4, 7), ('v', 4, 0, 1), ('v', 7, 0, 3),
        ('h', 1, 4, 7), ('h', 0, 4, 7),
    ]},
}

GLYPHS.update(_ACCENTED)

# ---------------------------------------------------------------------------
# Research group symbols (Private Use Area U+E000–U+E017)
# ---------------------------------------------------------------------------
from group_glyphs import GROUP_GLYPHS, GROUP_SLUGS  # noqa: E402
from brand_glyphs import get_brand_glyphs  # noqa: E402

GLYPHS.update(GROUP_GLYPHS)
GLYPHS.update(get_brand_glyphs(GLYPHS))
