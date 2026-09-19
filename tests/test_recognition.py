"""Research integrity and decision boundaries. No API calls or image generation."""
from copy import deepcopy
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('recognition', ROOT / 'pipeline/recognition.py')
recognition = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recognition)


class RecognitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads((ROOT / 'research/pillar-moai/v2/reference.json').read_text())

    def perfect_records(self):
        records = {}
        for im in self.reference['images']:
            for repeat in (1, 2):
                observation = {'description': 'Fixture observation', 'limitations': 'Fixture, not a model output'}
                for feature, expected in im['expected'].items():
                    observation[feature] = {'answer': expected or 'uncertain', 'evidence': 'Test fixture', 'box': None}
                records[(im['id'], repeat)] = {'status': 'complete', 'observation': observation}
        return records

    def test_perfect_screen_does_not_authorise_historical_ranking(self):
        result = recognition.evaluate(self.reference, self.perfect_records())
        self.assertTrue(result['screening_pass'])
        self.assertFalse(result['historical_ranking_permitted'])
        self.assertEqual(result['independent_review'], 'not_reviewed')

    def test_critical_face_error_blocks_high_average(self):
        records = self.perfect_records()
        records[('hoa-back', 1)]['observation']['large_face']['answer'] = 'present'
        result = recognition.evaluate(self.reference, records)
        self.assertGreater(result['accuracy_all'], .98)
        self.assertFalse(result['screening_pass'])
        self.assertEqual(result['critical_failures'][0]['feature'], 'large_face')

    def test_uncertain_and_missing_are_not_dropped_from_denominator(self):
        records = self.perfect_records()
        full = recognition.evaluate(self.reference, records)
        records.pop(('hoa-back', 1))
        records[('hoa-back', 2)]['observation']['avian']['answer'] = 'uncertain'
        result = recognition.evaluate(self.reference, records)
        self.assertEqual(result['scorable'], full['scorable'])
        self.assertEqual(result['totals']['missing'], 5)
        self.assertEqual(result['totals']['abstained'], 1)
        self.assertLess(result['accuracy_all'], result['accuracy_answered'])
        self.assertFalse(result['screening_pass'])

    def test_invalid_location_cannot_count_as_valid_response(self):
        observation = self.perfect_records()[('p43', 1)]['observation']
        for box in [[-.1, 0, 1, 1], [0, 0, 2, 1], [.9, 0, .1, 1], [0, 0, 1]]:
            broken = deepcopy(observation)
            broken['avian']['box'] = box
            self.assertFalse(recognition.valid_observation(broken))

    def test_frozen_files_and_raw_records_are_consistent(self):
        folder = ROOT / 'data/pillar-moai/v2'
        frozen = json.loads((folder / 'freeze.json').read_text())
        freeze_hash = hashlib.sha256((folder / 'freeze.json').read_bytes()).hexdigest()
        for path, expected in frozen['sha256'].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)
        records = {}
        for path in (folder / 'raw').glob('*.json'):
            rec = json.loads(path.read_text())
            self.assertEqual(rec['freeze_sha256'], freeze_hash)
            self.assertGreaterEqual(datetime.fromisoformat(rec['started_at']), datetime.fromisoformat(frozen['frozen_at']))
            key = (rec['image'], rec['repeat'])
            self.assertNotIn(key, records)
            self.assertIn(list(key), frozen['request_order'])
            if rec['status'] == 'complete':
                output = ''.join(part['text'] for item in rec['response']['output']
                                 if item['type'] == 'message' for part in item['content']
                                 if part['type'] == 'output_text')
                self.assertEqual(json.loads(output), rec['observation'])
            records[key] = rec
        recomputed = recognition.evaluate(self.reference, records)
        published = json.loads((folder / 'results.json').read_text())
        for key, value in recomputed.items():
            with self.subTest(field=key):
                self.assertEqual(published[key], value)
        self.assertLessEqual(sum(r['estimated_cost_usd'] for r in records.values()), frozen['estimated_budget_usd'])


if __name__ == '__main__':
    unittest.main()
