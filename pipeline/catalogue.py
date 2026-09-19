"""Validate and publish the curated catalogue. No network or model calls.

The JSON register is the editorial source. HTML dossiers and gallery cards are
generated from it, and remain readable without JavaScript.
"""
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
STATUS = {'examined': 'Evidence examined', 'source-check': 'Sources partly checked',
          'lead': 'Research lead', 'corrected': 'Claim corrected'}
DIFFUSION = {'unestablished': 'No route established in this review',
             'unassessed': 'Transmission not yet assessed', 'plausible': 'Regional transmission remains possible',
             'local': 'Documented local context', 'documented': 'Independent contact evidence'}


def esc(value):
    return html.escape(str(value), quote=True)


def href(value, prefix=''):
    return value if value.startswith(('https://', 'http://', '#')) else prefix + value


def a(url, label, prefix=''):
    return f'<a href="{esc(href(url, prefix))}">{esc(label)}</a>'


def index(data):
    return {key: {row['id']: row for row in data[key]} for key in
            ('sources', 'places', 'media', 'entities', 'groups', 'claims', 'motifs', 'cultures')}


def validate(data, check_files=True):
    idx = index(data)
    for key, records in idx.items():
        if len(records) != len(data[key]):
            raise ValueError(f'Duplicate {key}')
        if any(not re.fullmatch(r'[a-z0-9]+(?:[-_][a-z0-9]+)*', id) for id in records):
            raise ValueError(f'Unsafe identifier in {key}')

    def refs(row, field, target, required=True):
        values = row.get(field, [])
        if (required and not values) or len(set(values)) != len(values) or not set(values) <= set(idx[target]):
            raise ValueError(f'Invalid {field} in {row["id"]}')

    for s in data['sources']:
        if not all(s.get(k) for k in ['title', 'url', 'kind', 'checked', 'note']):
            raise ValueError('Incomplete source')
    for row in data['sources'] + data['media']:
        url = row['url']
        parsed = urlsplit(url)
        if (parsed.scheme and parsed.scheme not in ('http', 'https')) or url.startswith('//') or '\\' in url:
            raise ValueError('Unsafe source URL')
        if not parsed.scheme and (not (DOCS / parsed.path).resolve().is_relative_to(DOCS) or not (DOCS / parsed.path).exists()):
            raise ValueError(f'Missing local source {url}')
    for m in data['media']:
        path = (DOCS / m['path']).resolve()
        if not path.is_relative_to(DOCS) or not path.is_file():
            raise ValueError('Missing or unsafe media path')
        if not all(m.get(k) for k in ['credit', 'rights', 'caption', 'alt', 'kind', 'transformation', 'sha256']):
            raise ValueError('Incomplete media provenance')
        if check_files and hashlib.sha256(path.read_bytes()).hexdigest() != m['sha256']:
            raise ValueError(f'Media changed: {m["id"]}')
    for p in data['places']:
        if not -90 <= p['lat'] <= 90 or not -180 <= p['lon'] <= 180 or p['precision'] not in ('site', 'region'):
            raise ValueError('Invalid map location')
    for e in data['entities']:
        refs(e, 'sources', 'sources')
        if e['culture'] not in idx['cultures'] or e['id'] not in idx['cultures'][e['culture']]['members']:
            raise ValueError('Inconsistent culture membership')
        if e['media'] is not None and e['media'] not in idx['media']:
            raise ValueError('Missing media reference')
        refs(e, 'alternate_media', 'media', False)
        if e['media'] in e.get('alternate_media', []):
            raise ValueError('Repeated primary image in alternate views')
        if e['place'] is not None and e['place'] not in idx['places']:
            raise ValueError('Missing place reference')
        if not e['dates'] or not e.get('physical_id'):
            raise ValueError('Missing entity identity or dates')
        for d in e['dates']:
            start, end = d['start'], d['end']
            if (start is None) != (end is None):
                raise ValueError('Incomplete date interval')
            if start is not None and (type(start) is not int or type(end) is not int or start == 0 or end == 0 or start > end):
                raise ValueError('Invalid date interval')
            if start is not None and d['source'] not in idx['sources']:
                raise ValueError('Unsupported date')
            if not d.get('note') or not d.get('kind') or not d.get('label'):
                raise ValueError('Missing date qualification')
    for culture in data['cultures']:
        refs(culture, 'members', 'entities')
        if any(idx['entities'][id]['culture'] != culture['id'] for id in culture['members']):
            raise ValueError('Inconsistent culture membership')
    for g in data['groups']:
        refs(g, 'members', 'entities')
        refs(g, 'sources', 'sources')
        refs(g, 'cultures', 'cultures')
        if set(g['cultures']) != {idx['entities'][id]['culture'] for id in g['members']} or not g.get('membership_reason'):
            raise ValueError('Inconsistent group membership')
    for c in data['claims']:
        for field, target in [('members', 'entities'), ('groups', 'groups'), ('cultures', 'cultures'), ('motifs', 'motifs'), ('sources', 'sources')]:
            refs(c, field, target)
        refs(c, 'controls', 'claims', False)
        if set(c['members']) != {id for gid in c['groups'] for id in idx['groups'][gid]['members']}:
            raise ValueError(f'Claim/group membership differs: {c["id"]}')
        if set(c['cultures']) != {idx['entities'][id]['culture'] for id in c['members']}:
            raise ValueError('Claim/culture membership differs')
        if c['status'] not in STATUS or c['kind'] not in ('claim', 'control') or c['diffusion']['status'] not in DIFFUSION:
            raise ValueError('Invalid editorial status')
        if c['origin']['source'] not in idx['sources'] or not c['origin']['note']:
            raise ValueError('Missing proposing source')
        if any(idx['claims'][id]['kind'] != 'control' for id in c['controls']):
            raise ValueError('Control link points to a claim')
        if c.get('parent') and (c['parent'] == c['id'] or c['parent'] not in idx['claims'] or idx['claims'][c['parent']].get('parent')):
            raise ValueError('Invalid comparison parent')
        if not all(c.get(k) for k in ['features', 'differences', 'anomaly', 'next_steps', 'review']):
            raise ValueError('Incomplete comparison')


