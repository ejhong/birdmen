# Indus Valley and Rongorongo: A Visual Affinity Worth Testing, Not Yet a Demonstrated Connection

## Executive summary

The circulating de Hevesy/Archaic Lens comparison is **visually provocative but archaeologically under-sourced**. Some of its twenty-four paired forms are genuinely striking to the eye, particularly the anthropomorphic families in the upper two rows. The correct scholarly response is neither “they look alike, therefore they are related” nor “24 out of 500 is only 4.8%, therefore there is nothing here.” Neither is a valid test.

Guillaume de Hevesy proposed an Indus–Rongorongo relationship in the early 1930s and published a substantial comparison in 1933. Alfred Métraux attacked the proposal in 1938, focusing not simply on geographical distance but on **source fidelity, selective comparison, sign variation, cultural discontinuity and the absence of intermediates**; de Hevesy replied in the same year. citeturn26view0turn19view1turn19view0

Modern scholarship makes the old visual charts simultaneously **more testable and less trustworthy as evidence on their own**. Mahadevan's Indus concordance standardized thousands of inscriptions into 417 sign types, while Barthel's classic Rongorongo catalog listed 599 sign shapes—but the latter number contains variants and compounds, and later palaeographic work has repeatedly corrected older hand drawings using photographs and 3D scans. citeturn19view5turn28view2turn19view2

That means David Miano's social-media calculation—roughly “24/500 = 4.8% similarity”—does **not** measure statistical significance. At the same time, Archaic Lens's analogy to discovering the entire English alphabet elsewhere is also misleading: the twenty-four correspondences were selected retrospectively from large inventories, not specified in advance with known sound values and order. With 417 Mahadevan signs and 599 Barthel shapes, there are illustratively about **249,783 possible cross-pairs** before accounting for variants. A method must therefore ask whether the *best* Indus–Rongorongo matches are more extraordinary than the best matches obtainable between unrelated scripts of similar graphical complexity. The catalogue counts themselves are not probabilities. citeturn19view5turn28view2

The most important result of this investigation is a provenance problem: **I could not establish an occurrence-level source trail for the exact twenty-four-pair social-media chart.** It supplies neither Indus artifact numbers nor Rongorongo tablet/line positions. Because the drawings are normalized, it is unsafe to reverse-engineer exact Mahadevan, Parpola or Barthel numbers merely by eye. This does not establish that the glyphs are invented; it establishes that **the chart, as circulated, is not yet auditable evidence**.

That creates an unusually good project for open computational archaeology. The decisive test should authenticate every glyph against photographs or 3D models, preregister similarity metrics, compare the *entire* inventories, down-weight simple geometric shapes, require one-to-one reciprocal matches, generate equally optimized “best 24” charts for many unrelated scripts, and—most importantly—test whether apparent corresponding **families of base signs and modifiers** recur in both systems. Modern Indus computer-vision work and new Rongorongo 3D models show that the technical infrastructure for much of this already exists. citeturn28view3turn19view4turn23view0

My assessment is therefore:

> **There is a legitimate visual hypothesis here. The famous chart does not prove it, and existing dismissals do not statistically disprove it. The right next step is a blinded, corpus-wide, preregistered test.**

## What the historical record actually says

