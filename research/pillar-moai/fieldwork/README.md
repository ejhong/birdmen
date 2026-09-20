# The resemblance under a closer light

20 September 2026. Exploratory edition 1.0. The reading page is
[`docs/fieldwork.html`](../../../docs/fieldwork.html).

This study prepares better evidence for the pillar–moai–boulder question. It adds
source photographs, makes literal relationships inspectable, and checks the dates
and interpretations that a historical explanation would need. It produces no new
AI ranking, discovery claim or global frequency estimate.

## Units and observations

`register.json` has 22 distinct `physical_id` values. Each object has a stated
photographic/scene scope, a primary image, identity sources, a qualified date, five
feature observations and normalized image annotation boxes. Existing catalogue
identities are reused through `catalogue_entity`; the publisher checks the link.
Additional photographs of a physical object must stay attached to that identity.

The five questions concern a beaked figure, an extended limb, a separate rounded
form, their relation within the same figure/scene, and facing beaked figures.
An eye, suspension hole or body outline is not the rounded feature. A limb-and-form
relation requires its component features in the same scope. A feature on a second
object cannot complete a bundle on the first.

| State | Meaning |
| --- | --- |
| `present` | Recorded in the specified view and scope. |
| `uncertain` | A plausible reading with a stated visual ambiguity. |
| `not-seen` | Not seen in this view; not a claim of cultural or object-wide absence. |
| `unresolved` | The relevant area is missing or inadequate for this question. |
| `not-applicable` | The defined relation does not apply, for example to a human-headed figure. |

The optional uncertain filter includes only `uncertain`; it never promotes missing
evidence to a match. These are AI-prepared editorial observations informed by
sources. Independence, specialist review and reliable perception are not assumed.
The current figures and feature definitions are development material.

## Collection and source history

The [selection rules](SELECTION.md) preserve nine focal/local examples, twelve
new museum selections and an explicitly identified prior Assyrian anchor. The
Met title queries retain ordinary variants and log exclusions. `pipeline/fieldwork.py`
replays the saved responses offline, without fetching a changed result set.
[Raw-data notes](../../../data/pillar-moai/fieldwork/README.md) record the provenance.

The [historical search log](SEARCH-LOG.md) separates checked primary sources from
leads still to investigate. Nine dated records distinguish site context, museum
attribution, an ancestry model estimate, documentary bounds and collection events.
The timeline plots the selected Egyptian object ranges separately. It does not
fill their chronological gaps or turn museum transfer into a production date.

The moai study's proposed egg reading corrects overly categorical wording in the
earlier reading pages. It does not overwrite frozen V2/V3 references or settle the
damaged arms' exact contours. The strongest visible two-object relation in this
edition remains Pillar 43–boulder; the moai contributes a more uncertain but
published interpretation and a paired scene.

## Adding the next evidence

1. Identify the physical object and the exact scene. Reuse an existing identity
   when adding a view. Attach primary sources, date scope and remaining doubts.
2. Preserve authentic image bytes, source URL, rights, dimensions and SHA-256.
   Draw viewing regions in the web overlay; do not alter artefact contours.
3. Record every feature with a note, including uncertainty and incomplete views.
   Any new acquisition batch needs its selection rule and exclusions preserved.
4. Add supported motif attestations to the main catalogue. A control can stay
   in this study without becoming a claimed anomalous cultural connection.
5. Rebuild with `python3 pipeline/publish.py`, run relevant integrity/browser
   checks, and review the images and date presentation.

Before a new model experiment: obtain independent reference review, collect
matched alternate photographs, and freeze the diagnostic in a new version.
Localization, relation agreement and abstention should precede any ranking.
See [`research/NEXT-TESTS.md`](../../NEXT-TESTS.md).
