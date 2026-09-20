"""Exploratory resolution audit of a real AUV survey, without model/API calls.

Run with NumPy, SciPy, Pillow and Matplotlib installed:
    python3 pipeline/bathymetry_resolution.py
The original CC BY 4.0 archive is retained. This is a detectability prerequisite,
not a classifier, a wall-recovery score or an archaeological discovery.
"""
from io import BytesIO
import hashlib
import json
from pathlib import Path
import zipfile
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/submerged/baltic/data-2024-0001.zip'
GRID='Geersen_2024_multibeam_AUV.tif'
FACTORS=(1,4,10,20,50,230)


def block_average(a,valid,factor):
    """Mean of observed cells only, aligned at the original upper-left corner.

    Partial blocks are allowed and weighted by their observed cell count in
    all error summaries. No missing cell is treated as a zero depth.
    """
    h,w=a.shape
    ph=(-h)%factor;pw=(-w)%factor
    values=np.pad(np.where(valid,a,0),((0,ph),(0,pw)))
    weights=np.pad(valid.astype(np.int32),((0,ph),(0,pw)))
    shape=((h+ph)//factor,factor,(w+pw)//factor,factor)
    sums=values.reshape(shape).sum(axis=(1,3))
    counts=weights.reshape(shape).sum(axis=(1,3))
    mean=np.divide(sums,counts,out=np.full_like(sums,np.nan,dtype=float),where=counts>0)
    expanded=mean.repeat(factor,axis=0).repeat(factor,axis=1)[:h,:w]
    return mean,expanded,counts


def analyse(a,valid,pixel_size=.5):
    # A fixed 10 m Gaussian neighbourhood defines the local-relief diagnostic.
    # Normalised convolution excludes missing depths. Only well-supported centres
    # (at least 95% Gaussian weight observed) enter this diagnostic.
    sigma=10/pixel_size
    weight=gaussian_filter(valid.astype(float),sigma,mode='constant',cval=0)
    smooth=gaussian_filter(np.where(valid,a,0),sigma,mode='constant',cval=0)
    trend=np.divide(smooth,weight,out=np.full_like(smooth,np.nan),where=weight>0)
    support=valid&(weight>=.95)
    residual=a-trend
    rows=[];maps={}
    local_variance=float(np.var(residual[support]))
    for factor in FACTORS:
        coarse,reconstructed,counts=block_average(a,valid,factor)
        # To isolate loss of fine detail, apply the SAME averaging operator to the
        # original residual field. This is not a residual of a newly fitted model.
        _,resampled_residual,_=block_average(residual,support,factor)
        delta=reconstructed[valid]-a[valid]
        rows.append(dict(spacing_m=factor*pixel_size,valid_blocks=int((counts>0).sum()),
                         depth_rmse_m=float(np.sqrt(np.mean(delta**2))),
                         depth_max_abs_error_m=float(np.max(np.abs(delta))),
                         local_variance_retained=float(np.var(resampled_residual[support])/local_variance)))
        maps[factor]=np.where(support,resampled_residual,np.nan)
    return rows,maps,support,local_variance


def main():
    raw=SOURCE.read_bytes()
    with zipfile.ZipFile(BytesIO(raw)) as z: grid_bytes=z.read(GRID)
    image=Image.open(BytesIO(grid_bytes));a=np.asarray(image,dtype=float)
    pixel_size=image.tag_v2[33550][0]
    if image.tag_v2[33550][:2] != (.5,.5):raise ValueError('Unexpected survey spacing')
    valid=np.isfinite(a)&(a>-1e20)
    rows,maps,support,variance=analyse(a,valid,pixel_size)
    result=dict(status='Exploratory numerical resolution audit; no AI model or archaeological detector run',
                source=dict(title='Geersen 2024 AUV multibeam survey',url='https://doi.iow.de/10.12754/DATA-2024-0001',download='https://doi.iow.de/doi/2024/data-2024-0001/data-2024-0001.zip',license='CC BY 4.0',credit='J. Geersen; AUV data acquired by DLR during Littorina cruise L0123 (2023)',path=str(SOURCE.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),grid_sha256=hashlib.sha256(grid_bytes).hexdigest()),
                grid=dict(width=a.shape[1],height=a.shape[0],spacing_m=pixel_size,crs='EPSG:32632 · WGS 84 / UTM zone 32N',upper_left_m=list(image.tag_v2[33922][3:5]),valid_cells=int(valid.sum()),total_cells=a.size,depth_min_m=float(a[valid].min()),depth_max_m=float(a[valid].max()),vertical_datum='Not resolved from the GeoTIFF metadata; within-survey relative relief only'),
                method=dict(block_origin='upper left of the original grid',aggregation='arithmetic mean of valid source cells; partial blocks retained; no interpolation into missing areas',local_relief='original depth minus normalised Gaussian mean, sigma 10 metres; retain centres with at least 95% observed Gaussian support; block-average this fixed residual field',local_support_cells=int(support.sum()),local_variance_m2=variance,missing='Masked, never interpreted as absence of archaeology',comparison='RMSE at the same original observed cells. Local variance at the same supported cells; descriptive, not a detection rate.'),
                results=rows,limitations=['One known-site survey, selected after publication; no blind or independent archaeological labels.','115 m square blocks illustrate loss of detail; they do not reproduce EMODnet’s angular grid, original measurements, interpolation or datum.','No recovery model, AI classification, wall trace or new archaeological feature is claimed.','Different grid origins, survey noise, object size and relief affect these measurements.'])
    plot(maps,a.shape,pixel_size)
    figure=ROOT/'docs/img/submerged/baltic-resolution.png'
    result['figure']=dict(path=str(figure.relative_to(ROOT/'docs')),sha256=hashlib.sha256(figure.read_bytes()).hexdigest())
    target=ROOT/'research/submerged/resolution-result.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(valid_cells=int(valid.sum()),local_support=int(support.sum()),results=rows),indent=2))


def plot(maps,shape,pixel_size):
    # Scientific visualization of measured arrays, not an edited artefact image.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    cmap=LinearSegmentedColormap.from_list('seabed',['#163d49','#adc0b9','#efe9d9','#c49656','#6e492c'])
    cmap.set_bad('#163d49')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':'#253c3e','axes.labelcolor':'#253c3e'})
    fig,axes=plt.subplots(4,1,figsize=(12.6,12.1),layout='constrained',facecolor='#f5f1e7')
    extent=(0,shape[1]*pixel_size,0,shape[0]*pixel_size)
    for ax,factor in zip(axes,[1,4,20,230]):
        im=ax.imshow(maps[factor],extent=extent,origin='upper',interpolation='nearest',cmap=cmap,vmin=-.15,vmax=.15,aspect='equal')
        ax.set_title(f'{factor*pixel_size:g} m grid',loc='left',fontsize=13,fontweight='medium',pad=8)
        ax.set_ylabel('Northing offset (m)');ax.set_xlabel('Easting offset (m)')
        ax.spines[['top','right']].set_visible(False)
    fig.colorbar(im,ax=axes,orientation='horizontal',shrink=.6,aspect=45,pad=.035,label='Local relief relative to a 10 m Gaussian neighbourhood (m)',extend='both')
    dest=ROOT/'docs/img/submerged';dest.mkdir(parents=True,exist_ok=True)
    fig.savefig(dest/'baltic-resolution.png',dpi=150,metadata={'Title':'AUV survey: resolution and local relief','Description':'Measured Geersen 2024 data, CC BY 4.0. Fixed scale; missing/unsupported areas masked. Not an archaeological classification.'})
    plt.close(fig)


if __name__=='__main__':main()