def representative(group, idx):
    return idx['entities'][group['members'][0]]


def picture(e, idx, prefix='', large=False):
    if e['media']:
        m = idx['media'][e['media']]
        return f'<img src="{esc(prefix + m["path"])}" alt="{esc(m["alt"])}" loading="lazy" decoding="async">'
    label = 'Account · editorial paraphrase' if e['kind'] == 'account' else 'Source record · image pending' if e['kind'] == 'monument' else 'Research evidence'
    return f'<div class="text-specimen"><span>{label}</span><p>{esc(e["text"] or e["label"])}</p><i aria-hidden="true">∿</i></div>'


def card(c, idx):
    groups = [idx['groups'][id] for id in c['groups']]
    # A local control has one group, so show two of its members as a local set.
    reps = [representative(g, idx) for g in groups] if len(groups) > 1 else [idx['entities'][id] for id in groups[0]['members'][:2]]
    images = ''.join(f'<div class="card-specimen">{picture(e, idx)}</div>' for e in reps[:3])
    tags = ' · '.join(idx['motifs'][id]['label'] for id in c['motifs'] if id != 'contact') or 'Contact evidence'
    group_names = ' ↔ '.join(g['label'] for g in groups)
    count = len({idx['entities'][id]['physical_id'] for id in c['members']})
    return f'''<article class="catalogue-card" data-claim="{esc(c['id'])}" data-kind="{c['kind']}">
<a class="card-link" href="catalogue/{c['id']}.html"><div class="card-images images-{len(reps[:3])}">{images}<span class="open-arrow" aria-hidden="true">↗</span></div>
<div class="card-copy"><div class="card-kicker">{esc(tags)} <span>{'Context control' if c['kind'] == 'control' else STATUS[c['status']]}</span></div>
<h3>{esc(c['title'])}</h3><p>{esc(c['dek'])}</p><div class="card-groups">{esc(group_names)}</div>
<div class="card-foot">{len(groups)} {'group' if len(groups) == 1 else 'groups'} · {count} registered {'example' if count == 1 else 'examples'} <span>Explore →</span></div></div></a></article>'''


