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
  <p class="question">{esc(s['question'])}</p>
  <dl><dt>Finding / scope</dt><dd>{esc(s['finding'])}</dd><dt>Limitations</dt><dd>{esc(s['limitations'])}</dd></dl>
  <div class="versions">{links(s['versions']) if s['versions'] else link(s['url'], 'Read the companion investigation ↗')}</div>
</article>''')
    return "\n".join(out + ["</div>"])


def review(s):
    return f'''<aside class="study-review wrap" aria-label="Study scope and limitations">
  <div class="review-box"><div class="eyebrow">Reading this investigation · updated September 2026</div>
  <h2>{esc(s['question'])}</h2>
  <dl><div><dt>What remains useful</dt><dd>{esc(s['finding'])}</dd></div><div><dt>What it cannot settle</dt><dd>{esc(s['limitations'])}</dd></div></dl>
  <div class="reading-links">{link('./#investigations', 'All investigations')} {link('#limits', 'Full limitations')} {links(s['versions'])}</div></div>
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
            text = pending.get(path, path.read_text())
            if '<!-- study-review:start -->' not in text:
                text = text.replace('<main>', '<main>\n<!-- study-review:start -->\n<!-- study-review:end -->', 1)
            text = replace_region(text, 'study-review', review(s))
            if 'href="collection.css"' not in text:
                text = text.replace('</head>', '<link rel="stylesheet" href="collection.css">\n</head>')
            pending[path] = text
    for name, obj in [('investigations.json', studies), ('image-register.json', images), ('civilisers-v2.json', data)]:
        pending[DOCS / 'data' / name] = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'
    pending[DOCS / 'study4/source-method.md'] = (ROOT / 'research/civilisers/v2/method.md').read_text()
    pending[DOCS / 'study4/redo-protocol-draft.md'] = (ROOT / 'research/civilisers/v3/protocol-draft.md').read_text()
    pending[DOCS / 'data/fenton-thread.md'] = (ROOT / 'research/fenton/thread.md').read_text()
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
