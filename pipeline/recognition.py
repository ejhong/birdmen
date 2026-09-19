"""Frozen, bounded recognition diagnostic. Offline unless explicitly run.

python3 pipeline/recognition.py freeze | report
/usr/local/bin/python3 pipeline/recognition.py run
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/pillar-moai/v2'
DATA = ROOT / 'data/pillar-moai/v2'
FEATURES = ['avian', 'large_face', 'scorpion', 'round_motif', 'three_arches']
PROMPT = '''Look only at the carved surface of the main stone object in this photograph.
Ignore objects, people, labels and artworks in the background. Describe the visible
carving in two or three literal sentences before answering the feature questions.
Do not infer features from recognising an object. Separate what you can see from
what you might know. Do not discuss origin, date, meaning, historical connection,
or similarity to any other artwork.
For each feature report present, absent, or uncertain, with a short visual reason:
avian: a carved bird or figure with a birdlike head/beak (natural or humanlike body).
large_face: a large human face, with facial features, on the main visible surface
(a front or oblique front view counts; a blank back of a head does not).
scorpion: a carved scorpion, including legs and/or a segmented upturned tail.
round_motif: a distinct round/circular motif other than an eye, nostril, navel or
obvious modern repair. Do not assume that its meaning is an egg or celestial body.
three_arches: three repeated arch-topped forms arranged side by side in a row.
If the image is too ambiguous, say uncertain, not absent. For present features,
give one bounding box [left, top, right, bottom], coordinates 0 to 1 relative to
the whole photograph. Use null if you cannot locate it reliably. Do not trace or
reconstruct lost lines. In limitations, note anything which makes reading difficult.'''


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def schema():
    feature = {'type': 'object', 'additionalProperties': False, 'properties': {
        'answer': {'type': 'string', 'enum': ['present', 'absent', 'uncertain']},
        'evidence': {'type': 'string'},
        'box': {'anyOf': [{'type': 'array', 'items': {'type': 'number'}, 'minItems': 4, 'maxItems': 4}, {'type': 'null'}]}
    }, 'required': ['answer', 'evidence', 'box']}
    props = {'description': {'type': 'string'}, **{k: feature for k in FEATURES}, 'limitations': {'type': 'string'}}
    return {'type': 'object', 'additionalProperties': False, 'properties': props, 'required': list(props)}


def freeze():
    manifest = json.loads((RESEARCH / 'reference.json').read_text())
    paths = ['research/pillar-moai/v2/protocol.md', 'research/pillar-moai/v2/reference.json', 'pipeline/recognition.py']
    paths += [case['path'] for case in manifest['images']]
    current = {p: digest(ROOT / p) for p in paths}
    request_order = [(im['id'], repeat) for im in manifest['images'] for repeat in (1, 2)]
    random.Random(4301).shuffle(request_order)
    frozen = {'protocol': 'recognition-2.0', 'model': 'gpt-5.5', 'reasoning': 'low',
              'detail': 'high', 'max_output_tokens': 3500, 'estimated_budget_usd': 5,
              'reservation_per_request_usd': .23, 'input_per_million_usd': 5,
              'output_per_million_usd': 30, 'prompt': PROMPT, 'schema': schema(),
              'sha256': current, 'request_order': [list(v) for v in request_order]}
    path = DATA / 'freeze.json'
    if path.exists():
        previous = json.loads(path.read_text())
        comparable = {k: v for k, v in previous.items() if k != 'frozen_at'}
        if comparable != frozen:
            raise ValueError('Frozen inputs changed. Create a new protocol version; never overwrite this run.')
        return previous
    if any((DATA / 'raw').glob('*.json')):
        raise ValueError('Responses exist without a freeze; cannot retroactively freeze a run.')
    frozen['frozen_at'] = now()
    dump(path, frozen)
    return frozen


def valid_observation(observation):
    if not isinstance(observation, dict) or not isinstance(observation.get('description'), str):
        return False
    if not isinstance(observation.get('limitations'), str):
        return False
    for feature in FEATURES:
        value = observation.get(feature, {})
        if not isinstance(value, dict) or value.get('answer') not in {'present', 'absent', 'uncertain'}:
            return False
        if not isinstance(value.get('evidence'), str):
            return False
        box = value.get('box')
        if box is not None and (not isinstance(box, list) or len(box) != 4 or
                any(not isinstance(n, (int, float)) or not 0 <= n <= 1 for n in box) or
                box[0] >= box[2] or box[1] >= box[3]):
            return False
    return True


def evaluate(manifest, records):
    rows = []
    totals = dict(correct=0, wrong=0, abstained=0, missing=0)
    critical_failures = []
    for case in manifest['images']:
        for repeat in (1, 2):
            record = records.get((case['id'], repeat), {})
            result = record.get('observation', {}) if record.get('status') == 'complete' else {}
            if not valid_observation(result):
                result = {}
            cells = {}
            for key, expected in case['expected'].items():
                if expected is None:
                    continue
                answer = result.get(key, {}).get('answer')
                outcome = 'missing' if answer is None else 'abstained' if answer == 'uncertain' else 'correct' if answer == expected else 'wrong'
                totals[outcome] += 1
                cells[key] = {'expected': expected, 'answer': answer, 'outcome': outcome}
                if key in case.get('critical', []) and outcome != 'correct':
                    critical_failures.append({'image': case['id'], 'repeat': repeat, 'feature': key, 'outcome': outcome})
            rows.append({'id': case['id'], 'repeat': repeat, 'label': case['label'], 'path': case['path'],
                         'status': record.get('status', 'not_run'), 'cells': cells,
                         'description': result.get('description', ''), 'observation': result})
    n = sum(totals.values())
    answered = totals['correct'] + totals['wrong']
    accuracy = totals['correct'] / n if n else 0
    screening = accuracy >= .9 and not critical_failures and not totals['missing']
    disagreements = []
    for case in manifest['images']:
        pair = [r for r in rows if r['id'] == case['id']]
        for feature in case['expected']:
            answers = [r['cells'].get(feature, {}).get('answer') for r in pair]
            if all(a is not None for a in answers) and answers[0] != answers[1]:
                disagreements.append({'image': case['id'], 'feature': feature, 'answers': answers})
    views = []
    for group in sorted({im['group'] for im in manifest['images']}):
        images = [im for im in manifest['images'] if im['group'] == group]
        if len(images) < 2:
            continue
        shared = [f for f in FEATURES if images[0]['expected'].get(f) is not None and
                  all(im['expected'].get(f) == images[0]['expected'][f] for im in images)]
        for repeat in (1, 2):
            for f in shared:
                answers = [next(r for r in rows if r['id'] == im['id'] and r['repeat'] == repeat)['cells'][f]['answer'] for im in images]
                views.append({'group': group, 'repeat': repeat, 'feature': f, 'answers': answers,
                              'consistent': len(set(answers)) == 1 if all(a is not None for a in answers) else None})
    return {'totals': totals, 'scorable': n, 'accuracy_all': accuracy,
            'coverage': answered / n if n else 0, 'accuracy_answered': totals['correct'] / answered if answered else None,
            'screening_pass': screening, 'critical_failures': critical_failures,
            'independent_review': 'not_reviewed', 'historical_ranking_permitted': False,
            'repeat_disagreements': disagreements, 'cross_view': views, 'rows': rows}


def report():
    frozen = freeze()
    manifest = json.loads((RESEARCH / 'reference.json').read_text())
    records = {}
    for path in sorted((DATA / 'raw').glob('*.json')):
        value = json.loads(path.read_text())
        key = (value['image'], value['repeat'])
        if key in records:
            raise ValueError(f'Duplicate response {key}')
        if value['freeze_sha256'] != digest(DATA / 'freeze.json'):
            raise ValueError('Response does not match frozen protocol')
        records[key] = value
    result = evaluate(manifest, records)
    result.update(protocol=frozen['protocol'], model=frozen['model'], frozen_at=frozen['frozen_at'],
                  planned_requests=len(frozen['request_order']), completed_requests=sum(r.get('status') == 'complete' for r in records.values()),
                  estimated_cost_usd=round(sum(r.get('estimated_cost_usd', .23) for r in records.values()), 6),
                  freeze_sha256=digest(DATA / 'freeze.json'))
    dump(DATA / 'results.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ['rows', 'cross_view', 'critical_failures']}, ensure_ascii=False))
    return result


def run():
    frozen = freeze()
    from openai import OpenAI
    import certifi
    os.environ.setdefault('SSL_CERT_FILE', certifi.where())
    client = OpenAI(max_retries=0, timeout=180)
    manifest = json.loads((RESEARCH / 'reference.json').read_text())
    images = {im['id']: im for im in manifest['images']}
    spent = sum(json.loads(p.read_text()).get('estimated_cost_usd', .23) for p in (DATA / 'raw').glob('*.json'))
    for image_id, repeat in frozen['request_order']:
        path = DATA / 'raw' / f'{image_id}-{repeat}.json'
        if path.exists():
            continue
        if spent + frozen['reservation_per_request_usd'] > frozen['estimated_budget_usd']:
            print('Budget reserve reached; remaining requests not run.')
            break
        rec = {'image': image_id, 'repeat': repeat, 'started_at': now(), 'status': 'pending',
               'freeze_sha256': digest(DATA / 'freeze.json'), 'estimated_cost_usd': .23}
        # Reserve durably before the request. A process crash cannot silently retry.
        dump(path, rec)
        try:
            payload = base64.b64encode((ROOT / images[image_id]['path']).read_bytes()).decode()
            response = client.responses.create(model=frozen['model'], store=False,
                reasoning={'effort': frozen['reasoning']}, max_output_tokens=frozen['max_output_tokens'],
                input=[{'role': 'user', 'content': [
                    {'type': 'input_text', 'text': frozen['prompt']},
                    {'type': 'input_image', 'image_url': 'data:image/jpeg;base64,' + payload, 'detail': frozen['detail']}]}],
                text={'format': {'type': 'json_schema', 'name': 'recognition', 'strict': True, 'schema': frozen['schema']}})
            rec['response'] = response.model_dump(mode='json')
            rec['estimated_cost_usd'] = (response.usage.input_tokens * frozen['input_per_million_usd'] + response.usage.output_tokens * frozen['output_per_million_usd']) / 1_000_000
            rec['observation'] = json.loads(response.output_text)
            rec['status'] = 'complete' if response.status == 'completed' and valid_observation(rec['observation']) else 'invalid'
        except Exception as exc:
            # Do not log request headers, credentials or base64 payloads in errors.
            rec['status'] = 'error'
            rec['error_type'] = type(exc).__name__
            rec['http_status'] = getattr(exc, 'status_code', None)
        rec['finished_at'] = now()
        dump(path, rec)
        spent += rec['estimated_cost_usd']
        print(f'{image_id} / {repeat}: {rec["status"]}; estimated cumulative USD {spent:.4f}', flush=True)
        if rec['status'] == 'error':
            print('Stopped after API failure; no automatic retries.', flush=True)
            break
    report()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['freeze', 'run', 'report'])
    action = parser.parse_args().action
    if action == 'freeze':
        print(json.dumps(freeze(), ensure_ascii=False, indent=2))
    elif action == 'run':
        run()
    else:
        report()
