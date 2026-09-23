"""The two-repertoire walls: provenance, honest states and current output."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('corpus', ROOT / 'pipeline/corpus.py')
corpus = importlib.util.module_from_spec(spec)
spec.loader.exec_module(corpus)


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = corpus.load()

    def test_every_photograph_carries_its_provenance(self):
        corpus.validate(self.data)
        for item in self.data['items']:
            with self.subTest(item=item['id']):
                self.assertTrue(item['media']['url'].startswith('https://commons.wikimedia.org/'))
                self.assertIn('Commons', item['media']['transformation'])

    def test_broken_provenance_and_invented_states_are_rejected(self):
        for field in ('credit', 'rights', 'sha256'):
            d = deepcopy(self.data)
            d['items'][0]['media'][field] = ''
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'provenance'):
                corpus.validate(d, False)
        d = deepcopy(self.data)
        d['items'][0]['features']['bird'] = 'present'
        with self.assertRaisesRegex(ValueError, 'state'):
            corpus.validate(d, False)
        d = deepcopy(self.data)
        d['items'][0]['physical'] = ''
        with self.assertRaisesRegex(ValueError, 'physical'):
            corpus.validate(d, False)
        d = deepcopy(self.data)
        d['items'][1]['id'] = d['items'][0]['id']
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            corpus.validate(d, False)

    def test_counts_describe_photographs_and_never_inflate_objects(self):
        an = corpus.counts(self.data, 'anatolia')
        rn = corpus.counts(self.data, 'rapanui')
        self.assertEqual(an['total'], sum(1 for i in self.data['items'] if i['corpus'] == 'anatolia'))
        # Uncertain readings are never counted as a match.
        uncertain = [i for i in self.data['items'] if i['corpus'] == 'anatolia' and i['features']['bird'] == '?']
        self.assertTrue(uncertain)
        self.assertEqual(an['bird'], sum(1 for i in self.data['items']
                                         if i['corpus'] == 'anatolia' and i['features']['bird'] == '1'))
        # Three photographs of Pillar 43 are one object, and the page says so.
        self.assertEqual(an['both'], 3)
        self.assertEqual(an['both_objects'], 1)
        self.assertGreater(rn['both_objects'], an['both_objects'])
        self.assertLessEqual(an['objects'], an['total'])

    def test_the_selection_rule_and_its_exclusions_are_published(self):
        selection = self.data['selection']
        self.assertTrue(selection['rule'] and selection['caveat'])
        self.assertTrue(sum(e['count'] for e in selection['excluded']) > len(self.data['items']))
        self.assertIn('independent review is outstanding', self.data['review']['note'])
        drawn = [b for b in self.data['chronology'] if b['start'] is not None]
        self.assertTrue(any(b['start'] is None for b in self.data['chronology']))
        self.assertTrue(all(b['end'] >= b['start'] for b in drawn))

    def test_generated_page_is_current(self):
        for path, text in corpus.outputs().items():
            self.assertEqual(path.read_text(), text, str(path))


if __name__ == '__main__':
    unittest.main()
