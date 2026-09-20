"""Publish source registers and study summaries without running any paid AI calls.

    python3 pipeline/publish.py
    python3 pipeline/publish.py --check

Only marked generated sections and explicitly listed publishing assets are written.
Original experiment data, prompts and preregistrations are never modified. Supplied
images are copied unchanged; crops of supplied screenshots are made separately by
crop_inputs.py and only checked for presence here.
"""
import argparse
import html
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def esc(value):
    return html.escape(str(value), quote=True)


def link(url, label):
    return f'<a href="{esc(url)}">{esc(label)}</a>'


def links(items):
    return " ".join(link(v["url"], v["label"]) for v in items)


def replace_region(text, name, content):
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"Expected one complete generated region: {name}")
    return re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end),
                  lambda _: f"{start}\n{content}\n{end}", text)


def cards(studies):
    out = ['<div class="collection-grid">']
    for s in studies:
        out.append(f'''<article class="investigation" aria-labelledby="study-{esc(s['id'])}">
  <div class="eyebrow">{esc(s['number'])} · {esc(s['status'])}</div>
  <h3 id="study-{esc(s['id'])}">{link(s['url'], s['title'])}</h3>
  <p>{esc(s['summary'])}</p>
  <div class="versions">{link(s['url'], 'Evidence & method →')}</div>
</article>''')
    return "\n".join(out + ["</div>"])


def review(s, prefix=''):
    up = (lambda url: url if url.startswith(('http', '#')) else prefix + url)
    versions = ' '.join(link(up(v['url']), v['label']) for v in s['versions'])
    return f'''<aside class="study-review wrap" aria-label="Study scope and limitations">
  <div class="review-box"><div class="eyebrow">Reading this investigation · updated September 2026</div>
  <h2>{esc(s['question'])}</h2>
  <dl><div><dt>What remains useful</dt><dd>{esc(s['finding'])}</dd></div><div><dt>What it cannot settle</dt><dd>{esc(s['limitations'])}</dd></div></dl>
  <div class="reading-links">{link(prefix + '#investigations' if prefix else './#investigations', 'All investigations')} {link('#limits', 'Full limitations')} {versions}</div></div>
</aside>'''


def reference(e, sources):
    source = sources[e["source"]]
    return link(e.get("url", source["url"]), e["locator"])


def render_evidence(data):
    sources = {s["id"]: s for s in data["sources"]}
    figures = {f["id"]: f for f in data["figures"]}
    out = []
    for e in data["passages"]:
        figure = figures[e["figure"]]
        excerpt = f'<blockquote class="excerpt" lang="{esc(e.get("language", "en"))}">“{esc(e["excerpt"])}”</blockquote>' if e.get("excerpt") else ""
        out.append(f'''<article class="evidence-card" id="{esc(e['id'])}" data-figure="{esc(e['figure'])}" data-group="{esc(figure['group'])}">
  <div class="eyebrow">{esc(figure['name'])} · {esc(e['id'])}</div>
  <h3>{esc(e['title'])}</h3>
  {excerpt}
  <p>{esc(e['paraphrase'])}</p>
  <p class="qualification">{esc(e['qualification'])}</p>
  <p class="locator">{link('#source-' + e['source'], sources[e['source']]['short'])} · {reference(e, sources)}<br>Short source excerpt; explanation is this project's paraphrase. {esc(e['checked'])}</p>
</article>''')
    return "\n".join(out)


def render_sources(data):
    out = ['<div class="source-list">']
    for s in data["sources"]:
        out.append(f'''<article class="source-record" id="source-{esc(s['id'])}">
  <div class="eyebrow">{esc(s['id'])} · {esc(s['kind'])}</div><h3>{link(s['url'], s['title'])}</h3>
  <dl><dt>Composition / record</dt><dd>{esc(s['composition'])}</dd><dt>Witness and edition inspected</dt><dd>{esc(s['edition'])}</dd><dt>Source family / mediation</dt><dd>{esc(s['mediation'])}</dd><dt>Still to check</dt><dd>{esc(s['open_questions'])}</dd></dl>
</article>''')
    return "\n".join(out + ["</div>"])


