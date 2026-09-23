"""Culture-pair clusters: where the collection's open questions concentrate.

Derived entirely from the maintained catalogue register. Nothing here is a new
editorial claim. A cluster counts comparison lines; it never scores an anomaly,
ranks evidence strength or asserts that two traditions met.
"""
import json
import math
try:
    from pipeline.catalogue import ROOT, DOCS, STATUS, DIFFUSION, esc, a, shell, picture, index, validate
except ModuleNotFoundError:
    from catalogue import ROOT, DOCS, STATUS, DIFFUSION, esc, a, shell, picture, index, validate

# "Open" means no route was established or none was assessed in this review. An
# unassessed lead is open because nobody has checked it, which is a weakness.
OPEN = ('unestablished', 'unassessed')
FLAGSHIP = 'neolithic-anatolia--rapanui'


def year(n):
    return f"{abs(n):,} {'BCE' if n < 0 else 'CE'}"


def clusters(data, idx):
    """Mirror of clusters() in docs/catalogue-model.mjs; the tests compare both."""
    found = {}
    for c in data['claims']:
        if c['kind'] != 'claim':
            continue
        cultures = sorted(set(c['cultures']))
        root = c.get('parent') or c['id']
        for i in range(len(cultures)):
            for j in range(i + 1, len(cultures)):
                key = f'{cultures[i]}--{cultures[j]}'
                cluster = found.setdefault(key, {'id': key, 'a': cultures[i], 'b': cultures[j], 'lines': {}})
                children = cluster['lines'].setdefault(root, [])
                if c['id'] != root and c['id'] not in children:
                    children.append(c['id'])
    out = []
    for cluster in found.values():
        lines = [{'root': root, 'children': sorted(children)} for root, children in cluster['lines'].items()]
        roots = [idx['claims'][line['root']] for line in lines]
        unresolved = [c for c in roots if c['diffusion']['status'] in OPEN]
        threads = [id for line in lines for id in [line['root'], *line['children']]]
        records = {idx['entities'][m]['physical_id'] for id in threads for m in idx['claims'][id]['members']}
        out.append({'id': cluster['id'], 'a': cluster['a'], 'b': cluster['b'], 'lines': lines, 'threads': threads,
                    'families': list(dict.fromkeys(f['id'] for c in roots for f in data['families'] if c['id'] in f['claims'])),
                    'open': len(unresolved), 'checked': sum(1 for c in unresolved if c['status'] != 'lead'),
                    'examined': sum(1 for c in roots if c['status'] == 'examined'), 'records': len(records)})
    out.sort(key=lambda c: (-c['checked'], -c['open'], -len(c['lines']), -len(c['families']), -c['records'], c['id']))
    return out


def members(cluster, culture, idx):
    """Registered records on one side of a cluster, in the order the threads name them."""
    seen, out = set(), []
    for id in cluster['threads']:
        for eid in idx['claims'][id]['members']:
            e = idx['entities'][eid]
            if e['culture'] == culture and eid not in seen:
                seen.add(eid)
                out.append(e)
    return out


def representative(cluster, culture, idx):
    candidates = members(cluster, culture, idx)
    return next((e for e in candidates if e['media']), candidates[0] if candidates else None)


def span(entities):
    dates = [d for e in entities for d in e['dates'] if d['start'] is not None]
    if not dates:
        return 'No numerical episode date is yet registered here.'
    return f"Registered dated episodes: {year(min(d['start'] for d in dates))} to {year(max(d['end'] for d in dates))}."


def plate(entity, idx, prefix='', caption=None, bare=False):
    """The framed-photograph treatment: hairline frame, light mount, caption inside."""
    if entity is None:
        return ('<figure class="plate plate-empty"><div class="plate-mount"><i aria-hidden="true">∿</i></div>'
                + ('' if bare else '<figcaption><b>No registered image</b>The record is textual</figcaption>') + '</figure>')
    m = idx['media'].get(entity['media'])
    place = idx['places'].get(entity['place'])
    body = picture(entity, idx, prefix) if not m else f'<img src="{esc(prefix + m["path"])}" alt="{esc(m["alt"])}" loading="lazy" decoding="async">'
    where = caption or (place['name'] if place else 'Place unresolved')
    legend = '' if bare else f'<figcaption><b>{esc(entity["label"])}</b>{esc(where)}</figcaption>'
    return f'<figure class="plate"><div class="plate-mount">{body}</div>{legend}</figure>' 


