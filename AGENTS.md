# Working on Deep Memory

Deep Memory investigates apparent connections across ancient cultural traditions
and evidence potentially preserved in submerged landscapes. Preserve curiosity
and make the evidence inspectable. The site should be calm, beautiful and easy to
browse; implementation details belong in research records, not the reading flow.

## Project structure

- `docs/` is the GitHub Pages site. It uses native HTML, CSS, JavaScript and JSON.
- `research/` holds maintained source registers, editorial decisions and protocols.
- `data/` holds experimental inputs and saved results. Preserve raw responses.
- `pipeline/publish.py` generates marked regions and publishes source registers.
- `pipeline/catalogue.py` validates the catalogue and generates its HTML dossiers.
- `research/catalogue/catalogue.json` is the maintained catalogue source. Generated
  `docs/catalogue.html`, `docs/catalogue/*.html` and `docs/data/catalogue.json`
  must be changed through the register or publisher, not hand-edited.
- Schema 2 adds motif `families`, explicit `attestations` and unresolved `leads`.
  `pipeline/family_pages.py` generates `docs/families/` and `docs/input-audit.html`.
  Never infer an object's features from a claim's motif tags or from another
  object in the same culture. An attestation names its scope, feature subset,
  source and dated episode; separate observations do not prove a co-occurring set.
- Account for every supplied file in `research/catalogue/input-coverage.json`,
  including extra views, unresolved fragments and context-only material. Hash
  originals; never turn unverified montage captions into dated culture records.
- `research/submerged/` holds the underwater assessment and grid provenance.
  `pipeline/submerged.py` generates `docs/submerged.html`, its JSON registers and
  static map fallbacks. `pipeline/submerged_grid.py` is a separate, optional
  SciPy preparation step from retained original NetCDF downloads.
- `pipeline/research_updates.py` publishes the descriptive teaching-figure audit
  and `docs/bathymetry-lab.html`. `pipeline/bathymetry_resolution.py` is the optional
  scientific step from the retained AUV ZIP. Publishing uses saved results only.
  Resolution loss is not AI detection, survey accuracy or wall recovery.
  New experiment proposals belong in `research/NEXT-TESTS.md`; freeze a separate
  protocol before any new model runs, without rewriting the old protocols.

## Evidence rules

1. Distinguish a proposing source from evidence supporting the proposal. Attribute
   guest articles to their authors, not automatically to their host.
2. Separate cultures/periods, curated example groups, comparison threads, physical
   objects, surfaces, photographs and narrative witnesses. Reusing an image or a
   different surface does not produce independent evidence.
3. A claimed anomaly belongs in the catalogue before it is explained, provided
   its source and unresolved questions are explicit. Inclusion is not a finding
   that ordinary diffusion has been excluded. Useful controls remain optional.
4. Keep context dates, object production, later carvings, wood ages, composition,
   surviving witnesses and collection dates separate. Unknown dates stay unknown.
   Signed historical years use negative BCE and positive CE, without year zero.
5. Use authentic, source-linked evidence images. Never use generated imagery as
   artefact evidence. Preserve original bytes, credits, rights and transformations.
6. AI perception is an instrument to validate. A plausible description or high
   similarity score is not a verified location, identification or historical link.
7. Freeze protocols before experiments. Do not edit frozen recognition/view-trial
   inputs, code, prompts or outputs to improve a result. Add a new version or a
   clearly labelled post-run audit. Never run paid model calls just to publish.
8. Include local scholarship and the knowledge of living communities. Geographic
   umbrella groups must not be presented as homogeneous cultures.

## Submerged-landscape programme

See `research/submerged/PROGRAMME.md`. This is a second major strand alongside the
comparison catalogue. Distinguish direct archaeological discoveries, potential
landscapes, disputed claims and analytical opportunities. Modern bathymetry is not
a dated palaeoshoreline: account for regional relative sea level, land motion,
sedimentation, erosion and uncertainty. Never equate a sonar shape or dredged
object with an in-situ dated settlement. Satellite imagery has depth, turbidity
and resolution limits and cannot expose arbitrary deep seafloor detail.

## Delivery and verification

Preserve unrelated user changes and untracked supplied files. Keep standalone
dossiers readable without JavaScript, and make map/timeline content accessible
through text records. Shareable filters must survive navigation and browser back.
Do not imply migration with comparison lines or false precision with map pins.

Run checks appropriate to the change:

```sh
python3 pipeline/publish.py
python3 -m unittest discover -s tests
python3 pipeline/publish.py --check
node --test tests/catalogue.test.mjs tests/submerged.test.mjs
```

For browser checks, serve `docs/`, then run `tests/browser_smoke.mjs` with
`BIRDMEN_SITE_URL` set to that server. Use an isolated browser profile. Review
desktop and mobile screenshots when presentation changes. No model requests are
needed for these checks. Commit and push only when the conversation authorizes
it; an authorization already given does not need repeating.