def shell(title, description, body, prefix='', extra=''):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Deep Memory</title><meta name="description" content="{esc(description)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}style.css"><link rel="stylesheet" href="{prefix}catalogue.css">{extra}</head>
<body class="catalogue-site"><a class="skip-link" href="#main">Skip to content</a>
<div class="cat-masthead cat-wrap"><a class="cat-brand" href="{prefix}index.html">Deep Memory<span>Clues to a deeper past</span></a><nav aria-label="Main navigation"><a href="{prefix}catalogue.html">The collection</a><a href="{prefix}submerged.html">Submerged worlds</a><a href="{prefix}research-review.html">Research</a></nav></div>
{body}
<footer class="cat-footer cat-wrap"><div>Deep Memory<span>A living collection. A question kept open.</span></div><p><a href="{prefix}catalogue.html#about">About this collection</a> · <a href="{prefix}data/catalogue.json">Download the register</a><br><a href="https://github.com/ejhong/birdmen">Research &amp; code</a> · <a href="https://github.com/ejhong/birdmen/issues/new">Contribute a source or correction</a></p></footer>
</body></html>'''


def dossier(c, idx):
    group_html = []
    for gid in c['groups']:
        g = idx['groups'][gid]
        members = []
        for eid in g['members']:
            e = idx['entities'][eid]
            p = idx['places'].get(e['place'])
            m = idx['media'].get(e['media'])
            date_html = ''.join(f'<li><b>{esc(d["label"])}</b><span>{esc(d["kind"])} · {esc(d["note"])} {a(idx["sources"][d["source"]]["url"], "Date source", "../") if d["source"] else ""}</span></li>' for d in e['dates'])
            credit = f'<p class="image-credit">{esc(m["kind"])} · {esc(m["credit"])}. {esc(m["rights"])}. {a(m["url"], "Image record", "../")}<br>{esc(m["transformation"])}</p>' if m else ''
            media_html = picture(e, idx, '../')
            if m:
                media_html = f'<a href="../{esc(m["path"])}" aria-label="Open full image: {esc(e["label"])}">{media_html}</a>'
            alternate_html = ''
            if e.get('alternate_media'):
                views = []
                for mid in e['alternate_media']:
                    alt = idx['media'][mid]
                    views.append(f'<figure><a href="../{esc(alt["path"])}"><img src="../{esc(alt["path"])}" alt="{esc(alt["alt"])}" loading="lazy"></a><figcaption>{esc(alt["caption"])}<br>{esc(alt["credit"])} · {esc(alt["rights"])} · {a(alt["url"], "Image record", "../")}<br>{esc(alt["transformation"])}</figcaption></figure>')
                alternate_html = f'<details class="alternate-views"><summary>Another view of this example</summary><p>Additional photographs help us see the surface. They do not add independent objects to this group.</p>{"".join(views)}</details>'
            members.append(f'''<article class="group-member" id="example-{esc(eid)}"><div class="member-image">{media_html}</div>
<div class="member-copy"><span class="micro">{esc(e['kind'])} · {esc(p['name'] if p else 'Place unresolved')}</span><h3>{esc(e['label'])}</h3>
<p>{esc(e['note'])}</p><details><summary>Dates, sources &amp; image record</summary><ul class="date-records">{date_html}</ul>{credit}<p class="micro">{' · '.join(a(idx['sources'][id]['url'], idx['sources'][id]['title'], '../') for id in e['sources'])}</p></details>{alternate_html}</div></article>''')
        group_html.append(f'<section class="dossier-group"><div class="group-heading"><div class="micro">{esc(" / ".join(idx["cultures"][id]["label"] for id in g["cultures"]))}</div><h2>{esc(g["label"])}</h2><p>{esc(g["description"])}</p><details><summary>Why these examples belong together</summary><p>{esc(g["membership_reason"])}</p></details></div>{"".join(members)}</section>')
    source_ids = list(dict.fromkeys([c['origin']['source']] + c['sources'] + [id for eid in c['members'] for id in idx['entities'][eid]['sources']] + [d['source'] for eid in c['members'] for d in idx['entities'][eid]['dates'] if d['source']]))
    sources = ''.join(f'<li><span class="micro">{esc(idx["sources"][id]["kind"])} · {esc(idx["sources"][id]["author"])}</span><h3>{a(idx["sources"][id]["url"], idx["sources"][id]["title"], "../")}</h3><p>{esc(idx["sources"][id]["note"])}</p></li>' for id in source_ids)
    def bullets(lines): return '<ul>' + ''.join(f'<li>{esc(t)}</li>' for t in lines) + '</ul>'
    origin = idx['sources'][c['origin']['source']]
    control_html = ''.join(f'<a class="related-item" href="{id}.html"><span class="micro">Context control</span><strong>{esc(idx["claims"][id]["title"])}</strong><span>Open →</span></a>' for id in c['controls'])
    related = [r for r in idx['claims'].values() if r['id'] != c['id'] and r['kind'] == 'claim' and set(r['cultures']) & set(c['cultures'])]
    related.sort(key=lambda r: -len(set(r['members']) & set(c['members'])))
    control_html += ''.join(f'<a class="related-item" href="{r["id"]}.html"><span class="micro">Comparison thread</span><strong>{esc(r["title"])}</strong><span>Open →</span></a>' for r in related[:3])
    cultures_query = '&'.join(f'{"culture" if i == 0 else "with"}={id}' for i, id in enumerate(c['cultures'][:2]))
    body = f'''<main id="main"><header class="dossier-heading cat-wrap"><a class="back-link" href="../catalogue.html">← All comparisons</a>
