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

## Pilot B (added 4 September 2026, after pilot A's failure; fixed before any judgment was read)

Pilot A's feature coding could not be made reliable, and the neighbours it produced were not similar to the eye. Pilot B measures similarity directly:

- **Judgment.** Two panels are composited side by side, labelled A and B in random order, no captions, names or places. A vision model returns a score 0–10 on a fixed rubric (shared elements; element specificity 0–3; relationships 0–3; arrangement 0–3; style of depiction 0–3; gestalt 0–3; overall 0–10) and a two-sentence justification. The judge is told explicitly that it is comparing what is depicted (the iconography: kinds of elements, their specific forms, combination and arrangement) and not the medium, material, preservation or the photographs themselves.
- **Judges.** Claude Opus 5 (primary), Claude Sonnet 5, GPT-5.5.
- **Target images.** Pillar 43 from the excavators' photographs of the whole pillar (headless man included), and separately from the top-only Commons photograph pilot A used, to measure that error. The moai's back from the British Museum full-back photograph and from a closer view.
- **Sets.** Target pair: every judge, every image pairing, both orders. Null: 1,500 random pairs of panels from different traditions (Opus) plus 500 (GPT-5.5). Same-tradition: 200 random pairs (Opus). Positive control: 150 Assyria × Persepolis pairs (Opus). Searches: Pillar 43 and the moai's back against every other panel (Opus and GPT-5.5). Reliability: 200 null pairs re-judged by Sonnet and by GPT-5.5.
- **Statistics.** The target pair's mean score per judge; its percentile within that judge's null; comparison with same-tradition and positive-control distributions; the number of foreign panels each judge scores above the moai as a match for Pillar 43, and above Pillar 43 as a match for the moai; inter-judge Spearman correlation on shared pairs.
- **Predictions.** The pair scores above the foreign-pair median (the shared "birds above, band, figures below" scheme is real) but below the 95th percentile; several foreign panels outscore the moai as Pillar 43's match; the top-only pillar image scores higher than the whole pillar (the top register is where the resemblance lives). **What would count against the null:** the pair at or above the 95th percentile of the foreign null under two judges, with fewer than five foreign panels outscoring the moai in Pillar 43's search.

## Pilot C: blind lineups (added 4 September 2026, fixed before any lineup was judged)

Following the design used by social-rv.com for remote-viewing sessions: a judge sees one target panel and ten numbered candidates and ranks all ten by similarity to the target. One candidate is planted; nine are random decoys from other traditions. The planted candidate's rank (chance 5.5; rank 1 with probability 0.1) measures whether it stands out.

- Sets: moai's back planted among nine foreign decoys with Pillar 43 as target (40 trials); Pillar 43 planted with the moai as target (40); a hard lineup where the nine decoys are Opus's best matches for Pillar 43 (10); a related-tradition control, a random Assyrian panel planted with a random Persepolis panel as target (40); a same-tradition control (40).
- Judges: Claude Opus 5, GPT-5.5, Gemini 3.1 Pro on every trial; Claude Sonnet 5 and Grok 4.6 on the first twelve trials of each set.
- Statistics: mean planted rank and share of rank-1 per set and judge, with a binomial test against chance; the target sets compared with the two controls.
- Predictions: the moai ranks above chance for Pillar 43 (the shared top-register scheme is visible) but below the same-tradition and related-tradition controls; in the hard lineup the moai does not rank first for most judges. What would count against the null: the moai ranks first in more than half of trials for at least two judges, and above the related-tradition control.

## Change log

