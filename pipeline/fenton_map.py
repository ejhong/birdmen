"""Draw the movements claimed in Bruce R. Fenton's thread as a static SVG map.

    python3 pipeline/fenton_map.py

Reads the Natural Earth 110m coastlines already published in docs/data/site.json and writes
docs/img/fenton-map.svg. The arrows and dates are the thread's claims, drawn by this project;
they are not a reconstruction. Standard library only.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
W, H = 1040, 400
LEGEND = 64  # extra band under the map
SCALE = W / 360
LON0, LAT_TOP = -30, 76  # map seam at 30°W so the Pacific is unbroken


def x(lon):
    return ((lon - LON0) % 360) * SCALE


def y(lat):
    return (LAT_TOP - lat) * SCALE


def coast_paths(lines):
    out = []
    for line in lines:
        d, prev = [], None
        for lon, lat in line:
            if lat < LAT_TOP - H / SCALE - 5 or lat > LAT_TOP + 5:
                prev = None
                continue
            px, py = x(lon), y(lat)
            jump = prev is None or abs(px - prev) > W / 2
            d.append(f"{'M' if jump else 'L'}{px:.1f} {py:.1f}")
            prev = px
        if d:
            out.append(''.join(d))
    return out


def curve(a, b, bend=0.18, cls='sea'):
    """Quadratic curve from a to b (lon, lat), bowed sideways by a fraction of its length."""
    ax, ay, bx, by = x(a[0]), y(a[1]), x(b[0]), y(b[1])
    mx, my = (ax + bx) / 2, (ay + by) / 2
    dx, dy = bx - ax, by - ay
    cx, cy = mx - dy * bend, my + dx * bend
    return f'<path class="{cls}" d="M{ax:.1f} {ay:.1f} Q{cx:.1f} {cy:.1f} {bx:.1f} {by:.1f}"/>'


def dot(p, label, dx=7, dy=4, anchor='start'):
    return (f'<circle class="site" cx="{x(p[0]):.1f}" cy="{y(p[1]):.1f}" r="3.2"/>'
            f'<text class="lbl" x="{x(p[0]) + dx:.1f}" y="{y(p[1]) + dy:.1f}" text-anchor="{anchor}">{label}</text>')


def region(p, rx, ry, label, dy=0):
    return (f'<ellipse class="region" cx="{x(p[0]):.1f}" cy="{y(p[1]):.1f}" rx="{rx}" ry="{ry}"/>'
            f'<text class="region-lbl" x="{x(p[0]):.1f}" y="{y(p[1]) + dy:.1f}" text-anchor="middle">{label}</text>')


def build():
    site = json.loads((ROOT / 'docs/data/site.json').read_text())
    coast = ''.join(f'<path class="coast" d="{d}"/>' for d in coast_paths(site['coast']))
    sunda, sahul, java = (109, 1), (134, -20), (110, -7)
    n_aus, s_asia, e_africa, peru = (131, -12), (77, 9), (44, -3), (-80, -8)
    gt, olmec, ohio, brazil = (38.9, 37.2), (-94.8, 17.8), (-83.4, 39.0), (-63.5, -10)
    asia_main, china = (104, 22), (112, 30)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H + LEGEND}" width="{W}" height="{H + LEGEND}" role="img" aria-labelledby="t d">',
        '<title id="t">Movements claimed in Fenton\'s thread</title>',
        '<desc id="d">A world map centred on the Pacific with arrows for the movements Bruce R. Fenton claims: into Oceania about 900,000 years ago, back into Asia and Africa, a maritime expansion from Island Southeast Asia by 40,000 years ago reaching northern Australia, southern Asia, Africa and South America, and later routes to Göbekli Tepe and northwards through the Americas.</desc>',
        '<style>'
        'text{font-family:"IBM Plex Mono",Menlo,Consolas,monospace;fill:#4c453a}'
        '.coast{fill:none;stroke:#cbbfa8;stroke-width:.8;stroke-linejoin:round}'
        '.site{fill:#9a5b33}.lbl{font-size:10.5px;fill:#201b12}'
        '.region{fill:#9a5b33;fill-opacity:.09;stroke:#9a5b33;stroke-opacity:.5;stroke-dasharray:3 3}'
        '.region-lbl{font-size:10px;fill:#9a5b33;letter-spacing:.06em;text-transform:uppercase}'
        'path.deep{fill:none;stroke:#5d6672;stroke-width:1.6;stroke-dasharray:5 4;marker-end:url(#a-deep)}'
        'path.sea{fill:none;stroke:#9a5b33;stroke-width:1.9;marker-end:url(#a-sea)}'
        'path.late{fill:none;stroke:#47705f;stroke-width:1.9;marker-end:url(#a-late)}'
        '.key{font-size:10.5px}.note{font-size:9.5px;fill:#877e6c}'
        '</style>',
        '<defs>'
        + ''.join(f'<marker id="a-{k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>'
                  for k, c in [('deep', '#5d6672'), ('sea', '#9a5b33'), ('late', '#47705f')])
        + '</defs>',
        f'<rect width="{W}" height="{H + LEGEND}" fill="#f6f1e8"/><line x1="0" y1="{H}" x2="{W}" y2="{H}" stroke="#d9d0be"/>',
        coast,
        region(sunda, 62, 40, 'Sunda shelf', 0).replace(f'x="{x(sunda[0]):.1f}" y="{y(sunda[1]):.1f}"', f'x="{x(87):.1f}" y="{y(-11):.1f}"'),
        region((136, -22), 78, 62, 'Sahul', 0).replace(f'x="{x(136):.1f}" y="{y(-22):.1f}"', f'x="{x(150):.1f}" y="{y(-38):.1f}"'),
        # deep time (claimed): into Oceania c. 900 kya; back-migration c. 800 kya onward
        curve(java, sahul, -0.25, 'deep'), curve((128, -8), asia_main, 0.22, 'deep'), curve((95, 12), (41, 9), -0.1, 'deep'),
        # maritime culture (claimed): by 40 kya, reach of Island Southeast Asia
        curve(sunda, n_aus, 0.25, 'sea'), curve(sunda, s_asia, -0.2, 'sea'), curve((72, 4), (42, -7), 0.15, 'sea'),
        curve((128, 2), peru, -0.13, 'sea'),
        # after the sea-level rise (claimed): Anatolia; northwards through the Americas
        curve((96, 7), gt, -0.18, 'late'), curve(peru, olmec, -0.2, 'late'), curve(olmec, ohio, -0.2, 'late'),
        dot(gt, 'Göbekli Tepe, c. 9500 BCE', -7, -7, 'end'),
        dot((133.8, -12.6), 'Arnhem Land', 8, -3), dot((126, -15.5), 'Kimberley', -8, 12, 'end'), dot((133.9, -23.7), 'Central Australia', 8, 4),
        dot((121, 12.9), 'Mindoro · Timor-Leste, 40,000 BP', 8, -2),
        dot(peru, 'Peru', -8, 4, 'end'), dot(brazil, 'Karitiana, Suruí', -8, 16, 'end'), dot(olmec, 'Olmec heads', -8, 2, 'end'), dot(ohio, 'Serpent Mound', -8, 2, 'end'),
        # legend
        f'<g transform="translate(20 {H + 16})">'
        '<path class="deep" d="M0 4h30"/><text class="key" x="40" y="8">c. 900,000–800,000 years ago: into Oceania, then back into Asia and Africa (his 2017 model)</text>'
        '<path class="sea" d="M0 22h30"/><text class="key" x="40" y="26">by 40,000 years ago: a maritime culture of Island Southeast Asia and its claimed reach</text>'
        '<path class="late" d="M0 40h30"/><text class="key" x="40" y="44">after the sea-level rise: symbols carried to Anatolia; the Rainbow Serpent northwards</text>'
        f'<text class="note" x="{W - 40}" y="26" text-anchor="end">Arrows and dates are the thread\'s claims,</text>'
        f'<text class="note" x="{W - 40}" y="40" text-anchor="end">drawn by this project. Modern coastlines (Natural Earth).</text>'
        '</g>',
        '</svg>',
    ]
    out = ROOT / 'docs/img/fenton-map.svg'
    out.write_text('\n'.join(parts) + '\n')
    print(out.relative_to(ROOT), out.stat().st_size, 'bytes')


if __name__ == '__main__':
    build()
