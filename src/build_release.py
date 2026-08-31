#!/usr/bin/env python3
"""One-shot release build: fonts → web static → OG → zip → previews → tests.

Usage (from repo root or anywhere):
    python3 src/build_release.py
    python3 src/build_release.py --skip-tests
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
DIST = ROOT / 'dist'
WEB_FONTS = ROOT / 'web' / 'static' / 'fonts'
WEB_STATIC = ROOT / 'web' / 'static'
LICENSE = ROOT / 'LICENSE'
PS = 'MITMediaLabFont'
WEIGHTS = ('Thin', 'Light', 'Regular', 'Medium', 'Bold', 'Black')


def run(cmd: list[str], **kw) -> None:
    print('+', ' '.join(cmd))
    subprocess.check_call(cmd, cwd=ROOT, **kw)


def build_fonts() -> None:
    env = {**dict(**{k: v for k, v in __import__('os').environ.items()}),
           'PYTHONPATH': str(SRC)}
    run([sys.executable, str(SRC / 'build_font.py')], env=env)


def copy_fonts_to_web() -> None:
    WEB_FONTS.mkdir(parents=True, exist_ok=True)
    for w in WEIGHTS:
        for ext in ('ttf', 'otf'):
            src = DIST / f'{PS}-{w}.{ext}'
            if not src.exists():
                raise FileNotFoundError(src)
            shutil.copy2(src, WEB_FONTS / src.name)
    print(f'  copied {len(WEIGHTS) * 2} font files → web/static/fonts/')


def make_zip() -> Path:
    DIST.mkdir(exist_ok=True)
    zip_path = DIST / f'{PS}.zip'
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        if LICENSE.exists():
            zf.write(LICENSE, arcname='LICENSE')
        readme = ROOT / 'README.md'
        if readme.exists():
            zf.write(readme, arcname='README.md')
        for w in WEIGHTS:
            for ext in ('ttf', 'otf'):
                p = DIST / f'{PS}-{w}.{ext}'
                zf.write(p, arcname=f'fonts/{p.name}')
    # Mirror zip into the demo site's static root for download links.
    shutil.copy2(zip_path, WEB_STATIC / zip_path.name)
    print(f'  wrote {zip_path} ({zip_path.stat().st_size} bytes) + web copy')
    return zip_path


def make_og() -> None:
    og = SRC / 'make_og.py'
    if og.exists():
        run([sys.executable, str(og)])


def make_preview() -> None:
    preview = SRC / 'make_preview.py'
    if preview.exists():
        run([sys.executable, str(preview)])


def make_screenshots() -> None:
    shots = SRC / 'make_screenshots.py'
    if shots.exists():
        run([sys.executable, str(shots)])


def run_tests() -> None:
    test = ROOT / 'tests' / 'test_font.py'
    if test.exists():
        run([sys.executable, str(test)])


def write_font_version() -> str:
    """Bump a cache-bust query from the Regular TTF mtime/size."""
    regular = DIST / f'{PS}-Regular.ttf'
    ver = f'v{int(regular.stat().st_mtime)}-{regular.stat().st_size}'
    css = ROOT / 'web' / 'static' / 'fonts.css'
    text = css.read_text(encoding='utf-8')
    # Rewrite every /fonts/*.ttf|otf URL to include ?ver=
    import re
    def repl(m: re.Match) -> str:
        path = m.group(1)
        return f"url('{path}?{ver}')"

    new = re.sub(
        r"url\('(/fonts/MITMediaLabFont-[^']+\.(?:ttf|otf))(?:\?[^']*)?'\)",
        repl,
        text,
    )
    css.write_text(new, encoding='utf-8')
    print(f'  fonts.css cache-bust → {ver}')
    return ver


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skip-tests', action='store_true')
    ap.add_argument('--skip-screenshots', action='store_true')
    args = ap.parse_args()

    print('== build fonts ==')
    build_fonts()
    print('== copy to web ==')
    copy_fonts_to_web()
    print('== cache-bust fonts.css ==')
    write_font_version()
    print('== package zip ==')
    make_zip()
    print('== OG image ==')
    make_og()
    print('== glyph preview ==')
    make_preview()
    if not args.skip_screenshots:
        print('== README screenshots ==')
        make_screenshots()
    if not args.skip_tests:
        print('== tests ==')
        run_tests()
    print('done.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