def pair_labels(cluster, idx):
    return idx['cultures'][cluster['a']]['label'], idx['cultures'][cluster['b']]['label']


def pair_title(cluster, idx, join=' &amp; '):
    return join.join(esc(label) for label in pair_labels(cluster, idx))


def state_url(cluster, view='gallery'):
    return f'catalogue.html?view={view}&culture={cluster["a"]}&with={cluster["b"]}'


def separation(cluster, idx):
    """Great-circle distance between the registered contexts, rounded; sites are approximate."""
    def anchor(culture):
        return next((idx['places'][e['place']] for e in members(cluster, culture, idx)
                     if e['place'] and idx['places'].get(e['place'])), None)
    one, two = anchor(cluster['a']), anchor(cluster['b'])
    if not one or not two:
        return None
    lat1, lat2 = math.radians(one['lat']), math.radians(two['lat'])
    cosine = (math.sin(lat1) * math.sin(lat2) +
              math.cos(lat1) * math.cos(lat2) * math.cos(math.radians(two['lon'] - one['lon'])))
    return round(6371 * math.acos(max(-1, min(1, cosine))), -2)


def counts(cluster):
    lines = len(cluster['lines'])
    parts = [f"{lines} line{'' if lines == 1 else 's'} of comparison",
             f"{cluster['open']} without an established route",
             f"{len(cluster['families'])} motif famil{'y' if len(cluster['families']) == 1 else 'ies'}",
             f"{cluster['records']} registered object{'' if cluster['records'] == 1 else 's'}"]
    return ' · '.join(parts)


def ledger(cluster, idx, prefix=''):
    rows = []
    for line in cluster['lines']:
        c = idx['claims'][line['root']]
        open_ = c['diffusion']['status'] in OPEN
        mark = 'open' if open_ else 'context'
        rows.append(f'<li class="line-{mark}"><b>{esc(c["title"])}</b>'
                    f'<span>{esc(STATUS[c["status"]])} · {esc(DIFFUSION[c["diffusion"]["status"]])}</span></li>')
    return f'<ol class="cluster-ledger">{"".join(rows)}</ol>'


