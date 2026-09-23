# Deep Memory

An open inquiry into similarities across distant cultures and the human landscapes
now beneath the sea. Source-linked photographs, cultural connections, maps, dated
records and research that makes its limits inspectable.

[Public site](https://ejhong.github.io/birdmen/) · [Editorial changes](docs/REVISIONS.md) ·
[Research conventions](research/README.md)

Every page now shares one header and one footer site map, a single type scale with
nothing set below 12 px, and AA colour contrast. Four evidence images were replaced
with openly licensed photographs of the same objects — including an actual photograph
of the Cahokia birdman tablet in place of a modern illustration — with each previous
image kept as a second view.

The [collection](https://ejhong.github.io/birdmen/catalogue.html) now opens with
19 motif families across cultural traditions. Schema 2 separates 51 source-linked
or provisional observations from 20 proposed comparison threads, 4 optional controls
and 22 intake leads. Its 43 entity records and 56 images span 24 cultural/context
groups; these are not counts of independently verified artefacts. The
[input audit](https://ejhong.github.io/birdmen/input-audit.html) accounts for all
68 supplied files, including duplicates, modern reception and unresolved images.
A systematic worldwide survey remains future work.

The new [two walls](https://ejhong.github.io/birdmen/corpus.html) put the flagship
comparison back among its neighbours: 72 openly licensed photographs of carved surfaces,
39 Anatolian and 33 Rapanui, filtered together so the stones that carry nothing stay
visible. A bird and a rounded form share one surface in 3 of the 39 Anatolian photographs,
and those three are one object; on the Rapanui side the same combination appears across 2
objects inside a repertoire where birds dominate. Counts describe registered photographs,
never the published corpus.

The new [cluster index](https://ejhong.github.io/birdmen/clusters.html) asks which
cultural traditions keep meeting. Derived from the same register, it holds 23 culture
pairs and 19 distinct comparisons, 18 of them with no transmission route established
in this review, ordered by how many stay open *after* a source check rather than by
evidence strength. Göbekli Tepe and Rapa Nui lead with three separate lines of
comparison; each pair has a page setting the two traditions side by side, line by
line. A cluster is an index entry, not a finding of contact, and a subcomparison is
counted inside its parent line because it is not separate evidence.

The new [visual investigation](https://ejhong.github.io/birdmen/fieldwork.html)
brings together 22 physical objects, five explicit feature questions and nine dated
evidence records. Compare photographs with annotation regions, inspect ordinary
museum variants, and follow what each date actually establishes. The published
reading of the moai’s older ring as a possible egg now receives explicit treatment.
This is a source-informed exploratory study, not a new AI ranking or rarity estimate.

The [submerged-worlds programme](https://ejhong.github.io/birdmen/submerged.html)
opens with six research locations, seven data entry points and an interactive depth
explorer using retained NOAA relief data. Its world and three regional views are
**modern-depth experiments with no ancient date assigned**. A validated regional
reconstruction around 12,000 BP remains a next phase.

The [first survey experiment](https://ejhong.github.io/birdmen/bathymetry-lab.html)
measures resolution loss in the published 0.5 m Baltic AUV data. At 115 m, block
averaging retains 0.3% of the defined local-relief variance; this is a numerical
diagnostic, not AI detection or wall recovery. A new
[teaching-figure audit](https://ejhong.github.io/birdmen/signal-audit.html) unpacks
the 62.5% result into its 11 repeated pairings. The
[next tests](research/NEXT-TESTS.md) remain proposals; no new paid model calls ran.

To grow the collection, describe a cultural connection and ask for more examples,
or supply a photograph or source. See [adding evidence](research/catalogue/ADDING-EVIDENCE.md)
and [repository instructions](AGENTS.md). New photographs attach to existing object
records where appropriate; multiple views do not become independent artefacts.

## Find your way around

| Investigation | Reading page | Research and reproducibility |
| --- | --- | --- |
| 01 · Indus & rongorongo | [Study page](docs/rongo/index.html) | `pipeline/rongo/`, `data/rongo/`, `inputs/rongo/`; [method and run order](research/rongo/README.md) |
| 02 · Birds, serpents & sacred centres | [Catalogue experiment](docs/myths.html) | `pipeline/classes.py`, `analysis.py`, `build_site.py`; `data/raw/berezkin/`, `data/results/` |
| — · Culture clusters | [Cluster index](docs/clusters.html) | `pipeline/clusters.py`; mirrored by `clusters()` in `docs/catalogue-model.mjs` |
| 03 · The pillar & the moai | [Image pilots A–C](docs/pictures.html) | `pipeline/s3_*.py`; `data/s3/`; [original preregistration and changes](docs/study3/preregistration.md) |
| 04 · The civilisers | [V1: lineups](docs/heroes.html), [V2: source audit](docs/civilisers.html) | V1: `pipeline/s4_heroes.py`, `s4_mechanical.py`, `data/s4/`, [preregistration](docs/study4/preregistration.md). V2: [method](research/civilisers/v2/method.md), [evidence ledger](research/civilisers/v2/evidence.json) |
| 05 · The raven & the dove | [Flood-story coding](docs/floods.html) | `pipeline/s5_floods.py`, `s5_analysis.py`; `data/s5/`; [preregistration](docs/study5/preregistration.md) |

The [homepage](docs/index.html) now leads with the actual Pillar 43 and moai
photographs. The [central dossier](docs/pillar-and-moai.html) adds the identified
Orongo birdman boulder, a newly sourced 1919 photograph, alternate views, a zoomable
comparison viewer, feature observations, chronology, and competing explanations.
The [atlas](docs/atlas.html) retains the wider illustrated comparisons. Hancock and
Fenton receive comparable introductions on the homepage; Fenton's full illustrated
argument and preserved thread live in [their own essay](docs/fenton.html).
Old homepage and `narrative.html` bookmarks redirect to the corresponding chapters.

The [research review](docs/research-review.html) audits all five studies. Original
results remain intact; the reading pages qualify conclusions their methods cannot
support. `research/investigations.json` supplies the shared summaries and scope panels.

The new [recognition diagnostic](docs/recognition.html) is separate from the original
similarity studies: 10 photographs of 6 objects/rock surfaces, 20 planned GPT-5.5
requests, 19 completed and 1 connection failure. Against provisional AI-assembled
source-informed references, 73 of 94 scorable answers matched, 4 were wrong, 12
uncertain and 5 missing. The recognition screen failed. This is not a historical
similarity result, a representative accuracy estimate or an independently reviewed
benchmark. The protocol, prompt, images and references were frozen before requests;
individual responses and locations are inspectable. See
[the frozen protocol](research/pillar-moai/v2/protocol.md).

The [controlled follow-up](docs/view-trial.html) crosses one/two photographs with
low/high reasoning effort on the same three focal objects. All 24 requests completed
for an estimated $1.26. Primary categorical matches were 3/10, 4/10, 7/10 and 9/10,
respectively. These are **label matches, not verified perception accuracy**:
all three positive Pillar 43 scorpion answers pointed to the upper bird area rather
than the lower shaft. The separate post-run location audit makes this visible and
leaves the original categorical readout intact. Nothing authorizes historical ranking.

The [local context study](docs/local-context.html) adds a nine-object register,
a licensed Pillar 2 photograph, the 1919 reproduction of the existing Orongo rock
photograph, and the Rapa Nui museum’s paired painted birdmen. The latter image is
a source-provided preview of a 3D recording. Dates of collection are distinguished
from dates of making; duplicate photographs are not new objects. This is a purposive
context collection, not a representative baseline.

The maintained [catalogue register](research/catalogue/catalogue.json) separates
motif families, explicit observations, cultures, groups, objects/surfaces/accounts,
images, sources, intake leads and comparison claims. See [schema 2](research/catalogue/SCHEMA.md).
The [design notes](research/catalogue/CONCEPT.md) distinguish the implemented first
edition from its longer-term ambitions. Dossiers include the proposing source,
specific correspondences, differences, transmission assessment and next tests.
The [underwater programme](research/submerged/PROGRAMME.md) records an initial
assessment and a proposed North Sea investigation; [data preparation](research/submerged/DATA.md)
documents exactly what the prototype maps contain.

The civiliser source audit is exploratory: 29 passages, 10 source records and 10 figure
entries, one including two people. It is not a complete source genealogy or a global rarity
test. Source coverage, translation and recording history remain explicit. A
[stronger comparison protocol](research/civilisers/v3/protocol-draft.md) is a draft only;
no V3 rankings or results have been produced.

## Work on the site

The site is static HTML, CSS, JavaScript and JSON. Reading saved results needs no API keys,
build framework or paid model calls. From the repository root:

```sh
python3 pipeline/publish.py
python3 pipeline/publish.py --check
python3 -m unittest discover -s tests -v
node --test tests/catalogue.test.mjs tests/submerged.test.mjs tests/fieldwork.test.mjs
python3 -m http.server 4173 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:4173/`. These commands do not deploy the site.

`publish.py` uses only Python's standard library. It updates marked generated HTML sections,
publishes the registers, method, recognition records and thread transcript, and copies the supplied images
unchanged. Edit prose outside those markers directly; edit the registers for generated
content. The entire catalogue and submerged page are generated from their maintained
registers and `pipeline/catalogue.py` / `pipeline/family_pages.py` / `pipeline/submerged.py`.
`pipeline/research_updates.py` publishes the descriptive audits;
`pipeline/fieldwork.py` publishes the visual study and replays saved museum selections.
`--check` reports
drift without writing. The separate relief conversion step needs SciPy and NumPy;
publication, saved data checks and page viewing do not.

The optional Baltic reproduction uses NumPy, SciPy, Pillow and Matplotlib:

```sh
python3 pipeline/bathymetry_resolution.py
python3 -m unittest discover -s tests -p test_bathymetry_resolution.py
python3 pipeline/publish.py
```

Use an interpreter with those scientific dependencies installed. The standard-library
test run skips its three numerical checks otherwise; run them in the scientific
environment before changing the analysis. Source ZIP and figure hashes are checked
by publication without those dependencies. See [survey provenance](data/submerged/baltic/README.md).

Five pictures from the Fenton thread, and one from a post on Nan Madol, exist only inside phone screenshots. Their crop boxes
are recorded in `research/images.json` and cut by `pipeline/crop_inputs.py`, which needs
Pillow (`/usr/local/bin/python3 pipeline/crop_inputs.py`); `publish.py` only checks that the
crops exist. `pipeline/fenton_map.py` redraws `docs/img/fenton-map.svg`, the map of the
movements the thread claims, from the coastlines already in `docs/data/site.json`.

Optional browser smoke tests need Node 22+ and Chromium/Chrome. Keep the local server
running, then use `node tests/browser_smoke.mjs`. The script documents environment
overrides for the browser executable, site URL and screenshot output directory.

## Repository layout

```text
research/                     Versioned methods, source records and evidence for new work
  investigations.json         Shared register of questions, findings and limitations
  images.json                 Supplied-image identifications and unresolved credits
  civilisers/v2/              Method and source-level evidence ledger
  civilisers/v3/              Proposed comparison protocol; not run
  fenton/                     Transcript and screenshot inventory of Fenton's thread
  pillar-moai/v2/             Frozen recognition protocol, provisional references, sources and audit
  pillar-moai/v3/             Frozen view/reasoning trial; separate post-run location audit
  pillar-moai/context.json    Local object identities, evidence, image rights and date limits
  pillar-moai/fieldwork/      Exploratory image observations, selection rules and historical search log
  catalogue/                 Maintained catalogue, design notes and acquisition workflow
  submerged/                 Project/data register, map provenance and research programme
  rongo/                      Method, run order and article draft of the Indus / rongorongo study
inputs/                       Original supplied material; preserve untouched
  fenton/                     Screenshots and attachments of the thread (33 files) and one later screenshot
  rongo/                      The tweet screenshots and research briefs that started study 01
pipeline/                     Existing study scripts + offline publishing entry point
  rongo/                      Study 01's pipeline, in run order (see research/rongo/README.md)
data/                         Original datasets, model responses and calculated results
  pillar-moai/v2/             Freeze, raw request records and diagnostic results
  pillar-moai/v3/             Freeze, all 24 raw responses and controlled-trial readout
  pillar-moai/fieldwork/      Unchanged museum API responses and selection provenance
  submerged/etopo1/          Original downloaded NOAA NetCDF subsets
  submerged/baltic/          Original CC BY 4.0 AUV archive and provenance
  rongo/                      Study 01's scans, glyph crops, skeletons, results and fidelity review
docs/                         Published static site
  catalogue.html, catalogue/  Collection explorer and generated comparison dossiers
  families/, input-audit.html Motif families and complete input coverage
  submerged.html             Landscape explorer, projects and open-data assessment
  pillar-and-moai.html        Main source dossier and comparison viewer
  recognition.html           New diagnostic, all responses and model boxes
  view-trial.html             Controlled follow-up and visible location failures
  local-context.html          Illustrated local comparisons and object register
  fieldwork.html              22-object comparison, feature filters and dated historical evidence
  research-review.html       Audit and redesign requirements for all five studies
  signal-audit.html          Read-only breakdown of the teaching-figure signal
  bathymetry-lab.html         Measured resolution loss in the Baltic AUV survey
  atlas.html, fenton.html     Wider comparisons and separate Fenton essay
  rongo/                      Study 01's page, script and site data (served at /rongo/)
  data/                       Browser-ready datasets and generated registers
  img/                        Existing photographs, published input copies, the route map
    inputs/fenton/            Nine unchanged attachments and five registered crops
  study3/, study4/, study5/    Preserved preregistrations; published V2 method
tests/                        Offline integrity tests and optional browser smoke test
```

New investigations belong in a named, versioned directory under `research/`, with their
method, source register and evidence together. Original pipelines and data retain their
paths so recorded commands, imports and citations continue working. Earlier experiments
are not deleted or demoted into an inaccessible archive.

## Recognition diagnostic: inspect before rerunning

`python3 pipeline/recognition.py report` recomputes the saved diagnostic without
model calls and checks the frozen inputs. `run` needs the OpenAI SDK, certifi and
`OPENAI_API_KEY`; it resumes only missing requests, never replaces a recorded
response, uses no automatic retries, and stops after an API failure. The completed
version is frozen: create a new version to change images, references, prompt,
model, settings or the runner. Publishing has no API dependency.

The run's estimate is about USD 0.62 including a USD 0.23 reservation for the failed
connection; returned usage accounts for about USD 0.39. This is not a billing receipt.
The future comparison design and requirement for independent review are in the
protocol. No broader similarity experiment has been run in this revision.

`python3 pipeline/case_map.py` redraws the geographic context map using the existing
Natural Earth data. It shows approximate locations, without a transmission route.

## Reproduce an original experiment

Publishing and research are separate operations. Original research scripts can make
network requests, incur API charges or overwrite derived results. Inspect their commands
and method before running them. Saved results remain readable without rerunning models.

Study 01, Indus / rongorongo, was merged from its own repository on 10 September 2026 with its
history; the original repository, `ejhong/rongo`, is archived and its page redirects here. The
scripts now read `data/rongo/` and `inputs/rongo/` and write `docs/rongo/`, and run from this
repository's root (`python3 pipeline/rongo/build_site.py` refreshes published data and thumbnails from saved results).
The full run order and its heavier dependencies are in `research/rongo/README.md`.

The catalogue analysis needs NumPy (`requirements.txt`). Its recorded workflow is:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cd pipeline
python3 classes.py
python3 analysis.py
python3 build_site.py
```

The image/text pilots have additional script-specific dependencies, including Pillow,
SciPy, Pydantic and provider SDKs. The civiliser mechanical comparison also uses
`sentence-transformers` and scikit-learn. `requirements.txt` is not a lockfile for those
historical environments. Raw image-corpus downloads are not committed. Model availability
and exact historical rerun behaviour are not guaranteed.

`pipeline/s45_build.py` republishes saved study 4/5 results; `pipeline/s3_build.py` republishes
study 3 and needs its image dependencies. Neither is part of the new editorial publisher.
Do not replace an old version's evidence when creating a new version.

## Sources and rights

- The new opening uses photographs. The older AI-generated cover remains an archival
  asset; it is not archaeological evidence.
- Berezkin & Duvakin's analytical folklore catalogue, via D. Nikolaev's 2016
  `mythology-queries` snapshot: catalogue-derived data is CC BY-NC-SA 4.0.
- Natural Earth 110m coastlines: public domain.
- Catalogue image sources, credits, transformations and byte hashes are in
  `research/catalogue/catalogue.json`. Museum public-domain images, licensed
  photographs, historical scans and unresolved claim imagery are distinguished.
- The new visual study adds unchanged DAI publisher photographs and Met Open Access
  images. Its [register](research/pillar-moai/fieldwork/register.json) records rights,
  sources and hashes; the [raw-data notes](data/pillar-moai/fieldwork/README.md) explain
  the museum searches and exclusions. DAI copyright is retained.
- The submerged explorer uses NOAA ETOPO1 (2009) under the serving dataset's free
  use/redistribution terms. Retained files, request URLs and hashes are recorded in
  `research/submerged/grids.json`. GEBCO/EMODnet and satellite products are assessed
  as future inputs, not silently substituted for the displayed dataset.
- Original study references and limitations remain on each study page.
- Civiliser V2 editions, passage locators and mediation are in its evidence ledger.
- Existing photo credits remain in `docs/img/motifs/credits.json` and the atlas. Central-case sources and unchanged photo hashes are in
  `research/pillar-moai/v2/sources.json`; supplied-photo identities and unresolved
  rights remain in `research/images.json`.
- The pictures and quotations from Bruce R. Fenton's thread are reproduced for commentary.
  The photographers of the pictures he posted are mostly unidentified in the thread and are
  recorded as unresolved.

The existing MIT designation for code and eligible derived data does not relicense
third-party texts or photographs. Unverified photographic rights are not an open licence.
