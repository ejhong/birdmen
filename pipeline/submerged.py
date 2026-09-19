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
    source_html=''.join(f'<li><span class="micro">{esc(s["kind"])}</span><h3>{a(s["url"],s["title"])}</h3><p>{esc(s["note"])}</p></li>' for s in data['sources'])
    locations=''.join(f'<a href="#project-{p["id"]}" data-project-lat="{p["lat"]}" data-project-lon="{p["lon"]}" data-project-number="{i+1}"><span>{i+1:02d}</span> {esc(p["name"])}</a>' for i,p in enumerate(data['projects']))
    body=f'''<main id="main"><header class="water-hero"><div class="cat-wrap"><div class="micro">A second inquiry · Submerged landscapes</div><h1>Another world<br><em>lies offshore.</em></h1><div class="water-intro"><p>Rivers, coastlines, places people might have called home. As the sea rose, a vast part of the human landscape changed.</p><p>What survives beneath the water—and what could we learn from data already within reach?</p></div><nav aria-label="In this programme"><a href="#landscape">Explore the shelves ↓</a><a href="#projects">Discoveries &amp; projects</a><a href="#data">Open data</a><a href="#programme">A research programme</a></nav></div></header>
<section id="landscape" class="water-explorer cat-wrap"><div class="section-top"><div><div class="micro">Begin with the shape of the land</div><h2>Look beyond today’s coast.</h2></div><p>Actual relief data. A depth experiment.<br><b>No ancient date is assigned to this map.</b></p></div>
<div class="water-tools" id="water-tools" hidden><div class="region-buttons" aria-label="Map region">{''.join(f'<button type="button" data-water-region="{g["id"]}" aria-pressed="{str(g["id"]=="world").lower()}">{esc(g["label"])}</button>' for g in manifest['grids'])}</div><label class="depth-control" for="water-depth">Highlight down to <output id="depth-output">60 m</output><input type="range" id="water-depth" min="0" max="120" step="5" value="60" aria-describedby="depth-explanation"></label></div>
<div class="water-map-pair"><figure><div class="map-overline">Modern elevation baseline</div><canvas id="modern-canvas" hidden role="img" aria-label="Modern relief map"></canvas><img class="water-fallback" id="modern-fallback" src="img/submerged/world-modern.svg" alt="World relief from NOAA ETOPO1; present non-negative elevations in light green, negative elevations in blue"><figcaption>Present relief · an older global compilation</figcaption></figure><figure><div class="map-overline">Depth screen · <span id="scenario-title">0 to −60 m</span></div><canvas id="depth-canvas" hidden role="img" aria-label="Relief map with the selected shallow depth interval highlighted"></canvas><img class="water-fallback" id="depth-fallback" src="img/submerged/world-depth.svg" alt="The same world relief with elevations from minus 60 metres to zero highlighted in gold; no date assigned"><figcaption>Gold = cells within the selected depth interval</figcaption></figure></div>
<div class="water-map-legend"><span>Modern non-negative elevations</span><span>Selected shallow elevations</span><span>Deeper water</span></div><p id="water-status" role="status" class="water-map-status">World view · static 60 m depth screen. Interactive controls require JavaScript.</p><nav class="water-project-locations" aria-label="Projects in the mapped region">{locations}</nav><p class="water-map-status">Numbered markers locate the records below, approximately. The map uses an equirectangular view; areas are not directly comparable.</p><p id="depth-explanation" class="depth-explanation">This changes a threshold on <b>modern relief</b>. It does not account for land movement, sediment burial, erosion, ice cover or water connectivity. Gold can include inland depressions. It shows where to ask better questions, not where ancient people lived.</p><details class="water-method"><summary>What would a map of 12,000 years ago require?</summary><p>A dated regional sea-level model, the elevation of the former land surface and uncertainty for both. A single global “lower the water” setting cannot recover that history. The Last Glacial Maximum was earlier than 12,000 years ago; their shorelines must not be interchanged.</p><p>The North Sea’s published peat records and land-motion corrections are a promising next step. Here, “12,000 years BP” would mean 12,000 years before 1950—approximately 10,050 BCE—not the date of every inundation.</p><p class="water-sources">{refs(['lambeck','northsea-peats','northsea-data'])}</p><p class="water-sources">Prototype: NOAA ETOPO1 (2009), subsampled at 20′ globally and 2′–6′ regionally. <a href="data/submerged/grids.json">Exact requests, extents, hashes and limitations</a>. Source NetCDF files are retained in the repository.</p></details><noscript><p class="water-map-status">The maps above remain readable without scripting. All projects, datasets and sources follow below.</p></noscript></section>
<section id="scope" class="water-scope cat-wrap"><div><div class="micro">The initial assessment</div><h2>The missing landscape is real.<br>Its contents are a research question.</h2></div><div><p>Submerged archaeological sites and drowned land surfaces are documented. They give us good reasons to search beyond modern coastlines. They do not establish that most important evidence—or a particular lost civilisation—must be there. {refs(['pavlopetri','murujuga'])}</p><p>The productive question is where <b>past habitability, preservation and usable survey data</b> overlap. That turns a vast mystery into investigations we can actually attempt.</p><p class="water-sources">First assessment · checked {data['edition']}. Active projects, past fieldwork and disputed interpretations are labelled separately.</p></div></section>
<section id="projects" class="water-section cat-wrap"><div class="section-top"><div><div class="micro">The field, in six starting places</div><h2>What has come into view?</h2></div><p>Evidence ranges from mapped settlements to prospective landscapes. The difference is part of the story.</p></div><div class="water-projects">{projects}</div></section>
<section id="data" class="water-section water-data-section"><div class="cat-wrap"><div class="section-top"><div><div class="micro">An inventory for investigation</div><h2>Data we can begin with.</h2></div><p>These are concrete entry points, with access and limitations recorded. Finding data is the beginning of analysis.</p></div><div class="water-data-grid">{datasets}</div></div></section>
<section id="programme" class="water-section cat-wrap"><div class="section-top"><div><div class="micro">From an idea to a research programme</div><h2>Start with one defensible landscape.</h2></div><p>Our initial choice: the North Sea. This is an editorial assessment of feasibility, based on the sources above.</p></div><ol class="water-steps"><li><b>Reconstruct before searching.</b><p>Reproduce one dated regional shoreline with uncertainty, using the published sea-level data and an appropriate former land surface. Compare it explicitly with the modern-depth shortcut.</p></li><li><b>Find where the data are strongest.</b><p>Map survey footprints, resolution, interpolation and sediment cover. Identify gaps before interpreting a blank map as archaeological absence.</p></li><li><b>Ask a small, testable question.</b><p>For example: which mapped former freshwater margins combine a plausible occupation window, preserved sediments and accessible detailed survey data?</p></li><li><b>Make every candidate answerable.</b><p>Use independent surveys and geological alternatives to check proposed features. AI can help catalogue patterns; validation must distinguish natural landforms, survey artefacts and human activity.</p></li></ol><div class="water-programme-links"><a href="https://github.com/ejhong/birdmen/blob/main/research/submerged/PROGRAMME.md">Read the programme and next stages ↗</a><a href="data/submerged/register.json">Download the project &amp; data register ↗</a><a href="https://github.com/ejhong/birdmen/issues/new">Suggest a project, dataset or research question ↗</a></div></section>
<section id="sources" class="sources-section cat-wrap"><div class="section-top"><div><div class="micro">Follow the evidence</div><h2>Sources for this assessment.</h2></div><p>No archaeological discoveries or dated shorelines were inferred from this demonstrator. Records checked {data['edition']}.</p></div><ol class="dossier-sources">{source_html}</ol></section></main>'''
    result=shell('Submerged worlds','Explore drowned landscapes, underwater archaeology, open bathymetry and a new research programme.',body,extra='<link rel="stylesheet" href="submerged.css"><script type="module" src="submerged.js"></script>')
    return result.replace('class="catalogue-site"','class="catalogue-site submerged-site"').replace('href="catalogue.html#about"','href="submerged.html#scope"').replace('href="data/catalogue.json"','href="data/submerged/register.json"')


def outputs():
    data=json.loads((ROOT/'research/submerged/register.json').read_text())
    manifest=json.loads((ROOT/'research/submerged/grids.json').read_text())
    validate(data,manifest)
    world=next(g for g in manifest['grids'] if g['id']=='world')
    return {DOCS/'submerged.html':page(data,manifest),DOCS/'data/submerged/register.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',DOCS/'data/submerged/grids.json':json.dumps(manifest,indent=2)+'\n',DOCS/'img/submerged/world-modern.svg':preview(world,0,data['projects']),DOCS/'img/submerged/world-depth.svg':preview(world,60,data['projects'])}
