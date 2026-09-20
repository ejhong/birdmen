# Baltic AUV survey

Original archive downloaded on 20 September 2026:

- J. Geersen (2024), **AUV multibeam data** associated with the Baltic stone-alignment
  study. AUV data acquired by DLR during Littorina cruise L0123 in 2023.
- [Persistent dataset record](https://doi.iow.de/10.12754/DATA-2024-0001)
- [Original ZIP](https://doi.iow.de/doi/2024/data-2024-0001/data-2024-0001.zip)
- Licence: **CC BY 4.0**, as stated on the dataset record.
- [Associated archaeological paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10895374/)

`data-2024-0001.zip` is retained unchanged. It contains
`Geersen_2024_multibeam_AUV.tif`: 2,355 × 742 cells, 0.5 m spacing,
WGS 84 / UTM 32N (EPSG:32632), 663,281 valid depth cells. Missing values are masked.
The vertical datum has not been resolved from the GeoTIFF metadata. No cross-datum
elevation comparison or prehistoric shoreline is inferred.

`pipeline/bathymetry_resolution.py` reads these bytes directly. It requires NumPy,
SciPy, Pillow and Matplotlib; publication uses only the saved JSON and figure.
`research/submerged/resolution-result.json` records hashes of the ZIP, extracted
GeoTIFF and rendered figure, parameters, all measured values and limitations.

The exploratory analysis averages valid measurements into 0.5, 2, 5, 10, 25 and
115 m square blocks. Partial edge blocks are retained. Error is computed on the
same original observed cells, not on invented measurements outside survey coverage.
The local-relief diagnostic subtracts a normalised Gaussian mean (sigma 10 m),
retains well-supported centres (95% observed kernel weight), then averages that
fixed residual field. Its variance is not a labelled structure-detection metric.
Noise and natural seabed relief contribute; changing scale or grid origin can
change the result. There is no trained model, wall ground-truth mask or discovery.

The figure is a scientific rendering of measured arrays, with one colour scale,
not a generated or enhanced archaeological image.
