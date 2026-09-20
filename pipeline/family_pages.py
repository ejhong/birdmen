"""Motif-first browsing and source intake. No inferred motif memberships."""
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
try:
    from pipeline.catalogue import ROOT, DOCS, esc, a, shell, picture
except ModuleNotFoundError:
    from catalogue import ROOT, DOCS, esc, a, shell, picture


def observations(family, data):
    return [o for o in data['attestations'] if o['family'] == family['id']]


def family_card(f, data, idx):
    rows = observations(f, data)
    entities = [idx['entities'][o['entity']] for o in rows]
    cultures = {e['culture'] for e in entities} - {'unassigned'}
    leads = [l for l in data['leads'] if f['id'] in l['families'] and l['kind'] == 'claim']
    mids = [f['cover']] if f['cover'] else []
    first_culture = next((e['culture'] for e in entities if e['media'] == f['cover']), None)
    other = next((e['media'] for e in entities if e['media'] and e['media'] not in mids and e['culture'] != first_culture), None)
    if other and first_culture:
        mids.append(other)
    photos = ''.join(f'<img src="{esc(idx["media"][m]["path"])}" alt="{esc(idx["media"][m]["alt"])}" loading="lazy">' for m in mids)
    if not photos:
        labels = {'teaching-figures':'Arrival · teaching · departure', 'flood-sequences':'Warning · vessel · survival', 'stepped-monuments':'Form · construction · purpose'}
        photos = f'<div class="family-text-cover"><span>{esc(labels.get(f["id"],f["label"]))}</span><i aria-hidden="true">∿</i></div>'
    count = f'{len(cultures)} traditions · {len(entities)} records' if entities else 'Identifications pending'
    lead_count = f' · {len(leads)} '+('lead' if len(leads)==1 else 'leads') if leads else ''
    return f'''<article class="family-card" data-family="{f['id']}"><a class="family-link" href="families/{f['id']}.html"><div class="family-images images-{len(mids)}">{photos}</div><div class="family-copy"><div class="micro">{'Motif family' if rows else 'From the inputs'}</div><h3>{esc(f['label'])}</h3><p>{esc(f['summary'])}</p><div class="family-count">{count}{lead_count}<span aria-hidden="true">↗</span></div></div></a></article>'''


def lead_html(l, idx, prefix='../'):
    images = ''.join(f'<figure><a href="{esc(prefix+m["path"])}"><img src="{esc(prefix+m["path"])}" alt="{esc(m["alt"])}" loading="lazy"></a><figcaption>{esc(m["caption"])}<br>{esc(m["credit"])} {esc(m["rights"])}</figcaption></figure>' for m in (idx['media'][mid] for mid in l['media']))
    panels = ''
    if l['panels']:
        rows = ''.join(f'<tr><th scope="row">{esc(p["id"])}</th><td>{esc(p["label"])}</td><td>{esc(idx["entities"][p["entity"]]["label"]) if p.get("entity") else "Identity open"}</td></tr>' for p in l['panels'])
        panels = f'<details><summary>Panel-by-panel intake ({len(l["panels"])})</summary><div class="table-scroll"><table class="feature-matrix"><thead><tr><th>Panel</th><th>Caption / lead</th><th>Object match</th></tr></thead><tbody>{rows}</tbody></table></div></details>'
    sources = ' · '.join(a(idx['sources'][sid]['url'],idx['sources'][sid]['title'],prefix) for sid in l['sources'])
    return f'''<article class="intake-lead" id="lead-{l['id']}"><div class="micro">{'Correction recorded' if l['status']=='corrected' else 'Identification open'} · {esc(l['kind'])}</div><h3>{esc(l['title'])}</h3><p>{esc(l['note'])}</p><details><summary>Images, source check &amp; next step</summary><div class="intake-images">{images}</div><p><b>Next:</b> {esc(l['next_step'])}</p>{panels}<p class="image-credit">{sources}</p></details></article>'''


