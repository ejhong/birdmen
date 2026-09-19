# What the first landscape maps contain

The explorer shows **modern relief with a variable depth threshold**. It is not a
dated palaeocoastline model. No settlement or constructed feature was inferred
from these grids, and no satellite imagery has been analysed in this edition.

## Retained input

Source: NOAA ETOPO1 ice-surface relief (2009), served as `etopo180` by NOAA's
[ERDDAP service](https://coastwatch.pfeg.noaa.gov/erddap/info/etopo180/index.html).
The underlying global grid is at one arc-minute spacing. Four NetCDF responses
were downloaded unchanged on 19 September 2026 into `data/submerged/etopo1/`.

| View | Extent | Subsample spacing | Browser dimensions |
| --- | --- | --- | --- |
| World | 180°W–180°E, 70°S–85°N | 20 arc-minutes | 1081 × 466 |
| North Sea | 6°W–13°E, 49°N–61°N | 3 arc-minutes | 381 × 241 |
| Sunda | 94°E–120°E, 10°S–20°N | 6 arc-minutes | 261 × 301 |
| Gujarat / Khambhat | 68°E–74°E, 18°N–24°N | 2 arc-minutes | 181 × 181 |

Exact download URLs, original/derived SHA-256 hashes, extrema and metadata are in
`grids.json`. An ERDDAP stride selects nodes; it is not a mean over the intervening
area. The browser files together are 1,413,778 bytes. The serving dataset describes
WGS84 horizontal coordinates and mean-sea-level heights, and permits free use and
redistribution. Retain NOAA attribution and the dataset's qualifications.

ETOPO1 is an older compiled relief model. GEBCO_2025 and EMODnet DTM 2024 are
assessed separately as potential future inputs; they are not the displayed data.

## Reproduction

No network or model call is made during conversion or publishing:

```sh
# Optional preparation; Python with SciPy and NumPy installed:
/usr/local/bin/python3 pipeline/submerged_grid.py
# Standard-library publication and checks:
python3 pipeline/publish.py
python3 -m unittest discover -s tests
node --test tests/submerged.test.mjs
```

The converter flips the downloaded south-to-north rows into north-to-south browser
order, preserves signed elevations in metres, and writes little-endian int16
arrays. Coordinates refer to sampled nodes. The manifest records this convention.
Publishing checks both original and derived byte hashes and dimensions. Tests
also check known land/ocean locations to catch geographic orientation mistakes.
If downloading again, preserve the old response and compare hashes before updating
an edition: a live service may change its response or metadata.

The browser classifies non-negative elevations as the modern land baseline,
negative elevations within the selected interval as the gold depth screen, and
lower values as deeper water. The missing-value sentinel is 32767. There is no
ocean-connectivity mask; inland negative elevations can also be highlighted.
Equirectangular maps show orientation, not equal areas. Numbers mark approximate
project locations, including regional anchors rather than precise archaeological
features. Equivalent links and full source records accompany the maps.

## What must change for a dated reconstruction

Account for regional relative sea level, land motion, compaction, sedimentation,
erosion and ice cover, using an appropriate former land surface. Model uncertainty
must travel with the resulting coastline. Neither today's −60 m contour nor a
global −120 m setting can simply be labelled “12,000 years ago”.

The next proposed inputs are the North Sea peat database and its technical
documentation, followed by carefully checked regional model grids and survey
provenance. The programme document separates that future analysis from the
prototype delivered here.
