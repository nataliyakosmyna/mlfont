"""Tile the reference group glyph PNGs into one mosaic for analysis."""
from PIL import Image
from pathlib import Path

here = Path(__file__).parent
pngs = sorted(here.glob('*.svg.png'))
cols = 6
cell = 220
W = cols * cell
rows = (len(pngs) + cols - 1) // cols
H = rows * cell
out = Image.new('RGB', (W, H), '#f4f1ea')
for i, p in enumerate(pngs):
    im = Image.open(p).convert('RGB')
    im.thumbnail((cell - 8, cell - 8))
    x = (i % cols) * cell + (cell - im.width) // 2
    y = (i // cols) * cell + (cell - im.height) // 2
    out.paste(im, (x, y))
out.save(here / '_mosaic.png')
print(f'wrote _mosaic.png  {W}x{H}  ({len(pngs)} glyphs)')
