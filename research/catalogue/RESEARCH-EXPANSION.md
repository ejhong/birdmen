# A broader atlas, with a clearer research path

Assessment and proposed next phase, 20 September 2026. Audited site/data revision:
`ed8211aaff787446d72a3aad036e561052780d82`.

This is a plan, not a completed expansion or a new archaeological finding.
The next priority should be broad source research and a coherent comparison
interface. The motif-first foundation is appropriate; coverage and consistency
need substantial work before the site can fulfil its ambition.

## What the audit found

| Measure | Current position | Implication |
| --- | --- | --- |
| Motif families | 19 | A useful beginning, not a worldwide inventory. |
| Families with at most one cultural context | 7, including 3 with no registered observations | Some family pages are still research leads rather than developed cross-cultural comparisons. |
| Observations | 51; 17 belong to bird figures | The central case has received much more attention than most of the collection. |
| Evidence entities | 43, including 22 objects; other records include surfaces, accounts and corpora | Neither entity nor observation counts measure independent artefacts or confirmed anomalies. |
| Cultural/context groups | 24 | Geographic breadth does not establish coverage within each tradition. |
| Comparison threads | 20, plus 4 optional controls | Threads should remain an interpretation layer over the observations. |
| Supplied-material leads | 22: 19 unresolved, 3 corrected | Preserving a lead is the start of its investigation. |
| Supplied files | All 68 accounted for | File coverage includes duplicates, context and unidentified montage panels; it does not mean every comparison has been verified. |

The seven thin families are paired flankers, animal-on-human compositions,
enclosing creatures, neck lines, T-shaped figures, body signs and birthing figures.
Most other families have only two to four observations. The separate 22-object
visual study adds useful views and local examples, but does not solve broad coverage.

There are also concrete structural gaps:

- `docs/catalogue.js` supplies comparison threads to the map, timeline and culture
  views, while the family view uses attestations. For example, selecting Late
  Egyptian material finds a bird family but no comparison threads; the three new
  Thoth records consequently have no route into those other views. Their unknown
  locations should remain explicit, while their recorded dates remain usable.
- The filter model has broad motif tags but no selected family/configuration.
  A reader cannot carry one precise comparison set through every view.
- `pipeline/family_pages.py::validate_coverage` requires every lead to reference
  preserved files in `inputs/`. A source discovered in a book or on the web needs
  its own intake route, without manufacturing a supplied-file history.
- An attestation records a feature list and one overall status. The newer visual
  study already needs finer distinctions for individual features and views.
- Several claim origins point to our own essays or intake records. These are
  useful editorial destinations, but do not identify the external proposer.
  A single origin field also cannot represent several versions of a comparison.
- Catalogue and visual-study records partly duplicate object information. Shared
  identities should connect them while study selections and annotations stay explicit.

## Keep the structure; make the evidence more precise

The reader should move through **motif family → particular arrangement → cultural
contexts → dated examples**, with attributed proposals available at every level.
These are linked collections, not a rigid tree: an object can illustrate several
motifs, and a comparison can involve any number of traditions.

| Layer | Proposed role |
| --- | --- |
| Family | A broad question, such as bird–human imagery, across all represented traditions. |
| Configuration | A defined arrangement or feature combination. A bird near a round form, a limb touching it and paired bird figures are different observations. |
| Cultural context | Qualified tradition, period and region; allow disputed or multiple attributions without merging neighbouring peoples. |
| Object, surface and episode | Stable physical identity, the exact scene, and the carving/production/recording episode being compared. Date episodes should have stable IDs. |
| Observation | A feature or relationship within that scope, its supporting views/passages, uncertainty, source, reviewer and review date. |
| Proposal | Who connected which examples, where, which features they claimed, why they considered it anomalous, and their proposed explanation. Preserve multiple proponents and revisions. |
| Lead | A sourced candidate awaiting identification or review. Its origin may be a URL, book page, video timestamp or supplied file. |
| Source coverage | Which source portions were examined, the claims extracted, duplicates linked and remaining work. |

Separate feature states such as observed, uncertain, obscured, unreviewed and
explicitly assessed as absent. A missing annotation remains unrecorded. Preserve
disagreement between readings; a source-informed AI annotation is not independent
ground truth. Never combine features on different objects into one attested scene.

Keep identity, image fidelity, dating, interpretation and transmission assessment
as separate review questions. Use clear evidence labels rather than one mystery
score. A case may remain interesting after one proposed explanation is weakened.

Use one selected evidence set for the gallery, map, timeline and feature matrix.
Dates must follow the compared episode, including later additions to older objects.
Keep unknown dates/locations in an accessible list. Culture-to-culture connections
should open their underlying examples; shared-family counts describe the collection,
not the probability of contact. Claims and documented transmission are distinct
optional overlays. Preserve shareable selections and existing dossier URLs.

Keep the native static site and JSON registers unless scale demonstrates a need
for a database. This is a data and reading-flow improvement, not a framework rewrite.

## A systematic research pass

Define comprehensiveness against a published, expanding source inventory. Begin
with the material already cited and supplied, then add declared batches of books,
articles, talks and public comparisons. Record the edition and pages or timestamps
actually reviewed. An inaccessible book or an abstract-only review stays partial.

For each distinct comparison:

1. Preserve the proposing source, exact locator, examples and strongest specific
   version of its claim. Link repetitions to their source history.
2. Resolve object identities, original imagery, scene boundaries and dated episodes
   against collection records, excavation publications or primary textual witnesses.
3. Add authentic photographs with rights and credits, including wider views and
   alternate angles where a crop changes the interpretation.