- 4 Sept 2026, after coding and analysis (post hoc, reported separately as exploratory): only six features reached alpha ≥ 0.67 and the pre-registered distance could not be computed (it requires at least six agreeing features per pair). Two exploratory variants were then run and are labelled as such on the results page: (a) alpha ≥ 0.5 with each coder's mismatch averaged instead of requiring consensus; (b) the same, with shared absences ignored (Jaccard-style), because the first variant made sparsely coded panels everyone's nearest neighbour. Neither variant changes any pre-registered threshold or prediction.
- 4 Sept 2026, before batch coding, after a three-image dry run: the triage rule now excludes freestanding statues that simply are a figure (a moai seen from the front, a statuette) unless their surface carries separate imagery. The dry run had passed them as "statue surface", which would have added trivially coded single-figure objects to every sculptural tradition.
- 4 Sept 2026, during the pilot B/C runs (before any result was analysed): the prompts for both pilots were rewritten to say explicitly that the judges are comparing what is depicted, not the medium, material, state of preservation or the photographs (lighting, angle, crop, resolution). The first prompts asked for "the manner of rendering" as one criterion and had a style sub-score (0–3); that invited matching on medium and photo quality, which is not the question. The style sub-score was kept but redefined as the manner of depiction (schematic or naturalistic, proportions, outline and infill conventions), explicitly not medium or photograph; sub-scores for element specificity and for relationships between elements (what holds, touches, faces or encloses what) were added. Everything already judged under the first prompt (about 1,270 pair judgments and 64 lineups, not analysed) was set aside in `judgments_v1` / `lineups_v1` and every set was re-run from scratch under the new prompt. No prediction or threshold changed.
- 4 Sept 2026, twenty minutes into the re-run (target set and part of the Pillar 43 search judged, not analysed): one further sentence added to both prompts stating the standard of evidence: is the correspondence of the kind that would suggest a shared iconographic tradition, as opposed to what two unrelated traditions could easily produce independently; arbitrary, specific, conventional correspondences score high, universal or obvious ones low. The judges are still not told the purpose of the study, any hypothesis, or any culture. Both runs were restarted from scratch again.
- 4 Sept 2026, after the Pillar 43 search under the final prompt and before any lineup of the hard set was judged: the hard lineup's decoys are Opus's nine best matches for Pillar 43 *from other traditions* (the nine best overall were all other Göbekli Tepe photographs, several of Pillar 43 itself, which would test nothing).
- 4 Sept 2026, after reading the judges' reasons in the first target lineups (interim results seen: moai picked first for Pillar 43 in 27% of lineups, Pillar 43 picked first for the moai in 66%; controls 53% and 75%): the judges' stated reason was most often that both are "a free-standing monolith whose body is itself a figure" rather than a picture on a wall or rock, and nearly every decoy is a wall relief, rock panel or drawing. That is an object-type confound, not depicted content. Two additions, fixed before any of the new trials was judged: (1) every panel is classified blind by object type (free-standing monolith, statue, wall or architectural relief, rock surface, portable object, drawing) by Claude Sonnet 5, and new lineup sets draw all nine decoys from free-standing monoliths and statues, with a same-tradition control drawn the same way; (2) because the moai photograph shows a museum display piece behind the statue and the pillar photograph shows sky, wall and a neighbouring pillar, both targets are also used in an isolated form with the background removed (GrabCut, then hand-cleaned; the carved surfaces are untouched), with a set that uses the isolated targets among random decoys to separate the background effect from the object-type effect. The same isolated pair is judged directly by the three pilot B judges. Predictions unchanged; the object-type-matched sets are now the primary lineup test.
- 4 Sept 2026, during the second lineup round: the Gemini key exhausted its quota (HTTP 429) and the xAI account ran out of credit (HTTP 403) part-way through the object-type-matched sets, so Gemini and Grok cover only part of those sets (their n is shown in every table). Opus, GPT-5.5 and Sonnet completed every set. Failed calls were discarded, not counted.
- 4 Sept 2026, end of the pilot B run: the OpenAI account ran out of credit before GPT-5.5's 200 reliability re-judgments and its 500-pair null were run (a handful had been judged; failed calls were discarded). GPT-5.5's target judgments and both full-corpus searches are complete, so its agreement with Opus is measured on the 447 Pillar 43 search pairs instead of the 200 null pairs; its own null percentile is not reported.
