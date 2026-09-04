# Study 3 — Pre-registration: the composition of carved and painted panels

*Written 4 September 2026, before any image was coded. Changes after this date are logged at the end.*

## Question

Is the compositional similarity between Göbekli Tepe Pillar 43 and the carved back of Hoa Hakananai'a (Rapa Nui) greater than the similarity that decorated panels from unrelated traditions ordinarily reach with their best match in a foreign tradition? Secondarily: does compositional similarity across the corpus decay with geographic distance, and do known-related traditions come out as nearest neighbours (positive controls)?

## Sample (pilot)

Images are drawn from Wikimedia Commons categories, chosen before coding, listed in `pipeline/s3_corpus.py`. Every file in a listed category is fetched; a triage pass keeps only images that show a single decorated surface (relief, incised or pecked petroglyph, painting, carved panel) clearly enough to code. The triage coder does not see the category name.

| Group | Role | Commons categories |
|---|---|---|
| Göbekli Tepe, Karahan Tepe, Nevalı Çori | target A (Anatolian PPN) | site categories and their building/finds subcategories |
| Çatalhöyük | Anatolian Neolithic control, expected near target A | Çatalhöyük and findings |
| Rapa Nui | target B | Petroglyphs in Orongo area; Hoa Hakananai'a; Moai tangata manu; historical drawings of Orongo |
| Assyrian (Nimrud) | control; positive-control pair with Persepolis | Ashurnasirpal II reliefs |
| Achaemenid (Persepolis) | control; positive-control pair with Assyrian | Apadana stairs; delegation reliefs |
| Egypt | control | Boundary Steles of Akhenaten; Ancient Egyptian stelae (Vatican) |
| Maya | control | Maya stelae and subcategories |
| Mississippian | control (independent birdman tradition) | Mississippian avian themed artwork; Mississippian iconography |
| Gotland picture stones | control | Picture stones of Gotland |
| Tanum rock carvings | control | Rock carvings in Tanum |

Target size: up to 60 usable images per group after triage. Several photographs of the same object are allowed in the pilot but the object identifier is recorded so that analyses can be run per object.

## Coding

Two vision models (Claude Opus 5 and Claude Sonnet 5) code every image independently, with the same instructions, given only the image and the feature list: no file name, no category, no caption. Output is a fixed JSON schema. Features:

- `registers`: number of horizontal bands of imagery (1, 2, 3+).
- For each class {bird, human, bird_human_hybrid, other_hybrid, quadruped, reptile_or_snake, fish, insect_or_arachnid, disc_or_circle, container_or_bag, weapon_or_staff, plant_or_tree, geometric_band, text_or_glyphs}: present (yes/no) and, if present, vertical position of its topmost instance (top / middle / bottom third).
- `facing_pair`: two figures of the same class facing each other.
- `bilateral_symmetry`: the composition is roughly mirror-symmetric.
- `dominant_figure`: the single largest figure's class.
- `headless_human`: a human figure shown without a head.
- `bird_posture`: profile / spread wings / frontal / none.
- `hybrid_type`: bird-headed human / bird with human limbs / human in bird costume / none.
- `medium`: relief / painting / petroglyph / incised / statue surface / unclear.
- `confidence`: coder's own 1–5.

Reliability: per feature, Krippendorff's alpha (nominal) between the two coders across all images. Features below 0.67 are dropped before analysis. A human-coded subset (the author) is added if available and reported separately.

## Distance

Two panels' distance is the mean over retained features of a per-feature mismatch (0/1 for nominal, |Δ|/2 for the three-level position), computed on the consensus code (features where the two coders agree; disagreements are treated as missing for that feature).

## Analyses

1. **Nearest foreign neighbour.** For every panel, its smallest distance to any panel in a different group. The distribution of these minima is the null. Report where the Pillar 43 – Hoa Hakananai'a (back) distance falls in it (percentile), and where each of the two panels' own nearest foreign neighbours are.
2. **Group-level similarity.** Mean cross-group distance for every pair of groups; hierarchical clustering of groups.
3. **Positive controls.** Assyrian ↔ Persepolis, and Anatolian PPN ↔ Çatalhöyük, must be among each other's two closest groups; otherwise the method is not trusted and the target result is reported as uninformative.
4. **Distance decay.** Mantel correlation between group-pair composition distance and great-circle distance between the groups' sites, with the Anatolian trio treated as one location.
5. **Feature drivers.** For the target pair, which retained features match and which do not; matches on features with base rate above 50% across the corpus ("birds up, snakes down") are reported separately from matches on rarer features.

## Predictions

- At least half of the correspondences visible on the circulating poster do not exist on the real objects (already established in the fidelity figure).
- Pillar 43's nearest foreign neighbour is not in the Rapa Nui group.
- The Pillar 43 – Hoa Hakananai'a distance lies inside the central 90% of the nearest-foreign-neighbour distribution.
- The positive controls pass.
- Composition distance increases with geographic distance (positive Mantel correlation).

**What would count against the null:** the target pair in the closest 5% of nearest-foreign-neighbour distances, driven by features with corpus base rate below 25%.

## Known limitations of the pilot

Commons coverage is uneven; Orongo's petroglyph corpus is far larger than what is photographed there; several images may show the same object; vision-model coding of eroded surfaces is noisy, which is what the reliability threshold is for. The pilot exists to measure that noise before a full corpus is assembled.

## Change log

- 4 Sept 2026, after coding and analysis (post hoc, reported separately as exploratory): only six features reached alpha ≥ 0.67 and the pre-registered distance could not be computed (it requires at least six agreeing features per pair). Two exploratory variants were then run and are labelled as such on the results page: (a) alpha ≥ 0.5 with each coder's mismatch averaged instead of requiring consensus; (b) the same, with shared absences ignored (Jaccard-style), because the first variant made sparsely coded panels everyone's nearest neighbour. Neither variant changes any pre-registered threshold or prediction.
- 4 Sept 2026, before batch coding, after a three-image dry run: the triage rule now excludes freestanding statues that simply are a figure (a moai seen from the front, a statuette) unless their surface carries separate imagery. The dry run had passed them as "statue surface", which would have added trivially coded single-figure objects to every sculptural tradition.