4. Record local readings and relevant scholarship, including living communities'
   knowledge. Separate what is visible from what the symbols are taken to mean.
5. Compare the feature arrangement, differences, chronology and proposed routes.
   Preserve unresolved and corrected cases with the reason for their status.
6. State the next observation or source that could materially change the assessment.

AI can accelerate extraction, duplicate detection, source discovery and candidate
image matching. Factual promotions need supporting evidence. New user submissions
and delegated image searches should use this same intake path, then attach verified
examples to existing families or propose a new configuration.

Balance the source inventory by subject and geography. Include Hancock's own
arguments, Fenton's claims, other proposers and the scholarship relevant to their
examples. Guest articles retain their actual authors. Authors receive credit with
their claims; the main browsing structure follows the evidence.

A first expansion should develop six to eight illustrated cross-cultural dossiers
and clear the most tractable supplied-image leads. Priorities include staff/animal
holders, paired figures, creatures surrounding or above people, torso gestures,
handled forms, serpent configurations and specific architectural comparisons.
Retain narrative and sign comparisons, with passage- and sequence-level evidence
appropriate to their medium. Select dossiers for traceable material and precise
questions; do not impose an arbitrary artefact quota on thin evidence.

Two concrete source opportunities emerged in this audit:

- Richard Cassaro's [2019 guest article](https://grahamhancock.com/cassaror4/) is
  presently linked to the stepped-monument thread. Its proposed corbelled-vault,
  captive-grasping and back-to-back feline comparisons warrant separate intake and
  verification. The article establishes what Cassaro proposed; object identities,
  cultural labels and historical interpretations require independent checking.
- The DAI published Dietrich and Schmidt's [systematic pillar-imagery volume](https://publications.dainst.org/books/dai/catalog/book/2140)
  in January 2026. Its publisher describes a re-examination of carvings uncovered
  in 1995–2023, including revised identifications and quantitative assessment. This
  could improve the Anatolian baseline substantially. Only the publisher's synopsis
  and contents were inspected here: print is listed, while the PDF is scheduled for
  July 2027. Seek library/print access before treating its contents as reviewed.

Publish a compact coverage view by family, region and source: examined, partial,
awaiting access or unreviewed. A declared source batch is complete when each distinct
comparison in the reviewed portion has a record, a duplicate link or an explicit
unresolved destination. The number of beautiful cards alone cannot show completeness.

## Put the comparisons in front of the reader

Keep the existing calm typography, colours and authentic imagery. Improve hierarchy
and image variety before adding visual decoration.

- **Home:** a short statement of the question, a compelling visual tour of several
  distinct clusters, and clear entrances to the collection and submerged landscapes.
  Introduce what research can resolve with concrete examples.
- **Collection:** begin family pages with a cross-cultural image overview and date
  bands. Readers should see the relationship before scrolling through individual
  records. Offer synchronized gallery, map, timeline and feature views, with sources
  and detailed reviews available on demand.
- **Investigations:** organize work around questions and current findings. Give the
  pillar–moai–boulder investigation one clear home linking evidence, local chronology,
  visual study, experiments and revisions. Preserve older experiment URLs and results.
- **Submerged landscapes:** retain an equally prominent, distinct research strand:
  reconstructed landscapes, discoveries, available datasets and tractable studies.
  Missing coastal evidence is a research opportunity, not an established explanation
  for a motif connection.

Each illustrated dossier should answer, in order: **What resembles what? What makes
the comparison worth investigating? What do the dates and local contexts show?
Which readings remain possible? What would help decide between them?** Lead with
the actual images or passages. Keep essential uncertainty beside its evidence and
collapse repeated methodological prose into short explanations and source details.

The current homepage gives considerable space to our earlier AI failures and the
original five studies. Consolidate these into a research record showing what each
study actually established and what remains open. Make the growing evidence atlas
the principal introduction to the enigma.

## Implementation order and completion checks

1. Add source-based intake, proposal provenance and coverage records; reconcile shared
   object identities and define configuration/observation states. Preserve original
   input hashes and all frozen experimental data.
2. Make every collection view use the same selected observations and episodes.
   Bring the cross-cultural image overview to the top of family dossiers.
3. Complete the first declared source batch and its illustrated dossiers. Publish
   unresolved leads and corrections alongside verified examples, clearly labelled.
4. Reorganize home and investigations around this material; review desktop/mobile
   reading order, image legibility, navigation and accessibility.
5. Use the improved evidence to choose the next discriminating study from
   [NEXT-TESTS.md](../NEXT-TESTS.md). Keep discovery and testing selections separate.

Acceptance examples:

- Selecting Late Egyptian bird observations retains their dated records in the
  timeline even when no attributed comparison thread includes them.
- A web/book lead can enter without a fictitious file in `inputs/`; original
  supplied-file validation still catches missing or altered files.
- Switching between a family's images, dates and map preserves its selected scope.
- An uncertain limb–round-form relationship remains uncertain in matrices and exports.
- Several views of one object never inflate physical-object counts; unknown locations
  never become invented map pins.
- Every comparison in the declared reviewed source portion has a traceable destination.
- A new reader can find the resemblance, date qualification, source and next research
  step without reading the project's experiment history first.

A catalogue gathered because people noticed similarities is valuable for discovery.
It does not supply the background frequency needed to show how exceptional a motif
is. A later rarity test must draw on a separately defined corpus with ordinary
variants, selection rules and independent visual review. This distinction lets the
atlas grow comprehensively while the research becomes more capable of answering why
the similarities exist.
