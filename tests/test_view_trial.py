"""Check the controlled comparisons and preservation of the recorded experiment."""
from datetime import datetime
import json
import unittest

from pipeline import view_trial as trial


class ViewTrialTests(unittest.TestCase):
    def setUp(self):
        self.manifest = trial.manifest()
        self.records = {}
        objects = {obj['id']: obj for obj in self.manifest['objects']}
        for request in trial.planned(self.manifest):
            expected = objects[request['object']]['images'][request['order'] - 1]['expected']
            obs = dict(description='Fixture', limitations='Fixture')
            obs.update({key: dict(answer=value, evidence='Fixture', box=None) for key, value in expected.items()})
            self.records[request['id']] = dict(status='complete', observation=obs)

    def test_full_success_never_authorizes_historical_ranking(self):
        result = trial.evaluate(self.manifest, self.records)
        self.assertEqual(len(result['rows']), 24)
        for condition in result['conditions']:
            self.assertEqual(condition['all']['correct'], 30)
            self.assertEqual(condition['primary']['correct'], 10)
            self.assertEqual(condition['avian']['correct'], 6)
        self.assertFalse(result['historical_ranking_permitted'])
        self.assertEqual(result['independent_review'], 'not_reviewed')

    def test_missing_and_uncertain_remain_in_denominator(self):
        self.records.pop('hoa-low-single-1')
        self.records['boulder-low-single-2']['observation']['avian']['answer'] = 'uncertain'
        condition = trial.evaluate(self.manifest, self.records)['conditions'][0]
        self.assertEqual(condition['all']['total'], 30)
        self.assertEqual(condition['all']['missing'], 5)
        self.assertEqual(condition['primary']['missing'], 2)
        self.assertEqual(condition['avian']['uncertain'], 1)

    def test_transitions_pair_the_same_object_and_primary_photograph(self):
        self.records['hoa-low-single-1']['observation']['avian']['answer'] = 'absent'
        self.records['p43-high-paired-2']['observation']['scorpion']['answer'] = 'uncertain'
        result = trial.evaluate(self.manifest, self.records)
        changes = [t for t in result['transitions'] if t['change'] != 'no_correctness_change']
        self.assertEqual(len(changes), 4)
        self.assertEqual(sum(t['change'] == 'improved' for t in changes), 2)
        self.assertEqual(sum(t['change'] == 'worsened' for t in changes), 2)
        self.assertTrue(all(t['primary'] for t in changes))
        self.assertEqual({(t['object'], t['order']) for t in changes}, {('hoa', 1), ('p43', 2)})

    def test_invalid_localization_does_not_become_a_success(self):
        self.records['hoa-high-paired-1']['observation']['avian']['box'] = [0.9, 0.2, 0.1, 0.8]
        result = trial.evaluate(self.manifest, self.records)
        row = next(r for r in result['rows'] if r['id'] == 'hoa-high-paired-1')
        self.assertTrue(all(c['outcome'] == 'missing' for c in row['cells'].values()))

    def test_frozen_run_and_raw_responses_reproduce_the_report(self):
        self.assertTrue((trial.DATA / 'freeze.json').is_file())
        self.assertTrue((trial.DATA / 'results.json').is_file())
        frozen = trial.freeze()
        records = trial.load_records(frozen)
        result = json.loads((trial.DATA / 'results.json').read_text())
        computed = trial.evaluate(self.manifest, records)
        for key, value in computed.items():
            self.assertEqual(result[key], value, key)
        self.assertEqual(len(frozen['request_order']), 24)
        expected = {r['id'] for r in trial.planned(self.manifest)}
        self.assertEqual({r['id'] for r in frozen['request_order']}, expected)
        self.assertLessEqual(result['estimated_cost_usd'], frozen['estimated_budget_usd'])
        for record in records.values():
            self.assertGreaterEqual(datetime.fromisoformat(record['started_at']), datetime.fromisoformat(frozen['frozen_at']))
            if record['status'] != 'complete':
                continue
            self.assertEqual(record['response']['model'], frozen['model'])
            texts = [part['text'] for out in record['response']['output'] if out['type'] == 'message'
                     for part in out['content'] if part['type'] == 'output_text']
            self.assertEqual(json.loads(''.join(texts)), record['observation'])
            usage = record['response']['usage']
            cost = (usage['input_tokens'] * 5 + usage['output_tokens'] * 30) / 1_000_000
            self.assertAlmostEqual(record['estimated_cost_usd'], cost)
        self.assertAlmostEqual(result['estimated_cost_usd'], sum(r['estimated_cost_usd'] for r in records.values()), places=6)

    def test_location_audit_preserves_scores_and_includes_every_positive_scorpion(self):
        result = json.loads((trial.DATA / 'results.json').read_text())
        audit = json.loads((trial.RESEARCH / 'location-audit.json').read_text())
        expected = {r['id']: r for r in result['rows'] if r['object'] == 'p43' and r['observation']['scorpion']['answer'] == 'present'}
        self.assertEqual({c['request'] for c in audit['cases']}, set(expected))
        self.assertEqual(len(audit['cases']), len(expected))
        records = trial.load_records(trial.freeze())
        self.assertGreater(datetime.fromisoformat(audit['reviewed_at']), max(datetime.fromisoformat(r['finished_at']) for r in records.values()))
        for case in audit['cases']:
            row = expected[case['request']]
            self.assertEqual(case['model_box'], row['observation']['scorpion']['box'])
            self.assertEqual(row['cells']['scorpion']['outcome'], 'correct')
            a, b = case['model_box'], case['source_guide']
            overlap = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
            self.assertEqual(overlap, 0)


if __name__ == '__main__':
    unittest.main()
