## My actual view

**Your eyes are seeing a real visual pattern.** Some pairs in that chart are striking—especially the simpler signs in the bottom row—and the first two rows appear to show recurring correspondences among human-shaped signs and their appendages.

David Miano’s **“24 out of 500 is only 4.8%” is not a valid statistical rebuttal**. It is merely a percentage of one estimated inventory. It tells us nothing about how surprising those 24 correspondences would be under independence.

But there is an equally important qualification:

> **Your eyes establish that the chart contains close-looking pairs. They do not yet establish that the underlying ancient inscriptions contain those same close-looking pairs.**

The chart appears to descend from Guillaume de Hevesy’s 1930s Indus–Rongorongo comparison. Alfred Métraux challenged the comparison in a 1938 critical paper, including the reliability of the reproduced forms; de Hevesy published a reply defending his work. This is therefore an old scholarly controversy, not merely a recent internet meme—but it was conducted without today’s digital imaging, computer vision and rigorous corpus-wide statistics. ([jstor.org][1])

My verdict is:

* **Miano is right** that hand-drawn, selected signs cannot establish the claim.
* **Miano is wrong** that dividing 24 by roughly 500 disposes of the visual evidence.
* **Archaic Lens is right** that the pattern deserves serious measurement.
* **Archaic Lens overstates the result** by comparing it to finding the complete English alphabet. These are selected correspondences, not a predetermined alphabet with known order, sounds and one-to-one identities.

The question can now be tested properly—and AI makes the decisive test unusually feasible.

---

## Why “4.8% similarity” means almost nothing

The number of Rongorongo signs is itself not settled. Barthel’s catalogue had hundreds of numbered positions, but later analyses distinguish among approximately 322 recurring signs, roughly 120 fundamental graphical constituents, and a much smaller proposed inventory of 52 signs accounting for 99.7% of the corpus. The differences arise largely from disagreements about whether two forms are separate signs, variants, components or ligatures. The conventional Mahadevan inventory for the Indus system contains 417 signs, but it has similar sign-versus-variant problems. ([thepolynesiansociety.org][2])

So Miano’s calculation assumes comparable units when the catalogues may be counting very different things.

More fundamentally, suppose there were 417 Indus signs and 500 Rongorongo signs. An investigator searching freely has:

$$
417 \times 500 = 208{,}500
$$

possible cross-script pairings.

As a purely illustrative example, even if an eye-catching resemblance occurred in only **one out of every 10,000 unrelated pairings**, a search through 208,500 combinations would yield about 21 such pairs before accounting for dependencies and one-to-one restrictions.

That does **not** show that the observed pairs are coincidental. It shows why neither intuition nor “24/500” settles the matter. The required quantity is:

> How much better is the best complete Indus–Rongorongo alignment than the best alignments obtained between comparable but historically unrelated sign systems?

That is an empirical question.

Consider two extremes:

* If two 500-sign systems independently contained 24 pre-specified, bizarre, highly complex, twelve-stroke signs with identical internal organization, 4.8% could be overwhelmingly significant.
* If they shared circles, crescents, crosses, U-shapes, stick figures, trees and fish, 4.8% might be completely unsurprising.

**Complexity, selection procedure and the null distribution matter. The percentage does not.**

---

## The most interesting thing in the chart may not be the “identical” signs

The bottom row looks closest to literal identity. But it includes forms like an oval, figure eight, U, circle on a stem, crescent and branching line. Those are low-complexity shapes constructed from a tiny number of graphical primitives. They should receive relatively little evidential weight.

The first two rows may be scientifically more interesting, even though they look less exactly identical.

They seem to contain families built around an anthropomorphic base:

* person with an attached loop;
* person with a particular arm configuration;
* person holding or joined to another form;
* paired figures;
* variations in head, limb or appended-object structure.

There are two very different possible explanations.

### Weak explanation

Both scripts contain many pictorial people, and once dozens of human poses and attached objects exist, matching examples can be found.

### Stronger explanation

