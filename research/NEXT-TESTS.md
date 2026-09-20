# The next useful tests

20 September 2026. **Drafts, not frozen preregistrations and not new model results.**
The saved V1–V3 experiments remain unchanged. The signal breakdown and Baltic
resolution audit are new, explicitly post-run/descriptive analyses, without API calls.

## 1. Locate before comparing — the central visual case

**Question:** can an observer distinguish a bird above a ring from a bird holding
a rounded form, and locate the relevant features in the photograph?

Start with the three central objects and six close local/foreign alternatives,
not hundreds of unrelated images. Acquire two faithful views per physical object,
with comparable available detail. No generative enhancement. Select the alternatives
for concrete confusions (wing vs hand, ring below vs disc above), before scoring.

Have two source readers independently annotate visible regions and literal relations:
above/below, adjacent/separate, touching/not demonstrable. Preserve disagreements;
unclear features receive an “unresolved” reference and cannot be counted correct by
guessing. The model must locate each feature, cite the photograph and abstain when
the relation cannot be seen. Names hidden is not a claim of blindness.

Report per-feature localization overlap, relation agreement on resolved references,
abstention, and agreement across photographs, grouped by physical object. Establish
the overlap/tolerance rule and calibration examples before any new requests. A
correct label at the wrong location fails localization. Two photographs do not
double the number of objects.

Only after this gate should a pilot compare specific visual relationships, in both
presentation orders, against the close alternatives. Report every object, not just
the best matches. A small purposive set supports a reading test, not worldwide rarity
or a shared-history conclusion. Nine objects × two presentations = a feasible
18-request single-observer diagnostic; a second observer doubles it. This is a scope
estimate, not a budget or a sample-size justification.

**Still needed:** independently reviewed reference regions, final alternatives,
matched photographs, scoring tolerances and the dated frozen protocol. More model
reasoning alone is not a substitute: the last trial’s three “scorpion present”
boxes were located in the upper bird area.

## 2. Retest the teaching-figure signal at source level

The saved 248/397 first-place result reuses 11 pairs in two directions, with
figures shared across pairs. The new `signal-audit.html` shows all of them and
an equal-pair summary. Those are descriptive checks, not 397 independent trials.

Begin with a **reading pilot** on the existing V2 source families. The ten figure
entries include two figures from one Chinese textual sequence; do not call them
ten independent traditions. Use full relevant episodes, not pooled modern biographies.
Keep the status of instruction, arrival, departure and return separate. A source
that describes disappearance does not automatically describe a sea departure.

Develop passage-linked relationship coding with the named targets and role-matched
teachers/founders, including women and local analogues. Add explicitly synthetic
contrast checks that change an actor or reverse an event. Publish them as artificial
reading checks, never as evidence from antiquity. Check passage support before
allowing similarity rankings. Log unsupported outside knowledge and disagreements.

For the main pilot, freeze the source list, coverage effort, role eligibility,
rubric, handling of ties and variants, and stopping rule. Separate specific event
relations from generic “teaches” and “travels”; report results both with and without
the generic features. Give every target the same eligible competitor pool. Show
the strongest alternative matches, direction sensitivity and source-version sensitivity.
Hold aside source families before rubric development where possible; prior AI
pretraining prevents a perfect-blindness claim.

**Still needed:** a bounded source collection and matched complete packets. The
existing V2 examples are development material, not unseen confirmation. The broader
design remains in `research/civilisers/v3/protocol-draft.md`. No new chance p-value
is justified by shuffling the same summaries again.

## 3. Bathymetry — establish what is measurable

**Completed:** `pipeline/bathymetry_resolution.py` averages the actual 0.5 m
Geersen/DLR AUV grid at six resolutions. The retained ZIP, hashes, method, measured
values and fixed-scale figure make it reproducible. This uses no AI. It measures
depth disagreement and loss of a defined local-relief diagnostic, not wall recovery.
The 10 m Gaussian scale and one grid origin are exploratory choices. Noise and
natural relief contribute to the diagnostic. Regional-grid simulations must not
be described as reconstructions of actual EMODnet observations.

**Next AI experiment:** rank independently labelled stone/structure segments
against difficult glacial, geological and survey-artifact controls from multiple
high-resolution surveys. Compare a model with simple local-relief and line/ridge
baselines. Hold out whole sites or acquisition areas, not adjacent pixels. Fix
training, validation and final test partitions before tuning. Report precision–recall,
localization error, false positives per square kilometre and performance by resolution;
never label unreviewed background “no archaeology”. Audit interpolation and data gaps.
One wall cannot validate general detection.

**Other feasible routes:** reproduce a satellite-bathymetry benchmark using optical
imagery and independent soundings, with a held-out coast and turbidity/depth strata;
or map North Sea survey coverage and interpolation flags before ranking palaeochannel
candidates. Depth prediction, landscape targeting and archaeological identification
are separate tasks. Cross-dataset elevation comparisons require vertical-datum
alignment: EMODnet DTM depths use Lowest Astronomical Tide; this explorer’s ETOPO1
elevations use mean sea level.

Primary starting points:

- [Geersen 2024 AUV survey, CC BY 4.0](https://doi.iow.de/10.12754/DATA-2024-0001)
- [Published Baltic alignment study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10895374/)
- [SUBNORDICA work package 3](https://projects.au.dk/subnordica/research/work-package-3)
- [EMODnet bathymetry and datum](https://emodnet.ec.europa.eu/en/bathymetry)
- [NASA-hosted Sentinel-2 / ICESat-2 study](https://ntrs.nasa.gov/citations/20210011367)

An interesting outcome can be a limit: identifying which real measurements are
too coarse, which apparent matches depend on a retelling, or which image features
the observer cannot locate reliably. None settles the larger historical question.
