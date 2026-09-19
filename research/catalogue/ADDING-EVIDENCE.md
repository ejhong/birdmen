# Growing the collection

Tell the assistant which cultural connection or group to expand, provide images
or links if you have them, and describe the feature that caught your eye. “Find
more securely identified Rapanui bird-and-rounded-form examples” is a useful
research request. The site also links a GitHub issue form for asynchronous leads.

The hierarchy is **cultural traditions → comparison threads → curated groups →
objects, surfaces or narrative witnesses → images and sources**. A comparison can
join several groups. The culture view aggregates those threads; it does not
convert their number into an anomaly score or a claim of independent evidence.

## Editorial workflow

1. Preserve the proposing source and the original image's caption. Establish what
   exact features are being compared before replacing an image with a clearer one.
2. Look for an existing object record. A new view, a crop or a photograph of the
   other side is not another independent artefact. Link alternate surfaces using
   `physical_id`; identify every actual image separately in `media`.
   Set the entity's `media` to its primary image ID and add further photographs
   of the same example to `alternate_media`. They appear inside the dossier's
   “Another view” disclosure without creating another group member. A newly
   documented carving episode or surface can have its own entity record while
   retaining the same `physical_id`.
3. Trace identity, provenance, image creator/rights and object-specific dates.
   Mark incomplete checks explicitly. For unknown images, do not infer findspots
   or dates from similarity. Keep modern illustrations and reconstructions labelled.
4. Add or update the maintained `catalogue.json` register. Sources, media, entities,
   groups, cultures and claims use stable IDs. Groups state a selection reason;
   a culture can span many dated episodes without making them contemporary.
5. Assign the image to a documented entity and the entity to the relevant curated
   group. A single example can participate in several feature comparisons without
   implying it matches everything in either cultural repertoire.
6. Review all affected claims. Add correspondence, difference and next-test notes,
   and link controls. Keep a narrow subcomparison's `parent` reference so its
   culture-connection count does not masquerade as another independent family.
7. Publish, validate and inspect the resulting cards, map, timeline and dossiers.
   Record substantive corrections in `docs/REVISIONS.md`.

For example: “Expand the Anatolia–Rapa Nui bird-and-rounded-form comparison.
Find five candidate objects, prioritise excavation and museum sources, keep
unidentified leads separate, and add any better views of objects already here.”
It is also fine to send one image and ask where it belongs. A lead can be recorded
without inventing a date, findspot or cultural identity.

Use a new image's original download bytes, record the source URL and SHA-256 hash,
and preserve creator, rights, caption and any transformation. Update the register
before regenerating the pages:

```sh
python3 pipeline/publish.py
python3 -m unittest discover -s tests
node --test tests/catalogue.test.mjs tests/submerged.test.mjs
```

For a batch that changes navigation or layout, run the documented browser smoke
checks too. A data-only batch needs the affected dossiers and image credits
reviewed, not another paid AI similarity experiment.

Every dated range needs a source, a type of episode and a qualification. Numerical
unknowns are `null`, never 0. The date filter means **any recorded interval overlaps**;
it does not mean two cultures coexisted. One cannot infer motif frequency or absence
from this selected first-edition corpus.

## Next acquisition batches

- Expand the Anatolia–Rapa Nui repertoire with identified objects and alternate
  views. Several current groups still contain only one registered example.
- Replace caption leads with museum/excavation records, retaining the correction.
- Acquire architecture photographs and phase plans from traceable open sources.
- Broaden regional coverage and claim authors, while retaining first-proposal
  provenance and avoiding many copies of the same internet montage.
- Invite independent subject specialists to review identity, chronology and feature
  descriptions before resuming historical similarity rankings.
