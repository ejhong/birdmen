# Saved museum retrievals

Acquired 20 September 2026 from the Metropolitan Museum of Art's
[Collection API](https://collectionapi.metmuseum.org/public/collection/v1).
JSON response bytes are retained unchanged. Museum metadata is provided through
the Met's Open Access programme; selected photographs are marked public domain
in their object records. DAI and other images have separate rights in the research
register and are not relicensed by inclusion here.

Four `search-*.json` files retain requests of this form:

```text
https://collectionapi.metmuseum.org/public/collection/v1/search?title=true&hasImages=true&q=Horus
https://collectionapi.metmuseum.org/public/collection/v1/search?title=true&hasImages=true&q=Thoth
https://collectionapi.metmuseum.org/public/collection/v1/search?title=true&hasImages=true&q=winged%20protective%20spirit
https://collectionapi.metmuseum.org/public/collection/v1/search?title=true&hasImages=true&q=Relief%20panel
```

| Query | IDs returned | Inspected to stopping point | Included |
| --- | ---: | ---: | ---: |
| Horus | 117 | 4 | 4 |
| Thoth | 25 | 6 | 4 |
| winged protective spirit | 1 | 1 | 0 |
| Relief panel, Assyrian replacement batch | 34 | 14 | 4 |

Thirty `met-<id>.json` files retain `/objects/<id>` responses. These include
prefetches beyond the stopping points and the previously proposed 322614 anchor.
Only the 25 inspected candidates in the replay are inclusion/exclusion decisions;
prefetched records are not additional image observations. Twelve new objects are
selected. The four Horus objects remain despite their lack of a bird-headed figure.

The modern locket 891642 is excluded; its zero numeric dates must not be treated
as ancient. Thoth priest shabtis depict priests and are excluded under the subject
rule. The replacement query and prior anchor are documented in
[`SELECTION.md`](../../../research/pillar-moai/fieldwork/SELECTION.md).

`pipeline/fieldwork.py` replays the retained searches in numeric ID order, stopping
at four eligible records or query exhaustion. It publishes candidate decisions
with source-response hashes to `docs/data/pillar-moai/fieldwork/selection.json`.
Missing metadata before a stopping point fails publication rather than silently
dropping a candidate. Live API changes do not affect the saved edition.

Twelve unchanged Met display images and three unchanged DAI publisher photographs
are in `docs/img/fieldwork/`. Origin URLs, dimensions, SHA-256, credits and rights
are in `research/pillar-moai/fieldwork/register.json`. Existing focal photographs
and the Assyrian anchor image are reused from their original repository paths.
No AI-generated reconstruction or raster contour enhancement was used.