Both systems use the **same compositional grammar**: take a corresponding base figure and apply corresponding modifications—add a loop in the same position, raise the same limb, attach a similar object, duplicate the figure, and so on.

That second possibility is far more powerful. It is not merely matching individual nodes. It is matching the **relationships among families of signs**.

In graph terms:

* an isolated look-alike is one matching node;
* a corresponding system of bases and modifiers is an edge-preserving subgraph;
* matching how signs behave in actual inscriptions adds another independent evidential layer.

That should be the centerpiece of the AI investigation.

---

# The decisive AI project

I would call it:

## **Indus–Rongorongo Graphic Affinity Challenge**

The study should explicitly separate two hypotheses:

**H1 — Graphic anomaly:**
Indus and Rongorongo share more high-information graphical structure than comparable unrelated sign systems.

**H2 — Historical relationship:**
Any demonstrated graphical anomaly arose through transmission or common descent rather than convergence.

H1 can be tested without assuming H2. That separation is crucial. Some mainstream reactions appear to reject the visual question because the historical connection has a very low prior probability. Conversely, some proponents treat visual resemblance as if it already establishes historical transmission. Both moves are premature.

---

## 1. Authenticate every claimed pair

This is the indispensable first step.

For each of the 24 displayed pairs, create a source card containing:

* exact Indus artifact or inscription number;
* museum or excavation source;
* Mahadevan, Parpola or other catalogue number;
* photograph or seal impression;
* exact coordinates of the glyph on the artifact;
* exact Rongorongo tablet, face, line and glyph position;
* Barthel or later catalogue code;
* high-resolution photograph or 3D rendering;
* any damage, restoration or uncertain strokes;
* whether the published drawing has been rotated, reflected, simplified or reconstructed.

Use the original artifact imagery—not de Hevesy’s normalized drawings—as the analytical data.

Two independent researchers should trace each glyph without being shown its proposed partner. A third adjudicator resolves disagreements. The proposed pair should only be revealed after the tracings are frozen.

This alone could produce an important result:

* If many pairs cannot be found in the underlying artifacts, Miano’s objection wins.
* If the raw forms survive faithfully, the comparison becomes considerably more serious.

Modern Rongorongo research has produced high-resolution 3D models for several tablets, and the INSCRIBE project provides interactive models, although complete underlying datasets may require permission. Recent work has also developed automated image-processing and archival pipelines for Indus seals. ([site.unibo.it][3])

The decisive record should have one row per claimed pair:

```text
pair_id
indus_artifact_id
indus_sign_code
indus_image_coordinates
rongorongo_tablet
rongorongo_face_line_position
rongorongo_sign_code
orientation_transform
damage_confidence
independent_tracing_agreement
shape_complexity
similarity_scores
reciprocal_rank
control_percentile
family_modifier_match
contextual_match
```

---

## 2. Analyze three different inventory levels

Because “what counts as a sign?” is disputed, the test should be run three ways:

1. **Occurrence level:** every individual carved occurrence.
2. **Catalogue-sign level:** conventional sign types.
3. **Base-plus-modifier level:** basic forms with compounds and ligatures decomposed.

A genuine anomaly should not disappear merely because one reasonable inventory convention changes.

This also prevents misleading counting. Sixteen anthropomorphic pairs may be:

* sixteen independent correspondences;
* sixteen variants of one basic human sign;
* or one shared base sign plus a genuinely corresponding modifier system.

Those possibilities have very different evidential value.

---

## 3. Measure similarity with interpretable methods

Do not ask a general vision-language model, “Do these scripts look related?” That would be almost useless. Such models may have seen the famous chart during training, may focus on line thickness and reproduction style, and may produce persuasive but uncalibrated judgments.

Use several frozen representations:

### Contour similarity

Compare outlines using distance-transform, chamfer or Hausdorff-type measures.

### Skeleton topology

Reduce each sign to a graph and measure:

* number and location of endpoints;
* junctions;
* loops;
* enclosed spaces;
* branch ordering;
* symmetry;
* relative limb and appendage positions.

Graph-based recognition and graph-edit-distance methods have already been applied to petroglyphs and ancient writing, so this is technically realistic. ([ment.org][4])

### Part-based morphology

Represent signs as structured descriptions:

```text
BASE: anthropomorphic
HEAD: circular
LEFT_ARM: raised
RIGHT_ARM: attached-to-loop
LOWER_BODY: bifurcated
APPENDAGE_RIGHT: closed-loop
```

This is essential for testing the possible shared modifier grammar.

### Learned representation

Train a Siamese or contrastive model only on known **within-script variants**—for example, multiple carvings judged to be the same Indus sign or same Rongorongo sign. Freeze it before any cross-script comparison.

The famous 24 pairs must not be used as training examples. Otherwise the model will merely learn the desired conclusion.

---

## 4. Weight matches by information content

A circle matching a circle should count almost nothing. A complex configuration of seven branches, two loops and an asymmetric appended figure should count considerably more.

For every glyph, calculate a complexity measure based on:

* description length;
* number of strokes;
* endpoints and junctions;
* loops;
* asymmetry;
* uncommon spatial relationships;
* rarity of the underlying graphical components across all control systems.

Then estimate a match’s evidential weight as something like:

$$
E_{ij}=-\log P_{0}
\left(
\text{similarity at least this high}
\mid
\text{complexity of }i,j
\right)
$$

In plain language: **How rarely would two signs of this complexity resemble one another this closely among unrelated systems?**

This is the quantity your eyes are intuitively trying to assess.

---

## 5. Require reciprocal and one-to-one matches

Cherry-picking commonly allows one Rongorongo sign to resemble several Indus signs or vice versa. The test should require:

* **reciprocal nearest neighbors:** each sign is among the other’s closest matches;
* a maximum-weight **one-to-one alignment**, computable using the Hungarian algorithm;
* explicit penalties for reusing one base form repeatedly;
* multiple-comparison correction.

The headline result should not be “Here are our favorite 24.” It should be:

> Indus–Rongorongo produced X high-complexity reciprocal matches and a global one-to-one affinity score in the Yth percentile of all control comparisons.

---

## 6. Run the “Blind Best-24 Tournament”

This would be the most persuasive public-facing experiment.

Choose perhaps 20–40 comparison systems matched as closely as possible for pictoriality, inventory size and medium. Include Egyptian hieroglyphs, Luwian hieroglyphs, Maya, early Chinese signs, Proto-Elamite, Linear A, Cypro-Minoan, later symbolic systems and synthetic sign inventories.

For every control pairing, make the algorithm construct its own most impressive 24-pair chart under exactly the same rules.

Then:

1. Render all signs in a uniform neutral style.
2. Conceal all script names.
3. Randomize the panels.
4. Ask both experts and ordinary observers to rank the apparent relatedness.
5. Compare those judgments with the formal similarity scores.

This directly honors your intuition instead of telling you not to trust your eyes.

* If numerous unrelated systems produce equally astonishing charts, the original image loses force.
* If Indus–Rongorongo repeatedly stands out, even after blinding, complexity weighting and one-to-one matching, then critics have a real anomaly to explain.

Also include positive controls—known historically related scripts or stages, such as Phoenician and early Greek, Linear A and Linear B, or stages of Chinese writing. The method should identify known relationships before its verdict on the disputed one is trusted.

---

## 7. Test the possible shared modifier grammar

This may be the strongest analysis of all.

Cluster each script into sign families:

```text
base human
base human + right loop
base human + raised arm
base human + head extension
base human + held object
base human + second figure
```

Then ask:

> Is there a mapping between Indus and Rongorongo base forms under which the same graphical transformations are preserved?

Do this without using the old chart to define the transformations.

A successful result might look like:

```text
Indus base A       ↔ Rongorongo base B
A + right loop     ↔ B + right loop
A + raised arm     ↔ B + raised arm
A + attached object↔ B + attached object
A + duplication    ↔ B + duplication
```

