# Deep Memory — bird-men, handbags and the navel of the world

Case study 2 of a test bench for claims of long-distance motif transmission (case study 1:
[Indus and rongorongo](https://github.com/ejhong/rongo)). Social-media posts pair bird-headed
figures, serpents, "handbags" and sacred centres called navels across Iran, Assyria, Egypt,
Mexico, Anatolia, the Andes and Easter Island. The iconography has no inventory to count over;
the myths do. This repo tests whether bird-people, cosmic-serpent and world-centre myths
co-occur across the world's traditions more than unrelated motifs would, using the
Berezkin–Duvakin analytical catalogue (926 traditions × 2,138 motifs, 2016 snapshot).

Site: **https://ejhong.github.io/birdmen/**

- `docs/index.html` — the overview: every recurring picture and story (bird-men, handbags, the navel, hands on the belly, serpents, the civilisers), what the lost-source and scholarly accounts each say, what can be tested, and the design of study 3 (the pictures).
- `docs/myths.html` — study 2: the motif co-occurrence test on the Berezkin catalogue (the results below).
- `docs/pictures.html` — study 3 pilot: 1,270 Commons images from ten traditions, blind-coded composition (Opus 5 and Sonnet 5), pre-registered in `docs/study3/preregistration.md`; code in `pipeline/s3_*.py`, data in `data/s3/` (raw images not committed).
- Study 1, Indus and rongorongo, lives in its own repo: https://github.com/ejhong/rongo

**Note: this tests myths only, on a 2016 snapshot with thin coverage of the ancient Near East and Easter Island. It does not test the similarity of the pictures, which is the stronger part of the claim and remains open.**

Short version: all three motif classes are widespread (55%, 37%, 38% of traditions); they
co-occur in 131 traditions, which is *fewer* than a documentation-preserving null predicts;
the real bundle ranks 2,996 of 5,000 random bundles; two of the eight named cultures carry
the bundle, which random matched sets match 10% of the time; and the cosmic serpent is less
spatially clustered than a random motif of its frequency.

## Run it

```
python -m venv .venv && . .venv/bin/activate && pip install numpy
cd pipeline
python classes.py      # keyword rules -> data/classes.json
python analysis.py     # -> data/results/results.json (about 30 s)
python build_site.py   # -> docs/data/site.json
```

## Sources

- Yu. E. Berezkin & E. N. Duvakin, *Thematic classification and areal distribution of
  folklore-mythological motifs. Analytical catalogue*, ruthenia.ru/folklore/berezkin. CC BY-NC-SA 4.0.
- D. Nikolaev, mythology-queries (github.com/macleginn/mythology-queries): 2016 parse of the
  catalogue into a presence matrix with coordinates (`data/raw/berezkin/`).
- Natural Earth 110m coastlines, public domain.
- G. Strona et al. (2014), "A fast and unbiased procedure to randomize ecological binary
  matrices with fixed row and column totals", *Nature Communications* 5:4114 (curveball).

Code and derived data: MIT. Catalogue-derived data: CC BY-NC-SA 4.0, per the source.