def render_matrix(data):
    fields = [("arrival", "Arrives from the sea?"), ("teaching", "Named skills / institutions"), ("departure", "Sea departure?"), ("return", "Promises own return?")]
    out = ['<div class="frame"><table class="inv evidence-matrix"><caption class="cap">What the inspected accounts say. A blank in the historical record is not a negative result.</caption><thead><tr><th scope="col">Figure</th>']
    out.extend(f'<th scope="col">{label}</th>' for _, label in fields)
    out.append('</tr></thead><tbody>')
    for f in data["figures"]:
        out.append(f'<tr><th scope="row">{esc(f["name"])}<br><span class="kicker">{esc(f["group"])}</span></th>')
        for key, _ in fields:
            c = f["comparison"][key]
            refs = " · ".join(link('#' + p, p) for p in c["evidence"])
            out.append(f'<td>{esc(c["text"])}<br><span class="kicker">{esc(c["status"].replace("_", " "))}</span><br><span class="locator">{refs}</span></td>')
        out.append('</tr>')
    return "\n".join(out + ['</tbody></table></div>'])


def validate(data):
    source_ids = [s["id"] for s in data["sources"]]
    figure_ids = [f["id"] for f in data["figures"]]
    passage_ids = [e["id"] for e in data["passages"]]
    for name, values in [("sources", source_ids), ("figures", figure_ids), ("passages", passage_ids)]:
        if len(values) != len(set(values)):
            raise ValueError(f"Duplicate {name}")
    for e in data["passages"]:
        if e["source"] not in source_ids or e["figure"] not in figure_ids:
            raise ValueError(f"Invalid reference in {e['id']}")
        for key in ("locator", "paraphrase", "qualification", "checked"):
            if not e.get(key):
                raise ValueError(f"Missing {key}: {e['id']}")
    for f in data["figures"]:
        if set(f["comparison"]) != {"arrival", "teaching", "departure", "return"}:
            raise ValueError(f"Incomplete comparison: {f['id']}")
        for cell in f["comparison"].values():
            if cell["status"] not in {"present", "contradicted", "not_mentioned", "uncertain"}:
                raise ValueError(f"Invalid observation status: {f['id']}")
            if not cell["evidence"] or not set(cell["evidence"]) <= set(passage_ids):
                raise ValueError(f"Unsupported matrix cell: {f['id']}")
            owners = {e["figure"] for e in data["passages"] if e["id"] in cell["evidence"]}
            if f["id"] not in owners:
                raise ValueError(f"Mismatched figure evidence: {f['id']}")