Compare the number of preserved transformations with every negative-control pairing.

This would be much harder to explain through coincidental matching than a collection of isolated circles, crescents and stick figures.

---

## 8. Freeze the visual mapping, then test context

The mapping must first be derived from shape alone. After it is frozen, test information that the visual model never saw:

* frequency rank;
* initial, medial and final position;
* neighboring signs;
* repeated sign groups;
* bigram and co-occurrence networks;
* which modifiers combine with which bases;
* whether mapped signs occupy comparable structural roles.

The Indus corpus is known to exhibit nonrandom positional and sequential structure, and Rongorongo graphic analysis likewise relies heavily on parallel passages, recurring groups and contextual substitutions. ([arxiv.org][5])

The two systems need not have identical syntax or language. But if a mapping selected purely from shapes also predicts sign behavior better than control mappings, that would be a major independent result.

This is the equivalent of saying:

> “We did not merely find letters that look alike. The mapped forms also behave alike.”

That begins to approach historically meaningful evidence.

---

## 9. Only then investigate transmission

Even a powerful graphic anomaly would not prove that Indus writing travelled directly to Rapa Nui.

The surviving Indus inscriptions are Bronze Age; Rongorongo is vastly later. A 2024 study dated the wood of one tablet to approximately the late fifteenth or early sixteenth century, but explicitly warned that reused or old wood can predate its inscription. Three other sampled tablets fell mainly into much later ranges. Rongorongo’s precise inception therefore remains unresolved, but there is no presently documented continuous bridge back to the Indus period. ([Nature][6])

If the graphical test succeeds, the next study should search for intermediate transformations through:

* post-Indus South Asian marks;
* Southeast Asian and Austronesian graphic traditions;
* early Pacific symbolic systems;
* Polynesian petroglyphs;
* Rapa Nui rock art predating or associated with Rongorongo.

A historical relationship would become much more persuasive if the forms changed incrementally along a plausible chronological and geographic pathway.

Without intermediates, the proper conclusion might be:

> “The affinity is statistically anomalous, but its cause remains unresolved.”

That alone would still be an important result.

---

# What would genuinely compel me

I would regard the finding as a **serious graphical anomaly** if all of these occurred:

1. Most of the best pairs survive comparison with raw artifact photographs or 3D models.
2. Indus–Rongorongo ranks above at least 99.9% of matched negative controls under several independent similarity measures.
3. The result survives removing circles, crescents, U-shapes, stick figures and other low-complexity signs.
4. A substantial number of matches are reciprocal nearest neighbors.
5. The result survives all reasonable definitions of sign versus allograph versus compound.
6. The base-plus-modifier family structure maps significantly better than controls.
7. A mapping frozen from shape predicts some held-out positional or co-occurrence behavior.
8. Independent teams reproduce the result from the raw sources.

That would not yet prove a migration from the Indus Valley to Rapa Nui. But it would absolutely defeat the claim that the comparison can be dismissed with “4.8%.”

Conversely, the claim would be weakened if:

* the old drawings diverge substantially from their originals;
* most close pairs are simple geometric or obvious pictorial forms;
* the anthropomorphic matches reduce to one generic body template;
* unrelated scripts readily generate equally impressive “best 24” charts;
* or the mapping carries no information about sign families or textual behavior.

---

# Copy-paste AI research brief

