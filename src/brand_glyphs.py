"""MIT / Media Lab brand symbols (Private Use Area U+E030–U+E031).

MIT wordmark from ``reference_glyphs/MIT_logo_2023.svg`` (full M·I·T) at
native proportions. At render time each style scales the mark uniformly so
the M pillars match letter ``M`` ink height (same scale on X and Y).

When the wordmark sits among square PUA icons, shrink with CSS
``font-size: calc(1em * 63 / 119)`` (class ``mit-fit``).
"""

from __future__ import annotations

from svg_to_glyph import GRID

# 2023 MIT parent-brand module (720-unit cap, 160-unit module, 80-unit gap).
_M = 14 / 9
_G = 7 / 9
_STEM_H = 14 / 3
_BAR_W = 35 / 9
_MIT_W = 119 / 9

MIT_WIDTH_CELLS = _MIT_W
MIT_FIT = GRID / _MIT_W          # ≈ 0.529 — CSS shrink among square icons
MIT_TEXT_SCALE = 1.0             # native outlines already match cap height

MIT_CODEPOINT = 0xE030
MEDIA_LAB_CODEPOINT = 0xE031


def mit_logo_blocks() -> list[tuple]:
    """Full 2023 MIT wordmark at native proportions (height = cap = 7)."""
    m0 = 0.0
    m1 = _M + _G
    m2 = 2 * (_M + _G)
    xi = 3 * (_M + _G)
    xt = 4 * (_M + _G)
    return [
        (m0, 0, _M, 7),
        (m1, _M, _M, 7 - _M),
        (m2, 0, _M, 7),
        (xi, 0, _M, _STEM_H),
        (xi, 7 - _M, _M, _M),
        (xt, 0, _M, _STEM_H),
        (xt, 7 - _M, _BAR_W, _M),
    ]


def media_lab_mark_blocks() -> list[tuple]:
    return [
        (0, 6, 4, 1),
        (3, 4, 1, 2),
        (3, 3, 4, 1),
        (6, 0, 1, 4),
        (0, 0, 1, 4),
        (0, 0, 4, 1),
    ]


def media_lab_mark_to_glyph() -> dict:
    return {'w': GRID, 'blocks': media_lab_mark_blocks(), 'square': True}


def mit_logo_to_glyph() -> dict:
    """Full MIT wordmark — scaled uniformly per style to match letter ``M``.

    ``match_letter_stroke`` applies ``1 + weight/cap`` from the baseline
    so ink height and proportions track stroke weight (not vertical stretch).
    """
    return {
        'w': _MIT_W,
        'blocks': mit_logo_blocks(),
        'sb': 0.0,
        'match_letter_stroke': True,
    }


def get_brand_glyphs(_glyphs: dict) -> dict:
    return {
        chr(MIT_CODEPOINT): mit_logo_to_glyph(),
        chr(MEDIA_LAB_CODEPOINT): media_lab_mark_to_glyph(),
    }