def validate_case(register):
    ids = [s['id'] for s in register['sources']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate case source')
    for item in register['images']:
        if item['source'] not in ids:
            raise ValueError('Unsupported case image')
        path = ROOT / item['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'Case photograph changed: {path}')
        if not all(item.get(k) for k in ['credit', 'rights', 'transformation', 'origin']):
            raise ValueError('Incomplete image provenance')


def case_sources(register):
    return '<div class="case-sources">' + '\n'.join(
        f'<article id="source-{esc(s["id"])}"><h3>{link(s["url"], s["title"])}</h3>'
        f'<p class="source-inline">{esc(s["author"])} · {esc(s["date"])}</p><p>{esc(s["note"])}</p></article>'
        for s in register['sources']) + '</div>'


def case_images(register):
    sources = {s['id']: s for s in register['sources']}
    return '<ul class="source-inline">' + '\n'.join(
        f'<li>{link(i["path"].removeprefix("docs/"), Path(i["path"]).name)} — '
        f'{esc(i["credit"])}. {esc(i["rights"])}. {esc(i["transformation"])}. '
        f'{link(sources[i["source"]]["url"], "Context / record")}.</li>'
        for i in register['images']) + '</ul>'


def recognition_results(result, reference):
    t = result['totals']
    all_pct = f'{100 * result["accuracy_all"]:.1f}%'
    received = result['scorable'] - t['missing']
    observed_pct = f'{100 * t["correct"] / received:.1f}%' if received else 'not available'
    out = [f'''<div class="lab-summary"><div class="eyebrow">Frozen diagnostic · {esc(result['model'])}</div>
<h3>The recognition screen was {'passed' if result['screening_pass'] else 'not passed'}.</h3>
<p><b>{result['completed_requests']} of {result['planned_requests']} planned responses</b> completed.
{t['correct']} of {result['scorable']} scorable answers matched the provisional references ({all_pct}, counting missing answers).
Among received scorable answers, {t['correct']} of {received} matched ({observed_pct}).</p>
<p>{t['wrong']} wrong · {t['abstained']} uncertain · {t['missing']} missing.
The missing answers come from a request that failed with a connection error; they are not model perception errors.
The received answers also fall below the frozen 90% threshold.</p>
<p>Independent review: <b>{esc(result['independent_review'].replace('_', ' '))}</b>.
Historical ranking: <b>not permitted</b>. This purposive pilot does not estimate the model’s general accuracy or the resemblance’s rarity.</p></div>''']
    names = dict(avian='Bird / bird-headed figure', large_face='Large human face', scorpion='Scorpion', round_motif='Standalone round motif', three_arches='Three arched forms')
    out.append('<div class="recognition-records">')
    for im in reference['images']:
        rows = [r for r in result['rows'] if r['id'] == im['id']]
        score = sum(c['outcome'] == 'correct' for r in rows for c in r['cells'].values())
        count = sum(len(r['cells']) for r in rows)
        out.append(f'<details class="recognition-record" id="result-{esc(im["id"])}"><summary>{esc(im["label"])} <span>{score}/{count} reference matches</span></summary><div class="recognition-body">')
        out.append(f'<figure><div class="recognition-photo"><img src="{esc(im["path"].removeprefix("docs/"))}" alt="{esc(im["label"])}" loading="lazy"><div class="model-box" hidden></div></div><figcaption>Unaltered input photograph. {link(im["source_url"], "Reference source")}. Model boxes are unverified claims of location.</figcaption><button class="btn clear-box" type="button">Clear location box</button></figure><div>')
        out.append('<table class="read-table"><thead><tr><th scope="col">Feature</th><th scope="col">Reference</th><th scope="col">Run 1</th><th scope="col">Run 2</th></tr></thead><tbody>')
        for f, label in names.items():
            expected = im['expected'][f] or 'not scored'
            out.append(f'<tr><th scope="row">{label}</th><td>{esc(expected)}</td>')
            for row in rows:
                cell = row['cells'].get(f, {})
                obs = row.get('observation', {}).get(f, {})
                answer = obs.get('answer', cell.get('answer')) or 'missing'
                box = obs.get('box')
                content = esc(answer)
                if box:
                    content = f'<button type="button" class="box-link" data-box="{esc(",".join(map(str, box)))}" aria-label="Show run {row["repeat"]} location for {esc(label)}">{content} ↗</button>'
                out.append(f'<td class="outcome-{esc(cell.get("outcome", "unscored"))}">{content}</td>')
            out.append('</tr>')
        out.append('</tbody></table>')
        for row in rows:
            out.append(f'<h4>Run {row["repeat"]} · {esc(row["status"].replace("_", " "))}</h4>')
            if row['description']:
                out.append(f'<p>{esc(row["description"])}</p>')
            else:
                out.append('<p>No model description was received.</p>')
            if row['observation']:
                out.append('<details><summary>Feature explanations and limitations</summary><dl class="observation-notes">')
                for f, label in names.items():
                    out.append(f'<dt>{label}</dt><dd>{esc(row["observation"][f]["evidence"])}</dd>')
                out.append(f'</dl><p>{esc(row["observation"]["limitations"])}</p></details>')
            raw_link = link(f'data/pillar-moai/raw/{im["id"]}-{row["repeat"]}.json', 'Full saved response / request record')
            out.append(f'<p class="source-inline">{raw_link}</p>')
        out.append('</div></div></details>')
    out.append('</div>')
    cross = result['cross_view']
    consistent = sum(v['consistent'] is True for v in cross)
    available = sum(v['consistent'] is not None for v in cross)
    out.append(f'<p class="source-inline">Repeat disagreement: {len(result["repeat_disagreements"])} scorable image-feature pairs changed answer between completed repeats. Cross-view consistency: {consistent}/{available} available feature comparisons agreed across two photographs in the same repeat. Agreement can still be wrong. {link("data/pillar-moai/results.json", "Complete machine-readable readout")}.</p>')
    return '\n'.join(out)


def context_objects(register):
    sources = {s['id']: s for s in register['sources']}
    seen = set()
    out = []
    for obj in register['objects']:
        if obj['id'] in seen or not set(obj['sources']) <= set(sources):
            raise ValueError('Invalid context object identity or source')
        seen.add(obj['id'])
        if any(not (ROOT / image).is_file() for image in obj['images']):
            raise ValueError('Missing context photograph')
        out.append(f'<details class="context-record" id="object-{esc(obj["id"])}"><summary>{esc(obj["name"])}'
                   f'<span>{esc(obj["region"])} · {esc(obj["record"])} · {esc(obj["inspection"])}</span></summary><dl>')
        for key, title in [('context', 'Context'), ('date_scope', 'What is dated?'), ('observation', 'Observation'), ('relevance', 'Why include it?')]:
            out.append(f'<dt>{title}</dt><dd>{esc(obj[key])}</dd>')
        out.append('</dl><p class="source-inline">' + ' · '.join(link('#source-' + s, sources[s]['title']) for s in obj['sources']) + '</p></details>')
    return '\n'.join(out)


def view_summary(result):
    out = ['<div class="trial-conditions">']
    for condition in result['conditions']:
        p, a, bird = condition['primary'], condition['all'], condition['avian']
        label = 'One photograph' if condition['views'] == 'single' else 'Two photographs'
        out.append(f'<article class="trial-condition"><div class="eyebrow">{esc(condition["effort"].title())} reasoning · {label}</div>'
                   f'<div class="trial-score">{p["correct"]}<span> / {p["total"]}</span></div><p>primary labels matched</p>'
                   f'<div class="trial-bar" aria-hidden="true"><span style="width:{100*p["correct"]/p["total"]:.0f}%"></span></div>'
                   f'<p class="source-inline">{p["wrong"]} wrong · {p["uncertain"]} uncertain · {p["missing"]} missing<br>'
                   f'Bird labels: {bird["correct"]}/{bird["total"]}<br>All feature labels: {a["correct"]}/{a["total"]}</p></article>')
    out.append('</div>')
    out.append(f'<p class="source-inline">{result["completed_requests"]}/{result["planned_requests"]} requests completed. '
               f'Estimated API cost: ${result["estimated_cost_usd"]:.2f}. Same model snapshot throughout: {esc(result["model"])}. '
               'All uncertainty and missing answers stay in the denominators. These counts include incorrectly located features.</p>')
    out.append('<h3>What changed when one factor changed?</h3><div class="result-table-wrap" tabindex="0" role="region" aria-label="Paired changes in primary feature labels"><table class="read-table"><caption class="source-inline">Primary checks only. Compare the same object and first photograph; no significance test or population claim.</caption><thead><tr><th scope="col">Change</th><th scope="col">Became correct</th><th scope="col">Became incorrect or uncertain</th><th scope="col">No change in correctness</th></tr></thead><tbody>')
    for factor, fixed, label in [('views', 'low', 'Add a view · low reasoning'), ('views', 'high', 'Add a view · high reasoning'),
                                  ('effort', 'single', 'Raise reasoning · one photograph'), ('effort', 'paired', 'Raise reasoning · two photographs')]:
        selected = [t for t in result['transitions'] if t['factor'] == factor and t['fixed'] == fixed and t['primary']]
        values = [sum(t['change'] == kind for t in selected) for kind in ('improved', 'worsened', 'no_correctness_change')]
        out.append(f'<tr><th scope="row">{label}</th>' + ''.join(f'<td>{v}</td>' for v in values) + '</tr>')
    out.append('</tbody></table></div><p class="source-inline">An incorrect answer becoming uncertain is not counted as correct. Two correct labels can still differ in their descriptions and locations.</p>')
    return '\n'.join(out)


def view_locations(audit, result):
    positives = {r['id']: r for r in result['rows'] if r['object'] == 'p43' and r.get('observation') and r['observation']['scorpion']['answer'] == 'present'}
    if {c['request'] for c in audit['cases']} != set(positives) or len(audit['cases']) != len(positives):
        raise ValueError('Location audit must show all positive Pillar 43 scorpion responses')
    out = ['<p class="location-key"><span class="model-key">Model’s scorpion box</span><span class="source-key">Source-assisted scorpion guide</span></p><div class="audit-photos">']
    for case in audit['cases']:
        row = positives[case['request']]
        if case['model_box'] != row['observation']['scorpion']['box'] or case['path'] != row['path']:
            raise ValueError('Location audit differs from saved response')
        out.append(f'<figure><div class="recognition-photo"><img src="{esc(case["path"].removeprefix("docs/"))}" alt="Pillar 43: model box on upper panel; source guide on the lower shaft" loading="lazy">')
        for key, css, label in [('model_box', 'audit-model', 'Model'), ('source_guide', 'audit-source', 'Source guide')]:
            left, top, right, bottom = case[key]
            if not 0 <= left < right <= 1 or not 0 <= top < bottom <= 1:
                raise ValueError('Invalid location guide')
            out.append(f'<div class="audit-box {css}" aria-hidden="true" style="left:{left*100}%;top:{top*100}%;width:{(right-left)*100}%;height:{(bottom-top)*100}%"><span>{label}</span></div>')
        views = 'One photograph' if row['views'] == 'single' else 'Two photographs'
        out.append(f'</div><figcaption><b>High reasoning · {views.lower()} · {"A" if row["order"] == 1 else "B"} first</b>'
                   f'{link("#request-" + row["id"], "Inspect this response")} · {link(case["path"].removeprefix("docs/"), "Photograph without overlays")}</figcaption></figure>')
    out.append('</div><p class="source-inline">Photographs © DAI / Göbekli Tepe Project; credits retained from the original study. Boxes locate areas, not individual carved lines. '
               + link(audit['source_url'], 'Excavation-team description') + ' · ' + link('data/pillar-moai/v3/location-audit.json', 'Audit scope and observations') + '.</p>')
    return '\n'.join(out)


def view_records(result):
    names = dict(avian='Bird / bird-headed figure', large_face='Large human face', scorpion='Scorpion', round_motif='Standalone round motif', three_arches='Three arched forms')
    out, previous = [], None
    for row in result['rows']:
        if row['object'] != previous:
            out.append(f'<h3 class="trial-object" id="responses-{esc(row["object"])}">{esc(row["label"])}</h3>')
            previous = row['object']
        observation = row['observation'] or {}
        score = sum(c['outcome'] == 'correct' for c in row['cells'].values())
        views = 'one photograph' if row['views'] == 'single' else 'two photographs'
        label = f'{row["effort"].title()} reasoning · {views} · {"A" if row["order"] == 1 else "B"} first'
        out.append(f'<details class="recognition-record" id="request-{esc(row["id"])}"><summary>{esc(label)} <span>{score}/{len(row["cells"])} labels matched</span></summary><div class="recognition-body"><figure>')
        out.append(f'<div class="recognition-photo"><img src="{esc(row["path"].removeprefix("docs/"))}" alt="First input: {esc(row["label"])}" loading="lazy"><div class="model-box" hidden></div></div>'
                   '<figcaption>First input. Every model box refers to this photograph.</figcaption><button class="btn clear-box" type="button">Clear location box</button>')
        if row['second_path']:
            out.append(f'<img class="second-input" src="{esc(row["second_path"].removeprefix("docs/"))}" alt="Second input: alternate photograph of {esc(row["label"])}" loading="lazy"><figcaption>Second input, supplied only in the paired condition.</figcaption>')
        out.append('</figure><div><table class="read-table"><thead><tr><th scope="col">Feature</th><th scope="col">Reference</th><th scope="col">Answer</th></tr></thead><tbody>')
        for feature, name in names.items():
            cell = row['cells'][feature]
            value = observation.get(feature, {})
            answer = esc(cell['answer'] or 'missing')
            if value.get('box'):
                answer = f'<button type="button" class="box-link" data-box="{esc(",".join(map(str, value["box"])))}" aria-label="Show model location for {esc(name)}">{answer} ↗</button>'
            out.append(f'<tr><th scope="row">{name}{" *" if cell["primary"] else ""}</th><td>{esc(cell["expected"])}</td><td class="outcome-{esc(cell["outcome"])}">{answer}</td></tr>')
        out.append('</tbody></table><p class="source-inline">* Primary check. A matching label does not validate the location.</p>')
        out.append(f'<h4>Description · {esc(row["status"])}</h4><p>{esc(observation.get("description", "No valid model response received."))}</p>')
        if observation:
            out.append('<details><summary>Feature explanations and limitations</summary><dl class="observation-notes">')
            for feature, name in names.items():
                out.append(f'<dt>{name}</dt><dd>{esc(observation[feature]["evidence"])}</dd>')
            out.append('</dl><p>' + esc(observation['limitations']) + '</p></details>')
        out.append('<p class="source-inline">' + link(f'data/pillar-moai/v3/raw/{row["id"]}.json', 'Full saved request and response record') + '</p></div></div></details>')
    return '\n'.join(out)


def build(check=False):
    studies = json.loads((ROOT / 'research/investigations.json').read_text())
    images = json.loads((ROOT / 'research/images.json').read_text())
    data = json.loads((ROOT / 'research/civilisers/v2/evidence.json').read_text())
    validate(data)
    pending = {}
    home = (DOCS / 'index.html').read_text()
    pending[DOCS / 'index.html'] = replace_region(home, 'investigations', cards(studies))
    v2 = (DOCS / 'civilisers.html').read_text()
    for name, content in [('evidence', render_evidence(data)), ('sources', render_sources(data)), ('comparison', render_matrix(data))]:
        v2 = replace_region(v2, name, content)
    options = '<option value="all">All figures</option>\n' + '\n'.join(f'<option value="{esc(f["id"])}">{esc(f["name"])}</option>' for f in data['figures'])
    v2 = replace_region(v2, 'figure-options', options)
    v2 = replace_region(v2, 'corpus-count', f'{len(data["passages"])} passages · {len(data["sources"])} source records · {len(data["figures"])} figure entries')
    pending[DOCS / 'civilisers.html'] = v2
    for s in studies:
        pages = [s['url']] if not s['url'].startswith('https:') else []
        if s['id'] == 'civilisers':
            pages.append('heroes.html')
        for page in pages:
            path = DOCS / page
            if path.is_dir():
                path = path / 'index.html'
            prefix = '../' * (len(path.relative_to(DOCS).parts) - 1)
            text = pending.get(path, path.read_text())
            if '<!-- study-review:start -->' not in text:
                text = text.replace('<main>', '<main>\n<!-- study-review:start -->\n<!-- study-review:end -->', 1)
            text = replace_region(text, 'study-review', review(s, prefix))
            if f'href="{prefix}collection.css"' not in text:
                text = text.replace('</head>', f'<link rel="stylesheet" href="{prefix}collection.css">\n</head>')
            pending[path] = text
    for name, obj in [('investigations.json', studies), ('image-register.json', images), ('civilisers-v2.json', data)]:
        pending[DOCS / 'data' / name] = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'
    pending[DOCS / 'study4/source-method.md'] = (ROOT / 'research/civilisers/v2/method.md').read_text()
    pending[DOCS / 'study4/redo-protocol-draft.md'] = (ROOT / 'research/civilisers/v3/protocol-draft.md').read_text()
    pending[DOCS / 'data/fenton-thread.md'] = (ROOT / 'research/fenton/thread.md').read_text()
    case = ROOT / 'research/pillar-moai/v2'
    register = json.loads((case / 'sources.json').read_text())
    validate_case(register)
    case_page = (DOCS / 'pillar-and-moai.html').read_text()
    case_page = replace_region(case_page, 'case-sources', case_sources(register))
    pending[DOCS / 'pillar-and-moai.html'] = replace_region(case_page, 'case-images', case_images(register))
    result = json.loads((ROOT / 'data/pillar-moai/v2/results.json').read_text())
    reference = json.loads((case / 'reference.json').read_text())
    if result['historical_ranking_permitted'] or result['independent_review'] != 'not_reviewed':
        raise ValueError('This diagnostic has no independent review and cannot permit historical ranking')
    pending[DOCS / 'recognition.html'] = replace_region((DOCS / 'recognition.html').read_text(), 'recognition-results', recognition_results(result, reference))
    for source in list(case.glob('*.json')) + [case / 'protocol.md'] + list((ROOT / 'data/pillar-moai/v2').glob('*.json')):
        pending[DOCS / 'data/pillar-moai' / source.name] = source.read_text()
    for source in (ROOT / 'data/pillar-moai/v2/raw').glob('*.json'):
        pending[DOCS / 'data/pillar-moai/raw' / source.name] = source.read_text()
    pending[DOCS / 'data/pillar-moai/recognition.py'] = (ROOT / 'pipeline/recognition.py').read_text()
    context = json.loads((ROOT / 'research/pillar-moai/context.json').read_text())
    validate_case(context)
    context_page = (DOCS / 'local-context.html').read_text()
    for name, content in [('context-objects', context_objects(context)), ('context-sources', case_sources(context)), ('context-images', case_images(context))]:
        context_page = replace_region(context_page, name, content)
    pending[DOCS / 'local-context.html'] = context_page
    pending[DOCS / 'data/pillar-moai/context.json'] = json.dumps(context, ensure_ascii=False, indent=2) + '\n'
    try:
        from pipeline import view_trial
    except ModuleNotFoundError:
        import view_trial
    if not (view_trial.DATA / 'freeze.json').is_file():
        raise ValueError('View trial must already be frozen; publishing cannot create an experiment')
    frozen = view_trial.freeze()
    trial = json.loads((view_trial.DATA / 'results.json').read_text())
    computed = view_trial.evaluate(view_trial.manifest(), view_trial.load_records(frozen))
    if any(trial[key] != value for key, value in computed.items()):
        raise ValueError('View trial report differs from raw responses')
    audit = json.loads((view_trial.RESEARCH / 'location-audit.json').read_text())
    trial_page = (DOCS / 'view-trial.html').read_text()
    for name, content in [('view-summary', view_summary(trial)), ('view-locations', view_locations(audit, trial)), ('view-records', view_records(trial))]:
        trial_page = replace_region(trial_page, name, content)
    pending[DOCS / 'view-trial.html'] = trial_page
    for source in list(view_trial.RESEARCH.glob('*.json')) + [view_trial.RESEARCH / 'protocol.md'] + list(view_trial.DATA.glob('*.json')):
        pending[DOCS / 'data/pillar-moai/v3' / source.name] = source.read_text()
    for source in (view_trial.DATA / 'raw').glob('*.json'):
        pending[DOCS / 'data/pillar-moai/v3/raw' / source.name] = source.read_text()
    pending[DOCS / 'data/pillar-moai/v3/view_trial.py'] = (ROOT / 'pipeline/view_trial.py').read_text()
    try:
        from pipeline import catalogue
    except ModuleNotFoundError:
        import catalogue
    pending.update(catalogue.outputs())
    try:
        from pipeline import submerged
    except ModuleNotFoundError:
        import submerged
    pending.update(submerged.outputs())
    try:
        from pipeline import research_updates
    except ModuleNotFoundError:
        import research_updates
    pending.update(research_updates.outputs())
    try:
        from pipeline import fieldwork
    except ModuleNotFoundError:
        import fieldwork
    pending.update(fieldwork.outputs())
    changed = []
    for path, content in pending.items():
        if not path.exists() or path.read_text() != content:
            changed.append(str(path.relative_to(ROOT)))
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
    for item in images:
        src = ROOT / 'inputs' / item['input']
        dst = DOCS / 'img/inputs' / item['output']
        if not src.is_file():
            raise ValueError(f'Missing original image: {src}')
        if item.get('crop'):
            if not dst.is_file():
                raise ValueError(f'Missing crop {dst}; run pipeline/crop_inputs.py with Pillow')
            continue
        if not dst.is_file() or src.read_bytes() != dst.read_bytes():
            changed.append(str(dst.relative_to(ROOT)))
            if not check:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
    if not changed:
        print('Current: all generated content matches its sources')
    else:
        print(('Out of date: ' if check else 'Published: ') + ', '.join(changed))
    return 1 if check and changed else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='check publishing outputs without writing')
    raise SystemExit(build(parser.parse_args().check))
