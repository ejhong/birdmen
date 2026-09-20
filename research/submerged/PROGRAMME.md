# The submerged landscape programme

Requested 19 September 2026. A second major strand alongside the motif and
cultural-comparison catalogue, intended to grow into a substantial research
resource. This document records the initial scope and the first implementation.

## Implemented first assessment

`docs/submerged.html` now combines six project/place records, seven data entry
points and 20 sources with a real relief explorer. World, North Sea, Sunda and
Gujarat/Khambhat views use retained, subsampled NOAA ETOPO1 downloads. The slider
changes a modern elevation threshold between 0 and −120 m. No prehistoric date
is assigned, and no archaeological detection was performed. See [DATA.md](DATA.md)
for exact provenance, limits and reproduction.

The opening assessment covers SUBNORDICA/Doggerland, Khambhat, Pavlopetri,
Murujuga, the Baltic stone alignment and Sunda. Their record types and project
periods are explicit. The dataset register covers open North Sea peat records,
GEBCO, EMODnet, NCEI surveys, satellite opportunities and the prototype's actual
relief data. “Access checked” means the documented level of checking, not that
every scientific file has been downloaded or validated.

## First completed data experiment · 20 September

The published 0.5 m Baltic AUV grid is now downloaded, retained and analysed.
`docs/bathymetry-lab.html` shows a reproducible averaging experiment: 663,281
observed cells, six spacings, depth disagreement and a fixed local-relief diagnostic.
At 115 m, 0.3% of the defined local variance remains. This is not a wall-detection
score, an accuracy estimate or a new AI result. The original ZIP, GeoTIFF hash,
method and figure are inspectable. [Provenance](../../data/submerged/baltic/README.md).

The next bounded AI task is a detection benchmark across multiple surveys with
independent labels, difficult natural controls and held-out survey areas. It needs
those data before a model score can be meaningful. See [NEXT-TESTS.md](../NEXT-TESTS.md).
SUBNORDICA's official work package 3 offers a relevant active research context.

## First research choice

The North Sea is the initial preferred candidate, an editorial assessment based
on open sea-level data, documented landscape work and the active SUBNORDICA
programme. Start with the [2025 peat study](https://www.nature.com/articles/s41586-025-08769-7)
and its [CC BY 4.0 data repository](https://zenodo.org/records/10801302).
Repository metadata and the file list have been checked; scientific contents
have not yet been reanalysed here.

1. Read the technical documentation and HOLSEA spreadsheet. Separate index points,
   limiting observations, datums and age uncertainties. Reproduce a published
   numerical result before interpolating new shorelines.
2. Establish how the published GIA, compaction and subsidence corrections relate
   to regional relative sea level. A global ice-volume curve alone cannot date
   the exposure of each present seabed cell.
3. Find an appropriate former land surface and its uncertainty. Compare a dated
   reconstruction with today's bathymetry; show burial and erosion limits.
4. Publish a regional 12,000 BP view only if the data support it, with an explicit
   calendar convention, uncertainty and reproduction files. Other well-supported
   dates may be a better starting point.
5. Overlay actual survey coverage and source quality before choosing one question
   about former freshwater margins, preservation and potential occupation.

Khambhat's first useful task is an archival and survey-context audit, seeking
original georeferenced sonar and sample records. Sunda first needs an inventory
of accessible seismic and sediment evidence. Documented sites such as Pavlopetri
can supply positive recording controls. None of these priorities is a ranking
of the likelihood of a lost civilisation.

## Opening question

What evidence of earlier coastal lives may now lie underwater, what has actually
been found, and what can existing data help us investigate?

The proposition that most interesting evidence is submerged is a hypothesis to
examine, not the premise of a map. Distinguish the Last Glacial Maximum from
12,000 years ago and specify the calendar convention of every reconstruction.

## First edition

- A beautiful orientation page with an initial source-checked assessment.
- A geographic explorer of established discoveries, active/completed programmes,
  debated claims and promising datasets. Their statuses must remain distinct.
- Doggerland / North Sea and Gulf of Khambhat (Cambay) are explicit starting
  interests. Add other well-documented regions to avoid allowing a single
  disputed claim to dominate the field.
- An annotated data register: coverage, resolution, vertical datum, acquisition
  method, access/licence, download/API link and a concrete analytical use.
- A proposed past/present map experiment with uncertainty stated at the point of
  use. Modern depth contours may be a screening layer, never a secretly substituted
  reconstruction of a dated coastline.

## Future landscape explorer

Use dated regional relative-sea-level models wherever possible. Keep modern
bathymetry, estimated palaeotopography, coastal erosion, sediment burial and survey
coverage as separate layers. Let visitors inspect multiple dates and uncertainty
bands. Do not represent a global constant-offset coastline as a settled history.

An exposed shelf is potential terrain, not evidence of occupation. The most useful
targeting question may be where former rivers, estuaries, freshwater sources and
preservation conditions overlap with survey coverage and accessible data.

## Data and methods to evaluate

- GEBCO and NOAA global relief for regional orientation and coarse screening.
- EMODnet and national hydrographic bathymetry for finer shelf morphology.
- High-resolution multibeam, side-scan sonar and sub-bottom/seismic profiles for
  surface features and buried landscapes. Check whether the data are truly open.
- Sediment cores, pollen, environmental DNA and dated archaeological material for
  independent landscape and human-context evidence.
- Landsat / Sentinel and other satellite data for appropriate shallow, clear
  water; satellite-derived bathymetry and altimetric bathymetry are different
  methods with different limits.
- Repeatable candidate detection with negative controls, independent validation
  and recorded false positives. AI suggestions must not become “ruins” by caption.

## Research dossiers

Each should identify the precise question, location precision, geological model,
survey method, observations, dates and their material basis, custody of finds,
competing readings, accessible data and the next test. Record ongoing programmes
with a checked date; do not call an ended project active. Dates on dredged wood
must not silently date nearby sonar features.

## Decisions still to earn through research

Which region offers the strongest combination of a credible palaeolandscape model,
open detailed data and a testable archaeological question? What could be learned
without collecting new data, and what would require professional fieldwork?

The first assessment should lead to a ranked set of feasible investigations based
on data access and discriminating tests, not a ranking of “mystery” or an automated
probability of a lost civilisation.