<div class="micro">{'Context control' if c['kind']=='control' else STATUS[c['status']]} · {' / '.join(esc(idx['motifs'][id]['label']) for id in c['motifs'])}</div>
<h1>{esc(c['title'])}</h1><p class="dossier-deck">{esc(c['dek'])}</p><div class="dossier-meta">{len(c['groups'])} groups · {len(c['members'])} registered records · reviewed {esc(c['review']['date'])}</div>
<div class="dossier-links">{a('../catalogue.html?view=cultures&'+cultures_query, 'See the cultural connections')} {a('../catalogue.html?view=map&focus='+c['id'], 'Locate this comparison')} {a('../catalogue.html?view=time&focus='+c['id'], 'See the dates')}{''.join(a(l['url'],l['label'],'../') for l in c['links'])}</div>
{f'<p class="micro">A focused subcomparison of {a(c["parent"]+".html",idx["claims"][c["parent"]]["title"])}. It is not independent evidence for the same proposed link.</p>' if c.get('parent') else ''}</header>
<div class="dossier-groups cat-wrap">{''.join(group_html)}</div>
<section class="dossier-reading cat-wrap"><div><div class="micro">The proposed connection</div><h2>What makes it a question?</h2></div><div><p class="reading-lead">{esc(c['anomaly'])}</p><p class="origin-note">{esc(c['origin']['note'])}<br>{a(origin['url'], origin['title'], '../')}</p></div></section>
<section class="comparison-notes cat-wrap"><div><div class="micro">Look closely</div><h2>What appears to correspond</h2>{bullets(c['features'])}</div><div><div class="micro">Keep in the frame</div><h2>What differs or remains uncertain</h2>{bullets(c['differences'])}</div></section>
<section class="dossier-reading cat-wrap"><div><div class="micro">Transmission check</div><h2>{esc(DIFFUSION[c['diffusion']['status']])}</h2></div><div><p class="reading-lead">{esc(c['diffusion']['note'])}</p><h3>What would move this forward</h3>{bullets(c['next_steps'])}</div></section>
<section class="sources-section cat-wrap" id="sources"><div class="section-top"><div><div class="micro">Follow the evidence</div><h2>Sources &amp; scope</h2></div><p>{esc(c['review']['note'])}</p></div><ol class="dossier-sources">{sources}</ol></section>
<section class="related-section cat-wrap"><div class="micro">Continue exploring</div><h2>Other threads, useful context</h2><div class="related-grid">{control_html}</div></section></main>'''
    return shell(c['title'], c['dek'], body, '../',extra='<script src="../catalogue-dossier.js" defer></script>')


def landing(data, idx):
    total = sum(c['kind'] == 'claim' for c in data['claims'])
    controls = len(data['claims']) - total
    options = lambda rows: ''.join(f'<option value="{esc(r["id"])}">{esc(r["label"])}</option>' for r in rows)
    regions = sorted({p['region'] for p in data['places']})
    cards = '\n'.join(card(c,idx) for c in data['claims'])
    body = f'''<main id="main">
