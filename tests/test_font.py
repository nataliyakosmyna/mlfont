#!/usr/bin/env python3
"""Basic font integrity checks (cmap, empty glyphs, square advances)."""

from __future__ import annotations

import sys
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from brand_glyphs import get_brand_glyphs  # noqa: E402
from build_font import CAP_HEIGHT, STYLES  # noqa: E402
from glyphs import GLYPHS  # noqa: E402

DIST = ROOT / 'dist'
PS = 'MITMediaLabFont'
FAILS: list[str] = []


def fail(msg: str) -> None:
    FAILS.append(msg)
    print('FAIL:', msg)


def check_style(weight: str) -> None:
    path = DIST / f'{PS}-{weight}.ttf'
    if not path.exists():
        fail(f'missing {path}')
        return
    font = TTFont(path)
    cmap = font.getBestCmap() or {}
    glyf = font['glyf']
    hmtx = font['hmtx'].metrics

    # Every source glyph must be in cmap
    for ch in GLYPHS:
        cp = ord(ch)
        if cp not in cmap:
            fail(f'{weight}: missing cmap U+{cp:04X} ({ch!r})')
            continue
        name = cmap[cp]
        g = glyf[name]
        # Empty outline check (space may be empty)
        if ch != ' ' and (g.numberOfContours == 0 or g.numberOfContours is None):
            # composite / empty
            if not hasattr(g, 'data') or g.numberOfContours == 0:
                fail(f'{weight}: empty outline for U+{cp:04X} ({ch!r})')

    # Square brand / group icons: advance == cap height
    for ch, gdef in GLYPHS.items():
        if not gdef.get('square'):
            continue
        name = cmap.get(ord(ch))
        if not name:
            continue
        adv, _ = hmtx[name]
        if adv != CAP_HEIGHT:
            fail(f'{weight}: square {ch!r} advance {adv} != cap {CAP_HEIGHT}')

    # Tabular digits: equal advances
    dig_advs = []
    for d in '0123456789':
        name = cmap.get(ord(d))
        if name:
            dig_advs.append(hmtx[name][0])
    if dig_advs and len(set(dig_advs)) != 1:
        fail(f'{weight}: digit advances not tabular: {dig_advs}')

    # .notdef present and non-empty
    if '.notdef' not in glyf:
        fail(f'{weight}: missing .notdef')
    elif glyf['.notdef'].numberOfContours <= 0:
        fail(f'{weight}: empty .notdef')


def main() -> int:
    print(f'testing {len(STYLES)} weights against {len(GLYPHS)} source glyphs')
    # brand glyphs must be present in GLYPHS
    brands = get_brand_glyphs(GLYPHS)
    for ch in brands:
        if ch not in GLYPHS:
            fail(f'brand glyph {ch!r} not merged into GLYPHS')

    for weight in STYLES:
        check_style(weight)

    if FAILS:
        print(f'\n{len(FAILS)} failure(s)')
        return 1
    print('all checks passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
