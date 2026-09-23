"""The two repertoires, side by side: a countable population instead of a chosen pair.

Derived from research/corpus/corpus.json. Every count describes the registered
photographs, never the published corpus and never the objects themselves. A feature
state records what is legible in one photograph; a photograph cannot establish that
a feature is absent from an object.
"""
import json
try:
    from pipeline.catalogue import ROOT, DOCS, esc, a, shell
except ModuleNotFoundError:
    from catalogue import ROOT, DOCS, esc, a, shell

STATE = {'1': 'legible', '?': 'uncertain', '0': 'not legible in this view'}


def load():
    return json.loads((ROOT / 'research/corpus/corpus.json').read_text())


def validate(data, check_files=True):
    import hashlib
    ids, keys = set(), [f['id'] for f in data['features']]
    for item in data['items']:
        if item['id'] in ids:
            raise ValueError(f'Duplicate corpus item {item["id"]}')
        ids.add(item['id'])
        if item['corpus'] not in {c['id'] for c in data['corpora']}:
            raise ValueError(f'Unknown corpus in {item["id"]}')
        if list(item['features']) != keys:
            raise ValueError(f'Feature keys do not match the register in {item["id"]}')
        if any(v not in STATE for v in item['features'].values()):
            raise ValueError(f'Unknown feature state in {item["id"]}')
        m = item['media']
        if not item.get('physical'):
            raise ValueError(f'Missing physical identity in {item["id"]}')
        if not all(m.get(k) for k in ('path', 'credit', 'rights', 'url', 'transformation', 'sha256')):
            raise ValueError(f'Incomplete media provenance in {item["id"]}')
        path = (DOCS / m['path']).resolve()
        if not path.is_relative_to(DOCS) or not path.is_file():
            raise ValueError(f'Missing corpus image {m["path"]}')
        if check_files and hashlib.sha256(path.read_bytes()).hexdigest() != m['sha256']:
            raise ValueError(f'Corpus image changed: {item["id"]}')
    return True


def counts(data, corpus):
    """Photographs in which each feature is legible. Uncertain readings are not counted."""
    items = [i for i in data['items'] if i['corpus'] == corpus]
    out = {f['id']: sum(1 for i in items if i['features'][f['id']] == '1') for f in data['features']}
    both = [i for i in items if i['features']['bird'] == '1' and i['features']['round'] == '1']
    out['both'] = len(both)
    out['both_objects'] = len({i['physical'] for i in both})
    out['objects'] = len({i['physical'] for i in items})
    out['total'] = len(items)
    return out


def tile(item, features):
    marks = ' '.join(f'{k}-{item["features"][k]}' for k in features)
    m = item['media']
    return f'''<li class="wall-item" data-state="{esc(marks)}"><a href="{esc(m['path'])}" class="wall-plate">
<img src="{esc(m['path'])}" alt="{esc(item['label'])} — {esc(item['context'])}" loading="lazy" decoding="async"></a>
<div class="wall-caption"><b>{esc(item['label'])}</b>{esc(item['context'])}</div></li>'''


def wall(data, corpus):
    c = next(x for x in data['corpora'] if x['id'] == corpus)
    items = [i for i in data['items'] if i['corpus'] == corpus]
    n = counts(data, corpus)
    keys = [f['id'] for f in data['features']]
    return f'''<section class="wall" data-corpus="{esc(corpus)}" aria-labelledby="wall-{esc(corpus)}">
<header class="wall-head"><div class="micro">{esc(c['period'])}</div><h2 id="wall-{esc(corpus)}">{esc(c['label'])}</h2>
<p>{esc(c['sites'])}</p><p class="wall-count" data-total="{n['total']}">{n['total']} registered photographs</p></header>
<ol class="wall-grid">{''.join(tile(i, keys) for i in items)}</ol></section>'''


def gap_figure(data):
    """One timeline. The distance between the two bands is the honest obstacle."""
    lo, hi, w = -10000, 2000, 1000
    x = lambda year: (year - lo) * w / (hi - lo)
    drawn = [b for b in data['chronology'] if b['start'] is not None]
    bands, labels = [], []
    for b in data['chronology']:
        if b['start'] is None:   # An unresolved date cannot be drawn; it stays in the table.
            continue
        x1, x2 = x(b['start']), x(max(b['end'], b['start'] + 40))
        bands.append(f'<rect class="gap-band gap-{esc(b["side"])}" x="{x1:.1f}" y="{b["row"] * 46 + 18}" '
                     f'width="{max(2.0, x2 - x1):.1f}" height="26" rx="2"><title>{esc(b["label"])}</title></rect>')
        labels.append(f'<text class="gap-label" x="{min(w - 4, x2 + 9):.1f}" y="{b["row"] * 46 + 36}">{esc(b["label"])}</text>')
    ticks = ''.join(f'<g><line class="gap-tick" x1="{x(y):.1f}" y1="8" x2="{x(y):.1f}" y2="{len(drawn) * 46 + 26}"/>'
                    f'<text class="gap-year" x="{x(y):.1f}" y="{len(drawn) * 46 + 44}">'
                    f'{abs(y):,} {"BCE" if y < 0 else "CE"}</text></g>' for y in (-10000, -8000, -6000, -4000, -2000, 0, 2000))
    rows = ''.join(f'<tr><th scope="row">{esc(b["label"])}</th><td>{esc(b["note"])}</td></tr>' for b in data['chronology'])
    return f'''<div class="gap-figure"><svg viewBox="0 -4 1100 {len(drawn) * 46 + 56}" role="img" aria-labelledby="gap-title gap-desc">
<title id="gap-title">The interval between the two repertoires</title>
<desc id="gap-desc">Every registered episode on one linear scale from 10,000 BCE to 2000 CE. The table below carries the same dates as text.</desc>
{ticks}{''.join(bands)}{''.join(labels)}</svg></div>
<div class="table-scroll"><table class="feature-matrix"><caption class="sr-only">Registered dated episodes</caption>
<thead><tr><th>Episode</th><th>What the date describes</th></tr></thead><tbody>{rows}</tbody></table></div>'''