def family_page(f, data, idx):
    obs = observations(f, data)
    cultures = list(dict.fromkeys(idx['entities'][o['entity']]['culture'] for o in obs))
    features = {v['id']:v['label'] for v in f['features']}
    groups=[]
    for cid in cultures:
        members=[]
        for o in obs:
            e=idx['entities'][o['entity']]
            if e['culture'] != cid:continue
            m=idx['media'].get(e['media'])
            dates=[e['dates'][n] for n in o['date_indices']]
            date_label=' / '.join(d['label'] for d in dates)
            date_records=''.join(f'<li><b>{esc(d["label"])}</b> · {esc(d["kind"])}<br>{esc(d["note"])} {a(idx["sources"][d["source"]]["url"],"Date source","../") if d["source"] else ""}</li>' for d in dates)
            refs=' · '.join(a(idx['sources'][s]['url'],idx['sources'][s]['title'],'../') for s in o['sources'])
            media=picture(e,idx,'../')
            if m:media=f'<a href="../{esc(m["path"])}" aria-label="Open full image of {esc(e["label"])}">{media}</a>'
            credits=f'<p class="image-credit">{esc(m["credit"])} {esc(m["rights"])} {a(m["url"],"Image record","../")}<br>{esc(m["transformation"])}</p>' if m else ''
            chips=''.join(f'<span>{esc(features[k])}</span>' for k in o['features'])
            members.append(f'''<article class="family-member" id="record-{o['id']}"><div class="family-member-image">{media}</div><div><div class="micro">{'Source-linked observation' if o['status']=='documented' else 'Provisional reading'}</div><h3>{esc(e['label'])}</h3><p class="family-episode">{esc(date_label)}</p><div class="feature-chips">{chips}</div><p>{esc(o['note'])}</p><details><summary>Episode, sources &amp; image</summary><p><b>Observation scope:</b> {esc(o['scope'])}</p><ul class="date-records">{date_records}</ul><p class="image-credit">{refs}</p>{credits}</details></div></article>''')
        groups.append(f'<section class="family-culture" id="culture-{cid}"><header><div class="micro">Cultural context</div><h2>{esc(idx["cultures"][cid]["label"])}</h2></header><div class="family-members">{"".join(members)}</div></section>')
    table_rows=[]
    for o in obs:
        e=idx['entities'][o['entity']]
        cells=''.join(f'<td>{"Recorded" if o["status"]=="documented" else "Provisional"}</td>' if fid in o['features'] else '<td><span aria-label="Not recorded">—</span></td>' for fid in features)
        table_rows.append(f'<tr><th scope="row"><a href="#record-{o["id"]}">{esc(e["label"])}</a><small>{esc(o["scope"])}</small></th>{cells}</tr>')
    matrix=f'<details class="family-matrix"><summary>Compare the recorded features</summary><p>Each row describes one object, surface or textual scope. A dash means “not recorded”, not “absent”. Features across different rows do not establish co-occurrence.</p><div class="table-scroll"><table class="feature-matrix"><thead><tr><th>Record &amp; scope</th>{"".join(f"<th>{esc(v)}</th>" for v in features.values())}</tr></thead><tbody>{"".join(table_rows)}</tbody></table></div></details>' if obs else ''
    if f['id'] in ('bird-figures', 'bird-round-form'):
        matrix = '<p class="family-scope"><a href="../fieldwork.html">A closer study: compare 22 objects, visual relationships and dated histories →</a></p>' + matrix
    leads=[l for l in data['leads'] if f['id'] in l['families']]
    questions=[l for l in leads if l['kind']=='claim']
    controls=[l for l in leads if l['kind']!='claim']
    lead_section=f'<section class="family-leads"><div class="section-top"><div><div class="micro">The identification queue</div><h2>Leads worth following.</h2></div><p>Preserved claims and images, awaiting the checks needed for object records.</p></div>{"".join(lead_html(l,idx) for l in questions)}</section>' if questions else ''
    control_section=f'<details class="family-controls"><summary>Context &amp; controls ({len(controls)})</summary>{"".join(lead_html(l,idx) for l in controls)}</details>' if controls else ''
    links=''.join(f'<a class="related-item" href="../catalogue/{c["id"]}.html"><span class="micro">Proposed connection</span><strong>{esc(c["title"])}</strong><span>Evidence · map · dates →</span></a>' for c in (idx['claims'][id] for id in f['claims']))
    body=f'''<main id="main"><header class="dossier-heading cat-wrap"><a class="back-link" href="../catalogue.html">← Motif families</a><div class="micro">Across cultural traditions</div><h1>{esc(f['label'])}</h1><p class="dossier-deck">{esc(f['summary'])}</p><nav class="family-jumps" aria-label="Cultural contexts in this family">{' '.join(a('#culture-'+cid,idx['cultures'][cid]['label']) for cid in cultures)}</nav><p class="family-scope">{len(obs)} selected records · {len(questions)} intake {'lead' if len(questions)==1 else 'leads'}. Membership records a resemblance; it does not establish common origin.</p></header><div class="cat-wrap">{matrix}{''.join(groups)}{lead_section}{control_section}{f'<section class="related-section"><h2>The proposed connections.</h2><div class="related-grid">{links}</div></section>' if links else ''}<p class="family-closing"><a href="../input-audit.html">Input coverage &amp; corrections</a> · <a href="https://github.com/ejhong/birdmen/issues/new">Add an image or source</a></p></div></main>'''
    return shell(f['label'],f['summary'],body,'../',extra='<script src="../catalogue-dossier.js" defer></script>')


