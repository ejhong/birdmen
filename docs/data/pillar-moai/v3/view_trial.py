"""Bounded 2 × 2 development trial: additional view × reasoning effort.

python3 pipeline/view_trial.py freeze | report
/usr/local/bin/python3 pipeline/view_trial.py run
"""
import argparse
import base64
import json
import os
from pathlib import Path
import random

try:
    from . import recognition as baseline
except ImportError:
    import recognition as baseline

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/pillar-moai/v3'
DATA = ROOT / 'data/pillar-moai/v3'
EFFORTS = ('low', 'high')
VIEWS = ('single', 'paired')
PROMPT = '''You are shown one or two photographs of the same carved stone surface.
Describe only the carving visible in the FIRST photograph. If a second photograph
is supplied, use it to clarify ambiguous features in the first, not to add features
outside the first photograph. Every bounding box must refer to the FIRST image.
''' + baseline.PROMPT


def manifest():
    return json.loads((RESEARCH / 'reference.json').read_text())


def planned(data):
    return [dict(id=f"{obj['id']}-{effort}-{views}-{order}", object=obj['id'],
                 effort=effort, views=views, order=order)
            for obj in data['objects'] for effort in EFFORTS
            for views in VIEWS for order in (1, 2)]


def freeze():
    data = manifest()
    paths = ['research/pillar-moai/v3/protocol.md', 'research/pillar-moai/v3/reference.json',
             'pipeline/view_trial.py', 'pipeline/recognition.py']
    paths += [im['path'] for obj in data['objects'] for im in obj['images']]
    order = planned(data)
    random.Random(4303).shuffle(order)
    frozen = dict(protocol='view-trial-3.0', model='gpt-5.5-2026-04-23',
                  detail='high', max_output_tokens=6000, estimated_budget_usd=8,
                  reservation_per_request_usd=.30, input_per_million_usd=5,
                  output_per_million_usd=30, prompt=PROMPT, schema=baseline.schema(),
                  sha256={p: baseline.digest(ROOT / p) for p in paths}, request_order=order)
    path = DATA / 'freeze.json'
    if path.exists():
        previous = json.loads(path.read_text())
        if {k: v for k, v in previous.items() if k != 'frozen_at'} != frozen:
            raise ValueError('Frozen trial changed. Start a new version; never overwrite responses.')
        return previous
    if any((DATA / 'raw').glob('*.json')):
        raise ValueError('Cannot freeze after responses exist.')
    frozen['frozen_at'] = baseline.now()
    baseline.dump(path, frozen)
    return frozen


def counts(cells):
    totals = dict(correct=0, wrong=0, uncertain=0, missing=0)
    for cell in cells:
        totals[cell['outcome']] += 1
    return dict(**totals, total=sum(totals.values()))


def evaluate(data, records):
    objects = {obj['id']: obj for obj in data['objects']}
    rows = []
    for request in planned(data):
        obj = objects[request['object']]
        image = obj['images'][request['order'] - 1]
        record = records.get(request['id'], {})
        observation = record.get('observation') if record.get('status') == 'complete' else None
        if not baseline.valid_observation(observation):
            observation = None
        cells = {}
        for feature, expected in image['expected'].items():
            if expected is None:
                continue
            answer = observation[feature]['answer'] if observation else None
            outcome = ('missing' if answer is None else 'uncertain' if answer == 'uncertain'
                       else 'correct' if answer == expected else 'wrong')
            cells[feature] = dict(expected=expected, answer=answer, outcome=outcome,
                                  primary=feature in obj['primary'])
        rows.append(dict(**request, label=obj['label'], image=image['id'], path=image['path'],
                         second_path=obj['images'][2-request['order']]['path'] if request['views'] == 'paired' else None,
                         status=record.get('status', 'not_run'), cells=cells,
                         observation=observation))
    summaries = []
    for effort in EFFORTS:
        for views in VIEWS:
            selected = [r for r in rows if r['effort'] == effort and r['views'] == views]
            cells = [c for r in selected for c in r['cells'].values()]
            summaries.append(dict(effort=effort, views=views, all=counts(cells),
                                  primary=counts(c for c in cells if c['primary']),
                                  avian=counts(r['cells']['avian'] for r in selected)))
    transitions = []
    for factor, before, after, other in [('views', 'single', 'paired', 'effort'),
                                          ('effort', 'low', 'high', 'views')]:
        for left in (r for r in rows if r[factor] == before):
            right = next(r for r in rows if r['object'] == left['object'] and r['order'] == left['order']
                         and r[factor] == after and r[other] == left[other])
            for feature, cell in left['cells'].items():
                a, b = cell['outcome'], right['cells'][feature]['outcome']
                transitions.append(dict(factor=factor, fixed=left[other], object=left['object'],
                                        order=left['order'], feature=feature, primary=cell['primary'],
                                        before=a, after=b,
                                        change='improved' if a != 'correct' and b == 'correct' else
                                               'worsened' if a == 'correct' and b != 'correct' else 'no_correctness_change'))
    return dict(conditions=summaries, rows=rows, transitions=transitions,
                independent_review='not_reviewed', historical_ranking_permitted=False)


