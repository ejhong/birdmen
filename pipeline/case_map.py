"""Draw geographic context from the repo's Natural Earth coastlines. No route implied."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'data/raw/ne_110m_coastline.geojson').read_text())


def xy(lon, lat):
    return 30 + (lon + 180) / 360 * 1040, 25 + (85 - lat) / 170 * 470


out = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 520" role="img" aria-labelledby="title desc">
<title id="title">Göbekli Tepe and Rapa Nui in geographic context</title>
<desc id="desc">Göbekli Tepe lies in southeastern Anatolia; Rapa Nui lies in the southeastern Pacific west of South America. Only locations are shown. No transmission route is asserted.</desc>
<rect width="1100" height="520" fill="#efe8da"/>
<g fill="none" stroke="#c6bcaa" stroke-width="1.2">''']
for feature in data['features']:
    geometry = feature['geometry']
    lines = [geometry['coordinates']] if geometry['type'] == 'LineString' else geometry['coordinates']
    for line in lines:
        # A move at the date line avoids an erroneous line across the whole map.
        parts = []
        previous = None
        for lon, lat in line:
            x, y = xy(lon, lat)
            command = 'M' if previous is None or abs(lon - previous) > 180 else 'L'
            parts.append(f'{command}{x:.1f},{y:.1f}')
            previous = lon
        out.append('<path d="' + ' '.join(parts) + '"/>')
out.append('</g>')
for lon, lat, label, sub, dx, dy in [(38.92, 37.22, 'Göbekli Tepe', 'SOUTHEASTERN ANATOLIA', 18, -18), (-109.35, -27.12, 'Rapa Nui', 'SOUTHEASTERN PACIFIC', -24, -32)]:
    x, y = xy(lon, lat)
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#9a5b33"/><circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="none" stroke="#9a5b33" stroke-opacity=".35"/>')
    out.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" fill="#302a20" font-family="Georgia,serif" font-size="25">{label}</text><text x="{x+dx:.1f}" y="{y+dy+19:.1f}" fill="#736654" font-family="monospace" font-size="11" letter-spacing="1">{sub}</text>')
out.append('<text x="35" y="496" fill="#736654" font-family="monospace" font-size="11">GEOGRAPHIC CONTEXT · APPROXIMATE LOCATIONS · NO TRANSMISSION ROUTE SHOWN</text></svg>')
(ROOT / 'docs/img/case/locations.svg').write_text('\n'.join(out) + '\n')
