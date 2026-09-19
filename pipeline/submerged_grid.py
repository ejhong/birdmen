"""Convert retained NOAA ETOPO1 NetCDF subsets into small browser grids.

Requires scipy and numpy only for this explicit preparation step. Publication and
tests use the standard library. The inputs are unmodified ERDDAP responses. This
is modern relief, not a palaeogeographic or sea-level model.

    /usr/local/bin/python3 pipeline/submerged_grid.py
"""
import hashlib
import json
from pathlib import Path
from scipy.io import netcdf_file

ROOT=Path(__file__).resolve().parents[1]
SPECS={
 'world': ('World shelves',(-70,20,85),(-180,20,180)),
 'northsea': ('North Sea',(49,3,61),(-6,3,13)),
 'sunda': ('Sunda shelf',(-10,6,20),(94,6,120)),
 'khambhat': ('Gujarat / Khambhat',(18,2,24),(68,2,74))
}

def build():
    records=[]
    dest=ROOT/'docs/data/submerged';dest.mkdir(parents=True,exist_ok=True)
    for id,(label,latq,lonq) in SPECS.items():
        source=ROOT/'data/submerged/etopo1'/f'{id}.nc'
        with netcdf_file(source,'r',mmap=False) as f:
            lat=f.variables['latitude'].data.copy();lon=f.variables['longitude'].data.copy()
            # Grid served south to north; browser rows run north to south.
            z=f.variables['altitude'].data.copy()[::-1].astype('<i2')
        binary=z.tobytes(); path=dest/f'{id}.i16';path.write_bytes(binary)
        query=lambda q:f'[({q[0]}):{q[1]}:({q[2]})]'
        url='https://coastwatch.pfeg.noaa.gov/erddap/griddap/etopo180.nc?altitude'+query(latq)+query(lonq)
        records.append(dict(id=id,label=label,path=f'data/submerged/{id}.i16',width=len(lon),height=len(lat),
            west=float(lon[0]),east=float(lon[-1]),south=float(lat[0]),north=float(lat[-1]),
            step_degrees=float(lon[1]-lon[0]),minimum=int(z.min()),maximum=int(z.max()),nodata=32767,
            encoding='signed little-endian int16 metres; rows north to south, columns west to east; sample/node registered',
            source_path=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            sha256=hashlib.sha256(binary).hexdigest(),request_url=url,retrieved='2026-09-19'))
    manifest=dict(dataset='NOAA ETOPO1 ice-surface global relief (2009), ERDDAP etopo180',
        dataset_url='https://coastwatch.pfeg.noaa.gov/erddap/info/etopo180/index.html',
        citation='Amante, C. and B. W. Eakins (2009), NOAA Technical Memorandum NESDIS NGDC-24.',
        datum='WGS84 horizontal; mean sea level vertical, as documented by the serving dataset.',
        rights='NOAA ERDDAP metadata permit free use and redistribution; retain attribution and dataset limitations.',
        limitation='Older compiled modern relief, deliberately subsampled for orientation. Grid spacing is not measurement accuracy. No sediment, erosion, land-motion, ice or ocean-connectivity reconstruction is applied. Negative inland elevations may also be highlighted. No archaeological detection or dated coastline is inferred.',
        grids=records)
    (ROOT/'research/submerged/grids.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Prepared',len(records),'grids;',sum((dest/f'{id}.i16').stat().st_size for id in SPECS),'bytes')

if __name__=='__main__':build()
