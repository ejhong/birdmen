from copy import deepcopy
import json
from pathlib import Path
import unittest
from urllib.parse import unquote,urlsplit
from pipeline import research_updates
from test_catalogue import Links

ROOT=Path(__file__).resolve().parents[1]

class ResearchUpdateTests(unittest.TestCase):
    def test_pair_audit_reconciles_counts_and_does_not_count_orders_as_new_pairs(self):
        raw=json.loads((ROOT/'data/s4/results.json').read_text())
        r=research_updates.signal_audit(raw)
        self.assertEqual((r['completed'],r['first'],r['unordered_pairings'],r['directed_pairings']),(397,248,11,22))
        self.assertEqual(sum(len(p['directions']) for p in r['pairs']),22)
        self.assertAlmostEqual(r['rate'],248/397)
        broken=deepcopy(raw);broken['by_set']['hancock']['all']['n']+=1
        with self.assertRaisesRegex(ValueError,'totals disagree'):research_updates.signal_audit(broken)
    def test_research_outputs_current_and_links_resolve(self):
        for path,text in research_updates.outputs().items():
            self.assertEqual(path.read_text(),text)
            if path.suffix!='.html':continue
            page=Links(text);self.assertEqual(len(page.ids),len(set(page.ids)))
            for link in page.links:
                url=urlsplit(link)
                if url.scheme or url.netloc:continue
                target=(path.parent/unquote(url.path)).resolve() if url.path else path
                if target.is_dir():target=target/'index.html'
                self.assertTrue(target.is_file(),link)
                if url.fragment and target.suffix=='.html':self.assertIn(unquote(url.fragment),Links(target.read_text()).ids)
