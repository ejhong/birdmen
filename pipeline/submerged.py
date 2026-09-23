"""Publish the submerged-landscape assessment from its source registers."""
import hashlib
import json
from pathlib import Path
import struct
import re
from urllib.parse import urlsplit
try:
    from pipeline.catalogue import esc, a, shell
except ModuleNotFoundError:
    from catalogue import esc, a, shell

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'


def validate(data,manifest):
    source_ids={s['id'] for s in data['sources']}
    if len(source_ids)!=len(data['sources']):raise ValueError('Duplicate submerged source')
    grids={g['id']:g for g in manifest['grids']}
    if len(grids)!=len(manifest['grids']) or 'world' not in grids:raise ValueError('Invalid grid identifiers')
    for s in data['sources']:
        if urlsplit(s['url']).scheme!='https' or not urlsplit(s['url']).netloc:raise ValueError('Unsafe source URL')
        if not s.get('checked') or not s.get('note'):raise ValueError('Incomplete submerged source')
    for key in ['projects','datasets']:
        if len({v['id'] for v in data[key]})!=len(data[key]):raise ValueError('Duplicate submerged record')
        for r in data[key]:
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',r['id']):raise ValueError('Unsafe record identifier')
            if not r['sources'] or not set(r['sources'])<=source_ids:raise ValueError('Unsupported submerged record')
            if not r.get('limit'):raise ValueError('Missing evidence qualification')
    for p in data['projects']:
        if p['region'] not in grids or not (-90<=p['lat']<=90 and -180<=p['lon']<=180):raise ValueError('Invalid project location')
    for g in manifest['grids']:
        source=(ROOT/g['source_path']).resolve();output=(DOCS/g['path']).resolve()
        if not source.is_relative_to(ROOT/'data/submerged') or not output.is_relative_to(DOCS/'data/submerged'):raise ValueError('Unsafe relief path')
        raw=source.read_bytes();binary=output.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=g['source_sha256'] or hashlib.sha256(binary).hexdigest()!=g['sha256']:
            raise ValueError('Relief data changed')
        if len(binary)!=g['width']*g['height']*2:raise ValueError('Incorrect relief grid dimensions')
        if not (-180<=g['west']<g['east']<=180 and -90<=g['south']<g['north']<=90):raise ValueError('Invalid relief extent')


