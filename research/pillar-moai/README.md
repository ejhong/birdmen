# The pillar, the moai and the bird

This investigation separates the objects, visual observations, resemblance and
historical explanation. The main reading page is `docs/pillar-and-moai.html`;
the instrument diagnostic is `docs/recognition.html`.

## This edition

- `v2/sources.json`: checked sources and five photographic assets, with rights,
  origin and unchanged-byte hashes. The 1919 boulder image is a new acquisition.
- `v2/reference.json`: provisional feature references and exact input photographs.
  These were assembled by AI, not independently reviewed by specialists.
- `v2/protocol.md`: fixed recognition diagnostic and proposed later comparison.
- `v2/legacy-audit.json`: selected examples from old saved responses, without
  altering the originals or pretending the examples measure an error rate.
- `../../data/pillar-moai/v2/`: dated freeze, raw records and computed results.

Original image experiments remain at `data/s3/` and `docs/pictures.html`.
No historical resemblance rankings were produced by the new recognition pilot.
One request failed with APIConnectionError inside the sandbox before returning a
model response. The resumed run kept that failure and completed the other 19
planned requests; there was no replacement of an inconvenient model answer.

## Follow-up: view trial 3.0

`v3/protocol.md` and `v3/reference.json` were frozen before 24 new requests.
The trial crosses low/high reasoning with one/two views, using the same GPT-5.5
snapshot and six unchanged images. Each condition includes both primary-image
orders; these are different inputs, not stochastic repeats. All requests completed.

Primary label matches: low/single 3/10, low/paired 4/10, high/single 7/10,
high/paired 9/10. Full labels: 20/30, 22/30, 26/30, 28/30. Uncertainty stays in
the denominator. The estimated usage cost was USD 1.25556, within the USD 8 cap.

**The labels overstate verified recognition.** After the run, all three positive
Pillar 43 scorpion answers were inspected against the source and photograph.
Their boxes lie in the upper bird area; the scorpion is on the lower shaft.
`v3/location-audit.json` records this post-run check. It is AI-assisted, not expert
review, and does not silently replace the frozen categorical results.

`pipeline/view_trial.py report` reproduces the report offline. `run` requires
the OpenAI SDK, certifi and credentials, and only executes cells without an existing
record. Inputs, code and observations in this run are immutable. New experiments
need a new version. The reading page is `docs/view-trial.html`.

`context.json` is a separate, editable register of nine focal/local objects and
new image sources. It is not a scored corpus. The local study appears at
`docs/local-context.html`. The Orongo rock’s 1919 reproduction and the existing
Mata Ngarau image represent the same photograph/surface; do not count them twice.

## Expanded visual study — 20 September 2026

`fieldwork/register.json` now records 22 distinct physical objects: the nine
focal/local examples, twelve museum selections and the previously proposed
Assyrian eagle-headed figure. Three new DAI photographs resolve the missing
views of Pillars 33, 38 and 56. Twelve unchanged Met images add ordinary variants
under the documented [selection rules](fieldwork/SELECTION.md).

`docs/fieldwork.html` compares five literal features, with image-relative regions,
per-view observations, sources and date qualifications. These AI-prepared editorial
readings still require independent review. No new model requests or historical
similarity scores were produced. [The study notes](fieldwork/README.md) explain
its scope; [the historical search log](fieldwork/SEARCH-LOG.md) records the trail.

The 2014 digital study proposes that the moai’s older ring became part of the
later birdman composition, possibly as an egg. The damaged arms make our earlier
categorical held/not-held language too strong. Mutable reading pages now reflect
that interpretation and its uncertainty; frozen V2/V3 references remain untouched.

## What remains scientifically open

The dossier now identifies the boulder, separates carving episodes, distinguishes
visible motifs from interpretations, and establishes concrete perception failures.
It does not yet establish a transmission history or a worldwide rarity rate.
The next bottleneck is independent checking of images and reference observations,
followed by a broader, object-deduplicated local and comparative corpus. The full
requirements are in the protocol. A second large batch of the old scoring task
would not solve that problem.

## Supplied material awaiting identification

The following user files were already present and remain untouched. They are
research leads, not additions to the scored corpus. Similar appearance alone is
insufficient to identify them or date them.

| Input | Visible subject / next check |
| --- | --- |
| `inputs/HR8a1UQWYAMKmRJ.jpeg` | Architectural birdlike mask; find the original site/collection caption. |
| `inputs/HR8a1UvaIAAYYKT.jpeg` | Birdlike head in profile; establish its relation to the other views. |
| `inputs/HR8a1UvacAANypP.jpeg` | Human face framed by a birdlike form; identify the monument and photographer. |
| `inputs/HR9-AR_XwAMVrSt.jpeg` | Staff-bearer montage; identify each underlying object before comparing. |
| `inputs/HSWTVsSWMAAp-sG.jpeg` | Two figures holding animals; verify object dates, authenticity and photo sources separately. |
| `inputs/Screenshot 2026-09-13 at 5.14.08 AM.png` | Claimed San Agustín / Karahan Tepe comparison; verify both objects against collection or excavation records. |

These do not need to be resolved to inspect the now-identified central three
objects. Their eventual inclusion should carry source and rights records.