<header class="catalogue-intro cat-wrap"><div><div class="micro">The collection · First edition</div><h1>Distant worlds.<br><em>Familiar forms.</em></h1></div><div class="intro-copy"><p>A growing atlas of the similarities that make people wonder about our past.</p><p>Explore cultural traditions, follow a comparison, and look closely at the evidence.</p><div class="edition-counts">{total} comparison threads <span>·</span> {len(data['groups'])} groups <span>·</span> {len(data['sources'])} source records</div></div></header>
<section class="catalogue-feature cat-wrap" aria-labelledby="feature-title"><a class="feature-visual" href="catalogue/birdmen-worlds.html" aria-label="Explore the Anatolia and Rapa Nui birdman groups"><figure><img src="img/case/pillar43.jpg" alt="Pillar 43 at Göbekli Tepe" fetchpriority="high"><figcaption>Neolithic Anatolia</figcaption></figure><div class="feature-middle" aria-hidden="true">↔</div><figure><img src="img/case/hoa-back.jpg" alt="The carved back of Hoa Hakananai’a" fetchpriority="high"><figcaption>Rapanui traditions</figcaption></figure></a><div class="feature-copy"><div class="micro">Begin with a question</div><h2 id="feature-title">The pillar. <br>The moai. <br>The bird.</h2><p>Two cultural worlds, separated by an ocean and millennia. A resemblance becomes more interesting when we place it among the objects around it.</p><a class="quiet-action" href="catalogue/birdmen-worlds.html">Explore the two groups <span>↗</span></a><a class="feature-secondary" href="catalogue.html?view=cultures&amp;culture=neolithic-anatolia&amp;with=rapanui">Follow all their comparison threads →</a></div></section>
<section id="explore" class="explore-section cat-wrap"><div class="explore-top"><div><div class="micro">Find your way in</div><h2>Follow the resemblance.</h2></div><p>Images first. Sources always within reach.</p></div>
<form id="catalogue-filters" class="catalogue-filters" hidden><div class="filter-primary"><label class="search-label"><span class="sr-only">Search the collection</span><svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="10" cy="10" r="6.5"/><path d="m15 15 5 5"/></svg><input id="search" name="q" type="search" placeholder="Search objects, traditions, ideas…" autocomplete="off"></label><label><span class="sr-only">Theme</span><select name="motif" id="motif"><option value="">Every theme</option>{options(data['motifs'])}</select></label><label><span class="sr-only">Cultural tradition</span><select id="culture" name="culture"><option value="">Every cultural tradition</option>{options(data['cultures'])}</select></label><button type="button" id="more-filters" aria-expanded="false" aria-controls="filter-details">Refine <span aria-hidden="true">+</span></button></div>
<div id="filter-details" class="filter-details" hidden><label>Compare with<select id="with-culture" name="with"><option value="">Any other tradition</option>{options(data['cultures'])}</select></label><label>Region<select id="region" name="region"><option value="">Every region</option>{''.join(f'<option>{esc(r)}</option>' for r in regions)}</select></label><label>Review depth<select id="review" name="review"><option value="">All stages</option>{''.join(f'<option value="{k}">{v}</option>' for k,v in STATUS.items())}</select></label><label>Transmission check<select id="diffusion" name="diffusion"><option value="">Every status</option>{''.join(f'<option value="{k}">{v}</option>' for k,v in DIFFUSION.items())}</select></label><fieldset class="date-filter"><legend>Date interval</legend><label>From<input name="from" id="date-from" type="number" min="-12000" max="2026" placeholder="−10000"></label><label>To<input name="to" id="date-to" type="number" min="-12000" max="2026" placeholder="2026"></label><p>Negative years = BCE. Any recorded interval may overlap; witness dates are labelled. No year zero.</p></fieldset><div class="check-filters"><label><input id="unknown" type="checkbox" name="unknown" checked> Include examples with unresolved dates</label><label><input id="controls" type="checkbox" name="controls"> Include {controls} context controls</label></div></div><p id="filter-error" class="filter-error" role="alert" hidden></p></form>
<div class="view-toolbar" id="view-toolbar" hidden><nav class="view-buttons" aria-label="Browse the collection"><button type="button" data-view="gallery" aria-pressed="true">Comparisons</button><button type="button" data-view="cultures" aria-pressed="false">Cultures</button><button type="button" data-view="map" aria-pressed="false">Map</button><button type="button" data-view="time" aria-pressed="false">Timeline</button><button type="button" data-view="themes" aria-pressed="false">Themes</button></nav><button type="button" id="reset-filters">Clear filters</button></div>
<div class="results-line"><p id="result-count" role="status" aria-live="polite">{total} comparison threads · {controls} optional context controls</p><button type="button" id="copy-view" hidden>Copy this view ↗</button></div><p id="active-filters" class="active-filters" hidden></p><p class="filter-explanation" id="date-filter-note" hidden></p>
<div id="gallery-view" class="catalogue-grid">{cards}</div><section id="cultures-view" class="view-panel" hidden aria-label="Cultural connections"></section><section id="map-view" class="view-panel" hidden aria-label="Map of comparisons"></section><section id="time-view" class="view-panel" hidden aria-label="Comparison chronology"></section><section id="themes-view" class="view-panel" hidden aria-label="Motif collections"></section>
<div id="empty-state" class="empty-state" hidden><h3>No comparisons in this view.</h3><p>Try a broader theme or date interval. Unresolved dates and context controls can be included under Refine.</p><button type="button" id="empty-reset">Clear filters</button></div>
<noscript><p class="catalogue-message">All comparison dossiers are available below. Map, timeline and filtering need JavaScript.</p></noscript><p id="load-error" class="catalogue-message" role="status" hidden>The interactive views could not load. You can still open every comparison below.</p>
</section>
<section id="about" class="collection-about cat-wrap"><div><div class="micro">An open collection</div><h2>Room for wonder.<br>Room for scrutiny.</h2></div><div><p>We collect <strong>claimed anomalous similarities</strong>: comparisons that people believe reach beyond ordinary transmission. Inclusion records a question. It does not certify an unexplained historical connection.</p><p>The main clusters are cultural traditions, with dated examples inside them. Comparisons can connect whole groups, narrow subsets or particular objects. One object can belong to several threads without becoming several independent pieces of evidence.</p><details><summary>How to read the catalogue</summary><p><b>Evidence examined</b> means a specific source or image audit exists. <b>Sources partly checked</b> means some identities or passages have been traced. <b>Research lead</b> means substantial verification remains. <b>Claim corrected</b> preserves a comparison whose stated details changed under review. These are review stages, not anomaly scores.</p><p>The map uses approximate original contexts, not museum destinations. Its lines connect comparisons, not voyages. The timeline distinguishes object dates, broad site context, composition and later witnesses; unresolved dates remain visible.</p><p>This first edition is curated from the project archive and a new source search. It is not yet a systematic worldwide survey. Groups may contain only one registered example, and motif frequency cannot be inferred from these selected records. No generated image is used as archaeological evidence.</p></details><div class="about-links"><a href="data/catalogue.json">Download the complete register ↗</a><a href="https://github.com/ejhong/birdmen/issues/new">Suggest a comparison or better source ↗</a></div></div></section>
</main>'''
    return shell('Distant worlds. Familiar forms.', 'Explore claimed anomalous similarities across cultural traditions, with photographs, sources, maps and careful chronology.',body,extra='<script type="module" src="catalogue.js"></script>')


def outputs():
    data = json.loads((ROOT / 'research/catalogue/catalogue.json').read_text())
    validate(data)
    idx = index(data)
    coast = json.loads((ROOT / 'data/raw/ne_110m_coastline.geojson').read_text())
    lines = []
    for f in coast['features']:
        geometry = f['geometry']
        for line in ([geometry['coordinates']] if geometry['type'] == 'LineString' else geometry['coordinates']):
            lines.append([[round(x, 3), round(y, 3)] for x,y,*_ in line])
    out = {DOCS / 'catalogue.html': landing(data,idx),
           DOCS / 'data/catalogue.json': json.dumps(data,ensure_ascii=False,indent=2)+'\n',
           DOCS / 'data/catalogue-coast.json': json.dumps(dict(source='Natural Earth 1:110m coastline; public domain. Modern coastlines, not palaeogeography.',lines=lines),separators=(',',':'))+'\n'}
    for c in data['claims']:
        out[DOCS / 'catalogue' / (c['id'] + '.html')] = dossier(c,idx)
    return out


if __name__ == '__main__':
    for path, content in outputs().items():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(content)
    print('Published catalogue and all comparison dossiers')
