"""Publish a bounded visual comparison and historical evidence trail, offline."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

try:
    from pipeline.catalogue import ROOT, DOCS, esc, a, shell
except ModuleNotFoundError:
    from catalogue import ROOT, DOCS, esc, a, shell

RESEARCH = ROOT / 'research/pillar-moai/fieldwork'
DATA = ROOT / 'data/pillar-moai/fieldwork'
STATES = {'present', 'uncertain', 'not-seen', 'unresolved', 'not-applicable'}
LABELS = {'present': 'Observed', 'uncertain': 'Uncertain', 'not-seen': 'Not seen in this view',
          'unresolved': 'Unresolved', 'not-applicable': 'Does not apply'}
DATE_KINDS = {'context', 'upper-bound', 'estimate', 'production',
              'selected range', 'model estimate', 'documentary observation',
              'historical witness', 'collection'}


def selection():
    """Replay the saved searches in ID order; never silently skip missing metadata."""
    batches = []
    selected = set()
    for key, query in [('horus', 'Horus'), ('thoth', 'Thoth'),
                       ('spirit', 'winged protective spirit'), ('panel', 'Relief panel')]:
        path = DATA / f'search-{key}.json'
        response = json.loads(path.read_text())
        rows = []
        accepted = []
        for oid in sorted(response.get('objectIDs') or []):
            record_path = DATA / f'met-{oid}.json'
            record = json.loads(record_path.read_text())
            reason = ''
            if key == 'panel' and record['culture'] != 'Assyrian':
                reason = 'Outside the documented Assyrian replacement batch'
            elif oid in selected:
                reason = 'Physical object already selected'
            elif not record['isPublicDomain'] or not record['primaryImageSmall']:
                reason = 'No public-domain display image'
            elif not record['objectBeginDate'] or not record['objectEndDate']:
                reason = 'Numeric dates missing; zero is not an ancient date'
            elif record['objectEndDate'] > 600:
                reason = 'After the date cutoff'
            elif key == 'thoth' and 'priest of thoth' in record['title'].casefold():
                reason = 'The title depicts a priest, not Thoth'
            elif not record['title']:
                reason = 'Missing museum title'
            rows.append(dict(id=oid, title=record['title'], date=record['objectDate'],
                             decision='excluded' if reason else 'included', reason=reason or 'Eligible in ID order',
                             path=str(record_path.relative_to(ROOT)),
                             sha256=hashlib.sha256(record_path.read_bytes()).hexdigest()))
            if not reason:
                selected.add(oid)
                accepted.append(oid)
                if len(accepted) == 4:
                    break
        batches.append(dict(query=query, returned=response['total'], inspected=rows,
                            selected=accepted, path=str(path.relative_to(ROOT)),
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return dict(status='Exploratory retrieval audit; not a random sample or AI result',
                rules_sha256=hashlib.sha256((RESEARCH/'SELECTION.md').read_bytes()).hexdigest(),
                batches=batches, selected=sorted(selected), prior_anchor=322614,
                note='The twelve new museum objects are separate from nine focal/local records and one previously proposed Assyrian anchor. Prefetched records beyond the stopping point are not extra observations.')


def validate(data, check_files=True):
    for key in ('objects', 'sources', 'features', 'events', 'hypotheses'):
        ids = [row['id'] for row in data[key]]
        if len(ids) != len(set(ids)):
            raise ValueError(f'Duplicate {key}')
        if any(not re.fullmatch(r'[a-z0-9-]+', value) for value in ids):
            raise ValueError('Invalid record identity')
    sources = {s['id'] for s in data['sources']}
    objects = {o['id'] for o in data['objects']}
    features = {f['id'] for f in data['features']}
    physical_ids = [o['physical_id'] for o in data['objects']]
    if not all(physical_ids) or len(physical_ids) != len(set(physical_ids)):
        raise ValueError('Repeated or missing physical object identity')
    for s in data['sources']:
        if urlsplit(s['url']).scheme != 'https' or not urlsplit(s['url']).netloc:
            raise ValueError('Unsafe source URL')
    for obj in data['objects']:
        if set(obj['observations']) != features or not obj['scope']:
            raise ValueError('Incomplete observation scope')
        if not obj['sources'] or not set(obj['sources']) <= sources:
            raise ValueError('Unsupported object')
        for feature in obj['observations'].values():
            if feature['state'] not in STATES or not feature['note']:
                raise ValueError('Invalid observation')
        if obj['observations']['relation']['state'] == 'present':
            if any(obj['observations'][f]['state'] != 'present' for f in ('beak','reach','round')):
                raise ValueError('A relation needs its components in the same scope')
        im = obj['image']
        if not all(im[k] for k in ('credit','rights','origin','transformation','width','height','sha256')):
            raise ValueError('Incomplete image provenance')
        if (urlsplit(im['origin']).scheme != 'https' or not urlsplit(im['origin']).netloc
                or not (DOCS/im['path']).resolve().is_relative_to(DOCS.resolve())):
            raise ValueError('Unsafe image reference')
        ids = [m['id'] for m in im['annotations']]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate annotations')
        for mark in im['annotations']:
            x,y,w,h = mark['box']
            if min(x,y) < 0 or min(w,h) <= 0 or x+w > 1 or y+h > 1:
                raise ValueError('Annotation outside source image')
        if check_files and hashlib.sha256((DOCS/im['path']).read_bytes()).hexdigest() != im['sha256']:
            raise ValueError('Source photograph changed')
        validate_date(obj['date'])
    for row in data['events']:
        validate_date(row)
        if not row['sources'] or not set(row['sources']) <= sources or not set(row['objects']) <= objects:
            raise ValueError('Unsupported historical event')
    for row in data['hypotheses'] + data['findings']:
        if not row['sources'] or not set(row['sources']) <= sources:
            raise ValueError('Unsupported interpretation')
    if check_files:
        expected = {f'met-{oid}' for oid in selection()['selected']} | {'met-322614'}
        actual = {o['id'] for o in data['objects'] if o['group'] in ('museum','anchor')}
        if actual != expected:
            raise ValueError('Museum collection differs from selection rules')
        catalogue = json.loads((ROOT/'research/catalogue/catalogue.json').read_text())
        entities = {e['id']: e for e in catalogue['entities']}
        for obj in data['objects']:
            if obj.get('catalogue_entity'):
                entity = entities.get(obj['catalogue_entity'])
                if not entity or entity['physical_id'] != obj['physical_id']:
                    raise ValueError('Unresolved catalogue object identity')


def validate_date(d):
    lo, hi = d['start'], d['end']
    if (any(v is not None and (type(v) is not int or v == 0) for v in (lo, hi))
            or (lo is not None and hi is not None and lo > hi)):
        raise ValueError('Invalid date interval')
    if d['kind'] not in DATE_KINDS:
        raise ValueError('Missing date scope')
    if d['kind'] == 'upper-bound' and (lo is not None or hi is None):
        raise ValueError('An upper bound is not a production interval')


def refs(ids, data):
    by_id = {s['id']:s for s in data['sources']}
    return ' · '.join(a('#source-'+sid, by_id[sid]['title']) for sid in ids)


def photo(obj, guides=True):
    im=obj['image']; marks=[]
    for n,m in enumerate(im['annotations'],1):
        x,y,w,h=m['box']; scale=1000
        marks.append(f'<g><title>{esc(m["label"]+": "+m["note"])}</title><rect x="{x*scale:g}" y="{y*scale:g}" width="{w*scale:g}" height="{h*scale:g}"/><text x="{x*scale+5:g}" y="{y*scale+22:g}">{n}</text></g>')
    # The image and SVG share the same intrinsic aspect ratio, even in letterboxing.
    overlay=f'<svg class="fw-overlay" viewBox="0 0 1000 1000" preserveAspectRatio="none" aria-hidden="true">{"".join(marks)}</svg>' if guides else ''
    return f'<div class="fw-photo"><div class="fw-image-plane" style="--image-ratio:{im["width"]/im["height"]:.8f}"><img src="{esc(im["path"])}" width="{im["width"]}" height="{im["height"]}" alt="{esc(obj["label"]+". "+obj["scope"])}" loading="lazy">{overlay}</div></div>'


def panel(obj, side, data):
    options=''.join(f'<option value="{o["id"]}"{" selected" if o["id"]==obj["id"] else ""}>{esc(o["label"]+" · "+o["number"])}</option>' for o in data['objects'])
    im=obj['image']
    marks=''.join(f'<li><b>{i}. {esc(m["label"])}</b> {esc(m["note"])}</li>' for i,m in enumerate(im['annotations'],1))
    return f'''<article class="fw-panel" id="panel-{side}"><label class="fw-select fw-interactive" hidden>{'First' if side=='left' else 'Second'} object<select id="select-{side}">{options}</select></label>
{photo(obj)}<div class="fw-panel-copy"><div class="micro">{esc(obj['culture'])}</div><h3>{esc(obj['label'])}</h3><p class="fw-date">{esc(obj['date']['label'])}</p><p>{esc(obj['reading'])}</p><button class="fw-zoom fw-interactive" data-side="{side}" type="button" hidden>Enlarge photograph ↗</button>
<details><summary>Image, annotations &amp; sources</summary><p class="fw-small">{esc(im['credit'])} · {esc(im['rights'])} <a href="{esc(im['origin'])}">Source image / record</a>.</p><ol class="fw-annotation-list">{marks}</ol><p class="fw-small">{refs(obj['sources'],data)}</p><p class="fw-small">{esc(obj['date']['note'])}</p></details></div></article>'''


def matrix(left,right,data):
    rows=[]
    for f in data['features']:
        cells=[]
        for obj in (left,right):
            cell=obj['observations'][f['id']]
            cells.append(f'<td><span class="fw-state {cell["state"]}">{LABELS[cell["state"]]}</span>{esc(cell["note"])}</td>')
        rows.append(f'<tr><th scope="row">{esc(f["label"])}</th>{"".join(cells)}</tr>')
    return f'<div class="table-scroll"><table class="feature-matrix fw-matrix"><caption>Readings within the stated scene and photograph. “Not seen” is not absence from the whole object or culture.</caption><thead><tr><th>Relationship</th><th>{esc(left["label"])}</th><th>{esc(right["label"])}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def collection(data):
    cards=[]
    for obj in data['objects']:
        im=obj['image']
        cards.append(f'''<article class="fw-card" id="object-{obj['id']}" data-object="{obj['id']}"><a href="{esc(im['path'])}" class="fw-card-image"><img src="{esc(im['path'])}" width="{im['width']}" height="{im['height']}" alt="{esc(obj['label'])}" loading="lazy"></a><div class="fw-card-copy"><div class="micro">{esc(obj['culture'])}</div><h3>{esc(obj['label'])}</h3><p class="fw-date">{esc(obj['number'])}<br>{esc(obj['date']['label'])}</p><p>{esc(obj['reading'])}</p><button type="button" class="fw-choose fw-interactive" data-choose="{obj['id']}" hidden>Compare with first object ↗</button><details><summary>Full observation record</summary><p class="fw-small">Scope: {esc(obj['scope'])}</p><dl>{''.join(f'<dt>{esc(f["label"])}</dt><dd>{esc(obj["observations"][f["id"]]["note"])}</dd>' for f in data['features'])}</dl><p class="fw-small">{esc(obj['date']['note'])}</p><p class="fw-small">{refs(obj['sources'],data)}</p><p class="fw-small">{esc(im['credit'])}. {esc(im['rights'])}</p></details></div></article>''')
    return '<div class="fw-grid">'+''.join(cards)+'</div>'


def history(data):
    records=[]
    for row in data['events']:
        examples=' · '.join(a('#object-'+oid,next(o['label'] for o in data['objects'] if o['id']==oid)) for oid in row['objects'])
        example_links = f"<p class='fw-small'>{examples}</p>" if examples else ''
        records.append(f'<article class="fw-event" id="event-{row["id"]}"><div><span class="micro">{esc(row["lane"])}</span><p class="fw-date">{esc(row["when"])}</p><span class="fw-kind">{esc(row["kind"])}</span></div><div><h3>{esc(row["label"])}</h3><p>{esc(row["finding"])}</p><p class="fw-limit">{esc(row["limit"])}</p><p class="fw-small">{refs(row["sources"],data)}</p>{example_links}</div></article>')
    return ''.join(records)


def page(data, audit):
    idx={o['id']:o for o in data['objects']}
    findings=''.join(f'<article><h3>{esc(f["title"])}</h3><p>{esc(f["text"])}</p><p class="fw-small">{refs(f["sources"],data)}</p></article>' for f in data['findings'])
    questions=''.join(f'<article class="fw-hypothesis" id="explanation-{h["id"]}"><h3>{esc(h["title"])}</h3><dl><dt>What we would expect</dt><dd>{esc(h["prediction"])}</dd><dt>Evidence in hand</dt><dd>{esc(h["evidence"])}</dd><dt>Still missing</dt><dd>{esc(h["missing"])}</dd><dt>The next useful check</dt><dd>{esc(h["next"])}</dd></dl><p class="fw-small">{refs(h["sources"],data)}</p></article>' for h in data['hypotheses'])
    source_rows=''.join(f'<article id="source-{s["id"]}"><h3>{a(s["url"],s["title"])}</h3><p>{esc(s["note"])}</p><p class="fw-small">{esc(s["locator"])} · {esc(s["kind"])}</p></article>' for s in data['sources'])
    audit_rows=''.join(f'<tr><th>{esc(b["query"])}</th><td>{b["returned"]}</td><td>{len(b["inspected"])}</td><td>{len(b["selected"])}</td></tr>' for b in audit['batches'])
    body=f'''<main id="main">
<header class="fw-heading cat-wrap"><a class="back-link" href="pillar-and-moai.html">← The pillar, the moai &amp; the bird</a><div class="micro">A closer investigation · 22 objects · September 2026</div><h1>The resemblance,<br><em>under a closer light.</em></h1><p>What persists when we compare the actual arrangements, their local alternatives and the dates behind them?</p><nav class="fw-jumps" aria-label="Investigation sections"><a href="#compare">Inspect the images ↓</a><a href="#collection">Explore the 22 objects ↓</a><a href="#history">Follow the evidence ↓</a></nav></header>
<section class="fw-section cat-wrap" id="compare"><div class="fw-section-head"><div><div class="micro">01 / Look closely</div><h2>A bird. A rounded form.<br>A particular relationship.</h2></div><p>Separate what the photograph shows from what its symbols might mean.</p></div>
<div class="fw-tools fw-interactive" hidden><div class="fw-presets"><button type="button" data-preset="boulder">Pillar &amp; boulder</button><button type="button" data-preset="moai">Pillar &amp; moai</button><button type="button" data-preset="local">Local bird imagery</button><button type="button" data-preset="assyria">Assyrian variants</button></div><label><input id="show-guides" type="checkbox" checked> Show annotation regions</label><button type="button" id="share-comparison">Copy this view ↗</button><span id="share-status" role="status"></span></div>
<div class="fw-comparison">{panel(idx['gt-p43'],'left',data)}{panel(idx['rn-boulder'],'right',data)}</div>
<p class="fw-small fw-review">Source-informed editorial annotations, prepared with AI. Independent review remains open. Regions are viewing aids, not archaeological tracings or model predictions.</p>
<div id="comparison-matrix">{matrix(idx['gt-p43'],idx['rn-boulder'],data)}</div>
<details class="fw-method"><summary>What counts as a shared feature?</summary>{''.join(f'<p><b>{esc(f["label"])}</b> — {esc(f["definition"])}</p>' for f in data['features'])}<p>These definitions were developed while inspecting the material. This is an exploratory reading exercise, not a preregistered similarity test. Agreement between AI readers would not substitute for independent archaeological review.</p></details></section>
<section class="fw-section cat-wrap" id="findings"><div class="micro">The current assessment</div><h2>A resemblance clarified.<br>A history still to establish.</h2><div class="fw-findings">{findings}</div></section>
<section class="fw-section cat-wrap" id="collection"><div class="fw-section-head"><div><div class="micro">02 / Give the comparison context</div><h2>The surrounding evidence.</h2></div><p>Three focal objects, six local examples, twelve museum selections and one previously proposed Assyrian comparison.</p></div><div class="fw-filter-tools fw-interactive" hidden><label>Look for<select id="motif-filter"><option value="all">All 22 objects</option><option value="beaks">Beaked figures</option><option value="round">Beaked figure + rounded form</option><option value="relation">Rounded form at the limb</option><option value="pairs">Facing beaked figures</option></select></label><label><input id="include-uncertain" type="checkbox"> Include uncertain readings</label><button type="button" id="reset-collection">Reset collection</button></div><p class="fw-small" id="collection-count" role="status">22 selected objects. These counts are not worldwide motif frequencies.</p><p class="fw-empty" id="collection-empty" hidden>No recorded matches under this definition.</p>{collection(data)}
<details class="fw-method" id="selection"><summary>How these objects were selected</summary><p>The nine focal/local records are retained in full. New museum batches were selected in ascending object-ID order under written source and date rules. The ordinary variants and incomplete views stay in the set.</p><div class="table-scroll"><table class="feature-matrix"><thead><tr><th>Museum title query</th><th>Returned</th><th>Inspected to stopping point</th><th>Included</th></tr></thead><tbody>{audit_rows}</tbody></table></div><p>The first spirit query returned a modern locket with zero numeric dates. It was excluded; a documented Assyrian relief query replaced it. Horus queries retained mother-and-infant scenes. Thoth priest shabtis were excluded because they depict priests.</p><p>The selected set can expose reading errors and alternative arrangements. Its search terms, image availability and small quotas do not support a global rarity estimate. Related objects from one palace are not independent traditions.</p><div class="dossier-links"><a href="data/pillar-moai/fieldwork/selection.md">Selection rules &amp; amendments</a><a href="data/pillar-moai/fieldwork/selection.json">Every inspected inclusion / exclusion</a><a href="data/pillar-moai/fieldwork/register.json">Observations, dates &amp; image hashes</a></div></details></section>
<section class="fw-section cat-wrap" id="history"><div class="fw-section-head"><div><div class="micro">03 / Follow the dated evidence</div><h2>What connects—and<br>where the trail stops.</h2></div><p>Dates belong to a particular event. A photograph dates a record; a statue’s age does not date every later carving.</p></div><div class="fw-interactive" hidden><div class="fw-timeline-tools"><button type="button" data-era="all" aria-pressed="true">Full timespan</button><button type="button" data-era="recent" aria-pressed="false">Recent millennia</button></div><div class="fw-timeline" id="evidence-timeline" tabindex="0" role="region" aria-label="Dated evidence chart; full text records follow"></div><p class="fw-small">Solid ranges: object attribution or model estimate. Outlined ranges: broad context. Diamonds: documentary bounds or records. No connecting line implies transmission.</p></div>{history(data)}<p class="fw-small"><a href="data/pillar-moai/fieldwork/search-log.md">Sources checked, access limits &amp; leads still to follow →</a></p></section>
<section class="fw-section cat-wrap" id="explanations"><div class="micro">04 / Competing explanations</div><h2>What would change the answer?</h2><div class="fw-hypotheses">{questions}</div><p class="fw-small">These are competing research expectations, not probabilities or exclusive historical categories. Inheritance, borrowing and local reinvention can coexist.</p></section>
<section class="fw-section cat-wrap" id="next"><div class="micro">The next experiment</div><h2>Check the observer, then compare.</h2><p class="fw-lead">Review the feature regions independently, acquire matched alternate views, then freeze a new recognition test. A correct word at the wrong location should fail. The present collection is development material.</p><p><a href="data/next-tests.md">Proposed test and outstanding reference work →</a> · <a href="view-trial.html">Earlier experiment records</a></p></section>
<section class="fw-section cat-wrap" id="sources"><details class="fw-sources"><summary>Sources and access notes</summary><div>{source_rows}</div></details></section>
<dialog id="photo-dialog" aria-label="Enlarged source photograph"><button type="button" id="close-photo" aria-label="Close enlarged photograph">Close ×</button><div id="dialog-photo"></div><p id="dialog-caption" class="fw-small"></p></dialog>
</main>'''
    return shell('The resemblance, under a closer light','Inspect 22 source-linked objects, literal visual relationships and the dated evidence behind the pillar–moai–boulder question.',body,extra='<link rel="stylesheet" href="fieldwork.css?v=1"><script type="module" src="fieldwork.js?v=1"></script>')


def outputs():
    data=json.loads((RESEARCH/'register.json').read_text())
    validate(data)
    audit=selection()
    return {DOCS/'fieldwork.html':page(data,audit),
            DOCS/'data/pillar-moai/fieldwork/register.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',
            DOCS/'data/pillar-moai/fieldwork/selection.json':json.dumps(audit,ensure_ascii=False,indent=2)+'\n',
            DOCS/'data/pillar-moai/fieldwork/selection.md':(RESEARCH/'SELECTION.md').read_text(),
            DOCS/'data/pillar-moai/fieldwork/search-log.md':(RESEARCH/'SEARCH-LOG.md').read_text()}