def page(data):
    keys = [f['id'] for f in data['features']]
    an, rn = counts(data, 'anatolia'), counts(data, 'rapanui')
    chips = ''.join(f'<button type="button" data-feature="{esc(f["id"])}" aria-pressed="false">'
                    f'{esc(f["label"])}</button>' for f in data['features'])
    anchors = ''.join(f'''<figure class="anchor"><a href="{esc(i['media']['path'])}"><img src="{esc(i['media']['path'])}"
alt="{esc(i['label'])} — {esc(i['context'])}" loading="lazy"></a><figcaption><b>{esc(i['label'])}</b>{esc(i['context'])}<br>{esc(i['note'])}</figcaption></figure>'''
                      for i in (next(x for x in data['items'] if x['id'] == data['anchors'][0]),
                                next(x for x in data['items'] if x['id'] == data['anchors'][1])))
    contexts = ''.join(f'''<article class="context-panel"><div class="micro">{esc(c['period'])}</div><h3>{esc(c['label'])}</h3>
<p>{esc(c['context'])}</p><p class="context-source">{a(c['context_source']['url'], c['context_source']['title'])} · {esc(c['context_source']['note'])}</p></article>'''
                       for c in data['corpora'])
    excluded = ''.join(f'<li><b>{esc(e["reason"])}</b><span>{e["count"]} files</span></li>' for e in data['selection']['excluded'])
    body = f'''<main id="main">
<div class="cat-wrap cluster-crumb"><a class="back-link" href="clusters/neolithic-anatolia--rapanui.html">← The Göbekli Tepe &amp; Rapa Nui cluster</a></div>
<header class="catalogue-intro cat-wrap"><div><div class="micro">The two repertoires</div><h1>Every stone<br><em>we could find.</em></h1></div>
<div class="intro-copy"><p>{esc(data['deck'])}</p><p>{esc(data['deck_2'])}</p>
<div class="edition-counts">{an['total']} Anatolian photographs <span>·</span> {rn['total']} Rapanui photographs <span>·</span> all openly licensed</div></div></header>

<section class="wall-controls cat-wrap" id="filter"><div class="section-top"><div><div class="micro">Filter both walls at once</div>
<h2>What are you looking for?</h2></div><p>{esc(data['filter_note'])}</p></div>
<div class="feature-filters" role="group" aria-label="Features to highlight">{chips}<button type="button" id="wall-reset">Clear</button></div>
<p class="wall-readout" id="wall-readout" role="status" aria-live="polite">Nothing selected. Both walls show every registered photograph.</p>
<p class="wall-headline">Of {an['total']} Anatolian photographs, a bird is legible in <b>{an['bird']}</b> and a rounded form in <b>{an['round']}</b>. Both share one surface in <b>{an['both']}</b> — and those {an['both']} photographs are <b>{an['both_objects']} object{'' if an['both_objects'] == 1 else 's'}</b>. Of {rn['total']} Rapanui photographs the figures are <b>{rn['bird']}</b>, <b>{rn['round']}</b> and <b>{rn['both']}</b>, across <b>{rn['both_objects']} objects</b>.</p>
<p class="wall-finding">{esc(data['finding'])}</p></section>

<div class="walls cat-wrap">{wall(data, 'anatolia')}{wall(data, 'rapanui')}</div>

<section class="anchor-section cat-wrap"><div class="section-top"><div><div class="micro">The two stones the comparison rests on</div>
<h2>Back among their neighbours.</h2></div><p>{esc(data['anchor_note'])}</p></div>
<div class="anchor-pair">{anchors}</div></section>

<section class="context-section cat-wrap"><div class="section-top"><div><div class="micro">Why the motif lives here</div>
<h2>Each side has a local story.</h2></div><p>{esc(data['context_note'])}</p></div>
<div class="context-grid">{contexts}</div></section>

<section class="gap-section cat-wrap" id="gap"><div class="section-top"><div><div class="micro">The interval</div>
<h2>Ten thousand years.</h2></div><p>{esc(data['gap_note'])}</p></div>{gap_figure(data)}</section>

<section class="collection-about cat-wrap" id="method"><div><div class="micro">How this page was built</div><h2>The rule,<br>before the looking.</h2></div>
<div><p>{esc(data['selection']['rule'])}</p><p>{esc(data['selection']['caveat'])}</p>
<p>{esc(data['review']['note'])}</p>
<details><summary>What was excluded, and why</summary><ul class="exclusion-list">{excluded}</ul>
<p>{esc(data['selection']['exclusion_note'])}</p></details>
<div class="about-links"><a href="data/corpus.json">Download the corpus register ↗</a><a href="clusters/neolithic-anatolia--rapanui.html">The cluster this tests ↗</a><a href="https://github.com/ejhong/birdmen/issues/new">Suggest a stone we missed ↗</a></div></div></section>
</main>'''
    return shell('Every stone we could find', data['description'], body,
                 extra='<link rel="stylesheet" href="corpus.css"><script type="module" src="corpus.js"></script>')


def outputs():
    data = load()
    validate(data)
    return {DOCS / 'corpus.html': page(data),
            DOCS / 'data/corpus.json': json.dumps(data, ensure_ascii=False, indent=2) + '\n'}


if __name__ == '__main__':
    for path, content in outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print('Published the corpus walls')