def matrix(rows, idx):
    """A sparse table: most traditions in the collection have never been compared."""
    used = [id for id in dict.fromkeys([c[k] for c in rows for k in ('a', 'b')])]
    used.sort(key=lambda id: (-sum(1 for c in rows if id in (c['a'], c['b'])), idx['cultures'][id]['label']))
    by_pair = {c['id']: c for c in rows}
    head = ''.join(f'<th scope="col"><span>{esc(idx["cultures"][id]["label"])}</span></th>' for id in used)
    body = []
    for a_id in used:
        cells = []
        for b_id in used:
            if a_id == b_id:
                cells.append('<td class="matrix-self"></td>')
                continue
            cluster = by_pair.get('--'.join(sorted([a_id, b_id])))
            if not cluster:
                cells.append('<td></td>')
                continue
            tone = 'checked' if cluster['checked'] else 'open' if cluster['open'] else 'context'
            label = f"{' and '.join(pair_labels(cluster, idx))}: {counts(cluster)}"
            cells.append(f'<td class="matrix-cell matrix-{tone}"><a href="clusters/{esc(cluster["id"])}.html" '
                         f'aria-label="{esc(label)}" title="{esc(label)}"><span>{len(cluster["lines"])}</span></a></td>')
        body.append(f'<tr><th scope="row">{esc(idx["cultures"][a_id]["label"])}</th>{"".join(cells)}</tr>')
    return (f'<div class="table-scroll"><table class="cluster-matrix"><caption class="sr-only">Cultural traditions '
            f'compared with one another; each filled cell opens that cluster.</caption><thead><tr><td></td>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def cluster_row(cluster, rank, idx):
    left, right = representative(cluster, cluster['a'], idx), representative(cluster, cluster['b'], idx)
    families = ' · '.join(idx['families'][id]['label'] for id in cluster['families']) or 'No motif family assigned yet'
    depth = 'examined in depth' if cluster['examined'] else 'source checks begun' if cluster['checked'] else 'awaiting identification'
    return f'''<li class="cluster-row"><a class="cluster-link" href="clusters/{esc(cluster['id'])}.html">
<div class="cluster-plates">{plate(left, idx, bare=True)}<span class="plate-join" aria-hidden="true">↔</span>{plate(right, idx, bare=True)}</div>
<div class="cluster-copy"><div class="micro">{rank:02d} · {esc(depth)}</div><h3>{pair_title(cluster, idx, ' ↔ ')}</h3>
<p>{esc(families)}</p>{ledger(cluster, idx)}
<div class="cluster-foot">{esc(counts(cluster))}<span>Open the cluster →</span></div></div></a></li>'''


def landing(data, idx, rows):
    flagship = next(c for c in rows if c['id'] == FLAGSHIP)
    left, right = representative(flagship, flagship['a'], idx), representative(flagship, flagship['b'], idx)
    # Count each comparison once: a thread spanning three traditions joins three pairs.
    roots = {line['root'] for c in rows for line in c['lines']}
    unresolved = {id for id in roots if idx['claims'][id]['diffusion']['status'] in OPEN}
    checked_pairs = sum(1 for c in rows if c['checked'])
    body = f'''<main id="main">
<div class="cat-wrap cluster-crumb"><a class="back-link" href="catalogue.html">← The collection</a></div>
<header class="catalogue-intro cat-wrap"><div><div class="micro">The cluster index</div><h1>Which worlds<br><em>keep meeting?</em></h1></div>
<div class="intro-copy"><p>Every proposed comparison here joins two cultural traditions. Gathered as clusters, they show where this collection’s questions concentrate — and where an ordinary explanation is already on the table.</p>
<p>A cluster is an index entry, not a verdict. Counting comparisons cannot make them independent, and nothing below establishes that two traditions ever met.</p>
<div class="edition-counts">{len(rows)} culture pairs <span>·</span> {len(roots)} distinct comparisons <span>·</span> {len(unresolved)} with no route established</div></div></header>

<section class="cluster-flagship" aria-labelledby="flagship-title"><div class="cat-wrap flagship-inner">
<div class="flagship-plates">{plate(left, idx, caption='Göbekli Tepe · 10th–9th millennia BCE')}<span class="plate-join" aria-hidden="true">↔</span>{plate(right, idx, caption='Rapa Nui · later carvings, date open')}</div>
<div class="flagship-copy"><div class="micro">The densest cluster</div><h2 id="flagship-title">Göbekli Tepe<br>&amp; Rapa Nui.</h2>
<p>One pair carries more separate comparisons than any other in the collection: birds beside rounded forms, hands drawn across a torso, ribs cut into a lean body. Two of the three lines have been examined against sources rather than only collected.</p>
<p class="flagship-note">No transmission route has been established for any of them — and about {separation(flagship, idx):,.0f} km of ocean and land, plus several millennia, separate the registered contexts. That distance is a reason to look harder at the objects, not evidence of a link.</p>
{ledger(flagship, idx)}<a class="quiet-action" href="clusters/{esc(FLAGSHIP)}.html">Open the cluster <span>↗</span></a>
<a class="feature-secondary" href="pillar-and-moai.html">Or start from the two photographs →</a></div></div></section>

<section class="cluster-field cat-wrap" id="field"><div class="section-top"><div><div class="micro">The whole field</div><h2>A sparse table.</h2></div>
<p>{len(rows)} of the {possible(rows)} possible pairings between these traditions carry a comparison. Sparseness describes what has been collected, not a measurement of the world.</p></div>
{matrix(rows, idx)}
<div class="matrix-legend"><span class="matrix-key matrix-checked">Open after a source check</span><span class="matrix-key matrix-open">Open, not yet assessed</span><span class="matrix-key matrix-context">Context or documented exchange</span></div>
<p class="view-note">Each number is how many separate lines of comparison the pair carries. The ranked index below carries the same information as text.</p></section>

<section class="cluster-index cat-wrap" id="index"><div class="section-top"><div><div class="micro">Every cluster</div><h2>Where the questions concentrate.</h2></div>
<p>Ordered by how many comparisons remain open <i>after</i> a source check — never by how strong or how independent the evidence is.</p></div>
<ol class="cluster-list">{''.join(cluster_row(c, n + 1, idx) for n, c in enumerate(rows))}</ol></section>

<section class="collection-about cat-wrap" id="reading"><div><div class="micro">Reading a cluster</div><h2>What a cluster<br>cannot tell you.</h2></div>
<div><p>A line of comparison is one proposed resemblance between two traditions. Its subcomparisons — a narrower look at the same pair of objects — are counted inside it, because they are not separate evidence.</p>
<p>“No route established” records the state of this review. {checked_pairs} pair{'s' if checked_pairs != 1 else ''} reached that state after a source check; the rest are open mainly because their identifications are still unresolved. An unchecked lead is weaker than a checked one, not stronger.</p>
<p>Examples were selected because they resemble each other. That selection cannot tell us how often such forms occur worldwide, and similar human bodies, tools and birds constrain what any carver can produce.</p>
<div class="about-links"><a href="catalogue.html">Browse the motif families ↗</a><a href="data/clusters.json">Download the cluster index ↗</a><a href="input-audit.html">See what every input became ↗</a></div></div></section>
</main>'''
    return shell('Clusters', 'Which cultural traditions carry the most open comparisons in this collection, and what each pair actually rests on.', body,
                 extra='<link rel="stylesheet" href="clusters.css">', current='clusters.html')


def possible(rows):
    used = {id for c in rows for id in (c['a'], c['b'])}
    return len(used) * (len(used) - 1) // 2


def line_block(cluster, line, number, idx):
    c = idx['claims'][line['root']]
    left = [e for e in c['members'] if idx['entities'][e]['culture'] == cluster['a']]
    right = [e for e in c['members'] if idx['entities'][e]['culture'] == cluster['b']]
    pick = lambda ids: next((idx['entities'][id] for id in ids if idx['entities'][id]['media']), idx['entities'][ids[0]] if ids else None)
    bullets = lambda items: '<ul>' + ''.join(f'<li>{esc(t)}</li>' for t in items) + '</ul>'
    children = ''
    if line['children']:
        items = ''.join(f'<li>{a("../catalogue/" + id + ".html", idx["claims"][id]["title"])} — {esc(idx["claims"][id]["dek"])}</li>' for id in line['children'])
        children = (f'<div class="line-children"><div class="micro">Inside this line</div><ul>{items}</ul>'
                    '<p>A narrower look at the same objects. It is counted inside this line, not as separate evidence.</p></div>')
    other = [id for id in c['cultures'] if id not in (cluster['a'], cluster['b'])]
    reach = f'<p class="line-reach">This comparison also reaches {esc(" and ".join(idx["cultures"][id]["label"] for id in other))}.</p>' if other else ''
    return f'''<article class="cluster-line" id="line-{esc(line['root'])}"><div class="line-head"><div class="micro">Line {number:02d} · {esc(STATUS[c['status']])}</div>
<h2>{esc(c['title'])}</h2><p class="line-dek">{esc(c['dek'])}</p></div>
<div class="line-plates">{plate(pick(left), idx, '../')}<span class="plate-join" aria-hidden="true">↔</span>{plate(pick(right), idx, '../')}</div>
<div class="line-notes"><div><div class="micro">What appears to correspond</div>{bullets(c['features'])}</div>
<div><div class="micro">What differs or remains uncertain</div>{bullets(c['differences'])}</div></div>
<div class="line-status status-{'open' if c['diffusion']['status'] in OPEN else 'context'}"><div class="micro">Transmission check</div>
<h3>{esc(DIFFUSION[c['diffusion']['status']])}</h3><p>{esc(c['diffusion']['note'])}</p></div>
{reach}{children}<p class="line-more">{a('../catalogue/' + c['id'] + '.html', 'Open the full dossier: groups, dates and sources →')}</p></article>'''


def dossier(cluster, data, idx):
    left_records, right_records = members(cluster, cluster['a'], idx), members(cluster, cluster['b'], idx)
    culture_a, culture_b = idx['cultures'][cluster['a']], idx['cultures'][cluster['b']]
    controls = [c for c in data['claims'] if c['kind'] == 'control' and set(c['cultures']) & {cluster['a'], cluster['b']}]
    control_html = ''.join(f'''<a class="related-item" href="../catalogue/{esc(c['id'])}.html"><span class="micro">{esc(DIFFUSION[c['diffusion']['status']])}</span>
<strong>{esc(c['title'])}</strong><span>{esc(c['dek'])}</span></a>''' for c in controls)
    steps = list(dict.fromkeys(step for line in cluster['lines'] for step in idx['claims'][line['root']]['next_steps']))
    source_ids = list(dict.fromkeys(id for tid in cluster['threads'] for id in
                                    [idx['claims'][tid]['origin']['source'], *idx['claims'][tid]['sources']]))
    sources = ''.join(f'<li><span class="micro">{esc(idx["sources"][id]["kind"])} · {esc(idx["sources"][id]["author"])}</span>'
                      f'<h3>{a(idx["sources"][id]["url"], idx["sources"][id]["title"], "../")}</h3>'
                      f'<p>{esc(idx["sources"][id]["note"])}</p></li>' for id in source_ids)
    def side(culture, records):
        dated = ''.join(f'<li><b>{esc(e["label"])}</b><span>{esc(", ".join(d["label"] + " · " + d["kind"] for d in e["dates"]) or "No registered date")}</span></li>' for e in records)
        return f'''<div class="cluster-side"><div class="micro">Cultural context</div><h2>{esc(culture['label'])}</h2><p>{esc(culture['note'])}</p>
<p class="cluster-span">{esc(span(records))}</p><ul class="date-records">{dated}</ul></div>'''
    body = f'''<main id="main"><header class="dossier-heading cat-wrap"><a class="back-link" href="../clusters.html">← Cluster index</a>
<div class="micro">Cluster · {esc(counts(cluster))}</div><h1>{pair_title(cluster, idx, '<br><span aria-hidden="true">↔</span><br>')}</h1>
<p class="dossier-deck">{len(cluster['lines'])} separate line{'' if len(cluster['lines']) == 1 else 's'} of comparison join these two traditions in this collection. {cluster['open']} of them {'has' if cluster['open'] == 1 else 'have'} no established route.</p>
<div class="dossier-links">{a('../' + state_url(cluster), 'All threads in the collection')} {a('../' + state_url(cluster, 'map'), 'Map')} {a('../' + state_url(cluster, 'time'), 'Dates')}{a('../corpus.html', 'Both repertoires, every stone') if cluster['id'] == FLAGSHIP else ''}</div>
<p class="micro">Motif families: {' · '.join(a('../families/' + id + '.html', idx['families'][id]['label']) for id in cluster['families']) or 'none assigned yet'}</p></header>
<section class="cluster-sides cat-wrap">{side(culture_a, left_records)}{side(culture_b, right_records)}</section>
<section class="cluster-lines cat-wrap">{''.join(line_block(cluster, line, n + 1, idx) for n, line in enumerate(cluster['lines']))}</section>
<section class="dossier-reading cat-wrap"><div><div class="micro">Keep in the frame</div><h2>What would move this cluster forward?</h2></div>
<div><p class="reading-lead">Collected comparisons accumulate; they do not compound into proof. Each line still needs its own dated sequence.</p>
<ul>{''.join(f'<li>{esc(step)}</li>' for step in steps)}</ul></div></section>
{f'<section class="related-section cat-wrap"><div class="micro">Already on the table</div><h2>Ordinary explanations and documented context.</h2><div class="related-grid">{control_html}</div></section>' if control_html else ''}
<section class="sources-section cat-wrap" id="sources"><div class="section-top"><div><div class="micro">Follow the evidence</div><h2>Sources &amp; scope</h2></div>
<p>Provisional editorial records with no independent specialist sign-off. Review stages describe how far sources were checked, not the probability of a historical connection.</p></div>
<ol class="dossier-sources">{sources}</ol></section></main>'''
    title = ' & '.join(pair_labels(cluster, idx))
    return shell(title, f'The comparisons this collection records between {title}, with what corresponds, what differs and what remains unestablished.',
                 body, '../', extra='<link rel="stylesheet" href="../clusters.css">', current='clusters.html')


def outputs(data, idx):
    rows = clusters(data, idx)
    register = {'edition': data['edition'],
                'scope': 'Derived culture-pair index. Counts record comparisons in this collection, never evidence strength, independence or contact.',
                'clusters': rows}
    out = {DOCS / 'clusters.html': landing(data, idx, rows),
           DOCS / 'data/clusters.json': json.dumps(register, ensure_ascii=False, indent=2) + '\n'}
    for cluster in rows:
        out[DOCS / 'clusters' / (cluster['id'] + '.html')] = dossier(cluster, data, idx)
    return out


if __name__ == '__main__':
    data = json.loads((ROOT / 'research/catalogue/catalogue.json').read_text())
    validate(data)
    for path, content in outputs(data, index(data)).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print('Published the cluster index')