```text
Act as a computational epigrapher, computer-vision researcher,
adversarial statistician, and archaeological source auditor.

RESEARCH QUESTION

Do the Indus sign system and the Rongorongo sign system exhibit
anomalously high graphical affinity relative to comparable but
historically unrelated sign systems?

Separate two hypotheses throughout:

H1-GRAPHIC:
Indus and Rongorongo share more high-information graphical
structure than unrelated sign systems.

H2-HISTORICAL:
Any demonstrated graphical affinity resulted from historical
transmission or common descent rather than convergence.

Do not infer H2 merely from support for H1.

NON-NEGOTIABLE RULES

1. Do not treat the historical de Hevesy comparison drawings as
   primary data.
2. Do not use the famous proposed pairs as model-training data.
3. Do not select similarity metrics after examining the target result.
4. Do not permit pair-specific rotation, mirroring, stretching or
   simplification.
5. Do not report “percentage of shared glyphs” as statistical
   significance.
6. Distinguish glyph occurrences, catalogue signs, basic signs,
   allographs, modifiers, compounds and ligatures.
7. Publish negative results and all excluded examples.

PHASE 1 — PROVENANCE AUDIT

For every sign pair in the historical comparison:

- locate the exact Indus artifact and catalogue number;
- locate the exact Rongorongo tablet, face, line and glyph position;
- obtain the highest-quality available source image or 3D rendering;
- record museum, publication, object number and image coordinates;
- document damage, restoration and uncertain strokes;
- document every rotation, reflection or normalization;
- have two independent researchers trace the signs while blind to
  their proposed partners;
- compare the historical drawing with the independent tracings.

Produce:

source_manifest.csv
historical_pair_audit.csv
raw_source_pair_cards.pdf
independent_tracings/
excluded_or_unverified_pairs.csv

PHASE 2 — CORPUS CONSTRUCTION

Construct three parallel datasets:

A. all individual glyph occurrences;
B. accepted catalogue sign types;
C. decomposed base-sign and modifier families.

Where catalogues disagree, preserve all reasonable classifications
and run sensitivity analyses rather than selecting the classification
that produces the preferred result.

PHASE 3 — PREREGISTRATION

Before calculating the Indus–Rongorongo target score, freeze:

- permitted transformations;
- normalization procedures;
- sign-complexity measure;
- similarity metrics;
- control corpora;
- exclusion rules;
- one-to-one matching method;
- multiple-comparison correction;
- decisive thresholds;
- primary and secondary outcomes.

Hide script labels from the main analysis team where practical.

PHASE 4 — VISUAL REPRESENTATIONS

Calculate at least four independent similarity measures:

1. contour or distance-transform similarity;
2. skeleton topology and graph-edit distance;
3. interpretable part-based morphology;
4. a learned embedding trained only on within-script allograph or
   same-sign recognition, then frozen before cross-script testing.

Measure endpoints, junctions, loops, enclosed regions, symmetry,
stroke relationships, appendage position and compositional parts.

Do not rely on a general-purpose multimodal language model's
subjective similarity judgment.

PHASE 5 — COMPLEXITY WEIGHTING

Estimate the null probability of each similarity conditional on sign
complexity. Downweight circles, crosses, crescents, U-shapes, simple
stick figures and obvious depictions of universal objects.

Give greater weight to rare, multi-part, asymmetric and topologically
specific correspondences.

PHASE 6 — GLOBAL MATCHING

Calculate the complete all-versus-all similarity matrix.

Report:

- reciprocal nearest-neighbor matches;
- maximum-weight one-to-one matching;
- number of matches above frozen thresholds;
- complexity-weighted total affinity;
- uncertainty from damaged or disputed signs;
- empirical p-values and effect sizes;
- false-discovery-rate-adjusted results.

Do not construct the conclusion from a hand-selected gallery.

PHASE 7 — CONTROLS

Include:

- known related script pairs as positive controls;
- at least 20 matched unrelated sign-system pairs;
- pictorial as well as abstract controls;
- synthetic sign systems preserving each corpus's stroke count,
  complexity, part inventory and frequency distribution.

Allow a skeptical collaborator to nominate at least half of the
negative controls before unblinding.

For every control pair, automatically create its strongest 24-pair
visual comparison using the same procedure used for the target.

Conduct a blinded human-ranking experiment in which neither expert
nor non-expert judges know which chart is Indus–Rongorongo.

PHASE 8 — COMPOSITIONAL GRAMMAR

Independently infer base signs and graphical transformations within
each corpus.

Test whether a cross-script mapping preserves transformations such
as:

- add a loop;
- add or reposition an arm;
- add a head extension;
- attach an object;
- duplicate a figure;
- enclose a base;
- combine two bases.

Quantify preserved base-modifier relationships using graph matching.
Compare the result against every control pair and a permutation null.

This is a primary outcome, not an anecdotal supplement.

PHASE 9 — HELD-OUT CONTEXT TEST

Freeze the cross-script mapping using visual information only.

Then test whether mapped signs show above-control agreement in:

- frequency rank;
- initial, medial and final position;
- adjacent-sign distributions;
- co-occurrence networks;
- repeated groups;
- modifier compatibility;
- structural role.

Do not modify the visual mapping after seeing contextual results.

PHASE 10 — HISTORICAL ASSESSMENT

Only if H1-GRAPHIC survives the full test, evaluate competing causes:

A. independent convergence;
B. common pictographic constraints;
C. indirect transmission through intermediate traditions;
D. inheritance from an earlier common graphic tradition;
E. direct or near-direct historical contact.

Search for geographically and chronologically intermediate sign
traditions and require gradual, source-verifiable transformations.

DELIVERABLES

preregistration.md
source_manifest.csv
full_glyph_corpus/
similarity_matrices/
control_script_results.csv
reciprocal_matches.csv
one_to_one_alignment.csv
modifier_family_graphs/
blind_best_24_panels.pdf
human_blind_ratings.csv
permutation_results.csv
reproducible_code/
red_team_report.md
final_report.md

The final report must issue separate verdicts on:

1. fidelity of the historical chart;
2. existence of a corpus-wide visual anomaly;
3. evidence for a shared compositional grammar;
4. evidence from held-out sign behavior;
5. evidence for any historical transmission pathway.

State clearly what evidence would falsify each conclusion.
```

