from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('catalogue',ROOT/'pipeline/catalogue.py')
catalogue=importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalogue)

class Links(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.ids=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        for key in ['src','href']:
            if attrs.get(key):self.links.append(attrs[key])

class CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'research/catalogue/catalogue.json').read_text())
    def test_register_and_photograph_integrity(self):
        catalogue.validate(self.data)
    def test_duplicate_and_dangling_group_rejected(self):
        d=deepcopy(self.data);d['groups'][0]['members'].append('missing')
        with self.assertRaises(ValueError):catalogue.validate(d,False)
        d=deepcopy(self.data);d['groups'].append(d['groups'][0])
        with self.assertRaisesRegex(ValueError,'Duplicate'):catalogue.validate(d,False)
    def test_claim_cannot_silently_ignore_group_members(self):
        d=deepcopy(self.data);d['claims'][0]['members'].pop()
        with self.assertRaisesRegex(ValueError,'membership'):catalogue.validate(d,False)
    def test_date_must_have_valid_interval_and_source(self):
        for key,value in [('start',0),('end',-12000),('source','nonexistent'),('end',None)]:
            with self.subTest(key=key,value=value):
                d=deepcopy(self.data);d['entities'][0]['dates'][0][key]=value
                with self.assertRaises(ValueError):catalogue.validate(d,False)
    def test_media_provenance_and_source_safety(self):
        d=deepcopy(self.data);d['media'][0]['credit']=''
        with self.assertRaisesRegex(ValueError,'provenance'):catalogue.validate(d,False)
        d=deepcopy(self.data);d['sources'][0]['url']='javascript:alert(1)'
        with self.assertRaisesRegex(ValueError,'Unsafe'):catalogue.validate(d,False)
    def test_two_surfaces_are_not_two_statues(self):
        idx=catalogue.index(self.data)
        self.assertEqual(idx['entities']['hoa-back']['physical_id'],idx['entities']['hoa-front']['physical_id'])
        self.assertIsNone(idx['entities']['hoa-back']['dates'][0]['start'])
        self.assertEqual(len(idx['entities']['hoa-back']['alternate_media']),1)
        d=deepcopy(self.data);d['entities'][0]['alternate_media']=[d['entities'][0]['media']]
        with self.assertRaisesRegex(ValueError,'Repeated primary'):catalogue.validate(d,False)
    def test_motif_observations_require_real_features_and_episodes(self):
        for key,value in [('features',['made-up']),('date_indices',[100]),('status','verified-by-ai'),('scope','')]:
            d=deepcopy(self.data);d['attestations'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):catalogue.validate(d,False)
    def test_input_coverage_is_complete_and_duplicate_panels_share_identity(self):
        from pipeline.family_pages import validate_coverage
        coverage=json.loads((ROOT/'research/catalogue/input-coverage.json').read_text())
        validate_coverage(coverage,catalogue.index(self.data))
        broken=deepcopy(coverage);broken['files'].pop()
        with self.assertRaisesRegex(ValueError,'Inputs added or removed'):validate_coverage(broken,catalogue.index(self.data))
        lead=next(l for l in self.data['leads'] if l['id']=='enclosing-caption')
        self.assertEqual([p['entity'] for p in lead['panels'] if p['entity']],['laventa19','laventa19'])
        self.assertEqual(next(l for l in self.data['leads'] if l['id']=='lion-reception')['kind'],'control')
    def test_generated_dossiers_are_current_and_local_links_resolve(self):
        outputs=catalogue.outputs();parsed={}
        for path,text in outputs.items():
            self.assertEqual(path.read_text(),text,str(path))
            if path.suffix!='.html':continue
            page=Links(text)
            self.assertEqual(len(page.ids),len(set(page.ids)),str(path))
            for link in page.links:
                url=urlsplit(link)
                if url.scheme or url.netloc:continue
                target=(path.parent/unquote(url.path)).resolve() if url.path else path
                if target.is_dir():target=target/'index.html'
                self.assertTrue(target.is_file(),(path,link))
                if url.fragment and target.suffix=='.html':
                    if target not in parsed:parsed[target]=Links(target.read_text())
                    self.assertIn(unquote(url.fragment),parsed[target].ids,(path,link))

if __name__=='__main__':unittest.main()
