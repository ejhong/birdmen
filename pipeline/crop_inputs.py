"""Publish crops of supplied screenshots listed in research/images.json.

    /usr/local/bin/python3 pipeline/crop_inputs.py
    /usr/local/bin/python3 pipeline/crop_inputs.py --check

Entries with a "crop" box are pictures that were only captured inside phone screenshots.
The box is [left, top, right, bottom] in pixels of the untouched original in inputs/. The
crop is saved as a JPEG in docs/img/inputs/. Nothing else about the picture is changed: no
resampling, rotation, colour correction or retouching. Needs Pillow; publish.py itself
only checks that each crop exists.
"""
import argparse
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main(check=False):
    items = [i for i in json.loads((ROOT / 'research/images.json').read_text()) if i.get('crop')]
    changed = []
    for item in items:
        src = ROOT / 'inputs' / item['input']
        dst = ROOT / 'docs/img/inputs' / item['output']
        left, top, right, bottom = item['crop']
        with Image.open(src) as im:
            if not (0 <= left < right <= im.width and 0 <= top < bottom <= im.height):
                raise ValueError(f'Crop box outside the image: {item["input"]}')
            if dst.is_file():
                with Image.open(dst) as done:
                    if done.size == (right - left, bottom - top):
                        continue
            changed.append(str(dst.relative_to(ROOT)))
            if not check:
                dst.parent.mkdir(parents=True, exist_ok=True)
                im.crop((left, top, right, bottom)).convert('RGB').save(dst, 'JPEG', quality=88, optimize=True)
    print('Current: all crops present' if not changed else ('Missing: ' if check else 'Written: ') + ', '.join(changed))
    return 1 if check and changed else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='report missing or wrongly sized crops without writing')
    raise SystemExit(main(parser.parse_args().check))
