"""Download group lockup SVGs from MIT Media Lab overview pages.

Each overview page embeds two inline SVGs:
  - ``glyph-with-text``    full mark (icon + group name)
  - ``glyph-without-text`` icon only (newer coordinate system)

Saved under ``reference_glyphs/overview/``.

Usage:
    python3 src/fetch_group_overviews.py
    python3 src/fetch_group_overviews.py fluid-interfaces
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

from svg_to_glyph import GROUPS

UA = 'Mozilla/5.0 (compatible; mlfont/1.0)'
OVERVIEW = 'https://www.media.mit.edu/groups/{slug}/overview/'


def extract_svg(html: str, class_name: str) -> str | None:
    pat = rf"class='{class_name}'>(<svg.*?</svg>)"
    m = re.search(pat, html, re.S)
    return m.group(1) if m else None


def fetch_one(slug: str, out_dir: Path) -> dict[str, bool]:
    url = OVERVIEW.format(slug=slug)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='replace')

    got: dict[str, bool] = {}
    for cls, suffix in (
        ('glyph-with-text', 'lockup'),
        ('glyph-without-text', 'icon'),
    ):
        svg = extract_svg(html, cls)
        dest = out_dir / f'{slug}.{suffix}.svg'
        if svg:
            dest.write_text(svg)
            got[suffix] = True
        else:
            got[suffix] = False
    return got


def main():
    out_dir = Path(__file__).resolve().parent.parent / 'reference_glyphs' / 'overview'
    out_dir.mkdir(parents=True, exist_ok=True)
    slugs = [a for a in sys.argv[1:] if not a.startswith('-')] or GROUPS

    for slug in slugs:
        try:
            got = fetch_one(slug, out_dir)
            flags = ' '.join(k for k, v in got.items() if v)
            miss = ' '.join(k for k, v in got.items() if not v)
            line = f'{slug:42s} {flags or "(none)"}'
            if miss:
                line += f'  MISSING: {miss}'
            print(line)
        except Exception as exc:
            print(f'{slug:42s} ERROR: {exc}')


if __name__ == '__main__':
    main()
