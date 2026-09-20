from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit

from pipeline import fieldwork

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links = [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        self.links.extend(attrs[k] for k in ('href', 'src') if attrs.get(k))


class FieldworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((fieldwork.RESEARCH/'register.json').read_text())

    def test_source_photographs_selection_and_catalogue_identities(self):
        fieldwork.validate(self.data)
        self.assertEqual(len({o['physical_id'] for o in self.data['objects']}), 22)
        self.assertEqual(next(o for o in self.data['objects'] if o['id'] == 'rn-hoa')['physical_id'],
                         'hoa-hakananai-a')
        d = deepcopy(self.data)
        d['objects'][0]['catalogue_entity'] = 'unidentified-pillar'
        with self.assertRaisesRegex(ValueError, 'catalogue object identity'):
            fieldwork.validate(d)

    def test_retrieval_replays_ordinary_variants_and_exclusions(self):
        batches = {b['query']: b for b in fieldwork.selection()['batches']}
        self.assertEqual(batches['Horus']['selected'], [243744, 243745, 243746, 244461])
        self.assertEqual(batches['Thoth']['selected'], [329907, 544092, 544093, 545855])
        self.assertEqual(batches['Relief panel']['selected'], [321613, 322486, 322487, 322488])
        self.assertEqual(batches['winged protective spirit']['selected'], [])
        rejected = {r['id']: r for b in batches.values() for r in b['inspected'] if r['decision'] == 'excluded'}
        self.assertIn('zero', rejected[891642]['reason'])
        self.assertIn('priest', rejected[545440]['reason'])
        self.assertIn('priest', rejected[545441]['reason'])
        self.assertEqual(sum(len(b['inspected']) for b in batches.values()), 25)

    def test_two_records_cannot_double_one_physical_object(self):
        d = deepcopy(self.data)
        d['objects'][1]['physical_id'] = d['objects'][0]['physical_id']
        with self.assertRaisesRegex(ValueError, 'physical object identity'):
            fieldwork.validate(d, False)

    def test_relation_requires_visible_components_in_its_own_scope(self):
        for state in ('not-seen', 'uncertain', 'unresolved', 'not-applicable'):
            d = deepcopy(self.data)
            d['objects'][0]['observations']['beak']['state'] = state
            with self.subTest(state=state), self.assertRaisesRegex(ValueError, 'same scope'):
                fieldwork.validate(d, False)
        d = deepcopy(self.data)
        d['objects'][0]['observations']['beak']['state'] = 'probably'
        with self.assertRaisesRegex(ValueError, 'Invalid observation'):
            fieldwork.validate(d, False)

    def test_regions_and_image_references_cannot_escape_their_source(self):
        d = deepcopy(self.data)
        d['objects'][0]['image']['annotations'][0]['box'] = [.9, .2, .3, .3]
        with self.assertRaisesRegex(ValueError, 'outside source image'):
            fieldwork.validate(d, False)
        for path in ('../../README.md', '/private/tmp/unknown.jpg'):
            d = deepcopy(self.data)
            d['objects'][0]['image']['path'] = path
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'Unsafe image'):
                fieldwork.validate(d, False)

    def test_date_bounds_are_not_production_dates_or_year_zero(self):
        hoa = next(o for o in self.data['objects'] if o['id'] == 'rn-hoa')
        self.assertIsNone(hoa['date']['start'])
        self.assertEqual(hoa['date']['kind'], 'upper-bound')
        slab = next(e for e in self.data['events'] if e['id'] == 'slab')
        self.assertEqual((slab['start'], slab['kind']), (1974, 'collection'))
        for value in (0, -12000, 1.5, '1868'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                fieldwork.validate_date({'start': 1000, 'end': value, 'kind': 'production'})
        with self.assertRaisesRegex(ValueError, 'upper bound'):
            fieldwork.validate_date({'start': 1000, 'end': 1868, 'kind': 'upper-bound'})
        amulet = next(o for o in self.data['objects'] if o['id'] == 'met-545855')
        self.assertEqual((amulet['date']['start'], amulet['date']['end']), (-2110, -2030))
        self.assertIn('numeric', amulet['date']['note'])

    def test_generated_evidence_is_current_and_local_links_resolve(self):
        parsed = {}
        for path, text in fieldwork.outputs().items():
            self.assertEqual(path.read_text(), text, str(path))
            if path.suffix != '.html':
                continue
            page = Links(text)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            for link in page.links:
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                target = (path.parent/unquote(url.path)).resolve() if url.path else path
                if target.is_dir():
                    target = target/'index.html'
                self.assertTrue(target.is_file(), link)
                if url.fragment and target.suffix == '.html':
                    if target not in parsed:
                        parsed[target] = Links(target.read_text())
                    self.assertIn(unquote(url.fragment), parsed[target].ids, link)


if __name__ == '__main__':
    unittest.main()