def preview(g,depth,projects=()):
    values=struct.unpack('<'+'h'*(g['width']*g['height']),(DOCS/g['path']).read_bytes())
    paths={1:[],2:[]}
    def classify(z):return 0 if z==g['nodata'] else 1 if z>=0 else 2 if z>=-depth else 0
    for y in range(g['height']):
        row=values[y*g['width']:(y+1)*g['width']]
        start=0;cat=classify(row[0])
        for x in range(1,g['width']+1):
            nxt=classify(row[x]) if x<g['width'] else -1
            if nxt!=cat:
                if cat:paths[cat].append(f'M{start} {y}h{x-start}v1H{start}z')
                start=x;cat=nxt
    markers=[]
    for i,p in enumerate(projects):
        if not (g['west']<=p['lon']<=g['east'] and g['south']<=p['lat']<=g['north']):continue
        x=(p['lon']-g['west'])/(g['east']-g['west'])*(g['width']-1)
        y=(g['north']-p['lat'])/(g['north']-g['south'])*(g['height']-1)
        markers.append(f'<g><title>{esc(p["name"])} · {esc(p["precision"])}</title><circle cx="{x:.1f}" cy="{y:.1f}" r="12.7" fill="#f3ecda" stroke="#173b45"/><text x="{x:.1f}" y="{y+5:.1f}" text-anchor="middle" font-family="monospace" font-size="16" fill="#173b45">{i+1}</text></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {g['width']} {g['height']}" role="img"><title>NOAA ETOPO1 modern relief with elevations between minus {depth} metres and zero highlighted</title><desc>Modern land in light green, shallow negative elevations in gold, deeper water in blue. This is a depth screen, not a reconstruction of a dated ancient coastline. Inland depressions are not excluded. Numbered markers are approximate project locations.</desc><rect width="100%" height="100%" fill="#173b45"/><path fill="#d6d4b9" d="{''.join(paths[1])}"/><path fill="#d4a763" d="{''.join(paths[2])}"/>{''.join(markers)}</svg>'''


def page(data,manifest):
    sources={s['id']:s for s in data['sources']}
    def refs(ids):return ' · '.join(a(sources[id]['url'],sources[id]['title']) for id in ids)
    projects=''.join(f'''<article class="water-project" id="project-{p['id']}"><div class="project-number">{i+1:02d}</div><div><div class="micro">{esc(p['status'])}</div><h3>{esc(p['name'])}</h3><p class="project-lead">{esc(p['label'])}</p><p>{esc(p['finding'])}</p><details><summary>Evidence, limits &amp; next investigation</summary><dl><dt>Programme / record</dt><dd>{esc(p['activity'])}</dd><dt>What remains open</dt><dd>{esc(p['limit'])}</dd><dt>A useful next step</dt><dd>{esc(p['next'])}</dd><dt>Map precision</dt><dd>{esc(p['precision'])}</dd></dl></details><p class="water-sources">{refs(p['sources'])}</p><a class="project-map-link" href="submerged.html?region={p['region']}&amp;depth=60#landscape" data-region-link="{p['region']}">Explore the regional depth view ↗</a></div></article>''' for i,p in enumerate(data['projects']))
    datasets=''.join(f'''<article class="water-dataset" id="dataset-{d['id']}"><div class="micro">{esc(d['coverage'])}</div><h3>{esc(d['name'])}</h3><p>{esc(d['use'])}</p><details><summary>Resolution, access &amp; limitations</summary><dl><dt>Resolution</dt><dd>{esc(d['resolution'])}</dd><dt>Access checked</dt><dd>{esc(d['access'])}</dd><dt>Limits</dt><dd>{esc(d['limit'])}</dd></dl></details><p class="water-sources">{refs(d['sources'])}</p></article>''' for d in data['datasets'])
    source_html=''.join(f'<li><span class="micro">{esc(s["kind"])}</span><h3>{a(s["url"],s["title"])}</h3></li>' for s in data['sources'])
    locations=''.join(f'<a href="#project-{p["id"]}" data-project-lat="{p["lat"]}" data-project-lon="{p["lon"]}" data-project-number="{i+1}"><span>{i+1:02d}</span> {esc(p["name"])}</a>' for i,p in enumerate(data['projects']))
    body=f'''<main id="main"><header class="water-hero"><div class="cat-wrap"><div class="micro">A second inquiry · Submerged landscapes</div><h1>Another world<br><em>lies offshore.</em></h1><div class="water-intro"><p>The sea covered coastlines, rivers and places people once lived.</p><p>What survives—and what can today’s data reveal?</p></div><nav aria-label="In this programme"><a href="#landscape">Explore the shelves ↓</a><a href="#experiment">The first data test</a><a href="#projects">Discoveries &amp; projects</a><a href="#data">Open data</a><a href="#programme">A research programme</a></nav></div></header>
<section id="landscape" class="water-explorer cat-wrap"><div class="section-top"><div><div class="micro">Begin with the shape of the land</div><h2>Look beyond today’s coast.</h2></div><p>Modern relief · depth experiment.<br><b>No ancient date assigned.</b></p></div>
<div class="water-tools" id="water-tools" hidden><div class="region-buttons" aria-label="Map region">{''.join(f'<button type="button" data-water-region="{g["id"]}" aria-pressed="{str(g["id"]=="world").lower()}">{esc(g["label"])}</button>' for g in manifest['grids'])}</div><label class="depth-control" for="water-depth">Highlight down to <output id="depth-output">60 m</output><input type="range" id="water-depth" min="0" max="120" step="5" value="60" aria-describedby="depth-explanation"></label></div>
<div class="water-map-pair"><figure><div class="map-overline">Modern elevation baseline</div><canvas id="modern-canvas" hidden role="img" aria-label="Modern relief map"></canvas><img class="water-fallback" id="modern-fallback" src="img/submerged/world-modern.svg" alt="World relief from NOAA ETOPO1; present non-negative elevations in light green, negative elevations in blue"><figcaption>Present relief · an older global compilation</figcaption></figure><figure><div class="map-overline">Depth screen · <span id="scenario-title">0 to −60 m</span></div><canvas id="depth-canvas" hidden role="img" aria-label="Relief map with the selected shallow depth interval highlighted"></canvas><img class="water-fallback" id="depth-fallback" src="img/submerged/world-depth.svg" alt="The same world relief with elevations from minus 60 metres to zero highlighted in gold; no date assigned"><figcaption>Gold = cells within the selected depth interval</figcaption></figure></div>
<div class="water-map-legend"><span>Modern non-negative elevations</span><span>Selected shallow elevations</span><span>Deeper water</span></div><p id="water-status" role="status" class="water-map-status">World view · static 60 m depth screen. Interactive controls require JavaScript.</p><nav class="water-project-locations" aria-label="Projects in the mapped region">{locations}</nav><p class="water-map-status">Markers locate project regions. Map areas are not directly comparable.</p><p id="depth-explanation" class="depth-explanation">Gold marks a depth interval on <b>modern relief</b>, including inland depressions. Land motion, sediment, erosion and past ice cover are not modelled. It is not an ancient coastline.</p><details class="water-method"><summary>What would a map of 12,000 years ago require?</summary><p>A dated regional sea-level model and a reconstructed former land surface, with uncertainty. The Last Glacial Maximum was earlier than 12,000 years ago; those shorelines differ.</p><p>North Sea peat records offer a starting point. “12,000 years BP” means before 1950, approximately 10,050 BCE; inundation dates vary by place.</p><p class="water-sources">{refs(['lambeck','northsea-peats','northsea-data'])}</p><p class="water-sources">Prototype: NOAA ETOPO1 (2009), subsampled at 20′ globally and 2′–6′ regionally. <a href="data/submerged/grids.json">Exact requests, extents, hashes and limitations</a>. Source NetCDF files are retained in the repository.</p></details><noscript><p class="water-map-status">The maps above remain readable without scripting. All projects, datasets and sources follow below.</p></noscript></section>
<section id="scope" class="water-scope cat-wrap"><div><div class="micro">The initial assessment</div><h2>The missing landscape is real.<br>Its contents are a research question.</h2></div><div><p>Documented submerged sites justify the search. How much evidence survives, and what it contains, remain open questions. {refs(['pavlopetri','murujuga'])}</p><p>Start where <b>past habitability, preservation and usable surveys</b> overlap.</p><p class="water-sources">Assessment updated {data['edition']}.</p></div></section>
<section id="experiment" class="water-scope cat-wrap"><div><div class="micro">New · a test on actual survey data</div><h2>What a coarse grid erases.</h2></div><div><p>The Baltic alignment’s 0.5 m survey lets us measure how averaging removes fine relief. At 115 m, this test retains just <b>0.3% of local relief variance</b>.</p><p>A data-resolution result, not an AI detection or a wall-recovery score.</p><a class="quiet-action" href="bathymetry-lab.html">Inspect the survey and measurements ↗</a></div></section>
<section id="projects" class="water-section cat-wrap"><div class="section-top"><div><div class="micro">The field, in six starting places</div><h2>What has come into view?</h2></div><p>Discoveries, disputed claims and landscapes to investigate.</p></div><div class="water-projects">{projects}</div></section>
<section id="data" class="water-section water-data-section"><div class="cat-wrap"><div class="section-top"><div><div class="micro">An inventory for investigation</div><h2>Data we can begin with.</h2></div><p>Sources, access and resolution, checked before analysis.</p></div><div class="water-data-grid">{datasets}</div></div></section>
<section id="programme" class="water-section cat-wrap"><div class="section-top"><div><div class="micro">The research programme</div><h2>Two practical starting points.</h2></div><p>North Sea landscape reconstruction.<br>Baltic feature detectability.</p></div><ol class="water-steps"><li><b>Reconstruct a dated landscape.</b><p>Combine regional sea-level records, land motion and former surfaces. Keep uncertainty visible.</p></li><li><b>Map where the evidence survives.</b><p>Check survey coverage, sediment burial and resolution before interpreting an empty map.</p></li><li><b>Benchmark the observer.</b><p>Use labelled structures and natural alternatives from separate surveys. Compare AI with simple detection methods.</p></li><li><b>Test candidate sites independently.</b><p>Prioritise freshwater margins and preserved surfaces, then validate with complementary surveys and archaeology.</p></li></ol><div class="water-programme-links"><a href="data/next-tests.md">Concrete next tests ↗</a><a href="https://github.com/ejhong/birdmen/blob/main/research/submerged/PROGRAMME.md">Full programme ↗</a><a href="data/submerged/register.json">Project &amp; data register ↗</a></div></section>
<section id="sources" class="sources-section cat-wrap"><div class="section-top"><div><div class="micro">Follow the evidence</div><h2>Sources for this assessment.</h2></div><p>Source notes and checks: <a href="data/submerged/register.json">full register</a>.</p></div><ol class="dossier-sources">{source_html}</ol></section></main>'''
    result=shell('Submerged worlds','Explore drowned landscapes, underwater archaeology, open bathymetry and a new research programme.',body,extra='<link rel="stylesheet" href="submerged.css"><script type="module" src="submerged.js"></script>',current='submerged.html')
    return result.replace('class="catalogue-site"','class="catalogue-site submerged-site"').replace('href="catalogue.html#about"','href="submerged.html#scope"').replace('href="data/catalogue.json"','href="data/submerged/register.json"')


def outputs():
    data=json.loads((ROOT/'research/submerged/register.json').read_text())
    manifest=json.loads((ROOT/'research/submerged/grids.json').read_text())
    validate(data,manifest)
    world=next(g for g in manifest['grids'] if g['id']=='world')
    return {DOCS/'submerged.html':page(data,manifest),DOCS/'data/submerged/register.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',DOCS/'data/submerged/grids.json':json.dumps(manifest,indent=2)+'\n',DOCS/'img/submerged/world-modern.svg':preview(world,0,data['projects']),DOCS/'img/submerged/world-depth.svg':preview(world,60,data['projects'])}
