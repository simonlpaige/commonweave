"""Build the site's original typographic preview card (requires Pillow).

Uses installed Georgia or DejaVu Serif. Pass --font/--italic to reproduce with
specific font files. This is a brand graphic, not a screenshot of real map data.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path)
    parser.add_argument('--italic', type=Path)
    args = parser.parse_args()
    normal = args.font or next(p for p in [Path('C:/Windows/Fonts/georgia.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')] if p.exists())
    italic = args.italic or next(p for p in [Path('C:/Windows/Fonts/georgiai.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf')] if p.exists())
    paper, ink, moss = '#F2EBDC', '#16201A', '#2F4A33'
    image = Image.new('RGB', (1200, 630), paper)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 22, 630), fill=moss)
    draw.text((72, 46), 'commonweave', font=ImageFont.truetype(str(italic), 58), fill=moss)
    draw.line((74, 134, 1128, 134), fill=moss, width=2)
    title = ImageFont.truetype(str(normal), 64)
    draw.text((72, 184), 'Ideas for shared needs.', font=title, fill=ink)
    draw.text((72, 270), 'Organizations to investigate.', font=title, fill=ink)
    draw.text((76, 402), 'Explore the knowledge base and map.', font=ImageFont.truetype(str(normal), 34), fill=moss)
    draw.text((76, 526), 'commonweave.earth', font=ImageFont.truetype(str(normal), 30), fill=ink)
    target = ROOT / 'assets/images/commonweave-share.png'
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, optimize=True)
    print(target)


if __name__ == '__main__':
    main()