---

## The strongest way to approach Miano

I would not tell him that he is blind. I would make the methodological point he cannot reasonably dispute:

> “I agree that selected hand drawings are not enough. But 24 divided by an estimated inventory size is not a significance test. The relevant question is whether a source-verified, complexity-weighted, one-to-one Indus–Rongorongo alignment is an outlier relative to matched unrelated scripts. Would you help choose the negative controls and preregister what result would change your mind?”

That turns a social-media disagreement into an adversarial collaboration.

## Bottom line

**Do not abandon what your eyes noticed. Discipline it.**

The chart is visually provocative. Miano has not statistically explained it away. But the chart’s advocates have not yet demonstrated that its resemblance survives raw-source verification, full-corpus comparison and selection correction.

The most compelling contribution would not be a more dramatic collage. It would be:

1. authenticated raw-source glyph cards;
2. a blinded “best 24” tournament against dozens of controls;
3. a complexity-weighted one-to-one corpus score;
4. and, above all, a test for shared base-plus-modifier grammar.

If Indus–Rongorongo remains exceptional after that, the debate changes fundamentally. Critics could still dispute the historical explanation, but they could no longer reasonably dismiss the underlying anomaly with **“4.8%.”**

[1]: https://www.jstor.org/stable/41103161 "https://www.jstor.org/stable/41103161"
[2]: https://thepolynesiansociety.org/index.php/JPS/article/download/249/226/918 "https://thepolynesiansociety.org/index.php/JPS/article/download/249/226/918"
[3]: https://site.unibo.it/inscribe/en/output/3d-models?utm_source=chatgpt.com "3D Models — INSCRIBE"
[4]: https://ment.org/VISART14/proof.pdf?utm_source=chatgpt.com "Graph-based Shape Similarity of Petroglyphs"
[5]: https://arxiv.org/abs/0901.3017?utm_source=chatgpt.com "Statistical analysis of the Indus script using $n$-grams"
[6]: https://www.nature.com/articles/s41598-024-53063-7 "The invention of writing on Rapa Nui (Easter Island). New radiocarbon dates on the Rongorongo script | Scientific Reports"

