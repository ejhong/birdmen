# Deep Memory

Pictures, stories and open questions about similarities across distant cultures.
All five investigations stay together, with findings and limitations. A useful observation
is not automatically evidence for a particular historical explanation.

[Public site](https://ejhong.github.io/birdmen/) · [Editorial changes](docs/REVISIONS.md) ·
[Research conventions](research/README.md)

## Find your way around

| Investigation | Reading page | Research and reproducibility |
| --- | --- | --- |
| 01 · Indus & rongorongo | [Companion site](https://ejhong.github.io/rongo/) | [Separate repository](https://github.com/ejhong/rongo) |
| 02 · Birds, serpents & sacred centres | [Catalogue experiment](docs/myths.html) | `pipeline/classes.py`, `analysis.py`, `build_site.py`; `data/raw/berezkin/`, `data/results/` |
| 03 · The pillar & the moai | [Image pilots A–C](docs/pictures.html) | `pipeline/s3_*.py`; `data/s3/`; [original preregistration and changes](docs/study3/preregistration.md) |
| 04 · The civilisers | [V1: lineups](docs/heroes.html), [V2: source audit](docs/civilisers.html) | V1: `pipeline/s4_heroes.py`, `s4_mechanical.py`, `data/s4/`, [preregistration](docs/study4/preregistration.md). V2: [method](research/civilisers/v2/method.md), [evidence ledger](research/civilisers/v2/evidence.json) |
| 05 · The raven & the dove | [Flood-story coding](docs/floods.html) | `pipeline/s5_floods.py`, `s5_analysis.py`; `data/s5/`; [preregistration](docs/study5/preregistration.md) |

The [homepage](docs/index.html) combines the study collection first and the full illustrated
narrative below. The narrative's second section states Bruce R. Fenton's theory of a southern
origin for the Göbekli Tepe symbols, in his order and with his pictures, from his X thread of
24–26 February 2025; a verbatim transcript with one marked gap is in
[`research/fenton/thread.md`](research/fenton/thread.md). The bird-rock/Pillar 43 comparison
is in Bird-men; pigs and reptile-like animals follow Handbags. `docs/narrative.html` only redirects older links to the combined
page. `research/investigations.json` supplies the same question, finding, limitations and
version links to the collection and each local study page.

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
python3 -m http.server 4173 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:4173/`. These commands do not deploy the site.

`publish.py` uses only Python's standard library. It updates marked generated HTML sections,
publishes the registers, method and thread transcript, and copies the supplied images
unchanged. Edit prose outside those markers directly; edit the registers for generated
content. `--check` reports drift without writing.

Five pictures from the Fenton thread exist only inside phone screenshots. Their crop boxes
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
inputs/                       Original supplied material; preserve untouched
  fenton/                     Screenshots and attachments of the thread (33 files)
pipeline/                     Existing study scripts + offline publishing entry point
data/                         Original datasets, model responses and calculated results
docs/                         Published static site
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

## Reproduce an original experiment

Publishing and research are separate operations. Original research scripts can make
network requests, incur API charges or overwrite derived results. Inspect their commands
and method before running them. Saved results remain readable without rerunning models.

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

- Berezkin & Duvakin's analytical folklore catalogue, via D. Nikolaev's 2016
  `mythology-queries` snapshot: catalogue-derived data is CC BY-NC-SA 4.0.
- Natural Earth 110m coastlines: public domain.
- Original study references and limitations remain on each study page.
- Civiliser V2 editions, passage locators and mediation are in its evidence ledger.
- Existing photo credits remain in `docs/img/motifs/credits.json` and the illustrated
  narrative; new photo provenance and unresolved rights are in `research/images.json`.
- The pictures and quotations from Bruce R. Fenton's thread are reproduced for commentary.
  The photographers of the pictures he posted are mostly unidentified in the thread and are
  recorded as unresolved.

The existing MIT designation for code and eligible derived data does not relicense
third-party texts or photographs. Unverified photographic rights are not an open licence.