def validate_coverage(coverage, idx):
    seen=set()
    for row in coverage['files']:
        p=(ROOT/row['path']).resolve()
        if row['path'] in seen or not p.is_relative_to(ROOT/'inputs') or not p.is_file():
            raise ValueError('Invalid input coverage path')
        seen.add(row['path'])
        if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Input changed since audit: '+row['path'])
        if not set(row['claims'])<=set(idx['claims']) or not set(row['leads'])<=set(idx['leads']):
            raise ValueError('Unresolved input coverage reference')
        if row['status'] not in ('catalogued','lead recorded','context','unresolved') or not row.get('note'):
            raise ValueError('Unqualified input coverage')
    actual={str(p.relative_to(ROOT)) for p in (ROOT/'inputs').rglob('*') if p.is_file() and p.name!='.DS_Store'}
    if seen!=actual:raise ValueError('Inputs added or removed: update the coverage audit')
    for l in idx['leads'].values():
        if not l['inputs'] or not {'inputs/'+p for p in l['inputs']} <= seen:
            raise ValueError('Lead has no preserved input')


def audit_page(coverage,data,idx):
    rows=[]
    for r in coverage['files']:
        destinations=[a('catalogue/'+c+'.html',idx['claims'][c]['title']) for c in r['claims']]
        destinations += [a('input-audit.html#lead-'+l,idx['leads'][l]['title']) for l in r['leads']]
        if not destinations:destinations=[a(r['destination'],'Context record')]
        raw='https://github.com/ejhong/birdmen/blob/main/'+quote(r['path'])
        rows.append(f'<tr><th scope="row">{a(raw,r["path"].removeprefix("inputs/"))}<small>{esc(r["status"])}</small></th><td>{"<br>".join(destinations)}<p>{esc(r["note"])}</p></td></tr>')
    lead_sections=''.join(lead_html(l,idx,'') + '<p class="lead-family-links">'+ ' · '.join(a('families/'+f+'.html',idx['families'][f]['label']) for f in l['families'])+'</p>' for l in data['leads'])
    body=f'''<main id="main"><header class="dossier-heading cat-wrap"><a class="back-link" href="catalogue.html">← The collection</a><div class="micro">Source intake · {coverage['edition']}</div><h1>Every input.<br><em>A place to follow it.</em></h1><p class="dossier-deck">{len(coverage['files'])} files accounted for. Missing comparisons are now recorded; source verification remains open where the evidence is thin.</p><div class="dossier-links"><a href="#coverage">File-by-file coverage ↓</a><a href="#leads">New leads &amp; corrections ↓</a><a href="data/input-coverage.json">Download the audit ↗</a></div></header><section class="cat-wrap audit-findings"><article><div class="micro">A useful control</div><h2>The modern Gilgamesh.</h2><p>The lion-holder at Sydney was unveiled in 2000. An ancient-looking image can preserve a modern connection. {a(idx['sources']['sydney']['url'],'University archive')}</p></article><article><div class="micro">One object, twice</div><h2>La Venta’s changing labels.</h2><p>Two panels of the “Coincidence?” montage repeat Monument 19. Its Olmec identity replaces the conflicting regional labels; the Egyptian and Māori panels remain untraced.</p></article></section><section class="cat-wrap" id="coverage"><details class="coverage-register"><summary>All {len(coverage['files'])} files and their destinations</summary><p>“Accounted for” includes unresolved fragments, extra views and contextual arguments. AI planning drafts are preserved as proposals, not source verification.</p><div class="table-scroll"><table class="feature-matrix"><thead><tr><th>Supplied file</th><th>Where it is captured</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></details></section><section class="cat-wrap family-leads" id="leads"><h2>Leads &amp; corrections.</h2>{lead_sections}</section></main>'''
    return shell('Input coverage','The supplied-image audit: captured comparisons, duplicate objects, corrected labels and unresolved leads.',body)


def outputs(data,idx):
    coverage=json.loads((ROOT/'research/catalogue/input-coverage.json').read_text())
    validate_coverage(coverage,idx)
    out={DOCS/'input-audit.html':audit_page(coverage,data,idx),DOCS/'data/input-coverage.json':json.dumps(coverage,ensure_ascii=False,indent=2)+'\n'}
    for f in data['families']:
        out[DOCS/'families'/(f['id']+'.html')]=family_page(f,data,idx)
    return out