def load_records(frozen):
    requests = {r['id']: r for r in frozen['request_order']}
    records = {}
    for path in sorted((DATA / 'raw').glob('*.json')):
        record = json.loads(path.read_text())
        rid = record['id']
        if rid not in requests or rid in records or path.stem != rid:
            raise ValueError('Unknown or duplicate request record')
        if record['freeze_sha256'] != baseline.digest(DATA / 'freeze.json'):
            raise ValueError('Response does not match frozen run')
        if any(record[k] != v for k, v in requests[rid].items()):
            raise ValueError('Request metadata differs from freeze')
        records[rid] = record
    return records


def report():
    frozen = freeze()
    records = load_records(frozen)
    result = evaluate(manifest(), records)
    result.update(protocol=frozen['protocol'], model=frozen['model'], frozen_at=frozen['frozen_at'],
                  freeze_sha256=baseline.digest(DATA / 'freeze.json'),
                  planned_requests=len(frozen['request_order']),
                  completed_requests=sum(r.get('status') == 'complete' for r in records.values()),
                  estimated_cost_usd=round(sum(r.get('estimated_cost_usd', .30) for r in records.values()), 6))
    baseline.dump(DATA / 'results.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'transitions')}, ensure_ascii=False))
    return result


def run():
    frozen = freeze()
    records = load_records(frozen)
    from openai import OpenAI
    import certifi
    os.environ.setdefault('SSL_CERT_FILE', certifi.where())
    client = OpenAI(max_retries=0, timeout=180)
    objects = {obj['id']: obj for obj in manifest()['objects']}
    spent = sum(r.get('estimated_cost_usd', .30) for r in records.values())
    for request in frozen['request_order']:
        if request['id'] in records:
            continue
        if spent + frozen['reservation_per_request_usd'] > frozen['estimated_budget_usd']:
            print('Budget reserve reached; remaining requests not run.', flush=True)
            break
        path = DATA / 'raw' / (request['id'] + '.json')
        record = dict(**request, started_at=baseline.now(), status='pending',
                      freeze_sha256=baseline.digest(DATA / 'freeze.json'), estimated_cost_usd=.30)
        baseline.dump(path, record)
        try:
            images = list(objects[request['object']]['images'])
            if request['order'] == 2:
                images.reverse()
            if request['views'] == 'single':
                images = images[:1]
            content = [dict(type='input_text', text=frozen['prompt'])]
            for im in images:
                payload = base64.b64encode((ROOT / im['path']).read_bytes()).decode()
                content.append(dict(type='input_image', image_url='data:image/jpeg;base64,' + payload, detail=frozen['detail']))
            response = client.responses.create(model=frozen['model'], store=False,
                reasoning={'effort': request['effort']}, max_output_tokens=frozen['max_output_tokens'],
                input=[{'role': 'user', 'content': content}],
                text={'format': {'type': 'json_schema', 'name': 'view_trial', 'strict': True, 'schema': frozen['schema']}})
            record['response'] = response.model_dump(mode='json')
            record['estimated_cost_usd'] = (response.usage.input_tokens * frozen['input_per_million_usd'] + response.usage.output_tokens * frozen['output_per_million_usd']) / 1_000_000
            try:
                record['observation'] = json.loads(response.output_text)
            except (ValueError, TypeError):
                record['observation'] = None
            record['status'] = ('complete' if response.status == 'completed' and
                                baseline.valid_observation(record['observation']) else 'invalid')
        except Exception as exc:
            record.update(status='error', error_type=type(exc).__name__, http_status=getattr(exc, 'status_code', None))
        record['finished_at'] = baseline.now()
        baseline.dump(path, record)
        spent += record['estimated_cost_usd']
        print(f"{request['id']}: {record['status']}; estimated total USD {spent:.4f}", flush=True)
        if record['status'] == 'error':
            print('Stopped after API failure; no automatic retries.', flush=True)
            break
    report()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['freeze', 'run', 'report'])
    args = parser.parse_args()
    if args.action == 'freeze':
        frozen = freeze()
        print(f"Frozen {len(frozen['request_order'])} requests at {frozen['frozen_at']}")
    elif args.action == 'run':
        run()
    else:
        report()
