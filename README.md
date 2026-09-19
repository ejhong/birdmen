# Deep Memory

An open inquiry into similarities across distant cultures and the human landscapes
now beneath the sea. Source-linked photographs, cultural connections, maps, dated
records and research that makes its limits inspectable.

[Public site](https://ejhong.github.io/birdmen/) · [Editorial changes](docs/REVISIONS.md) ·
[Research conventions](research/README.md)

The [comparison collection](https://ejhong.github.io/birdmen/catalogue.html) has
19 comparison threads, 4 optional controls, 35 curated groups, 23 cultural/context
clusters and 40 source records. Browse photographs, cultural connections, a map,
timeline or themes. This first edition combines the existing archive with new
source checks; it is not yet a systematic worldwide survey.

The [submerged-worlds programme](https://ejhong.github.io/birdmen/submerged.html)
opens with six research locations, six data entry points and an interactive depth
explorer using retained NOAA relief data. Its world and three regional views are
**modern-depth experiments with no ancient date assigned**. A validated regional
reconstruction around 12,000 BP remains a next phase.

To grow the collection, describe a cultural connection and ask for more examples,
or supply a photograph or source. See [adding evidence](research/catalogue/ADDING-EVIDENCE.md)
and [repository instructions](AGENTS.md). New photographs attach to existing object
records where appropriate; multiple views do not become independent artefacts.

## Find your way around

| Investigation | Reading page | Research and reproducibility |
| --- | --- | --- |
| 01 · Indus & rongorongo | [Study page](docs/rongo/index.html) | `pipeline/rongo/`, `data/rongo/`, `inputs/rongo/`; [method and run order](research/rongo/README.md) |
| 02 · Birds, serpents & sacred centres | [Catalogue experiment](docs/myths.html) | `pipeline/classes.py`, `analysis.py`, `build_site.py`; `data/raw/berezkin/`, `data/results/` |
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
cultures, groups, objects/surfaces/accounts, images, sources and comparison claims.
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
node --test tests/catalogue.test.mjs tests/submerged.test.mjs
python3 -m http.server 4173 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:4173/`. These commands do not deploy the site.

`publish.py` uses only Python's standard library. It updates marked generated HTML sections,
publishes the registers, method, recognition records and thread transcript, and copies the supplied images
unchanged. Edit prose outside those markers directly; edit the registers for generated
content. The entire catalogue and submerged page are generated from their maintained
registers and `pipeline/catalogue.py` / `pipeline/submerged.py`. `--check` reports
drift without writing. The separate relief conversion step needs SciPy and NumPy;
publication, saved data checks and page viewing do not.

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
  submerged/etopo1/          Original downloaded NOAA NetCDF subsets
  rongo/                      Study 01's scans, glyph crops, skeletons, results and fidelity review
docs/                         Published static site
  catalogue.html, catalogue/  Collection explorer and generated comparison dossiers
  submerged.html             Landscape explorer, projects and open-data assessment
  pillar-and-moai.html        Main source dossier and comparison viewer
  recognition.html           New diagnostic, all responses and model boxes
  view-trial.html             Controlled follow-up and visible location failures
  local-context.html          Illustrated local comparisons and object register
  research-review.html       Audit and redesign requirements for all five studies
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
