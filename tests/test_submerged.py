from copy import deepcopy
import json
from pathlib import Path
import struct
import unittest
from pipeline import submerged
from test_catalogue import Links
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]

class SubmergedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'research/submerged/register.json').read_text())
        cls.manifest=json.loads((ROOT/'research/submerged/grids.json').read_text())

    def test_source_register_and_saved_data_integrity(self):
        submerged.validate(self.data,self.manifest)

    def test_unsupported_records_and_invalid_regions_are_rejected(self):
        data=deepcopy(self.data);data['projects'][0]['sources']=['missing']
        with self.assertRaisesRegex(ValueError,'Unsupported'):submerged.validate(data,self.manifest)
        data=deepcopy(self.data);data['projects'][0]['region']='missing'
        with self.assertRaisesRegex(ValueError,'location'):submerged.validate(data,self.manifest)
        data=deepcopy(self.data);data['sources'][0]['url']='javascript:alert(1)'
        with self.assertRaisesRegex(ValueError,'Unsafe'):submerged.validate(data,self.manifest)

    def test_corrupt_dimensions_or_source_hash_cannot_publish(self):
        manifest=deepcopy(self.manifest);manifest['grids'][0]['width']+=1
        with self.assertRaisesRegex(ValueError,'dimensions'):submerged.validate(self.data,manifest)
        manifest=deepcopy(self.manifest);manifest['grids'][0]['source_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'changed'):submerged.validate(self.data,manifest)

    def test_geographic_spot_checks_detect_flipped_rows_or_wrong_signs(self):
        # These known land/ocean positions check the geographic meaning of the
        # retained grid, independently of the optional NetCDF conversion code.
        checks=[('world',0,-150,False),('world',46,8,True),
                ('northsea',55.5,3.5,False),('northsea',55,-4,True)]
        for id,lat,lon,land in checks:
            g=next(g for g in self.manifest['grids'] if g['id']==id)
            data=(ROOT/'docs'/g['path']).read_bytes()
            x=round((lon-g['west'])/(g['east']-g['west'])*(g['width']-1))
            y=round((g['north']-lat)/(g['north']-g['south'])*(g['height']-1))
            z=struct.unpack_from('<h',data,2*(y*g['width']+x))[0]
            with self.subTest(grid=id,lat=lat,lon=lon):
                self.assertNotEqual(z,g['nodata']);self.assertEqual(z>=0,land)

    def test_page_and_static_maps_are_current_and_local_links_resolve(self):
        for path,text in submerged.outputs().items():
            self.assertEqual(path.read_text(),text,str(path))
            if path.suffix!='.html':continue
            page=Links(text)
            self.assertEqual(len(page.ids),len(set(page.ids)))
            for link in page.links:
                url=urlsplit(link)
                if url.scheme or url.netloc:continue
                target=(path.parent/unquote(url.path)).resolve() if url.path else path
                if target.is_dir():target=target/'index.html'
                self.assertTrue(target.is_file(),link)
                if url.fragment and target.suffix=='.html':
                    self.assertIn(unquote(url.fragment),Links(target.read_text()).ids,link)

if __name__=='__main__':unittest.main()