De Hevesy's claim is not a recent “alternative history” invention. His 1933 paper, *Sur une Écriture océanienne paraissant d'origine néolithique*, appeared in the *Bulletin de la Société préhistorique de France* after an earlier 1932 communication concerning the comparison. He explicitly invited objections and presented his proposal as something requiring caution. [The original 1933 paper and its plates are available through Persée.](https://www.persee.fr/doc/bspf_0249-7638_1933_num_30_7_12178) citeturn26view0turn27search6

Métraux, who had conducted field research on Rapa Nui, published *The Proto-Indian Script and the Easter Island Tablets: A Critical Study* in *Anthropos* in 1938. His objection was broader than “they are far apart.” He accepted that some forms looked alike but argued that de Hevesy's copying and selection procedures were unreliable, that Rongorongo had substantial graphical variability, and that the two inscriptional traditions differed radically in medium and textual organization. [Métraux's original article is catalogued by JSTOR.](https://www.jstor.org/stable/41103161) De Hevesy immediately answered with *The Easter Island and the Indus Valley Scripts*, defending his comparison. [That reply is also on JSTOR.](https://www.jstor.org/stable/41104307) citeturn19view1turn19view0

The old dispute contained exactly the problem now visible on X: **what counts as a faithful glyph?** A source-indexed historical summary of Métraux's critique identifies, among other examples, Mohenjo-daro seal **260**—Marshall's plate CX, no. 260—and seal **122**—Marshall's plate CVII, no. 122—as cases where Métraux challenged de Hevesy's rendered form. citeturn28view0 These occurrence IDs are useful leads, but I cannot securely place either one among the twenty-four positions in the cropped Archaic Lens chart; doing so from silhouette alone would reproduce the very methodological error under dispute.

Later corpora transformed the problem. Iravatham Mahadevan's 1977 *The Indus Script: Texts, Concordance and Tables* standardized 2,906 inscribed objects and listed 417 distinct signs. The concordance is now accessible through the [Indus Research Centre's IM77 site](https://indusscript.in/). Asko Parpola and collaborators' *Corpus of Indus Seals and Inscriptions* subsequently provided a much larger photographic reference corpus; the [Interactive Corpus of Indus Texts](https://www.epigraphica.de/indus/menueindus.htm) developed by Bryan Wells and Andreas Fuls provides another searchable sign/text framework. citeturn19view5turn19view6turn19view7

For Rongorongo, Thomas Barthel's 1958 *Grundlagen zur Entzifferung der Osterinselschrift* remains the reference coding system. A recent peer-reviewed reassessment notes that Barthel listed **599 sign shapes**, but warns that this inventory mixes variants and some compounds and therefore is not equivalent to 599 independent graphemes. Albert Davletshin has likewise shown why visually similar designs cannot automatically be assigned the same value and why allograph/variant distinctions need contextual testing. A useful, non-authoritative digital mirror of Barthel material is available at [Kohaumotu](https://kohaumotu.org/Rongorongo/Barthel/index.html). citeturn28view2turn19view2

This matters especially because newer documentation has corrected old tracings. Lastilla, Ravanelli, Valério and Ferrara used photogrammetry and structured-light scanning to revise the Échancrée tablet, explicitly noting disagreements and inaccuracies in earlier normalized drawings. The University of Bologna's INSCRIBE project provides [Rongorongo 3D resources](https://site.unibo.it/inscribe/en/output/3d-models), including Aruku Kurenga and Mamari; the 2024 dating project also produced high-resolution digital models of the four Rome tablets. citeturn28view2turn19view4turn23view0

Recent radiocarbon work changes the chronology but **does not establish an Indus connection**. In 2024, Ferrara and colleagues dated the wood of Tablet D/Échancrée to **1493–1509 cal AD at the reported 68.3% interval**, centuries before European arrival. But Tablet D is made from non-native *Podocarpus* wood, and the authors emphasize wood reuse: radiocarbon dates the timber, not the carving. They explicitly state that the inscription could be younger than the wood. Three other Rome tablets predominantly point toward the eighteenth–nineteenth-century horizon. [The open-access paper includes images, dates and 3D-model references.](https://www.nature.com/articles/s41598-024-53063-7) citeturn23view0

Mainstream opinion remains skeptical of historical transmission, but not every specialist has treated quantitative comparison as meaningless. Parpola rejects a historical connection; Mayank Vahia, while unconvinced by the visual examples, has argued that a defensible comparison would require explicit standards involving stroke distributions, style and statistical structure—and noted that such an analysis had not been undertaken by his group. That is very close to the experiment proposed below. citeturn19view8

## Provenance audit of the circulating twenty-four pairs

The following audit numbers the screenshot **left-to-right: upper row P01–P08, middle row P09–P16, bottom row P17–P24**. “Unsourced/unverified” means exactly that: the circulating chart provides insufficient information to attach the normalized drawing to a unique ancient occurrence. It does **not** mean that no comparable sign exists in the relevant corpus.

This distinction is fundamental. A Mahadevan sign number denotes a normalized type that can occur on multiple artifacts; a Barthel number similarly represents a classified graphical form rather than an automatically unique tablet occurrence. Proper provenance therefore needs both **catalog code and occurrence coordinates**.

| Pair | Form visible in circulating chart | Indus artifact ID | Mahadevan / Parpola | Indus raw image | Rongorongo tablet / Barthel occurrence | Rongorongo raw image / 3D | Drawing-to-original audit |
|---|---|---|---|---|---|---|---|
| P01 | anthropomorph + large side loop | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P02 | angular anthropomorph | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P03 | anthropomorph + spiral/loop | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P04 | anthropomorph + right appendage | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P05 | anthropomorph, raised limb | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P06 | anthropomorph, asymmetric limbs | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P07 | anthropomorph + curved side form | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P08 | anthropomorphic/branching form | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P09 | anthropomorph, arms raised | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P10 | anthropomorph, bent limb | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P11 | anthropomorph + small appendage | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P12 | anthropomorph + multiple strokes | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P13 | anthropomorph + block/loop | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P14 | paired anthropomorphs | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P15 | anthropomorph + head extension | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P16 | anthropomorph + vertical element | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P17 | oval with internal stroke | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable; low complexity |
| P18 | figure-eight | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable; low complexity |
| P19 | U/cup with crossbar | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable; low complexity |
| P20 | circle on stem | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable; low complexity |
| P21 | crescent | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable; low complexity |
| P22 | branched/tree form | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P23 | fork/Y with small elements | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable |
| P24 | U-shaped fork | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | **unsourced/unverified** | Not testable; low complexity |

This apparently disappointing table is in fact the first important finding. **The social-media object is a similarity illustration, not a reproducible dataset.** The old debate already showed why that distinction matters: Métraux challenged particular copies, and modern 3D Rongorongo work has independently demonstrated that established hand transcriptions can require correction. citeturn19view1turn28view0turn28view2

The next provenance task is therefore not to “identify the closest Mahadevan glyph” with AI. It is to reconstruct the genealogy of the chart: locate the exact de Hevesy plate or later reproduction from which each image was copied, recover de Hevesy's own source references to Marshall/Hunter and historical Rongorongo tracings, then cross-walk those references into Mahadevan/CISI and Barthel/modern tablet coordinates. Until that is done, assigning catalog numbers would create false precision.

Useful primary/data portals are [de Hevesy's 1933 Persée article](https://www.persee.fr/doc/bspf_0249-7638_1933_num_30_7_12178), [Mahadevan IM77](https://indusscript.in/), [ICIT](https://www.epigraphica.de/indus/menueindus.htm), [INSCRIBE Rongorongo 3D models](https://site.unibo.it/inscribe/en/output/3d-models), and the [2024 Scientific Reports Rongorongo study](https://www.nature.com/articles/s41598-024-53063-7). A 2025 peer-reviewed Indus computer-vision project has also released an annotated-seal pipeline and dataset through its [project repository](https://github.com/DM-BiCLab/Deep-Learning-in-Archiving-Indus-Script-and-Motif-Information). citeturn19view4turn28view3

## What would count as statistical evidence

The “4.8%” argument fails because it answers the wrong question. Twenty-four divided by an estimated inventory of 500 says what fraction of one inventory someone displayed; it does not tell us the probability of obtaining those similarities by chance. Worse, Barthel's approximately 599 graphic forms and Mahadevan's 417 standardized Indus signs are **not equivalent counting units**: variants, compounds and allographs are classified differently. citeturn28view2turn19view5turn19view2

The opposite argument—“these twenty-four look too close to be coincidence”—also encounters a multiple-search problem. Using the two traditional inventory counts merely as an illustration gives \(417\times599=249,783\) possible pairwise comparisons. These are not statistically independent, but the number shows why looking through two large iconographic repertoires and publishing only the strongest matches can create astonishing panels even under independence.

The appropriate null question is:

> **After giving every control script exactly the same opportunity to find its strongest matches, how exceptional is Indus–Rongorongo?**

A circle matching a circle should receive almost no evidential weight; a complex asymmetric figure sharing the same branches, loops, attachments and internal topology should receive much more. That is **complexity weighting**. Likewise, the algorithm should prohibit repeatedly matching several Indus forms to whichever Rongorongo glyph happens to be most flexible. A maximum-weight **one-to-one matching** and reciprocal-nearest-neighbor test are far harder to game.

The potentially strongest signal in the Archaic Lens image is therefore not P17–P24, despite their superficial near-identity. Those mostly use elementary geometries. More interesting are P01–P16 **if** their apparent correspondences prove genuine, because they look like related anthropomorphic bases carrying systematic modifications. A family-level correspondence such as “base person ↔ base person; same added loop ↔ same added loop; same duplication ↔ same duplication” would preserve relationships among signs rather than merely matching isolated silhouettes.

That gives a crucial distinction:

\[
\text{isolated look-alike} \ll
\text{complex reciprocal match} \ll
\text{preserved modifier system} \ll
\text{visual match + independent contextual behavior}
\]

Davletshin's work on Rongorongo makes the last step particularly important: graphically similar signs may have different textual functions, while differently drawn forms may function as equivalents. Visual affinity must therefore be followed by tests of distribution, substitution, frequency and position. citeturn19view2

## An open AI project that could actually move the debate

A credible volunteer project could reach a first result in roughly **twelve weeks**, provided that image rights and specialist access are resolved. Recent work already demonstrates automated extraction of Indus graphemes from seal imagery, while Rongorongo researchers have demonstrated sub-millimetric 3D documentation and palaeographic revision. citeturn28view3turn23view0

| Period | Work product | Decisive question |
|---|---|---|
| Weeks 1–2 | Historical/provenance audit of every de Hevesy pair | Do the drawings faithfully represent identifiable originals? |
| Weeks 3–4 | Raw-image corpus, masks, occurrence IDs, independent tracings | Are we comparing artifacts rather than normalized cartoons? |
| Week 5 | Frozen preregistration, controls and scoring rules | Can analysis choices no longer move after results are known? |
| Weeks 6–7 | Contour, topology, skeleton and part-based similarity matrices | Does the affinity survive multiple independent metrics? |
| Week 8 | Complexity weighting, reciprocal matches, global one-to-one assignment | Is the complete alignment exceptional? |
| Week 9 | Blind “best 24” tournament against controls | Can unrelated scripts generate equally convincing charts? |
| Week 10 | Base-plus-modifier/compositional-grammar test | Are relationships among sign families preserved? |
| Week 11 | Held-out frequency/position/co-occurrence tests | Does a shape-derived mapping predict anything it was not trained on? |
| Week 12 | Independent replication, red-team report, open release | Does the result survive hostile scrutiny? |

The similarity engine should deliberately combine **interpretable** measures: contour distance; skeleton topology; endpoints, junctions and loops; graph-edit distance; relative part placement; and an explicit morphological representation such as “anthropomorphic base + right-side closed loop.” A learned Siamese/contrastive embedding can be added, but it should be trained only to recognize documented *within-script* variants and frozen before the Indus–Rongorongo comparison. A general multimodal chatbot should not serve as the judge.

The public centerpiece should be a **Blind Best-24 Tournament**. Every control pairing receives the same optimizer and is allowed to publish its twenty-four most impressive correspondences. Labels are removed; rendering is standardized; experts and ordinary observers rank the panels blind. If Egyptian–Rongorongo, Maya–Indus and other unrelated pairings routinely look just as miraculous, the visual argument collapses. If Indus–Rongorongo remains an extreme outlier across algorithms and human judgments, there is then a genuine anomaly to explain.

The project should treat historical transmission as a **second hypothesis**, not bake it into the visual test. Even a p-value of \(10^{-6}\) for graphical affinity would not establish an Indus voyage to Polynesia. Transmission would require an independently plausible chronology and pathway, intermediate forms, archaeological evidence or some other historically diagnostic signal. The 2024 radiocarbon evidence does not supply that bridge because it dates wood, not the invention of Rongorongo or the moment at which Tablet D was carved. citeturn23view0

## Controls, decision rules, and FAQ

The negative controls should include both abstract and highly pictorial systems. Strong candidates are Egyptian hieroglyphs, Anatolian/Luwian hieroglyphs, Cretan Hieroglyphic, Linear A, early Chinese graphs and Maya glyphs. Proto-Elamite is useful as a **stress test rather than a clean independence control**, because its broader ancient Near Eastern context makes historical interaction questions more complicated. Controls should be matched as far as practical for inventory size, pictoriality, complexity and artifact medium.

Positive controls are equally important. The pipeline should be required to detect known or strongly established historical relationships such as **Linear A → Linear B adaptation**, **Phoenician → early Greek**, and successive historical stages of Chinese writing. A similarity metric that cannot recover known script descent should not be trusted when it announces a previously unknown one.

**Does “24 out of 500 = 4.8%” refute the hypothesis?** No. It is a fraction, not a significance test. The relevant statistic is how extreme the optimized corpus-wide affinity is relative to a preregistered null distribution. Catalogue sizes are also classification-dependent. citeturn19view5turn28view2

**Is Miano nevertheless right about hand drawings?** Yes, on this point. A hand-normalized comparative plate is not adequate primary evidence. Modern Rongorongo research has shown empirically that older drawings sometimes need correction after high-resolution and 3D examination. The claim becomes stronger, not weaker, by replacing every drawing with a source-linked artifact crop. citeturn28view2turn23view0

**Should we distrust our eyes?** No. Human vision is excellent at generating hypotheses about form. It is poor at intuitively correcting for the enormous number of comparisons that were available before a striking subset was selected. The right response to “that looks extraordinary” is **measurement**, not dismissal.

**What would make the result genuinely compelling?** Source-authenticated signs; an Indus–Rongorongo score beyond the extreme tail of many matched controls; survival after removing elementary shapes; reciprocal one-to-one matching; preserved base/modifier families; and, ideally, a visual mapping that predicts held-out textual properties. Davletshin's contextual treatment of Rongorongo variants makes this last criterion especially valuable. citeturn19view2

**Would a significant visual result prove transmission?** No. It would establish an anomaly requiring explanation. Convergence, common iconographic constraints, indirect transmission and historical descent would remain competing explanations. Parpola currently rejects the historical connection, while Vahia's response usefully points toward precisely the quantitative testing required to turn the question into science. citeturn19view8

**Does the fifteenth-century radiocarbon result solve the chronology?** No. Tablet D's wood dates to the fifteenth century, but it is non-native wood and may have been reused. The researchers explicitly caution that the carving can postdate the timber. citeturn23view0

The strongest predetermined success criterion would be something like: **Indus–Rongorongo must fall above the 99.9th percentile of matched unrelated systems under several independent metrics; retain the result after simple signs are removed; show an excess of reciprocal high-complexity matches; and preserve significantly more modifier-family relationships than permutation controls.** A contextual prediction would raise the result into a substantially more interesting category. These thresholds should be frozen before the target comparison is unblinded.

## Full preregistration brief and call to action

The following is a copy-ready specification for an open research repository, grant application or adversarial collaboration.

```text
PROJECT TITLE

Indus–Rongorongo Graphic Affinity Challenge

PRIMARY RESEARCH QUESTION

Do the Indus sign system and the Rongorongo sign system exhibit
anomalously high graphical affinity relative to comparable but
historically unrelated sign systems?

SEPARATE THE HYPOTHESES

H1-GRAPHIC
Indus and Rongorongo share more high-information graphical structure
than unrelated sign systems.

H2-HISTORICAL
Any demonstrated graphical affinity resulted from historical
transmission or common descent rather than independent convergence.

Support for H1 must not automatically be treated as support for H2.

NON-NEGOTIABLE RULES

1. Historical de Hevesy comparison drawings are not primary data.
2. The famous proposed pairs may not be used as model-training examples.
3. Similarity metrics, controls and exclusion rules are frozen before
   the target result is calculated.
4. No pair-specific rotation, mirroring, stretching or simplification
   is permitted unless the same transformation is available to every
   control comparison.
5. “Percentage of shared glyphs” is not a significance statistic.
6. Glyph occurrences, catalogue signs, allographs, modifiers, compounds
   and ligatures must be represented separately.
7. Negative results and excluded candidates must be retained and released.

PROVENANCE PHASE

For every historical claimed pair:

- recover the precise publication/page in de Hevesy;
- identify de Hevesy's Indus source;
- identify artifact/site/excavation/catalogue occurrence;
- cross-walk to Mahadevan and CISI/Parpola where possible;
- identify Rongorongo tablet, face, line and glyph position;
- cross-walk to Barthel and later transcriptions;
- obtain highest-quality photograph, impression or 3D rendering;
- record damage, restoration and uncertain strokes;
- record any rotation, reflection or normalization;
- commission two independent tracings made blind to the proposed partner.

Freeze the audit before similarity scoring.

Required outputs:
source_manifest.csv
historical_pair_audit.csv
raw_source_pair_cards.pdf
independent_tracings/
unverified_pairs.csv

CORPUS PHASE

Construct three parallel representations:

A. individual archaeological glyph occurrences;
B. accepted catalogue-level sign types;
C. decomposed base-sign/modifier families.

Where authorities disagree about allographs or compounds, retain all
reasonable classifications and perform sensitivity analyses.

PREREGISTRATION PHASE

Freeze in advance:

- permitted geometric transformations;
- image normalization;
- complexity metric;
- similarity metrics;
- negative and positive controls;
- exclusion rules;
- one-to-one assignment procedure;
- permutation/null procedure;
- multiple-comparison correction;
- primary outcome;
- secondary outcomes;
- success and falsification thresholds.

VISUAL METRICS

Calculate at least four independent representations:

1. contour/distance-transform similarity;
2. skeleton topology and graph-edit similarity;
3. interpretable part-based morphology;
4. learned embedding trained only on within-script variant recognition
   and frozen before cross-script comparison.

Extract endpoints, junctions, loops, enclosed regions, symmetry,
stroke relationships, appendage positions and compositional parts.

Do not use a general-purpose language model's subjective visual judgment
as the primary measurement.

COMPLEXITY WEIGHTING

Estimate the null probability of resemblance conditional on graphical
complexity.

Down-weight circles, crosses, crescents, U-shapes, generic stick figures
and other highly reusable primitives.

Increase evidential weight for rare, asymmetric, multipart and
topologically constrained configurations.

GLOBAL MATCHING

Calculate the complete all-versus-all similarity matrix.

Report:

- nearest-neighbor ranks;
- reciprocal nearest neighbors;
- maximum-weight one-to-one alignment;
- high-complexity matches above preregistered thresholds;
- total complexity-weighted affinity;
- sensitivity to disputed signs;
- empirical permutation probabilities;
- false-discovery-adjusted results.

Never build the statistical conclusion from a hand-selected gallery.

CONTROL PHASE

Include at minimum:

- several known-related script pairs as positive controls;
- twenty or more matched unrelated comparisons;
- pictorial and non-pictorial systems;
- synthetic inventories preserving relevant complexity distributions.

Allow skeptical specialists to nominate at least half the negative
controls before unblinding.

BLIND BEST-24 TOURNAMENT

For every target and control pairing:

- automatically select its best twenty-four one-to-one matches;
- render them in the same neutral format;
- remove script names and geographic information;
- randomize panels;
- obtain rankings from epigraphers and non-expert observers.

Compare human rankings with computational affinity scores.

COMPOSITIONAL-GRAMMAR TEST

Independently infer sign families within each corpus.

Test whether a cross-script mapping preserves transformations such as:

- add loop;
- add/reposition limb;
- add head extension;
- attach object;
- duplicate figure;
- enclose base;
- combine two bases.

Evaluate preservation using graph matching and permutation controls.

Treat this as a primary outcome.

HELD-OUT CONTEXT TEST

Freeze any visual mapping before examining contextual correspondence.

Then test whether mapped forms show above-control agreement in:

- frequency rank;
- line-initial/medial/final distribution;
- adjacent-sign distributions;
- co-occurrence networks;
- repeated groups;
- modifier compatibility;
- structural position.

Never alter the visual mapping after seeing these results.

HISTORICAL PHASE

Only after H1-GRAPHIC has been tested should the project compare:

A. independent convergence;
B. shared pictorial constraints;
C. indirect transmission through intermediate traditions;
D. inheritance from an earlier graphic tradition;
E. direct or near-direct historical contact.

Historical transmission requires evidence independent of visual
resemblance: chronology, intermediary forms, archaeology, population
history, trade/contact evidence or other diagnostic data.

REPRODUCIBILITY

Release, subject to museum rights:

preregistration.md
source_manifest.csv
glyph_occurrence_index.csv
similarity_matrices/
control_results.csv
reciprocal_matches.csv
one_to_one_alignment.csv
modifier_family_graphs/
blind_best24_panels/
blind_ratings.csv
permutation_results.csv
analysis_code/
red_team_report.md
final_report.md

FINAL VERDICTS MUST BE SEPARATE

1. Fidelity of the historical de Hevesy comparison.
2. Existence or absence of a corpus-wide visual anomaly.
3. Evidence for shared compositional grammar.
4. Evidence from held-out textual behavior.
5. Evidence, if any, for a historical transmission pathway.

For every verdict, state in advance what result would count against it.
```

The immediate bottleneck is not more AI—it is **provenance**. The project needs access to the original de Hevesy publications and their source lists, Marshall/Hunter-era Indus plates, Mahadevan/CISI cross-references, Barthel's full catalog, modern Rongorongo photography and 3D data, and specialists capable of adjudicating damaged or compound signs. Modern AI becomes valuable only after that layer is clean. The 2022 Rongorongo 3D work explicitly demonstrates why palaeographic reinspection is necessary, while the 2025 Indus deep-learning project demonstrates that automated glyph extraction and structured archival analysis are already practicable. citeturn28view2turn28view3

A productive collaboration would therefore bring together an Indus epigrapher, a Rongorongo palaeographer or Rapa Nui specialist, a historian able to reconstruct de Hevesy's sources, a computer-vision researcher, a statistician experienced with permutation/null models, and a skeptical red team. Museum and corpus custodians are equally important because image licensing and access to high-resolution originals may determine what can be released openly. citeturn19view7turn23view0

The proposition to fund is deliberately narrower—and more defensible—than “prove Indus people reached Rapa Nui”:

> **For the first time, determine quantitatively whether the famous Indus–Rongorongo visual resemblance survives primary-source authentication, full-corpus comparison, complexity correction, blind controls and compositional-grammar testing.**

That question is falsifiable. It treats the striking visual observation seriously without prejudging its explanation. And whatever the outcome—an exceptional affinity or an equally impressive set of matches generated from unrelated scripts—it would advance the debate far beyond both **“believe your eyes”** and **“4.8%, case closed.”**